# OWNER DECISION RECORD — PHASE B (canonical multi-asset TSMOM prospective confirmation)

```
RECORD_TYPE        = OWNER_DECISION_RECORD
PROGRAMME          = Phase B — canonical multi-asset TSMOM prospective confirmation
STUDIES            = C-A (primary prospective confirmation) · C-D (implementation-verification precondition)
DATE_OF_DECISIONS  = 2026-09-13 (OD-1 … OD-4) · 2026-09-14 (OD-5 … OD-7)
                     2026-09-13T17:42:06Z (OD-8 — SEAL C-A)
OWNER              = Aaron  (the only authority for every decision recorded here)
RECORD_STATUS      = CONFIRMED — on 2026-09-14 Aaron confirmed that the §2–§6
                     transcription of OD-1 … OD-4 is faithful, and adopted OD-5 … OD-7
RECORDED_BY        = Claude Opus 5 (Main Agent / research engineer), S1 entry session
                     2026-09-13; extended in the S1 bounded-repair session 2026-09-14
WORKFLOW_AUTHORITY = ../../QUANT_WORKFLOW_VNEXT.md  (vNext, cutover 2026-09-12)
```

**What this file is.** The durable record of the Owner decisions that closed S0 for
the Phase B programme and authorized entry to S1. It records **decisions**, not
workflow authority, and it seals nothing.

**What this file is not.** It is not a preregistration, not an authorization to
implement, not an authorization to run, and not an exposure event. It creates no
row in `EXPOSURE_LEDGER.md`, no row in `REVIEWER_EXPOSURE_LOG.md`, no record in
`EXECUTION_AUTHORIZATIONS.md`, and no trial in
`../research/extensions/TRIAL_LEDGER.md`. Writing this record revealed no outcome
and computed no performance.

---

## §1 Stage state at the time of recording

```
S0_STATUS                          = COMPLETE
S1_ENTRY_AUTHORIZED                = YES
S1_SEAL_AUTHORIZED                 = YES  (OD-8, 2026-09-13T17:42:06Z — SEAL ONLY)
S1_SEALED                          = YES
C_A_IMPLEMENTATION_AUTHORIZED      = NO
C_D_IMPLEMENTATION_AUTHORIZED      = NO
TARGET_RUN_AUTHORIZED              = NO
TARGET_OUTCOME_REVEAL_AUTHORIZED   = NO
```

**S0 sequence that produced these decisions**, in order: Fable S0 scientific frame →
Opus outcome-blind feasibility → Astra xHigh S0 challenge → Fable prospective C-A
design → bounded Fable repair → Fable Owner-decision advisory → independent Astra
OD-1 / OD-2 advisory → **Aaron's Owner decisions (recorded below)**.

---

## §2 Programme structure — fixed by the Owner

| Item | Decision |
|---|---|
| **C-A** | **The primary prospective confirmation programme.** One primary confirmatory estimand on genuinely forward months. |
| **C-D** | **REQUIRED PRECONDITION.** Independent implementation verification plus data/source reconciliation. It provides **no independent alpha evidence** and cannot move any strategy status. |
| **C-B** (historical proxy confirmation) | **PARKED.** Not reopened by this programme, this record, or any artifact created under it. |
| **Static-premium / timing-mechanism study** | **LATER, and a SEPARATE LINEAGE.** It may not alter C-A's rule, floors, terminal N or reveal schedule. |
| **Phase C factor / mechanism research** | May proceed **after** the C-A seal, under the contamination safeguards written into the C-A contract. |

**The canonical strategy is IMMUTABLE.** No parameter of it is changed by any
decision in this record: 17 ETFs in 5 sleeves (Equity SPY EEM EWJ XLE XLU · Fixed
income TLT SHY LQD HYG · Commodity USO UNG GLD DBA · FX UUP FXY · Real estate VNQ
RWX); month-end decisions; trailing 1/3/6/12-month returns; sign of each horizon
taken first, then the mean of the four signs, all four horizons required; 60-day
asset volatility; 10 % annualised asset vol target; asset position cap ±2;
equal-weight aggregation across live assets; 10 % portfolio vol target; 3× gross
cap; 2.0 bps one-way transaction cost per unit turnover. Historical canonical
metric convention: **raw net Sharpe, rf = 0**.

---

## §3 OD-1 — MATERIALITY

```
PRIMARY_PROSPECTIVE_ESTIMAND       = canonical raw net Sharpe, rf = 0, 2 bps transaction cost
POSITIVE_MATERIALITY_FLOOR   (+E)  = +0.30
ADVERSE_MATERIALITY_THRESHOLD (-F) = -0.20
BOUNDARY_RULE                      = STRICT CROSSING REQUIRED FOR EVERY INFERENTIAL DECISION
```

The two thresholds are **intentionally asymmetric**.

- **+0.30** means: economically meaningful **persistence of the canonical raw-return
  thesis**.
- **−0.20** means: economically meaningful **reversal / adverse forward performance**.

They were **not** chosen to maximise pass probability, and they are **independent of
FM-1** — that is, they were not set because a funding-adjusted complement exists.

**Boundary rule, stated so no later reading can soften it.** A lower confidence
bound of exactly `+0.30` does **not** trigger material positive persistence. An
upper confidence bound of exactly `−0.20` does **not** trigger materially adverse.
Every inferential decision requires **strict** crossing.

---

## §4 OD-2 — TERMINAL HORIZON

```
N_scored                          = 120 complete, eligible, non-invalidated monthly observations (~10 years)
TERMINAL_SCIENTIFIC_REVEALS       = ONE
POSITIVE_INTERIM_LOOK             = NONE
ADVERSE_ONE_BIT_ORACLE            = NONE
AUTOMATIC_EXTENSION_AFTER_120     = NONE
```

**A further block of new months is not an extension.** If future research wants
one it requires: a separate Owner authorization · a separate prospective seal · a
separate record · preservation of the Block 1 result. It may be called a **SECOND
PROSPECTIVE BLOCK** or a **PROSPECTIVE TEMPORAL REPLICATION**, and it must **not**
automatically be called statistically independent.

---

## §5 OD-3 — FM-1

```
FM-1_STATUS                       = INCLUDED as a COMPLEMENTARY prospective estimand
FM-1_IS_PRIMARY                   = NO
CAN_RESCUE_PRIMARY                = NO
CAN_REPLACE_PRIMARY               = NO
CAN_BECOME_FALLBACK_PRIMARY       = NO
CAN_UPGRADE_CANONICAL_CLAIM       = NO
COUNTS_AS_INDEPENDENT_REPLICATION = NO
SAMPLE                            = THE SAME prospective forward sample as the primary
```

**Required neutral language.** FM-1 is *the idealised funding-adjusted residual
under the sealed symmetric-cash convention*. It must **not** be described as a
guaranteed upper bound on realistic excess return.

**Current conceptual form** (the final rf source and timing must be mechanically
specified before seal):

```
x_t = r_net_t − net_held_t × rf_t
```

> **Completed by OD-6 (§6B), adopted 2026-09-14.** The rf source, observation rule,
> freshness window, monthly conversion, locking and no-fallback rule are fixed
> there. OD-3 as recorded above is unchanged; OD-6 supplies the mechanical
> specification it called for. The FM-1 **decision scale** is fixed separately by
> OD-7 (§6C) — FM-1 carries **no** `+0.30 / −0.20` floors.

Its accounting limitations must be explicit wherever it is reported.

---

## §6 OD-4 — CANONICAL ATTRITION POLICY

```
CANONICAL_UNIVERSE_POLICY               = ALL_17_REQUIRED
MINIMUM_N_FALLBACK                      = NONE
DYNAMIC_UNIVERSE                        = NO
DISCRETIONARY_POST-OUTCOME_SUBSTITUTION = NO
```

**Identity-preserving administrative events** may continue the same record if they
satisfy the sealed identity rule. Potentially identity-preserving: ticker rename ·
identifier change · split / reverse split · purely administrative continuity.

**Economic identity is judged from external fund / benchmark documentation, never
from strategy outcomes.**

**MATERIAL_OBJECT_CHANGE** is declared when an ETF or its underlying benchmark
changes materially in: economic mandate · selection rules · weighting rules ·
intended exposure · investment construction.

- A material canonical-object disappearance or change **FREEZES / TERMINATES** the
  canonical 17-object record at that boundary.
- **Do not reveal performance merely because the record terminates.**
- **No discretionary replacement.**
- A successor record may begin **only** under a sealed identity-preserving successor
  rule.
- **AMBIGUITY → TERMINATE THE CANONICAL RECORD.**
- A materially different successor is **A NEW, SEPARATELY LABELLED OBJECT**.

---

## §6A OD-5 — PRIMARY AND DIRECTIONAL SCIENTIFIC INFERENCE (adopted 2026-09-14)

```
INFERENCE = ONE central 95 % stationary-bootstrap percentile interval, per estimand.
```

On the existing accepted bootstrap architecture, unchanged: stationary bootstrap ·
expected block length 12 months · 10,000 replicates · percentile interval · linear
interpolation · the existing deterministic `SeedSequence` protocol · the existing
invalid-replicate policy and valid-replicate floor · joint monthly-vector resampling
where statistics share the same path.

**There is ONE interval.**

- Do **not** compute an alternative 90 % interval.
- Do **not** compute a separate one-sided interval.
- Do **not** select between intervals after outcomes.

**For the primary**, all inequalities **STRICT**:

```
P_MAT    :  lower bound > +0.30
P_POS    :  lower bound >  0
P_RULED  :  upper bound < +0.30
P_ADV    :  upper bound < -0.20
```

The central 95 % interval implies a **2.5 % directional tail at each endpoint**.

**This decision intentionally accepts the resulting high probability of an
`UNRESOLVED` terminal result.** `+0.30`, `−0.20` and `N = 120` are **not** reopened
by it. Blocker `SB-4` is **CLOSED** by this decision.

---

## §6B OD-6 — FM-1 RISK-FREE CONVENTION (adopted 2026-09-14)

```
SERIES              = FRED DGS3MO
OBSERVATION         = last available NON-MISSING print on or before the decision date
FRESHNESS           = must be no older than 7 CALENDAR DAYS
MONTHLY_CONVERSION  = rf_t = Y / 100 / 12
LOCKING             = the accepted rf_t is locked with the prospective position for that month
FALLBACK_SERIES     = NONE
```

**If no valid `DGS3MO` print exists within the 7-calendar-day freshness window:**
`RF_MISSING = TRUE`.

**Forbidden in that case:** substituting `DGS1MO` · carrying forward an arbitrarily
old yield · interpolating · using a future observation · inventing another rate
source.

- **The canonical PRIMARY is completely unaffected by `RF_MISSING`.**
- **FM-1 must preserve the SAME scored-month sample as the primary.** Do not drop an
  RF-missing month from FM-1; do not silently shorten FM-1's `N`; do not impute the
  rate.
- If the missing rate is later established, **before the reveal**, to be a purely
  mechanical / vendor transmission issue and can be recovered **causally** under the
  sealed correction rule, it **may be repaired** and is logged as a mechanical
  correction.
- If any `RF_MISSING` month remains unresolved at the terminal reveal:
  `FM-1 FORMAL SIGN ADJUDICATION = NOT ADJUDICABLE — DATA INCOMPLETE`, while
  `PRIMARY ADJUDICATION = UNAFFECTED`. **This is a complementary-data failure, not a
  primary-study failure.**

Blocker `SB-1` is **CLOSED** by this decision.

---

## §6C OD-7 — FM-1 DECISION SCALE (adopted 2026-09-14)

```
FM-1 HAS NO +0.30 / -0.20 MATERIALITY FLOORS.
```

The primary materiality scale is **not borrowed**. FM-1 asks a narrower
complementary question: *does the idealised funding-adjusted residual have an
established positive or negative sign under the sealed convention?* It uses the
**same central 95 % bootstrap architecture** (OD-5), against zero:

```
FM1_POSITIVE          :  lower bound > 0
FM1_NEGATIVE          :  upper bound < 0
FM1_SIGN_UNRESOLVED   :  otherwise
```

**Do not use `MATERIAL_POSITIVE_PERSISTENCE`, `MATERIALLY_ADVERSE` or
`MATERIAL_PERSISTENCE_RULED_OUT` for FM-1.** Those materiality labels belong to the
primary scale.

FM-1 remains: `COMPLEMENTARY` · `SAME_FORWARD_SAMPLE = YES` ·
`INDEPENDENT_REPLICATION = NO` · `CAN_RESCUE_PRIMARY = NO` ·
`CAN_REPLACE_PRIMARY = NO` · `CAN_BECOME_FALLBACK_PRIMARY = NO` ·
`CAN_UPGRADE_CANONICAL_CLAIM = NO`.

Blocker `SB-2` is **CLOSED** by this decision.

---

## §6D Status of the decisions as a whole

- **OD-1 to OD-4 remain authoritative and unchanged.** Nothing in OD-5 to OD-7
  alters the canonical strategy, the `+0.30 / −0.20` scale, `N = 120`, the single
  terminal reveal, FM-1's complementary status or the attrition policy.
- **Aaron confirmed the original transcription** of OD-1 to OD-4 on 2026-09-14.
- **OD-5, OD-6 and OD-7 were adopted by Aaron** on 2026-09-14, after the S1 draft
  surfaced the three questions as blockers.
- **`SB-1`, `SB-2` and `SB-4` are CLOSED** by these decisions.
- **`SB-3` remains OPEN.** It is an **implementation-verification blocker only**: it
  blocks `C_D_PASS` and **does not block the C-A S1 seal**.
- **Nothing was sealed or implemented by these decisions.** They fix contract
  content; the seal, the C-D implementation authorization, the C-A implementation
  authorization and every run and reveal authorization remain outstanding and
  Owner-only.

---

## §6E OD-8 — SEAL C-A (Owner authorization, 2026-09-13)

```
AARON_OWNER_AUTHORIZATION = SEAL C-A
C_A_SEAL_TIMESTAMP_UTC    = 2026-09-13T17:42:06Z
SEALED_BY                 = Aaron (Owner)
SEAL_EXECUTED_BY          = Claude Opus 5, Main Agent, C-A S1 seal session
SCOPE                     = THE C-A S1 SEAL ONLY
```

**What this authorization did.** It sealed the C-A preregistration
(`../research/extensions/ca/CA_PREREGISTRATION_DRAFT.md`, path retained per the X01
and Value convention; the document now reads **SEALED**). The seal changed **status
metadata only** — §A–§Z are byte-identical to the pre-seal bytes Aaron accepted.
OD-1 … OD-7 are now frozen sealed contract terms, and the T4 seal for this claim
family exists as of the timestamp above.

**Artifacts bound by this seal**, each pinned by SHA-256 in `../PROJECT_STATE.md`:
the sealed preregistration · this Owner Decision Record · the C-D verification
specification draft as the referenced prerequisite specification at seal time · the
instrument registry · the snapshot registry · `S_0` (path, hash, byte size,
acquisition identity) · the frozen historical panel · the C-A validators.

**What this authorization did NOT do — none of these is consumed.**

- It did **not** start S2, and no §Z.2 build item is authorized.
- It did **not** authorize the C-A implementation, the C-D implementation, or any
  independent C-D engine.
- It did **not** create `S_G` and did **not** authorize pipeline go-live.
- It did **not** start the prospective scoring stream: `PIPELINE_GO_LIVE` does not
  exist, so `N_scored = 0` and `FIRST_ELIGIBLE_SCORED_PERIOD` is **NOT YET
  DETERMINED**. No accrued pre-go-live month may ever be retroactively scored.
- It did **not** authorize any run, and `TARGET_RUN_AUTHORIZED = NO`. **No record
  was written to `EXECUTION_AUTHORIZATIONS.md`**, which is the execution axis and
  is not the seal axis; a seal is not permission to execute.
- It did **not** reveal any outcome, compute any target performance, resolve
  `SB-3`, reopen C-B, or start Phase C.

**A seal is not an exposure event.** Consistent with every prior seal in this
repository, no row was added to `EXPOSURE_LEDGER.md` for the seal act itself.

---

## §7 What was NOT authorized

Explicitly withheld at the time of these decisions, and not created by them:

- sealing any S1 artifact (`S1_SEAL_AUTHORIZED = NO`);
- implementing C-A or C-D (`*_IMPLEMENTATION_AUTHORIZED = NO`);
- executing any target run (`TARGET_RUN_AUTHORIZED = NO`);
- revealing any target outcome (`TARGET_OUTCOME_REVEAL_AUTHORIZED = NO`);
- computing any target performance, historical or prospective, for this programme;
- reopening C-B;
- starting the static-premium / timing-mechanism lineage;
- any data access beyond the existing grant; any purchase of data; any account
  registration;
- `git push`, opening or reopening a PR, merge, shared-history revert, force-push,
  or direct modification of `develop` / `main`.

**No T4 clock has started.** Under `../research/extensions/LOCKBOX_PROCEDURE.md` §1
and §5 a T4 clock starts per candidate **at that candidate's seal**, and nothing is
sealed. Accrued post-boundary history (after the ETF panel's frozen boundary
`2026-06-12`) is **not** T4 and **not** verified T3; its exposure status remains
`UNKNOWN_PENDING_AUTHORITATIVE_VERIFICATION`.

---

## §8 Scientific lineage — who contributed what

Recorded because Fable and Astra **materially contributed** to the adopted design,
and because contribution and certification are different things.

| Seat | Contribution |
|---|---|
| **Aaron (Owner)** | **Final Owner authority.** Every decision in §2–§6 is Aaron's, made by Aaron, and adopted by Aaron. No agent made any of them. |
| **Claude Fable 5.1** (constructive design) | S0 scientific frame; the prospective C-A architecture and its design alternatives; the bounded C-A repair (`TSMOM-CONF-FABLE-PHASE-B-CA-02`); the Owner-decision advisory for OD-1 to OD-4. |
| **GPT-6 Astra** (independent challenger) | The C-B challenge; canonical claim-identity reasoning; the independent OD-1 / OD-2 advisory; materiality and horizon contribution. |
| **Claude Opus 5** (Main Agent / builder) | Outcome-blind feasibility; this record; the C-A preregistration draft; the C-D verification specification draft. |
| **Aaron-side ChatGPT** | Acceptance checking, routing and prompt drafting across the Phase B sequence. Never the builder, never a decision authority. |

**Astra's standing on the adopted elements — stated precisely.** Astra was an
**independent advisor before adoption**. For any design element Astra materially
proposed and Aaron then adopted, Astra is thereafter a **design contributor**, and
**Astra is not an independent certifier of those elements**. The same applies to
Fable. Independence is carried by the session, and a session that helped produce a
deliverable is never the sole certifier of it.

**Owner decisions were made by Aaron.** Neither Astra nor Fable made any decision
recorded in §2–§6; both advised, and the advice on OD-1 and OD-2 was not adopted
unchanged (Fable recommended `+0.15 / −0.15`; the Owner chose `+0.30 / −0.20`).

**OD-5, OD-6 and OD-7 (§6A–§6C) are likewise Aaron's.** They were adopted on
2026-09-14 after the Opus S1 draft surfaced the three questions as blockers and
declined to choose them. **No Fable or Astra call was made in either S1 session** —
neither the 2026-09-13 drafting session nor the 2026-09-14 bounded repair — so
neither seat contributed to, or certified, OD-5, OD-6 or OD-7. Opus drafted the
options and the consequences; Aaron decided.

**Recorded record gaps (non-blocking, disclosed rather than papered over):** the
Opus outcome-blind feasibility pass and the independent Astra OD-1 / OD-2 advisory
have **no durable artifact in this repository** at the time of writing; both were
chat-carried. The Fable memos do exist on disk in the workspace root
(`../../2026-09-13-tsmom-phase-b-prospective-confirmation-programme-fable-01.md`,
`../../2026-09-13-tsmom-phase-b-c-a-final-s0-repair-fable-02.md`,
`../../2026-09-13-tsmom-phase-b-owner-decision-advisory-fable-03.md`). Whether to
transcribe the two missing inputs into the repository is an Owner decision; it is
not required for the S1 draft and does not block the seal.

---

## §9 Owner decisions the Owner has *not yet* made

These are not open design questions — they are the remaining Owner gates plus the
small register of items the draft contracts could not resolve from existing
authority.

1. ~~Confirm this record is a faithful transcription.~~ **DONE 2026-09-14**
   (`RECORD_STATUS` above).
2. ~~Resolve the S1 draft blockers.~~ **DONE 2026-09-14** — `SB-1`, `SB-2` and `SB-4`
   are closed by OD-6, OD-7 and OD-5 respectively. `SB-3` remains **OPEN** and is an
   implementation-verification blocker only: it blocks `C_D_PASS`, **not** the C-A
   S1 seal. The register is
   `../research/extensions/ca/CA_PREREGISTRATION_DRAFT.md` §Y — the single
   authoritative one; the C-D specification points at it rather than duplicating it.
3. **Seal the C-A preregistration** — after the seal-time snapshot / provenance
   procedure, the instrument registry pinning, and acceptance (C-A §Z.1).
4. **Authorize the C-D implementation** — a separate decision from the seal, and
   separately, the bounded zero-cost second-source feasibility probe for `SB-3`.
5. **Authorize the C-A implementation and pipeline go-live** — a separate decision
   again, gated by C-A §Z.2, none of whose items gates the seal.

Every later gate — the terminal reveal, promotion, falsification, retirement — is
Owner-only under vNext §10 and is not pre-committed by anything here.

---

## §10 Append log

| Date (UTC) | Appended | By |
|---|---|---|
| 2026-09-13 | Record created at S1 entry. §1 stage state; §2 programme structure and the immutable canonical strategy; §3 OD-1 (+0.30 / −0.20, strict crossing); §4 OD-2 (N = 120, one terminal reveal, no automatic extension); §5 OD-3 (FM-1 complementary, neutral language, cannot rescue, replace or upgrade); §6 OD-4 (ALL_17_REQUIRED, freeze-not-reveal, ambiguity → terminate); §7 what was not authorized; §8 scientific lineage and the two disclosed record gaps; §9 remaining Owner gates. Nothing sealed, implemented, executed or revealed. | Claude Opus 5, S1 entry session, under Aaron's `ENTER S1` authorization |
| 2026-09-14 | **Aaron confirmed** that the §2–§6 transcription of OD-1 … OD-4 is faithful; `RECORD_STATUS` moved `DRAFT` → `CONFIRMED`. **Aaron adopted three further S1 decisions**, appended as §6A OD-5 (one central 95 % stationary-bootstrap percentile interval; no 90 % alternative; no separate one-sided interval; no post-outcome selection; the high probability of `UNRESOLVED` intentionally accepted), §6B OD-6 (FM-1 rf convention: DGS3MO, last non-missing print on or before the decision date, ≤ 7-calendar-day freshness, `Y/100/12`, locked with the position, no fallback; `RF_MISSING` leaves the primary completely unaffected and yields `NOT ADJUDICABLE — DATA INCOMPLETE` for FM-1 if unresolved at the reveal), and §6C OD-7 (FM-1 has no `+0.30 / −0.20` floors; sign against zero only). §6D records that OD-1 … OD-4 remain authoritative and unchanged, that `SB-1`, `SB-2` and `SB-4` are closed, and that `SB-3` remains open as a `C_D_PASS` blocker only. §5 carries a forward pointer to OD-6 / OD-7; §9 items 1 and 2 marked done. **Nothing was sealed or implemented by these decisions.** | Claude Opus 5, S1 bounded-repair session, under Aaron's `FINAL S1 BOUNDED REPAIR` authorization |
