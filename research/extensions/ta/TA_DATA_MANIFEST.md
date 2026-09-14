# CTA-EDGE-01-TA — DATA MANIFEST

```
LINEAGE   = CTA-EDGE-01-TA
SCOPE     = every data object this lineage is bound to at the S1 seal
AUTHORITY = research/extensions/ta/TA_PREREGISTRATION.md §L
GRANT     = TA-OD-5, the limited S1 auction-metadata authorisation (CONSUMED)
```

Any receiver recomputes every hash below before use. Chat-carried bytes are never a
source of truth.

---

## §1 Acquired under the S1 grant — official Treasury auction metadata

```
SOURCE            = U.S. Treasury Fiscal Data -- "Treasury Securities Auctions Data"
DATASET PAGE      = https://fiscaldata.treasury.gov/datasets/treasury-securities-auctions-data/
ENDPOINT          = https://api.fiscaldata.treasury.gov/services/api/fiscal_service
                    /v1/accounting/od/auctions_query
ACCESS            = open; no account, no API key, no token
QUERY FILTER      = auction_date:gte:1990-01-01,
                    auction_date:lte:2026-06-12,
                    security_type:in:(Note,Bond)
QUERY SORT        = auction_date,cusip          PAGE SIZE = 10000
RETRIEVED_AT_UTC  = 2026-09-14T16:55:38Z
ROWS              = 2,373
LOCAL PATH        = data/ta/ta_auctions_raw.json   (git-ignored under the repository's
                                                    data/ policy; pinned here)
BYTES             = 1,006,030
SHA256            = e807f06647c420f22f7654186e076cf15cebac2a6be7de16d8d1a5fbbcaba552
FETCHED BY        = research/extensions/ta/ta_auction_fetch.py  (command: fetch)
LICENCE           = U.S. Government work; public domain. No redistribution constraint.
                    Held out of git only to respect the repository's blanket data/ rule.
REVISION POLICY   = the dataset is "Released As Needed". Auction dates and security
                    identity are announced in advance and are not revised. The
                    mitigation is mechanical, not editorial: fetched ONCE and pinned,
                    and nothing downstream ever re-reads a live endpoint.
```

### §1.1 Fields requested — 13, and what was deliberately NOT requested

```
REQUESTED  cusip · security_type · security_term · original_security_term ·
           announcemt_date · auction_date · issue_date · maturity_date ·
           reopening · inflation_index_security · floating_rate ·
           cash_management_bill_cmb · offering_amt

NOT REQUESTED, although the grant would have permitted them:
           high_yield · bid_to_cover_ratio · primary_dealer_accepted ·
           direct_bidder_accepted · indirect_bidder_accepted · comp_accepted ·
           price_per100 · low_yield · avg_med_yield · and every other auction
           OUTCOME field of the dataset's 114.

The sealed design does not use auction outcomes. Requesting them would have widened
this lineage's data surface for no design gain.
```

---

## §2 Derived and tracked — the sealed event calendar

```
PATH        = research/extensions/ta/TA_EVENT_CALENDAR.csv     (TRACKED in git)
ROWS        = 557   (245 PRIMARY 30-Year rows + 312 SECONDARY on-cycle 10-Year rows)
SHA256      = b27be5b1d94cfc13fc8310e0d5216675e097a2245fc954e4b12ed282563f7cb6
BUILT BY    = research/extensions/ta/ta_auction_fetch.py   (command: build)
INPUTS      = the raw extract in §1  +  the frozen ETF panel's Date column and
              non-null presence mask (see §3)
CONTENT     = DATES AND METADATA ONLY. No price, no return, no statistic, no outcome.
EOL         = LF, covered by .gitattributes `*.csv text eol=lf`, so the working-copy
              sha256 above is also the git-blob identity and reproduces from any
              checkout regardless of core.autocrlf.
```

Columns: `cell · instrument · tenor_family · auction_date · cusip · security_term ·
original_security_term · remaining_term_days · reopening · announcemt_date ·
issue_date · offering_amt · t0_is_trading_day · valid_window · exclusion_reason ·
pre_open · pre_close · post_open · post_close · t0_index · iso_year · iso_week ·
calendar_month · qra_in_window · qra_signed · ann_in_window · ann_signed ·
ovl_2Year · ovl_3Year · ovl_5Year · ovl_7Year · ovl_10Year · ovl_20Year ·
ovl_30Year · ovl_TIPS · ovl_FRN`.

---

## §3 Bound but not acquired — the frozen ETF panel

```
PATH        = data/close_prices_raw.csv            (git-ignored; pinned by the programme)
SHA256      = 3d2a7a56dbd92d4ff8138cfd894c87f5ac5ac088a11165db870673e0c05c3c31
COVERAGE    = 1993-01-29 .. 2026-06-12, 8,400 rows, 30 adjusted-close series
SAMPLE ROW  = SAMPLE_REUSE.md KB-1 (burned 6 of 6) + the CTA-EDGE-01-TA addendum
```

**How this lineage has touched it, and only this.** `ta_auction_fetch.trading_calendar()`
reads the `Date` column and a **non-null presence mask** for TLT, IEF, SHY and SPY. The
numeric close is inspected solely to ask *"is this cell empty?"* and is never retained,
returned, differenced or aggregated. No price and no return has left that function.

Derived and asserted at every build:

```
COMMON GRID = 6,007 trading days, 2002-07-30 .. 2026-06-12, ZERO internal gaps.
              TLT, IEF, SHY and SPY have an IDENTICAL date set inside that range.
              common_grid() re-asserts this and raises if it ever stops holding.
```

---

## §4 Declared, NOT acquired — the S2 macro-calendar contract

Required by the sealed §G.3 identification diagnostic and by nothing else.

| calendar | authority | status |
|---|---|---|
| CPI news-release dates | U.S. Bureau of Labor Statistics official release-schedule archives | **NOT ACQUIRED** |
| Employment Situation news-release dates | U.S. Bureau of Labor Statistics official release-schedule archives | **NOT ACQUIRED** |
| FOMC post-meeting statement dates | Board of Governors of the Federal Reserve System official FOMC calendars | **NOT ACQUIRED** |

All three are free and public. **Acquisition needs a separate Owner data
authorisation at S2.** TA-OD-5 is consumed and does not cover them. Failure to acquire
any of the three is a **LEVEL-1 PRE-RUN FAILURE** (contract §P) — never a silent skip,
and never an assumption that the diagnostic would have passed.

The fourth covariate, **QRA**, needs no acquisition: it is derived from §1 as the
`announcemt_date` shared by the original-issue 10-year note and 30-year bond of the
Feb/May/Aug/Nov refunding — 139 dates, 1990-01-31 … 2026-05-06.

---

## §5 Forbidden data — unchanged by this manifest

NY Fed primary-dealer positions · ZN/ZB futures · when-issued Treasury prices · cash
Treasury return data · NAV data · CFTC data · any other new research dataset.

---

## §6 Reproduction

```
python research/extensions/ta/ta_auction_fetch.py fetch     # -> §1 (re-fetch; the
                                                            #    hash pins the seal's
                                                            #    bytes, not a re-fetch)
python research/extensions/ta/ta_auction_fetch.py build     # -> §2, must reproduce
                                                            #    b27be5b1...7cb6
python research/extensions/ta/ta_prereg_validate.py         # mechanical seal check
```

A re-fetch may legitimately return more rows than §1 if Treasury has since published
new auctions; that does **not** invalidate the seal, because the sealed event calendar
is bound to the pinned bytes of §1 and the research calendar is frozen at
`2026-06-12`. The validator rebuilds from the **pinned** raw file and requires
`b27be5b1…7cb6` exactly.
