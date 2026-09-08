# DATABENTO_W1_INPUT_VERIFICATION.md — TSMOM-EXT-001

**Wave:** 1 · **Lane:** MEASUREMENT · **Stage:** C/D
**Created:** 2026-09-07 (Wave-1 execution, under Aaron's
`AUTHORIZE_WAVE_1_RESEARCH_EXECUTION_WITH_GATES`)
**Purpose:** the bounded input verification Wave 0 deliberately left open, run
before any dependent X02/X03 computation (Wave-1 prompt §4).
**Producer:** `research/extensions/wave1/probe_databento.py`
**Machine-readable output:** `research/extensions/wave1/databento_probe.json`

**Scope limit, binding.** Metadata, identity, coverage, units and roll-relevant
availability only. **No strategy return, no PnL, no Sharpe, no performance
comparison was computed, and no protected outcome was inspected.** Everything
read lies inside the declared frozen snapshot boundary. **This is not a data
purchase**; only existing local bytes were read.

---

## §1 Dataset and file identity — VERIFIED

| Item | Verified value | Source |
|---|---|---|
| Corpus root | `C:\Users\Aaron\quant-data\commodity-carry` | directory read |
| `ohlcv-1d.dbn.zst` size | **107,229,003 bytes** | filesystem |
| `ohlcv-1d.dbn.zst` SHA-256 | **`333095164e55c73a150949b654a0e4c9f15636cc01ee7c93bf625e5412c59539`** | recomputed here |
| Manifest agreement | **MATCH** — identical size and hash to `commodity-carry-research/data/MANIFEST.md` | manifest |
| Dataset | `GLBX.MDP3` | DBN metadata |
| Schema | `ohlcv-1d` | DBN metadata |
| `stype_in` / `stype_out` | `parent` / `instrument_id` | DBN metadata |
| Requested window | `2010-06-06T00:00:00Z` → `2026-07-01T00:00:00Z` (**end exclusive**) | DBN metadata |
| Parent symbols | **18**, exactly the pre-registered roots as `<ROOT>.FUT` | DBN metadata |
| `statistics` delivery | 5,026 files, `glbx-mdp3-20100606` → `glbx-mdp3-20260630` | directory read |
| `definition` delivery | 5,031 files, `glbx-mdp3-20100606` → `glbx-mdp3-20260630` | directory read |

**Per-file SHA-256 re-verification of all 10,058 delivered files was NOT run**
(Wave-0 `U8`). The `ohlcv-1d` file *was* hashed and matches. The aggregate
manifest hashes remain the record for the two partitioned schemas. This is a
recorded scope limit, unchanged, not a new finding.

---

## §2 The June-30 / July-1 boundary ambiguity — **RESOLVED**

Wave 0 carried this as an open ambiguity: the carry manifest records an
**exclusive** request end of `2026-07-01`, while `mean-reversion-research`'s
`protocol/SAMPLE_REUSE.md` KB-1a states that "the local `ohlcv-1d` extract runs
one session further, to 2026-07-01".

**Verified from the delivered bytes:**

| Fact | Value |
|---|---|
| Distinct session dates in `ohlcv-1d` | **4,993** |
| First session | **2010-06-06** |
| **Last session** | **2026-06-30** |
| Records dated 2026-07-01 | **none** |
| Last `statistics` file | `glbx-mdp3-20260630.statistics.dbn.zst` |
| Last `definition` file | `glbx-mdp3-20260630.definition.dbn.zst` |

**Resolution.** The request end `2026-07-01` is **exclusive**, and the delivered
data ends at **2026-06-30 inclusive**, consistently across all three schemas.
There is no 2026-07-01 session in this corpus. The MR note's "one session
further" reading is **not confirmed for `ohlcv-1d`** and should not be relied on;
MR's own conservative treatment (counting any such session as inside the burn)
remains safe because the session does not exist.

**Consequence.** The Databento frozen boundary is **2026-06-30**, matching
`commodity-carry-research/src/config.py` `SAMPLE_END = "2026-06-30"`. No
adjustment to the lockbox procedure's §2.2 boundary is needed.

---

## §3 Instrument composition — **79% of the delivery is calendar spreads**

This is the most consequential structural finding, and it was not previously
recorded anywhere in this program.

| Class | Records | Share |
|---|---|---|
| **Calendar / inter-commodity spreads** (e.g. `CLZ5-CLM6`, `RBQ6-HOQ6`) | **3,563,342** | **79.1%** |
| **Outright contracts** (e.g. `CLZ5`) | **941,928** | 20.9% |
| Unclassified | **0** | 0% |
| **Total** | **4,505,270** | 100% |

A `parent` (`.FUT`) pull returns every instrument under the parent, spreads
included. **Any roll, chained index or dollar ledger built over this delivery
without first excluding spreads would be silently and badly wrong** — spreads
carry small, frequently negative prices and their own instrument ids.

**Recorded as an X02a construction requirement:** outright-only filtering is a
precondition of every futures price path in this program, and the filter must be
positive (root + month code + year), not merely "reject symbols containing `-`".

**Method note, recorded because it changes what may be trusted.** A first version
of the probe inverted `metadata.mappings` by hand and produced results that were
obviously wrong (CL with 7 outright contracts; GC/SI/HG/PL/PA absent entirely;
negative settlements in the "outright" bucket). That version was **discarded**,
not patched, and the numbers above come from the vendor's own
`DBNStore.to_df(map_symbols=True)`. Nothing in this file derives from the
hand-rolled mapping.

---

## §4 Per-root coverage — all 18 roots present and VERIFIED

Outright contracts only; spreads excluded.

| Root | Records | Distinct raw symbols (**not** contracts — see §4A) | First | Last | Settle min | Settle max |
|---|---|---|---|---|---|---|
| CL | 107,977 | 136 | 2010-06-06 | 2026-06-30 | 9.0600 | 126.9900 |
| HO | 79,830 | 120 | 2010-06-06 | 2026-06-30 | 0.6170 | 4.9440 |
| RB | 64,075 | 120 | 2010-06-06 | 2026-06-30 | 0.4400 | 4.3150 |
| NG | 134,319 | 208 | 2010-06-06 | 2026-06-30 | 1.4410 | 10.0130 |
| GC | 52,279 | 120 | 2010-06-06 | 2026-06-30 | 1050.4000 | 5957.7000 |
| SI | 39,190 | 120 | 2010-06-06 | 2026-06-30 | 11.8500 | 127.1000 |
| HG | 56,606 | 120 | 2010-06-06 | 2026-06-30 | 1.9365 | 7.0815 |
| PL | 21,363 | 120 | 2010-06-06 | 2026-06-30 | 595.1000 | 2806.5000 |
| PA | 14,214 | 106 | 2010-06-06 | 2026-06-30 | 423.0000 | 3289.0000 |
| ZC | 49,039 | 50 | 2010-06-06 | 2026-06-30 | 301.5000 | 837.7500 |
| ZS | 50,491 | 70 | 2010-06-06 | 2026-06-30 | 786.5000 | 1770.0000 |
| ZW | 38,319 | 50 | 2010-06-06 | 2026-06-30 | 362.7500 | 1311.2500 |
| ZM | 51,943 | 80 | 2010-06-06 | 2026-06-30 | 249.0000 | 550.0000 |
| ZL | 50,246 | 80 | 2010-06-06 | 2026-06-30 | 25.0200 | 90.5600 |
| KE | 24,367 | 50 | **2013-12-16** | 2026-06-30 | 361.7500 | 1370.0000 |
| LE | 35,036 | 60 | 2010-06-07 | 2026-06-30 | 79.8500 | 258.4750 |
| HE | 41,205 | 80 | 2010-06-07 | 2026-06-30 | 37.2750 | 133.8750 |
| GF | 31,429 | 80 | 2010-06-07 | 2026-06-30 | 106.5000 | 381.9500 |

### §4A CORRECTION — the count column is raw symbols, not contracts

**Appended 2026-09-07, same session, after the X02a attempt exposed it.** The
column originally read "Outright contracts". It counts **distinct raw symbols**,
and CME parent symbology uses a **1-digit year that repeats every 10 years**, so
over a 16-year panel one symbol denotes two contracts. The column therefore
**undercounts** true contracts and must not be read as a contract census.

Everything else in §4 stands: record counts, first/last dates, settlement ranges,
and the zero/negative-settlement counts are all per-record and unaffected by
keying.

The same defect invalidated the X02a and X03 panels —
see `FUTURES_INFRA_TRUTH.md` §2, where it is diagnosed in full.

**Cross-checks against the carry configuration, all VERIFIED:**

- **KE first observed 2013-12-16** — exactly `carry_cfg.KE_ENTRY_DATE`. The
  symbol-entry rule is confirmed against delivered data, not assumed.
- **LE / HE / GF first observed 2010-06-07**, one session later than the other
  14 roots — exactly the basis for `SAMPLE_START = "2010-06-07"` ("the later of
  the two dataset-floor dates").
- Zero settlements: **0** across all roots. Negative settlements: **1**, in CL —
  the April-2020 negative WTI print, a real market event, not a data defect.

---

## §5 Price units — the 100× divisor defect, **IDENTIFIED FROM DATA**

MAP_v2 asserts a "100× defect on the 8 cents-quoted roots" and requires the
divisor to be applied at the cost boundary. **The carry repository contains no
divisor**: a source scan of `commodity-carry-research/src/*.py` finds no
`divisor`, no `price_unit`, and no `/100` in the cost path.
`costs.cost_per_side_pct` computes `usd / (settle_price * multiplier)` directly.

The observed settlement ranges above determine the quotation unit unambiguously,
and they identify **exactly eight** cents-quoted roots:

| Root | Observed range | Implied quotation | Sanity | **Divisor** |
|---|---|---|---|---|
| **ZC** | 301.5 – 837.75 | cents / bushel | corn $3.02–$8.38/bu | **100** |
| **ZS** | 786.5 – 1770.0 | cents / bushel | soybeans $7.87–$17.70/bu | **100** |
| **ZW** | 362.75 – 1311.25 | cents / bushel | wheat $3.63–$13.11/bu | **100** |
| **KE** | 361.75 – 1370.0 | cents / bushel | KC wheat $3.62–$13.70/bu | **100** |
| **ZL** | 25.02 – 90.56 | cents / lb | soybean oil $0.25–$0.91/lb | **100** |
| **LE** | 79.85 – 258.475 | cents / lb | live cattle $0.80–$2.58/lb | **100** |
| **HE** | 37.275 – 133.875 | cents / lb | lean hogs $0.37–$1.34/lb | **100** |
| **GF** | 106.5 – 381.95 | cents / lb | feeder cattle $1.07–$3.82/lb | **100** |
| CL, HO, RB, NG, GC, SI, HG, PL, PA, ZM | see §4 | decimal dollars | all plausible | **1** |

**ZM is decimal dollars, not cents** ($249–$550 per short ton), so it is *not* one
of the eight despite being a grain — a distinction worth stating, because
"all grains are cents-quoted" is the natural and wrong assumption.

**Independent confirmation from the spec table.** `CONTRACT_SPECS` is internally
consistent in **decimal dollars**: `tick_size × multiplier == tick_value` holds
for all 18 roots (e.g. ZC `0.0025 × 5000 = 12.50`). A cents-quoted price fed into
`settle_price * multiplier` therefore overstates contract notional by exactly
100×, and understates `cost_per_side_pct` by 100×, for the eight roots above.

**Binding consequence for X02a.** Every dollar-notional or cost computation in
this program must apply `settle_price / DIVISOR[root]` at the boundary.
`DIVISOR = 100` for `{ZC, ZS, ZW, KE, ZL, LE, HE, GF}` and `1` otherwise. This is
a fact about the data and the spec table, established here from bytes; it is
**not** a change to the carry repository, which is not modified by this program.

---

## §6 Roll-relevant availability — VERIFIED

The A1 roll rule is **open-interest-max at `t−1`**, so open interest is a hard
input, not a nicety.

| Item | Verified |
|---|---|
| Open interest present | **Yes** — `statistics` schema, `stat_type = 9` (`OPEN_INTEREST`), ~838 records/session |
| Settlement present | **Yes** — `statistics` schema, `stat_type = 3` (`SETTLEMENT_PRICE`), ~21,079 records/session |
| Cleared volume | present (`stat_type = 6`) |
| Coverage | 5,026 daily files, 2010-06-06 → 2026-06-30 |
| Null sentinel | `quantity = 2147483647` marks an absent quantity and **must** be dropped, not read as ~2.1 billion contracts |

Settlement — not the `ohlcv-1d` close — is the correct mark for a futures dollar
ledger, and it is what the carry construction uses. The extraction that feeds
X02a/X03 therefore reads the `statistics` schema and applies the outright-only
filter of §3.

---

## §7 Prior research exposure on this sample — unchanged, restated

| Fact | Status |
|---|---|
| Burned by | `strat.commodity-carry.xs-ts-carry-premium`, `N_trials = 14` **frozen** |
| Also consumed by | `c1-drag-audit` (cost accounting only; ledger deliberately not extended) |
| Also declared against by | `mean-reversion-research` (separate alpha family; strict-subset roots, identical period, same bytes) |
| TSMOM-EXT contribution to date | **0** — no TSMOM constructed strategy-return series exists on this panel |
| Authoritative dataset-level record | `commodity-carry-research/preregistration/PREREGISTRATION.md` §10 + `src/config.py:66` |

Nothing in this verification created a strategy-return series, so **nothing here
moves `N_trials`**. See `research/extensions/TRIAL_LEDGER.md` §3.1.

---

## §8 Verdict

`DATABENTO_W1_INPUT_VERIFICATION = PASS (with a third construction requirement added below)`

**The vendor data is sufficient** in identity, coverage, units and roll inputs.
The defect found downstream is in **this program's panel construction**, not in
the delivered data.

Three construction requirements, all binding on any futures price path here:

1. **Outright-only filtering** (§3) — 79% of the delivery is spreads.
2. **Price-unit divisor** (§5) — 100 for the eight cents-quoted roots.
3. **Key contracts by `(instrument_id, expiration)`, never by raw symbol**
   (§4A) — **added after this document's first version**, when a raw-symbol
   keying collapsed two listing cycles into one column and produced a degenerate
   roll series. See `FUTURES_INFRA_TRUTH.md` §2.

**Facts left `UNKNOWN`, unchanged:** per-file SHA-256 of the 10,058 delivered
files (Wave-0 `U8`); exposure status of any data after the 2026-06-30 boundary
(Wave-0 `U1`). Neither blocks X02a/X03; `U8` is owed before any *promotion*
resting on this panel.

---

## §9 Append log

| Date (UTC) | Appended | By |
|---|---|---|
| 2026-09-07 | Created at Wave-1 execution. Identity §1; June-30/July-1 boundary **resolved** §2; spread composition §3; per-root coverage §4; **price-unit divisor identified from data** §5; roll inputs §6; exposure restatement §7; verdict PASS §8. | Wave-1 session (Claude Opus 5) |
| 2026-09-07 | **CORRECTION §4A appended**, same session: the §4 count column is distinct **raw symbols**, not contracts, because the 1-digit year repeats every 10 years. §8 gains a **third construction requirement** — key contracts by `(instrument_id, expiration)`. No coverage, range, hash or boundary finding changed; the correction is to a column label and to the completeness of the construction requirements. | Wave-1 session (Claude Opus 5) |
