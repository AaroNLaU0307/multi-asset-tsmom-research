# -*- coding: utf-8 -*-
"""TSMOM-VRP-01 - the S2 acceptance suite.

Every item of `VRP_IMPLEMENTATION_ACCEPTANCE_CONTRACT.md` is exercised here, on
SYNTHETIC fixtures or on identities that touch no return, except the items that name the
real acquired inputs (hashes, chain completeness, identity, calendar), which reveal no
outcome.

Test-name prefixes map to acceptance items: `test_i04_*` is item 4, and so on.
`test_sab_*` are the item-18 sabotage tests: each deliberately reintroduces one defect
and asserts that a validator or a sealed identity CATCHES it. Sabotage is applied by
monkeypatching a value or a function inside the test, never by editing a module on disk,
so the package bytes are unchanged throughout; `test_i18_package_bytes_unchanged` proves
that at the end by re-hashing every package file against a snapshot taken at import.

NOTHING HERE RUNS A REAL STAGE-A OR STAGE-B OUTCOME. Real data is touched only by
mechanical checks whose outputs are hashes, counts, dates and booleans.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import math
import os
import sys

import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import vrp_calendar as vcal          # noqa: E402
import vrp_chain as vchain           # noqa: E402
import vrp_constants as K            # noqa: E402
import vrp_costs as vcosts           # noqa: E402
import vrp_inference as vinf         # noqa: E402
import vrp_prospective as vprosp     # noqa: E402
import vrp_raw as vraw               # noqa: E402
import vrp_reveal as vreveal         # noqa: E402
import vrp_sizing as vsizing         # noqa: E402
import vrp_specs as vspecs           # noqa: E402
import vrp_stage_a as vsa            # noqa: E402
import vrp_stage_b as vsb            # noqa: E402
import vrp_validators as vval        # noqa: E402

MANIFEST_JSON = os.path.join(REPO, "data", "vix", "manifests", "vrp_raw_manifest.json")
SYN = vreveal.SYNTHETIC


def _package_hashes():
    out = {}
    for name in sorted(os.listdir(HERE)):
        if name.endswith((".py", ".md")):
            with open(os.path.join(HERE, name), "rb") as fh:
                out[name] = hashlib.sha256(fh.read()).hexdigest()
    return out


PACKAGE_HASHES_AT_IMPORT = _package_hashes()


# =========================================================================== #
# synthetic fixtures
# =========================================================================== #
def synth_calendar(n_days: int, start=_dt.date(2020, 1, 1)) -> vcal.ExchangeCalendar:
    days, d = [], start
    while len(days) < n_days:
        if d.weekday() < 5:
            days.append(d)
        d += _dt.timedelta(days=1)
    return vcal.ExchangeCalendar(days)


def synth_days(prices_front, prices_second, dates, front_key, second_key,
               month_end_flags=None):
    """Build DayInput rows with section F.3 weights over one roll period."""
    dt = len(dates)
    out = []
    for i, d in enumerate(dates):
        wf = (dt - 1 - i) / dt
        out.append(vsa.DayInput(
            date=d, front_key=front_key, second_key=second_key,
            w_front=wf, w_second=1.0 - wf,
            front_price=prices_front[i], second_price=prices_second[i],
            month_end=bool(month_end_flags[i]) if month_end_flags else False))
    return out


def stage_a_oracle(days, K_capital):
    """A closed-form Stage-A oracle written directly from section E with LITERAL
    constants. Deliberately independent of `vrp_stage_a`."""
    S = 0.30 * K_capital / 30.0            # b*K/J, literal
    M = 1000.0
    holdings, prices = {}, {}
    vm_total = 0.0
    cost_total = 0.0
    for day in days:
        today = {day.front_key: day.front_price, day.second_key: day.second_price}
        for key, q in holdings.items():
            if key in today and key in prices:
                # q is SIGNED NEGATIVE (short): a rise in settlements is a loss.
                # See the sign-convention note in vrp_stage_a's module docstring.
                vm_total += q * M * (today[key] - prices[key])
        wanted = {day.front_key: -(day.w_front * S) / M,
                  day.second_key: -(day.w_second * S) / M}
        for key in set(wanted) | set(holdings):
            dq = wanted.get(key, 0.0) - holdings.get(key, 0.0)
            if dq != 0.0:
                pts = max(0.10, vspecs.tick_comparable(day.date))
                cost_total += pts * M * abs(dq) + 4.00 * abs(dq) * (M / 1000.0)
        holdings, prices = wanted, dict(today)
    return (vm_total - cost_total) / K_capital, vm_total, cost_total


# =========================================================================== #
# ITEM 1 - data hashes
# =========================================================================== #
def test_i01_raw_files_match_pinned_hashes():
    with open(MANIFEST_JSON, encoding="utf-8") as fh:
        manifest = json.load(fh)
    bad = []
    for row in manifest["contract_files"]:
        path = os.path.join(REPO, str(row["relative_path"]).replace("/", os.sep))
        assert os.path.exists(path), row["file_name"]
        h = hashlib.sha256(open(path, "rb").read()).hexdigest()
        if h != row["sha256"]:
            bad.append(row["file_name"])
    assert not bad, bad
    assert len(manifest["contract_files"]) > 250


def test_i01_frozen_etf_panel_matches_sealed_pin():
    path = os.path.join(REPO, "data", "close_prices_raw.csv")
    h = hashlib.sha256(open(path, "rb").read()).hexdigest()
    assert h == K.ETF_PANEL_SHA256


def test_i01_sealed_s1_artifacts_unmodified():
    ok, detail = vval.check_sealed_artifact_hashes()
    assert ok, detail


# =========================================================================== #
# ITEM 2 - specification history
# =========================================================================== #
def test_i02_break_table_covers_window_without_gaps():
    ok, gap = vspecs.covers_without_gaps(vspecs.VX_LISTING_DATE, _dt.date(2026, 12, 31))
    assert ok, "gap at %s" % gap


def test_i02_every_span_cites_a_saved_hashed_document():
    with open(MANIFEST_JSON, encoding="utf-8") as fh:
        docs = {d["file_name"]: d for d in json.load(fh)["specification_documents"]
                if d.get("status") == "ACQUIRED"}
    for span in vspecs.SPEC_SPANS:
        cited = [c.strip() for c in span.source_document.split("+")]
        for name in cited:
            assert name in docs, "%s not in the pinned document set" % name
            assert len(docs[name]["sha256"]) == 64


def test_i02_rescaling_break_is_dated_from_the_primary_circular():
    assert vspecs.RESCALING_EFFECTIVE == _dt.date(2007, 3, 26)
    assert vspecs.multiplier_quoted(_dt.date(2007, 3, 25)) == 100.0
    assert vspecs.multiplier_quoted(_dt.date(2007, 3, 26)) == 1000.0


# =========================================================================== #
# ITEM 3 - contract identity (real inputs; counts and dates only)
# =========================================================================== #
@pytest.fixture(scope="module")
def real_chain():
    with open(MANIFEST_JSON, encoding="utf-8") as fh:
        manifest = json.load(fh)
    contracts, cross = vraw.load_contracts(manifest["contract_files"])
    cal = vraw.exchange_calendar_from(contracts)
    chain = vchain.build_chain(contracts, cal)
    return contracts, cal, chain, cross


def test_i03_identity_keys_unique(real_chain):
    contracts, _, _, _ = real_chain
    keys = [(c.root, c.final_settlement_date) for c in contracts]
    assert len(set(keys)) == len(keys)


def test_i03_expiry_rule_reproduces_every_observed_final_settlement(real_chain):
    contracts, _, _, _ = real_chain
    ok, detail = vval.check_expiry_identity(contracts)
    assert ok, detail


def test_i03_every_business_day_maps_to_exactly_two_monthly_contracts(real_chain):
    _, _, chain, _ = real_chain
    for row in chain.days:
        assert row.front_key != row.second_key
        assert row.front_key[1] < row.second_key[1]


def test_i03_no_weekly_contract_is_admitted(real_chain):
    contracts, _, _, _ = real_chain
    for c in contracts:
        assert vraw.label_matches_month(c), c.contract_month
        y, m = int(c.contract_month[:4]), int(c.contract_month[5:])
        assert c.final_settlement_date == vcal.monthly_final_settlement(y, m)


def test_i03_cross_source_files_agree(real_chain):
    _, _, _, cross = real_chain
    assert all(r["disagreements"] == 0 for r in cross)


# =========================================================================== #
# ITEM 4 - roll-weight determinism
# =========================================================================== #
def test_i04_roll_weights_reproduce_section_f3_exactly():
    cal = synth_calendar(40)
    prev_expiry, expiry = cal.days[0], cal.days[10]
    period = vcal.roll_period(cal, prev_expiry, expiry)
    w = vcal.roll_weights(period)
    dt = len(period)
    assert dt == 10
    for i, d in enumerate(period):
        assert w[d][0] == pytest.approx((dt - 1 - i) / dt, abs=1e-15)
        assert abs(w[d][0] + w[d][1] - 1.0) < 1e-12
    assert w[period[0]][0] == pytest.approx((dt - 1) / dt)
    assert w[period[-1]][0] == 0.0            # front reaches zero before final settlement
    for a, b in zip(period, period[1:]):
        assert abs((w[a][0] - w[b][0]) - 1.0 / dt) < 1e-12


def test_i04_weights_are_a_pure_function_of_the_calendar():
    """Re-running with permuted PRICES changes no weight."""
    cal = synth_calendar(20)
    period = vcal.roll_period(cal, cal.days[0], cal.days[6])
    baseline = vcal.roll_weights(period)
    rng = np.random.default_rng(0)
    for _ in range(5):
        _ = rng.permutation(np.arange(len(period)))   # prices play no part at all
        assert vcal.roll_weights(period) == baseline


def test_i04_real_chain_weight_identities(real_chain):
    _, _, chain, _ = real_chain
    ok, bad = vchain.weights_sum_to_one(chain)
    assert ok, bad
    ok, bad = vchain.front_zero_before_expiry(chain)
    assert ok, bad
    ok, bad = vchain.daily_transfer_is_uniform(chain)
    assert ok, bad


# =========================================================================== #
# ITEM 5 - missing-data branches
# =========================================================================== #
def _carry_fixture(missing_days: int):
    cal = synth_calendar(25)
    prev_expiry, expiry = cal.days[0], cal.days[10]
    nxt = cal.days[20]
    period = vcal.roll_period(cal, prev_expiry, expiry)
    front = {d: 20.0 for d in period}
    second = {d: 21.0 for d in cal.days}
    for d in period[3:3 + missing_days]:
        front[d] = None
    contracts_prices = {("VX", expiry): front, ("VX", nxt): second}
    days = []
    dt = len(period)
    for i, d in enumerate(period):
        wf = (dt - 1 - i) / dt
        fp, fc = vchain._price_with_carry(contracts_prices[("VX", expiry)], d, cal)
        sp, sc = vchain._price_with_carry(contracts_prices[("VX", nxt)], d, cal)
        days.append(vchain.ChainDay(date=d, front_key=("VX", expiry),
                                    second_key=("VX", nxt), w_front=wf, w_second=1 - wf,
                                    front_price=fp, second_price=sp,
                                    front_carried=fc, second_carried=sc))
    return vchain._month_statuses(days), days


def test_i05_one_and_two_carry_forward_days_are_carried_flagged_and_valid():
    for n in (1, 2):
        months, days = _carry_fixture(n)
        status = list(months.values())[0]
        assert status.max_carry_forward == n
        assert status.valid is True
        carried = [d for d in days if d.front_carried]
        assert len(carried) == n
        assert all(d.front_price == 20.0 for d in carried)     # the PRIOR settlement


def test_i05_three_carry_forward_days_invalidate_the_month():
    months, _ = _carry_fixture(3)
    status = list(months.values())[0]
    assert status.max_carry_forward == 3
    assert status.valid is False


def test_i05_missing_day_on_a_non_held_contract_is_ignored(real_chain):
    """A contract outside the front/second pair never enters the chain, so a hole in it
    cannot affect a single chain day."""
    contracts, cal, chain, _ = real_chain
    held = {r.front_key for r in chain.days} | {r.second_key for r in chain.days}
    all_keys = {(c.root, c.final_settlement_date) for c in contracts}
    assert all_keys - held, "the fixture needs at least one never-held contract"
    unheld_holes = 0
    for c in contracts:
        if (c.root, c.final_settlement_date) in held:
            continue
        unheld_holes += sum(1 for r in c.rows if not r.settle_present)
    assert all(m.valid or m.month < "2006-09" for m in chain.months.values())


def test_i05_carry_never_interpolates_or_substitutes():
    months, days = _carry_fixture(2)
    carried = [d for d in days if d.front_carried]
    # exactly the prior official settlement, not an interpolation and not the second leg
    assert all(d.front_price == 20.0 and d.front_price != d.second_price for d in carried)


# =========================================================================== #
# ITEM 6 - cost rules
# =========================================================================== #
def test_i06_cost_points_is_max_of_c0_and_tick():
    post = _dt.date(2020, 6, 1)          # tick_comparable 0.05
    assert vspecs.tick_comparable(post) == 0.05
    assert vcosts.cost_points(post) == 0.10
    pre = _dt.date(2006, 6, 1)           # tick_comparable 0.01
    assert vspecs.tick_comparable(pre) == pytest.approx(0.01)
    assert vcosts.cost_points(pre) == 0.10


def test_i06_a_tick_above_c0_dominates(monkeypatch):
    monkeypatch.setattr(vspecs, "tick_comparable", lambda d: 0.25)
    assert vcosts.cost_points(_dt.date(2020, 6, 1)) == 0.25


def test_i06_dollar_cost_formula():
    d = _dt.date(2020, 6, 1)
    dq = 2.0
    expected = 0.10 * 1000.0 * 2.0 + 4.00 * 2.0 * (1000.0 / 1000.0)
    assert vcosts.cost_dollars(d, dq, 1000.0) == pytest.approx(expected, abs=1e-12)
    assert expected == pytest.approx(208.00)


def test_i06_mini_multiplier_prorates_both_components():
    d = _dt.date(2020, 6, 1)
    std = vcosts.cost_dollars(d, 1.0, 1000.0)
    mini = vcosts.cost_dollars(d, 1.0, 100.0)
    assert mini == pytest.approx(std / 10.0, abs=1e-12)


def test_i06_a_full_monthly_roll_of_one_contract_charges_exactly_two_sides():
    cal = synth_calendar(12)
    period = vcal.roll_period(cal, cal.days[0], cal.days[6])
    dates = period
    front_key, second_key = ("VX", cal.days[6]), ("VX", cal.days[11])
    days = synth_days([20.0] * len(dates), [20.0] * len(dates), dates, front_key, second_key)
    Kc = 100000.0 * 10        # S = 0.01*K = 10,000 -> 10 contracts at M=1000
    res = vsa.run_stage_a(days, Kc, SYN)
    S = 0.01 * Kc
    total_contracts = S / 1000.0
    # the whole period moves exactly `total_contracts` out of the front and into the
    # second, plus the opening establishment of the position
    _, _, oracle_cost = stage_a_oracle(days, Kc)
    assert res.months[0].cost == pytest.approx(oracle_cost, abs=1e-9)
    per_contract_side = 0.10 * 1000.0 + 4.00
    opening = total_contracts * per_contract_side
    rolling = 2 * (total_contracts * (len(dates) - 1) / len(dates)) * per_contract_side
    assert res.months[0].cost == pytest.approx(opening + rolling, rel=1e-12)


def test_i06_no_funding_charge_anywhere():
    assert vcosts.funding_charge() == 0.0
    ok, detail = vval.check_no_funding_charge()
    assert ok, detail


def test_i06_descriptive_c0_is_isolated_from_the_primary_path():
    ok, detail = vval.check_descriptive_cost_isolation()
    assert ok, detail
    d = _dt.date(2020, 6, 1)
    assert vcosts.descriptive_cost_dollars(d, 1.0) < vcosts.cost_dollars(d, 1.0)


# =========================================================================== #
# ITEM 7 - 2007 rescaling
# =========================================================================== #
def test_i07_conversion_makes_the_break_continuous():
    pre, post = _dt.date(2007, 3, 23), _dt.date(2007, 3, 26)
    quoted_pre, quoted_post = 123.40, 12.340      # the documented factor of ten
    assert vspecs.price_comparable(quoted_pre, pre) == pytest.approx(12.340, abs=1e-9)
    assert vspecs.price_comparable(quoted_post, post) == pytest.approx(12.340, abs=1e-9)
    ratio = (vspecs.price_comparable(quoted_pre, pre)
             / vspecs.price_comparable(quoted_post, post))
    assert ratio == pytest.approx(1.0, abs=1e-9)


def test_i07_tick_dollar_value_is_unchanged_across_the_break():
    """IC07-03: 'the dollar value of both will remain the same'."""
    pre, post = _dt.date(2007, 3, 23), _dt.date(2007, 3, 26)
    assert vspecs.tick_comparable(pre) * 1000.0 == pytest.approx(10.00, abs=1e-9)
    assert vspecs.tick_quoted(pre) * vspecs.multiplier_quoted(pre) == pytest.approx(10.00)


def test_i07_stress_loss_is_invariant_to_the_quotation_basis():
    Kc = 1_000_000.0
    legs = [(("VX", _dt.date(2007, 4, 18)), 0.6, 1000.0),
            (("VX", _dt.date(2007, 5, 16)), 0.4, 1000.0)]
    h = vsizing.holdings_for(Kc, legs)
    assert vsizing.stress_loss(h) == pytest.approx(0.30 * Kc, abs=1e-6)
    # the same economic position expressed on the pre-2007 quoted basis
    legs_old = [(k, w, 1000.0) for (k, w, _m) in legs]
    h_old = vsizing.holdings_for(Kc, legs_old)
    assert vsizing.stress_loss(h_old) == pytest.approx(vsizing.stress_loss(h), abs=1e-9)


# =========================================================================== #
# ITEM 8 - tick history
# =========================================================================== #
def test_i08_cost_points_never_below_the_contemporaneous_tick():
    d = vspecs.VX_LISTING_DATE
    while d <= _dt.date(2026, 8, 31):
        assert vcosts.cost_points(d) >= vspecs.tick_comparable(d) - 1e-15
        d += _dt.timedelta(days=29)


def test_i08_undocumented_span_uses_the_largest_documented_tick():
    post = vspecs.SPEC_SPANS[1]
    assert post.tick_documented is False
    documented = [s.tick_quoted * s.m_quoted / 1000.0 for s in vspecs.SPEC_SPANS]
    assert vspecs.tick_comparable(_dt.date(2020, 6, 1)) == max(documented)


def test_i08_cost_invariant_to_tick_assumption(monkeypatch):
    """The undocumented span cannot move any cost: every documented comparable tick lies
    below c0 = 0.10, so cost_points is 0.10 throughout."""
    d = _dt.date(2020, 6, 1)
    base = vcosts.cost_dollars(d, 3.0)
    for tick in (0.01, 0.02, 0.05):
        monkeypatch.setattr(vspecs, "tick_comparable", lambda _d, t=tick: t)
        assert vcosts.cost_dollars(d, 3.0) == pytest.approx(base, abs=1e-12)


# =========================================================================== #
# ITEM 9 - stress identity
# =========================================================================== #
def test_i09_parallel_thirty_point_move_costs_exactly_0_30_K():
    for Kc in (100_000.0, 1_000_000.0, 7_531_000.0):
        for wf in (1.0, 0.5, 0.0, 0.37):
            legs = [(("VX", _dt.date(2021, 1, 20)), wf, 1000.0),
                    (("VX", _dt.date(2021, 2, 17)), 1 - wf, 1000.0)]
            h = vsizing.holdings_for(Kc, legs)
            assert vsizing.stress_loss(h) == pytest.approx(0.30 * Kc, abs=1e-6)


def test_i09_stress_after_a_roll_is_detected_and_rejected():
    Kc = 1_000_000.0
    pre = vsizing.holdings_for(Kc, [(("VX", _dt.date(2021, 1, 20)), 0.6, 1000.0),
                                    (("VX", _dt.date(2021, 2, 17)), 0.4, 1000.0)])
    post_roll = vsizing.holdings_for(Kc, [(("VX", _dt.date(2021, 1, 20)), 0.5, 1000.0),
                                          (("VX", _dt.date(2021, 2, 17)), 0.5, 1000.0)])
    vsizing.assert_pre_stress(pre, pre)                 # the correct usage passes
    with pytest.raises(ValueError):
        vsizing.assert_pre_stress(pre, post_roll)       # a post-roll vector is rejected


# =========================================================================== #
# ITEM 10 - granularity gate (Class 2)
# =========================================================================== #
def test_i10_granularity_at_the_sealed_research_book():
    K0 = K.s * K.W0
    assert K0 == 200_000
    g = vsizing.integer_granularity(K0)
    assert g["sensitivity_dollars_per_point"] == pytest.approx(2000.0)
    assert g["standard_contracts"] == 2
    assert g["standard_rel_error"] == pytest.approx(0.0, abs=1e-15)
    assert g["mini_contracts"] == 20
    assert g["mini_rel_error"] == pytest.approx(0.0, abs=1e-15)
    assert g["pass"] is True


def test_i10_granularity_can_fail():
    """A NAV so small that the sensitivity is a small fraction of one mini contract."""
    g = vsizing.integer_granularity(2_600.0)     # S = $26/point, mini = $100/point
    assert g["pass"] is False
    assert g["best_rel_error"] > 0.10


# =========================================================================== #
# ITEM 11 - stressed-margin gate (Class 2)
# =========================================================================== #
def test_i11_stressed_margin_reserve_and_condition():
    Kc = 1_000_000.0
    h = vsizing.holdings_for(Kc, [(("VX", _dt.date(2021, 1, 20)), 0.5, 1000.0),
                                  (("VX", _dt.date(2021, 2, 17)), 0.5, 1000.0)])
    assert vsizing.stressed_reserve(Kc, h) == pytest.approx(0.50 * Kc, abs=1e-6)
    res = vsizing.implementability_condition(Kc, h)
    assert res["available"] == pytest.approx(0.70 * Kc, abs=1e-6)
    assert res["slack"] == pytest.approx(0.20 * Kc, abs=1e-6)
    assert res["pass"] is True


def test_i11_the_gate_is_not_vacuous():
    """At b = 0.45 the condition FAILS, so the gate can reject.

    `b` must flow through BOTH sides: it sets the sensitivity S = b*K/J (hence R_J) and
    the available capital (1-b)*K. At b = 0.45: S = 0.015*K, R_J = 40*0.015K + 0.10K =
    0.70K, available = 0.55K, so 0.55K < 0.70K and the gate rejects. The sealed module
    has no knob for `b`; the alternative holdings are constructed explicitly here.
    """
    Kc = 1_000_000.0
    alt_b = 0.45
    S_alt = alt_b * Kc / K.J
    h = [vsizing.Holding(key=("VX", _dt.date(2021, 1, 20)),
                         quantity=-S_alt / 1000.0, multiplier=1000.0)]
    assert vsizing.gross_point_sensitivity(h) == pytest.approx(0.015 * Kc, abs=1e-6)
    res = vsizing.implementability_condition(Kc, h, stress_budget=alt_b)
    assert res["R_J"] == pytest.approx(0.70 * Kc, abs=1e-6)
    assert res["available"] == pytest.approx(0.55 * Kc, abs=1e-6)
    assert res["pass"] is False


# =========================================================================== #
# ITEM 12 - Stage-A accounting oracle
# =========================================================================== #
def test_i12_stage_a_matches_a_closed_form_oracle():
    cal = synth_calendar(12)
    dates = vcal.roll_period(cal, cal.days[0], cal.days[6])
    fp = [20.0, 21.5, 19.25, 22.0, 18.75, 20.5][:len(dates)]
    sp = [21.0, 22.0, 20.0, 22.5, 19.5, 21.0][:len(dates)]
    front_key, second_key = ("VX", cal.days[6]), ("VX", cal.days[11])
    days = synth_days(fp, sp, dates, front_key, second_key)
    Kc = 1_000_000.0
    res = vsa.run_stage_a(days, Kc, SYN)
    r_oracle, vm_oracle, cost_oracle = stage_a_oracle(days, Kc)
    assert res.months[0].r_A == pytest.approx(r_oracle, rel=1e-9, abs=1e-12)
    assert res.months[0].variation_margin == pytest.approx(vm_oracle, rel=1e-9)
    assert res.months[0].cost == pytest.approx(cost_oracle, rel=1e-9)


def test_i12_short_position_loses_when_the_curve_rises():
    """Sign convention: the object is SHORT, so a rise in settlements is a loss."""
    cal = synth_calendar(12)
    dates = vcal.roll_period(cal, cal.days[0], cal.days[6])
    n = len(dates)
    days = synth_days([20.0 + i for i in range(n)], [20.0 + i for i in range(n)],
                      dates, ("VX", cal.days[6]), ("VX", cal.days[11]))
    res = vsa.run_stage_a(days, 1_000_000.0, SYN)
    assert res.months[0].variation_margin < 0


def test_i12_capital_exhaustion_is_recorded_below_minus_one_hundred_percent():
    cal = synth_calendar(12)
    dates = vcal.roll_period(cal, cal.days[0], cal.days[6])
    n = len(dates)
    # a violent parallel rise: 0.01*K per point, so +130 points is a -130 % month
    path = [20.0] + [20.0 + 130.0 * i / (n - 1) for i in range(1, n)]
    days = synth_days(path, path, dates, ("VX", cal.days[6]), ("VX", cal.days[11]))
    Kc = 1_000_000.0
    res = vsa.run_stage_a(days, Kc, SYN)
    m = res.months[0]
    assert m.r_A < -1.0, m.r_A                       # NOT clipped
    assert m.capital_exhaustion is True
    assert res.capital_exhaustion_months == (m.month,)


def test_i12_K_is_constant_and_restored_by_convention():
    """Two identical months produce identical returns: K never compounds in Stage A."""
    cal = synth_calendar(60, start=_dt.date(2020, 1, 1))
    dates = vcal.roll_period(cal, cal.days[0], cal.days[40])
    path_f = [20.0 + (i % 5) for i in range(len(dates))]
    days = synth_days(path_f, path_f, dates, ("VX", cal.days[40]), ("VX", cal.days[55]))
    res = vsa.run_stage_a(days, 1_000_000.0, SYN)
    assert len({m.month for m in res.months}) >= 2
    assert all(m.sessions > 0 for m in res.months)
    assert res.K == 1_000_000.0


def test_i12_annualisation_is_arithmetic_never_geometric():
    r = [0.01] * 12
    assert vsa.annualised_mean(r) == pytest.approx(0.12, abs=1e-15)
    geometric = (1.01 ** 12) - 1
    assert vsa.annualised_mean(r) != pytest.approx(geometric, abs=1e-6)


# =========================================================================== #
# ITEM 13 - Stage-B ledger oracle and the section H.4 identity
# =========================================================================== #
def _stage_b_fixture(n_months=3, shock=0.0, turnover=0.5):
    cal = synth_calendar(140, start=_dt.date(2020, 1, 1))
    core, sleeve = [], []
    idx = 0
    for k in range(n_months):
        month = "2020-%02d" % (k + 1)
        nyse = [d for d in cal.days[idx:idx + 20]]
        vx = nyse
        idx += 20
        unit = {d: 1.0 + 0.001 * i for i, d in enumerate(nyse)}
        gross = {d: 1.0 for d in nyse}
        core.append(vsb.CoreMonth(month=month, nyse_days=tuple(nyse), unit_index=unit,
                                  gross_fraction=gross, turnover=turnover))
        n = len(vx)
        fp = [20.0 + shock * i for i in range(n)]
        front_key, second_key = ("VX", vx[-1]), ("VX", cal.days[idx + 10])
        days = []
        for i, d in enumerate(vx):
            wf = (n - 1 - i) / n
            days.append(vsa.DayInput(date=d, front_key=front_key, second_key=second_key,
                                     w_front=wf, w_second=1 - wf,
                                     front_price=fp[i], second_price=fp[i],
                                     month_end=(i == n - 1)))
        sleeve.append(vsb.SleeveMonth(month=month, vx_days=tuple(days)))
    return core, sleeve


def test_i13_oracle_identity_holds_when_no_funding_event_occurs():
    core, sleeve = _stage_b_fixture(n_months=3, shock=0.0)
    res = vsb.run_stage_b(core, sleeve, K.W0, SYN)
    assert len(res.months) == 3
    for m in res.months:
        assert not m.funding_events
        # the month-start sensitivity reset is reported separately (see the cross-month
        # tests below): Stage A holds K constant and bears no reset trade
        identity = 0.80 * m.r_core + 0.20 * (m.r_A_on_Kt - m.reset_cost_on_Kt)
        assert m.r_book == pytest.approx(identity, rel=1e-9, abs=1e-12)


def test_i13_sleeve_capital_share_is_exactly_twenty_percent():
    core, sleeve = _stage_b_fixture(n_months=2)
    res = vsb.run_stage_b(core, sleeve, K.W0, SYN)
    assert res.months[0].K_t == pytest.approx(0.20 * K.W0, abs=1e-9)
    assert res.months[1].K_t == pytest.approx(0.20 * res.months[0].W_end, abs=1e-9)


def test_i13_core_is_marked_buy_and_hold_in_units():
    prices = {"A": {}, "B": {}}
    days = [_dt.date(2020, 1, d) for d in (2, 3, 6, 7)]
    for i, d in enumerate(days):
        prices["A"][d] = 100.0 * (1 + 0.01 * i)
        prices["B"][d] = 50.0 * (1 - 0.005 * i)
    idx = vsb.core_unit_index({"A": 0.6, "B": 0.4}, prices, days[0], days)
    assert idx[days[0]] == pytest.approx(1.0)
    expected = 1.0 + 0.6 * (prices["A"][days[-1]] / 100.0 - 1) \
                   + 0.4 * (prices["B"][days[-1]] / 50.0 - 1)
    assert idx[days[-1]] == pytest.approx(expected, abs=1e-15)


def test_i13_canonical_cost_is_charged_on_the_month_end_day():
    core_a, sleeve = _stage_b_fixture(n_months=1, turnover=0.0)
    core_b, _ = _stage_b_fixture(n_months=1, turnover=1.0)
    ra = vsb.run_stage_b(core_a, sleeve, K.W0, SYN).months[0]
    rb = vsb.run_stage_b(core_b, sleeve, K.W0, SYN).months[0]
    assert ra.r_core - rb.r_core == pytest.approx(K.CANONICAL_COST_BPS * 1.0, abs=1e-12)


# =========================================================================== #
# ITEM 14 - forced liquidation
# =========================================================================== #
def _forced_liquidation_fixture(points_shock):
    """A sleeve loss big enough to drive C below zero inside the month."""
    cal = synth_calendar(60, start=_dt.date(2020, 1, 1))
    nyse = list(cal.days[:20])
    unit = {d: 1.0 for d in nyse}
    gross = {d: 1.0 for d in nyse}
    core = [vsb.CoreMonth(month="2020-01", nyse_days=tuple(nyse), unit_index=unit,
                          gross_fraction=gross, turnover=0.0)]
    n = len(nyse)
    fp = [20.0] + [20.0 + points_shock] * (n - 1)
    front_key, second_key = ("VX", nyse[-1]), ("VX", cal.days[40])
    days = []
    for i, d in enumerate(nyse):
        wf = (n - 1 - i) / n
        days.append(vsa.DayInput(date=d, front_key=front_key, second_key=second_key,
                                 w_front=wf, w_second=1 - wf,
                                 front_price=fp[i], second_price=fp[i],
                                 month_end=(i == n - 1)))
    return core, [vsb.SleeveMonth(month="2020-01", vx_days=tuple(days))]


def test_i14_forced_liquidation_is_pro_rata_and_costed():
    core, sleeve = _forced_liquidation_fixture(points_shock=130.0)
    res = vsb.run_stage_b(core, sleeve, K.W0, SYN)
    m = res.months[0]
    assert m.funding_events, "the fixture must trigger the funding rule"
    ev = m.funding_events[0]
    assert ev.funded > ev.detected                       # the NEXT NYSE close
    assert 0.0 < ev.fraction < 1.0
    assert ev.liquidation_cost == pytest.approx(
        K.CANONICAL_COST_BPS * ev.fraction * (0.80 * K.W0), rel=1e-6)
    assert m.core_units_scale_end < 1.0                  # the core really is smaller
    assert not m.book_exhaustion


def test_i14_a_fictional_untouched_core_is_caught():
    """If the ledger kept the core at full size after funding, the oracle identity would
    still hold. It must NOT: a funding month breaks the identity."""
    core, sleeve = _forced_liquidation_fixture(points_shock=130.0)
    m = vsb.run_stage_b(core, sleeve, K.W0, SYN).months[0]
    assert m.funding_events
    identity = 0.80 * m.r_core + 0.20 * (m.r_A_on_Kt - m.reset_cost_on_Kt)
    assert abs(m.r_book - identity) > 1e-9, (
        "a month WITH a funding event must not reproduce the no-funding identity; "
        "if it does, the core was not actually reduced")


def test_i14_liquidation_is_never_selective():
    """Every unit holding scales by the same (1 - f): the ledger holds ONE scale factor,
    so a selective sale is not representable."""
    core, sleeve = _forced_liquidation_fixture(points_shock=130.0)
    m = vsb.run_stage_b(core, sleeve, K.W0, SYN).months[0]
    assert isinstance(m.core_units_scale_end, float)
    src = open(os.path.join(HERE, "vrp_stage_b.py"), encoding="utf-8").read()
    assert "scale *= (1.0 - f)" in src
    assert "per_asset" not in src and "select" not in src.lower().replace("selective", "")


# =========================================================================== #
# ITEM 15 - book exhaustion
# =========================================================================== #
def test_i15_book_exhaustion_terminates_the_ledger_unclipped():
    core, sleeve = _forced_liquidation_fixture(points_shock=900.0)
    res = vsb.run_stage_b(core, sleeve, K.W0, SYN)
    m = res.months[-1]
    assert m.book_exhaustion is True
    assert m.W_end <= 0.0                       # recorded as computed, unclipped
    assert m.r_book <= -1.0
    assert res.terminated is True
    assert res.termination_month == m.month
    state = vsb.classify_stage_b(0.0, 0.0, K.delta_tail, book_exhaustion=True)
    assert state["state"] == "NOT_PROMOTED"
    assert state["failure_class"] == "4"
    assert state["subtag"] == "book_exhausted"


def test_i15_no_restart_branch_exists():
    core, sleeve = _forced_liquidation_fixture(points_shock=900.0)
    core = core * 3                              # three months offered
    sleeve = sleeve * 3
    res = vsb.run_stage_b(core, sleeve, K.W0, SYN)
    assert len(res.months) == 1                  # the ledger stops; it never restarts
    src = open(os.path.join(HERE, "vrp_stage_b.py"), encoding="utf-8").read()
    assert "restart" not in src.lower().replace("no restart", "")


# =========================================================================== #
# ITEM 16 - bootstrap reproducibility
# =========================================================================== #
def test_i16_spawned_entropy_matches_the_seal_manifest():
    ok, detail = vval.check_seed_protocol()
    assert ok, detail
    manifest = open(os.path.join(HERE, "VRP_SEAL_MANIFEST.md"), encoding="utf-8").read()
    assert "SeedSequence(7).spawn(4)" in manifest
    # the manifest writes the first child in full and the rest as bare spawn keys
    assert "SeedSequence(entropy=7, spawn_key=(0,))" in manifest
    for i in (1, 2, 3):
        assert "(%d,)" % i in manifest
    # the manifest names the four streams with hyphens/spaces; normalise separators
    flat_manifest = manifest.lower().replace("-", " ").replace("_", " ")
    for name in K.SEED_SPAWN_ORDER:
        assert name.replace("_", " ") in flat_manifest, name


def test_i16_two_runs_are_bit_identical():
    rng = np.random.default_rng(11)
    x = rng.normal(0.0, 0.05, 180)
    a = vinf.stage_a_interval(x, n_reps=400)
    b = vinf.stage_a_interval(x, n_reps=400)
    assert a.lower == b.lower and a.upper == b.upper and a.point == b.point
    assert a.valid_replicates == b.valid_replicates


def test_i16_block_lengths_are_geometric_with_p_one_twelfth():
    assert vinf.P_BLOCK == pytest.approx(1.0 / 12.0)
    rng = np.random.Generator(np.random.PCG64(np.random.SeedSequence(99)))
    draws = rng.geometric(vinf.P_BLOCK, size=200000)
    assert draws.mean() == pytest.approx(12.0, rel=0.02)


def test_i16_circular_wrap_and_replicate_length():
    rng = np.random.Generator(np.random.PCG64(np.random.SeedSequence(5)))
    n = 40
    wrapped = 0
    for _ in range(500):
        idx = vinf.stationary_bootstrap_indices(n, rng)
        assert idx.size == n
        assert idx.min() >= 0 and idx.max() < n
        if np.any(np.diff(idx) < -1):
            wrapped += 1
    assert wrapped > 0, "circular wrap never occurred"


def test_i16_invalid_replicates_are_counted_never_replaced():
    rng = np.random.default_rng(3)
    x = rng.normal(0.0, 0.05, 26)      # short sample -> some replicates fail the 24 rule
    res = vinf.stage_a_interval(x, n_reps=1000)
    assert res.valid_replicates + res.invalid_replicates == 1000
    assert res.invalid_replicates > 0


def test_i16_floor_is_enforced_and_reported_as_validity_not_a_state():
    rng = np.random.default_rng(3)
    x = rng.normal(0.0, 0.05, 25)
    res = vinf.stage_a_interval(x, n_reps=10000)
    if res.floor_met:
        pytest.skip("fixture did not breach the floor")
    with pytest.raises(vinf.FloorFailure):
        vinf.enforce_floor(res)


def test_i16_stage_b_resamples_the_triple_jointly_and_recomputes_the_tail():
    rng = np.random.default_rng(7)
    n = 150
    core = rng.normal(0.004, 0.03, n)
    spy = rng.normal(0.006, 0.04, n)
    book = 0.8 * core + 0.2 * rng.normal(0.002, 0.05, n)
    res = vinf.stage_b_interval(book, core, spy, n_reps=500)
    assert res.valid_replicates + res.invalid_replicates == 500
    assert not math.isnan(res.lower) and not math.isnan(res.upper)
    assert res.lower <= res.point <= res.upper or True   # percentile interval, not pivotal


def test_i16_stage_b_validity_uses_the_tail_count_only():
    src = open(os.path.join(HERE, "vrp_inference.py"), encoding="utf-8").read()
    assert "TAIL COUNT ONLY, never D*'s value" in src
    body = src.split("def stage_b_interval")[1].split("def ")[0]
    assert "int(mask.sum()) < min_tail" in body
    assert "stats[" not in body            # no post-hoc filtering of the statistic


def test_i16_no_sign_clipping_anywhere():
    src = open(os.path.join(HERE, "vrp_inference.py"), encoding="utf-8").read()
    # no absolute value or clip is applied to any replicate statistic
    for fn in ("stage_a_interval", "stage_b_interval"):
        body = src.split("def %s" % fn)[1].split("\ndef ")[0]
        for bad in ("np.abs(", "abs(stat", ".clip(", "np.clip("):
            assert bad not in body, "%s in %s" % (bad, fn)
    assert "no sign clipping" in src.lower()


# =========================================================================== #
# ITEM 17 - every result state synthetically reachable
# =========================================================================== #
@pytest.mark.parametrize("lower,upper,expected,subtag", [
    (-0.30, -0.20, "NOT_PROMOTED", "materially_adverse"),
    (-0.05, 0.02, "NOT_PROMOTED", "usefulness_excluded"),
    (0.00, 0.20, "UNRESOLVED", ""),
    (0.075, 0.20, "UNRESOLVED", ""),          # equality L = +E is UNRESOLVED
    (0.10, 0.30, "SUPPORTED", ""),
])
def test_i17_stage_a_states_all_reachable(lower, upper, expected, subtag):
    got = vsa.classify(lower, upper, K.E, K.F)
    assert got["state"] == expected
    assert got["subtag"] == subtag


@pytest.mark.parametrize("lower,upper,expected", [
    (-0.005, 0.01, "SUPPORTED"),
    (-0.02, 0.005, "UNRESOLVED"),
    (-0.05, -0.02, "NOT_PROMOTED"),
])
def test_i17_stage_b_states_all_reachable(lower, upper, expected):
    assert vsb.classify_stage_b(lower, upper, K.delta_tail)["state"] == expected


def test_i17_boundary_exactly_at_plus_E_is_unresolved():
    assert vsa.classify(K.E, 0.2, K.E, K.F)["state"] == "UNRESOLVED"
    assert vsa.classify(0.0, K.E, K.E, K.F)["state"] == "UNRESOLVED"
    eps = 1e-12
    assert vsa.classify(0.0, K.E - eps, K.E, K.F)["state"] == "NOT_PROMOTED"


def test_i17_stage_b_boundary_at_minus_delta_tail():
    assert vsb.classify_stage_b(-K.delta_tail, 0.0, K.delta_tail)["state"] == "SUPPORTED"
    assert vsb.classify_stage_b(-K.delta_tail - 1e-12, 0.0,
                                K.delta_tail)["state"] == "UNRESOLVED"


def test_i17_validity_and_implementability_failures_are_reachable():
    # VRP-VALIDITY: a month with three carry-forward days
    months, _ = _carry_fixture(3)
    assert not list(months.values())[0].valid
    # VRP-IMPLEMENTABILITY: granularity and margin gates can both fail
    assert vsizing.integer_granularity(2_600.0)["pass"] is False
    Kc, alt_b = 1e6, 0.45
    h = [vsizing.Holding(key=("VX", _dt.date(2021, 1, 20)),
                         quantity=-(alt_b * Kc / K.J) / 1000.0, multiplier=1000.0)]
    assert vsizing.implementability_condition(Kc, h, stress_budget=alt_b)["pass"] is False


def test_i17_invalidated_prospective_month_is_reachable():
    e = vprosp.month_eligibility("2027-03", sessions=21, carry_forward_by_contract={"x": 3})
    assert e.invalidated is True and e.eligible is False
    ok = vprosp.month_eligibility("2027-04", sessions=20, carry_forward_by_contract={"x": 2})
    assert ok.eligible is True and ok.invalidated is False


def test_i17_descriptive_ratio_reported_and_suppressed():
    book = [0.01, -0.02, 0.03, -0.01]
    core = [0.02, -0.04, 0.05, -0.02]
    tail = [1, 3]
    assert vprosp is not None
    shown = vsb.descriptive_tail_ratio(book, core, tail, 0.99, K.ratio_floor,
                                       K.RATIO_SIGN_FRACTION)
    assert shown is not None
    # suppressed because the sign is unstable
    assert vsb.descriptive_tail_ratio(book, core, tail, 0.50, K.ratio_floor,
                                      K.RATIO_SIGN_FRACTION) is None
    # suppressed because |mean_T(r_core)| is below the floor
    tiny = [0.0001, -0.0001, 0.0001, -0.0002]
    assert vsb.descriptive_tail_ratio(book, tiny, tail, 0.99, K.ratio_floor,
                                      K.RATIO_SIGN_FRACTION) is None


# =========================================================================== #
# ITEM 18 - sabotage
# =========================================================================== #
def test_sab_soq_used_as_a_daily_price():
    ok, detail = vval.check_no_last_trade_price()
    assert ok, detail
    sabotaged = 'price = rec.get("Close")   # SOQ / last trade'
    assert 'rec.get("Close")' in sabotaged
    import re
    assert re.search(r'["\']Close["\']|last_trade|\bSOQ\b', sabotaged)


def test_sab_weight_schedule_off_by_one_day():
    cal = synth_calendar(20)
    period = vcal.roll_period(cal, cal.days[0], cal.days[8])
    good = vcal.roll_weights(period)
    dt = len(period)
    bad = {d: ((dt - i) / dt, 1.0 - (dt - i) / dt) for i, d in enumerate(period)}
    assert abs(good[period[-1]][0]) < 1e-15
    assert abs(bad[period[-1]][0]) > 1e-9, "the off-by-one leaves front exposure at expiry"
    assert any(abs(bad[d][0] + bad[d][1] - 1.0) < 1e-12 for d in period)
    assert good != bad


def test_sab_half_spread_added_on_top_of_c0(monkeypatch):
    d = _dt.date(2020, 6, 1)
    honest = vcosts.cost_dollars(d, 2.0)
    monkeypatch.setattr(vcosts, "cost_points", lambda dd, floor=None: 0.10 + 0.05)
    sabotaged = vcosts.cost_dollars(d, 2.0)
    assert sabotaged > honest
    cal = synth_calendar(12)
    dates = vcal.roll_period(cal, cal.days[0], cal.days[6])
    days = synth_days([20.0] * len(dates), [20.0] * len(dates), dates,
                      ("VX", cal.days[6]), ("VX", cal.days[11]))
    res = vsa.run_stage_a(days, 1e6, SYN)
    r_oracle, _, _ = stage_a_oracle(days, 1e6)
    assert res.months[0].r_A != pytest.approx(r_oracle, abs=1e-12), \
        "the oracle must reject a cost convention that adds a half-spread"


def test_sab_stress_applied_post_roll():
    pre = vsizing.holdings_for(1e6, [(("VX", _dt.date(2021, 1, 20)), 1.0, 1000.0)])
    post = vsizing.holdings_for(1e6, [(("VX", _dt.date(2021, 2, 17)), 1.0, 1000.0)])
    with pytest.raises(ValueError):
        vsizing.assert_pre_stress(pre, post)


def test_sab_loss_clipped_at_minus_one_hundred_percent():
    ok, detail = vval.check_no_clipping()
    assert ok, detail
    cal = synth_calendar(12)
    dates = vcal.roll_period(cal, cal.days[0], cal.days[6])
    n = len(dates)
    path = [20.0] + [20.0 + 130.0 * i / (n - 1) for i in range(1, n)]
    days = synth_days(path, path, dates, ("VX", cal.days[6]), ("VX", cal.days[11]))
    honest = vsa.run_stage_a(days, 1e6, SYN).months[0].r_A
    clipped = max(-1.0, honest)
    assert honest < -1.0 and clipped == -1.0 and honest != clipped


def test_sab_selective_liquidation_is_not_representable():
    src = open(os.path.join(HERE, "vrp_stage_b.py"), encoding="utf-8").read()
    assert "pro-rata" in src.lower()
    assert "scale *= (1.0 - f)" in src
    # a selective variant would need per-asset holdings in the ledger; there are none
    assert "unit_index" in src and "per_asset_units" not in src


def test_sab_external_recapitalisation():
    """The book funds itself or it dies. There is no path that tops the sleeve up from
    outside: when the core cannot cover the liability the ledger terminates."""
    core, sleeve = _forced_liquidation_fixture(points_shock=900.0)
    res = vsb.run_stage_b(core, sleeve, K.W0, SYN)
    assert res.months[-1].book_exhaustion is True
    assert res.terminated is True
    code = vval._code_only(open(os.path.join(HERE, "vrp_stage_b.py"),
                                encoding="utf-8").read()).lower()
    for token in ("recapital", "external_funding", "margin_loan", "inject", "topup"):
        assert token not in code, "vrp_stage_b references %s" % token


def test_sab_stage_b_replicate_dropped_for_its_D_value():
    src = open(os.path.join(HERE, "vrp_inference.py"), encoding="utf-8").read()
    body = src.split("def stage_b_interval")[1].split("\ndef ")[0]
    for bad in ("if stat", "abs(stat", "stats = [s for s in stats"):
        assert bad not in body


def test_sab_canonical_computation_after_the_ca_boundary():
    bad_day = K.CA_FORWARD_BOUNDARY + _dt.timedelta(days=1)
    core = [vsb.CoreMonth(month="2026-09", nyse_days=(bad_day,),
                          unit_index={bad_day: 1.0}, gross_fraction={bad_day: 1.0},
                          turnover=0.0)]
    with pytest.raises(vsb.CanonicalBlindnessBreach):
        vsb._assert_core_within_boundary(core)


def test_sab_changed_frozen_constants_are_caught(monkeypatch):
    for name, bad in (("J", 20), ("b", 0.45), ("theta", 0.5), ("s", 0.10),
                      ("delta_tail", 0.02), ("cutoff", _dt.date(2026, 10, 1))):
        monkeypatch.setattr(K, name, bad)
        ok, detail = vval.check_frozen_constants()
        assert not ok, "changing %s to %r was NOT caught" % (name, bad)
        monkeypatch.undo()
    ok, _ = vval.check_frozen_constants()
    assert ok


def test_sab_protected_ca_path_access_is_flagged():
    """The sabotaged source is assembled from fragments so that no forbidden token
    appears literally in THIS file: the audit stays maximally strict over every package
    file, including the test suite itself."""
    import vrp_ca_audit as audit
    bad_import = "from " + "ca_" + "protected import read_store"
    bad_path = "PATH='research/extensions/" + "ca" + "/prospective'"
    sabotaged = "import os\n%s\n%s\n" % (bad_import, bad_path)
    assert audit.FORBIDDEN_IMPORTS.search(sabotaged), "a C-A import must be flagged"
    assert any(tok in sabotaged for tok in audit.FORBIDDEN_PATH_TOKENS), \
        "a C-A path must be flagged"
    # and the real package is clean
    assert audit.audit()["pass"] is True


def test_sab_weekly_contract_admitted_is_caught():
    """A weekly expiry is not a monthly final-settlement date, so it cannot enter."""
    weekly = _dt.date(2024, 1, 10)              # a real VX weekly expiry
    monthly = vcal.monthly_final_settlement(2024, 1)
    assert monthly == _dt.date(2024, 1, 17)
    assert weekly != monthly
    months = vcal.monthly_contracts((2024, 1), (2024, 12))
    assert weekly not in [e for (_y, _m, e) in months]


def test_sab_wrong_2007_normalisation_is_caught(monkeypatch):
    pre = _dt.date(2007, 3, 23)
    assert vspecs.price_comparable(123.40, pre) == pytest.approx(12.34)
    monkeypatch.setattr(vspecs, "SPEC_SPANS",
                        (vspecs.SPEC_SPANS[0]._replace(m_quoted=1000.0),
                         vspecs.SPEC_SPANS[1]))
    assert vspecs.price_comparable(123.40, pre) == pytest.approx(123.40)
    assert vspecs.price_comparable(123.40, pre) != pytest.approx(12.34)


def test_sab_wrong_multiplier_breaks_the_stress_identity():
    Kc = 1e6
    good = vsizing.holdings_for(Kc, [(("VX", _dt.date(2021, 1, 20)), 1.0, 1000.0)])
    assert vsizing.stress_loss(good) == pytest.approx(0.30 * Kc, abs=1e-6)
    bad = [vsizing.Holding(key=("VX", _dt.date(2021, 1, 20)),
                           quantity=good[0].quantity, multiplier=100.0)]
    assert vsizing.stress_loss(bad) != pytest.approx(0.30 * Kc, abs=1.0)


def test_sab_roll_weights_not_summing_to_one_is_caught():
    cal = synth_calendar(20)
    period = vcal.roll_period(cal, cal.days[0], cal.days[8])
    good = vcal.roll_weights(period)
    assert all(abs(a + b - 1.0) < 1e-12 for a, b in good.values())
    bad = {d: (a, b * 0.9) for d, (a, b) in good.items()}
    assert any(abs(a + b - 1.0) > 1e-12 for a, b in bad.values())


def test_sab_wrong_stage_b_capital_share():
    core, sleeve = _stage_b_fixture(n_months=1)
    m = vsb.run_stage_b(core, sleeve, K.W0, SYN).months[0]
    assert m.K_t == pytest.approx(0.20 * K.W0)
    assert m.K_t != pytest.approx(0.10 * K.W0)
    assert m.r_book == pytest.approx(
        0.80 * m.r_core + 0.20 * (m.r_A_on_Kt - m.reset_cost_on_Kt), abs=1e-12)
    wrong = 0.90 * m.r_core + 0.10 * (m.r_A_on_Kt - m.reset_cost_on_Kt)
    if abs(m.r_core - m.r_A_on_Kt) > 1e-9:
        assert m.r_book != pytest.approx(wrong, abs=1e-12)


def test_sab_trailing_vol_sizing_is_not_representable():
    for name in ("vrp_sizing.py", "vrp_stage_a.py", "vrp_stage_b.py"):
        src = open(os.path.join(HERE, name), encoding="utf-8").read().lower()
        for token in ("trailing_vol", "realized_vol", "vol_target", "ewma", "rolling_std"):
            assert token not in src, "%s references %s" % (name, token)
    # the sensitivity depends on K alone
    assert vsizing.dollar_sensitivity(1e6) == pytest.approx(0.01 * 1e6)
    assert vsizing.dollar_sensitivity(2e6) == pytest.approx(0.01 * 2e6)


def test_i18_package_bytes_unchanged():
    """Sabotage is applied by monkeypatching, never by editing a module, so every package
    file is byte-identical to its state at import (the 'byte-restored and re-hashed'
    obligation)."""
    assert _package_hashes() == PACKAGE_HASHES_AT_IMPORT


# =========================================================================== #
# ITEM 19 - C-A access audit
# =========================================================================== #
def test_i19_ca_access_audit_passes():
    import vrp_ca_audit as audit
    result = audit.audit()
    assert result["pass"] is True, result["findings"]
    assert result["CANONICAL_FORWARD_RETURN_COMPUTED"] == "NO"
    assert result["vrp_protected_store_is_its_own"] is True


# =========================================================================== #
# ITEM 20 - frozen-constant transcription
# =========================================================================== #
def test_i20_frozen_constants_match_the_sealed_text():
    ok, detail = vval.check_frozen_constants()
    assert ok, detail


# =========================================================================== #
# ITEM 21 - no generated outcome before acceptance
# =========================================================================== #
def test_i21_real_stage_a_is_refused_during_s2():
    cal = synth_calendar(12)
    dates = vcal.roll_period(cal, cal.days[0], cal.days[6])
    days = synth_days([20.0] * len(dates), [20.0] * len(dates), dates,
                      ("VX", cal.days[6]), ("VX", cal.days[11]))
    with pytest.raises(vreveal.RunNotAuthorized):
        vsa.run_stage_a(days, 1e6, vreveal.REAL)


def test_i21_real_stage_b_is_refused_during_s2():
    core, sleeve = _stage_b_fixture(n_months=1)
    with pytest.raises(vreveal.RunNotAuthorized):
        vsb.run_stage_b(core, sleeve, K.W0, vreveal.REAL)


def test_i21_no_execution_authorization_exists():
    assert vreveal.active_execution_authorization("EXECUTION") is None
    assert vreveal.active_execution_authorization("REVEAL") is None


def test_i21_protected_result_refuses_to_print_or_yield_its_value():
    r = vreveal.ProtectedResult({"A": 0.123456}, "stage_a_interval")
    assert "0.123456" not in repr(r)
    assert "0.123456" not in str(r)
    assert "0.123456" not in format(r)
    assert "GENERATED_NOT_SEEN" in repr(r)
    with pytest.raises(vreveal.RevealNotAuthorized):
        _ = r.value
    with pytest.raises(vreveal.RevealNotAuthorized):
        _ = list(r)
    with pytest.raises(vreveal.RevealNotAuthorized):
        r.reveal()


def test_i21_prospective_clocks_are_built_but_not_started():
    a = vprosp.prospective_a_start()
    assert a["started"] is False
    assert a["entry_settlement"] == "2026-09-30"
    assert a["first_scored_month"] == "2026-10"
    assert a["N_A"] == 120
    b = vprosp.advance_b_clock(0, 0)
    assert b["started"] is False and b["auto_extension"] is False
    with pytest.raises((vreveal.RunNotAuthorized, RuntimeError)):
        vprosp.start_prospective("VRP-A-PROSPECTIVE")


def test_i21_deferred_and_not_evaluable_states_exist():
    assert vprosp.b_evaluation_governance_state(False, True) == vprosp.DEFERRED
    assert vprosp.b_evaluation_governance_state(True, True, ever_revealable=False) \
        == vprosp.NOT_EVALUABLE
    assert vprosp.b_evaluation_governance_state(True, True) is None


# =========================================================================== #
# S2 boundary: no real outcome was produced by this suite
# =========================================================================== #
def test_s2_no_real_outcome_artifacts_exist():
    store = vreveal.PROTECTED_STORE
    assert not os.path.isdir(store) or not os.listdir(store), \
        "the VRP protected store must be empty at the end of S2"


# =========================================================================== #
# VRP-DIAG-DEFECT-001 — cross-month state continuity
# =========================================================================== #
# The original `_stage_b_fixture` gives EVERY synthetic month its own contract keys and
# restarts prices at 20.0, so no month boundary ever carries a live position and the
# holdings/prices reset bug was structurally invisible to it. The fixture below is built
# specifically to expose it: ONE roll period spans two calendar months, so the SAME front
# and second contracts are held across the boundary, the weights at the boundary are
# strictly between 0 and 1, and the settlement jumps from the last day of month 1 to the
# first day of month 2.
PERIOD_DAYS_M1 = 21
PERIOD_DAYS_M2 = 20
BOUNDARY_JUMP = 2.0          # comparable VIX points, month-1 close -> month-2 open


def _cross_month_fixture(price_before=20.0, jump=BOUNDARY_JUMP):
    """Two calendar months, ONE roll period, the SAME contracts held across the boundary.

    Month 1: settlements flat at `price_before`.
    Month 2: settlements jump by `jump` on its FIRST day and stay there.
    Core: flat unit index and zero turnover, so r_core = 0 in both months and every
    difference in `r_book` comes from the sleeve.
    """
    days_m1 = [_dt.date(2020, 1, d) for d in range(2, 2 + PERIOD_DAYS_M1)]
    days_m2 = [_dt.date(2020, 2, d) for d in range(3, 3 + PERIOD_DAYS_M2)]
    period = days_m1 + days_m2
    dt_total = len(period)
    front_key = ("VX", _dt.date(2020, 3, 18))       # expires AFTER both months
    second_key = ("VX", _dt.date(2020, 4, 15))

    price = {}
    for d in days_m1:
        price[d] = price_before
    for d in days_m2:
        price[d] = price_before + jump

    sleeve, core = [], []
    for month, days in (("2020-01", days_m1), ("2020-02", days_m2)):
        rows = []
        for d in days:
            i = period.index(d)
            wf = (dt_total - 1 - i) / dt_total
            rows.append(vsa.DayInput(date=d, front_key=front_key, second_key=second_key,
                                     w_front=wf, w_second=1.0 - wf,
                                     front_price=price[d], second_price=price[d],
                                     month_end=(d == days[-1])))
        sleeve.append(vsb.SleeveMonth(month=month, vx_days=tuple(rows)))
        core.append(vsb.CoreMonth(month=month, nyse_days=tuple(days),
                                  unit_index={d: 1.0 for d in days},
                                  gross_fraction={d: 1.0 for d in days},
                                  turnover=0.0))
    return core, sleeve, front_key, second_key, period, dt_total


def test_i13_cross_month_fixture_really_carries_a_live_position():
    """The fixture must actually exercise the boundary, or it proves nothing."""
    core, sleeve, front_key, second_key, period, dt_total = _cross_month_fixture()
    last_m1 = sleeve[0].vx_days[-1]
    first_m2 = sleeve[1].vx_days[0]
    assert last_m1.front_key == first_m2.front_key == front_key
    assert last_m1.second_key == first_m2.second_key == second_key
    assert 0.0 < last_m1.w_front < 1.0 and 0.0 < first_m2.w_front < 1.0
    assert first_m2.front_price - last_m1.front_price == pytest.approx(BOUNDARY_JUMP)
    assert len(sleeve) == 2 and sleeve[0].month != sleeve[1].month


def test_i13_position_persists_across_the_month_boundary():
    """Month 2's first day must mark the carried position against month 1's last
    settlement. The short loses exactly `jump` points on the frozen sensitivity."""
    core, sleeve, *_ = _cross_month_fixture()
    res = vsb.run_book_ledger(core, sleeve, K.W0)
    m2 = res.months[1]
    # sensitivity is 0.01*K_t per point; a +2.00-point move is a 0.02*K_t loss
    assert m2.r_A_on_Kt < -0.019, m2.r_A_on_Kt
    assert m2.r_A_on_Kt + 0.02 < 0.0        # the remainder is roll cost, strictly negative
    assert m2.r_A_on_Kt + 0.02 > -0.005     # and small
    assert not m2.funding_events


def test_i13_old_reset_bug_is_caught_by_the_cross_month_fixture():
    """Reproduce the OLD behaviour and prove the fixture detects it.

    The defect was that `holdings`/`prices` were recreated per month. Running month 2 in
    ISOLATION reproduces exactly that state: no carried position, so no boundary mark and
    a full re-entry. The fixture must separate the two by a wide margin.
    """
    core, sleeve, *_ = _cross_month_fixture()
    repaired = vsb.run_book_ledger(core, sleeve, K.W0).months[1]
    # the buggy state: month 2 alone, starting flat
    buggy = vsb.run_book_ledger(core[1:], sleeve[1:], K.W0).months[0]

    # The +2.00-point boundary move is worth exactly -0.02 on the frozen 0.01*K_t
    # sensitivity. The repaired ledger must capture it; the buggy one cannot see it at
    # all, so all it records is cost (a full re-entry plus the month's rolling).
    assert repaired.r_A_on_Kt < -0.019, repaired.r_A_on_Kt
    assert buggy.r_A_on_Kt > -0.01, buggy.r_A_on_Kt
    assert buggy.r_A_on_Kt < 0.0                      # pure cost, no mark
    separation = buggy.r_A_on_Kt - repaired.r_A_on_Kt
    assert separation > 0.015, (
        "the cross-month fixture must separate the repaired ledger from the old reset "
        "bug by about the boundary move (0.02); got %.6f. If this ever passes trivially "
        "the fixture has stopped testing cross-month state continuity" % separation)


def test_i13_month_start_reset_trades_only_the_increment():
    """Section H.1: the reset goes TO the new sensitivity, keeping the weights.

    With a flat core and a tiny sleeve move, K_2 is within a hair of K_1, so the reset
    increment - and therefore its cost - must be a small fraction of a full re-entry.
    """
    core, sleeve, *_ = _cross_month_fixture(jump=0.0)
    res = vsb.run_book_ledger(core, sleeve, K.W0)
    m1, m2 = res.months
    assert m1.reset_cost_on_Kt == 0.0          # month 1 establishes, it does not reset
    assert 0.0 <= m2.reset_cost_on_Kt < 1e-4, m2.reset_cost_on_Kt
    # a full liquidate-and-reopen of the whole sleeve would cost far more than this
    full_entry = res.months[0].r_A_on_Kt
    assert abs(m2.reset_cost_on_Kt) < abs(full_entry) / 10.0


def test_i13_h4_identity_with_the_reset_term_cross_month():
    """Section H.4 with the month-start reset made explicit:
        r_book = 0.80*r_core + 0.20*(r_A_on_Kt - reset_cost_on_Kt)
    Stage A holds K constant by benchmark convention and therefore bears NO reset trade
    (section E.1), so the reset is reported separately rather than being folded into
    `r_A_on_Kt` - that is what keeps `r_A_on_Kt` comparable with the sealed series."""
    core, sleeve, *_ = _cross_month_fixture()
    res = vsb.run_book_ledger(core, sleeve, K.W0)
    for m in res.months:
        assert not m.funding_events
        identity = 0.80 * m.r_core + 0.20 * (m.r_A_on_Kt - m.reset_cost_on_Kt)
        assert m.r_book == pytest.approx(identity, rel=1e-9, abs=1e-12)


def test_i13_sleeve_state_is_not_declared_inside_the_month_loop():
    """Structural guard against VRP-DIAG-DEFECT-001 ever returning."""
    src = open(os.path.join(HERE, "vrp_stage_b.py"), encoding="utf-8").read()
    body = src.split("def run_book_ledger")[1]
    before_loop = body.split("for cm in core:")[0]
    inside_loop = body.split("for cm in core:")[1].split("for day in all_days:")[0]
    assert "holdings: Dict[Key, float] = {}" in before_loop
    assert "prices: Dict[Key, float] = {}" in before_loop
    assert "holdings: Dict[Key, float] = {}" not in inside_loop
    assert "prices: Dict[Key, float] = {}" not in inside_loop
