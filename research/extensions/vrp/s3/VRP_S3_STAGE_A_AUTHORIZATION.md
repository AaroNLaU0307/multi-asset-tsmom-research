# TSMOM-VRP-01 — S3 STAGE-A EXECUTION AUTHORIZATION (control plane)

```
LINEAGE                          = TSMOM-VRP-01
CONTRACT_ID                      = TSMOM-VRP-01-PREREG-01
AUTHORITY                        = CHATGPT_FINAL_S2_ACCEPTANCE_ON_BEHALF_OF_OWNER_WORKFLOW
AUTHORITY_RELAYED_BY             = Aaron (Owner), in session, 2026-09-14
AUTHORIZED                       = ONE HISTORICAL STAGE_A RUN
AUTHORIZED_REVEALS               = ONE PREDECLARED STAGE_A EVIDENCE PACKAGE
STAGE_B_AUTHORIZED               = NO
PARAMETER_CHANGE_AUTHORIZED      = NO
SECOND_STAGE_A_RUN_AUTHORIZED    = NO
INTERIM_LOOK_AUTHORIZED          = NO
RUN_ID                           = VRP-STAGE-A-RUN-0001
```

This artifact is the **control plane**. It records the authorization and nothing else.
**No scientific outcome appears here, before or after the run.** The generated evidence
lives only in the VRP protected store and, after the single authorised reveal, in the run
record and the revealed-package artifact.

---

## 1. Lineage this authorization binds to

```
CANONICAL_BASE          = main   d232d3361b23a9f64182c2ec8881284f0fc3b36e
AUTHORITATIVE_S1_SEAL   = 16d84545ba1385a482dbac7e776b31275f6fa5f7
S2_BUILD                = 72499019ce9ef97f16d1ddf3b3982697a4e6c4cc
S2_GOVERNANCE_CLOSURE   = f196cfdc3a866f64ca8d12d5b91bd9433b327d06   (this branch's base)
S3_BRANCH               = vrp/s3-stage-a
NON_AUTHORITATIVE_SEAL  = d19264af85f45c17f655493e02f71a653bfbdd86   — never authority
```

Sealed artifacts, each re-verified before the run:

| artifact | SHA256 |
|---|---|
| `VRP_PREREGISTRATION.md` | `dd5822440bedbe58f49940651bddf656f4dbb593295b59c4eff2b45b89cf53e6` |
| `VRP_IMPLEMENTATION_ACCEPTANCE_CONTRACT.md` | `4fad50df6ef0c031cdb67e8100034718f49382ce0dd4e6df8e93f29afecb7dbb` |
| `VRP_EXPOSURE_DISCLOSURE.md` | `afae108d6e894c3822c783d45d77b85e09838578e5e7bf8040ad6dac6a3788c1` |
| `vrp_prereg_validate.py` | `4684ecb2c9a633a9d17413a067aa0987a110718518954579a87ffd6122667876` |
| `VRP_S1_MECHANICAL_ERRATUM_01.md` | `b8a089ac2f1d3f26d0493684bb3512cfe564b4f82d49690c3b7daa77b28e8f1a` |

## 2. The variation-margin convention in force

Per `VRP_S1_MECHANICAL_ERRATUM_01.md`, the **SIGNED** convention:

```
q_i < 0                       for the short
VM_d = Σ_i q_i · M_i · ΔS_i
```

A rise in held VX settlements produces **negative** variation margin for the short. The
engine implements this and the pre-run gate re-asserts it from the source bytes.

## 3. What exactly is authorized

**One** governed historical Stage-A run over the sealed window, and **one** reveal of the
predeclared Stage-A evidence package.

```
STAGE_A_CUTOFF_DATE     = 2026-09-01          (sealed §K.1; fixed calendar date)
STAGE_A_LAST_MONTH      = 2026-08
STAGE_A_FIRST_MONTH     = 2006-09             (fixed MECHANICALLY by §F.6 at S2A;
                                               re-derived by the pre-run gate, never assumed)
EXPECTED_MONTH_COUNT    = 240
GAP_MONTHS              = excluded; 2026-09 is NOT in the window
```

The object is the sealed one and nothing else: unconditional, one-month constant-maturity,
short, first and second eligible **monthly** VX contracts, calendar-only deterministic
roll, official Cboe settlements. No weeklies, no timing, no contango or backwardation
filter, no volatility or trend filter, no parameter optimisation, no alternative maturity,
no options, no variance-premium proxy. `J = 30`, `b = 0.30`, sensitivity `0.01 · K` per
comparable point, constant within each month, no market-state resizing.

## 4. What is NOT authorized

- **Stage B.** Forbidden in this session **even if Stage A is SUPPORTED**. No book return,
  no `D`, no tail statistic, no core-VRP combination, no tail bootstrap, no crisis
  compatibility, no book exhaustion on real history.
- A **second** Stage-A run, a re-run with altered settings, or any recomputation after the
  first successful governed computation.
- Any **interim look** at the result before the post-compute integrity gate passes.
- Any **parameter change**: `J`, `b`, `theta`, `E`, `F`, `s`, `beta`, `delta_tail`, the
  maturity, the roll, the cost convention, the sample endpoints, the tail rule, or any
  added filter.
- Starting a **prospective clock**.
- Any access to **C-A** protected state.

## 5. Gate ordering this run follows

```
PRE-RUN GATES A–K  →  GENERATE (one run)  →  PROTECT (GENERATED_NOT_SEEN)
                   →  VERIFY (post-compute integrity)  →  SINGLE REVEAL
```

A failed **pre-run** gate means the run does not happen and **no Stage-A trial is spent**,
because no governed strategy-return series was constructed. A failed **post-compute** gate
means `S3_STATUS = HOLD_POST_COMPUTE`: the protected evidence is preserved, nothing is
revealed, and a re-run would need explicit governance review.

## 6. Trial accounting

The moment the governed real Stage-A strategy-return series is successfully constructed:

```
STAGE_A_TRIAL_SPENT              = YES
VIX_CHAIN_TRIAL_INCREMENT        = +1        (dataset.cboe.vix-futures-monthly-chain: 0 → 1)
STAGE_B_TRIAL_SPENT              = NO
```

This holds **regardless of the final Stage-A state**. Bootstrap replicates, descriptives,
synthetic tests and mechanical validators increment nothing.

## 7. Machine-readable grants

The sealed contract §S requires the grant to be read **only from committed state**, under
the existing `ops/EXECUTION_AUTHORIZATIONS.md` discipline. Two single-use grants are
recorded there for this lineage:

| id | kind | scope | committed |
|---|---|---|---|
| `VRP-AUTH-0001` | `EXECUTION` | one outcome-bearing Stage-A run, `run_id = VRP-STAGE-A-RUN-0001` | **before** the run |
| `VRP-AUTH-0002` | `REVEAL` | one reveal of the predeclared Stage-A evidence package | **after** the post-compute gate passes, **before** the reveal |

`vrp_reveal.require_run_authorization` refuses a real run unless `VRP-AUTH-0001` is
committed and the acceptance log shows every item PASS; `ProtectedResult.reveal` refuses
unless `VRP-AUTH-0002` is committed. Neither grant is reusable.

*This artifact is committed BEFORE the governed computation. It contains no result.*
