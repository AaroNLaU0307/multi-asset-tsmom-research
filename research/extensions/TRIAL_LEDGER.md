# TRIAL_LEDGER.md — TSMOM-EXT-001

**Program:** TSMOM extension (`TSMOM-EXT-001`), `multi-asset-tsmom-research`
**Created:** 2026-09-07 (Wave 0 governance execution, authorised by Aaron)
**Implements:** `TSMOM_EXTENSION_RESEARCH_PROGRAM_v2.md` §0B — the four-object
exposure and trial model
**Read with:** `research/extensions/SAMPLE_REUSE.md` · `ops/EXPOSURE_LEDGER.md`

**Append-only.** Rows are never deleted, merged, consolidated or reordered. An
error is corrected by appending a row that cites the row it corrects.

---

## §1 Four objects, never merged

| Object | Definition | Rules |
|---|---|---|
| **EXPOSURE_EVENT** | Any computation or read that **reveals outcomes or measurements** | Sample snapshot id; session; outputs actually revealed; a canonical `TBL-EXPOSURE-CLASSES` token plus the auxiliary explanatory category; seal timing relative to any contract; downstream design use as append-only link rows. Research-axis and reviewer-axis events are **linked without double-counting trials**. **Carried in `ops/EXPOSURE_LEDGER.md` (research axis) and `ops/REVIEWER_EXPOSURE_LOG.md` (seat axis)**; §2 below indexes them. |
| **VARIANT_ATTEMPT** | **Every distinct evaluated strategy configuration or selection opportunity** | Immutable, **one row each**, with design parent and family. **Never deleted, merged or consolidated after observing PnL correlation or any outcome.** Exact reproduction of an already-recorded configuration is a provenance / re-exposure record, **not automatically a new distinct variant**. |
| **HYPOTHESIS_FAMILY** | The **prospectively declared** inferential and selection scope | Declared in the preregistration **before any member runs** — including bridge cells, secondary metrics, cost levels and per-cell claims. **Family membership never deletes attempts.** Grouping follows the **actual selection process**, not document labels. |
| **GOVERNED_N_TRIALS_CONTRIBUTION** | The attempt's contribution to the sample's cumulative `N_trials` | Follows the **authoritative declared convention for that sample, and cites it**. One visible attempt is **not** automatically `+1`. |

### §1.1 Four prohibitions, stated so a later session cannot re-derive them away

1. **No post-result correlation consolidation.** Attempts are **never** erased,
   merged or re-grouped because their PnL turned out to be highly correlated, or
   because any other outcome was observed. High dependence triggers
   `HIGH_REDUNDANCY_REVIEW` (Program v2 §0 rule 12) — a **review**, not a
   deletion, and not an automatic `not_promoted`.
2. **No post-hoc family merging.** Families are declared **before** the first
   member runs. A grouping decided after seeing results is a new record with its
   own disclosure, never a retroactive edit.
3. **No automatic `+1` per attempt.** A `VARIANT_ATTEMPT` row is a record that an
   evaluation happened. Whether it contributes to `N_trials` is decided by the
   sample's **authoritative declared convention** — for the Databento panel, by
   whether it constructed a distinct strategy-return series.
4. **No silent recomputation of frozen historical counts.** A frozen count is
   changed only through the originating study's authorised deviation process,
   which forces the DSR consequence into the open.

---

## §2 EXPOSURE_EVENT — index (the ledgers are authoritative)

This section is an **index**, not a second copy. The authoritative rows are in
the ledgers named below; nothing here may diverge from them.

> **Index corrected 2026-09-08.** These counts had gone stale at 19/9 while the ledgers held 27/16 — they drifted across the Fable, cash-ledger, production-cash-path and documentation-closure phases. This section is an **index**; the ledgers are authoritative and were never wrong. Counts are re-derived from them here, and no ledger row was edited.

| Axis | Authoritative file | Rows today | Normalized value |
|---|---|---|---|
| RESEARCH | `ops/EXPOSURE_LEDGER.md` event table | **32** (1–9 historical · 10–12 Wave 0 · 13–17 Wave 1 · 18–19 contract-identity repair · 21 Fable repair · 23 cash-ledger repair · 24 production cash-path repair · 26 documentation closure · 27 X01 Stage-A2 repair · 28 O-3 wording closure · 29 owner-decision incorporation · 30 four-defect A2 repair · 31 blocked seal attempt · **32 seal completed** · errata **20, 22, 25**) | `HISTORICAL_CUMULATIVE = TARGET_METRIC`; `CURRENT_REVIEW_SCOPE = TARGET_METRIC` |
| SEAT | `ops/REVIEWER_EXPOSURE_LOG.md` §3 | **21** (S1–S6 Wave 0 · S7 the B2 erratum · S8 Wave 1 · S9/S11/S13/S14 repair seats · S16 X01 Stage-A2 seat · S17 O-3 wording closure · S18 owner-decision incorporation · S19 four-defect A2 repair · S20 blocked seal attempt · **S21 seal completed** · timestamp errata **S10, S12, S15**) | *not aggregated into research exposure — burning a seat consumes no research degrees of freedom* |

**Linked without double-counting:** `EXPOSURE_LEDGER.md` §5 cross-references the
seat rows **as pointers carrying no classification and no scope**, so no seat
event can enter the research normalization.

---

## §3 GOVERNED_N_TRIALS_CONTRIBUTION — per sample

### §3.1 `dataset.databento.commodity-futures-curves` — **convention VERIFIED, count FROZEN**

| Field | Value | Verified from |
|---|---|---|
| **Authoritative record** | `commodity-carry-research/preregistration/PREREGISTRATION.md` §10 | read 2026-09-07 |
| **Frozen `N_trials`** | **14** (2 primary + 12 robustness) | PREREG §10 line 205; `commodity-carry-research/src/config.py:66` (`N_TRIALS = 14`) |
| **Counting convention** | One trial per **distinct constructed strategy-return series** (primary and robustness arms). **Diagnostics of an existing series are excluded** (PREREG §10 items 8–9). | PREREG §10; restated at `src/config.py:62-66` |
| **Deviation consequence** | A deviation that adds or removes a constructed series **changes `N_trials`, and every already-computed DSR must be recomputed under the new count.** | PREREG §10 line 207 |
| **TSMOM-EXT contribution to date** | **0.** No TSMOM constructed strategy-return series has been built on this panel. | this program has run no computation |
| **Rule going forward** | Each new TSMOM constructed strategy-return series on this panel is **appended** under the convention above, citing it. **History is never recomputed.** Measurement that constructs no return series (roll dates, contract counts, margin-to-equity, sign-agreement rates, reconciliation residuals) contributes **0** — the `c1-drag-audit` precedent, which deliberately did not extend the ledger for exactly this reason. | Program v2 §0B; `c1-drag-audit/SAMPLE_REUSE.md` |

**Tripwire, inherited and restated:** the ledger **must** be extended the moment
a Sharpe, a confidence interval or a return series is computed on this panel.
A measurement-only pass must not become a back door.

#### §3.1a Owner decisions at the X01 pre-execution gate (2026-09-09)

Aaron adopted the **existing DISTRIBUTED accounting form**. **No new
dataset-level file was created**, and in particular
`quant-research-knowledge-base/registry/sample-trial-ledger.csv` was **not**
created and **no new KB schema was invented**.

| Field | Value |
|---|---|
| `SHARED_DATABENTO_HOME_GATE` | **`RESOLVED`** — the distributed form of §5.1 **is** the answer, not a placeholder for one |
| Historical frozen anchor | **`N_trials = 14`**, unchanged, from the accepted carry record. `commodity-carry-research` is **not modified** by this decision |
| Authoritative TSMOM prospective append view | **this file, §3.1 / §6.1** |
| `TSMOM_TRIAL_LEDGER_CURATOR` | **the X01 executing / governance session** |
| Other project views | remain **references**, not competing totals, and are **not silently rewritten** |
| Current TSMOM contribution | **0** |
| Planned X01 contribution | **+3**, for exactly **A1**, **S1**, **S2** |
| Resulting cumulative | **`authoritative shared cumulative total read immediately before execution + 3`**, subject to no intervening contribution. **`14 → 17` is NOT hard-coded and must not be.** |
| Read-at-execution obligation | the runner **must read the then-current authoritative cumulative Databento state immediately before the first governed construction**, and record what it read |
| Standing prohibition | **correlation can NEVER delete attempts after results are visible** (§1.1 rule 1) |

---

### §3.2 `dataset.yfinance.multi-asset-etf-panel` — **NO FROZEN CONVENTION EXISTS**

| Field | Value |
|---|---|
| **Authoritative record** | **None.** The core had **no preregistration**; no frozen computation ledger and no `N_trials` convention exists for this panel. |
| **What *is* established** | The panel is **burned 6 of 6** (`relationships.csv` lines 16–21, verified 2026-09-07). That is **sample-reuse tracking, not a trial count** — the relationship rows say so in terms. |
| **Historical count** | `UNKNOWN_PENDING_AARON_DECISION` — see §4. **No count has been manufactured.** |
| **45-cell robustness grid** | Its treatment **inside the core's record** (robustness, not selection; parameters unchanged) stays **historically frozen** and is not relabelled by this program. Later designs informed by its **observed outcomes** carry `ROBUSTNESS_GRID_INFORMED` lineage, appended as link rows (`EXPOSURE_LEDGER.md` §4, row L1). |
| **Rule going forward** | Until the convention in §4 is decided, **no `N_trials` figure may be asserted for this panel**, and no DSR computed against an invented count. A candidate needing one is blocked on D-ETF, not on Wave 0. |

---

### §3.3 `dataset.cboe.vix-futures-monthly-chain` — **convention DECLARED, count 0, NOTHING SPENT**

*Appended at TSMOM-VRP-01 S2 acceptance. Dataset identifier provisional until KB
registration (a separate Owner decision, not taken here). Sample record: `SAMPLE_REUSE.md`
KB-6.*

| Field | Value |
|---|---|
| **Authoritative record** | `research/extensions/vrp/VRP_PREREGISTRATION.md` §M (sealed 2026-09-14, SHA256 `dd582244…53e6`), and the acquisition pinned in `research/extensions/vrp/VRP_DATA_MANIFEST.md`. |
| **Counting convention** | The programme's existing convention, reused verbatim: **one trial per distinct constructed strategy-return series with a selection opportunity**; diagnostics of an existing series are excluded. |
| **`N_trials`** | **1**, as of 2026-09-14. Was 0; the sealed Stage-A primary ran ONCE under `VRP-AUTH-0001` (`run_id` VRP-STAGE-A-RUN-0001) and spent its governed trial on CONSTRUCTION, as the convention requires, whatever the state. Final state UNRESOLVED (Class 3). **`STAGE_A_TRIAL_SPENT = YES`.** |
| **Not attempts** | Bootstrap replicates; VRP-DESC members R1–R14; any output carrying `PROMOTION_POWER = NONE`, including the `c0 = 0.05` cost sensitivity. |
| **Stage B** | A paired combination on the heavily reused ETF/core panel, declared there as **T0 / further reuse (ninth-plus)** under the existing convention. It is **conditional on Stage A = SUPPORTED** and contributes nothing until Stage A resolves that way. |
| **Failure classes vs count** | Separate axes, per the sealed §M. A Level-1 (VRP-VALIDITY) or Level-2 (VRP-IMPLEMENTABILITY) failure occurs **before** the governed run and spends **no** trial; a Stage-A run spends its trial whatever its state. |
| **Status at S2 append (2026-09-14, superseded below)** | `STAGE_A_TRIAL_SPENT = NO` · `STAGE_B_TRIAL_SPENT = NO` · all outcome flags NO. S2 acquired and mechanically validated the raw chain only. |
| **Status after the S3 governed run (2026-09-14)** | `STAGE_A_TRIAL_SPENT = YES` · `VIX_CHAIN_TRIAL_INCREMENT = +1` (0 → 1) · `STAGE_B_TRIAL_SPENT = NO` · `SCIENTIFIC_STAGE_A_OUTCOME_GENERATED = YES` · `SCIENTIFIC_STAGE_B_OUTCOME_GENERATED = NO` · `SCIENTIFIC_OUTCOME_REVEALED = YES` (ONCE, under `VRP-AUTH-0002`). Stage-A state **UNRESOLVED / Class 3**. Under the sealed §O stop rule a Class-3 Stage A means **Stage B never runs** on this historical result; the only sealed continuation is VRP-A-PROSPECTIVE. |

---

## §4 AARON DECISION — the ETF-panel trial count (historical OPEN · forward RESOLVED)

> **Resolved at the X01 pre-execution gate, 2026-09-09.** The **historical**
> count stays `UNKNOWN` and is **not** reconstructed or fabricated. What Aaron
> resolved is the **forward** convention, prospectively and before any target
> outcome exists.
>
> | Token | Value |
> |---|---|
> | `D_ETF_COUNT_HISTORICAL` | **`UNKNOWN`** — deliberately not reconstructed |
> | `ETF_E_EXPOSURE_EVENT` | **`YES`** |
> | `ETF_E_VARIANT_ATTEMPT_CONTRIBUTION` | **`+1`** (conservative) |
> | `D_ETF_COUNT_FORWARD_CONVENTION` | **`E_COUNTS_AS_ONE_PROSPECTIVE_ATTEMPT`** |
> | `D_ETF_COUNT_GATE` | **`RESOLVED_FOR_X01_EXECUTION`** |
> | `D_ETF_COUNT_EFFECT_ON_DATABENTO_PLUS3` | **`NONE`** — the two samples are counted separately |
>
> **Reason, recorded as Aaron gave it:** `E` is a **newly constructed target
> return stream**, even though its construction rules are frozen and it serves as
> the *reference* leg. The `+1` is a **conservative governance count**. It does
> **not** imply `E` is a new alpha hypothesis, and it is **separate from the
> Databento futures count** — the planned `+3` for A1/S1/S2 is unaffected.
>
> **Ordering obligation:** before `E` is actually constructed in a later
> authorized run, the exposure event and the attempt classification are recorded
> **BEFORE the output is read**. `E` was **not** constructed in this gate.

### §4.0 The historical question, as originally recorded (still OPEN)

**Decision id:** `D-ETF-COUNT` (Map v2 §K decision **D4**'s embedded clause: *"record
the ETF-panel historical trial-count convention as an open Aaron decision inside
the ledger"*).
**Status:** `OPEN`.
**This is deliberately not a Wave-0 blocker** — Program v2 §2 lists it under
"Not preconditions", and Map v2 §K D4 says deciding it is not a Wave-0
prerequisite. Wave 0's obligation is to **record it here with its options**,
which this section does.

### What the decision is

What counting convention, if any, applies to the ETF panel's **historical** work,
and how the 45-cell robustness grid is counted under it.

### The facts the decision rests on (all verified)

- The core had **no preregistration**, so no ex-ante convention was ever frozen.
- The KB records **6** research paths against the panel, as *sample-reuse
  tracking* and explicitly **not** as a count of independent confirmations.
- The 45-cell grid sits **inside** the core's record as robustness (parameters
  unchanged, no selection among cells), not as 45 separate selections.
- The carry study's convention — one trial per distinct constructed
  strategy-return series, diagnostics excluded — exists and is verified, but it
  was declared for a **different sample** and does not automatically govern here.
- `c1-drag-audit/SAMPLE_REUSE.md` sets out the reasoning for **not** extending a
  trial ledger for measurement-only work, and why a wrongly-extended ledger
  misstates what DSR corrects for.

### Options, stated neutrally

| Option | Convention | What it implies for the historical count | Main objection to it |
|---|---|---|---|
| **A** | Adopt the carry convention retrospectively: one trial per distinct constructed strategy-return series; diagnostics excluded; the 45-cell grid counts as the robustness arms of the core, per its own record. | A specific finite number, derivable by enumerating the committed reports' constructed series. | Applies an ex-post convention to work that was never run under it; the enumeration is itself a research judgement made after the outcomes were seen. |
| **B** | Declare the historical count **permanently `UNKNOWN`** and forbid any DSR on this panel that depends on it; prospective TSMOM-EXT attempts are counted from Wave 0 forward under an explicitly declared convention. | No historical number is asserted. Future counts start at 0 with full disclosure that the residual is undeflatable. | Any future DSR on the panel is uncorrectable for prior search; claims must carry that limitation permanently. |
| **C** | Adopt a **new** ex-ante convention for future ETF work only, and record the historical residual as `UNKNOWN` (a hybrid of A's forward discipline and B's honesty about history). | Forward counts are governed; history stays `UNKNOWN`. | Requires Aaron to fix the forward convention's text before the first ETF candidate runs. |

**No option is recommended here as decided, and none has been implemented.**
The *effective state until Aaron decides* is Option B's operational half:
**no `N_trials` figure may be asserted for this panel.** That is the fail-closed
reading, not a decision.

### Where the decision gets recorded when taken

**Corrected at the B2/NB1 bounded repair.** An earlier revision of this section
directed the decision into `qros-state.yaml`'s `human_decisions[]`. **That is not
possible, and the instruction was wrong.** L6 spec §2.9 is the sole normative
site for `human_decisions[].type` and closes it at exactly three values —
`DORMANT_ENTER`, `DORMANT_EXIT`, `REVIEW_ATTEMPT_EXCLUDED` — and `qros check`
rejects an unrecognised one. A trial-count convention is none of them. **The
enum is not to be extended and no new type is to be invented**; the decision is
recorded through mechanisms that are already legal.

When Aaron takes `D-ETF-COUNT`, record it in all three of these, in this order:

1. **This file is the authoritative record.** Append a row to §7 carrying the
   decision, the option adopted, **Aaron's verbatim words**, and the date. Then
   restate the resulting convention in §3.2, replacing its
   `UNKNOWN_PENDING_AARON_DECISION` with the decided convention and citing the
   §7 row. This file is a durable, hash-pinned governance artifact — it is
   exactly the "owner-decision record mechanism" the schema leaves to the
   project, and it needs no enum value to hold a decision.
2. **Re-pin this file in `qros-state.yaml`.** Update the `trial_ledger` entry's
   `observed_sha256` in `inputs[]` to the new hash. That is the mechanical
   binding that makes the decision part of the declared state; without it the
   runtime reports the input `STALE` and the decision is not bound.
3. **Update `trial_accounting.value_anchor`** in `qros-state.yaml` — a
   free-valued DECLARED field, already the declared pointer to this ledger's
   headline values — so the ETF clause names the decided convention instead of
   `UNKNOWN_PENDING_AARON_DECISION (D-ETF-COUNT)`. `trial_accounting.canonical_ref`
   already points here and does not change.

Optionally, `session_log[]` may record that the decision was received, since its
fields are free-valued. It is a log, not the record, and it never substitutes for
step 1.

**The decision is NOT taken here.** It remains
`UNKNOWN_PENDING_AARON_DECISION` / `D-ETF-COUNT` until Aaron resolves it
separately, and the fail-closed operational state in the paragraph above governs
until then.

---

## §5 Cross-project shared-sample governance (the Databento panel)

**The rule (Program v2 §0B, verbatim):** *"Exposure and attempts travel with the
sample, not the folder. One authoritative dataset-level record, with project
references, is the shared source; project-level files are views or linked
records, never competing totals."*

### §5.1 How the rule is satisfied today

| Element | Implementation |
|---|---|
| **The one authoritative dataset-level record** | `commodity-carry-research/preregistration/PREREGISTRATION.md` §10, with its code anchor `commodity-carry-research/src/config.py:66`. It is frozen at `N_trials = 14` and carries the counting convention. **It already exists; this program does not create a rival.** |
| **Project references (views)** | `commodity-carry-research` (originator) · `c1-drag-audit/SAMPLE_REUSE.md` (measurement-only, ledger deliberately not extended) · `mean-reversion-research/protocol/SAMPLE_REUSE.md` KB-1/KB-1a (strict-subset symbols, identical period, same files) · **this file §3.1 and `research/extensions/SAMPLE_REUSE.md` KB-2** (TSMOM-EXT). |
| **Lineage does not reset at a folder boundary** | Stated and binding: a TSMOM constructed series on this panel appends to the **carry study's** frozen convention, and its DSR consequence is the carry study's consequence. Moving the work into `multi-asset-tsmom-research/` changes nothing. |
| **No competing totals** | This file **asserts no total of its own** for the Databento panel. It records TSMOM-EXT's contribution (currently **0**) against the authoritative count of 14. |

### §5.2 What is NOT settled — recorded, not invented

> **RESOLVED 2026-09-09 — `SHARED_LEDGER_PHYSICAL_HOME = DISTRIBUTED_EXISTING_FORM`.**
> Aaron adopted the arrangement already described in §5.1 rather than creating a
> new physical file. The carry PREREGISTRATION §10 record remains the single
> authoritative dataset-level anchor at `N_trials = 14`; this file §3.1/§6.1 is
> the authoritative **TSMOM prospective append view**, curated by the X01
> executing/governance session; the other project files remain **views**. **No
> KB registry CSV was created and no KB schema was invented.** The paragraph
> below is retained as the pre-decision record.

**`SHARED_LEDGER_PHYSICAL_HOME = UNKNOWN_PENDING_AARON_DECISION`** *(superseded by the box above)*.

No single physical file currently sits above all four projects. The authority is
distributed: the carry preregistration holds the count, and each consumer holds a
view. That satisfies the *rule* (one authoritative record, project references) but
not necessarily its most convenient *form*.

Creating a physical shared ledger inside `multi-asset-tsmom-research/` was
**deliberately not done**, because it would make TSMOM-EXT the owner of a record
governing `commodity-carry-research` and `mean-reversion-research` — which is
precisely the "competing total" the rule forbids, and it would be a write into
two other programs' governance surface that no Wave-0 authorisation covers.

**For Aaron, when convenient (not a Wave-0 blocker):** whether to create a
workspace-level shared record (candidate home: the knowledge base, whose
`relationships.csv` and dataset cards already own dataset-level facts), and who
curates it. Until then the distributed form above governs.

### §5.3 Family separation, stated explicitly

**Mean Reversion remains a SEPARATE alpha / research family.** It is **not**
combined with TSMOM. No MR research is run and no MR strategy design is altered
by this program. The only thing shared is the **sample**, and sharing a sample is
a governance fact, never a merger of research families.

---

## §6 VARIANT_ATTEMPT and HYPOTHESIS_FAMILY registers

### §6.1 VARIANT_ATTEMPT register

| # | attempt | sample | design parent | family | `N_trials` contribution | convention cited |
|---|---|---|---|---|---|---|
| — | *(still empty after Wave 1)* | | | | | |
| 1 | A1 (primary) | `dataset.databento.commodity-futures-curves` | X01 (sealed preregistration) | `F-X01` | +1 | carry PREREGISTRATION.md §10 - one trial per distinct constructed strategy-return series, diagnostics excluded; TRIAL_LEDGER §3.1; registered by run X01-RUN-0001 |
| 2 | S1 (construction sensitivity) | `dataset.databento.commodity-futures-curves` | X01 A1 | `F-X01` | +1 | carry PREREGISTRATION.md §10 - one trial per distinct constructed strategy-return series, diagnostics excluded; TRIAL_LEDGER §3.1; registered by run X01-RUN-0001 |
| 3 | S2 (roll-rule sensitivity) | `dataset.databento.commodity-futures-curves` | X01 A1 | `F-X01` | +1 | carry PREREGISTRATION.md §10 - one trial per distinct constructed strategy-return series, diagnostics excluded; TRIAL_LEDGER §3.1; registered by run X01-RUN-0001 |
| 4 | E (ETF reference leg) | `dataset.yfinance.multi-asset-etf-panel` | X01 (sealed preregistration) | `F-X01` | +1 | TRIAL_LEDGER §6.1 planned register - §4 conservative, separate sample; the ETF panel has no frozen convention (§3.2); registered by run X01-RUN-0001 |

**PLANNED, NOT CREATED (2026-09-09).** The X01 pre-execution gate declares
what *will* be registered when execution is later authorized. **These rows do not
exist yet and must not be created until each configuration is actually
evaluated:**

| planned attempt | sample | family | planned contribution |
|---|---|---|---|
| **A1** (primary) | `dataset.databento.commodity-futures-curves` | `F-X01` | +1 |
| **S1** (construction sensitivity) | same | `F-X01` | +1 |
| **S2** (roll-rule sensitivity) | same | `F-X01` | +1 |
| **E** (ETF reference leg) | `dataset.yfinance.multi-asset-etf-panel` | `F-X01` | **+1** (§4, conservative; separate sample) |

**Building the runner creates no attempt row.** An attempt row is created when a
configuration is **evaluated**, and nothing has been evaluated.

**No TSMOM-EXT variant attempt has been evaluated, including in Wave 1.** `X01`–`X46` are
**proposed candidates**, not attempts: an attempt row is created when a
configuration is actually **evaluated**, not when it is written down. All 46 are
`PROPOSED` in `DASHBOARD_v2.md`.

The historical ETF work (`EXPOSURE_LEDGER.md` rows 1–7) consists of **frozen
historical attempts of other research paths**, recorded there and governed by
§3.2 / §4. They are deliberately **not** transcribed into this register, which
would create a second competing account of them.

### §6.2 HYPOTHESIS_FAMILY register

| # | family | declared at | members / cells | multiplicity treatment | status |
|---|---|---|---|---|---|
| 1 | **`F-VRP`** | `research/extensions/vrp/VRP_PREREGISTRATION.md` §S, sealed 2026-09-14 (SHA256 `dd582244…53e6`); appended here at S2 acceptance, **before any member has run** | **VRP-A** (primary, the one governed Stage-A attempt) · **VRP-B** (primary, conditional on VRP-A = SUPPORTED) · **VRP-DESC R1–R14** (`PROMOTION_POWER = NONE`) | **No automatic +1 per attempt.** VRP-DESC members are not attempts and never enter `N_trials`. Precedence is by level (§B): a Level-1/Level-2 failure precedes the governed run and spends no trial. | **VRP-A HAS RUN ONCE** (2026-09-14, `VRP-STAGE-A-RUN-0001`, state UNRESOLVED / Class 3). `STAGE_A_TRIAL_SPENT = YES`, `STAGE_B_TRIAL_SPENT = NO`. VRP-B is conditional on VRP-A = SUPPORTED and, under §O, never runs on this historical result. VRP-DESC R1–R5, R12–R14 revealed with the primary; R6–R11 not computed. |
| 2 | **`F-TA`** | `research/extensions/ta/TA_PREREGISTRATION.md` §J, sealed 2026-09-15; appended here at the seal, **before any member has run** | **TA-PRIMARY** — TLT combined `AC_NET` (the ONE primary member, m = 1) · **TA-SECONDARY** — IEF combined `AC_NET` (`PROMOTION_POWER = NONE`, **no rescue power**) · **TA-DIAG** — SHY maturity gradient (`PROMOTION = KILL = DAMAGE = NONE`), SPY broad calendar placebo (`PROMOTION = NONE`, `DAMAGE = YES`), the macro/QRA adjusted specification (`PROMOTION = NONE`, `DAMAGE = YES`), leave-one-year-out (`PROMOTION = NONE`, `DAMAGE = YES`) · **TA-DESC D1–D9** (`PROMOTION_POWER = NONE`) | **m = 1; NO multiplicity correction**, because no selection across cells occurs — the verdict is read off the designated primary cell. **No automatic +1 per attempt.** Diagnostics and descriptives are not attempts and never enter `N_trials`; no diagnostic may become an additional shot on goal. A Level-1 or Level-2 failure (`TA_PREREGISTRATION.md` §P) precedes the governed run and spends no trial; a governed run spends its trial whatever the class | **NOTHING HAS RUN.** `TA_PRIMARY_TRIAL_SPENT = NO`. No `AC`, interval, Sharpe or bootstrap statistic exists. `N_trials` on the ETF panel is **NOT ASSERTED** — `D-ETF-COUNT` stays `UNKNOWN_PENDING_AARON_DECISION`, and the sealed design needs no DSR |


**This is the first declared family in this programme**, and it is declared on exactly the
condition the register already states below: TSMOM-VRP-01 has a **sealed** preregistration,
and the family is appended **before its first member runs**. Nothing about the
no-preregistration position for the pre-VRP candidates changes.

**For every other candidate, no family is declared, because a family is declared
in a preregistration before its first member runs, and no preregistration exists**
(`PREREG_SEALED=N/A`). Program v2 §11 carries the **reconciled family map** —
the planned grouping for each candidate, including the `F-X18`/`F-X39` grouping
question and the `F-X19`/`F-X20` counting choice. That map is **architecture**,
not a declaration: a family becomes declared only when its preregistration is
sealed, and it is appended here at that point.
| 3 | **`F-BENB`** | `research/extensions/benb/BENB_PREREGISTRATION.md` §I, sealed 2026-09-15; appended here at the seal, **before any member has run** | **BENB-PRIMARY** — HYG `beta_T`, the tradable next-session (open→close) convergence coefficient on discount-only observations (the ONE primary member, m = 1) · **BENB-DIAG** — `beta_O` overnight price discovery and `beta_N` NAV catch-down, both `PROMOTION_POWER = NONE` and explicitly unable to rescue `beta_T` · **BENB-GATE2** — the fixed-unit trade economics (mean NET_TRADE_RETURN and the calendarised Sharpe), a CONDITIONAL second gate on the same primary lineage, not another discovery shot · **BENB-SECONDARY** — LQD replication (`PROMOTION_POWER = NONE`, **no rescue power**) · **BENB-DESC** — the premium side and every descriptive tabulation (`PROMOTION_POWER = NONE`) | **m = 1; NO multiplicity correction**, because no selection across cells occurs — the verdict is read off the designated primary coefficient. **No automatic +1 per attempt.** Diagnostics, the secondary and descriptives are not attempts and never enter `N_trials`. A pre-run identity failure (`LEVEL-1`) precedes the governed run and spends no trial; a governed run spends its trial whatever the class | **BENB-PRIMARY HAS RUN ONCE** (2026-09-16, `BENB-RUN-20260915-01` under `BENB-AUTH-0001`, seed 1788924436, B = 10,000; class **A-M MIXED NON-HARVESTABLE CONVERGENCE**, `research_status = not_promoted`). `BENB_PRIMARY_TRIAL_SPENT = YES`. Gate 1 was NOT supported, so under the sealed §J.3 first-match-wins order the verdict terminated at STEP 1 and **BENB-GATE2 was computed and recorded but never consulted** — it is a conditional second gate on the same lineage, not another shot, and it spends no separate trial. BENB-DIAG (`beta_O`, `beta_N`), BENB-SECONDARY (LQD) and BENB-DESC were reported with the primary and promoted nothing. `N_trials` on the ETF panel is still **NOT ASSERTED** — `D-ETF-COUNT` stays `UNKNOWN_PENDING_AARON_DECISION`, and the sealed design needs no DSR |
| 4 | **`F-MMV`** | `research/extensions/mmv/MMV_PREREGISTRATION.md` §M, sealed 2026-09-17 (SHA256 `4bad9f0bcdb7e4991ab920d12e24a60f4d237205e5a43af693a8dadadb56b225`), **before any member ran**; TRANSCRIBED here late, at the S3 run of 2026-09-17 — see the disclosure note below | **MMV-PRIMARY** — the CTA-EDGE-04-MMV composite monthly portfolio return through the sealed Gate 1 (the ONE primary member, m = 1) · **MMV-GATE2** — M1 net mean and M2 net annualised Sharpe, a CONDITIONAL second gate on the same primary lineage, not another discovery shot · **MMV-GATE05** — the PnL-free position-level separability screen, which can KILL but can never promote and touches no return · **MMV-DIAG** — per-leg and per-instrument directions, first-release concordance, turnover and undefined-cell counts, all `PROMOTION_POWER = NONE` and `RESCUE_POWER = NONE` | **m = 1; NO multiplicity correction**, because no selection across cells occurs — the verdict is read off the designated composite. **No automatic +1 per attempt.** Gate 0.5 is a PnL-free screen and spends NO return trial; the Gate-2 metrics are conditional on the same lineage and spend no separate trial; diagnostics are not attempts. A structural stop before a return is produced spends nothing | **MMV-PRIMARY HAS RUN ONCE** (2026-09-17, `MMV-S3-20260917-01` under `MMV-AUTH-0002`, seed 1963028087 derived from the S1 seal-manifest hash, B = 10,000, 214 eligible return months). `MMV_PRIMARY_RETURN_TRIAL_SPENT = YES`. **CORRECTED 2026-09-17 under MMV-OD-8 = B_EXCLUDE (`MMV-S3-REPAIR-20260917-01`, `MMV-AUTH-0003`), `TRIAL_COUNT_INCREMENT = 0`, m UNCHANGED at 1.** The original run `MMV-S3-20260917-01` is **`INVALID_PRIMARY_SAMPLE` / `NONDECISIONAL`**: it included one partial terminal return observation, the row labelled 2026-06-30, whose data terminate 2026-06-12, contrary to `LOCKBOX_PROCEDURE.md` §2.1, which was written 2026-09-08 and so was PRE-EXISTING at the seal. Its Gate-1, M1, M2 and terminal class are **no longer programme evidence**; its artifacts are preserved immutably for provenance and were not edited. **These are the SAME trial, not two results**, and must never be presented as independent evidence. The DECISIONAL result is the corrected one on **213** eligible return months (2008-09-30..2026-05-31): Gate 1 was NOT supported — the 95 % interval for the mean monthly gross return SPANS ZERO (`+0.00014275`, 95 % `[-0.00428624, +0.00420283]`) — so under the sealed §K first-match order, applied FROM SCRATCH rather than carried forward, the verdict terminated at **CLASS D PREDICTIVE RESPONSE UNRESOLVED**, `PROGRAMME_STATUS = UNRESOLVED / LOW_POWER`, terminal. M1 and M2 were computed on the same draw set and recorded; neither can rescue a Gate-1 that did not pass. MMV-GATE05 ran earlier under `MMV-AUTH-0001` (1313/3270 = 40.152905 %, PASS, no kill) and spent NO return trial. The first-release concordance diagnostic was never run. `N_trials` on the ETF panel is still **NOT ASSERTED** — `D-ETF-COUNT` stays `UNKNOWN_PENDING_AARON_DECISION`, and the sealed design uses no DSR and no trial-count deflation |
| 5 | **`F-F6`** | `research/extensions/f6/F6_S1_PREREGISTRATION_SEALED.md` §9/§10/§12, sealed 2026-09-21 (SHA256 `f26df71d4596dd8cacd261e571040b5b0e39fd37ef897c87422af31eeef275d9`), `SEAL_ID = CTA-EDGE-05-F6-S1-2026-09-21`; appended here **at the seal, before any member has run** | **F6-PRIMARY** — the CTA-EDGE-05 / F6 pooled scheduled-announcement-day SPY rule judged through the sealed P1 + P2 + P3 conjunction on the 462 archive-eligible event sessions (the ONE primary member, m = 1) · **F6-DIAG** — per-family FOMC / CPI / NFP summaries, permitted only where already adopted by Owner authority, all `PROMOTION_POWER = NONE` and `RESCUE_POWER = NONE` | **m = 1; NO multiplicity correction**, because no selection across cells occurs — the verdict is read off the single designated P1/P2/P3 conjunction via the sealed §12 terminal table. **No automatic +1 per attempt.** P3 is a leave-one-calendar-year veto on the SAME lineage, not another shot on goal, and spends no separate trial; diagnostics are not attempts and never enter `N_trials`. TLT, F6.b, F6.c and 2026 are excluded from outcome computation entirely and constitute no members | **NOTHING HAS RUN. `F6_FAMILY_STATUS = SEALED / NOT EXECUTED`.** `F6_PRIMARY_TRIAL_SPENT = NO`. No P1 mean, no `beta_EVENT`, no interval, no bootstrap statistic, no LOYO quantity and no result artifact exists; the seal transaction was outcome-blind and read no SPY price value. Bootstrap frozen pre-outcome at B = 100,000 over 15 calendar-year blocks 2011–2025, seed **2540719150** derived from `SHA256("CTA-EDGE-05|F6|S1_BOOTSTRAP|" + FINAL_EVENT_MANIFEST_SHA256)` — metadata, never returns. `SAMPLE_REUSE_CLASS = T0_REUSED_DEPENDENT`, `EVIDENCE_CEILING = SUPPORTED`, `INDEPENDENT_CONFIRMATION = NO`. `N_trials` on the ETF panel is still **NOT ASSERTED** — `D-ETF-COUNT` stays `UNKNOWN_PENDING_AARON_DECISION`, and the sealed design uses no DSR and no trial-count deflation |

**Appended 2026-09-17 (CTA-EDGE-04-MMV S3 run) — LATE TRANSCRIPTION, disclosed rather than hidden.** `F-MMV` is the programme's **fourth** declared family. Its declaration is the sealed MMV preregistration §M of 2026-09-17, which fixed `PRIMARY TRIAL FAMILY = CTA-EDGE-04-MMV composite, m = 1` **before any member ran**; the seal, not this row, is the authority. The row itself was **not** appended at the S1 seal and is being written here at the S3 run, after the primary result exists. That is a transcription delay and it is recorded as one.

**Appended 2026-09-21 (CTA-EDGE-05 / F6 S1 seal) — ON TIME, at the seal.** `F-F6` is the
programme's **fifth** declared family, and it is declared on exactly the condition the
register states: a **sealed** preregistration, appended **before its first member runs**.
Unlike `F-MMV`, this row is **not** a late transcription — it is written as part of the same
atomic seal transaction that created the sealed contract, which is why no disclosure of a
transcription delay is needed here.

The declaring authority is the sealed preregistration at the hash in the row above, not this
row. A reader who doubts the membership, the `m = 1` treatment or the frozen bootstrap
settings should verify that file against its pinned SHA256 rather than take this row's word
for it.

The BH-FDR standing default below is **not** applied to `F-F6`, which has `m = 1` and no
selection across cells. No existing row or paragraph was edited, deleted or reordered.


It is **not** a post-hoc family construction, which §1.1 prohibition 2 forbids: nothing about the membership, the multiplicity treatment or `m = 1` was decided after seeing a result, and every element above is readable in the sealed contract at its pinned hash. A reader who doubts that should verify §M against `4bad9f0bcdb7e4991ab920d12e24a60f4d237205e5a43af693a8dadadb56b225` rather than take this row's word for it.

The BH-FDR standing default below is **not** applied to `F-MMV`, which has `m = 1` and no selection across cells. No existing row or paragraph was edited, deleted or reordered.



**Appended 2026-09-15 (CTA-EDGE-01-TA S1 seal) — reading note; no existing row or
paragraph was edited.** The two paragraphs above were written when `F-VRP` was the only
declared family and are left exactly as they were. Read them as describing `F-VRP`: it
is the **first** declared family, and **`F-TA` is the second**, declared on the same
condition — a sealed preregistration, appended before any member has run. "For every
other candidate, no family is declared" now means *every candidate other than
TSMOM-VRP-01 and CTA-EDGE-01-TA*. The no-preregistration position for the pre-VRP
candidates is unchanged. The BH-FDR standing default below is **not** applied to
`F-TA`, which has `m = 1` and no selection across cells.

**Standing multiplicity default:** BH-FDR q = 0.10, carried as a **challengeable
default**, not a decided rule (Program v2 §0 rule 5).

**Soft workload budget** (Program v2 §0 rule 10): eight FULL preregistrations in
the first twelve months, exceeding which needs Aaron's approval. **It is a
workload budget and explicitly not a multiplicity correction**; it never enters
`N_trials`.

---

## §7 Append log

| Date (UTC) | Appended | By |
|---|---|---|
| 2026-09-19 | **F4 `INVENTORY_STATE_COMMODITY_CURVE` PARKED PRE-OUTCOME — nothing was spent and nothing moved.** The `CTA-EDGE-05` slot ran a PRE-S0 review and an S0 **data-PIT feasibility audit only**; it is now **`PARKED_PRE_OUTCOME`**, reason `LOAD_BEARING_NG_STATE_NOT_PIT_RECONSTRUCTIBLE`. **F4 NEVER ENTERED TRIAL ACCOUNTING**: no `F-F4` `HYPOTHESIS_FAMILY` was ever declared in §6.2, no `VARIANT_ATTEMPT` row exists, the primary return family was never executed and **no F4 return outcome was ever accessed**. The PnL-free premise was never run and no TIGHT/AMPLE label, inventory deviation, stocks-to-use, basis or trend return was ever computed. **This row adds NOTHING to any count** — it exists so a future reader searching this ledger for F4 finds a definitive *never entered*, following the `CTA-EDGE-01-TA CLOSED PRE-OUTCOME` and F7 precedents. **No register row was created, edited, deleted or reordered**; §3.2 / §3.3 are untouched, `N_trials` stays **NOT ASSERTED** and `D-ETF-COUNT` stays `UNKNOWN_PENDING_AARON_DECISION`. Input inventory values read during the audit are **`DESIGN_INFORMING_MEASUREMENT`** only and are recorded as a `NO_OUTCOME` row in `ops/EXPOSURE_LEDGER.md`; **no return exposure was manufactured**. This is **not** a falsification of F4, of storage theory or of trend conditionality. Record: `research/extensions/f4/F4_PREOUTCOME_PARK_CLOSEOUT.md`. | F4 pre-outcome park closeout session (Claude Opus 5), under the controller's PARK disposition relayed by Aaron |
| 2026-09-18 | **F7 `REBALANCING_FLOW_REVERSAL` CLOSED AS A NON-RUN CANDIDATE — nothing was spent and nothing moved.** The proposed lineage `CTA-EDGE-05-RFR` was **never opened**. **F7 NEVER ENTERED TRIAL ACCOUNTING AT ALL**: no `F-RFR` `HYPOTHESIS_FAMILY` was ever declared in §6.2 (the 2026-09-16 candidate audit records *“No family declared yet”*), no `VARIANT_ATTEMPT` row exists, no historical return run was executed and **no F7 outcome of any kind was ever accessed**. So there is not even a reservation to distinguish from an execution. **This row adds NOTHING to any count** — it exists so a future reader searching this ledger for F7 finds a definitive *never entered* rather than ambiguous silence, following the `CTA-EDGE-01-TA CLOSED PRE-OUTCOME` precedent of 2026-09-15. **No register row was created, edited, deleted or reordered** and §3.2 / §3.3 are untouched: `N_trials` on the ETF panel stays **NOT ASSERTED** and `D-ETF-COUNT` stays `UNKNOWN_PENDING_AARON_DECISION`. **No exposure row was written either** — an `EXPOSURE_EVENT` is a computation or read that reveals outcomes or measurements, and F7 produced neither, so by §1's own definition there is no event to record. Disposition: F7 is **preserved as a mechanism-study candidate**, removed from the active edge queue, with `CTA-EDGE-05` **not assigned to it**; its return outcome remains **UNEXPOSED and unspent**. Record: `research/extensions/F7_NONRUN_DISPOSITION.md`. This is **not** a falsification of F7 and **not** a finding about its profitability. | F7 non-run closeout session (Claude Opus 5), under the programme controller's F7 disposition relayed by Aaron |
| 2026-09-17 | **CTA-EDGE-04-MMV CLOSED — no further trial spent.** The accepted verdict is **TERMINAL CLASS D PREDICTIVE RESPONSE UNRESOLVED**, `PROGRAMME_STATUS = UNRESOLVED / LOW_POWER`, `research_status = unresolved`, `FAILURE_TYPE = INSUFFICIENT_EVIDENCE / LOW_POWER`. **NOTHING MOVED**: `F-MMV` stays at **m = 1**, `MMV_PRIMARY_RETURN_TRIAL_SPENT` stays `YES` from the one governed run (spent once, corrected once, counted once), the correction spent **0** and created no `m = 2`, and M1/M2 were computed on the same draw set but **NOT CONSULTED** for promotion classification once class D became terminal at Gate 1 — the `F-BENB` Gate-2 precedent exactly — so they spend no separate trial. The first-release concordance diagnostic was **NEVER RUN** at any stage and is now permanently closed; it carried `PROMOTION_POWER = NONE` and `RESCUE_POWER = NONE`. `N_trials` on the ETF panel is still **NOT ASSERTED** and `D-ETF-COUNT` is still `UNKNOWN_PENDING_AARON_DECISION` — closing a lineage decides nothing about the count. `RESCUE_AUTHORIZED = NO` and no second run of any kind is authorized: alternate series, transforms, mappings, thresholds, costs, bootstraps, endpoints, component selection and a longer sample are all prohibited within this lineage, and any materially different future study needs a NEW family declared in a NEW preregistration before its first member runs. **No existing row was edited, deleted or reordered.** | CTA-EDGE-04-MMV final closeout session (Claude Opus 5), under the programme controller's accepted verdict |
| 2026-09-17 | **CTA-EDGE-04-MMV S3 PRIMARY-SAMPLE CORRECTION (MMV-OD-8 = B_EXCLUDE).** §**6.2** `F-MMV` status cell updated IN PLACE — the `F-BENB` precedent of 2026-09-16 and the `F-VRP` precedent of 2026-09-14 — to record that the original run `MMV-S3-20260917-01` is **`INVALID_PRIMARY_SAMPLE` / `NONDECISIONAL`** and that the decisional result is the corrected `MMV-S3-REPAIR-20260917-01` under `MMV-AUTH-0003`. **NOTHING WAS SPENT AND NOTHING WAS ADDED**: `TRIAL_COUNT_INCREMENT = 0`, **m stays 1**, no `m = 2` was created, no new family was declared, and no `VARIANT_ATTEMPT` row exists — a correction of an invalid sample is the SAME primary trial recomputed, **not** a second evaluation and **not** independent evidence. Reason: the original run included ONE partial terminal return observation (the row labelled 2026-06-30, data ending 2026-06-12) contrary to `LOCKBOX_PROCEDURE.md` §2.1, written 2026-09-08 and therefore pre-existing at the 2026-09-17 seal, which requires an evaluation either to truncate the terminal row and say so or to declare its inclusion in the preregistration; the sealed contract does neither, so truncation binds. `NEW_SCIENTIFIC_CHOICE = NO`. The corrected sample differs from the original by **exactly one row** — removed {2026-06-30}, added none — verified mechanically, with 14 files checked byte-identical to the parent-run commit and the parent's statistics reproduced bit-for-bit from the corrected run's own book. The corrected terminal class is **D PREDICTIVE RESPONSE UNRESOLVED**, classified FROM SCRATCH. **Gate 0.5 was NOT rerun** and its accepted 1313/3270 = 40.152905 % PASS stands; the 218-date decision grid is unaltered. **§3.2 / §3.3 untouched and no `N_trials` figure asserted**: `D-ETF-COUNT` stays `UNKNOWN_PENDING_AARON_DECISION`. Databento, VIX and the TA/BENB references untouched. **No existing row was deleted, merged or reordered**; only the `F-MMV` status cell was updated in place. | CTA-EDGE-04-MMV S3 correction session (Claude Opus 5), under the programme controller's PRIMARY-SAMPLE CORRECTION authorization relayed by Aaron |
| 2026-09-17 | **CTA-EDGE-04-MMV S3 primary historical return run.** §**6.2** appended: **`F-MMV`**, the programme's **fourth** declared `HYPOTHESIS_FAMILY`, declared in the sealed preregistration §M before any member ran and **transcribed here late, at the run** — the delay is disclosed in the note under the row, and nothing about the family was decided after seeing a result. Status recorded as **`MMV_PRIMARY_RETURN_TRIAL_SPENT = YES`**: the sealed composite primary ran ONCE under `MMV-AUTH-0002` (`MMV-S3-20260917-01`, seed 1963028087 derived from the S1 seal-manifest hash, B = 10,000, 214 eligible return months) and spent its governed return trial; the sealed class is **D PREDICTIVE RESPONSE UNRESOLVED**, `PROGRAMME_STATUS = UNRESOLVED / LOW_POWER`, terminal. M1 and M2 were computed on the same draw set and recorded but cannot rescue a Gate 1 that did not pass. **The earlier Gate 0.5 run spends NO return trial and is NOT counted as one** — it was a PnL-free position-separability screen that touched no return (`MMV-AUTH-0001`, 1313/3270 = 40.152905 %, PASS). **§3.2 / §3.3 untouched and no `N_trials` figure asserted**: the ETF panel has no frozen convention, `D-ETF-COUNT` stays `UNKNOWN_PENDING_AARON_DECISION`, and the sealed MMV design uses no DSR and no trial-count deflation. The first-release concordance diagnostic was never run. Databento, VIX and the TA/BENB references untouched. **No existing row was edited, deleted or reordered.** | CTA-EDGE-04-MMV S3 governed-run session (Claude Opus 5), under the programme controller's ONE-TIME PRIMARY HISTORICAL RETURN RUN AUTHORIZATION relayed by Aaron |
| 2026-09-16 | **CTA-EDGE-02-BENB CLOSED — no further trial spent.** The accepted S4 verdict is **Class A-M**, `research_status = not_promoted`. **Nothing moved**: `BENB_PRIMARY_TRIAL_SPENT` stays `YES` from the 2026-09-16 governed run, Gate 2 remains a conditional second gate that was computed but not consulted and spends no separate trial, and the diagnostics / LQD secondary / descriptives remain non-attempts. `N_trials` on the ETF panel is still **NOT ASSERTED** and `D-ETF-COUNT` is still `UNKNOWN_PENDING_AARON_DECISION` — closing a lineage decides nothing about the count. `RETUNE_AUTHORIZED = NO` and `SECOND_RUN_AUTHORIZED = NO`: the persistent 80.52 % discount-side state is recorded as a feature-design lesson and any hypothesis built on it needs a NEW family declared in a NEW preregistration before its first member runs. **No existing row was edited, deleted or reordered.** | CTA-EDGE-02-BENB S4 closeout session (Claude Opus 5), under the programme controller's accepted verdict |
| 2026-09-16 | **CTA-EDGE-02-BENB S3 governed historical run.** §**6.2** updated: `F-BENB` status **`BENB_PRIMARY_TRIAL_SPENT` NO → YES** — the sealed HYG `beta_T` primary ran ONCE under `BENB-AUTH-0001` (`BENB-RUN-20260915-01`, seed 1788924436 derived from the S1 seal-manifest hash, B = 10,000) and spent its governed trial; the sealed class is **A-M**, `research_status = not_promoted`. **§3.2 / §3.3 untouched and no `N_trials` figure asserted**: the ETF panel has no frozen convention and `D-ETF-COUNT` stays `UNKNOWN_PENDING_AARON_DECISION`; the sealed BENB design uses no DSR and no trial-count deflation, so nothing here decides it. Gate 2 was computed but not consulted (Gate 1 failed first) and spends no separate trial. Databento, VIX and the CTA-EDGE-01-TA references untouched. **No existing row was deleted, merged or reordered**; the `F-BENB` status cell was updated in place, exactly as the `F-VRP` precedent of 2026-09-14. | CTA-EDGE-02-BENB S3 governed-run session (Claude Opus 5), under the Owner execution decision relayed by Aaron |
| 2026-09-15 | **CTA-EDGE-02-BENB S1 seal.** **§6.2** appended: **`F-BENB`**, the programme's **third** declared `HYPOTHESIS_FAMILY`, declared from the sealed BENB preregistration **before any member has run**; **m = 1** on the HYG `beta_T` tradable-convergence coefficient, with `beta_O`, `beta_N`, the Gate-2 economics, the LQD replication and the premium side all carrying explicit declared powers and none able to promote or rescue. **Nothing was spent**: no governed run, no scientific outcome generated or revealed, `D-ETF-COUNT` still OPEN and **no `N_trials` figure asserted**; Databento, VIX and the CTA-EDGE-01-TA references untouched. **No existing row was edited or reordered.** | CTA-EDGE-02-BENB S1 seal session (Claude Opus 5), under the controller's S1 SEAL-COMPLETION authorisation and Aaron's BENB-OD-1 |
| 2026-09-15 | **CTA-EDGE-01-TA CLOSED PRE-OUTCOME.** The lineage is closed by controller decision before any governed run: the sealed §G.3 identification diagnostic is mechanically NOT_EVALUABLE (reference group 7 < sealed minimum 20), so Class D was structurally unreachable before any historical ETF outcome was opened. **NOTHING WAS SPENT**: `F-TA` was declared before any member ran and **no member ever ran**; `TA_PRIMARY_TRIAL_SPENT` stays **NO**; no `AC`, interval, Sharpe or bootstrap statistic exists; `D-ETF-COUNT` remains `UNKNOWN_PENDING_AARON_DECISION`; Databento and VIX references untouched. The §6.2 `F-TA` row is **not edited** — its status column already reads NOTHING HAS RUN and that remains true. **No existing row was edited or reordered.** | CTA-EDGE-01-TA closeout session (Claude Opus 5), under the controller's CLOSED PRE-OUTCOME decision |
| 2026-09-15 | **CTA-EDGE-01-TA S1 seal.** **§6.2** appended: **`F-TA`**, the programme's **second** declared `HYPOTHESIS_FAMILY`, declared from the sealed CTA-EDGE-01-TA preregistration **before any member has run**; **m = 1** on the TLT primary, with every secondary, diagnostic and descriptive carrying an explicit declared power and none able to promote. **Nothing was spent**: no governed run, no scientific outcome generated or revealed, `D-ETF-COUNT` still OPEN and **no `N_trials` figure asserted** for the ETF panel, Databento and VIX references untouched. **No existing row was edited or reordered.** | CTA-EDGE-01-TA S1 design/seal session (Claude Opus 5), Main Agent, under the controller's S1 DESIGN + PRE-SEAL REPAIR + CONDITIONAL SEAL authorisation |
| 2026-09-14 | **TSMOM-VRP-01 S3 governed Stage-A run.** §3.3 updated: `dataset.cboe.vix-futures-monthly-chain` **`N_trials` 0 → 1**; the sealed Stage-A primary ran ONCE under `VRP-AUTH-0001` and spent its governed trial on construction. §6.2 updated: `F-VRP` member **VRP-A has run**, state **UNRESOLVED / Class 3**. **`STAGE_B_TRIAL_SPENT` stays NO** — Stage B did not run and, under the sealed §O stop rule, never runs on this historical result. Bootstrap replicates and the revealed descriptives (R1–R5, R12–R14, `PROMOTION_POWER = NONE`) increment nothing. Databento and ETF frozen references untouched. **No existing row was edited or reordered.** | TSMOM-VRP-01 S3 run session (Claude Opus 5), implementation Main Agent, under CHATGPT_FINAL_S2_ACCEPTANCE_ON_BEHALF_OF_OWNER_WORKFLOW relayed by Aaron |
| 2026-09-14 | **TSMOM-VRP-01 S2 acceptance.** **§3.3** appended: the new `dataset.cboe.vix-futures-monthly-chain` contribution row at **`N_trials` = 0**, with the programme's existing counting convention reused verbatim. **§6.2** appended: **`F-VRP`** — the programme's **first declared HYPOTHESIS_FAMILY**, declared from the sealed VRP preregistration **before any member has run** (members VRP-A, VRP-B, VRP-DESC R1–R14; no automatic +1 per attempt). **Nothing was spent**: Stage A has not run, Stage B has not run, no scientific outcome was generated or revealed, and the Databento and ETF frozen references are untouched (`D-ETF-COUNT` stays open). **No existing row was edited or reordered.** | TSMOM-VRP-01 S2 governance-closure session (Claude Opus 5), implementation Main Agent, under Aaron's `S2 BOUNDED PRE-S3 GOVERNANCE CLOSURE` |
| 2026-09-09 | **X01 pre-execution gate — owner decisions recorded.** `SHARED_DATABENTO_HOME_GATE = RESOLVED` via the **existing distributed form** (§3.1a, §5.2); **no KB registry CSV created, no KB schema invented, carry not modified**. `TSMOM_TRIAL_LEDGER_CURATOR` = the X01 executing/governance session. `D-ETF-COUNT`: historical stays **`UNKNOWN`**, forward convention **`E_COUNTS_AS_ONE_PROSPECTIVE_ATTEMPT`**, gate **`RESOLVED_FOR_X01_EXECUTION`**, effect on the Databento `+3` **`NONE`** (§4). §6.1 now names the **planned** A1/S1/S2/E rows and states they **do not exist yet**. **Anchor still 14; TSMOM contribution still 0; planned +3 still conditional; the cumulative total is read at execution and is NOT hard-coded to 17. No attempt row was created and nothing was evaluated.** | X01 pre-execution gate session (Claude Opus 5) |
| 2026-09-08 | **X01 preregistration SEALED** at seal-base revision `df5b28ab7324`. §2 index **32/21**. **A commit and a seal are not strategy-return attempts:** **no `VARIANT_ATTEMPT` was created by this operation**, and none may be. **Databento contribution remains 0; frozen reference remains 14; planned future X01 contribution remains +3** on A1, S1 and S2, still conditional on exactly those three governed constructions, with the resulting cumulative total computed **at execution** and not hard-coded to 17. Shared Databento home and `D-ETF-COUNT` remain `PRE_EXECUTION`, were **not** resolved, and **the shared ledger was not created** - the seal does not authorize any of that. | Wave-1 seal-execution session (Claude Opus 5) |
| 2026-09-08 | **X01 seal attempt — BLOCKED.** §2 index **31/20**. **Nothing changed in trial accounting:** `PLANNED_X01_CONTRIBUTION` stays **+3** on A1, S1 and S2; **a seal creates no `VARIANT_ATTEMPT` and no trial**, and none was created here - nor would one have been had the seal completed. **Databento contribution remains 0; frozen reference remains 14**; the resulting cumulative total is still computed at execution and is not hard-coded to 17. Shared Databento home and `D-ETF-COUNT` remain `PRE_EXECUTION` and were **not** resolved; **the shared ledger was not created.** | Wave-1 seal-attempt session (Claude Opus 5) |
| 2026-09-08 | **X01 four-defect A2 repair.** §2 index **30/19**. **No trial-accounting object changed:** `PLANNED_X01_CONTRIBUTION` stays **+3** on the same three governed series (primary A1, S1, S2); the repairs alter how those series are *constructed and costed*, not how many exist. No `VARIANT_ATTEMPT` row was created, deleted or merged. **Databento contribution remains 0; frozen reference remains 14.** Shared Databento home and `D-ETF-COUNT` remain `PRE_EXECUTION`. | Wave-1 four-defect A2 repair session (Claude Opus 5) |
| 2026-09-08 | **X01 owner decisions O-1/O-2/O-6 incorporated.** §2 index **29/18**. `PLANNED_X01_CONTRIBUTION` stays **+3**, conditional on exactly the three governed constructed return series (primary A1, S1, S2) and no additional evaluated construction. **Aaron adopted O-1 Option B and O-6 Option 1, so O-1 Option A and O-6 Option 2 are NEVER constructed: no series, no `VARIANT_ATTEMPT` row and no trial for either, and neither may be computed later 'as a sensitivity to compare' — that would create the post-result choice the ex-ante adoption exists to remove.** The resulting cumulative total is still **computed at execution**, not hard-coded to 17. Shared Databento home and `D-ETF-COUNT` both remain **`PRE_EXECUTION`** and neither is resolved by guess. **Databento contribution remains 0; frozen reference remains 14; no attempt row was created, deleted or merged.** | Wave-1 owner-decision incorporation session (Claude Opus 5) |
| 2026-09-08 | **§2 index corrected** from 19/9 to **27/16** research/seat rows after drifting across four repair phases, and **X01 Stage-A2 repair** recorded: the preregistration's trial wording now states `+3` conditionally with the resulting total computed **at execution** (the immutable `14 → 17` is deleted), enumerates what does and does not create a `VARIANT_ATTEMPT`, and records that the ETF leg must be **constructed**, so `D-ETF-COUNT` is **not** untouched by X01 and must be classified pre-execution. **Databento contribution remains 0; the frozen reference remains 14; no attempt row was created, deleted or merged.** | Wave-1 X01 Stage-A2 repair session (Claude Opus 5) |
| 2026-09-08 | **Wave-1 contract-identity repair.** Databento contribution **unchanged at 0**; the frozen reference stays **14**. The repair re-extracted settlement and open interest on persistent contract keys and reran the X02a/X03 mechanical checks; **no strategy-return series was constructed**, so nothing contributes under the verified carry convention. The **invalid raw-symbol attempt (exposure row 17) is retained and is NOT counted** as a trial contribution: it is implementation-error history, not a strategy evaluation, and no configuration was selected on any outcome. No attempt was deleted, merged or consolidated; no family was declared; no count was recomputed. | Wave-1 repair session (Claude Opus 5) |
| 2026-09-07 | **Wave-1 execution.** Databento contribution **unchanged at 0**: the Wave-1 activities (input verification, settlement/OI extraction, X02a mechanical identities, X03 structural roll diagnostics) construct **no strategy-return series**, so under the verified carry convention they contribute nothing — the `c1-drag-audit` precedent exactly. ETF panel: the X45 static-book and residual series are **decompositions of the existing book, not evaluated candidate configurations and not selection opportunities** (MAP_v2's anti-snooping rule forbids selecting on them), so **no VARIANT_ATTEMPT row is created**; their `GOVERNED_N_TRIALS_CONTRIBUTION` remains `UNKNOWN_PENDING_AARON_DECISION` under the open `D-ETF-COUNT`, failing closed rather than asserting 0. **No count was recomputed, no attempt merged or deleted, and no family declared.** The shared-Databento append home is raised as an owner decision in `research/extensions/wave1/WAVE1_PREFLIGHT.md` §7.1 **before** the first X01 contribution, not after. | Wave-1 session (Claude Opus 5) |
| 2026-09-07 | Ledger created at Wave-0 execution. Four-object model §1 with the four prohibitions; exposure index §2; per-sample `N_trials` governance §3 (Databento verified/frozen at 14, ETF `UNKNOWN`); open decision `D-ETF-COUNT` §4 with options A/B/C; shared-sample governance §5 including `SHARED_LEDGER_PHYSICAL_HOME = UNKNOWN_PENDING_AARON_DECISION`; empty attempt and family registers §6. | Wave-0 governance session (Claude Opus 5), under Aaron's `AUTHORIZE_WAVE_0_GOVERNANCE_EXECUTION` |
| 2026-09-07 | **CORRECTION — non-blocking finding NB1, raised by the fresh GPT-6 Astra Wave-0 verifier and confirmed against bytes.** §4's "where the decision gets recorded" clause directed `D-ETF-COUNT` into `qros-state.yaml`'s `human_decisions[]`, whose `type` vocabulary L6 §2.9 closes at three values that cannot represent a trial-count convention — an instruction that could not have been followed. Replaced with the three already-legal mechanisms: this file as the authoritative record (§7 row with Aaron's verbatim words, plus a §3.2 restatement), the `inputs[]` hash re-pin that binds it, and the `trial_accounting.value_anchor` update. **The canonical enum is unchanged and no new `human_decisions[].type` was invented. `D-ETF-COUNT` is NOT decided by this correction** and remains `UNKNOWN_PENDING_AARON_DECISION`. No count, no attempt row and no family row was added or altered. | Wave-0 bounded repair session (Claude Opus 5), under Aaron's bounded-repair authorization |

```
TSMOM_EXT CONTRIBUTION TO databento N_trials = 0 (carry ledger frozen at 14)
ETF PANEL N_trials = UNKNOWN_PENDING_AARON_DECISION (D-ETF-COUNT, open)
VARIANT_ATTEMPTS = 0 · FAMILIES DECLARED = 0 · SEALS = 0
```
