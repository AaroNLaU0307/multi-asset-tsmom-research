# CTA-EDGE-04-MMV — S3 PRIMARY HISTORICAL RETURN RESULT

```
S3_STATUS                 = PASS   (the run executed cleanly and produced the
                                    sealed verdict; it is NOT a gate result)
RUN_ID                    = MMV-S3-20260917-01
RUN_TYPE                  = PRIMARY_HISTORICAL_RETURN
AUTHORIZATION_ID          = MMV-AUTH-0002      scope ONE_SHOT
AUTHORIZATION_COMMIT      = a6748e704333248157fd0fe05d8b6357a81ca6ae
RUN_DRIVER_COMMIT         = 93d9a4768a387d1fd1ffe30deba1c24dffeb9206
EXECUTED                  = 2026-09-17

TERMINAL_CLASS            = D — PREDICTIVE RESPONSE UNRESOLVED
PROGRAMME_STATUS          = UNRESOLVED / LOW_POWER      TERMINAL
FAILURE_TYPE              = NONE
EVIDENCE_CEILING          = supported   (never confirmed)

PRIMARY_RETURN_TRIAL_SPENT = YES        RERUN_PERFORMED = NO
```

---

## §1 The three sealed statistics

One calendar-year block bootstrap, **one common draw set**, `B = 10,000`,
95 % percentile intervals, `RNG_SEED = 1963028087`.

| | statistic | point | 95 % interval | rule | result |
|---|---|---|---|---|---|
| **GATE 1** | mean monthly **GROSS** return | `+0.00016410` | `[-0.00424423, +0.00420519]` | lower > 0 STRICT | **FAIL** |
| **M1** | mean monthly **NET** return | `+0.00002419` | `[-0.00439365, +0.00407023]` | lower > 0 STRICT | **FAIL** |
| **M2** | annualised **NET Sharpe** | `+0.003056` | `[-0.527604, +0.547064]` | lower > +0.30 STRICT | **FAIL** |

Sharpe = `mean(monthly net) / sd(monthly net, ddof=1) × √12`, `rf = 0`.

`+0.00016410` per month is `+0.197 %` per year, and `+0.00002419` per month is
`+0.029 %` per year — the same disclosed point estimates × 12, not new
statistics.

---

## §2 Terminal classification — contract §K, first match wins

```
CLASS C  needs Gate-1 UPPER <= 0.        upper = +0.00420519  > 0   NOT MATCHED
CLASS D  needs the Gate-1 interval to span 0.
         lower = -0.00424423 <= 0 <= +0.00420519 = upper       ->   MATCHED
```

```
TERMINAL_CLASS   = D
PROGRAMME_STATUS = UNRESOLVED / LOW_POWER
FAILURE_TYPE     = NONE
```

Classes E, F and S are unreachable: every one of them requires Gate 1 to pass
first, and the lower endpoint is negative.

**What CLASS D says.** Over the sealed sample the 95 % interval for the mean
monthly gross MMV return **contains zero**. The evidence does not resolve the
sign of the predictive response. The interval is wide relative to the point
estimate — `±0.42 %` per month around a point of `+0.016 %` — which is the
`LOW_POWER` half of the label.

**What CLASS D does NOT say.** It does not falsify the mechanism. It does not
establish that macro state carries no information about these instruments. It
does not say the response is adverse — that would be CLASS C, and CLASS C was
not matched. It says the sealed design, on the sealed sample, cannot tell.

**CLASS D is terminal by §K.** No retuning, no rescue, no second look.

---

## §3 The exact eligible sample

```
canonical decision dates (contract §H)            218   2008-05-31 .. 2026-06-30
wrapper warm-up months carrying no book             4   2008-05-31, 2008-06-30,
                                                        2008-07-31, 2008-08-31
ELIGIBLE RETURN MONTHS                            214   2008-09-30 .. 2026-06-30
MAPPED_INSTRUMENT_N                                15
VNQ / RWX                                    NOT_MAPPED, absent from the book
missing / unexplained returns                       0
duplicate months                                    0
decision months carrying fewer than 15 weights      0
```

The four excluded months are **structural, not chosen**: `PORT_VOL_WINDOW_DAYS`
is 60, so the canonical portfolio-vol estimate needs 60 daily returns of the
MMV book itself before any leverage exists. Until it does, `leverage` is NaN,
the portfolio weight is NaN, and no position is held. They are the first four
months of the window and nothing later is excluded.

**The final return month is truncated.** The frozen daily panel ends
`2026-06-12`, so the `2026-06-30` return spans a partial month. Contract §H
forbids extending the window past the authoritative canonical price panel, and
the canonical convention keeps every month with a defined return, so the month
stands. It is 1 of 214.

Calendar-year blocks, 19 of them: 2008 carries 4 months, 2026 carries 6, the
other 17 carry 12 each.

---

## §4 Return alignment and execution convention — RECOVERED, NOT INVENTED

The sealed authority determines the return interval uniquely. The run driver
**recovers it from committed canonical code at run time** and refuses to
continue if the exact fragments are no longer there.

```
RETURN_ALIGNMENT      month-end close -> month-end close, label ME
                      src/signals.py::to_monthly  (last daily close in the
                      calendar month, labelled at the calendar month-end)
                      src/performance.py::monthly_asset_returns = pct_change()

EXECUTION_CONVENTION  the position held during month M is the portfolio weight
                      decided at month-end M-1
                      src/portfolio.py::positions_from_weights -> shift(1)
                      "decide at close, execute from the next session onward"

INFORMATION_CUTOFF    15:45:00 America/New_York on the decision date (§C),
                      which precedes both the ~16:00 close and the execution
```

Verified mechanically at phase 3: `held(M) == port_weight(M-1)` for all 218
months, exactly.

**Causality was tested, not asserted.** The entire wrapper — asset vol, asset
weights, portfolio vol, leverage, portfolio weights — was recomputed on price
panels truncated at **2011-06-30, 2015-12-31, 2019-09-30 and 2023-03-31** and
compared with the full-sample run. Every value up to the truncation date is
**bitwise identical**. A wrapper that peeked at future prices could not survive
that test. This is what "the volatility input uses only information available at
decision time" means mechanically.

---

## §5 Cost and net accounting

```
ONE_WAY_COST          2.0 bps per unit turnover   (config.py:196, contract §G)
AGGREGATE_TURNOVER    149.7011  over 214 months   mean 0.699538 / month
AGGREGATE_COST        0.029940  over 214 months   mean 0.00013991 / month
```

`gross mean − cost mean = 0.00016410 − 0.00013991 = 0.00002419 = net mean.`
The net series reconciles with the gross series and the cost series exactly.

**Reconciled against the canonical implementation.** `gross`, `turnover` and
`net` were recomputed by `src/performance.py::portfolio_returns` and compared:

```
gross   vs canonical                    max |dev| = 0.000e+00   (bit-identical)
gross   vs canonical at ZERO cost       max |dev| = 0.000e+00
turnover vs canonical                   max |dev| = 8.882e-16
net     vs canonical                    max |dev| = 6.939e-18
```

The two non-zero deviations are one ULP: `sum(axis=1)` and
`sum(axis=1, min_count=1)` are the same formula down different pandas reduction
paths. The identity bound is `1e-12` — about nine orders of magnitude below a
monthly return, and **not a research threshold**: no gate, class or verdict
reads it.

**Cost is applied once.** The gross series computed at 0 bps and at 2 bps is
bit-identical, so no cost is inside gross; cost enters only at `net = gross −
cost`.

**Entry-trade boundary, disclosed.** The canonical `positions.diff()` is
undefined in the first held month (`2008-09-30`) because there is no prior held
book, which would leave `net` NaN. The sealed S2 rule
`engine/risk.py::turnover` treats an absent book as **flat**, so the entry trade
is charged in full — `Σ|w|` — rather than dropped. That is the conservative
direction, it affects exactly one month of 214, and it is the only month where
the two implementations differ at all.

---

## §6 Inference

```
METHOD      calendar-year block bootstrap over FROZEN monthly strategy tuples
BLOCKS      19 complete calendar years, resampled WITH REPLACEMENT
B           10,000
INTERVALS   95 % percentile (2.5 / 97.5)
RNG         numpy PCG64 via SeedSequence(1963028087)
SEED        DERIVED: int(S1 seal manifest sha256[:8], 16) = int('75016e77', 16)
DRAWS       ONE draw matrix of shape (10000, 19) serves Gate 1, M1 and M2
```

The PIT macro signal was computed **once, causally, on the true chronology**.
No fictional ALFRED history was rebuilt inside any replicate — the bootstrap
sees frozen `(year, gross, net)` tuples and nothing else.

`NO HAC · NO Newey-West · NO second bootstrap · NO monthly IID bootstrap.`
Valid replicates: 10,000 / 10,000 for all three statistics.

---

## §7 The sealed signal is the Gate-0.5 signal

Phase 2 rebuilt the sealed MMV directions by re-invoking the **committed
Gate-0.5 constructor verbatim** and checked the result against the Gate-0.5
structural fingerprint:

```
decision months 218 · defined cells 3270 · undefined 0 · flat 718
legs defined    G = 218   I = 218   P = 218
```

All five reproduce exactly. The S3 book is built from the same directions over
the same sample as the accepted Gate 0.5 run.

**Gate 0.5 was not rerun, recomputed or reinterpreted.** The accepted PASS
(`1313/3270` = 40.152905 %) was READ from the committed artifact.
`MMV-AUTH-0001` remains CONSUMED. The S3 driver reads **no canonical TSMOM sign
at all**, so it could not have recomputed the agreement statistic even by
accident.

---

## §8 Pinned inputs

All eleven reproduce their pinned hashes exactly. A mismatch is a structural
stop, never a substitution.

| sha256 | file |
|---|---|
| `4bad9f0bcdb7e4991ab920d12e24a60f4d237205e5a43af693a8dadadb56b225` | `research/extensions/mmv/MMV_PREREGISTRATION.md` |
| `75016e778ad58e8fe16e4833cf91c19eb52448b4d42138ab265460f371e8c0d5` | `research/extensions/mmv/MMV_SEAL_MANIFEST.md` |
| `ae34bf1e192c4355fb71136a3e3017dfd07525ac8e48d7d3ea102130fa6a11da` | `research/extensions/mmv/MMV_POLICY_ANNOUNCEMENT_SCHEDULE.csv` |
| `3f53f959e399e21a060c6c7ab04392b82950c916826a1c964472d8c78682ddd9` | `data/mmv/INDPRO.observations.realtime.json` |
| `c773c5681807fe0057dd66814aa18bfc03b8c0201be57a50f425b48e7c471bd6` | `data/mmv/PAYEMS.observations.realtime.json` |
| `75c3c36306c109b11683d808471b30aa8061a2dfc0a4141a6668e6fe8b9ad2f4` | `data/mmv/CPILFENS.observations.realtime.json` |
| `fa154e01ec597070729b5489ee4f8ed0e588add30c70d33196d7bf3c8069173f` | `output/monthly_signal_panel.csv` |
| `3d2a7a56dbd92d4ff8138cfd894c87f5ac5ac088a11165db870673e0c05c3c31` | `data/close_prices_raw.csv` |
| `1fa8df006574199cef2a6153f57f354d6fa93475b07c5c576036cebb09b6c3d8` | `research/extensions/mmv/gate05/MMV_GATE05_RESULT.json` |
| `05e20ef8740ccd55b051c4be31b0b85e1b38e9479ef703009037dcd1d8062440` | `research/extensions/mmv/MMV_GATE05_RESULT.md` |
| `029a5618182a9043680f14102b57de25386ce6bf87569c717d3520185fbee713` | `research/extensions/mmv/MMV_GATE05_AUDIT.md` |

Common risk wrapper, adopted unchanged from the canonical implementation and
read from `config.py` at call time rather than copied: 60-day asset vol, 10 %
asset vol target, ±2 asset cap, equal-weight live assets, 10 % portfolio vol
target, 3× gross leverage cap.

---

## §9 What was NOT computed

Not computed and withheld — **not computed at all**:

```
per-ETF return rankings            NO      per-leg PnL                   NO
growth-only / inflation-only /             best or worst years / months  NO
  policy-only PnL                  NO      recession / crisis cells      NO
drawdown                           NO      hit rate                      NO
rolling Sharpe                     NO      alternative start dates       NO
alternative lookbacks              NO      alternative costs             NO
alternative mappings               NO      alternative series            NO
first-release concordance          NO      Gate 0.5 rerun                NO
```

The first-release concordance diagnostic (§L.1) remains **CLOSED**. It has no
promotion, rescue or kill power and is not required for this verdict.

---

## §10 NO RESCUE

After this result, none of the following may be changed, tried, or reported as
an alternative: `CPILFENS` · core PCE · headline CPI · `FEDFUNDS` · `DGS2` ·
the growth aggregation · LQD or GLD treatment · adding VNQ/RWX · the 80 % Gate
0.5 threshold · the cost · the `+0.30` Sharpe target · the bootstrap · the
sample · the execution timing · component selection.

**Any such work requires a NEW LINEAGE** with its own preregistration and seal,
and that is an Owner decision, not a continuation of this one.

Under §O a CLASS D result establishes nothing about causation, nothing about
other information concepts, series families, mappings or horizons, and nothing
about what a different design would have found.

```
EVIDENCE_CEILING = supported.  NEVER confirmed.  NEVER independently confirmed.
```

---

## §11 Artifacts

```
MACHINE RESULT  research/extensions/mmv/s3/MMV_S3_RESULT.json
                sha256 70fc6f91ddcc9ce4888c76c4016d32684c8c273c9d9348754814a5860c306a5e
RUN DRIVER      research/extensions/mmv/mmv_s3_run.py          commit 93d9a47
AUTHORIZATION   ops/EXECUTION_AUTHORIZATIONS.md  MMV-AUTH-0002 commit a6748e7
```

```
RETURN_OUTCOME_ACCESSED    = YES
PRIMARY_RETURN_TRIAL_SPENT = YES   (CTA-EDGE-04-MMV composite, m = 1)
HISTORICAL_GATE05_RERUN    = NO
RERUN_PERFORMED            = NO
READY_FOR_CONTROLLER_REVIEW = YES
```
