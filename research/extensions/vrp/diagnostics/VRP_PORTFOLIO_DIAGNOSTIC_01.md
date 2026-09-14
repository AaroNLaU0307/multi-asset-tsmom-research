# VRP-PORTFOLIO-DIAGNOSTIC-01 — fixed 80/20 practical portfolio diagnostic

```
LINEAGE                              = VRP-PORTFOLIO-DIAGNOSTIC-01
EXPLORATORY_ONLY                     = YES
OUTCOME_EXPOSED_REUSE                = YES
PROMOTION_POWER                      = NONE
DOES_NOT_CHANGE_TSMOM_VRP_01_VERDICT = YES
TSMOM_VRP_01_HISTORICAL_VERDICT      = UNRESOLVED_CLASS_3   (unchanged)
DIAGNOSTIC_STATUS                    = COMPLETE
PRACTICAL_CLASSIFICATION             = NOT_COMPELLING
```

**This is not TSMOM-VRP-01 Stage B.** Stage B is barred by the sealed §O stop rule and its
confirmatory entry point still refuses. This is a separate, non-preregistered, descriptive
lineage answering one practical question at one already-fixed allocation. Every number
below is outcome-exposed exploratory reuse and can support no confirmatory claim.

---

## 1. The defect that had to be repaired first

`VRP-DIAG-DEFECT-001` — the book ledger recreated the sleeve's `holdings` and `prices`
inside the per-month loop, so the first VX day of every month recorded `VM = 0` and
re-established the whole position from flat.

**Root cause confirmed, and a second component found during the repair.** Carrying the
state across months was necessary but not sufficient: the month-`t` sensitivity reset was
also happening *after* month `t`'s first mark. §H.1 puts the reset at the month-end
allocation, so month `t`'s first variation margin must already be on a `K_t`-sized
position. With both parts fixed, the sleeve leg became scale-invariant and therefore
comparable, month for month, with the sealed constant-`K` Stage-A series.

The reset trade keeps the position's weights and rescales by `K_t / K_(t−1)`; only that
increment trades. Because Stage A holds `K` constant by benchmark convention and bears no
reset trade at all (§E.1), the reset is reported as its own field
(`reset_cost_on_Kt`, mean `2.07e-05` of `K_t` per month) rather than folded into
`r_A_on_Kt`. §H.4 therefore reads, with the reset made explicit:

```
r_book,t = 0.80 · r_core,t + 0.20 · ( r_A_on_Kt − reset_cost_on_Kt )
```

### Fixture history, stated honestly

```
PREVIOUS_ITEM_13 = PASS_BUT_FIXTURE_INSUFFICIENT
CURRENT_ITEM_13  = PASS
```

The original `_stage_b_fixture` gave every synthetic month its own contract keys and
restarted prices at 20.0, so **no month boundary ever carried a live position** and the bug
was structurally invisible. The original test did **not** catch this defect and is not
described as though it had.

`_cross_month_fixture` now spans two calendar months with **one** roll period, so the same
front and second contracts are held across the boundary, the boundary weights are strictly
between 0 and 1, and the settlement jumps `+2.00` comparable points into month 2.
`test_i13_old_reset_bug_is_caught_by_the_cross_month_fixture` reproduces the old state by
running month 2 in isolation and requires the two to separate by about the boundary move:

| | month-2 sleeve return |
|---|---|
| repaired ledger (captures the boundary mark) | `−0.0206` |
| old reset behaviour (mark discarded, full re-entry) | `−0.0020` |
| separation | `0.0186` — required `> 0.015` |

`OLD_BUG_CAUGHT_BY_NEW_FIXTURE = YES`. A structural guard
(`test_i13_sleeve_state_is_not_declared_inside_the_month_loop`) fails if the state is ever
moved back inside the loop. Items 14 and 15 share the fixture family and were re-run: all
of items 13–15 pass, 15/15.

## 2. Reconstruction gate

Required before any portfolio metric was produced:

```
max | ledger r_core − canonical net |                        = 1.110e-16     <= 1e-9  PASS
max | ledger r_A(K_t) − sealed r_A |, 216 carried months     = 8.327e-17     <= 1e-9  PASS
entry month 2008-05                                          = 1.392e-02     disclosed
funding events = 0        book_exhaustion = False
```

**The entry month differs by construction, and the difference is kept, not removed.** This
book establishes the sleeve on its first day and pays that one-off entry cost; the sealed
Stage-A series has held a live position continuously since 2006-09. Starting a sleeve costs
something, and that is part of the portfolio experience being measured. Every other month —
every month in which both objects hold a comparable carried position — agrees to floating
point.

**Zero funding events across 217 months.** The sleeve's worst month is about `−0.32·K_t`,
i.e. roughly `−6.4 %` of book at the 20 % share, so the sleeve collateral account never
approaches exhaustion and the core is never liquidated to fund it. That is a genuine
structural property of this allocation.

## 3. Sample and construction

```
COMMON_SAMPLE = 2008-05 .. 2026-05        N_MONTHS = 217 (contiguous, verified)
  lower bound = later of the canonical first complete scored month (2008-05) and the
                VRP first eligible complete month (2006-09)  -> 2008-05, derived mechanically
  upper bound = 2026-05; the canonical core has a complete month only through May 2026
                (the frozen panel ends 2026-06-12), so 2026-06 is partial and excluded
CORE_ONLY = 100 % frozen canonical 17-ETF TSMOM (Value §17 comparator identity, unchanged)
VRP_ONLY  = the sealed historical VRP sleeve, unchanged
COMBINED  = 80 % core + 20 % VRP, W0 = $1,000,000, validated self-financing ledger
```

The 20 % share is **reused** because `s = beta/b = 0.20` was fixed before any historical
outcome was seen. It is **not** claimed optimal and **no other weight was tested**. No
parameter sweep, no tenor variation, no filter, no alternative cost grid, no new window.

**Sharpe convention, stated explicitly:** `sqrt(12) · mean(monthly net) / std(monthly net,
ddof=1)`, `rf = 0`.

**Return definitions — the two legs sit on different cash bases, and both treatments are
reported rather than one being invented.** CORE is a net **total** return; VRP is
**excess-of-cash** on committed capital. The primary COMBINED row credits no cash yield to
the sleeve's collateral; the alternative rows credit the sealed FM-1 yield (defined for all
217 months).

## 4. Results

| | ann. mean | ann. vol | Sharpe | max DD | worst mo | best mo | pos % |
|---|---|---|---|---|---|---|---|
| **CORE_ONLY** | +0.0774 | 0.1031 | **+0.751** | −0.1560 | −0.0844 | +0.0889 | 62.2 |
| **VRP_ONLY** (excess of cash) | +0.0800 | 0.1657 | +0.483 | −0.4382 | −0.3217 | +0.1189 | 66.4 |
| **COMBINED 80/20** | +0.0777 | 0.0856 | **+0.908** | −0.0957 | −0.0825 | +0.0788 | 62.7 |
| *VRP_ONLY, FM-1 total return* | +0.0940 | 0.1656 | +0.568 | −0.4339 | −0.3209 | +0.1190 | 67.3 |
| *COMBINED, FM-1 total return* | +0.0805 | 0.0855 | +0.942 | −0.0920 | −0.0824 | +0.0789 | 63.1 |

```
TSMOM_VRP monthly correlation = −0.1050        covariance = −1.4941e-04
COMBINED − CORE  Sharpe       = +0.1573
COMBINED − CORE  annual vol   = −0.0175        (lower)
COMBINED − CORE  max drawdown = +0.0604        (shallower)
COMBINED − CORE  annual mean  = +0.0003        (essentially unchanged)

DELTA_SHARPE_POINT = +0.1573
DELTA_SHARPE_CI_95 = [ −0.0052 , +0.3113 ]     paired stationary block bootstrap,
                                               seed 20260914 (declared before execution),
                                               10,000 replicates, expected block 12 months,
                                               identical paired months in every replicate
```

**The interval crosses zero, so the Sharpe improvement is NOT robustly established.** The
rule was fixed in advance and is applied as written; "−0.005 is nearly zero" is not a
finding, exactly as the point estimate did not classify Stage A.

### SPY bottom-decile months (X46 rule, 22 months, threshold −0.0521)

```
mean CORE      = +0.0086          worst tail CORE     = −0.0813
mean COMBINED  = −0.0093          worst tail COMBINED = −0.0825
D_diag         = −0.0178          mean VRP sleeve in tail = −0.0806
```

This is the decisive block. **In the months the core exists to survive, the combined book
flips from positive to negative.** The core averaged +0.86 % in SPY's worst decile; adding
the sleeve turns that into −0.93 %, a loss of 1.78 percentage points per tail month.

### Declared crisis windows (compounded; all fixed in advance, none added after the fact)

| window | span | CORE | COMBINED | difference | VRP sleeve |
|---|---|---|---|---|---|
| 2008 GFC | 2008-09..2009-02 | **+0.1442** | **+0.0174** | **−0.1268** | −0.4153 |
| Feb 2018 vol shock | 2018-02 | −0.0479 | −0.0520 | −0.0041 | −0.0685 |
| Mar 2020 COVID | 2020-02..2020-03 | **+0.0787** | **−0.0050** | **−0.0838** | −0.3219 |
| CY2022 | 2022-01..2022-12 | +0.1497 | +0.1305 | −0.0191 | +0.0342 |
| Aug 2024 vol episode | 2024-08 | +0.0611 | +0.0497 | −0.0113 | +0.0044 |
| Apr 2025 vol episode | 2025-04 | −0.0133 | −0.0221 | −0.0087 | −0.0569 |

The core's two largest crisis gains are the ones the sleeve erases: the GFC gain falls from
+14.4 % to +1.7 %, and COVID turns from +7.9 % to −0.5 %. **Every one of the six declared
windows is worse combined than core-only.**

### Cost diagnostic (sealed §G, unchanged)

```
annualised execution cost / K = +0.02496
annualised gross carry  / K   = +0.10499
annualised net excess   / K   = +0.08003
cost as a fraction of GROSS carry = 23.77 %
cost as a fraction of NET return  = 31.18 %
```

Execution cost consumes roughly a quarter of the gross carry and is about 31 % the size of
what survives. That is a heavy, unavoidable drag under the sealed convention, and it is a
fact about the object, not an argument for changing the convention (§O forbids that).

## 5. Classification

```
PRACTICAL_CLASSIFICATION = NOT_COMPELLING
```

Two independent reasons, either of which is sufficient under the criteria fixed in advance:

1. **The Sharpe improvement is not robustly established.** `ΔSharpe = +0.157` with a 95 %
   interval of `[−0.005, +0.311]` that includes zero.
2. **The tail deterioration is substantial and is exactly the anticipated failure mode.**
   `D_diag = −1.78 pp` per tail month, the core's crisis-positive character is reversed,
   and all six declared crisis windows are worse. The Phase-C planning sentence — *"at
   meaningful size a short VIX sleeve may erase the core's crisis gain"* — is what the data
   shows at 20 %.

**The contrary evidence, stated fairly.** Whole-sample volatility falls by 1.75 pp, maximum
drawdown becomes 6.04 pp shallower, and the correlation is genuinely negative (−0.105). The
combined book looks calmer on unconditional statistics. But that calm is bought precisely
where it is least wanted: the sleeve pays steadily in quiet markets and loses heavily in the
episodes the core is held for. Unconditional drawdown improves while conditional crisis
performance collapses. For a book whose purpose includes crisis defence, that is not a
portfolio improvement.

This changes nothing about the scientific record. **TSMOM-VRP-01 remains `UNRESOLVED`,
Class 3**, and this diagnostic carries `PROMOTION_POWER = NONE`.

```
FABLE_FOLLOWUP_RECOMMENDED = NO
```

A new formal portfolio-overlay lineage would need a fixed-weight improvement worth
formalising. There is none here: the Sharpe gain is not robust and the tail trade-off runs
against the core's purpose. Close VRP and move to the next Phase-C candidate.

*Machine-readable metrics: `VRP_PORTFOLIO_DIAGNOSTIC_01.json`. Recompute every hash cited
here before use.*
