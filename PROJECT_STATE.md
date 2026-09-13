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
S3 RUN              = EXECUTED 2026-09-12. One real sealed execution under Aaron's
                      Owner decision AUTHORIZE ONE REAL SEALED X01 EXECUTION UNDER
                      GENERATED_NOT_SEEN. authorization_id X01-AUTH-0001,
                      run_id X01-RUN-0001, outcome_state COMPLETED_EVIDENCE.
                      The authorization is CONSUMED and can never authorize another
                      run; a further real attempt needs a new Owner authorization.
S4 VERDICT          = COMPLETE. Final Owner verdict recorded 2026-09-13.
CURRENT_VNEXT_STAGE = STOPPED — X01 is closed.
X01_LIFECYCLE_STATUS = CLOSED
FINAL_X01_VERDICT   = INSUFFICIENT_EVIDENCE (vNext S4 vocabulary)
KB_RESEARCH_STATUS  = unresolved — the knowledge-base schema has no
                      `insufficient_evidence` token, so both layers are recorded
                      side by side rather than one being substituted for the
                      other. No KB card exists for X01 and none was created here:
                      the knowledge base is a separate repository and writing the
                      first X01 card into it is a separate Owner decision.
FINAL_X01_CLAIM     = The paired historical evidence is insufficient to determine
                      whether the futures implementation preserved the ETF TSMOM
                      wrapper's performance within the preregistered 0.15 Sharpe
                      materiality tolerance. It establishes neither preservation
                      within that tolerance nor degradation beyond it. The point
                      estimate is negative and the 95% interval lies below zero,
                      but zero was not the sealed boundary and does not replace
                      -0.15 after the fact. Nothing here speaks to alpha
                      confirmation or falsification, out-of-sample validation,
                      deployment readiness, live profitability, causal mechanism,
                      or futures implementations in general.
INDEPENDENT_S4_JUDGMENT = ACCEPT_PROPOSED_VERDICT, MATERIAL_REASON = NONE.
                      Completed before this recording; no further reviewer is
                      required and none was called.
VERDICT_RECORDED_HERE = This file is the authoritative home of the final X01
                      verdict. research/extensions/DASHBOARD_v2.md still shows
                      X01 as PROPOSED and was deliberately NOT updated: it is a
                      frozen reviewed artifact whose hash is pinned both in
                      qros-state.yaml and inside validate_wave0.py, which is
                      itself pinned runner code, so editing it to write a status
                      field would mean changing frozen execution infrastructure
                      and rebuilding the execution manifest. Non-blocking and
                      disclosed rather than forced.
TARGET_X01_OUTCOME_GENERATED = YES — sealed artifact at
                      research/extensions/x01/X01_EVIDENCE.json, sha256
                      8a98af94c6eeb3067b041e53221d713c4281f8a0dd7e97eb00ac083046141d4f
TARGET_X01_OUTCOME_ACCESSED = YES — revealed 2026-09-12 under Aaron's Owner
                      decision AUTHORIZE REVEAL OF X01-RUN-0001 AND ENTER S4
                      VERDICT. Exposure classification for X01-RUN-0001 moved
                      GENERATED_NOT_SEEN -> REVEALED_TARGET_METRIC, recorded in
                      ops/EXPOSURE_LEDGER.md. The reveal read the existing
                      artifact only: no re-run, no recomputation from source
                      panels, no new authorization.
S4_DETERMINISTIC_EXTRACTION = DONE. Applying the sealed §5 rule to the stored
                      95% CI for ΔS against the sealed boundary −B = −0.15, the
                      interval spans the boundary, so
                      PRIMARY_PREREG_RESULT = UNRESOLVED, matching the artifact's
                      own stored classification
                      UNRESOLVED_INSUFFICIENT_PRECISION. Evidence integrity PASS
                      on every mechanical check.
AUTHORITATIVE_EVIDENCE = run X01-RUN-0001, authorization X01-AUTH-0001,
                      artifact research/extensions/x01/X01_EVIDENCE.json sha256
                      8a98af94c6eeb3067b041e53221d713c4281f8a0dd7e97eb00ac083046141d4f
                      against sealed preregistration
                      4db18f6cc084bf4a4ba9260e7ba81489e658d74adf03818aa4169208a40f54c5.
                      Sharpe(F) 0.4115061496832807, Sharpe(E) 0.6523207344790396,
                      dS -0.2408145847957589, 95% CI
                      [-0.4605709821173062, -0.0504890513489627] against the
                      sealed boundary -0.15. The interval spans the boundary, so
                      the sealed rule yields PRIMARY_PREREG_RESULT = UNRESOLVED.
SECONDARIES         = A1 is the primary futures arm. S1 and S2 are
                      DESCRIPTIVE_SENSITIVITY with S1_S2_PROMOTION_POWER = NONE
                      and did not change the verdict. The turnover diagnostic was
                      independently judged NON_BLOCKING and is not reopened.
NO_FUTURE_X01_RUN   = X01-AUTH-0001 is CONSUMED and active_authorizations is 0.
                      INSUFFICIENT_EVIDENCE is a legitimate terminal result, not
                      an invitation to retune: no parameter change, boundary
                      change, resampling, universe expansion, arm substitution or
                      repackaging of X01 follows from it. Any further work needs a
                      separate Owner decision and a genuinely new question.
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
TARGET_EXECUTION_AUTHORIZED = NO — the one grant on record is CONSUMED; there is
                      no active authorization. A seal is not authorization, and a
                      spent authorization is not a licence to run again.
TARGET_X01_OUTCOME_ACCESSED = NO — the evidence artifact has been GENERATED and
                      stored, and NOT seen. No Sharpe, ΔS, confidence interval,
                      bootstrap statistic or verdict has been read by any session.
X01_FIRST_EXECUTION_EXPOSURE_CLASSIFICATION = GENERATED_NOT_SEEN (Owner-sealed)
OPEN_MATERIAL_BLOCKERS = NONE recorded. The X01 draft reports
                      TECHNICAL_BLOCKERS = NONE and OWNER_DECISIONS_REMAINING = NONE.
NEXT_OWNER_DECISION = AUTHORIZE ONE REAL SEALED X01 EXECUTION under
                      GENERATED_NOT_SEEN — after housekeeping and a green rerun of
                      the minimal S3 readiness check. X01 target execution is NOT
                      authorized: zero authorization records exist, and a seal is
                      not authorization to execute.
```

## Time-Series Value — the next research question

```
RESEARCH_QUESTION   = Does fundamental cheapness relative to an asset's own prior
                      history predict higher subsequent excess returns, and does a
                      sleeve built on it add anything to the frozen TSMOM book?
FAMILY · ANCHOR     = FINANCIAL_ASSET_TIME_SERIES_VALUE · EXPANDING_OWN_HISTORY
S0 FRAME            = COMPLETE
S1 DESIGN+SEAL      = COMPLETE. SEALED 2026-09-13 under Aaron's Owner decision
                      SEAL TIME-SERIES VALUE S1. Sealed contract at
                      research/extensions/value/VALUE_PREREGISTRATION_DRAFT.md
                      (historical _DRAFT filename retained to avoid reference
                      churn; the document reads SEALED).
                      sealed sha256
                      844fea84d5f1dddc7da5cbaea4ead4af4f3fe3a15b4f0cd0dfb1a91a9948d1cb
                      at seal revision 9c9dd4c2fd400719ebd69925b8ef96c2a4bf6548,
                      carrying VALUE_S1_DATA_IDENTITY_AMENDMENT_001 (Sweden
                      two-table Fixed CPI; EUR coverage fact) and
                      VALUE_S1_COMPARATOR_IDENTITY_AMENDMENT_002 (§17, the frozen
                      TSMOM comparator identity). LINEAGE = original seal
                      df142f83...b3278cf at ba5814d8... -> _001
                      bc841ea8...a67a099 at 58129972... -> _002. Every prior seal
                      is SUPERSEDED, none erased. D1-D11 frozen and byte-identical
                      across all three seals; OWNER_DECISIONS_REMAINING = NONE.
COMPARATOR          = CANONICAL_17_ETF_TSMOM_BASELINE (§17). MAP_v2 §A.1 frozen
                      mechanism; signal per X01 §3.7 (SEALED); recomputed from the
                      X01-pinned panel 3d2a7a56... by the hash-pinned canonical
                      modules. NOT X01's E arm, which is four commodity ETFs with
                      the portfolio vol target and gross cap removed.
                      output/monthly_returns.csv is git-ignored and unhashed and is
                      NOT authority; it agrees with the recomputation at the
                      precision it was written to, as a diagnostic only.
S2 BUILD            = COMPLETE — orchestration, single-use authorization guard,
                      evidence schema, 25-check synthetic rehearsal over 11 cases,
                      119 S2 checks, 14 pre-S3 dry gates. No target outcome
                      computed; the S3 entry point refuses without an authorization.
S3 RUN              = NOT_STARTED. The 2026-09-13 authorization attempt was
                      HALTED at the run gate before any authorization object was
                      created; it is NOT an execution attempt.
                      AUTHORIZATION_CREATED = NO, AUTHORIZATION_CONSUMED = NO,
                      TARGET_CALCULATIONS_EXECUTED = NONE.
CURRENT_BLOCKER     = C3_STRUCTURAL_REACHABILITY = FAIL. On the real signal path
                      (§11 defines episodes from that path alone — no return,
                      Sharpe or correlation) FXY carries ONE constant-sign episode
                      spanning all 143 months, UUP 141, SPY 129. The sealed k = 3
                      selection therefore leaves 0, 2 and 14 months, all below the
                      24-distinct-month floor, so every leave-one-episode-out case
                      is invalid, C3 FAILS and candidacy is foreclosed whatever the
                      returns are. Confirmed with deliberately excellent synthetic
                      returns: C1 and C2 pass, C3 still fails. §13's reachability
                      check tests threshold algebra against hypothetical jackknife
                      inputs and never touches the signal path, so it could not
                      have caught this. Object A (standalone edge) remains
                      adjudicable; Object B (diversification candidacy) does not.
                      NOT repaired — k, the episode definition, the ranking, the
                      deletion operator and the distinct-month floor are all
                      sealed. Resolving this is an Owner decision.
EVALUATION_WINDOW   = 2014-07 .. 2026-05, N = 143 months. TLT (DFII20 from
                      2004-07 + 120-month warm-up) binds the start; the ETF price
                      panel, which ends 2026-06-12, binds the end.
UNIVERSE            = SPY, TLT, LQD, UUP, FXY (five instruments, four objects:
                      equity / duration / public corporate credit / FX real)
CREDIT_OBJECT       = BAA10Y, LQD only; HYG REMOVED. Explicit redefinition, frozen;
                      never to be described as an OAS or as high-yield Value.
DATA                = VALUE_DATA_PIT_READINESS = PASS. All legs acquired from
                      current official sources and pinned by sha256 in
                      VALUE_DATA_INVENTORY.json.
SHILLER_VINTAGE     = RECONSTRUCTED_HISTORICAL_SERIES_WITH_NON-VINTAGE_LIMITATION.
                      The 3-month publication lag fixes release timing only and
                      does NOT cure historical revision; no positive result may be
                      called strict vintage-PIT confirmation.
TARGET_OUTCOMES     = NONE COMPUTED. No Value return series, no Sharpe, no TSMOM
                      correlation, no combination result, no backtest. The signal
                      PATH has been computed (episode structure only), which §11
                      defines independently of any return.
NEXT_OWNER_DECISION = the C3 reachability blocker above: accept that Object B is
                      unadjudicable under the sealed design and run for Object A
                      alone, or amend the sealed episode machinery. Not an agent
                      decision.
```

## X01 — path to the seal under vNext — TAKEN 2026-09-13

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
