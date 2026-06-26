"""Cross-Sectional Momentum (XSMOM) — signal + portfolio-construction layers.

SCOPE: the THREE new layers only (signal, cross-sectional ranking, dollar-neutral
long-short construction). NO returns, NO Sharpe, NO portfolio vol targeting — those
reuse the TSMOM engine verbatim (``src/performance.py``, ``src/portfolio.py``,
``src/validation.py``). This module never modifies the engine.

What XSMOM is (vs the TSMOM in ``signals.py``)
----------------------------------------------
* TSMOM = *time-series* (absolute) momentum: each asset judged against ITS OWN
  past — sign of its trailing return. Long-only-able book can be net long/short.
* XSMOM = *cross-sectional* (relative-strength) momentum: each asset judged
  against THE OTHERS this month — rank, then long the top, short the bottom.
  Dollar-neutral by construction (Sigma w_long = +1, Sigma w_short = -1).

Signal (12-1, explicit skip-month)
-----------------------------------
``signal_{i,t} = P_{i, t-SKIP} / P_{i, t-FORM} - 1`` — the cumulative return from
~12 months ago to ~1 month ago, SKIPPING the most recent month. Pure arithmetic on
past closes (two ``shift``s look strictly backward), so it is look-ahead free by
construction; truncation invariance is unit-tested in ``tests/test_xsmom.py``.

No look-ahead
-------------
The signal at month-end ``M`` uses only daily closes ``<= M`` (resampled with
``.last()``). The position for the FOLLOWING month is the weight decided at the
previous month-end (``positions = weights.shift(1)``), exactly as in the TSMOM
layers. Both properties are unit-tested.

Anti-overfitting
----------------
Lookback (12-1), terciles (6/6) and the rank-weight scheme are academic
conventions fixed in ``xsmom_config.py`` and NOT tuned for a better curve.
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import pandas as pd

import config
import xsmom_config as xcfg


# --------------------------------------------------------------------------- #
# 1. Signal — 12-1 cross-sectional momentum with an explicit skip-month
# --------------------------------------------------------------------------- #
def momentum_skip(
    daily_prices: pd.DataFrame,
    skip_days: int = xcfg.SKIP_DAYS,
    formation_days: int = xcfg.LOOKBACK_DAYS,
    rule: str = config.SIGNAL_RESAMPLE,
) -> pd.DataFrame:
    """Month-end 12-1 momentum panel: ``P_{t-skip} / P_{t-formation} - 1``.

    Computed on the DAILY price grid (two backward ``shift``s => no look-ahead) and
    then sampled at each month-end (``.resample(rule).last()`` => the decision-time
    value as of the last trading day of the month). NaN until ``formation_days``
    prior closes exist for an asset (per-column history is respected — no
    cross-asset row dropping). Mirrors ``sizing.volatility_at_month_end``'s
    "rolling daily quantity, sampled at month-end" pattern.
    """
    if not 0 <= skip_days < formation_days:
        raise ValueError("require 0 <= skip_days < formation_days")
    mom_daily = daily_prices.shift(skip_days) / daily_prices.shift(formation_days) - 1.0
    return mom_daily.resample(rule).last()


# --------------------------------------------------------------------------- #
# 2. Cross-sectional rank
# --------------------------------------------------------------------------- #
def cross_sectional_rank(
    signal_monthly: pd.DataFrame, method: str = xcfg.RANK_METHOD
) -> pd.DataFrame:
    """Ordinal rank of each asset against the others, per month (1 = worst, N =
    best). NaN signals (insufficient history) stay NaN and are excluded from the
    ranking that month — so the rank set is always over the *available* names."""
    return signal_monthly.rank(axis=1, method=method)


# --------------------------------------------------------------------------- #
# 3a. HEADLINE construction — tercile (long top, short bottom, equal weight)
# --------------------------------------------------------------------------- #
def tercile_weights(
    signal_monthly: pd.DataFrame,
    n_long: int = xcfg.N_LONG,
    n_short: int = xcfg.N_SHORT,
) -> pd.DataFrame:
    """Long the top ``n_long`` names (+1/n_long each), short the bottom ``n_short``
    (-1/n_short each), middle flat. Dollar-neutral: Sigma w_long = +1,
    Sigma w_short = -1, Sigma w = 0 — *imposed* at the construction layer, not
    emergent. No intra-leg vol weighting (deliberate — see the study README).

    A month is only built when at least ``n_long + n_short`` names are rankable;
    warm-up months with fewer live assets get an all-NaN (no-book) row, so the
    book is never a different, smaller strategy (mirrors the TSMOM "full-universe
    only" evaluation discipline). Ties are broken deterministically (stable sort
    by signal, then column order) so the build is reproducible.
    """
    cols = signal_monthly.columns
    out: list[pd.Series] = []
    for t, row in signal_monthly.iterrows():
        s = row.dropna()
        w = pd.Series(0.0, index=cols)
        if len(s) < n_long + n_short:
            out.append(pd.Series(np.nan, index=cols))
            continue
        # stable sort => deterministic tie-break (continuous floats rarely tie).
        order = s.sort_values(ascending=False, kind="mergesort")
        w[order.index[:n_long]] = 1.0 / n_long
        w[order.index[-n_short:]] = -1.0 / n_short
        out.append(w)
    return pd.DataFrame(out, index=signal_monthly.index, columns=cols)


# --------------------------------------------------------------------------- #
# 3b. ROBUSTNESS construction — rank-weight (Lo-MacKinlay continuous weights)
# --------------------------------------------------------------------------- #
def rank_weights(signal_monthly: pd.DataFrame, method: str = xcfg.RANK_METHOD) -> pd.DataFrame:
    """Continuous version: ``raw_i = rank_i - mean_rank`` (the Lo-MacKinlay weight,
    which auto-sums to zero), then normalise the positive side to sum +1 and the
    negative side to sum -1. Uses all rankable names, smoother turnover, and ties
    directly to the cross-sectional profit decomposition.

    Dollar-neutral and gross = 2 by construction. The median name (raw == 0) gets
    zero weight. Warm-up rows with no rankable name are NaN (no book).
    """
    ranks = signal_monthly.rank(axis=1, method=method)          # NaN where signal NaN
    mean_rank = ranks.mean(axis=1)                              # over available names
    raw = ranks.sub(mean_rank, axis=0)                         # sums to ~0 per row

    pos = raw.clip(lower=0.0)
    neg = raw.clip(upper=0.0)
    pos_sum = pos.sum(axis=1)
    neg_sum = neg.sum(axis=1).abs()
    w_long = pos.div(pos_sum.where(pos_sum > 0), axis=0)        # sums to +1
    w_short = neg.div(neg_sum.where(neg_sum > 0), axis=0)       # sums to -1

    w = w_long.add(w_short, fill_value=0.0)
    w = w.where(signal_monthly.notna(), 0.0)                   # unavailable -> not in book
    all_nan = signal_monthly.isna().all(axis=1)
    w.loc[all_nan, :] = np.nan                                 # warm-up -> no book
    return w[signal_monthly.columns]


# --------------------------------------------------------------------------- #
# 4. Position timing (no look-ahead) — same convention as the TSMOM layers
# --------------------------------------------------------------------------- #
def positions_from_weights(weights_monthly: pd.DataFrame) -> pd.DataFrame:
    """Position held during month M+1 = weight decided at month-end M
    (``weights.shift(1)``). A weight set at a month-end close is only applied from
    the next month onward — strictly no look-ahead."""
    return weights_monthly.shift(1)


# --------------------------------------------------------------------------- #
# 5. Confound-decomposition variants (appendix robustness — see README §confound)
# The cross-asset universe has a confound: structurally different long-run mean
# returns across asset classes (equities > bonds, 2007-2026). Baseline XSMOM will
# on average long equities / short bonds, part of which is static equity risk
# premium disguised as momentum. These two variants test whether the edge SURVIVES
# once that static tilt is removed.
# --------------------------------------------------------------------------- #
def within_class_rank_weights(
    signal_monthly: pd.DataFrame,
    groups: dict[str, Sequence[str]],
    method: str = xcfg.RANK_METHOD,
) -> pd.DataFrame:
    """Confound (a) — within-asset-class ranking. Rank each asset ONLY against its
    own class (equities vs equities, bonds vs bonds, ...), build a dollar-neutral
    rank-weight book *inside* each class, then combine classes with equal gross.

    Because every class is internally dollar-neutral, the aggregate is too, and the
    cross-class static-premium tilt (long equities / short bonds) is removed by
    construction — only WITHIN-class relative strength survives. Classes with two
    names (FX, real estate) reduce to long-1 / short-1.
    """
    cols = signal_monthly.columns
    n_groups = len(groups)
    combined = pd.DataFrame(0.0, index=signal_monthly.index, columns=cols)
    any_book = pd.Series(False, index=signal_monthly.index)
    for members in groups.values():
        members = [m for m in members if m in cols]
        if len(members) < 2:
            continue
        sub = rank_weights(signal_monthly[members], method=method)   # internally +1/-1
        # equal gross across classes: each class contributes 1/n_groups of total gross.
        sub = sub / n_groups
        combined[members] = combined[members].add(sub.fillna(0.0), fill_value=0.0)
        any_book = any_book | sub.notna().any(axis=1)
    combined.loc[~any_book, :] = np.nan
    return combined


def demeaned_signal(
    signal_monthly: pd.DataFrame, min_periods: int = 1
) -> pd.DataFrame:
    """Confound (b) — demeaned signal. Subtract each asset's OWN long-run mean
    momentum before ranking, removing the asset-level bias (an asset that
    structurally trends up always ranks high). What remains is each asset's
    deviation from its own norm — dynamic relative strength, not static drift.

    The "long-run mean" is the **ex-ante expanding mean** (data <= t only) — the
    only look-ahead-free choice; a full-sample mean would peek. Truncation
    invariance is therefore preserved and unit-tested.
    """
    expanding_mean = signal_monthly.expanding(min_periods=min_periods).mean()
    return signal_monthly - expanding_mean


# --------------------------------------------------------------------------- #
# Convenience: daily prices -> decision-time weight panel for a named spec
# --------------------------------------------------------------------------- #
def build_weights(
    daily_prices: pd.DataFrame,
    spec: str = "tercile",
    skip_days: int = xcfg.SKIP_DAYS,
    formation_days: int = xcfg.LOOKBACK_DAYS,
    groups: dict[str, Sequence[str]] | None = None,
) -> dict[str, pd.DataFrame]:
    """End-to-end signal -> dollar-neutral weight panel.

    spec:
      'tercile'      -> headline tercile (long 6 / short 6, equal weight)
      'rank'         -> rank-weight (Lo-MacKinlay continuous)
      'within_class' -> confound (a): within-class rank-weight (needs ``groups``)
      'demean'       -> confound (b): rank-weight on the demeaned signal

    Returns {'signal', 'weight', 'position'} where position = weight.shift(1).
    """
    sig = momentum_skip(daily_prices, skip_days, formation_days)
    if spec == "tercile":
        w = tercile_weights(sig)
    elif spec == "rank":
        w = rank_weights(sig)
    elif spec == "within_class":
        if groups is None:
            raise ValueError("spec='within_class' requires groups=")
        w = within_class_rank_weights(sig, groups)
    elif spec == "demean":
        w = rank_weights(demeaned_signal(sig))
    else:
        raise ValueError(f"unknown spec {spec!r}")
    return {"signal": sig, "weight": w, "position": positions_from_weights(w)}
