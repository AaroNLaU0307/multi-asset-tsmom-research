# X01 — PREREGISTRATION **DRAFT** (UNSEALED)

```
X01_PREREG_SEALED = NO
X01_FULL_PERFORMANCE_EXECUTED = NO
X01_A2_VERDICT = FAIL (accepted) -> bounded design repair applied
X01_A2_FINAL_CLOSURE = NOT_YET
O1 = RESOLVED_BY_OWNER (ADOPT_OPTION_B)
O2 = RESOLVED_BY_OWNER (B = 0.15 annualised-Sharpe units)
O6 = RESOLVED_BY_OWNER (ADOPT_OPTION_1_SYMMETRIC_ZERO_CARRY)
OWNER_DECISIONS_REMAINING = NONE
TECHNICAL_BLOCKERS = NONE
SECONDARY_INFERENCE_ROLE = DESCRIPTIVE_SENSITIVITY
BH_FDR_REQUIRED = NO · S1_S2_PROMOTION_POWER = NONE · SECONDARY_MATERIALITY_GATE = NONE
STATUS = COMPLETE DRAFT AWAITING GPT-6 ASTRA A2 DELTA CLOSURE, THEN AARON'S SEAL
```

**Candidate:** X01 — Commodity-sleeve futures transfer, matched-map arm
**Family:** F-X01 · **Cluster:** C1 (implementation transfer / wrapper truth)
**Lane at execution:** FULL (only after a seal) · **Lane today:** MEASUREMENT
**Drafted:** 2026-09-07, Wave-1, by the Opus research builder
**Definitions:** `TSMOM_EXTENSION_RESEARCH_MAP_v2.md` Cluster C1 §X01 ·
`TSMOM_EXTENSION_RESEARCH_PROGRAM_v2.md` §0A, §0B, §0C, §1, §3, §10, §11

**This document seals nothing.** No threshold below is decided. Every number is
either (a) a fact verified from bytes and cited, or (b) a **designer proposal**
explicitly marked for challenge. The required next step is a **fresh GPT-6 Astra
A2 challenge**, then Aaron's adjudication and seal. **The drafting session may
not challenge or verify this contract** (`ops/REVIEWER_EXPOSURE_LOG.md` S8).

---

## §1 Question, and what an answer can and cannot mean

**Question.** Does the **futures wrapper** preserve the commodity sleeve's trend
PnL relative to the **ETF wrapper**, on the same economic history?

**This is deployment truth, not alpha.** X01 tests no new premium. The two legs
are expected to be **highly dependent by construction** — they run the same
signal on the same economic history — and a "good" X01 result is evidence that
the futures implementation *reproduces* a stream whose own historical evidence is
already dependent, not evidence that the stream works. **No numeric correlation
is assumed here**: MAP_v2's "≥ 0.9" is a designer expectation about *price*
pairs, it is not a measured strategy-stream correlation, and §6.2 does not use it
as one.

**The confirmation ceiling, stated before any threshold.** The ETF panel is
burned 6/6 and every X01 design input is post-exposure (`SAMPLE_REUSE.md` KB-1).
The Databento panel covers **the same 2010–2026 economic history** — evidence
context **T1**, not T2/T3/T4. Therefore:

> **A same-period futures result cannot independently confirm an ETF-informed
> historical performance edge.** Whatever X01 returns, it may be recorded at most
> as `supported` in context T1 for the *performance* claim (Program v2 §10). The
> stricter classification question is `CANONICAL_CLASSIFICATION_PENDING_VERIFICATION`
> — decision **D9**, for Aaron and the KB curator, and it is **not** resolved here.

**Design lineage and validation context are recorded separately and never merged:**

| | Value |
|---|---|
| Design lineage | `POST_EXPOSURE_DESIGN_ON_ETF_PANEL` + `CARRY_STUDY_INFORMED` |
| Validation context of the X01 primary | **T1** (same-period wrapper replication) |
| What T1 can support | wrapper transfer; implementation and construction robustness; partial external validity |
| What T1 cannot support | independent confirmation of the ETF-informed edge |

An exposed origin is disclosed forever and **does not** prevent this candidate
from later earning stronger evidence in T2/T3/T4. **No weakest-tier inheritance
rule is created or implied by this contract**: a later genuinely independent test
of this candidate is classified on its own facts.

---

## §2 Two separate objects, never conflated

Program v2 §X02 fixes this split and this contract inherits it.

| | **Implementation validity** | **Economic preservation** |
|---|---|---|
| Asks | does the futures accounting compute what it claims? | does the futures wrapper preserve the sleeve's economics? |
| Owner | **X02a**, MEASUREMENT, pre-seal | **X01 primary**, FULL, post-seal |
| Evidence type | `implementation_fact` (may reach `confirmed`, G4-verified) | empirical result — **never** `implementation_fact` |
| Failure meaning | **mechanical kill** — no futures performance work proceeds | a valid negative wrapper result |

**A mechanical accounting failure is not a performance result, and a performance
result is not permission to skip the accounting.** Invalid accounting is
inadmissible for any PnL "regardless of economic immateriality" — the v1
"< 2% / < 5 bps → the cheaper implementation may be used" clause is deleted and
is not reintroduced here.

---

## §3 Sample, window and construction (fixed ex ante)

| Item | Value | Status |
|---|---|---|
| Futures panel | `dataset.databento.commodity-futures-curves`, GLBX.MDP3 | VERIFIED |
| Snapshot boundary | **2026-06-30** (request end 2026-07-01 exclusive) | **VERIFIED** — `DATABENTO_W1_INPUT_VERIFICATION.md` §2 |
| ETF panel | `dataset.yfinance.multi-asset-etf-panel`, sha `3d2a7a56…c3c31`, last date **2026-06-12** | VERIFIED |
| **Common evaluation window** | **2011-07-31 → 2026-05-31** month-ends, **N = 179 paired months** — derived from the frozen eligibility rules, not chosen | **§3.5** (corrected: the former 2010-07-31 ignored the 12-month signal warm-up) |
| Mapped pairs (frozen, c1 D5 map, reused unchanged) | USO↔CL · UNG↔NG · GLD↔GC · **DBA↔ag proxy = `ZC ZS ZW LE HE GF`, equal weight 1/6 each** | three legs frozen from MAP_v2 / c1 `DEVIATIONS.md` D5; the ag leg **ADOPTED BY AARON**, `O1_OWNER_DECISION = ADOPT_OPTION_B` (§15 O-1). Classified **`FIXED_PROXY_WITH_COMPOSITION_MISMATCH`**, not `EXPOSURE_REPLICATION` |
| Degradation tolerance | **`B = 0.15` annualised-Sharpe units**; non-inferiority boundary **`−0.15`** | **ADOPTED BY AARON**, `O2_OWNER_DECISION = B_0.15` (§15 O-2), prospectively and before any X01 outcome |
| Capital / financing convention | **`SYMMETRIC_ZERO_CARRY`** — no cash yield, no margin financing, no borrow, on either leg | **ADOPTED BY AARON**, `O6_OWNER_DECISION = ADOPT_OPTION_1_SYMMETRIC_ZERO_CARRY` (§15 O-6) |
| Signal | the locked baseline composite, unchanged — **the MEAN OF THE SIGNS of the {1,3,6,12}-month returns**, all four horizons required (§3.7) | `src/signals.py::signal_method_b` (authoritative); MAP_v2 §Baseline; `config.py` `MOMENTUM_LOOKBACKS_MONTHS = (1,3,6,12)`, `SIGNAL_COMBINE = "mean"`, `MOMENTUM_MIN_PERIODS = 4`, `SIGNAL_RESAMPLE = "ME"` |
| Sizing | per-asset `w = signal x (0.10 / ann_vol)`, `ann_vol` from a **60-trading-day** rolling window x sqrt(252), `|w|` capped at 2.0; **equal-weight aggregation across the sleeve's legs; NO portfolio-level vol target and NO gross-leverage cap** (those are properties of the 5-sleeve portfolio, not of the wrapper) | `config.py` `VOL_WINDOW_DAYS=60`, `TARGET_VOL_ANNUAL=0.10`, `MAX_ASSET_WEIGHT=2.0`; see **§3.6** |
| Position timing | the signal at month-end `t` sets the position **held through month `t+1`** (`positions = decision_weights.shift(1)`) — identical on both legs | verified against the baseline engine in the X45 reconstruction (`FUTURES_INFRA_TRUTH.md`) |
| Roll rule (primary) | **A1: open-interest-max**, and a **DECLARED DEGREE OF FREEDOM** that must be named in the sealed text (`ROLL_RULE_DOF = REQUIRED`; `ROLL_RULE_ECONOMIC_MATERIALITY = UNRESOLVED`). **Effective causal timing: the decision at `t` uses open interest as of the `t−2` close, published during `t−1`** — the vendor publishes a day's OI referencing the prior close, and the rule then lags one further session. Causal, no look-ahead, one session staler than the "t−1 OI" phrasing. | `stat_type = 9` (vendor `OPEN_INTEREST`); lag reproduced from bytes in `FUTURES_INFRA_TRUTH.md` §2.2 |
| Costs | **CASH-FIRST, mandatory route: `research/extensions/wave1/run_x02a_v3.py::tsmom_chain_net_returns`.** Primitive cost is **fixed dollars per side** (`cost_per_side_usd = tick_value + $2.50`); the exit and entry legs of a roll are charged **independently**; any percentage is **derived** as cash / prior-held notional. **The legacy carry percentage route (`cost_per_side_pct`, `chain_returns`) is NOT an authorized X01 production accounting path.** | **binding: §3.4**; units: §3.2 |

### §3.1 The terminal-month exclusion

The ETF snapshot ends **2026-06-12**, so its terminal monthly row is labelled
`2026-06-30` while covering only 12 days (`LOCKBOX_PROCEDURE.md` §2.1). The
futures panel runs to a **full** 2026-06-30.

> **Declared before any computation: the paired comparison ends at
> 2026-05-31.** The June-2026 month is **excluded from both legs**, because a
> 12-day ETF month paired against a full futures month is a wrapper artefact, not
> a wrapper difference. It removes a known asymmetry rather than modelling it.

**The start is derived, not chosen — see §3.5.** The former text ("the start is
2010-07-31, the first month-end after the futures panel's floor with a full month
of futures returns") was **wrong**: it counted data availability as signal
eligibility and silently skipped the 12-month momentum warm-up. It is corrected
below and nothing is shortened to rescue it.

### §3.2 Price units — a VERIFIED defect that this contract must not inherit

`DATABENTO_W1_INPUT_VERIFICATION.md` §5 established from observed settlement
levels that **eight roots are quoted in cents** and the carry repository contains
**no divisor**:

`DIVISOR = 100` for `{ZC, ZS, ZW, KE, ZL, LE, HE, GF}`, `1` otherwise.

**Where the divisor must be applied — corrected twice.** An earlier revision
said the divisor was applied "at this program's boundary". Fable §7 found that
the **chained-return object was built on undivided prices**, so its roll-cost
term was 100x understated for the eight cents-quoted roots. A later revision of
this section then stated that requirement against the legacy callables
(`chain_returns` / `cost_per_side_pct`) — **that phrasing is superseded by §3.4,
which forbids those callables as an X01 production route**; the names survive
here only as lineage.

**The requirement, restated against the authorized route:** the settlement panel
passed into **`tsmom_chain_net_returns` must already be divided**. Under
cash-first accounting the divisor no longer touches the cost itself — the cash
cost is fixed dollars and is **divisor-invariant** — but it still binds through
the **notional denominator** `multiplier x qty x p_prev`. An undivided
cents-quoted price makes that denominator 100x too large and the cost **rate**
100x too small: the same defect, reached through the other term.
`production_divisor_regression` asserts **both** properties — cash cost
invariant, cost rate scaling by exactly the audited quote factor — and **fails
if the divisor is removed**.

Of X01's mapped roots, **CL, NG and GC are decimal-dollar (divisor 1)**; the
divisor **does** bite: the adopted ag proxy is `ZC ZS ZW LE HE GF`, and **all six of
those roots are cents-quoted** (`{ZC, ZS, ZW, KE, ZL, LE, HE, GF}`), so every ag
leg carries the divisor. **Every notional and cost computation applies
`settle / DIVISOR[root]` at the boundary.** A 100× notional error understates
the **cost rate** by 100× and would silently flatter the futures leg — the
exact direction that would manufacture a false `PRESERVATION_SUPPORTED`.

### §3.3 Instrument filtering and contract identity — VERIFIED requirement

**79.1% of the Databento delivery is calendar spreads.** Filtering is by the
**vendor's own `instrument_class == "F"` flag** in the `definition` schema — the
authoritative outright classification. **No string/symbol heuristic is used**;
the earlier "root + month code + year" description in this draft was wrong and
is corrected here.

**Persistent contract identity** is `instrument_id + "__" + expiration.date()`
(carry `pipeline.py::build_outright_panel`; findings F1/F6/F9/F10). **Raw symbol
is never the key** — CME's one-digit year repeats every 10 years and collapsed
two contracts into one column in the first attempt. Expiration is read from the
definition schema; no expiry inference remains.

---

### §3.4 Cost accounting — the ONE authorized production route (BINDING)

**This section is an active construction instruction, not commentary.** X01
production accounting **must** route through the TSMOM-local cash-first
implementation. Its entry point, in the bytes that were independently verified,
is:

```
research/extensions/wave1/run_x02a_v3.py :: tsmom_chain_net_returns(
        settle_dollars, front_series, root, qty=1, cost_multiplier=1.0)
    -> (net_return, gross_usd, cash_cost_usd, denominator)
    helper: production_roll_cash_cost(root, qty, cost_multiplier) -> (exit, entry)
```

**Verified semantics that X01 inherits and must not weaken:**

| # | Requirement |
|---|---|
| 1 | **Primitive cost is fixed dollars per side.** `cost_per_side_usd = tick_value + $2.50` (frozen carry `costs.py` / PREREGISTRATION §5). It does **not** scale with either contract's price. |
| 2 | **Exit and entry legs are charged independently.** A one-contract roll trades two sides and costs `qty x (C_exit + C_entry) = 2C`. CL: `$12.50 + $12.50 = $25.00`. |
| 3 | **Percentage cost is DERIVED, never primitive** — `cash_cost / (multiplier x qty x p_prev)`, against the **prior-held** notional. |
| 4 | **Percentages computed on different contract notionals are never summed.** This was the actual defect: charging both legs as percentages of the *old* notional yields `C + C x p_old/p_new` (CL 100 -> 110: **$23.863636**, not $25.00) and still reconciles to ~1e-16 against any implementation sharing that convention. |
| 5 | **Costs are charged on an actual roll only.** A day whose held contract is unchanged trades nothing and is charged nothing. This accounting object has **no rebalance leg**, so none is charged. A portfolio-level X01 construction that *does* rebalance must charge its rebalance trades under requirements 1-3, and must not reintroduce requirement 4's defect. |
| 6 | **No price splicing and no back-adjustment.** Every quantity comes from the single contract actually held over `t-1 -> t`. |

**Not authorized for X01 production accounting:**

`carry_costs.cost_per_side_pct` · `carry_returns.chain_returns`

These remain **available and unmodified** in `commodity-carry-research` and may
be called for **historical reproduction, cross-checking or reconciliation
reference**. They may **not** produce an X01 net return, an X01 cost figure, or
any quantity entering an X01 outcome state. The recorded finding
**`LEGACY_CARRY_PERCENTAGE_CONVENTION != AUTHORITATIVE_TSMOM_CASH_LEDGER`**
stands as history; `commodity-carry-research` is **not modified**, and whether
its convention should be revisited is the carry owner's question, not X01's.

**Verification status.** These semantics were established builder-side and then
independently accepted in a same-session GPT-6 Astra delta verification
(`PRODUCTION_CASH_ACCOUNTING = PASS`, `NET_LEDGER_INDEPENDENCE = MEANINGFUL`,
`ROLL_DAY_RECONCILIATION = PASS`, `NON_ROLL_RECONCILIATION = PASS`,
`COST_UNIT_PATH = PASS`, `EVENT_CHARGING = PASS`). **The route pinned by this
section is nevertheless a NEW byte-state of this draft and has not itself been
verified — precondition 1 stays `PENDING_INDEPENDENT_VERIFICATION` (§12).**

---

### §3.5 Eligibility, warm-up and the paired window — three DIFFERENT dates

The draft previously collapsed three distinct facts into one date. They are
separated here, each derived from a frozen rule applied to verified bytes.

| Fact | Value | How it is obtained |
|---|---|---|
| **DATA AVAILABILITY START** (futures) | **2010-06-06** | first settlement row of `settle_v2.parquet` — verified |
| First futures month-end price | **2010-06-30** | first month-end on or after the availability start |
| First futures **monthly return** | **2010-07-31** | needs two month-end prices |
| **FIRST SIGNAL-ELIGIBLE MONTH-END** | **2011-06-30** | the 12-month lookback at month-end `t` needs the price at `t−12`; `MOMENTUM_MIN_PERIODS = 4` requires **all four** lookbacks, so the 12-month leg binds. The 60-trading-day vol window is satisfied by ≈ 2010-08-31 and is **not** binding |
| **FIRST PAIRED EVALUATION MONTH** | **2011-07-31** | the signal at 2011-06-30 sets the position held through July 2011 |
| **HISTORICAL END** | **2026-05-31** | §3.1 terminal-month exclusion |
| **N** | **179 paired months** | inclusive count 2011-07 … 2026-05 |

**The ETF leg is not the binding constraint.** USO, UNG, GLD and DBA all have
prices from 2004–2007 (verified in the frozen panel), so the ETF leg's signal is
warm long before 2011. The **futures** leg sets the start, and the paired window
is the intersection.

**Prohibited shortcuts, named so they cannot be reintroduced.** No ETF-signal
bridge (using the ETF signal to position the futures leg during its warm-up);
no shortened composite (`MOMENTUM_MIN_PERIODS < 4`); no expanding-window signal;
no back-filled futures history. **None of these four** is authorised anywhere
in accepted V2,
and **losing 12 months is accepted rather than engineered away.**

**Initial position convention.** Before 2011-07-31 the futures leg holds
**no position and produces no return row**; the first evaluated month is the
first month with a fully-defined position. There is no zero-return padding: a
padded month is a fabricated observation, and it would deflate the volatility in
the denominator of Sharpe.

**Paired-date intersection rule.** The evaluated index is the **intersection** of
the two legs' month-ends after each leg's own eligibility rules are applied.
Month-ends are calendar month-ends; a month present in only one leg is dropped
from both.

**Missing / partial data — deterministic, declared here:**

| Case | Rule |
|---|---|
| **Missing root-month** (a mapped root has no eligible contract for the whole month) | the sleeve leg for that month is formed from the **remaining eligible roots of that ETF's map, renormalised to the same total leg weight**. Gross exposure is conserved; the substitution is recorded per month. |
| **Missing root, whole window** (e.g. a root whose panel history starts late) | the root is **excluded from the sealed map entirely** — see §15 O-1. A root is never spliced in mid-window. |
| **Missing ETF-month** | none exists in the frozen panel over the evaluated window; if one appeared, the month is dropped from **both** legs by the intersection rule. |
| **Partial month** | a month is evaluated only if **both** legs have a full calendar month of returns. The one known partial month, 2026-06, is excluded by §3.1. |
| **Incomplete sleeve** (one or more of the four ETF legs unavailable) | the month is **dropped from both legs**, not renormalised across ETFs — renormalising across ETFs would silently change the sleeve's composition, which is the object under test. Renormalisation is permitted **only within** one ETF's root map, per the first row. |

Every one of these is a **deterministic pre-declared treatment**. None depends on
an observed return, and none is selected after the fact.

### §3.6 The two sleeve return streams — frozen exactly

"The locked signal" is not a specification. Both streams are fixed here, to the
level at which two independent implementers would produce the same series.

**E — the ETF commodity-sleeve stream (the comparison leg).**

| Element | Frozen value |
|---|---|
| Source | `data/close_prices_raw.csv`, SHA256 `3d2a7a56dbd92d4ff8138cfd894c87f5ac5ac088a11165db870673e0c05c3c31` (the frozen `dataset.yfinance.multi-asset-etf-panel`) |
| Instruments | **USO, UNG, GLD, DBA** — the baseline commodity sleeve, `universe.py` |
| Prices | adjusted closes as delivered in that file; **no re-download, no re-adjustment** |
| Signal | the locked **mean-of-signs** composite (§3.7), on ETF month-end closes |
| Sizing | per-asset `signal x (0.10 / ann_vol_60d)`, `|w| ≤ 2.0` |
| Aggregation | **equal weight across the four ETFs** (`portfolio.py::equal_weight_aggregate`) |
| Lag | `positions = weights.shift(1)` |
| Risk scaling / capital normalisation | **sleeve-standalone**: per-asset vol targeting only. **No portfolio-level vol target and no gross-leverage cap** — those depend on the other four sleeves and would inject non-commodity information into a commodity wrapper test |
| Cost convention | `TRANSACTION_COST_BPS = 2.0` one-way per unit turnover (`config.py`), the baseline's own ETF convention — **ADOPTED at §15 O-6** |
| Cash / collateral yield · borrow | **NONE credited or charged** (`SYMMETRIC_ZERO_CARRY`, §15 O-6) |
| Net/gross | the **primary comparison is NET on both legs**; gross is reported as a diagnostic |
| Expense ratio | **already embedded** in the adjusted-close series and **NOT deducted again** — see §15 O-6, technical component (frozen, not an owner choice) |

**F — the futures commodity-sleeve stream (the leg under test).**

| Element | Frozen value |
|---|---|
| Source | `research/extensions/wave1/{settle_v2,oi_v2,contracts_meta}.parquet` — the accepted, independently verified panels |
| Instrument filter | vendor `instrument_class == "F"`; persistent key `instrument_id__expiration_date` (§3.3) |
| Roots | CL (USO) · NG (UNG) · GC (GLD) · **ag proxy (DBA) = `ZC ZS ZW LE HE GF`**, equal weight **1/6** of the DBA leg each — **ADOPTED, §15 O-1** |
| Within-ETF weights | each ETF's leg weight split **equally** across its roots, conserving total gross exposure and turnover (c1 D5 invariant, unit-tested there) |
| Price units | `settle / DIVISOR[root]` applied **before** any notional or cost computation (§3.2) |
| Signal input (PRIMARY) | the **chained held-contract return index** under the A1 roll rule — the same object X02a verified |
| **Signal surface** | **one signal per mapped ETF exposure, not per root.** CL, NG and GC are 1:1 so this is vacuous for them. For the ag leg the roots' **gross** chained return series are **equal-weighted into a single ag-basket return index first**, and the composite signal and 60-day vol are computed on **that index**, sized as one asset. **Rationale (outcome-independent):** the ETF leg carries exactly four signals; a per-root signal surface would give the futures leg nine, changing the number of independent bets and the rebalance surface, which is a **strategy** difference, not a **wrapper** difference. Costs remain per-root on the actually-held contracts |
| Roll rule (PRIMARY) | **A1 open-interest-max**, effective causal timing `t−2` close published during `t−1` (§3) |
| Sizing / aggregation / lag | **identical to E**, element for element |
| PnL accounting | `run_x02a_v3.py::tsmom_chain_net_returns` — the binding cash-first route (§3.4). Roll costs `qty x (C_exit + C_entry)`, `C = tick_value + $2.50`, charged on roll days only |
| Rebalance costs | charged on the **absolute traded contract quantity per contract identity** — `Σ_j |q_j,t − q_j,t−1| × C_j` (§3.8). The former `Δ|position| × C` expression is **deleted**: it misses reversals entirely and is not a traded quantity |
| Risk scaling / capital normalisation | sleeve-standalone, as E. Common unit-capital denominator, `SYMMETRIC_ZERO_CARRY` (§15 O-6) |
| Margin financing · collateral yield · borrow | **NONE credited or charged** — the return is defined on **full notional** (§15 O-6) |
| Expense ratio | **none** — futures have no fund ER. That asymmetry **is the wrapper difference under test**, not an accounting error |

**Symmetry statement.** Signal, lookbacks, vol window, vol target, weight cap,
aggregation, lag, rebalance timing, evaluation window and net/gross convention
are **identical** on both legs. The only intended differences are the ones the
wrapper question is about: instrument (ETF share vs futures contract), roll
(fund schedule vs A1), cost model (bps-on-turnover vs cash-per-side), and
expense ratio (embedded vs none).

> **A newly identified consequence, not resolved here.** §10 previously asserted
> the ETF leg is "a re-read of the published sleeve stream, constructing no new
> ETF series". That is **false** under this specification: no standalone
> commodity-sleeve monthly stream is published — `output/monthly_returns.csv` is
> portfolio-level and `output/dd_per_asset_net.csv` carries portfolio-leveraged
> contributions. **E must therefore be constructed.** Whether that construction
> is a governed ETF-panel trial is `D-ETF-COUNT`, which this draft does **not**
> resolve; it must be classified **before execution** (§10).

---

### §3.7 The signal — MEAN OF SIGNS, restored to the frozen V2 definition

**A defect this section exists to correct.** An earlier revision of §3 described
the composite as the *"mean of the {1,3,6,12}-month total returns"*. **That is
not the frozen baseline signal**, and as an active construction instruction it
contradicted accepted V2. It is corrected here and the correct definition is
reproduced from source rather than paraphrased.

**Authoritative sources, read rather than inferred:**

- `TSMOM_EXTENSION_RESEARCH_MAP_v2.md` §Baseline: *"Per asset, monthly: mean of
  `sign(R_1m), sign(R_3m), sign(R_6m), sign(R_12m)` on month-end closes → score
  ∈ {−1, −0.5, 0, +0.5, +1}"*, citing `src/signals.py::signal_method_b`.
- `src/signals.py::signal_method_b`, which takes `np.sign` of each horizon's
  return **first** and averages the signs **second**.

**The active construction instruction:**

```
R_n,t   = M_t / M_{t−n} − 1                     (simple n-month return, month-end closes)
s_t     = [ sign(R_1m) + sign(R_3m) + sign(R_6m) + sign(R_12m) ] / 4
```

| Frozen element | Value, from source |
|---|---|
| Order of operations | **sign FIRST, mean SECOND** |
| Return definition | `M_t / M_{t−n} − 1`, month-end closes only, backward-looking (`src/signals.py::momentum_return`) |
| **Zero / tie convention** | **`np.sign(0) = 0`** — a horizon with an exactly zero return contributes **0**, neither +1 nor −1. **This is the existing convention read from the code; no new one is invented.** V2's quoted score set {−1, −0.5, 0, +0.5, +1} is the set reachable when no horizon return is exactly zero; an exact zero is admissible and yields a multiple of 0.25 |
| Horizons required | **all four** (`MOMENTUM_MIN_PERIODS = 4`); the composite is **NaN** until every horizon exists — this is what fixes the first signal-eligible month at 2011-06-30 (§3.5) |
| Combine mode | `"mean"` — the **continuous** score, **not** `"vote"` (`np.sign(score)`) |
| Resample | `"ME"`, month-end |

**Three expressions that are NOT the signal, named so they cannot be substituted:**

1. **`mean(returns)`** — averaging the raw returns;
2. **`sign(mean(returns))`** — the `"vote"` variant applied to the wrong argument;
3. **`sign(mean(signs))`** — the `"vote"` combine mode, which V2 does not select.

### §3.7.1 Binding contract regression — mean-of-signs (no X01 data)

**A synthetic month-end path is constructed so the four horizon returns at the
final month are exactly `(+0.10, +0.10, +0.10, −0.01)`.** The implementation must
reproduce the first column and reject the others:

| Quantity | Value | Status |
|---|---|---|
| `sign` per horizon | `(+1, +1, +1, −1)` | — |
| **`mean(signs)` — REQUIRED** | **`+0.5`** | **the contract's signal** |
| `mean(returns)` | `+0.0725` | **REJECTED** |
| `sign(mean(returns))` | `+1.0` | **REJECTED** |

**Verified against the frozen implementation**: `signal_method_b` on that path
returns **`+0.500000`**, which lies on V2's score grid and differs from both
rejected expressions by more than 0.4. **This regression is binding at Stage C**
and any build whose signal returns `0.0725` or `+1.0` on this input **fails the
contract**, not merely a test. It uses **no X01 target data** — a hand-built
price path and pure arithmetic.

**A further pinned property:** the composite is **NaN** on a path with fewer than
twelve prior months, which is the mechanism behind §3.5's warm-up and is verified
on the same synthetic path.

---

### §3.8 Trade costs at the portfolio level — ABSOLUTE TRADED QUANTITY

**A defect this section exists to correct.** The contract previously charged
rebalance costs on `Δ|position|` — the change in position *magnitude*. **That is
not a traded quantity.** A reversal from `+1` to `−1` trades **two** contracts
and leaves `Δ|position| = 0`, so the cost was **zero where it should have been
two sides**. The same expression also returns 0 across a roll. It is deleted.

**The accepted X02 primitive is NOT changed**: `cost_per_side_usd = tick_value +
$2.50` remains the frozen per-side dollar cost, and every charge below is that
primitive applied to a traded side. This repair is confined to the **quantity**
the primitive is multiplied by.

**The governing expression, per contract identity `j`, per rebalance date `t`:**

```
trade_qty_j,t = | q_j,t − q_j,t−1 |          (SAME contract identity j)
cash_cost_t   = Σ_j  trade_qty_j,t × C_j     (C_j = cost_per_side_usd for j's root)
```

**Contract identity is the persistent key** `instrument_id__expiration_date`
(§3.3). Two different identities are **never** collapsed into one
position-magnitude difference: on a roll the outgoing identity goes `q → 0` and
the incoming goes `0 → q`, which are **two separate traded sides**, exactly the
cash-first roll semantics X02 verified. `trade_qty` is an absolute value, so a
reduction can never produce a negative cost.

**From the frozen sizing object to contract quantity** — using the
**already-authoritative** convention of §3.6, inventing no new sizing rule:

```
w_j,t = (leg weight from §3.6 sizing)          per-asset vol-targeted weight, |w| ≤ 2.0,
                                               split equally across the leg's roots
q_j,t = w_j,t × K / ( multiplier_j × P_j,t )   P = settle / DIVISOR[root]  (§3.2)
```

| Element | Frozen |
|---|---|
| `K` | the common unit-capital base of §3.6 / §15 O-6. **The result does not depend on it:** `q ∝ K`, so `cash_cost ∝ K` and the cost *rate* `cash_cost / K` is invariant. `K` is a bookkeeping constant, **not a tunable parameter** |
| **Quantity type** | **CONTINUOUS research quantities, not integer live contracts.** No rounding, no lot constraint and no minimum-tick position granularity is imposed. This is a stated **limitation of the research object**, not an implicit claim of tradability; integer-lot feasibility is a deployment question outside X01 |
| Roll days | the roll's two legs and any same-date rebalance are charged **together**, from the one expression above — a roll is not a special case, it is what the expression yields when the identity changes |
| Direction | `|·|` throughout; **a cost is never negative and never rebates** |

### §3.8.1 Binding contract regression — traded quantity (no X01 data)

Verified arithmetic, `C = $12.50` (CL):

| # | Position change | **Required traded qty** | Cash cost | What `Δ|position|` would have given |
|---|---|---|---|---|
| **A** | `+1 → +1` (no trade) | **0** | $0.00 | 0 ✔ |
| **B** | `+1 → 0` (close) | **1** | $12.50 | 1 ✔ |
| **C** | `+1 → +2` (add) | **1** | $12.50 | 1 ✔ |
| **D** | `+1 → −1` (**reversal**) | **2** | $25.00 | **0 ✘ — the defect** |
| **E** | roll: old `+1 → 0`, new `0 → +1` | **2** (two identities, one side each) | $25.00 | **0 ✘ — the defect** |

**All five verified**, together with: cost non-negative in every case; the roll
charging `{old: 1, new: 1}` rather than a single scalar; and the cost **rate**
being invariant to `K`. **Binding at Stage C**: a build returning 0 on case D or
E fails the contract.

---

## §4 Estimand — the scalar object, its inputs, and the boundary

**The primary estimand is a SCALAR, and it is not the paired difference series.**
The previous text conflated three different objects; they are separated here.

| Object | What it is | Role |
|---|---|---|
| `(F_t, E_t)`, t = 1…179 | the **paired monthly observations** | the **resampling unit / input pair**. NOT the primary statistic |
| `D_t = F_t − E_t` | the monthly difference series | a **diagnostic** (tracking error, max abs) |
| **`ΔS = Sharpe(F) − Sharpe(E)`** | the difference of the two legs' **annualised Sharpe ratios**, each computed on its own full stream | **THE PRIMARY SCALAR ESTIMAND** |

> **PRIMARY ESTIMAND — `ΔS = Sharpe(F) − Sharpe(E)`**, where `F` and `E` are the
> prospectively frozen paired monthly **net** streams of §3.6 over the 179-month
> window of §3.5.

**Sharpe, frozen to the byte-level convention already in the repository**
(`src/performance.py::sharpe_ratio`, unchanged and not re-specified here):

```
Sharpe(x) = mean(x) / std(x, ddof=1) * sqrt(12)
```

| Frozen element | Value |
|---|---|
| Frequency | **monthly** simple returns |
| Annualisation | **× √12**, applied to the monthly ratio |
| Raw or excess | **RAW returns — no risk-free rate is subtracted**, on **both** legs. This matches the repository convention and, being symmetric, cannot favour either wrapper. Cash/collateral yield is an **economic** question handled at §15 O-6, not smuggled in as a Sharpe convention |
| Risk-free / cash treatment | **none inside the Sharpe statistic**, and — following Aaron's adopted `SYMMETRIC_ZERO_CARRY` (§15 O-6) — **none in the return streams either**: no cash yield, margin financing or borrow is credited or charged on either leg. Had a carry convention been adopted it would have applied to **both** legs before the statistic, never to one |
| Denominator | **sample** standard deviation, `ddof = 1` |
| Zero / undefined volatility | if `std = 0` or `n < 2`, `Sharpe` is **undefined** (NaN). On the point estimate this is a **mechanical failure**, reported as such, not a performance outcome. In a bootstrap replicate it makes the replicate **invalid** (§6) |
| Minimum valid observations | the point estimate requires **all 179** paired months present; a replicate requires **≥ 24 distinct calendar months** and a positive standard deviation in **both** legs |
| Compounding | **none** — Sharpe is computed on simple monthly returns, not on a compounded equity curve |

**Standalone Sharpe of the futures leg is not admissible** for this claim
(Program v2 §0 rule 4): X01 modifies how the baseline's stream is produced, so it
is judged paired. **The pairing is preserved in the inference** (§6): `(F_t, E_t)`
are resampled **jointly**, and **both Sharpes and `ΔS` are recomputed inside
every replicate**.

**Four substitutions that are forbidden and are not used anywhere in this
contract:**

1. `mean(F − E)` as a substitute for `ΔS`;
2. `Sharpe(F − E)` as a substitute for `ΔS`;
3. **difference of significance** — comparing a futures interval that crosses
   zero against an ETF interval that does not;
4. **observed-power rescue** — post-hoc power from the realised effect.

**Path-level diagnostics are mandatory alongside**, because similar Sharpes do
not establish stream reproduction: monthly return correlation per mapped pair,
tracking error of `D`, `max |D_t|`, and the sign-agreement rate. These are
**reported**, never gates (§7), and **cannot become co-primary** (§8).

---

## §5 Outcome states — three, against a declared boundary

**`B = 0.15` annualised-Sharpe units — ADOPTED BY AARON**
(`O2_OWNER_DECISION = B_0.15`, §15 O-2), prospectively, **before any X01 paired
return series, Sharpe, `ΔS`, bootstrap result or crisis statistic existed.** It
is in the same units and on the same scale as `ΔS`. The non-inferiority boundary
is **`−B` = `−0.15`**. Let `[L, U]` be the 95 % confidence interval for `ΔS`
from §6.

**Endpoint convention — frozen, exhaustive, mutually exclusive:**

| State | Condition | With `B = 0.15` | Endpoint |
|---|---|---|---|
| `PRESERVATION_SUPPORTED` | **`L > −B`** | **`L > −0.15`** | **strict** |
| `MATERIAL_DEGRADATION_SUPPORTED` | **`U < −B`** | **`U < −0.15`** | **strict** |
| `UNRESOLVED_INSUFFICIENT_PRECISION` | **otherwise** — i.e. `L ≤ −B ≤ U` | **`L ≤ −0.15 ≤ U`** | inclusive |

> **There is no unclassified case.** The three conditions partition the real
> line: exactly one holds for every `(L, U)` with `L ≤ U`. In particular
> **`L = −B` exactly → `UNRESOLVED`**, **`U = −B` exactly → `UNRESOLVED`**, and
> **`ΔS = −B` exactly** is not itself a classification input — only the interval
> endpoints classify. A bound that merely *touches* `−B` never supports a claim.

**Four inference rules, stated so they cannot be re-derived away:**

**Four inference rules, stated so they cannot be re-derived away:**

1. **Classification is against `−B`, never against zero.** An interval containing
   zero is **not** by itself unresolved; an interval excluding zero is **not** by
   itself decisive. "CI contains zero ⇒ unresolved" is **not** used.
2. **No difference-of-significance logic.** The v1 rule comparing a futures
   interval that crosses zero against an ETF interval that does not is **deleted
   and not reinstated**. Difference of significance is not significance of
   difference.
3. **No observed-power rescue.** Post-hoc power computed from the realised effect
   may **not** be used to reinterpret an unresolved result. Precision is assessed
   **prospectively at §6**, for the *paired* estimand.
4. **Nonsignificance is not falsification.** `UNRESOLVED_INSUFFICIENT_PRECISION`
   maps to KB `unresolved`. `MATERIAL_DEGRADATION_SUPPORTED` maps to
   `not_promoted` **with the margin recorded**. `falsified` is not available to a
   single family (KB decisiveness convention, verified).

**`B` was set by Aaron, not by this session**, as an economic policy threshold —
`OWNER_DECISION_O2_B = 0.15`. Its derivation, and the material he was given, are
at **§15 O-2**.

> **`OWNER_DECISION_O2_B = 0.15` (annualised Sharpe). ADOPTED and CLOSED.**
> **`B` is not alterable after target outcomes become visible; there is no
> fallback `B`; and no alternative value of `B` may be reported after execution
> as a competing pass/fail specification.** The candidate values displayed at
> §15 O-2 are **historical decision material only** and are **not executable
> alternatives**.

**Kill-branch reachability — computed, not asserted.** The former text reasoned
from "an expected pair correlation ≥ 0.9" as though it were a measured
strategy-stream correlation. It is not: MAP_v2's ≥ 0.9 is a *designer
expectation* about **price** pairs, and the quantity that drives the precision of
`ΔS` is the correlation between the two **strategy return streams**, which is
unobserved and must not be assumed. §6 replaces that shortcut with a declared
**scenario grid**, and §15 O-2 tabulates what each candidate `B` implies for the
reachability of **both** branches. **Both branches must be shown reachable
before sealing**, per `lesson.rule-domain-analysis-before-freeze`; with
`B = 0.15` adopted, §15 O-2 records what each branch requires of the point
estimate under the declared scenario grid.

---

## §6 Inference

**O-3 is RESOLVED here.** Every element below is frozen; none is chosen after
seeing an X01 outcome, and no element was selected by inspecting the target
sample.

### §6.1 The procedure, frozen

| Element | Frozen value |
|---|---|
| Estimand | **`ΔS = Sharpe(F) − Sharpe(E)`** (§4) — a scalar, recomputed inside every replicate |
| Resampling unit | the **pair** `(F_t, E_t)`, t = 1…179, resampled **jointly**. The two legs are never resampled independently, and no index is drawn for one leg that is not drawn for the other |
| Bootstrap family | **stationary bootstrap** (Politis & Romano 1994) — geometric block lengths, circular wrap. The carry study's family is cited as precedent, **not inherited automatically**; the *value* below is derived independently |
| **Expected block length** | **L = 12 months** — a **prospectively chosen, design-based dependence horizon**, fixed as a **sealed inference convention** (option A of the three the A2 permitted: a single justified value). **It is anchored to the longest signal-formation window**: the composite's longest lookback is **12 months** (`MOMENTUM_LOOKBACKS_MONTHS` max), so consecutive months' positions are built from overlapping formation windows, and the design horizon is set to that span. The 60-trading-day (≈ 3-month) vol window is shorter and does not bind the choice. **The carry study's 21 is in trading days and is NOT transplanted**, and no universal block-length rule is invented |
| **What `L = 12` does NOT assert** | **It is a convention, not a theorem and not an empirical finding.** It does **not** claim that dependence in `F`, `E` or `ΔS` cannot extend beyond 12 months. Real dependence can outlast the formation window through **persistent positions, volatility scaling, common market dependence and regime persistence**, and the stationary bootstrap's geometric blocks place mass at every length in any case. `L` fixes the resampling scale **the contract commits to in advance**; it makes no claim about the true dependence structure |
| Why the value cannot have been steered | `L = 12` was fixed **before any X01 outcome exists**, from a **structural property of the signal specification alone** (`config.py`), with **no target-sample quantity consulted** and **no alternative value computed or compared**. That — not any presumed direction of effect on the interval — is what makes it unsteerable. **No claim is made that a longer `L` necessarily or monotonically widens the interval**: in a finite sample it need not, and such a claim would be an unverified assertion doing the work of a safeguard |
| Replications | **10,000** (`config.py BOOTSTRAP_N`) |
| CI level | **95 %** (`config.py CI_LEVEL`) |
| CI construction | **percentile interval**: `L = ` 2.5th and `U = ` 97.5th percentile of the 10,000 `ΔS*` values. Percentile is chosen over BCa deliberately — BCa's acceleration term is itself estimated from the target sample and would add an outcome-touching component to the interval. **No alternative interval is computed and no interval is selected after the fact** |
| Seed protocol | master seed **7** (`config.py RANDOM_SEED`). Per-arm streams are `numpy.random.SeedSequence(7).spawn(3)` taken in the **fixed order [primary, S1, S2]**, so each arm's stream is determined before any arm runs. The three spawned entropy values are written into the sealed text at seal time and the run reproduces bit-for-bit |
| **Degenerate / invalid replicates** | a replicate is **invalid** if either leg has `std = 0` or the replicate spans **< 24 distinct calendar months**. Invalid replicates are **discarded and counted — never re-drawn** (re-drawing conditions the sample on validity and biases the interval). If **fewer than 9,500** valid replicates remain, the result is `INFERENCE_PROCEDURE_FAILURE` — a **mechanical** condition, reported with the invalid count, and explicitly **not** one of the three outcome states of §5 |
| Multiplicity | **DECIDED, not deferred** (§8.3). The family `F-X01` contains **exactly one confirmatory test** — the primary. S1 and S2 emit **no decision and no verdict**, so there is **no multiple-testing exposure to correct**. **`BH_FDR_REQUIRED = NO`**: no multiplicity correction is applied to the primary, to S1 or to S2. Program v2 §0 rule 5 requires the family's multiplicity treatment to be *stated*; this is that statement, and BH-FDR q = 0.10 is **not adopted** |

### §6.2 Prospective precision and reachability — outcome-independent

**What the previous version did wrong.** It assessed precision "from the observed
pair correlation" and elsewhere reasoned from `expected correlation ≥ 0.9`.
Neither is admissible: MAP_v2's ≥ 0.9 is a designer expectation about **price**
pairs, the quantity that matters is the unobserved **strategy-stream**
correlation `ρ`, and no target-sample quantity may enter a pre-seal precision
exercise at all.

**What is used instead.** A declared **formula evaluated over a declared grid**.
For paired samples the asymptotic variance of a Sharpe difference (Jobson–Korkie,
Memmel correction), in **monthly** Sharpe units, is

```
Var(ΔS_m) ≈ [ 2(1 − ρ) + ½ ( S_F² + S_E² − 2 ρ² S_F S_E ) ] / N ,   N = 179
```

annualised by ×√12. **No X01 sample quantity appears anywhere in it** — `N` comes
from the frozen eligibility rules (§3.5) and `ρ`, `S_F`, `S_E` are **assumed
scenario values**, not measurements.

**Design-approximation 95 % half-width of `ΔS` (annualised Sharpe units), N = 179:**

| assumed S (both legs) | ρ = 0.50 | ρ = 0.70 | ρ = 0.90 | ρ = 0.95 |
|---|---|---|---|---|
| 0.20 | 0.508 | 0.394 | 0.227 | 0.161 |
| 0.40 | 0.510 | 0.395 | 0.228 | 0.162 |
| 0.60 | 0.513 | 0.398 | 0.230 | 0.163 |
| 0.80 | 0.518 | 0.402 | 0.233 | 0.165 |

**What this calculation IS — stated exactly, so it cannot be over-read:**

- a **pre-outcome design approximation / diagnostic**, computed at contract
  design to check that the study is worth running at all;
- **based entirely on declared scenario assumptions** — `ρ`, `S_F` and `S_E` are
  values this contract *stipulates* across a grid, chosen because the truth is
  unknown;
- a **sanity check on reachability**: whether *both* outcome branches can be
  reached at all under plausible assumptions, per
  `lesson.rule-domain-analysis-before-freeze`.

**What it is NOT — five explicit disclaimers:**

1. **NOT an estimate of the actual X01 paired-stream correlation.** `ρ` is
   stipulated, never measured. The grid spans 0.50–0.95 precisely because the
   strategy-stream correlation is unknown before execution, and MAP_v2's "≥ 0.9"
   is a *price*-pair expectation that is not used here.
2. **NOT proof of stationary-bootstrap coverage.** The formula is an
   iid-normal asymptotic approximation. It says nothing about the finite-sample
   coverage of the sealed §6.1 procedure, which is not established here and is
   not claimed.
3. **NOT a bound on the interval the sealed procedure will produce.** Positive
   serial dependence *typically* inflates variance relative to iid, so the
   bootstrap interval will **often** be wider — but that is a tendency, **not a
   guarantee**, and in a finite sample the realised interval may be narrower.
   **No monotone or one-sided relationship between this table and the sealed
   interval is asserted or relied on.**
4. **NOT an input to `B`.** `B = 0.15` was adopted by Aaron as an **owner
   utility / economic tolerance** and is explicitly **not** selected from this
   table, from observed X01 performance, from an anticipated probability of
   passing, from an observed paired correlation, from bootstrap results or from
   historical candidate optimisation (§15 O-2). This table only *displayed* each
   candidate's mechanical consequence before the decision was taken.
5. **NOT a substitute for the sealed inference.** The contract's outcome is
   determined **solely** by the §6.1 bootstrap interval. If the two disagree,
   **§6.1 governs and this table is discarded** — it never reinterprets,
   adjusts or overrides a realised result.

**One thing the table does say**, and it is a design observation rather than a
statistical claim: precision is governed far more by `ρ` than by the Sharpe level
— the columns move, the rows barely do.

**It constructs and exposes no X01 performance quantity.** It is a function of
declared constants only, and computing it revealed nothing about `F`, `E` or
`ΔS`.

**Consequence carried into §15 O-2**: the reachability of both outcome branches
is a function of `B` and `ρ`, and that mapping — not a preferred value — is what
Aaron is given.

---

## §7 Diagnostics that are NOT gates

Reported, never used to pass or fail the primary claim:

- Monthly return correlation per mapped pair (MAP_v2's "expect ≥ 0.9" is a
  designer expectation, **not** a gate).
- **Sign-agreement rate** between the ETF and futures composite. MAP_v2 is
  explicit: a low rate is a **diagnostic warning requiring investigation**, it is
  **not** proof of an implementation defect, and it grants **no permission to
  tune the futures construction toward higher agreement**. Accounting invalidity
  is established only by an actual mechanical/causal/accounting failure in X02a.
- Tracking error, max monthly |Δ|, turnover and realised cost per leg.

### §7.1 Crisis windows — exact, canonical, and fixed before any outcome

**Crisis behaviour is a claim-scoped deployment diagnostic, not a kill.**
Program v2 §0 rule 11: a crisis-preservation *requirement* applies only where a
candidate replaces the deployed stream while retaining its defensive role or
explicitly claims to. X01's commodity sleeve is one sleeve of five; it makes no
standalone defensive claim, so **no crisis-retention gate applies**. **Exact windows, both inclusive of their endpoint months:**

| Window | Months included | Count | Source of the definition |
|---|---|---|---|
| **COVID 2020** | **2020-02-29, 2020-03-31, 2020-04-30** | 3 | the repository's **pre-existing canonical** definition, `config.py::REGIMES["COVID 2020"] = ("2020-02-01", "2020-04-30")` — adopted verbatim, **not redefined here** |
| **CY2022** | **2022-01-31 … 2022-12-31** | 12 | plain calendar year; unambiguous, no definition needed |

**Calculation convention, frozen:** a window statistic is computed on the
**subset of the 179 evaluated paired months whose month-end falls inside the
window**, using the same §4 Sharpe convention and the same net streams. Windows
are **not** re-centred, extended, shifted or split; no alternative COVID window
is computed; and the windows were fixed from a pre-existing artifact **before any
X01 outcome exists**, so they cannot have been chosen for their result.

**GFC 2008 is absent and cannot be reported** — the futures panel starts
2010-06-06. `config.py` also defines a "Calm 2012-2019" regime; it is **not** an
X01 window and is not reported here.

**No crisis pass/fail gate exists, and no crisis window can rescue or overturn
the primary result.**

**Wave-1 evidence bearing on how crisis behaviour should be read** (from
`EDGE_DIAGNOSTICS.md`, on the ETF baseline, context T0): the unconditional
monthly convexity term vs SPY is indistinguishable from zero (R² = 0.0012,
p = 0.98), while correlation **within the SPY left tail is −0.516**. The
defensive character sits in tail conditioning, not in an unconditional
quadratic — so crisis diagnostics here use **declared event windows**, not a
full-sample convexity coefficient.

---

## §8 Declared secondary arms — named now, run after the primary

Both are declared **before** the seal and neither runs before the primary arm is
recorded.

### §8.0 The evidential hierarchy — explicit, and not re-orderable

| Tier | Members | What it may do |
|---|---|---|
| **PRIMARY** | the **single** predeclared Sharpe non-inferiority test of `ΔS` against `−B` (§4, §5) | determines the contract's outcome |
| **SECONDARY** | **only** S1 and S2 below, exactly as specified | characterise the robustness of the primary; reported whatever they show |
| **DIAGNOSTIC** | tracking error, `max|D_t|`, per-pair correlation, sign agreement, turnover, realised cost, crisis windows (§7) | describe; never gate |

**Three rules that close the escape routes:**

1. **There is no tracking co-primary and no path-metric co-primary.** Accepted V2
   fixes Sharpe non-inferiority as PRIMARY and tracking/path metrics as
   DIAGNOSTIC; this contract does not reopen that. *(The former open item O-4,
   which asked whether tracking should be co-primary, was an **invalid** open item
   — it proposed to reopen a settled V2 decision — and is **removed**, §9.)*
2. **A diagnostic cannot rescue a failed primary.** No combination of
   diagnostics converts `MATERIAL_DEGRADATION_SUPPORTED` or
   `UNRESOLVED_INSUFFICIENT_PRECISION` into support.
3. **A secondary arm cannot become primary after outcomes are seen**, and
   neither S1 nor S2 may substitute for a failed primary. **No "whichever
   passes" rule exists.**

### §8.1 S1 — construction sensitivity (former X02b), fully specified

**What S1 changes — exactly one thing:** the **price series the momentum
composite is computed on**.

| | PRIMARY | **S1** |
|---|---|---|
| **Signal input** | the **chained held-contract return index** under A1 | a **causally built ratio-adjusted price series** |
| roll rule | A1 open-interest-max | **A1 — unchanged** |
| PnL accounting | `tsmom_chain_net_returns` (cash-first) | **unchanged** |
| roots, map, weights | §3.6 | **unchanged** |
| vol window, target, cap, aggregation, lag | §3.6 | **unchanged** |
| costs, price-unit divisor | §3.2 / §3.4 | **unchanged** |
| window, N, pairing, ETF leg `E` | §3.5 / §3.6 | **unchanged** |
| estimand, boundary, inference | §4 / §5 / §6 | **unchanged** (own seed stream) |

**The alternate construction, resolved outcome-independently.** V2's X02 entry
names two legitimate causal constructions and requires one to be fixed ex ante;
it does not fully determine the second. The **one bounded ambiguity** —
*how* the ratio adjustment is built — is resolved here, **not** deferred to an
owner decision:

> **Forward cumulative ratio adjustment — the exact equation.**
>
> ```
> k_0        = 1                                   at the first eligible date
> at roll τ: k_new = k_old × P_old,τ / P_new,τ      NOTE THE DIRECTION
> for t ≥ τ: P_adj,t = k_new × P_new,t              until the next roll
> for t < τ: P_adj,t is UNCHANGED                   history is never restated
> ```
>
> **The direction was previously wrong.** The earlier text formed
> `r = P_new / P_old` and multiplied the running factor by it. With
> `P_old,τ = 100`, `P_new,τ = 110` and `k_old = 1` that gives
> `k_new = 1.1` and an adjusted roll level of `1.1 × 110 = 121` — a **21 %
> phantom jump at every roll**, precisely the discontinuity amplification this
> construction exists to avoid. The corrected factor is
> `k_new = k_old × P_old,τ / P_new,τ`, which **divides out** the new contract's
> price level and re-expresses it on the old contract's scale.

**Timing and inputs — every element frozen:**

| Element | Frozen value |
|---|---|
| **Roll event `τ`** | the **first date at which the A1 held-front series names the new contract** — the same `τ` at which `tsmom_chain_net_returns` charges the roll's two cash legs. The signal-input series and the PnL therefore roll on the *same* date; they never disagree about when a roll happened |
| **Which old settlement** | the **outgoing** contract's settlement **at `τ`**, `P_old,τ` |
| **Which new settlement** | the **incoming** contract's settlement **at `τ`**, `P_new,τ` |
| Both divided | yes — `settle / DIVISOR[root]` applied before the ratio (§3.2). The ratio is dimensionless, so the divisor cancels; it is applied anyway so that `P_adj` is in dollars |
| **When the new factor applies** | **at the roll observation `τ` itself, and every observation after it** until the next roll. At `τ` the two expressions agree exactly — `k_new × P_new,τ = k_old × P_old,τ` — so the series is continuous **by construction**, not by approximation |
| **Information available at `τ`** | both settlements of date `τ`, known at `τ`'s close. The A1 roll decision itself already uses open interest as of the `t−2` close (§3). **Nothing after `τ` is used** |
| **Compounding** | successive roll factors compound multiplicatively: `k_m = k_{m−1} × P_old,τ_m / P_new,τ_m`. Continuity holds at every roll independently |
| **If the two contracts share no settlement at `τ`** | use the **latest date ≤ `τ` on which both have a settlement**, searching back at most **10 sessions**. If no such date exists, that root's S1 series is recorded **`S1_ADJUSTMENT_UNDEFINED`** and **reported as such** — S1 is a sensitivity, so an undefined root is disclosed, never silently dropped, patched or interpolated |

**Binding continuity regression (no X01 data), verified arithmetic:**

| Step | Input | Required adjusted level |
|---|---|---|
| pre-roll, `k_old = 1` | old contract at 95 | **95** |
| roll `τ`, via **old** contract | `P_old,τ = 100` | **100** |
| roll `τ`, via **new** contract | `P_new,τ = 110`, `k_new = 100/110 = 0.909091` | **100** — *not 121* |
| next observation | new contract raw **121** | **110** — a clean **+10 %** from 100 |
| second roll | old 115.5 → new 60 | `k₂ = k₁ × 115.5/60`; continuity holds again |

**All verified**, together with: the adjusted return over `τ → τ+1` equalling the
**new contract's own** raw return exactly; and the pre-roll level of 95 being
**unchanged** by the roll — history is not restated. **Binding at Stage C**: a
build producing **121** at the roll fails the contract.

**Why this resolution and no other.** The conventional back-adjustment applies
ratios *backwards*, which restates history using future roll ratios and is
therefore non-causal — the exact defect X02a's truncation-invariance test exists
to catch. Forward accumulation is the unique variant that (i) is causal, (ii)
needs no parameter, and (iii) leaves a truncated prefix identical to the
untruncated one. **The reason is a causality property, not a performance
property**, and no return series was consulted to choose it.

**Why this is a construction sensitivity and not a new primary strategy.** The
traded object, the roll, the cost model, the accounting path and the position
sizing are **identical**. Only an information transform feeding an unchanged
signal rule differs. **Back-adjusted prices never produce traded PnL**
(V2 X02): the ratio-adjusted series is a **signal input only**, and every dollar
in S1 still comes from `tsmom_chain_net_returns` on the actually-held contracts.

**Interpretation.** S1 answers "is the primary conclusion an artefact of the
signal-input construction?" **descriptively**.

> **The former conditional consequence is DELETED.** It read: *"A material
> S1/primary divergence makes the signal-input construction a declared degree of
> freedom for every later futures hypothesis."* **"Material" was never defined**,
> and no materiality threshold is required by accepted V2 — so rather than invent
> a threshold to keep the sentence, the **condition is removed and the
> consequence made unconditional**:
>
> **`SIGNAL_INPUT_CONSTRUCTION_DOF = REQUIRED`.** The signal-input construction
> **is** a declared degree of freedom for every later futures hypothesis,
> **regardless of what S1 shows**. This mirrors `ROLL_RULE_DOF = REQUIRED`
> (§8.2), is a governance declaration rather than an inference, and needs no
> threshold. **S1 emits no verdict** (§8.3).

### §8.2 S2 — roll-rule sensitivity (former X03 performance arm), bound to the accepted comparator

**S2 changes exactly one thing: the roll rule.** Everything else — signal input
(the chained index), costs, sizing, aggregation, lag, window, `E`, estimand,
boundary, inference — is **identical to the primary**.

> **The S2 comparator is `commodity-carry-research/src/robustness.py::fixed_calendar_front_series`,
> called directly and unmodified** — the same function whose structural output
> X03 independently verified. **Generic wording such as "the fixed-calendar rule"
> is insufficient and is not used**: it previously admitted at least two
> different implementations.

**Its accepted mechanics, restated so the binding is unambiguous:**

| Element | Accepted mechanic |
|---|---|
| Roll timing | the **last business day of the month preceding the front contract's expiry month**. Parameter-free — there is no `N` to tune |
| Candidate selection | the **A2 existence filter**: the earliest later expiration whose **open interest at `t−1` is strictly positive** |
| OI information lag | **`t−1` throughout**; no look-ahead |
| Superseded comparator | the naive "5 calendar days / next listed month regardless of liquidity" variant that Fable §8 found mis-described is **not used**, and its numbers are not cited |

**Carried forward unchanged:** `ROLL_RULE_DOF = REQUIRED` and
`ROLL_RULE_ECONOMIC_MATERIALITY = UNRESOLVED`. The verified structural
disagreement between A1 and this comparator is large (mean 48.4 %, every root
> 10 %, `FUTURES_INFRA_TRUTH.md` §6), which is **why** the roll rule is a declared
degree of freedom — that is a **structural** fact and is **not** a performance
claim.

**No economic-materiality threshold is declared for S2, deliberately.** X01's
primary decision does not need one: S2 is reported as a `ΔS` alongside the
primary's `ΔS`, with its own interval, and the reader compares them. Inventing a
materiality bar here would create a second, unowned threshold with its own
selection surface. **If Aaron later wants a materiality verdict on the roll rule,
its threshold must be declared before outcome access**, in the contract that asks
for it. **S2 cannot replace a failed primary.**

---

### §8.3 Secondary inference — DECIDED, and deliberately minimal

**A defect this section exists to correct.** The contract previously left the
family's multiplicity treatment as a *"challengeable default, not a decided
rule"*, and attached a consequence to an undefined *"material divergence"*.
Neither could survive a seal: an undecided rule is a post-hoc choice waiting to
happen. Both are decided here.

**What accepted V2 actually requires — read before deciding.**

- Program v2 §0 rule 5: a preregistration *"states the family's multiplicity
  treatment (the repo's standing proposal is BH-FDR q = 0.10, **carried as a
  challengeable default**)"*. It requires the treatment to be **stated**; it does
  **not** mandate BH-FDR.
- Program v2 family table: `F-X01` = *"primary A1 arm; secondary arms: calendar
  roll, construction sensitivity"*, multiplicity scope *"one contract;
  secondaries declared"* — **declaration** is the treatment.
- Program v2: *"Secondary metrics and cost levels — declared inside each family;
  **no 'whichever passes' rule**"*.
- MAP_v2 X03: the consequence of a material roll rule is that it *"must be
  preregistered as a declared degree of freedom in every later futures
  hypothesis"* — **already discharged unconditionally** by
  `ROLL_RULE_DOF = REQUIRED` (§8.2), so **no materiality threshold is needed to
  trigger it**. The same reasoning discharges S1 via
  `SIGNAL_INPUT_CONSTRUCTION_DOF = REQUIRED` (§8.1).

**V2 therefore does NOT require S1 or S2 to be independent promoted hypothesis
tests.** The minimum design is adopted:

```
SECONDARY_INFERENCE_ROLE  = DESCRIPTIVE_SENSITIVITY
BH_FDR_REQUIRED           = NO
S1_S2_PROMOTION_POWER     = NONE
SECONDARY_MATERIALITY_GATE = NONE
```

| Arm | Role | May it decide anything? |
|---|---|---|
| **PRIMARY** | the single confirmatory test: `ΔS` against `−0.15` under §6.1 | **YES — it alone determines the contract's outcome** |
| **S1** | predeclared **construction sensitivity**, descriptive/secondary | **NO** |
| **S2** | predeclared **roll-rule sensitivity**, descriptive/secondary | **NO** |

**What S1 and S2 report, and nothing else:** their own `ΔS` point estimate and
95 % interval under the **identical** §6.1 procedure and their own seeded
streams, alongside the primary's. **Reported side by side; no comparison test
between arms is computed.**

**Six prohibitions, stated so they cannot be re-derived away:**

1. **No alternative primary decision.** No outcome state is ever assigned from S1
   or S2.
2. **No rescue.** A failed or unresolved primary is **not** recoverable by a
   secondary, in whole or in part.
3. **No promotion rule.** Neither secondary can be promoted to a hypothesis in
   its own right inside this contract; that requires a **new** preregistration.
4. **No significance-shopping.** No p-value, no threshold, no pass/fail label is
   attached to a secondary, and the arms are not scanned for the most favourable.
5. **No materiality conclusion.** **No materiality threshold exists**, so
   **immateriality is never claimed** — consistent with MAP_v2's rule that
   immateriality is claimed only within a declared margin and never from "no
   significant difference". `ROLL_RULE_ECONOMIC_MATERIALITY` stays `UNRESOLVED`.
6. **No multiplicity correction.** There is one confirmatory test, so there is
   nothing to correct; **BH-FDR q = 0.10 is not adopted**, and its former status
   as an undecided default is removed.

**If Aaron later wants a materiality verdict** on either the roll rule or the
signal-input construction, its threshold must be declared **before outcome
access**, in the contract that asks for it — never retrofitted to this one.

---

## §9 Open items — DISPOSITION (O-1, O-2 and O-6 now RESOLVED_BY_OWNER)

| # | Status after the A2 repair | Where it now lives |
|---|---|---|
| **O-1** — ag-basket composition | **RESOLVED_BY_OWNER, 2026-09-08.** `O1_OWNER_DECISION = ADOPT_OPTION_B` → `ZC ZS ZW LE HE GF`, equal weight 1/6, classified `FIXED_PROXY_WITH_COMPOSITION_MISMATCH`. Taken **before any X01 outcome existed**. Option A is **not** an evaluated X01 alternative | **§15 O-1** |
| **O-2** — the degradation boundary `B` | **RESOLVED_BY_OWNER, 2026-09-08.** `O2_OWNER_DECISION = B_0.15` → **`B = 0.15` annualised-Sharpe units**, boundary `−0.15`. An owner utility / economic tolerance, taken **before any X01 outcome existed**. No fallback `B`; no alternative `B` is executable | **§15 O-2** |
| **O-3** — bootstrap block length | **RESOLVED, technically, outcome-independently.** Stationary bootstrap, **L = 12 months**, mechanism-justified; family, level, CI construction, replications, seeds and degenerate handling all frozen | **§6.1** |
| **O-4** — tracking error as co-primary | **REMOVED as an invalid open item.** Accepted V2 already fixes Sharpe non-inferiority as PRIMARY and tracking/path metrics as DIAGNOSTIC. O-4 proposed to reopen a settled V2 decision, which this contract has no authority to do. The hierarchy is now stated explicitly and is not re-orderable | **§8.0** |
| **O-5** — D9 classification ceiling | **NOT a seal blocker for X01, and not resolved here.** For X01 the ceiling is fixed at **`AT_MOST_SUPPORTED_IN_T1_FOR_PAIRED_WRAPPER_PERFORMANCE`** (§9.1). D9 itself **may remain open beyond X01** | **§9.1** |
| **O-6** — capital, cost and financing comparability | **RESOLVED_BY_OWNER, 2026-09-08.** Technical half already frozen; `O6_OWNER_DECISION = ADOPT_OPTION_1_SYMMETRIC_ZERO_CARRY` for the policy half. Taken **before any X01 outcome existed**. Option 2 is **not** an alternative success route | **§3.6 + §15 O-6** |

### §9.1 O-5 — the X01 claim ceiling, fixed; D9 left open

For **X01 alone**, and regardless of how large or small the realised Sharpes are:

> **`AT_MOST_SUPPORTED_IN_T1_FOR_PAIRED_WRAPPER_PERFORMANCE`.**
> X01 may support a **narrowly scoped historical wrapper-transfer / economic-
> preservation** claim. It **cannot independently confirm** the original
> ETF-informed alpha, because the futures panel covers the **same 2010–2026
> economic history** on which the design was exposed. **A very high Sharpe does
> not change this** — precision is not independence.

**Three things this ceiling is not.**

1. **It is not weakest-tier inheritance.** The cap applies to **this test**, in
   **its** context (T1), for **this** claim type. It is not inherited by the
   candidate, the family, or any later test. `SAMPLE_REUSE.md` §0 Rule 2 is
   restated, not weakened.
2. **It is not permanent.** Genuinely independent later evidence (T2/T3/T4) is
   classified **on its own validation context** and may reach a stronger status.
3. **It is not a new seal blocker.** D9 — whether *any* sealed same-period
   wrapper comparison may ever exceed `supported` — is a broader question for
   Aaron and the KB curator, and **X01 does not wait on it**. X01 proceeds under
   the cap above; if D9 later relaxes the general rule, X01's record is reread
   under that rule rather than rerun.

**A number discussed historically is not thereby sealed.** MAP_v2's "≥ 0.9"
correlation, "85%" sign agreement and v1's "70%" crisis retention are recorded
as **designer proposals or expectations**, and none is adopted as a gate by this
draft. In particular **the "≥ 0.9" is never used as an observed quantity** — see
§6.2, which replaced exactly that shortcut.

---

## §10 Exposure and trial accounting — prospective

| Object | Treatment |
|---|---|
| **EXPOSURE_EVENT** | The X01 run is the program's **first futures `TARGET_PERFORMANCE_EXPOSURE`**. It is appended to `ops/EXPOSURE_LEDGER.md` **before the outcome is read**, with sample snapshot, scope, classification, outputs to be revealed and seal timing. Classification is by **actual outputs**, not by lane or intent. |
| **VARIANT_ATTEMPT** | The primary arm and each of S1, S2 are **distinct evaluated configurations** → **3 attempt rows**, each with design parent and family, created when evaluated. **Never deleted, merged or consolidated after observing PnL correlation or any outcome** — the expected ≥ 0.9 correlation with the ETF sleeve is *anticipated* and is not grounds to collapse rows. |
| **HYPOTHESIS_FAMILY** | **F-X01** = primary + S1 + S2, declared **here, before any member runs** (Program v2 §11). |
| **GOVERNED_N_TRIALS_CONTRIBUTION** | Databento panel, verified convention: **one trial per distinct constructed strategy-return series**, diagnostics excluded. See §10.1 — the contribution is **`+3`**, and the *resulting total* is **not** written as a frozen number here. |

### §10.1 The contribution is `+3`; the resulting total is computed at execution

**`+3`, conditional on exactly these conditions holding at execution:**

1. exactly **three** constructed strategy-return series are evaluated — the
   primary `F`, S1's `F`, and S2's `F`;
2. **no additional governed construction** is introduced (no extra cost level,
   sizing variant, basket variant or roll construction);
3. no **intervening shared contribution** from another project changes the
   cumulative reference between this seal and this execution.

**Written conceptually, never as a frozen arithmetic string:**

```
current frozen reference        = 14        (as of this draft; a historical fact)
planned X01 contribution        = +3
expected resulting total        = (the shared cumulative total for the Databento
                                   panel AT EXECUTION) + 3
```

> **The former text "`14 → 17`" is deleted.** It asserted a future cumulative
> state as though cross-project history could not move between seal and
> execution. The final value is **determined immediately before execution**, read
> from the authoritative shared record at that moment, and recorded then.
> **This forces DSR recomputation for every already-computed DSR on that panel**
> (carry PREREG §10) against the total **actually** obtaining.

**What does and does not create a `VARIANT_ATTEMPT`:**

| Object | Creates a new attempt? |
|---|---|
| the primary arm; S1; S2 | **YES — three attempts, three trials** |
| **bootstrap replicates** of any arm | **NO** — resampling one already-recorded series |
| **crisis-window slices** (§7.1) of an already-constructed series | **NO** — a subsetting diagnostic |
| tracking error, `max|D_t|`, correlation, sign agreement, turnover | **NO** — diagnostics on an existing series |
| high PnL correlation **between** the three arms | **NO deletion, ever.** Correlation triggers `HIGH_REDUNDANCY_REVIEW`, never a merge or a removed row (`TRIAL_LEDGER.md` §1.1 rule 1) |
| **any additional evaluated cost configuration, sizing configuration, basket configuration or roll construction** | **YES — and it must be prospectively classified BEFORE outcome access.** Adding one after seeing an outcome is a new selection opportunity, not a robustness check |

**Only Option B is evaluated.** Aaron's O-1 adoption means the Option-A ag map
is **never constructed**: there is **no Option-A return series, no Option-A
attempt row and no Option-A trial**, and it may **not** be computed later "as a
sensitivity, just to compare". Doing so would create a post-result choice between
two maps — exactly the selection surface the ex-ante adoption exists to remove.
The same holds for O-6 Option 2.

**Correlation cannot delete attempts.** This is restated here because the
three arms are expected to be **highly dependent** — they share a sample, a
signal and a window — and that is exactly the circumstance in which a later
session might be tempted to consolidate them. **No numeric correlation is
imported here**: MAP_v2's "≥ 0.9" was an ETF-vs-futures *price* expectation, not
an arm-vs-arm one.

**ETF-panel accounting — the previous claim is CORRECTED.** §3.6 shows that no
standalone commodity-sleeve monthly stream is published, so the ETF leg `E`
**must be constructed**, and the former assertion that it is "a re-read of the
published sleeve stream, constructing no new ETF series" is **false**.
`D-ETF-COUNT` is therefore **not** untouched by X01. This draft does **not**
resolve it; it records that **`E`'s trial classification against the ETF panel
must be settled before the first governed X01 construction**, alongside the
shared-home gate below.

---

## §11 Review chain (Program v2 §1) — none of it performed by this session

1. **A2** — a **fresh GPT-6 Astra session** challenges reachability, the SESOI /
   boundary and its metric scale, hidden degrees of freedom (O-1 was one, now
   adopted), the
   sample assumptions, the inference design and kill-branch reachability.
   **STATUS: performed. `X01_A2_VERDICT = FAIL`, `X01_SEALABLE_NOW = NO`,
   accepted; the bounded design repair is recorded at §13 and §13.1.** The A2
   session's own closure of that repair — and re-run after **any** further
   amendment, including Aaron's O-1/O-2/O-6 adoptions — is still outstanding
   (`X01_A2_FINAL_CLOSURE = NOT_YET`).
2. **B — Seal** — Aaron adjudicates and authorises. **Approval is a decision, not
   evidence.**
3. **C–F** — Opus builds and runs; truncation-invariance tests for every new
   causal primitive; reconciliation identities for every new PnL path.
4. **G — Fable adversarial audit** — the QROS trigger **applies**: futures roll /
   expiry logic and cost / price-unit logic. Read-only; repairs need separate
   authorisation.
5. **I — Stage I** — a **new fresh Astra session, never the A2 session**, reading
   the Lineage/Amendments first, and disclosing that the §0A/§0B framework this
   contract rests on was Astra-contributed (certification of those elements
   belongs to a non-producing session **not of Astra's family**).
6. **J–K** — Aaron adjudicates.

**Downstream adjudication.** A valid negative wrapper result does **not**
automatically suspend X06, X12, X32 or X43; each dependency is adjudicated by
Aaron on its own claim. **Only mechanical failure or infeasibility suspends
automatically.**

---

## §12 Preconditions before this may be sealed

| # | Precondition | Status |
|---|---|---|
| 1 | **X02a mechanical truth PASSES** | **PENDING INDEPENDENT VERIFICATION.** Builder-side complete after the Fable audit **and** the subsequent Astra cash-ledger repair (the one-contract cash ledger is now built from the frozen Sec 5 dollar primitive; a synthetic CL $25.00 regression with a literal oracle rejects the superseded $23.863636; independence is mutation-verified): panel sanity PASS; **gross** and **net** ledger reconciliations reported separately (the gross one is an algebraic tautology and is not evidence of accounting validity); end-to-end cost path repaired and verified by sabotage; MAP_v2 sign-agreement diagnostic computed; truncation invariance and roll monotonicity PASS. **Not MET** — the earlier "MET" was an overclaim, and the producing session cannot certify its own repair. **Update:** the production cash path was subsequently repaired (`tsmom_chain_net_returns`) and independently accepted by a same-session Astra delta verification; the X01 construction route is now pinned to it in **§3.4**. That pinning is itself new, unverified text, so this precondition **remains PENDING**. |
| 2 | X03 structural roll diagnostics complete; roll rule declared a DoF or recorded immaterial within a declared margin | **PENDING INDEPENDENT VERIFICATION.** Builder-side complete on the **authoritative** carry `fixed_calendar_front_series` comparator: mean disagreement 48.4%, all 18 roots > 10%. **`ROLL_RULE_DOF = REQUIRED`** as a governance declaration and **`ROLL_RULE_ECONOMIC_MATERIALITY = UNRESOLVED`** — no margin was sealed and no performance quantity computed. The roll rule must be named as a declared DoF in §3 before sealing, and **the A2 challenge must fix which calendar comparator S2 uses**. |
| 3 | O-1 … O-6 resolved and written into the sealed text | **CLOSED.** **O-1, O-2 and O-6 RESOLVED_BY_OWNER on 2026-09-08** and written into the active text (§3, §3.6, §5, §15). Previously: **O-3 RESOLVED** (§6.1) · **O-4 REMOVED as invalid** (§8.0) · **O-5 fixed for X01, D9 left open and NOT a blocker** (§9.1) · **O-6 technical half FROZEN** (§3.6). **Nothing remains open.** |
| 4 | `SHARED_DATABENTO_HOME_GATE` | **`PRE_EXECUTION` — no longer a seal blocker.** The physical location and curator must be resolved **before the first governed X01 construction / append**, not before the seal. Storage location is an operational fact and **cannot change the statistical interpretation** of the result; treating it as a seal blocker conflated the two. **The ledger is NOT created here.** |
| 4b | `E`'s ETF-panel trial classification (`D-ETF-COUNT`) | **PRE_EXECUTION**, newly identified — see §10.1. Not resolved by this draft |
| 5 | Fresh GPT-6 Astra A2 challenge completed and adjudicated | **NOT STARTED** |
| 6 | Aaron's explicit seal | **NOT GIVEN** |

**Not preconditions:** D3 (NAV — X05's dependency, not X01's), D1/D2 (deferred
acquisitions), `D-ETF-COUNT`.

---

## §13 Lineage and amendments

| Date | Entry |
|---|---|
| 2026-09-08 | **Final four A2 design defects repaired (`X01_A2_DELTA_VERDICT = FAIL`, 4 blockers, 0 owner decisions outstanding) + one non-blocking calendar correction.** **(1) SIGNAL — an executable contradiction with frozen V2, corrected.** §3 described the composite as the *mean of the {1,3,6,12}-month total returns*; accepted V2 (MAP_v2 §Baseline, `src/signals.py::signal_method_b`) specifies the **mean of the SIGNS**. New **§3.7** reproduces it from source — `s_t = [sign(R_1m)+sign(R_3m)+sign(R_6m)+sign(R_12m)]/4`, zero convention `np.sign(0)=0` **read from the code and not invented**, all four horizons required, `combine="mean"` not `"vote"` — and names the three rejected expressions. **§3.7.1** adds a binding synthetic regression: on `(+0.10,+0.10,+0.10,−0.01)` the frozen implementation returns **+0.5**, versus 0.0725 for mean-of-returns and +1.0 for sign-of-mean. **(2) PORTFOLIO TRADE COST — quantity semantics corrected.** The `Δ|position| × C` rebalance expression is **deleted**: it returns **0** for a `+1 → −1` reversal and **0** across a roll. New **§3.8** charges `Σ_j |q_j,t − q_j,t−1| × C_j` per **contract identity**, with the sizing→quantity map taken from the already-authoritative convention (`q = w·K/(mult·P)`, continuous research quantities, **not integer live contracts**, cost rate invariant to `K`). **The accepted X02 primitive `cost_per_side_usd = tick_value + $2.50` is NOT changed.** **§3.8.1** pins regressions A–E, including the reversal at **2 sides / $25.00** and the roll at two identities. **(3) S1 — exact equation and timing.** The prior prose formed `r = P_new/P_old` and multiplied, which at 100→110 yields an adjusted roll level of **121** — a phantom jump at every roll. Corrected to `k_new = k_old × P_old,τ / P_new,τ` with `P_adj,t = k_new × P_new,t` for `t ≥ τ`; `τ` is the A1 held-front change (the same date the cash legs are charged), both settlements at `τ`, the new factor applying **at** `τ`, history never restated, successive factors compounding, and an explicit rule when the two contracts share no settlement. Regression pins **100 → 100 → 110**. **S1 still changes only the signal input; PnL remains `tsmom_chain_net_returns`.** **(4) SECONDARY INFERENCE — decided.** BH-FDR is no longer an undecided default: `F-X01` holds **one** confirmatory test, so **`BH_FDR_REQUIRED = NO`**, and Program v2 §0 rule 5's requirement to *state* a treatment is satisfied by that statement. New **§8.3**: `SECONDARY_INFERENCE_ROLE = DESCRIPTIVE_SENSITIVITY`, `S1_S2_PROMOTION_POWER = NONE`, `SECONDARY_MATERIALITY_GATE = NONE`, with six prohibitions. The undefined *material divergence* consequence is **deleted**, not thresholded: the signal-input construction is declared a degree of freedom **unconditionally** (`SIGNAL_INPUT_CONSTRUCTION_DOF = REQUIRED`), mirroring `ROLL_RULE_DOF = REQUIRED`, which discharges MAP_v2 X03's conditional consequence without inventing a threshold. **(5) CALENDAR.** February-2020 month-end corrected **2020-02-28 → 2020-02-29**; the canonical Feb–Apr 2020 COVID window and all crisis semantics are otherwise unchanged. **Untouched:** O-1/O-2/O-6; the primary estimand; the sample; the O-3 bootstrap and its disclaimers; V2; X02/X03. **No outcome accessed, no performance computed; the draft remains UNSEALED and UNRUN.** |
| 2026-09-08 | **AARON OWNER DECISIONS O-1 / O-2 / O-6 ADOPTED — incorporated into the active contract.** All three taken **prospectively, before any X01 paired return series, `Sharpe(F)`, `Sharpe(E)`, `ΔS`, bootstrap result or crisis statistic had been computed or opened.** **`O1_OWNER_DECISION = ADOPT_OPTION_B`** — ag proxy `ZC ZS ZW LE HE GF`, equal weight 1/6 per root, monthly month-end rebalance, the drafted deterministic within-leg missing-contract treatment, roots' gross chained series equal-weighted into ONE ag proxy index carrying ONE signal; classified **`FIXED_PROXY_WITH_COMPOSITION_MISMATCH`**, **not** `EXPOSURE_REPLICATION`; rationale is published index constituency ∩ permitted-panel availability, avoiding the ZM/ZL crush quasi-constituents and the KE early-availability problem, with the absent ICE sugar/cocoa/coffee legs explicitly disclosed. **Option A is not an evaluated X01 alternative and must not be computed as a sensitivity to compare results.** **`O2_OWNER_DECISION = B_0.15`** — `B = 0.15` annualised-Sharpe units, boundary `−0.15`, an **owner utility / economic tolerance**, explicitly **not** selected from observed X01 performance, anticipated pass probability, the prospective precision table, observed paired correlation, bootstrap results or historical candidate optimisation; **no fallback `B`, not alterable after outcomes, no alternative `B` reportable after execution**. **`O6_OWNER_DECISION = ADOPT_OPTION_1_SYMMETRIC_ZERO_CARRY`** — no cash/collateral yield, no margin financing credit or charge, no borrow/short-financing adjustment on either leg; ETF expense ratio embedded exactly once via the adjusted-close stream and never double-deducted; ETF trading cost 2.0 bps per unit turnover; futures trading/roll costs from the independently accepted X02 cash-first production accounting; unit-capital common normalisation; NET primary, gross diagnostic. Recorded as a **symmetric research convention for the wrapper-transfer test, NOT a claim that it reproduces full live-deployment economics** — NAV-specific and richer financing/deployment feasibility remain outside X01. **Option 2 may not be introduced after observing X01 nor reported as an alternative success route.** **Preserved unchanged:** the O-3 repair in full (paired stationary bootstrap, `L = 12` as a prospective design convention with no theorem about dependence ending at 12 months, no CI-width monotonicity claim, the Jobson–Korkie/Memmel table diagnostic-only with its five disclaimers); `O-4 = CLOSED / INVALID AS AN OPEN CHOICE`; the T1 evidence ceiling; O-5/D9 unresolved outside the X01 seal. `POST_HOC_ESCAPE_ROUTES_REMAINING = NONE`. **No performance was computed, no target outcome accessed, and the draft remains UNSEALED and UNRUN — an owner design decision is not authorization to execute.** |
| 2026-09-08 | **O-3 statistical wording closure (bounded).** Two claims in the A2 repair were too strong and are corrected; **no O-3 mechanic changed** (stationary bootstrap, L = 12 months, paired monthly resampling, 10,000 replicates, 95 % percentile CI, master seed 7, degenerate handling and multiplicity all stand). **(i)** The block-length justification no longer states or implies that a 12-month formation window proves dependence extends *no further than* 12 months. `L = 12` is now stated as a **prospectively chosen, design-based dependence horizon anchored to the longest signal-formation window, sealed as an inference convention** — explicitly **not** a theorem or empirical claim; a new row records that real dependence can outlast the formation window through persistent positions, volatility scaling, common market dependence and regime persistence. **(ii)** The claim that longer blocks necessarily/monotonically widen the interval is **deleted**, and presumed CI monotonicity is no longer used as evidence that `L = 12` cannot favour the claim; unsteerability now rests on the value being fixed pre-outcome from the signal specification alone, with no alternative computed. **(iii)** The Jobson–Korkie/Memmel calculation's role is pinned with five explicit disclaimers: a pre-outcome design approximation on declared scenario assumptions; **not** an estimate of the actual paired-stream correlation; **not** proof of stationary-bootstrap coverage; **not** a bound on the sealed interval; **not** an input to `B`; and **not** a substitute for the sealed inference — §6.1 alone determines the outcome. The same over-strong qualifier was corrected where §15 O-2 quotes the table; **no O-1/O-2/O-6 option, candidate value, meaning or recommendation was changed.** No target-data-dependent block selection was added and no bootstrap sensitivity family was created. **No outcome accessed; draft remains UNSEALED and UNRUN.** |
| 2026-09-08 | **Stage A2 repair — `X01_A2_VERDICT = FAIL`, `X01_SEALABLE_NOW = NO`; bounded pre-outcome design repair.** **[A2-1] Primary estimand** rewritten as the scalar **`ΔS = Sharpe(F) − Sharpe(E)`**, separated from the paired observations `(F_t, E_t)` and from `D_t = F_t − E_t`; Sharpe, annualisation, raw-return, ddof, degenerate and minimum-observation conventions frozen; the four substitutions (`mean(F−E)`, `Sharpe(F−E)`, difference-of-significance, observed-power) explicitly forbidden (§4). **[A2-2] Decision rule** endpoints frozen strict/strict/inclusive so the three states partition the line and `L = −B` or `U = −B` classify as `UNRESOLVED` (§5). **[A2-3] O-3 RESOLVED**: paired stationary bootstrap, joint resampling, `ΔS` recomputed per replicate, **L = 12 months** mechanism-justified, 10,000 reps, 95 % percentile CI, `SeedSequence(7).spawn(3)` in fixed arm order, invalid replicates discarded-and-counted with a 9,500 floor (§6.1); the `expected correlation ≥ 0.9` precision shortcut **deleted** and replaced by a declared formula over a declared `ρ`-grid (§6.2). **[A2-4] O-4 REMOVED as an invalid open item**; PRIMARY / SECONDARY / DIAGNOSTIC hierarchy made explicit and non-re-orderable (§8.0). **[A2-5] O-5**: X01 capped at `AT_MOST_SUPPORTED_IN_T1_FOR_PAIRED_WRAPPER_PERFORMANCE`, D9 left open and **de-blockered**; no weakest-tier inheritance (§9.1). **[A2-6] Sample repaired**: the former 2010-07-31 start ignored the 12-month warm-up; DATA AVAILABILITY START / FIRST SIGNAL-ELIGIBLE MONTH / FIRST PAIRED EVALUATION MONTH now distinguished, giving **2011-07-31 → 2026-05-31, N = 179**, with deterministic missing/partial rules and no bridge or shortened composite (§3.5). **[A2-7] Both sleeve streams frozen** element-for-element, including the ag-basket signal surface (§3.6). **[A2-8] S1** fully specified as a signal-input-only construction sensitivity with a causal forward ratio adjustment; **S2** bound to `robustness.py::fixed_calendar_front_series` with its accepted mechanics (§8.1–8.2). **[A2-9] Crisis windows** fixed to the pre-existing canonical `config.py::REGIMES["COVID 2020"]` = 2020-02-01…2020-04-30 and CY2022 (§7.1). **[A2-10] Trial accounting** rewritten: `+3` conditional, `14 → 17` deleted, total computed at execution; shared-home moved to `SHARED_DATABENTO_HOME_GATE = PRE_EXECUTION`; **`D-ETF-COUNT` consequence newly identified and NOT resolved** (§10.1). **Reviewer contribution classification: `material_design_contributor`** — see §13.1. **No outcome was accessed, no performance computed, no threshold chosen by this session; O-1, O-2 and O-6's owner half remain OPEN; the draft remains UNSEALED and UNRUN.** |
| 2026-09-08 | **X01 production-route repair (documentation/governance only).** Astra found `LEGACY_CARRY_CONVENTION_REACHABLE_BY_X01 = YES`: the §3 cost row and §3.2 still named `cost_per_side_pct` / `chain_returns` as the construction path. New **§3.4** makes the cash-first route binding and names the verified entry point `run_x02a_v3.py::tsmom_chain_net_returns`; the §3 cost row and §3.2's divisor requirement are restated against it; the legacy callables are demoted to historical/reconciliation reference and are **not** an authorized X01 production path. `commodity-carry-research` **not modified**; the `LEGACY != AUTHORITATIVE` finding preserved. **No estimand, threshold, outcome state or open item resolved; O-1…O-6 remain open; precondition 1 remains PENDING_INDEPENDENT_VERIFICATION; the draft remains unsealed and unrun.** |
| 2026-09-08 | **Astra cash-ledger repair.** Precondition 1's supporting evidence updated to the repaired primitive cash ledger; the precondition itself **stays PENDING_INDEPENDENT_VERIFICATION** and is not marked MET. No estimand, threshold or open item resolved; O-1…O-6 remain open; draft unsealed. |
| 2026-09-08 | **Fable-audit repair.** §3.3 corrected to the vendor `instrument_class == "F"` filter and persistent contract identity (the string-heuristic description was wrong); §3 cost line corrected to require division **before** any `chain_returns`/cost call; roll-rule row now states the **effective t−2 causal OI lag**; preconditions 1–2 changed from MET to **PENDING INDEPENDENT VERIFICATION** with `ROLL_RULE_ECONOMIC_MATERIALITY = UNRESOLVED`. **No estimand, threshold or open item was resolved; O-1…O-6 remain open; the draft remains unsealed.** |
| 2026-09-08 | Preconditions 1 and 2 updated to **MET** after the contract-identity repair; roll rule recorded as a required preregistered DoF. **No estimand, threshold, outcome state or open item was resolved** — O-1…O-6 remain open for A2/Aaron. |
| 2026-09-08 | Precondition 1 and 2 statuses updated from "NOT COMPLETE" to **BLOCKED** with the located cause, after the Wave-1 X02a/X03 attempt. No estimand, threshold, outcome state or open item changed. |
| 2026-09-07 | **Draft created**, Wave 1, by the Opus research builder. Design lineage `POST_EXPOSURE_DESIGN_ON_ETF_PANEL` + `CARRY_STUDY_INFORMED`. Adopted Astra-contributed V2 elements: the evidence-context model (§0A), output-based exposure classification (§0B), the three-state outcome form and claim-specific crisis scoping — **adopted by the designer, not authored by Astra in this contract**, and their certification belongs to a non-producing session not of Astra's family. Incorporates Wave-1 verified facts: the 2026-06-30 futures boundary, the 79% spread composition, the eight cents-quoted roots, and the tail-vs-convexity finding from `EDGE_DIAGNOSTICS.md`. |

### §13.1 A2 provenance and its Stage I consequence

| Field | Value |
|---|---|
| Reviewer seat | fresh GPT-6 Astra, X01 Stage A2 pre-seal challenge |
| Verdict | **`X01_A2_VERDICT = FAIL`**, `X01_SEALABLE_NOW = NO` |
| Timing relative to outcomes | **before any X01 target outcome existed.** No X01 performance quantity was accessed by the reviewer or by this repair session |
| Classification | **`material_design_contributor`** — not `reviewer_only`. The scalar-estimand correction, the removal of O-4, the `PRE_EXECUTION` gating of the shared home and the escape-route taxonomy are **design elements supplied and adopted**, not merely objections raised |
| **Attribution caveat, recorded rather than resolved** | the findings reached this session **through Aaron's relay**, which also carried Aaron's own instructions. **Which adopted elements originated with the reviewer and which with the owner cannot be separated from the relay.** The classification above is therefore the **conservative** reading |
| **Stage I obligation (operating mode §3.2/§3.5)** | the adopted elements **must not rest on same-family (GPT-6 Astra) review as their sole independent certification.** A fresh Stage I Astra session retains context independence but **not** model-family diversity on these specific elements; certifying them requires Opus or Fable, or an explicit non-independent marking |
| Persisted record | `research/extensions/review_history/X01_STAGE_A2_DESIGN_REVIEW_2026-09-08.md` |
| **Gap** | the reviewer's **original artifact is not persisted on disk** — only this relayed record is. Recorded as a gap, not papered over. Reviewer/model diversity is **review diversity, never sample independence and never statistical replication** |

---

## §14 Post-hoc escape-route register

Every consequential freedom, and its disposition. **`FROZEN`** = fixed in this
text · **`RULE`** = governed by a deterministic outcome-independent rule ·
**`OWNER`** = a choice that was Aaron's; **all three are now ADOPTED**, so no
route remains in that state.

| # | Escape route | Disposition | Where |
|---|---|---|---|
| **1** | **Basket membership / weights / missing-root treatment** | **FROZEN — ADOPTED.** `ZC ZS ZW LE HE GF`, equal 1/6 (`O1_OWNER_DECISION = ADOPT_OPTION_B`, 2026-09-08, pre-outcome). Option A is **not evaluated and not computable as a sensitivity**. **RULE** for missing roots: renormalise within one ETF's map; a late-starting root is excluded from the sealed map entirely, never spliced mid-window | §15 O-1 · §3.5 |
| **2** | **Scalar primary statistic / tracking co-primary** | **FROZEN.** `ΔS = Sharpe(F) − Sharpe(E)`; four substitutions forbidden; hierarchy explicit and non-re-orderable; O-4 removed | §4 · §8.0 |
| **3** | **`B` chosen after outcomes** | **FROZEN — ADOPTED.** `B = 0.15` (`O2_OWNER_DECISION = B_0.15`, 2026-09-08, pre-outcome). **No fallback `B`; `B` is not alterable after outcomes; no alternative `B` may be reported after execution as a competing pass/fail specification.** The §15 O-2 candidate table is historical decision material, not an executable set | §5 · §15 O-2 |
| **4** | **Bootstrap / CI / favourable-sensitivity selection** | **FROZEN.** One family, one block length, one CI construction, one level, one replication count, one seed protocol, one arm order. **No alternative interval is computed**, so none can be chosen | §6.1 |
| **5** | **Warm-up / initial positions / effective dates / normalisation** | **FROZEN + RULE.** Three dates distinguished and derived; no padding; no bridge; no shortened composite; deterministic missing/partial table; sleeve-standalone normalisation on both legs | §3.5 · §3.6 |
| **6** | **S1 / S2 / financing conventions** | **FROZEN throughout.** S1's one ambiguity resolved on a causality property; S2 bound to the named accepted function; financing/carry **ADOPTED** as `SYMMETRIC_ZERO_CARRY` (`O6_OWNER_DECISION`, 2026-09-08, pre-outcome). **Option 2 may not be introduced after observing X01 and may not be reported as an alternative success route** | §8.1 · §8.2 · §15 O-6 |
| **7** | **COVID window** | **FROZEN** to the pre-existing canonical `config.py` definition; no alternative window computed; no crisis gate. Month-ends **2020-02-29 · 2020-03-31 · 2020-04-30** | §7.1 |
| **8** | **Signal definition** — swapping `mean(signs)` for `mean(returns)` or `sign(mean(returns))` | **FROZEN.** The frozen V2 mean-of-signs composite is reproduced from `src/signals.py::signal_method_b`; the zero convention (`np.sign(0)=0`) is read from the code, not invented; all four horizons required; a binding synthetic regression pins **+0.5** on `(+0.10,+0.10,+0.10,−0.01)` and rejects **0.0725** and **+1.0** | §3.7 · §3.7.1 |
| **9** | **Trade-cost quantity semantics** — charging position-magnitude change instead of traded quantity | **FROZEN.** `Σ_j |q_j,t − q_j,t−1| × C_j` per **contract identity**; `|·|` so costs never rebate; roll = two identities, two sides; the sizing→quantity map uses the already-authoritative convention and the cost rate is invariant to `K`; binding regressions A–E pin the reversal at **2 sides** where the deleted formula gave **0** | §3.8 · §3.8.1 |
| **10** | **S1 adjustment direction / roll timing** | **FROZEN.** One exact equation `k_new = k_old × P_old,τ / P_new,τ`, `P_adj,t = k_new × P_new,t` for `t ≥ τ`; `τ` is the A1 held-front change, the same date the cash legs are charged; both settlements at `τ`; new factor applies **at** `τ`; history never restated; a binding regression pins **100 → 100 → 110** and rejects **121** | §8.1 |
| **11** | **Secondary inference / undefined materiality** | **FROZEN.** `SECONDARY_INFERENCE_ROLE = DESCRIPTIVE_SENSITIVITY` · `BH_FDR_REQUIRED = NO` · `S1_S2_PROMOTION_POWER = NONE` · `SECONDARY_MATERIALITY_GATE = NONE`. The undefined "material divergence" consequence is **deleted** and replaced by the unconditional `SIGNAL_INPUT_CONSTRUCTION_DOF = REQUIRED`; no threshold was invented to preserve it | §8.3 · §8.1 |

> **`POST_HOC_ESCAPE_ROUTES_REMAINING = NONE`.**

All **eleven** routes are **FROZEN** or governed by a deterministic
outcome-independent **RULE**. **No consequential outcome-sensitive choice remains
executable** — not the agricultural roots, weights or missing-root treatment; not
the primary statistic; not `B`; not the bootstrap method or its settings; not the
warm-up, first eligible month or normalisation; not the S1 construction; not the
S2 comparator; not the financing/carry convention; not the COVID window; not an
alternative O-1/O-2/O-6 option; not a tracking metric as co-primary; not a
secondary arm as a rescue for a failed primary; **not the signal definition; not
the trade-cost quantity semantics; not the S1 adjustment direction or its roll
timing; and not the secondary-inference or materiality treatment.**

**Historical lineage (§13) and the rejected alternatives retained at §15 remain
readable, but they are labelled REJECTED and are not active instructions.**

---

## §15 OWNER DECISIONS — **ADOPTED** (Aaron, 2026-09-08)

```
O1_OWNER_DECISION = ADOPT_OPTION_B
O2_OWNER_DECISION = B_0.15
O6_OWNER_DECISION = ADOPT_OPTION_1_SYMMETRIC_ZERO_CARRY
OWNER_DECISIONS_REMAINING = NONE
```

> **Timing, which is the whole point.** All three were taken **prospectively**,
> **before any X01 paired return series, `Sharpe(F)`, `Sharpe(E)`, `ΔS`,
> bootstrap result or crisis statistic had been computed or opened.** No X01
> target-performance outcome existed at the moment of decision, and none exists
> now.

**What follows is the decision record**: the material Aaron was given, and what
he adopted. The options this session prepared were built from structural and
economic facts only — **no correlation, Sharpe or return of either leg was
consulted** — and **this session chose none of them**. The rejected alternatives
are retained below **as provenance, labelled REJECTED**; they are **not** active
instructions and **not** executable alternatives.

### O-1 — Agricultural mapping (DBA leg) — **ADOPTED: Option B**

> **`O1_OWNER_DECISION = ADOPT_OPTION_B`.** The DBA leg maps to `ZC ZS ZW LE HE GF`,
> **equal weight 1/6 per root**, monthly rebalance on the preregistered month-end
> convention, the §3.5 deterministic within-leg missing-contract treatment, and
> the §3.6 aggregation (roots' **gross** chained series equal-weighted into **one**
> ag proxy index carrying **one** signal). Classified
> **`FIXED_PROXY_WITH_COMPOSITION_MISMATCH`**, **not** `EXPOSURE_REPLICATION`.
>
> **Aaron's stated reasons:** the mapping corresponds to the published
> agricultural-index constituency available in the permitted CME panel; it avoids
> including the soybean crush products ZM/ZL as additional quasi-constituents; it
> avoids the severe early-KE availability problem; the choice rests on pre-outcome
> instrument membership and availability, **not** on X01 returns, correlation,
> Sharpe or cost; and the absent ICE sugar/cocoa/coffee legs leave the composition
> mismatch explicitly disclosed.
>
> **Option A is NOT an evaluated X01 alternative.** It must not be computed as a
> sensitivity merely to compare results, and **no post-result choice between A and
> B may be created** (§10.1, §14 route 1).

**Both options were pre-existing, pre-outcome objects** from
`c1-drag-audit/DEVIATIONS.md` D5, fixed there before any per-symbol figure was
visible. Neither is invented here.

| | **Option A — REJECTED** | **Option B — ADOPTED** |
|---|---|---|
| **Roots** | `ZC ZS ZW ZM ZL KE LE HE GF` (**9**) | `ZC ZS ZW LE HE GF` (**6**) |
| **Weights** | equal, **1/9** of the DBA leg each | equal, **1/6** of the DBA leg each |
| **Weight basis** | equal weight over *every* agricultural root in the panel — "chosen to avoid selecting roots by their cost" | equal weight over the **DBIQ-Diversified-Agriculture constituents present in this CME panel** |
| **Rebalance timing** | monthly, at the same month-end as every other leg | identical |
| **Missing-contract handling** | §3.5: renormalise within the DBA leg over the remaining eligible roots, conserving the leg's total weight | identical |
| **Aggregation** | roots' gross chained return series equal-weighted into one ag-basket index; **one signal**, sized as one asset (§3.6) | identical |
| **What it claims to represent** | DBA's broad agricultural exposure via the widest available CME agricultural set | DBA's **published index constituency**, intersected with panel availability |
| **Classification** | **`FIXED_PROXY_WITH_COMPOSITION_MISMATCH`** | **`FIXED_PROXY_WITH_COMPOSITION_MISMATCH`** |
| **Provenance** | c1 D5 **primary** map | c1 D5 **pre-specified sensitivity arm 1** |

**Why neither is `EXPOSURE_REPLICATION`, and why that matters.** DBA's index
includes **sugar, cocoa and coffee**, which are **ICE** products and are **absent
from the GLBX panel entirely**. No basket buildable from this panel replicates
DBA's exposure. Both options are therefore proxies with a known composition
mismatch, and **the DBA leg's contribution to `ΔS` is not a pure wrapper
difference** — it mixes wrapper effect with basket mismatch. This limitation is
disclosed here and carries into the result's interpretation whichever option is
adopted.

**Verified structural facts, from the accepted panels (no returns consulted):**

| Root | First settlement | Coverage over 2011-07 … 2026-05 |
|---|---|---|
| ZC, ZS, ZW, ZM, ZL | 2010-06-06 | 99.27 % |
| LE, HE | 2010-06-06 | 99.03 % |
| GF | 2010-06-06 | 98.99 % |
| **KE** | **2013-12-15** | **82.85 %** |

**This session's recommendation was Option B; Aaron adopted it.** The reasoning it was based on:

**Reason (three structural points, no outcome used):**

1. **Availability.** Every Option-B root has data from the panel's first day.
   **Option A contains KE, which does not exist until 2013-12-15** — 42 of the
   179 evaluated months. Under §3.5's missing-root rule a root absent for the
   window's start is excluded from the sealed map anyway, so **Option A as
   written is not executable without either dropping KE or accepting three and a
   half years of renormalisation** in the leg under test.
2. **Constituency.** Option A adds **ZM and ZL** — soybean **meal** and **oil**,
   the crush products of ZS. They are not DBIQ constituents, and including them
   beside ZS puts **3 of 9 (33 %)** of the ag leg on the soy complex versus
   **1 of 6 (17 %)** under Option B. That is a composition choice, not a wrapper
   choice.
3. **No fitting.** Option B's membership is determined by *published index
   constituency ∩ panel availability*. No return, correlation, cost or Sharpe
   entered the rule.

**Honest counterweight:** Option A is the c1-drag-audit's **primary** map, and
adopting it unchanged maximises cross-project consistency — a real governance
virtue that points the other way, and it was put to Aaron alongside the
recommendation rather than suppressed. **`OWNER_ADOPTION_REQUIRED` = SATISFIED —
`ADOPT_OPTION_B`, 2026-09-08.**

### O-2 — The degradation tolerance `B` — **ADOPTED: `B = 0.15`**

> **`O2_OWNER_DECISION = B_0.15`.** **`B = 0.15` annualised-Sharpe units**;
> non-inferiority boundary **`−0.15`**; primary scalar estimand unchanged as
> `ΔS = Sharpe(F) − Sharpe(E)`; the §5 endpoint convention applies exactly as
> repaired.
>
> **Aaron's stated interpretation:** a reduction of **up to 0.15 annualised
> Sharpe** in the futures wrapper relative to the ETF wrapper is the **maximum
> economically tolerable degradation** for this historical wrapper-transfer claim.
> This is an **OWNER UTILITY / ECONOMIC TOLERANCE**.
>
> **It was explicitly NOT selected from** observed X01 performance · an
> anticipated probability of passing · the prospective precision table below ·
> an observed paired correlation · bootstrap results · historical candidate
> optimisation.
>
> **Three standing prohibitions.** `B` is **not** to be altered after target
> outcomes are visible. There is **no fallback `B`**. Alternative values of `B`
> are **not** to be reported after execution as competing pass/fail
> specifications.

**Meaning, exactly:**

> **`B` is the maximum tolerated reduction in ANNUALISED SHARPE RATIO of the
> futures wrapper relative to the ETF wrapper**, over the 179-month paired
> window. It is in the **same units and on the same scale** as `ΔS`. The
> non-inferiority boundary is `−B`.

> *"If `B` = 0.10, the futures wrapper may deliver up to 0.10 less annualised
> Sharpe than the ETF wrapper and still satisfy the non-inferiority tolerance."*

**The candidate material Aaron was given — HISTORICAL DECISION PROVENANCE, not
an executable set.** The table below is retained so the basis of the decision is
recoverable. **Only `B = 0.15` is active**; the other rows are superseded and
must never be run as alternative specifications. From §6.2's declared formula, the
**design-approximation** (iid, scenario-based — see §6.2's five disclaimers;
it is **not** a bound on the sealed interval) 95 % half-width `h` is
0.397 at ρ = 0.70, **0.229 at ρ = 0.90**, 0.162 at ρ = 0.95. Since
`PRESERVATION` needs `ΔS − h > −B` and `MATERIAL_DEGRADATION` needs
`ΔS + h < −B`, the point estimate must reach:

| `B` | plain meaning | ρ = 0.90: `PRESERVATION` needs `ΔS >` | ρ = 0.90: `MATERIAL_DEGRADATION` needs `ΔS <` | ρ = 0.95: preservation / degradation |
|---|---|---|---|---|
| **0.05** | futures may lose at most 0.05 Sharpe | **+0.179** | **−0.279** | +0.112 / −0.212 |
| **0.10** | at most 0.10 Sharpe | **+0.129** | **−0.329** | +0.062 / −0.262 |
| **0.15** | at most 0.15 Sharpe | **+0.079** | **−0.379** | +0.012 / −0.312 |
| **0.20** | at most 0.20 Sharpe | **+0.029** | **−0.429** | −0.038 / −0.362 |
| **0.30** | at most 0.30 Sharpe | **−0.071** | **−0.529** | −0.138 / −0.462 |

**Four consequences worth reading before choosing:**

1. **For `B ≤ 0.20` at ρ = 0.90, the futures leg must actually BEAT the ETF leg**
   to earn `PRESERVATION_SUPPORTED` — a tolerance that small is, at this
   precision, effectively a superiority test. Whether that is what "preservation"
   should mean is a genuine owner judgement.
2. **A large `B` erodes the kill branch.** At `B = 0.30`, ρ = 0.90,
   `MATERIAL_DEGRADATION_SUPPORTED` needs `ΔS < −0.529` — a very large
   degradation. **This is precisely the drag-audit failure mode**
   (`finding.tsmom-futures-transfer.drag-audit-stands-no-kill-reach`: a sealed
   kill branch sitting 19× above the measurable value). **`B` must not be set so
   large that the kill branch is unreachable.**
3. **`UNRESOLVED_INSUFFICIENT_PRECISION` is a likely outcome at any `B`**, and it
   is a legitimate result, not a failure of the design. The table above is a
   scenario approximation, **not a bound** — the sealed bootstrap interval may
   come out wider or narrower, and §6.1 alone determines the outcome.
4. **Precision is governed by ρ, which is unknown.** If the strategy streams
   correlate at 0.70 rather than 0.90, every threshold above widens by ~0.17.

**No value was recommended by this session, and none was implied.** The economic
content of `B` — how much Sharpe Aaron is willing to give up to gain the futures
wrapper's capacity, capital efficiency and absence of fund expense ratios,
against its roll and rebalance costs — is not a statistical question and this
session had no standing to answer it. **Aaron answered it:
`OWNER_DECISION_O2_B = 0.15`, 2026-09-08, pre-outcome.**

**What `B = 0.15` requires of the point estimate**, read off the row above under
the declared scenario grid (a design approximation, **not a bound** — §6.2): at
ρ = 0.90, `PRESERVATION_SUPPORTED` needs `ΔS > +0.079` and
`MATERIAL_DEGRADATION_SUPPORTED` needs `ΔS < −0.379`; at ρ = 0.95, `+0.012` and
`−0.312`. **Both branches are reachable**, which is the property
`lesson.rule-domain-analysis-before-freeze` requires and which the drag-audit
precedent shows must be checked before a boundary is frozen. The sealed §6.1
bootstrap interval, not this arithmetic, determines the outcome.

### O-6 — Capital, cost and financing comparability — **ADOPTED: Option 1**

> **`O6_OWNER_DECISION = ADOPT_OPTION_1_SYMMETRIC_ZERO_CARRY`.** For X01: **no
> cash/collateral yield credited to either leg · no futures margin financing
> credit or charge · no borrow/short-financing adjustment on either leg · ETF
> expense ratio embedded exactly once through the authoritative adjusted-close
> return stream and never double-deducted · ETF trading cost at the accepted
> baseline 2.0 bps per unit turnover · futures trading and roll costs from the
> independently accepted X02 cash-first production accounting · both legs on the
> preregistered unit-capital / common normalisation · NET primary, gross
> diagnostic.**
>
> **Aaron's stated scientific interpretation:** this is a **symmetric research
> convention for the X01 wrapper-transfer test**. It is **NOT** a claim that these
> assumptions reproduce full live-deployment economics. **NAV-specific and richer
> financing / deployment feasibility remain outside X01 and are not established by
> this decision.**
>
> **Option 2 must not be introduced after observing X01, and must not be reported
> as an alternative success route.**

**Already FROZEN as technical components (not owner preferences), in §3.6:**

| Component | Frozen treatment |
|---|---|
| ETF return reference | adjusted closes from the frozen panel, SHA-pinned |
| ETF expense ratio | **already embedded** in those prices — **deducted exactly once, never twice** |
| Futures transaction / roll costs | the accepted X02 cash-first primitive, `C = tick_value + $2.50` per side |
| Common capital denominator | both legs are **unit-capital, full-notional** return streams under identical per-asset vol targeting; neither leg is levered relative to the other |
| Gross vs net | **primary comparison is NET on both legs**; gross reported as a diagnostic |

**Genuinely material owner-policy choices, presented as one bounded bundle
because they interact:**

| | **Option 1 — "symmetric zero-carry" — ADOPTED** | **Option 2 — "full carry accounting" — REJECTED** |
|---|---|---|
| Cash / collateral yield | **none on either leg** | T-bill yield added to **both** legs (`data/DGS3MO.csv` exists) |
| Futures margin / collateral | return defined on **full notional**; no financing credit or charge | futures earn yield on unposted capital; a financing charge applies to notional |
| ETF trading cost | `2.0 bps` per unit turnover — the baseline's own convention | a higher, instrument-specific figure for the less liquid USO/UNG/DBA |
| Short financing / borrow | **none on either leg** (the published baseline charges none) | ETF short borrow charged; futures shorts unaffected |
| Data dependency added | **none** | a rate series and a borrow-cost assumption, each a new degree of freedom |

**This session's recommendation was Option 1; Aaron adopted it.** The reasoning it was based on:

**Reason:** it is the baseline's own convention, it is applied identically to both
legs, and every element of Option 2 introduces a new assumption whose value would
itself need justifying and challenging before seal. **It is also conservative
against the claim under test**: futures genuinely earn yield on unposted collateral
and pay no borrow to short, so waiving both **removes advantages the futures
wrapper really has**. Option 1 therefore **cannot manufacture a favourable X01
result** — and that, not convenience, is why it is recommended. Waiving the ETF
borrow cost pushes the other way, so the residual asymmetries are opposed rather
than aligned.

**`OWNER_ADOPTION_REQUIRED` = SATISFIED — `ADOPT_OPTION_1_SYMMETRIC_ZERO_CARRY`,
2026-09-08.** The most favourable convention was not silently taken, and the
adopted one is the conservative-against-the-claim option.

---

```
X01_PREREG_SEALED = NO · X01_FULL_PERFORMANCE_EXECUTED = NO
X01_A2_VERDICT = FAIL (accepted) · X01_A2_FINAL_CLOSURE = NOT_YET
O1 = RESOLVED_BY_OWNER · O2 = RESOLVED_BY_OWNER · O6 = RESOLVED_BY_OWNER
TECHNICAL_BLOCKERS_REMAINING = NONE
OWNER_DECISIONS_REMAINING   = NONE
POST_HOC_ESCAPE_ROUTES_REMAINING = NONE
TARGET_X01_OUTCOME_ACCESSED = NO

An owner design decision is NOT authorization to execute. This contract is
complete but UNSEALED, and nothing may be run until the A2 delta closure and
Aaron's explicit seal.

NEXT GATE = SAME GPT-6 ASTRA X01 A2 DELTA CLOSURE
```
