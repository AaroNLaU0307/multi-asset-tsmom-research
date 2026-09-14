# TSMOM-VRP-01 — PREREGISTRATION CONTRACT (S1 DESIGN + SEAL)

```
LINEAGE                 = TSMOM-VRP-01
CONTRACT_ID             = TSMOM-VRP-01-PREREG-01
STATUS                  = SEALED BY THE S1 SEAL MANIFEST (VRP_SEAL_MANIFEST.md); ACCEPTANCE PENDING (ChatGPT / Aaron)
LANE                    = FULL  (Stage A and Stage B are confirmatory claims about one frozen object)
S0                      = CLOSED  (2026-09-14-tsmom-vrp-01-s0-frame-fable-02-repaired.md,
                                   SHA256 53f2d094d6fa06358869dda88e77daa80e0feba22c7f9253f2649e622a70d03a)
OWNER_DECISIONS         = COMPLETE (2026-09-14-tsmom-vrp-01-owner-decision-record.md,
                                   SHA256 76232d6c29980c79ece2ba6ead744c203fcf6fa15a70b6045cca91c1d40b9be3)
S0-01 (historical only) = 2026-09-14-tsmom-vrp-01-s0-frame-fable-01.md, SHA256 622e85cfdd0f31bbf3bd16f815be6565c433b68bb46556f93fd63fe7878e6859
```

Both authoritative inputs live at the workspace root (`..\..\..\..` relative to this file, i.e. the directory containing `multi-asset-tsmom-research`). The S1 session recomputed both hashes before writing this contract and they matched. Every scientific value below is transcribed from those two documents; **nothing is reinterpreted or improved**. Where the two could have conflicted they were checked and do not.

## §0 Authority, provenance and standing facts

- **Aaron authorised S1 DESIGN + SEAL for TSMOM-VRP-01** on 2026-09-14. Aaron **delegated VRP-OD-2 through VRP-OD-9 to Fable**; those decisions are Owner decisions made under explicit delegation and are recorded in the Owner Decision Record.
- **Claude Fable 5.1 is a MATERIAL DESIGN CONTRIBUTOR** (Phase-C map, final adjudication, S0-01, S0-02-repaired, the delegated Owner decisions, this contract). **GPT-6 Astra is a MATERIAL DESIGN CONTRIBUTOR** (Phase-C independent map and the accepted S0 challenge). **Neither may later be represented as a fresh blind certifier** of this design or of any result under it.
- **ChatGPT (Aaron-side) acts as programme controller / acceptance checker.** Acceptance of this seal by ChatGPT / Aaron is the next gate; this contract does not accept itself.
- **Canonical 17-ETF TSMOM remains FROZEN.** Nothing in this contract modifies its signal, sizing, aggregation, vol target, gross cap, cost convention or universe. Its scientific status remains `SUPPORTED — NOT INDEPENDENTLY CONFIRMED`; **no statement in this contract upgrades canonical TSMOM evidence.**
- **C-A remains LIVE / S3 PASSIVE ACCRUAL.** Protected C-A prospective positions, returns and outcomes are not accessed, computed, inferred or reconstructed by this lineage (§Q.3).
- **C-D remains CLOSED AT HOLD** and is not reopened.
- **This contract, seal and S1 package authorise nothing further:** not S2 build, not data acquisition, not any run, not any reveal. `S2_AUTHORIZED = NO`, `REAL_RUN_AUTHORIZED = NO`.

## §A The research object — LOCKED

**Object D.** A **standalone, unconditional, constant-maturity short position in listed monthly VIX futures**, with the following binding properties. Any material deviation is a new lineage.

| # | Binding property |
|---|---|
| A1 | Actual listed **monthly** VX futures contracts (the standard contract; the mini contract enters only the granularity check, §D.4) |
| A2 | **First and second eligible monthly contracts only** (§F) |
| A3 | **One-month constant weighted maturity** via the deterministic daily calendar roll of §F.3 |
| A4 | **Deterministic calendar roll** — weights are a function of the exchange calendar only |
| A5 | **Official exchange daily settlement prices** — never last trade, never the Special Opening Quotation as a daily pricing input |
| A6 | **Constant dollar VIX-point sensitivity per unit committed capital** (§D.2) — fixed within each calendar month |
| A7 | **No daily market-state exposure adjustment**; **no volatility scaling**; **no contango / backwardation filter**; **no timing rule**; **no loss-based de-risking**; no regime switch |
| A8 | **No alternative tenor**; **no weekly futures**; **no options**; **no variance-swap proxy** |
| A9 | **No modification to canonical TSMOM**; the frozen canonical stream enters only as Stage-B comparator over authorised historical months (§K, §H) |

**The four objects, preserved and binding:**

| Object | Definition | Standing in this lineage |
|---|---|---|
| **A** — variance risk premium | option-implied variance minus expected / subsequently realised variance | **NO CLAIM POWER**; background only |
| **B** — option-selling alpha | returns of option positions after hedge, path and skew effects | **NO CLAIM POWER**; background only |
| **C** — VIX-futures premium | compensation embedded in VIX futures relative to their eventual settlement distribution | **may be DESCRIBED** (gross carry decomposition, §R); tested by nothing here |
| **D** — implementable constant-maturity short-VIX-futures sleeve | the return object after actual holdings, rolling, variation margin, costs, collateral and frozen sizing | **the ONLY object this lineage formally tests** |

**Sealed, explicitly:** `VIX² − subsequently realised SPY variance` **IS NOT an edge premise** for this lineage. **There is no P&L-free edge premise for this instrument**: every statistic of the VIX term structure is object D's gross return in another unit. Stage A (§C) is the first and only edge evaluation, run once under this seal.

## §B Precedence and the sealed claim set

Every result is classified at **exactly one** level. A failure at an earlier level **stops progression**; a later level is never evaluated.

```
LEVEL 1  VRP-VALIDITY          is the sealed object represented correctly?            (mechanical, P&L-free)
LEVEL 2  VRP-IMPLEMENTABILITY  can the correctly represented frozen object be held?   (mechanical, P&L-free)
LEVEL 3  VRP-A                 standalone useful compensation                          (STANDALONE_EDGE)
LEVEL 4  VRP-B                 programme compatibility — ONLY IF VRP-A = SUPPORTED     (COMPATIBILITY)
         VRP-DESC              declared descriptive family, PROMOTION_POWER = NONE     (§R)
```

| Claim | Type | Failure consequence |
|---|---|---|
| **VRP-VALIDITY** | MEASUREMENT gate | `RESEARCH_STATUS = unresolved`; `FAILURE_CLASS = 1 INVALID_RESEARCH_DESIGN`; bounded correction restoring the **same** intended economics, re-seal, **no governed trial spent** |
| **VRP-IMPLEMENTABILITY** | MEASUREMENT gate | `RESEARCH_STATUS = not_promoted`; `FAILURE_CLASS = 2 PREREGISTERED_GATE_FAILED_BUT_MECHANISM_NOT_EXCLUDED`; **not repairable inside this lineage** by any change to `b`, `J`, sizing, `K`, cost, exposure or granularity; a successor is a new Owner-authorised lineage preserving the failed result |
| **VRP-A** | STANDALONE_EDGE, PRIMARY | the four states of §C.3 |
| **VRP-B** | COMPATIBILITY, PRIMARY, conditional | the states of §I.3 |
| **VRP-DESC** | descriptive | none; may never rescue, upgrade, replace or reinterpret a primary |

No mechanism claim is made anywhere in this lineage.

## §C Stage A — economics, margin and states (VRP-OD-2) — LOCKED

```
MARGIN_CONCEPT  = M2, premium-to-stress ratio
theta           = 0.25
b               = 0.30
+E              = theta · b  =  +0.075   annual excess return on committed capital K
−F              = −0.075                 annual excess return on K (symmetric)
```

**§C.1 Estimand.** `A = 12 · mean_t( r_A,t )`, the **annualised arithmetic mean of the monthly Stage-A excess return** (§E.2) over the frozen Stage-A window (§K.1). It is **not** a compounded annual growth rate and must never be described as one.

**§C.2 Interval.** `[L, U]` = the 95 % percentile interval of the stationary-bootstrap distribution of `A` (§J).

**§C.3 States — strict endpoints; exactly one holds; sealed.**

```
U  <  −0.075               →  NOT_PROMOTED   ·  Class 4 TARGET_MARGIN_RELIABLY_EXCLUDED  ·  subtag materially_adverse
−0.075 ≤ U < +0.075        →  NOT_PROMOTED   ·  Class 4 TARGET_MARGIN_RELIABLY_EXCLUDED  ·  subtag usefulness_excluded
L  ≤  +0.075  ≤  U         →  UNRESOLVED     ·  Class 3 INSUFFICIENT_EVIDENCE / LOW_POWER
L  >  +0.075               →  SUPPORTED
Equality L = +0.075 is UNRESOLVED.  Endpoints classify; the point estimate never does.
```

**No post-result Class-2 relabelling.** A Stage-A return result may never be reclassified as Class 2 on the ground that the margin, the cost convention or the sizing later appears demanding.

## §D Sizing, stress scenario, reserve, granularity (VRP-OD-3) — LOCKED

**§D.1 Stress primitive.** `J = 30` **economically comparable VIX-futures points**: a **parallel +30-point move in EVERY actually held monthly VIX-futures contract**, applied to the **PRE-STRESS holdings** (the contract vector held at the last daily settlement before the stress mark), with **no roll, rebalance or reset before the stress mark**. `J` is **NOT** spot VIX. `J` is **NOT** a maximum possible loss. `b · K` is a budget, not a bound.

**§D.2 Frozen dollar sensitivity.**
```
Σ_i ( q_i · M_i )  =  b · K / J  =  0.01 · K      dollars per VIX point        (q_i signed negative for the short; the
                                                                                 sensitivity is stated as the absolute
                                                                                 dollar loss per +1 point)
Standard multiplier M = $1,000 per point:   N = b·K/(J·M) = 0.01·K / 1,000 contracts
Loss under the declared stress:             Loss_J = J · Σ_i q_i M_i = 0.30 · K
```
Points on any historical quotation basis are converted to the **common $1,000-per-point basis** before any weight, cost, stress or return arithmetic (§F.5).

**§D.3 Stressed margin reserve and implementability condition.**
```
m_J     = 40 comparable points per contract-equivalent      lambda = 0.10 · K liquidity buffer
R_J     = m_J · Σ_i(q_i M_i)  +  0.10 · K   =  40 · 0.01·K + 0.10·K  =  0.50 · K
Condition:  (1 − b) · K  ≥  R_J      →     0.70 · K  ≥  0.50 · K      (holds; 0.20·K slack)
```

**§D.4 Granularity.** The frozen sensitivity at the Stage-B research book (§H.1) must be representable in **integer standard and/or mini contracts within ±10 %** relative error (mini multiplier $100 per point). The **historical research ledger models fractional quantities** at standard-contract prices; the integer check is a VRP-IMPLEMENTABILITY item, not a return modification.

## §E Stage A — accounting (VRP-OD-4) — LOCKED

**Stage A is a RETURN-ON-COMMITTED-CAPITAL RESEARCH BENCHMARK and NOT a self-financing wealth path.**

**§E.1 Rules.**
| Item | Sealed rule |
|---|---|
| Committed capital `K` | **Constant** across the Stage-A window; the denominator of every Stage-A return |
| Monthly reset | At the last exchange business day of each calendar month, after that day's settlement, `K` is restored to its constant (gains withdrawn, losses topped up) **by benchmark convention only**; the sensitivity is recomputed from `K` (unchanged in Stage A, so no reset trade occurs) |
| Variation margin | `VM_d = − Σ_i q_i,(d−1) · M_i · ( S_i,d − S_i,d−1 )` on the holdings at the close of the prior settlement, every exchange business day `d` |
| Collateral | `K` held as cash / bills; variation margin paid from and received into it; no leverage beyond the frozen sensitivity; margin posted from `K` |
| **Clipping** | **None.** A month whose cumulative loss exceeds `K` is recorded **as computed, below −100 %**; a `CAPITAL_EXHAUSTION` event is logged (§R); the benchmark continues from the next month-end with `K` restored by convention; no forced liquidation is modelled in Stage A (that is Stage B's object) |

**§E.2 Primary monthly return — EXCESS OF CASH.**
```
r_A,t  =  ( Σ_{d ∈ month t} VM_d  −  cost_t ) / K
```
Collateral yield cancels by construction (the return is in excess of cash on `K`).

**§E.3 Descriptive collateral total return — NO CLAIM POWER.** `r_A,t + rf_t`, with `rf_t` under the programme's sealed **FM-1 convention** reused verbatim: FRED `DGS3MO`; the last non-missing print on or before the decision date (the last exchange business day of month `t−1`), within a **maximum lookback of 7 calendar days**; **no fallback series**; converted `Y / 100 / 12`; applied to **all of `K`**. If no print exists within the lookback the descriptive value for that month is undefined and reported as such; the primary is unaffected.

## §F Constant-maturity construction (VRP-OD-5) — LOCKED

**§F.1 Eligible contracts.** Standard monthly VX futures (root `VX`) only. **No weekly expiries. No mini contracts for pricing. No alternative tenor. No curve timing.**

**§F.2 Calendars.** The **exchange (CFE) business-day calendar** governs settlements and roll weights. Final-settlement dates `E_k` are taken from the contract's own final-settlement record and verified against the published expiry rule (§L). Contracts are canonically ordered by `E_k` ascending, then by symbol.

**§F.3 Roll weights — exact, deterministic, calendar-only.**
For each exchange business day `d`, let `E_k` be the earliest monthly final-settlement date with `E_k > d`; the **front** contract is `F_k` (final settlement `E_k`) and the **second** is `F_{k+1}`. Define the roll period `P_k = { exchange business days d : E_{k−1} ≤ d < E_k }` (the prior final-settlement day is the first day of the new period because the prior front has already settled that morning), `dt = |P_k|`, and `dr(d)` = the number of business days in `P_k` **strictly after** `d`.
```
w_front(d)  =  dr(d) / dt          w_second(d)  =  1 − w_front(d)          for d ∈ P_k
```
At `d = E_{k−1}`: `w_front = (dt−1)/dt`. At `d = E_k − 1 business day`: `w_front = 0`, `w_second = 1` — **the front exposure reaches zero at the last settlement before final settlement**; the Special Opening Quotation is never a pricing input. Each business day in `P_k` moves exactly `1/dt` of the sensitivity from `F_k` to `F_{k+1}` at that day's settlement. Weights sum to one on every day. Contract quantities: `q_front = − w_front · S / M`, `q_second = − w_second · S / M`, with `S = b·K/J` the frozen dollar sensitivity.

**§F.4 Missing-price rule.** If an official settlement is **missing on an exchange business day** for a held contract: **carry the prior official settlement forward** and **FLAG** the day. **Maximum 2 carry-forward business days per contract per calendar month.** Exceedance inside the frozen historical sample → **VRP-VALIDITY failure**; the repair is completion of the data from primary sources, **never dropping the month**. In the prospective clocks a month exceeding the maximum is `INVALIDATED` (not scored, counted, disclosed; §P.2).

**§F.5 Specification breaks.** The **2007 quotation / multiplier rescaling** and **every minimum-tick change** must be dated from primary exchange sources (§L) and **converted to the common $1,000-per-point economic basis** before any arithmetic: `price_comparable = price_quoted · M_quoted / 1,000`, `tick_comparable = tick_quoted · M_quoted / 1,000`. Synthetic fixtures spanning each break are mandatory (acceptance contract). An undocumented break inside the frozen window is a VRP-VALIDITY failure.

**§F.6 First eligible complete month — mechanical.** The first calendar month from which, through the Stage-A cutoff, both eligible contracts have official settlements on every exchange business day of every roll period, subject to §F.4. Determined from data availability under this rule alone, never from outcomes.

## §G Cost convention (VRP-OD-6) — LOCKED

```
cost_points(i,t)   =  max( 0.10 ,  normalized_contemporaneous_minimum_tick(i,t) )        comparable VIX points per contract-side
c0 = 0.10          REPRESENTS TOTAL SPREAD + SLIPPAGE TOGETHER.  No further half-spread is added anywhere.
normalized tick    =  tick_quoted(i,t) · M_quoted(i,t) / $1,000      (preserves dollar economics across all rescalings)
commission         =  $2.00 per standard-contract-side
exchange+clearing  =  $2.00 per standard-contract-side
pro-rating         =  both dollar constants scale by fractional quantity and by (M_i / $1,000) for the mini contract
funding charge     =  NONE  (the primary is excess-of-cash; margin is funded from K; no borrowing exists)
cost_dollars(i,t)  =  cost_points(i,t) · M_i · |Δq_i,t|   +   $4.00 · |Δq_i,t| · ( M_i / $1,000 )
cost_t             =  Σ over every contract-side traded in month t (daily roll trades and the month-end reset trades)
```
**Descriptive sensitivity only:** `c0 = 0.05` is computed and reported once with `PROMOTION_POWER = NONE`. **No cost convention may change after any reveal.** No cost component may depend on realised strategy performance. If the contemporaneous tick is undocumented for a span, the **largest tick documented for the contract on the comparable basis** is used for that span (conservative; declared).

## §H Stage B — the self-financing book (VRP-OD-7) — LOCKED

```
beta  =  0.06     fraction of TOTAL book wealth the book may lose from the sleeve alone under the declared J stress
s     =  beta / b  =  0.20     strategic sleeve capital share
W0    =  $1,000,000     normalized RESEARCH book wealth (a research-book convention, NOT a claim about any deployable NAV)
At W0:  K_0 = $200,000;  frozen sensitivity = $2,000 per VIX point = 2 standard VX contracts under current standard
        multiplier economics (0 % integer rounding).
```
If a real deployment NAV is later supplied, implementability at that NAV is **reported separately**; research returns and gates are **not** modified.

**§H.1 Month-end allocation.** `W_(t−1)` = book wealth at the close of the last NYSE trading day of month `t−1` (after that month's settlement and cost). Core allocation `= 0.80 · W_(t−1)`; sleeve committed capital `K_t = 0.20 · W_(t−1)`; sleeve sensitivity `= 0.01 · K_t = 0.002 · W_(t−1)` dollars per point — **identical exposure per unit committed capital to Stage A**. Reset trades to the new sensitivity are executed at that day's VX settlement at the §G cost.

**§H.2 Accounts and rules — sealed.**
| Item | Sealed rule |
|---|---|
| Initial book wealth | `W_0 = $1,000,000` at the close of the last NYSE trading day before the first Stage-B month |
| Core account | Holds the core allocation applied to the **unchanged canonical positions** for month `t` (the weights decided at the end of `t−1`, `positions = weights.shift(1)`). **Daily mark = buy-and-hold in units:** `V_core,d = V_core,start · ( 1 + Σ_i p_i,t · ( P_i,d / P_i,start − 1 ) )` using the frozen panel's adjusted closes (`P_i,start` = the close on the allocation day). The canonical monthly cost (2 bps × canonical weight turnover) is charged on the month-end day. **Signal and position logic are untouched; only capital is accounted.** |
| Sleeve collateral account | `C` starts each month at `K_t`; every exchange business day `C ← C + VM_d − cost_d` |
| Daily variation margin | As §E.1, on the sleeve's holdings; days on which VX settles but NYSE is closed accrue to `C` that day; NYSE days without a VX settlement carry `C` unchanged (the missing-price rule §F.4 applies only to exchange business days) |
| Commissions / fees | §G for the sleeve; the canonical 2-bps weight-turnover convention for the core, plus the same 2-bps convention on any forced liquidation turnover |
| Internal cash transfers | Only (i) at the month-end allocation (restoring 0.80 / 0.20 from `W_(t−1)`), and (ii) under the funding rule below |
| **Funding rule (intra-month sleeve exhaustion)** | If after a day's settlement `C_d < 0`, the shortfall `X = −C_d` is funded **from the book itself** at the close of the **next NYSE trading day** `d+1`: liquidate a **pro-rata slice** of the core's unit holdings, fraction `f = X / V_core,(d+1)`, at that day's closes; charge `0.0002 · f · G_core,(d+1)` (canonical cost on the liquidated gross); transfer `X` to `C` (so `C ← 0` as of `d+1`); the core continues at `(1 − f)` of its unit holdings. **Never selective. The actual remaining core allocation is recorded; the ledger never continues a fictional untouched full-sized core.** The rule applies again on every later day it triggers. |
| No external borrowing | **None.** No margin loans, no external recapitalisation of the sleeve or the book at any time |
| Liabilities beyond sleeve capital | Recorded in full against book wealth; **no loss is clipped at −100 % of `K_t`** |
| **BOOK_EXHAUSTION** | If `X > V_core,(d+1)` (the book cannot fund the liability): liquidate the entire core, record `W = V_core,(d+1) − X` (≤ 0, as computed, unclipped) as the book's terminal value, record the month's `r_book` as computed, log `BOOK_EXHAUSTION`, **terminate the ledger**. Stage B → `NOT_PROMOTED · Class 4 · subtag book_exhausted`. **No restart.** |
| Sleeve replenishment | Only at month-end allocation, from the book's own wealth (`K_t = 0.20 · W_(t−1)`), automatically; never from outside |

**§H.3 Book return.** `r_book,t = W_t / W_(t−1) − 1`, where `W_t` is the book's value at the close of the last NYSE trading day of month `t`.

**§H.4 Oracle identity (binding on the acceptance contract).** In any month with no funding event, `r_book,t = 0.80 · r_core,t + 0.20 · r_A,t(K = K_t)` **exactly** (to floating tolerance), where `r_core,t` is the frozen canonical net monthly return and `r_A,t` the Stage-A excess return computed on `K_t`.

## §I Stage B — estimand, tail definition and states — LOCKED

**§I.1 Tail definition (X46 rule, retained).** Over the Stage-B window (§K.2), `q = quantile_0.10( r_SPY )` computed **once** on all aligned complete months (linear interpolation, §J.3); `T = { t : r_SPY,t ≤ q }` (equality included). `r_SPY,t` = SPY month-end adjusted-close total return from the frozen panel. **Aligned COMPLETE months only**: a month is in the sample only if `r_book,t`, `r_core,t` and `r_SPY,t` are all defined for the same complete calendar month.

**§I.2 Primary estimand.**
```
D  =  mean_{t ∈ T} ( r_book,t − r_core,t )          units: percentage points of whole-book return per tail month
delta_tail  =  0.0075   (0.75 percentage points per tail month)
```

**§I.3 States — strict endpoints; sealed.**
```
L(D)  ≥  −0.0075                 →  SUPPORTED compatibility
L(D)  <  −0.0075  ≤  U(D)        →  UNRESOLVED             ·  Class 3
U(D)  <  −0.0075                 →  NOT_PROMOTED           ·  Class 4 TARGET_MARGIN_RELIABLY_EXCLUDED
BOOK_EXHAUSTION in window        →  NOT_PROMOTED           ·  Class 4 · subtag book_exhausted
```
In no state does VRP-B move VRP-A. **The tail-retention ratio has no gate power.**

**§I.4 Descriptive ratio reporting rule.** `mean_T(r_book) / mean_T(r_core)` is shown **only if** `|mean_T(r_core)| ≥ 0.0025` **and** the denominator retains one sign in **≥ 95 %** of valid bootstrap replicates; **otherwise the ratio is not reported at all.** Post-tail descriptive horizon `k = 3` months.

## §J Inference — reused from the sealed X01 §6.1 protocol, with the Stage-B extension — LOCKED

| Item | Sealed rule |
|---|---|
| Family | **Stationary bootstrap** (Politis & Romano 1994): geometric block lengths, **circular wrap**, replicate length equal to the sample length |
| Expected block length | **12 months** (`p = 1/12`), the programme's sealed inference convention; not re-derived, no alternative computed |
| Replicates | **10,000** |
| Interval | **Percentile**: `L` = 2.5th and `U` = 97.5th percentile of the replicate statistics (linear interpolation, §J.3). No BCa, no alternative interval, none selected after the fact |
| Stage-A statistic | `A* = 12 · mean( r_A* )` per replicate |
| Stage-B statistic | resample the **aligned triple `(r_book, r_core, r_SPY)` jointly** in common time blocks; **inside each replicate** recompute `q* = quantile_0.10(r_SPY*)`, `T*` and `D*` |
| Stage-A replicate validity | invalid iff the replicate contains **fewer than 24 distinct calendar months** (X01 rule) |
| Stage-B replicate validity | invalid iff `|T*| < ceil( 0.5 · |T_full| )` — **the tail count only, never the value of `D*`** |
| Floor | run valid iff **≥ 9,500 of 10,000** replicates valid; invalid replicates are **counted and reported, never replaced, never selectively re-drawn**; **no sign clipping** anywhere; floor failure = **VRP-VALIDITY failure of inference** (mechanical), not a state |
| Seed protocol | master seed **7**; `numpy.random.SeedSequence(7).spawn(4)` in the **fixed order [Stage A historical, Stage B historical, VRP-A-PROSPECTIVE, VRP-B-PROSPECTIVE]**; generator `numpy.random.Generator(numpy.random.PCG64(child))`; block lengths from `rng.geometric(1/12)`, start indices from `rng.integers(0, n)`; the spawned entropy values are written into the seal manifest. The seed is a fixed constant and is derived from nothing |

**§J.3 Mechanical constants (reproducibility only; they change no estimand).**
| Item | Constant |
|---|---|
| RNG | NumPy `PCG64` via `Generator`, seeded as above |
| Floating point | IEEE-754 binary64 (`float64`); sums accumulated in date order; no extended precision |
| Quantile / percentile | NumPy `quantile` / `percentile` with `method="linear"` |
| Tail tie rule | `r_SPY,t ≤ q` (equality included); sort stable by calendar month |
| Dates and time zone | Exchange trading dates are calendar dates in the exchange's local zone (America/Chicago for VX; America/New_York for ETFs); no intraday timestamps in any estimand; seal and ledger timestamps in UTC |
| Month-end mapping | A calendar month's sleeve month-end = its last VX exchange business day; the book's month-end = its last NYSE trading day; the Stage-B alignment key is the calendar month (`YYYY-MM`) |
| Identity-test tolerance | relative `1e−9` on returns, absolute `1e−12` on weights (weights sum to 1), absolute `1e−6` dollars on ledgers; used only in mechanical identity tests |
| Contract ordering | by final-settlement date ascending, then symbol; contract identity key = (`root`, `final_settlement_date`) |
| Annualisation | `12 · mean` (arithmetic); never geometric |

## §K Sample and evaluation boundaries (VRP-OD-8) — LOCKED

**§K.1 Stage A (standalone).**
```
STAGE_A_CUTOFF_DATE        = 2026-09-01                       (a fixed calendar date; never "latest available")
STAGE_A_LAST_MONTH         = 2026-08  (the final complete calendar month before the cutoff)
STAGE_A_FIRST_MONTH        = the first eligible complete month under §F.6 (mechanical)
GAP_MONTHS_EXCLUDED        = 2026-09 through the month containing this S1 seal (neither historical nor prospective; never scored)
```
Stage A does **not** stop at the canonical TSMOM boundary; it is standalone and uses no canonical quantity.

**§K.2 Stage B (compatibility).**
```
STAGE_B_LAST_MONTH         = 2026-05  (ends 2026-05-31 under the frozen core boundary 2026-06-12; June 1–12 2026 is NOT a monthly observation)
STAGE_B_FIRST_MONTH        = the LATER of (i) the canonical first full-universe scored month (expected 2008-05; determined mechanically
                              under the canonical held-position liveness rule) and (ii) the first eligible complete VIX-futures month (§F.6)
COMPARATOR                 = the frozen canonical net monthly stream recomputed from the pinned frozen panel
                              (data/close_prices_raw.csv, SHA256 3d2a7a56dbd92d4ff8138cfd894c87f5ac5ac088a11165db870673e0c05c3c31) by the
                              hash-pinned canonical modules exactly as the sealed Value contract's §17 comparator identity; restricted to months
                              ≤ 2026-05-31; output/monthly_returns.csv is NOT authority
```

**§K.3 C-A blindness.** No canonical TSMOM signal, position or return is computed for any month after the C-A forward boundary (2026-09-11) on any panel in any session of this lineage; the C-A position and return layers are never read; any breach is a research-axis exposure row and a C-A blindness breach. Forward SPY **prices** may be read where independently permitted (they are prices, not canonical protected outcomes).

## §L Data acquisition contract — defined now, executed only after accepted seal and Owner data authorisation

**No data was fetched, opened or inspected at S1.** Outcome-bearing acquisition begins only after the accepted S1 seal **and** a separate Owner data-acquisition authorisation. Raw files land under the git-ignored `data/vix/raw/` and are pinned by a tracked manifest `research/extensions/vrp/VRP_DATA_MANIFEST.md` (created at acquisition, not now). **No fallback may alter the economic object** (official daily settlements of the standard monthly contract).

| Item | SOURCE PRIORITY | PRIMARY AUTHORITY | FALLBACK AUTHORITY (if permitted) | FILE FORMAT EXPECTATION | HASHING | RAW IMMUTABILITY | LICENSE / RETENTION | NORMALISATION | VALIDATION CHECKS |
|---|---|---|---|---|---|---|---|---|---|
| Monthly VX contract-level daily settlements (all listed monthly contracts, listing → final settlement) | 1 | Cboe (CFE) official historical per-contract data files, the **settlement** field | A licensed vendor copy of the **same official daily settlement** field (never last trade, never a constructed continuous series), admissible only if it reproduces the primary on every overlapping date; otherwise **not permitted** | One CSV per contract (trade date, symbol, OHLC, settle, volume, open interest as published) | SHA256 per raw file; manifest rows: URL/source, fetch UTC timestamp, bytes, hash | Raw files are never edited; all cleaning lives in a derived layer with its own hashes | Exchange personal/research-use terms; **no redistribution**; raw bytes retained in the git-ignored data directory for the life of the lineage; manifest tracked | `price_comparable = settle · M_quoted / 1000` per §F.5 | one row per (date, contract); dates monotone; no duplicates; settle > 0; settlement present on every exchange business day between listing and final settlement subject to §F.4; contract count per year plausible; final settlement date = last row date |
| Stable contract identifiers | 1 | Symbols in the primary files (`VX` + month code + year), mapped to the identity key (`root`, `final_settlement_date`) | Exchange product notices for symbol-convention changes | As in the primary files | Covered by the raw file hashes | — | — | Identity key is the pair, never the symbol string alone | Every (root, final_settlement_date) unique; every business day maps to exactly two eligible contracts (§F.3) |
| Listing / specification history | 1 | Cboe contract specifications and rule filings / product notices (public) | None; an undocumented break inside the window = VRP-VALIDITY failure | PDF / HTML saved as bytes | SHA256 per saved document | Never edited | Public documents; retained | Dated break table with `M_quoted`, `tick_quoted` per span, on the common basis | Break dates precede any affected price row; fixtures span each break |
| Expiry / final-settlement dates | 1 | Each contract's own final-settlement row in the primary files, verified against the published expiry rule (the Wednesday thirty days before the third Friday of the following month, holiday-adjusted) | The published annual expiration calendars | Derived table | Hash of the derived table | — | — | ISO dates | Rule-derived date = observed final-settlement date for every contract; mismatches enumerated; any unexplained mismatch = VRP-VALIDITY failure |
| Multiplier / quotation-basis history | 1 | Cboe specifications and the rule filing for the 2007 rescaling (public) | None | Saved documents + dated table | SHA256 | Never edited | Public | `M_quoted` per span; conversion factor per §F.5 | Price continuity across the break after conversion (a level ratio consistent with the documented factor); fixture test |
| Tick-size history | 1 | Cboe rule amendments / product notices | If undocumented for a span: the **largest documented tick** for the contract on the comparable basis (conservative; declared) | Dated table | SHA256 | Never edited | Public | `tick_comparable = tick_quoted · M_quoted / 1000` | Tick defined for every date in the window; `cost_points ≥ tick` everywhere |
| Exchange trading calendar | 1 | Cboe (CFE) holiday calendar | The union of settlement dates across all contracts, cross-checked against the NYSE calendar for consistency | Date list | SHA256 | — | Public | Business days as calendar dates | No settlement on a non-business day; no business day without any VX settlement beyond §F.4 |
| Transaction-cost metadata | 1 | Cboe fee schedule (current); the sealed constants of §G | None needed — the convention is sealed, not measured | Saved schedule | SHA256 | — | Public | Constants are already on the comparable basis | Sealed constants ≥ current schedule (documented once) |
| Stressed-margin-model inputs | 1 | The sealed constants `m_J = 40`, `lambda = 0.10` (§D.3) — a declared model | Exchange margin notices may be saved for plausibility only; they change nothing | Saved notices (optional) | SHA256 if saved | — | Public | — | Condition `(1 − b)·K ≥ R_J` evaluated from constants |
| Frozen ETF panel (SPY, canonical stream inputs) | already in hand | `data/close_prices_raw.csv`, SHA256 pinned in §K.2; the hash-pinned canonical modules | None | CSV | Existing pin | Frozen | Existing | Existing | Hash match before use; no month after 2026-05-31 used |
| `DGS3MO` (descriptive only) | already in hand | The repository's existing fetch with provenance (FM-1) | None (no fallback series) | CSV | Existing pin | Frozen | Public | FM-1 | Hash match |

If no acceptable primary or permitted fallback exists for a REQUIRED item at acquisition time, the corresponding gate fails **according to this contract** (VRP-VALIDITY for chain, identity, calendar, break and tick documentation; VRP-IMPLEMENTABILITY for anything that makes the frozen object unholdable); no substitute object is invented.

## §M Evidence context, trial accounting and exposure — LOCKED

- **Historical Stage-A evidence context = `DESIGN_INFORMED_FIRST_LOCAL_USE`.** Never "fresh". Never "independent". The label travels with every citation. Stage B is **T0** on the core side (a further reuse of the frozen ETF panel).
- **Local VIX-chain trial count:** the chain is a new dataset row in `research/extensions/SAMPLE_REUSE.md` under the programme's existing governed convention (one trial per distinct constructed strategy-return series with a selection opportunity; diagnostics excluded), starting at `N_trials = 0` before Stage A, **subject to repository verification** that no VIX-futures series was ever constructed here. **Stage A governed return series → +1.** **Stage B** is a paired combination on the heavily reused ETF / core panel and is declared there as T0 / further reuse under the existing programme convention (the frozen panel's historical count convention remains the open Owner item `D-ETF-COUNT` and is not resolved here). **VRP-DESC → no trial power. Bootstrap replicates → not attempts. Sensitivity outputs with `PROMOTION_POWER = NONE` → not attempts.**
- **Failure class and trial count are separate axes.** A Level-1 or Level-2 failure occurs before the governed run and spends no trial; a Stage-A run spends its trial whatever its state.
- **Design-exposed episodes (from S0; recorded here so no later document can present them as fresh confirmation):** the GFC; the 2010 volatility / flash-crash episode; February 2018; March 2020; the CY2022 core-stress context; the August 2024 volatility episode; the April 2025 volatility episode; approximate public facts about front-month VIX-futures moves in those episodes; the already-revealed canonical crisis behaviour (X46; GFC, COVID and CY2022 window returns; SPY-left-tail statistics). The Phase-C planning sentence about erasing the core's crisis gain at meaningful size is a hypothesis this lineage tests, not a verdict.
- **Global exposure:** VIX futures are heavily studied publicly; the sign of the long-run gross carry is common knowledge; new vendor bytes create no new market events.
- Ledger rows to be appended at S2 acceptance are written out in `VRP_EXPOSURE_DISCLOSURE.md`.

## §N Failure taxonomy — mutually exclusive mapping — SEALED

| Class | Where it can arise | Meaning here |
|---|---|---|
| **1 INVALID_RESEARCH_DESIGN** | **VRP-VALIDITY only** | chain, weights, breaks, calendar, inputs, accounting logic, branch reachability, or the bootstrap floor |
| **2 PREREGISTERED_GATE_FAILED_BUT_MECHANISM_NOT_EXCLUDED** | **VRP-IMPLEMENTABILITY only** | the correctly represented frozen object cannot be held under the frozen granularity, capital, stress budget, reserve, funding or cost rules |
| **3 INSUFFICIENT_EVIDENCE / LOW_POWER** | Stage A or Stage B | the interval straddles the required margin (`L ≤ +E ≤ U`; `L(D) < −delta_tail ≤ U(D)`) |
| **4 TARGET_MARGIN_RELIABLY_EXCLUDED** | Stage A or Stage B | the margin is reliably excluded, including subtags `materially_adverse`, `usefulness_excluded`, `book_exhausted` |
| **5 TRULY_UNTESTED_SUBSPACE_REMAINS** | a record, never a level | another tenor, sizing principle, filter, market, option object, capital share, stress value, cost convention, etc. **Class 5 never authorises immediate continuation**; a new Owner-authorised lineage is required |

## §O Stop rule — SEALED, exhaustive

```
VALIDITY fail            → stop → bounded repair of the SAME economics only → re-seal → no governed trial spent
IMPLEMENTABILITY fail    → stop lineage → not_promoted → no parameter rescue → successor only as a new Owner-authorised lineage
Stage A Class 4          → stop → Stage B never runs
Stage A Class 3          → stop historical study → Stage B never runs → only the sealed VRP-A-PROSPECTIVE continuation (§P)
Stage A SUPPORTED        → Stage B may execute ONCE
Stage B Class 3          → historical compatibility unresolved → only the sealed VRP-B-PROSPECTIVE continuation (§Q)
Stage B Class 4          → this combination not_promoted (the Stage-A result stands unchanged on its own record)
```
**No historical or prospective result may authorise changing:** `J`; `b`; `theta`; `E`; `F`; `s`; `beta`; `delta_tail`; the maturity; the roll; the cost convention; the sample endpoints; the tail rule; or adding any filter. Each is a new lineage with its own trial accounting. **Review budget:** the S0 Astra challenge is consumed and accepted; an S1 round only on a named material trigger; at most two substantive rounds per gate; a HOLD buys one bounded repair of a design defect before the run, never a change to the object after a result; one S4 evidence-to-claim judgment if a consequential claim results; no closure or residual-verification nodes.

## §P VRP-A-PROSPECTIVE — standalone useful compensation — SEALED NOW

```
START                 =  the first VX month-end settlement AFTER this S1 seal; the position is established at that
                         settlement (entry cost charged under §G); the first scored month is the following calendar month
N_A                   =  120 COMPLETE, ELIGIBLE, NON-INVALIDATED scored months
ELIGIBILITY           =  a prospective month scores only if every VX exchange business day in it has official settlements for
                         both eligible contracts under §F.4 (≤ 2 carry-forward days per contract); a month exceeding the
                         maximum is INVALIDATED — not scored, counted, disclosed — and the clock waits for 120 valid months
SAME AS STAGE A       =  construction (§F), sensitivity per K (§D), costs (§G), +E and −F (§C), classification rules (§C.3),
                         inference (§J, its own seed stream)
PLANNING ASSUMPTIONS  =  sigma_plan = 15 % per year on K; declared planning dispersion of one-month-maturity VIX-futures monthly
                         moves = 4.3 comparable points; dependence inflation = 1.25 on the iid half-width — PLANNING
                         ASSUMPTIONS ONLY, NOT EVIDENCE, used to derive N_A from the requirement that the terminal 95 %
                         half-width be ≤ 1.5·E; they bind nothing at the reveal
SINGLE TERMINAL REVEAL: no interim positive-result look; no adverse oracle; no automatic extension
PROTECTION            =  generated in the VRP family's own protected store under GENERATED_NOT_SEEN (a sibling of the C-A
                         mechanism, never the C-A store or key); monthly snapshots hashed; one Owner reveal authorisation,
                         single-use, recorded in committed state before access
```

## §Q VRP-B-PROSPECTIVE — compatibility in systemic-tail months — SEALED SEPARATELY

```
CONDITION             =  VRP-A = SUPPORTED, historically or prospectively
N_B                   =  120 CALENDAR months from the first prospective sleeve month; THE WINDOW FREEZES THERE; no month is ever
                         added after it
n_T_min_prosp         =  10 systemic-tail months inside the frozen window, under the X46 rule (§I.1) applied to forward SPY
                         monthly returns (forward SPY PRICES may be read from the append-only store where independently
                         permitted; they are prices, not canonical protected outcomes)
TERMINAL RULE         =  at N_B, tail count < 10 → UNRESOLVED; NEVER auto-extended until enough events occur
SAME AS STAGE B       =  self-financing ledger (§H), s = 0.20, D (§I.2), delta_tail = 0.0075, tail definition (§I.1),
                         inference (§J, its own seed stream), states (§I.3)
```

**§Q.3 C-A protections — SEALED.** VRP-B-PROSPECTIVE **does not authorise access to protected C-A prospective outcomes** and **does not authorise reconstruction of protected forward canonical returns anywhere** (not in a VRP session, not in a copy, not by re-running the canonical rule on forward prices). The sleeve's forward months are generated in the VRP store. The paired evaluation is executed **exactly once**, at the first date on which the core's forward months ≤ `N_B` become **legitimately readable** — the C-A terminal look, or an Owner-declared scoped reveal logged as such. If the VRP-B window finishes before those months are legitimately readable: **`DEFERRED_EVALUATION_FROZEN_WINDOW`** — the sleeve's months through `N_B` are hashed and frozen at `N_B`; no month is added later; the single evaluation waits. If they never become legitimately revealable: **`NOT_EVALUABLE`** (a governance state, distinct from the evidentiary state `unresolved`); no compatibility claim exists.

**TSMOM-VRP-01 cannot cause:** an early C-A reveal; reconstruction of protected canonical forward outcomes elsewhere; any C-A rule modification; any change to C-A's `N`; any change to C-A's clock. Canonical forward positions and returns remain protected.

## §R Declared descriptive outputs — every one `PROMOTION_POWER = NONE`

Declared before any run. **No descriptive can rescue, upgrade, replace or reinterpret a primary result.**

| # | Descriptive | Stage |
|---|---|---|
| R1 | Gross carry decomposition (object C): monthly roll-down in comparable points per unit sensitivity, gross of cost | A |
| R2 | Worst 1-day sleeve loss as a fraction of `K` | A |
| R3 | Worst 5-day sleeve loss as a fraction of `K` | A |
| R4 | Worst monthly sleeve loss as a fraction of `K`, against the declared budget `b = 0.30` | A |
| R5 | `CAPITAL_EXHAUSTION` events (count, months) | A |
| R6 | Stage-B forced-liquidation events (count, dates, fractions `f`) | B |
| R7 | `BOOK_EXHAUSTION` events | B |
| R8 | Declared crisis-window descriptions on the three design-exposed windows (GFC, COVID, CY2022 as fixed in the register): book and core cumulative returns; no gate | B |
| R9 | Expected-shortfall change `ES_5%(r_book) − ES_5%(r_core)` on the Stage-B window | B |
| R10 | 3-month post-tail descriptive: mean book and core returns over the `k = 3` months following each tail month | B |
| R11 | Tail-retention ratio, **only under the §I.4 reporting rule** | B |
| R12 | `c0 = 0.05` cost sensitivity of the Stage-A estimand | A |
| R13 | Collateral total-return version of the Stage-A series under FM-1 (§E.3) | A |
| R14 | Stage-A point estimate `A`, both bounds, invalid-replicate count; Stage-B `D`, both bounds, `|T|`, invalid-replicate count (reported with the primaries, not instead of them) | A, B |

## §S Reveal authorisation and recording — SEALED

- Every real Stage-A and Stage-B outcome is generated **only** after the acceptance contract passes (§T) and **only** under a **single-use Owner execution authorisation** recorded in committed state before the run (the existing `ops/EXECUTION_AUTHORIZATIONS.md` discipline: a grant is read only from committed state; a consumed authorisation is never reused). The generated evidence is stored `GENERATED_NOT_SEEN` and revealed **once** under a separate single-use Owner reveal authorisation.
- Recording obligations at S2 acceptance (rows drafted in `VRP_EXPOSURE_DISCLOSURE.md`): `ops/EXPOSURE_LEDGER.md` (research axis; existing table, existing tokens); `ops/REVIEWER_EXPOSURE_LOG.md` (seat axis); `research/extensions/TRIAL_LEDGER.md` (`HYPOTHESIS_FAMILY = F-VRP` declared before any member runs; the Stage-A primary as the one governed attempt; VRP-DESC members `PROMOTION_POWER = NONE`); `research/extensions/SAMPLE_REUSE.md` (new VIX-chain dataset row at `N_trials = 0`; ETF-panel further-reuse row); `PROJECT_STATE.md` (a `TSMOM-VRP-01` block, state only).
- KB recording follows the programme's existing vocabulary: `supported` / `not_promoted` / `unresolved` only; `falsified` never from one sealed construction; `confirmed` never from historical evidence.

## §T Seal prerequisites, gate ordering and the ten self-check questions

**§T.1 S1 seal prerequisites — all satisfied by the S1 session (see `VRP_SEAL_MANIFEST.md`).**
1. Owner decisions VRP-OD-1 … VRP-OD-9 complete and transcribed exactly (validator check).
2. Authoritative input hashes recomputed and matched (S0-02-repaired; Owner Decision Record).
3. `vrp_prereg_validate.py` passes on the sealed text (structure, vocabulary, constants, forbidden phrases, no data present).
4. Repository state recorded (HEAD, branch, clean worktree); no VIX outcome-bearing file accessed or present.
5. No generated result exists; no strategy code exists in the package.
6. The implementation acceptance contract exists and is hash-pinned (`VRP_IMPLEMENTATION_ACCEPTANCE_CONTRACT.md`).
7. The exposure disclosure exists and is hash-pinned (`VRP_EXPOSURE_DISCLOSURE.md`).

**§T.2 Gate ordering.** `S1 SEAL (this) → ChatGPT / Aaron ACCEPTANCE → Owner DATA-ACQUISITION AUTHORISATION → S2 BUILD (light loop; validators; the acceptance contract) → Owner SINGLE-USE EXECUTION AUTHORISATION → S3 RUN (Level 1 → 2 → 3 → 4) → Owner SINGLE-USE REVEAL → S4 VERDICT → STOP.` **No S2 item blocks this seal merely because it has not yet been built.** Nothing in this contract is authorised to run by the seal.

**§T.3 The ten self-check questions — answered on the sealed text.**
| # | Question | Answer | Where it is closed |
|---|---|---|---|
| 1 | Could an implementer choose a different `J`? | **NO** | §D.1 locks `J = 30`; §O forbids change; any other `J` is a new lineage |
| 2 | Could an implementer choose a different exposure? | **NO** | §D.2 fixes sensitivity `= 0.01·K`; §H.1 fixes `s = 0.20`, `K_t = 0.20·W_(t−1)`; §O |
| 3 | Could an implementer change costs? | **NO** | §G locks `c0 = 0.10` (spread + slippage together), $2.00 + $2.00, no funding charge; the `c0 = 0.05` variant is descriptive with no claim power; §O |
| 4 | Could an implementer choose another maturity? | **NO** | §A, §F lock one-month constant maturity on the first and second monthly contracts; any other tenor is a new lineage |
| 5 | Could an implementer change sample endpoints? | **NO** | §K fixes the cutoff 2026-09-01 (last month 2026-08), Stage B ends 2026-05-31, first months mechanical, gap months excluded |
| 6 | Could a bad result be relabelled? | **NO** | §C.3 and §I.3 map every interval to exactly one state and class; §N is mutually exclusive by level; no Class-2 relabelling of a return result; endpoints classify, point estimates never |
| 7 | Could Stage B shrink the sleeve? | **NO** | `s = beta/b = 0.20` is sealed; Stage B runs only at the Stage-A exposure per unit `K`; no re-targeting; §H.2, §O |
| 8 | Could C-A be accessed early? | **NO** | §K.3 and §Q.3: no canonical computation after 2026-09-11; the VRP-B evaluation waits for legitimate readability; `DEFERRED_EVALUATION_FROZEN_WINDOW` / `NOT_EVALUABLE` |
| 9 | Could a descriptive rescue a failed primary? | **NO** | §R: every descriptive `PROMOTION_POWER = NONE`; §I.4 ratio has no gate power; §S KB vocabulary |
| 10 | Could an implementer make a consequential choice not fixed here? | **NO** | Every economic constant, rule, window, estimand, state, calendar, cost, ledger rule and inference constant is sealed; the remaining implementation choices (code structure, file layout, test framework) are mechanical and cannot change an estimand; §J.3 fixes the reproducibility constants |

```
ALL_CONSEQUENTIAL_CHOICES_FROZEN = YES
SELF_CHECK_1_TO_10 = ALL_NO
```

*The SHA256 of this file is recorded in `VRP_SEAL_MANIFEST.md`; any receiver recomputes it before use. Chat-carried bytes are never a source of truth.*
