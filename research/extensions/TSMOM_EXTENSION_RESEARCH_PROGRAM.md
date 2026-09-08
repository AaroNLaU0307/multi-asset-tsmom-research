# TSMOM Extension Research Program — staged execution plan

**Companion to:** `TSMOM_EXTENSION_RESEARCH_MAP.md` (hypothesis IDs `X01`–`X46` are defined there and not repeated here).
**Status:** PROPOSAL. Nothing in this plan is authorised until Aaron decides the items in the map's Section K. Wave order may change on evidence; the ledger and lane rules may not.
**Date:** 2026-09-08 · **Author seat:** Claude Fable 5.1 (invoked directly; the default architect seat is Opus 5).

```ini
RECOMMENDED_MODEL=Claude Fable 5.1 (as invoked)
EFFORT_INTENT=VERY_HIGH
RECOMMENDED_EFFORT=xhigh
ROLE=research architect — program design only
WINDOW=NEW_TOP_LEVEL_SESSION
MUST_NOT_BE=builder or certifier of any wave in this program
LANE=EXPLORATORY
OUTCOME_EXPOSED=TARGET_METRIC (published results read; no new computation)
PREREG_SEALED=N/A
```

---

## 0. Ground rules that apply to every wave

1. **The baseline is frozen.** `multi-asset-tsmom-research` HEAD `c63114a` (`config.py`, `universe.py`, `src/{signals,sizing,portfolio,performance,validation}.py`) is the reference strategy. Extension code lives under `research/extensions/<family>/` and imports the engine; it never edits it. A better historical point estimate is not a reason to change the baseline.
2. **Three lanes, three kinds of claim.** EXPLORATORY emits hypotheses and leads; MEASUREMENT emits implementation facts and premise results; FULL emits promotion/falsification under a sealed preregistration. No lane may borrow another's vocabulary.
3. **Premise before PnL.** Every conditional or overlay hypothesis passes a descriptive premise test before any strategy PnL is fit. A failed premise is a finished result (`not_promoted`, reason `premise_not_confirmed`), recorded permanently.
4. **Paired, not standalone.** Any candidate whose estimated correlation with the baseline is ≥ 0.85 (map Section E, tier M) is judged only by a paired-difference bootstrap against the baseline (Δ-Sharpe, Δ-Calmar, Δ-skew, crisis retention, turnover Δ). Its standalone Sharpe is not admissible evidence.
5. **One family, one preregistration, every variant named.** A preregistration lists every variant, threshold and cell before the first computation. BH-FDR q = 0.10 within a family; Deflated Sharpe at FULL with the sample's cumulative `N_trials`. A variant not named in the preregistration is a new hypothesis with a new cycle.
6. **Exposure is recorded even when the ledger does not move.** Any computation that reveals a strategy-variant Sharpe, CI or return series on a sample is appended to `ops/EXPOSURE_LEDGER.md` (research axis). Reviewer-seat exposures go to `ops/REVIEWER_EXPOSURE_LOG.md`. Absence of a row means `UNKNOWN`, never `NONE`.
7. **Sample reuse is declared before running.** The ETF panel is burned 6/6; the Databento panel carries `N_trials = 14`. `SAMPLE_REUSE.md` in this program declares each reuse and extends the ledger when a performance trial runs. A shared ledger with `mean-reversion-research` is required for the Databento panel.
8. **Confirmation lives off the design sample.** Anything designed with knowledge of the ETF panel's published results (every `POST-EXPOSURE DESIGN` entry in the map) can be *confirmed* only on the futures panel, on acquired history, or on forward accrual. On the ETF panel it can only be a lead.
9. **Kill branches must be reachable.** Every FULL preregistration's decision rule is checked at Stage A2 for reachability against the measurable range (the `c1-drag-audit` lesson: a rule whose kill sat 19× above the measured value). A rule that cannot fail is rewritten before sealing.
10. **Stop rule.** When a preregistered question is answered, the wave stops. More variants require a new, declared question. A program-level cap of **8 FULL preregistrations in the first 12 months** is proposed; exceeding it needs Aaron's approval.
11. **Crisis-alpha retention is a gate, not a metric.** Any modification of the baseline stream must retain ≥ 70% of the GFC-2008, COVID-2020 and calendar-2022 window returns (or the futures panel's COVID-2020 and 2022 windows) to be promotable, regardless of Sharpe.
12. **Redundancy control.** At FULL, every candidate reports correlation with the baseline and with every previously accepted derivative (monthly, rolling 36-month, drawdown-episode Jaccard, crisis co-sign, tail-decile correlation). ≥ 0.9 with an accepted stream → `not_promoted (redundant_same_pnl_source)` unless paired Δ excludes zero and the candidate is cheaper to run.

---

## 1. Seat routing (QROS v2.0.1 canonical FULL chain)

| Stage | Seat | Effort | Notes |
|---|---|---|---|
| A Design (hypothesis, SESOI, decision rules, preregistration) | Opus 5 | High (Xhigh for futures-accounting waves) | This map's author does not write sealed preregistrations |
| A2 Pre-seal challenge | Sol, **fresh top-level session** | High | Challenges; does not author. Reachability, SESOI–metric scale, hidden DoF, sample assumptions |
| B Seal | — | — | Before any target-metric exposure on the study sample |
| C Build + D Mechanical verify | Opus 5 + tests | High / Xhigh | Truncation-invariance tests for every new causal primitive; reconciliation identities for every new PnL path |
| E Evidence + F Internal analysis | Opus 5 | High | Provisional classification only |
| G Adversarial audit | Fable 5.1 | High (Xhigh for promotion) | **Risk-gated**: triggers that apply here — futures roll/expiry and cost/price-unit logic (Wave 1), portfolio accounting changes (Wave 4), multiple-testing framework changes (Wave 0), any promotion or `falsified` decision. Read-only; repairs need separate authorisation. Budget ≤ 3 workflows per wave, default 3 total. |
| H Repair | Opus 5 | High | Confirmed defects only, with regression tests and a §5 change label |
| I Final verification | Sol, **new** fresh session (never the A2 session) | High / Xhigh | Reads the preregistration's Lineage/Amendments first; reports independence per dimension |
| J–K Adjudication | Aaron | — | Disagreements settled by tests and measurements, never by which model sounds more convincing |
| L KB record | Opus (KB session) | High | Findings in legal vocabulary; negatives recorded as first-class |

Routine engineering inside a wave (adapters, tests, plots) is `ROLE=builder`, Opus, no mandatory review. MEASUREMENT-lane premise tests need Opus + deterministic validation; a Sol check only when the measurement feeds a FULL design.

---

## 2. Wave 0 — Governance bootstrap (no research)

**Lane:** none (governance). **Requires:** Aaron's decision D4 (and D5) from the map. **Effort:** one Opus session.

Deliverables, all in `multi-asset-tsmom-research/`:

| Artifact | Content |
|---|---|
| `qros-state.yaml` | `research_id: TSMOM-EXT-001`; `lane: EXPLORATORY` (declared by Aaron); `workflow_stage: A`; `measurement_materiality: UNKNOWN` until first measurement; `outcome_exposure.declared: TARGET_METRIC` for HISTORICAL_CUMULATIVE (the published core results), scope-split per the `mean-reversion-research` precedent; pointers to both ledgers in `inputs[]`. Copy the field conventions from `mean-reversion-research/qros-state.yaml` (schema 17; double-quoted scalars; no trailing comments). |
| `ops/EXPOSURE_LEDGER.md` | Header block with the normalisation rule (`CLASSIFICATION_COLUMN_IS_CANONICAL`); row 1 = this map's design session (`REVEALED_TARGET_METRIC`, read-only, 2026-09-08); rows for every published artifact class already exposed (core, sleeves, robustness grid, cost sweep, RP control, overlays). |
| `ops/REVIEWER_EXPOSURE_LOG.md` | Empty seat ledger with header. |
| `research/extensions/SAMPLE_REUSE.md` | Declares: ETF panel 7th+ reuse (cite `relationships.csv` rows 16–21); Databento panel reuse with the `N_trials = 14` ledger to be extended at the first performance trial; shared-ledger arrangement with `mean-reversion-research`; the forward-accrual lockbox rule (D5). |
| `research/extensions/TRIAL_LEDGER.md` | The program's multiple-testing ledger: one row per strategy-variant Sharpe computed on a sample, with family, lane, sample, exposure class, and whether it counts toward `N_trials` for DSR. **Freeze the ETF-panel historical count convention here** (six hypotheses; the 45-combination robustness grid counted as robustness, not selection, with the c1 `SAMPLE_REUSE.md` reasoning cited) and never revisit it. |
| `research/extensions/idea_registry/` | `IDEA_REGISTRY.csv` (delivered with this map) becomes the authoritative candidate list; each candidate that enters MEASUREMENT gets its own `research/extensions/<family>/<XNN>/HYPOTHESIS.md`. |
| `research/extensions/DASHBOARD.md` | Delivered skeleton; updated at every wave close. |
| KB cards (D6, optional now) | Hypothesis cards for X01 (extends the existing `hypothesis.tsmom.futures-transfer`), X06, X09, X11, X16, X24, X43 — in a KB session, Opus, with `origin_type: ai_inferred`, `adversarial_review` pending. |

**Gate to Wave 1:** ledgers exist; lockbox rule declared; `qros status` (or the manual equivalent) reports no derived-value inconsistencies.

---

## 3. Wave 1 — Futures truth and edge diagnostics

**Purpose.** Establish what is true about the baseline and about the futures wrapper before any alpha idea is tested. **Lane:** MEASUREMENT (X02, X03, X05, X07, X45, X46) and one FULL (X01). **Sample:** Databento commodity panel (first TSMOM trial; ledger extends) and published ETF streams (read-only). **Fable trigger applies** (futures roll/cost/price-unit logic).

| Step | Item | Seat | Output | Gate |
|---|---|---|---|---|
| 1.1 | X45, X46, X07 diagnostics on published streams | Opus (builder) | `research/extensions/diagnostics/EDGE_DIAGNOSTICS.md` + CSVs | Reconciles to `output/monthly_returns.csv` at ≤ 1e-6 |
| 1.2 | X02 signal-price construction truth: chained held-contract index, dollar-ledger reconciliation, sign-disagreement rates; reuse `commodity-carry-research/src/{roll,returns,costs}.py`; apply the price-unit divisor; tests: truncation invariance, roll monotonicity, reconciliation identity, unit specs | Opus (Xhigh) | `research/extensions/futures_migration/infra/` + `FUTURES_INFRA_TRUTH.md` | All identities hold; no back-adjusted series anywhere in a PnL path |
| 1.3 | X03 roll-rule sensitivity | Opus | section in `FUTURES_INFRA_TRUTH.md` | Immaterial → A1 fixed; material → roll rule becomes a declared DoF in every futures prereg |
| 1.4 | X05 discrete-contract feasibility at the NAV set (D3) | Opus | `research/extensions/execution/CONTRACT_FEASIBILITY.md` | Feasibility bars met at the deployment NAV, or universe/NAV revised before X01's FULL |
| 1.5 | X01 preregistration (Opus) → **fresh Sol A2** (reachability, SESOI vs the ≈0.6 sleeve MDE, crisis-window definitions on a no-GFC panel) → seal → build → run → Fable audit (trigger: roll/cost) → repair → **new fresh Sol Stage I** → Aaron | full chain | `research/extensions/futures_migration/X01/{PREREGISTRATION,PREMISE_RESULTS,FULL_RESULTS}.md` | Verdict in KB vocabulary; ledger extended; `hypothesis.tsmom.futures-transfer` card updated |

**Wave-1 close.** Synthesis note: what the edge is (X45/46/07), whether the commodity sleeve transfers (X01), and the measured — no longer estimated — correlations that replace Section E's priors. If X01 is `falsified`, Waves 2's futures arm is suspended and D1/D2 are re-evaluated by Aaron; the ETF-panel premise waves continue.

**Estimated effort.** 6–8 Opus sessions, 2 Sol sessions, ≤ 3 Fable workflows.

---

## 4. Wave 2 — Breadth

**Lane:** MEASUREMENT premises → conditional FULL. **Sample:** Databento (X06) and ETF panel (X09, X08). **Prerequisite:** Wave 1 step 1.2 (chained index).

| Step | Item | Gate to FULL | FULL design if passed |
|---|---|---|---|
| 2.1 | X06 premise: 18-root trend-PnL correlation matrix, ENB vs 4-ETF sleeve | ENB gain > 1 and sleeve corr < 0.9 | Baseline + expanded commodity sleeve at a **fixed ex-ante sleeve risk share**; paired Δ-Sharpe/Δ-Calmar; crisis retention (COVID, 2022); ledger extends |
| 2.2 | X09 premise: four fixed spreads → corr with baseline, standalone CI, marginal Δ at 20% risk | corr < 0.7 and marginal Δ > 0 | Same book, futures replication later; **no pair may be added** |
| 2.3 | X08 premise (budget permitting): dropped-ETF trend-PnL correlations | any name < 0.6 with all anchors | Lead only on the ETF panel; carried to the futures universe design |

**Redundancy check at wave close:** X06 and X09 streams vs baseline and vs each other.

**Estimated effort.** 3–5 Opus sessions; Sol A2 + Stage I for each FULL.

---

## 5. Wave 3 — Same-mechanism diversification

**Lane:** MEASUREMENT (X11, X16, X14, X18) → conditional FULL (X17, X15, X12). **Sample:** ETF panel (leads) with futures replication for any FULL. Every sub-strategy Sharpe computed here is a recorded exposure.

| Step | Item | Gate | Conditional FULL |
|---|---|---|---|
| 3.1 | X11: four speed legs as sub-strategies — correlations, drawdown-overlap Jaccard, crisis split, turnover | any fast–slow corr < 0.8 and Jaccard < 0.8 | Leg-risk-balanced ensemble vs baseline, paired Δ-Calmar/Δ-Sortino; confirmation on futures/forward (`POST-EXPOSURE DESIGN`) |
| 3.2 | X16: four estimators as sub-strategies — 4×4 correlations | any pair < 0.85 | X17 EW ensemble (primary), median, majority (BH-FDR across 3) |
| 3.3 | X14: \|score\| and \|z12\| deciles → forward risk-adjusted return | monotone or hump with Spearman CI excluding 0 | X15 one mapping, paired |
| 3.4 | X18: ER tercile × sign, 6 cells | ≥ 1 cell clears BH-FDR + magnitude + stability | one conditioning rule, paired |
| 3.5 | X12 (futures only, after Wave 1): {1,3,6,12} vs {3,6,12}, paired | — | replication of an exposed fact; never on the ETF panel |

**Estimated effort.** 4–6 Opus sessions.

---

## 6. Wave 4 — Portfolio construction

**Lane:** FULL (paired controls) and MEASUREMENT. **Sample:** ETF panel. **Fable trigger applies** if portfolio accounting code changes (a sleeve-level aggregator is a new accounting path).

| Step | Item | Note |
|---|---|---|
| 4.1 | X26/X27: equal-sleeve, capped-sleeve (35%), cluster-hierarchical — **paired** Δ-Sharpe/Δ-MDD bootstrap | The null ("indistinguishable") is the robustness result; a positive Δ for equal-sleeve is a lead, confirmed only on futures/forward |
| 4.2 | X28: three fixed blends with the long book | Deployment allocation memo for Aaron; not a strategy |
| 4.3 | X29 | Remains deferred unless ≥ 2 sub-strategies were promoted in Waves 2–3 |

**Estimated effort.** 2–3 Opus sessions.

---

## 7. Wave 5 — Conditional alpha

**Lane:** MEASUREMENT premises with jackknife → conditional FULL. **Samples:** ETF panel (X24, X19–X23), Databento (X43). All premises here are BH-FDR families with the episode jackknife ranked above significance where the conditioning state is slow.

| Step | Item | Family size | Conditional FULL |
|---|---|---|---|
| 5.1 | X24 long/short decomposition by sleeve | 5 | X25 one asymmetric rule (0.5× short in confirmed sleeves) with the crisis-retention gate; confirmation off-panel |
| 5.2 | X43 carry–trend 2×2 sort on 18 roots | 5 (pooled + 4 sectors) | X44 tie-break rule, paired vs commodity-sleeve baseline; ledger extends; shared ledger with MR |
| 5.3 | X19/X20 acceleration, age, exhaustion | 3 | one rule, paired |
| 5.4 | X21–X23 breadth / dispersion / concentration states | 8 | one rule, paired; futures/forward confirmation |

**Estimated effort.** 4–6 Opus sessions.

---

## 8. Wave 6 — Risk and execution

**Lane:** MEASUREMENT (X30, X35, X36, X37/38, X39) and FULL-lite (X31, X32, X33, X34). **Samples:** ETF daily panel; Databento for X32.

| Step | Item | Note |
|---|---|---|
| 6.1 | X30 execution-day robustness (5 variants, no selection) | Prerequisite for any live deployment; dispersion is the statistic |
| 6.2 | X35 vol-estimator type (4 fixed) + X36 cap/floor | Judged by stability metrics only |
| 6.3 | X31 tranching; X33 signal smoothing (2 variants); X34 event-triggered re-evaluation premise | Paired; crisis retention; X33 is `POST-EXPOSURE DESIGN` |
| 6.4 | X32 contract-integer hysteresis on futures (2 thresholds) | After Wave 1; paired vs immediate rounding; tracking-error bar |
| 6.5 | X37/X38 own-state conditioning (jackknife) ; X39 high-vol tercile | Budget-permitting; the episode count is the binding constraint |

**Estimated effort.** 4–5 Opus sessions.

---

## 9. What the deployment book looks like at the end (the objective)

Not "Sharpe 2.0." The target is a small set of **independently validated return streams** plus a documented set of **falsified extensions**:

- Line 1: the baseline TSMOM stream — on futures where the wrapper transfers (X01/X04), on ETFs where no futures exist (credit, REITs).
- Line 2 (if X06 passes): expanded commodity breadth at a fixed sleeve budget.
- Line 3 (if X09 passes): spread trend.
- Line 4 (if X11 passes): the fast-leg sub-strategy, risk-balanced against the slow legs.
- Line 5 (if X43 passes): carry-conditioned commodity trend.
- A long risk-premium book blended per X28, sized by Aaron.

Allocation across lines only after ≥ 2 exist (X29). For every promoted line the dashboard records: standalone net Sharpe and CI, OOS/forward Sharpe, Sortino, MDD, turnover, cost breakpoint, correlation to baseline and to every other line, marginal portfolio Sharpe, key failure mode, and the final decision — and for every falsified line, the mechanism of failure.

---

## 10. Promotion classes → KB vocabulary

| Program class | KB `research_status` / `claim_status` | Condition |
|---|---|---|
| CONFIRMED CORE | `confirmed` | Preregistered evidence on a sample the design did not see (futures panel for ETF-designed ideas; acquired history; forward accrual). Not reachable on the burned ETF panel — the core itself is only `supported`. |
| SUPPORTED | `supported` | Preregistered positive on the design sample with all gates, or replication with a wide CI |
| NOT_PROMOTED | `not_promoted` | Fails a gate, premise not confirmed, or `redundant_same_pnl_source` |
| FALSIFIED | `falsified` | Multiple decisive independent tests (README decisiveness convention); prefer `not_promoted` when in doubt |
| UNRESOLVED | `unresolved` | Conflicting or insufficient evidence; never `insufficient_evidence` |

---

## 11. Immediate next actions (in order)

1. Aaron decides D1–D7 (map Section K). D4 and D5 are blocking; D1–D3 shape Wave 1's scope.
2. Opus session (`ROLE=builder`, High): Wave 0 artifacts; `python -m pytest -q` still 101 passing; nothing in `src/` or `config.py` touched.
3. Opus session (`ROLE=builder`, High): Wave 1 steps 1.1–1.4 (measurements), with tests.
4. Opus session (`ROLE=designer`, Xhigh): X01 preregistration draft → fresh Sol A2 → Aaron seals.
5. Only then: X01 build and run.
