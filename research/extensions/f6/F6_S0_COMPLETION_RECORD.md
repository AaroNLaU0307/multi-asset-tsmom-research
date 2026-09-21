# CTA-EDGE-05 / F6 — S0 COMPLETION RECORD

```
RECORD_TYPE = S0_COMPLETION_RECORD
LINEAGE     = CTA-EDGE-05 (F6 MACRO_ANNOUNCEMENT_PREMIUM)
DATE        = 2026-09-21
RULE        = F6-AUDIT-RULE-1, UNCHANGED
              sha256 5063fe3b35deb09674cbb32078744822c2db403959317996c18f93aade32be11
SCOPE       = schedule PIT completion, final primary manifest, cash mapping.
              METADATA ONLY. No F6 outcome.
```

```
TASK_STATUS             = HOLD
EVENT_SCHEDULE_PIT_GATE = HOLD
```

HOLD for one remaining reason, now narrow and precisely named: **seven
rescheduled BLS releases inside the primary window have no published
announcement date**, so the frozen rule's "knowable at close(t−1)" test cannot
be answered for them from source. Everything else in S0 is complete.

---

## §1 BLS schedule PIT — Part D

### 1.1 What the authorities gave

Two authoritative BLS documents were retrieved, and between them they supply
the **original scheduled dates** that no prior pass had:

```
"Updated Schedule of BLS News Releases"  (2013 lapse; last modified 2013-12-06)
"Revised news release dates following the 2025 and 2026 lapses in
 appropriations"                          (last modified 2026-02-12)
"September 2025 CPI Release Rescheduled"  (last modified 2025-10-10)  <- DATED
```

### 1.2 Every changed release in the primary window

| release | original | actual | classification |
|---|---|---|---|
| Employment Situation, Sep 2013 | Fri **2013-10-04** 08:30 | Tue **2013-10-22** 08:30 | orig `CANCELLED_BEFORE_ENTRY` · new `UNRESOLVED` |
| CPI, Sep 2013 | Wed **2013-10-16** 08:30 | Wed **2013-10-30** 08:30 | orig `CANCELLED_BEFORE_ENTRY` · new `UNRESOLVED` |
| Employment Situation, Oct 2013 | Fri **2013-11-01** 08:30 | Fri **2013-11-08** 08:30 | orig `CANCELLED_BEFORE_ENTRY` · new `UNRESOLVED` |
| CPI, Oct 2013 | Fri **2013-11-15** 08:30 | Wed **2013-11-20** 08:30 | orig `CANCELLED_BEFORE_ENTRY` · new `UNRESOLVED` |
| CPI, Sep 2025 | shutdown-suspended | Fri **2025-10-24** 08:30 | **`CHANGED_BEFORE_ENTRY`** |
| Employment Situation, Sep 2025 | Fri 2025-10-03 | Thu **2025-11-20** 08:30 | orig `CANCELLED_BEFORE_ENTRY` · new `UNRESOLVED` |
| Employment Situation, Oct 2025 | — | **CANCELLED ENTIRELY** | `CANCELLED_BEFORE_ENTRY` |
| CPI, Oct 2025 | — | **CANCELLED ENTIRELY** | `CANCELLED_BEFORE_ENTRY` |
| Employment Situation, Nov 2025 | Fri **2025-12-05** | Tue **2025-12-16** 08:30 | `UNRESOLVED` |
| CPI, Nov 2025 | Wed **2025-12-10** | Thu **2025-12-18** 08:30 | `UNRESOLVED` |
| Employment Situation, Jan 2026 | Fri 2026-02-06 | Wed 2026-02-11 | **outside the primary window** |
| CPI, Jan 2026 | Wed 2026-02-11 | Fri 2026-02-13 | **outside the primary window** |

Lapse periods, from the sources: **2013-10-01 to 2013-10-16** and
**2025-10-01 to 2025-11-12**.

### 1.3 The one release that IS resolved, and why

```
CPI, September 2025 data -> Friday 2025-10-24, 08:30 ET
notice "September 2025 CPI Release Rescheduled", last modified 2025-10-10
2025-10-10 precedes close(2025-10-23) by 13 days
=> CHANGED_BEFORE_ENTRY
```

That notice also states: *"No other releases will be rescheduled or produced
until the resumption of regular government services"* — which is what makes the
concurrent cancellations knowable rather than merely true.

### 1.4 Why the other six stay UNRESOLVED

A **cancellation** is classifiable on its face: the lapse was public, no release
occurred, and no event exists, so nothing about entry-time knowability can be
wrong. A **reschedule** creates an event on a new date, and the frozen rule asks
whether that date was public **before close(t−1)**.

```
The 2013 page's last-modified is 2013-12-06 — WEEKS AFTER every date it
describes. The 2025/2026 page's is 2026-02-12. Neither carries a PER-ITEM
announcement date, and the Employment Situation schedule page carries no
last-modified date and no reschedule footnote at all.
```

Each of the six was almost certainly announced in time. **"Almost certainly" is
not a source**, and the frozen rule's tier hierarchy has no tier 3, so they are
recorded as `UNRESOLVED` rather than waved through.

### 1.5 A correction to my own earlier method

The prior pass surfaced these exceptions with a *heuristic* cross-check —
"NFP not on a Friday" — and reported it as having found the 2013 case. **That
heuristic under-detected.** The BLS authority shows **four** changed 2013
releases; the heuristic found **one** (2013-10-22), because 2013-11-08 is itself
a Friday and CPI has no weekday regularity to violate.

```
THE HEURISTIC FOUND 1 OF 4. That is exactly why the frozen rule admits
heuristics only to RAISE EXCEPTIONS and never as authority.
```

All four 2013 revised dates are present in the manifest and none of the four
originals is — consistent with no release having occurred on the original dates.
**No ex-post correction was applied** and no original planned date was
substituted.

```
CPI_SCHEDULE_PIT = HOLD      NFP_SCHEDULE_PIT = HOLD
```

---

## §2 FOMC schedule PIT — Part E

```
FOMC_SCHEDULE_PIT = HOLD
```

Re-enumerated with the repaired **source-based** filter
(`f6_fomc_filter.py`), which classifies from the Fed's own annotations and uses
no per-year count heuristic:

```
scheduled post-meeting policy statements ONLY   YES
notation votes EXCLUDED                          YES — by the Fed's own
                                                 "(notation vote)" annotation
emergency / intermeeting actions EXCLUDED        YES — "(unscheduled)"
conference calls EXCLUDED                        YES
cancelled meetings EXCLUDED                      YES — "(cancelled)"
minutes / speeches / other statements EXCLUDED   YES — a framework document
                                                 reads "Statement on ...",
                                                 a post-meeting statement
                                                 reads "Statement:"
```

```
per-year scheduled counts 2006..2025 = 8 every year EXCEPT 2020 = 7
  (the March 17-18 2020 meeting was CANCELLED and the Fed labels it so)
IN PRIMARY WINDOW 2011..2025 = 119 scheduled statement releases
EXCLUDED as unscheduled, in window: 2011-08-01, 2011-11-28,
                                    2020-03-02, 2020-03-15
REJECTED by Fed annotation: 2020-03-18 cancel · 2020-03-19, 2020-03-23,
                            2020-03-31, 2020-08-27, 2025-08-22 notation
```

**Applicable historical statement-release time — a documented regime change
inside the window:**

```
Feb 1995 .. Jan 2013   2:15 p.m. ET
from March 2013        2:00 p.m. ET
                       Fed press release dated 2013-03-13, "Federal Reserve
                       announces time changes for FOMC statements and news
                       conferences"
```

Roughly the first two years of the primary window sit in the **2:15 p.m.**
regime. Blanket-applying 2:00 p.m. would be wrong for those. The exact first
meeting under the new regime was not confirmed per-meeting, which — with the
release times for CPI/NFP not established across the whole window — is why
`FOMC_TIME_PIT` and the family remain HOLD rather than PASS.

**Scheduled status knowable by entry:** yes by construction. The Fed publishes
its meeting calendar years ahead, and anything the Fed labels unscheduled is
excluded precisely because it was *not* knowable at close(t−1).

---

## §3 Final primary manifest — Part F

```
FINAL_PRIMARY_YEARS      2011 .. 2025
FINAL_PRIMARY_EVENT_COUNT              467
  FOMC_EVENT_COUNT                     119
  CPI_EVENT_COUNT                      179
  NFP_EVENT_COUNT                      179
  MULTI_EVENT_DAY_COUNT                 10
```

```
119 + 179 + 179 = 477 labels over 467 sessions; 477 - 467 = 10 = the
multi-event days. One unit, one trade, one observation each.
```

Multi-event sessions: 2013-10-30, 2014-09-17, 2014-12-17, 2016-03-16,
2017-03-15, 2017-06-14, 2017-12-13, 2019-12-11, 2020-06-10, 2024-06-12.

**2026 is carried in an explicitly NON-OUTCOME segment** — 15 sessions of
schedule metadata retained for discoverability. It is **not** in the primary
design matrix and no 2026 F6 outcome quantity may be computed.

### 3.1 Control matrix, 2011–2025

```
rows 3771      shape (3771, 9)      rank 9      FULL RANK
rank(controls) = 8 ; rank(controls + EVENT) = 9
EVENT_PERFECTLY_PREDICTED_BY_CONTROLS = NO
columns with no variation: NONE

EVENT x weekday   Fri 198 · Wed 158 · Thu 56 · Tue 49 · Mon 6     = 467
EVENT x TOM       TOM=1: 81 · TOM=0: 386                           = 467
EVENT x AUCTION   AUC=1: 68 · AUC=0: 399                           = 467
```

Every cross-tab sums to **467**, the manifest count. Monday remains thin at 6
event days but is non-empty, so it does not break rank; that is reported as
sparsity, not diagnosed.

`TOM` reuses the sealed `src/seasonality.py::is_tom` (last=1, first=3);
`AUCTION` reuses the pinned TA 10y/30y definition unaltered.

### 3.2 Year blocks

```
YEAR_BLOCK_COUNT = 15, all COMPLETE
events/year  2011:32 2012:32 2013:31 2014:30 2015:32 2016:31 2017:29
             2018:32 2019:31 2020:30 2021:32 2022:32 2023:32 2024:31 2025:30
LOYO remaining  435 .. 438 events
```

The partial-block asymmetry that forced an Owner decision at the prior pass is
**gone**: every block is a full year and every LOYO fold now deletes a
comparable amount.

---

## §4 DGS3MO mapping — Part G

```
DGS3MO_MAPPING_PASS      = YES
UNEXPLAINED_DGS3MO_GAPS  = NONE
```

Only the **Owner-chosen** mapping was implemented, and **no `rf_hold` value was
computed**:

```
rule   latest official DGS3MO observation dated <= prev(d),
       carried ONLY across source-explained non-publication
gap    a skipped date is EXPLAINED iff it is a weekend, or a date the official
       file itself carries as a missing observation. A business day with NO ROW
       in the official file would be an UNEXPLAINED gap -> METADATA_EXCEPTION.
```

```
primary sessions requiring an rf        3771
carry distance 0 calendar days          3743
carry distance 1 calendar day              8
carry distance 3 calendar days            20
MAXIMUM CARRY REQUIRED                     3 days
UNEXPLAINED GAPS                           0
```

**The rejected seven-day threshold was not merely unsourced — it was
unnecessary.** The data never needs more than three days, and every one of those
carries is a weekend-or-holiday pattern explained by the source's own
publication calendar. No arbitrary threshold appears anywhere in the mapping.

The `/365` divisor in `rf_hold = (DGS3MO/100) × calendar holding days / 365`
is recorded as **OWNER-CHOSEN** and is not attributed to Treasury, H.15 or FRED
— the source chain terminates without specifying a day count.

---

## §5 Firewall and accounting

```
F6_RETURN_OUTCOME_ACCESSED   = NO     BETA_EVENT_COMPUTED       = NO
F6_PRIMARY_RETURN_COMPUTED   = NO     F6_PRIMARY_TRIAL_CONSUMED = NO
2026_F6_OUTCOME_ACCESSED     = NO     TLT_RETURN_ACCESSED       = NO
F6B_RETURN_ACCESSED          = NO
cash-excess returns · event P&L · confidence intervals · Sharpe ·
LOYO performance · NQ outcomes · surprise data          = none computed
rf_hold VALUES                                          = none computed
```

The price panel was opened for its **date index only**. No return family was
executed, no performance-exposure row created, no ledger modified. Schedule and
rate metadata reads are `DESIGN_INFORMING_MEASUREMENT` on non-target inputs and
were never joined to a price.

---

## §6 What remains before S1

```
1. the F6 independent adjudication artifact — original bytes NOT PERSISTED
   (F6_INDEPENDENT_ADJUDICATION_CONTROLLER_TRANSCRIPT.md)
2. per-item BLS announcement dates for the SIX unresolved reschedules (§1.4)
3. per-year BLS schedule documents establishing 08:30 across the whole window,
   and per-meeting confirmation of the 2013 FOMC 2:15 -> 2:00 boundary (§2)
4. the S1 seal itself
```

None of these authorizes return access.

---

## ADDITIVE NOTE — 2026-09-21, superseded event count

The `PRIMARY_EVENT_COUNT = 467` recorded above was **provisional**. The final
schedule-PIT gate excluded 6 unresolved reschedules (5 whole sessions), giving
`FINAL_PRIMARY_EVENT_COUNT = 462`.

```
this record is RETAINED UNCHANGED as the correct PRE-GATE state.
superseded by  F6_SCHEDULE_PIT_FINAL_GATE.md
final manifest F6_FINAL_EVENT_MANIFEST.json
               sha256 49ff27bfc20eb98265c440bac7368e92022b356d77647dce9151f012e40ed382
```
