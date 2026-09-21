"""CTA-EDGE-02-BENB — decomposition, Gate-1 regressions, the fixed trade, monthly P&L.

Components H, I, J and K of the S2 build. Every formula is transcribed from the sealed
§E of `BENB_PREREGISTRATION.md`.
"""

from __future__ import annotations

import datetime as _dt
import math
from dataclasses import dataclass
from typing import Dict, List, Mapping, Optional, Sequence

import benb_contract as K
from benb_data import CellData
from benb_feature import FeatureRow

FLAT = 0
LONG = +1


# --------------------------------------------------------------------------- #
# H — the exact three-component decomposition                                  #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class Decomposition:
    date: _dt.date
    next_date: _dt.date
    r_overnight: float          # ln(P_open,t+1 / P_close,t)   -- before lawful entry
    r_tradable: float           # ln(P_close,t+1 / P_open,t+1) -- the only harvestable leg
    r_nav: float                # ln(NAV_t+1 / NAV_t)          -- catch-up / catch-down
    delta_b: float              # b_{t+1} - b_t

    @property
    def identity_residual(self) -> float:
        """delta_b - (R_ON + R_TR - R_NAV). Exactly zero up to floating point."""
        return self.delta_b - (self.r_overnight + self.r_tradable - self.r_nav)


def decompose(cell: CellData, day: _dt.date, next_day: _dt.date) -> Decomposition:
    ln = math.log
    r_on = ln(cell.p_open[next_day]) - ln(cell.p_close[day])
    r_tr = ln(cell.p_close[next_day]) - ln(cell.p_open[next_day])
    r_nav = ln(cell.nav[next_day]) - ln(cell.nav[day])
    b_t = ln(cell.p_close[day]) - ln(cell.nav[day])
    b_t1 = ln(cell.p_close[next_day]) - ln(cell.nav[next_day])
    return Decomposition(day, next_day, r_on, r_tr, r_nav, b_t1 - b_t)


def assert_identity(d: Decomposition, tol: float = 1e-12) -> None:
    if abs(d.identity_residual) > tol:
        raise AssertionError(
            f"decomposition identity violated on {d.date}: "
            f"residual {d.identity_residual:.3e} > {tol:.0e}")


# --------------------------------------------------------------------------- #
# Observation tuples — frozen once, causally                                   #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class Observation:
    """The frozen tuple the bootstrap resamples. Built ONCE on the true chronology."""
    date: _dt.date
    year: int
    entry_month: str            # the ENTRY calendar month, i.e. month of t+1
    d: float                    # discount severity, > 0
    r_overnight_bps: float
    r_tradable_bps: float
    r_nav_bps: float

    @property
    def net_trade_return_bps(self) -> float:
        """§E.4: NET = R_TRADABLE - ROUND_TRIP_COST, charged once per signal."""
        return self.r_tradable_bps - K.ROUND_TRIP_COST_BPS


def observations(cell: CellData, rows: Sequence[FeatureRow],
                 eligible_discounts: Sequence[FeatureRow],
                 check_identity: bool = True) -> List[Observation]:
    idx = {d: i for i, d in enumerate(cell.grid)}
    out: List[Observation] = []
    for r in eligible_discounts:
        nxt = cell.grid[idx[r.date] + 1]
        dec = decompose(cell, r.date, nxt)
        if check_identity:
            assert_identity(dec)
        out.append(Observation(
            date=r.date, year=r.date.year,
            entry_month=f"{nxt.year:04d}-{nxt.month:02d}",
            d=r.severity,
            r_overnight_bps=1e4 * dec.r_overnight,
            r_tradable_bps=1e4 * dec.r_tradable,
            r_nav_bps=1e4 * dec.r_nav))
    return out


# --------------------------------------------------------------------------- #
# I — the Gate-1 regressions. ONE transparent implementation.                   #
# --------------------------------------------------------------------------- #


def ols_slope_intercept(x: Sequence[float], y: Sequence[float]):
    """Simple OLS of y on [1, x]. Returns (intercept, slope).

    Written out longhand rather than delegated, so the estimator is inspectable and
    there is exactly one of it. Raises when the regressor has no variance, which the
    §J.2 evaluability rule turns into CLASS F rather than a silent NaN.
    """
    n = len(x)
    if n < 2:
        raise ValueError("OLS needs at least two observations")
    mx = sum(x) / n
    my = sum(y) / n
    sxx = sum((xi - mx) ** 2 for xi in x)
    if sxx <= 0.0:
        raise ValueError("regressor has zero variance")
    sxy = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
    slope = sxy / sxx
    return my - slope * mx, slope


@dataclass(frozen=True)
class GateOne:
    beta_T: float
    beta_O: float
    beta_N: float
    a_T: float
    a_O: float
    a_N: float
    n: int


def gate_one(obs: Sequence[Observation]) -> GateOne:
    """§E.2 and §E.3, on the discount-only sample, one regressor, three separate fits."""
    d = [o.d for o in obs]
    a_T, b_T = ols_slope_intercept(d, [o.r_tradable_bps for o in obs])
    a_O, b_O = ols_slope_intercept(d, [o.r_overnight_bps for o in obs])
    a_N, b_N = ols_slope_intercept(d, [o.r_nav_bps for o in obs])
    return GateOne(beta_T=b_T, beta_O=b_O, beta_N=b_N,
                   a_T=a_T, a_O=a_O, a_N=a_N, n=len(obs))


# --------------------------------------------------------------------------- #
# J — the fixed-unit trade                                                     #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class Leg:
    when: str
    from_position: int
    to_position: int


def position_path(o: Observation) -> List[Leg]:
    """§E.4, written out. No sizing by d_t, no leverage, no premium-side short.

    evening t : signal known            open(t+1) : flat -> LONG 1 unit
    close(t+1): LONG -> flat            otherwise : NO POSITION
    """
    return [Leg("open(t+1)", FLAT, LONG), Leg("close(t+1)", LONG, FLAT)]


def carries_overnight_exposure(o: Observation) -> bool:
    """The position is never open across close(t) -> open(t+1). Proven, not asserted."""
    return any(l.from_position != FLAT for l in position_path(o) if l.when == "open(t+1)")


def net_trade_returns_bps(obs: Sequence[Observation]) -> List[float]:
    return [o.net_trade_return_bps for o in obs]


# --------------------------------------------------------------------------- #
# K — the calendarised monthly P&L                                             #
# --------------------------------------------------------------------------- #


def month_grid(first: str, last: str) -> List[str]:
    y, m = int(first[:4]), int(first[5:7])
    y1, m1 = int(last[:4]), int(last[5:7])
    out = []
    while (y, m) <= (y1, m1):
        out.append(f"{y:04d}-{m:02d}")
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


def monthly_series(obs: Sequence[Observation],
                   grid: Optional[Sequence[str]] = None) -> List[float]:
    """§H.2. Trades are assigned to their ENTRY month. Zero months are RETAINED.

    The series is never compressed to active months: a month with no eligible trade
    enters as exactly 0.0, which is what charges the sleeve for idle calendar time.
    """
    if grid is None:
        if not obs:
            return []
        months = sorted(o.entry_month for o in obs)
        grid = month_grid(months[0], months[-1])
    by_month: Dict[str, float] = {m: 0.0 for m in grid}
    for o in obs:
        if o.entry_month not in by_month:
            raise KeyError(f"entry month {o.entry_month} is outside the sealed grid")
        by_month[o.entry_month] += o.net_trade_return_bps
    return [by_month[m] for m in grid]


def calendarised_sharpe(monthly: Sequence[float]) -> float:
    """§H.2: mean / sd(ddof=1) * sqrt(12), rf = 0. NaN if sd == 0 or n < 2."""
    n = len(monthly)
    if n < 2:
        return float("nan")
    mean = sum(monthly) / n
    var = sum((v - mean) ** 2 for v in monthly) / (n - K.SHARPE_DDOF)
    if var <= 0.0:
        return float("nan")
    return ((mean - K.RISK_FREE) / math.sqrt(var)
            * math.sqrt(K.SHARPE_PERIODS_PER_YEAR))


def mean_net_trade_return_bps(obs: Sequence[Observation]) -> float:
    if not obs:
        return float("nan")
    return sum(o.net_trade_return_bps for o in obs) / len(obs)
