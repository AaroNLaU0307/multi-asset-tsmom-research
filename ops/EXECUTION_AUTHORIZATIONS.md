# EXECUTION AUTHORIZATIONS — X01

Append-only. The machine-readable authority for whether a real, outcome-bearing
X01 execution may happen.

**There are zero authorization records in this file.**
`TARGET_EXECUTION_AUTHORIZED = NO`.

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

*(none — the section below is empty by design)*
