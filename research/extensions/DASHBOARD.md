# TSMOM Extension Dashboard

One row per independent candidate. **Every row is `PROPOSED` today; no extension test has been run.** Exploratory or premise numbers are never entered in the performance columns; only FULL-lane results under a sealed preregistration may fill `standalone_net_sharpe`, `oos_sharpe`, `marginal_portfolio_sharpe`. Update at every wave close. Definitions in `TSMOM_EXTENSION_RESEARCH_MAP.md`; rules in `TSMOM_EXTENSION_RESEARCH_PROGRAM.md` §0.

Baseline row for reference (frozen; tier `full_sample_fixed_parameter`; KB status `supported`): net Sharpe 0.75 [0.29, 1.23] · Sortino n/r · MDD −15.6% · turnover 17.6× · cost breakpoint ≈ 20 bps · 218 months 2008-05 → 2026-06.

| id | family | mechanism (short) | status | outcome_exposed | prereg_sealed | standalone_net_sharpe | oos_sharpe | sortino | max_dd | turnover | cost_breakpoint | corr_to_baseline | marginal_portfolio_sharpe | key_failure_mode | final_decision |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| X01 | 1 | futures wrapper transfer, commodity sleeve | PROPOSED | NONE (design read published ETF sleeve) | NO | — | — | — | — | — | — | est ≥0.9 | — | unreachable kill branch (fixed at A2); roll/price-unit defects | — |
| X02 | 1 | signal-price vs tradable-PnL truth | PROPOSED | NONE | N/A | — | — | — | — | — | — | — | — | back-adjustment profits | — |
| X03 | 1 | roll-rule sensitivity | PROPOSED | NONE | N/A | — | — | — | — | — | — | — | — | hidden DoF | — |
| X04 | 1 | financial-futures transfer | DEFERRED | NONE | N/A | — | — | — | — | — | — | est ≥0.9 | — | data not acquired | — |
| X05 | 12 | discrete-contract feasibility | PROPOSED | NONE | N/A | — | — | — | — | — | — | — | — | rounding error at NAV | — |
| X06 | 2 | commodity breadth (18 roots) | PROPOSED | NONE | NO | — | — | — | — | — | — | est 0.3–0.5 | — | no ENB gain; 2010+ sample | — |
| X07 | 2 | effective breadth diagnostic | PROPOSED | TARGET_METRIC (published inputs) | N/A | — | — | — | — | — | — | — | — | snooping temptation (asset removal banned) | — |
| X08 | 2 | dropped-ETF trend-PnL independence | PROPOSED | NONE | N/A | — | — | — | — | — | — | est 0.6–0.8 | — | burned panel; lead only | — |
| X09 | 2/9 | spread trend, 4 fixed spreads | PROPOSED | NONE | NO | — | — | — | — | — | — | est 0.1–0.4 | — | overlap with outright legs; pair selection | — |
| X10 | 2 | global financial breadth | DEFERRED | NONE | N/A | — | — | — | — | — | — | est 0.3–0.6 | — | data not acquired | — |
| X11 | 3 | speed-leg structure + risk-balanced ensemble | PROPOSED | AGGREGATE (grid exposed leg Sharpes) | NO | — | — | — | — | — | — | est 0.5–0.7 (fast) | — | leg weights optimised (banned) | — |
| X12 | 3 | fast-leg net contribution (futures) | PROPOSED | TARGET_METRIC on ETF (known) | NO | — | — | — | — | — | — | — | — | replication of exposed fact | — |
| X13 | 17 | asset-class speed specialization | DEFERRED | AGGREGATE | N/A | — | — | — | — | — | — | — | — | per-sleeve fitting | — |
| X14 | 4 | trend-strength deciles | PROPOSED | NONE | N/A | — | — | — | — | — | — | est ≥0.9 | — | flat response | — |
| X15 | 4 | bounded continuous sizing | PROPOSED (conditional) | NONE | NO | — | — | — | — | — | — | est ≥0.9 | — | turnover cost | — |
| X16 | 9 | estimator-family correlation | PROPOSED | NONE | N/A | — | — | — | — | — | — | est 0.8–0.95 | — | all ≥0.85 (one family) | — |
| X17 | 10 | estimator ensemble | PROPOSED (conditional) | NONE | NO | — | — | — | — | — | — | est ≥0.9 | — | no Δ over baseline | — |
| X18 | 15 | efficiency-ratio conditioning | PROPOSED | NONE | N/A | — | — | — | — | — | — | est ≥0.9 | — | 0/6 cells | — |
| X19 | 5 | acceleration / age | PROPOSED | NONE | N/A | — | — | — | — | — | — | est ≥0.9 | — | nonlinear overfit | — |
| X20 | 5 | exhaustion tail cell | PROPOSED | NONE | N/A | — | — | — | — | — | — | est ≥0.9 | — | single tail cell | — |
| X21 | 6 | trend breadth state | PROPOSED | TARGET_METRIC (published net as outcome) | N/A | — | — | — | — | — | — | est ≥0.9 | — | episode count | — |
| X22 | 6 | signal dispersion state | PROPOSED | as X21 | N/A | — | — | — | — | — | — | est ≥0.9 | — | episode count | — |
| X23 | 6 | trend concentration state | PROPOSED | as X21 | N/A | — | — | — | — | — | — | est ≥0.9 | — | episode count | — |
| X24 | 7 | long/short decomposition | PROPOSED | TARGET_METRIC (published inputs) | N/A | — | — | — | — | — | — | — | — | unstable across halves | — |
| X25 | 7 | asymmetric short scaling | PROPOSED (conditional) | AGGREGATE (post-exposure) | NO | — | — | — | — | — | — | est ≥0.9 | — | crisis-alpha loss | — |
| X26 | 8 | equal-sleeve risk (paired) | PROPOSED | AGGREGATE (sleeve stats published) | NO | — | — | — | — | — | — | est ≥0.95 | — | none (null expected) | — |
| X27 | 8 | cluster-hierarchical budget | PROPOSED | as X26 | NO | — | — | — | — | — | — | est ≥0.95 | — | cluster instability | — |
| X28 | 18 | static-premium blend | PROPOSED | TARGET_METRIC (published inputs) | N/A | — | — | — | — | — | — | est 0.1–0.3 | — | not a strategy | — |
| X29 | 18 | dynamic allocation | DEFERRED | NONE | N/A | — | — | — | — | — | — | — | — | no validated subs | — |
| X30 | 11 | execution-day robustness | PROPOSED | NONE | N/A | — | — | — | — | — | — | est ≥0.95 | — | dispersion > 0.15 | — |
| X31 | 11 | tranched execution | PROPOSED | NONE | NO | — | — | — | — | — | — | est ≥0.95 | — | turnover | — |
| X32 | 12 | contract-integer hysteresis | PROPOSED | NONE | NO | — | — | — | — | — | — | est ≥0.95 | — | tracking error | — |
| X33 | 12 | signal-path smoothing | PROPOSED | AGGREGATE (turnover split published) | NO | — | — | — | — | — | — | est ≥0.95 | — | lag in 2020-type moves | — |
| X34 | 14 | event-triggered re-evaluation | PROPOSED | NONE | N/A | — | — | — | — | — | — | est ≥0.9 | — | whipsaw | — |
| X35 | 13 | vol-estimator type | PROPOSED | NONE | N/A | — | — | — | — | — | — | est ≥0.97 | — | none (stability criterion) | — |
| X36 | 13 | vol floor / cap | PROPOSED | NONE | N/A | — | — | — | — | — | — | est ≥0.97 | — | immaterial | — |
| X37 | 14 | own-drawdown state | PROPOSED | TARGET_METRIC (published net) | N/A | — | — | — | — | — | — | est ≥0.9 | — | 2022-23 single episode | — |
| X38 | 14 | loss-clustering state | PROPOSED | as X37 | N/A | — | — | — | — | — | — | est ≥0.9 | — | few episodes | — |
| X39 | 15 | high-vol conditioning | PROPOSED | NONE | N/A | — | — | — | — | — | — | est ≥0.9 | — | low value | — |
| X40 | 15 | correlation state | DEFERRED | TARGET_METRIC (post-exposure) | N/A | — | — | — | — | — | — | est ≥0.9 | — | post-hoc inversion | — |
| X41 | 15 | COT positioning | DEFERRED | NONE | N/A | — | — | — | — | — | — | est ≥0.9 | — | data; reserved | — |
| X42 | 15 | VIX / MOVE | DEFERRED | NONE | N/A | — | — | — | — | — | — | est ≥0.9 | — | closed class | — |
| X43 | 16 | carry × trend agreement | PROPOSED | NONE | NO | — | — | — | — | — | — | est 0.7–0.9 | — | burned panel; sector over-read | — |
| X44 | 16 | carry tie-break | PROPOSED (conditional) | NONE | NO | — | — | — | — | — | — | est ≥0.9 | — | — | — |
| X45 | diag | hidden beta / static premium | PROPOSED | TARGET_METRIC (published inputs) | N/A | — | — | — | — | — | — | — | — | — | — |
| X46 | diag | convexity profile | PROPOSED | as X45 | N/A | — | — | — | — | — | — | — | — | — | — |

Column notes: `outcome_exposed` = exposure state *of the candidate's own test*, as of today (NONE = not yet run; TARGET_METRIC/AGGREGATE where the test's inputs are already-published outcomes). `prereg_sealed` = N/A for MEASUREMENT-lane items that never reach FULL. `corr_to_baseline` shows the map's prior until measured; replace with the measured value and drop the `est` prefix.
