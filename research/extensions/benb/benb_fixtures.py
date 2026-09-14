"""CTA-EDGE-02-BENB — synthetic fixture construction.

SYNTHETIC ONLY. Nothing here reads a file, a network endpoint or the historical panel.

The construction is exact rather than approximate, which is what makes the behavioural
tests discriminating. Because the sealed identity is

    delta_b = R_OVERNIGHT + R_TRADABLE - R_NAV

a fixture can pin any three of those four and the fourth follows:

    R_OVERNIGHT = delta_b - R_TRADABLE + R_NAV

So a "world" is specified by two coefficients — how `R_TRADABLE` and `R_NAV` respond to
the discount severity `d` — and the overnight leg is then forced. Each of the three
mandatory economic worlds is one line of parameters:

    WORLD 1  stale NAV            tr_coef = 0    nav_coef = -1   =>  R_ON = 0
    WORLD 2  overnight discovery  tr_coef = 0    nav_coef =  0   =>  R_ON = +d
    WORLD 3  tradable convergence tr_coef = +1   nav_coef =  0   =>  R_ON = 0
    MIXED                         tr_coef = 0    nav_coef = -0.5 =>  R_ON = +0.5 d

The burn-in holds 250 days at `b = 0`, and every non-signal day also sits at `b = 0`, so
the expanding median stays exactly 0 and `x_t = b_t = -d` with no approximation. That is
what lets a test assert an expected coefficient rather than a vague sign.
"""

from __future__ import annotations

import datetime as _dt
import math
from typing import Dict, List, Optional, Sequence, Set, Tuple

from benb_data import CellData, SyntheticCellSource

BURN_IN = 250


def business_days(start: _dt.date, n: int, holidays: Sequence[_dt.date] = ()) -> List[_dt.date]:
    out, d, hol = [], start, set(holidays)
    while len(out) < n:
        if d.weekday() < 5 and d not in hol:
            out.append(d)
        d += _dt.timedelta(days=1)
    return out


def _lcg(seed: int):
    """A tiny deterministic generator, so fixtures are reproducible without numpy."""
    state = seed & 0xFFFFFFFF
    while True:
        state = (1103515245 * state + 12345) & 0x7FFFFFFF
        yield state / 0x7FFFFFFF - 0.5          # uniform in [-0.5, 0.5)


def build_world(*, tr_coef: float, nav_coef: float,
                n_signals: int = 60, start: _dt.date = _dt.date(2010, 1, 4),
                severities: Optional[Sequence[float]] = None,
                noise: float = 0.0, seed: int = 7,
                ex_dates: Sequence[_dt.date] = (),
                px_ex_dates: Optional[Sequence[_dt.date]] = None,
                holidays: Sequence[_dt.date] = (),
                ticker: str = "HYG",
                spacer_days: int = 1,
                first_signal_index: Optional[int] = None) -> CellData:
    """One synthetic cell in a named economic world.

    Layout: `first_signal_index` burn-in days at `b = 0` (>= 250), then repeating
    blocks of [signal day t] [entry day t+1] [spacer days at b = 0].

    `first_signal_index` exists so a test can place a signal on an EXACT grid index -
    the last business day of a December, say - instead of hoping the block pattern
    happens to land there. A calendar-boundary test must be deterministic.
    """
    rnd = _lcg(seed)
    per_block = 2 + spacer_days
    start_idx = BURN_IN if first_signal_index is None else int(first_signal_index)
    if start_idx < BURN_IN:
        raise ValueError(f"first_signal_index must be >= {BURN_IN}")
    grid = business_days(start, start_idx + n_signals * per_block + 4, holidays)

    p_open: Dict[_dt.date, float] = {}
    p_close: Dict[_dt.date, float] = {}
    nav: Dict[_dt.date, float] = {}

    nav_level = 100.0
    for d in grid[:start_idx]:
        nav[d] = nav_level
        p_close[d] = nav_level                       # b = 0
        p_open[d] = nav_level

    sev = list(severities) if severities is not None else [
        0.002 + 0.0004 * (i % 25) for i in range(n_signals)]
    if len(sev) < n_signals:
        sev = (sev * (n_signals // len(sev) + 1))[:n_signals]

    i = start_idx
    for k in range(n_signals):
        if i + 1 >= len(grid):
            break
        d = sev[k]
        t = grid[i]
        t1 = grid[i + 1]

        # signal day t: b_t = -d  (NAV unchanged, price marked to a discount)
        nav[t] = nav_level
        p_close[t] = nav_level * math.exp(-d)
        p_open[t] = p_close[t]

        # entry day t+1
        eps = noise * next(rnd) if noise else 0.0
        r_nav = nav_coef * d + eps
        r_tr = tr_coef * d + (noise * next(rnd) if noise else 0.0)
        delta_b = 0.0 - (-d)                          # b_{t+1} = 0 by construction
        r_on = delta_b - r_tr + r_nav                 # forced by the sealed identity

        nav_level = nav_level * math.exp(r_nav)
        nav[t1] = nav_level
        p_close[t1] = nav_level                       # b_{t+1} = 0
        p_open[t1] = p_close[t] * math.exp(r_on)

        i += 2
        for _ in range(spacer_days):
            if i >= len(grid):
                break
            s = grid[i]
            nav[s] = nav_level
            p_close[s] = nav_level
            p_open[s] = nav_level
            i += 1

    for d in grid[i:]:                                # tail padding at b = 0
        nav[d] = nav_level
        p_close[d] = nav_level
        p_open[d] = nav_level

    grid = [d for d in grid if d in nav]
    union_ex = set(ex_dates) | set(px_ex_dates or ())
    cell = CellData(ticker=ticker, grid=grid, p_open=p_open, p_close=p_close,
                    nav=nav, ex_dates=union_ex)
    cell.validate()
    return cell


def source(*cells: CellData) -> SyntheticCellSource:
    return SyntheticCellSource({c.ticker: c for c in cells})


WORLDS = {
    "STALE_NAV":            dict(tr_coef=0.0, nav_coef=-1.0),
    "OVERNIGHT_DISCOVERY":  dict(tr_coef=0.0, nav_coef=0.0),
    "TRADABLE_CONVERGENCE": dict(tr_coef=1.0, nav_coef=0.0),
    "MIXED":                dict(tr_coef=0.0, nav_coef=-0.5),
    "NO_CONVERGENCE":       dict(tr_coef=0.0, nav_coef=0.0),   # with delta_b forced to 0
}
