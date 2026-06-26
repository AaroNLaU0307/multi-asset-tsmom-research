"""Tests for the Cross-Sectional Momentum (XSMOM) signal + construction layers.

Priorities (mirror the TSMOM signal tests):
  1. Correctness of the 12-1 signal and the EXPLICIT skip-month.
  2. Dollar-neutrality of both constructions (the defining XSMOM property).
  3. NO LOOK-AHEAD — truncation invariance + monthly position timing, including the
     demeaned-signal confound variant (its "long-run mean" must be backward-only).

Run:  python -m pytest -q
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import xsmom_config as xcfg  # noqa: E402
from src import xsmom  # noqa: E402


# --------------------------------------------------------------------------- #
# Synthetic daily prices
# --------------------------------------------------------------------------- #
def _synthetic_daily(seed: int = 7, days: int = 1008, n_assets: int = 14) -> pd.DataFrame:
    """Deterministic daily random-walk prices (>= 273 days so the 12-1 signal is
    defined, >= 12 assets so a 6/6 tercile can form)."""
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2016-01-01", periods=days)
    cols = [f"A{i:02d}" for i in range(n_assets)]
    out = {}
    for c in cols:
        steps = rng.normal(0.0003, 0.01, size=days)
        out[c] = 100.0 * np.exp(np.cumsum(steps))
    return pd.DataFrame(out, index=idx)


# --------------------------------------------------------------------------- #
# 1. Signal correctness — ordering by 12-1 return
# --------------------------------------------------------------------------- #
def test_signal_orders_by_12_1_return():
    days = 400
    idx = pd.bdate_range("2016-01-01", periods=days)
    # three constant-growth assets: faster growth => larger 12-1 return
    prices = pd.DataFrame({
        "SLOW": [100 * 1.0002 ** k for k in range(days)],
        "MID":  [100 * 1.0005 ** k for k in range(days)],
        "FAST": [100 * 1.0010 ** k for k in range(days)],
    }, index=idx)
    sig = xsmom.momentum_skip(prices).iloc[-1]
    assert sig["SLOW"] < sig["MID"] < sig["FAST"]
    # closed-form check: constant daily growth g => signal = g**(form-skip) - 1
    g = 1.0010
    expected_fast = g ** (xcfg.LOOKBACK_DAYS - xcfg.SKIP_DAYS) - 1.0
    assert sig["FAST"] == pytest.approx(expected_fast, rel=1e-9)


# --------------------------------------------------------------------------- #
# 2. The skip-month is EXPLICIT — a spike in the most recent month is excluded
# --------------------------------------------------------------------------- #
def test_skip_month_excludes_recent_spike():
    days = 400
    idx = pd.bdate_range("2016-01-01", periods=days)
    # flat at 100 through day 378, then a sharp +50% spike over the last 21 days.
    px = np.full(days, 100.0)
    for i in range(379, days):
        px[i] = 100.0 * 1.02 ** (i - 378)
    prices = pd.DataFrame({"SPIKE": px}, index=idx)

    skipped = xsmom.momentum_skip(prices, skip_days=21, formation_days=252).iloc[-1, 0]
    naive = xsmom.momentum_skip(prices, skip_days=0, formation_days=252).iloc[-1, 0]

    assert skipped == pytest.approx(0.0, abs=1e-9)   # last-month spike is skipped
    assert naive > 0.40                              # no-skip would chase the spike


# --------------------------------------------------------------------------- #
# 3. Tercile — dollar-neutral, equal-weight, top/bottom selection
# --------------------------------------------------------------------------- #
def test_tercile_dollar_neutral_equal_weight():
    daily = _synthetic_daily()
    sig = xsmom.momentum_skip(daily)
    w = xsmom.tercile_weights(sig)
    row = w.dropna(how="all").iloc[-1]               # a fully-formed month

    longs = row[row > 0]
    shorts = row[row < 0]
    assert len(longs) == xcfg.N_LONG
    assert len(shorts) == xcfg.N_SHORT
    assert longs.sum() == pytest.approx(1.0, abs=1e-12)
    assert shorts.sum() == pytest.approx(-1.0, abs=1e-12)
    assert row.sum() == pytest.approx(0.0, abs=1e-12)   # dollar-neutral
    assert np.allclose(longs.values, 1.0 / xcfg.N_LONG)  # equal weight in-leg
    assert np.allclose(shorts.values, -1.0 / xcfg.N_SHORT)


def test_tercile_longs_are_top_ranked():
    cols = [f"A{i:02d}" for i in range(13)]
    # one fully-formed month, strictly increasing signals A00<A01<...<A12
    sig = pd.DataFrame([{c: float(i) for i, c in enumerate(cols)}],
                       index=pd.to_datetime(["2020-01-31"]))
    w = xsmom.tercile_weights(sig).iloc[0]
    top = set(w[w > 0].index)
    bottom = set(w[w < 0].index)
    assert top == {f"A{i:02d}" for i in range(7, 13)}     # 6 highest signals
    assert bottom == {f"A{i:02d}" for i in range(0, 6)}   # 6 lowest signals


def test_tercile_warmup_is_no_book():
    daily = _synthetic_daily(days=300)
    sig = xsmom.momentum_skip(daily)
    w = xsmom.tercile_weights(sig)
    # before any asset has a 12-1 signal, the whole row is NaN (not a partial book)
    assert w.iloc[0].isna().all()


# --------------------------------------------------------------------------- #
# 4. Rank-weight — dollar-neutral, gross 2, monotone in the signal
# --------------------------------------------------------------------------- #
def test_rank_weights_dollar_neutral_and_monotone():
    daily = _synthetic_daily()
    sig = xsmom.momentum_skip(daily)
    w = xsmom.rank_weights(sig)
    row = w.dropna(how="all").iloc[-1]
    sigrow = sig.loc[row.name]

    assert row[row > 0].sum() == pytest.approx(1.0, abs=1e-12)
    assert row[row < 0].sum() == pytest.approx(-1.0, abs=1e-12)
    assert row.sum() == pytest.approx(0.0, abs=1e-12)
    assert row.abs().sum() == pytest.approx(2.0, abs=1e-12)   # gross = 2
    # monotone: ranking assets by signal and by weight must agree
    order_sig = sigrow.sort_values().index
    order_w = row.reindex(order_sig)
    assert (np.diff(order_w.values) >= -1e-12).all()


# --------------------------------------------------------------------------- #
# 5. NO LOOK-AHEAD — truncation invariance (signal + both constructions)
# --------------------------------------------------------------------------- #
def test_truncation_invariance_signal():
    daily = _synthetic_daily()
    full = xsmom.momentum_skip(daily)
    cut = full.dropna(how="all").index[3]
    trunc = xsmom.momentum_skip(daily.loc[:cut])
    pd.testing.assert_frame_equal(full.loc[trunc.index], trunc)


def test_truncation_invariance_constructions():
    daily = _synthetic_daily()
    cut = xsmom.momentum_skip(daily).dropna(how="all").index[3]
    for builder in (xsmom.tercile_weights, xsmom.rank_weights):
        full = builder(xsmom.momentum_skip(daily))
        trunc = builder(xsmom.momentum_skip(daily.loc[:cut]))
        pd.testing.assert_frame_equal(full.loc[trunc.index], trunc)


# --------------------------------------------------------------------------- #
# 6. NO LOOK-AHEAD — monthly position timing
# --------------------------------------------------------------------------- #
def test_positions_are_weights_shifted_one_month():
    daily = _synthetic_daily()
    w = xsmom.tercile_weights(xsmom.momentum_skip(daily))
    pos = xsmom.positions_from_weights(w)
    pd.testing.assert_frame_equal(pos, w.shift(1))
    assert pos.iloc[0].isna().all()


def test_position_uses_only_prior_month_data():
    """The weight decided at month-end T must be reproducible from data truncated
    at T — it cannot depend on anything after T."""
    daily = _synthetic_daily()
    sig = xsmom.momentum_skip(daily)
    w = xsmom.rank_weights(sig)
    t = w.dropna(how="all").index[5]
    w_trunc = xsmom.rank_weights(xsmom.momentum_skip(daily.loc[:t]))
    pd.testing.assert_series_equal(w.loc[t], w_trunc.loc[t])


# --------------------------------------------------------------------------- #
# 7. Confound variants
# --------------------------------------------------------------------------- #
def test_within_class_is_dollar_neutral():
    daily = _synthetic_daily(n_assets=14)
    cols = list(daily.columns)
    groups = {"G1": cols[:5], "G2": cols[5:9], "G3": cols[9:12], "G4": cols[12:14]}
    sig = xsmom.momentum_skip(daily)
    w = xsmom.within_class_rank_weights(sig, groups)
    row = w.dropna(how="all").iloc[-1]
    assert row.sum() == pytest.approx(0.0, abs=1e-12)        # dollar-neutral overall
    assert row[row > 0].sum() == pytest.approx(1.0, abs=1e-12)
    # each class is internally dollar-neutral too
    for members in groups.values():
        assert row[members].sum() == pytest.approx(0.0, abs=1e-12)


def test_demeaned_signal_truncation_invariance():
    """The demean uses an EXPANDING (backward-only) mean, so it must be
    truncation-invariant — a full-sample mean would fail this."""
    daily = _synthetic_daily()
    sig_full = xsmom.momentum_skip(daily)
    cut = sig_full.dropna(how="all").index[4]
    dm_full = xsmom.demeaned_signal(sig_full)
    dm_trunc = xsmom.demeaned_signal(xsmom.momentum_skip(daily.loc[:cut]))
    pd.testing.assert_frame_equal(dm_full.loc[dm_trunc.index], dm_trunc)
