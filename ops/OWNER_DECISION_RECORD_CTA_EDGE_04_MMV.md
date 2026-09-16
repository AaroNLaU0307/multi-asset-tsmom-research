# OWNER DECISION RECORD — CTA-EDGE-04-MMV (macro momentum on vintage data)

```
RECORD_TYPE        = OWNER_DECISION_RECORD
LINEAGE            = CTA-EDGE-04-MMV
DATE_OF_DECISIONS  = 2026-09-16
OWNER              = Aaron  (the only authority for every decision recorded here)
ADVICE SEAT        = Claude Fable 5.1 — DESIGN-EXPOSED / NOT INDEPENDENT
RELAY              = programme controller (Aaron-side ChatGPT), CTA-EDGE-04-MMV
                     S1 DESIGN + DATA FREEZE + PREREGISTRATION + CONDITIONAL SEAL brief
RECORDED_BY        = Claude Opus 5 (Main Agent / builder seat), S1 session 2026-09-16
WORKFLOW_AUTHORITY = ../QUANT_WORKFLOW_VNEXT.md  (vNext, cutover 2026-09-12)
```

**Every decision below was made and recorded BEFORE any historical MMV macro feature,
composite, position, separability result or return was computed.** At the time of writing
none of those objects exists anywhere in this repository, and the S1 seal does **not**
exist — see [`../research/extensions/mmv/MMV_S1_HOLD_RECORD.md`](../research/extensions/mmv/MMV_S1_HOLD_RECORD.md).

**What this file is not.** Not a preregistration, not a seal, not authorisation to
implement, not authorisation to run, not an exposure event. It creates no row in
`EXPOSURE_LEDGER.md`, no record in `EXECUTION_AUTHORIZATIONS.md` and no trial in
`../research/extensions/TRIAL_LEDGER.md`.

---

## §1 Stage state at the time of recording

```
S0 FRAME                = COMPLETE / PASS AFTER OWNER RESOLUTION
MMV-OD-1 .. OD-5        = DECIDED by this record
S1 DESIGN               = **HOLD** — two unbound aggregation rules (see §7)
S1 SEALED               = NO
S2 BUILD_AUTHORIZED     = NO
GATE 0.5 RUN            = NO
TARGET_RUN_AUTHORIZED   = NO
DATA FREEZE             = BLOCKED — no ALFRED API key present (§6)
```

---

## §2 MMV-OD-1 — the real-time information concept

```
DECISION_ID = MMV-OD-1
STATUS      = OWNER-CONFIRMED, BINDING

PRIMARY_INFORMATION_CONCEPT = LATEST_KNOWN_AS_OF_DECISION_DATE

At every canonical monthly decision date, reconstruct the macro history exactly as
publicly known at that cutoff, using ONE ALFRED vintage snapshot valid at that date.

PRIMARY SIGNAL LABEL = POINT_IN_TIME_MACRO_STATE_MOMENTUM

IT IS NOT:  macro news · macro surprise · first-release alpha · revision alpha
```

```
FIRST_RELEASE_CHAIN = DESCRIPTIVE CONCORDANCE DIAGNOSTIC ONLY
  PROMOTION_POWER = NONE
  RESCUE_POWER    = NONE
  KILL_POWER      = NONE
It reports disagreement and never changes the primary verdict.
NO large/small disagreement threshold is introduced.
```

**Why it matters, recorded now so it cannot be re-litigated after a result.** The traded
object is a **state**, re-read monthly, not a **shock**. Revisions enter only by changing
that state; the information shock between two decision dates is never decomposed and never
conditioned on. Fable's advice (§9 decision block) records eight supporting reasons, of
which the load-bearing one is that F5's premium is for acting on **public** information
before consensus catches up, and the public information at a decision date includes every
revision published by then.

**Structural consequence, verified in §5 below:** under the MMV-OD-2 series identities the
revision channel is confined to the **growth leg**. `CPILFENS` is final when issued and
the FOMC target is administered and never revised, so for those two legs the
first-release and latest-known concepts coincide.

## §3 MMV-OD-2 — series identity: inflation

```
DECISION_ID = MMV-OD-2 (inflation)
STATUS      = OWNER-CONFIRMED, BINDING. This is an OWNER REPAIR of an internally
              inconsistent F5 authority — F5 field 3 says "core CPI or core PCE" while
              F5 field 5 lists CPIAUCSL, which is HEADLINE. F5 must NOT be represented
              as having already fixed CPILFENS exactly.

INFLATION CONCEPT = core consumer-price inflation MOMENTUM
RAW SERIES        = CPILFENS   (CPI-U, all items less food and energy, NOT seasonally
                    adjusted)

pi12(m)          = CPILFENS(m) / CPILFENS(m-12) - 1
INFLATION SIGNAL = sign[ pi12(m) - pi12(m-12) ]

Interpretation: core inflation is higher or lower than one year earlier.

FORBIDDEN as alternative primary series: CPIAUCSL · CPILFESL · PCEPILFE
NO series family.
```

**Why the rate and not the index level.** Under a literal reading of F5's transform the
12-month change of a core price index **is** `pi12`, and its sign has been `+1` in every
month of the canonical window. That is a static long bet, not a momentum signal, and it
would have made the inflation leg a constant. Taking the momentum **of the rate** is the
smallest repair that keeps F5's fixed number 12 and its sign-only rule intact.

**Why not seasonally adjusted.** BLS states the unadjusted CPI-U series *"are final when
issued"*, while seasonally adjusted indexes *"are subject to revision for up to 5 years"*.
Choosing `CPILFENS` removes seasonal-factor revision from the signal entirely, and a
12-month change of an unadjusted index needs no seasonal adjustment by construction.

## §4 MMV-OD-2 — series identity: policy

```
DECISION_ID = MMV-OD-2 (policy)
STATUS      = OWNER-CONFIRMED, BINDING

POLICY CONCEPT = administered FOMC federal-funds target stance

target(t) = DFEDTAR                              through 2008-12-15
          = midpoint(DFEDTARL, DFEDTARU)         from  2008-12-16 onward

POLICY SIGNAL = sign[ target(t) - target(t - 12 months) ]
sign(0) = 0

FORBIDDEN: FEDFUNDS · DGS2 · any traded yield.
DGS2 / the 2-year yield is PERMANENTLY EXCLUDED from the MMV signal.
```

**The splice boundary is the official one, verified this session, not chosen.** FRED
`DFEDTAR` is titled *"Federal Funds Target Rate (DISCONTINUED)"*, runs 1982-09-27 →
**2008-12-15**, and carries the note *"Effective December 16, 2008, target rate is
reported as a range"*, naming `DFEDTARU` and `DFEDTARL` as its replacements. The sealed
splice date is therefore the series boundary itself and involves no judgement.

**Why the administered target and not the 2-year yield.** `DGS2` is the yield of the
assets this leg would trade — `SHY` holds 1–3-year Treasuries and `IEF`/`TLT` move with it
through the curve — so a leg built from it would be partly a transform of panel returns
and would break `MACRO_SIGNAL_CONSTRUCTIBLE_WITHOUT_PRICE`. `FEDFUNDS` is excluded as a
market-determined effective rate; the decision object is the **administered stance**.

**No vintage problem on this leg.** FOMC target decisions are announced and never revised,
so first-release and latest-known-as-of coincide here by construction.

## §5 MMV-OD-3 — MMV-specific economic materiality

```
DECISION_ID = MMV-OD-3
STATUS      = OWNER-CONFIRMED, BINDING

M2_METRIC   = calendarised annualised Sharpe of the NET MMV monthly return series
              rf = 0
              Sharpe = mean(monthly net) / sd(monthly net, ddof=1) * sqrt(12)
M2_VALUE    = +0.30
M2_OPERATOR = STRICT  >
PASS iff the LOWER 95 % confidence endpoint > +0.30.

M1_RULE     = lower 95 % bound of mean NET monthly return > 0, STRICT.
GATE1_RULE  = lower 95 % bound of mean GROSS monthly return > 0, STRICT.
              A point estimate alone never passes any of the three.
```

```
THIS IS AN MMV-SPECIFIC DECISION AND IS NOT A PORTABLE PROGRAMME-WIDE FLOOR.
It is NOT inherited from C-A, from CTA-EDGE-01-TA or from CTA-EDGE-02-BENB, and the
numerical coincidence with BENB's +0.30 creates no precedent in either direction.
BENB-OD-1 already established that a materiality bar is lineage-specific.
```

**Reason:** MMV is proposed as a standalone monthly cross-asset systematic sleeve under
the common canonical risk wrapper. The programme requires meaningful standalone
usefulness, not merely a positive point estimate.

## §6 MMV-OD-4 — the separability kill threshold

```
DECISION_ID = MMV-OD-4
STATUS      = OWNER-CONFIRMED, BINDING. Resolves F5's approximate "about 80 %" language
              to an exact, inclusive boundary, BEFORE any exposure.

SEPARABILITY_METRIC = POOLED_EXACT_SIGN_AGREEMENT
  = (# eligible instrument-month cells where MMV_sign(i,t) == TSMOM_sign(i,t))
  / (# all eligible instrument-month cells where BOTH signals are defined)

  Signs are drawn from {-1, 0, +1}. ZERO IS A REAL POSITION STATE:
      0 vs 0        = AGREEMENT
      0 vs +1 / -1  = DISAGREEMENT
  Do not condition only on active months. Do not discard zeros.

NOT_SEPARABLE_AT_POSITION_LEVEL  iff  POOLED_EXACT_SIGN_AGREEMENT >= 80.0%   INCLUSIVE
  79.999...%  -> does NOT trigger the kill
  80.000...%  -> TRIGGERS the kill

If triggered: STOP before any historical return evaluation.
  PROGRAMME_STATUS = NOT_PROMOTED
  FAILURE_TYPE     = NOT_SEPARABLE_AT_POSITION_LEVEL

Per-instrument agreement rates are DIAGNOSTIC ONLY: they cannot rescue a pooled
failure and cannot independently kill a pooled pass.
```

**What a trigger does and does not mean.** It means the proposed MMV sleeve is too close
to the canonical TSMOM position state for this lineage to justify spending another
historical-return trial. It does **not** mean macro information is false, that the
mechanism is falsified, or that TSMOM causes the macro state.

## §7 MMV-OD-5 — execution and cost footing

```
DECISION_ID = MMV-OD-5
STATUS      = OWNER-CONFIRMED, BINDING, conditional on the canonical-authority check
              below, which this session performed and PASSED.

ONE_WAY_COST   = 2 bps of turnover
COST_AUTHORITY = config.py:196  TRANSACTION_COST_BPS = 2.0
                 "one-way cost per unit turnover (liquid-ETF convention)"

CANONICAL RISK WRAPPER, adopted as COMMON INFRASTRUCTURE and NOT as alpha:
  asset volatility estimator  config.py:168  VOL_WINDOW_DAYS = 60
  asset vol target            config.py:169  TARGET_VOL_ANNUAL = 0.10
  asset position cap          config.py:170  MAX_ASSET_WEIGHT = 2.0
  live assets                 config.py:176  EQUAL-WEIGHT aggregation
  portfolio vol target        config.py:182  PORT_TARGET_VOL_ANNUAL = 0.10
  gross leverage cap          config.py:184  MAX_GROSS_LEVERAGE = 3.0

EVERY EXPECTED PARAMETER IN THE CONTROLLER BRIEF MATCHES THE REPOSITORY AUTHORITY
EXACTLY. No difference to report.

CANONICAL TSMOM ITSELF IS NOT ALTERED. It remains the frozen research benchmark.
```

**Execution mechanics are the same, verified rather than assumed.** `src/portfolio.py`
documents the canonical convention: a weight *"decided at a month-end close is only
applied from the next session onward"* (`reindex(daily).ffill().shift(1)`, "no same-bar
look-ahead"). MMV trades the same universe, at the same monthly frequency, through the
same wrapper and the same decision-to-execution lag, so the 2 bps liquid-ETF convention is
adopted on identical mechanics and not transplanted onto different ones.

## §8 Information cutoff — compatibility checked, not asserted

```
INFORMATION_CUTOFF = 15:45:00 America/New_York on the canonical month-end trading day
STATUS             = COMPATIBLE with the repository's canonical execution convention.
```

The canonical book **decides at the month-end close and executes from the next session**.
A 15:45 ET macro cutoff therefore sits strictly *before* the canonical decision timestamp
(~16:00 close) and well before the canonical execution (next session), so it is
**conservative in the safe direction** and cannot create look-ahead. No conflict exists
and no HOLD is raised on this point.

One asymmetry is recorded rather than smoothed over: the canonical TSMOM comparison signal
is formed from the 16:00 close while MMV's macro information is cut at 15:45. For Gate 0.5
this means MMV knows strictly *less* than the benchmark it is compared against, which
biases nothing in MMV's favour.

```
SAME-DAY RELEASE RULE
  eligible iff the OFFICIAL release timestamp <= the cutoff.
    08:30 ET CPI / payroll release      -> eligible
    09:15 ET industrial production      -> eligible
    14:00 ET FOMC announcement          -> eligible
    any release after 15:45 ET          -> NOT eligible until the next decision date
  If a same-day vintage exists but its release time CANNOT be established:
    USE THE PRIOR ELIGIBLE VINTAGE. Do not guess.
```

## §9 What these decisions do NOT decide

```
GROWTH-LEG AGGREGATION   how sign(D12 INDPRO) and sign(D12 PAYEMS) combine     UNBOUND
MACRO-COMPOSITE RULE     how growth, inflation and policy combine into a
                         per-instrument direction                              UNBOUND
```

Both are recorded as unresolved in
[`../research/extensions/mmv/MMV_S1_HOLD_RECORD.md`](../research/extensions/mmv/MMV_S1_HOLD_RECORD.md)
and are the reason S1 did not seal. Neither was invented here.

## §10 Design exposure

```
FABLE_DESIGN_EXPOSED = YES
  Fable originated F5, advised MMV-OD-1, and materially influenced the information
  concept and the series clarification. Adopting its advice does not restore
  independence: it remains DESIGN-EXPOSED and can never be a blind certifier of this
  design, implementation or result.
  Advice artifact: Quant trade/2026-09-16-cta-edge-04-mmv-od-1-information-concept-fable-01.md
  sha256 9c76f13d9cf02ce48502d40831d158439a0cabe39572caee884dce77ec987f58 (385 lines)

ASTRA_DESIGN_EXPOSED = NO
  PROVENANCE LIMITATION: Astra's Round-1 CTA map is NOT PERSISTED in this workspace.
  The NO means NO RECORDED ASTRA CONTRIBUTION TO MMV. It is not positive proof that
  Astra never considered anything adjacent, and must not be represented as such.
```

Seat rows are written to `REVIEWER_EXPOSURE_LOG.md` **at seal**, per the TA / BENB
convention. None is written here, because there is no seal.
