# SAMPLE_REUSE.md — TSMOM-EXT-001

**Program:** TSMOM extension (`TSMOM-EXT-001`), `multi-asset-tsmom-research`
**Created:** 2026-09-07 (Wave 0 governance execution, authorised by Aaron)
**Status:** `PRE-SEAL DECLARATION — KNOWN BURNS ENUMERATED + UNKNOWN RESIDUAL`
**Governing architecture:** `TSMOM_EXTENSION_RESEARCH_PROGRAM_v2.md` §0A, §0B,
§0 rule 7 · `TSMOM_EXTENSION_RESEARCH_MAP_v2.md` §A.5

**Append-only.** Rows are never rewritten or reordered. A burn discovered later
is **appended** with its discovery date; an error is corrected by appending a row
that cites the corrected one.

**What this file is and is not.** It declares **which samples this program
consumes and what has already been spent on them**, and it fixes what each
resulting test can support. It is **not** the trial ledger:
`research/extensions/TRIAL_LEDGER.md` carries the four-object trial record, and
this file never doubles as a count.

---

## §0 The two rules this file exists to enforce

**Rule 1 — design lineage ≠ validation evidence.** They are recorded separately
and never merged (Program v2 §0A). A candidate carries *one* design-lineage tag
describing where its idea came from, and *one evidence context per validation
test* describing what that test can support. An exposed-sample origin is
**disclosed forever**; it does **not** prevent that candidate from later earning
stronger independent evidence, and dependent historical evidence is **never**
relabelled as independent.

> A candidate may therefore legitimately read
> `POST_EXPOSURE_DESIGN_ON_ETF_PANEL` + dependent ETF-panel evidence (T0) +
> same-period futures transfer evidence (T1) + later prospective confirmation
> (T4), with no implication that the T0 or T1 evidence was independent, and with
> the T0 origin not blocking the T4 confirmation.

**Rule 2 — there is no weakest-tier inheritance, and none is implemented here.**
A candidate's claim ceiling is **not** pinned to the weakest context in its
history. Each *test* is classified on its own facts, and the claim it supports
follows from **that test's** context plus the canonical vocabulary
(`TSMOM_EXTENSION_RESEARCH_PROGRAM_v2.md` §10). What the exposed origin does is
constrain claims of **independence** — not the eventual grade a genuinely
independent later test may reach.

**Explicitly not adopted:** any rule of the form "a candidate designed on an
exposed sample can never exceed *status X*", or "a family's ceiling is the
minimum over its members' contexts". Neither appears in the accepted V2
architecture, and neither is created here.

---

## §1 Evidence contexts (restated from Program v2 §0A — authoritative there)

| Context | Definition | Can support | Cannot support |
|---|---|---|---|
| **T0 — exposed design sample** | The design or hypothesis was informed by outcomes observed on this sample | Hypothesis generation; retrospective descriptive evidence; explicitly **dependent** research evidence | Independent confirmation of a newly adapted performance claim. A later seal does not erase earlier exposure. |
| **T1 — same-period wrapper / instrument replication** | Same or materially overlapping economic history, different wrapper, instrument or implementation | Wrapper transfer; implementation and construction robustness; partial external validity. A narrowly scoped implementation fact may receive whatever status the canonical vocabulary permits. | Automatic independent confirmation of an ETF-informed performance edge. `confirmed implementation_fact` never implies `confirmed` strategy performance. |
| **T2 — temporally separate historical replication** | Different historical periods | Stronger cross-period evidence when the design is fixed and researcher exposure, literature-derived design choices, construction and claim scope are disclosed | Independence by virtue of different dates alone |
| **T3 — accrued but protected historical holdout** | Data that has already occurred, with **verified** protection from outcome access | Held-out historical evidence | Prospective status. "No file was downloaded by this project" is insufficient; related-project access and outcome-informed market knowledge matter. |
| **T4 — prospective forward evidence** | Design, seal and access protocol precede the market outcomes | The strongest temporal protection available; potential confirmation subject to adequate evidence and applicable gates | Conclusiveness when the period is too short or imprecise |

---

## §2 Known burns

### KB-1 — `dataset.yfinance.multi-asset-etf-panel` (the ETF historical panel)

| Field | Value |
|---|---|
| **Panel** | 30 yfinance adjusted-close series; working snapshot `data/close_prices_raw.csv`, 1993-01-29 → **2026-06-12**, 8,400 daily rows, SHA-256 `3d2a7a56dbd92d4ff8138cfd894c87f5ac5ac088a11165db870673e0c05c3c31` (verified 2026-09-07; see `WAVE0_VERIFICATION_RECORD.md` §2). The evaluated core universe is 17 assets. |
| **Burned by** | **6 of 6** registered research paths: `strat.tsmom.multi-asset-core`, `strat.tsmom.crash-defense-overlay`, `strat.tsmom.vol-breakout-overlay`, `strat.tsmom.seasonality-overlay`, `strat.tsmom.yield-spread-overlay`, `strat.xsmom.multi-asset` |
| **Verified from bytes** | `quant-research-knowledge-base/relationships/relationships.csv` **lines 16–21**, each `must_not_be_retested_on_same_sample → dataset.yfinance.multi-asset-etf-panel` (read 2026-09-07) |
| **Relationship type** | `must_not_be_retested_on_same_sample` |
| **Frozen trial-count convention** | **NONE EXISTS.** The core had no preregistration. See `TRIAL_LEDGER.md` §4 — the historical ETF count and the 45-cell grid's counting treatment are an **open Aaron decision**, recorded there with its options and **not improvised**. |
| **This program's reuse** | **7th and subsequent.** Declared here, which is the disclosure `relationships.csv` requires. |

**Inherited constraint, verbatim from `relationships.csv` line 16:**

> "This research path has already used this 17-ETF panel, in a full-sample
> fixed-parameter analysis. This panel must not be reused as fresh independent
> confirmation, and any later analysis on it must disclose the reuse. Several
> other strategies are registered against the same dataset with the same
> relationship type; that is sample-reuse tracking, not a count of independent
> confirmations. This relationship records sample exposure only; consult the
> linked evidence cards for research conclusions."

**Consequence for this program.** Every candidate designed from the published
ETF results is **context T0 on this panel**. Results on it are **dependent
evidence**, never independent confirmation — and per §0 Rule 1 that is a
statement about *those tests*, not a ceiling on the candidate.

**What a burn does not mean** (the KB gap-map header governs the reading):
`must_not_be_retested_on_same_sample` is **not** evidence that a mechanism was
refuted, and "every registered hypothesis has touched this panel" is **not**
"every hypothesis was rejected".

---

### KB-2 — `dataset.databento.commodity-futures-curves` (the Databento commodity panel)

| Field | Value |
|---|---|
| **Panel** | Databento `GLBX.MDP3`, 18 pre-registered CME roots (parent symbology), request range `2010-06-06` inclusive → `2026-07-01` exclusive == **through 2026-06-30 inclusive**; schemas `ohlcv-1d`, `statistics`, `definition`. Corpus at `C:\Users\Aaron\quant-data\commodity-carry`, ~9.43 GB. |
| **Snapshot identity (verified 2026-09-07)** | `ohlcv-1d.dbn.zst` 107,229,003 bytes SHA-256 `333095164e55c73a150949b654a0e4c9f15636cc01ee7c93bf625e5412c59539`; `definition` aggregate SHA-256 `76da3a39a7279ef3a3b4c03ffb2646048685f715466108ca5136aee6f7922277` (5,031 files); `statistics` aggregate SHA-256 `ee7dee4dc1c2dab44df207d20d5327b0dfb7e6193c49091b8e0a52bfb489001f` (5,026 files). Source: `commodity-carry-research/data/MANIFEST.md`. |
| **Burned by** | `strat.commodity-carry.xs-ts-carry-premium` (H1 cross-sectional + H2 time-series arms; multiple-testing family m = 2; both arms `NOT_PROMOTED`) |
| **`N_trials`** | **14, frozen.** Verified from bytes: `commodity-carry-research/preregistration/PREREGISTRATION.md` §10 line 205 (2 primary + 12 robustness = 14) and `commodity-carry-research/src/config.py:66` (`N_TRIALS = 14`). |
| **Counting convention (verified)** | One trial per **distinct constructed strategy-return series** (primary and robustness arms); diagnostics of an existing series are excluded (PREREG §10 items 8–9). A deviation that adds or removes a constructed series **changes `N_trials` and forces every already-computed DSR to be recomputed** (PREREG §10 line 207, verbatim intent). |
| **Also consumed by** | `c1-drag-audit` — **cost accounting only**; the ledger was deliberately **not** extended (`c1-drag-audit/SAMPLE_REUSE.md`, read 2026-09-07). Its tripwire stands: the ledger must be extended the moment a Sharpe, CI or return series is computed on this panel. |
| **Also declared against by** | `mean-reversion-research` (`protocol/SAMPLE_REUSE.md` KB-1 / KB-1a) — a **separate alpha family**, sharing the same bytes. See §4. |
| **TSMOM status** | **No TSMOM performance trial has ever run on this panel.** The first TSMOM constructed strategy-return series appends to the trial ledger under the verified convention above. |
| **Context for this program** | **T1** for ETF-designed candidates — same 2010–2026 price paths, different wrapper and instrument. **GFC is absent** (the panel starts 2010-06). |

---

### KB-3 — Same-period wrapper / instrument evidence (the T1 relationship itself)

This row exists because the ETF↔futures relationship is a *sample-reuse fact*,
not only a design choice, and it is the single most consequential one in the
program.

| Field | Value |
|---|---|
| **What is shared** | The **economic history**, 2010-06 → 2026-06. The ETF panel and the Databento commodity panel cover materially overlapping calendar time. |
| **What differs** | Wrapper (ETF vs listed future), instrument, construction (adjusted close vs settlement + roll), cost model, and the universe (17 mixed-asset ETFs vs 18 CME commodity roots). |
| **What T1 can support** | Wrapper transfer; implementation and construction robustness; partial external validity. A narrowly scoped **implementation fact** (accounting identity, units, multipliers, causality, truncation invariance) may carry whatever status the canonical vocabulary permits — under the verified G4 set, `implementation_fact` is **not** barred from `confirmed`. |
| **What T1 cannot support** | Automatic independent confirmation of an ETF-informed performance edge. `confirmed implementation_fact` **never** implies `confirmed` strategy performance. |
| **The X01 ceiling** | The X01 paired wrapper-performance comparison is an **empirical result**, not a fact about the code, and is **not eligible for `implementation_fact`**. V2 records it at most as `supported` in context T1. Whether a sealed same-period wrapper comparison may ever be classified above `supported` is `CANONICAL_CLASSIFICATION_PENDING_VERIFICATION` — decision **D9**, for Aaron and the KB curator. It is **not** a Wave-0 blocker. |

---

### KB-4 — Historical exposed samples, in general

Everything in KB-1 and KB-2 is an **historically exposed sample**: outcomes on it
have been observed by a researcher seat and are documented in committed reports.
Consequences, stated once:

- The exposure is **permanent**. A later seal, a later fresh reviewer session, or
  a change of model does not un-expose it.
- Dependent evidence produced on it is labelled dependent **at recording time**,
  not retrospectively.
- A candidate whose *design* was informed by it carries its lineage tag forever
  (`EXPOSURE_LEDGER.md` §4 link rows L1–L3; the Map's Section C is authoritative
  per candidate).

---

### KB-5 — Accrued-but-protected holdout, and prospective forward accrual

**These are two different things and are never merged.** The full mechanics are
in `research/extensions/LOCKBOX_PROCEDURE.md`; the sample-reuse consequences are
here.

| | **T3 — accrued but protected** | **T4 — prospective forward** |
|---|---|---|
| What it is | Market history that has **already occurred** but whose protected evaluation outcomes have not been validly released | Outcomes occurring **after** the relevant design / seal / access protocol |
| ETF panel | Everything after the frozen boundary **2026-06-12** | Everything after a specific contract's seal date |
| Databento panel | Everything after **2026-06-30** | Everything after a specific contract's seal date |
| Eligible today? | **NO.** Protection is **not verified**. Exposure status of post-boundary data is `UNKNOWN_PENDING_AUTHORITATIVE_VERIFICATION` — related-project access and outcome-informed market knowledge matter, and "not downloaded by this program" is explicitly insufficient. | **NO.** No contract is sealed; `PREREG_SEALED=N/A`. |
| Consequence | Until protection is **verified**, accrued data may **not** be claimed as T3 held-out evidence. It is not thereby T4 either — **accrued history is never relabelled prospective.** | T4 begins only at a seal, per candidate, and is recorded per candidate. |

**Opening protected data is an exposure event that burns the holdout for that
claim family.** It is logged on the research axis before any result is read.

---

### KB-6 — `dataset.cboe.vix-futures-monthly-chain` (the monthly VX settlement chain)

*Appended at TSMOM-VRP-01 S2 acceptance, under the rows drafted in
`research/extensions/vrp/VRP_EXPOSURE_DISCLOSURE.md` §5. The dataset identifier is
**provisional** until it is registered in the knowledge base; registering it there is a
separate Owner decision and was not taken here.*

| Field | Value |
|---|---|
| **Panel** | Monthly VX contract-level **official daily settlements**, listing → final settlement. 268 standard monthly contracts, 274 raw Cboe official per-contract files, 2004-03-26 → 2026-09-11, 47,160 rows (46,331 carrying an official settlement). Acquired under `research/extensions/vrp/VRP_PREREGISTRATION.md` §L. Every raw file is SHA-256 pinned in `research/extensions/vrp/VRP_DATA_MANIFEST.md`; the raw bytes themselves are git-ignored under `data/vix/` and are **not** committed (Cboe personal/research use, no redistribution). |
| **Source authority** | Cboe (CFE) official, `SOURCE_AUTHORITY_LEVEL = 1 / PRIMARY`, two endpoints (the delisted-contract archive and the market-statistics historical data). **No vendor copy**, so §L's fallback-authority clause is never exercised. The price taken is the official `Settle` field — never last trade, never the Special Opening Quotation. |
| **Burned by** | `TSMOM-VRP-01` VRP-A — ONE governed Stage-A strategy-return series, constructed 2026-09-14 over 2006-09..2026-08 (240 months), `run_id` VRP-STAGE-A-RUN-0001. Revealed once. This panel is now **exposed**: it may not be reused as fresh independent confirmation of this object, and any later analysis on it must disclose the reuse. |
| **Verified from bytes** | No file matching `vix`, `vx`, `vxx` or `cboe` was tracked anywhere in this repository at the S1 seal commit `16d84545`, and no tracked `.py` referenced VIX. This discharges the disclosure's "subject to repository verification that no VIX-futures series was ever constructed here". |
| **`N_trials`** | **1**, as of 2026-09-14. Was 0 before Stage A. Under the programme's convention (one trial per distinct constructed strategy-return series with a selection opportunity; diagnostics excluded), the sealed Stage-A primary ran ONCE under `VRP-AUTH-0001` and spent its governed trial on CONSTRUCTION, whatever the state. Final state **UNRESOLVED (Class 3)**. `STAGE_A_TRIAL_SPENT = YES`. |
| **Not attempts** | Bootstrap replicates; the declared VRP-DESC family R1–R14; any sensitivity carrying `PROMOTION_POWER = NONE` (including the `c0 = 0.05` cost variant). |
| **S2 exposure** | Raw contract settlements were acquired and read for mechanical implementation and validation only — hashes, counts, date ranges, identity, calendar, roll-weight identities, specification normalisation. No return, basis, carry or strategy statistic was computed at S2. |
| **S3 exposure** | **TARGET_METRIC.** The governed Stage-A run constructed the real monthly excess-return series and its bootstrap interval, stored `GENERATED_NOT_SEEN`, then revealed ONCE under `VRP-AUTH-0002`. The Main Agent seat has now seen the revealed Stage-A evidence. Stage B was not computed. |
| **Evidence context** | **`DESIGN_INFORMED_FIRST_LOCAL_USE`** — never "fresh", never "independent". Locally unsearched (verified above); globally saturated: VIX futures are heavily studied publicly and the sign of the long-run gross carry is common knowledge. The label travels with every citation. |

**ETF-panel consequence of the same lineage (KB-1 addendum).** TSMOM-VRP-01 **Stage B** is
a paired combination of the frozen canonical net stream (months ≤ 2026-05-31, recomputed by
the pinned canonical modules per the Value contract's §17 comparator identity) with the
Stage-A sleeve in a self-financing book at `s = 0.20`. It is **context T0 on the ETF panel
— a further declared reuse (ninth-plus)**, and SPY monthly returns are used for the X46
tail rule. The frozen panel's historical count convention (`D-ETF-COUNT`,
`TRIAL_LEDGER.md` §4) is **untouched** by this declaration. Stage B is conditional on
Stage A and has **not** run: `STAGE_B_TRIAL_SPENT = NO`.

---

## §3 Residual — `UNKNOWN`, and deliberately left so

Beyond the burns enumerated in §2, this program's cumulative prior exposure is
**`UNKNOWN`**.

- **No `NONE` retro-inference.** The absence of a recorded exposure event is not
  evidence that none occurred.
- **No fabricated deflation.** No DSR, `N_trials` or other numeric deflation of
  an unknowable residual is attempted. A fabricated number would be worse than
  the disclosure, because it would look like knowledge.
- `ops/EXPOSURE_LEDGER.md` is the canonical exposure record. Its historical rows
  transcribe documented burns; everything it does not enumerate is `UNKNOWN`.

---

## §4 Cross-project coordination — the Databento panel

Three programs consume, or propose to consume, the **same bytes** at
`C:\Users\Aaron\quant-data\commodity-carry`:

| Program | Family | Relationship to the panel |
|---|---|---|
| `commodity-carry-research` | commodity carry | **Originator.** Holds the only frozen trial ledger: `N_trials = 14`, PREREG §10. |
| `mean-reversion-research` | mean reversion — **a separate alpha family; not combined with TSMOM** | Declared burn KB-1/KB-1a: its 10 proposed roots are a **strict subset** of the carry panel's 18; period **identical**; **the same files**. |
| `multi-asset-tsmom-research` (this program) | time-series momentum | Declared here. **No TSMOM trial has run.** |

**The governing rule (Program v2 §0B, verbatim):** *"Exposure and attempts travel
with the sample, not the folder. One authoritative dataset-level record, with
project references, is the shared source; project-level files are views or
linked records, never competing totals."*

**How that is implemented, without inventing a competing total:** the
**authoritative dataset-level record for this panel is, and remains, the carry
study's frozen ledger** (`commodity-carry-research/preregistration/PREREGISTRATION.md`
§10 + `src/config.py:66`). This file and `TRIAL_LEDGER.md` are **views** onto it.
A project-folder change **never** resets the lineage. The mechanism, and the open
question of whether a single physical shared file should be created and who owns
it, are set out in `TRIAL_LEDGER.md` §5.

**No mean-reversion research is run, and no MR strategy design is altered, by
this program.**

---

## §5 Consequences for claims

1. **ETF-panel tests are dependent evidence (T0).** They may be recorded, cited
   and relied on — labelled as dependent. They are never independent confirmation.
2. **Futures same-period tests are T1.** Mechanical identities may reach
   `implementation_fact` / `confirmed`; the X01 performance comparison is capped
   at `supported` pending D9.
3. **`confirmed`-grade *performance* claims require T3 or T4 evidence** — i.e. a
   verified-protected holdout or genuine prospective accrual. Neither exists today.
4. **Negatives are first-class.** Premise failure → `not_promoted`, reason
   `premise_not_confirmed`. Insufficient precision → `unresolved`. `falsified`
   only under the KB's decisiveness convention (multiple independent decisive
   tests, nothing material untried); **prefer `not_promoted` when in doubt**.
   There is **no `insufficient_evidence`** value.
5. **Nonsignificance is not falsification**, and "CI includes zero" alone
   establishes neither absence, robustness nor equivalence. Equivalence and
   non-inferiority claims require margins declared **before** the run.

---

## §6 Append log

| Date (UTC) | Appended | By |
|---|---|---|
| 2026-09-14 | **TSMOM-VRP-01 S3 governed Stage-A run.** KB-6 updated: **`N_trials` 0 → 1**, `Burned by` now names the one governed VRP-A Stage-A series (2006-09..2026-08, 240 months), and an **S3 exposure** row records `TARGET_METRIC` — the series was generated, protected, and revealed ONCE. The panel is now exposed and may not be reused as fresh independent confirmation. Stage B did not run and, under the sealed §O stop rule, never runs on this historical result; the KB-1 ETF addendum is therefore unchanged and `D-ETF-COUNT` stays untouched. **No existing row was edited or reordered.** | TSMOM-VRP-01 S3 run session (Claude Opus 5) |
| 2026-09-14 | **TSMOM-VRP-01 S2 acceptance rows.** **KB-6** appended: the new `dataset.cboe.vix-futures-monthly-chain` dataset row at **`N_trials = 0` before Stage A**, with the repository verification that no VIX-futures series was ever constructed here, the Cboe PRIMARY source authority, the S2 mechanical-only exposure statement, and evidence context `DESIGN_INFORMED_FIRST_LOCAL_USE`. A **KB-1 addendum** records Stage B as **T0, further reuse (ninth-plus)** of the frozen ETF panel, leaving `D-ETF-COUNT` untouched. **No trial count moved**: Stage A has not run (`STAGE_A_TRIAL_SPENT = NO`), Stage B has not run (`STAGE_B_TRIAL_SPENT = NO`). **No existing row was edited or reordered.** | TSMOM-VRP-01 S2 governance-closure session (Claude Opus 5), implementation Main Agent, under Aaron's `S2 BOUNDED PRE-S3 GOVERNANCE CLOSURE` |
| 2026-09-07 | Initial declaration: KB-1 (ETF, 6/6 burned, 7th reuse declared, no frozen count convention), KB-2 (Databento, `N_trials = 14` verified), KB-3 (T1 wrapper relationship), KB-4 (exposed-sample consequences), KB-5 (T3/T4 separation); residual `UNKNOWN`; cross-project coordination §4; claim consequences §5. | Wave-0 governance session (Claude Opus 5), under Aaron's `AUTHORIZE_WAVE_0_GOVERNANCE_EXECUTION` |

```
WAVE_0_GOVERNANCE_ONLY · NO SEAL EXISTS · NO CANDIDATE HAS RUN
PROTECTED DATA NOT OPENED · STRATEGY_BUILD_READINESS = NOT_READY
```
