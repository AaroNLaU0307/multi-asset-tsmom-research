# -*- coding: utf-8 -*-
"""CTA-EDGE-05 / F6 — (D) returns, (E) cash mapping, (F) P1, (G) P2, (I) LOYO.

Pure functions over arrays and frames. Nothing here opens a file, so nothing
here can reach a real price on its own: the caller supplies prices, and the only
real-price supplier is `f6_data.load_price_values`, which is guarded.

Every scientific constant comes from `f6_contract`. There is no CLI default, no
keyword that changes a promotion-relevant setting, and no fallback anywhere.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd

import f6_contract as K


class SealedSpecViolation(RuntimeError):
    """A sealed requirement cannot be met. Deterministic STOP, never repaired."""


class UnexplainedCashGap(RuntimeError):
    """DGS3MO gap with no source explanation -> IMPLEMENTATION HOLD."""


# --------------------------------------------------------------------------- #
# (E) cash proxy mapping                                                      #
# --------------------------------------------------------------------------- #
def map_cash_rate(benchmark: pd.Timestamp, vdates: pd.DatetimeIndex,
                  values: Dict[pd.Timestamp, float],
                  rows_present: set) -> Tuple[float, int]:
    """Last official observation dated ON OR BEFORE `benchmark`.

    Carry is permitted ONLY across source-explained non-publication: a weekend,
    or a date the official file itself carries as a row (i.e. published-as-
    missing). A business day with NO row in the source is an UNEXPLAINED GAP and
    raises. There is deliberately no day threshold — the sealed contract rejects
    the unsourced 7-day rule.
    """
    j = vdates.searchsorted(benchmark, side="right") - 1
    if j < 0:
        raise UnexplainedCashGap(
            "no %s observation at or before %s" % (K.CASH_SERIES, benchmark.date()))
    src = vdates[j]
    k = src + pd.Timedelta(days=1)
    while k <= benchmark:
        if k.weekday() < 5 and k not in rows_present:
            raise UnexplainedCashGap(
                "IMPLEMENTATION HOLD: %s has no row for business day %s between "
                "the last observation %s and the benchmark date %s. Do not "
                "substitute another cash series and do not widen the carry."
                % (K.CASH_SERIES, k.date(), src.date(), benchmark.date()))
        k += pd.Timedelta(days=1)
    return float(values[src]), int((benchmark - src).days)


def rf_hold(annual_percent: float, hold_calendar_days: int) -> float:
    """rf_hold(d) = DGS3MO/100 * HOLD(d) / 365.

    The /365 divisor is OWNER-CHOSEN and must NEVER be attributed to Treasury,
    H.15 or FRED.
    """
    return (annual_percent / K.CASH_PERCENT_DIVISOR) * (
        float(hold_calendar_days) / K.CASH_DAYCOUNT)


# --------------------------------------------------------------------------- #
# (D) return construction                                                     #
# --------------------------------------------------------------------------- #
def simple_returns(prices: pd.Series, grid: pd.DatetimeIndex,
                   prev: Sequence[pd.Timestamp]) -> np.ndarray:
    """R(d) = AdjClose(d) / AdjClose(prev(d)) - 1."""
    cur = prices.reindex(grid).to_numpy(float)
    pri = prices.reindex(pd.DatetimeIndex(prev)).to_numpy(float)
    if not np.isfinite(cur).all() or not np.isfinite(pri).all():
        raise SealedSpecViolation(
            "missing price on a required date. STOP: do not interpolate, do not "
            "skip the session, do not shift the window.")
    return cur / pri - 1.0


def excess_returns(R: np.ndarray, rf: np.ndarray) -> np.ndarray:
    """r_excess(d) = R(d) - rf_hold(d)."""
    return R - rf


def net_event_returns(r_excess_event: np.ndarray) -> np.ndarray:
    """r_net(t) = r_excess(t) - 0.0004, charged on EVENT sessions only."""
    return r_excess_event - K.ROUND_TRIP_COST


# --------------------------------------------------------------------------- #
# frame construction                                                          #
# --------------------------------------------------------------------------- #
def build_frame(grid: pd.DatetimeIndex, boundary: pd.Timestamp,
                event_sessions: set, tom: np.ndarray,
                auction: set) -> pd.DataFrame:
    """The sealed P2 population: EVERY session in the grid, NO row dropped.

    `boundary` supplies prev() for the first row and is never itself a row.
    """
    prev = [boundary] + list(grid[:-1])
    f = pd.DataFrame(index=grid)
    f["prev"] = prev
    f["EVENT"] = [1 if d.strftime("%Y-%m-%d") in event_sessions else 0
                  for d in grid]
    f["weekday"] = [d.day_name() for d in grid]
    f["TOM"] = np.asarray(tom, dtype=int)
    f["HOLD"] = [(d - p).days for d, p in zip(grid, prev)]
    f["AUCTION"] = [1 if d in auction else 0 for d in grid]
    f["year"] = grid.year
    if boundary in set(f.index):
        raise SealedSpecViolation(
            "the opening boundary session %s became a regression row; it is an "
            "INPUT BOUNDARY OBSERVATION only" % boundary.date())
    if (f["HOLD"] <= 0).any():
        raise SealedSpecViolation("non-positive HOLD")
    bad_years = sorted(set(f["year"]) & set(K.PROHIBITED_YEARS))
    if bad_years:
        raise SealedSpecViolation(
            "PROHIBITED YEAR(S) %s entered the design. 2026 carries no F6 "
            "outcome quantity." % bad_years)
    return f


# --------------------------------------------------------------------------- #
# (G) the ONE fixed P2 model                                                  #
# --------------------------------------------------------------------------- #
def design_matrix(frame: pd.DataFrame) -> pd.DataFrame:
    """Exactly the sealed nine columns, in the sealed order, Friday omitted.

    The reference level is NOT inferred from the data and NOT produced by a
    library `drop_first`: it is pinned, so a library default cannot drift it.
    """
    X = pd.DataFrame(index=frame.index)
    X["const"] = 1.0
    X["EVENT"] = frame["EVENT"].to_numpy(float)
    for w in K.WEEKDAY_INDICATORS:
        X["weekday_" + w] = (frame["weekday"] == w).to_numpy(float)
    for c in ("TOM", "HOLD", "AUCTION"):
        X[c] = frame[c].to_numpy(float)
    if tuple(X.columns) != K.DESIGN_COLUMNS:
        raise SealedSpecViolation(
            "design columns %s != sealed %s" % (tuple(X.columns),
                                                K.DESIGN_COLUMNS))
    seen = set(frame["weekday"].unique())
    omitted = sorted(seen - set(K.WEEKDAY_INDICATORS))
    if omitted and omitted != [K.WEEKDAY_REFERENCE]:
        raise SealedSpecViolation(
            "weekday reference must be exactly %r; got omitted levels %s"
            % (K.WEEKDAY_REFERENCE, omitted))
    return X


def check_design_rank(X: pd.DataFrame) -> int:
    """Full column rank or STOP. No column dropping, no ridge, no repair."""
    A = X.to_numpy(float)
    r = int(np.linalg.matrix_rank(A))
    if r != A.shape[1]:
        raise SealedSpecViolation(
            "P2 design matrix is RANK DEFICIENT (rank %d of %d columns). STOP. "
            "The sealed contract forbids dropping a column, regularizing, or "
            "substituting a fallback model." % (r, A.shape[1]))
    return r


def ols_beta_event(X: pd.DataFrame, y: np.ndarray,
                   check_rank: bool = True) -> float:
    """beta_EVENT from the one fixed OLS. No HC, no cluster, no weights."""
    if check_rank:
        check_design_rank(X)
    A = X.to_numpy(float)
    coef, *_ = np.linalg.lstsq(A, np.asarray(y, float), rcond=None)
    return float(coef[list(X.columns).index("EVENT")])


# --------------------------------------------------------------------------- #
# (F) P1                                                                      #
# --------------------------------------------------------------------------- #
def p1_mean(r_net_event: np.ndarray) -> float:
    """EVENT-WEIGHTED arithmetic mean of r_net.

    One eligible session contributes exactly one observation, whatever number of
    family labels it carries. No annual equal weighting, no family equal
    weighting.
    """
    a = np.asarray(r_net_event, float)
    if a.size == 0:
        raise SealedSpecViolation("P1 over an empty event set")
    return float(a.mean())


def point_estimates(frame: pd.DataFrame, r_excess: np.ndarray
                    ) -> Tuple[float, float]:
    """(P1 mean, P2 beta_EVENT) on a given population — the shared kernel."""
    ev = frame["EVENT"].to_numpy(bool)
    p1 = p1_mean(net_event_returns(np.asarray(r_excess, float)[ev]))
    p2 = ols_beta_event(design_matrix(frame), r_excess)
    return p1, p2


# --------------------------------------------------------------------------- #
# (I) P3 — leave-one-calendar-year-out                                        #
# --------------------------------------------------------------------------- #
def loyo(frame: pd.DataFrame, r_excess: np.ndarray,
         years: Optional[Sequence[int]] = None) -> Dict[str, Any]:
    """Delete one complete calendar year at a time; refit the identical objects.

    P3 PASS only if BOTH point estimates are STRICTLY > 0 for EVERY deletion.
    No deletion-specific significance requirement is computed, because none
    exists in the sealed contract.
    """
    ys = sorted(set(int(y) for y in frame["year"])) if years is None else list(years)
    r = np.asarray(r_excess, float)
    per: Dict[int, Dict[str, float]] = {}
    for y in ys:
        keep = (frame["year"] != y).to_numpy(bool)
        sub = frame.loc[keep]
        if sub["EVENT"].sum() == 0:
            raise SealedSpecViolation("LOYO deletion of %d leaves no events" % y)
        p1, p2 = point_estimates(sub, r[keep])
        per[int(y)] = {"p1_point": p1, "beta_event_point": p2,
                       "events_removed": int(frame.loc[~keep, "EVENT"].sum()),
                       "events_remaining": int(sub["EVENT"].sum())}
    ok = all(v["p1_point"] > 0.0 and v["beta_event_point"] > 0.0
             for v in per.values())
    return {"years": ys, "per_year": per, "p3_pass": bool(ok),
            "failing_years": sorted(y for y, v in per.items()
                                    if not (v["p1_point"] > 0.0
                                            and v["beta_event_point"] > 0.0))}
