# TSMOM-VRP-01 — S2 ACCEPTANCE REPORT (BUILD + DATA ACQUISITION)

```
LINEAGE                   = TSMOM-VRP-01
CONTRACT_ID               = TSMOM-VRP-01-PREREG-01
AUTHORITATIVE_S1_SEAL     = 16d84545ba1385a482dbac7e776b31275f6fa5f7   (branch vrp/s1-seal-clean)
CANONICAL_BASE            = main @ d232d3361b23a9f64182c2ec8881284f0fc3b36e  (verified ancestor)
NON_AUTHORITATIVE_SEAL    = d19264af85f45c17f655493e02f71a653bfbdd86  — never used as authority
S2_BRANCH                 = vrp/s2-build   (created from the S1 seal commit; main not merged, not modified)
SESSION                   = Claude Opus / Claude Code, implementation Main Agent
S2_STATUS                 = READY_FOR_S3_ACCEPTANCE
REAL_RUN_AUTHORIZED       = NO
S3_AUTHORIZED             = NO
NEXT_GATE                 = ChatGPT S2 acceptance
```

**No real Stage-A or Stage-B outcome was computed, stored or revealed.** The engines are
implemented and exercised on synthetic fixtures only; the real acquired chain was touched
solely by mechanical checks whose outputs are hashes, counts, dates, contract identifiers
and booleans. `data/vrp_protected/` — the VRP family's own store — does not exist, and the
acceptance suite asserts it is empty at the end of S2.

---

## 1. What S2 was authorised to do, and what it did

| S2 authorisation | done |
|---|---|
| A. data acquisition / pinning | 274 Cboe official raw contract files + 7 primary specification documents, each SHA256-pinned |
| B. data ingestion / normalisation | loader, specification registry, normalized chain, empirical CFE calendar |
| C. engine implementation | 13 modules: chain, calendar, costs, sizing/stress, Stage A, Stage B, inference, prospective clocks, validators, reveal control |
| D. synthetic testing | 74 synthetic / identity tests |
| E. mechanical real-data validation | S2A gate, 32 checks, plus 9 real-data identity tests |
| F. implementation acceptance | all 21 acceptance-contract items PASS |

Not done, because S2 forbids it: no Stage-A historical outcome, no Stage-B historical
outcome, no return series, no Sharpe, CAGR, drawdown, bootstrap interval, tail statistic,
crisis-window outcome or cost-adjusted performance; no verdict about whether short VIX
works; no S3 run; no C-A prospective access.

---

## 2. S2A — DATA ACQUISITION, AUTHORITY, PINNING

`S2A_DATA_ACQUISITION_STATUS = PASS` — **32 checks PASS, 0 FAIL**
(`research/extensions/vrp/vrp_data_validate.py`; machine record
`data/vix/manifests/vrp_s2a_result.json`).

### 2.1 Source and authority

Both endpoints used are **Cboe official**, `SOURCE_AUTHORITY_LEVEL = 1 / PRIMARY`:

| endpoint | pattern | covers |
|---|---|---|
| Cboe delisted-contract archive | `cdn.cboe.com/resources/futures/archive/volume-and-price/CFE_<code><yy>_VX.csv` | 106 older monthly contracts |
| Cboe market-statistics historical data | `cdn.cboe.com/data/us/futures/market_statistics/historical_data/VX/VX_<expiry>.csv` | 162 newer monthly contracts |

No vendor copy is used anywhere, so §L's fallback-authority clause is never exercised.
The price taken is the official **`Settle`** column — never `Close`, never last trade,
never the Special Opening Quotation. `check_no_last_trade_price` asserts statically that
the loader does not read `Open`/`High`/`Low`/`Close` at all.

Where both endpoints serve one contract (6 contracts, 25 common settled dates) both files
are pinned and cross-checked on the common economic basis: **zero disagreements**. The
operative file is chosen by a mechanical rule that uses no return (most settled rows, then
most rows, then ARCHIVE).

**No credential of any kind exists in this lineage.** Both endpoints are public and
unauthenticated; nothing was printed, committed, hashed, logged or placed in a URL.

### 2.2 Coverage and integrity — permitted mechanical counts only

```
CONTRACT_COUNT                                = 268
FIRST_AVAILABLE_DATE                          = 2004-03-26
LAST_AVAILABLE_DATE                           = 2026-09-11
EXCHANGE_SESSIONS (empirical CFE calendar)    = 5654
CHAIN_DAYS                                    = 5617
NUMBER_OF_ROWS                                = 47160
NUMBER_OF_SETTLED_ROWS                        = 46331
NUMBER_OF_DUPLICATES                          = 0
STAGE_A_FIRST_MONTH  (§F.6, mechanical)       = 2006-09
STAGE_A_LAST_MONTH   (sealed)                 = 2026-08
STAGE_A_MONTHS                                = 240
MONTHLY_CONTRACT_COUNT_IN_WINDOW              = 242
NUMBER_OF_MISSING_SETTLEMENTS_IN_WINDOW       = 0
NUMBER_OF_CONTRACTS_WITH_GAPS_IN_WINDOW       = 0
SPECIFICATION_BREAK_COUNT                     = 1      (2007-03-26)
TICK_HISTORY_BREAK_COUNT                      = 1      (2007-03-26)
EXPIRY_RULE_BREAK_COUNT                       = 1      (contract month 2004-11)
EXPIRY_RULE_MATCH_COUNT                       = 264 / 264 expired contracts
CALENDAR_MISMATCH_COUNT (unexplained)         = 0
CALENDAR_DECLARED_CFE_ONLY_SESSIONS           = 3
RAW_DATA_COMMITTED                            = NO   (data/ is git-ignored; hashes are tracked)
```

`§F.6` is mechanical: the first calendar month from which every month through the Stage-A
cutoff is valid under §F.4. It resolves to **2006-09**, giving a frozen Stage-A window of
**240 months** with **zero** carry-forward days anywhere in it. Every month before that is
excluded by the rule alone, never by an outcome.

### 2.3 Three things the acquisition surfaced, and how each is closed

**(a) Four calendar months in which no standard monthly VX contract was ever listed** —
2004-12, 2005-04, 2005-07, 2005-09. Neither Cboe endpoint serves a file for these while
serving one for every neighbouring month. These are listing-history facts, not data gaps:
§F.3 orders contracts by final-settlement date and never assumes consecutive calendar
months. All four fall before the §F.6 first eligible month in any case.

**(b) VX has had two published monthly final-settlement rules.** Two expired contracts —
2004-07 (observed 2004-07-14) and 2004-10 (observed 2004-10-13) — do not match the rule
transcribed in §F.2/§L. They match the ORIGINAL rule exactly: *the Wednesday immediately
prior to the third Friday of the expiring month*. A dated expiry-rule registry now carries
both rules, and it reproduces the observed final settlement of **all 264 expired
contracts with zero mismatches**. §L's requirement — "rule-derived date = observed
final-settlement date for every contract; mismatches enumerated; any **unexplained**
mismatch = VRP-VALIDITY failure" — is therefore satisfied with no unexplained mismatch.
The data brackets the rule change to (2004-10, 2005-12]; inside that interval the two
rules agree on every date, so the boundary choice changes nothing this lineage uses. It
is outside the frozen window regardless. Details in `VRP_SPECIFICATION_REGISTRY.md` §2.

**(c) CFE keeps its own calendar.** Three dates in the record have official VX settlements
while the US equity market was closed: 2015-04-03 (Good Friday; CFE held a session),
2018-12-05 and 2025-01-09 (national days of mourning). They are declared exceptions in
`vrp_calendar.CFE_OPEN_WHEN_EQUITIES_CLOSED`; the consistency check FAILS on any mismatch
not listed there. There are **no** rule business days without any VX settlement anywhere.
Unexplained calendar differences: **0**.

### 2.4 Specification history — §F.5

Sourced to **CFE Information Circular IC07-03** (7 March 2007), saved and hashed as
`CFE-IC-2007-003.pdf`. Rescaling effective **2007-03-26**: price divided by ten,
multiplier $100 → $1,000, minimum tick $0.10 → 0.01 index point, dollar value of contract
and tick unchanged. The §F.5 conversion reproduces exactly that continuity, and the
rescaling date sits **inside** the frozen Stage-A window, so the normalisation is live, not
decorative.

**One span is undocumented, and the sealed rule closes it.** The exact date on which the
*outright* minimum increment moved from 0.01 to 0.05 index points is not established by any
primary Cboe document this session could obtain and read. §G's declared fallback applies:
the whole post-rescaling span carries the **largest documented comparable tick, 0.05**.
This is **economically inert and provably so** — §G charges `cost_points = max(0.10, tick)`
and every documented comparable tick lies in [0.01, 0.05], all below `c0 = 0.10`, so
`cost_points = 0.10` throughout regardless.
`test_i08_cost_invariant_to_tick_assumption` asserts it directly. Disclosed here and in
`VRP_SPECIFICATION_REGISTRY.md` §3, as acceptance item 8 requires.

---

## 3. S2B — ENGINE BUILD AND VALIDATION

### 3.1 Modules

| module | sealed role |
|---|---|
| `vrp_constants.py` | the frozen scientific constants; no tunables |
| `vrp_calendar.py` | expiry-rule registry, holiday rules, empirical CFE calendar, §F.3 roll weights |
| `vrp_specs.py` | dated quotation/multiplier/tick registry; the §F.5 conversion |
| `vrp_acquire.py`, `vrp_acquire_specs.py` | raw acquisition, immutable storage, hash pinning |
| `vrp_raw.py` | settlement loader, operative-source rule, normalisation |
| `vrp_chain.py` | constant-maturity chain, §F.4 carry-forward, §F.6 month validity |
| `vrp_costs.py` | §G cost engine; the `c0 = 0.05` variant structurally isolated |
| `vrp_sizing.py` | §D sizing, stress, reserve, granularity |
| `vrp_stage_a.py` | §E return-on-committed-capital benchmark |
| `vrp_stage_b.py` | §H self-financing book ledger |
| `vrp_inference.py` | §J stationary bootstrap |
| `vrp_prospective.py` | §P/§Q clocks — built, not started |
| `vrp_validators.py`, `vrp_ca_audit.py`, `vrp_data_validate.py`, `vrp_s2_accept.py` | gates |
| `vrp_reveal.py` | COMPUTE / STORE / REVEAL separation |

### 3.2 One defect found and fixed during the build — the variation-margin sign

§E.1 writes `VM_d = − Σ q_i,(d−1) · M_i · (S_i,d − S_i,d−1)` while §D.2 defines `q_i` as
"signed negative for the short" and adds that "the sensitivity is stated as the absolute
dollar loss per +1 point". Implemented literally — a leading minus on *signed-negative*
quantities — the position would **gain** when settlements rise, which is a long. The first
implementation did exactly that, and the closed-form oracle, written by the same session,
reproduced the same misreading and agreed with it. The economics test
(`test_i12_short_position_loses_when_the_curve_rises`) is what caught it.

The sealed object settles the reading: §A calls it a **short position**, and §D.2 fixes
`Loss_J = J · Σ q_i M_i = 0.30 · K` as a **loss** under a +30-point move. The two
consistent readings of §E.1 — a leading minus on *absolute* quantities, or no leading minus
on *signed* quantities — are the same arithmetic, and both give: settlements rise → the
short loses. The engine implements the signed form; the sign convention is documented at
the top of `vrp_stage_a.py` and pinned by a test so it cannot silently invert.

This is a **reading of the sealed text forced by the sealed object**, not a design change.
No Owner value moved. It is reported here because it is exactly the class of defect that
must not reach S3 unstated.

### 3.3 Acceptance-contract items — all 21 PASS

| # | item | level | result | tests |
|---|---|---|---|---|
| 1 | Data hashes | 1 | **PASS** | 3 |
| 2 | Specification-history tests | 1 | **PASS** | 3 |
| 3 | Contract identity | 1 | **PASS** | 5 |
| 4 | Roll-weight determinism | 1 | **PASS** | 3 |
| 5 | Missing-data branch tests | 1 | **PASS** | 4 |
| 6 | Cost rule tests | 1 | **PASS** | 7 |
| 7 | 2007 rescaling tests | 1 | **PASS** | 3 |
| 8 | Tick-history tests | 1 | **PASS** | 3 |
| 9 | Stress identity | 1 | **PASS** | 2 |
| 10 | Granularity gate | **2** | **PASS** | 2 |
| 11 | Stressed-margin gate | **2** | **PASS** | 2 |
| 12 | Stage-A accounting oracle | 1 | **PASS** | 5 |
| 13 | Self-financing Stage-B ledger oracle | 1 | **PASS** | 4 |
| 14 | Forced-liquidation oracle | 1 | **PASS** | 3 |
| 15 | Book-exhaustion oracle | 1 | **PASS** | 2 |
| 16 | Bootstrap reproducibility | 1 | **PASS** | 9 |
| 17 | Every result state synthetically reachable | 1 | **PASS** | 13 |
| 18 | Sabotage tests | 1 | **PASS** | 17 |
| 19 | C-A access audit | 1 | **PASS** | 1 |
| 20 | Frozen-constant transcription | 1 | **PASS** | 1 |
| 21 | No generated outcome before acceptance | 1 | **PASS** | 6 |

No item is cherry-picked; the runner maps every item to its evidencing tests and FAILS the
item if any is missing or failing. Machine record:
`research/extensions/vrp/s2/VRP_S2_ACCEPTANCE_LOG.json`.

Selected identities actually asserted:

- `Σ q_i M_i = 0.01·K` and `Loss_J = 30 · Σ|q_i M_i| = 0.30·K` within 1e−6 dollars.
- `R_J = 40·0.01K + 0.10K = 0.50·K`; `(1−b)·K = 0.70·K ≥ R_J`, slack `0.20·K`. The gate is
  proved non-vacuous: at `b = 0.45`, `R_J = 0.70K > 0.55K` and it **rejects**.
- At `W0 = $1,000,000`: `K_0 = $200,000`, sensitivity `$2,000/point` → exactly 2.0 standard
  or 20 mini contracts, 0 % rounding error.
- Roll weights sum to 1 within 1e−12 on all 5,617 real chain days; front weight is exactly
  0 on the last settlement before final settlement; the daily transfer is exactly `1/dt`.
- §H.4 oracle identity `r_book = 0.80·r_core + 0.20·r_A(K_t)` reproduced to ~7e−17 on
  synthetic no-funding months.
- `SeedSequence(7).spawn(4)` children match the seal manifest exactly
  (`entropy=7`, `spawn_key=(0,)…(3,)`), in the sealed order.

### 3.4 Sabotage battery — 17 defects, each caught

Each defect is reintroduced **by monkeypatching a value or function inside the test**,
never by editing a module on disk, and the corresponding validator or sealed identity is
asserted to reject it. `test_i18_package_bytes_unchanged` re-hashes every package file at
the end of the run against a snapshot taken at import, discharging the
"byte-restored and re-hashed" obligation with certainty rather than by procedure.

Caught: SOQ / last-trade used as a daily price · weight schedule off by one day · a cost
half-spread added on top of `c0` · stress applied post-roll · loss clipped at −100 % ·
selective (non-pro-rata) liquidation · external recapitalisation · a Stage-B replicate
dropped for its `D*` value · a canonical computation after 2026-09-11 · changed `J`, `b`,
`theta`, `s`, `delta_tail` or cutoff · protected C-A path access · a weekly contract
admitted · wrong 2007 normalisation · wrong multiplier · roll weights not summing to one ·
wrong Stage-B capital share · trailing-vol sizing.

### 3.5 Real-data mechanical validation — what was and was not run

Run on the real chain: chain completeness, contract identity, expiry identity, date
coverage, roll-weight identities, specification normalisation, missing-value flags,
calendar consistency, duplicate counts, hash re-pinning.

**Not run:** Stage A over real returns; Stage B over real history; any real candidate
return printed. `run_stage_a` and `run_stage_b` demand a `data_kind`, and `REAL` routes
through `vrp_reveal.require_run_authorization`, which refuses because no Owner execution
authorisation exists in committed state and the acceptance log is not yet committed.
`test_i21_real_stage_a_is_refused_during_s2` and its Stage-B twin assert the refusal.

`CONSTRUCTION_RECONCILIATION = NOT_RUN.` The S1 contract does not authorise a
public-index construction reconciliation for this object — §L lists no index source and
§R declares no reconciliation descriptive — so none was performed and no exposure was
incurred. Nothing in the acceptance contract requires one.

### 3.6 Reveal control

`vrp_reveal.py` keeps COMPUTE / STORE / REVEAL structurally apart. `ProtectedResult`
refuses `repr`, `str`, `format`, iteration and `.value`; a stray `print(result)` yields
`<ProtectedResult … GENERATED_NOT_SEEN sha256=…>` and nothing else. Generated evidence
would be written to `data/vrp_protected/` — the VRP family's own store, a sibling of the
C-A mechanism, never the C-A store or key — and a reveal needs a separate single-use Owner
grant read from committed state. No summary JSON produced by this build contains any
scientific outcome.

### 3.7 Prospective clocks — built, not started

```
VRP-A-PROSPECTIVE   entry settlement (first VX month-end settlement after the S1 seal) = 2026-09-30
                    first scored month = 2026-10 ;  N_A = 120 ;  started = NO
VRP-B-PROSPECTIVE   N_B = 120 calendar months, window freezes there ; n_T_min_prosp = 10 ; started = NO
                    DEFERRED_EVALUATION_FROZEN_WINDOW and NOT_EVALUABLE both implemented
```

The entry settlement is a **calendar fact implied by the seal**; computing it starts
nothing. `start_prospective` routes through the same Owner gate and cannot succeed in S2.

---

## 4. C-A safety

```
C_A_PROSPECTIVE_OUTCOME_ACCESSED   = NO
C_A_PROTECTED_STORE_ACCESSED       = NO
C_A_POSITION_LAYER_ACCESSED        = NO
C_A_RETURN_LAYER_ACCESSED          = NO
CANONICAL_FORWARD_RETURN_COMPUTED  = NO
```

A **static** audit (`vrp_ca_audit.py`, log `s2/VRP_CA_ACCESS_AUDIT.json`) reads all 21
package source files and proves none imports a C-A module, names a C-A store path or key,
or references the C-A prospective tree. The VRP package computes **no canonical quantity
at all**: Stage B consumes the core only as an externally supplied monthly return and daily
unit index. `run_stage_b` additionally refuses any core day after 2026-09-11 or after the
sealed Stage-B boundary 2026-05-31 (`CanonicalBlindnessBreach`). The audit is static on
purpose — it cannot be satisfied by a run that merely happened not to touch C-A.

---

## 5. Tests, validators, secret scan

| suite | result |
|---|---|
| VRP acceptance suite | **100 passed, 0 failed, 0 skipped** (74 synthetic/identity, 17 sabotage, 9 real-data mechanical) |
| Repository suite (`python -m pytest -q`) | **101 passed, 0 failed, 0 skipped** — unchanged; no pre-existing test was modified or weakened |
| Standalone validators | 7 / 7 PASS |
| C-A access audit | PASS |
| Secret scan | PASS — 28 files scanned, 0 findings |
| S2A data gate | PASS — 32 / 32 |

`vrp_tests.py` follows the repository's existing convention (`value_tests.py`,
`ca_s2_tests.py`) and is not auto-collected by the documented root `pytest` run.

### 5.1 Sealed prereg validator — one expected S1-state failure, disclosed

`vrp_prereg_validate.py` reports **113 checks PASS, 1 FAIL**, exit 1. The single failure is:

```
no data/vix directory exists yet                                       FAIL
```

This is an **S1-state assertion**, not a contract-content check: it exists to prove that at
the moment of sealing no outcome-bearing acquisition had begun. The Owner-authorised S2
data acquisition necessarily flips it, because §L itself mandates that raw files land under
`data/vix/raw/`. The validator is a hash-pinned S1 authoritative artifact and was **not
modified** (`check_sealed_artifact_hashes` confirms all four sealed files are byte-identical
to the seal). Every provenance, Owner-value, structural, forbidden-phrase and
companion-artifact check passes.

A second potential collision was avoided rather than accepted: all S2 JSON artifacts live
in `research/extensions/vrp/s2/`, so the validator's "no data-like files inside the package"
check (which is non-recursive) remains true of the sealed package directory.

`PREREG_VALIDATOR = PASS on all 113 contract-content checks; the one failing check is the
S1-state assertion that authorised S2 acquisition necessarily invalidates.`

---

## 6. What did not change

```
S1_ARTIFACTS_MODIFIED      = NO   (all four sealed files byte-identical; hashes re-verified)
OWNER_VALUES_CHANGED       = NO
SCIENTIFIC_DESIGN_CHANGED  = NO
MAIN_MODIFIED              = NO
C_D_MERGED                 = NO
PUSHED                     = NO
```

No sealed constant, window, estimand, state boundary, cost rule, calendar rule or inference
constant was altered. Nothing in `research/extensions/ca/` was touched. No configuration
knob exists for any sealed scientific value.

### Mechanical implementation details recorded (not Owner decisions)

Both are incapable of changing the economic estimand, as §J's own carve-out anticipates:

1. **Bootstrap draw order.** Within each block the generator is drawn in the order §J lists
   them — geometric block length first, then uniform start index. Both are independent
   draws from fixed distributions, so the law of the bootstrap distribution is identical
   under either order; only the realised stream differs.
2. **Operative-source rule** where two Cboe files serve one contract (most settled rows,
   then most rows, then ARCHIVE). Both files carry the same official field and agree on
   every common date, so the rule selects between identical economics.

---

## 7. Verdict

```
TSMOM_VRP_01_S2_COMPLETED  = YES
S2A_DATA_ACQUISITION_STATUS = PASS
ENGINE_IMPLEMENTED          = YES
SYNTHETIC_TESTS             = 74 pass / 0 fail
SABOTAGE_TESTS              = 17 pass / 0 fail
REAL_DATA_MECHANICAL_TESTS  = 9 pass / 0 fail
REPOSITORY_TESTS            = 101 pass / 0 fail / 0 skip
IMPLEMENTATION_ACCEPTANCE_CONTRACT = PASS  (21 / 21)
SECRET_SCAN                 = PASS
C_A_SAFETY                  = PASS
REAL_STAGE_A_COMPUTED       = NO
REAL_STAGE_B_COMPUTED       = NO
REAL_PERFORMANCE_REVEALED   = NO
S2_STATUS                   = READY_FOR_S3_ACCEPTANCE
S3_AUTHORIZED               = NO
REAL_RUN_AUTHORIZED         = NO
NEXT_GATE                   = CHATGPT S2 ACCEPTANCE
```

S2 completion gives ChatGPT something to accept. It authorises nothing further. Stage A has
not been run. Stage B has not been run. No real performance has been revealed.

*Recompute every hash cited here before use. Chat-carried bytes are never a source of truth.*
