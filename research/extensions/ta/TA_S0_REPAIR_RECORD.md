# CTA-EDGE-01-TA — S0 → S1 SUPERSESSION RECORD

```
LINEAGE     = CTA-EDGE-01-TA
PURPOSE     = enumerate every statement in the accepted S0 frame that the sealed S1
              contract supersedes, so that no later session can revive one
S0 ARTIFACT = research/extensions/ta/TA_S0_FRAME.md  -- PRESERVED BYTE-UNCHANGED
S1 AUTHORITY= research/extensions/ta/TA_PREREGISTRATION.md  -- THE SOLE DESIGN AUTHORITY
CREATED     = 2026-09-15
```

**Why the S0 file is not edited.** `TA_S0_FRAME.md` is an accepted artifact whose bytes
are pinned in `TA_SEAL_MANIFEST.md`. This repository does not rewrite accepted
artifacts — the Time-Series Value contract kept its `_DRAFT` filename after sealing,
and the VRP lineage carried a separate `S0-02-repaired` document rather than editing
`S0-01`. Editing S0 now would change a hash that the seal itself cites.

**The operative rule.** Where `TA_S0_FRAME.md` and `TA_PREREGISTRATION.md` disagree,
the contract wins, unconditionally. Every S0 sentence listed below is **DEAD**: it has
no force, may not be quoted as design, and may not be restored.

---

## The five mandated repairs

### Repair 1 — SHY is not a hard placebo

| | |
|---|---|
| **S0 said** | §C.6 `PLACEBO 1 = SHY … Literature-predicted NULL … A material SHY effect falsifies the supply interpretation`; §C.11 kill condition *"a placebo shows a material effect of the same size"*; §C.12 Class A *"and the placebos are null"*. |
| **Status** | **DEAD.** |
| **S1 replacement** | §G.1. `SHY_HARD_PLACEBO = REMOVED`. SHY is a `MATURITY_GRADIENT_DIAGNOSTIC` with `PROMOTION_POWER = NONE`, `KILL_POWER = NONE`, `DAMAGE_POWER = NONE`. **No classification rule in §I references SHY.** |
| **Why** | The primary is now explicitly a reduced-form refunding-week effect. §C.5 of the contract establishes mechanically that a 10-year auction sits inside **213 of 213** primary windows and a 3-year auction inside 210 of 213, and the 10-year auction has documented cross-maturity spillover to the short end. A non-zero SHY statistic is therefore fully consistent with the claim and cannot bear against it. |

### Repair 2 — self-differencing wording

| | |
|---|---|
| **S0 said** | §C.6 point 3: *"any drift that is constant in the ±5-day neighbourhood of an auction … **cancels exactly**"*; §C.6 closing paragraph *"the risk-free rate and any local drift difference out"*. |
| **Status** | **DEAD.** |
| **S1 replacement** | §D.2, verbatim semantic rule: `SELF_DIFFERENCING = REDUCES SENSITIVITY TO LOCALLY STABLE COMMON DRIFT`; `SELF_DIFFERENCING != EXACT REMOVAL OF NON-AUCTION SHOCKS`. Explicitly **not** removed: realised rate shocks, macro announcements, QRA information, policy surprises, other auctions' spillover, non-stationary expected returns. |
| **Estimand changed?** | **NO.** This repair is wording and interpretation only, as instructed. |

### Repair 3 — the position path

| | |
|---|---|
| **S0 said** | §C.6 point 2: *"short duration through the pre window, **flip long** at the auction-day close"*; §C.7 cost model *"flat -> short (1 unit) -> **flip to long (2 units)** -> flat (1 unit)"*. |
| **Status** | **DEAD.** The "flip" wording implied exposure carried across the excluded auction-day bar. |
| **S1 replacement** | §E.1, written out mark by mark: `close(t0-6) flat -> SHORT 1`; `close(t0-1) SHORT -> flat`; **auction-day bar: FLAT**; `close(t0) flat -> LONG 1`; `close(t0+5) LONG -> flat`. **There is NO short-to-long flip.** |
| **Cost arithmetic** | Unchanged: 1 + 1 + 1 + 1 = **4 one-way units** × 2 bps = **`COST_BPS` = 8.0 bps per event**. M1 net bar +8 bps, gross bar +16 bps. |
| **Enforcement** | §T.2 item 4 makes "exposure is ZERO across the auction-day bar" a mandatory S2 **behavioural** assertion with a discriminating fixture that must reproduce a deliberate flip implementation and require a stated separation. |

### Repair 4 — M2 defined precisely

| | |
|---|---|
| **S0 said** | §C.7: *"annualised Sharpe = mean(net AC) / sd(net AC) × **sqrt(number of event weeks per year)**"* — ambiguous, and it did not charge idle calendar time. |
| **Status** | **DEAD.** |
| **S1 replacement** | §F. A fixed **calendarised monthly** construction: `MONTH_GRID` = 2006-02 … 2026-05 = **244 months**; `MONTHLY_TA_RETURN[m]` = that month's `AC_NET` on one fixed unit notional, **0** in the 31 months with no event; `SHARPE = mean / sd(ddof=1) × sqrt(12)`; risk-free = 0; no leverage optimisation, volatility targeting, capital scaling or weight search. |
| **Multiple events per month** | Defined as the sum of all non-overlapping primary event P&Ls. **Verified vacuous on this calendar**: the sealed record shows a maximum of **1** valid primary event per calendar month and **zero** overlapping primary windows (minimum consecutive gap 17 grid days). The HOLD condition the controller attached to overlapping primary windows is therefore **not triggered**. |

### Repair 5 — outcome taxonomy, and Class I

| | |
|---|---|
| **S0 said** | §C.12 classes A / B / C / D with prose triggers, placebo-null conditions and no identification class. |
| **Status** | **DEAD in full.** |
| **S1 replacement** | §I: an **ordered, first-match-wins, verified disjoint and exhaustive** taxonomy **A / B / C / D / I** stated in the five interval bounds, with `CLASS I — IDENTIFICATION / DEPENDENCE FAILURE` added, its three diagnostic triggers sealed (§G.2 SPY, §G.3 macro/QRA, §G.4 LOYO), and its additional executed-calendar-contamination trigger (§I.3). Status mapping in §I.4, with `IDENTIFICATION_INSUFFICIENT_FOR_THE_CLAIM` as a **mandatory** qualifier that Class I may never be reported without. |

---

## Further S0 statements superseded

### 6 — the four-cell family and the decomposition

**S0 §C.8** discussed `{IEF, TLT} × {PRE, POST}` and whether BH-FDR applies. **DEAD.**
S1 §J: the primary family has **m = 1** (TLT combined `AC_NET`); no multiplicity
correction is required or applied because no selection across cells occurs; the four
legs are a descriptive decomposition with `PROMOTION_POWER = NONE`.

### 7 — the 2/5/7-year calendar claim — **factually corrected**

**S0 §C.6 point 4** asserted, flagged PROVISIONAL, that a ±5-day placebo anchor
*"lands on some Treasury auction almost everywhere"* because *"the 2-, 5- and 7-year
auctions sit at the end of the month"*. **The mechanical check contradicts the
detail.** Inside the 213 primary windows the end-of-month block appears in only
**3/213 (1.4 %)** of windows for each of the 2-, 5- and 7-year.

The S0's **conclusion** survives and is in fact stronger than it claimed: **0 of 213**
primary windows are free of another auction — but the occupants are the **10-year
(213/213)**, the **3-year (210/213)**, TIPS (120/213) and the 20-year (49/213), i.e.
the same mid-month refunding block, not the end-of-month block. S1 §C.5 records the
corrected table; S1 §D.3 keeps `PRIMARY CONTROL = none` on the corrected basis.

### 8 — event counts

**S0 §C.9** gave ranges (`~210-245` primary, `~260-287` secondary) because the
pre-2009 auction frequency was unverified. **DEAD — superseded by exact counts.**
S1 §C.2 / §C.3, from the pinned official record: **213** primary valid windows across
**21** calendar years, **258** secondary valid windows across **25**. The 30-year
frequency history is now established from the record (no auctions at all 2002–2005;
2/yr 2006–2008; 10 in 2009; 12/yr from 2010).

### 9 — the anchor and grid

**S0 §C.4/§C.5** spoke of "business days". **DEAD.** S1 §B.3: offsets are in
**common-grid trading days** on the frozen panel, with the cross-instrument identity
of the TLT / IEF / SHY / SPY calendars verified and re-asserted at every build.

### 10 — the event-family inclusion rule

**S0 §C.4** said reopenings and originals are one family and said nothing more.
**SUPERSEDED, not contradicted.** S1 §B.2 adds the six-part mechanical membership
test including the **ON-CYCLE RULE**, which is a **no-op on the primary family**
(0 of 245 rows dropped) and removes 5 off-cycle secondary rows.

### 11 — "matched control windows"

**S0 §C.6** rejected matched controls already. **RETAINED**, now on mechanically
verified grounds (§C.5) rather than a provisional calendar description.

---

## What is NOT superseded

`TA_S0_FRAME.md` sections **A** (programme facts), **B** (the verified literature
prior, including every primary-source extract and the correction of Fable's stale
citations), **D** (not-yet-tested claims), **E** (parked questions) and **F**
(forbidden interpretations) stand, and §F is carried forward and strengthened as S1
§K. The S0's designation of TLT as lineage-primary and IEF as declared secondary
stands and is now the controller's accepted decision.

```
S0_ARTIFACT_MODIFIED = NO
S0_ARTIFACT_ACCEPTED = YES
SOLE_DESIGN_AUTHORITY = research/extensions/ta/TA_PREREGISTRATION.md
```
