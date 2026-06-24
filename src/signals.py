"""Time-series momentum (TSMOM) signal layer.

SCOPE: signal *generation* only. No position sizing, no volatility scaling, no
portfolio construction, no returns, no performance. Those are later steps.

Design principles (anti-overfitting — non-negotiable)
-----------------------------------------------------
* Signals are pure arithmetic on closed prices — objective and unambiguous.
* Lookbacks are CONVENTIONAL ({1,3,6,12} months), never optimized for a better
  backtest. See ``config.MOMENTUM_LOOKBACKS_MONTHS``.
* No look-ahead: the signal at month-end ``t`` uses only month-end closes ``<= t``.
  The position for the *next* month is the signal decided at the *previous*
  month-end (``positions = signal.shift(1)``). Both properties are unit-tested
  (truncation invariance + monthly timing) in ``tests/test_signals.py``.

Sign convention
---------------
+1 = long, -1 = short, 0 = neutral/flat.
* Method A returns the discrete sign of the N-month return: {-1, 0, +1}.
* Method B (default) averages the per-horizon signs:
    - combine="mean"  -> continuous score in [-1, +1] (e.g. 4 horizons give values
      in {-1, -0.5, 0, +0.5, +1}); magnitude = cross-horizon agreement strength,
      sign = net direction.
    - combine="vote"  -> discrete majority direction {-1, 0, +1} (0 on a tie).
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import pandas as pd

import config


# --------------------------------------------------------------------------- #
# Price -> monthly closes
# --------------------------------------------------------------------------- #
def to_monthly(daily_prices: pd.DataFrame, rule: str = config.SIGNAL_RESAMPLE) -> pd.DataFrame:
    """Resample daily adjusted closes to one close per calendar month.

    Convention: the monthly value is the **last available daily close within the
    calendar month** (the month-end trading day), labeled at the calendar
    month-end (e.g. 2008-10-31). Months before a ticker's inception are NaN.
    """
    monthly = daily_prices.resample(rule).last()
    return monthly


# --------------------------------------------------------------------------- #
# Raw momentum
# --------------------------------------------------------------------------- #
def momentum_return(monthly: pd.DataFrame, lookback_months: int) -> pd.DataFrame:
    """N-month simple return at each month-end: ``M_t / M_{t-N} - 1``.

    Uses only past month-end closes (``shift`` looks backward), so it is
    look-ahead free by construction. NaN until ``N`` prior months exist.
    """
    if lookback_months < 1:
        raise ValueError("lookback_months must be >= 1")
    return monthly / monthly.shift(lookback_months) - 1.0


# --------------------------------------------------------------------------- #
# Method A — single-horizon sign
# --------------------------------------------------------------------------- #
def signal_method_a(
    monthly: pd.DataFrame,
    lookback_months: int = config.MOMENTUM_LOOKBACK_A,
) -> pd.DataFrame:
    """sign( N-month return ) in {-1, 0, +1}; NaN where history is insufficient."""
    return np.sign(momentum_return(monthly, lookback_months))


# --------------------------------------------------------------------------- #
# Method B — multi-horizon composite (recommended default)
# --------------------------------------------------------------------------- #
def signal_method_b(
    monthly: pd.DataFrame,
    lookbacks_months: Sequence[int] = config.MOMENTUM_LOOKBACKS_MONTHS,
    combine: str = config.SIGNAL_COMBINE,
    min_periods: int | None = None,
) -> pd.DataFrame:
    """Average the per-horizon momentum signs across ``lookbacks_months``.

    min_periods : how many horizons must have data before a composite is emitted.
        Defaults to all of them (consistent definition over time). With fewer,
        the composite averages whatever horizons are available.
    """
    lookbacks = list(lookbacks_months)
    if min_periods is None:
        min_periods = len(lookbacks)

    sign_frames = [np.sign(momentum_return(monthly, n)) for n in lookbacks]
    arr = np.stack([s.to_numpy(dtype=float) for s in sign_frames], axis=0)  # (L, T, A)

    valid = ~np.isnan(arr)
    count = valid.sum(axis=0)                       # (T, A) horizons available
    summ = np.nansum(arr, axis=0)                   # (T, A) sum of available signs
    with np.errstate(invalid="ignore", divide="ignore"):
        mean = summ / np.where(count == 0, np.nan, count)
    score = np.where(count >= min_periods, mean, np.nan)   # NaN if too few horizons

    if combine == "mean":
        out = score
    elif combine == "vote":
        out = np.sign(score)
    else:
        raise ValueError(f"combine must be 'mean' or 'vote', got {combine!r}")

    return pd.DataFrame(out, index=monthly.index, columns=monthly.columns)


# --------------------------------------------------------------------------- #
# Convenience: daily prices -> monthly signal
# --------------------------------------------------------------------------- #
def monthly_signals(daily_prices: pd.DataFrame, method: str = "B", **kwargs) -> pd.DataFrame:
    """End-to-end: daily adjusted closes -> month-end signal panel.

    method "A" -> signal_method_a; method "B" -> signal_method_b.
    Extra kwargs are forwarded to the chosen signal function.
    """
    monthly = to_monthly(daily_prices)
    if method.upper() == "A":
        return signal_method_a(monthly, **kwargs)
    if method.upper() == "B":
        return signal_method_b(monthly, **kwargs)
    raise ValueError(f"method must be 'A' or 'B', got {method!r}")


# --------------------------------------------------------------------------- #
# Signal -> position timing (no look-ahead)
# --------------------------------------------------------------------------- #
def positions_from_signals(signal_monthly: pd.DataFrame) -> pd.DataFrame:
    """Map month-end signals to the position held during the FOLLOWING month.

    The row labeled month-end ``T`` carries the signal decided at month-end
    ``T-1``. Equivalently: ``positions = signal.shift(1)``. This guarantees the
    position applied to month ``T`` depends only on data observed up to the end
    of month ``T-1`` — strictly no look-ahead. (A trade decided at the close of
    ``T-1`` is held through ``T``.)
    """
    return signal_monthly.shift(1)
