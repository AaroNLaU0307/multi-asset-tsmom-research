"""Step 5 — reusable point-in-time (causal) regime descriptors.

Unlike the full-sample descriptive episode labels in ``src/attribution.py``, these
variables are STRICTLY causal: each value at date ``t`` uses only data observed up
to and including ``t`` (trailing windows and trailing percentile ranks — no
full-sample mean/quantile normalization, no future leakage). They are meant to be
reusable as live signals when designing a later overlay, so look-ahead freedom is
non-negotiable here.

Variables
---------
* per-asset realized-vol percentile : trailing rolling rank of the current
  ``REGIME_VOL_WINDOW_DAYS`` annualized vol within a trailing
  ``REGIME_VOL_PCTILE_WINDOW`` window (fraction of that window <= today's vol).
* per-asset trendiness (efficiency ratio) : |p_t - p_{t-w}| / Σ|Δp| over the
  trailing ``REGIME_ER_WINDOW_DAYS`` window (~0 chop, ~1 clean trend).
* portfolio realized-vol percentile : same rank, on an equal-weight universe basket
  (a market-state proxy, position-independent so it is reusable as a pure signal).
* cross-asset dispersion : cross-sectional std across assets of the trailing
  ``REGIME_DISP_WINDOW_DAYS`` return, one value per date.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

import config


def _trailing_pctile(s: pd.Series, window: int) -> pd.Series:
    """Causal percentile rank: fraction of the trailing ``window`` (incl. today)
    that is <= today's value. NaN until a full window exists."""
    return s.rolling(window, min_periods=window).apply(
        lambda a: float((a <= a[-1]).mean()), raw=True
    )


def realized_vol(daily_px: pd.DataFrame, window: int = config.REGIME_VOL_WINDOW_DAYS) -> pd.DataFrame:
    """Trailing annualized realized vol per asset (backward-looking)."""
    rets = daily_px.pct_change()
    return rets.rolling(window, min_periods=window).std(ddof=1) * np.sqrt(config.TRADING_DAYS_PER_YEAR)


def efficiency_ratio(daily_px: pd.DataFrame, window: int = config.REGIME_ER_WINDOW_DAYS) -> pd.DataFrame:
    """Trailing Kaufman efficiency ratio per asset (causal): net move / path length."""
    net = (daily_px - daily_px.shift(window)).abs()
    path = daily_px.diff().abs().rolling(window, min_periods=window).sum()
    return net / path.where(path > config.ER_FLOOR_DENOM)


def cross_asset_dispersion(daily_px: pd.DataFrame, window: int = config.REGIME_DISP_WINDOW_DAYS) -> pd.Series:
    """Cross-sectional std (across assets) of the trailing ``window`` return."""
    win_ret = daily_px / daily_px.shift(window) - 1.0
    return win_ret.std(axis=1, ddof=1)


def build_panel(daily_px: pd.DataFrame) -> pd.DataFrame:
    """Assemble a wide, daily, strictly-causal regime panel (saved as one artifact).

    Columns: ``vol_pctile_<TKR>``, ``er_<TKR>`` per asset, plus portfolio-level
    ``port_vol``, ``port_vol_pctile`` (equal-weight basket proxy) and
    ``cross_asset_dispersion``.
    """
    vol = realized_vol(daily_px)
    vol_pctile = vol.apply(lambda c: _trailing_pctile(c, config.REGIME_VOL_PCTILE_WINDOW))
    er = efficiency_ratio(daily_px)

    # equal-weight universe basket as a position-independent market-state proxy
    basket = daily_px.pct_change().mean(axis=1, skipna=True)
    port_vol = basket.rolling(config.REGIME_VOL_WINDOW_DAYS,
                              min_periods=config.REGIME_VOL_WINDOW_DAYS).std(ddof=1) \
        * np.sqrt(config.TRADING_DAYS_PER_YEAR)
    port_vol_pctile = _trailing_pctile(port_vol, config.REGIME_VOL_PCTILE_WINDOW)
    disp = cross_asset_dispersion(daily_px)

    panel = pd.concat(
        [vol_pctile.add_prefix("vol_pctile_"),
         er.add_prefix("er_"),
         port_vol.rename("port_vol"),
         port_vol_pctile.rename("port_vol_pctile"),
         disp.rename("cross_asset_dispersion")],
        axis=1,
    )
    panel.index.name = "date"
    # keep rows where at least the portfolio-level vars are defined
    return panel.loc[panel["port_vol_pctile"].notna() | panel["cross_asset_dispersion"].notna()]
