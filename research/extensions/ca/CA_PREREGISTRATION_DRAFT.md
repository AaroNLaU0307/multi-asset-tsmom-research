# C-A — PREREGISTRATION (**SEALED**)

```
CA_PREREG_SEALED       = YES
CA_PREREG_SEAL_DECISION = AARON OWNER DECISION, 2026-09-13 — SEAL C-A
S1_SEALED              = YES
S1_SEAL_TIMESTAMP      = 2026-09-13T17:42:06Z   (UTC, the actual seal operation)
OWNER_SEAL_AUTHORIZED_BY = Aaron
STATUS                 = SEALED. The scientific content below is frozen. OD-1 … OD-7 are
                         Owner decisions and no alternative threshold, floor, horizon,
                         interval, estimand or decision rule may be introduced after this
                         seal. Nothing below has been implemented and nothing has been run.
S1_SEAL_AUTHORIZED     = YES   (C-A S1 SEAL ONLY — see the explicit non-authorizations below)
C_A_IMPLEMENTED        = NO
C_D_IMPLEMENTED        = NO
S_G_CREATED            = NO
PIPELINE_GO_LIVE       = NOT YET
T4_SEAL_EXISTS         = YES
T4_CLOCK_STARTED       = NO    (a seal alone does not create a prospective record — §E)
N_scored               = 0
FIRST_ELIGIBLE_SCORED_PERIOD = NOT YET DETERMINED
TARGET_PERFORMANCE_COMPUTED = NO
TARGET_OUTCOME_REVEALED     = NO
TARGET_RUN_AUTHORIZED       = NO
SEAL_CHANGED_SCIENTIFIC_CONTENT = NO   (status metadata only; §A–§Z unamended)
RESEARCH_ID            = TSMOM-CA-001   (within programme TSMOM-EXT-001)
LANE                   = FULL           (confirmatory performance claim permitted; lane is not evidence_type)
OWNER                  = Aaron
DRAFTED_BY             = Claude Opus 5 (Main Agent), 2026-09-13
REVISION               = S1 bounded repair, 2026-09-14 — Owner decisions on the interval (SB-4),
                         the FM-1 rf convention (SB-1) and the FM-1 decision scale (SB-2) applied;
                         contract-consistency repairs CB-1 (first scored month), CB-2 (S_0 vs S_G),
                         CB-3 (S1 vs S2 gate ordering). SB-3 remains OPEN and blocks C_D_PASS only.
                         No scientific redesign; S0 not reopened.
OPEN_S1_SCIENTIFIC_BLOCKERS = NONE   (SB-1, SB-2, SB-4 closed by Owner decision 2026-09-14)
OPEN_PRE_SEAL_ITEMS         = NONE   (PC-1 raised and CLOSED 2026-09-14 from existing §J
                              authority — classified MECHANICAL_CORRECTION; no new tolerance created)
INSTRUMENT_REGISTRY         = research/extensions/ca/CA_INSTRUMENT_REGISTRY.json   (17 objects,
                              pinned; §K conformance SATISFIED, COMPLETE_FOR_SEAL)
SNAPSHOT_REGISTRY           = research/extensions/ca/CA_SNAPSHOT_REGISTRY.md       (S_0 pinned; S_G not created)
OWNER_DECISION_RECORD  = ../../../ops/OWNER_DECISION_RECORD_PHASE_B.md
WORKFLOW_AUTHORITY     = ../../../../QUANT_WORKFLOW_VNEXT.md
PRECONDITION_STUDY     = ../cd/CD_VERIFICATION_SPECIFICATION_DRAFT.md   (C-D)
```

**This contract is SEALED.** Aaron sealed it on **2026-09-13T17:42:06Z** under the
Owner authorization `SEAL C-A`. The scientific content is frozen from that instant:
§A–§Z are byte-identical to the accepted pre-seal bytes and the seal changed status
metadata only.

**What the seal did and did not create.** It created the **T4 seal** for this claim
family — the reference instant against which every later month's eligibility is
judged. It did **not** start the prospective scoring stream. `PROSPECTIVE_START =
max(SEAL_TIMESTAMP, PIPELINE_GO_LIVE)` (§E), and `PIPELINE_GO_LIVE` does not yet
exist because `S_G` has not been created and the pipeline is not built. Therefore
`N_scored = 0`, `FIRST_ELIGIBLE_SCORED_PERIOD` is **NOT YET DETERMINED**, and no
month is eligible. **No accrued pre-go-live month may ever be retroactively
scored**, and accrued history is never relabelled prospective
(`LOCKBOX_PROCEDURE.md` §1).

**What this seal explicitly did NOT authorize.** S2 build · the C-A implementation ·
the C-D implementation · creating `S_G` · pipeline go-live · running the prospective
pipeline · generating any prospective position · computing any target performance ·
revealing any target outcome · resolving `SB-3` · reopening C-B · starting Phase C.
Each remains a separate Owner gate, and this seal consumes none of them.

**Design provenance.** The scientific architecture is Fable's
(`TSMOM-CONF-FABLE-PHASE-B-CA-01` and its bounded repair `…-CA-02`), challenged by
Astra, and decided by Aaron in the Owner Decision Record. Where CA-02 superseded
CA-01, CA-02 governs. Where Aaron's Owner decisions differ from either
recommendation, **Aaron governs** — notably the materiality scale (§D) and the
state vocabulary (§O).

---

## §A Hypothesis and claim

**Economic hypothesis (unchanged, inherited).** Trend continuation in a
diversified multi-asset book, arising from risk-premium and behavioural
under-reaction and slow information diffusion, produces a positive risk-adjusted
net return; part of the return comes from the ability to go short in crises, which
a long-only book cannot do.

**The claim C-A tests:**

> Over the scored prospective window, the canonical strategy's expected **raw net
> monthly return, expressed as an annualised Sharpe ratio with `rf = 0` and the
> canonical 2 bps cost**, is positive and economically material — at least
> **+0.30** — where the floor was fixed before any scored month existed.

Three things this wording deliberately does and does not say.

- It is a claim about a **population parameter over the forward regime**, not about
  reproducing the historical point estimate of 0.75. The historical estimate is one
  draw and is not part of the claim.
- It is a claim about the strategy **as implemented and costed at 2 bps**, on the
  **ETF book**, in the **forward era**. It is not a claim about futures, about any
  other universe, about the mechanism (timing versus static premium — a separate
  lineage), or about deployability at any other cost.
- The claim is one-directional in substance; the decision rule (§O) is nevertheless
  written so that negative outcomes are as sharply defined as the positive one.

**What C-A cannot test even in principle.** Whether the 2008–2026 result was luck
(the forward record *supplements* that question, it does not re-adjudicate it);
whether the rule beats a passive risk-premium book at matched risk (a separate
lineage); whether the edge is universe-specific (C-C, parked); whether the
historical series is a code or vendor artefact (that is C-D's job, §S).

**Inherited accounting limitation, disclosed and not corrected.** Under the
canonical `rf = 0` convention a book that is on average net long earns the bill
rate inside its asset total returns without being charged for it. By the identity
`r_raw = x + net_held · rf`, the raw Sharpe contains a cash component of roughly
`net · rf / σ` — historically ≈ 0 at zero bill rates, ≈ 0.18 at 2 %, ≈ 0.36 at 4 %
for an average net of +0.93 and 10.3 % annualised vol (planning constants already
on record; not measurements of any forward series). **A raw pass in a positive-rate
decade does not by itself establish an edge beyond cash.** The primary is
nevertheless the primary, because it is the claim on record
(`finding.tsmom-core.oos-sharpe-confirmed`, `strat.tsmom.multi-asset-core`,
`STUDY_SUMMARY.md` §4). §P is the complement that addresses the cash component, and
§O.5 fixes the joint reading in advance.

---

## §B Exact canonical strategy identity — IMMUTABLE

The tested object is the canonical rule **byte-identical to the sealed `src/`**,
applied to the canonical 17-ETF book. No parameter is changed by this contract.

**Universe — exactly 17 objects, five sleeves.**

| Sleeve | Tickers |
|---|---|
| Equity | SPY, EEM, EWJ, XLE, XLU |
| Fixed income | TLT, SHY, LQD, HYG |
| Commodity | USO, UNG, GLD, DBA |
| FX | UUP, FXY |
| Real estate | VNQ, RWX |

**Rule.**

| Element | Value | Source of truth |
|---|---|---|
| Decision frequency | month-end | `config.SIGNAL_RESAMPLE = "ME"` |
| Monthly price | last available daily adjusted close **within the calendar month**, labelled at the calendar month-end | `src/signals.py::to_monthly` |
| Momentum horizons | trailing 1, 3, 6, 12-month simple returns, `M_t / M_{t−N} − 1` | `config.MOMENTUM_LOOKBACKS_MONTHS` |
| Composite | **sign of each horizon first**, then the **mean of the four signs**; **all four horizons required** | `src/signals.py::signal_method_b`, `config.MOMENTUM_MIN_PERIODS = 4`, `SIGNAL_COMBINE = "mean"` |
| Asset volatility | rolling 60-day std of simple daily returns, `ddof = 1`, `min_periods = 60`, annualised ×√252, sampled at month-end | `src/sizing.py::rolling_volatility` |
| Asset weight | `clip(signal · 0.10 / vol, ±2)`; `vol ≤ 0` or NaN → NaN; `signal == 0` → `0.0` | `src/sizing.py::target_weights` |
| Aggregation | equal weight over assets **with a non-NaN weight** that month: `base_i = w_i / n_available` | `src/portfolio.py::equal_weight_aggregate` |
| Portfolio volatility | 60-day rolling std of the **unlevered base book's** daily returns, held weights `reindex(ffill).shift(1)`, `ddof = 1`, ×√252, sampled at month-end | `src/portfolio.py` |
| Leverage | `L = min(0.10 / port_vol, 3 / gross_base)`, NaN in either input propagates | `src/portfolio.py::leverage` |
| Position timing | `positions = port_weights.shift(1)` — the position held in month `t` is the weight decided at month-end `t−1` | `src/portfolio.py`, `src/performance.py` |
| Gross monthly return | `Σ_i position_{i,t} · R_{i,t}`, `R` = month-end-to-month-end simple return on the adjusted close | `src/performance.py::portfolio_returns` |
| Turnover | `Σ_i |position_{i,t} − position_{i,t−1}|` (one-way) | `src/performance.py::portfolio_returns` |
| Cost | `turnover × 2.0 / 1e4` | `config.TRANSACTION_COST_BPS = 2.0` |
| Net monthly return | `gross − cost` | `src/performance.py::portfolio_returns` |
| Sharpe | `mean / std(ddof = 1) × √12`, `rf = 0` | `src/performance.py::sharpe_ratio`, `config.RISK_FREE_ANNUAL = 0.0` |

**Object-identity rule.** The canonical strategy **is what the sealed `src/` does**.
Where a convention is not derivable from prose, the code governs and the C-D
specification (§S) must write it down explicitly. Two consequences are declared
here so no future session treats them as discoveries:

1. An asset with a **flat composite (`signal == 0`)** receives weight `0.0`, which
   is **non-NaN**, so it **counts in `n_available`** and dilutes the book. An asset
   with **missing volatility** receives weight NaN and is **excluded** from
   `n_available`. Where a flat signal and missing volatility coincide, the code's
   `where(signal != 0, 0.0)` override wins and the asset is **in the book at zero**.
   This is the canonical behaviour and it is preserved, not repaired.
2. `pct_change()` is called at three places (`src/sizing.py::daily_returns`,
   `src/portfolio.py::base_portfolio_daily_returns`,
   `src/performance.py::monthly_asset_returns`) **without an explicit
   `fill_method`**. Under the seal environment (pandas 2.3.3) the default is
   `fill_method='pad'`, which across a missing observation yields a `0.0` return
   followed by a clean return, rather than two NaNs. This default is **deprecated
   and changes in pandas 3.0** — verified mechanically on synthetic data in this
   session. The forward engine must therefore call `pct_change` with the fill
   behaviour **written explicitly** to reproduce the sealed behaviour, and the seal
   must pin the runtime (§I.4). This is a specification-tightening that preserves
   behaviour exactly; it is **not** a rule change.

**Frozen historical panel** (for C-D and for the pre-boundary state input):
`data/close_prices_raw.csv`, SHA-256
`3d2a7a56dbd92d4ff8138cfd894c87f5ac5ac088a11165db870673e0c05c3c31`, 1993-01-29 →
**2026-06-12** (`LOCKBOX_PROCEDURE.md` §2.1).

---

## §C Primary estimand

```
PRIMARY_ESTIMAND   =  S_raw  =  mean(r_net) / std(r_net, ddof = 1) · √12
r_net_t            =  Σ_i position_{i,t} · R_{i,t}  −  (2 / 1e4) · Σ_i |position_{i,t} − position_{i,t−1}|
position_{i,t}     =  canonical portfolio weight decided at month-end t−1 (weights.shift(1))
R_{i,t}            =  month-end-to-month-end simple return on the adjusted close (distributions embedded)
rf                 =  0, exactly the historical canonical computation; no financing, no cash credit
WINDOW             =  the scored forward months only (§E, §G)
NUMBER_OF_PRIMARY_CONFIRMATORY_ESTIMANDS = 1
```

There is **exactly one** primary. There are no co-primaries, no fallback primary,
and no rule by which any other statistic can become the primary.

---

## §D Economic thresholds — Owner decision OD-1

```
POSITIVE_MATERIALITY_FLOOR    (+E)  = +0.30
ADVERSE_MATERIALITY_THRESHOLD (-F)  = -0.20
BOUNDARY_RULE                       = STRICT CROSSING, every inferential decision
```

**Deliberately asymmetric.** `+0.30` is the level at which the canonical raw-return
thesis is judged to have **persisted in an economically meaningful way**; `−0.20`
is the level at which forward performance is judged **economically meaningfully
adverse — a reversal**, not merely a failure to add value. They were not chosen to
maximise pass probability and are independent of §P.

**Strict endpoints.** `L = +0.30` exactly → **not** material positive persistence.
`U = −0.20` exactly → **not** materially adverse. `L = 0` exactly → **not**
positive. Only interval endpoints classify; **the point estimate never classifies
anything.**

### §D.1 Materiality threshold ≠ point-estimate threshold

This is the single most important sentence in the contract. The final
classification uses **uncertainty**, not the realised Sharpe:

- a realised Sharpe of 0.80 does **not** establish material positive persistence;
- a realised Sharpe of −0.10 does **not** establish material adversity;
- a realised Sharpe of 0.35 does **not** establish anything at all.

Every statement in §O is a statement about the **95 % interval**, and no result may
be reported against `+0.30` or `−0.20` on the basis of a point estimate.

### §D.2 Preregistered reachability disclosure — outcome-independent, and honest

On the iid-normal design approximation at `N = 120` and the **central 95 %
two-sided** interval (§N), the half-width of an annualised Sharpe interval is ≈
**0.62** (standard error `√((1 + S²/24) / 120) · √12`; declared constants only, no
sample quantity used). The realised Sharpe each proposition would require is
therefore approximately:

| Established proposition | Requires realised Sharpe of about |
|---|---|
| `L > +0.30` — material positive persistence | **> +0.92** |
| `L > 0` — positive sign | **> +0.62** |
| `U < +0.30` — material persistence ruled out | **< −0.32** |
| `U < −0.20` — materially adverse | **< −0.82** |

**What this means, stated plainly rather than buried.** The band in which **nothing
is established** is wide: a realised Sharpe anywhere between roughly −0.32 and
+0.62 yields `UNRESOLVED`. Fable's OD-1/OD-2 advisory classified the pair
(+0.30, N = 120) as `TOO_UNDERPOWERED`, with P(material) ≈ 29 % under a fully
undecayed true raw Sharpe of 0.75 and ≈ 9 % at 0.50. **The Owner made this choice
with that advice in front of him, and reaffirmed it when fixing the interval
(§N.1): the resulting high probability of an `UNRESOLVED` terminal result is
intentionally accepted.** It is not reopened. It is recorded because a
preregistration that hides its own power profile is not a preregistration.

**Which configurations are reachable at `N = 120` — corrected.** An earlier draft
of this section asserted that *every* state remains reachable. That was wrong for
one configuration and is corrected here:

| Configuration (§O.1) | Reachable at `N = 120`? |
|---|---|
| `C1` `MATERIAL_POSITIVE_PERSISTENCE` | **YES** |
| `C3` positive sign, materiality unresolved | **YES** |
| `C4` `MATERIALLY_ADVERSE` | **YES** |
| `C5` `MATERIAL_PERSISTENCE_RULED_OUT`, direction not established | **YES** |
| `C6` `UNRESOLVED` | **YES** (the modal outcome) |
| `C2` `POSITIVE_BUT_DECAYED` (`L > 0` **and** `U < +0.30`) | **NO — logically defined, practically unreachable.** It requires the whole interval inside `(0, +0.30)`, i.e. a width below 0.30, where the architecture delivers ≈ 1.24 at `N = 120`. Reaching it would need `N` of order 2,000 months for an ordinary return series. |

`C2` is **retained in the rule** because the classifier must be total and because a
degenerate low-variance path could in principle produce it; it is **not** expected
to occur, and its paths are absorbed by `C3` and `C6`. **No decision, floor or
horizon changes because of this** — `C2` maps to `supported` and `C3` maps to
`supported`, so nothing in the claim ladder turns on the distinction.

Two further honest qualifications: (i) the sealed stationary bootstrap on a
serially dependent, fat-tailed record is typically **wider** than the iid
approximation, so the table above is optimistic; (ii) the raw primary's power rises
with the bill rate through the cash component described in §A, so the realised
power depends on a rate regime nobody controls.

**Mechanical status.** Synthetic reachability and classifier totality were verified
against the §N architecture on **synthetic series only** during the S1 bounded
repair of 2026-09-14 (`ca_synthetic_reachability.py`; no target data of any kind).
They are re-verified against the final sealed text at the seal gate (§Z.1).

---

## §E Scored forward boundary

| Field | Definition |
|---|---|
| `SEAL_TIMESTAMP` | Aaron's seal of this contract (UTC). Starts the T4 clock **for this claim family** and for nothing else. |
| `PIPELINE_GO_LIVE` | The timestamp at which the vintage / lock pipeline (§I) is accepted and has taken its first monthly snapshot under the sealed rule. |
| `PROSPECTIVE_START` | `max(SEAL_TIMESTAMP, PIPELINE_GO_LIVE)`. **A seal alone does not create a prospective record.** |
| `FORWARD_BOUNDARY` | The last eligible market observation **strictly before** `PROSPECTIVE_START`. Every observation on or before it is history for this lineage. |
| `FIRST_ELIGIBLE_SCORED_PERIOD` | The first calendar month `m` whose **decision month-end close** (the last trading day of `m−1`) is timestamped **strictly after** `PROSPECTIVE_START`. Both the decision and the whole holding month then post-date `PROSPECTIVE_START`. |

**Why the decision timestamp, not the return month, defines eligibility.** A month
whose position was decided before the seal is a position the designers could in
principle have known when sealing; scoring it would let the seal date be chosen
with knowledge of the open book. Requiring the **decision** to post-date the seal
closes that route at a cost of at most one month.

### §E.1 Two snapshots, never conflated: `S_0` and `S_G`

The seal and pipeline go-live are **distinct events** and may occur at distinct
times. Each has its own snapshot, and neither substitutes for the other.

| | **`S_0` — SEAL SNAPSHOT** | **`S_G` — GO-LIVE BASE SNAPSHOT** |
|---|---|---|
| Taken at | the seal gate | immediately before / at `PIPELINE_GO_LIVE`, under the sealed §I vintage rules |
| Purpose | pins **what was available at seal**; establishes seal provenance; verifies the historical / frozen-panel overlap | supplies the **state from which the prospective pipeline begins**; determines the effective pre-prospective state when go-live is later than the seal |
| Requirement | must reproduce the frozen panel over 1993-01-29 → 2026-06-12 **at the daily-return level** (`LOCKBOX_PROCEDURE.md` §6); every exceedance enumerated and classified under §J **before** sealing | must reproduce `S_0` over their common window at the daily-return level, with every exceedance classified under §J **before** go-live |
| Determines `FORWARD_BOUNDARY`? | **NO, not by itself** | **YES**, when `PIPELINE_GO_LIVE > SEAL_TIMESTAMP` |
| Pinned by hash | in the seal | in the snapshot registry at go-live |

**`S_0`'s last observation is NOT required to equal the eventual
`FORWARD_BOUNDARY`.** That requirement was a defect of an earlier draft: it silently
assumed seal and go-live coincide. What **is** required is that both snapshots exist,
that each is pinned by SHA-256, and that an **immutable lineage / hash linkage
between `S_0` and `S_G`** is recorded in the snapshot registry, so the provenance
chain from the frozen historical panel through the seal to the first prospective
decision is unbroken.

**If `PIPELINE_GO_LIVE > SEAL_TIMESTAMP`**, every observation between `S_0` and
`S_G` is classified:

```
POST_SEAL_UNSCORED_STATE_INPUT_ONLY
  - MAY update the canonical state required for the first post-start decision
    (lookback closes, asset vol, base-book vol);
  - is NEVER scored;
  - is NEVER retroactively a T4 outcome;
  - contributes ZERO to N_scored;
  - is declared and wasted, never recovered.
```

**No pre-seal scored period may enter C-A.** Already-accrued post-boundary months
(2026-06-13 onward) are **never** retroactively called T4, and are never called T3
either: their exposure status is `UNKNOWN_PENDING_AUTHORITATIVE_VERIFICATION`
(`LOCKBOX_PROCEDURE.md` §5), and the standing rule is `no record ⇒ UNKNOWN, never
NONE`.

---

## §F Warm-up treatment

```
WARMUP_INPUT     ≠  SCORED_OUTCOME        (the two are never merged and never counted together)
```

**No forward warm-up is required.** The rule's state at `PROSPECTIVE_START` — 12
month-end closes for the composite, 60 daily returns for asset volatility, 60 daily
base-book returns for portfolio volatility — is supplied **entirely by pre-start
data** (`S_G`, §E.1). No scored month is spent building state.

### §F.1 The four-step sequence — binding, and the only reading

```
1. PRE-START HISTORY
     -> state input for lookbacks and volatility. Never scored.

2. PRE-START HELD POSITION
     -> may serve ONLY as the prior-position term needed to compute turnover at the
        first eligible prospective decision transition, where the canonical
        arithmetic requires it. It is NEVER the scored holding position.

3. FIRST POST-PROSPECTIVE_START DECISION MONTH-END  (call it D1)
     -> the canonical prospective position is computed from S_{D1} alone and LOCKED.

4. THE FOLLOWING COMPLETE HOLDING MONTH  (call it M1)
     -> the FIRST ELIGIBLE SCORED MONTH. The position held during M1 is the one
        locked at D1.
```

**The position held during the first scored month is the position generated and
locked at the first eligible post-`PROSPECTIVE_START` decision month-end.** A
pre-`PROSPECTIVE_START` position is **never** the scored holding position.

**What the pre-start held position is still used for, and only this.** Canonical
turnover entering month `t` is `Σ_i |position_{i,t} − position_{i,t−1}|`, so the
first scored month `M1` needs a prior-position vector. That vector is the position
held during the month before `M1` — a position decided before `PROSPECTIVE_START`.
It enters **as the turnover term and nothing else**: its own return month is not
scored, it is not a prospective decision, and it contributes zero to `N_scored`.
This keeps `M1`'s turnover and cost ordinary rather than an artificial entry cost,
**without** scoring any pre-start decision.

**This is a contract-consistency repair, not a change to the canonical strategy
timing.** The canonical rule is unchanged: `positions = weights.shift(1)`, a
position decided at month-end `t−1` is held through month `t`.

```
NO PRE-START RETURN IS SCORED.
NO POSITION CHOSEN BEFORE PROSPECTIVE_START BECOMES A SCORED PROSPECTIVE POSITION.
```

**Classification of every pre-`PROSPECTIVE_START` month**, including the months
already accrued since the frozen boundary and any
`POST_SEAL_UNSCORED_STATE_INPUT_ONLY` months (§E.1):

```
ACCRUED_UNVERIFIED_STATE_INPUT_ONLY
  - feeds signal formation and volatility estimation;
  - is NEVER scored;
  - is NEVER called T3 (protection is unverified);
  - is NEVER called T4 (accrued history is never relabelled prospective);
  - contributes 0 to N_scored.
```

Warm-up history may be used to compute signals and volatility, and the pre-start
held position may be used as the §F.1 step-2 turnover term, because the sealed rule
says so. Neither may be used for anything else.

---

## §G Scoring month definition

A calendar month `m` is a **scored month** if and only if **all** of the following
hold. The list is exhaustive; nothing else makes a month scorable and nothing else
disqualifies one.

1. The **decision close** (the last trading day of `m−1`) is timestamped strictly
   after `PROSPECTIVE_START` (§E).
2. The position vector for `m` was computed from snapshot `S_{m−1}` alone, passed
   the monthly integrity gate (§T.2), and was **locked** before any price of `m`
   was observed by the pipeline.
3. The checkpoint snapshot contains the **month-end trading day's close for every
   live asset** (§H).
4. The month is not classified `RUN_INVALIDATING_EVENT` (§U) and is not held
   `PENDING_CLASSIFICATION`.
5. The canonical-17 record has not been frozen at or before `m` under §K.

```
N_scored  =  the count of scored months, in calendar order, with no gaps permitted
             inside the window: an unscorable month terminates the scored window
             at m−1 unless it is classified MECHANICAL_CORRECTION and becomes
             scorable within the same SNAPSHOT_LAG cycle.
```

**A month is scored once.** Its scored status is never revisited after the terminal
reveal, and never revised to improve a result.

---

## §H Partial-month policy

```
PARTIAL_MONTH_TREATMENT  =  NO PARTIAL MONTH IS EVER SCORED. TRUNCATION, ALWAYS.
SNAPSHOT_LAG             =  5 business days after calendar month-end
```

- A month is scorable only when the checkpoint snapshot contains the **month-end
  trading day's close for every live asset**. Snapshots are taken at
  `SNAPSHOT_LAG` so vendor settlement is complete.
- The **seal-time partial month** (the calendar month containing
  `PROSPECTIVE_START`) is state input, never a scored month.
- The **terminal month** is a complete month by construction: `N_scored` counts only
  complete, eligible, non-invalidated months, so the 120th scored month is by
  definition complete. No terminal-partial-month rule is needed, and none is
  created.
- This closes the defect `LOCKBOX_PROCEDURE.md` §2.1 records in the historical
  panel, where the June-2026 monthly row is labelled `2026-06-30` but built from
  data ending `2026-06-12`. That row is **state input only** and is never scored.

---

## §I Data-vintage policy

### §I.1 Two layers — locked decisions, best-truth outcomes

Adjusted-close series are revised by construction, so "the panel" is not one object
over time. The contract therefore separates what a prospective record must protect:

1. **Position ledger — vintage-locked, immutable.** After each month-end `m−1`,
   snapshot `S_{m−1}` (hashed, append-only, retained forever) passes the integrity
   gate and the canonical engine computes the position vector for month `m` **from
   `S_{m−1}` alone**. The vector, its gross, net, leverage and the snapshot hash are
   written once and **never changed**. No later data can enter it.
2. **Return layer — computed from the checkpoint snapshot.** At the terminal look,
   month returns are computed by applying the locked positions to that checkpoint's
   month-end prices, with turnover from the locked positions. Corrections to past
   prints flow into outcomes as truth improves; **look-ahead cannot enter
   positions**. The checkpoint's scored series is hashed and archived.

A third, purely mechanical series — the canonical engine run end-to-end on the
latest snapshot — is compared to the locked positions (`max |Δposition|`). Its only
human-visible output before a reveal is a **boolean**: within tolerance, or not. It
measures vendor-revision effects on decisions; it can never replace the scored
primary.

### §I.2 Snapshot identity and retention

- **Append-only.** One snapshot per month at `SNAPSHOT_LAG`. **New snapshots never
  overwrite the frozen historical panel or any prior snapshot** — a refresh writes
  a new file with its own hash (`LOCKBOX_PROCEDURE.md` §3.1). A code path capable of
  overwriting the frozen panel is a **build-stage defect that must be guarded and
  regression-tested before `PIPELINE_GO_LIVE`** (§Z item 6).
- **Immutable identity.** Each snapshot is identified by path + byte size + SHA-256
  + verified first/last date + per-ticker row counts, recorded in an append-only
  snapshot registry **before** the snapshot is used.
- **Original vintage retained indefinitely.** Positions are reproducible from
  vintages at any time. `S_0` and the frozen panel are pinned by hash **in the
  seal**; `S_G` is pinned by hash **at go-live**, with the immutable `S_0` → `S_G`
  lineage recorded in the registry (§E.1).
- **Storage location.** Market data is git-ignored in this repository for licensing
  reasons (`.gitignore`: `data/`). Snapshots therefore live under a git-ignored
  prospective store, while the **hash registry itself is tracked** at
  `research/extensions/ca/CA_SNAPSHOT_REGISTRY.md`. The registry, not the files, is
  the committed record of identity.
- **Traceability.** Every scored month's outcome is traceable to the exact vintage
  used for its decision (the locked snapshot hash) and the exact vintage used for
  its return (the checkpoint hash). Both are recorded with the month.

### §I.3 The risk-free snapshot

The FM-1 rate series (§P) is snapshotted on the same monthly cadence, hashed in the
same registry, and its **decision-time value is locked with the position**. A later
revision to the series changes nothing already locked.

### §I.4 Runtime identity

The seal pins the execution runtime — Python, pandas, numpy versions at minimum —
because §B.2 establishes that a library default change would silently alter the
daily-return series. The pipeline refuses to run under an unpinned or mismatched
runtime. Current environment observed at drafting: Python 3.13.14, pandas 2.3.3,
numpy 2.5.0.

---

## §J Revision policy — three classes, never conflated

```
MECHANICAL_CORRECTION    = handled by a rule fixed here or at the seal, with no outcome
                           inspected and no builder discretion.
SCIENTIFIC_CHANGE        = alters what is being tested. An amendment of the sealed contract.
                           OWNER-ONLY. FORBIDDEN after any outcome of the affected months has
                           been seen; permitted before a reveal only where the seal pre-specifies it.
RUN_INVALIDATING_EVENT   = the affected months can no longer support the canonical forward claim.
                           Owner review; the record continues as descriptive.
```

| Event | Treatment | Class |
|---|---|---|
| Split / dividend back-adjustment | Expected and absorbed: multiplicative rescaling leaves returns and signals invariant within a single snapshot. The locked-vs-recomputed position diagnostic measures any residual. | `MECHANICAL_CORRECTION` (no action) if `max |Δposition| ≤ 0.01` and no sign flip; otherwise the vendor-correction row |
| Vendor correction of a past print | **Positions stay as decided** — a live implementer would also have decided on the print available. Returns update at the checkpoint. Tolerance: a scored monthly return may move by ≤ 1 bp and the cumulative scored Sharpe by ≤ 0.01 between checkpoints. | within tolerance → `MECHANICAL_CORRECTION`, logged; beyond → Owner review; if traced to a vendor defect that **changed a decision sign**, the affected months → `RUN_INVALIDATING_EVENT` (excluded from `N_scored`, disclosed) |
| Corporate action recorded late (an unadjusted split appearing as a > 50 % one-day move) | The integrity gate holds the ticker (`JUMP_THRESHOLD = 0.50`, spike-and-revert); the second-source panel from C-D is consulted by a **fixed rule**: if the primary vendor shows a jump absent from the second source **and** matching a declared corporate-action list, the primary is deemed erroneous for that ticker and the position for **that decision only** is computed on the second source's adjusted series. **No outcome is inspected.** | `MECHANICAL_CORRECTION`, logged with both hashes |
| Late data corrections (values revised weeks later) | As vendor correction. | as above |
| Missing bars — within a month | The canonical `resample.last()` rule stands (last available close in the month); the event is flagged. | `MECHANICAL_CORRECTION` |
| Missing bars — whole month at the decision deadline | Refetch inside `SNAPSHOT_LAG`; then the second-source substitution rule for that ticker-month; if neither source has it, the canonical `NaN → not in book` convention applies and the month is flagged. **Three consecutive uncovered months on one ticker → Owner review.** | `MECHANICAL_CORRECTION` when covered by the rule |
| Stale observations (unchanged close ≥ 5 consecutive sessions) | Integrity flag; second source consulted; a vendor-only stale run is a vendor defect (substitution rule); a two-source stale run is a market fact (halt). | mechanical / market fact |
| `rf` series revision | The decision-time value is locked with the position; a later revision changes nothing. | mechanical |
| Primary vendor discontinued, or overlap irreproducible | If a replacement vendor reproduces the locked inputs **at the return level within tolerance**, it succeeds **by rule**; otherwise the forward series splits into two datasets (`LOCKBOX_PROCEDURE.md` §6) and the Owner decides. | Owner review; possible `RUN_INVALIDATING_EVENT` |

**A post-hoc vendor correction can never silently rewrite prior scored evidence.**
Every checkpoint series is hashed and archived; the difference between successive
checkpoint series over their common window is a **reconciliation diagnostic** with
the declared tolerances above, reported as a boolean before any reveal.

**The rule that governs everything in this table.** If an event is not covered by a
row here or elsewhere in this contract, **the builder does not choose**. The event
is logged, the affected months are held `PENDING_CLASSIFICATION`, and the **Owner
classifies before any outcome of those months is revealed**. A classification made
after a reveal is a post-hoc escape route and is **void**.

---

## §K Canonical 17-object attrition policy — Owner decision OD-4

```
CANONICAL_UNIVERSE_POLICY  =  ALL_17_REQUIRED. NO MINIMUM-N FALLBACK. NO DYNAMIC UNIVERSE.
                              NO DISCRETIONARY POST-OUTCOME SUBSTITUTION. NO REPLACEMENT INSTRUMENT, EVER.
```

**Three general rules.**

1. **Identity is the fund entity, not the symbol.** The seal carries an instrument
   registry keyed by legal fund identity with a documented identifier chain.
   Symbols, CUSIPs, listing venues, sponsors and names may change without changing
   the object. Adjusted prices absorb splits.
2. **Data is not the object.** A data event is handled by §J and never changes the
   universe.
3. **When the economic object changes, the canonical record ends; it is never
   patched.** The only successor path is the single mechanical rule below, and
   **any ambiguity resolves to termination**.

| Event | Class | Treatment |
|---|---|---|
| **A** Ticker / symbol rename | `IDENTITY_PRESERVING` | registry mapping; record continues |
| **B** Administrative identifier change (CUSIP / ISIN / name / sponsor / listing venue) | `IDENTITY_PRESERVING` | registry mapping; record continues |
| **C** Split / reverse split | `IDENTITY_PRESERVING` | adjusted-price handling; record continues |
| **D** Merger / reorganisation into a successor fund | `IDENTITY_PRESERVING` **only** under the five-condition successor rule below; otherwise `MATERIAL_OBJECT_CHANGE` | successor at the documented conversion ratio; the predecessor's adjusted history is carried; disclosed |
| **E** Merger into a materially different mandate | `MATERIAL_OBJECT_CHANGE` | freeze rule below |
| **F** Closure / liquidation / delisting / any permanent disappearance without an identity-preserving successor | `MATERIAL_OBJECT_CHANGE` | freeze rule below |
| **G** Benchmark / index / methodology change while the fund persists | `IDENTITY_PRESERVING, DISCLOSED` **if** the fund remains in the same asset class and the same sleeve (the USO-2020 precedent, already inside the historical record); `MATERIAL_OBJECT_CHANGE` if it leaves its asset class | the only test is asset-class and sleeve membership — **no judgment of "how different"** |
| **H** Temporary trading halt / suspension | `TEMPORARY_DATA_EVENT` if trading resumes within **one calendar month** — the canonical last-available-close rule applies, and a halt spanning a decision date leaves the executed position at its prior weight until trading resumes, logged as an **execution deviation, not a rule change**; otherwise treated as **F** at the last complete month | mechanical |
| **I** Short temporary missing data | `TEMPORARY_DATA_EVENT` | §J conventions; second-source fill by rule; logged |
| **J** Permanent loss of the data source while the ETF still exists | `TEMPORARY_DATA_EVENT` if a predeclared alternative source reproduces the overlap at the return level within tolerance, which then succeeds by rule; otherwise a **data-integrity termination**, logged distinctly from an object termination | mechanical |

**Material change is judged from external fund / benchmark documentation only.**
Economic mandate, selection rules, weighting rules, intended exposure, investment
construction. **Never from strategy outcomes.** The classification is made by the
firewalled pipeline role, recorded with the source documents, **before any affected
month is scored**.

**Successor rule (event D) — automatic succession requires ALL FIVE conditions**,
verified from external documents before the successor's first scored month, with no
performance access:

1. legal / economic continuity — holders receive successor shares at a stated ratio;
2. materially the same mandate, operationalised mechanically as: **same asset class,
   same sleeve, same base currency, no leverage and no inverse exposure**, and the
   successor tracks the same index or the sponsor's documented replacement index;
3. no discretionary selection among alternatives — the reorganisation names exactly
   one successor;
4. the event is externally documented (sponsor filing);
5. successor treatment is mechanically defined by this rule.

**Ambiguity on any condition → TERMINATE.** This is the only successor path; it is
declared now and **cannot be extended later**.

**Freeze rule on a `MATERIAL_OBJECT_CHANGE`.**

- (i) the affected exposure exits at its **last available month-end close** (that
  final month is scored to that close; position 0 thereafter);
- (ii) the **canonical-17 record closes at that month and is FROZEN, NOT
  REVEALED**. Its interval and state are computed at the programme's terminal date
  with its own `N_scored` disclosed. **Performance is not revealed merely because
  the record terminated.**
- (iii) a **successor record** of the remaining instruments under the byte-identical
  rule (the canonical engine's own equal weight over live assets) continues from the
  same month, **generated-not-seen**, labelled `CANONICAL_MINUS_k`. It is **a
  different object**; it cannot upgrade the canonical-17 claim; whether to adjudicate
  it as its own lineage is an Owner decision **taken at the terminal look, never
  before**. A second disappearance applies the same rule again.
- (iv) **no replacement instrument, ever, inside this lineage.** Substitution is a
  `SCIENTIFIC_CHANGE` that would start a new lineage.

**Why freeze rather than reveal.** An early reveal would burn blindness for the
successor record too — the two share almost every outcome — and would classify the
canonical record at a small `N` where `UNRESOLVED` is near-certain. Freezing loses
nothing and preserves the single-look architecture.

---

## §L Terminal N — Owner decision OD-2

```
N_scored_TERMINAL           =  120 complete, eligible, non-invalidated scored months (~10 years)
AUTOMATIC_EXTENSION         =  NONE
```

Calendar dates are **consequences, not a schedule**: the terminal look occurs when
the 120th scored month exists, whenever that is.

**A further block of new months is not an extension.** It requires a separate Owner
authorization, a separate prospective seal, a separate record, and preservation of
the Block 1 result. It may be called a **SECOND PROSPECTIVE BLOCK** or a
**PROSPECTIVE TEMPORAL REPLICATION**. It must **not** automatically be called
statistically independent: the two blocks share the same strategy, the same
instruments, the same pipeline and the same designer, and only the outcomes are new.

---

## §M Single terminal reveal — Owner decision OD-2

```
POSITIVE_REVEAL_COUNT    =  1
INTERIM_POSITIVE_LOOK    =  NONE
ADVERSE_ONE_BIT_ORACLE   =  NONE
```

**What is revealed, all at once, at the single terminal look:** the primary interval
and its established propositions (§O); the FM-1 interval and its established
propositions (§P); the crisis-response diagnostic (§Q); and the mandatory reporting
elements — per-sleeve contribution, forward break-even cost for `L > +0.30` and for
`L > 0`, realised turnover, mean `net_held`, mean `rf`. These reporting elements are
**deterministic decompositions of the revealed series with no degrees of freedom**;
they are reporting, not designs, and they are computed once, after the reveal.

**Before the look:** the monthly integrity gate and an annual integrity review —
**booleans and counts only** (§T.2). No outcome. No human views a position vector.

**After the look:** the pipeline continues unchanged and months after the look
remain `GENERATED_NOT_SEEN`, so an independent replication on non-overlapping
months remains possible as a **new lineage opened by Owner decision**. **No second
confirmatory look exists inside this lineage.**

**Adverse evidence is adjudicated at the same single look.** `MATERIALLY_ADVERSE` is
fully reachable there (§D.2). **What is not adverse evidence, and triggers
nothing:** a drawdown of any size; a negative year; one crisis in which the book did
not earn; an integrity failure; a result in any other lineage.

---

## §N Inference method — reused, not invented

Every element below is **inherited from sealed precedent** (X01 §6.1, sealed
2026-09-13; Value §9.1, sealed 2026-09-13) and is frozen here. No element is chosen
after seeing any outcome, and no element was selected by inspecting any target
sample.

| Element | Frozen value | Precedent |
|---|---|---|
| Bootstrap family | **stationary bootstrap** (Politis & Romano 1994), geometric block lengths, circular wrap | X01 §6.1 |
| Expected block length | **L = 12 months** — a prospective design convention anchored to the longest signal-formation window (`max(MOMENTUM_LOOKBACKS_MONTHS) = 12`). It is **not** a claim that dependence ends at 12 months. | X01 §6.1 |
| Replicates | **10,000** (`config.BOOTSTRAP_N`) | X01 §6.1 / Value §9.1 |
| Confidence level | **95 %**, two-sided (`config.CI_LEVEL`) | X01 §6.1 / Value §9.1 |
| Interval construction | **percentile**, with linear interpolation — chosen over BCa deliberately, because BCa's acceleration term is estimated from the target sample and would add an outcome-touching component. **No alternative interval is computed and none is selected after the fact.** | X01 §6.1 / Value §9.1 |
| Seed protocol | `numpy.random.SeedSequence(7).spawn(k)` in a **fixed arm order** written into the sealed text at seal time (`config.RANDOM_SEED = 7`); the run reproduces bit-for-bit | X01 §6.1 / Value §9.1 |
| Resampling unit | the **joint monthly vector** `(r_net_t, x_t, sleeve-contribution vector_t)`, resampled **jointly** where statistics share the same path, never independently per series. One draw produces every interval, so no statistic silently receives an iid interval. | Value §9.1, extended mechanically to this contract's statistics |
| Invalid replicates | a replicate is invalid iff the statistic is undefined on it — zero variance in the series, or fewer than **24 distinct calendar months** represented. Invalid replicates are **discarded and counted, never re-drawn** (re-drawing conditions the sample on validity and biases the interval). | X01 §6.1 / Value §9.1 |
| Valid floor | fewer than **9,500** valid replicates → `INFERENCE_PROCEDURE_FAILURE`, a **mechanical** condition reported with the invalid count and explicitly **not** one of the states in §O | X01 §6.1 |
| Multiplicity | `BH_FDR_REQUIRED = NO` — see §R | X01 §6.1 |

**No new inference engine is introduced.** If a statistic later proves to need an
extension, the smallest required extension is stated at that point and **not
implemented before the seal**.

**The two limbs of the invalid-replicate rule are evaluated in the stated order, and
the distinct-month limb is load-bearing.** A replicate that drew one month
repeatedly has zero true variance, but in floating point its computed standard
deviation is of order 1e-18 rather than exactly zero, so the variance limb alone
would let it through as a Sharpe of order 1e15 and contaminate the percentile tails.
The **24-distinct-month limb catches that case first**, which is why it is evaluated
first. Verified mechanically on synthetic data during the 2026-09-14 bounded repair;
no rule changes, and the existing sealed rule is confirmed adequate.

### §N.1 ONE interval — Owner decision, 2026-09-14

```
PRIMARY_AND_DIRECTIONAL_SCIENTIFIC_INFERENCE
    = ONE central 95 % stationary-bootstrap percentile interval, per estimand.

FORBIDDEN: an alternative 90 % interval.
FORBIDDEN: a separate one-sided interval.
FORBIDDEN: selecting between intervals after outcomes.
```

**There is exactly one interval per estimand and it is computed once.** No second
interval at any other level or sidedness is computed, stored, reported or referred
to — not as a sensitivity, not as context, not as a footnote.

**Directional propositions are read off that one central interval.** A central 95 %
two-sided interval places a **2.5 % directional tail at each endpoint**, so each of
`P_MAT`, `P_POS`, `P_RULED`, `P_ADV` (§O) is a one-sided statement made at the 2.5 %
level. That is a deliberate property of the decision, not an oversight, and it is
**not** a licence to construct a one-sided 5 % interval to obtain a more favourable
endpoint.

**This decision intentionally accepts the resulting high probability of an
`UNRESOLVED` terminal result** (§D.2). `+0.30`, `−0.20` and `N = 120` are **not**
reopened by it, and blocker `SB-4` is closed by it (§Y).

### §N.2 The primary's interval does not depend on FM-1

The month draws depend only on `(seed, N_scored, expected block length)`. They are
therefore **identical whether or not FM-1 is adjudicable** (§P.2), and the primary's
interval is **bit-identical** either way. If FM-1 is `NOT ADJUDICABLE — DATA
INCOMPLETE`, `x_t` is simply absent from the joint vector; nothing about the
primary's resampling, replicate count, validity accounting or interval changes.
**Verified mechanically on synthetic series** during the 2026-09-14 bounded repair.

---

## §O Decision-state mapping

Let `[L, U]` be the sealed 95 % two-sided percentile interval for the estimand in
question (`L ≤ U` always). Four primitive propositions are evaluated, each with a
**strict** inequality:

```
P_MAT    :  L  >  +0.30     "the evidence supports Sharpe > +0.30"
P_POS    :  L  >   0.00     "the evidence supports Sharpe > 0"
P_RULED  :  U  <  +0.30     "the evidence supports Sharpe < +0.30"
P_ADV    :  U  <  -0.20     "the evidence supports Sharpe < -0.20"
```

### §O.1 Reported result = the established propositions, not a single forced label

The result is reported as the **set of propositions the interval establishes**, with
`[L, U]` and `N_scored` always printed. Because the inequalities can co-hold, **no
interval is forced into exactly one label.** `L ≤ U` implies
`P_MAT ⇒ P_POS ∧ ¬P_RULED ∧ ¬P_ADV` and `P_ADV ⇒ P_RULED ∧ ¬P_POS ∧ ¬P_MAT`, which
leaves exactly six reportable configurations:

| # | Established | Headline label | Plain meaning |
|---|---|---|---|
| **C1** | `P_MAT`, `P_POS` | **`MATERIAL_POSITIVE_PERSISTENCE`** | a material positive edge persisted prospectively |
| **C2** | `P_POS`, `P_RULED` | **`POSITIVE_BUT_DECAYED`** (and `MATERIAL_PERSISTENCE_RULED_OUT`) | the sign persisted **and** material persistence is ruled out — both facts are reported |
| **C3** | `P_POS` only | **`POSITIVE_SIGN_ESTABLISHED, MATERIALITY_UNRESOLVED`** | a positive expected Sharpe is established; materiality is neither established nor ruled out |
| **C4** | `P_ADV`, `P_RULED` | **`MATERIALLY_ADVERSE`** (and `MATERIAL_PERSISTENCE_RULED_OUT`) | expected performance is materially negative — a reversal |
| **C5** | `P_RULED` only | **`MATERIAL_PERSISTENCE_RULED_OUT`** | a material edge at the `+0.30` scale is excluded; **direction is not established** |
| **C6** | none | **`UNRESOLVED`** | the evidence does not establish any relevant directional region. `[L, U]` and `N` are the result. |

**These are scientific interpretation labels. They are NOT registry tokens** and
none of them may be written into a KB `research_status`, `claim_status`,
`evidence_type`, `future_role` or `lifecycle_status` field.

**Prohibited readings, fixed in advance.** `C5` and `C6` are **failures to
establish**, never evidence of harm — reporting either as adverse is forbidden.
`C4` is a strict adverse finding and may never be softened into `C5` or `C6`. `C3`
may never be reported as `C1`.

### §O.2 Mapping to existing KB tokens — existing vocabulary only

Legal values, verified against the schemas in `quant-research-knowledge-base/`:
`Finding.claim_status ∈ {confirmed, supported, partially_supported, unresolved,
contradicted, retired, not_promoted}`; `Finding.evidence_type` includes
`out_of_sample`, `lockbox`, `preregistered_primary`, `preregistered_robustness`,
`implementation_fact`, `post_hoc_diagnostic`; `Strategy.research_status ∈
{confirmed, supported, not_promoted, falsified, active, archived, experimental,
unresolved}`. **No new token is proposed by this contract.**

Forward finding `evidence_type` = **`out_of_sample`**, with the T4 context recorded
in `notes`. `lockbox` is the only alternative token and the choice between them is a
curator detail, not a scientific one. Both sit outside the gate-G4 prohibition set,
so neither blocks `confirmed` by itself.

| State | Forward finding `claim_status` | Strategy `research_status` |
|---|---|---|
| **C1** | `confirmed` **permitted only** with the full evidence package (§O.3); otherwise `supported` | `confirmed` **only by Owner promotion decision** — never automatic |
| **C2** | `supported`, never `confirmed`; the `+0.30` exclusion recorded with the bound | unchanged (`supported`) |
| **C3** | `supported`, never `confirmed` | unchanged (`supported`) |
| **C5** | `unresolved`, with `U` and `N` recorded and the descriptive flag `MATERIAL_EDGE_EXCLUDED` in prose | unchanged (`supported`) |
| **C6** | `unresolved`, with `[L, U]` and `N` recorded | unchanged (`supported`) |
| **C4** | `not_promoted`, with the margin recorded | `not_promoted` **by Owner decision**; `falsified` is **unavailable** on one test under the KB decisiveness convention |

**In every non-`C1` case the historical finding
`finding.tsmom-core.oos-sharpe-confirmed` is NOT marked `contradicted`** — its claim
was about 2008–2026 and stands as a historical statement. A limitation is appended
to it instead. (`contradicted` also requires a non-empty `contradicted_by`, gate G6.)

### §O.3 `confirmed` requires more than one C-A pass — stated explicitly

**A C-A pass does not automatically upgrade anything.** Every one of the following
must also hold, and each is checkable mechanically or is an Owner act:

1. `C_D_PASS` on record (§S);
2. the seal preceded `PROSPECTIVE_START` (§E);
3. zero unresolved `RUN_INVALIDATING_EVENT`s in the scored window (§U);
4. every reveal performed under `LOCKBOX_PROCEDURE.md` §4 with authorization logged
   **before** access (§V);
5. no post-seal amendment other than mechanically established **pre-reveal**
   corrections, recorded as such (§J);
6. the primary adjudicated at the declared look at the declared level, and the
   complementary designs revealed at the same look with **none used to gate** (§R);
7. `SAMPLE_REUSE.md` §5 rule 3 — a `confirmed`-grade **performance** claim requires
   T3 or T4 evidence. C-A supplies T4, which is **necessary, not sufficient**.
8. The registry's own bar for `research_status: confirmed` is *"cleared every
   promotion bar this registry currently requires"*, and **no strategy currently
   holds it**. Promotion is an Owner decision under vNext §10 and is never
   self-authorized by any agent.

The registry's `confirmed` description also includes *"adequately powered"*. §D.2
records that this design has low power **to reach** `C1`; it does not weaken a `C1`
outcome if one occurs, because `C1` requires a realised Sharpe of roughly +0.92 and
is by construction a strong result. Both facts are recorded on the card.

### §O.4 What no outcome of C-A establishes

Futures deployability · performance at any other cost level · the mechanism (timing
versus static premium) · robustness beyond the one sealed rule · anything about the
next regime · that the 2008–2026 result was or was not luck.

### §O.5 Prespecified joint reading of the primary and FM-1

Fixed now so that no result is spun afterwards. **The primary's state is always
reported first.**

**FM-1's states are the sign states of §P.5 — `FM1_POSITIVE`, `FM1_NEGATIVE`,
`FM1_SIGN_UNRESOLVED`, or `NOT ADJUDICABLE — DATA INCOMPLETE`. The primary's
materiality labels are never applied to FM-1.**

| Primary | FM-1 | Recorded reading |
|---|---|---|
| `C1` | `FM1_POSITIVE` | canonical claim prospectively supported; the funding-adjusted residual has an **established positive sign**, so the raw result is not the cash component alone under the sealed convention |
| `C1` | `FM1_SIGN_UNRESOLVED` | canonical claim prospectively supported; the sign of the funding-adjusted residual is **NOT established** — the cash component (mean `net_held`, mean `rf`) is reported and the reading says so explicitly |
| `C1` | `FM1_NEGATIVE` | canonical claim prospectively supported **as stated**; under the FM-1 convention the path had an established negative residual against cash. The canonical `rf = 0` accounting is recorded as the source of the difference; the deployment reading is FM-1's, and **the canonical claim is still not upgraded or downgraded by FM-1** |
| `C1` | `NOT ADJUDICABLE` | canonical claim prospectively supported; **FM-1 emits no sign finding at all** (§P.2). The primary adjudication is unaffected, and the incompleteness is recorded as a complementary-data failure |
| `C2`, `C3`, `C5`, `C6` | any | the canonical claim is **not upgraded**; FM-1's sign state, if adjudicable, is recorded on its own card |
| `C4` | any | canonical claim prospectively adverse. **FM-1 cannot rescue it**, whatever its sign |

---

## §P FM-1 — complementary estimand — Owner decision OD-3

```
NAME                         = the idealised funding-adjusted residual under the sealed
                               symmetric-cash convention
ROLE                         = COMPLEMENTARY. Confirmatory for ITS OWN question only.
IS_PRIMARY                   = NO
CAN_RESCUE_PRIMARY           = NO
CAN_REPLACE_PRIMARY          = NO
CAN_BECOME_FALLBACK_PRIMARY  = NO
CAN_UPGRADE_CANONICAL_CLAIM  = NO
INDEPENDENT_REPLICATION      = NO
SAME_FORWARD_SAMPLE          = YES — identical months, identical locked positions
DECISION_SCALE               = SIGN AGAINST ZERO ONLY (§P.5). NO +0.30 / -0.20 FLOORS.
CARD_CEILING                 = `supported` in every case; a convention-dependent estimand is never `confirmed`
```

**It must never be described as a guaranteed upper bound on realistic excess
return.** That wording was withdrawn at S0 and is forbidden here: a real account
also has *positive* terms the convention omits, so the sign of the omitted total is
not guaranteed.

### §P.1 Mathematical form

```
x_t          =  r_net_t  −  net_held_t · rf_t
S_x          =  mean(x) / std(x, ddof = 1) · √12          (same window, same bootstrap as §N)
```

- **`net_held_t`** = `Σ_i position_{i,t}`, the **signed** sum of the positions
  actually held during month `t`, read from the **locked position ledger** (§I.1) —
  i.e. the weights decided at month-end `t−1`. It is not recomputed at the
  checkpoint and it is not the decision-month weight vector.
- **`r_net_t`** = the canonical net monthly return of §C, unchanged. The canonical
  2 bps transaction cost is applied **before** the cash term; FM-1 changes no cost.

### §P.2 Rate series, timing and alignment — **AUTHORITATIVE (Owner decision, 2026-09-14)**

Fixed by the Owner; blocker `SB-1` is closed (§Y). This is binding, not a draft.

```
SERIES              = FRED DGS3MO
OBSERVATION         = last available NON-MISSING print on or before the decision date
FRESHNESS           = the accepted print must be no older than 7 CALENDAR DAYS
MONTHLY_CONVERSION  = rf_t = Y / 100 / 12
LOCKING             = the accepted rf_t is locked with the prospective position for that month
FALLBACK_SERIES     = NONE
```

- The **decision date** is the last trading day of month `t−1`. The value is known
  at decision time, so `x_t` is causal.
- `rf_t = Y / 100 / 12` is **simple proration** of the annualised quote, **not**
  geometric de-annualisation.
- Once accepted and locked, `rf_t` is **never revised** by a later FRED revision
  (§I.3).

**If no valid `DGS3MO` print exists within the 7-calendar-day freshness window:**

```
RF_MISSING = TRUE
```

**Forbidden in that case, without exception:** substituting `DGS1MO` or any other
series · carrying forward an arbitrarily old yield · interpolating · using a future
observation · inventing another rate source.

**Consequences of `RF_MISSING`, stated exhaustively.**

| | Rule |
|---|---|
| **The canonical PRIMARY** | **COMPLETELY UNAFFECTED.** The primary does not use `rf` at any point. The position ledger, `N_scored`, the primary series and the primary interval are all unchanged (§N.2). |
| **FM-1's sample** | FM-1 **must preserve the SAME scored-month sample as the primary.** Therefore: **do not drop** an `RF_MISSING` month from FM-1; **do not silently shorten** FM-1's `N`; **do not impute** the rate. |
| **Pre-reveal recovery** | If the missing rate is later established, **before the reveal**, to be a purely **mechanical / vendor transmission issue** and can be recovered **causally** under the sealed correction rule (§J), it **may be repaired** and is logged as a `MECHANICAL_CORRECTION`. |
| **Unresolved at the terminal reveal** | `FM-1 FORMAL SIGN ADJUDICATION = NOT ADJUDICABLE — DATA INCOMPLETE`, while `PRIMARY ADJUDICATION = UNAFFECTED`. **This is a complementary-data failure, not a primary-study failure**, and it is recorded as such. No FM-1 sign finding is emitted (§P.5). |

**No discretion remains here.** The earlier draft held an `RF_MISSING` month as
`PENDING_CLASSIFICATION` for Owner classification before a reveal; that is
**superseded** — the rule above is deterministic and the only Owner act left is the
pre-reveal mechanical-correction judgment already governed by §J.

### §P.3 Interpretation — exactly what it means and what it cannot mean

**Means:** the canonical raw performance net of the cash return attributable to the
**held net exposure** at the declared bill rate, under the stipulation that every
position is financed and every dollar of collateral is remunerated at that one rate.

**Cannot mean:** what a real account would have earned.

### §P.4 Known accounting omissions — both directions

| Component | Real book | FM-1 convention | Direction of the omission |
|---|---|---|---|
| Long financing above 100 % of NAV | margin at bills + spread, or swap | financed at bills, zero spread | **cost omitted** |
| Short proceeds / rebate | bills − spread, often ≈ 0 retail | earn bills | **cost omitted** |
| Borrow fees | material on UNG / USO / DBA / RWX at times | none | **cost omitted** |
| Collateral yield | sweep rate ≤ bills; segregated haircuts | 100 % of NAV at bills | **cost omitted** |
| Gross vs net | spreads scale with gross; Reg-T cannot carry 3× gross | only net matters under symmetry | **ignored** |
| Securities-lending income on hard-to-borrow longs | positive | none | **benefit omitted** |
| Collateral / short-proceeds yield above the 3-month bill under an inverted curve | possible | none | **benefit omitted** |
| ETF internal carry and expenses | inside the fund's total return | already inside `R_i` | not omitted |
| Distributions on shorts | paid on the pay date | in the adjusted total return at the ex-date | timing only, immaterial monthly |
| Transaction costs | spread and impact | canonical 2 bps, unchanged | as the primary |

**Consequence:** FM-1 is neither a bound nor a forecast. It removes the one
first-order term whose sign and magnitude are **known** — the bill yield embedded in
a net-long book, of the same order as the materiality floor at positive rates — and
nothing else.

### §P.5 FM-1 decision states — sign against zero only — **AUTHORITATIVE (Owner decision, 2026-09-14)**

```
FM-1 HAS NO +0.30 / -0.20 MATERIALITY FLOORS.
The primary materiality scale is NOT borrowed, inherited or applied to FM-1.
```

FM-1 asks a **narrower complementary question**: *does the idealised
funding-adjusted residual have an established positive or negative sign under the
sealed convention?* It is adjudicated on the **same central 95 % bootstrap
architecture** as the primary (§N, §N.1) — one interval, no alternative level, no
one-sided variant — against **zero**:

| State | Condition (strict) |
|---|---|
| **`FM1_POSITIVE`** | `L > 0` |
| **`FM1_NEGATIVE`** | `U < 0` |
| **`FM1_SIGN_UNRESOLVED`** | otherwise |
| **`NOT ADJUDICABLE — DATA INCOMPLETE`** | any unresolved `RF_MISSING` month at the terminal reveal (§P.2) — no interval is computed and no sign state is emitted |

**Forbidden vocabulary for FM-1:** `MATERIAL_POSITIVE_PERSISTENCE`,
`MATERIALLY_ADVERSE`, `MATERIAL_PERSISTENCE_RULED_OUT`. Those labels belong to the
primary materiality scale and may never be written against FM-1. The §O.1
configurations `C1`–`C6` likewise do **not** apply to FM-1.

**KB mapping for the FM-1 card**, capped at `supported` in every case (a
convention-dependent estimand is never `confirmed`): `FM1_POSITIVE` → `supported`;
`FM1_NEGATIVE` → `not_promoted` with the interval recorded; `FM1_SIGN_UNRESOLVED` →
`unresolved` with `[L, U]` and `N` recorded; `NOT ADJUDICABLE` → **no FM-1 finding
card is created**, and the incompleteness is recorded in the run artifact and the
project record instead. FM-1 moves **no** strategy `research_status` in any case.

**Dependence, disclosed on the card:** FM-1 uses the same months and the same locked
positions. `x ≡ r_net` exactly when rates are zero, so the correlation with the
primary is near 1 at low rates and falls as rates rise. The realised correlation is
reported at the terminal look.

**Asymmetric evidential weight, unchanged.** An `FM1_NEGATIVE` means that even under
the most favourable financing assumption in §P.4 the residual against cash was
negative — decisive downward for that question. An `FM1_POSITIVE` means the raw
result is not the cash component alone *under this convention*, and says nothing
about realistic implementation costs. Neither moves the canonical claim.

---

## §Q Crisis-response diagnostic — RETAINED, fully ex-ante

**The question asked of it first: can it be specified prospectively without any
future subjective episode selection?** **Yes.** Every input is a deterministic
function of SPY month-end adjusted closes in the checkpoint snapshot. No human
labels an episode, no alternative window is computed, and nothing is chosen after
an outcome. It is therefore **retained**, as a descriptive diagnostic.

```
ROLE                         = DESCRIPTIVE DIAGNOSTIC (evidence_type preregistered_robustness)
PROMOTION_POWER              = NONE
CAN_UPGRADE_CANONICAL_CLAIM  = NO — not independently, not jointly, not in any combination
CAN_RESCUE_OR_OVERTURN_PRIMARY = NO. It may narrow or weaken the mechanism reading in prose.
MULTIPLICITY_TREATMENT       = none required (no claim power)
REVEAL                       = ONLY at the single terminal look. Never when the crisis happens.
```

**Mechanical definition, frozen.**

1. **Drawdown series.** `DD_m = SPY_m / max(SPY_j : j ≤ m) − 1`, on SPY **month-end
   adjusted closes** from the checkpoint snapshot, using the full available history
   including pre-boundary months (the running maximum is a property of SPY, not of
   the strategy).
2. **Trigger.** The first scored month `m*` with `DD_{m*} ≤ −0.20`.
3. **Peak month `p`.** The month-end at which the running maximum in force at `m*`
   was set.
4. **Window start.** The month **after** `p`.
5. **Window end.** The **trough month** — the month-end in `[start, terminal scored
   month]` at which SPY's adjusted close is lowest. If SPY has not set a new
   all-time high by the terminal scored month, the window ends at the last scored
   month and is flagged **`ONGOING_AT_TERMINAL`**.
6. **Reported.** Cumulative net return of the book over the window; short-side
   versus long-side contribution; per-sleeve contribution. Contributions use the
   original capital basis with no re-scaling (the Value C3 contribution-ledger
   convention).
7. **If no window occurs before the terminal look:** report **"no qualifying
   crisis"**. That is a complete and acceptable result, not a gap.
8. **One definition.** No alternative threshold, no alternative window, no
   re-centring, no extension, no split, no second episode ontology.

This is the repository's own kill criterion 4 (`DESIGN_DECISIONS.md`: *"crisis alpha
failing to appear in a new crisis"*), rendered testable. It remains **descriptive**
because it is conditional on an event that may not occur and would have an `N` of a
handful of months.

---

## §R Multiplicity and dependence disclosure

```
CONFIRMATORY_FAMILY  F-CA            =  { the primary, §C }          -- exactly ONE member
BH_FDR_REQUIRED                      =  NO
ALPHA_SPLITTING                      =  NONE
NUMBER_OF_COMPLEMENTARY_DESIGNS      =  2   (FM-1 §P; crisis diagnostic §Q)
```

**Why no correction.** The confirmatory family contains exactly one test. FM-1 is
confirmatory **for its own question**, on its own card, capped at `supported`, and
**cannot move the canonical claim in either direction**; the crisis diagnostic emits
no verdict at all. Neither creates multiple-testing exposure on the canonical claim,
so there is nothing to correct. This is the statement of multiplicity treatment the
programme's rules require — not a deferral.

**Dependence, disclosed on every card produced by this contract.**

| Object | Relationship to the primary |
|---|---|
| FM-1 | **same months, same locked positions**; a deterministic transformation of the same path plus one exogenous rate series. Correlation near 1 at low rates. **Never a replication.** |
| Crisis diagnostic | a **subset** of the same scored months |
| Per-sleeve contributions | a **deterministic decomposition** that sums to the primary series |
| Any `CANONICAL_MINUS_k` successor record (§K) | shares almost every outcome with the frozen canonical-17 record. A different object; **never a replication** |

**No post-outcome addition of confirmatory tests to `F-CA`.** A new confirmatory
question after any reveal is a **new lineage**, and the revealed months are T0 for
it. **No selection among variants on forward data**, ever. **Model or reviewer
diversity is review diversity, never evidence multiplication.**

---

## §S C-D prerequisite

```
C_D_REQUIRED_BEFORE   =  the first C-A reveal (not before the seal)
C_D_PROVIDES          =  implementation verification and data/source reconciliation
C_D_PROVIDES_ALPHA_EVIDENCE          =  NO
C_D_CAN_MOVE_research_status         =  NO
C_D_CONTAINS_NEW_HISTORICAL_OUTCOME_ANALYSIS  =  NO
```

The specification is `../cd/CD_VERIFICATION_SPECIFICATION_DRAFT.md`. Its outcome
binds this contract as follows:

- **`C_D_PASS`** — required for any claim stronger than `supported` (§O.3 item 1).
- **`C_D_HOLD`** — a bounded unresolved mechanical discrepancy. **No forward reveal
  until resolved.** The pipeline continues accruing; blindness is unaffected.
- **`C_D_FAIL`** — see the C-D specification for the three branches. A C-D failure
  affects **reliance on the historical / canonical implementation evidence**. It
  does **not** automatically falsify the economic TSMOM hypothesis, and it does not
  by itself invalidate accrued forward months: a **causality defect** invalidates
  affected months only where they cannot be recomputed from retained vintages by the
  corrected engine (§U).

**The seal does not wait for C-D.** C-D's own historical-reference computations are
not design inputs, and none is required to fix any threshold in this contract.

---

## §T Lockbox and generated-not-seen handling

### §T.1 Reuse, do not build

The existing machinery is reused as-is: `LOCKBOX_PROCEDURE.md` (three-state
separation, snapshot identity, refresh protocol, the seven-step release procedure,
the `UNKNOWN` rule); the X01 / Value pattern of a **single-use authorization record
plus an immutable evidence artifact pinned by SHA-256**; and the exposure ledgers.
**No new lockbox architecture, no new governance file family and no new encryption
capability is created by this contract.**

**Who may produce inaccessible evidence.** The existing architecture provides
**procedural**, not cryptographic, inaccessibility: the pipeline writes the locked
position vectors and the checkpoint return series to disk, they are hashed and
registered, and **no session reads them** — precisely the `GENERATED_NOT_SEEN`
classification already used for `X01-RUN-0001`. That is the mechanism this contract
relies on. If Aaron wants cryptographic inaccessibility (encryption at rest with a
key the pipeline operator does not hold), that is a **new capability decision**, not
a requirement of this design, and it is not assumed here.

### §T.2 Integrity monitoring — what it MAY inspect

Booleans and counts only:

- snapshot present, hashed, and registered;
- overlap with the prior snapshot within tolerance, **at the return level**;
- per-ticker row counts; first and last date;
- jump / spike / stale flags and their disposition;
- `rf` value present and locked;
- positions computed and locked; the locked-vs-recomputed position diagnostic
  **within tolerance / not** (a boolean);
- mechanical invariants: `gross ≤ 3`, `|asset weight| ≤ 2`;
- `N_scored` to date; counts of `PENDING_CLASSIFICATION` and
  `RUN_INVALIDATING_EVENT` months;
- instrument-registry events (§K) and their classification, with the external
  documents cited.

### §T.3 What integrity monitoring MUST NOT reveal

**No human and no agent may see, before the authorized terminal reveal:**

cumulative return · Sharpe · drawdown · win rate · sleeve performance · FM-1
performance · the crisis-diagnostic outcome · **any position vector** · **or any
proxy sufficient to infer scientific performance**.

**Positions are outcomes by another name**: a position vector plus public knowledge
of subsequent market moves is performance. The gate emits invariant booleans about
positions, never the positions themselves.

### §T.4 Blindness breach

A protected forward outcome read outside §V is logged **immediately** as a
research-axis exposure event. The statistical validity of the sealed rule is
unchanged **provided no amendment follows**; what is lost is `GENERATED_NOT_SEEN`
status for the months so far, and the T4 status of those months for any **new**
claim family. **Any amendment after a breach ends the lineage.** Continue-or-restart
is an Owner decision.

---

## §U Invalidation conditions

**`RUN_INVALIDATING_EVENT` — the affected months can no longer support the canonical
forward claim.** They are excluded from `N_scored`, disclosed, and the record
continues as descriptive.

1. A **look-ahead / causality defect** in the sealed engine, where the affected
   forward positions **cannot** be recomputed from retained vintages by the
   corrected engine. (Where they **can** be recomputed — reproducibly, and with the
   defect established mechanically rather than from outcomes — the months survive,
   and the recomputation is disclosed.)
2. A **vendor defect that changed a decision sign** (§J).
3. A month held `PENDING_CLASSIFICATION` that the Owner classifies as invalidating.
4. **Primary vendor discontinuation** with no replacement reproducing the locked
   inputs at the return level within tolerance, where the Owner so classifies it.
5. A **halt exceeding 20 trading days**, or **three consecutive uncovered missing
   months** on one ticker, where the Owner so classifies it after review.

**Claim-invalidating, distinct from run-invalidating:**

6. Any **post-seal amendment** other than a mechanically established **pre-reveal**
   correction recorded as such. Such an amendment ends the claim's eligibility for
   anything above `supported`.
7. Any **amendment after a blindness breach** — this ends the lineage (§T.4).
8. Any **reveal performed without prior authorization**, or outside the authorized
   scope (§V).

**Not invalidating, and explicitly listed so no future session treats them as
such:** a drawdown of any size; a negative year; a crisis in which the book did not
earn; a `C_D_HOLD`; a `MATERIAL_OBJECT_CHANGE` (that **freezes** the record under
§K, which is a different thing); an integrity flag that the monthly gate resolved by
rule.

---

## §V Reveal authorization

**Exactly one authorized scientific reveal** (§M). It follows
`LOCKBOX_PROCEDURE.md` §4 in order, and the ordering invariant there is binding:
**AUTHORIZATION MUST PRECEDE PROTECTED OUTCOME ACCESS.**

1. Identify the release contract and the claim family.
2. Verify eligibility and protected-snapshot identity — the contract is sealed, this
   is the release it provides for, and the snapshot identity matches the registry.
3. **Declare the planned access scope before requesting authorization** — which
   snapshot, which months, which outputs, at what granularity, and which holdout is
   burned for which claim family. This declaration reveals nothing.
4. **Aaron gives explicit authorization against that declared scope. This is the
   gate.** Without it the procedure stops and no protected outcome is accessed.
5. Only then: access the outcome, and only within the authorized scope.
6. Log the actual access immediately in `ops/EXPOSURE_LEDGER.md` (§X).
7. Classify the downstream evidence: T4 is fixed by **when the outcome occurred
   relative to the seal**, never by when it was fetched.

**Authorization discipline, inherited from X01.** A reveal authorization is
**single-use** and is recorded in committed state; a chat statement alone is not
sufficient; a sealed contract is not authorization; a green preflight is not
permission; a consumed authorization can never authorize a second access.

**Emergency access** is Owner-declared only, for a **named integrity cause**, under
the same seven steps. If the declared scope cannot avoid outcome exposure, the Owner
chooses between (i) a firewalled agent whose only output is integrity booleans and
who is thereafter barred from design work in this claim family, and (ii) treating it
as this lineage's single look.

---

## §W Claim-transition limits

1. **No automatic status upgrade.** No outcome of C-A, alone or combined with any
   other artifact, changes a KB status by itself. Promotion, falsification and
   retirement are Owner decisions (vNext §10).
2. **The complement can never upgrade the canonical claim** and can never rescue,
   replace or become the primary (§P).
3. **The crisis diagnostic can never upgrade the canonical claim**, independently or
   jointly (§Q).
4. **C-D can never move `research_status`** (§S). `confirmed implementation_fact`
   never implies confirmed strategy performance.
5. **A `CANONICAL_MINUS_k` successor record can never upgrade the canonical-17
   claim** (§K).
6. **One decade is one test.** `falsified` remains unavailable on a single test
   under the KB decisiveness convention; **prefer `not_promoted` in doubt**.
7. **A second prospective block is not automatic independence** (§L).
8. **Scope limits that survive any outcome:** the claim is about the 17-ETF book, at
   2 bps, under the one sealed rule, over the forward months actually observed. Not
   futures. Not another universe. Not another cost. Not the mechanism. Not the next
   regime.
9. **`insufficient_evidence` is not a KB value.** Record `unresolved`; prefer
   `not_promoted` when in doubt. (vNext §14 and `SAMPLE_REUSE.md` §5.)
10. **Negatives are first-class.** `C4`, `C5` and `C6` are legitimate terminal
    results, not invitations to retune. No parameter change, floor change,
    resampling, universe expansion, arm substitution or repackaging of C-A follows
    from any of them.

---

## §X Exposure and lineage recording requirements

**Three axes, never inferred from one another:** `LANE` (which claims may be
emitted) · `TRIAL_ACCOUNTING` (`SAMPLE_REUSE` / `N_trials` / DSR rules only) ·
`OUTCOME_EXPOSURE`.

| Record | Requirement |
|---|---|
| `ops/EXPOSURE_LEDGER.md` (research axis) | Append a `NO_OUTCOME` row for each monthly snapshot **before it is used**; a `GENERATED_NOT_SEEN` row for each locked position vector and each generated-but-unrevealed return series; one `REVEALED_TARGET_METRIC` row at the terminal reveal, in the existing scope `HISTORICAL_CUMULATIVE`, listing the outputs actually revealed. **The file shape is load-bearing** — exactly one markdown table, parsed as the event table; rows append to it and no second table is added. **No new scope or classification token is created.** |
| `ops/REVIEWER_EXPOSURE_LOG.md` (seat axis) | A row for any seat that views a protected outcome, and for any seat barred from further design work in this claim family under §V. Seat exposure **never** enters the research ledger and **never** licenses a stronger evidence context. |
| `ops/EXECUTION_AUTHORIZATIONS.md` | The reveal authorization is recorded in committed state before access, single-use, per the existing D1–D6 policy. (That file's current scope is X01; whether C-A uses the same file or a sibling under the same rules is a mechanical S2 decision, not a scientific one.) |
| `research/extensions/TRIAL_LEDGER.md` | A `VARIANT_ATTEMPT` row for the C-A primary; `HYPOTHESIS_FAMILY = F-CA` declared **before** any member runs; FM-1 and the crisis diagnostic recorded as declared complementary members with `PROMOTION_POWER = NONE`. **No automatic `+1` per attempt.** |
| `research/extensions/SAMPLE_REUSE.md` | Append a row declaring the **prospective forward ETF sample** as a **new sample**, distinct from the frozen historical panel, with its own reuse record. Its `N_trials` begins at zero and C-A's primary is its first governed trial. **The frozen historical panel's trial-count convention (`NONE EXISTS`, an open Aaron decision in `TRIAL_LEDGER.md` §4) is untouched by C-A and is not resolved here.** |
| Instrument registry | Keyed by legal fund identity with a documented identifier chain; pinned at the seal; every §K event appended with its external source documents and its classification. |
| Snapshot registry | `research/extensions/ca/CA_SNAPSHOT_REGISTRY.md`, tracked and append-only (§I.2). |
| Scientific lineage | `ops/OWNER_DECISION_RECORD_PHASE_B.md` §8 is the authoritative record of who contributed what, including the rule that a seat which materially proposed an adopted element is **not** an independent certifier of it. |

**Phase-C parallel safeguards — the minimum, and no governance bureaucracy.**
Phase C may proceed after the C-A seal under exactly three constraints:

1. **Forbidden computation.** No Phase C session computes the canonical rule's
   **signal, positions or returns** on any month after `FORWARD_BOUNDARY`, on any
   panel. Reading post-boundary **prices** from the append-only store is not a
   breach; reading the **position or return** layers is, and is logged as both a
   research-axis exposure event and a C-A blindness breach (§T.4).
2. **Frozen object.** The C-A engine, pipeline and store are hash-frozen. Phase C
   neither imports nor modifies them and works in its own package; a Phase C need
   for a TSMOM variant is met by a copy under a different name in Phase C space.
3. **Overlay research waits; standalone research does not.** Any Phase C design
   using the canonical stream as a comparator or combination leg uses it **only over
   months ≤ `FORWARD_BOUNDARY`** until the terminal look, or under an
   Owner-declared scoped reveal logged as such. Standalone new-factor research on
   post-boundary data proceeds under its own seal and burns those months for its own
   claim family only.

**Phase C may not** change the C-A rule, change the C-A floors, change the terminal
`N`, access protected C-A outcomes, or retroactively add a Phase-C factor into the
canonical C-A claim.

---

## §Y S1 BLOCKER REGISTER

**The single authoritative register for this programme.** The C-D specification
points here rather than keeping its own copy. **None of these was silently chosen.**

```
SB-1  CLOSED by Owner decision, 2026-09-14
SB-2  CLOSED by Owner decision, 2026-09-14
SB-3  OPEN   — blocks C_D_PASS only. Does NOT block the C-A S1 seal.
SB-4  CLOSED by Owner decision, 2026-09-14
PC-1  CLOSED from EXISTING §J authority, 2026-09-14. No new tolerance created.
```

### PC-1 — `S_0` overlap classification · scope C-A · **CLOSED**

Raised 2026-09-14 by executing §Z.1 item 7, and **closed the same day from the
contract's own §J text — no new threshold, rule, tolerance or interpretation was
created.**

**Why it closed without a new tolerance.** The question as first framed — "what
numeric tolerance applies to the §E.1 daily-return overlap?" — was the wrong
question. §J does not adjudicate this event on raw daily returns at all. Its
**Split / dividend back-adjustment** row states the treatment and the test verbatim:

> *"Expected and absorbed: multiplicative rescaling leaves returns and signals
> invariant within a single snapshot. **The locked-vs-recomputed position diagnostic
> measures any residual.**"* — class `MECHANICAL_CORRECTION` (no action) **if
> `max |Δposition| ≤ 0.01` and no sign flip**; otherwise the vendor-correction row.

The decision quantity is therefore **the position, not the daily return**, and its
tolerance — **0.01** — was already fixed by the contract. The daily-return figures
are enumeration evidence, not the test.

**Event identification** (from data integrity only, never from any outcome): the
discrepancy is present in exactly and only the instruments carrying a
distribution-adjustment chain, the four canonical objects that pay no distribution
(**USO, UNG, GLD, FXY**) agree **bit-identically**, the per-ticker price ratio is a
near-constant factor, and the calendar is identical with zero one-sided
observations. That is the §J **split / dividend back-adjustment** row.

**Diagnostic result** (`ca_s0_position_diagnostic.py`; record at
`data/prospective/S0_20260913T165624Z.position_diagnostic.json`):

| §J condition | required | observed | |
|---|---|---|---|
| `max \|Δposition\|` | ≤ 0.01 | **1.348102e-04** | **PASS** (≈ 74× inside the tolerance) |
| sign flip | none | **0** | **PASS** |

402 decision months compared over 1993-01-31 … 2026-06-30, 6,477 position cells,
zero cells present on only one side.

**Data boundary, asserted rather than assumed.** Both panels were truncated to the
frozen historical window ending **2026-06-12 before any computation**; the script
asserts zero post-boundary rows entered the engine through any path — prices,
volatility windows or momentum lookbacks. **No post-boundary signal, position,
return, Sharpe, PnL, drawdown, performance statistic or performance proxy was
computed.** Only the two quantities §J names were emitted.

```
PC-1 CLASSIFICATION = MECHANICAL_CORRECTION (no action), under the §J
                      "Split / dividend back-adjustment" row.
NEW_TOLERANCE_CREATED = NO
```

**What this does not mean.** It does not establish anything about the strategy, and
it is not a performance result. It establishes that a refetch of the same vendor
panel does not move a single canonical decision by more than 1.35e-04 of a position
unit, and flips no decision sign, over the whole historical window.

- **What was found.** `S_0` and the frozen panel agree on the calendar exactly
  (8,400 common trading days, zero one-sided observations). At the daily-return
  level the maximum discrepancy across the canonical 17 is **3.389e-06**, and the
  four canonical objects that pay no distribution — **USO, UNG, GLD, FXY** — agree
  **bit-identically**. The discrepancy therefore sits in exactly and only the
  instruments carrying a distribution-adjustment chain, which is the signature of
  routine dividend back-adjustment rather than a vendor price correction.

### SB-1 — FM-1 risk-free series, timing and conversion · scope C-A · **CLOSED**

- **Question as raised.** Which risk-free series defines `rf_t` in
  `x_t = r_net_t − net_held_t · rf_t`; at what observation timing; and is the monthly
  value `Y/100/12` (simple proration) or `(1 + Y/100)^(1/12) − 1` (geometric)?
- **Why it needed an Owner decision.** The only rf convention in any sealed artifact
  is `config.RISK_FREE_ANNUAL = 0.0`. `DGS3MO` appeared in this repository solely as
  a **regime conditioning variable** for a falsified overlay (`src/yields.py`), never
  as a financing rate inside a return computation. Aaron's OD-3 adopted the estimand
  **form** and required that the rf source and timing be mechanically specified
  before seal. A Fable recommendation is not an adoption.
- **OWNER DECISION, 2026-09-14.** `DGS3MO`; last available **non-missing** print on
  or before the decision date; the accepted print must be **no older than 7 calendar
  days**; `rf_t = Y / 100 / 12`; locked with the prospective position for that month;
  **no fallback series**. Failure of the freshness window sets `RF_MISSING = TRUE`,
  with the primary completely unaffected, FM-1's sample preserved without imputation
  or shortening, pre-reveal mechanical recovery permitted under §J, and an unresolved
  case yielding `FM-1 = NOT ADJUDICABLE — DATA INCOMPLETE` while
  `PRIMARY ADJUDICATION = UNAFFECTED`.
- **Where it is now binding.** §P.2 (authoritative), §O.5, §P.5, §N.2.

### SB-2 — FM-1 decision scale · scope C-A · **CLOSED**

- **Question as raised.** Does FM-1 use the primary's `+0.30 / −0.20` materiality
  scale, or its own?
- **Why it needed an Owner decision.** CA-02 fixed "same scored months, same
  bootstrap, same floors" under Fable's `±0.15`. OD-1 replaced the **values** and
  stated they are independent of FM-1, without saying whether the complement inherits
  them. Applying a raw-calibrated `+0.30` to the cash-stripped residual would be a
  *stricter* requirement on FM-1 than on the primary.
- **OWNER DECISION, 2026-09-14.** **FM-1 has no `+0.30 / −0.20` floors.** The primary
  materiality scale is not borrowed. FM-1 asks the narrower complementary question of
  whether the residual has an **established sign** under the sealed convention, on
  the same central 95 % bootstrap architecture, against zero: `FM1_POSITIVE`
  (`L > 0`), `FM1_NEGATIVE` (`U < 0`), otherwise `FM1_SIGN_UNRESOLVED`. The primary's
  materiality labels may never be applied to FM-1.
- **Where it is now binding.** §P.5 (authoritative), the §P header block, §O.5.

### SB-3 — C-D second-source availability · scope C-D · **OPEN**

```
BLOCKS C_D_PASS        = YES
BLOCKS THE C-A S1 SEAL = NO
```

- **Exact question.** Which second, independently fetched price/distribution source
  for the 17 ETFs will C-D reconcile against, and is it reachable without registering
  an account, purchasing data, or bypassing any access control?
- **Why existing authority does not answer it.** No second ETF price source is
  established anywhere in this repository. The only prior workspace vendor survey
  (`commodity-carry-research/docs/DATA_FEASIBILITY_REPORT.md`) concerned **futures
  term structure**, not ETFs, and recorded that Stooq returned empty/blocked
  responses to automated fetch and that the Nasdaq Data Link free tier is not
  oriented to this use. Tiingo and Nasdaq Data Link both require account
  registration, which the drafting sessions are forbidden to perform.
- **Smallest decision required.** Owner authorization for a **bounded, zero-cost,
  read-only feasibility probe** of candidate public sources for the 17 tickers,
  reporting reachability and licence terms only — **no account registration, no
  purchase** — plus a decision on the fallback if none is reachable (C-D proceeds on
  its other items and records the reconciliation as `NOT_PERFORMED`, capping the
  outcome at `C_D_HOLD`).
- **Materiality.** §J's late-corporate-action rule depends on a second source
  existing, and §O.3 requires `C_D_PASS` for any claim above `supported`. It is a
  real precondition for `C_D_PASS`. **It must not be used as a reason to delay the
  C-A seal**, and it was not resolved in the S1 drafting sessions.

### SB-4 — interval construction under low power · scope C-A · **CLOSED**

- **Question as raised.** §D.2 disclosed that the pair (`+0.30`, `N = 120`) yields a
  high probability of `UNRESOLVED`. Should the inference therefore use a different
  construction — a 90 % interval, or a one-sided interval — to raise the chance of a
  directional conclusion?
- **Why it needed an Owner decision.** Any answer trades nominal error control
  against the probability of a terminal conclusion, and choosing among interval
  constructions is exactly the degree of freedom a preregistration exists to remove.
- **OWNER DECISION, 2026-09-14.** **ONE central 95 % stationary-bootstrap percentile
  interval**, on the existing accepted architecture. **No** alternative 90 % interval.
  **No** separate one-sided interval. **No** selection between intervals after
  outcomes. The resulting 2.5 % directional tail at each endpoint is accepted, and
  **the high probability of an `UNRESOLVED` terminal result is intentionally
  accepted**. `+0.30`, `−0.20` and `N = 120` are not reopened.
- **Where it is now binding.** §N.1 (authoritative), §D.2, §P.5.

### Contract-consistency repairs applied 2026-09-14 (not scientific blockers)

| id | Defect in the earlier draft | Repair |
|---|---|---|
| **CB-1** | §F said the strategy "enters the first scored month already in position, continuing from the weights decided at the last pre-boundary month-end" — which would have scored a month held under a **pre-start** position, contradicting §E's `FIRST_ELIGIBLE_SCORED_PERIOD`. | §F.1 fixes the four-step sequence: the first scored month's held position is the one locked at the **first post-`PROSPECTIVE_START` decision month-end**; the pre-start held position survives **only** as the turnover prior-position term. Canonical timing unchanged. |
| **CB-2** | §E conflated seal-time state with go-live state by requiring `S_0`'s last close to equal `FORWARD_BOUNDARY`. | §E.1 separates `S_0` (seal snapshot) from `S_G` (go-live base snapshot), keeps `PROSPECTIVE_START = max(seal, go-live)`, makes `S_G` determine `FORWARD_BOUNDARY` when go-live is later, requires immutable hash lineage between them, and classifies the interval as `POST_SEAL_UNSCORED_STATE_INPUT_ONLY`. |
| **CB-3** | §Z placed S2 build demonstrations inside the S1 seal preconditions. | §Z.1 / §Z.2 split the gates; no S2 implementation item blocks the seal. |
| **CB-4** | The C-D draft's status block read `C_D_SPECIFICATION_WRITTEN = NO` while the specification document existed. | The C-D status block now distinguishes the **written verification specification** (YES) from **sealing** (NO), from the **executable rule specification produced during C-D execution** (NO), and from **implementation** (NO). |

### Explicitly NOT blockers — resolved mechanically from existing authority

Recorded so no later session reopens them: the bootstrap family, block length,
replicate count, confidence level, interval construction, seed protocol and
invalid-replicate rule (§N, sealed X01/Value precedent); the joint resampling unit
(mechanical extension of Value §9.1); the snapshot lag and partial-month truncation
(§H); the terminal partial-month question (§H — does not arise); the `pct_change`
fill behaviour and runtime pinning (§B.2, §I.4 — a behaviour-preserving
specification tightening); the flat-signal / missing-vol aggregation behaviour
(§B.1 — settled by the byte-identical-engine rule); and the frozen-panel overwrite
path (§I.2 — a build-stage guard, not a scientific choice).

---

## §Z Gate ordering — S1 SEAL versus S2 BUILD / GO-LIVE

The lifecycle is `S0 FRAME → S1 DESIGN+SEAL → S2 BUILD → S3 RUN → S4 VERDICT →
STOP`. An earlier draft placed S2 build demonstrations inside the S1 seal
preconditions. That was a stage-ordering defect and is corrected here.

```
NO S2 IMPLEMENTATION ITEM BLOCKS THE S1 SEAL MERELY BECAUSE IT HAS NOT YET BEEN BUILT.
```

### §Z.1 S1 SEAL PREREQUISITES — the complete list

| # | Item | Status |
|---|---|---|
| 1 | Owner decisions fixed (OD-1 … OD-4, plus the three S1 decisions of 2026-09-14) | **DONE** |
| 2 | Owner Decision Record confirmed as a faithful transcription | **DONE** (2026-09-14) |
| 3 | Preregistration internal-consistency validator passes (`ca_prereg_validate.py`) | **DONE** — re-run at the seal against the final sealed text |
| 4 | Synthetic reachability / logical-state validation passes (`ca_synthetic_reachability.py`; synthetic series only, no target data) | **DONE** — re-run at the seal against the final sealed text |
| 5 | No unresolved S1 **scientific** blocker (§Y) | **DONE** — `SB-1`, `SB-2`, `SB-4` closed; `SB-3` is a C-D implementation-verification blocker and does **not** block this seal |
| 6 | Instrument identity registry / specification pinned as required for the seal (§K) | **DONE — COMPLETE_FOR_SEAL.** §K conformance is documented inside the registry (`section_k_conformance`). — `CA_INSTRUMENT_REGISTRY.json`, 17 objects, keyed by the FIGI pair, every ISIN and CUSIP check-digit validated. Four fields are `NOT_PINNED` and disclosed there (prospectus legal name, sponsor of record, benchmark index name, prior-identifier lineage); none is required by any §K mechanism, which turns on **asset class and sleeve**, both pinned. |
| 7 | Seal-time snapshot and provenance procedure completed — `S_0` fetched, hashed, and verified against the frozen panel at the daily-return level, exceedances classified under §J (§E.1) | **DONE.** `S_0` pinned in `CA_SNAPSHOT_REGISTRY.md` §2, overlap in §3, and the event classified `MECHANICAL_CORRECTION` under the §J split/dividend row on that row's own test — observed max abs delta position **1.348102e-04** against the contract's 0.01, and **0** sign flips. |
| 8 | **`PC-1` closed** (§Y) | **DONE** — closed from existing §J authority; **no new tolerance created** |
| 9 | Acceptance by ChatGPT / Aaron, then **Aaron's seal** | **DONE — SEALED 2026-09-13T17:42:06Z** under Aaron's Owner authorization `SEAL C-A`. |

### §Z.2 S2 BUILD / GO-LIVE PREREQUISITES — outside the S1 seal gate

**None of these is authorized yet, and none of them gates the seal.** They gate
`PIPELINE_GO_LIVE`.

1. Frozen-panel **overwrite guard** and its regression test (§I.2).
2. **Explicit `pct_change`** fill behaviour at every call site (§B.2).
3. **Runtime enforcement** — the pipeline refuses to run under an unpinned or
   mismatched runtime (§I.4).
4. **Append-only snapshot writer** and the tracked hash registry (§I.2).
5. **Integrity gate** emitting booleans and counts only (§T.2).
6. **Write-once position ledger** that refuses to rewrite (§I.1).
7. **Behaviour-equivalence tests** against the seal runtime.
8. **Prospective pipeline implementation**, `S_G` acquisition and the first monthly
   snapshot under the sealed rule (§E.1).

```
S1_SEALED                     = YES  (2026-09-13T17:42:06Z, Owner: Aaron)
C_A_IMPLEMENTED               = NO
C_D_IMPLEMENTED               = NO
S_G_CREATED                   = NO
PIPELINE_GO_LIVE              = NOT YET
N_scored                      = 0
FIRST_ELIGIBLE_SCORED_PERIOD  = NOT YET DETERMINED
S2_STARTED                    = NO
TARGET_PERFORMANCE_COMPUTED   = NO
TARGET_OUTCOME_REVEALED       = NO
TARGET_RUN_AUTHORIZED         = NO
C_B_STATUS                    = PARKED
SB-3                          = OPEN — BLOCKS C_D_PASS ONLY; never the C-A S1 seal
```
