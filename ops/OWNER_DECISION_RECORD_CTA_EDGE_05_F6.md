# CTA-EDGE-05 / F6 — OWNER DECISION RECORD

```
RECORD_TYPE = OWNER_DECISION_RECORD
LINEAGE     = CTA-EDGE-05 (F6 MACRO_ANNOUNCEMENT_PREMIUM)
DATE        = 2026-09-21
STAGE       = S0 metadata feasibility. NOT sealed. NO F6 outcome exists.
SCOPE       = the adopted design state and its provenance. No result.
```

**What this document is.** The canonical record of what F6's design *is*, and —
separately — *who decided each part of it*. The programme's standing rule is that
advice, adjudication and adoption are different things, so they are kept in
different columns here rather than blended into a single "the design says".

---

## §0 How to read the provenance columns

```
ORIGINAL DESIGN AUTHORITY  the Round-1 discovery map's F6 entry. What F6 WAS
                           before anyone completed it.
FABLE ADVICE               constructive design advice. Fable is DESIGN-EXPOSED
                           on F6 and is never a verification or repair seat.
INDEPENDENT ADJUDICATION   the fresh independent pre-S0 seat. See §9 — its
                           original artifact is NOT PERSISTED.
CONTROLLER / OWNER ADOPTION   what Aaron, through the controller, actually fixed.
CONTROLLER OVERRIDE        where adoption DEPARTS from advice. Called out, not
                           smoothed over.
```

A line's authority is the **adoption** column. Advice that was adopted is still
advice as to its origin; that distinction is what makes an override legible
later.

---

## §1 Pinned authorities

| artifact | sha256 |
|---|---|
| Round-1 discovery map (F6 origin) | `02ca5f45fe41763e55a353090645c3b2a98b6dcf5fce572623ede604e569344a` |
| Round-1 backlog exhaustion review | `ec68547264dd95f022010b37…` |
| `Research Reports/2026-09-20-…-f6-od-1a-1h-s0-design-decisions-fable-01.md` | `0066584e7c4267926a6977eb…` |
| `Research Reports/2026-09-20-…-f6-od-2a-2h-pooling-control-gates-fable-01.md` | `4adaadc8f5be6ce0bc2a928c…` |
| `Research Reports/2026-09-21-…-f6-od-3a-3b-terminal-year-cash-return-object-fable-01.md` | `bf1642efd43ccdabbe95a8ba3f6b0bced808932c2c7c2934482c4eb2d3832a23` (VERIFIED) |
| `research/extensions/f6/F6_METADATA_AUDIT_RULE.md` (frozen) | `5063fe3b35deb09674cbb32078744822c2db403959317996c18f93aade32be11` |

All three Fable artifacts were verified **byte-identical after** the 2026-09-21
workspace reorganization moved them from the root into `Research Reports/`.

## §2 Decision aliases — no silent renumbering

```
F6-OD-TY    = the decision historically recorded as F6-OD-3A  (terminal partial year)
F6-OD-CASH  = the decision historically recorded as F6-OD-3B  (cash / payoff object)
```

These are **aliases for Owner-record readability**. The hash-pinned artifact
keeps its original `od-3a-3b` filename and its original internal labels, and is
**not renamed**.

> **A prior collision, preserved rather than tidied away.** An earlier OD-1
> section already used the informal label **"F6-OD-3"** for the **TLT
> diagnostic question**. That earlier usage is a different decision from
> OD-3A/OD-3B. Both usages are recorded here so a future reader who encounters
> the bare string "F6-OD-3" knows it is ambiguous and must be resolved by
> context.

---

## §3 Instrument, scope and lineage boundaries

| item | adopted state | provenance |
|---|---|---|
| promotion instrument | **SPY ONLY** | original authority; adoption confirms |
| TLT | **STRUCK ENTIRELY** from CTA-EDGE-05 outcome computation | **CONTROLLER ADOPTION**. TLT is not a secondary, not a diagnostic, not a robustness arm within this lineage |
| F6.b pre-FOMC drift | **SEPARATE FUTURE LINEAGE. MUST NOT BE COMPUTED here** | controller adoption |
| F6.c pre/post-2015 | **DESCRIPTIVE ONLY** — no promotion, no rescue, no kill power | controller adoption |

## §4 The primary object

```
ONE GLOBAL SPY SCHEDULED-EVENT STRATEGY, pooled over
   scheduled FOMC policy-statement releases
   CPI releases
   Employment Situation / NFP releases

conceptual trade   long 1 unit SPY at the prior eligible session close
                   exit at the eligible event-day close
                   flat otherwise
```

```
POOLING IS A PRE-OUTCOME MATERIAL DESIGN COMPLETION, NOT ORIGINAL AUTHORITY.
```

That sentence is load-bearing. The original F6 entry did not specify a pooled
three-family primary; pooling was completed before any outcome existed, which is
what makes it legitimate — and recording it as a *completion* rather than as
original authority is what keeps the F7 standard applied consistently here.

**Unit rule.** Each eligible event trading day receives **one unit weight, one
trade, one primary observation**. If several eligible releases fall on the same
trading day it remains **one position, one return, one observation**, with
multiple diagnostic labels permitted. **No double notional, ever.**

## §5 Payoff object and cash convention — F6-OD-CASH

```
PROMOTION PAYOFF = CASH_EXCESS_NET_TRADE_RETURN
```

| element | adopted state | provenance |
|---|---|---|
| cash benchmark | **DGS3MO** | **OWNER-CHOSEN EX-POST CASH OPPORTUNITY-COST PROXY** |
| what DGS3MO is NOT | not a signal input, not an eligibility input, not a position input, not a sizing input | controller adoption |
| accrual | `rf_hold = (annual DGS3MO / 100) × calendar holding days / 365` | **OWNER-CHOSEN** |
| transaction cost | **4 bps round trip** (2 bps entry + 2 bps exit) on traded event days | controller adoption |

> **The `/365` divisor is EXPLICITLY OWNER-CHOSEN and must never be attributed
> to Treasury, H.15 or FRED.** The S0 audit established that the source chain
> *terminates without specifying a day count*: FRED defers to H.15, H.15 states
> no day-count for constant-maturity yields and defers to Treasury, and
> Treasury's yield-curve methodology specifies no day count, no compounding and
> no daily divisor. `/365` is therefore a **design choice**, not a source fact,
> and this record keeps the two apart.

### 5.1 CONTROLLER OVERRIDE — the 16:15 publication lag

The S0 audit found that H.15 posts at **16:15 ET**, after the 16:00 NYSE close,
and reported that a rate *knowable at entry* would therefore be `DGS3MO(t−2)`.

```
OVERRIDDEN. Because DGS3MO is an EX-POST cash opportunity-cost proxy and NOT a
signal, eligibility, position or sizing input, its publication time imposes NO
t-2 trading-signal rule.
```

The audit's finding was correct **as a statement about knowability**; the
override is correct **as a statement about what this quantity is for**. Both are
recorded, because a later reader who sees only the override might otherwise
re-derive the lag and think it was missed.

### 5.2 CONTROLLER OVERRIDE — the rejected 7-day carry

Fable advice proposed *"last available DGS3MO within 7 calendar days."*

```
REJECTED. There is NO authority for seven days.

ADOPTED INSTEAD:
  latest official DGS3MO observation dated <= prev(d),
  carried ONLY when the missing observation is explained by the official
  source's own non-publication calendar.

If a gap is NOT explained by normal official non-publication:
  raise a METADATA_EXCEPTION. Never silently carry across an unexplained
  data defect.
```

Vindicated empirically at S0: over all 3,771 primary sessions the **maximum
carry required is 3 calendar days**, every skipped date is a weekend or a row
the official file itself carries as missing, and there are **zero unexplained
gaps**. A seven-day threshold would have been both unsourced and unnecessary.

## §6 Inference window — F6-OD-TY

```
PRIMARY INFERENCE PERIOD = calendar years 2011 .. 2025 ONLY
YEAR_BLOCK_SET           = 2011..2025      (15 complete blocks)
LOYO_YEAR_SET            = 2011..2025
2026                     = COMPLETELY OUTCOME-UNEXPOSED FOR F6
```

```
NO F6 QUANTITY MAY BE COMPUTED USING 2026 PRICE RETURNS.
```

2026 schedule **metadata** is retained in an explicitly non-outcome segment for
discoverability only; it does not enter the primary design matrix.

**Why this decision exists.** The S0 audit reported that a 16th block would have
been a *partial* year — roughly 5.4 months and 15 events against 29–32 for full
years — making it an unequal bootstrap block and a half-size LOYO fold. The
Owner resolved it by excluding 2026 entirely rather than by reweighting. All 15
remaining blocks are complete, and every LOYO fold now deletes a comparable
amount (435–438 events remain).

## §7 Promotion logic

```
P1  event strategy payoff = cash-excess SPY return MINUS 4 bps round trip on
    traded event days.
    PROMOTION: L95( mean r_net ) > 0.
    No additional magnitude floor.

P2  event-specificity coefficient, ONE FIXED CONTROL MODEL:
      r_excess(d) = a + beta_EVENT*EVENT(d) + weekday dummies + TOM(d)
                      + HOLD(d) + AUCTION(d) + error(d)
    on cash-excess daily SPY returns, GROSS of event transaction cost.
    PROMOTION: L95( beta_EVENT ) > 0.

P3  after P1 and P2 pass, EVERY leave-one-calendar-year-out point estimate of
    BOTH required effects must preserve positive sign.
```

```
A HYPOTHETICAL EVENT-TRADING COST IS NEVER SUBTRACTED FROM CONTROL DAYS.
P1 is net; P2 is gross. They are different objects and are not reconciled.
```

**Fixed model discipline.** No interactions, no alternate matched-control model,
no alternate regressions, no model selection. `TOM` reuses the sealed
seasonality definition exactly (`src/seasonality.py::is_tom`, last=1, first=3);
`AUCTION` reuses the pinned TA 10y/30y authority exactly.

```
THE CONTROL IS NOT ASSERTED TO BIAS TOWARD ZERO AND IS NOT ASSERTED TO BE
CONSERVATIVE. Any such claim is forbidden.
```

No Sharpe promotion floor — **Sharpe is descriptive only**. No extra economic
multiplier. **No power gate currently exists.**

## §8 Terminal classification — corrected

```
P1 harvestable + P2 specific  + P3 pass  -> SUPPORTED_HISTORICAL_EDGE
P1 harvestable + P2 specific  + P3 fail  -> ONE_YEAR_FRAGILITY / NOT_PROMOTED
P1 harvestable + P2 absent               -> POSITIVE_PAYOFF_NOT_ANNOUNCEMENT_
                                            SPECIFIC / NOT_PROMOTED
P1 harvestable + P2 unresolved           -> UNRESOLVED
P1 unresolved  + P2 specific             -> UNRESOLVED
P1 unresolved  + P2 unresolved           -> UNRESOLVED
P1 unresolved  + P2 absent               -> NOT_ANNOUNCEMENT_SPECIFIC / NOT_PROMOTED
P1 economically excluded                 -> NOT_PROMOTED regardless of P2
```

```
BECAUSE NO POWER GATE EXISTS:
   an interval spanning zero is UNRESOLVED.
   It is NOT automatically LOW_POWER, and it is NOT not_promoted.
```

**The earlier C-R classification that treated an unresolved payoff as
`not_promoted` is SUPERSEDED and must not be used.** This is a controller
correction, recorded as one.

**LOYO fragility semantics.** A P3 failure is `ONE_YEAR_FRAGILITY /
NOT_PROMOTED` — it is a statement that the effect does not survive deleting a
single calendar year, not a statement that the effect is absent.

## §9 Independent adjudication — provenance

```
F6_INDEPENDENT_ADJUDICATION_PROVENANCE_GAP = YES
ORIGINAL_INDEPENDENT_ARTIFACT              = NOT PERSISTED
ORIGINAL_HASH                              = UNKNOWN
```

The fresh independent adjudication was not persisted in the workspace or the
repository, re-checked mechanically at every pass. The accepted adjudication
**facts** are recorded in
[`../research/extensions/f6/F6_INDEPENDENT_ADJUDICATION_CONTROLLER_TRANSCRIPT.md`](../research/extensions/f6/F6_INDEPENDENT_ADJUDICATION_CONTROLLER_TRANSCRIPT.md),
which is explicitly labelled a **controller-supplied transcript /
reconstruction** and does **not** claim to be the original bytes. No hash was
fabricated.

This is a **pre-S1 documentation blocker**. It does not authorize return access
and does not block S0 metadata work.

## §10 What is NOT decided here

```
NO F6 OUTCOME EXISTS. No SPY return, no cash-excess return, no event P&L, no
beta_EVENT, no interval, no Sharpe, no LOYO performance has been computed.
F6_PRIMARY_TRIAL_CONSUMED = NO.
```

Still open before S1 sealing: the independent-adjudication artifact (§9), the
residual schedule-knowability items recorded in the S0 completion record, and
the S1 seal itself.

---

## §11 Final schedule-PIT event eligibility — `SCHEDULE_PIT_FAIL_CLOSED_RULE`

*Appended 2026-09-21. **Additive.** Nothing above this line is altered, and no
decision is renumbered.*

```
F6-OD-PIT   = SCHEDULE_PIT_FAIL_CLOSED_RULE   (new alias, §2 convention)
```

### §11.1 The adopted rule

```
A release whose date CHANGED is admissible ONLY IF the change was announced by
an authoritative contemporaneous source strictly before the entry decision at
close(t-1). Where the announcement timing CANNOT be established, the release is
PIT_UNRESOLVED_EVENT and is EXCLUDED from the primary sample, PRE-OUTCOME.

The ACTUAL release date is NEVER substituted for the announcement date merely
because it is known ex post.
```

Forbidden as evidence of announcement timing, and not used: a page's current
last-modified date · the actual release date · a weekday heuristic · media
recollection or the release contents.

```
THIS IS A SCHEDULE-AUTHORITY EXCLUSION.
It is NOT outcome filtering, NOT a mechanism failure, NOT return-based.
```

### §11.2 The ruling

```
BLS_RESCHEDULE_CASES_TOTAL = 8
  CHANGED_BEFORE_ENTRY     = 2   admissible at the ACTUAL date
                                 NFP 2013-11-08  (BLS blog 2013-10-31)
                                 CPI 2025-10-24  (BLS notice 2025-10-10)
  CHANGED_AFTER_ENTRY      = 0   none ESTABLISHED; not a claim that none exists
  PIT_UNRESOLVED_EXCLUDED  = 6   NFP 2013-10-22 · CPI 2013-10-30 (label only)
                                 CPI 2013-11-20 · NFP 2025-11-20
                                 NFP 2025-12-16 · CPI 2025-12-18
CANCELLED_ENTIRELY         = 2   NFP and CPI reference month 2025-10.
                                 No event ever existed; not an exclusion.
```

The excluded object is a **release**, not necessarily a session. **2013-10-30**
loses only its CPI label and **survives as an FOMC event**, because that FOMC
statement was independently scheduled and knowable.

### §11.3 Final counts — generated mechanically, asserted in code

```
PROVISIONAL_PRIMARY_EVENT_COUNT = 467   (superseded, retained, not rewritten)
FINAL_PRIMARY_EVENT_COUNT       = 462

FOMC 119 · CPI 176 · NFP 176 = 471 labels · 9 multi-event · 471 - 9 = 462
weekday / TOM / AUCTION event cells each sum to 462   ASSERTED, PASS
control matrix (3771, 9) rank 9 FULL RANK; EVENT not in span of controls
YEAR_BLOCKS = 15 (2011..2025); LOYO REMAINDERS = 430 .. 435
```

### §11.4 Release-time authority

```
CPI / NFP  08:30 ET, NO REGIME CHANGE LOCATED — contemporaneously attested at
           both ends of the window (USDL-13-2076 embargo line; BLS blog
           2013-10-31; 2025 reschedule notices). This is "none located", NOT
           "verified year by year".
FOMC       regime change LOCATED. From 2013-03-20: 2:00 p.m. ET, VERIFIED
           (Fed press release 2013-03-13 + frozen 2018-01-31 statement).
           Before it: 2:15 p.m. ET is an UNVERIFIED CARRY-OVER.
           ELIGIBILITY IMPACT = NONE — both times fall inside the session, so a
           close(t-1)->close(t) trade is unaffected either way.
```

### §11.5 Status

```
F6_PRIMARY_TRIAL_CONSUMED                 = NO
F6 outcome quantities computed            = NONE
EXACT_ADJUDICATION_TRANSCRIPT_STILL_OWED  = YES
F6_INDEPENDENT_ADJUDICATION_PROVENANCE_GAP= YES   (unchanged, still open)
```

This gate **finalizes event eligibility only**. It does not seal F6, does not
write S1 preregistration, and does not close the provenance gap in §9.

```
gate report    ../research/extensions/f6/F6_SCHEDULE_PIT_FINAL_GATE.md
final manifest ../research/extensions/f6/F6_FINAL_EVENT_MANIFEST.json
               sha256 49ff27bfc20eb98265c440bac7368e92022b356d77647dce9151f012e40ed382
```

---

## §12 S1 SEAL — Owner authorization and execution

*Appended 2026-09-21. **Additive.** Nothing above this line is altered, no
decision is renumbered, and no prior history is rewritten.*

```
OWNER_SEAL_AUTHORIZATION = YES
AUTHORIZATION_LITERAL    = "seal"
AUTHORIZED_BY            = Aaron (Owner)
S1_SEAL_STATUS           = SEALED
SEAL_ID                  = CTA-EDGE-05-F6-S1-2026-09-21
SEAL_DATE                = 2026-09-21
```

```
SEALED CONTRACT  ../research/extensions/f6/F6_S1_PREREGISTRATION_SEALED.md
                 sha256 f26df71d4596dd8cacd261e571040b5b0e39fd37ef897c87422af31eeef275d9
```

### §12.1 Three sources, never collapsed

```
FABLE          constructive design advice        OD-1 · OD-2 · OD-TY / OD-CASH
ASTRA          independent adversarial review    PASS,
               B_READY_FOR_S1_SEAL_WITH_CLAIM_CAP_NARROWING,
               sha256 23f723ed…ab589
               S1_SEAL_AUTHORIZED_BY_THIS_REVIEW = NO
AARON (OWNER)  adoption, and the SOLE seal authorization ("seal")
```

Advice is not review. Review is not authorization. **The independent review
expressly declined to authorize the seal**; only Aaron's explicit `"seal"` did.
These three remain three separate sources with three different authorities and
must never be presented as one.

### §12.2 What the seal did and did not change

```
SCIENTIFIC DESIGN CHANGED AT SEAL = NO
```

Instrument, SPY-only status, event families, pooled architecture, event
manifest, the 462-event sample, the 2011–2025 window, the 2026 exclusion,
entry, exit, position size, cost, cash proxy, the `/365` convention, P1, P2,
P3, terminal classification, bootstrap blocks, `B`, seed, quantile
implementation, TOM, AUCTION, the PIT exclusions, LOYO semantics and the claim
cap are all **unchanged**.

One parameterization was canonicalized, and it is not a design change:

```
WEEKDAY_REFERENCE = FRIDAY, with Monday/Tuesday/Wednesday/Thursday indicators
and an intercept.
```

OD-2's prose described the same control space with Monday as reference **and in
the same sentence recorded that δ is invariant to the choice of reference** —
which is correct, since `beta_EVENT` is numerically identical whichever weekday
is omitted from a full set alongside an intercept. The sealed contract carries
the Friday reference only. **OD-2 is historical and is not rewritten**; it keeps
its bytes and its pinned hash.

### §12.3 Accounting at seal

```
TRIAL_LEDGER_CHANGED          = YES   exactly one prospective family row, F-F6
F6_FAMILY_STATUS              = SEALED / NOT EXECUTED
F6_PRIMARY_TRIAL_CONSUMED     = NO
EXPOSURE_LEDGER_CHANGED       = NO
F6_PERFORMANCE_EXPOSURE_ADDED = NO
```

No exposure row was created because no F6 return or target measurement has been
revealed, and no new exposure type was invented to accommodate a seal.

### §12.4 Evidence is not upgraded by sealing

```
SAMPLE_REUSE_CLASS       = T0_REUSED_DEPENDENT
EVIDENCE_CEILING         = SUPPORTED
INDEPENDENT_CONFIRMATION = NO
```

### §12.5 Post-seal authorization state

```
S1                       = SEALED
S2_BUILD_AUTHORIZED      = YES
S3_RUN_AUTHORIZED        = NO
RETURN_REVEAL_AUTHORIZED = NO
```

S2 authorizes code and build work **only**. The historical run stays forbidden
until S2 implementation is complete, implementation acceptance passes, and a
**separate** S3 run authorization is issued by Aaron.

```
seal record     ../research/extensions/f6/F6_S1_SEAL_RECORD.md
sealed manifest ../research/extensions/f6/F6_S1_SEALED_MANIFEST.json
```

---

## §13 S4 VERDICT AND CLOSEOUT

*Appended 2026-09-22. **Additive.** Nothing above this line is altered and no
decision is renumbered.*

```
S4                  = COMPLETE
TERMINAL CLASS      = UNRESOLVED
PROMOTION STATUS    = NOT_PROMOTED
F6_LINEAGE_STATUS   = CLOSED / UNRESOLVED / NOT_PROMOTED
ROUND1_F6_ACTIVE    = NO
```

The one authorized primary ran once under `F6-AUTH-0001`
(`CTA-EDGE-05-F6-S3-PRIMARY-001`). Both point estimates are positive and both
nominal 95 % intervals span zero:

```
P1  +0.00035784   [-0.00062591, +0.00133231]   UNRESOLVED
P2  +0.00023075   [-0.00078811, +0.00123375]   UNRESOLVED
P3  NOT_APPLICABLE_BY_SEAL — never executed
```

```
MECHANISM_FALSIFIED               = NO
ECONOMIC_EFFECT_RELIABLY_EXCLUDED = NO
LOW_POWER                         = NOT ASSERTED
INDEPENDENT_CONFIRMATION          = NO
SAMPLE_REUSE                      = T0_REUSED_DEPENDENT
```

The study did not establish the declared edge, and equally did not exclude one.
It must never be described as falsified, as evidence of absence, as a negative
edge, as low power, as a causal failure, or as independently confirmed.

### §13.1 Execution governance reservation

```
POST_S2_EXECUTION_WRAPPER_ADDED = YES   commit c47fb228
SCIENTIFIC_COMPUTATION_CHANGED  = NO
S3_RESULT_INVALIDATED           = NO
GOVERNANCE_RESERVATION          = YES
```

An S3 orchestration driver was added after S2 acceptance and before exposure. It
performs orchestration only; the accepted S2 pipeline at build `43f0bb31`
remained the estimator, and the driver re-verified the accepted module hashes
before running. The first `--execute` invocation never launched Python — the
shell failed a log redirect into a missing directory — and caused **no** target
access; it is not counted as a historical execution. Neither fact is to be
rewritten away.

### §13.2 What remains closed

```
2026_F6_OUTCOME_ACCESSED = NO — and 2026 carries no confirmation, rescue or
promotion power for this closed primary. Any future use needs separate
prospective governance.

RERUN = NOT PERMITTED. The primary trial is consumed.

NEXT_EDGE_STARTED = NO. ROUND2_AUTHORIZED = NO. Control returns to the
programme Controller for next-edge selection.
```

```
closeout   ../research/extensions/f6/F6_CLOSEOUT.md sha256 f81390f804a5fde0a3ea1d8239fe424d00a75d83cb64aebf60a35917a41c5c8e
```
