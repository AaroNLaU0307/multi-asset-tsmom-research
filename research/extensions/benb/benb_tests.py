# -*- coding: utf-8 -*-
"""CTA-EDGE-02-BENB — the S2 build-validation suite.

Everything here runs on SYNTHETIC fixtures, on the sealed Markdown itself, or on
structural metadata that carries no outcome. NOTHING here computes a real historical
BENB basis, sign count, coefficient, return, Sharpe or bootstrap — and the firewall and
guard tests prove that rather than promise it.

The independent oracle (`benb_oracle.py`) imports nothing from the production engine and
reaches every expected value by a different algebraic route, because twice in this
programme an oracle reproduced the producer's own misreading and agreed with a wrong
engine.
"""
from __future__ import annotations

import copy
import datetime as _dt
import inspect
import math
import os
import re
import sys

import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
os.chdir(REPO)

import benb_authorization as auth          # noqa: E402
import benb_classify as bcls               # noqa: E402
import benb_contract as K                  # noqa: E402
import benb_data as bdata                  # noqa: E402
import benb_engine as beng                 # noqa: E402
import benb_feature as bfeat               # noqa: E402
import benb_fixtures as fx                 # noqa: E402
import benb_inference as binf              # noqa: E402
import benb_oracle as ORC                  # noqa: E402
import benb_pipeline as bpipe              # noqa: E402
import benb_report as brep                 # noqa: E402

PREREG = os.path.join(K.BENB_DIR, "BENB_PREREGISTRATION.md")
HAVE_PINNED_DATA = all(os.path.exists(os.path.join(K.DATA_DIR, n)) for n in K.PINNED)
needs_data = pytest.mark.skipif(
    not HAVE_PINNED_DATA,
    reason="pinned data/benb/ files are git-ignored and absent in this checkout")


def rng():
    return np.random.Generator(np.random.PCG64(np.random.SeedSequence(20260915)))


def contract_text():
    with open(PREREG, "r", encoding="utf-8") as fh:
        return fh.read()


def source_of(module_name):
    with open(os.path.join(HERE, module_name), "r", encoding="utf-8") as fh:
        return fh.read()


def import_lines(src):
    return [l for l in src.splitlines() if re.match(r"\s*(import|from)\s", l)]


def called_names(src):
    """Every bare function NAME actually called in `src`, from the parsed AST.

    Grepping for `open(` would trip over the string "open(t+1)", which is a position
    leg, not a call - so the check parses rather than greps.
    """
    import ast
    out = set()
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            out.add(node.func.id)
    return out


def run(cell, b=120, bootstrap=True):
    return bpipe.run_cell(fx.source(cell), cell.ticker, "PRIMARY",
                          b=b, rng=rng(), run_bootstrap=bootstrap)


def world(name, n=300, noise=0.00004, seed=3, **kw):
    return fx.build_world(**fx.WORLDS[name], n_signals=n, noise=noise, seed=seed, **kw)


def _res(name, n=300, noise=0.00004, seed=3, b=120, **kw):
    return run(world(name, n=n, noise=noise, seed=seed, **kw), b=b)


# --------------------------------------------------------------------------- #
# 0. The executable constants ARE the sealed contract                          #
# --------------------------------------------------------------------------- #


def test_c00_constants_are_re_derived_from_the_sealed_markdown():
    t = contract_text()
    assert re.search(r"ONE_WAY_COST\s+=\s+5\.0 bps", t) and K.ONE_WAY_COST_BPS == 5.0
    assert re.search(r"ROUND_TRIP_COST\s+=\s+10\.0 bps", t)
    assert K.ROUND_TRIP_COST_BPS == 10.0
    assert re.search(r"M2_VALUE\s+=\s+\+0\.30", t) and K.M2_SHARPE == 0.30
    assert re.search(r"M2_BOUNDARY_OPERATOR\s+=\s+STRICT\s+>", t)
    assert "MINIMUM PRIOR HISTORY = 250 observations." in t
    assert K.MIN_PRIOR_HISTORY == 250
    assert re.search(r"\bB\s+=\s+10,000", t) and K.BOOTSTRAP_B == 10_000
    assert "AT LEAST 3 calendar years" in t and K.MIN_YEARS_WITH_DISCOUNT == 3
    assert re.search(r"EVIDENCE_CEILING\s+=\s+supported", t)
    assert K.EVIDENCE_CEILING == "supported"


def test_c01_oracle_transcribed_the_same_constants():
    assert ORC.ORACLE_MIN_PRIOR == K.MIN_PRIOR_HISTORY
    assert ORC.ORACLE_ONE_WAY_BPS == K.ONE_WAY_COST_BPS
    assert ORC.ORACLE_ROUND_TRIP_BPS == K.ROUND_TRIP_COST_BPS
    assert ORC.ORACLE_M1 == K.M1_RETURN_FLOOR_BPS
    assert ORC.ORACLE_M2 == K.M2_SHARPE
    assert ORC.ORACLE_MONTHS_PER_YEAR == K.SHARPE_PERIODS_PER_YEAR


def test_c02_oracle_imports_nothing_from_the_production_engine():
    src = source_of("benb_oracle.py")
    for banned in ("benb_engine", "benb_feature", "benb_inference", "benb_classify",
                   "benb_pipeline", "benb_contract", "benb_data", "benb_fixtures"):
        assert not re.search(rf"^\s*(import|from)\s+{banned}\b", src, re.M), banned


def test_c03_seal_identity_is_pinned_in_the_contract_module():
    import hashlib
    with open(PREREG, "rb") as fh:
        assert hashlib.sha256(fh.read()).hexdigest() == K.SEALED_PREREG_SHA256
    with open(os.path.join(K.BENB_DIR, "BENB_SEAL_MANIFEST.md"), "rb") as fh:
        assert hashlib.sha256(fh.read()).hexdigest() == K.SEAL_MANIFEST_SHA256


# --------------------------------------------------------------------------- #
# §4 / §20 — the causal expanding median                                       #
# --------------------------------------------------------------------------- #


def monotone_cell(n=300, step=1e-4):
    """A cell whose basis is strictly increasing, so the expanding median MOVES every
    day. On a flat history a median test is vacuous - a single outlier cannot shift a
    median of 250 identical values - and a vacuous fixture proves nothing."""
    grid = fx.business_days(_dt.date(2010, 1, 4), n)
    cell = bdata.CellData(
        ticker="HYG", grid=grid,
        p_open={d: 100.0 * math.exp(step * i) for i, d in enumerate(grid)},
        p_close={d: 100.0 * math.exp(step * i) for i, d in enumerate(grid)},
        nav={d: 100.0 for d in grid}, ex_dates=set())
    cell.validate()
    return cell


def test_f01_expanding_median_excludes_the_current_day():
    cell = monotone_cell()
    rows = bfeat.features(cell)
    i = fx.BURN_IN
    base = rows[i]
    assert base.has_feature
    assert base.m == pytest.approx(1e-4 * 124.5)       # median of b_0..b_249

    mutated = copy.deepcopy(cell)                      # make TODAY a wild outlier
    mutated.p_close[cell.grid[i]] = mutated.nav[cell.grid[i]] * math.exp(-5.0)
    mrows = bfeat.features(mutated)
    assert mrows[i].m == pytest.approx(base.m), "b_t leaked into its own median"
    assert mrows[i].b == pytest.approx(-5.0) != pytest.approx(base.b)
    assert mrows[i].x == pytest.approx(-5.0 - base.m)

    # ...and it DOES move the NEXT day's median by one order statistic, so the
    # invariant above is a real separation rather than an artefact of a flat history
    assert rows[i + 1].m == pytest.approx(1e-4 * 125)
    assert mrows[i + 1].m == pytest.approx(1e-4 * 124)


def test_f02_future_observations_never_alter_a_historical_x():
    cell = world("TRADABLE_CONVERGENCE", n=30, noise=0.0)
    full = bfeat.features(cell)
    cut = fx.BURN_IN + 10
    truncated = bdata.CellData(
        ticker=cell.ticker, grid=cell.grid[:cut],
        p_open={d: cell.p_open[d] for d in cell.grid[:cut]},
        p_close={d: cell.p_close[d] for d in cell.grid[:cut]},
        nav={d: cell.nav[d] for d in cell.grid[:cut]}, ex_dates=cell.ex_dates)
    for a, b in zip(bfeat.features(truncated), full[:cut]):
        assert a.date == b.date
        assert (a.x is None) == (b.x is None)
        if a.x is not None:
            assert a.x == pytest.approx(b.x, abs=1e-15)


def test_f03_feature_matches_the_independent_oracle():
    cell = world("TRADABLE_CONVERGENCE", n=20)
    rows = bfeat.features(cell)
    want = ORC.oracle_features([cell.p_close[d] for d in cell.grid],
                               [cell.nav[d] for d in cell.grid])
    for r, (ob, om, ox) in zip(rows, want):
        assert r.b == pytest.approx(ob, abs=1e-15)
        if om is None:
            assert r.m is None and r.x is None
        else:
            assert r.m == pytest.approx(om, abs=1e-15)
            assert r.x == pytest.approx(ox, abs=1e-15)


def test_f04_burn_in_boundary_is_exactly_250():
    rows = bfeat.features(world("TRADABLE_CONVERGENCE", n=5))
    assert not rows[249].has_feature and rows[249].m is None
    assert rows[250].has_feature and rows[250].m is not None


def test_f05_discount_side_only_and_severity_is_continuous():
    cell = world("TRADABLE_CONVERGENCE", n=40)
    rows = bfeat.features(cell)
    elig = bdata.eligibility(cell)
    disc = bfeat.discount_rows(rows, elig.eligible)
    prem = bfeat.premium_rows(rows, elig.eligible)
    assert disc and prem
    assert not (set(r.date for r in disc) & set(r.date for r in prem))
    assert all(r.x < 0 and r.severity > 0 for r in disc)
    assert all(r.severity is None for r in prem)
    assert len({round(r.severity, 12) for r in disc}) > 1, "d_t must be continuous"


# --------------------------------------------------------------------------- #
# §7 — the exact three-component decomposition                                 #
# --------------------------------------------------------------------------- #


def test_d01_identity_holds_on_every_eligible_observation_in_every_world():
    for name in fx.WORLDS:
        cell = world(name, n=25, noise=0.0005, seed=11)
        idx = {d: i for i, d in enumerate(cell.grid)}
        worst = 0.0
        for d in bdata.eligibility(cell).eligible:
            dec = beng.decompose(cell, d, cell.grid[idx[d] + 1])
            beng.assert_identity(dec)
            worst = max(worst, abs(dec.identity_residual))
        assert worst < 1e-12, (name, worst)


def test_d02_decomposition_matches_the_oracle():
    cell = world("MIXED", n=15, noise=0.0004, seed=5)
    idx = {d: i for i, d in enumerate(cell.grid)}
    for d in bdata.eligibility(cell).eligible[:60]:
        n = cell.grid[idx[d] + 1]
        got = beng.decompose(cell, d, n)
        w = ORC.oracle_components(cell.p_close[d], cell.p_open[n], cell.p_close[n],
                                  cell.nav[d], cell.nav[n])
        assert got.r_overnight == pytest.approx(w[0], abs=1e-15)
        assert got.r_tradable == pytest.approx(w[1], abs=1e-15)
        assert got.r_nav == pytest.approx(w[2], abs=1e-15)
        assert got.delta_b == pytest.approx(w[3], abs=1e-15)


def test_d03_an_identity_violation_is_raised_not_repaired():
    bad = beng.Decomposition(_dt.date(2011, 1, 3), _dt.date(2011, 1, 4),
                             r_overnight=0.001, r_tradable=0.002, r_nav=0.0,
                             delta_b=0.010)
    with pytest.raises(AssertionError):
        beng.assert_identity(bad)


# --------------------------------------------------------------------------- #
# §14 — THE THREE MANDATORY ECONOMIC WORLDS (+ the mixed world, §15)           #
# --------------------------------------------------------------------------- #


def test_w1_stale_nav_world_is_never_supported():
    r = _res("STALE_NAV")
    b = r.boot
    assert b.beta_N.upper < 0, "beta_N must be SUPPORTED NEGATIVE in a stale-NAV world"
    assert not (b.beta_T.lower > 0), "beta_T must NOT be supported"
    v = bpipe.classify_primary(r)
    assert v.klass in ("A", "A-M"), v.klass
    assert v.research_status == "not_promoted"


def test_w2_overnight_discovery_world_is_never_supported():
    r = _res("OVERNIGHT_DISCOVERY")
    b = r.boot
    assert b.beta_O.lower > 0, "beta_O must be SUPPORTED POSITIVE"
    assert not (b.beta_T.lower > 0), "beta_T must NOT be supported"
    assert not (b.beta_N.upper < 0), "beta_N must not read as supported-negative here"
    v = bpipe.classify_primary(r)
    assert v.klass == "B", v.klass
    assert v.research_status == "not_promoted"
    assert v.qualifier == "OVERNIGHT_PRICE_DISCOVERY_ONLY"


def test_w3_tradable_convergence_is_the_only_world_that_reaches_gate_two():
    r = _res("TRADABLE_CONVERGENCE")
    assert r.boot.beta_T.lower > 0, "beta_T must be SUPPORTED POSITIVE"
    v = bpipe.classify_primary(r)
    assert v.klass in ("D", "S", "E", "G"), v.klass


def test_w4_mixed_world_is_A_M():
    r = _res("MIXED")
    b = r.boot
    assert b.beta_O.lower > 0 and b.beta_N.upper < 0
    assert not (b.beta_T.lower > 0)
    v = bpipe.classify_primary(r)
    assert v.klass == "A-M", v.klass
    assert v.qualifier == "MIXED_NON_HARVESTABLE_CONVERGENCE"


def test_w5_only_the_tradable_world_earns_a_positive_net_trade_return():
    net = {}
    for name in ("STALE_NAV", "OVERNIGHT_DISCOVERY", "TRADABLE_CONVERGENCE"):
        r = run(world(name, n=300), b=1, bootstrap=False)
        net[name] = beng.mean_net_trade_return_bps(r.obs)
    assert net["TRADABLE_CONVERGENCE"] > 0 > net["STALE_NAV"]
    assert net["OVERNIGHT_DISCOVERY"] < 0
    # the non-tradable worlds lose exactly the round trip, up to fixture noise
    assert net["STALE_NAV"] == pytest.approx(-K.ROUND_TRIP_COST_BPS, abs=0.5)


# --------------------------------------------------------------------------- #
# §6 / §19 — the ex-date rule, with a DISCRIMINATING disabled variant           #
# --------------------------------------------------------------------------- #


def test_x01_ex_date_rule_is_forward_looking_and_uses_the_union():
    base = world("TRADABLE_CONVERGENCE", n=12)
    t, t1 = base.grid[fx.BURN_IN], base.grid[fx.BURN_IN + 1]

    # (a) t+1 is an ex-date -> t is excluded
    c = world("TRADABLE_CONVERGENCE", n=12, ex_dates=[t1])
    assert t not in bdata.eligibility(c).eligible
    assert t in bdata.eligibility(c).excluded_ex_date

    # (b) t itself is an ex-date -> t is NOT excluded by that alone
    c2 = world("TRADABLE_CONVERGENCE", n=12, ex_dates=[t])
    assert t in bdata.eligibility(c2).eligible

    # (c) the §D.4 UNION wins when the two calendars disagree, in both directions
    only_price = world("TRADABLE_CONVERGENCE", n=12, ex_dates=[], px_ex_dates=[t1])
    only_issuer = world("TRADABLE_CONVERGENCE", n=12, ex_dates=[t1], px_ex_dates=[])
    assert t not in bdata.eligibility(only_price).eligible
    assert t not in bdata.eligibility(only_issuer).eligible


def test_x02_ex_date_fixture_reproduces_the_contamination_it_excludes():
    """Discriminating: with the exclusion DISABLED a distribution mechanically
    contaminates both diagnostic legs; the sealed rule removes the observation."""
    cell = world("TRADABLE_CONVERGENCE", n=12)
    t, t1 = cell.grid[fx.BURN_IN], cell.grid[fx.BURN_IN + 1]
    dist = 0.02                                        # a 2 % distribution

    contaminated = copy.deepcopy(cell)
    contaminated.nav[t1] *= math.exp(-dist)            # NAV drops ex-distribution
    contaminated.p_open[t1] *= math.exp(-dist)         # the price gaps down at the open
    contaminated.p_close[t1] *= math.exp(-dist)
    contaminated.ex_dates = {t1}

    clean = beng.decompose(cell, t, t1)
    cont = beng.decompose(contaminated, t, t1)
    assert cont.r_nav - clean.r_nav == pytest.approx(-dist, abs=1e-12)
    assert cont.r_overnight - clean.r_overnight == pytest.approx(-dist, abs=1e-12)
    assert cont.r_tradable == pytest.approx(clean.r_tradable, abs=1e-12)

    assert t not in bdata.eligibility(contaminated).eligible    # sealed rule ON
    disabled = copy.deepcopy(contaminated)
    disabled.ex_dates = set()
    assert t in bdata.eligibility(disabled).eligible            # rule OFF -> survives


def test_x03_disabling_the_exclusion_moves_the_estimated_diagnostics():
    """The separation the fixture requires: leaving contaminated days in MOVES beta_N."""
    cell = world("STALE_NAV", n=120)
    idx = {d: i for i, d in enumerate(cell.grid)}
    rows = bfeat.features(cell)
    hit = [r.date for r in rows
           if r.is_discount and idx[r.date] + 1 < len(cell.grid)][:20]

    contaminated = copy.deepcopy(cell)
    for d in hit:
        n = cell.grid[idx[d] + 1]
        for m in (contaminated.nav, contaminated.p_open, contaminated.p_close):
            m[n] *= math.exp(-0.02)
        contaminated.ex_dates.add(n)

    kept = run(contaminated, b=1, bootstrap=False)
    disabled = copy.deepcopy(contaminated)
    disabled.ex_dates = set()
    left_in = run(disabled, b=1, bootstrap=False)
    assert kept.n_discount < left_in.n_discount
    assert kept.gate1.beta_N != pytest.approx(left_in.gate1.beta_N, rel=1e-6)


# --------------------------------------------------------------------------- #
# §9 / §10 — the fixed trade and the calendarised monthly P&L                   #
# --------------------------------------------------------------------------- #


def test_t01_fixed_trade_carries_no_overnight_exposure_and_pays_the_round_trip():
    r = _res("TRADABLE_CONVERGENCE", n=300, b=1)
    o = r.obs[0]
    assert not beng.carries_overnight_exposure(o)
    assert [l.to_position for l in beng.position_path(o)] == [beng.LONG, beng.FLAT]
    assert o.net_trade_return_bps == pytest.approx(o.r_tradable_bps - 10.0)
    assert o.net_trade_return_bps == pytest.approx(
        ORC.oracle_net_trade_return_bps(o.r_tradable_bps))
    # the trade is FIXED: severity never sizes it
    big = max(r.obs, key=lambda x: x.d)
    small = min(r.obs, key=lambda x: x.d)
    assert (big.net_trade_return_bps - big.r_tradable_bps
            == pytest.approx(small.net_trade_return_bps - small.r_tradable_bps))


def test_t02_zero_signal_months_are_retained():
    cell = world("TRADABLE_CONVERGENCE", n=8, spacer_days=40)
    r = run(cell, b=40)
    grid = r.month_grid
    series = beng.monthly_series(r.obs, grid)
    active = {o.entry_month for o in r.obs}
    assert len(series) == len(grid) > len(active)
    assert len([v for v in series if v == 0.0]) == len(grid) - len(active) > 0
    assert series == pytest.approx(ORC.oracle_monthly(
        [o.entry_month for o in r.obs],
        [o.net_trade_return_bps for o in r.obs], grid))


def test_t03_retained_zero_months_materially_lower_the_sharpe():
    """The sealed choice, made visible: the same four trading months scored on a
    24-month calendar rather than compressed to the months that traded."""
    active = [12.0, 11.0, 13.0, 12.5]
    retained = [0.0] * 24
    for k, v in zip((0, 6, 12, 18), active):
        retained[k] = v
    compressed = beng.calendarised_sharpe(active)
    calendarised = beng.calendarised_sharpe(retained)
    assert calendarised < compressed / 10.0
    assert calendarised == pytest.approx(ORC.oracle_sharpe(retained))
    assert compressed == pytest.approx(ORC.oracle_sharpe(active))
    assert math.isnan(beng.calendarised_sharpe([5.0] * 10))     # sd == 0 -> NaN
    assert math.isnan(beng.calendarised_sharpe([1.0]))          # n < 2  -> NaN


def test_t04_trades_are_assigned_to_the_ENTRY_month():
    cell = world("TRADABLE_CONVERGENCE", n=300)
    r = run(cell, b=1, bootstrap=False)
    idx = {d: i for i, d in enumerate(cell.grid)}
    for o in r.obs:
        nxt = cell.grid[idx[o.date] + 1]
        assert o.entry_month == "%04d-%02d" % (nxt.year, nxt.month)
    assert [o for o in r.obs
            if o.entry_month != "%04d-%02d" % (o.date.year, o.date.month)], \
        "the fixture must contain at least one month-boundary crossing"


def test_t05_month_grid_matches_the_oracle_and_is_contiguous():
    g = beng.month_grid("2009-11", "2012-02")
    assert g == ORC.oracle_month_grid("2009-11", "2012-02")
    assert g[0] == "2009-11" and g[-1] == "2012-02" and len(g) == 28
    with pytest.raises(KeyError):
        beng.monthly_series(
            [beng.Observation(_dt.date(2013, 5, 1), 2013, "2013-05", 0.01,
                              0.0, 0.0, 0.0)], g)


# --------------------------------------------------------------------------- #
# §8 — Gate 1 against the oracle                                               #
# --------------------------------------------------------------------------- #


def test_g01_ols_matches_the_independent_oracle_on_all_three_legs():
    r = _res("MIXED", n=300, noise=0.0002, seed=17, b=1)
    d = [o.d for o in r.obs]
    for attr, series in (("beta_T", [o.r_tradable_bps for o in r.obs]),
                         ("beta_O", [o.r_overnight_bps for o in r.obs]),
                         ("beta_N", [o.r_nav_bps for o in r.obs])):
        _, want = ORC.oracle_ols(d, series)
        assert getattr(r.gate1, attr) == pytest.approx(want, rel=1e-9)


def test_g02_a_zero_variance_regressor_raises_rather_than_returning_nan():
    with pytest.raises(ValueError):
        beng.ols_slope_intercept([1.0, 1.0, 1.0], [1.0, 2.0, 3.0])
    with pytest.raises(ValueError):
        beng.ols_slope_intercept([1.0], [1.0])


def test_g03_gate1_slopes_recover_the_constructed_coefficients():
    # tr_coef = 1, nav_coef = 0 in log units -> beta_T = 1e4 bps per unit of d
    r = run(world("TRADABLE_CONVERGENCE", n=300, noise=0.0), b=1, bootstrap=False)
    assert r.gate1.beta_T == pytest.approx(1e4, rel=1e-9)
    assert r.gate1.beta_N == pytest.approx(0.0, abs=1e-6)
    assert r.gate1.beta_O == pytest.approx(0.0, abs=1e-6)
    s = run(world("STALE_NAV", n=300, noise=0.0), b=1, bootstrap=False)
    assert s.gate1.beta_N == pytest.approx(-1e4, rel=1e-9)
    assert s.gate1.beta_T == pytest.approx(0.0, abs=1e-6)


# --------------------------------------------------------------------------- #
# §11 / §21 — the bootstrap and the FROZEN causal feature                       #
# --------------------------------------------------------------------------- #


def test_b01_bootstrap_is_deterministic_and_shares_one_draw_set():
    cell = world("TRADABLE_CONVERGENCE", n=300, noise=0.00005, seed=2)
    a, b = run(cell, b=80), run(cell, b=80)
    assert a.boot.beta_T.as_dict() == b.boot.beta_T.as_dict()
    assert a.boot.sharpe.as_dict() == b.boot.sharpe.as_dict()
    for iv in (a.boot.beta_T, a.boot.beta_O, a.boot.beta_N, a.boot.mean_net):
        assert iv.lower <= iv.point <= iv.upper
    assert a.boot.years == sorted(set(o.year for o in a.obs))


def test_b02_the_bootstrap_requires_an_explicit_rng():
    r = _res("TRADABLE_CONVERGENCE", n=300, b=1)
    with pytest.raises(ValueError):
        binf.year_block_bootstrap(r.obs, r.month_grid, b=10, rng=None)


def test_b03_the_bootstrap_cannot_recompute_the_expanding_median():
    """The sealed §G.2 rule: replicates resample FROZEN tuples.

    Enforced by construction, not by care: `year_block_bootstrap` takes `Observation`
    tuples, never a `CellData` and never a price, so it could not rebuild the feature
    even if it tried — and the module imports nothing that would let it.
    """
    r = _res("TRADABLE_CONVERGENCE", n=300, b=1)
    before = [(o.date, o.d) for o in r.obs]
    binf.year_block_bootstrap(r.obs, r.month_grid, b=25, rng=rng())
    assert [(o.date, o.d) for o in r.obs] == before, "the frozen tuples were mutated"

    imports = "\n".join(import_lines(source_of("benb_inference.py")))
    assert "benb_feature" not in imports and "benb_data" not in imports
    params = set(inspect.signature(binf.year_block_bootstrap).parameters)
    assert params == {"obs", "month_grid", "b", "rng"}


def test_b04_year_resampling_would_move_a_recomputed_median():
    """Discriminating for the rule above: the years differ enough that a recomputed
    expanding median WOULD move, so freezing is observable rather than vacuous."""
    early, late = [0.001] * 30, [0.02] * 30
    assert ORC.oracle_median(early + late) != pytest.approx(
        ORC.oracle_median(late + late))
    assert ORC.oracle_median(early + late) == pytest.approx(0.0105)


def test_b05_replicates_are_whole_calendar_year_blocks():
    r = _res("TRADABLE_CONVERGENCE", n=300, b=1)
    by_year = binf.group_by_year(r.obs)
    assert sum(len(v) for v in by_year.values()) == len(r.obs)
    assert all(all(o.year == y for o in v) for y, v in by_year.items())
    assert len(by_year) >= K.MIN_YEARS_WITH_DISCOUNT


# --------------------------------------------------------------------------- #
# §12 — leave-one-calendar-year-out                                            #
# --------------------------------------------------------------------------- #


def test_l01_loyo_detects_a_single_carrying_year():
    r = _res("TRADABLE_CONVERGENCE", n=300, noise=0.00005, seed=4, b=40)
    assert r.loyo.passes
    carry = sorted({o.year for o in r.obs})[1]
    doctored = [o if o.year == carry else beng.Observation(
        o.date, o.year, o.entry_month, o.d,
        o.r_overnight_bps, -abs(o.r_tradable_bps), o.r_nav_bps) for o in r.obs]
    res = binf.leave_one_year_out(doctored)
    assert not res.passes
    assert res.min_beta_T <= 0 and res.min_year == carry


def test_l02_exactly_one_bootstrap_family_and_one_fragility_diagnostic():
    """Checked against what the module DEFINES, not against what its prose promises:
    a docstring agreeing with a claim is not evidence for it."""
    defined = {n for n, o in vars(binf).items()
               if inspect.isfunction(o) and o.__module__ == "benb_inference"}
    assert defined == {"year_block_bootstrap", "leave_one_year_out", "group_by_year",
                       "_percentile_interval"}, sorted(defined)
    src = source_of("benb_inference.py")
    assert src.count("def year_block_bootstrap") == 1
    assert src.count("def leave_one_year_out") == 1
    assert not re.findall(r"^def \w*(newey|hac|cluster|stationary)\w*", src,
                          re.M | re.I)


# --------------------------------------------------------------------------- #
# §13 / §16 — the classification engine                                        #
# --------------------------------------------------------------------------- #


def test_k01_classification_is_total_reachable_and_unpromotable():
    p = bcls.properties()
    assert p["undefined"] == 0
    assert all(p["reachable"][c] > 0 for c in bcls.CLASSES), p["reachable"]
    assert p["illegal_promotions"] == 0
    assert p["S_without_both_gates"] == 0


def test_k02_classification_matches_the_independent_oracle_everywhere():
    bad = []
    n = 0
    for case in bcls.sweep():
        n += 1
        got, want = bcls.classify(*case).klass, ORC.oracle_classify(*case)
        if got != want:
            bad.append((case, got, want))
    assert n > 10_000 and not bad, bad[:3]


def test_k03_gate_boundaries_are_strict():
    ok = dict(L_T=1.0, U_T=2.0, L_O=-1.0, U_O=-0.5, L_N=0.5, U_N=1.0, loyo_ok=True)
    assert bcls.classify(**ok, L_R=1.0, U_R=3.0, L_S=0.30, U_S=1.5).klass != "S"
    assert bcls.classify(**ok, L_R=1.0, U_R=3.0, L_S=0.3000001, U_S=1.5).klass == "S"
    assert bcls.classify(**ok, L_R=0.0, U_R=3.0, L_S=1.0, U_S=1.5).klass != "S"
    assert bcls.classify(**ok, L_R=1e-9, U_R=3.0, L_S=1.0, U_S=1.5).klass == "S"
    assert bcls.classify(L_T=0.0, U_T=2.0, L_O=-1.0, U_O=-0.5, L_N=0.5, U_N=1.0,
                         L_R=1.0, U_R=3.0, L_S=1.0, U_S=1.5, loyo_ok=True).klass != "S"


def test_k04_gate_two_and_fragility_failure_modes():
    ok = dict(L_T=1.0, U_T=2.0, L_O=-1.0, U_O=-0.5, L_N=0.5, U_N=1.0, loyo_ok=True)
    assert bcls.classify(**ok, L_R=-5.0, U_R=-1.0, L_S=-1.0, U_S=0.0).klass == "D"
    assert bcls.classify(**ok, L_R=-0.5, U_R=3.0, L_S=1.0, U_S=1.5).klass == "E"
    assert bcls.classify(**ok, L_R=-1.0, U_R=50.0, L_S=-0.5, U_S=9.0).klass == "E"
    assert bcls.classify(L_T=1.0, U_T=2.0, L_O=-1.0, U_O=-0.5, L_N=0.5, U_N=1.0,
                         L_R=5.0, U_R=9.0, L_S=1.0, U_S=2.0, loyo_ok=False).klass == "G"
    # Gate 1 not supported: A-M before A before B before C1 / C2
    assert bcls.classify(-1, 1, 0.5, 1, -1, -0.5, 9, 9, 9, 9, True).klass == "A-M"
    assert bcls.classify(-1, 1, -1, -0.5, -1, -0.5, 9, 9, 9, 9, True).klass == "A"
    assert bcls.classify(-1, 1, 0.5, 1, 0.5, 1, 9, 9, 9, 9, True).klass == "B"
    assert bcls.classify(-1, -0.5, -1, -0.5, 0.5, 1, 9, 9, 9, 9, True).klass == "C1"
    assert bcls.classify(-1, 1, -1, -0.5, 0.5, 1, 9, 9, 9, 9, True).klass == "C2"


def test_k05_classification_cannot_see_the_premium_side_or_LQD():
    params = set(inspect.signature(bcls.classify).parameters)
    assert params == {"L_T", "U_T", "L_O", "U_O", "L_N", "U_N", "L_R", "U_R",
                      "L_S", "U_S", "loyo_ok", "is_evaluable"}
    src = source_of("benb_classify.py")
    body = src[src.index("def classify("):src.index("def _v(")].lower()
    assert "premium" not in body and "lqd" not in body and "secondary" not in body


def test_k06_status_and_qualifier_mapping_is_sealed():
    assert set(K.STATUS_MAP) == set(bcls.CLASSES)
    assert K.STATUS_MAP["S"][0] == "supported"
    assert all(K.STATUS_MAP[c][0] != "supported" for c in bcls.CLASSES if c != "S")
    legal = {"confirmed", "supported", "not_promoted", "falsified", "active",
             "archived", "experimental", "unresolved"}
    assert all(v[0] in legal for v in K.STATUS_MAP.values())
    f = bcls.classify(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, False, is_evaluable=False)
    assert f.klass == "F" and f.evaluable is False
    assert f.research_status == "unresolved"


# --------------------------------------------------------------------------- #
# §17 / §18 — premium and LQD carry NO rescue and NO promotion power            #
# --------------------------------------------------------------------------- #


def test_r01_the_premium_side_cannot_rescue_a_failed_gate_one():
    r = _res("STALE_NAV")
    base = bpipe.classify_primary(r).klass
    assert r.n_premium > 0, "the fixture must contain premium observations"
    r.premium_descriptive["mean_premium_convergence_bps"] = 9_999.0
    r.premium_descriptive["premium_beta_T"] = 9_999.0
    assert bpipe.classify_primary(r).klass == base
    assert set(inspect.signature(bpipe.classify_primary).parameters) == {
        "primary", "hashes_ok"}
    assert K.POWERS["PREMIUM_SIDE"] == {"promotion": False, "rescue": False}


def test_r02_lqd_cannot_rescue_or_promote_hyg():
    src = fx.source(world("STALE_NAV", n=300, ticker="HYG"),
                    world("TRADABLE_CONVERGENCE", n=300, ticker="LQD"))
    p = bpipe.run_cell(src, "HYG", "PRIMARY", b=80, rng=rng())
    s = bpipe.run_cell(src, "LQD", "SECONDARY", b=80, rng=rng())
    assert s.boot.beta_T.lower > 0, "the LQD fixture must be spectacular"
    v = bpipe.classify_primary(p)
    assert v.klass in ("A", "A-M") and v.research_status == "not_promoted"
    summary = bpipe.secondary_summary(s)
    assert summary["promotion_power"] == "NONE" and summary["rescue_power"] == "NONE"
    assert "secondary" not in str(inspect.signature(bpipe.classify_primary)).lower()
    assert K.POWERS["LQD_SECONDARY"] == {"promotion": False, "rescue": False}


def test_r03_the_diagnostic_legs_cannot_promote():
    assert bcls.properties()["illegal_promotions"] == 0
    assert K.POWERS["BETA_O"]["promotion"] is False
    assert K.POWERS["BETA_N"]["promotion"] is False
    assert K.POWERS["HYG_BETA_T"]["promotion"] is True
    assert K.POWERS["HYG_BETA_T"]["rescue"] is False


def test_r04_the_secondary_runs_the_identical_sealed_code_path():
    cell = world("TRADABLE_CONVERGENCE", n=300, ticker="LQD")
    a = bpipe.run_cell(fx.source(cell), "LQD", "SECONDARY", b=1, rng=rng(),
                       run_bootstrap=False)
    b = bpipe.run_cell(fx.source(copy.deepcopy(cell)), "LQD", "PRIMARY", b=1,
                       rng=rng(), run_bootstrap=False)
    assert a.gate1.beta_T == pytest.approx(b.gate1.beta_T)
    assert a.n_discount == b.n_discount and a.month_grid == b.month_grid


# --------------------------------------------------------------------------- #
# §23 — cross-boundary behaviour                                               #
# --------------------------------------------------------------------------- #


def test_cb01_weekends_and_holidays_never_enter_the_grid():
    hol = [_dt.date(2011, 1, 17)]                      # a Monday holiday
    cell = world("TRADABLE_CONVERGENCE", n=30, holidays=hol)
    assert all(d.weekday() < 5 for d in cell.grid)
    assert hol[0] not in cell.grid
    idx = {d: i for i, d in enumerate(cell.grid)}
    for f in [d for d in cell.grid if d.weekday() == 4][:5]:
        assert cell.grid[idx[f] + 1].weekday() == 0    # Friday -> Monday, t+1
    j = idx[_dt.date(2011, 1, 14)]
    assert cell.grid[j + 1] == _dt.date(2011, 1, 18)   # skips the holiday Monday


def test_cb02_a_december_signal_enters_in_january():
    """Deterministic, not hopeful: the signal is PLACED on the last business day of a
    December by choosing the block offset, instead of waiting for one to occur."""
    per_block = 3
    grid = fx.business_days(_dt.date(2009, 1, 2), 250 + 300 * per_block + 4)
    target = next(i for i, d in enumerate(grid)
                  if i >= 260 and d.month == 12 and grid[i + 1].month == 1)
    first = fx.BURN_IN + ((target - fx.BURN_IN) % per_block)
    cell = world("TRADABLE_CONVERGENCE", n=300, start=_dt.date(2009, 1, 2),
                 first_signal_index=first)
    r = run(cell, b=1, bootstrap=False)
    signal_day = grid[target]
    hit = [o for o in r.obs if o.date == signal_day]
    assert hit, "no observation on the placed December signal %s" % signal_day
    o = hit[0]
    assert o.date.month == 12
    assert o.entry_month == "%04d-01" % (o.date.year + 1)
    assert o.year == o.date.year, "the YEAR block follows the signal date t"


def test_cb03_the_last_grid_date_has_no_next_and_is_excluded():
    cell = world("TRADABLE_CONVERGENCE", n=10)
    e = bdata.eligibility(cell)
    assert cell.grid[-1] in e.excluded_no_next
    assert cell.grid[-1] not in e.eligible
    assert len(e.excluded_burn_in) == K.MIN_PRIOR_HISTORY
    assert (len(e.eligible) + len(e.excluded_ex_date) + len(e.excluded_burn_in)
            + len(e.excluded_no_next)) == len(cell.grid)


def test_cb04_structural_defects_raise_rather_than_being_repaired():
    cell = world("TRADABLE_CONVERGENCE", n=5)
    dup = copy.deepcopy(cell)
    dup.grid = dup.grid + [dup.grid[-1]]
    with pytest.raises(bdata.DataDefect):
        dup.validate()
    missing = copy.deepcopy(cell)
    del missing.nav[missing.grid[10]]
    with pytest.raises(bdata.DataDefect):
        missing.validate()
    nonpos = copy.deepcopy(cell)
    nonpos.p_open[nonpos.grid[10]] = 0.0
    with pytest.raises(bdata.DataDefect):
        nonpos.validate()
    backwards = copy.deepcopy(cell)
    backwards.grid = list(reversed(backwards.grid))
    with pytest.raises(bdata.DataDefect):
        backwards.validate()


def test_cb05_the_common_grid_is_a_date_only_intersection():
    a = [_dt.date(2011, 1, d) for d in (3, 4, 5, 6, 7)]
    b = [_dt.date(2011, 1, d) for d in (4, 5, 8, 9)]
    assert bdata.align_grid(a, b) == [_dt.date(2011, 1, 4), _dt.date(2011, 1, 5)]
    assert bdata.align_grid(b, a) == bdata.align_grid(a, b)       # symmetric
    assert bdata.align_grid(a, []) == []                          # never a fill
    assert bdata.align_grid(list(reversed(a)), a) == a             # always ascending
    # no alignment repair anywhere in the module: checked as CALLS, since the
    # docstring names these very techniques in order to forbid them
    src = source_of("benb_data.py").lower()
    for banned in ("merge_asof(", ".reindex(", ".ffill(", ".fillna(", ".bfill(",
                   "interpolate(", "asfreq("):
        assert banned not in src, banned


def test_cb06_loyo_leaves_a_rank_sufficient_sample():
    r = _res("TRADABLE_CONVERGENCE", n=300, b=1)
    assert r.years_with_discount >= K.MIN_YEARS_WITH_DISCOUNT
    loyo = binf.leave_one_year_out(r.obs)
    assert all(np.isfinite(v) for v in loyo.per_year_beta_T.values())


def test_cb07_evaluability_requires_all_four_conjuncts():
    assert bcls.evaluable(True, True, True, 3)
    assert not bcls.evaluable(True, True, True, 2)
    assert not bcls.evaluable(True, True, False, 5)
    assert not bcls.evaluable(True, False, True, 5)
    assert not bcls.evaluable(False, True, True, 5)


def test_cb08_a_two_year_sample_is_class_F_not_a_verdict():
    cell = world("TRADABLE_CONVERGENCE", n=40)          # ~120 business days of signals
    r = run(cell, b=20)
    assert r.years_with_discount < K.MIN_YEARS_WITH_DISCOUNT
    v = bpipe.classify_primary(r)
    assert v.klass == "F" and v.research_status == "unresolved"
    assert v.qualifier == "IDENTIFICATION_INSUFFICIENT_FOR_THE_CLAIM"


# --------------------------------------------------------------------------- #
# §24 / §25 — the real-data firewall and the hard run guard                     #
# --------------------------------------------------------------------------- #


def test_fw01_every_s2_validation_path_is_synthetic():
    src = fx.source(world("TRADABLE_CONVERGENCE", n=5))
    assert src.data_kind == auth.SYNTHETIC
    bdata.assert_synthetic(src)
    assert bdata.synthetic_source_cannot_reach_production_paths(src)
    assert not hasattr(src, "_dir")


def test_fw02_a_real_source_is_rejected_by_the_s2_harness():
    class Pretend(bdata.CellSource):
        data_kind = auth.REAL

        def load(self, ticker):
            raise AssertionError("must never be reached")

    with pytest.raises(AssertionError):
        bdata.assert_synthetic(Pretend())
    assert not bdata.synthetic_source_cannot_reach_production_paths(Pretend())


def test_gd01_a_historical_run_without_a_committed_grant_is_blocked():
    st = auth.authorization_status()
    assert st["active_execution_authorizations"] == 0
    assert st["real_run_authorized"] is False
    with pytest.raises(auth.RunNotAuthorized):
        auth.require_run_authorization(auth.REAL, run_id="BENB-RUN-0001")
    with pytest.raises(auth.RunNotAuthorized):
        auth.require_run_authorization("MAYBE")
    auth.require_run_authorization(auth.SYNTHETIC)      # synthetic is always allowed


def test_gd02_the_guard_fires_before_any_historical_file_is_opened(monkeypatch):
    opened = []
    real_open = open

    def tracking_open(path, *a, **kw):
        opened.append(str(path))
        return real_open(path, *a, **kw)

    monkeypatch.setattr("builtins.open", tracking_open)
    with pytest.raises(auth.RunNotAuthorized):
        bdata.RealCellSource()
    monkeypatch.undo()
    touched = [p for p in opened
               if any(s in p for s in ("ohlc", "nav_daily", "fund_download"))]
    assert not touched, touched


def test_gd03_grants_are_read_from_committed_state_only():
    src = source_of("benb_authorization.py")
    assert re.search(r'"git",\s*"show"', src)
    assert auth.LEDGER_RELPATH == "ops/EXECUTION_AUTHORIZATIONS.md"
    assert auth.read_committed(auth.LEDGER_RELPATH) is not None
    assert auth.AUTH_ID_PREFIX == "BENB-AUTH"
    assert auth.read_committed("ops/NO_SUCH_LEDGER.md") is None


def test_gd04_the_outcome_chain_performs_no_file_access_at_all():
    """`benb_contract` is deliberately excluded: it OWNS `DATA_DIR`, which is exactly
    why only `benb_data.RealCellSource` - the one class behind the guard - may use it.

    Every other module on the path from a price to a verdict is checked for any file
    access at all, and for any reference to the historical directory."""
    for mod in ("benb_feature.py", "benb_engine.py", "benb_inference.py",
                "benb_classify.py", "benb_pipeline.py", "benb_oracle.py",
                "benb_fixtures.py"):
        src = source_of(mod)
        for token in ("DATA_DIR", "data/benb", chr(92).join(("data", "benb")),
                      "PINNED", "read_csv", "urlopen", "requests", "subprocess"):
            assert token not in src, (mod, token)
        # parsed, not grepped: the string "open(t+1)" is a POSITION LEG, not a call
        assert not called_names(src) & {"open", "exec", "eval", "compile",
                                        "__import__"}, mod
    # only the guarded real source and the driver name the historical directory
    users = [m for m in ("benb_data.py", "benb_pipeline.py", "benb_s2_build.py")
             if "DATA_DIR" in source_of(m)]
    assert users == ["benb_data.py", "benb_s2_build.py"], users
    body = source_of("benb_data.py")
    assert body.index("class RealCellSource") < body.index("K.DATA_DIR")


# --------------------------------------------------------------------------- #
# §26 — metadata-only structural validation of the pinned REAL files            #
# --------------------------------------------------------------------------- #


@needs_data
def test_meta01_pinned_hashes_reproduce():
    import hashlib
    for name, want in K.PINNED.items():
        with open(os.path.join(K.DATA_DIR, name), "rb") as fh:
            assert hashlib.sha256(fh.read()).hexdigest() == want, name


@needs_data
def test_meta02_structural_date_counts_only_no_values_are_joined():
    """Date SETS only. No price and no NAV value is parsed, so no basis can form."""
    import csv
    for tick, want_common in K.STRUCTURAL_COMMON.items():
        with open(os.path.join(K.DATA_DIR, "%s_raw_ohlc.csv" % tick),
                  encoding="utf-8", newline="") as fh:
            rd = csv.DictReader(fh)
            key = [c for c in rd.fieldnames if c.lower().startswith("date")][0]
            pdates = {_dt.date.fromisoformat(r[key][:10]) for r in rd}
        with open(os.path.join(K.DATA_DIR, "%s_nav_daily.csv" % tick),
                  encoding="utf-8", newline="") as fh:
            ndates = {_dt.date.fromisoformat(r["date"]) for r in csv.DictReader(fh)}
        assert len(bdata.align_grid(pdates, ndates)) == want_common, tick


# --------------------------------------------------------------------------- #
# §27 — the S3 result artifact                                                 #
# --------------------------------------------------------------------------- #


def test_rep01_schema_is_complete_and_stamped_synthetic():
    r = _res("STALE_NAV", n=300, b=60)
    v = bpipe.classify_primary(r)
    doc = brep.build_result(data_kind=auth.SYNTHETIC, verdict=v, primary=r,
                            secondary_summary=None)
    chk = brep.validate_result(doc)
    assert chk["ok"], chk["problems"]
    assert doc["synthetic_only"] == "YES" and doc["run_authorization_id"] is None
    for f in brep.REQUIRED_FIELDS:
        assert f in doc
    assert doc["evidence_ceiling"] == "supported"
    assert doc["classification_flags"]["m2_operator"] == "STRICT >"
    assert doc["classification_flags"]["m2_value"] == 0.30
    assert "REDUCED-FORM" in doc["forbidden_interpretations"]
    assert "MIXED / DEPENDENT" in doc["basis_data_provenance_warning"]
    assert doc["seal_manifest_sha256"] == K.SEAL_MANIFEST_SHA256


def test_rep02_a_real_artifact_without_a_grant_is_refused():
    r = _res("STALE_NAV", n=300, b=20)
    v = bpipe.classify_primary(r)
    with pytest.raises(ValueError):
        brep.build_result(data_kind="REAL", verdict=v, primary=r,
                          run_authorization_id=None)


def test_rep03_an_artifact_whose_status_contradicts_its_class_is_rejected():
    r = _res("STALE_NAV", n=300, b=20)
    v = bpipe.classify_primary(r)

    def doc(**over):
        d = dict(brep.build_result(data_kind=auth.SYNTHETIC, verdict=v, primary=r))
        d.update(over)
        return d

    assert not brep.validate_result(
        doc(final_class="F", research_status="unresolved", qualifier=""))["ok"]
    assert not brep.validate_result(doc(research_status="confirmed"))["ok"]
    assert not brep.validate_result(doc(evidence_ceiling="confirmed"))["ok"]
    assert not brep.validate_result(doc(synthetic_only="NO"))["ok"]
    assert brep.validate_result(doc())["ok"]


def test_rep04_the_writer_refuses_to_persist_an_invalid_artifact(tmp_path):
    r = _res("STALE_NAV", n=300, b=20)
    v = bpipe.classify_primary(r)
    bad = dict(brep.build_result(data_kind=auth.SYNTHETIC, verdict=v, primary=r))
    bad["research_status"] = "confirmed"
    with pytest.raises(AssertionError):
        brep.write_result(bad, str(tmp_path / "bad.json"))
    assert not (tmp_path / "bad.json").exists()
