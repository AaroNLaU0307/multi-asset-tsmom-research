# -*- coding: utf-8 -*-
"""CTA-EDGE-05 / F6 — GENERALIZED SCHEDULED-STATEMENT FILTER.

F6's semantic event is the SCHEDULED POST-MEETING POLICY-STATEMENT RELEASE.
The reused MMV parser classifies Federal Reserve calendar entries as scheduled
or unscheduled from the Fed's own parenthesised annotation, and correctly drops
"(cancelled)" entries and "Conference Call" entries. It has ONE blind spot for
F6's purpose, established from source:

    the Fed's CURRENT calendar renders a notation vote as

        August 22 (notation vote) Statement on Longer-Run Goals and
        Monetary Policy Strategy

    and the parser's current-calendar keyword is "Statement". The text after
    the annotation therefore STARTS WITH the keyword, the annotation contains
    neither "cancel" nor "unscheduled", and the entry is admitted as a
    SCHEDULED MEETING. It is not one: it is a framework-statement notation
    vote with no meeting behind it.

This module adds the missing discriminators WITHOUT touching the MMV file and
WITHOUT any per-year count heuristic, so it behaves correctly even when a
NOTATION VOTE and a CANCELLED MEETING fall in the same calendar year.

METADATA ONLY. No policy outcome, no rate, no return is read.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for p in (REPO, os.path.join(REPO, "research", "extensions", "mmv")):
    if p not in sys.path:
        sys.path.insert(0, p)

import mmv_policy_schedule_freeze as M          # noqa: E402

#: Annotations that disqualify an entry from being a scheduled MEETING.
#: Each is the Fed's own word, matched case-insensitively inside the
#: parenthesised annotation. None of these is a count heuristic.
DISQUALIFYING_ANNOTATIONS = ("cancel", "notation")

#: An entry the Fed marks this way is a real FOMC action but NOT a scheduled
#: meeting, and is returned separately rather than silently dropped.
UNSCHEDULED_ANNOTATION = "unscheduled"

#: In the CURRENT calendar a POST-MEETING policy statement is rendered with a
#: colon that introduces the document links ("Statement: PDF | HTML"). A
#: different Fed document is rendered as prose ("Statement on Longer-Run
#: Goals ..."). This is a second, independent discriminator.
POST_MEETING_STATEMENT_RE = re.compile(r"^Statement\s*:")
OTHER_STATEMENT_RE = re.compile(r"^Statement\s+on\b")


def classify_entry(text: str, end: int, keyword: str):
    """Classify the calendar entry whose date match ends at ``end``.

    Returns one of:
        ("scheduled",   annot)   a scheduled meeting entry
        ("unscheduled", annot)   an FOMC action the Fed labels unscheduled
        ("reject",      reason)  not a meeting entry at all

    The window and the case-sensitivity rules are MMV's, kept deliberately:
    a loose window lets prose such as "minutes of January 29/30 meeting" match,
    and a spurious scheduled date can only ever HIDE an intermeeting action.
    """
    w = text[end:end + 120].lstrip(" *–-")
    annot = ""
    if w.startswith("("):
        close = w.find(")")
        if close == -1 or close > 32:
            return "reject", "malformed annotation"
        annot = w[1:close].strip().lower()
        w = w[close + 1:].lstrip()

    if w.startswith("Conference Call"):
        return "reject", "conference call"
    for bad in DISQUALIFYING_ANNOTATIONS:
        if bad in annot:
            return "reject", "annotation:%s" % bad
    if not w.startswith(keyword):
        return "reject", "keyword mismatch"
    if keyword == "Statement":
        if OTHER_STATEMENT_RE.match(w):
            return "reject", "not a post-meeting statement"
        if not POST_MEETING_STATEMENT_RE.match(w):
            return "reject", "statement not in post-meeting link form"
    if UNSCHEDULED_ANNOTATION in annot:
        return "unscheduled", annot
    return "scheduled", annot


def _entries(text, year, keyword):
    """Date-bearing calendar entries, slash forms first (MMV's masking trick)."""
    out, chars = [], list(text)
    for m in M.CAL_SLASH_RE.finditer(text):
        m1, m2, _d1, d2 = m.groups()
        kind, why = classify_entry(text, m.end(), keyword)
        em = M._month_num(m2)
        ey = year + 1 if em < M._month_num(m1) else year
        try:
            d = dt.date(ey, em, int(d2))
        except ValueError:
            continue
        out.append((d, kind, why))
        for i in range(m.start(), m.end()):
            chars[i] = " "
    masked = "".join(chars)
    for m in M.CAL_SINGLE_RE.finditer(masked):
        mon, d1, d2 = m.groups()
        kind, why = classify_entry(masked, m.end(), keyword)
        try:
            d = dt.date(year, M._month_num(mon), int(d2 or d1))
        except ValueError:
            continue
        out.append((d, kind, why))
    return out


def scheduled_statement_dates():
    """(scheduled, unscheduled, rejected, sources) from the Fed's own pages."""
    sched, unsched, rejected, sources = {}, {}, {}, []

    for year in M.HISTORICAL_CAL_YEARS:
        url = M.HISTORICAL_CAL % year
        raw, _ = M.fetch(url, allow_404=True)
        if raw is None:
            continue
        sources.append({"url": url, "sha256": hashlib.sha256(raw).hexdigest()})
        text = M.plain(raw)
        for d, kind, why in _entries(text, year, M.HISTORICAL_KEYWORD):
            if kind == "scheduled":
                sched.setdefault(d, url)
            elif kind == "unscheduled":
                unsched.setdefault(d, url)
            elif why.startswith("annotation:"):
                rejected.setdefault(d, why)
        for m in re.finditer(r"\b(%s)\s+(\d{1,2})\s+Conference\s+Call"
                             % M.MONTH_TOKEN, text):
            try:
                unsched.setdefault(
                    dt.date(year, M._month_num(m.group(1)),
                            int(m.group(2))), url)
            except ValueError:
                pass

    raw, _ = M.fetch(M.CURRENT_CAL)
    sources.append({"url": M.CURRENT_CAL,
                    "sha256": hashlib.sha256(raw).hexdigest()})
    text = M.plain(raw)
    # The current calendar carries several YEARS on one page. It MUST be
    # segmented into per-year blocks first (MMV's YEAR_BLOCK_RE); parsing the
    # whole page once per year assigns every date-like token to every year and
    # manufactures ~46 spurious "scheduled" dates a year.
    blocks = list(M.YEAR_BLOCK_RE.finditer(text))
    for i, b in enumerate(blocks):
        year = int(b.group(1))
        stop = blocks[i + 1].start() if i + 1 < len(blocks) else len(text)
        chunk = text[b.end():stop]
        for d, kind, why in _entries(chunk, year, M.CURRENT_KEYWORD):
            if kind == "scheduled":
                sched.setdefault(d, M.CURRENT_CAL)
            elif kind == "unscheduled":
                unsched.setdefault(d, M.CURRENT_CAL)
            elif why.startswith("annotation:") or why.startswith("not a post"):
                rejected.setdefault(d, why)

    for d in list(sched):
        if d in unsched:
            del sched[d]

    # PARSE-LOSS ALARM, not a classification rule. A calendar format change
    # that silently dropped entries would otherwise reclassify scheduled
    # meetings as absent and still exit cleanly. MMV uses the same guard.
    import collections
    per = collections.Counter(d.year for d in sched)
    thin = sorted(y for y, n in per.items()
                  if n < M.MIN_SCHEDULED_MEETINGS_PER_YEAR
                  and y < dt.date.today().year)
    if thin:
        print("PARSE-LOSS ALARM: thin years %s (per-year %s)"
              % (thin, dict(sorted(per.items()))), file=sys.stderr)

    return (sorted(sched), sorted(unsched),
            {str(k): v for k, v in sorted(rejected.items())}, sources)


# --------------------------------------------------------------------------- #
# Self-test: the rule must survive a notation vote AND a cancelled meeting in
# the SAME year, which is precisely what a per-year count heuristic cannot do.
# --------------------------------------------------------------------------- #
FIXTURE = (
    "January 27-28 Statement: PDF | HTML Minutes "
    "March 17-18 (cancelled) Statement: PDF | HTML "
    "April 28-29 Statement: PDF | HTML "
    "June 9-10 Statement: PDF | HTML "
    "July 28-29 Statement: PDF | HTML "
    "August 22 (notation vote) Statement on Longer-Run Goals and Monetary "
    "Policy Strategy "
    "September 15-16 Statement: PDF | HTML "
    "November 4-5 Statement: PDF | HTML "
    "December 15-16 Statement: PDF | HTML "
    "March 15 (unscheduled) Statement: PDF | HTML "
)


def selftest():
    got = _entries(FIXTURE, 2020, "Statement")
    sched = sorted(d for d, k, _ in got if k == "scheduled")
    unsch = sorted(d for d, k, _ in got if k == "unscheduled")
    rej = sorted((d, w) for d, k, w in got if k == "reject")
    ok = True
    exp_s = [dt.date(2020, m, d) for m, d in
             ((1, 28), (4, 29), (6, 10), (7, 29), (9, 16), (11, 5), (12, 16))]
    print("fixture: one cancelled meeting AND one notation vote in the SAME year")
    print("  scheduled   %d -> %s" % (len(sched), [str(d) for d in sched]))
    print("  unscheduled %d -> %s" % (len(unsch), [str(d) for d in unsch]))
    print("  rejected    %s" % [(str(d), w) for d, w in rej])
    if sched != exp_s:
        ok = False
        print("  FAIL scheduled set != expected %s" % [str(d) for d in exp_s])
    if dt.date(2020, 8, 22) in sched:
        ok = False
        print("  FAIL notation vote admitted as scheduled")
    if dt.date(2020, 3, 18) in sched:
        ok = False
        print("  FAIL cancelled meeting admitted as scheduled")
    if unsch != [dt.date(2020, 3, 15)]:
        ok = False
        print("  FAIL unscheduled set wrong")
    print("  SELFTEST %s" % ("PASS" if ok else "FAIL"))
    return ok


if __name__ == "__main__":
    sys.exit(0 if selftest() else 1)
