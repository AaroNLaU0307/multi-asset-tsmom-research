"""Family-level statistics + mechanism decomposition for the multi-universe study.

New, self-contained (the repo had no DSR/PSR utility). Three blocks:

1. **Multiple-comparison control** — Benjamini–Hochberg FDR across the 5 headline tests.
2. **Selection control** — Probabilistic + Deflated Sharpe Ratio (Bailey & López de Prado
   2012, 2014): "the best of N trials — is it real after selection?"
3. **Mechanism decomposition** — the Lo–MacKinlay (1990) / Lewellen (2002) WRSS momentum
   profit split into own-autocovariance, lead-lag and cross-sectional dispersion, with
   block-bootstrap CIs.

Determinism: all resampling uses ``config.RANDOM_SEED``.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.stats import norm

import config
from . import performance as perf, validation

_EULER_GAMMA = 0.5772156649015329

# Moving-block-bootstrap block length for the decomposition CIs (months). Chosen a-priori,
# NOT tuned to the result. Rationale: it must exceed the lag-1 horizon the decomposition
# targets (so each block preserves the cross-autocovariance structure), and 12 months
# captures up to a full year of serial dependence in monthly returns — conservative vs the
# lighter L ≈ T^(1/3) ≈ 6 rule of thumb for T ≈ 218 (Politis-White). The qualitative
# conclusion (every term2 CI contains 0) is insensitive to 6 vs 12.
DECOMP_BLOCK_MONTHS = 12


# --------------------------------------------------------------------------- #
# 1. Benjamini–Hochberg FDR
# --------------------------------------------------------------------------- #
def benjamini_hochberg(pvalues: list[float], alpha: float = 0.05) -> dict:
    """BH-FDR control across a family of tests.

    Returns ``reject`` (bool per test, original order), BH-adjusted ``qvalues`` and the
    ``threshold`` p-value below which tests are rejected. A test is rejected iff its raw
    p ≤ the largest p_(k) satisfying p_(k) ≤ (k/m)·alpha.
    """
    p = np.asarray(pvalues, dtype=float)
    m = len(p)
    order = np.argsort(p)
    ranked = p[order]
    thresh_line = (np.arange(1, m + 1) / m) * alpha
    below = ranked <= thresh_line
    if below.any():
        k = np.max(np.where(below)[0])           # largest rank (0-based) passing
        threshold = ranked[k]
    else:
        threshold = -np.inf
    reject = p <= threshold
    # BH-adjusted q-values (monotone from the largest p down)
    q_ranked = ranked * m / np.arange(1, m + 1)
    q_ranked = np.minimum.accumulate(q_ranked[::-1])[::-1]
    q_ranked = np.clip(q_ranked, 0, 1)
    qvalues = np.empty(m)
    qvalues[order] = q_ranked
    return {"reject": reject.tolist(), "qvalues": qvalues.tolist(),
            "threshold": float(threshold), "alpha": alpha}


# --------------------------------------------------------------------------- #
# 2. Probabilistic + Deflated Sharpe Ratio (Bailey & López de Prado)
# --------------------------------------------------------------------------- #
def _per_period_sharpe_moments(returns: pd.Series) -> tuple[float, int, float, float]:
    """Return (per-period Sharpe, n, skew, kurtosis[non-excess])."""
    r = returns.dropna().to_numpy()
    n = len(r)
    sd = r.std(ddof=1)
    sr = r.mean() / sd if sd > 0 else 0.0
    m = r - r.mean()
    skew = (np.mean(m**3) / sd**3) if sd > 0 else 0.0
    kurt = (np.mean(m**4) / sd**4) if sd > 0 else 3.0      # Pearson (normal = 3)
    return float(sr), n, float(skew), float(kurt)


def probabilistic_sharpe_ratio(returns: pd.Series, sr_benchmark: float = 0.0) -> float:
    """PSR(SR*) = P(true per-period Sharpe > sr_benchmark) (Bailey-LdP 2012), adjusting
    for sample length and the return distribution's skew/kurtosis.

    ``sr_benchmark`` is in PER-PERIOD (here monthly) Sharpe units, matching the estimate."""
    sr, n, skew, kurt = _per_period_sharpe_moments(returns)
    if n < 2:
        return float("nan")
    denom = np.sqrt(max(1e-12, 1.0 - skew * sr + (kurt - 1.0) / 4.0 * sr**2))
    return float(norm.cdf((sr - sr_benchmark) * np.sqrt(n - 1) / denom))


def expected_max_sharpe(trial_sharpes: list[float], n_trials: int | None = None) -> float:
    """Expected MAXIMUM per-period Sharpe across ``n_trials`` independent trials under the
    null of zero true Sharpe (Bailey-LdP 2014):

        E[max SR] ≈ √V · [ (1−γ)·Z⁻¹(1 − 1/N) + γ·Z⁻¹(1 − 1/(N·e)) ]

    where V = variance of the trials' Sharpe estimates and γ is Euler-Mascheroni. This is
    the deflation benchmark for the DSR."""
    s = np.asarray(trial_sharpes, dtype=float)
    N = int(n_trials if n_trials is not None else len(s))
    V = s.var(ddof=1) if len(s) > 1 else 0.0
    if V <= 0 or N < 2:
        return 0.0
    z1 = norm.ppf(1.0 - 1.0 / N)
    z2 = norm.ppf(1.0 - 1.0 / (N * np.e))
    return float(np.sqrt(V) * ((1.0 - _EULER_GAMMA) * z1 + _EULER_GAMMA * z2))


def deflated_sharpe_ratio(best_returns: pd.Series, trial_sharpes: list[float],
                          n_trials: int | None = None) -> dict:
    """DSR (Bailey-LdP 2014): PSR of the BEST trial against the expected-max-under-null
    benchmark. DSR > 0.95 ⇒ the best of N trials is statistically significant after
    accounting for selection across the N trials and the return moments.

    ``trial_sharpes`` are the per-period Sharpes of all trials (used to estimate the
    cross-trial Sharpe variance); ``best_returns`` is the best trial's return series."""
    sr_star = expected_max_sharpe(trial_sharpes, n_trials)
    dsr = probabilistic_sharpe_ratio(best_returns, sr_benchmark=sr_star)
    return {"dsr": dsr, "sr_star": sr_star, "psr_vs0": probabilistic_sharpe_ratio(best_returns, 0.0)}


# --------------------------------------------------------------------------- #
# Bootstrap Sharpe-vs-0 p-value (reuses the engine's bootstrap_ci)
# --------------------------------------------------------------------------- #
def sharpe_pvalue_vs0(returns: pd.Series) -> float:
    """Two-sided bootstrap p-value for H0: Sharpe = 0, derived from the engine's
    ``validation.bootstrap_ci`` resample distribution (``frac_gt_0``). Deterministic."""
    ci = validation.bootstrap_ci(returns, stat="sharpe")
    frac = ci["frac_gt_0"]
    return float(2.0 * min(frac, 1.0 - frac))


# --------------------------------------------------------------------------- #
# 3. Lo–MacKinlay / Lewellen WRSS momentum-profit decomposition
# --------------------------------------------------------------------------- #
@dataclass
class Decomp:
    n_assets: int
    term1_autocov: float        # (N-1)/N^2 * tr(Gamma_1)   — own-autocorrelation
    term2_leadlag: float        # (1/N^2) * sum_offdiag(Gamma_1) — lead-lag (enters as -term2)
    term3_dispersion: float     # sigma^2_mu                — cross-sectional dispersion of means
    profit_reconstructed: float  # term1 - term2 + term3
    profit_realized: float       # realized mean WRSS momentum profit (validation)


def _lag1_autocov(returns: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    """Lag-1 cross-autocovariance matrix Gamma_1 (Gamma_1[i,j] = Cov(r_{i,t-1}, r_{j,t}))
    and the per-asset sample means, on a complete (no-NaN) return panel."""
    R = returns.to_numpy()
    mu = R.mean(axis=0)
    X = R[:-1] - mu            # r_{t-1}
    Y = R[1:] - mu             # r_{t}
    gamma1 = X.T @ Y / (len(R) - 1)
    return gamma1, mu


def lo_mackinlay_decomposition(returns: pd.DataFrame) -> Decomp:
    """Decompose the WRSS momentum profit (weights w_{i,t} = (1/N)(r_{i,t-1} − r̄_{t-1}))
    into the three pre-registered terms. Algebraic identity (derived in the study):

        E[π_momentum] = (N−1)/N²·tr(Γ₁) − (1/N²)·Σ_{i≠j}(Γ₁)_{ij} + σ²_μ
                      =        term1        −        term2          + term3

    term1 = own-autocovariance (the source TSMOM also harvests); term2 = lead-lag
    (XSMOM-only, enters with a MINUS); term3 = cross-sectional dispersion of means
    (static-premium suspect). ``profit_realized`` recomputes the strategy's mean profit
    directly as an implementation check.

    NOTE: this is the canonical *lag-1* (1-month) mechanism diagnostic of the universe's
    return structure — complementary to, not identical with, the 12-1 headline strategy.
    """
    R = returns.dropna(how="any")
    N = R.shape[1]
    gamma1, mu = _lag1_autocov(R)
    tr = np.trace(gamma1)
    offdiag = gamma1.sum() - tr
    term1 = (N - 1) / N**2 * tr
    term2 = offdiag / N**2
    term3 = float(np.var(mu, ddof=0))            # population cross-sectional variance of means
    recon = term1 - term2 + term3

    # realized WRSS momentum profit: w_t = (1/N)(r_{t-1} - mean(r_{t-1})), pi_t = w_t . r_t
    A = R.to_numpy()
    past = A[:-1]
    fut = A[1:]
    w = (past - past.mean(axis=1, keepdims=True)) / N
    realized = float((w * fut).sum(axis=1).mean())
    return Decomp(N, float(term1), float(term2), term3, float(recon), realized)


def decomposition_block_bootstrap(returns: pd.DataFrame, block: int = DECOMP_BLOCK_MONTHS,
                                  n: int = 2000, seed: int = config.RANDOM_SEED) -> dict:
    """Moving-block bootstrap CIs for the three decomposition terms. Blocks of ``block``
    contiguous months (default ``DECOMP_BLOCK_MONTHS`` = 12, justified at module top) keep the
    cross-sectional + serial structure intact (the lag-1 structure is only distorted at the
    few block joins — disclosed). Returns point estimate + 95% CI per term.

    The honesty caveat (pre-registered): Γ₁ has N(N−1) off-diagonals from ~218 months, so at
    large N term2 has WIDE CIs and should be read qualitatively (sign + rough magnitude).
    """
    R = returns.dropna(how="any")
    T = len(R)
    point = lo_mackinlay_decomposition(R)
    rng = np.random.default_rng(seed)
    n_blocks = int(np.ceil(T / block))
    keys = ("term1_autocov", "term2_leadlag", "term3_dispersion")
    dist = {k: np.empty(n) for k in keys}
    for b in range(n):
        starts = rng.integers(0, T - block + 1, size=n_blocks)
        idx = np.concatenate([np.arange(s, s + block) for s in starts])[:T]
        d = lo_mackinlay_decomposition(R.iloc[idx])
        for k in keys:
            dist[k][b] = getattr(d, k)
    out = {"point": point}
    for k in keys:
        lo, hi = np.percentile(dist[k], [2.5, 97.5])
        out[k] = {"point": float(getattr(point, k)), "lo": float(lo), "hi": float(hi)}
    return out


def term2_contains_zero(decomp_ci: dict) -> bool:
    """True iff the term2 (lead-lag) block-bootstrap CI brackets 0 — i.e. the XSMOM-only
    lead-lag channel is NOT statistically distinguishable from zero."""
    d = decomp_ci["term2_leadlag"]
    return bool(d["lo"] <= 0.0 <= d["hi"])


def term2_precision(decomp_ci: dict) -> dict:
    """Honesty fork (study §C1): is term2 *confidently small* or merely *imprecisely
    estimated*?

    Compares the most extreme magnitude term2's CI admits (``max(|lo|, |hi|)``) to ``|term1|``
    — both in the same units, so the ratio is scale-free. We may only claim "confidently
    small" if the CI contains 0 **and** even its favourable end stays below |term1| (so term2
    cannot rival the shared autocorrelation term). Otherwise term2 is "imprecise": not shown
    to be non-trivial, but NOT shown to be ~0 either. We never force the strong verdict.
    """
    t1 = abs(decomp_ci["term1_autocov"]["point"])
    d2 = decomp_ci["term2_leadlag"]
    max_mag = max(abs(d2["lo"]), abs(d2["hi"]))
    contains0 = bool(d2["lo"] <= 0.0 <= d2["hi"])
    confident = contains0 and t1 > 0 and max_mag < t1
    return {"contains_zero": contains0, "max_magnitude": float(max_mag), "abs_term1": float(t1),
            "ci_vs_term1": float(max_mag / t1) if t1 > 0 else float("inf"),
            "verdict": "confidently small" if confident else "imprecise"}
