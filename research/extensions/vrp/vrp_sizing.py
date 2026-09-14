# -*- coding: utf-8 -*-
"""TSMOM-VRP-01 - module G: frozen sizing, the declared stress, the reserve and
integer granularity (sealed sections D.1 - D.4).

    S(K)        = b * K / J = 0.01 * K          dollars of loss per +1 comparable point
    q_i         = - w_i * S(K) / M_i            signed NEGATIVE: the object is SHORT
    Loss_J      = J * sum_i |q_i * M_i| = 0.30 * K
    R_J         = m_J * sum_i |q_i M_i| + lambda * K = 40 * 0.01K + 0.10K = 0.50 * K
    condition   = (1 - b) * K >= R_J            ->  0.70 K >= 0.50 K   (0.20 K slack)

THE STRESS IS APPLIED TO PRE-STRESS HOLDINGS (section D.1): a parallel +30-point move in
EVERY actually held monthly contract, applied to the contract vector held at the last
daily settlement BEFORE the stress mark, with NO roll, rebalance or reset in between.
`stress_loss` therefore takes a holdings vector and refuses a post-roll vector: callers
must pass the pre-stress holdings, and `assert_pre_stress` makes an attempt to apply the
stress after a roll detectable.

There is NO state dependence anywhere in this module: no trailing-vol sizing, no
volatility trigger, no curve trigger, no loss trigger, no daily exposure rebalance. The
sensitivity is a function of K alone, and K changes only at the monthly reset.
"""
from __future__ import annotations

import math
from typing import Dict, Iterable, List, NamedTuple, Sequence, Tuple

from vrp_constants import (GRANULARITY_TOL, J, LAMBDA, MINI_MULTIPLIER,
                           STANDARD_MULTIPLIER, b, m_J)


class Holding(NamedTuple):
    key: Tuple[str, object]   # (root, final_settlement_date)
    quantity: float           # signed; negative for the short
    multiplier: float         # $ per comparable point


def dollar_sensitivity(K: float) -> float:
    """S(K) = b*K/J = 0.01*K dollars per comparable VIX point (section D.2)."""
    return b * K / J


def holdings_for(K: float,
                 legs: Sequence[Tuple[Tuple[str, object], float, float]]) -> List[Holding]:
    """Build the signed short holdings from (key, weight, multiplier) legs.

    `q_i = - w_i * S(K) / M_i` (section F.3). Weights must sum to one; the caller's
    weights come from the calendar alone.
    """
    S = dollar_sensitivity(K)
    return [Holding(key=key, quantity=-(w * S) / mult, multiplier=mult)
            for (key, w, mult) in legs]


def gross_point_sensitivity(holdings: Iterable[Holding]) -> float:
    """sum_i |q_i * M_i| : the absolute dollar loss per +1 comparable point."""
    return sum(abs(h.quantity * h.multiplier) for h in holdings)


def stress_loss(holdings: Sequence[Holding], shock_points: float = J) -> float:
    """Loss under a parallel +`shock_points` move applied to PRE-STRESS holdings."""
    return shock_points * gross_point_sensitivity(holdings)


def assert_pre_stress(pre: Sequence[Holding], at_mark: Sequence[Holding]) -> None:
    """Section D.1: no roll, rebalance or reset between the holdings vector and the mark.

    Raises if the two vectors differ, which is exactly what a 'stress applied after the
    roll' defect looks like (acceptance item 9, sabotage 'a stress applied post-roll').
    """
    a = sorted((h.key, round(h.quantity, 12), h.multiplier) for h in pre)
    c = sorted((h.key, round(h.quantity, 12), h.multiplier) for h in at_mark)
    if a != c:
        raise ValueError("stress must be applied to PRE-STRESS holdings; the vector "
                         "changed between the last settlement and the stress mark")


def stressed_reserve(K: float, holdings: Sequence[Holding]) -> float:
    """R_J = m_J * sum|q_i M_i| + lambda * K  (section D.3)."""
    return m_J * gross_point_sensitivity(holdings) + LAMBDA * K


def implementability_condition(K: float, holdings: Sequence[Holding],
                               stress_budget: float = b) -> Dict[str, float]:
    """(1 - b) * K >= R_J. Returns the pieces and the verdict.

    `stress_budget` exists ONLY so the acceptance suite can prove the gate is not
    vacuous (item 11 requires that e.g. b = 0.45 FAILS). The primary path never passes
    it; `b` is sealed.
    """
    R_J = stressed_reserve(K, holdings)
    available = (1.0 - stress_budget) * K
    return {"R_J": R_J, "available": available, "slack": available - R_J,
            "pass": bool(available >= R_J)}


def integer_granularity(K: float,
                        standard_multiplier: float = STANDARD_MULTIPLIER,
                        mini_multiplier: float = MINI_MULTIPLIER,
                        tol: float = GRANULARITY_TOL) -> Dict[str, object]:
    """Section D.4: the frozen sensitivity must be representable in integer standard
    and/or mini contracts within +/- `tol` relative error.

    The historical research ledger models FRACTIONAL quantities at standard-contract
    prices; this check is a VRP-IMPLEMENTABILITY item and never modifies a return.
    """
    S = dollar_sensitivity(K)
    target_std = S / standard_multiplier
    target_mini = S / mini_multiplier

    def best(target: float) -> Tuple[int, float]:
        n = int(round(target))
        if n <= 0:
            n = 0
        err = float("inf") if target == 0 else abs(n - target) / abs(target)
        return n, err

    n_std, err_std = best(target_std)
    n_mini, err_mini = best(target_mini)
    # mixed: whole standard contracts plus minis for the remainder
    n_std_floor = int(math.floor(target_std))
    remainder_dollars = S - n_std_floor * standard_multiplier
    n_mix_mini = int(round(remainder_dollars / mini_multiplier))
    mixed_dollars = n_std_floor * standard_multiplier + n_mix_mini * mini_multiplier
    err_mixed = abs(mixed_dollars - S) / S if S else float("inf")

    best_err = min(err_std, err_mini, err_mixed)
    return {
        "sensitivity_dollars_per_point": S,
        "standard_contracts": n_std, "standard_rel_error": err_std,
        "mini_contracts": n_mini, "mini_rel_error": err_mini,
        "mixed_standard": n_std_floor, "mixed_mini": n_mix_mini,
        "mixed_rel_error": err_mixed,
        "best_rel_error": best_err,
        "tolerance": tol,
        "pass": bool(best_err <= tol),
    }
