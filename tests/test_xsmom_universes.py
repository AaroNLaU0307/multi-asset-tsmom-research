"""Tests for the multi-universe XSMOM Phase-2 additions.

Priorities:
  1. Family-stats correctness — BH-FDR against a worked example, PSR/DSR monotonicity.
  2. Mechanism decomposition — the Lo-MacKinlay split must RECONSTRUCT the realized WRSS
     momentum profit (validates the term signs and algebra), and must localise to the right
     term in constructed dispersion / lead-lag panels.
  3. No look-ahead carries through the per-universe pipeline.

Run:  python -m pytest -q
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import xsmom as xs                      # noqa: E402
from src import xsmom_stats as xst               # noqa: E402
import xsmom_universes as uni                    # noqa: E402


# --------------------------------------------------------------------------- #
# 1. Benjamini–Hochberg FDR
# --------------------------------------------------------------------------- #
def test_bh_fdr_worked_example():
    # m=5, alpha=0.05; thresholds k/m*alpha = .01 .02 .03 .04 .05
    p = [0.001, 0.008, 0.039, 0.041, 0.9]
    out = xst.benjamini_hochberg(p, alpha=0.05)
    # 0.001<=.01 and 0.008<=.02 pass; 0.039>.03 fails -> reject the two smallest only
    assert out["reject"] == [True, True, False, False, False]
    assert abs(out["threshold"] - 0.008) < 1e-12


def test_bh_fdr_qvalues_monotone_and_order_preserved():
    p = [0.9, 0.001, 0.041, 0.008, 0.039]          # shuffled
    out = xst.benjamini_hochberg(p, alpha=0.05)
    assert out["reject"] == [False, True, False, True, False]
    q = np.array(out["qvalues"])
    # q sorted by p must be non-decreasing
    assert (np.diff(q[np.argsort(p)]) >= -1e-12).all()
    assert (q <= 1.0).all()


def test_bh_fdr_none_pass():
    out = xst.benjamini_hochberg([0.2, 0.3, 0.5, 0.7, 0.9], alpha=0.05)
    assert out["reject"] == [False] * 5


# --------------------------------------------------------------------------- #
# 2. Probabilistic / Deflated Sharpe
# --------------------------------------------------------------------------- #
def _normal_returns(mean, sd, n, seed=0):
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2008-01-31", periods=n, freq="ME")
    return pd.Series(rng.normal(mean, sd, n), index=idx)


def test_psr_zero_sharpe_is_half():
    # PSR(0) measures P(true SR > 0) from the SAMPLE Sharpe; demean so the realized
    # sample Sharpe is exactly 0 -> PSR(0) = Phi(0) = 0.5 regardless of skew/kurtosis.
    r = _normal_returns(0.0, 0.04, 600, seed=1)
    r = r - r.mean()
    assert xst.probabilistic_sharpe_ratio(r, 0.0) == pytest.approx(0.5, abs=1e-9)


def test_psr_increases_with_sharpe_and_length():
    weak = _normal_returns(0.004, 0.04, 200, seed=2)
    strong = _normal_returns(0.012, 0.04, 200, seed=2)
    assert xst.probabilistic_sharpe_ratio(strong, 0.0) > xst.probabilistic_sharpe_ratio(weak, 0.0)
    short = _normal_returns(0.008, 0.04, 60, seed=3)
    long = _normal_returns(0.008, 0.04, 400, seed=3)
    assert xst.probabilistic_sharpe_ratio(long, 0.0) > xst.probabilistic_sharpe_ratio(short, 0.0)


def test_expected_max_sharpe_grows_with_trials_and_variance():
    sr = [0.0, 0.1, 0.2, -0.1, 0.15]
    assert xst.expected_max_sharpe(sr, n_trials=20) > xst.expected_max_sharpe(sr, n_trials=5)
    wide = [-0.4, 0.0, 0.4, -0.2, 0.2]
    assert xst.expected_max_sharpe(wide, 5) > xst.expected_max_sharpe(sr, 5)


def test_dsr_deflates_below_psr_when_selection_matters():
    best = _normal_returns(0.012, 0.04, 200, seed=4)
    trials = [0.30, 0.10, -0.05, 0.18, 0.22]         # dispersed trial Sharpes
    out = xst.deflated_sharpe_ratio(best, trials, n_trials=5)
    assert out["sr_star"] > 0
    assert out["dsr"] <= out["psr_vs0"] + 1e-9        # deflation never raises significance


# --------------------------------------------------------------------------- #
# 3. Lo–MacKinlay decomposition
# --------------------------------------------------------------------------- #
def _panel(arr, cols=None):
    idx = pd.date_range("2000-01-31", periods=len(arr), freq="ME")
    cols = cols or [f"A{i}" for i in range(arr.shape[1])]
    return pd.DataFrame(arr, index=idx, columns=cols)


def test_decomposition_reconstructs_realized_profit():
    rng = np.random.default_rng(7)
    # random panel with mild structure; recon must equal realized WRSS profit
    R = _panel(rng.normal(0.005, 0.05, size=(5000, 6)))
    d = xs.momentum_skip  # noqa: F841  (ensure module import path is the package one)
    dec = xst.lo_mackinlay_decomposition(R)
    assert dec.profit_reconstructed == pytest.approx(dec.profit_realized, rel=0.02, abs=1e-6)


def test_dispersion_localises_to_term3():
    rng = np.random.default_rng(11)
    T, N = 4000, 5
    drifts = np.array([-0.01, -0.005, 0.0, 0.005, 0.01])    # distinct static means
    R = _panel(drifts + rng.normal(0.0, 0.03, size=(T, N)))  # iid noise, no autocorr
    dec = xst.lo_mackinlay_decomposition(R)
    # term3 (dispersion) dominates; autocov/lead-lag terms are ~0
    assert dec.term3_dispersion > 0
    assert dec.term3_dispersion > 10 * abs(dec.term1_autocov)
    assert dec.term3_dispersion > 10 * abs(dec.term2_leadlag)


def test_leadlag_shows_up_in_term2():
    rng = np.random.default_rng(13)
    T = 4000
    a = rng.normal(0.0, 0.04, T)
    b_follows_a = np.empty(T)
    b_follows_a[0] = 0.0
    b_follows_a[1:] = 0.8 * a[:-1] + rng.normal(0.0, 0.01, T - 1)   # B lags A strongly
    R = _panel(np.column_stack([a, b_follows_a]), cols=["A", "B"])
    iid = _panel(rng.normal(0.0, 0.04, size=(T, 2)), cols=["A", "B"])
    lead = xst.lo_mackinlay_decomposition(R)
    flat = xst.lo_mackinlay_decomposition(iid)
    assert abs(lead.term2_leadlag) > 5 * abs(flat.term2_leadlag)    # lead-lag inflates term2


def test_decomposition_block_bootstrap_ci_brackets_point():
    rng = np.random.default_rng(5)
    R = _panel(rng.normal(0.004, 0.05, size=(218, 9)))     # study-sized sample
    out = xst.decomposition_block_bootstrap(R, block=12, n=300)
    for k in ("term1_autocov", "term2_leadlag", "term3_dispersion"):
        assert out[k]["lo"] <= out[k]["point"] <= out[k]["hi"]


def test_decomp_block_constant_is_documented_default():
    # A3: the block length is a named, justified constant (not a bare literal) and the
    # bootstrap uses it by default.
    assert isinstance(xst.DECOMP_BLOCK_MONTHS, int) and xst.DECOMP_BLOCK_MONTHS >= 2
    rng = np.random.default_rng(9)
    R = _panel(rng.normal(0.003, 0.04, size=(120, 5)))
    out = xst.decomposition_block_bootstrap(R, n=200)       # no block= -> uses the constant
    assert "term2_leadlag" in out


def _ci(t1, lo, hi):
    return {"term1_autocov": {"point": t1, "lo": t1, "hi": t1},
            "term2_leadlag": {"point": (lo + hi) / 2, "lo": lo, "hi": hi},
            "term3_dispersion": {"point": 0.0, "lo": 0.0, "hi": 0.0}}


def test_term2_contains_zero():
    assert xst.term2_contains_zero(_ci(1.0, -0.5, 0.8)) is True
    assert xst.term2_contains_zero(_ci(1.0, 0.2, 0.9)) is False    # CI strictly positive


def test_term2_precision_fork():
    # confidently small: CI contains 0 AND its extreme magnitude < |term1|
    conf = xst.term2_precision(_ci(100.0, -5.0, 5.0))
    assert conf["contains_zero"] and conf["verdict"] == "confidently small"
    # imprecise: CI contains 0 but admits magnitudes >= |term1|
    imp = xst.term2_precision(_ci(10.0, -50.0, 50.0))
    assert imp["contains_zero"] and imp["verdict"] == "imprecise"
    # excludes 0 -> never 'confidently small' (it is non-zero, just imprecise about size)
    exc = xst.term2_precision(_ci(100.0, 5.0, 50.0))
    assert (not exc["contains_zero"]) and exc["verdict"] == "imprecise"


# --------------------------------------------------------------------------- #
# 4. No look-ahead carries through the per-universe pipeline
# --------------------------------------------------------------------------- #
def test_universe_pipeline_truncation_invariant():
    rng = np.random.default_rng(3)
    days = 1008
    idx = pd.bdate_range("2016-01-01", periods=days)
    cols = [f"T{i:02d}" for i in range(9)]                  # U1-sized universe
    px = pd.DataFrame(100 * np.exp(np.cumsum(rng.normal(0.0003, 0.01, (days, 9)), 0)),
                      index=idx, columns=cols)
    n_side = uni.tercile_n_side(9)
    full = xs.tercile_weights(xs.momentum_skip(px), n_long=n_side, n_short=n_side)
    cut = full.dropna(how="all").index[3]
    trunc = xs.tercile_weights(xs.momentum_skip(px.loc[:cut]), n_long=n_side, n_short=n_side)
    pd.testing.assert_frame_equal(full.loc[trunc.index], trunc)


def test_tercile_n_side_matches_family():
    assert uni.tercile_n_side(9) == 3
    assert uni.tercile_n_side(18) == 6
    assert uni.tercile_n_side(6) == 2
    assert uni.tercile_n_side(7) == 2
