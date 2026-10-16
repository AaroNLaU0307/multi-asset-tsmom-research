# Final Universe Confirmation — Window & Diversification Check

*Generated: 2026-09-29 01:13*  
*Scope: universe finalization + data-window re-confirmation + diversification verification. No strategy / signal / backtest logic. Prices from cache (no re-fetch).*

## 1. Final universe (17 ETFs) — LOCKED

> Locked at **17** assets: the 30-ETF screening removed strong redundancies, then CPER, WEAT and CORN were dropped so the common window reaches the 2008 GFC (see §2). Authoritative definition in `universe.py`.

| ticker | factor label | inception |
| --- | --- | --- |
| SPY | Equity/US-LargeCap | 1993-01-29 |
| EEM | Equity/EmergingMkts | 2003-04-14 |
| EWJ | Equity/Japan | 1996-03-18 |
| XLE | Equity/Sector-Energy | 1998-12-22 |
| XLU | Equity/Sector-Utilities | 1998-12-22 |
| TLT | Bond/US-Treasury-Long | 2002-07-30 |
| SHY | Bond/US-Treasury-Short | 2002-07-30 |
| LQD | Bond/US-IG-Credit | 2002-07-30 |
| HYG | Bond/US-HY-Credit | 2007-04-11 |
| USO | Commodity/Energy-Oil | 2006-04-10 |
| UNG | Commodity/Energy-NatGas | 2007-04-18 |
| GLD | Commodity/Metal-Gold | 2004-11-18 |
| DBA | Commodity/Agri-Broad | 2007-01-05 |
| UUP | FX/USD-Bull | 2007-03-01 |
| FXY | FX/JPY | 2007-02-13 |
| VNQ | RealEstate/US-REIT | 2004-09-29 |
| RWX | RealEstate/ExUS-REIT | 2006-12-19 |

**Excluded (with reason, recorded in `universe.py`):**
- `QQQ` — 0.93 with SPY — US large-cap factor already represented by SPY
- `XLK` — 0.97 with QQQ / 0.92 with SPY — tech is a slice of US equity
- `IWM` — 0.87 with SPY — US small cap co-moves with the broad index
- `XLF` — 0.85 with SPY — financials sector is a slice of US equity
- `EFA` — 0.85 with SPY — developed-ex-US tracks US too closely for a separate bet
- `IEF` — 0.92 with TLT — duration factor covered by TLT (long) + SHY (short)
- `FXE` — -0.94 with UUP — euro is the inverse of the USD factor (UUP)
- `XLV` — 0.79 with SPY — healthcare is a US-equity slice, not an independent factor
- `GDX` — 0.77 with GLD — gold miners = gold + equity beta, not independent
- `SLV` — 0.79 with GLD — precious-metals factor covered by GLD
- `CPER` — 2011 inception caps the backtest start and loses 2008; copper partly proxied by equity/EEM; also bad-print spike-and-revert data errors
- `WEAT` — 2011-09 inception — blocked the 2008 sample; agriculture kept via DBA (DBA-WEAT only 0.55, but the window cost outweighed the diversification)
- `CORN` — 2010-06 inception — blocked the 2008 sample; agriculture kept via DBA (DBA-CORN only 0.60)

## 2. Common data window (final 17)

- **Window: 2007-04-18 → 2026-06-12**  (4820 common trading days, ~19.1 years)
- **Binding (latest-inception) asset: `UNG` (2007-04-18)**
- **Covers the 2008 GFC (Lehman, 2008-09-15)?** YES
- **Covers the 2020 COVID crash (peak 2020-02-19)?** YES

> The window is bound by **`UNG`** (2007-04-18) and spans **both** major stress regimes (2008 and 2020) — exactly the samples a momentum study needs.

### 2a. Why WEAT / CORN were dropped

| scenario | start | end | days | binding asset | covers 2008? |
| --- | --- | --- | --- | --- | --- |
| Final universe (17 assets, grains excluded) | 2007-04-18 | 2026-06-12 | 4820 | `UNG` (2007-04-18) | YES |
| + re-add WEAT, CORN (excluded) | 2011-09-19 | 2026-06-12 | 3705 | `WEAT` (2011-09-19) | no |

Re-adding the two single-grain ETFs would drag the binding inception to 2011 and **lose the entire 2008 GFC** — the reason they were excluded.

### 2b. Full peel — which assets blocked 2008

From the prior 19-asset set, repeatedly drop the latest-inception asset until the window reaches the GFC:

| # assets | start | binding | covers 2008? | next action |
| --- | --- | --- | --- | --- |
| 19 | 2011-09-19 | `WEAT` | no | drop `WEAT` |
| 18 | 2010-06-09 | `CORN` | no | drop `CORN` |
| 17 | 2007-04-18 | `UNG` | YES | — (reached 2008) |

> **Read:** dropping `WEAT` then `CORN` extends the start back to **2007-04-18** (then bound by `UNG`), which **does** include 2008 — confirming the grains were exactly what cost the GFC sample.

## 3. Agriculture internal correlation (DBA vs WEAT vs CORN)

Daily-return correlation on the three ETFs' mutual window:

|  | DBA | WEAT | CORN |
| --- | --- | --- | --- |
| DBA | 1.000 | 0.554 | 0.599 |
| WEAT | 0.554 | 1.000 | 0.635 |
| CORN | 0.599 | 0.635 | 1.000 |

- DBA–WEAT = **0.55**, DBA–CORN = **0.60**, WEAT–CORN = **0.64**
- **DBA does NOT make WEAT/CORN redundant** on a >0.70 basis — the broad basket only moderately tracks the single grains. On pure diversification grounds all three carry some distinct signal.

**Decision (locked):** the grains were only moderately distinct (no >0.70 overlap), so on diversification grounds little is lost; but they were the only assets blocking 2008. They were dropped, keeping `DBA` as the agriculture representative — extending the window to **2007-04-18** and capturing the GFC, the regime where time-series momentum is most tested.

## 4. Diversification of the final universe (17 assets)

- Correlation matrix: [`final_correlation_matrix.csv`](final_correlation_matrix.csv)  
- Heatmap: [`final_correlation_heatmap.png`](final_correlation_heatmap.png)  
- Dendrogram: [`final_dendrogram.png`](final_dendrogram.png)  
- Cluster assignments: [`final_clusters.csv`](final_clusters.csv)

### 4a. Remaining redundancy

- **|r| ≥ 0.80 pairs remaining: 1** (see below)
| a | b | corr |
| --- | --- | --- |
| SPY | EEM | 0.83 |
- Moderate (0.60 ≤ |r| < 0.80) pairs remaining: 17 (mostly the persistent risk-on equity/credit/REIT block).

### 4b. Effective independent factors (vs the 30-ETF set)

| cut @ correlation | 30-ETF set | final set | final / N |
| --- | --- | --- | --- |
| 0.80 | 25 | 16 | 94% |
| 0.60 | 12 | 12 | 71% |
| 0.40 | 9 | 7 | 41% |

**Verdict:** at the 0.80 cut the final universe splits into **16** groups out of 17 assets — redundancy at the strong threshold is essentially eliminated. At corr≥0.60 it is **12** groups (71% of assets, vs 12/30 = 40% before), i.e. the effective-factor *density* improved markedly even though the risk-on equity/credit/REIT complex remains one shared factor (as it should — that co-movement is real, not a data artifact).
