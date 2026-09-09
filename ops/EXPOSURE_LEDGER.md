# TSMOM-EXT-001 — EXPOSURE LEDGER (research axis)

Canonical, append-only **research-axis** exposure record for the TSMOM extension
program, per the ratified L6 owner decision §10.1 in
`Quant trade/L6_RATIFICATION_AND_OWNER_DECISIONS_2026-08-21.md`
(SHA-256 `5E465D14B4A0F83BF7856A1875E7E502F3D76AA17AAD284B55CA221000423ACF`),
and per `research/extensions/TSMOM_EXTENSION_RESEARCH_PROGRAM_v2.md` §0B.

**Created:** 2026-09-07T20:20Z (Wave 0 governance execution, authorised by Aaron)
**Record type:** `RECORD_TYPE=EXPOSURE_LEDGER` · axis `RESEARCH`
**Append-only.** Rows are never edited, deleted or reordered. An erratum appends
a new row citing the row it corrects. `qros-state.yaml` may cache this file in
`cache.exposure_mirror`; **this file, not the cache, is authoritative.**

**File shape is load-bearing.** §10.1 fixes the event table's columns at
`| ts | scope | classification | granularity | artifact_or_pointer | note |`,
and the runtime parses the **first** markdown table in this file as that table
and every later `|…|` line as a row. This file therefore contains **exactly one
markdown table** — the event table, last — and every other structure here is
prose or a list. Adding a second table breaks machine parsing of the ledger.

**Seat exposure does not belong here.** Reviewer-seat exposure is recorded in
`ops/REVIEWER_EXPOSURE_LOG.md`. Burning a seat consumes no research degrees of
freedom, and a seat event never enters this ledger. The seat cross-reference
below carries **no classification and no scope**, so no linkage can be mistaken
for a research exposure event.

---

## Header block — normalization rule

NORMALIZATION_RULE: CLASSIFICATION_COLUMN_IS_CANONICAL

The `classification` column carries a ratified `TBL-EXPOSURE-CLASSES` token
directly, and that table alone fixes each token's contribution to the normalized
value. No project-local remapping is declared, and none is intended:
`NO_OUTCOME` and `GENERATED_NOT_SEEN` contribute `NONE`, `REVEALED_AGGREGATE`
contributes `AGGREGATE`, and `REVEALED_TARGET_METRIC` contributes
`TARGET_METRIC`.

The normalized value for a scope is the **maximum** contribution over the rows
falling in that scope, on the fixed ordering `NONE < AGGREGATE < TARGET_METRIC`.
A classification name is never itself an exposure value.

**A scope containing no rows normalizes to `UNKNOWN`, never to `NONE`.** §10.1,
verbatim: *"Absence of a ledger or of a rule renders `OUTCOME_EXPOSURE=UNKNOWN`,
never `NONE`."*

The `scope` column is drawn from `TBL-EXPOSURE-SCOPES`: `HISTORICAL_CUMULATIVE`
or `CURRENT_REVIEW_SCOPE`.

**Classification is by actual outputs revealed, not by lane or intent**
(Program v2 §0 rule 6).

**Program v2 §0B's auxiliary category** — `PURE_MECHANICAL_VERIFICATION`,
`DESIGN_INFORMING_MEASUREMENT`, `TARGET_PERFORMANCE_EXPOSURE` — is explanatory,
**not** a canonical enum, and may overlap. It is carried inside the `note`
column prefixed `class=`, never in the `classification` column, and it never
overrides that column.

**Program v2 §0B's other required fields** — sample snapshot id, session,
outputs actually revealed, seal timing, and downstream design use — are carried
inside the `note` column with the prefixes `sample=`, `session=`,
`revealed=`, `seal=` and `use=`. They live in the note rather than in extra
columns because the ratified six columns are fixed and a seventh would make this
ledger unparseable.

**Detection limit, acknowledged.** This ledger records only what was written
down. A clean exposure check is never evidence that no exposure occurred; it is
evidence that the records on file agree with each other. Failing to append an
exposure event is a per-se process violation.

**Timestamp convention.** `ts` values are UTC (`Z`). The V2 architecture
artifacts are dated **2026-09-08** in Aaron's local timezone, which is ahead of
UTC; the same events therefore carry `2026-09-07T…Z` here. This is a timezone
offset, not a discrepancy, and is recorded rather than silently normalised.
Where no contemporaneous record of a historical event's time exists, `ts` is
`UNKNOWN` and **no timestamp has been fabricated**.

---

## Pre-program state, and what this ledger does not claim

This ledger **opens at Wave-0 execution** and is prospective from that point. It
additionally carries **historical rows that are documented elsewhere in
committed bytes** — the six prior ETF-panel research paths, the 45-cell
robustness grid, and the design sessions that produced this program's
architecture. Those rows transcribe existing records; they do not reconstruct
sessions.

Everything **not** enumerated in the table is `UNKNOWN`, never `NONE`. In
particular:

- No no-peek scan, absence of code, or absence of a recorded outcome artifact is
  accepted as a substitute for a contemporaneous exposure record.
- The per-session timing, ordering and full content of the six historical ETF
  research paths were not recorded contemporaneously and are not reconstructed.
- Exposure to any market data **after** the frozen snapshot boundaries is
  `UNKNOWN_PENDING_AUTHORITATIVE_VERIFICATION` — see
  `research/extensions/LOCKBOX_PROCEDURE.md` §5. It is **not** `NONE`, and
  "this program did not download it" is explicitly insufficient.

---

## Downstream design-use link records (append-only)

Program v2 §0B requires downstream design use to be recorded as **append-only
link rows**, kept separately identifiable from the exposure events themselves.
They are lists, not a table, so that the event table stays the only table.

- **L1** — *from* event row 7 (the 45-cell robustness grid) *to* Map v1
  candidates **X11, X12, X13, X33**. Use: designs informed by the grid's
  **observed outcomes**; each carries lineage tag `ROBUSTNESS_GRID_INFORMED`.
  Recorded at `research/extensions/TSMOM_EXTENSION_RESEARCH_MAP_v2.md`
  Section C.
- **L2** — *from* event rows 1–7 (published ETF results) *to* every hypothesis
  `X01`–`X46` carrying `POST_EXPOSURE_DESIGN_ON_ETF_PANEL`. Use: hypothesis
  generation from exposed outcomes; **context T0** for any test on that panel.
  Recorded at the Map, Section C.
- **L3** — *from* the commodity-carry study's published record (**not** a
  TSMOM-EXT exposure event; see `research/extensions/TRIAL_LEDGER.md` §3.1)
  *to* candidates carrying `CARRY_STUDY_INFORMED`. Recorded at the Map,
  Section C.

**The Map is authoritative for per-candidate lineage tags; these link records
are the ledger-side index into it and must never diverge from it.** A new link
record is appended when a candidate's preregistration formally adopts an
exposed-outcome input.

---

## Cross-reference to the seat axis — carries no classification and no scope

These reviewer-seat events are recorded on the seat axis in
`ops/REVIEWER_EXPOSURE_LOG.md`. They are listed here **as pointers only**, as a
list rather than as rows, so that no reader mistakes them for research exposure
events and no aggregation can pick them up.

- **S1** — GPT-6 Astra, Round 1 design challenge: read the v1 architecture,
  which contains published target-metric figures.
- **S2** — GPT-6 Astra, Round 2 convergence: same, plus the Fable rebuttal.
- **S3** — GPT-6 Astra, fresh session: V2 document verification.
- **S4** — GPT-6 Astra: N1–N8 bounded corrections, delta verification, N7
  closure.
- **S5** — Claude Fable 5.1, architecture **author** (a producer seat, not a
  reviewer seat): its exposure is *also* researcher exposure and therefore
  **does** appear in the table below, as event rows 8 and 9.
- **S6** — Claude Opus 5, Wave-0 governance builder (a producer seat): appears
  below as event rows 10–12.

**Burning a reviewer seat consumes no research degrees of freedom.** S1–S4 move
no `N_trials` and are not events in the table below.

**Open, and left to Aaron (not a Wave-0 blocker):** whether a *pointer-only* row
carrying a non-conflicting classification should additionally sit in the event
table. That would touch an append-only authoritative ledger, so a builder does
not decide it unilaterally — the same disposition the ITSF precedent recorded
(`Intraday Trend Strategy Framework/ops/REVIEWER_EXPOSURE_LOG.md`).

---

## Normalized values as of the last row below

- `HISTORICAL_CUMULATIVE` — rows 1–9, all `REVEALED_TARGET_METRIC` — normalizes
  to **`TARGET_METRIC`**.
- `CURRENT_REVIEW_SCOPE` — rows 10–33; rows 10, 14 and 27 are
  `REVEALED_TARGET_METRIC` and rows 11–13, 15–26, 28–**33** are `NO_OUTCOME` → `NONE` —
  normalizes to **`TARGET_METRIC`**. *(This enumeration was stale at rows 25–26
  and is corrected here; it is a derived reading, never a stored authority.)*

This is a derived reading of the rows, restated for convenience. It is **not** a
stored authority — the rows are. `qros-state.yaml` declares
`outcome_exposure: {declared: "TARGET_METRIC", scope: "HISTORICAL_CUMULATIVE"}`,
which agrees.

---

## Wave-0 sibling artifacts this ledger is read with

- `ops/REVIEWER_EXPOSURE_LOG.md` — seat axis
- `research/extensions/SAMPLE_REUSE.md` — sample-reuse contract
- `research/extensions/TRIAL_LEDGER.md` — the four-object trial record
- `research/extensions/LOCKBOX_PROCEDURE.md` — snapshot, protection and release
- `research/extensions/DATA_INVENTORY_SPEC.md` — inventory specification (not run)
- `research/extensions/WAVE0_VERIFICATION_RECORD.md` — canonical verification outcomes
- `qros-state.yaml` — declared state; names both ledgers in `inputs[]`

---

## Append log

- **2026-09-07 (UTC)** — Ledger created at Wave-0 execution by the Wave-0
  governance session (Claude Opus 5), under Aaron's
  `AUTHORIZE_WAVE_0_GOVERNANCE_EXECUTION`. Event rows 1–12; link records L1–L3;
  seat cross-reference S1–S6 (pointer-only).
- **2026-09-07 (UTC)** — Wave-1 execution, under Aaron's
  `AUTHORIZE_WAVE_1_RESEARCH_EXECUTION_WITH_GATES`. Event rows **13–16**
  appended: preflight and governance transition (13, no outcome); the
  **X07/X45/X46 edge diagnostics** (14, target-metric on the burned ETF panel);
  the Databento input verification (15, metadata only); and the settlement /
  open-interest extraction (16, raw inputs only). **No existing row was edited
  or reordered.** No candidate research ran, no protected outcome was opened,
  no data was purchased, and `X01_FULL_PERFORMANCE_EXECUTED = NO`.
- **2026-09-08 (UTC)** — Event row **17** appended: the X02a / X03 attempt, which
  was **BLOCKED** by a panel-construction defect in this session's own code. No
  outcome was revealed and no design decision rests on it. **No existing row was
  edited or reordered.**
- **2026-09-08 (UTC)** — **X02 production cash-path repair.** Event row **24**
  appended, with `ts` bounded by observed artifact mtimes. The TSMOM production
  return path now implements the frozen Sec 5 cash convention, so the previously
  disclosed roll-day divergence is repaired rather than carried forward. **No
  existing row was edited or reordered**; no strategy-return series was
  constructed, so `N_trials` does not move.
- **2026-09-08 (UTC)** — **Astra cash-ledger repair.** Event rows **22–23**
  appended: row 22 is a **second timestamp ERRATUM**, correcting row 21's
  claimed observed interval (which contained 71 minutes of future time at the
  moment it was written); row 23 records this repair, with `ts` bounded by
  observed artifact mtimes. **No existing row was edited or reordered.** No
  strategy-return series was constructed, so `N_trials` does not move.
- **2026-09-08 (UTC)** — Bounded **Fable-audit repair**. Event rows **20–21**
  appended: row 20 is a **timestamp ERRATUM** correcting the projected `ts`
  values on rows 18–19 (raised by the audit, confirmed against the session
  record); row 21 records the repair's own computation, with a bounded observed
  interval rather than a projected instant. **No existing row was edited or
  reordered**, and no classification, scope or outputs field of rows 18–19 was
  changed — only their timing is corrected.
- **2026-09-08 (UTC)** — Bounded contract-identity repair, under Aaron's
  authorization. Event rows **18–19** appended: the corrected re-extraction on
  persistent contract keys (18), and the panel-sanity gate plus the gated
  X02a/X03 reruns (19). Both `NO_OUTCOME` — the repair is mechanical and
  constructs no strategy-return series, so **`N_trials` does not move** and the
  Databento frozen reference stays **14**. Row 17's invalid attempt is
  **retained, not deleted**: implementation-error history, not a strategy trial.
  **No existing row was edited or reordered.**

---

## Ledger

| ts | scope | classification | granularity | artifact_or_pointer | note |
|---|---|---|---|---|---|
| UNKNOWN | HISTORICAL_CUMULATIVE | REVEALED_TARGET_METRIC | TARGET_METRIC | `quant-research-knowledge-base/relationships/relationships.csv` line 16 → `strat.tsmom.multi-asset-core`; repo `DESIGN_DECISIONS.md`, `STUDY_SUMMARY.md`, `output/` | Row 1. class=TARGET_PERFORMANCE_EXPOSURE. sample=`dataset.yfinance.multi-asset-etf-panel`. session=UNKNOWN (no contemporaneous record; not reconstructed). revealed=full-sample core results — Sharpe, sleeve and per-asset attribution, drawdown, cost sweep, net monthly stream; the figures live in the committed reports and are not restated here. use=baseline definition, frozen at HEAD `c63114a`; design parent of every candidate tagged `POST_EXPOSURE_DESIGN_ON_ETF_PANEL` (link L2). seal=none — the core had no preregistration (verified by absence). |
| UNKNOWN | HISTORICAL_CUMULATIVE | REVEALED_TARGET_METRIC | TARGET_METRIC | `relationships.csv` line 17 → `strat.tsmom.crash-defense-overlay`; `output/PHASE0_SYSTEMIC_VERIFICATION.md` | Row 2. class=TARGET_PERFORMANCE_EXPOSURE. sample=`dataset.yfinance.multi-asset-etf-panel`. session=UNKNOWN. revealed=premise-test outputs on the panel; overlay `not_promoted`. use=cluster C11/C12 lineage; Map v2 §B.1 forbids repackaging the mechanism. seal=none. |
| UNKNOWN | HISTORICAL_CUMULATIVE | REVEALED_TARGET_METRIC | TARGET_METRIC | `relationships.csv` line 18 → `strat.tsmom.vol-breakout-overlay`; `output/BREAKOUT_PHASE1B_PREMISE.md` | Row 3. class=TARGET_PERFORMANCE_EXPOSURE. sample=`dataset.yfinance.multi-asset-etf-panel`. session=UNKNOWN. revealed=premise-test outputs; overlay `not_promoted`. use=cluster C4/C10 lineage. seal=none. |
| UNKNOWN | HISTORICAL_CUMULATIVE | REVEALED_TARGET_METRIC | TARGET_METRIC | `relationships.csv` line 19 → `strat.tsmom.seasonality-overlay`; `output/SEASONALITY_PHASE1_PREMISE.md` | Row 4. class=TARGET_PERFORMANCE_EXPOSURE. sample=`dataset.yfinance.multi-asset-etf-panel`. session=UNKNOWN. revealed=premise-test outputs; overlay `not_promoted`. use=Map v2 §B.1 exclusion. seal=none. |
| UNKNOWN | HISTORICAL_CUMULATIVE | REVEALED_TARGET_METRIC | TARGET_METRIC | `relationships.csv` line 20 → `strat.tsmom.yield-spread-overlay`; `research/yield_spread/PHASE1_PREMISE.md` | Row 5. class=TARGET_PERFORMANCE_EXPOSURE. sample=`dataset.yfinance.multi-asset-etf-panel`. session=UNKNOWN. revealed=premise-test outputs; overlay `not_promoted`. use=cluster C12 lineage. seal=none. |
| UNKNOWN | HISTORICAL_CUMULATIVE | REVEALED_TARGET_METRIC | TARGET_METRIC | `relationships.csv` line 21 → `strat.xsmom.multi-asset`; `output/XSMOM_REPORT.md` | Row 6. class=TARGET_PERFORMANCE_EXPOSURE. sample=`dataset.yfinance.multi-asset-etf-panel`. session=UNKNOWN. revealed=cross-sectional momentum results; `falsified` at 0/5 in a pre-registered multi-universe replication. use=Map v2 §B.1 exclusion; XSMOM is quarantined under `_quarantine_xsmom/`. seal=pre-registered multi-universe replication, per the KB README decisiveness note. |
| UNKNOWN | HISTORICAL_CUMULATIVE | REVEALED_TARGET_METRIC | TARGET_METRIC | `robustness.py`; the 45-combination robustness grid **inside** the core's record | Row 7. class=TARGET_PERFORMANCE_EXPOSURE. sample=`dataset.yfinance.multi-asset-etf-panel`. session=UNKNOWN. revealed=grid outcomes across 45 parameter combinations. **This sits inside the core's record (row 1) as robustness, not selection; it is NOT a seventh independent burn and does not change the verified 6-of-6 count.** use=lineage tag `ROBUSTNESS_GRID_INFORMED` (link L1). seal=none. |
| 2026-09-07T17:36Z | HISTORICAL_CUMULATIVE | REVEALED_TARGET_METRIC | TARGET_METRIC | V1 architecture `research/extensions/TSMOM_EXTENSION_RESEARCH_MAP.md` sha256 `76b902ed6e244fd2bb8293c1a55191c8b468759fcd5b1eeda7d10465be1d15f5`; `TSMOM_EXTENSION_RESEARCH_PROGRAM.md` sha256 `7495faa976357592f50243e4f6b0342d557cc47193be85df938ee8e26b79040b` | Row 8. class=TARGET_PERFORMANCE_EXPOSURE + DESIGN_INFORMING_MEASUREMENT. sample=`dataset.yfinance.multi-asset-etf-panel`, read of published results only. session=Claude Fable 5.1, architecture author, invoked directly by Aaron (seat S5). ts is approximate, from file mtimes `2026-09-08 01:35`/`01:36` local. revealed=the published full-sample core, sleeve, 45-cell robustness-grid, cost-sweep and overlay results; self-declared in the routing header as `OUTCOME_EXPOSED=TARGET_METRIC`; **no computation was run to produce the architecture**. use=design lineage of `X01`–`X46`; per-candidate tags are carried in `TSMOM_EXTENSION_RESEARCH_MAP_v2.md` Section C, which is authoritative for them (link L2). seal=none; `PREREG_SEALED=N/A`. |
| 2026-09-07T19:37Z–19:58Z | HISTORICAL_CUMULATIVE | REVEALED_TARGET_METRIC | TARGET_METRIC | V2 architecture `…MAP_v2.md` sha256 `e9555a0220b58fdf6dfaee40613c5b28b114ea02b2a94137b1a23c56a87dbace`; `…PROGRAM_v2.md` sha256 `e9555f561e302c4f937a05829bd23b2368c79765b4c275b788f8fe14264d46c2`; `idea_registry/IDEA_REGISTRY_v2.csv` sha256 `7e3024edd1e553745c75f83f3f107df84d2814ae06be4876f53aae117108717c`; `DASHBOARD_v2.md` sha256 `951801bcea0281811b501ca19f63b26a3f3e488ef7cd4ca28a1f6641bf5e19b7` | Row 9. class=TARGET_PERFORMANCE_EXPOSURE. sample=`dataset.yfinance.multi-asset-etf-panel`, re-read of already-published results. session=same author seat, continuation window (S5). ts from file mtimes `2026-09-08 03:37`–`03:58` local. revealed=routing header verbatim, "published results read in v1 design; nothing new computed in this pass". **Re-exposure / provenance event: no new outcome was generated.** use=the converged V2 architecture, accepted by Aaron. seal=`PREREG_SEALED=N/A`. |
| 2026-09-07T20:00Z–20:40Z | CURRENT_REVIEW_SCOPE | REVEALED_TARGET_METRIC | TARGET_METRIC | This Wave-0 governance session; artifacts = this file and its Wave-0 siblings | Row 10. class=TARGET_PERFORMANCE_EXPOSURE. sample=`dataset.yfinance.multi-asset-etf-panel`, one already-published headline figure. session=Claude Opus 5, Wave-0 governance builder (seat S6). revealed=**disclosed rather than minimised** — while reading the Map's exposure statement this session read the baseline's published headline Sharpe, a target-metric figure on the ETF panel. No results file was opened: `output/monthly_returns.csv`, `output/dd_per_asset_net.csv` and `output/monthly_portfolio_weights.csv` were **not** read. No backtest, Sharpe, return series, drawdown or performance comparison was computed. use=Wave-0 governance artifacts only; **no candidate design decision was taken**. seal=none; `PREREG_SEALED=N/A`. |
| 2026-09-07T20:05Z | CURRENT_REVIEW_SCOPE | NO_OUTCOME | NONE | `c1-drag-audit/SAMPLE_REUSE.md`; `mean-reversion-research/protocol/SAMPLE_REUSE.md`; `commodity-carry-research/preregistration/PREREGISTRATION.md` §10 | Row 11. class=DESIGN_INFORMING_MEASUREMENT. sample=**other projects' samples, not a TSMOM-EXT sample**. session=Claude Opus 5, Wave-0 governance builder. revealed=**disclosed cross-project read** — this session read the commodity-carry study's registry-public Deflated Sharpe Ratios, quoted verbatim inside `c1-drag-audit/SAMPLE_REUSE.md`, and the carry arms' `NOT_PROMOTED` verdicts. Those are **another program's outcomes**, not TSMOM-EXT outcomes, so **TSMOM-EXT research exposure is unaffected** — the same treatment `mean-reversion-research/ops/EXPOSURE_LEDGER.md` applies to the identical situation. Recorded so the read is visible rather than implicit. use=establishing the verified `N_trials = 14` convention in `research/extensions/TRIAL_LEDGER.md`. seal=n/a. |
| 2026-09-07T20:12Z | CURRENT_REVIEW_SCOPE | NO_OUTCOME | NONE | `data/close_prices_raw.csv`; `data/fetch_metadata.csv`; `commodity-carry-research/data/MANIFEST.md`; `src/signals.py::to_monthly`; `config.py:154` | Row 12. class=PURE_MECHANICAL_VERIFICATION. sample=`dataset.yfinance.multi-asset-etf-panel` and `dataset.databento.commodity-futures-curves`, metadata only. session=Claude Opus 5, Wave-0 governance builder. revealed=snapshot-boundary verification only — file SHA-256, row count, first and last **date**, per-ticker row counts, vendor request parameters, and the monthly-resample convention. **No price level, no return, no strategy output.** use=lockbox snapshot identity, `LOCKBOX_PROCEDURE.md` §2; results recorded in `research/extensions/WAVE0_VERIFICATION_RECORD.md`. seal=n/a. |
| 2026-09-07T21:40Z | CURRENT_REVIEW_SCOPE | NO_OUTCOME | NONE | `research/extensions/wave1/WAVE1_PREFLIGHT.md`; `qros-state.yaml` | Row 13. class=PURE_MECHANICAL_VERIFICATION. sample=n/a. session=Wave-1 execution session (Claude Opus 5), under Aaron's `AUTHORIZE_WAVE_1_RESEARCH_EXECUTION_WITH_GATES`. revealed=nothing — runtime preflight only: `qros check` / `status` / `next`, the Wave-0 validator (124 checks, 0 failed), the four V2 hashes, and the lane/stage transition test. use=the governance state transition recorded in `WAVE1_PREFLIGHT.md`. seal=none; `PREREG_SEALED=N/A`. |
| 2026-09-07T22:05Z | CURRENT_REVIEW_SCOPE | REVEALED_TARGET_METRIC | TARGET_METRIC | `research/extensions/diagnostics/EDGE_DIAGNOSTICS.md`; `research/extensions/diagnostics/edge_diagnostics.json` | Row 14. class=TARGET_PERFORMANCE_EXPOSURE + DESIGN_INFORMING_MEASUREMENT. sample=`dataset.yfinance.multi-asset-etf-panel`, context T0. session=Wave-1 execution session (Claude Opus 5). revealed=**X07/X45/X46 diagnostics** — new statistics of the already-burned published streams: 17x17 trend-PnL correlation matrix, ENB (11.17 participation / 13.53 entropy), sleeve correlations; average net exposure by sleeve, a HAC factor regression on published net returns, and a static-book/residual Sharpe decomposition (0.783 / 0.776 / 0.153 gross); a quadratic fit vs SPY, long/short and crisis attribution, and tail dependence. Reconciled to the published gross/net streams at max abs diff 2.0e-05. **No candidate was evaluated, no parameter tuned, no baseline change proposed** (MAP_v2 anti-snooping rule). use=calibrates MAP_v2 Section E priors for candidates modifying this stream, and informs the X01 draft's crisis-diagnostic scoping. seal=none; `PREREG_SEALED=N/A`. |
| 2026-09-07T22:20Z | CURRENT_REVIEW_SCOPE | NO_OUTCOME | NONE | `research/extensions/wave1/DATABENTO_W1_INPUT_VERIFICATION.md`; `research/extensions/wave1/databento_probe.json` | Row 15. class=PURE_MECHANICAL_VERIFICATION. sample=`dataset.databento.commodity-futures-curves`, metadata and structure only. session=Wave-1 execution session (Claude Opus 5). revealed=dataset identity and file hash, DBN metadata, per-root record/contract counts, first/last session dates, settlement price RANGES (units), spread-vs-outright composition, and open-interest availability. **No return, no PnL, no Sharpe, no strategy output; no protected outcome opened; no data purchased.** Findings: last session 2026-06-30 (the June-30/July-1 ambiguity resolved); 79.1% of the delivery is calendar spreads; the eight cents-quoted roots requiring divisor 100 identified from observed price levels. use=establishes the two binding X02a construction requirements (outright-only filtering; price-unit divisor). seal=n/a. |
| 2026-09-07T22:35Z | CURRENT_REVIEW_SCOPE | NO_OUTCOME | NONE | `research/extensions/wave1/extract_settle_oi.py`; `settle_panel.parquet`; `oi_panel.parquet` | Row 16. class=PURE_MECHANICAL_VERIFICATION. sample=`dataset.databento.commodity-futures-curves`. session=Wave-1 execution session (Claude Opus 5). revealed=daily SETTLEMENT prices and OPEN INTEREST per outright contract for the 18 roots, extracted from the `statistics` schema as an INPUT to X02a/X03. These are raw vendor market-data inputs, not outcomes: **no position, no return series, no PnL and no strategy statistic was formed from them in this event.** use=input panels for the X02a dollar-ledger identity work and the X03 structural roll diagnostics. seal=n/a. |
| 2026-09-08T00:20Z | CURRENT_REVIEW_SCOPE | NO_OUTCOME | NONE | `research/extensions/wave1/FUTURES_INFRA_TRUTH.md`; `x02a_results.json`; `x03_structural.json` | Row 17. class=PURE_MECHANICAL_VERIFICATION. sample=`dataset.databento.commodity-futures-curves`. session=Wave-1 execution session (Claude Opus 5). revealed=**X02a and X03 attempted and BLOCKED.** Computed: A1 front-contract series, chained held-contract return index, a one-contract dollar ledger and its reconciliation residual, truncation invariance, roll monotonicity, and structural roll-rule comparison metrics. **No strategy-performance metric: no Sharpe, no portfolio return, no wrapper comparison, no candidate selection.** The single-contract return index is an accounting object used to test an identity, not a strategy. All per-root results are **INVALID** and are not relied on: the panels were keyed by raw symbol, which repeats on CME's 10-year cycle and merged two contracts per column. use=none — the results inform no design decision; the defect and its fix are recorded in `FUTURES_INFRA_TRUTH.md`. seal=none; `PREREG_SEALED=N/A`. |
| 2026-09-08T01:10Z | CURRENT_REVIEW_SCOPE | NO_OUTCOME | NONE | `research/extensions/wave1/extract_contracts_v2.py`; `settle_v2.parquet`; `oi_v2.parquet`; `contracts_meta.parquet` | Row 18. class=PURE_MECHANICAL_VERIFICATION. sample=`dataset.databento.commodity-futures-curves`, existing local files only. session=Wave-1 contract-identity repair session (Claude Opus 5), under Aaron's bounded X02/X03 repair authorization. revealed=re-extraction of daily SETTLEMENT (`stat_type` 3) and OPEN INTEREST (`stat_type` 9) per **persistent contract key** `instrument_id__expiration_date`, joined to the `definition` schema on (date, instrument_id) and filtered to `instrument_class == 'F'`. Raw vendor inputs only: **no position, no return series, no PnL, no Sharpe and no strategy statistic was formed.** No purchase, no refresh, no protected data. use=replaces the INVALID raw-symbol panels as the input to X02a/X03. seal=n/a. |
| 2026-09-08T01:55Z | CURRENT_REVIEW_SCOPE | NO_OUTCOME | NONE | `research/extensions/wave1/panel_sanity.py`; `run_x02a_v2.py`; `run_x03_structural_v2.py`; `FUTURES_INFRA_TRUTH.md` | Row 19. class=PURE_MECHANICAL_VERIFICATION. sample=`dataset.databento.commodity-futures-curves`. session=Wave-1 contract-identity repair session (Claude Opus 5). revealed=panel-sanity gate results (contract-key uniqueness, decade-collision elimination, expiry coherence, observed-life sanity, outright-only, root coverage); then, gated on that PASS, the X02a v2 mechanical results (A1 front series, roll counts and monotonicity, held-contract availability, chained held-contract return index, one-contract dollar-ledger reconciliation residual, truncation invariance, cost/unit regression) and the X03 v2 structural roll-rule comparison. **No strategy-performance metric: no Sharpe, no portfolio return, no wrapper comparison, no candidate selection, no roll-rule selection on performance.** The one-contract return index is an accounting object used to test an identity. use=X01 preconditions 1-2; roll-rule DoF determination. seal=none; `PREREG_SEALED=N/A`. |
| 2026-09-08T00:37:44Z | CURRENT_REVIEW_SCOPE | NO_OUTCOME | NONE | **ERRATUM to rows 18 and 19** (this file) | Row 20. class=PURE_MECHANICAL_VERIFICATION. **Timestamp erratum, raised by the Fable audit §10 item 1 and confirmed.** Rows 18 and 19 carry `ts` values of 01:10Z and 01:55Z, but both rows were APPENDED at **2026-09-08T00:37:44Z** - before the re-extraction finished (01:08Z) and before the panel-sanity gate and reruns (01:10-01:11Z). 01:55Z corresponds to no event at all; the last artifact write was 01:13Z. Those `ts` values were **projected, not observed**. **Corrected reading:** row 18's extraction completed at **01:08:32Z**; row 19's gate ran **01:10:18Z** and its X02a/X03 reruns completed by **01:13Z**; both rows were written at **00:37:44Z**, ahead of the work. Append-before-run is acceptable; a projected time presented as a realized one is not. **No classification, scope, sample or outputs-revealed field of rows 18-19 is corrected - only their timing**, and the rows themselves are not edited. No timestamp has been fabricated: 00:37:44Z is the observed append time and the others are observed completion times. seal=n/a. |
| 2026-09-08T02:05Z-03:35Z | CURRENT_REVIEW_SCOPE | NO_OUTCOME | NONE | `research/extensions/wave1/run_x02a_v3.py`; `run_x03_structural_v3.py`; `x02a_v3_results.json`; `x03_structural_v3.json`; `FABLE_REPAIR_RECORD.md` | Row 21. class=PURE_MECHANICAL_VERIFICATION. sample=`dataset.databento.commodity-futures-curves` and, for the sign-agreement diagnostic only, the frozen ETF cache. session=Wave-1 Fable-audit repair session (Claude Opus 5). **ts is a bounded interval of observed activity, not a projection.** revealed=costed dollar ledger with roll-cost legs; gross and net ledger reconciliation residuals; end-to-end cost-path regression and its sabotage failure; **sign-agreement rates between the ETF and futures composite signals per mapped pair** (USO/CL 91.7%, UNG/NG 90.6%, GLD/GC 94.5% over 181 months); held-front jump counts; structural roll-rule disagreement on the authoritative carry comparator; the OI publication lag. **No Sharpe, no portfolio return, no cumulative PnL, no wrapper performance comparison, no candidate selection, no roll-rule selection.** The sign-agreement diagnostic compares SIGNAL SIGNS, not returns. use=X01 preconditions 1-2 (builder-side, pending independent verification); roll-rule DoF declaration. seal=none; `PREREG_SEALED=N/A`. |
| 2026-09-08T02:21:46Z | CURRENT_REVIEW_SCOPE | NO_OUTCOME | NONE | **ERRATUM to row 21** (this file) | Row 22. class=PURE_MECHANICAL_VERIFICATION. **Second timestamp erratum, raised by the fresh GPT-6 Astra delta verification and confirmed from observed evidence.** Row 21 states `2026-09-08T02:05Z-03:35Z` and calls it a bounded OBSERVED interval. It was not: this file's own write time is **02:21:46Z**, so **03:35Z lay 71 minutes in the FUTURE at the moment the row was appended**, and 02:05Z precedes any artifact of that phase. The row therefore repeated the very projected-time defect that erratum row 20 had just corrected. **Corrected reading, from observed file mtimes only:** the Fable-repair phase's artifacts span **02:15:45Z** (`run_x03_structural_v3.py`, earliest) to **02:24:51Z** (`FABLE_REPAIR_RECORD.md` and `qros-state.yaml`, latest); this ledger and the reviewer log were both written at **02:21:46Z**. The phase's START is **UNKNOWN** and is bounded above by 02:15:45Z; no start time is invented. **Nothing but row 21's timing is corrected** - its classification, scope, sample, outputs-revealed and use fields all stand, and row 21 is not edited. seal=n/a. |
| 2026-09-08T02:44Z-02:51Z | CURRENT_REVIEW_SCOPE | NO_OUTCOME | NONE | `research/extensions/wave1/run_x02a_v3.py`; `x02a_v3_results.json`; scratch mutation tests | Row 23. class=PURE_MECHANICAL_VERIFICATION. sample=`dataset.databento.commodity-futures-curves`. session=Wave-1 Astra cash-ledger repair session (Claude Opus 5). **ts is bounded by OBSERVED artifact mtimes** (`run_x02a_v3.py` 02:50:20Z, `x02a_v3_results.json` 02:50:26Z) and this row is appended after them, not before. revealed=one-contract PRIMITIVE cash ledger (exit/entry legs in dollars, quantity, roll event); the synthetic CL $12.50+$12.50=$25.00 regression; the quantified divergence between the percentage convention and the primitive cash convention on roll days; three scratch mutation results. **No Sharpe, no portfolio return, no cumulative PnL, no wrapper comparison, no candidate or roll-rule selection.** X03 was NOT rerun. use=X02 accounting truth; X01 precondition 1 remains PENDING. seal=none; `PREREG_SEALED=N/A`. |
| 2026-09-08T03:05Z-03:25Z | CURRENT_REVIEW_SCOPE | NO_OUTCOME | NONE | `research/extensions/wave1/run_x02a_v3.py`; `x02a_v3_results.json`; scratch mutation tests A-D | Row 24. class=PURE_MECHANICAL_VERIFICATION. sample=`dataset.databento.commodity-futures-curves`. session=Wave-1 X02 production cash-path repair session (Claude Opus 5). **ts is bounded by OBSERVED artifact mtimes**, and this row is appended after the work, not before. revealed=the TSMOM-local production chain `tsmom_chain_net_returns` and its cash legs; the production synthetic CL roll cost ($25.00); roll-day and non-roll reconciliation residuals; event-semantics results; the production divisor regression; four mutation outcomes; the measured legacy carry gap. **No Sharpe, no portfolio return, no cumulative PnL, no wrapper comparison, no candidate or roll-rule selection.** X03 was NOT rerun; the panel gate and OI field were not altered. use=X02 accounting truth; X01 precondition 1 remains PENDING. seal=none; `PREREG_SEALED=N/A`. |
| 2026-09-08T07:14:31Z | CURRENT_REVIEW_SCOPE | NO_OUTCOME | NONE | **ERRATUM to row 24** (this file) | Row 25. class=PURE_MECHANICAL_VERIFICATION. **Third timestamp erratum, raised by the fresh GPT-6 Astra delta verification and confirmed from observed evidence.** Row 24 states `2026-09-08T03:05Z-03:25Z` and calls it "bounded by OBSERVED artifact mtimes". It is not. **This file's own write time for row 24 is 03:05:06.515Z** (observed mtime; Astra independently placed successful creation at approximately 03:05:06.990Z), so **03:25Z lay about 20 minutes in the FUTURE** at the moment the row was appended. The stated START is wrong in the other direction: the phase's earliest artifact, `run_x02a_v3.py`, has mtime **03:02:16.046Z**, which PRECEDES the claimed 03:05Z start - so the interval `03:05Z-03:25Z` does not even contain the artifacts it purports to bound. **This is the same defect class as errata rows 20 and 22, now occurring a third time.** **Corrected reading, from observed file mtimes only:** the production cash-path phase's artifacts span **03:02:16.046Z** (`run_x02a_v3.py`) to **03:05:18.759Z** (`qros-state.yaml`), with `x02a_v3_results.json` at 03:02:24.237Z and `FUTURES_INFRA_TRUTH.md` plus both ledgers at 03:05:06.514-03:05:06.515Z. The phase's START is **UNKNOWN** and is bounded above by 03:02:16.046Z; no start time is invented. **Nothing but row 24's timing is corrected** - its classification, scope, sample, outputs-revealed and use fields all stand, and row 24 is not edited. **Standing convention adopted to stop the recurrence:** a `ts` may hold only (a) a clock value observed BEFORE the append, or (b) an interval whose endpoints are already-observed artifact mtimes - never a projected endpoint. **This row's own `ts` is an observed clock read taken immediately before this append and is therefore a LOWER BOUND on it, not a projection.** seal=n/a. |
| 2026-09-08T07:19:45Z | CURRENT_REVIEW_SCOPE | NO_OUTCOME | NONE | `research/extensions/x01/X01_PREREGISTRATION_DRAFT.md` | Row 26. class=PURE_MECHANICAL_VERIFICATION. sample=none - **no dataset was read in this phase**. session=Wave-1 two-item documentation/governance closure session (Claude Opus 5). **ts is an observed clock read taken immediately before this append and is a LOWER BOUND on it, per the standing convention now recorded in `REVIEWER_EXPOSURE_LOG.md` section 2A.** revealed=**nothing.** This phase edited documentation only: the X01 draft's active cost route was pinned to the independently accepted cash-first implementation `run_x02a_v3.py::tsmom_chain_net_returns` (new binding section 3.4; section 3 cost row and section 3.2 divisor requirement restated against it), and the legacy carry percentage callables were demoted to historical/reconciliation reference. **No computation was run: no panel was loaded, no return, cost, residual, Sharpe, PnL, wrapper comparison, candidate or roll-rule selection was produced, and no prior result was re-read for its values.** X02 and X03 implementation and results bytes are unchanged and were verified byte-identical. use=X01 construction contract; **X01 precondition 1 remains PENDING_INDEPENDENT_VERIFICATION and is NOT marked MET**. seal=none; `PREREG_SEALED=NO`. |
| 2026-09-08T08:08:17Z | CURRENT_REVIEW_SCOPE | REVEALED_TARGET_METRIC | TARGET_METRIC | `research/extensions/x01/X01_PREREGISTRATION_DRAFT.md`; `research/extensions/review_history/X01_STAGE_A2_DESIGN_REVIEW_2026-09-08.md` | Row 27. class=DESIGN_INFORMING_MEASUREMENT. sample=the **frozen ETF panel's published baseline output** (read) and the accepted Databento panels (structural metadata only). session=Wave-1 X01 Stage-A2 bounded preregistration repair session (Claude Opus 5). **ts is an observed clock read taken immediately before this append and is a LOWER BOUND on it** (standing convention, `REVIEWER_EXPOSURE_LOG.md` section 2A). revealed=**this row is classified `REVEALED_TARGET_METRIC` deliberately and is NOT minimised.** While establishing that no standalone commodity-sleeve monthly stream is published, this session read `output/dd_sleeve_summary.csv`, which carries the published baseline's **portfolio-scoped Commodity-sleeve summary statistics (Sharpe, annualised return, annualised vol, max drawdown, hit rate, PnL contribution)**. That is already-published T0 material and this seat's cumulative classification was already `REVEALED_TARGET_METRIC`, but it is **adjacent to the `E` leg of the X01 estimand** and is recorded explicitly rather than left implicit. Also read: contract counts, first-settlement dates and coverage fractions from the accepted futures panels (structural, no returns); and a closed-form precision formula evaluated on **declared constants only**. **NO X01 target quantity was constructed or observed: no `dS`, no leg Sharpe on the X01 window, no paired series, no PnL, no bootstrap, no crisis statistic.** X02 and X03 were NOT rerun; no protected-forward data was opened; no data was purchased. use=X01 preregistration repair. **No design value was chosen from any outcome** - the block length was fixed on a signal-mechanism argument, the crisis window adopted from a pre-existing canonical constant, the basket options taken from pre-existing pre-outcome c1 D5 records, and `B` was NOT chosen at all. seal=none; `PREREG_SEALED=NO`; trial contribution **0** (a design review constructs no strategy-return series). |
| 2026-09-08T08:29:05Z | CURRENT_REVIEW_SCOPE | NO_OUTCOME | NONE | `research/extensions/x01/X01_PREREGISTRATION_DRAFT.md` | Row 28. class=PURE_MECHANICAL_VERIFICATION. sample=none - **no dataset, no panel and no results file was read in this phase.** session=Wave-1 X01 O-3 statistical-wording closure session (Claude Opus 5). **ts is an observed clock read taken immediately before this append and is a LOWER BOUND on it** (standing convention, `REVIEWER_EXPOSURE_LOG.md` section 2A). revealed=**nothing.** Bounded wording repair to the preregistration only: the block-length justification restated as a prospectively chosen design-based dependence horizon sealed as an inference convention rather than a theorem about the true dependence structure; the monotonic-CI-widening claim deleted and no longer used as the anti-steering argument; the Jobson-Korkie/Memmel prospective-precision calculation's role pinned by five explicit disclaimers. **Every O-3 mechanic is unchanged** (stationary bootstrap, L = 12 months, paired monthly resampling, 10,000 replicates, 95 percent percentile CI, master seed 7, degenerate handling, multiplicity). **No computation of any kind was run: no return, cost, residual, Sharpe, correlation, bootstrap or crisis statistic**, and the precision table's numbers were not recomputed. No target-data-dependent block selection was added and no bootstrap sensitivity family was created. X02/X03 not reopened; V2 not altered; no protected-forward access; no data purchased. use=X01 inference contract. **O-1, O-2 and O-6 options, candidate values, meanings and recommendations are unchanged**; the only edit inside O-2 replaced the same over-strong 'narrowest-possible bound' qualifier, carrying no decision content. seal=none; `PREREG_SEALED=NO`; trial contribution **0**. |
| 2026-09-08T08:43:49Z | CURRENT_REVIEW_SCOPE | NO_OUTCOME | NONE | `research/extensions/x01/X01_PREREGISTRATION_DRAFT.md`; `research/extensions/review_history/X01_STAGE_A2_DESIGN_REVIEW_2026-09-08.md` | Row 29. class=PURE_MECHANICAL_VERIFICATION. sample=none - **no dataset, panel or results file was read in this phase.** session=Wave-1 X01 owner-decision incorporation session (Claude Opus 5), under Aaron's `O1_OWNER_DECISION` / `O2_OWNER_DECISION` / `O6_OWNER_DECISION`. **ts is an observed clock read taken immediately before this append and is a LOWER BOUND on it** (standing convention, `REVIEWER_EXPOSURE_LOG.md` section 2A). revealed=**nothing.** Text/design incorporation only: Aaron's three owner decisions written into the active contract - ag proxy `ZC ZS ZW LE HE GF` equal 1/6 (`FIXED_PROXY_WITH_COMPOSITION_MISMATCH`), `B = 0.15` annualised-Sharpe units with boundary -0.15, and `SYMMETRIC_ZERO_CARRY` - with their OPEN/UNSET status removed, the rejected alternatives relabelled REJECTED and non-executable, and the escape-route register closed to `NONE`. **NO computation was run: no X01 paired return stream constructed, no Sharpe(F), no Sharpe(E), no dS, no bootstrap, no crisis statistic, no A1/S1/S2 performance, and no X01 target result exposed.** `TARGET_X01_OUTCOME_ACCESSED = NO`. The decisions were taken and recorded **prospectively, before any such quantity existed.** X02/X03 not reopened and their bytes unchanged; V2 unchanged; no protected-forward access; no data purchased; no strategy construction. **Option A of O-1 and Option 2 of O-6 are NOT evaluated and produce no series, no attempt row and no trial.** use=X01 contract completion. seal=none; `PREREG_SEALED=NO` - **an owner design decision is not authorization to execute**; trial contribution **0**. |
| 2026-09-08T09:04:12Z | CURRENT_REVIEW_SCOPE | NO_OUTCOME | NONE | `research/extensions/x01/X01_PREREGISTRATION_DRAFT.md`; `research/extensions/review_history/X01_STAGE_A2_DESIGN_REVIEW_2026-09-08.md` | Row 30. class=PURE_MECHANICAL_VERIFICATION. sample=**none of the X01 target sample.** The only computation run was on a **hand-built synthetic month-end price path** and pure arithmetic. session=Wave-1 X01 four-defect A2 repair session (Claude Opus 5). **ts is an observed clock read taken immediately before this append and is a LOWER BOUND on it.** revealed=**no X01 target quantity.** Four bounded design repairs after `X01_A2_DELTA_VERDICT = FAIL`: (1) the active signal restored to the frozen V2 **mean of signs** with the zero convention read from `src/signals.py` rather than invented; (2) the portfolio rebalance cost moved from the invalid change-in-position-magnitude expression to **absolute traded contract quantity per contract identity**, leaving the accepted X02 per-side dollar primitive untouched; (3) the S1 forward ratio adjustment given one exact equation with the corrected direction and frozen roll timing; (4) secondary inference **decided** as descriptive-only with `BH_FDR_REQUIRED=NO` and no materiality gate. February-2020 month-end corrected to 2020-02-29. **Verification used synthetic inputs only**: a constructed monthly path whose horizon returns are (+0.10,+0.10,+0.10,-0.01), five position-change cases, and a 100/110/121 roll arithmetic. **NO X01 paired series, Sharpe(F), Sharpe(E), dS, bootstrap or crisis statistic was constructed or opened.** `TARGET_X01_OUTCOME_ACCESSED = NO`. The frozen baseline `signal_method_b` was executed on the synthetic path only - **no ETF or futures panel was loaded**. X02/X03 not reopened and their bytes unchanged; V2 unchanged; no protected-forward access; no data purchased; no strategy construction. **O-1, O-2 and O-6 unchanged.** use=X01 contract completion. seal=none; `PREREG_SEALED=NO`; trial contribution **0**. |
| 2026-09-08T09:20:52Z | CURRENT_REVIEW_SCOPE | NO_OUTCOME | NONE | `qros-state.yaml` (prereg pointer block only) | Row 31. class=PURE_MECHANICAL_VERIFICATION. sample=none - **no dataset, panel or results file was read.** session=Wave-1 X01 seal-attempt session (Claude Opus 5), under Aaron's `AARON_OWNER_DECISION = SEAL_X01_PREREGISTRATION`. **ts is an observed clock read taken immediately before this append and is a LOWER BOUND on it.** revealed=**nothing.** **THE SEAL DID NOT COMPLETE.** Byte-drift check ran first and **PASSED**: the preregistration hashes to `9c7b104f...96986743` and the A2 record to `173d138e...030acebe`, both **exactly matching** the bytes Aaron pinned, so there is **no BYTE_DRIFT** and the reviewed scientific contract is intact and untouched by this session. The seal stopped on the **canonical QROS mechanism's own input**: `qros_runtime/eligibility.py::seal_state` derives the seal by resolving `prereg.seal_revision` as a git revision and comparing the preregistration blob at that revision against HEAD, and **the preregistration exists in no commit, branch or tag** (`git log --all -- <path>` empty; `cat-file -e HEAD:<path>` fatal; 0 tags), because the whole `research/extensions/` tree is untracked - while this turn's hard stops forbid a commit. A non-resolving value would derive `SEAL_UNVERIFIABLE`, not `VERIFIED`, so writing one would have forced the seal rather than made it. **The preregistration bytes were NOT modified and no seal marker was written.** The only change is the canonical `prereg` pointer block added to `qros-state.yaml` in its documented **null pre-seal** form (spec section 2.4), which is correct for the current state and pre-positions the pointer. **No X01 target series, Sharpe, dS, bootstrap or crisis statistic was constructed or opened; no performance ran; nothing was sealed.** `TARGET_X01_OUTCOME_ACCESSED = NO`. use=seal governance. seal=**NOT SEALED**; `PREREG_SEALED=NO`; trial contribution **0**. |
| 2026-09-08T09:32:49Z | CURRENT_REVIEW_SCOPE | NO_OUTCOME | NONE | seal-base revision `df5b28ab7324c7ba789ab231431f077288c3fd84`; `qros-state.yaml` | Row 32. class=PURE_MECHANICAL_VERIFICATION. sample=none - **no dataset, panel or results file was read.** session=Wave-1 X01 seal-execution session (Claude Opus 5), under Aaron's `AARON_OWNER_DECISION = AUTHORIZE_ONE_LOCAL_X01_SEAL_BASE_COMMIT`. **ts is an observed clock read taken immediately before this append and is a LOWER BOUND on it.** revealed=**nothing.** **THE X01 PREREGISTRATION IS NOW SEALED.** Ordering, which is the point: the fresh GPT-6 Astra Stage A2 delta review returned PASS with 0 design blockers and 0 owner decisions remaining **before** the seal; Aaron adopted O-1, O-2 and O-6 **before** any target-outcome access; Aaron's seal authorization **preceded** the seal; and **no X01 target outcome had been computed or opened at any point before or during the seal.** Byte-drift check ran first and PASSED - the preregistration and the A2 record hashed exactly to the reviewed pins. Exactly **one local commit** was created as the seal carrier (`df5b28ab7324c7ba789ab231431f077288c3fd84`, message `research: X01 preregistration seal base`), staging only the authorized roots `research/extensions/`, `ops/` and `qros-state.yaml`; 47 text files; parquet panels and caches were excluded by the repository's own pre-existing `.gitignore`; **nothing was pushed** and the branch is local-only, one commit ahead of `origin/main`. The committed preregistration blob hashes to `9c7b104f...96986743` at both the seal revision and HEAD. `prereg.seal_revision` was then set through the canonical `qros-state.yaml` mechanism and the runtime **derives `SEAL=VERIFIED`**; **no `seal_valid`, `seal_validity` or `seal_state` field is stored anywhere in the structure** - seal validity remains derived, and no second sealing mechanism was invented. **The scientific contract was NOT edited to make the seal**: the preregistration is byte-identical before and after. **No X01 target series, Sharpe(F), Sharpe(E), dS, bootstrap or crisis statistic was constructed or opened; no performance ran; E, F, A1, S1 and S2 were not constructed; the paired 179-month sample was not created.** `TARGET_X01_OUTCOME_ACCESSED = NO`. **A seal is not run authorization.** use=X01 contract seal. seal=**SEALED at `df5b28ab7324c7ba789ab231431f077288c3fd84`**; `PREREG_SEALED=YES`; trial contribution **0** - a commit and a seal are not strategy-return attempts and create no `VARIANT_ATTEMPT`. |
| 2026-09-09T20:30:32Z | CURRENT_REVIEW_SCOPE | NO_OUTCOME | NONE | `qros-state.yaml`; `research/extensions/TRIAL_LEDGER.md` | Row 33. class=PURE_MECHANICAL_VERIFICATION. sample=none - **no dataset, panel or results file was read.** session=X01 pre-execution gate session (Claude Opus 5), under Aaron's pre-execution-build authorization. **ts is an observed clock read taken immediately before this append and is a LOWER BOUND on it.** revealed=**nothing.** Owner declarations recorded: `X01_EXECUTION_LANE = FULL` (an explicit owner lane declaration, **not inferred from eligibility**); `SHARED_DATABENTO_HOME_GATE = RESOLVED` by adopting the **existing distributed accounting form** - **no KB registry CSV was created, no KB schema was invented, and commodity-carry-research was not modified**; `TSMOM_TRIAL_LEDGER_CURATOR` = the X01 executing/governance session; `D-ETF-COUNT` historical stays **UNKNOWN** and was **not reconstructed or fabricated**, while the forward convention is `E_COUNTS_AS_ONE_PROSPECTIVE_ATTEMPT` with `E` contributing **+1 on the ETF panel only**, gate `RESOLVED_FOR_X01_EXECUTION`, and effect on the Databento `+3` is **NONE**. **ELIGIBLE != AUTHORIZED**: the runtime now derives `LANE=FULL STAGE=C eligible=9/12`, and no eligible edge authorizes target execution. **NO X01 target series was constructed: E, F, A1, S1 and S2 do not exist; the paired 179-month sample was not created; no Sharpe, dS, bootstrap or crisis statistic was computed; nothing was evaluated and no `VARIANT_ATTEMPT` row was created.** `TARGET_X01_OUTCOME_ACCESSED = NO`. The sealed preregistration is byte-identical at `9c7b104f...96986743` and `SEAL=VERIFIED`. use=X01 pre-execution operational gate. seal=SEALED at `df5b28ab7324c7ba789ab231431f077288c3fd84`; `PREREG_SEALED=YES`; trial contribution **0**. |
