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
