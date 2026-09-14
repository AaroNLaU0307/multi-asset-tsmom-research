# OWNER DECISION RECORD — CTA-EDGE-02-BENB (bond ETF–NAV basis)

```
RECORD_TYPE        = OWNER_DECISION_RECORD
LINEAGE            = CTA-EDGE-02-BENB
DATE_OF_DECISIONS  = 2026-09-15
OWNER              = Aaron  (the only authority for every decision recorded here)
RELAY              = programme controller (Aaron-side ChatGPT), CTA-EDGE-02-BENB
                     S1 SEAL-COMPLETION task brief
RECORDED_BY        = Claude Opus 5 (Main Agent / builder seat), S1 seal-completion
                     session 2026-09-15
WORKFLOW_AUTHORITY = ../QUANT_WORKFLOW_VNEXT.md  (vNext, cutover 2026-09-12)
```

**What this file is.** The durable record of the Owner decisions governing
`CTA-EDGE-02-BENB`. It records **decisions**, not workflow authority.

**What this file is not.** Not a preregistration, not authorisation to implement, not
authorisation to run, not an exposure event. It creates no row in
`EXPOSURE_LEDGER.md`, no record in `EXECUTION_AUTHORIZATIONS.md`, and no trial in
`../research/extensions/TRIAL_LEDGER.md`. Writing this record revealed no outcome and
computed no performance.

---

## §1 Stage state at the time of recording

```
S0 FRAME                = COMPLETE — initial HOLD, direction accepted
S0 DATA/DESIGN REPAIR   = COMPLETE / PASS
S1 ENTRY_AUTHORIZED     = YES
S1 SEAL_AUTHORIZED      = YES, conditional on this decision
S1 SEALED               = YES  (2026-09-15; BENB_SEAL_MANIFEST.md)
S2 BUILD_AUTHORIZED     = NO
TARGET_RUN_AUTHORIZED   = NO
REVEAL_AUTHORIZED       = NO
```

---

## §2 BENB-OD-1 — the M2 risk-adjusted usefulness floor

```
DECISION_ID  = BENB-OD-1
STATUS       = OWNER-CONFIRMED, BINDING
```

```
M2_METRIC             = calendarised annualised Sharpe of the sealed fixed-unit,
                        discount-only HYG sleeve
MONTHLY_CONSTRUCTION  = sum NET_TRADE_RETURN by ENTRY calendar month
ZERO_SIGNAL_MONTH     = exactly 0
RISK_FREE_RATE        = 0
ANNUALISATION         = sqrt(12)
M2_VALUE              = +0.30
M2_BOUNDARY_OPERATOR  = STRICT  >

PASS CONDITION
  The LOWER endpoint of the predeclared 95 % bootstrap interval for the calendarised
  annualised Sharpe must be STRICTLY GREATER THAN +0.30.

  Sharpe_CI_lower = 0.300000...   ->  FAILS M2
  Sharpe_CI_lower > 0.30          ->  MAY pass M2, subject to every other condition
```

### §2.1 Provenance — this is a BENB-specific decision

```
DECIDED BEFORE  historical basis computation · discount-sign count · regression ·
                any return outcome · any backtest.
```

At the moment this decision was taken, **no `b_t`, no `x_t`, no discount-observation
count, no `beta_T`, no `beta_O`, no `beta_N`, no strategy return, no Sharpe and no
bootstrap result existed** for this lineage. The value was therefore fixed with no
knowledge of the realised discount-severity distribution or of the signal's frequency.

```
NOT INHERITED FROM  C-A · CTA-EDGE-01-TA · any programme-wide convention.
```

This matters and is recorded deliberately. The S1 design pass established that the
programme has **no portable materiality floor**: C-A's `+0.30 / −0.20` is bound in its
own Owner record to *"canonical raw net Sharpe, rf = 0, 2 bps transaction cost"* and to
*"persistence of the canonical raw-return thesis"*, and OD-7 of that record explicitly
refused to lend the scale even to FM-1 inside C-A's own contract — *"the primary
materiality scale is **not borrowed**"*. Other lineages set their own (X01 a 0.15 Sharpe
tolerance; Time-Series Value a −0.15 adverse floor; TSMOM-VRP-01 +7.5 % annualised on
committed capital). CTA-EDGE-01-TA's `M2 = +0.30` was scoped to that lineage, which is
now closed pre-outcome.

**So the number here coincides with C-A's, and the authority does not.** This is Aaron's
decision for CTA-EDGE-02-BENB, taken on its own terms.

The **strict** boundary operator follows the Owner's established convention for
materiality crossings (C-A OD-1: *"A lower confidence bound of exactly `+0.30` does not
trigger material positive persistence"*), and is fixed here explicitly rather than
inherited by implication.

### §2.2 Explicitly excluded

```
NO active-month-only Sharpe.   The monthly series retains every calendar month in the
                               grid, and a month with no signal is exactly 0.
NO sparsity adjustment.        The sleeve is charged for idle calendar time by design.
NO post-outcome threshold change, in either direction, for any reason.
```

The disclosed consequence, accepted with the decision: this sleeve is flat on every day
without a discount signal, so its monthly series is mostly exact zeros by construction,
and a Sharpe computed on such a series is not the same statistic as a Sharpe on an
always-invested book. The Owner has fixed the floor knowing that, and knowing that the
degree of sparsity is unknown and must remain unknown until the governed run.

---

## §3 What no agent may infer from this record

- A decision is **not** a seal, and a seal is **not** authorisation to build, acquire,
  execute or reveal.
- BENB-OD-1 governs **M2 only**. It changes no other sealed value — not M1, not the cost,
  not the horizon, not the sample, not the estimand, not the classification structure.
- Nothing here alters canonical TSMOM, C-A, C-D, or any closed lineage, including
  CTA-EDGE-01-TA.
- `D-ETF-COUNT` is **not** decided here and remains `UNKNOWN_PENDING_AARON_DECISION`.

---

## §4 Outstanding Owner decisions for this lineage

| # | decision | when |
|---|---|---|
| 1 | Accept the S1 seal | now, on controller review |
| 2 | S2 BUILD authorisation | after seal acceptance |
| 3 | Single-use execution authorisation for the one governed historical run | after S2 acceptance |
| 4 | Single-use reveal authorisation | after the run |
| 5 | Final verdict and any knowledge-base registration | at S4 |

None of these is taken here.
