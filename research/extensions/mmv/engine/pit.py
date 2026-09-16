"""Latest-known-as-of vintage resolution for the ALFRED legs.

Contract section B.1 and C.1, implemented literally:

    eligible vintage at t = the LATEST vintage whose vintage date <= t.
    Within that vintage, use the newest reference observation eligible at t.
    A vintage dated AFTER t may never be consulted.
    Same-day vintage whose release time cannot be authoritatively established
      -> use the PRIOR eligible vintage. Do not guess.

The two-step shape matters and is deliberate. Selecting the eligible VINTAGE
DATE first, and only then reading observations from it, is what makes the
same-day rule expressible at all: a one-step "realtime interval contains t"
filter silently admits a vintage published at 17:00 on the decision day.

No macro value is ever parsed as a float. Values arrive as decimal strings and
are carried as Fraction, so every downstream sign is exact and the contract's
"no floating-point epsilon" clause is satisfied by construction rather than by
a tolerance.
"""

from __future__ import annotations

import datetime as dt
from fractions import Fraction
from typing import Iterable, Mapping, Sequence

from . import CUTOFF_HOUR, CUTOFF_MINUTE

#: The single sentinel for "not available at this cutoff". It is NEVER 0.
#: Contract section E.3: MISSING is never converted to zero.
UNDEFINED = None

#: ALFRED's own marker for a reference date carrying no value in a vintage.
NO_VALUE = "."

CUTOFF_TIME = dt.time(CUTOFF_HOUR, CUTOFF_MINUTE)


class ContractViolation(RuntimeError):
    """Raised when input cannot be served without breaking a sealed clause.

    Never caught internally and never softened into a default. A sealed clause
    that cannot be honoured is an Owner matter (contract section N), so the
    engine stops rather than repairing the science in code.
    """


def _as_date(d) -> dt.date:
    if isinstance(d, dt.datetime):
        return d.date()
    if isinstance(d, dt.date):
        return d
    return dt.date.fromisoformat(str(d)[:10])


def parse_value(raw: str):
    """Exact numeric parse of an ALFRED observation value.

    Returns UNDEFINED for ALFRED's "." marker, otherwise an exact Fraction.
    Never returns a float: sign comparisons downstream must be exact.
    """
    if raw is None:
        return UNDEFINED
    s = str(raw).strip()
    if s == "" or s == NO_VALUE:
        return UNDEFINED
    return Fraction(s)


class VintageSeries:
    """One ALFRED series held as its full real-time (output_type=1) history.

    Parameters
    ----------
    observations
        Rows exactly as ALFRED returns them: ``date``, ``realtime_start``,
        ``realtime_end``, ``value``.
    release_times
        Optional authoritative clock times for vintage dates, keyed by vintage
        date. A vintage date ABSENT from this mapping has no authoritative
        time, which under the sealed rule makes it ineligible on its own day.
        Supplying a time here is an assertion that the authority published it.
    """

    def __init__(self, series_id: str, observations: Iterable[Mapping],
                 release_times: Mapping[dt.date, dt.time] | None = None):
        self.series_id = series_id
        self._obs = []
        starts = set()
        for o in observations:
            rec = (_as_date(o["date"]), _as_date(o["realtime_start"]),
                   _as_date(o["realtime_end"]), o["value"])
            self._obs.append(rec)
            starts.add(rec[1])
        self._obs.sort(key=lambda r: (r[0], r[1]))
        #: Every distinct realtime_start IS a vintage date for this series.
        self.vintage_dates: Sequence[dt.date] = tuple(sorted(starts))
        self.release_times = dict(release_times or {})

    # -- vintage selection ------------------------------------------------

    def eligible_vintage(self, cutoff) -> dt.date | None:
        """The latest vintage date usable at ``cutoff``, or None.

        A vintage strictly BEFORE the cutoff date is always eligible: it was
        published on an earlier day, so it was public by 15:45 on this one.

        A vintage ON the cutoff date is eligible only when the authority
        published a clock time for it AND that time is at or before 15:45.
        With no authoritative time the sealed rule falls back to the PRIOR
        eligible vintage — it does not guess, and it does not admit the
        same-day release on the assumption that it was probably early.

        A vintage AFTER the cutoff date is never eligible.
        """
        cd = _as_date(cutoff)
        best = None
        for v in self.vintage_dates:
            if v > cd:
                break
            if v == cd and not self._same_day_admissible(v):
                continue
            best = v
        return best

    def _same_day_admissible(self, vintage: dt.date) -> bool:
        t = self.release_times.get(vintage)
        if t is None:
            return False                     # not establishable -> prior info
        return t <= CUTOFF_TIME

    # -- reconstruction ---------------------------------------------------

    def as_of(self, cutoff) -> dict:
        """The reference history as publicly known at ``cutoff``.

        Returns ``{reference_date: Fraction}`` for the eligible vintage, with
        valueless reference dates OMITTED rather than zero-filled. An empty
        dict means no eligible vintage exists, which is a real state the
        structural start rule consumes — not an error.
        """
        v = self.eligible_vintage(cutoff)
        if v is None:
            return {}
        out = {}
        for ref, rt_start, rt_end, raw in self._obs:
            if rt_start <= v <= rt_end:
                val = parse_value(raw)
                if val is not UNDEFINED:
                    out[ref] = val
        return out

    def latest_reference(self, cutoff) -> dt.date | None:
        """Newest reference month with a value in the eligible vintage."""
        snap = self.as_of(cutoff)
        return max(snap) if snap else None

    # -- diagnostic-only alternative information concept -------------------

    def first_release_chain(self) -> dict:
        """Reference date -> its FIRST published value (ALFRED output_type=4).

        Contract section B: the first-release chain is a DESCRIPTIVE
        CONCORDANCE DIAGNOSTIC with no promotion, rescue or kill power. It is
        exposed here so the sealed diagnostic can be built, never so that a
        result may be rescued by swapping information concepts.
        """
        out = {}
        for ref, rt_start, _rt_end, raw in self._obs:
            val = parse_value(raw)
            if val is UNDEFINED:
                continue
            if ref not in out or rt_start < out[ref][0]:
                out[ref] = (rt_start, val)
        return {ref: val for ref, (_start, val) in out.items()}


def months_back(ref: dt.date, n: int) -> dt.date:
    """The reference month ``n`` months before ``ref``, day component kept.

    Monthly ALFRED reference dates are first-of-month, so this is exact and
    needs no calendar library.
    """
    y, m = ref.year, ref.month - n
    while m <= 0:
        m += 12
        y -= 1
    while m > 12:
        m -= 12
        y += 1
    return dt.date(y, m, ref.day)


def require_months(snapshot: Mapping, newest: dt.date, needed: int) -> bool:
    """True iff ``snapshot`` carries the exact months the transform reads.

    Not a count of rows: the sealed transforms read SPECIFIC lags, so a
    snapshot with 40 assorted months but a hole at m-12 cannot serve them.
    Checking the actual lags is the difference between a coverage claim and a
    computability claim.
    """
    return all(months_back(newest, k) in snapshot for k in range(needed))
