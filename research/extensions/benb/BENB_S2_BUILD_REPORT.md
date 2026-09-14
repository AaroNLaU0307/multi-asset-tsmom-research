# CTA-EDGE-02-BENB — S2 BUILD + SYNTHETIC VALIDATION REPORT

    LINEAGE            CTA-EDGE-02-BENB   (bond ETF - NAV basis)
    STAGE              S2 BUILD                     (NOT S3. NOT a run. NOT a verdict.)
    DATE               2026-09-15
    BRANCH             cta-edge/bond-etf-nav-s0
    PARENT HEAD        c1a3f8155a9fdb86d55b620c33498f604fcbf8d0   (the S1 seal commit)
    DATA TOUCHED       SYNTHETIC fixtures + pinned-file BYTE IDENTITIES only
    OUTCOME EXPOSURE   NONE

This document records what was built, what was mechanically demonstrated, and — with
equal care — what was **not** established. Nothing here is evidence about HYG, LQD, the
bond-ETF basis, or any candidate edge. Every number in this report is a property of a
constructed fixture or of the sealed contract text.

---

## 0. SCOPE — WHAT THIS BUILD DID NOT DO

The following were forbidden by the task and none of them occurred. This is not a
promise; §8 and §9 below record the mechanical checks that make each one unreachable
from the S2 code paths.

    NOT computed / NOT inspected:
      historical b_t = ln(P_close / NAV)          historical x_t
      historical discount-sign count              historical discount severity
      actual signal dates                         beta_T / beta_O / beta_N on real data
      real HYG or LQD conditional returns         real mean NET trade return
      real calendarised Sharpe                    real bootstrap intervals
      real leave-one-year-out results             March-2020 basis inspection
      historical premium/discount plots           crisis outcome inspection
      a real A / B / C / D / E / F / S class      any backtest

    NOT done:
      git push       merge       PR       force-push      develop/main modification
      an S3 execution authorization               any change to a sealed artifact

The only historical bytes read were the seven pinned files, hashed whole and never
parsed (§7), plus — in two explicitly marked tests — the **date columns alone**, which
produce a structural row count and cannot form a basis.

---

## 1. SEAL IDENTITY (recomputed at build time)

    research/extensions/benb/BENB_PREREGISTRATION.md
      sha256   1b7ca2122ba14c4097e4d76d7a733bf0c77ab9c0d02dd93a38c25bc1be5160cf

    research/extensions/benb/BENB_SEAL_MANIFEST.md
      sha256   6aa0d21401b9887f4a44ab6559fa10d7a59ae5a8b512e1ad306543c061483703
      bytes    13,209

    ops/OWNER_DECISION_RECORD_CTA_EDGE_02_BENB.md   (BENB-OD-1, source of M2)
      sha256   63a3da1b79fad18486139950c7845bee20951b2dd2ec87f8dd446da07162d943

    seal commit   c1a3f8155a9fdb86d55b620c33498f604fcbf8d0

Both seal hashes are pinned in `benb_contract.py` and re-verified by
`test_c03_seal_identity_is_pinned_in_the_contract_module` and by the build driver.
**No sealed artifact was modified by this build.** `benb_prereg_validate.py` is
byte-identical to its sealed version (`dfaff01a…9b984`) and still returns 72/72 PASS.

---

## 2. COMPONENT INVENTORY

| module | lines | sha256 | role |
|---|---:|---|---|
| `benb_contract.py` | 126 | `776a9961a2f9b6e9078003f6a5b59a089c1474828d7352fef77b1814620a18d9` | the sealed constants, as executable values |
| `benb_authorization.py` | 125 | `71f20a49e8fd94313394153bf71ed2fb1ad6aeb16e467aa61747ac2dab3d6fb7` | the hard run guard (reuses the existing Owner ledger) |
| `benb_data.py` | 232 | `5a50c03560a80545769ee909203e13c1e0b411a17808a2ba41303c43eaf28b5b` | sources, validation, `align_grid`, eligibility, ex-dates |
| `benb_feature.py` | 93 | `a2f2d0995a8ea64a2f932fdeb899af503f3c15d6c07331ea712a5d0f1a622f3b` | `b_t`, the expanding median, `x_t`, the discount filter |
| `benb_engine.py` | 228 | `bb38e0905dab431085ecbe71b73d698ff48bb06bb5acfdee80dd7fe3c43f5c75` | decomposition, Gate 1, the fixed trade, monthly P&L |
| `benb_inference.py` | 167 | `42ee6589e14459881c4ed6f6f2b037f343c1b724e8a7760f4e2c56a341a8225e` | the ONE year-block bootstrap and the ONE LOYO diagnostic |
| `benb_classify.py` | 160 | `1a6b1ec4748bb02cedb0fda5c9efcb6d06e322e59c3d0644be01966b20a973a1` | the §J.3 decision order, transcribed exactly |
| `benb_pipeline.py` | 126 | `3e8646f50024983aa6c83c0d3004ea401ed3bf2fa7ed4813e5b79454b5d08f64` | the end-to-end cell run; `classify_primary` |
| `benb_report.py` | 139 | `2b0f3fb1808488d2123fcf27ea9b2be1097eb117ae86e00bd7a548c8bf2b0541` | the S3 result schema, builder, validator, writer |
| `benb_oracle.py` | 159 | `0e46e93ce5fe72e02d30f38c2a75452721f3a27a9db4e87b466ecc3051e8c310` | the INDEPENDENT synthetic oracle |
| `benb_fixtures.py` | 155 | `afffc979c4167f41cbf74e171410a58d6d08240d5d765167c3007af400276f78` | the synthetic economic worlds |
| `benb_tests.py` | 983 | `617db562e7acab96a0b3eef4ca7f2cbfaafc4d200a7d4374eda3d060abd655a2` | 65 behavioural tests |
| `benb_s2_build.py` | 241 | `6067a3292231c0f7889042f0d428a2b17a4fbf4e3626f64321a3ca2ed462969d` | the S2 driver |
| `BENB_SYNTHETIC_EXAMPLE_RESULT.json` | 115 | `70353e8c4e9cd129ac79cc7e8de15e56e06e84865df719635d78e48fc220f940` | example artifact, `SYNTHETIC_ONLY = YES` |

Unchanged and carried forward: `BENB_S0_FRAME.md`, `BENB_S0_REPAIR_RECORD.md`,
`BENB_PREREGISTRATION.md`, `BENB_SEAL_MANIFEST.md`, `benb_prereg_validate.py`.

---

## 3. TEST RESULTS

    research/extensions/benb/benb_tests.py      65 passed        3.06 s
    research/extensions/benb/benb_prereg_validate.py   72/72 PASS
    research/extensions/ta/ta_tests.py          48 passed  (prior lineage, unaffected)
    python -m pytest  (repository default)      98 passed, 3 failed, 2.30 s

The 65 BENB tests break down as:

| group | n | what it pins |
|---|---:|---|
| `c00–c03` | 4 | constants re-derived from the sealed Markdown; oracle independence; seal hashes |
| `f01–f05` | 5 | the strictly-causal expanding median; the 250-observation boundary; discount-only |
| `d01–d03` | 3 | the exact three-component identity in all four worlds; violations raise |
| `w1–w5` | 5 | the three mandatory economic worlds + the mixed world + the cost sign |
| `x01–x03` | 3 | the forward-looking ex-date rule, the UNION, and the disabled-exclusion variant |
| `t01–t05` | 5 | the fixed trade, the round trip, retained zero months, the ENTRY month |
| `g01–g03` | 3 | Gate-1 OLS against the oracle; zero-variance raises; coefficient recovery |
| `b01–b05` | 5 | determinism, the required RNG, the FROZEN feature, whole-year blocks |
| `l01–l02` | 2 | LOYO detects a single carrying year; exactly one fragility diagnostic exists |
| `k01–k06` | 6 | totality, reachability, strict boundaries, the sealed status map |
| `r01–r04` | 4 | premium, LQD and the diagnostic legs carry no rescue and no promotion power |
| `cb01–cb08` | 8 | weekend / holiday / month / year boundaries; structural defects; class F |
| `fw01–fw02`, `gd01–gd04` | 6 | the real-data firewall and the hard run guard |
| `meta01–meta02` | 2 | pinned byte identities; structural date counts only |
| `rep01–rep04` | 4 | the S3 artifact schema and its refusals |

---

## 4. THE THREE MANDATORY ECONOMIC WORLDS

The fixture builder exploits the sealed identity `Δb = R_ON + R_TR − R_NAV`: a world
pins how `R_TRADABLE` and `R_NAV` respond to the discount severity `d`, and the
overnight leg is then **forced**, not fitted. The burn-in and every non-signal day sit
at `b = 0`, so the expanding median is exactly `0` and `x_t = −d` with no approximation
— which is what lets a test assert an expected coefficient instead of a vague sign.

Driver run at the **sealed production** `B = 10,000`, 300 signals, 5 calendar years,
42-month grid, 300 discount and 603 premium observations per world:

| world | construction | beta_T 95 % | beta_O 95 % | beta_N 95 % | LOYO | CLASS |
|---|---|---|---|---|---|---|
| **1. STALE NAV** | `R_TR = 0`, `R_NAV = −d` | `[-3.28, 9.48]` | `[-8.08, 6.99]` | `[-10004.88, -9990.69]` | fail | **A** `not_promoted` |
| **2. OVERNIGHT DISCOVERY** | `R_TR = 0`, `R_NAV = 0` ⟹ `R_ON = +d` | `[-3.28, 9.48]` | `[9991.92, 10006.99]` | `[-4.88, 9.31]` | fail | **B** `not_promoted` |
| **3. TRADABLE CONVERGENCE** | `R_TR = +d`, `R_NAV = 0` | `[9996.72, 10009.48]` | `[-8.08, 6.99]` | `[-4.88, 9.31]` | pass | **S** (fixture) |
| **MIXED** (§15) | `R_TR = 0`, `R_NAV = −0.5 d` ⟹ `R_ON = +0.5 d` | `[-3.28, 9.48]` | `[4991.92, 5006.99]` | `[-5004.88, -4990.69]` | fail | **A-M** `not_promoted` |

Every required behaviour holds:

* **World 1** — `beta_N` supported negative, `beta_T` not supported, verdict is a
  non-harvestable stale-NAV class. Never supported.
* **World 2** — `beta_O` supported positive, `beta_T` not supported, verdict is
  overnight-price-discovery. Never supported. The move happens **before** the earliest
  lawful entry, so it is not harvestable under this signal timing.
* **World 3** — `beta_T` supported positive. This is the **only** world that reaches
  Gate 2 (`test_w3` asserts the class lies in `{D, S, E, G}`; the other three worlds
  terminate at Gate 1).
* **Mixed** — both diagnostic legs fire and `beta_T` still fails; A-M, `not_promoted`,
  with the mandatory `MIXED_NON_HARVESTABLE_CONVERGENCE` qualifier.

`test_w5` adds the economic sign check: only the tradable world earns a positive mean
`NET_TRADE_RETURN`; the two non-tradable worlds lose exactly the 10 bps round trip.

**The class-S result in world 3 is a property of a fixture that was built to converge in
the tradable window.** It says nothing whatsoever about HYG.

---

## 5. THE INDEPENDENT SYNTHETIC ORACLE

`benb_oracle.py` imports **nothing** from the production engine —
`test_c02_oracle_imports_nothing_from_the_production_engine` greps its import lines for
`benb_engine`, `benb_feature`, `benb_inference`, `benb_classify`, `benb_pipeline`,
`benb_contract`, `benb_data` and `benb_fixtures` and fails on any of them. It
re-transcribes the sealed constants from the contract text and `test_c01` fails if they
ever drift from `benb_contract`.

Independence is *algebraic*, not merely textual, because the failure mode this programme
has actually suffered twice (the VRP variation-margin sign; the `VRP-DIAG-DEFECT-001`
fixture) is an oracle that reproduces the producer's own misreading:

| quantity | production route | oracle route |
|---|---|---|
| median | `statistics.median` over a growing list | explicit sort-and-middle |
| OLS slope | centred sums of squares | Cramer's rule on the 2×2 normal equations |
| Sharpe | running variance | explicit two-pass sum of squared deviations |
| classification | `if` cascade over the §J.3 steps | independently re-derived from the contract |
| monthly P&L | dictionary accumulation over a pre-built grid | linear scan per grid month |

`test_k02` cross-checks the classifier against the oracle on the **entire** sealed sweep
(> 10,000 boundary-dense cases, 0 disagreements). `test_f03`, `test_d02`, `test_g01`,
`test_t02`, `test_t03` and `test_t05` cross-check the feature, the decomposition, all
three Gate-1 slopes, the monthly series, the Sharpe and the month grid.

---

## 6. DISCRIMINATING FIXTURES

Three places where a naive fixture would have proved nothing, and what was built
instead:

1. **The expanding-median test.** On the flat burn-in used by the economic worlds, a
   single outlier cannot move a median of 250 identical values, so the "today's value
   did not leak" assertion would pass for a *broken* engine too. `monotone_cell()`
   therefore builds a strictly increasing basis: `m_250` is exactly `1e-4 × 124.5`, and
   corrupting `b_250` leaves `m_250` unchanged while shifting `m_251` from
   `1e-4 × 125` to `1e-4 × 124` — one order statistic. The invariant is a real
   separation.

2. **The ex-date test.** `test_x02` injects a 2 % distribution on `t+1` — NAV drops,
   the price gaps down at the open — and asserts the contamination is exactly `−0.02`
   in **both** `R_NAV` and `R_OVERNIGHT` and exactly **zero** in `R_TRADABLE`. It then
   shows the sealed rule removes the observation, and that with the exclusion
   **disabled** the same observation survives. `test_x03` goes further and shows that
   leaving 20 such days in **moves the estimated `beta_N`**: the rule changes a number,
   not only a row count.

3. **The frozen-feature test.** `test_b03` proves the bootstrap cannot recompute the
   expanding median by construction — `year_block_bootstrap`'s parameters are exactly
   `{obs, month_grid, b, rng}`, it never sees a `CellData` or a price, and the module
   imports neither `benb_feature` nor `benb_data`. `test_b04` supplies the separation
   that makes this non-vacuous: two year-blocks whose medians genuinely differ, so a
   recomputed median *would* move.

The December-to-January boundary test (`test_cb02`) is likewise deterministic rather
than hopeful: `build_world` gained a `first_signal_index` parameter so the signal is
**placed** on the last business day of a December by choosing the block offset, instead
of waiting for the pattern to happen to land there.

---

## 7. PINNED DATA — IDENTITY ONLY

All seven pinned files reproduce their sealed sha256 (`test_meta01`, and the driver):

    ishares_HYG_fund_download.xml   10dcd91e095a56d83762019738aa5b14374ea5d1f723616636b52170150ec533
    ishares_LQD_fund_download.xml   d0cc3b0121806b20a227b00ae50d3f8523e6cc560e7bae16d715824b50ce0a47
    HYG_raw_ohlc.csv                1ed30697cd0c665d9abe3d60abfe8c03314fb8889f3a459df207c5b85cb3bce8
    LQD_raw_ohlc.csv                9d120233fd18bbd28188c18ce5a99b8347416f58b903d7452b83b47d011fe036
    HYG_nav_daily.csv               7735da958ef10522e39c9138b8cf8c686206585f3b805c327588fb61e9eae5de
    LQD_nav_daily.csv               3d78dbd80b92e9715eb9f6249597d65556d12b6517aad6832640e7296698007a
    benb_price_meta.json            8179c06f8f8dd088d3b08cb9b4d6a1a8abbd210239f3e2b226e70de223d8b339

These files were **hashed, not parsed**. The one exception is `test_meta02`, which reads
the **date column and nothing else** from the price and NAV CSVs and confirms the
structural intersection counts already established at S0 repair (HYG 4,887 / LQD 6,069).
No price value, no NAV value and therefore no basis can be formed from what that test
reads.

---

## 8. THE REAL-DATA FIREWALL

Price and NAV reach the engine through a `CellSource` and through nothing else. There
are exactly two implementations:

* `SyntheticCellSource` — in-memory fixtures, `data_kind = SYNTHETIC`. It has **no path
  attribute and performs no file access at all**, so a forgotten or mis-ordered patch
  cannot fall through to the historical files. `test_fw01` proves it holds no production
  path. `test_gd04` parses the AST of every module on the path from a price to a
  verdict (`feature`, `engine`, `inference`, `classify`, `pipeline`, `oracle`,
  `fixtures`) and asserts none of them calls `open`, `exec`, `eval` or
  `__import__`, and none mentions `DATA_DIR`, the historical directory, the pinned
  hash table, `read_csv`, `urlopen`, `requests` or `subprocess`. It parses rather
  than greps because the literal `"open(t+1)"` in `benb_engine` is a position leg,
  not a call. `benb_contract` is deliberately excluded from that list: it *owns*
  `DATA_DIR`, and `benb_data.RealCellSource` — the one class behind the guard — is
  the only consumer of it in the engine.
* `RealCellSource` — the pinned files, `data_kind = REAL`. Its constructor calls the run
  guard **before opening anything**.

`assert_synthetic()` is called on every S2 validation path and raises on anything whose
`data_kind` is not `SYNTHETIC` (`test_fw02`).

---

## 9. THE HARD RUN GUARD

Not a new mechanism: `benb_authorization.py` reuses the repository's existing append-only
Owner ledger `ops/EXECUTION_AUTHORIZATIONS.md`, read from **committed git state**, with
the same fenced-`json` record shape and lifecycle events that `x01_authorization.py`
defines and `ta_authorization.py` scoped for the previous lineage. Only the id prefix
differs (`BENB-AUTH`).

Two inherited asymmetries:

* **Granting requires committed state** — nobody authorises a real run by editing a file
  in the worktree.
* **Blocking does not** — an unreadable ledger, a missing ledger, no git, an unparseable
  record, or more than one live grant all **refuse**. Fail-closed is not symmetric.

Current status, recomputed at build time:

    ledger                    ops/EXECUTION_AUTHORIZATIONS.md
    BENB EXECUTION grants     0
    real_run_authorized       False
    RealCellSource(run_id=…)  REFUSED -> RunNotAuthorized

`test_gd02` installs a tracking `open()` and proves the refusal happens **before a single
price, NAV or fund file is opened**. `test_gd03` proves grants are read only via
`git show`, and that an unreadable path returns `None` (a refusal, not an absence).

**A seal is not authorization to execute. S2 completing is not authorization to execute.**

---

## 10. FIREWALLS AROUND THE VERDICT

| channel | promotion power | rescue power | mechanism |
|---|---|---|---|
| `HYG beta_T` (primary) | **yes** | no | the only Gate-1 input |
| `beta_O` (overnight) | no | no | classification consumes it only to *separate* A / A-M / B |
| `beta_N` (NAV) | no | no | same |
| LQD secondary | no | no | `classify_primary()` takes the primary cell and nothing else |
| premium side | no | no | `classify()` has no premium parameter at all |

* `test_k05` asserts `classify()`'s parameter set is **exactly** the ten interval bounds
  plus `loyo_ok` and `is_evaluable`, and that its body contains no mention of premiums,
  LQD or a secondary.
* `test_k01` sweeps the whole input domain and confirms `illegal_promotions == 0`: every
  class-S case remains S when `beta_O` and `beta_N` are replaced with neutral values, so
  a diagnostic can never be what produced a promotion.
* `test_r02` runs a **stale-NAV HYG** beside a **spectacular LQD** in the same source and
  confirms the HYG verdict is unchanged, `not_promoted`, with
  `promotion_power = rescue_power = NONE` on the secondary.
* `test_r01` writes a fabricated 9,999 bps premium convergence into the descriptive block
  and confirms the verdict does not move.

---

## 11. THE EXAMPLE S3 ARTIFACT

    research/extensions/benb/BENB_SYNTHETIC_EXAMPLE_RESULT.json
      sha256          70353e8c4e9cd129ac79cc7e8de15e56e06e84865df719635d78e48fc220f940
      schema          BENB-RESULT-1
      synthetic_only  YES
      data_kind       SYNTHETIC
      run_authorization_id   null
      source          the SYNTHETIC_TRADABLE_CONVERGENCE_FIXTURE world, B = 10,000

The headline world is the tradable one precisely because it is the only world that
populates **every** schema field, including the Gate-2 flags — which is what an example
artifact is for. The file carries an explicit `synthetic_world_note` saying so.

`build_result()` refuses to stamp `SYNTHETIC_ONLY = NO` without a run authorization id
(`test_rep02`). `validate_result()` rejects an artifact whose class, status, qualifier or
evidence ceiling contradict the sealed §I.4 mapping, and `write_result()` refuses to
persist one (`test_rep03`, `test_rep04`). The artifact is **not byte-reproducible across
runs** because it stamps `generated_at_utc`; every computed value in it is.

---

## 12. KNOWN FIXTURE PROPERTIES (not defects)

* **The synthetic worlds have only 5 calendar-year blocks.** With five blocks the
  bootstrap is coarse: the original multiset (all five years, each once) occurs in
  `5!/5⁵ = 3.84 %` of replicates, which exceeds 2.5 %, so the 97.5th percentile of the
  Sharpe lands exactly on the point estimate. This was checked directly — the point
  estimate is also the maximum over all 10,000 replicates — and it is arithmetic, not an
  engine fault. The structurally eligible HYG panel spans ~19 years.
* **The fixture noise is a small deterministic LCG**, not a statistical model. The worlds
  are built to make a coefficient *exactly* recoverable (`test_g03` asserts
  `beta_T = 1e4` and `beta_N = −1e4` to 1e-9 relative at zero noise), not to imitate
  markets. A fixture that imitated markets would be a worse test.
* **Class-S reachability in world 3 is a fixture fact.** It demonstrates that the Gate-2
  path is *reachable and correct*, which is exactly what an S2 build must show, and
  nothing more.

---

## 13. REPOSITORY SUITE — PRE_EXISTING vs NEW

    python -m pytest          98 passed, 3 failed

    FAILED tests/test_xsmom_universes.py::test_decomposition_reconstructs_realized_profit
    FAILED tests/test_xsmom_universes.py::test_dispersion_localises_to_term3
    FAILED tests/test_xsmom_universes.py::test_leadlag_shows_up_in_term2
      pandas._libs.tslibs.np_datetime.OutOfBoundsDatetime: Out of bounds timestamp:
      2333-04-30 00:00:00 with frequency 'ns'

    CLASSIFICATION: PRE_EXISTING  (3 of 3)
    NEW FAILURES:   0

Proof rather than assertion: `git status --porcelain` shows this build **modified no
tracked file** — every entry is a new untracked file under `research/extensions/benb/`.
The suite above therefore ran HEAD's own code for those three tests. The failure is a
pandas out-of-bounds timestamp in the XSMOM universe fixtures, unrelated to BENB, and it
was independently confirmed pre-existing on a clean detached worktree during the previous
lineage. **It was not "fixed" here** — repairing an unrelated pre-existing failure inside
a sealed-lineage build commit is exactly the kind of scope creep this governance model
forbids.

Note on collection: bare `pytest` collects only `tests/` because the extension suites are
named `*_tests.py`, which does not match pytest's default `test_*.py` / `*_test.py`
patterns. `benb_tests.py` and `ta_tests.py` are therefore run explicitly, as in the
previous lineage.

---

## 14. UNBOUND SCIENTIFIC CHOICES ENCOUNTERED

**NONE.** Every decision taken in this build was mechanical/software:

| decision | why it is mechanical |
|---|---|
| dependency-injected `CellSource` rather than monkeypatching | a firewall implementation detail; changes no definition |
| `align_grid()` extracted as a named function | the §D.1 intersection rule was already sealed; extracting it only made it testable without touching the panel |
| `first_signal_index` added to the fixture builder | a test-fixture control; affects no production path |
| `monotone_cell()` for the median test | a fixture that makes an existing sealed invariant falsifiable |
| driver default `B = 2,000`, `--production-b` for `10,000` | a runtime convenience; the recorded run used the sealed 10,000 |
| skipping the two `meta` tests when `data/benb/` is absent | those files are git-ignored; the driver performs the same check unconditionally |

No sealed definition was reinterpreted, relaxed, tightened or extended. Where the
contract was silent on an implementation detail, the build chose the option that made a
sealed rule **harder** to violate, never one that would have required a scientific call.

---

## 15. WHAT IS AND IS NOT ESTABLISHED

**Established (mechanical evidence, synthetic):**

* The sealed contract is implemented, and the implementation agrees with an independent
  oracle on the feature, the decomposition, all three Gate-1 slopes, the monthly series,
  the Sharpe and the entire classification domain.
* The three mandatory economic worlds produce the three mandated verdicts, and only the
  tradable-convergence world reaches Gate 2.
* The causal feature, the ex-date rule, the fixed trade, the retained zero months, the
  frozen-tuple bootstrap and the strict M1 / M2 boundaries all behave as sealed.
* Neither the premium side, nor LQD, nor either diagnostic leg can promote or rescue.
* A REAL run is mechanically refused at S2, before any historical byte is opened.

**NOT established, and not claimed:**

* Nothing about HYG, LQD, or the bond-ETF–NAV basis. No candidate statistic exists.
* Infrastructure readiness is **not** alpha. A green S2 is **not** an S3 authorization.
* `BUILDER CLAIM ≠ MECHANICAL EVIDENCE ≠ INDEPENDENT VERIFICATION`. This document is a
  builder report carrying mechanical evidence; it is not independent verification.
* The evidence ceiling for this lineage remains **`supported`** — never `confirmed`,
  never independently confirmed — because the ETF price leg is a reused / burned sample.
  A new NAV leg does not launder it.

---

## 16. NEXT GATE

The next step is **not** taken by an agent. It is Aaron's:

    S3 RUN requires a single-use Owner EXECUTION authorization recorded in
    ops/EXECUTION_AUTHORIZATIONS.md and COMMITTED, with a BENB-AUTH id, the
    lineage binding CTA-EDGE-02-BENB, and the run_id and RNG seed fixed in the
    grant rather than chosen from an outcome.

Until such a record exists in committed state, `require_run_authorization(REAL, …)`
refuses and `RealCellSource` cannot be constructed.

---

*S2 BUILD: COMPLETE. No run. No reveal. No promotion. No push.*
