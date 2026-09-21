"""CTA-EDGE-01-TA — the INDEPENDENT synthetic oracle.

This module deliberately imports **nothing** from the production engine: not
`ta_engine`, not `ta_inference`, not `ta_classify`, not `ta_contract`. It reconstructs
the expected value of every fixture from the fixture's own definition, using direct
transparent arithmetic and its own copies of the sealed constants.

Why it exists
-------------
Twice in this programme a producer-written oracle reproduced the producer's own
misreading and agreed with the wrong engine:

* the VRP variation-margin sign — the closed-form oracle was written in the same
  sitting from the same text and made the same mistake;
* `VRP-DIAG-DEFECT-001` — the fixture made the defect structurally unreachable.

So this oracle takes a different route to the same number. A fixture is DEFINED by its
per-day log returns; the production engine recovers `AC` from the LOG OF ENDPOINT
PRICES, while the oracle SUMS THE DECLARED DAILY RETURNS. An engine that mis-indexes a
window endpoint disagrees with the oracle immediately, because the oracle never touches
the price series at all.

The constants below are transcribed independently from the sealed contract. If they
ever disagree with `ta_contract`, `ta_tests.test_oracle_constants_agree` fails — which
is the point: a silent constant drift must break a test, not a run.
"""

from __future__ import annotations

import datetime as _dt
import math
from typing import Dict, List, Mapping, Sequence

# Independently transcribed from TA_PREREGISTRATION.md §B.4, §E.2, §E.3, §F.2.
ORACLE_PRE_OPEN = -6
ORACLE_PRE_CLOSE = -1
ORACLE_POST_OPEN = 0
ORACLE_POST_CLOSE = 5
ORACLE_COST_BPS = 4 * 2.0
ORACLE_M1_NET = 8.0
ORACLE_M2 = 0.30
ORACLE_MONTHS_PER_YEAR = 12


def oracle_ac_gross_bps(daily_logs: Mapping[_dt.date, float],
                        grid: Sequence[_dt.date], t0: _dt.date) -> float:
    """AC_GROSS by SUMMING the fixture's declared daily log returns.

    `daily_logs[d]` is the log return earned from the previous grid day's close to
    `d`'s close. The PRE window earns days GRID[i-5..i-1]; the POST window earns days
    GRID[i+1..i+5]; the auction-day bar GRID[i] is earned by NEITHER.
    """
    i = grid.index(t0)
    pre_days = grid[i + ORACLE_PRE_OPEN + 1: i + ORACLE_PRE_CLOSE + 1]
    post_days = grid[i + ORACLE_POST_OPEN + 1: i + ORACLE_POST_CLOSE + 1]
    if len(pre_days) != 5 or len(post_days) != 5:
        raise AssertionError("oracle: window is not 5 + 5 return-bearing days")
    r_pre = sum(daily_logs[d] for d in pre_days)
    r_post = sum(daily_logs[d] for d in post_days)
    return 1e4 * (r_post - r_pre)


def oracle_ac_net_bps(daily_logs, grid, t0) -> float:
    return oracle_ac_gross_bps(daily_logs, grid, t0) - ORACLE_COST_BPS


def oracle_auction_day_bar_bps(daily_logs: Mapping[_dt.date, float],
                               grid: Sequence[_dt.date], t0: _dt.date) -> float:
    """The excluded bar's own return — the day GRID[i] itself."""
    return 1e4 * daily_logs[grid[grid.index(t0)]]


def oracle_monthly_series(ac_net_by_t0: Mapping[_dt.date, float],
                          month_keys: Sequence[str]) -> List[float]:
    """Sum each month's AC_NET onto the month grid; months with no event stay 0.0."""
    out = []
    for key in month_keys:
        total = 0.0
        for t0, v in ac_net_by_t0.items():
            if f"{t0.year:04d}-{t0.month:02d}" == key:
                total += v
        out.append(total)
    return out


def oracle_mean(values: Sequence[float]) -> float:
    return sum(values) / len(values)


def oracle_sharpe(monthly: Sequence[float]) -> float:
    """mean / sample sd * sqrt(12), written out longhand."""
    n = len(monthly)
    if n < 2:
        return float("nan")
    mean = sum(monthly) / n
    ss = sum((x - mean) ** 2 for x in monthly)
    sd = math.sqrt(ss / (n - 1))
    if sd == 0.0:
        return float("nan")
    return mean / sd * math.sqrt(ORACLE_MONTHS_PER_YEAR)


def oracle_classify(l_ac_gross: float, u_ac_gross: float, l_s: float, u_s: float,
                    loyo_ok: bool, spy: bool, macro: bool) -> str:
    """The sealed §I.2 order, re-derived here from the contract text independently."""
    l_net = l_ac_gross - ORACLE_COST_BPS
    u_net = u_ac_gross - ORACLE_COST_BPS
    if u_ac_gross <= 0.0:
        return "A"
    if u_net < ORACLE_M1_NET or u_s < ORACLE_M2:
        return "B"
    if l_net >= ORACLE_M1_NET and l_s >= ORACLE_M2:
        return "D" if (loyo_ok and not spy and not macro) else "I"
    return "C"


def oracle_prices_from_daily_logs(grid: Sequence[_dt.date],
                                  daily_logs: Mapping[_dt.date, float],
                                  p0: float = 100.0) -> Dict[_dt.date, float]:
    """Build the price series the ENGINE will see from the fixture's daily returns.

    This is the only place the two routes meet: the oracle defines returns, this turns
    them into prices, and the engine must recover the same returns from those prices.
    """
    out: Dict[_dt.date, float] = {}
    level = math.log(p0)
    for d in grid:
        level += daily_logs.get(d, 0.0)
        out[d] = math.exp(level)
    return out
