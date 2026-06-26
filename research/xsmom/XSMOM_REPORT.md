# Cross-Sectional Momentum (XSMOM) vs Time-Series Momentum (TSMOM)

*Generated 2026-06-22 02:26. Same 17-ETF universe, same 12-1 cadence, same engine. Honest validation — results reported as-is, no tuning.*
*Common evaluation window: **2008-05-31 → 2026-06-30** (218 months). Costs 2 bps one-way × turnover; rf = 0%.*

## TL;DR — pre-registered verdict

- **XSMOM-tercile net Sharpe = 0.28**, 95% bootstrap CI **[-0.18, 0.75]** → **CROSSES 0**.
- Walk-forward: **4/5 blocks positive** → **pass**. 3/6/9/12 same sign: **True**.
- **CONFIRMED iff** CI excludes 0 **AND** walk-forward positive **AND** 3/6/9/12 same sign → **❌ NOT CONFIRMED**.
- **The punchline — `corr(XSMOM, TSMOM) = +0.42`** (rank-weight: +0.40). 50/50 combined Sharpe **0.66** vs best leg 0.75.

## 0. Pre-registered criteria (fixed before looking at results)

- **CONFIRMED iff** bootstrap Sharpe CI excludes 0 **AND** walk-forward OOS expectancy positive (majority of non-overlapping blocks positive) **AND** the 3/6/9/12-month formation neighbourhood is the same sign.
- **FALSIFIED if** the CI includes 0 **OR** walk-forward is negative — still documented.
- All three comparison outcomes pre-accepted: **low** corr → diversification payoff; **high** corr → "at ETF granularity, XS and TS are the same source" (honest negative); whoever wins Sharpe/crisis is reported as-is.
- **Confound**: edge survives within-class / demeaned ranking → real momentum; vanishes → static risk premium. Both honest.

## 1. Head-to-head (net of costs, identical months)

|  | ann return | ann vol | Sharpe | max DD | Calmar | win rate | turnover/yr |
| --- | --- | --- | --- | --- | --- | --- | --- |
| XSMOM-tercile (net) | 3.3% | 16.7% | 0.28 | -32.4% | 0.10 | 53.2% | 8.4x |
| XSMOM-rank (net) | 3.8% | 17.8% | 0.30 | -37.6% | 0.10 | 52.8% | 9.0x |
| TSMOM (net) | 7.4% | 10.3% | 0.75 | -15.6% | 0.48 | 62.4% | 17.6x |
| Equal-wt buy&hold | 2.7% | 9.7% | 0.33 | -34.8% | 0.08 | 63.3% | — |

> **Scale note.** XSMOM here is the *natural* dollar-neutral long-short book (Σ wₗₒₙ𝓰 = +1, Σ wₛₕₒᵣₜ = −1); TSMOM is the published engine strategy, already vol-targeted to ~10%. **Sharpe is scale-free**, so the comparison is fair; the raw max-DD / ann-vol differ because the books sit at different gross. §4 puts both at a common 10% vol for an apples-to-apples drawdown read. XSMOM is dollar-neutral / ≈0-beta, so it loses to a bull-market B&H *by design* — B&H is a background row, never the benchmark.

## 2. Is XSMOM distinguishable from zero? (vs 0, not vs B&H)

- **Tercile** Sharpe 0.28, 95% CI [-0.18, 0.75] — **crosses 0** (87.9% of resamples > 0).
- **Rank-weight** Sharpe 0.30, 95% CI [-0.16, 0.77] — **crosses 0**.
- Annual-return 95% CI (tercile): [-4.3%, 11.6%] — includes 0.

**Walk-forward (4-year non-overlapping blocks; no parameters fit ⇒ each block is OOS):**

| period | months | ann return | Sharpe | max DD |
| --- | --- | --- | --- | --- |
| 2008-2011 | 44.0 | 1.1% | 0.16 | -28.5% |
| 2012-2015 | 48.0 | 12.9% | 0.95 | -9.8% |
| 2016-2019 | 48.0 | -4.7% | -0.34 | -32.1% |
| 2020-2023 | 48.0 | 5.1% | 0.35 | -28.6% |
| 2024-2027 | 30.0 | 2.4% | 0.24 | -18.8% |

> 4/5 blocks positive → walk-forward **PASS**.

## 3. Correlation — the headline

- **`corr(XSMOM-tercile, TSMOM) = +0.42`** (monthly net, natural scale, identical months). Rank-weight: **+0.40**.
- corr(XSMOM-tercile, XSMOM-rank) = +0.98 (the two constructions agree).
- **No diversification payoff here.** ρ = +0.42 is *moderate and positive*, and because XSMOM's standalone edge (0.38) is far weaker than TSMOM's (0.75), the equal-risk mix (0.66) **dilutes rather than diversifies** — it underperforms TSMOM alone (0.75). At ETF granularity the two momentum forms substantially overlap (an honest negative for the diversification thesis; see §4).

## 4. Combined portfolio (equal-risk 50/50, vol-aligned to 10%)

Each leg is scaled to ~10% annualized vol with the **engine's vol estimator (verbatim)**, then combined 50/50. (Scaling is needed only here and for the equity curve; §1–3 use natural scale.)

| leg | Sharpe | realized vol |
| --- | --- | --- |
| XSMOM-tercile @10% | 0.38 | 10.2% |
| TSMOM @10% | 0.75 | 10.3% |
| **50/50 combined** | **0.66** | — |

- **Closed-form cross-check:** `S_combo = (S₁+S₂)/√(2(1+ρ))` = (0.38+0.75)/√(2(1++0.48)) = **0.66** vs realized **0.66**.
- Combined Sharpe does not beat the best single leg (0.75) by -0.09. ρ→0 ⇒ ≈1.41× single-leg Sharpe; ρ→1 ⇒ no gain.
- Equity curves (vol-aligned): [`xsmom_equity_curves.png`](xsmom_equity_curves.png).

## 5. Crisis windows — different-shaped tails

TSMOM's tail is **directional** (it earns crisis alpha by going net-short); XSMOM's tail is a **momentum crash** — the violent rebound of beaten-down losers blowing up the short leg (spring 2009). XSMOM has **no** directional crisis-alpha mechanism, so the two should behave differently in the same window (the physical source of low correlation).

| window | months | XSMOM cum | TSMOM cum | buy&hold cum |
| --- | --- | --- | --- | --- |
| GFC 2008 | 7 | 32.7% | 11.6% | -27.4% |
| Mom-crash 2009 | 4 | -24.9% | -4.5% | 14.8% |
| COVID 2020 | 3 | 17.3% | 7.3% | -13.0% |
| Calm 2012-2019 | 96 | 33.7% | 70.3% | 22.3% |

## 6. Robustness (appendix — never used to pick parameters)

**Formation neighbourhood (3/6/9/12-month, same 21-day skip):**

| formation | Sharpe | ann return | max DD |
| --- | --- | --- | --- |
| 3-1 (63d) | 0.30 | 3.6% | -37.4% |
| 6-1 (126d) | 0.42 | 5.6% | -29.8% |
| 9-1 (189d) | 0.51 | 7.3% | -28.2% |
| 12-1 (252d) | 0.28 | 3.3% | -32.4% |
> Same sign across the neighbourhood: **True** (sign/magnitude consistency, not a search for the best lookback).

**Tercile vs rank-weight:** Sharpe 0.28 vs 0.30, return corr +0.98 — conclusions agree.

## 7. Confound decomposition — momentum or static premium?

The cross-asset universe has structurally different long-run mean returns (equities > bonds, 2007–2026). Baseline XSMOM on average longs equities / shorts bonds — part of which is **static equity risk premium disguised as momentum**. Two controls strip that out (both on the rank-weight basis): **(a) within-class** ranking (equities vs equities, …) and **(b) demeaned signal** (subtract each asset's *ex-ante expanding* mean before ranking — the only look-ahead-free demean).

| spec | Sharpe | 95% CI | vs 0 |
| --- | --- | --- | --- |
| rank baseline | 0.30 | [-0.16, 0.77] | crosses 0 |
| within-class | 0.32 | [-0.13, 0.78] | crosses 0 |
| demeaned signal | 0.14 | [-0.32, 0.60] | crosses 0 |

> Edge **does NOT survive** both controls → a meaningful part was static cross-asset risk premium — reported honestly.

---
*Reuses the multi-asset TSMOM engine (signal-construction layers added in `src/xsmom.py`). No engine code was modified; the existing 43 no-look-ahead / correctness tests still pass alongside the new XSMOM tests. Research/education only — not investment advice.*