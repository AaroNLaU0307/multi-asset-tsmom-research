"""Causal yield-curve primitives for the macro-regime overlay (research/yield_spread).

External data: user-supplied FRED constant-maturity Treasury CSVs (DGS3MO/DGS2/DGS10)
in ``data/`` (gitignored). The conditioning STATE is strictly point-in-time / causal,
in the exact style of the Step-5 regime variables (``src/regime.py``):

    raw yields  ->  reindex onto the ETF trading calendar + PAST-ONLY ffill
                ->  slope (long - short, percentage points)
                ->  trailing-percentile rank within a trailing window (causal)
                ->  tercile bucket {flat, mid, steep}
                ->  USED AT t-1 (the signal that conditions day-t forward returns)

Treasury H.15 yields are published same-day and not materially revised, so the t-1
value is a genuine point-in-time observation. Forward-fill on the ~36 calendar-mismatch
days (Columbus/Veterans, when ETFs trade but no yield prints) carries the *last known*
yield — never a future one. Truncation-invariance of the state path is unit-tested.

The forward-return helpers (``forward_cum_return`` / ``backward_cum_return``) build the
OUTCOME ``y_t`` and are intentionally forward-looking; the no-look-ahead guarantee lives
in the SIGNAL (state at t-1), not the outcome.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

import config
from . import regime


# --------------------------------------------------------------------------- #
# Loading + causal alignment
# --------------------------------------------------------------------------- #
def load_yields(files: dict | None = None) -> pd.DataFrame:
    """Load FRED CMT CSVs into a wide DataFrame (index = date, columns = series ids).

    Robust to the two FRED header styles (``observation_date,<ID>`` or ``DATE,<ID>``)
    and the ``.`` missing-value token. Numeric, de-duplicated, sorted ascending.
    """
    files = files or config.YIELD_FILES
    cols: dict[str, pd.Series] = {}
    for fid, path in files.items():
        df = pd.read_csv(path, na_values=["."])
        date_col, val_col = df.columns[0], df.columns[1]
        s = pd.Series(
            pd.to_numeric(df[val_col], errors="coerce").to_numpy(),
            index=pd.to_datetime(df[date_col]),
            name=fid,
        )
        s = s[~s.index.duplicated(keep="last")].sort_index()
        cols[fid] = s
    out = pd.DataFrame(cols).sort_index()
    out.index.name = "date"
    return out


def align_to_calendar(yields_df: pd.DataFrame, calendar) -> pd.DataFrame:
    """Reindex yields onto ``calendar`` (the ETF trading days) and forward-fill
    PAST-ONLY. ffill carries the most recent *published* yield forward, so a day on
    which the bond market was closed but ETFs traded uses the prior business day's
    curve — causal, no look-ahead. Leading calendar dates with no prior yield stay NaN.
    """
    cal = pd.DatetimeIndex(calendar)
    return yields_df.reindex(cal).ffill()


def slope(aligned: pd.DataFrame, long_leg: str, short_leg: str) -> pd.Series:
    """Curve slope = long-maturity yield - short-maturity yield (percentage points)."""
    return (aligned[long_leg] - aligned[short_leg]).rename(f"{long_leg}_{short_leg}")


# --------------------------------------------------------------------------- #
# Causal regime state
# --------------------------------------------------------------------------- #
def trailing_pctile(s: pd.Series, window: int = config.YIELD_PCTILE_WINDOW) -> pd.Series:
    """Causal trailing-percentile rank of the slope (reuses the verified-causal
    ``regime._trailing_pctile``): fraction of the trailing ``window`` (incl. today)
    that is <= today's slope. NaN until a full window exists."""
    return regime._trailing_pctile(s, window)


def tercile_state(
    pctile: pd.Series,
    lo: float = config.YIELD_TERCILE_LO,
    hi: float = config.YIELD_TERCILE_HI,
) -> pd.Series:
    """Map a trailing-percentile series to {``flat``, ``mid``, ``steep``}.

    flat = relatively flat/inverted (pctile <= lo); steep = relatively steep
    (pctile >= hi); mid otherwise. Undefined (NaN pctile, e.g. warmup) -> NaN.
    NOTE: this is the CONTINUOUS slope state ("relatively flat" vs "relatively
    steep"), which is a different proposition from a raw ``slope<0`` inversion.
    """
    state = pd.Series(np.nan, index=pctile.index, dtype=object)
    defined = pctile.notna()
    state[defined & (pctile <= lo)] = "flat"
    state[defined & (pctile >= hi)] = "steep"
    state[defined & (pctile > lo) & (pctile < hi)] = "mid"
    return state


def inversion_state(slope_series: pd.Series) -> pd.Series:
    """Raw recession-signal state (robustness view): ``flat`` where slope < 0
    (inverted), ``steep`` otherwise. Binary, uses the absolute 0 threshold — a
    DIFFERENT proposition from the continuous tercile state above."""
    state = pd.Series(np.nan, index=slope_series.index, dtype=object)
    defined = slope_series.notna()
    state[defined & (slope_series < 0.0)] = "flat"
    state[defined & (slope_series >= 0.0)] = "steep"
    return state


# --------------------------------------------------------------------------- #
# Outcome (forward / backward returns) — forward-looking BY DESIGN (the outcome,
# not the signal). No look-ahead is enforced on the t-1 SIGNAL, not here.
# --------------------------------------------------------------------------- #
def forward_cum_return(r: pd.Series, h: int) -> pd.Series:
    """Cumulative simple return over the forward window [t, t+h-1] (h days starting
    at t). NaN where the full future window is not available (no peeking past the end)."""
    lr = np.log1p(r)
    fwd = lr.rolling(h, min_periods=h).sum().shift(-(h - 1))
    return np.expm1(fwd)


def backward_cum_return(r: pd.Series, h: int) -> pd.Series:
    """Cumulative simple return over the trailing window [t-h+1, t] (for the
    contemporaneous-vs-predictive confound diagnostic only)."""
    return np.expm1(np.log1p(r).rolling(h, min_periods=h).sum())


# --------------------------------------------------------------------------- #
# Episode identification (event-level robustness unit)
# --------------------------------------------------------------------------- #
def runs_to_episodes(mask: pd.Series, bridge: int = config.YIELD_EPISODE_BRIDGE) -> list[dict]:
    """Maximal contiguous runs of True in ``mask`` (indexed by trading day), merging
    runs separated by <= ``bridge`` trading days. Returns episode date spans + sizes.

    This is the independent unit for the leave-one-episode-out jackknife: with so few
    distinct curve episodes, the day count is NOT the effective sample size.
    """
    idx = mask.index
    vals = np.asarray(mask.to_numpy(), dtype=bool)
    n = len(vals)
    raw: list[list[int]] = []
    i = 0
    while i < n:
        if vals[i]:
            j = i
            while j + 1 < n and vals[j + 1]:
                j += 1
            raw.append([i, j])
            i = j + 1
        else:
            i += 1
    if bridge > 0 and len(raw) > 1:
        merged = [raw[0][:]]
        for s, e in raw[1:]:
            if s - merged[-1][1] - 1 <= bridge:
                merged[-1][1] = e
            else:
                merged.append([s, e])
        raw = merged
    return [
        {"start": idx[s], "end": idx[e], "n_days": e - s + 1}
        for s, e in raw
    ]
