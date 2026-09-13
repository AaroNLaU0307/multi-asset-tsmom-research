# Time-Series Value — Phase A closure

**Date:** 2026-09-13 · **Seat:** Claude Opus 5, Main Agent
**Machine inventory:** [`VALUE_DATA_INVENTORY.json`](VALUE_DATA_INVENTORY.json)

```
VALUE_DATA_PIT_READINESS = OWNER_DATA_ACTION_REQUIRED
ONLY REMAINING BLOCKER   = Japan CPI
S1 NOT ENTERED
TARGET_OUTCOMES_COMPUTED = NO
```

The universe was **not** shrunk. Four of five instruments are fully supported;
one leg of one object is missing.

## Frozen credit decision

```
CREDIT_OBJECT = BAA10Y
LQD = INCLUDED        HYG = REMOVED_FROM_VALUE_UNIVERSE
DESCRIPTION = PUBLIC_CORPORATE_CREDIT_VALUATION_COMPONENT
```

This is an **explicit scientific redefinition**, not a substitution. The claim
may never be described as an OAS, as LQD/HYG Value, or as high-yield Value.

`BAA_MINUS_AAA` is **not an active fallback.** Fable's suggested
inspect-overlap-then-maybe-switch route is deliberately **not implemented**: any
credit-vs-duration overlap diagnostic is predeclared and
`DIAGNOSTIC / CLAIM-INTERPRETATION ONLY`. It may not switch the credit object,
drop credit, change weights, or retune anything. If the two objects prove
redundant that is recorded as a limitation, not repaired.

## Data status

| instrument | object | source · series | coverage | PIT | raw SHA256 |
|---|---|---|---|---|---|
| **SPY** | real earnings yield (inverse CAPE) | Shiller `ie_data.xls` | 1871.01 → 2026.09 | `PIT_DATA_ACQUIRED_BUT_LIMITED` | `044196dafe44c303…` |
| **TLT** | real yield | FRED `DFII20` | 2004-07-27 → 2026-09-10 | `PIT_READY` | `3f7eacaeb7a87532…` |
| **LQD** | public corporate credit valuation | FRED `BAA10Y` | **1986-01-02 → 2026-09-10**, 10,173 obs | `PIT_READY` | `375268efe0e3d880…` |
| UUP/FXY leg | US CPI | FRED `CPIAUCSL` | 1947-01 → 2026-08 | `PIT_FEASIBLE_WITH_DECLARED_LAG` | recorded |
| UUP leg | euro HICP | **ECB** `ICP.M.U2.N.000000.4.INX` | 1996-01 → **2025-12** | `PIT_FEASIBLE_WITH_DECLARED_LAG` | `9bfa365fe6dd664c…` |
| UUP leg | UK CPI | ONS `D7BT` | 1988-01 → 2026-07 | `PIT_FEASIBLE_WITH_DECLARED_LAG` | `f1f7e51e3f0565b2…` |
| UUP leg | Canada CPI | StatCan `18-10-0004` | 1914-01 → current | `PIT_FEASIBLE_WITH_DECLARED_LAG` | `19f2712264fcfda9…` |
| UUP leg | Sweden CPI | **SCB** `KPItotM` `000004VU` | 1980M01 → **2025M12**, 552 obs | `PIT_FEASIBLE_WITH_DECLARED_LAG` | `b1a4892b51f94a7b…` |
| UUP leg | Switzerland CPI | SNB `plkopr` | 1921-01 → 2026-07 | `PIT_FEASIBLE_WITH_DECLARED_LAG` | `b53104b4da3d7cc5…` |
| **UUP/FXY leg** | **Japan CPI** | — | **NOT ACQUIRED** | `PIT_NOT_RELIABLY_FEASIBLE` | — |

Nominal FX legs (`DEXJPUS`, `DEXUSEU`, `DEXUSUK`, `DEXCAUS`, `DEXSDUS`,
`DEXSZUS`, 1971 → 2026-09) were already verified and are unchanged.

### Credit publication lag — determined, not assumed

Zero lag was **not** frozen. On Sunday 2026-09-13 the latest observation for both
`BAA10Y` and `DGS10` is Thursday 2026-09-10, with Friday 2026-09-11 — a business
day — still absent. At least one business day of publication lag is therefore
directly observable. **Recommended rule:** at month-end decision timestamp *t*,
use the most recent observation dated on or before *t* − 1 business day.
Conservative, mechanically grounded, outcome-independent.

Neither component is a revised statistic — Moody's seasoned Baa yields and the
H.15 Treasury constant-maturity series are published as observed and not
restated — so unlike the Shiller and Cleveland-Fed inputs there is no vintage
problem here. Components `BAA` and `DGS10` are archived alongside so the spread
can be reconstructed independently.

### Euro area and Sweden end 2025-12 — an evaluation-window question

Both now come from their authoritative publishers, and both currently end
**2025-12**. This was confirmed independently two ways — ECB `lastNObservations`
on the index *and* the annual rate, and Eurostat `lastTimePeriod` — so it is the
true current end of those feeds, not a stale index base or a wrong geo/unit code.

That is an **evaluation-end parameter, not a blocker**: any evaluation window
ending on or before 2025-12 is fully supported by every acquired leg. It belongs
in the same Owner-decision class as the evaluation start.

The earlier Sweden failure was **my malformed POST body**, not a source problem;
reading the table's own metadata gave five `ContentsCode` options and `000004VU`
is the fixed index-number series.

### Japan — the one blocker

Routes attempted and exhausted: FRED's five OECD mirrors (all discontinued
2021-06/2022-04) · OECD public SDMX (403) · IMF IFS (DNS failure, `api.imf.org`
404, datamapper 403) · `stat.go.jp` English pages (only item-and-weight
*classification* lists and an errata table — not the index series) ·
`stat.go.jp` Japanese pages (zero data-file links) · e-Stat file-search pages
(JavaScript-driven, no direct links and no `statInfId` in the served HTML) ·
e-Stat catalogue API (requires a free `appId`).

I did not register an account, did not scrape an unofficial mirror, and did not
substitute another country's or an OECD mirror series.

**Smallest Owner action — either one, both free:**

1. Register a free e-Stat `appId` at `https://www.e-stat.go.jp/` and supply it; or
2. Manually download Japan's **national CPI, all items, monthly index** series
   (2020-base or 2025-base, all Japan) from e-Stat and drop the file into
   `data/value_raw/`.

With that leg, `UUP` and `FXY` both become reconstructible and Phase A passes.

```
UUP_FIXED_BASKET_RECONSTRUCTIBLE = NO   (JPY leg missing; other five legs present)
FXY_BILATERAL_RECONSTRUCTIBLE    = NO   (JPY leg missing)
DATA_PROVENANCE_VALIDATION       = PASS (every recorded raw file re-hashes)
```
