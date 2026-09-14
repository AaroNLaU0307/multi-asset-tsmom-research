# VRP-PORTFOLIO-DIAGNOSTIC-01 — DEFECT 001, and why the diagnostic is on HOLD

```
DEFECT_ID        = VRP-DIAG-DEFECT-001
FOUND_BY         = VRP-PORTFOLIO-DIAGNOSTIC-01, first real-data reconstruction check
FOUND_UTC        = 2026-09-14
SEVERITY         = MATERIAL for any future Stage-B-style book run; LATENT today
AFFECTS          = research/extensions/vrp/vrp_stage_b.py  (the book ledger)
SEALED_RESULTS_AFFECTED = NONE
DIAGNOSTIC_STATUS = HOLD
```

The diagnostic stopped itself before producing a single portfolio metric, exactly as the
instruction requires: *"If a concrete implementation/data defect is found, stop and report
it."* No headline number is reported below, because the object that would produce it is
defective.

---

## 1. What the check found

The diagnostic rebuilds the COMBINED 80/20 book from two pinned inputs and then verifies
that the ledger reproduces **both** of them before using any output:

```
max abs( ledger r_core  -  canonical net monthly )   = 1.110e-16      OK
max abs( ledger r_A(K_t) -  sealed Stage-A monthly ) = 6.576e-02      FAIL
funding events = 0      book_exhaustion = False
```

The core leg is exact to floating point. **The sleeve leg is wrong by up to 6.58e-02 —
6.58 percentage points of committed capital in a single month — against a sealed identity
tolerance of 1e-9.**

## 2. The mechanism, precisely

In `vrp_stage_b.run_book_ledger`, the sleeve's position state is declared **inside** the
per-month loop:

```python
for cm in core:
    ...
    # sleeve state
    holdings: Dict[Key, float] = {}     # <-- reset every calendar month
    prices:   Dict[Key, float] = {}     # <-- reset every calendar month
```

So on the **first VX business day of every month** the ledger:

1. records `VM_d = 0`, because it believes it held nothing yesterday — discarding the real
   settlement move from the previous month-end into that day; and
2. re-establishes the **entire** sleeve position from flat, paying a full entry cost on the
   whole book instead of only the §H.1 reset increment.

The month boundary is **not** a roll boundary. Measured on the real chain, the first VX day
of each month sits mid-roll-period and the position is genuinely live:

```
2020-01-02  w_front = 0.5455        2020-03-02  w_front = 0.5500
2020-02-03  w_front = 0.5263        2020-04-01  w_front = 0.4211
```

A flat-and-reopen at those points is not a rounding artifact; it is a different strategy.

## 3. Why this contradicts the sealed text

§H.1 says reset trades go **"to the new sensitivity"** — an adjustment from the old level
to the new one, not a liquidation and re-entry. §H.2 keeps the sleeve collateral account
running continuously (`C ← C + VM_d − cost_d`) rather than re-opening a position.

Decisively, §H.4 is **binding on the acceptance contract**:

> in any month with no funding event, `r_book,t = 0.80 · r_core,t + 0.20 · r_A,t(K = K_t)`
> **exactly** (to floating tolerance)

`r_A,t` is the Stage-A excess return, and Stage A carries its holdings continuously across
month boundaries. The identity can therefore only hold if the Stage-B sleeve leg does too.
It does not, and the measured violation above is the proof.

## 4. Why acceptance item 13 did not catch it

`vrp_tests._stage_b_fixture` gives **every synthetic month its own front/second contract
keys and restarts prices at 20.0**, so each month is independent by construction. The
month boundary never carries a live position, and the reset is invisible. Item 13 passed on
a fixture that could not have detected this defect.

That is the honest reading of the acceptance evidence: **item 13's PASS is weaker than it
looked**, and the same is true of items 14 and 15 to the extent they share the fixture.

## 5. Blast radius

| | |
|---|---|
| **Sealed results affected** | **NONE.** Confirmatory Stage B never ran — the sealed §O stop rule bars it after a Class-3 Stage A — so no sealed Stage-B number exists to be wrong. |
| **TSMOM-VRP-01 Stage A** | **Unaffected.** Stage A uses `vrp_stage_a.run_stage_a`, which carries holdings continuously across months over one call. Its reconstruction in this very check is what exposed the Stage-B leg as wrong. The verdict stands: `UNRESOLVED`, Class 3. |
| **This diagnostic** | **Blocked.** A faithful COMBINED book cannot be built on a ledger that mismarks and over-charges the first day of every month. |
| **Direction of the error** | The defect **overstates sleeve costs** (a full entry every month) and **drops** each month's first-day variation margin. It does not obviously bias the COMBINED result in a flattering direction, but it is large enough that no conclusion should be drawn from it either way. |

## 6. What the fix is, and why this session did not apply it

The code fix is small and well defined: hoist `holdings` and `prices` out of the per-month
loop so the sleeve position persists across month boundaries, while `C`, `sleeve_vm` and
`sleeve_cost` continue to reset monthly (they are per-month accounts by §H.2). The
month-end reset trade then naturally costs only the increment from `0.01·K_t` to
`0.01·K_(t+1)`.

It is **not applied here** because:

- the instruction for this session is to **stop and report** a concrete implementation
  defect, not to repair it;
- `vrp_stage_b.py` is an **accepted S2 artifact**, and changing accepted code after S2
  acceptance is a governance act, not a builder's discretion; and
- the repair is not complete without **also** replacing the synthetic fixture with one that
  carries a live position across a month boundary, so that item 13 actually exercises what
  it claims to. Re-validating an acceptance item is an Owner/ChatGPT decision.

## 7. What was established before the stop, and is defect-independent

These facts do not depend on the sleeve ledger and are recorded so the work is not lost:

```
COMMON SAMPLE, derived mechanically
  canonical first complete scored month = 2008-05
  VRP first eligible complete month     = 2006-09
  START_MONTH = 2008-05   END_MONTH = 2026-05   N_MONTHS = 217   (contiguous, verified)
  end boundary: the canonical core has a complete month only through 2026-05;
                2026-06 is partial (the frozen panel ends 2026-06-12) and is excluded
  core reconstruction against the canonical net stream: exact (1.1e-16)
  funding events = 0, book_exhaustion = False
```

The zero funding events are robust to the defect and worth recording: the sleeve's worst
sealed month was about `−0.32 · K_t`, i.e. roughly `−6.4 %` of book at the 20 % share, so
the sleeve collateral account never approaches exhaustion and the core is never liquidated
to fund it. That is a genuine structural finding about this allocation, and it is the
reason the §H.4 identity would be expected to hold in **every** month of the common sample
once the ledger is corrected.

**No portfolio metric, Sharpe, drawdown, correlation, tail statistic, crisis figure,
ΔSharpe or bootstrap interval is reported.** Producing them from a shortcut while a
material ledger defect is open would present a finished-looking answer built on an object
known to be wrong.

## 8. Standing

```
TSMOM_VRP_01_HISTORICAL_VERDICT      = UNRESOLVED_CLASS_3   (unchanged)
DOES_NOT_CHANGE_TSMOM_VRP_01_VERDICT = YES
EXPLORATORY_ONLY                     = YES
PROMOTION_POWER                      = NONE
DIAGNOSTIC_STATUS                    = HOLD
PRACTICAL_CLASSIFICATION             = NOT_DETERMINED (blocked by VRP-DIAG-DEFECT-001)
```
