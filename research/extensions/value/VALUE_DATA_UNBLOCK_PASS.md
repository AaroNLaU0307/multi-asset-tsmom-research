# Time-Series Value — bounded data-source unblock pass

**Owner decision acted on:** preserve the original six-instrument design; one
bounded unblock pass; free / authoritative / legally reproducible sources first;
no purchase and no licensed commitment without a separate decision.
**Date:** 2026-09-13 · **Seat:** Claude Opus 5, Main Agent
**Scope:** credit (LQD/HYG) and FX (UUP/FXY) only. SPY and TLT untouched.

```
CREDIT_DATA_UNBLOCKED    = NO
FX_DATA_UNBLOCKED        = NO
VALUE_DATA_PIT_READINESS = OWNER_DATA_DECISION_REQUIRED
TARGET_OUTCOMES_COMPUTED = NO
S1 NOT ENTERED
```

Data feasibility only. Nothing was joined to a return series; no signal, PnL,
Sharpe, correlation or premise statistic exists.

---

## Credit — NO

The accepted object is an option-adjusted (or economically equivalent) spread
for IG and for HY *separately*.

| candidate | source | object | coverage | verdict |
|---|---|---|---|---|
| ICE BofA `BAMLC0A0CM` / `BAMLH0A0HYM2` | FRED | true OAS, correct exposures | rolling ~3y only | licence forbids reproduction; window truncated (established last pass) |
| **Gilchrist–Zakrajšek** `gz_spread`, `ebp` | **Federal Reserve Board**, FEDS Notes `ebp_csv.csv` | single aggregate US corporate credit spread from secondary-market bond prices, duration-matched synthetic risk-free leg | **1973-01 → 2026-07, monthly, 643 obs** | free, authoritative, documented, reproducible — but **not** the accepted object |
| Moody's `BAA10Y` / `AAA10Y` | FRED | seasoned long corporate yield minus 10y Treasury | 1986 / 1983 → 2026-09 | not OAS; maturity and composition mismatch; **no HY counterpart exists at all** |

**Why GZ does not unblock credit.** It is one aggregate series. It does not
separate investment grade from high yield, so it cannot supply two distinct
objects for LQD and HYG, and its constituent universe is a research sample of
senior unsecured bonds rather than the indices those ETFs track. Using it would
answer a *different* credit-valuation question.

```
IG : FREE_SOURCE_EXISTS_BUT_SCIENTIFIC_REDEFINITION_REQUIRED
HY : NO_FREE_EQUIVALENT_SOURCE_FOUND  ->  PAID_LICENSED_SOURCE_REQUIRED
```

High yield is the hard blocker: no free, authoritative, reproducible HY OAS with
usable history was found. The standard sources (ICE BofA, Bloomberg) are
licensed. `fed_gz_ebp.csv` was retrieved **as a candidate only and is not
adopted**; the record marks it `adopted: false`.

---

## FX — NO, but materially closer than the previous pass

The previous pass concluded foreign CPI was dead (Japan discontinued 2021-06,
four currencies stale since 2025-03/04 on FRED's OECD mirrors). That was true of
*FRED's mirrors*, not of the underlying official statistics. Going to the
national sources changes the picture.

| economy | official source | series | coverage | PIT class | status |
|---|---|---|---|---|---|
| **US** | FRED | `CPIAUCSL` | 1947-01 → 2026-08 | `PIT_FEASIBLE_WITH_DECLARED_LAG` | ✅ |
| **Switzerland** | **Swiss National Bank** `data.snb.ch` | cube `plkopr`, `LD2010100` | **1921-01 → 2026-07**, 1267 obs | `PIT_FEASIBLE_WITH_DECLARED_LAG` | ✅ |
| **United Kingdom** | **UK ONS** | `D7BT` CPI all-items 2015=100 | **1988-01 → 2026-07**, 463 obs | `PIT_FEASIBLE_WITH_DECLARED_LAG` | ✅ |
| **Canada** | **Statistics Canada** | table `18-10-0004` | 1914-01 → current | `PIT_FEASIBLE_WITH_DECLARED_LAG` | ✅ |
| **Euro area** | Eurostat | `prc_hicp_midx`, CP00 | 1996-01 → **2025-12** | unresolved | ⚠️ no 2026 periods returned for any `unit` or `geo` tried |
| **Sweden** | Statistics Sweden | `PR0101A/KPItotM` | metadata lists → 2025M12 | unresolved | ⚠️ observation query needs a correctly shaped POST |
| **Japan** | Statistics Bureau / e-Stat | CPI index, national | — | **unresolved** | ❌ no keyless programmatic route found |

**Japan is the blocker, as it was last time.** `2025base-list.xlsx` turned out to
be the item and weight *classification* list, not the index series — it was
downloaded, inspected, found to be the wrong object, and deleted rather than
recorded as CPI. e-Stat's `file-download` endpoint does serve files without a
key, but locating the CPI index series requires the catalogue API, which needs a
free `appId` — i.e. account registration, which I must not perform on Aaron's
behalf.

Without Japan both FX objects fail: FXY is bilateral JPY, and JPY is 13.6% of the
USDX basket UUP tracks.

```
UUP_FIXED_BASKET_RECONSTRUCTIBLE = NO   (JPY missing; EUR and SEK unresolved)
FXY_BILATERAL_RECONSTRUCTIBLE    = NO   (JPY missing)
```

Nominal FX legs are all confirmed good (FRED `DEXJPUS`, `DEXUSEU`, `DEXUSUK`,
`DEXCAUS`, `DEXSDUS`, `DEXSZUS`, 1971 → 2026-09). Per §4 no BIS changing-weight
effective index was substituted for the fixed-basket object.

---

## What would unblock what

1. **Japan CPI** — a free e-Stat `appId` (registration only, no payment) would
   almost certainly close Japan, and with it both FX objects. *Aaron must
   register it; I must not create accounts.* Alternatively a manual one-off
   download of the national CPI index series into `data/value_raw/`.
2. **Euro area and Sweden** — API parameter work on sources already confirmed
   reachable. Likely solvable without any new provider or any decision.
3. **HY credit** — no free route found. Preserving the accepted object requires a
   licensed feed (ICE BofA or Bloomberg). This is the only blocker that appears
   to need money rather than effort.
4. **IG credit** — free only by redefining the object (GZ spread, or a Moody's
   spread). Not adopted; requires an explicit scientific decision.

---

## Provenance

Raw snapshots under `data/value_raw/` (git-ignored, per the existing convention),
pinned by `sha256_of_raw_file_on_disk` in
[`VALUE_DATA_INVENTORY.json`](VALUE_DATA_INVENTORY.json).

| file | sha256 | note |
|---|---|---|
| `swiss_cpi_snb.csv` | `b53104b4da3d7cc5…` | SNB, adopted-eligible |
| `uk_cpi_ons_D7BT.json` | `f1f7e51e3f0565b2…` | ONS, adopted-eligible |
| `canada_cpi_statcan_18100004.zip` | `19f2712264fcfda9…` | StatCan, adopted-eligible |
| `euro_hicp_eurostat.json` | `a415bb22e67820a8…` | Eurostat, **stale at 2025-12** |
| `sweden_cpi_scb_meta.json` | `80be2e74a43a0e09…` | SCB **metadata only**, not observations |
| `fed_gz_ebp.csv` | `cc51b2747654e3ed…` | **candidate only, NOT adopted** |

No ICE BofA bytes are retained anywhere. The Japan classification file was
deleted. Licensing was treated as ambiguous-until-clear rather than assumed
favourable.
