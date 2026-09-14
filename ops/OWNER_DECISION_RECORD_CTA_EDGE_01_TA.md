# OWNER DECISION RECORD — CTA-EDGE-01-TA (Treasury auction supply absorption)

```
RECORD_TYPE        = OWNER_DECISION_RECORD
LINEAGE            = CTA-EDGE-01-TA
DATE_OF_DECISIONS  = 2026-09-15
OWNER              = Aaron  (the only authority for every decision recorded here)
RELAY              = programme controller (Aaron-side ChatGPT), CTA-EDGE-01-TA
                     S1 DESIGN + PRE-SEAL REPAIR + CONDITIONAL SEAL task brief
RECORDED_BY        = Claude Opus 5 (Main Agent / builder seat), S1 session 2026-09-15
WORKFLOW_AUTHORITY = ../QUANT_WORKFLOW_VNEXT.md  (vNext, cutover 2026-09-12)
```

**What this file is.** The durable record of the Owner decisions that closed S0 for
`CTA-EDGE-01-TA` and authorised entry to S1 with a conditional seal. It records
**decisions**, not workflow authority.

**What this file is not.** Not a preregistration, not authorisation to implement, not
authorisation to run, not an exposure event. It creates no row in
`EXPOSURE_LEDGER.md`, no record in `EXECUTION_AUTHORIZATIONS.md`, and no trial in
`../research/extensions/TRIAL_LEDGER.md`. Writing this record revealed no outcome and
computed no performance.

---

## §1 Stage state at the time of recording

```
S0_STATUS                     = COMPLETE — PASS (accepted by the controller)
S1_ENTRY_AUTHORIZED           = YES
S1_SEAL_AUTHORIZED            = YES, CONDITIONAL on every mandatory condition passing
S1_SEALED                     = YES  (2026-09-15; TA_SEAL_MANIFEST.md)
S2_BUILD_AUTHORIZED           = NO
MACRO_CALENDAR_ACQUISITION_AUTHORIZED = NO
TARGET_RUN_AUTHORIZED         = NO
REVEAL_AUTHORIZED             = NO
```

---

## §2 The decisions

### TA-OD-1 — the M2 risk-adjusted usefulness floor

```
DECISION   = M2 = +0.30 annualised CALENDARISED Sharpe
STATUS     = OWNER-CONFIRMED
CONFIRMED  = YES, BEFORE any candidate outcome was accessed, computed or inferred
TYPE       = Owner methodology decision (vNext section 10)
```

Provenance: +0.30 is this programme's **existing** materiality floor for
"economically material", taken from Aaron's C-A Owner decision OD-1 and re-confirmed
for this lineage. It is **not** derived from any Treasury-auction literature effect
size and **not** derived from any observed outcome.

**Binding constraint.** The threshold was fixed before exposure and **must not be
changed after exposure**, in either direction, for any reason. A later session
proposing to move it is proposing a new lineage, not an amendment.

The construction that the floor is applied to is sealed at
`research/extensions/ta/TA_PREREGISTRATION.md` §F — a calendarised monthly series over
a fixed 244-month grid with zero months retained,
`mean / sd(ddof=1) × sqrt(12)`, risk-free = 0.

### TA-OD-2 — primary claim type and object

```
PRIMARY_CLAIM_TYPE = REDUCED_FORM
PRIMARY_OBJECT     = the auction-cycle effect as it reaches a liquid duration ETF
```

Accepted. A dealer / intermediation causal claim is **NOT PRIMARY**, **NOT
ESTABLISHED**, and the dealer cell remains **PARKED**.

### TA-OD-3 — instrument mapping

```
PRIMARY_INSTRUMENT   = TLT
SECONDARY_INSTRUMENT = IEF   (declared secondary, NO rescue power)
20Y                  = not part of primary or secondary
```

### TA-OD-4 — the five mandatory pre-seal repairs

Accepted and not reopened:

1. remove SHY's hard-placebo / kill role;
2. weaken the "exact drift cancellation" wording;
3. correct the actual flat-gap trading path around `t0`;
4. define the M2 Sharpe construction and its interval precisely;
5. add an identification/dependence failure class and diagnostic `DAMAGE_POWER`.

Discharge is recorded item by item in
`research/extensions/ta/TA_S0_REPAIR_RECORD.md` and implemented in the sealed
contract.

### TA-OD-5 — limited S1 data authorisation

```
GRANTED   = official, non-outcome Treasury auction metadata only
AUTHORITY = U.S. Treasury Fiscal Data "Treasury Securities Auctions Data";
            TreasuryDirect official schedule / documentation
CEILING   = research event calendar restricted to <= 2026-06-12
CONSUMED  = YES, once. 2,373 Note/Bond rows retrieved 2026-09-14T16:55:38Z,
            pinned by sha256 in research/extensions/ta/TA_DATA_MANIFEST.md
NOT GRANTED = NY Fed dealer positions, ZN/ZB futures, when-issued prices, cash
            Treasury returns, NAV data, CFTC data, CPI/payrolls/FOMC calendars,
            or any other research dataset
```

Auction **outcome** fields — yields, prices, bid-to-cover, bidder allotments — were
deliberately **not requested**, although the grant would have permitted them, because
the sealed design does not use them.

---

## §3 What no agent may infer from this record

- A seal is **not** authorisation to build, acquire, execute or reveal.
- TA-OD-5 is **consumed** and authorises no further acquisition, including the CPI,
  Employment Situation and FOMC calendars that the sealed §G.3 diagnostic requires —
  those need a **separate** Owner data authorisation at S2.
- Nothing here alters canonical TSMOM, C-A, C-D or any closed lineage.
- `D-ETF-COUNT` is **not** decided here and remains
  `UNKNOWN_PENDING_AARON_DECISION`.

---

## §4 Outstanding Owner decisions for this lineage

| # | decision | when |
|---|---|---|
| 1 | Accept or reject the S1 seal | now, on controller review |
| 2 | S2 BUILD authorisation | after seal acceptance |
| 3 | Macro-calendar data acquisition (CPI, Employment Situation, FOMC) | at S2 |
| 4 | Single-use execution authorisation for the one governed historical run | after S2 acceptance |
| 5 | Single-use reveal authorisation | after the run |
| 6 | Final verdict and any knowledge-base registration | at S4 |

None of these is taken here.
