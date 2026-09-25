# Round 2 — free long-history inventory, and the Round-2 recommendation

**Date:** 2026-09-26.
**Builder:** Opus 5.5, under the research-mode mandate.
**Approved as method by:** DL-010.
**Scope:** a desk inventory only. No dataset was downloaded, no account was used, and no
performance figure from any source or paper was read into this record.

**Evidence classes:**
- Source facts come from a read-only web survey run by a subagent. They are REASONED
  from documentation pages; tags there mark [V] (seen on the source page) against [U]
  (not verified).
- The MDE figures are REPRODUCED from `research/round2/r2_resolvability.py`.

## What exists, and what it could resolve

MDE is the minimum detectable annualized Sharpe, at 80% power and two-sided 5%.

| source | span | tradable returns? | MDE | integrity caveat | literature exposure |
|---|---|---|---|---|---|
| Jordà–Schularick–Taylor Macrohistory (18 countries, annual) | ~140 y excluding war gaps | yes: annual total returns for equity, bonds and bills; FX | **0.24** | annual frequency only; reconstructed and revised between releases; CC BY-NC-SA | macro-finance use is heavy (returns on everything, credit-boom predictability) |
| Fed Gürkaynak–Sack–Wright yield curve (daily) | 1961–, ~65 y | constructible zero-coupon returns | 0.36 | fitted and smoothed curves; off-the-run only; revisable. Smoothing can flatter trend | bond carry and term premium are published |
| BIS policy rates (40+ economies) | 1946–, ~80 y | no: rates and decision dates only | 0.32 if returns are paired | instruments spliced within a series; returns need other long daily sources, which are not free | pre-announcement drift is published |
| NBER Macrohistory, pre-1914 money markets plus MeasuringWorth FX and gold | ~38 y | no: levels; returns must be constructed | 0.46 | mixed 19th-century sources; static archive; unknown trading realism | lightly exposed |
| CFTC Commitments of Traders | 1986–, ~40 y | no: positioning only | 0.45 | pre-1992 data errors; trader reclassification | hedging-pressure literature |
| Kenneth French, Shiller | 1926–, 1871– | French: US equity only. Shiller: monthly-averaged levels | — | Shiller's averaging creates autocorrelation, fatal for trend tests; French history is rebuilt at each update | saturated |
| AQR TSMOM, AQR Century of Factor Premia, AQR Commodities for the Long Run, Baltussen et al. | 1877– to 1985– | published **strategy outcomes** | — | these are outcomes, not raw data | **fully exposed** for trend, momentum, carry and value |
| Global Financial Data, Dimson–Marsh–Staunton, CRB | long | yes | — | — | paid, so an Owner gate |

## Assessment

1. **The classic CTA families are already tested over a century.** Trend, carry, value
   and momentum have been run across asset classes on 100-plus-year histories, and the
   results are published (AQR, Baltussen et al.). A long-history test of these families
   is a test on seen outcomes. By this project's own lockbox rules, outcome-informed
   market knowledge counts as exposure, so it cannot yield a claim above `supported`.
   It would also not be a new question (anti-revival).
2. **The one free asset that moves resolvability materially is JST.** Its MDE of about
   0.24 is roughly a third of the current panel's 0.67. But it is **annual**, so only
   mechanisms defined at an annual horizon qualify. Its known predictors (credit growth,
   housing, valuation) are heavily published.
3. **Everything else either stops short or is not tradable.** GSW, BIS, NBER pre-1914
   and COT give MDEs of 0.32–0.46, still above plausible edge sizes of 0.2–0.4. Several
   also give no tradable return, or give smoothed or constructed returns whose realism
   is uncertain.
4. **A genuinely new, resolvable mechanism test needs both a mechanism absent from the
   century-evidence literature and a long tradable span.** In free data, that
   intersection is nearly empty. Searching for a mechanism to fit the JST panel would
   invert the mandate's order (mechanism, then data) and invite hindsight selection.

## Recommendation (the decision is the delegate's)

**PARK Round 2 at a programme-level identifiability ceiling.** Disposition:
`PARKED_PRE_OUTCOME`. No trial is spent and no outcome touched.

Revival conditions, each of which would be a new S0:

- **(a)** A specific mechanism, argued a priori and absent from the century-evidence
  literature, whose natural horizon is annual. It would be tested on JST with its prior
  exposure disclosed. The data is free, so acquiring it is the delegate's gate.
- **(b)** Aaron funds long-history futures data (Global Financial Data, CSI or
  Databento pre-2010 roots), taking the MDE to about 0.4 or better. That is his
  spending gate.
- **(c)** A prospective lineage is opened with an honest horizon. At 10 years forward
  the MDE is about 0.91, so it confirms only large effects.

Unchanged: canonical TSMOM stays "SUPPORTED — NOT INDEPENDENTLY CONFIRMED". No Round-1
verdict is reinterpreted.
