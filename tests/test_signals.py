"""Tests for the momentum signal layer.

Two priorities:
  1. Correctness of the sign / composite arithmetic (deterministic monthly inputs).
  2. NO LOOK-AHEAD — truncation invariance and the monthly position timing. These
     are the core safety guarantees of the signal layer.

Run:  python -m pytest -q
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import signals  # noqa: E402


def _monthly(prices: list[float], col: str = "X") -> pd.DataFrame:
    idx = pd.date_range("2005-01-31", periods=len(prices), freq="ME")
    return pd.DataFrame({col: prices}, index=idx)


def _synthetic_daily(seed: int = 7, years: int = 5, cols=("A", "B")) -> pd.DataFrame:
    """Deterministic daily random-walk prices on business days."""
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2004-01-01", periods=years * 252)
    out = {}
    for c in cols:
        steps = rng.normal(0.0003, 0.01, size=len(idx))
        out[c] = 100.0 * np.exp(np.cumsum(steps))
    return pd.DataFrame(out, index=idx)


# --------------------------------------------------------------------------- #
# 1. Correctness — Method A
# --------------------------------------------------------------------------- #
def test_method_a_rising_is_long():
    m = _monthly([100 * 1.02 ** k for k in range(15)])
    sig = signals.signal_method_a(m, lookback_months=3)
    valid = sig["X"].dropna()
    assert (valid == 1.0).all()


def test_method_a_falling_is_short():
    m = _monthly([100 * 0.98 ** k for k in range(15)])
    sig = signals.signal_method_a(m, lookback_months=3)
    assert (sig["X"].dropna() == -1.0).all()


def test_method_a_flat_is_neutral():
    m = _monthly([100.0] * 15)
    sig = signals.signal_method_a(m, lookback_months=3)
    assert (sig["X"].dropna() == 0.0).all()


# --------------------------------------------------------------------------- #
# 2. Correctness — Method B composite
# --------------------------------------------------------------------------- #
def test_method_b_all_agree_long():
    m = _monthly([100 * 1.01 ** k for k in range(13)])
    score = signals.signal_method_b(m, lookbacks_months=[1, 3, 6, 12], combine="mean")
    assert score["X"].iloc[-1] == 1.0  # all four horizons positive


def test_method_b_mixed_score_and_vote():
    # up to a high plateau, then a recent drop:
    # 1M, 3M, 6M momentum < 0 ; 12M momentum > 0  ->  signs (-1,-1,-1,+1)
    prices = [100, 110, 120, 130, 140, 145, 150, 150, 150, 150, 150, 150, 120]
    m = _monthly(prices)
    mean = signals.signal_method_b(m, lookbacks_months=[1, 3, 6, 12], combine="mean")
    vote = signals.signal_method_b(m, lookbacks_months=[1, 3, 6, 12], combine="vote")
    assert mean["X"].iloc[-1] == -0.5      # (-1-1-1+1)/4
    assert vote["X"].iloc[-1] == -1.0      # majority short


def test_method_b_tie_is_neutral():
    # signs (+1,+1,-1,-1) -> mean 0 -> vote 0
    prices = [150, 150, 150, 150, 150, 150, 150, 100, 100, 100, 100, 100, 120]
    m = _monthly(prices)
    mean = signals.signal_method_b(m, lookbacks_months=[1, 3, 6, 12], combine="mean")
    vote = signals.signal_method_b(m, lookbacks_months=[1, 3, 6, 12], combine="vote")
    assert mean["X"].iloc[-1] == 0.0
    assert vote["X"].iloc[-1] == 0.0


def test_method_b_requires_all_periods_by_default():
    # 12M momentum needs 12 prior months; with 13 months only the last row qualifies.
    m = _monthly([100 * 1.01 ** k for k in range(13)])
    score = signals.signal_method_b(m)
    assert score["X"].iloc[:-1].isna().all()
    assert not np.isnan(score["X"].iloc[-1])


# --------------------------------------------------------------------------- #
# 3. NO LOOK-AHEAD — truncation invariance
# --------------------------------------------------------------------------- #
def test_truncation_invariance_method_b():
    daily = _synthetic_daily()
    full = signals.monthly_signals(daily, method="B")
    cut = full.index[30]                       # a month-end well into the series
    trunc = signals.monthly_signals(daily.loc[:cut], method="B")
    # Every signal at or before the cut must be byte-identical to the full-data run.
    pd.testing.assert_frame_equal(full.loc[trunc.index], trunc)


def test_truncation_invariance_method_a():
    daily = _synthetic_daily(seed=11)
    full = signals.monthly_signals(daily, method="A")
    cut = full.index[24]
    trunc = signals.monthly_signals(daily.loc[:cut], method="A")
    pd.testing.assert_frame_equal(full.loc[trunc.index], trunc)


# --------------------------------------------------------------------------- #
# 4. NO LOOK-AHEAD — monthly position timing
# --------------------------------------------------------------------------- #
def test_positions_are_signal_shifted_one_month():
    daily = _synthetic_daily()
    sig = signals.monthly_signals(daily, method="B")
    pos = signals.positions_from_signals(sig)
    pd.testing.assert_frame_equal(pos, sig.shift(1))
    assert pos.iloc[0].isna().all()           # first month has no prior signal


def test_position_uses_only_prior_month_data():
    """The position held in month T must be reproducible from data truncated at
    the end of month T-1 — i.e. it cannot depend on anything in month T or later."""
    daily = _synthetic_daily()
    sig = signals.monthly_signals(daily, method="B")
    pos = signals.positions_from_signals(sig)

    t = sig.index[40]
    t_prev = sig.index[39]
    # Recompute the signal using ONLY data up to the prior month-end.
    sig_trunc = signals.monthly_signals(daily.loc[:t_prev], method="B")
    reproduced = sig_trunc.loc[t_prev]
    pd.testing.assert_series_equal(pos.loc[t], reproduced, check_names=False)
