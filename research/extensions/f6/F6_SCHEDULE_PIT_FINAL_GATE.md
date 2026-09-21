# CTA-EDGE-05 / F6 — FINAL SCHEDULE-PIT EVENT ELIGIBILITY GATE

```
RECORD_TYPE   = S0 FACTUAL GATE / FINAL EVENT ELIGIBILITY
LINEAGE       = CTA-EDGE-05 (F6 MACRO_ANNOUNCEMENT_PREMIUM)
DATE          = 2026-09-21
SCOPE         = METADATA ONLY. NO F6 OUTCOME QUANTITY WAS COMPUTED.
STATUS        = FINAL for schedule eligibility. NOT an S1 seal.
```

This gate does **not** redesign F6. The instrument, the payoff object, the cash
convention, the inference window and the promotion logic are already decided in
[`../../../ops/OWNER_DECISION_RECORD_CTA_EDGE_05_F6.md`](../../../ops/OWNER_DECISION_RECORD_CTA_EDGE_05_F6.md)
and are untouched here. The DGS3MO mapping is **CLOSED / PASS** and was not
reopened.

The single job of this document is to turn the **provisional 467** into a
**final** event count by ruling, release by release, on whether the schedule was
knowable *before* the entry decision.

---

## §1 The rule

```
SCHEDULE_PIT_FAIL_CLOSED_RULE

A release whose date CHANGED is admissible ONLY IF the change was announced by
an authoritative contemporaneous source at a timestamp that is strictly before
the entry decision at close(t-1).

If the contemporaneous announcement timing cannot be established, the release is
      PIT_UNRESOLVED_EVENT
and is EXCLUDED FROM THE PRIMARY F6 EVENT SAMPLE, PRE-OUTCOME.
```

Four inferences are **forbidden** as evidence of announcement timing, and none
was used:

```
1. a page's CURRENT last-modified date                      FORBIDDEN
2. the ACTUAL release date                                  FORBIDDEN
3. a weekday heuristic ("NFP is the first Friday")          FORBIDDEN
4. media recollection, or the contents of the release       FORBIDDEN
```

**The actual release date is never substituted for the announcement date merely
because it is known ex post.** Where no announcement date was located, none was
invented; the release was excluded instead.

### 1.1 Why this is not outcome filtering

```
THIS EXCLUSION IS A SCHEDULE-AUTHORITY EXCLUSION.

It is NOT outcome filtering.
It is NOT a mechanism failure.
It is NOT a return-based exclusion.
```

Every ruling below was made **before any F6 return quantity existed**. No SPY
return, no event payoff, no cash-excess return, no `beta_EVENT`, no interval, no
Sharpe and no LOYO performance has been computed at the time of writing, and the
price panel was opened for its **date index** only.

### 1.2 The excluded object is a RELEASE, not necessarily a SESSION

A trading session can carry more than one event family. Excluding an unresolved
release removes **that family's label**. The session itself survives if it
carries another event whose schedule *was* independently knowable. This matters
exactly once below.

---

## §2 The reschedule ledger

```
BLS_RESCHEDULE_CASES_TOTAL = 8
```

Two clusters exist in 2011–2025: the **October 2013** federal shutdown and the
**October–December 2025** shutdown. Both were enumerated from the agencies' own
notices, not from count anomalies.

| # | family | ref | original | actual | classification |
|---|---|---|---|---|---|
| 1 | NFP | 2013-09 | 2013-10-04 | 2013-10-22 | **PIT_UNRESOLVED** |
| 2 | CPI | 2013-09 | 2013-10-16 | 2013-10-30 | **PIT_UNRESOLVED** |
| 3 | NFP | 2013-10 | 2013-11-01 | 2013-11-08 | **CHANGED_BEFORE_ENTRY** |
| 4 | CPI | 2013-10 | 2013-11-15 | 2013-11-20 | **PIT_UNRESOLVED** |
| 5 | NFP | 2025-09 | 2025-10-03 | 2025-11-20 | **PIT_UNRESOLVED** |
| 6 | CPI | 2025-09 | 2025-10-15 | 2025-10-24 | **CHANGED_BEFORE_ENTRY** |
| 7 | NFP | 2025-11 | 2025-12-05 | 2025-12-16 | **PIT_UNRESOLVED** |
| 8 | CPI | 2025-11 | 2025-12-10 | 2025-12-18 | **PIT_UNRESOLVED** |

```
CHANGED_BEFORE_ENTRY   = 2   (admissible at the ACTUAL date)
CHANGED_AFTER_ENTRY    = 0
PIT_UNRESOLVED         = 6   (EXCLUDED pre-outcome)
```

`CHANGED_AFTER_ENTRY = 0` is **not** a claim that no such case exists. It is the
honest statement that no case was *established* as announced after entry — the
six unresolved cases were excluded precisely because they could not be placed on
either side of the entry decision.

### 2.1 The two admissible cases, with their contemporaneous authority

**Case 3 — NFP for October 2013, released 2013-11-08.** A BLS blog entry posted
**2013-10-31** states verbatim:

> "The Employment Situation for October will be published Friday, November 8,
> 2013, at 8:30 A.M. Eastern Time."

That is a dated, contemporaneous, source-published statement **8 days before**
`close(2013-11-07)`. Admissible.

**Case 6 — CPI for September 2025, released 2025-10-24.** The BLS notice
*"September 2025 CPI Release Rescheduled"*, last modified **2025-10-10**, states
BLS will publish on Friday **2025-10-24 at 8:30 A.M. ET**. Here the page stamp
*precedes* the event by 13 days, so the stamp is usable as a **lower bound on
knowability** rather than as a forbidden ex-post inference. Admissible.

### 2.2 The six exclusions, and why the evidence was insufficient

**Cases 1 and 2 — NFP 2013-10-22 and CPI 2013-10-30.** The BLS 2013 blog archive
carries entries on **2013-10-25** and **2013-10-31** and **nothing between
2013-10-17 and 2013-10-25**. The 2013-10-25 entry describes the 2013-10-22
release **retrospectively**. The updated-schedule page's only stamp is
**2013-12-06**, after both events. Nothing establishes pre-entry knowability.

**Case 4 — CPI 2013-11-20.** The 2013-10-31 blog says BLS "updated our full
schedule … for the remainder of 2013" but does **not name this date**. Inferring
that page's contents from a stamp of 2013-12-06 is exactly the inference §1
forbids.

**Cases 5, 7 and 8 — NFP 2025-11-20, NFP 2025-12-16, CPI 2025-12-18.** No dated
BLS notice naming these dates in advance was located. The revised-dates page
carries only a page-level **2026-02-12** stamp — after all three — and the
Employment Situation schedule page carries none.

### 2.3 Cancellations — no event exists

```
NFP reference month 2025-10   CANCELLED ENTIRELY (household data never collected)
CPI reference month 2025-10   CANCELLED ENTIRELY
```

A cancelled release is **not** an exclusion. No event ever existed on any date,
so there is nothing to admit or remove, and the never-scheduled dates
`2013-10-04`, `2013-10-16`, `2013-11-01`, `2013-11-15` and `2025-10-03` were
likewise never in the manifest as events.

---

## §3 Release-time authority

The brief required the release **clock time** to rest on authority, not habit.

### 3.1 CPI and NFP — 08:30 ET, no regime change located

```
CPI_RELEASE_TIME = 08:30 ET      NFP_RELEASE_TIME = 08:30 ET
REGIME_CHANGES_LOCATED = NONE
```

Contemporaneous attestations at both ends of the window:

| year | family | source text |
|---|---|---|
| 2013 | CPI | news release **USDL-13-2076** header: "Transmission of material in this release is embargoed until **8:30 a.m. (EDT) Wednesday, October 30, 2013**" |
| 2013 | NFP | BLS blog 2013-10-31: "Friday, November 8, 2013, at **8:30 A.M. Eastern Time**" |
| 2025 | both | BLS reschedule notices state the revised releases at **8:30 AM ET** |

```
STATED HONESTLY: this is "NO REGIME CHANGE WAS LOCATED", anchored at both ends
of the window. It is NOT "verified release-by-release for every year".
```

### 3.2 FOMC — one located regime change, with an unverified pre-change time

```
FOMC_RELEASE_TIME_REGIME_CHANGE = LOCATED
```

| regime | time | status |
|---|---|---|
| through 2013-01-30 | 2:15 p.m. ET | **NOT VERIFIED** from a tier-1 schedule document in this session |
| from 2013-03-20 | **2:00 p.m. ET** | **VERIFIED** |

The Federal Reserve press release of **2013-03-13** states that Committee policy
statements for all regularly scheduled meetings will now be released at **2 p.m.
Eastern Time**. That release does **not** name the prior time and does **not**
name the first affected meeting; the first regularly scheduled meeting to
conclude after it is **2013-03-20**, which is therefore the boundary. The
post-change time is independently corroborated by the locally frozen statement
`data/mmv/fomc/fomc_statement_20180131.html`, which carries "For release at 2:00
p.m. EST".

The **pre-change clock time is an unverified carry-over**, not a source fact of
this session: the 2012 statement HTML carries no release-time line and the
corresponding PDFs return 404.

```
ELIGIBILITY IMPACT = NONE.
```

Both candidate times — 2:15 p.m. and 2:00 p.m. — fall **inside** the trading
session. A `close(t-1) -> close(t)` trade is unaffected either way, so the
unverified pre-2013 time cannot change a single eligibility ruling. It is
recorded as a residual factual gap, not as a blocker.

---

## §4 The final event sample — generated, not transcribed

Every number in this section was produced mechanically from the final manifest
and asserted in code. None was hand-transcribed.

```
PROVISIONAL_PRIMARY_EVENT_COUNT = 467
labels removed (PIT_UNRESOLVED)  =   6
sessions emptied entirely        =   5
sessions surviving on another family = 1

FINAL_PRIMARY_EVENT_COUNT       = 462
```

The one surviving session is **2013-10-30**, a CPI+FOMC day. The CPI label is
excluded as unresolved; the **FOMC statement of that date was independently
scheduled and knowable**, so the session remains in the sample as an FOMC event.
Five sessions — `2013-10-22`, `2013-11-20`, `2025-11-20`, `2025-12-16`,
`2025-12-18` — carried no other family and leave the sample entirely.

### 4.1 Composition

```
FOMC labels  119
CPI  labels  176
NFP  labels  176
             ---
labels       471
multi-event sessions            9
overlap adjustment              9
471 - 9 = 462                   == FINAL_PRIMARY_EVENT_COUNT
```

### 4.2 Design-matrix cross-tabs

| weekday | events |  | TOM | events |  | AUCTION | events |
|---|---|---|---|---|---|---|---|
| Monday | 6 | | 0 | 381 | | 0 | 394 |
| Tuesday | 47 | | 1 | 81 | | 1 | 68 |
| Wednesday | 157 | | **sum** | **462** | | **sum** | **462** |
| Thursday | 54 |
| Friday | 198 |
| **sum** | **462** |

### 4.3 The assertions that were enforced in code

```
ASSERT sum(event weekday cells)  == FINAL_PRIMARY_EVENT_COUNT     PASS
ASSERT sum(event TOM cells)      == FINAL_PRIMARY_EVENT_COUNT     PASS
ASSERT sum(event AUCTION cells)  == FINAL_PRIMARY_EVENT_COUNT     PASS
ASSERT family labels - overlap   == FINAL_PRIMARY_EVENT_COUNT     PASS
ASSERT EVENT column sum          == FINAL_PRIMARY_EVENT_COUNT     PASS
```

A failure raises and stops the build; it does not print a warning.

---

## §5 Final control matrix

```
rows                          3771     (2011-2025 sessions, first row dropped
                                        because HOLD is undefined at the edge)
shape                         (3771, 9)
rank                          9
FULL RANK                     YES
EVENT in span of controls     NO      <- EVENT is separately identified
required columns with no variation   NONE
```

The fixed model specified in the Owner record remains **rank sufficient after
the exclusions**. No second model was invented, and no column was dropped to
achieve rank.

---

## §6 LOYO year blocks

```
YEAR_BLOCKS = 15   (2011 .. 2025)
```

| year | EVENTS_REMOVED | EVENTS_REMAINING |
|---|---|---|
| 2011 | 32 | 430 |
| 2012 | 32 | 430 |
| 2013 | 29 | 433 |
| 2014 | 30 | 432 |
| 2015 | 32 | 430 |
| 2016 | 31 | 431 |
| 2017 | 29 | 433 |
| 2018 | 32 | 430 |
| 2019 | 31 | 431 |
| 2020 | 30 | 432 |
| 2021 | 32 | 430 |
| 2022 | 32 | 430 |
| 2023 | 32 | 430 |
| 2024 | 31 | 431 |
| 2025 | 27 | 435 |

```
LOYO_REMAINDER_RANGE = 430 .. 435
```

The brief's expectation of "approximately 435–438, subject to final event
exclusions" is met in shape but sits **5 lower**, which is exactly the arithmetic
of removing 5 sessions from every remainder. The values above are **generated**
from the final manifest, not transcribed.

`EVENTS_REMOVED` is stated per year as a count of held-out events;
**no LOYO performance quantity of any kind was computed.**

---

## §7 Firewall attestation

```
SPY returns read                      NO
event payoff computed                 NO
cash-excess return computed           NO
rf_hold VALUE computed                NO
beta_EVENT computed                   NO
confidence interval computed          NO
Sharpe computed                       NO
LOYO performance computed             NO
TLT inspected                         NO
F6.b inspected                        NO
2026 F6 performance inspected         NO
NQ outcomes inspected                 NO

F6_PRIMARY_TRIAL_CONSUMED = NO
```

---

## §8 What this gate does NOT do

```
It does not seal F6.
It does not write S1 preregistration.
It does not close the independent-adjudication provenance gap.
```

```
EXACT_ADJUDICATION_TRANSCRIPT_STILL_OWED = YES
```

No exact adjudication text was supplied in this execution context, so none was
written. The existing
[`F6_INDEPENDENT_ADJUDICATION_CONTROLLER_TRANSCRIPT.md`](F6_INDEPENDENT_ADJUDICATION_CONTROLLER_TRANSCRIPT.md)
remains a controller-supplied reconstruction carrying no original hash, and
`F6_INDEPENDENT_ADJUDICATION_PROVENANCE_GAP = YES` remains open as a pre-S1
documentation blocker.

Residual factual gaps carried forward, neither of which can change an
eligibility ruling:

```
1. the pre-2013 FOMC release clock time is an unverified carry-over (§3.2);
   eligibility impact NONE.
2. six reschedules are unresolved rather than proven-late; they are excluded,
   which is the conservative direction.
```

---

## §9 Artifacts

```
final manifest   F6_FINAL_EVENT_MANIFEST.json
                 sha256 49ff27bfc20eb98265c440bac7368e92022b356d77647dce9151f012e40ed382
supersedes       F6_PRIMARY_MANIFEST_2011_2025.json   (467 provisional; RETAINED,
                 NOT REWRITTEN — it remains the correct pre-gate record)
frozen rule      F6_METADATA_AUDIT_RULE.md
                 sha256 5063fe3b35deb09674cbb32078744822c2db403959317996c18f93aade32be11
owner record     ../../../ops/OWNER_DECISION_RECORD_CTA_EDGE_05_F6.md §11
```
