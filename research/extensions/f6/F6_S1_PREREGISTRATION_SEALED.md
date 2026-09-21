# CTA-EDGE-05 / F6 — MACRO_ANNOUNCEMENT_PREMIUM · S1 PREREGISTRATION (SEALED)

```
LINEAGE                    = CTA-EDGE-05 / F6 MACRO_ANNOUNCEMENT_PREMIUM
SEAL_STATUS                = SEALED
SEAL_ID                    = CTA-EDGE-05-F6-S1-2026-09-21
SEAL_DATE                  = 2026-09-21
OWNER_SEAL_AUTHORIZATION   = Aaron / explicit "seal"
NO_RETURN_EXPOSURE_BEFORE_SEAL = YES
F6_RETURN_OUTCOME_ACCESSED = NO
F6_PRIMARY_TRIAL_CONSUMED  = NO
```

> **This is the sealed contract.** It is promoted from
> `F6_S1_PREREGISTRATION_DRAFT.md` (sha256
> `5731b3fa1f4b6b779570e67936d40b011307f1d9e97cd75a3a284e04c9f9af00`), which is
> retained unmodified as the accepted pre-seal state. The scientific content is
> preserved; the only changes are the seal identity, the canonical weekday
> parameterization of §8.1, and the post-seal status of the ledger and
> authorization sections.
>
> **No scientific redesign was performed at seal.** Instrument, families,
> pooling, manifest, 462-event sample, window, 2026 exclusion, entry, exit,
> size, cost, cash proxy, `/365`, P1, P2, P3, terminal classification, bootstrap
> blocks, `B`, seed, quantile implementation, TOM, AUCTION, PIT exclusions, LOYO
> semantics and claim cap are all unchanged.

```
NO RETURN EXISTED WHEN THIS WAS SEALED. The seal operation was outcome-blind:
no SPY price value was read, no return, r_excess, r_net, beta_EVENT, interval,
Sharpe or LOYO performance was computed, at any point before or during it.
```

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

The exact bytes were copied into the repository, re-hashed, and the staged git
blob re-verified, so a fresh checkout reproduces the hash. It was not rewritten,
normalized or regenerated. **This review is the active pre-S1 independent review
authority.**

### §0.1 Three distinct sources, never collapsed

```
FABLE            constructive design advice (OD-1, OD-2, OD-TY / OD-CASH)
ASTRA            independent adversarial review — PASS, claim-cap narrowing
AARON (OWNER)    adoption, and the sole seal authorization
```

These are **three separate sources with three different authorities**. Advice is
not review; review is not authorization; and the review explicitly did **not**
authorize the seal. Only Aaron's explicit `"seal"` did.

### §0.2 The older missing artifact is NOT recovered

```
HISTORICAL_PROVENANCE_RESERVATION = YES   (NONBLOCKING)
```

The pre-S0 independent adjudication was never persisted.
[`F6_INDEPENDENT_ADJUDICATION_CONTROLLER_TRANSCRIPT.md`](F6_INDEPENDENT_ADJUDICATION_CONTROLLER_TRANSCRIPT.md)
remains a **controller-supplied reconstruction carrying no original hash**. It is
not independent evidence and not a certification. **Nothing here claims it was
recovered.** The reservation is non-blocking only because a *new* independent
review exists — new authority, not retrospective certification of the old.

---

## §1 Authority — every pin independently re-verified

Recomputed in the sealing session; **each reproduces the value the independent
reviewer recorded**.

| authority | sha256 |
|---|---|
| Round-1 F6 map (fields 1–15) | `02ca5f45fe41763e55a353090645c3b2a98b6dcf5fce572623ede604e569344a` |
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
| `TA_PREREGISTRATION.md` (auction authority) | `3b495fcb220a86b9c4226e308e4814bdfdd871d1c69ce352e99b78977436d35b` |
| `TA_EVENT_CALENDAR.csv` | `b27be5b1d94cfc13fc8310e0d5216675e097a2245fc954e4b12ed282563f7cb6` |
| seasonality `PREREGISTRATION.md` (TOM authority) | `d6f1909bd57b5c6fb1876613a9141a1d5203b66fdd64068dba5ee8908f33f7f1` |
| `src/seasonality.py` (sealed TOM implementation) | `43a75588b95f6ec42b090bc6b02fa2edc761f4fc82525288a544195ebab2a806` |
| `data/close_prices_raw.csv` (frozen SPY panel) | `3d2a7a56dbd92d4ff8138cfd894c87f5ac5ac088a11165db870673e0c05c3c31` |
| `data/DGS3MO.csv` (cash proxy source) | `50da2bfbb25e3e3241af7a4ad16e5a1bb5f08cdfb46bcb92f224954dce054319` |
| `F6_S1_PREREGISTRATION_DRAFT.md` (accepted pre-seal state) | `5731b3fa1f4b6b779570e67936d40b011307f1d9e97cd75a3a284e04c9f9af00` |
| `F6_S1_PRESEAL_MANIFEST.json` | `485a338d6456b1223ee2b7185c64732f0bb9d5f1b00b1146699549e845917786` |
| `F6_S1_PRESEAL_VALIDATION.json` | `40b389068431067ae32f04ffb9f9098654cb633190df8a666f5949e67b618df9` |

The Owner decision record and `TRIAL_LEDGER.md` both change **as part of this
seal transaction**; their post-seal hashes are pinned in
[`F6_S1_SEALED_MANIFEST.json`](F6_S1_SEALED_MANIFEST.json) and
[`F6_S1_SEAL_RECORD.md`](F6_S1_SEAL_RECORD.md), not here, so this contract
carries no stale pin for them.

**No historical authority was rewritten.** Superseded documents keep their bytes
and carry additive notes.

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
that authority**, pre-outcome. This is a completion of F6.a, not a new
hypothesis and not inherited permission.

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

**Regenerated mechanically from the manifest at `49ff27bf…ed382`; not
transcribed.** The manifest hash, not this table, is authoritative. A future
reader who cannot reproduce these numbers from that hash must STOP, never edit
the manifest into agreement.

### §3.1 Same-day multiple families

```
ONE trade · ONE unit · ONE return · ONE primary observation.
Diagnostic labels may be multiple. NO DOUBLE NOTIONAL.
```

The nine overlap sessions are exactly the difference between 471 labels and 462
observations.

### §3.2 The six PIT exclusions are permanent

```
NFP 2013-10-22 · CPI 2013-10-30 (label only) · CPI 2013-11-20
NFP 2025-11-20 · NFP 2025-12-16 · CPI 2025-12-18

NO POST-SEAL REINSTATEMENT. NO REINSTATEMENT AFTER OUTCOMES.
```

`2013-10-30` survives as an **FOMC-only** session, because that FOMC statement
was independently scheduled and knowable.

### §3.3 What the target population actually is

The estimand covers the **archive-verifiable eligible subset**, not every
announcement a contemporary investor might in fact have known about. Missing
schedule evidence clusters around shutdown disruption. **The sign of the
resulting external-validity difference is unknown**, and fail-closed exclusion is
not evidence of a performance bias in either direction.

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
order deadlines and slippage are un-modelled. The 4 bps figure in §7 is an
assumption, not a measured realized cost.

---

## §5 Opening 2011 control row — the all-session rule

```
P2 POPULATION = EVERY TRADING SESSION IN CALENDAR YEARS 2011-2025.
NO ROW IS DROPPED.
```

The independent review flagged that the S0 metadata gate had dropped its first
2011 row for undefined `HOLD`, whereas OD-TY and the adopted design say *every*
2011–2025 session. **The all-session rule governs.** A metadata-precheck
truncation is never promoted into a sample rule.

```
first primary session   2011-01-03
lag boundary session    2010-12-31

THE 2010 SESSION IS AN INPUT BOUNDARY OBSERVATION.
IT IS NOT A 2010 REGRESSION ROW. IT IS NEVER AN EVENT. IT IS NEVER
A BOOTSTRAP BLOCK MEMBER.
```

The same principle governs the cash-proxy mapping: the benchmark date for the
first 2011 session is `2010-12-31`.

```
P2 rows                                   3772
rows dropped for undefined HOLD              0
HOLD defined and strictly positive           PASS  (min 1, max 5)
EVENT column sums to 462                     PASS
OPENING_2011_ROW_RULE_VALIDATED           =  YES
```

---

## §6 Cash proxy — DGS3MO

```
ROLE = OWNER-CHOSEN EX-POST CASH OPPORTUNITY-COST PROXY

NOT a signal. NOT an eligibility input. NOT a position input.
NOT a sizing input.
```

Because it never touches eligibility, direction, size or execution, its
publication after the entry close introduces **no trading-signal look-ahead**.

### §6.1 Convention

```
rf_hold(d) = ( DGS3MO mapped annual percent / 100 ) * HOLD_calendar_days(d) / 365
```

```
THE /365 CONVENTION IS OWNER-CHOSEN.
IT MUST NEVER BE ATTRIBUTED TO TREASURY, H.15 OR FRED.
```

The source chain (FRED → H.15 → Treasury methodology) terminates without a day
count. This is also **not** an observed overnight cash-account return and **not**
a guaranteed reinvestment rate. It can affect both P1 and P2 and can matter near
a zero boundary; the earlier advisory claim that `HOLD` and the intercept
necessarily absorb the cash term is **false in general** and is not relied on.
That overstatement confers no authority to switch the proxy after results.

### §6.2 Mapping

```
Last official observation dated ON OR BEFORE the benchmark date, carrying
forward ONLY across source-explained non-publication (weekend, holiday, or a row
the source file itself carries as missing).

NO ARBITRARY 7-DAY RULE. There is no authority for one.
```

```
UNEXPLAINED SOURCE GAP  ->  IMPLEMENTATION HOLD.
DO NOT SUBSTITUTE ANOTHER CASH SERIES. DO NOT WIDEN THE CARRY.
```

```
sessions requiring rf_hold        3772
mapped to an official observation 3772
carry distribution (calendar days){0: 3744, 1: 8, 3: 20}
max carry                         3
UNEXPLAINED GAPS                  0
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

Charging the round trip in P1 only is deliberate: P1 asks whether the *declared
trade* clears cash plus cost; P2 asks whether *asset returns* carry a positive
EVENT coefficient. Different necessary properties.

---

## §8 The fixed P2 model — the only allowed specification

```
r_excess(d) = a
            + beta_EVENT * EVENT(d)
            + Monday + Tuesday + Wednesday + Thursday
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

### §8.1 CANONICAL WEEKDAY PARAMETERIZATION — sealed uniquely

```
WEEKDAY_REFERENCE = FRIDAY

INCLUDED WEEKDAY INDICATORS
  Monday · Tuesday · Wednesday · Thursday

WITH INTERCEPT.
```

The design matrix is exactly these nine columns:

```
const · EVENT · weekday_Monday · weekday_Tuesday · weekday_Wednesday ·
weekday_Thursday · TOM · HOLD · AUCTION
```

```
THIS IS THE CANONICAL PARAMETERIZATION OF THE ALREADY-ACCEPTED, FULL-RANK
WEEKDAY CONTROL SPACE. IT IS NOT A NEW MODEL AND NOT A DESIGN CHANGE.
```

> **Superseded prose, stated rather than hidden.** OD-2 specified the same
> control space while omitting a *different* weekday level — **and in the same
> sentence recorded that δ is invariant to the choice of reference.** That
> invariance is correct: with an intercept and a full weekday set less one
> level, `beta_EVENT` is numerically identical whichever weekday is omitted. The
> Friday reference is therefore a **reparameterization, not a contradiction**,
> and no scientific modification was required to adopt it.
>
> **This sealed contract serializes the Friday reference UNIQUELY**, and the
> superseded alternative is deliberately not restated here in any form that
> could be mistaken for a live specification. OD-2 itself is historical and is
> **not rewritten**; it keeps its bytes and its pinned hash at `4adaadc8…b34b1`.

Verified mechanically before and at seal:

```
shape (3772, 9)   rank 9   FULL COLUMN RANK
EVENT is NOT in the span of the controls    -> separately identified
Friday is the UNIQUE omitted weekday level
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

Event sessions concentrate on Wednesday (157) and Friday (198), with only 6
Mondays. `beta_EVENT` is therefore identified largely off Wednesday and Friday
sessions relative to the Friday reference. This is a **property of the frozen
event calendar**, recorded for honest interpretation. It creates no rank problem
and authorizes **no** reweighting, no alternative reference, and no additional
model.

---

## §9 P1 / P2 / P3 promotion gates

```
P1 HARVESTABLE
   L95( mean r_net ) > 0

   r_net = SPY adjusted-close close-to-close return
           minus the Owner-chosen DGS3MO cash opportunity-cost proxy
           minus 4 bps round-trip cost

P2 SPECIFIC
   L95( beta_EVENT ) > 0
   from the ONE fixed regression of §8, Friday reference.
   No interactions. No fallback model. No alternate matching design.

P3 YEAR FRAGILITY  —  ONLY AFTER P1 AND P2 BOTH PASS
   delete one complete calendar year at a time;
   refit the IDENTICAL objects;
   the P1 point estimate AND the P2 beta_EVENT point estimate must both remain
   STRICTLY > 0 for EVERY deletion.
   NO deletion-level significance requirement.
```

```
P3 FAILURE  ->  ONE_YEAR_FRAGILITY / NOT_PROMOTED.
                NOT MECHANISM FALSIFICATION.
```

`L95` denotes the lower endpoint of the §10 nominal 95% percentile-bootstrap
interval. P3 can only **veto** an otherwise-passing pair; it cannot rescue,
cannot reweight, and opens no optimization path. Requiring the conjunction is one
promotion decision, not a choice of whichever test passes — and it equally cannot
repair a miscalibrated constituent interval or historical sample selection.

---

## §10 Bootstrap authority — frozen

```
YEAR_BLOCKS = 2011 .. 2025   (15 complete, contiguous calendar-year blocks)
B           = 100000
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

A draw may contain one year repeated up to 15 times. Estimability was proved
**per individual year**, metadata only, on the pooled column set of §8.1:

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

Every block is full column rank, so **any** draw — including one repeating a
single year fifteen times — remains estimable. **No fallback was invented, and
none exists.**

### §10.2 Replication count

```
B = 100000
```

A **pre-outcome numerical-precision convention**. More draws improve numerical
resolution of the endpoints. They add **no historical information** and do not
improve coverage.

### §10.3 RNG — deterministic, derived pre-outcome

```
BOOTSTRAP_SEED_SOURCE
CTA-EDGE-05|F6|S1_BOOTSTRAP|49ff27bfc20eb98265c440bac7368e92022b356d77647dce9151f012e40ed382

SHA256 OF THAT STRING
97704c2ecdc530a56386c0a6b1a878bdf3083ad992011d6b946fd2a3bedcb180

FIRST 8 HEX CHARACTERS   97704c2e
BOOTSTRAP_SEED_LITERAL   2540719150
```

**Derived from the final event manifest hash — metadata — and never from returns
or any post-result artifact.**

> **Supersession, stated rather than hidden.** OD-2 contemplated deriving the
> seed from the *seal* manifest. The Owner instruction derives it from
> `FINAL_EVENT_MANIFEST_SHA256` instead. That is an explicit Owner decision and
> takes precedence; it is recorded so no future reader mistakes it for drift.
> The seed was fully determined **before** the seal and before any outcome.

### §10.4 Interval

```
INTERVAL  two-sided NOMINAL 95% percentile bootstrap
LOWER     0.025   (empirical 2.5th percentile)
UPPER     0.975   (empirical 97.5th percentile)

QUANTILE IMPLEMENTATION   numpy.percentile(..., method="linear")

PINNED ENVIRONMENT
  numpy  2.5.0
  pandas 2.3.3
  python 3.13.14
```

```
IF THE EXECUTION ENVIRONMENT DIFFERS, THE IMPLEMENTATION MUST STILL REPRODUCE
THE SEALED QUANTILE SEMANTICS.

DO NOT SILENTLY USE A CHANGED DEFAULT.
```

```
P1 AND P2 PROMOTION USE ONLY THE LOWER ENDPOINT.
```

S1 and S4 wording must say **nominal 95% percentile-bootstrap interval**, never
"exact 95% coverage".

### §10.5 Exceptional-case behaviour, frozen before outcomes

```
rank-deficient bootstrap draw     CANNOT ARISE (§10.1). If one nonetheless
                                  arises: STOP, report, do NOT drop a column,
                                  do NOT ridge, do NOT redraw.
missing price on a required date  STOP. Do not interpolate, do not skip the
                                  session, do not shift the window.
unexplained DGS3MO gap            IMPLEMENTATION HOLD (§6.2). Do not substitute
                                  a cash series, do not widen the carry.
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
concentration can compromise the approximation. Cluster asymptotics depend on the
number of clusters, and the literature supplies no universal safe cutoff. No
alternative block scheme is compared, and no power or precision is estimated from
returns.

---

## §12 Terminal classification — exhaustive, deterministic, frozen

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
positive          = lower endpoint > 0
unresolved        = lower endpoint <= 0 < upper endpoint
excluded / absent = upper endpoint <= 0
```

```
NO LOW_POWER LABEL EXISTS.
NO OBSERVED-POWER CALCULATION.
NO AUTOMATIC MECHANISM-FALSIFICATION LABEL FOLLOWS FROM THESE GATES.
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
SAMPLE_REUSE_CLASS       = T0_REUSED_DEPENDENT
EVIDENCE_CEILING         = SUPPORTED
INDEPENDENT_CONFIRMATION = NO
```

```
A NEW EVENT-METADATA LEG DOES NOT MAKE THE HEAVILY REUSED SPY PRICE HISTORY
INDEPENDENT.

SEALING DOES NOT UPGRADE EVIDENCE. `SUPPORTED` IS A CEILING, NOT AN ACHIEVED
VERDICT, AND `confirmed` IS UNREACHABLE FOR F6 UNDER THIS DESIGN.
```

---

## §15 Claim cap

A passing result may support **only**:

> historical, dependent **T0** support for the pooled SPY
> scheduled-announcement-day rule on the frozen single-vendor adjusted-close
> panel, under 2011–2025, 462 archive-eligible event sessions, the Owner-chosen
> DGS3MO opportunity-cost proxy, 4 bps round-trip cost, the fixed calendar
> regression, nominal/approximate 15-calendar-year percentile-bootstrap
> inference, and LOYO point-estimate **sign** preservation.

The strongest success claim, conditional on all three gates passing, must remain
semantically equivalent to:

> On the frozen single-vendor adjusted-close SPY panel for 2011–2025, the
> predeclared prior-close-to-event-session-close pooled rule on the 462
> archive-eligible scheduled FOMC, CPI and Employment Situation sessions met its
> fixed promotion criteria: its mean event payoff, after the Owner-chosen DGS3MO
> cash opportunity-cost proxy and 4 bps round-trip cost, had a nominal 95%
> calendar-year percentile-bootstrap lower endpoint above zero; the EVENT
> coefficient in the fixed gross cash-excess return regression with weekday,
> TOM, holding-length and 10y/30y-auction controls also had a nominal lower
> endpoint above zero; and both point estimates remained positive after each
> single-calendar-year deletion.

```
IT MUST NOT CLAIM:
  causal uncertainty compensation
  independent confirmation
  individual FOMC alpha · individual CPI alpha · individual NFP alpha
  TLT premium
  F6.b pre-FOMC drift
  post-2015 persistence
  future persistence
  buy-and-hold dominance
  LOYO significance
  stable LOYO magnitudes
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
to weights, family selection, cash proxy, cost, calendar, model or LOYO semantics
would **not inherit the independent PASS**.

---

## §16 Accounting at seal

```
F-F6 DECLARED AT THIS SEAL, BEFORE ANY MEMBER RUNS.

TRIAL_LEDGER_CHANGED            = YES  (exactly one prospective family row)
F6_FAMILY_STATUS                = SEALED / NOT EXECUTED
F6_PRIMARY_TRIAL_SPENT          = NO
F6_PRIMARY_TRIAL_CONSUMED       = NO
EXPOSURE_LEDGER_CHANGED         = NO
F6_PERFORMANCE_EXPOSURE_ADDED   = NO
```

**Trial ledger.** The `HYPOTHESIS_FAMILY` schema declares a family *at the seal*,
"appended here at the seal, before any member has run" (`F-TA`, `F-BENB`
precedent). `F-F6` is appended **as part of this seal transaction**, on time
rather than late — `F-MMV` had to be appended at its S3 run and the delay
disclosed. No `VARIANT_ATTEMPT` row, no executed-trial increment, no per-family
FOMC/CPI/NFP trial, no TLT trial, no F6.b trial.

**Exposure ledger.** An `EXPOSURE_EVENT` is a computation or read that *reveals
outcomes or measurements*. No F6 outcome or measurement exists, so there is no
row to append. **No new exposure type was invented.**

`N_trials` on the ETF panel remains **NOT ASSERTED** — `D-ETF-COUNT` stays
`UNKNOWN_PENDING_AARON_DECISION`, and this design uses no DSR and no trial-count
deflation.

---

## §17 Post-seal state

```
S1                      = SEALED
S2_BUILD_AUTHORIZED     = YES
S3_RUN_AUTHORIZED       = NO
RETURN_REVEAL_AUTHORIZED= NO
```

```
S2 AUTHORIZATION MEANS CODE AND BUILD WORK MAY BEGIN.
IT DOES NOT AUTHORIZE RUNNING THE HISTORICAL F6 OUTCOME.
```

The historical run remains forbidden until **all three** hold:

```
1. S2 implementation is complete;
2. implementation acceptance passes;
3. a SEPARATE S3 run authorization is issued by Aaron.
```

---

## §18 Firewall attestation at seal

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
F6.b COMPUTED                = NO
2026 F6 RETURNS READ         = NO
NQ OUTCOME DATA INSPECTED    = NO
SPY PRICE VALUES READ        = NO
```

The SPY panel was opened for its **date index and column presence (`notna`)
only** — the minimum needed to prove the design matrix and the opening boundary
row are constructible. No price value was read, printed, stored or used
arithmetically, at any point up to and including the seal.

---

## §19 Seal

```
SEAL_STATUS              = SEALED
SEAL_ID                  = CTA-EDGE-05-F6-S1-2026-09-21
SEAL_DATE                = 2026-09-21
OWNER_SEAL_AUTHORIZATION = Aaron / explicit "seal"
```

The seal identity and the post-seal pins are recorded in
[`F6_S1_SEAL_RECORD.md`](F6_S1_SEAL_RECORD.md) and
[`F6_S1_SEALED_MANIFEST.json`](F6_S1_SEALED_MANIFEST.json). This contract is now
immutable: it is superseded by citation, never by rewriting.
