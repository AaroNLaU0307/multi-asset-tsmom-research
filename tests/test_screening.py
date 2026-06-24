"""Unit tests for the two fragile custom pieces: the greedy correlation filter
and the spike-and-revert data-quality detector. No network; synthetic inputs
with asserted outcomes.

Run:  python -m pytest -q
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.data_quality import detect_spike_revert  # noqa: E402
from src.recommend import greedy_filter  # noqa: E402


def _corr(d: dict[tuple[str, str], float], labels: list[str]) -> pd.DataFrame:
    """Build a symmetric correlation matrix from an upper-triangle dict."""
    m = pd.DataFrame(np.eye(len(labels)), index=labels, columns=labels)
    for (a, b), v in d.items():
        m.loc[a, b] = v
        m.loc[b, a] = v
    return m


def test_greedy_drops_perfect_duplicate():
    labels = ["A", "B", "C"]
    corr = _corr({("A", "B"): 0.99, ("A", "C"): 0.10, ("B", "C"): 0.10}, labels)
    kept, drop, info = greedy_filter(corr, {"A": 1, "B": 2, "C": 3}, 0.80)
    assert set(kept) == {"A", "C"}
    assert drop == ["B"]
    assert info["B"][0] == "A"  # dropped because of A


def test_priority_decides_which_of_a_pair_survives():
    labels = ["A", "B"]
    corr = _corr({("A", "B"): 0.95}, labels)
    # B has the better (lower) priority => B is kept, A dropped.
    kept, drop, _ = greedy_filter(corr, {"A": 5, "B": 1}, 0.80)
    assert kept == ["B"]
    assert drop == ["A"]


def test_non_transitive_chain_keeps_both_ends():
    # A~B = 0.85, B~C = 0.85, but A~C = 0.50. Connected-components would merge all
    # three; the greedy pairwise filter must keep A and C and drop only B.
    labels = ["A", "B", "C"]
    corr = _corr({("A", "B"): 0.85, ("B", "C"): 0.85, ("A", "C"): 0.50}, labels)
    kept, drop, _ = greedy_filter(corr, {"A": 1, "C": 2, "B": 3}, 0.80)
    assert set(kept) == {"A", "C"}
    assert drop == ["B"]


def test_inverse_pair_is_redundant():
    # Near -1 correlation (e.g. a USD-bull vs EUR ETF) must count as redundant.
    labels = ["A", "B", "C"]
    corr = _corr({("A", "B"): -0.95, ("A", "C"): 0.0, ("B", "C"): 0.0}, labels)
    kept, drop, _ = greedy_filter(corr, {"A": 1, "B": 2, "C": 3}, 0.80)
    assert "B" in drop
    assert set(kept) == {"A", "C"}


def test_spike_revert_detects_bad_print_roundtrip():
    idx = pd.bdate_range("2020-01-01", periods=6)
    # Day 3 jumps +40%, day 4 reverts -35%: a bad-tick round-trip.
    rets = pd.Series([0.01, -0.005, 0.40, -0.35, 0.002, -0.001], index=idx)
    hits = detect_spike_revert(rets, 0.25)
    assert list(hits) == [idx[3]]  # flags the revert (second) leg


def test_spike_revert_ignores_real_one_sided_move():
    idx = pd.bdate_range("2020-01-01", periods=5)
    # A single big move not reversed the next day is a real return, not flagged.
    rets = pd.Series([0.0, 0.30, 0.02, -0.01, 0.0], index=idx)
    hits = detect_spike_revert(rets, 0.25)
    assert len(hits) == 0
