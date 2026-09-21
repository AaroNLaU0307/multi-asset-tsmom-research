# CTA-EDGE-02-BENB — PREREGISTRATION CONTRACT (S1 DESIGN)

```
LINEAGE                = CTA-EDGE-02-BENB
CONTRACT_ID            = CTA-EDGE-02-BENB-PREREG-01
CANDIDATE              = BOND_ETF_NAV_BASIS
PRIMARY_CLAIM_TYPE     = REDUCED-FORM PREDICTIVE / MARKET-STRUCTURE CLAIM
LANE                   = FULL
STATUS                 = SEALED
WORKFLOW_AUTHORITY     = ../../../QUANT_WORKFLOW_VNEXT.md  (vNext, cutover 2026-09-12)
CREATED                = 2026-09-15
AUTHOR                 = Claude Opus 5 (Main Agent / builder seat)
S1_SEAL_CREATED            = YES
S2_AUTHORIZED              = NO
RUN_AUTHORIZATION_CREATED  = NO
HISTORICAL_BASIS_COMPUTED  = NO
DISCOUNT_SIGN_COUNT_COMPUTED = NO
REGRESSION_RUN             = NO
BACKTEST_RUN               = NO
```

> **Every section below is final and binding on S2.** The one value this document
> previously left open — `M2` and its boundary operator — was taken by the Owner as
> **BENB-OD-1** on 2026-09-15, before any outcome existed, and is now sealed in §H.3.
> §Z records how that decision was reached and what it deliberately does not inherit.

---

## §0 Authority and provenance

This document is the **sole design authority** for `CTA-EDGE-02-BENB` once sealed.
Until it is sealed it is a proposal.

```
S0 FRAME         research/extensions/benb/BENB_S0_FRAME.md
                 sha256 5dabf6fc8af3b1c7455db72b468537428b9ca11d0188c68481e5c96b97a03b73
                 PRESERVED BYTE-FOR-BYTE. Accepted direction; superseded where the
                 repair record says so. Never design authority on a superseded point.
S0 REPAIR        research/extensions/benb/BENB_S0_REPAIR_RECORD.md
                 sha256 a4d81db3cc159f193a6aafdb3b5e5a263d138b3e307a1f7c54b1def456d0898b
                 Resolved the data footing, the timing, the decomposition, the
                 discount-only sample and the ex-date rule. Binding.
OWNER DECISION   ops/OWNER_DECISION_RECORD_CTA_EDGE_02_BENB.md
                 BENB-OD-1: the M2 floor, its metric, its monthly construction and its
                 STRICT boundary operator. Binding.
```

**Standing programme facts, unchanged by this contract.** Canonical TSMOM remains
`SUPPORTED — NOT INDEPENDENTLY CONFIRMED` and FROZEN. C-A remains sealed and LIVE under
passive monthly accrual, **not accessed**. C-D remains at `HOLD`. TSMOM-VRP-01,
Time-Series Value, X01 and XSMOM remain CLOSED. **CTA-EDGE-01-TA is CLOSED PRE-OUTCOME**
and is not reopened. The knowledge-base repository is not modified.

---

## §A The research object — LOCKED

```
PRIMARY_ETF        = HYG   (iShares iBoxx $ High Yield Corporate Bond ETF)
SECONDARY_ETF      = LQD   (iShares iBoxx $ Investment Grade Corporate Bond ETF)
                     DECLARED SECONDARY REPLICATION · NO RESCUE POWER
PRIMARY_INFORMATION_SOURCE = RAW ETF MARKET PRICE + OFFICIAL ISSUER NAV

GATE 1 (identification):
  After an ex-ante abnormal DISCOUNT of HYG to its official issuer NAV, is there
  positive predictive information about the ETF price move that a trader acting on
  that NAV could actually capture -- the next session's OPEN-to-CLOSE return?

GATE 2 (economic usefulness), conditional on Gate 1:
  Does the fixed-unit implementation of that signal produce a return that survives a
  predeclared round-trip cost, and reach the programme's risk-adjusted floor?
```

The study does **not** claim, and no result may be read as claiming: that AP constraints
cause returns; that dealer balance sheets cause the effect; that HYG discounts are
mispricing by definition; that NAV is always stale; crisis alpha; or any improvement to
canonical TSMOM. §K is binding.

---

## §B Point-in-time information rule — LOCKED

```
SIGNAL_AVAILABILITY_ASSUMPTION
  Official NAV_t becomes INSTITUTIONALLY AVAILABLE after close(t) and before open(t+1).

PUBLIC_WEBSITE_SAME_EVENING_TIMESTAMP = NOT ESTABLISHED
EARLIEST_PERMITTED_EXECUTION          = open(t+1)
```

Evidence, each quoted rather than inferred (full detail: S0 repair §1.3):

- **iShares, own product page:** *"The NAV of funds normally is calculated using prices
  as of 4:00 p.m. eastern time. Each fund normally trades on its respective stock
  exchange until 4:00 p.m. eastern time."* ⇒ `NAV_t` is computed **from** the 16:00 ET
  close and therefore **cannot exist before it**.
- **DTCC ETF processing timeline:** *"Pricing is available at approximately 6:30 PM"* on
  the trade date.
- **SEC Rule 6c-11** (per SEC staff ADI 2025-15): the ETF website must carry NAV, market
  price and premium/discount *"each as of the end of the **prior business day**"*.

```
NO SAME-CLOSE EXECUTION.
NO OVERNIGHT RETURN MAY EVER BE CREDITED TO THE STRATEGY.
Any implementation that assumes knowledge of NAV_t at close(t) is INVALID and must
fail its tests.
```

The exact public-website minute is **not** established, and this contract does not
pretend otherwise: it relies only on the weaker, well-evidenced claim that the value is
institutionally disseminated in the evening of day *t*, which is sufficient for an
`open(t+1)` entry and insufficient for anything earlier.

---

## §C Data footing — LOCKED and PINNED

```
RAW PRICE  yfinance Ticker(<TICK>).history(period="max", auto_adjust=False, actions=True)
           Verified UNADJUSTED: Close differs from Adj Close on 4,879 of 4,888 HYG rows
           and 6,061 of 6,070 LQD rows, equal on the final row. ZERO splits in either
           fund's entire history, so raw close and split-adjusted close coincide.
NAV        iShares / BlackRock "Data Download" workbook, worksheet "Historical":
           As Of | NAV per Share | Ex-Dividends | Shares Outstanding
           https://www.blackrock.com/varnish-api/blk-one01-product-data/product-data/
           api/v1/get-fund-document?appType=PRODUCT_PAGE&appSubType=ISHARES&
           targetSite=us-ishares&locale=en_US&portfolioId={239565 HYG|239566 LQD}&
           component=fundDownload
RETRIEVED  2026-09-14 (price 18:25:57Z; NAV same session)
```

| pinned file (`data/benb/`, git-ignored under the blanket `data/` policy) | bytes | sha256 |
|---|---:|---|
| `ishares_HYG_fund_download.xml` | 4,675,317 | `10dcd91e095a56d83762019738aa5b14374ea5d1f723616636b52170150ec533` |
| `ishares_LQD_fund_download.xml` | 8,845,823 | `d0cc3b0121806b20a227b00ae50d3f8523e6cc560e7bae16d715824b50ce0a47` |
| `HYG_raw_ohlc.csv` | 648,827 | `1ed30697cd0c665d9abe3d60abfe8c03314fb8889f3a459df207c5b85cb3bce8` |
| `LQD_raw_ohlc.csv` | 824,802 | `9d120233fd18bbd28188c18ce5a99b8347416f58b903d7452b83b47d011fe036` |
| `HYG_nav_daily.csv` (pass-through) | 155,726 | `7735da958ef10522e39c9138b8cf8c686206585f3b805c327588fb61e9eae5de` |
| `LQD_nav_daily.csv` (pass-through) | 198,877 | `3d78dbd80b92e9715eb9f6249597d65556d12b6517aad6832640e7296698007a` |
| `benb_price_meta.json` | 695 | `8179c06f8f8dd088d3b08cb9b4d6a1a8abbd210239f3e2b226e70de223d8b339` |

```
NAV_PROVENANCE = RECONSTRUCTED_HISTORICAL_SERIES_WITH_NON-VINTAGE_LIMITATION
                 One retrieved vintage. Restatement by the issuer cannot be excluded.
                 No positive result may ever be described as strict vintage-PIT
                 confirmation.
EVIDENCE_CEILING = supported.  NEVER confirmed. NEVER independently confirmed.
RE-FETCH         FORBIDDEN after seal unless a separate repair is authorised. Nothing
                 downstream may read a live endpoint.
```

---

## §D Definitions — LOCKED

### D.1 Basis

```
b_t = ln( P_close,t / NAV_t )
  P_close,t = RAW UNADJUSTED regular-session closing market price of the ETF on day t
  NAV_t     = official issuer per-share NAV for day t
  b_t < 0 => DISCOUNT       b_t > 0 => PREMIUM
```

Both legs are raw per-share values of the same object struck at the same 16:00 ET
instant. **An adjusted close may not appear anywhere in the basis, in any component, or
in any diagnostic.**

### D.2 Eligible dates

A date `t` is eligible if and only if all hold:

1. `t` is in the intersection of the NAV date set and the price date set for that fund
   (this removes pre-listing NAV days, issuer NAVs struck on non-trading days such as
   HYG's 2024-03-29 and 2024-03-31, and the NAV file's vintage lag);
2. `t+1` — the next date in that same intersection — exists;
3. at least **250** prior intersection observations of `b_s` exist (§D.3);
4. `t+1` is **not** an ex-date (§D.4).

```
Structural eligibility from S0, recomputed and unchanged:
  HYG  common 4,887 -> post-burn-in with next day 4,636 -> ELIGIBLE 4,415
       (2008-04-08 .. 2026-09-10, 19 calendar years; 221 removed by the ex-date rule)
  LQD  common 6,069 -> 5,818 -> ELIGIBLE 5,539
       (2003-07-28 .. 2026-09-10, 24 calendar years; 279 removed)
```

### D.3 Abnormal basis

```
m_t = MEDIAN{ b_s : s < t, s eligible under D.2 conditions 1 }   -- EXPANDING
x_t = b_t - m_t
MINIMUM PRIOR HISTORY = 250 observations. Below that, x_t does not exist and the
                        observation is EXCLUDED - never imputed, never back-filled.
UPDATE TIMING         = b_t is knowable in the evening of day t; m_t uses data strictly
                        before t; therefore x_t is knowable in the evening of day t.
```

```
NO rolling window. NO window search. NO z-score. NO percentile normalisation.
NO alternate normalisation of any kind.
```

*Expanding, because it has no window length and therefore nothing to search over.
Median, because the object of study is the tail and a mean norm would be dragged by the
very episodes the study is about.*

**Declared limitation:** the norm drifts as the sample grows and early observations are
normed against a shorter history than late ones. Stated before outcomes; not to be
"fixed" later.

### D.4 Ex-date rule

```
EXCLUDE observation t whenever t+1 is an ex-date, where the EX-DATE FAMILY is the UNION of
   (i)  the issuer's `Ex-Dividends` column, and
   (ii) the raw-price source's `Dividends` column.
Observation t is NOT excluded for being an ex-date itself: b_t is well defined on an
ex-date because both legs are struck ex.
```

Verified mechanics (S0 repair §5.1): the two calendars agree on **232 of 233** HYG dates
and **288 of 289** LQD dates; **neither fund has ever made a capital-gain distribution**
(0 rows in both). The union is used because it is the more conservative of two pinned,
independent calendars.

*Why the rule exists: on an ex-date the NAV falls by the distribution and the price gaps
down at the open. `R_TRADABLE` (open→close on t+1) is structurally immune, but `R_NAV`
and `R_OVERNIGHT` both carry the mechanical drop and their coefficients would be biased.
Excluding the transition preserves the §E.1 identity exactly on every retained
observation, at a cost of about 5 % of the sample.*

**No outcome around a distribution may ever be inspected to revise this rule.**

### D.5 Primary sample

```
PRIMARY_SAMPLE = eligible observations with x_t < 0 ONLY
DISCOUNT_SEVERITY  d_t = -x_t  > 0,  CONTINUOUS
```

```
There is NO additional discount threshold. No 1 %, no 50 bps, no percentile, no decile,
no extreme-event cutoff, ever.
PREMIUM observations (x_t >= 0): DESCRIPTIVE_ONLY · PROMOTION_POWER = NONE ·
RESCUE_POWER = NONE. They may never contribute to primary support and never enter §F.
```

---

## §E The estimands and the trade — LOCKED

### E.1 The exact decomposition

For each eligible discount observation:

```
R_OVERNIGHT,t+1 = ln( P_open,t+1  / P_close,t  )
R_TRADABLE,t+1  = ln( P_close,t+1 / P_open,t+1 )
R_NAV,t+1       = ln( NAV_t+1     / NAV_t      )

IDENTITY   delta_b(t -> t+1)  ==  R_OVERNIGHT + R_TRADABLE - R_NAV
```

Exact for any positive prices and NAVs — no approximation, no error term. Verified on
200,000 synthetic random draws at S0 repair: max residual `1.776e-15`.

```
R_OVERNIGHT = price discovery occurring BEFORE the NAV-informed trade can enter
R_TRADABLE  = price movement available AFTER lawful next-open execution
R_NAV       = NAV catch-up / catch-down component
ONLY R_TRADABLE MAY SUPPORT THE HARVESTABLE EDGE.
```

### E.2 Gate 1 — the primary identification coefficient

On **discount observations only**:

```
R_TRADABLE,t+1 = a_T + beta_T * d_t + epsilon_t        OLS

PREDICTED SIGN                     beta_T > 0
PRIMARY_IDENTIFICATION_COEFFICIENT beta_T   -- the ONLY one
GATE 1 SUPPORTED  iff  L_T > 0   (lower bound of the §G interval, STRICTLY above zero)
```

**The point estimate never passes Gate 1.**

```
THE SLOPE-MATERIALITY PROPOSAL (beta_T >= 0.10) IS WITHDRAWN AND MAY NOT RETURN.
A slope threshold cannot establish trade profitability: the economic return depends on
the realised discount-severity distribution, which is unknown at seal and must stay so.
Economics are tested by §E.4, on the fixed-unit trade, and nowhere else.
```

### E.3 Mandatory identification diagnostics — no rescue power, ever

Same sample, same regressor, estimated separately, OLS:

```
A. OVERNIGHT PRICE DISCOVERY
   R_OVERNIGHT,t+1 = a_O + beta_O * d_t + epsilon
   convergence sign beta_O > 0 ;  SUPPORTED POSITIVE iff L_O > 0
   PROMOTION_POWER = NONE

B. NAV CATCH-DOWN
   R_NAV,t+1 = a_N + beta_N * d_t + epsilon
   stale-NAV sign beta_N < 0 ;  SUPPORTED NEGATIVE iff U_N < 0
   PROMOTION_POWER = NONE
```

```
beta_O and beta_N may EXPLAIN a failure. They may NEVER rescue beta_T.
Neither appears in any condition that can produce CLASS S.
```

### E.4 Gate 2 — the fixed, parameter-free implementable trade

```
For EVERY eligible primary observation with x_t < 0:
   evening of t   signal known (NAV_t published)
   open(t+1)      LONG 1 FIXED UNIT of HYG
   close(t+1)     EXIT to flat
Otherwise: NO POSITION.

NO position sizing by d_t. NO threshold. NO leverage. NO volatility targeting.
NO holding-period search. NO premium-side short. NO second horizon.
```

*The continuous `d_t` regression tests mechanism strength; the fixed-unit trade tests
actual economics. They are different questions and are kept apart deliberately.*

```
NET_TRADE_RETURN_t+1 = R_TRADABLE,t+1 - ROUND_TRIP_COST
```

---

## §F Cost — SEALED

```
ONE_WAY_COST    = 5.0 bps
ROUND_TRIP_COST = 10.0 bps      (open(t+1) entry + close(t+1) exit = 2 one-way trades)
```

**Authority — external and pre-outcome only. No BENB return, basis observation or signal
day informed this number, and none could have: none exists.**

1. **Calm-market floor, issuer-published:** HYG's 30-day median bid/ask is **0.01 %
   (1 bp)**, i.e. a 0.5 bp one-way half-spread. 5 bps is **ten times** that.
2. **Programme convention:** 2.0 bps one-way, calibrated for month-end rebalancing of a
   broad ETF book. 5 bps is **2.5× more conservative** than the house number.
3. **Stress-period evidence:** BlackRock EII Global Research, *Pricing and Liquidity of
   Fixed Income ETFs in the Covid-19 Crisis of 2020* (July 2020, presented to the SEC
   Fixed Income Market Structure Advisory Committee) charts *"Average bid/ask spread
   (price bps), March 2020"* for broad market, US Treasuries, IG corporates, HY
   corporates and EM debt, separating ETF from underlying bid/offer, **on an axis
   running to roughly 160 bps**. Fixed-income ETF spreads in that month were one to two
   orders of magnitude above the calm-market median, even though ETF spreads were
   tighter than the underlying bonds'.

```
DECLARED ASYMMETRY, stated before outcomes and not to be revisited afterwards:
  A FIXED 5 bps is CONSERVATIVE in normal conditions and OPTIMISTIC in deep stress.
  The mechanism deliberately concentrates activity in stress, so the bias runs IN
  FAVOUR of the strategy.
  => A NEGATIVE result under this cost is STRENGTHENED by the bias.
  => A POSITIVE result MUST carry the caveat that deep-stress execution was not
     modelled, and may never be reported without it.
```

```
NO cost sensitivity grid, ever. NO post-outcome cost revision. NO lowering.
```

---

## §G Inference — ONE framework, SEALED

### G.1 The bootstrap

```
METHOD   = calendar-year block bootstrap
B        = 10,000
INTERVAL = 95 % PERCENTILE (2.5th, 97.5th)
UNIT     = the complete calendar year
DRAWS    = ONE set of replicate draws, shared by beta_T, beta_O, beta_N,
           mean NET_TRADE_RETURN and the calendarised Sharpe.
```

```
NOT STACKED: no HAC, no Newey-West, no second bootstrap family, no episode clustering,
no additional robustness procedure.
```

### G.2 The reconstruction rule — resolved mathematically here, not by S2

```
BOOTSTRAP_RECONSTRUCTION_RULE
  x_t is computed ONCE, causally, on the TRUE chronological record.
  The bootstrap then resamples complete CALENDAR-YEAR BLOCKS OF FROZEN OBSERVATION
  TUPLES  ( x_t , R_OVERNIGHT,t+1 , R_TRADABLE,t+1 , R_NAV,t+1 ) ,
  with replacement, len(year set) years per replicate.
  The expanding median is NOT recomputed inside a replicate.
```

**Why this is the only coherent choice.** `m_t` is a function of the entire chronological
prefix `{b_s : s < t}`. A year-block resample is a *multiset of years in draw order*: a
year may appear twice and a later year may precede an earlier one, so there is no
well-defined prefix. Recomputing the expanding median inside a replicate would (i) be
undefined in ordering, (ii) let a replicate's feature depend on years that in reality came
*after* `t` — i.e. it would **introduce look-ahead into the bootstrap** — and (iii) make
the feature a function of the resample rather than of history. Freezing the causally
constructed feature and resampling the tuples measures sampling uncertainty **in the
estimator given the feature**, which is what the interval is for.

**Declared limitation:** this interval does **not** propagate uncertainty in the
feature-construction step. That is the standard and unavoidable position for any
two-stage causal feature, and it is declared here rather than discovered later.

### G.3 Fragility — exactly one diagnostic

```
LOYO_RULE
  For each calendar year y in the primary year set:
      LOYO_T(y) = OLS beta_T re-estimated on every eligible discount observation NOT in y.
  PASS  iff  LOYO_T(y) > 0 for EVERY y.
  This is a FRAGILITY gate on the POINT estimate. It is not a second interval and not a
  second hypothesis test. Exactly one fragility diagnostic exists.
```

---

## §H Materiality — M1 SEALED, M2 OPEN

### H.1 M1 — cost-surviving expected return (SEALED)

```
M1  lower 95 % bound of mean NET_TRADE_RETURN  >  0        (STRICTLY above zero)
```

### H.2 Monthly P&L construction (SEALED)

```
MONTH_GRID = every calendar month from the month of the FIRST eligible observation to
             the month of the LAST, inclusive, for the primary fund. Determined
             mechanically at S2 from the sealed eligibility rule; zero months RETAINED.

MONTHLY_PNL[m] = SUM of NET_TRADE_RETURN over every sealed signal whose ENTRY falls in
                 month m ;  = 0 if no signal occurs in month m.

CALENDARISED_SHARPE = mean(MONTHLY_PNL) / sd(MONTHLY_PNL, ddof=1) * sqrt(12),  rf = 0.
If sd == 0 in a replicate the replicate's Sharpe is undefined, is dropped, and the
valid-replicate count is reported as k/10000.

NO capital scaling. NO leverage. NO volatility targeting. NO rescaling of any kind.
```

*The sleeve is flat on every day without a discount signal, and those months enter the
series as exact zeros. That is deliberate: it charges the strategy for idle calendar
time. It is also why §Z matters.*

### H.3 M2 — risk-adjusted usefulness — SEALED (BENB-OD-1)

```
M2_METRIC            = the calendarised annualised Sharpe of §H.2
M2_VALUE             = +0.30
M2_BOUNDARY_OPERATOR = STRICT  >

M2  lower 95 % bound of the calendarised annualised Sharpe  >  +0.30

BOUNDARY SEMANTICS, stated so no later reading can soften them:
    L_S = 0.300000...   ->  FAILS M2
    L_S > 0.30          ->  MAY pass M2, subject to every other condition of CLASS S
The POINT estimate of the Sharpe NEVER passes M2. Only the interval endpoint classifies.
```

Authority: **BENB-OD-1**, `ops/OWNER_DECISION_RECORD_CTA_EDGE_02_BENB.md`, taken
2026-09-15 **before** any basis, discount-sign count, regression, return outcome or
backtest existed for this lineage. It is a **BENB-specific** decision and is **not**
inherited from C-A, from CTA-EDGE-01-TA, or from any programme-wide convention — the
programme has none (§Z).

```
NO active-month-only Sharpe. NO sparsity adjustment. NO post-outcome threshold change,
in either direction, for any reason. M1 semantics are UNCHANGED by this decision.
```

---

## §I Multiplicity — LOCKED

```
PRIMARY HYPOTHESIS FAMILY = CTA-EDGE-02-BENB
PRIMARY MEMBER            = HYG beta_T                         m = 1
MULTIPLICITY CORRECTION   = NONE, and none is required: no selection across cells occurs.

beta_O, beta_N     mandatory diagnostics       PROMOTION_POWER = NONE
fixed-unit Gate 2  conditional second gate on the SAME primary lineage, not another
                   discovery shot
LQD                declared secondary replication  PROMOTION = NONE · RESCUE = NONE
premium side       descriptive only               PROMOTION = NONE · RESCUE = NONE
NO additional horizons. NO threshold family. NO second primary.
```

### I.1 LQD secondary

LQD applies the **identical** basis definition, expanding median, discount-side sample,
decomposition and `beta_T` framework. It is reported once, alongside, with its own
interval.

```
LQD CANNOT RESCUE HYG. "LQD passed" is never the claim and never enters §J.
If implementing LQD would require ANY scientific deviation from this contract, LQD is
PARKED rather than redesigned.
```

---

## §J Classification — SEALED, ORDERED, MUTUALLY EXCLUSIVE, EXHAUSTIVE

### J.1 Symbols

All from the §G bootstrap, one set of draws, 95 % percentile bounds:

```
L_T , U_T   beta_T                      L_O , U_O   beta_O        L_N , U_N   beta_N
L_R , U_R   mean NET_TRADE_RETURN       L_S , U_S   calendarised Sharpe
LOYO_OK     every leave-one-year-out beta_T point estimate > 0
```

"Supported positive" = lower bound strictly > 0. "Supported negative" = upper bound
strictly < 0.

### J.2 Evaluability

```
EVALUABLE iff  (a) every pinned hash in §C reproduces,
               (b) the decomposition can be formed on every eligible observation,
               (c) Var(d_t) > 0 on the primary sample, and
               (d) AT LEAST 3 calendar years contain at least one eligible discount
                   observation.
```
*(d) is forced by the structure of §G.3, not chosen: leave-one-year-out must leave a
non-degenerate two-year sample, so three years is the minimum for which the fragility
gate has any content.*

A **pre-run** hash failure is a `LEVEL-1 PRE-RUN FAILURE`: the design cannot execute, no
run happens, no verdict is issued, no trial is spent. It is **not** a verdict.

### J.3 The sealed decision order — FIRST MATCH WINS

```
STEP 0   CLASS F -- IDENTIFICATION / DATA FAILURE
         iff NOT EVALUABLE (J.2), or a post-run structural data defect is found.
         No positive and no negative edge verdict is issued.
         research_status = unresolved
                         + MANDATORY qualifier IDENTIFICATION_INSUFFICIENT_FOR_THE_CLAIM

--- Gate 1 NOT supported:  L_T <= 0  -------------------------------------------------

STEP 1   CLASS A-M -- MIXED NON-HARVESTABLE CONVERGENCE
         iff  (U_N < 0) AND (L_O > 0)
         Both alternatives are supported: the NAV catches down AND the ETF price
         converges overnight, while no tradable next-session convergence is supported.
         research_status = not_promoted, reason MIXED_NON_HARVESTABLE_CONVERGENCE

STEP 2   CLASS A -- STALE-NAV DOMINATED
         iff  (U_N < 0) AND NOT (L_O > 0)
         Discount convergence is materially explained by subsequent NAV catch-down
         without supported tradable ETF-price convergence.
         This does NOT mean the basis is fake.
         research_status = not_promoted, reason STALE_NAV_DOMINATED

STEP 3   CLASS B -- OVERNIGHT PRICE DISCOVERY
         iff  NOT (U_N < 0) AND (L_O > 0)
         ETF market-price convergence exists but occurs before NAV-informed next-open
         execution. Real information; NOT_PROMOTED for this implementation.
         research_status = not_promoted, reason OVERNIGHT_PRICE_DISCOVERY_ONLY

STEP 4   CLASS C1 -- TRADABLE CONVERGENCE RELIABLY EXCLUDED
         iff  neither alternative is supported AND U_T <= 0
         The interval excludes any positive beta_T.
         research_status = not_promoted, reason TRADABLE_CONVERGENCE_EXCLUDED

STEP 5   CLASS C2 -- UNRESOLVED / LOW POWER (identification)
         iff  neither alternative is supported AND U_T > 0
         The interval spans zero. Neither established nor excluded. TERMINAL.
         research_status = unresolved (LOW_POWER)

--- Gate 1 supported:  L_T > 0  ------------------------------------------------------

STEP 6   CLASS G -- FRAGILE / YEAR-DEPENDENT
         iff  NOT LOYO_OK
         Tradable convergence would otherwise be supported, but one calendar year
         carries it. A result one year can remove is not a result.
         research_status = unresolved + MANDATORY qualifier YEAR_DEPENDENT_FRAGILE

STEP 7   CLASS D -- TRADABLE CONVERGENCE PRESENT BUT UNECONOMIC
         iff  (U_R <= 0) OR (U_S <= +0.30)
         Programme-useful edge is reliably excluded.
         research_status = not_promoted, reason TARGET_MARGIN_EXCLUDED

STEP 8   CLASS S -- SUPPORTED PRICE-CONVERGENCE EDGE
         iff  (L_R > 0) AND (L_S > +0.30)          <-- M1 AND M2, both STRICT
         EVIDENCE CEILING = supported. NEVER confirmed. NEVER independently confirmed.
         research_status = supported

STEP 9   CLASS E -- LOW POWER / ECONOMICALLY UNRESOLVED
         everything else: the economic intervals span the required boundary.
         Price convergence appears tradable; useful economics can be neither
         established nor excluded. TERMINAL. No retuning.
         research_status = unresolved (LOW_POWER)
```

**Disjointness and exhaustiveness.** Steps 1–5 partition `L_T <= 0` on the two booleans
`(U_N < 0)` and `(L_O > 0)`, with the `U_T` split inside the residual cell — four
combinations, each landing in exactly one class. Steps 6–9 partition `L_T > 0`: G takes
the fragility failure; D requires an upper bound below a bar and S requires the matching
lower bound at/above it, which are disjoint because `L <= U`; E is the exact complement.
Every reachable combination of the five interval pairs and the LOYO flag maps to exactly
one class. **S2 must prove this mechanically over a synthetic sweep before any real
data is touched.**

**No diagnostic can promote.** `beta_O`, `beta_N`, the LQD replication and the premium
side appear in no condition that can produce `CLASS S`. `beta_O` and `beta_N` appear only
in Steps 1–3, which are unreachable once `L_T > 0`.

---

## §K Forbidden interpretations — BINDING ON EVERY LATER DOCUMENT AND SEAT

A **supported** result does **NOT** prove: authorised-participant causality ·
dealer-balance-sheet causality · that NAV is inefficient generally · that credit is
mispriced generally · crisis diversification · any TSMOM improvement.

A **stale-NAV** result does **NOT** prove: that ETFs are inefficient · that issuer NAV is
wrong in any legal or accounting sense.

An **overnight-convergence** result does **NOT** count as a harvestable edge under this
signal timing, and may never be reported as one.

**No result authorises** changing the horizon · adding thresholds · severity-scaled
leverage · premium-side shorts · changing fund · replacing the NAV source · changing the
normalisation · lowering the transaction cost · extending the holding period. Each is a
**new lineage** with its own S0, trial accounting and Owner authorisations.

**Never treat BlackRock material as independent** — it is issuer documentation,
authoritative about NAV construction and self-interested about conclusions.
**Never treat daily rows as independent tests.**
**"Failed" is not a verdict**; the permitted outcomes are exactly the classes of §J.3.

---

## §L Sample reuse, trial accounting, exposure — LOCKED

```
ETF_PRICE_SAMPLE_REUSE = BURNED / REUSED CONTEXT. The HYG and LQD price histories belong
                         to the lineage of the frozen ETF panel (KB-1, burned 6 of 6,
                         must_not_be_retested_on_same_sample). The raw unadjusted series
                         is a different FOOTING of the same economic history, not a new
                         sample, and is treated as reused.
NAV_PROVENANCE         = NEW external historical source, no prior programme exposure.
OVERALL                = DEPENDENT / MIXED PROVENANCE.
                         A new NAV leg does NOT launder the reused price sample.
EVIDENCE_CEILING       = supported
N_trials               = NOT ASSERTED. D-ETF-COUNT remains UNKNOWN_PENDING_AARON_DECISION
                         and is NOT decided here. This design uses no DSR and no
                         trial-count deflation, so it is not blocked on that decision.
HYPOTHESIS_FAMILY      = F-BENB, to be declared in TRIAL_LEDGER.md §6.2 AT SEAL, before
                         any member runs.
DISCOUNT_OBSERVATION_COUNT = UNKNOWN AT S1, deliberately. Counting x_t < 0 observations
                         would let feature-realisation information influence the cost,
                         the inference, the materiality or the taxonomy. Only the
                         STRUCTURAL eligibility counts of §D.2 are known.
```

```
FABLE_DESIGN_EXPOSED = YES   (the BENB candidate, the stale-NAV alternative, the
                              price-vs-NAV decomposition concept, the candidate
                              instrument family, the portfolio-risk warning)
ASTRA_DESIGN_EXPOSED = NO    (participation in the discovery round alone is not design
                              exposure to this lineage)
Neither status may be rewritten later for convenience. Rows are written to
ops/REVIEWER_EXPOSURE_LOG.md AT SEAL, not before.
```

---

## §M Conditional risk — recorded, not tested

The sleeve goes **long a credit ETF at a discount** precisely when liquidity is
disappearing and canonical trend is profiting from short risk exposure. Convergence is
mechanically bounded but the path can run through the discount widening further first.

```
THIS IS NOT A CRISIS DIVERSIFIER and must never be described as one.
Any FUTURE portfolio study must inspect the declared GFC, COVID and other stress windows
and may NOT rely on unconditional correlation. That is the VRP lesson, recorded here.
NO PORTFOLIO TEST EXISTS IN THIS CONTRACT and none is authorised by it.
```

---

## §Z `M2` — how it was decided, and what it deliberately does not inherit

```
S1_DESIGN_STATUS = PASS
THE DECISION     = BENB-OD-1, ops/OWNER_DECISION_RECORD_CTA_EDGE_02_BENB.md
                   M2 = +0.30, STRICT >, on the calendarised annualised Sharpe of §H.2
                   Taken 2026-09-15, BEFORE any basis, discount-sign count, regression,
                   return outcome or backtest existed for this lineage.
```

### Z.1 Why it had to be an Owner decision rather than an inheritance

The S1 design pass checked whether `+0.30` was already an applicable **programme**
convention and found that it was not. Four findings from the Owner's own records:

1. **C-A's OD-1 binds the number to one estimand.** `ops/OWNER_DECISION_RECORD_PHASE_B.md`
   §3: `PRIMARY_PROSPECTIVE_ESTIMAND = canonical raw net Sharpe, rf = 0, 2 bps
   transaction cost`, and *"**+0.30** means: economically meaningful **persistence of the
   canonical raw-return thesis**."* It is a floor on the canonical book's Sharpe, not a
   free-standing scale.
2. **The Owner had already refused to lend it once, inside C-A's own contract.** OD-7:
   *"FM-1 HAS NO +0.30 / −0.20 MATERIALITY FLOORS. The primary materiality scale is **not
   borrowed**."*
3. **There is no programme-wide floor.** Neither `QUANT_WORKFLOW_VNEXT.md` nor the
   programme handoff sets one. The real convention is per-lineage Owner choice: C-A
   `+0.30 / −0.20` · X01 a `0.15` Sharpe tolerance · Time-Series Value a `−0.15` adverse
   floor · TSMOM-VRP-01 `+7.5 %` annualised on committed capital.
4. **CTA-EDGE-01-TA's `M2 = +0.30` was scoped to that lineage**, which is now CLOSED
   PRE-OUTCOME.

**The number here coincides with C-A's; the authority does not.** BENB-OD-1 is Aaron's
decision for this lineage, taken on its own terms and recorded as such.

### Z.2 The boundary operator

`STRICT >` was fixed explicitly rather than inherited by implication, and it matches the
Owner's established convention for materiality crossings (C-A OD-1: *"A lower confidence
bound of exactly `+0.30` does not trigger material positive persistence"*).

```
L_S = 0.300000...  ->  FAILS M2 and therefore cannot reach CLASS S
```

### Z.3 The fact the Owner weighed, and accepted

C-A's floor governs a **fully invested, always-on** book. This sleeve is **flat on every
day without a discount signal**, so its monthly series is mostly exact zeros by
construction (§H.2), and a Sharpe on such a series is not the same statistic as a Sharpe
on an always-invested book. The degree of sparsity is **unknown at seal and must remain
unknown** until the governed run.

BENB-OD-1 fixes the floor knowing this, and explicitly forbids the three repairs that
knowledge of the sparsity would later invite:

```
NO active-month-only Sharpe · NO sparsity adjustment · NO post-outcome threshold change.
```

M1 semantics are **unchanged** by this decision.

---

```
SEALED. NO BUILD. NO RUN. NO RUN AUTHORIZATION. NO OUTCOME ACCESSED.
```
