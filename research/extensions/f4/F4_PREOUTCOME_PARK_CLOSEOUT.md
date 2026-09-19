# CTA-EDGE-05 / F4 — PRE-OUTCOME PARK CLOSEOUT

```
RECORD_TYPE = CANDIDATE_PREOUTCOME_PARK_CLOSEOUT
CANDIDATE   = F4 INVENTORY_STATE_COMMODITY_CURVE (Fable Round-1 map, rank 5)
LINEAGE SLOT = CTA-EDGE-05 — S0 data-PIT feasibility only; no lineage sealed
DATE        = 2026-09-19
SCOPE       = DOCUMENTATION / GOVERNANCE ONLY. No retrieval, no sampling, no
              state, no basis, no return, no F4 run.
```

```
F4_FINAL_STATUS         = PARKED_PRE_OUTCOME
PARK_REASON             = LOAD_BEARING_NG_STATE_NOT_PIT_RECONSTRUCTIBLE

MECHANISM_FALSIFIED     = NO
PRIMARY_RETURN_CLAIM_TESTED = NO
PNL_FREE_PREMISE_TESTED = NO
RETURN_OUTCOME_ACCESSED = NO
PRIMARY_TRIAL_CONSUMED  = NO
```

---

## §1 Why PARK, and why the prior HOLD was the wrong disposition

The S0 PIT audit itself **executed successfully**. The park is not a failure of
the audit; it is the audit's own finding, correctly classified.

The prior task returned `HOLD` on the reasoning that no load-bearing series was
proven unreconstructible. That reasoning was **too narrow**: it classified each
series by whether its *level* could be recovered, and treated the missing
natural-gas reference as an open question rather than as the failure of the
state itself. Controller review corrects it, and the correction is right.

```
F4's inventory STATE is defined as:
    working-gas storage  RELATIVE TO  the source-defined same-week historical
    comparison.

The audit established:
    NG storage LEVEL, first published   PARTIALLY reconstructible, 2015-06-19+
    NG same-week historical comparison  NG_REFERENCE_PIT = E, NOT RECONSTRUCTIBLE
```

A level without its reference is not the state. Both routes to the reference are
closed and were verified closed:

* there is **no per-release historical vintage** of the WNGSR, so the published
  comparison cannot be read as-of;
* the revisions file carries **no revision-date field**, so the as-of history
  state underlying the comparison cannot be rebuilt — 56 of the 72 genuinely
  revised weeks carry no note at all.

Therefore the **load-bearing natural-gas inventory STATE cannot be constructed
under the already-accepted F4 definition, in any era.** Not "not yet"; not
"pending more work". Under the current definition and the current data
authority, it cannot be done.

Programme authority is explicit: **ENERGY is load-bearing and NG may not be
silently dropped.** Failure of a load-bearing family's PIT leg parks the
candidate pre-outcome. That rule is applied here rather than argued around.

---

## §2 What this is NOT

```
F4 falsified                        NO
inventory / storage theory falsified NO
trend conditionality falsified       NO
curve premise falsified              NO
negative return evidence             NO
evidence of any kind about F4's claim NO
```

**No F4 scientific outcome was ever exposed.** The primary contrast

```
Δ = E[future sign-aligned commodity trend return | TIGHT]
  − E[future sign-aligned commodity trend return | AMPLE]
```

was never computed, never estimated, never approximated and never previewed. No
TIGHT/AMPLE label exists. The PnL-free premise was never run.

The correct one-line status is:

```
DATA_PIT_ACCESS / RECONSTRUCTIBILITY NOT ESTABLISHED
FOR THE LOAD-BEARING NATURAL-GAS STATE.
```

A candidate parked for data reconstructibility has been told nothing about
whether its mechanism is true.

---

## §3 Audit findings preserved

All of these stand and are **not** invalidated by the park. Full detail in
[`F4_FROZEN_SAMPLE_EXECUTION.md`](F4_FROZEN_SAMPLE_EXECUTION.md) and
[`F4_PIT_FEASIBILITY_REPORT.md`](F4_PIT_FEASIBILITY_REPORT.md).

```
FROZEN AUDIT RULE   F4_METADATA_AUDIT_RULE.md
                    sha256 5c9c4289fe209c2d7a0a67036d7b02d246132ceda88b84ae5973ee2c63296a36
                    commit 4f448cb, frozen BEFORE any sampled retrieval and
                    verified byte-identical at the start and end of execution.
                    NOT modified by this closeout.

PETROLEUM 45/45     the frozen PINS sample executed in full: every landing page,
                    every highlights document, every parse, including the
                    2013-10-21 shutdown Monday and the 2025-12-29 Christmas
                    release. Archive is date-addressable; the directory name IS
                    the release date.

PETROLEUM METHODOLOGY BREAK
                    the same-week reference appears in all 45 vintages as TWO
                    DIFFERENT OBJECTS: 19 vintages 2012-05-02..2018-05-02 give a
                    banded "upper limit of the average range for this time of
                    year"; 26 vintages 2018-08-22..2026-06-24 give "N%
                    above/below the five year average", for crude, gasoline AND
                    distillate. 19 + 26 = 45, no mixed case. Transition
                    bracketed after 2018-05-02 and on or before 2018-08-22.

NG ORIGINAL SERIES  the revisions file is NOT a sparse revision log. It is a
                    COMPLETE consecutive weekly series of originally published
                    values: 565 rows, 565 distinct weeks, zero non-7-day steps,
                    zero duplicates, zero history weeks lacking an original. The
                    map week -> original is total and unique and needs no
                    judgment, and it is not a no-op: 72 of 565 weeks differ from
                    current. Originals begin 2015-06-19 (November 2015 is when
                    EIA began RELEASING the file; it back-fills to June).
                    Reconciliation holds under source semantics: residuals are
                    essentially all +/-1 Bcf, the signature of independent
                    rounding, with two non-rounding outliers (+4, -6) flagged
                    and NOT explained.

NG REFERENCE        NOT reconstructible, in every era. This is the park reason.

WASDE               sample NOT executed. This is a TRANSPORT LIMITATION on the
                    retrieval route available to this seat and is explicitly
                    NOT a demonstrated archive failure: the USDA archive holds
                    every release and its own date facet enumerates 629 release
                    months, 1973-09 .. 2026-09. What blocked execution was that
                    older per-release download URLs are JS-rendered and absent
                    from server HTML, the REST API offers no publication filter
                    over 1.54M releases, the paginated view caps near 2019, and
                    the legacy derivable path 404s. Only 54 of 194 in-window
                    months resolved a file path. NO PARTIAL SAMPLE WAS RUN,
                    because sampling whichever URLs happen to resolve is
                    sampling on retrievability.

MARKETING YEARS     resolved from USDA FAS: wheat and wheat products Jun 1 -
                    May 31; corn, sorghum, soybeans Sep 1 - Aug 31; soybean cake
                    and meal and soybean oil Oct 1 - Sep 30. Meal and oil run a
                    DIFFERENT marketing year from soybeans — a one-month offset
                    that products do not inherit from the bean.

DATABENTO PRESENCE  all 18 requested roots are ACTUALLY PRESENT, with expiration
                    metadata and settlement stat_type 3, across 5,031 definition
                    files. Verified by stride scan plus exact binary search; no
                    price or settlement VALUE was read and ohlcv was never
                    opened.

KE COVERAGE         Hard Red Winter appears only from 2013-12-15, consistent
                    with the KCBT contract's migration to CME Globex, so KE
                    contributes no overlap before that date. A second window
                    constraint, independent of natural gas.
```

No historical report was rewritten. The prior reports keep their original text
and carry additive superseding notes.

---

## §4 NO RESCUE — none of these is a continuation of F4

Explicitly **not authorized** as a continuation of this candidate:

```
dropping natural gas from the load-bearing energy family
petroleum-only energy
grains-only F4
replacing the EIA historical comparison with a researcher-chosen rolling norm
using revised CURRENT natural-gas history as if it were historical PIT state
choosing a post-2018 window merely to obtain the petroleum five-year reference
continuing with whichever series happen to be available
```

Each of those changes the object being tested. Any such proposal requires a
**NEW CANDIDATE with a NEW S0**, carrying its own material-redesign
adjudication — the same standard applied to F7, where pre-outcome timing was
held not to make a material change minor.

```
A REDESIGNED TRANSFORM IS NOT "REOPENING F4".
```

The temptation here is specific and worth naming: the audit produced a clean,
attractive fallback — build a five-year norm from first-published values, which
becomes computable around 2020-06. That is a **different object** from the
publisher's reference, it is exactly the arbitrary reference-length choice N-1
that the design deliberately avoided for energy, and adopting it silently would
convert a parked candidate into an unadjudicated redesign. It is recorded as
available and **not taken**.

---

## §5 Reopen condition

F4 reopens **as F4** only on:

```
a genuinely NEW, CONCRETE data authority that reconstructs the required natural-
gas historical comparison AS-OF each decision date
```

Concretely, that means one of: a per-release WNGSR vintage archive; a
publisher-supplied revision record carrying revision DATES sufficient to rebuild
the as-of history state; or an equivalent third-party archive of the published
comparison with verifiable provenance. A plausible-looking reconstruction is not
enough — the audit's standard was determinism without researcher judgment, and
that standard carries over.

Otherwise:

```
a SEPARATELY DECLARED, MATERIALLY REDESIGNED CANDIDATE with its own S0 authority
```

---

## §6 Trial and exposure accounting

```
F4 PRIMARY RETURN FAMILY   NEVER EXECUTED — never even declared
F4 RETURN OUTCOME          UNEXPOSED
PNL-FREE PREMISE           NEVER EXECUTED
PRIMARY TRIAL CONSUMED     NO
GOVERNED RETURN TRIALS     UNCHANGED
```

F4 never entered trial accounting at all: no `F-F4` family exists in the
`HYPOTHESIS_FAMILY` register, no `VARIANT_ATTEMPT` row exists, and none is
created here. `N_trials` on any sample is unchanged and `D-ETF-COUNT` remains
`UNKNOWN_PENDING_AARON_DECISION` — parking a candidate decides nothing about
counts.

**Input values read during the feasibility audit remain
`DESIGN_INFORMING_MEASUREMENT` only.** The audit read historical EIA
natural-gas storage values (the history and revisions files, 565 weeks) to test
whether first publication is mechanically recoverable. Those are **non-target
INPUT data**: they were never combined with any futures price, basis or return,
and no F4 quantity was formed from them. Every petroleum and WASDE document was
processed with all digits replaced at extraction, so no inventory level from
those sources entered the record at all.

That read is recorded as a `NO_OUTCOME` / `NONE` row in
`ops/EXPOSURE_LEDGER.md`, following the row-11 precedent for a non-target read
recorded "so the read is visible rather than implicit". It normalizes to `NONE`,
contributes **0**, and is **not** a return exposure.

```
NO RETURN EXPOSURE IS MANUFACTURED BY THIS CLOSEOUT.
```

---

## §7 Slot status

```
F4           PARKED PRE-OUTCOME / PIT RECONSTRUCTIBILITY
CTA-EDGE-05  UNASSIGNED after the F4 park
```

**No next candidate is selected or authorized by this document.** That is a
separate Owner decision, and this closeout does not anticipate it.
