"""CTA-EDGE-01-TA — the outcome engine.

Components C–I of the S2 build: the PRE leg, the POST leg, the combined AC, cost
accounting, the calendarised monthly P&L, the mean NET AC statistic and the
calendarised Sharpe.

Every formula here is transcribed from the sealed §D, §E and §F. Prices arrive only
through a `PriceSource`, so the engine cannot reach the real panel on its own.
"""

from __future__ import annotations

import datetime as _dt
import math
from dataclasses import dataclass
from typing import Dict, List, Mapping, Sequence

import ta_contract as K
from ta_calendar import Event, month_grid
from ta_prices import PriceSource

SHORT = -1
FLAT = 0
LONG = +1


@dataclass(frozen=True)
class Leg:
    """One mark of the sealed position path."""
    day: _dt.date
    from_position: int
    to_position: int
    one_way_units: int


def position_path(event: Event) -> List[Leg]:
    """The sealed §E.1 path, written out mark by mark.

    flat -> SHORT at close(t0-6); SHORT -> flat at close(t0-1); FLAT across the
    excluded auction-day bar; flat -> LONG at close(t0); LONG -> flat at close(t0+5).

    There is no short-to-long flip. Exposure across GRID[i-1] -> GRID[i] is ZERO, and
    `exposure_on_auction_day_bar()` proves it rather than asserting it in prose.
    """
    return [
        Leg(event.pre_open, FLAT, SHORT, 1),
        Leg(event.pre_close, SHORT, FLAT, 1),
        Leg(event.post_open, FLAT, LONG, 1),
        Leg(event.post_close, LONG, FLAT, 1),
    ]


def exposure_on_auction_day_bar(event: Event) -> int:
    """The position held across the excluded bar close(t0-1) -> close(t0). Always 0."""
    held = FLAT
    for leg in position_path(event):
        if leg.day <= event.pre_close:
            held = leg.to_position
    return held


def one_way_units(event: Event) -> int:
    return sum(leg.one_way_units for leg in position_path(event))


# --------------------------------------------------------------------------- #
# C / D / E — the legs and the combined AC                                     #
# --------------------------------------------------------------------------- #


def _log(src: PriceSource, ticker: str, a: _dt.date, b: _dt.date) -> float:
    return math.log(src.close(ticker, b)) - math.log(src.close(ticker, a))


def pre_return(src: PriceSource, ticker: str, event: Event) -> float:
    """r_pre = ln P(GRID[i-1]) - ln P(GRID[i-6])."""
    return _log(src, ticker, event.pre_open, event.pre_close)


def post_return(src: PriceSource, ticker: str, event: Event) -> float:
    """r_post = ln P(GRID[i+5]) - ln P(GRID[i])."""
    return _log(src, ticker, event.post_open, event.post_close)


def ac_gross_bps(src: PriceSource, ticker: str, event: Event) -> float:
    """AC_GROSS = 1e4 * (r_post - r_pre)."""
    return 1e4 * (post_return(src, ticker, event) - pre_return(src, ticker, event))


def ac_net_bps(src: PriceSource, ticker: str, event: Event) -> float:
    """AC_NET = AC_GROSS - COST_BPS, with COST_BPS charged exactly once per event."""
    return ac_gross_bps(src, ticker, event) - K.COST_BPS


def ac_simple_bps(src: PriceSource, ticker: str, event: Event) -> float:
    """DESCRIPTIVE ONLY (§D.1), PROMOTION_POWER = NONE. Never adjudicable."""
    p = src.close
    r_pre = p(ticker, event.pre_close) / p(ticker, event.pre_open) - 1.0
    r_post = p(ticker, event.post_close) / p(ticker, event.post_open) - 1.0
    return 1e4 * (r_post - r_pre)


def auction_day_bar_bps(src: PriceSource, ticker: str, event: Event,
                        grid: Sequence[_dt.date]) -> float:
    """DESCRIPTIVE ONLY. The excluded bar's own return; enters no window."""
    a, b = event.auction_day_bar(grid)
    return 1e4 * _log(src, ticker, a, b)


# --------------------------------------------------------------------------- #
# F — cost accounting                                                          #
# --------------------------------------------------------------------------- #


def event_cost_bps(event: Event) -> float:
    """4 one-way units x 2 bps = 8.0 bps, derived from the path, not hard-coded."""
    return one_way_units(event) * K.ONE_WAY_BPS


# --------------------------------------------------------------------------- #
# Per-event series                                                             #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class EventResult:
    t0: _dt.date
    year: int
    calendar_month: str
    r_pre_bps: float
    r_post_bps: float
    ac_gross_bps: float
    ac_net_bps: float
    ac_simple_bps: float
    reopening: str


def event_results(src: PriceSource, ticker: str,
                  events: Sequence[Event]) -> List[EventResult]:
    out = []
    for e in events:
        g = ac_gross_bps(src, ticker, e)
        out.append(EventResult(
            t0=e.t0, year=e.year, calendar_month=e.calendar_month,
            r_pre_bps=1e4 * pre_return(src, ticker, e),
            r_post_bps=1e4 * post_return(src, ticker, e),
            ac_gross_bps=g, ac_net_bps=g - event_cost_bps(e),
            ac_simple_bps=ac_simple_bps(src, ticker, e), reopening=e.reopening))
    return out


# --------------------------------------------------------------------------- #
# G — the calendarised monthly P&L                                             #
# --------------------------------------------------------------------------- #


def monthly_series(results: Sequence[EventResult],
                   grid: Sequence[str] | None = None) -> List[float]:
    """§F.1. One entry per calendar month of the grid, zero months RETAINED.

    A month's value is the SUM of every valid primary event's AC_NET in that month.
    On the sealed calendar no month holds two events, but the sum is implemented so
    no builder has to decide, and `assert_max_one_event_per_month` checks the sealed
    property against the data rather than assuming it.
    """
    grid = list(grid if grid is not None else month_grid())
    by_month: Dict[str, float] = {m: 0.0 for m in grid}
    for r in results:
        if r.calendar_month not in by_month:
            raise KeyError(f"event month {r.calendar_month} is outside the sealed grid")
        by_month[r.calendar_month] += r.ac_net_bps
    return [by_month[m] for m in grid]


def assert_max_one_event_per_month(results: Sequence[EventResult]) -> None:
    from collections import Counter
    counts = Counter(r.calendar_month for r in results)
    worst = max(counts.values()) if counts else 0
    if worst > 1:
        offenders = {m: c for m, c in counts.items() if c > 1}
        raise AssertionError(
            f"sealed calendar asserts at most one primary event per calendar month; "
            f"found {offenders}")


# --------------------------------------------------------------------------- #
# H / I — the two primary statistics                                           #
# --------------------------------------------------------------------------- #


def mean_net_ac(results: Sequence[EventResult]) -> float:
    if not results:
        return float("nan")
    return sum(r.ac_net_bps for r in results) / len(results)


def mean_gross_ac(results: Sequence[EventResult]) -> float:
    if not results:
        return float("nan")
    return sum(r.ac_gross_bps for r in results) / len(results)


def calendarised_sharpe(monthly: Sequence[float]) -> float:
    """§F.2. mean / sd(ddof=1) * sqrt(12), risk-free 0. NaN if sd == 0 or n < 2.

    No leverage, no volatility targeting, no capital scaling, no weight search, and
    no annualisation based on events per year: the multiplier is sqrt(12) because the
    series is monthly, whatever the event frequency happens to be.
    """
    n = len(monthly)
    if n < 2:
        return float("nan")
    mean = sum(monthly) / n
    var = sum((x - mean) ** 2 for x in monthly) / (n - K.SHARPE_DDOF)
    if var <= 0.0:
        return float("nan")
    return (mean - K.RISK_FREE) / math.sqrt(var) * math.sqrt(K.SHARPE_PERIODS_PER_YEAR)
