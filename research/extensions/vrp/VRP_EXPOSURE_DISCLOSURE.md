# TSMOM-VRP-01 — EXPOSURE DISCLOSURE (S1)

```
LINEAGE  = TSMOM-VRP-01
SCOPE    = what the S1 session accessed, who contributed, what is design-exposed, and the ledger rows to be appended at S2 acceptance
```

## 1. S1 session access audit — what was and was not touched

| Category | Accessed | Detail |
|---|---|---|
| Historical VIX-futures settlement values | **NO** | none exist in the repository (verified by tracked-file name search: no `vix`, `vx`, `vxx` or `cboe` files) and none were fetched |
| VIX-futures price or index return histories | **NO** | no download, no API call, no web page displaying performance was opened |
| Any candidate-return series, carry statistic, Stage-A or Stage-B outcome | **NO** | none exists |
| Protected C-A store, key, position or return layers | **NO** | not read; the C-A package files in `research/extensions/ca/prospective/` were listed by name only to confirm the worktree is unaffected by the seal branch; none was opened |
| Canonical rule computed on any month after 2026-09-11 | **NO** | no canonical quantity computed at all |
| Repository documents read | YES | `PROJECT_STATE.md`, `.gitattributes`, `.gitignore`, the C-A contract's §X and §Z, the X01 contract's §6.1 bootstrap protocol, the C-A validator's header, `SAMPLE_REUSE.md` §5–§6, git metadata |
| Workspace-root inputs read | YES | the repaired S0 frame and the Owner Decision Record (hashes recomputed and matched) |
| External documents | **NO** | none opened this session; contract-specification, calendar, fee and methodology facts were stated from prior knowledge and are to be **sourced and hashed at acquisition** under §L of the contract; nothing in the sealed rules depends on their exact historical values (the rules are conditional on the documented history) |
| Market facts used | design-exposed only | the S0 episode list; no new market fact was introduced |

## 2. Contributor provenance — binding

- **Aaron** (Owner): authorised S0, the repair, the delegation of VRP-OD-2…9, and S1 DESIGN + SEAL. Owner gates after this seal (acceptance, data-acquisition authorisation, execution authorisation, reveal, verdict) remain Aaron's.
- **Claude Fable 5.1** — `MATERIAL_DESIGN_CONTRIBUTOR`: Phase-C map, Phase-C final adjudication, S0-01, S0-02-repaired, the delegated Owner decisions (under explicit delegation), this S1 package. **Not** a blind certifier of any of it, ever.
- **GPT-6 Astra** — `MATERIAL_DESIGN_CONTRIBUTOR`: the independent Phase-C map and the accepted S0 challenge whose repairs shaped the contract. **Not** a blind certifier of any of it, ever.
- **ChatGPT (Aaron-side)** — programme controller / acceptance checker; never the builder.
- **Claude Opus / Claude Code** — the future S2 builder (not yet dispatched); its session is the Main Agent and is never the sole certifier of its own material deliverable.
- **Certification plan (sealed in the contract §T and the Owner Decision Record VRP-OD-9):** historical results are judged by a fresh top-level session of the default independent reviewer **with this contributor disclosure on the record**; prospective terminal results by a genuinely uninvolved reviewer.

## 3. Design-exposed evidence — recorded so it can never be presented as fresh confirmation

Episodes: the GFC; the 2010 volatility / flash-crash episode; February 2018; March 2020; the CY2022 core-stress context; the August 2024 volatility episode; the April 2025 volatility episode. Facts: approximate public magnitudes of front-month VIX-futures moves in those episodes; the already-revealed canonical TSMOM crisis behaviour (X46; GFC, COVID and CY2022 window returns; SPY-left-tail statistics, including the core's tail-month mean). The Phase-C planning sentence ("at meaningful size a short VIX sleeve may erase the core's crisis gain; at a small enough size it may not matter") is a hypothesis this lineage tests, never a verdict. **None of these was used to calibrate any constant**; `J` was chosen for plausibility, `delta_tail` from the sleeve's own economics, and no threshold was chosen because history is known to clear it.

## 4. Evidence context and sample exposure

- Historical Stage A: **`DESIGN_INFORMED_FIRST_LOCAL_USE`** — locally unsearched (subject to repository verification), globally saturated (VIX futures are heavily studied; the sign of the long-run gross carry is public knowledge; new vendor bytes create no new market events). Never "fresh", never "independent".
- Historical Stage B: **T0** on the core side — a further declared reuse of the frozen ETF panel (ninth-plus) and of the frozen canonical stream over months ≤ 2026-05-31.
- Prospective clocks: T4 for the VRP family only, from this seal, under the family's own store; they confer nothing on C-A and take nothing from it.

## 5. Ledger rows to be appended at S2 acceptance (drafted here; appended by the accepted S2 session, not by S1)

**`research/extensions/SAMPLE_REUSE.md`** — two rows:
1. New dataset row `dataset.cboe.vix-futures-monthly-chain` (provisional id until KB registration): "Monthly VX contract-level official daily settlements, listing → final settlement, acquired under `VRP_PREREGISTRATION.md` §L after Owner data authorisation; **`N_trials = 0`** before Stage A under the programme's existing convention (one trial per distinct constructed strategy-return series with a selection opportunity; diagnostics excluded); the sealed Stage-A primary is its first governed trial (+1); bootstrap replicates, VRP-DESC and `PROMOTION_POWER = NONE` sensitivities are not attempts; historical evidence context `DESIGN_INFORMED_FIRST_LOCAL_USE`."
2. ETF-panel row: "TSMOM-VRP-01 Stage B — paired combination of the frozen canonical net stream (≤ 2026-05-31, recomputed by the pinned modules per the Value §17 comparator identity) with the Stage-A sleeve in a self-financing book at `s = 0.20`; **T0, further reuse of the frozen panel (ninth-plus)**; SPY monthly returns used for the X46 tail rule; the frozen panel's historical count convention (`D-ETF-COUNT`) untouched."

**`research/extensions/TRIAL_LEDGER.md`** — `HYPOTHESIS_FAMILY = F-VRP` declared before any member runs: members VRP-A (primary, governed attempt), VRP-B (primary, conditional), VRP-DESC R1–R14 (`PROMOTION_POWER = NONE`); no automatic +1 per attempt.

**`ops/EXPOSURE_LEDGER.md`** (existing single table; existing tokens only) — one `NO_OUTCOME` / `PURE_MECHANICAL_VERIFICATION` row for this S1 seal (sample: none read; revealed: nothing; session: Claude Fable 5.1 under Aaron's S1 DESIGN + SEAL authorisation; design-exposed episode list attached by reference to this file); later, `NO_OUTCOME` rows for acquisition and each prospective snapshot before use; `GENERATED_NOT_SEEN` rows for generated evidence; one `REVEALED_TARGET_METRIC` row per authorised reveal.

**`ops/REVIEWER_EXPOSURE_LOG.md`** (seat axis) — rows recording Fable and Astra as `material_design_contributor` for `TSMOM-VRP-01`, barred from blind certification of this design.

**`PROJECT_STATE.md`** — a `TSMOM-VRP-01` block (state only, never workflow authority): `STAGE = S1 SEALED — ACCEPTANCE PENDING`, `DATA_GRANT = none for VIX futures; acquisition requires a separate Owner authorisation`, `OUTCOME_EXPOSURE = none`, `NEXT_OWNER_DECISION = accept the S1 seal; then authorise data acquisition`.

## 6. What this disclosure does not do

It appends nothing itself (the S1 session modifies only the `research/extensions/vrp/` package). It authorises no acquisition, no run and no reveal. It upgrades no canonical TSMOM evidence.

*The SHA256 of this file is recorded in `VRP_SEAL_MANIFEST.md`.*
