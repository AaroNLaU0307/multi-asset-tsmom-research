# CTA-EDGE-04-MMV — S2 BUILD RECORD

```
LINEAGE        = CTA-EDGE-04-MMV
STAGE          = S2 BUILD — SYNTHETIC VALIDATION ONLY
S2_STATUS      = PASS
DATE           = 2026-09-17
BRANCH         = cta-edge/macro-momentum-vintage-s2
PRE_S2_HEAD    = cdb01fdc903e97671c3ef50fde6875628ca39ac8
```

```
SEAL_ID              = CTA-EDGE-04-MMV-SEAL-01
SEAL_SHA256          = 75016e778ad58e8fe16e4833cf91c19eb52448b4d42138ab265460f371e8c0d5   VERIFIED
PREREG_SHA256        = 4bad9f0bcdb7e4991ab920d12e24a60f4d237205e5a43af693a8dadadb56b225   VERIFIED
SEALED_ARTIFACTS     = UNMODIFIED on this branch (asserted by test, not by claim)
```

S2 implements the sealed contract and **makes no scientific choice**. Every
constant in the engine traces to a numbered contract clause. Nothing was
tuned, relaxed, defaulted or repaired.

---

## §1 Validation results

| suite | result | command |
|---|---|---|
| S2 synthetic validator | **151 / 151 PASS** | `python research/extensions/mmv/mmv_s2_validate.py` |
| S2 data-layer parser check | **32 / 32 PASS** | `python research/extensions/mmv/mmv_s2_parser_check.py` |
| S1 pre-seal check, against the sealed commit | **38 / 38 PASS** | see §6 |

Exit code is 0 only when every test passes. No check depends on markdown line
wrapping, document formatting or prose — the two S1 checks that did were
rewritten before the seal, and none was reintroduced here.

---

## §2 Implemented modules

All under `research/extensions/mmv/engine/`.

| module | contract clause | what it implements |
|---|---|---|
| `pit.py` | B.1, C.1 | latest-known-as-of vintage resolver, same-day rule, first-release chain |
| `policy.py` | B.1, B.2, C.2, D.3 | administered-policy resolver on **announcement** authority; DFEDTAR → range splice |
| `legs.py` | D.1, D.2, D.3 | growth, inflation and policy primitive legs |
| `votes.py` | E.1, E.2, E.3 | frozen 15-instrument coefficient table, raw direction, domain enforcement |
| `gate05.py` | I.2 | pooled exact sign agreement, kill at ≥ 80.0 % inclusive |
| `concordance.py` | B, L.1 | first-release descriptive diagnostic — no threshold, no verdict |
| `risk.py` | F, G | integration with the canonical wrapper; the 15-vs-17 dilution guard |
| `start.py` | H | structural start rule with per-condition exclusion reasons |

```
PIT_RESOLVER_IMPLEMENTED             = YES
POLICY_RESOLVER_IMPLEMENTED          = YES
GROWTH_ENGINE_IMPLEMENTED            = YES
INFLATION_ENGINE_IMPLEMENTED         = YES
POLICY_ENGINE_IMPLEMENTED            = YES
ASSET_VOTE_ENGINE_IMPLEMENTED        = YES
FIRST_RELEASE_DIAGNOSTIC_IMPLEMENTED = YES
GATE05_ENGINE_IMPLEMENTED            = YES
RISK_WRAPPER_INTEGRATION_IMPLEMENTED = YES
STRUCTURAL_START_ENGINE_IMPLEMENTED  = YES
```

### 2.1 Three places the contract is enforced structurally, not by test

A test can be deleted. These cannot be bypassed without deleting the type that
forbids the bypass, which shows up in review as a deliberate act.

1. **`realtime_start` cannot reach a policy decision.** No function or
   constructor in `policy.py` accepts a vintage, realtime or catalog parameter.
   `spliced_target` takes `(effective_date, value)` maps only. The S1 audit
   finding is therefore not merely tested against — it is unexpressible.
   `t_realtime_start_is_structurally_absent_from_the_policy_api` asserts this
   by reflecting over every signature in the module.
2. **VNQ/RWX cannot become a signal.** `votes.raw_direction` raises
   `NotInDomain` for them rather than returning `0` or `UNDEFINED`. A sentinel
   would be silently consumable; an exception is not.
3. **The coefficient table cannot be altered.** It is a `MappingProxyType`
   module constant with no constructor argument, config key or override hook.

### 2.2 Exact arithmetic, because the contract forbids thresholds

Every macro value is parsed from its decimal string into `Fraction` and never
into `float`. Every sign, every 12-month change, every `pi12` ratio and the
Gate 0.5 threshold comparison are exact rational arithmetic.

This is a contract requirement rather than a preference: section D forbids
thresholds, and a floating-point epsilon **is** a threshold. It also matters at
the kill boundary, which fires on equality — a gate that kills at exactly 80.0 %
must not turn on which side of a representation error a count lands.

---

## §3 Synthetic test coverage

```
SYNTHETIC_TESTS        = research/extensions/mmv/mmv_s2_validate.py
SYNTHETIC_TEST_COUNT   = 151
SYNTHETIC_TEST_PASS    = 151
SYNTHETIC_TEST_FAIL    = 0
```

| group | n | covers |
|---|---:|---|
| SEAL | 4 | seal and prereg hashes, sealed-commit ancestry, sealed artifacts unmodified |
| PIT | 16 | vintage eligibility, same-day rule at 14:00 / 15:45 / 15:46 / no-time, no-future, no final-revised leakage, exact-lag holes, first-release chain |
| POLICY | 20 | all three same-day cases, splice both sides, exact midpoint, contiguity, inverted range, **the metadata regression** |
| LEGS | 27 | all 9 growth pairs individually, inflation rate-vs-change, 24 vs 25 months, exactness, `sign(0)=0` |
| VOTES | 27 | 15-instrument domain, all 27 states, every sealed identity, tie/zero/missing semantics |
| GATE05 | 19 | 79/100, 799/1000, 80/100, 800/1000, 81/100, zeros, undefined, unmapped, per-instrument |
| CONCORD | 7 | no threshold, no verdict field, counts, exclusions |
| RISK | 15 | wrapper parameters, 15-column frame, dilution demonstration, caps, cost, no same-bar lookahead |
| START | 7 | insufficient history, first eligible month, each exclusion reason |
| FIREWALL | 9 | no artifact, no import-time reads, no forbidden series, guard-not-vacuous |

```
ALL_27_MACRO_STATES_TESTED         = YES
ALL_9_GROWTH_PAIRS_TESTED          = YES  (nine separate named tests)
FXY_NEG_UUP_TESTED                 = YES  (all 27 states)
MISSING_NOT_ZERO_TESTED            = YES  (all 15 instruments x 3 legs)
POLICY_METADATA_REGRESSION_TESTED  = YES
GATE05_79_9_TESTED                 = YES  (79/100 and 799/1000 both PASS)
GATE05_80_0_TESTED                 = YES  (80/100 and 800/1000 both KILL)
```

### 3.1 Tests written to be discriminating rather than decorative

Several assertions exist specifically because a plausible implementation would
fail them:

- **`t_require_months_detects_hole_at_the_exact_lag`** — a 29-month snapshot
  missing exactly `m-12` passes a naive row COUNT and must still be rejected.
  Coverage claims and computability claims are different claims.
- **`t_revision_becomes_visible_after_publication`** — without it, the
  no-leakage test above it would pass vacuously on a resolver that returns
  nothing at all.
- **`t_inflation_leg_is_the_change_in_the_rate_not_the_rate`** — a steadily
  rising index has `pi12 > 0` every month, yet the sealed leg reads the CHANGE
  in that rate and must return −1 here. An implementation that quietly traded
  the inflation LEVEL would pass a weaker test and fail this one.
- **`t_unmapped_zero_columns_would_dilute_the_book`** — asserts that the
  canonical wrapper really does dilute, so the guard against it is not vacuous.
- **`t_the_read_guard_is_not_vacuous`** — proves the firewall's AST read-scanner
  actually catches a read before trusting it to certify that none exist.
- **`t_policy_metadata_regression_poisoned_catalog_stamp_changes_nothing`** —
  see §4.

### 3.2 The policy-metadata regression, in full

The fixture rebuilds the exact S1 defect in miniature: a synthetic
DFEDTAR-shaped series in which every historical observation carries a single
late `realtime_start`, the 2008-12-15 discontinuation artefact.

The test asserts both halves:

```
the ALFRED view says nothing was public before the stamp
    poisoned.as_of("1991-06-28") == {}
    poisoned.as_of("2007-06-29") == {}

yet policy eligibility is completely unaffected
    before == after == [8, 6, 6]
```

Had the resolver consulted `realtime_start`, the first three cutoffs would have
gone UNDEFINED and the test would fail. This is the regression that protects
the audit issue discovered during S1.

---

## §4 Domain and dilution

```
MAPPED_INSTRUMENT_N   = 15
VNQ_IN_SIGNAL_DOMAIN  = NO
RWX_IN_SIGNAL_DOMAIN  = NO
```

VNQ and RWX are **absent**, not zero and not NaN. `risk.signal_frame` raises on
any attempt to include them, and `risk.assert_no_dilution` guards the frame
handed to the wrapper.

The reason is measured, not asserted. `src.portfolio.equal_weight_aggregate`
divides each asset's weight by the count of columns carrying a **non-NaN**
weight. A flat MMV cell is a real position and correctly counts as live. An
unmapped real-estate column carrying `0.0` would also count as live, shrinking
every real MMV weight by exactly 15/17 — verified in
`t_unmapped_zero_columns_would_dilute_the_book`, which asserts the ratio to
within 1e-12. Nothing about macro information would have caused that.

The Gate 0.5 side of the same distinction is verified separately:
`t_gate05_excludes_unmapped_from_numerator_and_denominator` and
`t_gate05_unmapped_cannot_push_agreement_down`.

---

## §5 Outcome firewall

```
HISTORICAL_RAW_MACRO_SIGNAL_COMPUTED           = NO
HISTORICAL_MMV_POSITIONS_COMPUTED              = NO
HISTORICAL_FIRST_RELEASE_DISAGREEMENT_COMPUTED = NO
HISTORICAL_GATE05_RESULT_COMPUTED              = NO
RETURN_OUTCOME_ACCESSED                        = NO
PNL_COMPUTED                                   = NO
SHARPE_COMPUTED                                = NO
BOOTSTRAP_RUN                                  = NO
BACKTEST_RUN                                   = NO
```

Enforced mechanically:

- every test builds its own synthetic world; **not one** reads a real macro
  value, a real price or a canonical TSMOM sign;
- `t_no_s2_build_file_reads_the_canonical_panel_or_frozen_macro_data` parses
  every S2 build file and fails on any file-read call whose path literal names
  `data/mmv`, `close_prices_raw` or `monthly_signal_panel`;
- `t_engine_modules_read_no_data_at_import` fails on module-level control flow
  or reads, so importing the engine cannot touch the frozen bytes;
- `t_engine_defines_no_pnl_sharpe_or_bootstrap_function` AST-scans the engine;
- `t_no_mmv_output_artifact_exists` walks the lineage directory for any `.csv`,
  `.json`, `.parquet`, `.pkl` or `.npy` that is not a pinned manifest.

The §14 boundary between **data parser validation** and **candidate feature
execution** is kept by construction. `mmv_s2_parser_check.py` resolves no cutoff
date, imports nothing from `legs` or `votes`, and touches exactly **one**
observation per series — it cannot build a leg, because it never looks at a
second reference month.

One parser result is worth recording because it re-confirms the S1 finding from
a second direction: `DFEDTAR.plumbing` reports **1 distinct vintage date across
9,577 observations**.

---

## §6 The S1 pre-seal check after a build — stated, not hidden

`mmv_preseal_check.py` is a **sealed S1 artifact**, pinned in the seal manifest
at `ab0eeb99…`. It has not been modified, and it must not be: it is the
validator of the S1 state.

Run against the **sealed commit** `cdb01fd` in a clean worktree, it still
reports **38/38 PASS**.

Run against the **S2 working tree**, it reports **36/38**, with groups A, B and
C at **33/33** and exactly two D-group failures:

```
D1  research/extensions/mmv/engine/gate05.py       (filename contains "gate")
D2  mmv_s2_validate.py imports src/config/pandas/numpy
    mmv_s2_validate.py defines position/sharpe/bootstrap/agreement
```

Both are correct behaviour from a check that asserts **"no implementation
exists yet"** — which was the right firewall at S1 and is the wrong one after
S2 was authorized to build. The D2 hits are substring matches against the
*names of the very tests that enforce the firewall*, e.g.
`t_engine_defines_no_pnl_sharpe_or_bootstrap_function`.

I did not rename modules or tests to keep the sealed check green. Contorting
names to satisfy a substring scan would have produced a passing check that
meant less than the honest failure. The S1 check validates the S1 commit; the
S2 validator carries the S2-appropriate firewall.

---

## §7 Canonical wrapper — reused, not cloned

`engine/risk.py` calls the canonical implementations directly:

```
asset vol       src.sizing.volatility_at_month_end        60d, annualized
asset weight    src.sizing.target_weights                 10% target, +/-2 cap
book            src.portfolio.equal_weight_aggregate      equal weight
portfolio vol   src.portfolio.realized_portfolio_vol
leverage        src.portfolio.leverage                    10% target, 3x cap
held position   src.portfolio.positions_from_weights      shift(1)
```

Every parameter is read from `config.py` at call time rather than copied, so a
divergence becomes an error instead of two hard-coded numbers drifting apart.
`t_wrapper_parameters_match_canonical_config` asserts all six against
`config.py` directly. **Canonical TSMOM is untouched.**

---

## §8 Open items

```
SCIENTIFIC_CHOICES_REMAINING    = NONE
CONTRACT_IMPLEMENTATION_BLOCKERS = NONE
```

No sealed definition proved impossible or internally contradictory. No epsilon,
alternate series, extra weight, fallback mapping, alternate cutoff, imputation
or extra asset class was introduced.

**One construction question is deferred to S3, and it is not a scientific
choice about the signal.** `PolicySchedule` is generic over an explicit
sequence of `(announced_on, announced_at, target)` records, and S2 tests it
that way. Building the *real* schedule requires attributing each administered
target change to the announcement that made it public. The contract fully
determines eligibility **given** a schedule (section C.2, and the six
collisions are pinned in `MMV_FOMC_TIMING_MANIFEST.json`), but it does not
specify how an effective date maps to its announcing meeting — which matters
for intermeeting changes, where a naive "latest FOMC date ≤ effective date"
rule could attribute a change to a meeting weeks earlier and admit it too soon.

```
S3_PREREQUISITE = announcement-schedule construction rule for the administered
                  policy target, to be confirmed before any historical policy
                  leg is built. NOT decided here. NOT a change to any sealed
                  definition.
```

It is recorded now rather than at S3 because deciding it later, with the
schedule half-built, is how a look-ahead gets rationalised.

---

## §9 Non-authorizations

This build record authorizes **nothing**.

```
RUN_AUTHORIZATION_CREATED = NO
S3_AUTHORIZATION_CREATED  = NO
```

Still requiring explicit Owner authorization: any historical MMV feature,
composite or position; the historical Gate 0.5 evaluation; the first-release
concordance cell; any return, Sharpe, bootstrap or interval; any RNG seed; any
`git push`, PR or merge.

```
EVIDENCE_CEILING = supported
```
