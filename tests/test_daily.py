"""Tests for the daily research infrastructure (vol-compression breakout, Phase 1A).

Fragile pieces:
  1. RECONCILIATION — compounding daily returns within a month must equal the engine's
     price-based monthly return (the identity that ties daily infra to the monthly engine).
  2. CAUSALITY — vol percentile / recent-high / recent-low are trailing-only
     (truncation invariant); the breakout reference excludes the current day.

Synthetic data only, per repo convention. Run:  python -m pytest -q
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import daily  # noqa: E402


def _synth(seed: int = 3, n: int = 900, cols=("A", "B", "C")) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2015-01-01", periods=n)
    return pd.DataFrame(
        {c: 100.0 * np.exp(np.cumsum(rng.normal(0.0003, 0.01, n))) for c in cols}, index=idx
    )


def test_daily_to_monthly_reconciles():
    rec = daily.reconcile_daily_to_monthly(_synth())
    assert rec["max_abs_diff"] < 1e-12
    assert rec["n_obs"] > 0


def test_recent_high_excludes_today():
    # strictly rising series: today's close must exceed the prior-window max every day.
    idx = pd.bdate_range("2020-01-01", periods=60)
    s = pd.DataFrame({"A": np.arange(1.0, 61.0)}, index=idx)
    rh = daily.recent_high(s, lookback=5)["A"].dropna()
    assert (s["A"].loc[rh.index] > rh).all()


def test_daily_primitives_causal():
    px = _synth()
    for fn in (daily.realized_vol, daily.vol_percentile, daily.recent_high, daily.recent_low):
        full = fn(px)
        cut = px.index[int(len(px) * 0.6)]
        tr = fn(px.loc[:cut])
        common = tr.index.intersection(full.index)
        d = (full.loc[common, tr.columns] - tr.loc[common, tr.columns]).abs().to_numpy()
        assert float(np.nanmax(d)) < 1e-12
