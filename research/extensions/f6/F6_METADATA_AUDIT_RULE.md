# CTA-EDGE-05 / F6 — METADATA AUDIT RULE

**Frozen BEFORE the substantive eligible F6 event sample was enumerated.**

```
RECORD_TYPE = SCHEDULE_PIT_METADATA_AUDIT_RULE
LINEAGE     = CTA-EDGE-05 (F6 MACRO_ANNOUNCEMENT_PREMIUM)
DATE        = 2026-09-20
RULE_ID     = F6-AUDIT-RULE-1
SCOPE       = schedule / calendar metadata and design feasibility ONLY.
              No SPY return, no control return, no beta_EVENT, no Sharpe,
              no interval, no LOYO performance, no TLT, no F6.b, no surprise.
```

**Why frozen first.** An event-study feasibility audit that picks its event
list after seeing which dates are convenient will always report that the
calendar works. The hierarchy, the inclusion test and the failure semantics
below are fixed before the sample exists.

---

## §0 Retrieval position at the moment of freezing

```
SUBSTANTIVE ELIGIBLE F6 EVENT SAMPLE ENUMERATED BEFORE THIS FREEZE = NONE
```

What was read before freezing, and is permitted because none of it is the
eligible sample: the **structure and limitations** of the candidate authorities
— column sets, series coverage, per-year row counts, whether a time column
exists, and whether a scheduled/unscheduled flag exists. Establishing that an
authority is *unfit* is part of writing the hierarchy, not part of selecting
events.

No SPY price, no return and no event outcome of any kind was touched.

---

## §1 Authoritative source hierarchy

Applied in order. A lower tier may never override a higher one, and a tier is
used only for what it actually establishes.

```
TIER 1  THE PUBLISHER'S OWN SCHEDULE DOCUMENT
        CPI / NFP : BLS annual release schedules (published a year ahead)
        FOMC      : the Federal Reserve's own meeting calendars, including the
                    Fed's own "(unscheduled)" and "(cancelled)" annotations

TIER 2  A PINNED REPOSITORY AUTHORITY DERIVED FROM TIER 1
        research/extensions/ta/TA_MACRO_CALENDAR.csv
          sha256 8f10675033267136cb2622bf...   755 rows, series CPI/FOMC/NFP/QRA
          columns: series,date,weekday,source,source_url,detail
        research/extensions/mmv/mmv_policy_schedule_freeze.py
          scheduled_meeting_end_dates() -> (scheduled, unscheduled, sources),
          which parses the Fed's own annotations and was validated 33/33 at the
          MMV policy freeze.

TIER 3  NOTHING. There is no tier 3. A date with no tier-1 or tier-2 support is
        NOT an F6 event, and is listed as unsupported rather than inferred.
```

**Heuristics are barred as authority.** "First Friday" for NFP, "second day of
a two-day meeting" for FOMC, and "mid-month Wednesday" for CPI may be used as
**cross-checks that can raise an exception**, never as the source of an event
date.

### §1.1 A tier-2 authority already known to be unfit for one purpose

`TA_MACRO_CALENDAR.csv` is fit for **CPI and NFP dates**. It is **NOT fit, on
its own, to define the F6 FOMC event**, and this was established before the
freeze:

```
its `detail` field is uniformly "FOMC statement" for all 171 FOMC rows — it
carries NO scheduled/unscheduled distinction, yet it demonstrably contains
UNSCHEDULED actions (2007-08-10, 2008-03-11, 2008-10-08, 2010-05-09,
2019-10-11, 2020-03-03, 2020-03-15, 2020-03-23), and it is MISSING the
2008-01-22 intermeeting action entirely.
```

So the FOMC event list is formed at **tier 1 / tier 2 via the Fed's own
annotations**, and `TA_MACRO_CALENDAR` is used for FOMC only as a
cross-check.

---

## §2 What proves an event was SCHEDULED BEFORE ENTRY

This is the load-bearing test, because F6 enters at `close(t-1)`.

```
SCHEDULED_BEFORE_ENTRY(e) is satisfied only if the event's date was fixed by a
publisher schedule document issued STRICTLY BEFORE close(t-1), where t is the
event trading session.

CPI / NFP : BLS publishes the following year's release schedule in advance, so
            an event on date t is scheduled-before-entry iff it appears on the
            BLS annual schedule for its year.
FOMC      : the Fed publishes its meeting calendar years ahead, so a SCHEDULED
            meeting end date qualifies. An UNSCHEDULED action does NOT, by
            definition — it was not knowable at close(t-1) — and is EXCLUDED
            from the primary, not merely flagged.
```

```
AN UNSCHEDULED ACTION CAN NEVER SATISFY THIS TEST. Including one would be
look-ahead, whatever its economic interest.
```

## §3 What proves release DATE and TIME

```
DATE  established when a tier-1 or tier-2 authority names it.
TIME  established only when a publisher document states a clock time with a
      timezone. A date alone is NOT a time.
```

**If the release time is not established from a publisher document, it is
recorded as `NOT_ESTABLISHED` and never guessed.** The MMV precedent governs:
an unestablished clock time is reported, not imputed.

For F6's conceptual trade — enter `close(t-1)`, exit `close(t)` — the time
matters for exactly one question: whether the release falls **within session t**
rather than after its close. A release known only by date is therefore a
**HOLD-level metadata gap for that event**, not an automatic exclusion, and the
count of such events is reported.

## §4 Calendar revisions, postponements, shutdowns

```
REVISION TO A PUBLISHED SCHEDULE
  the schedule in force AT close(t-1) governs. A later-published correction
  does NOT retroactively change eligibility.

POSTPONEMENT KNOWN ONLY AFTER ENTRY
  the ORIGINAL PLANNED TRADE DATE IS RETAINED, per the controller's
  instruction, and the occurrence is RECORDED. No ex-post correction is made.
  This is the honest treatment: the trade really would have been entered.

SHUTDOWN / SUSPENSION
  a release cancelled or indefinitely suspended before close(t-1) is NOT an
  event. One postponed to a later date creates an event on the NEW date if that
  new date was itself published before ITS close(t-1); the original date is
  handled by the postponement rule above.

Every such case is enumerated individually. None is silently dropped.
```

## §5 Unscheduled FOMC actions — excluded, and what "unscheduled" means

```
EXCLUDED from the primary: emergency / intermeeting actions, unscheduled
statements, conference calls, cancelled meetings, minutes releases, speeches,
testimony, press conferences that are not the statement release.

INCLUDED: the officially scheduled FOMC POLICY-STATEMENT RELEASE only.

The classification comes from the FED'S OWN annotation, not from this audit's
judgement and not from a date heuristic.
```

## §6 Event-to-NYSE-session mapping

```
TRADING SESSIONS are the dates present in the frozen ETF panel
data/close_prices_raw.csv (sha256 3d2a7a56dbd92d4ff8138cfd...), which IS the
execution calendar for this study. A date absent from the panel is not a
session.

MAPPING
  release on a trading session      -> that session is the EVENT SESSION t
  release on a NON-trading day      -> the NEXT trading session is t
                                       (the information is first tradeable then)
  entry session t-1                 -> the trading session immediately PRIOR to
                                       t in the panel index
  HOLD(t)                           -> calendar days between close(t-1) and
                                       close(t), capturing weekends and holidays
```

Good Friday, NYSE holidays and early closes are handled by this rule
automatically, because the panel's own index defines the sessions. Early closes
are **not** treated specially and the count of event sessions falling on an
early close is reported.

## §7 Same-day multiple events

```
ONE EVENT TRADING DAY = ONE unit weight, ONE trade, ONE primary observation,
                        ONE position, ONE return.
NO DOUBLE NOTIONAL under any circumstance.
Multiple event-family LABELS are retained for DIAGNOSTICS ONLY.
```

## §8 Missing-document semantics

```
A required document that cannot be retrieved is LISTED EXPLICITLY, with the
date and what was sought. No imputation, no substitution from an adjacent
year's schedule, no cross-family filling, no heuristic backfill.
A retrieval failure is reported as a TRANSPORT limitation and is NEVER recorded
as a source deficiency unless the publisher itself is shown not to hold it.
```

## §9 PASS / HOLD / PARK

```
PER-FAMILY (CPI, NFP, FOMC)
  PASS  every event in the window has an establishable date from tier 1 or 2,
        the scheduled-before-entry test is satisfiable for all of them, and the
        scheduled/unscheduled distinction is decidable from source
  HOLD  the family is usable but at least one metadata element is unestablished
        (typically clock time), or one classification needs a publisher document
        not yet retrieved
  PARK  the family's event list cannot be formed from source at all, or the
        scheduled-before-entry test cannot be satisfied

EVENT_SCHEDULE_PIT_GATE = the WEAKEST of the three families.

DESIGN MATRIX
  the fixed control model is the ONLY model. If the metadata design matrix is
  RANK DEFICIENT, or EVENT is perfectly predicted by the controls, the result
  is HOLD. A second model is NOT invented, and no column is dropped to rescue
  rank.
```

```
FAIL-CLOSED. Any element that cannot be established from source leaves its
family at HOLD or PARK. Nothing is upgraded by assumption, and no gap is
closed by a heuristic.
```

## §10 Forbidden throughout

```
SPY event return · SPY control return · mean return · beta_EVENT · Sharpe ·
confidence interval · LOYO performance · TLT returns · F6.b pre-FOMC drift ·
pre/post-2015 return differences · NQ outcome data · consensus forecasts ·
actual release values · surprise values · post-release direction ·
date or control optimisation
```

Reading **schedule metadata** — dates, times, weekday, holiday and auction
calendars — is the purpose of this audit and is classified
`DESIGN_INFORMING_MEASUREMENT` on non-target inputs. It may never be joined to
a price.
