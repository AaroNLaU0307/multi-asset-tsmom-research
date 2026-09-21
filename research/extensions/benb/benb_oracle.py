"""CTA-EDGE-02-BENB — the INDEPENDENT synthetic oracle.

This module imports **nothing** from the production engine: not `benb_engine`, not
`benb_feature`, not `benb_inference`, not `benb_classify`, not `benb_pipeline`, not
`benb_contract`. It reconstructs the expected value of every fixture from the fixture's
own definition, by a different route, with its own transcription of the sealed
constants.

Why it exists: twice in this programme an oracle reproduced the producer's own
misreading and agreed with a wrong engine (the VRP variation-margin sign; the
`VRP-DIAG-DEFECT-001` fixture). So this one takes a different road to the same numbers.

* The production feature differences **logs of endpoint levels**; the oracle works from
  the fixture's **declared per-day quantities** and computes the median with an
  explicit sort-and-middle rather than `statistics.median`.
* The production OLS uses centred sums of squares; the oracle solves the 2x2 normal
  equations by Cramer's rule.
* The production Sharpe uses a running variance; the oracle uses an explicit two-pass
  sum of squared deviations.

If the constants below ever disagree with `benb_contract`, `benb_tests` fails — which
is the point: a silent drift must break a test, not a run.
"""

from __future__ import annotations

import datetime as _dt
import math
from typing import Dict, List, Mapping, Sequence, Tuple

# Independently transcribed from BENB_PREREGISTRATION.md §D.3, §F, §H and BENB-OD-1.
ORACLE_MIN_PRIOR = 250
ORACLE_ONE_WAY_BPS = 5.0
ORACLE_ROUND_TRIP_BPS = 10.0
ORACLE_M1 = 0.0
ORACLE_M2 = 0.30
ORACLE_MONTHS_PER_YEAR = 12


def oracle_basis(p_close: float, nav: float) -> float:
    return math.log(p_close) - math.log(nav)


def oracle_median(values: Sequence[float]) -> float:
    """Explicit sort-and-middle. Deliberately not `statistics.median`."""
    v = sorted(values)
    n = len(v)
    if n == 0:
        raise ValueError("median of nothing")
    mid = n // 2
    return v[mid] if n % 2 == 1 else 0.5 * (v[mid - 1] + v[mid])


def oracle_features(p_close: Sequence[float], nav: Sequence[float],
                    min_prior: int = ORACLE_MIN_PRIOR):
    """(b, m, x) per index. `m` uses ONLY strictly earlier observations."""
    b = [oracle_basis(pc, nv) for pc, nv in zip(p_close, nav)]
    out = []
    for i in range(len(b)):
        if i >= min_prior:
            m = oracle_median(b[:i])          # strictly before i, by construction
            out.append((b[i], m, b[i] - m))
        else:
            out.append((b[i], None, None))
    return out


def oracle_components(p_close_t: float, p_open_t1: float, p_close_t1: float,
                      nav_t: float, nav_t1: float) -> Tuple[float, float, float, float]:
    """(R_ON, R_TR, R_NAV, delta_b) in natural log units."""
    r_on = math.log(p_open_t1) - math.log(p_close_t)
    r_tr = math.log(p_close_t1) - math.log(p_open_t1)
    r_nav = math.log(nav_t1) - math.log(nav_t)
    delta_b = oracle_basis(p_close_t1, nav_t1) - oracle_basis(p_close_t, nav_t)
    return r_on, r_tr, r_nav, delta_b


def oracle_ols(x: Sequence[float], y: Sequence[float]) -> Tuple[float, float]:
    """(intercept, slope) by Cramer's rule on the 2x2 normal equations.

    Deliberately a different algebraic route from the production centred-sums form.
    """
    n = float(len(x))
    sx = sum(x)
    sy = sum(y)
    sxx = sum(xi * xi for xi in x)
    sxy = sum(xi * yi for xi, yi in zip(x, y))
    det = n * sxx - sx * sx
    if det == 0.0:
        raise ValueError("singular design")
    intercept = (sy * sxx - sx * sxy) / det
    slope = (n * sxy - sx * sy) / det
    return intercept, slope


def oracle_net_trade_return_bps(r_tradable_bps: float) -> float:
    return r_tradable_bps - ORACLE_ROUND_TRIP_BPS


def oracle_month_grid(first: str, last: str) -> List[str]:
    y, m = int(first[:4]), int(first[5:7])
    y1, m1 = int(last[:4]), int(last[5:7])
    out = []
    while (y, m) <= (y1, m1):
        out.append("%04d-%02d" % (y, m))
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


def oracle_monthly(entry_months: Sequence[str], net_bps: Sequence[float],
                   grid: Sequence[str]) -> List[float]:
    """Zero months retained: a month with no trade contributes exactly 0.0."""
    out = []
    for g in grid:
        total = 0.0
        for em, v in zip(entry_months, net_bps):
            if em == g:
                total += v
        out.append(total)
    return out


def oracle_sharpe(monthly: Sequence[float]) -> float:
    """Two-pass mean / sample sd * sqrt(12), written longhand."""
    n = len(monthly)
    if n < 2:
        return float("nan")
    mean = sum(monthly) / n
    ss = 0.0
    for v in monthly:
        ss += (v - mean) * (v - mean)
    sd = math.sqrt(ss / (n - 1))
    if sd == 0.0:
        return float("nan")
    return mean / sd * math.sqrt(ORACLE_MONTHS_PER_YEAR)


def oracle_classify(L_T, U_T, L_O, U_O, L_N, U_N, L_R, U_R, L_S, U_S,
                    loyo_ok, is_evaluable=True) -> str:
    """The sealed §J.3 order, re-derived here from the contract text independently."""
    if not is_evaluable:
        return "F"
    if L_T <= 0.0:
        nav_neg = U_N < 0.0
        on_pos = L_O > 0.0
        if nav_neg and on_pos:
            return "A-M"
        if nav_neg:
            return "A"
        if on_pos:
            return "B"
        return "C1" if U_T <= 0.0 else "C2"
    if not loyo_ok:
        return "G"
    if (U_R <= ORACLE_M1) or (U_S <= ORACLE_M2):
        return "D"
    if (L_R > ORACLE_M1) and (L_S > ORACLE_M2):
        return "S"
    return "E"
