# PROJECT_STATE — multi-asset TSMOM research

**Current state only.** This file is governed by `QUANT_WORKFLOW_VNEXT.md` v2 §6, which
lives in the workspace and is not part of this repository.

- **Never authority.** It records state; it does not decide anything.
- **Rewritten at every checkpoint.** Superseded facts are deleted, not annotated.
- **Not outcome-blind.** Do not give it to a seat that must stay blind.

**Where the history is.** The full pre-v2 text (1,654 lines) is frozen byte-exact in
[`PROJECT_STATE_ARCHIVE_2026-09-26.md`](PROJECT_STATE_ARCHIVE_2026-09-26.md), sha256
`a2cae76f…1db3c9`. That archive is the **verdict record for X01 and Time-Series Value**,
whose authoritative home was that file.

**Decisions from 2026-09-26 onward** are in [`ops/DECISION_LOG.md`](ops/DECISION_LOG.md).

```
UPDATED            = 2026-09-26 — Round 2 PARKED (DL-011); earlier: state cut DL-002,
                     C-A closure DL-008
RESEARCH_QUESTION  = find, and honestly falsify, standalone systematic-macro / CTA
                     edges beyond the frozen canonical TSMOM benchmark
MANDATE            = standing research-mode authorization (DL-009,
                     ops/MANDATE_2026-09-26_AGI_RESEARCH_MODE.md); DORMANT — no
                     research under it until a revival S0 is opened (DL-011)
STAGE              = STOPPED. Round 1 CLOSED / EXHAUSTED. Round 2 PARKED_PRE_OUTCOME
                     at a programme-level identifiability ceiling (DL-011;
                     research/round2/R2_CLOSEOUT.md); no trial spent
REVIVAL            = a new S0 under one of: (a) an a-priori annual-horizon mechanism
                     absent from the century literature, on JST, exposure disclosed
                     (delegate gate); (b) Aaron funds long-history futures data
                     (Owner gate); (c) an honest prospective lineage, MDE stated
                     up front
CANONICAL_TSMOM    = SUPPORTED — NOT INDEPENDENTLY CONFIRMED; frozen research
                     benchmark (STUDY_SUMMARY.md)
ACTIVE_LINEAGES    = NONE
LIVE_GRANTS        = NONE — every grant in ops/EXECUTION_AUTHORIZATIONS.md is ONE_SHOT
                     and spent; CA-GOLIVE-0001 consumed, void by C-A closure
LIVE_OBLIGATIONS   = NONE
OUTCOME_EXPOSURE   = ops/EXPOSURE_LEDGER.md (append-only)
TRIAL_ACCOUNTING   = research/extensions/TRIAL_LEDGER.md (view) ·
                     research/extensions/SAMPLE_REUSE.md. ETF panel N_trials NOT
                     ASSERTED (D-ETF-COUNT = UNKNOWN_PENDING_AARON_DECISION); every
                     candidate on it is T0_REUSED_DEPENDENT, ceiling `supported`
OPEN_BLOCKERS      = NONE
NEXT_DECISION      = Aaron: whether to fund long-history futures data (revival b).
                     Open, not due: D-ETF-COUNT (delegate)
```

**Round-2 carry-forward constraints:** see [`ROUND1_CLOSEOUT.md`](ROUND1_CLOSEOUT.md) §7.

## Closed lineages

Each line gives the lineage, its status and where the record lives.

| lineage | status | record |
|---|---|---|
| X01 · TSMOM-EXT-001 | CLOSED 2026-09-13 · INSUFFICIENT_EVIDENCE (KB `unresolved`) | [archive](PROJECT_STATE_ARCHIVE_2026-09-26.md) (verdict home) · `research/extensions/x01/X01_EVIDENCE.json` |
| Time-Series Value | CLOSED 2026-09-13 · materially adverse under the sealed construction (KB `not_promoted`) | [archive](PROJECT_STATE_ARCHIVE_2026-09-26.md) (verdict home) · `research/extensions/value/VALUE_EVIDENCE.json` |
| TSMOM-VRP-01 | CLOSED 2026-09-14 · UNRESOLVED (Class 3) | [VRP_HISTORICAL_CLOSURE.md](research/extensions/vrp/VRP_HISTORICAL_CLOSURE.md) |
| C-A · TSMOM-CA-001 | CLOSED_PRE_OUTCOME 2026-09-26 · N_scored = 0 | [CA_CLOSEOUT.md](research/extensions/ca/CA_CLOSEOUT.md) |
| C-B | PARKED | [archive](PROJECT_STATE_ARCHIVE_2026-09-26.md) |
| F1 / TA · CTA-EDGE-01 | CLOSED PRE-OUTCOME | [TA_CLOSURE.md](research/extensions/ta/TA_CLOSURE.md) |
| F3 / BENB · CTA-EDGE-02 | NOT PROMOTED | [BENB_CLOSURE.md](research/extensions/benb/BENB_CLOSURE.md) |
| PINS · CTA-EDGE-03 | PARKED PRE-OUTCOME (S0 HOLD) | [PINS_CLOSURE.md](research/extensions/pins/PINS_CLOSURE.md) |
| MMV · CTA-EDGE-04 | UNRESOLVED / NOT PROMOTED (terminal class D) | [MMV_CLOSEOUT.md](research/extensions/mmv/MMV_CLOSEOUT.md) |
| F6 · CTA-EDGE-05 | CLOSED_UNRESOLVED_NOT_PROMOTED | [F6_CLOSEOUT.md](research/extensions/f6/F6_CLOSEOUT.md) |
| F4 | PARKED PRE-OUTCOME | [F4_PREOUTCOME_PARK_CLOSEOUT.md](research/extensions/f4/F4_PREOUTCOME_PARK_CLOSEOUT.md) |
| F7 | NON-RUN, CLOSED | [F7_NONRUN_DISPOSITION.md](research/extensions/F7_NONRUN_DISPOSITION.md) |
| F2 / F8 / F9 / F10 | BLOCKED / PARKED / NOT STANDALONE; never opened | [CTA_EDGE_04_CANDIDATE_AUDIT.md](research/extensions/CTA_EDGE_04_CANDIDATE_AUDIT.md) |

Round-1 dispositions are derived in [`ROUND1_CLOSEOUT.md`](ROUND1_CLOSEOUT.md). Where it
disagrees with a lineage's own record, the lineage record wins.
