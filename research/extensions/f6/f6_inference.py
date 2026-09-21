# -*- coding: utf-8 -*-
"""CTA-EDGE-05 / F6 — (H) the sealed calendar-year block bootstrap.

Sealed, and not negotiable at build time:

```
blocks      15 complete calendar years, 2011..2025
B           100000
seed        2540719150
draw        the SAME year draw feeds P1 and P2 in each replication
weighting   P1 event-weighted · P2 session-weighted
interval    numpy.percentile(..., method="linear") at [2.5, 97.5]
```

No BCa, no studentization, no alternate interval, no alternate block scheme.

`B` may be reduced **only** for synthetic unit tests, and only through the
explicit `b=` argument of `bootstrap()`. `production_bootstrap()` takes no such
argument: it always uses the sealed `B`, so a test cannot silently become the
production path.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional, Sequence, Tuple

import numpy as np
import pandas as pd

import f6_contract as K
from f6_engine import SealedSpecViolation, point_estimates


def rng_for(seed: int = K.BOOTSTRAP_SEED_LITERAL) -> np.random.Generator:
    """Deterministic PCG64 via SeedSequence — the programme's existing choice."""
    return np.random.default_rng(np.random.SeedSequence(seed))


def year_blocks(frame: pd.DataFrame) -> Dict[int, np.ndarray]:
    """Row positions of each complete calendar-year block."""
    pos = {}
    yr = frame["year"].to_numpy()
    for y in sorted(set(int(v) for v in yr)):
        pos[y] = np.flatnonzero(yr == y)
    return pos


def replicate_rows(blocks: Dict[int, np.ndarray],
                   drawn: Sequence[int]) -> np.ndarray:
    """Concatenate the drawn year blocks, DUPLICATING a repeated year's rows.

    A year drawn k times contributes its rows k times, which is what makes the
    replicate session-weighted rather than year-weighted.
    """
    return np.concatenate([blocks[int(y)] for y in drawn])


def bootstrap(frame: pd.DataFrame, r_excess: np.ndarray, b: int,
              seed: int = K.BOOTSTRAP_SEED_LITERAL,
              years: Optional[Sequence[int]] = None,
              progress: Optional[Callable[[int], None]] = None
              ) -> Dict[str, Any]:
    """`b` replications. Pass the sealed B for production; smaller ONLY in tests."""
    blocks = year_blocks(frame)
    ys = sorted(blocks) if years is None else [int(y) for y in years]
    if len(ys) != len(blocks):
        raise SealedSpecViolation("year set does not match the frame")
    r = np.asarray(r_excess, float)
    g = rng_for(seed)
    k = len(ys)
    p1 = np.empty(b, float)
    p2 = np.empty(b, float)
    ys_arr = np.asarray(ys)
    for i in range(b):
        drawn = ys_arr[g.integers(0, k, size=k)]       # WITH replacement
        rows = replicate_rows(blocks, drawn)
        sub = frame.iloc[rows]
        # the SAME draw feeds both estimands in this replication
        a, c = point_estimates(sub, r[rows])
        p1[i] = a
        p2[i] = c
        if progress is not None and (i + 1) % 1000 == 0:
            progress(i + 1)
    return {"b": int(b), "seed": int(seed), "blocks": len(ys),
            "p1_draws": p1, "beta_event_draws": p2}


def production_bootstrap(frame: pd.DataFrame, r_excess: np.ndarray,
                         progress: Optional[Callable[[int], None]] = None
                         ) -> Dict[str, Any]:
    """The sealed production path. Takes NO `b` — B is always 100000."""
    return bootstrap(frame, r_excess, b=K.BOOTSTRAP_B,
                     seed=K.BOOTSTRAP_SEED_LITERAL, progress=progress)


def percentile_interval(draws: np.ndarray) -> Tuple[float, float]:
    """The ONE recorded quantile implementation. No software-default drift."""
    a = np.asarray(draws, float)
    if not np.isfinite(a).all():
        raise SealedSpecViolation(
            "non-finite bootstrap replicate. STOP and report; replicates are "
            "never silently dropped from the set.")
    lo, hi = np.percentile(a, [K.QUANTILE_LOWER * 100.0,
                               K.QUANTILE_UPPER * 100.0],
                           method=K.QUANTILE_METHOD)
    return float(lo), float(hi)


def classify_interval(lower: float, upper: float) -> str:
    """positive / unresolved / excluded_absent, by the sealed definitions."""
    if lower > 0.0:
        return K.CLASS_POSITIVE
    if upper <= 0.0:
        return K.CLASS_ABSENT
    return K.CLASS_UNRESOLVED


def summarize(draws: np.ndarray, point: float) -> Dict[str, Any]:
    lo, hi = percentile_interval(draws)
    return {"point": float(point), "lower": lo, "upper": hi,
            "klass": classify_interval(lo, hi),
            "interval": K.INTERVAL_WORDING,
            "quantile_implementation": K.QUANTILE_IMPLEMENTATION,
            "coverage_claim": "NOMINAL / APPROXIMATE. NOT exact finite-sample "
                              "95% coverage."}
