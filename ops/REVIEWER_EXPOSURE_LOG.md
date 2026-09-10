# TSMOM-EXT-001 — REVIEWER EXPOSURE LOG (seat axis)

```
RECORD_TYPE=REVIEWER_EXPOSURE_LOG
AXIS=SEAT
CREATED=2026-09-07
APPEND_ONLY=YES — rows are only appended, never edited, never reordered
AUTHORITY=this file records SEAT exposure, not research exposure accounting
```

Per the ratified L6 owner decision §10.1
(`Quant trade/L6_RATIFICATION_AND_OWNER_DECISIONS_2026-08-21.md`, SHA-256
`5E465D14B4A0F83BF7856A1875E7E502F3D76AA17AAD284B55CA221000423ACF`) and
`~/.claude/CLAUDE.md`'s L6 Runtime clause 5: exposure has **two axes that are
never merged**. This is the seat axis.

---

## §1 Why this is a separate file from `ops/EXPOSURE_LEDGER.md`

**Burning a reviewer seat consumes no research degrees of freedom.** A seat
event says *this session may no longer hold a particular outcome-blind role*. It
does not say *a researcher acquired information about a target statistic on a
sample*. Recording the two on one axis would invent research exposure that never
happened, and would move `N_trials` accounting that must not move.

`ops/EXPOSURE_LEDGER.md` §5 cross-references the rows below **as pointers with
no classification and no scope**, so nothing here can be picked up by that
ledger's normalization.

**The L6 requirement "no ledger ⇒ that axis is `UNKNOWN`, never `NONE`" is
satisfied per axis.** This file satisfies it for the seat axis of TSMOM-EXT-001.

---

## §2 What a seat row does and does not establish

- **Reviewer independence is a session property, not a statistical one.** A
  fresh reviewer session is independent *of the producing session*. It is
  **never** empirical independence, sample independence, statistical
  replication, or a second draw of data. Model diversity is review diversity
  only (`quant-research-knowledge-base/docs/session-conventions.md` §1, verified).
- A seat row therefore **never** licenses a stronger evidence context (T0–T4),
  never adds a trial, and never converts dependent evidence into independent
  evidence.
- **Classification of a seat's own exposure is the seat's self-report where it
  gave one.** A builder does not downgrade another seat's self-assessment.
- **Three sources of a field's value, kept distinct** — this distinction was
  added at the B2 repair, because collapsing the first two is what produced that
  defect:
  1. **Seat self-report in a persisted artifact.** The strongest source short of
     direct observation. It is what the seat itself wrote, in bytes on disk, at
     a recorded hash. **It must be read before a field is filled from anything
     weaker** — see erratum S7, where a persisted self-description of session
     character sat unread on disk while the field was filled from source 3.
  2. **Derivation from what a read artifact demonstrably contains.** Legitimate
     and used here for every Astra `classification` value: an artifact that
     restates published target-metric figures exposes whoever read it,
     regardless of whether that seat ever classified itself. Derivation is
     labelled as derivation in the row.
  3. **A third party's framing** — the architecture's or Aaron's narrative
     description of a seat. It is the weakest source, it is **not** the seat's
     own account, and a field filled from it must say so and must yield to
     sources 1 and 2 the moment either is available.
- Where **none** of the three is available, the field is `UNKNOWN`, not an
  inferred value.

---

## §2A Errata index — read before the log

The log below is **append-only**: a row that was wrong is **never edited**, and
a correction is a **new row that cites the row it corrects**. A reader who takes
a superseded row at face value would be misled, so every superseded field is
indexed here.

| superseded row | field | as originally written | corrected by | corrected reading |
|---|---|---|---|---|
| **S2** | `window` | `fresh session (asserted by the architecture)` | **S7** | **CONTINUATION** of the Astra design-review session that produced Round 1. Round 2 was **not** a fresh independent reviewer session. |
| **S11** | `ts` | `2026-09-08T02:05Z–03:35Z` "claimed a bounded **observed** interval" | **S12** | The row was written at **02:21:46Z**, so 03:35Z was **71 minutes in the future**. Observed phase span: 02:15:45Z–02:24:51Z; start UNKNOWN, bounded above by 02:15:45Z. |
| **S9** | `ts` | `2026-09-08T01:00Z-03:00Z` | **S10** | The row was written at **00:37:44Z**, before the interval it claims. Corrected reading: the seat's repair activity ran **00:34Z – 01:13Z**. Projected, not observed. |
| **S14** | `ts` | `2026-09-08T03:05Z–03:25Z` "bounded by observed artifact mtimes" | **S15** | The row was written at **03:05:06.515Z**, so 03:25Z was **about 20 minutes in the future**; and the claimed 03:05Z start **postdates** the phase's earliest artifact (03:02:16.046Z). Observed phase span: **03:02:16.046Z–03:05:18.759Z**; start UNKNOWN, bounded above by 03:02:16.046Z. |

**Standing convention, adopted after the third occurrence of this defect
(S10 → S9, S12 → S11, S15 → S14).** A `ts` in this log may hold **only**:

1. a clock value **observed before the append**, recorded as a lower bound; or
2. an interval whose endpoints are **already-observed artifact mtimes**.

A projected endpoint is never written, not even one expected to be correct
within minutes. Where a start cannot be recovered it is recorded as **UNKNOWN**
with an observed upper bound, never estimated.

**Nothing else in S2 is superseded.** Its artifact pointer, its hash, its
`classification` and its "not outcome-blind" consequence all stand.

---

## §3 Log

| # | ts | seat | window | artifact_read | what_was_seen | classification | consequence | source of this row |
|---|---|---|---|---|---|---|---|---|
| S1 | UNKNOWN (no contemporaneous seat record; the round is dated 2026-09-08 local by the architecture) | GPT-6 Astra — Round 1 design challenge | fresh session (asserted by the architecture; not independently verified here) | V1 architecture `TSMOM_EXTENSION_RESEARCH_MAP.md` (SHA256 `76b902ed…d1e5`) and `TSMOM_EXTENSION_RESEARCH_PROGRAM.md` (SHA256 `7495faa9…040b`) | The v1 documents, which restate published TSMOM target-metric figures (core Sharpe, sleeve attribution, robustness grid, cost sweep) | `REVEALED_TARGET_METRIC` — **derived from the artifact's contents, not from a seat self-report**; no Astra self-classification is on file | This seat has read the program's published baseline figures and is **not** outcome-blind for TSMOM-EXT | `TSMOM_EXTENSION_RESEARCH_PROGRAM_v2.md` header ("GPT-6 Astra Round 1 — not persisted in this repository; its findings are represented through Astra Round 2's resolution table") |
| S2 | UNKNOWN (round dated 2026-09-08 local) | GPT-6 Astra — Round 2 convergence ("CONDITIONAL CONVERGENCE") | fresh session (asserted by the architecture) | The v1 architecture plus the Fable Round-1 response; persisted verbatim at `research/extensions/review_history/ASTRA_ROUND2_CONVERGENCE_2026-09-08.md`, SHA256 `0a89d43919813eee302863eb642571347370e374c7966c9a81303dc9e0579869` — `PIN_STATUS = AUTHORITATIVE_MATCHED` (declared authoritative by Aaron 2026-09-08; recomputed and matched) | Same published target-metric figures, plus the Round-1 exchange | `REVEALED_TARGET_METRIC` — derived from artifact contents; no seat self-report on file | Not outcome-blind for TSMOM-EXT. **Material design contribution**: §0A evidence-context model, output-based exposure classification (§0B), claim-specific crisis scope, redundancy-review reframing, three-state X01 contract form, X44 correction, X09 naming, X35/X36 split — adopted by the architecture author, not by Astra | `TSMOM_EXTENSION_RESEARCH_PROGRAM_v2.md` header and Provenance paragraph |
| S3 | UNKNOWN (dated 2026-09-08 local) | GPT-6 Astra — fresh document-only verification of the V2 draft | `NEW_TOP_LEVEL_SESSION` (asserted by Aaron's Wave-0 authorisation narrative; **not independently verified from bytes by this session** — no verification artifact is persisted in this repository) | `TSMOM_EXTENSION_RESEARCH_MAP_v2.md`, `TSMOM_EXTENSION_RESEARCH_PROGRAM_v2.md` (hashes in `EXPOSURE_LEDGER.md` row 9) | The V2 documents, which restate the same published target-metric figures | `REVEALED_TARGET_METRIC` — derived from artifact contents | Not outcome-blind for TSMOM-EXT | Aaron's Wave-0 authorisation message, §"The TSMOM Extension V2 architecture has completed"; **the verification artifact itself is not on disk — see §5 gap G-1** |
| S4 | UNKNOWN (dated 2026-09-08 local) | GPT-6 Astra — bounded N1–N8 corrections, delta verification, and final N7 single-cell closure | asserted continuation of the verification arc; **not independently verified from bytes** | The V2 documents and the correction deltas | Same | `REVEALED_TARGET_METRIC` — derived from artifact contents | Not outcome-blind for TSMOM-EXT | Aaron's Wave-0 authorisation message; **no persisted artifact — see §5 gap G-1** |
| S5 | 2026-09-07T17:36Z–19:58Z (approx.) | Claude Fable 5.1 — architecture **author** (v1 drafting, Round-1 rebuttal, V2 drafting) | invoked directly by Aaron; `WINDOW=NEW_TOP_LEVEL_SESSION` then `CONTINUATION` | The repository's committed reports and the knowledge base | Published full-sample core, sleeve, robustness-grid, cost-sweep and overlay results — **self-declared** in both routing headers as `OUTCOME_EXPOSED=TARGET_METRIC` | `REVEALED_TARGET_METRIC` — **seat self-report, not downgraded** | **This is a producer seat, not a reviewer seat.** Its exposure is therefore *also* researcher exposure and is carried on the research axis as `EXPOSURE_LEDGER.md` rows 8–9. It is listed here so the seat map is complete. Consequence: this seat **must not** certify its own program (`MUST_NOT_BE` in its own header, verbatim: "sole certifier of any FULL result in this program … verifier of this draft") | v1/v2 routing headers, verbatim |
| S6 | 2026-09-07T20:00Z–20:40Z | Claude Opus 5 — Wave-0 **governance builder** (this session) | `NEW_EXECUTION_SESSION` under `AARON_DECISION=AUTHORIZE_WAVE_0_GOVERNANCE_EXECUTION` | The V2 architecture; the L6 spec and ratification record; the KB schemas, `validate.py`, `README.md`, `relationships.csv`, `session-conventions.md`; the carry preregistration §10 and `src/config.py`; `c1-drag-audit/SAMPLE_REUSE.md`; `mean-reversion-research` state file, ledger and `protocol/SAMPLE_REUSE.md`; the `qros-runtime` sources; this repo's `data/` metadata and `src/signals.py` | The baseline's published headline Sharpe (read incidentally inside the Map's exposure statement); the **carry** study's registry-public DSRs and `NOT_PROMOTED` verdicts (another program's outcomes). **No TSMOM results file was opened; no strategy computation was run.** | `REVEALED_TARGET_METRIC` — **self-report, not minimised** (see `EXPOSURE_LEDGER.md` rows 10–11) | This session is a **producer** of the Wave-0 governance artifacts and therefore **must not certify them**. Any Wave-0 audit or verification requires a fresh session that did not write these files | this session |
| S7 | 2026-09-07T21:10Z (erratum appended; the event it corrects is S2) | **ERRATUM to S2** — GPT-6 Astra, Round 2 convergence | **CONTINUATION**, correcting S2's `window` field, which read "fresh session (asserted by the architecture)" | The pinned Round-2 artifact `research/extensions/review_history/ASTRA_ROUND2_CONVERGENCE_2026-09-08.md`, SHA256 `0a89d43919813eee302863eb642571347370e374c7966c9a81303dc9e0579869` — **the same bytes S2 already cited** | The artifact self-describes its session character, verbatim at its line 17: *"This is a continuation convergence review, **not fresh Stage I verification**."* Consistent with the same line's account of reviewing "Fable's complete pinned response against Round 1", which presupposes Round-1 context | unchanged from S2 — `REVEALED_TARGET_METRIC`, derived from artifact contents | **Round 2 was a CONTINUATION of the Astra design-review session, not a fresh independent reviewer session.** S1 and S2 are therefore **one reviewer seat spanning both rounds**, not two independent looks, and no independence may be claimed between them. The later fresh-Astra final verification (S3) remains a **distinct** seat *as asserted*, but that assertion is itself unverified — see gap **G-1**. Reviewer independence is in every case a session property and **never** statistical or sample independence (§2). | This bounded-repair session, reading the pinned artifact's own bytes. **The defect was mine:** S2 recorded the architecture's framing without reading the pinned artifact's self-description, which was on disk and hash-matched the whole time. Raised as blocker **B2** by the fresh GPT-6 Astra Wave-0 verifier. |
| S8 | 2026-09-07T21:40Z-23:30Z | Claude Opus 5 - Wave-1 **research builder** (continuation of the S6 seat) | `CONTINUATION` under Aaron's `AUTHORIZE_WAVE_1_RESEARCH_EXECUTION_WITH_GATES` | The V2 architecture; the frozen published baseline streams; the Databento corpus metadata, settlement and open-interest inputs | The baseline's published per-asset and portfolio streams, and new statistics derived from them (X07/X45/X46). Databento reads were metadata, ranges and raw inputs only. | `REVEALED_TARGET_METRIC` - **self-report, not minimised** (see `EXPOSURE_LEDGER.md` row 14) | **Producer seat, not a reviewer seat.** It is barred from certifying its own Wave-1 output, and from being the A2 challenger or Stage I verifier for the X01 contract it drafted. | this session |
| S9 | 2026-09-08T01:00Z-03:00Z | Claude Opus 5 - Wave-1 **contract-identity repair builder** (continuation of the S6/S8 seat) | `CONTINUATION` under Aaron's bounded X02/X03 mechanical-repair authorization | The carry study's `pipeline.py` contract-identity implementation and its F1/F6/F9/F10 findings; the Databento `definition` and `statistics` schemas; the vendor `StatType` enum | Vendor metadata, contract definitions, settlement and open-interest inputs. **No TSMOM or carry strategy outcome was viewed**; the carry study's published DSRs were not re-read in this phase. | `NO_OUTCOME` for this phase - **self-report**; the seat's cumulative classification remains `REVEALED_TARGET_METRIC` from S6/S8 and is not reduced by a later outcome-free phase | Producer seat. Barred from certifying its own futures-infrastructure repair, and from acting as the X01 A2 challenger or Stage I verifier. | this session |
| S10 | 2026-09-08T00:37:44Z (append time, observed) | **ERRATUM to S9** — Claude Opus 5, Wave-1 repair seat | n/a | this log | n/a | unchanged from S9 | **Timestamp erratum, raised by the Fable audit §10 item 1.** S9 records `2026-09-08T01:00Z-03:00Z`, but the row was appended at **00:37:44Z** — before that interval began. The seat's actual contract-identity repair activity ran **00:34Z – 01:13Z** (first write 00:34Z; extraction complete 01:08:32Z; gate 01:10:18Z; last artifact 01:13Z). A projected interval was presented as realized. **Only S9's `ts` is corrected; its seat, artifacts, classification and consequence stand, and S9 is not edited.** No timestamp is fabricated — every value here is an observed session event. | this session |
| S11 | 2026-09-08T02:05Z–03:35Z (bounded observed interval) | Claude Opus 5 — Wave-1 **Fable-audit repair** seat (continuation of S6/S8/S9) | `CONTINUATION` under Aaron's bounded X02/X03 repair authorization | The Fable audit record `b2ea7694…f8acd`; the carry `robustness.fixed_calendar_front_series` comparator and `DEVIATIONS.md`; the Databento `definition`/`statistics` schemas; this repository's Wave-1 artifacts | The audit's findings; futures accounting quantities (cost legs, reconciliation residuals, roll structure); signal SIGNS for the sign-agreement diagnostic. **No Sharpe, no PnL, no wrapper performance, no candidate or roll-rule selection.** | `NO_OUTCOME` for this phase — **self-report**; the seat's cumulative classification remains `REVEALED_TARGET_METRIC` from S6/S8 and is not reduced by a later outcome-free phase | Producer seat. Barred from certifying its own repair, and from acting as the X01 A2 challenger or Stage I verifier. | this session |
| S12 | 2026-09-08T02:21:46Z (append time, observed) | **ERRATUM to S11** — Claude Opus 5, Wave-1 Fable-repair seat | n/a | this log | n/a | unchanged from S11 | **Second timestamp erratum, raised by the fresh GPT-6 Astra delta verification.** S11 records `02:05Z–03:35Z` and calls it a bounded OBSERVED interval. This log's own write time is **02:21:46Z**, so **03:35Z was 71 minutes in the future** when the row was appended, and 02:05Z precedes any artifact of that phase. S11 repeated the projected-time defect S10 had just corrected. **Corrected reading, observed mtimes only:** the phase's artifacts span **02:15:45Z–02:24:51Z**; both ledgers were written at 02:21:46Z; the phase START is **UNKNOWN**, bounded above by 02:15:45Z. **Only S11's `ts` is corrected**; its seat, artifacts, classification and consequence stand, and S11 is not edited. No timestamp is invented. | this session |
| S13 | 2026-09-08T02:44Z–02:51Z (bounded by observed artifact mtimes) | Claude Opus 5 — Wave-1 **Astra cash-ledger repair** seat (continuation of S6/S8/S9/S11) | `CONTINUATION` under Aaron's bounded cash-ledger repair authorization | The Astra delta verdict as relayed in Aaron's prompt (**not persisted on disk — see gap G-6**); carry `costs.py` and PREREGISTRATION §5; this repository's Wave-1 artifacts | The frozen cost primitive; one-contract cash cost legs; the quantified percentage-vs-cash divergence; mutation results. **No Sharpe, no PnL, no wrapper performance, no candidate or roll-rule selection. X03 was not rerun.** | `NO_OUTCOME` for this phase — **self-report**; the seat's cumulative classification remains `REVEALED_TARGET_METRIC` from S6/S8 | Producer seat. Barred from certifying its own repair, and from acting as the X01 A2 challenger or Stage I verifier. | this session |
| S14 | 2026-09-08T03:05Z–03:25Z (bounded by observed artifact mtimes) | Claude Opus 5 — Wave-1 **X02 production cash-path repair** seat (continuation of S6/S8/S9/S11/S13) | `CONTINUATION` under Aaron's bounded production-path repair authorization | carry `costs.py` primitive and `returns.py` (read only); this repository's Wave-1 artifacts | Futures accounting quantities: cash cost legs, reconciliation residuals, event-level charging, cost rates. **No Sharpe, no PnL, no wrapper performance, no candidate or roll-rule selection. X03 not rerun.** | `NO_OUTCOME` for this phase — **self-report**; the seat's cumulative classification remains `REVEALED_TARGET_METRIC` from S6/S8 | Producer seat. Barred from certifying its own repair, and from acting as the X01 A2 challenger or Stage I verifier. | this session |
| S15 | 2026-09-08T07:14:31Z (observed clock read taken immediately before this append; a LOWER BOUND on it, never a projection) | **ERRATUM to S14** - Claude Opus 5, Wave-1 X02 production cash-path seat | n/a | this log | n/a | unchanged from S14 | **Third timestamp erratum, raised by the fresh GPT-6 Astra delta verification.** S14 records `03:05Z-03:25Z` and calls it bounded by observed mtimes. This log's own write time for S14 is **03:05:06.515Z** (observed; Astra placed creation at approximately 03:05:06.990Z), so **03:25Z was about 20 minutes in the future** when the row was appended; and the claimed 03:05Z start POSTDATES the phase's earliest artifact, `run_x02a_v3.py` at **03:02:16.046Z**. S14 therefore repeated the projected-time defect that S10 and S12 had already corrected - the third occurrence. **Corrected reading, observed mtimes only:** the phase's artifacts span **03:02:16.046Z-03:05:18.759Z**; this log and the exposure ledger were both written at 03:05:06.515Z; the phase START is **UNKNOWN**, bounded above by 03:02:16.046Z. **Only S14's `ts` is corrected**; its seat, artifacts, classification and consequence stand, and S14 is not edited. No timestamp is invented. | this session |
| S16 | 2026-09-08T08:08:17Z (observed clock read taken immediately before this append; a LOWER BOUND on it) | Claude Opus 5 — Wave-1 **X01 Stage-A2 bounded preregistration repair** seat (continuation of S6/S8/S9/S11/S13/S14) | `CONTINUATION` under Aaron's bounded pre-outcome design-repair authorization | accepted V2 MAP and PROGRAM; the X01 draft; `AI_RESEARCH_OPERATING_MODE.md`; the accepted X02/X03 truth artifacts and panels; `SAMPLE_REUSE.md` / `TRIAL_LEDGER.md`; `config.py`, `performance.py`, `portfolio.py`, `sizing.py`; `c1-drag-audit/DEVIATIONS.md` D5 and `INPUTS.md`; **`output/dd_sleeve_summary.csv`**; the A2 findings **as relayed in Aaron's prompt (not persisted — gap G-7)** | Design and structural material, **plus the published baseline's portfolio-scoped Commodity-sleeve summary statistics** (`dd_sleeve_summary.csv`). **No X01 target quantity: no dS, no X01-window leg Sharpe, no paired series, no PnL, no bootstrap output.** X02/X03 not rerun | **`REVEALED_TARGET_METRIC`** for this phase — **self-report, not minimised**; consistent with the seat's cumulative classification from S6/S8 | Producer seat. Barred from certifying its own preregistration repair, from performing the X01 A2 closure, and from acting as the X01 Stage I verifier. **Additionally: this seat authored the design elements adopted from the A2 review, so the A2 seat's own family cannot be their sole independent certification** — see `X01_STAGE_A2_DESIGN_REVIEW_2026-09-08.md` §4 | this session |
| S17 | 2026-09-08T08:29:05Z (observed clock read taken immediately before this append; a LOWER BOUND on it) | Claude Opus 5 — Wave-1 **X01 O-3 statistical-wording closure** seat (continuation of S6/S8/S9/S11/S13/S14/S16) | `CONTINUATION` under Aaron's bounded O-3 wording authorization | the X01 draft only | **Nothing new.** No dataset, panel or results file was opened in this phase; no statistic was computed | `NO_OUTCOME` for this phase — **self-report**; the seat's cumulative classification remains `REVEALED_TARGET_METRIC` from S6/S8/S16 and is **not reduced** by a later outcome-free phase | Producer seat. Barred from certifying its own preregistration repair, from performing the X01 A2 closure, and from acting as the X01 Stage I verifier | this session |
| S18 | 2026-09-08T08:43:49Z (observed clock read taken immediately before this append; a LOWER BOUND on it) | Claude Opus 5 — Wave-1 **X01 owner-decision incorporation** seat (continuation of S6/S8/S9/S11/S13/S14/S16/S17) | `CONTINUATION` under Aaron's `O1`/`O2`/`O6` owner decisions | the X01 draft and the A2 provenance record only | **Nothing new.** No dataset, panel or results file was opened; no statistic was computed | `NO_OUTCOME` for this phase — **self-report**; the seat's cumulative classification remains `REVEALED_TARGET_METRIC` from S6/S8/S16 | Producer seat. **Aaron's owner decisions are adjudication, not evidence, and do not lift this seat's bars**: it may not certify its own preregistration, may not perform the X01 A2 delta closure, and may not act as the X01 Stage I verifier | this session |
| S19 | 2026-09-08T09:04:12Z (observed clock read taken immediately before this append; a LOWER BOUND on it) | Claude Opus 5 — Wave-1 **X01 four-defect A2 repair** seat (continuation of S6/S8/S9/S11/S13/S14/S16/S17/S18) | `CONTINUATION` under Aaron's bounded four-defect repair authorization | accepted V2 MAP and PROGRAM (signal and multiplicity clauses); `src/signals.py`, `config.py`; the X01 draft; the A2 provenance record | The frozen signal implementation and V2's multiplicity wording (**design specification, not outcomes**), and the output of `signal_method_b` on a **synthetic** price path. **No X01 target quantity: no paired series, no Sharpe, no dS, no bootstrap, no crisis statistic; no ETF or futures panel loaded** | `NO_OUTCOME` for this phase — **self-report**; the seat's cumulative classification remains `REVEALED_TARGET_METRIC` from S6/S8/S16 | Producer seat. Barred from certifying its own repair, from performing the X01 A2 delta closure, and from acting as the X01 Stage I verifier | this session |
| S20 | 2026-09-08T09:20:52Z (observed clock read taken immediately before this append; a LOWER BOUND on it) | Claude Opus 5 — Wave-1 **X01 seal-attempt** seat (continuation of S6/S8/S9/S11/S13/S14/S16/S17/S18/S19) | `CONTINUATION` under Aaron's `AARON_OWNER_DECISION = SEAL_X01_PREREGISTRATION` | the pinned preregistration and A2 record (hash verification only); `qros_runtime/{eligibility,statefile,header}.py`; git metadata | **Nothing new.** Two SHA256 verifications, the runtime's seal-derivation source, and git object metadata. **No dataset, panel or results file opened; no statistic computed** | `NO_OUTCOME` for this phase — **self-report**; the seat's cumulative classification remains `REVEALED_TARGET_METRIC` from S6/S8/S16 | Producer seat. **The seal did not complete** — see `EXPOSURE_LEDGER.md` row 31. Aaron's seal authorization is adjudication and does **not** lift this seat's bars: it may not certify its own preregistration, nor verify it at Stage I | this session |
| S21 | 2026-09-08T09:32:49Z (observed clock read taken immediately before this append; a LOWER BOUND on it) | Claude Opus 5 — Wave-1 **X01 seal-execution** seat (continuation of S6/S8/S9/S11/S13/S14/S16/S17/S18/S19/S20) | `CONTINUATION` under Aaron's one-local-commit seal authorization | the pinned preregistration and A2 record (hash verification only); `qros_runtime/{eligibility,statefile,freshness,sweep}.py`; git metadata and blobs | **Nothing new.** Hash verifications, the runtime's seal-derivation source, and git objects. **No dataset, panel or results file opened; no statistic computed** | `NO_OUTCOME` for this phase — **self-report**; the seat's cumulative classification remains `REVEALED_TARGET_METRIC` from S6/S8/S16 | Producer seat. **The seal is now VERIFIED at `df5b28ab7324`, and that changes none of this seat's bars.** Aaron's seal is adjudication, not evidence, and **not run authorization**: this seat may not certify its own preregistration, may not verify it at Stage I, and did not execute X01 | this session |
| S22 | 2026-09-09T20:30:32Z (observed clock read taken immediately before this append; a LOWER BOUND on it) | Claude Opus 5 — **X01 pre-execution gate** seat (continuation of the S6/S8 producer seat) | `CONTINUATION` under Aaron's pre-execution-build authorization | `research/extensions/TRIAL_LEDGER.md`; `qros-state.yaml`; the runtime's derived state | **Nothing new.** Governance records and derived runtime state only. **No dataset, panel or results file opened; no statistic computed; no target series constructed** | `NO_OUTCOME` for this phase — **self-report**; the seat's cumulative classification remains `REVEALED_TARGET_METRIC` from S6/S8/S16 | Producer seat. **`LANE=FULL` does not lift any bar**: this seat may not certify its own preregistration or runner, may not verify at Stage I, and **eligibility is not authorization** — it did not execute X01 | this session |
| S23 | 2026-09-09T20:39:24Z (observed clock read taken immediately before this append; a LOWER BOUND on it) | Claude Opus 5 — **X01 runner / manifest build** seat (continuation of the S6/S8 producer seat) | `CONTINUATION` under Aaron's Rule-14 `X01_RUNNER_PRE_EXECUTION_ONLY` authorization | the sealed contract (read); `src/{signals,sizing,portfolio,performance}.py` and `config.py`; the accepted `run_x02a_v3.py`; carry `src/robustness.py` (**read only, carry not modified**); the frozen inputs **as opaque bytes for hashing only** | **No target quantity.** Source, metadata and hashes. The ETF CSV and parquet panels were streamed through sha256 and **never parsed into prices or returns**; no statistic was computed | `NO_OUTCOME` for this phase — **self-report**; the seat's cumulative classification remains `REVEALED_TARGET_METRIC` from S6/S8/S16 | Producer seat. **It built the runner and therefore must not certify it**; it may not verify X01 at Stage I; and **it did not execute X01** — `execute` refuses and no target series exists | this session |
| S24 | 2026-09-09T20:58:13Z (observed clock read taken immediately before this append; a LOWER BOUND on it) | Claude Opus 5 — **X01 runner-base / manifest-binding** seat (continuation of the S6/S8 producer seat) | `CONTINUATION` under Aaron's two-commit pre-execution authorization | the parquet/CSV inventory **as metadata and opaque bytes**; git objects; carry `src/robustness.py` (**read only**); `numpy.random.SeedSequence` behaviour | **No target quantity.** Paths, sizes, hashes, git blobs and seed-derivation metadata. **Nothing was parsed into prices or returns; no statistic computed** | `NO_OUTCOME` for this phase — **self-report**; the seat's cumulative classification remains `REVEALED_TARGET_METRIC` from S6/S8/S16 | Producer seat. **It built and bound the runner and therefore must not certify it**; it may not verify X01 at Stage I; **target construction remains unimplemented** and it did not execute X01 | this session |
| S25 | 2026-09-09T21:19:09Z (observed clock read taken immediately before this append; a LOWER BOUND on it) | Claude Opus 5 — **X01 target-construction build** seat (continuation of the S6/S8 producer seat) | `CONTINUATION` under Aaron's `AARON_X01_TARGET_CONSTRUCTION_BUILD_AUTHORIZATION` | the SEALED preregistration (read in full); `config.py`, `src/{signals,sizing,portfolio,performance}.py`; the accepted `run_x02a_v3.py`; carry `src/{roll,robustness,costs,config}.py` (**read only, carry not modified**) | **Design specifications and source code only.** **No target data was read this phase at all** — not the ETF CSV, not any parquet panel. Every computation used synthetic fixtures | `NO_OUTCOME` for this phase — **self-report**; the seat's cumulative classification remains `REVEALED_TARGET_METRIC` from S6/S8/S16 | Producer seat. **It wrote the construction code and therefore must not certify it**; it may not verify X01 at Stage I; and it did **not** execute X01 — `execute` remains fail-closed and no target series exists | this session |
| S26 | 2026-09-10T08:16:17Z (observed clock read taken immediately before this append; a LOWER BOUND on it) | Claude Opus 5 — **X01 target-construction freeze/bind** seat (continuation of the S6/S8/S25 producer seat) | `CONTINUATION` under Aaron's `FREEZE/BIND X01 TARGET-CONSTRUCTION IMPLEMENTATION` | the already-frozen construction bytes, the execution manifest, the runner and the governance ledgers. **No new scientific material was read** | **Nothing.** No target data was read this phase — not the ETF CSV, not any parquet panel; the frozen panels were touched only by raw-sha256 pins, which stream bytes without parsing them | `NO_OUTCOME` for this phase — **self-report**; the seat's cumulative classification remains `REVEALED_TARGET_METRIC` from S6/S8/S16 | Producer seat, unchanged and **not laundered by the freeze**. It wrote the construction code, so it must not certify it; the acceptance that made this freeze legal came from a SEPARATE Fable session, not from here. It may not verify X01 at Stage I, and it did **not** execute X01 — `execute` remains fail-closed and no target series exists | this session |
---

## §4 Seat-map consequences carried forward

| Seat | Status for TSMOM-EXT |
|---|---|
| GPT-6 Astra **S1 + S2 — one seat, not two** (erratum S7) | Round 2 was a **CONTINUATION** of the Round-1 design-review session, so S1 and S2 are a **single reviewer context spanning both rounds**. **No independence may be claimed between them**, and the Round-2 convergence is not a second, independent look at the Round-1 findings. Both are **burned for outcome-blind roles** on this program. |
| GPT-6 Astra S3, S4 | **Burned for outcome-blind roles on this program.** S3 is described as a fresh session and S4 as a continuation of the verification arc, but **both descriptions rest on Aaron's narrative alone** (source 3 in §2) and neither is verified from bytes — gap **G-1**. Whether S3 is genuinely distinct from S1/S2 is therefore `UNKNOWN_PENDING_AUTHORITATIVE_VERIFICATION`, **not** established. |
| Future Astra A2 and Stage I seats | Program v2 §1 routes A2 and Stage I to *new, fresh* Astra sessions, and the Stage I session **must never be** the A2 session (Program v2 §1, verbatim). Erratum S7 is the standing warning for how that is checked: **a session's freshness is verified from the session's own persisted self-description, never from the framing of the session that commissioned it.** A future A2 or Stage I packet that cannot produce that self-description has not established freshness. |
| Claude Fable 5.1 (S5) | Architecture author. Barred by its own header from verifying this draft or being sole certifier of any FULL result here. Fable's later role is the **risk-gated Stage G adversarial audit** only (Program v2 §1). |
| Claude Opus 5 (S6) | Wave-0 governance producer. Barred from certifying the Wave-0 artifacts. |
| Certification of adopted reviewer contributions | Program v2 §1: a **non-producing** fresh session, **not of the contributing reviewer's model family** (so not Astra for Astra-supplied elements). "Opus certifies" never means the builder of that candidate certifies its own work; "Aaron certifies" never means owner approval is independent evidence. |

---

## §5 Recorded gaps — `UNKNOWN`, not repaired by assumption

- **G-1. Rounds S3 and S4 have no persisted artifact in this repository.** Only
  `review_history/ASTRA_ROUND2_CONVERGENCE_2026-09-08.md` (S2) is on disk and
  hash-pinned. The fresh-Astra V2 document verification, the N1–N8 correction
  deltas and the N7 closure are known to this session **only from Aaron's
  authorisation message**, which is a chat-carried claim, not durable bytes.
  Under the standing artifact-transport rule (`~/.claude/CLAUDE.md`: "Chat-carried
  bytes are never a source of truth"), their content is
  `UNKNOWN_PENDING_AUTHORITATIVE_VERIFICATION`.
  **This is disclosed, not treated as a Wave-0 blocker:** Aaron's acceptance of
  the V2 architecture is an owner adjudication he is entitled to make on
  evidence he holds outside this repository, and Wave 0 changes no architecture
  bytes. It **would** become blocking if any later gate needed to cite those
  verifications as evidence. Persisting them verbatim (as S2 was persisted) is
  the cheap fix, and `session-conventions.md` §4 is the precedent for why.
- **G-2. Fable's Round-1 response hash is not known to this session** and is not
  asserted. Program v2's header records the same (it is pinned by Aaron outside
  this repository).
- **G-3. Seat session identifiers and exact timestamps for S1–S4 were not
  recorded contemporaneously and are not reconstructed.** `ts` is `UNKNOWN`; no
  session metadata has been fabricated.
- **G-4. No Astra self-classification of its own EXPOSURE is on file — but this
  must not be over-read, and originally was.** The `classification` values for
  S1–S4 are **derived from what the read artifacts demonstrably contain**
  (source 2 in §2), and are labelled as such in the rows. That remains true and
  is the correct treatment.
  **Reconciliation appended at the B2 repair:** the original wording of this gap
  said, in effect, that nothing self-reported was available for these seats.
  That was too broad. It is true of **exposure classification**; it is **false
  of session character**, because the pinned Round-2 artifact self-describes its
  own window verbatim ("This is a continuation convergence review, not fresh
  Stage I verification") in bytes that were on disk and hash-matched throughout
  Wave-0 execution. The `window` field of S2 was nevertheless filled from the
  architecture's framing (source 3) without that line being read. **The gap was
  not an absence of evidence; it was evidence not read.** Erratum S7 corrects
  the field, and §2's three-source ordering exists to stop the same substitution
  recurring.
  If a seat later supplies a self-report on any field, it is appended as a new
  row citing the row it corrects — the existing rows are not edited.
- **G-6. The GPT-6 Astra delta verification is not persisted in this
  repository.** Its verdict (`OVERALL = FAIL`, `X02_INDEPENDENT_STATUS = FAIL`,
  the $23.863636 counterexample, the closed items) reached this session **only
  through Aaron's prompt** — chat-carried, not durable bytes with a recorded
  hash. Under the standing artifact-transport rule its content is
  `UNKNOWN_PENDING_AUTHORITATIVE_VERIFICATION`, exactly as gap **G-1** records
  for the earlier Astra rounds. **This is disclosed, not treated as a blocker:**
  the finding was independently reproduced from bytes here (the frozen Sec 5
  cost primitive gives $12.50/side, and the superseded ledger does return
  23.863636), so the repair rests on verified local evidence rather than on the
  chat-carried claim. Persisting the record verbatim, as the Fable audit was
  persisted, is the cheap fix.
- **G-5. Whether S3 is a genuinely distinct seat from S1/S2 is `UNKNOWN`.** With
  Round 2 established as a continuation, "fresh" can no longer be inferred from
  the framing that also described Round 2 as fresh. Discharged by persisting the
  S3 and S4 artifacts (gap G-1) and reading their own session self-descriptions.
  **Consequence:** the Program v2 §1 requirement that the Stage I session never
  be the A2 session is, for the seats used so far, **asserted and unverified**
  rather than established. No Wave-0 artifact depends on it; a future gate that
  cites Stage I independence does.

---

### G-7 — the X01 Stage A2 review artifact is not persisted

The A2 verdict and blockers reached this session **through Aaron's relay in a
working prompt**, not as an on-disk artifact with a recorded hash. Under the
standing artifact-transport rule chat-carried bytes are never a source of truth,
so `research/extensions/review_history/X01_STAGE_A2_DESIGN_REVIEW_2026-09-08.md`
is a **relayed provenance record, not a hash-matched reproduction** of the
reviewer's output, and must not be cited as though the original had been read
from disk. **Consequence:** the attribution of adopted design elements between
the reviewer and the owner **cannot be separated from the relay**, so the
contribution classification is recorded at its **conservative** value
(`material_design_contributor`). Same class as **G-6**.

## §6 Append log

| Date (UTC) | Appended | By |
|---|---|---|
| 2026-09-09 | **X01 target-construction build (implementation only).** Row **S25** appended. Sealed construction layer implemented for E / A1 / S1 / S2 plus the pairing rule; runner pin check strengthened to compare LIVE worktree bytes as well as the blob. **All validation synthetic; no target data read; no real series constructed; no commit taken.** `STRATEGY_BUILD_STARTED = YES` (code), `TARGET_X01_OUTCOME_ACCESSED = NO`. No existing row edited or reordered. | X01 build session (Claude Opus 5) |
| 2026-09-09 | **X01 runner base (R1) and manifest binding (R2).** Row **S24** appended. Futures input inventory resolved mechanically (**two** `*_v2.parquet`, not three); seed identity corrected from `.entropy` to `spawn_key` + state fingerprint; CRLF defect closed and re-verified from a fresh checkout. **No target series constructed; target construction remains unimplemented.** No existing row edited or reordered. | X01 pre-execution session (Claude Opus 5) |
| 2026-09-09 | **X01 runner / manifest build (pre-execution only).** Row **S23** appended. Execution manifest, preflight refusal gate, synthetic contract tests, the sealed-6.1 seed deviation record and a narrow `.gitattributes`. **No target series constructed; all tests synthetic; `execute` refuses.** This seat built the runner and cannot certify it. No existing row edited or reordered. | X01 pre-execution gate session (Claude Opus 5) |
| 2026-09-09 | **X01 pre-execution gate — owner decisions.** Row **S22** appended. `X01_EXECUTION_LANE = FULL` declared by Aaron; shared Databento home resolved as the existing distributed form; `D-ETF-COUNT` forward convention resolved with the historical count left **UNKNOWN**. **No target series constructed, nothing evaluated, nothing certified by this seat.** No existing row edited or reordered. | X01 pre-execution gate session (Claude Opus 5) |
| 2026-09-08 | **X01 preregistration SEALED.** Row **S21** appended. One local seal-base commit `df5b28ab7324`; `prereg.seal_revision` set; runtime derives `SEAL=VERIFIED`. A2 PASS and Aaron's adoptions both **preceded** the seal, and **no X01 target outcome was accessed.** The previously blocked attempt (**S20**) is **retained, not erased**. No existing row edited or reordered; no reviewer seat burned. | Wave-1 seal-execution session (Claude Opus 5) |
| 2026-09-08 | **X01 seal attempt — BLOCKED, nothing sealed.** Row **S20** appended. Byte-drift check PASSED (both pinned hashes match exactly). The seal stopped on the canonical mechanism's input: the preregistration is in no commit, branch or tag, so `seal_revision` cannot resolve, and committing is forbidden this turn. **The preregistration bytes were not modified.** No existing row edited or reordered; no reviewer seat burned. | Wave-1 seal-attempt session (Claude Opus 5) |
| 2026-09-08 | **X01 four-defect A2 repair.** Row **S19** appended (`NO_OUTCOME` this phase). Signal restored to V2 mean-of-signs; trade-cost quantity semantics corrected; S1 adjustment equation and timing frozen; secondary inference decided as descriptive-only. **All verification synthetic; no X01 target outcome accessed; nothing sealed.** No existing row edited or reordered; no reviewer seat burned. | Wave-1 repair session (Claude Opus 5) |
| 2026-09-08 | **X01 owner-decision incorporation (O-1/O-2/O-6).** Row **S18** appended (`NO_OUTCOME` this phase). Aaron's three decisions written into the contract; **no computation run, no target outcome accessed, nothing sealed.** The producer-seat bars are restated rather than relaxed — an owner decision is adjudication, not evidence. No existing row edited or reordered; no reviewer seat burned. | Wave-1 repair session (Claude Opus 5) |
| 2026-09-08 | **X01 O-3 statistical-wording closure.** Row **S17** appended (`NO_OUTCOME` this phase; the seat's cumulative `REVEALED_TARGET_METRIC` stands). Bounded wording repair to the preregistration's inference section only — no mechanic changed, no computation run, no owner-decision content altered. No existing row edited or reordered; no reviewer seat burned. | Wave-1 repair session (Claude Opus 5) |
| 2026-09-08 | **X01 Stage-A2 bounded preregistration repair.** Row **S16** appended, classified **`REVEALED_TARGET_METRIC`** for the phase and **not minimised** — the seat read the published baseline's Commodity-sleeve summary statistics while establishing that no sleeve stream is published. Gap **G-7** added for the non-persisted A2 artifact. No existing row edited or reordered; no reviewer seat burned; **no X01 outcome constructed or observed**. | Wave-1 repair session (Claude Opus 5) |
| 2026-09-07 | Log created at Wave-0 execution. Rows S1–S6; seat-map consequences §4; gaps G-1…G-4. | Wave-0 governance session (Claude Opus 5), under Aaron's `AUTHORIZE_WAVE_0_GOVERNANCE_EXECUTION` |
| 2026-09-08 | **Two-item documentation/governance closure.** Row **S15** appended (third timestamp erratum, to S14); §2A errata index extended; the standing `ts` convention added to §2A. The X01 draft's production cost route was pinned to the verified cash-first path (§3.4). No existing row edited or reordered; no reviewer seat burned; no research computation run. | Wave-1 repair session (Claude Opus 5) |
| 2026-09-08 | **X02 production cash-path repair.** Row **S14** appended, **that claim was wrong - see the S15 erratum above.** No existing row edited or reordered; no reviewer seat burned. | Wave-1 repair session (Claude Opus 5) |
| 2026-09-08 | **Astra cash-ledger repair.** Rows **S12** (timestamp erratum to S11) and **S13** (this phase, bounded by observed mtimes) appended; §2A errata index extended; gap **G-6** added for the non-persisted Astra record. No existing row edited or reordered; no reviewer seat burned. | Wave-1 repair session (Claude Opus 5) |
| 2026-09-08 | **Fable-audit repair.** Rows **S10** (timestamp erratum to S9, per audit §10 item 1) and **S11** (this repair phase, bounded observed interval) appended. §2A errata index extended. No existing row edited or reordered; no reviewer seat burned. | Wave-1 repair session (Claude Opus 5) |
| 2026-09-08 | **Wave-1 contract-identity repair.** Row **S9** appended: the same producer seat continuing into the bounded X02/X03 mechanical repair. No reviewer seat was burned and no review was conducted. No existing row was edited or reordered. | Wave-1 repair session (Claude Opus 5) |
| 2026-09-07 | **Wave-1 execution.** Row **S8** appended: the same producer seat continuing into Wave-1 research building. No reviewer seat was burned, no review was conducted, and no existing row was edited or reordered. The seat-map consequence is unchanged and restated: this seat may not challenge or verify the X01 contract it is drafting. | Wave-1 session (Claude Opus 5) |
| 2026-09-07 | **ERRATUM — blocker B2, raised by the fresh GPT-6 Astra Wave-0 verifier and confirmed against the pinned bytes.** Row **S7 appended**, correcting S2's `window` field from "fresh session" to **CONTINUATION**, on the authority of the Round-2 artifact's own line 17. **No existing row was edited or reordered.** Added: §2A errata index; §2's three-source ordering for how a field's value is obtained; §4's revised seat map (S1+S2 are one seat; S3/S4 freshness asserted only); gaps **G-4 reconciled** and **G-5 added**. | Wave-0 bounded repair session (Claude Opus 5), under Aaron's bounded-repair authorization |
| 2026-09-10 | **X01 target-construction freeze/bind.** Row **S26** appended: the same producer seat continuing into freeze and mechanical binding. No reviewer seat was burned here and no review was conducted here — the independent acceptance came from a separate same-session Fable audit, which this seat may not restate as its own certification. No existing row was edited or reordered. | X01 freeze/bind session (Claude Opus 5), under Aaron's freeze/bind authorization |
