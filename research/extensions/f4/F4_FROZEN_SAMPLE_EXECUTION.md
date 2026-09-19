# CTA-EDGE-05 / F4 — FROZEN-SAMPLE EXECUTION REPORT

```
RECORD_TYPE = FROZEN_SAMPLE_EXECUTION
LINEAGE     = CTA-EDGE-05 (F4 INVENTORY_STATE_COMMODITY_CURVE)
DATE        = 2026-09-19
RULE        = F4-AUDIT-RULE-1, UNCHANGED
              sha256 5c9c4289fe209c2d7a0a67036d7b02d246132ceda88b84ae5973ee2c63296a36
              commit 4f448cb — re-verified byte-identical at the start of this task
SCOPE       = input-data feasibility only. No F4 scientific outcome.
```

```
TASK_STATUS              = HOLD
LOAD_BEARING_F4_PIT_GATE = HOLD
```

Not PARK: natural gas **can** be reconstructed, deterministically, over a
defined span — so the controller's park trigger ("if NG cannot be reconstructed
at all") is **not** met. Not PASS: one load-bearing object is now shown to be
**not reconstructible at all**, and it is not the one anyone expected.

---

## §1 The finding that matters most

**EIA's own same-week five-year reference for natural gas cannot be
reconstructed as-of any historical release.** Not from an archive, and not by
recomputation.

```
NG_FIRST_PUBLICATION = PARTIALLY_RECONSTRUCTIBLE
NG_REFERENCE_PIT     = E   (NOT_RECONSTRUCTIBLE)
```

The two routes both close:

```
route (a) read it from the week-W vintage
          -> no per-release vintage archive exists for the WNGSR. Confirmed
             again this task: the report page and the schedule page link a
             current history file and a revisions file, never dated snapshots.

route (b) recompute it from the history as it stood at W
          -> requires knowing WHICH revisions had landed by W.
             The revisions file has NO revision-date column at all, and of the
             72 weeks that were actually revised, 56 carry no note whatsoever.
             The intermediate history states are therefore unrecoverable.
```

You know the **original** value and you know the **current** value. You do not
know *when* the change happened, so you cannot rebuild what EIA held on any
intermediate date — and EIA's published five-year average is a function of
exactly that.

This is the §8 distinction biting hard:

```
SOURCE_DEFINED_REFERENCE_EXISTS          = YES  (established previously)
HISTORICAL_REFERENCE_PIT_RECONSTRUCTIBLE = NO   for natural gas, in EVERY era
```

There is **no window** in which NG's source-defined norm is PIT-reconstructible.
A five-year reference built only from first-published values would become
computable from ~2020-06, but that is a **different object** from the
publisher's, and adopting it is an Owner design decision (N-1), not an audit
finding. **This audit does not adopt it.**

---

## §2 Natural gas — first publication IS deterministic, over a defined span

The previous task rated NG class **D** on the suspicion that reconstruction
would require inverting current history through a sparse revision record. That
suspicion was wrong, and the test says so.

The revisions file is **not** a list of revised weeks. It is a **complete,
consecutive weekly series of originally-published values**:

```
originals span          2015-06-19 .. 2026-04-10
rows                    565        distinct weeks 565        duplicates 0
non-7-day steps         0          <- no gaps anywhere in the span
history weeks in overlap 565
history weeks with NO original row   0   <- the "no-row" hazard does NOT arise
```

So within the span the map *week -> original value* is **total and unique**, and
recovery needs **no researcher judgment**: you read the row. And the
reconstruction is not a no-op — **72 of 565 weeks were genuinely revised** (69 of
them in the Lower-48 total), so ~12.7 % of weeks differ between first-published
and current.

```
NG_EARLIEST_VERIFIED_PIT_DATE = 2015-06-19
```

Three boundaries, all recorded rather than smoothed:

```
285 history weeks BEFORE 2015-06-19 (back to 2010-01-01) have NO original
 22 history weeks AFTER  2026-04-10 (to 2026-09-11) have no original row YET
  1 residual ambiguity: a week revised MORE THAN ONCE has only ONE row, and the
    file says it is "updated with the original estimate prior to the revision".
    Whether that row keeps the FIRST published value or the most recent
    pre-revision value cannot be determined from the file, because no duplicate
    rows exist to reveal it. This is why NG is class B and not class A.
```

**Reconciliation checks out under source semantics.** Region sums versus the
Lower-48 total, and Salt+NonSalt versus South Central, differ in about a third of
rows — but essentially all residuals are ±1 Bcf, the signature of independent
rounding to the nearest Bcf, not a definitional failure:

```
region sum - Total Lower 48   -2:2  -1:95  0:380  +1:86  +2:1  +4:1
Salt+NonSalt - South Central  -6:1  -1:74  0:414  +1:76
```

Two non-rounding outliers (+4 and −6) are **flagged, not explained** — they sit
near reclassification weeks, which is a hypothesis this audit did not test.

The documented **7 Bcf → 4 Bcf** threshold change (announced 2014-10-07,
implemented November 2015) is a methodology break under the frozen rule, and it
sits essentially at the start of the originals span.

```
NG_CLASS = B   (level, over 2015-06-19 .. 2026-04-10; class C before that)
```

---

## §3 Petroleum — the frozen 45 executed in full, and it found an era break

```
FROZEN_SAMPLE_FULLY_EXECUTED = YES   (45 / 45)
```

The sample was **reused verbatim** from `PINS_AUDIT_SAMPLE.json` — fixed
2026-09-16, in another lineage, before F4's S0 existed.

```
landing page exists      45 / 45
highlights.pdf exists    45 / 45
parsed                   45 / 45
missing dates            none
```

Every sampled vintage resolves at
`archive/{YYYY}/{YYYY_MM_DD}/pdf/highlights.pdf` — the **directory name is the
release date** — including the awkward ones the rule deliberately reaches for:
the 2013-10-21 government-shutdown Monday and the 2025-12-29 Christmas-week
release.

### 3.1 The era break

The publisher's same-week seasonal reference is present in **every** vintage —
but it is **two different objects**, and the partition is exact:

| era | dates | wording | crude | gasoline | distillate |
|---|---|---|---|---|---|
| 2012-05-02 → 2018-05-02 | **19** | *"in the upper limit of the **average range** for this time of year"* | — | — | — |
| 2018-08-22 → 2026-06-24 | **26** | *"are about N% above/below the **five year average** for this time of year"* | ✓ | ✓ | ✓ |

```
19 + 26 = 45.  No mixed case. No vintage carries both.
TRANSITION BRACKET = after 2018-05-02, on or before 2018-08-22
```

The earlier form is a **band position**, qualitative; the later form is a
**percentage deviation from a five-year average**, which is precisely the
OD-1D energy norm. They are not interchangeable, and a study that treats the
pre-2018 vintages as supplying the same quantity would be wrong.

```
PETROLEUM_REFERENCE_PIT = A from 2018-08 onward (read directly from the vintage,
                              for crude, gasoline AND distillate)
                          F before it — the five-year object is simply absent;
                              a DIFFERENT, banded object is published instead
```

### 3.2 A measurement error I made, corrected

The first pass reported `gasoline_ref = 0` and `distillate_ref = 1`. That was my
bug, not the source: digit redaction leaves the decimal point in
*"N.N million barrels"*, so a `[^.]` proximity gap could never span the
sentence. Re-measured with a bounded any-char gap, **all three products carry
the reference in all 26 post-2018 vintages**. The uncorrected figures are not
carried anywhere in this record.

```
CRUDE_CLASS      = A    WCESTUS1 — vintages 45/45, first publication established
                        for this exact series by CTA-EDGE-03-PINS from 2012-01-05
GASOLINE_CLASS   = B    WGTSTUS1 — same vintages, and the highlights name it
                        explicitly post-2018, but the first-published LEVEL sits
                        in the appendix tables, which this task did not open
DISTILLATE_CLASS = B    WDISTUS1 — as gasoline
PETROLEUM_PIT    = HOLD
```

An identity item still open: the dnav label says *"Commercial Crude Oil (Excl.
Lease Stock)"* while the report says *"excluding the Strategic Petroleum
Reserve"*. Both exclusions may hold, but equivalence is **not verified**.

---

## §4 WASDE — frame enumerable, sample NOT executed

```
WASDE_SAMPLE_FULLY_EXECUTED = NO
```

This is a **transport limitation on my side, not a defect in the USDA archive**,
and it is reported as such rather than dressed up.

What is established:

```
the archive's own date facet enumerates EVERY release month:
    629 months, 1973-09 .. 2026-09   (the "December 1973" figure quoted from a
    page summary in the previous task is superseded by this direct enumeration)
    191 months inside the A-3 window 2010-06 .. 2026-07
release clock attribute is uniformly 12:00 across the window
```

What blocked execution:

```
- the paginated publication view caps out around 2019-05 regardless of page
  depth, and pagination is 0-based (I initially walked it 1-based);
- for older releases the per-release download URLs are NOT in the server-
  rendered HTML — they are JS-rendered, so the date facet yields dates but not
  file paths;
- the ESMIS REST API exposes release files, but offers NO publication filter:
  /api/v1/release/findAll reports 1,541,971 releases site-wide and the
  publication/identifier parameters are ignored;
- the legacy derivable path usda.gov/oce/commodity/wasde/wasde{MMYY}.{pdf,txt}
  returns 404 for historical months.
```

**No partial sample was run.** The frozen rule exists to stop exactly that: had
I fetched the subset whose URLs happen to resolve, I would have sampled on
retrievability, which is the bias the freeze removes. Consistent with the
petroleum decision in the previous task, a stratified sample is executed or it
is not.

Structure therefore remains verified only on a **current** release (previous
task): the wheat-by-class table with explicit Hard Red Winter and Soft Red
Winter columns, the combined soybeans-and-products table with SOYBEAN MEAL and
SOYBEAN OIL sections, `Ending Stocks` rows, and `Use, Total` / `Total Use`
denominators whose label varies by table. Historical stability of those tables
is **unverified**.

```
ZC_CLASS = B   ZS_CLASS = B   ZW_CLASS = B   KE_CLASS = B
ZM_CLASS = B   ZL_CLASS = B
GRAINS_OILSEEDS_PIT = HOLD      GRAINS_FAMILY_PIT = HOLD
```

---

## §5 Marketing-year metadata — RESOLVED, and it contains a trap

From USDA Foreign Agricultural Service, *Commodity Marketing Years*, verbatim
rows:

```
June 1 - May 31        Barley, Flaxseed, Linseed Oil, Oats, Rye, Wheat,
                       Wheat Products
September 1 - August 31  Corn, Sorghum, Soybeans
October 1 - September 30 Cottonseed Cake and Meal, Cottonseed Oil,
                       Soybean Cake and Meal, Soybean Oil, Sunflower Seed Oil
```

```
MARKETING_YEAR_METADATA_RESOLVED = YES
  ZC corn      Sep 1 - Aug 31
  ZS soybeans  Sep 1 - Aug 31
  ZW / KE      Jun 1 - May 31   (also confirmed in-table: "Year begining June N")
  ZM meal      Oct 1 - Sep 30   <-- NOT the soybean year
  ZL oil       Oct 1 - Sep 30   <-- NOT the soybean year
```

**Soybean meal and oil run on a different marketing year from soybeans — one
month offset.** It would have been natural to assume products inherit the bean
year; they do not. Any old-crop/new-crop switch rule must treat ZM and ZL
separately from ZS.

No monthly state mapping was created.

---

## §6 Futures roots — requested vs actually present

Read from the frozen Databento corpus: instrument **definitions** only. No
price, no settlement value; `ohlcv-1d` was never opened.

Method: stride scan of every 21st definition file, then **exact binary search**
of each root's first and last appearance.

| root | requested | present | settlement field | expiry metadata | coverage |
|---|---|---|---|---|---|
| CL | ✓ | ✓ | ✓ | ✓ | 2010-06-06 .. 2026-06-30 |
| HO | ✓ | ✓ | ✓ | ✓ | 2010-06-06 .. 2026-06-30 |
| RB | ✓ | ✓ | ✓ | ✓ | 2010-06-06 .. 2026-06-30 |
| NG | ✓ | ✓ | ✓ | ✓ | 2010-06-06 .. 2026-06-30 |
| ZC | ✓ | ✓ | ✓ | ✓ | 2010-06-06 .. 2026-06-30 |
| ZS | ✓ | ✓ | ✓ | ✓ | 2010-06-06 .. 2026-06-30 |
| ZW | ✓ | ✓ | ✓ | ✓ | 2010-06-06 .. 2026-06-30 |
| ZM | ✓ | ✓ | ✓ | ✓ | 2010-06-06 .. 2026-06-30 |
| ZL | ✓ | ✓ | ✓ | ✓ | 2010-06-06 .. 2026-06-30 |
| **KE** | ✓ | ✓ | ✓ | ✓ | **2013-12-15** .. 2026-06-30 |

```
5,031 definition files scanned across 2010-06-06 .. 2026-06-30
expiration field present in every scanned file
settlement: stat_type codes 1..10 present, including 3 (settlement);
            NO settlement PRICE value was read
all 18 requested roots are ACTUALLY PRESENT
```

**KE is the exception and it is load-bearing.** Hard Red Winter wheat futures
appear only from **2013-12-15** — consistent with the KCBT contract's migration
to CME Globex — so KE contributes **no overlap** before that date. This is a
second window constraint, independent of natural gas.

---

## §7 Family gates and the window consequence

```
PETROLEUM_PIT        = HOLD
NATURAL_GAS_PIT      = HOLD
ENERGY_FAMILY_PIT    = HOLD
GRAINS_OILSEEDS_PIT  = HOLD
GRAINS_FAMILY_PIT    = HOLD
LOAD_BEARING_F4_PIT_GATE = HOLD
```

```
COMMON_WINDOW_CONSEQUENCE
  natural gas first-published values      from 2015-06-19
  natural gas originals currently end at       2026-04-10  (22 weeks uncovered)
  petroleum FIVE-YEAR reference form      from 2018-08 (bracketed, not exact)
  KE futures coverage                     from 2013-12-15
  futures panel                           2010-06-06 .. 2026-06-30

  If the source-defined five-year reference is required for petroleum and
  natural gas is retained, the binding start is the LATER of the NG originals
  and the petroleum reference era: ~2018-08, ending ~2026-04
  -> roughly SEVEN YEARS AND EIGHT MONTHS.

  But natural gas's own reference is NOT reconstructible in any era (§1), so on
  a strict reading of the source-defined norm there is NO window in which the
  energy family's state can be built as specified.
```

**This audit does not choose whether F4 should accept a shortened window, adopt
a proxy norm, or drop a leg.** Those are Owner decisions and they are named, not
taken.

```
ROOT_LEVEL_REDUCTION_OWNER_DECISION_REQUIRED = NO
```

No load-bearing root is class C or E on its **level**, so no root is failing
outright and none is being silently dropped. The live decisions are:

```
1. NG_REFERENCE_OWNER_DECISION_REQUIRED = YES
   EIA's published NG five-year reference is unreconstructible as-of. Accept a
   proxy norm built from first-published values (available ~2020-06, a
   different object), or drop natural gas from the load-bearing family — which
   WOULD be a root-level reduction and needs its own decision.
2. PETROLEUM_REFERENCE_ERA_OWNER_DECISION_REQUIRED = YES
   Start at ~2018-08 and use EIA's five-year form, or use the pre-2018 banded
   "average range" object, or construct a norm from vintages. Three different
   studies.
3. KE_WINDOW_OWNER_DECISION_REQUIRED = YES
   KE contributes nothing before 2013-12-15.
```

---

## §8 Firewall

```
INVENTORY_INPUT_VALUES_READ      = YES, and only where the frozen audit required it
FUTURES_TARGET_OUTCOME_ACCESSED  = NO
BASIS_COMPUTED                   = NO
TREND_RETURN_COMPUTED            = NO
F4_RETURN_OUTCOME_ACCESSED       = NO
F4_PRIMARY_TRIAL_CONSUMED        = NO
PNL_FREE_PREMISE_EXECUTED        = NO
TIGHT/AMPLE · z-score · stocks-to-use · norm length · correlation · Sharpe ·
X43 · backtest                   = none computed
```

Inventory input values were read in exactly one place: the **EIA natural-gas
history and revisions files**, to test whether first publication is
mechanically recoverable. That read is classified
`DESIGN_INFORMING_MEASUREMENT`. It was never combined with any futures price,
basis or return, and the record reports **counts, dates and determinism**, not
inventory levels.

Every petroleum and WASDE document was processed with **all digits replaced at
the point of extraction**, which is why quoted report wording appears as
*"N% above the five year average"*.

No exposure row is written: nothing here reveals an outcome or a measurement of
the F4 target, and the brief directs that a row must not be invented for reading
public metadata.

---

## §9 Choices still unbound

```
NUMERIC
  N-1  multi-year REFERENCE LENGTH where no source convention survives — now
       LARGER than before: it applies to grains, to natural gas in every era,
       and to petroleum before ~2018-08.
  N-2  DISPERSION WINDOW, only if the z-score form is kept.
  N-3  KILL BOUND of any PnL-free separability screen.
  N-4  S1 inference margins.

CATEGORICAL
  old-crop / new-crop switch rule (ZM and ZL on their OWN Oct-Sep year)
  stocks-to-use denominator label mapping across tables
  natural gas aggregation — Lower 48 total vs regional
  WCESTUS1 "Excl. Lease Stock" vs "excluding the SPR"
  F4 sample WINDOW START
  whether a first-published-only proxy norm may substitute for a publisher norm
```
