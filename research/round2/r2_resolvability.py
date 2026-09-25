"""Round-2 resolvability arithmetic: what can the programme's samples resolve?

Pure arithmetic: reads no data, computes no strategy returns, touches no outcome.
Reproduce with:  python research/round2/r2_resolvability.py

Sharpe-ratio standard error for iid returns (Lo 2002), annualized, over T years:
    SE(SR) ~= sqrt((1 + SR^2 / 2) / T)
The standard error depends on calendar span, not on sampling frequency, so daily or
event-level data does not shrink it for a given span. Serial correlation only widens it.
The minimum detectable effect at two-sided alpha 0.05 and power 0.80 is
    MDE ~= (1.96 + 0.84) * SE.
For a pooled cross-instrument test of a per-instrument predictive effect, N
instruments with average pairwise correlation rho carry an effective breadth of
    N_eff = N / (1 + (N - 1) * rho).
"""
import math

Z = 1.96 + 0.8416          # two-sided 5%, 80% power

SPANS = {                  # calendar years, from the project's own records
    "ETF panel, 17-asset common window 2008-05..2026-06": 218 / 12,
    "ETF panel, longest single series 1993-01..2026-06": 33.4,
    "Databento commodity panel 2010-06..2026-06": 16.0,
    "Cboe VX settlement chain 2004-03..2026-09": 22.5,
    "a new forward (T4) window after 5 years": 5.0,
    "a new forward (T4) window after 10 years": 10.0,
}


def se(sr, years):
    return math.sqrt((1 + sr * sr / 2) / years)


def mde(years, sr_guess=0.3):
    return Z * se(sr_guess, years)


def years_needed(sr):
    return Z * Z * (1 + sr * sr / 2) / (sr * sr)


def n_eff(n, rho):
    return n / (1 + (n - 1) * rho)


if __name__ == "__main__":
    print("MDE (annualized Sharpe, 80% power, two-sided 5%) by span:")
    for name, t in SPANS.items():
        print(f"  {name:55s} T={t:5.1f}y  SE={se(0.3, t):.3f}  MDE={mde(t):.2f}")
    print("\nYears of data needed to detect a true Sharpe at 80% power:")
    for sr in (0.2, 0.3, 0.4, 0.5, 0.7, 1.0):
        print(f"  SR={sr:.1f}: {years_needed(sr):6.1f} years")
    print("\nTo exclude a material edge SR>=0.30 (one-sided 5%) over the ETF window,")
    t = 218 / 12
    print(f"  the point estimate must be <= {0.30 - 1.645 * se(0.0, t):.2f}")
    print("\nEffective breadth for pooled per-instrument tests (N=18 commodity roots).")
    print("  This sharpens the PER-INSTRUMENT effect only. A diversified portfolio's Sharpe")
    print("  already embeds the same breadth, so pooling is no escape from the span limit:")
    for rho in (0.0, 0.1, 0.2, 0.3, 0.5):
        ne = n_eff(18, rho)
        print(f"  rho={rho:.1f}: N_eff={ne:5.2f}  SE shrink factor={1 / math.sqrt(ne):.2f}")
