# X01 — STAGE A2 PRE-SEAL DESIGN REVIEW — provenance record

**Study:** X01 — Commodity-sleeve futures transfer, matched-map arm (`TSMOM-EXT-001`)
**Stage:** A2 (pre-seal design challenge), QROS v2.0.1 / `AI_RESEARCH_OPERATING_MODE.md` §3.1
**Reviewer seat:** fresh GPT-6 Astra session
**Artifact reviewed:** `research/extensions/x01/X01_PREREGISTRATION_DRAFT.md`,
byte-state SHA256 `7ab9c5caf926842be7ac2f1017462ad50d77f35cb4f4360cadf8ee1a4f7914e8`
(the state produced by the preceding production-route repair)
**Record written by:** the Wave-1 Opus builder seat, during the bounded A2 repair.
**This seat produced the repair and cannot certify it.**

---

## §0 What this file is, and what it is NOT

This is a **provenance record of an accepted A2 review and of what was adopted
from it**. It is written under the mechanism the operating mode names for
durable A2 provenance (§3.2: the preregistration's Lineage/Amendments as
primary, a detailed review record as the companion), using this repository's
**existing** `review_history/` location. No new governance mechanism is created.

> **GAP — recorded, not papered over.** **The reviewer's original artifact is not
> persisted on disk.** The findings reached the builder session **through Aaron's
> relay in a working prompt**, which also carried Aaron's own instructions. Under
> the standing artifact-transport rule, chat-carried bytes are never a source of
> truth, so **this record is a relayed account, not a hash-matched reproduction
> of the reviewer's output.** It must not be cited as if the original had been
> read from disk. This is the same class of gap as `G-6` in
> `ops/REVIEWER_EXPOSURE_LOG.md`.

---

## §1 Verdict, as relayed and accepted

```
X01_A2_VERDICT   = FAIL
X01_SEALABLE_NOW = NO
```

The verdict was **accepted without dispute** by the builder seat and by Aaron.
The independently accepted futures infrastructure was explicitly **not** reopened:

```
X02_INDEPENDENT_STATUS      = PASS
X03_INDEPENDENT_STATUS      = PASS
WAVE1_FUTURES_INFRA_ACCEPTED = YES
```

---

## §2 Exposure — the point of A2's separation

| Field | Value |
|---|---|
| Timing relative to X01 outcomes | **BEFORE any X01 target outcome existed** |
| X01 performance accessed by the reviewer | **NONE.** No `ΔS`, no leg Sharpe, no paired series, no PnL |
| X01 performance accessed by this repair session | **NONE** — see the caveat in §5 |
| Protected forward data | **not opened** |
| Trial-ledger movement | **none.** A design review constructs no strategy-return series |

A2 exists precisely so that the design can be attacked while the answer is still
unknown. That property held here.

---

## §3 Blockers found, and their disposition

| # | Blocker (as relayed) | Disposition | Where |
|---|---|---|---|
| **1** | **Primary estimand conflated three objects** — paired observations `(F_t, E_t)`, the difference series `F_t − E_t`, and the scalar Sharpe difference. These are not interchangeable | **REPAIRED.** Primary estimand is now the scalar `ΔS = Sharpe(F) − Sharpe(E)`; the pairs are the resampling unit; `D_t` is a diagnostic. Sharpe, annualisation, raw/excess, ddof, degenerate and minimum-observation conventions frozen; four substitutions forbidden | §4 |
| **2** | **Endpoint treatment at the boundary was unspecified** — cases at exactly `ΔS = −B` or a bound touching `−B` were unclassified | **REPAIRED.** Strict / strict / inclusive-otherwise; the three states partition the line; a bound that touches `−B` never supports a claim | §5 |
| **3** | **O-3 unresolved**; risk of importing carry's 21-**trading-day** block rule into a **monthly** problem | **RESOLVED technically.** Paired stationary bootstrap, joint resampling, `ΔS` recomputed per replicate, **L = 12 months** mechanism-justified, 10,000 reps, 95 % percentile CI, `SeedSequence(7).spawn(3)` in fixed arm order, invalid replicates discarded-and-counted with a 9,500 floor. Carry's 21 **not** transplanted | §6.1 |
| **4** | **§6 precision relied on `expected correlation ≥ 0.9`** as though it were an observed paired-strategy correlation | **REPAIRED.** Replaced by a declared Jobson–Korkie/Memmel formula evaluated over a declared `ρ`-grid (0.50–0.95). No target-sample quantity enters. **Superseded wording note (O-3 closure, same day):** this disposition originally read "stated as a lower bound on the bootstrap width, hence an optimistic reachability check". That claim was itself too strong and was retracted from the contract — the table is a **pre-outcome design approximation, NOT a bound** on the sealed interval, and §6.2 now carries five explicit disclaimers | §6.2 |
| **5** | **O-4 was an invalid open item** — it proposed reopening V2's settled PRIMARY/DIAGNOSTIC split | **REMOVED.** Hierarchy made explicit and non-re-orderable; no tracking co-primary; diagnostics cannot rescue a failed primary; secondaries cannot become primary | §8.0, §9 |
| **6** | **Sample definition incomplete**; warm-up, initial positions and effective dates unspecified | **REPAIRED — and a defect was found.** The former **2010-07-31** start counted data availability as signal eligibility and silently skipped the 12-month warm-up. Three dates now distinguished: availability **2010-06-06**, first signal-eligible month-end **2011-06-30**, first paired evaluation month **2011-07-31**. **N = 179.** No bridge, no shortened composite, no padding | §3.5 |
| **7** | **"The locked signal" was insufficient** — neither return stream was defined to implementation level | **REPAIRED.** `E` and `F` frozen element-for-element, including the ag-basket signal surface, with an explicit symmetry statement | §3.6 |
| **8** | **S1 insufficiently specified** ("alternative construction") | **REPAIRED.** S1 changes exactly one thing — the signal-input price series — resolved to a **causal forward cumulative ratio adjustment**, chosen on a **causality** property, never a performance one. PnL still from the cash ledger | §8.1 |
| **9** | **S2 said only "fixed calendar"**, which previously admitted multiple implementations | **REPAIRED.** Bound to `commodity-carry-research/src/robustness.py::fixed_calendar_front_series`, with its accepted mechanics restated. No materiality threshold invented | §8.2 |
| **10** | **`COVID-2020` window ambiguous** | **REPAIRED.** Fixed to the repository's **pre-existing canonical** `config.py::REGIMES["COVID 2020"]` = 2020-02-01 … 2020-04-30; CY2022 is a plain calendar year. No alternative window computed; no crisis gate | §7.1 |
| **11** | **Trial accounting written as an immutable `14 → 17`** | **REPAIRED.** `+3` stated conditionally; the resulting total is computed **at execution** from the shared cumulative record. What does and does not create a `VARIANT_ATTEMPT` enumerated. Correlation cannot delete attempts | §10.1 |
| **12** | **Shared Databento home treated as a seal blocker** | **RE-GATED** to `SHARED_DATABENTO_HOME_GATE = PRE_EXECUTION`. Storage location cannot change statistical interpretation. **Ledger not created** | §12 |
| **13** | **O-1 / O-2 / O-6 unowned** | **CONVERTED to a bounded owner packet.** Two fully specified pre-existing options for O-1 with a structural recommendation; O-2's units, meaning, candidates and reachability consequences with **no value proposed**; O-6's technical half frozen and its policy half bounded | §15 |

**Escape-route sweep.** All seven routes the review enumerated are registered
with their disposition at **§14**. At the time of this repair,
`POST_HOC_ESCAPE_ROUTES_REMAINING` = the three owner decisions and nothing else;
**after Aaron's adoptions (§6A) it is `NONE`.**

---

## §4 Contribution classification

**`material_design_contributor`** — *not* `reviewer_only`.

The operating mode (§3.2) draws the line at *supplying* a design element that is
adopted, versus identifying a defect and asking for justification. Several
adopted elements fall on the supplying side: the **scalar-estimand
reformulation**, the **removal of O-4**, the **`PRE_EXECUTION` re-gating of the
shared home**, and the **escape-route taxonomy** that §14 implements.

> **Attribution caveat, recorded rather than resolved.** The findings arrived
> through Aaron's relay, which also carried Aaron's own instructions. **Which
> adopted elements originated with the reviewer and which with the owner cannot
> be separated from the relay.** `material_design_contributor` is therefore the
> **conservative** classification, chosen because under-claiming reviewer
> contribution would weaken the Stage I obligation below.

### Stage I consequence — binding

Per the operating mode's contamination accounting, a fresh Stage I **GPT-6 Astra**
session would retain **context independence** and would not be this artifact's
author, but would **lack model-family diversity** on precisely these elements.
Therefore:

> **The elements listed above must not rest on same-family review as their sole
> independent certification.** Certifying them requires routing to **Opus or
> Fable**, or marking that certification **explicitly non-independent**. The
> Stage I verifier reads this record **before** verification begins and reports
> independence **scoped** — "independent of the implementation and post-seal
> analysis", never "fully independent reviewer".

**Reviewer and model diversity are review diversity. They are never sample
independence and never statistical replication.**

---

## §5 What the repair session did and did not touch

**Did not:** run X01 performance · compute any X01 Sharpe from the target sample ·
inspect protected-forward outcomes · seal X01 · choose any design value from an
outcome · modify accepted V2 · rerun X02 or X03 · modify
`commodity-carry-research` · purchase data · start strategy construction ·
resolve D3 or D9 · create the shared Databento ledger.

**Did:** repair the preregistration text; verify structural facts from the
accepted panels (contract counts, first-settlement dates, coverage fractions);
evaluate a closed-form precision formula on **declared constants**.

> **Disclosed incidental exposure.** While establishing that no standalone
> commodity-sleeve monthly stream is published (§3.6), the session read
> `output/dd_sleeve_summary.csv`, which carries the **published baseline's
> portfolio-scoped Commodity-sleeve summary statistics**. That is
> already-published T0 material and this seat's cumulative classification was
> already `REVEALED_TARGET_METRIC`, but it is **adjacent to the `E` leg of `ΔS`**
> and is therefore recorded as a research-axis exposure event rather than left
> implicit. **It was not used to choose `B`, the block length, the basket, or any
> other design value**, and no O-1/O-2/O-6 rationale in §15 rests on it.

---

## §6A Owner decisions taken after this review — appended 2026-09-08

The three items this review left to the owner were decided by Aaron and
incorporated into the preregistration (§13 Lineage, §15). **Appended here so the
A2 record and the contract cannot drift apart.**

| Item | Decision | Timing |
|---|---|---|
| **O-1** | `O1_OWNER_DECISION = ADOPT_OPTION_B` — ag proxy `ZC ZS ZW LE HE GF`, equal 1/6, `FIXED_PROXY_WITH_COMPOSITION_MISMATCH`. **Option A is not an evaluated alternative** | pre-outcome |
| **O-2** | `O2_OWNER_DECISION = B_0.15` — `B = 0.15` annualised Sharpe, boundary `−0.15`, an **owner utility / economic tolerance**. No fallback; not alterable after outcomes; no alternative `B` reportable | pre-outcome |
| **O-6** | `O6_OWNER_DECISION = ADOPT_OPTION_1_SYMMETRIC_ZERO_CARRY`. A **symmetric research convention**, explicitly **not** a claim of live-deployment economics. **Option 2 is not an alternative success route** | pre-outcome |

**Prospective timing — the property that matters.** All three were taken
**before any X01 paired return series, `Sharpe(F)`, `Sharpe(E)`, `ΔS`, bootstrap
result or crisis statistic had been computed or opened.** No X01 target-outcome
artifact existed at the moment of decision and none exists now
(`TARGET_X01_OUTCOME_ACCESSED = NO`).

**What this does NOT change.** The §4 contribution classification stands:
`material_design_contributor`, with the attribution caveat and the **binding
Stage I obligation** that those elements must not rest on same-family (GPT-6
Astra) review as their sole independent certification. The §0 gap stands: the
reviewer's original artifact is **not persisted on disk**. **Reviewer and model
diversity remain review diversity — never sample independence, never statistical
replication.** An owner decision is adjudication, **not evidence**, and **not
authorization to execute**.

**A2 must be re-run on the amended contract**, because the amendment is exactly
the kind of change §3.1 of the operating mode says can introduce a new defect.

---

## §6B Delta review — four design defects, repaired 2026-09-08

The same A2 reviewer re-read the amended contract and returned
**`X01_A2_DELTA_VERDICT = FAIL`**, `X01_A2_DESIGN_BLOCKERS = 4`,
`X01_A2_OWNER_DECISIONS_REMAINING = 0`. The verdict was **accepted**; the
independently accepted infrastructure (X02, X03, panel, OI, cash-first
primitive, V2) was **not reopened**.

| # | Defect | Repair | Where |
|---|---|---|---|
| **1** | **Active signal contradicted frozen V2** — §3 said *mean of the {1,3,6,12}-month total returns*; V2 and `src/signals.py::signal_method_b` specify the **mean of the SIGNS** | **REPAIRED.** `s_t = [sign(R_1m)+sign(R_3m)+sign(R_6m)+sign(R_12m)]/4`, reproduced from source; zero convention `np.sign(0)=0` **read from the code, not invented**; all four horizons required; `combine="mean"`. Binding regression: **+0.5** on `(+0.10,+0.10,+0.10,−0.01)`, rejecting 0.0725 and +1.0 | §3.7, §3.7.1 |
| **2** | **Rebalance cost used `Δ|position|`** — a position-magnitude change, not a traded quantity. Returns **0** on a `+1 → −1` reversal and **0** across a roll | **REPAIRED.** `Σ_j |q_j,t − q_j,t−1| × C_j` per **contract identity**; sizing→quantity from the authoritative convention; continuous research quantities declared as such; cost rate invariant to `K`. **The X02 primitive is unchanged.** Regressions A–E pin the reversal at **2 sides / $25.00** | §3.8, §3.8.1 |
| **3** | **S1 ratio direction and roll timing ambiguous** — the prose formed `r = P_new/P_old` and multiplied, which at 100→110 gives an adjusted roll level of **121**, amplifying rather than removing the discontinuity | **REPAIRED.** One exact equation, `k_new = k_old × P_old,τ / P_new,τ` and `P_adj,t = k_new × P_new,t` for `t ≥ τ`; `τ` = the A1 held-front change (the same date the cash legs are charged); both settlements at `τ`; factor applies **at** `τ`; history never restated; compounding and the no-common-settlement case declared. Regression: **100 → 100 → 110**, rejecting 121 | §8.1 |
| **4** | **Secondary inference undecided** — BH-FDR carried as a *"challengeable default, not a decided rule"*, and a consequence attached to an undefined *"material divergence"* | **DECIDED.** `F-X01` holds one confirmatory test, so **`BH_FDR_REQUIRED = NO`**; `SECONDARY_INFERENCE_ROLE = DESCRIPTIVE_SENSITIVITY`, `S1_S2_PROMOTION_POWER = NONE`, `SECONDARY_MATERIALITY_GATE = NONE`, with six prohibitions. The undefined condition is **deleted, not thresholded**: `SIGNAL_INPUT_CONSTRUCTION_DOF = REQUIRED` unconditionally, mirroring `ROLL_RULE_DOF = REQUIRED` | §8.3, §8.1 |
| *n/b* | February-2020 month-end typo | **CORRECTED** 2020-02-28 → **2020-02-29**; the canonical Feb–Apr 2020 window and all crisis semantics unchanged | §7.1 |

**Completion-first note on defect 4.** V2 was read before deciding. Program v2
§0 rule 5 requires a preregistration to **state** its family's multiplicity
treatment and carries BH-FDR only as a *challengeable default*; the family table
gives `F-X01` the scope *"one contract; secondaries declared"*. **No formal
secondary inference is required**, so the minimum design was adopted rather than
a threshold invented. MAP_v2 X03's conditional consequence is discharged
**unconditionally** by the two DoF declarations, which is why no materiality
gate was needed to preserve it.

**Cross-family certification.** Astra's delta result states
`CROSS_FAMILY_CERTIFICATION_REQUIRED_BEFORE_SEAL = NO`. **No Fable pre-seal gate
is created here.** The broader obligation recorded at §4 is preserved exactly as
the pinned doctrine states — the adopted design elements must not rest on
same-family review as their **sole** independent certification — **without
inventing a timing requirement** for when that certification must occur.

**Exposure.** No X01 target outcome was accessed by the reviewer or by this
repair session; the four repairs were verified on **synthetic inputs and pure
arithmetic only**. `TARGET_X01_OUTCOME_ACCESSED = NO`.

---

## §6 Status after this review

```
X01_A2_VERDICT               = FAIL (accepted)
X01_TECHNICAL_PREREG_REPAIR  = COMPLETE
TECHNICAL_BLOCKERS_REMAINING = NONE
OWNER_DECISIONS_REMAINING    = NONE  (O-1/O-2/O-6 adopted -- see §6A)
X01_PREREG_SEALED            = NO
X01_FULL_PERFORMANCE_EXECUTED = NO
X01_A2_FINAL_CLOSURE         = NOT_YET
X01_A2_DELTA_VERDICT         = FAIL (accepted) -> four defects repaired, see §6B
NEXT GATE                    = SAME GPT-6 ASTRA X01 A2 DELTA CLOSURE
```

**A2 must be re-run after Aaron's adoptions**, because fixing one rule defect can
introduce another (operating mode §3.1). The builder seat that wrote this record
may not perform that closure.
