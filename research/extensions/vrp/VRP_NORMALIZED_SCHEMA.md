# TSMOM-VRP-01 — NORMALIZED DATA SCHEMA

```
LINEAGE = TSMOM-VRP-01
LAYERS  = RAW (immutable, git-ignored, hash-pinned)
          -> NORMALIZED (derived in memory by vrp_raw/vrp_chain; re-derivable from the
             raw bytes alone, so it is never a separate source of truth)
RULE    = every normalized value points back to an exact raw SHA256 input via
          VRP_DATA_MANIFEST.md; nothing is normalised from an unpinned byte
```

## 1. Raw row (as published by Cboe)

| column | use |
|---|---|
| `Trade Date` | parsed as `YYYY-MM-DD` (current endpoint) or `M/D/YYYY` (archive) |
| `Futures` | the contract label, e.g. `F (Jan 2024)`; used as a POSITIVE identity check that the file served for a monthly expiry really is that monthly contract |
| `Settle` | **the official settlement — the only price field this lineage reads** |
| `Total Volume`, `Open Interest` | carried for diagnostics only; never a price |
| `Open`, `High`, `Low`, `Close` | **never read.** §A5 forbids last trade as a price; `check_no_last_trade_price` asserts the loader does not read them |

## 2. Normalized contract record

| field | derivation |
|---|---|
| `root` | `"VX"` (standard monthly only; no weekly, no mini for pricing) |
| `final_settlement_date` | the contract's own last settled row once expired (§L PRIMARY); for a still-listed contract, the rule-derived date (there is no final-settlement row yet) |
| identity key | `(root, final_settlement_date)` — §J.3; never the symbol string alone |
| `contract_month` | `YYYY-MM` delivery month |
| `settle_present` | `Settle` parses to a strictly positive number. A zero/blank `Settle` is **no official settlement** (Cboe publishes all-zero placeholder rows for listed-but-unsettled days) and triggers §F.4, not a price |
| `price_comparable` | `settle_quoted * M_quoted / 1000`, with `M_quoted` from the dated specification registry — never inferred from the prices themselves |

## 3. Chain day (the constant-maturity layer)

| field | derivation |
|---|---|
| `front_key` / `second_key` | the first and second eligible monthly contracts: `E_k` is the earliest monthly final settlement `> d`; front is `F_k`, second is `F_(k+1)` |
| `w_front` / `w_second` | `dr(d)/dt` and `1 - w_front` over `P_k = { business days d : E_(k-1) <= d < E_k }`; a pure function of the calendar |
| `front_price` / `second_price` | comparable settlements, with §F.4 carry-forward applied |
| `front_carried` / `second_carried` | TRUE when the day's value is a carried-forward prior official settlement; counted per contract per calendar month against the max of 2 |

## 4. Month status (§F.4 / §F.6)

A calendar month is VALID iff no held contract exceeds **2** carry-forward business days in
it and no held contract lacks a settlement entirely. §F.6's first eligible complete month is
the start of the maximal terminal run of valid months ending at the Stage-A last month —
determined from availability under this rule alone, never from outcomes.

Result on the acquired chain: **first eligible complete month = 2006-09**, and every month
from 2006-09 through 2026-08 is valid with **zero** carry-forward days.

## 5. What the normalized layer never contains

No return, no cumulative return, no basis, no carry, no roll yield, no average price, no
strategy quantity and no outcome of any kind. Stage A (`vrp_stage_a`) is the only module
that forms a return, and during S2 it refuses to run on real data.

