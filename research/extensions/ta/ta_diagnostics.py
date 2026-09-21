"""CTA-EDGE-01-TA — the secondary cell and the three damage diagnostics.

Components L, M, N and O of the S2 build.

Powers, enforced here and re-enforced in `ta_classify.py`:

    IEF   declared SECONDARY   promotion NONE · damage NONE · kill NONE
    SHY   maturity gradient    promotion NONE · damage NONE · kill NONE
    SPY   broad placebo        promotion NONE · DAMAGE YES  · kill NONE
    MACRO identification       promotion NONE · DAMAGE YES  · kill NONE

A damage diagnostic can only move a would-be Class D to Class I. None of them can
ever promote, upgrade or rescue anything.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Sequence

import numpy as np

import ta_contract as K
from ta_covariates import EventCovariates, design_matrix, evaluability
from ta_engine import EventResult
from ta_inference import Interval


# --------------------------------------------------------------------------- #
# L — the declared secondary (IEF)                                             #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class SecondaryResult:
    """§D.4: mean AC_NET and its interval ONLY. No Sharpe, no monthly series."""
    n_events: int
    mean_net_ac: Interval
    promotion_power = "NONE"
    damage_power = "NONE"
    kill_power = "NONE"

    def as_dict(self) -> Dict[str, object]:
        return {"n_events": self.n_events,
                "mean_net_ac_bps": self.mean_net_ac.as_dict(),
                "promotion_power": self.promotion_power,
                "damage_power": self.damage_power, "kill_power": self.kill_power,
                "note": "declared secondary; NO rescue power; never enters §I"}


# --------------------------------------------------------------------------- #
# M — the maturity-gradient diagnostic (SHY)                                   #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class GradientResult:
    """§G.1: reported so the maturity gradient is visible. No powers whatsoever."""
    n_events: int
    mean_gross_ac: Interval
    promotion_power = "NONE"
    damage_power = "NONE"
    kill_power = "NONE"

    def as_dict(self) -> Dict[str, object]:
        return {"n_events": self.n_events,
                "mean_gross_ac_bps": self.mean_gross_ac.as_dict(),
                "promotion_power": self.promotion_power,
                "damage_power": self.damage_power, "kill_power": self.kill_power,
                "note": ("maturity-gradient diagnostic only; may answer whether the "
                         "pattern attenuates toward the short end; may NOT answer "
                         "whether the mechanism exists; never enters §I")}


# --------------------------------------------------------------------------- #
# N — the broad calendar placebo (SPY), DAMAGE only                            #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class PlaceboResult:
    n_events: int
    mean_gross_ac: Interval
    bar_bps: float
    triggered: bool

    def as_dict(self) -> Dict[str, object]:
        return {"n_events": self.n_events,
                "mean_gross_ac_bps": self.mean_gross_ac.as_dict(),
                "damage_bar_bps": self.bar_bps, "triggered": self.triggered,
                "rule": ("TRIGGER iff L95(mean AC_GROSS of SPY) >= +16.0 bps/event; "
                         "absolute, one-sided, takes NO TLT input"),
                "promotion_power": "NONE", "damage_power": "YES"}


def spy_damage(interval: Interval, n_events: int,
               bar_bps: float = K.M1_GROSS_BPS) -> PlaceboResult:
    """§G.2. Absolute and same-signed; no TLT quantity is an input to this function."""
    triggered = bool(np.isfinite(interval.lower) and interval.lower >= bar_bps)
    return PlaceboResult(n_events=n_events, mean_gross_ac=interval,
                         bar_bps=bar_bps, triggered=triggered)


# --------------------------------------------------------------------------- #
# O — the macro / QRA adjusted specification, DAMAGE only                      #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class MacroResult:
    n_events: int
    evaluable: bool
    not_evaluable_reasons: Sequence[str]
    design_matrix_rank: int
    reference_group_n: int
    b0_gross_bps: float
    coefficients: Dict[str, float]
    bar_bps: float
    triggered: bool

    def as_dict(self) -> Dict[str, object]:
        return {"n_events": self.n_events, "evaluable": self.evaluable,
                "not_evaluable_reasons": list(self.not_evaluable_reasons),
                "design_matrix_rank": self.design_matrix_rank,
                "reference_group_n": self.reference_group_n,
                "min_reference_group": K.MACRO_MIN_REFERENCE_GROUP,
                "b0_gross_bps": self.b0_gross_bps,
                "coefficients_bps": dict(self.coefficients),
                "damage_bar_bps": self.bar_bps, "triggered": self.triggered,
                "rule": ("TRIGGER iff b0 < +16.0 bps OR NOT_EVALUABLE; read off the "
                         "POINT estimate - a damage diagnostic, not a hypothesis test"),
                "promotion_power": "NONE", "damage_power": "YES"}


def macro_damage(results: Sequence[EventResult], covs: Sequence[EventCovariates],
                 bar_bps: float = K.MACRO_DAMAGE_BAR_GROSS_BPS) -> MacroResult:
    """§G.3. One fixed OLS, solved by `numpy.linalg.lstsq` (minimum-norm).

    NO interactions. NO alternative windows. NO stepwise selection. NO
    outcome-dependent covariate removal. Covariates are NEVER dropped, even when a
    covariate is sparse or the reference group is small — that is what the
    NOT_EVALUABLE test is for, and it is checked first.
    """
    ev = evaluability(covs)
    by_t0 = {c.t0: c for c in covs}
    missing = [r.t0 for r in results if r.t0 not in by_t0]
    if missing:
        raise KeyError(f"{len(missing)} events have no covariate row, first {missing[0]}")
    ordered = [by_t0[r.t0] for r in results]
    X = design_matrix(ordered)
    y = np.asarray([r.ac_gross_bps for r in results], dtype=float)
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    names = ["INTERCEPT"] + list(K.MACRO_COVARIATES)
    coeffs = {n: float(v) for n, v in zip(names, beta)}
    b0 = coeffs["INTERCEPT"]
    triggered = bool((not ev["evaluable"]) or b0 < bar_bps)
    return MacroResult(
        n_events=len(results), evaluable=bool(ev["evaluable"]),
        not_evaluable_reasons=tuple(ev["not_evaluable_reasons"]),
        design_matrix_rank=int(ev["design_matrix_rank"]),
        reference_group_n=int(ev["reference_group_n"]),
        b0_gross_bps=b0, coefficients=coeffs, bar_bps=bar_bps, triggered=triggered)


def macro_not_evaluable(covs: Sequence[EventCovariates],
                        bar_bps: float = K.MACRO_DAMAGE_BAR_GROSS_BPS) -> MacroResult:
    """The pre-outcome form: decide NOT_EVALUABLE from the CALENDAR alone.

    Needs no `AC` and therefore no outcome. When the specification is already
    NOT_EVALUABLE the damage diagnostic triggers whatever the returns turn out to be,
    and that is knowable — as here — while the lineage is still outcome-blind.
    """
    ev = evaluability(covs)
    return MacroResult(
        n_events=len(covs), evaluable=bool(ev["evaluable"]),
        not_evaluable_reasons=tuple(ev["not_evaluable_reasons"]),
        design_matrix_rank=int(ev["design_matrix_rank"]),
        reference_group_n=int(ev["reference_group_n"]),
        b0_gross_bps=float("nan"), coefficients={}, bar_bps=bar_bps,
        triggered=not bool(ev["evaluable"]))
