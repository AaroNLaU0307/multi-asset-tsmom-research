# CTA-EDGE-04-MMV — POST-GATE-0.5 STATIC AUDIT

```
POST_GATE05_AUDIT_STATUS = PASS        (15 / 15 checks)
AUDIT TYPE               = STATIC / ARTIFACT ONLY
DATE                     = 2026-09-17
VALIDATOR                = research/extensions/mmv/mmv_gate05_audit.py

HISTORICAL_GATE05_RERUN_PERFORMED = NO
AGREEMENT STATISTIC RECOMPUTED    = NO
RETURNS ACCESSED                  = NO
NEW AUTHORIZATION CREATED         = NO
MMV-AUTH-0001                     = still CONSUMED
```

---

## §1 The primary question, answered three independent ways

**Did the committed historical run convert the canonical TSMOM composite to
`sign(composite)` before the Gate 0.5 equality comparison?**

```
CANONICAL_COMPOSITE_SIGN_NORMALIZED_BEFORE_GATE05 = YES
GATE05_REPRESENTATION_STATUS                      = VALID
```

### 1.1 Traced code path — committed state, not the working tree

| step | location | code |
|---|---|---|
| canonical panel reader | `mmv_gate05_run.py:336` | `def canonical_signs(dec)` |
| file open | `mmv_gate05_run.py:337` | `with open(PANEL, encoding="utf-8") as fh:` |
| empty cell | `mmv_gate05_run.py:346` | `out[(d, inst)] = UNDEFINED` |
| parsed value type | `mmv_gate05_run.py:349` | `v = Fraction(cell)` — exact rational, never float |
| **normalization** | **`mmv_gate05_run.py:350`** | **`out[(d, inst)] = (v > 0) - (v < 0)`** |
| gate input construction | `mmv_gate05_run.py:520` | `tsmom, tsmom_undef = canonical_signs(dec)` |
| handed to the gate | `mmv_gate05_run.py:432` | `out = gate05.evaluate(raw, tsmom)` |
| type guard | `engine/gate05.py:36, 63, 66` | `VALID_SIGNS = (-1, 0, 1)` · `_check_sign` raises |
| guard applied to canonical | `engine/gate05.py:102` | `t = _check_sign(tsmom_signs.get(key, UNDEFINED), …)` |
| **exact equality** | **`engine/gate05.py:110`** | **`if m == t:`** |

`(v > 0) - (v < 0)` is the three-valued sign written inline: strictly positive →
`+1`, strictly negative → `−1`, zero → `0`. It is applied at line 350, one line
after the parse and 170 lines before the value reaches the gate. There is no
path from the CSV cell to the comparison that skips it — `canonical_signs()` is
the only reader of the panel's instrument columns, and the value it returns is
the only thing handed to `gate05.evaluate`.

### 1.2 Synthetic representation test — authorized by §3

```
input   ['-1', '-0.75', '-0.5', '-0.25', '0', '0.25', '0.5', '0.75', '1']
output  [ -1,   -1,      -1,     -1,      0,    1,      1,     1,      1 ]
expect  [ -1,   -1,      -1,     -1,      0,    1,      1,     1,      1 ]
SYNTHETIC_NORMALIZATION_TEST = PASS
```

Run with the **exact expression from the committed line 350**, over the full
composite alphabet the panel can carry. Also verified: the sealed gate
**accepts** a normalized sign and **rejects** a raw composite of `1/2` with
`ContractViolation`.

### 1.3 The impossibility argument — decisive, and it recomputes nothing

```
fractional canonical cells inside the decision window,
  over the 15 mapped instruments             : 1167
eligible cells the completed run reported    : 3270
sealed gate behaviour on a non-ternary value : ContractViolation (raises)
```

`engine/gate05.py:102` passes **every** canonical value through `_check_sign`
before the comparison at line 110, and `_check_sign` raises on anything outside
`{-1, 0, +1}`. There are **1167 fractional composite cells** inside the audited
window over the mapped instruments. Had the run compared raw composites, the
guard would have raised on the first of them and **no result artifact could
exist**.

A completed run that reported 3270 eligible cells is therefore possible **only**
with sign normalization applied first. This holds without trusting the trace or
the synthetic test: it follows from the committed guard and the existence of the
artifact.

```
REPORTED_RESULT_STATUS = VALID_PENDING_CONTROLLER_ACCEPTANCE
```

1313/3270 = 40.152905 % was generated from **sign-vs-sign** comparison:
MMV `raw(i,t) ∈ {−1,0,+1}` against `sign(canonical composite) ∈ {−1,0,+1}`, with
`0 == 0` counted as agreement and `0` vs `±1` as disagreement. No new historical
diagnostic was produced by this audit.

---

## §2 Collision reconciliation

```
COLLISION_RECONCILIATION_STATUS = COMPATIBLE
```

### 2.1 The six S1 collision dates

| date | FOMC event? | target/range change? | announcement time status | Gate-0.5 category | policy value used | reason |
|---|---|---|---|---|---|---|
| 2013-07-31 | YES | NO | NOT_ESTABLISHED | C | 1/8 | no target change at this meeting, so the same-day rule has no new value to gate |
| 2014-04-30 | YES | NO | NOT_ESTABLISHED | C | 1/8 | as above |
| 2018-01-31 | YES | NO | VERIFIED 2:00 p.m. EST | C | 11/8 | time is published, but nothing changed |
| **2019-07-31** | YES | **YES** | VERIFIED 2:00 p.m. EDT | **A** | 17/8 | 14:00 ≤ 15:45, newly announced target admitted |
| 2024-01-31 | YES | NO | VERIFIED 2:00 p.m. EST | C | 43/8 | time is published, but nothing changed |
| 2024-07-31 | YES | NO | VERIFIED 2:00 p.m. EDT | C | 43/8 | as above |

```
A = 1   B = 0   C = 5        A + B + C = 6
```

Policy values are midpoints of the administered range, in exact rational form
(`1/8` = 0.125 %, `43/8` = 5.375 %).

### 2.2 Why "1 verified / 2 unknown" and "1 verified / 0 unknown / 5 no-change" are compatible

**They count different populations, not different denominators of one
population.**

```
POLICY FREEZE, "cutoff collisions" = 3
  population: cutoffs (DECISION *or* LAGGED) that coincide with a
              target-CHANGE announcement
  members:    2007-10-31  LAGGED_ONLY   NOT_ESTABLISHED
              2008-04-30  LAGGED_ONLY   NOT_ESTABLISHED
              2019-07-31  DECISION      VERIFIED
  -> 1 verified, 2 unknown

GATE 0.5, "six collision accounting" = 6
  population: the six PINNED S1 collisions — canonical month-end DECISION
              dates that are FOMC announcement dates, whether or not the
              target changed
  -> A=1 verified change, B=0 unknown-time change, C=5 no change
```

The two sets **intersect in exactly one member**, 2019-07-31, and it is
`VERIFIED` in both. That is the only date that is simultaneously a decision
date, an FOMC announcement date, and a target change.

The two `NOT_ESTABLISHED` entries cannot appear in the six for a structural
reason, not a bookkeeping one: **2007-10-31 and 2008-04-30 both fall before the
decision window opens on 2008-05-31**, so neither is a decision date at all.
They enter the study only as the `t − 12 months` cutoff of a later decision.

`B = 0` within the six is therefore not a disagreement with "2 unknown". It says
that among the six decision-date collisions, **no target changed with an
unestablished time** — three of the five class-C meetings do publish a 2:00 p.m.
time and simply changed nothing, and two publish no time and also changed
nothing. A meeting that changes nothing offers the same-day rule no new value to
admit or withhold.

### 2.3 The two lagged cutoffs

```
LAGGED_2007_10_31_STATUS = SEPARATE LAGGED-CUTOFF EVENT
                           NOT one of the six S1 collision dates
                           target change effective 2007-10-31,
                           announcement time NOT_ESTABLISHED -> PRIOR TARGET
                           it is the t-12m cutoff of the 2008-10-31 decision

LAGGED_2008_04_30_STATUS = SEPARATE LAGGED-CUTOFF EVENT
                           NOT one of the six S1 collision dates
                           target change effective 2008-04-30,
                           announcement time NOT_ESTABLISHED -> PRIOR TARGET
                           it is the t-12m cutoff of the 2009-04-30 decision
```

Both were surfaced during the policy-schedule freeze precisely because the
original six-date analysis intersected FOMC dates with **decision** dates only,
while the sealed policy leg also reads a cutoff twelve months earlier. No policy
rule was changed then and none is changed now.

---

## §3 Authorization / consumption guard

```
CONSUMPTION_GUARD_WORKTREE_BLOCKS       = YES
CONSUMPTION_GUARD_LIFECYCLE_SCOPE_FIXED = YES
RERUN_CURRENTLY_BLOCKED                 = YES
```

Verified statically, without executing the driver:

- **`consumed_ids()`** (`mmv_authorization.py:103`) unions committed records with
  the **working tree**, while grants come only from `read_committed`. Blocking
  does not require a commit; granting does.
- **`_scoped`** retains a LIFECYCLE record that carries **no** `lineage` field —
  the defect that previously dropped the consumption record entirely and made
  the guard fail open — while still rejecting a record that declares a
  *different* lineage, so the relaxation widened nothing.
- Live status: *"every CTA-EDGE-04-MMV grant is CONSUMED (['MMV-AUTH-0001']);
  consumption is permanent and no retry is authorized."*
- A **second, independent** layer: the driver refuses outright when a result
  artifact already exists (`mmv_gate05_run.py:509`).

---

## §4 Exposure accounting

```
PNL_FREE_EXPOSURE_STATUS = VALID_GATE05_EXPOSURE
exposure class           = PNL_FREE_STRUCTURAL_EXPOSURE  (controller's term)
RETURN_TRIAL_SPENT       = NO
RETURN_OUTCOME_ACCESSED  = NO
```

Recorded as **row 56** of `ops/EXPOSURE_LEDGER.md` under the existing convention.
The ratified `classification` token is **`REVEALED_AGGREGATE`** (granularity
`AGGREGATE`): a pooled aggregate statistic about historical positions was
revealed, and no target performance metric was. `REVEALED_TARGET_METRIC` would
have been wrong — no return, cost, Sharpe or drawdown exists.

No trial was invented and nothing was written to
`research/extensions/TRIAL_LEDGER.md`. The contract's `m = 1` primary trial is
the **Gate-1 return test**, which remains unspent and unauthorized.

---

## §5 Scope of this audit

Nothing in §10's prohibition list was performed: no Gate 0.5 rerun, no corrected
agreement computation, no per-instrument or per-leg agreement, no calendar
agreement map, no first-release diagnostic, no returns, PnL, Sharpe, bootstrap,
Gate 1, M1 or M2.

The result artifact was neither deleted nor overwritten; it stands as committed
at `8a30ec3`, sha256
`1fa8df006574199cef2a6153f57f354d6fa93475b07c5c576036cebb09b6c3d8`.

The PASS **remains pending controller acceptance**. This audit establishes only
that the reported statistic is a valid sign-vs-sign measurement under the sealed
contract — it does not accept the result, and it does not authorize a return
test.
