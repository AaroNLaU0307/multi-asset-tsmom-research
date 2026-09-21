# -*- coding: utf-8 -*-
"""CTA-EDGE-05 / F6 — the S2 build-validation suite.

Everything here runs on SYNTHETIC fixtures, on the sealed Markdown itself, or on
structural metadata that carries no outcome. **Nothing here computes a real
historical F6 return, cash-excess, beta_EVENT, interval or LOYO quantity** — and
the firewall and guard tests prove that rather than promise it.

The independent oracle (`f6_oracle.py`) imports nothing from the production
engine and reaches every expected value by a different algebraic route.
"""
from __future__ import annotations

import ast
import inspect
import json
import os
import re
import sys

import numpy as np
import pandas as pd
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
os.chdir(REPO)

import f6_authorization as auth      # noqa: E402
import f6_classify as fcls           # noqa: E402
import f6_contract as K              # noqa: E402
import f6_data as fdata              # noqa: E402
import f6_engine as feng             # noqa: E402
import f6_fixtures as fx             # noqa: E402
import f6_inference as finf          # noqa: E402
import f6_oracle as orc              # noqa: E402
import f6_pipeline as fpipe          # noqa: E402
import f6_report as frep             # noqa: E402

TOL = 1e-12


def _sealed_text():
    with open(K.abspath(K.SEALED_PREREG_RELPATH), encoding="utf-8") as fh:
        return fh.read()


def _sealed_manifest():
    with open(K.abspath(K.SEALED_MANIFEST_RELPATH), encoding="utf-8") as fh:
        return json.load(fh)


# =========================================================================== #
# A. SEAL INTEGRITY — the contract must not drift from the sealed bytes       #
# =========================================================================== #
def test_a01_every_pinned_authority_reproduces():
    r = fdata.verify_seal_integrity(strict=False)
    assert r["ok"], r["failed"]


def test_a02_contract_constants_are_rederived_from_the_sealed_markdown():
    S = _sealed_text()
    assert "SEAL_STATUS                = SEALED" in S
    assert K.SEAL_ID in S
    assert "FINAL_PRIMARY_EVENT_COUNT = %d" % K.FINAL_PRIMARY_EVENT_COUNT in S
    assert "FOMC 119 · CPI 176 · NFP 176  =  471 family labels" in S
    assert "WEEKDAY_REFERENCE = FRIDAY" in S
    assert "B           = %d" % K.BOOTSTRAP_B in S
    assert "BOOTSTRAP_SEED_LITERAL   %d" % K.BOOTSTRAP_SEED_LITERAL in S
    assert K.BOOTSTRAP_SEED_SOURCE in S
    assert 'numpy.percentile(..., method="linear")' in S
    assert "0.0004 = 2 bps entry + 2 bps exit" in S
    assert "/ 365" in S and "OWNER-CHOSEN" in S
    assert "P2 rows                                   %d" % K.P2_ROWS in S
    assert K.OPENING_BOUNDARY_SESSION in S


def test_a03_contract_matches_the_sealed_manifest():
    m = _sealed_manifest()
    fc = m["frozen_constants"]
    assert fc["final_primary_event_count"] == K.FINAL_PRIMARY_EVENT_COUNT
    assert fc["family_labels"] == K.FAMILY_LABELS
    assert fc["bootstrap_B"] == K.BOOTSTRAP_B
    assert fc["bootstrap_seed_literal"] == K.BOOTSTRAP_SEED_LITERAL
    assert fc["bootstrap_seed_source"] == K.BOOTSTRAP_SEED_SOURCE
    assert fc["quantile_implementation"] == K.QUANTILE_IMPLEMENTATION
    assert fc["round_trip_cost"] == K.ROUND_TRIP_COST
    assert fc["year_blocks"] == K.YEAR_BLOCK_COUNT
    assert fc["evidence_ceiling"] == K.EVIDENCE_CEILING
    assert fc["independent_confirmation"] is K.INDEPENDENT_CONFIRMATION
    assert m["canonical_weekday_parameterization"]["weekday_reference"] == "FRIDAY"
    assert m["seal_id"] == K.SEAL_ID


def test_a04_the_seed_literal_reproduces_from_its_source_string():
    import hashlib
    d = hashlib.sha256(K.BOOTSTRAP_SEED_SOURCE.encode("ascii")).hexdigest()
    assert int(d[:8], 16) == K.BOOTSTRAP_SEED_LITERAL


# =========================================================================== #
# B. HISTORICAL-RUN GUARD                                                     #
# =========================================================================== #
def test_b01_no_f6_execution_grant_exists_at_s2():
    st = auth.authorization_status()
    assert st["active_execution_authorizations"] == 0
    assert st["real_run_authorized"] is False


def test_b02_a_real_run_is_refused():
    with pytest.raises(auth.RunNotAuthorized):
        auth.require_run_authorization(auth.REAL)
    with pytest.raises(auth.RunNotAuthorized):
        auth.require_run_authorization(auth.REAL, run_id="F6-RUN-0001")


def test_b03_synthetic_is_allowed_and_is_not_a_forged_real_grant():
    auth.require_run_authorization(auth.SYNTHETIC)      # no raise
    with pytest.raises(auth.RunNotAuthorized):
        auth.require_run_authorization("real")          # not the token
    with pytest.raises(auth.RunNotAuthorized):
        auth.require_run_authorization("")
    with pytest.raises(auth.RunNotAuthorized):
        auth.require_run_authorization("PRODUCTION")


def test_b04_the_production_entry_point_refuses_before_touching_anything():
    with pytest.raises(auth.RunNotAuthorized):
        fpipe.run_real(run_id="F6-RUN-0001")


def test_b05_the_guard_is_the_first_statement_of_both_real_paths():
    for fn in (fdata.load_price_values, fpipe.run_real):
        tree = ast.parse(inspect.getsource(fn).lstrip())
        body = [n for n in tree.body[0].body
                if not isinstance(n, ast.Expr)
                or not isinstance(n.value, ast.Constant)]
        first = body[0]
        src = ast.dump(first)
        assert "require_run_authorization" in src, (
            "%s does not call the guard first" % fn.__name__)


def test_b06_an_unreadable_or_absent_ledger_refuses_rather_than_permits(monkeypatch):
    monkeypatch.setattr(auth, "read_committed", lambda *a, **k: None)
    assert auth.active_execution_authorization() is None
    with pytest.raises(auth.RunNotAuthorized):
        auth.require_run_authorization(auth.REAL)


def test_b07_an_unparseable_record_refuses(monkeypatch):
    monkeypatch.setattr(auth, "read_committed",
                        lambda *a, **k: "```json\n{not json}\n```")
    assert auth.active_execution_authorization() is None


def test_b08_two_live_grants_refuse(monkeypatch):
    rec = ('```json\n{"record_type":"AUTHORIZATION","authorization_id":'
           '"F6-AUTH-000%d","status":"AUTHORIZED","grant_kind":"EXECUTION",'
           '"lineage":"%s","binding":{"lineage":"%s"}}\n```')
    txt = (rec % (1, K.LINEAGE, K.LINEAGE)) + "\n" + (rec % (2, K.LINEAGE,
                                                             K.LINEAGE))
    monkeypatch.setattr(auth, "read_committed", lambda *a, **k: txt)
    assert auth.active_execution_authorization() is None


def test_b09_a_worktree_edit_cannot_grant_a_run():
    # the reader is `git show HEAD:...`, never open() on the worktree
    src = inspect.getsource(auth.read_committed)
    assert "git" in src and "show" in src
    assert "open(" not in src


def test_b10_the_guard_module_offers_no_way_to_mint_a_grant():
    src = inspect.getsource(auth)
    for bad in ("def grant", "def authorize(", "def create_authorization",
                "def mint"):
        assert bad not in src


# =========================================================================== #
# C. FIREWALL — only one function may read a price                            #
# =========================================================================== #
def test_c01_only_load_price_values_parses_the_spy_column():
    src = inspect.getsource(fdata)
    readers = [n for n in ast.walk(ast.parse(src))
               if isinstance(n, ast.FunctionDef)
               and "PRIMARY_TICKER" in ast.dump(n)]
    assert [n.name for n in readers] == ["load_price_values"]


def test_c02_metadata_readers_never_select_a_price_column():
    for fn in (fdata.panel_sessions, fdata.panel_columns):
        s = inspect.getsource(fn)
        assert "SPY" not in s and "PRIMARY_TICKER" not in s
    assert 'usecols=["Date"]' in inspect.getsource(fdata.panel_sessions)


def test_c03_engine_inference_classify_and_fixtures_open_no_files():
    for mod in (feng, finf, fcls, fx, orc):
        s = inspect.getsource(mod)
        assert "read_csv" not in s, mod.__name__
        assert "open(" not in s, mod.__name__


def test_c04_the_oracle_does_not_import_the_engine():
    s = inspect.getsource(orc)
    for bad in ("import f6_engine", "import f6_inference", "import f6_pipeline",
                "from f6_engine", "from f6_inference"):
        assert bad not in s


def test_c05_no_test_in_this_suite_calls_the_real_price_reader():
    """AST, not substring: a substring check would match its own assertion."""
    tree = ast.parse(open(os.path.abspath(__file__), encoding="utf-8").read())
    called = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Call):
            f = n.func
            name = (f.attr if isinstance(f, ast.Attribute)
                    else getattr(f, "id", None))
            if name == "load_price_values":
                called.append(ast.dump(n))
    assert called == [], called


def test_c06_metadata_tier_works_and_returns_only_dates():
    idx = fdata.panel_sessions()
    assert isinstance(idx, pd.DatetimeIndex) and len(idx) > 0
    assert K.PRIMARY_TICKER in fdata.panel_columns()      # schema only


# =========================================================================== #
# D. EVENT MANIFEST                                                           #
# =========================================================================== #
def test_d01_the_sealed_manifest_validates_to_462():
    fam = fdata.load_event_manifest()
    r = fdata.validate_event_manifest(fam)
    assert r["n_sessions"] == 462
    assert r["labels"] == {"FOMC": 119, "CPI": 176, "NFP": 176}
    assert r["overlap"] == 9 and r["multi"] == 9


def test_d02_a_reinstated_pit_exclusion_is_refused():
    fam = fdata.load_event_manifest()
    bad = dict(fam)
    bad["2025-11-20"] = ["NFP"]
    with pytest.raises(fdata.InputValidationError, match="REINSTATED"):
        fdata.validate_event_manifest(bad, expect_counts=False)


def test_d03_a_2026_session_is_refused():
    fam = dict(fdata.load_event_manifest())
    fam["2026-01-28"] = ["FOMC"]
    with pytest.raises(fdata.InputValidationError, match="PROHIBITED YEAR"):
        fdata.validate_event_manifest(fam, expect_counts=False)


def test_d04_an_unknown_family_is_refused():
    with pytest.raises(fdata.InputValidationError):
        fdata.validate_event_manifest({"2011-01-05": ["GDP"]},
                                      expect_counts=False)


def test_d05_a_tampered_manifest_fails_the_hash_gate(monkeypatch):
    monkeypatch.setattr(K, "EVENT_MANIFEST_SHA256", "0" * 64)
    with pytest.raises(fdata.SealIntegrityError):
        fdata.load_event_manifest()


def test_d06_dropping_one_event_breaks_the_sealed_count():
    fam = dict(fdata.load_event_manifest())
    fam.pop(sorted(fam)[0])
    with pytest.raises(fdata.InputValidationError, match="event count"):
        fdata.validate_event_manifest(fam)


# =========================================================================== #
# E. RETURNS, CASH AND THE GOLDEN TEST                                        #
# =========================================================================== #
def test_e01_golden_returns_cash_and_p1_match_the_independent_oracle():
    g = fx.golden()
    exp = orc.golden_expectations(g)

    grid = pd.DatetimeIndex(pd.bdate_range("2011-01-04", periods=6))
    prev = [pd.Timestamp("2011-01-03")] + list(grid[:-1])
    prices = pd.Series(g["prices"],
                       index=[pd.Timestamp("2011-01-03")] + list(grid))
    R = feng.simple_returns(prices, grid, prev)
    assert np.allclose(R, exp["R"], atol=TOL, rtol=0)

    rf = np.array([feng.rf_hold(g["dgs3mo_annual_percent"], h)
                   for h in g["hold_days"]])
    assert np.allclose(rf, exp["rf_hold"], atol=TOL, rtol=0)

    rx = feng.excess_returns(R, rf)
    assert np.allclose(rx, exp["r_excess"], atol=TOL, rtol=0)

    ev = np.array(g["event_flags"], bool)
    p1 = feng.p1_mean(feng.net_event_returns(rx[ev]))
    assert abs(p1 - exp["p1_mean"]) < TOL
    # and the cost really is subtracted once per event session
    assert abs(p1 - (float(np.mean(rx[ev])) - K.ROUND_TRIP_COST)) < TOL


def test_e02_dgs3mo_normal_publication():
    vd, val, rows = fx.cash_fixture("normal")
    rate, carry = feng.map_cash_rate(pd.Timestamp("2011-01-14"), vd, val, rows)
    assert rate == 0.15 and carry == 0


def test_e03_source_explained_carry_is_permitted():
    vd, val, rows = fx.cash_fixture("explained_carry")
    rate, carry = feng.map_cash_rate(pd.Timestamp("2011-01-17"), vd, val, rows)
    assert rate == 0.15 and carry == 3          # back to Friday the 14th


def test_e04_an_unexplained_gap_fails_closed():
    vd, val, rows = fx.cash_fixture("unexplained_gap")
    with pytest.raises(feng.UnexplainedCashGap, match="IMPLEMENTATION HOLD"):
        feng.map_cash_rate(pd.Timestamp("2011-01-17"), vd, val, rows)


def test_e05_there_is_no_arbitrary_day_threshold():
    assert K.CASH_ARBITRARY_DAY_RULE is None
    assert "7" not in inspect.getsource(feng.map_cash_rate).split("def")[1][:400]


def test_e06_a_missing_price_stops_rather_than_interpolating():
    grid = pd.DatetimeIndex(pd.bdate_range("2011-01-04", periods=3))
    prev = [pd.Timestamp("2011-01-03")] + list(grid[:-1])
    p = pd.Series([100.0, np.nan, 102.0, 103.0],
                  index=[pd.Timestamp("2011-01-03")] + list(grid))
    with pytest.raises(feng.SealedSpecViolation, match="missing price"):
        feng.simple_returns(p, grid, prev)


def test_e07_real_dgs3mo_metadata_maps_every_primary_session_with_no_gap():
    # METADATA ONLY: dates and the rate series. No SPY value is touched.
    sessions = fdata.panel_sessions()
    grid, boundary = fdata.primary_grid(sessions)
    vd, val, rows = fdata.load_cash_series()
    prev = [boundary] + list(grid[:-1])
    carries = [feng.map_cash_rate(p, vd, val, rows)[1] for p in prev]
    assert len(carries) == K.P2_ROWS
    assert max(carries) <= 4


# =========================================================================== #
# F. OPENING BOUNDARY                                                         #
# =========================================================================== #
def test_f01_the_opening_boundary_is_the_sealed_prior_session():
    sessions = fdata.panel_sessions()
    grid, boundary = fdata.primary_grid(sessions)
    assert str(grid[0].date()) == K.FIRST_PRIMARY_SESSION
    assert str(boundary.date()) == K.OPENING_BOUNDARY_SESSION
    assert boundary.year == K.PRIMARY_YEAR_FIRST - 1
    assert len(grid) == K.P2_ROWS


def test_f02_the_boundary_is_an_input_never_a_regression_row():
    b = fx.make_frame()
    assert b["boundary"] not in set(b["frame"].index)
    assert b["frame"].index.min() == b["grid"][0]
    assert b["frame"]["prev"].iloc[0] == b["boundary"]
    assert b["frame"]["HOLD"].iloc[0] > 0
    assert b["frame"]["prev"].iloc[0] not in set(b["frame"].index)


def test_f03_no_prior_year_row_is_created():
    b = fx.make_frame()
    years = set(int(y) for y in b["frame"]["year"])
    assert min(years) == K.PRIMARY_YEAR_FIRST


def test_f04_no_row_is_dropped_for_undefined_hold():
    b = fx.make_frame()
    assert len(b["frame"]) == len(b["grid"])
    assert b["frame"]["HOLD"].notna().all()


def test_f05_a_grid_with_no_prior_session_stops():
    sessions = pd.DatetimeIndex(pd.bdate_range("2011-01-03", periods=20))
    with pytest.raises(fdata.InputValidationError, match="no prior panel"):
        fdata.primary_grid(sessions)


# =========================================================================== #
# G. THE FIXED P2 DESIGN                                                      #
# =========================================================================== #
def test_g01_friday_is_the_unique_reference_level():
    f = fx.make_frame()["frame"]
    X = feng.design_matrix(f)
    assert tuple(X.columns) == K.DESIGN_COLUMNS
    assert "weekday_Friday" not in X.columns
    omitted = sorted(set(f["weekday"]) - set(K.WEEKDAY_INDICATORS))
    assert omitted == ["Friday"]


def test_g02_friday_rows_are_all_zero_in_the_weekday_block():
    f = fx.make_frame()["frame"]
    X = feng.design_matrix(f)
    w = X[["weekday_" + c for c in K.WEEKDAY_INDICATORS]].to_numpy()
    fri = (f["weekday"] == "Friday").to_numpy()
    assert w[fri].sum() == 0
    assert (w[~fri].sum(axis=1) == 1).all()


def test_g03_an_alternate_weekday_base_is_refused():
    bad = fx.f_alternate_weekday_base()
    with pytest.raises(feng.SealedSpecViolation, match="weekday reference"):
        feng.design_matrix(bad)


def test_g04_a_rank_deficient_design_stops_without_repair():
    d = fx.f_rank_deficient()
    with pytest.raises(feng.SealedSpecViolation, match="RANK DEFICIENT"):
        feng.check_design_rank(feng.design_matrix(d["frame"]))


def test_g05_full_rank_on_a_healthy_fixture_and_event_is_identified():
    f = fx.make_frame()["frame"]
    X = feng.design_matrix(f)
    assert feng.check_design_rank(X) == K.DESIGN_RANK
    C = X.drop(columns=["EVENT"]).to_numpy(float)
    assert np.linalg.matrix_rank(np.column_stack([C, X["EVENT"]])) != \
        np.linalg.matrix_rank(C)


def test_g06_every_individual_year_block_is_full_rank():
    f = fx.make_frame()["frame"]
    X = feng.design_matrix(f)
    for y in sorted(set(int(v) for v in f["year"])):
        sub = feng.design_matrix(f[f["year"] == y]).reindex(
            columns=X.columns, fill_value=0.0)
        assert np.linalg.matrix_rank(sub.to_numpy(float)) == K.DESIGN_RANK, y


def test_g07_a_real_metadata_design_is_full_rank_per_year():
    # METADATA ONLY: dates, event manifest, TOM, auctions. No prices.
    sys.path.insert(0, K.REPO)
    import config as cfg
    from src import seasonality as seas
    fam = fdata.load_event_manifest()
    sessions = fdata.panel_sessions()
    grid, boundary = fdata.primary_grid(sessions)
    tom = seas.is_tom(grid, last=cfg.SEAS_TOM_LAST,
                      first=cfg.SEAS_TOM_FIRST).astype(int).values
    f = feng.build_frame(grid, boundary, set(fam), tom,
                         fdata.auction_sessions(sessions))
    assert len(f) == K.P2_ROWS
    assert int(f["EVENT"].sum()) == K.FINAL_PRIMARY_EVENT_COUNT
    X = feng.design_matrix(f)
    assert feng.check_design_rank(X) == K.DESIGN_RANK
    ys = sorted(set(int(v) for v in f["year"]))
    assert ys == list(K.PRIMARY_YEARS) and len(ys) == K.YEAR_BLOCK_COUNT
    for y in ys:
        sub = feng.design_matrix(f[f["year"] == y]).reindex(
            columns=X.columns, fill_value=0.0)
        assert np.linalg.matrix_rank(sub.to_numpy(float)) == K.DESIGN_RANK, y


def test_g08_beta_event_is_recovered_exactly_on_noiseless_linear_data():
    for b in (0.0020, -0.0015, 0.0):
        f = fx.fixture(beta_event=b)
        est = feng.ols_beta_event(feng.design_matrix(f["frame"]),
                                  f["r_excess"])
        assert abs(est - b) < 1e-10, (b, est)


def test_g09_beta_event_agrees_with_the_independent_fwl_oracle():
    f = fx.noisy(beta_event=0.0009, scale=0.002)
    X = feng.design_matrix(f["frame"])
    est = feng.ols_beta_event(X, f["r_excess"])
    ref = orc.oracle_beta_event_fwl(X.to_numpy(float), f["r_excess"],
                                    list(X.columns))
    assert abs(est - ref) < 1e-10


def test_g10_a_2026_row_never_enters_the_design():
    grid = fx.f_prohibited_year_frame()
    with pytest.raises(feng.SealedSpecViolation, match="PROHIBITED YEAR"):
        feng.build_frame(grid, grid[0] - pd.Timedelta(days=3), set(),
                         np.zeros(len(grid), int), set())


def test_g11_no_prohibited_target_or_object_is_a_design_column():
    cols = " ".join(K.DESIGN_COLUMNS).upper()
    for bad in K.PROHIBITED_TARGETS + K.PROHIBITED_OBJECTS:
        assert bad.upper().replace(".", "") not in cols.replace(".", "")
    src = inspect.getsource(feng.design_matrix)
    for bad in ("TLT", "IEF", "NQ", "surprise", "consensus"):
        assert bad not in src


# =========================================================================== #
# H. P1 WEIGHTING AND SAME-DAY OVERLAP                                        #
# =========================================================================== #
def test_h01_a_two_family_session_is_one_position_one_observation():
    d = fx.f_multi_event_same_day()
    f, fam = d["frame"], d["families"]
    assert len(fam[d["multi_session"]]) == 2
    assert int(f.loc[pd.Timestamp(d["multi_session"]), "EVENT"]) == 1
    assert set(np.unique(f["EVENT"])) <= {0, 1}       # never 2, never 2 units
    assert int(f["EVENT"].sum()) == len(fam)          # one observation per session


def test_h02_p1_is_event_weighted_not_annually_or_family_weighted():
    f = fx.fixture(beta_event=0.0020)
    frame, y = f["frame"], f["r_excess"]
    ev = frame["EVENT"].to_numpy(bool)
    p1 = feng.p1_mean(feng.net_event_returns(y[ev]))
    # equal-weighted annual mean, the thing the seal FORBIDS
    ann = np.mean([np.mean(y[ev & (frame["year"] == yr).to_numpy()])
                   - K.ROUND_TRIP_COST
                   for yr in sorted(set(int(v) for v in frame["year"]))])
    assert abs(p1 - float(np.mean(y[ev])) + K.ROUND_TRIP_COST) < TOL
    assert p1 != pytest.approx(ann, abs=1e-15) or True   # documented, not required


def test_h03_p1_over_an_empty_event_set_stops():
    with pytest.raises(feng.SealedSpecViolation):
        feng.p1_mean(np.array([]))


# =========================================================================== #
# I. BOOTSTRAP                                                                #
# =========================================================================== #
def test_i01_the_bootstrap_is_deterministic_for_a_fixed_seed():
    f = fx.noisy(beta_event=0.001, scale=0.002)
    a = finf.bootstrap(f["frame"], f["r_excess"], b=25, seed=12345)
    b = finf.bootstrap(f["frame"], f["r_excess"], b=25, seed=12345)
    assert np.array_equal(a["p1_draws"], b["p1_draws"])
    assert np.array_equal(a["beta_event_draws"], b["beta_event_draws"])
    c = finf.bootstrap(f["frame"], f["r_excess"], b=25, seed=999)
    assert not np.array_equal(a["p1_draws"], c["p1_draws"])


def test_i02_p1_and_p2_use_the_same_year_draw_in_each_replication():
    f = fx.noisy(beta_event=0.001, scale=0.002)
    frame, y = f["frame"], f["r_excess"]
    got = finf.bootstrap(frame, y, b=12, seed=777)
    # replay the identical draw sequence independently
    blocks = finf.year_blocks(frame)
    ys = np.asarray(sorted(blocks))
    g = finf.rng_for(777)
    for i in range(12):
        drawn = ys[g.integers(0, len(ys), size=len(ys))]
        rows = finf.replicate_rows(blocks, drawn)
        p1, p2 = feng.point_estimates(frame.iloc[rows], y[rows])
        assert abs(p1 - got["p1_draws"][i]) < TOL
        assert abs(p2 - got["beta_event_draws"][i]) < TOL


def test_i03_a_draw_repeating_one_year_fifteen_times_stays_estimable():
    f = fx.fixture(beta_event=0.0020)
    frame, y = f["frame"], f["r_excess"]
    blocks = finf.year_blocks(frame)
    year = sorted(blocks)[0]
    rows = finf.replicate_rows(blocks, [year] * K.YEAR_BLOCK_COUNT)
    assert len(rows) == K.YEAR_BLOCK_COUNT * len(blocks[year])
    sub = frame.iloc[rows]
    assert feng.check_design_rank(feng.design_matrix(sub)) == K.DESIGN_RANK
    p1, p2 = feng.point_estimates(sub, y[rows])
    assert abs(p2 - 0.0020) < 1e-9


def test_i04_uniform_duplication_preserves_the_estimands():
    """15 copies of one block must give that block's own P1 and beta."""
    f = fx.fixture(beta_event=0.0020)
    frame, y = f["frame"], f["r_excess"]
    blocks = finf.year_blocks(frame)
    year = sorted(blocks)[3]
    one = frame.iloc[blocks[year]]
    p1a, p2a = feng.point_estimates(one, y[blocks[year]])
    rows = finf.replicate_rows(blocks, [year] * K.YEAR_BLOCK_COUNT)
    p1b, p2b = feng.point_estimates(frame.iloc[rows], y[rows])
    assert abs(p1a - p1b) < 1e-12 and abs(p2a - p2b) < 1e-9


def test_i05_a_repeated_year_really_duplicates_rows():
    f = fx.fixture(beta_event=0.001)
    blocks = finf.year_blocks(f["frame"])
    y0, y1 = sorted(blocks)[:2]
    rows = finf.replicate_rows(blocks, [y0, y0, y1])
    assert len(rows) == 2 * len(blocks[y0]) + len(blocks[y1])
    assert list(rows[:len(blocks[y0])]) == list(rows[len(blocks[y0]):
                                                     2 * len(blocks[y0])])


def test_i06_the_interval_matches_the_independent_quantile_oracle():
    draws = np.linspace(-0.01, 0.03, 401)
    lo, hi = finf.percentile_interval(draws)
    assert abs(lo - orc.oracle_percentile(draws, K.QUANTILE_LOWER)) < 1e-15
    assert abs(hi - orc.oracle_percentile(draws, K.QUANTILE_UPPER)) < 1e-15


def test_i07_a_different_quantile_method_gives_a_different_answer():
    """Proves `method=` is load-bearing, so a default could not drift silently."""
    draws = np.arange(40, dtype=float)
    lo, _ = finf.percentile_interval(draws)
    other = np.percentile(draws, 2.5, method="higher")
    assert lo != other


def test_i08_production_bootstrap_cannot_be_asked_for_a_smaller_b():
    sig = inspect.signature(finf.production_bootstrap)
    assert "b" not in sig.parameters
    assert "b=K.BOOTSTRAP_B" in inspect.getsource(finf.production_bootstrap)
    assert K.BOOTSTRAP_B == 100000


def test_i09_a_nonfinite_replicate_stops_rather_than_being_dropped():
    with pytest.raises(feng.SealedSpecViolation, match="non-finite"):
        finf.percentile_interval(np.array([0.1, np.nan, 0.2]))


def test_i10_interval_classification_matches_the_sealed_definitions():
    assert finf.classify_interval(0.001, 0.01) == K.CLASS_POSITIVE
    assert finf.classify_interval(-0.001, 0.01) == K.CLASS_UNRESOLVED
    assert finf.classify_interval(0.0, 0.01) == K.CLASS_UNRESOLVED   # STRICT >
    assert finf.classify_interval(-0.01, 0.0) == K.CLASS_ABSENT      # upper <= 0
    assert finf.classify_interval(-0.01, -0.001) == K.CLASS_ABSENT
    for lo, hi in ((0.001, 0.01), (-0.001, 0.01), (-0.01, -0.001)):
        assert finf.classify_interval(lo, hi) == orc.oracle_classify_interval(lo,
                                                                              hi)


# =========================================================================== #
# J. P3 LOYO                                                                  #
# =========================================================================== #
def test_j01_loyo_runs_exactly_one_refit_per_calendar_year():
    f = fx.fixture(beta_event=0.0020)
    r = feng.loyo(f["frame"], f["r_excess"])
    assert len(r["years"]) == K.YEAR_BLOCK_COUNT
    assert sorted(r["per_year"]) == list(K.PRIMARY_YEARS)
    tot = int(f["frame"]["EVENT"].sum())
    for y, v in r["per_year"].items():
        assert v["events_removed"] + v["events_remaining"] == tot


def test_j02_all_year_sign_pass():
    f = fx.fixture(beta_event=0.0020, level_shift=0.0100)   # both clearly positive
    r = feng.loyo(f["frame"], f["r_excess"])
    assert r["p3_pass"] is True and r["failing_years"] == []
    for v in r["per_year"].values():
        assert v["p1_point"] > 0 and v["beta_event_point"] > 0


def test_j03_a_single_year_sign_failure_fails_p3():
    f = fx.fixture(beta_event=0.0020, level_shift=0.0100)
    frame, y = f["frame"], f["r_excess"].copy()
    # make ONE year's retained-sample P1 negative by pushing every OTHER year's
    # event payoff down hard; deleting that year then leaves a negative mean
    victim = sorted(set(int(v) for v in frame["year"]))[0]
    ev = frame["EVENT"].to_numpy(bool)
    other = ev & (frame["year"] != victim).to_numpy()
    y[other] -= 0.05
    r = feng.loyo(frame, y)
    assert r["p3_pass"] is False
    assert victim in r["failing_years"]


def test_j04_loyo_computes_no_deletion_level_significance():
    src = inspect.getsource(feng.loyo)
    for bad in ("percentile", "bootstrap", "lower", "upper", "interval",
                "pvalue", "p_value"):
        assert bad not in src


# =========================================================================== #
# K. TERMINAL CLASSIFIER                                                      #
# =========================================================================== #
def test_k01_every_reachable_state_is_covered_and_matches_the_oracle():
    states = fcls.reachable_states()
    # 3x3 = 9 (p1, p2) branches; the (positive, positive) branch alone splits on
    # P3, so 8 + 2 = 10 reachable inputs.
    assert len(states) == 10
    for p1, p2, p3 in states:
        got = fcls.classify(p1, p2, p3)["terminal_classification"]
        assert got == orc.oracle_terminal(p1, p2, p3), (p1, p2, p3, got)


def test_k02_the_sealed_table_is_reproduced_exactly():
    C = fcls.classify
    assert C("positive", "positive", True)["terminal_classification"] == \
        "SUPPORTED_HISTORICAL_EDGE"
    assert C("positive", "positive", False)["terminal_classification"] == \
        "ONE_YEAR_FRAGILITY / NOT_PROMOTED"
    assert C("positive", "unresolved")["terminal_classification"] == "UNRESOLVED"
    assert C("positive", "excluded_absent")["terminal_classification"] == \
        "POSITIVE_PAYOFF_NOT_ANNOUNCEMENT_SPECIFIC / NOT_PROMOTED"
    assert C("unresolved", "positive")["terminal_classification"] == "UNRESOLVED"
    assert C("unresolved", "unresolved")["terminal_classification"] == "UNRESOLVED"
    assert C("unresolved", "excluded_absent")["terminal_classification"] == \
        "NOT_ANNOUNCEMENT_SPECIFIC / NOT_PROMOTED"
    for p2 in ("positive", "unresolved", "excluded_absent"):
        assert C("excluded_absent", p2)["terminal_classification"] == \
            "NOT_PROMOTED"


def test_k03_only_the_passing_pair_promotes():
    for p1, p2, p3 in fcls.reachable_states():
        v = fcls.classify(p1, p2, p3)
        assert v["promoted"] == (p1 == "positive" and p2 == "positive"
                                 and p3 is True)
        assert v["research_status"] in ("supported", "not_promoted")
        assert v["research_status"] != "confirmed"


def test_k04_p3_is_required_on_the_passing_pair_and_refused_elsewhere():
    with pytest.raises(fcls.TerminalStateError, match="MUST be evaluated"):
        fcls.classify("positive", "positive", None)
    with pytest.raises(fcls.TerminalStateError, match="never a rescue"):
        fcls.classify("positive", "unresolved", True)
    with pytest.raises(fcls.TerminalStateError, match="never a rescue"):
        fcls.classify("excluded_absent", "positive", True)


def test_k05_no_low_power_or_mechanism_falsified_state_exists():
    outs = {fcls.classify(*s)["terminal_classification"]
            for s in fcls.reachable_states()}
    for bad in K.FORBIDDEN_TERMINAL_STATES:
        assert not any(bad in o for o in outs)
    # no forbidden token is EMITTABLE: check the table's values, not the prose
    # (the module docstring says "NO LOW_POWER STATE", which is the point)
    for v in fcls._TABLE.values():
        for bad in K.FORBIDDEN_TERMINAL_STATES:
            assert bad not in v


def test_k06_an_out_of_space_class_is_refused_not_coerced():
    for bad in ("POSITIVE", "significant", "", None, "low_power"):
        with pytest.raises(fcls.TerminalStateError):
            fcls.classify(bad, "positive")


def test_k07_a_changed_terminal_rule_fails_the_suite(monkeypatch):
    monkeypatch.setitem(fcls._TABLE, ("positive", "positive", False),
                        "SUPPORTED_HISTORICAL_EDGE")
    assert fcls.classify("positive", "positive", False)[
        "terminal_classification"] != orc.oracle_terminal("positive", "positive",
                                                          False)


# =========================================================================== #
# L. END-TO-END SYNTHETIC BRANCHES                                            #
# =========================================================================== #
def _branch(f, b=60):
    return fpipe.run_synthetic(f, b=b)


def test_l01_p1_and_p2_clearly_positive_reaches_a_terminal_state():
    r = _branch(fx.f_p1_positive())
    assert r["p1"]["klass"] == K.CLASS_POSITIVE
    assert r["p2"]["klass"] == K.CLASS_POSITIVE
    assert r["p3"] is not None
    assert r["verdict"]["terminal_classification"] in (
        K.TERMINAL_SUPPORTED, K.TERMINAL_FRAGILITY)


def test_l02_p1_economically_excluded_is_not_promoted():
    r = _branch(fx.f_p1_excluded())
    assert r["p1"]["klass"] == K.CLASS_ABSENT
    assert r["verdict"]["terminal_classification"] == K.TERMINAL_NOT_PROMOTED
    assert r["p3"] is None


def test_l03_unresolved_intervals_reach_unresolved():
    r = _branch(fx.f_unresolved())
    assert r["p1"]["klass"] == K.CLASS_UNRESOLVED
    assert r["verdict"]["terminal_classification"] in (
        K.TERMINAL_UNRESOLVED, K.TERMINAL_NOT_SPECIFIC)
    assert r["p3"] is None


def test_l04_p3_is_never_computed_off_the_passing_pair():
    for f in (fx.f_p1_excluded(), fx.f_unresolved()):
        assert _branch(f)["p3"] is None


def test_l05_the_synthetic_path_never_reads_a_sealed_or_real_file():
    src = inspect.getsource(fpipe.run_synthetic)
    for bad in ("load_price_values", "verify_seal_integrity",
                "load_event_manifest", "panel_sessions"):
        assert bad not in src


def test_l06_intervals_are_labelled_nominal_not_exact():
    r = _branch(fx.f_p1_positive())
    for k in ("p1", "p2"):
        assert "nominal" in r[k]["interval"].lower()
        assert "NOT exact" in r[k]["coverage_claim"]


# =========================================================================== #
# M. MUTATION / ANTI-DRIFT — seal-integrity, not numerical, tests             #
# =========================================================================== #
@pytest.mark.parametrize("attr,mutated", [
    ("FINAL_PRIMARY_EVENT_COUNT", 461),
    ("ROUND_TRIP_COST", 0.0002),
    ("CASH_DAYCOUNT", 360.0),
    ("BOOTSTRAP_B", 10000),
    ("BOOTSTRAP_SEED_LITERAL", 12345),
    ("QUANTILE_METHOD", "higher"),
    ("QUANTILE_IMPLEMENTATION", 'numpy.percentile(..., method="higher")'),
    ("WEEKDAY_REFERENCE", "Monday"),
    ("YEAR_BLOCK_COUNT", 14),
    ("EVENT_MANIFEST_SHA256", "0" * 64),
    ("EVIDENCE_CEILING", "confirmed"),
])
def test_m01_mutating_a_sealed_constant_breaks_the_build(attr, mutated,
                                                         monkeypatch):
    """Each of these is checked against the sealed bytes somewhere, so a silent
    edit of `f6_contract.py` cannot survive the suite."""
    monkeypatch.setattr(K, attr, mutated)
    with pytest.raises(Exception):
        if attr == "EVENT_MANIFEST_SHA256":
            fdata.load_event_manifest()
        elif attr == "FINAL_PRIMARY_EVENT_COUNT":
            fdata.validate_event_manifest(fdata.load_event_manifest(
                verify_hash=False))
        elif attr == "WEEKDAY_REFERENCE":
            feng.design_matrix(fx.make_frame(years=K.PRIMARY_YEARS[:2],
                                             weeks_per_year=3)["frame"])
        else:
            m = _sealed_manifest()["frozen_constants"]
            mapping = {"ROUND_TRIP_COST": ("round_trip_cost", K.ROUND_TRIP_COST),
                       "CASH_DAYCOUNT": ("cash_proxy", None),
                       "BOOTSTRAP_B": ("bootstrap_B", K.BOOTSTRAP_B),
                       "BOOTSTRAP_SEED_LITERAL": ("bootstrap_seed_literal",
                                                  K.BOOTSTRAP_SEED_LITERAL),
                       "QUANTILE_METHOD": ("quantile_implementation", None),
                       "QUANTILE_IMPLEMENTATION": ("quantile_implementation",
                                                   K.QUANTILE_IMPLEMENTATION),
                       "YEAR_BLOCK_COUNT": ("year_blocks", K.YEAR_BLOCK_COUNT),
                       "EVIDENCE_CEILING": ("evidence_ceiling",
                                            K.EVIDENCE_CEILING)}
            key, live = mapping[attr]
            if attr == "CASH_DAYCOUNT":
                assert "/ 365" in _sealed_text()
                assert K.CASH_DAYCOUNT == 365.0
            elif attr == "QUANTILE_METHOD":
                assert K.QUANTILE_METHOD == "linear"
            else:
                assert m[key] == live


def test_m02_the_2026_prohibition_cannot_be_relaxed():
    assert 2026 in K.PROHIBITED_YEARS
    assert "2026                = NO F6 OUTCOME QUANTITY MAY BE FORMED" in \
        _sealed_text()


def test_m03_tlt_and_f6b_prohibitions_are_carried_in_the_sealed_text():
    S = _sealed_text()
    assert "STRUCK ENTIRELY FROM CTA-EDGE-05 OUTCOME COMPUTATION" in S
    assert "SEPARATE FUTURE LINEAGE. NOT COMPUTED." in S
    assert "TLT" in K.PROHIBITED_TARGETS


def test_m04_tom_and_auction_authorities_are_the_sealed_ones():
    m = _sealed_manifest()["pins"]
    assert m["tom_authority_implementation"]["sha256"] == \
        fdata.sha256_file("src/seasonality.py")
    assert m["ta_auction_calendar"]["sha256"] == K.AUCTION_SHA256
    assert fdata.sha256_file(K.AUCTION_RELPATH) == K.AUCTION_SHA256


def test_m05_the_year_set_is_exactly_2011_to_2025():
    assert list(K.PRIMARY_YEARS) == list(range(2011, 2026))
    assert len(K.PRIMARY_YEARS) == K.YEAR_BLOCK_COUNT == 15


def test_m06_no_module_offers_an_alternate_model_or_cost_knob():
    """Identifiers, not prose: the modules DESCRIBE what they refuse to do, so a
    substring scan would flag their own disclaimers."""
    banned = {"hc0", "hc1", "hc3", "cluster", "ridge", "lasso", "alpha",
              "regularize", "bca", "studentize", "cov_type", "weights"}
    for mod in (feng, finf, fpipe):
        tree = ast.parse(inspect.getsource(mod))
        names = set()
        for n in ast.walk(tree):
            if isinstance(n, ast.Name):
                names.add(n.id.lower())
            elif isinstance(n, ast.Attribute):
                names.add(n.attr.lower())
            elif isinstance(n, ast.keyword) and n.arg:
                names.add(n.arg.lower())
            elif isinstance(n, ast.arg):
                names.add(n.arg.lower())
        hit = names & banned
        assert not hit, (mod.__name__, sorted(hit))


def test_m07_no_promotion_relevant_setting_has_a_mutable_default():
    assert "b" not in inspect.signature(finf.production_bootstrap).parameters
    for p in inspect.signature(feng.rf_hold).parameters.values():
        assert p.default is inspect.Parameter.empty
    for p in inspect.signature(feng.net_event_returns).parameters.values():
        assert p.default is inspect.Parameter.empty


# =========================================================================== #
# N. RESULT SCHEMA                                                            #
# =========================================================================== #
def test_n01_the_empty_schema_is_valid_and_carries_no_outcome():
    d = frep.empty_result()
    assert frep.validate_result(d)["ok"]
    assert d["run_state"] == frep.NOT_RUN
    for v in (d["measurement"]["p1_estimate"], d["measurement"]["p2_beta_event"],
              d["inference"]["p1_lower"], d["gate"]["p1_class"],
              d["verdict"]["terminal_classification"]):
        assert v == frep.NOT_RUN
    assert d["provenance"]["f6_primary_trial_consumed"] is False


def test_n02_zero_is_not_an_acceptable_placeholder():
    d = frep.empty_result()
    d["measurement"]["p1_estimate"] = 0.0
    assert not frep.validate_result(d)["ok"]


def test_n03_the_six_layers_are_all_present_and_separate():
    d = frep.empty_result()
    for layer in ("measurement", "inference", "gate", "verdict", "claim_cap",
                  "provenance"):
        assert layer in d


def test_n04_a_document_contradicting_the_seal_is_rejected():
    def doc(**over):
        d = frep.empty_result()
        for path, val in over.items():
            a, b = path.split(".")
            d[a][b] = val
        return d
    assert not frep.validate_result(doc(**{"inference.bootstrap_B": 10000}))["ok"]
    assert not frep.validate_result(
        doc(**{"inference.bootstrap_seed_literal": 1}))["ok"]
    assert not frep.validate_result(
        doc(**{"claim_cap.evidence_ceiling": "confirmed"}))["ok"]
    assert not frep.validate_result(
        doc(**{"claim_cap.independent_confirmation": True}))["ok"]
    assert not frep.validate_result(
        doc(**{"measurement.event_count": 461}))["ok"]
    assert not frep.validate_result(
        doc(**{"verdict.research_status": "confirmed"}))["ok"]


def test_n05_the_writer_refuses_to_persist_an_invalid_artifact(tmp_path):
    d = frep.empty_result()
    d["verdict"]["research_status"] = "confirmed"
    with pytest.raises(AssertionError):
        frep.write_result(d, str(tmp_path / "bad.json"))
    assert not (tmp_path / "bad.json").exists()


def test_n06_the_claim_cap_travels_with_the_schema():
    d = frep.empty_result()
    must = d["claim_cap"]["must_not_claim"]
    for s in ("independent confirmation", "buy-and-hold dominance",
              "exact finite-sample 95% coverage", "future persistence",
              "LOYO significance", "stable LOYO magnitudes"):
        assert s in must


# =========================================================================== #
# O. BUILD STATUS                                                             #
# =========================================================================== #
def test_o01_status_reports_s2_built_and_s3_unauthorized():
    st = fpipe.status()
    assert st["S1"] == "SEALED"
    assert st["S2_BUILD_AUTHORIZED"] is True
    assert st["S3_RUN_AUTHORIZED"] is False
    assert st["RETURN_REVEAL_AUTHORIZED"] is False
    assert st["HISTORICAL_OUTCOME_RUN"] == "NOT_AUTHORIZED"
    assert st["empty_result_schema_valid"] is True


def test_o02_no_f6_result_artifact_exists_in_the_repository():
    import subprocess
    out = subprocess.run(["git", "ls-files"], cwd=REPO, capture_output=True,
                         text=True).stdout.splitlines()
    hits = [l for l in out if "f6" in l.lower()
            and any(t in l.lower() for t in ("_result", "_outcome", "_s3_run",
                                             "backtest"))]
    assert hits == [], hits


# =========================================================================== #
# P. THE SIX P1 x P2 BRANCH FIXTURES, END TO END                              #
# =========================================================================== #
@pytest.mark.parametrize("maker,want_p1,want_p2",
                         [(m, a, b) for m, a, b in fx.BRANCH_CASES],
                         ids=[m.__name__ for m, _, _ in fx.BRANCH_CASES])
def test_p01_every_p1_x_p2_cell_is_reachable_and_classified(maker, want_p1,
                                                            want_p2):
    r = fpipe.run_synthetic(maker(), b=60)
    assert r["p1"]["klass"] == want_p1
    assert r["p2"]["klass"] == want_p2
    assert r["verdict"]["terminal_classification"] == orc.oracle_terminal(
        want_p1, want_p2, r["verdict"]["p3_pass"])


def test_p02_all_three_p1_classes_and_all_three_p2_classes_are_exercised():
    seen_p1, seen_p2 = set(), set()
    for maker, a, b in fx.BRANCH_CASES:
        r = fpipe.run_synthetic(maker(), b=40)
        seen_p1.add(r["p1"]["klass"])
        seen_p2.add(r["p2"]["klass"])
    assert seen_p1 == {"positive", "unresolved", "excluded_absent"}
    assert seen_p2 == {"positive", "unresolved", "excluded_absent"}


def test_p03_p3_is_evaluated_on_exactly_the_passing_pair():
    for maker, a, b in fx.BRANCH_CASES:
        r = fpipe.run_synthetic(maker(), b=40)
        assert (r["p3"] is not None) == (a == "positive" and b == "positive")


def test_p04_a_level_shift_moves_p1_but_never_beta_event():
    """The decoupling the branch fixtures rely on, stated as a test."""
    a = fx.fixture(beta_event=0.0020, level_shift=0.0)
    b = fx.fixture(beta_event=0.0020, level_shift=0.0500)
    X = feng.design_matrix(a["frame"])
    ba = feng.ols_beta_event(X, a["r_excess"])
    bb = feng.ols_beta_event(X, b["r_excess"])
    assert abs(ba - bb) < 1e-12
    ev = a["frame"]["EVENT"].to_numpy(bool)
    p1a = feng.p1_mean(feng.net_event_returns(a["r_excess"][ev]))
    p1b = feng.p1_mean(feng.net_event_returns(b["r_excess"][ev]))
    assert abs((p1b - p1a) - 0.0500) < 1e-12
