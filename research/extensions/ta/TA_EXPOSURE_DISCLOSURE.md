# CTA-EDGE-01-TA — DESIGN-CONTRIBUTOR AND OUTCOME-EXPOSURE DISCLOSURE

```
LINEAGE = CTA-EDGE-01-TA
STATUS  = BINDING. Recorded at the S1 seal, 2026-09-15.
SEAT AXIS RECORD = ops/REVIEWER_EXPOSURE_LOG.md rows S31, S32, S33
```

---

## §1 Outcome exposure for this lineage, at seal

```
CANDIDATE_OUTCOME_ACCESSED = NO
ETF_EVENT_RETURN_COMPUTED  = NO
AC_COMPUTED                = NO
SHARPE_COMPUTED            = NO
BOOTSTRAP_RUN              = NO
BACKTEST_RUN               = NO
BUILD_STARTED              = NO
C_A_ACCESSED               = NO
CANONICAL_TSMOM_MODIFIED   = NO
```

No ETF event return, `AC`, leg return, auction-day bar return, mean, interval, Sharpe,
bootstrap replicate, P&L or portfolio quantity exists for this lineage. The single
contact with the frozen ETF panel is `ta_auction_fetch.trading_calendar()`, which
reads the `Date` column and a **non-null presence mask** for TLT, IEF, SHY and SPY and
retains no numeric value. A presence mask is data availability, not a price and not a
return.

**Panel-level context carried in, and not created here.** The ETF panel is `KB-1`,
burned 6 of 6, and its historical target metrics were revealed to this programme long
before this lineage existed. Every seat below is therefore `REVEALED_TARGET_METRIC`
**on the panel** as inherited programme context, and `NO_OUTCOME` **on this lineage's
auction-conditioned statistic**, which has never been computed by anyone.

---

## §2 Material design contributors — BARRED FROM BLIND CERTIFICATION

### Claude Fable 5.1 — `material_design_contributor`

```
FABLE_DESIGN_EXPOSED = YES
```

Contribution: the CTA edge-discovery round-1 mechanism and feature map
(`2026-09-15-cta-edge-discovery-r1-mechanism-feature-map-fable-01.md`, family **F1**,
with **F2** as the proposed conditional dealer cell) — the Treasury-auction candidate
itself, the IEF/TLT instrument mapping, the reduced-form event-window framing, and the
dealer-inventory secondary proposal.

**Consequence.** Fable may never later be represented as a fresh independent certifier
of this design, this implementation, or any result under it.

### GPT-6 Astra — `material_design_contributor`

```
ASTRA_DESIGN_EXPOSED = YES
```

Contribution: the independent identification challenge to the causal reading —
duration-weighted announced supply, point-in-time dealer inventories, when-issued
pricing, cash Treasury and futures information, the separation of auction effect from
duration repricing and macro news, and the warning that genuinely constrained
intermediation episodes are far fewer than raw auction observations. That challenge is
why the primary claim is `REDUCED_FORM`, why the dealer cell is `PARKED`, and why
`CAUSAL_MECHANISM_EFFECTIVE_N` is recorded separately from the event count.

**Consequence.** Astra may never later be represented as a fresh independent certifier
of this design, this implementation, or any result under it.

**Recorded provenance limitation.** Astra's round-1 output is **not on disk in this
workspace**. It reached the S0 session only through the programme controller's task
brief. The substance was accepted and acted on; this disclosure cannot cite Astra
bytes, and that gap is recorded rather than papered over.

---

## §3 The producing seat

### Claude Opus 5 — S0 frame and S1 design/seal — `producer`

The same Main-Agent seat authored `TA_S0_FRAME.md`, the sealed
`TA_PREREGISTRATION.md`, the event-calendar builder and the mechanical validator.

**Consequence.** It is the producer of this design and **must not certify it**. It may
not act as the independent verifier of this contract, of the S2 implementation it will
build, or of any result under it. Independence is carried by the session, not the
model: a fresh top-level session is required, and a subagent of this seat is never
independent of it.

---

## §4 Who can still certify

Any later blind or independent certification of this lineage needs a seat that is
**neither** the producing seat **nor** a material design contributor. Fable and Astra
are both barred by §2. Under current Owner routing that leaves a fresh top-level
session of the `OWNER_DEFAULT_INDEPENDENT_REVIEWER` only where it is genuinely fresh
with respect to **this** lineage — and Astra is not, so an alternative independent
seat must be named by Aaron if a blind certification is ever required.

This is recorded now, at seal, so that no later document can quietly present a barred
seat as a fresh certifier.
