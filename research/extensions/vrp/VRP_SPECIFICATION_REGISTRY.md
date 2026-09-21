# TSMOM-VRP-01 — SPECIFICATION REGISTRY (dated break table)

```
LINEAGE   = TSMOM-VRP-01
GOVERNS   = VRP_PREREGISTRATION.md §F.5 (specification breaks) and §G (tick history)
RULE      = specification changes are EXPLICIT METADATA. They are never inferred from a
            price jump. Every span is sourced to a saved, hashed primary Cboe document.
BASIS     = everything is converted to the common $1,000-per-point economic basis:
            price_comparable = price_quoted * M_quoted / 1000
            tick_comparable  = tick_quoted  * M_quoted / 1000
```

## 1. Quotation basis, multiplier and tick

| span start | span end | M_quoted ($/quoted pt) | tick_quoted | conversion factor | tick_comparable | tick documented | primary source |
|---|---|---|---|---|---|---|---|
| 2004-03-26 | 2007-03-25 | 100 | 0.10 | 0.100 | 0.01 | YES | `CFE-IC-2007-003.pdf` |
| 2007-03-26 | open | 1000 | 0.05 | 1.000 | 0.05 | NO (see §3) | `CFE-IC-2007-003.pdf + cboe_vx_contract_specifications.html` |

### The 2007 rescaling — CFE Information Circular IC07-03

Saved and hashed as `CFE-IC-2007-003.pdf`. Dated 7 March 2007, it states:

> The rescaling will be effective March 26, 2007 and will apply to all VIX and VXD
> futures contracts. … CFE will divide the VIX and VXD futures contracts by 10 … Second,
> CFE will increase the current multiplier for the VIX and VXD futures contracts from
> \$100 to \$1,000. As a result, the traded futures price will be reduced by a factor of
> ten and the minimum tick will be reduced from \$0.10 to 0.01 index point, but the
> dollar value of both will remain the same.

and tabulates the two practices side by side:

| | futures price | contract multiplier | contract value | minimum tick | value per tick |
|---|---|---|---|---|---|
| Current practice (pre-2007-03-26) | 103.90 | $100 | $10,390 | $0.10 | $10 |
| Rescaled practice (from 2007-03-26) | 10.39 | $1,000 | $10,390 | 0.01 index point | $10 |

The §F.5 conversion reproduces exactly this economic continuity: the comparable price is
unchanged across the break and the comparable tick is worth $10 on both sides.
`test_i07_*` assert both, and `test_i07_stress_loss_is_invariant_to_the_quotation_basis`
asserts that the §D.1 stress loss does not depend on the quotation basis.

## 2. Expiry-rule registry

VX has had two published monthly final-settlement rules. The registry reproduces the
observed final settlement of **every one of the 264 expired acquired contracts** with
**zero mismatches** (`test_i03_expiry_rule_reproduces_every_observed_final_settlement`).

| contract months | rule | holiday adjustment |
|---|---|---|
| VX listing (2004-03) … 2004-10 | the Wednesday immediately prior to the third Friday of the **expiring** month | if that Wednesday, or the Friday it is measured against, is a Cboe Options holiday → the business day immediately preceding that Wednesday |
| 2004-11 … present | the Wednesday **thirty days** prior to the third Friday of the **following** calendar month (the rule transcribed in §F.2 and §L) | as above |

**Where the boundary is, and how far the data pins it.** The two rules give the same date
in most months, so the observed history cannot date the change to the month; it brackets
it exactly. The last contract whose observed final settlement follows the ORIGINAL rule
and not the current one is **2004-07** (observed 2004-07-14, current rule 2004-07-21) and
**2004-10** (observed 2004-10-13, current rule 2004-10-20). The first contract whose
observed final settlement follows the CURRENT rule and not the original one is **2005-12**
(observed 2005-12-21, original rule 2005-12-14). For every contract month in between the
two rules agree, so the choice of boundary inside (2004-10, 2005-12] changes **no date**
this lineage uses. 2004-11 is taken as the boundary.

This is outside the frozen Stage-A window in any case: §F.6 puts the first eligible
complete month at **2006-09**.

## 3. The one undocumented span, and the sealed rule that closes it

The exact date on which the **outright** minimum increment moved from 0.01 to 0.05 index
points is not established by any primary Cboe document this session could obtain and read.
(CFE-2009-01, whose title suggested it, is in fact a Threshold-Width amendment and says
nothing about the tick; it is deliberately **not** cited.)

§G fixes what to do:

> If the contemporaneous tick is undocumented for a span, the **largest tick documented
> for the contract on the comparable basis** is used for that span (conservative; declared).

So the whole post-rescaling span carries `tick_comparable = 0.05`, the largest documented
comparable tick. **This is economically inert and provably so**: §G charges
`cost_points = max(0.10, tick_comparable)`, and every tick documented for this contract on
the comparable basis lies in [0.01, 0.05] — all below `c0 = 0.10`. So `cost_points = 0.10`
throughout the window regardless of which value is assumed.
`test_i08_cost_invariant_to_tick_assumption` asserts exactly that, and
`test_i08_cost_points_never_below_the_contemporaneous_tick` asserts
`cost_points >= tick_comparable` on every date in the window.

**Consequence for the acceptance contract:** item 8's requirement — "undocumented span →
the largest documented tick is applied and disclosed" — is satisfied here, by this
disclosure and that test. The undocumented span cannot move any cost, any Stage-A return
or any estimand.

## 4. Exchange calendar

The **operative** CFE business-day calendar is the union of official settlement dates
across every acquired monthly contract — §L's own construction for this calendar, and the
only definition under which "a missing official settlement on an exchange business day"
(§F.4) is well posed. It is cross-checked against the rule-derived US equity / Cboe
Options holiday calendar over the whole acquired range.

Result: **zero unexplained differences**. Three dates are declared exceptions on which the
US equity market was closed but CFE held a session and published official VX settlements:

| date | why |
|---|---|
| 2015-04-03 | Good Friday; CFE held a session (the US employment report fell that day) |
| 2018-12-05 | national day of mourning for President G. H. W. Bush; NYSE and Cboe Options closed, CFE traded |
| 2025-01-09 | national day of mourning for President Carter; same pattern |

`vrp_calendar.CFE_OPEN_WHEN_EQUITIES_CLOSED` declares them, and
`check_calendar_consistency` FAILS on any mismatch not listed there.

There are **no** rule business days without any VX settlement anywhere in the record.

*Any receiver recomputes the document hashes in `VRP_DATA_MANIFEST.md` before use.*
