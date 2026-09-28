# Study Summary — Multi-Asset Time-Series Momentum

*A falsification-oriented research study. Every result below is reported as-is; no
parameter was tuned to flatter the numbers, and the limitations section is not
optional.*

---

## 1. Research question

A prior pair of projects backtested **single-instrument** trend / Smart-Money-Concept
strategies on XAUUSD ([quant-backtest-framework](https://github.com/AaroNLaU0307/quant-backtest-framework))
and, using walk-forward and Monte-Carlo validation, **honestly
falsified them**: the Sharpe confidence intervals crossed zero — no confirmable edge (the verdict held
in the re-run on the engine corrected on 2026-09-27: 0/42 BH-FDR survivors on XAUUSD,
[`output/grid/master_table.csv`](https://github.com/AaroNLaU0307/quant-backtest-framework/blob/main/output/grid/master_table.csv)).
The lesson was not "trend doesn't work" but that a **single instrument has too low a
signal-to-noise ratio** for a confirmable edge to survive honest statistics.

This project asks the natural follow-up:

> **Can diversifying time-series momentum across many independent risk factors raise
> the signal-to-noise ratio enough to produce a *confirmable* edge — and does that
> edge survive honest, falsification-oriented validation?**

Time-series momentum (TSMOM) is a good test case: it has decades of published evidence
across asset classes (Moskowitz–Ooi–Pedersen 2012; AQR's "A Century of Evidence on
Trend-Following"), so a clean implementation *should* find something — if the method
and the statistics are sound.

---

## 2. Method overview

### 2.1 Universe construction (30 → 17, by independent factor, not by count)

Starting from 30 candidate ETFs across equities, bonds, commodities, FX and real
estate, the universe was cut by a correlation screen plus discretionary trims, then a
sample-window step (all three lists are in [`universe.py`](universe.py)):

- **Daily-return correlation matrix** (not price levels — price correlation is
  spuriously inflated by shared trends).
- **Hierarchical clustering** on `1 − correlation` distance to count *effective
  independent factors*: the 30 ETFs collapsed to **~12 clusters at a 0.60 correlation
  cut** — i.e. far fewer truly independent bets than 30 names suggest.
- A **greedy correlation filter** removed redundancies (`|r| ≥ 0.80`): e.g. QQQ/XLK/IWM/
  XLF/EFA are ~0.85–0.97 correlated with SPY (the US-equity factor is already
  represented), IEF is 0.92 with TLT, FXE is −0.94 with UUP (the euro is the inverse of
  the USD factor).
- Three more were dropped by **discretionary trim below that threshold**: XLV (0.79 with
  SPY), GDX (0.77) and SLV (0.79, both with GLD). The greedy filter would have kept them;
  this was judgement, not the fixed rule.
- Three more were dropped for a **deliberate sample-window trade-off** (see §3): CPER,
  WEAT, CORN — the only assets whose 2010–2011 inceptions blocked the **2008 crisis**
  sample.

**Final universe: 17 ETFs** spanning equities (SPY, EEM, EWJ, XLE, XLU), bonds (TLT,
SHY, LQD, HYG), commodities (USO, UNG, GLD, DBA), FX (UUP, FXY) and real estate (VNQ,
RWX). Common data window **2007-04-18 → 2026-06-12** (`config.CORE_END_DATE`), bound by UNG's inception, covering
**both the 2008 GFC and the 2020 COVID crash**.

### 2.2 The five-step pipeline

1. **Signal** — TSMOM direction per asset. Default = multi-period composite: mean of the
   signs of `{1, 3, 6, 12}`-month returns, evaluated on month-end closes.
2. **Per-asset volatility scaling** — `weight = signal × target_vol / asset_vol`
   (60-day vol, 10% target), capped at ±2.0 to stop ultra-low-vol assets (SHY)
   demanding extreme leverage.
3. **Portfolio aggregation** — equal-weight average of the vol-scaled positions.
4. **Portfolio risk control** — scale the book to a 10% portfolio vol target
   (dynamic de-levering when realized vol is high), capped at 3.0× gross notional.
5. **Validation** — returns net of costs, then bootstrap CIs, regime attribution,
   walk-forward, Monte Carlo, and a buy-&-hold comparison.

Every stage is **no-look-ahead by construction and unit-tested** (truncation
invariance: signals/weights computed on a data prefix `[:t]` equal the full-data
values sliced at `t`). Positions are always the *previous* month-end's decision
(`positions = weights.shift(1)`).

---

## 3. Key design decisions (and why)

| Decision | Rationale |
| --- | --- |
| **Select by independent factor, not by count** | 30 names ≈ 12 independent bets. Adding correlated ETFs is fake diversification; it inflates apparent breadth without raising signal-to-noise. |
| **Do NOT optimize the lookback** — use the conventional `{1,3,6,12}` months | The whole prior-project lesson is that tuning manufactures in-sample edges that vanish out of sample. Conventional academic lookbacks avoid that degree of freedom entirely. |
| **Volatility scaling** | Equalizes ex-ante risk per asset so no single high-vol asset (oil, nat-gas) dominates portfolio risk. |
| **Equal-weight, NOT covariance optimization** | A 17×17 covariance is noisily estimated and unstable in crises; mean-variance/risk-parity optimizers routinely lose to 1/N out of sample (DeMiguel–Garlappi–Uppal 2009). Equal-weight on vol-scaled positions is already a naive risk parity. (Tested as a control — §5.3.) |
| **Trade WEAT/CORN for the 2008 sample** | The grains were only moderately distinct (corr ~0.55–0.64 with DBA) but were the *only* assets blocking the GFC. Capturing 2008 — the regime where trend-following earns its reputation — was worth more than two marginal agriculture factors. |
| **Costs always modelled; reported gross and net** | An edge that only exists gross of costs is not an edge. |

---

## 4. Main result (honest)

Evaluation window: **2008-05 → 2026-06 (218 months)**, the period when all 17 assets are
live. `rf = 0` (disclosed; ~1–2% cash would trim Sharpe slightly).

| Metric (net of 2 bps) | TSMOM | Equal-weight buy & hold |
| --- | --- | --- |
| Annualized return | 7.4% | 2.7% |
| Annualized vol | 10.3% | 9.7% |
| **Sharpe** | **0.75** | 0.33 |
| Max drawdown | **−15.6%** | −34.8% |
| Calmar | 0.48 | 0.08 |
| Win rate (months) | 62% | 63% |

- **Bootstrap 95% CI on Sharpe: [0.29, 1.23] — does not cross 0** (99.95% of 10,000
  resamples > 0). Annualized-return CI [2.5%, 12.6%] also excludes 0. Not deflated: the
  historical trial count for this panel is unknown
  ([`TRIAL_LEDGER`](research/extensions/TRIAL_LEDGER.md) §3.2).
- **Crisis alpha** — the core of TSMOM's value (it can go short; buy & hold cannot):

  | Regime | TSMOM cum. return | Buy & hold |
  | --- | --- | --- |
  | GFC 2008 | **+11.6%** | −27.4% |
  | COVID 2020 | **+7.3%** | −13.0% |
  | Calm 2012–2019 | +70.3% | +22.3% |

- **Walk-forward stability** (no parameters fit): sub-period Sharpes 0.78 / 0.71 / 0.74 /
  0.58 / 1.06 — every block positive; the edge is not one lucky stretch.

→ **SUPPORTED — the CI excludes 0; not independently confirmed.** No held-out or
independent confirmation exists; the core was not pre-registered, and its prospective test
(C-A) has been live since 2026-09-13 with no month scored yet. Materially different from the
single-instrument null, but *modest*: the CI is wide and the lower bound (0.29) is only
mildly positive.

---

## 5. Three control experiments

### 5.1 Parameter robustness (is 0.75 a fragile sweet spot?)
45 parameter combinations (single & multi-period lookbacks, target vols 8–15%, vol
windows 40–120d): **net Sharpe range [0.38, 0.87], 100% positive, 89% above 0.5**. The
conventional default sits at the **71st percentile — not the peak** (e.g. `{6,12}` scores
0.87 > the default 0.75), demonstrating no sweet-spot cherry-picking. The only soft spot
is an isolated single-15-month horizon (0.39) — sample noise (its 12m/18m neighbours are
~0.70), and an argument *for* the multi-period blend. **Verdict: robust.**

### 5.2 Cost sensitivity (where does the edge break?)
Turnover ≈ 17.6×/yr (81% from signal/sizing changes, only 19% from leverage re-scaling).

| One-way cost | Net Sharpe | CI excludes 0? |
| --- | --- | --- |
| 2 bps | 0.75 | yes |
| 5 bps (realistic blend) | 0.70 | yes |
| 10 bps | 0.61 | yes |
| 20 bps | 0.44 | **no — CI [−0.01, 0.92]** |

→ **The edge survives to ~10 bps one-way but becomes marginal at 20 bps.** It is
cost-sensitive at the illiquid-ETF end. A **no-trade band** was tried to cut turnover;
it only reduced turnover ~9% (turnover is mostly genuine signal-driven trades, not
waste) and *slightly hurt* net Sharpe — **an honest negative result; the band was not
adopted.**

### 5.3 Risk parity vs equal-weight (does complexity pay?)
Same pipeline, swapping only the aggregation (net @ 5 bps):

| Aggregation | Net Sharpe | 95% CI | Turnover | Covariance needed? |
| --- | --- | --- | --- | --- |
| Equal-weight (main) | 0.70 | [0.24, 1.18] | 17.6× | no |
| Inverse-volatility | 0.78 | [0.32, 1.27] | 21.2× | no |
| Risk parity (ERC) | 0.73 | [0.27, 1.22] | 22.0× | yes (noisy) |

→ The alternatives' point Sharpes are higher but **within equal-weight's bootstrap CI —
not statistically distinguishable.** The covariance-based ERC adds an unstable estimate
for no clear gain. **The control supports the simple equal-weight choice**: as good,
fewer parameters, lower turnover, no covariance dependence.

---

## 6. Honest limitations (not hidden)

- **Wide confidence interval.** Sharpe CI lower bound is 0.29; 218 months ≈ one full
  regime cycle — limited statistical power. The edge is supported but its *magnitude* is
  uncertain, and the CI is not deflated for the (unknown) number of historical trials.
- **Cost sensitivity.** Survives to ~10 bps; at a pessimistic 20 bps (illiquid ETFs like
  UNG/RWX/DBA) the CI crosses 0.
- **Monte-Carlo tail risk.** Realized max drawdown (−15.6%) was on the benign side:
  across 10,000 bootstrap paths, **P(drawdown ≥ 20%) ≈ 45%** and P(≥ 30%) ≈ 7%. A 20%+
  drawdown is plausible.
- **Sample window** starts ~2008; it does not include earlier trend regimes (the 17-ETF
  universe did not exist before then).
- **ETF proxies, not true futures.** Some commodity/FX ETFs carry roll/expense drag and
  are imperfect proxies for the underlying futures a real TSMOM program would trade.
- **rf = 0** in the Sharpe; incorporating cash would lower it slightly.

---

## 7. Transferable conclusions

1. **Signal-to-noise is the deciding variable.** The same honest methodology falsified a
   single-instrument strategy and supported (CI excludes 0; not independently confirmed) a
   diversified multi-asset one. Diversifying
   across *independent* factors — not adding correlated names — is what made the edge
   detectable.
2. **Point estimates lie; look at the distribution.** A single Sharpe number is
   meaningless without its CI, regime breakdown, and drawdown distribution. The
   contaminated full-history run showed Sharpe 1.00; the honest full-universe window
   showed 0.75.
3. **Simple and robust beats complex and fragile.** Equal-weight ties risk parity;
   conventional lookbacks beat tuned ones out of sample; a clever turnover trick didn't
   help. Complexity must *earn* its place against a noise-aware baseline.
4. **Anti-overfitting discipline is a process, not a slogan.** No parameter was tuned on
   results; controls were run to *falsify* "robust", not to confirm it; negative results
   (the band) were reported as plainly as positive ones.

---

## 8. Research arc & future directions

One honest validation methodology, applied at two levels.

**Across projects** — signal-to-noise is the deciding variable:

- **SMC / breakout on XAUUSD (single instrument)** → *falsified* (CI crosses 0; held in the 2026-09-27 corrected-engine re-run, [`output/grid/master_table.csv`](https://github.com/AaroNLaU0307/quant-backtest-framework/blob/main/output/grid/master_table.csv)); low
  signal-to-noise is a mathematical inevitability for one instrument.
  [github.com/AaroNLaU0307/quant-backtest-framework](https://github.com/AaroNLaU0307/quant-backtest-framework)
- **Multi-asset TSMOM (this project)** → *supported* (CI excludes 0; not independently
  confirmed) a modest, cost-capped edge with genuine crisis alpha, via cross-factor
  diversification.
- **Cross-sectional momentum (XSMOM)** — *now folded into this repo*
  ([`research/xsmom/`](research/xsmom/XSMOM_README.md)) → did *not* confirm at ETF granularity:
  standalone Sharpe 0.28 (CI crosses 0), **+0.42-correlated** with the supported TSMOM core (no
  diversification), and **0/5** universes in the Phase-2 FDR-controlled map. The cross-sectional
  premium that large single-name universes show dissipates across liquid ETFs.

**Within this project** — with the modest core supported, **four orthogonal overlay
families** were tested to extend it, **each rejected at the cheapest premise stage and recorded
as `not_promoted`** (full write-ups in [`research/`](research/README.md)):

- **Crash-defense** — `not_promoted` (rejected at Phase 0; premise not supported, a descriptive
  comparison with no inference): the strategy's pain does not look like a systemic-risk-spike
  regime; the trigger maxes out in the 2008/2020 *profit* windows and is average in the real
  drawdowns.
- **Vol-compression breakout** — `not_promoted` (rejected at Phase 1B; premise not supported, a
  descriptive comparison with no inference): close-to-close compression precedes vol expansion
  but **not direction**; the apparent edge was a narrow-channel counting artifact.
- **Seasonality / calendar effects** — `not_promoted` (rejected at premise, 0/18): **0 of 18** pre-registered cells survived the
  BH-FDR + magnitude + stability conjunction. The textbook equity turn-of-month premium is
  ~+0.5 bps at ETF granularity (arbitraged away — the same mechanism as the XSMOM finding), and
  the one tempting near-miss — the **Monday** effect, "significant" in isolation (Bond *p*=0.026)
  — is one raw *p* < 0.05 in 18 tests, about what noise alone produces; that cell also fails the
  pre-registered magnitude and stability gates, and no cell survives BH-FDR — all settled *before
  any P&L was fit*.
- **Yield-curve slope (macro regime)** — `not_promoted` (rejected at premise, 0/6): a single
  economy-wide curve slope (10Y-3M primary, 10Y-2Y robustness) as a **portfolio-regime
  conditioner**; **0 of 6** pre-registered cells confirmed (BH-FDR *p* = 0.60–0.67, every bootstrap
  CI crosses 0) — a **clean null with no claimable direction**. Dropping the 2022-24 episode keeps
  26–68% of the weak whipsaw-side (H−) tilt, sign unchanged in all 6 cells, and takes the two
  h = 126 cells below the 4%/yr bar; the tested tercile-flat state spans 12–13 episodes, of which
  2022-24 is 19–21% of the days. The binding-episode jackknife rule was changed after the first run;
  under the registered rule 3 of 6 cells pass it, so the null rests on BH-FDR, not on the jackknife
  ([`research/ERRATA_2026-09-27.md`](research/ERRATA_2026-09-27.md) §1–2). Lesson kept: ~4,800
  trading days of a slow macro state are only about a dozen independent episodes.

**The meta-point.** The modest TSMOM edge has **no obvious orthogonal extension in the four
directions tested** — three price-based (crash-defense, vol-breakout, seasonality) and one genuinely
macro / orthogonal to the price paths (yield-curve slope) — and establishing that, *with each
failure's mechanism*, is itself the deliverable. The same machinery that **supported** the core also
**rejected** every plausible addition, and along the way declined a tempting **calendar effect**
(seasonality's Monday: one raw *p* < 0.05 in 18 tests, as noise predicts; none survives BH-FDR). A broader **macro-regime overlay**
was deliberately not separately tested — pre-emptively ruled out at the event-count level: as the same
class of slow, economy-wide signal as the yield curve, its regime transitions are equally sparse
in-sample, so it would face the same shortage of independent episodes; declining to test a direction
already known to be this sparse is disciplined budget allocation, not an untested gap. Negatives are
first-class results here, reported as plainly as the one positive.

**Future work:** true futures data (remove ETF roll/expense bias and extend the history
pre-2008); an explicit transaction-cost-aware execution layer; and combining trend with
carry/value for a multi-style program.

---

*Research / educational use only. Not investment advice. Past (or backtested)
performance does not guarantee future results.*
