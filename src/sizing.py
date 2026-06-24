"""Step 3 — per-asset volatility scaling and position sizing.

SCOPE: per-asset position SIZE only. NO portfolio-level vol targeting, NO returns,
NO performance. Those are step 4+.

Idea
----
Convert a direction signal into a position whose size is **inversely proportional
to the asset's own volatility**, so every asset targets the same ex-ante risk
(``target_vol``):

    weight = signal * (target_vol / asset_vol)         (then capped)

High-vol assets (oil USO, natural gas UNG) get small positions; low-vol assets
(short Treasuries SHY) get large ones. A per-asset cap prevents an ultra-low-vol
asset from demanding extreme leverage — the well-known pitfall of vol scaling
(a low measured vol can mask tail/black-swan risk).

No look-ahead
-------------
The volatility used at month-end ``M`` is a rolling estimate from daily returns
up to and including ``M`` (strictly backward-looking), and the signal at ``M`` is
likewise built from closes ``<= M``. The sized weight at ``M`` therefore uses no
future data; the position is *held* during ``M+1`` (``positions = weight.shift(1)``).
Truncation invariance and the backward-only volatility are unit-tested.

Design knobs (conventional, NOT optimized — see config.py):
  * VOL_WINDOW_DAYS    = 60   rolling daily-vol window (~3 months)
  * TARGET_VOL_ANNUAL  = 0.10 per-asset annualized vol target
  * MAX_ASSET_WEIGHT   = 2.0  cap on |weight| per asset
"""

from __future__ import annotations

import numpy as np
import pandas as pd

import config
from . import signals


# --------------------------------------------------------------------------- #
# Volatility estimate (ex-ante, backward-looking)
# --------------------------------------------------------------------------- #
def daily_returns(daily_prices: pd.DataFrame) -> pd.DataFrame:
    """Per-asset simple daily returns (no cross-asset row dropping — each column
    keeps its own history)."""
    return daily_prices.pct_change()


def rolling_volatility(
    daily_prices: pd.DataFrame,
    window: int = config.VOL_WINDOW_DAYS,
    annualize: bool = True,
) -> pd.DataFrame:
    """Rolling standard deviation of daily returns over the trailing ``window``
    days. ``min_periods=window`` => NaN until a full window exists (no partial,
    no peeking). Annualized by sqrt(252) for comparability with the target."""
    rets = daily_returns(daily_prices)
    vol = rets.rolling(window=window, min_periods=window).std(ddof=1)
    if annualize:
        vol = vol * np.sqrt(config.TRADING_DAYS_PER_YEAR)
    return vol


def volatility_at_month_end(
    daily_prices: pd.DataFrame,
    window: int = config.VOL_WINDOW_DAYS,
    rule: str = config.SIGNAL_RESAMPLE,
) -> pd.DataFrame:
    """Ex-ante annualized vol sampled at each month-end (the decision-time value:
    the trailing-window vol as of the last trading day of the month)."""
    return rolling_volatility(daily_prices, window).resample(rule).last()


# --------------------------------------------------------------------------- #
# Position sizing
# --------------------------------------------------------------------------- #
def target_weights(
    signal_monthly: pd.DataFrame,
    vol_monthly: pd.DataFrame,
    target_vol: float = config.TARGET_VOL_ANNUAL,
    max_weight: float = config.MAX_ASSET_WEIGHT,
) -> pd.DataFrame:
    """weight = clip( signal * target_vol / asset_vol , -max, +max ).

    * vol <= 0 or NaN (insufficient history)  -> weight NaN (cannot size).
    * signal == 0 (flat)                      -> weight 0.
    """
    vol = vol_monthly.reindex(index=signal_monthly.index, columns=signal_monthly.columns)
    scalar = target_vol / vol.where(vol > 0)          # NaN where vol<=0 or NaN
    raw = signal_monthly * scalar
    capped = raw.clip(lower=-max_weight, upper=max_weight)
    # A flat signal is a deliberate 0 position regardless of vol.
    capped = capped.where(signal_monthly != 0, 0.0)
    return capped


def positions_from_weights(weights_monthly: pd.DataFrame) -> pd.DataFrame:
    """Position held during month ``M+1`` = weight decided at month-end ``M``
    (``weights.shift(1)``) — same no-look-ahead convention as the signal layer."""
    return weights_monthly.shift(1)


# --------------------------------------------------------------------------- #
# Convenience: daily prices -> sized positions
# --------------------------------------------------------------------------- #
def build_position_sizes(
    daily_prices: pd.DataFrame,
    method: str = "B",
    window: int = config.VOL_WINDOW_DAYS,
    target_vol: float = config.TARGET_VOL_ANNUAL,
    max_weight: float = config.MAX_ASSET_WEIGHT,
    signal_kwargs: dict | None = None,
) -> dict[str, pd.DataFrame]:
    """End-to-end (signal-layer + vol scaling). Returns dict with keys:
    'signal' (month-end), 'vol' (annualized, month-end), 'weight' (sized, at
    decision month-end), 'position' (weight.shift(1) = held next month)."""
    sig = signals.monthly_signals(daily_prices, method=method, **(signal_kwargs or {}))
    vol = volatility_at_month_end(daily_prices, window)
    weight = target_weights(sig, vol, target_vol, max_weight)
    position = positions_from_weights(weight)
    return {"signal": sig, "vol": vol, "weight": weight, "position": position}
