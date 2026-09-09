# X01 — DEVIATIONS from the sealed preregistration

**Sealed contract:** `research/extensions/x01/X01_PREREGISTRATION_DRAFT.md`
**Sealed SHA256:** `9c7b104f980fddb5613f02a3e8c1fab68ed9750b03b8161d42f92c3c96986743`
**Seal revision:** `df5b28ab7324c7ba789ab231431f077288c3fd84`

This file is the **post-seal** change-control record, in the sense the operating
mode fixes: *"`DEVIATIONS.md` keeps its existing meaning — departures from an
already-sealed contract. Do not blur pre-seal amendment with post-seal
deviation."* Pre-seal design evolution lives in the preregistration's own §13
Lineage; it does **not** belong here.

**Append-only.** A row is never edited or deleted. A correction is a new row
citing the row it corrects.

**The sealed bytes are never edited by anything recorded here.** A deviation is a
record *about* the contract, not a change *to* it — editing the sealed file would
move the HEAD blob and make the canonical seal derive `SEAL_MISMATCH`.

---

## D-X01-1 — sealed §6.1 names the seed-derivation rule but omits the literal child entropies

| Field | Value |
|---|---|
| **Raised by** | Claude Fable, independent mechanism review |
| **Recorded** | 2026-09-09, at the X01 pre-execution gate |
| **Class** | **CLERICAL / DEVIATION-CLASS.** Not a methodology change, not a hypothesis change |
| **Sealed text at issue** | §6.1 *Seed protocol*: *"The three spawned entropy values are written into the sealed text at seal time and the run reproduces bit-for-bit."* |
| **The discrepancy** | The sealed bytes **do not contain** the three literal spawned values. The sentence describes an act that did not happen at seal time. |
| **Scientific effect** | **NONE.** The protocol is already fully deterministic from what *is* sealed: master seed **7** (`config.py RANDOM_SEED`), derivation **`numpy.random.SeedSequence(7).spawn(3)`**, and the **fixed arm order `[primary, S1, S2]`**. Any implementer re-derives the same three streams from the sealed rule alone; this was verified on a synthetic run — two independent `spawn(3)` calls return identical `spawn_key`s and identical generated states. |
| **What is NOT being done** | The sealed preregistration is **not edited** — doing so to insert the literals would move the HEAD blob and trigger `SEAL_MISMATCH` for a clerical omission. **A2 is not recertified.** No scientific design choice is changed. No threshold, estimand, sample, boundary or inference element moves. |
| **Resolution** | The three child streams are **derived mechanically from the sealed rule** and **recorded in the execution manifest BEFORE any target output is read**. |
| **Stream identity — a correction to the obvious representation** | The sealed sentence says "entropy values", and recording `.entropy` would have been the natural reading. **It would also have been useless as an identifier: all three children of `SeedSequence(7)` report `entropy == 7`.** Verified: `{k.entropy for k in SeedSequence(7).spawn(3)} == {7}`. What distinguishes them is the deterministic **`spawn_key`** — `(0,)`, `(1,)`, `(2,)` — together with the state each child generates. The manifest therefore records, per arm in the sealed order, the `spawn_key` and a 4×uint32 `state_fingerprint`, and states explicitly that `.entropy` is **not** an identifier. **No statistical protocol changes**: this is a precise operational representation of the already-sealed `SeedSequence(7).spawn(3)`. |
| **Exposure at the time of recording** | **No X01 target outcome had been accessed.** `E`, `F`, `A1`, `S1` and `S2` did not exist; no Sharpe, `ΔS`, bootstrap or crisis statistic had been computed. `TARGET_X01_OUTCOME_ACCESSED = NO`. |
| **Label (operating mode §5)** | `CLERICAL` — seal unchanged, preregistration unamended, prior evidence unaffected (there is none), lineage unchanged. |

**Why this is recorded rather than fixed.** The honest options were to edit the
sealed text (breaking the seal over a clerical omission) or to record the
omission and bind the obligation elsewhere. The second preserves the seal's
meaning: the seal guarantees the *scientific* contract has not moved, and it has
not. What the sealed sentence promised — bit-for-bit reproducibility from a
recorded seed — is delivered by the manifest, before any outcome is visible.

---

## D-X01-2 — *(none)*

No further deviation has been recorded. **No target execution has occurred**, so
no execution-time deviation can yet exist.
