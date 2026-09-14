"""CTA-EDGE-02-BENB — the deterministic classification engine.

Component N of the S2 build. This is the sealed §J.3 decision order of
`BENB_PREREGISTRATION.md`, transcribed exactly, first match wins.

The function signature is itself part of the firewall: it accepts only the five
interval pairs, the LOYO flag and an evaluability flag. There is **no parameter** for a
premium-side result, for an LQD result, or for anything else, so neither can reach the
verdict even by mistake.

Boundary operators are STRICT where the contract says strict:

    Gate 1   L_T > 0
    M1       L_R > 0
    M2       L_S > +0.30            never >=
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Sequence

import benb_contract as K

CLASSES = ("F", "A-M", "A", "B", "C1", "C2", "G", "D", "S", "E")

CLASS_TITLE = {
    "F": "IDENTIFICATION / DATA FAILURE",
    "A-M": "MIXED NON-HARVESTABLE CONVERGENCE",
    "A": "STALE-NAV DOMINATED",
    "B": "OVERNIGHT PRICE DISCOVERY",
    "C1": "TRADABLE CONVERGENCE RELIABLY EXCLUDED",
    "C2": "UNRESOLVED / LOW POWER (identification)",
    "G": "FRAGILE / YEAR-DEPENDENT",
    "D": "TRADABLE CONVERGENCE PRESENT BUT UNECONOMIC",
    "S": "SUPPORTED PRICE-CONVERGENCE EDGE",
    "E": "LOW POWER / ECONOMICALLY UNRESOLVED",
}


@dataclass(frozen=True)
class Verdict:
    klass: str
    title: str
    research_status: str
    qualifier: str
    inputs: Dict[str, float]
    evaluable: bool

    def as_dict(self) -> Dict[str, object]:
        return {"class": self.klass, "title": self.title,
                "research_status": self.research_status,
                "qualifier": self.qualifier, "evaluable": self.evaluable,
                "inputs": dict(self.inputs),
                "evidence_ceiling": K.EVIDENCE_CEILING,
                "forbidden_interpretations": K.FORBIDDEN_CAUSAL_REMINDER}


def evaluable(hashes_ok: bool, decomposition_ok: bool, var_d_positive: bool,
              n_years_with_discount: int) -> bool:
    """Contract §J.2, all four conjuncts."""
    return bool(hashes_ok and decomposition_ok and var_d_positive
                and n_years_with_discount >= K.MIN_YEARS_WITH_DISCOUNT)


def classify(L_T: float, U_T: float, L_O: float, U_O: float,
             L_N: float, U_N: float, L_R: float, U_R: float,
             L_S: float, U_S: float, loyo_ok: bool,
             is_evaluable: bool = True) -> Verdict:
    """The sealed §J.3 order. FIRST MATCH WINS."""
    inputs = {"L_T": L_T, "U_T": U_T, "L_O": L_O, "U_O": U_O,
              "L_N": L_N, "U_N": U_N, "L_R": L_R, "U_R": U_R,
              "L_S": L_S, "U_S": U_S, "LOYO_OK": float(bool(loyo_ok))}

    # STEP 0
    if not is_evaluable:
        return _v("F", inputs, False)

    if L_T <= 0.0:                                   # Gate 1 NOT supported
        nav_supported_negative = U_N < 0.0
        overnight_supported_positive = L_O > 0.0
        if nav_supported_negative and overnight_supported_positive:
            return _v("A-M", inputs, True)           # STEP 1
        if nav_supported_negative:
            return _v("A", inputs, True)             # STEP 2
        if overnight_supported_positive:
            return _v("B", inputs, True)             # STEP 3
        return _v("C1" if U_T <= 0.0 else "C2", inputs, True)   # STEPS 4, 5

    # Gate 1 SUPPORTED: L_T > 0
    if not loyo_ok:
        return _v("G", inputs, True)                 # STEP 6
    if (U_R <= K.M1_RETURN_FLOOR_BPS) or (U_S <= K.M2_SHARPE):
        return _v("D", inputs, True)                 # STEP 7
    if (L_R > K.M1_RETURN_FLOOR_BPS) and (L_S > K.M2_SHARPE):
        return _v("S", inputs, True)                 # STEP 8
    return _v("E", inputs, True)                     # STEP 9


def _v(klass: str, inputs, is_eval: bool) -> Verdict:
    status, qualifier = K.STATUS_MAP[klass]
    return Verdict(klass=klass, title=CLASS_TITLE[klass], research_status=status,
                   qualifier=qualifier, inputs=inputs, evaluable=is_eval)


# --------------------------------------------------------------------------- #
# Mechanical properties, proved rather than asserted in prose                  #
# --------------------------------------------------------------------------- #


def sweep():
    """A coarse but boundary-dense grid over the sealed input domain."""
    import itertools
    t = [-2.0, -0.5, 0.0, 1e-9, 0.5, 2.0]
    s = [-1.0, 0.0, 0.2999999, 0.30, 0.3000001, 1.5]
    r = [-5.0, -1e-9, 0.0, 1e-9, 3.0]
    on = ((0.5, 1.0), (-0.5, 0.5), (-1.0, -0.5))       # (L_O, U_O)
    nv = ((-1.0, -0.5), (-1.0, 0.5), (0.5, 1.0))       # (L_N, U_N)
    for L_T, U_T in itertools.product(t, repeat=2):
        if L_T > U_T:
            continue
        for L_O, U_O in on:
            for L_N, U_N in nv:
                for L_R, U_R in itertools.product(r, repeat=2):
                    if L_R > U_R:
                        continue
                    for L_S, U_S in itertools.product(s, repeat=2):
                        if L_S > U_S:
                            continue
                        for loyo in (True, False):
                            for ev in (True, False):
                                yield (L_T, U_T, L_O, U_O, L_N, U_N,
                                       L_R, U_R, L_S, U_S, loyo, ev)


def properties() -> Dict[str, object]:
    """Totality, reachability, and the impossibility of a diagnostic promotion."""
    from collections import Counter
    seen = Counter()
    undefined = 0
    illegal_promotions = []
    s_without_gates = []
    for case in sweep():
        k = classify(*case).klass
        if k not in CLASSES:
            undefined += 1
        seen[k] += 1
        if k == "S":
            L_T, U_T, L_O, U_O, L_N, U_N, L_R, U_R, L_S, U_S, loyo, ev = case
            # S must satisfy BOTH gates strictly, and must not depend on beta_O/beta_N
            if not (L_R > K.M1_RETURN_FLOOR_BPS and L_S > K.M2_SHARPE and L_T > 0):
                s_without_gates.append(case)
            neutral = classify(L_T, U_T, -1.0, -0.5, 0.5, 1.0,
                               L_R, U_R, L_S, U_S, loyo, ev).klass
            if neutral != "S":
                illegal_promotions.append(case)
    return {"reachable": {c: seen.get(c, 0) for c in CLASSES},
            "undefined": undefined,
            "illegal_promotions": len(illegal_promotions),
            "S_without_both_gates": len(s_without_gates)}
