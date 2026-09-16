# CTA-EDGE-02-BENB — S4 VERDICT AND LINEAGE CLOSURE

```
LINEAGE                             = CTA-EDGE-02-BENB  (bond ETF - NAV basis)
CONTRACT_ID                         = CTA-EDGE-02-BENB-PREREG-01
STATUS                              = CLOSED
CLOSED_UTC                          = 2026-09-16
CLOSED_BY                           = programme controller decision (Aaron-side ChatGPT),
                                      relayed to the Main Agent seat

S3_RESULT                           = ACCEPTED
FINAL_CLASS                         = A-M — MIXED NON-HARVESTABLE CONVERGENCE
PROGRAMME_STATUS                    = NOT_PROMOTED

PRIMARY_CLAIM_SUPPORTED             = NO
TRADABLE_CONVERGENCE_SUPPORTED      = NO
OVERNIGHT_PRICE_DISCOVERY_SUPPORTED = YES
NAV_CATCH_DOWN_SUPPORTED            = YES
MECHANISM_FALSIFIED                 = NO
HARVESTABLE_NEXT-OPEN-TO-CLOSE_EDGE = NOT SUPPORTED

PORTFOLIO_TEST_AUTHORIZED           = NO
RETUNE_AUTHORIZED                   = NO
SECOND_RUN_AUTHORIZED               = NO

HISTORICAL_OUTCOME_EXPOSED          = YES
EVIDENCE_CEILING                    = supported  (never independently confirmed)

SEALED_PREREG_SHA256                = 1b7ca2122ba14c4097e4d76d7a733bf0c77ab9c0d02dd93a38c25bc1be5160cf
S1_SEAL_MANIFEST_SHA256             = 6aa0d21401b9887f4a44ab6559fa10d7a59ae5a8b512e1ad306543c061483703
S1_SEAL_COMMIT                      = c1a3f8155a9fdb86d55b620c33498f604fcbf8d0
S2_BUILD_COMMIT                     = d1ccefc8c6ed6e15e6366856ff0b64a0f6516bc3
S3_AUTHORIZATION_COMMIT             = 39e9bdce9f6530f163d76683f512f8a0eaa230e5
S3_RUN_COMMIT                       = 90dd5aab74485f83a3758e1987ca34c2313e7ae1
RUN_ID · AUTHORIZATION_ID           = BENB-RUN-20260915-01 · BENB-AUTH-0001 (CONSUMED)
```

This document records the accepted S4 verdict and closes the lineage. It **amends no
seal**, deletes nothing, recomputes nothing, and authorises nothing.

---

## 1. The verdict, and how it was reached

One governed historical run, under a single-use grant, with a seed derived from the seal
rather than from any outcome. The sealed §J.3 order is first-match-wins and it matched at
STEP 1:

```
L_T <= 0   AND   (U_N < 0)   AND   (L_O > 0)      ->   A-M
```

| estimand | point | 95 % interval | reading |
|---|---:|---|---|
| `beta_T` tradable, open(t+1)→close(t+1) | 787.98 | [ −14.53, 1432.72 ] | **NOT SUPPORTED** |
| `beta_O` overnight, close(t)→open(t+1) | 1448.39 | [ 555.23, 2014.54 ] | supported **positive** |
| `beta_N` NAV, t→t+1 | −2096.99 | [ −2783.12, −1898.88 ] | supported **negative** |

Gate 2 and the leave-one-year-out diagnostic were computed and recorded, and under the
sealed order **neither was consulted** — both sit after Gate 1. Full detail:
[`s3/BENB_S3_RUN_RECORD.md`](s3/BENB_S3_RUN_RECORD.md),
[`s3/BENB_S3_RESULT.json`](s3/BENB_S3_RESULT.json).

## 2. The research lesson

> The ETF–NAV basis **contained information**, but the convergence was materially
> expressed through (1) **overnight ETF price discovery before legal NAV-informed entry**
> and (2) **subsequent NAV catch-down** — not through a supported next-open-to-close
> tradable convergence edge.

This is the sealed design working as intended. The three-component decomposition existed
precisely so that "the discount closes" could be separated from "a CTA can harvest the
close". The discount does close. The part a lawful entry can reach does not carry a
supported coefficient.

**Carried forward as a design rule:** when the signal is published after a market's
close and the earliest lawful entry is the next open, the decomposition that separates
the unreachable overnight leg from the reachable intraday leg must be **in the sealed
contract**, not added later. Here it was, and it is the whole reason this lineage
produced an interpretable negative instead of an ambiguous one.

## 3. The feature-design lesson — recorded, and deliberately not acted on

The sealed expanding-median abnormal-basis definition produced a **highly persistent
discount-side state**:

```
3,555 / 4,415 eligible observations  =  80.52 % on the discount side
```

An expanding median carries the entire history, so once the basis level shifts, most
later observations sit below it. The sealed contract left `DISCOUNT_OBSERVATION_COUNT`
**unknown at seal** precisely so this number could not reach the cost model, the
inference, the materiality bars or the taxonomy. It did not.

**This is a feature-design lesson only.** It does **NOT** authorize, inside this or any
lineage:

```
changing the threshold          rolling z-score            top-decile discount selection
longer holding                  overnight capture          LQD promotion
premium-side shorts
```

Any such hypothesis is a **NEW LINEAGE** with its own S0, its own trial accounting and
its own Owner authorisations. Reading a tuning knob off an exposed outcome is the
specific failure this programme is built to prevent, and the fact that the knob is
visible is not a reason to turn it.

## 4. What this closure IS NOT

- **NOT falsification of the mechanism.** `MECHANISM_FALSIFIED = NO`. Both diagnostic
  legs fired: the abnormal discount demonstrably converges. What is unsupported is a
  harvestable next-open-to-close response, under this signal timing, on this sample.
- **NOT a claim that ETF–NAV basis carries no information.** It carried information;
  the information was expressed where a lawful entry could not reach it.
- **NOT evidence about authorised-participant behaviour, dealer balance sheets, NAV
  correctness in any legal or accounting sense, credit mispricing, crisis
  diversification, or any TSMOM improvement.** The sealed §K forbidden-interpretation
  block binds this negative reading exactly as it would have bound a positive one.
- **NOT an independently confirmed result.** `EVIDENCE_CEILING = supported`. The
  HYG/LQD price leg is reused / burned context (KB-1, 6 of 6); the NAV leg is new but a
  new NAV leg does not launder a reused price sample. Combined provenance is
  MIXED / DEPENDENT.
- **NOT a portfolio finding.** No portfolio test exists in the sealed contract and
  `PORTFOLIO_TEST_AUTHORIZED = NO`.

## 5. What is preserved unchanged

The S0 frame, the S0 repair record, the sealed preregistration, the seal manifest, the
pre-seal validator and all twelve S2 implementation modules are byte-unchanged and were
re-verified after the run (`git diff d1ccefc8..HEAD`).

```
BENB_SEAL_MODIFIED           = NO
BENB_REDESIGNED              = NO
SECOND_RUN_PERFORMED         = NO
ALTERNATE_SEED_USED          = NO
POST_OUTCOME_TUNING          = NO
DESIGN_CHANGED_AFTER_EXPOSURE = NO
```

`benb_s3_validate.py` returns **47/47 PASS** and `benb_tests.py` **65 passed** at the
closing commit. `benb_prereg_validate.py` returns **71/72** by design: its one failing
check, `E/no execution authorization exists for this lineage`, is an S1-seal-time *state*
assertion that a governed run legitimately invalidates. All 71 checks of the sealed
contract's **content** pass. The validator was not modified — see
[`s3/BENB_S3_RUN_RECORD.md`](s3/BENB_S3_RUN_RECORD.md) §16a.

## 6. Accounting

```
TRIAL SPENT              = ONE. F-BENB / BENB-PRIMARY, m = 1.
                           BENB_PRIMARY_TRIAL_SPENT = YES (TRIAL_LEDGER.md §6.2).
                           Gate 2 was computed but not consulted and spends no
                           separate trial; diagnostics, the LQD secondary and the
                           descriptives are not attempts and never enter N_trials.
ETF PANEL BURN           = the reuse OCCURRED. The KB-1 addendum carries an appended
                           row, "Exposure after the S3 governed run =
                           REVEALED_TARGET_METRIC". The panel is now outcome-exposed
                           for this lineage and may not be reused as fresh
                           independent confirmation of it.
NAV SERIES               = now outcome-exposed as part of the same joined object.
N_trials                 = NOT ASSERTED, unchanged.
D-ETF-COUNT              = untouched, still UNKNOWN_PENDING_AARON_DECISION.
EXECUTION AUTHORIZATIONS = BENB-AUTH-0001, CONSUMED. Zero live grants. No further
                           BENB historical execution is authorised by anything in
                           committed state.
EXPOSURE LEDGER          = row 54 (REVEALED_TARGET_METRIC, the run) and the closure
                           row appended here (NO_OUTCOME — this closure reveals
                           nothing new).
```

## 7. Design-contributor and seat status, unchanged

Claude Fable 5.1 remains `material_design_contributor` for CTA-EDGE-02-BENB
(`ops/REVIEWER_EXPOSURE_LOG.md` S34) and remains **barred from blind certification** of
this design or any result under it. Closure does not lift a bar.

The Main Agent seat (S35 design/implementation, S36 governed run) is **outcome-exposed**
and is the producer of both the design and the implementation. It may not certify,
verify or adjudicate what it generated.

`ASTRA_DESIGN_EXPOSED = NO` for this lineage (`BENB_PREREGISTRATION.md` §L) and is
unchanged by this closure.

## 8. Reopening

Reopening CTA-EDGE-02-BENB is **not** a bounded repair and is **not** available to any
agent. The sealed contract's own prohibitions stand, and the exposed outcome now adds a
second, independent bar: any redesign informed by what this run revealed would be
post-outcome design. A different signal timing, a different instrument, an intraday
design, a threshold or selection rule, a longer holding period, an overnight leg, an LQD
primary or a premium-side strategy would each be a **new lineage** — with its own S0,
its own seal, its own trial accounting, its own Owner authorisations, and an explicit
declaration that its design was informed by an exposed outcome.

```
NEXT LINEAGE = CTA-EDGE-03-PINS (physical inventory news x scarcity), opened separately
```
