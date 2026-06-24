"""Step 4 — portfolio aggregation + portfolio-level volatility targeting.

SCOPE: combine the per-asset vol-scaled weights (step 3) into one portfolio and
apply a single portfolio-level risk control. NO covariance / risk-parity
optimization — deliberately:
  * a 17x17 covariance matrix is noisily estimated and ill-conditioned,
  * cross-asset correlations are unstable and spike toward 1 in crises,
  * mean-variance / risk-parity optimizers routinely lose to naive 1/N out of
    sample (DeMiguel-Garlappi-Uppal 2009).
Risk parity is left as an OPTIONAL later benchmark, not the baseline.

Also NO returns / Sharpe / drawdown / performance (step 5). We do build a
portfolio *return stream*, but ONLY to estimate its volatility for risk
targeting — not to evaluate performance.

Pipeline
--------
1. Equal-weight aggregate the 17 per-asset weights (each already vol-scaled to
   ~10% individual vol). Average over the assets that have a weight that month
   (NaN weight => not in the book), so the book scale is stable as assets come
   online: ``base_w_i = w_i / N_available``.
2. Portfolio vol target: scale the whole book by
       L = target_port_vol / realized_port_vol
   (dynamic de-levering — shrink when realized vol is high, grow when low).
3. Gross-leverage cap (safety valve): cap sum|weights| so very low realized vol
   cannot lever the book excessively.

No look-ahead
-------------
``realized_port_vol`` at month-end M is a backward-looking rolling std of the
*base* (unlevered) portfolio's daily returns up to M; the daily held weight on
day d is the previous month-end's decision (``.shift(1)``), so day d's return is
never earned with a weight set using day d's close. Using the unlevered base
portfolio avoids any circularity with the leverage it feeds. Truncation
invariance is unit-tested.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

import config
from . import sizing


# --------------------------------------------------------------------------- #
# 1. Equal-weight aggregation
# --------------------------------------------------------------------------- #
def equal_weight_aggregate(asset_weights: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Per-asset contribution = weight / (# assets with a weight that month).

    NaN weights (no signal / insufficient history) are treated as 'not in the
    book' (0 contribution) and excluded from the count, so early months with
    fewer live assets are not artificially shrunk.
    Returns (base_weights, n_available).
    """
    avail = asset_weights.notna().sum(axis=1)
    base = asset_weights.fillna(0.0).div(avail.where(avail > 0), axis=0)
    return base, avail


# --------------------------------------------------------------------------- #
# Alternative aggregations — CONTROL experiments only (the main strategy uses
# equal_weight_aggregate). All produce signed pre-leverage base weights with
# sum|weight| = 1 over available assets; the same portfolio vol target + cap then
# apply, so only the cross-asset RISK ALLOCATION differs.
# --------------------------------------------------------------------------- #
def inverse_vol_aggregate(
    signal_monthly: pd.DataFrame, vol_monthly: pd.DataFrame
) -> tuple[pd.DataFrame, pd.Series]:
    """Inverse-volatility ("simple risk parity"): weight_i ∝ signal_i / vol_i.

    Each asset gets equal *standalone* risk (ignores correlations). Uses the same
    backward-looking vol estimate as the main sizing layer (no look-ahead)."""
    raw = signal_monthly / vol_monthly.where(vol_monthly > 0)
    gross = raw.abs().sum(axis=1)                      # skips NaN
    base = raw.div(gross.where(gross > 0), axis=0)     # sum|base| = 1
    avail = signal_monthly.notna().sum(axis=1)
    return base, avail


def _erc_weights(cov: np.ndarray, iters: int = 1000, tol: float = 1e-12) -> np.ndarray:
    """Equal-risk-contribution weights (positive, sum 1) via cyclical coordinate
    descent (Griveau-Billion et al. 2013): each asset's total risk contribution
    w_i·(Σw)_i is equalized. Reduces to inverse-vol when assets are uncorrelated."""
    n = cov.shape[0]
    diag = np.diag(cov).copy()
    diag[diag <= 1e-15] = 1e-15
    b = 1.0 / n
    w = 1.0 / np.sqrt(diag)          # inverse-vol start
    w = w / w.sum()
    for _ in range(iters):
        w_old = w.copy()
        for i in range(n):
            a = cov[i, i]
            beta = cov[i, :] @ w - a * w[i]      # Σ_{j≠i} w_j cov_ij
            w[i] = (-beta + np.sqrt(beta * beta + 4.0 * a * b)) / (2.0 * a)
        s = w.sum()
        if not np.isfinite(s) or s <= 0:
            return np.ones(n) / n
        w = w / s
        if np.max(np.abs(w - w_old)) < tol:
            break
    return w


def risk_parity_aggregate(
    signal_monthly: pd.DataFrame,
    daily_prices: pd.DataFrame,
    cov_window: int,
) -> tuple[pd.DataFrame, pd.Series]:
    """Covariance-based equal-risk-contribution ("full risk parity").

    At each month-end M, estimate the covariance of daily returns over the trailing
    ``cov_window`` days (data <= M only — no look-ahead), solve ERC magnitudes, and
    apply the signal direction: base_i ∝ signal_i × erc_i, sum|base| = 1.
    Unlike inverse-vol, this accounts for cross-asset CORRELATIONS (the 'complex'
    bit), at the cost of estimating a noisy covariance matrix."""
    rets = daily_prices.pct_change()
    base = pd.DataFrame(np.nan, index=signal_monthly.index, columns=signal_monthly.columns)
    avail = pd.Series(0, index=signal_monthly.index, dtype=int)
    for M in signal_monthly.index:
        sig = signal_monthly.loc[M].dropna()
        if sig.empty:
            continue
        w_rets = rets.loc[:M, sig.index].tail(cov_window).dropna(axis=1, how="any")
        if w_rets.shape[1] < 2 or w_rets.shape[0] < cov_window:
            continue
        cov = np.cov(w_rets.to_numpy(), rowvar=False, ddof=1)
        erc = _erc_weights(cov)
        signed = sig[w_rets.columns].to_numpy() * erc          # direction × risk weight
        g = np.abs(signed).sum()
        if g > 0:
            base.loc[M, w_rets.columns] = signed / g
            avail.loc[M] = w_rets.shape[1]
    return base, avail


# --------------------------------------------------------------------------- #
# 2. Realized portfolio volatility (backward-looking)
# --------------------------------------------------------------------------- #
def base_portfolio_daily_returns(base_weights: pd.DataFrame, daily_prices: pd.DataFrame) -> pd.Series:
    """Daily return of the unlevered equal-weight base book.

    The weight held on day d is the most recent PRIOR month-end's base weight
    (``reindex(daily).ffill().shift(1)``): the ``shift(1)`` guarantees a weight
    decided at a month-end close is only applied from the next session onward —
    no same-bar look-ahead.
    """
    rets = daily_prices.pct_change()
    held = base_weights.reindex(rets.index, method="ffill").shift(1)
    return (held * rets).sum(axis=1, min_count=1)


def realized_portfolio_vol(
    base_daily_returns: pd.Series,
    window: int = config.PORT_VOL_WINDOW_DAYS,
    rule: str = config.SIGNAL_RESAMPLE,
) -> pd.Series:
    """Annualized rolling std of the base portfolio's daily returns, sampled at
    each month-end (the decision-time estimate). NaN until a full window exists."""
    vol_daily = base_daily_returns.rolling(window, min_periods=window).std(ddof=1)
    vol_daily = vol_daily * np.sqrt(config.TRADING_DAYS_PER_YEAR)
    return vol_daily.resample(rule).last()


# --------------------------------------------------------------------------- #
# 3. Leverage (vol target + gross cap)
# --------------------------------------------------------------------------- #
def leverage(
    port_vol: pd.Series,
    gross_base: pd.Series,
    target_vol: float = config.PORT_TARGET_VOL_ANNUAL,
    max_gross: float = config.MAX_GROSS_LEVERAGE,
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Return (leverage L, uncapped L_raw, cap_binds).

    L_raw = target_vol / realized_port_vol  (the pure vol-target scalar).
    The gross cap limits sum|weights| = L * gross_base <= max_gross, i.e.
    L <= max_gross / gross_base. L = min(L_raw, L_cap). Both NaN-aware: a missing
    vol estimate (warm-up) yields NaN leverage (no position), never a cap-only value.
    """
    l_raw = target_vol / port_vol.where(port_vol > 0)
    l_cap = max_gross / gross_base.where(gross_base > 0)
    # skipna=False so a NaN in EITHER input propagates (warm-up -> NaN, not L_cap).
    L = pd.concat([l_raw, l_cap], axis=1).min(axis=1, skipna=False)
    cap_binds = (l_raw > l_cap).fillna(False)
    return L, l_raw, cap_binds


def portfolio_weights(base_weights: pd.DataFrame, L: pd.Series) -> pd.DataFrame:
    """Final portfolio weights = base weights scaled by the portfolio leverage."""
    return base_weights.mul(L, axis=0)


def positions_from_weights(port_weights: pd.DataFrame) -> pd.DataFrame:
    """Position held during month M+1 = portfolio weight decided at month-end M."""
    return port_weights.shift(1)


def apply_no_trade_band(target_weights: pd.DataFrame, band: float) -> pd.DataFrame:
    """Suppress tiny rebalances. For each asset each month, keep the previously
    EXECUTED weight unless the new target moved by >= ``band`` (fraction of NAV).

    Economic rationale: most monthly turnover is sub-threshold re-scaling from the
    leverage / vol target that costs money but barely changes exposure. A band lets
    those drift and only trades when the change is material. It is path-dependent
    but look-ahead free: the executed weight at month M depends only on the target
    at M (data <= M) and the executed weight at M-1.

    band = 0 reproduces the target weights exactly.
    """
    cols = target_weights.columns
    out: list[pd.Series] = []
    prev: pd.Series | None = None
    for _, tgt in target_weights.iterrows():
        if tgt.isna().all():            # warm-up / no book: pass through, reset
            out.append(tgt)
            prev = None
            continue
        if prev is None:                # first executed month: trade to target
            cur = tgt.copy()
        else:                           # keep prev where |Δ| < band, else move to target
            move = (tgt - prev).abs() >= band
            cur = tgt.where(move, prev)
        out.append(cur)
        prev = cur
    return pd.DataFrame(out, index=target_weights.index, columns=cols)


# --------------------------------------------------------------------------- #
# End-to-end build
# --------------------------------------------------------------------------- #
def build_portfolio(
    daily_prices: pd.DataFrame,
    method: str = "B",
    agg: str = "equal_weight",
    cov_window: int = config.RP_COV_WINDOW_DAYS,
    target_vol: float = config.PORT_TARGET_VOL_ANNUAL,
    vol_window: int = config.PORT_VOL_WINDOW_DAYS,
    max_gross: float = config.MAX_GROSS_LEVERAGE,
    sizing_kwargs: dict | None = None,
) -> dict[str, object]:
    """daily prices -> sized per-asset weights -> aggregated book -> vol-targeted,
    capped portfolio. ``agg`` selects the aggregation: 'equal_weight' (main
    strategy, default), 'inverse_vol', or 'risk_parity' (CONTROLS). Returns a dict
    of the intermediate and final panels."""
    sized = sizing.build_position_sizes(daily_prices, method=method, **(sizing_kwargs or {}))
    asset_w = sized["weight"]

    if agg == "equal_weight":
        base, avail = equal_weight_aggregate(asset_w)
    elif agg == "inverse_vol":
        base, avail = inverse_vol_aggregate(sized["signal"], sized["vol"])
    elif agg == "risk_parity":
        base, avail = risk_parity_aggregate(sized["signal"], daily_prices, cov_window)
    else:
        raise ValueError(f"agg must be 'equal_weight'|'inverse_vol'|'risk_parity', got {agg!r}")
    gross_base = base.abs().sum(axis=1)

    rp = base_portfolio_daily_returns(base, daily_prices)
    port_vol = realized_portfolio_vol(rp, window=vol_window).reindex(base.index)

    L, l_raw, cap_binds = leverage(port_vol, gross_base, target_vol, max_gross)
    port_w = portfolio_weights(base, L)

    return {
        "asset_weight": asset_w,            # step-3 per-asset weights (month-end)
        "base_weight": base,                # equal-weight book (pre-leverage)
        "n_available": avail,               # live assets per month
        "gross_base": gross_base,           # sum|base weight|
        "asset_vol": sized["vol"],          # per-asset annualized vol (month-end)
        "port_vol": port_vol,               # realized portfolio vol estimate
        "leverage": L,                      # applied portfolio leverage
        "leverage_raw": l_raw,              # uncapped vol-target leverage
        "cap_binds": cap_binds,             # gross cap binding that month?
        "port_weight": port_w,              # final portfolio weights (decision month-end)
        "gross": port_w.abs().sum(axis=1),  # final gross notional
        "net": port_w.sum(axis=1),          # final net exposure
        "position": positions_from_weights(port_w),  # held next month
    }
