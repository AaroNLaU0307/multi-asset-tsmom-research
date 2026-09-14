# TSMOM-VRP-01 — STAGE-A RUN RECORD (VRP-STAGE-A-RUN-0001)

```
LINEAGE                 = TSMOM-VRP-01
CONTRACT_ID             = TSMOM-VRP-01-PREREG-01
RUN_ID                  = VRP-STAGE-A-RUN-0001
RUN_COUNT               = 1
AUTHORITY               = CHATGPT_FINAL_S2_ACCEPTANCE_ON_BEHALF_OF_OWNER_WORKFLOW,
                          relayed by Aaron in session
EXECUTION_GRANT         = VRP-AUTH-0001  (single-use, committed before the run)
REVEAL_GRANT            = VRP-AUTH-0002  (single-use, committed only after the
                          post-compute gate passed)
S3_BRANCH               = vrp/s3-stage-a
S3_BASE_COMMIT          = f196cfdc3a866f64ca8d12d5b91bd9433b327d06
CODE_COMMIT AT RUN      = 2ef4700497dd...  (recorded in the run manifest, verified == HEAD)
RESULT_STATE            = GENERATED_NOT_SEEN → REVEALED_ONCE
REVEAL_COUNT            = 1
STAGE_B_EXECUTED        = NO
STAGE_B_AUTHORIZED      = NO
```

---

## 1. Integrity metadata (recorded before the reveal)

### 1.1 Lineage pins, all re-verified at the pre-run gate

| pin | value |
|---|---|
| canonical base (`main`) | `d232d3361b23a9f64182c2ec8881284f0fc3b36e` |
| authoritative S1 seal | `16d84545ba1385a482dbac7e776b31275f6fa5f7` |
| S2 build | `72499019ce9ef97f16d1ddf3b3982697a4e6c4cc` |
| S2 governance closure | `f196cfdc3a866f64ca8d12d5b91bd9433b327d06` |
| `VRP_PREREGISTRATION.md` | `dd5822440bedbe58f49940651bddf656f4dbb593295b59c4eff2b45b89cf53e6` |
| `VRP_IMPLEMENTATION_ACCEPTANCE_CONTRACT.md` | `4fad50df6ef0c031cdb67e8100034718f49382ce0dd4e6df8e93f29afecb7dbb` |
| `VRP_EXPOSURE_DISCLOSURE.md` | `afae108d6e894c3822c783d45d77b85e09838578e5e7bf8040ad6dac6a3788c1` |
| `vrp_prereg_validate.py` | `4684ecb2c9a633a9d17413a067aa0987a110718518954579a87ffd6122667876` |
| `VRP_S1_MECHANICAL_ERRATUM_01.md` | `b8a089ac2f1d3f26d0493684bb3512cfe564b4f82d49690c3b7daa77b28e8f1a` |
| protected result | `baa0a07d647b4d1be082a569022dbcc09d1eb23e5f64b76374449a8139fce1bc` |

Raw inputs: 274 Cboe official per-contract files, each SHA-256 pinned in
`VRP_DATA_MANIFEST.md` and re-verified at the gate; acquisition manifest hash and
`DGS3MO.csv` hash recorded in `VRP_STAGE_A_RUN_MANIFEST.json`.

### 1.2 Sample

```
HISTORICAL_STAGE_A_WINDOW = 2006-09 .. 2026-08
N_MONTHS                  = 240      (contiguous; no gap month; 2026-09 excluded)
CHAIN_DAYS                = 5032
STAGE_A_CUTOFF_DATE       = 2026-09-01   (sealed §K.1)
FIRST MONTH               = 2006-09      (fixed MECHANICALLY by §F.6, re-derived at the gate)
CARRY-FORWARD DAYS        = 0 in the window
K                         = $200,000 = s · W0 (§H.1). r_A is exactly invariant to K:
                            VM and every cost component are linear in K.
```

### 1.3 Convention in force

Per `VRP_S1_MECHANICAL_ERRATUM_01.md`, the **SIGNED** convention:
`q_i < 0` for the short, `VM_d = Σ_i q_i · M_i · ΔS_i`. A rise in held VX settlements
produces negative variation margin. Re-asserted from the source bytes at the gate.

### 1.4 Inference

```
family      = stationary bootstrap, geometric blocks, circular wrap
block       = expected 12 months (p = 1/12)
replicates  = 10,000     valid = 10,000     invalid = 0     floor = 9,500 (met)
interval    = 95 % percentile, linear interpolation
seed        = master 7; SeedSequence(7).spawn(4), stream[0] = stage_a_historical
```

### 1.5 Gates

```
S3_PRE_RUN_GATES     = PASS  (40 / 40)   research/extensions/vrp/s3/VRP_S3_PRERUN_GATES.json
S3_POST_COMPUTE_GATE = PASS  (19 / 19)   research/extensions/vrp/s3/VRP_S3_POSTCOMPUTE_GATES.json
```

---

## 2. THE REVEALED STAGE-A EVIDENCE PACKAGE

*Appended after the single authorised reveal under `VRP-AUTH-0002`. Machine-readable copy:
`VRP_STAGE_A_REVEALED_PACKAGE.json`.*

### 2.1 Primary

```
HISTORICAL_STAGE_A_WINDOW              = 2006-09 .. 2026-08
N_MONTHS                               = 240
ANNUALISED_MEAN_NET_EXCESS_RETURN_ON_K = +0.073224      (+7.3224 %)
CI_95_LOW                              = +0.003906      (+0.3906 %)
CI_95_HIGH                             = +0.136081      (+13.6081 %)
ECONOMIC_USEFULNESS_MARGIN  (+E)       = +0.075         (+7.5 %)
ADVERSE_FLOOR               (−F)       = −0.075         (−7.5 %)

STAGE_A_STATE                          = UNRESOLVED
FAILURE_CLASS                          = 3  INSUFFICIENT_EVIDENCE / LOW_POWER
FAILURE_SUBTAG                         = NONE
RESEARCH_STATUS                        = unresolved
STAGE_A_TRIAL_SPENT                    = YES
```

The estimand is the **annualised arithmetic mean** of the monthly Stage-A excess return,
`A = 12 · mean(r_A,t)` (§C.1). It is **not** a CAGR and is never compounded. No Sharpe is
reported; no second metric with claim power exists.

**Why UNRESOLVED, mechanically.** §C.3 classifies on the **interval endpoints**, never on
the point estimate. `L = +0.003906 ≤ +0.075 ≤ U = +0.136081`, so `L ≤ +E ≤ U` holds and the
state is **UNRESOLVED, Class 3**. The point estimate lands just under the margin; that is
not a state and does not make this a near miss in either direction. The 95 % interval
spans roughly +0.4 % to +13.6 % annualised on committed capital, so the sample is
consistent both with compensation well above the required margin and with compensation far
below it. **The evidence is insufficient to decide**, which is exactly what Class 3 names.

**What this does not say.** It does not say the sleeve is useful. It does not say it is
useless. It establishes neither that the +7.5 % margin is cleared nor that it is excluded.
Nothing here speaks to Stage-B compatibility, to prospective performance, to deployment,
or to any mechanism.

### 2.2 Predeclared descriptives — `PROMOTION_POWER = NONE`

None of these can change, rescue, upgrade or reinterpret the classification above (§R).

| # | descriptive | value |
|---|---|---|
| R1 | mean monthly gross carry, comparable points per unit sensitivity | `+0.8186` |
| R2 | worst 1-day sleeve loss, fraction of `K` | `−0.156554` |
| R3 | worst 5-day sleeve loss, fraction of `K` | `−0.325413` |
| R4 | worst monthly sleeve loss, fraction of `K` (declared budget `b = 0.30`) | `−0.321684` |
| R5 | `CAPITAL_EXHAUSTION` events | `0` |
| R12 | `c0 = 0.05` cost sensitivity, annualised mean | `+0.085248` |
| R13 | FM-1 collateral total return, annualised mean | `+0.088604` (239 / 240 months defined) |
| R14 | point estimate / L / U / invalid replicates | `+0.073224` / `+0.003906` / `+0.136081` / `0` |

**R4 against the declared budget.** The worst single month lost `0.3217 · K`, slightly more
than the declared stress budget `b · K = 0.30 · K`. §D.1 already states that `b · K` is **a
budget, not a bound**, and that `J` is not a maximum possible loss, so this is the declared
quantity behaving as declared rather than a finding against it. No month exhausted capital
(R5 = 0), and Stage A models no forced liquidation.

**R13 undefined month.** `2026-08` is undefined because its FM-1 decision date — the last
exchange business day of 2026-07 — has no `DGS3MO` print within the sealed 7-calendar-day
lookback (the pinned series ends 2026-06-23). §E.3 requires exactly this: report it as
undefined, no fallback series, primary unaffected.

**Stage-B descriptives R6–R11 are not reported.** Stage B has not run.

---

## 3. Stop rule now in force

§O, sealed and exhaustive:

> `Stage A Class 3 → stop historical study → Stage B never runs → only the sealed
> VRP-A-PROSPECTIVE continuation (§P)`

So the historical study **stops here**. Stage B is not merely unauthorised in this session —
under the sealed stop rule it **never runs** on this historical result. The only sealed
continuation is **VRP-A-PROSPECTIVE** (§P), which is an Owner decision and was not started.

§O also forbids, on the strength of any result: changing `J`, `b`, `theta`, `E`, `F`, `s`,
`beta`, `delta_tail`, the maturity, the roll, the cost convention, the sample endpoints or
the tail rule, and forbids adding any filter. Each would be a **new lineage** with its own
trial accounting. Nothing in this record proposes one.

---

## 4. Trial accounting

```
SAMPLE                     = dataset.cboe.vix-futures-monthly-chain
N_trials BEFORE            = 0
N_trials AFTER             = 1
VIX_CHAIN_TRIAL_INCREMENT  = +1
STAGE_A_TRIAL_SPENT        = YES   (spent on construction, whatever the state)
STAGE_B_TRIAL_SPENT        = NO
```

Bootstrap replicates, descriptives, synthetic tests and mechanical validators increment
nothing.

---

## 5. Firewalls at the close of the run

```
REAL_STAGE_B_COMPUTED             = NO
C_A_PROSPECTIVE_OUTCOME_ACCESSED  = NO
C_A_PROTECTED_STORE_ACCESSED      = NO
CANONICAL_FORWARD_RETURN_COMPUTED = NO
OWNER_VALUES_CHANGED              = NO
SCIENTIFIC_DESIGN_CHANGED         = NO
RERUN_PERFORMED                   = NO
```

Stage B is refused **structurally**, not merely by instruction: `require_run_authorization`
is stage-scoped and `VRP-AUTH-0001` carries `stage_b_authorized = false`.

*Any receiver recomputes every hash cited here before use.*
