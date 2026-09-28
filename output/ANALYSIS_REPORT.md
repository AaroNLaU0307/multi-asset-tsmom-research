# Multi-Asset TSMOM — Step 1: Data, Correlation & Universe Screening

*Generated: 2026-09-29 01:13*  
*Universe: 30 ETFs. Source: yfinance (adjusted Close, `auto_adjust=True`).*  
*Scope: data acquisition + correlation analysis + screening **suggestions** only. No strategy, no signals, no backtest. Nothing is auto-dropped.*

## 0. Fetch status
All 30 tickers fetched successfully.

## 1. Data quality

- **Short-history flags** (start after 2010-01-01): `CPER`, `WEAT`, `CORN`
- **Daily-jump anomalies** (|return| > 50%): none
- **Suspected bad prints** (spike-and-revert, both legs > 25%): `CPER`

| ticker | factor | start_date | end_date | n_trading_days | internal_missing | short_history_flag | n_jumps | max_abs_daily_move | max_move_date | n_spike_revert | spike_revert_detail |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SPY | Equity/US-LargeCap | 1993-01-29 | 2026-06-12 | 8400 | 0 | False | 0 | 0.1452 | 2008-10-13 | 0 |  |
| QQQ | Equity/US-Nasdaq100 | 1999-03-10 | 2026-06-12 | 6858 | 0 | False | 0 | 0.1684 | 2001-01-03 | 0 |  |
| IWM | Equity/US-SmallCap | 2000-05-26 | 2026-06-12 | 6550 | 0 | False | 0 | 0.1327 | 2020-03-16 | 0 |  |
| EFA | Equity/DevelopedExUS | 2001-08-27 | 2026-06-12 | 6235 | 0 | False | 0 | 0.1589 | 2008-10-13 | 0 |  |
| EEM | Equity/EmergingMkts | 2003-04-14 | 2026-06-12 | 5829 | 0 | False | 0 | 0.2277 | 2008-10-13 | 0 |  |
| EWJ | Equity/Japan | 1996-03-18 | 2026-06-12 | 7609 | 0 | False | 0 | 0.1582 | 2008-10-13 | 0 |  |
| TLT | Bond/US-Treasury-Long | 2002-07-30 | 2026-06-12 | 6007 | 0 | False | 0 | 0.0752 | 2020-03-20 | 0 |  |
| IEF | Bond/US-Treasury-Interm | 2002-07-30 | 2026-06-12 | 6007 | 0 | False | 0 | 0.0343 | 2009-03-18 | 0 |  |
| SHY | Bond/US-Treasury-Short | 2002-07-30 | 2026-06-12 | 6007 | 0 | False | 0 | 0.01 | 2023-03-13 | 0 |  |
| LQD | Bond/US-IG-Credit | 2002-07-30 | 2026-06-12 | 6007 | 0 | False | 0 | 0.0977 | 2008-09-30 | 0 |  |
| HYG | Bond/US-HY-Credit | 2007-04-11 | 2026-06-12 | 4825 | 0 | False | 0 | 0.1227 | 2008-10-13 | 0 |  |
| USO | Commodity/Energy-Oil | 2006-04-10 | 2026-06-12 | 5076 | 0 | False | 0 | 0.2532 | 2020-03-09 | 0 |  |
| UNG | Commodity/Energy-NatGas | 2007-04-18 | 2026-06-12 | 4820 | 0 | False | 0 | 0.2485 | 2026-02-02 | 0 |  |
| XLE | Equity/Sector-Energy | 1998-12-22 | 2026-06-12 | 6910 | 0 | False | 0 | 0.2014 | 2020-03-09 | 0 |  |
| GLD | Commodity/Metal-Gold | 2004-11-18 | 2026-06-12 | 5425 | 0 | False | 0 | 0.1129 | 2008-09-17 | 0 |  |
| SLV | Commodity/Metal-Silver | 2006-04-28 | 2026-06-12 | 5063 | 0 | False | 0 | 0.2854 | 2026-01-30 | 0 |  |
| CPER | Commodity/Metal-Copper | 2011-11-15 | 2026-06-12 | 3664 | 0 | True | 0 | 0.4989 | 2014-12-05 | 2 | 2014-12-05(-33%->+50%); 2015-02-03(-29%->+46%) |
| DBA | Commodity/Agri-Broad | 2007-01-05 | 2026-06-12 | 4890 | 0 | False | 0 | 0.0861 | 2008-10-06 | 0 |  |
| WEAT | Commodity/Agri-Wheat | 2011-09-19 | 2026-06-12 | 3705 | 0 | True | 0 | 0.1561 | 2022-03-03 | 0 |  |
| CORN | Commodity/Agri-Corn | 2010-06-09 | 2026-06-12 | 4028 | 0 | True | 0 | 0.1459 | 2010-10-08 | 0 |  |
| UUP | FX/USD-Bull | 2007-03-01 | 2026-06-12 | 4853 | 0 | False | 0 | 0.0406 | 2007-06-21 | 0 |  |
| FXE | FX/EUR | 2005-12-12 | 2026-06-12 | 5157 | 0 | False | 0 | 0.0367 | 2009-03-18 | 0 |  |
| FXY | FX/JPY | 2007-02-13 | 2026-06-12 | 4864 | 0 | False | 0 | 0.0435 | 2008-10-28 | 0 |  |
| VNQ | RealEstate/US-REIT | 2004-09-29 | 2026-06-12 | 5461 | 0 | False | 0 | 0.1951 | 2008-12-01 | 0 |  |
| RWX | RealEstate/ExUS-REIT | 2006-12-19 | 2026-06-12 | 4900 | 0 | False | 0 | 0.1071 | 2008-10-13 | 0 |  |
| XLF | Equity/Sector-Financials | 1998-12-22 | 2026-06-12 | 6910 | 0 | False | 0 | 0.1667 | 2008-12-01 | 0 |  |
| XLK | Equity/Sector-Technology | 1998-12-22 | 2026-06-12 | 6910 | 0 | False | 0 | 0.161 | 2001-01-03 | 0 |  |
| XLV | Equity/Sector-Healthcare | 1998-12-22 | 2026-06-12 | 6910 | 0 | False | 0 | 0.1205 | 2008-10-13 | 0 |  |
| XLU | Equity/Sector-Utilities | 1998-12-22 | 2026-06-12 | 6910 | 0 | False | 0 | 0.1279 | 2020-03-17 | 0 |  |
| GDX | Equity/GoldMiners | 2006-05-22 | 2026-06-12 | 5047 | 0 | False | 0 | 0.2654 | 2008-11-21 | 0 |  |

> `internal_missing` = NaNs inside a ticker's own [start,end] span measured against the union trading calendar (i.e. days peers traded but this ETF did not).

**Suspected data errors to eyeball before use:**
- `CPER`: 2014-12-05(-33%->+50%); 2015-02-03(-29%->+46%) — big move offset by a big opposite move next day (round-trip = likely bad tick).

## 2. Common analysis period

Correlation is computed only where **all tickers overlap**:

- **2011-11-15 → 2026-06-12**
- **3664 common trading days** (~14.5 years)

The window is bounded by the youngest ETF(s): `CPER`.

## 3. Correlation matrix

Computed on **daily simple returns** (`pct_change`), method = pearson. Returns, not price levels, are used — price correlation is spuriously inflated by common trends.

- Full matrix: [`correlation_matrix.csv`](correlation_matrix.csv)
- Heatmap (clustered order): [`correlation_heatmap.png`](correlation_heatmap.png)

## 4. 'Fake diversification' — high-correlation pairs

### 4a. Strong / redundant — |r| ≥ 0.80  (12 pairs)

| asset_a | asset_b | corr | factor_a | factor_b |
| --- | --- | --- | --- | --- |
| QQQ | XLK | 0.9708 | Equity/US-Nasdaq100 | Equity/Sector-Technology |
| UUP | FXE | -0.9446 | FX/USD-Bull | FX/EUR |
| SPY | QQQ | 0.9312 | Equity/US-LargeCap | Equity/US-Nasdaq100 |
| SPY | XLK | 0.9213 | Equity/US-LargeCap | Equity/Sector-Technology |
| TLT | IEF | 0.9163 | Bond/US-Treasury-Long | Bond/US-Treasury-Interm |
| SPY | IWM | 0.87 | Equity/US-LargeCap | Equity/US-SmallCap |
| SPY | XLF | 0.8503 | Equity/US-LargeCap | Equity/Sector-Financials |
| SPY | EFA | 0.8463 | Equity/US-LargeCap | Equity/DevelopedExUS |
| EFA | EWJ | 0.8399 | Equity/DevelopedExUS | Equity/Japan |
| EFA | EEM | 0.834 | Equity/DevelopedExUS | Equity/EmergingMkts |
| EFA | RWX | 0.8246 | Equity/DevelopedExUS | RealEstate/ExUS-REIT |
| IWM | XLF | 0.8193 | Equity/US-SmallCap | Equity/Sector-Financials |

### 4b. Moderate — 0.60 ≤ |r| < 0.80  (58 pairs)

| asset_a | asset_b | corr | factor_a | factor_b |
| --- | --- | --- | --- | --- |
| GLD | SLV | 0.793 | Commodity/Metal-Gold | Commodity/Metal-Silver |
| SPY | XLV | 0.7914 | Equity/US-LargeCap | Equity/Sector-Healthcare |
| IWM | EFA | 0.7863 | Equity/US-SmallCap | Equity/DevelopedExUS |
| QQQ | IWM | 0.7778 | Equity/US-Nasdaq100 | Equity/US-SmallCap |
| IEF | SHY | 0.7763 | Bond/US-Treasury-Interm | Bond/US-Treasury-Short |
| EFA | XLF | 0.7701 | Equity/DevelopedExUS | Equity/Sector-Financials |
| GLD | GDX | 0.7683 | Commodity/Metal-Gold | Equity/GoldMiners |
| IWM | XLK | 0.7603 | Equity/US-SmallCap | Equity/Sector-Technology |
| SPY | HYG | 0.7599 | Equity/US-LargeCap | Bond/US-HY-Credit |
| SPY | EEM | 0.753 | Equity/US-LargeCap | Equity/EmergingMkts |
| QQQ | EFA | 0.7524 | Equity/US-Nasdaq100 | Equity/DevelopedExUS |
| EFA | XLK | 0.7395 | Equity/DevelopedExUS | Equity/Sector-Technology |
| EFA | HYG | 0.7237 | Equity/DevelopedExUS | Bond/US-HY-Credit |
| EEM | RWX | 0.7218 | Equity/EmergingMkts | RealEstate/ExUS-REIT |
| IEF | LQD | 0.7211 | Bond/US-Treasury-Interm | Bond/US-IG-Credit |
| SPY | EWJ | 0.7198 | Equity/US-LargeCap | Equity/Japan |
| QQQ | EEM | 0.7166 | Equity/US-Nasdaq100 | Equity/EmergingMkts |
| IWM | HYG | 0.7148 | Equity/US-SmallCap | Bond/US-HY-Credit |
| SPY | VNQ | 0.7148 | Equity/US-LargeCap | RealEstate/US-REIT |
| IWM | VNQ | 0.7071 | Equity/US-SmallCap | RealEstate/US-REIT |
| EEM | XLK | 0.7054 | Equity/EmergingMkts | Equity/Sector-Technology |
| VNQ | XLU | 0.7042 | RealEstate/US-REIT | Equity/Sector-Utilities |
| IWM | EEM | 0.6953 | Equity/US-SmallCap | Equity/EmergingMkts |
| TLT | LQD | 0.6948 | Bond/US-Treasury-Long | Bond/US-IG-Credit |
| EEM | EWJ | 0.6914 | Equity/EmergingMkts | Equity/Japan |
| SLV | GDX | 0.6872 | Commodity/Metal-Silver | Equity/GoldMiners |
| QQQ | XLV | 0.6863 | Equity/US-Nasdaq100 | Equity/Sector-Healthcare |
| EWJ | RWX | 0.6846 | Equity/Japan | RealEstate/ExUS-REIT |
| EFA | XLV | 0.6816 | Equity/DevelopedExUS | Equity/Sector-Healthcare |
| XLF | XLV | 0.6816 | Equity/Sector-Financials | Equity/Sector-Healthcare |
| VNQ | RWX | 0.681 | RealEstate/US-REIT | RealEstate/ExUS-REIT |
| SPY | RWX | 0.678 | Equity/US-LargeCap | RealEstate/ExUS-REIT |
| HYG | VNQ | 0.6748 | Bond/US-HY-Credit | RealEstate/US-REIT |
| QQQ | HYG | 0.6747 | Equity/US-Nasdaq100 | Bond/US-HY-Credit |
| IWM | XLV | 0.6738 | Equity/US-SmallCap | Equity/Sector-Healthcare |
| QQQ | XLF | 0.6724 | Equity/US-Nasdaq100 | Equity/Sector-Financials |
| HYG | XLF | 0.6702 | Bond/US-HY-Credit | Equity/Sector-Financials |
| XLF | XLK | 0.6688 | Equity/Sector-Financials | Equity/Sector-Technology |
| IWM | EWJ | 0.6678 | Equity/US-SmallCap | Equity/Japan |
| XLE | XLF | 0.6668 | Equity/Sector-Energy | Equity/Sector-Financials |
| VNQ | XLF | 0.6632 | RealEstate/US-REIT | Equity/Sector-Financials |
| HYG | XLK | 0.6627 | Bond/US-HY-Credit | Equity/Sector-Technology |
| IWM | RWX | 0.6624 | Equity/US-SmallCap | RealEstate/ExUS-REIT |
| HYG | RWX | 0.6622 | Bond/US-HY-Credit | RealEstate/ExUS-REIT |
| QQQ | EWJ | 0.6577 | Equity/US-Nasdaq100 | Equity/Japan |
| EFA | VNQ | 0.6514 | Equity/DevelopedExUS | RealEstate/US-REIT |
| EWJ | XLK | 0.6455 | Equity/Japan | Equity/Sector-Technology |
| EEM | HYG | 0.6449 | Equity/EmergingMkts | Bond/US-HY-Credit |
| XLK | XLV | 0.6435 | Equity/Sector-Technology | Equity/Sector-Healthcare |
| IWM | XLE | 0.6366 | Equity/US-SmallCap | Equity/Sector-Energy |
| WEAT | CORN | 0.6365 | Commodity/Agri-Wheat | Commodity/Agri-Corn |
| EEM | XLF | 0.6331 | Equity/EmergingMkts | Equity/Sector-Financials |
| EWJ | XLF | 0.6325 | Equity/Japan | Equity/Sector-Financials |
| VNQ | XLV | 0.6254 | RealEstate/US-REIT | Equity/Sector-Healthcare |
| SPY | XLE | 0.6229 | Equity/US-LargeCap | Equity/Sector-Energy |
| USO | XLE | 0.6226 | Commodity/Energy-Oil | Equity/Sector-Energy |
| RWX | XLF | 0.6187 | RealEstate/ExUS-REIT | Equity/Sector-Financials |
| HYG | XLV | 0.6014 | Bond/US-HY-Credit | Equity/Sector-Healthcare |

> Bands use **|r|** so inverse pairs (negative correlation) count as redundant.

## 5. Hierarchical clustering — effective independent factors

Average linkage on distance `d = 1 - corr`. Dendrogram: [`dendrogram.png`](dendrogram.png). Cluster assignments: [`clusters.csv`](clusters.csv).

**Number of clusters when the tree is cut at each co-movement tolerance:**

| cut @ correlation | distance | # clusters (≈ independent groups) |
| --- | --- | --- |
| 0.80 | 0.20 | 25 |
| 0.60 | 0.40 | 12 |
| 0.40 | 0.60 | 9 |

**Read:** at a corr≈0.60 tolerance the 30 ETFs collapse into **~12 effective groups** — that is the honest count of independent risk bets this universe actually offers, far fewer than 30.

## 6. Screening suggestion (for your confirmation)

Greedy correlation filter: assets are processed in keep-priority order and an asset is dropped only if |r| ≥ 0.80 with an asset **already kept** (pairwise, not transitive — so distinct regional equities are not chained together).

- **Suggested KEEP (23)**: `SPY`, `EEM`, `EWJ`, `TLT`, `SHY`, `LQD`, `HYG`, `USO`, `UNG`, `XLE`, `GLD`, `SLV`, `CPER`, `DBA`, `WEAT`, `CORN`, `UUP`, `FXY`, `VNQ`, `RWX`, `XLV`, `XLU`, `GDX`
- **Suggested DROP candidates (7)**: `QQQ`, `IWM`, `EFA`, `IEF`, `FXE`, `XLF`, `XLK`

| ticker | factor | decision | nearest_kept | corr_with_kept | reason |
| --- | --- | --- | --- | --- | --- |
| SPY | Equity/US-LargeCap | KEEP |  |  | anchor — first asset processed for its factor |
| QQQ | Equity/US-Nasdaq100 | DROP (candidate) | SPY | 0.931 | \|corr\|=0.93 with kept SPY (Equity/US-LargeCap) — factor already represented |
| IWM | Equity/US-SmallCap | DROP (candidate) | SPY | 0.87 | \|corr\|=0.87 with kept SPY (Equity/US-LargeCap) — factor already represented |
| EFA | Equity/DevelopedExUS | DROP (candidate) | SPY | 0.846 | \|corr\|=0.85 with kept SPY (Equity/US-LargeCap) — factor already represented |
| EEM | Equity/EmergingMkts | KEEP | SPY | 0.753 | kept, but borderline: \|corr\|=0.75 with SPY (<0.80) — optional further-trim candidate |
| EWJ | Equity/Japan | KEEP | SPY | 0.72 | kept, but borderline: \|corr\|=0.72 with SPY (<0.80) — optional further-trim candidate |
| TLT | Bond/US-Treasury-Long | KEEP | SPY | -0.217 | distinct: nearest kept asset SPY only \|corr\|=0.22 |
| IEF | Bond/US-Treasury-Interm | DROP (candidate) | TLT | 0.916 | \|corr\|=0.92 with kept TLT (Bond/US-Treasury-Long) — factor already represented |
| SHY | Bond/US-Treasury-Short | KEEP | TLT | 0.575 | distinct: nearest kept asset TLT only \|corr\|=0.57 |
| LQD | Bond/US-IG-Credit | KEEP | TLT | 0.695 | distinct: nearest kept asset TLT only \|corr\|=0.69 |
| HYG | Bond/US-HY-Credit | KEEP | SPY | 0.76 | kept, but borderline: \|corr\|=0.76 with SPY (<0.80) — optional further-trim candidate |
| USO | Commodity/Energy-Oil | KEEP | SPY | 0.282 | distinct: nearest kept asset SPY only \|corr\|=0.28 |
| UNG | Commodity/Energy-NatGas | KEEP | USO | 0.127 | distinct: nearest kept asset USO only \|corr\|=0.13 |
| XLE | Equity/Sector-Energy | KEEP | SPY | 0.623 | distinct: nearest kept asset SPY only \|corr\|=0.62 |
| GLD | Commodity/Metal-Gold | KEEP | TLT | 0.222 | distinct: nearest kept asset TLT only \|corr\|=0.22 |
| SLV | Commodity/Metal-Silver | KEEP | GLD | 0.793 | kept, but borderline: \|corr\|=0.79 with GLD (<0.80) — optional further-trim candidate |
| CPER | Commodity/Metal-Copper | KEEP | EEM | 0.325 | distinct: nearest kept asset EEM only \|corr\|=0.33 |
| DBA | Commodity/Agri-Broad | KEEP | USO | 0.259 | distinct: nearest kept asset USO only \|corr\|=0.26 |
| WEAT | Commodity/Agri-Wheat | KEEP | DBA | 0.554 | distinct: nearest kept asset DBA only \|corr\|=0.55 |
| CORN | Commodity/Agri-Corn | KEEP | WEAT | 0.637 | distinct: nearest kept asset WEAT only \|corr\|=0.64 |
| UUP | FX/USD-Bull | KEEP | GLD | -0.432 | distinct: nearest kept asset GLD only \|corr\|=0.43 |
| FXE | FX/EUR | DROP (candidate) | UUP | -0.945 | \|corr\|=0.94 with kept UUP (FX/USD-Bull) — factor already represented |
| FXY | FX/JPY | KEEP | UUP | -0.552 | distinct: nearest kept asset UUP only \|corr\|=0.55 |
| VNQ | RealEstate/US-REIT | KEEP | SPY | 0.715 | kept, but borderline: \|corr\|=0.71 with SPY (<0.80) — optional further-trim candidate |
| RWX | RealEstate/ExUS-REIT | KEEP | EEM | 0.722 | kept, but borderline: \|corr\|=0.72 with EEM (<0.80) — optional further-trim candidate |
| XLF | Equity/Sector-Financials | DROP (candidate) | SPY | 0.85 | \|corr\|=0.85 with kept SPY (Equity/US-LargeCap) — factor already represented |
| XLK | Equity/Sector-Technology | DROP (candidate) | SPY | 0.921 | \|corr\|=0.92 with kept SPY (Equity/US-LargeCap) — factor already represented |
| XLV | Equity/Sector-Healthcare | KEEP | SPY | 0.791 | kept, but borderline: \|corr\|=0.79 with SPY (<0.80) — optional further-trim candidate |
| XLU | Equity/Sector-Utilities | KEEP | VNQ | 0.704 | kept, but borderline: \|corr\|=0.70 with VNQ (<0.80) — optional further-trim candidate |
| GDX | Equity/GoldMiners | KEEP | GLD | 0.768 | kept, but borderline: \|corr\|=0.77 with GLD (<0.80) — optional further-trim candidate |

### 6a. Optional further trim → ~20 (borderline keeps, 0.70 ≤ |r| < 0.80)

These survive the 0.80 filter but still co-move strongly with a kept anchor. A tighter, more-independent universe could drop the ones that are not the sole representative of their factor:

| ticker | factor | closest kept | corr |
| --- | --- | --- | --- |
| `SLV` | Commodity/Metal-Silver | `GLD` | +0.79 |
| `XLV` | Equity/Sector-Healthcare | `SPY` | +0.79 |
| `GDX` | Equity/GoldMiners | `GLD` | +0.77 |
| `HYG` | Bond/US-HY-Credit | `SPY` | +0.76 |
| `EEM` | Equity/EmergingMkts | `SPY` | +0.75 |
| `RWX` | RealEstate/ExUS-REIT | `EEM` | +0.72 |
| `EWJ` | Equity/Japan | `SPY` | +0.72 |
| `VNQ` | RealEstate/US-REIT | `SPY` | +0.71 |
| `XLU` | Equity/Sector-Utilities | `VNQ` | +0.70 |

### Factor coverage of the suggested-keep set

- **Bond**: `TLT`, `SHY`, `LQD`, `HYG`
- **Commodity**: `USO`, `UNG`, `GLD`, `SLV`, `CPER`, `DBA`, `WEAT`, `CORN`
- **Equity**: `SPY`, `EEM`, `EWJ`, `XLE`, `XLV`, `XLU`, `GDX`
- **FX**: `UUP`, `FXY`
- **RealEstate**: `VNQ`, `RWX`

> These are suggestions. No data or asset has been removed. Confirm the keep/drop list before step 2 (momentum signal construction).
