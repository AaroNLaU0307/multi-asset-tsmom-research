# CTA-EDGE-05 / F6 — S2 IMPLEMENTATION RECORD

```
STAGE                     = S2 BUILD
SEAL_ID                   = CTA-EDGE-05-F6-S1-2026-09-21
SEAL_COMMIT               = 0fd380682c6f0438c13ab25aa41c8fc9a3f5b70c
SEAL_INTEGRITY_VERIFIED   = YES   (29 / 29 pins reproduce)
BUILD_VALIDATION          = PASS
HISTORICAL_OUTCOME_RUN    = NOT_AUTHORIZED
S3_AUTHORIZATION_REQUIRED = YES
F6_PRIMARY_TRIAL_CONSUMED = NO
DATE                      = 2026-09-22
```

> **The engine is complete and it has never been run on F6.** Every numeric
> result in this build came from synthetic fixtures. No real SPY price value was
> read, no real return, `r_excess`, `r_net`, `beta_EVENT`, interval, Sharpe or
> LOYO quantity was computed, and no F6 result artifact exists.

---

## §1 Seal integrity

Before a line was written, every pinned authority was recomputed:

```
sealed manifest pins          29 / 29 reproduce
seal-record cross-checks      5 / 5 MATCH
seal validation               PASS
tree at the seal commit       clean
```

`f6_data.verify_seal_integrity()` re-checks the seven pins the engine actually
depends on at every run, strict by default. A mismatch **raises** and is never
repaired in code.

---

## §2 Module layout

Following the established BENB S2/S3 convention in this repository.

| module | stage | responsibility |
|---|---|---|
| `f6_contract.py` | A | the sealed contract as executable constants |
| `f6_authorization.py` | — | the production-run guard |
| `f6_data.py` | A·B·C | authority loading, input and manifest validation |
| `f6_engine.py` | D·E·F·G·I | returns, cash mapping, design, P1, P2, LOYO |
| `f6_inference.py` | H | the calendar-year block bootstrap |
| `f6_classify.py` | J | the sealed terminal table as code |
| `f6_report.py` | K | the S3 result schema |
| `f6_pipeline.py` | A–K | orchestration; `run_real` is the guarded entry point |
| `f6_fixtures.py` | test | deterministic synthetic fixtures |
| `f6_oracle.py` | test | the independent oracle |
| `f6_tests.py` | test | 114 checks |
| `f6_s2_build.py` | tool | build validation and manifest emission |

**Scientific definitions never mix with mutable defaults.** Every
promotion-relevant setting lives in `f6_contract` and is checked against the
sealed bytes by the test suite; `production_bootstrap()` takes no `b` argument
at all, so a test cannot quietly become the production path.

---

## §3 The historical-run guard

```
HISTORICAL_RUN_GUARD = PASS
```

**No new mechanism was invented.** The guard reuses the repository's existing
one: the append-only Owner ledger `ops/EXECUTION_AUTHORIZATIONS.md`, read from
**committed git state**, with the same fenced-`json` record shape and lifecycle
events that `x01_authorization.py` defines and `benb_authorization.py` scoped
for the previous lineage. Only the scope differs — `F6-AUTH`.

Two inherited asymmetries make it safe:

```
GRANTING requires committed state — a worktree edit cannot authorize a run.
BLOCKING requires nothing — unreadable ledger, missing ledger, no git, zero
grants or MORE THAN ONE live grant all REFUSE.
```

It satisfies the four required properties:

| property | how |
|---|---|
| deterministic | a pure function of the committed ledger blob |
| testable | 10 guard tests, including the refusal itself |
| fail-closed | every non-grant path raises `RunNotAuthorized` |
| unbypassable by an ordinary test command | `SYNTHETIC` is a *separate* `data_kind`, not a forged `REAL` grant; no fixture can mint one |

The guard is proven to be the **first statement** of both real paths
(`f6_data.load_price_values` and `f6_pipeline.run_real`) by AST inspection, not
by assertion. In `run_real` it fires before seal verification, before the
manifest is read and long before any price is parsed, so a refusal cannot leak
so much as a file handle on the outcome panel.

```
NO S3 AUTHORIZATION WAS CREATED BY THIS BUILD.
NO FAKE AUTHORIZATION EXISTS THAT PRODUCTION CODE WOULD LATER ACCEPT.
`f6_authorization.py` contains no function that can mint a grant, and a test
asserts that.
```

Probed live at build time: **0 active grants, real run refused.**

---

## §4 The firewall, enforced structurally

The package has two access tiers, and the split *is* the firewall:

```
METADATA TIER   schemas, column names, hashes, DATE INDICES, the event
                manifest, calendar metadata, the DGS3MO rate series.
                `panel_sessions()` reads usecols=["Date"] — no price byte is
                parsed at all.

VALUE TIER      `f6_data.load_price_values` is the ONLY function in the package
                that parses a real price, and its first statement is the guard.
```

Tests prove this by source inspection rather than by promise:

- `load_price_values` is the **only** function in `f6_data` whose body mentions
  the price column;
- `f6_engine`, `f6_inference`, `f6_classify`, `f6_fixtures` and `f6_oracle`
  contain **no** `read_csv` and **no** `open(` — they cannot reach a file;
- no test in the suite calls the real reader (checked by AST, because a
  substring check matched its own assertion text);
- `run_synthetic` references none of the sealed or real loaders.

---

## §5 What the tests establish

```
114 tests, 114 passing, 0 failing.
```

| group | count | what it pins |
|---|---|---|
| A seal integrity | 4 | contract constants re-derived from the sealed Markdown **and** the sealed manifest; the seed literal recomputed from its source string |
| B run guard | 10 | refusal, guard-is-first-statement, unreadable/absent/unparseable ledger, two live grants, worktree edits, no mint path |
| C firewall | 6 | the single-reader property, by AST |
| D event manifest | 6 | 462 / 471 / 9, reinstated PIT exclusion, 2026, tampered hash |
| E returns & cash | 7 | the golden case, normal publication, source-explained carry, unexplained gap, missing price |
| F opening boundary | 5 | 2011-01-03 from 2010-12-31, no prior-year row, no dropped row |
| G fixed P2 design | 11 | Friday unique reference, rank, rank-deficient STOP, per-year rank on the **real metadata** design |
| H P1 weighting | 3 | event-weighted, same-day overlap |
| I bootstrap | 10 | determinism, same draw for P1 and P2, repeated-year draw, duplication weights, quantile oracle, production `B` |
| J LOYO | 4 | 15 refits, sign pass, single-year failure, no deletion-level significance |
| K terminal classifier | 7 | exhaustive coverage against the oracle, P3 discipline, forbidden states |
| L end-to-end | 6 | synthetic branches |
| M mutation / anti-drift | 7 | seal-integrity, not numerical |
| N result schema | 6 | six layers, `NOT_RUN`, zero-placeholder refusal |
| O build status | 2 | S3 unauthorized, no result artifact |
| P branch coverage | 4 | all six P1×P2 cells, P3 discipline, the decoupling itself |

### §5.1 The golden test

`f6_oracle.py` **imports nothing from the production engine** and reaches every
expected value by a different route: returns as `(p_t − p_prev)/p_prev` rather
than `p_t/p_prev − 1`; `rf_hold` with the same three constants regrouped; P1 by
an explicit accumulate-and-divide loop; `beta_EVENT` by **Frisch–Waugh–Lovell**
partialling-out rather than solving the nine-column system; and the percentile
by a written-out interpolated order statistic.

The strongest route uses **no estimator at all**. Most fixtures build `r_excess`
as an *exactly linear* function of the sealed regressors with no error term, so
the true `beta_EVENT` is a constant chosen in the fixture file and OLS must
return it. Agreement there is a real check rather than two implementations
sharing a bug — which matters, because twice in this programme an oracle
reproduced the producer's own misreading and agreed with a wrong engine.

### §5.2 Two fixture defects found and fixed during the build

Both were mine, and both were caught by the per-year rank test rather than by
inspection:

```
1. On an unbroken business-day calendar, HOLD is EXACTLY 1 + 2*Monday, so it
   is a linear combination of the intercept and the Monday indicator. The
   fixture calendar now punches out holidays, as the real panel has.

2. An event every 5 business days always lands on the same weekday, making
   EVENT identical to one weekday indicator. The fixture spacing is now 6.
```

Neither is a property of F6: the real metadata design is full rank 9/9 pooled
and 9/9 in **every** individual calendar year, which `test_g07` verifies against
the actual event manifest, TOM authority and auction calendar — metadata only,
no prices.

### §5.3 Branch coverage, and how P1 and P2 were decoupled

All six P1×P2 cells are reached by real fixtures, not by stubbing the classifier.
The decoupling is the interesting part: a **uniform level shift applied to every
row** moves the P1 level but is absorbed by the intercept, leaving `beta_EVENT`
untouched, while `beta_event` moves the event rows relative to the controls and
so moves both. `test_p04` asserts exactly that invariant. The P1-unresolved cells
are self-calibrating — the fixture reads its own P1 point and translates it to
zero — rather than carrying a magic number.

---

## §6 Sealed settings, reproduced

```
event sample        462 sessions · FOMC 119 · CPI 176 · NFP 176 · 471 labels
                    · 9 overlaps · six PIT exclusions permanently absent
population          3772 rows, every 2011-2025 session, none dropped
opening boundary    2011-01-03 lagged from 2010-12-31, an INPUT only
weekday             REFERENCE = Friday; indicators Mon/Tue/Wed/Thu + intercept
cost                0.0004 round trip = 2 bps entry + 2 bps exit, P1 only
cash                DGS3MO/100 * HOLD/365, /365 OWNER-CHOSEN
bootstrap           15 blocks · B = 100000 · seed 2540719150 · same draw for
                    P1 and P2 · numpy.percentile(..., method="linear") at
                    [2.5, 97.5]
terminal            the sealed table, exhaustive, no LOW_POWER state
ceiling             T0_REUSED_DEPENDENT · SUPPORTED · no independent confirmation
```

**No scientific change was required or made.** Nothing in the implementation
conflicted with the seal, so no `HOLD_SEALED_SPEC_CONFLICT` arose.

---

## §7 Ledgers — deliberately untouched

```
TRIAL_LEDGER_CHANGED          = NO
F-F6 marked executed          = NO
EXPOSURE_LEDGER_CHANGED       = NO
PERFORMANCE_EXPOSURE_ADDED    = NO
F6_PRIMARY_TRIAL_CONSUMED     = NO
```

`F-F6` remains `SEALED / NOT EXECUTED`, exactly as the seal transaction left it.
**S2 implementation work is not a return attempt**, no outcome or measurement
has been revealed, and no new performance state was invented to describe a
build. The existing schema has no implementation/build lifecycle field, so none
was used and none was added.

---

## §8 The result schema, designed and empty

`f6_report.empty_result()` carries six separated layers — MEASUREMENT,
INFERENCE, GATE, TERMINAL VERDICT, CLAIM CAP, PROVENANCE — with every outcome
slot set to the string `NOT_RUN`.

```
A ZERO PLACEHOLDER IN A RETURN FIELD IS INDISTINGUISHABLE FROM A REAL ZERO
RESULT. `validate_result` REJECTS 0.0 IN AN UNRUN SLOT, AND `write_result`
REFUSES TO PERSIST AN INVALID DOCUMENT AT ALL.
```

It also rejects a document that contradicts the seal: a changed `B`, a changed
seed, a changed quantile implementation, an event count other than 462, an
evidence ceiling above `SUPPORTED`, `research_status = confirmed`, or a
forbidden terminal state.

---

## §9 No performance interpretation

```
NO ESTIMATE OF A LIKELY RESULT, EXPECTED SHARPE, EXPECTED RETURN, PROBABILITY
OF SUCCESS, OR WHETHER F6 WILL PASS APPEARS ANYWHERE IN THIS BUILD.
```

Every effect size in `f6_fixtures.py` is an arbitrary round number chosen to
exercise a code branch. None is fitted to, derived from, or inferred about the
actual F6 outcome, and the fixture file says so at the top. **S2 is engineering
acceptance only.**

---

## §10 Post-S2 state

```
S2_STATUS                = BUILD_COMPLETE
S3_RUN_AUTHORIZED        = NO
RETURN_REVEAL_AUTHORIZED = NO
```

The historical run remains forbidden until **all three** hold:

```
1. S2 implementation is complete          <- satisfied by this record
2. implementation acceptance passes       <- Aaron's judgment, not this build's
3. a SEPARATE S3 run authorization is issued by Aaron, as a committed
   F6-AUTH record in ops/EXECUTION_AUTHORIZATIONS.md
```

```
artifacts   F6_S2_BUILD_MANIFEST.json · F6_S2_BUILD_VALIDATION.json
seal        ../../../research/extensions/f6/F6_S1_PREREGISTRATION_SEALED.md
```
