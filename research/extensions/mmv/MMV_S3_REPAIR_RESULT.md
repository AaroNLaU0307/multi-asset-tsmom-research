# CTA-EDGE-04-MMV — S3 PRIMARY-SAMPLE CORRECTION RESULT

**THIS RESULT SUPERSEDES THE PRIOR PRIMARY VERDICT FOR DECISIONAL PURPOSES.**

```
REPAIR_STATUS             = PASS
REPAIR_RUN_ID             = MMV-S3-REPAIR-20260917-01
REPAIR_AUTHORIZATION_ID   = MMV-AUTH-0003    scope ONE_SHOT
REPAIR_AUTH_COMMIT        = 1734dcb37bbe8f6e1202fe91f6917e6af712c941
RUN_DRIVER_COMMIT         = cd41614781b4d56b1bf6c33f01ef86a95b8bfa5b

PARENT_RUN                = MMV-S3-20260917-01
PARENT_RESULT_STATUS      = INVALID_PRIMARY_SAMPLE
PARENT_DECISIONAL_STATUS  = NONDECISIONAL     (preserved unmodified)

TERMINAL_CLASS            = D — PREDICTIVE RESPONSE UNRESOLVED
PROGRAMME_STATUS          = UNRESOLVED / LOW_POWER      TERMINAL
FAILURE_TYPE              = NONE
EVIDENCE_CEILING          = supported   (never confirmed)

TRIAL_FAMILY = F-MMV · m = 1 · TRIAL_COUNT_INCREMENT = 0
OLD_RESULT_DECISIONAL = NO      NEW_RESULT_DECISIONAL = YES
```

---

## §1 MMV-OD-8 — the authority is pre-existing, not new

```
MMV_OD_8_RECORDED          = B_EXCLUDE
LOCKBOX_AUTHORITY_VERIFIED = YES
NEW_SCIENTIFIC_CHOICE      = NO
```

`research/extensions/LOCKBOX_PROCEDURE.md` §2.1 was written **2026-09-08**, nine
days before the MMV seal of 2026-09-17. It verifies the frozen ETF panel's
boundary at **`2026-06-12`** from bytes, and states of the June 2026 monthly row:

> a complete label over an incomplete period

Its rule gives an evaluation exactly two paths:

```
(a) TRUNCATE the terminal monthly row and state so
(b) DECLARE in the preregistration that a partial terminal month is included,
    and why
```

The sealed MMV contract records the boundary in §P and **never exercises (b)** —
`grep` for *partial*, *terminal* or *incomplete* in the preregistration returns
nothing bearing on it. Therefore **(a) binds.**

**The parent run did neither.** It included the row and *stated that it had*,
which reads like (a) but is not: (a) requires truncation. That is the entire
defect, and it is the only thing this correction repairs.

§2.1 also calls this *"the first item every new candidate's A2 challenge should
check"*. It was a documented trap and the parent run walked into it.

---

## §2 The corrected sample — exactly one row

```
ORIGINAL_ELIGIBLE_MONTH_N  = 214      2008-09-30 .. 2026-06-30
REPAIRED_ELIGIBLE_MONTH_N  = 213      2008-09-30 .. 2026-05-31
REMOVED_RETURN_ROWS        = {2026-06-30}
ADDED_RETURN_ROWS          = none
all earlier eligible months identical, in the original order = YES
```

The 4-month wrapper warm-up (`2008-05-31 .. 2008-08-31`) is unchanged, and
**the 218-date MMV decision grid is NOT altered**. `2026-06-30` remains a valid
decision-state date; only its *return* observation is ineligible.

### The guard is structural, not a hard-coded date

```
A month M is eligible only if the authoritative price panel contains a date
STRICTLY AFTER M's last calendar day.
```

That is what establishes completeness: if the panel continues past M, then the
last price observed inside M necessarily *is* M's final trading close. A panel
that stops inside M cannot establish it by any inspection of M's own rows, so M
**fails closed**. The rule names no date and would exclude a different month
unprompted if the panel were re-frozen earlier.

What the run recorded for the excluded month — the reason, not just the filter:

```
EXCLUDED  2026-06-30
   reason                  the panel does not continue past this month, so its
                           final trading close is NOT established by the data
   authoritative last px   2026-06-12
   canonical month end     2026-06-30   (18 calendar days later)
   primary_return_2026_06 = INELIGIBLE
```

---

## §3 The repaired primary statistics

One calendar-year block bootstrap, **one common draw set**, `B = 10,000`,
95 % percentile intervals, `RNG_SEED = 1963028087` — **all unchanged from the
parent run.**

| | statistic | point | 95 % interval | rule | result |
|---|---|---|---|---|---|
| **GATE 1** | mean monthly **GROSS** return | `+0.00014275` | `[-0.00428624, +0.00420283]` | lower > 0 STRICT | **FAIL** |
| **M1** | mean monthly **NET** return | `+0.00000230` | `[-0.00443109, +0.00406748]` | lower > 0 STRICT | **FAIL** |
| **M2** | annualised **NET Sharpe** | `+0.00029` | `[-0.531249, +0.545330]` | lower > +0.30 STRICT | **FAIL** |

```
AGGREGATE_TURNOVER = 149.5821   mean 0.702263 / month
AGGREGATE_COST     = 0.029916   mean 0.00014045 / month
```

`gross mean − cost mean = 0.00014275 − 0.00014045 = 0.00000230 = net mean.`

Reconciled against `src/performance.py`: gross **bit-identical**, turnover
`8.882e-16`, net `6.939e-18` — one ULP, under the `1e-12` numerical-identity
bound, which is not a research threshold.

---

## §4 Classification applied FROM SCRATCH

The parent's class was **not** carried forward. §K was re-run on the repaired
intervals:

```
CLASS C  needs Gate-1 UPPER <= 0.        upper = +0.00420283  > 0   NOT MATCHED
CLASS D  needs the Gate-1 interval to span 0.
         lower = -0.00428624 <= 0 <= +0.00420283 = upper       ->   MATCHED
```

```
TERMINAL_CLASS   = D — PREDICTIVE RESPONSE UNRESOLVED
PROGRAMME_STATUS = UNRESOLVED / LOW_POWER
FAILURE_TYPE     = NONE
```

Classes E, F and S remain unreachable: each requires Gate 1 to pass first.

**The class is the same letter the invalid run reported, and that is a
coincidence of arithmetic, not a carry-forward.** The invalid run's D is
withdrawn and has no standing; this D is derived independently on the valid
sample. Removing one month of 214 moved the gross mean by `-2.1e-05` and every
interval endpoint by less than `5e-05` — far too little to cross a boundary that
the point estimate misses by two orders of magnitude.

**What CLASS D says.** The 95 % interval for the mean monthly gross return
contains zero. The evidence does not resolve the sign of the predictive
response. The interval is `±0.42 %` per month around a point of `+0.014 %` —
the `LOW_POWER` half of the label.

**What it does not say.** It does not falsify the mechanism, it does not show
the response is adverse (that would be CLASS C, not matched), and it establishes
nothing about other information concepts, series families, mappings or horizons.
**CLASS D is terminal under §K.**

---

## §5 Why only one row could have changed

```
DRIVER_DIFF_AUDIT       = PASS
OUTCOME_AFFECTING_DIFFS = TERMINAL_ROW_ONLY
```

The repair driver does not reimplement any scientific step. It **imports the
committed parent driver and reuses its functions as the same objects**. The
parent's `phase4` already takes the eligible-month index as a *parameter*, so
correcting the sample required **no edit to any scientific function** — only a
different value passed in.

Three mechanical guards, all run before execution:

```
1. FROZEN BYTES        14 / 14 files byte-identical to their bytes at the
                       parent-run commit: the parent driver, src/performance.py,
                       src/portfolio.py, src/sizing.py, src/signals.py,
                       config.py, all seven sealed engine/ modules and the
                       Gate-0.5 driver.

2. REUSE IDENTITY      9 scientific functions checked by OBJECT IDENTITY against
                       the parent module — build_book, classify, load_prices,
                       phase1, phase2, phase3, phase4, phase5, sharpe. A later
                       edit that shadows one locally becomes a hard stop.

3. NOTHING UNCLASSIFIED  the repair module's own definitions are derived from
                       its AST and required to match a declared §5 category
                       table EXACTLY. 11 definitions, every one a correction
                       authorization handler, a provenance writer, the
                       terminal-completeness assertion, or a repair guard.
                       No scientific function is defined.
```

Guard 3 tripped on itself the moment it was written — it flagged
`assert_nothing_unclassified` as unclassified — which is the behaviour wanted
from a check that is meant to be real.

---

## §6 Signal and position identity — verified by reproduction

```
SIGNAL_IDENTITY_VERIFIED   = YES
POSITION_IDENTITY_VERIFIED = YES
```

Before computing anything repaired, the run recomputed the **parent's** 214-month
statistics from its own freshly built book and required them to reproduce the
parent's published numbers **exactly**:

```
gross mean, net mean, net Sharpe, and all three 95 % interval endpoints
aggregate turnover 149.7010850378876
aggregate cost     0.029940217007577524
entry-trade boundary month 2008-09-30
eligible month count 214
```

All reproduced bit-for-bit. Had the macro feature, the 218-date decision grid,
the positions, the wrapper, the cost model or the bootstrap drifted by anything
at all, they could not have. This exposes nothing new — the parent result is
already on the record — and it is the only way to *prove* rather than assert that
the correction changed the sample and nothing else.

The Gate-0.5 structural fingerprint was also reproduced: 218 decision months,
3270 defined cells, 0 undefined, 718 flat, legs G/I/P = 218/218/218.

---

## §7 Gate 0.5 remains closed and valid

```
GATE05_RERUN = NO
accepted result = 1313 / 3270 = 40.152905 %   PASS   (unchanged)
```

Gate 0.5 compares **decision-date position states** and never requires the
following month to be a complete return observation, so the terminal-row defect
cannot touch it. `MMV-AUTH-0001` stays CONSUMED and the S3 repair driver reads
no canonical TSMOM sign at all.

---

## §8 Bootstrap boundary semantics

```
BOOTSTRAP_BOUNDARY_SEMANTICS_UNAMBIGUOUS = YES
```

A calendar year is **one block whatever its month count**. The 2026 block simply
loses its terminal month and is drawn as a 5-month block:

```
2008:4 · 2009-2025: 12 each · 2026:5        19 blocks, 213 months
```

This is not a new rule invented for the repair. It is the rule that already
produced a **4-month 2008 block** in the parent run, it is the established
programme implementation in
`research/extensions/benb/benb_inference.py::year_block_bootstrap` — which groups
by year over all observations and resamples `len(years)` indices — and contract
§J's *"resample COMPLETE calendar years"* names the resampling **unit** (a whole
year, as opposed to the monthly IID draw §J forbids), not a filter on which years
qualify. Under a 12-month-only reading the sample would be 204 months, not 213.

The draw matrix is identical to the parent's: same seed, same 19 blocks, same
shape. The correction changes the panel, not the draws.

```
HIGH_DIFFICULTY_OWNER_DECISION_REQUIRED = NO
FABLE_OWNER_ADVICE_REQUIRED             = NO
```

---

## §9 Trial and exposure accounting

```
TRIAL_FAMILY = F-MMV     m BEFORE = 1     m AFTER = 1
TRIAL_COUNT_INCREMENT = 0        is_new_trial = NO
is_independent_evidence = NO
```

The parent and repaired outcomes are **the same primary trial**, one of them
computed on an invalid sample. They are never to be presented as two pieces of
evidence, and no row was created that would let them be counted twice.

`ops/EXPOSURE_LEDGER.md`: the original row 57 is **preserved unedited** — the
ledger is append-only and corrects by citation, never by rewriting — and row 58
is appended, marking row 57 `INVALID_PRIMARY_SAMPLE / NONDECISIONAL` and
carrying this replacement primary result.

---

## §10 What was NOT computed

Not computed and withheld — **not computed at all**: per-ETF returns · per-leg
returns · alternative sample endpoints · the first-release diagnostic ·
drawdown · hit rate · yearly rankings · rolling Sharpe · alternative costs ·
an alternate bootstrap · any rescue analysis.

The only sample endpoint evaluated is the one MMV-OD-8 mandates. **No search
over endpoints was performed**, and none is authorized.

---

## §11 NO RESCUE

No series, transform, coefficient, mapping, threshold, cost, target, bootstrap,
sample rule or execution rule may be changed after this result. Any further
hypothesis requires a **NEW LINEAGE** with its own preregistration and seal, and
that is an Owner decision, not a continuation of this one.

```
EVIDENCE_CEILING = supported.  NEVER confirmed.  NEVER independently confirmed.
```

---

## §12 Artifacts

```
MACHINE RESULT   research/extensions/mmv/s3/MMV_S3_REPAIR_RESULT.json
                 sha256 987f50b49083f42d6ddd79f718430466ebdaf335f363e196cdce94a32bbd59a0

PARENT (INVALID, PRESERVED IMMUTABLY)
                 research/extensions/mmv/s3/MMV_S3_RESULT.json
                 sha256 70fc6f91ddcc9ce4888c76c4016d32684c8c273c9d9348754814a5860c306a5e
                 research/extensions/mmv/MMV_S3_RESULT.md
                 sha256 4ae4ad2a43345d86639a8f9a0b282c46d3c8af0f500fa72be612c1134b0d4d3f

RUN DRIVER       research/extensions/mmv/mmv_s3_repair_run.py   commit cd41614
AUTHORIZATION    ops/EXECUTION_AUTHORIZATIONS.md  MMV-AUTH-0003 commit 1734dcb
```

```
RERUN_PERFORMED = NO UNAUTHORIZED RERUN
PARENT_ARTIFACT_MODIFIED = NO
READY_FOR_CONTROLLER_REVIEW = YES
```
