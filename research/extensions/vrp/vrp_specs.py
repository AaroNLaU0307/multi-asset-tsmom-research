# -*- coding: utf-8 -*-
"""TSMOM-VRP-01 - module A: contract metadata / specification registry.

The DATED break table required by section F.5 and by acceptance-contract items 2, 7
and 8. Every span is sourced to a saved, hashed primary Cboe document under
`data/vix/raw/specifications/`. Specification changes are EXPLICIT METADATA here and
are never inferred from a price jump (section F.5 forbids that).

Everything is converted to the COMMON $1,000-PER-POINT ECONOMIC BASIS before any
weight, cost, stress or return arithmetic:

    price_comparable = price_quoted * M_quoted / 1000
    tick_comparable  = tick_quoted  * M_quoted / 1000

THE DOCUMENTED HISTORY
----------------------
CFE Information Circular IC07-03 (7 March 2007), "Rescaling of VIX and VXD Futures
Contracts", saved and hashed, states verbatim:

    "The rescaling will be effective March 26, 2007 and will apply to all VIX and VXD
     futures contracts."
    "CFE will divide the VIX and VXD futures contracts by 10 ... Second, CFE will
     increase the current multiplier for the VIX and VXD futures contracts from $100
     to $1,000. As a result, the traded futures price will be reduced by a factor of
     ten and the minimum tick will be reduced from $0.10 to 0.01 index point, but the
     dollar value of both will remain the same."

and tabulates: Current Practice - price 103.90, multiplier $100, minimum tick $0.10,
value per tick $10; Rescaled Practice - price 10.39, multiplier $1,000, minimum tick
0.01 index point, value per tick $10.

The Cboe VX contract-specification page (saved and hashed; "Contract Snapshot as of
June 13, 2025") documents the CURRENT outright minimum price interval as "0.05
points, equal to $50.00 per contract" and the contract multiplier as $1000, and the
VX listing date as March 26, 2004.

THE ONE UNDOCUMENTED SPAN, AND THE SEALED RULE THAT CLOSES IT
-------------------------------------------------------------
The exact date on which the OUTRIGHT minimum increment moved from 0.01 to 0.05 index
points is not established by any primary Cboe document this session could obtain and
read (CFE-2009-01, the filing whose title suggested it, is in fact a Threshold-Width
amendment and says nothing about the tick; it is deliberately NOT cited here).

Section G fixes what to do:

    "If the contemporaneous tick is undocumented for a span, the largest tick
     documented for the contract on the comparable basis is used for that span
     (conservative; declared)."

So the whole post-rescaling span carries the LARGEST documented comparable tick,
0.05. This is declared, conservative, and - provably - economically inert: section G
charges `cost_points = max(0.10, tick_comparable)`, and every tick documented for
this contract on the comparable basis lies in [0.01, 0.05], all below 0.10. The
acceptance suite asserts that invariance directly
(`test_cost_invariant_to_tick_assumption`), so the undocumented span cannot move any
cost, any Stage-A return, or any estimand.

This module reads no market data and computes no return.
"""
from __future__ import annotations

import datetime as _dt
from typing import Dict, List, NamedTuple, Optional, Tuple

from vrp_constants import COMMON_BASIS_MULTIPLIER, MINI_MULTIPLIER, STANDARD_MULTIPLIER

# VX standard monthly futures listing date (Cboe VX specification page, saved+hashed).
VX_LISTING_DATE = _dt.date(2004, 3, 26)

# Effective date of the quotation / multiplier rescaling (CFE IC07-03, saved+hashed).
RESCALING_EFFECTIVE = _dt.date(2007, 3, 26)

OPEN_END = _dt.date(9999, 12, 31)


class SpecSpan(NamedTuple):
    start: _dt.date
    end: _dt.date              # inclusive
    m_quoted: float            # $ per quoted point
    tick_quoted: float         # quoted points
    tick_documented: bool      # False -> the section G conservative fallback applies
    source_document: str       # file under data/vix/raw/specifications/
    note: str


SPEC_SPANS: Tuple[SpecSpan, ...] = (
    SpecSpan(
        start=VX_LISTING_DATE,
        end=RESCALING_EFFECTIVE - _dt.timedelta(days=1),
        m_quoted=100.0,
        tick_quoted=0.10,
        tick_documented=True,
        source_document="CFE-IC-2007-003.pdf",
        note=("Pre-rescaling practice: the futures price is ten times the VIX index "
              "(the Increased Value VIX, VBI), the multiplier is $100 and the minimum "
              "tick is $0.10 quoted = $10 per tick. On the common $1,000 basis: "
              "price_comparable = quoted/10, tick_comparable = 0.01."),
    ),
    SpecSpan(
        start=RESCALING_EFFECTIVE,
        end=OPEN_END,
        m_quoted=1000.0,
        tick_quoted=0.05,
        tick_documented=False,
        source_document="CFE-IC-2007-003.pdf + cboe_vx_contract_specifications.html",
        note=("Post-rescaling practice: the futures price is the VIX index itself and "
              "the multiplier is $1,000, so the quoted basis IS the common basis. "
              "IC07-03 documents a 0.01 index-point tick at the rescaling; the Cboe "
              "specification snapshot documents the current outright tick as 0.05 "
              "index points ($50.00). The transition date between them is NOT "
              "documented by an obtainable primary source, so the section G "
              "conservative fallback applies to the whole span: the LARGEST documented "
              "comparable tick, 0.05. Economically inert because "
              "max(0.10, tick) = 0.10 for every tick in [0.01, 0.05]."),
    ),
)

# Calendar months in which no standard monthly VX contract was ever listed. Established
# empirically and mechanically at acquisition: the Cboe archive endpoint serves a file
# for every neighbouring month and none for these, and the Cboe historical-data endpoint
# serves none either. These are LISTING-HISTORY facts, not data gaps: section F.3 orders
# contracts by final-settlement date and never assumes consecutive calendar months, and
# section F.6 decides the first eligible complete month mechanically from availability.
NEVER_LISTED_MONTHS: Tuple[str, ...] = ("2004-12", "2005-04", "2005-07", "2005-09")


def _span_for(d: _dt.date) -> SpecSpan:
    for span in SPEC_SPANS:
        if span.start <= d <= span.end:
            return span
    raise KeyError("no specification span covers %s; the break table has a gap" % d)


def multiplier_quoted(d: _dt.date) -> float:
    """$ per QUOTED point on date `d`."""
    return _span_for(d).m_quoted


def tick_quoted(d: _dt.date) -> float:
    """Minimum price increment in QUOTED points on date `d`."""
    return _span_for(d).tick_quoted


def conversion_factor(d: _dt.date) -> float:
    """M_quoted / $1,000 : the section F.5 conversion to the common economic basis."""
    return _span_for(d).m_quoted / COMMON_BASIS_MULTIPLIER


def price_comparable(price_quoted: float, d: _dt.date) -> float:
    """price_quoted * M_quoted / 1000  (section F.5)."""
    return price_quoted * conversion_factor(d)


def tick_comparable(d: _dt.date) -> float:
    """tick_quoted * M_quoted / 1000  (section F.5)."""
    span = _span_for(d)
    return span.tick_quoted * span.m_quoted / COMMON_BASIS_MULTIPLIER


def tick_is_documented(d: _dt.date) -> bool:
    return _span_for(d).tick_documented


def effective_multiplier(d: _dt.date, mini: bool = False) -> float:
    """The economic $ per COMPARABLE point actually held.

    On the common basis the standard contract is $1,000 per comparable point on every
    date - that is what the section F.5 conversion is for - and the mini contract is
    $100. The mini enters ONLY the section D.4 granularity check; it is never a
    pricing input.
    """
    return MINI_MULTIPLIER if mini else STANDARD_MULTIPLIER


def break_dates() -> List[_dt.date]:
    """The dated specification breaks inside the registry (start of each later span)."""
    return [span.start for span in SPEC_SPANS[1:]]


def covers_without_gaps(start: _dt.date, end: _dt.date) -> Tuple[bool, Optional[_dt.date]]:
    """Acceptance item 2: the break table covers every date in [start, end] with no gaps."""
    d = start
    while d <= end:
        try:
            _span_for(d)
        except KeyError:
            return False, d
        d += _dt.timedelta(days=1)
    return True, None


def registry_rows() -> List[Dict[str, object]]:
    """The dated break table, for the tracked specification-registry artifact."""
    rows: List[Dict[str, object]] = []
    for span in SPEC_SPANS:
        rows.append({
            "start": span.start.isoformat(),
            "end": "open" if span.end == OPEN_END else span.end.isoformat(),
            "m_quoted_usd_per_quoted_point": span.m_quoted,
            "tick_quoted_points": span.tick_quoted,
            "conversion_factor_to_common_basis": span.m_quoted / COMMON_BASIS_MULTIPLIER,
            "tick_comparable_points": span.tick_quoted * span.m_quoted / COMMON_BASIS_MULTIPLIER,
            "tick_documented": span.tick_documented,
            "source_document": span.source_document,
            "note": span.note,
        })
    return rows
