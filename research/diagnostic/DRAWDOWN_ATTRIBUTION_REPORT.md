# Drawdown Attribution — Multi-Asset TSMOM (descriptive diagnostic)

*Generated 2026-06-24 13:59. DESCRIPTIVE only — no parameter tuning, no Sharpe optimization, no overlay. Reuses the exact vol-scaled positions from the confirmed backtest.*
*Evaluation window: **2008-05-31 → 2026-06-30** (218 months), the full-17-asset period.*

## TL;DR — chop or crash?

- **Overall drawdown split: 61.4% CRASH (held-trend reversals) vs 38.6% CHOP (whipsaw).**
- The strategy's drawdowns are predominantly **turning-point momentum crashes**, and they are **systemic** — on average 85% of sleeves are down together during a decline (not idiosyncratic).
- **Implication for a pullback-MR overlay:** 🔴 NO-GO (crash-dominant: MR would add to losers at reversals) at the portfolio level. Per-sleeve verdicts below — bonds differ from the rest.

## 0. Reconciliation gate (non-negotiable)

- Reconstructed per-asset decomposition vs the engine: **max abs monthly diff = 3.47e-18**, cumulative diff = 0.00e+00 over 218 months → **exact** (decomposition is additive by construction).
- Vs the serialized `monthly_returns.csv`: max abs diff = 4.96e-07 (= 6-dp rounding in the saved file). Confirms the Step-0.5 XSMOM cleanup did not change the strategy.

## 1. Chop-vs-crash by sleeve (CORE result) + overlay go/no-go

| sleeve | crash % | chop % | Σ decline PnL | pullback-MR verdict |
| --- | --- | --- | --- | --- |
| Equity | 62.3% | 37.7% | -33.4% | 🔴 NO-GO (crash-dominant: MR would add to losers at reversals) |
| Bond | 45.8% | 54.2% | -18.8% | 🟠 CAUTION (mixed; test gingerly behind a regime filter) |
| Commodity | 67.4% | 32.6% | -10.7% | 🔴 NO-GO (crash-dominant: MR would add to losers at reversals) |
| FX | 77.0% | 23.0% | -5.9% | 🔴 NO-GO (crash-dominant: MR would add to losers at reversals) |
| RealEstate | 66.3% | 33.7% | -21.3% | 🔴 NO-GO (crash-dominant: MR would add to losers at reversals) |
| **Overall** | 61.4% | 38.6% | -90.1% | 🔴 NO-GO (crash-dominant: MR would add to losers at reversals) |

> **crash** = loss while *holding* a position aligned with the 12-month entry trend (a trend-follower bleeding as the trend reversed). **chop** = loss from sign-flips / entries / exits during the episode (whipsaw). The two buckets are additive and sum to each sleeve's decline-phase PnL. Method: position-conditional split (task Step 4.5), weighted by realized loss across the flagged episodes.

## 2. Per-sleeve standalone summary (full sample)

| sleeve | Sharpe | max DD | hit rate | % of total PnL | % of total DD loss |
| --- | --- | --- | --- | --- | --- |
| Equity | 0.60 | -10.6% | 59.6% | 34.1% | 33.0% |
| Bond | 0.69 | -7.0% | 61.0% | 29.8% | 17.4% |
| Commodity | 0.55 | -7.1% | 59.2% | 26.0% | 17.4% |
| FX | 0.18 | -7.7% | 50.5% | 6.1% | 10.9% |
| RealEstate | 0.11 | -7.6% | 50.7% | 4.1% | 21.3% |

> A sleeve's stream here is its *contribution* to portfolio net (its assets' net_i), so the columns sum across sleeves to the portfolio. A sleeve whose **% of DD loss ≫ % of PnL** is a drawdown driver carrying little upside.

## 3. Drawdown episodes (ranked by depth)

| # | peak | trough | recovery | depth | decline mo | underwater mo | recovered |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2022-09-30 | 2023-11-30 | 2024-09-30 | -15.6% | 14 | 24 | ✓ |
| 2 | 2018-01-31 | 2019-01-31 | 2019-08-31 | -10.3% | 12 | 19 | ✓ |
| 3 | 2010-04-30 | 2010-07-31 | 2011-01-31 | -8.6% | 3 | 9 | ✓ |
| 4 | 2015-01-31 | 2015-10-31 | 2016-07-31 | -8.4% | 9 | 18 | ✓ |
| 5 | 2024-09-30 | 2025-04-30 | 2025-10-31 | -7.9% | 7 | 13 | ✓ |
| 6 | 2012-01-31 | 2012-06-30 | 2013-01-31 | -7.5% | 5 | 12 | ✓ |
| 7 | 2008-06-30 | 2008-07-31 | 2008-09-30 | -6.8% | 1 | 3 | ✓ |
| 8 | 2013-04-30 | 2013-09-30 | 2013-12-31 | -6.6% | 5 | 8 | ✓ |
| 9 | 2009-11-30 | 2010-01-31 | 2010-04-30 | -6.4% | 2 | 5 | ✓ |
| 10 | 2014-06-30 | 2014-09-30 | 2014-11-30 | -5.6% | 3 | 5 | ✓ |
| 11 | 2021-10-31 | 2022-01-31 | 2022-03-31 | -5.1% | 3 | 5 | ✓ |
| 12 | 2016-07-31 | 2017-01-31 | 2017-05-31 | -4.6% | 6 | 10 | ✓ |

*23 episodes ≥ 1% depth; 11 flagged for attribution (top 10 + any ≥ 5%).*

## 4. Per-episode chop-vs-crash + corroborating metrics

| # | depth | label | crash % | signflips/mo | decline ER | pre-trend ER | worst-5d share | daily skew |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | -15.6% | crash | 56.5% | 7.7 | 0.06 | 0.16 | 15.1% | -0.57 |
| 2 | -10.3% | crash | 57.5% | 7.3 | 0.04 | 0.25 | 21.2% | -1.12 |
| 3 | -8.6% | crash | 98.8% | 6.0 | 0.08 | 0.19 | 50.4% | -0.08 |
| 4 | -8.4% | crash | 64.3% | 6.4 | 0.05 | 0.20 | 15.0% | 0.19 |
| 5 | -7.9% | crash | 59.3% | 6.9 | 0.04 | 0.21 | 27.1% | -0.30 |
| 6 | -7.5% | chop | 17.0% | 7.4 | 0.08 | 0.06 | 26.0% | -0.40 |
| 7 | -6.8% | crash | 82.4% | 9.0 | 0.42 | 0.20 | 74.9% | -0.57 |
| 8 | -6.6% | crash | 52.0% | 6.2 | 0.10 | 0.26 | 27.9% | -0.25 |
| 9 | -6.4% | crash | 87.7% | 5.0 | 0.16 | 0.17 | 46.6% | -0.23 |
| 10 | -5.6% | crash | 82.8% | 6.3 | 0.15 | 0.24 | 42.9% | -1.19 |
| 11 | -5.1% | chop | 15.5% | 8.7 | 0.08 | 0.07 | 57.7% | -2.69 |

> Corroboration (context, not the split): low **decline ER** = choppy price path; low **pre-trend ER** = weak prior trend (less to 'crash'); high **worst-k-day share** + negative **daily skew** = a few large adverse days (crash signature). These temper or support the position-conditional label.

## 5. Co-drawdown — systemic vs idiosyncratic

- Mean fraction of sleeves simultaneously down during flagged declines: **85%** (10/11 episodes have ≥80% of sleeves down together).
- Drawdowns are therefore **broad/systemic**: diversification across sleeves does *not* spare the book in a decline. This is itself evidence against chop being the main cause (idiosyncratic whipsaw would not co-move across asset classes).

## 6. Method & honesty notes

- **Reuse, not re-derivation:** positions = `portfolio.build_portfolio(px, 'B')['position']`, unchanged from the backtest. Per-asset net = position × monthly return − |Δposition|×bps.
- **Episode labels are full-sample descriptive** (we are characterizing realized history — legitimate). The **reusable regime variables** in [`regime_variables_pit.csv`](regime_variables_pit.csv) are by contrast **strictly point-in-time / causal** (trailing windows + trailing percentile ranks only), so they can serve as live overlay signals.
- **Daily texture** (decline ER, worst-k-day, skew) uses a daily gross stream of the held monthly book (intra-month drift); the episode **depth** always uses the official monthly net curve.
- **No tuning.** All thresholds are conventional descriptive choices in `config.py`; nothing here changes the strategy.

## Figures

- [`dd_underwater.png`](dd_underwater.png) — portfolio underwater curve
- [`dd_sleeve_equity.png`](dd_sleeve_equity.png) — per-sleeve cumulative contribution
- [`dd_episode_attribution.png`](dd_episode_attribution.png) — per-episode loss attribution by sleeve
- [`dd_chop_crash_timeline.png`](dd_chop_crash_timeline.png) — drawdown timeline tagged chop vs crash
