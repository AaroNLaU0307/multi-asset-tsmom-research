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

## CTA-EDGE-04-MMV — macro momentum on vintage data — S3 CORRECTED, CLASS D 2026-09-17

*State only, never workflow authority (vNext §0).*

```
RESEARCH_QUESTION   = Does the DIRECTION OF CHANGE in a small predeclared set of
                      macroeconomic series - measured only from information actually
                      published by the decision date - predict the direction of
                      subsequent asset-class returns, SEPARABLY from the asset-return
                      trend the canonical book already trades?
RESEARCH_ID · LANE  = CTA-EDGE-04-MMV · not yet assigned (S0)
ORIGIN              = Fable Round-1 discovery map, family F5 MACRO_MOMENTUM_VINTAGE.
                      Authority 2026-09-15-cta-edge-discovery-r1-mechanism-feature-map-
                      fable-01.md sha256 02ca5f45fe41763e55a353090645c3b2a98b6dcf5fce
                      572623ede604e569344a, re-verified at this S0.
S0 FRAME            = COMPLETE / **PASS AFTER OWNER RESOLUTION** (2026-09-16).
                      Artifact research/extensions/mmv/MMV_S0_FRAME.md
S1 DESIGN+SEAL      = **COMPLETE / SEALED 2026-09-17**.
                      Contract research/extensions/mmv/MMV_PREREGISTRATION.md
                      sha256 4bad9f0bcdb7e4991ab920d12e24a60f4d237205e5a43af693a8dada
                      db56b225. Seal research/extensions/mmv/MMV_SEAL_MANIFEST.md.
                      Owner decisions MMV-OD-1..OD-6 are recorded and binding:
                      ops/OWNER_DECISION_RECORD_CTA_EDGE_04_MMV.md
                      The 2026-09-16 HOLD record is RETAINED UNEDITED as history.
S2 BUILD            = **COMPLETE / PASS 2026-09-17**, SYNTHETIC VALIDATION ONLY.
                      Branch cta-edge/macro-momentum-vintage-s2 from the sealed
                      commit cdb01fd. Record research/extensions/mmv/
                      MMV_S2_BUILD.md. Engine research/extensions/mmv/engine/
                      (pit, policy, legs, votes, gate05, concordance, risk, start).
                      Seal and preregistration hashes VERIFIED at build time; the
                      validator asserts no sealed artifact was modified.
S2 VALIDATION       = **151/151 PASS** synthetic (research/extensions/mmv/
                      mmv_s2_validate.py) + **32/32 PASS** data-layer parser check
                      (mmv_s2_parser_check.py). Groups SEAL 4 / PIT 16 / POLICY 20
                      / LEGS 27 / VOTES 27 / GATE05 19 / CONCORD 7 / RISK 15 /
                      START 7 / FIREWALL 9. All 27 macro states enumerated; all 9
                      growth pairs tested as nine separate named tests; FXY == -UUP
                      across all 27; missing-not-zero across all 15 instruments x 3
                      legs; Gate 0.5 boundary 79/100 and 799/1000 PASS, 80/100 and
                      800/1000 KILL.
S2 STRUCTURAL GUARDS = Three sealed clauses are enforced by construction rather
                      than by a deletable test: (1) no function or constructor in
                      engine/policy.py accepts a vintage/realtime/catalog
                      parameter, so the S1 metadata defect is UNEXPRESSIBLE, not
                      merely tested against; (2) votes.raw_direction RAISES
                      NotInDomain for VNQ/RWX rather than returning 0 or UNDEFINED;
                      (3) the coefficient table is a MappingProxyType constant with
                      no override hook. All macro arithmetic is exact Fraction, never
                      float - an epsilon would itself be a forbidden threshold, and
                      the kill gate fires on equality.
S2 ARITHMETIC       = EXACT. Values parse from decimal strings to Fraction; the
                      Gate 0.5 comparison is Fraction(agree, eligible) >=
                      Fraction(4,5).
S1 CHECK AFTER BUILD = STATED, NOT HIDDEN. mmv_preseal_check.py is a SEALED S1
                      artifact and was NOT modified. Against the sealed commit in a
                      clean worktree it still reports 38/38 PASS. Against the S2
                      tree it reports 36/38: groups A/B/C remain 33/33, and the two
                      D-group failures are correct behaviour from a check that
                      asserts "no implementation exists yet" - D1 flags the filename
                      engine/gate05.py, D2 flags the validator importing pandas and
                      defining tests whose NAMES contain position/sharpe/bootstrap/
                      agreement (they are the tests that enforce the firewall).
                      Modules and tests were NOT renamed to keep the sealed check
                      green. See MMV_S2_BUILD.md section 6.
S1_BLOCKERS         = **NONE** (resolved 2026-09-17). Both former blockers cleared.
                      ALFRED_API_ACCESS is CLEARED: the freeze ran and all six sealed
                      inputs are pinned (research/extensions/mmv/
                      MMV_RAW_DATA_MANIFEST.md; raw bytes in git-ignored data/mmv/).
                      The freeze SURFACED a new unbound choice - UNBOUND-4, the
                      availability semantics of the administered policy leg.
                      ALFRED carries NO genuine availability metadata for it: every
                      DFEDTAR observation from 1982-09-27 to 2008-12-15 has
                      realtime_start = 2008-12-15, the day the series was
                      DISCONTINUED, and DFEDTARU's earliest realtime_start is
                      2014-04-03 although the target RANGE has been public since
                      2008-12-16. Those are FRED series-creation artefacts, not
                      information availability.
                      MMV-OD-1's PRINCIPLE ("as publicly known at that cutoff") and its
                      MECHANISM ("one ALFRED vintage valid at that date") diverge here
                      and only here. Taken literally the mechanism leaves the policy leg
                      UNDEFINED on 71 of 218 canonical decision dates, and the policy
                      leg has a non-zero coefficient for 9 of the 15 mapped instruments
                      - so 9 instruments go undefined across roughly a third of the
                      sample. Undefined cells leave the Gate 0.5 denominator, so the
                      choice MOVES THE KILL GATE before any return exists.
UNBOUND-4 RESOLUTION = **RESOLVED_BY_EXISTING_AUTHORITY** (controller, 2026-09-17).
                      NOT accepted as a new scientific blocker: policy availability was
                      ALREADY BOUND PRE-OUTCOME by the official FOMC / Federal Reserve
                      announcement date and time. NEW_SCIENTIFIC_CHOICE = NO.
                      MMV_OD_7_CREATED = NO. MMV-OD-1..OD-6 NOT reopened. Fable NOT
                      consulted. ALFRED_REALTIME_START_USED_FOR_AVAILABILITY = NO;
                      OFFICIAL_FOMC_ANNOUNCEMENT_USED_FOR_AVAILABILITY = YES.
                      The discovered mismatch is NOT hidden: preregistration section
                      B.2 states it in full and classifies it a FRED/ALFRED
                      SERIES-METADATA LIMITATION, not historical unavailability;
                      pre-seal check B10 reproduces the 71/218 and 9/15 figures the
                      rejected reading would have cost. Record research/extensions/
                      mmv/MMV_S1_HOLD_RECORD.md section 10 (retained unedited).
FOMC TIMING FREEZE  = COMPLETE 2026-09-17. Exactly SIX canonical month-end decision
                      dates are also FOMC announcement dates (2013-07-31, 2014-04-30,
                      2018-01-31, 2019-07-31, 2024-01-31, 2024-07-31), derived from the
                      committed TA_MACRO_CALENDAR.csv intersected with the canonical
                      month-ends. Four carry an official 2:00 p.m. ET release time and
                      admit the newly announced target. Two (2013-07-31, 2014-04-30)
                      say "For immediate release" with NO clock time on the statement
                      page, the 2013 historical calendar OR the current FOMC calendar,
                      so the sealed fallback retains the PREVIOUS target. All six
                      resolve DETERMINISTICALLY; nothing is guessed. Manifest
                      data/mmv/MMV_FOMC_TIMING_MANIFEST.json sha256 be6f17afdf77aafc7
                      d44bee593a1a94a01bb9b9474112cd197e6ed177737c4f9.
DATA FREEZE         = COMPLETE 2026-09-16T19:37Z. INDPRO 1,222 vintages from 1927-01-26;
                      PAYEMS 859 from 1955-05-06; CPILFENS 358 from 1996-12-12;
                      DFEDTAR/L/U splice verified CONTIGUOUS at 2008-12-15/16 with no
                      gap or overlap. CPILFENS has exactly ONE reference date with no
                      value in any vintage (2025-10-01), cause NOT asserted, already
                      governed by MMV-OD-6 section 11.7 (missing -> UNDEFINED, never 0,
                      counted and reported). No forbidden series was requested. The
                      credential was never printed, written to a file or committed.
MMV-OD-6            = DECIDED 2026-09-17, before any feature, position, separability
                      percentage or return existed. Closes all three previously
                      unbound scientific choices. Fable advice artifact sha256
                      ff413cfa46cc4aa8919731d9fe52adbb4abbf58b8514447e84934375e5dfc443
                      VERIFIED; Fable remains DESIGN-EXPOSED / NOT INDEPENDENT.
                      GROWTH     G = sign(sign(D12 INDPRO) + sign(D12 PAYEMS)),
                                 sign(0)=0; opposed measures abstain, a silent measure
                                 does not veto.
                      ARCHITECTURE asset-specific votes, never a global scalar:
                                 raw(i,t) = sign(c_iG*G + c_iI*I + c_iP*P); ties -> 0
                                 with no priority theme; a zero leg abstains; a MISSING
                                 leg -> UNDEFINED, never 0, counted and reported.
                      COEFFICIENTS all in {-1,0,+1}, so there is no weight to tune.
                                 Equity (+1,0,-1) - duration (-1,-1,-1) -
                                 credit (+1,0,0) - commodities (0,+1,0) -
                                 UUP (0,+1,+1) - FXY (0,-1,-1).
                      REAL ESTATE VNQ and RWX are NOT_MAPPED: weight 0 always, and
                                 UNDEFINED in Gate 0.5, entering NEITHER numerator nor
                                 denominator. Coding them as signal 0 would inject
                                 mechanical disagreement every month IN MMV'S FAVOUR
                                 and corrupt the kill gate.
                      DOMAIN     15 mapped ETFs drawn from the canonical 17. The claim
                                 must NOT say "all canonical 17 ETFs"; corrected in
                                 research/extensions/mmv/MMV_S0_AMENDMENT_01.md.
                      LQD/HYG    credit class only, raw = G. Recorded as a PRE-OUTCOME
                                 CATEGORICAL OWNER COMPLETION; F5 did NOT itself
                                 resolve the credit/duration ambiguity.
PRE-SEAL CHECK      = **38/38 PASS** (research/extensions/mmv/mmv_preseal_check.py,
                      2026-09-17). A freeze integrity / B point-in-time + information
                      concept / C sealed definitions / D outcome firewall. Verifies
                      mechanically: 19 raw files present with reproducing hashes and
                      byte counts; recorded coverage RECOMPUTES from the frozen bytes;
                      no credential-shaped token in any of 351 tracked files;
                      INDPRO/PAYEMS/CPILFENS latest-known-as-of reconstruction valid at
                      all 218 decision dates with enough reference months for the
                      sealed transform; NO final-revised leakage exhaustively over 218
                      dates x 3 series; output_type=1 everywhere; CPILFENS missingness
                      exactly one date under the sealed UNDEFINED rule; splice
                      contiguous at 2008-12-16; all 6 FOMC collisions pinned to Federal
                      Reserve bytes and deterministic; ALFRED realtime_start NOT the
                      policy clock; OD-1..OD-6 present and no OD-7; 15 mapped exact;
                      VNQ/RWX excluded from BOTH sides of Gate 0.5; Gate 0.5 kill
                      boundary 80.0% INCLUSIVE; all 27 (G,I,P) states enumerated; and
                      the outcome firewall intact by directory walk + AST scan.
CONSTRUCTION CHECKS = 15/15 PASS, arithmetic only over the 27-state {-1,0,+1} space:
                      growth truth table exact; exactly 15 mapped; VNQ/RWX absent from
                      the coefficient table; LQD row exact; FXY == -UUP in all 27
                      states; GLD == I; LQD == G; XLE/XLU == sign(G-P); tie rule; zero
                      = abstention not veto; raw always in {-1,0,+1}. No series, no
                      price and no outcome was touched. SUPERSEDED by the 38/38
                      pre-seal check above, which subsumes all fifteen.
VERIFIED AND NOT BLOCKING = canonical risk wrapper matches the brief EXACTLY
                      (config.py: VOL_WINDOW_DAYS 60, TARGET_VOL_ANNUAL 0.10,
                      MAX_ASSET_WEIGHT 2.0, equal weight, PORT_TARGET_VOL_ANNUAL 0.10,
                      MAX_GROSS_LEVERAGE 3.0, TRANSACTION_COST_BPS 2.0); the 15:45 ET
                      cutoff is COMPATIBLE and strictly conservative against the
                      canonical decide-at-close / execute-next-session convention
                      (src/portfolio.py:148); the DFEDTAR -> DFEDTARL/U splice at
                      2008-12-15/16 is the OFFICIAL series boundary, verified on FRED.
HOLD_REASON (RESOLVED by MMV-OD-1; retained as history)
                    = MMV-OD-1, the REAL-TIME INFORMATION CONCEPT. F5 says "on
                      point-in-time (ALFRED) vintages" and never confronts the
                      difference between (A) a chain of FIRST RELEASES - what the
                      investor LEARNED, ALFRED output_type=4 - and (B) a SINGLE VINTAGE
                      SNAPSHOT as-of the decision date - what everything published by
                      then implied, ALFRED vintage_dates. Both are point-in-time, both
                      are obtainable with one documented API parameter, and they encode
                      different theories of what the investor responds to. Under (B) an
                      annual payroll benchmark revision or a February CPI seasonal-factor
                      revision moves today's signal with no new information about the
                      current month. The affected series are exactly F5's two
                      most-defensible legs. Not a feasibility question; purely
                      scientific; cannot be deferred past S1 without making the study
                      unfalsifiable.
FIXED BY F5, PRESERVED = the transform (12-MONTH CHANGE, SIGN-ONLY), the series family
                      (F5.b inflation and F5.c policy most defensible, F5.a growth as
                      declared third leg), the cross-asset directional mapping table,
                      and the cheap PnL-free gate.
OUTCOME FIREWALL    = INTACT AT SEAL. HISTORICAL_MACRO_FEATURE_COMPUTED = NO /
                      HISTORICAL_MMV_POSITIONS_COMPUTED = NO /
                      SEPARABILITY_RESULT_COMPUTED = NO /
                      GATE_05_AGREEMENT_RATE_COMPUTED = NO /
                      FIRST_RELEASE_DISAGREEMENT_COMPUTED = NO /
                      RETURN_OUTCOME_ACCESSED = NO / BACKTEST_RUN = NO.
                      Enforced by checks D1-D5, not asserted.
CHEAP GATE          = monthly SIGN AGREEMENT between the macro composite and the
                      canonical composite, per instrument and pooled, months <=
                      2026-06-12; stop above a declared bound (~80%) with reason
                      `not_separable_at_position_level`. The benchmark side is ALREADY
                      ON DISK (output/monthly_signal_panel.csv, 17 x 402, 1993-01-31..
                      2026-06-30). NOT RUN AT S0 - designed only, runs after
                      preregistration.
SETTLED AT S0       = MACRO_SIGNAL_CONSTRUCTIBLE_WITHOUT_PRICE = YES, conditional on
                      F5.c resolving to the ADMINISTERED POLICY RATE. The 2-year
                      Treasury yield is EXCLUDED BY RULE: it is a traded price
                      mechanically tied to SHY/IEF/TLT returns inside the traded panel.
                      Vintage coverage verified on ALFRED: PAYEMS from 1955-05-06
                      (~850+ vintages), CPIAUCSL from 1972-07-21 (~650+), PCEPILFE from
                      2000-08-01 (~314) - all decades before the 2008-05 window.
DATA POSITION       = NEW_PAID_ENTITLEMENT_REQUIRED = NO. FRED/ALFRED requires a
                      self-service registration key; the terms page checked does not
                      state a fee and a registration key is NOT an institutional
                      entitlement - categorically unlike the LSEG/ICE problem that
                      closed PINS. No vintage data and no ALFRED-aware code exists in
                      the repository yet; nothing was fetched.
PRICE_SAMPLE_REUSE  = ETF panel BURNED / context T0 (KB-1, 6 of 6,
                      must_not_be_retested_on_same_sample, D-ETF-COUNT open).
MACRO_DATA_REUSE    = ALFRED vintages NEW. The REVISED counterparts of some series were
                      used by the closed Value lineage - a different object, declared.
TRIAL_FAMILY_OVERLAP = LOW. No macro-CHANGE signal has ever been built here. No family
                      declared at S0.
EVIDENCE_CEILING    = supported. A new ALFRED vintage leg does not launder a reused
                      price sample.
DESIGN EXPOSURE     = FABLE_DESIGN_EXPOSED = YES (originated F5; barred from blind
                      certification; advising on MMV-OD-1 will not restore
                      independence). ASTRA_DESIGN_EXPOSED = NO, but recorded as an
                      INFERENCE FROM ABSENCE: Astra's Round-1 output is not persisted
                      anywhere in this workspace (REVIEWER_EXPOSURE_LOG S32/S38 carry
                      the same gap). Seat rows are written AT SEAL, not at S0.
OUTCOME EXPOSURE    = NONE. No macro feature, composite, position, return, regression,
                      Sharpe or hit rate was computed; no famous macro episode was
                      inspected against candidate returns. No exposure-ledger row was
                      written, following the TA / BENB / PINS S0 precedent.
POLICY SCHEDULE     = **FROZEN / PASS 2026-09-17**. Closes the S3_PREREQUISITE
                      recorded at S2. Record research/extensions/mmv/
                      MMV_POLICY_SCHEDULE_FREEZE.md. Schedule research/extensions/
                      mmv/MMV_POLICY_ANNOUNCEMENT_SCHEDULE.csv sha256 ae34bf1e192c
                      4355fb71136a3e3017dfd07525ac8e48d7d3ea102130fa6a11da.
                      42 regimes, 2006-06-29 .. 2025-12-11 effective. Window
                      derived: targets needed from 2007-05-31 because the leg
                      reads target(t-12m). SCIENTIFIC_CHOICE = NONE; this is
                      data-authority completion only.
                      METHOD each regime matched to the OFFICIAL Federal Reserve
                      press release that STATES that exact target. Acceptance is
                      DOCUMENT CONTENT; proximity is never the criterion. 42/42
                      sources on federalreserve.gov, each hashed; the validator
                      re-opens every cached page and re-confirms the target.
                      WHY NO HEURISTIC the Fed's own footnote ("On July 10, 2024,
                      this date was corrected from March 3, 2020, to March 4,
                      2020") shows its date column is EFFECTIVE, not announcement.
                      Offsets are BOTH 0 and -1 days, so no fixed lag works. The
                      committed TA_MACRO_CALENDAR lacks 2008-01-22 entirely, so
                      "latest calendar event <= effective" would misdate that
                      intermeeting cut by six weeks. All three are live regression
                      checks, not prose.
                      INTERMEETING 4, each POSITIVELY corroborated by a Federal
                      Reserve Conference Call or "(unscheduled)" label:
                      2008-01-22 (call 01-21), 2008-10-08 (call 10-07),
                      2020-03-03 ("March 2 (unscheduled) Meeting - Statement
                      Released March 3"), 2020-03-15 ("(unscheduled) Meeting").
                      TIMES 31 VERIFIED, 11 NOT_ESTABLISHED - the Fed's archived
                      pages say only "For immediate release". NO time was
                      invented. Sealed fallback (previous target) applies.
POLICY SCHEDULE CHECKS = **33/33 PASS** (mmv_policy_schedule_validate.py).
                      TARGET_SERIES_MATCH = YES, TARGET_RANGE_SPLICE_MATCH = YES,
                      NEAREST_MEETING_HEURISTIC_USED = NO,
                      ALFRED_REALTIME_START_USED = NO, FIXED_LAG_USED = NO.
                      The Fed open-market table reproduces the SAME ORDERED LEVEL
                      SEQUENCE as the frozen regimes - a date-free confirmation.
                      Zero revisions across every vintage of all three policy
                      series, confirming the sealed unrevisedness premise.
POLICY DISCREPANCY RECORDED = FRED and the Fed disagree by ONE DAY on the
                      effective date of exactly two regimes: FRED stamps
                      2015-12-16 / 2016-12-14 (announcement day), the Fed stamps
                      2015-12-17 / 2016-12-15 (stated effective day). VALUES are
                      identical and the announcement dates are independently
                      established from the statements, which is what the sealed
                      rule reads. NOT material; recorded, not repaired.
LAGGED-CUTOFF FINDING = The S1 six-collision list intersected FOMC dates with
                      DECISION dates only. The policy leg also reads a cutoff 12
                      months earlier, and TWO lagged cutoffs are themselves
                      target-change announcement dates: 2007-10-31 (lagged for the
                      2008-10-31 decision) and 2008-04-30 (lagged for 2009-04-30),
                      both NOT_ESTABLISHED -> PREVIOUS target by the sealed
                      fallback. Of the six pinned collisions only 2019-07-31 is
                      also a target CHANGE (2:00 p.m. EDT, eligible); the other
                      five are no-change meetings. SAME sealed rule at the cutoff
                      it was always defined on - no new rule, no new choice.
                      Recorded because a lagged cutoff resolving silently is
                      exactly what should not resolve silently.
S3_PREREQUISITE     = CLOSED 2026-09-17 by the policy schedule freeze above.
                      Originally: ONE construction question was deferred rather
                      than decided: how each administered target change maps to the
                      announcement that made it public. The contract fully determines
                      eligibility GIVEN a schedule (section C.2; the six collisions
                      are pinned), but does not specify effective-date -> announcing-
                      meeting attribution, which matters for INTERMEETING changes
                      where a naive "latest FOMC date <= effective date" rule could
                      attribute a change to a meeting weeks earlier and admit it too
                      soon. PolicySchedule is therefore generic over an explicit
                      announcement sequence and S2 tests it that way. This is NOT a
                      change to any sealed definition and NOT a scientific choice
                      about the signal; it is recorded now because deciding it later,
                      with the schedule half-built, is how a look-ahead gets
                      rationalised.
GATE 0.5            = **RUN ONCE, PASS, 2026-09-17**. RUN_ID
                      MMV-GATE05-20260917-01 under MMV-AUTH-0001, scope
                      ONE_SHOT_SINGLE_PNL_FREE_GATE05_RUN, now CONSUMED
                      permanently. RNG_SEED = NONE (deterministic exact integer
                      counting; no resampling exists to seed).
                      POOLED_EXACT_SIGN_AGREEMENT = 1313 / 3270 = 40.152905%,
                      compared as Fraction(1313,3270) against Fraction(4,5), NOT
                      from a rounded percentage. Sealed threshold >= 80.0%
                      INCLUSIVE -> NO KILL.
                      Record research/extensions/mmv/MMV_GATE05_RESULT.md;
                      machine artifact research/extensions/mmv/gate05/
                      MMV_GATE05_RESULT.json.
GATE 0.5 STRUCTURAL = 218 decision months 2008-05-31..2026-06-30; 15 mapped
                      instruments; 3270 instrument-months, no duplicates; VNQ and
                      RWX ABSENT (never constructed, so excluded_unmapped = 0 is
                      not an empty filter); all three legs defined at all 218
                      dates; 0 undefined MMV cells; 0 undefined canonical cells;
                      718 zero (flat) MMV cells counted on both sides.
                      PIT observed: newest-reference lag is 1 month in 216-217 of
                      218 cases per series, with a few genuine 2-3 month
                      publication gaps. The sealed same-day vintage rule BIT ONCE
                      (one INDPRO vintage fell on a decision date; no
                      authoritative release clock time exists, so the prior
                      vintage was used).
                      The known CPILFENS hole at 2025-10-01 never fell on a lag
                      the transform reads, because the leg takes the newest
                      VALUED reference month rather than a fixed calendar slot.
GATE 0.5 MEANING    = MMV raw position states are NOT a restatement of the
                      canonical TSMOM control, so the lineage is not spending a
                      return trial on a sleeve that merely re-expresses the core
                      book in macro vocabulary. It does NOT mean alpha,
                      diversification, predictive power or positive return
                      exists, and it does NOT support the macro mechanism. A
                      PnL-free direction screen cannot distinguish a separable
                      strategy from a worthless one.
SIX-COLLISION ACCT  = A=1 (2019-07-31, 2:00 p.m. EDT <= 15:45, new target
                      eligible), B=0, C=5. A+B+C=6. The two collisions whose Fed
                      pages say only "For immediate release" (2013-07-31,
                      2014-04-30) are class C no-change meetings: no new target
                      value existed for the unestablished time to gate, so the
                      conservative fallback was available and simply not needed.
PRIMARY TRIAL       = **NOT SPENT**. Contract section M sets the primary trial
                      family to the MMV composite, m=1, and that trial is the
                      GATE-1 RETURN TEST, which remains unspent and
                      unauthorized. Gate 0.5 is the sealed PnL-FREE pre-PnL
                      falsification and touched no return.
                      No row was written to ops/EXPOSURE_LEDGER.md or
                      research/extensions/TRIAL_LEDGER.md under this grant;
                      whether a PnL-free position-agreement reveal warrants a
                      ledger row is a CONTROLLER question, not a builder
                      decision, and the brief did not direct one.
DIAGNOSTICS         = per-instrument, per-leg and calendar-period agreement were
                      NOT COMPUTED AT ALL - not computed and withheld. No
                      best/worst instrument ranking, per-leg breakdown or
                      calendar map of unusual agreement exists for anyone to
                      build a later narrative on.
POST-RUN VALIDATORS = S2 parser 32/32 PASS, policy schedule 33/33 PASS, S2
                      synthetic 150/151 with ONE expected flag:
                      t_no_mmv_output_artifact_exists now detects the AUTHORIZED
                      result artifact. That is a PRE-RUN assertion behaving
                      correctly after an authorized run - the same stage-bound
                      situation the controller already ruled on for the S1
                      D-checks. The test was NOT modified.
POST-GATE05 AUDIT   = **PASS 15/15, STATIC ONLY** (research/extensions/mmv/
                      mmv_gate05_audit.py; record MMV_GATE05_AUDIT.md). No rerun,
                      no recomputation of the agreement statistic, no returns, no
                      new authorization. MMV-AUTH-0001 remains CONSUMED.
REPRESENTATION      = **VALID**. CANONICAL_COMPOSITE_SIGN_NORMALIZED_BEFORE_
                      GATE05 = YES. The committed reader canonical_signs()
                      (mmv_gate05_run.py:336) parses each cell as an exact
                      Fraction at :349 and applies the inline three-valued sign
                      (v > 0) - (v < 0) at **:350**, one line later and 170 lines
                      before the value reaches the gate. That reader is the ONLY
                      reader of the panel's instrument columns and its output is
                      the ONLY thing handed to gate05.evaluate (:520 -> :432).
                      Exact equality at engine/gate05.py:110.
                      SYNTHETIC_NORMALIZATION_TEST = PASS: the committed
                      expression maps [-1,-0.75,-0.5,-0.25,0,0.25,0.5,0.75,1] to
                      exactly [-1,-1,-1,-1,0,1,1,1,1].
                      IMPOSSIBILITY ARGUMENT (decisive, recomputes nothing):
                      engine/gate05.py:102 passes every canonical value through
                      _check_sign, which RAISES on anything outside {-1,0,+1}.
                      **1167 fractional composite cells** lie inside the audited
                      window over the 15 mapped instruments, so a run comparing
                      raw composites would have raised on the first one and no
                      artifact could exist. A completed run reporting 3270
                      eligible cells is possible ONLY with normalization applied.
                      REPORTED_RESULT_STATUS = VALID_PENDING_CONTROLLER_ACCEPTANCE.
COLLISION RECONCILE = **COMPATIBLE**. The two counts measure DIFFERENT
                      POPULATIONS, not different denominators of one population.
                      The policy freeze's "1 verified / 2 unknown" counted CUTOFFS
                      (decision OR lagged) coinciding with a target-CHANGE
                      announcement: {2007-10-31 L unknown, 2008-04-30 L unknown,
                      2019-07-31 D verified}. The Gate 0.5 "A=1 / B=0 / C=5"
                      classified the SIX PINNED S1 collisions - canonical
                      month-end DECISION dates that are FOMC announcement dates,
                      change or no change. The sets intersect in exactly ONE
                      member, 2019-07-31, VERIFIED in both.
                      B=0 is not a contradiction of "2 unknown": among the six,
                      NO target changed with an unestablished time. Three of the
                      five class-C meetings (2018-01-31, 2024-01-31, 2024-07-31)
                      publish a 2:00 p.m. time and changed nothing; two
                      (2013-07-31, 2014-04-30) publish no time and also changed
                      nothing. A meeting that changes nothing gives the same-day
                      rule no new value to admit or withhold.
LAGGED CUTOFF STATUS = 2007-10-31 and 2008-04-30 are SEPARATE LAGGED-CUTOFF
                      EVENTS, NOT among the six. Structurally they cannot be:
                      both fall BEFORE the decision window opens on 2008-05-31,
                      so neither is a decision date. Each is a target-change
                      announcement with time NOT_ESTABLISHED -> PRIOR TARGET, and
                      each enters the study only as the t-12m cutoff of a later
                      decision (2008-10-31 and 2009-04-30 respectively).
GUARD AUDIT         = RERUN_CURRENTLY_BLOCKED = YES, verified statically without
                      executing the driver. consumed_ids() unions committed
                      records with the WORKING TREE (mmv_authorization.py:103)
                      while grants come only from committed state; _scoped
                      retains a LIFECYCLE record carrying no lineage field (the
                      defect that previously dropped consumption and made the
                      guard fail OPEN) while still rejecting a record declaring a
                      DIFFERENT lineage; and the driver independently refuses when
                      a result artifact exists (mmv_gate05_run.py:509).
EXPOSURE            = **ops/EXPOSURE_LEDGER.md row 56**, classification
                      REVEALED_AGGREGATE / granularity AGGREGATE, note
                      class=PNL_FREE_STRUCTURAL_EXPOSURE (controller's term,
                      recorded as directed; NOT a member of the Program v2 S0B
                      triple). PNL_FREE_EXPOSURE_STATUS = VALID_GATE05_EXPOSURE.
                      REVEALED_TARGET_METRIC would have been WRONG - no return,
                      cost, Sharpe or drawdown exists. RETURN_TRIAL_SPENT = NO;
                      nothing written to TRIAL_LEDGER and no trial invented.
S3 RUN              = **COMPLETE 2026-09-17**. The controller accepted the Gate 0.5
                      PASS and authorized MMV-AUTH-0002, the FIRST and ONLY primary
                      historical return trial. It ran ONCE under run_id
                      MMV-S3-20260917-01 (driver research/extensions/mmv/
                      mmv_s3_run.py, commit 93d9a47; grant commit a6748e7) and is
                      now CONSUMED. RERUN_PERFORMED = NO.
RETURN ALIGNMENT    = **RECOVERED, NEVER INVENTED**. The sealed authority uniquely
                      determines the return interval and the driver re-derives it
                      from committed canonical code at run time, refusing to
                      continue if the exact fragments are gone: month-end close ->
                      month-end close (src/signals.py::to_monthly +
                      src/performance.py::monthly_asset_returns), position held
                      during month M = portfolio weight decided at month-end M-1
                      (src/portfolio.py shift(1)), 2 bps one-way x turnover charged
                      in the month the trade executes and subtracted ONCE.
                      HIGH_DIFFICULTY_OWNER_DECISION_REQUIRED = NO.
                      FABLE_OWNER_ADVICE_REQUIRED = NO.
SAMPLE              = **213 eligible return months, 2008-09-30 .. 2026-05-31**, 15
                      mapped instruments, VNQ/RWX absent. 218 canonical decision
                      dates minus the ineligible partial terminal return month
                      2026-06-30 (MMV-OD-8) and a 4-month wrapper warm-up
                      (2008-05-31..2008-08-31):
                      the canonical portfolio-vol estimate needs 60 daily returns of
                      the MMV book itself before any leverage exists, so those months
                      carry no position. STRUCTURAL, not chosen; nothing later is
                      excluded. The 218-date DECISION grid is NOT altered:
                      2026-06-30 remains a valid decision-state date and only its
                      RETURN observation is ineligible. 0 missing returns, 0
                      duplicate months, 0 partial books.
CAUSALITY           = TESTED, not asserted. The whole wrapper (asset vol, asset
                      weights, portfolio vol, leverage, portfolio weights) was
                      recomputed on price panels truncated at 2011-06-30, 2015-12-31,
                      2019-09-30 and 2023-03-31 and is **BITWISE identical** up to
                      each truncation date. held(M) == port_weight(M-1) exactly on
                      all 218 months.
FIRST RESULT (VOID) = **INVALID_PRIMARY_SAMPLE / NONDECISIONAL**, superseded
                      2026-09-17. The run MMV-S3-20260917-01 included ONE partial
                      terminal return observation - the row labelled 2026-06-30,
                      whose data end 2026-06-12. Its Gate-1, M1, M2 and terminal
                      class are NO LONGER PROGRAMME EVIDENCE and are not restated
                      here; the artifacts are preserved immutably for provenance
                      at MMV_S3_RESULT.md / s3/MMV_S3_RESULT.json, unedited.
MMV-OD-8            = **B_EXCLUDE** (controller, 2026-09-17).
                      LOCKBOX_AUTHORITY_VERIFIED = YES; NEW_SCIENTIFIC_CHOICE = NO.
                      research/extensions/LOCKBOX_PROCEDURE.md section 2.1 was
                      written 2026-09-08, NINE DAYS BEFORE the seal. It verifies
                      the panel boundary at 2026-06-12, calls the June 2026 row
                      "a complete label over an incomplete period", and requires
                      an evaluation EITHER to (a) truncate the terminal row and
                      state so OR (b) declare the inclusion in its
                      preregistration. The sealed contract records the boundary
                      in section P and never exercises (b), so (a) BINDS. The
                      first run included the row and merely stated that it had,
                      which is neither path. Section 2.1 also calls this "the
                      first item every new candidate's A2 challenge should
                      check" - it was a documented trap and the first run walked
                      into it.
CORRECTION RUN      = **MMV-S3-REPAIR-20260917-01**, one bounded repair of the
                      SAME primary trial under MMV-AUTH-0003 (grant commit
                      1734dcb, driver research/extensions/mmv/mmv_s3_repair_run.py
                      commit cd41614), now CONSUMED. TRIAL_COUNT_INCREMENT = 0,
                      F-MMV stays at m = 1, NOT a new trial and NOT independent
                      evidence. Seed, B, execution convention, wrapper, cost and
                      bootstrap implementation ALL UNCHANGED.
ONE ROW, PROVEN     = removed exactly {2026-06-30}, added none, 214 -> 213, every
                      earlier month identical and in order. The guard is
                      STRUCTURAL, not a hard-coded date: a month is eligible only
                      if the price panel continues PAST it, which is what
                      establishes that the last observed price inside it is its
                      final trading close; a panel that stops inside a month
                      fails closed. Three mechanical checks: 14 files verified
                      BYTE-IDENTICAL to the parent-run commit (parent driver,
                      canonical src/, config.py, all seven sealed engine/ modules,
                      the Gate-0.5 driver); 9 scientific functions reused by
                      OBJECT IDENTITY from the parent module; and the repair
                      module's own definitions derived from its AST and required
                      to match a declared classification table exactly - which
                      tripped on itself when written, as a real check should.
                      OUTCOME_AFFECTING_DIFFS = TERMINAL_ROW_ONLY.
IDENTITY            = SIGNAL_IDENTITY_VERIFIED = YES, POSITION_IDENTITY_VERIFIED
                      = YES, proven by REPRODUCTION: before computing anything
                      repaired, the run recomputed the first run's 214-month
                      statistics from its own freshly built book and reproduced
                      every published figure BIT-FOR-BIT. Had the macro feature,
                      the decision grid, the positions, the wrapper, the cost
                      model or the bootstrap drifted at all, they could not have.
PRIMARY RESULT      = **DECISIONAL. GATE 1 FAIL / M1 FAIL / M2 FAIL** on the
                      corrected **213-month** sample, one calendar-year block
                      bootstrap, 19 blocks (2008:4 .. 2026:5), B = 10,000, ONE
                      common draw set, seed **1963028087 UNCHANGED**.
                        GATE 1  gross mean  +0.00014275  95% [-0.00428624, +0.00420283]
                        M1      net mean    +0.00000230  95% [-0.00443109, +0.00406748]
                        M2      net Sharpe  +0.00029     95% [-0.531249, +0.545330]
                      Aggregate turnover 149.5821, aggregate cost 0.029916 at the
                      sealed 2 bps. gross mean - cost mean = net mean exactly.
BOOTSTRAP BOUNDARY  = UNAMBIGUOUS. A calendar year is ONE block whatever its month
                      count; the 2026 block simply drops from 6 months to 5. Same
                      rule that already produced a 4-month 2008 block, same rule
                      implemented in benb_inference.py::year_block_bootstrap, and
                      section J's "resample COMPLETE calendar years" names the
                      resampling UNIT - a whole year rather than the monthly IID
                      draw section J forbids - not a filter on which years
                      qualify. The draw matrix is identical to the first run's.
                      Reconciled against src/performance.py: gross BIT-IDENTICAL,
                      turnover and net within one ULP (bound 1e-12, which is a
                      floating-point identity check and NOT a research threshold).
TERMINAL CLASS      = **D - PREDICTIVE RESPONSE UNRESOLVED**, classified FROM
                      SCRATCH on the corrected sample; the void run's class was
                      NOT carried forward. It is the same letter the void run
                      reported and that is arithmetic, not inheritance: removing
                      one month of 214 moved every interval endpoint by less than
                      5e-05, far too little to cross a boundary the point estimate
                      misses by two orders of magnitude. PROGRAMME_STATUS =
                      UNRESOLVED / LOW_POWER. FAILURE_TYPE = NONE. TERMINAL under
                      section K: no retuning, no rescue, no second look. The Gate-1
                      95% interval SPANS ZERO, so the sealed first-match order stops
                      at D. It is NOT class C - the upper endpoint is positive - and
                      it is NOT a falsification of the mechanism. It says the sealed
                      design, on the sealed sample, cannot resolve the sign of the
                      response. EVIDENCE_CEILING = supported, NEVER confirmed.
LEDGERS             = TRIAL_LEDGER section 6.2 row **F-MMV** appended (the fourth
                      declared family, declared in sealed section M before any member
                      ran, TRANSCRIBED LATE at the run and disclosed as such);
                      MMV_PRIMARY_RETURN_TRIAL_SPENT = YES, m = 1.
                      the status cell was then CORRECTED IN PLACE at the repair
                      (the F-BENB / F-VRP precedent); m UNCHANGED at 1, no m = 2,
                      TRIAL_COUNT_INCREMENT = 0.
                      ops/EXPOSURE_LEDGER.md **row 57** (the void result) is
                      PRESERVED UNEDITED - the ledger is append-only and corrects
                      by citation, never by rewriting - and **row 58** is
                      appended, marking row 57 INVALID_PRIMARY_SAMPLE /
                      NONDECISIONAL and carrying the replacement primary result.
                      Both rows are the SAME trial and are NEVER to be counted as
                      independent evidence. Row 56, the PnL-free Gate 0.5
                      exposure, is NOT counted as a return trial at all. N_trials
                      on the ETF panel stays NOT ASSERTED; D-ETF-COUNT remains
                      UNKNOWN_PENDING_AARON_DECISION.
NOT COMPUTED        = per-ETF return rankings, per-leg PnL, growth/inflation/policy-
                      only PnL, best or worst years or months, recession or crisis
                      cells, drawdown, hit rate, rolling Sharpe, alternative start
                      dates, lookbacks, costs, mappings or series. Not computed and
                      withheld - NOT COMPUTED AT ALL. The first-release concordance
                      diagnostic remains CLOSED. Gate 0.5 was NOT rerun - not at
                      the first run and not at the repair - and neither S3 driver
                      reads ANY canonical TSMOM sign. Gate 0.5 is unaffected by
                      the terminal-row defect because it compares DECISION-DATE
                      position states and never needs the following month to be a
                      complete return observation: 1313/3270 = 40.152905% PASS
                      stands. No search over sample endpoints was performed; the
                      single endpoint evaluated is the one MMV-OD-8 mandates.
NEXT_OWNER_DECISION = CONTROLLER S4 VERDICT on a TERMINAL CLASS D. NO RESCUE,
                      RETUNE OR COMPONENT SELECTION IS AUTHORIZED: series,
                      transforms, coefficients, mappings, thresholds, cost, the
                      +0.30 target, the bootstrap, the sample and the execution
                      timing are all closed. Any further hypothesis requires a NEW
                      LINEAGE with its own preregistration and seal, which is an
                      Owner decision and not a continuation of this one.
                      HIGH_DIFFICULTY_OWNER_DECISION_REQUIRED = NO. No scientific
                      choice remains open. Still UNAUTHORIZED: any historical MMV
                      feature, composite or position; the historical Gate 0.5
                      evaluation; the first-release concordance cell; any return,
                      Sharpe, bootstrap or interval; any RNG seed; any push, PR or
                      merge.
```

## CTA-EDGE-03-PINS — physical inventory news × scarcity — S0 HOLD 2026-09-16

*State only, never workflow authority (vNext §0).*

```
RESEARCH_QUESTION   = Does a FIRST-PUBLISHED unexpected change in U.S. commercial crude
                      oil inventories produce a directionally consistent WTI futures
                      price response that survives a realistic post-release execution
                      delay and realistic release-window costs, and is that response
                      stronger when the pre-release physical inventory state was already
                      scarce?
RESEARCH_ID · LANE  = CTA-EDGE-03-PINS · not yet assigned (S0)
S0 FRAME            = COMPLETE / **HOLD** (2026-09-16).
                      Artifact research/extensions/pins/PINS_S0_FRAME.md
HOLD_REASON         = PINS-OD-1, a high-difficulty Owner decision on the EXPECTATION
                      SOURCE. The three live options are three different hypotheses:
                      (1) survey consensus (Reuters/Bloomberg/Platts) - licensed, not
                      held, and economic-calendar "forecast" columns have undocumented
                      provenance; (2) API Weekly Statistical Bulletin as the expectation,
                      the Ye & Karali construction - academically standard and genuinely
                      point-in-time, but subscription-only via Refinitiv/ICE;
                      (3) a model-based expectation - always available, costs nothing,
                      and is A DIFFERENT HYPOTHESIS requiring a renamed lineage;
                      (4) close at S0 as a DATA/PIT failure, spending no trial.
                      PINS-OD-2 (scarcity definition), PINS-OD-3 (execution latency +
                      primary horizon) and PINS-OD-4 (materiality scale) are RECORDED
                      but DEFERRED behind OD-1, which is a gate.
PINS-OD-1           = DECIDED 2026-09-16 = CONDITIONAL OPTION 1. Anchor on ONE named
                      PRE-API analyst-survey consensus family (C), with the
                      first-reported API pre-release estimate (P) as a MANDATORY second
                      point-in-time input; BOTH must be reconstructible. Option 2 (API
                      alone) not accepted under this claim; option 3 (model expectation)
                      rejected; option 4 (close) correct if feasibility fails.
                      Fable advice ACCEPTED WITH QUALIFIERS PINS-Q1 (the linear update
                      heuristic E* ~ C + k(P-C) is HEURISTIC_ONLY, k UNKNOWN, no
                      price-fitted k), PINS-Q2 (measurement-error DIRECTION is not a
                      programme fact) and PINS-Q3 (binding terminology: P is never
                      "market expectation", A-P is never a "market-expectation
                      surprise"). Record
                      ops/OWNER_DECISION_RECORD_CTA_EDGE_03_PINS.md.
PINS-OD-1 FEASIBILITY = **FAIL** (2026-09-16). Against a 45-release sample frozen from
                      the EIA release calendar BEFORE any retrieval: consensus coverage
                      0/45 for Reuters/LSEG and 0/45 for the one permitted retry
                      (S&P Global Platts), against a >=90% threshold. reuters.com is
                      inaccessible to the agent at the user-agent level; the LSEG Reuters
                      Polls product does not document the weekly petroleum inventory poll
                      as in scope; Platts has no date-addressable public archive.
                      Economic-calendar "forecast" fields were REFUSED BY RULE — no named
                      family, no forecast timestamp, and an explicit prohibition on use
                      and storage. The API leg has a lawful documented route (ICE Data
                      Services, API WSB, history from 2000) but NO ENTITLEMENT IS HELD,
                      so it was NOT TESTED, and whether that series is first-reported or
                      revised is UNVERIFIED.
                      Record research/extensions/pins/PINS_OD1_FEASIBILITY_RESULT.md.
LIFECYCLE_STATUS    = **CLOSED PRE-OUTCOME** / DATA-PIT ACCESS NOT ESTABLISHED.
                      Declared by the programme controller 2026-09-16. No trial was
                      spent, no data was purchased, and no candidate outcome was ever
                      generated.
CLOSURE_RECORD      = research/extensions/pins/PINS_CLOSURE.md
MECHANISM_TESTED    = NO · WTI_RESPONSE_TESTED = NO · SCARCITY_MODERATION_TESTED = NO
REOPEN_ONLY_IF      = new concrete lawful access to the required point-in-time
                      expectation inputs. The frozen 45-release audit sample
                      (sha256 52e70b40...4283a) stands, so a retry would spend no
                      research degrees of freedom.
RECOMMENDED_ACTION  = CLOSE CTA-EDGE-03-PINS AT S0 / DATA-PIT FAILURE (negative outcome
                      class A), SUBJECT TO one Owner fact that is procurement and not
                      science: does Aaron hold, or will he authorise, an entitlement to a
                      named survey family's historical consensus — and does that product
                      actually carry this weekly poll at the required coverage? If NO,
                      close. If YES, re-run THIS SAME pilot against THE SAME frozen
                      sample, which costs nothing in research degrees of freedom because
                      the sample and thresholds are already committed.
S1 DESIGN+SEAL      = NOT STARTED. No seal, no contract, no build, no run
                      authorization, no data purchase.
SETTLED AT S0       = DAILY_DATA_ADEQUATE = NO; INTRADAY_REQUIRED = YES. The mechanism
                      is a jump at 10:30:00 ET whose effect is largely spent inside the
                      first half-hour; a daily close-to-close return cannot answer the
                      harvestability question. This is the CTA-EDGE-01-TA lesson applied
                      directly, and no daily fallback is offered.
                      FIRST_PUBLISHED_EIA_SERIES_RECONSTRUCTIBLE = YES from 2012-01-05:
                      the EIA per-release archive holds 765 releases through 2026-09-10,
                      each with 15 CSV tables (enumerated from link metadata only).
DATA POSITION       = CL intraday NOT held but cheaply obtainable under a live Databento
                      GLBX.MDP3 entitlement (~$14-19 per CME root for 12-15 years of
                      ohlcv-1m, observed). CL daily IS held and is part of KB-2, which is
                      BURNED. No EIA and no consensus data exist anywhere on this machine.
PRICE_SAMPLE_REUSE  = REUSED / BURNED CONTEXT (KB-2, N_trials = 14 frozen). An intraday
                      CL panel is a different FOOTING of the same economic history, not a
                      new sample - the BENB reading, inherited.
EVIDENCE_CEILING    = supported. A new physical (EIA) leg does not launder a reused
                      price leg.
DESIGN EXPOSURE     = ASTRA_DESIGN_EXPOSED = YES (REVIEWER_EXPOSURE_LOG S38).
                      FABLE_DESIGN_EXPOSED = **YES** as of 2026-09-16 (S37), created by
                      ADOPTION of its PINS-OD-1 advice, not by asking for it. Fable MAY
                      still act as a delegated Owner-advice seat for PINS-OD-2/3/4; it
                      MAY NOT be a fresh BLIND CERTIFIER. With both seats exposed, any
                      blind certification of a future PINS result needs a THIRD seat that
                      is none of Fable, Astra or this Main Agent. Supersedes the
                      PINS_S0_FRAME.md §G status by AMENDMENT (PINS_S0_AMENDMENT_01.md),
                      not by rewriting.
OUTCOME EXPOSURE    = NONE. No surprise, scarcity value, interaction, conditional return,
                      regression, event P&L, Sharpe, hit rate or extreme-event list was
                      computed or inspected. No exposure-ledger row was written, which
                      follows the CTA-EDGE-01-TA and CTA-EDGE-02-BENB precedent: an S0
                      frame generates no outcome, and seat rows are written AT SEAL.
NEXT_OWNER_DECISION = NONE for this lineage. It is closed. The backlog successor is
                      audited in research/extensions/CTA_EDGE_04_CANDIDATE_AUDIT.md.
```

## CTA-EDGE-02-BENB — bond ETF–NAV basis — CLOSED 2026-09-16

*State only, never workflow authority (vNext §0).*

```
RESEARCH_QUESTION   = Does an abnormal HYG discount to official issuer NAV converge in
                      the next session's TRADABLE window (open(t+1) -> close(t+1)), by
                      enough to survive costs, and separably from overnight price
                      discovery and NAV catch-down?
RESEARCH_ID · LANE  = CTA-EDGE-02-BENB · FULL
S0 FRAME            = COMPLETE / PASS (2026-09-15), after a S0 DATA-RESOLUTION and
                      DESIGN-REPAIR pass that replaced the dividend-adjusted panel with
                      raw unadjusted prices and located the issuer daily NAV history.
S1 DESIGN+SEAL      = COMPLETE / SEALED. research/extensions/benb/BENB_PREREGISTRATION.md
                      sha256 1b7ca2122ba14c4097e4d76d7a733bf0c77ab9c0d02dd93a38c25bc1be5160cf;
                      seal manifest sha256
                      6aa0d21401b9887f4a44ab6559fa10d7a59ae5a8b512e1ad306543c061483703
                      at seal commit c1a3f8155a9fdb86d55b620c33498f604fcbf8d0.
                      M2 = +0.30 STRICT > fixed by Aaron's Owner decision BENB-OD-1.
S2 BUILD            = COMPLETE / PASS at commit d1ccefc8c6ed6e15e6366856ff0b64a0f6516bc3.
                      65 targeted tests pass; the three mandatory economic worlds behave
                      as mandated; benb_prereg_validate.py 72/72 at that commit.
S3 RUN              = EXECUTED 2026-09-16. ONE governed historical run under the
                      single-use grant BENB-AUTH-0001, run_id BENB-RUN-20260915-01,
                      rng_seed 1788924436 = int("6aa0d214", 16) from the seal-manifest
                      hash, B = 10,000. The authorization is CONSUMED; zero live grants
                      remain and a further real run is refused.
S4 VERDICT          = COMPLETE / ACCEPTED 2026-09-16 (programme controller).
LIFECYCLE_STATUS    = CLOSED
CLOSURE_RECORD      = research/extensions/benb/BENB_CLOSURE.md
FINAL_CLASS         = A-M — MIXED NON-HARVESTABLE CONVERGENCE
PROGRAMME_STATUS    = NOT_PROMOTED   (KB research_status = not_promoted)
FAILURE_TYPE        = GATE_1_NOT_SUPPORTED
CLOSURE_REASON      = The sealed Gate-1 coefficient on the only lawfully reachable leg,
                      beta_T over open(t+1) -> close(t+1), has 95 % interval
                      [-14.53, 1432.72] and does not clear the STRICT > 0 bar, while BOTH
                      diagnostics fire: beta_O [555.23, 2014.54] supported positive and
                      beta_N [-2783.12, -1898.88] supported negative. Under the sealed
                      §J.3 first-match-wins order that is STEP 1, class A-M. Gate 2
                      (mean NET -11.19 bps, calendarised Sharpe -3.057) and LOYO (passes)
                      were computed and recorded but NOT consulted: both sit after
                      Gate 1 in the order.
HISTORICAL_OUTCOME_EXPOSED = YES
PRIMARY_CLAIM_SUPPORTED = NO · TRADABLE_CONVERGENCE_SUPPORTED = NO
OVERNIGHT_PRICE_DISCOVERY_SUPPORTED = YES · NAV_CATCH_DOWN_SUPPORTED = YES
MECHANISM_FALSIFIED = NO   · PORTFOLIO_TEST_AUTHORIZED = NO
RETUNE_AUTHORIZED   = NO   · SECOND_RUN_AUTHORIZED     = NO
EVIDENCE_CEILING    = supported. The HYG/LQD price leg is REUSED / BURNED context
                      (KB-1, 6 of 6); the NAV leg is new; combined provenance is
                      MIXED / DEPENDENT. A new NAV leg does not launder a reused sample.
TRIAL ACCOUNTING    = F-BENB / BENB-PRIMARY spent, m = 1. N_trials on the ETF panel
                      remains NOT ASSERTED; D-ETF-COUNT untouched.
FEATURE-DESIGN NOTE = the sealed expanding median produced a highly persistent
                      discount-side state, 3,555 / 4,415 = 80.52 %. Recorded as a
                      design lesson ONLY. It authorizes no threshold, z-score,
                      top-decile selection, longer holding, overnight capture, LQD
                      promotion or premium-side short inside this lineage; each is a
                      NEW lineage.
NEXT_OWNER_DECISION = NONE for this lineage. It is closed.
```

## CTA-EDGE-01-TA — Treasury auction / refunding-week ETF effect — CLOSED PRE-OUTCOME 2026-09-15

*State only, never workflow authority (vNext §0).*

```
RESEARCH_QUESTION   = Does the predeclared US Treasury coupon-auction cycle produce an
                      economically harvestable, repeatable round-trip return pattern in a
                      liquid duration ETF (TLT), measured close-to-close, surviving costs
                      and not carried by a single year?
RESEARCH_ID · LANE  = CTA-EDGE-01-TA · FULL
S0 FRAME            = COMPLETE / PASS (2026-09-15)
S1 DESIGN+SEAL      = COMPLETE / SEALED. Sealed contract
                      research/extensions/ta/TA_PREREGISTRATION.md sha256
                      3b495fcb220a86b9c4226e308e4814bdfdd871d1c69ce352e99b78977436d35b
                      at seal commit 881e684b4ddca73f117ea78af14843dabf3c59c9.
S2 BUILD            = COMPLETE / PASS at commit 3bc779a67247110625378b8558cad3dfcf698ed6.
                      48 targeted tests pass; ta_prereg_validate.py 122/122 PASS.
S3 RUN              = NOT AUTHORIZED. No execution authorization for this lineage ever
                      existed and none was created.
LIFECYCLE_STATUS    = CLOSED PRE-OUTCOME
CLOSURE_RECORD      = research/extensions/ta/TA_CLOSURE.md
FAILURE_TYPE        = IDENTIFICATION_DESIGN_INSUFFICIENT
CLOSURE_REASON      = The sealed §G.3 macro/QRA identification diagnostic is mechanically
                      NOT_EVALUABLE on the sealed event calendar: design-matrix rank 5 of
                      5 (not deficient) but REFERENCE_GROUP_N = 7 against the sealed
                      minimum of 20. Under the sealed rule NOT_EVALUABLE triggers the
                      damage diagnostic, and under §I.2 a triggered damage diagnostic
                      converts a would-be Class D into Class I. Class D was therefore
                      STRUCTURALLY UNREACHABLE before any historical ETF outcome was
                      opened, and the controller closed the lineage rather than spend a
                      governed run on it.
HISTORICAL_OUTCOME_EXPOSED = NO
MECHANISM_FALSIFIED = NO   · ETF_EDGE_FALSIFIED = NO · TARGET_MARGIN_EXCLUDED = NO
VERDICT             = NONE. Classes A/B/C/D/I are the sealed verdict vocabulary and none
                      applies: the study did not run. This is NOT falsification, NOT
                      target-margin exclusion, NOT low power from a result, and NOT
                      evidence against the Treasury auction mechanism — which the intraday
                      literature identifies with a causal design.
RESEARCH_LESSON     = At daily ETF frequency the mid-month refunding-week object is too
                      structurally entangled with the sealed macro/QRA calendar to support
                      the programme's positive identification standard. CPI falls after the
                      auction in 125 of 213 windows and payrolls precede it in 178 of 213;
                      only 7 windows are free of all four covariates.
TRIALS              = NONE SPENT. F-TA was declared before any member ran and no member
                      ever ran. D-ETF-COUNT untouched.
SAMPLE              = No burn added to the ETF panel: no event return, AC, mean, interval,
                      Sharpe or bootstrap statistic was computed on it by this lineage.
                      The Treasury auction record and the macro release calendars are
                      metadata, not outcome samples, and create no burn.
DESIGN_EXPOSURE     = Fable and Astra remain material_design_contributor and remain barred
                      from blind certification (REVIEWER_EXPOSURE_LOG rows S31, S32).
REOPENING           = NOT AVAILABLE to any agent. Sealed §K.8 stands. A design capable of
                      the identification this one lacked is a NEW lineage with its own S0.
NEXT_OWNER_DECISION = NONE for this lineage. It is closed.
```

Nothing in this block alters canonical TSMOM's status, C-A's status, C-D's HOLD, or any
closed lineage.

---

## TSMOM-VRP-01 — short-VIX-futures sleeve — CLOSED 2026-09-14 — UNRESOLVED (Class 3)

*State only, never workflow authority (vNext §0).*

```
RESEARCH_QUESTION   = Does a standalone, unconditional, constant-maturity SHORT position in
                      listed monthly VIX futures, held at a frozen stress-budgeted size,
                      deliver useful compensation after real holdings, rolling, variation
                      margin, costs and collateral (Stage A) -- and, only if it does, is it
                      compatible with the canonical TSMOM programme in systemic-tail months
                      (Stage B)?
RESEARCH_ID · LANE  = TSMOM-VRP-01 · FULL
S0 FRAME            = COMPLETE (Fable Phase-C map + final adjudication; independent Astra
                      Phase-C map and accepted S0 challenge; Aaron's Owner decisions, with
                      VRP-OD-2...VRP-OD-9 delegated to Fable by Aaron).
S1 DESIGN+SEAL      = COMPLETE. SEALED 2026-09-14T08:04:09Z on the canonical base.
                      Authoritative seal commit 16d84545ba1385a482dbac7e776b31275f6fa5f7
                      (branch vrp/s1-seal-clean, parent main d232d336).
                      Sealed contract research/extensions/vrp/VRP_PREREGISTRATION.md
                      sha256 dd5822440bedbe58f49940651bddf656f4dbb593295b59c4eff2b45b89cf53e6.
                      The earlier attempt d19264af85f45c17f655493e02f71a653bfbdd86 is
                      NON-AUTHORITATIVE (wrong lineage base) and is preserved as provenance.
S2 BUILD            = IMPLEMENTATION COMPLETE, PENDING FINAL CHATGPT S2 ACCEPTANCE.
                      Build commit 72499019ce9ef97f16d1ddf3b3982697a4e6c4cc, governance
                      closure appended on branch vrp/s2-build. S2A data gate 32/32 PASS;
                      21/21 implementation-acceptance items PASS; 100 VRP tests, 101
                      repository tests, all pass.
S2 ACCEPTANCE       = COMPLETE. ChatGPT final S2 acceptance; S2_STATUS = ACCEPTED / CLOSED.
S3 RUN              = EXECUTED 2026-09-14. ONE governed historical Stage-A run under the
                      single-use grant VRP-AUTH-0001, run_id VRP-STAGE-A-RUN-0001,
                      RUN_COUNT = 1. Generated GENERATED_NOT_SEEN into the VRP protected
                      store, post-compute integrity gate PASS 19/19, then exactly ONE
                      authorised reveal under the separate grant VRP-AUTH-0002.
                      REVEAL_COUNT = 1. Both grants are consumed.
STAGE_A_RESULT      = window 2006-09..2026-08, 240 months.
                      ANNUALISED_MEAN_NET_EXCESS_RETURN_ON_K = +0.073224
                      CI_95 = [+0.003906, +0.136081]
                      against +E = +0.075 and -F = -0.075.
                      STAGE_A_STATE = UNRESOLVED
                      FAILURE_CLASS = 3 INSUFFICIENT_EVIDENCE / LOW_POWER
                      RESEARCH_STATUS = unresolved
                      Endpoints classify; the point estimate never does. L <= +E <= U.
                      The interval spans roughly +0.4 % to +13.6 % annualised on
                      committed capital: consistent both with compensation well above
                      the required margin and with compensation far below it.
STOP_RULE_IN_FORCE  = Sealed section O: a Class-3 Stage A STOPS the historical study and
                      STAGE B NEVER RUNS on this result. The only sealed continuation is
                      VRP-A-PROSPECTIVE (section P), an Owner decision, NOT started.
                      No result may authorise changing J, b, theta, E, F, s, beta,
                      delta_tail, the maturity, the roll, the cost convention, the sample
                      endpoints or the tail rule, or adding a filter. Each is a NEW
                      lineage with its own trial accounting.
CURRENT_VNEXT_STAGE = S3 complete; next gate is ChatGPT Stage-A evidence acceptance.
DATA_GRANT          = VIX chain acquired under Aaron's PHASE D authorisation. 274 raw Cboe
                      official contract files + 7 primary specification documents, SHA-256
                      pinned in research/extensions/vrp/VRP_DATA_MANIFEST.md; raw bytes
                      git-ignored under data/vix/ and NOT committed (Cboe research use, no
                      redistribution). Dataset row: SAMPLE_REUSE.md KB-6.
SAMPLE              = dataset.cboe.vix-futures-monthly-chain (identifier provisional until
                      KB registration -- a separate Owner decision, not taken).
                      268 monthly contracts, 2004-03-26 -> 2026-09-11.
                      Stage-A window 2006-09 -> 2026-08 = 240 months, first month fixed
                      MECHANICALLY by the sealed section F.6 rule, never by an outcome.
DATA_CONTEXT        = DESIGN_INFORMED_FIRST_LOCAL_USE. Never "fresh", never "independent".
OUTCOME_EXPOSURE    = TARGET_METRIC on the VIX chain, as of 2026-09-14. The governed
                      Stage-A series and its interval were generated, protected, and
                      revealed ONCE (EXPOSURE_LEDGER rows 50-51; reviewer seat S30).
                      The Main Agent seat is no longer outcome-blind for VRP Stage A and
                      may not certify the evidence it generated.
                      Stage B: NOT computed. No book return, no D, no tail statistic, no
                      core-VRP combination, no crisis compatibility, no book exhaustion.
                      Stage-B descriptives R6-R11 neither computed nor revealed.
TRIALS              = STAGE_A_TRIAL_SPENT = YES · STAGE_B_TRIAL_SPENT = NO.
                      N_trials on the VIX chain = 1 (was 0; TRIAL_LEDGER.md section 3.3).
                      The trial is spent on CONSTRUCTION, whatever the state.
                      HYPOTHESIS_FAMILY F-VRP declared before any member ran
                      (TRIAL_LEDGER.md section 6.2) -- the programme's first declared family.
MECHANICAL_ERRATUM  = TSMOM-VRP-01-ERRATUM-01, the variation-margin sign notation, at
                      research/extensions/vrp/VRP_S1_MECHANICAL_ERRATUM_01.md. Freezes the
                      SIGNED convention forced by the sealed object (section A "short
                      position"; section D.2 Loss_J = +b*K). SCIENTIFIC_DESIGN_CHANGED = NO,
                      OWNER_VALUE_CHANGED = NO, OUTCOME_USED_TO_RESOLVE = NO. The sealed
                      text is NOT amended and is byte-identical to the seal.
SEAL_VALIDATOR      = The hash-pinned S1 validator vrp_prereg_validate.py is unmodified and
                      still exits 1: 113 contract/content checks PASS and exactly one
                      SEAL-TIME STATE assertion ("no data/vix directory exists yet") now
                      fails, because authorised S2 acquisition made it false -- section L
                      itself mandates data/vix/raw/. That exit code is reported as-is and is
                      never relabelled PASS. The state transition is checked instead by
                      research/extensions/vrp/s2/vrp_post_s2_validate.py (47/47 PASS).
C_A_INTERACTION     = NONE. Static audit over 21 package files: no C-A import, path, key or
                      store; no canonical quantity computed anywhere; Stage B refuses any
                      core day after the C-A forward boundary 2026-09-11 or after the sealed
                      Stage-B boundary 2026-05-31.
PROSPECTIVE         = DECLINED BY OWNER 2026-09-14. Aaron explicitly decided NOT to
                      activate the long-horizon experiment.
                      VRP_A_PROSPECTIVE_STATUS = NOT_ACTIVATED_BY_OWNER_DECISION
                      LONG_HORIZON_PROSPECTIVE_EXPERIMENT = CLOSED_WITHOUT_ACTIVATION
                      ENTRY_2026_09_30 = NOT_ARMED · MONTHLY_ACCRUAL = DISABLED
                      SCHEDULER = NONE · BACKGROUND_RUNNER = NONE
                      TERMINAL_120_MONTH_CLOCK = NOT_STARTED
                      VRP_B_PROSPECTIVE = NOT_ACTIVATED
                      No trial is spent by declining activation. Nothing had to be
                      dismantled: no scheduler, daemon, cron, runner or prospective
                      store was ever created. The S1 seal is NOT rewritten to remove
                      its prospective clauses; the decision is recorded alongside it in
                      research/extensions/vrp/VRP_HISTORICAL_CLOSURE.md.
LIFECYCLE_STATUS    = CLOSED. HISTORICAL_RESEARCH_COMPLETE = YES.
                      MORE_HISTORICAL_TUNING = FORBIDDEN_INSIDE_TSMOM-VRP-01.
                      Both ONE_SHOT grants VRP-AUTH-0001 and VRP-AUTH-0002 are CONSUMED.
DIAGNOSTIC          = VRP-PORTFOLIO-DIAGNOSTIC-01, a SEPARATE exploratory lineage
                      (EXPLORATORY_ONLY, PROMOTION_POWER = NONE) = COMPLETE.
                      VRP-DIAG-DEFECT-001 REPAIRED: sleeve position state now persists
                      across calendar months and the month-start sensitivity reset moved
                      to the allocation boundary. 216 of 217 months reconstruct to
                      8.3e-17 against the sealed series; the entry month 2008-05 differs
                      by construction (the book starts flat) and is disclosed, not removed.
                      Item 13 revalidated with a cross-month fixture that provably catches
                      the old bug (PREVIOUS_ITEM_13 = PASS_BUT_FIXTURE_INSUFFICIENT).
                      RESULT over 2008-05..2026-05, 217 months, fixed 80/20:
                        CORE  Sharpe 0.751, vol 0.1031, maxDD -0.1560
                        VRP   Sharpe 0.483, vol 0.1657, maxDD -0.4382 (excess of cash)
                        COMB  Sharpe 0.908, vol 0.0856, maxDD -0.0957
                        correlation -0.105, DELTA_SHARPE +0.1573, CI [-0.0052, +0.3113]
                        SPY bottom decile: CORE +0.0086 -> COMBINED -0.0093, D_diag -0.0178
                        all six declared crisis windows worse combined than core-only
                      PRACTICAL_CLASSIFICATION = NOT_COMPELLING. The Sharpe gain is not
                      robust (CI includes zero) and the tail trade-off runs against the
                      core's purpose. It does not and cannot change the verdict below.
NEXT_OWNER_DECISION = ChatGPT final diagnostic acceptance, then move to the next Phase-C
                      candidate. FABLE_FOLLOWUP_RECOMMENDED = NO.
REAL_RUN_AUTHORIZED = NO   (VRP-AUTH-0001 is CONSUMED; a further run needs a new grant)
STAGE_B_AUTHORIZED  = NO
```

Nothing in this block alters canonical TSMOM's status, C-A's status, or C-D's closure.

---

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
C-A PIPELINE        = **LIVE** since 2026-09-13T18:33:11Z under Aaron's OD-9
                      C_A_GO_LIVE_AUTHORIZATION (CA-GOLIVE-0001, consumed).
                      PROSPECTIVE_START = 2026-09-13 18:33:11+00:00
                      FORWARD_BOUNDARY  = 2026-09-11
                      FIRST_ELIGIBLE_DECISION_MONTH_END = 2026-09-30 (scheduled;
                        confirmed from that month's snapshot)
                      FIRST_ELIGIBLE_SCORED_MONTH = 2026-10
                      N_scored = 0. No prospective position has been generated.
                      S_G = data/prospective/snapshots/S_G_20260913T183249Z.csv
                        sha256 8e2e3de98384c470a3ffef947f3fee2b17893b25c8caacdbc15f371b5a768a35, 1948685 bytes, 17/17 canonical objects,
                        1993-01-29 .. 2026-09-11 (git-ignored; identity pinned here
                        and in research/extensions/ca/prospective/CA_OPERATIONAL_STATE.json).
                      Protected store + key: OUTSIDE the repository, AES-256-GCM,
                        key fingerprint (non-secret) 9c6d2c48dce7fa1a5c22844b5ebcbb1e8954c7fb456a4f9d0eddec4fae2f6d5c, off-repo backup verified.
                      TERMINAL_REVEAL_AUTHORIZED = NO. No target performance computed,
                        no outcome revealed, no position vector human-visible.
S2 BUILD            = COMPLETE (build + synthetic validation only), under Aaron's
                      C_A_S2_BUILD_AUTHORIZATION. Package at
                      research/extensions/ca/prospective/ (11 modules + runbook).
                      Forward engine reproduces src/ EXACTLY on the frozen panel
                      (max abs diff 0.000e+00, identical NaN patterns). 22-class S2
                      suite: 138 assertions, 0 failures, synthetic fixtures only.
                      NOT LIVE: S_G_CREATED = NO, PIPELINE_GO_LIVE does not exist,
                      no prospective position generated, no real post-seal data used,
                      no Sharpe/PnL/return/drawdown/FM-1/crisis outcome computed.
                      GO-LIVE REQUIRES A SEPARATE OWNER AUTHORIZATION.
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
NEXT_OWNER_DECISION = NONE required to accrue. The pipeline runs monthly under the
                      sealed contract. Separately and still outstanding: the C-D
                      implementation authorization (which must go to an independent
                      session) and, only at N_scored = 120, the single terminal
                      reveal authorization. Neither the seal, the S2 build
                      authorization nor OD-9 consumed either of them.
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
C_A_SEAL_REVISION = 7706d61df8b06beccc8f81ccdb1a22fe79680590
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
