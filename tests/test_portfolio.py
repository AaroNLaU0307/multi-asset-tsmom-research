"""Tests for the portfolio aggregation + risk-control layer.

Priorities:
  1. Correctness of equal-weight aggregation, the vol-target leverage, and the
     gross-leverage cap.
  2. NO LOOK-AHEAD — truncation invariance of portfolio weights & leverage, and a
     backward-only realized portfolio vol.

Run:  python -m pytest -q
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import portfolio, signals  # noqa: E402


def _synthetic_daily(seed: int = 7, years: int = 7, cols=("A", "B", "C")) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2004-01-01", periods=years * 252)
    out = {}
    for c in cols:
        steps = rng.normal(0.0003, 0.01, size=len(idx))
        out[c] = 100.0 * np.exp(np.cumsum(steps))
    return pd.DataFrame(out, index=idx)


def _monthly(values: dict[str, list[float]]) -> pd.DataFrame:
    n = len(next(iter(values.values())))
    idx = pd.date_range("2010-01-31", periods=n, freq="ME")
    return pd.DataFrame(values, index=idx)


# --------------------------------------------------------------------------- #
# 1. Equal-weight aggregation
# --------------------------------------------------------------------------- #
def test_equal_weight_aggregate_and_nan_handling():
    w = _monthly({"A": [1.0, 0.5], "B": [-0.5, 0.5], "C": [np.nan, 1.0]})
    base, avail = portfolio.equal_weight_aggregate(w)

    assert avail.iloc[0] == 2 and avail.iloc[1] == 3
    # month 0: NaN asset excluded, divide by 2
    assert base["A"].iloc[0] == 0.5
    assert base["B"].iloc[0] == -0.25
    assert base["C"].iloc[0] == 0.0
    # month 1: divide by 3
    assert np.isclose(base["A"].iloc[1], 0.5 / 3)
    assert np.isclose(base["C"].iloc[1], 1.0 / 3)


# --------------------------------------------------------------------------- #
# 2. Leverage: vol target + gross cap + warm-up
# --------------------------------------------------------------------------- #
def test_leverage_cap_and_delevering():
    port_vol = pd.Series([0.02, 0.20, 0.05, np.nan])
    gross_base = pd.Series([1.0, 1.0, 0.5, 1.0])
    L, l_raw, cap = portfolio.leverage(port_vol, gross_base, target_vol=0.10, max_gross=3.0)

    assert np.isclose(l_raw.iloc[0], 5.0) and L.iloc[0] == 3.0 and cap.iloc[0]   # capped
    assert np.isclose(L.iloc[1], 0.5) and not cap.iloc[1]                        # de-levered
    assert np.isclose(L.iloc[2], 2.0) and not cap.iloc[2]                        # below cap
    assert np.isnan(L.iloc[3]) and not cap.iloc[3]                               # warm-up -> NaN


def test_gross_never_exceeds_cap():
    daily = _synthetic_daily()
    out = portfolio.build_portfolio(daily, method="B", max_gross=3.0)
    gross = out["gross"].dropna()
    assert (gross <= 3.0 + 1e-9).all()


# --------------------------------------------------------------------------- #
# 3. NO LOOK-AHEAD
# --------------------------------------------------------------------------- #
def test_portfolio_truncation_invariance():
    daily = _synthetic_daily()
    full = portfolio.build_portfolio(daily, method="B")
    cut = full["port_weight"].index[50]
    trunc = portfolio.build_portfolio(daily.loc[:cut], method="B")

    pw_full, pw_tr = full["port_weight"], trunc["port_weight"]
    pd.testing.assert_frame_equal(pw_full.loc[pw_tr.index], pw_tr)
    lev_full, lev_tr = full["leverage"], trunc["leverage"]
    pd.testing.assert_series_equal(lev_full.loc[lev_tr.index], lev_tr)


def test_realized_vol_uses_only_past_returns():
    daily = _synthetic_daily()
    base, _ = portfolio.equal_weight_aggregate(
        __import_sizing_weights(daily)
    )
    rp = portfolio.base_portfolio_daily_returns(base, daily)
    # The held weight on day d is the prior month-end's weight (shift(1)); so the
    # base return on a month-end day cannot use that day's freshly-decided weight.
    # Truncating daily data at day d leaves rp[:d] unchanged.
    cut = rp.dropna().index[400]
    rp_trunc = portfolio.base_portfolio_daily_returns(base.loc[:cut], daily.loc[:cut])
    common = rp_trunc.dropna().index
    pd.testing.assert_series_equal(rp.loc[common], rp_trunc.loc[common])


def __import_sizing_weights(daily):
    from src import sizing
    return sizing.build_position_sizes(daily, method="B")["weight"]


def test_position_is_portfolio_weight_shifted():
    daily = _synthetic_daily()
    out = portfolio.build_portfolio(daily, method="B")
    pd.testing.assert_frame_equal(out["position"], out["port_weight"].shift(1))


# --------------------------------------------------------------------------- #
# No-trade band
# --------------------------------------------------------------------------- #
def test_band_zero_reproduces_target():
    tgt = _monthly({"A": [0.0, 0.5, 0.52, -0.4], "B": [0.0, 0.3, 0.31, 0.30]})
    exec_w = portfolio.apply_no_trade_band(tgt, band=0.0)
    pd.testing.assert_frame_equal(exec_w, tgt)


def test_band_suppresses_small_moves_only():
    # A drifts in small steps (<0.05) then jumps; B always tiny moves.
    tgt = _monthly({"A": [0.50, 0.53, 0.40, 0.42], "B": [0.20, 0.22, 0.23, 0.24]})
    exec_w = portfolio.apply_no_trade_band(tgt, band=0.05)
    # month0 executes target
    assert exec_w["A"].iloc[0] == 0.50 and exec_w["B"].iloc[0] == 0.20
    # month1: A move 0.03 (<0.05) -> keep 0.50 ; B move 0.02 -> keep 0.20
    assert exec_w["A"].iloc[1] == 0.50 and exec_w["B"].iloc[1] == 0.20
    # month2: A move from 0.50 to 0.40 = 0.10 (>=0.05) -> trade to 0.40
    assert exec_w["A"].iloc[2] == 0.40
    # B never moves >= 0.05 from 0.20 -> stays 0.20 throughout
    assert (exec_w["B"] == 0.20).all()


def test_band_reduces_turnover():
    daily = _synthetic_daily()
    out = portfolio.build_portfolio(daily, method="B")
    tgt = out["port_weight"]
    banded = portfolio.apply_no_trade_band(tgt, band=0.05)
    to_tgt = tgt.diff().abs().sum(axis=1).sum()
    to_band = banded.diff().abs().sum(axis=1).sum()
    assert to_band < to_tgt


def test_band_truncation_invariance():
    daily = _synthetic_daily()
    tgt = portfolio.build_portfolio(daily, method="B")["port_weight"]
    full = portfolio.apply_no_trade_band(tgt, band=0.05)
    cut = full.dropna(how="all").index[40]
    trunc = portfolio.apply_no_trade_band(tgt.loc[:cut], band=0.05)
    pd.testing.assert_frame_equal(full.loc[trunc.index], trunc)


# --------------------------------------------------------------------------- #
# Control aggregations: inverse-vol & risk parity
# --------------------------------------------------------------------------- #
def test_inverse_vol_aggregate():
    sig = _monthly({"A": [1.0], "B": [1.0]})
    vol = _monthly({"A": [0.05], "B": [0.20]})
    base, avail = portfolio.inverse_vol_aggregate(sig, vol)
    # weight ∝ 1/vol -> [20, 5] -> normalized [0.8, 0.2]
    assert np.isclose(base["A"].iloc[0], 0.8)
    assert np.isclose(base["B"].iloc[0], 0.2)
    assert np.isclose(base.abs().sum(axis=1).iloc[0], 1.0)


def test_erc_weights_equal_risk_contribution():
    # diagonal cov (uncorrelated): ERC -> w ∝ 1/vol
    cov = np.diag([0.04, 0.01])                 # vols 0.20, 0.10
    w = portfolio._erc_weights(cov)
    assert np.isclose(w.sum(), 1.0)
    assert np.isclose(w[0] / w[1], 0.5, atol=1e-3)   # 1/0.2 : 1/0.1 = 1:2
    rc = w * (cov @ w)                            # risk contributions
    assert np.isclose(rc[0], rc[1], atol=1e-8)   # equal


def test_risk_parity_truncation_invariance():
    daily = _synthetic_daily(years=7)
    sig = signals.monthly_signals(daily, method="B")
    full, _ = portfolio.risk_parity_aggregate(sig, daily, cov_window=120)
    cut = full.dropna(how="all").index[30]
    sig_t = signals.monthly_signals(daily.loc[:cut], method="B")
    trunc, _ = portfolio.risk_parity_aggregate(sig_t, daily.loc[:cut], cov_window=120)
    common = trunc.dropna(how="all").index
    pd.testing.assert_frame_equal(full.loc[common], trunc.loc[common])


def test_build_portfolio_agg_dispatch_caps_gross():
    daily = _synthetic_daily(years=7)
    for agg in ("inverse_vol", "risk_parity"):
        out = portfolio.build_portfolio(daily, method="B", agg=agg, cov_window=120, max_gross=3.0)
        gross = out["gross"].dropna()
        assert (gross <= 3.0 + 1e-9).all()
        assert len(gross) > 0
