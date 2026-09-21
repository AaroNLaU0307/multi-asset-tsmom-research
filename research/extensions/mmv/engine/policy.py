"""Administered-policy resolution on ANNOUNCEMENT authority.

Contract section B.1:

    POLICY  (FOMC target)   OFFICIAL FOMC / FEDERAL RESERVE ANNOUNCEMENT DATE
                            AND TIME.
                            ALFRED vintage reconstruction is NOT required and
                            NOT used.
                            ALFRED_REALTIME_START_USED_FOR_AVAILABILITY = NO

and section C.2:

    announcement time <= 15:45 ET  -> the newly announced target/range IS
                                      eligible at t
    announcement time >  15:45 ET  -> the PREVIOUS target/range remains eligible
    time not authoritatively establishable
                                   -> the PREVIOUS target/range remains eligible

The guarantee against the S1 audit finding is STRUCTURAL, not merely tested.
`realtime_start` is not a parameter of anything in this module: `spliced_target`
accepts ``(effective_date, value)`` pairs only, and `PolicySchedule` accepts
announcement stamps only. There is no code path by which a FRED catalog stamp
could reach an eligibility decision, so the defect the S1 freeze surfaced —
DFEDTAR carrying a single realtime_start of 2008-12-15 across twenty-six years,
DFEDTARU stamping 2014-04-03 on a range public since 2008-12-16 — cannot be
reintroduced by a later edit without deleting the type signature that forbids it.
"""

from __future__ import annotations

import datetime as dt
from fractions import Fraction
from typing import Iterable, Mapping, NamedTuple, Sequence

from . import CUTOFF_HOUR, CUTOFF_MINUTE
from .pit import UNDEFINED, ContractViolation, _as_date, parse_value

CUTOFF_TIME = dt.time(CUTOFF_HOUR, CUTOFF_MINUTE)

#: Contract section D.3. DFEDTAR is authoritative THROUGH this date; the target
#: RANGE is authoritative FROM the following day. Verified contiguous against
#: the frozen bytes by S1 pre-seal check B7 — no gap, no overlap.
SPLICE_LAST_SINGLE = dt.date(2008, 12, 15)
SPLICE_FIRST_RANGE = dt.date(2008, 12, 16)

#: Contract section D.3, FORBIDDEN as alternatives. DGS2 is permanently excluded
#: because it is a traded price mechanically tied to SHY/IEF/TLT inside the
#: traded panel.
FORBIDDEN_POLICY_SERIES = frozenset({"FEDFUNDS", "DGS2", "DFF", "EFFR", "SOFR"})


class PolicyAnnouncement(NamedTuple):
    """One official announcement of an administered target or target range.

    announced_on
        The official FOMC / Federal Reserve announcement DATE.
    announced_at
        The official clock time in America/New_York, or None when the authority
        published none. None is a recorded FINDING, not a placeholder to be
        filled in later with a plausible value.
    target
        The administered target, already spliced (single target before
        2008-12-16, range midpoint from 2008-12-16). Exact Fraction.
    """

    announced_on: dt.date
    announced_at: dt.time | None
    target: Fraction


class PolicySchedule:
    """The announcement-authority view of the administered policy target.

    Deliberately knows nothing about ALFRED. It cannot be constructed from
    vintage metadata because it accepts no vintage metadata.
    """

    def __init__(self, announcements: Iterable[PolicyAnnouncement]):
        self._ann: Sequence[PolicyAnnouncement] = tuple(
            sorted(announcements, key=lambda a: a.announced_on))
        for a, b in zip(self._ann, self._ann[1:]):
            if a.announced_on == b.announced_on:
                raise ContractViolation(
                    "two announcements share the date %s; the schedule must be "
                    "unambiguous at the cutoff" % a.announced_on)

    def __len__(self) -> int:
        return len(self._ann)

    def eligible(self, cutoff):
        """The target eligible at ``cutoff``, or UNDEFINED.

        An announcement made on an EARLIER day is always eligible. One made on
        the cutoff day is eligible only when the authority published a time at
        or before 15:45 ET. With no published time the previous target is
        retained — the rule does not assume the release was early.
        """
        cd = _as_date(cutoff)
        best = UNDEFINED
        for a in self._ann:
            if a.announced_on > cd:
                break
            if a.announced_on == cd and not self._same_day_admissible(a):
                continue
            best = a.target
        return best

    def _same_day_admissible(self, a: PolicyAnnouncement) -> bool:
        if a.announced_at is None:
            return False                      # not establishable -> previous
        return a.announced_at <= CUTOFF_TIME

    def eligible_pair(self, cutoff, months: int = 12):
        """(target at cutoff, target 12 months before cutoff).

        Both legs resolve under the SAME announcement rule. The lagged leg is
        not exempt: a target that was not yet public a year ago was not public
        a year ago, whatever later data says.
        """
        cd = _as_date(cutoff)
        return self.eligible(cd), self.eligible(_shift_months(cd, -months))


def _shift_months(d: dt.date, n: int) -> dt.date:
    y, m = d.year, d.month + n
    while m <= 0:
        m += 12
        y -= 1
    while m > 12:
        m -= 12
        y += 1
    day = d.day
    while True:
        try:
            return dt.date(y, m, day)
        except ValueError:
            day -= 1                          # month-end clamp, e.g. 31 -> 30


def spliced_target(effective_date, single: Mapping, lower: Mapping,
                   upper: Mapping):
    """The administered target in effect on ``effective_date``, per section D.3.

        target = DFEDTAR                       through 2008-12-15
               = midpoint(DFEDTARL, DFEDTARU)  from  2008-12-16 onward

    ``single``/``lower``/``upper`` map effective date -> value. They carry NO
    realtime metadata, by design: this function cannot consult a FRED catalog
    stamp because it is never given one.
    """
    d = _as_date(effective_date)
    if d <= SPLICE_LAST_SINGLE:
        v = single.get(d, UNDEFINED)
        return parse_value(v) if isinstance(v, str) else v
    lo = lower.get(d, UNDEFINED)
    hi = upper.get(d, UNDEFINED)
    lo = parse_value(lo) if isinstance(lo, str) else lo
    hi = parse_value(hi) if isinstance(hi, str) else hi
    if lo is UNDEFINED or hi is UNDEFINED:
        return UNDEFINED
    if hi < lo:
        raise ContractViolation(
            "target range upper bound %s is below lower bound %s on %s"
            % (hi, lo, d))
    return (lo + hi) / 2


def assert_splice_contiguous(single_dates: Iterable[dt.date],
                             range_dates: Iterable[dt.date]) -> None:
    """Fail loudly on a gap or an overlap at the 2008-12-15/16 boundary.

    A silent overlap would let two different definitions of "the target" be
    live on the same day; a silent gap would make the leg undefined for a
    stretch that has nothing to do with macro information. Either would move
    the Gate 0.5 denominator, so neither may pass quietly.
    """
    s = {_as_date(d) for d in single_dates}
    r = {_as_date(d) for d in range_dates}
    overlap = {d for d in s if d >= SPLICE_FIRST_RANGE}
    gap = {d for d in r if d <= SPLICE_LAST_SINGLE}
    if overlap:
        raise ContractViolation(
            "single-target series extends past the splice: %s"
            % sorted(overlap)[:5])
    if gap:
        raise ContractViolation(
            "range series starts before the splice: %s" % sorted(gap)[:5])
    if s and r:
        if max(s) >= SPLICE_FIRST_RANGE or min(r) <= SPLICE_LAST_SINGLE:
            raise ContractViolation("splice boundary is not contiguous")
