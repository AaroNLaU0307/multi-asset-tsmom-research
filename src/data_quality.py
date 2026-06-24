"""Data quality checks. Reports only — never drops anything automatically."""

from __future__ import annotations

import numpy as np
import pandas as pd

import config


def detect_spike_revert(returns: pd.Series, threshold: float) -> pd.DatetimeIndex:
    """Dates where a big move (> threshold) is immediately reversed by a big
    opposite move the next day — the signature of a bad price print.

    The returned date is the *revert* day (the second leg). Pure helper, unit-tested.
    """
    prev = returns.shift(1)
    mask = (returns.abs() > threshold) & (prev.abs() > threshold) & (
        np.sign(returns) != np.sign(prev)
    )
    return returns.index[mask.fillna(False)]


def build_quality_table(prices: pd.DataFrame) -> pd.DataFrame:
    """Per-ticker quality summary.

    Columns
    -------
    start_date, end_date  : first / last valid observation
    n_trading_days        : count of non-NaN observations
    internal_missing      : NaNs *inside* the ticker's own [start, end] span,
                            measured against the union calendar (internal gaps)
    short_history_flag    : True if it starts after config.LATE_START_FLAG
    n_jumps               : count of |daily return| > config.JUMP_THRESHOLD
    jump_detail           : "YYYY-MM-DD:+.x; ..." for flagged jumps (or "")
    max_abs_daily_move    : largest |daily return| observed
    max_move_date         : date of that largest move
    n_spike_revert        : count of bad-print "spike-and-revert" days
    spike_revert_detail   : "YYYY-MM-DD; ..." for those days (or "")
    """
    late_start = pd.Timestamp(config.LATE_START_FLAG)
    rows = []
    for t in config.TICKERS:
        s = prices[t] if t in prices.columns else pd.Series(dtype=float)
        valid = s.dropna()
        if valid.empty:
            rows.append(
                {
                    "ticker": t,
                    "factor": config.ASSET_UNIVERSE[t],
                    "start_date": "",
                    "end_date": "",
                    "n_trading_days": 0,
                    "internal_missing": 0,
                    "short_history_flag": True,
                    "n_jumps": 0,
                    "jump_detail": "NO DATA",
                    "max_abs_daily_move": float("nan"),
                    "max_move_date": "",
                    "n_spike_revert": 0,
                    "spike_revert_detail": "",
                }
            )
            continue

        start, end = valid.index.min(), valid.index.max()
        span = s.loc[start:end]
        internal_missing = int(span.isna().sum())

        ret = valid.pct_change().dropna()
        jumps = ret[ret.abs() > config.JUMP_THRESHOLD]
        jump_detail = "; ".join(f"{d.date()}:{v:+.0%}" for d, v in jumps.items())

        # spike-and-revert: a big move immediately reversed by a big opposite move.
        prev = ret.shift(1)
        sr_dates = detect_spike_revert(ret, config.SPIKE_REVERT_MOVE)
        sr_detail = "; ".join(
            f"{d.date()}({prev.loc[d]:+.0%}->{ret.loc[d]:+.0%})" for d in sr_dates
        )

        max_date = ret.abs().idxmax() if not ret.empty else None
        rows.append(
            {
                "ticker": t,
                "factor": config.ASSET_UNIVERSE[t],
                "start_date": start.date().isoformat(),
                "end_date": end.date().isoformat(),
                "n_trading_days": int(valid.shape[0]),
                "internal_missing": internal_missing,
                "short_history_flag": bool(start > late_start),
                "n_jumps": int(jumps.shape[0]),
                "jump_detail": jump_detail,
                "max_abs_daily_move": round(float(ret.abs().max()), 4) if not ret.empty else float("nan"),
                "max_move_date": max_date.date().isoformat() if max_date is not None else "",
                "n_spike_revert": int(len(sr_dates)),
                "spike_revert_detail": sr_detail,
            }
        )

    table = pd.DataFrame(rows).set_index("ticker")
    table.to_csv(config.DATA_QUALITY_CSV)
    return table


def common_period(prices: pd.DataFrame) -> tuple[pd.Timestamp, pd.Timestamp, pd.DataFrame]:
    """Restrict to dates where *every* successfully-fetched ticker has data.

    Returns (start, end, aligned_prices). The common window is bounded by the
    youngest ETF's inception, so we report it explicitly.
    """
    have = [t for t in config.TICKERS if t in prices.columns and prices[t].notna().any()]
    sub = prices[have].dropna(how="any")
    if sub.empty:
        raise RuntimeError("No overlapping dates across all tickers.")
    return sub.index.min(), sub.index.max(), sub
