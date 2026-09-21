# CTA-EDGE-02-BENB — S3 SINGLE GOVERNED HISTORICAL RUN — RUN RECORD

    LINEAGE                     CTA-EDGE-02-BENB   (bond ETF - NAV basis)
    STAGE                       S3 GOVERNED HISTORICAL RUN
    RUN_ID                      BENB-RUN-20260915-01
    AUTHORIZATION_ID            BENB-AUTH-0001        scope ONE_SHOT
    RNG_SEED                    1788924436            B = 10,000
    EXECUTION_COUNT             1
    HISTORICAL_OUTCOME_EXPOSED  YES
    EVIDENCE_CEILING            supported             never independently confirmed

    BRANCH                      cta-edge/bond-etf-nav-s0
    PRE-AUTH HEAD               d1ccefc8c6ed6e15e6366856ff0b64a0f6516bc3  (accepted S2)
    AUTHORIZATION COMMIT        39e9bdce9f6530f163d76683f512f8a0eaa230e5  (pre-run)
    S1 SEAL MANIFEST sha256     6aa0d21401b9887f4a44ab6559fa10d7a59ae5a8b512e1ad306543c061483703
    SEALED PREREG sha256        1b7ca2122ba14c4097e4d76d7a733bf0c77ab9c0d02dd93a38c25bc1be5160cf

    FINAL_CLASS                 A-M   MIXED NON-HARVESTABLE CONVERGENCE
    PROGRAMME_STATUS            not_promoted
    FAILURE_TYPE                GATE_1_NOT_SUPPORTED — the tradable leg's 95 % interval
                                straddles zero while BOTH diagnostics fire

This record reports what the sealed contract produced. It does **not** interpret the
result beyond the sealed §J taxonomy, does not propose a follow-up, and does not begin
S4. The figures below are the one authorised reveal of this lineage's statistics.

---

## 1. ORDERING — WHAT HAPPENED, IN WHAT ORDER

The ordering is the evidence that the authorization preceded the outcome, so it is
recorded before the numbers.

1. **Pre-authorization verification.** Branch `cta-edge/bond-etf-nav-s0`, HEAD
   `d1ccefc8` = the accepted S2 commit, worktree clean. All twelve sealed and pinned
   sha256 values reproduced. `benb_prereg_validate.py` 72/72 PASS. **Zero** BENB
   authorization records, **zero** lifecycle records, **zero** BENB run ids, **no** BENB
   result artifact anywhere in the repository, and **no** exposure-ledger row recording
   a BENB reveal.
2. **The grant was written and, while still only in the working tree, the guard was
   asked whether a real run was authorized. It answered `NO`** —
   `active_execution_authorizations = 0`. Granting requires committed state; blocking
   does not. That asymmetry was demonstrated, not assumed.
3. **Commit `39e9bdce`** — the single-use grant plus `benb_s3_run.py`, the run driver.
   The driver is in the *pre-run* commit deliberately: the code that would touch the
   outcome is fixed in committed bytes before any outcome exists.
4. **Re-verification after commit.** The guard recognised exactly `BENB-AUTH-0001`,
   accepted `run_id` `BENB-RUN-20260915-01`, and refused both a mutated BENB run id and
   another lineage's run id. Every bound identity matched. The grant was unconsumed.
5. **ONE invocation** of `benb_s3_run.py --execute`.
6. The result artifact was written, the grant was marked `CONSUMED`, and the exposure,
   trial and seat ledgers were appended.

No preview, no dry run, no exploratory pass, and no second invocation occurred at any
point. The driver refuses to start without `--execute` and refuses outright if a
governed result already exists on disk.

---

## 2. THE GRANT

```
authorization_id            BENB-AUTH-0001
scope                       ONE_SHOT_SINGLE_OUTCOME_BEARING_RUN
grant_kind                  EXECUTION
binding.lineage             CTA-EDGE-02-BENB
binding.run_id              BENB-RUN-20260915-01
binding.rng_seed            1788924436
binding.sealed_prereg       1b7ca2122ba14c4097e4d76d7a733bf0c77ab9c0d02dd93a38c25bc1be5160cf
binding.s1_seal_manifest    6aa0d21401b9887f4a44ab6559fa10d7a59ae5a8b512e1ad306543c061483703
binding.s1_seal_commit      c1a3f8155a9fdb86d55b620c33498f604fcbf8d0
binding.s2_implementation   d1ccefc8c6ed6e15e6366856ff0b64a0f6516bc3
binding.bootstrap_replicates 10000
```

The seed is **outcome-independent by construction**: `int("6aa0d214", 16) = 1788924436`,
where `6aa0d214` is the first eight hexadecimal digits of the accepted S1 seal-manifest
sha256. It is derived from the seal, fixed before the run, and recorded in the grant.
No second seed exists and none was tried.

---

## 3. LEVEL-1 PRE-RUN INTEGRITY — the phase boundary that protects the trial

Phase 1 verifies identities and reproduces the **sealed structural counts**. It computes
no basis, no feature and no outcome, so an abort there would have spent no trial. All
seven pinned files reproduced their sealed sha256 and both seal documents were
unchanged.

| | HYG | LQD |
|---|---:|---:|
| common grid dates (date-only intersection) | **4,887** = sealed 4,887 | **6,069** = sealed 6,069 |
| structurally eligible (§D.2) | **4,415** = sealed 4,415 | **5,539** = sealed 5,539 |
| excluded: 250-observation burn-in | 250 | 250 |
| excluded: no next grid date | 1 | 1 |
| excluded: t+1 is an ex-date (§D.4 union) | 221 | 279 |
| grid span | 2007-04-11 … 2026-09-11 | 2002-07-30 … 2026-09-11 |

Both sealed structural counts reproduced **exactly**, from the pinned bytes, through the
independently written §D.2 implementation. That is the strongest available pre-run
evidence that the S0-repair structural facts and the S2 implementation agree.

---

## 4. FEATURE REALISATION — now legitimately outcome-exposed

Reported mechanically, as §6 of the run brief requires. **None of it was used to change
anything**: the design was sealed at S1 and is byte-unchanged.

```
HYG structurally eligible observations      4,415
HYG primary discount observations (x_t < 0) 3,555
    as a percentage of eligible             80.52 %
HYG premium observations (x_t >= 0)           860
signal span                                 2008-04-11 .. 2026-09-10
calendar years represented                  19
entry-month grid                            222 months (2008-04 .. 2026-09)
zero-signal months                          2      (2008-12, 2009-01)
maximum signals in one entry month          22     (2011-03)
discount severity d_t   min 4.08e-08   mean 0.004278   max 0.099925
```

**Signals by calendar year** (the bootstrap's blocks):

| year | n | year | n | year | n | year | n |
|---|---:|---|---:|---|---:|---|---:|
| 2008 | 83 | 2013 | 226 | 2018 | 223 | 2023 | 171 |
| 2009 | 86 | 2014 | 233 | 2019 | 213 | 2024 | 210 |
| 2010 | 214 | 2015 | 203 | 2020 | 141 | 2025 | 205 |
| 2011 | 196 | 2016 | 175 | 2021 | 230 | 2026 | 158 |
| 2012 | 214 | 2017 | 223 | 2022 | 151 | | |

**Signals by month of year** — flat, as a calendar artefact check would want:

| Jan | Feb | Mar | Apr | May | Jun | Jul | Aug | Sep | Oct | Nov | Dec |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 277 | 294 | 305 | 295 | 323 | 322 | 285 | 331 | 319 | 292 | 256 | 256 |

**One mechanical observation, recorded and not acted on.** 80.52 % of eligible
observations fall on the discount side. That is a property of an *expanding* median
applied to a basis series that drifts: the median carries the whole history, so once the
level shifts, most later observations sit below it. The sealed contract chose the
expanding median and chose to leave `DISCOUNT_OBSERVATION_COUNT` **unknown at seal**
precisely so this number could not influence the cost model, the inference, the
materiality bars or the taxonomy. It did not. It is reported because §6 requires it, and
it changes nothing.

---

## 5. THE THREE SEALED COMPONENTS AND THE IDENTITY

For every eligible discount observation:

```
R_OVERNIGHT = ln(P_open,t+1 / P_close,t)
R_TRADABLE  = ln(P_close,t+1 / P_open,t+1)
R_NAV       = ln(NAV_t+1 / NAV_t)
```

The sealed identity `Δb = R_OVERNIGHT + R_TRADABLE − R_NAV` was checked on **every**
observation used, with `Δb` computed independently from the endpoint basis levels rather
than from the components:

| cell | observations checked | max abs residual | tolerance |
|---|---:|---:|---|
| HYG | 3,555 | **0.0** | 1e-12 |
| LQD | 3,840 | **0.0** | 1e-12 |

No material identity failure. The run therefore proceeded to the scientific verdict, as
the contract allows.

*A note on scope.* A second, differently associated cross-check (`math.fsum` over the
three legs) was **deliberately not run**: it would have required re-opening the
historical panel, and the grant authorised exactly one historical execution. The
identity check that exists is the one the sealed contract specifies, run inside the
authorised execution, over every observation.

---

## 6. GATE 1 — HYG PRIMARY

Sealed regressions on the discount-only sample, one regressor, three separate fits;
95 % percentile intervals from the ONE calendar-year block bootstrap,
`B = 10,000`, seed `1788924436`, all 10,000 replicates valid. Units are basis points of
return per unit of log discount severity `d_t`.

| estimand | point | 95 % interval | reading |
|---|---:|---|---|
| **`beta_T`** tradable (open→close, t+1) | **787.98** | **[ −14.53, 1432.72 ]** | **NOT SUPPORTED** — `L_T ≤ 0` |
| `beta_O` overnight (close t → open t+1) | 1448.39 | [ 555.23, 2014.54 ] | supported **positive** |
| `beta_N` NAV (t → t+1) | −2096.99 | [ −2783.12, −1898.88 ] | supported **negative** |

```
GATE1_PASS  (L_T > 0, STRICT)   NO
```

The point estimate of `beta_T` is positive and its leave-one-year-out minimum is
positive, but the sealed gate is the **interval**, not the point estimate, and the
interval includes zero. That is the rule as written, and it is applied as written.

---

## 7. GATE 2 — COMPUTED, RECORDED, AND NOT CONSULTED

Under the sealed §J.3 first-match-wins order, `L_T ≤ 0` terminates at STEP 1, so Gate 2
never enters the verdict. It was computed and is recorded for completeness and for
future mechanical audit.

Fixed trade, exactly as sealed: long 1 unit at `open(t+1)`, flat at `close(t+1)`, 5 bps
one way / 10 bps round trip, `NET_TRADE_RETURN = R_TRADABLE − 10 bps`, charged once per
signal, never sized by severity, never held overnight.

| quantity | point | 95 % interval | bar | pass |
|---|---:|---|---|---|
| mean `NET_TRADE_RETURN` | **−11.19 bps** | [ −13.69, −9.51 ] | M1 `L_R > 0` STRICT | **NO** |
| calendarised Sharpe (monthly, ×√12, rf = 0, ddof = 1) | **−3.057** | [ −2.636, −1.274 ] | M2 `L_S > +0.30` STRICT | **NO** |

Monthly P&L was built on the complete 222-month calendar grid, trades assigned by
**entry** month, and the two zero-signal months retained as exactly 0.

**A mechanical property worth recording.** The Sharpe's percentile interval
`[−2.636, −1.274]` does **not** contain its point estimate `−3.057`. This is expected
behaviour of a year-block percentile bootstrap on a fixed calendar grid, not a defect: a
replicate that omits some years leaves their months at zero and doubles others, which
raises the monthly standard deviation and pulls the replicate Sharpe toward zero. Every
one of the other four intervals contains its point estimate. It changes nothing here —
M2 fails at `L_S = −2.636` either way, and Gate 2 is not consulted at all — but a later
reader should see it stated rather than discover it.

---

## 8. LEAVE-ONE-CALENDAR-YEAR-OUT

The single sealed fragility diagnostic. `beta_T` re-estimated on the frozen observation
tuples with one whole calendar year dropped.

| dropped | `beta_T` | dropped | `beta_T` | dropped | `beta_T` | dropped | `beta_T` |
|---|---:|---|---:|---|---:|---|---:|
| 2008 | **224.62** | 2013 | 795.40 | 2018 | 802.26 | 2023 | 804.86 |
| 2009 | 820.77 | 2014 | 797.64 | 2019 | 810.02 | 2024 | 820.18 |
| 2010 | 980.27 | 2015 | 781.68 | 2020 | 767.99 | 2025 | 793.09 |
| 2011 | 815.22 | 2016 | 795.22 | 2021 | 793.13 | 2026 | 796.60 |
| 2012 | 836.41 | 2017 | 811.59 | 2022 | 795.46 | | |

```
LOYO_PASS   YES   (all 19 omitted-year point estimates > 0)
range       224.62 (dropping 2008)  ..  980.27 (dropping 2010)
```

LOYO is consulted only **after** Gate 1 is supported (§J.3 STEP 6). Gate 1 was not
supported, so this diagnostic did not enter the verdict either. It is recorded because
the contract requires it to be run and reported.

---

## 9. LQD SECONDARY — NO PROMOTION POWER, NO RESCUE POWER

Identical sealed definitions, identical code path, its own interval, reported once
alongside. 3,840 discount observations over 24 calendar years, 1,699 premium
observations.

| estimand | point | 95 % interval |
|---|---:|---|
| `beta_T` | 1017.76 | [ −1980.32, 2245.45 ] |
| `beta_O` | 1498.45 | [ 893.29, 2030.18 ] |
| `beta_N` | −1845.86 | [ −4321.38, −803.79 ] |
| mean `NET_TRADE_RETURN` | −11.10 bps | [ −12.55, −9.98 ] |
| calendarised Sharpe | −3.137 | [ −2.527, −1.360 ] |
| leave-one-year-out | fails (min −1279.75, dropping 2008) | |

LQD tells the same qualitative story as HYG and rescues nothing, which is exactly the
status it was given at seal. **`classify_primary()` takes the primary cell and nothing
else**; there is no parameter through which this table could have reached the verdict.

---

## 10. PREMIUM SIDE — DESCRIPTIVE ONLY

```
HYG premium-side eligible observations    860
LQD premium-side eligible observations  1,699
PROMOTION_POWER = NONE     RESCUE_POWER = NONE
```

The sealed contract makes the premium side `DESCRIPTIVE_ONLY` and **enumerates no
premium statistic**. The accepted S2 implementation emits the eligible count and nothing
else, so the count and nothing else is reported. Inventing a premium statistic after the
seal — a premium `beta_T`, a convergence mean, a short-side P&L — would have been a
design change after outcome exposure, which is forbidden. It was not done.

---

## 11. THE SEALED CLASSIFICATION

The recorded intervals were fed to the production classification engine. No manual
interpretation preceded it.

```
§J.2 EVALUABLE      YES   pinned hashes reproduce; the decomposition is formable;
                          Var(d_t) > 0; 19 calendar years carry a discount observation
                          (sealed minimum 3)

§J.3 STEP 0  F      no    evaluable
     L_T <= 0                                  ->  the Gate-1-failed branch
§J.3 STEP 1  A-M    YES   (U_N < 0) AND (L_O > 0)          <- FIRST MATCH, wins

FINAL_CLASS       A-M   MIXED NON-HARVESTABLE CONVERGENCE
PROGRAMME_STATUS  not_promoted
QUALIFIER         MIXED_NON_HARVESTABLE_CONVERGENCE
FAILURE_TYPE      GATE_1_NOT_SUPPORTED
```

There is no "almost supported" here and no discretionary override. `beta_T`'s lower
bound is `−14.53`; the bar is `> 0`; it did not clear it.

---

## 12. WHAT THIS DOES AND DOES NOT ESTABLISH

**What the sealed taxonomy says A-M means.** The abnormal HYG discount **does** close,
and the closure is measurable in both directions the design was built to separate: a
supported positive overnight component and a supported negative NAV component. The
tradable open-to-close leg — the only leg reachable under the sealed point-in-time
timing — is not supported. That is what "mixed, non-harvestable" names.

**Binding, from the sealed §K.** This result does NOT prove authorised-participant
causality, dealer-balance-sheet causality, that NAV is inefficient generally, that credit
is mispriced generally, crisis diversification, or any TSMOM improvement. A stale-NAV
component does NOT prove ETFs are inefficient or that issuer NAV is wrong in any legal
or accounting sense. An overnight-convergence component is NOT a harvestable edge under
this signal timing.

**Provenance limitation.** The HYG/LQD price leg is **reused / burned context** (KB-1,
6 of 6, `must_not_be_retested_on_same_sample`). The NAV leg is a new external source
with a `RECONSTRUCTED_HISTORICAL_SERIES_WITH_NON-VINTAGE_LIMITATION`. Combined
provenance is **MIXED / DEPENDENT**: a new NAV leg does not launder a reused price
sample. `EVIDENCE_CEILING = supported`, never `confirmed`, never independently
confirmed — and that ceiling binds a negative reading exactly as it would have bound a
positive one.

**Seat status.** The seat that produced this result designed the contract and built the
implementation, and is now outcome-exposed (`ops/REVIEWER_EXPOSURE_LOG.md` S36). It may
not certify, verify or adjudicate what it generated.

---

## 13. TRIAL ACCOUNTING AND EXPOSURE

```
F-BENB   BENB_PRIMARY_TRIAL_SPENT   NO -> YES        m = 1, no multiplicity correction
         BENB-GATE2                 computed, NOT consulted; spends no separate trial
         BENB-DIAG / SECONDARY / DESC   never attempts; never enter N_trials
N_trials on the ETF panel           NOT ASSERTED (unchanged)
D-ETF-COUNT                         UNKNOWN_PENDING_AARON_DECISION (untouched)
```

`ops/EXPOSURE_LEDGER.md` row **54** records `REVEALED_TARGET_METRIC` / `TARGET_METRIC`
for this run. `research/extensions/SAMPLE_REUSE.md` gains one **appended** KB-1 addendum
field recording that the reuse actually occurred; the seal-time
`Exposure at this append = NONE` row is left exactly as written, because it was a true
statement about the S1 seal. No trial-count number was invented: KB-1 has no frozen
trial-count convention and the sealed design uses no DSR.

---

## 14. CONSUMPTION

```
LIFECYCLE  BENB-AUTH-0001  CONSUMED  2026-09-16T06:41:00Z
  run_id BENB-RUN-20260915-01   run_count 1   reveal_count 1   execution_count 1
```

After consumption the guard reports `active_execution_authorizations = 0` and
`real_run_authorized = false`, and `RealCellSource` cannot be constructed. The grant is
not reusable, and no further BENB historical execution is authorised by anything in
committed state.

---

## 15. FORBIDDEN POST-RESULT ACTIONS — NONE TAKEN

```
second run performed                 NO
alternate seed used                  NO
costs changed                        NO      5 bps / 10 bps, unchanged
M1 or M2 changed                     NO      STRICT > 0 and STRICT > +0.30, unchanged
horizon changed                      NO      open(t+1) -> close(t+1), unchanged
HYG swapped for LQD                  NO
adjusted prices used                 NO      raw unadjusted close throughout
expanding median altered             NO
threshold or extreme-discount
  selection added                    NO
ex-date rule changed                 NO
multi-day holding added              NO
overnight exposure taken             NO
severity-scaled positions            NO
premium shorts added                 NO
years removed                        NO
macro filters added                  NO
anything optimised                   NO
design changed after exposure        NO      seal and S2 implementation byte-unchanged
```

No rescue run. No second look. The lineage stops here and waits for the Owner.

---

## 16. ARTIFACTS

| artifact | sha256 |
|---|---|
| `research/extensions/benb/s3/BENB_S3_RESULT.json` | `ebc3baeed51d40916aef3c68a3e50f83ca13ad21077344dcacc5516830106157` |
| `research/extensions/benb/s3/BENB_S3_FEATURE_REALISATION.json` | `7f4c93aa58527240295eb73f0960b871d4b58a313e93e6cc497c89062fa0c469` |

`research/extensions/benb/benb_s3_validate.py` re-validates the recorded result against
the sealed contract, the committed grant and the consumed lifecycle record: schema, seal
integrity, input hashes, grant binding, seed, `B = 10,000`, one execution, consumption,
re-classification of the recorded intervals, gate-flag consistency, the structural
pre-run reproduction, evaluability, and the firewalls. It runs **entirely on the
artifact and committed state** and never re-opens `data/benb/`, because the grant
authorised one historical execution and it has been spent.

---

## 16a. POST-RUN VALIDATION RESULTS

*Appended after the post-run commit, because two of these results can only be produced
once the consumption record is in committed state. No design artifact, result value or
governance decision is changed by this section.*

```
benb_s3_validate.py                          47/47 PASS
benb_tests.py            (S2 behavioural)    65 passed
ta_tests.py              (prior lineage)     48 passed
python -m pytest         (repository)        98 passed, 3 failed
benb_prereg_validate.py  (S1 pre-seal)       71/72   <- see below
```

**The three repository failures are PRE_EXISTING**, all in
`tests/test_xsmom_universes.py` (`pandas OutOfBoundsDatetime: 2333-04-30`). They are
unrelated to BENB and were **not** repaired here: fixing an unrelated failure inside a
governed-run commit is scope creep, and repairing anything after outcome exposure is
exactly what the S3 brief forbids. NEW failures: **0**.

**`benb_prereg_validate.py` now returns 71/72, and that is correct.** The one failing
check is:

```
E/no execution authorization exists for this lineage
    "CTA-EDGE-02-BENB" not in ops/EXECUTION_AUTHORIZATIONS.md
```

That is an **S1-seal-time state assertion**, not a statement about the contract. It was
true at the seal and is deliberately false now: `BENB-AUTH-0001` exists, was exercised
once, and is recorded CONSUMED. All 71 checks that test the **content** of the sealed
contract still pass, and the two seal hashes reproduce.

**The validator was not modified.** It is a sealed-lineage artifact (sha256
`dfaff01a38011ec898199e2e00d6fa8324ba4bcd52bd87d10d043eb9617db984`), byte-unchanged
since the seal, and editing it after outcome exposure — even to "fix" a check that has
done its job — would be precisely the post-result design change the brief prohibits. The
expected reading is recorded here instead.

**`benb_tests.py` gd01 and gd02 pass again**, and the round trip is itself evidence:
they assert "no live BENB EXECUTION grant, and `RealCellSource` refuses". That was true
at S2, went **false** in the window between the authorization commit and consumption —
which is the only window in which a historical run was possible — and is true again now.

**Design integrity after exposure**, by `git diff d1ccefc8..HEAD`: every sealed document
and every accepted S2 module is **UNCHANGED** — `BENB_S0_FRAME.md`,
`BENB_S0_REPAIR_RECORD.md`, `BENB_PREREGISTRATION.md`, `BENB_SEAL_MANIFEST.md`,
`benb_prereg_validate.py`, and all twelve `benb_*.py` implementation modules. The only
changes are the five governance ledgers and the new S3 artifacts.

---

## 17. NEXT

S3 ends here. This record does not start S4, does not ask a reviewer to interpret the
result, does not open another candidate, and does not run portfolio integration. The
S4 evidence-to-claim judgment, if the controller wants one, belongs to a seat that is
neither this one nor a `material_design_contributor`.

*CTA-EDGE-02-BENB: one governed run, one class, no rescue.*
