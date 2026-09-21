"""CTA-EDGE-01-TA — the deterministic A/B/C/D/I classification engine.

Component P of the S2 build. This is the sealed §I.2 decision order, transcribed
exactly, first match wins. There is no human judgment at S3 and no discretion here.

    STEP 1  CLASS A   iff  U_AC <= 0
    STEP 2  CLASS B   iff  (U_N < +8.0) OR (U_S < +0.30)
    STEP 3  W = (L_N >= +8.0) AND (L_S >= +0.30)
            3a  CLASS D  iff W AND loyo passes AND NOT spy damage AND NOT macro damage
            3b  CLASS I  iff W AND at least one of those three triggers
    STEP 4  CLASS C   everything else

`U_AC` / `L_AC` are the bootstrap percentile bounds of mean **AC_GROSS**;
`U_N = U_AC - 8.0` and `L_N = L_AC - 8.0` are the same bounds for mean **AC_NET**;
`L_S` / `U_S` are the bounds of the calendarised Sharpe. Nothing else is an input:
IEF and SHY are absent from this module by construction.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Sequence

import ta_contract as K

CLASSES = ("A", "B", "C", "D", "I")

CLASS_TITLE = {
    "A": "DIRECTIONAL ETF PATTERN EXCLUDED",
    "B": "TARGET MARGIN RELIABLY EXCLUDED",
    "C": "UNRESOLVED / LOW POWER",
    "D": "SUPPORTED ETF-LEVEL EFFECT",
    "I": "IDENTIFICATION / DEPENDENCE FAILURE",
}


@dataclass(frozen=True)
class Verdict:
    klass: str
    title: str
    research_status: str
    qualifier: str
    would_be_d: bool
    triggers: Sequence[str]
    inputs: Dict[str, float]

    def as_dict(self) -> Dict[str, object]:
        return {"class": self.klass, "title": self.title,
                "research_status": self.research_status,
                "qualifier": self.qualifier, "would_be_d_condition": self.would_be_d,
                "damage_triggers": list(self.triggers), "inputs": dict(self.inputs),
                "evidence_ceiling": K.EVIDENCE_CEILING,
                "forbidden_interpretations": K.FORBIDDEN_CAUSAL_REMINDER}


def classify(l_ac_gross: float, u_ac_gross: float,
             l_sharpe: float, u_sharpe: float,
             loyo_passes: bool, spy_damage: bool, macro_damage: bool,
             executed_calendar_contaminated: bool = False) -> Verdict:
    """The sealed §I.2 order. First match wins.

    `executed_calendar_contaminated` is the §I.3 post-run trigger: if the executed
    event calendar is found to deviate from the sealed one in a way that invalidates
    the sealed estimand, the verdict is Class I regardless of the bounds. A PRE-run
    identity failure is a different thing entirely (§P Level 1) and is never a verdict.
    """
    l_net = l_ac_gross - K.COST_BPS
    u_net = u_ac_gross - K.COST_BPS
    inputs = {"L_AC_gross": l_ac_gross, "U_AC_gross": u_ac_gross,
              "L_AC_net": l_net, "U_AC_net": u_net,
              "L_sharpe": l_sharpe, "U_sharpe": u_sharpe}

    triggers = []
    if not loyo_passes:
        triggers.append("LOYO_FRAGILITY")
    if spy_damage:
        triggers.append("SPY_BROAD_CALENDAR_PLACEBO")
    if macro_damage:
        triggers.append("MACRO_QRA_IDENTIFICATION")

    if executed_calendar_contaminated:
        return _verdict("I", False, triggers + ["EXECUTED_CALENDAR_CONTAMINATION"],
                        inputs)

    # STEP 1
    if u_ac_gross <= 0.0:
        return _verdict("A", False, triggers, inputs)
    # STEP 2
    if (u_net < K.M1_NET_BPS) or (u_sharpe < K.M2_SHARPE):
        return _verdict("B", False, triggers, inputs)
    # STEP 3
    would_be_d = (l_net >= K.M1_NET_BPS) and (l_sharpe >= K.M2_SHARPE)
    if would_be_d:
        if not triggers:
            return _verdict("D", True, triggers, inputs)
        return _verdict("I", True, triggers, inputs)
    # STEP 4
    return _verdict("C", False, triggers, inputs)


def _verdict(klass: str, would_be_d: bool, triggers, inputs) -> Verdict:
    status, qualifier = K.STATUS_MAP[klass]
    return Verdict(klass=klass, title=CLASS_TITLE[klass], research_status=status,
                   qualifier=qualifier, would_be_d=would_be_d,
                   triggers=tuple(triggers), inputs=inputs)


# --------------------------------------------------------------------------- #
# Mechanical properties, asserted rather than asserted-in-prose                #
# --------------------------------------------------------------------------- #


def sweep(ac_grid=None, sharpe_grid=None):
    """Every (bounds x flags) combination of a coarse grid. Used by the tests."""
    import itertools
    ac_grid = ac_grid or [-40.0, -8.0, 0.0, 0.01, 8.0, 16.0, 16.5, 40.0, 120.0]
    sharpe_grid = sharpe_grid or [-1.0, 0.0, 0.1, 0.2999, 0.30, 0.31, 1.5]
    for l_ac, u_ac in itertools.product(ac_grid, repeat=2):
        if l_ac > u_ac:
            continue
        for l_s, u_s in itertools.product(sharpe_grid, repeat=2):
            if l_s > u_s:
                continue
            for loyo, spy, macro in itertools.product((True, False), repeat=3):
                yield (l_ac, u_ac, l_s, u_s, loyo, spy, macro)


def diagnostics_can_never_promote() -> Dict[str, object]:
    """Firing ANY damage flag must never move a class towards D.

    The check is exhaustive over the sweep: for every bound combination, the class
    obtained with all flags clean is compared against every other flag combination,
    and a `D` that appears only when a flag fires would be an illegal upgrade.
    """
    illegal = []
    for l_ac, u_ac, l_s, u_s, loyo, spy, macro in sweep():
        clean = classify(l_ac, u_ac, l_s, u_s, True, False, False).klass
        got = classify(l_ac, u_ac, l_s, u_s, loyo, spy, macro).klass
        if got == "D" and clean != "D":
            illegal.append((l_ac, u_ac, l_s, u_s, loyo, spy, macro))
    return {"illegal_upgrades": len(illegal), "examples": illegal[:3]}


def reachability() -> Dict[str, int]:
    from collections import Counter
    seen = Counter(classify(*case).klass for case in sweep())
    return {k: seen.get(k, 0) for k in CLASSES}
