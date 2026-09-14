# TSMOM-VRP-01 — FINAL HANDOFF

```
LINEAGE                         = TSMOM-VRP-01
HISTORICAL_VERDICT              = UNRESOLVED / CLASS 3 (INSUFFICIENT_EVIDENCE / LOW_POWER)
HISTORICAL_STAGE_B              = NOT_RUN_BY_SEALED_STOP_RULE
PROSPECTIVE_CONFIRMATION        = NOT_ACTIVATED_BY_OWNER_DECISION
DIAGNOSTIC (separate lineage)   = VRP-PORTFOLIO-DIAGNOSTIC-01, NOT_COMPELLING, PROMOTION_POWER = NONE
STATUS                          = CLOSED
FINAL_HANDOFF_READY             = YES
NEXT_GATE                       = ChatGPT final diagnostic acceptance
```

---

## 1. What was established

**The sealed historical question.** A standalone, unconditional, constant-maturity short
position in listed monthly VIX futures, held at a frozen stress-budgeted size, over
2006-09 … 2026-08 (240 months): the annualised arithmetic mean net excess return on
committed capital was `+0.073224` with a 95 % interval of `[+0.003906, +0.136081]` against
a required margin of `+0.075`. The interval straddles the margin, so the evidence is
**insufficient to decide** — it establishes neither that the margin is cleared nor that it
is excluded. Endpoints classify; the point estimate does not.

**The practical portfolio question.** At the one already-fixed 80/20 allocation, over the
217-month overlap 2008-05 … 2026-05: whole-sample Sharpe rises 0.751 → 0.908, volatility
falls, drawdown becomes shallower, and the correlation is genuinely negative (−0.105) — but
`ΔSharpe`'s 95 % interval `[−0.005, +0.311]` includes zero, and in SPY's worst decile the
book flips from `+0.86 %` to `−0.93 %` per month while all six declared crisis windows get
worse (GFC `+14.4 % → +1.7 %`, COVID `+7.9 % → −0.5 %`). **NOT_COMPELLING.**

**Taken together:** the sleeve is not shown to pay its way on its own, and at the one
allocation that was fixed in advance it buys unconditional calm at the cost of the core's
crisis behaviour. That is a coherent, closed answer, not a near miss to be retuned.

## 2. What must not be inferred

- `UNRESOLVED` is **not** "it doesn't work" and **not** "it nearly worked". It is
  insufficient evidence at the preregistered margin.
- The diagnostic is exploratory, outcome-exposed reuse with **no promotion power**. It
  cannot upgrade, rescue or reinterpret the historical verdict.
- Nothing here speaks to other tenors, other sizings, filtered variants, other markets, the
  option-based objects (A and B), or prospective behaviour. Sealed §O makes each of those a
  **new lineage** with its own trial accounting and its own Owner authorisation.
- The VIX-chain panel is now **exposed** (`N_trials = 1`) and may not be reused as fresh
  independent confirmation of this object.

## 3. Ledger of record

| | |
|---|---|
| VIX chain `N_trials` | 0 → **1**; `STAGE_A_TRIAL_SPENT = YES`, `STAGE_B_TRIAL_SPENT = NO` |
| Hypothesis family | `F-VRP` declared before any member ran; VRP-A has run, VRP-B never will |
| Exposure ledger | rows 48–52 (S1 seal, S2 acquisition, `GENERATED_NOT_SEEN`, single reveal, closure) |
| Reviewer seats | S27 Fable, S28 Astra — `material_design_contributor`, barred from blind certification; S29/S30 Opus — producer and now outcome-exposed, may not certify its own work |
| Grants | `VRP-AUTH-0001` (execution) and `VRP-AUTH-0002` (reveal), both **CONSUMED** |
| Prospective | never armed; no scheduler, daemon, cron, runner or prospective store ever existed |

## 4. Defect record

`VRP-DIAG-DEFECT-001` — found by the diagnostic's own reconstruction gate, repaired, and
re-validated. The book ledger recreated the sleeve position each calendar month, discarding
every month's first-day mark and re-entering from flat; the month-start sensitivity reset
was also mis-timed. Both are fixed, and 216 of 217 months now reconstruct to `8.3e-17`
against the sealed series. **No sealed result was affected** — confirmatory Stage B never
ran.

The honest part: **acceptance item 13 passed on a fixture that could not have caught this**,
because every synthetic month had its own contract keys and fresh prices. That is recorded
as `PREVIOUS_ITEM_13 = PASS_BUT_FIXTURE_INSUFFICIENT`, not rewritten.

---

## 5. KNOWLEDGE_BASE_INGESTION

*Candidate entries for later ingestion. **Deliberately not forced into the current KB
schema**, and the separate `quant-research-knowledge-base` repository was **not modified**.
These are handoff notes for when Aaron restarts the knowledge-base programme.*

### 5.1 Strategy / hypothesis result

```
id (suggested)     : strat.vrp.short-vix-futures-constant-maturity
question           : does an unconditional one-month constant-maturity short position in
                     listed monthly VX futures deliver useful compensation on committed
                     capital, after real holdings, rolling, variation margin, costs and
                     collateral, at a frozen stress-budgeted size?
research_status    : unresolved
failure_class      : 3 INSUFFICIENT_EVIDENCE / LOW_POWER
estimand           : annualised ARITHMETIC mean monthly excess return on committed capital
                     (never a CAGR, never compounded)
result             : +0.073224, 95 % [+0.003906, +0.136081], margin +0.075, floor -0.075
sample             : 2006-09 .. 2026-08, 240 months
evidence_context   : DESIGN_INFORMED_FIRST_LOCAL_USE (never "fresh", never "independent")
inference          : stationary bootstrap, 10,000 replicates, expected block 12 months,
                     95 % percentile, seed 7; 10,000/10,000 valid
trials_spent       : 1 (this sample's first and only governed trial)
successor_status   : any change to tenor, sizing, roll, cost convention, endpoints, tail
                     rule or any added filter is a NEW lineage (sealed stop rule)
```

### 5.2 Historical finding (descriptive, no promotion power)

```
id (suggested)     : finding.vrp.short-vix-erases-tsmom-crisis-gain-at-20pct
statement          : at a fixed 20 % capital share alongside the canonical 17-ETF TSMOM
                     book over 2008-05..2026-05, a short-VIX-futures sleeve lowered
                     whole-sample volatility and drawdown and raised Sharpe 0.751 -> 0.908,
                     but the Sharpe gain was NOT robust (95 % CI [-0.005, +0.311]) and the
                     book's SPY-bottom-decile mean flipped +0.86 % -> -0.93 %, with all six
                     declared crisis windows worse (GFC +14.4 % -> +1.7 %).
status             : EXPLORATORY, outcome-exposed reuse, PROMOTION_POWER = NONE
caveat             : one allocation only, fixed in advance; no weight was searched
cost fact          : execution cost consumed 23.8 % of gross carry / 31.2 % of net return
```

### 5.3 Dataset

```
id (suggested)     : dataset.cboe.vix-futures-monthly-chain
content            : monthly VX contract-level OFFICIAL daily settlements, listing ->
                     final settlement; 268 standard monthly contracts; 274 raw Cboe files;
                     2004-03-26 .. 2026-09-11; 47,160 rows, 46,331 settled; 0 duplicates
authority          : Cboe (CFE) official, two endpoints (delisted-contract archive and
                     market-statistics historical data); no vendor copy anywhere
licence            : Cboe personal / research use; NO REDISTRIBUTION; raw bytes stay
                     git-ignored, only hashes and manifests are tracked
N_trials           : 1 (exposed by this lineage)
relationship       : must_not_be_retested_on_same_sample -> this object
known structure    : four calendar months were never listed (2004-12, 2005-04, 2005-07,
                     2005-09); TWO published monthly final-settlement rules, boundary
                     bracketed to (2004-10, 2005-12]; the 2007-03-26 quotation/multiplier
                     rescaling (CFE IC07-03) sits INSIDE the usable window; CFE traded on
                     three dates US equities were closed (2015-04-03, 2018-12-05,
                     2025-01-09); first eligible complete month 2006-09 by the sealed rule
```

### 5.4 Failure mode — `VRP-DIAG-DEFECT-001`

```
id (suggested)     : failure.ledger.cross-month-state-reset
class              : implementation defect, multi-period accounting
symptom            : a book ledger's per-instrument position state was recreated inside the
                     per-CALENDAR-MONTH loop, so the first trading day of every month
                     recorded zero variation margin and re-established the entire position
                     from flat, paying a full round-trip every month
detection          : NOT by the unit tests. It was caught by a RECONSTRUCTION GATE that
                     required the ledger to reproduce an independently sealed monthly
                     return series to 1e-9 before any downstream metric was produced.
                     Magnitude at detection: 6.58e-02 on a 1e-9 tolerance.
second component   : the month-start sensitivity reset was applied AFTER the month's first
                     mark instead of at the month-end allocation, so the first day was
                     marked on the previous month's sizing
resolution         : hoist position state above the month loop; move the reset to the
                     allocation boundary; report the reset cost as its own field because
                     the constant-capital benchmark bears no reset trade
blast radius       : none — the confirmatory run it would have affected was already barred
                     by the stop rule, so the defect was latent
```

### 5.5 Research lesson — cross-month state continuity

```
lesson : in any multi-period ledger, the POSITION is continuous state and the ACCOUNTS are
         periodic state. They have different lifetimes and must be declared at different
         scopes. Resetting position state at an accounting boundary silently changes the
         strategy: it discards the boundary mark and converts a hold into a round trip.
generalises to : monthly rebalancing, quarterly reporting periods, fiscal-year books,
         any roll/settlement calendar that does not align with the reporting calendar.
tell   : if a period boundary is not also a natural flat point, ask what the position was
         the instant before it and whether the ledger still knows.
```

### 5.6 Research lesson — synthetic fixtures that structurally hide state bugs

```
lesson : a fixture can make a whole class of defect UNREACHABLE and still pass loudly. The
         Stage-B fixture gave every synthetic month its own contract keys and restarted
         prices at a constant, so no month boundary ever carried a live position. The test
         asserted the right identity and could never have failed on this bug.
why it survived : the identity under test (r_book = w*r_core + (1-w)*r_sleeve) is ALGEBRAIC
         in the ledger's own aggregates. It re-derives the book arithmetic, not the
         sleeve's correctness. A self-consistent ledger satisfies it while being wrong.
countermeasures :
  1. an identity that only uses the object's own intermediate values tests arithmetic, not
     correctness — pair it with a reconstruction against an INDEPENDENTLY produced series;
  2. fixtures must carry state ACROSS the boundary they claim to test, with a non-zero
     move at that boundary and weights strictly between 0 and 1;
  3. prove the fixture is discriminating: reproduce the old defect and require the fixture
     to separate the two by a stated margin, so it cannot pass trivially later;
  4. add a structural guard on the code shape itself (here: assert the position state is
     not declared inside the period loop);
  5. an oracle written by the producer in the same sitting reproduces the producer's
     misreadings — it catches slips, not misunderstandings.
precedent in this lineage : the SAME pattern appeared earlier, in the variation-margin sign
         (VRP_S1_MECHANICAL_ERRATUM_01): the closed-form oracle agreed with the engine
         because both encoded the same misreading, and only a test of the ECONOMICS
         ("a short must lose when the curve rises") caught it. Twice now, the thing that
         worked was asserting the object's behaviour rather than its formula.
```

### 5.7 Reusable components

```
vrp_calendar.py    : dated expiry-rule registry (two published VX rules), CFE holiday rules
                     with declared open-when-equities-closed exceptions, empirical exchange
                     calendar from settlement records, deterministic roll weights
vrp_specs.py       : dated quotation/multiplier/tick registry with primary-source pinning
                     and the common-basis conversion; the conservative undocumented-span rule
vrp_raw.py         : Cboe per-contract loader, official-settlement-only discipline,
                     mechanical operative-source selection, cross-source agreement check
vrp_chain.py       : constant-maturity front/second chain, carry-forward rule with per
                     contract-per-month limits, mechanical first-eligible-month derivation
vrp_costs.py       : max(c0, tick) cost engine with structurally isolated descriptive variant
vrp_sizing.py      : stress-budgeted sizing, stressed reserve, integer-granularity gate
vrp_stage_b.py     : self-financing book ledger with pro-rata internal funding, book
                     exhaustion, and (now) correct cross-month position continuity
vrp_reveal.py      : COMPUTE / STORE / REVEAL separation; committed-state single-use grants;
                     stage-scoped authorisation; a ProtectedResult that refuses to print
reconstruction gate: the pattern of requiring a derived object to reproduce an independently
                     sealed series to tolerance BEFORE any downstream metric is computed.
                     This is what found the defect, and it is the most portable idea here.
```

---

## 6. Recommended next step

Close TSMOM-VRP-01 and move to the next Phase-C / alpha candidate. No Fable round is
recommended: there is no fixed-weight improvement worth turning into a formal
portfolio-overlay lineage. `FABLE_FOLLOWUP_RECOMMENDED = NO`.

*Any receiver recomputes every hash cited in the underlying artifacts before use.*
