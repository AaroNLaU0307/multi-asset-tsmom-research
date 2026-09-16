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
