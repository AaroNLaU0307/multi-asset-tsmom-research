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

## C-A — canonical TSMOM prospective confirmation — S1 SEALED 2026-09-13

```
RESEARCH_QUESTION   = Does the canonical 17-ETF multi-asset TSMOM strategy's expected
                      raw net Sharpe (rf = 0, 2 bps) remain positive and economically
                      material -- at least +0.30 -- over a genuinely prospective window?
RESEARCH_ID · LANE  = TSMOM-CA-001 · FULL
S0 FRAME            = COMPLETE. Fable frame -> Opus outcome-blind feasibility -> Astra
                      xHigh challenge -> Fable prospective design -> bounded repair ->
                      Fable Owner-decision advisory -> independent Astra OD-1/OD-2
                      advisory -> Aaron's Owner decisions.
S1 DESIGN+SEAL      = COMPLETE. **SEALED 2026-09-13T17:42:06Z** under Aaron's Owner
                      authorization `SEAL C-A` (OD-8, ops/OWNER_DECISION_RECORD_PHASE_B.md
                      §6E). Sealed contract at
                      research/extensions/ca/CA_PREREGISTRATION_DRAFT.md (historical
                      _DRAFT filename retained to avoid reference churn, exactly as the
                      Value contract did; the document reads SEALED).
                      The seal changed STATUS METADATA ONLY: §A-§Z are byte-identical to
                      the pre-seal bytes Aaron accepted.
OWNER_DECISIONS     = OD-1 materiality +0.30 / -0.20, strict crossing ·
                      OD-2 N_scored = 120, ONE terminal reveal, no interim look, no
                      adverse oracle, no automatic extension ·
                      OD-3 FM-1 complementary only ·
                      OD-4 ALL_17_REQUIRED ·
                      OD-5 ONE central 95% stationary-bootstrap percentile interval,
                      block length 12, 10,000 replicates ·
                      OD-6 FM-1 rf = FRED DGS3MO, <= 7 calendar days, Y/100/12, no
                      fallback · OD-7 FM-1 sign-vs-zero only, no materiality floors ·
                      OD-8 SEAL C-A.
CB REPAIRS SEALED IN = CB-1 first scored month requires a post-PROSPECTIVE_START decision ·
                      CB-2 S_0 and S_G distinct · CB-3 S1/S2 gates separate ·
                      CB-4 C-D spec is a DRAFT only.
PC-1                = CLOSED from existing §J authority. The S_0-vs-frozen overlap is
                      classified MECHANICAL_CORRECTION (no action) under the §J
                      split/dividend back-adjustment row, on that row's own declared
                      test: max abs delta position 1.348102e-04 against 0.01, and 0 sign
                      flips, over 402 decision months and 6,477 position cells, computed
                      strictly inside the frozen window ending 2026-06-12.
                      NO new daily-return tolerance was created.
S2 BUILD            = NOT STARTED and NOT AUTHORIZED.
S3 RUN              = NOT AUTHORIZED. TARGET_RUN_AUTHORIZED = NO. No record exists in
                      ops/EXECUTION_AUTHORIZATIONS.md for C-A, and a seal is not
                      permission to execute.
PROSPECTIVE STATE   = T4_SEAL_EXISTS = YES, but the scoring stream has NOT started.
                      PROSPECTIVE_START = max(SEAL_TIMESTAMP, PIPELINE_GO_LIVE) and
                      PIPELINE_GO_LIVE does not exist. S_G_CREATED = NO.
                      N_scored = 0. FIRST_ELIGIBLE_SCORED_PERIOD = NOT YET DETERMINED.
                      No accrued pre-go-live month may ever be retroactively scored.
TARGET_OUTCOMES     = NONE COMPUTED, NONE REVEALED.
SB-3                = OPEN -- blocks C_D_PASS ONLY. It never blocked the C-A S1 seal.
C-B                 = PARKED.
NEXT_OWNER_DECISION = S2 BUILD AUTHORIZATION for C-A (and, separately, C-D
                      implementation authorization). Both are distinct gates that this
                      seal did not consume.
```

### C-A sealed identity

Recorded per the X01 / Value convention: the sealed bytes and the seal revision.
All artifacts are stored LF (`.gitattributes` `eol=lf`), so each SHA-256 below is
the working-copy **and** the git-blob identity and reproduces from any checkout
regardless of `core.autocrlf`.

| artifact | SHA-256 |
|---|---|
| sealed preregistration `research/extensions/ca/CA_PREREGISTRATION_DRAFT.md` | `9a41d7cf2055b5212d8517fa11fbde08218e2b6d2b92e39cbd2081ee9eea882b` |
| Owner Decision Record `ops/OWNER_DECISION_RECORD_PHASE_B.md` | `cc6a297abbb06b1e9711cd311d933cd52523784cba3899f2251b7e22c46d5603` |
| C-D verification spec at seal time `research/extensions/cd/CD_VERIFICATION_SPECIFICATION_DRAFT.md` | `c8db66dfe0dd064d4f4c6af4d574a840bf6f5180f3528748152dad7101ad1a5c` |
| instrument registry `research/extensions/ca/CA_INSTRUMENT_REGISTRY.json` | `8dd261fd1b5487af023f07ba230c4cdc8e43b14197f1f09d9e086cb20d26ed65` |
| snapshot registry `research/extensions/ca/CA_SNAPSHOT_REGISTRY.md` | `3a563aee06b145672a65e77cd0b25697406b7fcff66e46d1c410ff3e17c5b933` |
| validator `research/extensions/ca/ca_prereg_validate.py` | `95b9ade8c02caa5733031e30b9ac47fbbbcc5ceca428efda59bd8b5cfb8c9f8f` |
| validator `research/extensions/ca/ca_synthetic_reachability.py` | `c7d996cc91aee2b69033c35578c7bc4d97f71693242a56be6b7a42629ba6f81a` |
| builder `research/extensions/ca/ca_instrument_registry_build.py` | `25872777696f06fc2221b6c35fe2e6ea3e90d33df828ac52ae83ee81dd3c36b7` |
| `S_0` `data/prospective/S0_20260913T165624Z.csv` (git-ignored; 3,323,945 bytes; acquired 2026-09-13T16:56:24Z–16:57:01Z; 1993-01-29 → 2026-09-11; 30/30 tickers) | `c4a21dc86038f9f0d06e32a267810b46cb39d9dd3549c35ef3329c87f884d6fb` |
| frozen historical panel `data/close_prices_raw.csv` | `3d2a7a56dbd92d4ff8138cfd894c87f5ac5ac088a11165db870673e0c05c3c31` |

```
C_A_SEAL_REVISION = __REVISION__
```

`S_0` and its sidecars stay outside git because `data/` is git-ignored for vendor
licensing; their exact path, SHA-256, byte size and acquisition identity are pinned
here in tracked sealed state, which is what makes them durable.

---

## Time-Series Value — CLOSED 2026-09-13

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
                      f5f377b195d3ba2081e772b675d251d3adc036511133a461a823f72ddd6582ee
                      at seal revision 0ed9bfff2205a61ad048aca1ef3607991ddef460,
                      carrying VALUE_S1_DATA_IDENTITY_AMENDMENT_001 (Sweden
                      two-table Fixed CPI; EUR coverage fact) and
                      VALUE_S1_COMPARATOR_IDENTITY_AMENDMENT_002 (§17, the frozen
                      TSMOM comparator identity) and
                      VALUE_S1_EPISODE_REACHABILITY_AMENDMENT_003 (§18, the C3
                      contribution-ablation operator). LINEAGE = original seal
                      df142f83...b3278cf at ba5814d8... -> _001
                      bc841ea8...a67a099 at 58129972... -> _002
                      844fea84...9948d1cb at 9c9dd4c2... -> _003. Every prior seal
                      is SUPERSEDED, none erased. D1-D10 byte-identical across all
                      four seals; D11 carries the authorized textual C3 operator
                      change with k = 3 itself unchanged; every numerical threshold
                      unchanged. OWNER_DECISIONS_REMAINING = NONE.
C3                  = CONTRIBUTION_SENSITIVITY_ROBUSTNESS via individual
                      selected-episode contribution ablation (§11.1 as amended).
                      V_t = a_t + sum_i c_i,t on the ORIGINAL portfolio capital
                      basis; V^(-e) removes instrument i(e)'s own attributed net
                      contribution in the mapped contribution months (signal month
                      m -> contribution month m+1). Every calendar month is
                      retained; no resizing, vol re-targeting, gross re-scaling or
                      capital redistribution; ablations are never cumulative.
                      It does NOT test TEMPORAL_REGIME_ROBUSTNESS, and
                      shared-regime dependence may remain because the other
                      instruments keep contributing in the same calendar regime.
COMPARATOR          = CANONICAL_17_ETF_TSMOM_BASELINE (§17). MAP_v2 §A.1 frozen
                      mechanism; signal per X01 §3.7 (SEALED); recomputed from the
                      X01-pinned panel 3d2a7a56... by the hash-pinned canonical
                      modules. NOT X01's E arm, which is four commodity ETFs with
                      the portfolio vol target and gross cap removed.
                      output/monthly_returns.csv is git-ignored and unhashed and is
                      NOT authority; it agrees with the recomputation at the
                      precision it was written to, as a diagnostic only.
S2 BUILD            = COMPLETE — orchestration, contribution ledger, ablation
                      operator, single-use authorization guard, evidence schema,
                      46-check synthetic rehearsal over 12 cases, 119 S2 checks,
                      16 pre-S3 dry gates, all green. No target outcome computed;
                      the S3 entry point refuses without an authorization.
S3 RUN              = COMPLETE. Exactly ONE real sealed execution, 2026-09-13,
                      under a single-use Owner authorization.
                      AUTHORIZATION_ID = VALUE_S3_AUTH_60e4ad292aa74bce
                      RUN_ID           = VALUE_S3_RUN_60e4ad292aa74bce
                      AUTHORIZATION_CONSUMED = YES. No rerun, no retry, no second
                      authorization, no retuning, no data refresh.
S4 VERDICT          = COMPLETE. Reveal and deterministic adjudication 2026-09-13;
                      every verdict recomputed from the stored interval bounds and
                      agreeing with the stored labels.
VALUE_LIFECYCLE_STATUS = CLOSED
FINAL_VALUE_VERDICT = MATERIALLY_ADVERSE UNDER THE SEALED CONSTRUCTION;
                      DIVERSIFICATION CANDIDACY FAILED; FULL NOT EXECUTED.
                      Aaron's final Owner verdict, recorded 2026-09-13. This file
                      is the authoritative home of that verdict.
AUTHORITATIVE_EVIDENCE = research/extensions/value/VALUE_EVIDENCE.json
                      sha256 c8b37d513489344d8e8012963a894ea11f007249354410bf83f8129bc0d11b8b
                      IMMUTABLE. Never edited.
PROVENANCE_CORRECTION = research/extensions/value/VALUE_EVIDENCE_PROVENANCE_CORRECTION_001.json
                      sha256 fbe793c40feffc0a6555fb4af0b54abcb71fa1399f004e441550632ba340b311
                      Provenance metadata only; SCIENTIFIC_RESULT_CHANGED = NO.
S4_EVIDENCE         = VALUE_SHARPE = -1.030455,
                      CI95 = [-1.559647, -0.545022]  (10000/10000 valid)
                      STANDALONE_VALUE_STATE = MATERIALLY_ADVERSE
                      C1 = FAIL
                      VALUE_TSMOM_PEARSON_RHO = -0.217239,
                      CI95 = [-0.383617, -0.059500]  (10000/10000 valid)
                      C2 = PASS  (rho_upper -0.0595 <= 0.40)
                      C3 = FAIL  (0 of 3 contribution-ablation cases pass)
                      DIVERSIFICATION_CANDIDACY = FAIL
                      FULL_EXECUTED = NO — the sealed conditional branch stopped
                      at candidacy, so NO combination statistic exists. FULL is
                      recorded as NOT EXECUTED, never as adverse and never as
                      not-established.
C3_RECORD           = CONTRIBUTION_SENSITIVITY_ROBUSTNESS via INDIVIDUAL
                      INSTRUMENT-EPISODE CONTRIBUTION ABLATION. All three cases
                      were VALID and retained all 143 evaluation months; all three
                      remained MATERIALLY_ADVERSE, failed C1, passed C2 and failed
                      their individual case. Episodes: FXY 2014-07..2026-05 (143
                      signal months, 142 contribution months), UUP 2014-09..2026-05
                      (141/140), SPY 2014-07..2025-03 (129/129). This is NOT
                      temporal-regime robustness, NOT temporal-regime replication,
                      NOT independent episode replication and NOT independent
                      valuation-regime confirmation. The very long FXY and UUP
                      episodes remain an explicit limitation.
DECISIVENESS        = The standalone 95% interval lies WHOLLY below the
                      preregistered -0.15 adverse floor, so the adverse margin is
                      reliably excluded. This is a decisive negative for the tested
                      construction — distinct from UNRESOLVED_EDGE, from
                      insufficient power, from a non-adjudicable branch, and from a
                      simple failure to exceed a positive threshold.
SCOPE_OF_VERDICT    = The ONE frozen construction actually tested. NOT evidence
                      that Time-Series Value is disproven generally, that Value has
                      no economic mechanism, that all Value implementations fail,
                      that every Value subcomponent independently lacks edge, or
                      anything about an untested allocation, universe,
                      normalisation or signal definition.
KB_RESEARCH_STATUS  = not_promoted (strategy) / not_promoted (finding), the
                      registry's existing vocabulary. `falsified` is reserved by
                      the KB convention for negatives established via multiple
                      independent decisive tests with nothing material left
                      untried; this is one sealed construction, so `not_promoted`
                      with the declared margin is correct.
KB_CARDS            = strat.tsmom.time-series-value-sleeve
                      finding.tsmom-time-series-value.materially-adverse
                      plus 3 relationship rows (tested_on,
                      must_not_be_retested_on_same_sample, benchmarked_against).
CURRENT_BLOCKER     = NONE.
MAINTENANCE_ITEM    = NON-SCIENTIFIC, RESOLVED 2026-09-13 (post-closure). value_orchestrator.py emitted
                      AMENDMENT_LINEAGE using a stale hardcoded AMENDMENT_002
                      label paired with the live seal constants, so the terminal
                      row carried the correct _003 identities under the wrong
                      label and the genuine _002 row was absent; and the evidence
                      schema checked that AMENDMENT_LINEAGE was present but not
                      that it was internally consistent. Bounded and corrected by
                      the immutable sidecar above. It did NOT invalidate the real
                      run: the two fields that bind the run to a contract
                      (SEALED_PREREG_SHA256, SEAL_REVISION) were correct, and the
                      in-run conformance check passed 53/53 against the _003
                      contract. REPAIRED for FUTURE evidence only: the lineage
                      is now defined once as value_contract.AMENDMENT_LINEAGE and
                      emitted via lineage_records(), never hand-assembled, and
                      value_evidence.validate() now rejects a wrong entry count, a
                      duplicate or mislabelled amendment, a label paired with the
                      wrong seal revision or sealed sha256, a non-active terminal
                      entry and out-of-order lineage. Verified non-vacuous: the
                      historical artifact is rejected by the new validator with 5
                      lineage problems. The historical artifact was NOT rewritten
                      and NOT regenerated; it remains authoritative, bounded by the
                      correction sidecar. No run, authorization, evidence
                      regeneration or recomputation was triggered.
MAINTENANCE_ITEM_2  = NON-SCIENTIFIC, RESOLVED 2026-09-13 (post-closure). The Value run artifacts were written
                      with platform line endings, so on disk they are CRLF while
                      git stores LF (.gitattributes covers *.md/*.csv/*.py, not
                      *.json; core.autocrlf = true). The recorded SHA256s are of
                      the WORKING-COPY bytes and reproduce on a machine with
                      autocrlf = true, but NOT from the blob bytes directly. X01
                      differs: X01_EVIDENCE.json is LF both on disk and in the
                      blob. The artifacts were deliberately NOT rewritten — the
                      Owner decision forbids editing them, and normalising them
                      now would change the very hashes this record, the sidecar
                      and the KB cards all cite. RESOLVED by exact-byte
                      retention instead: .gitattributes now carries `-text` for
                      exactly those three paths, and they were re-indexed from the
                      already-authoritative working-copy bytes. The git blob is now
                      byte-identical to the working copy for all three, so the
                      recorded SHA256s are reproduced by any checkout regardless of
                      the user's core.autocrlf. Verified on a fresh detached
                      worktree: all three hashes REPRODUCED. The artifacts
                      themselves were never edited — only how git stores them — so
                      every recorded hash still means the bytes the real run
                      produced. Repo-wide JSON policy unchanged.
ARTIFACT_BYTE_CONVENTION = The three immutable Value run artifacts are retained
                      EXACT-BYTE: working-copy bytes == git blob bytes, and the
                      recorded SHA256 is of those bytes. This is the unambiguous
                      identity for any future verifier.
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
TARGET_OUTCOMES     = COMPUTED ONCE and REVEALED_FOR_S4 under Aaron's explicit
                      S4 authorization. Recorded above and in the immutable
                      evidence artifact.
EVIDENCE_CEILING    = T0 / POST-EXPOSURE / AT MOST SUPPORTED. This study is never
                      CONFIRMED and never INDEPENDENTLY_CONFIRMED.
ASTRA               = NOT CALLED. The inherited rule attaches an Astra xHigh
                      evidence-to-claim challenge to a consequential FULL result;
                      FULL never executed, so there is no consequential FULL claim
                      and no review round was manufactured.
NEXT_OWNER_DECISION = NONE. The lineage is CLOSED. Any alternative horizon,
                      warm-up, universe, threshold, CPI source, credit object, FX
                      basket, risk split, sizing, episode definition or evaluation
                      window would be a NEW research question requiring a fresh
                      S0 -> S1 lineage, and none is opened here.
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
