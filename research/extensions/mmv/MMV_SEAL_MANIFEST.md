# CTA-EDGE-04-MMV — S1 SEAL MANIFEST

```
LINEAGE          = CTA-EDGE-04-MMV
CANDIDATE        = MACRO_MOMENTUM_VINTAGE  (Fable Round-1 discovery family F5)
STAGE            = S1 DESIGN + SEAL
SEAL_ID          = CTA-EDGE-04-MMV-SEAL-01
SEAL_DATE        = 2026-09-17
SEAL_STATUS      = SEALED
BRANCH           = cta-edge/macro-momentum-vintage-s0
PARENT_COMMIT    = 8a60a66795db9394af6d142df654cd6687a64bbb
```

```
CONTRACT         = MMV_PREREGISTRATION.md
CONTRACT_SHA256  = 4bad9f0bcdb7e4991ab920d12e24a60f4d237205e5a43af693a8dadadb56b225
PRE_SEAL_CHECK   = mmv_preseal_check.py  ->  38 / 38 PASS
```

---

## §1 Outcome-blindness attestation

```
HISTORICAL_MACRO_FEATURE_COMPUTED      = NO
HISTORICAL_MMV_COMPOSITE_COMPUTED      = NO
HISTORICAL_MMV_POSITIONS_COMPUTED      = NO
SEPARABILITY_RESULT_COMPUTED           = NO
GATE_05_AGREEMENT_RATE_COMPUTED        = NO
FIRST_RELEASE_DISAGREEMENT_COMPUTED    = NO
RETURN_OUTCOME_ACCESSED                = NO
SHARPE_OR_BOOTSTRAP_COMPUTED           = NO
BACKTEST_RUN                           = NO
```

Enforced mechanically, not asserted: check **D1** walks the lineage directory and fails
on any result-shaped artifact; **D2** AST-scans every `.py` in the lineage and fails if
any defines a feature, composite, position, agreement, Sharpe or bootstrap helper, or
imports the production engine or a numeric stack; **D3** verifies that the checker reads
only the `month_end` column of the canonical panel and never a canonical TSMOM sign
value; **D4** fails on any verdict asserted pre-outcome.

**No S3 authorization is requested by this seal.** No RNG seed is chosen.

---

## §2 The pre-seal adversarial check — 38 / 38

Reproduce with:

```bash
python research/extensions/mmv/mmv_preseal_check.py
```

### A — freeze integrity (9/9)

| id | what it falsifies |
|---|---|
| A1 | 18 series files + 1 manifest = **19** raw files |
| A2 | every frozen file present on disk |
| A3 | every recorded sha256 reproduces byte-for-byte |
| A4 | every recorded byte count reproduces |
| A5 | recorded coverage (rows, vintages, distinct reference dates, distinct realtime starts, first/last reference date, first/last vintage) **recomputes from the frozen bytes** for all 6 series |
| A6 | the fetcher `mmv_data_freeze.py` is tracked in git |
| A7 | `api_key` is `<REDACTED>` in every recorded request |
| A8 | no credential-shaped token (32-hex, or a literal `FRED_API_KEY` assignment) in any of the 351 tracked files |
| A9 | `data/mmv/` is untracked and credential patterns are in `.gitignore` |

### B — point-in-time / information concept (12/12)

| id | what it falsifies |
|---|---|
| B0 | **218** canonical decision dates, 2008-05-31 … 2026-06-30 |
| B1 | **INDPRO latest-known-as-of is valid**: an eligible vintage exists at all 218 dates and every as-of snapshot carries ≥ 13 reference months |
| B2 | **PAYEMS latest-known-as-of is valid**: same, ≥ 13 reference months |
| B3 | **CPILFENS PIT is valid**: same, ≥ 25 reference months (the transform needs two stacked 12-month changes) |
| B4 | **no final-revised leakage**: exhaustively over all 218 dates × all three ALFRED series, the as-of selector admits **no** observation whose `realtime_start` post-dates the decision date |
| B5 | every observations request used `output_type=1` (real-time period) — final-revised history was never requested |
| B6 | **CPILFENS missingness follows the sealed rule**: exactly one valueless reference date (2025-10-01), no other series has any, and the contract maps it to UNDEFINED — never zero, never imputed, never carried forward |
| B7 | **splice contiguous at 2008-12-16**: `DFEDTAR` ends 2008-12-15, `DFEDTARL`/`DFEDTARU` begin 2008-12-16, no gap and no overlap |
| B8 | **policy availability comes from the official announcement authority**: all 6 collisions pinned from the Federal Reserve's own statement pages, raw HTML hashes reproduce |
| B9 | **same-day FOMC handling is deterministic and conservative**: 4 collisions carry an official time and admit the new target; 2 carry none and retain the previous target by the rule's own fallback; an unestablished time is *never* treated as eligible |
| B10 | **ALFRED `realtime_start` is NOT the policy clock** — and the mismatch is quantified, not hidden |
| B11 | the 15:45 ET cutoff precedes the canonical decide-at-close / execute-next-session convention in `src/portfolio.py` |

### C — sealed definitions (12/12)

| id | what it falsifies |
|---|---|
| C1 | MMV-OD-1 … MMV-OD-6 all present and **no MMV-OD-7 exists** |
| C2 | the mapped set is **exactly** the canonical 17 minus `{VNQ, RWX}` — 15 instruments |
| C3 | VNQ/RWX are `NOT_MAPPED`, explicitly *not* "signal = 0", and enter **neither** the Gate-0.5 numerator **nor** its denominator |
| C4 | all 45 coefficients lie in `{-1, 0, +1}` — `NEW_TUNABLE_NUMERIC_PARAMETERS = NONE` |
| C5 | the growth truth table equals `sign(sign(a) + sign(b))` on all 9 states |
| C6 | all **27** `(G, I, P)` states enumerated; every algebraic identity the contract asserts holds — `FXY == −UUP`, `XLE == XLU == sign(G−P)`, `GLD == I`, `LQD == HYG == G`, `UUP == sign(I+P)` |
| C7 | **Gate 0.5 denominator and threshold exact**: kills at ≥ 80.0 % *inclusive* (80/100 kills, 799/1000 passes); 15 mapped instruments only; zeros counted on both sides; undefined excluded from both |
| C8 | transform locked to the 12-month change, sign only; no lookback/threshold/z-score/smoothing family; `m = 1` |
| C9 | M2 = lower 95 % bound of net Sharpe > +0.30 STRICT, declared MMV-specific; `EVIDENCE_CEILING = supported`, never `confirmed` |
| C10 | one inference framework: calendar-year block bootstrap, B = 10,000, 95 % percentile, one common set of year draws; HAC / Newey-West / second bootstrap forbidden |
| C11 | cost and every risk-wrapper parameter reproduce from canonical `config.py` |
| C12 | Fable recorded design-exposed and barred from blind certification; Astra's non-exposure recorded as an inference from absence; ETF sample recorded reused/burned; `D-ETF-COUNT` left open |

### D — outcome firewall (5/5)

See §1.

---

## §3 UNBOUND-4 — resolved by existing authority

```
UNBOUND_4_STATUS                            = RESOLVED_BY_EXISTING_AUTHORITY
NEW_SCIENTIFIC_CHOICE                       = NO
MMV_OD_7_CREATED                            = NO
MMV_OD_1_THROUGH_OD_6_REOPENED              = NO
FABLE_CONSULTED_ON_THIS                     = NO

POLICY_AVAILABILITY_AUTHORITY               = official FOMC / Federal Reserve
                                              announcement date and time
ALFRED_REALTIME_START_USED_FOR_AVAILABILITY = NO
OFFICIAL_FOMC_ANNOUNCEMENT_USED_FOR_AVAILABILITY = YES
```

The S1 freeze surfaced a mismatch in FRED/ALFRED policy metadata: `DFEDTAR` stamps
twenty-six years of history with a single `realtime_start = 2008-12-15` (its
discontinuation date), and `DFEDTARU` stamps 2014-04-03 on a target range that has been
public since 2008-12-16. I raised this as a candidate blocker. **The controller ruled
that it is not one**: policy availability was already bound, pre-outcome, by the
official announcement authority, so no new scientific choice was needed and none was
made.

Check **B10** quantifies what the rejected reading would have cost, so the finding sits
in the record rather than being absorbed silently: it would strand **71 of 218** decision
dates and, through the policy coefficient, **9 of the 15** mapped instruments — moving
the Gate-0.5 denominator for a reason with no macroeconomic content. The finding is
classified in the contract as a **FRED/ALFRED series-metadata limitation, not historical
public unavailability**, and §B.2 of the preregistration states it in full.

The S1 hold record is retained unedited (check **D5**), so the trail from discovery to
resolution is readable end to end.

---

## §4 Pinned artifacts — sha256

### 4.1 The contract and its lineage record

| sha256 | bytes | path |
|---|---:|---|
| `4bad9f0bcdb7e4991ab920d12e24a60f4d237205e5a43af693a8dadadb56b225` | 24299 | `research/extensions/mmv/MMV_PREREGISTRATION.md` |
| `c4d77a6b3f7699c588ac4df92e6767465310242bca5795f5e65bcdcffb010d0c` | 44018 | `research/extensions/mmv/MMV_S0_FRAME.md` |
| `08a245caaac543db6bbd2f4f50f47f1e8d50cb0196c5ec4f58e5200131556c35` | 4660 | `research/extensions/mmv/MMV_S0_AMENDMENT_01.md` |
| `5fde08d3c7ebf910aacb38a25bf8b848dc057309ee60d2120029ab8144efb391` | 26005 | `research/extensions/mmv/MMV_S1_HOLD_RECORD.md` |
| `5b4589db5f83076a6bea83816157e512404986b260080ad1b814efc7fdb3afeb` | 6930 | `research/extensions/mmv/MMV_RAW_DATA_MANIFEST.md` |
| `c19ad1cd53271b988840dbe31c81a346b282da26195b1d04f8f000ece7c4cbb3` | 21105 | `ops/OWNER_DECISION_RECORD_CTA_EDGE_04_MMV.md` |

### 4.2 Code

| sha256 | bytes | path |
|---|---:|---|
| `a7a211eed8c3a4075ba63463a1161cde6072057889a72ab7121b69707d106f3b` | 12961 | `research/extensions/mmv/mmv_data_freeze.py` |
| `fd4efc3e2ac828415a508160204f431761fe47345b674ace8150041648eca104` | 8072 | `research/extensions/mmv/mmv_fomc_timing_freeze.py` |
| `ab0eeb99c75c33ebc47fd7ab93833532cbac5f2f604716a52ca1043b89493fef` | 27756 | `research/extensions/mmv/mmv_preseal_check.py` |

### 4.3 Frozen macro data manifests (git-ignored payload, pinned by hash)

| sha256 | bytes | path |
|---|---:|---|
| `908e2d6deeceedf9d74f3cc684a5ab6b1224e5960887af082aba3329787706da` | 12348 | `data/mmv/MMV_RAW_MANIFEST.json` |
| `be6f17afdf77aafc7d44bee593a1a94a01bb9b9474112cd197e6ed177737c4f9` | 5139 | `data/mmv/MMV_FOMC_TIMING_MANIFEST.json` |

### 4.4 Frozen ALFRED observation payloads

| sha256 | bytes | path |
|---|---:|---|
| `3f53f959e399e21a060c6c7ab04392b82950c916826a1c964472d8c78682ddd9` | 3819154 | `data/mmv/INDPRO.observations.realtime.json` |
| `c773c5681807fe0057dd66814aa18bfc03b8c0201be57a50f425b48e7c471bd6` | 1321009 | `data/mmv/PAYEMS.observations.realtime.json` |
| `75c3c36306c109b11683d808471b30aa8061a2dfc0a4141a6668e6fe8b9ad2f4` | 81468 | `data/mmv/CPILFENS.observations.realtime.json` |
| `bfaca909a51796fe61942aa6cf218b12f696d824f0d64712dab3c947ed71c50f` | 902294 | `data/mmv/DFEDTAR.observations.realtime.json` |
| `a1096b552be2059a53e3864e20c16e3c0c61b714f7f601b6fe1e0f5dd29d5925` | 1794597 | `data/mmv/DFEDTARL.observations.realtime.json` |
| `36bbfb3efc9b8e82db415af0ddd74ae6544a74253ed8c82831b51de6396197e4` | 1547984 | `data/mmv/DFEDTARU.observations.realtime.json` |

The 12 companion files (`*.series.json`, `*.vintagedates.json`) are pinned inside
`MMV_RAW_MANIFEST.json`, whose own hash is pinned above. Checks A1–A5 verify all 18.

### 4.5 Canonical repository authority (read-only, unmodified)

| sha256 | bytes | path |
|---|---:|---|
| `fa154e01ec597070729b5489ee4f8ed0e588add30c70d33196d7bf3c8069173f` | 26641 | `output/monthly_signal_panel.csv` |
| `3d2a7a56dbd92d4ff8138cfd894c87f5ac5ac088a11165db870673e0c05c3c31` | 3298252 | `data/close_prices_raw.csv` |
| `6c2d9820963cb5cc0bd1991b4697417d755333fc87f73081eaf403e45cba258f` | 21982 | `config.py` |
| `aa06eb1c5fcd69be57f911fab21b76e299f5e71ee727fd27aa138ddf52aa4479` | 13146 | `src/portfolio.py` |
| `8f10675033267136cb2622bf80f2f6da8ca922c0e074fae4c09128a49b1c4789` | 90832 | `research/extensions/ta/TA_MACRO_CALENDAR.csv` |

`TA_MACRO_CALENDAR.csv` is **reused from CTA-EDGE-01-TA, not refetched**; it supplied the
171 FOMC announcement dates whose intersection with the canonical month-ends produced the
six collisions.

### 4.6 Discovery origin

```
Quant trade/2026-09-15-cta-edge-discovery-r1-mechanism-feature-map-fable-01.md
sha256 02ca5f45fe41763e55a353090645c3b2a98b6dcf5fce572623ede604e569344a
family F5, MACRO_MOMENTUM_VINTAGE
```

---

## §5 What this seal does and does not authorize

```
AUTHORIZES     S2 BUILD of the sealed contract, SYNTHETIC ONLY.

DOES NOT AUTHORIZE
  any historical MMV signal, composite or position
  any Gate 0.5 evaluation on historical data
  any return, Sharpe, bootstrap or interval
  the first-release concordance cell (post-seal, pre-return, but still an
    Owner-gated historical computation)
  any S3 run, any RNG seed, any reveal
  git push, PR, or merge
```

S2 implements this contract and **makes no scientific choice**. Any question S2 cannot
answer from the contract alone is an Owner decision, not a builder decision.

```
EVIDENCE_CEILING = supported
```
