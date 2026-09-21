"""CTA-EDGE-02-BENB — the ONE bootstrap family and the ONE fragility diagnostic.

Components L and M of the S2 build.

THE SEALED RECONSTRUCTION RULE (§G.2), implemented literally:

    x_t is computed ONCE, causally, on the TRUE chronology. The bootstrap then
    resamples complete CALENDAR-YEAR BLOCKS OF FROZEN OBSERVATION TUPLES. The
    expanding median is NEVER recomputed inside a replicate.

Recomputing it would be incoherent — a resample is a multiset of years in draw order,
so there is no well-defined prefix — and would introduce look-ahead into the bootstrap.
This module therefore takes `Observation` tuples, not prices, and cannot recompute the
feature even by accident: it never sees a `CellData`.

No HAC. No Newey-West. No second bootstrap. No episode-cluster bootstrap.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Mapping, Sequence

import numpy as np

import benb_contract as K
from benb_engine import (Observation, calendarised_sharpe, gate_one,
                         mean_net_trade_return_bps, monthly_series)


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
    return Interval(point,
                    float(np.percentile(vals, K.CI_LOWER_PCT)),
                    float(np.percentile(vals, K.CI_UPPER_PCT)),
                    int(vals.size), b)


@dataclass
class BootstrapResult:
    """Every quantity below shares ONE set of replicate draws (§G.1)."""
    years: List[int]
    replicates: int
    beta_T: Interval = None
    beta_O: Interval = None
    beta_N: Interval = None
    mean_net: Interval = None
    sharpe: Interval = None
    month_grid: List[str] = field(default_factory=list)


def group_by_year(obs: Sequence[Observation]) -> Dict[int, List[Observation]]:
    out: Dict[int, List[Observation]] = {}
    for o in obs:
        out.setdefault(o.year, []).append(o)
    return out


def year_block_bootstrap(obs: Sequence[Observation],
                         month_grid: Sequence[str],
                         b: int = K.BOOTSTRAP_B,
                         rng: np.random.Generator | None = None) -> BootstrapResult:
    """§G. Resample complete calendar years of FROZEN tuples, with replacement.

    The same draw row drives every statistic, so the five intervals are mutually
    consistent rather than five independent resamplings.
    """
    if rng is None:
        raise ValueError(
            "an explicit RNG is required; the seed is supplied by the S3 run "
            "authorisation and is never chosen from an outcome")
    by_year = group_by_year(obs)
    years = sorted(by_year)
    n = len(years)
    if n == 0:
        raise ValueError("no observations to bootstrap")
    draws = rng.integers(0, n, size=(b, n))

    g = gate_one(obs)
    point = {
        "beta_T": g.beta_T, "beta_O": g.beta_O, "beta_N": g.beta_N,
        "mean_net": mean_net_trade_return_bps(obs),
        "sharpe": calendarised_sharpe(monthly_series(obs, month_grid)),
    }
    acc: Dict[str, List[float]] = {k: [] for k in point}

    for row in draws:
        rep: List[Observation] = []
        for j in row:
            rep.extend(by_year[years[j]])
        try:
            gg = gate_one(rep)
            acc["beta_T"].append(gg.beta_T)
            acc["beta_O"].append(gg.beta_O)
            acc["beta_N"].append(gg.beta_N)
        except ValueError:
            for k in ("beta_T", "beta_O", "beta_N"):
                acc[k].append(float("nan"))
        acc["mean_net"].append(mean_net_trade_return_bps(rep))
        acc["sharpe"].append(calendarised_sharpe(monthly_series(rep, month_grid)))

    res = BootstrapResult(years=years, replicates=b, month_grid=list(month_grid))
    res.beta_T = _percentile_interval(point["beta_T"], acc["beta_T"], b)
    res.beta_O = _percentile_interval(point["beta_O"], acc["beta_O"], b)
    res.beta_N = _percentile_interval(point["beta_N"], acc["beta_N"], b)
    res.mean_net = _percentile_interval(point["mean_net"], acc["mean_net"], b)
    res.sharpe = _percentile_interval(point["sharpe"], acc["sharpe"], b)
    return res


# --------------------------------------------------------------------------- #
# M — leave-one-calendar-year-out. Exactly one fragility diagnostic.           #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class LoyoResult:
    per_year_beta_T: Dict[int, float]
    min_beta_T: float
    min_year: int
    passes: bool

    def as_dict(self) -> Dict[str, object]:
        return {"per_year_beta_T": {str(k): v for k, v
                                    in sorted(self.per_year_beta_T.items())},
                "min_beta_T": self.min_beta_T, "min_year": self.min_year,
                "passes": self.passes}


def leave_one_year_out(obs: Sequence[Observation]) -> LoyoResult:
    """§G.3. Drop one whole calendar year; re-estimate beta_T on the frozen tuples.

    PASS iff every leave-one-year-out point estimate is strictly > 0. This is a
    FRAGILITY gate on the point estimate, not a second interval and not a second
    hypothesis test. Exactly one fragility diagnostic exists.
    """
    by_year = group_by_year(obs)
    years = sorted(by_year)
    out: Dict[int, float] = {}
    for y in years:
        kept = [o for o in obs if o.year != y]
        try:
            out[y] = gate_one(kept).beta_T
        except ValueError:
            out[y] = float("nan")
    if not out:
        return LoyoResult({}, float("nan"), -1, False)
    min_year = min(out, key=lambda k: (np.nan_to_num(out[k], nan=np.inf)))
    min_beta = out[min_year]
    passes = all(np.isfinite(v) and v > 0.0 for v in out.values())
    return LoyoResult(out, min_beta, min_year, passes)
