# C-A PROSPECTIVE PIPELINE — OPERATIONS RUNBOOK

```
STATUS            = **LIVE** since 2026-09-13T18:33:11Z (Aaron's OD-9).
S_G_CREATED       = YES   sha256 8e2e3de98384c470a3ffef947f3fee2b17893b25c8caacdbc15f371b5a768a35
PIPELINE_GO_LIVE  = 2026-09-13T18:33:11Z
PROSPECTIVE_START = 2026-09-13T18:33:11Z
FORWARD_BOUNDARY  = 2026-09-11
FIRST_ELIGIBLE_DECISION_MONTH_END = 2026-09-30 (scheduled; confirmed from that month's snapshot)
FIRST_ELIGIBLE_SCORED_MONTH       = 2026-10
N_scored          = 0
SEALED CONTRACT   = ../CA_PREREGISTRATION_DRAFT.md  (SEALED 2026-09-13T17:42:06Z)
TERMINAL_REVEAL_AUTHORIZED = NO
```

> **GO-LIVE HAS OCCURRED** (OD-9, 2026-09-13T18:33:11Z). The pipeline is now in
> prospective accrual. `N_scored = 0` until the first complete eligible holding
> month (2026-10) has genuinely elapsed under the sealed process.
>
> **The terminal reveal is a SEPARATE Owner authorization that does not exist.** No
> interim reveal may be created, and there is no debugging exception: if an
> operational incident seems to require inspecting protected content before the
> terminal reveal, **HOLD and return to Aaron** for a new explicit Owner decision.

---

## 1. Prerequisites before go-live may even be requested

| # | Prerequisite | Where |
|---|---|---|
| 1 | Sealed prereg hash matches `9a41d7cf…` | `ca_contract.assert_seal_intact()` — runs on every import |
| 2 | Frozen panel hash matches `3d2a7a56…` | `ca_store.assert_frozen_panel_intact()` |
| 3 | Runtime matches the pin (py 3.13.14 / pandas 2.3.3 / numpy 2.5.0) | `ca_contract.assert_runtime()` |
| 4 | S2 test suite green | `python research/extensions/ca/prospective/ca_s2_tests.py` |
| 5 | Instrument registry present, 17 objects, §K SATISFIED | `ca_identity.load_registry()` |
| 6 | Off-repository **key backup destination chosen** (§5A) | operational decision at go-live |
| 7 | Protected store **explicitly initialized** — `initialize_blind_store()`; not done yet | `ca_blind` |
| 8 | **Owner go-live authorization** | `GoLiveAuthorization(owner="Aaron", …)` |

`C_D_PASS` is **not** a go-live prerequisite. It is required before the first
*reveal*, not before accrual (sealed §S). `SB-3` blocks `C_D_PASS` only.

---

## 2. Go-live, once authorized

1. Acquire the designated go-live base snapshot and pass it to
   `ca_golive.establish_go_live(registry=…, panel=…, authorization=…)`.
2. It registers `S_G` (hash, byte size, dates, per-ticker counts) **before** any use.
3. `PIPELINE_GO_LIVE` is established at that moment.
4. `PROSPECTIVE_START = max(SEAL_TIMESTAMP, PIPELINE_GO_LIVE)` — since go-live is
   later than the seal, `S_G` drives it.
5. `FORWARD_BOUNDARY` = the last eligible market observation **strictly before**
   `PROSPECTIVE_START`.
6. `first_eligible_scored_period()` returns the first month whose **decision
   month-end is strictly after** `PROSPECTIVE_START`. The month *after* that
   decision is the first scored month.
7. Every observation between `S_0` and `S_G` is
   `POST_SEAL_UNSCORED_STATE_INPUT_ONLY`: it may update canonical state, it is
   **never scored**, it is **never retroactively T4**, it contributes **zero** to
   `N_scored`.

---

## 3. The monthly cycle

Run at **`SNAPSHOT_LAG` = 5 business days** after each calendar month-end.

| step | action | module |
|---|---|---|
| 1 | Acquire the monthly snapshot | operator + `ca_store` |
| 2 | **Register it before any scientific use** — path, hash, size, first/last date, per-ticker counts | `SnapshotRegistry.register_snapshot` |
| 3 | Confirm the frozen panel is still intact | `assert_frozen_panel_intact` |
| 4 | Lock `rf` for the decision date: DGS3MO, last non-missing print ≤ 7 calendar days old, `Y/100/12` | `ca_rf.lock_rf` |
| 5 | Compute the decision vector **from that snapshot alone** | `ca_engine.decision_vector` |
| 6 | Run the integrity gate | `ca_integrity.monthly_gate` |
| 7 | **Write the position record once** — a duplicate holding month fails loudly | `ca_ledger.PositionLedger.append` |
| 8 | Record any instrument event and its §K classification | `ca_identity.classify` |

The position must be **locked before any price of the holding month is observed**
(sealed §G.2). That ordering is the whole point of the `SNAPSHOT_LAG` schedule.

---

## 4. What operators MAY see

Exactly the sealed §T.2 allowlist, and the gate refuses to emit anything else:

snapshot present / hashed / registered · overlap within tolerance at the return
level · per-ticker **row counts**, first and last date · jump, spike and stale flags
and their disposition · `rf` present and locked, or `rf_missing` · positions
computed, positions locked · locked-vs-recomputed within tolerance (a **boolean**)
· `gross ≤ 3` and `|asset weight| ≤ 2` (**booleans**) · `n_available` ·
`N_scored` to date · `PENDING_CLASSIFICATION` and `RUN_INVALIDATING_EVENT` counts ·
instrument events and their classifications · runtime match · pipeline-health
boolean.

## 5. What operators MUST NOT see

**Before the single authorized terminal reveal, no human and no agent may see:**

cumulative return · Sharpe · drawdown · win rate · sleeve performance · FM-1
performance · the crisis-diagnostic outcome · **any position vector** · **any proxy
sufficient to infer scientific performance**.

**Positions are outcomes by another name.** The ledger record preserves the
position vector because reproducibility demands it, but it is stored **encrypted**
inside a `protected_position` envelope (§5A) and reading it requires a
`MachineCapability`. `PositionLedger.public_summary()` and
`ProtectedOutcomeStore.describe()` are the operator-facing views and emit counts,
booleans and hashes only. `ca_integrity._enforce` raises
`BlindnessBreachBlocked` rather than leak.

---

## 5A. The blindness boundary — where it actually lives

Blindness is **not** enforced by operators choosing the polite API. A go-live probe
showed the first build's protected files were plaintext JSON in the working tree,
so `cat`, an editor, a repo grep or a one-line `json.load` exposed a position
vector and an outcome payload with no authorization. `ca_blind` closes that.

**Protection.** **AES-256-GCM** from `cryptography` (pyca), a fresh 96-bit nonce per
object from `os.urandom`, and **associated data** binding each ciphertext to its own
immutable identity — record type, record id, holding month, snapshot identity,
sealed prereg hash, schema — so ciphertext cannot be silently transplanted between
records. No scientific outcome value ever goes in AAD. Authentication failure
**hard-fails**; there is no unauthenticated decryption path. Plaintext is never
written to disk: sealing happens in memory and only the envelope is written.

An earlier interim build used a hand-rolled encrypt-then-MAC construction. For a
study that must hold ~10 years that is not acceptable, and it has been **removed
entirely** — no home-grown cipher, no home-grown MAC composition, no ambient key
loader. `cryptography` is pinned in `ca_contract.PINNED_RUNTIME` and in
`requirements.txt`, and a runtime mismatch refuses to run.

**Location.** Protected content and the key live **outside the repository**
(default `%LOCALAPPDATA%\ca_prospective_store`; override with
`CA_PROSPECTIVE_STORE` / `CA_PROSPECTIVE_KEY_FILE`). A store path inside the repo is
**refused**, so git, grep, diff, editors and code review can never surface it.

### Key lifecycle — explicit, and never automatic

`initialize_blind_store()` is the **only** thing that may create a key, and it
refuses if the store is already initialized or if an unidentified key is already
present. Nothing else creates key material.

Once a store is initialized, each of these is a **HARD HOLD**:

| condition | behaviour |
|---|---|
| key file missing | `ProtectedStoreHold`. **No key is generated.** |
| key unreadable / malformed | `ProtectedStoreHold`. No key is generated. |
| key fingerprint changed | `ProtectedStoreHold`. Continuing would orphan every record. |

`unlock_store()` **never** generates a new key, continues with a different key,
overwrites the stored identity, or creates a second key. The non-secret fingerprint
`SHA256(master_key)` is recorded in the store's own state file — S2 operational
state, **never** in the sealed S1 preregistration — and is verified on every unlock.

### The capability is not decorative

A `MachineCapability` **cannot be constructed by ordinary code**; it is issued only
by an unlocked `BlindSession` and carries the key. Since there is no ambient key
loader, code that has not explicitly unlocked a fingerprint-verified store cannot
decrypt anything. Purposes are limited to `TURNOVER_PRIOR_POSITION`,
`LOCKED_VS_RECOMPUTED_DIAGNOSTIC`, `TERMINAL_REVEAL`, `SYNTHETIC_TEST`. No
operator-facing report unlocks a store.

### Honest threat boundary

Aaron owns this machine, the key file and the repository. This is **not** secrecy
against the Owner or a machine administrator, and nothing here pretends otherwise.
The property delivered is the one the contract needs: **accidental or normal
supported operator actions cannot decrypt protected content.** Deliberate
Owner/admin circumvention is outside the threat model.

Local permissions are hardened as far as the OS cheaply allows — `icacls`
inheritance removed and access granted to the current user on Windows, `chmod 0600`
elsewhere — and `permissions_report()` verifies no broad principal (Everyone,
Users, Authenticated Users) can read the store or key.

### Key custody and backup — REQUIRED BEFORE GO-LIVE

- **Losing the only key makes every protected record permanently unrecoverable.**
- The key must **never** be committed to the repository.
- The backup must live **outside the repository**.
- Restoration must verify the **same** key fingerprint recorded in the store state.
- **Restoring a different key is forbidden** — it is a HARD HOLD, not a recovery.

This project has **no existing secure-backup destination**, and none is invented
here. **A secure off-repository backup location must be chosen as part of the later
go-live operation**, before the first protected record is written. That is an
operational requirement, not a scientific decision.

**No production key exists today.** `initialize_blind_store()` has not been run
against the production store; that happens during the authorized go-live procedure.

### Reproducibility is not weakened

The SHA-256 of the *plaintext* is recorded in the clear inside every envelope, so
record identity stays verifiable without decrypting.
`PositionLedger.position_identity()` returns it on an operator-safe path.

---

## 6. Failure and hold branches

| condition | branch |
|---|---|
| Snapshot missing at the deadline | refetch inside `SNAPSHOT_LAG`; then second-source rule; else canonical `NaN → not in book`, month flagged. **Three consecutive uncovered months on one ticker → Owner review.** |
| Snapshot fails registration / hash mismatch | HOLD. Do not compute a decision on unregistered bytes. |
| Runtime mismatch | HOLD. The pipeline refuses to run (§I.4). |
| Duplicate holding month | **Hard failure.** The ledger is write-once; investigate, never overwrite. |
| `RF_MISSING` | **Continue.** The primary is completely unaffected. Record the flag; FM-1 may be repaired pre-reveal only as a mechanical/vendor correction under §J. |
| Event not covered by §J or §K | log it, hold the month `PENDING_CLASSIFICATION`, and **the Owner classifies before any outcome of those months is revealed.** A classification made after a reveal is void. |
| `MATERIAL_OBJECT_CHANGE` or ambiguity | **FREEZE** the canonical-17 record. **Do not reveal.** Do not replace the instrument — ever. A `CANONICAL_MINUS_k` successor record continues generated-not-seen as a different object. |
| Blindness breach | log immediately as a research-axis exposure event. **Any amendment after a breach ends the lineage.** |

---

## 7. `RF_MISSING`, precisely

`RF_MISSING = TRUE` when no non-missing DGS3MO print exists on or before the
decision date within 7 calendar days. Then, without exception: **do not** substitute
`DGS1MO`, **do not** carry forward an older yield, **do not** interpolate, **do
not** use a future observation. The primary is unaffected. FM-1's sample is never
shortened and the rate is never imputed. If any `RF_MISSING` month is unresolved at
the reveal: `FM-1 = NOT ADJUDICABLE — DATA INCOMPLETE` while
`PRIMARY ADJUDICATION = UNAFFECTED` — a complementary-data failure, not a
primary-study failure.

---

## 8. The terminal reveal — how it will eventually be authorized

One reveal, at `N_scored = 120` complete, eligible, non-invalidated months
(`POSITIVE_REVEAL_COUNT = 1`). It follows `LOCKBOX_PROCEDURE.md` §4 in order, and
the ordering invariant is binding: **AUTHORIZATION MUST PRECEDE PROTECTED OUTCOME
ACCESS.**

1. Identify the release contract and claim family.
2. Verify eligibility and protected-snapshot identity.
3. **Declare the planned access scope before requesting authorization.**
4. **Aaron authorizes against that declared scope. This is the gate.**
5. Only then access the outcome, within scope.
6. Log the access in `ops/EXPOSURE_LEDGER.md`.
7. Classify the evidence — T4 is fixed by when the outcome occurred relative to the
   seal, never by when it was fetched.

`ProtectedOutcomeStore.reveal()` enforces the mechanical half: owner is Aaron,
scope declared before access, `N_scored ≥ 120`, authorization not already consumed.
**No authorization exists today and this package never creates one.**

Also required before any claim above `supported`: `C_D_PASS` on record (sealed
§O.3). C-D must be implemented by a **different, independent session** — the
sessions that read `src/`, wrote the C-D specification, or built this pipeline are
all disqualified.

---

## 9. Module map

| module | role |
|---|---|
| `ca_contract.py` | sealed constants, runtime pin, build identity; re-verifies the seal on import |
| `ca_store.py` | frozen-panel guard, append-only snapshot store and registry |
| `ca_engine.py` | canonical forward engine, every convention explicit |
| `ca_rf.py` | FM-1 rate locking (OD-6) |
| `ca_ledger.py` | write-once position ledger |
| `ca_protected.py` | generated-not-seen outcome store and the reveal gate |
| `ca_integrity.py` | the §T.2 allowlist gate |
| `ca_identity.py` | §K instrument-identity events |
| `ca_golive.py` | S_G machinery and §G eligibility |
| `ca_inference.py` | sealed inference engine and §O / §P.5 classifiers |
| `ca_s2_tests.py` | 22-class S2 test suite, synthetic fixtures only |
