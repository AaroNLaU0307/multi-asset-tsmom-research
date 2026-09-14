# CTA-EDGE-01-TA — MACRO / QRA COVARIATE CROSS-TABULATION

```
LINEAGE                 = CTA-EDGE-01-TA
SEALED_PREREG_SHA256    = 3b495fcb220a86b9c4226e308e4814bdfdd871d1c69ce352e99b78977436d35b
STAGE                   = S2, produced BEFORE any AC exists
CONTAINS_RETURNS        = NO   (every number below is a COUNT)
GENERATED_UTC           = 2026-09-14T17:51:47Z
```

The sealed contract §G.3 requires this table to be reported **before any `AC`
is computed**, so that Class-D reachability is known to the Owner while the
lineage is still outcome-blind. Covariates are the sealed signed form:
`+1` a release on a POST return-bearing day, `-1` on a PRE one, `0` otherwise.

Events: **213** primary windows (2006-02-09 … 2026-05-13).

| covariate | POST `+1` | neither `0` | PRE `-1` |
|---|---:|---:|---:|
| **CPI** | 125 | 57 | 31 |
| **NFP** | 8 | 27 | 178 |
| **FOMC** | 52 | 145 | 16 |
| **QRA** | 0 | 207 | 6 |

## Combination counts (CPI, NFP, FOMC, QRA)

| combination | events |
|---|---:|
| `1,-1,0,0` | 73 |
| `0,-1,0,0` | 33 |
| `1,-1,1,0` | 22 |
| `-1,-1,0,0` | 14 |
| `-1,-1,1,0` | 10 |
| `1,-1,-1,0` | 8 |
| `1,0,0,0` | 8 |
| `0,-1,1,0` | 8 |
| `0,0,0,0` | 7 |
| `0,0,1,0` | 5 |
| `1,0,1,0` | 4 |
| `1,1,0,0` | 4 |
| `-1,-1,-1,0` | 3 |
| `0,1,0,0` | 2 |
| `1,-1,1,-1` | 2 |

Distinct combinations observed: **23**.

## The sealed evaluability test

```
DESIGN_MATRIX_COLUMNS   = 5
DESIGN_MATRIX_RANK      = 5
REFERENCE_GROUP_N       = 7   (events with all four signed covariates = 0)
MIN_REFERENCE_GROUP     = 20
MACRO_SPEC_EVALUABLE    = NO
NOT_EVALUABLE_REASONS   = ['REFERENCE_GROUP_TOO_SMALL (7 < 20)']
```

> **The sealed §G.3 diagnostic is mechanically `NOT_EVALUABLE`, and this was
> established from the CALENDAR ALONE, with no return in existence.** Under the
> sealed rule `NOT_EVALUABLE` makes the macro/QRA damage diagnostic TRIGGER,
> so a would-be Class D becomes **Class I**. The specification is **not**
> redesigned and the seal is **not** amended: the S1 contract disclosed this
> exact risk and required this exact pre-check, and the pre-check has fired.

The finding is itself the substantive result of the pre-check: at daily
close-to-close frequency the mid-month refunding week is almost never
macro-clean, which is precisely why the intraday literature had to go
intraday to identify the effect.

