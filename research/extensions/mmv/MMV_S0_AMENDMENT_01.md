# CTA-EDGE-04-MMV — S0 AMENDMENT 01

**Signal domain corrected: 15 mapped instruments, not all 17**

```
RECORD_TYPE   = S0_AMENDMENT
LINEAGE       = CTA-EDGE-04-MMV
AMENDMENT_ID  = MMV-S0-AMD-01
DATE          = 2026-09-17
AMENDS        = MMV_S0_FRAME.md (2026-09-16, commit 89b7949547da70732eae17fc011abf9453376af2)
AUTHORITY     = ../../../ops/OWNER_DECISION_RECORD_CTA_EDGE_04_MMV.md §11 (MMV-OD-6)
```

**`MMV_S0_FRAME.md` is NOT rewritten.** It stands exactly as committed. This document is
the delta, following the `PINS_S0_AMENDMENT_01` precedent.

---

## §1 The correction

**What the S0 frame said** (§C.8, `PRIMARY_ASSET_MAPPING`):

> `PRIMARY_ASSET_MAPPING = CROSS-ASSET DIRECTIONAL, pooled across the four mapped classes
> (equity, duration/credit, commodities, dollar), inside the canonical 17-ETF universe.
> Not one asset, not one sleeve.`

The "four mapped classes" half was right. The phrase **"inside the canonical 17-ETF
universe"** is corrected, because it can be read — and in the S0 frame's §H and §I it was
effectively read — as the MMV alpha covering all seventeen instruments.

```
CORRECTED

PRIMARY MMV SIGNAL DOMAIN = 15 MAPPED ETFs DRAWN FROM the canonical 17-ETF universe:
  SPY EEM EWJ XLE XLU  ·  TLT SHY  ·  LQD HYG  ·  USO UNG GLD DBA  ·  UUP FXY

NOT MAPPED, and therefore outside the primary signal domain:
  VNQ  RWX      (RealEstate/US-REIT, RealEstate/ExUS-REIT)

The canonical RISK INFRASTRUCTURE still spans the full canonical book and is unchanged.
Real estate simply receives NO MMV ALPHA EXPOSURE: primary MMV weight = 0 always.
```

Verified against repository authority rather than asserted: `output/monthly_signal_panel.csv`
carries exactly 17 canonical instruments, and the canonical 17 minus `{VNQ, RWX}` is
exactly the 15-row coefficient table of MMV-OD-6 §11.3.

## §2 Why real estate is unmapped, and why the distinction is load-bearing

F5 maps its themes to **four classes** — equity, duration/credit, commodities and the
dollar — and its own Gate-1 wording is *"pooled across the four mapped classes"*. Real
estate is the canonical book's **fifth** sleeve and was never one of them. F5 gives it no
direction, and inventing one would be a scientific claim about REIT behaviour, not a
mechanical step.

**`NOT_MAPPED` is not the same as `signal = 0`**, and the difference decides the kill gate:

```
IF VNQ/RWX were coded as signal 0 in every month, then under MMV-OD-4's own rule
(0 versus +/-1 = DISAGREEMENT) they would contribute mechanical DISAGREEMENT in every
month in which the canonical composite is non-zero — by construction, regardless of any
macro information. Two permanently unmapped instruments would push pooled agreement
DOWN, which is the direction that helps MMV survive Gate 0.5.

That is an artefact, it favours the candidate, and it has nothing to do with whether
the macro composite is the core's static bet in macro vocabulary.
```

So:

```
Gate 0.5:  VNQ / RWX cells are UNDEFINED and enter NEITHER numerator NOR denominator,
           exactly like a missing-leg cell under the hold record's T-SEP-8.
```

This is an interpretation of *"cells where BOTH signals are defined"* in MMV-OD-4, **not**
a change to the threshold, the metric, or the zero rule for mapped instruments. Zeros on
mapped instruments remain real position states and are never discarded.

## §3 Claim wording — binding

```
PERMITTED:  "... the 15 mapped ETFs drawn from the canonical 17-ETF universe ..."
FORBIDDEN:  "... all canonical 17 ETFs ..." for the MMV alpha.
```

Every later document in this lineage inherits this wording. The S0 frame's §C.1 research
question, §C.8 mapping paragraph and §H claim text are all read subject to this
amendment.

## §4 What this amendment does NOT change

```
The research question and mechanism                       unchanged
The three separate information concepts A / B / C         unchanged
MMV-OD-1 latest-known-as-of primary                       unchanged
MMV-OD-2 CPILFENS and the DFEDTAR splice                  unchanged
The 12-month change, sign-only transform                  unchanged
MMV-OD-3 materiality, MMV-OD-4 the 80.0% inclusive kill   unchanged
MMV-OD-5 cost and the canonical risk wrapper              unchanged
The information cutoff and same-day release rule          unchanged
Negative outcome taxonomy A..G                            unchanged
EVIDENCE_CEILING = supported                              unchanged
Sample reuse: ETF price leg BURNED / T0, macro leg NEW    unchanged
Canonical TSMOM remains the frozen research benchmark     unchanged
```

No accepted artifact of any other lineage was touched.
