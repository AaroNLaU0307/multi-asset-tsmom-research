"""Step 5a — portfolio return calculation + core performance metrics.

Honest by construction: no parameter is touched here to flatter results. We
compute the realized monthly return of the step-4 portfolio and standard metrics.

No look-ahead
-------------
The position held during month M is the portfolio weight decided at month-end
M-1 (``positions = port_weight.shift(1)``). The month-M return multiplies that
position by the asset's month-M return (end of M-1 -> end of M). So the weight is
always older than the return it earns. Truncation invariance is unit-tested.

Costs
-----
A simple, disclosed turnover model: each month we trade |Δ position| of notional
and pay ``cost_bps`` one-way. Intra-month drift is ignored (turnover is measured
on target weights) — a minor, standard simplification, stated in the report. Both
gross and net are reported.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

import config


def monthly_asset_returns(monthly_prices: pd.DataFrame) -> pd.DataFrame:
    """Month-over-month simple returns of each asset (end M-1 -> end M)."""
    return monthly_prices.pct_change()


def portfolio_returns(
    positions: pd.DataFrame,
    monthly_prices: pd.DataFrame,
    cost_bps: float = config.TRANSACTION_COST_BPS,
) -> pd.DataFrame:
    """Realized monthly portfolio return stream.

    positions : weights HELD during each month (already shift(1) of the decision
                weights — must not be the same-month decision weights).
    Returns a frame with columns: gross, turnover, cost, net.
    """
    rets = monthly_asset_returns(monthly_prices).reindex_like(positions)
    gross = (positions * rets).sum(axis=1, min_count=1)

    # turnover entering each month = |position_M - position_{M-1}| summed (one-way).
    turnover = positions.diff().abs().sum(axis=1, min_count=1)
    cost = turnover * (cost_bps / 1e4)
    net = gross - cost

    out = pd.DataFrame({"gross": gross, "turnover": turnover, "cost": cost, "net": net})
    # keep only months with an actual position/return
    return out.dropna(subset=["gross"])


def equity_curve(returns: pd.Series) -> pd.Series:
    """Cumulative growth of $1 (compounded)."""
    return (1.0 + returns.fillna(0.0)).cumprod()


def drawdown_curve(returns: pd.Series) -> pd.Series:
    eq = equity_curve(returns)
    return eq / eq.cummax() - 1.0


def max_drawdown(returns: pd.Series) -> float:
    """Max peak-to-trough decline (returned as a negative number)."""
    return float(drawdown_curve(returns).min())


def metrics(returns: pd.Series, periods_per_year: int = 12) -> dict[str, float]:
    """Standard metrics. Sharpe uses arithmetic mean / vol with rf = 0 (disclosed);
    ann_return is geometric (CAGR)."""
    r = returns.dropna()
    n = len(r)
    if n == 0:
        return {k: float("nan") for k in
                ["n_months", "ann_return", "ann_vol", "sharpe", "max_drawdown", "calmar", "win_rate"]}
    mean, sd = r.mean(), r.std(ddof=1)
    ann_vol = sd * np.sqrt(periods_per_year)
    ann_ret = float((1.0 + r).prod() ** (periods_per_year / n) - 1.0)
    sharpe = float(mean / sd * np.sqrt(periods_per_year)) if sd > 0 else float("nan")
    mdd = max_drawdown(r)
    calmar = float(ann_ret / abs(mdd)) if mdd < 0 else float("nan")
    return {
        "n_months": n,
        "ann_return": ann_ret,
        "ann_vol": ann_vol,
        "sharpe": sharpe,
        "max_drawdown": mdd,
        "calmar": calmar,
        "win_rate": float((r > 0).mean()),
    }


def sharpe_ratio(returns: pd.Series, periods_per_year: int = 12) -> float:
    r = returns.dropna()
    sd = r.std(ddof=1)
    return float(r.mean() / sd * np.sqrt(periods_per_year)) if sd > 0 and len(r) > 1 else float("nan")


def annual_return(returns: pd.Series, periods_per_year: int = 12) -> float:
    r = returns.dropna()
    if len(r) == 0:
        return float("nan")
    return float((1.0 + r).prod() ** (periods_per_year / len(r)) - 1.0)


# --------------------------------------------------------------------------- #
# Buy-and-hold benchmark: equal-weight, long-only, monthly-rebalanced (1/N).
# --------------------------------------------------------------------------- #
def buy_and_hold_returns(monthly_prices: pd.DataFrame) -> pd.Series:
    """Equal-weight (1/N over available assets), long-only, no signal, no leverage.
    Monthly return = cross-sectional mean of the assets' monthly returns."""
    rets = monthly_asset_returns(monthly_prices)
    return rets.mean(axis=1, skipna=True).dropna()
