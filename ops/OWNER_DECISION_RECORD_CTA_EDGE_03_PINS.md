# OWNER DECISION RECORD — CTA-EDGE-03-PINS (physical inventory news × scarcity)

```
RECORD_TYPE        = OWNER_DECISION_RECORD
LINEAGE            = CTA-EDGE-03-PINS
DATE_OF_DECISIONS  = 2026-09-16
OWNER              = Aaron  (the only authority for every decision recorded here)
ADVICE SEAT        = Claude Fable 5.1, delegated Owner-advice seat for PINS-OD-1
RELAY              = programme controller (Aaron-side ChatGPT), CTA-EDGE-03-PINS
                     PINS-OD-1 EXPECTATION-SOURCE FEASIBILITY RESOLUTION task brief
RECORDED_BY        = Claude Opus 5 (Main Agent / builder seat), PINS-OD-1 feasibility
                     session 2026-09-16
WORKFLOW_AUTHORITY = ../QUANT_WORKFLOW_VNEXT.md  (vNext, cutover 2026-09-12)
```

**What this file is.** The durable record of the Owner decisions governing
`CTA-EDGE-03-PINS`. It records **decisions**, not workflow authority.

**What this file is not.** Not a preregistration, not authorisation to implement, not
authorisation to run, not an exposure event. It creates no row in `EXPOSURE_LEDGER.md`,
no record in `EXECUTION_AUTHORIZATIONS.md` and no trial in
`../research/extensions/TRIAL_LEDGER.md`. Writing this record revealed no outcome and
computed no performance.

---

## §1 Stage state at the time of recording

```
S0 FRAME                = COMPLETE — HOLD on PINS-OD-1 (PINS_S0_FRAME.md, 2026-09-16)
PINS-OD-1               = DECIDED by this record
PINS-OD-2/3/4           = DEFERRED, not asked, not decided
S1 ENTRY_AUTHORIZED     = NO
S1 SEAL_AUTHORIZED      = NO
S2 BUILD_AUTHORIZED     = NO
TARGET_RUN_AUTHORIZED   = NO
REVEAL_AUTHORIZED       = NO
DATA_PURCHASE_AUTHORIZED = NO
```

---

## §2 PINS-OD-1 — the expectation source

```
DECISION_ID  = PINS-OD-1
STATUS       = OWNER-CONFIRMED, BINDING
QUESTION     = What is the pre-release expectation against which the first-published
               EIA weekly crude inventory change is differenced, and is that source
               lawfully reconstructible point-in-time?

DECISION     = CONDITIONAL OPTION 1

EXPECTATION_ANCHOR        = ONE NAMED PRE-API ANALYST-SURVEY CONSENSUS FAMILY
MANDATORY_SECOND_PIT_INPUT = FIRST-REPORTED API PRE-RELEASE CRUDE INVENTORY ESTIMATE

CONDITION    = The lineage requires BOTH to be historically reconstructible
               point-in-time. Either one alone does not satisfy this decision.
```

### §2.1 What the other options now mean

```
OPTION 2 — API alone            = NOT ACCEPTED under the current PINS claim.
                                  If API alone is later desired it requires a
                                  SEPARATELY NAMED lineage with its own claim. It may
                                  not be reached by relaxing this lineage.

OPTION 3 — model expectation    = REJECTED for the current PINS claim.
                                  If later pursued: CLOSE or PARK the current PINS and
                                  open a RENAMED statistical-expectation lineage. It is
                                  a different hypothesis and may not be substituted in.

OPTION 4 — close at S0          = the correct outcome if the accepted feasibility rules
                                  fail. Negative outcome class A (DATA / PIT FAILURE).
                                  No trial spent.
```

### §2.2 Why "conditional"

The decision is conditional on a feasibility audit that had not been run when it was
taken. A PASS on that audit authorises **full-series acquisition or reconstruction** and
nothing else; it does **not** authorise S1, a seal, a build, a run, or a data purchase.

---

## §3 Controller qualifiers — binding, and narrower than the advice

Fable's advice was accepted **with qualifiers**. The qualifiers are part of the decision
and override anything in the advice that conflicts with them.

### §3.1 PINS-Q1 — no fitted `k`

Fable used the conceptual model

```
E*  ≈  C + k (P − C)
```

as a way of thinking about how a market expectation might update between the analyst
survey and the API print.

```
LINEAR_MARKET_EXPECTATION_UPDATE_MODEL = HEURISTIC_ONLY
k                                      = UNKNOWN

This model is NOT sealed as a factual description of market expectation formation.
```

**No historical WTI return may be used to estimate `k`.** Specifically forbidden:

```
price-fitted k          return-maximising k        regression-selected k
post-outcome weighting  any k chosen after any outcome is visible
```

If a future S1 wants a fixed combination of `C` and `P`, that combination must be chosen
**before outcome exposure**, from economic or external authority, and frozen in the
sealed contract.

### §3.2 PINS-Q2 — measurement error is a risk, not a known direction

```
RECORDED: using C alone, or P alone, creates material proxy / measurement risk.
```

**Not sealed as programme facts:**

```
"the measurement error is classical"
"the bias must attenuate toward zero"
```

The exact bias direction depends on statistical assumptions that have **not** been
established for this lineage. Halova, Kurov & Kucher (2014) established that OLS
price-impact estimates are materially biased by surprise measurement error in this
literature; they did not license this programme to assert a direction here. The S0
frame's §B.3 and §H wording, which leaned on attenuation, is corrected accordingly in
`../research/extensions/pins/PINS_S0_AMENDMENT_01.md` §4.

### §3.3 PINS-Q3 — terminology, binding

```
A  = first-published EIA weekly crude inventory change
C  = named pre-API analyst-survey consensus
P  = first-reported API pre-release estimate

PERMITTED:
  A − C   "consensus surprise", or
          "inventory news relative to the pre-API analyst consensus"
  A − P   "EIA–API discrepancy"
  P       "pre-release inventory estimate"

FORBIDDEN:
  calling P        "market expectation"
  calling A − P    "market-expectation surprise"
```

**No unqualified final "inventory news" regressor is defined yet.** The functional form
remains an S1 design question and is not settled by this record.

---

## §4 Design exposure consequence

```
FABLE_DESIGN_EXPOSED = YES     (changed from NO by this decision)
ASTRA_DESIGN_EXPOSED = YES     (unchanged)
```

Because the advice was **adopted**, Claude Fable 5.1 materially influenced PINS-OD-1 and
therefore the expectation information set of this lineage. Both seats are now design-
exposed to PINS.

```
This does NOT prevent Fable from acting again as a delegated Owner-advice seat.
It DOES prevent treating Fable as a fresh BLIND CERTIFIER of the PINS design,
implementation or result.
```

Recorded on the seat axis in `REVIEWER_EXPOSURE_LOG.md`. The S0 frame's §G, which
recorded `FABLE_DESIGN_EXPOSED = NO`, is superseded on that point — and it is superseded
by **amendment**, not by rewriting: see `PINS_S0_AMENDMENT_01.md`.

---

## §5 What this record does not decide

```
PINS-OD-2  scarcity definition                  DEFERRED — not asked, not decided
PINS-OD-3  execution latency + primary horizon  DEFERRED — not asked, not decided
PINS-OD-4  economic materiality scale           DEFERRED — not asked, not decided
```

Also not decided here: the survey family (chosen by the outcome-free rule in the
feasibility protocol, not by Owner preference), the functional form of the news
regressor, the sample window, the instrument convention, and anything about `k`.
