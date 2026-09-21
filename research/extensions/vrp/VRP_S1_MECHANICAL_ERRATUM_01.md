# TSMOM-VRP-01 — S1 MECHANICAL ERRATUM 01

## Variation-margin sign notation

```
ERRATUM_ID                 = TSMOM-VRP-01-ERRATUM-01
LINEAGE                    = TSMOM-VRP-01
CONTRACT_ID                = TSMOM-VRP-01-PREREG-01
CLASS                      = MECHANICAL NOTATION REPAIR
RAISED_AT                  = S2 BUILD (implementation Main Agent, Claude Opus / Claude Code)
RAISED_BY                  = a synthetic economics test, not by any real-data result
AUTHORITATIVE_S1_SEAL      = 16d84545ba1385a482dbac7e776b31275f6fa5f7
SEALED_TEXT_MODIFIED       = NO  — VRP_PREREGISTRATION.md is byte-identical to the seal
                                  (SHA256 dd5822440bedbe58f49940651bddf656f4dbb593295b59c4eff2b45b89cf53e6)
STANDING                   = an ADDITIONAL authoritative implementation-control artifact,
                             read alongside the sealed contract for S3
```

This erratum **does not amend the sealed contract**. The sealed bytes are preserved
unmodified and remain the scientific authority. What is frozen here is the
**implementation notation** the sealed text leaves ambiguous, and nothing else.

---

## 1. The inconsistency

The sealed preregistration contains two statements which, taken together and read
literally, invert the intended economics of the research object.

**A — `q_i` is defined as a SIGNED quantity, negative for a short.** §D.2:

> `Σ_i ( q_i · M_i ) = b · K / J = 0.01 · K` dollars per VIX point *(q_i signed negative
> for the short; the sensitivity is stated as the absolute dollar loss per +1 point)*

and §F.3 constructs the quantities with an explicit leading minus:

> `q_front = − w_front · S / M`, `q_second = − w_second · S / M`

**B — the variation margin is written with an ADDITIONAL leading minus.** §E.1:

> `VM_d = − Σ_i q_i,(d−1) · M_i · ( S_i,d − S_i,d−1 )`

**The literal composition of A and B.** With `q_i < 0` and a rise in settlements
(`ΔS_i > 0`), `− q_i · M_i · ΔS_i > 0`: the position would be credited variation margin
when VIX futures rise. That is a **long**. The sealed research object is a **short**.

The two minus signs are the whole of the defect. There is no third reading.

---

## 2. Why the intended economics is unambiguous

The sealed text settles its own meaning in two independent places, neither of which
requires any outcome, any data, or any judgement:

**The research object.** §A defines Object D as

> a **standalone, unconditional, constant-maturity SHORT position in listed monthly VIX
> futures**

**The stress identity.** §D.1–§D.2 declare a `+J` parallel move in every held contract and
fix its consequence as a **loss**:

> `Loss under the declared stress: Loss_J = J · Σ_i q_i M_i = 0.30 · K`

A `+30`-point move producing `Loss_J = +0.30 · K` — a loss of thirty per cent of committed
capital — is only consistent with a short. Under the literal reading of §E.1 the same move
would produce a **gain** of `0.30 · K`, contradicting §D.2 in the same contract.

The §D.2 parenthetical resolves which of the two statements carries the loose notation: it
says the sensitivity "is stated as the **absolute** dollar loss per +1 point", i.e. the
sums in §D.2 and §E.1 are written over magnitudes even though §D.2/§F.3 construct `q_i`
with a sign.

```
+J futures move  →  Loss_J = + b·K        (sealed, §D.1–§D.2)
SHORT POSITION                             (sealed, §A)
⇒ a rise in held VIX futures settlements MUST produce negative variation margin.
```

---

## 3. The frozen notation

Two conventions are equivalent and both reproduce the sealed economics exactly. The
implementation uses the **SIGNED** convention.

**SIGNED convention — USED BY THIS IMPLEMENTATION**

```
q_i < 0                       for a short
VM_d = Σ_i q_i · M_i · ΔS_i
```

**MAGNITUDE convention — equivalent, not used**

```
q_abs,i > 0                   denotes short magnitude
VM_d = − Σ_i q_abs,i · M_i · ΔS_i
```

Since `q_i = − q_abs,i`, the two expressions are the same number on every day, for every
holdings vector, under every price path. Choosing between them changes no estimand, no
return, no cost and no interval — it changes only which of the two places the minus sign
is written.

**Implementation location.** `research/extensions/vrp/vrp_stage_a.py` carries the
convention in its module docstring and computes

```python
vm += q * STANDARD_MULTIPLIER * (today_prices[key] - prices[key])
```

`research/extensions/vrp/vrp_stage_b.py` uses the identical form for the sleeve leg.
`vrp_sizing.gross_point_sensitivity` and `vrp_sizing.stress_loss` work in magnitudes
(`Σ|q_i · M_i|`), which is why the stress identity `Loss_J = 0.30·K` was already correct
and could serve as the fixed point the sign was repaired against.

---

## 4. Declarations

```
SCIENTIFIC_DESIGN_CHANGED   = NO
OWNER_VALUE_CHANGED         = NO
ESTIMAND_CHANGED            = NO
EXPOSURE_CHANGED            = NO
COST_CHANGED                = NO
WINDOW_CHANGED              = NO
OUTCOME_USED_TO_RESOLVE     = NO
```

No sealed constant moved: `theta`, `b`, `E`, `F`, `J`, `m_J`, `lambda`, `c0`, the
commission and fee constants, `beta`, `s`, `W0`, `delta_tail`, `k`, `N_A`, `N_B`,
`n_T_min_prosp`, the cutoff, the Stage-B boundary, the block length, the replicate count,
the floor and the seed are all unchanged and are re-asserted against the sealed text on
every acceptance run (item 20).

`OUTCOME_USED_TO_RESOLVE = NO` is the load-bearing declaration. The sign was **not**
determined by looking at which orientation produced a more plausible historical result —
no historical Stage-A or Stage-B quantity has ever been computed in this lineage. It was
determined from two structural statements in the sealed contract (§A "short position",
§D.2 `Loss_J = +b·K`) and demonstrated on a **synthetic** monotone price path.

---

## 5. The proving test

```
research/extensions/vrp/vrp_tests.py::test_i12_short_position_loses_when_the_curve_rises
```

It builds a synthetic settlement path rising monotonically across one roll period, runs
the Stage-A engine on it with `data_kind = SYNTHETIC`, and asserts

```python
assert res.months[0].variation_margin < 0
```

A synthetic falling path is the mirror case. On the frozen sensitivity `0.01·K` with
`K = $1,000,000`, a +5-point rise produces variation margin of exactly `−$50,000`
(`5 × $10,000`), which is the §D.2 sensitivity acting in the loss direction.

Two further tests hold the surrounding arithmetic fixed:
`test_i12_stage_a_matches_a_closed_form_oracle` (the closed-form §E oracle, written with
literal constants) and `test_i09_parallel_thirty_point_move_costs_exactly_0_30_K` (the
§D.1 stress identity at `0.30·K` for every capital level and every weight split).

**How the defect was actually caught, recorded because it matters for how much the oracle
is worth.** The first implementation followed §E.1 literally and inverted the sign. The
closed-form oracle, written in the same session from the same sealed text, reproduced the
same misreading and **agreed with the engine**. An oracle written by the producer is
therefore not independent evidence of correctness against a misreading of the
specification; it only catches arithmetic slips. What caught this was the separate
economics assertion above, which encodes the *object* rather than the *formula*.

---

## 6. Standing for S3

This erratum is an additional authoritative implementation-control artifact for
TSMOM-VRP-01. It is read alongside, never instead of, the sealed
`VRP_PREREGISTRATION.md`. It authorises nothing: not a run, not a reveal, not a scope
change. `S3_AUTHORIZED = NO`, `REAL_RUN_AUTHORIZED = NO`.

If any later session finds the implementation computing variation margin in the opposite
direction — a short credited when settlements rise — that is a defect against this erratum
and against §A and §D.2, and it is a VRP-VALIDITY failure, not a matter of taste.

*The SHA256 of this file is recorded in the S2 governance-closure commit message and in
the return block of the session that created it. Any receiver recomputes it before use.*
