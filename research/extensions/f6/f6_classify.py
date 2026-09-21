# -*- coding: utf-8 -*-
"""CTA-EDGE-05 / F6 — (J) the sealed terminal classifier, as deterministic code.

The sealed §12 table, and nothing else. It is exhaustive over the nine
reachable (P1 class, P2 class, P3) states, it is first-match on an explicit
table rather than on prose, and it refuses to emit a state the seal does not
define.

```
NO LOW_POWER STATE.
NO OBSERVED-POWER CALCULATION.
NO AUTOMATIC MECHANISM-FALSIFICATION STATE.
```
"""

from __future__ import annotations

from typing import Any, Dict, Optional

import f6_contract as K

POS = K.CLASS_POSITIVE
UNR = K.CLASS_UNRESOLVED
ABS_ = K.CLASS_ABSENT
VALID_CLASSES = (POS, UNR, ABS_)


class TerminalStateError(RuntimeError):
    """An input outside the sealed state space. Never coerced to a nearby state."""


#: (p1_class, p2_class, p3_pass_or_None) -> terminal. P3 is consulted ONLY on the
#: harvestable+specific branch, because that is the only branch where the sealed
#: contract evaluates it.
_TABLE = {
    (POS, POS, True): K.TERMINAL_SUPPORTED,
    (POS, POS, False): K.TERMINAL_FRAGILITY,
    (POS, UNR, None): K.TERMINAL_UNRESOLVED,
    (POS, ABS_, None): K.TERMINAL_NOT_SPECIFIC_POSITIVE,
    (UNR, POS, None): K.TERMINAL_UNRESOLVED,
    (UNR, UNR, None): K.TERMINAL_UNRESOLVED,
    (UNR, ABS_, None): K.TERMINAL_NOT_SPECIFIC,
    (ABS_, POS, None): K.TERMINAL_NOT_PROMOTED,
    (ABS_, UNR, None): K.TERMINAL_NOT_PROMOTED,
    (ABS_, ABS_, None): K.TERMINAL_NOT_PROMOTED,
}

#: the qualifier that must travel with a terminal state whose payoff is itself
#: unresolved, so a reader never converts it into a reliable negative
_QUALIFIER = {
    K.TERMINAL_NOT_SPECIFIC: "the payoff itself remains UNRESOLVED",
    K.TERMINAL_UNRESOLVED: "a failure to establish positivity is NOT a reliable "
                           "negative",
    K.TERMINAL_FRAGILITY: "NOT mechanism falsification",
    K.TERMINAL_NOT_PROMOTED: "P1 economically excluded; NOT_PROMOTED regardless "
                             "of P2",
}


def p3_is_evaluated(p1_class: str, p2_class: str) -> bool:
    """P3 is evaluated ONLY after P1 and P2 both pass. It can only veto."""
    return p1_class == POS and p2_class == POS


def classify(p1_class: str, p2_class: str,
             p3_pass: Optional[bool] = None) -> Dict[str, Any]:
    for name, v in (("p1_class", p1_class), ("p2_class", p2_class)):
        if v not in VALID_CLASSES:
            raise TerminalStateError("%s=%r is outside the sealed state space %s"
                                     % (name, v, VALID_CLASSES))
    evaluated = p3_is_evaluated(p1_class, p2_class)
    if evaluated:
        if p3_pass is None:
            raise TerminalStateError(
                "P1 and P2 both passed, so P3 MUST be evaluated before a "
                "terminal state exists")
        key = (p1_class, p2_class, bool(p3_pass))
    else:
        if p3_pass is not None:
            raise TerminalStateError(
                "P3 was supplied on a branch where the sealed contract does not "
                "evaluate it (p1=%s, p2=%s). P3 is a veto on a passing pair, "
                "never a rescue." % (p1_class, p2_class))
        key = (p1_class, p2_class, None)
    terminal = _TABLE[key]
    if terminal in K.FORBIDDEN_TERMINAL_STATES:
        raise TerminalStateError("forbidden terminal state %r" % terminal)
    promoted = terminal == K.TERMINAL_SUPPORTED
    return {
        "p1_class": p1_class, "p2_class": p2_class,
        "p3_evaluated": evaluated,
        "p3_pass": (bool(p3_pass) if evaluated else None),
        "terminal_classification": terminal,
        "promoted": promoted,
        "qualifier": _QUALIFIER.get(terminal, ""),
        "evidence_ceiling": K.EVIDENCE_CEILING,
        "sample_reuse_class": K.SAMPLE_REUSE_CLASS,
        "independent_confirmation": K.INDEPENDENT_CONFIRMATION,
        "research_status": "supported" if promoted else "not_promoted",
    }


def reachable_states():
    """Every reachable (p1, p2, p3) input — used to prove exhaustive coverage."""
    out = []
    for p1 in VALID_CLASSES:
        for p2 in VALID_CLASSES:
            if p3_is_evaluated(p1, p2):
                out.append((p1, p2, True))
                out.append((p1, p2, False))
            else:
                out.append((p1, p2, None))
    return out
