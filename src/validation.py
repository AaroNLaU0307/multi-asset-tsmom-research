"""Step 5b — honest validation: bootstrap CIs, regime/sub-period attribution,
Monte Carlo path risk. Standard methodology, implemented fresh here so the
project stays self-contained (no cross-project imports).

Determinism: all resampling uses a fixed seed (config.RANDOM_SEED).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

import config
from . import performance as perf


# --------------------------------------------------------------------------- #
# Bootstrap confidence intervals
# --------------------------------------------------------------------------- #
def bootstrap_ci(
    returns: pd.Series,
    stat: str = "sharpe",
    n: int = config.BOOTSTRAP_N,
    ci: float = config.CI_LEVEL,
    seed: int = config.RANDOM_SEED,
) -> dict[str, float]:
    """IID bootstrap of monthly returns. stat in {'sharpe','ann_return'}.

    Returns point estimate, [lo, hi] percentile CI, and the fraction of resamples
    above 0 (crucial for the 'does the CI cross 0?' question).
    """
    r = returns.dropna().to_numpy()
    rng = np.random.default_rng(seed)
    m = len(r)
    fn = perf.sharpe_ratio if stat == "sharpe" else perf.annual_return

    idx = rng.integers(0, m, size=(n, m))
    samples = r[idx]
    if stat == "sharpe":
        mean = samples.mean(axis=1)
        sd = samples.std(axis=1, ddof=1)
        with np.errstate(invalid="ignore", divide="ignore"):
            dist = np.where(sd > 0, mean / sd * np.sqrt(12), np.nan)
    else:  # ann_return (geometric)
        dist = (1.0 + samples).prod(axis=1) ** (12.0 / m) - 1.0
    dist = dist[~np.isnan(dist)]

    lo, hi = np.percentile(dist, [(100 - ci) / 2, 100 - (100 - ci) / 2])
    point = fn(returns)
    return {
        "stat": stat,
        "point": float(point),
        "lo": float(lo),
        "hi": float(hi),
        "frac_gt_0": float((dist > 0).mean()),
        "crosses_0": bool(lo < 0 < hi),
    }


# --------------------------------------------------------------------------- #
# Regime & sub-period attribution
# --------------------------------------------------------------------------- #
def regime_performance(returns: pd.Series, regimes: dict = config.REGIMES) -> pd.DataFrame:
    """Cumulative + annualized return and Sharpe within each named window."""
    rows = []
    for name, (start, end) in regimes.items():
        seg = returns.loc[start:end].dropna()
        if seg.empty:
            rows.append({"regime": name, "months": 0, "cum_return": np.nan,
                         "ann_return": np.nan, "sharpe": np.nan})
            continue
        rows.append({
            "regime": name,
            "months": len(seg),
            "cum_return": float((1 + seg).prod() - 1),
            "ann_return": perf.annual_return(seg),
            "sharpe": perf.sharpe_ratio(seg),
        })
    return pd.DataFrame(rows).set_index("regime")


def subperiod_performance(returns: pd.Series, block_years: int = 4) -> pd.DataFrame:
    """Walk-forward stability: metrics on consecutive non-overlapping blocks.

    No parameters are fit, so this tests whether the edge is stable across time
    rather than coming from a single lucky stretch.
    """
    r = returns.dropna()
    if r.empty:
        return pd.DataFrame()
    rows = []
    start_year = r.index.min().year
    end_year = r.index.max().year
    y = start_year
    while y <= end_year:
        block_end = y + block_years - 1
        seg = r.loc[f"{y}-01-01":f"{block_end}-12-31"]
        if len(seg) >= 6:
            rows.append({
                "period": f"{y}-{block_end}",
                "months": len(seg),
                "ann_return": perf.annual_return(seg),
                "ann_vol": float(seg.std(ddof=1) * np.sqrt(12)),
                "sharpe": perf.sharpe_ratio(seg),
                "max_drawdown": perf.max_drawdown(seg),
            })
        y += block_years
    return pd.DataFrame(rows).set_index("period")


def yearly_returns(returns: pd.Series) -> pd.Series:
    """Calendar-year compounded returns."""
    return returns.dropna().groupby(returns.dropna().index.year).apply(lambda s: (1 + s).prod() - 1)


# --------------------------------------------------------------------------- #
# Monte Carlo path risk
# --------------------------------------------------------------------------- #
def _path_stats(paths: np.ndarray) -> dict:
    """paths: (n_paths, horizon) of monthly returns. Returns DD/terminal stats."""
    equity = np.cumprod(1.0 + paths, axis=1)
    running_max = np.maximum.accumulate(equity, axis=1)
    dd = (equity / running_max - 1.0).min(axis=1)        # most negative per path
    terminal = equity[:, -1]
    return {
        "dd_median": float(np.median(dd)),
        "dd_p95": float(np.percentile(dd, 5)),           # 5th pct = a bad (deep) DD
        "dd_worst": float(dd.min()),
        "term_median": float(np.median(terminal)),
        "term_lo": float(np.percentile(terminal, 2.5)),
        "term_hi": float(np.percentile(terminal, 97.5)),
        "p_loss": float((terminal < 1.0).mean()),
        "p_dd_20": float((dd <= -0.20).mean()),
        "p_dd_30": float((dd <= -0.30).mean()),
    }


def monte_carlo(
    returns: pd.Series,
    n: int = config.MONTE_CARLO_N,
    seed: int = config.RANDOM_SEED,
) -> dict:
    """Two resampling schemes:
      * shuffle   — permute the realized months (preserves distribution, destroys
        ordering => sequence/path risk);
      * bootstrap — resample with replacement (sampling variability).
    Horizon = the realized sample length. Returns stats for both + bootstrap
    equity percentile bands for a fan chart.
    """
    r = returns.dropna().to_numpy()
    m = len(r)
    rng = np.random.default_rng(seed)

    # shuffle
    shuffled = np.array([rng.permutation(r) for _ in range(n)])
    # bootstrap
    boot = r[rng.integers(0, m, size=(n, m))]

    stats = {"shuffle": _path_stats(shuffled), "bootstrap": _path_stats(boot)}

    eq = np.cumprod(1.0 + boot, axis=1)
    pct = {p: np.percentile(eq, p, axis=0) for p in (5, 25, 50, 75, 95)}
    fan = pd.DataFrame(pct, index=returns.dropna().index)
    return {"stats": stats, "fan": fan, "horizon": m}
