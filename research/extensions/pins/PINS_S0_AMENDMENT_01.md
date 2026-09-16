# CTA-EDGE-03-PINS — S0 AMENDMENT 01

**PINS-OD-1 resolved · S0 assumptions corrected · provenance preserved**

```
RECORD_TYPE   = S0_AMENDMENT
LINEAGE       = CTA-EDGE-03-PINS
AMENDMENT_ID  = PINS-S0-AMD-01
DATE          = 2026-09-16
AMENDS        = PINS_S0_FRAME.md  (2026-09-16, commit 2242109dae59a09e7dd8e8e0cdb9d357df823669)
AUTHORITY     = ../../../ops/OWNER_DECISION_RECORD_CTA_EDGE_03_PINS.md  (PINS-OD-1)
```

**`PINS_S0_FRAME.md` is NOT rewritten.** It stands exactly as committed, including the
parts this amendment corrects. That is deliberate: the frame is the record of what the
S0 session believed and why it held, and overwriting it would destroy the provenance
that makes the HOLD meaningful. This document is the delta.

---

## §1 The sequence, recorded in order

```
1.  2026-09-16   S0 FRAME returns HOLD on PINS-OD-1 (expectation source), with
                 four alternatives stated and none chosen. PINS-OD-2/3/4 recorded
                 but deferred behind OD-1 as a gate.
                 -> PINS_S0_FRAME.md §H, commit 2242109d

2.  2026-09-16   Aaron routes PINS-OD-1 to Claude Fable 5.1 as a delegated
                 Owner-advice seat, as the frame recommended.

3.  2026-09-16   Fable advises: anchor on a named pre-API analyst-survey consensus
                 and carry the first-reported API estimate as a second point-in-time
                 input; reasons about how a market expectation might update between
                 the two using the heuristic E* ~ C + k(P-C); and flags measurement
                 error in the surprise.

4.  2026-09-16   Programme controller ACCEPTS the advice WITH QUALIFIERS and relays
                 the binding Owner decision.
                 -> PINS-OD-1 = CONDITIONAL OPTION 1
                 -> qualifiers PINS-Q1 (no fitted k), PINS-Q2 (measurement error is
                    a risk, not a known direction), PINS-Q3 (binding terminology)

5.  2026-09-16   This amendment records the decision and corrects three S0 statements
                 that the advice and the controller's review showed to be wrong or
                 overstated.
```

---

## §2 What PINS-OD-1 resolved

```
PINS-OD-1 = CONDITIONAL OPTION 1

EXPECTATION_ANCHOR         = one named PRE-API analyst-survey consensus family
MANDATORY_SECOND_PIT_INPUT = first-reported API pre-release crude inventory estimate
CONDITION                  = BOTH must be historically reconstructible point-in-time
```

The S0 frame presented four options and asked for one. The answer was **not** simply
"option 1": it is option 1 **plus** a mandatory second point-in-time input that the frame
had treated as an *alternative* to the survey rather than as a companion to it. That is a
genuine change to the information set of the lineage, and it is why Fable is now
design-exposed.

Option 2 (API alone) is **not** reachable by relaxing this lineage — it would need a
separately named lineage. Option 3 (model expectation) is **rejected** for the current
claim; pursuing it means closing or parking PINS and opening a renamed
statistical-expectation lineage. Option 4 (close at S0) remains the correct outcome if
feasibility fails.

---

## §3 CORRECTION 1 — the survey statistic is not assumed to be a median

**What the S0 frame said** (§H, PINS-OD-1 option 1):

> *"survey consensus (Reuters / Bloomberg / Platts poll **median**, published Mon–Tue
> before the Wednesday release)"*

**Correction.** *"Median"* was an assumption, not a verified fact, and it was carried in
as though it were part of the option's definition.

```
CORRECTED: the headline statistic is whatever the NAMED FAMILY PUBLISHES as its
           headline, and it must be read off that family's own material per release.
           Fable's verified Reuters examples used an AVERAGE, not a median.
```

This matters more than it looks. A mean and a median of a small analyst panel diverge
exactly when the panel disagrees — which is when the "surprise" is most interesting — so
silently assuming the wrong statistic would inject error precisely into the observations
that carry the most information. The feasibility protocol therefore records the statistic
as a **per-family verified field**, never a default.

---

## §4 CORRECTION 2 — API does not "avoid the expectation problem entirely"

**What the S0 frame said** (§E, parked question 2):

> *"Ye & Karali's construction … **avoids the survey problem entirely** — but API is
> subscription-only"*

**Correction.** Overstated in a way that flattered option 2.

```
CORRECTED: the API Weekly Statistical Bulletin avoids some SURVEY-ACCESS problems.
           It does NOT avoid the expectation problem. API is a DISTINCT PHYSICAL
           ESTIMATE produced from a voluntary-reporting survey of operators — it is
           another measurement of the same physical quantity, not a measurement of
           what the market expected.
```

Binding terminology follows from this and is recorded in PINS-Q3: `P` is a
**"pre-release inventory estimate"**, never *"market expectation"*, and `A − P` is the
**"EIA–API discrepancy"**, never a *"market-expectation surprise"*. The S0 frame's §B.3
table, which listed API under *"where the literature gets the expectation"*, is corrected
to read: where the literature gets a **pre-release estimate** that it then uses as an
expectation proxy.

---

## §5 CORRECTION 3 — measurement-error direction is not a programme fact

**What the S0 frame said** (§B.3 and §H):

> *"Measurement error in the consensus **attenuates the coefficient toward zero**"* …
> *"a weak expectation proxy therefore produces a **false negative**"*

**Correction.** The cited result (Halova, Kurov & Kucher 2014) establishes that OLS
price-impact estimates in this literature are **materially biased** by surprise
measurement error, with identification-through-censoring estimates about twice OLS for
petroleum. The frame then went one step further and asserted the *direction* as a general
fact.

```
CORRECTED: measurement / proxy risk is REAL and MATERIAL — that much stands.
           The DIRECTION of the bias is NOT established for this lineage.

NOT SEALED as programme facts:
    "the error is classical"
    "the bias must attenuate toward zero"
```

The direction depends on statistical assumptions — classical versus non-classical error,
correlation between the error and the true surprise, and whether the proxy is a rational
forecast — none of which has been established here. The practical consequence is
unchanged: a weak proxy is dangerous. The claim that it is dangerous *in one specific
direction* is withdrawn.

---

## §6 CORRECTION 4 — API access is not settled either way

**What the S0 frame said** (§B.3):

> *"access: **SUBSCRIPTION ONLY**, 'solely via subscription purchase through our
> authorized redistributors: Refinitiv … and Intercontinental Exchange (ICE)'"*

The quotation is accurate and is API's own statement about the **full Weekly Statistical
Bulletin**. But the frame let it stand as though it settled the question.

```
CORRECTED: the FULL API WSB may be subscription-based. PUBLIC REPORTING of the
           HEADLINE crude estimate may nonetheless exist, since the headline number
           is widely republished after the Tuesday release.

           Neither the existence of such reporting, nor the lawfulness of
           reconstructing and STORING a historical series from it, may be assumed.
           Both must be VERIFIED. That verification is part of the feasibility audit,
           not a background assumption.
```

---

## §7 Design exposure — updated

```
FABLE_DESIGN_EXPOSED = YES      (was NO in PINS_S0_FRAME.md §G)
ASTRA_DESIGN_EXPOSED = YES      (unchanged)
```

Fable materially influenced PINS-OD-1 and the expectation information set: the
survey-anchor choice, the mandatory second point-in-time input, and the framing that
produced qualifiers Q1 and Q2. Adopting advice is what creates exposure — asking for it
would not have been enough.

The S0 frame said this status was *"load-bearing: it is what preserves Fable as an
eligible delegated Owner-advice seat."* That reasoning was half right and is corrected
here:

```
Fable MAY still act as a delegated Owner-advice seat for PINS-OD-2/3/4.
Fable MAY NOT be treated as a fresh BLIND CERTIFIER of the PINS design,
implementation or result.
```

Both seats being design-exposed means that **any blind certification of a future PINS
result needs a third seat** that is neither Fable, nor Astra, nor this Main Agent seat.
That is a real constraint on the lineage and is recorded now rather than discovered at
S4.

---

## §8 What this amendment does NOT change

```
The research question                    unchanged
The three separate claims A / B / C      unchanged
DAILY_DATA_ADEQUATE = NO                 unchanged
INTRADAY_REQUIRED   = YES                unchanged
FIRST_PUBLISHED_EIA_SERIES_RECONSTRUCTIBLE = YES from 2012-01-05   unchanged
The R_PRE / R_JUMP / R_TRADABLE timing split                        unchanged
The mandatory distinctness-from-curve identification requirement    unchanged
The negative outcome taxonomy A..G                                  unchanged
EVIDENCE_CEILING = supported                                        unchanged
Sample-reuse status (price leg BURNED, physical NEW)                unchanged
PINS-OD-2 / OD-3 / OD-4                                             still deferred
```

No accepted artifact of any other lineage was touched. The BENB seal, result and closure
are byte-unchanged.
