# CTA-EDGE-03-PINS — PINS-OD-1 FEASIBILITY AUDIT PROTOCOL

**Written and frozen BEFORE any consensus or API value was retrieved.**

```
RECORD_TYPE = FEASIBILITY_AUDIT_PROTOCOL
LINEAGE     = CTA-EDGE-03-PINS
DATE        = 2026-09-16
AUTHORITY   = ../../../ops/OWNER_DECISION_RECORD_CTA_EDGE_03_PINS.md  (PINS-OD-1)
SCOPE       = expectation-data feasibility ONLY. No price data of any kind.
```

The point of freezing this document first is narrow and important: a feasibility audit
that chooses its own sample after seeing what is retrievable will always report that
retrieval works. The sample below is fixed by a rule over the EIA release calendar alone,
and the selected dates were committed before a single consensus or API figure was looked
up.

---

## §1 What is being audited

```
C  = named pre-API analyst-survey consensus            -> the EXPECTATION ANCHOR
P  = first-reported API pre-release crude estimate     -> MANDATORY SECOND PIT INPUT
A  = first-published EIA weekly crude inventory change -> already YES from 2012-01-05
                                                          (PINS_S0_FRAME.md §B.2)
```

Both `C` and `P` must be historically reconstructible point-in-time. Either alone fails
PINS-OD-1.

**Not audited here, and not permitted here:** any WTI price, any return, any scarcity
feature, any interaction, any regression, any `k`.

---

## §2 PINS-AUDIT-RULE-1 — the frozen sample selection rule

**Inputs: EIA release dates, calendar year, and weekday only.** No outcome, no price, no
news salience, no event fame.

```
UNIVERSE
  every archived EIA WPSR release, enumerated from the per-release archive index's own
  link structure (the directory name IS the release date).
    765 releases, 2012-01-05 .. 2026-09-10
    archive index sha256 032a8955053ed30ca373af112f7c67e84edb1709d40794688d13bfefa6e84141
    weekday distribution: Wed 651 · Thu 102 · Fri 10 · Mon 2

STRATA, per calendar year Y in 2012..2026
  ORD(Y)   releases in Y with weekday == Wednesday          (ordinary)
  SHF(Y)   releases in Y with weekday != Wednesday          (holiday-shifted)
  ODD(Y)   releases in Y with weekday not in {Wed, Thu}     (irregular beyond a
                                                             one-day holiday shift)

SELECTION, per year, all lists sorted ascending by date, 0-indexed
  ordinary_1 = ORD(Y)[ floor( len(ORD(Y)) / 3 ) ]
  ordinary_2 = ORD(Y)[ floor( 2 * len(ORD(Y)) / 3 ) ]
  shifted    = ODD(Y)[ floor( len(ODD(Y)) / 2 ) ]   if ODD(Y) is non-empty
               SHF(Y)[ floor( len(SHF(Y)) / 2 ) ]   otherwise

RESULT
  3 releases per year x 15 years = 45
```

The `ODD` preference exists so that genuinely irregular release times — the Friday and
Monday releases, which carry 11:00, 12:00 and 17:00 ET timestamps rather than 10:30 — are
represented rather than left to chance. It is stated as a rule, not applied case by case.

## §3 The frozen sample

```
AUDIT_SAMPLE_N        = 45
AUDIT_SAMPLE_RANGE    = 2012-05-02 .. 2026-06-24
PER YEAR              = 3 in every one of 2012..2026, no exceptions
PER STRATUM           = 30 ORDINARY_WEDNESDAY · 15 SHIFTED_IRREGULAR
WEEKDAY MIX           = Wed 30 · Fri 7 · Thu 6 · Mon 2
FILE                  = PINS_AUDIT_SAMPLE.json
FILE sha256           = 52e70b40e61a7b36057e2345f116c94bdab9ab091f6caa4bdf7d78178204283a
CALENDAR FILE         = PINS_EIA_RELEASE_DATES.txt  (765 lines)
CALENDAR sha256       = 98a3ebdc4a006075097468994b194c0fb2843fe834ab94a0a363c3c03c91f9e4
```

Two selected dates deserve a note, because both were produced **by the rule** and not
chosen:

* **2013-10-21 (Monday)** — the October 2013 federal government shutdown delayed EIA
  publication. It is exactly the kind of irregular release the rule is meant to surface,
  and its presence is a property of the calendar, not of anyone's judgement.
* **2025-12-29 (Monday, 17:00 ET)** — the Christmas-week release. A release whose
  timestamp is neither 10:30 nor a Thursday noon is the hardest case for any
  `C < P < A` ordering test, which is why the rule reaches for it.

---

## §4 Survey-family audit fields — required per family

A family qualifies only if every field below is **verified**, not inferred:

```
named source                    the publishing organisation, by name
exact headline statistic        mean / median / other — READ OFF THE FAMILY'S OWN
                                MATERIAL. Never defaulted. (PINS-S0-AMD-01 §3)
respondent count                if published
survey cut-off                  when responses close
publication timestamp           date AND time, with timezone
pre-API snapshot?               is the archived value the one published BEFORE the
                                Tuesday API print, or a later refresh?
overwrite behaviour             do later updates overwrite the historical value?
target quantity                 weekly change in U.S. commercial crude stocks excl. SPR
units                           thousand vs million barrels
sign convention                 build positive or draw positive
historical coverage             first available release, and gaps
licence / storage rights        may the value be retained and used in this repository?
```

```
An undocumented economic-calendar "forecast" field is NOT ACCEPTED unless it can be
mechanically tied to a NAMED SURVEY FAMILY and a TIMESTAMP.
```

## §5 Family selection rule — outcome-free

```
Among legally usable named survey families that satisfy the point-in-time definition,
PREFER THE FAMILY WITH THE HIGHEST VERIFIED HISTORICAL COVERAGE.

No WTI price data may enter this selection.
Do NOT combine families.
Do NOT fill missing weeks from another family.
A second family may later be a PREREGISTERED ROBUSTNESS SERIES only.
```

Retry budget: if the first family fails, **one** retry on **one** second named family is
allowed, on point-in-time / coverage / access grounds only.

---

## §6 Pilot pass thresholds — fixed in advance

```
CONSENSUS PILOT PASS requires ALL of:
  >= 90 % retrieval coverage over the 45 predeclared releases   (>= 41 of 45)
  every covered calendar year represented
  each retained C demonstrably published BEFORE the API print
  named-family provenance
  statistic identified
  unit / target match
  no licensing or lawful-storage blocker

API PILOT PASS requires ALL of:
  >= 95 % retrieval coverage over the 45 predeclared releases   (>= 43 of 45)
  first-reported headline status reconstructible
  publication timestamp before the EIA release
  unit / target match
  no licensing or lawful-storage blocker

PER-ROW ORDERING, required for every retained row:
  timestamp(C)  <  timestamp(P)  <  timestamp(A)

  unless an OBJECTIVELY DOCUMENTED exceptional publication schedule requires a
  different but still valid order — in which case the exception is REPORTED, never
  improvised around.
```

## §7 Full-series eligibility — what a pilot PASS would authorise

A pilot PASS authorises **full-series acquisition or reconstruction only**. It does not
authorise S1, a seal, a build, a run, or a purchase.

```
Before any future sealing, the intended full historical inputs must be capable of:

  CONSENSUS   >= 95 % of all scheduled releases in the window
              AND no calendar year below 90 %
  API         >= 95 % overall

  Missing releases: EXPLICITLY LISTED.
  No imputation. No cross-family filling.
  A thin survey (n < 5 respondents) is FLAGGED, not dropped.
```

## §8 Quantity identity check

`C`, `P` and `A` must refer to the same intended quantity, or every non-equivalence must
be documented.

```
TARGET  = weekly CHANGE in U.S. COMMERCIAL crude oil inventories EXCLUDING SPR

CHECK   stock vs change           commercial vs total
        SPR inclusion             thousand vs million barrels
        sign convention (build positive vs draw positive)

OUTCOME-FREE CONSISTENCY CHECK: where pre-release survey material quotes the PRIOR
WEEK'S ACTUAL, that quoted figure may be compared against the archived EIA vintage for
the same prior week. This uses no price and is a units/definition check only.
```

## §9 Information-timing diagnostic — deferred by default

The adopted advice proposes a future **Gate 0.5**: whether the API print materially
updates the pre-API analyst consensus before the EIA release.

```
AT THIS STAGE: establishing that comparable C and P observations EXIST is permitted.
               FITTING the PINS return model is NOT.

Any price-free inventory-only diagnostic must:
   use no WTI price          have NO PROMOTION POWER
   be declared BEFORE computation      be labelled a feasibility / information-timing
                                       diagnostic
   NEVER be used to fit k

If the diagnostic is not necessary to resolve feasibility: DEFER IT.
```

**Declared position: deferred.** Feasibility turns on whether `C` and `P` are lawfully
reconstructible at all. Nothing about the size of `P − C` changes that answer, so
computing it now would spend information for no decision value.

## §10 Forbidden throughout

```
WTI post-release returns        pre/post price charts       release-day reactions
inventory-conditioned returns   historical PINS regression  event P&L
Sharpe                          hit rate                    horizon comparison
latency comparison              historical scarcity feature scarcity interaction
outcome-conditioned sample selection                        any estimate of k
```
