"""The structural start rule — contract section H.

    A decision date t is ELIGIBLE iff ALL hold:
      1. t is a canonical month-end in output/monthly_signal_panel.csv
      2. an eligible vintage exists at t for each ALFRED leg
      3. that vintage contains enough reference months for the sealed transform:
           growth    >= 13 monthly observations
           inflation >= 25 monthly observations
      4. an announced policy target exists at or before t
      5. canonical ETF price data exist at t
    Dates failing any condition are EXCLUDED, COUNTED and REPORTED - never
    imputed.

    NO start date may be chosen on performance.

The rule is STRUCTURAL: it reads coverage, never a macro value's direction, so
evaluating it reveals nothing about the candidate. It returns an explicit
per-condition reason for every excluded date, because section H requires
exclusions to be counted and reported rather than silently trimmed.
"""

from __future__ import annotations

import datetime as dt
from typing import Mapping, NamedTuple

from .legs import GROWTH_MONTHS_REQUIRED, INFLATION_MONTHS_REQUIRED
from .pit import UNDEFINED, _as_date, require_months

#: Contract section H, in order. A date is excluded on the FIRST condition it
#: fails, so the reason is deterministic rather than "one of several".
CONDITIONS = (
    "not_canonical_month_end",
    "no_eligible_growth_vintage",
    "insufficient_growth_history",
    "no_eligible_inflation_vintage",
    "insufficient_inflation_history",
    "no_announced_policy_target",
    "no_canonical_price_data",
)


class Eligibility(NamedTuple):
    date: dt.date
    eligible: bool
    reason: str | None


def evaluate_date(t, *, canonical_month_ends, indpro, payems, cpi,
                  policy_schedule, priced_instruments) -> Eligibility:
    """Apply the sealed structural rule to one decision date.

    Parameters mirror the contract's five conditions one-for-one. ``indpro``,
    ``payems`` and ``cpi`` are `pit.VintageSeries`; ``policy_schedule`` is a
    `policy.PolicySchedule`; ``priced_instruments`` is the set of mapped
    instruments with canonical price data at ``t``.
    """
    d = _as_date(t)

    if d not in {_as_date(x) for x in canonical_month_ends}:
        return Eligibility(d, False, "not_canonical_month_end")

    for series, label in ((indpro, "growth"), (payems, "growth")):
        snap = series.as_of(d)
        if not snap:
            return Eligibility(d, False, "no_eligible_growth_vintage")
        if not require_months(snap, max(snap), GROWTH_MONTHS_REQUIRED):
            return Eligibility(d, False, "insufficient_growth_history")

    csnap = cpi.as_of(d)
    if not csnap:
        return Eligibility(d, False, "no_eligible_inflation_vintage")
    if not require_months(csnap, max(csnap), INFLATION_MONTHS_REQUIRED):
        return Eligibility(d, False, "insufficient_inflation_history")

    now, then = policy_schedule.eligible_pair(d)
    if now is UNDEFINED or then is UNDEFINED:
        return Eligibility(d, False, "no_announced_policy_target")

    if not priced_instruments:
        return Eligibility(d, False, "no_canonical_price_data")

    return Eligibility(d, True, None)


def summarise(results) -> Mapping:
    """Counts per exclusion reason, so nothing is dropped without a tally."""
    counts = {r: 0 for r in CONDITIONS}
    counts["eligible"] = 0
    for r in results:
        if r.eligible:
            counts["eligible"] += 1
        else:
            counts[r.reason] += 1
    return counts
