# CTA-EDGE-05 / F6 — S3 SEALED PRIMARY EXECUTION RECORD

```
RUN_ID                     = CTA-EDGE-05-F6-S3-PRIMARY-001
SEAL_ID                    = CTA-EDGE-05-F6-S1-2026-09-21
SEAL_COMMIT                = 0fd380682c6f0438c13ab25aa41c8fc9a3f5b70c
BUILD_COMMIT               = 43f0bb3156673402866f4c1e2d06f25044455d48
BUILD_HASH                 = 050bb3d73e7c95930d79ebb987797d5a720c5d5081f70b423c3ebeb0a9a05d49
F6_AUTH_COMMIT             = 67e3cc1d0d0fc06aaf3a5566db1ce9156e2d8c0c
AUTHORIZATION_ID           = F6-AUTH-0001
OWNER_LITERAL              = "run F6"
DATE                       = 2026-09-22

F6_OUTCOME_EXPOSURE_OCCURRED = YES
F6_PRIMARY_TRIAL_CONSUMED    = YES
PRIMARY_EXECUTION_COUNT      = 1
SECOND_HISTORICAL_RUN        = NO
```

> **This record reports an execution. It is not an S4 verdict.** The terminal
> class below is the sealed classifier's mechanical output, nothing was
> interpreted beyond it, and the lineage is **not** closed here.

---

## §1 Pre-run integrity gate — passed before any target access

```
working tree clean                                    YES
HEAD == accepted build commit 43f0bb3                 YES
seal commit is a direct ancestor of the build commit  YES (exactly 1 commit apart)
```

All eight authoritative hashes recomputed and matched: sealed preregistration
`f26df71d…`, sealed manifest `7e61af33…`, final Astra review `23f723ed…`, final
event manifest `49ff27bf…`, post-seal trial ledger `d57c5601…`, S2 build
manifest `74656451…`, S2 build validation `38a21f16…`, S2 implementation record
`7188a7f5…`.

```
F-F6 rows                     1 (exactly once)
F-F6 status at gate           SEALED / NOT EXECUTED
existing F6-AUTH records      0
F6 result artifacts           0
prior F6 performance exposure 0
```

### §1.1 Environment gate

```
python 3.13.14   numpy 2.5.0   pandas 2.3.3
```

Every literal version **matches the sealed environment exactly**, so no
compatibility mechanism was needed and none was invoked. No package was
installed, upgraded or downgraded at any point.

---

## §2 Authorization

`F6-AUTH-0001` was appended to the **existing** Owner ledger
`ops/EXECUTION_AUTHORIZATIONS.md` using the established X01 / VRP / BENB / MMV
schema. No competing authorization system was created. The record is
`ONE_SHOT_SINGLE_PRIMARY_RETURN_RUN`, scope `SEALED_PRIMARY_ONLY`, bound to this
seal, build, run_id and owner literal, and it explicitly prohibits a second run,
any variant or alternative model, family-specific trials, TLT, F6.b, 2026,
reinstating a PIT-excluded release, and any S4 action.

The authorization commit `67e3cc1d` contains **only** that governance change —
107 lines added, 0 deleted. The run driver was committed separately beforehand
(`c47fb228`), precisely so the authorization commit stayed governance-only.

**Before** the authorization was committed, preflight failed on exactly the two
authorization checks and passed the other twenty. **After** it, preflight passed
22/22 reading from committed git state. That ordering is the guard working, and
it is recorded rather than asserted.

---

## §3 A transport failure before exposure, disclosed

The first `--execute` invocation **never started**. The shell redirect targeted
`research/extensions/f6/s3/f6_s3_console.log` in a directory that did not yet
exist, so bash exited 1 before exec'ing Python.

```
s3 directory existed          NO
sentinel written              NO
result artifact written       NO
therefore write_sentinel()    NEVER RAN
therefore run_real()          NEVER RAN
therefore load_price_values() NEVER RAN
=> NO TARGET VALUE WAS READ. NO EXPOSURE. TRIAL NOT CONSUMED.
```

This was a **transport / packaging failure in the invocation**, not a failed
execution: the program was never reached, so it establishes no implementation
failure and consumed nothing. The grant's own stated consumption condition —
*"CONSUMED once that run durably writes its result artifact"* — was not met,
because no artifact existed. The directory was created and the driver was then
invoked for the **first** time.

```
This is recorded, not hidden. A reader should be able to see that an invocation
failed and satisfy themselves it failed BEFORE the boundary.
```

---

## §4 The exposure boundary

```
17:00:42 UTC   PREFLIGHT PASS (22 checks, 0 failing)
17:00:42 UTC   SENTINEL WRITTEN — state TARGET_ACCESS_ABOUT_TO_BEGIN
17:00:42 UTC   irreversible boundary crossed
17:04:20 UTC   sealed pipeline COMPLETE
17:04:20 UTC   result written
17:04:20 UTC   sentinel closed — state TARGET_ACCESS_COMPLETED
```

The sentinel was written **before** the first real price read, so a crash could
not have left exposure status ambiguous. It is not a result and carries no
statistic.

Console output during the run carried operational status only — a preflight
summary, the boundary notice, periodic bootstrap progress counts and completion.
**No intermediate historical target metric was printed at any point**, and no
decision was taken between the boundary and completion.

---

## §5 What was executed

Exactly the sealed primary, once:

```
instrument     SPY only
window         2011-2025, 3772 trading sessions, NO row dropped
opening row    2011-01-03, lagged from 2010-12-31 as an INPUT BOUNDARY ONLY
events         462 archive-eligible sessions (FOMC 119 + CPI 176 + NFP 176
               = 471 labels, 9 overlaps), one trade / one unit / one observation
returns        adjusted-close close-to-close on the frozen single-vendor panel
cash           DGS3MO /100 * HOLD / 365, the /365 OWNER-CHOSEN
cost           0.0004 round trip, charged in P1 ONLY
P2 model       the ONE fixed regression, FRIDAY reference
bootstrap      15 calendar-year blocks, B = 100000, ONE common draw shared by
               P1 and P2, seed 2540719150
interval       numpy.percentile(..., method="linear") at [2.5, 97.5]
```

No override argument was available or used, no debug mode exists, no partial
family execution occurred, no preliminary or reduced-B run on real data was
performed, and no exploratory output was produced.

---

## §6 Result — mechanical, unmodified

```
P1  event-weighted mean r_net       +0.00035784
    nominal 95% interval            [-0.00062591, +0.00133231]
    P1_CLASS                        UNRESOLVED

P2  beta_EVENT                      +0.00023075
    nominal 95% interval            [-0.00078811, +0.00123375]
    P2_CLASS                        UNRESOLVED

P3  APPLICABLE                      NO
    P3_RESULT                       NOT_APPLICABLE_BY_SEAL
```

**Both intervals span zero.** Under the sealed §12 table, `P1 unresolved + P2
unresolved` maps to:

```
MECHANICAL_TERMINAL_CLASSIFICATION = UNRESOLVED
research_status                    = not_promoted
```

### §6.1 Why P3 was not computed

The sealed contract evaluates P3 **only** after P1 and P2 both pass. They did
not. Computing the fifteen LOYO deletions anyway — "just to see" — would have
manufactured an unsealed quantity on an exposed sample, so the pipeline did not
compute it and the artifact records `NOT_APPLICABLE_BY_SEAL` rather than a
number.

### §6.2 What this result is not

```
A FAILURE TO ESTABLISH POSITIVITY IS NOT A RELIABLE NEGATIVE.
```

Neither interval excludes zero, so neither a positive nor a negative effect is
established. There is **no** `LOW_POWER` label, **no** observed-power
calculation and **no** mechanism-falsification label — none exists for F6, by
seal. `UNRESOLVED` means unresolved.

```
EVIDENCE_CEILING = SUPPORTED is a CEILING, NOT AN ACHIEVED VERDICT.
SAMPLE_REUSE_CLASS = T0_REUSED_DEPENDENT.
INDEPENDENT_CONFIRMATION = NO.
```

---

## §7 Structural validation — no second run

```
S3_RESULT_VALIDATION = PASS (0 failing)
HISTORICAL PANEL REREAD = NO
SECOND_HISTORICAL_RUN_PERFORMED = NO
```

The validator checks hashes, counts, sealed constants, provenance, artifact
completeness, the CI-to-class arithmetic recomputed from the recorded endpoints,
P3 applicability, and the terminal-table mapping — the last three cross-checked
against the **independent oracle**, which imports nothing from the engine. It
never reopens the price panel and never recomputes the trial.

Two validator defects were found and fixed **in the validator, not the result**:
a substring scan flagged `bootstrap_seed_lit`**era**`l` and `cov`**era**`ge_claim`
as "era" diagnostics, and it counted its own output file. Both were replaced with
an exact key-allowlist derived from the sealed schema, which is stricter — it
catches *any* undeclared field rather than only keyword-shaped ones. **No result
value was touched.**

---

## §8 Accounting

```
EXPOSURE_LEDGER_CHANGED        YES   exactly ONE row (61), REVEALED_TARGET_METRIC
TRIAL_LEDGER_CHANGED           YES   F-F6 recorded as executed, increment 1
F6_PRIMARY_TRIAL_CONSUMED      YES
VARIANT_ATTEMPT ROWS ADDED     0
```

One exposure row covers the **entire** sealed primary. P1, P2, the bootstrap and
the LOYO machinery belong to the same authorized run and are **not** separate
exposures. No new exposure taxonomy was invented.

The `F-F6` status column was updated **in place** to record the consumed trial —
the same pattern `F-BENB` and `F-MMV` carry — and the superseded sentence is
quoted verbatim in a dated disclosure note beneath the register, so the change is
auditable rather than silent. Nothing else in the row was altered, and no row was
deleted or reordered. `N_trials` on the ETF panel remains **NOT ASSERTED**.

---

## §9 What was NOT done after the result

```
NO post-result research of any kind.
```

Not attempted, not computed, not inspected: why it resolved as it did beyond the
sealed outputs · per-family FOMC / CPI / NFP slicing · another benchmark · another
cost · another window · another start date · added or dropped controls · a changed
bootstrap or year definition · dropping a year · reinstating a PIT-excluded
release · 2026 · TLT · F6.b · parameter comparisons · rescue hypotheses.

If any of that is ever to happen, it belongs to a **future separately governed
lineage** with its own preregistration and seal.

---

## §10 Status

```
S3 EXECUTION           COMPLETE
S4_VERDICT_AUTHORIZED  NO
LINEAGE CLOSED         NO
```

The controller performs S4 acceptance after reviewing this run. This record does
not close the lineage, does not declare promotion beyond the sealed mechanical
class, does not start the next edge and writes no new research design.

```
result      s3/F6_S3_RESULT.json
validation  s3/F6_S3_RESULT_VALIDATION.json
sentinel    s3/F6_S3_RUN_SENTINEL.json
seal        F6_S1_PREREGISTRATION_SEALED.md
```
