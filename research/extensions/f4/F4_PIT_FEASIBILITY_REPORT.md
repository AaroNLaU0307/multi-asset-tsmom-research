# CTA-EDGE-05 / F4 — PIT FEASIBILITY REPORT

```
RECORD_TYPE = METADATA_PIT_FEASIBILITY_REPORT
LINEAGE     = CTA-EDGE-05 (F4 INVENTORY_STATE_COMMODITY_CURVE)
DATE        = 2026-09-18
SCOPE       = BLOCKING DATA / PIT FEASIBILITY ONLY. Not a scientific F4 test.
RULE        = F4-AUDIT-RULE-1, frozen BEFORE sampled retrieval,
              research/extensions/f4/F4_METADATA_AUDIT_RULE.md
              sha256 5c9c4289fe209c2d7a0a67036d7b02d246132ceda88b84ae5973ee2c63296a36
```

```
TASK_STATUS                = HOLD
LOAD_BEARING_F4_PIT_GATE   = HOLD
```

> **SUPERSEDED IN PART — 2026-09-19. Appended; nothing below is edited.**
> The frozen sample has since been executed. See
> [`F4_FROZEN_SAMPLE_EXECUTION.md`](F4_FROZEN_SAMPLE_EXECUTION.md). Three
> findings below are now known to be wrong or incomplete, and are corrected
> there rather than rewritten here:
>
> * **Natural gas is class B, not D.** The revisions file is not a sparse
>   revision log — it is a COMPLETE consecutive weekly series of originally
>   published values, 565 weeks with zero gaps and zero duplicates, so first
>   publication needs no inversion and no judgment.
> * **The originals start 2015-06-19**, not “November 2015”; the November 2015
>   date is when EIA began releasing the file, and it back-fills to June.
> * **A NEW blocker was found that this report did not anticipate:** EIA's
>   published same-week five-year reference for natural gas is NOT
>   reconstructible as-of any release, in any era, because the revisions file
>   carries no revision DATE. `NG_REFERENCE_PIT = E`.
>
> Also superseded: the WASDE archive starts **1973-09**, not December 1973,
> per direct enumeration of the archive's own date facet; and the petroleum
> five-year reference wording exists only from ~2018-08 — earlier vintages
> publish a different, banded “average range” object.

**HOLD, not PARK, and not PASS.** No load-bearing series is proven unreconstructible, so
there is no blocker that would trigger the controller's PARK rule. Equally, no family is
fully established, so nothing passes. The specific reason is named per series below.

---

## §1 Family verdicts

```
PETROLEUM_PIT        = HOLD
NATURAL_GAS_PIT      = HOLD
ENERGY_FAMILY_PIT    = HOLD
GRAINS_OILSEEDS_PIT  = HOLD
GRAINS_FAMILY_PIT    = HOLD
```

| leg | series / table | root | class |
|---|---|---|---|
| Petroleum | `WCESTUS1` commercial crude excl. SPR | CL | **A** |
| Petroleum | `WGTSTUS1` total motor gasoline | RB | **B** |
| Petroleum | `WDISTUS1` distillate fuel oil | HO | **B** |
| Natural gas | WNGSR working gas, Lower 48 | NG | **D** |
| Grains | WASDE U.S. Feed Grain and Corn | ZC | **B** |
| Oilseeds | WASDE U.S. Soybeans and Products | ZS | **B** |
| Grains | WASDE Wheat by Class — Soft Red Winter | ZW | **B** |
| Grains | WASDE Wheat by Class — Hard Red Winter | KE | **B** |
| Oilseeds | WASDE Soybeans and Products — meal section | ZM | **B** |
| Oilseeds | WASDE Soybeans and Products — oil section | ZL | **B** |

Full metadata per series is in `F4_SERIES_INVENTORY.json`.

---

## §2 The four findings that actually matter

### 2.1 Natural gas has no vintage archive, and its usable PIT history starts 2015-11

This is the binding constraint on the whole energy family.

EIA publishes **no per-release vintage archive** for the WNGSR. What it does publish is a
separate **historical file of revisions and reclassifications**, which carries *"the
original estimate prior to the revision or reclassification and the accompanying note"* —
and that file **begins November 2015**.

So first-published natural-gas values are recoverable only by **inverting** the current
history with the revisions file, not by reading a vintage; the completeness of that
inversion is unverified; and before November 2015 the position is
`CURRENT/REVISED_HISTORY_ONLY`.

```
NATURAL GAS  first-published reconstructible  PARTIAL, from 2015-11 only
             class                            D   (pre-2015-11: class C)
```

Petroleum's archive starts **2012-01-05** and the futures panel starts **2010-06-06**, so
**natural gas — not petroleum, and not the futures data — is what binds the energy
window, at 2015-11.** That is roughly eleven years to the panel boundary.

### 2.2 EIA supplies the seasonal reference F4's energy norm needs — for all four legs

`SOURCE_DEFINED_SEASONAL_REFERENCE_AVAILABLE`:

```
WCESTUS1 crude       YES   "N% above the five-year average"      (WPSR summary)
WGTSTUS1 gasoline    YES   "N% below the five-year average"      (WPSR summary)
WDISTUS1 distillate  YES   "NN% below the five-year average"     (WPSR summary)
WNGSR natural gas    YES   "Historical Comparisons": a "Year ago" column and an
                           "N-year average (YYYY-YY)" column, by region and total
WASDE grains         NO    WASDE publishes no multi-year-average convention for
                           stocks-to-use
```

*(Every numeral above is redacted at source — see §5.)*

This matters more than it looks. It means **N-1, the arbitrary reference-length choice,
does not arise for the energy families** — EIA's own five-year same-week convention is
available as the norm, and a percentage deviation from it needs no dispersion window
either. N-1 remains live for grains, where the source supplies no such convention.

**Not yet established:** that the *archived 2012+ WPSR vintages* carry the same summary
wording. Only the current release was inspected. A second caveat is structural and
permanent: EIA recomputes its five-year average from revised history each week, so the
*published* figure is point-in-time but the window behind it is not.

### 2.3 USDA moved WASDE's release time — a documented publication-timing break

```
2013-01-11   WASDE release time changed 8:30 a.m. ET  ->  12:00 p.m. ET
             announced 2012-09-19; also affects Acreage, Crop Production, Grain
             Stocks, Prospective Plantings and Small Grains Summary
```

This does not damage reconstructibility — both regimes are documented — but any F4
snapshot rule that assumes a single intraday convention across the sample would be wrong
on one side of that date. It must be bound before the state is built, not after.

Two further documented breaks: the WNGSR revision threshold changed **7 Bcf → 4 Bcf**
(announced 2014-10-07, implemented November 2015), and the WASDE archive **migrated from
Cornell Mann Library to NAL/ESMIS on 2025-10-01**.

### 2.4 The WASDE archive is the strongest leg, and it resolves three open identities

Every WASDE release from **December 1973** is individually archived and addressable by
date, in PDF/TXT/XLS/XML, with documented gaps at Feb 1974, Feb 1975, Jan 1976 and
Feb 1977. Because each monthly release *is* the first publication, first-published
reconstruction is **structurally** available — far better than either energy leg.

Three `NEEDS_VERIFICATION` items from F4-OD-1D are now resolved from source:

```
WHEAT BY CLASS   RESOLVED. "U.S. Wheat by Class: Supply and Use" exists, with explicit
                 columns Hard Red Winter | Hard Red Spring | Soft Red Winter | White |
                 Durum | Total. So KE -> Hard Red Winter and ZW -> Soft Red Winter are
                 SOURCE-SUPPORTED mappings, not assumptions.
MARKETING YEAR   PARTLY RESOLVED. The class table states "Year beginning June 1" for
                 wheat. Corn and soybean marketing-year START dates are NOT stated in
                 the WASDE text and are NOT asserted here.
MEAL / OIL       RESOLVED. Soybean meal and soybean oil are SECTIONS INSIDE "U.S.
                 Soybeans and Products Supply and Use (Domestic Measure)", not separate
                 root tables.
```

The stocks-to-use denominator exists but its **label varies by table** — `Use, Total` for
soybeans, `Total Use` and `Domestic, Total` elsewhere. A mapping detail to bind, not a
blocker.

Why grains are still class **B** and not **A**: the historical *stability* of these tables
was never verified, because only the current release was inspected and the sampled
historical check was not executed (§4). The wheat-by-class table in particular may not
exist in early releases. Under the frozen rule this fails closed rather than being
upgraded by assumption.

---

## §3 Futures-root compatibility (Phase 6 — existing metadata only)

All ten F4 load-bearing roots are inside the 18-root requested set
(`CL HO RB NG GC SI HG PL PA ZC ZS ZW ZM ZL KE LE HE GF`):

```
ENERGY   CL  HO  RB  NG          GRAINS/OILSEEDS   ZC  ZS  ZW  KE  ZM  ZL
OPTIONAL HG (not audited, per the brief)
EXCLUDED GC SI PL PA (precious) · LE HE GF (livestock)

COVERAGE        2010-06-06 inclusive -> 2026-07-01 exclusive; frozen boundary
                2026-06-30 inclusive (LOCKBOX §2.2, manifest-verified)
CONTRACT META   definition schema, 5,031 per-day files
SETTLEMENT      statistics schema, 5,026 per-day files
EXPIRY META     carried in the definition schema
```

**Stated limitation, not glossed.** Those are the *requested* symbols.
`DATA_INVENTORY_SPEC` explicitly distinguishes "symbols actually present, enumerated" from
"the symbols that were requested", and `LOCKBOX` §2.2 records that per-file SHA-256
re-verification of the 10,058 delivered files **was not run in Wave 0 and is owed before
the first computation on this panel**. Per-root presence and per-root calendar coverage
were **not** independently enumerated here. Open-interest presence for the 18 roots also
remains an open question in `DATA_INVENTORY_SPEC`.

No basis, no trend and no target return was computed or inspected.

---

## §4 What was NOT done, and why — stated so the gap is visible

```
PHASE 5 SAMPLED REVISION CHECK = NOT EXECUTED. Unreached, NOT waived.
```

The audit rule was frozen before any sampled historical record was retrieved, and the
sampled retrieval was then **not performed**. It is reported as unreached rather than
quietly skipped, following the PINS precedent where an unrun consistency check was
recorded the same way.

**Why not a partial run.** The petroleum sample is 45 predeclared releases. Executing
*some* of them would reintroduce exactly the selection freedom the freeze exists to
remove — the easy-to-retrieve ones would be the ones that got done. A stratified sample is
either executed or it is not. The frozen rule means it can be executed later, by anyone,
without bias.

**What it would and would not change.** It would firm up B → A for gasoline, distillate
and the grain tables by confirming field presence and table stability in the vintages. It
would **not** change the verdicts that drive the family gates: natural gas's November 2015
boundary and its missing vintage archive are properties of what EIA publishes, and no
amount of sampling alters them.

The NG and WASDE frames were also never enumerated, so under the frozen rule no sampled
record from either source *may* be retrieved yet.

---

## §5 Firewall — what was read

```
INVENTORY_VALUES_READ            = NO
FUTURES_TARGET_OUTCOME_ACCESSED  = NO
BASIS_COMPUTED                   = NO
TREND_RETURN_COMPUTED            = NO
F4_RETURN_OUTCOME_ACCESSED       = NO
F4_PRIMARY_TRIAL_CONSUMED        = NO
PNL_FREE_PREMISE_EXECUTED        = NO
TIGHT/AMPLE LABEL · z-SCORE · X43 · BACKTEST · SHARPE · HIT RATE  = none computed
```

Phase 5 *permits* reading source-side inventory values as
`DESIGN_INFORMING_MEASUREMENT`. **None were read.** Every document fetched was processed
with **all digits replaced by `N` at the point of extraction**, so structure, labels,
units and timestamps entered the record and quantities did not. That is why every quoted
report sentence in this document appears as *"N% above the five-year average"*.

Dates, policy thresholds (4 Bcf, 10 Bcf, 7 Bcf) and archive years are metadata, not
inventory levels, and are reported unredacted.

**No exposure row is written for this audit.** Nothing here reveals an outcome or a
measurement of the F4 target: public publisher metadata was read, and the repository's own
definition of an exposure event is a computation or read that reveals outcomes or
measurements. The brief also directs that an exposure row must not be invented merely for
reading public metadata.

---

## §6 Choices still unbound (Phase 9 — surfaced, not resolved)

```
NUMERIC
  N-1  multi-year REFERENCE LENGTH where no source convention exists — GRAINS only.
       NOT needed for energy: EIA's five-year same-week reference is source-supplied.
  N-2  DISPERSION WINDOW — only if the z-score form is kept instead of a percentage
       deviation from the source reference.
  N-3  KILL BOUND of any PnL-free separability screen.
  N-4  S1 inference margins.

CATEGORICAL
  WASDE marketing-year switch rule (old-crop / new-crop)
  corn and soybean marketing-year START dates — unverified from source
  meal / oil inclusion as separate primary roots
  stocks-to-use denominator label mapping across tables
  natural gas aggregation — Lower 48 total vs regional
  reconciliation of WCESTUS1 "Excl. Lease Stock" vs "excluding the SPR"
  F4 SAMPLE WINDOW START — currently bound by natural gas at 2015-11
```

None of these were selected. No trailing lookback, z-score window, percentile threshold,
tight/ample cut-off, stocks-to-use norm length, winsorization or composite weight was
chosen, and none may be chosen from an outcome later.

---

## §7 Owner decisions this audit surfaces

```
ROOT_LEVEL_REDUCTION_OWNER_DECISION_REQUIRED = NO
```

No load-bearing root is class C or E, so no root is failing and none is being silently
dropped.

```
WINDOW_START_OWNER_DECISION_REQUIRED = YES
```

This is a **family-window** decision, not a root reduction, and it is recorded as its own
question rather than forced into the root-reduction box. Natural gas is reconstructible
only from **2015-11**. The Owner therefore faces a choice that is not this audit's to
make:

* start the F4 sample at **2015-11**, keeping natural gas and accepting roughly eleven
  years; or
* start earlier and **drop natural gas**, which *would* be a root-level reduction of a
  load-bearing family and needs the same explicit decision; or
* commission the verification that would establish whether EIA's revisions file inverts
  cleanly to first-published values, and whether any pre-2015 vintage source exists.

```
AUDIT_RULE_OWNER_DECISION_REQUIRED = NO
```

The rule was frozen from existing authority without inventing a consequential numeric
choice. The one adaptation with no direct source backing — the `[8, 13]` day-of-month
boundary for "beyond a one-day shift" in the monthly WASDE strata — is flagged in the rule
itself, affects only *which* irregular release is sampled, and touches no F4 quantity.

---

## §8 Provenance

```
F4 origin           2026-09-15-cta-edge-discovery-r1-mechanism-feature-map-fable-01.md
                    sha256 02ca5f45fe41763e55a35309...  (F5-F10 Round-1 map, rank 5)
F4 reconstruction   2026-09-18-cta-edge-05-f4-inventory-state-pre-s0-reconstruction-fable-01.md
                    sha256 21c06528089c5267811ef699...
F4 pre-S0 adjudication
                    2026-09-18-cta-edge-05-f4-inventory-state-pre-s0-independent-adjudication-fable-01.md
                    sha256 a11e54ea44b66f4d95108af4...
F4-OD-1A..1D        2026-09-18-cta-edge-05-f4-od-1a-1d-primary-channel-universe-semantics-fable-01.md
                    sha256 0f08b230ec68ae12e63ee35c...
PINS precedent      research/extensions/pins/PINS_OD1_FEASIBILITY_PROTOCOL.md  fad05d1533bead98...
                    research/extensions/pins/PINS_AUDIT_SAMPLE.json            52e70b40e61a7b36...
                    research/extensions/pins/PINS_EIA_RELEASE_DATES.txt        98a3ebdc4a006075...
                    research/extensions/pins/PINS_OD1_FEASIBILITY_RESULT.md    bcd5ed719a27d7e8...
Panel authority     research/extensions/LOCKBOX_PROCEDURE.md §2.2              5d786ad832a1507e...
Accounting          research/extensions/TRIAL_LEDGER.md · ops/EXPOSURE_LEDGER.md ·
                    research/extensions/SAMPLE_REUSE.md   — read, not modified
```

**Seat provenance, carried forward as the artifact itself states it.** The F4 pre-S0
adjudication discloses that its seat is a **new top-level Claude Fable 5.1 session**, that
independence there is *carried by the session, not by model diversity*, and that the
originating seat was also Fable 5.1 — so if the Owner wants model-diverse review of F4
novelty, that document is Owner-advice input and **not a model-diverse verdict**. This
report does not upgrade that characterisation.

`FABLE_DESIGN_EXPOSED = YES` for F4: Fable authored F4 in the Round-1 map and wrote the
reconstruction and the OD-1A..1D advice.

**No provenance gap.** Every artifact the brief listed was located and hash-pinned, and
none was altered.

---

## §9 Accounting

```
F4_PRIMARY_RETURN_TRIAL_CONSUMED = NO
F-RFR / F4 RETURN-FAMILY EXECUTION ROW WRITTEN = NO
TRIAL_LEDGER   read, NOT modified
EXPOSURE_LEDGER read, NOT modified
SAMPLE_REUSE   read, NOT modified
```

No trial family was declared for F4, nothing was executed, and no exposure row was
invented for reading public metadata.
