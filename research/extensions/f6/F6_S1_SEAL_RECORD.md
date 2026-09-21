# CTA-EDGE-05 / F6 — S1 SEAL RECORD

```
SEAL_ID                  = CTA-EDGE-05-F6-S1-2026-09-21
SEAL_DATE                = 2026-09-21
LINEAGE                  = CTA-EDGE-05 / F6 MACRO_ANNOUNCEMENT_PREMIUM
SEAL_STATUS              = SEALED
OWNER_SEAL_AUTHORIZATION = YES
AUTHORIZATION_LITERAL    = "seal"
AUTHORIZED_BY            = Aaron (Owner)
PRESEAL_COMMIT           = 96901c48a0e5fe8cfd3d5e46db204a6e5a0e21f6
```

This record is the immutable seal identity. It is **superseded by citation,
never by rewriting**.

---

## §1 Sealed pins

These are the post-seal bytes. Each was computed after the sealed contract was
written and after the `F-F6` trial-ledger append, so none is stale.

```
SEALED_PREREGISTRATION_SHA256
  f26df71d4596dd8cacd261e571040b5b0e39fd37ef897c87422af31eeef275d9
  research/extensions/f6/F6_S1_PREREGISTRATION_SEALED.md

POST_SEAL_TRIAL_LEDGER_SHA256
  d57c56012267c78b1e5e06198ba12f3c9592b8a5c31195b68fa1db9aae5c5c67
  research/extensions/TRIAL_LEDGER.md   (F-F6 appended; 0 deletions)

OWNER_DECISION_RECORD_SHA256
  3390515aba1e742705e6c80e69053de2617b398ecd5a97440f9547a4f625a4d8
  ops/OWNER_DECISION_RECORD_CTA_EDGE_05_F6.md   (§12 appended; 0 deletions)

FINAL_ASTRA_REVIEW_SHA256
  23f723ed100ca71e11bc8b99f03a2ddf86988b0654ebb7b66e1537daf23ab589
  research/extensions/review_history/F6_FINAL_INDEPENDENT_REVIEW_2026-09-21_ASTRA_01.md

FINAL_EVENT_MANIFEST_SHA256
  49ff27bfc20eb98265c440bac7368e92022b356d77647dce9151f012e40ed382
  research/extensions/f6/F6_FINAL_EVENT_MANIFEST.json
```

### §1.1 Why the sealed manifest hash is NOT pinned here

```
AVOIDING A HASH CYCLE.
```

`F6_S1_SEALED_MANIFEST.json` is generated **after** this record and **pins this
record**. Pinning it back here would make each file's hash depend on the other's,
which is unsatisfiable. The dependency is therefore a one-way chain:

```
sealed preregistration
        |
        v
   F-F6 ledger append  +  Owner record §12
        |
        v
   THIS SEAL RECORD          (pins the five hashes above)
        |
        v
   F6_S1_SEALED_MANIFEST.json (pins this record and everything else)
        |
        v
   FINAL_SEALED_MANIFEST_SHA256 recorded EXTERNALLY —
   in the seal commit message and the task return.
```

Per the same rule, this record's own SHA256 is not written inside it; it is
recorded externally in the seal commit message and the task return, and is
pinned by the sealed manifest.

---

## §2 The frozen research constants

Restated here so the seal identity is readable without opening the contract. The
**sealed preregistration at the hash above is authoritative**; if this section
and that file ever disagree, that file wins and this one is wrong.

```
FINAL_PRIMARY_EVENT_COUNT   462   (FOMC 119 + CPI 176 + NFP 176 = 471 labels,
                                   9 multi-event overlaps, 471 - 9 = 462)
PRIMARY YEARS               2011 .. 2025 inclusive
2026                        NO F6 OUTCOME QUANTITY MAY BE FORMED
P2 POPULATION               3772 sessions, NO row dropped
OPENING BOUNDARY            2010-12-31, an INPUT BOUNDARY OBSERVATION only
WEEKDAY_REFERENCE           FRIDAY (Mon/Tue/Wed/Thu indicators + intercept)
COST                        0.0004 round trip = 2 bps entry + 2 bps exit
CASH PROXY                  DGS3MO, /365, OWNER-CHOSEN
YEAR_BLOCKS                 15
B                           100000
BOOTSTRAP_SEED_LITERAL      2540719150
BOOTSTRAP_SEED_SOURCE       CTA-EDGE-05|F6|S1_BOOTSTRAP|49ff27bfc20eb98265c440bac7368e92022b356d77647dce9151f012e40ed382
INTERVAL                    two-sided NOMINAL 95% percentile bootstrap
LOWER / UPPER               0.025 / 0.975
QUANTILE IMPLEMENTATION     numpy.percentile(..., method="linear")
PINNED ENVIRONMENT          numpy 2.5.0 · pandas 2.3.3 · python 3.13.14
SAMPLE_REUSE_CLASS          T0_REUSED_DEPENDENT
EVIDENCE_CEILING            SUPPORTED
INDEPENDENT_CONFIRMATION    NO
```

---

## §3 Authorization chain — three sources, never collapsed

```
FABLE          constructive design advice      OD-1 · OD-2 · OD-TY / OD-CASH
ASTRA          independent adversarial review  PASS / B_READY_FOR_S1_SEAL_WITH_
                                               CLAIM_CAP_NARROWING
                                               S1_SEAL_AUTHORIZED_BY_THIS_REVIEW = NO
AARON (OWNER)  adoption, and the SOLE seal authorization: "seal"
```

```
ADVICE IS NOT REVIEW. REVIEW IS NOT AUTHORIZATION.
THE INDEPENDENT REVIEW EXPRESSLY DECLINED TO AUTHORIZE THE SEAL.
ONLY AARON'S EXPLICIT "seal" DID.
```

```
HISTORICAL_PROVENANCE_RESERVATION = YES   (NONBLOCKING)
```

The pre-S0 independent adjudication was never persisted and **is not recovered**.
Nothing in this seal claims otherwise.

---

## §4 Accounting at seal

```
TRIAL_LEDGER_CHANGED          = YES   exactly one prospective row, F-F6
F_F6_ROW_COUNT                = 1
F6_FAMILY_STATUS              = SEALED / NOT EXECUTED
F6_PRIMARY_TRIAL_SPENT        = NO
F6_PRIMARY_TRIAL_CONSUMED     = NO
VARIANT_ATTEMPT ROWS ADDED    = 0
EXPOSURE_LEDGER_CHANGED       = NO
F6_PERFORMANCE_EXPOSURE_ADDED = NO
```

No exposure row exists because **no F6 return or target measurement has been
revealed**, and no new exposure type was invented to accommodate a seal.

---

## §5 Firewall attestation — the seal itself was outcome-blind

```
F6_RETURN_OUTCOME_ACCESSED = NO     SPY PRICE VALUES READ      = NO
F6_PRIMARY_RETURN_COMPUTED = NO     R / r_excess / r_net       = NOT COMPUTED
BETA_EVENT_COMPUTED        = NO     BOOTSTRAP_EXECUTED         = NO
CI COMPUTED                = NO     SHARPE COMPUTED            = NO
LOYO PERFORMANCE COMPUTED  = NO     TLT INSPECTED              = NO
F6.b COMPUTED              = NO     2026 F6 RETURNS READ       = NO
NQ OUTCOME DATA INSPECTED  = NO     RESULT ARTIFACT EXISTS     = NO
```

The SPY panel was opened for its **date index and column presence (`notna`)
only**. No price value was read, printed, stored or used arithmetically at any
point up to and including the seal.

---

## §6 Post-seal authorization state

```
S1                       = SEALED
S2_BUILD_AUTHORIZED      = YES
S3_RUN_AUTHORIZED        = NO
RETURN_REVEAL_AUTHORIZED = NO
```

```
S2 AUTHORIZES CODE AND BUILD WORK ONLY.
IT DOES NOT AUTHORIZE RUNNING THE HISTORICAL F6 OUTCOME.
```

The historical run remains forbidden until **all three** hold: S2 implementation
is complete; implementation acceptance passes; and a **separate** S3 run
authorization is issued by Aaron.
