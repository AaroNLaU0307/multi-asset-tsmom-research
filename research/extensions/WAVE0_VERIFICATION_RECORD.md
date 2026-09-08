# WAVE0_VERIFICATION_RECORD.md — TSMOM-EXT-001

**Program:** TSMOM extension (`TSMOM-EXT-001`)
**Created:** 2026-09-07 (Wave 0 governance execution, authorised by Aaron)
**Implements:** `TSMOM_EXTENSION_RESEARCH_PROGRAM_v2.md` §2, row "Canonical
verification tasks" — *"Confirm from bytes the facts listed in §12 as
`UNKNOWN_PENDING_WAVE0_VERIFICATION`; record them as verified or leave them
`UNKNOWN`. Unverified facts block any dependent research gate."*

Every row below was read from local bytes by this session on **2026-09-07 (UTC)**.
Nothing was inferred, and nothing was carried over from the architecture's own
assertions without re-reading the source.

---

## §1 Authoritative V2 architecture — hash check

| Artifact | Expected SHA-256 (Aaron's authorisation) | Recomputed | Result |
|---|---|---|---|
| `research/extensions/TSMOM_EXTENSION_RESEARCH_MAP_v2.md` | `e9555a0220b58fdf6dfaee40613c5b28b114ea02b2a94137b1a23c56a87dbace` | identical | **MATCH** |
| `research/extensions/TSMOM_EXTENSION_RESEARCH_PROGRAM_v2.md` | `e9555f561e302c4f937a05829bd23b2368c79765b4c275b788f8fe14264d46c2` | identical | **MATCH** |
| `research/extensions/idea_registry/IDEA_REGISTRY_v2.csv` | `7e3024edd1e553745c75f83f3f107df84d2814ae06be4876f53aae117108717c` | identical | **MATCH** |
| `research/extensions/DASHBOARD_v2.md` | `951801bcea0281811b501ca19f63b26a3f3e488ef7cd4ca28a1f6641bf5e19b7` | identical | **MATCH** |
| `research/extensions/review_history/ASTRA_ROUND2_CONVERGENCE_2026-09-08.md` (Round-2 provenance) | `0a89d43919813eee302863eb642571347370e374c7966c9a81303dc9e0579869` | identical | **MATCH** |

**No V2 architecture byte was modified in Wave 0.** These five files are
unchanged; the hashes above were recomputed again after the Wave-0 artifacts were
written, and still match.

**Baseline reference:** `multi-asset-tsmom-research` HEAD
`c63114a06275c782b5835f219b14c17f1b33cd80` on branch `main` — matches the
architecture's declared frozen baseline `c63114a`. **VERIFIED.**

---

## §2 Program v2 §12 items marked `UNKNOWN_PENDING_WAVE0_VERIFICATION`

### §2.1 ETF cache — **VERIFIED**

| Fact | §12 status before | Verified value | Source (read 2026-09-07) |
|---|---|---|---|
| ETF cache **last date** | `UNKNOWN_PENDING_WAVE0_VERIFICATION` (observed 2026-06-12 in orientation) | **`2026-06-12`** | `data/close_prices_raw.csv`, final `Date` value |
| ETF cache **snapshot hash** | `UNKNOWN_PENDING_WAVE0_VERIFICATION` | **`3d2a7a56dbd92d4ff8138cfd894c87f5ac5ac088a11165db870673e0c05c3c31`** | SHA-256 of `data/close_prices_raw.csv` |
| First date | not listed | `1993-01-29` | same file |
| Shape | not listed | 3,298,252 bytes; 8,400 data rows + 1 header; 30 tickers | same file; `data/fetch_metadata.csv` (30 rows, all `ok=True`) |
| **Partial-month construction of the last monthly row** | `UNKNOWN_PENDING_WAVE0_VERIFICATION` | **VERIFIED, and it IS partial.** `src/signals.py::to_monthly` = `daily_prices.resample(rule).last()`; `config.py:154` `SIGNAL_RESAMPLE = "ME"` (month-END). The convention labels the monthly value at the **calendar month-end**. The cache ends `2026-06-12`, so the terminal monthly row is **labelled `2026-06-30` while covering only 2026-06-01 → 2026-06-12**. | `src/signals.py` lines 40–48 (docstring + body); `config.py:154` |

**Consequence, recorded so a later gate can use it:** any evaluation touching the
terminal monthly row must truncate it, or declare in its preregistration that a
partial terminal month is included and why. A partial row must never be compared
against full months as though it were one. Carried into
`LOCKBOX_PROCEDURE.md` §2.1.

### §2.2 Databento panel — **VERIFIED**

| Fact | §12 status before | Verified value | Source (read 2026-09-07) |
|---|---|---|---|
| Databento **last date** | `UNKNOWN_PENDING_WAVE0_VERIFICATION` (2026-06-30 per manifest as reported) | **`2026-06-30` inclusive** (request range `2010-06-06` inclusive → `2026-07-01` exclusive) | `commodity-carry-research/data/MANIFEST.md`, "Request parameters (locked, PREREGISTRATION.md Sec 2)" |
| Databento **snapshot hash** | `UNKNOWN_PENDING_WAVE0_VERIFICATION` | `ohlcv-1d.dbn.zst` **`333095164e55c73a150949b654a0e4c9f15636cc01ee7c93bf625e5412c59539`** (107,229,003 bytes); `definition` aggregate **`76da3a39a7279ef3a3b4c03ffb2646048685f715466108ca5136aee6f7922277`** (5,031 files); `statistics` aggregate **`ee7dee4dc1c2dab44df207d20d5327b0dfb7e6193c49091b8e0a52bfb489001f`** (5,026 files) | same manifest |
| Corpus presence | — | `C:\Users\Aaron\quant-data\commodity-carry` present; `ohlcv-1d.dbn.zst` present at the manifest's stated size | directory listing |
| Total | — | 3 schemas, 10,058 files, 9,427,421,483 bytes | manifest |

**Scope limit, stated:** per-file SHA-256 re-verification of the 10,058 delivered
files was **not** run — the manifest's aggregate hashes are the recorded record,
reproducible from `DATA_DIR` at any time. This is a **recorded scope limit, not a
verification failure**; it is owed before the first computation on this panel.

### §2.3 Post-boundary exposure status — **REMAINS `UNKNOWN`**

| Fact | Status | Why it stays UNKNOWN |
|---|---|---|
| Exposure status of any data after the frozen snapshot boundaries (related-project access; outcome-informed market knowledge) | **`UNKNOWN_PENDING_AUTHORITATIVE_VERIFICATION`** | Nothing in this repository can establish it. "Not downloaded by this program" is explicitly insufficient (Program v2 §0A, T3 row). Establishing it requires a cross-project account of what other programs on this machine have evaluated over the same period on overlapping instruments — a future authorised task, partly addressed by `DATA_INVENTORY_SPEC.md` §2.3. |

**Consequence, enforced:** accrued post-boundary history **may not** be claimed as
T3 held-out evidence, and is **not** T4. Recorded in `LOCKBOX_PROCEDURE.md` §5
and `SAMPLE_REUSE.md` KB-5.

### §2.4 Financial-futures ownership — **REMAINS NOT ESTABLISHED**

| Fact | Status |
|---|---|
| Financial futures (ES/NQ, ZT/ZF/ZN/ZB/UB, 6E/6J/6B/6A/6C/6S/6N, NKD) | **`not established as owned; inventory pending`** — unchanged. **No inventory was run** (Wave 0 defines the task only; `DATA_INVENTORY_SPEC.md`). **This is deliberately not phrased as "not acquired"**, which would assert an unverified fact. |

### §2.5 Reviewer-artifact hashes

| Fact | Status |
|---|---|
| Astra Round-2 artifact hash | **`0a89d439…579869` — MATCH** (§1). Declared authoritative by Aaron 2026-09-08; recomputed here and matched. |
| Fable Round-1 response hash | **not known to this session; not asserted.** Pinned by Aaron outside this repository. Unchanged from §12. |
| Fresh-Astra V2 document verification; N1–N8 corrections; delta verification; N7 closure | **`UNKNOWN_PENDING_AUTHORITATIVE_VERIFICATION`** — known only from Aaron's chat-carried authorisation; **no artifact is persisted in this repository**. Recorded as gap **G-1** in `ops/REVIEWER_EXPOSURE_LOG.md` §5. Disclosed; not treated as a Wave-0 blocker (Wave 0 changes no architecture bytes and Aaron's acceptance is an owner adjudication). It **would** block any later gate that needed to cite those verifications as evidence. |

---

## §3 Canonical vocabulary and gate verification — **all VERIFIED from bytes**

Program v2 §10 asserts these; this session re-read every one of them rather than
transcribing.

| Item | Verified content | Source, read 2026-09-07 |
|---|---|---|
| Legal `research_status` (strategy) | `confirmed, supported, not_promoted, falsified, active, archived, experimental, unresolved` | `quant-research-knowledge-base/schemas/strategy.schema.yaml` line 29 — **MATCH** |
| Legal `claim_status` (finding) | `confirmed, supported, partially_supported, unresolved, contradicted, retired, not_promoted` — **no `falsified` at Finding level** | `schemas/finding.schema.yaml` line 29 — **MATCH** |
| Legal `evidence_type` | `preregistered_primary, preregistered_robustness, preregistered_premise_test, out_of_sample, full_sample_fixed_parameter, lockbox, post_hoc_diagnostic, exploratory, implementation_fact, external_literature, researcher_interpretation` | `schemas/finding.schema.yaml` lines 30–43 — **MATCH** |
| **Gate G4 disallowed set** | `post_hoc_diagnostic, exploratory, researcher_interpretation, full_sample_fixed_parameter, external_literature` can never carry `claim_status: confirmed`. **`implementation_fact` is NOT in the disallowed set** | `src/quant_kb/validate.py::check_no_confirmed_post_hoc` lines 116–133; `README.md` lines 96–100 — **MATCH** |
| Definition of `implementation_fact` | *"A fact about the code/system itself, not an empirical result."* | `README.md` line 92 — **MATCH** |
| Decisiveness convention | `falsified` only via multiple independent decisive tests with nothing material untried; `not_promoted` for single/simpler gate failures, premise failures, or an untested sub-space; **prefer `not_promoted` when in doubt**; a convention, **not enforced by `validate.py`** | `README.md` lines 133–152 — **MATCH** |
| **No `insufficient_evidence` value exists** | Confirmed by the two enums above; `unresolved` is the correct value | as above — **MATCH** |
| Session-role independence | *"no session both produces a thing and judges it"*; a subagent is not independent of its spawner; changing model is not enough | `docs/session-conventions.md` §1 — **MATCH** |
| HALT output must be a named file | A next stage must verify the file is present and never accept a chat summary in its place | `docs/session-conventions.md` §4 — **MATCH** (this is the basis of gap G-1) |

---

## §4 Sample facts — **VERIFIED from bytes**

| Fact | Verified | Source |
|---|---|---|
| ETF panel **burned 6 of 6** | **YES** — 6 rows, each `must_not_be_retested_on_same_sample → dataset.yfinance.multi-asset-etf-panel`: `strat.tsmom.multi-asset-core`, `strat.tsmom.crash-defense-overlay`, `strat.tsmom.vol-breakout-overlay`, `strat.tsmom.seasonality-overlay`, `strat.tsmom.yield-spread-overlay`, `strat.xsmom.multi-asset` | `quant-research-knowledge-base/relationships/relationships.csv` **lines 16–21** — **MATCH** |
| Databento **`N_trials = 14`, frozen** | **YES** — "primary = 1 + 1 = 2. Robustness = ... = 12. Total N_trials = 2 + 12 = 14" | `commodity-carry-research/preregistration/PREREGISTRATION.md` §10 line 205 — **MATCH** |
| The counting convention | **YES** — one trial per distinct constructed strategy-return series; items 8–9 excluded as diagnostics; a deviation that adds/removes a series changes `N_trials` and forces DSR recomputation | PREREG §10 lines 205–207; `commodity-carry-research/src/config.py:62-66` (`N_TRIALS = 14`, with the comment "2 primary + 12 robustness arms, items 8-9 excluded as diagnostics") — **MATCH** |
| ETF panel has **no frozen trial-count convention** | **YES, by absence** — the core had no preregistration and no frozen computation ledger exists for this panel. Recorded as the open decision `D-ETF-COUNT` (`TRIAL_LEDGER.md` §4) rather than filled with a manufactured number. | absence verified across the repo and the KB |

---

## §5 Runtime facts — **VERIFIED from bytes**

| Fact | Verified value | Source |
|---|---|---|
| `qros-state.yaml` schema version | **`17`** | `qros-runtime/qros_runtime/statefile.py:49` `SCHEMA_VERSION = "17"` |
| Top-level required fields | `schema_version, research_id, lane, workflow_stage` | `statefile.py:168`, `:227` |
| `lane` enum | `EXPLORATORY \| MEASUREMENT \| FULL` — closed at three | `L6_RUNTIME_SPEC.md` `[TBL-LANE-CHAINS]`; QROS §1 |
| EXPLORATORY chain | `A(light) → C → D → E → F → L` | `L6_RUNTIME_SPEC.md` §2.5 `[TBL-LANE-CHAINS]` |
| **No `A → B` edge in any lane** | Confirmed in the spec text and asserted by a conformance check | `L6_RUNTIME_SPEC.md` §2.5 |
| `measurement_materiality` enum | `ORDINARY \| MATERIAL \| UNKNOWN \| N_A` | `L6_RUNTIME_SPEC.md` `[TBL-MATERIALITY]` |
| `outcome_exposure.scope` enum | `HISTORICAL_CUMULATIVE \| CURRENT_REVIEW_SCOPE` | `[TBL-EXPOSURE-SCOPES]` |
| Exposure classes | `NO_OUTCOME \| GENERATED_NOT_SEEN \| REVEALED_AGGREGATE \| REVEALED_TARGET_METRIC`, contributing `NONE / NONE / AGGREGATE / TARGET_METRIC`; max on `NONE < AGGREGATE < TARGET_METRIC` | `[TBL-EXPOSURE-CLASSES]`, §3.4C |
| No ledger ⇒ `UNKNOWN` never `NONE` | Confirmed | `L6_RUNTIME_SPEC.md` §3.4C; ratification §10.1 |
| `inputs[]` required fields | `id, path, observed_revision, observed_sha256`; `WORKTREE` is the uncommitted-basis sentinel | `statefile.py:259-264`; `freshness.py:52` |
| `qros` CLI operational | `qros.py` runs; subcommands `status, check, next, packet, prompt` | `qros-runtime/qros.py --help` |

---

## §6 Facts left `UNKNOWN` after Wave 0 — the complete list

Each carries **what would discharge it**, so a later session knows what to check.

| # | Fact | Status | Discharged by |
|---|---|---|---|
| U1 | Exposure status of any data after the frozen snapshot boundaries | `UNKNOWN_PENDING_AUTHORITATIVE_VERIFICATION` | A cross-project account of what other programs on this machine have evaluated over the same period on overlapping instruments, plus a statement on outcome-informed market knowledge for the claim family in question |
| U2 | Financial-futures ownership | `not established as owned; inventory pending` | Executing `DATA_INVENTORY_SPEC.md` under a separate authorisation |
| U3 | Pre-2008 futures-history ownership | `not established as owned; inventory pending` | Same |
| U4 | ETF-panel historical trial count and the 45-cell grid's counting treatment | `UNKNOWN_PENDING_AARON_DECISION` (`D-ETF-COUNT`) | Aaron choosing among `TRIAL_LEDGER.md` §4's options A/B/C |
| U5 | Whether a sealed same-period wrapper comparison (X01) may be classified above `supported` | `CANONICAL_CLASSIFICATION_PENDING_VERIFICATION` (**D9**) | Aaron and the KB curator |
| U6 | Fable Round-1 response hash | not known to this session; not asserted | Aaron supplying the pinned bytes |
| U7 | Fresh-Astra V2 verification, N1–N8 corrections, delta verification, N7 closure | `UNKNOWN_PENDING_AUTHORITATIVE_VERIFICATION` (gap **G-1**) | Persisting those artifacts verbatim in `research/extensions/review_history/` with recorded SHA-256, as was done for Round 2 |
| U8 | Per-file SHA-256 of the 10,058 Databento files | not re-verified in Wave 0 (recorded scope limit) | Re-running the per-file hash from `DATA_DIR`; owed before the first computation on that panel |
| U9 | Physical home and curator of a workspace-level shared dataset ledger | `UNKNOWN_PENDING_AARON_DECISION` | Aaron; the distributed form in `TRIAL_LEDGER.md` §5.1 governs until then |
| U10 | Deployment NAV bracket for X05/X32 | **D3**, open; default grid {$100k, $250k, $500k, $1M} | Aaron |
| U11 | Whether the fresh-Astra V2 verification seat (S3) is genuinely distinct from the Round-1/Round-2 seat | `UNKNOWN_PENDING_AUTHORITATIVE_VERIFICATION` (gap **G-5**, added at the B2 repair) | Persisting the S3/S4 artifacts (U7 / gap G-1) and reading their own session self-descriptions, as was done for Round 2. **Why this is now open:** Round 2 was recorded as a fresh session on the architecture's framing; the pinned artifact says verbatim it was a *continuation*. The framing that described Round 2 as fresh also describes S3 as fresh, so "fresh" can no longer be inferred from it for any seat. Consequence: Program v2 §1's requirement that the Stage I session never be the A2 session is **asserted and unverified** for the seats used so far. No Wave-0 artifact depends on it; a future gate citing Stage I independence does. |

**None of U1–U11 blocks Wave 0.** U1, U2, U3, U8 block specific *future* gates
(protected-holdout claims; D1/D2; the first Databento computation). U4 blocks any
ETF-panel DSR. U5 caps X01's classification at `supported`. U7 blocks only a gate
that would need to cite those verifications as evidence.

---

## §7 Append log

| Date (UTC) | Appended | By |
|---|---|---|
| 2026-09-07 | Record created at Wave-0 execution. V2 hash check §1 (all MATCH); §12 verification items §2 (ETF and Databento snapshots VERIFIED; post-boundary exposure and futures ownership remain UNKNOWN); canonical vocabulary and G4 re-verified §3; sample facts §4; runtime facts §5; the complete `UNKNOWN` list §6. | Wave-0 governance session (Claude Opus 5), under Aaron's `AUTHORIZE_WAVE_0_GOVERNANCE_EXECUTION` |
| 2026-09-07 | **Bounded repair pass.** `U11` appended to §6 after the **B2** provenance erratum established that Astra Round 2 was a CONTINUATION, not a fresh session — which reopens whether the S3 verification seat is distinct (gap **G-5**). §6's completeness claim updated to U1–U11. **No previously verified fact was changed, no `UNKNOWN` was discharged, and §1–§5 are untouched.** | Wave-0 bounded repair session (Claude Opus 5), under Aaron's bounded-repair authorization |
