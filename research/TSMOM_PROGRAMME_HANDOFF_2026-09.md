# TSMOM PROGRAMME HANDOFF — Phases A → D, September 2026

```
SCOPE     = programme-level handoff and retrospective for the completed Phase A -> Phase D arc
STATUS    = Phase A COMPLETE · Phase B COMPLETE (conservative label retained) ·
            Phase C COMPLETE · Phase D COMPLETE / CLOSED
AUTHORITY = documentation only. This document authorises no run, no reveal, no candidate,
            no parameter change and no prospective activation.
CREATED   = 2026-09-14
```

This is the document to read instead of reconstructing the story from commits. It explains
what each phase established, what the evidence does and does not license, and what the next
CTA research cycle should inherit. It overwrites no historical handoff; lineage-level
handoffs stay authoritative for their own lineages.

---

## 1. State at closure

| | |
|---|---|
| Canonical TSMOM | **SUPPORTED — NOT INDEPENDENTLY CONFIRMED** |
| Canonical TSMOM role | **FROZEN RESEARCH BENCHMARK** |
| C-A prospective confirmation | sealed, **live under passive monthly accrual**, untouched here |
| C-D independent verification | **HOLD**, with strong evidence and one unresolved cross-vendor residual |
| Latest completed candidate | **TSMOM-VRP-01** — short VIX futures |
| VRP historical verdict | **UNRESOLVED / Class 3 — INSUFFICIENT_EVIDENCE / LOW_POWER** |
| VRP practical diagnostic | **NOT_COMPELLING** (exploratory, `PROMOTION_POWER = NONE`) |
| VRP prospective | **NOT ACTIVATED** — closed without activation, by Owner decision |
| VRP lineage | **CLOSED** |
| Next | ChatGPT programme-handoff acceptance → new CTA edge discovery |

---

## 2. Phase A — research and status cleanup · **COMPLETE**

Phase A turned an accumulated pile of studies into a programme with a defensible ledger.

- **The canonical 17-ETF TSMOM definition was frozen** — universe, the 1/3/6/12-month
  mean-of-signs composite, 60-day volatility sizing, asset target and caps, equal weighting,
  the portfolio volatility target and gross cap, month-end decision held through the next
  month, 2 bps one-way costs, and the full-universe liveness rule. Frozen means *identified
  by module and hash*, not described in prose: the Value contract's §17 comparator identity
  is the executable statement of it, and every later study consumes that object rather than
  a re-derivation of it.
- **Research statuses were reconciled** against the knowledge base and the repository, so a
  claim's label matches what was actually run on what sample.
- **Negative studies were kept, not silently discarded.** Four overlays (crash-defense,
  vol-compression breakout, seasonality, yield-curve slope) and a parallel cross-sectional
  study (XSMOM) are recorded with the *mechanism* of each failure, not just the outcome.
- **The status vocabulary was separated and is used strictly:**
  `supported` (evidence for, on a possibly-exposed sample) · `not_promoted` (a preregistered
  gate was failed, mechanism not excluded) · `falsified` (decisively rejected under a
  preregistered replication) · `unresolved` (insufficient evidence / low power — a terminal
  result, not a pending one).
- **Prior extensions and overlays were closed** where the evidence supported closing them.
- **Same-sample retuning and rebranding were explicitly rejected.** A failed overlay does not
  come back with a new lookback, a new threshold or a new name on the sample that failed it.

---

## 3. Phase B — canonical TSMOM validation · **COMPLETE, label deliberately conservative**

### 3.1 The canonical core

```
CANONICAL_TSMOM = SUPPORTED — NOT INDEPENDENTLY CONFIRMED
```

**Not upgraded here, and not upgradeable by anything in this document.** The historical
evidence is a full-sample, fixed-parameter result on a panel this programme has reused many
times; that supports the core as a *benchmark*, not as independently confirmed alpha.

### 3.2 C-A — prospective confirmation · live, untouched

C-A asks whether the canonical book's expected net Sharpe stays positive and materially
above +0.30 over a genuinely prospective window. It is **sealed and LIVE under passive
monthly accrual** in its existing state.

- It is **not** part of the long-horizon VRP plan that was rejected. The two are different
  studies with different objects; declining VRP's prospective clock says nothing about C-A.
- **Its state is not changed by this handoff**, and **no C-A prospective outcome was
  accessed, computed, inferred or reconstructed.** The terminal reveal remains a separate,
  unconsumed Owner authorisation at `N_scored = 120`.

### 3.3 C-D — independent verification · HOLD, with one residual

An independent implementation reproduced the canonical engine from the specification, and a
second vendor source (Tiingo) was reconciled against the frozen Yahoo-derived panel under
the sealed criterion.

- **Agreement is very high.** The sealed correlation gate passed: net-return-stream
  correlation **0.99940867** against a threshold of **0.995**, over **218 paired months**
  with no month dropped for a missing leg. Both vendor-driven implementations independently
  selected the identical evaluation window.
- **The outcome is nevertheless `C_D_HOLD`,** because the sealed `C_D_PASS` clause is
  *conjunctive*. Its second conjunct — *"every residual discrepancy explained by documented
  adjustment differences"* — is not satisfied. Discrepancy **D-S5** is classified
  `UNEXPLAINED`: October-2008 cross-vendor closing-price disagreements on XLE, XLU, RWX,
  DBA, HYG and VNQ (roughly 1–4 % on a handful of days) are not explained by any documented
  adjustment difference, the closing-convention hypothesis could not be verified, and two
  sources cannot arbitrate which vendor is right.
- **A high correlation does not discharge that clause.** The correlation bounds the
  *consequence* of D-S5 on the return stream; it does not *explain* D-S5. No threshold was
  invented for the residual, and the residual is traceable in principle — a third source or
  exchange records would settle it — but is not yet traced.
- **No casual upgrade follows.** C-D at HOLD does not make the canonical core independently
  confirmed.

*C-D's detailed artifacts live on the `cd-independent-verification` branch
(`CD_DISCREPANCY_REGISTER.md`, `CD_SPEC_CLARIFICATION_001.md`,
`CD_SB3_TIINGO_RECONCILIATION.md`), not on this one.*

### 3.4 What Phase B established, in plain language

The canonical TSMOM core looks **genuine enough to serve as the frozen research benchmark**
— an independent reimplementation reproduces it, and a second data vendor reproduces its
return stream to a correlation of 0.9994 — **while its evidence label stays conservative**,
because one cross-vendor residual is unexplained and the prospective confirmation has not
finished. Good enough to build against; not yet good enough to call independently confirmed.

---

## 4. Phase C — next-edge discovery and adjudication · **COMPLETE**

### 4.1 How candidates were found

- **Claude Fable 5.1** — opportunity map and constructive design; later the S0 frame, the
  delegated Owner decisions and the S1 seal package for the selected candidate.
- **GPT-6 Astra** — an *independent* opportunity map and an adversarial S0 challenge whose
  accepted repairs shaped the sealed contract.
- **Both are recorded as `material_design_contributor`** for the selected lineage and are
  **barred from ever blind-certifying** that design or any result under it. That bar is
  recorded on the seat axis (`ops/REVIEWER_EXPOSURE_LOG.md`, rows S27 and S28) so no later
  document can present either as a fresh certifier.

### 4.2 Final disposition at closure

Only the candidates actually present in the Phase-C records appear here; none is invented.

| candidate | disposition |
|---|---|
| **VRP / unconditional short VX futures** | **TESTED, now CLOSED** — see Phase D |
| **Treasury auction / intermediation** | **RESERVE** candidate for a future cycle; not started |
| **Positioning** (CFTC / crowding) | **PARKED** — the mechanism is high in principle but unidentifiable with the available data; it could not be separated from trend strength |
| macro-momentum and other reserve directions | retained **only** as the existing records describe them; nothing is promoted or added here |
| previously failed carry / overlay lineages | **must not be casually revived** — a failed overlay is not a new candidate because it has a new name |

VRP was selected over Treasury auction and Positioning on mechanism quality, genuinely new
information (implied volatility), clean standalone falsifiability, and a fresh futures
sample — with its known weaknesses (one consequential sizing choice; a slow independent-
confirmation path) recorded at selection rather than discovered later.

---

## 5. Phase D — TSMOM-VRP-01 · **COMPLETE / CLOSED**

### 5.1 The sealed historical experiment

A standalone, unconditional, one-month constant-maturity **short** position in listed
monthly VX futures at a frozen stress-budgeted size, with actual contracts, a calendar-only
deterministic roll, official Cboe settlements, daily variation margin, spread-plus-slippage
and per-side commissions, and collateral.

```
sample                                    = 2006-09 .. 2026-08, 240 months
annualised arithmetic mean net excess
  return on committed capital K           = +7.3224 %
95 % stationary-bootstrap interval        = [ +0.3906 % , +13.6081 % ]
required economic usefulness margin       = +7.5 %
HISTORICAL VERDICT                        = UNRESOLVED
FAILURE CLASS                             = Class 3 — INSUFFICIENT_EVIDENCE / LOW_POWER
evidence context                          = DESIGN_INFORMED_FIRST_LOCAL_USE
```

**The interval contains the +7.5 % margin**, so the study neither establishes that the sleeve
clears the required compensation nor reliably excludes it. Endpoints classify; the point
estimate never does.

*This result is not "almost passed", not "failed", not supported and not falsified.*

Historical Stage B was **barred by the sealed stop rule** (it was permitted only if Stage A
came out `SUPPORTED`), so it never ran and never spent a trial. The long-horizon prospective
clock was **declined by the Owner** and is closed without activation — nothing was ever
armed.

### 5.2 The accepted exploratory diagnostic

> `EXPLORATORY_ONLY = YES` · `OUTCOME_EXPOSED_REUSE = YES` · `PROMOTION_POWER = NONE`
> This is **not** Stage B and cannot change the verdict above. One allocation, fixed before
> any outcome was seen. No weight was searched.

Common sample **2008-05 … 2026-05, 217 months**:

| | ann. return | ann. vol | Sharpe | max DD |
|---|---|---|---|---|
| **CORE** canonical TSMOM | +7.74 % | 10.31 % | 0.751 | −15.60 % |
| **VRP** (excess of cash) | +8.00 % | 16.57 % | 0.483 | −43.82 % |
| **80/20 combined** | +7.77 % | 8.56 % | 0.908 | −9.57 % |

```
correlation      = -0.105
Delta Sharpe     = +0.157      95 % CI = [ -0.005 , +0.311 ]
PRACTICAL_CLASSIFICATION = NOT_COMPELLING
```

**Why NOT_COMPELLING**, in the order that matters:

1. **Unconditional volatility and drawdown did improve** — vol falls 1.75 pp, maximum
   drawdown becomes 6.04 pp shallower, and the correlation is genuinely negative. This is
   stated first because it is the honest case *for* the sleeve.
2. **The Sharpe improvement is not robustly established.** The 95 % interval on ΔSharpe
   includes zero. The rule was fixed in advance and applied as written; "−0.005 is nearly
   zero" is not a finding.
3. **Crisis and tail behaviour deteriorated.** In SPY bottom-decile months the book flips
   from **+0.86 %** to **−0.93 %** (−1.78 pp per tail month), and **all six** declared crisis
   windows are worse — the GFC gain falls from **+14.4 % to +1.7 %**, COVID turns from
   **+7.9 % to −0.5 %**.
4. **So the overlay weakens one of the core book's most valuable properties.** A CTA/TSMOM
   core earns much of its keep by being positive when equities are not. The sleeve buys
   unconditional calm precisely where calm is least wanted.

→ [`vrp/VRP_HISTORICAL_CLOSURE.md`](extensions/vrp/VRP_HISTORICAL_CLOSURE.md) ·
[`vrp/s3/VRP_STAGE_A_RUN_RECORD.md`](extensions/vrp/s3/VRP_STAGE_A_RUN_RECORD.md) ·
[`vrp/diagnostics/VRP_PORTFOLIO_DIAGNOSTIC_01.md`](extensions/vrp/diagnostics/VRP_PORTFOLIO_DIAGNOSTIC_01.md) ·
[`vrp/diagnostics/VRP_DIAGNOSTIC_DEFECT_001.md`](extensions/vrp/diagnostics/VRP_DIAGNOSTIC_DEFECT_001.md) ·
[`vrp/VRP_FINAL_HANDOFF.md`](extensions/vrp/VRP_FINAL_HANDOFF.md)

---

## 6. Reusable lessons

### A. The variation-margin sign incident

§E.1 wrote the variation margin with a leading minus while §D.2 defined the quantity as
*signed negative* for a short. Implemented literally, the position **gained** when futures
rose — a long. The first implementation did exactly that, **and the closed-form oracle,
written in the same sitting from the same text, reproduced the same misreading and agreed
with it.**

What caught it was a test of **economic behaviour**: *a short position must lose when futures
rise*. Not a test of the formula — a test of the object.

> A producer-written oracle catches slips, not misunderstandings. It encodes the same
> assumptions as the code it checks.

### B. `VRP-DIAG-DEFECT-001` — state reset at an accounting boundary

The book ledger recreated the sleeve's position state inside the per-**calendar-month** loop,
so the first trading day of every month recorded zero variation margin and re-established
the whole position from flat. A second component: the month-start sensitivity reset was
applied *after* that first mark instead of at the allocation boundary.

**The original fixture made the bug structurally unreachable** — every synthetic month had
its own contract keys and restarted prices, so no boundary ever carried a live position. The
test asserted the right identity and could never have failed on this defect.

What caught it was a **reconstruction gate**: the diagnostic required its ledger to reproduce
an *independently produced* sealed monthly series to 1e-9 before any downstream metric was
computed. The defect showed up as 6.58e-02 against that tolerance. After repair, 216 of 217
months reconstruct to 8.3e-17.

```
PREVIOUS_ITEM_13 = PASS_BUT_FIXTURE_INSUFFICIENT
CURRENT_ITEM_13  = PASS
```

No sealed result was affected: the confirmatory run this ledger serves was already barred.

### C. The general principle

**An internally self-consistent identity proves arithmetic consistency, not economic
correctness.** The §H.4 identity that item 13 checked is *algebraic in the ledger's own
aggregates* — a self-consistent but wrong ledger satisfies it.

For stateful portfolio engines, prefer:

- **behavioural invariants** — assert what the object must *do* (a short loses when the
  underlying rises), not what the formula looks like;
- **cross-boundary fixtures** — carry live state across every boundary the code partitions
  on, with a non-zero move at the boundary, and *prove the fixture is discriminating* by
  reproducing the old defect and requiring a stated separation;
- **independent reconstruction gates** — require the object to reproduce a series produced
  by a different path, to tolerance, *before* any downstream number is trusted.

In this programme the same failure pattern bit twice — an oracle and then a fixture each
encoding the producer's own assumption — and both times the thing that worked was asserting
behaviour rather than form.

---

## 7. Controls: what to keep, what not to default to

### KEEP as default for future CTA research

data authority and provenance · contract / instrument identity · no-look-ahead ·
transaction-cost realism · basic accounting identities · **economic-direction sanity tests**
· **state-continuity tests** · **independent reconstruction where practical** · a
predeclared primary rule · **one** governed historical evaluation · an uncertainty estimate
appropriate to the estimand · a fixed portfolio-relevance diagnostic when useful.

Every one of these is cheap relative to what it prevents, and three of them
(direction tests, state-continuity tests, reconstruction gates) are the specific controls
that caught real defects in this programme.

### DO NOT default to

multi-year / 10-year prospective experiments · endless independent vendors · repeated audit
rounds with no concrete failure evidence · repeated parameter sweeps after outcome exposure ·
elaborate governance for simple low-dimensional strategies · **confirmation work whose only
purpose is to avoid closing an unresolved result**.

The last one is the important one. An `UNRESOLVED` result is a terminal answer. Reaching for
a decade-long clock to avoid writing it down is not rigour.

### When prospective confirmation *is* appropriate

Only when **explicitly requested by Aaron**, when **deployment importance justifies it**, or
when a **genuinely high-value strategy needs stronger evidence than history can give**. It is
not a default step, and it is not a way to keep a lineage open.

---

## 8. The default next-generation CTA workflow

```
CANDIDATE DISCOVERY
  -> MECHANISM SCREEN
  -> FRAME / PREDECLARE
  -> BUILD
  -> VALIDATE FRAGILE PIECES
  -> ONE GOVERNED HISTORICAL RUN
  -> PORTFOLIO RELEVANCE
  -> VERDICT
  -> HANDOFF
  -> NEXT EDGE
```

**`LONG PROSPECTIVE CONFIRMATION` is deliberately NOT appended.** It is an exception invoked
on the conditions in §7, not a stage.

Note also *VALIDATE FRAGILE PIECES*, not "validate everything": validation effort belongs on
the components that are stateful, cross-boundary, cost-bearing or hard to reason about.

---

## 9. Canonical TSMOM is the frozen research benchmark

**Do not continuously mutate it.** The canonical book is the thing new ideas are measured
*against*; a benchmark that changes with every idea measures nothing.

New ideas become **separate research lineages** with their own identifiers, their own trial
accounting and their own Owner authorisations — for example `CTA-EDGE-01`, `CTA-EDGE-02`,
`TSMOM-X02`.

A new signal should answer, before it is built:

1. Does it contain **standalone** information?
2. Is it **economically distinct** from the core, or a repackaging of the same source?
3. Does it **survive costs**?
4. Is its improvement **robust**, not a point estimate?
5. What happens **conditionally** — in crisis, in trend, in chop?
6. Does it improve the portfolio **for the right reason**?

Question 6 is what VRP failed: the 80/20 book looked better unconditionally while getting
worse in exactly the states the core exists for. Question 2 is what XSMOM failed: at
liquid-ETF granularity it was largely the same source the time-series core already harvests.

---

## 10. Research map for the next cycle — **a map, not permission**

**Nothing below is authorised, scoped or scheduled. No candidate is selected.** This is the
space to choose from, not a queue to work through.

**TREND / MOMENTUM** — multi-speed trend · trend strength · breadth · acceleration and
deceleration · cross-sectional versus time-series information · signal aggregation.

**CARRY** — rates · FX · commodities · volatility · interaction with trend.

**POSITIONING / FLOWS** — CFTC positioning · crowding · systematic-flow pressure · dealer and
intermediary balance-sheet effects where measurable.

**TERM STRUCTURE / MARKET STRUCTURE** — futures curve · roll structure · dispersion ·
correlation state · liquidity state.

**MACRO / RATES** — Treasury auction / intermediation · monetary, inflation and growth state
*where the evidence and the event count support it*.

**PORTFOLIO / RISK** — conditional diversification · crisis convexity · dynamic risk
allocation · breadth and concentration · regime-specific correlation.

### Prioritise on

1. a plausible **economic mechanism**;
2. **data available** at sufficient history and event count;
3. **low overlap** with already-tested failed lineages;
4. potential **complementarity** with canonical TSMOM;
5. **manageable implementation complexity**;
6. a **clearly testable falsification condition**.

### Reject candidates that are merely

a parameter change · another lookback · another threshold · a renamed failed overlay · a
same-sample rescue of an exposed idea.

---

## 11. `KNOWLEDGE_BASE_PENDING_INGESTION`

```
KB_REPOSITORY_MODIFIED = NO
```

The separate `quant-research-knowledge-base` repository is **not modified**. These notes are
staged for ingestion when Aaron explicitly restarts the knowledge-base programme.

| candidate entry | source of record |
|---|---|
| canonical TSMOM state — `SUPPORTED — NOT INDEPENDENTLY CONFIRMED`, frozen benchmark | §3 here; `PROJECT_STATE.md` |
| Phase A–D programme map | §2–§5 here |
| VRP strategy result — `unresolved`, Class 3, with sample, estimand and interval | `VRP_FINAL_HANDOFF.md` §5.1 |
| VRP portfolio finding — 80/20 erodes crisis behaviour without a robust Sharpe gain | `VRP_FINAL_HANDOFF.md` §5.2 |
| Cboe VX dataset record — authority, licence, structure, `N_trials = 1` | `VRP_FINAL_HANDOFF.md` §5.3 |
| state-continuity failure mode (`VRP-DIAG-DEFECT-001`) | `VRP_FINAL_HANDOFF.md` §5.4; §6B here |
| synthetic-fixture failure lesson | `VRP_FINAL_HANDOFF.md` §5.6; §6C here |
| reusable validation / reconstruction patterns | `VRP_FINAL_HANDOFF.md` §5.7; §7 here |
| workflow lesson — avoid unnecessary long prospective experiments | §7 here |

---

## 12. Retrospective

### What worked

- **Preregistration prevented post-result rescue.** The VRP margin, window, cost convention
  and state boundaries were fixed before any number existed, so `UNRESOLVED` could not be
  argued into `SUPPORTED` afterwards — and was not.
- **Behaviour-level validation caught real bugs.** The variation-margin sign survived a
  producer-written oracle and died to a one-line economic assertion.
- **Reconstruction gates exposed state defects.** `VRP-DIAG-DEFECT-001` was invisible to the
  unit tests and obvious to a gate that demanded agreement with an independently produced
  series.
- **Negative and unresolved outcomes were actually closed.** Four overlays, XSMOM, X01,
  Value and now VRP are all written down and shut, with mechanisms.
- **Separating "generated" from "revealed" worked as designed.** The single governed run
  produced evidence nobody had seen, and the integrity gate ran on it before anyone looked.

### What was too heavy

- **Prospective machinery for ordinary candidate screening.** A 120-month clock was designed,
  sealed and built for a candidate that the historical evidence and a one-page portfolio
  diagnostic closed in a day. The design work was not wasted — but defaulting to it was.
- **Overextended governance for exploratory decisions.** Multi-seat authorisation discipline
  is right for a governed run; it is overhead for a descriptive diagnostic with no promotion
  power.
- **Audit layers past the point of diminishing returns.** Rounds that produced no concrete
  failure evidence cost real time. The controls that actually caught defects were cheap and
  specific; the expensive general ones caught nothing.

### What we will change

- **Faster candidate turnover** — more questions closed per unit of calendar time.
- **Mechanism first.** Screen on whether a plausible economic story exists and is
  *distinguishable from the core* before building anything.
- **Validate the fragile pieces, not everything.** Stateful ledgers, cross-boundary logic,
  cost accounting and instrument identity earn deep tests; the rest does not.
- **Bring portfolio relevance forward.** The 80/20 diagnostic was decisive and cheap; it
  should come near the verdict, not after a prospective plan.
- **Hand off immediately after the terminal verdict**, rather than looking for further work
  to justify the lineage staying open.

### What must never be lost

- **No same-sample rebranding.** A failed idea does not return with a new name on the sample
  that failed it.
- **No parameter rescue after outcome exposure.** Once a result is seen, changing `J`, the
  tenor, the cost convention or the window makes a *new lineage* with its own trial
  accounting — not a better version of the old one.
- **No promotion from a point estimate alone.** Endpoints classify. `+7.3224 %` against a
  `+7.5 %` margin with an interval spanning `[+0.39 %, +13.61 %]` is `UNRESOLVED`, and
  nothing about how close the point estimate looks changes that.
- **Negative and unresolved results are research capital.** They are the reason the next
  cycle can start from a real position instead of re-litigating settled ground.

---

*Every figure here reconciles to the accepted lineage artifacts; recompute their hashes
before relying on them. This document changes no verdict, no state and no authorisation.*
