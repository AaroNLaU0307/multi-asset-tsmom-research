# Seasonality — Step 1 premise test (descriptive)

*DESCRIPTIVE only — mean daily return on effect-days vs non-effect-days. No positions, no P&L, no tuning. Only the pre-registered effects ([`PREREGISTRATION.md`](PREREGISTRATION.md)) are tested; the family, the BH-FDR plan, the 5 bps/day magnitude bar, and the decision rule were all fixed before any computation.*

Balanced daily window **2007-04-19 → 2026-06-12** (4819 trading days, equal-weight over the 17 always-present assets). Primary p-value = Newey–West HAC *t* (lag 10); cross-check = moving-block bootstrap 95% CI (block 10, 10,000 resamples, seed 7). **BH-FDR q = 0.1** across all 18 cells.

## Family results (Δ in bps/day; raw vs FDR-adjusted)

| effect | scope | Δ bps | HAC t | p_raw | p_BH | FDR sig? | |Δ|≥bar | stable | not-conc | **verdict** |
| --- | --- | ---: | ---: | ---: | ---: | :--: | :--: | :--: | :--: | :--: |
| E1_TOM | Pooled | +1.35 | +0.58 | 0.561 | 0.776 | · | · | Y | · | no |
| E1_TOM | Equity | +0.55 | +0.14 | 0.892 | 0.944 | · | · | · | · | no |
| E1_TOM | Bond | +1.11 | +0.72 | 0.469 | 0.767 | · | · | Y | · | no |
| E1_TOM | Commodity | +1.53 | +0.31 | 0.755 | 0.944 | · | · | · | · | no |
| E1_TOM | FX | +0.15 | +0.14 | 0.888 | 0.944 | · | · | · | · | no |
| E1_TOM | RealEstate | +4.71 | +0.97 | 0.331 | 0.694 | · | · | Y | Y | no |
| E2_Halloween | Pooled | +1.66 | +0.88 | 0.380 | 0.694 | · | · | Y | · | no |
| E2_Halloween | Equity | +3.55 | +1.13 | 0.258 | 0.694 | · | · | Y | · | no |
| E2_Halloween | Bond | +0.70 | +0.61 | 0.540 | 0.776 | · | · | · | · | no |
| E2_Halloween | Commodity | +0.12 | +0.03 | 0.974 | 0.974 | · | · | · | · | no |
| E2_Halloween | FX | -1.06 | -1.25 | 0.210 | 0.694 | · | · | · | · | no |
| E2_Halloween | RealEstate | +4.66 | +1.17 | 0.243 | 0.694 | · | · | Y | · | no |
| E3_Monday | Pooled | -4.39 | -1.56 | 0.118 | 0.694 | · | · | Y | Y | no |
| E3_Monday | Equity | -4.63 | -0.87 | 0.385 | 0.694 | · | · | Y | Y | no |
| E3_Monday | Bond | -3.41 | -2.22 | 0.026 | 0.476 | · | · | · | Y | no |
| E3_Monday | Commodity | -4.25 | -0.88 | 0.378 | 0.694 | · | · | · | Y | no |
| E3_Monday | FX | -0.16 | -0.15 | 0.883 | 0.944 | · | · | · | · | no |
| E3_Monday | RealEstate | -10.28 | -1.76 | 0.078 | 0.694 | · | Y | Y | Y | no |

## E1 Turn-of-Month — prior: TOM > non-TOM (+)

Sub-period stability (Δ bps/day) and daily concentration check:

| scope | Δ full | H1 | H2 | T1 | T2 | T3 | Δ winsor | top-1 day share | FDR sig? |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--: |
| Pooled | +1.35 | +0.49 | +2.22 | +4.27 | -4.41 | +4.15 | +1.35 | -0.36 | · |
| Equity | +0.55 | -0.77 | +1.88 | +4.64 | -6.06 | +3.01 | +1.23 | -1.66 | · |
| Bond | +1.11 | +0.02 | +2.19 | +2.33 | -1.55 | +2.52 | +0.76 | +0.25 | · |
| Commodity | +1.53 | -0.35 | +3.44 | +3.82 | -8.88 | +9.55 | +1.79 | -0.60 | · |
| FX | +0.15 | -0.85 | +1.15 | -2.79 | +1.53 | +1.72 | +0.33 | +1.11 | · |
| RealEstate | +4.71 | +7.62 | +1.79 | +15.21 | -3.03 | +1.89 | +4.97 | -0.32 | · |

- **Pooled**: not confirmed — fails BH-FDR, |Δ|=1.4<5 bps, concentration-driven.
- **Equity**: not confirmed — fails BH-FDR, |Δ|=0.5<5 bps, unstable, concentration-driven.
- **Bond**: not confirmed — fails BH-FDR, |Δ|=1.1<5 bps, concentration-driven.
- **Commodity**: not confirmed — fails BH-FDR, |Δ|=1.5<5 bps, unstable, concentration-driven.
- **FX**: not confirmed — fails BH-FDR, |Δ|=0.2<5 bps, unstable, concentration-driven.
- **RealEstate**: not confirmed — fails BH-FDR, |Δ|=4.7<5 bps.

## E2 Halloween/Sell-in-May — prior: winter > summer (+)

Year-level stability (per-year winter−summer sign count) and year jackknife (Δ bps/day) — *inherently low-powered: ~19 annual cycles*:

| scope | Δ full | yrs +/total | LOO min (yr) | LOO max (yr) | drop top-2 yrs | FDR sig? |
| --- | ---: | :--: | ---: | ---: | ---: | :--: |
| Pooled | +1.66 | 12/20 | +0.34 (2008) | +2.39 (2009) | -0.14 | · |
| Equity | +3.55 | 12/20 | +2.16 (2008) | +4.40 (2025) | +2.83 | · |
| Bond | +0.70 | 9/20 | -0.31 (2008) | +1.26 (2009) | -1.38 | · |
| Commodity | +0.12 | 10/20 | -1.87 (2008) | +2.51 (2020) | +1.22 | · |
| FX | -1.06 | 10/20 | -1.25 (2015) | -0.77 (2012) | -0.45 | · |
| RealEstate | +4.66 | 15/20 | +2.64 (2008) | +6.09 (2024) | +1.15 | · |

- **Pooled**: not confirmed — fails BH-FDR, |Δ|=1.7<5 bps, concentration-driven.
- **Equity**: not confirmed — fails BH-FDR, |Δ|=3.6<5 bps, concentration-driven.
- **Bond**: not confirmed — fails BH-FDR, |Δ|=0.7<5 bps, unstable, concentration-driven.
- **Commodity**: not confirmed — fails BH-FDR, |Δ|=0.1<5 bps, unstable, concentration-driven.
- **FX**: not confirmed — fails BH-FDR, sign opposes prior, |Δ|=1.1<5 bps, unstable, concentration-driven.
- **RealEstate**: not confirmed — fails BH-FDR, |Δ|=4.7<5 bps, concentration-driven.

## E3 Monday — prior: Monday < rest (-)

Sub-period stability (Δ bps/day) and daily concentration check:

| scope | Δ full | H1 | H2 | T1 | T2 | T3 | Δ winsor | top-1 day share | FDR sig? |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--: |
| Pooled | -4.39 | -4.52 | -4.27 | -2.11 | -7.65 | -3.41 | -3.65 | -0.16 | · |
| Equity | -4.63 | -5.70 | -3.55 | -5.54 | -5.91 | -2.42 | -3.87 | -0.35 | · |
| Bond | -3.41 | +0.79 | -7.62 | +3.99 | -3.82 | -10.42 | -3.36 | -0.12 | · |
| Commodity | -4.25 | -8.50 | -0.01 | +0.72 | -19.63 | +6.15 | -3.06 | +0.20 | · |
| FX | -0.16 | +3.08 | -3.40 | +5.54 | -1.28 | -4.76 | -0.43 | -1.51 | · |
| RealEstate | -10.28 | -11.83 | -8.74 | -19.09 | -2.10 | -9.65 | -7.33 | +0.13 | · |

- **Pooled**: not confirmed — fails BH-FDR, |Δ|=4.4<5 bps.
- **Equity**: not confirmed — fails BH-FDR, |Δ|=4.6<5 bps.
- **Bond**: not confirmed — fails BH-FDR, |Δ|=3.4<5 bps, unstable.
- **Commodity**: not confirmed — fails BH-FDR, |Δ|=4.3<5 bps, unstable.
- **FX**: not confirmed — fails BH-FDR, |Δ|=0.2<5 bps, unstable, concentration-driven.
- **RealEstate**: not confirmed — fails BH-FDR.

## Overall verdict

**NOT confirmed — clean negative.** Of 18 pre-registered cells, 0 survive BH-FDR and 1 clear the 5 bps/day magnitude bar, but **0** clear all five gates jointly (FDR **and** sign **and** magnitude **and** stability **and** non-concentration). Per the pre-registered decision rule this is a clean negative — consistent with the portfolio's honest-falsification record. **Do not build the overlay.** No Step 2.
