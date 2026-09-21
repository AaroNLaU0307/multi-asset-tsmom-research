# CTA-EDGE-05 / F6 — S0 REPAIR / COMPLETION RECORD

```
RECORD_TYPE = S0_METADATA_REPAIR_RECORD
LINEAGE     = CTA-EDGE-05 (F6 MACRO_ANNOUNCEMENT_PREMIUM)
DATE        = 2026-09-20
RULE        = F6-AUDIT-RULE-1, UNCHANGED
              sha256 5063fe3b35deb09674cbb32078744822c2db403959317996c18f93aade32be11
              re-verified byte-identical before and after this pass
SCOPE       = metadata only. No F6 return outcome of any kind.
```

```
TASK_STATUS              = HOLD
EVENT_SCHEDULE_PIT_GATE  = HOLD
EVENT_COUNT_MISMATCH_RESOLVED = YES
```

---

## §1 The 482 / 483 discrepancy — traced, not patched

The controller was right, and the cause is **mine, in the report prose**, not in
the data or the code.

```
MISMATCH_CAUSE
  The report's design-matrix cross-tabs were TRANSCRIBED FROM THE
  PRE-EXCLUSION RUN. The single differing date is 2025-08-22, a FRIDAY, which
  was the notation vote excluded under frozen rule section 5. Every headline
  count in that same report was POST-exclusion (482). The machine artifact was
  never wrong.
```

Demonstrated rather than asserted:

```
2025-08-22 weekday                         Friday
2025-08-22 in the manifest event set       False
manifest unique sessions                   482
manifest design_matrix.event_days          482
report weekday cells (pre-exclusion)        205 + 164 + 56 + 51 + 7 = 483
regenerated weekday cells (post-exclusion)  204 + 164 + 56 + 51 + 7 = 482
```

The Friday cell moving 205 → 204 is the whole discrepancy. No count was
edited: the cross-tabs were regenerated from the corrected event set.

**A second consequence of the same transcription error, which the controller
did not flag and which I am correcting here:** the LOYO remaining-event counts
printed in the prior report (451..467) were also pre-exclusion. The corrected
values are **450..467**.

### 1.1 Recomputed, metadata only

```
CORRECTED_PRIMARY_EVENT_COUNT      482
CORRECTED_FOMC_EVENT_COUNT         122
CORRECTED_CPI_EVENT_COUNT          185
CORRECTED_NFP_EVENT_COUNT          185
CORRECTED_MULTI_EVENT_DAY_COUNT     10      (all CPI+FOMC)

family labels 122 + 185 + 185 = 492 over 482 sessions; 492 - 482 = 10 = the
multi-event days. One unit, one trade, one observation each.

DESIGN_MATRIX_EVENT_ROWS        482
EVENT_MANIFEST_UNIQUE_SESSIONS  482
COUNTS_MATCH                    YES

EVENT x weekday   Fri 204 · Wed 164 · Thu 56 · Tue 51 · Mon 7      = 482
EVENT x TOM       TOM=0: 400 · TOM=1: 82                            = 482
EVENT x AUCTION   AUC=0: 409 · AUC=1: 73                            = 482

design matrix shape (3883, 9)   rank 9   FULL RANK
rank(controls) = 8 ; rank(controls + EVENT) = 9
EVENT_PERFECTLY_PREDICTED_BY_CONTROLS = NO
smallest singular values 20.064, 16.912, 12.060, 9.542

events per year  2011:32 2012:32 2013:31 2014:30 2015:32 2016:31 2017:29
                 2018:32 2019:31 2020:30 2021:32 2022:32 2023:32 2024:31
                 2025:30 2026:15
LOYO remaining   450 451 451 452 450 451 453 450 451 452 450 450 450 451
                 452 467
```

---

## §2 Generalized FOMC statement filter

```
FED_FOMC_FILTER_GENERALIZED = YES
research/extensions/f6/f6_fomc_filter.py
```

The prior pass excluded 2025-08-22 by a hard-coded date found through a
per-year count anomaly. That is replaced by a **source-based rule**, and the
MMV file was **not modified**.

### 2.1 What the Fed actually writes

```
August 22 (notation vote) Statement on Longer-Run Goals and Monetary Policy
Strategy
```

The MMV parser's current-calendar keyword is `Statement`. The text after the
annotation therefore *starts with* the keyword, the annotation contains neither
`cancel` nor `unscheduled`, and the entry is admitted as a scheduled meeting.
That is the whole defect, now explained from source rather than inferred.

### 2.2 The rule

```
REJECT if the Fed's own parenthesised annotation contains "cancel"
REJECT if it contains "notation"                     <- the new discriminator
REJECT if the entry is followed by "Conference Call"
REJECT (current calendar) unless the statement is in POST-MEETING LINK FORM
       "Statement:"  — a framework document reads "Statement on ..."
CLASSIFY UNSCHEDULED if the annotation contains "unscheduled"
```

Two independent discriminators, both source-derived. **No count heuristic
anywhere**, which is what makes it survive the case the controller specified.

### 2.3 Self-test: a notation vote AND a cancelled meeting in the same year

```
fixture year contains both
  scheduled    7  (Jan 28, Apr 29, Jun 10, Jul 29, Sep 16, Nov 5, Dec 16)
  unscheduled  1  (Mar 15)
  rejected        Mar 18 annotation:cancel ; Aug 22 annotation:notation
  SELFTEST PASS
```

A per-year count test would have seen 8 and reported nothing.

### 2.4 Re-enumeration, and a defect in my own first attempt

Re-running against the live Fed pages produced **46–50 "scheduled" dates per
year from 2019**. My current-calendar loop re-parsed the whole multi-year page
once per year, assigning every date token to every year. Fixed by adopting
MMV's `YEAR_BLOCK_RE` per-year segmentation, and a **parse-loss alarm** was
added — an alarm, never a classifier, mirroring MMV's own guard.

```
scheduled per year  2006..2019 = 8 each · 2020 = 7 (cancellation) ·
                    2021..2025 = 8 each · 2026 = 6 (calendar published so far)
total 165 ; IN WINDOW 122
rejected by Fed annotation
   2020-03-18 cancel · 2020-03-19 notation · 2020-03-23 notation ·
   2020-03-31 notation · 2020-08-27 notation · 2025-08-22 notation
```

The generalized rule reproduces the hand-patched 122 exactly, and additionally
catches four 2020 notation votes the hand patch never named.

---

## §3 The two "unscheduled" sets — they were never the same thing

My prior report said TA's four extras "are precisely unscheduled actions".
**That claim was imprecise and is withdrawn.**

```
FED_PARSER_UNSCHEDULED_SET  2011-08-01, 2011-11-28, 2020-03-02, 2020-03-15
TA_EXTRA_SET                2019-10-11, 2020-03-03, 2020-03-15, 2020-03-23
INTERSECTION                2020-03-15   (one date only)
```

```
WHY_DIFFERENT
  They are answers to different questions over different universes, and they
  are keyed to different calendars.

  1. UNIVERSE. The Fed set is built from the Fed's MEETING CALENDAR: entries
     the Fed labels "(unscheduled)", plus Conference Call entries. The TA set
     is the residue of TA_MACRO_CALENDAR's FOMC series, which is a list of
     STATEMENT RELEASES (detail = "FOMC statement") — a different object.

  2. KEY DATE. The Fed set is keyed to the MEETING / CALL date; the TA set to
     the STATEMENT RELEASE date. 2020-03-02 is the conference-call date and
     2020-03-03 is the release of that statement. They are the same episode
     one day apart, which is why they do not intersect.

  3. MEMBERSHIP. 2011-08-01 and 2011-11-28 are CONFERENCE CALLS that produced
     no separate statement release, so TA has no row for them at all.
     2019-10-11 is a statement release with NO meeting entry anywhere in the
     Fed calendar parse — not scheduled, not unscheduled, not rejected.
     2020-03-23 is a NOTATION VOTE, rejected by annotation in section 2.

  4. Only 2020-03-15 is simultaneously a Fed-labelled unscheduled action AND a
     statement release date, which is exactly why it is the sole intersection.
```

**The accurate claim, which replaces the withdrawn one:** every member of
`TA_EXTRA_SET` is a **non-scheduled FOMC statement release**, and none is a
scheduled post-meeting policy statement. After the generalized filter, the
count relationship is:

```
generalized-scheduled dates absent from TA : 0
TA FOMC rows in window                     : 126 = 122 scheduled + 4 extras
```

---

## §4 CPI / NFP schedule knowability

```
CPI_SCHEDULE_PIT = HOLD
NFP_SCHEDULE_PIT = HOLD
```

Authoritative BLS document retrieved: **"Revised news release dates following
the 2025 and 2026 lapses in appropriations"**
(`bls.gov/bls/2025-lapse-revised-release-dates.htm`, last modified
**2026-02-12**). It resolves the substance of every late-2025 / early-2026
exception:

| release | original | revised | classification |
|---|---|---|---|
| Employment Situation, Oct 2025 data | — | **CANCELLED ENTIRELY** | `KNOWN_BEFORE_ENTRY` |
| CPI, Oct 2025 data | — | **CANCELLED ENTIRELY** | `KNOWN_BEFORE_ENTRY` |
| Employment Situation, Nov 2025 data | Fri 2025-12-05 | Tue **2025-12-16** 08:30 ET | `UNRESOLVED` |
| CPI, Nov 2025 data | Wed 2025-12-10 | Thu **2025-12-18** 08:30 ET | `UNRESOLVED` |
| Employment Situation, Jan 2026 data | Fri 2026-02-06 | Wed **2026-02-11** 08:30 ET | `UNRESOLVED` |
| CPI, Jan 2026 data | Wed 2026-02-11 | Fri **2026-02-13** 08:30 ET | `UNRESOLVED` |
| CPI, Sep 2025 data | Fri 2025-10-24 08:30 ET (shutdown-delayed) | — | `UNRESOLVED` |
| Employment Situation, Sep 2025 data | released **2025-11-20** | — | `UNRESOLVED` |
| Employment Situation, Sep 2013 data (2013 shutdown) | 2013-10-04 | **2013-10-22** | `UNRESOLVED` |

The appropriations lapse ran **2025-10-01 to 2025-11-12**.

**Why CANCELLED is resolvable and RESCHEDULED is not.** A cancelled release
produces no event, so there is nothing whose knowability could be wrong — the
classification is safe on its face. A rescheduled release produces an event on
a new date, and the frozen rule asks whether that change was public **before
close(t−1)**. The BLS revised-dates page carries only a **page-level
last-modified stamp (2026-02-12)**, not a per-item announcement date. One of
those items (the 2026-02-11 Employment Situation) has an event date *earlier
than the page's own last-modified stamp*, so the page cannot establish
pre-entry knowledge even in principle.

```
PER-ITEM ANNOUNCEMENT DATES ARE NOT ESTABLISHED BY THE DOCUMENTS RETRIEVED.
They are almost certainly early enough. "Almost certainly" is not a source.
```

The 2013 case is not covered by this notice at all and its BLS notice was not
retrieved, so it stays `UNRESOLVED`.

**No ex-post correction was applied and no original planned date was
substituted.** The event calendar retains actual release dates, exactly as the
frozen rule requires, and the unresolved items are the named HOLD reason.

---

## §5 Release times

```
CPI_TIME_PIT  = HOLD
NFP_TIME_PIT  = HOLD
FOMC_TIME_PIT = HOLD
```

**CPI and NFP.** `08:30 AM ET` is stated explicitly in the BLS revised-dates
notice for each rescheduled release, and the CPI schedule page lists 08:30 for
every date through 2026. That establishes the time **for the releases those
documents cover**. It does **not** establish the convention across the whole
2011–2026 window, and the frozen rule forbids blanket-backfilling a modern
time into earlier history. Per-year BLS schedule documents were not retrieved.

**FOMC — a documented timing-regime change inside the window.**

```
Feb 1995 .. Jan 2013   statement released 2:15 p.m. ET
from March 2013        statement released 2:00 p.m. ET
                       announced by Fed press release dated 2013-03-13
                       ("Federal Reserve announces time changes for FOMC
                        statements and news conferences")
```

The F6 window opens 2011-01, so roughly the first two years sit in the
**2:15 p.m.** regime and the remainder in the **2:00 p.m.** regime. Blanket
2:00 p.m. would be wrong for about 17 scheduled statements. The exact first
meeting under the new regime was not confirmed per-meeting, which is why this
is HOLD rather than PASS.

---

## §6 DGS3MO — source facts versus owner choice

```
DGS3MO_DAY_BASIS = NOT ESTABLISHED BY SOURCE
DGS3MO_PUBLICATION_LAG = H.15 posts 4:15 p.m. ET, AFTER the 16:00 NYSE close
DGS3MO_CONVERSION_OWNER_DECISION_REQUIRED = YES
```

### 6.1 SOURCE FACTS

```
FRED title      "Market Yield on U.S. Treasury Securities at 3-Month Constant
                Maturity, Quoted on an Investment Basis"; percent, daily
publisher       Board of Governors, via the H.15 release
H.15            posted daily Mon-Fri at 4:15 p.m. ET; NOT posted on holidays
                or when the Board is closed; states NO day-count for constant
                maturity yields and defers to Treasury methodology
Treasury yield  "The inputs for the bills are bid discount rates corresponding
curve method    to their bond equivalent yields." It specifies NO day-count
                convention, NO compounding convention, and NO simple daily
                accrual divisor anywhere.
missing obs     167 of 4030 in-window rows
```

The source chain **terminates without establishing a conversion**. FRED defers
to H.15; H.15 defers to Treasury; Treasury is silent.

### 6.2 The one thing that IS mechanically determined

Because H.15 posts at 16:15 and the NYSE closes at 16:00:

```
DGS3MO(d) is first knowable only AFTER the close on d.
=> the latest observation knowable at close(t-1) is DGS3MO(t-2), or, across
   holidays, the last available observation dated on or before t-2.
```

That is the **exact maximum mechanically valid carry-forward**, and it is a
source-fact consequence, not a preference. Forward-filling from that point uses
only past observations and introduces no look-ahead.

### 6.3 OWNER CHOICE

Turning an annualized coupon-equivalent quote into a **one-interval cash
return** requires a compounding convention and a day-count basis. The source
supplies neither.

```
NEITHER /365 NOR /360 IS INVENTED HERE. Choosing between them — or choosing a
compounded form — is an Owner decision, and it is a DESIGN CHOICE, not a
source fact.
```

---

## §7 Independent adjudication provenance

```
F6_INDEPENDENT_ADJUDICATION_PROVENANCE_GAP = YES
```

Re-checked mechanically this pass: `git ls-files` across the repository and a
listing of the workspace root both return **ABSENT**. The exact original bytes
were not supplied in this session.

**Nothing was reconstructed from memory or from a summary, and no hash was
fabricated.** This remains a pre-S1 documentation blocker and is not a reason
to access returns.

---

## §8 2026 partial year — facts refreshed, decision not taken

```
YEAR_BLOCK_COUNT = 16
PARTIAL_2026_OWNER_DECISION_REQUIRED = YES
```

```
full years 2011..2025   29 to 32 events, mean 31.1
2026                    15 events
calendar span of 2026   2026-01-02 .. 2026-06-12 (panel boundary), ~5.4 months
LOYO deletion sizes     dropping any full year leaves 450-453 events;
                        dropping 2026 leaves 467
```

So the 2026 fold deletes roughly **half** what every other fold deletes. Facts
only. **No replacement bootstrap method was tried and no alternative blocking
was attempted.**

---

## §9 Firewall and accounting

```
RETURN_OUTCOME_ACCESSED   = NO      BETA_EVENT_COMPUTED        = NO
F6_PRIMARY_RETURN_COMPUTED= NO      F6_PRIMARY_TRIAL_CONSUMED  = NO
TLT_RETURN_ACCESSED       = NO      F6B_RETURN_ACCESSED        = NO
mean payoff · confidence interval · Sharpe · LOYO performance ·
NQ outcome data · surprise data · model alternatives = none
```

No return family executed, no performance-exposure row created, no ledger
modified. Metadata reads only, classified `DESIGN_INFORMING_MEASUREMENT` on
non-target inputs and never joined to a price. The frozen rule was not modified.

---

## §10 Still owed before S1

```
1. the F6 independent adjudication artifact (section 7)
2. per-item BLS announcement dates for each rescheduled release, and the 2013
   shutdown notice (section 4)
3. per-year BLS schedule documents to establish the 08:30 convention across the
   whole window, and per-meeting confirmation of the 2013 FOMC timing boundary
   (section 5)
4. an Owner decision on the DGS3MO conversion (section 6.3)
5. an Owner decision on the partial 2026 block (section 8)
```
