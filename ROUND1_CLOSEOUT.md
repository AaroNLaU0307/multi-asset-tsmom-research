# CTA / systematic-macro DISCOVERY ROUND 1 — CLOSEOUT

```
ROUND1_STATUS             = CLOSED / EXHAUSTED
ROUND1_NEW_SUPPORTED_EDGE = NONE
ROUND1_EXHAUSTED          = YES
ROUND2_READY              = YES
ROUND2_STARTED            = NO
DATE                      = 2026-09-22
```

> **This document is a programme-level summary, not an authority.** Each row
> points at the artifact that actually decides it. Where this page and a lineage
> artifact disagree, **the lineage artifact wins** and this page is stale.
> Workflow authority is
> [`QUANT_WORKFLOW_VNEXT.md`](../QUANT_WORKFLOW_VNEXT.md); per-project *state* is
> [`PROJECT_STATE.md`](PROJECT_STATE.md).

---

## §1 The headline

```
NO NEW STANDALONE EDGE WAS PROMOTED IN ROUND 1.
```

Eleven candidate objects from the Round-1 discovery map were triaged. **One**
reached a sealed primary historical trial and returned `UNRESOLVED`. Two others
were run to a preregistered verdict and not promoted. The remaining **eight**
closed, parked, were blocked or were ruled non-standalone **before** any return
outcome was touched.

The canonical multi-asset TSMOM core is unaffected by all of this:

```
CANONICAL TSMOM = SUPPORTED — NOT INDEPENDENTLY CONFIRMED
ROLE            = FROZEN RESEARCH BENCHMARK
```

It is the benchmark these candidates were measured against, not a Round-1
finding, and nothing in Round 1 raised or lowered its status.

---

## §2 Candidate dispositions

| candidate / lineage | mechanism | outcome accessed? | terminal status | why, in one sentence | revival authorized? |
|---|---|---|---|---|---|
| **F1 / TA** — CTA-EDGE-01 | Treasury auction / refunding-week intermediation effect in duration ETFs | **NO** | **CLOSED PRE-OUTCOME** | The identification design was not sufficient to separate the auction effect from ordinary calendar structure, so it was closed before any return was tested. | NO — a new lineage would be required |
| **F3 / BENB** — CTA-EDGE-02 | Bond-ETF price vs NAV basis convergence | **YES** | **NOT PROMOTED** | The tradable primary (`beta_T`) did not pass its sealed gate; the evidence pointed toward overnight price discovery and NAV catch-down rather than the declared tradable effect. | NO |
| **PINS** — CTA-EDGE-03 | Physical inventory news × scarcity | **NO** | **PARKED PRE-OUTCOME (S0 HOLD)** | Point-in-time data authority for the inventory state could not be established, so S0 halted before outcome exposure. | Only under new data authority + a new lineage |
| **MMV** — CTA-EDGE-04 | Macro momentum on vintage (as-published) data | **YES** | **UNRESOLVED / NOT PROMOTED** | The sealed Gate-1 interval for the mean monthly return spans zero; the lineage is terminal and **no rescue is authorized**. | NO |
| **F4** — CTA-EDGE-05 candidate | Inventory state × commodity curve | **NO** | **PARKED PRE-OUTCOME** | The load-bearing natural-gas state is not point-in-time reconstructible from available sources, so the energy family fails before any return is formed. | Only under new data authority |
| **F7** | Rebalancing flow reversal | **NO** | **NON-RUN, CLOSED** | Preserved as a mechanism study rather than an active edge; any material redesign would require a new lineage. | NO — new lineage only |
| **F6** — CTA-EDGE-05 | Scheduled macro announcement premium (FOMC / CPI / NFP) in SPY | **YES** — one consumed sealed primary trial | **CLOSED_UNRESOLVED_NOT_PROMOTED** | Both point estimates are positive but both nominal 95% intervals span zero, so neither gate passed and neither excluded an effect. | NO — the primary trial is consumed |
| **F2** | — | **NO** | **BLOCKED / NOT STANDALONE** | Not standalone under the available proxy authority. | Needs new authority |
| **F8** | Positioning / crowding | **NO** | **PARKED — PREREQUISITE** | Parked on an unmet data prerequisite. | Needs the prerequisite first |
| **F9** | — | **NO** | **NOT A STANDALONE EDGE** | Does not constitute a standalone edge. | NO |
| **F10** | — | **NO** | **OVERLAPPING / PRICE-DERIVED** | Price-derived and overlapping with existing work; not standalone. | NO |

Candidate-level triage for F2 / F8 / F9 / F10 is recorded in
[`research/extensions/CTA_EDGE_04_CANDIDATE_AUDIT.md`](research/extensions/CTA_EDGE_04_CANDIDATE_AUDIT.md)
and the idea registry; they never became lineages and never touched a return.

---

## §3 Where each disposition is actually decided

| lineage | authoritative artifact |
|---|---|
| F1 / TA | [`research/extensions/ta/TA_CLOSURE.md`](research/extensions/ta/TA_CLOSURE.md) · [`TA_EXPOSURE_DISCLOSURE.md`](research/extensions/ta/TA_EXPOSURE_DISCLOSURE.md) |
| F3 / BENB | [`research/extensions/benb/BENB_CLOSURE.md`](research/extensions/benb/BENB_CLOSURE.md) |
| PINS | [`research/extensions/pins/PINS_CLOSURE.md`](research/extensions/pins/PINS_CLOSURE.md) |
| MMV | [`research/extensions/mmv/MMV_CLOSEOUT.md`](research/extensions/mmv/MMV_CLOSEOUT.md) |
| F4 | [`research/extensions/f4/F4_PREOUTCOME_PARK_CLOSEOUT.md`](research/extensions/f4/F4_PREOUTCOME_PARK_CLOSEOUT.md) |
| F7 | [`research/extensions/F7_NONRUN_DISPOSITION.md`](research/extensions/F7_NONRUN_DISPOSITION.md) |
| **F6** | [`research/extensions/f6/F6_CLOSEOUT.md`](research/extensions/f6/F6_CLOSEOUT.md) |
| F2 / F8 / F9 / F10 | [`research/extensions/CTA_EDGE_04_CANDIDATE_AUDIT.md`](research/extensions/CTA_EDGE_04_CANDIDATE_AUDIT.md) |

---

## §4 F6 — the one sealed primary trial of Round 1

F6 is the only Round-1 candidate that reached a governed historical execution.

```
SEAL_ID                           CTA-EDGE-05-F6-S1-2026-09-21
S0 COMPLETE · S1 SEALED · S2 ACCEPTED · S3 ACCEPTED · S4 COMPLETE

P1  +0.00035784   nominal 95% [-0.00062591, +0.00133231]   UNRESOLVED
P2  +0.00023075   nominal 95% [-0.00078811, +0.00123375]   UNRESOLVED
P3  NOT_APPLICABLE_BY_SEAL — never executed

TERMINAL          CLOSED_UNRESOLVED_NOT_PROMOTED
MECHANISM_FALSIFIED               = NO
ECONOMIC_EFFECT_RELIABLY_EXCLUDED = NO
LOW_POWER_ASSERTED                = NO
PRIMARY_EXECUTION_COUNT           = 1
SECOND_HISTORICAL_RUN             = NO
POST_RESULT_RESEARCH              = NO
2026_F6_OUTCOME_ACCESSED          = NO
```

```
THE F6 RESULT MUST NEVER BE DESCRIBED AS falsified, evidence of absence, a
negative edge, low power, a causal failure, or independently confirmed.
```

Both endpoints matter. The lower endpoint failing to clear zero is why nothing
was promoted; the upper endpoint sitting above zero is why nothing was excluded.
An unresolved result is a statement about the evidence, not a finding about the
world. The full verdict, the interpretation boundary, the rerun prohibition and
the execution governance reservation are in
[`F6_CLOSEOUT.md`](research/extensions/f6/F6_CLOSEOUT.md).

---

## §5 What Round 1 actually produced

Not an edge. What it produced is a working governed lifecycle and a set of
negative-space results that cost little because most candidates were stopped
**before** outcome exposure:

```
candidate objects triaged                  11
lineages opened                             5   (TA, BENB, PINS, MMV, F6)
historical return outcomes accessed         3   (BENB, MMV, F6)
sealed primary trials consumed              3
new supported edges                         0
closed / parked / blocked PRE-OUTCOME       8
```

Eight of eleven candidate objects were resolved without spending a return trial
at all. That is the point of the S0 gate, not a shortfall.

### §5.1 Recurring reasons a candidate died

```
POINT-IN-TIME DATA AUTHORITY   PINS, F4, F8 — the state could not be
                               reconstructed as it was actually known
IDENTIFICATION                 TA — the effect could not be separated from
                               ordinary calendar structure
NOT STANDALONE                 F2, F9, F10 — subsumed by, or derived from,
                               work already done
EVIDENCE INSUFFICIENT          BENB, MMV, F6 — ran to a verdict, did not clear
                               the sealed gate, and did not establish the
                               opposite either
```

---

## §6 Accounting state at close of Round 1

```
TRIAL LEDGER      research/extensions/TRIAL_LEDGER.md
                  Declared families: F-VRP, F-TA, F-BENB, F-MMV, F-F6.
                  F-F6 EXECUTED once, trial spent. N_trials on the ETF panel
                  remains NOT ASSERTED (D-ETF-COUNT =
                  UNKNOWN_PENDING_AARON_DECISION).

EXPOSURE LEDGER   ops/EXPOSURE_LEDGER.md
                  62 rows. Exactly one F6 performance exposure (row 61); row 62
                  is the F6 closeout governance row and contributes 0.

AUTHORIZATIONS    ops/EXECUTION_AUTHORIZATIONS.md
                  Every grant is ONE_SHOT. All are CONSUMED or spent. No live
                  execution authorization exists for any lineage.

SAMPLE REUSE      research/extensions/SAMPLE_REUSE.md
                  The ETF panel is heavily reused; every Round-1 candidate on it
                  is T0_REUSED_DEPENDENT with an evidence ceiling of `supported`.
```

```
NO LINEAGE IN ROUND 1 OBTAINED INDEPENDENT CONFIRMATION.
`supported` was a CEILING throughout, and it was never achieved by a Round-1
candidate.
```

---

## §7 Round 2

```
ROUND2_READY   = YES
ROUND2_STARTED = NO
```

Round 2 is authorized conceptually and **has not been started**. No Round-2
candidate has been selected, no discovery map has been commissioned, no S0 has
been opened, and no new research design exists in this repository.

Carry-forward constraints for whoever opens Round 2:

```
1. A Round-1 parked candidate may NOT be silently revived. PINS, F4 and F8 need
   genuine new data authority; reviving one is a NEW lineage with its own
   preregistration and seal.
2. A consumed primary trial is consumed. F6, MMV and BENB may not be rerun,
   re-specified or renamed onto the same exposed historical samples.
3. No Round-1 result may be retroactively promoted by a Round-2 finding.
4. The ETF panel is already heavily reused. Any Round-2 candidate on it inherits
   T0_REUSED_DEPENDENT and the `supported` ceiling.
5. 2026 is unexposed for F6 and carries no confirmation, rescue or promotion
   power for it. Prospective use needs its own governance.
```

---

## §8 Navigation

```
workflow authority      ../QUANT_WORKFLOW_VNEXT.md        (workspace root)
project state           PROJECT_STATE.md
this summary            ROUND1_CLOSEOUT.md                (programme-level, derived)
canonical study         STUDY_SUMMARY.md · README.md §1
lineages                research/extensions/<lineage>/
owner decisions         ops/OWNER_DECISION_RECORD_*.md
ledgers                 research/extensions/TRIAL_LEDGER.md · ops/EXPOSURE_LEDGER.md
authorizations          ops/EXECUTION_AUTHORIZATIONS.md
independent reviews     research/extensions/review_history/
```

Some Round-1 design advice (the Fable OD-series for F6) lives **outside this
repository**, in the workspace `Research Reports/` directory. Those artifacts are
hash-pinned from inside the repo — the sealed F6 contract and
`F6_S1_SEALED_MANIFEST.json` carry their SHA256s — so their identity is
verifiable here even though their bytes are not stored here. That is a known,
recorded dependency, not an oversight.
