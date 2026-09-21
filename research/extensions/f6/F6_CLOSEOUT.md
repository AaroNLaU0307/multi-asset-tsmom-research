# CTA-EDGE-05 / F6 — MACRO_ANNOUNCEMENT_PREMIUM · S4 VERDICT AND CLOSEOUT

```
LINEAGE            = CTA-EDGE-05 / F6 MACRO_ANNOUNCEMENT_PREMIUM
S4                 = COMPLETE
F6_LINEAGE_STATUS  = CLOSED / UNRESOLVED / NOT_PROMOTED
DATE               = 2026-09-22
```

> **This is the terminal record for F6.** The single sealed primary historical
> trial was executed exactly once, the Controller accepted S3, and the verdict
> below is authoritative. No further work on this lineage is authorized.

---

## §1 The authoritative S4 verdict

```
P1   estimate               +0.00035784
     nominal 95% lower      -0.00062591
     nominal 95% upper      +0.00133231
     class                  UNRESOLVED

P2   beta_EVENT             +0.00023075
     nominal 95% lower      -0.00078811
     nominal 95% upper      +0.00123375
     class                  UNRESOLVED

P3   NOT_APPLICABLE_BY_SEAL — because P1 and P2 did not both pass
```

```
TERMINAL SCIENTIFIC CLASS         = UNRESOLVED
PROMOTION STATUS                  = NOT_PROMOTED
MECHANISM_FALSIFIED               = NO
ECONOMIC_EFFECT_RELIABLY_EXCLUDED = NO
LOW_POWER                         = NOT ASSERTED
INDEPENDENT_CONFIRMATION          = NO
SAMPLE_REUSE                      = T0_REUSED_DEPENDENT
EVIDENCE_CEILING                  = SUPPORTED (a ceiling, never achieved here)
```

---

## §2 The interpretation boundary

The permitted interpretation, and the only one:

> The frozen F6 historical study did not establish the declared positive
> scheduled-announcement SPY edge under either required interval gate. Both
> point estimates are positive, but both nominal intervals span zero. Therefore
> the evidence is insufficient for promotion. The study also did **not** reliably
> exclude zero or a positive effect.

```
THIS RESULT MUST NEVER BE CALLED:

  falsified                 evidence of absence        a negative edge
  low power                 a causal failure           independent confirmation
```

Both endpoints matter and both are recorded. The lower endpoint failing to clear
zero is why nothing is promoted; the upper endpoint sitting above zero is why
nothing is excluded. An unresolved result is a *statement about the evidence*,
not a finding about the world.

### §2.1 Why "low power" is not asserted

`LOW_POWER` is not a state in the sealed contract, no observed-power calculation
was performed, and none may be performed now — computing one on an exposed
sample would be post-result research dressed as a caveat. The interval width is
what it is and is reported directly.

---

## §3 P3 was never executed

```
P3_EXECUTED = NO
```

The sealed contract evaluates P3 **only** after P1 and P2 both pass. They did
not. The fifteen leave-one-calendar-year-out refits were therefore never
computed, and the result artifact records `NOT_APPLICABLE_BY_SEAL` rather than a
number. Computing them anyway — "just to look" — would have manufactured an
unsealed quantity on an exposed sample.

---

## §4 No post-result exploration was performed

```
POST_RESULT_RESEARCH_PERFORMED = NO
```

Not computed, not inspected, not generated at any point after the result:

```
FOMC-only results          CPI-only results           NFP-only results
leave-one-family-out       era splits                 post-2015 results
individual years           2026 returns               TLT
F6.b                       alternate controls         alternate benchmark
alternate cost             alternate bootstrap        alternate event window
alternate start date       rescue hypotheses
```

```
NO RESCUE HYPOTHESIS WAS GENERATED FROM THE EXPOSED SAMPLE.
```

---

## §5 Rerun policy

```
THE PRIMARY TRIAL IS CONSUMED.

No rerun. No corrected primary run. No parameter adjustment. No renamed F6
variant on the same exposed historical sample.
```

A future study may proceed only under a **genuinely new governed lineage** or a
**separately sealed prospective objective**. It may not retroactively promote
this F6 result, and this result may not be re-presented as its supporting
evidence.

---

## §6 Execution governance reservation — recorded, not hidden

```
POST_S2_EXECUTION_WRAPPER_ADDED = YES
SCIENTIFIC_COMPUTATION_CHANGED  = NO
S3_RESULT_INVALIDATED           = NO
GOVERNANCE_RESERVATION          = YES
```

After S2 acceptance but **before** target exposure, an S3 orchestration driver
`research/extensions/f6/f6_s3_run.py` was added in commit **`c47fb228`**. The
driver was reported to perform orchestration only — preflight, exposure
sentinel, one call into the accepted pipeline, artifact serialization — and no
scientific estimation. The accepted S2 production pipeline
(`f6_pipeline.run_real` and the modules beneath it, at build commit
`43f0bb31`, build hash `050bb3d7…`) remained the estimator, and the driver
re-verified those module hashes against `F6_S2_BUILD_MANIFEST.json` before
running.

```
This is a RESERVATION, not a defect finding. It is recorded because code was
added to the execution path after the build was accepted, and a future reader
is entitled to know that without having to reconstruct it from commit order.
It is NOT to be rewritten away.
```

### §6.1 The first invocation never launched Python

```
NOT COUNTED AS A HISTORICAL EXECUTION.
```

The first `--execute` invocation targeted a console-log path inside
`research/extensions/f6/s3/`, a directory that did not yet exist, so the shell
exited 1 **before** exec'ing Python. Afterwards there was no `s3` directory, no
sentinel and no result artifact — therefore `write_sentinel()` never ran,
therefore `run_real()` never ran, therefore `load_price_values()` never ran.

```
NO TARGET ACCESS OCCURRED. It was a transport failure in the invocation, not a
failed execution, and it consumed nothing.

PRIMARY_EXECUTION_COUNT = 1
```

---

## §7 2026 remains unexposed

```
2026_F6_OUTCOME_ACCESSED = NO
```

```
2026 HAS NO AUTOMATIC CONFIRMATION ROLE.
2026 HAS NO RESCUE ROLE.
2026 HAS NO PROMOTION POWER FOR THIS CLOSED F6 PRIMARY.
```

The sealed design excluded 2026 from every outcome quantity before any return
existed, and nothing in this closeout changes that. Any future use of 2026 for
F6-like work requires **separate prospective governance** — a new lineage with
its own preregistration and seal. It cannot be attached to this closed result.

---

## §8 Accounting — final state

```
F6_PRIMARY_TRIAL_CONSUMED         = YES
PRIMARY_EXECUTION_COUNT           = 1
SECOND_HISTORICAL_RUN_PERFORMED   = NO
PERFORMANCE_EXPOSURE_RECORD_COUNT = 1
```

**Trial ledger.** `F-F6` exists exactly once, recorded as executed with
`F6_PRIMARY_TRIAL_SPENT = YES`, `TRIAL_COUNT_INCREMENT = 1`, m unchanged at 1.
No variant attempt, no family-specific trial, no TLT trial, no F6.b trial, no
2026 trial. This closeout adds an **append-only** dated note recording S4
acceptance rather than rewriting the row a second time. `N_trials` on the ETF
panel remains **NOT ASSERTED** — `D-ETF-COUNT` stays
`UNKNOWN_PENDING_AARON_DECISION`, and the sealed F6 design uses no DSR and no
trial-count deflation, so this closure changes no deflated figure anywhere.

**Exposure ledger.** Exactly **one** performance exposure exists for F6 — row
61, `REVEALED_TARGET_METRIC`, covering the entire sealed primary. P1, P2, the
bootstrap and the LOYO machinery belong to that same authorized run and are not
separate exposures. This closeout adds a `NO_OUTCOME` governance row that
normalizes to `NONE` and contributes **0**, exactly as the MMV closeout did; it
is **not** a second performance exposure and reveals nothing new.

---

## §9 Pinned identities

```
SEAL_ID                    CTA-EDGE-05-F6-S1-2026-09-21
S1 seal commit             0fd380682c6f0438c13ab25aa41c8fc9a3f5b70c
S2 accepted build commit   43f0bb3156673402866f4c1e2d06f25044455d48
S2 build hash              050bb3d73e7c95930d79ebb987797d5a720c5d5081f70b423c3ebeb0a9a05d49
S3 driver commit           c47fb2283b7056a1a8aedb9aeadc90e51b68c533   (see §6)
F6-AUTH commit             67e3cc1d0d0fc06aaf3a5566db1ce9156e2d8c0c   (F6-AUTH-0001)
S3 result commit           0de947cf3c733a47e51b2d8f003fe81c9255b48b
RUN_ID                     CTA-EDGE-05-F6-S3-PRIMARY-001
```

```
sealed preregistration     f26df71d4596dd8cacd261e571040b5b0e39fd37ef897c87422af31eeef275d9
sealed manifest            7e61af335eae8a3b236c13724d9705cbb269bfa393894d43f2d6fcdfa4c841c7
final event manifest       49ff27bfc20eb98265c440bac7368e92022b356d77647dce9151f012e40ed382
final independent review   23f723ed100ca71e11bc8b99f03a2ddf86988b0654ebb7b66e1537daf23ab589

raw S3 result              033ed34a6c52e6febecbef942482d345fb7c2319c4f0e6dad154c91699f70401
S3 result validation       3425c9f5a5e9e4d9651d3f5a97ddc0c53c47c1dbc89c03cd2e1fb288e4dc9e22
S3 execution record        f991286a80f40a84e1bb76074c61cc6d338a1a2ff72b0e4775cf8e9fd2a588fe
```

Ledger state **at the moment of this closeout's authorship** (both files are
modified by this same commit, so their post-closeout hashes are recorded in the
commit message rather than self-referentially here):

```
TRIAL_LEDGER    5e7a21a9b8ddec248f7784a0c38aa7bf4f30f5afa76e89c3ef1cc166280769de
                F-F6 present once, EXECUTED, trial spent
EXPOSURE_LEDGER 2ec7c6b6e2a4dd640e7f14562b3899dd6410c135a4b52b36969afb54f56a37aa
                row 61 REVEALED_TARGET_METRIC, exactly one F6 performance exposure
```

---

## §10 What F6 never obtained

```
INDEPENDENT_CONFIRMATION = NO
```

No independent confirmation of the F6 result exists, and none was ever obtained.
The pre-S0 independent adjudication was **never persisted** and is **not
recovered**; `F6_INDEPENDENT_ADJUDICATION_CONTROLLER_TRANSCRIPT.md` remains a
controller-supplied reconstruction carrying no original hash. The final Astra
review of 2026-09-21 was a **pre-S1 design review** that expressly did not
authorize the seal and never saw an outcome — it is not confirmation of this
result and must never be cited as such.

```
HISTORICAL_PROVENANCE_RESERVATION = YES (carried into closure, unresolved)
```

The evidence ceiling `supported` was a ceiling only. Nothing here is upgraded to
`supported`, `confirmed` or `independently confirmed`.

---

## §11 Programme state

```
S4                  = COMPLETE
CTA_EDGE_05_F6      = CLOSED / UNRESOLVED / NOT_PROMOTED
ROUND1_F6_ACTIVE    = NO
NEXT_EDGE_STARTED   = NO
ROUND2_AUTHORIZED   = NO
```

```
CONTROL RETURNS TO THE PROGRAMME CONTROLLER FOR NEXT-EDGE SELECTION.
No other candidate was started, no Round 2 was authorized, and no new research
design was written.
```

---

## §12 Cross-references

```
sealed contract     F6_S1_PREREGISTRATION_SEALED.md
seal record         F6_S1_SEAL_RECORD.md
sealed manifest     F6_S1_SEALED_MANIFEST.json
S2 implementation   F6_S2_IMPLEMENTATION_RECORD.md
S3 execution        F6_S3_EXECUTION_RECORD.md
raw result          s3/F6_S3_RESULT.json
result validation   s3/F6_S3_RESULT_VALIDATION.json
Owner decisions     ../../../ops/OWNER_DECISION_RECORD_CTA_EDGE_05_F6.md
authorization       ../../../ops/EXECUTION_AUTHORIZATIONS.md (F6-AUTH-0001)
```
