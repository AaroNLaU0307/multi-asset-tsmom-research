# Yield-curve slope as a macro-regime conditioner — Step-1 PREMISE results

**VERDICT: NOT CONFIRMED — clean negative. STOP; do not build the overlay.**
0/6 cells confirmed; **0/6 pass the decisive event-level jackknife.** This is the **4th** overlay in
the arc to fail at premise (after crash-defense, vol-breakout, seasonality).

Pre-registered in [`PREREGISTRATION.md`](PREREGISTRATION.md) (contract committed `3378fad`, clarifications
`0d3c4ae`) **before** any slope×TSMOM result. Descriptive only — no positions, no P&L, no tuning.

- **Sample:** confirmed full-17 TSMOM **daily gross** returns, **2008-04-30 → 2026-06-12 (n = 4,559)**
  (restricted to the validated full-universe window, `dec["first_full"]`); curve state on the 4,820-day
  ETF calendar with causal past-only ffill; state used at **t−1**.
- **Effect everywhere is a weak NEGATIVE** Δ (flat→*lower* forward TSMOM — the H− "transition-whipsaw"
  direction, not H+ crisis-alpha), magnitude −1.9% to −4.9%/yr.

---

## 1. The decisive gate — episode jackknife (ranked ABOVE significance)

**The weak negative tilt is carried by the single 2022-24 inversion episode.** In every cell the
**binding (most-weakening) episode is the 2022-24 run**; dropping it collapses Δ far below the 4%/yr
bar. Dropping the *largest-by-size* flat episode instead (the 2017-2020 flattening, n≈710-760)
*strengthens* Δ — because that stretch had a **~zero standalone effect** (`delta_alone ≈ 0`). The
negative is concentrated in one episode, not broad-based. **pass_jackknife = False for all 6.**

| spread | h | full Δ (%/yr) | drop **2022-24** → Δ | drop largest (2017-20) → Δ | pass_jackknife |
|---|---|---|---|---|---|
| 10Y-3M | 21 | −1.91 | **−0.50** | −3.51 | ❌ |
| 10Y-3M | 63 | −3.09 | **−1.49** | −5.46 | ❌ |
| 10Y-3M | 126 | −4.61 | **−3.16** | −6.83 | ❌ |
| 10Y-2Y | 21 | −2.66 | **−1.62** | −3.71 | ❌ |
| 10Y-2Y | 63 | −3.54 | **−1.71** | −5.34 | ❌ |
| 10Y-2Y | 126 | −4.87 | **−2.94** | −7.05 | ❌ |

Even the two cells that clear the magnitude bar on the full sample (h=126: −4.61, −4.87) fall to
−3.16 / −2.94 %/yr — below 4%/yr — once the 2022-24 episode is removed. This is exactly the
event-sparsity artifact the pre-registration was built to catch.

*(≥2-episode presence "passes" superficially — 8-10 of 12-13 episodes share the negative sign — but
those same-sign episodes are mostly tiny/noisy and the **magnitude** lives in 2022-24. The binding
jackknife, which tests magnitude-dependence, is the correct decisive test, and it fails.)*

---

## 2. Primary family (tercile flat-vs-steep state, t−1) — significance also fails

BH-FDR q=0.10 across all 6 cells. **Nothing is remotely significant** and most cells are sub-magnitude.

| spread | h | Δ ann | p_raw | **p_FDR** | FDR reject | mag ≥4%? | CI excl. 0? |
|---|---|---|---|---|---|---|---|
| 10Y-3M | 21 | −0.0191 | 0.673 | 0.673 | no | no | no |
| 10Y-3M | 63 | −0.0309 | 0.467 | 0.616 | no | no | no |
| 10Y-3M | 126 | −0.0461 | 0.201 | 0.602 | no | **yes** | no |
| 10Y-2Y | 21 | −0.0266 | 0.513 | 0.616 | no | no | no |
| 10Y-2Y | 63 | −0.0354 | 0.357 | 0.616 | no | no | no |
| 10Y-2Y | 126 | −0.0487 | 0.176 | 0.602 | no | **yes** | no |

p_FDR ∈ [0.60, 0.67] — an order of magnitude from the 0.10 gate; every block-bootstrap CI on Δ
crosses zero. Gate 1 fails decisively on its own.

## 3. Robustness — raw `slope<0` inversion (binary) · *flatness ≠ inversion*

Same negative direction, all insignificant (p 0.18–0.80, every CI crosses 0). Since the **tercile
primary did not confirm**, the locked clarification-1 "flatness-not-inversion" reporting rule is moot —
neither the continuous-flatness nor the raw-inversion proposition is supported.

| spread | h | Δ ann | p_raw | CI excl. 0? |
|---|---|---|---|---|
| 10Y-3M | 21 / 63 / 126 | −0.029 / −0.022 / −0.011 | 0.60 / 0.66 / 0.80 | no / no / no |
| 10Y-2Y | 21 / 63 / 126 | −0.041 / −0.050 / −0.071 | 0.57 / 0.41 / 0.18 | no / no / no |

## 4. Confound diagnostics (contemporaneous vs forward vs t+21 skip, annualized)

For 10Y-3M the **contemporaneous** Δ (−0.041 / −0.053 / −0.061) exceeds the **forward** Δ in magnitude —
consistent with a co-movement component rather than prediction. The t+21 forward-skip keeps the sign,
so a faint predictive residual cannot be ruled out — but per the contract the episode jackknife is the
arbiter, and it shows the residual is the 2022-24 co-occurrence. Confound not separable from a clean
predictive edge → no support.

---

## 5. Method notes & honest disclosures

- **Jackknife definition correction (disclosed).** The contract §3b literally said "most influential =
  largest |ΔΔ|". On first run that selected an episode whose removal *strengthened* Δ (the near-zero
  2017-20 stretch), yielding a misleading "pass". I corrected the operationalization to **the episode
  whose removal most *weakens* the effect** (worst-case; matches clarification 2's explicit "drop the
  2022-24 episode" intent). The correction is **stricter** and the verdict is **unchanged** (0/6 either
  way; significance fails regardless). The locked contract is left as the timestamped record; this
  correction is noted here, not retro-edited into it.
- **Window fidelity.** Restricted to the confirmed full-17 strategy returns (post `first_full`,
  2008-04-30), which also correctly drops the **2007 inversion** (it predates the strategy).
- **Reuse:** HAC t-test (`seasonality.hac_diff_test`, lag=h), moving-block bootstrap
  (`block_bootstrap_ci`, block=h), `bh_fdr`; causal state via `regime._trailing_pctile`. Overlapping
  forward windows / mid-tercile gaps make the CI/HAC approximate, but the verdict is nowhere near the
  margins.
- Artifacts: [`yield_spread_premise_family.csv`](yield_spread_premise_family.csv),
  [`yield_spread_episodes.csv`](yield_spread_episodes.csv). Deterministic (seed 7).

## 6. Conclusion

The orthogonality premise was appealing — a rates-term-structure signal is not a function of the ETF
price paths — but the in-sample evidence does **not** support that the curve-slope regime predicts
forward TSMOM returns. The apparent weak negative tilt is **statistically indistinguishable from
zero**, mostly **sub-magnitude**, and **dependent on the single 2022-24 episode** (collapses when it is
dropped). Per the contract: **clean negative, STOP — do not build the overlay.** Overlay #4 falsified
at premise; the arc's honest-falsification record holds.
