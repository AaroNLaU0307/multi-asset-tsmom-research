# CTA-EDGE-03-PINS — CLOSURE

```
LINEAGE                      = CTA-EDGE-03-PINS  (physical inventory news × scarcity)
LINEAGE_STATUS               = CLOSED_PRE_OUTCOME
FAILURE_TYPE                 = DATA_PIT_ACCESS_NOT_ESTABLISHED
CLOSED_UTC                   = 2026-09-16
CLOSED_BY                    = programme controller decision, relayed to the Main Agent
                               seat; recorded here at the CTA-EDGE-04 opening

MECHANISM_TESTED             = NO
WTI_RESPONSE_TESTED          = NO
SCARCITY_MODERATION_TESTED   = NO

HISTORICAL_OUTCOME_EXPOSED   = NO
TRIAL SPENT                  = NONE
DATA PURCHASED               = NONE
EXPOSURE LEDGER              = no outcome-exposure row; no outcome was ever generated

REOPEN_ONLY_IF               = new concrete lawful access to the required point-in-time
                               expectation inputs

FROZEN_AUDIT_SAMPLE          = research/extensions/pins/PINS_AUDIT_SAMPLE.json
                               sha256 52e70b40e61a7b36057e2345f116c94bdab9ab091f6caa4bdf7d78178204283a
                               45 releases · 3 per year 2012–2026 · 30 ordinary
                               Wednesdays + 15 shifted/irregular · 2012-05-02 … 2026-06-24
                               Frozen and committed at db78c90040b3ff6d7fde09a2eb2d307c43d16ea0
                               BEFORE any retrieval was attempted.
```

This document records a closure. It **reopens nothing**, modifies no accepted PINS
decision, and authorises nothing.

---

## 1. Why it closed

PINS-OD-1 bound the lineage to **CONDITIONAL OPTION 1**: a named pre-API analyst-survey
consensus (`C`) as the expectation anchor, **and** the first-reported API pre-release
estimate (`P`) as a mandatory second point-in-time input, with **both** required to be
historically reconstructible.

The feasibility audit, run against a sample frozen before any retrieval, returned:

```
Family 1  Reuters / LSEG          0 of 45   (required >= 41)   FAIL
Family 2  S&P Global Platts       0 of 45   (required >= 41)   FAIL   (the one permitted retry)
API leg                           NOT TESTED — a lawful documented route exists
                                  (ICE Data Services, API WSB, history from 2000) but no
                                  entitlement is held, and first-reported-versus-revised
                                  status is unverified
```

Economic-calendar "forecast" fields were **refused by rule** — no named survey family, no
forecast publication timestamp, and an explicit prohibition on use and storage. That
refusal is the substance of the closure, not an obstacle around it: the route that would
have made the lineage look feasible is the one that could not be attributed.

Full record: [`PINS_OD1_FEASIBILITY_RESULT.md`](PINS_OD1_FEASIBILITY_RESULT.md).

## 2. What this closure is NOT

- **NOT** evidence that inventory news is uninformative. No price was ever touched and
  Claim B was never approached.
- **NOT** falsification of the mechanism. Nothing was tested.
- **NOT** a finding that the S0 design was wrong. The design is untested.
- **NOT** a finding that a consensus series does not exist. It plainly exists as a
  commercial product; it was not reachable without an entitlement.

## 3. What is preserved

The S0 frame, the S0 amendment, PINS-OD-1 and its controller qualifiers, the feasibility
protocol, the frozen audit sample and the EIA release calendar are all preserved exactly
as committed. Nothing is rewritten and nothing is deleted.

One work product outlives the lineage and is recorded as reusable: the **EIA
first-published vintage path** — 765 archived WPSR releases, 2012-01-05 … 2026-09-10,
each with 15 machine-readable CSVs, enumerated in
[`PINS_EIA_RELEASE_DATES.txt`](PINS_EIA_RELEASE_DATES.txt). It is the same archive that
the parked F4 `INVENTORY_STATE_COMMODITY_CURVE` candidate would need.

## 4. Design-contributor status, unchanged

```
ASTRA_DESIGN_EXPOSED = YES   material_design_contributor (REVIEWER_EXPOSURE_LOG S38)
FABLE_DESIGN_EXPOSED = YES   material_design_contributor via adopted PINS-OD-1 advice (S37)
```

Both remain barred from blind certification of this design. **Closure does not lift a
bar.**

## 5. Reopening

Reopening requires **new concrete lawful access to the required point-in-time expectation
inputs** — specifically a named survey family's historical consensus meeting the frozen
coverage thresholds, together with a first-reported API series. If such access is
obtained, the correct step is to re-run the **existing** pilot against the **existing**
frozen sample; the protocol and thresholds are already committed, so a retry spends no
research degrees of freedom.

Any change to the expectation concept itself — API alone, a model expectation, or an
undocumented calendar field — is **not** a reopening of PINS. Each would be a separately
named lineage, as PINS-OD-1 already records.

```
NEXT LINEAGE = CTA-EDGE-04-MMV (macro momentum on vintage data), opened separately
```
