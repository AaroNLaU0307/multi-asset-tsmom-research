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
