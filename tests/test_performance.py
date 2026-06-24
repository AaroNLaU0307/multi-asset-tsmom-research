"""Tests for the return-calculation / performance layer.

Priorities:
  1. NO LOOK-AHEAD in the realized return stream (positions are shift(1)'d, and
     truncating the price history does not change past returns).
  2. Correctness of the return aggregation, costs, and the core metrics.

Run:  python -m pytest -q
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import performance as perf  # noqa: E402
from src import portfolio, signals  # noqa: E402


def _synthetic_daily(seed: int = 7, years: int = 7, cols=("A", "B", "C")) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2004-01-01", periods=years * 252)
    out = {}
    for c in cols:
        steps = rng.normal(0.0004, 0.01, size=len(idx))
        out[c] = 100.0 * np.exp(np.cumsum(steps))
    return pd.DataFrame(out, index=idx)


def _monthly(values: dict[str, list[float]]) -> pd.DataFrame:
    n = len(next(iter(values.values())))
    idx = pd.date_range("2010-01-31", periods=n, freq="ME")
    return pd.DataFrame(values, index=idx)


# --------------------------------------------------------------------------- #
# 1. Return aggregation + cost correctness
# --------------------------------------------------------------------------- #
def test_portfolio_return_and_cost():
    prices = _monthly({"A": [100, 110, 121], "B": [100, 90, 99]})
    positions = _monthly({"A": [0.0, 1.0, 0.5], "B": [0.0, -1.0, 0.5]})
    out = perf.portfolio_returns(positions, prices, cost_bps=10.0)
    # month0 has NaN gross (no prior price) and is dropped, so row 0 == month1.
    assert list(out.index) == list(prices.index[1:])

    # month1: A +10% (pos 1), B -10% (pos -1) -> 0.10 + 0.10 = 0.20
    assert np.isclose(out["gross"].iloc[0], 0.20)
    # month2: A +10% (0.5), B +10% (0.5) -> 0.10
    assert np.isclose(out["gross"].iloc[1], 0.10)
    # turnover month1 = |1-0|+|-1-0| = 2.0 ; cost = 2.0 * 10bps = 0.002
    assert np.isclose(out["turnover"].iloc[0], 2.0)
    assert np.isclose(out["net"].iloc[0], 0.20 - 0.002)


def test_buy_and_hold_is_cross_sectional_mean():
    prices = _monthly({"A": [100, 110], "B": [100, 120]})
    bh = perf.buy_and_hold_returns(prices)
    assert np.isclose(bh.iloc[-1], np.mean([0.10, 0.20]))


# --------------------------------------------------------------------------- #
# 2. Metric correctness
# --------------------------------------------------------------------------- #
def test_max_drawdown():
    r = pd.Series([0.10, -0.50, 0.10])      # 1.1 -> 0.55 -> 0.605 ; trough 0.55/1.1-1
    assert np.isclose(perf.max_drawdown(r), -0.5)


def test_annual_return_compounding():
    r = pd.Series([0.01] * 12)
    assert np.isclose(perf.annual_return(r), 1.01 ** 12 - 1)


def test_sharpe_sign_and_zero_vol():
    assert perf.sharpe_ratio(pd.Series([0.01, 0.02, 0.015, 0.012])) > 0
    assert np.isnan(perf.sharpe_ratio(pd.Series([0.01, 0.01, 0.01])))  # zero vol


# --------------------------------------------------------------------------- #
# 3. NO LOOK-AHEAD — truncation invariance of the realized return stream
# --------------------------------------------------------------------------- #
def test_returns_truncation_invariance():
    daily = _synthetic_daily()
    port = portfolio.build_portfolio(daily, method="B")
    mpx = signals.to_monthly(daily)
    full = perf.portfolio_returns(port["position"], mpx)

    cut = full.index[45]
    port_t = portfolio.build_portfolio(daily.loc[:cut], method="B")
    mpx_t = signals.to_monthly(daily.loc[:cut])
    trunc = perf.portfolio_returns(port_t["position"], mpx_t)

    common = trunc.index.intersection(full.index)
    pd.testing.assert_frame_equal(
        full.loc[common, ["gross", "net"]], trunc.loc[common, ["gross", "net"]]
    )
