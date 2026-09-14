# CTA-EDGE-02-BENB — S0 DATA-RESOLUTION + DESIGN-REPAIR RECORD

```
LINEAGE              = CTA-EDGE-02-BENB
CANDIDATE            = BOND_ETF_NAV_BASIS
STAGE                = S0 DATA-RESOLUTION + DESIGN-REPAIR PASS   (NOT S1)
S0_REPAIR_STATUS     = PASS
CREATED              = 2026-09-15
AUTHOR               = Claude Opus 5 (Main Agent / builder seat)
AUTHORITY            = QUANT_WORKFLOW_VNEXT.md (workspace root)
ORIGINAL S0 ARTIFACT = research/extensions/benb/BENB_S0_FRAME.md
                       PRESERVED BYTE-FOR-BYTE, sha256
                       5dabf6fc8af3b1c7455db72b468537428b9ca11d0188c68481e5c96b97a03b73
S1_SEAL_CREATED            = NO
BUILD_STARTED              = NO
RUN_AUTHORIZATION_CREATED  = NO
BASIS_COMPUTED             = NO
ABNORMAL_BASIS_COMPUTED    = NO
REGRESSION_RUN             = NO
BACKTEST_RUN               = NO
```

> **ORIGINAL S0 HOLD = ACCEPTED BUT SUPERSEDED on decomposition and primary-sample
> design.** `BENB_S0_FRAME.md` is not rewritten. It stands as the accepted S0 direction
> and as provenance; every statement this record supersedes is enumerated in §8 below,
> and a superseded statement has no force. Where the two disagree, **this record wins**.

---

## 1. The blocker is cleared

The original S0 returned HOLD on one blocker: *"the lineage has no usable price input"* —
the local panel is dividend-adjusted, with no raw close and no open — compounded by NAV
publication timing that could not be established at issuer authority.

Under the Owner's S0 data authorisation, all three legs are now resolved.

```
RAW_PRICE_SOURCE = Yahoo Finance daily bars via yfinance, auto_adjust=False,
                   actions=True  (the repository's existing price authority, used here
                   in its UNADJUSTED mode rather than the panel's adjusted mode)
NAV_SOURCE       = iShares / BlackRock issuer "Data Download" workbook,
                   worksheet "Historical" - the issuer's own daily per-share NAV
```

### 1.1 Raw price footing — RESOLVED

| | HYG | LQD |
|---|---|---|
| `RAW_CLOSE_AVAILABLE` | **YES** | **YES** |
| `RAW_OPEN_AVAILABLE` | **YES** | **YES** |
| `RAW_HIGH_LOW_AVAILABLE` | **YES** | **YES** |
| rows | 4,888 | 6,070 |
| coverage | 2007-04-11 … 2026-09-14 | 2002-07-30 … 2026-09-14 |
| index timezone | America/New_York | America/New_York |
| missing `Open` on a price date | **0** | **0** |
| **stock splits in history** | **0** | **0** |
| distribution rows | 232 | 289 |
| capital-gain distribution rows | **0** | **0** |

**The unadjusted footing is verified, not assumed.** `Close` differs from `Adj Close` on
**4,879 of 4,888** HYG rows and **6,061 of 6,070** LQD rows, and the two are equal on the
final row — the signature of a series that is *not* dividend-adjusted, with the
adjustment factor accumulating backwards from the present. Because both funds have
**zero splits** in their entire history, `Close` is additionally free of any split
ambiguity: raw close and split-adjusted close are identical objects here.

`P_close,t` is therefore **the regular-session official closing market price**, which is
the object the issuer itself uses in its premium/discount line graph: *"the daily closing
price for shares of the fund … The closing prices are determined by the fund's listing
exchange."*

*(A second iShares convention exists and is deliberately NOT used: the premium/discount
bar chart uses "the midpoint between the highest bid and the lowest offer on the listing
exchange, as of the time that the Fund's NAV is calculated". Our design uses the exchange
official close. The choice is fixed here so no builder faces it.)*

### 1.2 NAV footing — RESOLVED

```
DAILY_NAV_AVAILABLE (HYG) = YES        DAILY_NAV_AVAILABLE (LQD) = YES
```

The issuer workbook contains five worksheets — `Disclaimers`, `Holdings`, **`Historical`**,
`Performance`, `Distributions`. The `Historical` sheet is a daily series with exactly four
columns:

```
As Of  |  NAV per Share  |  Ex-Dividends  |  Shares Outstanding
```

| | HYG | LQD |
|---|---|---|
| data rows | **4,893** | **6,077** |
| coverage | **2007-04-04 … 2026-09-11** | **2002-07-22 … 2026-09-11** |
| first NAV date vs fund inception | 2007-04-04 = **inception** | 2002-07-22 = **inception** |
| unparseable dates | 0 | 0 |
| duplicate dates | 0 | 0 |
| empty or `--` NAV cells | **0** | **0** |
| rows per year | 250–254 (full trading calendar) | 250–254 |
| ex-dividend rows | 233 | 289 |

```
per-share NAV      = YES, six decimal places
currency           = USD
valuation date     = the "As Of" date
official issuer NAV = YES - this is BlackRock's own published NAV, not a vendor estimate
total-return adjusted = NO. It is the raw per-share NAV; distributions leave the fund
                     and the NAV falls accordingly, with the amount given in the
                     Ex-Dividends column on the same row.
```

**This overturns the original S0's concern.** That draft recorded that only a *quarterly*
premium/discount artefact appeared to be published. That was wrong: the issuer's Data
Download carries the **full daily NAV history from fund inception**, and it was found by
reading the product page's own data API rather than its rendered HTML.

**NAV revision policy — NOT ESTABLISHED, and declared.** A single vintage was retrieved,
so whether BlackRock ever restates a historical NAV cannot be determined from it. The
mitigation is mechanical rather than editorial — **fetch once, pin by sha256, and never
re-read a live endpoint** — which is the treatment the Treasury auction record received.
The consequence for claims is recorded in §6.

### 1.3 NAV timing — RESOLVED, and it is the load-bearing result

```
NAV_VALUATION_TIME  = 16:00 ET
NAV_PUBLICATION_TIME = same day, AFTER the close; operationally available in the
                       clearing system at approximately 18:30 ET
PUBLICATION_CHANNEL  = NSCC / ETF agent distribution on trade date; issuer website the
                       following business day
EARLIEST_NAV_KNOWABLE_TIME = the EVENING of day t, circa 18:30 ET
```

Three independent authorities, each quoted rather than inferred:

1. **iShares, on its own product page:** *"Close of Trading Times: The NAV of funds
   normally is calculated using prices as of 4:00 p.m. eastern time. Each fund normally
   trades on its respective stock exchange until 4:00 p.m. eastern time."*
2. **DTCC ETF processing timeline:** *"Pricing is available at approximately 6:30 PM"* on
   the trade date, after which instructions stream to Universal Trade Capture.
3. **SEC Rule 6c-11, per SEC staff guidance ADI 2025-15:** an ETF must post *"its current
   NAV, market price, and premium or discount each as of the end of the **prior business
   day**"* — i.e. the public website carries `NAV_t` on day *t+1*.

```
CAN NAV_t BE KNOWN BEFORE THE SAME DAY'S REGULAR-SESSION CLOSE?   NO.
```

Not merely by convention — **deductively**. `NAV_t` is computed *from* 16:00 ET prices, so
it cannot exist before 16:00 ET, and the fund trades until exactly that instant. The DTCC
timeline then places practical availability at ~18:30 ET.

```
EARLIEST_REALISTIC_EXECUTION = the OPEN of day t+1.
```

`NAV_t` is knowable roughly **fifteen hours before** the open of *t+1*, so the §12 HOLD
condition does **not** fire: the signal is reliably available before the entry mark, with
a wide margin, on every trading day. The horizon is **not** shifted.

```
POINT_IN_TIME_RECONSTRUCTIBLE = YES
BASIS_FOOTING_VALID           = YES
```

---

## 2. The repaired decomposition — exact, and checked

```
b_t  =  ln( P_close,t / NAV_t )          raw exchange close over official issuer NAV
```

Both legs are per-share values of the same object struck at the same instant (16:00 ET),
and both are raw. Then:

```
R_OVERNIGHT,t+1 = ln( P_open,t+1  / P_close,t  )
R_TRADABLE,t+1  = ln( P_close,t+1 / P_open,t+1 )
R_NAV,t+1       = ln( NAV_t+1     / NAV_t      )

DECOMPOSITION_IDENTITY
   delta_b(t -> t+1)  ==  R_OVERNIGHT + R_TRADABLE - R_NAV
```

**Algebra.** `b_{t+1} − b_t = ln(P_close,t+1/P_close,t) − ln(NAV_{t+1}/NAV_t)`, and the
close-to-close price move splits through the open without residue:
`ln(P_close,t+1/P_close,t) = ln(P_open,t+1/P_close,t) + ln(P_close,t+1/P_open,t+1)`.
Substituting gives the identity. It is exact for any positive prices and NAVs — no
approximation, no assumption, no error term.

**Checked mechanically on SYNTHETIC values**, 200,000 random draws:

```
max | delta_b - (R_OVERNIGHT + R_TRADABLE - R_NAV) |  =  1.776e-15
```

i.e. floating-point only. **No real price or NAV value entered this check.**

**Why the split matters, stated once.** The original S0 regressed the *close-to-close*
ETF return on the lagged signal. That return begins at `close(t)` — before the signal
exists. The overnight segment is therefore unreachable by any trader acting on `NAV_t`,
and folding it into the dependent variable would have credited the strategy with a move
it could never have captured. The three-component form separates exactly that segment out.

---

## 3. The repaired primary sample — discount side only

```
PRIMARY_SAMPLE            = observations with x_t < 0 ONLY
DISCOUNT_SEVERITY_DEFINITION = d_t = -x_t  > 0
FEATURE_FORM              = CONTINUOUS.  No threshold beyond the sign of x_t.
                            No 1 %, no percentile, no decile, no stress cutoff.
PREMIUM_SIDE_ROLE         = DESCRIPTIVE_ONLY · PROMOTION_POWER = NONE ·
                            NO RESCUE POWER · never enters the classification
```

The original S0's full-sample symmetric regression is **rejected as primary**. The
economic claim is one-sided — a discount is the state in which someone is paid to supply
liquidity to forced sellers — and the estimand must be estimated on the states the claim
is about. Premium observations are reported for completeness and can never rescue,
promote or qualify the result.

---

## 4. The repaired primary estimands

For discount observations only, with `d_t = −x_t > 0`:

```
A.  OVERNIGHT PRICE DISCOVERY   (diagnostic)
      R_OVERNIGHT,t+1 = a_O + beta_O * d_t + e
      beta_O > 0  =>  the ETF price converges in the predicted direction, but BEFORE
                      the next-day open. Real information, NOT harvestable from a
                      NAV_t signal.

B.  TRADABLE PRICE CONVERGENCE  ***PRIMARY***
      R_TRADABLE,t+1 = a_T + beta_T * d_t + e
      PREDICTED SIGN: beta_T > 0
      PRIMARY_IDENTIFICATION_COEFFICIENT = beta_T
      Only beta_T can support a harvestable edge.

C.  NAV CATCH-DOWN              (diagnostic)
      R_NAV,t+1 = a_N + beta_N * d_t + e
      beta_N < 0  =>  the NAV falls toward the price: the stale-NAV alternative.
```

All three are OLS, on the **same discount-only sample**, with the **same regressor**,
estimated **separately**. No joint model, no instrument, no controls, no interactions.

```
OVERNIGHT_DIAGNOSTIC      = beta_O    (PROMOTION_POWER = NONE)
NAV_STALENESS_DIAGNOSTIC  = beta_N    (PROMOTION_POWER = NONE)
```

**Classification concept, fixed before outcomes:**

| case | condition | reading |
|---|---|---|
| **A — STALE NAV** | `beta_N` materially < 0 while `beta_T` does not support positive tradable convergence | NAV catches down. Not harvestable. **Not** a statement that the ETF was mispriced |
| **B — OVERNIGHT PRICE DISCOVERY** | `beta_O` materially > 0 while `beta_T` does not support positive tradable convergence | the ETF price corrects, but before a `NAV_t` signal can be traded. Real information, not harvestable under the observed timing |
| **C — TRADABLE PRICE CONVERGENCE** | `beta_T` materially > 0 | the only case that proceeds to the Gate-2 economic test |
| **D — MIXED** | more than one component moves materially | the question remains whether `beta_T` survives once `beta_O` and `beta_N` are explicitly measured |

The unstable `PRICE_SHARE` ratio proposed in the original S0 is **withdrawn entirely** and
is not reported even as a descriptive: a ratio whose denominator can cross zero cannot
carry a reading that is fixed before outcomes.

---

## 5. Horizon, ex-dates and the normalisation rule

```
PRIMARY_HORIZON   = ONE SESSION
SIGNAL_KNOWABLE_AT = evening of day t, circa 18:30 ET (NAV_t published)
ENTRY              = OPEN of day t+1
EXIT               = CLOSE of day t+1
```

No 2-day, 5-day or 10-day variant. No holding-period sweep. One horizon, and it is the
first one the signal can reach.

### 5.1 Ex-date treatment — deterministic, and it protects the primary

**Verified mechanics, not assumed.** The issuer's `Ex-Dividends` column gives the
per-share distribution on each ex-date; the price source's `Dividends` column gives the
same event independently. The two calendars agree almost exactly — **232 of 233** HYG
dates and **288 of 289** LQD dates match — and **neither fund has ever made a
capital-gain distribution** (0 rows in both), so the ex-date family is dividends only.

On an ex-date the NAV falls by the distribution because the cash leaves the fund, and the
price gaps down at the open for the same reason. The consequence is asymmetric across the
three components:

- `R_NAV` across an ex-date carries a mechanical drop that is not an economic loss →
  **`beta_N` would be biased**;
- `R_OVERNIGHT` carries the ex-open gap → **`beta_O` would be biased**;
- `R_TRADABLE` runs **open → close on t+1**, entirely after the gap → **structurally
  immune**.

So the primary coefficient is already protected; the two diagnostics are not. Rather than
introduce a distribution add-back — which would break the exact identity of §2 — the rule
excludes the affected transitions:

```
EX_DATE_TREATMENT
   EXCLUDE observation t whenever day t+1 is an ex-date for that fund, where the
   ex-date family is the UNION of
       (i)  the issuer's Ex-Dividends column, and
       (ii) the price source's Dividends column.
   The union is used because it is strictly the more conservative of two pinned,
   independent calendars. Observation t is NOT excluded for being an ex-date itself:
   b_t is well defined on an ex-date, since both legs are struck ex.
```

This keeps the §2 identity **exact on every retained observation**, is defined entirely
by two pinned files, is independent of any outcome, and costs about 5 % of the sample.

### 5.2 Normalisation rule — verified implementable, NOT computed

```
BASIS_DEFINITION          = b_t = ln( P_close,t / NAV_t )
ABNORMAL_BASIS_DEFINITION = x_t = b_t - m_t
NORMALISATION_RULE        = m_t = MEDIAN{ b_s : s <= t-1 }, EXPANDING, recomputed daily,
                            using information strictly before t
MINIMUM_HISTORY_RULE      = x_t exists only once 250 prior common-date observations of
                            b_s are available; earlier observations are EXCLUDED, never
                            imputed and never back-filled
UPDATE TIMING             = b_t is knowable in the evening of day t; m_t uses data through
                            t-1 only; therefore x_t is knowable in the evening of day t
```

**It was NOT computed in this task.** Only its implementability was checked, against the
mechanical hazards the task named:

| hazard | finding |
|---|---|
| NAV missing days | **0** empty or `--` NAV cells in either fund's entire history |
| ETF holidays / market closure mismatch | the issuer strikes a NAV on a handful of days the exchange is shut — HYG carries NAV on **2024-03-29 (Good Friday)** and **2024-03-31 (a Sunday)**. Handled by intersecting on dates where **both** a NAV and a trading day exist; the rule is stated once and needs no case work |
| stale issuer dates | the NAV file ends 2026-09-11 while prices run to 2026-09-14 — an ordinary vintage lag, which the intersection removes |
| fund distributions | §5.1 |
| pre-listing NAV | HYG has NAV for 2007-04-04…04-10 before its first trade; LQD for 2002-07-22…07-29. Removed by the same intersection |

```
The definition is implementable deterministically. No rolling alternative was invented.
```

---

## 6. Data pinning

Raw bytes live under `data/benb/`, which is **git-ignored** by the repository's blanket
`data/` policy, and are pinned here by sha256 — the treatment the Cboe VX chain received.
The BlackRock workbook additionally carries an explicit licence restriction
(*"solely for your personal, non-commercial use … you may not copy, distribute, modify,
post, frame or deep link this content"*), which the ignore policy already satisfies.

```
RETRIEVED_AT_UTC (price) = 2026-09-14T18:25:57Z
RETRIEVED_AT_UTC (NAV)   = same session, 2026-09-14
```

| file | bytes | sha256 |
|---|---:|---|
| `ishares_HYG_fund_download.xml` | 4,675,317 | `10dcd91e095a56d83762019738aa5b14374ea5d1f723616636b52170150ec533` |
| `ishares_LQD_fund_download.xml` | 8,845,823 | `d0cc3b0121806b20a227b00ae50d3f8523e6cc560e7bae16d715824b50ce0a47` |
| `HYG_raw_ohlc.csv` | 648,827 | `1ed30697cd0c665d9abe3d60abfe8c03314fb8889f3a459df207c5b85cb3bce8` |
| `LQD_raw_ohlc.csv` | 824,802 | `9d120233fd18bbd28188c18ce5a99b8347416f58b903d7452b83b47d011fe036` |
| `HYG_nav_daily.csv` (normalised pass-through) | 155,726 | `7735da958ef10522e39c9138b8cf8c686206585f3b805c327588fb61e9eae5de` |
| `LQD_nav_daily.csv` (normalised pass-through) | 198,877 | `3d78dbd80b92e9715eb9f6249597d65556d12b6517aad6832640e7296698007a` |
| `benb_price_meta.json` | 695 | `8179c06f8f8dd088d3b08cb9b4d6a1a8abbd210239f3e2b226e70de223d8b339` |

Endpoints, for reproduction:

```
NAV   https://www.blackrock.com/varnish-api/blk-one01-product-data/product-data/api/v1/
      get-fund-document?appType=PRODUCT_PAGE&appSubType=ISHARES&targetSite=us-ishares&
      locale=en_US&portfolioId={239565 HYG | 239566 LQD}&component=fundDownload
PRICE yfinance Ticker(<TICK>).history(period="max", auto_adjust=False, actions=True)
```

The normalised NAV CSVs are a **pass-through**: date, `nav_per_share`, `ex_dividend`,
`shares_outstanding`, sorted ascending. No value is transformed, rounded, filled or
joined to any price.

```
EVIDENCE CEILING (unchanged)   = supported
NAV VINTAGE CLASSIFICATION     = RECONSTRUCTED_HISTORICAL_SERIES_WITH_NON-VINTAGE_
                                 LIMITATION.  One retrieved vintage; restatement cannot
                                 be excluded. No positive result may ever be described
                                 as strict vintage-PIT confirmation.
SAMPLE REUSE                   = UNCHANGED BY THIS TASK. No outcome test has run, so no
                                 burn count moves. The ETF PRICE leg remains the burned
                                 panel lineage context; the NAV leg is newly acquired.
                                 Mixed provenance does NOT create independent
                                 confirmation.
```

---

## 7. Point-in-time alignment audit — DATE-ONLY

Counts only. No price, NAV, basis or return was touched.

| | HYG | LQD |
|---|---:|---:|
| NAV dates | 4,893 | 6,077 |
| price dates | 4,888 | 6,070 |
| **common dates** | **4,887** | **6,069** |
| common span | 2007-04-11 … 2026-09-11 | 2002-07-30 … 2026-09-11 |
| price dates with **no NAV** | 1 *(2026-09-14, vintage lag)* | 1 *(same)* |
| NAV dates with **no price** | 6 *(4 pre-listing; 2024-03-29 Good Friday; 2024-03-31 Sunday)* | 8 *(6 pre-listing; 2 non-trading)* |
| missing next-day **open** | **0** | **0** |
| after 250-day burn-in, with a next trading day | 4,636 | 5,818 |
| excluded because *t+1* is an ex-date | 221 | 279 |
| **STRUCTURALLY ELIGIBLE** | **4,415** | **5,539** |
| eligible span | 2008-04-08 … 2026-09-10 | 2003-07-28 … 2026-09-10 |
| calendar years represented | **19** | **24** |

**These are structural eligibility counts, not sample sizes for the primary claim.** The
primary sample is the *discount-side subset* of these observations, and its size cannot be
known without computing the basis — which this stage forbids. It will be established at
S1/S2 as an outcome-free tabulation of the regressor's sign, before any dependent variable
is touched. The original S0's inherited "15–25 independent episodes" remains **advisory and
unverified** and is not promoted to a fact here.

---

## 8. What this record supersedes in `BENB_S0_FRAME.md`

| # | original S0 statement | status | replacement |
|---|---|---|---|
| 1 | §G blocker: "the lineage has no usable price input" | **CLEARED** | §1 — raw OHLC and issuer daily NAV both acquired and pinned |
| 2 | §B.3 / §G: NAV publication time "NOT ESTABLISHED at issuer authority" | **CLEARED** | §1.3 — valuation 16:00 ET (issuer), availability ~18:30 ET (DTCC), website *t+1* (SEC Rule 6c-11) |
| 3 | §B.3 note that only a **quarterly** premium/discount artefact appeared to be published | **FACTUALLY CORRECTED** | §1.2 — the issuer publishes the **full daily NAV history from inception** |
| 4 | §C.5 two-component estimand `(B_P, B_N)` on the close-to-close price return | **DEAD** | §2, §4 — three components; `R_TRADABLE` is the primary and begins at the open of *t+1* |
| 5 | §C.5 `PRICE_SHARE` reported as a descriptive | **WITHDRAWN ENTIRELY** | §4 — an unstable ratio is not reported at all |
| 6 | §C.5 identification regression estimated on the **full symmetric sample** | **DEAD** | §3 — discount-only primary sample, `d_t = −x_t` |
| 7 | §C.9 "the identification regression is estimated on the FULL sample; only the GATE 2 position is one-sided" | **DEAD** | §3 — the split is now at the estimand, not only at the position |
| 8 | §C.3 "raw-vs-raw makes the ex-date problem vanish" | **TOO STRONG** | §5.1 — it vanishes for `b_t` and for `R_TRADABLE`, but **not** for `R_NAV` or `R_OVERNIGHT`; a deterministic exclusion is therefore defined |
| 9 | §C.6 `REALISTIC_ENTRY_POSSIBLE_WITH_EXISTING_DATA = NO` | **SUPERSEDED** | §1.1 — raw opens now exist; entry at `open(t+1)` is implementable |
| 10 | §C.10 "15–25 independent episodes" | **STILL UNVERIFIED** | §7 — retained as an advisory planning range only |

**Not superseded and carried forward unchanged:** the primary research question and its
two-gate structure (§C.1); the instrument selection and its reasoning, including the LQD
policy-confound argument (§C.2); the basis definition (§C.3); the abnormal-basis
transform (§C.4); the outcome taxonomy A–F (§C.7); the uncertainty and fragility plan
(§C.12); distinctness (§C.13); and the forbidden interpretations (§F), which remain
binding in full.

---

## 9. Cost and materiality — NOT sealed

```
TRANSACTION_COST_RULE_STATUS = PROVISIONAL
M1_STATUS                    = PROVISIONAL
```

The 5 bps one-way / 10 bps round-trip proposal and the `beta_T >= 0.10` bar are carried
forward **unchanged and unsealed**. They were **not** revised using any historical data —
no price or NAV value informed them, and none could have, because no basis was computed.

One observation relevant to the Owner's decision, from data already in hand and requiring
no outcome: the design's entry is at the **open** and its exit at the **close** of the same
session. That is a single-session round trip in an instrument whose documented 30-day
median bid/ask is 0.01 %, but whose economically relevant states are exactly those in
which that spread widens. The cost question is therefore real and the Owner's choice
between a fixed conservative number and a state-dependent convention is material.

```
The controller decides M1 at the next acceptance step. Nothing here pre-empts it.
```

---

## 10. Firewall statement of record

For this lineage, at this stage:

- **no basis, abnormal basis, premium/discount history, episode count, plot, regression,
  coefficient, P&L, Sharpe or strategy result was computed, read or inferred;**
- **historical raw prices and historical NAV values were never joined**; the only
  cross-file operations performed were **set operations on dates** and **counts**;
- price values were examined only as *schema* facts — column presence, non-null counts,
  `Close` versus `Adj Close` inequality counts, split and distribution row counts — and
  never as levels, returns or comparisons against NAV;
- NAV values were examined only as *format patterns* (decimal-place classes) and
  *non-null counts*, never as levels;
- the three-component identity was checked on **synthetic random numbers**;
- March 2020 was not inspected, singled out, filtered for, or looked at in any way;
- canonical TSMOM was not modified and **C-A was not accessed**;
- `BENB_S0_FRAME.md` was not modified — its sha256 is unchanged.

```
HISTORICAL_PRICE_VALUES_INSPECTED_FOR_OUTCOME = NO
HISTORICAL_NAV_VALUES_INSPECTED_FOR_OUTCOME   = NO
BASIS_COMPUTED = NO · ABNORMAL_BASIS_COMPUTED = NO · REGRESSION_RUN = NO
BACKTEST_RUN = NO · S1_SEAL_CREATED = NO · RUN_AUTHORIZATION_CREATED = NO
```

---

## 11. S0 PASS conditions — item by item

| condition | result |
|---|---|
| raw unadjusted HYG close exists | **YES** — 4,888 rows, zero splits, `Close` ≠ `Adj Close` on 4,879 |
| HYG next-day open exists | **YES** — 0 missing opens among eligible observations |
| official daily HYG NAV exists | **YES** — 4,893 rows from inception, 0 gaps |
| `NAV_t` point-in-time reconstructible | **YES** — one pinned vintage; non-vintage limitation declared |
| publication timing proves the signal is knowable before the next-day open | **YES** — ~18:30 ET on day *t*, ~15 hours of margin |
| date-only alignment mechanically feasible | **YES** — 4,415 structurally eligible HYG observations, 19 years |
| basis footing economically coherent | **YES** — raw/raw, same 16:00 ET instant, issuer NAV |
| distribution treatment deterministic | **YES** — union ex-date exclusion, two pinned calendars |
| three-component decomposition exact | **YES** — max residual 1.8e-15 on 200,000 synthetic draws |
| primary discount-only sample fully specified | **YES** — `x_t < 0`, `d_t = −x_t`, continuous, no threshold |
| no outcome inspected | **YES** — §10 |
| no scientific choice left to an S1 builder on timing, decomposition or sample side | **YES** |

LQD carries no data issue of its own and remains the **declared secondary with NO rescue
power**. It was not promoted and could not have been: HYG's own data leg is complete.

```
S0_REPAIR_STATUS = PASS
NEXT = AARON / CHATGPT ACCEPTANCE -> CTA-EDGE-02 S1 DESIGN + SEAL
```
