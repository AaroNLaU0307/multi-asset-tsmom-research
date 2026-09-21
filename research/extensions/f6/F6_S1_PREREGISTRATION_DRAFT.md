# CTA-EDGE-05 / F6 — MACRO_ANNOUNCEMENT_PREMIUM · S1 PREREGISTRATION (DRAFT)

```
SEAL_STATUS            = DRAFT / OWNER_APPROVAL_REQUIRED
SEALED                 = NO
DATE                   = 2026-09-21
LINEAGE                = CTA-EDGE-05 / F6 MACRO_ANNOUNCEMENT_PREMIUM
DESIGN_STATUS          = CLOSED TO REDESIGN
F6_RETURN_OUTCOME_ACCESSED = NO
```

> **This document is not a seal.** It is the serialization of an already-closed
> design, plus the mechanical evidence that the design is constructible. Aaron
> alone performs the irreversible seal action. Nothing here authorizes a run, a
> backtest, a reveal, or a trial.

---

## §0 What closed the design

The final fresh independent re-adjudication —
[`../review_history/F6_FINAL_INDEPENDENT_REVIEW_2026-09-21_ASTRA_01.md`](../review_history/F6_FINAL_INDEPENDENT_REVIEW_2026-09-21_ASTRA_01.md),
sha256 `23f723ed100ca71e11bc8b99f03a2ddf86988b0654ebb7b66e1537daf23ab589` —
returned:

```
F6_FINAL_INDEPENDENT_REVIEW_STATUS = PASS
FINAL_CLASS = B_READY_FOR_S1_SEAL_WITH_CLAIM_CAP_NARROWING
S1_SEAL_AUTHORIZED_BY_THIS_REVIEW  = NO
CONFIDENCE = MEDIUM
```

```
FINAL_INDEPENDENT_REVIEW_IMPORTED = YES
```

The exact bytes were copied into the repository and re-hashed; the copy is
byte-identical to the source. It was not rewritten, normalized or regenerated.
**This new review is the active pre-S1 independent review authority.**

### §0.1 The older missing artifact is NOT recovered

```
HISTORICAL_PROVENANCE_RESERVATION = YES   (NONBLOCKING)
```

The pre-S0 independent adjudication was never persisted. The file
[`F6_INDEPENDENT_ADJUDICATION_CONTROLLER_TRANSCRIPT.md`](F6_INDEPENDENT_ADJUDICATION_CONTROLLER_TRANSCRIPT.md)
remains a **controller-supplied reconstruction carrying no original hash**. It
is not independent evidence, it is not a certification, and **nothing in this
document pretends it was recovered**. The reservation is now explicitly
non-blocking because a *new* independent review exists — that is new authority,
not retrospective certification of the old one.

---

## §1 Authority — every pin independently re-verified

All hashes below were recomputed in this session and **each one reproduces the
value the independent reviewer recorded**.

| authority | sha256 |
|---|---|
| Round-1 F6 map (fields 1–15) | `02ca5f45fe41763e55a353090645c3b2a98b6dcf5fce572623ede604e569344a` |
| Owner decision record (F6) | `0912398432ee730fdea7ee6b48137c0633e5e631a51685ce5f614d8209e0917f` |
| OD-1 (1a–1h) | `0066584e7c4267926a6977eb0159a5b978057865baafc00df31f6ed62abcac10` |
| OD-2 (2a–2h) | `4adaadc8f5be6ce0bc2a928cf1d68ffad296ff8ec2b146a50af9248a9e6b34b1` |
| OD-TY / OD-CASH (filed as od-3a-3b) | `bf1642efd43ccdabbe95a8ba3f6b0bced808932c2c7c2934482c4eb2d3832a23` |
| `F6_METADATA_AUDIT_RULE.md` (frozen) | `5063fe3b35deb09674cbb32078744822c2db403959317996c18f93aade32be11` |
| `F6_EVENT_SCHEDULE_PIT_REPORT.md` | `5a516516bc4bcbad1b25219ba0b3d5386fe7559858b941f4eecb2a879788e506` |
| `F6_S0_REPAIR_RECORD.md` | `feebb831d42a7f7a51012b43fd03104e62f7482d5ee329f99d4bc258d3330b96` |
| `F6_S0_COMPLETION_RECORD.md` | `40a84ed9ac4dd749be19fa9d5d376053b6b1e25536aa31816863376b9dd39003` |
| **`F6_FINAL_EVENT_MANIFEST.json`** | **`49ff27bfc20eb98265c440bac7368e92022b356d77647dce9151f012e40ed382`** |
| `F6_SCHEDULE_PIT_FINAL_GATE.md` | `de24eec7bd4f2be15181d93611e7e4e17305027c23cffb8e6c2c72230f769b2d` |
| **final Astra review** | **`23f723ed100ca71e11bc8b99f03a2ddf86988b0654ebb7b66e1537daf23ab589`** |
| `SAMPLE_REUSE.md` | `5c3b11372fcf44e8e820866e182008f4c56d91afc564897206869f28e4be0218` |
| `TRIAL_LEDGER.md` | `711d4ab41eac6ef53985b260835b186e7fd95eea0a452ba8f05ab99e08b2d0e2` |
| `EXPOSURE_LEDGER.md` | `ed3c5bf93a8c768b30237b9772f6c2e8ddec2c9bd9ea199992352c486ae72730` |
| `TA_PREREGISTRATION.md` (auction authority) | `3b495fcb220a86b9c4226e308e4814bdfdd871d1c69ce352e99b78977436d35b` |
| `TA_EVENT_CALENDAR.csv` | `b27be5b1d94cfc13fc8310e0d5216675e097a2245fc954e4b12ed282563f7cb6` |
| seasonality `PREREGISTRATION.md` (TOM authority) | `d6f1909bd57b5c6fb1876613a9141a1d5203b66fdd64068dba5ee8908f33f7f1` |
| `src/seasonality.py` (sealed TOM implementation) | `43a75588b95f6ec42b090bc6b02fa2edc761f4fc82525288a544195ebab2a806` |
| `data/close_prices_raw.csv` (frozen SPY panel) | `3d2a7a56dbd92d4ff8138cfd894c87f5ac5ac088a11165db870673e0c05c3c31` |
| `data/DGS3MO.csv` (cash proxy source) | `50da2bfbb25e3e3241af7a4ad16e5a1bb5f08cdfb46bcb92f224954dce054319` |

**The latest Owner decisions and the final event manifest supersede stale
intermediate counts.** No historical authority was rewritten: superseded
documents keep their bytes and carry additive notes.

---

## §2 Final claim identity

```
LINEAGE            = CTA-EDGE-05 / F6 MACRO_ANNOUNCEMENT_PREMIUM
SCIENTIFIC OBJECT  = historical pooled scheduled-macro-announcement-day edge
                     in SPY
PROMOTION INSTRUMENT = SPY ONLY
TLT                = STRUCK ENTIRELY FROM CTA-EDGE-05 OUTCOME COMPUTATION
F6.b PRE-FOMC DRIFT= SEPARATE FUTURE LINEAGE. NOT COMPUTED.
F6.c ERA SPLIT     = DESCRIPTIVE ONLY. NO PROMOTION. NO RESCUE.
GLOBAL POOLING     = MATERIAL PRE-OUTCOME DESIGN COMPLETION,
                     NOT ORIGINAL PROMOTION AUTHORITY
```

Pooling is **material**. The original Round-1 pooled *kill* language does not by
itself authorize this pooled *promotion* architecture; **Owner adoption supplies
that authority**, pre-outcome. This is recorded as a completion of F6.a, not as
a new hypothesis and not as inherited permission.

---

## §3 Event universe

Primary families: **scheduled FOMC policy-statement releases · CPI · Employment
Situation (NFP)**.

```
FINAL PRIMARY YEARS = 2011 .. 2025 inclusive
2026                = NO F6 OUTCOME QUANTITY MAY BE FORMED
```

```
FINAL_PRIMARY_EVENT_COUNT = 462 unique event sessions
  FOMC 119 · CPI 176 · NFP 176  =  471 family labels
  9 multi-event overlaps
  471 - 9 = 462
```

**These counts were regenerated mechanically from the manifest at
`49ff27bf…ed382` and reconcile exactly. They were not transcribed.** The
manifest hash, not this table, is authoritative; if a future reader cannot
reproduce these numbers from that hash, the correct action is to STOP, never to
edit the manifest into agreement.

### §3.1 Same-day multiple families

```
ONE trade · ONE unit · ONE return · ONE primary observation.
Diagnostic labels may be multiple. NO DOUBLE NOTIONAL.
```

A session carrying two eligible families is a single position and a single P1
observation. The nine overlap sessions are exactly the difference between 471
labels and 462 observations.

### §3.2 The six PIT exclusions are permanent

Six historically changed BLS releases, excluded pre-outcome by the accepted
`SCHEDULE_PIT_FAIL_CLOSED` rule, **remain excluded**:

```
NFP 2013-10-22 · CPI 2013-10-30 (label only) · CPI 2013-11-20
NFP 2025-11-20 · NFP 2025-12-16 · CPI 2025-12-18

NO POST-SEAL REINSTATEMENT. NO REINSTATEMENT AFTER OUTCOMES.
```

`2013-10-30` survives as an **FOMC-only** session, because that FOMC statement
was independently scheduled and knowable. Verified mechanically at pre-seal.

### §3.3 What the target population actually is

The estimand covers the **archive-verifiable eligible subset**, not every
announcement a contemporary investor might in fact have known about. Missing
schedule evidence clusters around shutdown disruption. **The sign of the
resulting external-validity difference is unknown**, and fail-closed exclusion
is not evidence of a downward performance bias in either direction.

---

## §4 The trade

```
POSITION  long 1 unit notional SPY on every eligible event session
ENTRY     prior eligible trading-session close
EXIT      eligible event-session close
OTHERWISE flat
LEVERAGE  none
```

No input from: **consensus · actual macro print · surprise · post-release
reaction · NQ signal · TLT signal.** The rule reads only the event calendar and
the date index.

### §4.1 Price representation — an execution proxy, stated as one

```
frozen single-vendor adjusted-close SPY panel
data/close_prices_raw.csv  sha256 3d2a7a56…c31

THIS IS AN EXECUTION PROXY.
IT IS NOT PRODUCTION-GRADE FILL EVIDENCE.
```

Single-vendor adjustment, dividend treatment, market-on-close implementation,
order deadlines and slippage all remain un-modelled. The 4 bps assumption in §7
is an assumption, not a measured realized cost.

---

## §5 Opening 2011 control row — the all-session rule

```
P2 POPULATION = EVERY TRADING SESSION IN CALENDAR YEARS 2011-2025.
NO ROW IS DROPPED.
```

The independent review flagged a discrepancy: the S0 metadata gate reported
dropping its first 2011 row because `HOLD` was undefined at the panel edge,
whereas OD-TY and the adopted design say *every* 2011–2025 session. **The
adopted all-session rule governs.** A metadata-precheck truncation must never be
silently promoted into a sample rule.

For the first 2011 trading session, the lagged close, the interval boundary and
`HOLD` are constructed from the **immediately preceding panel trading session**:

```
first primary session   2011-01-03
lag boundary session    2010-12-31

THE 2010 SESSION IS AN INPUT BOUNDARY OBSERVATION.
IT IS NOT A 2010 REGRESSION ROW. IT IS NEVER AN EVENT. IT IS NEVER
A BOOTSTRAP BLOCK MEMBER.
```

The same principle governs the cash-proxy mapping: the benchmark date for the
first 2011 session is `2010-12-31`, and that maps to an official DGS3MO
observation with no unexplained gap.

Proved mechanically at pre-seal, metadata only:

```
P2 rows                                   3772
rows dropped for undefined HOLD              0
HOLD defined and strictly positive on every row   PASS  (min 1, max 5)
first 2011 row present in the design      PASS
boundary session exists and carries a non-null SPY entry   PASS
                                          (PRESENCE check only; no value read)
EVENT column sums to 462                  PASS
```

```
OPENING_2011_ROW_RULE_VALIDATED = YES
```

---

## §6 Cash proxy — DGS3MO

```
ROLE = OWNER-CHOSEN EX-POST CASH OPPORTUNITY-COST PROXY

NOT a signal. NOT an eligibility input. NOT a position input.
NOT a sizing input.
```

Because it never touches eligibility, direction, size or execution, its
publication after the entry close introduces **no trading-signal look-ahead**
under this role.

### §6.1 Convention

```
rf_hold(d) = ( DGS3MO mapped annual percent / 100 ) * HOLD_calendar_days(d) / 365
```

```
THE /365 CONVENTION IS OWNER-CHOSEN.
IT MUST NEVER BE ATTRIBUTED TO TREASURY, H.15 OR FRED.
```

The source chain (FRED → H.15 → Treasury methodology) terminates without
specifying a day count. This is also **not** an observed overnight cash-account
return and **not** a guaranteed reinvestment rate. It can affect both P1 and P2
and can matter near a zero boundary; the earlier advisory claim that `HOLD` and
the intercept necessarily absorb the cash term is **false in general** and is
not relied on. That overstatement confers no authority to switch the proxy after
results.

### §6.2 Mapping

```
Use the last official observation dated ON OR BEFORE the required benchmark
date, carrying forward ONLY where the missing dates are explained by the
official source's own non-publication calendar (weekend, holiday, or a row the
source file itself carries as missing).

NO ARBITRARY 7-DAY RULE. There is no authority for one.
```

```
UNEXPLAINED SOURCE GAP  ->  IMPLEMENTATION HOLD.
DO NOT SUBSTITUTE ANOTHER CASH SERIES. DO NOT WIDEN THE CARRY.
```

Verified mechanically at pre-seal over all 3772 sessions including the 2011
opening boundary:

```
sessions requiring rf_hold        3772
mapped to an official observation 3772
carry distribution (calendar days){0: 3744, 1: 8, 3: 20}
max carry                         3
UNEXPLAINED GAPS                  0
DGS3MO_MAPPING_PASS = YES
```

---

## §7 Return objects

```
R(d)        = AdjClose(d) / AdjClose(prev(d)) - 1
r_excess(d) = R(d) - rf_hold(d)
r_net(t)    = r_excess(t) - 0.0004
```

```
0.0004 = 2 bps entry + 2 bps exit (round trip).
```

```
P1 TARGET = the EVENT-WEIGHTED ARITHMETIC MEAN of r_net over the 462 eligible
            event sessions.

P2 DEPENDENT VARIABLE = r_excess(d) over ALL 2011-2025 trading sessions.
```

```
P2 IS GROSS OF EVENT TRANSACTION COST.
DO NOT SUBTRACT A HYPOTHETICAL STRATEGY COST FROM CONTROL SESSIONS.
```

Charging the round-trip cost in P1 only is deliberate and is not an
inconsistency: P1 asks whether the *declared trade* clears cash plus cost; P2
asks whether *asset returns* carry a positive EVENT coefficient. They are
different necessary properties.

**No value of `R`, `r_excess` or `r_net` has been computed.** The panel has been
opened for its date index and column presence only.

---

## §8 The fixed P2 model — the only allowed specification

```
r_excess(d) = a
            + beta_EVENT * EVENT(d)
            + weekday dummies
            + TOM(d)
            + HOLD(d)
            + AUCTION(d)
            + error(d)
```

Reused **exactly**, not re-derived:

```
TOM      src/seasonality.py::is_tom (sealed), last = SEAS_TOM_LAST,
         first = SEAS_TOM_FIRST, as pinned in config
AUCTION  TA_EVENT_CALENDAR.csv, tenor_family in {10-Year, 30-Year} nominal
         coupon auctions, mapped to the first panel session at or after the
         auction date
```

```
FORBIDDEN, WITH NO EXCEPTION:
  interactions · matched-control alternative · alternate regression ·
  variable selection · fallback model · post-result model repair
```

### §8.1 Pinned column set and baseline

The design matrix is exactly these nine columns, in this order, with the
weekday baseline pinned so no library default can drift it:

```
const · weekday_Monday · weekday_Thursday · weekday_Tuesday ·
weekday_Wednesday · EVENT · TOM · HOLD · AUCTION

WEEKDAY_BASELINE = Friday   (the alphabetical drop_first level; pinned
                             explicitly so it cannot silently change)
```

Verified at pre-seal:

```
shape (3772, 9)   rank 9   FULL COLUMN RANK
EVENT is NOT in the span of the controls    -> separately identified
no required column is constant
no TLT / IEF / NQ / F6.b / surprise / consensus / actual field present
```

### §8.2 What P2 is, and is not

```
P2 IS A CONDITIONAL LINEAR ASSOCIATION.
IT IS NOT CAUSAL IDENTIFICATION AND NOT EXACT MATCHING.

DO NOT CALL THE CONTROL CONSERVATIVE.
```

Other macro announcements and pre-FOMC sessions remain in the comparison set,
and unexplained calendar structure may remain. A positive `beta_EVENT` does not
establish cost-adjusted superiority over any alternative strategy, and P1 and P2
jointly do **not** prove dominance over buy-and-hold.

### §8.3 A descriptive property of the fixed design, recorded not remedied

Event sessions are concentrated on Wednesday (157) and Friday (198), with only 6
Mondays. `beta_EVENT` is therefore identified largely off Wednesday and Friday
sessions relative to the Friday baseline. This is a **property of the frozen
event calendar**, recorded here for honest interpretation. It creates no rank
problem (verified above), and it authorizes **no** reweighting, no alternative
baseline, and no additional model.

---

## §9 P1 / P2 / P3 promotion gates

```
P1 HARVESTABLE
   lower endpoint of the declared NOMINAL 95% calendar-year percentile-bootstrap
   interval for mean r_net  >  0

P2 SPECIFIC
   lower endpoint of the declared NOMINAL 95% calendar-year percentile-bootstrap
   interval for beta_EVENT  >  0

P3 YEAR FRAGILITY  —  EVALUATED ONLY IF P1 AND P2 BOTH PASS
   delete one complete calendar year at a time;
   refit the IDENTICAL objects;
   EVERY resulting P1 point estimate AND every P2 beta_EVENT point estimate
   must remain STRICTLY > 0.
   NO deletion-specific significance requirement.
```

```
P3 FAILURE  ->  ONE_YEAR_FRAGILITY / NOT_PROMOTED.
                NOT MECHANISM FALSIFICATION.
```

P3 can only **veto** an otherwise-passing pair. It cannot rescue, cannot
reweight, and opens no optimization path. Requiring the conjunction is one
promotion decision, not a choice of whichever test passes — and it equally
cannot repair a miscalibrated constituent interval or historical sample
selection.

---

## §10 Exact bootstrap serialization — frozen now, pre-outcome

```
BLOCKS = 15 calendar years, 2011 .. 2025. Verified contiguous and complete.
```

Each replication, with the **same year-resampling draw used for P1 and P2**:

```
1. draw 15 calendar-year labels WITH REPLACEMENT from {2011..2025};
2. concatenate the corresponding COMPLETE year blocks, duplicating a year's
   rows whenever that year was drawn more than once;
3. compute the EVENT-WEIGHTED P1 mean on the replicated event rows;
4. refit the EXACT fixed P2 OLS of §8 on the replicated daily rows;
5. retain the P1 mean and beta_EVENT.
```

```
TARGET ESTIMANDS REMAIN EVENT-WEIGHTED / SESSION-WEIGHTED.
THEY ARE NOT EQUALLY WEIGHTED ANNUAL MEANS.
```

### §10.1 Per-year rank — why a degenerate draw stays estimable

A draw may contain one year repeated up to 15 times. Estimability was therefore
proved **per individual year**, metadata only, on the pooled column set of §8.1:

| year | rows | events | rank | | year | rows | events | rank |
|---|---|---|---|---|---|---|---|---|
| 2011 | 252 | 32 | 9/9 | | 2019 | 252 | 31 | 9/9 |
| 2012 | 250 | 32 | 9/9 | | 2020 | 253 | 30 | 9/9 |
| 2013 | 252 | 29 | 9/9 | | 2021 | 252 | 32 | 9/9 |
| 2014 | 252 | 30 | 9/9 | | 2022 | 251 | 32 | 9/9 |
| 2015 | 252 | 32 | 9/9 | | 2023 | 250 | 32 | 9/9 |
| 2016 | 252 | 31 | 9/9 | | 2024 | 252 | 31 | 9/9 |
| 2017 | 251 | 29 | 9/9 | | 2025 | 250 | 27 | 9/9 |
| 2018 | 251 | 32 | 9/9 | | | | | |

```
INDIVIDUAL_YEAR_MATRIX_RANK_PASS = YES
BOOTSTRAP_RANK_OWNER_REVIEW_REQUIRED = NO
```

Every individual block is full column rank, so **any** draw — including one
repeating a single year fifteen times — remains estimable under the fixed model.
Had any year been deficient, the declared behaviour was to STOP and return
`BOOTSTRAP_RANK_OWNER_REVIEW_REQUIRED = YES`; **no fallback was invented, and
none exists.**

### §10.2 Replication count

```
B = 100000
```

This is a **pre-outcome numerical-precision convention**. More draws improve
numerical resolution of the interval endpoints. They add **no historical
information** and do not improve coverage.

### §10.3 RNG — deterministic, derived pre-outcome

```
SOURCE STRING
CTA-EDGE-05|F6|S1_BOOTSTRAP|49ff27bfc20eb98265c440bac7368e92022b356d77647dce9151f012e40ed382

SHA256 OF THAT STRING
97704c2ecdc530a56386c0a6b1a878bdf3083ad992011d6b946fd2a3bedcb180

FIRST 8 HEX CHARACTERS        97704c2e
SEED LITERAL (unsigned 32-bit) 2540719150
```

Both the source string and the literal integer are persisted, here and in the
pre-seal manifest. **The seed is derived from the final event manifest hash —
metadata — and never from returns or from any post-result artifact.**

> **Supersession, stated rather than hidden.** OD-2 contemplated deriving the
> seed from the *seal* manifest, and the independent review noted OD-2 leaves
> the bootstrap count to S1. The current Owner instruction derives the seed from
> `FINAL_EVENT_MANIFEST_SHA256` instead. That is an explicit Owner decision and
> takes precedence; it is recorded here so no future reader mistakes it for
> drift. The seed is fully determined **before** the seal and before any
> outcome, which is the property that matters.

### §10.4 Interval

```
NOMINAL TWO-SIDED 95% PERCENTILE-BOOTSTRAP INTERVAL

LOWER ENDPOINT  empirical 2.5th percentile
UPPER ENDPOINT  empirical 97.5th percentile

QUANTILE IMPLEMENTATION  numpy.percentile(..., method="linear")
  numpy  2.5.0
  pandas 2.3.3
  python 3.13.14
```

One quantile implementation, recorded exactly, with an explicit `method=`.
**Software-default drift is not permitted**: if a future environment cannot
supply `numpy 2.5.0` with `method="linear"`, that is an implementation hold for
Aaron, not a licence to take whatever the default gives.

```
P1 AND P2 PROMOTION USE ONLY THE LOWER ENDPOINT.
```

S1 and S4 wording must say **nominal 95% percentile-bootstrap interval**, never
"exact 95% coverage".

### §10.5 Exceptional-case behaviour, frozen before outcomes

The independent review asked that exceptional-case behaviour be fixed
pre-outcome with no fallback model. It is:

```
rank-deficient bootstrap draw     CANNOT ARISE (§10.1 proves every block is
                                  full rank). If one nonetheless arises:
                                  STOP, report, do NOT drop a column, do NOT
                                  ridge, do NOT redraw.
missing price on a required date  STOP. Do not interpolate, do not skip the
                                  session, do not shift the window.
unexplained DGS3MO gap            IMPLEMENTATION HOLD (§6.2). Do not substitute
                                  a cash series and do not widen the carry.
non-finite P1 or beta_EVENT       STOP and report. Never silently dropped from
                                  the replication set.
```

```
NO FALLBACK MODEL EXISTS. NO RETRY-WITH-DIFFERENT-SETTINGS EXISTS.
EVERY EXCEPTIONAL CASE TERMINATES IN A STOP OR AN OWNER DECISION.
```

---

## §11 Bootstrap / inference claim limitation

```
FIFTEEN YEAR BLOCKS IMPLY APPROXIMATE, ASSUMPTION-DEPENDENT INFERENCE.

A LARGE EVENT COUNT DOES NOT CREATE ADDITIONAL INDEPENDENT YEAR CLUSTERS.
462 events do not substitute for more than 15 clusters.
```

```
THE BOOTSTRAP DOES NOT ESTABLISH:
  finite-sample calibrated 95% coverage
  cross-regime replication
  future persistence

LOYO DOES NOT VALIDATE BOOTSTRAP COVERAGE.
LOYO DOES NOT ESTABLISH STABLE MAGNITUDES.
```

Complete calendar years are not made independent or exchangeable merely by being
complete. Material multi-year dependence, regime shifts, leverage or tail
concentration can compromise the approximation. Cluster asymptotics depend on
the number of clusters, and the literature supplies no universal safe cutoff. No
alternative block scheme is compared, and no power or precision is estimated
from returns.

---

## §12 Terminal classification — exhaustive, fixed

| P1 | P2 | terminal classification |
|---|---|---|
| harvestable | specific | **P3 pass → `SUPPORTED_HISTORICAL_EDGE`** · **P3 fail → `ONE_YEAR_FRAGILITY / NOT_PROMOTED`** |
| harvestable | unresolved | `UNRESOLVED` |
| harvestable | absent | `POSITIVE_PAYOFF_NOT_ANNOUNCEMENT_SPECIFIC / NOT_PROMOTED` |
| unresolved | specific | `UNRESOLVED` |
| unresolved | unresolved | `UNRESOLVED` |
| unresolved | absent | `NOT_ANNOUNCEMENT_SPECIFIC / NOT_PROMOTED`, **while the payoff itself remains unresolved** |
| economically excluded | any | `NOT_PROMOTED` regardless of P2 |

```
DEFINITIONS
positive   = lower endpoint > 0
unresolved = lower endpoint <= 0 < upper endpoint
excluded / absent = upper endpoint <= 0
```

```
NO LOW_POWER LABEL EXISTS.
NO OBSERVED-POWER CALCULATION.
NO MECHANISM-FALSIFIED LABEL FOLLOWS FROM THESE GATES.
```

A failure to establish positivity is **not** automatically a reliable negative,
and rejecting the conjunction because one necessary property is excluded does
**not** resolve the other property.

---

## §13 Diagnostics

```
NO ADDITIONAL PROMOTION-CAPABLE DIAGNOSTIC MAY BE INTRODUCED.
```

Per-family FOMC / CPI / NFP summaries may exist **only** where already adopted by
Owner authority. Where serialized they carry:

```
PROMOTION_POWER = NONE
RESCUE_POWER    = NONE
no alternate weighting · no family-deletion rescue
```

```
DO NOT ADD new leave-one-family-out or regime diagnostics merely because the
final reviewer mentioned them illustratively.

NO TLT. NO F6.b. NO 2026 PERFORMANCE.
```

---

## §14 Sample reuse and evidence ceiling

```
SAMPLE_REUSE_CLASS      = T0_REUSED_DEPENDENT
EVIDENCE_CEILING        = SUPPORTED
INDEPENDENT_CONFIRMATION = NO
```

```
A NEW EVENT-METADATA LEG DOES NOT MAKE THE HEAVILY REUSED SPY PRICE HISTORY
INDEPENDENT.
```

`SUPPORTED` is a **ceiling, not an achieved verdict**. `confirmed` is
unreachable for F6 under this design.

---

## §15 Claim cap

The strongest success claim, conditional on all three gates passing, must remain
semantically equivalent to:

> On the frozen single-vendor adjusted-close SPY panel for 2011–2025, the
> predeclared prior-close-to-event-session-close pooled rule on the 462
> archive-eligible scheduled FOMC, CPI and Employment Situation sessions met its
> fixed promotion criteria: its mean event payoff, after the Owner-chosen
> DGS3MO cash opportunity-cost proxy and 4 bps round-trip cost, had a nominal
> 95% calendar-year percentile-bootstrap lower endpoint above zero; the EVENT
> coefficient in the fixed gross cash-excess return regression with weekday,
> TOM, holding-length and 10y/30y-auction controls also had a nominal lower
> endpoint above zero; and both point estimates remained positive after each
> single-calendar-year deletion.

```
THIS IS: HISTORICAL · DEPENDENT · T0 · SUPPORTED

UNDER: an adjusted-close execution proxy, an Owner-chosen cash proxy, and
       approximate 15-year-block inference.
```

```
IT MUST NOT CLAIM:
  causal uncertainty compensation
  independent confirmation
  individual FOMC alpha · individual CPI alpha · individual NFP alpha
  TLT premium
  pre-FOMC drift
  post-2015 persistence
  future persistence
  buy-and-hold dominance
  significance after every LOYO deletion
  production-grade fills
  exact finite-sample 95% coverage
```

### §15.1 Overclaims from superseded advice, explicitly not carried forward

```
"the cash convention is neutral because HOLD and the intercept absorb it"  FALSE IN GENERAL
"every family must show a positive announcement premium"                   NOT A THEOREM
"P1 and P2 jointly demonstrate buy-and-hold dominance"                      NOT ESTABLISHED
"the control is conservative"                                               NOT ASSERTED
```

Superseded advisory options are **not live permissions**. Any post-result change
to weights, family selection, cash proxy, cost, calendar, model or LOYO
semantics would **not inherit the independent PASS**.

---

## §16 Pre-seal accounting

```
TRIAL_LEDGER_CHANGED    = NO
EXPOSURE_LEDGER_CHANGED = NO
F6_PRIMARY_TRIAL_CONSUMED = NO
LEDGER_PRESEAL_OWNER_REVIEW_REQUIRED = NO
```

**Exposure ledger.** An `EXPOSURE_EVENT` is defined as a computation or read
that *reveals outcomes or measurements*. No F6 outcome or measurement exists, so
there is no row to append. Appending one would misrepresent the record.

**Trial ledger.** The `HYPOTHESIS_FAMILY` schema does support prospective, pre-run
registration — but its declaration trigger is explicit and unambiguous: *"a
family becomes declared only when its preregistration is **sealed**, and it is
appended here at that point"* (`F-TA` and `F-BENB` were both "appended here at
the seal, before any member has run"). **F6 is not sealed**, so the row is not
yet due. Registering it now would assert a seal that does not exist. No
ambiguity had to be resolved and no new accounting state was invented.

### §16.1 The row to append AT SEAL — drafted now so it is not transcribed late

`F-MMV` was appended **late**, at its S3 run rather than at its seal, and that
transcription delay had to be disclosed. To avoid a repeat, the `F-F6` row is
drafted here and is to be appended to `TRIAL_LEDGER.md` §6.2 **at the moment
Aaron seals**, before any member runs:

```
family  F-F6
declared at  research/extensions/f6/F6_S1_PREREGISTRATION.md, sealed <DATE>
             (SHA256 <SEAL HASH>); appended at the seal, BEFORE ANY MEMBER RUNS
members  F6-PRIMARY  the P1/P2/P3 conjunction on the 462-session pooled rule
                     (the ONE primary member, m = 1)
         F6-DIAG     per-family FOMC/CPI/NFP summaries where already adopted;
                     PROMOTION_POWER = NONE, RESCUE_POWER = NONE
multiplicity  m = 1; NO multiplicity correction, because no selection across
              cells occurs — the verdict is read off the single designated
              conjunction. No automatic +1 per attempt. P3 is a veto on the same
              lineage, not another shot. Diagnostics never enter N_trials.
status  NOTHING HAS RUN. F6_PRIMARY_TRIAL_SPENT = NO. No P1 mean, no
        beta_EVENT, no interval, no bootstrap statistic exists. N_trials on the
        ETF panel remains NOT ASSERTED — D-ETF-COUNT stays
        UNKNOWN_PENDING_AARON_DECISION, and this design uses no DSR.
```

This draft row is **not** an append and **not** a declaration. It becomes either
when Aaron seals.

---

## §17 Pre-seal mechanical validation — result

Full machine evidence:
[`F6_S1_PRESEAL_VALIDATION.json`](F6_S1_PRESEAL_VALIDATION.json), generated by
[`f6_s1_preseal_validate.py`](f6_s1_preseal_validate.py).

```
final event manifest = 462 unique sessions          PASS
family labels and overlaps reconcile (471 - 9)      PASS
all final count assertions pass                     PASS
15 complete, contiguous year blocks 2011..2025      PASS
each individual year's P2 design matrix full rank   PASS
all-session 2011-2025 control-row rule represented  PASS  (3772 rows, 0 dropped)
opening 2011 row has a valid prior-session boundary PASS  (2010-12-31)
DGS3MO mapping has no unexplained gaps              PASS  (max carry 3 days)
no 2026 outcome row enters the design               PASS
no TLT target field                                 PASS
no F6.b target field                                PASS
no alternate model                                  PASS
no alternate cost                                   PASS
no alternate benchmark                              PASS
no result file                                      PASS
no F6 outcome has been accessed                     PASS

VALIDATION = PASS, 0 failing checks
RESULT_CONTINGENT_BRANCH_FOUND = NO
```

**On `RESULT_CONTINGENT_BRANCH_FOUND`.** Every branch in §9 and §12 is fixed
before outcomes and is *terminal or vetoing*, never selective: P3 is evaluated
only after a passing pair but can solely downgrade; the §12 table is exhaustive
over the sign configurations; no branch chooses a different estimator, weight,
sample, cost or model as a function of a result. The independent review reached
the same conclusion — `RESULT_CONTINGENT_PROMOTION_BRANCH_REMAINS = NO`.

---

## §18 Firewall attestation

```
F6_RETURN_OUTCOME_ACCESSED   = NO
F6_PRIMARY_RETURN_COMPUTED   = NO
R / r_excess / r_net COMPUTED= NO
BETA_EVENT_COMPUTED          = NO
BOOTSTRAP_EXECUTED           = NO
CI COMPUTED                  = NO
SHARPE COMPUTED              = NO
LOYO PERFORMANCE COMPUTED    = NO
TLT INSPECTED                = NO
F6.b INSPECTED               = NO
2026 F6 PERFORMANCE INSPECTED= NO
NQ INSPECTED                 = NO
PRICE VALUES READ            = NO
```

The SPY panel was opened for its **date index and column presence (`notna`)
only** — the minimum strictly necessary to prove the design matrix and the
opening boundary row are constructible. No price value was read, printed, stored
or used arithmetically.

---

## §19 Seal status

```
SEAL_STATUS = DRAFT / OWNER_APPROVAL_REQUIRED

THE IRREVERSIBLE SEAL HAS NOT BEEN CREATED.
AARON ALONE MAY SEAL.
THIS DOCUMENT AUTHORIZES NO RUN, NO BACKTEST, NO DATA ACCESS BEYOND THE
EXISTING GRANT, AND NO REVEAL.
```

On seal, three things happen together: this draft is promoted to the sealed
contract and hashed; the `F-F6` row of §16.1 is appended to `TRIAL_LEDGER.md`
§6.2 with the seal date and seal hash filled in; and the pre-seal manifest
[`F6_S1_PRESEAL_MANIFEST.json`](F6_S1_PRESEAL_MANIFEST.json) is superseded by the
seal manifest. Until then, nothing about F6 has run.
