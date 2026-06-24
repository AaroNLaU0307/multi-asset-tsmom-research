"""Tests for the drawdown-attribution diagnostic (descriptive layer).

Fragile pieces worth pinning:
  1. RECONCILIATION — the per-asset PnL decomposition must sum EXACTLY to the
     engine's portfolio net (the Step-1 gate; attributing on an unverified
     decomposition is forbidden).
  2. ADDITIVITY — the chop/crash buckets must sum to each episode's (and each
     sleeve's) decline-phase PnL.
  3. EPISODE DEPTH — peak->trough depth on a constructed equity curve.
  4. CAUSALITY — the Step-5 regime variables must be look-ahead free
     (truncation invariance).

Synthetic data only (no network / no cached files), per repo convention.

Run:  python -m pytest -q
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import universe  # noqa: E402
from src import attribution as A, regime as R  # noqa: E402


def _synth_universe(seed: int = 7, years: int = 8) -> pd.DataFrame:
    """Deterministic daily price panel for all 17 universe tickers (random walks
    with mildly varied drift/vol so the strategy produces real drawdowns)."""
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2004-01-01", periods=years * 252)
    out = {}
    for i, c in enumerate(universe.TICKERS):
        steps = rng.normal(0.0002 + 0.00004 * i, 0.008 + 0.0004 * i, size=len(idx))
        out[c] = 100.0 * np.exp(np.cumsum(steps))
    return pd.DataFrame(out, index=idx)


# --------------------------------------------------------------------------- #
# 1. Reconciliation gate — decomposition is additive == engine
# --------------------------------------------------------------------------- #
def test_decomposition_reconciles_with_engine():
    dec = A.decompose(_synth_universe())
    diff = (dec["port_net"] - dec["engine_net"]).abs().max()
    assert diff < 1e-12, f"decomposition does not reconcile with engine: {diff}"
    rec = A.reconcile(dec)
    assert rec["ok"]
    assert rec["n"] > 0


# --------------------------------------------------------------------------- #
# 2. Chop/crash buckets are additive (sum to the decline-phase PnL)
# --------------------------------------------------------------------------- #
def test_chop_crash_buckets_are_additive():
    px = _synth_universe()
    dec = A.decompose(px)
    eps = A.flag_episodes(A.find_episodes(dec["port_net"]))
    flagged = eps[eps["flagged"]] if eps["flagged"].any() else eps
    assert not flagged.empty, "synthetic data produced no drawdown episodes"

    ep_cc, asset_cc = A.chop_vs_crash(dec, flagged, px)
    net_i = dec["net_i"]
    for r in ep_cc.itertuples():
        win = net_i[(net_i.index > r.peak_date) & (net_i.index <= r.trough_date)]
        total = float(win.sum(min_count=1).sum())
        assert abs((r.crash_contrib + r.chop_contrib) - total) < 1e-10

    agg = A.aggregate_chop_crash(ep_cc, asset_cc)
    ps = agg["per_sleeve"]
    assert np.allclose((ps["crash_contrib"] + ps["chop_contrib"]).to_numpy(),
                       ps["net_contrib"].to_numpy(), atol=1e-10)
    # The crash/chop SHARE is only well-defined when both buckets are losses (a
    # sleeve can net positive during portfolio declines on random data, which makes
    # the ratio meaningless — guard for that). Where both are adverse, share ∈ [0,1].
    both_loss = (ps["crash_contrib"] <= 0) & (ps["chop_contrib"] <= 0)
    s = ps.loc[both_loss, "crash_share"].dropna()
    assert ((s >= -1e-9) & (s <= 1 + 1e-9)).all()


# --------------------------------------------------------------------------- #
# 3. Episode depth on a constructed curve
# --------------------------------------------------------------------------- #
def test_find_episodes_depth_and_recovery():
    # +10%, then three -10% months, then recover above the prior peak.
    idx = pd.date_range("2010-01-31", periods=6, freq="ME")
    r = pd.Series([0.10, -0.10, -0.10, -0.10, 0.20, 0.20], index=idx)
    eps = A.find_episodes(r, min_depth=0.01)
    assert len(eps) == 1
    ep = eps.iloc[0]
    # peak eq = 1.1; trough = 1.1*0.9^3 = 0.8019  -> depth = 0.8019/1.1 - 1 ~ -0.271
    assert ep["depth"] < -0.25
    assert ep["recovered"]
    assert ep["decline_months"] == 3


# --------------------------------------------------------------------------- #
# 4. Efficiency ratio — known values
# --------------------------------------------------------------------------- #
def test_efficiency_ratio_known():
    ramp = pd.Series(np.arange(10, dtype=float))            # clean trend -> 1.0
    assert abs(A.efficiency_ratio(ramp) - 1.0) < 1e-12
    zig = pd.Series([0, 1, 0, 1, 0, 1, 0, 1.0])            # pure chop -> small
    assert A.efficiency_ratio(zig) < 0.2


# --------------------------------------------------------------------------- #
# 5. Step-5 regime variables are causal (truncation invariance)
# --------------------------------------------------------------------------- #
def test_regime_variables_are_causal():
    px = _synth_universe()
    full = R.build_panel(px)
    cut = px.index[int(len(px) * 0.7)]
    trunc = R.build_panel(px.loc[:cut])
    common = trunc.index.intersection(full.index)
    assert len(common) > 0
    a = full.loc[common, trunc.columns]
    b = trunc.loc[common, trunc.columns]
    assert float(np.nanmax((a - b).abs().to_numpy())) < 1e-12
