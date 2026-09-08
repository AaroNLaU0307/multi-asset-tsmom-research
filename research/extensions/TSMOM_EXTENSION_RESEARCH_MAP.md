# TSMOM Extension Research Map

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
MUST_NOT_BE=sole certifier of any FULL result in this program; author of a sealed preregistration without a fresh Sol A2 challenge; modifier of the frozen baseline
LANE=EXPLORATORY
OUTCOME_EXPOSED=TARGET_METRIC (read-only: the published full-sample core, sleeve, robustness-grid and overlay results were read during design; no new outcome was generated)
PREREG_SEALED=N/A
WHY_THIS_MODEL=Aaron invoked Fable directly. Recorded as a departure from the default Opus architect seat, not a silent substitution.
```

**Exposure statement.** The designer of this map has read every published full-sample result of the core and its overlays (Sharpe 0.75, sleeve attributions, the 45-combination robustness grid, the cost sweep, the drawdown diagnostic). Several hypotheses below are therefore *partly informed by exposed outcomes*. Each such case is labelled **`POST-EXPOSURE DESIGN`** in its entry, and the program (companion document) routes its confirmation to a sample the design did not see. The research-axis exposure ledger for this project does not yet exist (see Wave 0 in the program); this document is the first row it must record.

**Companion documents (same directory):**
- `TSMOM_EXTENSION_RESEARCH_PROGRAM.md` — the staged execution plan (Waves 0–6), seat routing, trial-ledger and redundancy rules.
- `idea_registry/IDEA_REGISTRY.csv` — one machine-readable row per hypothesis (IDs `X01`–`X46`).
- `DASHBOARD.md` — one row per candidate; all rows are `PROPOSED` today.

---

## How to read this document

- **Hypothesis IDs** are `X01`–`X46`. Prefix `X` = extension candidate. IDs are stable; never renumber.
- **Lane at entry** is the QROS lane the first test runs in (`MEASUREMENT` for premise/structure tests, `FULL` only once a preregistration is sealed). An entry marked `DEFERRED` has no lane yet.
- **Estimated PnL correlation with the baseline** is a designer's prior, not a measurement. It is the single most important number for ranking, and Section E says why.
- **Falsification condition** is written so that a fresh Stage A2 reviewer can check kill-branch reachability. Thresholds marked *(A2 sets)* are deliberately left to the preregistration stage; this document does not seal anything.
- Vocabulary follows the knowledge base: `confirmed · supported · not_promoted · falsified · unresolved`; "REDUNDANT" is recorded as `not_promoted` with the reason `redundant_same_pnl_source` (no KB enum exists for it). There is no `insufficient_evidence`.

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
| Crisis alpha | GFC 2008 **+11.6%**, COVID 2020 **+7.3%**, calendar 2022 **+15.0%** | the short side of risk assets and bonds during sustained macro trends |
| Monte Carlo | P(DD ≥ 20%) ≈ 45%, P(DD ≥ 30%) ≈ 7% | realized −15.6% was on the benign side |
| Construction sensitivity | EW 0.70 / inverse-vol 0.78 / ERC 0.73 (5 bps); vol window 40/60/90/120 d → 0.76/0.75/0.72/0.71; per-asset target vol 8–15% → all 0.75 | the edge lives in signal direction + breadth, not in sizing details |
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

A modest, broad, **slow** trend premium harvested across five loosely related sleeves, whose value is disproportionately **convex**: it earns its reputation in sustained macro trends (2008, 2020, 2022) by being short risk assets and bonds, and it pays for that in long, grinding, multi-sleeve reversals in calm markets. On this sample the slower legs carried more of the Sharpe than the 1-month leg; sizing and aggregation choices are nearly irrelevant; costs are the binding constraint at the illiquid end. It is a replication of a published factor on ETF proxies, with wide uncertainty on magnitude and no evidence yet on the instruments a real program would trade.

What is **not** known about the edge, and should be measured before anything is built (Cluster 14, Section C): its average net exposures and hidden beta (a static-premium decomposition was done for XSMOM, never for TSMOM); its convexity profile against a long book; the split of PnL and crisis alpha between long and short positions; and the effective number of independent *trend* bets in the 17-asset book (the ≈12-cluster figure is on returns, not on trend PnL).

### A.5 Sample and exposure state (governs everything below)

| Sample | State | Consequence |
|---|---|---|
| ETF panel 2007-04 → 2026-06 (`dataset.yfinance.multi-asset-etf-panel`) | **Burned 6 of 6** (KB `relationships.csv` rows 16–21: core, 4 overlays, XSMOM). All published sleeve/asset/robustness figures are target-metric exposures. | Every new hypothesis on it is a 7th+ reuse and must be declared (`SAMPLE_REUSE.md`). Results on it are **leads**, never independent confirmation. |
| Databento commodity panel, 18 CME roots, 2010-06 → 2026-06 (`dataset.databento.commodity-futures-curves`, on disk at `C:\Users\Aaron\quant-data\commodity-carry`, 9.5 GB) | Burned by commodity-carry (frozen `N_trials = 14`); consumed for cost accounting only by `c1-drag-audit` (ledger deliberately not extended). **No TSMOM performance trial has ever run on it.** | First TSMOM trial extends the ledger. A shared ledger with the mean-reversion program is required if both consume it. GFC is absent (starts 2010-06). |
| Financial futures (ES/NQ, ZT/ZF/ZN/ZB, 6E/6J/6B/6A) | **Not acquired**; vendor path (Databento GLBX.MDP3) established; cost/coverage unverified. | An Aaron decision, not a research step. See Program §Decisions. |
| Pre-2008 futures history (decades) | Not acquired; would need a long-history vendor. | The largest honest OOS gain available to this program: same markets, different decades. Decision for Aaron. |
| Forward accrual after 2026-06-12 | ≈3 months exist today; untouched. | Proposed **lockbox**: do not refresh the working panel; open only inside a sealed confirmation (Program Wave 0). Weak for years, but it is the only ETF-panel OOS that will ever exist. |
| Pre-2008 reduced-universe ETF window (≈9 assets live 2003–2007) | Excluded from the core's evaluation ("a different strategy") and therefore **never evaluated**. | Usable for *structural* replications (leg correlations, long/short split), never for confirming the 17-asset strategy. |

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
| 7 | Inverse-vol and ERC risk parity vs equal-weight | **Indistinguishable** (0.78 / 0.73 vs 0.70; CIs overlap) — but note the comparison was *unpaired* (Δ judged against the EW CI). | `output/RISK_PARITY_CONTROL_REPORT.md` |
| 8 | Lookback / target-vol / vol-window neighbourhood | **Robust**, [0.38, 0.87]; default 71st percentile; {6,12} = 0.87 is the exposed peak. | `output/ROBUSTNESS_REPORT.md` |

### B.2 Tested or closed elsewhere in the workspace

| Item | Where | State | Consequence for this map |
|---|---|---|---|
| Commodity carry, XS tercile and TS sign, 18 CME futures | `commodity-carry-research` | **NOT PROMOTED** 0/5 gates each: net Sharpe −0.003 / −0.126, ≈26 robustness variants all ≪ 0.30, gross ≈ net (cost is not the explanation) | Standalone carry is dead on this panel. **Carry × trend interaction is untested and explicitly reserved** by that prereg's §9 for a separate preregistration. |
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

### Cluster C1 — Implementation transfer (wrapper truth)

#### X01 — Commodity-sleeve futures transfer, matched-map arm
`Family 1 · C1 · Lane: FULL (after prereg) · Data: Databento 18-root panel (in hand) + ETF sleeve stream (read-only)`
- **Mechanism.** Not a new premium. Tests whether the futures wrapper (OI-max front-contract roll, tick + commission costs, no expense ratio) preserves the commodity sleeve's trend PnL relative to the ETF wrapper (expense ratio, fund roll schedule, tracking). This is the executable continuation of KB `hypothesis.tsmom.futures-transfer` (registered, WOUNDED, ranked #1 by expected information gain).
- **Inefficiency.** Same underreaction / slow diffusion + crisis shorting.
- **Independence.** None by construction; expected corr ≥ 0.9 with the ETF commodity-sleeve stream. Value is deployment truth, not alpha.
- **Horizon.** Monthly; 1–12 m formation.
- **Data.** Chained held-contract returns under the A1 OI-max(t−1) roll rule (`commodity-carry-research/src/roll.py`, `returns.py`); costs via `cost_per_side_pct` with the price-unit divisor applied at the boundary (100× defect on the 8 cents-quoted roots); the c1-drag-audit's frozen primary ETF→futures map (D5) reused unchanged.
- **Cheapest premise test.** (i) Monthly return correlation of each mapped pair (USO↔CL chain, UNG↔NG, GLD↔GC, DBA↔ag basket): expect ≥ 0.9. (ii) Month-by-month sign-agreement rate of the locked composite computed on the ETF vs on the chained futures index: if < 85% for any pair, the construction is wrong (roll jumps) and must be fixed before any PnL (X02).
- **Overfitting risk.** Low: locked signal, one roll rule, one map. The real risk is a decision rule whose kill branch is unreachable (the drag audit's defect); Stage A2 must verify reachability against the measurable range (`lesson.rule-domain-analysis-before-freeze`).
- **Implementation risk.** High: roll logic, contract specs, price units, dead serial months in grains, settlement-time vs ETF-close alignment for signal dating.
- **Est. PnL corr with baseline sleeve.** ≥ 0.9.
- **Capacity.** High (CL, NG, GC, ZC are among the most liquid futures).
- **Falsification.** On the common 2010-07 → 2026-06 window, with the locked signal and one ex-ante roll rule: paired-difference bootstrap of (futures-sleeve net Sharpe − ETF-sleeve net Sharpe) with the 95% CI entirely below a SESOI *(A2 sets; the KB card's own arithmetic puts the sleeve MDE near 0.6, so the SESOI must be chosen with that precision in mind)*, **or** the futures-sleeve net Sharpe CI crossing zero while the ETF sleeve's does not, **or** the sign of the COVID-2020 and calendar-2022 window returns disagreeing between wrappers. Any one kills "the wrapper preserves the edge."
- **Trial accounting.** First TSMOM performance trial on the Databento panel: extend the carry ledger from `N_trials = 14`. Coordinate with `mean-reversion-research` (shared-ledger requirement on the KB card).

#### X02 — Signal-price vs tradable-PnL construction truth
`Family 1 · C1 · Lane: MEASUREMENT · Data: Databento`
- **Mechanism.** An implementation fact. Three candidate "signal price" series: (a) chained held-contract return index (cumulative product of held-contract returns; roll yield included; no jumps); (b) raw front-month settlement (roll jumps → spurious signs); (c) Panama back-adjusted (leaks unless built causally). Claim: only (a) makes signal and PnL reflect what was tradable.
- **Cheapest test.** Per root: fraction of months where the composite sign differs between (a) and (b)/(c); PnL attributable to roll-jump months; and a reconciliation identity — PnL from (a) must equal a contract-by-contract dollar ledger (`multiplier × Δsettle`, roll legs charged) to numerical tolerance, the futures analogue of the repo's daily↔monthly 1.3e-15 identity.
- **Overfitting / implementation risk.** None / high (this is where futures backtests manufacture profits).
- **Falsification of "construction is immaterial".** Sign-disagreement rate < 2% and PnL difference < 5 bps yr⁻¹ → immaterial; otherwise (a) is mandatory for X01, X06, X43.
- **Tests required.** Truncation invariance of the causal chain; roll-date monotonicity; the reconciliation identity; multiplier/tick unit tests (reuse carry repo's); the price-unit divisor test.

#### X03 — Roll-rule sensitivity for trend (OI-max vs fixed calendar)
`Family 1 · C1 · Lane: MEASUREMENT · Data: Databento`
- **Mechanism.** The carry study found its XS arm sensitive to the roll rule (fixed-calendar 0.125 vs −0.003). A slow trend signal should be nearly indifferent. Robustness, not selection: A1 stays primary.
- **Cheapest test.** X01 pipeline under both rules; Δ net Sharpe and PnL correlation (expect > 0.98).
- **Falsification of immateriality.** |ΔSharpe| > 0.1 or corr < 0.95 → the roll rule is a hidden degree of freedom and must be preregistered as such in every futures hypothesis.

#### X04 — Financial-futures transfer (equity index, rates, FX) — DEFERRED
`Family 1 · C1 · Lane: none (data not acquired)`
- **Mechanism.** X01 for the Equity, Bond and FX sleeves.
- **Data.** Not acquired. Candidate map: SPY↔ES, EWJ↔NKD, TLT↔ZB/UB, SHY↔ZT, FXY↔6J; UUP↔DX is **ICE, not GLBX**; **LQD/HYG and VNQ/RWX have no liquid futures** → a real program is a hybrid (futures for index/rates/FX/commodities, ETFs for credit and REITs). This hybrid structure should be decided before acquisition.
- **Why deferred.** Requires Aaron's acquisition decision (Program §Decisions). Rates futures are one duration factor (ZT/ZF/ZN/ZB), so breadth gain there is illusory; real breadth gains are in FX (6A, 6C, 6B, 6S, 6N) and non-GLBX rates (Bund/Gilt/JGB).
- **Falsification.** As X01, per sleeve.

#### X05 — Discrete-contract feasibility at account NAV
`Family 12 · C1 · Lane: MEASUREMENT · Data: contract specs (carry `CONTRACT_SPECS` for 18 roots), exchange initial-margin tables (dated snapshot), micro-contract specs`
- **Mechanism.** Capital efficiency and implementability, not alpha. For a predeclared NAV set (e.g., $100k / $250k / $500k / $1M — Aaron to confirm the bracket that matters), compute per-market contract counts at the 10% vol target (standard and micro contracts: MES/MNQ/M2K/MYM, MGC, MCL, M6E/M6B, micro 10Y), rounding tracking error vs the continuous target, margin-to-equity, and post-rounding turnover.
- **Falsification of feasibility.** At the deployment NAV, median rounding error in risk terms > 25% of a market's target risk in more than one-third of markets, or margin-to-equity above a predeclared cap → the universe or NAV must change before any FULL futures test is worth running.
- **Why it is Tier 1.** "Deploy in my own account" makes this a prerequisite; it also prices X32.

### Cluster C2 — Breadth (independent markets)

#### X06 — Commodity breadth: 18 futures roots vs 4 commodity ETFs
`Family 2 · C2 · Lane: MEASUREMENT premise → FULL · Data: Databento`
- **Mechanism.** Trend is a per-market phenomenon; each independently trending market adds a nearly independent bet — the project's own breadth lesson (single instrument falsified; 17 assets confirmed). Commodities are the most heterogeneous sleeve: energy, metals, grains, livestock respond to distinct supply/demand shocks.
- **Independence.** Expected trend-PnL corr of an 18-root commodity trend book with the baseline: 0.3–0.5 (it overlaps the 4-ETF sleeve, 26% of baseline PnL).
- **Horizon.** Monthly.
- **Cheapest premise test.** On the chained panel, per-root trend-PnL streams (locked signal, locked sizing) → correlation matrix → effective number of bets (PCA participation ratio; Meucci ENB) vs the 4-ETF sleeve's; within-sector average pairwise trend-PnL correlation. Descriptive; no portfolio Sharpe required at the premise stage (aggregate-level exposure only).
- **Overfitting risk.** Low degrees of freedom. Root selection is the carry study's ex-ante liquidity list (already fixed) — do not re-select. Sample starts 2010-06 (no GFC).
- **Implementation risk.** As X01/X02; livestock and grain roll sparsity.
- **Est. PnL corr with baseline.** 0.3–0.5 for the added markets; ≈1.0 for the overlapping four.
- **Capacity.** High.
- **Falsification.** ENB(18 roots) ≤ ENB(4 ETFs) + 1, **or** the 18-root sleeve's trend PnL corr with the 4-ETF sleeve ≥ 0.9 → no incremental breadth. FULL stage (only if premise passes): baseline + expanded commodity sleeve at a **fixed ex-ante sleeve risk share** (the sleeve must not grow its budget merely because it has more names — that is X26's question) vs baseline: paired Δ-Sharpe and Δ-Calmar bootstrap.
- **Trial accounting.** Extends the Databento ledger.

#### X07 — Effective breadth of the current 17-asset book (diagnostic)
`Family 2 · C2 · Lane: MEASUREMENT · Data: published per-asset net PnL (output/dd_per_asset_net.csv) — no new performance trial`
- **Mechanism.** The "≈12 clusters at 0.60" figure is on *returns*. Trend-PnL correlation is what determines portfolio breadth. Compute the 17×17 trend-PnL correlation matrix, ENB, sleeve-level PnL correlations, and the RealEstate–Equity and FX overlaps.
- **Why.** Calibrates X06, X08, X26, and Section E's priors.
- **Anti-snooping rule.** No ETF is removed from the baseline on this basis. A finding such as "RealEstate trend PnL corr with Equity ≥ 0.8" feeds only the design of the *new* futures universe (where REITs do not exist anyway).

#### X08 — Dropped-ETF trend-PnL independence
`Family 2 · C2 · Lane: MEASUREMENT premise · Data: raw 30-ETF panel (in hand; 13 screened-out names)`
- **Mechanism.** Two assets with return corr 0.85 can have trend-PnL corr well below that because their sign flips differ in timing. Screening dropped on return correlation, so independent trend PnL may have been discarded (SLV, GDX, IWM, XLV, XLF, EFA, IEF, FXE, QQQ, XLK, CPER, WEAT, CORN).
- **Cheapest test.** Per dropped ETF, trend-PnL stream (locked signal) vs its kept anchor's: correlation; ENB of 30 vs 17.
- **Overfitting risk.** Medium: 13 candidate additions on a burned panel. Inclusion may only follow a **pre-stated** trend-PnL correlation threshold (e.g., < 0.6 with every kept asset), never Sharpe; and the ETF result is a lead — confirmation needs the futures panel or forward accrual.
- **Est. PnL corr with baseline.** 0.6–0.8 for additions.
- **Capacity.** High (liquid ETFs) but with expense drag; CPER has documented bad prints; WEAT/CORN start 2010–11.
- **Falsification.** All 13 have trend-PnL corr ≥ 0.6 with a kept anchor → no hidden breadth.

#### X09 — Spread-trend (relative-value trend) on four predeclared economic spreads
`Family 2 / own idea · C2 · Lane: MEASUREMENT premise (ETF) → FULL · Data: ETF panel; futures later`
- **Mechanism.** The same underreaction applied to *relative* prices whose drivers differ from outright levels: curve slope (TLT/SHY — policy-expectation trends), credit spread (HYG/LQD — default-cycle trends), EM vs US equity (EEM/SPY — growth/USD-cycle trends), energy equity vs crude (XLE/USO — refining/capex cycle). A trend in a ratio bets on persistence of a relative flow, partly orthogonal to outright trends.
- **Independence.** Expected corr with baseline 0.1–0.4 — but the outright book already holds signed positions in both legs (long TLT / short SHY *is* a curve trade), so overlap must be measured, not assumed.
- **Horizon.** Monthly, 1–12 m.
- **Cheapest test.** Four log-ratio series, monthly; the locked {1,3,6,12} sign composite; vol-scale each spread; equal-weight the four → PnL stream. Report corr with baseline, standalone Sharpe CI, and marginal Δ-Sharpe when added at a fixed 20% risk share (paired bootstrap). Family = 4 spreads, fixed here; BH-FDR across 4 if per-spread claims are made. **No pair may be added or swapped after this line.**
- **Overfitting risk.** Medium (pair choice is the degree of freedom; fixed above, economically motivated).
- **Implementation risk.** Low on ETFs; on futures the credit and EM legs have no clean instruments.
- **Capacity.** High.
- **Falsification.** Corr with baseline ≥ 0.7 (redundant), **or** marginal Δ-Sharpe paired CI includes 0 with point < +0.05, **or** the spread book's standalone Sharpe CI lies entirely below 0.
- **Exposure.** 7th+ hypothesis on the burned ETF panel — declare; lead only.

#### X10 — Global financial-futures breadth — DEFERRED
`Family 2 · C2 · Lane: none`
- With X04. Genuine breadth is more likely in FX pairs and non-US rates than in additional equity indices (global equity beta) or the US curve (one duration factor). Requires acquisition; venue mix (CME, ICE, Eurex, OSE) multiplies data cost.

### Cluster C3 — Same mechanism, different speed

#### X11 — Speed-leg decomposition and leg-risk-balanced ensemble
`Family 3 · C3 · Lane: MEASUREMENT (structure) → FULL (ensemble) · Data: ETF panel first; futures replication`
- **Mechanism.** Fast (1–3 m) and slow (6–12 m) legs capture different phases of one underreaction–overreaction cycle: fast legs enter and exit early (more whipsaw, faster crisis response); slow legs ride mature trends and bleed at reversals (the 2022-23 loss profile). If their failure periods differ, an ensemble of individually modest speeds can have better Calmar/Sortino than any single speed even at equal Sharpe.
- **The one real design difference.** The baseline averages *signs* then vol-scales once. A *leg-risk-balanced* ensemble vol-targets each leg's portfolio separately before combining, so faster legs (lower realized vol per unit signal because they flip more) receive a different risk share. That is the testable object — not "the ensemble", which at equal sign-weights is the baseline itself.
- **Independence.** Fast leg vs baseline 0.5–0.7; slow legs vs baseline 0.8–0.9; fast vs slow 0.3–0.6 (priors).
- **Cheapest test.** The four legs {1}, {3}, {6}, {12} already exist as Method-A signals. Build each as a full sub-strategy with identical sizing/portfolio machinery → pairwise PnL correlation, drawdown-episode overlap (Jaccard of underwater months), crisis-window attribution per leg, turnover per leg.
- **Overfitting risk.** Low if the leg set stays {1,3,6,12} and weights are never searched (equal risk only). The trap is turning the correlation table into weight optimisation — forbidden.
- **Implementation risk.** Low.
- **Capacity.** Fast leg lower (turnover).
- **Falsification.** (i) All pairwise leg PnL correlations ≥ 0.8 (no speed diversification exists); **or** (ii) the leg-risk-balanced ensemble's Calmar *and* Sortino are not better than the baseline under paired bootstrap (Δ CIs include 0); **or** (iii) fast–slow drawdown-overlap Jaccard ≥ 0.8.
- **`POST-EXPOSURE DESIGN`.** The robustness grid already revealed {6,12} = 0.87 > {1,3,6,12} = 0.75 on this sample, so any "slower is better" conclusion on the ETF panel is post-exposure and not confirmable there. The *correlation and overlap structure* was never exposed and is the clean premise. Ensemble confirmation must come from the futures panel or forward accrual.

#### X12 — Fast-leg marginal contribution net of realistic costs (replication-only)
`Family 3 · C3 · Lane: FULL on the futures panel only`
- **Mechanism.** The 1-month leg flips most often and drives the signal-driven 81% of turnover; on the ETF sample it reduced Sharpe by ≈0.10 ({3,6,12} = 0.85 vs 0.75 — **exposed**). Hypothesis: at measured futures costs, its marginal net contribution ≤ 0.
- **Cheapest test.** Futures panel only: {1,3,6,12} vs {3,6,12}, paired Δ-Sharpe at the measured c* costs. One comparison, no scan.
- **Overfitting risk.** High if run on the ETF panel (answer already known) — hence replication-only. Even on futures the 2010–26 price paths overlap the ETFs' (implementation-level independence only, as the KB card states).
- **Falsification.** Paired Δ-Sharpe(with − without) CI entirely > 0 → the fast leg helps; "fast leg hurts net" is falsified.
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
- **Cheapest test.** Pooled panel (17 × ≈218 ≈ 3,700 asset-months). (i) Forward 1-month sign-aligned return per unit ex-ante vol for |score| = 0.5 vs 1.0. (ii) By decile of |z12| (12 m return ÷ 12 m realised vol): mean sign-aligned forward risk-adjusted return per decile with block-bootstrap CIs; Spearman of decile rank vs outcome. Predeclare: monotone-increasing = premise for continuous sizing; hump-shaped = premise for bounded/capped sizing; flat = reject (sign is all that matters; keep baseline).
- **Overfitting risk.** Medium: one z horizon (12 m) plus the existing score; deciles fixed; no curve fitting.
- **Implementation risk.** Low.
- **Est. PnL corr with baseline** for any resulting sizing variant: ≥ 0.9.
- **Capacity.** High.
- **Falsification.** Spearman(decile, outcome) 95% CI includes 0 **and** top-minus-bottom decile difference below a bar *(A2 sets, in monthly risk-adjusted units)* → no magnitude information → X15 is not built.
- **Exposure.** 7th+ reuse; aggregate-level (no strategy Sharpe).

#### X15 — Bounded continuous sizing (conditional on X14)
`Family 4 · C4 · Lane: FULL`
- One mapping, chosen by X14's shape (linear clipped at ±2σ if monotone; hump-capped if concave); everything else identical. Paired Δ-Sharpe / Δ-Calmar vs baseline; turnover change; crisis retention.
- **Falsification.** Paired Δ CI includes 0, or turnover +20% without Δ-Sharpe > +0.1.

#### X16 — Estimator-family correlation (same-source test)
`Family 9 · C4 · Lane: MEASUREMENT · Data: ETF panel (daily for EWMA)`
- **Mechanism.** Return-sign composite (baseline), EWMA-crossover triplet (8/24, 16/48, 32/96 days, z-scored and capped, per Baz et al. 2015), robust 12-month regression-slope t-stat, and Donchian channel position (6 m and 12 m) are four representations of one behavioural mechanism. If pairwise PnL correlations are ≥ 0.85 they are one alpha; if not, estimator-specific whipsaw partly cancels in an ensemble.
- **Cheapest test.** Build each as a full sub-strategy with identical sizing/portfolio machinery; 4×4 PnL correlation, drawdown overlap, turnover, signal-agreement rates. No selection.
- **Overfitting risk.** Low (four estimators fixed at standard parameterisations; nothing tuned).
- **Implementation risk.** Low–medium.
- **Est. PnL corr with baseline.** 0.8–0.95 each.
- **Capacity.** High.
- **Falsification of the diversification claim.** All pairwise PnL correlations ≥ 0.85 → SAME FAMILY; X17 is not built.
- **Exposure.** Four sub-strategy Sharpes become exposed (target-metric ×4); record them. X17's confirmation therefore belongs on futures/forward.

#### X17 — Estimator ensemble vs baseline (conditional on X16)
`Family 10 · C4 · Lane: FULL`
- Equal-weight ensemble (primary); median and majority-vote as two predeclared secondaries (BH-FDR across 3). A later, more complex weighting must beat the equal-weight ensemble, not the baseline.
- **Falsification.** EW ensemble paired Δ-Sharpe CI includes 0 **and** Δ-Calmar ≤ 0.

#### X18 — Path-efficiency (efficiency-ratio) conditioning
`Family 15 · C4 · Lane: MEASUREMENT premise · Data: ETF panel (causal regime panel exists: src/regime.py)`
- **Mechanism.** A trend that unfolded efficiently (high Kaufman ER) reflects persistent one-directional participation; a noisy path with the same net return reflects contested pricing → lower follow-through. Distinct from the vol-breakout study, which used *post-move* ER as an outcome, not trailing ER as a conditioner.
- **Cheapest test.** Per asset-month, trailing 63-day ER tercile (causal) × sign signal → forward-month sign-aligned hit rate and risk-adjusted return; pooled + 5 sleeves = 6 cells; BH-FDR q = 0.10; magnitude bar (≥ 3 pp hit-rate difference top vs bottom tercile).
- **Overfitting risk.** Low–medium (one window, terciles).
- **Falsification.** No cell clears BH-FDR + magnitude + half-sample stability.

### Cluster C5 — Trend dynamics (acceleration, age, exhaustion)

#### X19 — Acceleration and trend-age premise
`Family 5 · C5 · Lane: MEASUREMENT premise · Data: ETF panel`
- **Mechanism.** Information diffusion is a process: a trend that is young (recently flipped) and accelerating (Δz > 0) is mid-diffusion; a mature, decelerating trend is closer to full absorption or crowding. Δz and age carry information beyond level only if diffusion speed varies across episodes.
- **Cheapest test.** Pooled panel regression of forward sign-aligned risk-adjusted return on level (z12), Δz (z12_t − z12_{t−3}), and age (months since the composite's sign last flipped, capped at 24); Newey–West HAC; plus a 3×3 sort (level tercile × Δ tercile). Family: two coefficients + one corner contrast.
- **Overfitting risk.** Medium–high (nonlinear temptation). Functional forms fixed here: linear coefficients and terciles only; no splines, no thresholds searched.
- **Implementation risk.** Low.
- **Est. PnL corr with baseline** of any resulting overlay: ≥ 0.9.
- **Falsification.** Δz and age HAC 95% CIs include 0 **and** the corner contrast is below the bar → reject.

#### X20 — Exhaustion after extreme acceleration
`Family 5 · C5 · Lane: MEASUREMENT (same family as X19)`
- Top-decile Δz (and top-decile |z|) → forward return relative to the rest; one tail cell, decile fixed, no cutoff search.
- **Falsification.** Tail-cell difference CI includes 0.

### Cluster C6 — Trend-state conditioning (breadth, dispersion, concentration)

#### X21 — Trend breadth predicts continuation
`Family 6 · C6 · Lane: MEASUREMENT premise · Data: ETF panel + published net returns`
- **Mechanism.** Broad cross-market trend agreement usually reflects a macro driver (2008 deleveraging, 2020 shock, 2022 inflation/rates) that propagates slowly through many markets → more persistent; narrow trends are idiosyncratic and fragile.
- **Cheapest test.** Causal breadth state at month-end t: B1 = fraction of assets with |score| = 1; B2 = fraction of sleeves whose members agree in sign; tercile of a trailing 36-month causal percentile. Forward strategy net return at 1 and 3 months by tercile; HAC; **and an episode jackknife** (breadth regimes are slow: count distinct high-breadth episodes, require ≥ 4, and require that no single episode carries the effect — the yield-curve lesson applied in advance).
- **Overfitting risk.** Medium (2 definitions × 2 horizons = 4 cells; the episode-count trap is the real risk).
- **Est. PnL corr with baseline** of any overlay: ≥ 0.9.
- **Falsification.** 0 of 4 cells clear BH-FDR + magnitude (≥ 3% yr⁻¹ Δ) + episode jackknife.
- **Exposure.** Uses the strategy's own published net returns as the outcome → target-metric exposure; lead only.

#### X22 — Signal dispersion / mixed-horizon disagreement → whipsaw regime
`Family 6 · C6 · Lane: MEASUREMENT (same family as X21)`
- B3 = average |score| across assets (low = many mixed signals). Low-B3 months precede lower hit rates. Adds 2 cells to the X21 family.

#### X23 — Trend concentration (effective number of active trends)
`Family 6 · C6 · Lane: MEASUREMENT (same family as X21)`
- B4 = 1/HHI of |base-weight| shares. Concentrated risk precedes worse tail outcomes. Adds 2 cells. **X21–X23 form one preregistered family of 8 cells under a single BH-FDR.**

### Cluster C7 — Directional asymmetry

#### X24 — Long/short decomposition by sleeve
`Family 7 · C7 · Lane: MEASUREMENT (decomposition) · Data: published per-asset net PnL and positions (no new performance trial)`
- **Mechanism.** Long trend in risk assets (equities, credit, REITs) is aligned with the risk premium; its bleed is the mean-reverting rally after dips. Short trend in the same assets fights the premium and faces sharp V-shaped recoveries (2009, 2020) → lower Sharpe, worse skew, shorter duration — yet **all crisis alpha is short-side**. In rates, FX and commodities the premium is weaker or ambiguous, so long ≈ short is the prior.
- **Cheapest test.** Split each asset-month's net PnL by position sign. Per sleeve: long vs short Sharpe, hit rate, skew, mean holding duration, turnover share, crisis-window contribution; block bootstrap of the long − short Sharpe difference; half-sample stability. Family: 5 sleeves × 1 contrast, BH-FDR.
- **Overfitting risk.** Low (no parameters). The risk lives in the follow-on rule (X25).
- **Implementation risk.** None.
- **Est. PnL corr with baseline.** n/a (decomposition).
- **Falsification of asymmetry.** No sleeve shows a stable (same sign in both halves) long − short difference that passes BH-FDR with |ΔSharpe| ≥ 0.3.
- **Exposure.** Sub-stream Sharpes become exposed; lead only.

#### X25 — Asymmetric short-side scaling in risk-premium sleeves (conditional on X24)
`Family 7 · C7 · Lane: FULL · Data: futures panel / forward accrual for confirmation`
- **Mechanism.** If X24 is stable, identical signal magnitude should not imply identical long and short risk in premium-bearing sleeves.
- **Design.** One predeclared rule: in the sleeves X24 confirmed, short positions sized at 0.5× (one value, never searched); everything else unchanged. **Gate on crisis-alpha retention** (≥ 70% of the GFC, COVID and calendar-2022 window returns) because the mechanism predicts the rule sacrifices exactly the strategy's most valuable property. Paired Δ-Sharpe / Δ-Calmar / Δ-skew.
- **Est. PnL corr with baseline.** ≥ 0.9.
- **Falsification.** Crisis retention < 70% **or** paired Δ-Sharpe CI includes 0.
- **`POST-EXPOSURE DESIGN`** with respect to X24's ETF sub-streams; confirmation on futures/forward only.

### Cluster C8 — Risk budgeting and allocation

#### X26 — Equal-sleeve risk vs equal-asset risk
`Family 8 · C8 · Lane: FULL (paired control) · Data: ETF panel`
- **Mechanism.** The current budget is by asset count (Equity 5/17, Bond 4/17, Commodity 4/17, FX 2/17, RealEstate 2/17) — an artifact of screening, not a risk view. Equal sleeve risk removes the artifact. The prediction is genuinely ambiguous (it upweights FX and RealEstate); the value is a robustness finding: the baseline's result does not depend on the accidental count weighting.
- **Cheapest test.** Reuse the `rp_comparison.py` pattern with a sleeve-level aggregation; **paired** Δ-Sharpe / Δ-MDD bootstrap (fixing the unpaired comparison used in the risk-parity control). Two variants only: equal-sleeve; uniform sleeve cap at 35%.
- **Overfitting risk.** Low (two symmetric structural variants).
- **Est. PnL corr with baseline.** ≥ 0.95.
- **Falsification of "budgeting matters".** Paired Δ CI includes 0 → keep the baseline. The null is the *desired* outcome for robustness.
- **`POST-EXPOSURE DESIGN` note.** Sleeve statistics are published, so the designer knows FX and RealEstate are weak. A "cap the weak sleeves" rule would be snooping; the only admissible variants are symmetric rules stated before any run.

#### X27 — Cluster-based hierarchical risk budget
`Family 8 · C8 · Lane: FULL (same family as X26)`
- Sleeves defined by causal correlation clustering (trailing 3 years, cut at 0.6) instead of named asset classes; risk equalised across clusters, then within. Adds estimation noise (cluster instability); must beat *equal-sleeve*, not just equal-asset.
- **Falsification.** Paired Δ vs equal-sleeve CI includes 0.

#### X28 — Static risk-premium blend (deployment portfolio)
`Family 18 / own idea · C8 · Lane: MEASUREMENT · Data: published TSMOM net and equal-weight buy-and-hold streams`
- **Mechanism.** For a personal account, TSMOM's low correlation with a long risk-premium book (the repo's equal-weight buy-and-hold has Sharpe 0.33) may raise portfolio Sharpe/Calmar more than any overlay: trend as a convex overlay on a long book. Not alpha; allocation.
- **Cheapest test.** corr(TSMOM net, buy-and-hold); Sharpe/Calmar of three fixed blends (100/0, 75/25, 50/50 by risk); paired vs TSMOM alone.
- **Overfitting risk.** Low.
- **Est. corr with baseline.** 0.1–0.3 (the long book).
- **Falsification.** No fixed blend improves Calmar with Δ-Sharpe not worse than −0.05.

#### X29 — Dynamic allocation across validated sub-strategies — DEFERRED
`Family 18 · C8 · Lane: none until ≥ 2 validated sub-strategies exist (today: 0)`
- Predeclared candidate set when reached: equal, inverse-vol, capped inverse-vol. No performance chasing.

### Cluster C9 — Execution and turnover

#### X30 — Execution-day robustness
`Family 11 · C9 · Lane: MEASUREMENT · Data: ETF daily panel (src/daily.py infra exists)`
- **Mechanism.** None — robustness. Variants: execute at close T (baseline), T+1, T+2, T+3; signal dated day 15 with execution T+1. Five variants, no selection; the baseline stays T.
- **Cheapest test.** Daily held-weight paths; net Sharpe, MDD, crisis returns per variant; dispersion across variants.
- **Falsification of "robust".** Any variant's net Sharpe outside the baseline's bootstrap CI, **or** a crisis-window sign flip, **or** Sharpe dispersion across variants > 0.15.
- **Exposure.** Five target-metric exposures of the same strategy; record them.

#### X31 — Tranched (staggered) execution
`Family 11 · C9 · Lane: FULL-lite (single variant) · Data: daily panel`
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
- **`POST-EXPOSURE DESIGN`** (turnover composition is published); confirmation on futures.

#### X34 — Event-triggered intra-month re-evaluation after a large adverse move
`Family 14 / own idea · C9 · Lane: MEASUREMENT premise → FULL · Data: daily panel`
- **Mechanism.** 61% of drawdown loss is crash-type and declines last 14 months; a monthly calendar ignores a −2σ intra-month move against a held position. If such moves predict further adverse drift within the month (trend break), an event-triggered re-check (recompute the composite that day; exit or flip only if the sign changed) cuts crash losses; if they predict rebound (noise), it adds whipsaw.
- **Cheapest premise test.** For each asset-month, on the first day the position's month-to-date return ≤ −2σ (ex-ante monthly σ): remaining-month sign-aligned return vs unconditional; and whether the composite sign has already changed that day. Six cells (pooled + 5 sleeves), BH-FDR.
- **Overfitting risk.** Medium (threshold and horizon fixed here).
- **Implementation risk.** Medium (intra-month execution, costs).
- **Falsification.** Post-event remaining-month sign-aligned return not worse than base by at least the bar → no premise; do not build.

### Cluster C10 — Volatility estimation

#### X35 — Volatility-estimator type
`Family 13 · C10 · Lane: MEASUREMENT (4 fixed variants) · Data: ETF panel`
- **Mechanism.** Sizing stability, not alpha. A simple 60-day window drops old shocks abruptly (edge effects → step changes in weights → turnover); EWMA (λ = 0.97) decays smoothly; a fast/slow blend (20 d / 120 d) damps; a MAD-based robust estimator resists single-day outliers. Expect Sharpe ≈ unchanged (the window sweep gave 0.71–0.76), vol-driven turnover reduced, realised-vs-target tracking similar or better.
- **Test.** Four estimators, one parameterisation each: vol-attributable turnover, realised/target vol ratio error, worst month, paired Δ net Sharpe. Selection **only** by the pre-stated stability criterion, never by Sharpe.
- **Falsification of "estimator matters".** No estimator cuts vol-driven turnover ≥ 15% without worse tracking → keep the baseline.

#### X36 — Vol floor and per-asset cap interaction
`Family 13 · C10 · Lane: MEASUREMENT · Data: ETF panel`
- **Mechanism.** SHY (short Treasuries, σ ≈ 1–2%) is very likely cap-bound at ±2 every month, making it a levered short-rate bet whose contribution was never isolated. Measure cap-bind frequency per asset, PnL and drawdown contribution of cap-bound positions, and one predeclared vol floor (4% annualised) as an alternative to the cap.
- **Falsification.** Floor changes nothing material (ΔSharpe < 0.02, Δgross < 5%) → keep the cap.

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

#### X40 — Cross-asset correlation state — `POST-EXPOSURE DESIGN`, fresh data only
`Family 15 · C12 · Lane: DEFERRED to the futures panel / forward accrual`
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
- **Cheapest test.** Each month per root, 2×2 sort (trend sign × carry sign) → forward monthly sign-aligned return per unit risk; contrast aligned − opposed; HAC and block bootstrap; per-sector robustness (4 sectors) → 5 cells, BH-FDR. Primary carry definition: front − next (the 12-month-deferred variant is not a second try).
- **Overfitting risk.** Medium (burned panel; reserved family; one carry definition).
- **Implementation risk.** Medium (carry alignment to signal dates; roll congestion).
- **Est. PnL corr** of a carry-conditioned commodity trend with the commodity trend: 0.7–0.9.
- **Capacity.** High.
- **Falsification.** Aligned − opposed difference CI includes 0 or is below the bar *(A2 sets)* pooled **and** in ≥ 3 of 4 sectors.
- **Trial accounting.** Declare Databento reuse; extend the ledger; coordinate with the mean-reversion program's shared ledger.

#### X44 — Carry as tie-breaker for ambiguous trend (conditional on X43)
`Family 16 · C13 · Lane: FULL (same family as X43)`
- Where |score| ≤ 0.5, the carry sign decides direction; one rule; paired vs the commodity-sleeve baseline.

### Cluster C14 — Edge diagnostics (what the baseline actually is)

#### X45 — Hidden beta / static-premium decomposition of the core
`Diagnostics · C14 · Lane: MEASUREMENT · Data: published streams`
- **Mechanism.** XSMOM turned out to be partly a static premium (Sharpe halves under demeaning). TSMOM's net exposure is time-varying but its *average* may be structurally long (bonds and equities trended up more often than down over 2008–26). Measure: average net exposure by sleeve; monthly regression of TSMOM net returns on SPY, TLT, a commodity basket and UUP (HAC); and a **static-book control** — the Sharpe of the average-position book held constant, and the Sharpe of the residual (position − average position).
- **Falsification of "pure dynamic edge".** Residual Sharpe after removing the static average-position book drops by more than 50%.
- **Value.** Calibrates every independence estimate in Section E and X28.

#### X46 — Convexity profile and crisis-alpha attribution
`Diagnostics · C14 · Lane: MEASUREMENT (same family as X45)`
- TSMOM monthly return vs SPY (and vs the equal-weight long book): quadratic fit (the "smile"); crisis-alpha attribution long vs short; tail-event correlation. Informs Cluster C7 and the mechanism claim behind "genuine crisis alpha."

---

## Section D — Mechanism clustering

| Cluster | Mechanism | Members | Same-alpha risk within cluster | Designer's note |
|---|---|---|---|---|
| C1 Implementation transfer | Same signal, different wrapper | X01 X02 X03 X04 X05 | Total (by construction) | Not alpha research; deployment truth. Everything else on futures depends on it. |
| C2 Breadth | Same mechanism, more independent markets | X06 X07 X08 X09 X10 | Low across markets; X09 partly overlaps the outright book | The only cluster with a demonstrated prior in this repo (single-instrument null → 17-asset confirmation). |
| C3 Speed | Same mechanism, different formation horizon | X11 X12 X13 | Medium (slow legs ≈ baseline) | The baseline already averages the legs; the object is leg *risk balance* and failure-period diversity. |
| C4 Signal representation | Same mechanism, different estimator or magnitude map | X14 X15 X16 X17 X18 | High (0.8–0.95 expected) | Null hypothesis is "one family"; ensemble value only if correlations fall below 0.85. |
| C5 Trend dynamics | Diffusion speed varies across episodes | X19 X20 | High as overlays | Nonlinear temptation; forms fixed in advance. |
| C6 Trend-state conditioning | Macro-driven vs idiosyncratic trends | X21 X22 X23 | High as overlays; one 8-cell family | Episode-count trap; jackknife ranked above significance. |
| C7 Directional asymmetry | Risk premium interacts with trend direction | X24 X25 | High | Crisis alpha is short-side; retention gate mandatory. |
| C8 Risk budgeting / allocation | Where the risk sits, not what the signal is | X26 X27 X28 X29 | Total (≥ 0.95) except X28 | The null (indistinguishable) is the robustness win. |
| C9 Execution & turnover | Path of trades, not the signal | X30 X31 X32 X33 X34 | Total (≥ 0.95) | X32 is futures-native and distinct from the ETF band. |
| C10 Volatility estimation | Sizing stability | X35 X36 | Total | Stability metrics decide, never Sharpe. |
| C11 Strategy-state control | Persistence of the strategy's own state | X37 X38 | High | Structurally distinct from external crash prediction; few episodes. |
| C12 External-state conditioning | Market-state variables | X39 X40 X41 X42 | High | Mostly deferred or closed; the family that has failed four times. |
| C13 Carry interaction | Two expected-return sources on one instrument | X43 X44 | Medium (0.7–0.9) | Reserved by the carry prereg; burned panel. |
| C14 Edge diagnostics | Measuring the baseline | X45 X46 | n/a | Cheapest, most informative, zero selection pressure. |

**Cosmetic-variant control.** Within C3, C4, C9 and C10 any two members with PnL correlation ≥ 0.95 are one hypothesis for ledger purposes; the program's trial ledger counts the *family*, and the preregistration for each family names every variant up front.

---

## Section E — Estimated independence from the baseline

The ranking rule in one line: **portfolio contribution is what is being bought; standalone Sharpe is not.** A Sharpe-0.6 stream at correlation 0.2 raises a Sharpe-0.75 book far more than a Sharpe-1.2 stream at correlation 0.9.

| Tier | Meaning | Members | Evaluation rule at FULL |
|---|---|---|---|
| **N — candidate new PnL source** (est. corr < 0.7) | Could be a separate line in the book | X06 (0.3–0.5), X09 (0.1–0.4), X11 fast leg (0.5–0.7), X28 long book (0.1–0.3), X43/X44 (0.7–0.9, borderline), X08 additions (0.6–0.8, borderline) | Standalone evidence package **and** marginal paired Δ at a fixed risk share |
| **M — modification of the same stream** (est. corr ≥ 0.85) | Changes how the baseline's stream is produced | X14–X20, X21–X27, X30–X38, X39–X42, X25 | **Paired-difference only.** Standalone Sharpe is not admissible evidence. Report Δ-Sharpe, Δ-Calmar, Δ-skew, crisis retention, turnover Δ. |
| **I — implementation truth** (corr ≈ 1 by construction) | Same stream, different wrapper or bookkeeping | X01–X05 | Reconciliation identities, wrapper Δ with a reachable kill branch, feasibility bars |
| **D — diagnostic** | Measures the baseline | X07, X45, X46 | Findings only; no promotion vocabulary applies |

**Correlation must be measured, never assumed.** Every FULL candidate reports: monthly return correlation with the baseline and with every previously accepted derivative; rolling 36-month correlation; drawdown-episode overlap (Jaccard); crisis-window co-sign; sleeve attribution overlap; tail-event correlation (worst-decile months). A candidate at corr ≥ 0.9 with any accepted stream is `not_promoted (redundant_same_pnl_source)` unless its paired Δ is positive with a CI excluding zero **and** it is cheaper to run.

**The exposure caveat on the priors above.** These correlations are priors from the mechanism, not measurements; X07, X45 and X46 (Wave 1) will replace most of them with numbers before any FULL test is designed.

---

## Section F — Overfitting risk

Scored 0–10 on: degrees of freedom · family size · exposure contamination (design informed by published outcomes) · implementation ambiguity · data-quality risk · execution sensitivity.

| Risk band | IDs | Dominant risk | Mitigation written into the entry |
|---|---|---|---|
| **Low (≤ 3)** | X02 X03 X05 X07 X16 X24 X26 X28 X30 X35 X36 X45 X46 | none material | fixed variants; no selection |
| **Low–medium (3–4)** | X01 X06 X11 X14 X18 X31 | kill-branch reachability (X01); exposed leg Sharpes (X11) | A2 reachability check; confirmation off-panel |
| **Medium (5–6)** | X08 X09 X12 X15 X17 X19 X20 X21 X22 X23 X25 X27 X32 X33 X34 X39 X43 X44 | pair/threshold choice; episode counts; post-exposure design | families fixed; jackknife; futures/forward confirmation |
| **High (≥ 7)** | X13 X37 X38 X40 X41 X42 | per-sleeve fitting; few episodes; post-exposure inversion | deferred, or premise-with-jackknife only |

**Program-level multiplicity.** Every strategy-variant Sharpe computed on a sample is a trial in the program's ledger (`TRIAL_LEDGER.md`, Wave 0) regardless of lane. Premise cells are BH-FDR'd within their family; FULL results carry a Deflated Sharpe with `N_trials` = the sample's cumulative count. The ETF panel's historical count must be reconstructed and frozen in Wave 0 (six hypotheses, plus the 45-combination robustness grid whose counting convention — robustness vs selection — must be decided once, in writing, and never revisited; the c1-drag-audit's `SAMPLE_REUSE.md` is the precedent for that reasoning).

---

## Section G — Required data

| Data | Exists? | Location / status | Needed by |
|---|---|---|---|
| ETF adjusted close, 30 names, 1993→2026-06-12 | Yes | `data/close_prices_raw.csv` (yfinance cache) | X07–X09, X11, X14–X39, X45, X46 |
| ETF daily infra (causal vol %ile, ER, dispersion) | Yes | `src/regime.py`, `src/daily.py`, `output/regime_variables_pit.csv` | X18, X21, X30, X34, X39 |
| Published streams (monthly net, per-asset net, positions, weights) | Yes | `output/monthly_returns.csv`, `output/dd_per_asset_net.csv`, `output/monthly_portfolio_weights.csv` | X07, X24, X28, X37, X45, X46 |
| Databento GLBX.MDP3 commodity panel, 18 roots, 2010-06→2026-06 (ohlcv-1d, statistics, definition) | Yes | `C:\Users\Aaron\quant-data\commodity-carry` (9.5 GB); roll/returns/cost code in `commodity-carry-research/src/` | X01–X03, X06, X12, X32, X43, X44 |
| Contract specs (tick, multiplier) for 18 roots | Yes | `commodity-carry-research/src/config.py::CONTRACT_SPECS` (apply the price-unit divisor) | X01, X05, X32 |
| Financial futures (ES/NQ/RTY/YM, ZT/ZF/ZN/ZB/UB, 6E/6J/6B/6A/6C/6S/6N, NKD) | **No** | Databento GLBX.MDP3; cost/coverage unverified | X04, X10, hybrid deployment |
| Long-history futures (pre-2008, decades) | **No** | vendor decision (e.g., Norgate / CSI / Pinnacle-class) | the only genuinely fresh decades for every ETF-designed hypothesis |
| Exchange initial-margin tables; micro-contract specs | **No** (public) | CME margin pages (dated snapshot) | X05, X32 |
| CFTC COT (weekly) | **No** (public) | cftc.gov | X41 (deferred) |
| OHLC for range-based vol | Partly (yfinance has OHLC; cache is close-only) | re-fetch | optional for X35 (not required) |
| Forward accrual > 2026-06-12 | Exists, untouched | do **not** refresh into the working cache (Wave 0 lockbox rule) | all confirmations |

---

## Section H — Cheapest falsification test per hypothesis

Compact form; the full test is in each Section C entry. "Sessions" = rough builder-session estimate (Opus, high effort), infrastructure included where it does not yet exist.

| ID | Cheapest test | Lane | New code? | Sessions | Kills the idea if… |
|---|---|---|---|---|---|
| X01 | pair return corr + sign agreement; then paired wrapper Δ | MEAS → FULL | futures signal adapter | 3–4 | wrapper Δ CI below SESOI, or futures CI crosses 0, or crisis sign flips |
| X02 | sign-disagreement rate + dollar-ledger reconciliation | MEAS | yes (chain + ledger) | 2 | n/a (truth test; sets the mandatory construction) |
| X03 | A1 vs calendar roll Δ | MEAS | small | 0.5 | immaterial → roll rule not a DoF |
| X04 | as X01 per sleeve | — | after acquisition | — | — |
| X05 | contract counts / rounding error / margin-to-equity at NAV set | MEAS | small | 1 | rounding error > 25% risk in > 1/3 markets |
| X06 | ENB and corr matrix of 18-root trend PnL | MEAS → FULL | reuse X02 infra | 1 (+2 FULL) | ENB gain ≤ 1 or corr with 4-ETF sleeve ≥ 0.9 |
| X07 | 17×17 trend-PnL corr, ENB | MEAS | none | 0.5 | n/a (diagnostic) |
| X08 | dropped-ETF trend-PnL corr vs anchors | MEAS | none | 0.5 | all ≥ 0.6 |
| X09 | 4-spread trend book: corr, standalone CI, marginal Δ | MEAS → FULL | small | 1 (+1) | corr ≥ 0.7 or marginal Δ ≤ 0 |
| X11 | 4-leg sub-strategies: corr, DD overlap, crisis split | MEAS → FULL | small | 1 (+1) | all leg corr ≥ 0.8; ensemble Δ-Calmar/Sortino ≤ 0 |
| X12 | {1,3,6,12} vs {3,6,12} on futures, paired | FULL (futures) | none | 0.5 | Δ with-1m > 0 |
| X14 | \|score\| and \|z12\| deciles → forward risk-adj return | MEAS | small | 0.5 | flat (Spearman CI ∋ 0) |
| X15 | one mapping vs baseline, paired | FULL | small | 1 | Δ ≤ 0 or turnover +20% |
| X16 | 4 estimators → PnL corr matrix | MEAS | medium (EWMA, slope, Donchian) | 1.5 | all corr ≥ 0.85 |
| X17 | EW/median/majority ensemble vs baseline, paired | FULL | small | 1 | Δ-Sharpe ∋ 0 and Δ-Calmar ≤ 0 |
| X18 | ER tercile × sign → hit rate (6 cells) | MEAS | none | 0.5 | 0/6 |
| X19 | HAC regression on z, Δz, age + 3×3 sort | MEAS | small | 1 | coefficients ∋ 0 |
| X20 | top-decile Δz tail cell | MEAS | none | 0.25 | ∋ 0 |
| X21–23 | breadth/dispersion/concentration terciles → fwd net return, jackknife (8 cells) | MEAS | small | 1 | 0/8 after jackknife |
| X24 | long/short split per sleeve (5 cells) | MEAS | none | 0.5 | no stable \|Δ\| ≥ 0.3 |
| X25 | one asymmetric rule, crisis-retention gate | FULL | small | 1 | retention < 70% or Δ ∋ 0 |
| X26/27 | sleeve-risk variants, paired | FULL | small | 1 | Δ ∋ 0 (keep baseline) |
| X28 | 3 fixed blends with the long book | MEAS | none | 0.25 | no Calmar gain |
| X30 | 5 execution-day variants | MEAS | small (daily weights) | 1 | dispersion > 0.15 or CI breach |
| X31 | 4-tranche variant, paired | FULL-lite | small | 0.5 | Δ < −0.05 |
| X32 | 2 hysteresis thresholds on futures, paired | FULL | medium | 1 | both reduce net Sharpe |
| X33 | 2 smoothing variants, paired at 2/5/10 bps | FULL | small | 1 | turnover −15% not reached or Δ ≤ 0 |
| X34 | −2σ event → remaining-month return (6 cells) | MEAS | small | 1 | no adverse-drift premise |
| X35 | 4 vol estimators: stability metrics | MEAS | small | 1 | no ≥ 15% vol-turnover cut |
| X36 | cap-bind stats; one floor | MEAS | none | 0.25 | immaterial |
| X37/38 | DD-state / loss-cluster terciles, jackknife | MEAS | none | 0.5 | nothing survives jackknife |
| X39 | high-vol tercile × sign (6 cells) | MEAS | none | 0.25 | 0/6 |
| X43 | 2×2 trend × carry sort (5 cells) | MEAS → FULL | small (carry series exist) | 1 (+1) | aligned − opposed ∋ 0 |
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
| X06 | 8 | 3 | 2 | 0.3–0.5 | Only cluster with an in-repo demonstrated prior; data in hand |
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
| X26 | 5 | 2 | 1 | ≥ 0.95 | Robustness null is the win |
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
| **1 — run first** | 1 | X02, X05, X07, X45, X46 | Measurement truth: zero selection pressure, cheapest, and every later design depends on their numbers |
| | 2 | X01 (+X03) | The registered #1 hypothesis; data in hand; a reachable kill branch this time |
| | 3 | X06 | Breadth on real futures; the one prior this repo has actually demonstrated |
| | 4 | X11 | Speed structure; low DoF; clean premise (correlations were never exposed) |
| | 5 | X16 | Decides whether estimator diversity exists before any ensemble is built |
| | 6 | X24 | Long/short structure; cheap; feeds deployment and Cluster C7 |
| **2 — premise tests, then conditional FULLs** | 7 | X14, X18 | Cheap gates on the continuous-signal and path-quality families |
| | 8 | X30, X35, X26 | Robustness of execution day, vol estimator, sleeve budget; the null is fine |
| | 9 | X09 | Spread trend — the cheapest candidate new PnL source |
| | 10 | X43 | Carry × trend — reserved, data in hand, needs ledger coordination |
| | 11 | X28 | Deployment blend |
| | 12 | X19/X20, X21–X23 | Dynamics and breadth-state premises with jackknife |
| | 13 | X31, X32, X33, X34 | Execution refinements; X32 only after Wave 1 |
| **3 — conditional or low value** | 14 | X15, X17, X25, X44, X27, X12 | Only if their premise passes |
| | 15 | X08, X36, X37/X38, X39 | Low value or high episode risk; run only if budget remains |
| **4 — deferred** | — | X04, X10, X13, X29, X40, X41, X42 | Data acquisition, validated-subs prerequisite, post-exposure, or closed |

### J.2 Five highest-priority ideas — and why

1. **X01 Commodity-sleeve futures transfer (with X02/X03 truth tests).** It is the single question the KB already ranks first, the data is on disk, the roll/cost code exists, and it converts the strategy from "ETF proxy replication" into something deployable. Its prior failure mode — an unreachable kill branch — is known and fixable at A2.
2. **X06 Commodity breadth (18 roots vs 4 ETFs).** Breadth is the one extension mechanism this project has *demonstrated* (single-instrument null → 17-asset confirmation). The premise test is descriptive and needs no portfolio Sharpe.
3. **X11 Speed-leg decomposition and leg-risk-balanced ensemble.** Same mechanism, different failure periods, four legs the baseline already computes, and the clean object (correlation and overlap structure) has never been exposed. Low degrees of freedom.
4. **X16 Estimator-family correlation.** Cheap, fixed, and decisive for two whole families (9 and 10): if four textbook estimators are ≥ 0.85 correlated, the ensemble idea dies before a dollar is fit.
5. **X24 Long/short decomposition.** No parameters, published data, and it addresses the mechanism behind both the crisis alpha and the crash-type drawdowns — the two properties that define the edge.

### J.3 Five high-upside, high-risk ideas — and why they are not first

1. **X43 Carry × trend agreement.** A second expected-return source on the same instrument; but the panel is burned by carry, standalone carry was null, and the interaction is easy to over-read across four sectors.
2. **X09 Spread trend.** The cheapest candidate for a genuinely new PnL source (est. corr 0.1–0.4); the risk is pair selection — hence four economically fixed pairs and a ban on additions.
3. **X19 Acceleration and trend age.** A real diffusion mechanism with nonlinear temptations; forms fixed to linear + terciles.
4. **X21 Trend breadth predicts continuation.** Plausible macro mechanism; slow regimes mean a handful of episodes — the exact trap that killed the yield-curve overlay, so the jackknife is ranked above significance from the start.
5. **X37 Own-drawdown-state conditioning.** Structurally distinct from the falsified crash-defense, but twelve episodes and one dominant 2022-23 episode make it the easiest thing in this map to overfit.

### J.4 Five cheap premise tests — and why

1. **X14 Trend-strength deciles** — one afternoon on the existing panel; gates Family 4 entirely.
2. **X18 Efficiency-ratio conditioning** — the causal ER already exists in `src/regime.py`; six cells.
3. **X45/X46 Hidden beta and convexity** — published streams only; converts Section E's priors into measurements.
4. **X30 Execution-day robustness** — the daily infrastructure exists; five variants; the answer matters for every futures deployment.
5. **X35 Vol-estimator type** — four fixed estimators judged by stability, never by Sharpe.

### J.5 Five deliberately deferred ideas — and why

1. **X04/X10 Financial-futures transfer and breadth** — the data does not exist; acquisition (and the hybrid futures/ETF structure for credit and REITs) is Aaron's decision, and the long-history question should be decided at the same time.
2. **X13 Asset-class speed specialization** — the highest overfitting risk in the map; X11 will show whether there is anything to specialise, for free.
3. **X29 Dynamic strategy allocation** — there are zero validated sub-strategies today; allocation among them is a question for after Waves 2–5.
4. **X40 Correlation-state conditioning** — a hypothesis generated by inverting an exposed negative result; admissible only on data the design never saw.
5. **X41/X42 COT positioning and VIX/MOVE** — data not fetched and reserved elsewhere (X41); same class as two falsified overlays with the same episode-count trap (X42).

---

## Section K — Decisions requested from Aaron, and what happens next

Nothing below is authorised by this document; each is a decision only Aaron can take.

| # | Decision | Why it is needed now | Default if undecided |
|---|---|---|---|
| D1 | Acquire financial futures (GLBX.MDP3: ES/NQ, ZT/ZF/ZN/ZB/UB, 6E/6J/6B/6A/6C/6S/6N, NKD) — and decide the hybrid structure (credit and REITs stay ETF) | Unblocks X04/X10 and a real deployment universe | Program runs commodity-only futures (Waves 1–2) and ETF-panel premises |
| D2 | Acquire long-history futures (pre-2008 decades) from a long-history vendor | The only genuinely fresh decades available for every ETF-designed hypothesis; larger OOS gain than any single idea in this map | Confirmation relies on the 2010+ futures panel and forward accrual |
| D3 | Confirm the deployment NAV bracket for X05/X32 | Feasibility bars depend on it | Use {$100k, $250k, $500k, $1M} |
| D4 | Create `qros-state.yaml`, `ops/EXPOSURE_LEDGER.md`, `ops/REVIEWER_EXPOSURE_LOG.md`, `SAMPLE_REUSE.md`, `TRIAL_LEDGER.md` for this program (Wave 0) and freeze the ETF-panel trial-count convention | Required by the L6 runtime; nothing MEASUREMENT-lane should run before the ledgers exist | Program does not start |
| D5 | Adopt the forward-accrual lockbox rule (no working-panel refresh past 2026-06-12 outside a sealed confirmation) | Protects the only ETF OOS that will ever exist | Data drifts into every exploratory run and is lost as OOS |
| D6 | Authorise KB hypothesis cards for Tier-1 candidates (Opus, in a KB session) | KB rule 16 and the registry's provenance conventions | Cards written at each candidate's preregistration instead |
| D7 | Seat routing: confirm Opus designs/builds each wave, fresh Sol A2 challenges each FULL preregistration, and Fable is invoked only on the QROS triggers that apply (futures roll/cost model in Wave 1; portfolio accounting in Wave 4; any promotion decision) | Independence lives in the session; this map's author must not certify its own program | As stated |

The staged plan, seat routing, ledger rules and per-wave gates are in `TSMOM_EXTENSION_RESEARCH_PROGRAM.md`.

---

*Treat "no incremental edge exists" as a valid final result for every entry above. A falsified hypothesis in this map is a permanent research asset; do not overwrite it, rename it, or split it into cosmetic variants.*
