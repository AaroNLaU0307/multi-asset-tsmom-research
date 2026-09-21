# TA_S0_FRAME — `CTA-EDGE-01-TA` — Treasury auction supply absorption

```
LINEAGE_ID        = CTA-EDGE-01-TA
CANDIDATE         = TREASURY_AUCTION_SUPPLY_ABSORPTION
STAGE             = S0 FRAME — RESEARCH-QUESTION DEFINITION ONLY
STATUS            = PROPOSAL, AWAITING CONTROLLER / OWNER ACCEPTANCE
CREATED           = 2026-09-15
AUTHOR            = Claude Opus 5 (Main Agent / builder seat)
AUTHORITY         = QUANT_WORKFLOW_VNEXT.md (workspace root). This document
                    authorises NOTHING: no build, no fetch, no run, no reveal.
DATA_FETCHED               = NO
CANDIDATE_OUTCOME_ACCESSED = NO
BACKTEST_RUN               = NO
BUILD_STARTED              = NO
S1_SEAL_CREATED            = NO
RUN_AUTHORIZATION_CREATED  = NO
```

> **Reading rule.** Section **A** is fact. Section **B** is external literature —
> other people's results, never this programme's evidence. Section **C** is a
> **proposal**. Section **D** lists what is **not yet tested**. Section **E** is
> parked. Section **F** is forbidden. Nothing in C, D or E may be cited as an
> established property of this programme.

---

## A. CURRENT FACTS / AUTHORITY

### A.1 Programme state — read, unchanged by this document

| object | state at the time of writing | touched here? |
|---|---|---|
| canonical TSMOM | `SUPPORTED — NOT INDEPENDENTLY CONFIRMED`, frozen research benchmark | **NO** |
| C-A prospective confirmation | sealed, LIVE under passive monthly accrual, `N_scored = 0`, terminal reveal unconsumed | **NO — not accessed, not inferred, not inspected** |
| C-D independent verification | `HOLD` on the unexplained October-2008 cross-vendor residual D-S5 | **NO** |
| TSMOM-VRP-01 | `CLOSED` — `UNRESOLVED` / Class 3; prospective declined by Owner | **NO** |
| Time-Series Value, X01, XSMOM, the four overlays | closed | **NO** |
| Quant Research Knowledge Base repository | not the active workstream | **NOT MODIFIED** |

Sources read: `README.md`, `PROJECT_STATE.md`, `../../../QUANT_WORKFLOW_VNEXT.md`,
`research/TSMOM_PROGRAMME_HANDOFF_2026-09.md`,
`research/extensions/SAMPLE_REUSE.md`, `research/extensions/TRIAL_LEDGER.md`,
`ops/EXECUTION_AUTHORIZATIONS.md`.

### A.2 Prior programme record specific to this candidate

- **Phase C disposition (handoff §4.2):** *Treasury auction / intermediation* =
  **RESERVE candidate for a future cycle; not started.** VRP was selected over it.
  There is therefore **no prior TSMOM auction study, no prior auction-conditioned
  statistic and no prior auction result** in this repository.
- **Handoff §10 research map** lists *Treasury auction / intermediation* under
  MACRO / RATES, explicitly *"where the evidence and the event count support it"*,
  and states that the map is **a map, not permission**.
- **Handoff §9 lineage convention** names `CTA-EDGE-01` as an example identifier
  for a new separate lineage. `CTA-EDGE-01-TA` follows it.
- **Adjacent closed work, checked for overlap:**
  - `research/yield_spread/` — the yield-curve **slope-level regime gate** overlay.
    Different object: a level used as a gate on the canonical book.
  - `research/seasonality/` — calendar-regularity overlay. Its bond turn-of-month
    cell was **0/18**, a prior *against* a bond calendar artefact producing a false
    positive. A useful negative prior, not an overlap.
  - No repository file other than the two Fable discovery documents and the
    programme handoff mentions Treasury auctions at all (repository grep, 2026-09-15).
- **No idea-registry row exists for this candidate.**
  `research/extensions/idea_registry/IDEA_REGISTRY*.csv` predate Phase C.

### A.3 Local data facts — metadata only, no event returns read

Verified from the `data/close_prices_raw.csv` header, `data/fetch_metadata.csv` and
a first/last non-null scan. **No return was computed and no auction-conditioned view
was taken.**

| fact | value |
|---|---|
| panel | `data/close_prices_raw.csv`, 30 yfinance adjusted-close series, 8,400 rows, 1993-01-29 → **2026-06-12**, sha256 `3d2a7a56…0c05c3c31` (KB-1) |
| IEF | present; first non-null **2002-07-30**; last **2026-06-12**; 6,007 non-null rows |
| TLT | present; first non-null **2002-07-30**; last **2026-06-12**; 6,007 non-null rows |
| SHY (proposed negative control) | present; 6,007 rows, same coverage |
| SPY (proposed placebo) | present; 8,400 rows |
| convention | **adjusted** close — dividend- and split-adjusted, i.e. total return, not price return. The concession is a *price* effect and these ETFs accrue coupon daily. Over equal-length adjacent windows the accrual largely differences out (C.6), but it is not zero. |
| frozen boundary | everything after **2026-06-12** is outside the panel |

**Sample-reuse status (`SAMPLE_REUSE.md` KB-1).** The ETF panel is **burned 6 of 6**
registered research paths and carries `must_not_be_retested_on_same_sample`. Any
result here is **context T0 — dependent evidence, never independent confirmation**,
and the reuse must be disclosed. Evidence ceiling: **at most `supported`**; never
`confirmed`, never `independently confirmed`.

**Trial accounting (`TRIAL_LEDGER.md` §3.2, §4).** `D-ETF-COUNT` is **OPEN**
(`UNKNOWN_PENDING_AARON_DECISION`). The standing rule is: until it is decided, no
`N_trials` figure may be asserted for this panel and no DSR computed against an
invented count. The design in section C **needs neither** — its materiality rule
(C.7) uses no DSR and no trial-count deflation. So `D-ETF-COUNT` is **not a blocker
for this lineage**, and it is **not decided here**. It remains Aaron's.

### A.4 Seat / exposure facts

- **Fable 5.1** contributed the candidate, the ETF mapping, the reduced-form
  event-window framing and the dealer-inventory secondary
  (`../../../2026-09-15-cta-edge-discovery-r1-mechanism-feature-map-fable-01.md`,
  family **F1**, with **F2** as the conditional cell).
- **GPT-6 Astra** contributed the identification challenge: duration-weighted
  announced supply, point-in-time dealer inventories, when-issued pricing, cash
  Treasury / futures information, the auction-vs-duration-vs-macro separation, and
  the warning that constrained-intermediation episodes are far fewer than raw
  auctions. **Astra's round-1 output is not on disk in this workspace**; it reached
  this session only through the controller's task brief. That is a provenance
  limitation, recorded rather than papered over: the *substance* was accepted and
  acted on below, but this document cannot cite Astra bytes.

```
FABLE_DESIGN_EXPOSED = YES
ASTRA_DESIGN_EXPOSED = YES
```

Neither may later be presented as the sole blind independent certifier of this
design or of any result under it. This mirrors `ops/REVIEWER_EXPOSURE_LOG.md`
rows S27/S28 for the VRP lineage. **No row is written to that log here** — writing
to the reviewer-exposure ledger is governance *execution*, and this task is a frame.
The row is an S1 item (C.12).

---

## B. EXTERNAL LITERATURE PRIOR

**Status of this section:** external results. They fix the mechanism and let the
event windows be predeclared. They are **not evidence for this programme**, and no
reported Sharpe, t-statistic or effect size is imported as a programme claim.

Every source below was **read from the primary document**, not recalled. The Fable
references that could not be verified as stated are flagged in B.5.

### B.1 Fleming, Liu & Nguyen (2026) — the decisive current source

| field | value |
|---|---|
| title | *Intraday Price Pressure and Order Flow Around U.S. Treasury Auctions* |
| authors / year | Michael Fleming (FRBNY), Weiling Liu (Northeastern), Giang Nguyen (Penn State); FRBNY Staff Report **no. 1188**, March 2026, **revised July 2026**; doi 10.59576/sr.1188 |
| market / instrument | US Treasury secondary market, **on-the-run** nominal coupon securities (2, 3, 5, 7, 10, 30-year); interdealer trades and quotes (GovPX 1991–2000, BrokerTec 2001–2024) |
| sample | 1991-06-25 → 2024-07-24 (33 years) |
| frequency | **intraday**, one-minute resolution |
| event window | six hours. `ΔY(pre) = Y(0−) − Y(−180 min)`, `ΔY(post) = Y(+180 min) − Y(0+)`, where `0` is the auction close / results release |
| direction | yields **rise** into the auction and **fall** after results — an inverted V |
| pre / auction-day / post | the effect is **centred on auction day itself**, tightly around the 1:00 p.m. close and the results release |
| causal claim | **causal supply effect claimed** for the intraday result, on the strength of the narrow window plus a placebo: FOMC and employment releases do **not** produce the same inverted V. Dealer-constraint transmission is evidenced through **net order flow** |

Magnitudes actually printed in the paper (Tables 2 and 3, full sample 1991–2024,
bps; `***` p<0.01, `**` p<0.05, `*` p<0.1):

| | 2Y | 3Y | 5Y | 7Y | **10Y** | **30Y** |
|---|---|---|---|---|---|---|
| yield pressure (6h) | 0.712*** | 0.749*** | 1.038*** | 0.659*** | **1.192*** | **0.869*** |
| `ΔY(pre)` | 0.397*** | 0.355*** | 0.565*** | 0.221 | 0.442*** | 0.634*** |
| `ΔY(post)` | −0.315** | −0.394*** | −0.473*** | −0.438*** | −0.750*** | **−0.235 (n.s.)** |
| **price** pressure (6h) | 1.336*** | 2.255*** | 4.615*** | 4.020*** | **9.905*** | **17.106*** |
| pre-auction return | −0.733*** | −1.134*** | −2.523*** | −1.204 | −3.822*** | −12.075*** |
| post-auction return | 0.603** | 1.120*** | 2.107*** | 2.816*** | 6.084*** | **5.031 (n.s.)** |

Subsample **price** pressure (Table 3 Panel B):

| era | 10Y | 30Y |
|---|---|---|
| S1 1991–2006 | 10.883*** | 6.296 (n.s.) |
| S2 2007–2014 | 15.222*** | 25.514*** |
| **S3 2015–2024** | **5.165\*** | **14.224\*** |

Five findings from this paper materially shape the frame.

1. **Scale calibration.** The authors replicate Lou et al.'s **10-day** daily-frequency
   measure and report the 10-day yield effect at **roughly 2–5 bps** full sample, of
   which the six-hour window is **about 25 %**. The multi-day, daily-close effect is
   therefore roughly **four times** the six-hour numbers above.
2. **Attenuation is real and documented.** *"the strong auction-cycle effects
   documented by Lou et al. (2013), whose sample ends in 2008, do not persist at the
   same magnitude when the sample is extended through 2024."* Post-2014 yield
   pressure is **less than half** the earlier magnitudes; F-tests reject equality
   after 2014 for the 3- and 10-year. The same conclusion holds at the 10-day daily
   frequency (their Online Appendix Table A2).
3. **The auction-day afternoon carries a large share of the reversal.** The post leg
   starts one minute after the results release, ~1:02 p.m. ET. A **close-to-close
   daily ETF study structurally cannot capture the 1:02 p.m.–4:00 p.m. portion of the
   reversal.** This is a declared, irreducible attenuation of the ETF design (C.4).
4. **Cross-maturity spillover is asymmetric** (Table 4, six-hour yield pressure in
   each secondary-market maturity, by auctioned tenor):
   - a **10-year auction** moves the **whole curve** — 2Y 1.013\*\*\*, 3Y 1.076\*\*\*,
     5Y 1.259\*\*\*, 7Y 0.796\*\*\*, 10Y 1.192\*\*\*, **30Y 1.294\*\*\***;
   - a **30-year auction** moves **only the long end** — 30Y 0.869\*\*\*, with
     2Y −0.073, 3Y −0.035, 5Y 0.182, 7Y 0.326, 10Y 0.395, **none significant**.
   - The effect is **not confined to on-the-run** securities: their Online Appendix
     Table A3 finds qualitatively similar patterns for first-off-the-run. This is the
     single most supportive fact for an ETF-basket mapping.
5. **The 20-year is excluded by the authors**, because issuance was suspended
   **June 1986 → May 2020** (footnote 9). The same footnote records the **30-year
   bond issuance gap, August 2001 → February 2006**.

### B.2 Lou, Yan & Zhang (2013) — the origin of the daily-frequency window

| field | value |
|---|---|
| title | *Anticipated and Repeated Shocks in Liquid Markets* |
| authors / year | Dong Lou (LSE), Hongjun Yan (Yale SOM), Jinfan Zhang (Yale SOM); *Review of Financial Studies* **26(8), 1891–1912, 2013** |
| market / instrument | US Treasury secondary market; on-the-run **and off-the-run** 2-, 5-, 10-year notes; plus the repo market |
| sample | **January 1980 → June 2008** |
| event window | a **20-day window** — 10 business days before and 10 business days after each auction, tracking the same security throughout |
| direction | yields rise before, fall after — the inverted V |
| reported | 5-day pre / 5-day post yield change: 2Y **+2.53 / −2.32** bps; 5Y **+2.67 / −2.74**; **10Y +1.57 / −2.00**. Return differential (post minus pre) at 5 days: 2Y 8.89 bps (t = 2.93), 5Y 22.54 (t = 3.67), **10Y 23.84 (t = 1.78)**. Issuance cost at t = 5: 9.07 / 16.81 / **18.43** bps of auction size |
| causal claim | **reduced-form association**, *linked to* limited dealer risk-bearing capacity and imperfect end-investor capital mobility. Not an identified causal design |
| strategy claim | a **duration-neutral relative-value** trade — short the on-the-run 2-year, long a duration-matched 6-month-bill + 10-year portfolio for the 10 days before, reversed for the 10 days after — with annualised Sharpe **0.84** at t = 10 over 1998–2008, **after bid-ask spreads and repo funding costs** |

**That strategy is not the strategy framed here**, and the difference is material:
theirs is **duration-neutral relative value** on a single on-the-run security financed
in repo; an IEF/TLT position is an **outright duration bet in a basket**. Their Sharpe
does not transfer and is not cited as a prior for ours.

### B.3 Somogyi, Wallen & Xu (2025) — the post-2010 reversal in the long end

| field | value |
|---|---|
| title | *What Treasury Auctions Reveal About Investor Demand* |
| authors / year | Fabricius Somogyi (Northeastern), Jonathan Wallen (HBS), Lingdi Xu (Harvard); HBS Working Paper **26-033**, version **2 December 2025** |
| market / sample | US Treasury auctions, bidding data, **1992 → present**, long-term Treasuries |
| finding | demand elasticity collapsed — 1992–2010, a 1 % supply increase ≈ **+2 bps** on long-term yields; **since 2010 ≈ +9 bps**, about five times more inelastic |
| **the fact that matters here** | prior to 2010, long-term yields declined on average by **1.5 bps after auctions**; after 2010 the trend **reversed and yields no longer fall after auctions** |
| causal claim | measurement of demand elasticity plus association; not an identified causal design for the price path |

This is a **primary-source prior against a post-auction recovery in long-duration
Treasuries in the modern era**, and it converges with SR 1188's non-significant
30-year `ΔY(post)`. It is the single most important reason the post window is **not**
promoted to an independent primary cell (C.5).

### B.4 Corroborating work, verified as cited within SR 1188

`Fleming et al. (2024)` — secondary-market prices fall in auction weeks and rise in
subsequent weeks; the weekly-frequency statement closest to this design.
`Beetsma et al. (2016, 2018)` — Italian and euro-area sovereign auction cycles.
`Sigaux (2024)` — Italian government bonds; uncertainty about natural-buyer demand.
`Albuquerque et al. (2024)` — Portuguese; the V-shape is significant **only when
demand elasticity is low**. `Amin & Tedongap (2023)` — US TIPS; **non-dealer**
strategic behaviour, not dealers, explains the pre-auction pattern.
`Andrade & Da Rocha (2024)` — Brazil. At least four independent groups, five markets.

### B.5 Fable's recalled citations — verification outcome

| Fable's recollection | verification |
|---|---|
| "Lou, Yan and Zhang 2013" | **VERIFIED** (B.2). Fable's description is accurate. |
| "Fleming and Liu on intraday auction-day pricing" | **VERIFIED and superseded.** That working paper was retitled and is now Fleming, **Liu and Nguyen**, SR 1188 (B.1). Fable's citation is stale by a co-author and, far more importantly, **predates the attenuation result**. |
| "Beetsma et al. on euro-area auction cycles" | **VERIFIED as existing and as cited by SR 1188** (2016, 2018). **Not read at primary source here.** Recorded as corroborating, not load-bearing. |
| "at least two independent groups, two markets" | **UNDERSTATED** — the true count is ≥ 4 groups and ≥ 5 markets. |

Fable's F1 entry is otherwise sound. Its two substantive gaps, both closed here, are
(i) no awareness of the **post-2014 attenuation** and the **post-2010 disappearance of
the long-end post-auction recovery**, and (ii) the assumption that **matched
non-auction control windows** exist in this calendar — they largely do not (C.6).

### B.6 Market mechanics, verified from official sources

| fact | source | note |
|---|---|---|
| auction record dataset *Treasury Securities Auctions Data*, coverage **1979-11-15 → 2026-09-30**, "Released As Needed", last updated 2026-09-13, **114 fields** | `fiscaldata.treasury.gov/datasets/treasury-securities-auctions-data/` | documented fields include `record_date`, `cusip`, `security_type`, `security_term`, `auction_date`; the dataset description states announcement date, auction date and issue date are carried |
| API is **open — no account, no token**; `filter=field:op:value`, `sort=`, `page[number]` / `page[size]`; response `meta` carries `labels`, `dataTypes`, `total-count` | `fiscaldata.treasury.gov/api-documentation/` | endpoints are `/services/api/fiscal_service/vX/…` |
| 10-year note: **original issues** announced in the first half of **Feb, May, Aug, Nov**; **reopenings** announced in the first half of **Jan, Mar, Apr, Jun, Jul, Sep, Oct, Dec**; auctioned in the **second week**; issued on the **15th** or next business day | `treasurydirect.gov/auctions/general-auction-timing/` | ⇒ **12 auctions/year on the current schedule** |
| 20- and 30-year bonds: the **same** original-issue / reopening month pattern, auctioned in the **second week**; 30-year issued on the 15th; 20-year original issues settle at month end, reopenings on the Friday of auction week | same | 10y, 20y and 30y therefore share one mid-month week |
| competitive bidding closes **1:00 p.m. ET**; Treasury targets a **two-minute** release of results; noncompetitive results ~15 minutes before the competitive close | TreasuryDirect auction-results pages | ⇒ results are public **~1:02 p.m. ET**, three hours before the 4:00 p.m. ETF close |
| 30-year bond issuance gap **Aug 2001 → Feb 2006**; 20-year bond suspended **Jun 1986 → May 2020** | SR 1188 footnote 9 | primary source |
| NY Fed primary dealer statistics: weekly, **published Thursdays ~4:15 p.m. with a one-week lag**; available from **1998-01-28**; the series is **split into periods because the reporting structure changed** | `newyorkfed.org/markets/counterparties/primary-dealers-statistics`; OFR STFM dataset page | the breaks are real, and are why E.1 parks the dealer cell |

**Not verified, and therefore not asserted:** the *historical* auction frequency of
the 10-year note and the 30-year bond before 2009. The current TreasuryDirect
schedule is verified; the widely-held facts that the 10-year ran at eight auctions a
year before 2009, and that the reintroduced 30-year was quarterly through 2008 before
going roughly monthly in 2009, could **not** be confirmed from a primary source in
this session. Event counts in C.9 are therefore given as **ranges**, and pinning them
is a mechanical S1 task against the official record.

### B.7 ETF implementation mapping — verified

| | IEF | TLT |
|---|---|---|
| index (current) | **ICE US Treasury 7-10 Year Bond Index** | **ICE US Treasury 20+ Year Bond Index** |
| index before 2016-03-31 | Barclays US Treasury Bond 7-10 Year Term Index | Barclays US 20+ Year Treasury Bond Index |
| maturity rule | remaining maturity **≥ 7 and < 10 years**, ≥ $300 m outstanding ex-Fed | remaining maturity **> 20 years** (iShares wording: *greater than twenty years*) |
| inception | 2002-07-22 | 2002-07-22 |
| effective duration (2026-09-11) | **6.92 y** | **14.98 y** |
| weighted average maturity | 8.47 y | 26.09 y |
| **number of holdings** | **16** | **47** |
| 30-day median bid/ask | 0.01 % | 0.01 % |

**What this means economically, and where the mapping is imperfect.**

- **IEF does not hold the security being auctioned.** A newly auctioned 10-year note
  has exactly ten years remaining, and the index rule is **strictly less than ten
  years**; it becomes eligible only at a later rebalance. During the event window IEF
  holds the **seasoned 7–10-year ladder** (16 bonds) — off-the-run 10-year notes from
  the previous ~3 years, plus old long bonds that have aged into the bucket. The
  concession reaches IEF **only through curve-wide spillover**, which B.1 item 4
  documents as present and significant in exactly that sector, and which B.1's
  off-the-run result supports.
- **TLT does eventually hold the security being auctioned** — a new 30-year bond has
  30 years remaining, comfortably inside `> 20` — but it enters only at a subsequent
  rebalance, so it too is absent from the fund *during* the window. The rest of the
  20+ ladder is present, and a 30-year auction's pressure is concentrated in exactly
  that sector.
- **Both are baskets, so both attenuate.** On-the-run pressure is diluted across 16
  and 47 bonds. The *direction* of attenuation is known (towards zero); its *size* is
  not known, and measuring it is one of the two things this study does.
- **Index discontinuity 2016-03-31** (Barclays → ICE) for both funds. iShares states
  no significant change in exposure; it is nevertheless a declared structural break
  inside the sample.
- **The 20-year bond may never enter TLT at issue.** If the ICE rule is strictly
  `> 20 years`, a freshly issued 20-year bond is ineligible on day one. The sources
  reachable here (the iShares product page and the ICE index description) both say
  *greater than*, but neither is the index methodology document. **UNRESOLVED** — and
  a second, independent reason to keep the 20-year out of the primary (C.3).
- **Adjusted closes are total return.** IEF and TLT accrue coupon daily; the
  concession is a price effect. Over equal-length adjacent windows the accrual
  largely differences out (C.6), but it is not zero, and it is declared rather than
  assumed away.

---

## C. PROPOSED STUDY DESIGN

**Everything in this section is a proposal for S1. Nothing here is sealed, decided,
or established.**

### C.1 The primary research question

> Does the predeclared US Treasury coupon-auction cycle produce an **economically
> harvestable**, repeatable round-trip return pattern in a **liquid duration ETF**,
> measured close-to-close, that survives the programme's realistic transaction costs,
> and that is not carried by a single year or a single regime?

```
PRIMARY_CLAIM_TYPE = REDUCED_FORM
```

The claim is about **the auction cycle as it reaches a liquid duration ETF**. It is
not a claim about cash Treasuries, dealers, supply, or rates generally. Section F
states the boundary in full.

### C.2 Why a reduced-form claim, and why the disagreement is not resolved by choosing

Fable proposed a reduced-form ETF test; Astra argued that a dealer/intermediation
claim needs duration-weighted announced supply, point-in-time dealer inventories,
when-issued pricing and cash/futures data. **Both are right about different claims**,
and B.1 settles which claim this data can carry:

- SR 1188 obtains a **causal** supply reading only because it works **intraday**, in a
  six-hour window, on **interdealer quotes for the specific on-the-run security**, and
  validates it with an FOMC/payrolls placebo. None of those three conditions can be
  met with daily ETF closes.
- Therefore a daily ETF study **cannot** identify a dealer-capacity channel, and any
  attempt to do so would be overclaiming. The reduced-form question it *can* answer is
  worth answering on its own terms, because it is the question a CTA book actually
  faces: *is there money in this at ETF granularity, net of cost?*

The distinction is preserved explicitly and permanently:

```
REDUCED_FORM ETF EFFECT  !=  CAUSALLY IDENTIFIED DEALER-INTERMEDIATION EFFECT
```

### C.3 Instrument mapping and the 20-year

```
PRIMARY_INSTRUMENT_MAPPING
  30-year nominal Treasury bond auction  ->  TLT   (LINEAGE-PRIMARY cell)
  10-year nominal Treasury note auction  ->  IEF   (declared SECONDARY cell)
20Y_TREATMENT = EXCLUDED FROM THE PRIMARY AND FROM THE SECONDARY.
                Post-2020 descriptive only, and only if S1 resolves the index
                eligibility question in B.7.
```

**Why TLT is the lineage-primary and IEF the secondary** — a change from the discovery
prior, which treated the two symmetrically:

1. **Economic headroom.** The predeclared position path costs the same in both
   instruments (C.7) while TLT's duration is **14.98 y against IEF's 6.92 y**, and the
   cash-market price pressure is **17.1 bps at the 30-year against 9.9 bps at the
   10-year** (B.1). TLT is the only cell with a realistic chance of clearing a cost
   bar, so a TLT null nearly closes the lineage while an IEF null would not.
2. **The contamination that argues against TLT does not bite a reduced-form claim.**
   The 10-year auction moves the 30-year sector **more** than the 30-year auction does
   (1.294 vs 0.869 bps, B.1 item 4), and it falls in the same week. That makes the TLT
   estimate a **refunding-week** effect, not a 30-year-supply effect — which is
   exactly what a reduced-form claim asserts. It bars only the causal reading, which
   section F already forbids.
3. **IEF's cell is the cleaner identification but the weaker economics**, so it is
   retained as a declared secondary and reported with its own interval.

**Why the 20-year is excluded** — two independent reasons, either sufficient:

- Issuance was **suspended June 1986 → May 2020** (B.1 item 5). Within the panel it
  contributes only ~2020-05 → 2026-06, entirely inside the era in which the effect is
  documented to be weakest.
- It is **not established that a freshly issued 20-year bond is index-eligible for
  TLT at all** under a strict `> 20 years` rule (B.7). Anchoring a cell on an auction
  whose security may never enter the instrument is not defensible.

### C.4 Event definition and the event unit

```
PRIMARY_EVENT_UNIT = THE AUCTION WEEK (the ISO week containing t0)
t0                 = the AUCTION DATE of the instrument's mapped tenor,
                     taken from the official record, never inferred from prices
```

- **Reopenings and original issues are ONE family.** The mechanism — scheduled supply
  that must be absorbed — is identical. Reopening status is carried as a **declared
  descriptive split**, reported, never a gate and never a filter.
- **Consecutive 10-year and 30-year auctions are NOT two independent events.** They
  fall in the same mid-month week (B.6), and the 10-year spills into the long end
  (B.1). Inference clusters at the week, and above it at the year (C.8).
- **Is the event week scientifically appropriate as the independence unit?** For
  *within-month* dependence, yes, and it is if anything conservative. But it is **not
  sufficient on its own**: the dependence that actually matters is at the **year /
  regime** level (issuance size, QE/QT, the 2007–2014 vs 2015–2024 break that B.1
  documents). The uncertainty plan is therefore anchored on **years**, not weeks
  (C.8). Treating 220 event weeks as 220 independent experiments would be wrong, and
  C.9 states the three counts separately for exactly this reason.
- **Schedule anomalies.** Holidays, moved auctions and the 2001–2006 30-year gap are
  handled **mechanically from the official record**: an event exists if and only if
  the record contains an auction of the mapped tenor with a complete window inside the
  panel. No date is edited, inferred or interpolated.
- **Overlapping own-tenor events.** If two auctions of the same mapped tenor fall
  within 5 business days of each other, the event windows overlap. The predeclared
  rule: **keep both, and let the year-level resample carry the dependence.** No event
  is deleted.
- **Auction-day close.** The auction closes at 1:00 p.m. ET and results are public
  ~1:02 p.m., three hours before the 4:00 p.m. ETF close (B.6). The auction-day
  close-to-close bar therefore **nets the morning concession against the afternoon
  reversal**, and cannot be assigned to either leg. It is excluded from both windows
  by construction and reported as a declared descriptive quantity only.

### C.5 The event windows — one pair, fixed from the literature, no search

```
PRIMARY_PRE_WINDOW  = close(t0 − 6 business days)  ->  close(t0 − 1)
                      i.e. the cumulative log return over the 5 business days
                      ending on the last close strictly BEFORE the auction
PRIMARY_POST_WINDOW = close(t0)  ->  close(t0 + 5 business days)
                      i.e. the cumulative log return over the 5 business days
                      beginning at the auction-day close, which is AFTER results
AUCTION DAY t0      = its own close-to-close return belongs to NEITHER window
```

- **Why 5 business days.** It is the window for which Lou et al. print **per-maturity**
  results (B.2), and SR 1188 replicates the same daily-frequency family. It is the one
  window taken from the literature, and it is fixed before any outcome is computed.
- **Why not Lou's t = 10.** With one mapped auction per month, a ±10-business-day
  window covers essentially every trading day; Lou et al. say so themselves for the
  2-year. At t = 10 there is no calendar outside the event, so neither a control
  window nor a clean event definition survives. This is a **mechanical** reason, not
  an outcome-informed one.
- **Why the boundaries fall where they do.** They are forced by the intraday timing in
  B.6/B.1 item 3, not chosen: `close(t0−1)` is the last close entirely before the
  auction, and `close(t0)` is the first close entirely after results. Any other choice
  mixes the two legs inside one daily bar.
- **The declared cost of this.** The design **forfeits the 1:02 p.m.–4:00 p.m.
  reversal on auction day**, which B.1 shows is a material share of the post-auction
  move. The post leg is therefore **structurally attenuated** in this design. Declared
  now, before any outcome — not discovered afterwards.
- **Both instruments use the same relative-day definition**, each anchored on its own
  mapped auction date.

### C.6 The primary estimand and the control design

```
PRIMARY_ESTIMAND
  For the lineage-primary instrument TLT, and per event week i:

      AC_i  =  r_post,i  −  r_pre,i          (log total return, close-to-close)

  where r_pre and r_post are the two windows of C.5.

  The primary quantity is the MEAN of AC_i over all event weeks in the sample,
  reported with ONE 95 % interval (C.8), in basis points per event week.

  Predicted sign: AC > 0  (prices fall into the auction, recover after).

  The identical statistic is computed for the SECONDARY cell (IEF), and for the
  two placebos, and is reported alongside with no power to rescue the primary.
```

**Why this estimand, and why not "abnormal return versus matched control windows".**

1. **It is the literature's own primary statistic.** It is exactly SR 1188 equation
   (1) in return space — *post-auction return minus pre-auction return* — and exactly
   Lou et al.'s return-differential measure. Lou et al. state the reason plainly: it
   integrates both legs into one measure and raises the power to detect the effect.
2. **It is the tradable object.** `AC` is the gross P&L of the predeclared round trip:
   short duration through the pre window, flip long at the auction-day close, flat at
   `t0 + 5`. Nothing has to be reinterpreted to turn the measurement into a strategy.
3. **It is self-differencing.** The two windows are adjacent and of equal length, so
   any drift that is constant in the ±5-day neighbourhood of an auction — the term
   premium, the sample's bond bull market, the daily coupon accrual of an adjusted
   close — **cancels exactly**. That is a far weaker assumption than sample-wide
   constancy, and it removes the need to model a drift.
4. **Matched non-auction control windows are not implementable in this calendar, and
   the discovery prior is wrong on this point.** The mapped auctions sit in the
   mid-month week; the 2-, 5- and 7-year auctions sit at the end of the month; TIPS
   and (post-2020) the 20-year sit in between. A ±5-business-day placebo anchor
   therefore lands on some Treasury auction almost everywhere, and B.1 Table 4 shows
   5-year and 7-year auctions **do** produce significant pressure at 10 and 30 years
   (5Y → 10Y 0.736\*\*\*, 5Y → 30Y 0.562\*\*\*; 7Y → 10Y 0.490\*\*, 7Y → 30Y 0.353\*).
   There is no clean non-auction window to match to.
   *The month-position detail of the 2/5/7-year block is from general market knowledge
   and is **PROVISIONAL**; it must be established mechanically from the official
   record at S1. The conclusion does not depend on it: even the mid-month week alone
   contains three coupon auctions.*

```
CONTROL_DESIGN
  PRIMARY      = none. The self-differencing estimand needs no control window,
                 and no matched control window exists (point 4 above).
  PLACEBO 1    = SHY (1-3y Treasury ETF), same statistic, anchored on the 30-year
                 auction. Literature-predicted NULL: B.1 Table 4 shows 30-year
                 auctions produce no significant pressure at short maturities.
                 A material SHY effect falsifies the supply interpretation.
  PLACEBO 2    = SPY (equity), same statistic, both anchors. The mechanism predicts
                 nothing. A material SPY effect means the pattern is a generic
                 mid-month calendar artefact, not a duration/supply effect.
  Both placebos are DECLARED BEFORE OUTCOMES, have predicted nulls, and can only
  DAMAGE the primary reading — never rescue it.
```

**Raw, excess or abnormal?** The estimand is a **difference of two raw windows**,
which is why it needs no excess-return or abnormal-return construction: the risk-free
rate and any local drift difference out. An explicit duration control (a Treasury-market
return factor) is **deliberately not** in the primary — with two adjacent equal windows
it would mostly re-remove what the difference already removes, at the cost of a model
choice. It is available as a declared secondary only.

### C.7 Economic materiality — audit of the discovery rule, and the proposal

**The discovery rule was `effect ≥ 2 × round-trip ETF trading cost per event`. It is
retained as a floor but is NOT sufficient**, for three reasons:

1. `2 × cost` is a signal-to-cost ratio, not an economic quantity. It says nothing
   about whether the sleeve is worth capital.
2. **It ignores the risk taken.** A 5-day outright TLT position carries roughly a
   percent of standing volatility per leg. Clearing a cost bar by a few basis points
   twice a month is compatible with a Sharpe near zero — which is not an edge.
3. It is **not comparable to this programme's own precedents**: C-A uses a Sharpe
   floor of **+0.30** (Owner decision OD-1) and VRP used an annualised economic-usefulness
   margin. A bar with no risk dimension would be a step backwards.

```
ECONOMIC_MATERIALITY_RULE  (conjunctive; both parts fixed before any outcome)

  COST MODEL
    programme convention, 2 bps one-way, applied to the predeclared position path
    flat -> short (1 unit) -> flip to long (2 units) -> flat (1 unit)
      = 4 one-way units = 8 bps per instrument per event week.

  M1  COST CLEARANCE (necessary)
      mean NET AC  >=  +8 bps per event week
      equivalently mean GROSS AC >= +16 bps, i.e. the discovery rule's 2x cost.
      Source of the number: the programme's own 2 bps cost convention. NOT the
      literature.

  M2  RISK-ADJUSTED USEFULNESS (sufficient)
      annualised Sharpe of the net per-event-week P&L on a fixed notional
        =  mean(net AC) / sd(net AC) * sqrt(events per year)   >=  +0.30
      Source of the number: this programme's EXISTING materiality floor for
      "economically material", Aaron's C-A Owner decision OD-1. NOT the literature.

  CLASSIFICATION uses the 95 % INTERVAL against these bars, never the point
  estimate. Endpoints classify.
```

Neither number is reverse-engineered from a literature effect size. Both come from
decisions this programme has already taken.

```
OWNER DECISION REQUIRED AT S1
  Confirm or replace M2 = +0.30. Setting a materiality threshold is a material
  methodology decision (vNext section 10) and is not self-authorised here.
  M1 = 8 bps net follows mechanically from the 2 bps convention and needs
  confirmation only if the cost convention itself is revisited.
```

**Power note — a feasibility statement, NOT a threshold.** Having fixed M1 and M2
independently, it is honest to record where the literature's cash-market magnitudes
sit relative to them. SR 1188's six-hour 30-year price pressure is 17.1 bps full
sample and 14.2 bps in 2015–2024, and the multi-day daily effect is roughly four times
the six-hour effect in yield terms — while the ETF basket attenuates by an unknown
factor and the design forfeits the auction-day afternoon. **The plausible ETF-level
effect therefore straddles the 16 bps gross bar rather than sitting clearly above or
below it.** That makes this a genuine two-sided experiment, and it makes a Class-3
low-power outcome a realistic result rather than a failure of the design. It does not
move either bar.

### C.8 Uncertainty and multiplicity

```
UNCERTAINTY_PLAN  (the smallest set that answers the claim)
  1. ONE 95 % interval: block bootstrap resampling CALENDAR YEARS with
     replacement, 10,000 replicates, percentile interval.
     Years, not weeks, because the dependence that matters is regime-level
     (issuance size, QE/QT, the documented 2015+ attenuation), and a year-level
     resample subsumes within-week and within-month clustering.
     Reuses the programme's existing stationary/block bootstrap machinery
     (C-A OD-5, VRP), so nothing new is built.
  2. LEAVE-ONE-YEAR-OUT JACKKNIFE, reported and RANKED ABOVE significance.
     Its purpose is fragility, not inference: if dropping one year removes the
     result, the result is one year.

  DELIBERATELY NOT STACKED: HAC/Newey-West (redundant with a year-level
  resample at this frequency), separate event-week clustering (subsumed),
  and every additional robustness variant. Stacking methods is not rigour.
```

```
MULTIPLICITY_PLAN
  The primary family has ONE cell: TLT. m = 1. No correction is required and
  none is applied, because NO SELECTION ACROSS CELLS OCCURS: the lineage verdict
  is read off the TLT cell, designated in advance.

  IEF is a DECLARED SECONDARY with its own interval and its own classification.
  It has NO power to rescue a TLT failure, and "IEF passed" is never the claim.

  The four-cell family {IEF, TLT} x {PRE, POST} suggested at discovery is NOT
  retained, for two reasons:
    (a) the primary estimand already combines the two legs, which is what the
        literature does and what the tradable object is;
    (b) the literature prior for the POST leg in LONG duration is absent or
        reversed in the modern era (B.3; B.1 30-year dY(post) = -0.235 n.s.).
        Declaring a primary cell with a predicted sign the literature does not
        support would be manufacturing a hypothesis.
  The four leg-level quantities ARE computed and reported as a DECLARED
  DECOMPOSITION of the primary, with PROMOTION_POWER = NONE. Reporting a
  decomposition is not testing four hypotheses.
```

### C.9 Sample size — three different counts, never one

Estimated **mechanically from schedule metadata and panel coverage**, with no ETF
event return computed. Ranges, because the pre-2009 frequency is unverified (B.6).

```
EXPECTED_RAW_AUCTION_COUNT
  10-year notes, 2002-08 -> 2026-06 (IEF coverage, 23.9 years)
      ~261 if 8/yr through 2008 and 12/yr thereafter
      ~287 if 12/yr throughout
      => ~260-287
  30-year bonds, first post-gap auction 2006-02 -> 2026-06 (20.4 years)
      ~220 if quarterly 2006-2008 and 12/yr thereafter
      ~245 if 12/yr throughout
      => ~210-245
  TOTAL mapped auctions in scope ~ 470-530.
  Fable's "~290 and ~245" is the upper end of both and assumes monthly
  throughout; it is an OVERCOUNT unless S1 shows otherwise.

EXPECTED_EFFECTIVE_EVENT_COUNT  (independent event weeks)
  LINEAGE-PRIMARY cell (TLT, 30-year anchored):  ~210-245 event weeks
  SECONDARY cell (IEF, 10-year anchored):        ~260-287 event weeks
  UNION of distinct auction weeks:               ~260-287, of which ~210-245
                                                 carry both instruments
  The two cells are NOT independent of each other: they share the week.

CAUSAL_MECHANISM_EFFECTIVE_N  (what a dealer-capacity claim would actually have)
  ~3 regulatory/market eras   (SR 1188's own S1/S2/S3 partition)
  ~20-30 independent dealer-inventory swings 2001-2026 (Fable F2, ADVISORY,
        not independently verified here)
  ~5 funding-stress episodes  (2008, 2011, 2019-09, 2020-03, 2023-03)
  => ORDER 3 TO 30. One to two orders of magnitude below the event count.
  This is Astra's point and it is accepted in full.

YEAR-LEVEL RESAMPLE UNITS = ~20 (TLT) / ~24 (IEF) calendar years.
  This, not the event count, is what the interval width will reflect.
```

### C.10 Calendar confounds

SR 1188 states the problem directly: at daily frequency, CPI, payrolls and GDP
releases *"produce yield movements that are difficult to disentangle from
auction-driven dynamics"* — which is why the authors went intraday. A daily ETF study
**cannot** disentangle them. The response is to declare the treatment in advance and
never to delete events.

| confound | when | treatment | why |
|---|---|---|---|
| **CPI** | ~10th–15th, 8:30 a.m. ET | **COVARIATE**, declared secondary only | lands squarely inside the mid-month auction week; the highest-risk confound |
| **Payrolls** | first Friday, 8:30 a.m. ET | **COVARIATE**, declared secondary only | usually week 1, so usually inside the pre window |
| **FOMC** | 8 per year, 2:00 p.m. ET | **COVARIATE**, declared secondary only | sometimes in the auction week; the 2:00 p.m. statement lands after the auction close on those days |
| **Quarterly Refunding Announcement** | Feb/May/Aug/Nov, the Wednesday before the refunding auctions | **COVARIATE**, declared secondary only, and reported separately | **the confound the discovery map missed.** The QRA is itself a supply-*news* event; its price effect is information, not absorption, and it sits inside the pre window four times a year |
| **Other Treasury auctions in the window** | 2/5/7-year, TIPS, 20-year | **STRUCTURAL — neither covariate nor exclusion** | they are part of "the auction cycle as it reaches a duration ETF" under a reduced-form claim. They are what bars the tenor-specific causal reading (section F), and they are why no clean control window exists (C.6) |

```
RULE, FIXED BEFORE OUTCOMES
  The PRIMARY estimand is the UNCONDITIONAL mean of AC over all event weeks.
  No scheduled macro event ever deletes an event, shortens a window, or moves a
  boundary. Covariate-adjusted versions exist as ONE declared secondary
  specification with PROMOTION_POWER = NONE.
  NO AD-HOC EVENT DELETION RULE MAY BE CREATED AT ANY LATER STAGE.
```

The covariate specification is declared secondary rather than primary deliberately:
putting covariates in the primary would introduce a model choice (which covariates,
which functional form) that an outcome could later be used to adjudicate. That is the
degree of freedom this design exists to close.

### C.11 The cheap falsification gate

```
CHEAP_FALSIFICATION_GATE
  ONE governed historical run. No strategy, no optimiser, no sweep, no weights.

  INPUTS
    - the official auction record, fetched once and pinned by sha256
      (a separate Owner data decision, not taken here)
    - the existing frozen ETF panel, declared reuse under KB-1

  COMPUTE, exactly once
    1. mean AC and its 95 % year-block-bootstrap interval, for TLT (primary)
    2. the same for IEF (declared secondary)
    3. the same for SHY and SPY (declared placebos, predicted null)
    4. leave-one-year-out jackknife for 1 and 2
    5. the declared decomposition: the four leg means, plus the auction-day
       close-to-close mean, plus the reopening/original split
       -- all PROMOTION_POWER = NONE

  DECIDE, by the sealed rule, on the INTERVAL
    See C.12. Endpoints classify; the point estimate never does.

  KILL CONDITIONS (any one closes the lineage)
    - the TLT interval lies wholly BELOW the M1 net-cost bar
    - the sign is wrong (interval wholly below zero)
    - the result does not survive leave-one-year-out
    - a placebo shows a material effect of the same size
```

### C.12 Negative-outcome classification — four distinct outcomes, never collapsed

```
NEGATIVE_OUTCOME_CLASSIFICATION

  CLASS A -- MECHANISM ABSENT AT THIS GRANULARITY
    The TLT interval is wholly below zero, or spans zero tightly enough to
    exclude any useful effect, AND the placebos are null.
    Reading: no auction-cycle pattern reaches a liquid duration ETF at daily
    close-to-close frequency. Says NOTHING about the cash market, which B.1
    documents intraday with a causal design.
    KB status: not_promoted.

  CLASS B -- MECHANISM PLAUSIBLY PRESENT, NOT HARVESTABLE THROUGH THE ETF
    The sign is right and the interval excludes zero, but the interval lies
    wholly BELOW the M1 cost bar (or clears M1 and fails M2 decisively).
    Reading: the ETF basket, the close-to-close constraint and the forfeited
    auction-day afternoon attenuate a real effect below harvestability.
    This is a DIFFERENT and MORE INFORMATIVE result than Class A, and it is the
    one the design is most likely to produce.
    KB status: not_promoted, with the measured attenuation recorded.

  CLASS C -- LOW POWER / UNRESOLVED
    The interval SPANS a materiality bar. The study establishes neither that the
    effect clears the bar nor that it fails to.
    This is a TERMINAL result, exactly as VRP Stage A was. It is not an
    invitation to retune, extend the sample, change the window or add a filter.
    KB status: unresolved.

  CLASS D -- USEFUL ETF-LEVEL EFFECT SUPPORTED
    The interval lies wholly ABOVE M1 and the Sharpe interval clears M2, and the
    result survives leave-one-year-out, and the placebos are null.
    Reading: a reduced-form, cost-surviving auction-cycle effect exists in TLT on
    an EXPOSED panel. Ceiling: `supported`. Never `confirmed`, never
    `independently confirmed` (A.3).

  TARGET-MARGIN EXCLUDED is the boundary between B and C and is read off the
  INTERVAL ENDPOINTS, never the point estimate.
  "Failed" is not a class and is not a permitted verdict word.
```

**Items carried to S1** (recorded here, decided there): pin the auction frequency and
the 2/5/7-year calendar mechanically from the official record; resolve the ICE 20+
index eligibility question; confirm M2; write the Fable and Astra design-exposure rows
into `ops/REVIEWER_EXPOSURE_LOG.md`; declare the hypothesis family in
`TRIAL_LEDGER.md` §6.2 **before any member runs**; record the KB-1 reuse in
`SAMPLE_REUSE.md`.

### C.13 Data decision

```
OFFICIAL_AUCTION_DATA_SOURCE
  U.S. Treasury Fiscal Data -- "Treasury Securities Auctions Data"
  https://fiscaldata.treasury.gov/datasets/treasury-securities-auctions-data/
  API base https://api.fiscaldata.treasury.gov/services/api/fiscal_service/
  Cross-check source: TreasuryDirect auction announcements / results.

DATA_SOURCE_ACCEPTABLE = YES

  Because, verified in B.6:
    - it is the ISSUER's own record -- primary authority, not a vendor;
    - coverage 1979-11-15 -> 2026-09-30 covers the panel with 23 years to spare;
    - announcement date, auction date and issue date are distinguishable, which
      is what makes t0 point-in-time by construction;
    - 114 fields, including the security identifiers and terms the design needs;
    - the API is open, free, documented, filterable and paginated -- the records
      are plainly downloadable;
    - auction dates and announced sizes are PUBLIC IN ADVANCE and are not
      revised: the anchor cannot be contaminated by hindsight.

  RESIDUALS, all S1 items, none blocking:
    - "Released As Needed" is not a stated revision policy. The mitigation is
      mechanical, not editorial: fetch once, pin by sha256, and record the
      fetch timestamp. Nothing downstream re-reads a live endpoint.
    - The presence of the reopening indicator, the offering amount and the
      bidder-class allotment fields was NOT confirmed field-by-field, because
      confirming it means calling the endpoint and this task may not fetch. They
      are documented as part of the dataset; the primary design needs only
      security term, auction date and reopening status, and the first two are
      confirmed by name. If the reopening flag turns out to be absent it can be
      derived from CUSIP repetition -- an S1 mechanical question, not a risk to
      the frame.

DATA_FETCHED = NO.  No Owner data grant is requested or implied by this document.
```

### C.14 Portfolio role — framing only, no test

```
HYPOTHETICAL ROLE = scheduled standalone premium / possible TSMOM complement
NOT               = crisis diversifier. Never described as one.

EXPECTED CONDITIONAL RISK, recorded now
  The pre-auction leg is SHORT DURATION. In a flight-to-quality week -- 2008-Q4,
  2011-08, 2020-03 -- yields collapse into the auction and that leg loses
  sharply. The sleeve is therefore expected to be NEGATIVELY exposed to exactly
  the states in which the canonical book earns its keep.

CONSEQUENCE FOR ANY FUTURE PORTFOLIO TEST
  Unconditional correlation is NOT sufficient evidence of complementarity. Any
  future relevance test MUST examine the programme's declared crisis and tail
  windows, because that is precisely how VRP looked good unconditionally and bad
  where it mattered (handoff section 9, question 6).
  NO PORTFOLIO TEST IS PERFORMED OR AUTHORISED HERE.
```

### C.15 Distinctness

```
DISTINCT_FROM_YIELD_CURVE  = YES
  The closed overlay gated the canonical book on the LEVEL of the curve slope.
  This takes no view on level, slope or direction, is flat outside a few days a
  month, and is driven by an exogenous issuance calendar.

DISTINCT_FROM_CARRY        = YES
  Carry harvests roll-down and term premium from a HELD position. This harvests a
  TRANSIENT absorption concession over <= 5 days whose sign reverses inside the
  same cycle. Opposite holding period, opposite sign structure, different payer.

DISTINCT_FROM_SEASONALITY  = YES, with a declared caveat.
  The anchor is an ANNOUNCED, DATED, EXOGENOUS supply event with a published
  mechanism, an independent official record, and intraday causal evidence -- not
  a calendar regularity found in prices.
  THE CAVEAT: because the auction calendar is itself near-monthly and mid-month,
  the estimand is PARTIALLY CONFOUNDED with a generic mid-month calendar effect
  at daily frequency. That is exactly what PLACEBO 2 (SPY) is declared to detect,
  and the closed seasonality study's bond turn-of-month cell (0/18) is a prior
  against such an artefact. The caveat is stated, not assumed away.

DISTINCT FROM MACRO REGIME GATING = YES. No macro state variable enters the
  primary. Macro releases appear only as declared covariates in a secondary.
```

---

## D. NOT-YET-TESTED CLAIMS

Everything below is **unmeasured in this programme**. None may be cited as a fact.

1. That any auction-cycle effect reaches IEF or TLT **at all** at daily close-to-close
   frequency. Unmeasured.
2. The **size** of the ETF-basket attenuation relative to the cash on-the-run
   magnitudes in B.1. Unmeasured — and it is one of the two things the study measures.
3. That the effect, if present, **survives 2 bps one-way costs**. Unmeasured.
4. That the effect is **stable across years or across the documented 2015+ regime
   break**. Unmeasured, and B.1 gives a positive reason to doubt it.
5. That the post leg exists at all in the modern era for long duration. B.3 is a
   primary-source prior **against** it.
6. That the TLT result, if any, is attributable to **30-year supply**. It cannot be —
   the 10-year auction in the same week moves the long end more (B.1 item 4).
7. That any of this is **complementary to canonical TSMOM**, or improves the book, or
   behaves acceptably in crisis. No portfolio quantity is computed here or authorised.
8. That the **dealer-capacity channel** operates at ETF granularity. Parked (E.1).
9. That the local ETF panel's IEF/TLT series are **free of the C-D cross-vendor
   residual**. D-S5 touched XLE, XLU, RWX, DBA, HYG and VNQ — not IEF or TLT — but
   that is an absence of a recorded finding, **not** a positive verification of those
   two series. An S1 data-integrity item.
10. The **historical auction frequency** before 2009, and therefore the exact event
    count. Unverified (B.6); ranges only.

---

## E. SECONDARY / PARKED QUESTIONS

### E.1 The dealer-inventory mechanism cell

```
SECONDARY_DEALER_CELL = PARK
```

Assessed against the four criteria asked for:

| criterion | assessment |
|---|---|
| **scientifically interpretable?** | Partly. The sign is fixed by theory (higher dealer inventory → larger concession), which is good. But SR 1188 reports that **traditional dealer-constraint proxies have declining explanatory power** in recent years and that non-dealers now absorb the supply; Amin & Tedongap find **non-dealer** behaviour drives the TIPS pattern. A null would be genuinely ambiguous. |
| **historically reconstructible?** | Only with work. NY Fed primary-dealer statistics start 1998-01-28 and are **split into periods by reporting-structure changes** (B.6). Bridging maturity-bucket redefinitions across those breaks is itself a methodology decision — an Owner gate, not a build step. |
| **compatible across reporting breaks?** | **Not established.** This is the binding objection. |
| **sufficiently powered?** | **No.** `CAUSAL_MECHANISM_EFFECTIVE_N` is order 3–30 (C.9), against ~210–245 event weeks for the reduced-form cell. A conditioning contrast on ~20–30 independent inventory swings has very little power. |

**Decision: PARK.** A reduced-form ETF result must be classifiable **without** any
dealer evidence, and under C.12 it is. Adding this cell would buy a second data
acquisition, a bridging decision and a second family member, and would buy no
additional ability to close the lineage.

**Un-park conditions** (all three, and an Owner decision): the reduced-form primary
returns Class D; Aaron wants the mechanism established rather than the effect
harvested; and the bridging rule for the NY Fed series breaks is fixed in advance of
seeing any conditioned outcome.

### E.2 Other parked directions

Recorded so they are not silently lost, and so none is mistaken for scope.

- **Futures implementation (ZN / ZB).** The natural instrument for an outright
  duration bet with leverage, and it would remove the ETF-basket attenuation entirely.
  **Not in scope**, requires a Databento purchase beyond the current grant, and is a
  separate lineage.
- **Cash / when-issued identification.** What Astra's stronger claim would actually
  need. Out of scope for the reduced-form question, and a different research object.
- **Auction outcome surprise** (tail, bid-to-cover, dealer take-down) as a predictor of
  the post window — Fable's F1.d. **Parked.** It would split the post leg into
  distribution versus news, but the post leg is the weaker leg (B.3), so splitting it
  first is the wrong order of work.
- **Concession conditional on offered size** — Fable's F1.b. **Parked** for the same
  reason plus one more: announced size trends monotonically upward across the sample,
  so a size effect and an era effect are nearly collinear. It is a secondary at best,
  and never a primary.
- **The 20-year cell, post-2020.** Descriptive only, and only if B.7's index
  eligibility question resolves in its favour.
- **Euro-area / Italian / Brazilian replication.** Genuine external validity, no data,
  a different lineage.

---

## F. FORBIDDEN INTERPRETATIONS

Binding on every later document, seat and stage in this lineage.

1. **A result here is NEVER evidence that primary-dealer balance-sheet constraints
   cause it.** Daily ETF closes cannot identify that channel; SR 1188 needed intraday
   interdealer quotes and an order-flow decomposition to claim it.
2. **A result here is NEVER a claim about cash Treasuries.** The object is a liquid
   duration ETF, and the claim must always be worded *"the auction-cycle premium as it
   reaches a duration ETF"*.
3. **A TLT result is NEVER attributable to 30-year supply specifically.** The 10-year
   auction sits in the same week and moves the long end more (B.1 item 4). Any TLT
   effect is a **refunding-week** effect.
4. **A null is NEVER "the auction cycle does not exist".** B.1 establishes it intraday
   with a causal design. A null here is Class A or Class B of C.12, and the difference
   between them must be stated.
5. **A result here is NEVER evidence about auction supply and Treasury expected
   returns generally**, nor about term premia, nor about issuance policy.
6. **This is NEVER crisis diversification** and must never be described as such. The
   expected conditional risk runs the other way (C.14).
7. **This NEVER improves canonical TSMOM** unless a separately authorised portfolio
   test says so on the declared crisis and tail windows — and no such test exists or is
   authorised.
8. **No result may authorise changing** the window, the anchor, the mapped tenor, the
   instrument, the cost convention, the materiality bars, the sample endpoints, the
   event definition or the placebo set. Each would be a **new lineage** with its own
   trial accounting. This is the VRP §O discipline, carried forward deliberately.
9. **No outcome may be used to choose anything.** Windows, tenors, entry and exit days,
   thresholds and controls are fixed in this document from mechanism, official
   mechanics and literature, before any outcome exists.
10. **The evidence ceiling is `supported`.** The ETF panel is exposed (KB-1).
    `confirmed` and `independently confirmed` are unreachable for this lineage on this
    panel, whatever the result.
11. **Fable and Astra are design-exposed** (A.4) and may never be presented as the sole
    blind independent certifier of this design or of any result under it.
12. **"Failed" is not a verdict.** The permitted outcomes are Class A, B, C or D of
    C.12, mapped to `not_promoted` / `unresolved` / `supported`.

---

## Appendix — primary sources read

| # | source | how read |
|---|---|---|
| 1 | Fleming, Liu & Nguyen, *Intraday Price Pressure and Order Flow Around U.S. Treasury Auctions*, FRBNY Staff Report 1188, Mar 2026 rev. Jul 2026 | full PDF, text-extracted; Tables 2, 3, 4 and §§1–4 read directly |
| 2 | Lou, Yan & Zhang, *Anticipated and Repeated Shocks in Liquid Markets*, RFS 26(8) 1891–1912, 2013 | full PDF, text-extracted; §§I–III read directly |
| 3 | Somogyi, Wallen & Xu, *What Treasury Auctions Reveal About Investor Demand*, HBS WP 26-033, 2 Dec 2025 | PDF, abstract and front matter text-extracted |
| 4 | U.S. Treasury Fiscal Data — *Treasury Securities Auctions Data* dataset page and API documentation | fetched |
| 5 | TreasuryDirect — *General Auction Timing*; auction-results pages | fetched |
| 6 | Federal Reserve Bank of New York — *Primary Dealer Statistics*; OFR Short-Term Funding Monitor dataset page | fetched |
| 7 | iShares — IEF and TLT product pages; ICE US Treasury 7-10 Year and 20+ Year index descriptions | fetched |

**Not read at primary source, and therefore not load-bearing:** Beetsma et al. (2016,
2018); Sigaux (2024); Albuquerque et al. (2024); Amin & Tedongap (2023); Andrade & Da
Rocha (2024); Fleming et al. (2024). Each is recorded above only as cited within
source 1.

```
END OF S0 FRAME. NO SEAL. NO BUILD. NO FETCH. NO RUN.
```
