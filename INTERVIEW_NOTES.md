# Design decisions & anticipated questions

*A short briefing, not an essay — the questions a sharp interviewer would actually ask, answered the
same way the rest of this repo reports results: plainly, with the number attached, caveats included.
Grounded only in what the repo already shows; nothing here is a new claim.*

---

## "The Sharpe CI lower bound is 0.29 — is this really an edge?"

Yes, but a modest one, and the CI width is the honest answer to "how modest." **95% bootstrap CI
[0.29, 1.23]** on 218 months of data means the edge is *confirmable* at the 95% level (100% of
resamples > 0) — a materially different statement from the earlier single-instrument SMC/breakout
project, whose CI crossed zero. It is not a strong claim: the lower bound (0.29) is only mildly
positive, and 218 months ≈ one full regime cycle is limited statistical power. "Confirmable but
modest," not "large," is the correct read — and that's exactly how [`STUDY_SUMMARY.md`](STUDY_SUMMARY.md)
states it.

## "Why BH-FDR rather than Bonferroni?"

Bonferroni controls the probability of *any* false positive across the family (FWER) — the right tool
when a single false discovery would be catastrophic. Benjamini–Hochberg controls the *expected
proportion* of false discoveries among the rejections (FDR) — the right tool for a **mechanism map**: a
small, pre-registered family of individually-motivated hypotheses (18 seasonality cells, 6 yield-curve
cells, 5 XSMOM universes) where the goal is an honest map of what survives, not a single yes/no gate.
Bonferroni's power penalty at these family sizes would make it nearly impossible to detect a real effect
even if one existed — which would make the falsifications *artifacts of the correction*, not honest
negatives. BH-FDR at q = 0.10 is disclosed up front in every pre-registration, not chosen after seeing
results.

## "ETFs aren't futures — how much of this is proxy bias?"

Stated as a limitation, not hidden: commodity and currency ETFs carry roll/expense drag that a real
futures program wouldn't. It's called out explicitly where it matters most — the XSMOM commodities
universe (U4) is flagged as "not a clean proxy for the futures the literature uses," and it's also the
*one* universe with the largest (still-falsified) point estimate, so the caveat is directly
load-bearing, not decorative. The honest scope: this is the confirmable edge **on liquid ETFs**, not a
claim about the futures market. [`STUDY_SUMMARY.md`](STUDY_SUMMARY.md)'s future-work section names true
futures data as the natural next step.

## "All four overlays failed — doesn't that mean your framework is broken?"

The opposite: a framework that can't reject anything isn't falsification-oriented, it's marketing. The
same machinery that **confirmed** the core (Sharpe CI excludes 0, walk-forward stable, robust across 45
parameter combinations) also **rejected** four plausible-sounding extensions and a parallel strategy —
each at the *cheapest* stage, before a dollar of P&L was fit, each with a stated mechanism (trigger
anti-alignment, no directional premise, BH-FDR multiplicity, single-episode illusion, same-source
correlation). Premise-before-strategy gates exist precisely so most candidate ideas die cheaply. Five
falsifications and one confirmation, reached by the same honest process, is the deliverable — not a
defect in it.

## "Walk me through one thing your discipline caught that eyeballing would have missed."

Two, because they're different failure modes:
- **The Monday false positive (seasonality).** In isolation, the Monday effect looked real — correct
  sign in all 6 scopes, Bond *p* = 0.026. But the smallest raw *p* in the 18-cell family (0.026) sits far
  above the BH rank-1 threshold (≈ 0.0056), so it evaporates under the pre-registered multiplicity
  correction. Eyeballing a "significant" *p* = 0.026 without the family context would have shipped a
  false discovery.
- **The yield-curve single-episode illusion.** The tercile-state effect looked directionally consistent
  and even cleared the magnitude bar at longer horizons — but the **leave-one-episode-out jackknife**
  showed the whole effect was carried by the single 2022-24 inversion (97% of inverted 10Y-2Y days);
  dropping it collapsed the effect below the bar. ~4,800 trading days is not ~4,800 independent
  observations when the regime itself only transitioned a handful of times — the day count alone would
  have fooled a naive significance test.

## "What would make you abandon the confirmed core?"

Concretely, from what's already disclosed: (1) a **materially longer OOS sample whose Sharpe CI crosses
zero** — the current CI is wide precisely because 218 months is limited power, so this is the honest
kill test, not a hypothetical; (2) **realized costs migrating toward the ~20 bps zone** — the
cost-sensitivity sweep already shows the CI crosses 0 there ([−0.01, 0.92]), a pre-identified failure
boundary, not a new one; (3) **a walk-forward sub-period going meaningfully negative** — every block is
currently positive (0.58–1.06), and that stability is the actual claim; a broken block breaks it; (4)
**crisis alpha failing to appear in a new crisis** — the edge's most distinctive property is going short
and earning in 2008/2020-style regimes; if the next crisis doesn't show it, the mechanism claim, not
just the number, is wrong.

## "Why equal-weight instead of risk parity or mean-variance optimization?"

Tested as a control, not assumed: inverse-vol (0.78) and risk-parity/ERC (0.73) are statistically
**indistinguishable** from equal-weight (0.70) — all three CIs overlap heavily, and ERC's covariance
estimate is noisier for no measurable gain (consistent with DeMiguel–Garlappi–Uppal 2009: mean-variance
optimizers routinely lose to 1/N out of sample). Equal-weight on vol-scaled positions is already a naive
risk parity; adding a covariance estimate is complexity that doesn't pay for itself here. Control
experiment: [`rp_comparison.py`](rp_comparison.py).

## "Why lock the lookbacks instead of optimizing them?"

Because the entire lesson of the prior single-instrument project was that tuning manufactures in-sample
edges that vanish out of sample. The `{1,3,6,12}`-month TSMOM composite and the 12-1 XSMOM signal are
academic conventions, fixed before any result, not searched. The proof this isn't just a slogan: a
45-combination robustness sweep puts the locked default at the **71st percentile of Sharpe outcomes —
not the peak** (e.g. `{6,12}` alone scores 0.87 > the default's 0.75); and in XSMOM, the locked 12-1 is
explicitly the **weakest** of the 3/6/9/12 neighbourhood (0.28 vs 9-1's 0.51). Both facts are reported
even though picking the best-scoring variant would have looked better.

## "Isn't the 30→17 ETF universe selection itself a form of data snooping?"

The selection criterion was independence, not performance: a daily-return correlation matrix +
hierarchical clustering removed redundant proxies for the same factor (e.g. QQQ/XLK/IWM/EFA are
0.85–0.97 correlated with SPY) using a fixed threshold (`|r| ≥ 0.80`), decided before looking at any
backtest result. The one deliberately *costly* choice — trading WEAT/CORN/CPER for the 2008 sample —
went the **opposite** direction a snooper would: it was kept despite slightly weaker diversification,
specifically to preserve the hardest regime for a trend-follower to survive, not to flatter the number.

---

*This document makes no claims the rest of the repo doesn't already make. If a question above sends
you looking for the underlying number and it isn't where this doc says it is, that's a bug in this
doc, not a new finding.*
