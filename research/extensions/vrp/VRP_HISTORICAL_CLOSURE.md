# TSMOM-VRP-01 — HISTORICAL CLOSURE

```
LINEAGE                          = TSMOM-VRP-01
CONTRACT_ID                      = TSMOM-VRP-01-PREREG-01
HISTORICAL_RESEARCH_COMPLETE     = YES
HISTORICAL_STAGE_A               = UNRESOLVED_CLASS_3
HISTORICAL_STAGE_B               = NOT_RUN_BY_SEALED_STOP_RULE
PROSPECTIVE_CONFIRMATION         = NOT_ACTIVATED_BY_OWNER_DECISION
MORE_HISTORICAL_TUNING           = FORBIDDEN_INSIDE_TSMOM-VRP-01
STATUS                           = CLOSED
CLOSED_UTC                       = 2026-09-14
```

This document closes the TSMOM-VRP-01 historical lineage. It **changes no verdict**,
deletes nothing, and authorises nothing.

---

## 1. The historical result, unchanged

```
HISTORICAL_STAGE_A_WINDOW              = 2006-09 .. 2026-08   (240 months)
ANNUALISED_MEAN_NET_EXCESS_RETURN_ON_K = +0.073224
CI_95                                  = [+0.003906, +0.136081]
ECONOMIC_USEFULNESS_MARGIN (+E)        = +0.075
ADVERSE_FLOOR (−F)                     = −0.075
STAGE_A_STATE                          = UNRESOLVED
FAILURE_CLASS                          = 3  INSUFFICIENT_EVIDENCE / LOW_POWER
RESEARCH_STATUS                        = unresolved
EVIDENCE_CONTEXT                       = DESIGN_INFORMED_FIRST_LOCAL_USE
STAGE_A_TRIAL_SPENT                    = YES   (VIX-chain N_trials 0 → 1)
run_id VRP-STAGE-A-RUN-0001 · RUN_COUNT 1 · REVEAL_COUNT 1
protected result sha256 baa0a07d647b4d1be082a569022dbcc09d1eb23e5f64b76374449a8139fce1bc
```

**The claim, preserved verbatim in its sealed language.** The 95 % interval straddles the
required margin (`L ≤ +E ≤ U`), so the historical evidence is **insufficient to determine**
whether the sealed short-VIX-futures sleeve delivers useful compensation on committed
capital at the preregistered `+7.5 %` margin. It establishes neither that the margin is
cleared nor that it is excluded. Endpoints classify; the point estimate never does.
Nothing here speaks to prospective performance, to deployment, to portfolio
compatibility, or to any mechanism.

**Evidence context travels with every citation:** `DESIGN_INFORMED_FIRST_LOCAL_USE` —
never "fresh", never "independent".

## 2. Stage B: not run, by the sealed stop rule

Sealed §O, exhaustive:

> `Stage A Class 3 → stop historical study → Stage B never runs → only the sealed
> VRP-A-PROSPECTIVE continuation (§P)`

Historical Stage B under TSMOM-VRP-01 was never executed and **never will be** under this
lineage. `STAGE_B_TRIAL_SPENT = NO`. The Stage-B descriptives R6–R11 were neither computed
nor revealed.

## 3. Prospective confirmation: declined by the Owner

Aaron has explicitly decided **not** to activate the long-horizon VRP-A-PROSPECTIVE
experiment. Recorded exactly:

```
VRP_A_PROSPECTIVE_STATUS         = NOT_ACTIVATED_BY_OWNER_DECISION
LONG_HORIZON_PROSPECTIVE_EXPERIMENT = CLOSED_WITHOUT_ACTIVATION
ENTRY_2026_09_30                 = NOT_ARMED
MONTHLY_PROSPECTIVE_ACCRUAL      = DISABLED
SCHEDULER                        = NONE
BACKGROUND_RUNNER                = NONE
TERMINAL_120_MONTH_CLOCK         = NOT_STARTED
VRP_B_PROSPECTIVE                = NOT_ACTIVATED
```

**No trial is spent by declining prospective activation.** Declining to start a clock
constructs no strategy-return series and is not an attempt.

**Nothing had to be dismantled.** No scheduler, daemon, cron entry, background runner or
accrual job was ever created for this lineage, and no prospective snapshot or protected
prospective store exists. `vrp_prospective.py` reports `started = False` for both clocks,
which is the state it has always been in. `LONG_HORIZON_OPS_PRESENT = NO`,
`LONG_HORIZON_OPS_REMOVED = NONE`.

## 4. What is preserved, and why

Every accepted historical artifact is **research provenance** and is retained unmodified:

| kept | |
|---|---|
| S0 frame documents and the Owner Decision Record | workspace root, hash-pinned in the seal |
| the sealed preregistration and its S1 package | `research/extensions/vrp/` — byte-identical to the seal |
| the mechanical erratum | `VRP_S1_MECHANICAL_ERRATUM_01.md` |
| the S2 build, acceptance report, data manifest, specification registry, schema | `research/extensions/vrp/` |
| the S3 authorization, run record, run manifest, revealed package, gate records | `research/extensions/vrp/s3/` |
| the raw Cboe VX chain and the protected Stage-A result | git-ignored under `data/`, hash-pinned |
| the historical engine, validators and the 100-test acceptance suite | `research/extensions/vrp/` |
| the programme ledgers | `SAMPLE_REUSE.md`, `TRIAL_LEDGER.md`, `EXPOSURE_LEDGER.md`, `REVIEWER_EXPOSURE_LOG.md` |

**The S1 seal is NOT rewritten to remove its prospective clauses.** §P and §Q remain in the
sealed text exactly as sealed. A design that was sealed and then not activated is part of
the record; editing the seal to erase it would falsify the provenance. The Owner's decision
not to activate is recorded **here**, alongside the seal, not inside it.

`AUTHORITATIVE_HISTORICAL_ARTIFACTS_DELETED = NO`.

## 5. What is now forbidden inside this lineage

`MORE_HISTORICAL_TUNING = FORBIDDEN_INSIDE_TSMOM-VRP-01`. Per sealed §O, no result may
authorise changing `J`, `b`, `theta`, `E`, `F`, `s`, `beta`, `delta_tail`, the maturity,
the roll, the cost convention, the sample endpoints or the tail rule, or adding any filter.
Each is a **new lineage** with its own trial accounting and its own Owner authorisation.

The historical Stage A is **not re-run**. `VRP-AUTH-0001` and `VRP-AUTH-0002` are consumed.

An `UNRESOLVED` result is a legitimate terminal historical outcome. It is not an invitation
to retune, resample, reweight or repackage.

## 6. Relationship to VRP-PORTFOLIO-DIAGNOSTIC-01

A separate, **exploratory** diagnostic lineage (`VRP-PORTFOLIO-DIAGNOSTIC-01`) reuses the
already-generated sealed historical VRP monthly series as an input to answer a practical
portfolio question at a fixed 80/20 allocation. It is **not** TSMOM-VRP-01 Stage B, it is
**not** preregistered, it is **outcome-exposed exploratory reuse**, and it carries
`PROMOTION_POWER = NONE`.

**It does not and cannot change the verdict in §1.** TSMOM-VRP-01 remains `UNRESOLVED`,
Class 3, whatever that diagnostic shows.

*Any receiver recomputes every hash cited here before use.*
