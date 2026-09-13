# TIME-SERIES VALUE — PREREGISTRATION **DRAFT** (UNSEALED)

```
VALUE_PREREG_SEALED = NO
VALUE_FULL_PERFORMANCE_EXECUTED = NO
TARGET_OUTCOMES_COMPUTED = NO
STATUS = S1 DESIGN IN PROGRESS — awaiting Aaron's resolution of the open decisions
         in §12, then his seal. Nothing below has been run.
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

`R_USD,basket` uses the **fixed USDX weights of the traded proxy** — EUR 0.576,
JPY 0.136, GBP 0.119, CAD 0.091, SEK 0.042, CHF 0.036 (sum 1.000) — as a
weighted geometric mean of the six bilateral `R_USD,f`. A changing-weight BIS
effective index is **forbidden**: it is a different economic object.

`DEXUSEU` and `DEXUSUK` are quoted USD-per-foreign and **must be inverted**;
`DEXJPUS`, `DEXCAUS`, `DEXSDUS`, `DEXSZUS` are already foreign-per-USD.

## 3. Sources, provenance and PIT status — FROZEN

Raw snapshots live in `data/value_raw/` (git-ignored) and are pinned by
`sha256_of_raw_file_on_disk` in the inventory. Every file re-hashes.

| leg | source · series | coverage | PIT class |
|---|---|---|---|
| SPY CAPE | Shiller `shillerdata.com` `ie_data.xls` | 1871.01 → 2026.09 | `PIT_DATA_ACQUIRED_BUT_LIMITED` |
| TLT real yield | FRED `DFII20` | 2004-07-27 → 2026-09-10 | `PIT_READY` |
| LQD credit | FRED `BAA10Y` (+ `BAA`, `DGS10`) | 1986-01-02 → 2026-09-10 | `PIT_READY` |
| US CPI | FRED `CPIAUCSL` | 1947-01 → 2026-08 | `PIT_FEASIBLE_WITH_DECLARED_LAG` |
| EUR CPI | Eurostat `prc_hicp_minr`, `coicop18=TOTAL`, `unit=I25` | 1996-01 → 2026-08 | `PIT_FEASIBLE_WITH_DECLARED_LAG` |
| JPY CPI | e-Stat `statInfId=000040482943` (All items, code 0001) | 1970-01 → 2026-07 | `PIT_FEASIBLE_WITH_DECLARED_LAG` |
| GBP CPI | ONS `D7BT` | 1988-01 → 2026-07 | `PIT_FEASIBLE_WITH_DECLARED_LAG` |
| CAD CPI | StatCan `18-10-0004` | 1914-01 → current | `PIT_FEASIBLE_WITH_DECLARED_LAG` |
| SEK CPI | SCB `KPI2020M`, `00000808` | 1980M01 → 2026M07 | `PIT_FEASIBLE_WITH_DECLARED_LAG` |
| CHF CPI | SNB `plkopr`, `LD2010100` | 1921-01 → 2026-07 | `PIT_FEASIBLE_WITH_DECLARED_LAG` |
| nominal FX ×6 | FRED `DEX*` | 1971/1999 → 2026-09 | `PIT_READY` |

**Reference-base transitions are mechanical, not splices of convenience.**
Eurostat serves `I25` (2025=100) and `I15` (2015=100) over the *same*
1996-01→2026-08 span, so any rebasing is a single multiplicative constant
recoverable from the overlap. SCB publishes the whole 1980M01 history already on
the 2020=100 table, so no splice is needed at all. Japan's file is 2025-base with
history back to 1970-01 as published by the agency. In every case the index level
is used only through a **ratio to its own history**, so a base constant cancels.

### 3.1 Vintage limitation that must be stated in any result

Shiller's CAPE history is **reconstructed, not vintage**: trailing earnings are
revised and the real series is deflated with the *current* CPI vintage. A declared
publication lag makes the construction causal with respect to *release timing*
only. A CAPE value dated 1995-03 is today's estimate of 1995-03, not what an
investor could have computed then. CPI series are likewise revised (US CPI is
seasonally adjusted and restated). `DFII20`, `BAA10Y` and the `DEX*` rates are
market quotes and are **not** revised.

### 3.2 Publication lag — FROZEN where mechanically determined

| leg | lag rule |
|---|---|
| `DFII20`, `BAA10Y`, `DEX*` | value dated ≤ *t* − 1 business day |
| all CPI legs | value for reference month *m* is usable only from *m* + 2 calendar months |
| Shiller CAPE | §12-D1 (open) |

The one-business-day market lag is **observed, not assumed**: on Sunday
2026-09-13 the latest `BAA10Y` and `DGS10` observation is Thursday 2026-09-10,
with Friday 2026-09-11 absent. The two-month CPI rule is deliberately
conservative: every agency here publishes within ~2–4 weeks, so two months clears
first release and most routine revisions.

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

## 6. Sample

- **Evaluation start:** §12-D4 (open) — driven by `W` and by the latest-starting
  object, `DFII20` (2004-07).
- **Evaluation end:** §12-D5 (open) — recommended **2026-07**, the earliest
  last-observation across the CPI legs.
- Monthly frequency; all decisions at month-end; returns measured on the
  following month.

## 7. Object A — standalone edge — FROZEN states

Let `μ_V` be the Value sleeve's net annualised Sharpe over the evaluation sample,
with a paired bootstrap interval `[L_V, U_V]` (§9).

```
L_V > +E              -> SUPPORTED_POSITIVE_EDGE
U_V < −F              -> MATERIALLY_ADVERSE
otherwise             -> UNRESOLVED_EDGE
```

`+E` (§12-D6) and `−F` (§12-D7) are frozen before seal. **Zero alone is never the
boundary.** Endpoints are strict; an interval touching a boundary is
`UNRESOLVED_EDGE`.

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
- **C2** — dependence with the frozen TSMOM sleeve satisfies `ρ ≤ ρ_max`
  (§12-D8), on the adjudication basis fixed in §12-D8.
- **C3** — the episode-robustness rule of §11 passes.

If C1 ∧ C2 ∧ C3 hold, **exactly one** fixed-split combination test (§9) is
permitted. `UNRESOLVED_EDGE` **may** proceed. Passing candidacy never changes the
Object-A status and is never reported as evidence of a Value edge.

## 9. FULL stage and inference — FROZEN

**Primary estimand**

```
ΔS_combo = Sharpe(TSMOM + Value) − Sharpe(TSMOM)
```

at exactly **one** preregistered risk split (§12-D9), under comparable portfolio
risk budgets. No weight grid. No reallocation after seeing any result.

```
L_combo > +δ                      -> SUPPORTED_INCREMENTAL_BENEFIT
U_combo < 0                       -> INCREMENTAL_BENEFIT_ADVERSE
otherwise                         -> INCREMENTAL_BENEFIT_NOT_ESTABLISHED
```

`+δ` is §12-D10. **Three distinct labels are used deliberately.**
`INCREMENTAL_BENEFIT_ADVERSE` is a strict adverse finding (the interval lies
wholly below zero). `INCREMENTAL_BENEFIT_NOT_ESTABLISHED` means only that the
positive margin was not demonstrated. Conflating those two is forbidden.

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

For Object A the same machinery is applied to the single Value series against a
zero benchmark. No new inference engine is introduced. If any premise statistic
later proves to need an extension, the smallest required extension is stated at
that point and **not implemented before seal**.

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

Leave-one-episode-out robustness: recompute the primary statistic omitting each
of the *k* largest episodes by month count (§12-D11 fixes *k*). This is a
**bounded diagnostic**, not a regime framework and not a gate — except as it
enters C3, whose pass rule is fixed in §12-D11.

## 12. `OWNER_DECISIONS_REQUIRED_BEFORE_SEAL`

Recommendations come from mechanism, algebra or existing programme convention.
**No target outcome has been inspected.**

| id | decision | options | recommended default | rationale |
|---|---|---|---|---|
| **D1** | Shiller CAPE publication lag | 2 / **3** / 4 months | **3 months** | S&P quarterly earnings finalise with a multi-month lag and CPI adds ~1; 3 clears both without being punitive |
| **D2** | expanding-history warm-up `W` | 60 / **120** / 180 months | **120 months** | a decade of own history before a *z* is trusted; matches the slow-moving nature of these objects and is common in the literature |
| **D3** | staleness limit `S` | 2 / **3** / 6 months | **3 months** | every CPI leg publishes monthly within ~4 weeks; 3 tolerates one missed release plus the declared lag without carrying dead information |
| **D4** | evaluation start | data-driven | **first month-end with ≥ W history on every object**, given `DFII20` starts 2004-07 | mechanical consequence of D2; no discretion |
| **D5** | evaluation end | **2026-07** / 2026-06 | **2026-07** | earliest last-observation across the CPI legs; not forced to 2025-12 |
| **D6** | standalone positive margin `+E` | 0.10 / **0.15** / 0.20 Sharpe | **0.15** | reuses the X01 materiality scale already adopted as an Owner tolerance |
| **D7** | materially-adverse floor `−F` | −0.10 / **−0.15** / −0.25 | **−0.15** | symmetric with D6; asymmetry would need its own justification |
| **D8** | `ρ_max` and adjudication basis | 0.3 / **0.4** / 0.5; point estimate **or** CI upper bound | **0.4, adjudicated on the CI upper bound** | the upper bound is the conservative reading — it refuses candidacy when dependence is merely *plausibly* high |
| **D9** | Trend/Value risk split | **75/25** / 70/30 / 50/50 | **75/25** | TSMOM is the incumbent with far stronger evidence; a minority Value allocation is the conservative single shot |
| **D10** | incremental margin `+δ` | 0.05 / **0.10** / 0.15 Sharpe | **0.10** | must exceed plausible estimation noise on a paired difference yet stay attainable; see §13 |
| **D11** | episode diagnostic `k` and C3 pass rule | k ∈ {1,2,3}; rule | **k = 3; C3 passes if the primary sign is unchanged for all 3** | prevents one episode carrying the conclusion without becoming a regime model |

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

```
A SEAL IS NOT AUTHORIZATION TO EXECUTE. This contract is a DRAFT. Nothing may be
run until Aaron resolves §12 and seals it, and then separately authorizes one
execution.

NEXT GATE = AARON — RESOLVE §12 AND SEAL, OR AMEND
```
