# Multi-Universe XSMOM — a pre-registered mechanism map

**Where does cross-sectional momentum (XSMOM) carry a real, mechanism-explicable edge on
liquid tradable ETFs — and where does it not, and *why*?** This is a **mechanism map, not
a strategy hunt.** Success is *not* "find a universe where XSMOM wins"; success is an
**FDR-controlled map** of where XSMOM survives, where it is falsified, and a **Lo–MacKinlay
decomposition** explaining each outcome. A clean, mechanism-explained negative across the
whole family is a fully successful result and is pre-accepted as such.

> Phase 2 of the XSMOM study. Builds on [`XSMOM_README.md`](XSMOM_README.md) (Phase 1) and
> reuses the TSMOM engine + the Phase-1 `src/xsmom.py` signal/construction layers
> **verbatim**. The only new logic is the universe loop, the family-level statistics
> (BH-FDR, Deflated Sharpe), and the mechanism decomposition.

---

## ⛔ PRE-REGISTRATION — sealed before any result was computed

*This section was written and committed **before** a single Sharpe number was produced. The
universe family, the a-priori arguments, the criteria and the multiple-comparison protocol
below are fixed. Nothing here may be revised in light of results — results are appended
afterwards under "THE MAP".*

### 0. Epistemic frame

This is a mechanism map. **Why it is not data-snooping:** (1) the universe family is **fixed
and sealed before any result is seen** (this document); (2) each universe is included on an
**a-priori homogeneity argument** written before running, not because its result looked
good; (3) the family of headline tests is corrected with **Benjamini–Hochberg FDR**; (4) the
single best universe is additionally checked with a **selection-adjusted Deflated Sharpe
Ratio**.

### 1. The universe family (SEALED — 5 universes)

Each universe is included because of a *theoretical homogeneity argument*: the assets share
a dominant common factor, so cross-sectional ranking nets that factor out and isolates
dispersion / lead-lag. The argument is stated **before** results.

| # | Universe | A-priori homogeneity argument | Prior | Candidate tickers |
|---|---|---|---|---|
| **U1** | **US equity sectors** | All large-cap US equity → share the US market factor → ranking nets out market beta → residual is **pure sector-rotation dispersion**. Removes the cross-asset static-premium confound of Phase 1. Textbook XSMOM domain (Moskowitz–Grinblatt 1999). | **Strong** | XLB XLE XLF XLI XLK XLP XLU XLV XLY |
| **U2** | **Country equity indices** | All single-country equity → share the global equity factor → ranking nets it out → residual is **country momentum** (Asness–Liew–Stevens 1997). Large N → terciles well-populated. | **Strong** | EWA EWC EWG EWH EWJ EWL EWP EWQ EWU EWW EWS EWY EWT EWZ EWI EWN EWM EWD |
| **U3** | **G10 FX vs USD** | All majors quoted vs USD → share the USD factor → ranking nets it out → residual is **currency cross-momentum**. Caveat: small N → thin legs; FX momentum is historically weak. | Weak | FXA FXB FXC FXE FXF FXY |
| **U4** | **Commodities (ETF)** | Loosely "all commodities", but gold / nat-gas / agriculture are **heterogeneous** (different supply-demand drivers). **Mandatory caveat:** commodity ETFs suffer roll/contango decay and are *not* clean proxies for the futures the literature uses — itself a confound, reported as such. | Weak / caveated | GLD SLV USO UNG DBA DBB DBO |
| **U5** | **Bonds — NEGATIVE CONTROL** | "All fixed income", but duration and credit are **different betas** → ranking sorts on duration/credit, i.e. on **static term/credit premia**, not dynamic momentum. Included to **validate the confound theory**: predicted to (a) look weakly positive on raw returns and (b) collapse hardest under demeaning. A predicted negative that tests our own framework. | **Predicted negative** | SHY IEF TLT LQD HYG TIP EMB |

**Family-sealing rules.** (a) These five are the entire family; no universe may be added
after seeing any result. (b) Each universe's **headline = 12-1 tercile only**; the 3/6/9/12
neighbourhood and rank-weight are robustness and are **not** in the FDR family. (c) Tickers
failing data-coverage verification are dropped with the drop **reported**; the homogeneity
argument and the inclusion decision do not change.

### 2. Locked design (inherited verbatim from Phase 1, applied identically to every universe)

- **Signal:** 12-1 momentum, explicit 21-day skip-month, `signal = P[t-21]/P[t-252] − 1`.
  No lookback tuning; 3/6/9/12 reported as robustness only.
- **Construction:** headline **tercile** (long top 1/3, short bottom 1/3); robustness
  **rank-weight**. **Dollar-neutral enforced** (`Σwₗₒₙ𝓰 = +1`, `Σwₛₕₒᵣₜ = −1`).
  **Equal-weight legs** (no intra-leg vol-tilt). Tercile fraction held constant across the
  family for comparability; at small N (U3) legs are thin — acknowledged, not optimised away.
- **Risk:** portfolio-layer ex-ante vol-target using the **engine's vol estimator verbatim**,
  for the equity-curve overlay and 50/50 combo only. Sharpe / correlation / all tests run on
  **natural-scale** returns (scale-invariant).
- **Rebalance:** monthly. **Common window:** the Phase-1 window (≈2008-05 → present,
  ~218 months) applied to **all** universes, so each spans 2008 + the 2009 momentum-crash +
  2020 with comparable T. Each universe's native max window is a secondary robustness table.

### 3. Pre-registered criteria & multiple-comparison protocol

**Per-universe headline test (vs 0):** is the natural-scale long-short Sharpe distinguishable
from zero?

- **Primary family control — BH-FDR across the 5 headline tests.** Compute each universe's
  bootstrap p-value for Sharpe-vs-0; apply Benjamini–Hochberg at the family level (α = 0.05).
  A universe is **CONFIRMED** iff, *after BH-FDR correction*, its CI excludes 0 **AND** its
  walk-forward OOS expectancy is positive **AND** its 3/6/9/12 neighbourhood is sign-consistent.
- **Secondary selection control — Deflated Sharpe Ratio.** On the single best universe, report
  the DSR (Bailey–López de Prado) deflating the observed Sharpe for the number of trials (5)
  and the return moments. Answers "the best of five — is it real after selection?"
- **FALSIFIED** if the BH-FDR-corrected CI includes 0 **or** walk-forward OOS is negative.
  Documented either way.

### 4. Mechanism decomposition (Lo–MacKinlay, per universe)

For every universe, estimate the three terms on common-window monthly returns (Γ₁ = lag-1
cross-autocovariance matrix, `(Γ₁)ᵢⱼ = Cov(rᵢ,ₜ₋₁, rⱼ,ₜ)`):

- **term(1) own-autocorr:** `(N−1)/N² · tr(Γ₁)` — the source TSMOM also harvests.
- **term(2) lead-lag:** `(1/N²) Σ_{i≠j} (Γ₁)ᵢⱼ` — XSMOM-only; the term that must be non-trivial
  for XSMOM to beat TSMOM.
- **term(3) dispersion:** `σ²_μ` — cross-sectional variance of sample mean returns
  (static-premium suspect).

**Mandatory honesty caveat.** Γ₁ has N(N−1) off-diagonal entries estimated from ~218 months;
at large N (U2 ≈ 18) term(2) is **estimated with wide uncertainty**. Each term is reported as a
point estimate **with block-bootstrap CIs**, and term(2) is interpreted **qualitatively**
(sign and rough magnitude), not as a precise value. term(3) is cross-validated against the
demean robustness test: large term(3) **and** Sharpe collapse under demeaning ⟹ the dispersion
contribution was static premium. Decomposition and demean test are two independent angles on
the same mechanism.

**Pre-registered mechanism hypothesis:** XSMOM carries a genuine (non-static) edge in a
universe iff term(2) is non-trivial **and** term(3) survives demeaning. Expectation per theory:
U1/U2 are where term(2) has the best chance of being non-trivial; U5 is predicted to be
dominated by a static term(3) that collapses under demeaning.

### 5. Pre-committed interpretation grid (every outcome pre-accepted)

- **Survives BH-FDR + OOS + neighbourhood + non-static decomposition** → a real,
  mechanism-explained XSMOM edge on tradable ETFs. Report Sharpe, corr vs TSMOM-on-same-universe,
  combo gain.
- **Falsified** → reported as-is, with the decomposition explaining *why* (e.g. term(2)≈0 →
  XSMOM is a market-neutral, weaker echo of the same trend engine TSMOM already harvests).
- **Whole map negative** → the authoritative conclusion: *at liquid-ETF granularity, XSMOM's
  edge is marginal / arbitraged even inside its theoretical domain.* Stronger and more citable
  than "it failed in the wrong universe."
- **corr vs TSMOM & combo (per universe):** low corr + comparable strength → diversification
  (combo > best leg); high corr or weak XSMOM leg → dilution (combo < TSMOM) — both honest. The
  diversification break-even ρ is reported so "no payoff" is shown to follow from the shared
  term(1), not from arbitrary thresholds.
- **Cross-universe XSMOM correlation matrix** reported for completeness (are sector- and
  country-XSMOM the same bet?).

### 6. Known limitations, declared up front

- **No single stocks via yfinance.** The most canonical XSMOM domain is index-constituent
  single stocks, but yfinance provides only *current* constituents → survivorship bias →
  inflated momentum, violating this project's honesty standard. Single-stock XSMOM is deferred
  to a future project *with point-in-time constituent data*; **out of scope here**, stated not
  hidden.
- **Commodity ETF roll/contango** (U4) distorts returns vs the futures the literature uses;
  reported as a confound.
- **Thin legs at small N** (U3, and U4/U5 at N≈7): tercile legs of 2–3 names are noisy;
  acknowledged as a structural limit of tradable-ETF universes, not corrected by re-choosing
  fractions.
- **Sample length:** ~218 months → Sharpe CIs are wide (~±0.45); powered to detect only
  sizable edges. A negative-dominated map is the expected outcome and an informative result,
  not a failure.

---

## THE MAP — results (appended after the pre-registration above was sealed)

*Run 2026-06-22. Full per-universe tables, the mechanism map and the Methods note: [`XSMOM_UNIVERSES_REPORT.md`](XSMOM_UNIVERSES_REPORT.md).*

**CONFIRMED universes: 0 / 5.** Best = U4 (Commodities (ETF)), net Sharpe 0.42; selection-adjusted **Deflated Sharpe = 0.779** (5 trials, SR\*=0.070/mo) → not significant after selection.

| universe | N | net Sharpe | 95% CI | p | q(BH) | WF OOS | 3·6·9·12 | confirmed? | corr vs TSMOM | combo vs best leg | cost ceil |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **U1** US equity sectors | 9 | +0.09 | [-0.37, +0.56] | 0.697 | 0.988 | 4/5✓ | ✗ | ❌ | +0.12 | 0.41 vs 0.34 | 15bp |
| **U2** Country equity indices | 18 | -0.12 | [-0.58, +0.35] | 0.614 | 0.988 | 3/5✗ | ✓ | ❌ | +0.14 | 0.03 vs 0.11 | 0bp |
| **U3** G10 FX vs USD | 6 | +0.04 | [-0.43, +0.50] | 0.878 | 0.988 | 3/5✓ | ✗ | ❌ | +0.23 | -0.00 vs 0.07 | 5bp |
| **U4** Commodities (ETF) | 7 | +0.42 | [-0.04, +0.88] | 0.071 | 0.357 | 4/5✓ | ✓ | ❌ | +0.31 | 0.56 vs 0.46 | 150bp |
| **U5** Bonds (NEGATIVE CONTROL) | 6 | +0.01 | [-0.44, +0.46] | 0.988 | 0.988 | 3/5✓ | ✓ | ❌ | +0.25 | 0.52 vs 0.64 | 3bp |

![map](xsmom_universes_map.png)

**Authoritative conclusion (pre-accepted in §5):** across the entire sealed family, *no* universe survives the BH-FDR-corrected headline test together with walk-forward and neighbourhood consistency. **At liquid-ETF granularity, XSMOM's edge is marginal / arbitraged even inside its theoretical domain.**

**Failed-to-reject, not proven-absent (honest scope).** The Sharpe map is a *failed-to-reject* at limited power (N as small as 6; ~218 months; Sharpe CIs ≈ ±0.45) — we do **not** claim the edge is *proven* zero. The **power-independent** leg is the mechanism: for XSMOM to beat TSMOM the lead-lag term (term2) had to be non-trivial, yet in **5/5** universes term2's block-bootstrap CI contains 0. term2 is *imprecisely* estimated (its CI admits magnitudes ≥ |term1| in every universe; widest at N=18), so we state **"term2 not shown to be non-trivial"** — not "term2 ≈ 0". The only reliably-present term is term1 (own-autocorrelation), which TSMOM already harvests; on the combined weight of the all-negative map, the demean collapse and the undemonstrated lead-lag, XSMOM behaves as a market-neutral echo of the same source.

*Per-universe detail, the Lo-MacKinlay mechanism map (term1/2/3 with CIs + the C1 precision fork), crisis tables, confound controls, the Methods & honest-scope note and the cross-universe correlation matrix are in the full report.*
