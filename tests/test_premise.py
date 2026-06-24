"""Tests for the Phase-1B premise primitives (forward-window alignment is fragile).

Pins the efficiency-ratio / breakout / follow-through window logic on constructed
series with known outcomes. Synthetic only. Run:  python -m pytest -q
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import premise  # noqa: E402


def _series(vals) -> pd.DataFrame:
    idx = pd.bdate_range("2020-01-01", periods=len(vals))
    return pd.DataFrame({"A": np.asarray(vals, dtype=float)}, index=idx)


def test_ramp_is_fully_directional():
    # strictly rising ramp: efficiency ratio == 1, every breakout follows through.
    px = _series(np.arange(1.0, 81.0))
    fs = premise.forward_stats(px, horizon=5, lookback=5)
    er = fs["er"]["A"].dropna()
    assert np.allclose(er.to_numpy(), 1.0)
    follow = fs["follow"]["A"].where(fs["valid"]["A"]).dropna()
    assert follow.all()          # rising trend -> no false breakouts


def test_zigzag_is_choppy():
    # pure oscillation: low efficiency ratio, breakouts do NOT follow through.
    px = _series([100 + (i % 2) for i in range(80)])
    fs = premise.forward_stats(px, horizon=6, lookback=5)
    er = fs["er"]["A"].where(fs["valid"]["A"]).dropna()
    assert er.mean() < 0.5
    follow = fs["follow"]["A"].where(fs["valid"]["A"]).dropna()
    assert follow.mean() < 0.5   # mostly false breakouts


def test_valid_excludes_incomplete_forward_window():
    px = _series(np.arange(1.0, 41.0))
    N = 5
    fs = premise.forward_stats(px, horizon=N, lookback=5)
    # the last N rows cannot have a complete forward window
    assert not fs["valid"]["A"].iloc[-N:].any()


def test_masked_rate_counts_only_masked_cells():
    b = pd.DataFrame({"A": [True, False, True, True]})
    m = pd.DataFrame({"A": [True, True, False, False]})
    rate, n = premise._masked_rate(b, m, ["A"])
    assert n == 2 and abs(rate - 0.5) < 1e-12   # first two cells: True, False
