# CTA-EDGE-04-MMV — RAW MACRO DATA MANIFEST (S1 FREEZE)

```
RECORD_TYPE   = RAW_DATA_MANIFEST
LINEAGE       = CTA-EDGE-04-MMV
RETRIEVED_UTC = 2026-09-16T19:37:24Z  ..  2026-09-16T19:37:36Z
SOURCE        = Federal Reserve Bank of St. Louis, FRED/ALFRED API
API_BASE      = https://api.stlouisfed.org/fred/
PRODUCER      = research/extensions/mmv/mmv_data_freeze.py
RAW BYTES     = data/mmv/  (git-ignored per .gitignore `data/`, hashes pinned here)
MANIFEST JSON = data/mmv/MMV_RAW_MANIFEST.json
  sha256      908e2d6deeceedf9d74f3cc684a5ab6b1224e5960887af082aba3329787706da

CREDENTIAL    = never printed, never written to any file, never committed.
  source      Windows User-scope persisted variable (the process environment carried a stale value)
  every recorded request parameter carries api_key = <REDACTED>
```

> This product uses the FRED(R) API but is not endorsed or certified by the Federal Reserve Bank of St. Louis.

**Nothing in this freeze computes a macro feature, composite, position, separability
figure or return.** Only raw provider bytes and structural coverage were produced.

---

## §1 The six sealed inputs — and only these

MMV-OD-2 forbids `CPIAUCSL`, `CPILFESL`, `PCEPILFE`, `FEDFUNDS`, `DGS2` and any traded
yield. None was requested.

| series | title | freq | SA | reference span | rows | vintages | vintage span |
|---|---|---|---|---|---:|---:|---|
| `INDPRO` | Industrial Production: Total Index | Monthly | Sea | 1919-01-01 → 2026-07-01 | 39,356 | 1,222 | 1927-01-26 → 2026-08-18 |
| `PAYEMS` | All Employees, Total Nonfarm | Monthly | Sea | 1939-01-01 → 2026-08-01 | 13,688 | 859 | 1955-05-06 → 2026-09-04 |
| `CPILFENS` | Consumer Price Index for All Urban Consumers | Monthly | Not | 1957-01-01 → 2026-08-01 | 848 | 358 | 1996-12-12 → 2026-09-11 |
| `DFEDTAR` | Federal Funds Target Rate (DISCONTINUED) | Daily, 7- | Not | 1982-09-27 → 2008-12-15 | 9,577 | 1 | 2008-12-15 → 2008-12-15 |
| `DFEDTARL` | Federal Funds Target Range - Lower Limit | Daily, 7- | Not | 2008-12-16 → 2026-09-16 | 18,895 | 5,108 | 2008-12-17 → 2026-09-16 |
| `DFEDTARU` | Federal Funds Target Range - Upper Limit | Daily, 7- | Not | 2008-12-16 → 2026-09-16 | 16,295 | 3,781 | 2014-04-03 → 2026-09-16 |

## §2 Pinned file identities

| file | sha256 | bytes |
|---|---|---:|
| `data/mmv/INDPRO.series.json` | `a1aec442891ded272d7497f327c7028ed4ca9d2fa40a2515271dc89f48b5e44b` | 662 |
| `data/mmv/INDPRO.observations.realtime.json` | `3f53f959e399e21a060c6c7ab04392b82950c916826a1c964472d8c78682ddd9` | 3,819,154 |
| `data/mmv/INDPRO.vintagedates.json` | `3173e3c439c7d7e8a4024ef9dfdf837fdf7268df94d67eb2185e60774f5d1a36` | 15,887 |
| `data/mmv/PAYEMS.series.json` | `b91405887b6e806d4984d13b0e6dd3da95b79ffe9c7ddafe7e01b066e341310a` | 2,107 |
| `data/mmv/PAYEMS.observations.realtime.json` | `c773c5681807fe0057dd66814aa18bfc03b8c0201be57a50f425b48e7c471bd6` | 1,321,009 |
| `data/mmv/PAYEMS.vintagedates.json` | `2c43dcf7bcbbbf0f8d75d810ca16131cdfc4a323b719a4493fd243c4aacad769` | 11,168 |
| `data/mmv/CPILFENS.series.json` | `bdcc84b7156397350d98c21ccd8397ceeb4b513b89e2f30cddf6ce773650eaf6` | 1,047 |
| `data/mmv/CPILFENS.observations.realtime.json` | `75c3c36306c109b11683d808471b30aa8061a2dfc0a4141a6668e6fe8b9ad2f4` | 81,468 |
| `data/mmv/CPILFENS.vintagedates.json` | `3dda86335026e37e63abfc68f9f0c8cb4f021d5414442ca454c178366dcb02bf` | 4,655 |
| `data/mmv/DFEDTAR.series.json` | `55b3aacd479f7452be145f48d7a886f04f5e48d6b427c84f4ae373525918c1c9` | 1,094 |
| `data/mmv/DFEDTAR.observations.realtime.json` | `bfaca909a51796fe61942aa6cf218b12f696d824f0d64712dab3c947ed71c50f` | 902,294 |
| `data/mmv/DFEDTAR.vintagedates.json` | `9f5ef60eab3fdbb7256b5294d0d87297eb3a9890e80461ef1750b4eca6ccd366` | 14 |
| `data/mmv/DFEDTARL.series.json` | `b40b3fbbbf3140dcad6caa5f93c8342905378462a97a63ee868434f8efeb4ceb` | 606 |
| `data/mmv/DFEDTARL.observations.realtime.json` | `a1096b552be2059a53e3864e20c16e3c0c61b714f7f601b6fe1e0f5dd29d5925` | 1,794,597 |
| `data/mmv/DFEDTARL.vintagedates.json` | `aae0e003cac41ca0e4e630fea229498108c0b4ba2abd90c857eb88275f31aee2` | 66,405 |
| `data/mmv/DFEDTARU.series.json` | `276da832a1297c82f31b1b56e97a3f7176ee049cbc681dc580116b8f8274a293` | 606 |
| `data/mmv/DFEDTARU.observations.realtime.json` | `36bbfb3efc9b8e82db415af0ddd74ae6544a74253ed8c82831b51de6396197e4` | 1,547,984 |
| `data/mmv/DFEDTARU.vintagedates.json` | `51c75a344b3b567aaaae429b6166be6c878f442bcebc15795c48b53f031d5f5a` | 49,154 |
| `data/mmv/MMV_RAW_MANIFEST.json` | `908e2d6deeceedf9d74f3cc684a5ab6b1224e5960887af082aba3329787706da` | 12,348 |

## §3 Request shape

```
series         GET fred/series?series_id=<SID>
observations   GET fred/series/observations?series_id=<SID>
                   &realtime_start=1776-07-04&realtime_end=9999-12-31
                   &output_type=1&limit=100000&offset=0..n
vintagedates   GET fred/series/vintagedates?series_id=<SID>&limit=10000&offset=0..n

output_type=1 over the FULL real-time range is ALFRED's compact revision history:
one row per (reference date, value-interval) carrying realtime_start / realtime_end.
The vintage as known on date t is exactly the rows with
    realtime_start <= t <= realtime_end
which is what MMV-OD-1 requires and what makes the rule mechanically provable.
```

**Fetch mode per series.** FRED caps `output_type=1` at 2,000 vintage dates per
window. The daily target-range series exceed that because every business day
**extends** them with a new observation, not because past values are revised. For
those, the series' own vintage list was sliced into groups of at most 1,500 and one
window requested per group; content is identical and only the request shape differs.

```
  INDPRO    single
  PAYEMS    single
  CPILFENS  single
  DFEDTAR   single
  DFEDTARL  chunked_by_vintage_list:4_windows
  DFEDTARU  chunked_by_vintage_list:3_windows
```

## §4 Structural coverage findings — recorded, not repaired

```
CPILFENS reference dates with NO value in ANY vintage:  ['2025-10-01']
  Recorded as a FACT. Its cause is NOT asserted here and must be confirmed at S2.
  It is already governed by MMV-OD-6 §11.7: a missing leg makes the cell UNDEFINED,
  never 0, and undefined cells must be COUNTED AND REPORTED.

Policy splice, verified mechanically:
  DFEDTAR  1982-09-27 .. 2008-12-15   n = 9,577
  DFEDTARL 2008-12-16 .. 2026-09-16   n = 6,484
  boundary CONTIGUOUS - no gap, no overlap, exactly the MMV-OD-2 splice date.

All other series: zero reference dates missing across all vintages.
```

## §5 The finding that stops the seal

The freeze itself succeeded. It also established that **ALFRED does not carry genuine
availability metadata for the administered policy leg** — see
[`MMV_S1_HOLD_RECORD.md`](MMV_S1_HOLD_RECORD.md) §10. That is a scientific question
about MMV-OD-1's semantics, not a data-acquisition problem, and it is why no
preregistration and no seal exist at this commit.
