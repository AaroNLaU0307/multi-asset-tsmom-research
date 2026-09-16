"""The frozen 15-instrument coefficient table and the raw direction rule.

Contract section E:

    raw(i,t) = sign( c_iG * G_t  +  c_iI * I_t  +  c_iP * P_t )      sign(0) = 0

Asset-specific votes. NEVER a global macro scalar.

The table is a module constant, not a parameter with a default. There is no
constructor argument, no config key and no override hook by which a caller
could supply a different mapping: section E states COEFFICIENTS ARE NOT
ALTERABLE, and the way to implement "not alterable" is to provide no way to
alter it.
"""

from __future__ import annotations

from types import MappingProxyType
from typing import Mapping

from .legs import sign
from .pit import UNDEFINED, ContractViolation

#: Contract section E.1. Read-only: MappingProxyType blocks mutation of the
#: sealed table through the module attribute.
COEFFICIENTS: Mapping[str, tuple] = MappingProxyType({
    # equity — growth long, policy short
    "SPY": (1, 0, -1),
    "EEM": (1, 0, -1),
    "EWJ": (1, 0, -1),
    "XLE": (1, 0, -1),
    "XLU": (1, 0, -1),
    # duration
    "TLT": (-1, -1, -1),
    "SHY": (-1, -1, -1),
    # credit
    "LQD": (1, 0, 0),
    "HYG": (1, 0, 0),
    # commodities
    "USO": (0, 1, 0),
    "UNG": (0, 1, 0),
    "GLD": (0, 1, 0),
    "DBA": (0, 1, 0),
    # dollar
    "UUP": (0, 1, 1),
    "FXY": (0, -1, -1),
})

#: Contract section E: the PRIMARY MMV DOMAIN. Exactly 15 instruments.
MAPPED = frozenset(COEFFICIENTS)

#: Contract section E.2. NOT the same thing as "signal = 0".
NOT_MAPPED = frozenset({"VNQ", "RWX"})

#: The canonical book, for the domain assertions. MMV's alpha covers 15 of
#: these; the claim may NEVER be stated as "all canonical 17 ETFs".
CANONICAL_17 = frozenset({
    "SPY", "EEM", "EWJ", "XLE", "XLU", "TLT", "SHY", "LQD", "HYG",
    "USO", "UNG", "GLD", "DBA", "UUP", "FXY", "VNQ", "RWX"})

LEG_NAMES = ("G", "I", "P")


class NotInDomain(KeyError):
    """Raised when an instrument outside the 15-instrument domain is asked for
    a direction.

    VNQ and RWX raise this rather than returning 0 or UNDEFINED. The contract
    is explicit that coding an unmapped instrument as a signal zero would make
    it disagree with the canonical composite in every month that composite is
    non-zero — mechanically, regardless of macro information — pushing pooled
    Gate 0.5 agreement down IN MMV's OWN FAVOUR. An exception makes the
    distinction impossible to lose by accident; a sentinel would not.
    """


def is_mapped(instrument: str) -> bool:
    return instrument in COEFFICIENTS


def coefficients(instrument: str) -> tuple:
    try:
        return COEFFICIENTS[instrument]
    except KeyError:
        raise NotInDomain(
            "%r is not in the MMV signal domain (15 mapped instruments). "
            "It is NOT_MAPPED, which is not the same as signal = 0."
            % instrument) from None


def required_legs(instrument: str) -> tuple:
    """The leg names whose absence makes this instrument UNDEFINED.

    Dependency-sensitive, per contract section E.3: only a leg with a NON-ZERO
    coefficient is required. HYG loads on growth alone, so a missing inflation
    or policy reading leaves HYG perfectly well defined. Treating every
    instrument as requiring every leg would silently delete cells from the
    Gate 0.5 denominator for legs those cells never used.
    """
    c = coefficients(instrument)
    return tuple(name for name, coef in zip(LEG_NAMES, c) if coef != 0)


def raw_direction(instrument: str, G, I, P):
    """The sealed raw direction for one instrument in one macro state.

    Returns -1, 0, +1 or UNDEFINED. Raises NotInDomain for VNQ/RWX.

    A zero leg ABSTAINS — it contributes nothing to the vote sum and never
    vetoes the others. A tie (vote sum 0) is a real flat position, resolved by
    no priority theme and no carry-forward. A MISSING leg that this instrument
    actually loads on makes the cell UNDEFINED, never 0.
    """
    cg, ci, cp = coefficients(instrument)
    legs = {"G": (cg, G), "I": (ci, I), "P": (cp, P)}
    total = 0
    for coef, value in legs.values():
        if coef == 0:
            continue                          # unrelated leg: irrelevant
        if value is UNDEFINED:
            return UNDEFINED                  # required leg missing
        total += coef * value
    return sign(total)


def direction_row(G, I, P) -> dict:
    """raw direction for all 15 mapped instruments in one macro state."""
    return {i: raw_direction(i, G, I, P) for i in sorted(COEFFICIENTS)}


def assert_domain(instruments) -> None:
    """Fail loudly if a caller hands the engine a non-domain instrument.

    The MMV signal frame must carry exactly the 15 mapped columns. VNQ/RWX
    present as zero-filled or NaN-filled columns are both wrong: the first
    corrupts Gate 0.5, the second dilutes the equal-weight book. They must be
    ABSENT.
    """
    given = set(instruments)
    intruders = given & NOT_MAPPED
    if intruders:
        raise ContractViolation(
            "%s are NOT_MAPPED and must be ABSENT from the MMV signal domain, "
            "not present as zero or NaN columns" % sorted(intruders))
    unknown = given - MAPPED
    if unknown:
        raise ContractViolation(
            "instruments outside the sealed 15: %s" % sorted(unknown))
    if given != MAPPED:
        raise ContractViolation(
            "MMV signal domain must be exactly the 15 mapped instruments; "
            "missing %s" % sorted(MAPPED - given))
