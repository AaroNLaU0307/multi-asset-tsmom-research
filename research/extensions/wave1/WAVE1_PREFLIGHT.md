# WAVE1_PREFLIGHT.md — TSMOM-EXT-001

**Created:** 2026-09-07 (Wave-1 execution under Aaron's
`AUTHORIZE_WAVE_1_RESEARCH_EXECUTION_WITH_GATES`)
**Purpose:** establish the legal execution state before any candidate
computation (Wave-1 prompt §2), and record the governance transition Wave 1
requires.

---

## §1 Authoritative input check — PASS

| Artifact | Expected | Result |
|---|---|---|
| `TSMOM_EXTENSION_RESEARCH_MAP_v2.md` | `e9555a02…6a87dbace` | **MATCH** |
| `TSMOM_EXTENSION_RESEARCH_PROGRAM_v2.md` | `e9555f56…14264d46c2` | **MATCH** |
| `idea_registry/IDEA_REGISTRY_v2.csv` | `7e3024ed…7108717c` | **MATCH** |
| `DASHBOARD_v2.md` | `951801bc…41cb5e19b7` | **MATCH** |
| `research/extensions/validate_wave0.py` | `08d95cc5…c45a15e97a` | **MATCH** |
| Wave-0 validator run | — | **124 checks, 0 failed**, `CANONICAL_PARSER_CROSS_CHECK = ACTIVE` |
| `qros check` | — | **exit 0**, "no rejection" |
| Baseline HEAD | `c63114a0…` | **MATCH**, branch `main` |

Wave 0 is **CLOSED and not reopened**. No Wave-0 finding was re-audited.

---

## §2 Pre-transition runtime state

```
LANE=EXPLORATORY  STAGE=A   measurement_materiality=UNKNOWN
OUTCOME_EXPOSURE=TARGET_METRIC  scope=HISTORICAL_CUMULATIVE  EXPOSURE_CONFLICT=NO
A → C ELIGIBLE · C → D ELIGIBLE · D → E ELIGIBLE · E → F ELIGIBLE · F → L HOLD
```

---

## §3 The `F → L` HOLD — assessed, not ignored

Wave-1 prompt §2 requires this HOLD be addressed rather than waved past because
Aaron authorised Wave 1.

**What the HOLD is.** `TBL-PRECONDITIONS.R06`: `measurement_materiality` is
`UNKNOWN`, so "nothing may be recorded as evidence on an unresolved
classification" (L6 §2.8, §10.4). It holds exactly one edge: `F → L`.

**What `L` is.** The KB-record stage — writing a finding into
`quant-research-knowledge-base`. It is the only thing the HOLD prevents.

**Why it does not block any Wave-1 activity authorised in this turn.** Every
authorised item is `C` (build), `D` (mechanical verify), `E` (evidence) or `F`
(internal analysis) work. **No KB card is written in this turn**, and Program v2
§2 defers KB cards explicitly (decision **D6**: "created when a candidate enters
material research requiring them"). The HOLD is therefore correct, expected, and
non-blocking — and it will become blocking the moment a Wave-1 finding is to be
recorded to the KB, which is the right place for it to bite.

**Why `measurement_materiality` stays `UNKNOWN`.** The `[TBL-MATERIALITY]`
`UNKNOWN` row covers two distinct situations: "not yet classified, **or the
representation question (§10.4) is unresolved**". **§10.4 is itself recorded as
BLOCKING and unresolved** in the L6 spec — how materiality should be represented
canonically is Aaron's decision and has not been taken. `UNKNOWN` is therefore
the *correct* value on canonical grounds independent of any per-activity
judgement, and Wave-1 prompt §2's instruction to "preserve UNKNOWN if
authoritative facts remain unresolved" applies directly.

**Per-activity materiality assessment, recorded as required.** This is the
working session's assessment of each Wave-1 item, recorded so a later gate has
something to check. It is **not** a declaration and it does not change the field.

| Wave-1 item | Assessed materiality | Basis |
|---|---|---|
| Preflight, governance transition | `ORDINARY` | system/state facts under deterministic validation |
| Databento input verification | `ORDINARY` | data facts under deterministic validation; no research evidence |
| X07 / X45 / X46 diagnostics | **`MATERIAL` if ever recorded as evidence** | they produce statistics that calibrate design priors; as *internal analysis* they are not recorded as evidence in this turn |
| X02a mechanical truth | **`MATERIAL` if ever recorded as evidence** | Program v2 §10 permits `implementation_fact` + `confirmed`, which is a KB evidence record |
| X03 structural | `ORDINARY` → **`MATERIAL` if it becomes a preregistration DoF** | a declared degree of freedom shapes a sealed contract |

**Consequence recorded for the next gate:** before **any** Wave-1 finding is
written to the KB (`F → L`), `measurement_materiality` must be declared, and on
the assessment above the honest declaration for X02a and the diagnostics is
`MATERIAL` — which under `[TBL-MATERIALITY]` triggers the §7 conditional
independent-review requirement, not merely a field change. **That is a future
gate, not something this turn may pre-empt.**

---

## §4 The lane and stage transition

**Why a transition is needed.** QROS §1 fixes lane semantics as *which claims the
work may emit*. `EXPLORATORY` emits hypotheses and leads; **`MEASUREMENT` emits
implementation facts, structural findings and premise results**. Every Wave-1
item authorised here is labelled `Lane: MEASUREMENT` in MAP_v2 (X07, X45, X46,
X02a, X03-structural, X05). Emitting them on the `EXPLORATORY` lane would emit
claims the declared lane does not license.

**Authority.** Lane declaration sits in L6 §4.1's Authority row — it is **Aaron's
act, never a session's inference**. Aaron's Wave-1 routing header declares
`LANE = MEASUREMENT`, and his permit list authorises "governance state
transitions that are canonically required and legally supported". This records
his declaration; if he intends otherwise he corrects the field.

**The order is load-bearing, and was verified against the runtime before use.**

| Combination tested | Runtime verdict |
|---|---|
| `EXPLORATORY` + `A` (before) | `A → C ELIGIBLE` |
| `EXPLORATORY` + `C` | `C → D ELIGIBLE` |
| **`MEASUREMENT` + `C`** (after) | **`C → D ELIGIBLE`** |
| `MEASUREMENT` + `A` | **"no transition leaves stage A in the MEASUREMENT chain"** — a dead end |

The MEASUREMENT chain is `C → D → E → F → L` and **contains no stage `A`**.
Declaring the lane while still at `A` would have stranded the project at a stage
its own chain does not contain. The legal order is therefore:

1. **`A → C` on the EXPLORATORY chain** — a real edge, reported `ELIGIBLE`.
2. **Then declare `lane: MEASUREMENT` at stage `C`** — a stage the MEASUREMENT
   chain contains.

Both were verified with a throwaway state file inside the repository (deleted
immediately); neither was inferred.

**Why stage `C`.** `C` is "build" — the stage currently due or in progress. Wave 1
builds the futures input path and runs mechanical verification on it. `C` is the
MEASUREMENT chain's entry stage and the honest description of where the project
is; nothing in this turn reaches `L`.

**Not recorded in `ops_events[]`.** `[TBL-OPS-EVENT-TYPES]` is closed and
contains no stage- or lane-transition type. No type was invented; the transition
is recorded here and in `session_log[]`, whose fields are free-valued — the same
discipline Wave 0 applied to Aaron's authorisation.

---

## §5 Post-transition runtime state

```
LANE=MEASUREMENT  STAGE=C   measurement_materiality=UNKNOWN
OUTCOME_EXPOSURE=TARGET_METRIC  scope=HISTORICAL_CUMULATIVE  EXPOSURE_CONFLICT=NO
C → D ELIGIBLE · D → E ELIGIBLE · E → F ELIGIBLE · F → L HOLD (expected)
```

---

## §6 Shared Databento accounting — pre-execution gate (prompt §3)

**Does this turn require a new governed Databento trial contribution?** **No.**

| Activity | Constructs a strategy-return series? | `N_trials` contribution |
|---|---|---|
| Databento input verification | No — metadata and ranges only | **0** |
| Settlement / OI extraction | No — raw vendor inputs only | **0** |
| X02a mechanical identities | No — residuals, not return series | **0** |
| X03 structural roll diagnostics | No — roll dates, counts, OI crossover timing | **0** |

This is the `c1-drag-audit` precedent exactly: a measurement pass that computes
no Sharpe, no CI and no return series does not extend the ledger, and extending
it would misstate what DSR corrects for. **The §3 gate is therefore not tripped
by this turn, and no append destination is needed yet.**

**It will be tripped by X01**, whose first constructed futures strategy-return
series is a real contribution under the carry convention. That is why the owner
decision below is raised now rather than at the moment of need.

**Inspection performed (prompt §3 steps 1–4).**

1. **Existing structure.** The authoritative dataset-level record for this panel
   already exists and is frozen: `commodity-carry-research/preregistration/PREREGISTRATION.md`
   §10 with its code anchor `src/config.py:66`, `N_trials = 14`.
2. **Existing legal append destination.** There is **no** shared physical file
   above the projects. Authority is distributed: the carry preregistration holds
   the count; `c1-drag-audit/SAMPLE_REUSE.md`, `mean-reversion-research/protocol/SAMPLE_REUSE.md`
   and this program's `TRIAL_LEDGER.md` §3.1 are *views* that reference it.
3. **Responsible owner.** Undetermined. The carry study's preregistration is
   frozen and its §11 deviation process is the only mechanism that changes its
   count — but that process belongs to the carry study, and TSMOM-EXT is not its
   owner.
4. **Can all projects reference one cumulative history?** **Today, only by
   convention, not by construction.** Each project points at the carry
   preregistration; nothing mechanically prevents divergence.

**`OWNER_DECISION_REQUIRED_SHARED_DATABENTO_HOME`** — see §7.

---

## §7 Owner decisions required

### 7.1 `OWNER_DECISION_REQUIRED_SHARED_DATABENTO_HOME`

**Needed before:** the first X01 constructed futures strategy-return series.
**Not blocking:** anything in this turn.

**Recommended location and mechanism — one recommendation, as asked:**

> **Create `quant-research-knowledge-base/registry/sample-trial-ledger.csv`,
> curated by the KB curator seat, as the single authoritative append destination
> for per-sample cumulative trial history; keep the carry preregistration's
> `N_trials = 14` as its frozen opening row for
> `dataset.databento.commodity-futures-curves`.**

**Why there, and not elsewhere.**

- The KB **already owns dataset-level facts** across projects — `relationships.csv`
  carries `must_not_be_retested_on_same_sample` for exactly these panels, and
  `generated/open-research-gaps.md` already aggregates "samples already searched".
  A trial ledger is the same *kind* of fact, so it belongs to the same owner.
- The KB has a **curator seat and a validator** (`validate.py`), so appends are
  reviewable by an existing mechanism rather than a new one.
- It is **outside every consuming project**, so no consumer owns the record that
  governs its peers — which is the "competing total" failure Program v2 §0B
  forbids and the reason Wave 0 declined to create this file inside
  `multi-asset-tsmom-research`.
- It **preserves the frozen carry count** as an opening row rather than
  recomputing it, satisfying "never silently recompute historical frozen trial
  counts".

**What this session did NOT do:** create that file, write to the KB, or alter any
project's `SAMPLE_REUSE.md`. Establishing it is Aaron's decision and, once taken,
a KB-curator task — not a TSMOM-EXT builder task.

### 7.2 `D3` — deployment NAV bracket

**Status: OPEN.** Verified against local bytes: `WAVE0_VERIFICATION_RECORD.md`
`U10` records D3 as open, and no authoritative artifact resolves it. The bracket
`{$100k, $250k, $500k, $1M}` remains an **existing proposal, not an adopted
decision**, and this session does not adopt it.

**Consequence:** `X05_STATUS = BLOCKED_PENDING_D3_OWNER_DECISION`. X05 is the
only Wave-1 item this blocks; all other Wave-1 work proceeds independently.

---

## §8 Lockbox status — unchanged

| State | Status this turn |
|---|---|
| Frozen historical working snapshot | ETF `2026-06-12` (sha `3d2a7a56…`); Databento `2026-06-30` — **both confirmed, neither refreshed** |
| Accrued but protected holdout | **Not opened.** Protection remains unverified (Wave-0 `U1`), so it is not usable as T3. |
| Prospective forward accrual | **Does not exist.** No seal, so no T4 clock has started. |

The partial June-2026 ETF month (label `2026-06-30`, data to `2026-06-12`) is
carried per `LOCKBOX_PROCEDURE.md` §2.1 and flagged in `EDGE_DIAGNOSTICS.md`.

`PROTECTED_FORWARD_DATA_OPENED = NO` · `NEW_DATA_PURCHASED = NO`

---

## §9 Append log

| Date (UTC) | Appended | By |
|---|---|---|
| 2026-09-07 | Created at Wave-1 preflight. Input check §1; HOLD assessment §3; lane/stage transition with runtime verification §4; shared-Databento gate §6; owner decisions §7; lockbox §8. | Wave-1 session (Claude Opus 5) |
