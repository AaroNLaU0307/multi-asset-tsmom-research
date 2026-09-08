# LOCKBOX_PROCEDURE.md — TSMOM-EXT-001

**Program:** TSMOM extension (`TSMOM-EXT-001`), `multi-asset-tsmom-research`
**Created:** 2026-09-07 (Wave 0 governance execution, authorised by Aaron)
**Implements:** `TSMOM_EXTENSION_RESEARCH_PROGRAM_v2.md` §2 (Lockbox procedure)
and §0A (contexts T3/T4) · `TSMOM_EXTENSION_RESEARCH_MAP_v2.md` §A.5, §G
**Corresponds to** Map v2 §K decision **D5** (adopt the lockbox procedure).

**This document defines mechanics. It opens nothing.** No protected outcome was
inspected, no panel was refreshed, and no data after any frozen boundary was read
in producing it.

---

## §1 Three states, kept distinguishable

The single most important property of this procedure: **the three states below
are never conflated, and accrued history is never relabelled prospective.**

| State | Definition | What it can support | Today |
|---|---|---|---|
| **FROZEN HISTORICAL WORKING SNAPSHOT** | Data already available and already used for historical work. Outcomes on it **have been observed**. | Context **T0** (exposed design sample) for anything designed from those outcomes; context **T1** for a different wrapper over the same period. Dependent evidence. | **This is what both panels are.** See §2. |
| **ACCRUED BUT PROTECTED HOLDOUT** | Market history that **has already occurred** but whose protected evaluation outcomes have not been validly released. | Context **T3** — held-out historical evidence — **only after protection is verified**. | **Exists as data, but is NOT usable as T3.** Protection is **not** verified. See §5. |
| **PROSPECTIVE FORWARD ACCRUAL** | Outcomes occurring **after** the relevant design / seal / access protocol. | Context **T4** — the strongest temporal protection available. | **Does not exist.** No contract is sealed (`PREREG_SEALED=N/A`), so no T4 clock has started for any candidate. |

**The rule that keeps them distinguishable:** a datum's state is fixed by **when
it occurred relative to the relevant seal or protocol**, never by when this
program happened to download it. Data that occurred before a seal cannot become
T4 by being fetched after the seal.

---

## §2 Snapshot identity — per dataset

A snapshot is identified by **path + byte size + SHA-256 + verified last date**.
All values below were verified from bytes on 2026-09-07 and are recorded in
`WAVE0_VERIFICATION_RECORD.md`.

### §2.1 `dataset.yfinance.multi-asset-etf-panel`

| Field | Value | Status |
|---|---|---|
| Working snapshot | `data/close_prices_raw.csv` | VERIFIED |
| SHA-256 | `3d2a7a56dbd92d4ff8138cfd894c87f5ac5ac088a11165db870673e0c05c3c31` | VERIFIED 2026-09-07 |
| Size / shape | 3,298,252 bytes; 8,400 data rows + header; 30 tickers | VERIFIED |
| First date | `1993-01-29` | VERIFIED |
| **Frozen boundary (last date)** | **`2026-06-12`** | VERIFIED — the value Map v2 §A.5 carried as "observed in orientation" is now verified from bytes |
| Provenance sidecar | `data/fetch_metadata.csv` — per-ticker `ok`/`rows`; 30 rows, all `True` | VERIFIED |
| Vendor | yfinance (adjusted close) | as documented in-repo |

**Incomplete-period handling — VERIFIED, and consequential.**
`src/signals.py::to_monthly` is `daily_prices.resample(rule).last()` with
`config.py:154` `SIGNAL_RESAMPLE = "ME"` (month-END). Its docstring states the
convention: *the monthly value is the last available daily close within the
calendar month, labeled at the calendar month-end.*

Therefore **the final monthly row for June 2026 is labelled `2026-06-30` but is
constructed from data ending `2026-06-12` — a partial month.** It is a complete
label over an incomplete period.

**Rule:** any evaluation that uses the terminal monthly row must either
(a) **truncate** it and state so, or (b) declare in its preregistration that a
partial terminal month is included and why. A partial terminal row must never be
compared against full months as though it were one. **This is the first item
every new candidate's A2 challenge should check**, and it is recorded here so
that check has something to check against.

### §2.2 `dataset.databento.commodity-futures-curves`

| Field | Value | Status |
|---|---|---|
| Corpus root | `C:\Users\Aaron\quant-data\commodity-carry` (~9.43 GB) | VERIFIED present |
| Authoritative manifest | `commodity-carry-research/data/MANIFEST.md`, generated 2026-07-11T06:03:52Z | VERIFIED |
| Dataset / symbology | `GLBX.MDP3`, 18 pre-registered CME roots, parent symbology | VERIFIED from manifest |
| Request range | `2010-06-06` inclusive → `2026-07-01` exclusive | VERIFIED from manifest |
| **Frozen boundary (last date)** | **`2026-06-30` inclusive** | VERIFIED — Map v2 §A.5's "as reported by the carry manifest" is now verified from the manifest bytes |
| `ohlcv-1d` | `ohlcv-1d.dbn.zst`, 107,229,003 bytes, SHA-256 `333095164e55c73a150949b654a0e4c9f15636cc01ee7c93bf625e5412c59539` | VERIFIED from manifest; file present on disk at the stated size |
| `definition` | 5,031 per-day files, 2,153,223,347 bytes, aggregate SHA-256 `76da3a39a7279ef3a3b4c03ffb2646048685f715466108ca5136aee6f7922277` | VERIFIED from manifest |
| `statistics` | 5,026 per-day files, 7,166,969,133 bytes, aggregate SHA-256 `ee7dee4dc1c2dab44df207d20d5327b0dfb7e6193c49091b8e0a52bfb489001f` | VERIFIED from manifest |
| Superseded provenance | 4 retired `statistics` chunks under `_superseded/`, never resolved by the loader | recorded in manifest |

**Incomplete-period handling:** the request range ends at a **month end**
(2026-06-30), so no partial calendar month exists at the boundary. Roll and
expiry effects near the boundary are a **construction** question owned by each
candidate's contract, not by this procedure.

**Per-file SHA-256 re-verification of the 10,058 delivered files was NOT run in
Wave 0** — it is a bulk read of the corpus with no governance benefit at this
stage. The manifest's aggregate hashes are the recorded record; re-verification
is reproducible from `DATA_DIR` at any time and is owed **before** the first
computation on this panel, not now.

---

## §3 Refresh protocol

1. **A refresh writes a NEW snapshot with its own hash. It never overwrites the
   frozen panel.** The frozen file keeps its path and bytes; the refresh lands
   beside it under a distinct name recording its fetch date.
2. **A refresh that revises historical adjusted prices is a NEW DATASET, not a
   longer version of the old one.** yfinance adjusted closes are revised by
   splits, dividends and vendor corrections; a refreshed series is therefore not
   guaranteed to reproduce the frozen series over the overlapping period.
   Consequence: results computed on the frozen snapshot are **not** comparable to
   results computed on the refreshed one, and a refresh must not be treated as
   "more of the same data".
3. **Working use is truncated at the frozen boundary.** A refreshed snapshot may
   be used for *working* purposes only when truncated at the frozen boundary
   (2026-06-12 for the ETF panel; 2026-06-30 for the Databento panel), so that
   post-boundary values are not silently absorbed.
4. **Every refresh is logged before it is used:** an `ops/EXPOSURE_LEDGER.md` row
   recording what was fetched, the new snapshot's hash, and whether any
   historical value changed.
5. **A refresh is not a release.** Fetching post-boundary *data* is distinct from
   reading post-boundary *outcomes*; §4 governs the latter.
6. **Do not refresh a protected panel in order to discover what happened.** That
   is a release under §4 with the paperwork skipped.

---

## §4 Access control and release procedure

**Protected paths.** For each dataset, everything strictly **after** its frozen
boundary is protected: `> 2026-06-12` (ETF) and `> 2026-06-30` (Databento).
Protection attaches to **outcomes evaluated over that period**, not merely to
files.

**Release rule.** **An opening is an exposure event that burns the holdout for
that claim family.** Once a candidate's outcomes over the protected period have
been read, that period can never again supply held-out evidence *for that claim
family*.

**The governing principle, which the ordered steps below implement:**

> **AUTHORIZATION MUST PRECEDE PROTECTED OUTCOME ACCESS.**

No step that reads, computes, displays or otherwise reveals a protected outcome
may occur before Aaron's explicit authorization for that specific release. A
builder session never opens a holdout on its own judgement, and an authorization
given for one release never carries to another.

**Procedure, in order:**

1. **Identify the release contract.** Name the preregistration (or the release
   contract it provides for) and the **claim family** the release is for. A
   release is always *for something*; an open-ended look burns everything.
2. **Verify eligibility and protected-snapshot identity.** Confirm the contract
   is sealed and that this release is the one it provides for; confirm the
   protected snapshot's identity (path, size, SHA-256, boundary date) against
   §2. An unsealed release is not a T4 event and must not be called one.
3. **Declare the planned access/release scope** *before* requesting
   authorization: which sample and snapshot, which period, which outputs are to
   be revealed and at what granularity, and which claim family the holdout will
   be burned for. This declaration is what Aaron authorizes; it is prospective
   and reveals nothing.
4. **Aaron gives explicit authorization** for the protected release, against the
   scope declared at step 3. **This is the gate.** Without it, the procedure
   stops here and no protected outcome is accessed.
5. **Only after authorization: access/release the protected outcome**, and only
   within the authorized scope. Anything outside that scope is a new release
   needing its own authorization.
6. **Log the actual access/release immediately** as an exposure/release event in
   `ops/EXPOSURE_LEDGER.md` — sample snapshot, scope, classification,
   granularity, the outputs actually revealed, seal timing, and the
   authorization it was performed under. The log records what *did* happen; the
   step-3 declaration recorded what was *planned*, and a divergence between them
   is itself reportable.
7. **Classify the downstream evidence** under the accepted rules: the evidence
   context (T3 or T4) is fixed by §1's rule — when the outcome occurred relative
   to the seal, never when it was fetched — and the holdout is thereafter
   recorded as burned for that claim family.

**Why the order is written out.** An earlier revision of this procedure listed
"read the outcome" as step 4 and "Aaron authorises" as step 6. That ordering
would have permitted a builder to open a holdout and seek authorization
afterwards, which is not authorization at all — the information is already out.
The defect was procedural only: **no protected data was accessed under it, and
`PROTECTED_FORWARD_DATA_OPENED = NO` has been continuously true.** It is
recorded here, rather than silently fixed, because the failure mode it would
have licensed is the exact one this document exists to prevent.

**Ordering invariant, stated so it survives a future edit:** in any revision of
this procedure, the step at which Aaron authorizes must have a strictly lower
number than every step that reads, computes or displays a protected outcome. An
edit that inverts them is a defect regardless of how the steps are worded.

**Access lineage.** A release records **who** read it and **on what authority**.
"This program did not download it" is not a protection claim (§5). Related-project
access counts: if another program on this machine has already evaluated outcomes
over the same period on the same instruments, the holdout is compromised for any
claim family that overlaps.

---

## §5 T3-vs-T4 classification of accrued data — the honest current answer

**`POST_BOUNDARY_EXPOSURE_STATUS = UNKNOWN_PENDING_AUTHORITATIVE_VERIFICATION`.**

Data after both boundaries exists at the vendors. Its exposure status is
**`UNKNOWN`**, and by the standing rule (`no record ⇒ UNKNOWN, never NONE`) it
must not be recorded as unexposed.

**What is explicitly insufficient to establish protection**, per Program v2 §0A's
T3 row and the workspace's standing rule:

- "No file was downloaded by this project."
- The absence of post-boundary files in this repository.
- The absence of a recorded exposure event.
- A clean scan of the repository for outcome artifacts.

**What would be needed** to classify accrued data as usable **T3**: a verified
account of (a) whether any related project on this machine has evaluated
outcomes over the same period on the same or overlapping instruments, and
(b) whether outcome-informed market knowledge held by the researcher bears on
the claim family in question. Neither has been established. Establishing it is a
**future authorised task**, and the `DATA_INVENTORY_SPEC.md` scope is where the
first half of it would be answered.

**Until then:**

- Accrued post-boundary history **may not be claimed as T3 held-out evidence**.
- It is **not** T4 either. **Accrued history is never relabelled prospective.**
- A **T4 clock starts per candidate at that candidate's seal**, and only then.

---

## §6 Revised adjusted historical prices — treatment

| Situation | Treatment |
|---|---|
| A refresh returns **identical** values over the overlapping period | The refresh extends coverage; the overlap is unchanged. Record the new snapshot hash and the verification that the overlap matched. |
| A refresh returns **different** values over the overlapping period | **It is a new dataset.** It gets its own dataset identity, its own snapshot record, and its own exposure lineage. Prior results are **not** restated on it, and the two are never mixed in one evaluation. |
| The overlap is **not checked** | The refresh is unusable for any claim that depends on comparability. Checking is cheap; not checking is not a neutral choice. |

This applies with force to the ETF panel, whose adjusted closes are
revision-prone by construction. It applies less to Databento settlement data,
which is not adjustment-based — but the rule is stated uniformly so that no
future session has to decide which case it is in under time pressure.

---

## §7 `UNKNOWN` treatment — the standing rule for this procedure

1. **No record ⇒ `UNKNOWN`, never `NONE`.** Per axis, per dataset, per claim
   family.
2. An `UNKNOWN` is **discharged by verification, never by argument.** A plausible
   inference that no exposure occurred does not convert `UNKNOWN` to `NONE`.
3. An `UNKNOWN` that a dependent gate needs **blocks that gate**, and only that
   gate. It does not block unrelated work.
4. `UNKNOWN` is recorded with **what would discharge it**, so a later session
   knows what to go and check. Every `UNKNOWN` in this file and in
   `WAVE0_VERIFICATION_RECORD.md` carries that.

---

## §8 What this procedure does NOT authorise

- Opening any protected outcome.
- Refreshing any panel.
- Reading any data after either frozen boundary.
- Purchasing any data.
- Treating accrued history as prospective.
- Starting any T4 clock (no seal exists).

**Nothing in §1–§7 was executed in Wave 0.** The mechanics are defined; the
locks are closed.

---

## §9 Append log

| Date (UTC) | Appended | By |
|---|---|---|
| 2026-09-07 | Procedure created at Wave-0 execution. Three-state separation §1; per-dataset snapshot identity §2 with the ETF partial-terminal-month finding verified from `src/signals.py` and `config.py:154`; refresh protocol §3; access and release §4; T3/T4 status `UNKNOWN_PENDING_AUTHORITATIVE_VERIFICATION` §5; revised-price treatment §6; `UNKNOWN` rule §7. | Wave-0 governance session (Claude Opus 5), under Aaron's `AUTHORIZE_WAVE_0_GOVERNANCE_EXECUTION` |
| 2026-09-07 | **ERRATUM — blocker B1, raised by the fresh GPT-6 Astra Wave-0 verifier and confirmed against bytes.** §4's ordered release procedure placed "Read the outcome" at step 4 and "Aaron authorises" at step 6, so the written order permitted protected access before authorization. §4 is corrected to the seven-step order in which authorization is step 4 and access is step 5, with the governing principle `AUTHORIZATION MUST PRECEDE PROTECTED OUTCOME ACCESS` stated above the steps and an ordering invariant stated below them. **Procedural repair only: no protected data was accessed under the defective ordering, no retroactive access is claimed, and `PROTECTED_FORWARD_DATA_OPENED = NO` was and remains true.** No other section was changed. | Wave-0 bounded repair session (Claude Opus 5), under Aaron's bounded-repair authorization |
