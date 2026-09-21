# CTA-EDGE-01-TA — MACRO CALENDAR DATA MANIFEST (S2)

```
LINEAGE   = CTA-EDGE-01-TA
STAGE     = S2, under the S2 metadata-only macro-calendar authorisation
SCOPE     = RELEASE DATES ONLY. No market price, no index level, no economic data
            VALUE was read, stored or used. Every field is a date, a release name or
            a URL.
PURPOSE   = the four sealed §G.3 covariates, and nothing else
```

This manifest is **additive**. It does not amend, replace or reinterpret the sealed
`TA_DATA_MANIFEST.md`, whose bytes are pinned in `TA_SEAL_MANIFEST.md` and are
unchanged.

---

## §1 What was fetched

```
RETRIEVED_AT_UTC = 2026-09-14T17:37:32Z
PAGES            = 39            RAW BYTES = 3,838,181
RAW DIRECTORY    = data/ta/macro_raw/   (git-ignored under the repository data/ policy)
RAW INDEX        = data/ta/ta_macro_raw_index.json
RAW INDEX SHA256 = 888a7374d6091d07c13a63fb1f3fc7722915c30e15bab17277470e639c86cf55
FETCHER          = research/extensions/ta/ta_macro_calendar.py   (command: fetch)
```

Every one of the 39 raw pages is individually pinned by sha256 inside the raw index,
and `build()` re-verifies each page against its pin before parsing it.

| source kind | pages | authority |
|---|---:|---|
| `BLS_YEAR` | 21 | `https://www.bls.gov/schedule/<year>/home.htm`, 2006–2026 |
| `BLS_YEAR_PDF` | 2 | `https://www.bls.gov/bls/bls<year>sched.pdf`, 2006 and 2007 |
| `FOMC_HISTORICAL` | 15 | `https://www.federalreserve.gov/monetarypolicy/fomchistorical<year>.htm`, 2006–2020 |
| `FOMC_CALENDARS` | 1 | `https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm`, 2021–2026 |

**Why two BLS formats.** The `/schedule/<year>/home.htm` pages for **2006 and 2007**
are navigation shells with no schedule table; for those two years the official annual
schedule is the PDF, and it is parsed structurally. 2008 onward is the HTML table. The
two formats agree where they meet — the 2006 PDF's trailing January-2007 rows and the
2007 PDF's own January rows reproduce the same dates, and 2008 from HTML continues the
same monthly cadence.

**All four Fed statement sources are read the same way**: only an anchor whose visible
text is exactly `Statement` (historical pages), or the first statement link following a
`Statement:` label (calendars page), is taken. Minutes, implementation notes and
projection materials are structurally excluded.

---

## §2 The normalised calendar

```
PATH        = research/extensions/ta/TA_MACRO_CALENDAR.csv      (TRACKED)
ROWS        = 755
SHA256      = 8f10675033267136cb2622bf80f2f6da8ca922c0e074fae4c09128a49b1c4789
BUILT BY    = research/extensions/ta/ta_macro_calendar.py       (command: build)
COLUMNS     = series · date · weekday · source · source_url · detail
CONTENT     = DATES AND RELEASE NAMES ONLY. No value of any published statistic.
```

| series | rows | span | per-year |
|---|---:|---|---|
| **CPI** | 251 | 2006-01-18 … 2026-12-10 | 12/yr, except **11 in 2025** |
| **NFP** | 251 | 2006-01-06 … 2026-12-04 | 12/yr, except **11 in 2025** |
| **FOMC** | 171 | 2006-01-31 … 2026-07-29 | 8/yr scheduled, 9–10 in 2007/2008/2010/2019/2020 |
| **QRA** | 82 | 2006-02-01 … 2026-05-06 | 4/yr |

By source: `BLS` 454 · `BLS_PDF` 48 · `FRB_HISTORICAL` 126 · `FRB_CALENDARS` 45 ·
`TREASURY_AUCTION_RECORD` 82.

**QRA is not fetched.** It is derived from the already-pinned Treasury auction record
as the `announcemt_date` shared by the original-issue 10-year note and 30-year bond of
the Feb/May/Aug/Nov refunding, and is written into this same committed calendar so the
run-time artifact is self-contained. It reproduces the S1-sealed tabulation exactly:
signed `−1` for 6 of the 213 primary windows, `0` for the other 207.

**Disclosed calendar facts, recorded rather than smoothed:**

- **2025 carries 11 CPI and 11 NFP release dates, not 12.** That is the official
  schedule, not a parse gap: the September CPI was released 2025-10-24, the September
  Employment Situation on 2025-11-20, no October Employment Situation was released, and
  the November CPI followed on 2025-12-18. The calendar records what happened.
- FOMC counts above 8 in a year are unscheduled statements, which are still post-meeting
  statements under the sealed §G.3 definition.
- The calendar extends past the last primary event (2026-05-13) because it is built by
  whole calendar years. Dates after the last return-bearing day simply never match.

---

## §3 The derived covariates

```
PATH      = research/extensions/ta/TA_MACRO_COVARIATES.csv      (TRACKED)
ROWS      = 213    (one per primary event)
SHA256    = 92cb21b269da66ff69f9e93540ffb2cba193d80496bf2f09887707a1aacfda04
COLUMNS   = t0 · calendar_month · year · cpi · nfp · fomc · qra
VALUES    = the sealed signed form, in {-1, 0, +1}
CROSSTAB  = research/extensions/ta/TA_MACRO_CROSSTAB.md
```

Built from this calendar plus the sealed event calendar plus the panel's trading grid
(a `Date` column read and a non-null presence mask — no price). **No return is
involved at any point.**

---

## §4 What was NOT acquired

Unchanged and still forbidden: NY Fed primary-dealer positions · ZN/ZB futures ·
when-issued Treasury prices · cash Treasury return data · NAV data · CFTC data · any
market outcome series of any kind. The S2 authorisation covers release **calendars**
only, and only the four the sealed diagnostic names.

---

## §5 Reproduction

```bash
python research/extensions/ta/ta_macro_calendar.py fetch    # re-fetch raw pages
python research/extensions/ta/ta_macro_calendar.py build    # -> the committed CSV
python research/extensions/ta/ta_macro_calendar.py report   # coverage summary
python research/extensions/ta/ta_s2_build.py                # covariates + crosstab
```

A re-fetch may return newer BLS/Fed pages, since both publishers extend their schedules
forward. That does not invalidate anything: the committed CSV is the artifact the
engine reads, and the raw index pins the exact bytes these rows were parsed from.
Re-parsing the 2006/2007 PDFs requires `pypdf` (recorded in `requirements.txt`); the
committed CSV needs no such dependency.
