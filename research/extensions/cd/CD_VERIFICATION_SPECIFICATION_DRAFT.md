# C-D — IMPLEMENTATION VERIFICATION SPECIFICATION (**DRAFT — NOT SEALED, NOT IMPLEMENTED**)

```
STATUS                             = SPECIFICATION DRAFT WRITTEN. NOT SEALED. NOT IMPLEMENTED. NOT RUN.
REVISION                           = S1 bounded repair, 2026-09-14 — status block disambiguated (CB-4);
                                     FM-1 floor dependency removed; C-A first-scored-month cross-reference
                                     corrected (CB-1). SB-3 preserved exactly as an open C_D_PASS blocker.
                                     C-D was NOT redesigned.
C_D_IMPLEMENTATION_AUTHORIZED      = NO
C_D_CONTAINS_NEW_HISTORICAL_OUTCOME_ANALYSIS = NO
PROVIDES_INDEPENDENT_ALPHA_EVIDENCE          = NO
CAN_MOVE_research_status                     = NO
OWNER                              = Aaron
DRAFTED_BY                         = Claude Opus 5 (Main Agent), 2026-09-13
OWNER_DECISION_RECORD              = ../../../ops/OWNER_DECISION_RECORD_PHASE_B.md
PRIMARY_CONTRACT                   = ../ca/CA_PREREGISTRATION_DRAFT.md   (C-A)
BLOCKER_REGISTER                   = ../ca/CA_PREREGISTRATION_DRAFT.md §Y  (single authoritative register)
```

---

## §1 Role and boundary

**C-D is implementation verification and data-source reconciliation. Nothing else.**

```
WHAT C-D ESTABLISHES  =  that the reported canonical series is the specified rule
                         on the stated data, and that the stated data is not a
                         vendor artefact.
WHAT C-D DOES NOT ESTABLISH  =  any forward or out-of-sample performance; the economic
                         mechanism; that the historical Sharpe is not luck; anything
                         about live costs; anything about persistence; any upgrade of
                         `research_status`.
```

**C-D generates no new historical scientific metric.** CA-01 §6.1 item 7 and OD-11
— the one-off historical excess-return computation — are **deleted** and are not
reinstated by this specification. C-D computes **no** historical funding-adjusted
(FM-1) statistic, and **no** performance statistic presented as a research result.

Every number C-D emits is a **reconciliation quantity**, classified
`implementation_fact`. Where a headline metric appears at all (§7.4), it appears
**only** as a discrepancy against a value the canonical programme has already
published, inside the reconciliation artifact, never as a finding.

**If a C-D outcome later makes Aaron want a historical FM-1 computation**, it is
classified **in advance** as `POST_EXPOSURE · T0 · post_hoc_diagnostic · NOT
independent evidence`; it may occur **only after** the C-A seal has frozen both
estimands and their decision rules — the primary's `+0.30 / −0.20` materiality scale
and FM-1's sign-against-zero rule (C-A §D, §P.5; **FM-1 carries no `+0.30 / −0.20`
floors**); it is logged as a `REVEALED_TARGET_METRIC` row in scope
`HISTORICAL_CUMULATIVE`; and **it may never be used to set, revisit or reinterpret
any forward threshold.** It is not a design input, it is not required for S1, and
**the C-A seal must not wait for it.**

**C-D depends on no FM-1 threshold of any kind.** It computes no FM-1 statistic, and
nothing in §5–§10 references a materiality floor.

**Ordering.** `C_D_PASS` is required **before the first C-A reveal**, not before the
C-A seal. C-D runs on the frozen historical panel; the C-A pipeline accrues forward
months in parallel and is unaffected by C-D's schedule.

---

## §2 Independence requirements

```
ROLE      = independent implementer of the canonical rule from a written specification
WINDOW    = NEW_TOP_LEVEL_SESSION
MUST_NOT_BE = any session that has read `src/`, `config.py`, the repository's tests,
              any backtest report, or that wrote the specification in §3
```

- **Two distinct seats.** The **specification author** (who reads `src/`) and the
  **independent implementer** (who must not) are different sessions. A subagent is
  never independent of its spawner. The producing session is never the sole
  certifier of the same deliverable.
- **The implementer must not use `src/` as design authority.** It builds from the
  specification alone, in an **isolated workspace / package with no import path to
  `src/`**. Language and library choice are irrelevant; **author independence and
  source independence** are what the verification rests on.
- **Model diversity is review diversity, never evidence multiplication.** C-D
  consumes no independence budget on the research axis and adds no trial.

---

## §3 Step 1 — the executable specification, written from the code

An executable specification of the canonical rule, written from `src/`, `config.py`
and the repository's tests — **not from prose, and not from any README or study
summary**. It must be complete enough that a competent implementer who has never
seen `src/` reproduces the series.

Every convention a second implementer could plausibly choose differently must be
written down, including at minimum:

- month-end resample as the **last available close within the calendar month**,
  labelled at the calendar month-end;
- `M_t / M_{t−N} − 1` for `N ∈ {1, 3, 6, 12}`;
- `np.sign` semantics with **`sign(0) = 0`**;
- mean of the four signs with **all four required** (`MOMENTUM_MIN_PERIODS = 4`);
  the resulting grid `{−1, −½, 0, ½, 1}`;
- rolling 60-day std of **simple** daily returns, `ddof = 1`, `min_periods = 60`,
  annualised ×√252, sampled at month-end;
- `weight = clip(signal · 0.10 / vol, ±2)`; `vol ≤ 0` or NaN → NaN;
  **`signal == 0` → `0.0`, overriding a NaN volatility** (§8, Q-2);
- equal weight over assets with a **non-NaN** weight: `base_i = w_i / n_available`;
- base-book daily returns with held weights `reindex(ffill).shift(1)`;
- 60-day portfolio vol on the **unlevered** base book, `ddof = 1`;
- `L = min(0.10 / port_vol, 3 / gross_base)` with **NaN propagation from either
  input** (a missing vol estimate yields NaN leverage, never a cap-only value);
- `positions = weights.shift(1)`;
- `gross = Σ position · monthly simple return`;
- `turnover = Σ |Δposition|`, one-way, **including how the first position month is
  treated** (§8, Q-5);
- `cost = turnover × 2 / 1e4`; `net = gross − cost`;
- Sharpe `mean / std(ddof = 1) · √12`, `rf = 0`;
- the evaluation window restriction to months with **all 17 assets live**;
- terminal partial-month handling;
- the **exact fill semantics of every `pct_change` call** (§8, Q-1) and the runtime
  under which they hold.

**The specification is a deliverable in its own right**, and it is what the C-A
contract means by "the canonical rule as sealed". If C-D shows the specification is
incomplete or ambiguous, fixing it is part of C-D's output.

---

## §4 Step 2 — independent reimplementation

- Built from the §3 specification **alone**.
- In an **isolated package** with no import path to `src/`, and no access to the
  repository's own intermediate outputs.
- Run on the **canonical frozen input panel**: `data/close_prices_raw.csv`, SHA-256
  `3d2a7a56dbd92d4ff8138cfd894c87f5ac5ac088a11165db870673e0c05c3c31`, 1993-01-29 →
  2026-06-12. The panel hash is **recomputed from bytes** before any work; on
  mismatch, **STOP and report**.
- The implementer emits **every intermediate panel** in §5, not just the headline.

---

## §5 Intermediate reconciliation — exact, monthly, and not optional

**`Headline-Sharpe agreement alone is NOT acceptance.`** Two implementations can
agree on a Sharpe while disagreeing on signals, sizing and turnover in offsetting
ways. Reconciliation is **month by month, panel by panel**, at the levels below.

| # | Level | Comparison | Tolerance |
|---|---|---|---|
| 1 | **Input identity** | panel SHA-256, byte size, shape, first/last date, per-ticker row counts and first/last valid date | **exact** |
| 2 | **Month-end prices** | the month-end price panel (17 tickers × all months) | **exact** (same floats from the same bytes) |
| 3 | **1/3/6/12-month returns** | four momentum panels | `1e-12` relative |
| 4 | **Horizon signs** | four sign panels on `{−1, 0, +1}` | **exact equality**, including every `sign(0) = 0` cell |
| 5 | **Combined signal** | the composite panel on the `{−1, −½, 0, ½, 1}` grid | **exact equality**; NaN pattern must match exactly |
| 6 | **60-day asset volatility** | the month-end annualised vol panel | `1e-10` relative |
| 7 | **Asset target positions** | the sized weight panel before capping | `1e-10` relative |
| 8 | **Caps** | the count and identity of every `|weight| = 2` cap-binding cell | **exact** |
| 9 | **Live-asset aggregation** | `n_available` per month, and the base-weight panel | `n_available` **exact**; base weights `1e-10` relative |
| 10 | **Portfolio volatility** | the month-end realised portfolio vol series | `1e-10` relative |
| 11 | **Leverage** | `L`, `L_raw`, and the NaN pattern | `1e-10` relative; NaN pattern **exact** |
| 12 | **Gross cap** | the identity of every month where the cap binds; final `gross` and `net` per month | cap months **exact**; series `1e-10` relative |
| 13 | **Turnover** | per-month one-way turnover; annualised turnover (the published ≈ 17.6× must reproduce) | `1e-10` relative |
| 14 | **Transaction costs** | per-month cost | `1e-10` relative |
| 15 | **Monthly net return stream** | per-month gross, cost and net | **`1e-8` absolute** |
| — | **Headline metrics** | net Sharpe, annualised return, annualised vol, max drawdown, on the frozen panel | `1e-6` |
| — | **Truncation invariance** | re-verified by the **independent** engine: truncating the panel at any date leaves every earlier value unchanged | **exact**, no look-ahead |

**Every discrepancy above tolerance is traced to a documented cause within the
bounded C-D effort, or recorded as `UNEXPLAINED` with its magnitude.
Sub-tolerance discrepancies are recorded, not waived.**

---

## §6 Truncation invariance and causality

The independent engine re-verifies, on its own code:

1. **Truncation invariance** — for a set of declared cut dates, every panel value at
   or before the cut is bit-identical to the untruncated run.
2. **Monthly timing** — the position applied to month `t` is a function only of data
   observed on or before the last trading day of month `t−1`.
3. **Backward-only volatility** — both the asset and the portfolio volatility
   estimates at month-end `M` use only returns up to and including `M`, and the
   portfolio vol uses the **unlevered** base book (no circularity with the leverage
   it feeds).

**A causality (look-ahead) defect found here is `C_D_FAIL` branch (a)** and is the
single most consequential thing C-D can find.

---

## §7 Second-source reconciliation — data integrity, not alpha

```
PURPOSE  =  DATA INTEGRITY. NOT independent alpha evidence, NOT a second test,
            NOT a replication, and NOT a new historical finding.
VENDOR   =  NOT PRESCRIBED. No particular vendor is required and none is established today.
            See blocker SB-3 in the C-A register.
```

### §7.1 The threat this closes

The canonical panel is a **single vendor's adjusted closes** (yfinance). Adjusted
series are revised by construction, and adjustment-timing differences can flip the
**sign of a one-month return** — particularly on SHY, LQD and TLT, where a
distribution is large relative to a month's price move, and a flipped monthly sign
can flip a composite horizon. That is the specific open threat C-D exists to close.

### §7.2 Comparison levels

| Level | What is compared |
|---|---|
| **Corporate actions** | splits and reverse splits present in each vendor's series, on a declared event list; verified on at least three known events — USO's 2020 reverse split, a UNG reverse split, a large TLT distribution |
| **Adjusted-close / total-return treatment** | whether each vendor reinvests distributions on the ex-date or supplies price-only series; the two vendors' adjusted series must give the **same ex-date returns within tolerance** on the declared events |
| **Sign of monthly returns** | per ticker-month sign agreement, and the **count of ticker-months where the composite signal differs** — the level at which a vendor difference becomes a decision difference |
| **Material price discrepancies** | per-ticker daily-return correlation and max absolute discrepancy versus the frozen panel |
| **Distribution timing** | ex-date versus pay-date treatment, and its size at monthly frequency |
| **Missing observations** | ticker-days present in one source and absent from the other; stale runs present in one and not the other |
| **Derived agreement** | position tracking error between the two panels; monthly net return correlation and max `|Δ|` |

### §7.3 If no reproducible second source is available

**Recorded as a concrete feasibility blocker, not worked around.** This task
registers **SB-3** in the C-A blocker register and does not attempt to resolve it:
**no account is registered, no data is purchased, and no access control is
bypassed.** Candidate public sources exist but none is established in this
repository, and the only prior workspace vendor survey concerned futures term
structure, not ETFs.

**Declared fallback, so the programme is not held hostage.** If the Owner's bounded
probe finds no reachable reproducible source, C-D proceeds on §3–§6 and §8 and
records:

```
SECOND_SOURCE_RECONCILIATION = NOT_PERFORMED — NO REPRODUCIBLE SECOND SOURCE AVAILABLE
```

which **caps the outcome at `C_D_HOLD`** (§10) and leaves §J of the C-A contract's
late-corporate-action rule without its second-source leg — an Owner matter at that
point, not a builder one.

### §7.4 What may be emitted

Reconciliation quantities only: correlations, max `|Δ|`, sign-agreement counts,
composite-difference counts, tracking error, and the **event-level adjustment
checks**. Where a headline metric is used at all, it is used as a **tolerance check
against the already-published canonical value** (`|Δ Sharpe| ≤ 0.05`), reported
inside the reconciliation artifact, tagged `implementation_fact · T0 re-exposure of
already-revealed outcomes on different bytes · normalised exposure unchanged`, and
**never** written as a research finding or into any strategy card.

---

## §8 Intended strategy rule vs accidental implementation quirk

**The governing instruction: do not blindly copy a bug into the independent
specification merely to make the outputs match.** Each item below is classified, and
where the intended behaviour is **not** established by authority it is escalated
rather than assumed.

**The classification rule.** The canonical claim object is *the sealed `src/` as it
behaves under the pinned runtime* — so a behaviour the code exhibits **deterministically
and reproducibly** is part of the object and is written into the specification with a
dedicated regression test, **disclosed as a convention rather than silently
inherited**. A behaviour that is **environment-dependent**, **non-reproducible**, or
**causally defective** is a defect and is escalated.

| # | Item | Finding | Classification and disposition |
|---|---|---|---|
| **Q-1** | **`pct_change()` fill semantics** — called without an explicit `fill_method` at `src/sizing.py::daily_returns`, `src/portfolio.py::base_portfolio_daily_returns`, `src/performance.py::monthly_asset_returns` | **Verified mechanically in this session on synthetic data (pandas 2.3.3):** the default is `fill_method='pad'`, so across a missing observation the series yields `0.0` then a clean return, where `fill_method=None` yields two NaNs. The default is **deprecated and changes in pandas 3.0.** | **ENVIRONMENT-DEPENDENT — a specification defect, not a rule.** The specification must state the fill behaviour **explicitly**; the forward engine must pass it explicitly; the seal must pin the runtime. Behaviour under the pinned runtime is preserved exactly. C-D reports the count of affected ticker-days on the frozen panel. |
| **Q-2** | **Flat signal with missing volatility** — `target_weights` applies `where(signal != 0, 0.0)` **after** the vol-derived NaN, so an asset with `signal == 0` and no vol estimate receives weight `0.0`, is **non-NaN**, and therefore **counts in `n_available`** and dilutes the book | Deterministic and reproducible; partially documented by the docstrings ("a flat signal is a deliberate 0 position regardless of vol"; "NaN weights are treated as not in the book"), but the **combination** is documented nowhere | **INTENDED RULE by the byte-identical-engine rule.** Written into the specification explicitly, with a dedicated test; reconciled at level 9. **Disclosed** in the C-A contract §B.1 so it is never later discovered and treated as a bug. |
| **Q-3** | **Mixed calendars** — 30 tickers with differing inception dates on one daily index; month-end labels are calendar month-ends while data are trading days; `base_weights.reindex(daily, method='ffill').shift(1)` bridges the two | Deterministic; the canonical evaluation window already restricts to months with all 17 live | **INTENDED RULE.** Specified explicitly: the daily index, the ffill-then-shift convention, the calendar-month-end labelling, and the all-17-live window restriction. Reconciled at levels 2, 9 and 10. |
| **Q-4** | **Partial terminal month** — the June-2026 monthly row is labelled `2026-06-30` but built from data ending `2026-06-12` (`LOCKBOX_PROCEDURE.md` §2.1) | A complete label over an incomplete period | **NOT A RULE — a data-boundary artefact.** C-D reports results **both** with the terminal row truncated and included, and states which the canonical published figures used. C-A never scores a partial month (§H). |
| **Q-5** | **First-position-month turnover** — `positions.diff()` yields NaN where the prior row is NaN, so turnover and therefore `net` can be NaN in the first month a position exists, while `gross` is finite and the row survives `dropna(subset=['gross'])` | Deterministic; immaterial inside the all-17-live window, but it fixes whether establishing the initial book is charged | **UNDER-SPECIFIED, resolved by the engine rule.** The specification states the behaviour explicitly and C-D reconciles the first live month exactly. Forward this cannot arise: the prior-position term for C-A's first scored month is supplied by the pre-start held position, which is used for the turnover term and nothing else (C-A §F.1 step 2), so turnover is well defined without scoring any pre-start decision. |
| **Q-6** | **Frozen-panel overwrite path** — a fetch/refresh code path capable of writing over `data/close_prices_raw.csv` | An engineering hazard against `LOCKBOX_PROCEDURE.md` §3.1 | **NOT A SCIENTIFIC QUESTION — a build-stage guard.** C-D verifies the hash before and after its own run. The forward pipeline must carry a write guard and a regression test before `PIPELINE_GO_LIVE` (C-A §I.2, §Z item 6). |

**Escalation rule for anything not in this table.** If the independent implementer
finds a behaviour whose **intended** semantics are not established by the code's
determinism, the docstrings, the tests or a sealed artifact, it is **recorded as an
open specification question and escalated** — it is never resolved by choosing
whichever reading makes the two engines agree. Making the outputs match is not
evidence; it is the thing being tested.

---

## §9 Discrepancy policy

1. Every discrepancy above tolerance is traced to a documented cause, or recorded
   `UNEXPLAINED` with its magnitude and the panels it appears in.
2. Sub-tolerance discrepancies are **recorded**, never waived.
3. A discrepancy is **never** resolved by adjusting the independent implementation
   toward `src/` after seeing the difference; it is resolved by finding which
   specification sentence was wrong or missing, and fixing **the specification**.
4. A discrepancy whose cause is a documented **vendor adjustment difference** is
   classified as such and does not count as an implementation discrepancy.

---

## §10 Outcomes

```
C_D_PASS
  - the independent engine reproduces EVERY intermediate panel in §5 within tolerance
    on the frozen panel;
  - no causality defect (§6);
  - the consequential intermediate states — signal grid, n_available, cap-binding
    months, leverage NaN pattern, turnover — reconcile exactly where §5 says exactly;
  - second-source reconciliation performed, with net return stream correlation
    >= 0.995 against the frozen-panel stream and every residual discrepancy explained
    by documented adjustment differences within the sealed tolerance;
  - ZERO `UNEXPLAINED` discrepancies above tolerance;
  - the §3 specification is complete: no open specification question remains.
  => a new Finding, evidence_type = `implementation_fact`, claim_status `confirmed`
     PERMITTED, claim = "the reported canonical series is the specified rule on the
     stated data". Strategy `research_status` UNCHANGED.

C_D_HOLD
  - frozen-panel reproduction achieved, but one or more of:
      * second-source discrepancies above tolerance that are traceable in principle
        and not yet traced;
      * SECOND_SOURCE_RECONCILIATION = NOT_PERFORMED (§7.3);
      * the specification was found ambiguous and both engines resolved it identically
        by coincidence rather than by the written text.
  - ONE bounded repair (vNext §6). NO forward C-A reveal until resolved.
  - The C-A pipeline continues accruing months; blindness is unaffected.

C_D_FAIL
  (a) a look-ahead / causality defect in `src/`; or
  (b) the independent engine cannot reproduce the canonical series from the
      specification, and the difference traces to `src/` behaviour not derivable from
      the stated rule — i.e. the canonical strategy is UNDER-SPECIFIED as a claim
      object; or
  (c) the second source materially disagrees, with the discrepancy traced to defects
      in the canonical panel rather than to documented adjustment differences.
```

**Consequences of each `C_D_FAIL` branch.**

- **(a)** Historical evidence is invalidated until reconciled. The forward engine is
  corrected; the forward claim becomes a test of the **corrected** rule; forward
  positions are recomputed from retained vintages where that is possible,
  reproducibly and without outcome information (C-A §U.1). The historical card's
  fate is an **Owner decision**.
- **(b)** The specification is amended to describe `src/` exactly — the canonical
  strategy is what `src/` does — the forward engine is unchanged, and the historical
  claim's object is written down for the first time.
- **(c)** The historical finding acquires a **vendor-dependence limitation**; the
  forward programme continues on a two-source-verified basis.

**A C-D failure affects reliance on the historical / canonical implementation
evidence. It does NOT automatically falsify the economic TSMOM hypothesis**, and it
does not by itself invalidate accrued forward months.

---

## §11 What C-D does not establish — restated because it is the most likely misreading

`confirmed implementation_fact` **never** implies confirmed strategy performance. A
`C_D_PASS` says the published numbers are the arithmetic they claim to be, on the
bytes they claim to be on. It says **nothing** about whether the strategy has an
edge, whether that edge persists, whether the historical result was luck, or whether
any of it survives real costs. It re-exposes nothing new and consumes no
independence; what it buys is that the forward evidence is **about the strategy**
rather than about a possible artefact.

---

## §12 Exposure and recording

| Record | Requirement |
|---|---|
| `ops/EXPOSURE_LEDGER.md` | C-D operates on the **already-revealed** historical panel; its work is a **T0 re-exposure of already-revealed outcomes**, so the normalised research-axis exposure for scope `HISTORICAL_CUMULATIVE` is **unchanged** (it is already `TARGET_METRIC`). Rows are appended for the second-source panel acquisition and for §7.4, using **existing tokens only** — no new classification or scope is created, and the file's single-table shape is preserved. |
| `ops/REVIEWER_EXPOSURE_LOG.md` | A seat row for the specification author and for the independent implementer, recording that the implementer's `MUST_NOT_BE` constraint held. **Seat exposure never enters the research ledger and never licenses a stronger evidence context.** |
| `research/extensions/TRIAL_LEDGER.md` | C-D contributes **no** `VARIANT_ATTEMPT` and **no** `N_trials`: it constructs no new strategy configuration and evaluates no new selection opportunity. |
| C-D artifact | One immutable JSON/Markdown reconciliation artifact pinned by SHA-256, in the X01 / Value evidence-artifact style, recording every level in §5 and §7 with its tolerance, its result, and every `UNEXPLAINED` residual. |

---

## §13 Preconditions and status

None has been performed. C-D is **not implemented** and **not authorized**.

1. **Owner authorization to implement C-D** — a decision distinct from the C-A seal.
2. **SB-3 resolved** (C-A §Y) — the bounded, zero-cost, read-only second-source
   feasibility probe, or the §7.3 fallback accepted.
3. **Two seats identified** under §2, with the `MUST_NOT_BE` constraint recorded
   before either starts.
4. **Frozen panel hash recomputed from bytes** before any work.
5. **Runtime pinned** and recorded (Python / pandas / numpy), because Q-1 makes the
   reconciliation runtime-dependent.

**Four distinct things, never conflated.** A written specification is not a sealed
one, a sealed one is not an implementation, and none of them is the executable rule
specification that C-D's own §3 produces **during** execution.

```
C_D_SPEC_DRAFT_CREATED                       = YES   (this document)
C_D_VERIFICATION_SPEC_DRAFT_WRITTEN          = YES   (this document)
C_D_SPEC_SEALED                              = NO
C_D_EXECUTABLE_RULE_SPECIFICATION_WRITTEN    = NO    (the §3 artifact, produced during C-D execution)
INDEPENDENT_ENGINE_BUILT                     = NO
C_D_IMPLEMENTED                              = NO
SECOND_SOURCE_ESTABLISHED                    = NO    (blocker SB-3, OPEN — blocks C_D_PASS only)
NEW_HISTORICAL_SCIENTIFIC_OUTCOME_ANALYSIS   = NONE
TARGET_PERFORMANCE_COMPUTED                  = NO
```
