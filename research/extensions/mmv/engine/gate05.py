"""Gate 0.5 — position-level separability, PnL-free, and it can KILL.

Contract section I.2:

    ELIGIBLE_GATE_05_CELL(i,t) iff
        i is one of the 15 mapped instruments
        AND MMV_sign(i,t) is defined
        AND canonical_TSMOM_sign(i,t) is defined

    POOLED_EXACT_SIGN_AGREEMENT
        = count( MMV_sign == TSMOM_sign ) / count( ELIGIBLE_GATE_05_CELL )

    ZERO IS A REAL POSITION STATE:
        0 vs 0       = AGREEMENT
        0 vs +1/-1   = DISAGREEMENT

    KILL iff POOLED_EXACT_SIGN_AGREEMENT >= 80.0 %, INCLUSIVE.

The threshold is evaluated in exact rational arithmetic against Fraction(4, 5).
That is not fastidiousness: 800/1000 in binary floating point is 0.8 exactly,
but 4/5 reached through other counts is not always, and a gate that KILLS on
equality must not turn on which side of a representation error a count lands.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Mapping, NamedTuple

from .pit import UNDEFINED, ContractViolation
from .votes import MAPPED, NOT_MAPPED

#: Contract section I.2. Inclusive. 80.0 % kills; 79.999...% passes.
KILL_THRESHOLD = Fraction(4, 5)

VALID_SIGNS = (-1, 0, 1)


class Gate05Outcome(NamedTuple):
    """The complete Gate 0.5 result.

    Carries counts and a kill flag and NOTHING ELSE. There is deliberately no
    p-value, no confidence interval and no per-instrument verdict: section I.2
    makes per-instrument agreement DIAGNOSTIC ONLY, unable to rescue a pooled
    failure or kill a pooled pass, and the way to enforce that is to not return
    a per-instrument verdict at all.
    """

    eligible_cells: int
    agreement_cells: int
    pooled_agreement: Fraction
    kill: bool
    excluded_unmapped: int
    excluded_mmv_undefined: int
    excluded_tsmom_undefined: int

    @property
    def pooled_agreement_pct(self) -> float:
        """Presentation only. Never used for the kill decision."""
        return float(self.pooled_agreement) * 100.0


def _check_sign(value, where: str):
    if value is UNDEFINED:
        return UNDEFINED
    if value not in VALID_SIGNS:
        raise ContractViolation(
            "sign must be one of -1, 0, +1 (zero is a real position state); "
            "got %r at %s" % (value, where))
    return value


def evaluate(mmv_signs: Mapping, tsmom_signs: Mapping,
             mapped=MAPPED) -> Gate05Outcome:
    """Pooled exact sign agreement over eligible cells.

    Parameters
    ----------
    mmv_signs, tsmom_signs
        ``{(date, instrument): sign_or_UNDEFINED}``. A key absent from either
        mapping is treated as UNDEFINED for that side — an unobserved cell and
        an explicitly undefined cell are the same thing here.
    mapped
        The 15-instrument domain. Exposed so the function is generic and
        testable, not so the domain can be widened in production: `assert_domain`
        guards the real path.

    Cells are drawn from the UNION of the two key sets, so a month present in
    one matrix and absent from the other cannot silently vanish.
    """
    eligible = agree = 0
    exc_unmapped = exc_mmv = exc_tsmom = 0

    for key in sorted(set(mmv_signs) | set(tsmom_signs), key=repr):
        _date, instrument = key
        if instrument not in mapped:
            # Contract section E.2: VNQ/RWX enter NEITHER numerator NOR
            # denominator. Their cells are UNDEFINED, not zero.
            exc_unmapped += 1
            continue
        m = _check_sign(mmv_signs.get(key, UNDEFINED), "MMV %r" % (key,))
        t = _check_sign(tsmom_signs.get(key, UNDEFINED), "TSMOM %r" % (key,))
        if m is UNDEFINED:
            exc_mmv += 1
            continue
        if t is UNDEFINED:
            exc_tsmom += 1
            continue
        eligible += 1
        if m == t:                 # 0 == 0 is AGREEMENT; 0 vs +/-1 is not
            agree += 1

    if eligible == 0:
        raise ContractViolation(
            "Gate 0.5 has an empty denominator: no eligible cell exists. This "
            "is a CLASS A data condition, not a pass and not a kill.")

    pooled = Fraction(agree, eligible)
    return Gate05Outcome(
        eligible_cells=eligible,
        agreement_cells=agree,
        pooled_agreement=pooled,
        kill=pooled >= KILL_THRESHOLD,
        excluded_unmapped=exc_unmapped,
        excluded_mmv_undefined=exc_mmv,
        excluded_tsmom_undefined=exc_tsmom,
    )


def kills(agreement_cells: int, eligible_cells: int) -> bool:
    """The bare threshold predicate, exact and inclusive."""
    if eligible_cells <= 0:
        raise ContractViolation("empty Gate 0.5 denominator")
    return Fraction(agreement_cells, eligible_cells) >= KILL_THRESHOLD


def per_instrument_agreement(mmv_signs: Mapping, tsmom_signs: Mapping,
                             mapped=MAPPED) -> dict:
    """DIAGNOSTIC ONLY — contract section I.2 and section L.

    Returns ``{instrument: (agree, eligible)}`` counts. It returns COUNTS, not
    verdicts, and no caller can obtain a per-instrument kill from it. A pooled
    failure may not be rescued by a subset of instruments, and a pooled pass
    may not be killed by one.
    """
    out = {i: [0, 0] for i in sorted(mapped)}
    for key in set(mmv_signs) | set(tsmom_signs):
        _date, instrument = key
        if instrument not in mapped:
            continue
        m = mmv_signs.get(key, UNDEFINED)
        t = tsmom_signs.get(key, UNDEFINED)
        if m is UNDEFINED or t is UNDEFINED:
            continue
        out[instrument][1] += 1
        if m == t:
            out[instrument][0] += 1
    return {k: tuple(v) for k, v in out.items()}


def assert_no_unmapped(keys) -> None:
    """Guard: VNQ/RWX must never reach Gate 0.5 as a cell at all."""
    bad = {i for _d, i in keys if i in NOT_MAPPED}
    if bad:
        raise ContractViolation(
            "%s reached Gate 0.5; unmapped instruments carry no cell"
            % sorted(bad))
