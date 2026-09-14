# -*- coding: utf-8 -*-
"""CTA-EDGE-01-TA — the S2 build-validation suite.

Everything here runs on SYNTHETIC fixtures or on identities that touch no return.
NOTHING here computes a real historical CTA-EDGE-01-TA outcome: the real ETF panel is
never opened for returns, and `test_firewall_*` and `test_guard_*` prove it rather
than promise it.

Test-name prefixes map to the S2 task's required behavioural tests: `test_b01_*` is
behavioural test 1, and so on.

The independent oracle (`ta_oracle.py`) imports nothing from the production engine and
reaches every expected value by a different route — summing the fixture's declared
daily log returns rather than differencing endpoint prices. That is deliberate: this
programme has twice been bitten by an oracle that reproduced the engine's own
misreading.
"""
from __future__ import annotations

import datetime as _dt
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

import ta_authorization as auth          # noqa: E402
import ta_calendar as tcal               # noqa: E402
import ta_classify as tcls               # noqa: E402
import ta_contract as K                  # noqa: E402
import ta_covariates as tcov             # noqa: E402
import ta_diagnostics as tdiag           # noqa: E402
import ta_engine as teng                 # noqa: E402
import ta_inference as tinf              # noqa: E402
import ta_oracle as ORC                  # noqa: E402
import ta_prices as tpx                  # noqa: E402
import ta_report as trep                 # noqa: E402

CONTRACT_PATH = os.path.join(K.TA_DIR, "TA_PREREGISTRATION.md")


# --------------------------------------------------------------------------- #
# Fixture construction                                                         #
# --------------------------------------------------------------------------- #


def weekday_grid(start: _dt.date, n: int, holidays=()) -> list:
    """A synthetic trading grid: weekdays, minus any declared holidays."""
    out, d = [], start
    hol = set(holidays)
    while len(out) < n:
        if d.weekday() < 5 and d not in hol:
            out.append(d)
        d += _dt.timedelta(days=1)
    return out


def fixture(grid, t0s, daily_logs_by_ticker, cell=K.PRIMARY_CELL,
            instrument=K.PRIMARY_INSTRUMENT):
    """Turn declared per-day log returns into (events, source, daily_logs)."""
    series = {t: ORC.oracle_prices_from_daily_logs(grid, dl)
              for t, dl in daily_logs_by_ticker.items()}
    src = tpx.SyntheticPriceSource(series, grid=grid)
    events = tcal.windows_from_grid(t0s, grid, cell, instrument)
    return events, src


def flat_logs(grid, value=0.0):
    return {d: value for d in grid}


def cycle_logs(grid, t0s, pre_bps, post_bps, bar_bps=0.0):
    """Put `pre_bps` on each PRE return-bearing day and `post_bps` on each POST day."""
    logs = {d: 0.0 for d in grid}
    for t0 in t0s:
        i = grid.index(t0)
        for d in grid[i - 5:i]:
            logs[d] = pre_bps / 5.0 / 1e4
        for d in grid[i + 1:i + 6]:
            logs[d] = post_bps / 5.0 / 1e4
        logs[grid[i]] = bar_bps / 1e4
    return logs


# --------------------------------------------------------------------------- #
# 0. The sealed contract agrees with the executable constants                  #
# --------------------------------------------------------------------------- #


def _contract_text():
    with open(CONTRACT_PATH, "r", encoding="utf-8") as fh:
        return fh.read()


def test_c00_constants_match_the_sealed_contract():
    t = _contract_text()
    assert "COST_BPS                       = 4 x 2 = 8.0 bps" in t
    assert K.COST_BPS == 8.0
    assert "mean AC_NET  >=  +8.0 bps per event" in t and K.M1_NET_BPS == 8.0
    assert "mean AC_GROSS >= +16.0 bps" in t and K.M1_GROSS_BPS == 16.0
    assert "calendarised annualised Sharpe  >=  +0.30" in t and K.M2_SHARPE == 0.30
    assert "= 2006-02 .. 2026-05  =  244 months" in t and K.MONTH_GRID_N == 244
    assert "VALID COMPLETE WINDOWS                       = 213" in t
    assert K.PRIMARY_VALID_WINDOWS == 213
    assert "numpy.random.SeedSequence(7).spawn(5)[4]" in t
    assert (K.SEED_ENTROPY, K.SEED_SPAWN_N, K.SEED_CHILD_INDEX) == (7, 5, 4)
    assert "B = 10,000" in t and K.BOOTSTRAP_B == 10_000
    assert "fewer than 20 events have all four signed covariates = 0" in t
    assert K.MACRO_MIN_REFERENCE_GROUP == 20


def test_c01_oracle_constants_agree():
    """A silent drift between the oracle and the contract must break a test."""
    assert ORC.ORACLE_COST_BPS == K.COST_BPS
    assert ORC.ORACLE_M1_NET == K.M1_NET_BPS
    assert ORC.ORACLE_M2 == K.M2_SHARPE
    assert ORC.ORACLE_PRE_OPEN == K.PRE_OFFSET_OPEN
    assert ORC.ORACLE_PRE_CLOSE == K.PRE_OFFSET_CLOSE
    assert ORC.ORACLE_POST_OPEN == K.POST_OFFSET_OPEN
    assert ORC.ORACLE_POST_CLOSE == K.POST_OFFSET_CLOSE
    assert ORC.ORACLE_MONTHS_PER_YEAR == K.SHARPE_PERIODS_PER_YEAR


def test_c02_oracle_does_not_import_the_engine():
    with open(os.path.join(HERE, "ta_oracle.py"), "r", encoding="utf-8") as fh:
        src = fh.read()
    for banned in ("ta_engine", "ta_inference", "ta_classify", "ta_contract",
                   "ta_diagnostics"):
        assert not re.search(rf"^\s*(import|from)\s+{banned}\b", src, re.M), banned


# --------------------------------------------------------------------------- #
# Behavioural test 1 / 2 — the auction cycle, both signs                       #
# --------------------------------------------------------------------------- #


def test_b01_positive_auction_cycle():
    grid = weekday_grid(_dt.date(2020, 1, 1), 60)
    t0 = grid[20]
    logs = cycle_logs(grid, [t0], pre_bps=-30.0, post_bps=+40.0)
    events, src = fixture(grid, [t0], {"TLT": logs})
    got = teng.ac_gross_bps(src, "TLT", events[0])
    want = ORC.oracle_ac_gross_bps(logs, grid, t0)
    assert got > 0
    assert math.isclose(got, want, abs_tol=1e-9)
    assert math.isclose(want, 70.0, abs_tol=1e-9)


def test_b02_negative_auction_cycle():
    grid = weekday_grid(_dt.date(2020, 1, 1), 60)
    t0 = grid[20]
    logs = cycle_logs(grid, [t0], pre_bps=+35.0, post_bps=-25.0)
    events, src = fixture(grid, [t0], {"TLT": logs})
    got = teng.ac_gross_bps(src, "TLT", events[0])
    want = ORC.oracle_ac_gross_bps(logs, grid, t0)
    assert got < 0
    assert math.isclose(got, want, abs_tol=1e-9)
    assert math.isclose(want, -60.0, abs_tol=1e-9)


# --------------------------------------------------------------------------- #
# Behavioural test 3 — auction-day isolation, with a DISCRIMINATING fixture    #
# --------------------------------------------------------------------------- #


def _flip_implementation_ac_bps(src, ticker, event, grid):
    """The DEFECT this fixture exists to catch: a short->long flip at close(t0-1).

    An engine that flips instead of going flat measures the POST leg from
    close(t0-1), so the excluded auction-day bar leaks into the P&L.
    """
    i = event.t0_index
    r_pre = math.log(src.close(ticker, grid[i - 1])) - math.log(src.close(ticker, grid[i - 6]))
    r_post = math.log(src.close(ticker, grid[i + 5])) - math.log(src.close(ticker, grid[i - 1]))
    return 1e4 * (r_post - r_pre)


def test_b03_auction_day_bar_is_excluded_and_position_is_flat():
    grid = weekday_grid(_dt.date(2020, 1, 1), 60)
    t0 = grid[20]
    # every return-bearing day is zero; the ONLY move is a huge auction-day bar
    logs = cycle_logs(grid, [t0], pre_bps=0.0, post_bps=0.0, bar_bps=+500.0)
    events, src = fixture(grid, [t0], {"TLT": logs})
    ev = events[0]

    assert teng.exposure_on_auction_day_bar(ev) == teng.FLAT
    assert [l.to_position for l in teng.position_path(ev)] == [
        teng.SHORT, teng.FLAT, teng.LONG, teng.FLAT]

    sealed = teng.ac_gross_bps(src, "TLT", ev)
    assert math.isclose(sealed, ORC.oracle_ac_gross_bps(logs, grid, t0), abs_tol=1e-9)
    assert math.isclose(sealed, 0.0, abs_tol=1e-9), "the excluded bar leaked into AC"

    # the fixture is proved DISCRIMINATING: the old defect gives a wildly different
    # answer on exactly this data, so a passing engine cannot be passing by luck
    flip = _flip_implementation_ac_bps(src, "TLT", ev, grid)
    assert math.isclose(flip, 500.0, abs_tol=1e-6)
    assert abs(flip - sealed) > 100.0

    # the bar's own return is still reported, as a DESCRIPTIVE quantity
    bar = teng.auction_day_bar_bps(src, "TLT", ev, grid)
    assert math.isclose(bar, ORC.oracle_auction_day_bar_bps(logs, grid, t0), abs_tol=1e-9)
    assert math.isclose(bar, 500.0, abs_tol=1e-6)


def test_b03b_direction_of_each_leg():
    """The PRE leg is SHORT: it must LOSE when the instrument rises over the pre window."""
    grid = weekday_grid(_dt.date(2020, 1, 1), 60)
    t0 = grid[20]
    up_pre = cycle_logs(grid, [t0], pre_bps=+50.0, post_bps=0.0)
    events, src = fixture(grid, [t0], {"TLT": up_pre})
    assert teng.ac_gross_bps(src, "TLT", events[0]) < 0        # short leg lost
    up_post = cycle_logs(grid, [t0], pre_bps=0.0, post_bps=+50.0)
    events2, src2 = fixture(grid, [t0], {"TLT": up_post})
    assert teng.ac_gross_bps(src2, "TLT", events2[0]) > 0      # long leg gained


# --------------------------------------------------------------------------- #
# Behavioural test 4 — cost accounting                                         #
# --------------------------------------------------------------------------- #


def test_b04_cost_accounting_is_exactly_eight_bps():
    grid = weekday_grid(_dt.date(2020, 1, 1), 60)
    t0 = grid[20]
    logs = cycle_logs(grid, [t0], pre_bps=-10.0, post_bps=+10.0)   # gross = +20 bps
    events, src = fixture(grid, [t0], {"TLT": logs})
    ev = events[0]
    gross = teng.ac_gross_bps(src, "TLT", ev)
    net = teng.ac_net_bps(src, "TLT", ev)
    assert math.isclose(gross, 20.0, abs_tol=1e-9)
    assert math.isclose(net, 12.0, abs_tol=1e-9), "net must be +12, not +16 and not +8"
    assert math.isclose(net, ORC.oracle_ac_net_bps(logs, grid, t0), abs_tol=1e-9)
    assert teng.one_way_units(ev) == 4
    assert math.isclose(teng.event_cost_bps(ev), 8.0, abs_tol=1e-12)


# --------------------------------------------------------------------------- #
# Behavioural test 5 — zero months survive into the Sharpe series              #
# --------------------------------------------------------------------------- #


def test_b05_zero_months_are_retained():
    grid = weekday_grid(_dt.date(2020, 1, 1), 250)
    t0s = [grid[20], grid[120]]            # two events, many months apart
    logs = cycle_logs(grid, t0s, pre_bps=-10.0, post_bps=+30.0)
    events, src = fixture(grid, t0s, {"TLT": logs})
    results = teng.event_results(src, "TLT", events)
    months = tcal.month_grid(results[0].calendar_month, results[-1].calendar_month)
    series = teng.monthly_series(results, months)
    assert len(series) == len(months) > len(results)
    zeros = [v for v in series if v == 0.0]
    assert len(zeros) == len(months) - len(results) > 0
    ac_by_t0 = {r.t0: r.ac_net_bps for r in results}
    assert series == pytest.approx(ORC.oracle_monthly_series(ac_by_t0, months))


def test_b05b_sealed_grid_has_thirty_one_zero_months():
    """The sealed §F.1 count, checked against the sealed calendar itself."""
    events = tcal.load_sealed_events(K.PRIMARY_CELL)
    months = tcal.month_grid()
    event_months = {e.calendar_month for e in events}
    assert len(months) == 244
    assert len(event_months) == 213
    assert len(months) - len(event_months) == 31


# --------------------------------------------------------------------------- #
# Behavioural test 6 — the Sharpe is calendarised, never event-frequency based #
# --------------------------------------------------------------------------- #


def test_b06_sharpe_ignores_event_frequency_metadata():
    monthly = [5.0, 0.0, -3.0, 12.0, 0.0, 0.0, 7.0, -1.0, 0.0, 4.0, 2.0, 0.0]
    base = teng.calendarised_sharpe(monthly)
    assert math.isclose(base, ORC.oracle_sharpe(monthly), rel_tol=1e-12)

    # Identical monthly P&L reached from two DIFFERENT event frequencies.
    dense = [teng.EventResult(_dt.date(2020, m, 15), 2020, f"2020-{m:02d}",
                              0.0, 0.0, monthly[m - 1] + K.COST_BPS, monthly[m - 1],
                              0.0, "No") for m in range(1, 13)]
    sparse_months = [m for m in range(1, 13) if monthly[m - 1] != 0.0]
    sparse = [teng.EventResult(_dt.date(2020, m, 15), 2020, f"2020-{m:02d}",
                               0.0, 0.0, monthly[m - 1] + K.COST_BPS, monthly[m - 1],
                               0.0, "No") for m in sparse_months]
    grid = tcal.month_grid("2020-01", "2020-12")
    assert len(dense) == 12 and len(sparse) == 7
    assert teng.calendarised_sharpe(teng.monthly_series(dense, grid)) == pytest.approx(
        teng.calendarised_sharpe(teng.monthly_series(sparse, grid)))
    assert teng.calendarised_sharpe(teng.monthly_series(dense, grid)) == pytest.approx(base)
    assert "sqrt(12)" in _contract_text()


# --------------------------------------------------------------------------- #
# Behavioural test 7 — one year carries the result -> LOYO damage              #
# --------------------------------------------------------------------------- #


def _loyo_fixture(dominant_year_value=400.0, other_value=-5.0):
    years = list(range(2006, 2011))
    results, monthly_by_year = [], {}
    for y in years:
        vals = []
        for m in range(1, 13):
            v = dominant_year_value if y == 2008 else other_value
            vals.append(v)
            results.append(teng.EventResult(_dt.date(y, m, 15), y, f"{y}-{m:02d}",
                                            0.0, 0.0, v + K.COST_BPS, v, 0.0, "No"))
        monthly_by_year[y] = vals
    return years, results, monthly_by_year


def test_b07_year_dominance_triggers_loyo_damage():
    years, results, monthly = _loyo_fixture()
    loyo = tinf.leave_one_year_out(results, monthly, years)
    assert not loyo.passes
    assert loyo.min_year == 2008
    assert loyo.min_mean_net <= 0.0
    # the same shape with a broad-based effect must PASS
    years2, results2, monthly2 = _loyo_fixture(dominant_year_value=40.0,
                                               other_value=30.0)
    assert tinf.leave_one_year_out(results2, monthly2, years2).passes
    # independent check of one LOYO estimate
    kept = [r.ac_net_bps for r in results if r.year != 2008]
    assert loyo.per_year_mean_net[2008] == pytest.approx(ORC.oracle_mean(kept))


# --------------------------------------------------------------------------- #
# Behavioural tests 8 / 9 / 14 — the damage paths to Class I                   #
# --------------------------------------------------------------------------- #

_D_BOUNDS = dict(l_ac_gross=30.0, u_ac_gross=60.0, l_sharpe=0.55, u_sharpe=1.20)


def test_b08_spy_damage_turns_a_would_be_D_into_class_I():
    clean = tcls.classify(**_D_BOUNDS, loyo_passes=True, spy_damage=False,
                          macro_damage=False)
    assert clean.klass == "D"
    spy = tdiag.spy_damage(tinf.Interval(20.0, 18.0, 25.0, 100, 100), n_events=213)
    assert spy.triggered
    damaged = tcls.classify(**_D_BOUNDS, loyo_passes=True, spy_damage=spy.triggered,
                            macro_damage=False)
    assert damaged.klass == "I"
    assert "SPY_BROAD_CALENDAR_PLACEBO" in damaged.triggers
    # a trivial placebo must NOT trigger
    assert not tdiag.spy_damage(tinf.Interval(4.0, 1.0, 7.0, 100, 100), 213).triggered
    # a large NEGATIVE placebo must NOT trigger (one-sided, same-signed)
    assert not tdiag.spy_damage(tinf.Interval(-40.0, -60.0, -20.0, 100, 100), 213).triggered


def test_b09_macro_damage_turns_a_would_be_D_into_class_I():
    macro_ok = tcls.classify(**_D_BOUNDS, loyo_passes=True, spy_damage=False,
                             macro_damage=False)
    assert macro_ok.klass == "D"
    damaged = tcls.classify(**_D_BOUNDS, loyo_passes=True, spy_damage=False,
                            macro_damage=True)
    assert damaged.klass == "I"
    assert "MACRO_QRA_IDENTIFICATION" in damaged.triggers


def test_b09b_macro_ols_is_the_sealed_specification():
    """b0 is the fitted AC_GROSS of an event with no net macro asymmetry."""
    # A deliberately EVALUABLE design: full column rank and a reference group of 30,
    # so the test exercises the OLS rather than the NOT_EVALUABLE short circuit.
    profiles = [({"CPI": 0, "NFP": 0, "FOMC": 0, "QRA": 0}, 30)]
    for name in ("CPI", "NFP", "FOMC", "QRA"):
        for sign in (+1, -1):
            profiles.append(({k: (sign if k == name else 0)
                              for k in K.MACRO_COVARIATES}, 12))
    covs, results, i = [], [], 0
    for vals, count in profiles:
        for _ in range(count):
            t0 = _dt.date(2010, 1, 1) + _dt.timedelta(days=7 * i)
            i += 1
            covs.append(tcov.EventCovariates(t0, f"{t0.year}-{t0.month:02d}",
                                             t0.year, dict(vals)))
            gross = (25.0 + 11.0 * vals["CPI"] - 4.0 * vals["NFP"]
                     + 6.0 * vals["FOMC"] + 2.0 * vals["QRA"])
            results.append(teng.EventResult(t0, t0.year, f"{t0.year}-{t0.month:02d}",
                                            0.0, 0.0, gross, gross - K.COST_BPS,
                                            0.0, "No"))
    res = tdiag.macro_damage(results, covs)
    assert res.evaluable, res.not_evaluable_reasons
    assert res.b0_gross_bps == pytest.approx(25.0, abs=1e-6)
    assert res.coefficients["CPI"] == pytest.approx(11.0, abs=1e-6)
    assert not res.triggered                      # 25.0 >= 16.0
    # and a clean-event effect below the M1 gross bar DOES trigger
    low = [teng.EventResult(r.t0, r.year, r.calendar_month, 0.0, 0.0,
                            r.ac_gross_bps - 15.0, r.ac_net_bps - 15.0, 0.0, "No")
           for r in results]
    assert tdiag.macro_damage(low, covs).triggered


def test_b14_every_class_I_path_is_independently_reachable():
    paths = {
        "LOYO_FRAGILITY": dict(loyo_passes=False, spy_damage=False, macro_damage=False),
        "SPY_BROAD_CALENDAR_PLACEBO": dict(loyo_passes=True, spy_damage=True,
                                           macro_damage=False),
        "MACRO_QRA_IDENTIFICATION": dict(loyo_passes=True, spy_damage=False,
                                         macro_damage=True),
    }
    for trigger, flags in paths.items():
        v = tcls.classify(**_D_BOUNDS, **flags)
        assert v.klass == "I", trigger
        assert trigger in v.triggers
    # the structural NOT_EVALUABLE path, reachable from the CALENDAR alone
    sparse = [tcov.EventCovariates(_dt.date(2010, 1, 1) + _dt.timedelta(days=i),
                                   "2010-01", 2010,
                                   {"CPI": 1, "NFP": -1, "FOMC": 0, "QRA": 0})
              for i in range(50)]
    ne = tdiag.macro_not_evaluable(sparse)
    assert not ne.evaluable and ne.triggered
    assert tcls.classify(**_D_BOUNDS, loyo_passes=True, spy_damage=False,
                         macro_damage=ne.triggered).klass == "I"
    # the §I.3 executed-calendar-contamination path
    assert tcls.classify(**_D_BOUNDS, loyo_passes=True, spy_damage=False,
                         macro_damage=False,
                         executed_calendar_contaminated=True).klass == "I"


# --------------------------------------------------------------------------- #
# Behavioural tests 10 / 11 / 12 — nothing else may touch the verdict          #
# --------------------------------------------------------------------------- #


def test_b10_ief_secondary_cannot_rescue():
    for bounds in (dict(l_ac_gross=-5.0, u_ac_gross=20.0, l_sharpe=0.0, u_sharpe=0.20),
                   dict(l_ac_gross=5.0, u_ac_gross=60.0, l_sharpe=0.1, u_sharpe=1.0)):
        base = tcls.classify(**bounds, loyo_passes=True, spy_damage=False,
                             macro_damage=False)
        assert base.klass in ("B", "C")
        spectacular = tdiag.SecondaryResult(
            n_events=258, mean_net_ac=tinf.Interval(900.0, 800.0, 1000.0, 100, 100))
        assert spectacular.promotion_power == "NONE"
        after = tcls.classify(**bounds, loyo_passes=True, spy_damage=False,
                              macro_damage=False)
        assert after.klass == base.klass
    with open(os.path.join(HERE, "ta_classify.py"), "r", encoding="utf-8") as fh:
        assert "IEF" not in fh.read().replace("IEF and SHY are absent", "")


def test_b11_shy_has_exactly_zero_power():
    with open(os.path.join(HERE, "ta_classify.py"), "r", encoding="utf-8") as fh:
        body = fh.read()
    assert "SHY" not in body.replace("IEF and SHY are absent", "")
    for val in (-900.0, 0.0, +900.0):
        g = tdiag.GradientResult(213, tinf.Interval(val, val - 50, val + 50, 100, 100))
        assert (g.promotion_power, g.damage_power, g.kill_power) == ("NONE",) * 3
        v = tcls.classify(**_D_BOUNDS, loyo_passes=True, spy_damage=False,
                          macro_damage=False)
        assert v.klass == "D"
    assert K.POWERS["SHY_GRADIENT"] == {"promotion": False, "damage": False,
                                        "kill": False}


def test_b12_no_diagnostic_can_ever_promote():
    report = tcls.diagnostics_can_never_promote()
    assert report["illegal_upgrades"] == 0, report["examples"]


# --------------------------------------------------------------------------- #
# Behavioural test 13 — materiality boundary semantics                         #
# --------------------------------------------------------------------------- #


def test_b13_materiality_boundaries_are_exactly_as_sealed():
    # M1: L_N exactly +8.0 satisfies `>= +8.0`
    v = tcls.classify(l_ac_gross=16.0, u_ac_gross=40.0, l_sharpe=0.30, u_sharpe=1.0,
                      loyo_passes=True, spy_damage=False, macro_damage=False)
    assert v.klass == "D" and v.inputs["L_AC_net"] == pytest.approx(8.0)
    # a hair below the bar is NOT D
    assert tcls.classify(l_ac_gross=15.999, u_ac_gross=40.0, l_sharpe=0.30,
                         u_sharpe=1.0, loyo_passes=True, spy_damage=False,
                         macro_damage=False).klass == "C"
    # M2: L_S exactly +0.30 satisfies `>= +0.30`; a hair below does not
    assert tcls.classify(l_ac_gross=16.0, u_ac_gross=40.0, l_sharpe=0.2999,
                         u_sharpe=1.0, loyo_passes=True, spy_damage=False,
                         macro_damage=False).klass == "C"
    # B is STRICT: U_N exactly +8.0 is NOT below the bar, so not B
    assert tcls.classify(l_ac_gross=0.0, u_ac_gross=16.0, l_sharpe=0.1, u_sharpe=0.30,
                         loyo_passes=True, spy_damage=False, macro_damage=False
                         ).klass == "C"
    assert tcls.classify(l_ac_gross=0.0, u_ac_gross=15.999, l_sharpe=0.1,
                         u_sharpe=1.0, loyo_passes=True, spy_damage=False,
                         macro_damage=False).klass == "B"
    # A is inclusive at zero
    assert tcls.classify(l_ac_gross=-40.0, u_ac_gross=0.0, l_sharpe=-1.0,
                         u_sharpe=-0.5, loyo_passes=True, spy_damage=False,
                         macro_damage=False).klass == "A"
    assert tcls.classify(l_ac_gross=-40.0, u_ac_gross=0.001, l_sharpe=-1.0,
                         u_sharpe=-0.5, loyo_passes=True, spy_damage=False,
                         macro_damage=False).klass == "B"


# --------------------------------------------------------------------------- #
# Classification engine — total, single-valued, exhaustive, oracle-checked     #
# --------------------------------------------------------------------------- #


def test_cls_all_five_classes_reachable_and_single_valued():
    counts = tcls.reachability()
    assert all(counts[c] > 0 for c in tcls.CLASSES), counts


def test_cls_matches_the_independent_oracle_everywhere():
    bad = []
    for case in tcls.sweep():
        got = tcls.classify(*case).klass
        want = ORC.oracle_classify(*case)
        if got != want:
            bad.append((case, got, want))
    assert not bad, bad[:3]


def test_cls_status_mapping_is_the_sealed_one():
    assert tcls.classify(**_D_BOUNDS, loyo_passes=True, spy_damage=False,
                         macro_damage=False).research_status == "supported"
    i = tcls.classify(**_D_BOUNDS, loyo_passes=False, spy_damage=False,
                      macro_damage=False)
    assert i.research_status == "unresolved"
    assert i.qualifier == "IDENTIFICATION_INSUFFICIENT_FOR_THE_CLAIM"
    a = tcls.classify(l_ac_gross=-20.0, u_ac_gross=-1.0, l_sharpe=-1.0, u_sharpe=-0.5,
                      loyo_passes=True, spy_damage=False, macro_damage=False)
    assert (a.klass, a.research_status) == ("A", "not_promoted")


# --------------------------------------------------------------------------- #
# Bootstrap — one family, sealed seed, deterministic                           #
# --------------------------------------------------------------------------- #


def test_boot_seed_protocol_is_the_sealed_one():
    a, b = tinf.seed_children()
    ref = np.random.SeedSequence(7).spawn(5)[4].spawn(2)
    assert a.entropy == ref[0].entropy and a.spawn_key == ref[0].spawn_key
    assert b.spawn_key == ref[1].spawn_key
    # the VRP children are untouched
    vrp = np.random.SeedSequence(7).spawn(4)
    assert vrp[0].spawn_key == np.random.SeedSequence(7).spawn(5)[0].spawn_key


def test_boot_is_deterministic_and_reconstructs_zero_months():
    years = list(range(2006, 2011))
    per_year = {y: [10.0 + y % 3] * 12 for y in years}
    months = {y: ([5.0] * 6 + [0.0] * 6) for y in years}     # half the months are zero
    r1 = tinf.year_block_bootstrap(years, {"tlt_gross": per_year}, months, b=200,
                                   rng=tinf.primary_rng())
    r2 = tinf.year_block_bootstrap(years, {"tlt_gross": per_year}, months, b=200,
                                   rng=tinf.primary_rng())
    assert r1.means["tlt_gross"].as_dict() == r2.means["tlt_gross"].as_dict()
    assert r1.sharpe.as_dict() == r2.sharpe.as_dict()
    assert r1.means["tlt_gross"].lower <= r1.means["tlt_gross"].point <= \
        r1.means["tlt_gross"].upper
    # every replicate's monthly series keeps the zero months: 5 years x 12 months
    full = [v for y in years for v in months[y]]
    assert len(full) == 60 and full.count(0.0) == 30
    assert r1.sharpe.point == pytest.approx(ORC.oracle_sharpe(full))


def test_boot_shares_one_set_of_draws_across_tlt_spy_shy():
    years = list(range(2006, 2011))
    vals = {"tlt": {y: [20.0] * 12 for y in years},
            "spy": {y: [1.0] * 12 for y in years},
            "shy": {y: [-2.0] * 12 for y in years}}
    res = tinf.year_block_bootstrap(years, vals, None, b=50, rng=tinf.primary_rng())
    assert set(res.means) == {"tlt", "spy", "shy"}
    for name, v in (("tlt", 20.0), ("spy", 1.0), ("shy", -2.0)):
        assert res.means[name].point == pytest.approx(v)


# --------------------------------------------------------------------------- #
# Cross-boundary / state-continuity                                            #
# --------------------------------------------------------------------------- #


def test_x01_windows_skip_weekends_and_holidays():
    hol = [_dt.date(2020, 1, 20)]
    grid = weekday_grid(_dt.date(2020, 1, 1), 60, holidays=hol)
    assert all(d.weekday() < 5 for d in grid) and hol[0] not in grid
    t0 = grid[20]
    ev = tcal.windows_from_grid([t0], grid, K.PRIMARY_CELL, "TLT")[0]
    assert ev.pre_open == grid[14] and ev.pre_close == grid[19]
    assert ev.post_open == grid[20] and ev.post_close == grid[25]
    assert len(ev.pre_days(grid)) == 5 and len(ev.post_days(grid)) == 5
    assert (ev.pre_close, ev.post_open) == ev.auction_day_bar(grid)


def test_x02_year_boundary_events():
    grid = weekday_grid(_dt.date(2019, 12, 1), 60)
    dec = [d for d in grid if d.month == 12][10]
    jan = [d for d in grid if d.month == 1][3]
    evs = tcal.windows_from_grid([dec, jan], grid, K.PRIMARY_CELL, "TLT")
    assert len(evs) == 2
    assert evs[0].post_close.year == 2020 or evs[0].t0.year == 2019
    assert evs[0].calendar_month.startswith("2019-12")
    assert evs[1].calendar_month.startswith("2020-01")
    months = tcal.month_grid("2019-12", "2020-01")
    assert months == ["2019-12", "2020-01"]


def test_x03_month_grid_spans_years_and_keeps_partial_years():
    grid = tcal.month_grid()
    assert grid[0] == "2006-02" and grid[-1] == "2026-05" and len(grid) == 244
    assert len(tcal.months_of_year(grid, 2006)) == 11
    assert len(tcal.months_of_year(grid, 2026)) == 5
    assert len(tcal.months_of_year(grid, 2015)) == 12
    assert sum(len(tcal.months_of_year(grid, y)) for y in K.PRIMARY_YEARS) == 244


def test_x04_incomplete_windows_are_excluded_complete_ones_included():
    grid = weekday_grid(_dt.date(2020, 1, 1), 30)
    too_early = grid[5]        # needs i-6 -> out of range
    too_late = grid[26]        # needs i+5 -> out of range
    ok = grid[6]
    evs = tcal.windows_from_grid([too_early, too_late, ok], grid, K.PRIMARY_CELL, "TLT")
    assert [e.t0 for e in evs] == [ok]
    off_grid = _dt.date(2020, 1, 4)        # a Saturday, not on the grid
    assert off_grid not in grid
    assert tcal.windows_from_grid([off_grid], grid, K.PRIMARY_CELL, "TLT") == []


def test_x05_monthly_series_rejects_an_event_outside_the_grid():
    r = teng.EventResult(_dt.date(1999, 5, 5), 1999, "1999-05", 0, 0, 0, 0, 0, "No")
    with pytest.raises(KeyError):
        teng.monthly_series([r], tcal.month_grid())


def test_x06_overlap_detection_matches_the_sealed_threshold():
    grid = weekday_grid(_dt.date(2020, 1, 1), 80)
    a, near, far = grid[20], grid[31], grid[32]        # gaps of 11 and 12
    assert tcal.overlapping_pairs(
        tcal.windows_from_grid([a, near], grid, K.PRIMARY_CELL, "TLT"))
    assert not tcal.overlapping_pairs(
        tcal.windows_from_grid([a, far], grid, K.PRIMARY_CELL, "TLT"))


# --------------------------------------------------------------------------- #
# The sealed event calendar reproduces, without any ETF outcome                #
# --------------------------------------------------------------------------- #


def test_seal_primary_calendar_reproduces_213():
    events = tcal.load_sealed_events(K.PRIMARY_CELL)
    check = tcal.validate_primary(events)
    assert check["ok"], check["problems"]
    assert check["n_events"] == 213 and check["n_years"] == 21
    assert check["n_overlaps"] == 0 and check["n_zero_months"] == 31


def test_seal_secondary_calendar_reproduces_258():
    events = tcal.load_sealed_events(K.SECONDARY_CELL)
    check = tcal.validate_secondary(events)
    assert check["ok"], check["problems"]
    assert check["n_events"] == 258 and check["n_overlaps"] == 1


def test_seal_calendar_hash_is_pinned():
    assert tcal.sealed_calendar_sha256() == K.EVENT_CALENDAR_SHA256


def test_seal_max_one_primary_event_per_month_is_checked_not_assumed():
    events = tcal.load_sealed_events(K.PRIMARY_CELL)
    results = [teng.EventResult(e.t0, e.year, e.calendar_month, 0, 0, 0, 0, 0,
                                e.reopening) for e in events]
    teng.assert_max_one_event_per_month(results)          # sealed calendar: passes
    doubled = results + [results[0]]
    with pytest.raises(AssertionError):
        teng.assert_max_one_event_per_month(doubled)      # and the check is not vacuous


# --------------------------------------------------------------------------- #
# The macro covariates and the sealed evaluability rule                        #
# --------------------------------------------------------------------------- #


def test_macro_covariates_are_signed_and_symmetric():
    grid = weekday_grid(_dt.date(2020, 1, 1), 60)
    t0 = grid[20]
    ev = tcal.windows_from_grid([t0], grid, K.PRIMARY_CELL, "TLT")[0]
    pre, post = ev.pre_days(grid), ev.post_days(grid)
    assert tcov.signed_covariate({post[2]}, pre, post) == +1
    assert tcov.signed_covariate({pre[2]}, pre, post) == -1
    assert tcov.signed_covariate({pre[2], post[2]}, pre, post) == 0
    assert tcov.signed_covariate(set(), pre, post) == 0
    assert tcov.signed_covariate({grid[20]}, pre, post) == 0      # the excluded bar


def test_macro_evaluability_rule_is_the_sealed_one():
    def mk(n, vals):
        return [tcov.EventCovariates(_dt.date(2010, 1, 1) + _dt.timedelta(days=i),
                                     "2010-01", 2010, dict(vals)) for i in range(n)]
    allzero = mk(25, {"CPI": 0, "NFP": 0, "FOMC": 0, "QRA": 0})
    assert not tcov.evaluability(allzero)["evaluable"]      # rank deficient
    mixed = mk(19, {"CPI": 0, "NFP": 0, "FOMC": 0, "QRA": 0})
    for i, v in enumerate([{"CPI": 1, "NFP": 0, "FOMC": 0, "QRA": 0},
                           {"CPI": 0, "NFP": 1, "FOMC": 0, "QRA": 0},
                           {"CPI": 0, "NFP": 0, "FOMC": 1, "QRA": 0},
                           {"CPI": 0, "NFP": 0, "FOMC": 0, "QRA": 1}]):
        mixed += mk(3, v)
    ev = tcov.evaluability(mixed)
    assert ev["reference_group_n"] == 19 < K.MACRO_MIN_REFERENCE_GROUP
    assert not ev["evaluable"] and "REFERENCE_GROUP_TOO_SMALL" in ev[
        "not_evaluable_reasons"][0]
    mixed += mk(1, {"CPI": 0, "NFP": 0, "FOMC": 0, "QRA": 0})
    assert tcov.evaluability(mixed)["evaluable"]


def test_macro_real_calendar_crosstab_is_outcome_free_and_not_evaluable():
    """The sealed pre-check, on the real 213 events. Counts only - no return exists."""
    import ta_auction_fetch as auc
    grid = auc.common_grid(auc.trading_calendar())        # presence mask only
    events = tcal.load_sealed_events(K.PRIMARY_CELL)
    covs = tcov.build_covariates(events, grid, tcov.load_macro_calendar())
    ct = tcov.crosstab(covs)
    assert ct["n_events"] == 213
    assert ct["design_matrix_rank"] == 5                  # full column rank
    assert ct["reference_group_n"] < K.MACRO_MIN_REFERENCE_GROUP
    assert ct["evaluable"] is False
    assert tdiag.macro_not_evaluable(covs).triggered
    # QRA reproduces the S1-sealed tabulation exactly
    assert ct["per_covariate"]["QRA"] == {"post_plus1": 0, "neither_0": 207,
                                          "pre_minus1": 6}


# --------------------------------------------------------------------------- #
# Firewall and the hard production-run guard                                   #
# --------------------------------------------------------------------------- #


def test_firewall_s2_paths_are_synthetic():
    grid = weekday_grid(_dt.date(2020, 1, 1), 40)
    _, src = fixture(grid, [grid[20]], {"TLT": flat_logs(grid)})
    assert src.data_kind == auth.SYNTHETIC
    tpx.assert_synthetic(src)
    assert not hasattr(src, "_panel_path")


def test_firewall_rejects_a_real_source_in_validation():
    class Pretend(tpx.PriceSource):
        data_kind = auth.REAL
        def tickers(self): return ("TLT",)
        def grid(self): return []
    with pytest.raises(AssertionError):
        tpx.assert_synthetic(Pretend())


def test_guard_historical_run_without_authorization_is_blocked():
    """At S2 no CTA-EDGE-01-TA grant exists. REAL must refuse."""
    status = auth.authorization_status()
    assert status["active_execution_authorizations"] == 0
    assert status["real_run_authorized"] is False
    with pytest.raises(auth.RunNotAuthorized):
        auth.require_run_authorization(auth.REAL, run_id="TA-RUN-0001")
    auth.require_run_authorization(auth.SYNTHETIC)          # synthetic always passes
    with pytest.raises(auth.RunNotAuthorized):
        auth.require_run_authorization("MAYBE")


def test_guard_fires_before_any_panel_byte_is_read(monkeypatch):
    """The guard must terminate the run BEFORE the panel is opened."""
    opened = []
    real_open = open

    def tracking_open(path, *a, **kw):
        opened.append(str(path))
        return real_open(path, *a, **kw)

    monkeypatch.setattr("builtins.open", tracking_open)
    with pytest.raises(auth.RunNotAuthorized):
        tpx.RealPanelPriceSource(("TLT",))
    assert not any("close_prices_raw" in p for p in opened), opened


def test_guard_ledger_is_read_from_committed_state():
    src = open(os.path.join(HERE, "ta_authorization.py"), "r", encoding="utf-8").read()
    assert "git" in src and "show" in src
    assert auth.LEDGER_RELPATH == "ops/EXECUTION_AUTHORIZATIONS.md"
    assert auth.read_committed("ops/EXECUTION_AUTHORIZATIONS.md") is not None


# --------------------------------------------------------------------------- #
# Report schema                                                                #
# --------------------------------------------------------------------------- #


def _synthetic_report_doc():
    iv = tinf.Interval
    verdict = tcls.classify(l_ac_gross=4.0, u_ac_gross=14.0, l_sharpe=-0.1,
                            u_sharpe=0.22, loyo_passes=True, spy_damage=False,
                            macro_damage=True)
    loyo = tinf.LoyoResult({2006: 1.0}, {2006: 0.1}, 1.0, 2006, True)
    return trep.build_result(
        data_kind=auth.SYNTHETIC, verdict=verdict,
        primary={"n_events": 213, "years": list(K.PRIMARY_YEARS),
                 "mean_gross": iv(9.0, 4.0, 14.0, 10000, 10000),
                 "mean_net_point": 1.0, "sharpe": iv(0.05, -0.1, 0.22, 10000, 10000)},
        loyo=loyo,
        secondary=tdiag.SecondaryResult(258, iv(2.0, -3.0, 7.0, 10000, 10000)),
        gradient=tdiag.GradientResult(213, iv(0.5, -1.0, 2.0, 10000, 10000)),
        placebo=tdiag.spy_damage(iv(1.0, -2.0, 4.0, 10000, 10000), 213),
        macro=tdiag.macro_not_evaluable(
            [tcov.EventCovariates(_dt.date(2010, 1, 1), "2010-01", 2010,
                                  {"CPI": 1, "NFP": -1, "FOMC": 0, "QRA": 0})]),
        monthly_grid={"months": 244, "event_months": 213, "zero_months": 31},
        descriptives={"note": "synthetic"})


def test_report_schema_is_complete_and_stamped_synthetic():
    doc = _synthetic_report_doc()
    assert trep.validate_result(doc)["ok"]
    assert doc["synthetic_only"] == "YES"
    assert doc["run_authorization_id"] is None
    for field in trep.REQUIRED_FIELDS:
        assert field in doc
    assert doc["evidence_ceiling"] == "supported"
    assert "REDUCED_FORM ONLY" in doc["forbidden_interpretations"]
    assert "sqrt" not in str(doc["final_class"])
    assert doc["final_class"] == "B"


def test_report_refuses_a_real_artifact_without_authorization():
    with pytest.raises(ValueError):
        trep.build_result(
            data_kind="REAL", verdict=tcls.classify(1, 2, 0, 0, True, False, False),
            primary={"n_events": 1, "years": [2006],
                     "mean_gross": tinf.Interval(1, 0, 2, 1, 1),
                     "mean_net_point": -7.0,
                     "sharpe": tinf.Interval(0, 0, 0, 1, 1)},
            loyo=tinf.LoyoResult({}, {}, float("nan"), -1, False),
            secondary=None, gradient=None, placebo=None, macro=None,
            monthly_grid={}, run_authorization_id=None)


def test_report_rejects_a_class_I_without_the_mandatory_qualifier():
    doc = dict(_synthetic_report_doc())
    doc["final_class"] = "I"
    doc["research_status"] = "unresolved"
    doc["qualifier"] = ""
    assert not trep.validate_result(doc)["ok"]


# --------------------------------------------------------------------------- #
# End-to-end on synthetic data, checked against the independent oracle         #
# --------------------------------------------------------------------------- #


def test_e2e_synthetic_pipeline_agrees_with_the_oracle():
    grid = weekday_grid(_dt.date(2006, 1, 2), 260 * 5)
    t0s = []
    for y in range(2006, 2011):
        for m in range(1, 13):
            same = [d for d in grid if d.year == y and d.month == m]
            if len(same) > 12:
                t0s.append(same[8])
    # a per-event jitter so the monthly series has non-zero dispersion; without it
    # sd == 0 and the sealed Sharpe is correctly undefined
    logs = {d: 0.0 for d in grid}
    for n, t0 in enumerate(t0s):
        jitter = 6.0 * ((n % 5) - 2)
        part = cycle_logs(grid, [t0], pre_bps=-12.0 + jitter, post_bps=+18.0 + jitter)
        for d in grid:
            if part[d]:
                logs[d] = part[d]
    events, src = fixture(grid, t0s, {"TLT": logs})
    results = teng.event_results(src, "TLT", events)
    teng.assert_max_one_event_per_month(results)

    for r, t0 in zip(results, [e.t0 for e in events]):
        assert r.ac_gross_bps == pytest.approx(
            ORC.oracle_ac_gross_bps(logs, grid, t0), abs=1e-9)
        assert r.ac_net_bps == pytest.approx(
            ORC.oracle_ac_net_bps(logs, grid, t0), abs=1e-9)

    months = tcal.month_grid(results[0].calendar_month, results[-1].calendar_month)
    monthly = teng.monthly_series(results, months)
    assert monthly == pytest.approx(
        ORC.oracle_monthly_series({r.t0: r.ac_net_bps for r in results}, months))
    assert teng.mean_net_ac(results) == pytest.approx(
        ORC.oracle_mean([r.ac_net_bps for r in results]))
    assert teng.calendarised_sharpe(monthly) == pytest.approx(ORC.oracle_sharpe(monthly))

    years = sorted({r.year for r in results})
    boot = tinf.year_block_bootstrap(
        years, {"gross": tinf.group_values_by_year(results, "ac_gross_bps")},
        tinf.group_months_by_year(months, monthly), b=200, rng=tinf.primary_rng())
    loyo = tinf.leave_one_year_out(
        results, tinf.group_months_by_year(months, monthly), years)
    verdict = tcls.classify(boot.means["gross"].lower, boot.means["gross"].upper,
                            boot.sharpe.lower, boot.sharpe.upper,
                            loyo.passes, False, False)
    assert verdict.klass in tcls.CLASSES
    assert verdict.klass == ORC.oracle_classify(
        boot.means["gross"].lower, boot.means["gross"].upper,
        boot.sharpe.lower, boot.sharpe.upper, loyo.passes, False, False)
