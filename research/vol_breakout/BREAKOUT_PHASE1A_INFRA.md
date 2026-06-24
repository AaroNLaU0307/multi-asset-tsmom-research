# Phase 1A — Daily research infrastructure (vol-compression breakout)

*Read-only infra. Reuses the existing 17-ETF universe, the cached daily adjusted-close loader (same source the monthly engine resamples), and the verified-causal regime primitives. No strategy/positions/P&L.*

## Data coverage

- Source: `close_prices_raw.csv` — cached yfinance adjusted close, identical to the monthly backtest's source (so daily and monthly stay reconcilable).
- Daily frame: **8400 rows × 17 assets**, 1993-01-29 → 2026-06-12.
- **All-17-present daily window: 2007-04-18 → 2026-06-12** (4820 trading days), bound by UNG's 2007-04-18 inception — the same bound as the monthly engine.
- Short daily history (post-2006 inception): USO, RWX, DBA, FXY, UUP, HYG, UNG. No tickers are dropped; the common window already accounts for them.

## Causal daily primitives (truncation-invariance)

All trailing-window only; breakout references exclude the current day. Recomputing each on a 70% price prefix reproduces the full-data values exactly at the overlap:

| primitive | max abs diff vs prefix |
| --- | --- |
| `daily_returns` | 0.00e+00 |
| `realized_vol` | 0.00e+00 |
| `vol_percentile` | 0.00e+00 |
| `recent_high` | 0.00e+00 |
| `recent_low` | 0.00e+00 |

**Strictly causal / no look-ahead: True.** Built: daily returns, realized vol (window 20d), vol percentile (trailing 252d rank = the compression measure), recent-high / recent-low (20d Donchian breakout references).

## Daily → monthly reconciliation (ties to the validated engine)

- Compounding daily simple returns within each month vs the engine's `to_monthly(px).pct_change()`:
- **max abs diff = 1.33e-15** over 4715 asset-months (402 months × 17 assets) → reconciles (telescoping identity). The daily data is consistent with the monthly engine.

Sample primitives (SPY, last 200 rows): [`daily_primitives_sample.csv`](daily_primitives_sample.csv).

## Conventions (stated up front, NOT searched)

- compression vol window = 20d; percentile window = 252d; compressed = percentile ≤ 0.2.
- breakout lookback = 20d; premise horizons = (5, 10, 20) days.
- Compression uses realized-vol percentile (adjusted-close data has no intraday H/L for a true ATR); same verified definition style as the Step-5 regime vars.