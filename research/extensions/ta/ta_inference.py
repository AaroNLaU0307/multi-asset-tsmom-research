"""CTA-EDGE-01-TA — uncertainty and fragility.

Components J and K of the S2 build: the ONE sealed calendar-year block bootstrap
(§H) and the leave-one-year-out fragility gate (§G.4).

There is exactly one bootstrap family and exactly one fragility metric. No HAC, no
Newey-West, no parametric Sharpe inference, no week clustering, no second family, no
alternative annualisation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Mapping, Sequence

import numpy as np

import ta_contract as K
from ta_engine import EventResult, calendarised_sharpe, mean_net_ac


# --------------------------------------------------------------------------- #
# The sealed seed protocol — constants only, no data                           #
# --------------------------------------------------------------------------- #


def seed_children():
    """`SeedSequence(7).spawn(5)[4].spawn(2)` -> (primary, secondary)."""
    root = np.random.SeedSequence(K.SEED_ENTROPY).spawn(K.SEED_SPAWN_N)[K.SEED_CHILD_INDEX]
    kids = root.spawn(2)
    return kids[K.SEED_SUBSPAWN_PRIMARY], kids[K.SEED_SUBSPAWN_SECONDARY]


def primary_rng() -> np.random.Generator:
    return np.random.Generator(np.random.PCG64(seed_children()[0]))


def secondary_rng() -> np.random.Generator:
    return np.random.Generator(np.random.PCG64(seed_children()[1]))


# --------------------------------------------------------------------------- #
# J — the calendar-year block bootstrap                                        #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class Interval:
    point: float
    lower: float
    upper: float
    valid_replicates: int
    replicates: int

    def as_dict(self) -> Dict[str, object]:
        return {"point": self.point, "lower": self.lower, "upper": self.upper,
                "valid_replicates": self.valid_replicates,
                "replicates": self.replicates}


def _percentile_interval(point: float, draws: Sequence[float], b: int) -> Interval:
    vals = np.asarray([v for v in draws if np.isfinite(v)], dtype=float)
    if vals.size == 0:
        return Interval(point, float("nan"), float("nan"), 0, b)
    lo = float(np.percentile(vals, K.CI_LOWER_PCT))
    hi = float(np.percentile(vals, K.CI_UPPER_PCT))
    return Interval(point, lo, hi, int(vals.size), b)


@dataclass
class BootstrapResult:
    """Intervals for every quantity that shares ONE set of replicate draws."""
    year_set: List[int]
    replicates: int
    means: Dict[str, Interval] = field(default_factory=dict)
    sharpe: Interval | None = None


def year_block_bootstrap(year_set: Sequence[int],
                         per_year_values: Mapping[str, Mapping[int, Sequence[float]]],
                         per_year_months: Mapping[int, Sequence[float]] | None = None,
                         b: int = K.BOOTSTRAP_B,
                         rng: np.random.Generator | None = None) -> BootstrapResult:
    """§H.1–H.2. Resample COMPLETE calendar years with replacement.

    `per_year_values` maps a statistic name to {year -> the event values of that year};
    every such statistic is a mean and shares the SAME draws. `per_year_months`, when
    given, maps {year -> that year's months of the calendarised grid, zero months
    INCLUDED}; each replicate rebuilds the whole monthly series by concatenating the
    drawn years' month blocks in draw order, then computes the calendarised Sharpe.
    """
    years = list(year_set)
    n = len(years)
    rng = rng if rng is not None else primary_rng()
    idx = rng.integers(0, n, size=(b, n))

    point_means = {}
    for name, by_year in per_year_values.items():
        flat = [v for y in years for v in by_year.get(y, ())]
        point_means[name] = float(np.mean(flat)) if flat else float("nan")
    point_sharpe = float("nan")
    if per_year_months is not None:
        full = [v for y in years for v in per_year_months.get(y, ())]
        point_sharpe = calendarised_sharpe(full)

    draws: Dict[str, List[float]] = {name: [] for name in per_year_values}
    sharpe_draws: List[float] = []
    arrays = {name: {y: np.asarray(by_year.get(y, ()), dtype=float) for y in years}
              for name, by_year in per_year_values.items()}
    month_arrays = ({y: np.asarray(per_year_months.get(y, ()), dtype=float)
                     for y in years} if per_year_months is not None else None)

    for row in idx:
        drawn = [years[j] for j in row]
        for name in per_year_values:
            parts = [arrays[name][y] for y in drawn if arrays[name][y].size]
            draws[name].append(float(np.concatenate(parts).mean()) if parts
                               else float("nan"))
        if month_arrays is not None:
            parts = [month_arrays[y] for y in drawn if month_arrays[y].size]
            series = np.concatenate(parts) if parts else np.asarray([])
            sharpe_draws.append(calendarised_sharpe(series.tolist()))

    res = BootstrapResult(year_set=years, replicates=b)
    for name in per_year_values:
        res.means[name] = _percentile_interval(point_means[name], draws[name], b)
    if per_year_months is not None:
        res.sharpe = _percentile_interval(point_sharpe, sharpe_draws, b)
    return res


# --------------------------------------------------------------------------- #
# K — leave-one-year-out fragility                                             #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class LoyoResult:
    per_year_mean_net: Dict[int, float]
    per_year_sharpe: Dict[int, float]
    min_mean_net: float
    min_year: int
    passes: bool

    def as_dict(self) -> Dict[str, object]:
        return {"per_year_mean_net_ac_bps": {str(k): v for k, v
                                             in sorted(self.per_year_mean_net.items())},
                "per_year_calendarised_sharpe": {str(k): v for k, v
                                                 in sorted(self.per_year_sharpe.items())},
                "min_mean_net_ac_bps": self.min_mean_net,
                "min_year": self.min_year, "passes": self.passes}


def leave_one_year_out(results: Sequence[EventResult],
                       monthly_by_year: Mapping[int, Sequence[float]],
                       year_set: Sequence[int]) -> LoyoResult:
    """§G.4. Drop one whole calendar year at a time.

    The GATE is the sign of mean NET AC, and nothing else: PASS iff every one of the
    LOYO estimates is strictly greater than zero. The LOYO calendarised Sharpe is
    computed and reported alongside but is NOT part of the gate — exactly one
    fragility metric exists.
    """
    means: Dict[int, float] = {}
    sharpes: Dict[int, float] = {}
    for y in year_set:
        kept = [r for r in results if r.year != y]
        means[y] = mean_net_ac(kept)
        series = [v for yy in year_set if yy != y
                  for v in monthly_by_year.get(yy, ())]
        sharpes[y] = calendarised_sharpe(series)
    min_year = min(means, key=lambda k: means[k]) if means else -1
    min_mean = means[min_year] if means else float("nan")
    return LoyoResult(per_year_mean_net=means, per_year_sharpe=sharpes,
                      min_mean_net=min_mean, min_year=min_year,
                      passes=bool(means) and all(v > 0.0 for v in means.values()))


# --------------------------------------------------------------------------- #
# helpers for grouping by calendar year                                        #
# --------------------------------------------------------------------------- #


def group_values_by_year(results: Sequence[EventResult],
                         attr: str) -> Dict[int, List[float]]:
    out: Dict[int, List[float]] = {}
    for r in results:
        out.setdefault(r.year, []).append(getattr(r, attr))
    return out


def group_months_by_year(month_keys: Sequence[str],
                         monthly: Sequence[float]) -> Dict[int, List[float]]:
    """{year -> that year's months of the grid, zero months INCLUDED and in order}."""
    out: Dict[int, List[float]] = {}
    for key, value in zip(month_keys, monthly):
        out.setdefault(int(key[:4]), []).append(value)
    return out
