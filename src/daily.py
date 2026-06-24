"""Daily research infrastructure for the vol-compression breakout study (strategy B).

Vol-compression breakout is inherently a DAILY concept (vol/ATR percentile, breakout
of recent highs) that cannot be expressed on the monthly engine. This module adds the
daily primitives, REUSING existing components:
  * the same 17-ETF universe and the same cached daily adjusted closes that the monthly
    engine resamples (``fetch_data`` -> ``px``), so results stay reconcilable;
  * the verified-causal regime primitives (``src/regime.py``) for the vol percentile.

Every primitive is strictly point-in-time / causal (trailing windows only; breakout
references exclude the current day), exactly like the Step-5 regime variables —
truncation-invariance is unit-tested. Data is adjusted-close only (no intraday H/L),
so "compression" uses the daily realized-vol percentile rather than a true ATR.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

import config
from . import regime, signals


def daily_returns(px: pd.DataFrame) -> pd.DataFrame:
    """Per-asset simple daily returns."""
    return px.pct_change()


def realized_vol(px: pd.DataFrame, window: int = config.COMPRESSION_VOL_WINDOW) -> pd.DataFrame:
    """Trailing annualized realized vol per asset (reuses regime.realized_vol)."""
    return regime.realized_vol(px, window)


def vol_percentile(
    px: pd.DataFrame,
    window: int = config.COMPRESSION_VOL_WINDOW,
    pctile_window: int = config.COMPRESSION_PCTILE_WINDOW,
) -> pd.DataFrame:
    """Causal compression measure: trailing percentile rank of the current realized
    vol within a trailing ``pctile_window`` (low percentile = compressed). Same
    definition style as the verified-causal Step-5 vol percentile."""
    vol = realized_vol(px, window)
    return vol.apply(lambda c: regime._trailing_pctile(c, pctile_window))


def recent_high(px: pd.DataFrame, lookback: int = config.BREAKOUT_LOOKBACK) -> pd.DataFrame:
    """Trailing max over the prior ``lookback`` days, EXCLUDING today (so a same-day
    close can break it) — the causal upside breakout reference (Donchian channel top)."""
    return px.shift(1).rolling(lookback, min_periods=lookback).max()


def recent_low(px: pd.DataFrame, lookback: int = config.BREAKOUT_LOOKBACK) -> pd.DataFrame:
    """Trailing min over the prior ``lookback`` days, EXCLUDING today (Donchian bottom)."""
    return px.shift(1).rolling(lookback, min_periods=lookback).min()


def is_compressed(px: pd.DataFrame, threshold: float = config.COMPRESSION_THRESHOLD,
                  **kw) -> pd.DataFrame:
    """Boolean panel: True where the causal vol percentile is <= ``threshold``."""
    return vol_percentile(px, **kw) <= threshold


def monthly_return_from_daily(px: pd.DataFrame, rule: str = config.SIGNAL_RESAMPLE) -> pd.DataFrame:
    """Compound daily simple returns within each calendar month -> monthly return.

    Within a month the product of (1+r_d) telescopes to last_close/prev_month_last_close,
    so this MUST equal ``to_monthly(px).pct_change()`` (the engine's monthly returns) on
    every full month — the reconciliation identity that ties the daily infra to the
    validated monthly engine."""
    r = daily_returns(px)
    return (1.0 + r).resample(rule).prod() - 1.0


def monthly_return_from_prices(px: pd.DataFrame) -> pd.DataFrame:
    """The engine's monthly asset returns: to_monthly(px).pct_change()."""
    return signals.to_monthly(px).pct_change()


def reconcile_daily_to_monthly(px: pd.DataFrame) -> dict[str, float]:
    """Max abs diff between daily-compounded and price-based monthly returns, over the
    overlap where both are defined (first month is NaN for the price-based version)."""
    a = monthly_return_from_daily(px)
    b = monthly_return_from_prices(px)
    common = a.index.intersection(b.index)
    a, b = a.loc[common], b.loc[common]
    diff = (a - b).abs().where(a.notna() & b.notna())   # only where both defined
    arr = diff.to_numpy()
    finite = np.isfinite(arr)
    return {
        "max_abs_diff": float(np.nanmax(arr)) if finite.any() else float("nan"),
        "n_months": int(len(common)),
        "n_obs": int(finite.sum()),
        "n_assets": int(px.shape[1]),
    }
