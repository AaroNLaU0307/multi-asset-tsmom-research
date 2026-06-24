# Study Summary — Multi-Asset Time-Series Momentum

*A falsification-oriented research study. Every result below is reported as-is; no
parameter was tuned to flatter the numbers, and the limitations section is not
optional.*

---

## 1. Research question

A prior pair of projects backtested **single-instrument** trend / Smart-Money-Concept
strategies on XAUUSD ([quant-backtest-framework](https://github.com/AaroNLaU0307/quant-backtest-framework))
and, using walk-forward and Monte-Carlo validation, **honestly
falsified them**: the Sharpe confidence intervals crossed zero — no confirmable edge.
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
estate, the universe was screened **objectively** rather than hand-picked:

- **Daily-return correlation matrix** (not price levels — price correlation is
  spuriously inflated by shared trends).
- **Hierarchical clustering** on `1 − correlation` distance to count *effective
  independent factors*: the 30 ETFs collapsed to **~12 clusters at a 0.60 correlation
  cut** — i.e. far fewer truly independent bets than 30 names suggest.
- A **greedy correlation filter** removed redundancies (`|r| ≥ 0.80`): e.g. QQQ/XLK/IWM/
  XLF/EFA are ~0.85–0.97 correlated with SPY (the US-equity factor is already
  represented), IEF is 0.92 with TLT, FXE is −0.94 with UUP (the euro is the inverse of
  the USD factor).
- Three more were dropped for a **deliberate sample-window trade-off** (see §3): CPER,
  WEAT, CORN — the only assets whose 2010–2011 inceptions blocked the **2008 crisis**
  sample.

**Final universe: 17 ETFs** spanning equities (SPY, EEM, EWJ, XLE, XLU), bonds (TLT,
SHY, LQD, HYG), commodities (USO, UNG, GLD, DBA), FX (UUP, FXY) and real estate (VNQ,
RWX). Common data window **2007-04-18 → 2026-06**, bound by UNG's inception, covering
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

- **Bootstrap 95% CI on Sharpe: [0.29, 1.23] — does not cross 0** (100% of 10,000
  resamples > 0). Annualized-return CI [2.5%, 12.6%] also excludes 0.
- **Crisis alpha** — the core of TSMOM's value (it can go short; buy & hold cannot):

  | Regime | TSMOM cum. return | Buy & hold |
  | --- | --- | --- |
  | GFC 2008 | **+11.6%** | −27.4% |
  | COVID 2020 | **+7.3%** | −13.0% |
  | Calm 2012–2019 | +70.3% | +22.3% |

- **Walk-forward stability** (no parameters fit): sub-period Sharpes 0.78 / 0.71 / 0.74 /
  0.58 / 1.06 — every block positive; the edge is not one lucky stretch.

→ **This is a confirmable edge at the 95% level — materially different from the
single-instrument null.** It is *real but modest*; the CI is wide and the lower bound
(0.29) is only mildly positive.

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
  regime cycle — limited statistical power. The edge is real but its *magnitude* is
  uncertain.
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
   single-instrument strategy and confirmed a diversified multi-asset one. Diversifying
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

This is the third project in a deliberate arc using one honest validation methodology:

- **SMC / breakout on XAUUSD (single instrument)** → *falsified* (CI crosses 0); low
  signal-to-noise is a mathematical inevitability for one instrument.
  [github.com/AaroNLaU0307/quant-backtest-framework](https://github.com/AaroNLaU0307/quant-backtest-framework)
- **Multi-asset TSMOM (this project)** → *confirmed* a modest, cost-capped edge with
  genuine crisis alpha, via cross-factor diversification.
- Together: a portfolio that **both falsifies ineffective strategies and confirms
  effective ones** with the same rigor — the point is the methodology, not a number.

**Future work:** true futures data (remove ETF roll/expense bias and extend the history
pre-2008); cross-sectional momentum as a complementary factor; an explicit
transaction-cost-aware execution layer; and combining trend with carry/value for a
multi-style program.

---

*Research / educational use only. Not investment advice. Past (or backtested)
performance does not guarantee future results.*
