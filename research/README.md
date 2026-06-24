# Research arc — the three investigations

This folder holds the **committed write-ups** of the research arc around the confirmed
multi-asset TSMOM core: one diagnostic and two falsified overlays. The reports and figures
here are snapshots — the code lives at the repo root / `src/` (kept there so imports stay
clean), and re-running the scripts regenerates the live copies under `output/` (git-ignored).

The two falsifications are **first-class results**, not discarded experiments: the value of
this project is the honest *confirmed → falsified* arc, each negative reached at the cheapest
stage with a mechanism explanation.

| # | Investigation | Verdict | Report | Code (repo root / `src/`) | Reproduce |
|---|---|---|---|---|---|
| 1 | **Drawdown attribution diagnostic** | drawdowns are crash-type, multi-sleeve, in ordinary-vol / low-correlation regimes | [`diagnostic/DRAWDOWN_ATTRIBUTION_REPORT.md`](diagnostic/DRAWDOWN_ATTRIBUTION_REPORT.md) | `run_drawdown_attribution.py`, `src/attribution.py`, `src/regime.py` | `python run_drawdown_attribution.py` |
| 2 | **Crash-defense overlay** | **FALSIFIED** at Phase 0 — systemic-risk trigger anti-aligned (fires in 2008/2020 profit windows, silent in real drawdowns) | [`crash_defense/PHASE0_SYSTEMIC_VERIFICATION.md`](crash_defense/PHASE0_SYSTEMIC_VERIFICATION.md) | `verify_systemic.py`, `src/attribution.py`, `src/regime.py` | `python verify_systemic.py` |
| 3 | **Vol-compression breakout overlay** | **FALSIFIED** at Phase 1B — close-to-close compression precedes vol expansion but **not** directional follow-through; apparent edge was a narrow-channel artifact | [`vol_breakout/BREAKOUT_PHASE1A_INFRA.md`](vol_breakout/BREAKOUT_PHASE1A_INFRA.md) (infra), [`vol_breakout/BREAKOUT_PHASE1B_PREMISE.md`](vol_breakout/BREAKOUT_PHASE1B_PREMISE.md) (premise) | `run_breakout_phase1a.py`, `run_breakout_phase1b.py`, `src/daily.py`, `src/premise.py` | `python run_breakout_phase1a.py` → `python run_breakout_phase1b.py` |

## Method spine (shared by all three)
- **Reuse, not re-derivation** — every investigation reuses the *exact* vol-scaled positions /
  data of the validated monthly engine and **reconciles** before attributing (diagnostic
  reconciled to 3.5e-18; daily infra reconciles to the monthly engine at 1.3e-15).
- **No look-ahead, proven by tests** — point-in-time primitives with truncation-invariance unit
  tests; the descriptive episode labels are flagged as full-sample, the *reusable* regime
  variables are strictly causal.
- **Premise before strategy** — overlays are gated: verify the premise exists (cheap, read-only)
  before building anything. Both overlays were killed at the premise gate, before any P&L fitting.
- **Honest evaluation** — pre-registered thresholds, robustness across a neighborhood (not a menu
  to cherry-pick), and effect sizes read against an economically meaningful bar — never tuned to a win.

See the top-level [`README.md`](../README.md) for the full narrative and the confirmed-core results.
