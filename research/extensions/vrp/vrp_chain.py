# -*- coding: utf-8 -*-
"""TSMOM-VRP-01 - module C: normalized constant-maturity contract chain.

Builds, for every exchange business day, the pair of eligible monthly contracts
(front, second) and their section F.3 roll weights, applies the section F.4 missing-
settlement rule, and exposes the per-month validity that section F.6 needs.

WHAT THIS MODULE DOES NOT DO
    It does not compute a return, a variation margin, a basis, a carry, a roll yield
    or any average of prices. It produces a price PATH and a WEIGHT path. Stage A
    (`vrp_stage_a`) is the only place a return is formed, and section 1 of the S2
    authorisation forbids running that over the real chain during S2.
"""
from __future__ import annotations

import datetime as _dt
from typing import Dict, List, NamedTuple, Optional, Sequence, Tuple

import vrp_calendar as vcal
import vrp_raw as vraw
from vrp_constants import MAX_CARRY_FORWARD_DAYS


class ChainDay(NamedTuple):
    date: _dt.date
    front_key: Tuple[str, _dt.date]
    second_key: Tuple[str, _dt.date]
    w_front: float
    w_second: float
    front_price: Optional[float]     # comparable points; None if unavailable even after carry
    second_price: Optional[float]
    front_carried: bool              # True if this is a carried-forward prior settlement
    second_carried: bool


class MonthStatus(NamedTuple):
    month: str                       # "YYYY-MM"
    sessions: int
    carry_forward_by_contract: Dict[Tuple[str, _dt.date], int]
    max_carry_forward: int
    missing_without_prior: int       # held contract with no prior settlement to carry
    valid: bool


class Chain(NamedTuple):
    days: Tuple[ChainDay, ...]
    calendar: vcal.ExchangeCalendar
    months: Dict[str, MonthStatus]
    expiries: Tuple[_dt.date, ...]
    prices: Dict[Tuple[str, _dt.date], Dict[_dt.date, Optional[float]]]


def _month_key(d: _dt.date) -> str:
    return "%04d-%02d" % (d.year, d.month)


def build_chain(contracts: Sequence[vraw.Contract],
                calendar: vcal.ExchangeCalendar,
                start: Optional[_dt.date] = None,
                end: Optional[_dt.date] = None) -> Chain:
    """Assemble the daily front/second chain with section F.3 weights and section F.4 carry."""
    ordered = sorted(contracts, key=lambda c: (c.final_settlement_date, c.contract_month))
    expiries = [c.final_settlement_date for c in ordered]
    by_key = {(c.root, c.final_settlement_date): c for c in ordered}
    prices = {k: vraw.normalize_contract(c) for k, c in by_key.items()}

    days: List[ChainDay] = []
    # Roll periods: P_k = business days in [E_(k-1), E_k). The first period has no
    # E_(k-1), so the chain begins at the first expiry (the contract's own listing
    # history before that is not a constant-maturity period under section F.3).
    for i in range(1, len(ordered) - 1):
        prev_expiry = expiries[i - 1]
        expiry = expiries[i]
        period = vcal.roll_period(calendar, prev_expiry, expiry)
        if not period:
            continue
        weights = vcal.roll_weights(period)
        front_key = (ordered[i].root, expiry)
        second_key = (ordered[i + 1].root, expiries[i + 1])
        for d in period:
            if start is not None and d < start:
                continue
            if end is not None and d > end:
                continue
            wf, ws = weights[d]
            fp, fc = _price_with_carry(prices[front_key], d, calendar)
            sp, sc = _price_with_carry(prices[second_key], d, calendar)
            days.append(ChainDay(date=d, front_key=front_key, second_key=second_key,
                                 w_front=wf, w_second=ws,
                                 front_price=fp, second_price=sp,
                                 front_carried=fc, second_carried=sc))
    days.sort(key=lambda r: r.date)
    return Chain(days=tuple(days), calendar=calendar,
                 months=_month_statuses(days),
                 expiries=tuple(expiries),
                 prices=prices)


def _price_with_carry(series: Dict[_dt.date, Optional[float]],
                      d: _dt.date,
                      calendar: vcal.ExchangeCalendar) -> Tuple[Optional[float], bool]:
    """Section F.4: on a missing official settlement, carry the prior official settlement
    forward and FLAG the day. Never interpolate, never substitute another price field,
    never use a nearby contract's price."""
    p = series.get(d)
    if p is not None:
        return p, False
    # walk back over exchange business days to the last official settlement
    i = calendar.index(d) if d in calendar else None
    if i is None:
        return None, False
    j = i - 1
    while j >= 0:
        prior = calendar.days[j]
        q = series.get(prior)
        if q is not None:
            return q, True
        j -= 1
    # nothing to carry forward: not a carry-forward day, an outright absence
    return None, False


def _month_statuses(days: Sequence[ChainDay]) -> Dict[str, MonthStatus]:
    """Per-calendar-month section F.4 accounting: carry-forward days PER CONTRACT."""
    buckets: Dict[str, List[ChainDay]] = {}
    for row in days:
        buckets.setdefault(_month_key(row.date), []).append(row)
    out: Dict[str, MonthStatus] = {}
    for month, rows in buckets.items():
        counts: Dict[Tuple[str, _dt.date], int] = {}
        missing = 0
        for r in rows:
            if r.front_carried:
                counts[r.front_key] = counts.get(r.front_key, 0) + 1
            if r.second_carried:
                counts[r.second_key] = counts.get(r.second_key, 0) + 1
            if r.front_price is None or r.second_price is None:
                missing += 1
        worst = max(counts.values()) if counts else 0
        out[month] = MonthStatus(
            month=month,
            sessions=len(rows),
            carry_forward_by_contract=counts,
            max_carry_forward=worst,
            missing_without_prior=missing,
            valid=(worst <= MAX_CARRY_FORWARD_DAYS and missing == 0),
        )
    return out


def first_eligible_complete_month(chain: Chain, last_month: str) -> Optional[str]:
    """Section F.6, mechanical: the first calendar month from which, THROUGH the Stage-A
    cutoff, every month is valid under section F.4.

    Implemented as the start of the maximal TERMINAL run of valid months ending at
    `last_month`. Determined from data availability under this rule alone, never from
    outcomes.
    """
    months = sorted(m for m in chain.months if m <= last_month)
    if not months or last_month not in chain.months:
        return None
    first = None
    for m in reversed(months):
        if not chain.months[m].valid:
            break
        first = m
    # months must also be contiguous back to `first`
    return first


def weights_sum_to_one(chain: Chain, tol: float = 1e-12) -> Tuple[bool, List[str]]:
    bad = [r.date.isoformat() for r in chain.days if abs(r.w_front + r.w_second - 1.0) > tol]
    return (not bad), bad[:20]


def front_zero_before_expiry(chain: Chain, tol: float = 1e-12) -> Tuple[bool, List[str]]:
    """Section F.3: the front weight is 0 on the last settlement before final settlement."""
    last_of_period: Dict[Tuple[str, _dt.date], ChainDay] = {}
    for r in chain.days:
        last_of_period[r.front_key] = r
    bad = [k[1].isoformat() for k, r in last_of_period.items() if abs(r.w_front) > tol]
    return (not bad), sorted(bad)[:20]


def daily_transfer_is_uniform(chain: Chain, tol: float = 1e-12) -> Tuple[bool, List[str]]:
    """Each business day in P_k moves exactly 1/dt of the sensitivity from F_k to F_(k+1)."""
    periods: Dict[Tuple[str, _dt.date], List[ChainDay]] = {}
    for r in chain.days:
        periods.setdefault(r.front_key, []).append(r)
    bad: List[str] = []
    for key, rows in periods.items():
        rows = sorted(rows, key=lambda r: r.date)
        dt = len(rows)
        for a, bnext in zip(rows, rows[1:]):
            if abs((a.w_front - bnext.w_front) - 1.0 / dt) > tol:
                bad.append(bnext.date.isoformat())
    return (not bad), sorted(bad)[:20]
