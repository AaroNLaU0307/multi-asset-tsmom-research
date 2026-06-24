# Pre-registration — Seasonality / calendar effects on the multi-asset TSMOM universe

**Status: CONTRACT. Written BEFORE any calendar statistic is computed.** Once signed off this list is
fixed. No effect is added, dropped, or re-defined mid-analysis to chase a result. A new idea that
arises later is a *separate* future pre-registration, not an amendment to this family.

*Why the extra discipline here:* seasonality is the **highest-overfitting-risk** direction in this
research arc. Calendar slicing has many dimensions (month, day-of-week, day-of-month, turn-of-month,
holiday-adjacent, quarter-end, option-expiry, FOMC, …) and **any** random return series contains some
"significant-looking" calendar pattern purely from multiple comparisons. Therefore the bar is set
*stricter* than the prior two overlays (crash-defense, vol-breakout): a pre-registered, deliberately
**small** family, BH-FDR multiplicity control across the **entire** family, **plus** two further
independent hurdles (sub-period stability and an economic-magnitude bar). Statistical significance
alone is explicitly **not** sufficient.

---

## 0. Data, scope, and what stays descriptive

- **Series:** the existing verified-causal daily simple returns (`src/daily.daily_returns` on the
  cached adjusted-close panel — the same source the validated monthly engine resamples; daily↔monthly
  reconciles to ~1e-15). No new data.
- **Sample:** the common all-17-present daily window **2007-04-18 → 2026-06-12 (4,820 trading days)**,
  bound by UNG's inception — identical to the monthly engine's window. A balanced cross-section
  (no composition drift) for the whole study.
- **In-sample / overfitting note.** This repo's TSMOM core has *no calendar IS/OOS wall*; its
  anti-overfitting discipline is *no parameter tuning* + sub-period stability. **Step 1 is purely
  descriptive and pre-registered — there is nothing to fit, hence nothing to overfit.** The
  sub-period split (§3) is the stability guard. The genuine overfitting risk lives in **Step 2**
  (a strategy with P&L); §6 pre-commits a train/holdout split there so the overlay is never confirmed
  on the same data that surfaced the effect.
- **Step 1 is descriptive only:** mean returns on effect-days vs non-effect-days. **No positions, no
  P&L, no strategy, no tuning.** P&L appears only in Step 2, and only if an effect is CONFIRMED here.

---

## 1. The fixed family of effects (small, motivated, a-priori — NOT discovered from the data)

Three effects, each with genuine prior literature support. Each is tested **pooled and per-sleeve**
(see §5), so the family is **3 effects × (1 pooled + 5 sleeves) = 18 tests**.

| # | Effect | Exact day definition | Prior direction | One-line justification |
|---|--------|----------------------|-----------------|------------------------|
| **E1** | **Turn-of-the-Month (TOM)** | Trading days **[-1, +1, +2, +3]**: the last trading day of each calendar month plus the first 3 trading days of the next month (4 days/month). Everything else = non-TOM. | **Positive** (TOM > non-TOM) | Among the most robust calendar anomalies in the literature — Ariel (1987), Lakonishok & Smidt (1988), McConnell & Xu (2008): equity returns cluster around the month boundary (cash-flow / payroll / rebalancing timing). |
| **E2** | **Halloween / "Sell in May"** | **Winter = Nov–Apr** vs **Summer = May–Oct** (calendar months of the trading day). Δ = mean(winter) − mean(summer). | **Positive** (winter > summer) | Bouman & Jacobsen (2002): documented across many markets — the equity premium is disproportionately earned Nov–Apr; summer returns near zero. |
| **E3** | **Monday (day-of-week)** | **Monday** (or the first trading day of the week if Monday is a holiday) vs **all other weekdays**. Δ = mean(Monday) − mean(non-Monday). | **Negative** (Monday < rest) | French (1980), Gibbons & Hess (1981): the classic negative-Monday/weekend effect. Including it also tests *honestly* whether the effect has decayed post-2000 (a likely clean negative is itself a result). |

### What I am explicitly NOT testing (and why these are excluded)

To make the no-data-mining commitment concrete, the following calendar dimensions are **out of this
family** — each would be its own future pre-registration if ever motivated, never folded in here:

- **January effect / January barometer / "other-month" month-of-year contrasts** (E2 already fixes the
  *one* month-partition I will test; testing 12 months or "best month" is the data-mining trap).
- **Day-of-week other than Monday** (Tuesday/Wed/Thu/Friday individually) — I have a specific Monday
  prior only; scanning all 5 weekdays is exactly the multiple-comparison trap E3 is meant to avoid.
- **Day-of-month / intramonth seasonality beyond the fixed TOM window** (no search over "which days").
- **Holiday-adjacent (pre-/post-holiday) effects**, **quarter-end / window-dressing**,
  **options-expiration (triple-witching) week**, **FOMC-day drift**, **tax-loss-selling / Santa-rally
  late-December**, **half-of-month (Ariel split)**, lunar/weather/sports effects.
- **Interactions** between effects (e.g. "TOM in winter only") — no conditioning stacks.

---

## 2. Test statistic (per effect × scope)

For each (effect, scope) cell:

1. **Scope return series** `r_t`: equal-weight mean of the in-scope assets' daily returns on day *t*
   (pooled = all 17; sleeve = that sleeve's members). Computed on the common balanced window.
2. **Effect difference** `Δ = mean(r_t | effect-day) − mean(r_t | non-effect-day)`, reported in **bps/day**.
3. **Primary p-value:** Newey–West **HAC** *t*-test of the effect-day dummy coefficient (`r_t = α + β·1[effect] + ε`),
   **lag = 10 trading days** (covers weekly autocorrelation and the 4-day TOM cluster). `β = Δ`.
   **Two-sided** p-values feed the BH-FDR family (the conservative choice); the **sign** is checked
   against the prior direction separately as part of the decision rule (§4).
4. **Robustness CI (cross-check):** moving-block bootstrap of `Δ` — block length **10 trading days**,
   **10,000** resamples, **seed = `config.RANDOM_SEED` (7)** → 95% CI. Reported alongside the HAC test.

All windows/blocks/lags above are **fixed here, not searched.** Per-effect horizon = **daily mean**
(the effect is a property of the labelled days; no forward-return horizon is involved in Step 1).

---

## 3. Robustness / stability requirements (what separates a real seasonal from an artifact)

Reported for every cell; **required** (not optional) for any CONFIRMED verdict. **The stability and
concentration checks are matched to each effect's event frequency** — a generic daily half/thirds
split is appropriate for the high-frequency effects (E1, E3: hundreds–thousands of independent events)
but is statistically meaningless for the annual effect (E2: only ~19 winter-vs-summer cycles in the
sample), and a daily-winsorized concentration check cannot detect E2's real fragility, which is at the
**year** level, not the day level.

### 3a. High-frequency effects — **E1 (turn-of-month) and E3 (Monday)**

- **Sub-period stability.** Split the 4,820-day common index into **equal halves** and **equal thirds**
  (by trading-day count, fixed here):
  - Halves: H1 ≈ 2007-04 → 2016-10, H2 ≈ 2016-10 → 2026-06.
  - Thirds: T1 ≈ 2007-04 → 2013-07, T2 ≈ 2013-07 → 2019-12, T3 ≈ 2019-12 → 2026-06.
  A real effect keeps the **same sign** and roughly the magnitude in **both halves** (and in **≥ 2 of 3
  thirds**); an effect that lives in one era/regime only fails this hurdle.
- **Concentration / outlier check.** Recompute `Δ` on **1%/99%-winsorized** returns; report the share
  of the raw `Δ` contributed by the single largest effect-day. A "seasonal" that survives only because
  of a few extreme days is fragile — to pass, winsorized `Δ` must **keep its sign** and retain
  **≥ 0.5×** the magnitude bar (≥ 2.5 bps/day).

### 3b. Annual effect — **E2 (Halloween / Sell-in-May)** — year-level checks (replaces 3a for E2)

E2 has only **~19 annual cycles**, so the daily half/thirds split (≈6–10 annual observations per
bucket) and the daily-winsorized check are not informative for it. Instead:

- **Stability (year-level, low-power by construction).** Report the **per-year winter-minus-summer
  spread** across all ~19 years (table / distribution) and state **how many individual years carry the
  prior-consistent sign**. We **explicitly do NOT over-claim stability** from a half/thirds split for
  E2: with ~19 cycles the evidence is inherently low-powered, and that limitation is reported as such.
  A pass requires the spread to be **positive in a clear majority of years** (not a near-even split that
  only looks positive on average).
- **Concentration (year-level jackknife).** **Leave-one-year-out**: recompute the full-sample
  winter−summer Δ dropping each year in turn, and also dropping the **1–2 most extreme years** together.
  To pass, no single year (nor the top 1–2 jointly) may **flip the sign** or **collapse the magnitude
  below the bar** (≥ 5 bps/day). This is E2's real fragility test — a "seasonal" driven by a couple of
  extreme winters/summers fails here.

### 3c. Applies to all three effects

- **Per-sleeve consistency vs a single-sleeve fluke.** A pooled effect should not be the artifact of one
  sleeve; a sleeve-specific effect must be coherent with its economic story (§5).

---

## 4. Decision rule — stated up front (CONFIRMED vs clean negative)

### Multiplicity control
**BH-FDR at q = 0.10** applied across the **entire 18-test family** (all 3 effects × pooled + 5 sleeves).
Raw and FDR-adjusted results reported side-by-side. BH-FDR is the *multiplicity* gate; the magnitude
and stability hurdles below are *additional, independent* gates (a deliberate conjunction — this is
where the "stricter than prior overlays" discipline lives).

### Economic-magnitude bar (significance is NOT enough)
**|Δ| ≥ 5 bps/day (0.05%)** on the full sample, in the prior-consistent direction. Justification:
- It exceeds plausible **round-trip transaction cost** (~2 bps one-way ⇒ ~4 bps round-trip) — below
  this, no tilt could survive costs.
- It is **literature-calibrated**: TOM ≈ 10–15 bps/day, the Halloween winter−summer gap ≈ 6 bps/day,
  the historical Monday effect ≈ −10 to −15 bps/day — so 5 bps/day sits *below* the genuine-effect
  magnitudes (won't reject a real effect) yet *above* economic noise (a sub-5-bps "significant"
  result is, correctly, a clean negative — the same significance-≠-tradeable discipline used to kill
  vol-breakout at +0.02).

### Verdict (an effect is CONFIRMED only if it clears ALL of):
1. **Survives BH-FDR** (q = 0.10) across the 18-test family; **and**
2. **Sign matches the prior** direction (§1); **and**
3. **Clears the magnitude bar** |Δ| ≥ 5 bps/day on the full sample; **and**
4. **Stable** — by the effect-appropriate check (§3): for **E1/E3**, sub-period stable (same sign +
   ~magnitude in both halves and ≥ 2/3 thirds, §3a); for **E2**, the per-year winter−summer spread is
   prior-consistent in a clear majority of the ~19 years (§3b), reported as inherently low-powered; **and**
5. **Not concentration-driven** — by the effect-appropriate check (§3): for **E1/E3**, the daily
   1%/99%-winsorized check (§3a); for **E2**, the year-level leave-one(-or-two)-out jackknife does not
   flip the sign or drop Δ below the bar (§3b).

- **CONFIRMED:** ≥ 1 effect clears all five, on a stated scope (pooled and/or specific sleeves)
  → proceed to Step 2, scoped to exactly those sleeves.
- **NOT confirmed:** no effect clears all five (fails FDR, or below magnitude, or unstable, or
  outlier-driven) → **STOP. Clean negative**, consistent with the portfolio's honest-falsification
  record. Do **not** build a strategy.

---

## 5. Per-sleeve handling (committed up front)

**Both pooled and per-sleeve**, all counted in the BH-FDR family. Rationale: prior work in this arc
showed effects are frequently **universe-specific** (equities ≠ bonds/commodities/FX), so a real
equity seasonal must not be **pooled away** by bonds/FX that don't share it. But every sleeve test
**pays the multiplicity tax** — hence all 18 cells enter BH-FDR together. Sleeves (from
`universe.GROUPS`): **Equity** (SPY EEM EWJ XLE XLU), **Bond** (TLT SHY LQD HYG),
**Commodity** (USO UNG GLD DBA), **FX** (UUP FXY), **RealEstate** (VNQ RWX).

A priori, the literature effects (E1–E3) are **equity-centric**; finding them in Equity/RealEstate but
not Bond/FX would be *coherent*, whereas an effect appearing only in, say, FX with no equity analogue
would be treated as a likely fluke pending the stability/concentration checks.

---

## 6. Step 2 forward-commitment (only if an effect is CONFIRMED; recorded now to bind it)

If Step 1 confirms an effect, Step 2 will:
- Express the surviving effect as **ONE simple, mechanical tilt** on the existing TSMOM exposure,
  scoped to the sleeves where it held. **No stacking** of calendar conditions; survive first, add
  complexity only if warranted.
- Be **point-in-time / causal** throughout, with **full transaction-cost modelling** (calendar tilts
  churn positions — costs are charged).
- Be evaluated by a **paired-difference bootstrap of the Sharpe** between (TSMOM + overlay) and
  (plain TSMOM); the CI on the *difference* must exclude zero. If multiple overlay variants are tried,
  they are **pre-stated** and BH-FDR'd across variants. Trade count / CI width reported honestly
  (a wide CI from few effect-days is itself a soft negative).
- **Train/holdout discipline:** because seasonality is the highest-overfit-risk direction, the overlay's
  paired comparison will additionally be checked on a **pre-committed final holdout (last 4 years,
  2022-06 → 2026-06)** kept untouched while the rule is specified — the overlay is not declared a win on
  the same data that surfaced the effect. (Exact split confirmed at Step 2 entry.)
- **No tuning to a win.** A null/negative is a valid, publishable outcome.

---

## 7. Reproducibility

Deterministic: fixed seed (`config.RANDOM_SEED = 7`), fixed windows/blocks/lags as stated. Same input +
this contract ⇒ identical output. The Step-1 computation will live in a new causal module with
truncation-invariance unit tests for any new point-in-time primitive (e.g. the TOM-day labeller), like
the existing daily infra.
