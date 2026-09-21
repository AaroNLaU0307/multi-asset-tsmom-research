# CTA-EDGE-04-MMV — POLICY ANNOUNCEMENT SCHEDULE FREEZE

```
LINEAGE                 = CTA-EDGE-04-MMV
TASK                    = PRE-GATE-0.5 POLICY AVAILABILITY FREEZE
POLICY_SCHEDULE_STATUS  = PASS
DATE                    = 2026-09-17
BRANCH                  = cta-edge/macro-momentum-vintage-s2
S2_COMMIT_VERIFIED      = dc2817b99f048f561f1db55f998e24ff2193df10

SCIENTIFIC_CHOICE                        = NONE
IMPLEMENTATION / DATA AUTHORITY COMPLETION = YES
```

This is a data-authority completion. It changes no sealed definition, reopens no
Owner decision, and creates no new one. It computes no macro feature.

---

## §1 What was missing

S2 correctly left `PolicySchedule` generic over an explicit announcement
sequence, because the sealed contract determines eligibility **given** a
schedule but does not say how to build one. This freeze builds it from official
Federal Reserve authority, one regime at a time.

---

## §2 Why no calendar rule could have done this

Each of the forbidden shortcuts fails on the actual record, and the evidence is
from the sources rather than from reasoning about them:

**The "date" columns everywhere are EFFECTIVE dates, not announcements.** The
Federal Reserve says so against itself, in a footnote on its own open-market
page:

> On July 10, 2024, this date was corrected from March 3, 2020, to March 4, 2020.

That intermeeting cut was *announced* on the 3rd and took effect on the 4th.

**A fixed publication lag is wrong somewhere, whichever lag is chosen.** The
observed announcement-minus-effective offsets are **both 0 and −1 days**: 0
through 2016, −1 from 2017-03-16 onward. FRED stamps 2015-12-16 and 2016-12-14
on the *announcement* day while the Fed's own table stamps 2015-12-17 and
2016-12-15, the stated effective day.

**A "latest calendar event ≤ effective date" rule misattributes intermeeting
actions.** The repository's committed `TA_MACRO_CALENDAR.csv` does not contain
**2008-01-22** at all. That rule would assign the January 2008 intermeeting cut
to the **2007-12-11** meeting — six weeks early — and the nearest-meeting rule
would assign it to 2008-01-30, eight days late. Both are asserted as regression
checks (E1, E2), computed live rather than asserted in prose.

---

## §3 How each regime was established

```
VALUES + EFFECTIVE DATES   frozen ALFRED/FRED bytes, pinned at S1
ANNOUNCEMENT               the OFFICIAL Federal Reserve press release that
                           STATES that exact target
ACCEPTANCE CRITERION       the latest candidate date whose press release
                           states the target. PROXIMITY IS NEVER THE CRITERION.
INTERMEETING FLAG          the Federal Reserve's own calendar label
                           ("Conference Call", "(unscheduled)", "(cancelled)")
```

Candidate dates run backwards from the effective date, but a candidate is
*accepted* only on document content. The validator re-opens all 42 cached pages
and re-confirms that each states the target attributed to it (check B1), so a
row whose source does not say what it claims cannot survive.

`realtime_start` is not merely unused — no function in the freeze takes a
`realtime`, `vintage` or `catalog` parameter, and the frozen schedule has no
such column (checks F1, F2).

---

## §4 Results

```
POLICY_EVENT_N            = 42
POLICY_SCHEDULE_START     = 2006-06-29   (effective), announced 2006-06-29
POLICY_SCHEDULE_END       = 2025-12-11   (effective), announced 2025-12-10
REGIMES_IN_FROZEN_SERIES  = 185  (42 of them are required by the sealed window)

OFFICIAL_SOURCE_COVERAGE  = 42 / 42 from federalreserve.gov, each hashed
VERIFIED_ANNOUNCEMENT_TIME     = 31
NOT_ESTABLISHED_ANNOUNCEMENT_TIME = 11
INTERMEETING_EVENT_N      = 4
```

**Window derivation.** The sealed decision window is 2008-05-31 … 2026-06-30.
The policy leg reads `target(t)` *and* `target(t − 12 months)`, so targets are
needed from **2007-05-31**, which requires the regime in force on that date —
the 5.25 % target effective 2006-06-29. Extending the MMV sample would require
extending this schedule.

### 4.1 The four intermeeting actions, each corroborated

| announced | effective | target | corroborating Federal Reserve calendar entry |
|---|---|---|---|
| 2008-01-22 | 2008-01-22 | 3.50 % | Conference Call, 2008-01-21 |
| 2008-10-08 | 2008-10-08 | 1.50 % | Conference Call, 2008-10-07 |
| 2020-03-03 | 2020-03-04 | 1.00–1.25 % | "March 2 (unscheduled) Meeting — Statement (Released March 3, 2020)" |
| 2020-03-15 | 2020-03-16 | 0–0.25 % | "March 15 (unscheduled) Meeting" |

Each is corroborated **positively**, by the Fed labelling an unscheduled meeting
or conference call — not by the date merely being absent from a scrape that
could have dropped it. The 2020-03-02 entry independently confirms the
content-verified announcement date of 2020-03-03.

### 4.2 Agreement with the frozen target series

```
TARGET_SERIES_MATCH        = YES   every value and midpoint reproduces exactly
TARGET_RANGE_SPLICE_MATCH  = YES   last single target 2008-10-29,
                                   first range 2008-12-16, DFEDTAR ends 2008-12-15
CHRONOLOGICAL / NO DUPLICATES = YES
NO UNEXPLAINED GAPS        = YES
REVISIONS IN POLICY SERIES = ZERO, across every vintage of all three series
```

The Federal Reserve's open-market table reproduces the **same ordered level
sequence** as the frozen regimes — a date-free confirmation that does not depend
on either source's stamping convention (check C5).

**One recorded discrepancy, not material.** FRED and the Fed disagree by one day
on the effective date of exactly two regimes:

| regime | FRED stamps | Federal Reserve stamps |
|---|---|---|
| 0.25–0.50 % | 2015-12-16 (announcement day) | 2015-12-17 (stated effective day) |
| 0.50–0.75 % | 2016-12-14 (announcement day) | 2016-12-15 (stated effective day) |

The **values are identical** and the **announcement dates are independently
established** from the statements themselves, which is what the sealed rule
reads. The discrepancy is therefore recorded rather than repaired, and neither
source was silently adjusted to match the other.

### 4.3 Announcement times

```
UNKNOWN_TIME_FALLBACK = PRIOR_TARGET
```

Eleven announcements carry **no official clock time**: the Federal Reserve's own
archived pages say only *"For immediate release"*. This is the same pattern S1
found for 2013-07-31 and 2014-04-30. **No time was invented for any of them**,
and the sealed conservative rule applies.

One verified time falls after the cutoff — 2020-03-15 at **17:00 ET**. It is a
Sunday and not a canonical decision date, so the rule is recorded rather than
applied (check G4).

---

## §5 Same-day reconciliation

```
SIX_MONTH_END_COLLISIONS_RECONCILED = YES
VERIFIED_TIME_COLLISION_N  = 1
UNKNOWN_TIME_COLLISION_N   = 2
```

The six pinned FOMC/month-end collisions are FOMC *meeting* dates. Only **one**
of them is also a target **change**:

| pinned collision | target change? | resolution |
|---|---|---|
| 2013-07-31 | no | no-change meeting; the sealed rule cannot alter the target |
| 2014-04-30 | no | as above |
| 2018-01-31 | no | as above |
| **2019-07-31** | **yes** | official time **2:00 p.m. EDT ≤ 15:45** → newly announced target eligible |
| 2024-01-31 | no | no-change meeting |
| 2024-07-31 | no | no-change meeting |

**A finding the S1 analysis did not enumerate, surfaced here.** The S1 six-date
list intersected FOMC dates with *decision* dates only. The policy leg also
reads a cutoff **12 months earlier**, and two of those lagged cutoffs are
themselves target-change announcement dates:

| cutoff | role | time status | eligible target |
|---|---|---|---|
| 2007-10-31 | lagged cutoff for the 2008-10-31 decision | NOT_ESTABLISHED | **PREVIOUS** target (rule fallback) |
| 2008-04-30 | lagged cutoff for the 2009-04-30 decision | NOT_ESTABLISHED | **PREVIOUS** target (rule fallback) |
| 2019-07-31 | decision date | VERIFIED 14:00 EDT | newly announced target |

This is the **same sealed rule** applied at the cutoff it was always defined on;
no new rule and no new choice. It is written down because a lagged cutoff
resolving silently is exactly the kind of thing that should not resolve
silently. `"For immediate release"` is **not** treated as evidence of a clock
time.

---

## §6 Validation

```
POLICY_SCHEDULE_VALIDATOR   = research/extensions/mmv/mmv_policy_schedule_validate.py
POLICY_SCHEDULE_CHECK_COUNT = 33
POLICY_SCHEDULE_CHECK_PASS  = 33
POLICY_SCHEDULE_CHECK_FAIL  = 0
```

| group | n | covers |
|---|---:|---|
| A direct authority | 4 | 42 regimes, cached pages present, hashes reproduce, every source on federalreserve.gov |
| B source says what the row claims | 2 | all 42 pages re-confirm their target; each page's own Release Date agrees |
| C frozen-series agreement | 6 | values, midpoints, chronology, splice, ordered level sequence, the two recorded date deltas |
| D announcement authority | 4 | no announcement post-dates its effective date; both offsets occur; four intermeeting actions; all corroborated |
| E no nearest-meeting heuristic | 5 | live regression on 2008-01-22 and 2020-03-03; no nearest/closest/guess/infer helper |
| F no ALFRED availability | 2 | no realtime/vintage/catalog parameter or column |
| G the sealed same-day rule | 6 | loads into `engine.policy`; 3 cutoffs; verified ≤ 15:45 admits; unestablished retains; 11 times not invented; six pinned collisions |
| H no feature produced | 4 | no artifact, no leg/sign/gate function, engine not imported, canonical panel not read |

```
NEAREST_MEETING_HEURISTIC_USED = NO
ALFRED_REALTIME_START_USED     = NO
FIXED_PUBLICATION_LAG_USED     = NO
```

### 6.1 Three parse defects the guards caught

Recorded because each would have produced a *plausible, silently wrong*
schedule, and each was found by a guard rather than by inspection:

1. **Cross-month meetings are written with a slash** — `Jan/Feb 31-1`,
   `Oct/Nov 31-1`, `Jul/Aug 31-1`, `April/May 30-1` — on **both** page families.
   The first parse missed them and reported the scheduled 2023-02-01 decision as
   an intermeeting action. The per-year completeness guard caught it. For 2019
   the single-month pattern matched *inside* `April/May 30-1` and produced the
   right date by luck, which would have hidden the bug entirely.
2. **Prose matched as calendar entries.** `"minutes of January 29/30 meeting"`
   injected a spurious 2008-01-29 into the scheduled set. A spurious *scheduled*
   date can only ever **hide** an intermeeting action, so the keyword must follow
   the date immediately and is matched case-sensitively — the Fed capitalises
   headings and lowercases cross-references.
3. **The Fed's label sits between the date and the keyword** —
   `March 2 (unscheduled) Meeting`, `March 17-18 (cancelled) Meeting`. Reading
   the annotation directly is what classifies 2020-03-15 correctly and excludes
   the meeting that never happened.

The guard that caught (1) and (3) is the corroboration requirement: an
intermeeting classification must be *positively* supported by a Federal Reserve
label, so losing one is a HOLD rather than a shorter list. The four expected
intermeeting dates are also named in the freeze itself.

---

## §7 Outcome firewall

```
HISTORICAL_POLICY_SIGNAL_COMPUTED    = NO
HISTORICAL_GROWTH_SIGNAL_COMPUTED    = NO
HISTORICAL_INFLATION_SIGNAL_COMPUTED = NO
HISTORICAL_MMV_POSITIONS_COMPUTED    = NO
HISTORICAL_GATE05_RESULT_COMPUTED    = NO
RETURN_OUTCOME_ACCESSED              = NO
PNL_COMPUTED · SHARPE_COMPUTED · BOOTSTRAP_RUN = NO
```

The freeze imports neither the MMV engine nor the production book (check H3), so
it could not compute a candidate feature even by accident. The validator resolves
target availability at exactly the **three** reconciliation cutoffs §5 requires
and nowhere else — never across the 218 decision dates, and never differenced.

Regression suites re-run green: **S2 synthetic 151/151**, **S2 parser 32/32**.

Two exemptions were added to the S2 validator's firewall lists, named
individually so the exemption list is itself auditable: the schedule CSV is
frozen **input authority** rather than an MMV output, and the two policy tools
are authorized to read the frozen target series because §5 of the brief requires
them to cross-check it. Neither check was weakened and the engine is exempt from
nothing.

---

## §8 Artifacts

| sha256 | bytes | path |
|---|---:|---|
| `ae34bf1e192c4355fb71136a3e3017dfd07525ac8e48d7d3ea102130fa6a11da` | 13837 | `research/extensions/mmv/MMV_POLICY_ANNOUNCEMENT_SCHEDULE.csv` |
| `bc364873764c50bdd21f7eb031696e2d4ed97e66614cb0fb15d9f76e03c8f2bf` | 5766 | `data/mmv/MMV_POLICY_SCHEDULE_MANIFEST.json` |
| `81371c07c374684144e7a6d5b8b3878c36ad0839e0fdbde5d53e4df68d6a10a5` | 35517 | `research/extensions/mmv/mmv_policy_schedule_freeze.py` |
| `e9d671e5f0dec0f582271143dc58a4de06b9f39a596f9e3e667e4943370a831b` | 17808 | `research/extensions/mmv/mmv_policy_schedule_validate.py` |

Source authority, pinned in the manifest:

```
Federal Reserve open-market table
  https://www.federalreserve.gov/monetarypolicy/openmarket.htm
  sha256 bf79dcb489370b0f3cac2bc65b2bd12d616d3fcd1eb62ad24d2e2e1a0081c660

FOMC calendars  16 official pages (fomchistorical2006..2020 + fomccalendars.htm)
                166 scheduled meeting ends · 18 unscheduled meetings / calls

Press releases  42 statements, one per regime, each hashed in the schedule CSV
Raw pages       77 cached under data/mmv/policy/ (git-ignored, hashes pinned)
```

---

## §9 Non-authorizations

```
HIGH_DIFFICULTY_OWNER_DECISION_REQUIRED = NO
FABLE_OWNER_ADVICE_RECOMMENDED          = NO
RUN_AUTHORIZATION_CREATED               = NO
S3_AUTHORIZATION_CREATED                = NO
```

Still requiring explicit Owner authorization: the historical MMV signal,
positions and Gate 0.5 evaluation; the first-release concordance cell; any
return, Sharpe, bootstrap or interval; any RNG seed; any `git push`, PR or merge.

```
EVIDENCE_CEILING = supported
```
