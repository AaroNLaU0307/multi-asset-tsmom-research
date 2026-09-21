# CTA-EDGE-03-PINS — PINS-OD-1 FEASIBILITY RESULT

```
RECORD_TYPE   = FEASIBILITY_AUDIT_RESULT
LINEAGE       = CTA-EDGE-03-PINS
DATE          = 2026-09-16
PROTOCOL      = PINS_OD1_FEASIBILITY_PROTOCOL.md, frozen at commit db78c90040b3ff6d7fde09a2eb2d307c43d16ea0
SAMPLE        = PINS_AUDIT_SAMPLE.json, sha256 52e70b40e61a7b36057e2345f116c94bdab9ab091f6caa4bdf7d78178204283a
                45 releases, 3 per year 2012-2026, frozen BEFORE any retrieval

PINS_OD_1_FEASIBILITY = FAIL
FAILURE_MODE          = CONSENSUS (C) NOT RECONSTRUCTIBLE BY ANY ROUTE THIS SEAT CAN
                        LAWFULLY EXERCISE
RECOMMENDED_PROGRAMME_ACTION = CLOSE CTA-EDGE-03-PINS AT S0 / DATA-PIT FAILURE
                        — subject to the ONE Owner fact in §7, which is procurement,
                        not science, and which I cannot resolve.

WTI_OUTCOME_ACCESSED = NO   ·  SCARCITY_FEATURE_COMPUTED = NO
RETURN_REGRESSION_RUN = NO  ·  BACKTEST_RUN = NO
A - C COMPUTED = NO         ·  k ESTIMATED = NO
```

**Scope discipline, stated up front.** No `A` value was retrieved for any sample week, so
no `A − C` could be formed even in principle. No WTI price of any kind was accessed. The
Gate 0.5 information-timing diagnostic remains **declared deferred** per protocol §9.

---

## §1 Result against the frozen thresholds

| test | threshold | result | verdict |
|---|---|---|---|
| Consensus retrieval coverage, family 1 | ≥ 90 % (≥ 41 of 45) | **0 of 45 (0 %)** | **FAIL** |
| Consensus retrieval coverage, family 2 (the one permitted retry) | ≥ 90 % (≥ 41 of 45) | **0 of 45 (0 %)** | **FAIL** |
| API retrieval coverage | ≥ 95 % (≥ 43 of 45) | **NOT TESTED** — lawful documented route exists, entitlement not held | not reached |
| Per-row ordering `t(C) < t(P) < t(A)` | required | **NOT TESTABLE** — no `C`, no `P` retrieved | not reached |
| Quantity identity `C` / `P` / `A` | required | **PARTIAL**, from documentation only (§6) | not reached |

Under protocol §5 the retry budget is **one** second named family. It was spent. Under the
controller's §14 branch, no named family passing after the one retry is a **FAIL**.

---

## §2 Family 1 — Reuters / LSEG

```
NAMED SOURCE          Reuters (news polls) · LSEG "Reuters Polls Consensus" (data product)
HEADLINE STATISTIC    AVERAGE of polled analysts — VERIFIED, not median
                      Repeatedly worded "analysts polled by Reuters estimated ON AVERAGE".
                      This CONFIRMS correction 1 in PINS_S0_AMENDMENT_01 §3 and refutes
                      the original S0 frame's "median" assumption.
RESPONDENT COUNT      published per poll, and HIGHLY VARIABLE — observed wordings cite
                      three, five and nine analysts on different weeks. Directly engages
                      the protocol's "thin survey (n < 5) is FLAGGED, not dropped" rule.
SURVEY TIMING         conducted AHEAD of both the API and EIA reports -> pre-API
                      requirement SATISFIED IN PRINCIPLE
TARGET QUANTITY       weekly change in U.S. crude inventories (survey material reports in
                      MILLION barrels; EIA WCESTUS1 is THOUSAND barrels — a documented
                      unit difference, see §6)
```

### Retrieval outcome

```
ROUTE A — reuters.com directly
  INACCESSIBLE TO THIS AGENT. Fetches to www.reuters.com are refused at the
  user-agent level by the site's own policy. This is a hard access fact, not an
  interpretation of terms of use, and it means the primary archive could not be
  reached at all.

ROUTE B — public web search for specific frozen-sample release dates
  Tested 2025-08-27 and 2012-05-02 (both ORDINARY_WEDNESDAY, opposite ends of the
  window). Neither returned a Reuters poll value for the correct week with a named
  provenance and a publication timestamp. Searches returned other weeks' polls,
  aggregator landing pages, and unrelated material.
  RETRIEVED: 0.

ROUTE C — LSEG "Reuters Polls Consensus" data product
  Coverage documented as 900+ economic indicators, FX measures, central bank policy
  rates, money market rates and bond yields, from 1999. WEEKLY US PETROLEUM
  INVENTORY POLLS ARE NOT DOCUMENTED AS IN SCOPE on either of the two LSEG product
  pages checked. Requires an entitlement that is not held.
  RETRIEVED: 0. Coverage of the needed series: UNCONFIRMED.
```

```
FAMILY 1 PILOT COVERAGE = 0 / 45 = 0 %        REQUIRED >= 90 %       -> FAIL
FAMILY 1 LAWFUL ACCESS  = NOT ESTABLISHED for any route reachable by this seat
FAMILY 1 PIT PASS       = NOT DEMONSTRATED (the pre-API property is documented, but no
                          dated, timestamped observation was obtained to demonstrate it)
```

## §3 Family 2 — S&P Global Platts / Commodity Insights (the one permitted retry)

Selected as the retry on **coverage and access feasibility only**, per protocol §5. No
price data entered the selection.

```
NAMED SOURCE          S&P Global Commodity Insights (Platts)
SURVEY TIMING         analysts surveyed on MONDAYS, published ahead of the Wednesday EIA
                      release -> pre-API requirement SATISFIED IN PRINCIPLE
HEADLINE STATISTIC    published in Platts' own analysis articles; NOT independently
                      verified here as mean or median, because no dated article for a
                      sample week was obtained
PUBLIC ARTICLES       exist on spglobal.com across at least 2017-2025
```

### Retrieval outcome

```
No DATE-ADDRESSABLE systematic archive was located. Article URLs use an opaque
MMDDYY-plus-slug pattern, so a specific historical week cannot be addressed without
already knowing its headline. A domain-restricted search for the frozen sample week
2024-08-21 (survey published Monday 2024-08-19) returned no matching article.

FAMILY 2 PILOT COVERAGE = 0 / 45 = 0 %        REQUIRED >= 90 %       -> FAIL
```

## §4 Rejected by rule — NOT counted as families, NOT used as a retry

```
Investing.com, FXStreet, Forex Factory, TradingEconomics economic-calendar
"Forecast" fields.

Verified in detail on the Investing.com EIA crude oil inventories page:
  1. NO named survey family is attributed to the Forecast column.
  2. NO publication timestamp exists for the forecast, only for the release.
  3. Explicit prohibition: "It is prohibited to use, store, reproduce, display,
     modify, transmit or distribute the data contained in this website without the
     explicit prior written permission of Fusion Media and/or the data provider."

FAILS PROTOCOL §4 and §7 ON THREE INDEPENDENT COUNTS: no named family, no
timestamp, and a lawful-storage blocker. The controller's instruction is explicit
that such a field may not be accepted, and it was not.
```

This is the route that would have made the lineage look feasible. It is the one that most
needed to be refused, and refusing it is the substance of the finding rather than an
inconvenience around it.

## §5 The API leg (`P`) — a lawful route exists, and was not exercisable

```
NAMED SOURCE     American Petroleum Institute, Weekly Statistical Bulletin
RELEASE          Tuesday ~16:30 ET (Wednesday ~16:30 ET if Monday is a Federal holiday)
                 -> BEFORE the EIA release, satisfying t(P) < t(A) by schedule
ACCESS (API's own statement)
                 "solely via subscription purchase through our authorized
                 redistributors: Refinitiv ... and Intercontinental Exchange (ICE)"
LAWFUL ROUTE     ICE Data Services distributes the API WSB with history BACK TO 2000,
                 weekly, via ICE Connect and ICE's Data API, including U.S. crude oil
                 inventories and regional Cushing detail, in machine-readable delivery.
COVERAGE vs NEED 2000 start PRE-DATES the 2012-01-05 EIA archive start, so the API leg
                 would not be the binding constraint on the usable window.
ENTITLEMENT      NOT HELD. No ICE or Refinitiv/LSEG entitlement exists on this machine
                 or in this repository.

API_PILOT_COVERAGE               = NOT TESTED (not 0 by rule — the route exists)
API_FIRST_REPORTED_RECONSTRUCTIBLE = UNVERIFIED
```

**An open point-in-time question survives even with an entitlement.** API revises its
weekly figures. Whether the ICE-distributed series carries the **first-reported** value or
a later revised one is undocumented on the pages checked, and it is exactly the trap the
EIA leg had to be rescued from at S0. It must be verified before any use, not assumed.

## §6 Quantity identity — partial, from documentation only

```
TARGET = weekly CHANGE in U.S. COMMERCIAL crude oil inventories EXCLUDING SPR

A  EIA WCESTUS1, "Weekly U.S. Ending Stocks excluding SPR of Crude Oil",
   THOUSAND BARRELS, a STOCK LEVEL — the CHANGE is derived, not published as such
C  Reuters / Platts survey material reports an expected CHANGE in MILLION BARRELS
P  API WSB reports U.S. crude oil inventories, level and change

DOCUMENTED NON-EQUIVALENCES ALREADY VISIBLE:
   units      thousand (EIA) vs million (survey reporting)         -> reconcilable
   stock vs change   EIA publishes a LEVEL; the surprise is on a CHANGE  -> derivation
                     must be defined and is an S1 task
   commercial vs total / SPR   API's series is an industry survey of operators, EIA's
                     excludes SPR explicitly; equivalence NOT verified
   sign convention   build-positive vs draw-positive differs across sources and is NOT
                     yet fixed (PINS-OD-1 leaves the final regressor form to S1)

QUANTITY_IDENTITY_PASS = PARTIAL / NOT VERIFIED PER ROW
```

The protocol's outcome-free consistency check — comparing a prior-week actual quoted in
survey material against the archived EIA vintage — **could not be run**, because no survey
material for a sample week was obtained. It is not waived; it is unreached.

## §7 The single Owner fact that could change this result

This is **not** a rescue attempt, and it is not one of the three rescues the controller
forbade. It is the one lawful route the protocol itself contemplates — its pass criteria
include *"no licensing or lawful-storage blocker"*, which presupposes that a licensed
route is legitimate — and which this seat cannot exercise.

```
WHAT FAILED   every route to a named, timestamped, lawfully storable consensus series
              that is REACHABLE WITHOUT A COMMERCIAL ENTITLEMENT.

WHAT WAS NOT TESTED
              LSEG (Reuters Polls / Commodity Insights), S&P Global Commodity Insights
              (Platts), and ICE (API WSB) as ENTITLED data products.

THE OWNER FACT
              Does Aaron hold, or will he authorise acquiring, an entitlement to a
              named survey family's historical US crude inventory consensus?
              AND does that product actually carry the weekly petroleum inventory poll
              at >= 95 % coverage with no calendar year below 90 %?

WHY IT IS NOT MINE TO DECIDE
              It is a procurement and entitlement question, not a scientific one.
              Protocol §15 and the controller brief agree: "Mechanical questions of
              archive retrieval do not require Fable." It equally does not require —
              or permit — me to answer it by treating "this seat could not reach it"
              as "it is not reachable".
```

**If that fact resolves NO**, the recommendation stands and CTA-EDGE-03-PINS closes at S0
as negative outcome class **A — DATA / PIT FAILURE**, with **no trial spent, no data
purchased, and no outcome ever generated**. That is a clean, cheap, honest close: the
lineage was killed by the gate designed to kill it, before it cost anything.

**If it resolves YES**, the correct next step is a **repeat of this same pilot against the
same frozen 45-date sample** using the entitled source. The sample, the thresholds and
this protocol are already fixed and committed, so re-running them costs nothing in
research degrees of freedom — which is precisely why they were frozen first.

## §8 What this result does NOT establish

* **Not** that inventory news is uninformative. No price was touched; Claim B was never
  approached.
* **Not** that the mechanism is absent. This is a data-availability finding.
* **Not** that the S0 design was wrong. The design is untested.
* **Not** that a consensus series does not exist. It plainly exists as a commercial
  product; it is not reachable from here.
* **Not** a licence to substitute API alone, a model expectation, or a calendar forecast
  field. All three are explicitly barred by PINS-OD-1, and none was used.

```
TRIAL SPENT           = NONE. No family declared, no member ran, nothing computed.
DATA PURCHASED        = NONE.
EXPOSURE LEDGER       = no outcome-exposure row written; no outcome was generated.
EVIDENCE CEILING      = unchanged and untouched (supported).
```
