# C-A — canonical TSMOM prospective confirmation — CLOSEOUT

```
LINEAGE            = C-A · TSMOM-CA-001 · FULL
DISPOSITION        = CLOSED_PRE_OUTCOME
DECIDED            = Aaron, 2026-09-26 (ops/DECISION_LOG.md DL-008; relayed by
                     the delegate and confirmed by Aaron directly in the builder
                     session)
N_SCORED           = 0
POSITIONS_EVER_GENERATED = NONE
TARGET_OUTCOME_COMPUTED  = NO
TARGET_OUTCOME_ACCESSED  = NO
TRIAL_SPENT        = NO
KB_RESEARCH_STATUS = not applicable (the lineage never produced evidence)
CANONICAL_TSMOM    = SUPPORTED — NOT INDEPENDENTLY CONFIRMED (unchanged)
```

## Pre-closure state (from the records, not re-derived)

- **Sealed** 2026-09-13T17:42:06Z under OD-8. Contract:
  `CA_PREREGISTRATION_DRAFT.md`, sha256 `9a41d7cf…9eea882b`, at seal revision
  `7706d61df8b06beccc8f81ccdb1a22fe79680590`.
- **Pipeline went live** 2026-09-13T18:33:11Z under OD-9 (`CA-GOLIVE-0001`,
  consumed).
- **Scheduled but never reached:** the first eligible decision month-end
  (2026-09-30) and its snapshot cycle (2026-10-07).
- **No monthly cycle ever ran.** No position vector was ever generated or locked,
  and no prospective return was ever observed.

## Why closing loses nothing and needs no rescue rule

The scored window never opened. No outcome, interim or terminal, exists for anyone
to have seen. So the closure spends no trial, moves no exposure, and alters no
evidence.

## Left untouched, deliberately

- **Sealed records.** The sealed preregistration, `ops/OWNER_DECISION_RECORD_PHASE_B.md`
  (OD-1 to OD-9), the snapshot and instrument registries, and the S_0 and S_G
  identities all stay as they are.
- **Operational files.** `prospective/CA_OPERATIONAL_STATE.json` and the runbook
  still read "live". They are kept as historical operating records, and this file
  supersedes them for current state.
- **The protected store and key outside the repository**
  (`%LOCALAPPDATA%\ca_prospective_store`). Removing them would be a permanent
  deletion, which is Aaron's gate. The store contains no position, because none was
  ever generated.

## Known defects in the unused pipeline

These are recorded for anyone who ever opens a new lineage from this code. They were
found read-only on 2026-09-26 and were **not** fixed, because the build decision was
withdrawn (DL-003).

1. **The live branch was never built.** `prospective/ca_pipeline.py`
   `monthly_cycle(dry_run=False)` raises `NotImplementedError`.
2. **The scheduler skips the cycle it should run.** `next_scheduled_event`
   advances past a cycle once `decision + BDay(5) < now`. As a result, `due_now`
   is true only at the exact instant 00:00:00, so a due cycle is skipped silently.
3. **Exchange holidays are ignored.** `BDay` does not account for them.
4. **One rule was still open.** SB-3, the second-source rule for missing bars, was
   still open in the preregistration text.

## Revival

Only as a **new lineage**, with its own S0, preregistration and seal. That includes a
genuinely prospective start after the new seal. C-A's seal is not reusable authority
for a later start.
