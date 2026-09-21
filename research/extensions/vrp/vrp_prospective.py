# -*- coding: utf-8 -*-
"""TSMOM-VRP-01 - module K: the prospective clocks and eligibility engine
(sealed sections P and Q).

VRP-A-PROSPECTIVE
    START        the first VX month-end settlement AFTER the S1 seal; the position is
                 established at that settlement (entry cost charged under section G);
                 the first scored month is the FOLLOWING calendar month.
    N_A          120 COMPLETE, ELIGIBLE, NON-INVALIDATED scored months.
    ELIGIBILITY  a prospective month scores only if every VX exchange business day in it
                 has official settlements for both eligible contracts under section F.4
                 (<= 2 carry-forward days per contract). A month exceeding the maximum is
                 INVALIDATED - not scored, not counted, not disclosed - and the clock
                 WAITS for 120 valid months.
    SINGLE TERMINAL REVEAL: no interim positive look, no adverse oracle, no automatic
                 extension.

VRP-B-PROSPECTIVE
    CONDITION    VRP-A = SUPPORTED, historically or prospectively.
    N_B          120 CALENDAR months from the first prospective sleeve month; THE WINDOW
                 FREEZES THERE and no month is ever added after it.
    n_T_min      10 systemic-tail months inside the frozen window (X46 rule on forward
                 SPY monthly returns).
    TERMINAL     at N_B with fewer than 10 tail months -> UNRESOLVED. NEVER auto-extended.
    SECTION Q.3  no access to protected C-A prospective outcomes and no reconstruction of
                 protected forward canonical returns anywhere. If the VRP-B window
                 finishes before the core's forward months are legitimately readable:
                 DEFERRED_EVALUATION_FROZEN_WINDOW. If they never become legitimately
                 revealable: NOT_EVALUABLE (a governance state, distinct from the
                 evidentiary state `unresolved`).

BOTH CLOCKS ARE BUILT HERE AND NEITHER IS STARTED. `start_prospective` refuses without an
Owner authorisation, exactly as the sealed gate ordering requires; S2 completion is not
sufficient and this module does not pretend otherwise.
"""
from __future__ import annotations

import datetime as _dt
from typing import Dict, List, NamedTuple, Optional, Sequence, Tuple

import vrp_calendar as vcal
import vrp_reveal as vreveal
from vrp_constants import (MAX_CARRY_FORWARD_DAYS, N_A, N_B, S1_SEAL_COMMIT,
                           n_T_min_prosp)

S1_SEAL_UTC = _dt.datetime(2026, 9, 14, 8, 4, 9, tzinfo=_dt.timezone.utc)

DEFERRED = "DEFERRED_EVALUATION_FROZEN_WINDOW"
NOT_EVALUABLE = "NOT_EVALUABLE"


class MonthEligibility(NamedTuple):
    month: str
    sessions: int
    max_carry_forward: int
    eligible: bool
    invalidated: bool


class ClockState(NamedTuple):
    name: str
    started: bool
    start_settlement: Optional[_dt.date]
    first_scored_month: Optional[str]
    scored_months: int
    target: int
    complete: bool


def _rule_sessions_in_month(year: int, month: int) -> List[_dt.date]:
    """Exchange business days of a calendar month under the rule-derived calendar.

    Used only to project FUTURE dates, where no settlement record exists yet; historical
    months use the empirical calendar built from the exchange's own settlements.
    """
    d = _dt.date(year, month, 1)
    out: List[_dt.date] = []
    while d.month == month:
        if vcal.is_rule_business_day(d) or d in vcal.CFE_OPEN_WHEN_EQUITIES_CLOSED:
            out.append(d)
        d += _dt.timedelta(days=1)
    return out


def first_month_end_settlement_after(moment: _dt.datetime) -> _dt.date:
    """Section P START: the first VX month-end settlement strictly after `moment`."""
    day = moment.date()
    year, month = day.year, day.month
    for _ in range(24):
        sessions = _rule_sessions_in_month(year, month)
        if sessions and sessions[-1] > day:
            return sessions[-1]
        month += 1
        if month == 13:
            year, month = year + 1, 1
    raise RuntimeError("no month-end settlement found")


def prospective_a_start() -> Dict[str, object]:
    """The sealed section P start facts. Computing them starts nothing."""
    settlement = first_month_end_settlement_after(S1_SEAL_UTC)
    y, m = (settlement.year, settlement.month)
    m += 1
    if m == 13:
        y, m = y + 1, 1
    return {
        "s1_seal_commit": S1_SEAL_COMMIT,
        "s1_seal_utc": S1_SEAL_UTC.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "entry_settlement": settlement.isoformat(),
        "first_scored_month": "%04d-%02d" % (y, m),
        "N_A": N_A,
        "started": False,
        "note": ("the entry settlement is a CALENDAR fact implied by the seal; the clock "
                 "does not run until an Owner authorisation exists (sections S, T.2)"),
    }


def month_eligibility(month: str, sessions: int,
                      carry_forward_by_contract: Dict[object, int]) -> MonthEligibility:
    """Section P ELIGIBILITY, which is section F.4 applied prospectively."""
    worst = max(carry_forward_by_contract.values()) if carry_forward_by_contract else 0
    ok = worst <= MAX_CARRY_FORWARD_DAYS and sessions > 0
    return MonthEligibility(month=month, sessions=sessions, max_carry_forward=worst,
                            eligible=ok, invalidated=not ok)


def advance_a_clock(eligibilities: Sequence[MonthEligibility]) -> ClockState:
    """Count only COMPLETE, ELIGIBLE, NON-INVALIDATED months toward N_A. An invalidated
    month is not scored, not counted and not disclosed; the clock simply waits."""
    scored = sum(1 for e in eligibilities if e.eligible)
    start = prospective_a_start()
    return ClockState(name="VRP-A-PROSPECTIVE", started=False,
                      start_settlement=_dt.date.fromisoformat(str(start["entry_settlement"])),
                      first_scored_month=str(start["first_scored_month"]),
                      scored_months=scored, target=N_A, complete=scored >= N_A)


def advance_b_clock(calendar_months_elapsed: int, tail_months: int) -> Dict[str, object]:
    """Section Q: N_B is a CALENDAR-month window that FREEZES at 120. The terminal rule
    is evaluated only at N_B and is never auto-extended."""
    frozen = calendar_months_elapsed >= N_B
    state: Optional[str] = None
    if frozen:
        state = "UNRESOLVED" if tail_months < n_T_min_prosp else "EVALUABLE"
    return {"name": "VRP-B-PROSPECTIVE", "started": False,
            "calendar_months_elapsed": calendar_months_elapsed,
            "N_B": N_B, "window_frozen": frozen,
            "tail_months": tail_months, "n_T_min_prosp": n_T_min_prosp,
            "terminal_state": state,
            "auto_extension": False}


def b_evaluation_governance_state(core_forward_legitimately_readable: bool,
                                  window_frozen: bool,
                                  ever_revealable: bool = True) -> Optional[str]:
    """Section Q.3: the paired evaluation happens EXACTLY ONCE, at the first date the
    core's forward months become legitimately readable."""
    if not ever_revealable:
        return NOT_EVALUABLE
    if window_frozen and not core_forward_legitimately_readable:
        return DEFERRED
    return None


def start_prospective(clock: str) -> None:
    """Starting a clock generates real prospective outcomes, so it is an Owner gate."""
    vreveal.require_run_authorization(vreveal.REAL, run_id="")
    raise RuntimeError("unreachable during S2: no authorisation can exist yet (%s)" % clock)
