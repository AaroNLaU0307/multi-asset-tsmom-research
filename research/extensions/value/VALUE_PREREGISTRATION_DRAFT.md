# TIME-SERIES VALUE — PREREGISTRATION (**SEALED**)

```
VALUE_PREREG_SEALED = YES
VALUE_PREREG_SEAL_DECISION = AARON OWNER DECISION, 2026-09-13 —
                             SEAL TIME-SERIES VALUE S1
VALUE_FULL_PERFORMANCE_EXECUTED = NO
TARGET_OUTCOMES_COMPUTED = NO
STATUS = SEALED. The scientific content below is frozen. D1-D11 are Owner
         decisions and no alternative threshold may be introduced after this
         seal. Nothing below has been run.
OWNER_DECISIONS_REMAINING = NONE
ACCEPTED_DESIGN_REVISION = 4c31add4cd7f927952139715206029ae70fb4e3b
                           (the bytes Aaron reviewed and accepted; the original
                           seal changed status metadata only)
AMENDMENTS = VALUE_S1_DATA_IDENTITY_AMENDMENT_001 (2026-09-13) — see §16.
             VALUE_S1_COMPARATOR_IDENTITY_AMENDMENT_002 (2026-09-13) — see §17.
             ORIGINAL_SEAL_REVISION = ba5814d8dad2b81f28d45a0b6df7c010ef4c052f
             ORIGINAL_SEALED_PREREG_SHA256 =
               df142f83d82996f1df87d7953c1480397e4d128c8b32d599e31237901b3278cf
             AMENDMENT_001_SEAL_REVISION =
               5812997229eafe2184fe68193856bea2fa41eeae
             AMENDMENT_001_SEALED_PREREG_SHA256 =
               bc841ea80dd1afd521d8ecd2dc656b3e608396f4dd6546eab9c7b809ca67a099
             LINEAGE = original seal → AMENDMENT_001 → AMENDMENT_002
             The original seal is NOT erased; this document supersedes it and
             its lineage is preserved above and in §16 and §17.
```

**Research family:** `FINANCIAL_ASSET_TIME_SERIES_VALUE`
**Anchor:** `EXPANDING_OWN_HISTORY` (accepted at S0; not reopened)
**Workflow:** `QUANT_WORKFLOW_VNEXT`, stage S1 DESIGN+SEAL
**Data record:** [`VALUE_DATA_INVENTORY.json`](VALUE_DATA_INVENTORY.json) ·
[`VALUE_PHASE_A_CLOSURE.md`](VALUE_PHASE_A_CLOSURE.md)

---

## 1. Question and economic premise

Does greater fundamental cheapness of a financial asset **relative to its own
prior history** predict higher subsequent excess returns at comparable risk
scale — and if so, does a sleeve built on that idea add anything to a portfolio
that already runs the frozen TSMOM strategy?

This is a coherent research *family*, not a claim that one common economic driver
operates across all five instruments. The study is explicitly **two separate
objects**, and they must never be collapsed:

| object | question |
|---|---|
| **A — `VALUE_STANDALONE_EDGE`** | does the Value sleeve have a standalone edge? |
| **B — `VALUE_DIVERSIFICATION_CANDIDACY`** | is it eligible to be combined with TSMOM? |

Passing B establishes nothing about A.

## 2. Universe and valuation objects — FROZEN

Five instruments, four conceptual objects.

| instrument | object | raw series | orientation (higher = cheaper) |
|---|---|---|---|
| **SPY** | equity valuation | Shiller `ie_data.xls`, CAPE column | `+1 / CAPE` (real earnings yield) |
| **TLT** | duration / real-yield valuation | FRED `DFII20` | `+DFII20` (higher real yield = cheaper) |
| **LQD** | **public corporate credit valuation component** | FRED `BAA10Y` | `+BAA10Y` (wider spread = cheaper) |
| **UUP** | FX real valuation, fixed USDX basket | 6 nominal FX + 7 CPIs | `−R_USD` (see §2.2) |
| **FXY** | FX real valuation, bilateral JPY | `DEXJPUS` + US & JP CPI | `+R_USD|JPY` (see §2.2) |

### 2.1 Credit — an explicit redefinition, frozen

```
CREDIT_OBJECT = BAA10Y      (Moody's seasoned Baa yield − 10y Treasury CMT)
LQD = INCLUDED              HYG = REMOVED_FROM_VALUE_UNIVERSE
DESCRIPTION = PUBLIC_CORPORATE_CREDIT_VALUATION_COMPONENT
```

This is **not** an option-adjusted spread, **not** LQD/HYG Value and **not**
high-yield Value, and no result may be described in those terms. The original
ICE BofA OAS objects are unavailable under a licence that prohibits
reproduction. `BAA_MINUS_AAA` is **not an active fallback** — see §10.

### 2.2 FX orientation — derived, not assumed

Define the USD real exchange rate against foreign currency *f*:

```
R_USD,f (t) = S_f(t) · P_US(t) / P_f(t)        S_f = units of f per USD
```

A rising `R_USD` means the USD buys more foreign goods, i.e. the USD is **rich**.
Verified on synthetic values (`S=100→120`, `P_US=110`, `P_f=100` gives
`Q=110→132`), so:

- **UUP** is long USD ⇒ object `= −R_USD,basket` (higher ⇒ USD cheaper).
- **FXY** is long JPY ⇒ object `= +R_USD,JPY` (USD rich ⇔ JPY cheap).

#### 2.2.1 Exact formulae — FROZEN, no implementation discretion

At month-end *t*, with the §3.2 cut-offs applied (FX at *t* − 1 business day,
price levels at reference month *t* − 2):

**Nominal orientation.** Let `q_f(t)` be the quoted FRED rate. Then

```
S_f(t) = q_f(t)                      for DEXJPUS, DEXCAUS, DEXSDUS, DEXSZUS
                                     (already foreign units per USD)
S_f(t) = 1 / q_f(t)                  for DEXUSEU, DEXUSUK
                                     (quoted USD per foreign unit -> inverted)
```

**Bilateral real USD rate, in logs:**

```
r_f(t) = log S_f(t) + log P_US(t−2) − log P_f(t−2)
```

**Basket aggregation — weighted geometric mean, i.e. a weighted mean of logs:**

```
r_basket(t) = Σ_f  w_f · r_f(t)
w = { EUR 0.576, JPY 0.136, GBP 0.119, CAD 0.091, SEK 0.042, CHF 0.036 },  Σ w_f = 1
```

This matches the geometric construction of the USDX the traded proxy follows. A
changing-weight BIS effective index is **forbidden**: it is a different economic
object.

**The two Value objects:**

```
x_UUP(t) = − r_basket(t)          (long USD  -> higher = USD cheaper)
x_FXY(t) = + r_JPY(t)             (long JPY  -> USD rich <=> JPY cheap)
```

**Why logs.** A reference-base change multiplies a price index by a constant over
its whole history, which is an *additive* constant in logs. The expanding
*z*-score subtracts its own mean, so a uniform additive shift cancels exactly and
the base becomes irrelevant. Levels would not have this property. The seven
economies therefore need no base harmonisation beyond §3.

## 3. Sources, provenance and PIT status — FROZEN

Raw snapshots live in `data/value_raw/` (git-ignored) and are pinned by
`sha256_of_raw_file_on_disk` in the inventory. Every file re-hashes.

| leg | source · series | coverage | PIT class |
|---|---|---|---|
| SPY CAPE | Shiller `shillerdata.com` `ie_data.xls` | 1871.01 → 2026.09 | `PIT_DATA_ACQUIRED_BUT_LIMITED` |
| TLT real yield | FRED `DFII20` | 2004-07-27 → 2026-09-10 | `PIT_READY` |
| LQD credit | FRED `BAA10Y` (+ `BAA`, `DGS10`) | 1986-01-02 → 2026-09-10 | `PIT_READY` |
| US CPI | FRED **`CPIAUCNS`** (NSA) | 1913-01 → 2026-08 | `PIT_FEASIBLE_WITH_DECLARED_LAG` |
| EUR CPI | Eurostat `prc_hicp_minr`, `coicop18=TOTAL`, `unit=I25` | **1999-12 → 2026-08, 321 numeric** (period labels run from 1996-01; see §16) | `PIT_FEASIBLE_WITH_DECLARED_LAG` |
| JPY CPI | e-Stat `statInfId=000040482943` (All items, code 0001) | 1970-01 → 2026-07 | `PIT_FEASIBLE_WITH_DECLARED_LAG` |
| GBP CPI | ONS `D7BT` | 1988-01 → 2026-07 | `PIT_FEASIBLE_WITH_DECLARED_LAG` |
| CAD CPI | StatCan `18-10-0004` | 1914-01 → current | `PIT_FEASIBLE_WITH_DECLARED_LAG` |
| SEK CPI | SCB **two-table Fixed CPI** — `KPI2020M1980`/`000007T9` then `KPI2020M`/`00000808` (§16) | 1980-01 → 2026-07, **559 numeric** | `PIT_FEASIBLE_WITH_DECLARED_LAG` |
| CHF CPI | SNB `plkopr`, `LD2010100` | 1921-01 → 2026-07 | `PIT_FEASIBLE_WITH_DECLARED_LAG` |
| nominal FX ×6 | FRED `DEX*` | 1971/1999 → 2026-09 | `PIT_READY` |

**Reference-base transitions are mechanical, not splices of convenience.**
Eurostat serves `I25` (2025=100) and `I15` (2015=100) over the *same*
1996-01→2026-08 span, so any rebasing is a single multiplicative constant
recoverable from the overlap. SCB publishes the whole 1980M01 history already on
the 2020=100 table, so no splice is needed at all. Japan's file is 2025-base with
history back to 1970-01 as published by the agency. In every case the index level
is used only through a **ratio to its own history**, so a base constant cancels.

### 3.1 Vintage limitation — FROZEN, and it is not cured by the lag

```
SHILLER_VINTAGE_STATUS =
  RECONSTRUCTED_HISTORICAL_SERIES_WITH_NON-VINTAGE_LIMITATION
SHILLER_PUBLICATION_LAG = 3 months (D1)
```

**Two different things, deliberately kept apart.**

| | what it is | what it fixes |
|---|---|---|
| **PUBLICATION_LAG** | the delay before a value for reference month *m* could have been *seen* | release timing, i.e. look-ahead from using a number before it existed |
| **HISTORICAL_REVISION / VINTAGE RISK** | the published value for month *m* later *changed* | **nothing — the lag does not address this at all** |

The 3-month lag in D1 fixes the first and leaves the second untouched. It must
never be written or implied that "a 3-month lag makes Shiller strictly PIT".
Shiller's file is rebuilt each month: trailing S&P earnings are revised after the
fact and the real series is deflated with the **current** CPI vintage, not the
vintage in force at the time. A CAPE value dated 1995-03 is today's estimate of
1995-03, not what an investor could have computed in 1995-03. No true vintage
archive is distributed.

**Scientific consequences, frozen:**

1. This is a known **T0 data limitation** on the SPY valuation input specifically;
   `DFII20`, `BAA10Y` and the `DEX*` rates are market quotes and are **not**
   revised, so they do not carry it.
2. A positive result may **not** be described as strict vintage-point-in-time
   confirmation. The permitted wording is that the result holds on a
   *reconstructed* historical series under a declared publication lag.
3. The limitation must appear in any reported claim that rests on the SPY object.
4. **No future Shiller snapshot may be selected after outcomes are seen.** The
   sealed file is pinned by SHA256 in the inventory
   (`044196dafe44c3030b2facbdea023975b3f6aa68b4e52f8f9bafc403e19589c1`); a later
   re-download is a different dataset and may not be substituted to improve a
   result.
5. CPI series are also revised and rebased; the same distinction applies to them,
   though their effect enters only through ratios (§3).

### 3.0 Seasonal-adjustment policy — FROZEN

```
CPI_SEASONAL_ADJUSTMENT_POLICY =
  ALL-ITEMS NOT-SEASONALLY-ADJUSTED PRICE INDEX FOR EVERY ECONOMY
```

A real exchange rate is a **ratio** of two price levels. Mixing a seasonally
adjusted numerator with a non-seasonally-adjusted denominator injects a spurious
seasonal cycle into the object itself, which the expanding *z*-score would then
treat as genuine valuation variation. One treatment is therefore used for all
seven economies.

| economy | series | all-items definition | SA / NSA | reference base | freq |
|---|---|---|---|---|---|
| US | FRED `CPIAUCNS` | CPI-U, All Items, U.S. city average | **NSA** | 1982-84 = 100 | monthly |
| Euro area | Eurostat `prc_hicp_minr`, `coicop18=TOTAL`, `unit=I25` | HICP overall index (ECOICOP v2) | **NSA** | 2025 = 100 | monthly |
| UK | ONS `D7BT` | CPI INDEX 00: ALL ITEMS | **NSA** | 2015 = 100 | monthly |
| Canada | StatCan `18-10-0004` | CPI, all-items, Canada | **NSA** | 2002 = 100 | monthly |
| Sweden | SCB `KPI2020M1980`/`000007T9` + `KPI2020M`/`00000808` (§16) | Fixed CPI, all items | **NSA** | 2020 = 100 | monthly |
| Switzerland | SNB `plkopr`, `LD2010100` | Landesindex der Konsumentenpreise, total | **NSA** | Dec 2010 = 100 | monthly |
| Japan | e-Stat `000040482943`, Group/Item `0001` | All items, Indices of Items, Japan | **NSA** | 2025 = 100 | monthly |

**The US series was corrected.** The previous inventory used `CPIAUCSL`, which is
seasonally adjusted and was the only SA series among the seven. It is replaced by
its official NSA counterpart `CPIAUCNS` (1913-01 → 2026-08, so no coverage is
lost; the US CPI leg never bound the evaluation window). The SA/NSA status was
established **mechanically**, not from the ticker convention alone: over
1990-2026 the month-of-year dispersion of month-on-month log changes is 0.00633
for `CPIAUCNS` against 0.00133 for `CPIAUCSL`, a factor of 4.7.

Japan's file comes from the *Indices of Items* time series, which is the NSA
series; e-Stat publishes its seasonally adjusted tables separately as 16-1 and
16-2, and those are **not** used. This correction is a measurement-consistency
decision made before any Value signal, return or performance quantity existed,
and was **not** chosen by inspecting signal behaviour.

### 3.2 Month-end information cut-off — one causal rule per raw series, FROZEN

The **observation date** and the **date the observation may enter a signal** are
different things. A value for reference month July may not be used at July
month-end if it was published in August.

At month-end *t*, the admissible value of each raw series is:

| raw series | observation unit | admissible at month-end *t* | lag |
|---|---|---|---|
| `DFII20` | business-daily quote | last quote dated ≤ *t* − 1 business day | 1 bd |
| `BAA10Y` (and `BAA`, `DGS10`) | business-daily quote | last quote dated ≤ *t* − 1 business day | 1 bd |
| `DEXUSEU`, `DEXJPUS`, `DEXUSUK`, `DEXCAUS`, `DEXSDUS`, `DEXSZUS` | business-daily quote | last quote dated ≤ *t* − 1 business day | 1 bd |
| `CPIAUCNS` (US) | monthly, reference month *m* | *m* ≤ *t* − 2 months | 2 mo |
| Eurostat `prc_hicp_minr` (EUR) | monthly, reference month *m* | *m* ≤ *t* − 2 months | 2 mo |
| e-Stat `000040482943` (JPY) | monthly, reference month *m* | *m* ≤ *t* − 2 months | 2 mo |
| ONS `D7BT` (GBP) | monthly, reference month *m* | *m* ≤ *t* − 2 months | 2 mo |
| StatCan `18-10-0004` (CAD) | monthly, reference month *m* | *m* ≤ *t* − 2 months | 2 mo |
| SCB two-table Fixed CPI (SEK) | monthly, reference month *m* | *m* ≤ *t* − 2 months | 2 mo |
| SNB `plkopr` (CHF) | monthly, reference month *m* | *m* ≤ *t* − 2 months | 2 mo |
| Shiller `ie_data.xls` CAPE | monthly, reference month *m* | *m* ≤ *t* − 3 months | 3 mo (D1) |

**Composite objects.** `UUP` and `FXY` mix daily FX with monthly CPI. The frozen
rule is: the nominal FX leg takes its *t* − 1 business day quote, and each price
level takes reference month *t* − 2. The resulting real rate is therefore a
deliberately mixed-frequency object, and that is stated rather than hidden. The
same alignment is used in every month, including the first and last.

The one-business-day market lag is **observed, not assumed**: on Sunday
2026-09-13 the latest `BAA10Y` and `DGS10` observation is Thursday 2026-09-10,
with Friday 2026-09-11 — a business day — absent. The two-month CPI rule is
deliberately conservative: every agency here publishes within ~2–4 weeks, so two
months clears first release and most routine revisions.

## 4. Signal grammar — FROZEN

At each month-end *t*, for each instrument *i*:

1. take the raw object `x_i(t)` using **only** values whose declared lag has
   elapsed as of *t* (§3.2);
2. orient so that **higher = cheaper** (§2);
3. standardise against its **own expanding history**:
   `z_i(t) = (x_i(t) − μ_i(1..t)) / σ_i(1..t)`, where `μ` and `σ` use every
   observation from the object's first available month through *t* inclusive,
   `σ` with `ddof = 1`; if `σ_i(1..t) = 0` the signal is `0`;
4. require at least `W` months of history (§12-D2), else the signal is `0`;
5. **primary signal is sign-only**: `s_i(t) = sign(z_i(t))`, with `sign(0) = 0`;
6. size by the existing core volatility-sizing and position-cap machinery,
   unchanged;
7. aggregate the five instruments at **equal risk weight** — one frozen low-DoF
   rule, no optimisation, no tilt;
8. apply the existing portfolio volatility target and gross cap, unchanged.

A **continuous** `z`-signal is a declared **descriptive secondary** with
`PROMOTION_POWER = NONE`. It may be reported beside the primary and may never
replace it.

### 4.1 Staleness and missing data — FROZEN shape, §12-D3 for the number

An object whose most recent lag-cleared observation is older than `S` months
(§12-D3) is **stale**: its signal becomes `0` and its risk is *not*
redistributed to the other instruments. A month with no observation at all is
treated identically. Forward-fill is permitted only *within* the staleness
window. There is no interpolation, no backfill and no proxy.

## 5. Costs — inherited, not tuned

Inherited unchanged from the ETF programme: **2.0 bps per unit turnover**, where
turnover is the sum of absolute changes in target weights at each monthly
rebalance. Rebalancing is **monthly at month-end**. A change in a fundamental
signal creates a trade exactly as any weight change does. A signal going stale
unwinds that instrument's position to zero at the next rebalance and is charged
at the same rate. No cost parameter is fitted.

## 6. Sample — FROZEN, derived mechanically

Derived from data availability, the §3.2 cut-offs and `W = 120`, using dates and
schema only. No return or signal was computed to obtain it.

| object | earliest formable month | first month with ≥ 120 own observations |
|---|---|---|
| SPY | 1881-11 | 1891-10 |
| TLT | **2004-07** | **2014-06** |
| LQD | 1986-01 | 1995-12 |
| UUP | 1999-01 | 2008-12 |
| FXY | 1971-01 | 1980-12 |

```
FIRST_COMMON_ELIGIBLE_SIGNAL_MONTH = 2014-06     (binds on TLT)
EVALUATION_START  = 2014-07   (first evaluable RETURN month)
EVALUATION_END    = 2026-05   (last evaluable RETURN month)
CALENDAR_MONTH_COUNT = 143
```

**TLT binds the start.** `DFII20` begins 2004-07, and 120 months of own history
first exist at month-end 2014-06, so the first evaluated return month is 2014-07.
This is stated plainly: **the common window begins in mid-2014**, and the warm-up
is *not* shortened to recover sample length, nor is the TLT construction switched
to the longer `DGS20 − EXPINF20YR` route, whose second leg is model-based and
revised.

**The end is bound by the ETF price panel, not by CPI timing.** The binding
constraint is `data/close_prices_raw.csv`, which ends **2026-06-12** — June 2026
has only 10 trading days and is incomplete, so the last *complete* return month
is **2026-05** (20 trading days). The earlier suggestion of 2026-07 is **not**
evaluable and is discarded; the end date is derived, not chosen for convenience.
All five tickers (`SPY`, `TLT`, `LQD`, `UUP`, `FXY`) are present in that panel.

For completeness, and stated **prospectively rather than as a current fact**: the
fundamental legs held today would, under §3.2, permit signals to be formed at
month-ends beyond the evaluation end. That is a statement about the fundamental
inputs already in hand, not a claim that any future month's ETF prices exist. It
changes nothing: the evaluation end is frozen at **2026-05**, and the panel is
deliberately **not** refreshed to extend the sample.

Monthly frequency; every decision at month-end *t*; the return is measured over
month *t* + 1.

## 7. Object A — standalone edge — FROZEN states

Let `μ_V` be the Value sleeve's net annualised Sharpe over the evaluation sample,
with a paired bootstrap interval `[L_V, U_V]` (§9).

```
L_V >  +0.15          -> SUPPORTED_POSITIVE_EDGE
U_V <  −0.15          -> MATERIALLY_ADVERSE
otherwise             -> UNRESOLVED_EDGE
```

`+E = +0.15` (D6) and `−F = −0.15` (D7) are FROZEN. **Zero alone is never the
boundary.** Both inequalities are **strict**, so a boundary touch is predetermined:
`L_V = +0.15` exactly, or `U_V = −0.15` exactly, is `UNRESOLVED_EDGE`. There is no
prose discretion after outcomes.

**Required wording.** Failure to establish `MATERIALLY_ADVERSE` means only that
materially adverse standalone performance **was not established** under this
rule. It does **not** mean adverse performance has been excluded from the
plausible interval, unless the interval itself establishes that.

## 8. Object B — diversification candidacy — FROZEN

```
PURPOSE = SCREEN_FOR_COMBINATION_ELIGIBILITY      (never CONFIRM_VALUE_FACTOR)
```

Three screens, all evaluated before any combination is computed:

- **C1** — Object A is **not** adjudicated `MATERIALLY_ADVERSE`.
- **C2** — dependence with the frozen TSMOM sleeve (**§17**) satisfies
  `ρ_upper ≤ 0.40`, where `ρ_upper` is the **upper bound of the 95% interval**
  for the Pearson correlation between the two monthly net-return series,
  computed by the bootstrap in §9.1 (D8). Adjudicating on the upper bound rather
  than the point estimate is the conservative choice: it refuses candidacy when
  dependence is merely *plausibly* high. The comparison is `≤`, so
  `ρ_upper = 0.40` exactly **passes**.
- **C3** — the **premise conditions survive** the preregistered
  leave-one-valuation-episode-out rule of §11: for each of the `k = 3`
  preregistered episodes, both **C1 and C2 are recomputed on the sample with
  that episode's calendar months deleted, and both must PASS**. C3 passes iff
  C1 ∧ C2 hold in **all three** jackknife cases.

If C1 ∧ C2 ∧ C3 hold, **exactly one** fixed-split combination test (§9) is
permitted. `UNRESOLVED_EDGE` **may** proceed. Passing candidacy never changes the
Object-A status and is never reported as evidence of a Value edge.

## 9. FULL stage and inference — FROZEN

**Primary estimand**

```
ΔS_combo = Sharpe(TSMOM + Value) − Sharpe(TSMOM)
```

at exactly **one** preregistered risk split (§12-D9), under comparable portfolio
risk budgets. No weight grid. No reallocation after seeing any result. `TSMOM`
is the frozen comparator identified in **§17**.

```
L_combo >  +0.10        -> SUPPORTED_INCREMENTAL_BENEFIT
U_combo <   0.00        -> INCREMENTAL_BENEFIT_ADVERSE
otherwise               -> INCREMENTAL_BENEFIT_NOT_ESTABLISHED
```

`+δ = +0.10` (D10) is FROZEN. Both inequalities are **strict**, so boundary
touches are predetermined: `L_combo = +0.10` exactly is `NOT_ESTABLISHED`, and
`U_combo = 0.00` exactly is `NOT_ESTABLISHED`. No prose discretion after
outcomes.

**Three distinct labels, deliberately.** They mean different things and may never
share a name:

| label | meaning |
|---|---|
| `SUPPORTED_INCREMENTAL_BENEFIT` | the interval lies wholly above the `+δ` margin |
| `INCREMENTAL_BENEFIT_ADVERSE` | **a strict adverse finding** — the interval lies wholly below zero, i.e. adding Value plausibly *hurt* |
| `INCREMENTAL_BENEFIT_NOT_ESTABLISHED` | **failure to demonstrate the `+δ` margin** — this is NOT evidence of harm |

Reporting `NOT_ESTABLISHED` as though it were `ADVERSE`, or vice versa, is
forbidden.

### 9.1 Bootstrap — one engine for all three interval statistics, FROZEN

**Inference** reuses the sealed X01 machinery, which is scientifically
appropriate because the estimand is the same shape — a paired difference of
Sharpe ratios on two monthly series over one common sample:

- paired resampling of the joint monthly observation vector (never independently);
- stationary bootstrap, Politis–Romano (1994);
- expected block length **12 months**, a prospective design convention anchored
  to the longest formation window — not a claim about where dependence ends;
- **10,000** replicates; `ΔS` recomputed per replicate;
- `numpy.random.SeedSequence(7).spawn(k)` in fixed arm order;
- invalid replicates discarded and counted, with a **9,500** valid floor;
- **95%** percentile interval, linear interpolation.

The **same** engine produces all three intervals — Object A's Sharpe, the C2
correlation, and the FULL `ΔS_combo` — so no statistic silently gets an IID
interval:

| | statistic | paired resampling unit |
|---|---|---|
| Object A | annualised net Sharpe of the Value sleeve, against a zero benchmark | the monthly Value return |
| C2 | Pearson correlation between the Value and frozen-TSMOM monthly net returns | the **joint pair** (Value, TSMOM) for that month |
| FULL | `ΔS_combo` | the joint vector (TSMOM, TSMOM+Value) for that month |

In every case: stationary bootstrap (Politis–Romano 1994), expected block length
**12 months**, **10,000** replicates, seed `SeedSequence(7).spawn(k)` in fixed arm
order, **95% percentile** interval with linear interpolation, invalid replicates
discarded and counted against a **9,500** valid floor. A replicate is invalid iff
the statistic is undefined on it — zero variance in either leg, or fewer than
**24 distinct calendar months** represented. Months are always resampled
**jointly**, never independently per series; an IID correlation interval is
explicitly forbidden.

No new inference engine is introduced. If a premise statistic later proves to
need an extension, the smallest required extension is stated at that point and
**not implemented before seal**.

## 10. Credit–duration overlap — DIAGNOSTIC ONLY, declared before any inspection

`BAA10Y` and `DFII20` may share macro drivers. A predeclared diagnostic may
report (a) the correlation between the frozen credit and duration `z`-signals and
(b) their sign-agreement rate.

```
ROLE = DIAGNOSTIC / CLAIM-INTERPRETATION ONLY
```

It may **not** switch `BAA10Y` to `BAA−AAA`, drop credit, change weights, alter
the grammar, or trigger any retuning. Strong overlap is recorded as a
**limitation** — lower effective object independence — and is never repaired.
This is declared here, before any historical overlap has been inspected.

## 11. Valuation episodes and effective sample

Value signals move slowly, so calendar months overstate independent information.
**Definition, fixed mechanically so it cannot be redrawn after outcomes:** for
each instrument, a *valuation episode* is a maximal run of consecutive months in
which `sign(z_i(t))` is constant. Episodes are computed from the signal path
alone and never from returns.

The definition uses **only** the frozen signal path. It may not use future
returns, PnL, Sharpe, drawdowns, or any later discretionary regime label.

**Episode selection, deterministic.** Episodes are pooled across the five
instruments and ranked by month count, **descending**, with ties broken by (1)
earlier start month, then (2) instrument name in the fixed order
`SPY, TLT, LQD, UUP, FXY`. That ordering is total, so the three largest episodes
are uniquely determined with no discretion.

### 11.1 The deletion operator — exactly one, FROZEN

For a selected episode *e*:

1. take `M(e)` = the set of calendar months belonging to *e*;
2. **delete those calendar months from the entire paired evaluation sample** —
   the Value sleeve series, the frozen TSMOM series (**§17**), and the
   combined series alike, so every statistic is recomputed on the *same*
   reduced set of common months;
3. recompute **C1** (the §7 standalone adjudication) and **C2** (the §8
   `ρ_upper ≤ 0.40` test) on the remaining months, using the §9.1 bootstrap
   unchanged;
4. the reduced sample must still satisfy the §9.1 validity floor; a jackknife
   case that cannot produce a valid interval counts as **FAIL**, never as a pass
   by default.

This operator does **not**: remove only the contributing instrument while keeping
the portfolio sample; replace an instrument; reweight the sleeve; redraw episode
boundaries; or use returns to define an episode. There is exactly one operator.

*Previously this section said C3 passed iff the primary point estimate's sign was
unchanged. That was weaker than the accepted structure — it adjudicated on a sign
rather than on whether the premise conditions survive — and it is replaced. The
sign-stability observation is retained below as a description with no
adjudicating power.*

**C3 pass rule (D11), FROZEN:**

```
C3 = PASS  iff  for every e in the 3 selected episodes:
                C1(sample \ M(e)) = PASS  AND  C2(sample \ M(e)) = PASS
```

**Descriptive only, no adjudication power:** the sign of the primary point
estimate in each jackknife case may be reported alongside, purely as commentary.
It cannot pass, fail, or modify C3.

## 12. Owner decisions — FROZEN

Aaron's decisions, carried forward unchanged. Each rationale is from mechanism,
algebra or existing programme convention. **No target outcome was inspected.**

| id | decision | frozen value | one-line rationale |
|---|---|---|---|
| **D1** | Shiller publication lag | **3 months** | S&P quarterly earnings finalise with a multi-month lag and CPI adds ~1; 3 clears both. Does **not** cure the vintage limitation (§3.1) |
| **D2** | expanding-history warm-up `W` | **120 months** | a decade of own history before a *z* is trusted, matching how slowly these objects move |
| **D3** | staleness limit `S` | **3 months** | every CPI leg publishes monthly within ~4 weeks; 3 tolerates one missed release plus the declared lag |
| **D4** | evaluation start | **2014-07** | mechanical consequence of D2 and `DFII20`'s 2004-07 start; no discretion |
| **D5** | evaluation end | **2026-05** | last *complete* month in the ETF panel, which ends 2026-06-12; derived, not chosen |
| **D6** | standalone positive margin `+E` | **+0.15** | reuses the materiality scale already adopted as an Owner tolerance in X01 |
| **D7** | materially-adverse floor `−F` | **−0.15** | symmetric with D6; asymmetry would need its own justification |
| **D8** | `ρ_max` and basis | **0.40, on the CI upper bound** | the upper bound is conservative — it refuses candidacy when dependence is merely plausibly high |
| **D9** | Trend/Value risk split | **75 / 25** | TSMOM is the incumbent with far stronger evidence; a minority Value allocation is the conservative single shot |
| **D10** | incremental margin `+δ` | **+0.10** | must exceed plausible estimation noise on a paired difference yet stay attainable (§13) |
| **D11** | episodes `k`, C3 rule | **k = 3; C3 passes iff C1 ∧ C2 both pass in all three leave-one-episode-out samples** (§11.1) | prevents one valuation episode from carrying the premise, tested on the conditions that actually gate the combination |

```
OWNER_DECISIONS_REMAINING = NONE
```

**Not** open, and deliberately so: the anchor, the universe, the credit object,
the sign-only grammar, the equal-risk aggregation, the cost convention, the
bootstrap mechanics, and the overlap diagnostic's role.

## 13. Reachability — checked before seal

With the recommended defaults, every branch must be attainable and no two
thresholds may be algebraically contradictory. See
[`value_reachability_check.py`](value_reachability_check.py); results are
recorded in §14.

## 14. Claim ceiling — FROZEN

```
EVIDENCE_CEILING = T0 / POST-EXPOSURE / AT_MOST_SUPPORTED
```

The ETF sample is reused and already outcome-exposed; new fundamental inputs do
**not** make it independent validation. Two possible positive statements exist
and **neither implies the other**:

- **A** — a supported standalone Value edge on this reused historical sample;
- **B** — a supported incremental portfolio benefit from adding this frozen
  valuation sleeve at this one preregistered allocation.

No result may establish independent Value confirmation, untouched
out-of-sample evidence, general Value efficacy, efficacy of any excluded sleeve
(`HYG`, `EEM`, `EWJ`, `XLE`, `XLU`, `SHY`, `USO`, `UNG`, `GLD`, `DBA`, `VNQ`,
`RWX`), futures Value, or deployment readiness.

## 15. Terminal outcomes — no automatic repair

- `MATERIALLY_ADVERSE` standalone → **stop**; no combination.
- Candidacy fails C1, C2 or C3 → **stop**; no combination.
- `UNRESOLVED_EDGE` with candidacy passing → exactly one combination test.
- `INCREMENTAL_BENEFIT_ADVERSE` → **stop**.
- `INCREMENTAL_BENEFIT_NOT_ESTABLISHED` → **stop**, `INSUFFICIENT_EVIDENCE`.

No parameter tweak, no alternate split, no structural-anchor rescue after seeing
expanding-anchor results, no automatic "Value v2". Any further work needs a
separate Owner decision and a genuinely new question.

---

## 16. `VALUE_S1_DATA_IDENTITY_AMENDMENT_001`

**Owner decision, 2026-09-13:** authorise the official SCB two-table Fixed-CPI
join for Sweden, and correct the euro-area numeric-coverage statement. A narrow
data-identity correction. No scientific choice is reopened.

**1. The originally sealed Swedish source identity had insufficient numeric
history.** `SCB KPI2020M` / `00000808` exposes 559 monthly period *labels* but
carries only **7 numeric observations**, 2026M01–2026M07. Every earlier month is
`".."`. The coverage recorded at seal — "1980M01 → 2026M07" — counted labels, not
values.

**2. S2 detected this before any target outcome was computed.** The build's data
validation failed on this leg; no Value return, signal, Sharpe, correlation,
combination outcome or verdict existed then or exists now.

**3. The Swedish scientific object is unchanged:**
`SWEDEN_ALL_ITEMS_FIXED_CPI_NSA`. **Shadow CPI is NOT used** — it is a different
official object and was explicitly rejected.

**4. The object is implemented through two official SCB Fixed-CPI tables across
the reference-year transition**, because no single table spans it:

| leg | table | code | description | numeric coverage |
|---|---|---|---|---|
| historical | `KPI2020M1980` | `000007T9` | Fixed CPI, index numbers 1980=100 rebased to 2020=100 | 1980-01 → 2025-12 (552) |
| current | `KPI2020M` | `00000808` | CPI, fixed index numbers | 2026-01 → 2026-07 (7) |

```
COMPOSITION (strict concatenation, frozen):
    month <= 2025-12  ->  KPI2020M1980 / 000007T9
    month >= 2026-01  ->  KPI2020M     / 00000808
```

Verified mechanically: `OVERLAP_MONTHS = 0`, `GAP_MONTHS_AT_JUNCTION = 0`,
`REFERENCE_BASE_MATCH = YES` (both 2020=100), `SEASONAL_ADJUSTMENT_MATCH = YES`
(both NSA), `OBJECT_DEFINITION_MATCH = YES` (both all-items Fixed CPI), composed
series contiguous 1980-01 → 2026-07 with 559 observations. The junction is
`2025-12 = 124.42 → 2026-01 = 124.58` on one basis. **No leg was rescaled, no
bridge factor estimated, nothing interpolated or averaged, and nothing spliced on
observed price behaviour.** The composed object never hides its two-source
provenance: both raw identities are pinned separately in the inventory.

**5. The euro-area coverage statement is corrected** from "1996-01 → 2026-08" to
its actual numeric coverage **1999-12 → 2026-08** (321 values across 368 period
labels) — the same label-counting error. This is a factual correction only: the
euro source, object, reference basis, lag, the real-FX formula and the evaluation
window are all unchanged, and the leg is usable from 2000-02, far before the
2014-07 start.

**6–8. Nothing else changed.** No `D1`–`D11` value, no evaluation window, no
signal, inference, portfolio, episode, C3 or verdict rule.

```

## 17. `VALUE_S1_COMPARATOR_IDENTITY_AMENDMENT_002`

**Owner decision, 2026-09-13:** pin the identity and provenance of the frozen
TSMOM comparator. A narrow specification repair. No scientific choice is
reopened and no previously decided value changes.

**1. The defect this section exists to correct.** §1, §8 (C2), §9 (FULL) and
§11.1 all consume "the frozen TSMOM sleeve", and the sealed text never
identified it — no universe, no construction, no module, no configuration, no
hash. Three of the four adjudicating screens depend on that object, so a reader
could not have reproduced `C2`, `C3` or `ΔS_combo` from the sealed bytes. The
S3 run gate halted on exactly this, **before** any authorization was created.

**2. State at the moment of this amendment, mechanically verified:**

```
VALUE_TARGET_RETURNS_COMPUTED     = NO
VALUE_SHARPE_COMPUTED             = NO
VALUE_TSMOM_CORRELATION_COMPUTED  = NO
COMBINATION_OUTCOME_COMPUTED      = NO
S3_AUTHORIZATION_CREATED          = NO
S3_AUTHORIZATION_CONSUMED         = NO
EVIDENCE_ARTIFACT_EXISTS          = NO
```

No Value outcome of any kind existed when this comparator was pinned, so the
choice cannot have been informed by one.

**3. The comparator, frozen:**

```
VALUE_TSMOM_COMPARATOR = CANONICAL_17_ETF_TSMOM_BASELINE
```

It is the project's already-accepted canonical multi-asset TSMOM book, frozen at
`TSMOM_EXTENSION_RESEARCH_MAP_v2.md` §A.1 *"The mechanism as implemented
(frozen)"*. Every element is **read from an authoritative artifact, not
inferred**, and a call-site argument or a Python default argument is never
treated as authority:

| element | frozen value | authority |
|---|---|---|
| universe | the canonical 17-ETF book | `universe.py::TICKERS`; MAP_v2 §A.1 |
| signal | mean-of-signs composite of the 1/3/6/12-month month-end returns; **sign first, mean second**; all four horizons required; `combine="mean"`; `np.sign(0)=0`; resample `ME` | `src/signals.py::signal_method_b`; **X01 §3.7** (SEALED, pinned to implementer-equality); MAP_v2 §A.1 |
| sizing | `w = score × 0.10 / σ_60d`, clipped to ±2.0 | `src/sizing.py::target_weights`; `config.TARGET_VOL_ANNUAL`, `MAX_ASSET_WEIGHT`, `VOL_WINDOW_DAYS` |
| aggregation | equal weight over available assets, `base_i = w_i / N_live` | `src/portfolio.py::equal_weight_aggregate`, which the module itself declares the main strategy and names the alternatives CONTROL experiments |
| portfolio risk | `L = min(0.10 / σ_60d(base book), 3.0 / gross_base)` | `src/portfolio.py::leverage`; `config.PORT_TARGET_VOL_ANNUAL`, `PORT_VOL_WINDOW_DAYS`, `MAX_GROSS_LEVERAGE` |
| timing | decision at month-end *t*, held through *t+1* (`shift(1)`) | `src/sizing.py::positions_from_weights`; MAP_v2 §A.1 |
| costs | **2.0 bps** one-way per unit turnover on `Σ|Δposition|` | `src/performance.py`; `config.TRANSACTION_COST_BPS` — the same convention §5 already inherits for the Value sleeve |
| eligibility | a return month counts only when the decision month carried all 17 weights | `run_backtest.py`, the canonical full-universe rule |
| return basis | **NET** monthly returns | §9 compares net to net |
| price panel | `data/close_prices_raw.csv`, SHA256 `3d2a7a56dbd92d4ff8138cfd894c87f5ac5ac088a11165db870673e0c05c3c31` | the identical pin carried by the **SEALED X01 contract**; verified matched on disk |

The 17 instruments are exactly the union of this contract's §2 partition —
the five valued instruments plus the twelve excluded ones:

```
SPY EEM EWJ XLE XLU TLT SHY LQD HYG USO UNG GLD DBA UUP FXY VNQ RWX
```

That the partition reproduces the book exactly is checked mechanically, and a
mismatch is a hard error: the study and its comparator must describe one world.

**4. This is NOT X01's E arm, and the distinction is deliberate.** X01's E arm
shares this signal definition, this panel pin and this cost convention, but it
restricts to the four commodity ETFs and **removes the portfolio-level
volatility target and gross cap**, because those "depend on the other four
sleeves and would inject non-commodity information into a commodity wrapper
test". This contract needs the opposite object: §4 step 8 keeps "the existing
portfolio volatility target and gross cap, unchanged", and §1 asks about a
portfolio "that already runs the frozen TSMOM strategy" — the whole book.
Reusing X01's E arm here would silently substitute a four-asset commodity
sleeve for the incumbent portfolio.

**5. The comparator is RECOMPUTED, never read from an untracked file.** Its
authority is this frozen construction path applied to the hash-pinned panel by
the hash-pinned canonical modules — implemented at
[`value_comparator.py`](value_comparator.py), which passes every canonical
argument explicitly and refuses to run if the panel or any canonical module has
moved. `output/monthly_returns.csv` is **git-ignored and carries no hash**; it
is a historical convenience artifact and is **NOT** the scientific authority
here. That it agrees with the recomputation at the full precision it was written
to is recorded as a corroborating diagnostic only.

**6. Nothing else changed.** No `D1`–`D11` value, no evaluation window
(`2014-07 → 2026-05`, `N = 143`), no source, no lag, no Value object, signal,
staleness, portfolio, cost, episode, bootstrap, C1/C2/C3, candidacy or verdict
rule, and no claim ceiling.

```
```
A SEAL IS NOT AUTHORIZATION TO EXECUTE. This contract is SEALED and its
scientific content is frozen. S2 BUILD may implement it without changing it.
Nothing may be RUN until Aaron separately authorizes one real execution, and no
such authorization exists.

NEXT GATE = S2 BUILD — IMPLEMENT THE SEALED CONTRACT WITHOUT CHANGING IT
```
