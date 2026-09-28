# Backtest & Validation — Multi-Asset TSMOM (equal-weight, vol-targeted)

*Generated 2026-09-29 01:08. Honest validation — results reported as-is, no parameter tuning.*
*Return period: **2008-05-31 → 2026-06-30** (218 months), panel truncated at 2026-06-12. rf = 0% (disclosed).*

## TL;DR — does the net-Sharpe CI exclude 0?

- **Net Sharpe = 0.75**, 95% bootstrap CI **[0.29, 1.23]** → **DOES NOT cross 0** (99.95% of resamples > 0). Not deflated: the historical trial count for this panel is unknown (research/extensions/TRIAL_LEDGER.md).
- Net annualized return 95% CI: **[2.5%, 12.6%]** → excludes 0.
- **Verdict: SUPPORTED — CI excludes 0; not independently confirmed.**

## 1. Return calculation & costs

- **Evaluation window = only months when all 17 assets are live** (full universe with 12-month signals, from ~2008). Earlier months would be a smaller, growing universe — a different strategy — so they are excluded for an honest read.
- Monthly return = Σ(position × asset monthly return); **position = portfolio weight `shift(1)`** (decided the prior month-end → no look-ahead, unit-tested).
- Costs: **2 bps one-way × turnover** (liquid-ETF convention; intra-month drift ignored). Reported gross & net.
- Avg annual turnover ≈ **17.6×**; cost drag ≈ **0.4%/yr**.

## 2. Core performance (gross vs net vs buy&hold)

|  | ann return | ann vol | Sharpe | max DD | Calmar | win rate |
| --- | --- | --- | --- | --- | --- | --- |
| TSMOM gross | 7.8% | 10.3% | 0.78 | -15.2% | 0.51 | 63.3% |
| TSMOM net | 7.4% | 10.3% | 0.75 | -15.6% | 0.48 | 62.4% |
| Equal-wt buy&hold | 2.7% | 9.7% | 0.33 | -34.8% | 0.08 | 63.3% |

## 3. Bootstrap confidence intervals (net, 10,000 resamples)

- **Sharpe**: point 0.75, 95% CI [0.29, 1.23] — **does not cross 0**.
- **Annual return**: point 7.4%, 95% CI [2.5%, 12.6%] — **does not cross 0**.

## 4. Regime attribution (crisis alpha test)

| regime | months | TSMOM cum return | buy&hold cum return |
| --- | --- | --- | --- |
| GFC 2008 | 7 | 11.6% | -27.4% |
| COVID 2020 | 3 | 7.3% | -13.0% |
| Calm 2012-2019 | 96 | 70.3% | 22.3% |

> Crisis alpha = does the strategy hold up (or profit) when buy&hold is crashing? Momentum can go short; buy&hold cannot.

## 5. Walk-forward / sub-period stability (no params fit)

| period | months | ann return | Sharpe | max DD |
| --- | --- | --- | --- | --- |
| 2008-2011 | 44.0 | 8.0% | 0.78 | -8.6% |
| 2012-2015 | 48.0 | 7.0% | 0.71 | -8.4% |
| 2016-2019 | 48.0 | 6.7% | 0.74 | -10.3% |
| 2020-2023 | 48.0 | 6.1% | 0.58 | -15.6% |
| 2024-2027 | 30.0 | 10.5% | 1.06 | -7.9% |

## 6. Monte Carlo path risk (10,000 paths each)

**bootstrap** — maxDD median -19.2%, 5th-pctile -31.7%, worst -59.1%; terminal $1→ median 3.66 (95% [1.58, 8.55]); P(loss)=0.1%, P(DD≥20%)=44.7%, P(DD≥30%)=7.2%.

**shuffle** — maxDD median -19.1%, 5th-pctile -28.8%, worst -45.2%; terminal $1→ median 3.67 (95% [3.67, 3.67]); P(loss)=0.0%, P(DD≥20%)=42.6%, P(DD≥30%)=3.5%.

Fan chart: [`monte_carlo_fan_chart.png`](monte_carlo_fan_chart.png).

## 7. vs Buy & Hold

- Sharpe: **TSMOM 0.75** vs **buy&hold 0.33**.
- Max drawdown: **TSMOM -15.6%** vs **buy&hold -34.8%**.
- Crisis windows (cum return), strategy vs buy&hold: see §4.
- Equity curves: [`equity_curve.png`](equity_curve.png); drawdown: [`drawdown.png`](drawdown.png).
> Note: TSMOM is vol-targeted (~10%); buy&hold is unlevered. Sharpe is scale-free (fair); raw drawdowns also reflect the vol difference.

## 8. Calendar-year net returns

| year | net return |
| --- | --- |
| 2008 | 8.3% |
| 2009 | 10.6% |
| 2010 | 1.8% |
| 2011 | 8.8% |
| 2012 | 0.6% |
| 2013 | 17.2% |
| 2014 | 11.0% |
| 2015 | 0.3% |
| 2016 | 4.4% |
| 2017 | 14.8% |
| 2018 | -0.8% |
| 2019 | 9.2% |
| 2020 | 11.6% |
| 2021 | 7.5% |
| 2022 | 15.0% |
| 2023 | -8.3% |
| 2024 | 11.0% |
| 2025 | 11.7% |
| 2026 | 3.6% |
