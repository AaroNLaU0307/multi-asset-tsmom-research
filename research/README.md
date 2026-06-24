# Research arc — the four investigations

This folder holds the **committed write-ups** of the research arc around the confirmed
multi-asset TSMOM core: one diagnostic and three falsified overlays. The reports and figures
here are snapshots — the code lives at the repo root / `src/` (kept there so imports stay
clean), and re-running the scripts regenerates the live copies under `output/` (git-ignored).

The three falsifications are **first-class results**, not discarded experiments: the value of
this project is the honest *confirmed → falsified* arc, each negative reached at the cheapest
stage with a mechanism explanation.

| # | Investigation | Verdict | Report | Code (repo root / `src/`) | Reproduce |
|---|---|---|---|---|---|
| 1 | **Drawdown attribution diagnostic** | drawdowns are crash-type, multi-sleeve, in ordinary-vol / low-correlation regimes | [`diagnostic/DRAWDOWN_ATTRIBUTION_REPORT.md`](diagnostic/DRAWDOWN_ATTRIBUTION_REPORT.md) | `run_drawdown_attribution.py`, `src/attribution.py`, `src/regime.py` | `python run_drawdown_attribution.py` |
| 2 | **Crash-defense overlay** | **FALSIFIED** at Phase 0 — systemic-risk trigger anti-aligned (fires in 2008/2020 profit windows, silent in real drawdowns) | [`crash_defense/PHASE0_SYSTEMIC_VERIFICATION.md`](crash_defense/PHASE0_SYSTEMIC_VERIFICATION.md) | `verify_systemic.py`, `src/attribution.py`, `src/regime.py` | `python verify_systemic.py` |
| 3 | **Vol-compression breakout overlay** | **FALSIFIED** at Phase 1B — close-to-close compression precedes vol expansion but **not** directional follow-through; apparent edge was a narrow-channel artifact | [`vol_breakout/BREAKOUT_PHASE1A_INFRA.md`](vol_breakout/BREAKOUT_PHASE1A_INFRA.md) (infra), [`vol_breakout/BREAKOUT_PHASE1B_PREMISE.md`](vol_breakout/BREAKOUT_PHASE1B_PREMISE.md) (premise) | `run_breakout_phase1a.py`, `run_breakout_phase1b.py`, `src/daily.py`, `src/premise.py` | `python run_breakout_phase1a.py` → `python run_breakout_phase1b.py` |
| 4 | **Seasonality / calendar-effects overlay** | **FALSIFIED** at premise — **0/18** pre-registered cells survive the 5-gate conjunction (BH-FDR q=0.10 + sign + ≥5 bps/day magnitude + sub-period/year stability + non-concentration); the Monday near-miss (right sign in all 6 sleeves, Bond *p*=0.026 in isolation) is an **actively-caught false positive** that evaporates under the 18-test multiplicity tax | [`seasonality/PREREGISTRATION.md`](seasonality/PREREGISTRATION.md) (contract), [`seasonality/SEASONALITY_PHASE1_PREMISE.md`](seasonality/SEASONALITY_PHASE1_PREMISE.md) (premise) | `run_seasonality_premise.py`, `src/seasonality.py`, `src/daily.py` | `python run_seasonality_premise.py` |

## Method spine (shared by all four)
- **Reuse, not re-derivation** — every investigation reuses the *exact* vol-scaled positions /
  data of the validated monthly engine and **reconciles** before attributing (diagnostic
  reconciled to 3.5e-18; daily infra reconciles to the monthly engine at 1.3e-15).
- **No look-ahead, proven by tests** — point-in-time primitives with truncation-invariance unit
  tests; the descriptive episode labels are flagged as full-sample, the *reusable* regime
  variables are strictly causal.
- **Premise before strategy** — overlays are gated: verify the premise exists (cheap, read-only)
  before building anything. All three overlays were killed at the premise gate, before any P&L fitting.
- **Pre-registration + multiplicity control** — for the seasonality study (the highest-overfitting-risk
  direction), the full 18-test family and decision rule were **written down before any computation**, and
  corrected with **BH-FDR** across the whole family; this is what dissolved the tempting Monday false
  positive (significant in isolation, gone after the multiplicity tax).
- **Honest evaluation** — pre-registered thresholds, robustness across a neighborhood (not a menu
  to cherry-pick), and effect sizes read against an economically meaningful bar — never tuned to a win.

See the top-level [`README.md`](../README.md) for the full narrative and the confirmed-core results.
