# CTA-EDGE-04-MMV — S1 HOLD RECORD

```
RECORD_TYPE   = S1_DESIGN_HOLD
LINEAGE       = CTA-EDGE-04-MMV
DATE          = 2026-09-16
BRANCH        = cta-edge/macro-momentum-vintage-s0
PRE_S1_HEAD   = 89b7949547da70732eae17fc011abf9453376af2  (S0 frame)

S1_DESIGN_STATUS = HOLD
S1_SEAL_CREATED  = NO
PREREGISTRATION_CREATED = NO

SEAL-BLOCKING   = 3 UNBOUND SCIENTIFIC CHOICES  (§2, §3, §4)
DATA-BLOCKING   = 1 ORDINARY ACQUISITION BLOCKER (§5)
```

The S1 brief's §5, §6, §7 and §8 each instruct a STOP if the F5 authority leaves the
corresponding rule undefined. Three of those four conditions are met. This record names
each missing rule exactly, shows the authority text that fails to bind it, and records
everything that **is** resolved so the post-resolution S1 is short.

**No invention was made anywhere.** Where F5 is silent, this record says so.

---

## §1 What IS resolved — the seal is not blocked on any of this

| item | status | authority |
|---|---|---|
| Information concept | `LATEST_KNOWN_AS_OF_DECISION_DATE` | MMV-OD-1 |
| First-release cell | diagnostic only; promotion / rescue / **kill** power all NONE | MMV-OD-1 |
| Inflation series | `CPILFENS`; `sign[pi12(m) − pi12(m−12)]` | MMV-OD-2 |
| Policy series | `DFEDTAR` → 2008-12-15, then `midpoint(DFEDTARL, DFEDTARU)`; `sign(0)=0` | MMV-OD-2 |
| Splice boundary | **verified against FRED**: `DFEDTAR` is titled `(DISCONTINUED)`, last observation **2008-12-15**, note *"Effective December 16, 2008, target rate is reported as a range"* | FRED series pages |
| Transform | 12-month change, **sign only**. No 3m/6m/18m/24m, no z-score, no scaling, no threshold, no percentile, no smoothing family | F5 field 1 |
| Growth inputs | `INDPRO`, `PAYEMS`. `UNRATE` excluded — F5 lists it as data with **no feature role** | F5 fields 3 and 5 |
| Materiality | Gate 1 gross mean L95 > 0; M1 net mean L95 > 0; M2 net Sharpe L95 > +0.30, all STRICT | MMV-OD-3 |
| Separability | pooled exact sign agreement ≥ **80.0 % inclusive** → kill; zeros are real states | MMV-OD-4 |
| Cost | 2 bps one-way | MMV-OD-5, `config.py:196` |
| Risk wrapper | 60-day vol, 10 % asset vol target, ±2 cap, equal weight, 10 % portfolio vol, 3× gross — **every expected parameter matches the repository exactly** | `config.py:168–184` |
| Information cutoff | 15:45 ET on the month-end trading day — **compatible**, strictly conservative against a decide-at-close / execute-next-session convention | `src/portfolio.py:148` |
| Price independence | no price enters the raw signal; `DGS2` permanently excluded | MMV-OD-2 |
| Bootstrap | calendar-year block, B = 10,000, 95 % percentile, one common draw set, frozen monthly tuples, no HAC / Newey-West / second bootstrap / monthly IID | brief §20 |
| Fragility menu | none added; Gate 0.5 is the pre-PnL falsification | brief §21 |
| Trial family | m = 1, one MMV composite; ETF price sample burned / T0; macro leg new; evidence ceiling `supported` | brief §23 |

---

## §2 UNBOUND-1 — the growth-leg aggregation rule

```
UNBOUND_SCIENTIFIC_CHOICE =
  How sign(D12 INDPRO) and sign(D12 PAYEMS) combine into ONE growth-leg sign.
```

F5 field 3, verbatim and complete for this leg:

> **F5.a Growth momentum:** 12-month change in industrial production and in payrolls
> (vintage) → long equity / credit, short duration.

That is the entire text. It names **two series** and **one mapping** and never says how
the two become one. The brief's §6 is explicit: *"If F5 does NOT bind how INDPRO and
PAYEMS combine: STOP … Do not silently equal-weight / majority-vote them."*

The disagreement case is not hypothetical: industrial production and payrolls diverge for
quarters at a time around manufacturing-led slowdowns, which is precisely where a
turning-point signal earns or loses. With two inputs and `sign(0) = 0` there are nine
sign pairs, and at least the four mixed ones need a declared answer.

```
ALTERNATIVES the controller may choose among (not chosen here):
  (a) average the two 12-month changes first, then take one sign  (a units question:
      INDPRO is an index, PAYEMS is a level in thousands, so this needs a declared
      normalisation, which is itself a transform choice F5 forbids searching over)
  (b) sign each separately, then average the two signs, with sign(0)=0 -> leg in
      {-1, -0.5, 0, +0.5, +1}, which breaks the sign-only rule unless re-signed
  (c) sign each separately, unanimity required, disagreement -> 0 (leg abstains)
  (d) declare one series primary and the other a diagnostic
```

## §3 UNBOUND-2 — the macro composite rule

```
UNBOUND_SCIENTIFIC_CHOICE =
  How the growth, inflation and policy legs combine into the MACRO COMPOSITE, and
  from there into a per-instrument direction. Component weights, sign arithmetic,
  tie rule, zero rule and missing-leg rule are all undefined.
```

**F5 uses the phrase "the macro composite" exactly three times — lines 245, 259 and 547 —
and every one of them is a *reference* inside the falsification gate. The map never
defines the object.** Searching the whole 635-line authority for `composite`, `aggregat`,
`weight`, `combine`, `equal`, `majority` and `average` returns no definition.

This is not a tidy-up detail, because **F5's own mapping table structurally contradicts
itself on equity**:

| asset class | growth (F5.a) | inflation (F5.b) | policy (F5.c) | status |
|---|---|---|---|---|
| **equity** | **LONG** | — | **SHORT** | **DIRECT CONTRADICTION** |
| duration | SHORT | SHORT | SHORT | unanimous |
| credit | LONG | — | — | single leg speaks |
| commodities | — | LONG | — | single leg speaks |
| dollar | — | LONG | LONG | agree |

Whatever rule resolves equity — and whether a single speaking leg is enough to take a
position in credit and commodities — **changes the position matrix directly**. The
position matrix is the input to Gate 0.5, and Gate 0.5 is the kill gate. So this choice
moves the number that decides whether the lineage lives, before any return exists. It is
estimand-level, not implementation-level.

The brief's §7 is explicit: *"If F5 does not sufficiently define the composite: return
HOLD."* It also forbids the escape hatch: *"No component may receive a weight based on
historical return performance."*

## §4 UNBOUND-3 — the class-to-instrument mapping is not implementable as written

```
UNBOUND_SCIENTIFIC_CHOICE =
  F5 maps macro legs to ASSET CLASSES. Mapping those classes onto the canonical
  17-ETF universe cannot be completed mechanically.
```

The brief's §8 says *"If F5 uses class-level mapping: mechanically map the existing
canonical ETFs to those classes"* and *"If the F5 mapping is not implementable without a
scientific choice: return HOLD."* Attempting the mechanical map surfaces four gaps:

```
REAL ESTATE (VNQ, RWX)   Appears in NO F5 class. F5 names equity, credit, duration,
                         commodities and the dollar. Two of the seventeen canonical
                         instruments have no theoretical direction at all. Assigning
                         them to "equity" is a scientific claim about REIT behaviour,
                         not a mechanical step; assigning them 0 permanently is a
                         different scientific claim.

FXY (yen)                F5 says "long dollar". Long dollar implies SHORT yen, so FXY
                         would take the OPPOSITE sign to UUP. That inversion is an
                         inference, not F5 text, and it is the only instrument in the
                         universe whose mapped sign is the negation of its class.

LQD                      Sits in BOTH contested classes: it is investment-grade CREDIT
                         (growth says LONG) and carries substantial DURATION (all three
                         legs say SHORT). F5 gives no rule for an instrument that is in
                         two classes with opposing directions. HYG is the same problem
                         with a different credit/duration balance.

GLD, XLE                 GLD is a commodity for the inflation leg (LONG) while the same
                         leg says LONG DOLLAR, and gold is conventionally the dollar's
                         mirror — F5's two inflation prescriptions point opposite ways
                         for this instrument. XLE is an equity-sector fund with direct
                         commodity exposure and therefore inherits the contested equity
                         cell plus a commodity reading.
```

None of these is resolvable by reading F5 more carefully. Each requires a decision about
what an instrument *is*, and the brief forbids removing inconvenient ETFs or expanding the
universe to avoid the question.

## §5 DATA_FREEZE_BLOCKER — ALFRED_API_ACCESS

```
DATA_FREEZE_BLOCKER = ALFRED_API_ACCESS
RAW_MACRO_INPUTS_PINNED = NO
```

The brief's §27 requires the raw macro inputs to be acquired and pinned before seal if
technically possible, and is explicit about the failure mode: *"If an ALFRED API key is
required and not currently available: do not substitute revised FRED history. Return S1
HOLD: DATA_FREEZE_BLOCKER = ALFRED_API_ACCESS. This is ordinary data acquisition, not a
Fable Owner decision."*

Checked this session and **no key was found**: no `FRED*` or `ALFRED*` environment
variable, no `~/.fredapikey`, no `.env`, and no `api_key` reference in `config.py`,
`research/extensions/value/value_data.py` or `src/yields.py`. The FRED API terms state
*"In order to use the FRED® API, you must have register for an API Key."*

**No revised FRED history was substituted, and nothing was fetched.** Obtaining a key is a
self-service registration and is not an institutional entitlement — categorically unlike
the LSEG / ICE wall that closed PINS. This blocker is mechanical and expected to clear
trivially; it is recorded separately from §2–§4 because it is **not** a scientific
question and must not be routed to an advice seat.

Series metadata verified without a key, by reading public ALFRED and FRED pages only:

```
PAYEMS     vintages from 1955-05-06 (ALFRED download page lists 1,024 as read)
CPIAUCSL   vintages from 1972-07-21
PCEPILFE   vintages from 2000-08-01            (not a primary series under MMV-OD-2)
DFEDTAR    1982-09-27 .. 2008-12-15, DISCONTINUED, replaced by DFEDTARL / DFEDTARU
```

## §6 Firewall status at this record

```
HISTORICAL_MACRO_FEATURE_COMPUTED = NO      HISTORICAL_MMV_POSITIONS_COMPUTED = NO
SEPARABILITY_RESULT_COMPUTED      = NO      RETURN_OUTCOME_ACCESSED           = NO
BACKTEST_RUN                      = NO      BOOTSTRAP_RUN                     = NO
FIRST_RELEASE_DISAGREEMENT_COMPUTED = NO    FAMOUS-RECESSION INSPECTION       = NONE

Raw macro data acquired: NONE (blocked, §5). Nothing was combined into any signal.
research/extensions/mmv/ contains only MMV_S0_FRAME.md and this record.
```

---

## §7 DRAFTED, NOT SEALED — implementation test specifications

The brief's §28 and §29 ask for exact S2 test specifications. They depend on none of the
unbound choices, so they are drafted here to shorten the post-resolution S1. **They carry
no authority until they appear inside a sealed preregistration.**

### §7.1 Point-in-time / same-day tests (brief §28)

```
T-PIT-1  a vintage dated ONE DAY BEFORE the cutoff is ELIGIBLE
T-PIT-2  a vintage dated ONE DAY AFTER the cutoff is INELIGIBLE
T-PIT-3  a same-day release timestamped 08:30 ET (CPI / payrolls) is ELIGIBLE
T-PIT-4  a same-day release timestamped 09:15 ET (industrial production) is ELIGIBLE
T-PIT-5  a same-day release timestamped 14:00 ET (FOMC) is ELIGIBLE
T-PIT-6  a same-day release timestamped after 15:45 ET is INELIGIBLE at this decision
         date and becomes eligible only at the next one
T-PIT-7  a same-day vintage whose release time CANNOT be established falls back to the
         PRIOR eligible vintage — never to a guess
T-PIT-8  a final-revised value never leaks backward: recomputing decision month m after
         later vintages exist reproduces the original month-m signal bit-for-bit
T-PIT-9  a FUTURE benchmark revision cannot alter an EARLIER historical decision
T-PIT-10 the signal at decision date t is invariant to the deletion of every vintage
         dated after t  — the strongest form of the same rule
```

### §7.2 Separability tests (brief §29, no return values needed)

```
T-SEP-1  a constructed panel at exactly 79.999 % pooled agreement PASSES Gate 0.5
T-SEP-2  a constructed panel at exactly 80.000 % pooled agreement yields CLASS B
T-SEP-3  a (0, 0) cell counts as AGREEMENT
T-SEP-4  a (0, +1) cell and a (0, -1) cell each count as DISAGREEMENT
T-SEP-5  zeros are never discarded: a panel differing only by retained zero cells
         produces a different pooled agreement than one that drops them
T-SEP-6  one instrument at 100 % agreement while the pooled figure is below 80 %
         leaves Gate 0.5 PASSING — per-instrument rates cannot kill
T-SEP-7  one instrument at very low agreement while the pooled figure is at or above
         80 % still yields CLASS B — per-instrument rates cannot rescue
T-SEP-8  cells where either signal is undefined are excluded from BOTH numerator and
         denominator
```

---

## §8 What is needed to clear the HOLD

```
SCIENTIFIC (route to an Owner decision; Fable is DESIGN-EXPOSED / NOT INDEPENDENT but
            this is CONSTRUCTIVE DESIGN, which is its designated role):
  UNBOUND-1  the growth-leg aggregation rule
  UNBOUND-2  the macro composite rule, including the equity contradiction and whether
             a single speaking leg suffices for credit and commodities
  UNBOUND-3  the class-to-instrument mapping: real estate, FXY's sign inversion,
             LQD/HYG dual membership, GLD and XLE

MECHANICAL (no advice seat required):
  ALFRED API key, after which the raw macro inputs can be pinned and Gate 0 completed
```

All three scientific gaps are **narrow and listable** — each has a small, explicit option
set — and all three sit in the same place: F5 specified the *inputs* and the *directions*
in full, and never specified the *arithmetic* that turns them into a position. Resolving
them is one focused decision round, not a redesign.

```
NOTHING IN THIS RECORD AUTHORISES S2, A SEAL, A RUN, A DATA PURCHASE, OR ANY
COMPUTATION ON ANY CANDIDATE OUTCOME.
```
