# CTA-EDGE-05 / F6 — EVENT SCHEDULE PIT + CALENDAR DESIGN FEASIBILITY

```
RECORD_TYPE = S0_SCHEDULE_PIT_FEASIBILITY_REPORT
LINEAGE     = CTA-EDGE-05 (F6 MACRO_ANNOUNCEMENT_PREMIUM)
DATE        = 2026-09-20
RULE        = F6-AUDIT-RULE-1, frozen BEFORE enumeration
              research/extensions/f6/F6_METADATA_AUDIT_RULE.md
              sha256 5063fe3b35deb09674cbb32078744822c2db403959317996c18f93aade32be11
              commit d72501c
SCOPE       = metadata and calendar design feasibility ONLY. No F6 outcome.
```

```
TASK_STATUS             = HOLD
EVENT_SCHEDULE_PIT_GATE = HOLD
```

> **CORRECTED IN PART — 2026-09-20. Appended; nothing below is edited.**
> Two errors in THIS document are corrected in
> [`F6_S0_REPAIR_RECORD.md`](F6_S0_REPAIR_RECORD.md), sha256 `feebb831d42a7f7a51012b43fd03104e62f7482d5ee329f99d4bc258d3330b96`:
>
> * **§6's cross-tabs and §7's LOYO counts were transcribed from the
>   PRE-exclusion run** and sum to 483, not 482. The differing date is
>   2025-08-22, a Friday — the notation vote this document itself excludes.
>   Corrected weekday cells are **204**+164+56+51+7 = 482; TOM 400+82; AUCTION
>   409+73; LOYO 450..467. The machine artifact was never wrong.
> * **§3's claim that the two authorities “agree exactly”, with TA's four
>   extras being “precisely unscheduled actions”, is WITHDRAWN as imprecise.**
>   The Fed-parser unscheduled set and TA's extra set share only ONE member
>   (2020-03-15); they are keyed to meeting dates versus statement-release
>   dates over different universes. The accurate claim is that every TA extra
>   is a NON-SCHEDULED statement release.
>
> The hard-coded 2025-08-22 exclusion is also replaced by a general,
> source-based filter (`f6_fomc_filter.py`) that needs no count heuristic.
> All headline counts in this document — 482 / 122 / 185 / 185 / 10 — remain
> correct.

HOLD, not PARK: all three families' event lists **can** be formed from source,
the scheduled-before-entry test **is** satisfiable in principle, and the fixed
control model is **full rank**. Each family carries a named, repairable metadata
gap, and one reused authority carries a demonstrated defect.

---

## §1 Provenance — and a gap that must be repaired before S1

```
F6_INDEPENDENT_ADJUDICATION_PROVENANCE_GAP = YES
```

Checked mechanically, not assumed. `git ls-files` across the repository and a
listing of the workspace root return **no F6 independent adjudication artifact**
of any kind. The only pre-S0 adjudication present is F4's
(`2026-09-18-cta-edge-05-f4-inventory-state-pre-s0-independent-adjudication-fable-01.md`).

**No artifact or hash is fabricated for it.** The adjudication verdict is
carried only by the controller's relayed statement. This gap **must be repaired
before S1 sealing**; it does not authorize return access and it does not block
this metadata audit.

Verified and hash-pinned Phase-0 authorities:

| artifact | sha256 (24) |
|---|---|
| Round-1 discovery map (F6 origin) | `02ca5f45fe41763e55a35309` |
| Round-1 backlog exhaustion review | `ec68547264dd95f022010b37` |
| F6 OD-1a..1h S0 design decisions | `0066584e7c4267926a6977eb` |
| F6 OD-2a..2h pooling / control / gates | `4adaadc8f5be6ce0bc2a928c` |
| `ta/TA_MACRO_CALENDAR.csv` | `8f10675033267136cb2622bf` |
| `ta/TA_EVENT_CALENDAR.csv` (auctions) | `b27be5b1d94cfc13fc8310e0` |
| `src/seasonality.py` (sealed TOM) | `43a75588b95f6ec42b090bc6` |
| `data/DGS3MO.csv` | `50da2bfbb25e3e3241af7a4a` |
| `data/close_prices_raw.csv` | `3d2a7a56dbd92d4ff8138cfd` |
| `mmv/mmv_policy_schedule_freeze.py` | `81371c07c374684144e7a6d5` |

`SAMPLE_REUSE.md`, `TRIAL_LEDGER.md` and `EXPOSURE_LEDGER.md` were read and
**not modified**.

---

## §2 The primary event sample

```
PRIMARY_START_DATE   2011-01-07   (first eligible event session on/after 2011-01-01)
PRIMARY_END_DATE     2026-06-10   (last event session within the 2026-06-12 boundary)

PRIMARY_EVENT_COUNT      482   event trading sessions
  FOMC_EVENT_COUNT       122   scheduled policy-statement releases
  CPI_EVENT_COUNT        185
  NFP_EVENT_COUNT        185
  MULTI_EVENT_DAY_COUNT   10   (all CPI+FOMC)

122 + 185 + 185 = 492 family labels over 482 sessions. The 10-session
difference is exactly the multi-event days, which carry ONE unit, ONE trade and
ONE observation each. No double notional anywhere.
```

Multi-event sessions: 2013-10-30, 2014-09-17, 2014-12-17, 2016-03-16,
2017-03-15, 2017-06-14, 2017-12-13, 2019-12-11, 2020-06-10, 2024-06-12.

---

## §3 FOMC — the reused authority had a defect, and the cross-check caught it

```
FOMC_SCHEDULE_PIT = HOLD
```

The frozen rule refused to let `TA_MACRO_CALENDAR` define the FOMC event, and
that refusal was correct: its `detail` field reads *"FOMC statement"* for all
171 rows with no scheduled/unscheduled distinction, it contains unscheduled
actions, and it omits 2008-01-22 entirely.

The event list was therefore formed from the **Fed's own annotations** via
`mmv_policy_schedule_freeze.scheduled_meeting_end_dates()`, which parses the
Fed's `(unscheduled)` and `(cancelled)` labels from hash-recorded
`federalreserve.gov` pages.

**Excluded as unscheduled** (not knowable at close(t−1), so including them would
be look-ahead): `2011-08-01`, `2011-11-28`, `2020-03-02`, `2020-03-15`.

### 3.1 The defect

The rule's mandated cross-check against the TA calendar raised one exception:

```
Fed-scheduled but absent from TA : 2025-08-22
```

Verified against tier-1 authority — the Fed's own `fomccalendars` page — which
lists **exactly eight** scheduled 2025 meetings and shows 2025-08-22 as a
**notation vote releasing the "Statement on Longer-Run Goals and Monetary Policy
Strategy"**. That is not a meeting policy-statement release, so under frozen
rule §5 it is **excluded**, taking FOMC from 123 to **122**.

```
THE REUSED scheduled_meeting_end_dates() TREATS A NOTATION VOTE AS A SCHEDULED
MEETING END. It carries no notation-vote filter. That is a real defect in a
pinned authority and it is why FOMC is HOLD rather than PASS.
```

It was harmless for MMV, which only needed target-change dates. It is **not**
harmless for F6, whose event *is* the statement release.

**Honest limitation of my own detection.** I found it by a per-year count
anomaly — every year has 8 scheduled meetings except 2020's 7 (the March 17–18
meeting was *cancelled*, which the Fed labels and the parser correctly drops)
and 2025's 9. That method would **miss** a notation vote in a year that also had
a cancellation, since the counts would net to 8. A general source-based filter
is owed before S1; I did not build one.

After the exclusion the two authorities agree exactly: **0** Fed-scheduled dates
absent from TA, and TA's 4 extras (`2019-10-11`, `2020-03-03`, `2020-03-15`,
`2020-03-23`) are precisely unscheduled actions.

---

## §4 CPI and NFP — a shared, specific blocking gap

```
CPI_SCHEDULE_PIT = HOLD
NFP_SCHEDULE_PIT = HOLD
```

Dates come from `TA_MACRO_CALENDAR`, itself derived from BLS annual release
schedules with a `source_url` per row. BLS publishes those schedules a year
ahead, which is what makes the scheduled-before-entry test satisfiable in
principle.

The heuristic cross-checks the rule permits — permitted only to *raise
exceptions*, never as authority — raised these:

```
NFP not on a Friday (8)  2013-10-22, 2014-07-03, 2015-07-02, 2020-07-02,
                         2025-07-03, 2025-11-20, 2025-12-16, 2026-02-11
NFP later than the 12th  2013-10-22, 2025-11-20, 2025-12-16
month with NO CPI        2025-11
month with NO NFP        2025-10
```

`2013-10-22` is the October 2013 federal-shutdown postponement of the September
employment report. The July Thursday releases are routine pre-Independence-Day
scheduling. The 2025-10 NFP and 2025-11 CPI absences with the late 2025-11-20
and 2025-12-16 NFP dates are consistent with a 2025 shutdown suspension. **None
of that is asserted as a cause** — each is an exception awaiting a BLS schedule
document.

### 4.1 The gap, stated precisely

```
TA_MACRO_CALENDAR records ACTUAL release dates. It carries NO field marking a
date as originally-scheduled versus postponed, and NO field for WHEN a
postponement was announced.
```

Frozen rule §4 asks whether a postponement was known **before close(t−1)**.
That question **cannot be answered from the pinned authority alone** — it needs
the BLS schedule documents themselves. Until it is, every postponed release is
a date whose entry-time knowability is unverified.

```
POSTPONEMENT_CASES = 8 exceptions raised, of which 2013-10-22, 2025-11-20 and
2025-12-16 are the strong postponement candidates, plus 2 suspended months
(2025-10 NFP, 2025-11 CPI). Metadata only. No ex-post correction was applied
and no original planned date was substituted.
```

Release **times** are also not established: `TA_MACRO_CALENDAR` has no time
column, and no per-event publisher time document was retrieved. Under the rule
that is `NOT_ESTABLISHED`, never guessed.

---

## §5 NYSE session mapping

```
NYSE_SESSION_MAPPING = PASS
```

Sessions are the frozen panel's own index, so holidays, Good Friday and early
closes need no special case.

```
releases on a NON-trading day, mapped forward to the next session
  FOMC  0
  CPI   2   2017-04-14 -> 2017-04-17 ; 2020-04-10 -> 2020-04-13
  NFP   5   2012-04-06 -> 2012-04-09 ; 2015-04-03 -> 2015-04-06 ;
            2021-04-02 -> 2021-04-05 ; 2023-04-07 -> 2023-04-10 ; +1
```

Every one is a Good Friday. FOMC never lands off-session, as expected for
meetings scheduled around the trading week.

```
entry/exit availability: 482 / 482 event sessions have a SPY observation at
BOTH close(t-1) and close(t). No event lacks a tradable entry or exit.
```

---

## §6 Control design matrix — FULL RANK

```
DESIGN_MATRIX_RANK_OK                = YES
EVENT_PERFECTLY_PREDICTED_BY_CONTROLS = NO
```

Built from calendar metadata only. **No returns were attached.**

```
rows                3883 sessions (2011-01-03 .. 2026-06-12, first row dropped
                    because HOLD is undefined for it)
columns (9)         const, weekday_Monday, weekday_Thursday, weekday_Tuesday,
                    weekday_Wednesday, EVENT, TOM, HOLD, AUCTION
shape               (3883, 9)      rank 9      FULL RANK
smallest singular values   20.085, 16.911, 12.056, 9.541   — no near-singularity
rank(controls) = 8 ; rank(controls + EVENT) = 9
  => EVENT is NOT in the span of the controls
```

Column provenance is reused, not redefined:

```
TOM      src/seasonality.py::is_tom, SEALED — last=1, first=3
         (config.SEAS_TOM_LAST / SEAS_TOM_FIRST), 743 TOM days
AUCTION  TA_EVENT_CALENDAR.csv, tenor families 10-Year and 30-Year ONLY,
         definition unaltered, 373 auction sessions
HOLD     calendar days between close(t-1) and close(t):
         1:3038  2:40  3:700  4:104  5:1
```

No empty cells anywhere:

```
EVENT x weekday   Fri 205/576 · Wed 164/632 · Thu 56/726 · Tue 51/748 · Mon 7/718
EVENT x TOM       TOM=1: 82 events / 661 non-events ; TOM=0: 401 / 2739
EVENT x AUCTION   AUCTION=1: 73 events / 300 non-events ; AUCTION=0: 410 / 3100
```

**Monday is thin — 7 event days out of 725 Mondays — but it is not empty**, so
it does not break rank. It is reported as a factual sparsity, not diagnosed.

No interaction, no alternate model and no model selection was attempted, and no
column was dropped. `beta_EVENT` was **not** estimated.

---

## §7 Inference feasibility

```
YEAR_BLOCK_COUNT = 16   (2011 .. 2026)
YEAR_BLOCK_INFERENCE_OWNER_REVIEW_REQUIRED = YES
```

Mechanically implementable: every calendar year is a non-empty block and every
leave-one-year-out deletion leaves a large remainder.

```
events per year  2011:32 2012:32 2013:31 2014:30 2015:32 2016:31 2017:29
                 2018:32 2019:31 2020:30 2021:32 2022:32 2023:32 2024:31
                 2025:30 2026:15
LOYO remaining   451 .. 467 events in every case
```

**The factual reason for Owner review**, stated without proposing a fix: of the
16 blocks, **15 are full years carrying 29–32 events and one — 2026 — is a
partial year of 15 events covering roughly 5.4 months**, because the sample ends
at the frozen panel boundary 2026-06-12. That asymmetry touches both proposed
uses of the year block: it is an unequal block in a calendar-year block
bootstrap, and under P3 the leave-2026-out fold deletes about half the data a
normal fold deletes.

**No replacement inference method was chosen and no alternative blocking was
tried.**

---

## §8 Cash authority — two findings

```
DGS3MO_AUTHORITY = FRED DGS3MO, "Market Yield on U.S. Treasury Securities at
                   3-Month Constant Maturity, Quoted on an Investment Basis",
                   Board of Governors via the H.15 Selected Interest Rates release
DGS3MO_DAY_BASIS = NOT ESTABLISHED FROM SOURCE
DGS3MO_PIT       = HOLD
FORWARD_FILL_RULE_VALID = YES (mechanically), subject to §8.2
```

### 8.1 Day basis is not what the design assumed

The series is quoted on an **investment (coupon-equivalent) basis**, not a
discount basis — that much is stated in the series title. But **H.15 does not
state a day-count convention for constant-maturity yields**; it defers to
Treasury yield-curve methodology, and its "360-day year or bank interest"
footnote applies to other instruments, not CMT.

```
THE /365 SIMPLE-ACCRUAL ASSUMPTION IS NOT CONFIRMED BY SOURCE.
```

Reported as the source-defined position rather than adopted or replaced. This is
a metadata correction, not an outcome-driven redesign, and resolving it is an
Owner decision.

### 8.2 A publication-timing finding that affects entry

```
H.15 is posted daily Monday-Friday at 4:15 p.m. ET.
The NYSE close is 4:00 p.m. ET.
=> DGS3MO(d) is NOT knowable at close(d).
```

A cash rate "known at entry" is therefore at best `DGS3MO(t−2)`, not
`DGS3MO(t−1)`. The design's cash convention has not been checked against this,
and this audit does not choose the lag.

Missing observations: H.15 is not posted on holidays or when the Board is
closed; **167 of 4030 in-window rows are missing**. Forward-filling the last
available value is mechanically sound — it uses only past observations, so it
introduces no look-ahead — but it inherits the 16:15 finding above.

---

## §9 SPY / execution metadata

```
SPY_METADATA_COVERAGE = PASS
```

```
SPY span                    1993-01-29 .. 2026-06-12, covering the whole window
event sessions with close(t)     482 / 482
event sessions with close(t-1)   482 / 482
```

**Adjusted-close limitation, carried forward unchanged:** the panel is a single
vendor (yfinance) **adjusted**-close matrix with no separate raw/adjusted
columns. Adjusted-close status is `ACCEPTABLE_WITH_LIMITATION` and is **not
proven perfect point-in-time**. No ratio, return or price level was computed;
the panel was opened for its date index and for observation presence only.

---

## §10 Firewall and accounting

```
RETURN_OUTCOME_ACCESSED   = NO      BETA_EVENT_COMPUTED       = NO
F6_PRIMARY_RETURN_COMPUTED= NO      F6_PRIMARY_TRIAL_CONSUMED = NO
TLT_RETURN_ACCESSED       = NO      F6B_RETURN_ACCESSED       = NO
Sharpe · intervals · LOYO performance · pre/post-2015 differences ·
NQ outcome data · consensus · actual release values · surprises = none touched
```

No return family was executed. No performance-exposure row is created. Schedule
metadata reads are `DESIGN_INFORMING_MEASUREMENT` on non-target inputs and were
never joined to a price.

---

## §11 What is owed before S1

```
1. the F6 independent adjudication artifact (provenance gap, §1)
2. a source-based NOTATION-VOTE filter for the FOMC authority (§3.1)
3. BLS schedule documents to decide postponement knowability at close(t-1) (§4.1)
4. publisher release TIMES for CPI, NFP and FOMC (§4)
5. an Owner ruling on the partial 2026 year block (§7)
6. an Owner ruling on the DGS3MO day basis and the 16:15 publication lag (§8)
```

None of these is resolved here, and none authorizes return access.
