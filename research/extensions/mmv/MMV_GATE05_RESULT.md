# CTA-EDGE-04-MMV — GATE 0.5 RESULT

```
RUN_ID            = MMV-GATE05-20260917-01
RUN_TYPE          = HISTORICAL_PNL_FREE_SEPARABILITY
AUTHORIZATION     = MMV-AUTH-0001   (ONE_SHOT_SINGLE_PNL_FREE_GATE05_RUN)
AUTHORIZED BY     = Owner execution decision relayed by Aaron
EXECUTIONS        = 1     RERUN_PERFORMED = NO
RNG_SEED          = NONE  (deterministic: exact integer counting, no resampling)
DATE              = 2026-09-17
```

```
GATE05_RESULT = PASS
```

---

## §1 The single primary statistic

```
POOLED_EXACT_SIGN_AGREEMENT = 1313 / 3270 = 40.152905 %

SEALED THRESHOLD            = agreement / eligible >= 4/5, INCLUSIVE
                              (kill at >= 80.0 %)
1313/3270 < 4/5             -> NO KILL
```

Evaluated in exact rational arithmetic, not from a rounded percentage. The
displayed figure is a presentation of `Fraction(1313, 3270)`; the decision
compared that fraction directly against `Fraction(4, 5)`.

```
eligible cells            3270
agreement cells           1313
excluded, unmapped        0     (VNQ/RWX were never constructed)
excluded, MMV undefined   0
excluded, canonical undef 0
```

`excluded_unmapped = 0` is not an empty filter. VNQ and RWX are **absent from
the position matrix entirely** — `votes.raw_direction` raises for them — so
there was never an unmapped cell to exclude. That is the sealed
`NOT_MAPPED ≠ signal 0` requirement enforced upstream of the gate rather than at
it.

---

## §2 What this result does and does not mean

**It means** the sealed MMV raw position states are **not** a restatement of the
canonical TSMOM control. They agree on 40.2 % of eligible instrument-months,
well below the 80.0 % kill boundary, so the lineage is not spending a
historical-return trial on a sleeve that merely re-expresses the core book in
macro vocabulary.

**It does NOT mean any of the following**, and no later document may say
otherwise:

```
NOT: alpha exists                      NOT: diversification exists
NOT: predictive power exists           NOT: positive return exists
NOT: the macro mechanism is supported  NOT: MMV improves canonical TSMOM
```

Gate 0.5 is a **PnL-free separability screen**. It compares directions and
nothing else. A strategy can be perfectly separable from the control and still
be worthless; this gate is incapable of distinguishing those cases and was never
intended to.

```
HISTORICAL RETURNS REMAIN CLOSED.
A Gate 0.5 PASS is NOT a return authorization.
```

---

## §3 Structural counts

```
decision months            218      2008-05-31 .. 2026-06-30
mapped instruments          15      VNQ present: NO   RWX present: NO
instrument-months         3270      = 218 x 15, no duplicates

macro legs defined         G = 218 / 218
                           I = 218 / 218
                           P = 218 / 218

MMV defined cells         3270
MMV undefined cells          0      (no sealed missing-leg condition arose)
MMV zero (flat) cells      718      a real position state, counted on both
                                    sides of the gate and never discarded
canonical undefined cells    0
```

Every one of the 218 decision dates carried all three legs. The sealed
missingness machinery was therefore exercised but never triggered: the single
known `CPILFENS` hole at 2025-10-01 never fell on a lag the transform reads,
because the leg reads the newest **valued** reference month rather than a fixed
calendar slot.

### 3.1 Point-in-time behaviour actually observed

Newest reference month available at the decision date, in months of lag:

| series | 1 month | 2 months | 3 months |
|---|---:|---:|---:|
| INDPRO | 216 | 1 | 1 |
| PAYEMS | 216 | 2 | — |
| CPILFENS | 217 | 1 | — |

The normal case is a one-month lag. The handful of longer lags are real
publication gaps as seen at the decision date — they are what point-in-time
reconstruction is *for*, and they were not smoothed over.

```
SAME-DAY VINTAGES EXCLUDED = { INDPRO: 1 }
```

On exactly one decision date an INDPRO vintage carried that same date. No
authoritative release **clock time** exists for that release, so the sealed rule
in §C.1 — *"Same-day vintage whose release time cannot be authoritatively
established → use the PRIOR eligible vintage. Do not guess."* — applied and the
prior vintage was used. The rule bit once, conservatively, and is recorded.

---

## §4 Pre-run accounting

### 4.1 Six-collision classification

```
A  target/range change, announcement time VERIFIED       = 1
B  target/range change, announcement time NOT_ESTABLISHED = 0
C  FOMC/month-end collision, NO new target value          = 5
                                                    A+B+C = 6
```

| collision | class |
|---|---|
| 2013-07-31 | C |
| 2014-04-30 | C |
| 2018-01-31 | C |
| **2019-07-31** | **A** — 2:00 p.m. EDT ≤ 15:45, newly announced target eligible |
| 2024-01-31 | C |
| 2024-07-31 | C |

The two collisions whose official pages say only *"For immediate release"* —
2013-07-31 and 2014-04-30 — are **class C**: they are no-change meetings, so no
new target value existed for the unestablished time to gate. The conservative
fallback was available and was simply not needed. Bookkeeping only; no rule was
introduced.

### 4.2 Policy coverage through sample end

```
POLICY_COVERAGE_COMPLETE = YES
last policy CHANGE  2025-12-11   final regime carries forward to 2026-06-30
defined at all 218 decision cutoffs AND all 218 lagged (t-12m) cutoffs
```

The last change date is not the end of coverage. Verified mechanically at every
required cutoff, both current and lagged, rather than inferred from the final
event date.

```
12-MONTH LAG READING: the canonical-month-end reading and the calendar-day
reading of "t - 12 months" agree on all 218 dates, so the month-end convention
introduces no ambiguity and no choice was needed.
```

### 4.3 The one canonical direction input

```
path        output/monthly_signal_panel.csv
sha256      fa154e01ec597070729b5489ee4f8ed0e588add30c70d33196d7bf3c8069173f
dimensions  402 rows x 17 instrument columns
coverage    1993-01-31 .. 2026-06-30   (decision window 2008-05-31 .. 2026-06-30)
coding      sign(canonical TSMOM composite)
```

The panel carries the canonical **composite** in
`{−1, −0.75, −0.5, −0.25, 0, +0.25, +0.5, +0.75, +1}` — the mean of the four
sealed lookback votes — not a pre-reduced ±1 direction. The canonical position
is that composite scaled by a **strictly positive** vol-target scalar, so the
canonical position *direction* is `sign(composite)`. An empty cell is UNDEFINED,
never 0.

Only the 15 mapped columns were read. The VNQ and RWX columns of this file were
never opened. Canonical TSMOM was not reconstructed, retuned or modified.

---

## §5 Outcome firewall

```
HISTORICAL_MMV_FEATURE_COMPUTED       = YES   (authorized, first time)
HISTORICAL_MMV_POSITIONS_COMPUTED     = YES   (authorized, first time)

RETURN_OUTCOME_ACCESSED               = NO
PNL_COMPUTED                          = NO
SHARPE_COMPUTED                       = NO
BOOTSTRAP_RUN                         = NO
GATE1_RUN · M1_RUN · M2_RUN           = NO
FIRST_RELEASE_DIAGNOSTIC_RUN          = NO
```

The run module opens no price, return, cost or performance file. Its only
canonical input is the sealed monthly **signal** panel, read for direction cells
alone.

### 5.1 Diagnostics deliberately not computed

```
PER_INSTRUMENT_AGREEMENT_COMPUTED     = NO
PER_LEG_AGREEMENT_COMPUTED            = NO
CALENDAR_PERIOD_AGREEMENT_COMPUTED    = NO
```

These are preregistered as non-promotional and remain so. They were **not
computed and withheld — they were not computed at all**, so no one holds a
best/worst instrument ranking, a per-leg breakdown, or a calendar map of where
agreement was unusual. Nothing about them was needed for this kill decision, and
not producing them is the cheapest way to keep a later narrative from being
built on them.

---

## §6 Inputs, all verified before execution

| sha256 | path |
|---|---|
| `4bad9f0bcdb7e4991ab920d12e24a60f4d237205e5a43af693a8dadadb56b225` | `research/extensions/mmv/MMV_PREREGISTRATION.md` |
| `75016e778ad58e8fe16e4833cf91c19eb52448b4d42138ab265460f371e8c0d5` | `research/extensions/mmv/MMV_SEAL_MANIFEST.md` |
| `ae34bf1e192c4355fb71136a3e3017dfd07525ac8e48d7d3ea102130fa6a11da` | `research/extensions/mmv/MMV_POLICY_ANNOUNCEMENT_SCHEDULE.csv` |
| `3f53f959e399e21a060c6c7ab04392b82950c916826a1c964472d8c78682ddd9` | `data/mmv/INDPRO.observations.realtime.json` |
| `c773c5681807fe0057dd66814aa18bfc03b8c0201be57a50f425b48e7c471bd6` | `data/mmv/PAYEMS.observations.realtime.json` |
| `75c3c36306c109b11683d808471b30aa8061a2dfc0a4141a6668e6fe8b9ad2f4` | `data/mmv/CPILFENS.observations.realtime.json` |
| `fa154e01ec597070729b5489ee4f8ed0e588add30c70d33196d7bf3c8069173f` | `output/monthly_signal_panel.csv` |

```
S1 seal commit            cdb01fdc903e97671c3ef50fde6875628ca39ac8
S2 build commit           dc2817b99f048f561f1db55f998e24ff2193df10
policy freeze commit      d52883f230d1961c6c1f23b1dbb63402177e5dd3
authorization commit      8d37746629f7cbaa741eaa13907e118eb1a35537

PRE-RUN REGRESSION        S2 synthetic 151/151 · S2 parser 32/32 ·
                          policy schedule 33/33 · sealed S1 commit 38/38
```

Machine-readable result: [`gate05/MMV_GATE05_RESULT.json`](gate05/MMV_GATE05_RESULT.json)
sha256 `1fa8df006574199cef2a6153f57f354d6fa93475b07c5c576036cebb09b6c3d8`.

---

## §7 Status after this run

```
GATE05_RESULT      = PASS
AUTHORIZATION      = CONSUMED, permanently
PROGRAMME_STATUS   = still ACTIVE at S3; NOT promoted, NOT falsified
EVIDENCE_CEILING   = supported
```

MMV survives the pre-PnL position-separability gate. **No return test is
authorized**, and Gate 1, M1, M2, the bootstrap and the first-release
concordance cell all remain closed pending separate controller authorization.

One cosmetic note for reproducers: the console line for the threshold printed a
literal `%%`. The durable artifacts carry the threshold correctly, the decision
used exact fractions, and the executed driver was left unmodified because
rerunning it is not authorized.
