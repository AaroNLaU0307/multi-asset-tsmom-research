# DATA_INVENTORY_SPEC.md — TSMOM-EXT-001

**Program:** TSMOM extension (`TSMOM-EXT-001`)
**Created:** 2026-09-07 (Wave 0 governance execution, authorised by Aaron)
**Implements:** `TSMOM_EXTENSION_RESEARCH_PROGRAM_v2.md` §2, row
"Data-inventory specification (defined, not run)"

```
STATUS = SPECIFICATION ONLY — NOT EXECUTED
EXECUTION = REQUIRES A SEPARATE AARON AUTHORISATION
```

**This document defines a task. Wave 0 did not run it, and running it is not
part of Wave 0.** Program v2 §2 says so in terms: *"Running it is a separately
authorised task."*

---

## §1 Why this exists, and the language rule it enforces

Two deferred decisions — **D1** (financial futures) and **D2** (long-history
futures) — turn on **what Aaron already owns**. Nobody has checked. The correct
current statement is therefore:

> **`not established as owned; inventory pending`**

and **not** *"financial futures not acquired"*, which asserts a fact nobody has
verified. Map v2 §A.5 and §G already use the correct form; this specification
exists so the inventory that would settle it is defined rather than improvised,
and so the epistemically correct language survives contact with a future session
in a hurry.

**Language rule, binding on anything this task produces:** an item is
`OWNED` only when a file, a manifest or a vendor entitlement record was actually
observed. Everything else is `NOT_ESTABLISHED_AS_OWNED` or
`UNKNOWN_PENDING_INVENTORY`. **`NOT_OWNED` is never written from absence of
evidence.**

---

## §2 Scope

### §2.1 Locations to enumerate

| # | Root | Notes |
|---|---|---|
| 1 | `C:\Users\Aaron\OneDrive\Desktop\Quant trade\` — the whole workspace | Every project repository, including `data/` directories inside each |
| 2 | `C:\Users\Aaron\quant-data\` | Known external root. Observed subdirectories at spec time: `commodity-carry`, `databento-archive`, `itsf-registry`, `itsf-runs`, `itsf-runs-archive`, `registry-witness`, `review`, `tools` |
| 3 | Vendor account entitlements | Databento (and any other vendor) account-side dataset entitlements and download history — **catalogue and manifest only** |
| 4 | Vendor download manifests already on disk | e.g. `commodity-carry-research/data/MANIFEST.md`, `_carry-research-workspace/batch_staging/*/manifest.json`, `_carry-research-workspace/manifest_perfile_*.json` |
| 5 | Prior purchase records | e.g. `commodity-carry-research/docs/samples/COST_LEDGER.md` — what was actually billed, and for what |
| 6 | Any other root Aaron names at execution time | The list above is what a Wave-0 session could see; it is not asserted to be exhaustive |

### §2.2 Fields to record, per dataset

| Field | Notes |
|---|---|
| `dataset_id` | KB id where one exists; otherwise a provisional local id marked as provisional |
| `vendor` / `dataset_code` | e.g. Databento `GLBX.MDP3` |
| `instruments` | Symbols/roots actually present, enumerated — not the symbols that were *requested* |
| `exchanges` | |
| `date_coverage` | First and last date **actually present**, distinguished from the requested range |
| `schema(s)` | e.g. `ohlcv-1d`, `statistics`, `definition`, `mbp-10` |
| `raw_vs_continuous` | Raw per-contract series vs a stitched/continuous series, and if continuous, **which stitching rule** |
| `contract_definitions` | Whether `definition` records (or equivalent contract specs: tick, multiplier, price-unit divisor, expiry calendar) are present |
| `open_interest_availability` | Present / absent / partial — this gates OI-crossover roll rules |
| `units` | Price units and the divisor needed to reach dollars; the single most common source of silent accounting error |
| `provenance` | Manifest path, generation timestamp, SHA-256 (per-file or aggregate) |
| `licensing` | Redistribution and retention terms as recorded by the vendor agreement |
| `size_bytes` / `file_count` | |
| `known_prior_research_exposure` | Which programs have consumed it, what they revealed, and any frozen trial count — **cross-referenced to `relationships.csv`, each project's `SAMPLE_REUSE.md`, and `TRIAL_LEDGER.md`; never re-derived independently** |
| `ownership_status` | `OWNED` \| `NOT_ESTABLISHED_AS_OWNED` \| `UNKNOWN_PENDING_INVENTORY` — under §1's language rule |

### §2.3 Specific questions the inventory must answer

1. **Financial futures** — ES/NQ/RTY/YM, ZT/ZF/ZN/ZB/UB, 6E/6J/6B/6A/6C/6S/6N,
   NKD: present anywhere, at any coverage? (Gates **D1**; needed by X04, X10 and
   any hybrid deployment universe.)
2. **Pre-2008 futures history**: present anywhere? (Gates **D2**; would be the
   only route to context **T2**.)
3. **Open interest** for the 18 commodity roots: present in the existing
   `statistics` corpus? (Gates the OI-crossover roll rule and the Wave-1 roll
   diagnostics.)
4. **Exchange initial-margin tables and micro-contract specs**: any dated
   snapshot on disk? (Needed by X05/X32 feasibility; public data, no purchase.)
5. **OHLC (not close-only)** for the ETF universe: available for range-based
   volatility? (Optional for X35a; the existing cache is close-only.)
6. **Duplicate or overlapping corpora**: the same vendor bytes present under more
   than one root, which would let one sample be double-counted as two.

---

## §3 Access boundary — binding on the executing session

**Catalogues, manifests and metadata only.**

| Permitted | Forbidden |
|---|---|
| Directory listings, file sizes, file counts | Opening any protected performance outcome |
| Reading manifests, cost ledgers, entitlement records | Refreshing any panel, or fetching any new data |
| Reading contract-definition and specification metadata | **Purchasing anything** |
| Computing file hashes | Decoding market data records beyond what a header/metadata read requires |
| Reading **first and last dates** and record counts | Reading price levels or computing any return, statistic or strategy output |

**Precedent for the metadata-only mode:** `mean-reversion-research`'s
Databento cost analysis performed *"DBN-header metadata inspection only — no
price record decoded"* and recorded the fact. The same standard applies here.

**Exposure logging:** the inventory task appends its own row to
`ops/EXPOSURE_LEDGER.md` before it runs, and the expected classification is
`NO_OUTCOME` / `PURE_MECHANICAL_VERIFICATION`. If the executing session finds
itself about to read an outcome, that is a **halt**, not a reclassification.

---

## §4 Output

A single **ownership table** — one row per dataset, the §2.2 fields — written to
`research/extensions/DATA_INVENTORY.md`, feeding **D1** and **D2**.

The output must state, for each of §2.3's six questions, one of: the verified
answer with its evidence; `NOT_ESTABLISHED_AS_OWNED`; or
`UNKNOWN_PENDING_INVENTORY` with what would discharge it.

**The output is an input to Aaron's decisions. It is not itself a decision, and
it authorises no acquisition.**

---

## §5 What this specification does not do

- It does not run the inventory.
- It does not authorise a purchase. **D1 and D2 remain deferred**, and Map v2 §K
  records for both: *"no purchase authorised"*.
- It does not assert what is or is not owned.
- It does not open protected data.

---

## §6 Append log

| Date (UTC) | Appended | By |
|---|---|---|
| 2026-09-07 | Specification created at Wave-0 execution. Scope §2, access boundary §3, output §4. **Not executed.** | Wave-0 governance session (Claude Opus 5), under Aaron's `AUTHORIZE_WAVE_0_GOVERNANCE_EXECUTION` |
