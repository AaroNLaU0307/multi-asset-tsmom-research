# CTA-EDGE-04-MMV — PREREGISTRATION CONTRACT (S1 DESIGN)

```
LINEAGE      = CTA-EDGE-04-MMV
CANDIDATE    = MACRO_MOMENTUM_VINTAGE
CONTRACT_ID  = CTA-EDGE-04-MMV-PREREG-01
STATUS       = SEALED AT S1
DATE         = 2026-09-17
ORIGIN       = Fable Round-1 discovery map, family F5
             Quant trade/2026-09-15-cta-edge-discovery-r1-mechanism-feature-map-fable-01.md
             sha256 02ca5f45fe41763e55a353090645c3b2a98b6dcf5fce572623ede604e569344a
OWNER DECISIONS = MMV-OD-1 .. MMV-OD-6
             ../../../ops/OWNER_DECISION_RECORD_CTA_EDGE_04_MMV.md
```

This document is the **sole design authority** for CTA-EDGE-04-MMV. S2 implements it and
makes no scientific choice. Where this contract and any other document disagree, this
contract wins.

**Outcome blindness at seal.** No historical MMV macro feature, composite, position
matrix, separability figure, first-release disagreement figure, return, Sharpe or
bootstrap existed anywhere when this was written, and none exists now.

---

## §A The research object — LOCKED

```
MECHANISM (F5 field 2, verbatim)
  "Markets underreact to slow-moving changes in growth, inflation and policy the way
   they underreact to price: releases are noisy, lagged and revised; consensus and
   institutional allocation update over quarters. A sleeve that trades the direction of
   change in fundamentals earns the premium for acting on slow information before the
   consensus catches up."

CLAIM TYPE = REDUCED-FORM PREDICTIVE. Not causal. Not a macro nowcast. Not a regime
             classifier. Never a gate on the canonical book.
PRIMARY SIGNAL LABEL = POINT_IN_TIME_MACRO_STATE_MOMENTUM
```

The traded object is a **state**, re-read monthly, not a **shock**. Revisions enter only
by changing that state; the information shock between two decision dates is never
decomposed and never conditioned on.

---

## §B Information concept — LOCKED (MMV-OD-1)

```
PRIMARY_INFORMATION_CONCEPT = LATEST_KNOWN_AS_OF_DECISION_DATE

At each canonical monthly decision date, reconstruct the macro history exactly as
publicly known at that cutoff.

IT IS NOT: macro news · macro surprise · first-release alpha · revision alpha
FINAL-REVISED HISTORY IS FORBIDDEN as a substitute, in any cell, at any stage.
```

```
FIRST_RELEASE_CHAIN = DESCRIPTIVE CONCORDANCE DIAGNOSTIC ONLY
  PROMOTION_POWER = NONE · RESCUE_POWER = NONE · KILL_POWER = NONE
  NO large/small disagreement threshold exists or may be introduced.
```

### B.1 Availability authority, per leg

Two different authorities, because the legs are different kinds of object. This is the
single most important clarification in this contract and it is stated in full, with the
metadata limitation that prompted it, in §B.2.

```
GROWTH  (INDPRO, PAYEMS)   ALFRED vintage reconstruction.
INFLATION (CPILFENS)       ALFRED vintage reconstruction.
POLICY  (FOMC target)      OFFICIAL FOMC / FEDERAL RESERVE ANNOUNCEMENT DATE AND TIME.
                           ALFRED vintage reconstruction is NOT required and NOT used.
                           ALFRED_REALTIME_START_USED_FOR_AVAILABILITY = NO
                           OFFICIAL_FOMC_ANNOUNCEMENT_USED_FOR_AVAILABILITY = YES
```

The policy target eligible at cutoff `t` is **the latest administered target or target
range publicly ANNOUNCED at or before `t`**. The policy series is **unrevised by
construction**: an administered rate *is* its announcement.

### B.2 The FRED/ALFRED policy-metadata limitation — recorded, not hidden

The S1 data freeze established, from the frozen bytes:

```
DFEDTAR   EVERY observation from 1982-09-27 to 2008-12-15 carries
          realtime_start = 2008-12-15, realtime_end = 9999-12-31.
          ONE interval for twenty-six years - the day the series was DISCONTINUED.
DFEDTARU  earliest realtime_start = 2014-04-03, although the target RANGE (both
          bounds, announced in the same sentence) has been public since 2008-12-16.
DFEDTARL  earliest realtime_start = 2008-12-17.
```

```
CLASSIFICATION = FRED / ALFRED SERIES-METADATA LIMITATION
             NOT historical public unavailability.
```

`realtime_start = 2008-12-15` does **not** mean earlier FOMC targets were unknown before
2008, and `DFEDTARU`'s 2014 stamp does **not** mean the range beginning 2008-12-16 was
unavailable until 2014. These are artefacts of when FRED created or restructured each
series. Reading them as availability would leave the policy leg undefined on **71 of the
218** canonical decision dates and, through the policy coefficient, would make **9 of the
15** mapped instruments undefined across roughly a third of the sample — moving the
Gate-0.5 denominator for a reason that has nothing to do with macro information.

**This limitation was discovered during the S1 freeze, before any feature, position,
separability figure or return existed, and is resolved by the availability authority in
§B.1, which was bound pre-outcome.**

---

## §C Information cutoff and the same-day rule — LOCKED

```
DECISION DATE      = the canonical final trading day of each month, as carried by
                     output/monthly_signal_panel.csv
INFORMATION_CUTOFF = 15:45:00 America/New_York on that day

MACRO_VALUE_AS_OF  = only information with an official availability timestamp
                     <= the cutoff may enter the decision for that month.
```

Compatible with, and strictly more conservative than, the canonical execution
convention: `src/portfolio.py` applies a weight decided at a month-end close only from
the next session onward (`shift(1)`, "no same-bar look-ahead"). 15:45 precedes both the
~16:00 decision close and the next-session execution.

```
NO SAME-PERIOD LOOKAHEAD. A reference month's own date is irrelevant to eligibility;
only its PUBLICATION date and time govern. A January reading published in February is
eligible for a February decision and NOT for a January one.
```

### C.1 ALFRED legs (growth, inflation)

```
eligible vintage at t = the LATEST vintage whose vintage date <= t.
Within that vintage, use the newest reference observation eligible at t.
A vintage dated AFTER t may never be consulted.
Same-day vintage whose release time cannot be authoritatively established
  -> use the PRIOR eligible vintage. Do not guess.
```

### C.2 Policy leg (FOMC announcement)

```
announcement time <= 15:45 ET  -> the newly announced target/range IS eligible at t
announcement time >  15:45 ET  -> the PREVIOUS target/range remains eligible
time not authoritatively establishable -> the PREVIOUS target/range remains eligible
```

**The rule bites on exactly six dates in the window**, and all six are pinned in
`data/mmv/MMV_FOMC_TIMING_MANIFEST.json`:

| decision date | official release time | eligible target |
|---|---|---|
| 2013-07-31 | **not published** — statement reads "For immediate release"; no time on the statement page, the 2013 historical calendar, or the current FOMC calendar | **PREVIOUS** (rule fallback) |
| 2014-04-30 | **not published**, as above | **PREVIOUS** (rule fallback) |
| 2018-01-31 | 2:00 p.m. EST | newly announced |
| 2019-07-31 | 2:00 p.m. EDT | newly announced |
| 2024-01-31 | 2:00 p.m. EST | newly announced |
| 2024-07-31 | 2:00 p.m. EDT | newly announced |

All six resolve **deterministically**. Nothing is guessed. The two fallbacks are the
authority's own silence, recorded as a finding rather than filled in.

---

## §D Series identity and transforms — LOCKED (MMV-OD-2, MMV-OD-6)

```
TRANSFORM (F5 field 1) = 12-MONTH CHANGE, SIGN ONLY.
  NO 3m / 6m / 18m / 24m · NO z-score · NO standardisation · NO magnitude scaling
  NO threshold · NO percentile · NO smoothing family · NO lookback search.
sign(0) = 0 everywhere.
```

### D.1 Growth leg

```
G_t = sign( sign(D12 INDPRO_t) + sign(D12 PAYEMS_t) )

(-1,-1) -> -1     (0,-1) -> -1     (+1,-1) ->  0
(-1, 0) -> -1     (0, 0) ->  0     (+1, 0) -> +1
(-1,+1) ->  0     (0,+1) -> +1     (+1,+1) -> +1
```

One measure, one vote; opposed measures abstain; a silent measure does not veto.

### D.2 Inflation leg

```
RAW SERIES = CPILFENS   (CPI-U, all items less food and energy, NOT seasonally adjusted)
pi12(m)    = CPILFENS(m) / CPILFENS(m-12) - 1
I_t        = sign[ pi12(m) - pi12(m-12) ]

FORBIDDEN as alternative primary: CPIAUCSL · CPILFESL · PCEPILFE. No series family.
```

The **rate**, not the index level: the 12-month change of a core price index *is* `pi12`,
whose sign is `+1` in every month of the window — a static bet, not a momentum signal.

### D.3 Policy leg

```
target(t) = DFEDTAR                       through 2008-12-15
          = midpoint(DFEDTARL, DFEDTARU)  from  2008-12-16 onward
P_t       = sign[ target(t) - target(t - 12 months) ]

FORBIDDEN: FEDFUNDS · DGS2 · any traded yield. DGS2 is PERMANENTLY EXCLUDED.
```

Splice boundary verified mechanically from the frozen bytes: `DFEDTAR` ends 2008-12-15
(9,577 observations), `DFEDTARL`/`DFEDTARU` begin 2008-12-16 (6,484 each) —
**contiguous, no gap, no overlap**.

---

## §E Position construction — LOCKED (MMV-OD-6)

```
raw(i,t) = sign( c_iG * G_t  +  c_iI * I_t  +  c_iP * P_t )        sign(0) = 0
```

Asset-specific votes. **Never a global macro scalar.**

### E.1 The frozen coefficient table — 15 mapped instruments

| instrument | c_G | c_I | c_P | class |
|---|---:|---:|---:|---|
| SPY, EEM, EWJ, XLE, XLU | +1 | 0 | −1 | equity |
| TLT, SHY | −1 | −1 | −1 | duration |
| LQD, HYG | +1 | 0 | 0 | credit |
| USO, UNG, GLD, DBA | 0 | +1 | 0 | commodities |
| UUP | 0 | +1 | +1 | dollar |
| FXY | 0 | −1 | −1 | dollar, orientation −1 |

```
COEFFICIENTS ARE NOT ALTERABLE. NO SECONDARY ASSET LOADINGS.
All coefficients are in {-1, 0, +1}: NEW_TUNABLE_NUMERIC_PARAMETERS = NONE.
Consequences, all verified by enumeration over the 27 (G, I, P) states:
  FXY == -UUP everywhere   ·   XLE == XLU == sign(G - P)
  GLD == I                 ·   LQD == HYG == G        ·   UUP == sign(I + P)
```

### E.2 Real estate

```
VNQ = NOT_MAPPED        RWX = NOT_MAPPED
Primary MMV portfolio weight = 0 ALWAYS.
THEY ARE *NOT* "MMV signal = 0".
Gate 0.5: their cells are UNDEFINED and enter NEITHER numerator NOR denominator.
```

Coding an unmapped instrument as a signal zero would make it disagree with the canonical
composite in every month that composite is non-zero — mechanically, regardless of macro
information — pushing pooled agreement down **in MMV's own favour**. That is an artefact,
and it is excluded by construction.

```
PRIMARY MMV DOMAIN = 15 MAPPED ETFs DRAWN FROM the canonical 17-ETF universe.
The claim may NEVER be stated as "all canonical 17 ETFs".
```

### E.3 Ties, zeros, missing

```
TIE      vote sum = 0  ->  raw = 0.   No priority theme. No carry-forward.
ZERO     a zero macro leg casts NO VOTE - abstention, never a veto.
         All-zero eligible votes -> raw = 0.
MISSING  NEVER converted to zero. If a leg with a NON-ZERO coefficient for instrument
         i is unavailable at t, then raw(i,t) = UNDEFINED.
         Undefined cells: carry NO position · excluded from Gate 0.5 · excluded from
         primary return statistics · MUST BE COUNTED AND REPORTED.
NO IMPUTATION. NO CARRY-FORWARD.
```

**Known missingness, recorded and governed, not repaired.** `CPILFENS` has exactly one
reference date with no value in any frozen vintage: **2025-10-01**. Its cause is **not
asserted** by this contract. It is governed entirely by the rule above: wherever the
inflation leg is unavailable for an instrument-month with a non-zero `c_I`, that cell is
UNDEFINED, counted and reported.

### E.4 Price independence

```
MACRO_SIGNAL_CONSTRUCTIBLE_WITHOUT_PRICE = YES
```

No price of any kind enters the construction of `G`, `I`, `P` or `raw`. Price is used
ONLY for: common portfolio risk scaling, transaction-cost accounting, return evaluation,
and the canonical TSMOM comparison. Forbidden in the alpha signal: trailing returns,
moving averages, yields, curve signals, volatility-conditioned signs, price trend filters.

---

## §F Common risk wrapper — INFRASTRUCTURE, NOT ALPHA

Adopted unchanged from the canonical implementation. **Canonical TSMOM itself is a frozen
research benchmark and is not modified by this lineage in any way.**

```
asset volatility estimator   60 trading days        config.py:168 VOL_WINDOW_DAYS
asset vol target             10 %                   config.py:169 TARGET_VOL_ANNUAL
asset position cap           +/- 2                  config.py:170 MAX_ASSET_WEIGHT
live assets                  EQUAL WEIGHT           config.py:176
portfolio vol target         10 %                   config.py:182 PORT_TARGET_VOL_ANNUAL
gross leverage cap           3x                     config.py:184 MAX_GROSS_LEVERAGE
```

```
SIGNAL_FREQUENCY = MONTHLY     REBALANCE_FREQUENCY = MONTHLY
No holding-period family. No rebalance-frequency search. Daily trading is never
forced onto monthly information.
```

## §G Cost — LOCKED (MMV-OD-5)

```
ONE_WAY_COST   = 2 bps of turnover
COST_AUTHORITY = config.py:196 TRANSACTION_COST_BPS = 2.0, "one-way cost per unit
                 turnover (liquid-ETF convention)"
```

Adopted because the execution mechanics are identical — same universe, same monthly
frequency, same wrapper, same decide-at-close / execute-next-session lag. No cost number
was chosen from any return.

---

## §H Sample — STRUCTURAL START RULE, fixed before any feature

```
STRUCTURAL_START_RULE — a decision date t is ELIGIBLE iff ALL hold:
  1. t is a canonical month-end in output/monthly_signal_panel.csv
  2. an eligible vintage exists at t for each ALFRED leg (§C.1)
  3. that vintage contains enough reference months for the sealed transform:
       growth    >= 13 monthly observations
       inflation >= 25 monthly observations
  4. an announced policy target exists at or before t (§C.2)
  5. canonical ETF price data exist at t
Dates failing any condition are EXCLUDED, COUNTED and REPORTED - never imputed.
```

```
EXPECTED WINDOW = 2008-05-31 .. 2026-06-30, 218 canonical decision dates.
The exact eligible set is DERIVED MECHANICALLY at S2 by the rule above.
NO start date may be chosen on performance. The window may NOT be extended past the
authoritative canonical price panel merely because newer macro vintages exist.
```

---

## §I Gates — SEALED, ORDERED

### I.1 Gate 0 — data / PIT feasibility

Passes iff the frozen inputs support §B and §C with no final-revised substitution. A
failure is **CLASS A**, and no return run occurs.

### I.2 Gate 0.5 — position-level separability (PnL-FREE, and it can KILL)

```
ELIGIBLE_GATE_05_CELL(i,t) iff
    i is one of the 15 mapped instruments
    AND MMV_sign(i,t) is defined
    AND canonical_TSMOM_sign(i,t) is defined

POOLED_EXACT_SIGN_AGREEMENT
    = count( MMV_sign(i,t) == TSMOM_sign(i,t) ) / count( ELIGIBLE_GATE_05_CELL )

Signs are from {-1, 0, +1}. ZERO IS A REAL POSITION STATE:
    0 vs 0       = AGREEMENT
    0 vs +1/-1   = DISAGREEMENT
Zeros are NEVER discarded and the metric is NEVER conditioned on active months only.
VNQ / RWX NEVER enter numerator or denominator.

KILL iff POOLED_EXACT_SIGN_AGREEMENT >= 80.0 %, INCLUSIVE.
    79.999...%  -> Gate 0.5 PASSES
    80.000...%  -> CLASS B
```

On a kill: **STOP before any return evaluation.** `PROGRAMME_STATUS = NOT_PROMOTED`,
`FAILURE_TYPE = NOT_SEPARABLE_AT_POSITION_LEVEL`. Per-instrument agreement rates are
**diagnostic only**: they can neither rescue a pooled failure nor kill a pooled pass.

A kill does **not** mean macro information is false, that the mechanism is falsified, or
that TSMOM causes the macro state.

### I.3 Gate 1 — predictive response

```
PRIMARY RETURN OBJECT = GROSS monthly MMV portfolio return, before transaction cost,
                        from the sealed raw directions through the common wrapper.
GATE1 PASSES iff the LOWER endpoint of the predeclared 95 % interval > 0, STRICT.
A point estimate alone never passes.
NO per-ETF, per-sleeve, inflation-only, growth-only or policy-only promotion exists.
```

### I.4 Gate 2 — economic usefulness

```
NET MONTHLY RETURN = gross portfolio return - sealed turnover cost (§G)

M1  lower 95 % bound of mean NET monthly return  > 0        STRICT
M2  lower 95 % bound of calendarised annualised NET Sharpe  > +0.30   STRICT
    Sharpe = mean(monthly net) / sd(monthly net, ddof=1) * sqrt(12), rf = 0
```

```
M2 IS AN MMV-SPECIFIC OWNER DECISION (MMV-OD-3). It is NOT inherited from C-A,
CTA-EDGE-01-TA or CTA-EDGE-02-BENB, and its numerical coincidence with BENB's +0.30
creates no precedent in either direction.
```

---

## §J Inference — ONE framework

```
METHOD   calendar-year block bootstrap. Resample COMPLETE calendar years of the full
         monthly cross-asset state/return panel, preserving cross-sectional dependence.
B        10,000            INTERVALS  95 % percentile
ONE COMMON SET OF YEAR DRAWS serves Gate-1 gross mean, M1 net mean and M2 net Sharpe.

The PIT macro signal is computed ONCE, causally, on the true chronology. The bootstrap
operates on FROZEN monthly strategy tuples. Fictional ALFRED histories are NEVER
rebuilt after year resampling.

FORBIDDEN: HAC · Newey-West · a second bootstrap · monthly IID bootstrap.
RNG SEED is not chosen until a future S3 authorization.
```

```
NO ADDITIONAL FRAGILITY MENU. No LOYO. Gate 0.5 is the pre-PnL falsification and the
programme validates fragile pieces, not everything.
```

---

## §K Classification — SEALED, FIRST MATCH WINS

```
CLASS A   DATA / PIT FAILURE
          vintage reconstruction, release timing, series identity, mapping or
          execution footing invalid. No edge verdict.

CLASS B   NOT SEPARABLE AT POSITION LEVEL
          Gate 0.5 pooled exact sign agreement >= 80.0 %.
          STOP before return exposure. PROGRAMME_STATUS = NOT_PROMOTED.
          The mechanism is NOT falsified.

CLASS C   PREDICTIVE RESPONSE RELIABLY ABSENT / ADVERSE
          Gate 0.5 passes and the Gate-1 UPPER 95 % endpoint <= 0.
          PROGRAMME_STATUS = NOT_PROMOTED.

CLASS D   PREDICTIVE RESPONSE UNRESOLVED
          Gate 0.5 passes and the Gate-1 interval spans 0.
          PROGRAMME_STATUS = UNRESOLVED / LOW_POWER. Terminal. No retuning.

CLASS E   PRESENT BUT ECONOMIC TARGET EXCLUDED
          Gate 1 passes and EITHER the upper 95 % endpoint of mean NET return <= 0
          OR the upper 95 % endpoint of NET Sharpe <= +0.30.
          PROGRAMME_STATUS = NOT_PROMOTED. FAILURE_TYPE = TARGET_MARGIN_EXCLUDED.

CLASS F   ECONOMIC USEFULNESS UNRESOLVED
          Gate 1 passes; M1 and/or M2 intervals span their boundaries without
          reliably excluding them. UNRESOLVED / LOW_POWER. Terminal.

CLASS S   SUPPORTED MMV EDGE - ALL of:
          1. Gate 0 / PIT valid
          2. pooled TSMOM sign agreement < 80.0 %
          3. gross mean lower 95 % endpoint > 0
          4. net mean lower 95 % endpoint > 0
          5. net Sharpe lower 95 % endpoint > +0.30
          6. no scientific or data failure
```

```
EVIDENCE_CEILING = supported.  NEVER confirmed. NEVER independently confirmed.
```

---

## §L Diagnostics — NONE MAY PROMOTE OR RESCUE

```
PERMITTED: growth-leg direction · inflation-leg direction · policy-leg direction ·
           per-instrument MMV sign · per-instrument TSMOM agreement · first-release
           concordance · turnover · component contribution · undefined-cell counts

ALL carry PROMOTION_POWER = NONE and RESCUE_POWER = NONE.
No component may rescue the composite. There is no post-hoc
"growth works even though MMV failed".
```

### L.1 The first-release concordance cell

Built after this seal and before any return exposure, using ALFRED `output_type = 4`
(initial release only), with **identical** series identity, transform, asset mapping and
monthly dates. Reports only: pooled sign disagreement percentage, disagreement by macro
leg, by instrument, and calendar clustering.

```
NO threshold · NO pass/fail · NO promotion · NO rescue · NO kill · NO return data.
Purpose is interpretation only. Large disagreement -> report that the primary result is
specifically a LATEST-KNOWN macro-state result. Small disagreement -> report that
revision handling is empirically less consequential. NO CLAIM BROADENING EITHER WAY.
```

Under the §D series identities the revision channel is confined to the **growth leg**:
`CPILFENS` is final when issued and the FOMC target is administered and never revised.

---

## §M Multiplicity, sample reuse, exposure — LOCKED

```
PRIMARY TRIAL FAMILY = CTA-EDGE-04-MMV composite,  m = 1
No additional horizons, no threshold family, no second primary.

ETF PRICE SAMPLE = REUSED / BURNED, context T0 (SAMPLE_REUSE.md KB-1, burned 6 of 6,
                   must_not_be_retested_on_same_sample, D-ETF-COUNT open)
MACRO VINTAGE LEG = NEW historical information source, no prior programme exposure
COMBINED          = DEPENDENT / MIXED PROVENANCE. A new macro leg does NOT launder the
                    reused ETF price sample.
EVIDENCE_CEILING  = supported
N_trials          = NOT ASSERTED. D-ETF-COUNT remains UNKNOWN_PENDING_AARON_DECISION
                    and is NOT decided here.
```

```
FABLE_DESIGN_EXPOSED = YES - originated F5, advised MMV-OD-1 and MMV-OD-6. Barred from
  blind certification of this design, implementation or result. Adopting its advice
  does not restore independence.
ASTRA_DESIGN_EXPOSED = NO - meaning NO RECORDED CONTRIBUTION to MMV. Astra's Round-1
  map is not persisted in this workspace, so this is an inference from absence, not a
  positive attestation. It must not be represented as stronger than that.
```

---

## §N Forbidden post-result actions — BINDING

A failed or unresolved result does **NOT** authorise:

```
changing the 12m lookback · headline CPI · core PCE · effective fed funds · the 2Y
yield · changing growth inputs · changing composite weights · changing the asset
mapping · changing the 80.0 % threshold · dropping zero positions · changing the risk
wrapper · lowering costs · lowering +0.30 · adding trend filters · adding carry · using
final-revised macro data · swapping the latest-known primary for first-release ·
selecting only the macro legs that worked
```

**Any such study is a NEW LINEAGE** with its own S0, seal, trial accounting and Owner
authorisations.

---

## §O Forbidden interpretations — BINDING ON EVERY LATER DOCUMENT AND SEAT

```
THIS IS NOT A CRISIS DIVERSIFIER and must never be described as one.
```

F5's own field 11 predicts the opposite: in 2020-03 every growth-momentum reading was
still positive when prices crashed, so the sleeve would have been long risk into the
crash and would have co-lost with the core's static long component. Any tail claim must
be reported on **declared windows** and never asserted from an unconditional correlation.

A **supported** result would NOT establish: that macro data *cause* asset returns; that
the canonical book should be gated, de-grossed or overlaid; that macro momentum works in
other universes, horizons or instruments; that the published statistics are *accurate*
(the study uses what was **published**, which is the investor's information set, not the
truth); or any improvement to canonical TSMOM.

A **negative** result would NOT establish: that macroeconomic information is irrelevant
to asset prices; that Brooks (2017) or Dahlquist & Hasseltoft (2020) are wrong — neither
uses this construction, universe or sample, and MMV is **not** a replication of either;
or that a different information concept, series family, mapping or horizon would fail.

---

## §P Pinned inputs

```
RAW MACRO DATA      data/mmv/  (git-ignored), hashes pinned in MMV_RAW_DATA_MANIFEST.md
RAW MANIFEST        data/mmv/MMV_RAW_MANIFEST.json
FOMC TIMING         data/mmv/MMV_FOMC_TIMING_MANIFEST.json + data/mmv/fomc/*.html
CANONICAL PRICES    data/close_prices_raw.csv (frozen ETF panel, 1993-01-29..2026-06-12)
CANONICAL SIGNALS   output/monthly_signal_panel.csv (17 x 402, 1993-01-31..2026-06-30)
CANONICAL PARAMS    config.py
FOMC CALENDAR       research/extensions/ta/TA_MACRO_CALENDAR.csv (FRB_HISTORICAL,
                    FRB_CALENDARS) - reused, not refetched
```

Exact sha256 values for every pinned artifact are carried in
[`MMV_SEAL_MANIFEST.md`](MMV_SEAL_MANIFEST.md).
