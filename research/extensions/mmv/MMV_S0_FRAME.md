# CTA-EDGE-04-MMV — S0 FRAME

**MACRO MOMENTUM ON VINTAGE DATA**

```
LINEAGE (provisional)      = CTA-EDGE-04-MMV
WORKING NAME               = MACRO_MOMENTUM_VINTAGE
ORIGIN                     = Fable Round-1 discovery map, family F5
STAGE                      = S0 FRAME  (research-question definition only)
DATE                       = 2026-09-16
BRANCH                     = cta-edge/macro-momentum-vintage-s0
PARENT COMMIT              = e6ece03980617d19527bfd4ac5e35dfdd42c5d8e  (PINS closure)

S0_FRAME_STATUS            = HOLD
HOLD_REASON                = MMV-OD-1, the REAL-TIME INFORMATION CONCEPT. F5 says
                             "on point-in-time (ALFRED) vintages" and never confronts
                             the difference between a chain of FIRST RELEASES and a
                             SINGLE VINTAGE SNAPSHOT as-of the decision date. Both are
                             point-in-time, both are mechanically reconstructible, and
                             they encode different theories of what the investor
                             responds to. The task's §8 names this exactly.

MACRO_FEATURE_COMPUTED = NO   CANDIDATE_POSITION_COMPUTED = NO
RETURN_OUTCOME_ACCESSED = NO  REGRESSION_RUN = NO   BACKTEST_RUN = NO
S1_SEAL_CREATED = NO   BUILD_STARTED = NO   RUN_AUTHORIZATION_CREATED = NO
```

This document defines a research question from an existing authority. It is not a
design, not a contract, not an implementation and not a result.

---

# A. REPOSITORY FACTS

*Verified from bytes in this repository and on this machine.*

## A.1 The F5 authority — located and hash-verified, not reconstructed

```
FILE    Quant trade/2026-09-15-cta-edge-discovery-r1-mechanism-feature-map-fable-01.md
        635 lines · 97,240 bytes
sha256  02ca5f45fe41763e55a353090645c3b2a98b6dcf5fce572623ede604e569344a
        Re-verified at the opening of this session; unchanged since the CTA-EDGE-04
        candidate audit.
F5      §1 lines 224–262 (full entry) and §4 lines 541–553 (RESEARCH_PRIORITY = 4)
```

`ORIGINAL_F5_EXACT_NAME = MACRO_MOMENTUM_VINTAGE`

### The exact F5 text, extracted

**Candidate name (field 1), verbatim:**

> `MACRO_MOMENTUM_VINTAGE` — the 12-month change in a small predeclared set of macro
> series, mapped to asset-class direction by a table fixed from theory before any data,
> sign-only, on point-in-time (ALFRED) vintages with a fixed release-lag rule.

**Economic mechanism (field 2), verbatim:**

> Markets underreact to slow-moving changes in growth, inflation and policy the way they
> underreact to price: releases are noisy, lagged and revised; consensus and
> institutional allocation update over quarters. A sleeve that trades the *direction of
> change* in fundamentals earns the premium for acting on slow information before the
> consensus catches up. **Who pays:** investors and mandates that update slowly; **why it
> persists:** release lags and revisions are permanent, and inputs change monthly, so it
> cannot be crowded at price speed.

Distinctness stated in the same field: *"Distinct from Value (a level against own
history, closed materially adverse) and from the yield-curve overlay (a level used as a
gate)."*

**Proposed variables, transformation and mapping (field 3), verbatim:**

| feature | variable and transform | mapping |
|---|---|---|
| **F5.a Growth momentum** | 12-month change in industrial production and in payrolls (vintage) | → long equity / credit, short duration |
| **F5.b Inflation momentum** | 12-month change in core CPI or core PCE (vintage) | → short duration, long commodities, long dollar |
| **F5.c Policy momentum** | 12-month change in the policy rate or the 2-year yield (unrevised) | → short duration, long dollar, short equity |
| **F5.d Cross-country differentials** | growth/inflation differentials for non-US legs, those economies' own vintage series | the only out-of-sample replication available without buying data |

> Most defensible: **F5.b and F5.c** (inflation and policy) because their asset mappings
> are the least theory-ambiguous; growth-to-bond mapping flips sign in disinflationary
> booms.

**Cheapest falsification (field 8), verbatim — this is the object §10 of the brief asks
to be recovered rather than improvised:**

> PnL-free first: the monthly sign-agreement between the macro composite and the
> canonical composite, per instrument and pooled, over months ≤ 2026-06-12; if agreement
> exceeds a declared bound (about 80 %) the sleeve is the core's bet restated — stop,
> `not_promoted`, reason `not_separable_at_position_level`. Then the premise: forward
> sign-aligned return per unit risk of the macro composite pooled across the four mapped
> classes, one family of five, BH-FDR, with a leave-one-macro-episode-out jackknife
> defined from the vintage series before any return is seen.

**Known failure modes (fields 7, 11, 13, 15), verbatim:**

* *"about 10–15 macro turning points in the US … perhaps 15–20 effective turns in total
  … the power is low and the honest terminal state may be `unresolved`."*
* *"Macro data lag prices by one to two months: in 2020-03 every growth-momentum reading
  was still positive when prices crashed, so the sleeve would have been long risk into
  the crash and would have co-lost with the core's static long component."*
* *"The series-to-asset mapping is the dominant degree of freedom; any cell revised after
  a disappointing result makes the study unfalsifiable. Position-level collapse into the
  static bet. Vintage alignment defects."*
* Abandon immediately if *"the position-level screen fails … which makes the rest of the
  study a confirmation of X45 rather than a new source."*

**Parked inside F5:** F5.d (cross-country replication) is offered but not ranked;
`UNRATE` appears in the data list with no feature attached to it.

### A discrepancy inside the authority, surfaced rather than repaired

```
F5 field 3 (the scientific statement)  "12-month change in core CPI or core PCE"
F5 field 5 (the data list)             "ALFRED vintages for CPIAUCSL, PCEPILFE, ..."

CPIAUCSL is HEADLINE CPI (all items). The core CPI series is CPILFESL.
```

Field 3 is the scientific statement and says **core**; field 5 names a **headline**
series. This frame does **not** silently pick one. §C.3 proposes following field 3 (core)
and records the discrepancy for controller confirmation, because headline CPI carries
food and energy — which is the part of inflation that moves fastest and is most
correlated with the commodity leg the mapping already trades.

## A.2 What data already exists here

| asset | status | verified from |
|---|---|---|
| **Canonical monthly signal panel** | **ON DISK.** `output/monthly_signal_panel.csv`, 17 tickers × 402 monthly rows, 1993-01-31 … 2026-06-30. `output/monthly_position_weights.csv` same shape. | file read (header and row count only) |
| **Canonical signal spec** | `MOMENTUM_LOOKBACKS_MONTHS = (1, 3, 6, 12)`, `SIGNAL_RESAMPLE = "ME"` (month-end close), `SIGNAL_COMBINE = "mean"` | `config.py:152–158` |
| **ETF price panel** | `data/close_prices_raw.csv`, 30 series, 8,400 rows, 1993-01-29 … 2026-06-12 (frozen) | file read (header only) |
| **Unrevised market rates** | `data/DGS2.csv`, `DGS10.csv`, `DGS3MO.csv` on disk; the Value inventory classifies these as *"Market-observed quote. Published next business day and not revised, so a one-business-day lag is sufficient and no vintage problem arises."* | `VALUE_DATA_INVENTORY.json` |
| **Foreign CPI, credit spreads, FX** | `data/value_raw/` — CPIAUCSL, CPIAUCNS, CPALTT01JPM661S, BAA, BAA10Y, DEX* FX, DFII*, DGS20/30 | directory listing |
| **ALFRED vintage data** | **NONE.** No vintage file of any kind exists in this repository or on this machine. | directory inventory |
| **ALFRED-aware code** | **NONE.** `value_data.py`, `src/yields.py` and `config.py` contain no `realtime_start`, `realtime_end`, `vintage_dates` or `output_type` parameter. | grep |

**The single most useful repository fact for this lineage**, and it is a warning the
programme has already written down once:

> `VALUE_DATA_INVENTORY.json`: `pit_classification = PIT_DATA_ACQUIRED_BUT_LIMITED`,
> because *"the history is RECONSTRUCTED, not vintage … the real series is deflated with
> the CURRENT CPI vintage rather than the CPI that was published at the time."*

The closed Value lineage already hit the reconstructed-versus-vintage wall and recorded
it. MMV is the first lineage in this programme whose entire premise is to **not** make
that substitution. That is the reason §B.1 below is the load-bearing section.

## A.3 The frozen benchmark this lineage must be distinguished from

```
CANONICAL TSMOM = FROZEN RESEARCH BENCHMARK. Not modified, not touched, not re-run.
  17 ETFs in 5 sleeves; mean-of-signs of 1/3/6/12-month returns; 60-day vol sizing;
  equal weight; portfolio vol target and gross cap; month-end decision held one month;
  2 bps one-way. Evaluated 2008-05 → 2026-06 (218 months).
  SUPPORTED — NOT INDEPENDENTLY CONFIRMED.
```

Two measured properties of the core bind this design and were established before it
(both already-revealed T0 programme context, restated from the F5 authority §0.2):

* **X45** — the hindsight static average-position book has Sharpe 0.776 against 0.783 for
  the full book; the timing residual retains 19.5 %; average net exposure is **+0.93, long
  bonds/credit (+0.57) and equity (+0.28)**, with SHY / HYG / LQD / SPY net long 61–74 %
  of months. *Consequence:* any same-stream conditioner has a ceiling of roughly
  **0.15 Sharpe**, and any "new" signal that ends up long bonds, credit and equity most of
  the time is the core's static bet restated and **must be screened at position level
  before any return is read.**
* **X46** — no unconditional convexity; crisis gains are short-side. *Consequence:* MMV
  may not be called a diversifier, and F5's own field 11 predicts it would have been long
  risk into 2020-03.

X45 is why F5's cheap gate is a position-level screen and not a return test, and it is
why this lineage can be killed before any P&L exists.

## A.4 Sample reuse and trial overlap — mechanically verified

```
PRICE_SAMPLE_REUSE   = ETF panel `dataset.yfinance.multi-asset-etf-panel`,
                       BURNED / CONTEXT T0.
                       SAMPLE_REUSE.md KB-1: "Burned by 6 of 6 registered research
                       paths"; "This program's reuse = 7th and subsequent";
                       relationship type `must_not_be_retested_on_same_sample`;
                       "Frozen trial-count convention = NONE EXISTS", D-ETF-COUNT open.
MACRO_DATA_REUSE     = ALFRED vintages: NEW. No prior programme exposure, no vintage
                       data has ever been fetched here. The REVISED counterparts of
                       some series (CPIAUCSL, foreign CPI) were used by the closed
                       Value lineage — a different object from their vintages, and the
                       adjacency is declared rather than ignored.
TRIAL_FAMILY_OVERLAP = LOW. No macro-CHANGE signal has ever been built in this
                       programme. TRIAL_LEDGER §6.2 holds three declared families
                       (F-VRP, F-TA, F-BENB); none covers macro momentum. No family is
                       declared here — a family is declared in a preregistration
                       before its first member runs, which is S1's job, not S0's.
EVIDENCE_CEILING     = supported.
                       NEVER confirmed, NEVER independently confirmed. A new ALFRED
                       vintage leg does NOT launder a reused price sample — the reading
                       sealed at CTA-EDGE-02-BENB and inherited here.
```

---

# B. VERIFIED EXTERNAL FACTS

## B.1 ALFRED — and the fact that it settles feasibility but not the science

Verified from the official FRED API documentation
(`fred.stlouisfed.org/docs/api/fred/series_observations.html`):

```
realtime_start / realtime_end   "The start / end of the real-time period" — retrieve
                                data as it was known during a specified timeframe.
vintage_dates                   "A comma separated string of YYYY-MM-DD formatted dates
                                in history … used to download data as it existed on
                                these specified dates in history."
output_type = 1                 Observations by Real-Time Period  (default)
output_type = 2                 Observations by Vintage Date, All Observations
output_type = 3                 Observations by Vintage Date, New and Revised Only
output_type = 4                 "Observations, Initial Release Only"
```

**This is the decisive feasibility finding, and it cuts both ways.**

```
CURRENT_REVISED_SERIES_AVAILABLE = YES   (ordinary FRED; already partly on disk)
VINTAGE_SERIES_AVAILABLE         = YES   (ALFRED vintage_dates / realtime_*)
FIRST_RELEASE_RECONSTRUCTIBLE    = YES   (output_type = 4, a single documented parameter)
LATEST_KNOWN_ASOF_RECONSTRUCTIBLE = YES  (vintage_dates, or realtime_start = realtime_end)
```

Both competing information concepts are **equally and trivially obtainable**. The choice
between them is therefore **purely scientific** — it cannot be settled by asking which is
feasible, which is exactly why it is MMV-OD-1 and not a data task.

### Vintage coverage per series — verified on ALFRED

| series | meaning | freq | units | earliest vintage | ~vintages | note |
|---|---|---|---|---|---|---|
| `PAYEMS` | All employees, total nonfarm | monthly | thousands of persons, SA | **1955-05-06** | ~850+ | annual **benchmark revisions**; title changed 2019-09-06 |
| `CPIAUCSL` | CPI all items | monthly | index, SA | **1972-07-21** | ~650+ | **rebased 1988-02-26** from 1967=100 to 1982-84=100 |
| `PCEPILFE` | PCE excl. food and energy (core) | monthly | index 2017=100, SA | **2000-08-01** | ~314 | BEA *"revises previously published PCE data to reflect updated information or new methodology"* |

Every one of these begins **decades before** the 2008-05 evaluation window. Vintage
coverage is not a constraint on this lineage.

Two mechanical notes recorded now so they cannot surprise S1:

* **Rebasing is harmless to the transform.** A rebase multiplies the whole index by a
  constant, so a 12-month *ratio* change computed **within one vintage** is invariant to
  it. A 12-month change computed **across** vintages that straddle a rebase is **not**.
  That is a concrete way in which concepts A and B differ mechanically, not just
  philosophically.
* **PCEPILFE's 2000 vintage start** is the shortest of the three and still comfortably
  precedes the window; `INDPRO` and `UNRATE` were not separately verified because no F5
  feature depends on `UNRATE` and `INDPRO` is a declared third-leg input.

### Access

```
NEW_PAID_ENTITLEMENT_REQUIRED = NO
```

The FRED API terms of use state *"In order to use the FRED® API, you must have register
for an API Key"* and require the attribution notice *"This product uses the FRED® API but
is not endorsed or certified by the Federal Reserve Bank of St. Louis."* The terms page
checked does **not** state a fee; a self-service registration key is **not** an
institutional entitlement, and this is categorically different from the LSEG / ICE
entitlement that closed PINS. Recorded honestly: *confirming the key is free and
obtaining one is a trivial mechanical step that has not yet been performed.*

The terms also warn that *"Data series available through the FRED® API may be owned by
third parties and subject to copyright restrictions."* The series named here are US
federal statistical products (BLS, BEA, Federal Reserve), but the caveat is recorded
rather than waved away.

## B.2 Literature — used to fix definitions, never to import profitability

```
NO REPORTED PROFITABILITY FROM ANY PAPER IS IMPORTED AS PROGRAMME EVIDENCE.
```

| source | claim | sample | macro-data treatment | universe | horizon | predictive or causal |
|---|---|---|---|---|---|---|
| **Brooks (2017)**, *A Half Century of Macro Momentum*, AQR white paper | long assets whose fundamental macro trends are improving, short those deteriorating; themes include business cycle (**changes in real GDP growth forecasts**), monetary policy (**the front end of the yield curve**) and risk sentiment (**equity excess returns**) | 1970–2016 | **forecast-based and market-based inputs, not ALFRED first releases** | global equities, currencies, government bonds, interest rates | monthly-ish | predictive, not causal |
| **Dahlquist & Hasseltoft (2020)**, *Economic momentum and currency returns*, JFE **136**(1), 152–167 | past trends in fundamentals linked to economic activity and inflation predict currency returns; economic momentum **subsumes the alpha of carry** | 1976-01 → 2017-03 | five fundamentals: industrial production, retail sales, unemployment, consumer prices, producer prices | 21 developed + some emerging currencies | monthly | predictive |
| **Croushore & Stark (2001)**, *A Real-Time Data Set for Macroeconomists*, J. Econometrics **105**, 111–130 | the canonical real-time data infrastructure: *"vintages, or snapshots, of time series … data as they existed in the middle of each quarter … identical to those one would have seen in published sources at that time"* | 1965-11 → | **vintage snapshots** | n/a (macro forecasting) | n/a | methodological |

**What the literature does and does not settle for this lineage:**

* It supports the **mechanism** (fundamental trends predict asset returns across classes)
  independently in currencies (Dahlquist & Hasseltoft) and in a broad macro book (Brooks).
* It does **not** ratify F5's exact construction. Brooks uses **GDP growth forecasts** and
  the **front end of the yield curve** — a forecast and a market price — where F5 proposes
  realised vintage statistics and an administered rate. F5 is *inspired by* this
  literature, not a replication of it, and S1 must not describe it as one.
* On **A versus B**: the canonical real-time infrastructure (Croushore & Stark, and the
  Philadelphia Fed RTDSM it describes) is built from **vintage snapshots**, which is
  concept B. That is evidence about what the macro-forecasting literature standardised on;
  it is **not** a ruling about what a trading signal should use, because the RTDSM exists
  to reproduce *forecasts*, not to represent *news*. The literature therefore **informs**
  MMV-OD-1 and does not decide it.

---

# C. PROPOSED STUDY

*A proposal for S1 to accept, amend or reject. Nothing here is sealed.*

## C.1 The question

> **Does the direction of change in a small, predeclared set of macroeconomic series —
> measured only from information that was actually published by the decision date —
> predict the direction of subsequent asset-class returns, separably from the asset-return
> trend the canonical book already trades?**

```
PRIMARY_MECHANISM = Underreaction to slow-moving fundamental change. Releases are noisy,
                    lagged and revised; consensus and institutional allocation update
                    over quarters. The premium is for acting on slow public information
                    before consensus catches up. It persists because release lags and
                    revisions are permanent.
PRIMARY_CLAIM_TYPE = REDUCED-FORM PREDICTIVE. Not causal. Not a macro nowcast. Not a
                    regime classifier.
```

**What this lineage is explicitly NOT:**

```
NOT price momentum                the signal uses no asset price (§C.6)
NOT trend following               the input is published statistics, not returns
NOT macro regime labelling        it is a DIRECTIONAL signal, never a gate on the core.
                                  The programme's ban on macro-regime classifiers as
                                  gates (the yield-curve single-episode wall) is
                                  respected, as F5 field 12 already states.
NOT revised-history prediction    using today's revised values to represent what was
                                  known then is the defect this lineage exists to avoid
```

## C.2 Macro-momentum definition — FIXED BY F5, preserved

The brief's §5 says to preserve the definition if the authority already fixes it. **It
does**, in field 1:

```
MACRO_MOMENTUM_DEFINITION = the 12-MONTH CHANGE in the series, SIGN-ONLY,
                            mapped to asset-class direction by a table fixed from
                            theory before any data.

NO transform family.   NO lookback search.   NO magnitude scaling at S0.
NO acceleration, no surprise-vs-forecast, no z-scoring, no smoothing variants.
```

Those alternatives are listed in the brief's §5 as *conceptual families that may exist*;
F5 chose one and this frame does not reopen it. The only definitional question F5 left
open is **which values enter the 12-month change** — MMV-OD-1.

## C.3 Macro-series family — the smallest set F5 requires

F5's own ranking is *"Most defensible: F5.b and F5.c"*. This frame proposes exactly that,
with growth as F5's declared third leg and nothing else.

| leg | category | why it is REQUIRED | proposed ALFRED series |
|---|---|---|---|
| **F5.b** inflation | inflation | F5's joint-most-defensible leg; *"the least theory-ambiguous"* asset mapping | **core**, per field 3: `PCEPILFE` and/or `CPILFESL` — **see the field-3 vs field-5 discrepancy in §A.1** |
| **F5.c** policy | monetary / liquidity | F5's other most-defensible leg | the **administered policy rate** — **not** the 2-year yield, see §C.6 |
| **F5.a** growth | growth / activity + labour | F5's declared third leg; explicitly weaker (*"growth-to-bond mapping flips sign in disinflationary booms"*) | `INDPRO`, `PAYEMS` |

```
EXCLUDED, and why:
  UNRATE   appears in F5's data list with NO feature attached to it. Not included.
           Adding it because ALFRED has it is precisely the feature zoo §6 forbids.
  F5.d     cross-country differentials — PARKED for S1, not deleted. It is F5's only
           out-of-sample replication, but the foreign legs on disk are NON-VINTAGE
           (VALUE_DATA_INVENTORY), so it cannot be point-in-time today.
  anything else in ALFRED                 not required by the authority.
```

## C.4 The real-time information concept — **UNRESOLVED, see MMV-OD-1**

```
A. FIRST-RELEASE SIGNAL          what the investor initially LEARNED. Chain the
                                 first print of each month. ALFRED output_type = 4.
B. LATEST-KNOWN-AS-OF-t SIGNAL   what everything published by t implied. One vintage
                                 snapshot per decision date. ALFRED vintage_dates.
C. FINAL-REVISED HISTORY         what we know today.
                                 FORBIDDEN as a substitute for A or B, in any cell,
                                 at any stage, for any reason.
```

```
PRIMARY_INFORMATION_CONCEPT = UNRESOLVED -> MMV-OD-1
REVISION_HANDLING           = follows from MMV-OD-1 and is not separable from it
```

C is not a candidate. It is named only so that a later document cannot quietly slide into
it, which is the exact defect the closed Value lineage recorded against its own Shiller
input.

## C.5 Publication lag and the as-of rule

```
SIGNAL_FREQUENCY    = MONTHLY (the release frequency of every proposed series)
REBALANCE_FREQUENCY = MONTHLY, at the canonical month-end decision point
                      No holding-period family. No rebalance-frequency search.
                      Daily trading is NOT forced onto monthly information.

INFORMATION_CUTOFF  = the canonical month-end decision timestamp: the last exchange
                      session of month m, at the close. This aligns MMV with the frozen
                      book's own decision point, which is what makes the position-level
                      screen in §C.7 a like-for-like comparison.

MACRO_VALUE_AS_OF   = only values with an ALFRED real-time availability date STRICTLY
                      ON OR BEFORE the information cutoff may enter the decision for
                      month m. The eligible vintage is the latest whose vintage date
                      <= the cutoff.

RELEASE_LAG_HANDLING = NOT a fixed assumed lag. ALFRED's vintage dates ARE the release
                      dates, so the rule is a date comparison against published
                      metadata rather than an assumption about how late BLS or BEA
                      usually are. Holiday and irregular-release timing is therefore
                      handled automatically — which is the opposite of the trap the TA
                      lineage hit with a hard-coded calendar.

NO SAME-PERIOD LOOKAHEAD. The reference month of an observation is irrelevant; only its
publication date governs eligibility. A January CPI reading published in February is
eligible for a February decision and NOT for a January one.
```

This rule is **mechanically provable after the fact** — a synthetic or metadata check can
assert, for every decision month, that no value carrying a vintage date after the cutoff
entered the signal. S1 should require that proof, not a comment claiming it.

## C.6 Distinctness from price — mandatory, and one constraint it forces

```
MACRO_SIGNAL_CONSTRUCTIBLE_WITHOUT_PRICE = YES,
  CONDITIONAL on F5.c resolving to the ADMINISTERED POLICY RATE rather than the
  2-year Treasury yield.
```

F5.c offers *"the policy rate **or** the 2-year yield (unrevised)"*. These are not
interchangeable for this lineage:

* The **2-year Treasury yield** is a traded market price, mechanically tied to the returns
  of `SHY`, `IEF` and `TLT` — three instruments inside the panel this signal would trade.
  Building the macro signal from it would make the "macro" leg partly a transform of the
  price of an asset in the book, which is the failure mode this lineage exists to avoid
  and which the brief's §9 forbids outright.
* The **administered policy rate** is a policy instrument, not a panel asset return.

This frame therefore proposes the policy rate and records the 2-year yield as
**excluded by rule, with the reason**, so the exclusion is auditable and the controller
can overrule it deliberately rather than by omission. Which policy-rate series (effective
fed funds, continuous since 1954 and unrevised, versus the target range with its
documented December-2008 single-target-to-range break) is a mechanical S1 detail, not an
S0 blocker.

Price is used **only** for: mapping to assets, diagnostics, and returns. No price
variable enters the construction of any macro leg.

## C.7 The cheap PnL-free falsification — recovered from F5, not improvised

```
CHEAP_PNL_FREE_FALSIFICATION = monthly SIGN AGREEMENT between the MACRO COMPOSITE and
                               the CANONICAL COMPOSITE, per instrument and pooled, over
                               months <= 2026-06-12. If agreement exceeds a declared
                               bound (F5 says about 80 %), stop: `not_promoted`, reason
                               `not_separable_at_position_level`.
```

**The two sign objects compared:**

| object | what it is | where it comes from |
|---|---|---|
| canonical composite sign | `sign(mean of the 1/3/6/12-month return signs)` per instrument per month-end | **already on disk**: `output/monthly_signal_panel.csv`, 17 × 402, nothing to compute |
| macro composite sign | the predeclared mapping table applied to the 12-month change of each macro leg, aggregated to a per-instrument direction | not yet built; blocked on MMV-OD-1 |

**Why agreement or disagreement is scientifically informative.** X45 established that the
core's *static* average position — long bonds, credit and equity — already reproduces
almost all of its Sharpe, and that any same-stream conditioner is capped near 0.15 Sharpe.
A macro sleeve that takes the same side as the canonical book in most months is therefore
not a second return source; it is the same static bet expressed in macro vocabulary, and
any subsequent positive return result would be a re-measurement of X45 rather than new
evidence. The screen detects that **before any P&L exists**, which is why it is cheap.

**What it can kill:** high agreement kills the *separability* claim, and F5's field 15
makes that fatal — *"the position-level screen fails … which makes the rest of the study a
confirmation of X45 rather than a new source."*

**What it cannot do, stated because the brief's §11 requires it:**

```
HIGH agreement does NOT prove the macro mechanism is absent. It proves this
  IMPLEMENTATION of it is not separable from the book we already own.
LOW agreement does NOT prove diversification, does NOT prove predictive power, and
  does NOT prove crisis protection. It only clears the way for Gate 1.
```

Both readings must be written into the sealed contract **before** the screen runs, or the
result becomes unfalsifiable in the way F5's field 13 warns about.

**This screen was NOT run during S0.** It is designed here and runs only after
preregistration, per the brief's §10. Its benchmark input was confirmed to exist by
reading a header and a row count — no signal, position or statistic was computed.

## C.8 Asset mapping

F5 binds the direction of every theme for every class, and this frame does not enlarge it:

```
F5.a growth     ->  long equity / credit, short duration
F5.b inflation  ->  short duration, long commodities, long dollar
F5.c policy     ->  short duration, long dollar, short equity

PRIMARY_ASSET_MAPPING = CROSS-ASSET DIRECTIONAL, pooled across the four mapped classes
                        (equity, duration/credit, commodities, dollar), inside the
                        canonical 17-ETF universe. Not one asset, not one sleeve.
                        F5 §4: "pooled across the four mapped classes, one family of five".
```

```
UNIVERSE IS NOT ENLARGED AT S0.  No asset is selected on realised performance.
The table is FIXED FROM THEORY BEFORE ANY DATA. F5 field 13 is explicit that revising
any cell after a disappointing result makes the study unfalsifiable — so the mapping
must be frozen in the S1 seal and is never repairable afterwards.
```

The one genuine under-specification F5 leaves is **how the three theme signs aggregate
into one per-instrument direction** when they disagree (inflation says short duration,
growth says short duration, policy says short equity while growth says long equity). That
is an S1 design task with a small, declarable option set — it does not change the
estimand and is not escalated here.

## C.9 Gate sequence

```
GATE 0    PIT / VINTAGE FEASIBILITY
          Can the required macro information be reconstructed as ACTUALLY KNOWN, under
          the chosen information concept, with a date-comparison rule that a later
          check can prove? Largely answered YES by §B.1 — but not fully, because the
          concept itself is unresolved.

GATE 0.5  PNL-FREE MECHANISM PREMISE  (§C.7)
          The sign-agreement screen. Runs only after preregistration. Kills the lineage
          at `not_separable_at_position_level` without any P&L existing.

GATE 1    PREDICTIVE RESPONSE
          Only if the premise survives. F5: "forward sign-aligned return per unit risk
          of the macro composite pooled across the four mapped classes, one family of
          five, BH-FDR, with a leave-one-macro-episode-out jackknife DEFINED FROM THE
          VINTAGE SERIES BEFORE ANY RETURN IS SEEN."

GATE 2    ECONOMIC USEFULNESS
          Only if predictive evidence survives.

No jump to portfolio Sharpe. No portfolio test exists in this frame and none is
authorised by it.
```

## C.10 Materiality and costs — both deliberately unset

```
MATERIALITY_STATUS = NOT SET, and NOT INHERITED.
  BENB's +0.30 and TA's +0.30 are NOT portable — Aaron's BENB-OD-1 established that a
  materiality bar is lineage-specific. C-A thresholds are likewise not inherited.
  F5 fixes no numeric threshold, so none is proposed.
  The appropriate ECONOMIC OBJECT, from F5's own Gate-1 wording, is
  FORWARD SIGN-ALIGNED RETURN PER UNIT RISK of the macro composite, pooled across the
  four mapped classes — a monthly, sign-only, cross-asset object. Whether the bar is set
  at S1 or left to S4 is an Owner choice not asked here.

COST_STATUS = NOT SET, and no cost is invented.
  Turnover mechanism: sign changes in a 12-month macro change, which is SLOW — a
  12-month difference flips rarely, so turnover should be materially LOWER than the
  canonical book's 81 % signal-driven turnover.
  Instrument type: the same liquid ETFs the frozen book trades.
  Rebalance frequency: monthly.
  Existing programme cost authority: the canonical book's 2 bps one-way convention is
  the natural candidate BECAUSE the instruments and the decision point are identical —
  but it is named as a candidate, not adopted, and no return was inspected to choose it.
```

## C.11 Negative outcome taxonomy — defined before outcomes

```
A  VINTAGE / PIT FAILURE          the required information cannot be reconstructed as
                                  actually known, or the as-of rule cannot be proved
B  MECHANISM PREMISE FAILURE      the macro composite carries no directional content
                                  of the predeclared sign
C  NOT DISTINCT                   the macro composite agrees with the canonical
                                  composite above the declared bound
                                  -> `not_separable_at_position_level`
D  PREDICTIVE RESPONSE NOT SUPPORTED
E  RESPONSE PRESENT BUT UNECONOMIC
F  LOW POWER / UNRESOLVED         F5's own honest expectation: 10-15 US macro turns,
                                  "the honest terminal state may be `unresolved`"
G  SUPPORTED
```

**Only B is anything close to "the mechanism is not there."** A and C are statements about
*this construction* and *this book*; E and F are statements about power and economics.
A later document describing any of A, C, D, E or F as "falsified" is in breach of this
frame.

---

# D. NOT-YET-TESTED CLAIMS

1. That markets underreact to slow-moving macro change in the way F5 describes.
2. That a 12-month change, sign-only, is the right encoding of that underreaction.
3. That the macro composite is separable from the canonical composite at position level.
4. That the predeclared mapping table has the right signs.
5. That 10–15 effective macro turns give enough power for anything but `unresolved`.
6. That first-release and latest-known-as-of-t signals differ *materially* in practice —
   asserted here on the mechanics of benchmark and seasonal-factor revisions, **not
   measured**.
7. That the FRED API key is free (terms page does not state a fee).
8. That `INDPRO` and `UNRATE` vintage coverage matches the three series verified.

```
No macro feature was computed. No composite was built. No position was formed.
No return was accessed. No regression, Sharpe, hit rate or conditional return exists.
No famous macro episode was inspected against candidate returns.
```

---

# E. PARKED QUESTIONS

1. **F5.d cross-country replication** — F5's only out-of-sample leg, parked because the
   foreign CPI series on disk are **non-vintage** (`VALUE_DATA_INVENTORY`). Reviving it
   needs foreign vintage sources, which ALFRED does not generally carry.
2. **`UNRATE`** — in F5's data list with no feature attached. Not included; not deleted.
3. **Core CPI series identity** — `CPILFESL` versus `PCEPILFE`, and the field-3 vs
   field-5 headline/core discrepancy (§A.1). Proposed resolution: follow field 3 (core).
   Needs controller confirmation, but does not change the estimand.
4. **Theme aggregation rule** when the three legs disagree (§C.8).
5. **Which policy-rate series** — effective fed funds (continuous, unrevised) versus the
   target range with its December-2008 structural break (§C.6).
6. **Whether an MMV coefficient joins an existing trial family or declares a new one** —
   an S1 question with real consequences, unaffected by S0.
7. **The 2008-05 window start.** The canonical book is evaluated from 2008-05, but ALFRED
   vintages reach back decades. Whether MMV inherits the book's window or uses a longer
   macro history is an S1 choice with power implications, and it must be made before any
   return is seen.

---

# F. FORBIDDEN INTERPRETATIONS

*Binding on every later document and seat in this lineage.*

```
THIS IS NOT A CRISIS DIVERSIFIER and must never be described as one.
```

F5's own field 11 predicts the opposite: *"in 2020-03 every growth-momentum reading was
still positive when prices crashed, so the sleeve would have been long risk into the crash
and would have co-lost with the core's static long component."* Any tail claim must be
reported on **declared windows** and never asserted from an unconditional correlation —
the VRP lesson, recorded here before any result exists.

A **supported** result would NOT establish:

* that macro data *cause* asset returns — the design is reduced-form;
* that the canonical book should be gated, de-grossed or overlaid by a macro state;
* that macro momentum works in other universes, horizons or instruments;
* that the published macro statistics are *accurate* — the study uses what was
  **published**, which is the investor's information set, not the truth;
* any improvement to canonical TSMOM, which remains a **frozen research benchmark** and
  is not modified by this lineage in any way.

A **negative** result would NOT establish:

* that macroeconomic information is irrelevant to asset prices;
* that the Brooks or Dahlquist–Hasseltoft findings are wrong — neither uses this
  construction, this universe or this sample;
* that a different information concept, series family, mapping or horizon would also fail.

```
EVIDENCE_CEILING = supported.  NEVER confirmed. NEVER independently confirmed.
The ETF price leg is reused / burned context (KB-1). A new ALFRED vintage leg does not
launder a reused price sample.
```

---

# G. DESIGN EXPOSURE

```
FABLE_DESIGN_EXPOSED = YES
ASTRA_DESIGN_EXPOSED = NO
```

**Claude Fable 5.1 is a `material_design_contributor`**: it originated F5 — the candidate,
the 12-month sign-only transform, the series family, the mapping table, the position-level
screen and the stated failure modes. It is **barred from blind certification** of this
design, this implementation or any result under it. If it later supplies Owner advice on
MMV-OD-1, adopting that advice does not restore independence: it remains design-exposed
and cannot become a blind certifier.

**GPT-6 Astra is recorded as NOT exposed to this lineage**, with a limitation stated
rather than papered over:

```
ASTRA_PROVENANCE_LIMITATION
  Astra's Round-1 CTA discovery output is NOT PERSISTED anywhere in this workspace.
  A disk-wide search at the CTA-EDGE-04 candidate audit found no Astra artifact; its
  contributions reached the earlier S0 sessions only through the controller's task
  brief. The `ASTRA_DESIGN_EXPOSED = NO` status for MMV is therefore an inference from
  the ABSENCE of any recorded Astra contribution to F5, not a positive attestation from
  Astra bytes. Recorded per REVIEWER_EXPOSURE_LOG S32/S38, which carry the same gap.
  Do not represent Astra's provenance as stronger than this.
```

Seat rows are written to `ops/REVIEWER_EXPOSURE_LOG.md` **at seal**, per the convention
the TA and BENB lineages followed. None is written at S0.

---

# H. MMV-OD-1 — THE OWNER DECISION

```
HIGH_DIFFICULTY_OWNER_DECISION_REQUIRED = YES
FABLE_OWNER_ADVICE_RECOMMENDED          = YES, marked DESIGN-EXPOSED / NOT INDEPENDENT
INDEPENDENT_ADJUDICATOR_RECOMMENDED     = NO
```

**OWNER_DECISION_QUESTION**

> Which real-time information concept is the primary hypothesis built on: the chain of
> **FIRST RELEASES** (what the investor *learned* each month), or the **SINGLE VINTAGE
> SNAPSHOT as-of the decision date** (what everything published by then implied)?

**ALTERNATIVES**

```
(A) FIRST-RELEASE CHAIN            ALFRED output_type = 4.
    The 12-month change is built from the value each month was FIRST published at.
    The signal moves only when NEW information arrives.

(B) VINTAGE SNAPSHOT AS-OF t       ALFRED vintage_dates.
    The 12-month change is computed inside the single vintage available at the
    decision date. The signal also moves when a REVISION rewrites the past.

(C) DECLARE ONE PRIMARY AND THE OTHER A PREREGISTERED ROBUSTNESS CELL with no
    promotion power — one estimand, one declared sensitivity.

(D) HOLD the lineage until the concept can be settled from external authority.
```

**WHY_IT_MATTERS**

* **It selects the estimand, not the implementation.** A and B encode different theories
  of what the investor responds to. Under B, an annual payroll **benchmark revision** or a
  February **seasonal-factor revision** changes today's 12-month change *without any new
  information about the current month* — a real change in what the investor believes, but
  not "the direction of change in fundamentals" in the sense F5's mechanism describes.
  Under A the signal moves only on new prints, which is closer to *news* but further from
  *what the investor currently believes*.
* **The affected series are exactly the load-bearing ones.** Payrolls carry annual
  benchmark revisions; seasonally adjusted CPI is revised for the prior five years each
  February; core PCE carries annual and comprehensive BEA revisions. This is not a corner
  case in the two legs F5 called *most defensible*.
* **It is not a feasibility question.** §B.1 verified both are obtainable with one
  documented API parameter. Nothing about cost, access or entitlement discriminates them,
  so the choice is purely scientific and cannot be deferred to a data task.
* **It cannot be deferred past S1.** F5's field 13 warns that revising any cell after a
  disappointing result makes the study unfalsifiable. Choosing the information concept
  after seeing a result would be the largest possible instance of that.
* **The literature informs but does not decide.** The real-time macro infrastructure
  standardised on vintage snapshots (Croushore & Stark) — but it did so to reproduce
  *forecasts*, not to represent *news*, so it is evidence rather than a ruling.

**Why Fable, and why not an independent adjudicator.** This is a **constructive design**
question — *what should the information concept be?* — which is Fable's designated role,
and it is not a request to certify or adjudicate Fable's own claim. An independent
adjudicator is the right seat when the question is *"does this argument clear a bar?"*;
here the question is *"what is the right object?"*. Fable must nonetheless be marked
**DESIGN-EXPOSED / NOT INDEPENDENT** in any record of the advice, and adopting it will not
change that status.

---

## I. What would change the status

```
S0 = PASS   once MMV-OD-1 is resolved to (A), (B) or (C), the §A.1 core-CPI discrepancy
            is confirmed, and the §C.6 policy-rate exclusion is confirmed or overruled.
            Nothing else is blocking: the data is free, the vintages reach back decades,
            the benchmark panel is on disk, and the cheap gate is designed.

S0 = HOLD   current state, on MMV-OD-1 alone.

S0 = FAIL   only if the Owner rules that a point-in-time macro-change signal is not a
            research slot in this cycle. No data or feasibility path to FAIL exists.
```

**Nothing in this frame authorises S1, a seal, a build, a data fetch, an API key
registration, or any computation on any candidate outcome.**

---

*CTA-EDGE-04-MMV S0: the transform, the series family, the mapping and the cheap gate all
come from the authority unchanged. The one thing the authority never confronted is which
version of the past the investor is assumed to have been looking at, and that is the
question going back.*
