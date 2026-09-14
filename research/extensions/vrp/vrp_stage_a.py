# -*- coding: utf-8 -*-
"""TSMOM-VRP-01 - module H: the Stage-A accounting engine (sealed section E).

STAGE A IS A RETURN-ON-COMMITTED-CAPITAL RESEARCH BENCHMARK, NOT A SELF-FINANCING
WEALTH PATH. The committed capital K is CONSTANT across the window and is the
denominator of every Stage-A return.

    VM_d    = sum_i q_i,(d-1) * M_i * ( S_i,d - S_i,d-1 )      every exchange business day
              with q_i SIGNED NEGATIVE for the short (sections D.2, F.3)

SIGN CONVENTION - READ THIS BEFORE CHANGING THE LINE ABOVE.
    Section E.1 writes the variation margin as `VM_d = - sum_i q_i,(d-1) * M_i * (S_i,d -
    S_i,d-1)` while section D.2 defines `q_i` as "signed negative for the short" and
    immediately adds that "the sensitivity is stated as the absolute dollar loss per +1
    point". Taken with a signed-negative q, the leading minus would make the position
    GAIN when settlements rise, which is a LONG. That is excluded by the sealed object
    itself: section A calls it a "short position", and section D.2 fixes
    `Loss_J = J * sum_i q_i M_i = 0.30 * K` as a LOSS under a +30-point move. The two
    readings of section E.1 - a leading minus on ABSOLUTE quantities, or no leading minus
    on SIGNED quantities - are the same arithmetic, and both give: settlements rise ->
    the short loses. This module implements the signed form. `vrp_tests` pins the
    economics directly (`test_i12_short_position_loses_when_the_curve_rises`) so the sign
    cannot silently invert.

    r_A,t   = ( sum_{d in month t} VM_d  -  cost_t ) / K        EXCESS OF CASH
    K reset = at the last exchange business day of each calendar month, after that day's
              settlement, by BENCHMARK CONVENTION only. In Stage A the sensitivity is
              recomputed from an unchanged K, so NO reset trade occurs and no reset cost
              is charged. (Stage B, where K_t moves with book wealth, does trade.)
    clipping= NONE. A month whose cumulative loss exceeds K is recorded AS COMPUTED,
              below -100 %, and a CAPITAL_EXHAUSTION event is logged. No forced
              liquidation is modelled in Stage A - that is Stage B's object.

Collateral yield cancels by construction: the primary is in excess of cash on K. The
FM-1 collateral total-return version (section E.3) is DESCRIPTIVE ONLY (R13) and lives
in `descriptive_total_return`, which the primary path never calls.

S2 AUTHORISATION BOUNDARY
    This engine may be IMPLEMENTED and TESTED ON SYNTHETIC DATA in S2. It may NOT be
    executed across the real historical VX chain in S2. `run_stage_a` therefore demands
    a `data_kind` and routes REAL through `vrp_reveal.require_run_authorization`, which
    cannot be satisfied during S2 because no Owner execution authorisation exists.
"""
from __future__ import annotations

import datetime as _dt
from typing import Dict, List, NamedTuple, Optional, Sequence, Tuple

import vrp_costs as vcosts
import vrp_reveal as vreveal
import vrp_sizing as vsizing
from vrp_constants import STANDARD_MULTIPLIER

Key = Tuple[str, _dt.date]


class DayInput(NamedTuple):
    """One exchange business day of the constant-maturity chain."""
    date: _dt.date
    front_key: Key
    second_key: Key
    w_front: float
    w_second: float
    front_price: float        # comparable points
    second_price: float       # comparable points
    month_end: bool           # last exchange business day of its calendar month


class MonthResult(NamedTuple):
    month: str
    variation_margin: float
    cost: float
    r_A: float
    capital_exhaustion: bool
    intra_month_exhaustion: bool
    sessions: int
    contract_sides_traded: int


class StageAResult(NamedTuple):
    months: Tuple[MonthResult, ...]
    K: float
    capital_exhaustion_months: Tuple[str, ...]


def _month_key(d: _dt.date) -> str:
    return "%04d-%02d" % (d.year, d.month)


def target_holdings(day: DayInput, K: float) -> Dict[Key, float]:
    """Signed contract quantities for one day: q_i = - w_i * S(K) / M_i (section F.3)."""
    legs = [(day.front_key, day.w_front, STANDARD_MULTIPLIER),
            (day.second_key, day.w_second, STANDARD_MULTIPLIER)]
    return {h.key: h.quantity for h in vsizing.holdings_for(K, legs)}


def run_stage_a(days: Sequence[DayInput],
                K: float,
                data_kind: str,
                run_id: str = "") -> StageAResult:
    """The sealed Stage-A benchmark.

    `data_kind` must be `vrp_reveal.SYNTHETIC` or `vrp_reveal.REAL`. REAL is gated.
    """
    vreveal.require_run_authorization(data_kind, run_id)
    if not days:
        return StageAResult(months=(), K=K, capital_exhaustion_months=())

    prices: Dict[Key, float] = {}
    holdings: Dict[Key, float] = {}
    by_month: Dict[str, Dict[str, float]] = {}
    order: List[str] = []

    for day in days:
        month = _month_key(day.date)
        if month not in by_month:
            by_month[month] = {"vm": 0.0, "cost": 0.0, "sessions": 0, "sides": 0,
                               "min_cum": 0.0}
            order.append(month)
        bucket = by_month[month]
        bucket["sessions"] += 1

        # 1. variation margin on the holdings carried into today, at today's settlement
        today_prices = {day.front_key: day.front_price, day.second_key: day.second_price}
        vm = 0.0
        for key, q in holdings.items():
            if key in today_prices and key in prices:
                vm += q * STANDARD_MULTIPLIER * (today_prices[key] - prices[key])
        bucket["vm"] += vm

        # 2. roll to today's calendar weights, at today's settlement, at section G cost
        wanted = target_holdings(day, K)
        cost = 0.0
        sides = 0
        for key in set(wanted) | set(holdings):
            dq = wanted.get(key, 0.0) - holdings.get(key, 0.0)
            if dq != 0.0:
                cost += vcosts.cost_dollars(day.date, dq, STANDARD_MULTIPLIER)
                sides += 1
        bucket["cost"] += cost
        bucket["sides"] += sides

        holdings = wanted
        prices = dict(today_prices)

        running = bucket["vm"] - bucket["cost"]
        if running < bucket["min_cum"]:
            bucket["min_cum"] = running

        # 3. month-end: K is restored BY CONVENTION. K is constant in Stage A, so the
        #    sensitivity is unchanged and NO reset trade occurs.
        if day.month_end:
            pass

    months: List[MonthResult] = []
    exhausted: List[str] = []
    for month in order:
        bucket = by_month[month]
        net = bucket["vm"] - bucket["cost"]
        r = net / K                      # NO CLIPPING: recorded as computed
        exhaust = net < -K
        if exhaust:
            exhausted.append(month)
        months.append(MonthResult(
            month=month,
            variation_margin=bucket["vm"],
            cost=bucket["cost"],
            r_A=r,
            capital_exhaustion=exhaust,
            intra_month_exhaustion=bucket["min_cum"] < -K,
            sessions=int(bucket["sessions"]),
            contract_sides_traded=int(bucket["sides"]),
        ))
    return StageAResult(months=tuple(months), K=K,
                        capital_exhaustion_months=tuple(exhausted))


def annualised_mean(monthly_returns: Sequence[float]) -> float:
    """A = 12 * mean( r_A,t )  (section C.1). ARITHMETIC. Never a CAGR."""
    if not monthly_returns:
        raise ValueError("no months")
    return 12.0 * (sum(monthly_returns) / len(monthly_returns))


def classify(lower: float, upper: float,
             plus_E: float, minus_F: float) -> Dict[str, str]:
    """Section C.3. Strict endpoints; exactly one state holds; the point estimate never
    classifies."""
    if upper < minus_F:
        return {"state": "NOT_PROMOTED", "failure_class": "4",
                "class_name": "TARGET_MARGIN_RELIABLY_EXCLUDED",
                "subtag": "materially_adverse"}
    if upper < plus_E:
        return {"state": "NOT_PROMOTED", "failure_class": "4",
                "class_name": "TARGET_MARGIN_RELIABLY_EXCLUDED",
                "subtag": "usefulness_excluded"}
    if lower <= plus_E <= upper:
        return {"state": "UNRESOLVED", "failure_class": "3",
                "class_name": "INSUFFICIENT_EVIDENCE_LOW_POWER", "subtag": ""}
    return {"state": "SUPPORTED", "failure_class": "", "class_name": "", "subtag": ""}


def descriptive_total_return(monthly_excess: Sequence[float],
                             rf_monthly: Sequence[Optional[float]]) -> List[Optional[float]]:
    """R13 / section E.3, DESCRIPTIVE ONLY, PROMOTION_POWER = NONE.

    r_A,t + rf_t under the FM-1 convention, applied to all of K. A month whose FM-1
    print is missing within the 7-calendar-day lookback is undefined and reported as
    such; the primary is unaffected.
    """
    out: List[Optional[float]] = []
    for r, rf in zip(monthly_excess, rf_monthly):
        out.append(None if rf is None else r + rf)
    return out
