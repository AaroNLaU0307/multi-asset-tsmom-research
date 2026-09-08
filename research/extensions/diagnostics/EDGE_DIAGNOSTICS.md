# EDGE_DIAGNOSTICS.md — X07 · X45 · X46

**Program:** TSMOM extension (`TSMOM-EXT-001`) · **Wave:** 1 · **Lane:** MEASUREMENT
**Created:** 2026-09-07 (Wave-1 execution under Aaron's
`AUTHORIZE_WAVE_1_RESEARCH_EXECUTION_WITH_GATES`)
**Producer:** `research/extensions/diagnostics/run_edge_diagnostics.py`
**Machine-readable output:** `research/extensions/diagnostics/edge_diagnostics.json`
**Definitions:** `TSMOM_EXTENSION_RESEARCH_MAP_v2.md` Cluster C2 (X07), C14 (X45, X46)

---

## §0 What these are, and what they are not

These are **diagnostics of the frozen, already-burned baseline**. They are not
candidate tests, not premise tests, and not evidence for or against any
extension hypothesis.

- **No parameter was tuned. No candidate was selected. No baseline change is
  proposed.** MAP_v2's anti-snooping rule for X07 is binding: no ETF is removed
  from the baseline on the strength of anything below.
- **Evidence context T0** — the exposed design sample. Every number here is a
  new statistic of streams that were already target-metric exposures. Nothing
  here is independent confirmation of anything, and nothing here may be
  presented as out-of-sample.
- **Result-state vocabulary does not apply.** These findings carry no
  `confirmed` / `supported` / `not_promoted` / `falsified` status, because they
  adjudicate no hypothesis. MAP_v2 §D classes them as "Findings only; no
  promotion vocabulary applies".
- **Exposure class:** `TARGET_PERFORMANCE_EXPOSURE` (new decompositions of
  burned streams) **+** `DESIGN_INFORMING_MEASUREMENT`. Logged as
  `ops/EXPOSURE_LEDGER.md` row 14.

**Window:** 2008-05-31 → 2026-06-30, **218 months**.

**Terminal-month caveat, binding.** The ETF snapshot ends **2026-06-12**, so the
final monthly row is labelled `2026-06-30` while covering only 2026-06-01 →
2026-06-12 (`LOCKBOX_PROCEDURE.md` §2.1). It is one row of 218 and is not
separately excluded here; **any later evaluation that is sensitive to the
terminal month must truncate it or declare its inclusion**.

---

## §1 Reconciliation to the canonical baseline — PASS

Two independent reconciliations were required before any statistic below could
be trusted.

| Check | Result |
|---|---|
| Published per-asset net (`dd_per_asset_net.csv`) sums to published portfolio net | max abs residual **5.0e-07** over 218 months |
| Independent reconstruction (positions × monthly asset returns) vs published **gross** | corr **0.99999998**, max abs diff **1.93e-05** |
| Same reconstruction vs published **net** | corr **0.99999998**, max abs diff **2.02e-05** |
| Reconstructed per-asset `net_i` vs published `dd_per_asset_net.csv` | max abs diff **2.41e-05** |

Published CSVs are rounded to 6 dp, so residuals at the 1e-05 scale are rounding,
not disagreement. **Verdict: RECONCILED.**

**A real error was found and corrected by this gate, and is recorded rather than
quietly fixed.** The first reconstruction paired each month's decision weights
with the *same* month's asset returns and did **not** reconcile (corr 0.44, mean
abs difference 3.7% per month). The engine's convention is
`positions_t = decision_weights_{t-1}` (`src/attribution.py::decompose`,
`src/portfolio.py::positions_from_weights`). The X45 static-book numbers computed
on the unreconciled basis were discarded; everything in §3 below is on the
reconciled basis. **A decomposition that does not reconcile to the stream it
claims to decompose is not a finding, and was not reported as one.**

---

## §2 X07 — Effective breadth of the current 17-asset book

**Question (MAP_v2):** the "≈12 clusters at 0.60" figure is on *returns*;
trend-**PnL** correlation is what determines portfolio breadth.

### Effective number of bets

| Measure | Value | of |
|---|---|---|
| ENB, PCA participation ratio | **11.17** | 17 assets |
| ENB, eigenvalue-entropy | **13.53** | 17 assets |
| ENB of the 5 sleeve streams (participation ratio) | **3.99** | 5 sleeves |

Two ENB families are reported because they answer slightly different questions
and neither is canonical on its own; they bracket the honest answer at roughly
**11–13.5 effective bets out of 17**. The book is neither near-independent (17)
nor narrow.

### Dependence structure

| Statistic | Value |
|---|---|
| Mean absolute off-diagonal trend-PnL correlation | **0.134** |
| Maximum | **0.587** (XLE ↔ USO) |
| Minimum | **−0.186** |

**Most dependent pairs:** XLE↔USO 0.587 · SPY↔EWJ 0.538 · VNQ↔RWX 0.528 ·
SPY↔HYG 0.493 · TLT↔LQD 0.422 · EEM↔RWX 0.408 · EEM↔HYG 0.368 · XLU↔VNQ 0.367 ·
SHY↔LQD 0.350 · EEM↔EWJ 0.343.

### Sleeve-level trend-PnL correlation

| | Equity | Bond | Commodity | FX | RealEstate |
|---|---|---|---|---|---|
| **Equity** | 1.000 | 0.322 | 0.251 | 0.069 | 0.461 |
| **Bond** | 0.322 | 1.000 | 0.035 | 0.132 | 0.395 |
| **Commodity** | 0.251 | 0.035 | 1.000 | 0.257 | 0.013 |
| **FX** | 0.069 | 0.132 | 0.257 | 1.000 | 0.079 |
| **RealEstate** | 0.461 | 0.395 | 0.013 | 0.079 | 1.000 |

### The named overlaps MAP_v2 asked for

| Overlap | Trend-PnL correlation |
|---|---|
| RealEstate ↔ Equity (sleeve level) | **0.461** |
| VNQ ↔ SPY | 0.282 |
| RWX ↔ SPY | 0.233 |
| VNQ ↔ RWX | 0.528 |
| FX ↔ Equity (sleeve level) | 0.069 |
| UUP ↔ FXY | 0.321 |

**Reading.** MAP_v2 offered "RealEstate trend PnL corr with Equity ≥ 0.8" as an
*illustrative* finding shape. The measured sleeve-level value is **0.461** — the
REIT sleeve is meaningfully but not redundantly dependent on Equity, and the
illustrative 0.8 is **not** observed. Commodity and FX are the most independent
sleeves (Commodity↔Bond 0.035, Commodity↔RealEstate 0.013, FX↔Equity 0.069).

**Use, and only this use.** These numbers replace designer priors in MAP_v2
Section E **for candidates that modify this same stream, and for sleeve overlap
only**. They cannot measure the dependence of candidate streams that do not yet
exist (X06, X09, X11 legs, X43); those are measured when those streams are built.
The commodity/FX independence is a **design input for the new futures universe**,
where REITs do not exist anyway — it is not a reason to touch the ETF baseline.

---

## §3 X45 — Hidden beta / static-premium decomposition

### 3.1 Average net exposure

| Sleeve | Average net exposure |
|---|---|
| Bond | **+0.568** |
| Equity | **+0.278** |
| RealEstate | +0.091 |
| Commodity | −0.003 |
| FX | −0.002 |
| **Total net** | **+0.932** |
| **Average gross** | **2.028** |

Months net long, by asset: SPY 74.3% · SHY 72.9% · HYG 71.1% · XLU 70.6% ·
LQD 61.5% · VNQ 59.2% · EWJ 56.4% · RWX 52.3% · EEM 51.8% · XLE 51.8% ·
GLD 51.4% · UUP 49.1% · TLT 44.0% · USO 40.4% · DBA 35.8% · FXY 32.1% · UNG 18.3%.

The book's *average* posture over 2008–2026 is structurally long, concentrated in
bonds and credit — consistent with MAP_v2's stated suspicion.

### 3.2 Factor regression (published net returns, HAC)

n = 218, HAC maxlags = 4 (Newey–West plug-in), **R² = 0.0096**.

| Term | Coefficient | HAC t | HAC p |
|---|---|---|---|
| const | **+0.00667** | **+3.40** | **0.0007** |
| SPY | −0.03111 | −0.51 | 0.611 |
| TLT | +0.06191 | +0.87 | 0.383 |
| UUP | −0.03310 | −0.28 | 0.778 |
| COMMOD | +0.01244 | +0.26 | 0.795 |

**At monthly frequency the published net stream carries essentially no linear
loading on SPY, TLT, UUP or a commodity basket** (R² ≈ 1%). Intercept +0.67%/month
(≈ 8%/yr) with t = 3.40. This is a full-sample in-sample description on the burned
panel; it is **not** an alpha claim.

### 3.3 Static-book control — the substantive finding

Positions decomposed as `position_t = p̄ + (position_t − p̄)`, where `p̄` is the
full-sample mean position. Gross basis, so the split is exact
(identity residual **0.0**).

| Component | Annualised Sharpe |
|---|---|
| Full book (reconstructed, gross) | **0.783** |
| **Static average-position book** | **0.776** |
| **Residual (timing) book** | **0.153** |
| Residual retention of full Sharpe | **19.5%** |

| Structure | Value |
|---|---|
| corr(full, static) | −0.014 |
| corr(full, residual) | +0.799 |
| Variance share, static | 0.578 |
| Variance share, residual | 1.600 |

**Reading, carefully.** On this sample the constant average-position book —
long bonds and credit (SHY +0.225, HYG +0.188, LQD +0.138), long equity
(SPY +0.104) — achieves **almost the whole Sharpe of the full time-varying
book**, while the timing residual retains only **19.5%** of it. The variance
shares summing above 1 means static and residual are strongly *negatively*
correlated: the timing component reduces variance more than it adds return.

MAP_v2's reading rule proposed "a large drop in residual Sharpe … (the v1 figure
of 50% is a designer proposal) indicates a material static component". At 19.5%
the drop is well beyond that proposal. **The 50% figure is a designer proposal,
not a decided bar, and is not adopted here.**

**Four limits on this finding, all binding.**

1. **`p̄` is computed with full-sample knowledge.** The static book is **not an
   ex-ante deployable strategy**; nobody could have known the 2008–2026 average
   position in 2008. This is a retrospective description of a burned sample.
2. **Gross of costs.** The static book bears no rebalancing turnover here, while
   the full book's mean monthly turnover is **1.458**. The static Sharpe is
   therefore an upper bound relative to a cost-bearing comparison.
3. **Sample-period contingent.** 2008–2026 contained strong, sustained bond and
   equity trends; a structurally long book is flattered by that history.
4. **It is not a test.** Nothing here says the TSMOM timing rule is worthless, or
   that a static book should be deployed. It says the burned sample's Sharpe is
   largely reproducible by a constant book computed in hindsight.

**Use.** Calibrates MAP_v2 Section E priors and X28. It raises — and does **not**
answer — the question of how much of the baseline's historical Sharpe is a static
premium. Answering it needs an ex-ante-constructed static control, which is a
candidate design question for A2, not something to settle here.

---

## §4 X46 — Convexity profile and crisis-alpha attribution

### 4.1 The "smile" — not detected

Quadratic fit of published net on SPY monthly return, HAC maxlags 4, n = 218,
**R² = 0.0012**.

| Term | Coefficient | HAC t | HAC p |
|---|---|---|---|
| const | +0.00670 | +3.07 | 0.0021 |
| SPY | −0.02252 | −0.37 | 0.712 |
| SPY² | **−0.02105** | **−0.03** | **0.979** |

**No convexity is detected at monthly frequency on the full sample.** The
quadratic term is indistinguishable from zero (p = 0.98) and its point estimate
is *negative*, i.e. the opposite sign to a smile.

**This is a negative diagnostic result and it is recorded as one.** It does not
falsify anything — MAP_v2 forbids that reading, no margin was declared in
advance, and a monthly full-sample quadratic is a weak instrument for
crisis-window convexity. What it does is remove "the smile is visible in the
unconditional monthly fit" from the set of things this program may assume.

### 4.2 Long/short attribution

Per-asset published net PnL split by the sign of the **held** position (decision
weights shifted, matching the engine). Sum check vs per-asset total: **2.8e-17**.

| Component | Cumulative net PnL contribution |
|---|---|
| Long positions | **+1.340** |
| Short positions | **+0.072** |
| Flat / not held | −0.012 |

Over the whole sample the book's cumulative PnL is overwhelmingly **long-side**.

### 4.3 Crisis windows

| Window | Months | Long | Short | Total | Short share |
|---|---|---|---|---|---|
| GFC 2008-05 → 2009-03 | 11 | **−0.036** | **+0.115** | +0.078 | 1.47 |
| COVID 2020-01 → 2020-04 | 4 | **−0.072** | **+0.147** | +0.075 | 1.96 |
| CY2022 | 12 | +0.029 | **+0.121** | +0.150 | 0.81 |

**In all three crisis windows the short side carried the gains**, and in GFC and
COVID the long side *lost* money — which is why the short share exceeds 1 there.

**Reading.** MAP_v2 states explicitly that "all crisis alpha is short-side" is a
**hypothesis X24/X46 test, not a premise**. The attribution above is
**descriptively consistent** with it on all three windows. It remains an
attribution of a burned stream over three short, hand-named windows (11, 4 and 12
months), not a test with a declared margin, and it is not evidence that the
short side will carry future crisis behaviour.

### 4.4 Tail dependence

| Statistic | Value |
|---|---|
| SPY 10th-percentile monthly return | −0.0533 |
| Tail months | 22 |
| corr(TSMOM net, SPY), all months | **−0.034** |
| corr(TSMOM net, SPY), **in the SPY left tail** | **−0.516** |
| Mean TSMOM net in tail | **+0.86%** |
| Mean TSMOM net outside tail | +0.62% |

Unconditional correlation with equities is ≈ 0, but **within the equity left tail
the relationship is strongly negative (−0.516)**, and the mean return in tail
months is *higher* than outside. This is the shape a defensive overlay is
supposed to have, measured descriptively on the burned sample.

**Consequence for the program.** Combined with §4.1, the defensive character
appears in **tail conditioning**, not in an unconditional quadratic. Any later
candidate claiming to preserve crisis behaviour should therefore be judged on
declared event windows and tail conditioning — as Program v2 §0 rule 11 already
requires — and **not** on a full-sample convexity coefficient.

---

## §5 Trial and exposure accounting

| Object | Treatment |
|---|---|
| **EXPOSURE_EVENT** | **Yes** — one row (`ops/EXPOSURE_LEDGER.md` row 14), `REVEALED_TARGET_METRIC`, `CURRENT_REVIEW_SCOPE`, class `TARGET_PERFORMANCE_EXPOSURE` + `DESIGN_INFORMING_MEASUREMENT`, context T0. |
| **VARIANT_ATTEMPT** | **No.** No evaluated strategy configuration and no selection opportunity arose. The static-book and residual series of §3.3 are *decompositions* of the existing book, not candidate configurations, and MAP_v2's anti-snooping rule forbids selecting on them. |
| **HYPOTHESIS_FAMILY** | **None declared.** A family is declared in a preregistration before its first member runs; no preregistration exists. |
| **GOVERNED_N_TRIALS_CONTRIBUTION** | **`UNKNOWN_PENDING_AARON_DECISION`** (`D-ETF-COUNT`). The ETF panel has **no frozen counting convention**; under a carry-style "distinct constructed strategy-return series with selection" convention this would contribute 0, but that convention governs the Databento panel and does not govern here. **Fails closed: no count is asserted.** |

---

## §6 Status

`X07 = EXECUTED` · `X45 = EXECUTED` · `X46 = EXECUTED`

No promotion vocabulary is emitted, no candidate advanced, and no baseline change
proposed. `STRATEGY_BUILD_STARTED = NO`.

| Date (UTC) | Appended | By |
|---|---|---|
| 2026-09-07 | Created at Wave-1 execution. Reconciliation gate §1 (including the discarded unreconciled first attempt); X07 §2; X45 §3; X46 §4; accounting §5. | Wave-1 session (Claude Opus 5) |
