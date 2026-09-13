# C-A PROSPECTIVE PIPELINE — OPERATIONS RUNBOOK

```
STATUS            = BUILT AND SYNTHETICALLY VALIDATED. NOT LIVE.
GO-LIVE REQUIRES SEPARATE OWNER AUTHORIZATION.
S_G_CREATED       = NO
PIPELINE_GO_LIVE  = NOT YET
N_scored          = 0
FIRST_ELIGIBLE_SCORED_PERIOD = NOT YET DETERMINED
SEALED CONTRACT   = ../CA_PREREGISTRATION_DRAFT.md  (SEALED 2026-09-13T17:42:06Z)
```

> **GO-LIVE REQUIRES SEPARATE OWNER AUTHORIZATION.** The C-A S1 seal did not grant
> it and the S2 build authorization did not grant it. `ca_golive.establish_go_live`
> refuses without a `GoLiveAuthorization` constructed by Aaron. Until that happens
> there is no prospective record, no eligible month, and nothing to score.

---

## 1. Prerequisites before go-live may even be requested

| # | Prerequisite | Where |
|---|---|---|
| 1 | Sealed prereg hash matches `9a41d7cf…` | `ca_contract.assert_seal_intact()` — runs on every import |
| 2 | Frozen panel hash matches `3d2a7a56…` | `ca_store.assert_frozen_panel_intact()` |
| 3 | Runtime matches the pin (py 3.13.14 / pandas 2.3.3 / numpy 2.5.0) | `ca_contract.assert_runtime()` |
| 4 | S2 test suite green | `python research/extensions/ca/prospective/ca_s2_tests.py` |
| 5 | Instrument registry present, 17 objects, §K SATISFIED | `ca_identity.load_registry()` |
| 6 | **Owner go-live authorization** | `GoLiveAuthorization(owner="Aaron", …)` |

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

Blindness is **not** enforced by operators choosing the polite API. A go-live
preflight probe showed that the first build's protected files were plaintext JSON
in the working tree, so `cat`, an editor, a repo grep or a one-line `json.load`
exposed a position vector and an outcome payload with no authorization. Three
mechanisms now close that, and `ca_blind` owns all three:

1. **Protected content lives OUTSIDE the repository.** Default
   `%LOCALAPPDATA%\ca_prospective_store` (override with `CA_PROSPECTIVE_STORE`).
   A store path inside the repo is **refused**, so git, grep, diff, editors and
   code review can never surface protected content.
2. **Encrypted at rest.** Bytes on disk are ciphertext (encrypt-then-MAC,
   domain-separated subkeys, HMAC-SHA256 counter-mode keystream — stdlib, because
   no AEAD library is installed here). `cat` yields nothing.
3. **The key lives outside the repository and is never committed.** Default
   `<store>/blind.key` (override with `CA_PROSPECTIVE_KEY_FILE`).

**Honest limit, stated plainly.** Aaron owns this machine and the key file, so this
is *not* secrecy against the Owner and never can be. What it provides is the
standard the contract requires: the sealed blindness rule no longer depends only on
voluntary API discipline. Ordinary operational use cannot expose a position vector
or an outcome; circumventing it now requires deliberately locating the key and
calling a decryption path, which is a knowing act rather than an accident.

**Reproducibility is not weakened.** The SHA-256 of the *plaintext* is recorded in
the clear inside every envelope, so record identity stays verifiable without
decrypting. `PositionLedger.position_identity()` returns it and is operator-safe.

**The supported machine path.** `ca_blind.MachineCapability` names the purpose —
`TURNOVER_PRIOR_POSITION`, `LOCKED_VS_RECOMPUTED_DIAGNOSTIC`, `TERMINAL_REVEAL` —
and `PositionLedger.machine_read_position()` requires one. No operator-facing
report constructs a capability. An unsupported purpose is refused.

**Key custody at go-live.** The key is created on first use if absent. Back it up
**outside the repository**: losing it makes protected outcomes unrecoverable, and
committing it would silently undo the whole boundary. It must never enter git.

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
