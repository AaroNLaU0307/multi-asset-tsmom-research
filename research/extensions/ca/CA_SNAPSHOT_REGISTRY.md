# CA_SNAPSHOT_REGISTRY — tracked snapshot identity record

```
RECORD_TYPE   = CA_SNAPSHOT_REGISTRY
ROLE          = CA_PREREGISTRATION_DRAFT.md §I.2 — the tracked, append-only record of
                snapshot IDENTITY. Market data itself is git-ignored (`.gitignore`: `data/`)
                for licensing reasons; this registry, not the files, is the committed record.
STATUS        = C-A S1 SEALED 2026-09-13T17:42:06Z; PIPELINE LIVE 2026-09-13T18:33:11Z.
APPEND_ONLY   = YES — rows are never edited, deleted or reordered.
```

**What this file is.** The durable identity of every snapshot this lineage pins:
path, byte size, SHA-256, verified first/last date, coverage, and provenance.

**What this file is not.** It is not a data file, not an exposure ledger (that is
`ops/EXPOSURE_LEDGER.md`), not evidence, and not an authorization.

---

## §1 Frozen historical panel — the pre-existing baseline

| field | value |
|---|---|
| dataset | `dataset.yfinance.multi-asset-etf-panel` |
| path | `data/close_prices_raw.csv` |
| SHA-256 | `3d2a7a56dbd92d4ff8138cfd894c87f5ac5ac088a11165db870673e0c05c3c31` |
| byte size | 3,298,252 |
| window | 1993-01-29 → **2026-06-12** (the frozen boundary) |
| shape | 8,400 rows × 30 tickers |
| authority | `research/extensions/LOCKBOX_PROCEDURE.md` §2.1 |
| status at this seal gate | **re-verified from bytes, UNCHANGED**, before and after the S_0 acquisition |

This panel is **never overwritten** (LOCKBOX §3.1). No process in this lineage
opens it for writing.

---

## §2 `S_0` — seal-time snapshot (CA §E.1)

```
ROLE  = pins what was available at the seal gate; establishes seal provenance;
        verifies the historical overlap against the frozen panel.
NOT   = not S_G · not the prospective scored sample · not T4 evidence ·
        not a target-performance run · not a reveal.
```

| field | value |
|---|---|
| artifact | `S_0` |
| path | `data/prospective/S0_20260913T165624Z.csv` |
| **SHA-256** | `c4a21dc86038f9f0d06e32a267810b46cb39d9dd3549c35ef3329c87f884d6fb` |
| byte size | 3,323,945 |
| acquisition started (UTC) | 2026-09-13T16:56:24Z |
| acquisition finished (UTC) | 2026-09-13T16:57:01Z |
| source | yfinance (Yahoo Finance), `Ticker.history(period="max", auto_adjust=True)`, per ticker — the same call shape as `src/fetch_data.py::_fetch_one`, so `S_0` and the frozen panel are comparable |
| acquisition runtime | Python 3.13.14 · pandas 3.0.3 · yfinance 1.4.1 |
| acquisition tool | `research/extensions/ca/ca_s0_acquire.py` (one-off S1 provenance tool; **not** the S2 prospective snapshot writer) |
| first date | 1993-01-29 |
| last date | **2026-09-11** |
| shape | 8,462 rows × 30 tickers |
| tickers requested / acquired | 30 / 30 (zero failures) |
| identity sidecar | `data/prospective/S0_20260913T165624Z.identity.json` |
| overlap record | `data/prospective/S0_20260913T165624Z.overlap.json` |
| exposure ledger | `ops/EXPOSURE_LEDGER.md` row 46, classification `NO_OUTCOME`, granularity `NONE` |

**`S_0`'s last observation is NOT required to equal `FORWARD_BOUNDARY`** (CA §E.1).
`FORWARD_BOUNDARY` is determined by `S_G` when go-live is later than the seal.

**Rows after the frozen boundary.** 62 rows, 2026-06-15 → 2026-09-11. These are
`POST_SEAL_UNSCORED_STATE_INPUT_ONLY` (CA §E.1) / `ACCRUED_UNVERIFIED_STATE_INPUT_ONLY`
(CA §F): they may update canonical state for a future first post-start decision,
they are **never scored**, they are **never** T3 and **never** T4, and they
contribute **zero** to `N_scored`.

---

## §3 `S_0` ↔ frozen-panel overlap verification (CA §E.1, LOCKBOX §6)

Compared at the **daily-return level**, per ticker, over the common window
`1993-01-29 … 2026-06-12`. Adjusted-close *prices* are expected to differ over an
overlap because every distribution rescales the whole prior series; a constant
multiplicative rescale leaves simple daily returns invariant, which is why the
contract specifies the return level.

| check | result |
|---|---|
| frozen rows / `S_0` historical rows / common rows | 8,400 / 8,400 / **8,400** |
| trading days present in only one panel | **0** (in either direction) |
| observations present on only one side, canonical 17 | **0** |
| max &#124;Δ daily return&#124;, canonical 17 | **3.389e-06** (TLT, 2005-07-05) |
| max &#124;Δ daily return&#124;, all 30 | 3.389e-06 |
| canonical objects agreeing **bit-identically** | **USO, UNG, GLD, FXY** — exactly the four canonical objects that pay no distribution |
| per-ticker price ratio (frozen ÷ `S_0`) | a near-constant per-ticker factor, 1.0000 – 1.0150, spread ≤ 4.4e-06 |

**Mechanical reading.** The discrepancy is present in exactly and only those
instruments that carry a distribution-adjustment chain, is of order 1e-6, and is
absent — to the last bit — where no such chain exists. That is the signature of
routine dividend back-adjustment accumulating rounding across a longer factor
chain, not of a vendor price correction. The calendar is identical and no
observation is missing on either side.

**Adjudicated 2026-09-14 under §J — `MECHANICAL_CORRECTION` (no action).**

The daily-return figures above are **enumeration evidence, not the test**. §J's
**Split / dividend back-adjustment** row names the decision quantity itself: *"The
locked-vs-recomputed position diagnostic measures any residual"*, class
`MECHANICAL_CORRECTION` (no action) **if `max |Δposition| ≤ 0.01` and no sign
flip**. That tolerance was already fixed by the contract; none was invented.

| §J condition | required | observed | |
|---|---|---|---|
| `max &#124;Δposition&#124;` | ≤ 0.01 | **1.348102e-04** | **PASS** (≈ 74× inside) |
| sign flip | none | **0** | **PASS** |

402 decision months (1993-01-31 … 2026-06-30), 6,477 position cells, zero cells
present on only one side. Tool: `ca_s0_position_diagnostic.py`; record at
`data/prospective/S0_20260913T165624Z.position_diagnostic.json`.

**Data boundary asserted, not assumed.** Both panels were truncated at
**2026-06-12 before any computation**, and the script asserts that zero
post-boundary rows entered the engine through prices, volatility windows or
momentum lookbacks. **No post-boundary signal, position, return, Sharpe, PnL,
drawdown or performance proxy was computed**, and only the two quantities §J names
were emitted.

`PC-1` in `CA_PREREGISTRATION_DRAFT.md` §Y is **CLOSED** on this basis.

---

## §4 `S_G` — go-live base snapshot

```
S_G_CREATED = YES  (2026-09-13T18:33:11Z, under Aaron's OD-9 C_A_GO_LIVE_AUTHORIZATION)
```

| field | value |
|---|---|
| artifact | `S_G` — GO-LIVE BASE SNAPSHOT |
| snapshot id | `S_G_20260913T183249Z` |
| path | `data/prospective/snapshots/S_G_20260913T183249Z.csv` (git-ignored: `data/`; identity pinned here) |
| **SHA-256** | `8e2e3de98384c470a3ffef947f3fee2b17893b25c8caacdbc15f371b5a768a35` |
| byte size | 1948685 |
| universe | the canonical **17**, all present |
| window | 1993-01-29 → 2026-09-11 |
| shape | 8,462 rows × 17 |
| source | yfinance, `Ticker.history(period="max", auto_adjust=True)` — the sealed acquisition path, same call shape as `S_0` |
| registered | before any scientific use, append-only |

`S_G` **determines `FORWARD_BOUNDARY`** because go-live is later than the seal
(§E.1): `PROSPECTIVE_START = max(SEAL, PIPELINE_GO_LIVE) = 2026-09-13 18:33:11+00:00`, and
`FORWARD_BOUNDARY = 2026-09-11`.

Neither `S_0` nor the frozen historical panel was overwritten — both re-verified
unchanged before and after registration.

**`S_0` → `S_G` lineage.** `S_0` (`c4a21dc8…`, 2026-09-13T16:56:24Z) is the
seal-time provenance anchor; `S_G` (`8e2e3de98384c470a3ffef947f3fee2b17893b25c8caacdbc15f371b5a768a35`, 2026-09-13T18:33:11Z) is the go-live base. Both
are pinned by SHA-256 in tracked state, giving an unbroken chain from the frozen
historical panel through the seal to the first prospective decision. Observations
between them are `POST_SEAL_UNSCORED_STATE_INPUT_ONLY`: they may update canonical
state, they are never scored, never retroactively T4, and contribute zero to
`N_scored`.

---

## §5 Append log

| date (UTC) | appended | by |
|---|---|---|
| 2026-09-13 | Registry created at the C-A final seal gate. §1 frozen-panel baseline re-verified from bytes; §2 `S_0` acquired, hashed and pinned; §3 overlap verified at the daily-return level with the result recorded and its adjudication deliberately left to the Owner as `PC-1`; §4 `S_G` explicitly not created. No strategy quantity computed; no outcome revealed; nothing sealed. | Claude Opus 5, C-A S1 final seal-gate preflight, under Aaron's `FINAL S1 SEAL GATE` instruction |
