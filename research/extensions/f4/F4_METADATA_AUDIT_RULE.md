# CTA-EDGE-05 / F4 — METADATA & PIT AUDIT RULE

**Frozen BEFORE any sampled historical record was retrieved.**

```
RECORD_TYPE = METADATA_PIT_AUDIT_RULE
LINEAGE     = CTA-EDGE-05 (F4 INVENTORY_STATE_COMMODITY_CURVE)
DATE        = 2026-09-18
RULE_ID     = F4-AUDIT-RULE-1
BASE        = PINS-AUDIT-RULE-1, research/extensions/pins/PINS_OD1_FEASIBILITY_PROTOCOL.md
              sha256 fad05d1533bead98051c4464... (§2), frozen 2026-09-16 for CTA-EDGE-03-PINS
SCOPE       = source metadata and point-in-time reconstructibility ONLY.
              No F4 inventory state, no z-score, no basis, no trend, no return.
```

**Why this document exists at all.** A feasibility audit that chooses its sample after
seeing what is retrievable will always report that retrieval works. The sample below is
fixed by a rule over publication calendars alone.

---

## §0 Retrieval status at the moment of freezing — stated so it can be checked

```
SAMPLED HISTORICAL RECORDS RETRIEVED BEFORE THIS FREEZE = NONE
```

What *was* retrieved before freezing, and is permitted because none of it is a sampled
historical record: **current** release documents and the publishers' own **standing
metadata** — release-schedule pages, revision-policy pages, series-identifier listings,
archive landing pages and the single most-recent release of each report. PINS did the
same when it enumerated and hashed the WPSR archive index inside its own protocol §2.

Enumerating a complete calendar is the opposite of choosing a sample: it fixes the frame
the rule then selects from, without discretion.

---

## §1 The reused rule — PINS-AUDIT-RULE-1

Reproduced from the PINS protocol §2 and **reused unchanged in structure**:

```
STRATA, per calendar year Y
  ORD(Y)   releases on the source's OWN ordinary publication day
  SHF(Y)   releases NOT on the ordinary day
  ODD(Y)   releases beyond a ONE-DAY shift from the ordinary day

SELECTION, per year, lists sorted ascending by date, 0-indexed
  ordinary_1 = ORD(Y)[ floor( len(ORD(Y)) / 3 ) ]
  ordinary_2 = ORD(Y)[ floor( 2 * len(ORD(Y)) / 3 ) ]
  shifted    = ODD(Y)[ floor( len(ODD(Y)) / 2 ) ]   if ODD(Y) is non-empty
               SHF(Y)[ floor( len(SHF(Y)) / 2 ) ]   otherwise

RESULT       3 releases per calendar year
```

**Nothing numeric in that block was chosen by this audit.** The three-per-year count, the
`floor(n/3)`, `floor(2n/3)` and `floor(n/2)` positions and the ORD/SHF/ODD stratification
are all PINS's, adopted verbatim.

### §1.1 The only adaptations, each named with its justification

The brief permits adaptation "only to source cadence where mechanically necessary".
Three adaptations qualify. Each is stated so the Owner can reject it.

```
A-1  ORDINARY DAY IS SOURCE-DEFINED, not fixed at Wednesday.
       WPSR   Wednesday  (EIA's own schedule; PINS's original value)
       WNGSR  Thursday   (EIA: "at 10:30 a.m. eastern time on Thursdays",
                          ir.eia.gov/ngs/schedule.html, read 2026-09-18)
     Mechanically necessary: PINS's "Wednesday" is not a universal constant, it is the
     WPSR's publication day. Substituting each source's own day preserves the rule.

A-2  MONTHLY CADENCE HAS NO WEEKDAY STRATA (WASDE only).
     WASDE is monthly at 12:00 ET, released in USDA's own documented day-of-month window
     (releases fall on the 9th-12th; the 2026 calendar runs Jan 12, Feb 10, Mar 10,
     Apr 9, May 12, Jun 11, Jul 10, Aug 12, Sep 11, Oct 9, Nov 10, Dec 10).
       ORD(Y)  day-of-month in [9, 12]      <- USDA's own window, not chosen here
       SHF(Y)  day-of-month outside [9, 12]
       ODD(Y)  day-of-month outside [8, 13] <- "beyond a one-day shift", the structural
                                               analogue of PINS's ODD
     The [8, 13] boundary is THIS AUDIT'S STRUCTURAL ANALOGUE of PINS's "beyond a
     one-day holiday shift", not a source convention. It is flagged as the single
     adaptation with no direct source authority; it affects WHICH irregular release is
     sampled, never any F4 quantity.

A-3  FRAME WINDOW = source archive extent INTERSECTED with the verified Databento
     commodity-futures panel span 2010-06-06 .. 2026-07-01
     (LOCKBOX_PROCEDURE.md §2.2, VERIFIED from the carry manifest).
     Justification: inventory vintages outside the futures coverage cannot serve the F4
     estimand at all, so auditing them would spend effort on periods F4 can never use.
     The archive's TRUE full extent is reported separately as a metadata fact and is NOT
     truncated in the report.
```

**No pass-threshold percentage is invented.** PINS's 90 %/95 % retrieval thresholds were
written for its own two objects (a survey consensus and an API print) and are not
transplanted. This audit classifies with the **brief's own A-F taxonomy**, which is
categorical, and fails closed (§4).

---

## §2 The frames and the realized samples

### §2.1 PETROLEUM — WPSR. Sample REUSED, not re-selected.

```
FRAME     research/extensions/pins/PINS_EIA_RELEASE_DATES.txt
          sha256 98a3ebdc4a006075097468994b194c0fb2843fe834ab94a0a363c3c03c91f9e4
          765 releases, 2012-01-05 .. 2026-09-10
SAMPLE    research/extensions/pins/PINS_AUDIT_SAMPLE.json
          sha256 52e70b40e61a7b36057e2345f116c94bdab9ab091f6caa4bdf7d78178204283a
          45 releases, 3 per year 2012..2026, rule_id PINS-AUDIT-RULE-1
```

F4's petroleum legs are carried by the **same WPSR releases** PINS already sampled, so
the PINS sample is adopted **verbatim**. This is the strongest available anti-selection
property in this audit: the 45 dates were fixed on **2026-09-16**, in a different
lineage, for a different question, **before F4's S0 existed**. They cannot have been
chosen to suit F4.

### §2.2 NATURAL GAS — WNGSR. Frame NOT YET ENUMERATED.

```
FRAME     to be enumerated from EIA's own WNGSR release calendar / archive index,
          Thursdays, intersected per A-3
SAMPLE    NOT YET REALIZED. Determined by §1 once the frame is enumerated.
```

### §2.3 GRAINS / OILSEEDS — WASDE. Frame NOT YET ENUMERATED.

```
FRAME     to be enumerated from the ESMIS/NAL WASDE archive listing
          (esmis.nal.usda.gov; migrated from Cornell Mann Library 2025-10-01),
          monthly, intersected per A-3
SAMPLE    NOT YET REALIZED. Determined by §1 + A-2 once the frame is enumerated.
```

**A frame that is not yet enumerated cannot be sampled**, and no sampled historical
WNGSR or WASDE record may be retrieved until it is. That is the whole point of freezing
this document first.

---

## §3 Required per-series metadata fields

A series is only ever described by fields **verified from the publisher's own material**.
Nothing is inferred from a modern website convention and back-dated.

```
SOURCE · SERIES or TABLE ID · UNITS · REFERENCE PERIOD · PUBLICATION CADENCE
NORMAL PUBLICATION DAY and CLOCK TIME with TIMEZONE
HOLIDAY SHIFT SEMANTICS · REVISION SEMANTICS
HISTORICAL ARCHIVE START
FIRST-PUBLISHED VALUES RECONSTRUCTIBLE       YES / NO / PARTIAL
LATEST-KNOWN-AS-OF RECONSTRUCTIBLE           YES / NO / PARTIAL
SOURCE-DEFINED SEASONAL REFERENCE            present? reconstructible PIT?
```

## §4 What counts as verified — and how this rule fails

```
TIMESTAMP VERIFIED
  the publisher states a release DATE and CLOCK TIME with a TIMEZONE, in its own
  material. A date alone is NOT a verified timestamp.

FIRST-PUBLICATION RECONSTRUCTION ESTABLISHED
  requires BOTH
    (i)  a DATE-ADDRESSABLE SYSTEMATIC archive of per-release vintages, OR a
         publisher-maintained record of pre-revision original estimates; AND
    (ii) the target field present in the sampled vintages.
  PINS's finding that "no DATE-ADDRESSABLE systematic archive was located" is the
  precedent for treating (i) as decisive.

LATEST-KNOWN-AS-OF RECONSTRUCTION ESTABLISHED
  the full history as it stood at each decision date is recoverable — i.e. current
  history PLUS a complete revision record, or a per-release vintage archive.

METHODOLOGY BREAK
  a change the PUBLISHER ITSELF documents: a definitional change, a series
  discontinuity, a table renumbering, a coverage or sample change, a unit change, a
  revision-policy change, or a change in publication time.
  Bound to publisher documentation precisely so this audit never has to invent a
  numeric test for "break".

MISSING DOCUMENT
  EXPLICITLY LISTED. No imputation, no substitution from an adjacent release, no
  cross-source filling. (PINS §7, adopted.)

FAIL-CLOSED
  Any sampled release that cannot be retrieved, or whose target field or timestamp
  cannot be verified, prevents class A. The series lands in B or D per the brief's
  taxonomy. A series is NEVER upgraded to A by assumption.
```

## §5 Pass / hold / park semantics

Per-series classification uses the **brief's own taxonomy**, not a threshold invented
here:

```
A  PIT_RECONSTRUCTIBLE                         D  ARCHIVE_EXISTS_BUT_FIRST-PUBLICATION
B  LIKELY_RECONSTRUCTIBLE_BUT_ONE_METADATA_GAP    NOT_ESTABLISHED
C  CURRENT/REVISED_HISTORY_ONLY                E  NOT_RECONSTRUCTIBLE
                                               F  IDENTITY_UNRESOLVED
```

```
FAMILY PASS   every load-bearing series in the family is class A
FAMILY HOLD   no series is class C or E, but at least one is B, D or F
              -> not established, no blocker proven, verification incomplete
FAMILY PARK   any load-bearing series is class C or E
              -> a proven blocker

LOAD_BEARING GATE   the controller's rule: if EITHER load-bearing family
                    (ENERGY, GRAINS/OILSEEDS) cannot be reconstructed at
                    research-grade PIT, PARK F4 PRE-OUTCOME.
                    Never silently continue with one surviving family.
```

**Minimum root count is NOT defined here.** If a family is otherwise viable but one root
inside it fails, this audit returns
`ROOT_LEVEL_REDUCTION_OWNER_DECISION_REQUIRED = YES` and names the root. It does not
drop the root and it does not invent a tolerance.

## §6 Forbidden throughout this audit

```
F4 TIGHT/AMPLE label      inventory z-score         basis
inventory/basis correlation                         future commodity returns
trend returns             F4 primary return series  Sharpe        hit rate
transform optimisation    X43                       any backtest
any trailing lookback, window, percentile, threshold or composite weight
```

Reading **source-side inventory values** for the frozen sample is permitted at Phase 5
and is classified `DESIGN_INFORMING_MEASUREMENT`: inventory is INPUT data, not an F4
market outcome. It may never be combined with futures price, basis or return data.
