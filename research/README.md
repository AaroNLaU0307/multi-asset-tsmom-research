# Research arc — the five investigations

This folder holds the **committed write-ups** of the research arc around the confirmed
multi-asset TSMOM core: one diagnostic, four falsified overlays, and a parallel cross-sectional study
(XSMOM). The reports and figures
here are snapshots — the code lives at the repo root / `src/` (kept there so imports stay
clean), and re-running the scripts regenerates the live copies under `output/` (git-ignored).

The four falsifications are **first-class results**, not discarded experiments: the value of
this project is the honest *confirmed → falsified* arc, each negative reached at the cheapest
stage with a mechanism explanation.

| # | Investigation | Verdict | Report | Code (repo root / `src/`) | Reproduce |
|---|---|---|---|---|---|
| 1 | **Drawdown attribution diagnostic** | drawdowns are crash-type, multi-sleeve, in ordinary-vol / low-correlation regimes | [`diagnostic/DRAWDOWN_ATTRIBUTION_REPORT.md`](diagnostic/DRAWDOWN_ATTRIBUTION_REPORT.md) | `run_drawdown_attribution.py`, `src/attribution.py`, `src/regime.py` | `python run_drawdown_attribution.py` |
| 2 | **Crash-defense overlay** | **FALSIFIED** at Phase 0 — systemic-risk trigger anti-aligned (fires in 2008/2020 profit windows, silent in real drawdowns) | [`crash_defense/PHASE0_SYSTEMIC_VERIFICATION.md`](crash_defense/PHASE0_SYSTEMIC_VERIFICATION.md) | `verify_systemic.py`, `src/attribution.py`, `src/regime.py` | `python verify_systemic.py` |
| 3 | **Vol-compression breakout overlay** | **FALSIFIED** at Phase 1B — close-to-close compression precedes vol expansion but **not** directional follow-through; apparent edge was a narrow-channel artifact | [`vol_breakout/BREAKOUT_PHASE1A_INFRA.md`](vol_breakout/BREAKOUT_PHASE1A_INFRA.md) (infra), [`vol_breakout/BREAKOUT_PHASE1B_PREMISE.md`](vol_breakout/BREAKOUT_PHASE1B_PREMISE.md) (premise) | `run_breakout_phase1a.py`, `run_breakout_phase1b.py`, `src/daily.py`, `src/premise.py` | `python run_breakout_phase1a.py` → `python run_breakout_phase1b.py` |
| 4 | **Seasonality / calendar-effects overlay** | **FALSIFIED** at premise — **0/18** pre-registered cells survive the 5-gate conjunction (BH-FDR q=0.10 + sign + ≥5 bps/day magnitude + sub-period/year stability + non-concentration); the Monday near-miss (right sign in all 6 sleeves, Bond *p*=0.026 in isolation) is an **actively-caught false positive** that evaporates under the 18-test multiplicity tax | [`seasonality/PREREGISTRATION.md`](seasonality/PREREGISTRATION.md) (contract), [`seasonality/SEASONALITY_PHASE1_PREMISE.md`](seasonality/SEASONALITY_PHASE1_PREMISE.md) (premise) | `run_seasonality_premise.py`, `src/seasonality.py`, `src/daily.py` | `python run_seasonality_premise.py` |
| 5 | **Yield-curve slope overlay (macro regime)** | **FALSIFIED** at premise — a single economy-wide curve slope (10Y-3M primary, 10Y-2Y robustness) as a **portfolio-regime conditioner**: **0/6** pre-registered cells confirmed (BH-FDR *p*=0.60–0.67, all bootstrap CIs cross 0), and the weak negative tilt is **carried entirely by the single 2022-24 inversion episode** — it collapses below the 4%/yr bar when that episode is dropped (the largest flat stretch, 2017-20, contributes ≈0). A **clean null with no claimable direction**. Distinct pitfall vs the prior three: **nominal sample size, not significance** — ~4,800 days but the inverted state is effectively **one** macro episode (2022-24 = 97% of 10Y-2Y inverted days); the **episode jackknife, ranked above the significance test**, is what exposed it. | [`yield_spread/PREREGISTRATION.md`](yield_spread/PREREGISTRATION.md) (contract), [`yield_spread/PHASE1_PREMISE.md`](yield_spread/PHASE1_PREMISE.md) (premise) | `run_yield_premise.py`, `src/yields.py`, `src/seasonality.py` (reused stats) | `python run_yield_premise.py` |

## Method spine (shared by all five)
- **Reuse, not re-derivation** — every investigation reuses the *exact* vol-scaled positions /
  data of the validated monthly engine and **reconciles** before attributing (diagnostic
  reconciled to 3.5e-18; daily infra reconciles to the monthly engine at 1.3e-15).
- **No look-ahead, proven by tests** — point-in-time primitives with truncation-invariance unit
  tests; the descriptive episode labels are flagged as full-sample, the *reusable* regime
  variables are strictly causal.
- **Premise before strategy** — overlays are gated: verify the premise exists (cheap, read-only)
  before building anything. All four overlays were killed at the premise gate, before any P&L fitting.
- **Pre-registration + multiplicity control** — for the seasonality study (the highest-overfitting-risk
  direction), the full 18-test family and decision rule were **written down before any computation**, and
  corrected with **BH-FDR** across the whole family; this is what dissolved the tempting Monday false
  positive (significant in isolation, gone after the multiplicity tax).
- **Honest evaluation** — pre-registered thresholds, robustness across a neighborhood (not a menu
  to cherry-pick), and effect sizes read against an economically meaningful bar — never tuned to a win.
- **Effective event count, not nominal sample size** — the yield-spread overlay added a distinct
  pitfall the prior three did not: a slow macro-regime signal can present ~4,800 daily observations yet
  only a *handful of independent episodes*. The **episode jackknife is ranked above the significance
  test** — an effect that evaporates when its single dominant episode (2022-24) is dropped is a clean
  null, however many days it nominally spanned.

**The meta-point now spans four orthogonal overlay directions** — crash-defense, vol-compression
breakout, seasonality (price-based) and yield-curve slope (genuinely macro / orthogonal to the price
paths) — **all falsified before any P&L, each with a mechanism.** The disciplined process has now caught
two *different* statistical illusions: a tempting **false positive** (seasonality's Monday, dissolved by
the BH-FDR multiplicity tax) and a **nominal-sample-size illusion** (yield-spread's single-episode
effect, dissolved by the episode jackknife). A broader **macro-regime overlay** (beyond the yield
curve) was then **pre-emptively closed at the event-count level** rather than taken to a premise test:
as the same class of slow, economy-wide signal, its regime transitions are equally sparse in-sample
(a handful of independent episodes), so it would hit the identical wall and only reproduce a foregone
conclusion — disciplined budget allocation, not an untested gap.

## Parallel investigation — Cross-sectional momentum (XSMOM)

Distinct from the overlay arc above: XSMOM is **not an overlay on** the TSMOM core but its
**cross-sectional counterpart** — the same 17 ETFs and the same engine, ranking assets *against each
other* (dollar-neutral long/short) instead of each against its own trend. Pre-registered, falsified,
reusing the engine verbatim, in two phases:

| Phase | Verdict | Report | Code (repo root / `src/`) |
|---|---|---|---|
| **P1 — 17-ETF head-to-head** | **FALSIFIED** — net Sharpe **0.28** (95% CI [−0.18, 0.75] crosses 0); `corr(XSMOM, TSMOM) = +0.42` ⇒ the 50/50 mix *dilutes* (0.66 < TSMOM's 0.75); part static premium (Sharpe halves under demeaning) | [`xsmom/XSMOM_README.md`](xsmom/XSMOM_README.md) | `src/xsmom.py`, `xsmom_config.py`, `run_xsmom.py` |
| **P2 — 5-universe FDR map** | **FALSIFIED 0/5** — no universe survives BH-FDR + walk-forward + Deflated-Sharpe; Lo–MacKinlay shows the XSMOM-only **lead-lag term is not shown to be non-trivial anywhere** | [`xsmom/XSMOM_UNIVERSES_README.md`](xsmom/XSMOM_UNIVERSES_README.md) | `src/xsmom_data.py`, `src/xsmom_stats.py`, `xsmom_universes.py`, `run_xsmom_universes.py` |

**Mechanism (why it belongs in the arc):** at liquid-ETF granularity, rank-relative and trend-absolute
momentum are largely the **same source** the confirmed core already harvests — so XSMOM adds **no
diversification** (the +0.42 correlation) and **no confirmable standalone edge**. A parallel
falsification *with a mechanism*, sitting alongside the four overlays. (Reproduce: `python run_xsmom.py`
→ 0.28 / +0.42; `python run_xsmom_universes.py` → 0/5. +28 tests, suite total 101.)

See the top-level [`README.md`](../README.md) for the full narrative and the confirmed-core results.
