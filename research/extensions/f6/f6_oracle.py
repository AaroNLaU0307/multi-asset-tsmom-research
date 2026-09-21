# -*- coding: utf-8 -*-
"""CTA-EDGE-05 / F6 — the INDEPENDENT oracle.

```
THIS MODULE IMPORTS NOTHING FROM THE PRODUCTION ENGINE.
```

It reaches every expected value by a **different route**:

* returns as `(p_t - p_prev) / p_prev`, not `p_t / p_prev - 1`;
* `rf_hold` with a different grouping of the same three constants;
* P1 by an explicit accumulate-and-divide loop, not `ndarray.mean`;
* `beta_EVENT` by **Frisch–Waugh–Lovell** partialling-out, not by solving the
  full nine-column system;
* and, for the exactly-linear fixtures, by **no estimator at all** — the true
  coefficient is a constant chosen in `f6_fixtures`, so agreement is a real
  check rather than two implementations sharing a bug.

That last route matters. Twice in this programme an oracle reproduced the
producer's own misreading and cheerfully agreed with a wrong engine.
"""

from __future__ import annotations

from typing import Any, Dict, List, Sequence

import numpy as np

# deliberately NOT importing f6_engine / f6_inference / f6_pipeline
from f6_contract import (CASH_DAYCOUNT, CASH_PERCENT_DIVISOR, ROUND_TRIP_COST,
                         WEEKDAY_INDICATORS)


def oracle_returns(prices: Sequence[float]) -> List[float]:
    """R via a difference quotient. `prices[0]` is the boundary observation."""
    out = []
    for i in range(1, len(prices)):
        prev = float(prices[i - 1])
        out.append((float(prices[i]) - prev) / prev)
    return out


def oracle_rf_hold(annual_percent: float, hold_days: int) -> float:
    """Same three constants, regrouped: a/(100*365) * h rather than (a/100)*(h/365)."""
    return float(annual_percent) / (CASH_PERCENT_DIVISOR * CASH_DAYCOUNT) * float(
        hold_days)


def oracle_excess(R: Sequence[float], rf: Sequence[float]) -> List[float]:
    return [float(a) - float(b) for a, b in zip(R, rf)]


def oracle_p1(r_excess: Sequence[float], event_flags: Sequence[int]) -> float:
    """Explicit accumulate-and-divide over EVENT rows. One session, one term."""
    total, n = 0.0, 0
    for v, e in zip(r_excess, event_flags):
        if e:
            total += float(v) - ROUND_TRIP_COST
            n += 1
    if n == 0:
        raise ZeroDivisionError("no event rows")
    return total / n


def oracle_beta_event_fwl(X: "np.ndarray | Any", y: Sequence[float],
                          columns: Sequence[str]) -> float:
    """Frisch-Waugh-Lovell: residualize EVENT on the other columns, then project.

    beta = <e_perp, y> / <e_perp, e_perp>, where e_perp is EVENT with every
    other regressor partialled out. Never solves the full system.
    """
    cols = list(columns)
    j = cols.index("EVENT")
    A = np.asarray(X, float)
    e = A[:, j]
    Z = np.delete(A, j, axis=1)
    g, *_ = np.linalg.lstsq(Z, e, rcond=None)
    e_perp = e - Z @ g
    denom = float(e_perp @ e_perp)
    if denom == 0.0:
        raise ZeroDivisionError("EVENT is in the span of the controls")
    return float(e_perp @ np.asarray(y, float)) / denom


def oracle_percentile(draws: Sequence[float], q: float) -> float:
    """Linear-interpolated order statistic, written out rather than delegated.

    numpy's `method="linear"` places the qth quantile at virtual index
    (n-1)*q and interpolates linearly between the bracketing order statistics.
    """
    a = sorted(float(v) for v in draws)
    n = len(a)
    if n == 0:
        raise ValueError("empty")
    pos = (n - 1) * float(q)
    lo = int(np.floor(pos))
    hi = int(np.ceil(pos))
    if lo == hi:
        return a[lo]
    frac = pos - lo
    return a[lo] * (1.0 - frac) + a[hi] * frac


def oracle_classify_interval(lower: float, upper: float) -> str:
    if lower > 0.0:
        return "positive"
    if upper <= 0.0:
        return "excluded_absent"
    return "unresolved"


def oracle_terminal(p1: str, p2: str, p3) -> str:
    """The sealed table, re-transcribed independently from the contract text."""
    if p1 == "excluded_absent":
        return "NOT_PROMOTED"
    if p1 == "positive":
        if p2 == "positive":
            return ("SUPPORTED_HISTORICAL_EDGE" if p3
                    else "ONE_YEAR_FRAGILITY / NOT_PROMOTED")
        if p2 == "unresolved":
            return "UNRESOLVED"
        return "POSITIVE_PAYOFF_NOT_ANNOUNCEMENT_SPECIFIC / NOT_PROMOTED"
    # p1 unresolved
    if p2 in ("positive", "unresolved"):
        return "UNRESOLVED"
    return "NOT_ANNOUNCEMENT_SPECIFIC / NOT_PROMOTED"


def golden_expectations(g: Dict[str, Any]) -> Dict[str, Any]:
    """Every expected value of the golden fixture, derived here, longhand."""
    R = oracle_returns(g["prices"])
    rf = [oracle_rf_hold(g["dgs3mo_annual_percent"], h) for h in g["hold_days"]]
    rx = oracle_excess(R, rf)
    p1 = oracle_p1(rx, g["event_flags"])
    r_net = [v - ROUND_TRIP_COST for v, e in zip(rx, g["event_flags"]) if e]
    return {"R": R, "rf_hold": rf, "r_excess": rx, "event_r_net": r_net,
            "p1_mean": p1, "n_events": sum(g["event_flags"])}
