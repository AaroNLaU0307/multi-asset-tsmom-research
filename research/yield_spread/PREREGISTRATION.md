# Pre-registration — Yield-curve slope as a macro-regime conditioner on the multi-asset TSMOM

**Status: CONTRACT. Written BEFORE any slope×TSMOM statistic is computed.** Once signed off, this
family and these gates are fixed. No spread, horizon, state, or rule is added, dropped, or re-defined
mid-analysis to chase a result. A new idea that arises later is a *separate* future pre-registration,
not an amendment to this contract.

*Scope of "before any result":* the only things computed so far are **univariate characterizations of
the conditioning variable and the data** (coverage, the calendar-mismatch count, and the inversion /
flat-regime **episode structure** of the yield curve itself — §0/§3). None of these touches the
slope→forward-TSMOM relationship, which is the hypothesis under test and is untouched until sign-off.

---

## Why the extra discipline here: **EVENT SPARSITY, not statistical significance**

The three prior overlays in this arc were *price-based* (crash-defense, vol-breakout, seasonality) and
their overfitting risk was multiple-comparison / calendar-slicing. This signal is different and its
real trap is **event sparsity**: a yield-curve regime is one slow-moving macro variable, and curve
**inversions/flattenings are rare** — over 2007–2026 there is effectively a *handful* of distinct
episodes, even though there are 4,820 trading days. The days are **not** independent observations; the
independent unit is the **episode**. Concretely, from the supplied data (univariate, pre-result):

| Spread | Inverted (slope<0) days | Distinct merged episodes (bridge ≤10 td) | Share of inverted days in the single 2022–2024 episode |
|---|---|---|---|
| **10Y–3M** (primary) | 786 / 4,820 (16.3%) | ~10 (2007, 2019, 2020, **2022–24**, 2025) | **69%** (542 td) |
| **10Y–2Y** (robustness) | 564 / 4,820 (11.7%) | **4** (2007, 2019, 2022, **2022–24**) | **97%** (546 td) |

So a naive "inverted vs not" test is, for 10Y–2Y, essentially a **one-episode** test. The entire point
of the gates below is that **statistical significance computed over ~4,800 autocorrelated daily
observations is meaningless if it rests on one or two macro episodes.** Therefore: a deliberately
small pre-registered family, BH-FDR across it, **and** — the load-bearing hurdle — an **event-level
leave-one-episode-out** requirement, **and** an economic-magnitude bar, **and** an explicit
**contemporaneous-vs-predictive confound** test. Significance alone is explicitly **not** sufficient,
and a result resting on one episode is a **clean negative**.

---

## 0. Data, scope, and what stays descriptive

- **Yield data (external, user-supplied, gitignored `data/`):** FRED constant-maturity Treasury CSVs
  `DGS3MO`, `DGS2`, `DGS10` (`observation_date,<ID>`, daily, missing = `.`). Histories begin
  1981/1976/1962 → 2026-06-23, so the test window has decades of warmup. The pre-computed FRED spreads
  (`T10Y3M`/`T10Y2Y`) are **derived** here as `DGS10−DGS3MO` and `DGS10−DGS2` (in percentage points).
- **TSMOM return series:** the **confirmed Method-B portfolio's daily held-book return** — the same
  series the drawdown-attribution diagnostic uses (`portfolio.build_portfolio(px, method="B")` →
  `attribution.daily_strategy`, where the held weight is `port_weight.ffill().shift(1)`, i.e. the prior
  decision held forward — causal). **Gross** daily return is the premise series (costs are a Step-2
  concern; they are charged on the *overlay's* turnover, not the descriptive premise). No re-parameterization.
- **Sample:** the common all-17-present daily window **2007-04-18 → 2026-06-12 (4,820 trading days)**,
  identical to the monthly engine and the seasonality study.
- **Causal calendar alignment (verified):** the FRED (SIFMA) calendar differs from the ETF (NYSE)
  calendar on **36** window days (≈ Columbus/Veterans days, when ETFs trade but no yield prints).
  Yields are reindexed onto the **ETF trading-day index** and **forward-filled past-only** (carry the
  last *published* yield); this leaves **0** missing in-window and **cannot peek ahead** (on a
  no-print day the signal uses the prior business day's curve). This is the same `shift`/trailing
  discipline as `src/daily.py`.
- **Timing rule (no look-ahead):** the regime state that conditions day-*t* forward returns is the
  slope state **known as of the prior close, `t−1`** (`S_{t−1}`). This holds regardless of the
  intraday H.15 publication time. CMT yields are published same-day and are **not materially revised**
  (unlike GDP/payrolls), so `t−1` is a genuine point-in-time value.
- **Step 1 is descriptive only:** forward TSMOM returns conditioned on the curve regime. **No
  positions, no P&L, no overlay, no tuning.** P&L appears only in Step 2, and only if the premise is
  CONFIRMED here.

---

## 1. The fixed family (small, motivated, a-priori — NOT discovered from the data)

**Economic linkage (locked at Step 0, approved):** a single economy-wide **macro REGIME/STATE
conditioner on the WHOLE portfolio** — *not* a per-asset signal. The yield-curve slope is one number;
it is the canonical business-cycle / recession-risk proxy (Estrella–Mishkin; the NY-Fed model uses
10Y–3M) and is **orthogonal to the 17 ETF price paths** the core TSMOM already uses (term structure of
risk-free rates, not a function of those returns). Per-sleeve use is explicitly rejected — one macro
series is not a clean signal for nat-gas or the yen.

**The conditioning variable (causal `S_{t−1}`):** the slope's **causal trailing-percentile rank**
within a trailing **756-trading-day (~3y)** window (the existing `config.REGIME_VOL_PCTILE_WINDOW`,
via the verified-causal `regime._trailing_pctile`). The percentile (vs a raw `<0` cut) is chosen
because it is **rate-era robust** (a 0% slope means different things in a 1% vs a 5% world) and uses
the **full sample** — giving the signal its **most powerful fair shot** rather than rigging it to fail
on sparsity. The state is a **tercile contrast**: `flat` = bottom third (pr ≤ ⅓), `steep` = top third
(pr ≥ ⅔); the middle third is excluded from the contrast.

**Interpretation rule (locked — clarification 1).** The tercile primary tests the **continuous slope
state** — "relatively flat" vs "relatively steep" within the slope's own trailing-3y range — which is a
**different proposition** from a raw recession-signal **inversion** (`slope < 0`). Pinned now so it
cannot be glossed later: (i) any confirmed tercile-primary result is reported as a claim about the
**continuous slope state**, **never** as "yield-curve inversion predicts TSMOM"; (ii) if the tercile
primary confirms but the raw-`<0` inversion robustness view (§3a) does **not**, the verdict **must**
state that the effect comes from **flatness, not inversion** — a materially different economic meaning
that does not carry the recession-signal narrative.

**The fixed grid (the BH-FDR family):**

| Dimension | Levels | Count | Motivation |
|---|---|---|---|
| Spread | **10Y–3M** (primary), **10Y–2Y** (robustness) | 2 | The two canonical slope measures; both approved at Step 0. |
| Forward horizon | **21, 63, 126** trading days (≈ 1, 3, 6 months) | 3 | A business-cycle regime acts over *months*; fixed, not searched. |
| State | tercile **flat vs steep** (above) | 1 | One causal regime definition. |

⇒ **Family = 2 × 3 × 1 = 6 cells.** BH-FDR is applied across **all 6** (faithful to "count the full
family"). 10Y–3M is the headline spread; 10Y–2Y must be *consistent* (robustness) — but both are
counted in the multiplicity correction because both are tested.

### Direction of effect — two competing mechanisms, **two-sided** test (justified)

For trend-following specifically, the sign is **genuinely ambiguous a priori**, and I will not
manufacture a false directional prior:
- **H+ (crisis-alpha / divergent-trends):** flat/inverted curves presage the late-cycle macro
  dislocations where sustained cross-asset trends emerge → **flat ⇒ HIGHER** forward TSMOM (Δ>0).
- **H− (transition-whipsaw):** flat/inverted curves mark policy-pivot transitions with frequent trend
  reversals → **flat ⇒ LOWER** forward TSMOM (Δ<0).

The confirmatory detection is therefore **two-sided** (CI on Δ excludes 0; two-sided HAC p into
BH-FDR). This is **not** a hedge: the gates that establish an effect are sign-agnostic but *demanding*
— magnitude **and** dropping the dominant episode **and** presence in ≥2 episodes — which is strictly
harder than a one-sided test, not easier. A confirmed sign must additionally be **economically
coherent with one of H+/H−** (an incoherent sign is reported as exploratory, never confirmatory).

**Two-sided is NOT a back door (locked — clarification 2).** The two-sided design is justified **only**
by the genuine mechanism ambiguity above (H+ vs H−); it is explicitly **not** a licence to report
whichever direction happens to be significant. The arbiter of any result is the **episode jackknife
(§3b), which ranks above the significance test**: an effect that is significant two-sided on the full
sample but **collapses when the 2022–24 episode is dropped is a clean negative**, no matter how
significant it looked. (§4 encodes this precedence.)

### What I am explicitly NOT testing (no-data-mining commitment)
Out of this family — each would be its own future pre-registration, never folded in here: other
maturities/spreads (2Y–3M, 5Y, 30Y, real yields, credit spreads, MOVE/VIX); slope **level changes /
momentum / steepening-speed**; other state encodings searched for fit (raw `<0`, z-scores, other
percentile windows, >3 buckets) — the raw-`<0` inversion and a forward-skip are pre-stated *robustness
gates* (§3/§5), not extra shots at significance; per-sleeve conditioning (rejected at Step 0);
interactions with the existing vol/ER regime variables; horizons other than {21,63,126}.

---

## 2. Test statistic (per cell = spread × horizon)

1. **Forward return** `y_t` = the confirmed strategy's **`h`-day forward cumulative gross return**,
   `∏_{k=t}^{t+h−1}(1+r_k) − 1`, defined where the full window exists.
2. **Regime label** `d_t = S_{t−1}` ∈ {flat=1, steep=0}; middle-tercile days dropped from the cell.
3. **Effect** `Δ = mean(y | flat) − mean(y | steep)`, reported **annualized** (and as bps/day).
4. **Primary p-value:** Newey–West **HAC** *t*-test of the regime dummy, **lag = `h`** (covers the
   overlapping forward-window autocorrelation). **Two-sided**, feeds BH-FDR; sign handled in §4.
5. **Robustness CI:** moving-block bootstrap of Δ, **block length = `h`** (each resampled block spans
   a full forward window), **10,000** resamples, **seed = `config.RANDOM_SEED` (7)** → 95% CI; must
   exclude 0. Reuses `seasonality.block_bootstrap_ci` (with `block=h`).

All windows/lags/blocks are **fixed here, not searched.**

---

## 3. Event-level robustness (what separates a real regime effect from one macro episode)

This **replaces** the calendar half/thirds split of the seasonality study, because here the
independent unit is the **episode**, not the day. Reported for every cell; **required** for CONFIRMED.

- **3a. Episode identification (pre-registered algorithm).** A `flat` **episode** = a maximal
  contiguous run of bottom-tercile (`S=flat`) trading days, with runs separated by **≤ 10 trading
  days merged** into one episode. Report **K** (the episode count) and each episode's date span and
  its contribution to Δ. (For the raw-`<0` robustness view, episodes are runs of `slope<0`; the
  univariate counts are in the table above — K≈10 for 10Y–3M, K=4 for 10Y–2Y.)
- **3b. Leave-one-episode-out (the load-bearing test).** Recompute Δ dropping each episode's days in
  turn; identify the **single most influential** episode (largest |ΔΔ|). To **pass**, after removing
  that one episode Δ must **keep its sign** *and* retain **|Δ| ≥ the magnitude bar** (§4). Given that
  one episode (2022–24) holds 69–97% of inverted days, this is where a sparse-event artifact dies.
- **3c. ≥2-episode presence.** The cell must show the **same-sign** flat−steep forward difference in
  **at least two independent episodes** — not a single regime dressed up as 4,800 observations.
- **3d. Low-power honesty.** With so few episodes the evidence is **inherently low-powered**; this is
  stated as a limitation in every verdict and **no result is over-claimed** from one or two episodes.
- **3e. Sub-period sanity (secondary).** Split the window into halves/thirds and report Δ; with so few
  episodes this is descriptive context, **not** a pass/fail gate (3b/3c are the real test).

---

## 4. Decision rule — stated up front (CONFIRMED vs clean negative)

**Multiplicity:** BH-FDR at **q = 0.10** across the **entire 6-cell family**. Raw and FDR-adjusted
results side by side. BH-FDR is the multiplicity gate; the bars below are *additional, independent*
gates (a deliberate conjunction).

**Economic-magnitude bar (significance is NOT enough):** **|Δ| ≥ 4% annualized** (≈ 1.6 bps/day) in a
single coherent direction, on the full sample. Justification: the strategy targets 10% vol, so a
flat-vs-steep forward gap of ≥4%/yr is a ≈ **0.4 Sharpe-equivalent** regime difference — large enough
that a tilt could matter after costs, yet a level a genuine business-cycle effect would clear. Below
it, a "significant" split is too small to build a tradeable overlay on (the same significance-≠-
tradeable discipline that killed vol-breakout at +0.02 Sharpe).

**Gate precedence (locked — clarification 2): the event-level jackknife is the decisive gate and ranks
ABOVE statistical significance.** Full-sample significance (gate 1 below) is **necessary but not
sufficient**. If a cell passes gates 1–3 but **fails leave-one-episode-out (§3b) or the ≥2-episode
presence (§3c)**, it is a **clean negative** — a result resting on the single dominant 2022–24 episode
does not count, however significant it looked on the full sample. Every cell's verdict **leads with the
jackknife outcome**.

**A cell is CONFIRMED only if it clears ALL of:**
1. **Survives BH-FDR** (q=0.10) across the 6-cell family **and** the block-bootstrap CI on Δ excludes 0; **and**
2. **Clears the magnitude bar** (|Δ| ≥ 4%/yr) on the full sample; **and**
3. **Economically coherent sign** — matches H+ *or* H− (§1), reported as such; **and**
4. **Event-robust** — survives **leave-one-episode-out** (§3b: most-influential episode removed, sign
   and magnitude hold) **and** shows ≥2-episode presence (§3c); **and**
5. **Predictive, not contemporaneous** — passes the confound test (§5).

- **CONFIRMED:** ≥1 cell clears all five (10Y–3M and/or 10Y–2Y, at a stated horizon) → proceed to
  Step 2 (overlay), pending sign-off.
- **NOT confirmed:** no cell clears all five (fails FDR, or sub-magnitude, or collapses under
  leave-one-episode-out, or lives in one episode, or is a contemporaneous confound) → **STOP. Clean
  negative**, consistent with this arc's honest-falsification record (now 0/3 overlays). Do **not**
  build an overlay.

---

## 5. The specific confound: contemporaneous co-movement vs genuine prediction

The rare inversions (2008-adjacent, 2022) **coincide** with TSMOM's own large macro moves. The premise
must distinguish *"the `t−1` slope state **predicts** forward TSMOM"* from *"slope and TSMOM are both
driven by the same macro shock **contemporaneously**."* Pre-registered separation:
- **Forward by construction:** state at `t−1`, returns over `[t, t+h]` — never contemporaneous.
- **Contemporaneous diagnostic:** also compute the same-window *contemporaneous* association (state at
  `t` vs return over `[t−h, t]`). If the forward effect ≈ the contemporaneous effect **and** both die
  under leave-one-episode-out, it is co-movement, not prediction.
- **Forward-skip robustness:** repeat with the forward window starting at **`t+21`** (skip the first
  month, i.e. the acute co-move). Predictive content should survive; a pure co-occurrence will not.
- **Decisive rule:** the leave-one-episode-out (§3b) is the arbiter. **If the only evidence is
  contemporaneous co-occurrence during 2–3 macro shocks — i.e. the effect vanishes when the dominant
  episode is dropped — that is a confound, not an edge → clean negative.**

---

## 6. Step-2 forward-commitment (only if CONFIRMED; recorded now to bind it)

If the premise is confirmed, Step 2 will:
- Express the regime as **ONE simple, mechanical, causal tilt** on aggregate TSMOM exposure
  (`S_{t−1}`-conditioned multiplier on the whole book) — no per-asset signal, no stacking.
- Charge **full transaction costs** on the overlay's incremental turnover (`config.TRANSACTION_COST_BPS`).
- Be judged by a **paired-difference bootstrap of the net Sharpe** between (TSMOM+overlay) and (plain
  TSMOM); the CI on the **difference** must exclude 0. Any overlay variants are **pre-stated** and
  **BH-FDR'd across variants**; CI width / few-episode fragility reported honestly.
- **Out-of-sample = leave-one-episode-out, not a single time split.** Because the dominant inversion
  (2022–24) sits at the sample end, a last-N-years holdout would confound episode placement with
  out-of-sample; the appropriate cross-validation for a sparse-event signal is **drop-one-episode**
  (does the overlay still help when its biggest episode is withheld?). This is pre-committed as the
  primary OOS check.
- **No tuning to a win.** A null/negative is a valid, publishable outcome.

---

## 7. Reproducibility & the new causal primitive

Deterministic: fixed seed (`config.RANDOM_SEED = 7`), fixed windows/lags/blocks/terciles as stated.
A new module (`src/yields.py`) will hold the causal yield primitives (FRED loader → ETF-calendar
reindex + past-only ffill → slope → trailing-percentile state → `t−1` lag). It gets a
**truncation-invariance unit test** (recompute on any prefix `[0..i]` ⇒ identical history) plus a
calendar-alignment test, exactly like the existing daily/regime infra. New config constants
(percentile window reuse, tercile cuts, horizon set, magnitude bar, episode-merge gap) live in
`config.py` — no magic numbers inline. Same input + this contract ⇒ identical output.
