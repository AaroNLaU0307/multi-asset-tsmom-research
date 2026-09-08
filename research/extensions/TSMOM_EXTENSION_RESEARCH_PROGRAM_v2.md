# TSMOM Extension Research Program — v2 (converged draft)

**Status:** PROVISIONAL REVIEWABLE DRAFT. Produced 2026-09-08 under Aaron's authorisation to draft the amended architecture only. Nothing here authorises Wave 0 execution, Wave 1, strategy construction, any backtest, any FULL study, any data acquisition, opening protected outcomes, forward-data release, or any change to the frozen baseline. The next gate is a fresh GPT-6 Astra document-only verification of this draft.
**Supersedes nothing yet.** The v1 originals remain immutable review-history artifacts:
- `TSMOM_EXTENSION_RESEARCH_PROGRAM.md` — SHA256 `7495faa976357592f50243e4f6b0342d557cc47193be85df938ee8e26b79040b`
- `TSMOM_EXTENSION_RESEARCH_MAP.md` — SHA256 `76b902ed6e244fd2bb8293c1a55191c8b468759fcd5b1eeda7d10465be1d15f5`

**Governing review artifacts for this draft (authority order: Aaron's instructions → Astra Round 2 → accepted Fable Round-1 amendments → accepted Astra Round-1 findings → v1):**
- GPT-6 Astra Round 2, "CONDITIONAL CONVERGENCE" — chat-carried, persisted verbatim at `review_history/ASTRA_ROUND2_CONVERGENCE_2026-09-08.md`, SHA256 `0a89d43919813eee302863eb642571347370e374c7966c9a81303dc9e0579869`. **PIN_STATUS = AUTHORITATIVE_MATCHED** — declared authoritative by Aaron on 2026-09-08 (closing D0); recomputed and matched in a transport-reconciliation pass that made no architecture change. The persisted file is unmodified (its own header line still reads "pending" because those bytes are the pinned bytes).
- Fable Round-1 response — pinned by Aaron outside this repository (Astra cites a `.codex/attachments/…/pasted-text.txt` copy); its hash is not known to this session and is not asserted here.
- GPT-6 Astra Round 1 — not persisted in this repository; its findings are represented through Astra Round 2's resolution table.

**Companion:** `TSMOM_EXTENSION_RESEARCH_MAP_v2.md` (hypotheses `X01`–`X46`, amended), `idea_registry/IDEA_REGISTRY_v2.csv`, `DASHBOARD_v2.md`.

```ini
RECOMMENDED_MODEL=Claude Fable 5.1 (original author, drafting the converged amendments as instructed)
EFFORT_INTENT=VERY_HIGH
RECOMMENDED_EFFORT=xhigh
EXECUTION_MODE=STANDARD
ROLE=architecture author — document-only amendment pass
WINDOW=CONTINUATION
MUST_NOT_BE=strategy builder; backtest runner; Wave-0 executor; preregistration certifier; alpha optimiser; data purchaser; verifier of this draft
LANE=EXPLORATORY
OUTCOME_EXPOSED=TARGET_METRIC (published results read in v1 design; nothing new computed in this pass)
PREREG_SEALED=N/A
```

**Provenance of adopted reviewer contributions.** The following V2 elements were supplied or materially shaped by GPT-6 Astra (Rounds 1–2) and are adopted here by the architecture author, not by Astra: the evidence-context model and the separation of design lineage from validation evidence (§0A); output-based exposure classification (§0B); claim-specific crisis-preservation scope (§0 rule 11); the redundancy-review reframing (§0 rule 12); the three-state X01 contract form (§3); the X44 logical correction (§7); the X09 structural-screen naming (§4); the X35/X36 stage split (§8). At each candidate's preregistration the design owner (Opus) must formally adopt and justify any of these it uses. Independent certification of a candidate that rests on these elements follows §1's non-producing-session rule; Aaron's approval is adjudication, never independent statistical evidence.

---

## 0. Ground rules that apply to every wave

1. **The baseline is frozen.** `multi-asset-tsmom-research` HEAD `c63114a` (`config.py`, `universe.py`, `src/{signals,sizing,portfolio,performance,validation}.py`) is the reference strategy, KB status `supported` (evidence type `full_sample_fixed_parameter`). Extension code lives under `research/extensions/<family>/` and imports the engine; it never edits it. A better historical point estimate is not a reason to change the baseline.
2. **Three lanes, three kinds of claim.** EXPLORATORY emits hypotheses and leads; MEASUREMENT emits implementation facts, structural findings and premise results; FULL emits promotion or non-promotion under a sealed preregistration. There is no fourth lane and no "lite" variant of any lane: a small FULL study has proportionate effort and full claim protection.
3. **Premise before PnL.** Every conditional or overlay hypothesis passes a descriptive premise test before any strategy PnL is fit. A failed premise is a finished result (`not_promoted`, reason `premise_not_confirmed`), recorded permanently. A premise pass admits nothing further by itself.
4. **Paired, not standalone.** Any candidate that modifies how the baseline's stream is produced is judged by a paired comparison against the baseline on the objective the candidate actually claims (Sharpe non-inferiority or improvement, drawdown, tracking, cost, capacity, reliability). Its standalone Sharpe is not admissible evidence for a modification claim.
5. **One family, one preregistration, every variant named.** A preregistration lists every variant, threshold, cell and secondary claim before the first computation, and states the family's multiplicity treatment (the repo's standing proposal is BH-FDR q = 0.10, carried as a challengeable default). A variant not named in the preregistration is a new attempt with a new record.
6. **Exposure is recorded by what was revealed, not by lane.** Every computation or read that reveals a strategy-variant outcome is an exposure event (§0B). Absence of a row means `UNKNOWN`, never `NONE`.
7. **Sample reuse is declared before running.** The ETF panel is burned 6 of 6 (KB `relationships.csv` rows 16–21, verified). The Databento commodity panel carries the carry study's frozen `N_trials = 14` (verified: `commodity-carry-research/preregistration/PREREGISTRATION.md` §10; `src/config.py` line 66). `SAMPLE_REUSE.md` in this program declares each reuse; the ledger extends per the governing convention (§0B). A shared record with `mean-reversion-research` is required for the Databento panel.
8. **Design lineage and validation evidence are recorded separately** (§0A). An exposed-sample origin is disclosed forever; it does not prevent later independent validation, and dependent historical evidence is never relabelled as independent.
9. **Kill branches must be reachable.** Every FULL decision rule is checked at A2 for reachability against the measurable range. A rule that cannot fail is rewritten before sealing.
10. **Stop rule and soft budget.** When a preregistered question is answered, the wave stops; further variants need a new declared question. Eight FULL preregistrations in the first twelve months is a soft workload budget; exceeding it needs Aaron's approval. It is not a multiplicity correction.
11. **Crisis preservation is claim-specific.** A crisis-preservation requirement applies when a candidate is intended to replace the deployed TSMOM stream while retaining its defensive role, or explicitly claims to preserve crisis behaviour. It does not apply to accounting reconciliation, contract-specification truth, feasibility facts, or diversifying lines that make no defensive claim; those report crisis behaviour and are judged at portfolio level. Any retention figure (the v1 proposal was 70%) is a proposed economic policy threshold that the designer must justify, the challenger may attack, and Aaron decides; it is not a scientific constant. The requirement must specify common risk scaling, fixed event windows, and the treatment of a small, zero or negative reference return.
12. **Redundancy is reviewed, not decreed.** High dependence between a candidate and any accepted stream triggers `HIGH_REDUNDANCY_REVIEW` covering monthly PnL correlation, rolling dependence, tail dependence, drawdown overlap, position-level overlap, cost, capacity, tracking, operational reliability, implementation simplicity and marginal book contribution. High correlation restricts claims of *independence*; it does not prove two candidates are one alpha source, and it imposes no automatic `not_promoted` and no universal prohibition on a separate line unless Aaron adopts such a cap as explicit portfolio policy.
13. **Nonsignificance is not falsification.** A result is `premise not confirmed` / `not_promoted`, `unresolved`, materially ruled out to a justified margin, or `falsified` only under the KB's decisiveness convention (multiple independent decisive tests; prefer `not_promoted` when in doubt — README, verified). "CI includes zero" alone establishes neither absence nor robustness nor equivalence; equivalence and non-inferiority claims require explicit margins declared before the run.
14. **Strategy-build gate.** No strategy construction begins on the strength of a premise pass, a completed Wave 0, or completed mechanical work. When a candidate first reaches genuine strategy-construction readiness, the session STOPS and surfaces `STRATEGY_BUILD_READINESS = READY` with `AARON_ACTION_REQUIRED = decide whether to authorise Opus to begin strategy construction`. Construction starts only on Aaron's separate yes.

---

## 0A. Evidence contexts and lineage

Evidence contexts describe *what a given test can support*. They are not a scalar status ladder, and one study can carry evidence in more than one context.

| Context | Definition | Can support | Cannot support |
|---|---|---|---|
| **T0 — exposed design sample** | The design or hypothesis was informed by outcomes observed on this sample | Hypothesis generation; retrospective descriptive evidence; explicitly dependent research evidence | Independent confirmation of a newly adapted performance claim. A later seal does not erase earlier exposure. |
| **T1 — same-period wrapper / instrument replication** | Same or materially overlapping economic history, different wrapper, instrument or implementation | Wrapper transfer; implementation and construction robustness; partial external validity. A narrowly scoped implementation fact may receive whatever status the canonical vocabulary permits (§10). | Automatic independent confirmation of an ETF-informed performance edge. `confirmed implementation_fact` never implies `confirmed` strategy performance. |
| **T2 — temporally separate historical replication** | Different historical periods | Stronger cross-period evidence when the design is fixed and researcher exposure, literature-derived design choices, construction and claim scope are disclosed | Independence by virtue of different dates alone |
| **T3 — accrued but protected historical holdout** | Data that has already occurred, with *verified* protection from outcome access | Held-out historical evidence | Prospective status. "No file was downloaded by this project" is insufficient; related-project access and outcome-informed market knowledge matter. |
| **T4 — prospective forward evidence** | Design, seal and access protocol precede the market outcomes | The strongest temporal protection available; potential confirmation subject to adequate evidence and applicable gates | Conclusiveness when the period is too short or imprecise |

**Design lineage is recorded separately from validation evidence.** Each candidate carries a design-lineage tag (for example `POST_EXPOSURE_DESIGN_ON_ETF_PANEL`, `ROBUSTNESS_GRID_INFORMED`, `CARRY_STUDY_INFORMED`) and, for each validation test it later runs, the evidence context of that test. The two are never merged. A candidate may therefore legitimately read:

`POST_EXPOSURE_DESIGN_ON_ETF_PANEL` + dependent ETF-panel evidence (T0) + same-period futures transfer evidence (T1) + later prospective confirmation (T4)

without any implication that the T0 or T1 evidence was independent, and without the T0 origin preventing the T4 confirmation.

---

## 0B. Exposure and trial model

Four objects, never merged:

| Object | Definition | Required fields / rules |
|---|---|---|
| **EXPOSURE_EVENT** | Any computation or read that reveals outcomes or measurements | Sample snapshot id; session; outputs actually revealed; classification token under the existing exposure vocabulary (`NO_OUTCOME` / `GENERATED_NOT_SEEN` / `REVEALED_AGGREGATE` / `REVEALED_TARGET_METRIC`, per the ledger normalisation rule already used in this workspace) plus a descriptive auxiliary field for the explanatory category below; seal timing relative to any contract; downstream design use (append-only link rows). Research-axis and reviewer-axis events are linked without double-counting trials. |
| **VARIANT_ATTEMPT** | Every distinct evaluated strategy configuration or selection opportunity | Immutable, one row each, with design parent and family. Never deleted, merged or consolidated after observing PnL correlation or any outcome. Exact reproduction of an already-recorded configuration is a provenance/re-exposure record, not automatically a new distinct variant. |
| **HYPOTHESIS_FAMILY** | The prospectively declared inferential and selection scope | Declared in the preregistration before any member runs, including bridge cells, secondary metrics, cost levels and per-cell claims. Family membership never deletes attempts. Grouping follows the actual selection process, not document labels. |
| **GOVERNED_N_TRIALS_CONTRIBUTION** | The attempt's contribution to the sample's cumulative `N_trials` | Follows the authoritative declared convention and cites it. **Databento panel (verified):** the carry preregistration §10 counts every distinct constructed strategy-return series (primary and robustness arms) as one trial and excludes diagnostics of an existing series; frozen at 14; a deviation that adds a series changes `N_trials` and forces DSR recomputation. New TSMOM series on that panel are appended under that convention, never recomputing history. **ETF panel:** no frozen convention exists (the core had no preregistration); the historical count and the treatment of the 45-cell grid are an **Aaron decision to be recorded in Wave 0**, not improvised here. One visible attempt is not automatically `+1`. |

**Explanatory exposure categories** (used in the auxiliary field; they are not new canonical enum values and may overlap — a performance exposure can also be design-informing):

| Category | Examples |
|---|---|
| `PURE_MECHANICAL_VERIFICATION` | accounting identity; multiplier and price-unit correctness; causality; deterministic reconciliation residual; truncation invariance |
| `DESIGN_INFORMING_MEASUREMENT` | roll-schedule structure; contract availability; signal agreement rates; feasibility at NAV; descriptive structure that influences a later contract |
| `TARGET_PERFORMANCE_EXPOSURE` | return series; Sharpe; ΔSharpe; drawdown; crisis return; Calmar; strategy-performance CI — including a historical PnL series displayed while reconciling it |

Classification is by *actual outputs*, not by lane or intent. Activity type, outcome exposure and downstream design use are kept separately identifiable.

**Historical 45-cell grid.** Its treatment inside the core's record (robustness, not selection; parameters unchanged) stays historically frozen and is not relabelled by this program. Later designs informed by its observed outcomes (X11, X12, X13, X33 in v1) carry `ROBUSTNESS_GRID_INFORMED` lineage, and each such use is appended as a link row. If source reconciliation later reveals an omission, it is documented through the authorised correction process; history is not rewritten.

**Cross-project rule.** Exposure and attempts travel with the sample, not the folder. One authoritative dataset-level record, with project references, is the shared source; project-level files are views or linked records, never competing totals.

---

## 0C. Result-state vocabulary

| State | Meaning | Legal recording |
|---|---|---|
| Premise not confirmed | The declared premise contrast did not clear its declared gate | `not_promoted`, reason `premise_not_confirmed` |
| Unresolved / insufficient precision | The interval neither clears the gate nor excludes the declared margin | `unresolved` |
| Materially ruled out | The interval excludes the declared SESOI / equivalence margin | `not_promoted` with the margin recorded; `falsified` only under the decisiveness convention |
| Preservation / equivalence supported | The paired interval lies inside the declared margin | the claim's status per §10 |
| Falsified | Multiple independent decisive tests, nothing material untried | strategy-level `falsified` (Finding level has no such value) |

---

## 1. Seat routing

| Stage | Seat | Rule |
|---|---|---|
| A Design | Opus | Proposes and justifies hypothesis, SESOI / margins, decision rules, family, inference scheme, preregistration text. Owns every threshold. |
| A2 Pre-seal challenge | **fresh GPT-6 Astra session** | Challenges reachability, SESOI–metric scale, hidden degrees of freedom, sample assumptions, inference design, kill-branch reachability. Challenges; does not author the sealed contract. Re-run after any amendment. (The global routing file names a different Codex model for this seat; Aaron has designated GPT-6 Astra for this program.) |
| B Seal | Aaron | Adjudicates the challenge and authorises sealing. Approval is a decision, not evidence. |
| C Build, D Mechanical verify, E Evidence, F Internal analysis | Opus + tests | Truncation-invariance tests for every new causal primitive; reconciliation identities for every new PnL path; provisional classification only. Entered only after the §0 rule-14 build gate where strategy construction is involved. |
| G Adversarial audit | Fable | Risk-gated on QROS triggers only: futures roll/expiry and cost/price-unit logic (Wave 1); portfolio accounting changes (Wave 4); multiple-testing framework changes; any promotion or `falsified` decision. Read-only; repairs need separate authorisation; ≤ 3 workflows per wave. |
| H Repair | Opus | Confirmed defects only, with regression tests and a change label; separately authorised. |
| I Final verification | **new fresh GPT-6 Astra session** (never the A2 session) | Reads the preregistration's Lineage/Amendments first; reports independence per dimension. |
| Certification of adopted reviewer contributions | a **non-producing** fresh session that did not build the candidate and is not of the contributing reviewer's model family | Applies to any design element supplied by Astra and adopted by the designer. "Opus certifies" never means the builder of that candidate certifies its own work; "Aaron certifies" never means owner approval is independent evidence. |
| J–K Adjudication | Aaron | Disagreements are settled by tests and measurements. |
| L KB record | Opus (KB session) | Legal vocabulary only; negatives first-class. |
| Workflow assistant | ChatGPT (Aaron's separate use) | Interpreter, explanation, acceptance and stage-status coordination. Not a strategy author, parameter tuner, builder, or certifier. A user-workflow preference, not an independence claim. |

No reviewer chain beyond A2 and Stage I is created by this program.

---

## 2. Wave 0 — governance bootstrap (definition only; execution needs separate authorisation)

**Lane:** none (governance). **Preconditions (genuine governance prerequisites only):** acceptance of the §0A evidence rules, the §0B exposure/trial contract and the §0C result states; the lockbox semantics below; the §1 routing and provenance rules; the shared dataset-level ledger ownership rule (§0B); the inventory-task definition below; and Aaron's explicit authorisation of governance execution. **Not preconditions:** D1 and D2 (deferred acquisitions), D8 (`X09_ROUTE_PENDING_AARON`, candidate-specific), D9 (the X01 classification ceiling), the ETF-panel count decision itself (recorded as an open Aaron decision inside the ledger), and every candidate-specific detail (X14 contrasts, X19/X20 variables, X34 eligibility, X43/X44 bridge, X09 mechanics, X35/X36 acceptance parameters); those gate their own candidate stages.

Wave 0 scope, when authorised:

| Artifact / task | Content |
|---|---|
| `qros-state.yaml` | `research_id: TSMOM-EXT-001`; `lane: EXPLORATORY` (declared by Aaron); `workflow_stage: A`; `measurement_materiality: UNKNOWN`; `outcome_exposure` declared per scope with the two ledgers named in `inputs[]`; field conventions copied from the `mean-reversion-research` precedent (schema 17; quoted scalars; no trailing comments). |
| `ops/EXPOSURE_LEDGER.md` (research axis) | Header with the normalisation rule; historical rows: this map's v1 design session (target-metric read of published results); the six prior hypotheses and the 45-cell grid as frozen historical attempts with their classification; Astra Rounds 1–2 as reviewer-axis rows (target-metric read of the map's published numbers). |
| `ops/REVIEWER_EXPOSURE_LOG.md` (seat axis) | Header; rows linked to the research-axis rows above without double-counting. |
| `research/extensions/SAMPLE_REUSE.md` | ETF panel 7th+ reuse (rows 16–21); Databento reuse under the verified §10 convention with the shared record with `mean-reversion-research`; lockbox rule. |
| `research/extensions/TRIAL_LEDGER.md` | The four-object record (§0B) as one dataset-level authoritative index with project references; the Databento baseline of 14 preserved; the ETF-panel historical count recorded as **Aaron's decision**, with the options and the c1 `SAMPLE_REUSE.md` reasoning cited. |
| Lockbox procedure | Per dataset: snapshot identity and hash; verified last date; incomplete-period handling; refresh protocol (a refresh writes a new snapshot with its own hash and never overwrites the frozen panel; a refresh that revises historical adjusted prices is a new dataset); protected paths; release rule (an opening is an exposure event that burns the holdout for that claim family); access lineage; the T3-vs-T4 classification of any accrued data. |
| Canonical verification tasks | Confirm from bytes the facts listed in §12 as `UNKNOWN_PENDING_WAVE0_VERIFICATION`; record them as verified or leave them `UNKNOWN`. Unverified facts block any dependent research gate. |
| Data-inventory specification (defined, not run) | Scope: the whole `Quant trade` workspace; known external roots such as `C:\Users\Aaron\quant-data`; prior vendor purchases; vendor entitlements and download manifests. Fields: instruments, exchanges, date coverage, schemas, contract definitions, open-interest availability, raw vs continuous series, units, provenance, licensing, known prior research exposure. Access boundary: catalogues, manifests and metadata only; no protected performance outcome is opened. Output: an ownership table feeding D1/D2. Running it is a separately authorised task. |
| Registry and dashboard | `IDEA_REGISTRY_v2.csv` becomes the working candidate list once accepted; each candidate entering MEASUREMENT gets `research/extensions/<family>/<XNN>/HYPOTHESIS.md`. |
| KB cards | Deferred (D6): created when a candidate enters material research requiring them. |

**Gate to Wave 1:** ledgers exist with their historical rows; lockbox procedure declared; Wave-0 verification tasks either verified or explicitly `UNKNOWN` with their dependent gates blocked; Aaron authorises Wave 1 mechanical work separately.

---

## 3. Wave 1 — baseline anatomy, futures mechanical truth, matched wrapper transfer

No futures strategy-performance outcome is exposed before the X01 contract is sealed. The Fable audit trigger (roll, cost and price-unit logic) applies.

| Step | Item | Activity | Exposure classification (by outputs) | Notes |
|---|---|---|---|---|
| 1.1 | X07, X24, X45, X46 on published streams | Baseline anatomy | `TARGET_PERFORMANCE_EXPOSURE` (new decompositions and substream statistics of burned, published streams) and `DESIGN_INFORMING_MEASUREMENT` | Not fresh OOS evidence. "All crisis alpha is short-side" is a hypothesis X24/X46 test, not a premise. |
| 1.2 | X02a futures mechanical truth | Causal signal-input construction (one fixed ex ante among the causal options); contract and accounting identities; units; roll causality; dollar-ledger reconciliation; deterministic tests; sign-agreement rates between the ETF signal and the futures signal | `PURE_MECHANICAL_VERIFICATION` and `DESIGN_INFORMING_MEASUREMENT`. Any historical PnL series displayed during reconciliation is `TARGET_PERFORMANCE_EXPOSURE` and is logged as such; reconciliation is designed to report residuals, not series. | Invalid accounting is inadmissible for any PnL regardless of economic immateriality. |
| 1.3 | X05 feasibility | Contract counts, rounding error, margin-to-equity at the declared NAV grid (D3) | `DESIGN_INFORMING_MEASUREMENT` | Not a performance trial. |
| 1.4 | Pre-seal roll diagnostics (the structural part of v1's X03) | Roll dates, roll counts, open-interest crossover timing, contract availability under the A1 and calendar rules | `DESIGN_INFORMING_MEASUREMENT` | No ΔSharpe, no wrapper-performance comparison, no return series. |
| 1.5 | X01 contract | Opus proposes: the paired estimand for wrapper preservation; degradation tolerance / SESOI with its economic justification; the three outcome states; prospective precision assessed for the *paired* estimand (no transplanted marginal MDE, no shortcut multiplier); crisis and deployment diagnostics scoped to the deployment claim; declared secondary performance arms (construction sensitivity = former X02b; roll-rule sensitivity = former X03 performance arm); dependency-specific adjudication for X06/X12/X32/X43 under each outcome. Fresh Astra A2 challenges. Aaron authorises sealing. | — | The build gate (§0 rule 14) applies before any construction the contract requires. |
| 1.6 | X01 run | Primary A1 arm first and recorded; secondary arms after | First futures `TARGET_PERFORMANCE_EXPOSURE`; ledger appended under the verified convention (each distinct constructed strategy-return series) | Mechanical accounting failure is distinct from a valid negative wrapper result. |
| 1.7 | Review chain | Opus analysis → Fable audit (trigger applies) → repair if separately authorised → new fresh Astra Stage I (with disclosure of Astra-contributed contract elements and their non-Astra certification) → Aaron | — | A valid negative wrapper result does not automatically suspend futures trend research; Aaron adjudicates each dependency. |

**X01 outcome states:** `PRESERVATION_SUPPORTED` (the whole paired interval lies on the preserved side of the declared degradation boundary), `MATERIAL_DEGRADATION_SUPPORTED` (the whole interval lies beyond the boundary), `UNRESOLVED_INSUFFICIENT_PRECISION` (the interval straddles the boundary). Classification is against the declared boundary, never against zero — an interval containing zero is not by itself unresolved; the boundary is defined by the X01 contract, not here. The v1 rule comparing a futures interval that crosses zero with an ETF interval that does not is deleted: difference of significance is not significance of difference. The wrapper-performance comparison is an empirical result and is classified at recording (§10); it is never recorded as an implementation fact.

---

## 4. Wave 2 — breadth

| Step | Item | Control / route | Exposure |
|---|---|---|---|
| 2.1 | X06 premise | **Principal control: expanded 18-root futures universe vs the matched futures subset** (the c1 map's roots) under identical dates, identical futures construction, identical risk convention, fixed sleeve risk budget. ETF comparison secondary. Structural outputs: trend-PnL correlation matrix and effective number of bets. | Per-root trend-PnL streams are `TARGET_PERFORMANCE_EXPOSURE`; logged. |
| 2.2 | X06 FULL (if the structural premise warrants it) | Baseline + expanded sleeve at the fixed budget vs baseline with the matched subset; paired Δ on the declared objective | Ledger appended |
| 2.3 | X09 | **`X09_ROUTE_PENDING_AARON`.** A = structural overlap / non-redundancy screen (does each proposed spread merely reconstruct outright exposures already held? position-level overlap only; no PnL) → sealed FULL. B = declared exploratory performance exposure → logged lead. Executable spread definitions (hedge ratios, leg notionals, financing and short cost, risk scaling) precede any performance test under either route. The structural screen establishes no alpha, no Sharpe, no low realised correlation and no portfolio benefit. | A: `DESIGN_INFORMING_MEASUREMENT`; B: `TARGET_PERFORMANCE_EXPOSURE` |
| 2.4 | X08 (budget permitting) | Generating 13 candidate streams and selecting on their correlations is design selection; all candidates and the inclusion decision are recorded | `TARGET_PERFORMANCE_EXPOSURE` |

---

## 5. Wave 3 — same-mechanism diversification

| Step | Item | Rule |
|---|---|---|
| 3.1 | X11a structural | Four speed-leg sub-strategies: return streams, correlations, drawdown overlap, crisis behaviour, turnover. `TARGET_PERFORMANCE_EXPOSURE`, logged. Lineage `ROBUSTNESS_GRID_INFORMED`. |
| 3.2 | X11b | Any leg-risk-balanced ensemble or altered strategy is FULL under its own sealed contract. X11a exposure is dependent evidence, never independent evidence for X11b. Build gate applies. |
| 3.3 | X16 | Four estimator sub-strategies; 4×4 dependence. Four Sharpes are exposed and logged. |
| 3.4 | X17 | FULL, conditional; EW ensemble primary, two declared secondaries. |
| 3.5 | X14 | Premise with two predeclared shape-sensitive contrasts (monotone; concave). Failure of both stops progression; it is not falsification. Multiplicity and the exact contrasts fixed at candidate design. |
| 3.6 | X18 | Six-cell premise; family grouping with X39 decided by the actual selection process (§11). |
| 3.7 | X12 | Futures panel only; replication of an exposed ETF fact; T1 context, dependent. |

---

## 6. Wave 4 — portfolio construction

| Step | Item | Rule |
|---|---|---|
| 4.1 | X26/X27 | Objective is robustness: an **equivalence / non-inferiority** formulation with a declared margin. "No significant difference" is not equivalence. Paired bootstrap. A positive Δ is a lead in T0. Fable trigger applies if the aggregator changes accounting. |
| 4.2 | X28 | Three fixed blends. Allocation-performance exposure, logged. A deployment allocation memo for Aaron, not a strategy. |
| 4.3 | X29 | Deferred until ≥ 2 sub-strategies have passed the §9 gate. |

---

## 7. Wave 5 — conditional alpha

| Step | Item | Family | Rule |
|---|---|---|---|
| 5.1 | X25 (X24 has moved to Wave 1) | 1 rule | Sleeve selection from X24 is outcome-informed; lineage preserved. Crisis preservation applies because X25 modifies the deployed stream's defensive side. |
| 5.2 | X43 → X44 | X43: pooled + 4 sectors + **one bridge cell** conditioned on the ambiguous-but-non-zero trend state (|score| = 0.5) testing the direction rule X44 actually contemplates | Ledger appended; shared record with MR. **Neutral-state carry (`CARRY_CONDITIONAL_ON_NEUTRAL_TREND_STATE`, score = 0) is outside X44's scope by choice and is recorded as DEFERRED / UNTESTED CONDITIONAL HYPOTHESIS — not falsified, not equivalent to the not-promoted unconditional carry sign, not a research commitment.** |
| 5.3 | X19/X20 | 4 (acceleration coefficient, age coefficient, 3×3 corner contrast, X20 tail cell; level is a covariate, not a counted test — governance choice B: the corner contrast is decision-bearing and counted) | Proposed definitions (acceleration = (z_t − z_{t−3}) × sign(score_t); age = consecutive months of the same non-zero sign, reset at zero) are candidate proposals for the normal design → challenge → decision process, not sealed methodology. |
| 5.4 | X21–X23 | 8 | Conditioning on published strategy returns is `TARGET_PERFORMANCE_EXPOSURE`; episode jackknife ranked above significance. |

Panel inference for every pooled asset-month premise (X14, X18–X23, X34, X39, X43): decided before the candidate runs; must preserve common calendar shocks, serial dependence, overlapping horizons where present, and the cross-sectional dependence relevant to the estimand; ~3,700 asset-months are not ~3,700 independent observations; no universal block-length rule; no post-result observed-power calculation.

---

## 8. Wave 6 — risk and execution

| Step | Item | Rule |
|---|---|---|
| 6.1 | X30 | Five execution-day variants; no selection; Sharpe, MDD and crisis outcomes exposed and logged; dispersion is the statistic. |
| 6.2 | X35a / X35b | X35a: estimator-stability diagnostic (its Sharpe or worst-month outputs remain exposed). X35b: sealed replacement study with a non-inferiority acceptance rule on the stated objective; the same historical sample is not fresh for it. |
| 6.3 | X36a / X36b | X36a: cap-binding diagnostic. X36b: vol-floor policy evaluation under its own contract. |
| 6.4 | X31 | FULL, single variant, paired. |
| 6.5 | X32 | FULL on the futures panel after Wave 1; two declared thresholds; tracking-error objective. |
| 6.6 | X33 | FULL, two declared variants; lineage `POST_EXPOSURE_DESIGN_ON_ETF_PANEL` (turnover split published) and `ROBUSTNESS_GRID_INFORMED` (§0B; lineage link only). |
| 6.7 | X34 | Premise with a comparable forward horizon and a clearly defined eligible-event population; any exclusion of late-period events changes the target population and must be justified; the horizon is fixed at candidate design, not here. |
| 6.8 | X37/X38, X39 | Budget permitting; episode jackknife for X37/X38. |

---

## 9. Line acceptance and deployment

Passing a premise creates no portfolio line. A candidate reaches final-book consideration only after its research path has produced an appropriately scoped evidence package. The admission review covers:

- claim status and the evidence context of each supporting test (§0A), with design lineage disclosed;
- position-level overlap with Line 1 and every admitted line;
- PnL dependence (monthly, rolling, tail);
- drawdown and crisis overlap;
- marginal combined-book evaluation at fixed total risk;
- implementation, cost, capacity and operational considerations;
- Aaron's decision.

A `supported` historical result does not mean independently validated, and neither `supported` nor `confirmed` means authorised for live deployment. Deployment authorisation is a separate owner decision. Strategy construction for any line is itself gated by §0 rule 14.

---

## 10. Status vocabulary (verified from canonical bytes on 2026-09-08)

| Item | Verified content | Source |
|---|---|---|
| Legal `research_status` (strategy) | `confirmed, supported, not_promoted, falsified, active, archived, experimental, unresolved` | `schemas/strategy.schema.yaml` line 29 |
| Legal `claim_status` (finding) | `confirmed, supported, partially_supported, unresolved, contradicted, retired, not_promoted` — no `falsified` at Finding level | `schemas/finding.schema.yaml` line 29 |
| Legal `evidence_type` | `preregistered_primary, preregistered_robustness, preregistered_premise_test, out_of_sample, full_sample_fixed_parameter, lockbox, post_hoc_diagnostic, exploratory, implementation_fact, external_literature, researcher_interpretation` | `schemas/finding.schema.yaml` lines 30–43 |
| Gate G4 | `post_hoc_diagnostic, exploratory, researcher_interpretation, full_sample_fixed_parameter, external_literature` can never carry `claim_status: confirmed`; `implementation_fact` is **not** in the disallowed set | `src/quant_kb/validate.py` lines 116–133; `README.md` lines 96–100 |
| Definition of `implementation_fact` | "A fact about the code/system itself, not an empirical result." | `README.md` line 92 |
| Decisiveness convention | `falsified` only via multiple independent decisive tests with nothing material untried; `not_promoted` for single/simpler gate failures, premise failures, or untested sub-space; prefer `not_promoted` when in doubt; convention, not enforced by `validate.py` | `README.md` lines 135–150 |

Consequences encoded in V2:

- Mechanical identities (X02a: reconciliation, units, causality, multipliers, truncation invariance) may be recorded as `implementation_fact` and, when reproducibly verified, may carry `confirmed`. **This never implies a confirmed strategy-performance edge.**
- The X01 paired wrapper-performance comparison is an empirical result, not a fact about the code, and is **not** eligible for `implementation_fact`. Under G4 as verified, a sealed `preregistered_primary` finding is not barred from `confirmed`; but the README's stated rationale for the `full_sample_fixed_parameter` cap (no held-out window) applies in substance to a same-period comparison on price paths that informed the design. V2 therefore records the X01 performance claim at most as `supported` in context T1, and lists the stricter classification question under §12 as `CANONICAL_CLASSIFICATION_PENDING_VERIFICATION` for Aaron and the KB curator.
- Program classes map as: CONFIRMED → `confirmed` only with T3/T4 evidence (or an implementation fact as above); SUPPORTED → `supported`; NOT_PROMOTED → `not_promoted` (reasons include `premise_not_confirmed`, `redundancy_review_declined`, `materially_ruled_out_to_margin`); FALSIFIED → `falsified` under the decisiveness convention; UNRESOLVED → `unresolved`. There is no `insufficient_evidence`.

---

## 11. Family map (reconciled)

| Family | Members and cells | Multiplicity scope |
|---|---|---|
| F-X01 | primary A1 arm; secondary arms: calendar roll, construction sensitivity | one contract; secondaries declared |
| F-X06 | structural premise; FULL paired Δ | one contract |
| F-X09 | route A: structural screen (no inference); route B or FULL: composite claim + 4 per-spread claims + marginal claim = 6 declared claims | one family |
| F-X11 | X11a structural (no inference); X11b one ensemble | one contract |
| F-X14 | 2 shape contrasts on |score| levels and |z12| deciles | one family |
| F-X16/X17 | X16 descriptive; X17 EW primary + 2 secondaries | one family of 3 |
| F-X18 and F-X39 | each 6 cells; **grouped into one 12-cell family if a single selection step chooses among them; separate only if run as separately sealed, non-competing contracts** — decided at candidate design | per decision |
| F-X19/X20 | acceleration coefficient, age coefficient, 3×3 corner contrast, X20 tail cell = 4 (level is a covariate, not counted; the corner contrast is decision-bearing and counted — governance choice B) | one family |
| F-X21–X23 | 8 cells | one family |
| F-X24 | 5 sleeve contrasts | one family |
| F-X26/X27 | equal-sleeve, capped-sleeve, cluster-hierarchical = 3 equivalence tests | one family |
| F-X30 | 5 variants, no selection | descriptive; logged |
| F-X34, F-X37/X38 | X34: 6 cells; X37/X38: 2 states × 2 horizons + 1 = 5 | separate families unless one selection step spans them |
| F-X35/X36 | a-stages descriptive; b-stages one contract each | per contract |
| F-X43/X44 | pooled + 4 sectors + 1 bridge cell = 6; X44 one rule | one family |
| Secondary metrics and cost levels | declared inside each family; no "whichever passes" rule | — |

---

## 12. Verification status of facts used in V2

| Fact | Status |
|---|---|
| G4 disallowed set; `implementation_fact` not in it; its definition | VERIFIED from bytes (2026-09-08) |
| Legal `research_status`, `claim_status`, `evidence_type` enums | VERIFIED |
| Decisiveness convention for `falsified` | VERIFIED |
| Databento `N_trials = 14` and the counting convention | VERIFIED (`PREREGISTRATION.md` §10; `config.py` line 66) |
| ETF panel burned 6/6 | VERIFIED (`relationships.csv` rows 16–21) |
| Session-role independence and persist-to-file rules | VERIFIED (`session-conventions.md` §1, §4, §9) |
| Whether a sealed same-period wrapper comparison may be classified above `supported` | `CANONICAL_CLASSIFICATION_PENDING_VERIFICATION` (Aaron / KB curator) |
| ETF-panel historical trial count and 45-cell grid counting treatment | Aaron decision, Wave 0 |
| ETF cache last date (observed 2026-06-12 in orientation), partial-month construction of the last monthly row, Databento last date (2026-06-30 per manifest as reported) | `UNKNOWN_PENDING_WAVE0_VERIFICATION` as authoritative snapshot facts |
| Exposure status of any data after the cache boundary (related-project access, market knowledge) | `UNKNOWN_PENDING_WAVE0_VERIFICATION` |
| Financial-futures ownership | not established as owned in the available orientation; inventory pending |
| Fable Round-1 response hash | not known to this session |
| Astra Round-2 artifact hash | `0a89d439…579869` — declared authoritative by Aaron 2026-09-08; recomputed and MATCHED (transport reconciliation, D0 closed) |

---

## 13. Next actions

1. CLOSED 2026-09-08: Aaron declared the Astra Round-2 hash authoritative; it was recomputed and matched; no architecture change was made in the reconciliation pass.
2. Fresh GPT-6 Astra document-only verification of this draft and of `TSMOM_EXTENSION_RESEARCH_MAP_v2.md`.
3. Aaron authorises Wave 0 execution once the genuine governance prerequisites in §2 are accepted (evidence, exposure and trial rules; lockbox semantics; routing and provenance; shared-ledger ownership; inventory-task definition). Deferred acquisitions (D1, D2), the candidate-specific X09 route (D8), the X01 classification ceiling (D9), the ETF-panel count decision (recorded as open inside the ledger) and future candidate thresholds do **not** block this authorisation.
4. Only then: Wave 0 execution by an Opus builder session, governance artifacts only; the strategy-build gate (§0 rule 14) remains closed.

`WAVE_0_EXECUTED = NO` · `WAVE_1_EXECUTED = NO` · `STRATEGY_BUILD_STARTED = NO` · `FULL_ALPHA_TESTING_STARTED = NO` · `PROTECTED_FORWARD_DATA_OPENED = NO` · `NEW_DATA_PURCHASED = NO`
