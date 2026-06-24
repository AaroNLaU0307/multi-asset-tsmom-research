# Phase 1B — Premise test: does vol compression precede directional expansion?

*DESCRIPTIVE only — no positions, no P&L, no tuning. Conditioning (compression) is strictly point-in-time; the outcome window is forward-looking by design. Pre-registered headline threshold = **0.20**; 0.10/0.30 are a robustness sanity check, NOT a menu.*

## Scope of claim (data constraint)

The data is adjusted-**close-only** (no intraday H/L), so compression here is **close-to-close realized-vol percentile, NOT a true intraday ATR squeeze**. The premise tested is precisely: *does close-to-close vol compression precede directional expansion?* The conclusion does **not** generalize to an intraday-ATR squeeze (which would need OHLC data).

## Decisive metric — follow-through quality & efficiency, conditional vs base rate

After compression the Donchian channel is narrow, so breakouts are mechanically easier; the decisive question is whether those breakouts **follow through** (genuine) or **reverse** (false), and whether the post-move is **directional** (efficiency ratio). Both compared to the unconditional base rate.

### Pooled @ threshold 0.20

| horizon | n_comp | breakout rate (comp/base) | follow-through\|breakout (comp/base/Δ) | efficiency ratio (comp/base/Δ) | vol expansion (comp) |
| --- | --- | --- | --- | --- | --- |
| 5d | 23862 | 0.67 / 0.60 | 0.713 / 0.712 / **+0.001** | 0.46 / 0.45 / **+0.007** | 1.44x |
| 10d | 23850 | 0.83 / 0.76 | 0.680 / 0.668 / **+0.011** | 0.32 / 0.32 / **+0.004** | 1.31x |
| 20d | 23848 | 0.94 / 0.90 | 0.689 / 0.669 / **+0.020** | 0.23 / 0.23 / **+0.000** | 1.29x |

### Per sleeve @ threshold 0.20, horizon 10d

| sleeve | n_comp | follow-through\|breakout (comp/base/Δ) | efficiency ratio (comp/base/Δ) | directional edge? |
| --- | --- | --- | --- | --- |
| Pooled | 23850 | 0.680 / 0.668 / **+0.011** | 0.32 / 0.32 / **+0.004** | no |
| Equity | 8250 | 0.684 / 0.666 / **+0.018** | 0.31 / 0.31 / **+0.003** | no |
| Bond | 6022 | 0.680 / 0.685 / **-0.005** | 0.32 / 0.32 / **-0.002** | no |
| Commodity | 4568 | 0.671 / 0.655 / **+0.016** | 0.34 / 0.33 / **+0.016** | no |
| FX | 2448 | 0.672 / 0.663 / **+0.009** | 0.33 / 0.32 / **+0.012** | no |
| RealEstate | 2562 | 0.689 / 0.670 / **+0.018** | 0.31 / 0.32 / **-0.006** | no |

### Robustness (NOT optimization) — pooled decisive deltas across thresholds

| threshold | horizon | follow-through\|breakout Δ | efficiency ratio Δ |
| --- | --- | --- | --- |
| 0.10 | 5d | +0.005 | +0.008 |
| 0.10 | 10d | +0.009 | +0.003 |
| 0.10 | 20d | +0.023 | -0.003 |
| 0.20 | 5d | +0.001 | +0.007 |
| 0.20 | 10d | +0.011 | +0.004 |
| 0.20 | 20d | +0.020 | +0.000 |
| 0.30 | 5d | +0.001 | +0.006 |
| 0.30 | 10d | +0.009 | +0.003 |
| 0.30 | 20d | +0.019 | +0.002 |

## Verdict

- **Vol expansion** after compression: present (pooled forward/trailing vol ~ 1.31× — the robust, expected part; vol clusters/mean-reverts as expected).
- **Directional follow-through MEANINGFULLY above base rate** (the decisive part; bar = +0.02 on BOTH the artifact-free measures, efficiency ratio and follow-through-given-breakout): pooled **NO** (ER Δ +0.004, ft|breakout Δ +0.011); sleeves clearing the bar: **none**.
- **Read the numbers honestly:** the post-compression efficiency ratio is **≈ identical to baseline** (Δ ~0.00–0.02), and follow-through *quality* given a breakout is up only ~1pp on a ~67% base (Bond/RealEstate are flat-to-negative). The one sizeable positive — `genuine_ft_delta` ~+0.05 — is the **mechanical narrow-channel artifact** (low vol ⇒ tight Donchian channel ⇒ more breakouts in either direction), which carries no directional information. The deltas also **do not strengthen at tighter compression** (0.10 ≈ 0.20 ≈ 0.30) — the signature of a real effect is absent.
- **Premise NOT confirmed** for close-to-close compression on this universe.

Compression precedes a vol expansion, but that expansion is **not directional beyond the base rate** — post-compression breakouts follow through at essentially the same rate as any breakout, and the move is no more efficient. The apparent 'edge' is a narrow-channel counting artifact. Per the gate this is a **clean negative**: do **not** build the strategy on close-to-close compression. (Scope: this does not test an intraday-ATR squeeze, which would require OHLC data — a separate question the current data cannot answer.)