# EXECUTION AUTHORIZATIONS — X01

Append-only. The machine-readable authority for whether a real, outcome-bearing
X01 execution may happen.

**This file holds exactly one authorization record.**
`TARGET_EXECUTION_AUTHORIZED = YES` for exactly one run — `X01-RUN-0001` under
`X01-AUTH-0001` — and for nothing else. The scope is `ONE_SHOT`:
once that run durably reaches step 2 the authorization is CONSUMED and can
never authorize another run, another `run_id`, or a retry.

---

## What this file is

Owner decision **D1**: a real X01 execution is authorized by a machine-readable
record committed here, and by nothing else. In particular it is *not*
authorized by:

- a statement in chat — a chat statement alone is not sufficient for production
  execution;
- `human_decisions[]` in `qros-state.yaml` — that vocabulary is closed
  (`DORMANT_ENTER`, `DORMANT_EXIT`, `REVIEW_ATTEMPT_EXCLUDED`) and means
  something else; `qros check` rejects anything outside it, and stretching a
  token to cover execution authorization would corrupt a different record;
- a passing `x01_runner.py preflight` — preflight proves byte integrity, which
  is not permission;
- a sealed preregistration or a FULL lane — those say *what* would be measured,
  never *whether* it may be measured now.

This axis is also **not** the exposure axis. `ops/EXPOSURE_LEDGER.md` (research
outcome exposure) and `ops/REVIEWER_EXPOSURE_LOG.md` (reviewer seat exposure)
are separate ledgers with separate parsers, and none of the three is derived
from another. Owner decision **D5**: writing a record here is not an exposure
event and increments nothing.

## The Owner policy this file implements

| | decision | effect |
|---|---|---|
| **D1** | dedicated append-only ledger | this file is the authority |
| **D2** | commit required | a record that is not in committed git state is `INVALID`, not merely suspect |
| **D3** | `ONE_SHOT` | one `authorization_id` authorizes exactly one outcome-bearing run; never persistent, reusable, implicit, or transferable to another `run_id` |
| **D4** | exact binding | seven identities, each compared exactly; no fuzzy matching and no fallback |
| **D5** | authorization is not exposure | exposure and trial accounting begin at the authoritative step 2 |
| **D6** | consumption at durable step 2 | permanent once step 2 is durably complete; ambiguity resolves to `CONSUMED_OR_INDETERMINATE` and is never reusable |

The implementation is `research/extensions/x01/x01_authorization.py`, and it is
the only reader that matters: everything below describes what that parser
accepts.

## Format

Records are fenced ```json blocks, in file order. **Only ```json fences are
records.** The examples in this file are in ```text fences and are therefore
invisible to the parser — which is why this file can document the format
without containing an authorization.

Any block the parser cannot fully account for makes the whole ledger unusable.
There is no partial credit: a ledger whose state is unknown fails closed.

### AUTHORIZATION — the grant

Written by Aaron, then committed. Its `status` is always `AUTHORIZED`; later
states are *appended* as LIFECYCLE records and never edited in.

```text
{
  "record_type": "AUTHORIZATION",
  "schema": {"name": "x01-execution-authorization", "version": 1},
  "authorization_id": "<unique, e.g. X01-AUTH-0001>",
  "owner": "Aaron",
  "authorized_utc": "<ISO-8601 UTC>",
  "status": "AUTHORIZED",
  "scope": "ONE_SHOT_SINGLE_OUTCOME_BEARING_RUN",
  "binding": {
    "research_id": "TSMOM-EXT-001",
    "run_id": "<unique, e.g. X01-RUN-0001>",
    "prereg_sha256": "<64 hex — the sealed preregistration>",
    "execution_infrastructure_revision": "<40 hex>",
    "construction_binding_revision": "<40 hex>",
    "inference_binding_revision": "<40 hex>",
    "manifest_sha256": "<64 hex — X01_EXECUTION_MANIFEST.json>"
  }
}
```

The `binding` block must be **exactly** those seven keys. A missing key means
the machine would check less than the Owner decided; an extra key means the
record appears to bind something nothing checks. Both are refused.

`execution_infrastructure_revision` is the revision of the code that would
execute — `x01_authorization.py`, `x01_evidence.py`, `x01_execution_tests.py`,
`x01_orchestrator.py`, `x01_runner.py` — and deliberately not the repository
HEAD: the authorization commit cannot contain its own hash. While any of those
files is uncommitted, or differs from its committed bytes, the runtime reports
an unmatchable sentinel instead of a revision and no authorization can match.

### LIFECYCLE — everything after the grant

```text
{
  "record_type": "LIFECYCLE",
  "schema": {"name": "x01-execution-authorization", "version": 1},
  "authorization_id": "<the id being transitioned>",
  "event": "STEP2_ATTEMPT_STARTED | STEP2_ABANDONED_NO_DURABLE_WRITE | CONSUMED | CONSUMED_OR_INDETERMINATE | INVALIDATED",
  "event_utc": "<ISO-8601 UTC>",
  "run_id": "<must equal the run_id the grant binds>",
  "reason": "<why>"
}
```

## Lifecycle and the crash boundary

Resolution replays this file's records in order for one `authorization_id`. The
four states the machine must distinguish are `AUTHORIZED`, `CONSUMED`,
`CONSUMED_OR_INDETERMINATE` and `INVALIDATED`; terminal states absorb, so
nothing appended afterwards can return an authorization to `AUTHORIZED`.

Consumption cannot be made atomic with the step-2 exposure write — they are two
files — so the ordering is write-ahead:

1. `STEP2_ATTEMPT_STARTED` is appended and **fsynced** before step 2 is
   attempted;
2. step 2 runs;
3. exactly one resolving event is appended:
   - step 2 durably completed → `CONSUMED` (D6: permanent);
   - the recorder *proved* nothing durable was written →
     `STEP2_ABANDONED_NO_DURABLE_WRITE`, and the authorization survives, usable
     only while all seven bound identities are unchanged;
   - anything else → `CONSUMED_OR_INDETERMINATE`.

A process that dies between 1 and 3 leaves an unresolved marker, and an
unresolved marker resolves to `CONSUMED_OR_INDETERMINATE`. The failure mode is
therefore a wasted authorization, never a reused one.

**Granting requires committed state; blocking does not.** A grant is read only
from the committed blob, so no one can authorize a run by editing a working
tree. Lifecycle events are honoured from the working tree as well, because a
run that has already spent its authorization must be stopped whether or not the
event it wrote has been committed yet.

## Append-only discipline

Do not edit or delete a record. The committed record list must remain an exact
prefix of the working-tree record list; a working tree that dropped, reordered
or rewrote a committed record is refused whole, including the grants it still
appears to contain.

## After a failure

- **Before step 2** — no exposure or trial commitment exists. The authorization
  may be retried only if step 2 is known not to have been durably written and
  all seven bound identities are unchanged.
- **During step 2, persistence ambiguous** — `CONSUMED_OR_INDETERMINATE`. A
  fresh Aaron authorization is required.
- **After step 2** — the authorization is already consumed. The run records
  `EXECUTION_MECHANICAL_FAILURE` with the `authorization_id`, the `run_id`, the
  last successfully completed orchestration stage, the failure class and the
  available provenance. That is never converted into
  `PRESERVATION_SUPPORTED`, `MATERIAL_DEGRADATION_SUPPORTED` or
  `UNRESOLVED_INSUFFICIENT_PRECISION`. There is no automatic resume; another
  real attempt needs a new `authorization_id`, a new `run_id` and a new
  explicit Aaron authorization.

## Records

### X01-AUTH-0001 — Aaron, 2026-09-12T20:05:54Z

Owner decision: **AUTHORIZE ONE REAL SEALED X01 EXECUTION UNDER
GENERATED_NOT_SEEN.** No broader authority: no scientific amendment, no
parameter change, no second run, no retry after consumption, and no
authority to reveal the target outcome. The first-execution exposure
classification is `GENERATED_NOT_SEEN` — the result may be generated and
durably stored, and must not be opened, parsed or interpreted without a
separate Owner decision.

The seven bound identities below were derived mechanically from the live
manifest and git via `x01_orchestrator.execution_identity`, which is the
same function the run itself uses, so the grant is checked against the
revision that would actually execute.

```json
{
  "record_type": "AUTHORIZATION",
  "schema": {
    "name": "x01-execution-authorization",
    "version": 1
  },
  "authorization_id": "X01-AUTH-0001",
  "owner": "Aaron",
  "authorized_utc": "2026-09-12T20:05:54Z",
  "status": "AUTHORIZED",
  "scope": "ONE_SHOT_SINGLE_OUTCOME_BEARING_RUN",
  "binding": {
    "research_id": "TSMOM-EXT-001",
    "run_id": "X01-RUN-0001",
    "prereg_sha256": "4db18f6cc084bf4a4ba9260e7ba81489e658d74adf03818aa4169208a40f54c5",
    "execution_infrastructure_revision": "4cafd68d2cbb79c20fadbfb29a6b7c1a32b49ad9",
    "construction_binding_revision": "bc6c80536cd0fefc2ed1f440ca65d1c73d270e37",
    "inference_binding_revision": "bc6c80536cd0fefc2ed1f440ca65d1c73d270e37",
    "manifest_sha256": "b0fedeb3f972f7d0a2129cbe9f7a864d11cbf3ac04bef975ad9dba2c95c25572"
  }
}
```

### LIFECYCLE — X01-AUTH-0001 — STEP2_ATTEMPT_STARTED

```json
{
  "authorization_id": "X01-AUTH-0001",
  "event": "STEP2_ATTEMPT_STARTED",
  "event_utc": "2026-09-12T20:08:01Z",
  "reason": "the authoritative step-2 exposure and trial commitment is about to be attempted; if this marker is never resolved the authorization is indeterminate and unusable (D6)",
  "record_type": "LIFECYCLE",
  "run_id": "X01-RUN-0001",
  "schema": {
    "name": "x01-execution-authorization",
    "version": 1
  }
}
```

### LIFECYCLE — X01-AUTH-0001 — CONSUMED

```json
{
  "authorization_id": "X01-AUTH-0001",
  "event": "CONSUMED",
  "event_utc": "2026-09-12T20:08:01Z",
  "evidence": {
    "exposure_record_reference": {
      "classification": "GENERATED_NOT_SEEN",
      "exposure_row": "| 2026-09-12T20:08:01Z | CURRENT_REVIEW_SCOPE | GENERATED_NOT_SEEN | NONE | ops/...",
      "journal": "ops/execution-journal/X01-RUN-0001.step2.json",
      "trial_attempts": {
        "attempts": [
          "A1 (primary)",
          "S1 (construction sensitivity)",
          "S2 (roll-rule sensitivity)",
          "E (ETF reference leg)"
        ],
        "first_row_number": 1,
        "register": "research/extensions/TRIAL_LEDGER.md",
        "rows_appended": 4
      }
    }
  },
  "reason": "STEP2_DURABLY_COMPLETED",
  "record_type": "LIFECYCLE",
  "run_id": "X01-RUN-0001",
  "schema": {
    "name": "x01-execution-authorization",
    "version": 1
  }
}
```

### VRP-AUTH-0001 — TSMOM-VRP-01 Stage-A historical run

One outcome-bearing historical Stage-A run for TSMOM-VRP-01, and nothing else.
**Stage B is NOT authorized by this grant** and remains forbidden even if Stage A
is SUPPORTED. The reveal is a SEPARATE single-use grant (`VRP-AUTH-0002`),
committed only after the post-compute integrity gate passes.

```json
{
  "authority": "CHATGPT_FINAL_S2_ACCEPTANCE_ON_BEHALF_OF_OWNER_WORKFLOW; relayed by Aaron in session",
  "authorization_id": "VRP-AUTH-0001",
  "authorized_utc": "2026-09-14T18:05:00Z",
  "binding": {
    "erratum_sha256": "b8a089ac2f1d3f26d0493684bb3512cfe564b4f82d49690c3b7daa77b28e8f1a",
    "prereg_sha256": "dd5822440bedbe58f49940651bddf656f4dbb593295b59c4eff2b45b89cf53e6",
    "research_id": "TSMOM-VRP-01",
    "run_id": "VRP-STAGE-A-RUN-0001",
    "s1_seal_commit": "16d84545ba1385a482dbac7e776b31275f6fa5f7",
    "s2_closure_commit": "f196cfdc3a866f64ca8d12d5b91bd9433b327d06",
    "stage": "STAGE_A_HISTORICAL_ONLY",
    "stage_b_authorized": false
  },
  "grant_kind": "EXECUTION",
  "owner": "Aaron",
  "record_type": "AUTHORIZATION",
  "schema": {
    "name": "vrp-execution-authorization",
    "version": 1
  },
  "scope": "ONE_SHOT_SINGLE_OUTCOME_BEARING_RUN",
  "status": "AUTHORIZED"
}
```

### VRP-AUTH-0002 — TSMOM-VRP-01 Stage-A single reveal

Committed ONLY after the post-compute integrity gate passed 19/19 on the
protected result named in the binding. Authorises exactly ONE reveal of the
predeclared Stage-A evidence package. Stage-B descriptives are NOT covered:
Stage B has not run.

```json
{
  "authority": "CHATGPT_FINAL_S2_ACCEPTANCE_ON_BEHALF_OF_OWNER_WORKFLOW; relayed by Aaron in session",
  "authorization_id": "VRP-AUTH-0002",
  "authorized_utc": "2026-09-14T18:40:00Z",
  "binding": {
    "protected_result_sha256": "baa0a07d647b4d1be082a569022dbcc09d1eb23e5f64b76374449a8139fce1bc",
    "research_id": "TSMOM-VRP-01",
    "reveals": "ONE_PREDECLARED_STAGE_A_EVIDENCE_PACKAGE",
    "run_id": "VRP-STAGE-A-RUN-0001",
    "stage": "STAGE_A_HISTORICAL_ONLY",
    "stage_b_authorized": false
  },
  "grant_kind": "REVEAL",
  "owner": "Aaron",
  "record_type": "AUTHORIZATION",
  "schema": {
    "name": "vrp-execution-authorization",
    "version": 1
  },
  "scope": "ONE_SHOT_SINGLE_REVEAL",
  "status": "AUTHORIZED"
}
```

### LIFECYCLE — VRP-AUTH-0001 — CONSUMED

```json
{
  "authorization_id": "VRP-AUTH-0001",
  "event": "CONSUMED",
  "event_utc": "2026-09-14T19:20:00Z",
  "evidence": {
    "protected_result_sha256": "baa0a07d647b4d1be082a569022dbcc09d1eb23e5f64b76374449a8139fce1bc",
    "reveal_count": 1,
    "run_count": 1,
    "run_record": "research/extensions/vrp/s3/VRP_STAGE_A_RUN_RECORD.md"
  },
  "reason": "the one governed historical Stage-A run VRP-STAGE-A-RUN-0001 completed and its evidence was durably stored as GENERATED_NOT_SEEN",
  "record_type": "LIFECYCLE",
  "run_id": "VRP-STAGE-A-RUN-0001",
  "schema": {
    "name": "vrp-execution-authorization",
    "version": 1
  }
}
```

### LIFECYCLE — VRP-AUTH-0002 — CONSUMED

```json
{
  "authorization_id": "VRP-AUTH-0002",
  "event": "CONSUMED",
  "event_utc": "2026-09-14T19:20:00Z",
  "evidence": {
    "protected_result_sha256": "baa0a07d647b4d1be082a569022dbcc09d1eb23e5f64b76374449a8139fce1bc",
    "reveal_count": 1,
    "run_count": 1,
    "run_record": "research/extensions/vrp/s3/VRP_STAGE_A_RUN_RECORD.md"
  },
  "reason": "the single authorised Stage-A reveal was performed; reveal_count = 1",
  "record_type": "LIFECYCLE",
  "run_id": "VRP-STAGE-A-RUN-0001",
  "schema": {
    "name": "vrp-execution-authorization",
    "version": 1
  }
}
```

---

### BENB-AUTH-0001 — CTA-EDGE-02-BENB S3 single governed historical run

One outcome-bearing historical run of the sealed CTA-EDGE-02-BENB contract, and
nothing else. The scope is `ONE_SHOT`: a single invocation of
`research/extensions/benb/benb_s3_run.py --execute` under `run_id`
`BENB-RUN-20260915-01`. Once that run durably writes its result artifact the
authorization is CONSUMED and can never authorize another run, another `run_id`,
another seed, or a retry.

**The reader for these records is `research/extensions/benb/benb_authorization.py`**,
which is scoped to `BENB-AUTH` ids and to the `CTA-EDGE-02-BENB` lineage. It reuses the
X01 asymmetries unchanged: **granting requires committed state** (a grant in the working
tree only is invalid), while **blocking does not** (an unreadable ledger, an unparseable
record, or more than one live grant all refuse).

`rng_seed` is `1788924436`, the first eight hexadecimal digits of the accepted S1 seal
manifest sha256 (`6aa0d214`) read as an integer. It is derived from the SEAL, not from
any outcome, and was fixed before the run. No second seed is authorized.

This grant authorizes **execution and the reveal of the sealed statistics it produces**
— unlike the VRP lineage, CTA-EDGE-02-BENB has no separate `GENERATED_NOT_SEEN` stage,
because its sealed §J classification is mechanical and its result artifact is the
verdict. It authorizes nothing beyond that: no redesign, no tuning, no rescue run, no
alternate specification, no portfolio integration, and no S4 action.

```json
{
  "authority": "OWNER EXECUTION DECISION relayed by Aaron in session as the CTA-EDGE-02-BENB S3 task brief section 0 (FIXED OWNER EXECUTION DECISION)",
  "authorization_id": "BENB-AUTH-0001",
  "authorized_utc": "2026-09-16T06:35:37Z",
  "binding": {
    "bootstrap_replicates": 10000,
    "lineage": "CTA-EDGE-02-BENB",
    "no_refetch": "live or re-downloaded data is NOT authorized; a pinned-hash mismatch is a LEVEL-1 STOP, never a substitution",
    "permitted_inputs": [
      "data/benb/HYG_raw_ohlc.csv sha256 1ed30697cd0c665d9abe3d60abfe8c03314fb8889f3a459df207c5b85cb3bce8",
      "data/benb/HYG_nav_daily.csv sha256 7735da958ef10522e39c9138b8cf8c686206585f3b805c327588fb61e9eae5de",
      "data/benb/LQD_raw_ohlc.csv sha256 9d120233fd18bbd28188c18ce5a99b8347416f58b903d7452b83b47d011fe036",
      "data/benb/LQD_nav_daily.csv sha256 3d78dbd80b92e9715eb9f6249597d65556d12b6517aad6832640e7296698007a",
      "data/benb/ishares_HYG_fund_download.xml sha256 10dcd91e095a56d83762019738aa5b14374ea5d1f723616636b52170150ec533",
      "data/benb/ishares_LQD_fund_download.xml sha256 d0cc3b0121806b20a227b00ae50d3f8523e6cc560e7bae16d715824b50ce0a47",
      "data/benb/benb_price_meta.json sha256 8179c06f8f8dd088d3b08cb9b4d6a1a8abbd210239f3e2b226e70de223d8b339"
    ],
    "permitted_operation": "exactly ONE invocation of research/extensions/benb/benb_s3_run.py --execute, which performs the LEVEL-1 structural pre-check and then the sealed CTA-EDGE-02-BENB computation as preregistered",
    "prohibited": [
      "any parameter change",
      "any horizon change (the sealed trade is open(t+1) to close(t+1) and nothing else)",
      "any cost change (5 bps one way, 10 bps round trip, sealed)",
      "any feature change (b_t, the expanding median with 250 prior observations, x_t, the discount-only sample, the t+1 ex-date union rule)",
      "any classification change (the sealed J.3 order, M1 STRICT > 0, M2 STRICT > +0.30)",
      "a second run, a second seed, an alternate run_id, a retry, an exploratory preview or a dry run on historical outcomes",
      "promotion, falsification, portfolio integration or any S4 action"
    ],
    "rng_seed": 1788924436,
    "rng_seed_derivation": "first 8 hexadecimal digits of the accepted S1 seal-manifest sha256, 6aa0d214, read as an integer: 1788924436. Outcome-independent and fixed by the Owner.",
    "run_id": "BENB-RUN-20260915-01",
    "s1_seal_commit": "c1a3f8155a9fdb86d55b620c33498f604fcbf8d0",
    "s1_seal_manifest_sha256": "6aa0d21401b9887f4a44ab6559fa10d7a59ae5a8b512e1ad306543c061483703",
    "s2_implementation_commit": "d1ccefc8c6ed6e15e6366856ff0b64a0f6516bc3",
    "sealed_prereg_sha256": "1b7ca2122ba14c4097e4d76d7a733bf0c77ab9c0d02dd93a38c25bc1be5160cf"
  },
  "grant_kind": "EXECUTION",
  "lineage": "CTA-EDGE-02-BENB",
  "owner": "Aaron",
  "record_type": "AUTHORIZATION",
  "schema": {
    "name": "benb-execution-authorization",
    "version": 1
  },
  "scope": "ONE_SHOT_SINGLE_OUTCOME_BEARING_RUN",
  "status": "AUTHORIZED"
}
```

### LIFECYCLE — BENB-AUTH-0001 — CONSUMED

The single authorised CTA-EDGE-02-BENB historical execution ran exactly once,
under `run_id` `BENB-RUN-20260915-01` with the grant's `rng_seed` `1788924436`
and the sealed `B = 10,000`, and durably wrote its result artifact. The grant is
now spent: no second run, no second seed, no alternate `run_id` and no retry is
authorized by it, and none was performed.

`BENB_PRIMARY_TRIAL_SPENT` moves `NO -> YES` in
`research/extensions/TRIAL_LEDGER.md` §6.2. `N_trials` on the ETF panel remains
**NOT ASSERTED** — `D-ETF-COUNT` is still `UNKNOWN_PENDING_AARON_DECISION`, and
the sealed design uses no DSR, so nothing here decides it.

```json
{
  "authorization_id": "BENB-AUTH-0001",
  "event": "CONSUMED",
  "event_utc": "2026-09-16T06:41:00Z",
  "evidence": {
    "alternate_seed_used": false,
    "bootstrap_replicates": 10000,
    "design_changed_after_exposure": false,
    "execution_count": 1,
    "exposure_row": "ops/EXPOSURE_LEDGER.md row 54",
    "feature_realisation_artifact": "research/extensions/benb/s3/BENB_S3_FEATURE_REALISATION.json",
    "feature_realisation_sha256": "7f4c93aa58527240295eb73f0960b871d4b58a313e93e6cc497c89062fa0c469",
    "final_class": "A-M",
    "post_outcome_tuning": false,
    "research_status": "not_promoted",
    "result_artifact": "research/extensions/benb/s3/BENB_S3_RESULT.json",
    "result_artifact_sha256": "ebc3baeed51d40916aef3c68a3e50f83ca13ad21077344dcacc5516830106157",
    "reveal_count": 1,
    "rng_seed": 1788924436,
    "run_count": 1,
    "run_record": "research/extensions/benb/s3/BENB_S3_RUN_RECORD.md",
    "second_run_performed": false
  },
  "reason": "the one governed historical run BENB-RUN-20260915-01 completed and durably wrote its result artifact; under D6 consumption is permanent",
  "record_type": "LIFECYCLE",
  "run_id": "BENB-RUN-20260915-01",
  "schema": {
    "name": "benb-execution-authorization",
    "version": 1
  }
}
```

### MMV-AUTH-0001 — CTA-EDGE-04-MMV historical PnL-free Gate 0.5 run

One historical execution of the sealed CTA-EDGE-04-MMV **Gate 0.5** — the
PnL-free position-level separability screen — and nothing else. The scope is
`ONE_SHOT`: a single invocation of
`research/extensions/mmv/mmv_gate05_run.py --execute` under `run_id`
`MMV-GATE05-20260917-01`. Once that run durably writes its result artifact the
authorization is CONSUMED and can never authorize another run, another
`run_id`, or a retry.

**The reader for these records is `research/extensions/mmv/mmv_authorization.py`**,
scoped to `MMV-AUTH` ids and to the `CTA-EDGE-04-MMV` lineage. It reuses the X01
asymmetries unchanged: **granting requires committed state** (a grant in the
working tree only is invalid), while **blocking does not** (an unreadable
ledger, an unparseable record, or more than one live grant all refuse).

`rng_seed` is **NONE**. This run is fully deterministic: the sealed Gate 0.5 is
exact integer counting over sign states, with no resampling, no simulation and
no tie-breaking. A seed would imply a stochastic step that the sealed design
does not contain.

This grant authorizes the **first historical construction of the sealed MMV
macro feature and raw position matrix**, and the reveal of the sealed Gate 0.5
statistic those produce. It authorizes **nothing about returns**. Historical
return exposure remains CLOSED whatever the Gate 0.5 outcome, and a PASS is not
a return authorization.

```json
{
  "authority": "OWNER EXECUTION DECISION relayed by Aaron in session as the CTA-EDGE-04-MMV HISTORICAL GATE 0.5 task brief (ONE-TIME PNL-FREE RUN AUTHORIZATION)",
  "authorization_id": "MMV-AUTH-0001",
  "authorized_utc": "2026-09-17T00:00:00Z",
  "binding": {
    "accepted_policy_freeze_commit": "d52883f230d1961c6c1f23b1dbb63402177e5dd3",
    "accepted_s2_commit": "dc2817b99f048f561f1db55f998e24ff2193df10",
    "lineage": "CTA-EDGE-04-MMV",
    "no_refetch": "live or re-downloaded data is NOT authorized; a pinned-hash mismatch is a STRUCTURAL STOP, never a substitution",
    "permitted_inputs": [
      "research/extensions/mmv/MMV_PREREGISTRATION.md sha256 4bad9f0bcdb7e4991ab920d12e24a60f4d237205e5a43af693a8dadadb56b225",
      "research/extensions/mmv/MMV_SEAL_MANIFEST.md sha256 75016e778ad58e8fe16e4833cf91c19eb52448b4d42138ab265460f371e8c0d5",
      "research/extensions/mmv/MMV_POLICY_ANNOUNCEMENT_SCHEDULE.csv sha256 ae34bf1e192c4355fb71136a3e3017dfd07525ac8e48d7d3ea102130fa6a11da",
      "data/mmv/MMV_RAW_MANIFEST.json sha256 908e2d6deeceedf9d74f3cc684a5ab6b1224e5960887af082aba3329787706da",
      "data/mmv/MMV_FOMC_TIMING_MANIFEST.json sha256 be6f17afdf77aafc7d44bee593a1a94a01bb9b9474112cd197e6ed177737c4f9",
      "data/mmv/INDPRO.observations.realtime.json sha256 3f53f959e399e21a060c6c7ab04392b82950c916826a1c964472d8c78682ddd9",
      "data/mmv/PAYEMS.observations.realtime.json sha256 c773c5681807fe0057dd66814aa18bfc03b8c0201be57a50f425b48e7c471bd6",
      "data/mmv/CPILFENS.observations.realtime.json sha256 75c3c36306c109b11683d808471b30aa8061a2dfc0a4141a6668e6fe8b9ad2f4",
      "output/monthly_signal_panel.csv sha256 fa154e01ec597070729b5489ee4f8ed0e588add30c70d33196d7bf3c8069173f"
    ],
    "permitted_operation": "exactly ONE invocation of research/extensions/mmv/mmv_gate05_run.py --execute, which performs the structural pre-checks and then the sealed CTA-EDGE-04-MMV Gate 0.5 as preregistered",
    "prohibited": [
      "any access to ETF returns, MMV gross or net returns, transaction-cost results, Sharpe, drawdown, hit rate, predictive regression, bootstrap, Gate 1, M1 or M2",
      "the first-release concordance diagnostic, which remains CLOSED under this grant",
      "per-instrument, per-leg or calendar-period agreement diagnostics, which are preregistered as non-promotional but are NOT required for this kill decision and are intentionally not exposed",
      "any series, transform, coefficient, mapping, threshold or cutoff change",
      "ALFRED realtime_start as the policy availability clock",
      "any imputation, carry-forward or conversion of a missing leg to zero",
      "a second run, an alternate run_id, a retry, an exploratory preview or a dry run on historical outcomes",
      "promotion, falsification, portfolio integration or any S4 action"
    ],
    "rng_seed": null,
    "rng_seed_derivation": "NONE. The sealed Gate 0.5 is deterministic exact integer counting over sign states; there is no resampling, simulation or tie-break, so no seed exists to fix.",
    "run_id": "MMV-GATE05-20260917-01",
    "run_type": "HISTORICAL_PNL_FREE_SEPARABILITY",
    "s1_seal_commit": "cdb01fdc903e97671c3ef50fde6875628ca39ac8",
    "s1_seal_manifest_sha256": "75016e778ad58e8fe16e4833cf91c19eb52448b4d42138ab265460f371e8c0d5",
    "sealed_prereg_sha256": "4bad9f0bcdb7e4991ab920d12e24a60f4d237205e5a43af693a8dadadb56b225"
  },
  "grant_kind": "EXECUTION",
  "lineage": "CTA-EDGE-04-MMV",
  "owner": "Aaron",
  "record_type": "AUTHORIZATION",
  "schema": {
    "name": "mmv-execution-authorization",
    "version": 1
  },
  "scope": "ONE_SHOT_SINGLE_PNL_FREE_GATE05_RUN",
  "status": "AUTHORIZED"
}
```

### LIFECYCLE — MMV-AUTH-0001 — CONSUMED

The single authorised CTA-EDGE-04-MMV Gate 0.5 execution ran exactly once, under
`run_id` `MMV-GATE05-20260917-01`, and durably wrote its result artifact. The
grant is now spent: no second run, no alternate `run_id` and no retry is
authorized by it, and none was performed. The run driver refuses outright if a
result artifact already exists.

The run was **deterministic** — exact integer counting over sign states, no RNG,
no resampling, no tie-break — so reproducing it requires no seed.

**This consumption did NOT spend the primary return trial.** Contract §M sets
`PRIMARY TRIAL FAMILY = CTA-EDGE-04-MMV composite, m = 1`, and that trial is the
Gate-1 return test, which remains unspent and unauthorized. Gate 0.5 is the
sealed **PnL-free** pre-PnL falsification: it compared position DIRECTIONS
against the canonical control and touched no return. `RETURN_OUTCOME_ACCESSED`
remains `NO`.

No row was written to `ops/EXPOSURE_LEDGER.md` or
`research/extensions/TRIAL_LEDGER.md` under this grant. Whether a PnL-free
position-agreement reveal warrants a ledger row is a governance question for the
controller, not a builder decision, and the brief did not direct one.

```json
{
  "authorization_id": "MMV-AUTH-0001",
  "event": "CONSUMED",
  "event_utc": "2026-09-17T00:00:00Z",
  "lineage": "CTA-EDGE-04-MMV",
  "evidence": {
    "alternate_run_id_used": false,
    "authorization_commit": "8d37746629f7cbaa741eaa13907e118eb1a35537",
    "design_changed_after_exposure": false,
    "execution_count": 1,
    "first_release_diagnostic_run": false,
    "gate05_agreement_cells": 1313,
    "gate05_eligible_cells": 3270,
    "gate05_pooled_agreement_exact": "1313/3270",
    "gate05_result": "PASS",
    "gate05_threshold": "agreement / eligible >= 4/5, inclusive",
    "per_instrument_diagnostics_computed": false,
    "post_outcome_tuning": false,
    "primary_return_trial_spent": false,
    "result_artifact": "research/extensions/mmv/gate05/MMV_GATE05_RESULT.json",
    "result_artifact_sha256": "1fa8df006574199cef2a6153f57f354d6fa93475b07c5c576036cebb09b6c3d8",
    "result_record": "research/extensions/mmv/MMV_GATE05_RESULT.md",
    "result_record_sha256": "05e20ef8740ccd55b051c4be31b0b85e1b38e9479ef703009037dcd1d8062440",
    "return_outcome_accessed": false,
    "reveal_count": 1,
    "rng_seed": null,
    "run_count": 1,
    "run_driver_commit": "6918688be6850e5f1bf513eb7f0698e7f5789a30",
    "second_run_performed": false
  },
  "reason": "the one governed historical run MMV-GATE05-20260917-01 completed and durably wrote its result artifact; consumption is permanent",
  "record_type": "LIFECYCLE",
  "run_id": "MMV-GATE05-20260917-01",
  "schema": {
    "name": "mmv-execution-authorization",
    "version": 1
  }
}
```
