# CTA-EDGE-03-PINS — S0 FRAME

**PHYSICAL INVENTORY NEWS × SCARCITY**

```
LINEAGE (provisional)      = CTA-EDGE-03-PINS
WORKING NAME               = PHYSICAL_INVENTORY_NEWS_X_SCARCITY
STAGE                      = S0 FRAME  (research-question definition only)
DATE                       = 2026-09-16
BRANCH                     = cta-edge/physical-inventory-news-s0
PARENT COMMIT              = 13adfdac2a2f78f4a6f3d0f05c95ecb77db80888  (BENB closeout)

S0_FRAME_STATUS            = HOLD
HOLD_REASON                = PINS-OD-1, a load-bearing Owner decision on the
                             EXPECTATION SOURCE. It is not a data-plumbing problem and
                             it is not mine to take: the three live options are three
                             different hypotheses.

HISTORICAL_SURPRISE_COMPUTED = NO    SCARCITY_FEATURE_COMPUTED = NO
INTERACTION_COMPUTED         = NO    RETURN_OUTCOME_ACCESSED   = NO
REGRESSION_RUN               = NO    BACKTEST_RUN              = NO
S1_SEAL_CREATED              = NO    BUILD_STARTED             = NO
RUN_AUTHORIZATION_CREATED    = NO
```

This document defines a research question. It is not a design, not a contract, not an
implementation and not a result. Nothing in it has been tested. Every external claim is
labelled with what was actually verified and how.

---

# A. PROGRAMME / REPOSITORY FACTS

*Verified from bytes in this repository and on this machine.*

## A.1 Identifier and branch — collision-checked

```
git ls-files | grep -i "pins|cta-edge-03"        -> no match
grep -r "CTA-EDGE-03|PINS_|CTA_EDGE_03" repo      -> no match outside .venv
research/extensions/pins/                         -> did not exist
branch cta-edge/physical-inventory-news-s0        -> did not exist
```

`CTA-EDGE-03-PINS` is free and follows the established `CTA-EDGE-NN-XXXX` convention
(`CTA-EDGE-01-TA`, `CTA-EDGE-02-BENB`). The directory convention
`research/extensions/<short>/` and the artifact convention `<SHORT>_S0_FRAME.md` both
match the two prior lineages. The branch was created from the BENB closeout commit, not
from `main`, so the governance ledgers (`TRIAL_LEDGER`, `SAMPLE_REUSE`,
`EXPOSURE_LEDGER`) carry forward intact. **Nothing was merged or rebased.**

## A.2 What price data actually exists

| holding | detail | verified from |
|---|---|---|
| **CL daily bars** | Databento `GLBX.MDP3`, schema `ohlcv-1d`, `stype_in=parent`, 18 CME roots **including `CL.FUT`**, 2010-06-06 → 2026-07-01 (through 2026-06-30). `ohlcv-1d.dbn.zst` 107,229,003 bytes, sha256 `333095164e55c73a…c59539` | `research/extensions/wave1/databento_probe.json`; `SAMPLE_REUSE.md` KB-2 |
| **Contract identity** | Actual per-contract identity IS available: the Wave-1 repair established that the panel must be keyed on `instrument_id + expiration`, never on raw CME symbol (a one-digit year repeats every 10 years and silently merged `CLZ5` 2015 with `CLZ5` 2025 **with no gap**) | `research/extensions/wave1/FUTURES_INFRA_TRUTH.md` §1 |
| **CL intraday** | **NONE HELD.** The only intraday holdings are `NQ.v.0` `ohlcv-1m` (2010-06-06→2022-01-01) and `MNQ.v.0` `bbo-1s` (2025-01-01→2025-04-01), both for the separate *intraday-trend* project | `databento-archive/intraday-trend/*/_local_manifest.json` |
| **Acquisition capability** | Proven. Databento GLBX.MDP3 entitlement is live and has been billed. Observed quotes: `ohlcv-1m` one CME root ≈ **$14–19** for 12–15 years; `bbo-1s` one symbol ≈ **$6.5 per quarter** | `databento-archive/quote_matrix_v2.json`, `_local_manifest.json` |
| **EIA / inventory data** | **NONE.** No EIA series, no WPSR file, no inventory data of any kind exists in this repository or in `C:\Users\Aaron\quant-data`. | directory inventory |
| **Consensus / survey data** | **NONE.** No Reuters, Bloomberg, Platts or API survey data exists anywhere on this machine. | directory inventory |

**The operative fact:** CL intraday data is **not held but is cheaply and lawfully
obtainable** under an entitlement Aaron already pays for. That removes the usual
"intraday is impossible" objection — and it means the binding constraint lies elsewhere.

## A.3 Sample-reuse status — inherited, not invented

```
PRICE_SAMPLE_REUSE_STATUS     = REUSED / BURNED CONTEXT
PHYSICAL_DATA_REUSE_STATUS    = NEW  (no prior programme exposure)
CONSENSUS_DATA_REUSE_STATUS   = NEW  (no prior programme exposure), and UNOBTAINED
EVIDENCE_CEILING              = supported
```

`CL` is one of the 18 roots in **KB-2** `dataset.databento.commodity-futures-curves`,
which is **burned by** `strat.commodity-carry.xs-ts-carry-premium` with
**`N_trials = 14, frozen`** (verified from `commodity-carry-research` preregistration §10
and `src/config.py:66`).

A 1-minute CL panel would be a **different footing of the same economic history**, not a
new sample — exactly the reading the BENB lineage sealed for raw-versus-adjusted ETF
prices. A new physical (EIA) leg does **not** launder a reused price leg. Combined
provenance is therefore **DEPENDENT / MIXED** and the evidence ceiling is **`supported`**,
never `confirmed`, whatever the eventual result.

**No trial count is invented here.** KB-2's `N_trials = 14` belongs to the commodity-carry
counting convention (one trial per distinct constructed strategy-return series); whether a
PINS event-study coefficient is a member of that count is an **open question for S1**, not
something S0 decides.

## A.4 Two programme lessons this lineage inherits

1. **From CTA-EDGE-01-TA (closed pre-outcome):** *do not use coarse data for a
   timing-sensitive mechanism.* TA died because a daily ETF design could not separate a
   mid-month auction window from the macro calendar. §B.5 below is the direct
   application of that lesson, and it is why this frame does not offer a daily fallback.
2. **From CTA-EDGE-02-BENB (closed, Class A-M):** *the decomposition that separates the
   unreachable part of a move from the reachable part must be in the sealed contract.*
   BENB produced an interpretable negative — "the discount closes, but before a lawful
   entry" — only because that split was preregistered. PINS has the identical shape:
   a scheduled release, a fast response, and an entry that cannot be simultaneous with
   publication. §C.6 carries the split forward.

---

# B. VERIFIED EXTERNAL LITERATURE / MARKET MECHANICS

*Each entry records what was verified and from where. Where a primary source was
paywalled, that is stated rather than papered over. **No reported profitability from any
paper is imported as programme evidence** — the literature is used only to fix
definitions, timing, sign and the scarcity concept.*

## B.1 The EIA release — verified from EIA

| field | value | source |
|---|---|---|
| Report | Weekly Petroleum Status Report (WPSR), DOE/EIA-0208 | eia.gov |
| Standard release | **Wednesday, 10:30 a.m. Eastern** — `wpsrsummary.pdf`, `overview.pdf`, and **Tables 1–14 in CSV and XLS**. All *other* PDF and HTML files follow at **1:00 p.m. Eastern** | [eia.gov schedule](https://www.eia.gov/petroleum/supply/weekly/schedule.php) |
| Holiday rule | *"For some weeks that include holidays, releases are delayed by one day."* Verified 2025–2026 exceptions: New Year, MLK, Presidents' Day, Memorial Day, Labor Day, Columbus Day, Veterans Day → **Thursday, 11:00 a.m. or 12:00 p.m. ET**; Christmas 2025 → **Monday 29 Dec, 5:00 p.m. ET** | same |
| Headline series | **`WCESTUS1`** — *Weekly U.S. Ending Stocks excluding SPR of Crude Oil*, **thousand barrels** | eia.gov/dnav |
| Scarcity series (official) | **`W_EPC0_VSD_NUS_DAYS`** — *Weekly U.S. Days of Supply of Crude Oil excluding SPR (Number of Days)* | eia.gov/dnav |
| Revisions | The WPSR legend carries **`R = Revised Data`**. Weekly estimates are revised; monthly re-benchmarking against the *Petroleum Supply Monthly* and the STEO production review is documented in Appendix B | eia.gov |

**The holiday rule is not cosmetic.** A design that hard-codes "Wednesday 10:30" will
silently mis-timestamp roughly 7 releases a year, and several of those land at a
*different hour* (12:00 p.m.) with one at 5:00 p.m. on a Monday. The release calendar is
a first-class object, and after the TA lineage this programme knows what an unexamined
calendar costs.

## B.2 First-published reconstructibility — verified by enumeration

```
FIRST_PUBLISHED_EIA_SERIES_RECONSTRUCTIBLE = YES for 2012-01-05 onward
```

The EIA maintains a **per-release archive** at
`https://www.eia.gov/petroleum/supply/weekly/archive/`. Enumerated from the index's own
link structure (metadata only — **no inventory value was read**):

```
765 archived releases      earliest 2012-01-05      latest 2026-09-10
per-year: 2012:52  2013:52  2014:53  2015:52  2016:52  2017:52  2018:52  2019:52
          2020:53  2021:52  2022:51  2023:51  2024:52  2025:53  2026:36 (partial)
```

Each archived release directory offers **15 CSV tables plus 32–40 PDFs** (later years add
`wcrudeoilstorage.xlsx`). The earliest release, 2012-01-05, **already carries all 15
CSVs** — so machine-readable per-vintage data exists across the whole archive, not only
recently.

**This is the strongest data fact in the frame**, and it is exactly the fact the BENB
lineage had to go and find the hard way. A modern API series would have been the revised
series; the archive is the publication vintage.

Two caveats recorded honestly:

* **Pre-2012 is not covered** by this archive. A design wanting 2008 would need a
  different vintage source (e.g. web archives of `ir.eia.gov`), which was **not**
  verified here.
* Whether each archived CSV is byte-for-byte the object published at 10:30 that morning,
  rather than a later re-render, was **deliberately not tested by value comparison** —
  comparing an archived vintage against the current series would touch the physical
  series, and §26 forbids that at S0. It is a **mandatory Level-1 check at S1/S2**, not
  an assumption to carry forward.

## B.3 The expectation — where the literature actually gets it

| paper | what it uses as the expectation |
|---|---|
| **Ye & Karali (2016)**, *The informational content of inventory announcements: intraday evidence from crude oil futures market*, Energy Economics **59**, 349–364 | API surprise measured against **Reuters** analyst expectations; **EIA** surprise measured against **the API report published the day before** |
| **Halova, Kurov & Kucher (2014)**, *Noisy Inventory Announcements and Energy Prices*, Journal of Futures Markets **34**(10), 911–933 | Survey-based surprises, and the paper's entire point is that they are **noisy** |
| **Bu (2014)**, *Effect of inventory announcements on crude oil price volatility*, Energy Economics **46**, 485–494 | An explicit **information-shock** measure rather than the raw inventory change |

**Halova, Kurov & Kucher is the load-bearing methodological finding for this lineage**,
and it is a warning, not an encouragement: *"the bias in OLS estimates of the price impact
of inventory surprises is quite large"*; identification-through-censoring estimates are
**about twice** the OLS estimates for petroleum commodities. Measurement error in the
consensus attenuates the coefficient toward zero. A study that uses a *poor* expectation
proxy will under-estimate the response and can produce a false negative — which is a
specific, named way this lineage could fail for a reason that has nothing to do with the
economics.

**The American Petroleum Institute Weekly Statistical Bulletin**, the natural
"expectation" for EIA under Ye & Karali's construction:

```
released     Tuesday afternoon, approximately 4:30 p.m. ET
             (Wednesday afternoon if Monday is a Federal holiday)
published    since 1929
access       SUBSCRIPTION ONLY, "solely via subscription purchase through our
             authorized redistributors: Refinitiv ... and Intercontinental Exchange (ICE)"
```
Source: [api.org](https://www.api.org/products-and-services/statistics/api-weekly-statistical-bulletin).

## B.4 The price response — what is actually established

| paper | verified finding |
|---|---|
| **Ye & Karali (2016)** | Unexpected inventory changes from **both** API and EIA exert an **immediate inverse impact on returns** and a positive impact on volatility. **EIA shocks are longer and larger in duration and magnitude than API shocks.** Largest impacts when Reuters and API forecasts agree directionally |
| **Bjursell, Gentle & Wang (2015)**, Energy Economics **48**, 336–349, intraday 1990–2008, NYMEX crude/heating oil/natural gas | *"Large jump components are often associated with the EIA's inventory announcement dates."* Intraday volatility **returns to normal faster** after announcements with jumps than after those without |
| **Rousse & Sévi**, *Informed Trading in the WTI Oil Futures Market*, The Energy Journal **40**(2) | **Pre-announcement drift.** Significantly more buyer-initiated orders in the **two hours preceding** the official release, with an average price move of **−0.25 % ahead of the news**. Also *"an asymmetric response of the oil price to the news, and an over-reaction that is partly compensated in the hours following the announcement"* |
| **Wen, Indriawan, Lien & Xu (2023)**, The Energy Journal **44** | On EIA days the **third half-hour** return (the half-hour containing 10:30 ET) significantly and positively predicts the **last half-hour** return; on non-EIA days only the first half-hour predicts. EIA releases *"attract more informed traders"* and the surrounding period is *"associated with a reduction in liquidity"* |
| **Chebbi & Hmedat (2024)**, IJFE **29**(2), 1513–1533, WTI, 2012-03-27 → 2018-10-02 | Inventory surprises **inversely** affect oil prices, **stronger during price-collapse periods**; inventory news is **more relevant than macroeconomic or monetary-policy news** inside announcement windows |
| **Bu (2014)** | Inventory **shocks**, not raw inventory changes, negatively affect returns **on the release day**; the effect **weakens in rapid-growth periods and disappears in steep-fall markets** |

Secondary sources report the release effect is largely complete within roughly **20–25
minutes**. That figure is recorded as **secondary and unverified**: the primary text
(Ye's UGA dissertation) returned HTTP 403 and ScienceDirect/Wiley/SAGE returned 403 to
this session. **A primary-source confirmation of the decay window is a mandatory S1
input**, because the primary response horizon depends on it.

**Three findings that cut against the candidate, recorded up front:**

1. **Pre-announcement drift** (Rousse & Sévi) means part of the "news" is already in the
   price at 10:29:59. Whatever the surprise measures, the *incremental* information at
   10:30 is smaller than the raw surprise implies.
2. **Over-reaction partly compensated in the following hours** (Rousse & Sévi) means the
   sign of a *post-entry* return is not obviously the sign of the surprise. A reversal
   and a continuation both have literature support at different horizons. This is not a
   detail; it determines the sign convention.
3. **Reduced liquidity around the release** (Wen et al.) means §19's warning about
   elevated spread and slippage is a verified market fact, not a hypothesis.

## B.5 Daily versus intraday — the feasibility gate

```
DAILY_DATA_ADEQUATE = NO
INTRADAY_REQUIRED   = YES
```

This is the one design question the evidence settles outright. The mechanism is a jump at
a known second (10:30:00 ET) whose effect is largely spent inside the first half-hour; the
harvestability question is *"is anything left after a realistic entry delay"*. A daily
close-to-close return contains that jump plus six and a half hours of unrelated
information plus an overnight session. It cannot answer the question asked.

The programme has made this mistake once already, and CTA-EDGE-01-TA is the record of
what it cost. **This frame therefore offers no daily fallback.** If intraday data cannot
be obtained, the correct outcome is HOLD or FAIL, not a downgraded question.

## B.6 The instrument — verified CME mechanics

```
PRIMARY_INSTRUMENT       = CME/NYMEX WTI Light Sweet Crude Oil futures, Globex code CL
contract unit            = 1,000 barrels                 quotation: USD per barrel
minimum fluctuation      = $0.01/bbl  =  $10.00 per contract
Globex hours             = Sunday 5:00 p.m. CT -> Friday 4:00 p.m. CT,
                           60-minute halt 4:00-5:00 p.m. CT Mon-Thu
settlement               = PHYSICAL delivery at Cushing, Oklahoma
termination of trading   = third business day prior to the 25th calendar day of the
                           month preceding the delivery month
```

**10:30 a.m. ET = 9:30 a.m. CT falls squarely inside the continuous Globex session**, so
every standard release and every verified holiday-shifted release (11:00 a.m., 12:00 p.m.,
and the 5:00 p.m. ET Monday case) is inside a tradable window. That is a necessary
condition and it is met.

Two contract-identity consequences, both inherited from the Wave-1 repair:

* A back-adjusted continuous series is **not** appropriate for an event study: the
  question is what a contract actually did in a 30-minute window, so the panel must be
  keyed on `instrument_id + expiration` and the specific contract named.
* The **front contract is not always the right contract** near expiry, and physical
  delivery at Cushing makes the expiring contract behave idiosyncratically. A
  liquidity-based nearby convention (Databento's `CL.v.0`) and an expiry-proximity
  exclusion are both candidate rules — and choosing between them is an S1 design task,
  not an S0 assertion.

## B.7 Scarcity — what external authority actually supports

Two definitions have genuine institutional authority, and they are **not** equivalent:

| candidate | what it is | authority |
|---|---|---|
| **Days of supply** | `W_EPC0_VSD_NUS_DAYS`, an official EIA weekly series: commercial crude stocks ÷ current daily consumption rate. Continuous, published, known before the release | EIA publishes it as a series in its own right |
| **Deviation from the 5-year seasonal range** | Current commercial stocks versus the trailing 5-year average for the same week of year. Continuous. This is **EIA's own presentational convention** and the industry standard for reading a level seasonally | EIA WPSR / *This Week in Petroleum* charting convention |

A third, **storage-capacity utilisation**, is economically attractive (it is the
convexity story: scarcity bites when tanks are near empty, gluts bite when near full) but
EIA has published working storage capacity only **semi-annually since 2011**, which makes
it a poor weekly point-in-time conditioner. Recorded and parked.

**Both of the first two are point-in-time, continuous, seasonally aware and
authority-supported. They normalise by different things** — consumption versus history —
and they will not agree. See **PINS-OD-2**.

**No threshold is proposed and none may be searched.** "Bottom 20 % inventories" and any
percentile cut are explicitly excluded: no external authority justifies a specific cut,
and choosing one from data would be the exact failure mode this programme exists to
prevent.

---

# C. PROPOSED STUDY DESIGN

*A proposal for S1 to accept, amend or reject. Nothing here is sealed.*

## C.1 The primary research question

> **Does a first-published unexpected change in U.S. commercial crude oil inventories
> produce a directionally consistent WTI futures price response that survives a realistic
> post-release execution delay and realistic release-window costs; and is that response
> systematically stronger when the pre-release physical inventory state was already
> scarce?**

```
PRIMARY_CLAIM_TYPE = REDUCED-FORM PREDICTIVE / EVENT-RESPONSE.
                     Not causal. Not a market-efficiency claim. Not a forecast of
                     inventories. Not a claim about OPEC, shale, or the oil market
                     in general.
```

## C.2 Three claims, kept separate

The single most important structural decision in this frame. These must never be
collapsed, and a later document that reports one as evidence for another is in breach of
this frame.

```
CLAIM A   INVENTORY NEWS EXISTS
          The first-published actual change differs from the market's pre-release
          expectation, materially and repeatedly.
          -> a DATA claim. Falsifiable without touching any price.

CLAIM B   PRICE RESPONSE EXISTS
          The surprise predicts the direction/magnitude of POST-RELEASE WTI returns
          measured from a realistic entry.
          -> the PRIMARY claim.

CLAIM C   SCARCITY MODERATION EXISTS
          The response to the same surprise is stronger when pre-release inventories
          were already scarce.
          -> a SEPARATE claim. B can hold while C fails. C cannot rescue B.
```

**Claim A is testable before Claim B**, using no price data at all, and it is the
cheapest thing in this lineage. That ordering is deliberate (see §C.8).

## C.3 The information object

```
FIRST_PUBLISHED_ACTUAL = the change in U.S. commercial crude oil stocks excluding SPR,
                         AS PUBLISHED in the WPSR release of week t and never as later
                         revised. Source: the per-release EIA archive (§B.2).
                         Series identity: WCESTUS1 / WPSR Table 1.

INVENTORY_SURPRISE_t   = FIRST_PUBLISHED_ACTUAL_CHANGE_t  -  PRE_RELEASE_EXPECTATION_t

                         where PRE_RELEASE_EXPECTATION is UNRESOLVED -> PINS-OD-1.
```

```
actual  -  zero               is NOT news.        Explicitly excluded.
actual  -  a model fitted today on the full history   is NOT contemporaneous market
                              expectation, and substituting it silently would be a
                              DIFFERENT HYPOTHESIS. Explicitly excluded.
```

## C.4 Sign convention — proposed, to be frozen before outcomes

```
POSITIVE_INVENTORY_NEWS  =  a LARGER-THAN-EXPECTED DRAW
                            i.e.  surprise = expectation - actual_change
                            so a bigger-than-expected fall in stocks is positive.

PROVISIONAL EXPECTED SIGN:  positive news -> bullish WTI response.
```

The economics is intuitive and the literature's "inverse impact of unexpected inventory
*changes* on returns" is the same statement with the opposite algebraic sign. **The exact
algebra must be fixed against the verified EIA definition of the published change before
sealing**, and once sealed there is no later sign flipping.

**A real complication, recorded not hidden:** Rousse & Sévi document an over-reaction
partly compensated in the following hours. If the primary horizon lands inside the
compensation window, the sign of a harvestable response could be *opposite* to the sign
of the immediate response. The sign convention and the primary horizon are therefore
**one joint decision**, not two — see **PINS-OD-3**.

## C.5 The scarcity state

```
SCARCITY_t-1           = a CONTINUOUS, pre-release, point-in-time physical measure of
                         how tight U.S. commercial crude inventories already were.
SCARCITY_DEFINITION    = UNRESOLVED -> PINS-OD-2
SCARCITY_POINT_IN_TIME = YES for both live candidates (both are functions of
                         previously published WPSR releases only)
SEASONALITY_TREATMENT  = mandatory and definition-specific. Days-of-supply carries
                         seasonality through the consumption denominator; the 5-year
                         deviation removes it by construction. They are NOT
                         interchangeable.
```

Hard constraints, whichever definition wins: known strictly before release *t*;
reconstructible from first-published vintages only; **no threshold, no percentile, no
regime dummy, no same-release information**.

## C.6 Estimand — parsimonious, and explicitly not a kitchen sink

```
POST_RETURN_t  =  a  +  b1 * NEWS_t  +  b2 * SCARCITY_t-1  +  b3 * NEWS_t x SCARCITY_t-1  +  e_t

b1   the news response                         -> CLAIM B, the PRIMARY coefficient
b3   the scarcity-moderation coefficient       -> CLAIM C, SECONDARY, no rescue power
b2   present for correct interpretation of the interaction, not as a claim
```

**`b1` is primary and `b3` is not.** The candidate is "inventory news moves price,
possibly amplified by scarcity"; a design in which the interaction alone carries the
verdict would be a different, weaker and much easier-to-overfit study. Whether the
candidate must pass **both** b1 and b3, or b1 alone with b3 reported as a conditional
second gate, is an S1 decision — the BENB two-gate structure is the obvious precedent.

Deliberately **absent** from the primary specification: trend, carry, curve slope,
realised volatility, macro variables, dollar index, positioning. None is necessary for
identification of a response to a scheduled release. Each may become a **diagnostic** at
S1 with declared powers, never a primary regressor.

### The timing split — carried forward from BENB

The single most important structural borrowing from the closed BENB lineage. The release
response must be decomposed so the unreachable part is separated from the reachable part
**in the sealed contract**:

```
R_PRE      =  pre-release drift, from some point before 10:30 to 10:30:00
              -> NOT harvestable by this signal. Rousse & Sevi show it is non-zero.
R_JUMP     =  10:30:00 to the earliest realistic entry
              -> NOT harvestable. This is where the literature says most of the
                 response lives.
R_TRADABLE =  earliest realistic entry -> end of the primary horizon
              -> THE ONLY HARVESTABLE LEG. The primary claim lives here and nowhere else.
```

A study that reports a large coefficient on the 10:30-to-10:31 return has demonstrated
that the market works, not that a CTA can earn anything. BENB is the programme's proof
that this distinction changes the verdict.

## C.7 Distinctness from carry, curve and trend

```
DISTINCT_FROM_CARRY = YES (conditional on the identification test below)
DISTINCT_FROM_CURVE = YES (conditional on the identification test below)
DISTINCT_FROM_TREND = YES
```

The distinguishing object is **new physical information released at time t relative to
what the market expected before t**. By construction a surprise is orthogonal to the
pre-release information set, and therefore cannot be read off pre-release futures prices
— which is precisely what backwardation, inventory level and term structure are.

But the scarcity state is a **different matter**: an inventory level is plausibly already
encoded in the curve, since convenience yield is the storage-theory link between scarcity
and backwardation. So:

> **MANDATORY IDENTIFICATION REQUIREMENT for S1.** A supported result must demonstrate
> that `NEWS` carries information **incremental to pre-release futures prices**,
> including the pre-release curve slope. If the whole hypothesis can be expressed using
> only pre-release futures prices, it is **not sufficiently distinct** and must be closed
> as a relabelled carry study. This diagnostic carries **DAMAGE power** and no promotion
> power.

Two further contamination risks recorded: the pre-announcement drift means the curve at
10:29 may already contain part of the surprise; and the **API release the previous
afternoon** is itself pre-release public-ish information about the same physical quantity.

## C.8 The cheapest decisive gate

```
GATE 0   DATA / PIT FEASIBILITY                     <- cheapest, no price data at all
         Can ALL FOUR be reconstructed point-in-time?
           (a) first-published EIA actual        -> §B.2 says YES from 2012-01-05
           (b) pre-release market expectation    -> PINS-OD-1, UNRESOLVED
           (c) pre-known scarcity state          -> YES once PINS-OD-2 is taken
           (d) executable intraday CL prices     -> obtainable, not held
         If NO -> close or park BEFORE any outcome. No trial spent.

GATE 0.5 CLAIM A — DOES NEWS EXIST AT ALL?
         Is the surprise series materially non-degenerate and non-trivially
         autocorrelated? This uses NO price data and can falsify the lineage for
         a few dollars. It is a DATA claim, not a performance claim.

GATE 1   CLAIM B — INFORMATION RESPONSE
         Does NEWS have the predeclared directional response in R_TRADABLE?

GATE 2   CLAIM C — SCARCITY MODERATION
         Is the same response stronger in the predeclared scarcity direction?

GATE 3   HARVESTABILITY
         After the realistic entry delay and release-window costs, is anything left?
```

**No portfolio relevance is built into the first historical run**, and none is authorised
by this frame.

## C.9 Negative outcome taxonomy — defined before outcomes

```
A  DATA / PIT FAILURE          first-published actual, consensus, scarcity state or
                               executable prices cannot be reconstructed properly
B  NEWS NOT INFORMATIVE        the surprise has no supported directional response
C  PRICE DISCOVERY TOO FAST    news moves price, but the move is complete before a
                               realistic entry. (The BENB outcome shape.)
D  SCARCITY MODERATION NOT SUPPORTED    B holds, C does not
E  EFFECT PRESENT BUT UNECONOMIC        a tradable response exists but the target
                               economic margin is reliably excluded
F  LOW POWER / UNRESOLVED      evidence can neither establish nor exclude usefulness
G  SUPPORTED                   the predeclared edge survives identification, timing
                               and economic gates
```

**Only B is anything like "the mechanism is not there."** A, C, E and F are all
non-falsifying, and a later document that describes any of them as "falsified" is in
breach of this frame. Class C in particular is a statement about *this signal's timing*,
never about the economics.

## C.10 Effective sample size — and what it is not

```
EXPECTED_RAW_RELEASE_COUNT  = 765 archived EIA releases, 2012-01-05 .. 2026-09-10
                              (enumerated from the EIA archive index; ~52/yr)
                              Intersecting the Databento CL window (from 2010-06)
                              does not bind: the EIA archive is the shorter leg.

EXPECTED_EFFECTIVE_REGIMES  = UNKNOWN AT S0, DELIBERATELY.
```

**765 weekly reports are not 765 independent macro experiments.** The surprise may be
close to independent week to week; the **scarcity state is a slow-moving stock variable**
and is strongly autocorrelated, so the number of independent scarcity regimes is of the
order of the number of multi-month inventory cycles in the window, not the number of
weeks. The interaction coefficient `b3` is therefore identified off far less information
than `b1`, and any inference must respect that — block bootstrap by inventory cycle or by
calendar year, never i.i.d. resampling of weeks.

The discovery prior's *15–25 meaningful scarcity episodes, ~5 extreme* is **ADVISORY
ONLY and was not verified**, because verifying it would require computing the historical
scarcity feature, which §26 forbids at S0.

**Window note:** the usable window begins 2012, so the **2008 crisis is absent**. It
contains the 2014–16 crash, the 2020 COVID collapse — including the **April 2020 negative
WTI settlement**, a structural event no event study over this window may ignore — and the
2022 Russia/SPR-release period.

## C.11 Cost and materiality — both unresolved, and deliberately not invented

```
TRANSACTION_COST_MODEL_STATUS = NOT ESTABLISHED. A defensible pre-outcome fixed cost
                                model is BLOCKED ON DATA, not on judgment.
ECONOMIC_MATERIALITY_STATUS   = NOT SET. No numerical threshold is proposed.
```

**Cost.** The generic 2 bps ETF convention is **explicitly not imported**; nor are
BENB's 5/10 bps. Wen et al. verify that liquidity *falls* around the release, so the
release window is precisely where a generic convention would be most wrong. What exists:
no CL spread evidence anywhere in the repository, and a proven ability to buy
`bbo-1s` quote data (observed at ~$6.5 per symbol-quarter for a different product —
**an order of magnitude, not a CL quote**). The honest position is that the cost model
should be **measured from release-window quote data before sealing**, not assumed.

**Materiality.** BENB's `+0.30` and TA's `+0.30` are **not** portable. Aaron's own
BENB-OD-1 established that a materiality bar is lineage-specific and cannot be lent
between lineages. This is an event study in bps per release, and what "economically
useful" means for ~52 discrete events per year is a different object from a calendarised
sleeve Sharpe. The candidate scales are recorded as alternatives in **PINS-OD-4**; none
is chosen here.

---

# D. NOT-YET-TESTED CLAIMS

*Everything below is a hypothesis. Nothing has been computed.*

1. That the first-published actual differs materially and repeatedly from the market
   expectation (**Claim A**).
2. That the surprise predicts the direction of post-release WTI returns (**Claim B**).
3. That the response is stronger under pre-release scarcity (**Claim C**).
4. That anything survives a realistic entry delay and release-window costs.
5. That the archived per-release CSVs are the true publication vintage (§B.2 caveat).
6. That the ~20–25 minute decay window is correct (secondary sources only).
7. That `NEWS` carries information incremental to the pre-release curve (§C.7).
8. That the effective number of independent scarcity regimes is adequate for `b3`.
9. That any of this is distinct from what a trend follower already earns in crude.

**No historical surprise, scarcity value, interaction value, conditional return,
regression, event P&L, Sharpe, hit rate, threshold count or extreme-event list was
computed, inspected or plotted. No "big draws and what WTI did next" was looked at. 2008,
2020 and 2022 outcomes were not inspected.**

---

# E. PARKED QUESTIONS

*Recorded so they are not silently resolved later.*

1. **Pre-2012 vintages.** Whether `ir.eia.gov` WPSR releases before 2012 are
   reconstructible from web archives. Would add ~2008–2011 including the GFC.
2. **API WSB as the expectation.** Ye & Karali's construction (EIA surprise relative to
   the previous afternoon's API print) is academically standard and **avoids the survey
   problem entirely** — but API is subscription-only via Refinitiv/ICE. Whether Aaron has
   or wants such access is an Owner question, not a design question. *If it were
   available it would likely be the strongest option, and that is why it is surfaced in
   PINS-OD-1 rather than quietly dropped.*
3. **Storage-capacity utilisation** as the scarcity variable — economically the best
   story, but EIA publishes working capacity only semi-annually since 2011.
4. **April 2020 negative prices.** Log returns are undefined through negative settlements.
   Requires an explicit, pre-outcome, non-discretionary rule. Not a licence to drop 2020.
5. **Contract convention near expiry** — liquidity-based nearby versus front, and the
   expiry-proximity exclusion.
6. **Whether a PINS coefficient is a member of KB-2's frozen `N_trials = 14`**, or a new
   family on a reused sample. S1 question with real consequences.
7. **Products other than crude** — gasoline, distillates, natural gas, Brent. Each is a
   **separate lineage**. None is added here and none may be added silently.
8. **Asymmetry of draws versus builds.** Ye & Karali find asymmetric cross-commodity
   responses; Bu finds regime dependence. Testing asymmetry is a second hypothesis, not a
   free diagnostic, and it doubles the claim surface if admitted.

---

# F. FORBIDDEN INTERPRETATIONS

*Binding on every later document and seat in this lineage.*

```
THIS IS NOT A CRISIS DIVERSIFIER and must never be described as one.
```

The provisional portfolio role is **PHYSICAL-NEWS / FUNDAMENTAL INFORMATION EDGE**,
possibly a trend complement or short-horizon event alpha. **No portfolio test exists in
this frame and none is authorised by it.** Any eventual portfolio study must separately
examine crisis behaviour, trend overlap, commodity-sleeve concentration, and whether the
"event alpha" merely adds crude exposure — the VRP lesson, recorded here before any
result exists.

A supported result would **NOT** establish:

* that inventory announcements *cause* oil price moves — the design is reduced-form;
* that the oil market is inefficient, or that anyone trades on leaked data;
* anything about OPEC, shale production, refinery behaviour or physical arbitrage;
* that the same effect exists in gasoline, distillates, natural gas or Brent;
* that EIA's published estimates are accurate — the study uses what was *published*,
  which is the market's information set, not the truth;
* any improvement to canonical TSMOM or to any existing sleeve.

A **negative** result would **NOT** establish:

* that inventory news is uninformative — Class C explicitly means the opposite;
* that the storage-theory link between scarcity and price is wrong;
* that a different instrument, horizon or expectation source would also fail.

```
EVIDENCE_CEILING = supported.  NEVER confirmed. NEVER independently confirmed.
```
The CL price history is reused/burned context (KB-2). A new physical leg does not launder
a reused price sample — the identical reading the BENB lineage sealed and this frame
inherits.

---

# G. DESIGN EXPOSURE

```
ASTRA_DESIGN_EXPOSED = YES
FABLE_DESIGN_EXPOSED = NO
```

**GPT-6 Astra is a `material_design_contributor` to this exact candidate.** It supplied
the physical-inventory-news × scarcity candidate itself, the EIA crude emphasis, the
point-in-time consensus warning, the immediate-price-discovery risk, the curve-overlap
warning and the effective-N caution. Astra is therefore **barred from blind certification**
of this design or any result under it.

**Claude Fable 5.1 is NOT exposed to this lineage.** Fable's discovery work included a
*related but different* candidate — an inventory-state commodity curve study — and this
frame **imports no Fable-specific design content**. The candidate, the market, the
release object, the expectation problem, the scarcity treatment and the timing split all
come from Astra's contribution, from the verified literature, or from the two closed
programme lineages.

This status is **load-bearing**: it is what preserves Fable as an eligible delegated
Owner-advice seat for the decisions in §H. If a later session materially uses Fable F4
design content to resolve this lineage, that exposure must be recorded honestly and Fable
becomes barred.

---

# H. OWNER DECISIONS

```
HIGH_DIFFICULTY_OWNER_DECISION_REQUIRED = YES
FABLE_OWNER_ADVICE_RECOMMENDED          = YES
```

Four decisions are open. **They are not independent and they should not be taken
together**: PINS-OD-1 is a gate, and if it closes the lineage the other three never need
to be answered. Only **PINS-OD-1 is being asked now**.

## PINS-OD-1 — THE EXPECTATION SOURCE *(asked now; blocking)*

**OWNER_DECISION_QUESTION**

> What is the pre-release expectation against which the first-published EIA crude
> inventory change is differenced — and is the required source lawfully available to
> Aaron on a point-in-time basis?

**ALTERNATIVES**

```
(1) SURVEY CONSENSUS — the academic standard (Reuters / Bloomberg / Platts poll
    median, published Mon-Tue before the Wednesday release).
    STATUS: no such data exists on this machine; all three are licensed products.
    Economic-calendar sites (Investing.com, FXStreet, Forex Factory, TradingEconomics)
    display a historical "forecast" column, but the provenance of that number is
    undocumented (whose survey, median or mean, revised or as-of), and redistribution
    is restricted by their terms. UNVERIFIED PROVENANCE IS NOT POINT-IN-TIME.

(2) API-AS-EXPECTATION — Ye & Karali's construction: the EIA surprise measured
    relative to the API Weekly Statistical Bulletin published ~4:30 p.m. ET the
    previous afternoon.
    STATUS: academically standard, avoids the survey problem entirely, genuinely
    point-in-time. Subscription only, via Refinitiv or ICE. Cost and entitlement
    unknown to this session.

(3) MODEL-BASED EXPECTATION — a forecast built from the first-published history
    (seasonal, lagged-change, or similar), fitted strictly point-in-time.
    STATUS: always available, costs nothing, and IS A DIFFERENT HYPOTHESIS. It tests
    "deviation from a statistical norm", not "news relative to what the market
    expected". Under this option the lineage must be renamed and reframed.

(4) CLOSE THE LINEAGE at S0 as a DATA/PIT failure (negative outcome class A),
    spending no trial and no data budget.
```

**WHY_IT_MATTERS**

This is not plumbing. It selects the estimand:

* Options 1 and 2 test **market news**. Option 3 tests **statistical deviation**. They
  are different claims with different economic meanings, and a result under one is not
  evidence for the other.
* **Halova, Kurov & Kucher (2014) is the reason this cannot be waved through**: they show
  the OLS price-impact coefficient is materially biased by measurement error in the
  surprise, with corrected estimates about **twice** OLS for petroleum. A weak expectation
  proxy therefore produces a *false negative* — the lineage would fail for a measurement
  reason while appearing to fail for an economic one, which is the most expensive kind of
  wrong answer this programme can produce.
* Option 3 has a subtler trap. A model fitted on first-published history is point-in-time
  in the narrow sense, yet it still asserts that the market's expectation *was* that
  model. Nothing tests that assertion, and the resulting "surprise" may be large exactly
  when the model is bad rather than when the market was wrong.
* Option 4 is a legitimate answer. Closing here costs one S0 and no trial.

**MY POSITION:** I have not chosen, and under §25 I must not. The decision changes the
claim, and the claim is the Owner's.

## PINS-OD-2 — SCARCITY DEFINITION *(recorded; deferred behind OD-1)*

> Days of supply (`W_EPC0_VSD_NUS_DAYS`, normalising by consumption) **or** deviation
> from the trailing 5-year seasonal average (normalising by history)?

Both are continuous, point-in-time and authority-supported. They measure different
things, `b3` is defined relative to whichever is chosen, and a design that tried both and
reported the better one would be threshold mining by another name. A third option —
declaring one primary and the other a declared robustness cell with no promotion power —
is available and is itself an Owner choice.

## PINS-OD-3 — EXECUTION LATENCY AND PRIMARY HORIZON *(recorded; deferred)*

> One realistic post-release entry delay, and one primary response horizon — jointly,
> because the sign convention depends on both.

The literature does not settle this. The immediate response is a jump; Rousse & Sévi
document an over-reaction *partly compensated in the following hours*; Wen et al. find
the announcement half-hour predicts the **last** half-hour. So a short horizon and a long
horizon can have **opposite** expected signs, and no horizon family or search is
permitted. A primary-source confirmation of the decay window is a prerequisite input.

## PINS-OD-4 — ECONOMIC MATERIALITY SCALE *(recorded; deferred)*

> What is the economically meaningful object — bps per release, return per unit of
> release-window risk, an event-strategy Sharpe, or an annualised sleeve Sharpe on ~52
> events a year — and is a numerical bar set at S1 or left to S4?

No numerical threshold is proposed. BENB's and TA's `+0.30` are **not** inherited;
BENB-OD-1 established that such a bar is lineage-specific.

---

# I. WHAT WOULD CHANGE THE STATUS

```
S0 = PASS  requires PINS-OD-1 resolved to option (1) or (2) WITH a verified,
           lawfully accessible, documented point-in-time source; then OD-2, OD-3
           and OD-4 taken; then a Gate-0 data-feasibility pass.

S0 = PASS (reframed)  if PINS-OD-1 resolves to option (3), the lineage is renamed
           and reframed as a statistical-deviation study, and the claim vocabulary
           in this frame is rewritten accordingly. It is NOT the same candidate.

S0 = FAIL  if PINS-OD-1 resolves to option (4), or if no expectation source of any
           kind is reconstructible. Negative outcome class A. No trial spent.
```

**Nothing in this frame authorises S1, a seal, a build, a data purchase, or any
computation on any candidate outcome.**

---

*CTA-EDGE-03-PINS S0: the question is defined, the data path is mapped, and the one
decision that determines what is being asked is left where it belongs.*
