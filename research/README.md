# Research arc — five investigations + a parallel study

This folder holds the **committed write-ups** of the research arc around the supported
multi-asset TSMOM core (SUPPORTED — CI excludes 0; not independently confirmed): one diagnostic,
four overlays recorded as `not_promoted`, and a parallel cross-sectional study (XSMOM, `falsified`). The reports and figures
here are snapshots — the code lives at the repo root / `src/` (kept there so imports stay
clean), and re-running the scripts regenerates the live copies under `output/` (git-ignored).

The four rejections are **first-class results**, not discarded experiments: the value of
this project is the honest arc from a *supported* core to overlays that were *not promoted*, each
negative reached at the cheapest stage with a mechanism explanation. Corrections to statements in
the dated reports here are in [`ERRATA_2026-09-27.md`](ERRATA_2026-09-27.md).

| # | Investigation | Verdict | Report | Code (repo root / `src/`) | Reproduce |
|---|---|---|---|---|---|
| 1 | **Drawdown attribution diagnostic** | drawdowns are crash-type, multi-sleeve, in ordinary-vol / low-correlation regimes | [`diagnostic/DRAWDOWN_ATTRIBUTION_REPORT.md`](diagnostic/DRAWDOWN_ATTRIBUTION_REPORT.md) | `run_drawdown_attribution.py`, `src/attribution.py`, `src/regime.py` | `python run_drawdown_attribution.py` |
| 2 | **Crash-defense overlay** | **`not_promoted`** (rejected at Phase 0) — premise not supported (descriptive comparison, no inference): the systemic-risk trigger is anti-aligned (maxed in the 2008/2020 profit windows, average in the real drawdowns) | [`crash_defense/PHASE0_SYSTEMIC_VERIFICATION.md`](crash_defense/PHASE0_SYSTEMIC_VERIFICATION.md) | `verify_systemic.py`, `src/attribution.py`, `src/regime.py` | `python verify_systemic.py` |
| 3 | **Vol-compression breakout overlay** | **`not_promoted`** (rejected at Phase 1B) — premise not supported (descriptive comparison, no inference): close-to-close compression precedes vol expansion but **not** directional follow-through; apparent edge was a narrow-channel artifact | [`vol_breakout/BREAKOUT_PHASE1A_INFRA.md`](vol_breakout/BREAKOUT_PHASE1A_INFRA.md) (infra), [`vol_breakout/BREAKOUT_PHASE1B_PREMISE.md`](vol_breakout/BREAKOUT_PHASE1B_PREMISE.md) (premise) | `run_breakout_phase1a.py`, `run_breakout_phase1b.py`, `src/daily.py`, `src/premise.py` | `python run_breakout_phase1a.py` → `python run_breakout_phase1b.py` |
| 4 | **Seasonality / calendar-effects overlay** | **`not_promoted`** (rejected at premise, 0/18) — **0/18** pre-registered cells survive the 5-gate conjunction (BH-FDR q=0.10 + sign + ≥5 bps/day magnitude + sub-period/year stability + non-concentration); the Monday near-miss (right sign in all 6 scopes, Bond *p*=0.026 in isolation) is one raw *p* < 0.05 in 18 tests, about what noise alone produces; that cell also fails the magnitude and stability gates | [`seasonality/PREREGISTRATION.md`](seasonality/PREREGISTRATION.md) (contract), [`seasonality/SEASONALITY_PHASE1_PREMISE.md`](seasonality/SEASONALITY_PHASE1_PREMISE.md) (premise) | `run_seasonality_premise.py`, `src/seasonality.py`, `src/daily.py` | `python run_seasonality_premise.py` |
| 5 | **Yield-curve slope overlay (macro regime)** | **`not_promoted`** (rejected at premise, 0/6) — a single economy-wide curve slope (10Y-3M primary, 10Y-2Y robustness) as a **portfolio-regime conditioner**: **0/6** pre-registered cells confirmed (BH-FDR *p*=0.60–0.67, all bootstrap CIs cross 0) — a **clean null with no claimable direction**. Dropping the 2022-24 episode keeps 26–68% of the weak negative tilt (sign unchanged in 6/6 cells) and takes the two h=126 cells below the 4%/yr bar; the tested tercile-flat state spans 12–13 episodes, 2022-24 being 19–21% of its days. The binding-episode jackknife rule was changed after the first run; under the registered rule 3/6 cells pass it, so the null rests on BH-FDR ([`ERRATA_2026-09-27.md`](ERRATA_2026-09-27.md) §1–2). | [`yield_spread/PREREGISTRATION.md`](yield_spread/PREREGISTRATION.md) (contract), [`yield_spread/PHASE1_PREMISE.md`](yield_spread/PHASE1_PREMISE.md) (premise) | `run_yield_premise.py`, `src/yields.py`, `src/seasonality.py` (reused stats) | `python run_yield_premise.py` |

## Method spine (shared by all five)
- **Reuse, not re-derivation** — every investigation reuses the *exact* vol-scaled positions /
  data of the validated monthly engine and **reconciles** before attributing (diagnostic
  reconciled to 3.5e-18; daily infra reconciles to the monthly engine at 1.3e-15).
- **No look-ahead, tested** — point-in-time primitives with truncation-invariance unit
  tests; the descriptive episode labels are flagged as full-sample, the *reusable* regime
  variables are strictly causal.
- **Premise before strategy** — overlays are gated: verify the premise exists (cheap, read-only)
  before building anything. All four overlays were killed at the premise gate, before any P&L fitting.
- **Pre-registration + multiplicity control** — for the seasonality study (the highest-overfitting-risk
  direction), the full 18-test family and decision rule were **written down before any computation**, and
  corrected with **BH-FDR** across the whole family; under it the tempting Monday cell (significant in
  isolation) does not survive, and it also fails the magnitude and stability gates.
- **Honest evaluation** — pre-registered thresholds, robustness across a neighborhood (not a menu
  to cherry-pick), and effect sizes read against an economically meaningful bar — never tuned to a win.
- **Effective event count, not nominal sample size** — the yield-spread overlay added a distinct
  pitfall the prior three did not: a slow macro-regime signal can present ~4,800 daily observations yet
  only about a dozen independent episodes (12–13 in the tested flat state), so the episode count, not
  the day count, bounds the evidence. The registered leave-one-episode-out jackknife made this a gate;
  its binding-episode rule was later changed (see the errata), and the yield null itself rests on
  BH-FDR.

**The meta-point now spans four orthogonal overlay directions** — crash-defense, vol-compression
breakout, seasonality (price-based) and yield-curve slope (genuinely macro / orthogonal to the price
paths) — **all rejected at the premise gate before any P&L (`not_promoted`), each with a
mechanism.** Along the way the process declined a tempting **calendar effect** (seasonality's Monday:
one raw *p* < 0.05 in 18 tests, as noise predicts; none survives BH-FDR). A broader **macro-regime overlay** (beyond the yield
curve) was then **pre-emptively closed at the event-count level** rather than taken to a premise test:
as the same class of slow, economy-wide signal, its regime transitions are equally sparse in-sample
(about a dozen independent episodes), so it would face the same shortage of evidence and only
reproduce a foregone conclusion — disciplined budget allocation, not an untested gap.

## Parallel investigation — Cross-sectional momentum (XSMOM)

Distinct from the overlay arc above: XSMOM is **not an overlay on** the TSMOM core but its
**cross-sectional counterpart** — the same 17 ETFs and the same engine, ranking assets *against each
other* (dollar-neutral long/short) instead of each against its own trend. Pre-registered, falsified,
reusing the engine verbatim, in two phases:

| Phase | Verdict | Report | Code (repo root / `src/`) |
|---|---|---|---|
| **P1 — 17-ETF head-to-head** | **`falsified`** — net Sharpe **0.28** (95% CI [−0.18, 0.75] crosses 0); `corr(XSMOM, TSMOM) = +0.42` ⇒ the 50/50 mix *dilutes* (0.66 < TSMOM's 0.75); part static premium (Sharpe halves under demeaning) | [`xsmom/XSMOM_README.md`](xsmom/XSMOM_README.md) | `src/xsmom.py`, `xsmom_config.py`, `run_xsmom.py` |
| **P2 — 5-universe FDR map** | **`falsified` 0/5** — no universe passes BH-FDR (α = 0.05) + walk-forward + 3/6/9/12 sign consistency (best universe U4: Deflated Sharpe 0.779); the Lo–MacKinlay decomposition **cannot separate the terms**: the XSMOM-only lead-lag term's CI contains 0 in 5/5 universes, and so does the own-autocorrelation term TSMOM harvests (errata §4) | [`xsmom/XSMOM_UNIVERSES_README.md`](xsmom/XSMOM_UNIVERSES_README.md) | `src/xsmom_data.py`, `src/xsmom_stats.py`, `xsmom_universes.py`, `run_xsmom_universes.py` |

**Mechanism (why it belongs in the arc):** XSMOM is +0.42-correlated with the supported core, so it
adds **no diversification**, and it has **no standalone edge** at this power. The decomposition does not
show *why*: only static dispersion (term3) is distinguishable from 0, and demeaning collapses the Sharpe
in 1/5 universes (U4). A parallel falsification sitting alongside the four overlays. (Reproduce:
`python run_xsmom.py` → 0.28 / +0.42; `python run_xsmom_universes.py` → 0/5; the price snapshot is not
committed, see [`../data/README.md`](../data/README.md).)

See the top-level [`README.md`](../README.md) for the full narrative and the supported-core results.
