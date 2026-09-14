# -*- coding: utf-8 -*-
"""TSMOM-VRP-01 - module D: trading / expiry calendar.

Two calendars, deliberately separated:

*   the RULE-DERIVED calendar: the published Cboe Options holiday rule, implemented
    mechanically, used to DERIVE candidate monthly final-settlement dates and to
    CROSS-CHECK the empirical calendar (contract section L, "cross-checked against
    the NYSE calendar for consistency");
*   the EMPIRICAL CFE business-day calendar: the union of official settlement dates
    across every acquired monthly contract. This is the contract's own declared
    construction (section L, exchange trading calendar row, fallback authority) and
    it is the calendar that GOVERNS roll weights and the section F.4 missing-price
    rule, because "a missing official settlement on an exchange business day" is
    only well defined against the set of days on which the exchange actually
    settled VX.

The published monthly final-settlement rule (section F.2, section L):

    The final settlement date is the Wednesday thirty days prior to the third Friday
    of the calendar month immediately following the month in which the contract
    expires. If that Wednesday, or the Friday thirty days following it, is a Cboe
    Options holiday, the final settlement date is the business day immediately
    preceding that Wednesday.

This module computes dates only. It reads no price and computes no return.
"""
from __future__ import annotations

import datetime as _dt
from typing import Dict, Iterable, List, Sequence, Set, Tuple

MONTH_CODES = "FGHJKMNQUVXZ"   # Jan..Dec


def month_code(month: int) -> str:
    return MONTH_CODES[month - 1]


def code_to_month(code: str) -> int:
    return MONTH_CODES.index(code) + 1


# --------------------------------------------------------------------------- #
# Rule-derived US equity / Cboe Options holiday calendar
# --------------------------------------------------------------------------- #
def _nth_weekday(year: int, month: int, weekday: int, n: int) -> _dt.date:
    """The n-th `weekday` (Mon=0) of `year`-`month`."""
    d = _dt.date(year, month, 1)
    offset = (weekday - d.weekday()) % 7
    return d + _dt.timedelta(days=offset + 7 * (n - 1))


def _last_weekday(year: int, month: int, weekday: int) -> _dt.date:
    """The last `weekday` (Mon=0) of the month: walk back from the month's LAST day."""
    if month == 12:
        last = _dt.date(year, 12, 31)
    else:
        last = _dt.date(year, month + 1, 1) - _dt.timedelta(days=1)
    return last - _dt.timedelta(days=(last.weekday() - weekday) % 7)


def _easter(year: int) -> _dt.date:
    """Anonymous Gregorian computus."""
    a = year % 19
    bb = year // 100
    c = year % 100
    d = bb // 4
    e = bb % 4
    f = (bb + 8) // 25
    g = (bb - f + 1) // 3
    h = (19 * a + bb - d - g + 15) % 30
    i = c // 4
    kk = c % 4
    ll = (32 + 2 * e + 2 * i - h - kk) % 7
    m = (a + 11 * h + 22 * ll) // 451
    month = (h + ll - 7 * m + 114) // 31
    day = ((h + ll - 7 * m + 114) % 31) + 1
    return _dt.date(year, month, day)


def _observed(d: _dt.date) -> List[_dt.date]:
    """US exchange observation rule for a fixed-date holiday."""
    if d.weekday() == 5:          # Saturday -> preceding Friday
        return [d - _dt.timedelta(days=1)]
    if d.weekday() == 6:          # Sunday -> following Monday
        return [d + _dt.timedelta(days=1)]
    return [d]


# National days of mourning and weather closures on which the US equity and Cboe
# options markets were closed. Enumerated because no rule generates them.
SPECIAL_CLOSURES: Tuple[_dt.date, ...] = (
    _dt.date(2004, 6, 11),    # President Reagan, national day of mourning
    _dt.date(2007, 1, 2),     # President Ford, national day of mourning
    _dt.date(2012, 10, 29),   # Hurricane Sandy
    _dt.date(2012, 10, 30),   # Hurricane Sandy
    _dt.date(2018, 12, 5),    # President G. H. W. Bush, national day of mourning
    _dt.date(2025, 1, 9),     # President Carter, national day of mourning
)


# Dates on which the US EQUITY market was closed but the CBOE FUTURES EXCHANGE held a
# session and published official VX settlements. CFE keeps its own calendar; these are
# the only such dates in the acquired record, and each is enumerated here so the
# empirical-vs-rule cross-check has zero UNEXPLAINED differences (section L: the exchange
# calendar is "cross-checked against the NYSE calendar for consistency").
#
#   2015-04-03  Good Friday. CFE held a session that day (the US employment report fell
#               on Good Friday); the equity market was closed.
#   2018-12-05  National day of mourning for President G. H. W. Bush: NYSE and Cboe
#               Options closed, CFE traded.
#   2025-01-09  National day of mourning for President Carter: same pattern.
#
# These are established from the exchange's OWN published settlement record - the primary
# per-contract files - which is the section L authority for the trading calendar, and are
# consistent with the acquired CFE holiday-calendar page. They are declared, not inferred
# silently: `vrp_validators.check_calendar_consistency` fails on any mismatch NOT listed
# here.
CFE_OPEN_WHEN_EQUITIES_CLOSED: Tuple[_dt.date, ...] = (
    _dt.date(2015, 4, 3),
    _dt.date(2018, 12, 5),
    _dt.date(2025, 1, 9),
)


def holidays(year: int) -> Set[_dt.date]:
    """Cboe Options / US equity market holidays for `year` (rule-derived)."""
    out: Set[_dt.date] = set()
    # New Year's Day: when 1 Jan is a Saturday the market is NOT closed on 31 Dec.
    ny = _dt.date(year, 1, 1)
    if ny.weekday() == 6:
        out.add(_dt.date(year, 1, 2))
    elif ny.weekday() != 5:
        out.add(ny)
    out.add(_nth_weekday(year, 1, 0, 3))            # Martin Luther King Jr. Day
    out.add(_nth_weekday(year, 2, 0, 3))            # Washington's Birthday
    out.add(_easter(year) - _dt.timedelta(days=2))  # Good Friday
    out.add(_last_weekday(year, 5, 0))              # Memorial Day
    if year >= 2022:                                # Juneteenth
        out.update(_observed(_dt.date(year, 6, 19)))
    out.update(_observed(_dt.date(year, 7, 4)))     # Independence Day
    out.add(_nth_weekday(year, 9, 0, 1))            # Labor Day
    out.add(_nth_weekday(year, 11, 3, 4))           # Thanksgiving
    out.update(_observed(_dt.date(year, 12, 25)))   # Christmas
    out.update(d for d in SPECIAL_CLOSURES if d.year == year)
    return out


_HOLIDAY_CACHE: Dict[int, Set[_dt.date]] = {}


def is_holiday(d: _dt.date) -> bool:
    if d.year not in _HOLIDAY_CACHE:
        _HOLIDAY_CACHE[d.year] = holidays(d.year)
    return d in _HOLIDAY_CACHE[d.year]


def is_rule_business_day(d: _dt.date) -> bool:
    return d.weekday() < 5 and not is_holiday(d)


def prev_rule_business_day(d: _dt.date) -> _dt.date:
    d -= _dt.timedelta(days=1)
    while not is_rule_business_day(d):
        d -= _dt.timedelta(days=1)
    return d


# --------------------------------------------------------------------------- #
# Monthly VX final-settlement date
# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
# Dated expiry-rule registry
# --------------------------------------------------------------------------- #
# VX has had TWO published monthly final-settlement rules.
#
#   ORIGINAL (contract months up to and including 2004-10)
#       the Wednesday immediately prior to the third Friday of the EXPIRING month.
#       The first VX contract, April 2004, settled on Wednesday 14 April 2004, the
#       Wednesday immediately before the third Friday of April 2004 (16 April).
#
#   CURRENT (contract months from 2004-11 onward)
#       the Wednesday thirty days prior to the third Friday of the calendar month
#       IMMEDIATELY FOLLOWING the expiring month - the rule transcribed in the sealed
#       contract, sections F.2 and L.
#
# Both rules carry the same holiday adjustment: if that Wednesday, or the Friday it is
# measured against, is a Cboe Options holiday, final settlement moves to the business
# day immediately preceding that Wednesday.
#
# WHERE THE BOUNDARY IS, AND HOW FAR THE DATA PINS IT. The two rules give the SAME date
# in most months, so the observed history cannot date the change to the month. It can
# bracket it exactly: the last contract whose observed final settlement follows the
# ORIGINAL rule and not the current one is 2004-10 (observed 2004-10-13, current rule
# 2004-10-20), and the first contract whose observed final settlement follows the
# CURRENT rule and not the original one is 2005-12 (observed 2005-12-21, original rule
# 2005-12-14). For every contract month in between the two rules agree, so the choice of
# boundary inside (2004-10, 2005-12] changes NO date this lineage uses. 2004-11 is taken
# as the boundary; `vrp_validators.check_expiry_identity` proves the registry reproduces
# the observed final settlement of every acquired contract, which is what section L
# actually requires ("rule-derived date = observed final-settlement date for every
# contract; mismatches enumerated").
EXPIRY_RULE_BOUNDARY = (2004, 11)   # first contract month on the CURRENT rule


def _adjust(wednesday: _dt.date, friday: _dt.date) -> _dt.date:
    if is_holiday(wednesday) or is_holiday(friday):
        return prev_rule_business_day(wednesday)
    return wednesday


def monthly_final_settlement_current_rule(year: int, month: int) -> _dt.date:
    """The Wednesday thirty days prior to the third Friday of the FOLLOWING month."""
    ny, nm = (year + 1, 1) if month == 12 else (year, month + 1)
    third_friday = _nth_weekday(ny, nm, 4, 3)
    wednesday = third_friday - _dt.timedelta(days=30)
    assert wednesday.weekday() == 2, "thirty days before a third Friday is always a Wednesday"
    return _adjust(wednesday, third_friday)


def monthly_final_settlement_original_rule(year: int, month: int) -> _dt.date:
    """The Wednesday immediately prior to the third Friday of the EXPIRING month."""
    third_friday = _nth_weekday(year, month, 4, 3)
    wednesday = third_friday - _dt.timedelta(days=2)
    assert wednesday.weekday() == 2
    return _adjust(wednesday, third_friday)


def monthly_final_settlement(year: int, month: int) -> _dt.date:
    """Rule-derived final-settlement date under the dated expiry-rule registry."""
    if (year, month) < EXPIRY_RULE_BOUNDARY:
        return monthly_final_settlement_original_rule(year, month)
    return monthly_final_settlement_current_rule(year, month)


def monthly_contracts(first: Tuple[int, int],
                      last: Tuple[int, int]) -> List[Tuple[int, int, _dt.date]]:
    """[(year, month, final_settlement_date)] inclusive, ordered by final settlement."""
    out: List[Tuple[int, int, _dt.date]] = []
    y, m = first
    while (y, m) <= last:
        out.append((y, m, monthly_final_settlement(y, m)))
        m += 1
        if m == 13:
            y, m = y + 1, 1
    out.sort(key=lambda t: (t[2], t[0], t[1]))
    return out


# --------------------------------------------------------------------------- #
# Empirical CFE business-day calendar
# --------------------------------------------------------------------------- #
class ExchangeCalendar:
    """The operative CFE business-day calendar: the sorted union of official
    settlement dates across every acquired monthly contract (section L fallback
    authority, which is the contract's own construction for this calendar)."""

    def __init__(self, days: Iterable[_dt.date]):
        self.days: List[_dt.date] = sorted(set(days))
        self._index: Dict[_dt.date, int] = {d: i for i, d in enumerate(self.days)}

    def __len__(self) -> int:
        return len(self.days)

    def __contains__(self, d: _dt.date) -> bool:
        return d in self._index

    def index(self, d: _dt.date) -> int:
        return self._index[d]

    def between(self, start: _dt.date, end: _dt.date) -> List[_dt.date]:
        """Business days with start <= d <= end."""
        return [d for d in self.days if start <= d <= end]

    def sessions_in_month(self, year: int, month: int) -> List[_dt.date]:
        return [d for d in self.days if d.year == year and d.month == month]

    def last_session_of_month(self, year: int, month: int) -> _dt.date:
        ss = self.sessions_in_month(year, month)
        if not ss:
            raise KeyError("no exchange session in %04d-%02d" % (year, month))
        return ss[-1]

    def previous(self, d: _dt.date) -> _dt.date:
        i = self._index[d]
        if i == 0:
            raise KeyError("no session before %s" % d)
        return self.days[i - 1]

    def next(self, d: _dt.date) -> _dt.date:
        i = self._index[d]
        if i + 1 >= len(self.days):
            raise KeyError("no session after %s" % d)
        return self.days[i + 1]

    def cross_check_rule(self, start: _dt.date, end: _dt.date) -> Dict[str, List[_dt.date]]:
        """Compare the empirical calendar with the rule-derived one over [start, end].

        Returns the two mismatch sets. Dates only; no price is touched.
        """
        emp = set(self.between(start, end))
        rule: Set[_dt.date] = set()
        d = start
        while d <= end:
            if is_rule_business_day(d):
                rule.add(d)
            d += _dt.timedelta(days=1)
        extra = sorted(emp - rule)
        absent = sorted(rule - emp)
        declared = set(CFE_OPEN_WHEN_EQUITIES_CLOSED)
        return {
            "settled_but_not_rule_business_day": extra,
            "rule_business_day_without_any_settlement": absent,
            "explained_cfe_open": [d for d in extra if d in declared],
            "unexplained": sorted([d for d in extra if d not in declared] + absent),
        }


def roll_period(calendar: ExchangeCalendar,
                prev_expiry: _dt.date,
                expiry: _dt.date) -> List[_dt.date]:
    """P_k = { exchange business days d : E_(k-1) <= d < E_k }  (section F.3)."""
    return [d for d in calendar.days if prev_expiry <= d < expiry]


def roll_weights(period: Sequence[_dt.date]) -> Dict[_dt.date, Tuple[float, float]]:
    """w_front(d) = dr(d)/dt, w_second = 1 - w_front  (section F.3).

    A pure function of the calendar. `dr(d)` = business days in the period STRICTLY
    AFTER d, so w_front = (dt-1)/dt on the first day of the period and 0 on its last
    day (the last settlement before final settlement).
    """
    dt = len(period)
    if dt == 0:
        return {}
    out: Dict[_dt.date, Tuple[float, float]] = {}
    for i, d in enumerate(period):
        dr = dt - 1 - i
        wf = dr / dt
        out[d] = (wf, 1.0 - wf)
    return out
