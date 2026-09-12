# PROJECT_STATE — multi-asset TSMOM extensions

Current **state** of this project under
[`QUANT_WORKFLOW_VNEXT.md`](../QUANT_WORKFLOW_VNEXT.md) (cutover 2026-09-12) — state,
never workflow authority (vNext §0).

```
RESEARCH_QUESTION   = X01: does the commodity-sleeve TSMOM implementation transfer
                      to futures under the matched map (matched-map arm, cluster C1
                      implementation-transfer / wrapper-truth)?
RESEARCH_ID · LANE  = TSMOM-EXT-001 · FULL (sealed 2026-09-13)
S1 DESIGN+SEAL      = COMPLETE — X01_PREREG_SEALED = YES. Aaron's Owner decision
                      of 2026-09-13, "SEAL X01 AS CURRENT PREREGISTRATION, NO
                      SCIENTIFIC AMENDMENT", is persisted in the preregistration
                      itself. Sealed identity
                      4db18f6cc084bf4a4ba9260e7ba81489e658d74adf03818aa4169208a40f54c5
                      at seal revision bc123fee7c8d847a6f883dd2187a9a2100f9c490.
                      The pre-seal identity 9c7b104f...96986743 is superseded; the
                      scientific content is byte-identical across the seal.
S2 BUILD            = COMPLETE — execution infrastructure frozen and bound at
                      0b79a904cf8b3d9e27fe16cdbf22bf19cbe3f985.
CURRENT_VNEXT_STAGE = S3 RUN
S3_RUN_READY        = NOT_YET_RECHECKED. The minimal S3 readiness check must be
                      rerun after repository housekeeping; the 2026-09-12 run of it
                      refused on a modified README.md from the vNext cutover, which
                      is untouched here to keep the seal independently reviewable.
                      CURRENT_VNEXT_STAGE is a stage label, not a readiness claim,
                      and PROJECT_STATE is not a gate.
ACTIVE_HYPOTHESIS   = X01 matched-map transfer; sealed contract at
                      research/extensions/x01/X01_PREREGISTRATION_DRAFT.md
DATA_GRANT          = existing Databento + ETF panels only; the Databento ceiling
                      (ops/EXECUTION_AUTHORIZATIONS.md) is unchanged; no purchase
                      authorized
TRIAL_ACCOUNTING    = research/extensions/TRIAL_LEDGER.md — a VIEW. The authoritative
                      Databento dataset ledger stays
                      commodity-carry-research/preregistration/PREREGISTRATION.md §10
                      (N_trials = 14, TSMOM-EXT contribution 0, planned X01 +3).
                      ETF panel: D-ETF-COUNT historical count remains UNKNOWN.
OUTCOME_EXPOSURE    = TARGET_METRIC / HISTORICAL_CUMULATIVE (ops/EXPOSURE_LEDGER.md).
                      RETAINED: full-sample core, sleeve, robustness-grid, cost-sweep
                      and overlay results are already revealed, so exposure tracking
                      is materially required (vNext §11).
TARGET_EXECUTION_AUTHORIZED = NO — zero authorization records exist in
                      ops/EXECUTION_AUTHORIZATIONS.md. A seal is not authorization.
TARGET_X01_OUTCOME_ACCESSED = NO — no real E, A1, S1, S2, Sharpe, ΔS, bootstrap,
                      crisis slice, diagnostic or evidence artifact has been
                      computed or opened.
X01_FIRST_EXECUTION_EXPOSURE_CLASSIFICATION = GENERATED_NOT_SEEN (Owner-sealed)
OPEN_MATERIAL_BLOCKERS = NONE recorded. The X01 draft reports
                      TECHNICAL_BLOCKERS = NONE and OWNER_DECISIONS_REMAINING = NONE.
NEXT_OWNER_DECISION = AUTHORIZE ONE REAL SEALED X01 EXECUTION under
                      GENERATED_NOT_SEEN — after housekeeping and a green rerun of
                      the minimal S3 readiness check. X01 target execution is NOT
                      authorized: zero authorization records exist, and a seal is
                      not authorization to execute.
```

## Path to the seal under vNext — TAKEN 2026-09-13

> Recorded for provenance. Aaron sealed X01 on 2026-09-13 without a further Astra
> round, exactly as the reasoning below anticipated. The section is kept as the
> account of how the seal was reached, not as an outstanding plan.

The draft's own status line reads *"AWAITING GPT-6 ASTRA A2 DELTA CLOSURE, THEN
AARON'S SEAL"*. Under vNext that closure round is **not mandatory**:

- An Astra A2 challenge already ran and returned `FAIL` with four design defects
  and zero outstanding Owner decisions; the bounded repair was applied and the
  review accepted; the independently accepted infrastructure (X02, X03, panel,
  OI, cash-first primitive, V2) was not reopened.
- A second round on the repaired delta is a **review of a review** — exactly the
  step vNext removes (§6: a HOLD buys one bounded repair, then Aaron accepts on
  the settling evidence, authorizes one closure check if materially justified, or
  parks the work).

So: run the mechanical prereg validators, take ChatGPT/Aaron acceptance, and the
seal is Aaron's decision. A further Astra round needs a named material trigger
(vNext §4) or Aaron asking — reassurance is not a trigger.

S2 BUILD is complete. What remains is S3 RUN behind the mechanical gate plus
Aaron's explicit X01 execution authorization, then S4 VERDICT — where one Astra
MEDIUM evidence-to-claim judgment is normal, because the X01 claim is
consequential and FULL-lane.

## What changed for this project at cutover

Retired as default routing, kept as history: the Wave-0/Wave-1 A–L stage
declarations and `qros next` routing · Review Packet machinery · standing
reviewer seats and per-artifact seat identity · review-of-review · closure and
residual-verification packages · automatic node creation from findings.
`qros check` / `qros status` remain **on-demand** mechanical diagnostics;
`qros-state.yaml` stays the mechanical state record, not the stage authority.

Still in force: Owner-only sealing and execution authorization, the append-only
`ops/EXECUTION_AUTHORIZATIONS.md` grant discipline (a grant is read only from
committed state; a consumed authorization is never reused), the exposure and
reviewer-exposure ledgers, and every Owner gate in vNext §10.
