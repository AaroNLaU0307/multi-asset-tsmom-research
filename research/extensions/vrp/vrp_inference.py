# -*- coding: utf-8 -*-
"""TSMOM-VRP-01 - module J: the sealed inference engine (section J, reused X01 6.1).

    family        stationary bootstrap (Politis & Romano 1994): geometric block lengths,
                  CIRCULAR WRAP, replicate length equal to the sample length
    block         expected 12 months (p = 1/12); not re-derived, no alternative computed
    replicates    10,000
    interval      PERCENTILE, 2.5th and 97.5th, numpy linear interpolation. No BCa.
    Stage A       A* = 12 * mean( r_A* ) per replicate
    Stage B       the aligned triple (r_book, r_core, r_SPY) is resampled JOINTLY in
                  common time blocks; q*, T* and D* are recomputed INSIDE each replicate
    validity      Stage A: invalid iff the replicate contains fewer than 24 distinct
                  calendar months.
                  Stage B: invalid iff |T*| < ceil( 0.5 * |T_full| ) - THE TAIL COUNT
                  ONLY, never the value of D*.
    floor         the run is valid iff >= 9,500 of 10,000 replicates are valid. Invalid
                  replicates are COUNTED AND REPORTED, never replaced, never selectively
                  re-drawn. No sign clipping anywhere. A floor failure is a VRP-VALIDITY
                  failure of inference (mechanical), NOT a state.
    seed          master 7; numpy.random.SeedSequence(7).spawn(4) in the fixed order
                  [Stage A historical, Stage B historical, VRP-A-PROSPECTIVE,
                  VRP-B-PROSPECTIVE]; Generator(PCG64(child)).

MECHANICAL_IMPLEMENTATION_DETAIL (section J leaves it open; it cannot change the
estimand): within each block the generator is drawn from in the order the contract lists
them - the geometric block length first, then the uniform start index. Both are
independent draws from fixed distributions, so the law of the bootstrap distribution is
identical under either order; only the particular realised stream differs. Recorded here
rather than treated as an Owner decision.
"""
from __future__ import annotations

import math
from typing import Callable, Dict, List, NamedTuple, Optional, Sequence, Tuple

import numpy as np

from vrp_constants import (CI_LOWER_PCT, CI_UPPER_PCT, SEED_SPAWN_ORDER,
                           STAGE_A_MIN_DISTINCT_MONTHS, block, floor, reps, seed)

P_BLOCK = 1.0 / block


class Interval(NamedTuple):
    point: float
    lower: float
    upper: float
    valid_replicates: int
    invalid_replicates: int
    floor_met: bool
    stream: str


def spawn_generators() -> Dict[str, np.random.Generator]:
    """The four sealed child streams, in the sealed order."""
    children = np.random.SeedSequence(seed).spawn(len(SEED_SPAWN_ORDER))
    return {name: np.random.Generator(np.random.PCG64(child))
            for name, child in zip(SEED_SPAWN_ORDER, children)}


def spawned_entropy() -> List[Dict[str, object]]:
    """The spawned entropy values, for the seal-manifest cross-check (acceptance 16)."""
    children = np.random.SeedSequence(seed).spawn(len(SEED_SPAWN_ORDER))
    return [{"name": name, "entropy": int(c.entropy), "spawn_key": tuple(c.spawn_key)}
            for name, c in zip(SEED_SPAWN_ORDER, children)]


def stationary_bootstrap_indices(n: int, rng: np.random.Generator) -> np.ndarray:
    """One stationary-bootstrap index replicate of length `n`, circular wrap."""
    out = np.empty(n, dtype=np.int64)
    filled = 0
    while filled < n:
        L = int(rng.geometric(P_BLOCK))          # block length first (see module docstring)
        start = int(rng.integers(0, n))          # then the start index
        take = min(L, n - filled)
        idx = (start + np.arange(take)) % n
        out[filled:filled + take] = idx
        filled += take
    return out


# --------------------------------------------------------------------------- #
# Stage A
# --------------------------------------------------------------------------- #
def stage_a_interval(monthly_returns: Sequence[float],
                     stream: str = "stage_a_historical",
                     n_reps: int = reps) -> Interval:
    """Percentile interval for A = 12 * mean(r_A)."""
    x = np.asarray(list(monthly_returns), dtype=np.float64)
    n = x.size
    if n == 0:
        raise ValueError("no months")
    rng = spawn_generators()[stream]
    stats: List[float] = []
    invalid = 0
    for _ in range(n_reps):
        idx = stationary_bootstrap_indices(n, rng)
        if np.unique(idx).size < STAGE_A_MIN_DISTINCT_MONTHS:
            invalid += 1                          # counted, NEVER replaced or re-drawn
            continue
        stats.append(12.0 * float(x[idx].mean()))
    valid = len(stats)
    arr = np.asarray(stats, dtype=np.float64)
    lower = float(np.percentile(arr, CI_LOWER_PCT, method="linear")) if valid else float("nan")
    upper = float(np.percentile(arr, CI_UPPER_PCT, method="linear")) if valid else float("nan")
    return Interval(point=12.0 * float(x.mean()), lower=lower, upper=upper,
                    valid_replicates=valid, invalid_replicates=invalid,
                    floor_met=valid >= floor, stream=stream)


# --------------------------------------------------------------------------- #
# Stage B
# --------------------------------------------------------------------------- #
def stage_b_interval(r_book: Sequence[float],
                     r_core: Sequence[float],
                     r_spy: Sequence[float],
                     quantile: float = 0.10,
                     stream: str = "stage_b_historical",
                     n_reps: int = reps) -> Interval:
    """Percentile interval for D = mean_{t in T}( r_book - r_core ), with the tail set
    RECOMPUTED inside every replicate from the jointly resampled triple."""
    b = np.asarray(list(r_book), dtype=np.float64)
    c = np.asarray(list(r_core), dtype=np.float64)
    sp = np.asarray(list(r_spy), dtype=np.float64)
    if not (b.size == c.size == sp.size):
        raise ValueError("the aligned triple must have equal length")
    n = b.size
    q_full = float(np.quantile(sp, quantile, method="linear"))
    t_full = int(np.sum(sp <= q_full))
    if t_full == 0:
        raise ValueError("empty full-sample tail set")
    min_tail = math.ceil(0.5 * t_full)

    rng = spawn_generators()[stream]
    stats: List[float] = []
    invalid = 0
    for _ in range(n_reps):
        idx = stationary_bootstrap_indices(n, rng)
        bs, cs, ss = b[idx], c[idx], sp[idx]
        q_star = float(np.quantile(ss, quantile, method="linear"))
        mask = ss <= q_star
        if int(mask.sum()) < min_tail:            # TAIL COUNT ONLY, never D*'s value
            invalid += 1
            continue
        stats.append(float(np.mean(bs[mask] - cs[mask])))
    valid = len(stats)
    arr = np.asarray(stats, dtype=np.float64)
    lower = float(np.percentile(arr, CI_LOWER_PCT, method="linear")) if valid else float("nan")
    upper = float(np.percentile(arr, CI_UPPER_PCT, method="linear")) if valid else float("nan")
    full_mask = sp <= q_full
    return Interval(point=float(np.mean(b[full_mask] - c[full_mask])),
                    lower=lower, upper=upper,
                    valid_replicates=valid, invalid_replicates=invalid,
                    floor_met=valid >= floor, stream=stream)


def denominator_sign_stability(r_core: Sequence[float],
                               r_spy: Sequence[float],
                               quantile: float = 0.10,
                               stream: str = "stage_b_historical",
                               n_reps: int = reps) -> float:
    """Fraction of VALID replicates in which mean_T*(r_core) keeps one sign (section I.4)."""
    c = np.asarray(list(r_core), dtype=np.float64)
    sp = np.asarray(list(r_spy), dtype=np.float64)
    n = c.size
    q_full = float(np.quantile(sp, quantile, method="linear"))
    min_tail = math.ceil(0.5 * int(np.sum(sp <= q_full)))
    full_sign = math.copysign(1.0, float(np.mean(c[sp <= q_full])))
    rng = spawn_generators()[stream]
    same = total = 0
    for _ in range(n_reps):
        idx = stationary_bootstrap_indices(n, rng)
        cs, ss = c[idx], sp[idx]
        mask = ss <= float(np.quantile(ss, quantile, method="linear"))
        if int(mask.sum()) < min_tail:
            continue
        total += 1
        if math.copysign(1.0, float(np.mean(cs[mask]))) == full_sign:
            same += 1
    return (same / total) if total else 0.0


class FloorFailure(RuntimeError):
    """The 9,500 valid-replicate floor was not met: a VRP-VALIDITY failure of inference
    (Class 1, mechanical), never a result state."""


def enforce_floor(interval: Interval) -> Interval:
    if not interval.floor_met:
        raise FloorFailure(
            "valid-replicate floor not met on stream %s: %d valid of %d (floor %d). "
            "This is a VRP-VALIDITY failure of inference, not a state."
            % (interval.stream, interval.valid_replicates,
               interval.valid_replicates + interval.invalid_replicates, floor))
    return interval
