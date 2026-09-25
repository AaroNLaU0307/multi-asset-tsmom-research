# Round 2, first finding: the binding constraint is sample span, not candidate supply

Date: 2026-09-26. Builder: Opus 5.5, working under the standing research-mode mandate
(`ops/MANDATE_2026-09-26_AGI_RESEARCH_MODE.md`). This is a pre-outcome desk result:

- no data was read and no strategy return was computed;
- no outcome of any candidate was seen;
- the frozen canonical benchmark's own historical results (already fully exposed) were
  not used.

To reproduce: `python research/round2/r2_resolvability.py`.

## Result

The programme's evidence assets were inventoried read-only on 2026-09-26. None of them
can support a performance claim above `supported`:

- every historical sample is T0 or T1;
- the post-boundary data is `UNKNOWN`, so no holdout can be verified;
- no forward (T4) clock is running.

Within that ceiling, a standalone Sharpe test resolves only large effects. Minimum
detectable annualized Sharpe (MDE), at 80% power and two-sided 5%:

| sample | span | MDE |
|---|---|---|
| ETF panel, 17-asset common window | 18.2 y | **0.67** |
| ETF panel, longest single series | 33.4 y | 0.50 |
| Databento commodity panel | 16.0 y | **0.72** |
| Cboe VX chain | 22.5 y | 0.60 |
| a new forward window after 10 years | 10 y | 0.91 |

Years of data needed to detect a true Sharpe at 80% power:

| true Sharpe | 0.2 | 0.3 | 0.4 | 0.5 | 0.7 |
|---|---|---|---|---|---|
| years needed | 200 | 91 | 53 | 35 | 20 |

The standard error depends on calendar span, not on sampling frequency. Daily or
event-level data does not shrink it for a given span.

Breadth does not help either. Pooling instruments sharpens a per-instrument effect, but
the diversified portfolio's Sharpe already contains that breadth. For the economic
claim, span is the binding constraint.

## What this explains

A plausible new standalone CTA / macro edge, after costs, is roughly Sharpe 0.2–0.4.
Such an edge is **unidentifiable** on any sample the programme holds.

Exclusion is just as weak. Ruling out a material edge (SR ≥ 0.30) over the ETF window
needs a point estimate of −0.09 or lower. Even a true null misses that bar about 65% of
the time, so a null candidate will usually return `unresolved`.

Round 1's three evaluations all returned `unresolved`. That is what this arithmetic
predicts. It reflects the design, not bad luck or poor candidates. I did not verify
whether each Round-1 prereg computed an MDE, and nothing here reinterprets any Round-1
verdict.

## Consequence for Round 2

More candidates of the Round-1 type — a standalone edge, a historical sample, a
portfolio-Sharpe gate — would mostly produce `unresolved` results. They would also add
multiple-testing burden on a panel whose trial count cannot be stated (`D-ETF-COUNT`).
That work is low-information. By the mandate's own test, it would reproduce a known
ceiling.

The alternatives, each of which changes the evidence frontier:

1. **Longer history.** This is the only lever that moves the MDE. Examples: pre-2008
   futures (decisions D1/D2 in `DATA_INVENTORY_SPEC.md`; a purchase is Aaron's gate), or
   free public long-history series with point-in-time integrity. A 46-year span gives
   MDE ≈ 0.42; a century gives about 0.29. Point-in-time rights must be asked first,
   and prior exposure of any such series must be disclosed.
2. **Large-effect-only screening.** Admit a candidate to S1 only if it carries an
   a-priori, mechanism-grounded argument that its effect is at least the sample's MDE.
   Expect few or none; zero is a legitimate result.
3. **Park Round 2.** Record a programme-level identifiability ceiling as the Round-2
   end state. This is the delegate's decision (closure or park).

**Builder's judgement.** Option 1 is the only one that raises what the programme can
learn. Its first step is a no-cost, read-only inventory: which free long-history series
exist, whether they are point-in-time, and whether any of them is already exposed.
Without that, option 3 is the honest end state. Option 2 alone is unlikely to admit
anything.
