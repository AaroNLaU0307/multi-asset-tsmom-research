# CTA-EDGE-01-TA — PRE-OUTCOME CLOSURE

```
LINEAGE                      = CTA-EDGE-01-TA
CONTRACT_ID                  = CTA-EDGE-01-TA-PREREG-01
STATUS                       = CLOSED PRE-OUTCOME
CLOSED_UTC                   = 2026-09-15
CLOSED_BY                    = programme controller decision (Aaron-side ChatGPT),
                               relayed to the Main Agent seat
FAILURE_TYPE                 = IDENTIFICATION_DESIGN_INSUFFICIENT
HISTORICAL_OUTCOME_EXPOSED   = NO
S3_RUN                       = NOT_AUTHORIZED
MECHANISM_FALSIFIED          = NO
ETF_EDGE_FALSIFIED           = NO
TARGET_MARGIN_EXCLUDED       = NO
SEALED_PREREG_SHA256         = 3b495fcb220a86b9c4226e308e4814bdfdd871d1c69ce352e99b78977436d35b
S1_SEAL_COMMIT               = 881e684b4ddca73f117ea78af14843dabf3c59c9
S2_BUILD_COMMIT              = 3bc779a67247110625378b8558cad3dfcf698ed6
```

This document closes the lineage. It **amends no seal**, deletes nothing, changes no
verdict — there is no verdict — and authorises nothing.

---

## 1. Why it closed

The sealed contract §G.3 required S2 to report the macro/QRA covariate
cross-tabulation **before any `AC` was computed**, precisely because the size of the
diagnostic's reference group could not be established at S1. That pre-check ran on the
real 213 primary events using **counts only**, and returned:

```
DESIGN_MATRIX_RANK      = 5 of 5 columns      -> NOT rank deficient
REFERENCE_GROUP_N       = 7
SEALED_MINIMUM          = 20
MACRO_SPEC_EVALUABLE    = NO
NOT_EVALUABLE_REASON    = REFERENCE_GROUP_TOO_SMALL (7 < 20)
```

Under the sealed §G.3, `NOT_EVALUABLE` makes the macro/QRA damage diagnostic **trigger**;
under the sealed §I.2, a triggered damage diagnostic converts a would-be Class D into
Class I. **Class D was therefore structurally unreachable before any historical ETF
outcome was opened**, and the controller closed the lineage rather than spend a governed
run on a design that could not reach its own positive class.

Evidence: [`TA_MACRO_CROSSTAB.md`](TA_MACRO_CROSSTAB.md),
[`TA_S2_BUILD_REPORT.md`](TA_S2_BUILD_REPORT.md) §1.

## 2. What this closure IS

```
PRE-OUTCOME IDENTIFICATION-DESIGN CLOSURE
```

The sealed design could not satisfy the programme's positive identification standard on
the data it was defined over, and that was established **from the calendar alone** while
the lineage was still entirely outcome-blind.

## 3. What this closure IS NOT

- **NOT empirical falsification.** No historical `AC`, mean, interval, Sharpe, bootstrap
  or LOYO value was ever computed for any instrument.
- **NOT target-margin exclusion.** No margin was tested against anything.
- **NOT low power from a historical result.** No historical result exists.
- **NOT evidence that the Treasury auction mechanism does not exist.** The intraday
  literature identifies it with a causal design (`TA_S0_FRAME.md` §B.1); nothing here
  touches that.
- **NOT a verdict.** Classes A, B, C, D and I are the sealed verdict vocabulary and
  none of them applies: the study did not run.

## 4. The research lesson

> At daily ETF frequency, the mid-month refunding-week object is too structurally
> entangled with the sealed macro/QRA calendar to support the programme's positive
> identification standard.

The cross-tabulation shows the entanglement concretely: CPI falls after the auction in
**125** of 213 windows and payrolls precede it in **178** of 213; only **7** windows are
free of all four covariates. That is the same fact the intraday literature reports as its
reason for working intraday rather than daily. It is a property of the calendar, not of
the implementation.

**Carried forward as a design rule:** when a candidate's event window is pinned to a
fixed point in the month, check the macro-calendar cross-tabulation **before sealing**,
not after. This lineage's seal deferred that check to S2 and the check then closed the
lineage; a future lineage with a calendar-pinned window should establish the reference
group at S0.

## 5. What is preserved unchanged

The S1 seal, the sealed preregistration, the event calendar, the S2 implementation and
its tests are all preserved exactly as committed. Nothing is rewritten, nothing deleted.
`ta_prereg_validate.py` still passes 122/122 and `ta_tests.py` still passes 48/48 at the
closing commit.

```
TA_ENGINE_RUN_ON_REAL_DATA   = NO
TA_REDESIGNED                = NO
TA_SEAL_MODIFIED             = NO
```

## 6. Accounting

```
TRIAL SPENT                  = NONE.  F-TA was declared before any member ran and no
                               member ever ran (TRIAL_LEDGER.md §6.2).
ETF PANEL BURN               = NONE ADDED.  The KB-1 addendum's "Exposure at this
                               append = NONE" stands: no ETF event return, AC, mean,
                               interval, Sharpe or bootstrap statistic was computed on
                               the panel by this lineage.
AUCTION RECORD               = metadata, not an outcome sample; creates no burn.
MACRO CALENDARS              = release dates only; create no burn.
EXECUTION AUTHORIZATIONS     = none ever existed for this lineage; none was created.
EXPOSURE LEDGER              = no outcome-exposure row was written, because no outcome
                               was generated.
D-ETF-COUNT                  = untouched, still UNKNOWN_PENDING_AARON_DECISION.
```

## 7. Design-contributor status, unchanged

Fable and Astra remain `material_design_contributor` for CTA-EDGE-01-TA and remain
barred from blind certification of that design
(`ops/REVIEWER_EXPOSURE_LOG.md` rows S31, S32; `TA_EXPOSURE_DISCLOSURE.md`). Closure
does not lift a bar.

## 8. Reopening

Reopening CTA-EDGE-01-TA is **not** a bounded repair and is **not** available to any
agent. The sealed §K.8 stands: no change to the window, anchor, tenor, instrument, cost
convention, materiality bars, sample endpoints, event definition, on-cycle rule,
covariate set or diagnostic powers is permitted inside this lineage. A design capable of
the identification this one lacked — intraday data, a cash/futures instrument, or a
different event object — would be a **new lineage** with its own S0, its own trial
accounting and its own Owner authorisations.

```
NEXT LINEAGE = CTA-EDGE-02-BENB (bond ETF-NAV basis), opened separately
```
