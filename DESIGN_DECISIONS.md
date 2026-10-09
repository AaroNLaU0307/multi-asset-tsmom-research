# Design decisions & known objections

*A short briefing, not an essay — the strongest objections to this research, answered with the repo's
own evidence: plainly, with the number attached, caveats included. Grounded only in what the repo
already shows; nothing here is a new claim.*

---

## "The Sharpe CI lower bound is 0.29 — is this really an edge?"

Supported, but modest, and the CI width is the honest answer to "how modest." The **95% bootstrap
CI [0.29, 1.23]** on 218 months at 2 bps excludes 0 (99.95% of resamples > 0) — a materially
different statement from the earlier single-instrument SMC/breakout project, whose CI crossed zero.
The recorded status is **SUPPORTED — CI excludes 0; not independently confirmed**: no held-out or
independent confirmation exists yet (the prospective C-A test went live on 2026-09-13), and the CI
is not deflated, because the historical trial count for this panel is unknown
([`TRIAL_LEDGER`](research/extensions/TRIAL_LEDGER.md) §3.2). At the repo's "realistic" 5 bps the
figures are 0.70 [0.24, 1.18] (repo-reported; not reproducible from committed files). The lower
bound is only mildly positive, and 218 months ≈ one full regime cycle is limited statistical power.
"Supported but modest," not "large" or "confirmed," is the correct read — and that's how
[`STUDY_SUMMARY.md`](STUDY_SUMMARY.md) states it.

## "Why BH-FDR rather than Bonferroni?"

Bonferroni controls the probability of *any* false positive across the family (FWER) — the right tool
when a single false discovery would be catastrophic. Benjamini–Hochberg controls the *expected
proportion* of false discoveries among the rejections (FDR) — the right tool for a **mechanism map**: a
small, pre-registered family of individually-motivated hypotheses (18 seasonality cells, 6 yield-curve
cells, 5 XSMOM universes) where the goal is an honest map of what survives, not a single yes/no gate.
Bonferroni's power penalty at these family sizes would make it nearly impossible to detect a real effect
even if one existed — which would make the falsifications *artifacts of the correction*, not honest
negatives. The level is stated in each study's pre-registration: q = 0.10 for seasonality and the
yield curve, α = 0.05 for XSMOM (whose verdict is the same at 0.10: its smallest q is 0.357).

## "ETFs aren't futures — how much of this is proxy bias?"

Stated as a limitation, not hidden: commodity and currency ETFs carry roll/expense drag that a real
futures program wouldn't. It's called out explicitly where it matters most — the XSMOM commodities
universe (U4)'s ETFs "suffer roll/contango decay and are not clean proxies for the futures the literature
uses," and it's also the
*one* universe with the largest (still-falsified) point estimate, so the caveat is directly
load-bearing, not decorative. The honest scope: this is the supported edge **on liquid ETFs**, not a
claim about the futures market. [`STUDY_SUMMARY.md`](STUDY_SUMMARY.md)'s future-work section names true
futures data as the natural next step.

## "All four overlays failed — doesn't that mean your framework is broken?"

The opposite: a framework that can't reject anything isn't falsification-oriented, it's marketing. The
same machinery that **supported** the core (Sharpe CI excludes 0, every 4-year sub-period positive,
positive across 45 parameter combinations) also **rejected** four plausible-sounding extensions and a
parallel strategy — each at the *cheapest* stage, before a dollar of P&L was fit, each with a stated
mechanism (trigger anti-alignment and no directional premise, both descriptive comparisons with no
inference; nothing surviving BH-FDR for seasonality; no significant yield-curve cell; a +0.42
correlation with TSMOM for XSMOM). Premise-before-strategy gates exist precisely so most candidate
ideas die cheaply. Four overlays `not_promoted`, one parallel study `falsified` and one core
`supported`, reached by the same honest process, is the deliverable — not a defect in it.

## "Walk me through one thing your discipline caught that eyeballing would have missed."

Two, because they're different failure modes:
- **The Monday near-miss (seasonality).** In isolation, the Monday effect looked real — correct
  sign in all 6 scopes, Bond *p* = 0.026. But one raw *p* < 0.05 among 18 tests is about what noise
  alone produces, and 0.026 sits far above the BH rank-1 threshold (≈ 0.0056). The Bond cell also
  fails the pre-registered magnitude (3.4 < 5 bps/day) and stability gates, so the conjunction
  rejects it even before the correction; BH-FDR is the only binding gate for one cell, RealEstate
  Monday (*p* = 0.078). Eyeballing a "significant" *p* = 0.026 without the family context would
  have shipped a false discovery.
- **The yield-curve day count vs its episode count.** None of the 6 pre-registered cells was
  statistically significant (BH-FDR *p* 0.60–0.67; every bootstrap CI crosses zero) — a clean null with
  no claimable direction. But 2 of the 6 (both the 126-day horizon) cleared the 4%/yr economic-magnitude
  bar on the raw full sample despite being insignificant — exactly the kind of point estimate that
  invites over-reading. The episode analysis puts it in proportion: the tested flat state has only
  12–13 episodes, and dropping the 2022-24 one keeps 26–68% of the tilt but takes those two cells below
  the bar. The jackknife's binding-episode rule was changed after the first run (under the registered
  rule 3 of 6 cells pass it), so what carries the null is BH-FDR
  ([`research/ERRATA_2026-09-27.md`](research/ERRATA_2026-09-27.md) §1–2). ~4,800 trading days are not
  ~4,800 independent observations when the state itself changed only about a dozen times — the day
  count alone would have overstated the evidence.

## "What would make you abandon the supported core?"

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

The selection criterion was independence, not performance, but it was a correlation screen plus
discretionary trims, not a single mechanical rule. A daily-return correlation matrix + hierarchical
clustering and a greedy `|r| ≥ 0.80` filter removed redundant proxies for the same factor (e.g.
QQQ/XLK/IWM/XLF/EFA are 0.85–0.93 correlated with SPY). XLV (0.79 with SPY), GDX (0.77) and SLV (0.79,
both with GLD) were then dropped by judgement *below* that threshold, and CPER/WEAT/CORN for their
post-2008 inceptions. All three lists are in [`universe.py`](universe.py). The screening outputs are
git-ignored and the history before the first commit is squashed, so the repo cannot show that the
screen preceded the first backtest.

---

*This document makes no claims the rest of the repo doesn't already make. If a question above sends
you looking for the underlying number and it isn't where this doc says it is, that's a bug in this
doc, not a new finding.*
