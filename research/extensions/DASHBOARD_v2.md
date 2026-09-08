# TSMOM Extension Dashboard — v2 (converged draft)

**Status:** PROVISIONAL REVIEWABLE DRAFT (2026-09-08). Companion to `TSMOM_EXTENSION_RESEARCH_MAP_v2.md` and `TSMOM_EXTENSION_RESEARCH_PROGRAM_v2.md`. The v1 `DASHBOARD.md` is preserved unchanged as review history.

**Every row is `PROPOSED`; no extension test has been run.** Performance columns are filled only by FULL-lane results under a sealed preregistration, each tagged with its evidence context (T0–T4, Program v2 §0A). Design lineage and validation evidence are separate columns and are never merged. Exposure classes describe the *first test's actual outputs* (Program v2 §0B); they are explanatory, not canonical enum values.

**Global gates today:** `STRATEGY_BUILD_READINESS = NOT_READY` for every row · `WAVE_0_EXECUTED = NO` · `WAVE_1_EXECUTED = NO` · `NEW_DATA_PURCHASED = NO` · `X09_ROUTE_PENDING_AARON`.

Baseline row for reference (frozen; evidence type `full_sample_fixed_parameter`; KB status `supported`): net Sharpe 0.75 [0.29, 1.23] · MDD −15.6% · turnover 17.6× · cost breakpoint ≈ 20 bps · 218 months 2008-05 → 2026-06 (last-row construction `UNKNOWN_PENDING_WAVE0_VERIFICATION`).

| id | family | mechanism (short) | stage / status | design_lineage | first_test_exposure_class | validation_evidence_context | prereg_sealed | standalone_net_sharpe | oos_sharpe | sortino | max_dd | turnover | cost_breakpoint | corr_to_baseline | marginal_portfolio_sharpe | redundancy_review | key_failure_mode | final_decision |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| X01 | 1 | futures wrapper transfer, commodity sleeve (paired, 3 states) | PROPOSED — FULL after seal | KB card + c1 map D5 | TARGET_PERFORMANCE (after seal only) | — (T1 when run) | NO | — | — | — | — | — | — | prior ≥0.9 | — | — | unreachable kill branch (A2 check); roll/price-unit defects | — |
| X02 | 1 | X02a mechanical truth / X02b construction arm inside X01 | PROPOSED — MEASUREMENT (a) | none | PURE_MECHANICAL + DESIGN_INFORMING (a) | — | N/A (a) | — | — | — | — | — | — | — | — | — | back-adjustment PnL; invalid accounting | — |
| X03 | 1 | roll-schedule diagnostics pre-seal / performance arm inside X01 | PROPOSED — MEASUREMENT (structural) | none | DESIGN_INFORMING (pre-seal) | — | N/A | — | — | — | — | — | — | — | — | — | hidden DoF | — |
| X04 | 1 | financial-futures transfer | DEFERRED | none | — | — | N/A | — | — | — | — | — | — | prior ≥0.9 | — | — | ownership not established; inventory pending | — |
| X05 | 12 | discrete-contract feasibility | PROPOSED — MEASUREMENT | none | DESIGN_INFORMING | — | N/A | — | — | — | — | — | — | — | — | — | rounding error at NAV | — |
| X06 | 2 | expanded futures universe vs matched futures subset | PROPOSED — MEASUREMENT → FULL | none | TARGET_PERFORMANCE (per-root streams) | — | NO | — | — | — | — | — | — | prior 0.3–0.5 | — | — | no breadth gain; 2010+ sample | — |
| X07 | 2 | effective breadth diagnostic | PROPOSED — MEASUREMENT | T0 published inputs | TARGET_PERFORMANCE (new statistics) | T0 | N/A | — | — | — | — | — | — | — | — | — | asset-removal temptation (banned) | — |
| X08 | 2 | dropped-ETF trend-PnL independence | PROPOSED — MEASUREMENT | none | TARGET_PERFORMANCE (13 streams) | — | N/A | — | — | — | — | — | — | prior 0.6–0.8 | — | — | burned panel; selection by correlation | — |
| X09 | 2/9 | spread trend, 4 fixed spreads | PROPOSED — X09_ROUTE_PENDING_AARON | none | A: DESIGN_INFORMING (structural overlap) / B: TARGET_PERFORMANCE | — | NO | — | — | — | — | — | — | prior 0.1–0.4 | — | — | spreads reconstruct held outrights; undefined mechanics | — |
| X10 | 2 | global financial breadth | DEFERRED | none | — | — | N/A | — | — | — | — | — | — | prior 0.3–0.6 | — | — | ownership not established | — |
| X11 | 3 | X11a speed-leg structure / X11b ensemble | PROPOSED — MEASUREMENT (a) / FULL (b) | ROBUSTNESS_GRID_INFORMED | TARGET_PERFORMANCE (four streams) | — | NO (b) | — | — | — | — | — | — | prior 0.5–0.7 (fast) | — | — | leg weights optimised (banned) | — |
| X12 | 3 | fast-leg net contribution (futures) | PROPOSED — FULL (futures only) | ROBUSTNESS_GRID_INFORMED | TARGET_PERFORMANCE | — (T1, dependent) | NO | — | — | — | — | — | — | — | — | — | replication of exposed fact | — |
| X13 | 17 | asset-class speed specialization | DEFERRED | ROBUSTNESS_GRID_INFORMED | — | — | N/A | — | — | — | — | — | — | — | — | — | per-sleeve fitting | — |
| X14 | 4 | trend-strength shape contrasts | PROPOSED — MEASUREMENT | none | DESIGN_INFORMING (conditional forward returns) | — | N/A | — | — | — | — | — | — | prior ≥0.9 | — | — | both contrasts fail → stop (not falsification) | — |
| X15 | 4 | bounded continuous sizing | PROPOSED (conditional on X14) — FULL | X14-informed | TARGET_PERFORMANCE | — | NO | — | — | — | — | — | — | prior ≥0.9 | — | — | turnover cost | — |
| X16 | 9 | estimator-family dependence | PROPOSED — MEASUREMENT | none | TARGET_PERFORMANCE (four Sharpes) | — | N/A | — | — | — | — | — | — | prior 0.8–0.95 | — | — | high dependence restricts independence claims | — |
| X17 | 10 | estimator ensemble | PROPOSED (conditional on X16) — FULL | X16-informed | TARGET_PERFORMANCE | — | NO | — | — | — | — | — | — | prior ≥0.9 | — | — | no Δ over baseline | — |
| X18 | 15 | efficiency-ratio conditioning | PROPOSED — MEASUREMENT | none | DESIGN_INFORMING | — | N/A | — | — | — | — | — | — | prior ≥0.9 | — | — | 0/6 cells | — |
| X19 | 5 | sign-aligned acceleration / age / 3×3 corner contrast (family of 4 with X20; corner contrast counted — choice B) | PROPOSED — MEASUREMENT | none | DESIGN_INFORMING | — | N/A | — | — | — | — | — | — | prior ≥0.9 | — | — | nonlinear overfit | — |
| X20 | 5 | exhaustion tail cell | PROPOSED — MEASUREMENT | none | DESIGN_INFORMING | — | N/A | — | — | — | — | — | — | prior ≥0.9 | — | — | single tail cell | — |
| X21 | 6 | trend breadth state | PROPOSED — MEASUREMENT | T0 published inputs | TARGET_PERFORMANCE (published net as outcome) | T0 | N/A | — | — | — | — | — | — | prior ≥0.9 | — | — | episode count | — |
| X22 | 6 | signal dispersion state | PROPOSED — MEASUREMENT | T0 published inputs | TARGET_PERFORMANCE | T0 | N/A | — | — | — | — | — | — | prior ≥0.9 | — | — | episode count | — |
| X23 | 6 | trend concentration state | PROPOSED — MEASUREMENT | T0 published inputs | TARGET_PERFORMANCE | T0 | N/A | — | — | — | — | — | — | prior ≥0.9 | — | — | episode count | — |
| X24 | 7 | long/short decomposition (Wave 1) | PROPOSED — MEASUREMENT | T0 published inputs | TARGET_PERFORMANCE (substream statistics) | T0 | N/A | — | — | — | — | — | — | — | — | — | unstable across halves | — |
| X25 | 7 | asymmetric short scaling | PROPOSED (conditional on X24) — FULL | POST_EXPOSURE_DESIGN_ON_ETF_PANEL | TARGET_PERFORMANCE | — | NO | — | — | — | — | — | — | prior ≥0.9 | — | — | crisis-preservation claim fails | — |
| X26 | 8 | equal-sleeve risk (equivalence) | PROPOSED — FULL | POST_EXPOSURE_DESIGN_ON_ETF_PANEL | TARGET_PERFORMANCE | — | NO | — | — | — | — | — | — | prior ≥0.95 | — | — | margin not met (not "significant difference") | — |
| X27 | 8 | cluster-hierarchical budget | PROPOSED — FULL | as X26 | TARGET_PERFORMANCE | — | NO | — | — | — | — | — | — | prior ≥0.95 | — | — | cluster instability | — |
| X28 | 18 | static-premium blend | PROPOSED — MEASUREMENT | T0 published inputs | TARGET_PERFORMANCE (allocation) | T0 | N/A | — | — | — | — | — | — | prior 0.1–0.3 | — | — | not a strategy | — |
| X29 | 18 | dynamic allocation | DEFERRED | none | — | — | N/A | — | — | — | — | — | — | — | — | — | no lines past §9 gate | — |
| X30 | 11 | execution-day robustness | PROPOSED — MEASUREMENT | none | TARGET_PERFORMANCE (5 variants) | — | N/A | — | — | — | — | — | — | prior ≥0.95 | — | — | dispersion | — |
| X31 | 11 | tranched execution | PROPOSED — FULL | none | TARGET_PERFORMANCE | — | NO | — | — | — | — | — | — | prior ≥0.95 | — | — | turnover | — |
| X32 | 12 | contract-integer hysteresis | PROPOSED — FULL (after Wave 1) | none | TARGET_PERFORMANCE | — | NO | — | — | — | — | — | — | prior ≥0.95 | — | — | tracking error | — |
| X33 | 12 | signal-path smoothing | PROPOSED — FULL | POST_EXPOSURE_DESIGN_ON_ETF_PANEL + ROBUSTNESS_GRID_INFORMED | TARGET_PERFORMANCE | — | NO | — | — | — | — | — | — | prior ≥0.95 | — | — | lag in 2020-type moves | — |
| X34 | 14 | event-triggered re-evaluation | PROPOSED — MEASUREMENT → FULL | none | DESIGN_INFORMING (conditional forward returns) | — | N/A | — | — | — | — | — | — | prior ≥0.9 | — | — | whipsaw; population definition | — |
| X35 | 13 | X35a stability diagnostic / X35b non-inferiority replacement | PROPOSED — MEASUREMENT (a) / FULL (b) | none | TARGET_PERFORMANCE where produced (a) | — | NO (b) | — | — | — | — | — | — | prior ≥0.97 | — | — | a-stage exposure reused as fresh (banned) | — |
| X36 | 13 | X36a cap-binding diagnostic / X36b floor policy | PROPOSED — MEASUREMENT (a) / FULL (b) | none | DESIGN_INFORMING + TARGET_PERFORMANCE (a: PnL/drawdown attribution of cap-bound positions) / TARGET_PERFORMANCE (b) | — | NO (b) | — | — | — | — | — | — | prior ≥0.97 | — | — | immaterial | — |
| X37 | 14 | own-drawdown state | PROPOSED — MEASUREMENT | T0 published inputs | TARGET_PERFORMANCE (published net conditioned) | T0 | N/A | — | — | — | — | — | — | prior ≥0.9 | — | — | 2022-23 single episode | — |
| X38 | 14 | loss-clustering state | PROPOSED — MEASUREMENT | T0 published inputs | TARGET_PERFORMANCE | T0 | N/A | — | — | — | — | — | — | prior ≥0.9 | — | — | few episodes | — |
| X39 | 15 | high-vol conditioning | PROPOSED — MEASUREMENT | none | DESIGN_INFORMING | — | N/A | — | — | — | — | — | — | prior ≥0.9 | — | — | low value | — |
| X40 | 15 | correlation state | DEFERRED (T3/T4 only) | POST_EXPOSURE_DESIGN (inversion of crash-defense) | — | — | N/A | — | — | — | — | — | — | prior ≥0.9 | — | — | post-hoc inversion | — |
| X41 | 15 | COT positioning | DEFERRED | none | — | — | N/A | — | — | — | — | — | — | prior ≥0.9 | — | — | data; reserved | — |
| X42 | 15 | VIX / MOVE | DEFERRED | none | — | — | N/A | — | — | — | — | — | — | prior ≥0.9 | — | — | closed class | — |
| X43 | 16 | carry × trend agreement + bridge cell | PROPOSED — MEASUREMENT → FULL | CARRY_STUDY_INFORMED | TARGET_PERFORMANCE (conditional returns) | — | NO | — | — | — | — | — | — | prior 0.7–0.9 | — | — | burned panel; sector over-read | — |
| X44 | 16 | carry direction rule, non-zero ambiguous state only | PROPOSED (conditional on X43 bridge) — FULL | X43-informed | TARGET_PERFORMANCE | — | NO | — | — | — | — | — | — | prior ≥0.9 | — | — | neutral-state carry deferred/untested, not falsified | — |
| X45 | diag | hidden beta / static premium | PROPOSED — MEASUREMENT | T0 published inputs | TARGET_PERFORMANCE (static-book Sharpes) | T0 | N/A | — | — | — | — | — | — | — | — | — | retrospective description, not ex-ante strategy | — |
| X46 | diag | convexity profile | PROPOSED — MEASUREMENT | T0 published inputs | TARGET_PERFORMANCE (crisis attribution) | T0 | N/A | — | — | — | — | — | — | — | — | — | — | — |

Column notes: `design_lineage` records where the design came from and never changes. `validation_evidence_context` records the context (T0–T4) of each supporting test as it runs; a T0 origin does not prevent a later T4 entry. `redundancy_review` records the outcome of `HIGH_REDUNDANCY_REVIEW` when triggered; it is a review outcome, not an automatic verdict. `corr_to_baseline` shows the map's prior until measured; replace with the measured value and drop the `prior` prefix.
