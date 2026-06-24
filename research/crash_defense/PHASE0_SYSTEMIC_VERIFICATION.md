# Phase 0 — Systemic verification (standalone, bias-free)

*Read-only. Standalone unit-risk sleeve streams (each its own 10%-vol TSMOM via `build_portfolio`), vs the diagnostic's portfolio-weighted contribution streams.*

## 1+2. Co-drawdown — standalone vs portfolio-weighted

| # | window | depth | standalone down | portfolio-wtd down |
| --- | --- | --- | --- | --- |
| 1 | 2022-09-30→2023-11-30 | -15.6% | 5/5 (100%) | 80% |
| 2 | 2018-01-31→2019-01-31 | -10.3% | 4/5 (80%) | 80% |
| 3 | 2010-04-30→2010-07-31 | -8.6% | 3/5 (60%) | 80% |
| 4 | 2015-01-31→2015-10-31 | -8.4% | 4/5 (80%) | 80% |
| 5 | 2024-09-30→2025-04-30 | -7.9% | 3/5 (60%) | 60% |
| 6 | 2012-01-31→2012-06-30 | -7.5% | 3/5 (60%) | 100% |
| 7 | 2008-06-30→2008-07-31 | -6.8% | 5/5 (100%) | 100% |
| 8 | 2013-04-30→2013-09-30 | -6.6% | 3/5 (60%) | 80% |
| 9 | 2009-11-30→2010-01-31 | -6.4% | 5/5 (100%) | 100% |
| 10 | 2014-06-30→2014-09-30 | -5.6% | 4/5 (80%) | 80% |
| 11 | 2021-10-31→2022-01-31 | -5.1% | 5/5 (100%) | 100% |

- **Mean standalone frac-down: 80%** vs portfolio-weighted 85% (diagnostic ~85%).

## 3. Cross-sleeve correlation (standalone, equal-weighted pairs)

- outside drawdowns: **+0.162** (125 mo)
- during drawdowns: **+0.123** (47 mo)
- delta: **-0.039** (does not spike during drawdowns)

## 4. Event anchoring

- Deepest episode #1 (2022-09-30→2023-11-30, -15.6%) standalone sleeve cum net: Equity -16.6%, Bond -16.2%, Commodity -13.3%, FX -5.7%, RealEstate -9.0%.
- GFC 2008 window strategy net: **+11.3%** (in a flagged drawdown? False).
- COVID 2020 window strategy net: **+7.4%** (in a flagged drawdown? False).

## 5. Would a systemic-risk trigger fire in the right place?

| window | port_vol_pctile | dispersion_pctile |
| --- | --- | --- |
| drawdowns | 0.49 | 0.55 |
| GFC 2008 | 0.95 | 0.94 |
| COVID 2020 | 0.94 | 0.95 |
| full sample | 0.49 | 0.50 |

> If GFC/COVID read higher than 'drawdowns', a de-grossing trigger fires where the strategy MAKES money (killing crisis alpha) and stays quiet in the real drawdowns.

## Verdict

Systemic claim **NOT confirmed** on a bias-free basis.