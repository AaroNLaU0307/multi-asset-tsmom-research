# CTA-EDGE-04-MMV — FINAL CLOSEOUT

*Macro momentum on vintage data. Closed 2026-09-17 by controller decision.*

```
FINAL_LINEAGE_STATUS = TERMINAL
TERMINAL_CLASS       = D — PREDICTIVE RESPONSE UNRESOLVED
PROGRAMME_STATUS     = UNRESOLVED / LOW_POWER
FAILURE_TYPE         = INSUFFICIENT_EVIDENCE / LOW_POWER
research_status      = unresolved

EVIDENCE_CEILING     = supported  — A CEILING, NOT THE ACHIEVED VERDICT.
ACHIEVED             = UNRESOLVED / LOW_POWER.
NEVER                = confirmed · independently confirmed · supported
```

Nothing in this lineage was promoted. No result is upgraded by this closeout.

---

## §1 The final scientific verdict

```
GATE 0 / PIT                  VALID
GATE 0.5                      PASS   — pooled exact sign agreement
                                       1313 / 3270 = 40.152905 %
                                       sealed kill threshold >= 80.0 % INCLUSIVE
                                       SURVIVED. Not separable-at-position-level
                                       was NOT triggered.
PRIMARY RETURN TRIAL          m = 1   (family F-MMV)
VALID ELIGIBLE MONTH N        213
VALID SAMPLE END              2026-05

GATE 1   mean monthly GROSS return
         point   +0.00014275
         CI95    [-0.00428624, +0.00420283]
         rule    lower 95 % endpoint > 0, STRICT
         RESULT  FAIL — the 95 % interval SPANS ZERO
```

Under contract §K, first match wins: CLASS C requires the Gate-1 upper endpoint
`<= 0` and the upper endpoint is `+0.00420283`, so C does not match; CLASS D
requires the interval to span zero, and it does. **CLASS D, terminal.**

---

## §2 Failure-type semantics — what this result IS and IS NOT

The sealed §K assigns a `FAILURE_TYPE` only to CLASS E
(`TARGET_MARGIN_EXCLUDED`). It assigns none to CLASS D, which is why the
machine artifacts carry `failure_type: NONE` — that is the *sealed field*, and
those artifacts are **not edited by this closeout**. The substantive
interpretation is recorded here:

```
FAILURE_TYPE                        = INSUFFICIENT_EVIDENCE / LOW_POWER
MECHANISM_FALSIFIED                 = NO
PREDICTIVE_SIGN_RESOLVED            = NO
TARGET_MARGIN_RELIABLY_EXCLUDED     = NO
NOT_PROMOTED_DUE_TO_NEGATIVE_EFFECT = NO
```

**This is not a reliable negative result. It is an unresolved result.**

A reliable negative would be CLASS C — Gate-1 upper endpoint `<= 0` — and CLASS
C was not matched. The interval is `±0.42 %` per month around a point estimate
of `+0.014 %`: the data do not resolve the sign of the predictive response in
either direction.

> **Vocabulary warning for future readers.** `INSUFFICIENT_EVIDENCE` is a
> `FAILURE_TYPE` label, **not** a `research_status`. The programme's legal
> `research_status` vocabulary is `confirmed · supported · not_promoted ·
> falsified · active · archived · experimental · unresolved` and contains no
> `insufficient_evidence` token. The `research_status` for this lineage is
> **`unresolved`**. Do not translate one field into the other.

Under contract §O, a CLASS D result establishes nothing about causation, and
nothing about whether a different information concept, series family, mapping or
horizon would have succeeded or failed.

---

## §3 M1 and M2 — observed, not consulted

```
NET MONTHLY MEAN        +0.00000230   CI95 [-0.00443109, +0.00406748]
NET ANNUALISED SHARPE   +0.00029      CI95 [-0.531249,  +0.545330]
```

```
M1_M2_CLASSIFICATION_ROLE =
  OBSERVED IN THE AUTHORIZED PRIMARY RUN, BUT NOT CONSULTED FOR PROMOTION
  CLASSIFICATION AFTER CLASS D BECAME TERMINAL AT GATE 1.
```

Both were computed on the same bootstrap draw set and are preserved for audit.
Neither can rescue CLASS D and neither can worsen it: classes E and F both
require Gate 1 to pass first, and it did not. This is the same treatment
CTA-EDGE-02-BENB's Gate 2 received — computed, recorded, never consulted — and
it spends no separate trial.

---

## §4 The two S3 runs — one trial, one decisional result

```
MMV-S3-20260917-01         INVALID_PRIMARY_SAMPLE
                           NONDECISIONAL
                           SUPERSEDED FOR DECISIONAL PURPOSES
   reason  included the PARTIAL TERMINAL JUNE-2026 return — the row labelled
           2026-06-30, whose underlying data end 2026-06-12.

MMV-S3-REPAIR-20260917-01  SOLE DECISIONAL PRIMARY RETURN RESULT
   TRIAL COUNT              1
   REPAIR TRIAL INCREMENT   0
```

**The two runs are NOT two independent tests.** They are the same primary trial,
one of which was computed on an invalid sample. Presenting them as two results,
or counting them twice, is forbidden.

All original artifacts are preserved immutably, byte-identical, with their
exposure and provenance intact. Nothing was deleted, overwritten or rewritten.

**MMV-OD-8 = `B_EXCLUDE`**, and its authority is **pre-existing**:
`research/extensions/LOCKBOX_PROCEDURE.md` §2.1 was written **2026-09-08**, nine
days before the seal. It verifies the panel boundary at `2026-06-12`, calls the
June 2026 row *"a complete label over an incomplete period"*, and requires an
evaluation either to **(a)** truncate the terminal row and state so, or **(b)**
declare the inclusion in its preregistration. The sealed contract records the
boundary in §P and never exercises (b), so (a) binds. The first run included the
row and merely stated that it had — neither path. `NEW_SCIENTIFIC_CHOICE = NO`.

The correction removed exactly `{2026-06-30}`, added nothing, and left the
218-date decision grid untouched. Gate 0.5 was not rerun and is unaffected: it
compares decision-date position states and never requires the following month to
be a complete return observation.

---

## §5 Pinned authority chain

### Origin

| item | value |
|---|---|
| F5 discovery authority | `2026-09-15-cta-edge-discovery-r1-mechanism-feature-map-fable-01.md` |
| sha256 | `02ca5f45fe41763e55a353090645c3b2a98b6dcf5fce572623ede604e569344a` |
| family | F5 `MACRO_MOMENTUM_VINTAGE`, Claude Fable 5.1 Round-1 map |

### Owner decisions

`ops/OWNER_DECISION_RECORD_CTA_EDGE_04_MMV.md` sha256
`c19ad1cd53271b988840dbe31c81a346b282da26195b1d04f8f000ece7c4cbb3`

| id | subject | state |
|---|---|---|
| MMV-OD-1 | real-time information concept — latest-known-as-of vintage | DECIDED 2026-09-16 |
| MMV-OD-2 | series identity — inflation (`CPILFENS`) and policy (FOMC target) | DECIDED 2026-09-16 |
| MMV-OD-3 | MMV-specific economic materiality — net Sharpe target `+0.30` | DECIDED 2026-09-16 |
| MMV-OD-4 | separability kill threshold — `>= 80.0 %` INCLUSIVE | DECIDED 2026-09-16 |
| MMV-OD-5 | execution and cost footing — 2 bps one-way, canonical wrapper | DECIDED 2026-09-16 |
| MMV-OD-6 | signal construction semantics, coefficient table, VNQ/RWX exclusion | DECIDED 2026-09-17 |
| **MMV-OD-7** | **NEVER CREATED** — the UNBOUND-4 policy-availability question was `RESOLVED_BY_EXISTING_AUTHORITY`, so no new decision was opened. `MMV_OD_7_CREATED = NO`, attested in the seal manifest check C1. | DOES NOT EXIST |
| MMV-OD-8 | terminal-month policy — `B_EXCLUDE` | DECIDED 2026-09-17 |

> **The OD-7 gap is real, not a missing file.** Anyone auditing the sequence
> should expect to find nothing at OD-7.
>
> **MMV-OD-8 is recorded here and in the `MMV-AUTH-0003` grant**, not in the
> Owner decision record, which this closeout does not modify. If the controller
> wants OD-8 transcribed into that document, that is a separate instruction.

### Stage artifacts

| stage | artifact | sha256 | commit |
|---|---|---|---|
| S0 FRAME | `MMV_S0_FRAME.md` | `c4d77a6b3f7699c588ac4df92e6767465310242bca5795f5e65bcdcffb010d0c` | `89b7949` |
| S0 amendment | `MMV_S0_AMENDMENT_01.md` | `08a245caaac543db6bbd2f4f50f47f1e8d50cb0196c5ec4f58e5200131556c35` | `cddc5e0` |
| S1 hold record | `MMV_S1_HOLD_RECORD.md` | `5fde08d3c7ebf910aacb38a25bf8b848dc057309ee60d2120029ab8144efb391` | `8a60a66` |
| raw data freeze | `MMV_RAW_DATA_MANIFEST.md` | `5b4589db5f83076a6bea83816157e512404986b260080ad1b814efc7fdb3afeb` | `8a60a66` |
| **S1 SEAL — contract** | `MMV_PREREGISTRATION.md` | `4bad9f0bcdb7e4991ab920d12e24a60f4d237205e5a43af693a8dadadb56b225` | `cdb01fd` |
| **S1 SEAL — manifest** | `MMV_SEAL_MANIFEST.md` | `75016e778ad58e8fe16e4833cf91c19eb52448b4d42138ab265460f371e8c0d5` | `cdb01fd` |
| S2 BUILD | `MMV_S2_BUILD.md` | `5cb4bb215a383d873e6425972e66202224f266c282c9272a594135c9b631d521` | `dc2817b` |
| policy freeze — record | `MMV_POLICY_SCHEDULE_FREEZE.md` | `f368b840de31aee67afe3eefbd92e244af0cc20478cd175948062a006813086c` | `d52883f` |
| policy freeze — schedule | `MMV_POLICY_ANNOUNCEMENT_SCHEDULE.csv` | `ae34bf1e192c4355fb71136a3e3017dfd07525ac8e48d7d3ea102130fa6a11da` | `d52883f` |
| GATE 0.5 — record | `MMV_GATE05_RESULT.md` | `05e20ef8740ccd55b051c4be31b0b85e1b38e9479ef703009037dcd1d8062440` | `8a30ec3` |
| GATE 0.5 — machine | `gate05/MMV_GATE05_RESULT.json` | `1fa8df006574199cef2a6153f57f354d6fa93475b07c5c576036cebb09b6c3d8` | `8a30ec3` |
| GATE 0.5 — audit | `MMV_GATE05_AUDIT.md` | `029a5618182a9043680f14102b57de25386ce6bf87569c717d3520185fbee713` | `059f359` |
| **S3 INVALID — record** | `MMV_S3_RESULT.md` | `4ae4ad2a43345d86639a8f9a0b282c46d3c8af0f500fa72be612c1134b0d4d3f` | `e9c132b` |
| **S3 INVALID — machine** | `s3/MMV_S3_RESULT.json` | `70fc6f91ddcc9ce4888c76c4016d32684c8c273c9d9348754814a5860c306a5e` | `e9c132b` |
| **S3 VALID — record** | `MMV_S3_REPAIR_RESULT.md` | `6586d6814746c1812cb726881e7bcf3a3296cc4d567da25c95f0bdb10348ad59` | `069b185` |
| **S3 VALID — machine** | `s3/MMV_S3_REPAIR_RESULT.json` | `987f50b49083f42d6ddd79f718430466ebdaf335f363e196cdce94a32bbd59a0` | `069b185` |
| terminal-month authority | `research/extensions/LOCKBOX_PROCEDURE.md` | `5d786ad832a1507e4b82575ed1782076de3ce3ee78d98dd450ddbdcbec45d437` | `df5b28a` |

### Execution authorizations — all CONSUMED, permanently

| id | scope | run | commit |
|---|---|---|---|
| MMV-AUTH-0001 | PnL-free Gate 0.5 | `MMV-GATE05-20260917-01` | `8d37746` |
| MMV-AUTH-0002 | primary historical return | `MMV-S3-20260917-01` *(invalid sample)* | `a6748e7` |
| MMV-AUTH-0003 | primary-sample correction | `MMV-S3-REPAIR-20260917-01` *(decisional)* | `1734dcb` |

```
Commit chain
89b7949 S0 -> 32430a2 -> cddc5e0 -> 6e6b1a5 -> 8a60a66 -> cdb01fd S1 SEAL
-> dc2817b S2 -> d52883f policy freeze -> 8d37746 AUTH-0001 -> 6918688 driver
-> 8a30ec3 GATE 0.5 -> 059f359 audit -> 93d9a47 S3 driver -> a6748e7 AUTH-0002
-> e9c132b S3 (invalid) -> cd41614 repair driver -> 1734dcb AUTH-0003
-> 069b185 S3 REPAIR (valid)
```

---

## §6 NO RESCUE — binding within this lineage

The following are **prohibited** in CTA-EDGE-04-MMV, permanently:

```
alternate inflation series · headline CPI · core PCE · FEDFUNDS · DGS2
alternate growth aggregation · alternate asset mapping
alternate LQD treatment · alternate GLD treatment · adding VNQ/RWX
alternate lookback · alternate threshold · alternate cost · alternate bootstrap
alternate endpoint · component selection · longer sample · first-release rescue
```

`RESCUE_AUTHORIZED = NO.`

Any materially different future study requires a **NEW LINEAGE** with its own
preregistration and seal. That is an Owner decision and is not a continuation of
this one. A new lineage does not inherit this lineage's sample, and the ETF price
panel remains `REUSED / BURNED` (context T0, KB-1, 6 of 6), with `N_trials`
**NOT ASSERTED** and `D-ETF-COUNT` still `UNKNOWN_PENDING_AARON_DECISION`.

---

## §7 First-release concordance diagnostic — NOT RUN

```
FIRST_RELEASE_DIAGNOSTIC = NOT RUN
```

It was preregistered in §L.1 with `NO threshold · NO pass/fail · NO promotion ·
NO rescue · NO kill`. The primary lineage is already terminal, so no additional
outcome or interpretive exposure is justified for programme decision-making. It
was never run at any stage — not at S2, not at Gate 0.5, not at either S3 run,
and not here.

---

## §8 Programme lesson — TERMINAL_MONTH_POLICY

**Every future CTA-EDGE preregistration must explicitly declare a
`TERMINAL_MONTH_POLICY` before outcome exposure.**

> A calendar month-end **label** does not itself prove that the underlying
> period is complete.

`src/signals.py::to_monthly` labels the last available close in a calendar month
at that month's calendar end. When the panel is frozen mid-month, the resulting
row is a complete label over an incomplete period, and it will silently enter a
monthly mean or a `×√12` Sharpe as though it were a full month.

This was **documented before it bit**: `LOCKBOX_PROCEDURE.md` §2.1 states the
trap and calls it *"the first item every new candidate's A2 challenge should
check"*. The MMV S3 run did not check it. The lesson is not that the rule was
missing — it is that a pre-existing written rule with no mechanical enforcement
did not prevent the error.

### Programme-level refinement, recorded for future validation work

Completeness should ultimately be determined using **the authoritative final
trading date for the relevant calendar month**, not merely whether the panel
contains observations in a later month.

**The MMV repair's guard is weaker than that, and this is stated plainly rather
than glossed.** The repair uses: *month M is eligible only if the panel contains
a date strictly after M's last calendar day.* That predicate is:

* **sufficient and conservative at the panel boundary**, which is the only place
  it was applied — it fails closed on the terminal month and correctly excluded
  June 2026;
* **but not a true completeness test mid-panel** — a panel missing the final
  days of month M while carrying data in M+1 would pass the check while M is in
  fact incomplete.

A trading-calendar-based test would catch that case; the panel-continuation test
would not. **The accepted MMV repair is NOT altered on this basis**: no such gap
exists in the frozen ETF panel at any month the repair evaluated, and reopening
an accepted terminal result to strengthen a guard that changed nothing would be
exactly the kind of post-result action §N forbids.

```
TERMINAL_MONTH_POLICY_LESSON_RECORDED = YES
MMV_REPAIR_ALTERED_ON_THIS_BASIS      = NO
```

---

## §9 Governance state at closeout

```
TRIAL_LEDGER    F-MMV, m = 1. Unchanged by the repair and unchanged by this
                closeout. No m = 2, no second family, no VARIANT_ATTEMPT row.
                MMV_PRIMARY_RETURN_TRIAL_SPENT = YES (spent once, corrected once,
                counted once). N_trials on the ETF panel NOT ASSERTED.

EXPOSURE_LEDGER row 56  Gate 0.5 PnL-free structural exposure (no return trial)
                row 57  the INVALID S3 exposure — RETAINED, UNEDITED
                row 58  the repair — SOLE DECISIONAL PRIMARY RESULT, cites and
                        supersedes row 57
                row 59  this closeout (no new outcome)
                Rows 57 and 58 are ONE trial. Never counted as two.

PROJECT_STATE   CTA-EDGE-04-MMV terminal status recorded. State only, never
                workflow authority.
```

**No result is upgraded by this closeout.** Not to `supported`, not to
`confirmed`, not to `independently confirmed`. The evidence ceiling was
`supported`; the **achieved** state is `UNRESOLVED / LOW_POWER`. A ceiling is
what a result could at most have been, never what it was.

Design exposure, unchanged: `FABLE_DESIGN_EXPOSED = YES` (originated F5, advised
MMV-OD-1 and MMV-OD-6; barred from blind certification of this design,
implementation or result). `ASTRA_DESIGN_EXPOSED = NO`, which remains an
**inference from absence** — Astra's Round-1 map is not persisted in this
workspace — and must never be represented as a positive attestation.

No independent verification of this lineage was ever obtained. Every result here
is `BUILDER CLAIM` plus `MECHANICAL EVIDENCE`, and never
`INDEPENDENT VERIFICATION`.

---

## §10 Closeout

```
CTA-EDGE-04-MMV = TERMINAL
No further outcome analysis. No rescue. No new lineage started.
```

The mechanism was not falsified, the predictive sign was not resolved, and the
economic target margin was not reliably excluded. The study answered its own
question honestly: on the sealed design and the sealed sample, it cannot tell.
