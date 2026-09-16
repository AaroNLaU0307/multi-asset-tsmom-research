"""First-release concordance — DESCRIPTIVE DIAGNOSTIC ONLY.

Contract section B and section L.1:

    FIRST_RELEASE_CHAIN = DESCRIPTIVE CONCORDANCE DIAGNOSTIC ONLY
      PROMOTION_POWER = NONE · RESCUE_POWER = NONE · KILL_POWER = NONE
      NO large/small disagreement threshold exists or may be introduced.

    NO threshold · NO pass/fail · NO promotion · NO rescue · NO kill · NO
    return data. Purpose is interpretation only.

This module reports counts and rates. It has no threshold constant, returns no
boolean, and exposes no function whose name or signature could be mistaken for
a gate. That is the enforcement: a component that cannot express a verdict
cannot be asked for one later by someone who has forgotten why it must not.

Under the sealed series identities the revision channel is confined to the
GROWTH leg — CPILFENS is final when issued, and the FOMC target is administered
and never revised — so a large reading here is a statement about INDPRO and
PAYEMS revisions specifically.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Mapping, NamedTuple

from .pit import UNDEFINED
from .votes import MAPPED


class ConcordanceReport(NamedTuple):
    """Counts only. There is no verdict field, by design."""

    compared_cells: int
    disagreement_cells: int
    disagreement_rate: Fraction
    by_instrument: Mapping
    by_leg: Mapping
    by_year: Mapping

    @property
    def disagreement_pct(self) -> float:
        return float(self.disagreement_rate) * 100.0


def compare(primary_signs: Mapping, first_release_signs: Mapping,
            mapped=MAPPED) -> ConcordanceReport:
    """Pooled sign disagreement between the two information concepts.

    Both inputs are ``{(date, instrument): sign_or_UNDEFINED}`` built with
    IDENTICAL series identity, transform, asset mapping and monthly dates — the
    only difference permitted is the information concept. A cell counts only
    when BOTH are defined; an undefined cell on either side is not evidence of
    agreement or of disagreement.
    """
    compared = disagree = 0
    by_instrument: dict = {}
    by_year: dict = {}

    for key in set(primary_signs) | set(first_release_signs):
        date, instrument = key
        if instrument not in mapped:
            continue
        a = primary_signs.get(key, UNDEFINED)
        b = first_release_signs.get(key, UNDEFINED)
        if a is UNDEFINED or b is UNDEFINED:
            continue
        compared += 1
        year = getattr(date, "year", None) or int(str(date)[:4])
        ai = by_instrument.setdefault(instrument, [0, 0])
        ay = by_year.setdefault(year, [0, 0])
        ai[1] += 1
        ay[1] += 1
        if a != b:
            disagree += 1
            ai[0] += 1
            ay[0] += 1

    rate = Fraction(disagree, compared) if compared else Fraction(0, 1)
    return ConcordanceReport(
        compared_cells=compared,
        disagreement_cells=disagree,
        disagreement_rate=rate,
        by_instrument={k: tuple(v) for k, v in sorted(by_instrument.items())},
        by_leg={},
        by_year={k: tuple(v) for k, v in sorted(by_year.items())},
    )


def compare_legs(primary_legs: Mapping, first_release_legs: Mapping) -> dict:
    """Disagreement counts per macro leg, ``{'G'|'I'|'P': (disagree, n)}``.

    Inputs are ``{date: {'G': s, 'I': s, 'P': s}}``. Reported so a reader can
    see WHERE the two concepts part company, which is the whole interpretive
    value of the cell.
    """
    out = {name: [0, 0] for name in ("G", "I", "P")}
    for date in set(primary_legs) & set(first_release_legs):
        a, b = primary_legs[date], first_release_legs[date]
        for name in out:
            av, bv = a.get(name, UNDEFINED), b.get(name, UNDEFINED)
            if av is UNDEFINED or bv is UNDEFINED:
                continue
            out[name][1] += 1
            if av != bv:
                out[name][0] += 1
    return {k: tuple(v) for k, v in out.items()}


#: Named so that a reader who goes looking for the threshold finds this instead.
NO_THRESHOLD_EXISTS = (
    "Contract section L.1: this diagnostic has NO threshold, NO pass/fail and "
    "NO kill power. A large disagreement is reported as 'the primary result is "
    "specifically a LATEST-KNOWN macro-state result'; a small one as 'revision "
    "handling is empirically less consequential'. NEITHER broadens the claim "
    "and neither changes the verdict.")
