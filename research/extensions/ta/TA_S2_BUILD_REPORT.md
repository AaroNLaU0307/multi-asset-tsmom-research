# CTA-EDGE-01-TA — S2 BUILD + SYNTHETIC VALIDATION REPORT

```
LINEAGE                 = CTA-EDGE-01-TA
STAGE                   = S2 BUILD + SYNTHETIC VALIDATION ONLY
S2_BUILD_STATUS         = PASS
BRANCH                  = cta-edge/ta-auction-s1
PRE_S2_HEAD             = 881e684b4ddca73f117ea78af14843dabf3c59c9  (the accepted S1 seal)
SEALED_PREREG_SHA256    = 3b495fcb220a86b9c4226e308e4814bdfdd871d1c69ce352e99b78977436d35b
S1_SEAL_VERIFIED        = YES  (12 of 12 sealed hashes reproduced exactly)
SCIENTIFIC_CHOICES_MADE_AFTER_S1 = NONE
REAL_ETF_DATA_USED_FOR_OUTCOMES  = NO
RUN_AUTHORIZATION_CREATED        = NO
OUTCOME_EXPOSURE_LEDGER_WRITTEN  = NO
```

---

## 1. The headline finding — the sealed pre-check has FIRED

The sealed contract §G.3 required S2 to report the macro covariate cross-tabulation
**before any `AC` is computed**, because the size of the diagnostic's reference group
could not be established at S1. That pre-check has now run, on the real 213 primary
events, using **counts only and no return of any kind**:

```
DESIGN_MATRIX_RANK      = 5   of 5 columns        -> NOT rank deficient
REFERENCE_GROUP_N       = 7   (events with all four signed covariates = 0)
MIN_REFERENCE_GROUP     = 20  (sealed)
MACRO_SPEC_EVALUABLE    = NO
NOT_EVALUABLE_REASONS   = REFERENCE_GROUP_TOO_SMALL (7 < 20)
```

Under the sealed §G.3 rule, `NOT_EVALUABLE` makes the macro/QRA damage diagnostic
**TRIGGER**. Under the sealed §I.2 order, a triggered damage diagnostic converts a
would-be Class D into **Class I**. Therefore, on the sealed design as it stands:

> **CLASS D IS NOT REACHABLE FOR THIS LINEAGE.** The governed historical run can
> return Class A, Class B, Class C or Class I, and nothing else.

**The specification has NOT been redesigned and the seal has NOT been amended**, exactly
as the S2 task requires. The S1 contract disclosed this risk in terms, required this
pre-check, and the pre-check has resolved it — while the lineage is still entirely
outcome-blind. This is the control working, not the control failing.

The per-covariate table shows why, and the reason is substantive rather than technical:

| covariate | POST `+1` | neither `0` | PRE `-1` |
|---|---:|---:|---:|
| **CPI** | 125 | 57 | 31 |
| **NFP** | 8 | 27 | **178** |
| **FOMC** | 52 | 145 | 16 |
| **QRA** | 0 | 207 | 6 |

CPI lands after the mid-month auction in 125 of 213 windows; payrolls precede it in 178
of 213. **At daily close-to-close frequency the refunding week is almost never
macro-clean** — which is precisely the reason the intraday literature had to go intraday
to identify the effect at all. Only **7** of 213 windows are free of all four.

The QRA column reproduces the S1-sealed tabulation exactly (6 at `−1`, 207 at `0`),
which is an independent cross-check that the covariate machinery is wired correctly.

Full table: [`TA_MACRO_CROSSTAB.md`](TA_MACRO_CROSSTAB.md).
Per-event values: [`TA_MACRO_COVARIATES.csv`](TA_MACRO_COVARIATES.csv).

**This is a controller decision, not a builder decision.** Nothing in this report
changes the sealed design. Whether to run the study knowing Class D is unreachable,
to park the lineage, or to open a new lineage with a design capable of the
identification this one lacks, is Aaron's.

---

## 2. Seal verification

Every sealed artifact reproduced its pinned sha256 before any build work began:

| artifact | result |
|---|---|
| `TA_PREREGISTRATION.md` | **MATCH** `3b495fcb…36d35b` |
| `TA_S0_FRAME.md` · `TA_S0_REPAIR_RECORD.md` · `TA_DATA_MANIFEST.md` | MATCH |
| `TA_EXPOSURE_DISCLOSURE.md` · `TA_SEAL_MANIFEST.md` | MATCH |
| `TA_EVENT_CALENDAR.csv` | **MATCH** `b27be5b1…7cb6` |
| `ta_auction_fetch.py` · `ta_prereg_validate.py` | MATCH |
| `ops/OWNER_DECISION_RECORD_CTA_EDGE_01_TA.md` | MATCH |
| `data/ta/ta_auctions_raw.json` · `data/close_prices_raw.csv` | MATCH |

Branch `cta-edge/ta-auction-s1`, worktree clean at start, `main` an ancestor of HEAD,
and the accepted S1 commit `881e684b` an ancestor of HEAD. `ta_prereg_validate.py`
re-run: **122 / 122 PASS, exit 0**.

---

## 3. Components built

| | component | module |
|---|---|---|
| A | event-calendar loading / validation | `ta_calendar.py` |
| B | trading-grid / window construction | `ta_calendar.py` |
| C | PRE leg | `ta_engine.pre_return` |
| D | POST leg | `ta_engine.post_return` |
| E | combined AC | `ta_engine.ac_gross_bps` / `ac_net_bps` |
| F | transaction-cost accounting | `ta_engine.event_cost_bps`, derived from the path |
| G | calendarised monthly P&L | `ta_engine.monthly_series` |
| H | mean NET AC | `ta_engine.mean_net_ac` |
| I | calendarised Sharpe | `ta_engine.calendarised_sharpe` |
| J | calendar-year block bootstrap | `ta_inference.year_block_bootstrap` |
| K | leave-one-year-out fragility | `ta_inference.leave_one_year_out` |
| L | IEF secondary | `ta_diagnostics.SecondaryResult` |
| M | SHY maturity gradient | `ta_diagnostics.GradientResult` |
| N | SPY damage placebo | `ta_diagnostics.spy_damage` |
| O | macro / QRA damage specification | `ta_covariates.py` + `ta_diagnostics.macro_damage` |
| P | A/B/C/D/I classification engine | `ta_classify.py` |
| Q | report writer and schema | `ta_report.py` |
| R | hard production-run guard | `ta_authorization.py` |

Supporting: `ta_contract.py` (sealed constants), `ta_prices.py` (the firewall),
`ta_oracle.py` (the independent oracle), `ta_macro_calendar.py` (calendar metadata),
`ta_s2_build.py` (the S2 driver), `ta_tests.py` (the suite).

**Not built, deliberately:** no portfolio integration, no TSMOM-combination logic, no
futures implementation, no optimiser, no parameter search.

---

## 4. The position path, as implemented

```
close(GRID[i-6])  flat  -> SHORT 1 unit
close(GRID[i-1])  SHORT -> flat
auction-day bar   FLAT                 exposure across GRID[i-1] -> GRID[i] is ZERO
close(GRID[i])    flat  -> LONG 1 unit
close(GRID[i+5])  LONG  -> flat

one-way units = 1 + 1 + 1 + 1 = 4      COST_BPS = 4 x 2 = 8.0 per event
```

There is no short-to-long flip anywhere in the implementation, and
`exposure_on_auction_day_bar()` returns the held position across the excluded bar so a
test can assert it directly rather than trusting prose.

---

## 5. Validation

### 5.1 Targeted suite

```
python -m pytest research/extensions/ta/ta_tests.py -q      ->  48 passed
python research/extensions/ta/ta_prereg_validate.py         ->  122/122 PASS, exit 0
python -m pytest -q  (whole repository)                     ->  98 passed, 3 failed
```

The three repository failures are **pre-existing and unrelated** — see §7.

### 5.2 The required behavioural tests

| # | test | result | how it is made non-vacuous |
|---|---|---|---|
| 1 | positive auction cycle | **PASS** | fixture falls in PRE, rises in POST; `AC_GROSS = +70 bps`, matched by the oracle |
| 2 | negative auction cycle | **PASS** | rises in PRE, falls in POST; `AC_GROSS = −60 bps` |
| 3 | auction-day isolation | **PASS** | a **+500 bps** move on the excluded bar and zero elsewhere must give `AC = 0`. The fixture is proved **discriminating**: a deliberately reintroduced short-to-long flip returns **+500 bps** on exactly this data, a separation of >100 bps |
| 4 | cost accounting | **PASS** | gross `+20` → net **`+12`**, asserted against `+16` and `+8` explicitly |
| 5 | zero months | **PASS** | sparse events; zero months counted and asserted equal to grid−events; the sealed grid's **31** zero months checked separately |
| 6 | calendarised Sharpe, not event-frequency | **PASS** | the same monthly series reached from **12** events and from **7** events gives an identical Sharpe |
| 7 | year dominance → LOYO | **PASS** | all the effect in 2008 ⇒ LOYO fails on 2008; the broad-based control case passes |
| 8 | SPY damage | **PASS** | would-be D + SPY lower bound ≥ +16 bps ⇒ **Class I**; a 4 bps placebo does not fire; a large negative placebo does not fire |
| 9 | macro damage | **PASS** | would-be D + `b0` below +16 bps ⇒ **Class I**; the OLS recovers a planted `b0 = 25.0` and `βCPI = 11.0` exactly |
| 10 | IEF cannot rescue | **PASS** | a spectacular IEF result leaves a Class-B and a Class-C verdict unchanged; `ta_classify.py` is proved to contain no `IEF` reference |
| 11 | SHY power = zero | **PASS** | SHY swung from −900 to +900 bps changes nothing; `ta_classify.py` contains no `SHY` reference |
| 12 | diagnostics cannot promote | **PASS** | exhaustive sweep over bounds × flags: **0** illegal upgrades to D |
| 13 | materiality boundaries | **PASS** | `L_N` exactly `+8.0` → D; `15.999` gross → C; `L_S` exactly `0.30` → D, `0.2999` → C; `U_N` exactly `+8.0` is **not** B; `U_AC` exactly `0` **is** A |
| 14 | Class-I reachability | **PASS** | all four paths independently: LOYO, SPY, macro, and the §I.3 executed-calendar contamination; plus the structural `NOT_EVALUABLE` path reached from the calendar alone |

### 5.3 The independent synthetic oracle

```
INDEPENDENT_SYNTHETIC_ORACLE = PASS
```

`ta_oracle.py` imports **nothing** from the production engine — a test asserts that
mechanically — and carries its own transcription of the sealed constants, with a test
that fails if the two ever drift apart. It reaches every expected value by a different
route: a fixture is **defined** by its per-day log returns, the production engine
recovers `AC` from the **log of endpoint prices**, and the oracle **sums the declared
daily returns**. A mis-indexed window endpoint therefore disagrees immediately.

The oracle independently checks `AC_GROSS`, `AC_NET`, the auction-day bar, the monthly
series, the mean, the calendarised Sharpe, and the whole A/B/C/D/I classification over
the full sweep. This exists because this programme has twice been bitten by an oracle
that reproduced the engine's own misreading.

### 5.4 Cross-boundary and state continuity

```
CROSS_BOUNDARY_TESTS = PASS
```

Weekend skipping · a declared holiday removed from the grid · December and January
events across a year boundary · the month grid spanning year transitions · partial
years (2006 contributes 11 months, 2026 contributes 5, and the 21 years sum to exactly
244) · an event month outside the grid rejected loudly · events at the beginning and end
of the sample excluded for incomplete windows · a complete window included · an
off-grid anchor excluded · the overlap threshold exact at 11 grid days and clear at 12.

**The sealed event calendar reproduces without reading any ETF outcome:**

```
EXPECTED_PRIMARY_WINDOWS    = 213
IMPLEMENTED_PRIMARY_WINDOWS = 213      first 2006-02-09  last 2026-05-13
                              21 calendar years · 213 unique ISO weeks
                              max 1 event per week AND per calendar month
                              0 overlapping windows · 73 new / 140 reopenings
                              month grid 244 = 213 event months + 31 zero months
SECONDARY                   = 258 windows, 25 years, exactly 1 overlapping pair
                              (2019-06-12 / 2019-06-21), both retained
```

The "max one event per calendar month" property is **checked against the data**, not
assumed, and the check is proved non-vacuous by feeding it a duplicated event and
requiring it to raise.

### 5.5 Firewall and the production-run guard

```
HISTORICAL_RUN_WITHOUT_AUTHORIZATION = BLOCKED
```

The guard reuses the repository's existing mechanism — the append-only Owner ledger
`ops/EXECUTION_AUTHORIZATIONS.md`, read from **committed git state**, with the same
fenced-`json` record shape and lifecycle events as `x01_authorization.py` and
`vrp_reveal.py`. No weaker parallel flag was invented. Only the lineage scope differs
(`TA-AUTH` ids). At S2 the status is:

```
active_execution_authorizations = 0      real_run_authorized = FALSE
```

Prices reach the engine only through a `PriceSource`, by **dependency injection, not
monkey-patching**:

- `SyntheticPriceSource` holds fixture series in memory. It has no path and no file
  access, so no test can fall through to the real panel if a patch is forgotten.
- `RealPanelPriceSource.__init__` calls the guard **before opening anything**. A test
  instruments `builtins.open`, attempts an unauthorised real construction, and asserts
  both that it raises **and that the panel was never opened**.

---

## 6. Artifacts

| artifact | sha256 |
|---|---|
| `TA_MACRO_CALENDAR.csv` (755 rows) | `8f10675033267136cb2622bf80f2f6da8ca922c0e074fae4c09128a49b1c4789` |
| `TA_MACRO_COVARIATES.csv` (213 rows) | `92cb21b269da66ff69f9e93540ffb2cba193d80496bf2f09887707a1aacfda04` |
| `TA_MACRO_CROSSTAB.md` | `0f7c98cb6f35ab1015665c7b02b4906942e300cb286918c92fbf7dd6adabea16` |
| `s2/TA_S2_SYNTHETIC_RESULT.json` | `91ffa6ee4ace32977bbbb7654b201a5b2b885821083c604a06f2c294318b0ff1` |
| raw macro index `data/ta/ta_macro_raw_index.json` (git-ignored, 39 pages) | `888a7374d6091d07c13a63fb1f3fc7722915c30e15bab17277470e639c86cf55` |

The synthetic example result artifact is stamped **`SYNTHETIC_ONLY = YES`**, carries
`run_authorization_id = null`, and every number in it is a placeholder; the writer
**refuses** to stamp `SYNTHETIC_ONLY = NO` without a run authorization id, and refuses
to emit a Class-I artifact that lacks the mandatory
`IDENTIFICATION_INSUFFICIENT_FOR_THE_CLAIM` qualifier. Both refusals are tested.

The schema carries every required field: seal hash · run authorization id · data hashes ·
event-calendar hash · macro-calendar hashes · primary event count · mean `AC_GROSS` ·
mean `AC_NET` · the 95 % interval for mean `AC_NET` · monthly Sharpe · the Sharpe
interval · LOYO results · IEF secondary · SHY diagnostic · SPY placebo · macro/QRA `b0` ·
diagnostic triggers · final class · evidence ceiling · the forbidden-causal reminder.

---

## 7. Pre-existing unrelated failures — reported, NOT fixed

```
tests/test_xsmom_universes.py::test_decomposition_reconstructs_realized_profit   FAILED
tests/test_xsmom_universes.py::test_dispersion_localises_to_term3               FAILED
tests/test_xsmom_universes.py::test_leadlag_shows_up_in_term2                   FAILED
```

These are XSMOM tests with a pandas-version cause. **Proved pre-existing**: a clean
detached worktree at the accepted S1 commit `881e684b`, containing none of this task's
work, reproduces exactly the same three failures. Nothing in this build touches `src/`,
`xsmom_universes.py` or anything they import. They were not "fixed" to make the suite
green, as the S2 task requires.

---

## 8. What this build did NOT do

No real TLT, IEF, SPY or SHY `AC`. No real mean, interval, Sharpe, bootstrap or LOYO
outcome. No backtest, no optimiser, no parameter search, no plot of real event returns,
no "quick sanity check". No run authorization, no outcome-exposure ledger row, no S3
result artifact, no verdict. C-A was not accessed. Canonical TSMOM was not modified.
`PROJECT_STATE.md` was not told that the study ran.

```
NEXT = AARON / CHATGPT ACCEPTANCE -> S3 GOVERNED HISTORICAL RUN AUTHORIZATION
```
