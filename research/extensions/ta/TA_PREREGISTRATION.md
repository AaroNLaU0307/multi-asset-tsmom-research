# CTA-EDGE-01-TA — PREREGISTRATION CONTRACT (S1 DESIGN + SEAL)

```
LINEAGE                = CTA-EDGE-01-TA
CONTRACT_ID            = CTA-EDGE-01-TA-PREREG-01
CANDIDATE              = TREASURY_AUCTION_SUPPLY_ABSORPTION
PRIMARY_CLAIM_TYPE     = REDUCED_FORM
LANE                   = FULL
STATUS                 = SEALED
WORKFLOW_AUTHORITY     = ../../../QUANT_WORKFLOW_VNEXT.md  (vNext, cutover 2026-09-12)
SEAL_ACT               = S1 DESIGN + PRE-SEAL REPAIR + CONDITIONAL SEAL, performed by
                         Claude Opus 5 (Main Agent / builder seat) under the programme
                         controller's CTA-EDGE-01-TA S1 authorisation of 2026-09-15,
                         which accepted S0 = PASS, confirmed M2 = +0.30, and mandated
                         five pre-seal repairs
S2_AUTHORIZED          = NO
DATA_ACQUISITION_AUTHORIZED = NO   (beyond the S1 auction-metadata grant already used)
REAL_RUN_AUTHORIZED    = NO
RUN_AUTHORIZATION_CREATED = NO
```

---

## §0 Authority, provenance and standing facts

**This document is the SOLE design authority for `CTA-EDGE-01-TA`.** Where it and
any other document disagree about this lineage's design, this document wins.

`TA_S0_FRAME.md` is **provenance, never design authority**. It is preserved
byte-unchanged and pinned in `TA_SEAL_MANIFEST.md`. Every S0 statement that this
contract supersedes is enumerated in `TA_S0_REPAIR_RECORD.md`; a superseded S0
sentence has no force, and no later session may revive one.

**Standing programme facts, unchanged by this contract.** Canonical TSMOM remains
`SUPPORTED — NOT INDEPENDENTLY CONFIRMED` and FROZEN. C-A remains sealed and LIVE
under passive monthly accrual, **not accessed, not inferred, not inspected**. C-D
remains at `HOLD`. TSMOM-VRP-01, Time-Series Value, X01, XSMOM and the four overlays
remain CLOSED. The knowledge-base repository is **not modified**.

**Outcome state at seal.** No ETF event return, no `AC`, no Sharpe, no bootstrap
result, no P&L and no candidate statistic of any kind has been computed, read or
inferred for this lineage. See §S.

---

## §A The research object — LOCKED

```
PRIMARY_RESEARCH_QUESTION
  Does the predeclared US Treasury coupon-auction cycle produce an economically
  harvestable, repeatable round-trip return pattern in a liquid duration ETF,
  measured close-to-close, that survives the programme's realistic transaction
  costs and is not carried by a single year or regime?

PRIMARY_OBJECT     = the auction-cycle effect AS IT REACHES A LIQUID DURATION ETF
PRIMARY_INSTRUMENT = TLT   (iShares 20+ Year Treasury Bond ETF)
SECONDARY_INSTRUMENT = IEF (iShares 7-10 Year Treasury Bond ETF)
20Y                = EXCLUDED from the primary and from the secondary (§C.4)
DEALER / INTERMEDIATION CAUSAL CLAIM = NOT PRIMARY · NOT ESTABLISHED · PARKED (§R.1)
```

The claim is **reduced-form**. It is never a claim about cash Treasuries, about
30-year supply specifically, or about dealer balance-sheet capacity. §K is binding.

---

## §B The event definition — LOCKED

### B.1 Anchor

```
t0 (PRIMARY)   = the auction date of a nominal 30-Year Treasury bond auction
t0 (SECONDARY) = the auction date of a nominal 10-Year Treasury note auction
```

`t0` is read from the pinned official record (§L) and never inferred from prices.

### B.2 Family membership — the sealed inclusion rule

An auction row joins a tenor family if and only if **all** of the following hold on
the pinned record:

1. `security_type` ∈ {`Note`, `Bond`};
2. `cash_management_bill_cmb` is not truthy;
3. `inflation_index_security` is not truthy  (TIPS excluded);
4. `floating_rate` is not truthy  (FRNs excluded);
5. `original_security_term` equals the family key (`30-Year` / `10-Year`);
6. **ON-CYCLE RULE** — `maturity_date − auction_date ≥ tenor_years × 365.25 − 183`
   days, i.e. the security still has at least (tenor − 6 months) to run.

Rule 6 exists because `original_security_term` alone admits off-cycle reopenings of
heavily seasoned securities — the record contains 10-year reopenings with 3 years and
with 6 years remaining — which are not the mid-month refunding auction the mechanism
describes. **Rule 6 is a NO-OP on the primary family**: it drops 0 of 245 `30-Year`
rows. It therefore cannot have been chosen to shape the primary result. On the
secondary it drops exactly 5 rows, all of them enumerated in §M.2.

### B.3 The common trading grid

```
GRID = the ordered set of dates on which the frozen ETF panel
       data/close_prices_raw.csv carries a NON-NULL close for TLT.
     = 6,007 trading days, 2002-07-30 .. 2026-06-12, ZERO internal gaps.
```

**Verified at seal:** IEF, SHY and SPY have an *identical* date set inside that
range — zero dates in one and not another. One grid therefore serves every cell, and
`common_grid()` re-asserts this at every build and raises if it ever stops holding.

All offsets below are in **grid days**: not calendar days, not generic business days.

### B.4 Window geometry — one pair, applied identically to every cell

Let `i` be the grid index of `t0`.

```
PRE  window : close(GRID[i-6])  ->  close(GRID[i-1])
POST window : close(GRID[i])    ->  close(GRID[i+5])
AUCTION-DAY BAR : the close-to-close return GRID[i-1] -> GRID[i]
                  belongs to NEITHER window. It is excluded by construction.
```

Return-bearing days are therefore `GRID[i-5 .. i-1]` (PRE) and `GRID[i+1 .. i+5]`
(POST) — five each, eleven marks, twelve grid points spanned.

Why the boundaries fall exactly here, from the verified mechanics (§N.1): the
competitive auction closes 1:00 p.m. ET and results are public ~1:02 p.m., three
hours before the 4:00 p.m. ETF close. `close(t0-1)` is the last close entirely before
the auction; `close(t0)` is the first close entirely after results. Any other choice
nets the pre-auction concession against the post-auction reversal inside one daily
bar. The design therefore **forfeits the 1:02 p.m.–4:00 p.m. reversal on auction
day** — a declared, irreducible attenuation, fixed before any outcome exists.

### B.5 Event validity

An event is **VALID** iff `t0 ∈ GRID` and `i-6 ≥ 0` and `i+5 ≤ len(GRID)-1`.
There is no other inclusion criterion, and **no outcome may ever remove an event**.

Exclusion reasons are mechanical and exhaustive: `T0_NOT_ON_GRID`,
`WINDOW_BEFORE_PANEL_START`, `WINDOW_AFTER_PANEL_END`.

### B.6 Reopenings, schedule anomalies, overlaps

- **Reopenings and original issues are ONE family.** The reopening split is a
  declared descriptive tabulation (§R.2), never a gate and never a filter.
- **Schedule anomalies** (holidays, moved auctions, the 30-year issuance gap
  2001-08 → 2006-02, the 20-year suspension 1986-06 → 2020-05) are handled entirely
  by §B.5. No date is edited, inferred or interpolated.
- **Overlapping windows.** Two events collide when their `t0` grid indices are at
  most 11 apart. On the sealed calendar the **primary has ZERO collisions** (minimum
  consecutive gap 17 grid days). The secondary has exactly one
  (2019-06-12 / 2019-06-21, gap 7); **both events are retained**, no deletion, and
  the dependence is carried by the year-level resample (§H).

---

## §C Sample boundaries and the sealed event calendar — LOCKED

### C.1 Frozen endpoints

```
PANEL              = data/close_prices_raw.csv, 30 yfinance adjusted-close series,
                     1993-01-29 .. 2026-06-12, sha256
                     3d2a7a56dbd92d4ff8138cfd894c87f5ac5ac088a11165db870673e0c05c3c31
FROZEN_LAST_DATE   = 2026-06-12   (nothing after it is an observation, ever)
AUCTION_RECORD_CUTOFF = 2026-06-12
```

### C.2 PRIMARY cell — TLT / 30-Year — as counted from the pinned record

```
in-family rows 1990-01-01 .. 2026-06-12      = 245
dropped by the ON-CYCLE rule                 = 0
VALID COMPLETE WINDOWS                       = 213
exclusions                                   = 31 T0_NOT_ON_GRID (all pre-2002-07-30)
                                               1 WINDOW_AFTER_PANEL_END (2026-06-11)
first valid t0                               = 2006-02-09
last  valid t0                               = 2026-05-13
calendar years represented                   = 21   (2006 .. 2026)
unique ISO auction weeks                     = 213
max valid events per ISO week                = 1
MAX VALID EVENTS PER CALENDAR MONTH          = 1     (no month has two)
minimum consecutive t0 gap                   = 17 grid days   (collision <= 11)
OVERLAPPING VALID WINDOWS                    = 0
reopening split                              = 73 original issue / 140 reopening
MONTH GRID                                   = 2006-02 .. 2026-05 = 244 months
                                               (213 event months, 31 zero months)
valid events per year = 2006:2 2007:2 2008:2 2009:10 2010..2025:12 each 2026:5
```

The 30-year frequency history is thereby established **from the record, not from
recollection**: 2–4 per year 1990–2001, **no auctions at all 2002–2005**, 2 per year
2006–2008, 10 in 2009, and 12 per year from 2010.

### C.3 SECONDARY cell — IEF / 10-Year

```
in-family rows                               = 317
dropped by the ON-CYCLE rule                 = 5   (enumerated in §M.2)
on-cycle auctions                            = 312
VALID COMPLETE WINDOWS                       = 258
exclusions                                   = 53 T0_NOT_ON_GRID, 1 AFTER_PANEL_END
first / last valid t0                        = 2002-08-07 / 2026-05-12
calendar years represented                   = 25   (2002 .. 2026)
unique ISO auction weeks                     = 258     max per ISO week = 1
max valid events per calendar month          = 2       (2019-06 only)
OVERLAPPING VALID WINDOWS                    = 1       (2019-06-12 / 2019-06-21)
reopening split                              = 96 original issue / 162 reopening
```

10-year frequency history from the record: 4 per year 1990–2002 (6 in 1996), 6 in
2003, 8 per year 2004–2007, 12 per year from 2008 (14 in 2019).

### C.4 The 20-year is excluded — two independent reasons

1. Issuance was **suspended 1986-06 → 2020-05**, so within the panel it would
   contribute only 2020-05 onward — entirely inside the era in which the published
   effect is weakest.
2. `20Y_ELIGIBILITY = UNRESOLVED_NON_BLOCKING`. Whether a freshly issued 20-year bond
   satisfies TLT's index rule at issue is not resolved: the iShares product page and
   the ICE index description both say *greater than twenty years*, which a security
   with exactly twenty years to run does not satisfy, but neither source is the index
   methodology document. Per the controller's §15 this question is **non-blocking**
   and no further effort was spent on it.

The 20-year nevertheless appears **inside** 49 of the 213 primary windows and is
accounted for as structural calendar overlap (§C.5), not ignored.

### C.5 Structural calendar overlap inside the 213 primary windows — a sealed FACT

Counts of auctions of other families falling on a **return-bearing day** of a primary
window (the primary's own auction day is the excluded bar, so `30-Year` cannot
appear):

| family | windows containing at least one | share |
|---|---|---|
| **10-Year** | **213 / 213** | **100.0 %** |
| **3-Year** | **210 / 213** | **98.6 %** |
| TIPS | 120 / 213 | 56.3 % |
| 20-Year | 49 / 213 | 23.0 % |
| 2-Year | 3 / 213 | 1.4 % |
| 5-Year | 3 / 213 | 1.4 % |
| 7-Year | 3 / 213 | 1.4 % |
| FRN | 2 / 213 | 0.9 % |
| **no other auction of any family** | **0 / 213** | **0.0 %** |

**This is the mechanical justification for the reduced-form claim, and it is
decisive.** Every single primary window contains a 10-year auction, and almost every
one also contains a 3-year auction. The TLT estimate is therefore a **refunding-week**
effect. It is not, and can never be presented as, a 30-year-supply effect. §K.3.

It also **corrects** an S0 statement: the end-of-month 2/5/7-year block is *not* a
routine occupant of the primary window (1.4 % each), contrary to the S0's provisional
calendar description. See `TA_S0_REPAIR_RECORD.md` item 7.

---

## §D The primary estimand — LOCKED

### D.1 Definition

For a valid event `i` of a cell, with `P(d)` the panel's adjusted close on grid day
`d` for that cell's instrument:

```
r_pre,i  = ln P(GRID[i-1]) - ln P(GRID[i-6])
r_post,i = ln P(GRID[i+5]) - ln P(GRID[i])

AC_GROSS_i  = 1e4 * ( r_post,i - r_pre,i )            [basis points]
AC_NET_i    = AC_GROSS_i - COST_BPS                   [basis points, COST_BPS = 8.0]

PRIMARY STATISTIC = mean over all valid PRIMARY events of AC_NET_i
PREDICTED SIGN    = positive
```

Log returns are used because the estimand is the literature's own price-pressure
measure — SR 1188 Table 3 computes its pre- and post-auction returns as changes in
the log mid-price, and combines them as *post minus pre* exactly as here.

**Declared approximation, stated before any outcome.** `AC` is a log-return
difference. Its reading as the P&L of one unit of notional traded along §E.1 is exact
to first order; the second-order discrepancy is immaterial at the magnitudes the bars
sit at. The implementation additionally reports `AC_SIMPLE_i` (the same quantity in
simple returns) as a declared descriptive series with `PROMOTION_POWER = NONE`, so the
discrepancy is visible and is never adjudicable.

### D.2 Self-differencing — what it does and does not do

```
SELF_DIFFERENCING  =  REDUCES SENSITIVITY TO A LOCALLY STABLE COMMON EXPECTED DRIFT,
                      AND APPROXIMATELY REMOVES COMMON ACCRUAL COMPONENTS
SELF_DIFFERENCING !=  EXACT REMOVAL OF NON-AUCTION SHOCKS
```

Equal-length adjacent pre/post differencing reduces sensitivity to a common expected
drift that is locally stable across the event neighbourhood, and approximately removes
the daily coupon accrual carried by an adjusted (total-return) close.

It does **not** remove: realised rate shocks · macro announcements · Quarterly
Refunding Announcement information · policy surprises · other auctions' spillover ·
non-stationary expected returns. No claim in this lineage may rest on the difference
having removed any of those.

### D.3 Controls

```
PRIMARY CONTROL = none.
```

The estimand is self-differencing in the bounded sense of §D.2, and no matched
non-auction control window exists in this calendar — §C.5 shows 0 of 213 windows are
free of other auctions. Building a "matched control" here would be inventing a
counterfactual the calendar does not contain. Identification support is carried
instead by the diagnostics of §G, each with an explicitly declared power.

### D.4 Secondary cell statistic

The secondary (IEF / 10-Year) reports **mean `AC_NET` and its interval only**. It has
**no** calendarised Sharpe and **no** monthly series. This is deliberate: it removes
the only place where the secondary's single overlapping window pair could have created
a monthly-aggregation ambiguity, and the secondary has no rescue power in any case.

---

## §E Cost model and position path — LOCKED

### E.1 The position path — written out exactly

```
close(GRID[i-6])  :  flat   ->  SHORT 1 unit of the instrument
close(GRID[i-1])  :  SHORT  ->  flat
auction-day bar   :  FLAT                      <-- exposure is ZERO across GRID[i-1] -> GRID[i]
close(GRID[i])    :  flat   ->  LONG 1 unit of the instrument
close(GRID[i+5])  :  LONG   ->  flat
```

**There is NO short-to-long flip.** The position is FLAT across the excluded
auction-day bar. Any implementation that carries exposure from `GRID[i-1]` to
`GRID[i]` is WRONG and must fail its tests. The S2 implementation-acceptance contract
carries this as a mandatory behavioural assertion (§T.2 item 4).

### E.2 Cost arithmetic

```
one-way units traded per event = 1 (open short) + 1 (close short)
                               + 1 (open long)  + 1 (close long)   = 4
one-way cost                   = 2 bps      (programme convention)
COST_BPS                       = 4 x 2 = 8.0 bps per instrument per event
```

### E.3 Materiality bars

```
M1  COST CLEARANCE          mean AC_NET  >=  +8.0 bps per event
                            (equivalently mean AC_GROSS >= +16.0 bps)
    Source of the number: the programme's 2 bps one-way cost convention. NOT the
    literature, and not any observed outcome.

M2  RISK-ADJUSTED USEFULNESS  calendarised annualised Sharpe  >=  +0.30
    Source of the number: Aaron's existing C-A Owner decision OD-1 materiality
    floor, re-confirmed for this lineage as an Owner methodology decision
    (ops/OWNER_DECISION_RECORD_CTA_EDGE_01_TA.md, TA-OD-1).
    OWNER_M2_CONFIRMATION = YES, given BEFORE any candidate outcome was accessed.
    It may NOT be changed after exposure, in either direction, for any reason.
```

---

## §F Calendarised Sharpe — M2's construction — LOCKED

### F.1 The monthly series

```
MONTH_GRID = every calendar month from the month of the FIRST valid primary event to
             the month of the LAST valid primary event, inclusive
           = 2006-02 .. 2026-05  =  244 months   (fixed by §C.2, not re-derived)

For each month m in MONTH_GRID:
  MONTHLY_TA_RETURN[m] = sum of AC_NET_i over every valid PRIMARY event i whose
                         AUCTION DATE t0_i falls in month m, expressed as a return on
                         ONE FIXED UNIT NOTIONAL;
                       = 0 if no valid primary event falls in month m.
```

On the sealed calendar **every month contains at most one valid primary event**, so
the summation is well defined and never exercised; it is written down anyway so no
builder has to decide. `PRIMARY_EVENT_WINDOWS_OVERLAP = NO`, so no overlapping P&L is
ever summed.

Zero months are **retained**, not dropped: 213 event months and **31 zero months**.
This deliberately charges the strategy for idle calendar time.

```
NO leverage optimisation · NO volatility targeting · NO capital scaling ·
NO weight search · NO rescaling of any kind · risk-free rate = 0.
```

### F.2 The statistic

```
CALENDARISED_SHARPE = mean(MONTHLY_TA_RETURN) / sd(MONTHLY_TA_RETURN) * sqrt(12)
                      sd uses ddof = 1.
```

If `sd == 0` in a replicate the replicate's Sharpe is undefined; it is dropped and the
valid-replicate count is reported as `k/10000`, following the VRP convention.

---

## §G Diagnostics and their powers — LOCKED

Every quantity this lineage computes carries exactly one declared power. Nothing is
silently promoted into an additional shot on goal.

| quantity | role | PROMOTION | DAMAGE | KILL |
|---|---|---|---|---|
| **TLT combined `AC_NET`** | **PRIMARY**, m = 1 | — | — | — |
| IEF combined `AC_NET` | declared SECONDARY | **NONE** | NONE | NONE |
| **SHY** combined `AC` | **MATURITY-GRADIENT DIAGNOSTIC** | **NONE** | **NONE** | **NONE** |
| **SPY** combined `AC` | **BROAD CALENDAR PLACEBO** | **NONE** | **YES** (§G.2) | NONE |
| macro / QRA adjusted specification | identification diagnostic | **NONE** | **YES** (§G.3) | NONE |
| leave-one-year-out | fragility gate | **NONE** | **YES** (§G.4) | NONE |
| PRE and POST leg decomposition | descriptive | **NONE** | NONE | NONE |
| auction-day bar return | descriptive | **NONE** | NONE | NONE |
| original-issue / reopening split | descriptive | **NONE** | NONE | NONE |
| `AC_SIMPLE` | descriptive | **NONE** | NONE | NONE |
| own-announcement-in-window tabulation | descriptive | **NONE** | NONE | NONE |

### G.1 SHY — maturity-gradient diagnostic, NOT a placebo

**The S0's hard-null reading of SHY is REJECTED and removed.** SHY anchored on the
30-year auction sits inside a window that contains a 10-year auction 100 % of the
time and a 3-year auction 98.6 % of the time (§C.5), and the 10-year auction has
documented cross-maturity spillover to the short end. A non-zero SHY statistic is
therefore **entirely consistent** with the reduced-form refunding-week claim and says
nothing against it.

```
SHY_HARD_PLACEBO    = REMOVED
SHY_FINAL_ROLE      = MATURITY_GRADIENT_DIAGNOSTIC
SHY may answer      : "Does the measured pattern attenuate toward the short end?"
SHY may NOT answer  : "Does the auction-cycle mechanism exist?"
SHY_PROMOTION_POWER = NONE
SHY_KILL_POWER      = NONE
SHY_DAMAGE_POWER    = NONE
A material SHY statistic, alone or in combination, NEVER kills, downgrades or
qualifies the TLT verdict. No classification rule in §I references SHY.
```

SHY is reported as `mean AC_GROSS` with the same interval method, alongside TLT and
IEF, purely so the maturity gradient is visible.

### G.2 SPY — broad calendar placebo, DAMAGE only

SPY exists to detect one specific alternative: that the same mid-month timing produces
a **broad cross-asset return pattern unrelated to Treasury duration**.

SPY is **not** a complete control for Treasury-specific macro news, CPI sensitivity,
QRA supply information, or duration shocks, and is never described as one.

```
SPY_DAMAGE_RULE  (sealed, absolute, evaluated only against a would-be Class D)

    TRIGGER  iff   L95( mean AC_GROSS of SPY )  >=  +16.0 bps per event

where L95 is the lower bound of the SAME year-block bootstrap interval (§H), on the
SAME replicate draws, anchored on the SAME 213 primary event dates, on SPY's own
close series.

  +16.0 bps is the M1 GROSS bar - the same absolute yardstick the primary must clear.
  One-sided and same-signed: a negative SPY statistic does not explain a positive TLT
  statistic, so only a positive broad pattern can damage.
```

The rule is absolute, not a ratio to TLT, and takes no TLT input, so it cannot be
resolved by ranking after the fact. It cannot fire on a trivial few-basis-point
placebo: it requires a *reliably* useful-sized equity pattern.

### G.3 Macro / QRA adjusted specification — ONE fixed model, DAMAGE only

The primary remains **UNCONDITIONAL**. No event is ever deleted, shortened or moved.

**Covariates, signed.** For covariate type `k` and event `i`:

```
X_k,i = 1{ a release of type k falls on a POST return-bearing day }
      - 1{ a release of type k falls on a PRE  return-bearing day }      in {-1, 0, +1}
```

The signed form is used because `AC` is a *difference* of the two windows: a release
matters through which side it lands on, and a release present on both sides, or on
neither, correctly scores 0.

**The four covariate types, sealed:**

| k | definition | source |
|---|---|---|
| `CPI` | the date of the BLS Consumer Price Index news release | BLS official release-schedule archives — S2 acquisition (§L.2) |
| `NFP` | the date of the BLS Employment Situation news release | BLS official release-schedule archives — S2 acquisition (§L.2) |
| `FOMC` | the date of the FOMC post-meeting statement | Federal Reserve official FOMC calendars — S2 acquisition (§L.2) |
| `QRA` | the Quarterly Refunding Announcement date | **already derived from the pinned record** (§L.1): the `announcemt_date` shared by the ORIGINAL-ISSUE 10-year note and 30-year bond of the Feb/May/Aug/Nov refunding. 139 dates, 1990-01-31 .. 2026-05-06. On the 213 primary windows: signed value −1 for 6 windows, 0 for 207 |

**The model:**

```
AC_GROSS_i = b0 + b1*CPI_i + b2*NFP_i + b3*FOMC_i + b4*QRA_i + e_i

  Ordinary least squares, solved by numpy.linalg.lstsq (minimum-norm, deterministic).
  NO interactions. NO alternative windows. NO stepwise selection.
  NO outcome-dependent covariate removal. Covariates are NEVER dropped.

ADJUSTED_EFFECT = b0   (the fitted AC_GROSS of an event with no net macro asymmetry)
```

```
MACRO_QRA_DAMAGE_RULE  (sealed, evaluated only against a would-be Class D)

    TRIGGER  iff   b0  <  +16.0 bps          (the M1 GROSS bar)
             or    the diagnostic is NOT_EVALUABLE.

    NOT_EVALUABLE  iff  the design matrix is rank deficient
                   or   fewer than 20 events have all four signed covariates = 0.
```

Tied to M1, absolute, fixed before outcomes, and not a percentage change. It is a
**damage diagnostic, not a hypothesis test**: it is read off the point estimate and
consumes no inferential shot. It can only move a would-be D to Class I — **it can
never upgrade A, B, C or I to D.**

**Disclosed risk, and its outcome-free pre-check.** The reference group's size cannot
be established at S1, because the CPI / NFP / FOMC calendars are outside this stage's
data authorisation. If the auction window is almost never macro-clean, the diagnostic
returns `NOT_EVALUABLE` and a would-be D becomes Class I — which is the honest reading,
since a design in which no auction window is ever macro-clean cannot separate the
auction from the macro calendar at daily frequency. **S2 must report the covariate
cross-tabulation — a pure calendar cross-tab containing no return and no outcome —
BEFORE any `AC` is computed**, so that reachability is known to the Owner while the
lineage is still outcome-blind (§T.2 item 6).

**Recorded, not adopted.** 143 of the 213 primary windows contain the event's **own**
announcement date on a PRE return-bearing day (signed −1; 70 score 0). That is the
densest supply-information covariate available and it is derivable from pinned data,
but it is **not** in the accepted four-covariate list and is therefore **not** added:
it is reported as a descriptive tabulation only. Whether to add it is an Owner
decision for a future lineage, not a choice this contract may make.

### G.4 Leave-one-year-out — the fragility gate

```
LOYO_DAMAGE_RULE  (sealed, evaluated only against a would-be Class D)

  For each of the 21 calendar years y in 2006..2026:
      LOYO_y = mean of AC_NET over every valid primary event NOT in year y.

  PASS  iff  LOYO_y > 0 for ALL 21 years.
  TRIGGER (fail) iff  min_y LOYO_y <= 0.
```

This is a **fragility** gate, not a second confidence interval and not a second
hypothesis test. It is ranked above significance: a result that one year can remove is
not a result. **Exactly one fragility metric exists.** The LOYO calendarised Sharpe is
also **reported** for every year (§H.3) but is **not** part of the gate, so no second
metric is constructed.

---

## §H Uncertainty — ONE bootstrap, LOCKED

### H.1 The resample

```
UNIT             = the complete CALENDAR YEAR
PRIMARY YEAR SET = the 21 years 2006..2026 (from §C.2)
SECONDARY YEAR SET = the 25 years 2002..2026 (from §C.3)
METHOD           = non-parametric block bootstrap: draw len(YEAR_SET) years WITH
                   REPLACEMENT, B = 10,000 replicates, 95 % PERCENTILE interval
                   (2.5th and 97.5th).
```

Years, not weeks: the dependence that matters is regime-level — issuance size, QE/QT,
the documented post-2014 attenuation — and a year-level resample subsumes within-week
and within-month clustering, including the secondary's single overlapping pair.

### H.2 What each replicate reconstructs

For every replicate, in this order:

1. resample complete calendar years with replacement;
2. reconstruct the **event observations** for the mean statistics — every valid event
   belonging to a drawn year, once per time that year is drawn;
3. reconstruct the **complete monthly calendarised series**, including zero months —
   each drawn year contributes exactly the months it holds in `MONTH_GRID` (2006
   contributes Feb–Dec = 11 months, 2026 contributes Jan–May = 5, every other year 12),
   concatenated in draw order;
4. compute, on that replicate: **mean `AC_NET`** and **calendarised Sharpe**.

```
RETURN exactly ONE 95 % percentile interval for mean AC_NET
   and exactly ONE 95 % percentile interval for calendarised Sharpe.

NO second bootstrap family. NO parametric Sharpe test. NO HAC stack.
NO alternative annualisation. NO additional robustness variant.
```

### H.3 Scope of the same draws

The **same** replicate draws over the primary year set drive, jointly: TLT mean
`AC_NET`, TLT calendarised Sharpe, SPY mean `AC_GROSS` (§G.2) and SHY mean `AC_GROSS`
(§G.1). The secondary cell uses its own 25-year set.

```
SEED PROTOCOL (constants only; no data)
  numpy.random.SeedSequence(7).spawn(5)[4]   -- a new, previously unused child of the
                                               programme's existing seed constant 7;
                                               children 0..3 remain VRP's and are
                                               untouched
  that child .spawn(2) -> [0] drives the PRIMARY-grid bootstrap (TLT, SPY, SHY)
                          [1] drives the SECONDARY (IEF) bootstrap
  each child drives numpy.random.Generator(numpy.random.PCG64(child))
```

The seed is a fixed constant of the programme, derived from nothing, and is not
tunable.

---

## §I Classification — the A/B/C/D/I taxonomy — SEALED, ORDERED, EXHAUSTIVE

### I.1 Symbols

```
L_AC , U_AC  = 2.5th / 97.5th percentile of mean AC_GROSS  (bps per event), TLT
L_N = L_AC - 8.0 , U_N = U_AC - 8.0        = the same bounds for mean AC_NET
L_S , U_S    = 2.5th / 97.5th percentile of calendarised Sharpe, TLT
```

### I.2 The sealed decision order — FIRST MATCH WINS

```
STEP 1   CLASS A -- DIRECTIONAL ETF PATTERN EXCLUDED
         iff  U_AC <= 0
         The predeclared POSITIVE auction-cycle AC is excluded at this ETF /
         close-to-close granularity. This does NOT falsify the cash-Treasury auction
         mechanism (§K.4).
         DISPOSITION = NOT_PROMOTED

STEP 2   CLASS B -- TARGET MARGIN RELIABLY EXCLUDED
         iff  ( U_N < +8.0 )  OR  ( U_S < +0.30 )
         The directional effect is not excluded as in A, but at least one
         useful-margin UPPER bound lies below its required threshold: a positive
         ETF-level effect may exist, and the study reliably excludes a
         programme-useful one under the sealed implementation.
         DISPOSITION = NOT_PROMOTED, reason = TARGET_MARGIN_EXCLUDED

STEP 3   evaluate the WOULD-BE-D CONDITION
             W  =  ( L_N >= +8.0 )  AND  ( L_S >= +0.30 )

         STEP 3a  CLASS D -- SUPPORTED ETF-LEVEL EFFECT
                  iff  W  AND  LOYO passes (G.4)
                          AND  SPY damage does NOT trigger (G.2)
                          AND  macro/QRA damage does NOT trigger (G.3)
                  EVIDENCE CEILING = SUPPORTED.  Never CONFIRMED, never
                  INDEPENDENTLY CONFIRMED (§Q).

         STEP 3b  CLASS I -- IDENTIFICATION / DEPENDENCE FAILURE
                  iff  W  AND  at least one of those three diagnostics triggers
                  The result cannot be given a valid positive or negative mechanism
                  reading. It is NOT relabelled failed, falsified, "not enough
                  alpha", or unresolved-because-the-interval-is-wide.

STEP 4   CLASS C -- UNRESOLVED / LOW POWER
         everything else, i.e. not A, not B, and not W: the interval spans one or
         both materiality boundaries and the evidence establishes neither a useful
         effect nor its exclusion.
         TERMINAL. No new window, threshold tweak, sample extension, alternate ETF,
         filter or parameter search may rescue this lineage (§O).
```

**Mutual exclusivity and exhaustiveness, verified:** A implies `U_N ≤ −8 < 8`, so A
would also satisfy B's test — the ordering resolves it and A wins. B requires an upper
bound below a threshold; `W` requires both lower bounds at or above the same
thresholds, and `L ≤ U`, so B and `W` are disjoint. 3a and 3b partition `W`. C is the
exact complement of (A ∪ B ∪ W). Every reachable combination of the five bounds lands
in exactly one class.

### I.3 Class I — the additional executed-calendar trigger

Class I is also the verdict if, **after** the run, the executed event calendar is found
to deviate from the sealed one in a way that invalidates the sealed estimand
(mechanical event-calendar contamination).

A **pre-run** identity failure is a different thing and is **not** a verdict: if the
sealed hashes in `TA_DATA_MANIFEST.md` do not reproduce before the run, that is a
**LEVEL-1 PRE-RUN FAILURE** — the design cannot execute, no run happens, no verdict is
issued and no trial is spent (§P).

### I.4 Programme status mapping

```
CLASS A  -> research_status = not_promoted
CLASS B  -> research_status = not_promoted   (reason TARGET_MARGIN_EXCLUDED)
CLASS C  -> research_status = unresolved
CLASS D  -> research_status = supported
CLASS I  -> research_status = unresolved, with the mandatory qualifier
            IDENTIFICATION_INSUFFICIENT_FOR_THE_CLAIM recorded alongside it.
```

The knowledge-base vocabulary has no `identification_failure` token. `unresolved` is
the nearest legal value and the qualifier carries the distinction; the qualifier is
**not optional** and a Class-I result may never be reported as plain `unresolved`.
Registering any of this in the knowledge-base repository is a separate Owner decision
and is **not** taken here.

---

## §J Multiplicity — LOCKED

```
PRIMARY HYPOTHESIS FAMILY = CTA-EDGE-01-TA
PRIMARY MEMBER            = TLT combined AC_NET        m = 1
MULTIPLICITY CORRECTION   = NONE, and none is required: no selection across cells
                            occurs. The lineage verdict is read off the TLT cell,
                            designated in advance.
```

`IEF` is a declared secondary with its own interval and **no rescue power**; "IEF
passed" is never the claim and never enters §I. `SHY`, `SPY`, the leg decomposition,
the auction-day bar, the reopening split, `AC_SIMPLE` and the own-announcement
tabulation are diagnostics or descriptives with the powers in §G. **No diagnostic is
ever turned into an additional shot on goal.**

The four-cell family `{IEF, TLT} × {PRE, POST}` considered at S0 is **not** retained:
the estimand already combines the legs, and the literature prior for the POST leg in
long duration is absent or reversed in the modern era.

---

## §K Forbidden interpretations — BINDING ON EVERY LATER DOCUMENT AND SEAT

1. **Never** evidence that primary-dealer balance-sheet constraints cause the effect.
   Daily ETF closes cannot identify that channel.
2. **Never** a claim about cash Treasuries. The object is a liquid duration ETF, and
   the claim is always worded *"the auction-cycle premium as it reaches a duration
   ETF"*.
3. **Never** attributable to 30-year supply specifically. Every primary window
   contains a 10-year auction (§C.5). Any TLT effect is a **refunding-week** effect.
4. A null is **never** "the auction cycle does not exist". A null is Class A or Class
   B, and the difference between them must be stated.
5. **Never** evidence about auction supply and Treasury expected returns generally,
   nor about term premia, nor about issuance policy.
6. **Never** crisis diversification. The expected conditional risk runs the other way:
   the PRE leg is short duration and loses in flight-to-quality weeks.
7. **Never** an improvement to canonical TSMOM. No portfolio quantity is computed or
   authorised by this contract.
8. **No result may authorise changing** the window, the anchor, the mapped tenor, the
   instrument, the cost convention, M1, M2, the sample endpoints, the event
   definition, the on-cycle rule, the covariate set or the diagnostic powers. Each
   would be a NEW lineage with its own trial accounting.
9. **No outcome may be used to choose anything.** Every choice in this contract is
   fixed now, from mechanism, official mechanics and literature.
10. **Evidence ceiling is `supported`.** The ETF panel is exposed (§Q).
11. **Fable and Astra are design-exposed** and may never be the sole blind independent
    certifier of this design or of any result under it (`TA_EXPOSURE_DISCLOSURE.md`).
12. **"Failed" is not a verdict.** The permitted outcomes are exactly A, B, C, D, I.

---

## §L Data — LOCKED

### L.1 Acquired and pinned under the S1 metadata authorisation

```
SOURCE     = U.S. Treasury Fiscal Data - "Treasury Securities Auctions Data"
ENDPOINT   = https://api.fiscaldata.treasury.gov/services/api/fiscal_service
             /v1/accounting/od/auctions_query
FILTER     = auction_date:gte:1990-01-01, auction_date:lte:2026-06-12,
             security_type:in:(Note,Bond)
FIELDS     = 13 metadata fields. AUCTION OUTCOME FIELDS (yields, prices,
             bid-to-cover, bidder allotments) WERE DELIBERATELY NOT REQUESTED.
RETRIEVED  = 2026-09-14T16:55:38Z
ROWS       = 2,373
RAW FILE   = data/ta/ta_auctions_raw.json   (git-ignored under the repository's
             data/ policy; pinned by sha256 here and in TA_DATA_MANIFEST.md)
RAW SHA256 = e807f06647c420f22f7654186e076cf15cebac2a6be7de16d8d1a5fbbcaba552
EVENT CALENDAR = research/extensions/ta/TA_EVENT_CALENDAR.csv, 557 rows (tracked)
EVENT CALENDAR SHA256 =
             b27be5b1d94cfc13fc8310e0d5216675e097a2245fc954e4b12ed282563f7cb6
BUILDER    = research/extensions/ta/ta_auction_fetch.py
```

The record is the issuer's own, announced in advance, and not revised: `t0` is
point-in-time by construction. The raw extract is fetched once and pinned; nothing
downstream re-reads a live endpoint.

### L.2 Declared, NOT acquired — the S2 macro-calendar contract

Required for §G.3 and for nothing else:

| calendar | authority |
|---|---|
| CPI news-release dates | U.S. Bureau of Labor Statistics official release-schedule archives |
| Employment Situation news-release dates | U.S. Bureau of Labor Statistics official release-schedule archives |
| FOMC post-meeting statement dates | Board of Governors of the Federal Reserve System official FOMC calendars |

Each is free and public. **Acquisition is NOT authorised by this contract**; it needs
a separate Owner data authorisation at S2, exactly as the VRP data contract did. The
scientific *definition* of each covariate is sealed above; only the access mechanics
are deferred, and mechanics cannot change a definition.

Failure to acquire any of the three is a **LEVEL-1 PRE-RUN FAILURE** (§P) — the sealed
design cannot execute. It is never silently skipped, and it never becomes an
assumption that the diagnostic would have passed.

### L.3 Forbidden data — unchanged

NY Fed dealer positions · ZN/ZB futures · when-issued Treasury prices · cash Treasury
returns · NAV data · CFTC data · any other new research dataset.

---

## §M Mechanical facts recorded at seal

### M.1 Tenor-family row counts on the pinned record, 1990-01-01 … 2026-06-12

`2-Year` 422 · `5-Year` 390 · `10-Year` 317 · TIPS 265 · `3-Year` 261 ·
`30-Year` 245 · `7-Year` 233 · FRN 151 · `20-Year` 74 · plus 11 rows in four residual
`original_security_term` spellings (`5-Year 2-Month` 4, `4-Year` 4,
`29-Year 9-Month` 4, `30-Year 3-Month` 3) which belong to no mapped family and enter
nothing.

### M.2 The five secondary rows dropped by the on-cycle rule

| auction date | `security_term` |
|---|---|
| 2008-10-08 | 6-Year 7-Month |
| 2008-10-08 | 6-Year 10-Month |
| 2008-10-09 | 6-Year 4-Month |
| 2008-10-09 | 9-Year 4-Month |
| 2019-11-05 | 3-Year |

All are off-cycle reopenings of seasoned notes. Zero primary rows are dropped.

### M.3 The single secondary window overlap

`2019-06-12` window `[2019-06-04 .. 2019-06-19]` and `2019-06-21` window
`[2019-06-13 .. 2019-06-28]`, seven grid days apart, same CUSIP `9128286T2`. Both are
retained.

---

## §N Verified external mechanics and literature — PRIOR ONLY, NEVER EVIDENCE

### N.1 Market mechanics

Competitive bidding closes 1:00 p.m. ET; Treasury targets a two-minute release of
results; 10-, 20- and 30-year auctions fall in the second week of the month, with
original issues in Feb/May/Aug/Nov and reopenings in the other eight months; 10-year
notes and 30-year bonds settle on the 15th. 30-year issuance gap 2001-08 → 2006-02;
20-year suspension 1986-06 → 2020-05.

### N.2 Literature prior

Fleming, Liu & Nguyen, FRBNY Staff Report 1188 (Mar 2026, rev. Jul 2026); Lou, Yan &
Zhang, *RFS* 26(8) 1891–1912 (2013); Somogyi, Wallen & Xu, HBS WP 26-033 (2 Dec 2025).
Their magnitudes, t-statistics and Sharpe ratios are **not imported as programme
evidence** and appear nowhere in §E, §I or §J. They fixed the window pair and the
predicted sign, and nothing else. `TA_S0_FRAME.md` §B carries the full verified
extracts.

---

## §O Stop rule — SEALED, EXHAUSTIVE

A verdict in §I ends this lineage. Specifically:

- **Class C is TERMINAL.** An `UNRESOLVED / LOW POWER` result is a complete answer.
  Reaching for a wider window, a later sample, another ETF, a filter, a threshold
  tweak or a parameter search to avoid writing it down is forbidden.
- **Class A and Class B are TERMINAL** for this construction.
- **Class I** ends the lineage and hands the Owner one decision: park, or open a
  genuinely new lineage with a design capable of the identification this one lacked.
- **Class D** permits nothing beyond recording `supported`. It is not deployment
  readiness, not a portfolio decision, and not an authorisation of anything.
- The historical study runs **ONCE**, under a single-use Owner execution
  authorisation that does not yet exist.

---

## §P Failure levels — separate from the verdict classes

```
LEVEL 1  PRE-RUN DESIGN / DATA FAILURE
         sealed hashes do not reproduce; the macro calendars cannot be acquired;
         the common-grid assertion fails; the event calendar cannot be rebuilt
         identically.
         => the design cannot execute. NO run, NO verdict, NO trial spent.

LEVEL 2  IMPLEMENTATION FAILURE
         the S2 acceptance contract (§T.2) does not pass.
         => no run. NO trial spent.

LEVEL 3  VERDICT  =  exactly one of CLASS A / B / C / D / I.
         A governed run spends its trial whatever the class.
```

---

## §Q Evidence context, sample reuse, trial accounting — LOCKED

```
SAMPLE            = dataset.yfinance.multi-asset-etf-panel (KB-1), burned 6 of 6,
                    carrying must_not_be_retested_on_same_sample
EVIDENCE CONTEXT  = T0 -- dependent evidence on an exposed panel
EVIDENCE CEILING  = SUPPORTED.  Never confirmed, never independently confirmed.
DESIGN PROVENANCE = the design was taken from EXTERNAL literature and an EXTERNAL,
                    official auction calendar. The auction-conditioned statistic has
                    never been computed on this panel by anyone. The panel is
                    nonetheless exposed, and the ceiling stands regardless.
N_trials          = NOT ASSERTED. D-ETF-COUNT remains OPEN
                    (UNKNOWN_PENDING_AARON_DECISION). This design uses NO DSR and no
                    trial-count deflation, so it is not blocked on that decision, and
                    that decision is NOT taken here.
HYPOTHESIS_FAMILY = F-TA, declared in TRIAL_LEDGER.md section 6.2 BEFORE any member
                    has run.
```

---

## §R Secondary and parked questions

### R.1 The dealer / intermediation cell — PARKED

`SECONDARY_DEALER_CELL = PARK`. Not part of primary success, not a prerequisite for
classifying the reduced-form claim, and not acquired (§L.3). Un-parking needs all of:
a Class-D primary; an Owner decision to establish the mechanism rather than harvest
the effect; and a bridging rule for the NY Fed series breaks fixed in advance of any
conditioned outcome.

### R.2 Declared descriptive outputs — every one `PROMOTION_POWER = NONE`

D1 PRE and POST leg means · D2 auction-day bar mean · D3 original-issue vs reopening
split · D4 `AC_SIMPLE` · D5 per-year mean `AC_NET` · D6 LOYO calendarised Sharpe by
year · D7 SHY maturity gradient · D8 own-announcement-in-window tabulation ·
D9 the §G.3 covariate cross-tabulation.

None may be promoted, none may rescue, none may kill, and none is a hypothesis.

---

## §S Prohibited outcome access — statement of record at seal

At S1 and at this seal, for this lineage: **no** ETF event return, `AC`, leg return,
auction-day bar return, mean, interval, Sharpe, bootstrap replicate, P&L, portfolio
quantity or candidate statistic of any kind was computed, read, plotted or inferred.
No strategy engine exists. The only contact with the frozen panel was
`trading_calendar()`, which read the `Date` column and a **non-null presence mask**
for TLT, IEF, SHY and SPY and retained no numeric value. The protected C-A store, key,
position and return layers were **not** touched and no C-A quantity was computed.
Canonical TSMOM was not modified. No external outcome dataset was opened.

---

## §T Gate ordering and prerequisites

### T.1 What this seal does and does not authorise

```
S1 SEALED                    = YES
S2 BUILD AUTHORIZED          = NO   (needs controller / Owner acceptance of this seal)
MACRO CALENDAR ACQUISITION   = NO   (separate Owner data authorisation at S2)
REAL RUN AUTHORIZED          = NO   (separate single-use Owner execution authorisation)
REVEAL AUTHORIZED            = NO   (separate single-use Owner reveal authorisation)
```

A seal is not authorisation to execute. A spent authorisation is never reusable.

### T.2 Mandatory S2 implementation-acceptance items (defined now, executed later)

1. Rebuild `TA_EVENT_CALENDAR.csv` from the pinned raw extract and reproduce
   sha256 `b27be5b1…7cb6` exactly.
2. Re-assert the common-grid identity for TLT, IEF, SHY and SPY; fail closed if it
   does not hold.
3. Assert the sealed counts: **213** primary valid windows, **0** primary overlaps,
   **max 1** primary event per calendar month, **244** months in `MONTH_GRID` with
   **31** zero months, **21** primary calendar years; **258** secondary valid windows.
4. **BEHAVIOURAL ASSERTION — exposure is ZERO across the auction-day bar.** A fixture
   must carry a large non-zero move on `GRID[i-1] -> GRID[i]` and prove the engine's
   P&L is unaffected by it. The fixture must be shown to be discriminating by
   reproducing a deliberate short-to-long-flip implementation and requiring a stated
   separation. (Programme lesson: assert what the object must *do*, not what the
   formula looks like.)
5. **BEHAVIOURAL ASSERTION — direction.** The PRE leg must LOSE when the instrument
   rises over the pre window, and the POST leg must GAIN when it rises over the post
   window.
6. **Report the §G.3 covariate cross-tabulation — counts only, no returns — BEFORE any
   `AC` is computed**, and state whether the reference group reaches 20 events, so
   Class-D reachability is known while the lineage is still outcome-blind.
7. Assert that `COST_BPS = 8.0` is applied exactly once per event per instrument.
8. Assert the seed protocol reproduces bit-identically from the sealed constants.
9. Prove the classification function in §I is total and single-valued over a synthetic
   sweep of the five bounds, and that no diagnostic can upgrade any class to D.

### T.3 Seal self-check — ten questions, every answer required to be NO

| # | question | answer |
|---|---|---|
| 1 | Does any threshold in this contract remain undefined? | **NO** |
| 2 | Is there any choice a builder must make after seeing an outcome? | **NO** |
| 3 | Can two verdict classes both apply to one result? | **NO** (§I.2 is ordered and verified disjoint) |
| 4 | Is any verdict class unreachable by construction? | **NO** — D is reachable; its dependence on the §G.3 reference group is a disclosed data risk with an outcome-free S2 pre-check, not a construction defect |
| 5 | Can any diagnostic promote, upgrade or rescue? | **NO** (§G, §J) |
| 6 | Does SHY retain any kill or damage power anywhere? | **NO** (§G.1) |
| 7 | Does any text describe a short-to-long flip across `t0`? | **NO** (§E.1) |
| 8 | Is the Sharpe annualisation ambiguous? | **NO** (§F.2, fixed monthly calendarisation, ×√12) |
| 9 | Is any sample rule outcome-selected? | **NO** (§B.5) |
| 10 | Has any candidate outcome been accessed? | **NO** (§S) |

---

```
END OF CONTRACT. SEALED. NO BUILD. NO RUN. NO REVEAL. NO RUN AUTHORIZATION.
```
