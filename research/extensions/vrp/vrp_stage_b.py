# -*- coding: utf-8 -*-
"""TSMOM-VRP-01 - module I: the Stage-B self-financing book ledger (sealed section H).

    W_0             = $1,000,000 at the close of the last NYSE trading day before the
                      first Stage-B month (a RESEARCH-book convention, not a deployable NAV)
    month-end       core = 0.80 * W_(t-1);  sleeve K_t = 0.20 * W_(t-1)
                    sleeve sensitivity = 0.01 * K_t = 0.002 * W_(t-1) per comparable point
                    - identical exposure per unit committed capital to Stage A
    core mark       BUY-AND-HOLD IN UNITS:
                    V_core,d = V_core,start * ( 1 + sum_i p_i,t * ( P_i,d / P_i,start - 1 ) )
                    with the canonical 2-bps weight-turnover cost charged on the
                    month-end day. Signal and position logic are UNTOUCHED; only capital
                    is accounted.
    sleeve          C starts each month at K_t; every VX exchange business day
                    C <- C + VM_d - cost_d
    funding rule    if C_d < 0 after a day's settlement, the shortfall X = -C_d is funded
                    from the BOOK at the close of the NEXT NYSE trading day d+1 by
                    liquidating a PRO-RATA slice f = X / V_core,(d+1) of the core's UNIT
                    holdings, charging 0.0002 * f * G_core,(d+1), transferring X to C
                    (so C <- 0), and continuing the core at (1 - f) of its units.
                    NEVER SELECTIVE. The reduced core is carried forward; the ledger
                    never continues a fictional untouched full-sized core.
    no borrowing    none, ever. No margin loan, no external recapitalisation.
    no clipping     liabilities beyond sleeve capital are recorded in full against book
                    wealth; no loss is clipped at -100 % of K_t.
    BOOK_EXHAUSTION if X > V_core,(d+1): liquidate the entire core, record
                    W = V_core,(d+1) - X (<= 0, unclipped) as terminal, record the
                    month's r_book as computed, log BOOK_EXHAUSTION, TERMINATE. No restart.

Section H.4 oracle identity, binding: in any month with NO funding event,
    r_book,t = 0.80 * r_core,t + 0.20 * r_A,t(K = K_t)   exactly.

S2 AUTHORISATION BOUNDARY: implementable and synthetically testable in S2; a REAL run is
gated by `vrp_reveal.require_run_authorization`, which S2 cannot satisfy.
"""
from __future__ import annotations

import datetime as _dt
from typing import Dict, List, NamedTuple, Optional, Sequence, Tuple

import vrp_costs as vcosts
import vrp_reveal as vreveal
import vrp_stage_a as vstage_a
from vrp_constants import (CANONICAL_COST_BPS, CA_FORWARD_BOUNDARY, CORE_SHARE,
                           STANDARD_MULTIPLIER, s, stageB_end)

Key = Tuple[str, _dt.date]


class CanonicalBlindnessBreach(RuntimeError):
    """Section K.3: no canonical quantity may be formed for any month after the C-A
    forward boundary (2026-09-11), and Stage B ends at the frozen core boundary
    2026-05-31. Raised before any arithmetic touches such a month."""


def _assert_core_within_boundary(core: Sequence["CoreMonth"]) -> None:
    for cm in core:
        for d in cm.nyse_days:
            if d > CA_FORWARD_BOUNDARY:
                raise CanonicalBlindnessBreach(
                    "core day %s is after the C-A forward boundary %s"
                    % (d, CA_FORWARD_BOUNDARY))
            if d > stageB_end:
                raise CanonicalBlindnessBreach(
                    "core day %s is after the sealed Stage-B boundary %s"
                    % (d, stageB_end))


class CoreMonth(NamedTuple):
    """The frozen canonical core for one month. Positions are the weights decided at the
    end of month t-1 (`positions = weights.shift(1)`); nothing here alters them."""
    month: str
    nyse_days: Tuple[_dt.date, ...]          # ascending; the last is the book month-end
    unit_index: Dict[_dt.date, float]        # 1 + sum_i p_i * (P_i,d / P_i,start - 1)
    gross_fraction: Dict[_dt.date, float]    # G_core,d / V_core,d (canonical gross exposure)
    turnover: float                          # canonical weight turnover for month t


class SleeveMonth(NamedTuple):
    month: str
    vx_days: Tuple[vstage_a.DayInput, ...]   # VX exchange business days of the month


class FundingEvent(NamedTuple):
    detected: _dt.date
    funded: _dt.date
    shortfall: float
    fraction: float
    liquidation_cost: float


class BookMonthResult(NamedTuple):
    month: str
    W_start: float
    W_end: float
    r_book: float
    K_t: float
    r_core: float
    r_A_on_Kt: float               # Stage-A-equivalent sleeve return, EXCLUDING the reset
    reset_cost_on_Kt: float        # month-start sensitivity reset, as a fraction of K_t
    funding_events: Tuple[FundingEvent, ...]
    book_exhaustion: bool
    core_units_scale_end: float


class StageBResult(NamedTuple):
    months: Tuple[BookMonthResult, ...]
    terminated: bool
    termination_month: Optional[str]


def core_unit_index(positions: Dict[str, float],
                    prices: Dict[str, Dict[_dt.date, float]],
                    start: _dt.date,
                    days: Sequence[_dt.date]) -> Dict[_dt.date, float]:
    """V_core,d / V_core,start under the sealed BUY-AND-HOLD-IN-UNITS mark (section H.2)."""
    out: Dict[_dt.date, float] = {}
    for d in days:
        acc = 0.0
        for asset, p in positions.items():
            P0 = prices[asset][start]
            acc += p * (prices[asset][d] / P0 - 1.0)
        out[d] = 1.0 + acc
    return out


def run_stage_b(core: Sequence[CoreMonth],
                sleeve: Sequence[SleeveMonth],
                W0: float,
                data_kind: str,
                run_id: str = "") -> StageBResult:
    """The sealed CONFIRMATORY Stage-B book. `core` and `sleeve` are aligned month by month.

    This is the gated, preregistered entry point. Under the sealed section O stop rule a
    Class-3 Stage A means Stage B never runs, and `require_run_authorization` refuses
    without a grant whose `stage_b_authorized` is true.
    """
    vreveal.require_run_authorization(data_kind, run_id, stage="STAGE_B")
    if data_kind == vreveal.REAL:
        _assert_core_within_boundary(core)
    return run_book_ledger(core, sleeve, W0)


def run_book_ledger(core: Sequence[CoreMonth],
                    sleeve: Sequence[SleeveMonth],
                    W0: float) -> StageBResult:
    """The self-financing book LEDGER MECHANICS, with no governance gate of their own.

    Separated from `run_stage_b` so that a DIFFERENT, clearly-labelled lineage may reuse
    the mechanics that acceptance items 13, 14 and 15 already validated, without either
    weakening the confirmatory Stage-B gate or re-implementing the ledger and risking
    divergence. The confirmatory entry point above is the ONLY caller that may present a
    result as sealed Stage-B evidence; any other caller is exploratory and carries
    `PROMOTION_POWER = NONE`.
    """
    sleeve_by_month = {m.month: m for m in sleeve}

    results: List[BookMonthResult] = []
    W = float(W0)
    terminated = False
    termination_month: Optional[str] = None

    # THE SLEEVE POSITION PERSISTS ACROSS CALENDAR-MONTH BOUNDARIES (section H.1/H.2).
    # It is deliberately declared here, outside the month loop. Recreating it per month
    # was VRP-DIAG-DEFECT-001: it discarded each month's first-day variation margin and
    # re-established the whole position from flat, which is a different strategy and
    # violates the binding section H.4 identity against the real Stage-A series.
    holdings: Dict[Key, float] = {}
    prices: Dict[Key, float] = {}
    K_prev: Optional[float] = None

    for cm in core:
        if terminated:
            break
        sm = sleeve_by_month.get(cm.month)
        vx_days: Tuple[vstage_a.DayInput, ...] = sm.vx_days if sm else ()

        W_start = W
        V_core_start = CORE_SHARE * W_start
        K_t = s * W_start
        C = K_t
        reset_charged = False
        scale = 1.0                     # core unit-holdings scale after liquidations
        funding: List[FundingEvent] = []
        pending: List[Tuple[_dt.date, float]] = []   # (detected_day, shortfall)
        exhausted = False

        # PER-MONTH accounts only. The sleeve POSITION (`holdings`, `prices`) lives
        # outside this loop: see VRP-DIAG-DEFECT-001 and its closure record under
        # research/extensions/vrp/diagnostics/.
        sleeve_vm = 0.0
        sleeve_roll_cost = 0.0
        reset_cost = 0.0

        vx_by_date = {d.date: d for d in vx_days}
        all_days = sorted(set(cm.nyse_days) | set(vx_by_date))

        # Section H.1: the sleeve's point sensitivity for month t is 0.01 * K_t, and the
        # reset trade to that new sensitivity is executed at the month-end allocation -
        # i.e. BEFORE the new month's first variation margin is marked. The carried
        # position keeps its weights and is rescaled by K_t / K_(t-1); only that increment
        # trades. This is what makes r_A_on_Kt scale-invariant and therefore comparable,
        # month for month, with the sealed constant-K Stage-A series.
        if holdings and K_prev:
            factor = K_t / K_prev
            resized: Dict[Key, float] = {}
            for key, q in holdings.items():
                dq = q * (factor - 1.0)
                if dq != 0.0:
                    reset_cost += vcosts.cost_dollars(all_days[0], dq, STANDARD_MULTIPLIER)
                resized[key] = q * factor
            holdings = resized
        K_prev = K_t

        def core_value(day: _dt.date) -> float:
            idx = cm.unit_index.get(day)
            if idx is None:
                # NYSE closed: the core carries at its last available mark
                earlier = [x for x in cm.nyse_days if x <= day]
                idx = cm.unit_index[earlier[-1]] if earlier else 1.0
            return V_core_start * scale * idx

        C -= reset_cost
        for day in all_days:
            # ---- sleeve leg: VX settles today --------------------------------
            if day in vx_by_date:
                di = vx_by_date[day]
                today = {di.front_key: di.front_price, di.second_key: di.second_price}
                vm = 0.0
                for key, q in holdings.items():
                    if key in today and key in prices:
                        vm += q * STANDARD_MULTIPLIER * (today[key] - prices[key])
                wanted = vstage_a.target_holdings(di, K_t)
                cost = 0.0
                for key in set(wanted) | set(holdings):
                    dq = wanted.get(key, 0.0) - holdings.get(key, 0.0)
                    if dq != 0.0:
                        cost += vcosts.cost_dollars(day, dq, STANDARD_MULTIPLIER)
                holdings, prices = wanted, dict(today)
                sleeve_vm += vm
                sleeve_roll_cost += cost
                C += vm - cost
                if C < 0.0:
                    pending.append((day, -C))

            # ---- funding leg: executed at the close of the NEXT NYSE day -----
            if day in cm.nyse_days and pending:
                due = [(dd, x) for (dd, x) in pending if dd < day]
                if due:
                    X = sum(x for _, x in due)
                    pending = [(dd, x) for (dd, x) in pending if dd >= day]
                    V = core_value(day)
                    if X > V:
                        # BOOK_EXHAUSTION: the book cannot fund the liability
                        W = V - X                      # <= 0, as computed, unclipped
                        scale = 0.0
                        exhausted = True
                        terminated = True
                        termination_month = cm.month
                        break
                    f = X / V
                    gross = cm.gross_fraction.get(day, 1.0) * V
                    liq_cost = CANONICAL_COST_BPS * f * gross
                    scale *= (1.0 - f)
                    C += X                              # C returns to 0 as of d+1
                    # the liquidation cost is borne by the book, from the core side
                    V_after = core_value(day)
                    if V_after > 0:
                        scale *= max(0.0, 1.0 - liq_cost / V_after)
                    funding.append(FundingEvent(detected=due[-1][0], funded=day,
                                                shortfall=X, fraction=f,
                                                liquidation_cost=liq_cost))

        if exhausted:
            r_book = W / W_start - 1.0
            results.append(BookMonthResult(
                month=cm.month, W_start=W_start, W_end=W, r_book=r_book, K_t=K_t,
                r_core=float("nan"), r_A_on_Kt=(sleeve_vm - sleeve_roll_cost) / K_t,
                reset_cost_on_Kt=reset_cost / K_t,
                funding_events=tuple(funding), book_exhaustion=True,
                core_units_scale_end=0.0))
            break

        # ---- month end: canonical cost on the month-end day, then wealth ------
        month_end = cm.nyse_days[-1]
        gross_core_end = core_value(month_end)
        canonical_cost = CANONICAL_COST_BPS * cm.turnover * V_core_start * scale
        V_core_end = gross_core_end - canonical_cost
        W_end = V_core_end + C

        r_core = (cm.unit_index[month_end] - 1.0) - CANONICAL_COST_BPS * cm.turnover
        r_A = (sleeve_vm - sleeve_roll_cost) / K_t

        results.append(BookMonthResult(
            month=cm.month, W_start=W_start, W_end=W_end,
            r_book=W_end / W_start - 1.0, K_t=K_t,
            r_core=r_core, r_A_on_Kt=r_A, reset_cost_on_Kt=reset_cost / K_t,
            funding_events=tuple(funding), book_exhaustion=False,
            core_units_scale_end=scale))
        W = W_end

    return StageBResult(months=tuple(results), terminated=terminated,
                        termination_month=termination_month)


# --------------------------------------------------------------------------- #
# Section I - tail definition, estimand, states
# --------------------------------------------------------------------------- #
def tail_months(r_spy: Sequence[float], quantile: float = 0.10) -> Tuple[float, List[int]]:
    """X46 rule (section I.1): q = quantile_0.10(r_SPY) over the aligned COMPLETE months,
    linear interpolation; T = { t : r_SPY,t <= q }, equality INCLUDED."""
    import numpy as np
    arr = np.asarray(list(r_spy), dtype=np.float64)
    q = float(np.quantile(arr, quantile, method="linear"))
    return q, [i for i, v in enumerate(arr) if v <= q]


def tail_differential(r_book: Sequence[float], r_core: Sequence[float],
                      tail_idx: Sequence[int]) -> float:
    """D = mean_{t in T} ( r_book,t - r_core,t )  (section I.2)."""
    if not tail_idx:
        raise ValueError("empty tail set")
    return sum(r_book[i] - r_core[i] for i in tail_idx) / len(tail_idx)


def classify_stage_b(lower: float, upper: float, delta_tail: float,
                     book_exhaustion: bool = False) -> Dict[str, str]:
    """Section I.3. Strict endpoints; sealed."""
    if book_exhaustion:
        return {"state": "NOT_PROMOTED", "failure_class": "4",
                "class_name": "TARGET_MARGIN_RELIABLY_EXCLUDED",
                "subtag": "book_exhausted"}
    if lower >= -delta_tail:
        return {"state": "SUPPORTED", "failure_class": "", "class_name": "", "subtag": ""}
    if upper < -delta_tail:
        return {"state": "NOT_PROMOTED", "failure_class": "4",
                "class_name": "TARGET_MARGIN_RELIABLY_EXCLUDED", "subtag": ""}
    return {"state": "UNRESOLVED", "failure_class": "3",
            "class_name": "INSUFFICIENT_EVIDENCE_LOW_POWER", "subtag": ""}


def descriptive_tail_ratio(r_book: Sequence[float], r_core: Sequence[float],
                           tail_idx: Sequence[int],
                           sign_stable_fraction: float,
                           ratio_floor: float,
                           sign_threshold: float) -> Optional[float]:
    """R11 / section I.4: reported ONLY if |mean_T(r_core)| >= ratio_floor AND the
    denominator keeps one sign in >= `sign_threshold` of valid replicates. Otherwise the
    ratio is NOT REPORTED AT ALL (None). It has no gate power in any state."""
    mean_core = sum(r_core[i] for i in tail_idx) / len(tail_idx)
    if abs(mean_core) < ratio_floor or sign_stable_fraction < sign_threshold:
        return None
    mean_book = sum(r_book[i] for i in tail_idx) / len(tail_idx)
    return mean_book / mean_core
