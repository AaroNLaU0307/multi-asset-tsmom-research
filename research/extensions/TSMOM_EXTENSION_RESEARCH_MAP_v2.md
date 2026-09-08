# TSMOM Extension Research Map — v2 (converged draft)

**V2 status:** PROVISIONAL REVIEWABLE DRAFT, 2026-09-08, produced under Aaron's authorisation to draft the amended architecture only. It authorises nothing: no Wave 0 execution, no Wave 1, no strategy construction, no backtest, no FULL study, no data acquisition, no opening of protected outcomes, no forward-data release, no change to the frozen baseline. Next gate: fresh GPT-6 Astra document-only verification.
**V1 originals (immutable review history):** `TSMOM_EXTENSION_RESEARCH_MAP.md` SHA256 `76b902ed6e244fd2bb8293c1a55191c8b468759fcd5b1eeda7d10465be1d15f5`; `TSMOM_EXTENSION_RESEARCH_PROGRAM.md` SHA256 `7495faa976357592f50243e4f6b0342d557cc47193be85df938ee8e26b79040b`.
**Governing review artifact:** GPT-6 Astra Round 2 ("CONDITIONAL CONVERGENCE"), chat-carried and persisted verbatim at `review_history/ASTRA_ROUND2_CONVERGENCE_2026-09-08.md`, SHA256 `0a89d43919813eee302863eb642571347370e374c7966c9a81303dc9e0579869` — **PIN_STATUS = AUTHORITATIVE_MATCHED** (declared authoritative by Aaron on 2026-09-08, closing D0; recomputed and matched in a transport-reconciliation pass with no architecture change; the persisted file is unmodified, so its own header line still reads "pending" — those bytes are the pinned bytes). Authority order for reconciling text: Aaron's instructions → Astra Round 2 → accepted Fable Round-1 amendments → accepted Astra Round-1 findings → v1.
**Provenance of adopted reviewer contributions:** the evidence-context model and the separation of design lineage from validation evidence, output-based exposure classification, claim-specific crisis scope, the redundancy-review reframing, the three-state X01 contract form, the X44 logical correction, the X09 structural-screen naming and the X35/X36 stage split were supplied or materially shaped by GPT-6 Astra and are adopted here by the architecture author. At each candidate's preregistration the design owner (Opus) formally adopts and justifies any it uses; certification of elements resting on them follows Program v2 §1 (non-producing session, not of the contributing family); Aaron's approval is adjudication, never independent evidence. The governance rules referenced below (evidence contexts §0A, exposure and trial model §0B, result states §0C, routing §1) live in `TSMOM_EXTENSION_RESEARCH_PROGRAM_v2.md`.

**Project:** `multi-asset-tsmom-research` — extension program ("TSMOM-EXT")
**Baseline (frozen reference):** repo HEAD `c63114a06275c782b5835f219b14c17f1b33cd80`, 101 tests passing (re-run 2026-09-08 in this session: `101 passed in 11.90s`)
**Document status:** EXPLORATORY-lane design artifact. Nothing in this document is evidence. No computation was run to produce it; every number quoted is read from the repo's committed reports or the knowledge base and is cited to its source.
**Date:** 2026-09-08
**Author seat:** Claude Fable 5.1, invoked directly by Aaron for this task.

```ini
RECOMMENDED_MODEL=Claude Fable 5.1 (as invoked; the default architect seat under ~/.claude/CLAUDE.md is Opus 5)
EFFORT_INTENT=VERY_HIGH
RECOMMENDED_EFFORT=xhigh
EXECUTION_MODE=STANDARD
ROLE=research architect — hypothesis inventory + staged program design (no build, no test runs)
WINDOW=NEW_TOP_LEVEL_SESSION
MUST_NOT_BE=sole certifier of any FULL result in this program; author of a sealed preregistration without a fresh GPT-6 Astra A2 challenge; modifier of the frozen baseline; Wave-0 executor; strategy builder; verifier of this draft
LANE=EXPLORATORY
OUTCOME_EXPOSED=TARGET_METRIC (read-only: the published full-sample core, sleeve, robustness-grid and overlay results were read during design; no new outcome was generated)
PREREG_SEALED=N/A
WHY_THIS_MODEL=Aaron invoked Fable directly. Recorded as a departure from the default Opus architect seat, not a silent substitution.
```

**Exposure statement.** The designer of this map has read every published full-sample result of the core and its overlays (Sharpe 0.75, sleeve attributions, the 45-combination robustness grid, the cost sweep, the drawdown diagnostic). Several hypotheses below are therefore *partly informed by exposed outcomes*. Each such case carries a **design-lineage tag** in its entry (`POST_EXPOSURE_DESIGN_ON_ETF_PANEL`, `ROBUSTNESS_GRID_INFORMED`, `CARRY_STUDY_INFORMED`). Design lineage is recorded separately from validation evidence (Program v2 §0A): an exposed origin is disclosed forever, dependent historical evidence is never relabelled as independent, and the origin does not prevent later independent validation in contexts T2–T4. The research-axis exposure ledger for this project does not yet exist (Wave 0 defines it); this document's v1 design session, and the Astra reviews that read its published numbers (reviewer axis), are the first rows it must record.

**Companion documents (same directory):**
- `TSMOM_EXTENSION_RESEARCH_PROGRAM_v2.md` — the staged execution plan (Waves 0–6), evidence contexts (§0A), exposure and trial model (§0B), result states (§0C), seat routing (§1), family map (§11), verification status (§12).
- `idea_registry/IDEA_REGISTRY_v2.csv` — one machine-readable row per hypothesis (IDs `X01`–`X46`; stage splits a/b under stable IDs).
- `DASHBOARD_v2.md` — one row per candidate; all rows are `PROPOSED` today.
- v1 companions (`TSMOM_EXTENSION_RESEARCH_PROGRAM.md`, `idea_registry/IDEA_REGISTRY.csv`, `DASHBOARD.md`) are preserved unchanged as review history.

---

## How to read this document

- **Hypothesis IDs** are `X01`–`X46`. Prefix `X` = extension candidate. IDs are stable; never renumber.
- **Lane at entry** is the QROS lane the first test runs in (`MEASUREMENT` for premise/structure tests, `FULL` only once a preregistration is sealed). An entry marked `DEFERRED` has no lane yet.
- **Estimated PnL correlation with the baseline** is a designer's prior, not a measurement. It is the single most important number for ranking, and Section E says why.
- **Falsification condition** is written so that a fresh A2 challenger can check kill-branch reachability. Thresholds marked *(designer proposes; A2 challenges; Aaron decides)* are deliberately left to the preregistration stage; this document seals nothing and no reviewer authors a threshold.
- **Result states** follow Program v2 §0C: premise not confirmed → `not_promoted`; unresolved / insufficient precision → `unresolved`; materially ruled out to a declared margin → `not_promoted` with the margin; `falsified` only under the KB's decisiveness convention. "CI includes zero" alone establishes neither absence, robustness nor equivalence. Where an entry below says "stops progression", it means exactly that and not falsification.
- **Evidence contexts** (Program v2 §0A): T0 exposed design sample · T1 same-period wrapper/instrument replication · T2 temporally separate historical replication · T3 accrued-but-protected historical holdout · T4 prospective forward evidence. They describe what a test can support; they are not a scalar status ladder, and a candidate's design lineage is recorded separately from the context of each validation test it later runs.
- **Exposure classes** (Program v2 §0B, explanatory, not canonical enums): `PURE_MECHANICAL_VERIFICATION` · `DESIGN_INFORMING_MEASUREMENT` · `TARGET_PERFORMANCE_EXPOSURE`. Each entry's first test is classified by its actual outputs; a performance exposure can also be design-informing.
- Vocabulary follows the knowledge base (verified 2026-09-08, Program v2 §10): `confirmed · supported · not_promoted · falsified · unresolved`. High dependence with an accepted stream triggers `HIGH_REDUNDANCY_REVIEW` (Program v2 §0 rule 12), a review outcome recorded as `not_promoted` with reason `redundancy_review_declined` only when the review so concludes. There is no `insufficient_evidence` and no "lite" lane.

---

## Section A — What the existing TSMOM edge actually appears to be

Sources: `README.md`, `STUDY_SUMMARY.md`, `output/BACKTEST_REPORT.md`, `output/ROBUSTNESS_REPORT.md`, `output/COST_AND_TURNOVER_REPORT.md`, `output/RISK_PARITY_CONTROL_REPORT.md`, `research/diagnostic/DRAWDOWN_ATTRIBUTION_REPORT.md`, `research/crash_defense/PHASE0_SYSTEMIC_VERIFICATION.md`, KB card `strat.tsmom.multi-asset-core`.

### A.1 The mechanism as implemented

| Layer | Implementation (frozen) | Source |
|---|---|---|
| Universe | 17 ETFs / 5 sleeves: Equity SPY EEM EWJ XLE XLU · Bond TLT SHY LQD HYG · Commodity USO UNG GLD DBA · FX UUP FXY · RealEstate VNQ RWX. Screened from 30 by return-correlation clustering (`\|r\| ≥ 0.80` dropped), not by performance. | `universe.py`, `config.py` |
| Signal | Per asset, monthly: mean of `sign(R_1m), sign(R_3m), sign(R_6m), sign(R_12m)` on month-end closes → score ∈ {−1, −0.5, 0, +0.5, +1}. | `src/signals.py::signal_method_b` |
| Sizing | `w = score × 10% / σ_60d`, clipped to ±2.0. | `src/sizing.py::target_weights` |
| Aggregation | Equal-weight over available assets: `base_i = w_i / N_live`. | `src/portfolio.py::equal_weight_aggregate` |
| Portfolio risk | Scale book by `10% / σ_60d(base book)`; gross capped at 3.0×. | `src/portfolio.py::leverage` |
| Timing | Decision at month-end close, held the following month (`shift(1)`); truncation-invariance tested. | `src/signals.py`, tests |
| Costs | 2 bps one-way on `Σ\|Δposition\|`; sweep at 2/5/10/20. | `src/performance.py` |
| Data | yfinance adjusted close, 2007-04-18 → **2026-06-12** (cache); evaluation 2008-05 → 2026-06, 218 months. | `data/close_prices_raw.csv`, `output/monthly_returns.csv` |

Two properties of the frozen signal matter for the extension families and are easy to miss:

1. **The baseline is already a crude "continuous" signal and already a crude "multi-speed ensemble."** The score's magnitude is cross-horizon agreement (two levels, 0.5 and 1.0), and the four legs are averaged as *signs* before a single vol-scaling. Family 3 (speed) and Family 4 (continuous strength) therefore cannot be "add magnitude" or "add speeds"; they must be about *what the sign-averaging throws away* — the correlation structure between legs, and whether a finer magnitude carries information beyond two levels.
2. **The equal-weight aggregation encodes an accidental sleeve risk budget** by asset count: Equity 5/17 ≈ 29%, Bond 24%, Commodity 24%, FX 12%, RealEstate 12%. That budget was never chosen; it is a by-product of how many ETFs survived screening. Family 8 is really the question "does the result depend on this accident?"

### A.2 The evidence, stated at its true tier

| Claim | Number | Tier / caveat |
|---|---|---|
| Net Sharpe (2 bps) | **0.75**, 95% bootstrap CI **[0.29, 1.23]**, 100% of resamples > 0 | `full_sample_fixed_parameter`. The KB records the core as `supported`, **not** `confirmed`, and prohibits calling it preregistered or out-of-sample: no holdout exists; parameters were not fitted. |
| Gross Sharpe / cost drag | 0.78 / ≈37 bps yr⁻¹ at 2 bps; turnover **17.6× yr⁻¹** (81% signal/sizing, 19% leverage re-scaling) | measured |
| Cost break | 5 bps → 0.70; 10 bps → 0.61 (CI [0.16, 1.09]); **20 bps → 0.44, CI [−0.01, 0.92] crosses 0** | pre-identified failure boundary |
| Ann. return / vol / MDD / Calmar | 7.4% / 10.3% / −15.6% / 0.48 | |
| Walk-forward blocks (no fitting) | 0.78 / 0.71 / 0.74 / 0.58 / 1.06 | stability, not out-of-sampleness |
| Crisis alpha | GFC 2008 **+11.6%**, COVID 2020 **+7.3%**, calendar 2022 **+15.0%** | published crisis gains motivate the hypothesis that short-side positioning contributes materially; attribution remains to be measured (X24, X46) |
| Monte Carlo | P(DD ≥ 20%) ≈ 45%, P(DD ≥ 30%) ≈ 7% | realized −15.6% was on the benign side |
| Construction sensitivity | EW 0.70 / inverse-vol 0.78 / ERC 0.73 (5 bps); vol window 40/60/90/120 d → 0.76/0.75/0.72/0.71; per-asset target vol 8–15% → all 0.75 | the repo reads this as insensitivity to sizing details; overlapping intervals without a declared margin establish neither difference nor equivalence (X26 formalises the equivalence question) |
| Parameter neighbourhood | 45 combos: net Sharpe [0.38, 0.87], default at 71st percentile; single lookbacks 3m 0.60 · 6m 0.76 · 9m 0.72 · 12m 0.70 · 15m 0.39 · 18m 0.68; combos {6,12} **0.87**, {3,6,12} 0.85, {1,3,6,12,18} 0.81 | robustness sweep — **also an outcome exposure** (see A.5) |

### A.3 Where the PnL and the losses come from

Per-sleeve, full sample (`DRAWDOWN_ATTRIBUTION_REPORT.md` §2):

| Sleeve | Standalone Sharpe | % of total PnL | % of total DD loss |
|---|---|---|---|
| Equity | 0.60 | 34.1 | 33.0 |
| Bond | 0.69 | 29.8 | 17.4 |
| Commodity | 0.55 | 26.0 | 17.4 |
| FX | 0.18 | 6.1 | 10.9 |
| RealEstate | 0.11 | 4.1 | **21.3** |

Three sleeves carry ≈90% of the PnL. FX and RealEstate together contribute ≈10% of PnL and ≈32% of drawdown loss. **This is an exposed fact and must not be turned into an asset-removal rule** (brief §36; KB rule 6). It is, however, legitimate input to the design of a *new* futures universe, where REITs do not exist and FX breadth is far larger.

Drawdown mechanism (`DRAWDOWN_ATTRIBUTION_REPORT.md`, `PHASE0_SYSTEMIC_VERIFICATION.md`):

- **61% crash-type** (a held position bleeding as its trend reverses) vs 39% chop; drawdowns are **multi-sleeve** (≈80–85% of sleeves down together) and occur in **ordinary-vol, low-correlation** regimes (portfolio-vol percentile 0.49 in drawdowns vs 0.95/0.94 in GFC/COVID).
- The deepest episode is **2022-09 → 2023-11 (−15.6%)**: a 14-month decline, 24 months underwater — the reversal of the 2022 rates/USD/commodity trends followed by a directionless 2023. The second is 2018-01 → 2019-01 (−10.3%).
- Cross-sleeve correlation does **not** rise in drawdowns (+0.16 outside vs +0.12 inside).

### A.4 So what is the edge, in one paragraph

A modest, broad, **slow** trend premium harvested across five loosely related sleeves, whose value is disproportionately **convex**: its published gains in sustained macro trends (2008, 2020, 2022) motivate the hypothesis that short-side positioning contributes materially — attribution remains to be measured by X24/X46 — and it pays for that in long, grinding, multi-sleeve reversals in calm markets. On this sample the slower legs carried more of the Sharpe than the 1-month leg; sizing and aggregation choices are nearly irrelevant; costs are the binding constraint at the illiquid end. It is a replication of a published factor on ETF proxies, with wide uncertainty on magnitude and no evidence yet on the instruments a real program would trade.

What is **not** known about the edge, and should be measured before anything is built (Cluster 14, Section C): its average net exposures and hidden beta (a static-premium decomposition was done for XSMOM, never for TSMOM); its convexity profile against a long book; the split of PnL and crisis alpha between long and short positions; and the effective number of independent *trend* bets in the 17-asset book (the ≈12-cluster figure is on returns, not on trend PnL).

### A.5 Sample and exposure state (governs everything below)

| Sample | State | Consequence |
|---|---|---|
| ETF panel 2007-04 → 2026-06 (`dataset.yfinance.multi-asset-etf-panel`); frozen working snapshot = the cache observed in orientation (last date 2026-06-12 observed; snapshot hash, last date and the construction of the final partial-month row are `UNKNOWN_PENDING_WAVE0_VERIFICATION`) | **Burned 6 of 6** (KB `relationships.csv` rows 16–21: core, 4 overlays, XSMOM — verified). All published sleeve/asset/robustness figures are target-metric exposures. No frozen trial-count convention exists for this panel (the core had no preregistration). | Context T0 for every candidate designed here. Every new hypothesis on it is a 7th+ reuse and must be declared (`SAMPLE_REUSE.md`). Results on it are **dependent evidence**, never independent confirmation. The historical count convention (including the 45-cell grid's treatment) is an Aaron decision recorded in Wave 0. |
| Databento commodity panel, 18 CME roots (`dataset.databento.commodity-futures-curves`; corpus observed at `C:\Users\Aaron\quant-data\commodity-carry`, 9.5 GB; coverage 2010-06 → 2026-06 as reported by the carry manifest — snapshot hash and last date `UNKNOWN_PENDING_WAVE0_VERIFICATION`) | Burned by commodity-carry (frozen `N_trials = 14`, verified: carry `PREREGISTRATION.md` §10, `src/config.py` line 66; convention = one trial per distinct constructed strategy-return series, diagnostics excluded); consumed for cost accounting only by `c1-drag-audit` (ledger deliberately not extended). **No TSMOM performance trial has ever run on it.** | Context T1 for ETF-designed candidates (same 2010–26 price paths); the first TSMOM constructed series appends to the ledger under the verified convention. One shared dataset-level record with `mean-reversion-research` is required. GFC is absent (starts 2010-06). |
| Financial futures (ES/NQ, ZT/ZF/ZN/ZB, 6E/6J/6B/6A) | **Not established as owned in the available orientation; inventory pending** (the KB card and the workspace survey report none; no disk or entitlement inventory has been run). Vendor path (Databento GLBX.MDP3) established; cost/coverage unverified. | An Aaron decision (D1) after the Wave-0-defined inventory, not a research step. No purchase is authorised. |
| Pre-2008 futures history (decades) | Not established as owned; would need a long-history vendor. | Context T2 if acquired: same markets, different decades — but the published TSMOM literature's own design conventions were fitted on those decades, so exposure history must be disclosed; different dates alone do not establish independence. Decision for Aaron (D2) after inventory and cost/coverage assessment. |
| Data after the frozen snapshot boundary | Exists at the vendor; **exposure status `UNKNOWN_PENDING_WAVE0_VERIFICATION`** (related-project access and outcome-informed market knowledge matter; "not downloaded by this program" is insufficient). | Two distinct contexts: **T3** accrued-but-protected historical holdout (only after verified protection) and **T4** prospective accrual after a specific contract's seal. Lockbox procedure (Program v2 §2): frozen snapshot identity and hash; a refresh writes a new snapshot and never overwrites the frozen panel; a refresh that revises historical adjusted prices is a new dataset; an opening is an exposure event that burns the holdout for that claim family. |
| Pre-2008 reduced-universe ETF window (≈9 assets live 2003–2007) | Excluded from the core's evaluation ("a different strategy") and therefore **never evaluated by this project**; exposure history otherwise `UNKNOWN`. | Can test claims about that reduced universe only (leg correlations, long/short split); never confirms the 17-asset strategy. |

---

## Section B — What has already been tested and must not be duplicated

Every item below has a committed report or a KB card. "Do not repackage" means: a new hypothesis may reference the mechanism, but its premise test must differ in conditioning variable, sample, or claim, and the difference must be written into its preregistration.

### B.1 Falsified or not promoted, in this repo

| # | Tested | Verdict | Mechanism of failure | Source |
|---|---|---|---|---|
| 1 | Crash-defense / systemic-risk de-grossing | **FALSIFIED at Phase 0** | Trigger anti-aligned: vol/dispersion percentiles max out in the 2008/2020 *profit* windows (0.94–0.95) and are average (0.49) in real drawdowns; cross-sleeve correlation does not spike in drawdowns. | `research/crash_defense/PHASE0_SYSTEMIC_VERIFICATION.md` |
| 2 | Close-to-close vol-compression breakout | **FALSIFIED at Phase 1B** | Compression precedes vol expansion (1.3×) but not direction: efficiency-ratio Δ ≈ 0.00, follow-through Δ ≈ +0.01 on a 0.67 base, no dose-response across thresholds; the one positive was a narrow-channel counting artifact. Scope: close-only data; intraday ATR squeeze untested. | `research/vol_breakout/BREAKOUT_PHASE1B_PREMISE.md` |
| 3 | Seasonality (turn-of-month, Halloween, Monday) | **FALSIFIED 0/18** | Nothing survives BH-FDR q = 0.10 + sign + ≥5 bps/day + stability + non-concentration; Monday (Bond p = 0.026) was an actively caught false positive. | `research/seasonality/SEASONALITY_PHASE1_PREMISE.md` |
| 4 | Yield-curve slope regime conditioning | **FALSIFIED 0/6** | Nominal-sample-size illusion: the inverted/flat state is effectively one episode (2022-24 = 97% of inverted days); effect collapses under leave-one-episode-out. **A broader macro-regime overlay was pre-emptively closed at the event-count level.** | `research/yield_spread/PHASE1_PREMISE.md` |
| 5 | Cross-sectional momentum (XSMOM), 17-ETF and 5-universe map | **FALSIFIED 0/5**; corr with TSMOM **+0.42** → 50/50 mix dilutes (0.66 < 0.75); partly a static risk premium (Sharpe halves under demeaning); Lo–MacKinlay lead-lag term not shown non-trivial. | `research/xsmom/` |
| 6 | No-trade band (5% of NAV, ETF) | **Negative, not adopted** | Turnover 17.6× → 16.0× (−9%) only; net Sharpe −0.06 at every cost level; crisis returns slightly weaker. Premise ("turnover is mostly wasteful re-scaling") was false: 81% is signal-driven. | `output/COST_AND_TURNOVER_REPORT.md` §B |
| 7 | Inverse-vol and ERC risk parity vs equal-weight | Reported by the repo as indistinguishable (0.78 / 0.73 vs 0.70; CIs overlap) — but the comparison was *unpaired* (Δ judged against the EW CI) and no equivalence margin was declared, so under Program v2 §0C this establishes neither a difference nor equivalence. | `output/RISK_PARITY_CONTROL_REPORT.md` |
| 8 | Lookback / target-vol / vol-window neighbourhood | **Robust**, [0.38, 0.87]; default 71st percentile; {6,12} = 0.87 is the exposed peak. | `output/ROBUSTNESS_REPORT.md` |

### B.2 Tested or closed elsewhere in the workspace

| Item | Where | State | Consequence for this map |
|---|---|---|---|
| Commodity carry, XS tercile and TS sign, 18 CME futures | `commodity-carry-research` | **NOT PROMOTED** 0/5 gates each: net Sharpe −0.003 / −0.126, ≈26 robustness variants all ≪ 0.30, gross ≈ net (cost is not the explanation) | Both preregistered standalone carry arms were not promoted on this panel under their tested definitions (the KB records `not_promoted`, not `falsified`). **Carry × trend interaction is untested and explicitly reserved** by that prereg's §9 for a separate preregistration. Carry conditional on a neutral trend state is a different conditional claim, untested either way. |
| ETF → futures cost-drag audit, commodity sleeve | `c1-drag-audit`; KB `finding.tsmom-futures-transfer.drag-audit-stands-no-kill-reach` | c*_sleeve = **6.81 bps** one-way vs a frozen ≤10 boundary → STANDS; **kill branch unreachable** (first reachable kill ≈130 bps). No PnL was run. | The wrapper's cost structure is not disqualifying. STANDS is *not* evidence TSMOM works on futures. The transfer hypothesis (`hypothesis.tsmom.futures-transfer`, WOUNDED, ranked #1) is open. **Reuse the audit's fixed ETF→futures map (D5) and its roll/cost code; reapply the 100× price-unit divisor at the call boundary.** |
| Futures roll / continuous-contract infrastructure | `commodity-carry-research/src/{roll,returns,costs,config}.py`; `c1-drag-audit/audit/{panel,drag}.py` | Built, tested, with documented data traps (outright filter, reused instrument_ids, dead serial months deadlock the naive roll rule) | Reuse; do not re-derive. Chained held-contract returns, never back-adjusted series, for PnL. |
| Financial-futures MR program | `mean-reversion-research` | Governance infra only; proposes the same GLBX universe; **no futures PnL infra**; shared trial ledger required | Coordinate ledgers; do not double-mine. |
| Earlier TSMOM snapshots | `unuse/multi_asset_tsmom`, `unuse/tsmom-*` | Progressive snapshots; zero unique results | Nothing to salvage. |
| KB hypotheses already registered | `registry/hypotheses/` | `hypothesis.tsmom.futures-transfer` (proposed/WOUNDED); `hypothesis.commodity.index-roll-congestion`; FX carry; short-vol; crypto funding; orderflow; spot-MFI | Only the first overlaps this map (= X01/X04). None of the other hypotheses here duplicates a registered card. |

### B.3 Genuinely untested (verified by search of all repos and the KB)

Continuous vs sign signal strength · trend acceleration / age · cross-sectional trend breadth as a state · long/short asymmetry · sleeve-level risk budgeting · alternative trend estimators and their ensemble · execution-day / tranching robustness · vol *estimator type* (only the window was swept) · strategy-state drawdown control · carry × trend · spread (relative-value) trend · futures-native discreteness · TSMOM on any futures panel.

---

## Section C — Extension hypotheses (46 entries, 14 mechanism clusters)

Cluster key (Section D expands it): **C1** implementation transfer · **C2** breadth · **C3** speed · **C4** signal representation · **C5** trend dynamics · **C6** trend-state conditioning · **C7** directional asymmetry · **C8** risk budgeting / allocation · **C9** execution & turnover · **C10** volatility estimation · **C11** strategy-state risk control · **C12** external-state conditioning · **C13** carry interaction · **C14** edge diagnostics.

Field key per entry: Mechanism · Inefficiency/behaviour · Independence from baseline · Horizon · Data · Cheapest premise test · Overfitting risk · Implementation risk · Est. PnL corr with baseline · Capacity · Falsification.

V2 conventions inside entries: **stage splits** (X02a/X02b, X11a/X11b, X35a/X35b, X36a/X36b) are sub-stages under stable IDs, not new hypotheses; **exposure class** names the first test's actual outputs (Program v2 §0B); **design lineage** is stated where the design was informed by exposed outcomes; a "Falsification" bullet describes what *stops progression* under the declared gate — it never means `falsified` unless the KB decisiveness convention is met (Program v2 §0C). Every numeric bar in an entry is a designer proposal for the normal design → challenge → decision process unless marked verified.

### Cluster C1 — Implementation transfer (wrapper truth)

#### X01 — Commodity-sleeve futures transfer, matched-map arm
`Family 1 · C1 · Lane: FULL (after prereg) · Data: Databento 18-root panel (in hand) + ETF sleeve stream (read-only)`
- **Mechanism.** Not a new premium. Tests whether the futures wrapper (OI-max front-contract roll, tick + commission costs, no expense ratio) preserves the commodity sleeve's trend PnL relative to the ETF wrapper (expense ratio, fund roll schedule, tracking). This is the executable continuation of KB `hypothesis.tsmom.futures-transfer` (registered, WOUNDED, ranked #1 by expected information gain).
- **Inefficiency.** Same underreaction / slow diffusion + crisis shorting.
- **Independence.** None by construction; expected corr ≥ 0.9 with the ETF commodity-sleeve stream. Value is deployment truth, not alpha.
- **Horizon.** Monthly; 1–12 m formation.
- **Data.** Chained held-contract returns under the A1 OI-max(t−1) roll rule (`commodity-carry-research/src/roll.py`, `returns.py`); costs via `cost_per_side_pct` with the price-unit divisor applied at the boundary (100× defect on the 8 cents-quoted roots); the c1-drag-audit's frozen primary ETF→futures map (D5) reused unchanged.
- **Cheapest premise test.** (i) Monthly return correlation of each mapped pair (USO↔CL chain, UNG↔NG, GLD↔GC, DBA↔ag basket): expect ≥ 0.9. (ii) Month-by-month sign-agreement rate of the locked composite computed on the ETF vs on the chained futures index: a low agreement rate (the v1 figure 85% is a designer proposal) is a **diagnostic warning** that requires investigation of a possible roll or signal-construction issue before any PnL work; it is not proof of an implementation defect, and it grants no permission to tune the construction toward higher agreement. Accounting invalidity is established only by an actual mechanical, causal or accounting failure in X02a.
- **Overfitting risk.** Low: locked signal, one roll rule, one map. The real risk is a decision rule whose kill branch is unreachable (the drag audit's defect); Stage A2 must verify reachability against the measurable range (`lesson.rule-domain-analysis-before-freeze`).
- **Implementation risk.** High: roll logic, contract specs, price units, dead serial months in grains, settlement-time vs ETF-close alignment for signal dating.
- **Est. PnL corr with baseline sleeve.** ≥ 0.9.
- **Capacity.** High (CL, NG, GC, ZC are among the most liquid futures).
- **Contract (paired, three states).** On the common 2010-07 → 2026-06 window, with the locked signal and one ex-ante roll rule, the estimand is the *paired* wrapper difference (futures-sleeve stream − ETF-sleeve stream on the same months, judged on the objective the deployment claim names — Sharpe non-inferiority as the primary, with path-level diagnostics because similar Sharpes do not establish stream reproduction). Opus proposes and justifies the degradation tolerance / SESOI; a fresh GPT-6 Astra A2 challenges it; Aaron decides. Outcomes are classified against the declared degradation boundary, never against zero: `PRESERVATION_SUPPORTED` if the whole paired interval lies on the preserved side of the boundary; `MATERIAL_DEGRADATION_SUPPORTED` if the whole interval lies beyond it; `UNRESOLVED_INSUFFICIENT_PRECISION` otherwise (the interval straddles the boundary). An interval that contains zero is not by itself unresolved, and one that excludes zero is not by itself decisive; the boundary is defined by the X01 contract, not here. Prospective precision is assessed for the paired estimand at contract design — not transplanted from the KB card's marginal sleeve MDE and not derived from a correlation-based shortcut. Crisis-window behaviour (COVID-2020, calendar 2022) is reported as a deployment diagnostic scoped to the claim, not a kill. A mechanical accounting failure (X02a identities) is a separate, non-performance kill. **Deleted from v1:** the rule comparing a futures interval that crosses zero with an ETF interval that does not — difference of significance is not significance of difference.
- **Declared secondary arms (inside this contract, run after the primary):** construction sensitivity (former X02b) and roll-rule sensitivity (former X03 performance arm). Both are named before the seal; neither runs before it.
- **Downstream adjudication.** A valid negative wrapper result does not automatically suspend X06, X12, X32 or X43; each dependency is adjudicated by Aaron on its own claim. Only mechanical failure or infeasibility suspends automatically.
- **Status vocabulary.** Mechanical identities may be recorded as `implementation_fact` (verified: G4 permits `confirmed` for that type; Program v2 §10). The wrapper-performance comparison is an empirical result, not a fact about the code; it is recorded at most as `supported` in context T1, and the stricter classification question is `CANONICAL_CLASSIFICATION_PENDING_VERIFICATION`. Neither implies a confirmed strategy-performance edge.
- **Trial accounting.** First TSMOM constructed strategy-return series on the Databento panel: append to the carry ledger under the verified §10 convention (one trial per distinct constructed series). One shared dataset-level record with `mean-reversion-research`.
- **Exposure class / lineage.** `TARGET_PERFORMANCE_EXPOSURE` after the seal only; lineage: KB card + c1 map D5; design context T0 (ETF sleeve), validation context T1.

#### X02 — Signal-input construction and tradable-PnL accounting truth (X02a mechanical · X02b performance arm inside X01)
`Family 1 · C1 · Lane: MEASUREMENT (X02a) / declared secondary arm of the sealed X01 contract (X02b) · Data: Databento`
- **Two separate objects.** *Signal input:* the price series the composite is computed on. Several causal constructions are legitimate (a chained held-contract return index; a causally built ratio-adjusted series); one is fixed ex ante for the program and its economic interpretation is stated. *Tradable PnL:* the contract-by-contract dollar ledger (`multiplier × Δsettle` within each held contract, roll legs charged at their costs). For PnL this accounting is mandatory; a mathematically equivalent implementation is acceptable only if it reconciles to that ledger. **Back-adjusted prices never manufacture traded PnL, and no economic-immateriality test can license invalid accounting** (the v1 "< 2% / < 5 bps → cheaper one may be used" clause is deleted for PnL).
- **X02a — mechanical truth (pre-seal, MEASUREMENT).** Causality of the chosen signal input (truncation invariance); roll-date monotonicity; the reconciliation identity between the return-index PnL and the dollar ledger, reported as a residual; multiplier, tick and price-unit tests (reuse the carry repo's, with the divisor applied at the boundary); contract-availability diagnostics; and the sign-agreement rate between the ETF signal and the futures signal per mapped pair. **Exposure class:** `PURE_MECHANICAL_VERIFICATION` and `DESIGN_INFORMING_MEASUREMENT`. Reconciliation is designed to report residuals, not to display return series; any historical PnL series that is displayed is `TARGET_PERFORMANCE_EXPOSURE` and is logged as such.
- **X02b — construction-sensitivity performance arm (inside X01).** Any comparison of strategy returns across signal-input constructions is a performance exposure and runs only as a declared secondary arm of the sealed X01 contract, after the primary arm.
- **Overfitting / implementation risk.** None / high (this is where futures backtests manufacture profits).
- **Stops progression if** any identity fails: no futures performance work proceeds until the residual is explained and fixed. This is a mechanical kill, distinct from any performance outcome.
- **Status vocabulary.** The identities are facts about the code and may be recorded as `implementation_fact` and, when reproducibly verified, `confirmed` (verified against G4; Program v2 §10). This never implies anything about strategy performance.

#### X03 — Roll-rule diagnostics (structural, pre-seal) and roll-rule sensitivity (performance arm inside X01)
`Family 1 · C1 · Lane: MEASUREMENT (structural part only) / declared secondary arm of the sealed X01 contract (performance part) · Data: Databento`
- **Mechanism.** The carry study found its XS arm sensitive to the roll rule (fixed-calendar 0.125 vs −0.003). A slow trend signal should be nearly indifferent. Robustness, not selection: A1 stays primary.
- **Pre-seal (structural only).** Roll dates, roll counts, open-interest crossover timing and contract availability under the A1 and calendar rules. **No Δ net Sharpe, no PnL correlation, no wrapper-performance comparison before the X01 seal** — v1 scheduled exactly that exposure ahead of the seal, and it is removed. Exposure class: `DESIGN_INFORMING_MEASUREMENT`.
- **Inside X01 (performance).** The X01 pipeline under both rules is a declared secondary arm; Δ on the contract's objective and PnL dependence are reported after the primary arm.
- **Consequence if the roll rule proves material** (declared margin, designer-proposed): the roll rule is a hidden degree of freedom and must be preregistered as such in every later futures hypothesis. Immateriality is claimed only within a declared margin, never from "no significant difference".

#### X04 — Financial-futures transfer (equity index, rates, FX) — DEFERRED
`Family 1 · C1 · Lane: none (data not established as owned in the available orientation; inventory pending)`
- **Mechanism.** X01 for the Equity, Bond and FX sleeves.
- **Data.** Not established as owned in the available orientation; inventory pending (Section K, D1). Candidate map: SPY↔ES, EWJ↔NKD, TLT↔ZB/UB, SHY↔ZT, FXY↔6J; UUP↔DX is **ICE, not GLBX**; **LQD/HYG and VNQ/RWX have no liquid futures** → a real program is a hybrid (futures for index/rates/FX/commodities, ETFs for credit and REITs). This hybrid structure should be decided before acquisition.
- **Why deferred.** Requires the Wave-0-defined data inventory and then Aaron's acquisition decision (Section K, D1); no purchase is authorised. Rates futures are one duration factor (ZT/ZF/ZN/ZB), so breadth gain there is illusory; real breadth gains are in FX (6A, 6C, 6B, 6S, 6N) and non-GLBX rates (Bund/Gilt/JGB).
- **Falsification.** As X01, per sleeve.

#### X05 — Discrete-contract feasibility at account NAV
`Family 12 · C1 · Lane: MEASUREMENT · Data: contract specs (carry `CONTRACT_SPECS` for 18 roots), exchange initial-margin tables (dated snapshot), micro-contract specs`
- **Mechanism.** Capital efficiency and implementability, not alpha. For a predeclared NAV set (e.g., $100k / $250k / $500k / $1M — Aaron to confirm the bracket that matters), compute per-market contract counts at the 10% vol target (standard and micro contracts: MES/MNQ/M2K/MYM, MGC, MCL, M6E/M6B, micro 10Y), rounding tracking error vs the continuous target, margin-to-equity, and post-rounding turnover.
- **Falsification of feasibility.** At the deployment NAV, median rounding error in risk terms > 25% of a market's target risk in more than one-third of markets, or margin-to-equity above a predeclared cap → the universe or NAV must change before any FULL futures test is worth running.
- **Why it is Tier 1.** "Deploy in my own account" makes this a prerequisite; it also prices X32.
- **Exposure class.** `DESIGN_INFORMING_MEASUREMENT`; not a performance trial. The feasibility bars above are designer proposals for the normal design → challenge → decision process.

### Cluster C2 — Breadth (independent markets)

#### X06 — Commodity breadth: 18 futures roots vs 4 commodity ETFs
`Family 2 · C2 · Lane: MEASUREMENT premise → FULL · Data: Databento`
- **Mechanism.** Trend is a per-market phenomenon; each independently trending market adds a nearly independent bet. The prior is literature plus a *suggestive, confounded* cross-project contrast in this workspace (a single-instrument SMC study not promoted; a 17-asset TSMOM study `supported`) — that contrast varies signal family and breadth at once and demonstrates nothing about breadth on its own. Commodities are the most heterogeneous sleeve: energy, metals, grains, livestock respond to distinct supply/demand shocks.
- **Independence.** Expected trend-PnL corr of an 18-root commodity trend book with the baseline: 0.3–0.5 (it overlaps the 4-ETF sleeve, 26% of baseline PnL).
- **Horizon.** Monthly.
- **Cheapest premise test (structural).** On the chained panel, per-root trend-PnL streams (locked signal, locked sizing) → correlation matrix → effective number of bets (PCA participation ratio; Meucci ENB). **Principal control: the expanded 18-root futures universe vs the matched futures subset** (the c1 map's roots) under identical dates, identical futures construction, identical risk convention and a fixed sleeve risk budget — so the comparison isolates breadth from wrapper. The 4-ETF sleeve comparison is secondary. **Exposure class:** the per-root trend-PnL streams are `TARGET_PERFORMANCE_EXPOSURE` (generated strategy returns), logged as such even though the premise uses only their dependence structure; no portfolio Sharpe is computed at this stage.
- **Overfitting risk.** Low degrees of freedom. Root selection is the carry study's ex-ante liquidity list (already fixed) — do not re-select. Sample starts 2010-06 (no GFC).
- **Implementation risk.** As X01/X02; livestock and grain roll sparsity.
- **Est. PnL corr with baseline.** 0.3–0.5 for the added markets; ≈1.0 for the overlapping four.
- **Capacity.** High.
- **Stops progression if** the expanded universe adds no effective breadth over the matched futures subset under a declared margin (the v1 figures "ENB gain ≤ 1" and "sleeve corr ≥ 0.9" are designer proposals, not fixed bars). FULL stage (only if the structural premise warrants it): baseline with the expanded sleeve at a **fixed ex-ante sleeve risk share** (the sleeve must not grow its budget merely because it has more names — that is X26's question) vs baseline with the matched subset: paired Δ on the declared objective. Crisis behaviour is reported; no crisis-retention gate applies to a diversifying line (Program v2 §0 rule 11).
- **Trial accounting.** Extends the Databento ledger.

#### X07 — Effective breadth of the current 17-asset book (diagnostic)
`Family 2 · C2 · Lane: MEASUREMENT · Data: published per-asset net PnL (output/dd_per_asset_net.csv) — no new performance trial`
- **Mechanism.** The "≈12 clusters at 0.60" figure is on *returns*. Trend-PnL correlation is what determines portfolio breadth. Compute the 17×17 trend-PnL correlation matrix, ENB, sleeve-level PnL correlations, and the RealEstate–Equity and FX overlaps.
- **Why.** Calibrates X06, X08, X26, and Section E's priors.
- **Anti-snooping rule.** No ETF is removed from the baseline on this basis. A finding such as "RealEstate trend PnL corr with Equity ≥ 0.8" feeds only the design of the *new* futures universe (where REITs do not exist anyway).
- **Exposure class / lineage.** Re-read of published (already exposed) streams plus *new* statistics derived from them: `TARGET_PERFORMANCE_EXPOSURE` (new decompositions of burned streams) and `DESIGN_INFORMING_MEASUREMENT`; context T0. It can calibrate priors for candidates that modify the same stream and for sleeve overlap; it cannot measure correlations of candidate streams that do not yet exist (X06, X09, X11 legs).

#### X08 — Dropped-ETF trend-PnL independence
`Family 2 · C2 · Lane: MEASUREMENT premise · Data: raw 30-ETF panel (in hand; 13 screened-out names)`
- **Mechanism.** Two assets with return corr 0.85 can have trend-PnL corr well below that because their sign flips differ in timing. Screening dropped on return correlation, so independent trend PnL may have been discarded (SLV, GDX, IWM, XLV, XLF, EFA, IEF, FXE, QQQ, XLK, CPER, WEAT, CORN).
- **Cheapest test.** Per dropped ETF, trend-PnL stream (locked signal) vs its kept anchor's: correlation; ENB of 30 vs 17.
- **Overfitting risk.** Medium: 13 candidate additions on a burned panel. Generating 13 candidate streams and selecting on their correlations **is design selection even without choosing by Sharpe**; every candidate and the inclusion decision are recorded as attempts. Inclusion may only follow a **pre-stated** trend-PnL correlation threshold (e.g., < 0.6 with every kept asset). The ETF result is dependent evidence (T0); any validation belongs to contexts T1–T4.
- **Exposure class.** `TARGET_PERFORMANCE_EXPOSURE` (13 generated strategy streams), logged.
- **Est. PnL corr with baseline.** 0.6–0.8 for additions.
- **Capacity.** High (liquid ETFs) but with expense drag; CPER has documented bad prints; WEAT/CORN start 2010–11.
- **Stops progression if** no dropped ETF clears the pre-stated trend-PnL dependence margin against every kept anchor (the v1 figure 0.6 is a designer proposal) → no hidden-breadth lead. High dependence restricts an independence claim; it does not prove identity.

#### X09 — Spread-trend (relative-value trend) on four predeclared economic spreads
`Family 2 / own idea · C2 · Lane: X09_ROUTE_PENDING_AARON — A: structural overlap / non-redundancy screen (MEASUREMENT) → sealed FULL; B: declared exploratory performance exposure → logged lead · Data: ETF panel; futures later`
- **Mechanism.** The same underreaction applied to *relative* prices whose drivers differ from outright levels: curve slope (TLT/SHY — policy-expectation trends), credit spread (HYG/LQD — default-cycle trends), EM vs US equity (EEM/SPY — growth/USD-cycle trends), energy equity vs crude (XLE/USO — refining/capex cycle). A trend in a ratio bets on persistence of a relative flow, partly orthogonal to outright trends.
- **Independence.** Expected corr with baseline 0.1–0.4 — but the outright book already holds signed positions in both legs (long TLT / short SHY *is* a curve trade), so overlap must be measured, not assumed.
- **Horizon.** Monthly, 1–12 m.
- **Executable definitions come first (either route).** A log price ratio is not a self-financing portfolio. Before any performance test: hedge ratios (vol-neutral or beta/duration-neutral legs, fixed per spread), leg notionals, financing and short cost, risk scaling, and the fact that TLT/SHY and HYG/LQD are not pure curve or credit-spread exposures merely because they are ratios.
- **Route A — structural overlap / non-redundancy screen (MEASUREMENT).** Does each proposed spread merely reconstruct outright exposures the baseline already holds? Measured at position level from the baseline's published weights (implied spread exposure of the outright book vs the proposed spread position); no PnL is generated. It can establish only that a spread is or is not structurally redundant with the held book. It establishes **no positive alpha, no Sharpe, no low realised PnL correlation and no portfolio benefit**; those are the sealed FULL study's questions. Exposure class: `DESIGN_INFORMING_MEASUREMENT`.
- **Route B — declared exploratory performance exposure.** Four log-ratio series, monthly; the locked {1,3,6,12} sign composite; vol-scaled spreads; equal-weight → PnL stream; corr with baseline, standalone interval, marginal Δ at a fixed 20% risk share. This is `TARGET_PERFORMANCE_EXPOSURE` and is logged as an exploratory lead on the burned ETF panel (T0); no later seal makes those outcomes fresh.
- **Family (declared for the performance study under either route):** composite claim + 4 per-spread claims + marginal-portfolio claim = 6 claims, one family. The four spreads are fixed here; **no pair may be added or swapped after this line.**
- **Overfitting risk.** Medium (pair choice is the degree of freedom; fixed above, economically motivated).
- **Implementation risk.** Low on ETFs; on futures the credit and EM legs have no clean instruments.
- **Capacity.** High.
- **Stops progression if** (route A) the structural screen shows every spread is reconstructing held outright exposure within a declared overlap margin, or (performance study) the declared marginal-contribution gate is not met; high PnL correlation with the baseline triggers `HIGH_REDUNDANCY_REVIEW`, not an automatic kill. The v1 figures (0.7, +0.05) are designer proposals.
- **Exposure / lineage.** 7th+ hypothesis on the burned ETF panel — declare. Route B produces `TARGET_PERFORMANCE_EXPOSURE`; route A does not. Either way the ETF result is dependent evidence (T0).

#### X10 — Global financial-futures breadth — DEFERRED
`Family 2 · C2 · Lane: none`
- With X04. Genuine breadth is more likely in FX pairs and non-US rates than in additional equity indices (global equity beta) or the US curve (one duration factor). Data not established as owned in the available orientation; inventory pending; venue mix (CME, ICE, Eurex, OSE) multiplies data cost.

### Cluster C3 — Same mechanism, different speed

#### X11 — Speed-leg decomposition and leg-risk-balanced ensemble
`Family 3 · C3 · Lane: X11a structural decomposition (MEASUREMENT) / X11b leg-risk-balanced ensemble (FULL, own sealed contract, build gate applies) · Data: ETF panel first; contexts T1–T4 for validation · Lineage: ROBUSTNESS_GRID_INFORMED`
- **Mechanism.** Fast (1–3 m) and slow (6–12 m) legs capture different phases of one underreaction–overreaction cycle: fast legs enter and exit early (more whipsaw, faster crisis response); slow legs ride mature trends and bleed at reversals (the 2022-23 loss profile). If their failure periods differ, an ensemble of individually modest speeds can have better Calmar/Sortino than any single speed even at equal Sharpe.
- **The one real design difference.** The baseline averages *signs* then vol-scales once. A *leg-risk-balanced* ensemble vol-targets each leg's portfolio separately before combining, so faster legs (lower realized vol per unit signal because they flip more) receive a different risk share. That is the testable object — not "the ensemble", which at equal sign-weights is the baseline itself.
- **Independence.** Fast leg vs baseline 0.5–0.7; slow legs vs baseline 0.8–0.9; fast vs slow 0.3–0.6 (priors).
- **Cheapest test.** The four legs {1}, {3}, {6}, {12} already exist as Method-A signals. Build each as a full sub-strategy with identical sizing/portfolio machinery → pairwise PnL correlation, drawdown-episode overlap (Jaccard of underwater months), crisis-window attribution per leg, turnover per leg.
- **Overfitting risk.** Low if the leg set stays {1,3,6,12} and weights are never searched (equal risk only). The trap is turning the correlation table into weight optimisation — forbidden.
- **Implementation risk.** Low.
- **Capacity.** Fast leg lower (turnover).
- **X11a → X11b progression.** X11a stops progression if the leg streams show no failure-period diversity under declared margins (the v1 figures — pairwise correlation 0.8, Jaccard 0.8 — are designer proposals). X11b, if built under its own sealed contract, is judged by a paired comparison on its declared objective (Calmar and Sortino were the v1 proposal). X11a's exposed leg statistics are dependent evidence for X11b, never independent evidence; "Δ CI includes 0" in X11b is `unresolved` or `not_promoted`, not falsification.
- **Exposure class.** X11a generates four sub-strategy return streams: `TARGET_PERFORMANCE_EXPOSURE`, logged. The 1-month leg's standalone statistics are new exposure; the 3/6/12-month legs' were already exposed by the robustness grid.
- **Design lineage: `ROBUSTNESS_GRID_INFORMED`.** The robustness grid already revealed {6,12} = 0.87 > {1,3,6,12} = 0.75 on this sample, so any "slower is better" conclusion on the ETF panel is dependent evidence (T0). The *correlation and overlap structure* was never exposed and is the clean structural premise. Validation of X11b belongs to contexts T1–T4, each recorded separately from this lineage; the origin does not prevent later independent validation and the T0 evidence is never relabelled as independent.

#### X12 — Fast-leg marginal contribution net of realistic costs (replication-only)
`Family 3 · C3 · Lane: FULL on the futures panel only · Lineage: ROBUSTNESS_GRID_INFORMED · Validation context: T1 (dependent — same 2010–26 price paths as the ETF design)`
- **Mechanism.** The 1-month leg flips most often and drives the signal-driven 81% of turnover; on the ETF sample it reduced Sharpe by ≈0.10 ({3,6,12} = 0.85 vs 0.75 — **exposed**). Hypothesis: at measured futures costs, its marginal net contribution ≤ 0.
- **Cheapest test.** Futures panel only: {1,3,6,12} vs {3,6,12}, paired Δ-Sharpe at the measured c* costs. One comparison, no scan.
- **Overfitting risk.** High if run on the ETF panel (answer already known) — hence replication-only. Even on futures the 2010–26 price paths overlap the ETFs' (implementation-level independence only, as the KB card states).
- **Does not support progression if** the paired Δ-Sharpe(with − without) interval lies entirely on the "fast leg helps" side of the declared margin: that contradicts the tested claim ("the fast leg hurts net") under this study. Final KB status follows the canonical decisiveness convention; a single paired result is not general falsification.
- **Condition.** Only meaningful if X11 shows the fast leg is not redundant with the slow legs.

#### X13 — Asset-class speed specialization — DEFERRED
`Family 17 · C3 · Lane: none`
- **Mechanism.** Commodities/FX may trend on shorter horizons (inventory and flow cycles), rates/equities slower (policy cycles).
- **If ever run.** Exactly two specs per sleeve (fast {1,3} vs slow {6,12}), 5 sleeves → 10 cells, BH-FDR, within-sleeve consistency across all members required, futures replication required.
- **Why deferred.** X11's per-sleeve leg correlations arrive for free and will show whether there is anything to specialise; and the exposed grid already tempts a fitted answer. Highest overfitting risk in the map.

### Cluster C4 — Signal representation of the same trend

#### X14 — Trend-strength premise: does magnitude carry information beyond sign?
`Family 4 · C4 · Lane: MEASUREMENT premise · Data: ETF panel (+ futures replication)`
- **Mechanism.** If underreaction is gradual, a stronger normalised trend (return ÷ vol over the lookback, a t-stat-like z) reflects more accumulated, not-yet-absorbed information → higher expected continuation; alternatively extreme z reflects crowding or exhaustion → flat/negative. The literature is mixed (concave response). The baseline already sizes by horizon agreement (|score| ∈ {0.5, 1}).
- **Cheapest test.** Pooled panel (17 × ≈218 asset-months, which are **not** ≈3,700 independent observations — inference must preserve common calendar shocks, serial dependence and overlapping horizons; the scheme is decided at candidate design, Program v2 §7). (i) Forward 1-month sign-aligned return per unit ex-ante vol for |score| = 0.5 vs 1.0. (ii) By decile of |z12| (12 m return ÷ 12 m realised vol): mean sign-aligned forward risk-adjusted return per decile. **Two predeclared shape-sensitive contrasts:** a monotone contrast (trend across deciles) and a concavity contrast (middle deciles vs extremes, or a quadratic term in decile rank). A monotone test alone cannot reject a symmetric hump; the v1 rule that would have done so is deleted. Predeclare the mapping: monotone contrast positive → premise for continuous sizing; concavity contrast positive without a strong monotone term → premise for bounded/capped sizing.
- **Overfitting risk.** Medium: one z horizon (12 m) plus the existing score; deciles fixed; no curve fitting.
- **Implementation risk.** Low.
- **Est. PnL corr with baseline** for any resulting sizing variant: ≥ 0.9.
- **Capacity.** High.
- **Stops progression if** both contrasts fail their declared gates (multiplicity across the two contrasts and the exact statistics fixed at candidate design; Opus proposes, Astra challenges, Aaron decides). Failure stops X15; it does not establish general falsification of magnitude information.
- **Exposure class / lineage.** 7th+ reuse on the ETF panel; `DESIGN_INFORMING_MEASUREMENT` (conditional forward returns that can determine a later sizing rule; no strategy Sharpe); any resulting X15 design carries lineage to this measurement.

#### X15 — Bounded continuous sizing (conditional on X14)
`Family 4 · C4 · Lane: FULL`
- One mapping, chosen by X14's shape (linear clipped at ±2σ if monotone; hump-capped if concave); everything else identical. Paired Δ-Sharpe / Δ-Calmar vs baseline; turnover change; crisis retention.
- **Falsification.** Paired Δ CI includes 0, or turnover +20% without Δ-Sharpe > +0.1.

#### X16 — Estimator-family correlation (same-source test)
`Family 9 · C4 · Lane: MEASUREMENT · Data: ETF panel (daily for EWMA)`
- **Mechanism.** Return-sign composite (baseline), EWMA-crossover triplet (8/24, 16/48, 32/96 days, z-scored and capped, per Baz et al. 2015), robust 12-month regression-slope t-stat, and Donchian channel position (6 m and 12 m) are four representations of one behavioural mechanism. High pairwise PnL dependence (the v1 figure 0.85 is a designer proposal, not a cutoff) restricts any claim that they are independent sources and triggers `HIGH_REDUNDANCY_REVIEW`; it does not prove a single alpha source. If dependence is lower, estimator-specific whipsaw partly cancels in an ensemble.
- **Cheapest test.** Build each as a full sub-strategy with identical sizing/portfolio machinery; 4×4 PnL correlation, drawdown overlap, turnover, signal-agreement rates. No selection.
- **Overfitting risk.** Low (four estimators fixed at standard parameterisations; nothing tuned).
- **Implementation risk.** Low–medium.
- **Est. PnL corr with baseline.** 0.8–0.95 each.
- **Capacity.** High.
- **Stops progression if** the four estimators show no failure-period diversity under a declared dependence margin (the v1 figure 0.85 is a designer proposal). High dependence restricts claims of *independence*; it does not by itself establish a single alpha source, and a low-cost ensemble or implementation improvement may still be proposed under X17 through `HIGH_REDUNDANCY_REVIEW` rather than being killed by a cutoff.
- **Exposure class.** `TARGET_PERFORMANCE_EXPOSURE`: four sub-strategy Sharpes and return streams are generated and logged. X17's design is outcome-informed by them (dependent evidence, T0); its validation contexts are recorded separately.

#### X17 — Estimator ensemble vs baseline (conditional on X16)
`Family 10 · C4 · Lane: FULL`
- Equal-weight ensemble (primary); median and majority-vote as two predeclared secondaries (BH-FDR across 3). A later, more complex weighting must beat the equal-weight ensemble, not the baseline.
- **Falsification.** EW ensemble paired Δ-Sharpe CI includes 0 **and** Δ-Calmar ≤ 0.

#### X18 — Path-efficiency (efficiency-ratio) conditioning
`Family 15 · C4 · Lane: MEASUREMENT premise · Data: ETF panel (causal regime panel exists: src/regime.py)`
- **Mechanism.** A trend that unfolded efficiently (high Kaufman ER) reflects persistent one-directional participation; a noisy path with the same net return reflects contested pricing → lower follow-through. Distinct from the vol-breakout study, which used *post-move* ER as an outcome, not trailing ER as a conditioner.
- **Cheapest test.** Per asset-month, trailing 63-day ER tercile (causal) × sign signal → forward-month sign-aligned hit rate and risk-adjusted return; pooled + 5 sleeves = 6 cells; BH-FDR q = 0.10; magnitude bar (≥ 3 pp hit-rate difference top vs bottom tercile).
- **Overfitting risk.** Low–medium (one window, terciles).
- **Stops progression if** no cell clears the declared conjunction (multiplicity treatment, magnitude bar and stability check fixed at candidate design). Family grouping with X39 follows the actual selection process: one 12-cell family if a single selection step chooses among them, separate only if run as separately sealed, non-competing contracts (Program v2 §11).
- **Exposure class.** `DESIGN_INFORMING_MEASUREMENT` (conditional forward returns); panel inference per Program v2 §7.

### Cluster C5 — Trend dynamics (acceleration, age, exhaustion)

#### X19 — Acceleration and trend-age premise
`Family 5 · C5 · Lane: MEASUREMENT premise · Data: ETF panel`
- **Mechanism.** Information diffusion is a process: a trend that is young (recently flipped) and accelerating (Δz > 0) is mid-diffusion; a mature, decelerating trend is closer to full absorption or crowding. Δz and age carry information beyond level only if diffusion speed varies across episodes.
- **Cheapest test (proposed candidate definitions, not sealed methodology).** Pooled panel regression of forward sign-aligned risk-adjusted return on level (z12), **sign-aligned acceleration** (acceleration = (z12_t − z12_{t−3}) × sign(score_t), so that strengthening in the direction of the current trend is positive), and age (consecutive months of the same non-zero composite sign, **reset at a zero score**; zero-score asset-months carry no position and are excluded from the age analysis); plus a 3×3 sort (level tercile × acceleration tercile). Dependence-aware panel inference decided before the run (Program v2 §7). **Selection scope — governance choice B, faithful to the existing design in which the corner contrast is decision-bearing:** the prospective inferential family is {acceleration coefficient, age coefficient, 3×3 corner contrast, X20 tail cell} = **4**. The corner contrast is part of the selection scope and is counted; level (z12) is a covariate/control, not a counted test.
- **Overfitting risk.** Medium–high (nonlinear temptation). Functional forms fixed here: linear coefficients and terciles only; no splines, no thresholds searched.
- **Implementation risk.** Low.
- **Est. PnL corr with baseline** of any resulting overlay: ≥ 0.9.
- **Stops progression if** the acceleration and age terms and the corner contrast all fail their declared gates. This stops the overlay; it does not establish general falsification. Numerical bars and the inference scheme are fixed at candidate design (Opus proposes, Astra challenges, Aaron decides).
- **Exposure class.** `DESIGN_INFORMING_MEASUREMENT` (conditional forward returns).

#### X20 — Exhaustion after extreme acceleration
`Family 5 · C5 · Lane: MEASUREMENT (same family as X19)`
- Top-decile sign-aligned acceleration (and top-decile |z|) → forward return relative to the rest; one tail cell, decile fixed, no cutoff search. Fourth member of the X19/X20 family {acceleration coefficient, age coefficient, 3×3 corner contrast, tail cell} (total 4, reconciled with Program v2 §11; level is a covariate, not counted; corner contrast counted — governance choice B).
- **Falsification.** Tail-cell difference CI includes 0.

### Cluster C6 — Trend-state conditioning (breadth, dispersion, concentration)

#### X21 — Trend breadth predicts continuation
`Family 6 · C6 · Lane: MEASUREMENT premise · Data: ETF panel + published net returns`
- **Mechanism.** Broad cross-market trend agreement usually reflects a macro driver (2008 deleveraging, 2020 shock, 2022 inflation/rates) that propagates slowly through many markets → more persistent; narrow trends are idiosyncratic and fragile.
- **Cheapest test.** Causal breadth state at month-end t: B1 = fraction of assets with |score| = 1; B2 = fraction of sleeves whose members agree in sign; tercile of a trailing 36-month causal percentile. Forward strategy net return at 1 and 3 months by tercile; HAC; **and an episode jackknife** (breadth regimes are slow: count distinct high-breadth episodes, require ≥ 4, and require that no single episode carries the effect — the yield-curve lesson applied in advance).
- **Overfitting risk.** Medium (2 definitions × 2 horizons = 4 cells; the episode-count trap is the real risk).
- **Est. PnL corr with baseline** of any overlay: ≥ 0.9.
- **Falsification.** 0 of 4 cells clear BH-FDR + magnitude (≥ 3% yr⁻¹ Δ) + episode jackknife.
- **Exposure class / lineage.** Uses the strategy's own published net returns as the outcome → `TARGET_PERFORMANCE_EXPOSURE`, context T0; any resulting overlay is outcome-informed and carries this lineage. Panel and episode inference decided before the run (Program v2 §7).

#### X22 — Signal dispersion / mixed-horizon disagreement → whipsaw regime
`Family 6 · C6 · Lane: MEASUREMENT (same family as X21)`
- B3 = average |score| across assets (low = many mixed signals). Low-B3 months precede lower hit rates. Adds 2 cells to the X21 family.

#### X23 — Trend concentration (effective number of active trends)
`Family 6 · C6 · Lane: MEASUREMENT (same family as X21)`
- B4 = 1/HHI of |base-weight| shares. Concentrated risk precedes worse tail outcomes. Adds 2 cells. **X21–X23 form one preregistered family of 8 cells under a single BH-FDR.**

### Cluster C7 — Directional asymmetry

#### X24 — Long/short decomposition by sleeve
`Family 7 · C7 · Lane: MEASUREMENT (decomposition) · Wave 1 (moved from Wave 5) · Data: published per-asset net PnL and positions · Exposure class: TARGET_PERFORMANCE_EXPOSURE (new substream statistics of burned, published streams), context T0`
- **Mechanism.** Long trend in risk assets (equities, credit, REITs) is aligned with the risk premium; its bleed is the mean-reverting rally after dips. Short trend in the same assets fights the premium and faces sharp V-shaped recoveries (2009, 2020) → lower Sharpe, worse skew, shorter duration. **Whether crisis gains are short-side is a hypothesis this decomposition tests, not an established fact; the published crisis gains only motivate it.** In rates, FX and commodities the premium is weaker or ambiguous, so long ≈ short is the prior.
- **Cheapest test.** Split each asset-month's net PnL by position sign. Per sleeve: long vs short Sharpe, hit rate, skew, mean holding duration, turnover share, crisis-window contribution; block bootstrap of the long − short Sharpe difference; half-sample stability. Family: 5 sleeves × 1 contrast, BH-FDR.
- **Overfitting risk.** Low (no parameters). The risk lives in the follow-on rule (X25).
- **Implementation risk.** None.
- **Est. PnL corr with baseline.** n/a (decomposition).
- **Falsification of asymmetry.** No sleeve shows a stable (same sign in both halves) long − short difference that passes BH-FDR with |ΔSharpe| ≥ 0.3.
- **Exposure / lineage.** Sub-stream Sharpes and crisis attributions are new decompositions of burned streams: `TARGET_PERFORMANCE_EXPOSURE`, T0, logged. Any sleeve selection into X25 is outcome-informed and carries this lineage.

#### X25 — Asymmetric short-side scaling in risk-premium sleeves (conditional on X24)
`Family 7 · C7 · Lane: FULL (own sealed contract; build gate applies) · Lineage: POST_EXPOSURE_DESIGN_ON_ETF_PANEL (X24-selected sleeves) · Validation contexts recorded separately (T1–T4)`
- **Mechanism.** If X24 is stable, identical signal magnitude should not imply identical long and short risk in premium-bearing sleeves.
- **Design.** One predeclared rule: in the sleeves X24 identified, short positions sized at 0.5× (one value, never searched); everything else unchanged. **Crisis preservation applies here because the rule modifies the deployed stream's defensive side** (Program v2 §0 rule 11, claim-specific): the designer proposes the retention requirement and its economic justification (the v1 figure was 70%; it is a proposed policy threshold, not a scientific constant), specifying common risk scaling, fixed event windows and the treatment of small or negative reference returns; Astra challenges; Aaron decides. Paired Δ on the declared objective (Δ-Sharpe / Δ-Calmar / Δ-skew were the v1 proposal).
- **Est. PnL corr with baseline.** ≥ 0.9.
- **Stops progression if** the declared crisis-preservation requirement is not met **or** the paired comparison fails its declared gate; a paired interval that merely includes zero is `unresolved`, not falsification.
- **Design lineage: `POST_EXPOSURE_DESIGN_ON_ETF_PANEL`** with respect to X24's sub-streams; the ETF-panel result is dependent evidence (T0); validation contexts T1–T4 are recorded separately.

### Cluster C8 — Risk budgeting and allocation

#### X26 — Equal-sleeve risk vs equal-asset risk
`Family 8 · C8 · Lane: FULL (paired control) · Data: ETF panel`
- **Mechanism.** The current budget is by asset count (Equity 5/17, Bond 4/17, Commodity 4/17, FX 2/17, RealEstate 2/17) — an artifact of screening, not a risk view. Equal sleeve risk removes the artifact. The prediction is genuinely ambiguous (it upweights FX and RealEstate); the value is a robustness finding: the baseline's result does not depend on the accidental count weighting.
- **Cheapest test.** Reuse the `rp_comparison.py` pattern with a sleeve-level aggregation; **paired** bootstrap of the difference (fixing the unpaired comparison used in the risk-parity control). Two variants only: equal-sleeve; uniform sleeve cap (35% was the v1 proposal). **Objective = robustness, so the formulation is equivalence / non-inferiority with a declared margin**, not a demand for positive Sharpe improvement.
- **Overfitting risk.** Low (two symmetric structural variants).
- **Est. PnL corr with baseline.** ≥ 0.95.
- **Result states.** Equivalence supported (paired interval inside the declared margin) → the baseline's result does not depend on the count weighting; materially different (interval beyond the margin) → a lead in T0 for whichever budget is better on the declared objective; interval that neither fits inside the margin nor excludes it → `unresolved`. "No significant difference" is never reported as equivalence.
- **Design lineage: `POST_EXPOSURE_DESIGN_ON_ETF_PANEL`.** Sleeve statistics are published, so the designer knows FX and RealEstate are weak. A "cap the weak sleeves" rule would be snooping; the only admissible variants are symmetric rules stated before any run.

#### X27 — Cluster-based hierarchical risk budget
`Family 8 · C8 · Lane: FULL (same family as X26)`
- Sleeves defined by causal correlation clustering (trailing 3 years, cut at 0.6) instead of named asset classes; risk equalised across clusters, then within. Adds estimation noise (cluster instability); must beat *equal-sleeve*, not just equal-asset.
- **Result states.** Same equivalence formulation as X26, measured against equal-sleeve; an interval that includes zero without fitting inside the margin is `unresolved`.

#### X28 — Static risk-premium blend (deployment portfolio)
`Family 18 / own idea · C8 · Lane: MEASUREMENT · Data: published TSMOM net and equal-weight buy-and-hold streams`
- **Mechanism.** For a personal account, TSMOM's low correlation with a long risk-premium book (the repo's equal-weight buy-and-hold has Sharpe 0.33) may raise portfolio Sharpe/Calmar more than any overlay: trend as a convex overlay on a long book. Not alpha; allocation.
- **Cheapest test.** corr(TSMOM net, buy-and-hold); Sharpe/Calmar of three fixed blends (100/0, 75/25, 50/50 by risk); paired vs TSMOM alone.
- **Overfitting risk.** Low.
- **Est. corr with baseline.** 0.1–0.3 (the long book).
- **Stops progression if** no fixed blend meets the declared objective (Calmar improvement with a declared Sharpe non-inferiority margin was the v1 proposal).
- **Exposure class.** Sharpe and Calmar of three blends are allocation-performance outcomes: `TARGET_PERFORMANCE_EXPOSURE`, T0, logged. "Not a strategy" is not an exemption from accounting for tested allocations.

#### X29 — Dynamic allocation across validated sub-strategies — DEFERRED
`Family 18 · C8 · Lane: none until ≥ 2 validated sub-strategies exist (today: 0)`
- Predeclared candidate set when reached: equal, inverse-vol, capped inverse-vol. No performance chasing.

### Cluster C9 — Execution and turnover

#### X30 — Execution-day robustness
`Family 11 · C9 · Lane: MEASUREMENT · Data: ETF daily panel (src/daily.py infra exists)`
- **Mechanism.** None — robustness. Variants: execute at close T (baseline), T+1, T+2, T+3; signal dated day 15 with execution T+1. Five variants, no selection; the baseline stays T.
- **Cheapest test.** Daily held-weight paths; net Sharpe, MDD, crisis returns per variant; dispersion across variants.
- **The robustness claim is not supported if** the dispersion of outcomes across the five variants exceeds the declared dispersion margin (the v1 figure 0.15 is a designer proposal) **or** a crisis-window sign flips. Robustness is a declared-margin claim: a variant's Sharpe falling outside the baseline's bootstrap interval is not the criterion, and the absence of a significant difference is not the criterion either.
- **Exposure class.** Five variants' Sharpe, MDD and crisis outcomes: `TARGET_PERFORMANCE_EXPOSURE`, logged; the whole grid is preserved and no winner is selected. "Robust" is claimed only within a declared dispersion margin, never from the absence of a significant difference.

#### X31 — Tranched (staggered) execution
`Family 11 · C9 · Lane: FULL (single variant; proportionate effort, full claim protection) · Data: daily panel`
- **Mechanism.** Split the book into four tranches, each rebalanced on its own weekly anchor from its own decision date → diversifies timing luck, smooths turnover; standard CTA practice.
- **Test.** One variant vs baseline: paired Δ-Sharpe, Δ-MDD, turnover; and the dispersion across X30's calendar variants should shrink.
- **Falsification.** Paired Δ-Sharpe CI entirely < −0.05, or turnover +15%.

#### X32 — Contract-integer hysteresis band (futures-native)
`Family 12 · C9 · Lane: FULL on the futures panel · Data: Databento + X05 specs`
- **Mechanism.** With integer contracts the natural rebalance unit is one contract. Trade only when the target count differs from held by ≥ 1 **and** the implied risk change exceeds a threshold (two predeclared: 10% and 25% of the market's risk allocation). Structurally distinct from the ETF 5%-of-NAV band (which suppressed genuine trades): discreteness already imposes a floor; the question is whether a risk threshold on top reduces churn without tracking-error cost.
- **Test.** Turnover, cost, tracking error vs continuous target, net Sharpe at c*, tail; paired vs immediate rounding.
- **Falsification.** Both thresholds reduce net Sharpe (paired CI < 0) **or** tracking error > 10% of target vol.
- **Honours the ETF band negative.** The premise there ("turnover is wasteful") was false; the premise here ("rounding noise is wasteful") is different and measurable.

#### X33 — Signal-path smoothing / sign-persistence confirmation
`Family 12 · C9 · Lane: FULL (2 variants) · Data: ETF panel then futures`
- **Mechanism.** 81% of turnover is signal-driven and the 1-month leg's sign flips are its noisiest component. Smoothing the composite score (EWMA, 2-month half-life, one value) or requiring two consecutive months of a leg's sign before it counts changes the *signal path* rather than suppressing trades — a different mechanism from the failed band.
- **Test.** Turnover reduction; paired Δ net Sharpe at 2/5/10 bps; crisis retention; lag cost (2020 response). Two variants, BH-FDR across 2.
- **Overfitting risk.** Medium (the smoothing parameter is a degree of freedom; fixed at one value each).
- **Falsification.** Turnover reduction < 15% **or** paired Δ net Sharpe at 5 bps ≤ 0.
- **Design lineage: `POST_EXPOSURE_DESIGN_ON_ETF_PANEL`** (turnover composition is published) **and `ROBUSTNESS_GRID_INFORMED`** (the 1-month leg's sign-flip noise that the smoothing targets was highlighted by the grid's observed outcomes; a lineage link only — the grid's historical classification is unchanged); the ETF result is dependent evidence (T0); validation contexts T1–T4 recorded separately.

#### X34 — Event-triggered intra-month re-evaluation after a large adverse move
`Family 14 / own idea · C9 · Lane: MEASUREMENT premise → FULL · Data: daily panel`
- **Mechanism.** 61% of drawdown loss is crash-type and declines last 14 months; a monthly calendar ignores a −2σ intra-month move against a held position. If such moves predict further adverse drift within the month (trend break), an event-triggered re-check (recompute the composite that day; exit or flip only if the sign changed) cuts crash losses; if they predict rebound (noise), it adds whipsaw.
- **Cheapest premise test.** For each eligible event (first day an asset's position shows a month-to-date return ≤ −2σ, ex-ante monthly σ — the threshold is a designer proposal): the sign-aligned return over a **comparable forward horizon that is the same for every event** vs the unconditional return over that horizon, and whether the composite sign has already changed that day. The v1 "remaining-month" outcome is deleted: event dates leave different horizons to month-end, and an unmatched benchmark can manufacture an effect. The eligible-event population (including whether late-period events are excluded, which changes the target population and needs justification) and the horizon are fixed at candidate design, not here. Six cells (pooled + 5 sleeves); multiplicity and panel inference per Program v2 §7.
- **Overfitting risk.** Medium (threshold and horizon fixed here).
- **Implementation risk.** Medium (intra-month execution, costs).
- **Stops progression if** the post-event forward return is not worse than the matched unconditional return by the declared bar → no premise; do not build. Exposure class: `DESIGN_INFORMING_MEASUREMENT`.

### Cluster C10 — Volatility estimation

#### X35 — Volatility-estimator type
`Family 13 · C10 · Lane: X35a estimator-stability diagnostic (MEASUREMENT, 4 fixed variants) / X35b replacement study (FULL, own sealed contract, non-inferiority acceptance) · Data: ETF panel`
- **Mechanism.** Sizing stability, not alpha. A simple 60-day window drops old shocks abruptly (edge effects → step changes in weights → turnover); EWMA (λ = 0.97) decays smoothly; a fast/slow blend (20 d / 120 d) damps; a MAD-based robust estimator resists single-day outliers. Expect Sharpe ≈ unchanged (the window sweep gave 0.71–0.76), vol-driven turnover reduced, realised-vs-target tracking similar or better.
- **X35a (diagnostic).** Four estimators, one parameterisation each: vol-attributable turnover, realised/target vol ratio error, worst month. Selection of a candidate replacement **only** by the pre-stated stability criterion, never by Sharpe. Any Sharpe or worst-month output produced here is `TARGET_PERFORMANCE_EXPOSURE` and remains exposed; the same historical sample is not fresh for X35b.
- **X35b (replacement study, FULL).** If a replacement is proposed: a sealed contract with a **non-inferiority** acceptance rule on the stated objective (Sharpe non-inferiority within a declared margin plus the stability improvement), paired; lineage to X35a preserved.
- **Stops progression if** no estimator meets the declared stability criterion without worse tracking (the v1 figure of a 15% turnover cut is a designer proposal) → keep the baseline; no X35b is proposed.

#### X36 — Vol floor and per-asset cap interaction
`Family 13 · C10 · Lane: X36a cap-binding diagnostic (MEASUREMENT) / X36b vol-floor policy evaluation (FULL, own sealed contract) · Data: ETF panel`
- **Mechanism.** SHY (short Treasuries, σ ≈ 1–2%) is very likely cap-bound at ±2 every month, making it a levered short-rate bet whose contribution was never isolated. Measure cap-bind frequency per asset, PnL and drawdown contribution of cap-bound positions, and one predeclared vol floor (4% annualised) as an alternative to the cap.
- **X36a (diagnostic).** Cap-bind frequency per asset; PnL and drawdown contribution of cap-bound positions (new statistics of published streams: `TARGET_PERFORMANCE_EXPOSURE`, T0, logged).
- **X36b (policy evaluation, FULL).** One predeclared floor evaluated under its own contract with an equivalence / non-inferiority formulation; "changes nothing material" is claimed only within a declared margin (the v1 figures are designer proposals).

### Cluster C11 — Strategy-state risk control

#### X37 — Own-drawdown-state conditioning
`Family 14 · C11 · Lane: MEASUREMENT premise · Data: published net returns`
- **Mechanism.** Strategy-state, not market-state — structurally distinct from the falsified crash-defense. If drawdowns are long slow declines (14 months), the underwater state is persistent, so being in a drawdown predicts further drawdown and an exposure cut reduces depth. Counter-mechanism: cutting at the trough delays recovery (already 24 months underwater) and momentum crashes reverse sharply.
- **Cheapest test.** Causal drawdown depth (from running peak) tercile at t → next-month and next-3-month net return; also own trailing 3-month return tercile; HAC; **episode jackknife** (12 episodes ≥ 4.6%; the effect must survive dropping each episode, and the 2022-23 episode in particular).
- **Overfitting risk.** Medium–high (few episodes; sequential dependence; a rule here is trivially fitted to 2022-23).
- **Falsification.** No conditional difference beyond the bar after the jackknife → no state rule; do not build.

#### X38 — Loss-clustering state
`Family 14 · C11 · Lane: MEASUREMENT (same family as X37)`
- State = ≥ 4 losing months in the trailing 6. One cell; same jackknife discipline.

### Cluster C12 — External-state conditioning

#### X39 — High-vol-regime conditioning per asset
`Family 15 · C12 · Lane: MEASUREMENT · Data: ETF panel (causal regime panel)`
- **Mechanism.** Vol-scaling already cuts size in high vol; the open question is hit rate: does the sign signal follow through less in the top vol tercile? The vol-breakout study covered only the compressed end (≤ 0.20).
- **Test.** Causal vol-percentile tercile × sign → forward sign-aligned hit rate and risk-adjusted return; 6 cells, BH-FDR.
- **Falsification.** As X18. Low expected value (first-order effect already handled by sizing).

#### X40 — Cross-asset correlation state — lineage `POST_EXPOSURE_DESIGN` (inversion of the crash-defense result)
`Family 15 · C12 · Lane: DEFERRED; admissible only in validation contexts T3/T4 (verified-protected holdout or prospective accrual)`
- **Mechanism.** The crash-defense Phase 0 revealed that vol/dispersion percentiles peak in the strategy's profit windows and are average in its drawdowns — which inverts to "high systemic-state periods are good for trend." That inference was generated *after* outcome exposure; it is a NEW HYPOTHESIS post-exposure and cannot be confirmed on the ETF panel.

#### X41 — CFTC positioning / crowding (COT) — DEFERRED
`Family 15 · C12 · Lane: none`
- Weekly COT data (free) not fetched; reserved by the carry preregistration for a future separate preregistration; mechanism: crowded speculative positioning → trend fragility. Futures-native; wait for Wave 1 infrastructure.

#### X42 — VIX / MOVE macro-uncertainty conditioning — DEFERRED (closed unless a distinct mechanism is stated)
`Family 15 · C12 · Lane: none`
- Same class as the crash-defense vol percentile (VIX ≈ equity implied vol; the causal realised-vol percentile already proxied it and was anti-aligned) and the same slow-episode trap as the yield curve for MOVE regimes.

### Cluster C13 — Carry × trend (futures only)

#### X43 — Carry–trend agreement premise
`Family 16 · C13 · Lane: MEASUREMENT premise → FULL · Data: Databento 18-root panel (carry series exist: front−next annualised basis, src/carry.py)`
- **Mechanism.** Carry is the expected return if spot is unchanged; trend is the expected return from continuation. Aligned positions (backwardation + uptrend, contango + downtrend) earn both; opposed positions pay roll drag against the trend. Standalone carry was ≈ 0 on this panel, so carry may still discriminate *within* trend positions without being an edge alone — the interaction, not the level.
- **Cheapest test.** Each month per root, 2×2 sort (trend sign × carry sign) → forward monthly sign-aligned return per unit risk; contrast aligned − opposed; per-sector robustness (4 sectors); **plus one declared bridge cell** conditioned on the ambiguous-but-non-zero trend state (|score| = 0.5) that tests the direction rule X44 actually contemplates, not merely generic agreement → **6 cells, one family** (Program v2 §11). Primary carry definition: front − next (the 12-month-deferred variant is not a second try). Panel inference decided before the run (Program v2 §7).
- **Exposure class / lineage.** Conditional strategy returns on the Databento panel: `TARGET_PERFORMANCE_EXPOSURE`; lineage `CARRY_STUDY_INFORMED`.
- **Overfitting risk.** Medium (burned panel; reserved family; one carry definition).
- **Implementation risk.** Medium (carry alignment to signal dates; roll congestion).
- **Est. PnL corr** of a carry-conditioned commodity trend with the commodity trend: 0.7–0.9.
- **Capacity.** High.
- **Stops progression if** the aligned − opposed contrast fails its declared gate pooled and in the declared number of sectors (the designer proposes the bar; Astra challenges; Aaron decides); an interval that includes zero is `unresolved` or `not_promoted`, not falsification. X44 proceeds only if the bridge cell (not merely generic agreement) clears its declared gate.
- **Trial accounting.** Declare Databento reuse; append each distinct constructed strategy-return series under the verified carry §10 convention; one shared dataset-level record with the mean-reversion program.

#### X44 — Carry as tie-breaker for ambiguous trend (conditional on X43)
`Family 16 · C13 · Lane: FULL (same family as X43)`
- **Scope (v2).** Where the composite is ambiguous but non-zero (|score| = 0.5), the carry sign decides direction; one rule; paired vs the commodity-sleeve baseline; licensed only by X43's declared bridge cell, not by generic agreement evidence.
- **Neutral-state carry (score = 0) is outside this scope by choice.** `CARRY_CONDITIONAL_ON_NEUTRAL_TREND_STATE` is recorded as a **DEFERRED / UNTESTED CONDITIONAL HYPOTHESIS**: carry conditional on a neutral TSMOM state is not logically identical to the unconditional carry sign (not promoted on this panel), so it is neither already ruled out nor supported; investigating it would need a separate future hypothesis and its own accounting. No research commitment is made here.

### Cluster C14 — Edge diagnostics (what the baseline actually is)

#### X45 — Hidden beta / static-premium decomposition of the core
`Diagnostics · C14 · Lane: MEASUREMENT · Data: published streams`
- **Mechanism.** XSMOM turned out to be partly a static premium (Sharpe halves under demeaning). TSMOM's net exposure is time-varying but its *average* may be structurally long (bonds and equities trended up more often than down over 2008–26). Measure: average net exposure by sleeve; monthly regression of TSMOM net returns on SPY, TLT, a commodity basket and UUP (HAC); and a **static-book control** — the Sharpe of the average-position book held constant, and the Sharpe of the residual (position − average position).
- **Reading rule.** A large drop in residual Sharpe after removing the static average-position book (the v1 figure of 50% is a designer proposal) indicates a material static component. This is a **retrospective full-sample description**: the average-position control is not an ex-ante deployable strategy and the finding is a description of the burned sample, not a test of any candidate.
- **Exposure class.** Static-book and residual Sharpes are new statistics of published streams: `TARGET_PERFORMANCE_EXPOSURE`, T0, logged.
- **Value.** Calibrates the priors in Section E for candidates that modify the same stream, and X28. It cannot establish the correlations of candidate streams that do not yet exist.

#### X46 — Convexity profile and crisis-alpha attribution
`Diagnostics · C14 · Lane: MEASUREMENT (same family as X45)`
- TSMOM monthly return vs SPY (and vs the equal-weight long book): quadratic fit (the "smile"); crisis-alpha attribution long vs short; tail-event correlation. Informs Cluster C7 and the mechanism claim behind "genuine crisis alpha."

---

## Section D — Mechanism clustering

| Cluster | Mechanism | Members | Expected dependence within cluster (prior; never proof of identity) | Designer's note |
|---|---|---|---|---|
| C1 Implementation transfer | Same signal, different wrapper | X01 X02 X03 X04 X05 | Total (by construction) | Not alpha research; deployment truth. Everything else on futures depends on it. |
| C2 Breadth | Same mechanism, more independent markets | X06 X07 X08 X09 X10 | Low across markets; X09 partly overlaps the outright book | The cluster with the strongest prior: literature plus a suggestive but confounded cross-project contrast (single-instrument SMC not promoted; 17-asset TSMOM `supported`) that varies signal family and breadth together. |
| C3 Speed | Same mechanism, different formation horizon | X11 X12 X13 | Medium (slow legs ≈ baseline) | The baseline already averages the legs; the object is leg *risk balance* and failure-period diversity. |
| C4 Signal representation | Same mechanism, different estimator or magnitude map | X14 X15 X16 X17 X18 | High (0.8–0.95 expected) | High dependence restricts independence claims and triggers `HIGH_REDUNDANCY_REVIEW`; ensemble value depends on failure-period diversity under declared margins, not on a correlation cutoff. |
| C5 Trend dynamics | Diffusion speed varies across episodes | X19 X20 | High as overlays | Nonlinear temptation; forms fixed in advance. |
| C6 Trend-state conditioning | Macro-driven vs idiosyncratic trends | X21 X22 X23 | High as overlays; one 8-cell family | Episode-count trap; jackknife ranked above significance. |
| C7 Directional asymmetry | Risk premium interacts with trend direction | X24 X25 | High | Whether crisis gains are short-side is the attribution question X24/X46 measure; crisis preservation applies only where a candidate replaces the deployed stream's defensive role or claims to preserve it. |
| C8 Risk budgeting / allocation | Where the risk sits, not what the signal is | X26 X27 X28 X29 | Total (≥ 0.95) except X28 | Equivalence within a declared margin is the robustness result; no significant difference is not equivalence. |
| C9 Execution & turnover | Path of trades, not the signal | X30 X31 X32 X33 X34 | Total (≥ 0.95) | X32 is futures-native and distinct from the ETF band. |
| C10 Volatility estimation | Sizing stability | X35 X36 | Total | Stability metrics decide, never Sharpe. |
| C11 Strategy-state control | Persistence of the strategy's own state | X37 X38 | High | Structurally distinct from external crash prediction; few episodes. |
| C12 External-state conditioning | Market-state variables | X39 X40 X41 X42 | High | Mostly deferred or closed; the family that has failed four times. |
| C13 Carry interaction | Two expected-return sources on one instrument | X43 X44 | Medium (0.7–0.9) | Reserved by the carry prereg; burned panel. |
| C14 Edge diagnostics | Measuring the baseline | X45 X46 | n/a | Cheapest, most informative, zero selection pressure. |

**Variant control (v2).** The v1 rule that treated members with realised PnL correlation ≥ 0.95 as one hypothesis for ledger purposes is deleted: it consolidated attempts after observing outcomes. Under Program v2 §0B every evaluated configuration is a `VARIANT_ATTEMPT` that is never merged or deleted; a `HYPOTHESIS_FAMILY` is declared prospectively (a declaration that two variants are cosmetic is admissible only before they run and only defines the family); and each attempt's `GOVERNED_N_TRIALS_CONTRIBUTION` follows the cited authoritative convention. Clusters in this table group *mechanisms* for reading; they are not ledger units.

---

## Section E — Estimated independence from the baseline

The ranking rule in one line: **portfolio contribution is what is being bought; standalone Sharpe is not.** A Sharpe-0.6 stream at correlation 0.2 raises a Sharpe-0.75 book far more than a Sharpe-1.2 stream at correlation 0.9.

| Tier | Meaning | Members | Evaluation rule at FULL |
|---|---|---|---|
| **N — candidate new PnL source** (tier assigned by mechanism: a separately held stream; the prior est. corr < 0.7 is a descriptor, not a membership rule) | Could be a separate line in the book | X06 (0.3–0.5), X09 (0.1–0.4), X11 fast leg (0.5–0.7), X28 long book (0.1–0.3), X43/X44 (0.7–0.9, borderline), X08 additions (0.6–0.8, borderline) | Standalone evidence package **and** marginal paired Δ at a fixed risk share |
| **M — modification of the same stream** (tier assigned by mechanism: the candidate changes how the baseline's stream is produced; the prior est. corr ≥ 0.85 is a descriptor, not a membership rule) | Changes how the baseline's stream is produced | X14–X20, X21–X27, X30–X38, X39–X42, X25 | **Paired comparison on the candidate's declared objective** (improvement, non-inferiority or equivalence with a declared margin). Standalone Sharpe is not admissible evidence. Report Δ-Sharpe, Δ-Calmar, Δ-skew, turnover Δ; crisis preservation applies only where the candidate replaces the deployed stream's defensive role or claims to preserve it (Program v2 §0 rule 11). |
| **I — implementation truth** (corr ≈ 1 by construction) | Same stream, different wrapper or bookkeeping | X01–X05 | Reconciliation identities (mechanical, may be `implementation_fact`); the X01 wrapper comparison is a paired empirical estimand with a reachable kill branch; feasibility bars. No crisis-return gate applies to accounting truth, contract-specification truth or feasibility facts. |
| **D — diagnostic** | Measures the baseline | X07, X45, X46 | Findings only; no promotion vocabulary applies |

**Dependence must be measured, never assumed.** Every FULL candidate reports: monthly return correlation with the baseline and with every previously accepted stream; rolling 36-month correlation; drawdown-episode overlap (Jaccard); crisis-window co-sign; sleeve attribution overlap; position-level overlap; tail-event correlation (worst-decile months). High dependence with an accepted stream triggers **`HIGH_REDUNDANCY_REVIEW`** (Program v2 §0 rule 12), which weighs those measures together with cost, capacity, tracking, operational reliability, implementation simplicity and marginal book contribution. High correlation restricts claims of *independence* (such a candidate is not described as a new PnL source); it does not establish a single alpha source, it imposes no automatic `not_promoted`, and it prohibits a separate line only if Aaron adopts such a cap as explicit portfolio policy. The v1 rule (corr ≥ 0.9 → `not_promoted` unless improvement *and* cheaper) is deleted.

**The exposure caveat on the priors above.** These correlations are priors from the mechanism, not measurements. X07, X45 and X46 (Wave 1) can replace the priors for candidates that modify the same stream and for sleeve overlap; they cannot measure the dependence of candidate streams that do not yet exist (X06, X09, X11 legs, X43), which is measured when those streams are built.

---

## Section F — Overfitting risk

Scored 0–10 on: degrees of freedom · family size · exposure contamination (design informed by published outcomes) · implementation ambiguity · data-quality risk · execution sensitivity.

| Risk band | IDs | Dominant risk | Mitigation written into the entry |
|---|---|---|---|
| **Low (≤ 3)** | X02 X03 X05 X07 X16 X24 X26 X28 X30 X35 X36 X45 X46 | none material | fixed variants; no selection |
| **Low–medium (3–4)** | X01 X06 X11 X14 X18 X31 | kill-branch reachability (X01); exposed leg Sharpes (X11) | A2 reachability check; confirmation off-panel |
| **Medium (5–6)** | X08 X09 X12 X15 X17 X19 X20 X21 X22 X23 X25 X27 X32 X33 X34 X39 X43 X44 | pair/threshold choice; episode counts; post-exposure design | families fixed; jackknife; futures/forward confirmation |
| **High (≥ 7)** | X13 X37 X38 X40 X41 X42 | per-sleeve fitting; few episodes; post-exposure inversion | deferred, or premise-with-jackknife only |

**Program-level multiplicity (v2).** Governed by the four-object model in Program v2 §0B: every computation that reveals an outcome is an `EXPOSURE_EVENT`; every distinct evaluated configuration is a `VARIANT_ATTEMPT` that is never merged or deleted; each `HYPOTHESIS_FAMILY` is declared prospectively with its multiplicity treatment (BH-FDR q = 0.10 is the repo's standing, challengeable proposal); and each attempt's `GOVERNED_N_TRIALS_CONTRIBUTION` follows the cited authoritative convention — for the Databento panel the verified carry §10 rule (one trial per distinct constructed strategy-return series, diagnostics excluded, frozen baseline 14 appended to, never recomputed); for the ETF panel no frozen convention exists and the historical count is an Aaron decision recorded in Wave 0. One visible attempt is not automatically `+1`. The 45-cell grid's historical classification inside the core's record stays frozen; later designs informed by its outcomes carry `ROBUSTNESS_GRID_INFORMED` lineage, appended as use-rows; an authorised correction process handles any later-discovered omission — history is not rewritten and "never revisit" is not a bar to such corrections. Within-family BH-FDR does not control error across adaptively selected families, and a Deflated Sharpe does not repair a biased sample or a mis-specified paired comparison; the primary claim and the selection/continuation rules are frozen before FULL work.

---

## Section G — Required data

| Data | Exists? | Location / status | Needed by |
|---|---|---|---|
| ETF adjusted close, 30 names, 1993→2026-06-12 | Yes | `data/close_prices_raw.csv` (yfinance cache) | X07–X09, X11, X14–X39, X45, X46 |
| ETF daily infra (causal vol %ile, ER, dispersion) | Yes | `src/regime.py`, `src/daily.py`, `output/regime_variables_pit.csv` | X18, X21, X30, X34, X39 |
| Published streams (monthly net, per-asset net, positions, weights) | Yes | `output/monthly_returns.csv`, `output/dd_per_asset_net.csv`, `output/monthly_portfolio_weights.csv` | X07, X24, X28, X37, X45, X46 |
| Databento GLBX.MDP3 commodity panel, 18 roots, 2010-06→2026-06 (ohlcv-1d, statistics, definition) | Yes | `C:\Users\Aaron\quant-data\commodity-carry` (9.5 GB); roll/returns/cost code in `commodity-carry-research/src/` | X01–X03, X06, X12, X32, X43, X44 |
| Contract specs (tick, multiplier) for 18 roots | Yes | `commodity-carry-research/src/config.py::CONTRACT_SPECS` (apply the price-unit divisor) | X01, X05, X32 |
| Financial futures (ES/NQ/RTY/YM, ZT/ZF/ZN/ZB/UB, 6E/6J/6B/6A/6C/6S/6N, NKD) | **Not established as owned in the available orientation; inventory pending** | Databento GLBX.MDP3 is the established vendor path; cost/coverage unverified; no purchase authorised | X04, X10, hybrid deployment |
| Long-history futures (pre-2008, decades) | **Not established as owned; inventory pending** | vendor decision after inventory and cost/coverage assessment (D2) | context T2 evidence for ETF-designed hypotheses, with the literature's own exposure of those decades disclosed |
| Exchange initial-margin tables; micro-contract specs | **No** (public) | CME margin pages (dated snapshot) | X05, X32 |
| CFTC COT (weekly) | **No** (public) | cftc.gov | X41 (deferred) |
| OHLC for range-based vol | Partly (yfinance has OHLC; cache is close-only) | any re-fetch goes through the Wave-0 lockbox procedure: a new snapshot with its own hash, truncated at the frozen boundary for working use, never overwriting the frozen panel (a re-fetch that revises historical adjusted prices is a new dataset) | optional for X35a (not required) |
| Data after the frozen snapshot boundary | Exists at the vendor; exposure status `UNKNOWN_PENDING_WAVE0_VERIFICATION` | not refreshed into the working cache; T3 (verified-protected holdout) or T4 (prospective accrual after a seal) per Program v2 §0A; each opening is an exposure event | validation contexts T3/T4 |

---

## Section H — Cheapest falsification test per hypothesis

Compact form; the full test is in each Section C entry. "Sessions" = rough builder-session estimate (Opus, high effort), infrastructure included where it does not yet exist. "Stops progression if" never means `falsified`; every number is a designer proposal for the normal design → challenge → decision process; lanes are EXPLORATORY / MEASUREMENT / FULL only.

| ID | Cheapest test | Lane | New code? | Sessions | Stops progression if… |
|---|---|---|---|---|---|
| X01 | paired wrapper estimand under a sealed contract (three states; secondary arms X02b, X03 performance) | FULL | futures signal adapter | 3–4 | `MATERIAL_DEGRADATION_SUPPORTED` (paired interval beyond the declared tolerance); mechanical failure is a separate kill; `UNRESOLVED_INSUFFICIENT_PRECISION` only when the interval straddles the declared boundary, not merely because it contains zero |
| X02a | causal signal input; dollar-ledger reconciliation residual; units; roll causality; sign-agreement rates | MEAS (mechanical + design-informing) | yes (chain + ledger) | 2 | any identity fails (mechanical kill); no performance comparison pre-seal |
| X03 | pre-seal: roll dates, counts, OI crossover, availability; performance arm inside X01 | MEAS (structural) / arm of X01 | small | 0.5 | n/a pre-seal; materiality claimed only within a declared margin inside X01 |
| X04 | as X01 per sleeve | — | after acquisition | — | — |
| X05 | contract counts / rounding error / margin-to-equity at NAV set | MEAS | small | 1 | rounding error > 25% risk in > 1/3 markets |
| X06 | ENB and dependence structure of 18-root trend PnL; principal control = matched futures subset under common dates, construction and risk budget | MEAS → FULL | reuse X02a infra | 1 (+2 FULL) | no effective breadth over the matched futures subset under the declared margin; ETF-sleeve correlation is secondary descriptive evidence only, never the stopping rule |
| X07 | 17×17 trend-PnL corr, ENB | MEAS | none | 0.5 | n/a (diagnostic) |
| X08 | dropped-ETF trend-PnL corr vs anchors | MEAS | none | 0.5 | all ≥ 0.6 |
| X09 | route pending (D8): A = structural overlap screen at position level (no PnL) → sealed FULL; B = declared exploratory performance exposure | X09_ROUTE_PENDING_AARON | small | 1 (+1) | A: spreads reconstruct held outrights within a declared margin; performance study: declared marginal gate not met; high correlation → `HIGH_REDUNDANCY_REVIEW`, not a kill |
| X11 | X11a: 4-leg sub-strategies — dependence, DD overlap, crisis split (exposed, logged); X11b: ensemble under own sealed contract | MEAS (a) / FULL (b) | small | 1 (+1) | X11a: no failure-period diversity under declared margins; X11b: paired gate not met (`unresolved` if the interval merely includes zero) |
| X12 | {1,3,6,12} vs {3,6,12} on futures, paired | FULL (futures) | none | 0.5 | paired Δ(with − without) entirely on the "helps" side of the declared margin → contradicts the tested claim under this study (not general falsification) |
| X14 | \|score\| and \|z12\| deciles → forward risk-adj return; two shape contrasts (monotone, concave) | MEAS | small | 0.5 | both contrasts fail their declared gates (stops X15; not falsification) |
| X15 | one mapping vs baseline, paired | FULL | small | 1 | Δ ≤ 0 or turnover +20% |
| X16 | 4 estimators → PnL dependence matrix | MEAS | medium (EWMA, slope, Donchian) | 1.5 | no failure-period diversity under the declared margin → `HIGH_REDUNDANCY_REVIEW` for any ensemble proposal (not an automatic kill, not proof of one alpha) |
| X17 | EW/median/majority ensemble vs baseline, paired | FULL | small | 1 | Δ-Sharpe ∋ 0 and Δ-Calmar ≤ 0 |
| X18 | ER tercile × sign → hit rate (6 cells) | MEAS | none | 0.5 | 0/6 |
| X19 | HAC regression on z, Δz, age + 3×3 sort | MEAS | small | 1 | Acceleration, age and the 3×3 corner contrast all fail their declared gates; level is a covariate only. |
| X20 | top-decile Δz tail cell | MEAS | none | 0.25 | ∋ 0 |
| X21–23 | breadth/dispersion/concentration terciles → fwd net return, jackknife (8 cells) | MEAS | small | 1 | 0/8 after jackknife |
| X24 | long/short split per sleeve (5 cells) | MEAS | none | 0.5 | no stable \|Δ\| ≥ 0.3 |
| X25 | one asymmetric rule, crisis-retention gate | FULL | small | 1 | retention < 70% or Δ ∋ 0 |
| X26/27 | sleeve-risk variants, paired equivalence / non-inferiority with a declared margin | FULL | small | 1 | interval neither inside the margin nor beyond it → `unresolved`; inside → equivalence supported (keep baseline); beyond → lead in T0 |
| X28 | 3 fixed blends with the long book | MEAS | none | 0.25 | no Calmar gain |
| X30 | 5 execution-day variants | MEAS | small (daily weights) | 1 | dispersion beyond the declared margin, or a crisis sign flip (no CI-breach rule) |
| X31 | 4-tranche variant, paired | FULL | small | 0.5 | paired interval beyond the declared non-inferiority margin |
| X32 | 2 hysteresis thresholds on futures, paired | FULL | medium | 1 | both reduce net Sharpe |
| X33 | 2 smoothing variants, paired at 2/5/10 bps | FULL | small | 1 | turnover −15% not reached or Δ ≤ 0 |
| X34 | −2σ event → comparable fixed forward horizon vs matched unconditional (6 cells); eligible population defined at design | MEAS | small | 1 | no adverse-drift premise under the declared bar |
| X35 | X35a: 4 vol estimators, stability metrics (exposed outputs logged); X35b: sealed non-inferiority replacement study | MEAS (a) / FULL (b) | small | 1 | X35a: no estimator meets the declared stability criterion without worse tracking; X35b: non-inferiority margin not met |
| X36 | X36a: cap-bind statistics (exposed, logged); X36b: one floor under its own contract, equivalence formulation | MEAS (a) / FULL (b) | none | 0.25 | X36b: equivalence within the declared margin → keep the cap |
| X37/38 | DD-state / loss-cluster terciles, jackknife | MEAS | none | 0.5 | nothing survives jackknife |
| X39 | high-vol tercile × sign (6 cells) | MEAS | none | 0.25 | 0/6 |
| X43 | 2×2 trend × carry sort + one bridge cell at \|score\| = 0.5 (6 cells) | MEAS → FULL | small (carry series exist) | 1 (+1) | aligned − opposed fails its declared gate (`unresolved` / `not_promoted`, not falsification); X44 needs the bridge cell |
| X44 | carry tie-break rule, paired | FULL | small | 0.5 | Δ ∋ 0 |
| X45/46 | net-exposure regression, static-book control, smile | MEAS | none | 0.5 | n/a (diagnostic) |

---

## Section I — Expected research value

Value (0–10) = mechanism plausibility + potential incremental Sharpe + potential diversification + potential drawdown improvement + scalability, compressed. Risk (0–10) as in Section F. Cost = falsification cost (1 cheap · 2 moderate · 3 expensive/needs acquisition). These are designer judgments, disclosed as such.

| ID | Value | Risk | Cost | Est. corr | Why the value is where it is |
|---|---|---|---|---|---|
| X01 | 8 | 3 | 2 | ≥ 0.9 | Prerequisite for any deployment; KB #1 by information gain; data in hand |
| X02 | 7 | 1 | 1 | — | Futures PnL is worthless until this identity holds |
| X03 | 4 | 1 | 1 | — | Small, closes a hidden DoF |
| X04 | 8 | 5 | 3 | ≥ 0.9 | High value, blocked on acquisition |
| X05 | 7 | 1 | 1 | — | Deployment feasibility at Aaron's NAV |
| X06 | 8 | 3 | 2 | 0.3–0.5 | Strongest prior (literature plus a suggestive, confounded in-workspace contrast); data in hand; matched-futures control isolates breadth |
| X07 | 6 | 1 | 1 | — | Replaces guesses with numbers |
| X08 | 4 | 5 | 1 | 0.6–0.8 | Breadth inside a burned panel; lead only |
| X09 | 7 | 5 | 1 | 0.1–0.4 | Genuinely different PnL source if it exists; cheap |
| X10 | 6 | 4 | 3 | 0.3–0.6 | Blocked on acquisition |
| X11 | 8 | 3 | 1 | 0.5–0.7 (fast) | Failure-period diversity of the same mechanism; low DoF |
| X12 | 4 | 4 | 2 | — | Replication of an exposed fact |
| X13 | 4 | 8 | 2 | — | Highest overfit risk |
| X14 | 6 | 3 | 1 | ≥ 0.9 | Cheap gate on the whole "continuous signal" family |
| X15 | 5 | 4 | 2 | ≥ 0.9 | Conditional |
| X16 | 7 | 2 | 1 | 0.8–0.95 | Decides whether Family 9/10 exists at all |
| X17 | 5 | 3 | 2 | ≥ 0.9 | Conditional |
| X18 | 5 | 3 | 1 | ≥ 0.9 | Cheap; distinct from vol-breakout |
| X19 | 6 | 6 | 1 | ≥ 0.9 | Real mechanism; nonlinear temptation |
| X20 | 4 | 6 | 1 | ≥ 0.9 | Tail cell |
| X21 | 6 | 6 | 1 | ≥ 0.9 | Plausible; episode trap |
| X22 | 4 | 5 | 1 | ≥ 0.9 | |
| X23 | 3 | 5 | 1 | ≥ 0.9 | |
| X24 | 7 | 2 | 1 | — | Structural, cheap, deployment-relevant |
| X25 | 6 | 5 | 2 | ≥ 0.9 | Conditional; crisis-alpha at stake |
| X26 | 5 | 2 | 1 | ≥ 0.95 | Equivalence within a declared margin is the robustness result |
| X27 | 3 | 5 | 2 | ≥ 0.95 | Adds estimation for little |
| X28 | 6 | 1 | 1 | 0.1–0.3 | Deployment allocation |
| X29 | — | — | — | — | Deferred (no validated subs) |
| X30 | 6 | 1 | 1 | ≥ 0.95 | Robustness prerequisite |
| X31 | 5 | 2 | 2 | ≥ 0.95 | |
| X32 | 6 | 3 | 2 | ≥ 0.95 | Futures-native, distinct from the ETF band |
| X33 | 4 | 5 | 2 | ≥ 0.95 | Post-exposure |
| X34 | 5 | 5 | 1 | ≥ 0.9 | Targets the crash-type loss directly |
| X35 | 5 | 2 | 1 | ≥ 0.97 | Stability |
| X36 | 3 | 1 | 1 | ≥ 0.97 | |
| X37 | 5 | 7 | 1 | ≥ 0.9 | Few episodes |
| X38 | 3 | 7 | 1 | ≥ 0.9 | |
| X39 | 3 | 3 | 1 | ≥ 0.9 | Low expected value |
| X40 | 3 | 8 | — | ≥ 0.9 | Post-exposure inversion |
| X41 | 5 | 5 | 3 | ≥ 0.9 | Data + reserved |
| X42 | 2 | 6 | — | ≥ 0.9 | Closed unless new mechanism |
| X43 | 7 | 5 | 2 | 0.7–0.9 | Reserved interaction; data in hand |
| X44 | 4 | 4 | 2 | ≥ 0.9 | Conditional |
| X45 | 7 | 1 | 1 | — | Tells us what the edge is |
| X46 | 5 | 1 | 1 | — | |

---

## Section J — Ranked research queue and selections

Priority = value, discounted by risk and by falsification cost, with a hard rule: **an idea whose cheapest test needs data that does not exist is deferred regardless of value.** Ties broken toward lower correlation with the baseline.

### J.1 The queue (tier, then order within tier)

| Tier | Order | IDs | One-line rationale |
|---|---|---|---|
| **1 — run first (converged order)** | 1 | X07, X24, X45, X46 | Baseline anatomy: what the baseline actually contains (breadth, directional attribution, static exposure, defensive behaviour). Cheap and selection-free, but **not exposure-free**: new decompositions of burned streams are logged as `TARGET_PERFORMANCE_EXPOSURE` |
| | 2 | X02a, X05, structural roll diagnostics | Futures mechanical truth and feasibility at the NAV grid; resolves the largest downstream validity risk before any performance is interpreted |
| | 3 | X01 (X02b and X03 performance arms inside its contract) | The registered #1 hypothesis; data in hand; paired estimand with a reachable kill branch; runs only after its seal |
| | 4 | X06 | Breadth on real futures against a matched futures control; the strongest prior in the map |
| | 5 | X11a | Speed-leg structural description, separated from any ensemble test; the dependence structure was never exposed |
| | 6 | X16 | Decides whether estimator diversity exists before any ensemble is proposed; high dependence restricts independence claims without killing a low-cost improvement |
| **2 — premise tests, then conditional FULLs** | 7 | X14, X18 | Cheap gates on the continuous-signal and path-quality families |
| | 8 | X30, X35a, X26 | Robustness of execution day, vol estimator, sleeve budget — each judged by a declared dispersion, stability or equivalence margin, never by the absence of a significant difference |
| | 9 | X09 | Spread trend — the cheapest candidate new PnL source |
| | 10 | X43 | Carry × trend — reserved, data in hand, needs ledger coordination |
| | 11 | X28 | Deployment blend |
| | 12 | X19/X20, X21–X23 | Dynamics and breadth-state premises with jackknife |
| | 13 | X31, X32, X33, X34 | Execution refinements; X32 only after Wave 1 |
| **3 — conditional or low value** | 14 | X15, X17, X25, X44, X27, X12 | Only if their premise passes |
| | 15 | X08, X36, X37/X38, X39 | Low value or high episode risk; run only if budget remains |
| **4 — deferred** | — | X04, X10, X13, X29, X40, X41, X42 | Data not established as owned (inventory pending), no lines past the §9 gate, post-exposure origin admissible only in T3/T4, or closed class |

### J.2 Five highest-priority ideas — and why

1. **Baseline anatomy — X07, X24, X45, X46.** What does the baseline actually contain? Breadth, directional attribution, static exposure and defensive behaviour are established before they are used as design premises. Cheap and selection-free, but the new decompositions are exposure events and are logged.
2. **Futures mechanical truth and feasibility — X02a, X05, structural roll diagnostics.** Can the futures representation reconcile to a dollar ledger and be implemented across the declared NAV grid? This resolves the largest downstream validity risk before any performance is interpreted.
3. **X01 Commodity-sleeve futures transfer under the paired contract** (with the X02b and X03 performance arms inside it). The registered #1 hypothesis, data on disk, roll/cost code existing; its prior failure mode — an unreachable kill branch — is addressed by the three-state paired design, and the first futures performance exposure occurs only after the seal.
4. **X06 Commodity breadth against a matched futures control.** Does expansion add effective breadth beyond the matched subset, holding construction, dates, risk convention and sleeve budget fixed? The strongest prior in the map, now tested without confounding breadth with wrapper.
5. **X11a Speed-leg structural description.** Do the existing legs fail differently enough to justify a separate, sealed ensemble study (X11b)? Structural description is separated from any ensemble performance claim, and its dependence structure was never exposed.

X16 follows closely; a high estimator dependence restricts independence claims but does not by itself kill a low-cost ensemble or implementation improvement. X09 deserves an early, correctly classified step once its spread mechanics are defined and Aaron has chosen its route (D8).

### J.3 Five high-upside, high-risk ideas — and why they are not first

1. **X43 Carry × trend agreement.** A second expected-return source on the same instrument; but the panel is burned by carry, both standalone carry arms were not promoted under their tested definitions, and the interaction is easy to over-read across four sectors.
2. **X09 Spread trend.** The cheapest candidate for a genuinely new PnL source (est. corr 0.1–0.4); the risk is pair selection — hence four economically fixed pairs and a ban on additions.
3. **X19 Acceleration and trend age.** A real diffusion mechanism with nonlinear temptations; forms fixed to linear + terciles.
4. **X21 Trend breadth predicts continuation.** Plausible macro mechanism; slow regimes mean a handful of episodes — the exact trap that killed the yield-curve overlay, so the jackknife is ranked above significance from the start.
5. **X37 Own-drawdown-state conditioning.** Structurally distinct from the falsified crash-defense, but twelve episodes and one dominant 2022-23 episode make it the easiest thing in this map to overfit.

### J.4 Five cheap premise tests — and why

1. **X14 Trend-strength deciles** — one afternoon on the existing panel; gates Family 4 entirely.
2. **X18 Efficiency-ratio conditioning** — the causal ER already exists in `src/regime.py`; six cells.
3. **X45/X46 Hidden beta and convexity** — published streams only; converts Section E's priors for same-stream candidates into measurements (it cannot measure candidate streams that do not yet exist); its new statistics are logged as exposure.
4. **X30 Execution-day robustness** — the daily infrastructure exists; five variants; the answer matters for every futures deployment.
5. **X35a Vol-estimator stability diagnostic** — four fixed estimators judged by stability, never by Sharpe; any replacement (X35b) needs its own sealed non-inferiority study, and the diagnostic's exposed outputs are not fresh for it.

### J.5 Five deliberately deferred ideas — and why

1. **X04/X10 Financial-futures transfer and breadth** — the data is not established as owned in the available orientation; the Wave-0-defined inventory comes first, then acquisition (and the hybrid futures/ETF structure for credit and REITs) is Aaron's decision (D1), with the long-history question (D2) decided on the same inventory. No purchase is authorised.
2. **X13 Asset-class speed specialization** — the highest overfitting risk in the map; X11 will show whether there is anything to specialise, for free.
3. **X29 Dynamic strategy allocation** — there are zero validated sub-strategies today; allocation among them is a question for after Waves 2–5.
4. **X40 Correlation-state conditioning** — a hypothesis generated by inverting an exposed negative result; admissible only in validation contexts T3/T4 (verified-protected holdout or prospective accrual).
5. **X41/X42 COT positioning and VIX/MOVE** — data not fetched and reserved elsewhere (X41); same class as two falsified overlays with the same episode-count trap (X42).

---

## Section K — Decisions requested from Aaron, and what happens next

Nothing below is authorised by this document; each is a decision only Aaron can take.

| # | Decision | Why it is needed now | Default if undecided |
|---|---|---|---|
| D0 | Astra Round-2 artifact hash (`0a89d439…579869`) — **CLOSED 2026-09-08: declared authoritative by Aaron; recomputed and matched** | Transport reconciliation only; no architecture change was made | — |
| D1 | Financial futures (GLBX.MDP3: ES/NQ, ZT/ZF/ZN/ZB/UB, 6E/6J/6B/6A/6C/6S/6N, NKD) and the hybrid structure (credit and REITs stay ETF) — **DEFERRED** until the Wave-0-defined inventory establishes ownership and a coverage/cost assessment exists | Unblocks X04/X10 and a real deployment universe | Program runs commodity-only futures (Waves 1–2) and ETF-panel premises; no purchase authorised |
| D2 | Long-history futures (pre-2008 decades) — **DEFERRED** until inventory, gap analysis and cost/coverage assessment | Context T2 evidence for ETF-designed hypotheses (with the literature's exposure of those decades disclosed) | Validation relies on T1 and T3/T4 contexts; no purchase authorised |
| D3 | Confirm the deployment NAV bracket for X05/X32 (feasibility grid; NAV is never chosen by historical strategy performance) | Feasibility bars depend on it | Use the declared grid {$100k, $250k, $500k, $1M} |
| D4 | Authorise Wave 0 execution (governance only): `qros-state.yaml`, both ledgers, `SAMPLE_REUSE.md`, `TRIAL_LEDGER.md`, the lockbox procedure, the inventory *specification*, and the canonical-verification tasks — after the §0A/§0B/§1 rules are accepted; and **record the ETF-panel historical trial-count convention as an open Aaron decision inside the ledger** (no frozen convention exists; deciding it is not a Wave-0 prerequisite; the 45-cell grid's historical classification stays frozen; its outcomes' later use is recorded as lineage). Wave-0 authorisation depends only on the genuine governance prerequisites in Program v2 §2 — not on D1, D2, D8, D9 or any candidate-specific threshold | Required by the L6 runtime; nothing MEASUREMENT-lane runs before the ledgers exist | Program does not start |
| D5 | Adopt the lockbox procedure (per-dataset frozen snapshot with hash; refreshes as new snapshots, never overwriting; release rule; T3-vs-T4 classification; exposure status `UNKNOWN` until verified) | Protects the only ETF-panel holdout that will ever exist | Data drifts into every exploratory run and is lost as holdout |
| D6 | KB hypothesis cards — **DEFERRED**: created when a candidate enters material research requiring them | KB rule 16 and provenance conventions | Cards written at each candidate's preregistration |
| D7 | Seat routing: Opus proposes and builds; a fresh GPT-6 Astra session challenges each FULL preregistration (A2) and a new fresh Astra session verifies (Stage I); Fable only on the QROS triggers that apply; certification of adopted reviewer contributions by a non-producing session not of the contributing family; ChatGPT as Aaron's workflow assistant only | Independence lives in the session; this map's author must not certify its own program | As stated |
| D8 | `X09_ROUTE_PENDING_AARON`: A (structural non-redundancy screen → sealed FULL) or B (declared exploratory performance exposure → logged lead) | Determines whether X09's first step generates performance exposure | Neither route runs |
| D9 | Whether a sealed same-period wrapper comparison (X01) may be classified above `supported` — `CANONICAL_CLASSIFICATION_PENDING_VERIFICATION` for Aaron and the KB curator | Determines the ceiling of the X01 performance claim | Capped at `supported` in context T1 |
| D10 | **Strategy-build gate** (Program v2 §0 rule 14): when any candidate first reaches genuine strategy-construction readiness the session stops and reports `STRATEGY_BUILD_READINESS = READY` with `AARON_ACTION_REQUIRED = decide whether to authorise Opus to begin strategy construction` | No premise pass, completed Wave 0 or completed mechanical work authorises construction | `STRATEGY_BUILD_READINESS = NOT_READY` for every candidate today |

The staged plan, evidence contexts, exposure and trial model, seat routing, family map and per-wave gates are in `TSMOM_EXTENSION_RESEARCH_PROGRAM_v2.md`. Execution state at drafting: `WAVE_0_EXECUTED = NO` · `WAVE_1_EXECUTED = NO` · `STRATEGY_BUILD_STARTED = NO` · `FULL_ALPHA_TESTING_STARTED = NO` · `PROTECTED_FORWARD_DATA_OPENED = NO` · `NEW_DATA_PURCHASED = NO`.

---

*Treat "no incremental edge exists" as a valid final result for every entry above. A falsified hypothesis in this map is a permanent research asset; do not overwrite it, rename it, or split it into cosmetic variants.*
