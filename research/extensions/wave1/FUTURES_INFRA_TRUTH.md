# FUTURES_INFRA_TRUTH.md — X02a and X03 (structural)

**Program:** TSMOM-EXT-001 · **Wave:** 1 · **Lane:** MEASUREMENT · **Stage:** C/D
**Created:** 2026-09-07 · **Repaired:** 2026-09-08 (bounded contract-identity repair)
**Definitions:** `TSMOM_EXTENSION_RESEARCH_MAP_v2.md` Cluster C1 §X02, §X03

```
PANEL_SANITY                  = PASS   (10/10 checks)
GROSS_LEDGER_RECONCILIATION   = PASS   (ALGEBRAIC TAUTOLOGY - not evidence of accounting validity)
TSMOM_PRODUCTION_CASH_ACCOUNTING = PASS   (production synthetic CL roll cost = $25.00)
ONE_CONTRACT_CASH_LEDGER      = PASS   (independent oracle; 23.863636 rejected)
NET_CASH_LEDGER_RECONCILIATION = PASS   (roll days 1.18e-17, non-roll 4.18e-17)
EVENT_SEMANTICS               = PASS   (cost charged on rolls only, both legs)
COST_PATH_PRODUCTION          = PASS   (divisor binds via the denominator)
NET_LEDGER_INDEPENDENCE       = MEANINGFUL (mutations A-D all DETECTED)
LEGACY_CARRY_PERCENTAGE_CONVENTION != AUTHORITATIVE_TSMOM_CASH_LEDGER
COST_PATH_END_TO_END          = PASS   (fails if the divisor is removed - verified by sabotage)
SIGN_AGREEMENT_DIAGNOSTIC     = COMPUTED
X02_BUILDER_STATUS            = COMPLETE_PENDING_INDEPENDENT_VERIFICATION
X03_BUILDER_STATUS            = COMPLETE_PENDING_INDEPENDENT_VERIFICATION
ROLL_RULE_DOF                 = REQUIRED (governance declaration)
ROLL_RULE_ECONOMIC_MATERIALITY = UNRESOLVED
```

**Status wording, deliberately.** The prior revision said `X02_STATUS = COMPLETE`
and marked X01 preconditions 1-2 `MET`. Fable found both **overclaimed**: the
costed reconciliation was untested, the chained path inherited the unit defect,
and a MAP_v2 X02a component was silently deferred. Those defects are now
repaired, but **this session produced the repair and cannot certify it**. The
repository has no legal intermediate status enum, so the builder-side status is
carried in prose as `COMPLETE_PENDING_INDEPENDENT_VERIFICATION` and the X01
preconditions stay **PENDING**, not MET.

**No strategy performance was computed.** No Sharpe, no portfolio return, no
wrapper comparison, no candidate selection, no roll-rule selection on
performance. `X01` remains unsealed and unrun.

**Producers:** `extract_contracts_v2.py` · `panel_sanity.py` · **`run_x02a_v3.py`** ·
**`run_x03_structural_v3.py`** (v2 modules retained as lineage)
**Machine-readable:** `extract_v2_meta.json` · `panel_sanity.json` ·
**`x02a_v3_results.json`** · **`x03_structural_v3.json`**

---

## §1 The defect that caused the first attempt to fail (retained lineage)

The first attempt keyed contract panels by **raw CME symbol**. Parent symbology
uses a one-digit year that repeats every 10 years, so over a 16-year panel one
symbol denotes **two contracts** and the column merged them.

Verified evidence, retained:

| Symbol | Observations | First | Last | Gaps > 400 days |
|---|---|---|---|---|
| `GCM1` | 2,502 | 2010-06-06 | 2026-06-30 | **2** |
| `GCZ0` | 2,474 | 2010-06-06 | 2026-06-30 | **2** |
| `CLZ5` | 4,416 | 2010-06-06 | 2025-11-20 | **0** |

A gold June contract trades ~2 years, not 16. `CLZ5` is worse — crude's listing
horizon makes the 2015 and 2025 cycles **overlap continuously**, so the
collision left **no gap** and was invisible to any gap-based check.

**How it surfaced, and why the identity check did not catch it.** The
reconciliation identity `pnl_usd == notional_{t−1} × r_gross` passed at
**1.21e-16** on those panels. It is **algebraic** — it holds for any numbers,
including nonsense — so it was **vacuously satisfied**. What actually surfaced
the defect was an absurd roll series: GC rolling **3 times in 16 years** and
held-contract settlement availability of **44–63%**.

**This was avoidable.** `commodity-carry-research/src/pipeline.py`'s
`build_outright_panel()` docstring states its key is instrument_id + expiration,
"not raw_symbol-prefixed … for why raw_symbol was dropped from the key". That
comment was read during the session and not acted on.

**Lineage preservation.** `run_x02a.py`, `run_x03_structural.py`,
`extract_settle_oi.py`, `settle_panel.parquet`, `oi_panel.parquet`,
`x02a_results.json` and `x03_structural.json` are **retained, not deleted**, and
are declared in the validator registry as superseded. Exposure ledger row 17
records the invalid attempt. **It is implementation-error history, not a
strategy trial**, and contributes nothing to `N_trials`.

---

## §2 Persistent contract identity — adopted, not invented

The carry study had already solved this. Its method is adopted in substance:

```
_contract_key = str(instrument_id) + "__" + expiration.date()
```

| Element | Why | Carry finding |
|---|---|---|
| Join definition→statistics on **(date, instrument_id)** | a single-date key unambiguously identifies one instrument on one day; instrument_id reuse only bites when used *without* a date | **F6** |
| Key on the expiration **calendar date**, not the timestamp | one KE contract's expiration time was corrected mid-life; timestamp keying split it and froze the roll permanently | **F10** |
| **Exclude raw_symbol from the key entirely** | one CL contract appeared as `CLM19` then `CLM9`; symbol keying split one contract into two | **F9** |
| Filter `instrument_class == "F"` | the vendor's own outright flag is the authoritative spread filter | **F1** |

**The expiry-guess heuristic is deleted from the active path.** Expiration is
read from the `definition` schema. No year search, no one-digit expansion, no
inference from observation dates remains in the construction path.

### §2.1 Open interest — a disclosed divergence from the carry implementation

`pipeline.py` line 100 reads `stat_type == 6` into a column named `oi`. The
vendor enum is unambiguous:

```
StatType.CLEARED_VOLUME = 6      StatType.OPEN_INTEREST = 9
```

and the two carry different values — on 2026-06-30, CLQ6 shows **170,488** at
stat_type 6 versus **245,241** at stat_type 9.

The A1 roll rule is specified on **open interest**, so this extraction uses
**stat_type 9**. This is recorded as a **disclosure about code this program
reuses, not a verdict on the carry study**: its pipeline is not modified, its
results are not re-audited here, and whether that line is a defect or a
deliberate proxy is the carry owner's question. The consequence for this program
is that TSMOM's front-contract series **will not be identical to carry's**, and
that difference is expected and declared rather than reconciled away.

### §2.2 Open-interest publication lag — the real causal information set

Fable §4 flagged that the implemented decision is one session staler than the
"t-1 OI" phrasing. Reproduced from raw bytes:

| File date | `stat_type` 9 records for CLQ6 | `ts_ref` | Quantity |
|---|---|---|---|
| 2026-06-29 | one, 14:13:03Z | **2026-06-26** | 249,744 |
| 2026-06-30 | two: 02:53:28Z, 14:16:53Z | **2026-06-29** | 245,442 → 245,241 |

Open interest carried in the file for date **D** describes the **D-1 close**
(preliminary overnight, final ~14:15Z on D). Taking the last value of day D
therefore yields OI as of D-1. The roll rule then applies `shift(1)`.

> **Effective causal timing: the A1 roll decision at session `t` uses open
> interest as of the `t-2` close, published during `t-1`.**

This is **causal — no look-ahead** — but one session staler than "t-1 OI". It is
**described, not "improved"**: the goal is an accurate statement of the real
information set, and changing the lag post hoc would be a design change, not a
repair. The X01 draft's roll-rule text now states it.

---

## §3 Re-extraction — COMPLETE

Existing local files only. **No purchase, no refresh, no protected data.**

| Item | Value |
|---|---|
| Days paired (definition ∩ statistics) | **5,026** |
| Definition-only days (no statistics) | 5 |
| Settlement points | **2,706,911** |
| Open-interest points | **1,946,760** |
| **Persistent contracts** | **3,349** (vs 1,936 raw-symbol columns) |
| Non-outright rows dropped (`instrument_class != F`) | 41,455,600 |
| Settlement panel | 4,902 × 3,335 |
| OI panel | 4,906 × 3,094 |
| Coverage | **2010-06-06 → 2026-06-30**, both panels |

**Independent cross-validation against the carry study's own QA report:**

| Quantity | Carry DATA_QA_REPORT | This extraction | Agreement |
|---|---|---|---|
| Unique outright contracts | **3,353** | **3,349** | within 4 |
| Outright rows in `ohlcv-1d` | 941,928 (20.91%) | 941,928 (20.9%) | exact |
| Spread/combo rows | 3,563,342 (79.09%) | 3,563,342 (79.1%) | exact |
| `instrument_class` values | exactly `F` and `S` | exactly `F` and `S` | exact |

Two independently written extractions landing within 4 contracts of each other
is meaningful corroboration of the identity method.

### §3.1 Corrections to the prior input-verification report

`DATABENTO_W1_INPUT_VERIFICATION.md` §4 reported per-root counts of **distinct
raw symbols** and originally labelled them "outright contracts". That column
**undercounts**. The persistent-contract counts are:

| Root | Raw symbols (prior) | **Keys with settlement columns** | Root | Raw symbols | **Keys w/ settle** |
|---|---|---|---|---|---|
| CL | 136 | **320** | ZC | 50 | **96** |
| HO | 120 | **235** | ZS | 70 | **133** |
| RB | 120 | **236** | ZW | 50 | **95** |
| NG | 208 | **342** | ZM | 80 | **159** |
| GC | 120 | **227** | ZL | 80 | **153** |
| SI | 120 | **224** | KE | 50 | **73** |
| HG | 120 | **241** | LE | 60 | **107** |
| PL | 120 | **207** | HE | 80 | **141** |
| PA | 106 | **207** | GF | 80 | **139** |

**Column-label correction (Fable §10 item 4).** The counts in the table above
are **keys carrying a settlement column** (3,335 total), which is **not** the
headline persistent-contract count of **3,349** (all keys, including 14 with no
settlement column). Affected cells: HO 235 vs 237 keys, KE 73 vs 78, ZW 95 vs
100, GF 139 vs 141. Both numbers are correct for what they count; the prior
label conflated them.

**Nothing else in that report changes.** Coverage dates, the 2026-06-30 boundary
resolution, the spread share, the settlement ranges and the divisor finding are
all per-record facts, unaffected by keying. The correction was appended to that
document as §4A rather than rewritten in place.

---

## §4 Panel sanity gate — PASS (10/10), and it ran FIRST

The gate exists because the identity passed on nonsense. It runs before any
identity is believed, and `run_x02a_v2.py` **refuses to execute** unless it
reads `PANEL_SANITY = PASS`.

| Check | Result |
|---|---|
| S1 contract keys unique | **PASS** — 0 duplicates |
| S1 one key → one (asset, expiration) | **PASS** — 0 offending |
| **S2 no contract spans ~the whole panel** (decade-collision signature) | **PASS** — 0 of 3,349 span ≥95% of the 5,868-day panel |
| S3 no settlement materially after expiry | **PASS** — 0 |
| S4 observed lives non-negative | **PASS** |
| S5 negative settlements enumerated | **PASS** — 4, all attributable |
| S6 non-positive share of observed cells | **PASS** — 0.319% |
| S7 all 18 roots present / no extras | **PASS** |
| **S8 decade collision eliminated** | **PASS** — GC June resolves to **23 distinct keys**, 2010–2032, one per year |

**The gate genuinely failed first.** On its first run S5/S6 failed (4 negatives,
8,631 zeros) and the chained job **stopped the dependent computation** rather
than forcing it green. Investigation showed:

- **CL `22770__2020-04-21` settled at −37.63 on 2020-04-20** — the real negative
  WTI settlement, documented and KEPT-with-citation in carry's own QA report.
- **Three ZM contracts at exactly −1.10 on 2016-03-07** — soybean meal cannot
  settle at −$1.10/ton; a vendor artifact, recorded.
- **8,631 zeros** across 1,075 contracts, concentrated 2010–2016, in contracts
  that otherwise settle normally.

**Two design changes were made, both relocating checks to their canonical locus
rather than loosening them:**

1. The generic observed-life cap was replaced by the **collision-specific**
   test (span ≥95% of the panel). CME lists deep curves years ahead — natural
   gas ~12 years — so a flat cap would have false-failed legitimate contracts,
   and raising it would have weakened the check. The long-lived list is still
   reported (0 contracts exceed 4,200 days).
2. S5/S6 became **reported diagnostics**, because the carry study's own spec
   puts the zero/negative-price **HALT on the held front contract**
   (`returns.held_front_zero_price_guard`), not on the panel: a non-positive
   settlement in a contract nobody holds is never divided by. That guard is now
   wired into X02a and **fired CLEAR on all 18 roots** — no held contract ever
   had a settlement ≤ 0. Nothing that would have failed a PnL path now passes
   one.

---

## §5 X02a — builder-side complete, pending independent verification

| Root | Contracts | Rolls | Held-contract availability | Reconciliation (relative) | Truncation mismatches | Divisor |
|---|---|---|---|---|---|---|
| CL | 320 | 136 | 1.00000 | 1.21e-16 | 0 | 1 |
| HO | 235 | 192 | 1.00000 | 1.15e-16 | 0 | 1 |
| RB | 236 | 193 | 1.00000 | 1.19e-16 | 0 | 1 |
| NG | 342 | 127 | 0.99980 | 1.19e-16 | 0 | 1 |
| GC | 227 | 81 | 1.00000 | 1.12e-16 | 0 | 1 |
| SI | 224 | 82 | 1.00000 | 1.15e-16 | 0 | 1 |
| HG | 241 | 82 | 1.00000 | 1.13e-16 | 0 | 1 |
| PL | 207 | 66 | 1.00000 | 1.12e-16 | 0 | 1 |
| PA | 207 | 65 | 1.00000 | 1.22e-16 | 0 | 1 |
| ZC | 96 | 69 | 1.00000 | 1.12e-16 | 0 | **100** |
| ZS | 133 | 78 | 1.00000 | 1.12e-16 | 0 | **100** |
| ZW | 95 | 80 | 1.00000 | 1.13e-16 | 0 | **100** |
| ZM | 159 | 81 | 1.00000 | 1.13e-16 | 0 | 1 |
| ZL | 153 | 80 | 1.00000 | 1.14e-16 | 0 | **100** |
| KE | 73 | 63 | 1.00000 | 1.12e-16 | 0 | **100** |
| LE | 107 | 97 | 1.00000 | 1.12e-16 | 0 | **100** |
| HE | 141 | 114 | 1.00000 | 1.18e-16 | 0 | **100** |
| GF | 139 | 121 | 1.00000 | 1.14e-16 | 0 | **100** |

**Before vs after the repair** — the measure of what was actually wrong:

| | Raw-symbol panels | Persistent keys |
|---|---|---|
| GC rolls in 16 years | **3** | **81** |
| SI rolls | **2** | 82 |
| HG rolls | **5** | 82 |
| Minimum held-contract availability | **44%** | **99.98%** |
| Reconciliation residual | 1.21e-16 | 1.22e-16 |

The residual is **unchanged** across a repair that fixed everything else — the
clearest possible demonstration that the identity was never measuring panel
validity.

**Verdicts.** `ROLL_CONSTRUCTION = PASS` (all roll counts within the declared
25–260 band; all availability ≥ 95%) · `HELD_FRONT_ZERO_GUARD = CLEAR` ·
`ACCOUNTING_IDENTITY = PASS` (all roots monotonic, all truncation-invariant,
max relative residual 1.22e-16) · `COST_UNIT_REGRESSION = PASS`.

**Roll frequencies are now economically coherent:** energy on monthly cycles
(HO 192, RB 193 ≈ one per month over 16 years), metals and grains on their
even/quarterly cycles (GC 81, PL 66, KE 63), livestock in between (LE 97,
GF 121). Nothing is stuck.

**No back-adjusted price enters any PnL path.** Every dollar figure is
`multiplier × (settle_t(held) − settle_{t−1}(held)) / divisor` on **one held
contract**. No continuous or ratio-adjusted series is constructed, spliced or
differenced.

**Correction (Fable B1).** The prior revision of this sentence claimed the
ledger charged "roll legs as costs". **It did not** — the v2 ledger was gross
only. The costed ledger now exists in `run_x02a_v3.py` and is reported in §5.2;
this sentence no longer claims what the code does not do.

### §5.2 The costed dollar ledger — Fable blocker B1, repaired

MAP_v2 §X02 requires the dollar ledger to charge roll legs at their costs, and
asks for the reconciliation of the **net return index against that costed
ledger**. The v2 ledger was gross only, so that reconciliation had never been
performed. `run_x02a_v3.py` builds it.

**Two reconciliations, reported separately. Neither is evidence for the other.**

| | Definition | Result | What it proves |
|---|---|---|---|
| **`GROSS_LEDGER_RECONCILIATION`** | gross USD vs notional × gross return | **PASS**, max relative residual **1.22e-16** | **Arithmetic only.** An ALGEBRAIC TAUTOLOGY: it holds for any numbers, including the nonsense raw-symbol panels, where it also read 1.21e-16. It is **not** evidence of accounting validity, and is labelled so in the JSON. |
| **`NET_LEDGER_RECONCILIATION`** | net USD from this module's independently built cost legs vs notional × carry `chain_returns`' net return | **PASS**, max relative residual **1.22e-16**; cost-term agreement **6.5e-18** | **Not a tautology.** The two cost treatments come from two independent code paths — this file's ledger and carry's `chain_returns`. A disagreement in cost convention (which leg is priced off which contract, whether both legs are charged, whether the divisor was applied) surfaces here and nowhere else. |

The ledger records, per session: notional, gross USD, gross return, the roll-event
flag, cost percentage, cost USD and net USD. Costs are charged only on roll days
and mirror carry's convention exactly — **both legs priced off the old contract**
(close at `p_{t-1}`, open at `p_t`), the quirk Fable §7 notes.

Median roll-day cost, divisor-corrected, per contract held: CL **3.80 bps** ·
ZC **13.91 bps** · ZM **7.30 bps**.

### §5.2a Cash-ledger repair — Astra blocker, and what the divergence means

The fresh GPT-6 Astra delta verification returned `X02_INDEPENDENT_STATUS = FAIL`
on a decisive point: the §5.2 ledger **reproduced `chain_returns`' cost
convention rather than independently establishing one-contract dollar cash
costs**, so the reconciliation proved only that two implementations of the same
error agreed.

**The defect, exactly.** Both roll legs were charged as percentages of the **old**
notional:

```
cost_usd = [pct(p_old) + pct(p_new)] * (mult * p_old)  =  C + C * p_old/p_new
```

The entry leg silently scaled by `p_old/p_new`. Astra's synthetic CL case
(100 → 110, one contract, $12.50/side) therefore produced **$23.863636** where
two fixed sides cost **$25.00** — and it still reconciled at ~1e-16, because
`chain_returns` shares that convention. **A reconciliation between two
expressions of one convention cannot detect that convention being wrong.**

**The authoritative primitive**, read from the frozen cost model
(carry `costs.py`, PREREGISTRATION §5) rather than inferred:

```
cost_per_side_usd = tick_value + $2.50 all-in fee     <- PRIMITIVE (frozen)
cost_per_side_pct = cost_per_side_usd / (settle x multiplier)   <- DERIVED
"Charged on every rebalance trade and every roll leg"
```

CL: `10.00 + 2.50 = $12.50` per side. A one-contract roll trades **two sides**,
so the cash cost is **$25.00 — independent of both contract prices.**

**PATH B is now built from that primitive**: quantity × per-side dollars ×
sides. It never reads a percentage, never reads `chain_returns`, and never
reuses a derived cost object. The ledger carries `held_before`, `held_after`,
`qty`, `exit_cost_usd`, `entry_cost_usd`, `cash_cost_usd`, `gross_usd`,
`net_usd`.

**Synthetic regression, permanent, literal oracle:**

| | Expected | Actual |
|---|---|---|
| exit leg | $12.50 | **$12.50** |
| entry leg | $12.50 | **$12.50** |
| total roll cash cost | **$25.00** | **$25.00** |
| superseded percentage value | — | 23.863636 — **rejected by the test** |

The oracle uses **literal** economic inputs. It does not call
`cost_per_side_pct`, `chain_returns`, or any derived net-return object.

### The Path A vs Path B divergence — real, quantified, and NOT tuned away

With Path B now primitive, the two paths **no longer agree on roll days**, and
that is the point:

| | Value |
|---|---|
| Non-roll days, Path A vs Path B | **1.22e-16** — exact agreement, as it must be (no cost on either path) |
| Roll days | **divergence DETECTED** |
| Maximum gap | **$3.39 per roll** (one contract) |
| Structural form | `gap = C x (1 - p_old/p_new)` |

Path A (`chain_returns`, a percentage convention) implies a cash cost of
`C + C·p_old/p_new`; Path B (the frozen primitive) charges `2C`. The gap is
signed — positive when the new contract is dearer, negative when cheaper — so it
largely cancels in a long sum (net −$4.91 across all 18 roots over 16 years) even
though individual rolls differ by up to $3.39.

**SUPERSEDED BY §5.2b.** This section originally concluded that the divergence
was an acceptable finding to disclose. That conclusion was **wrong**: the frozen
Sec 5 primitive is authoritative, so a production path that disagrees with it is
defective and must be repaired. §5.2b records the repair. The measurements above
stand as the *diagnosis*; only the disposition changed.

**`commodity-carry-research` is NOT modified**, its results are not re-audited,
and whether its percentage convention should be revisited is the carry owner's
question — the same disposition as the `stat_type 6` finding in §9.

### Independence — `NET_LEDGER_INDEPENDENCE = MEANINGFUL`

| | Shared | Independent |
|---|---|---|
| Settlements, held-contract series, multiplier, divisor | **shared primitives** (allowed) | — |
| Cost construction | — | Path A: `chain_returns` percentage convention · Path B: `cost_per_side_usd` × sides × quantity |
| Net dollar result | — | computed separately in each path |

**No derived cost object crosses between them.**

**Mutation-verified** (scratch, nothing written):

| Mutation | Result |
|---|---|
| **A** — double costs in the chain path only | **DETECTED** — comparison gap widened $1.72 → $28.45 (16.5×); Path B moved **$0.000000** |
| **B** — halve the shared percentage helper | **DETECTED** — Path B cash moved **$0.000000**, synthetic oracle stayed $25.00, comparison gap widened $1.72 → $13.19 |
| **C** — force all divisors to 1 | **DETECTED** — the ZC cents-quote regression still fails correctly (0.1390 vs spec-implied 13.9130 bps; ratio 1 ≠ 100) |

Mutation B is the decisive one: the previously reported behaviour — *halve the
shared helper and the reconciliation stays green* — **is no longer possible**.

### §5.2b Production path repaired — the divergence is gone because Path A changed

**§5.2a ended in the wrong place.** It built a correct independent oracle, found
that the production path disagreed with it on roll days, and reported that
divergence as an acceptable disclosed finding. That was a mistake: the frozen
Sec 5 dollar model is **authoritative**, so a production path charging
`C + C·p_old/p_new` instead of `2C` is simply **defective**, and the correct
response is to repair it, not to disclose it and hand it to a verifier.

**What was repaired.** `tsmom_chain_net_returns` is a **TSMOM-local production
chain** that derives the percentage from the cash ledger rather than the
reverse:

```
gross_usd   = multiplier × qty × (p_t − p_{t−1})        [single held contract]
cash_cost   = qty × (C_exit + C_entry)  on roll days, else 0
denominator = multiplier × qty × p_{t−1}                [prior held notional]
net_return  = (gross_usd − cash_cost) / denominator
```

**`commodity-carry-research` is NOT modified.** Its `chain_returns` is retained
**only as a labelled legacy reference**, so the divergence stays visible and
measurable; it builds, checks and corrects nothing.

**Production synthetic CL, through the production path** (§4's requirement —
the earlier synthetic only exercised the oracle):

| | Value |
|---|---|
| p_old → p_new, qty | 100 → 110, 1 contract |
| multiplier | 1,000 |
| **production cash cost** | **$25.00** |
| denominator | $100,000 |
| net return | −0.00025 |
| legacy carry convention would charge | 23.863636 — **rejected** |

**Reconciliation, Path A (production) vs Path B (independent oracle):**

| | Residual |
|---|---|
| **Roll days** | **1.18e-17** (was a gap of up to **$3.39**) |
| Non-roll days | 4.18e-17 |

The gap closed **because Path A was corrected**, not because Path B was
weakened: Path B's oracle is byte-identical to §5.2a's and still returns $25.00.

**Event semantics** (§8), deterministic:

| Case | Expected | Result |
|---|---|---|
| Same contract held, no trade | $0 | **$0** |
| One roll | one charged day at 2C | **1 day, $25.00** |
| Exit and entry legs | C each | **$12.50 / $12.50** |
| Two rolls | two charged days | **2** |
| Rebalance leg | none exists for a one-contract object | none charged |

**Production divisor regression** (§7 — both properties must hold at once):

| Root | Cash/roll (divided) | Cash/roll (undivided) | Cash divisor-invariant | Cost rate divided | undivided | Ratio |
|---|---|---|---|---|---|---|
| **ZC** | $30.00 | $30.00 | **yes** | 13.9130 bps | 0.1391 bps | **100.00** |
| CL | $25.00 | $25.00 | yes | 3.8178 bps | 3.8178 bps | 1.00 |
| ZM | $25.00 | $25.00 | yes | 7.3078 bps | 7.3078 bps | 1.00 |

The cash cost is **fixed dollars and cannot be corrupted by the divisor**; the
divisor still binds through the **notional denominator**, so a removed divisor
makes the ZC cost *rate* 100× too small. Both properties are asserted, and the
oracle is `EXPECTED_COST_RATIO`, never `DIVISOR`.

**Mutations, re-run against the repaired structure:**

| | Result |
|---|---|
| **A** — double production cost only | **DETECTED** — reconciliation $0 → $25.00; oracle unmoved |
| **B** — corrupt `cost_per_side_pct` (legacy-only helper) | **DETECTED as no-op**: production and oracle both unmoved, synthetic stays $25.00, only the legacy reference reacts ($1.72 → $13.19). **The repaired production path does not call that helper at all.** |
| **C** — zero the primitive cost used by production only | **DETECTED** — reconciliation $0 → $25.00; Path B kept its own oracle |
| **D** — force all divisors to 1 | **DETECTED** in both the legacy end-to-end test (ZC 0.1390 vs spec 13.9130) and the **production** divisor test (rate ratio 1 ≠ 100) |

*A harness note, recorded because it nearly contaminated the evidence:*
`carry_costs` is a cached module shared across reloads, so mutation B's patch
initially leaked into C and D and halved their reported bps. The harness now
restores it; the figures above are from the clean run.

### §5.2c Lineage of this accounting, preserved in full

None of these steps is erased:

1. **Gross tautology** — reconciliation at 1.22e-16 that proved only arithmetic.
2. **First "net" reconciliation** — shared `chain_returns`' convention, so it
   compared two expressions of one error.
3. **Astra detects the wrong one-contract cash cost** — $23.863636 vs $25.00.
4. **Primitive independent oracle introduced** (Path B).
5. **The oracle exposes a real Path-A divergence** — up to $3.39 per roll.
6. **Production TSMOM path repaired** to the cash-first convention.
7. **Independent reconciliation passes** at 1.18e-17, mutation-verified.

### §5.3 Cost path — end-to-end, and it fails when broken

Fable §7's required correction: `chain_returns` was called on **undivided**
settlements, so the eight cents-quoted roots' roll-cost term inside the actual
chained object was 100x understated even though the helper-level regression
passed. Every call into `chain_returns` / `cost_per_side_pct` from this program
now receives `settle / DIVISOR[root]`.

The regression exercises the **real chained path**, not a helper:

| Root | Divisor | Cost undivided | Cost divided | Ratio | Spec-implied | Gross-return invariant |
|---|---|---|---|---|---|---|
| **ZC** (cents) | 100 | 0.1390 bps | **13.9050 bps** | **100.00** | 13.9130 bps | yes (2.2e-16) |
| **CL** (decimal) | 1 | 3.8048 bps | 3.8048 bps | 1.00 | 3.8178 bps | yes (0.0) |
| **ZM** (decimal grain) | 1 | 7.3035 bps | 7.3035 bps | 1.00 | 7.3078 bps | yes (0.0) |

Two oracles, **neither derived from `DIVISOR`**: the audited quote-convention
literals, and the spec-implied cost level computed from `CONTRACT_SPECS` over the
true dollar notional. Dividing the panel is confirmed **dimensionally neutral for
the return** (a ratio) and correct for the **cost** (dollars over dollar
notional) — asserted, not assumed.

**Verified by sabotage.** Setting `DIVISOR` to all-1 makes the regression FAIL:

```
ZC: divided cost level 0.1390 bps deviates from the spec-implied 13.9130 bps
ZC: end-to-end cost ratio 1.000000 != 100
```

**A defect in the test itself was found this way.** Its first version derived the
expected ratio from `DIVISOR`, so sabotaging `DIVISOR` moved the oracle with the
code under test and the test still passed — precisely the vacuous-test class this
repair exists to eliminate. The oracle is now independent, and the sabotage run
is the evidence.

**The legacy broken path is not reachable by X01**: every cost call in this
program's futures path goes through the divisor-corrected panel, and the
regression fails if that is undone. `commodity-carry-research` is unmodified.

### §5.4 Sign-agreement diagnostic — MAP_v2 X02a, no longer deferred

Fable §6 found this MAP_v2 X02a component silently deferred. It is now computed:
the locked baseline composite (`signals.signal_method_b`, 1/3/6/12-month
horizons) applied to the ETF adjusted-close cache and to the chained
held-contract futures index, per mapped pair.

| Pair | Months | Sign-agreement rate |
|---|---|---|
| USO ↔ CL | 181 | **91.7%** |
| UNG ↔ NG | 181 | **90.6%** |
| GLD ↔ GC | 181 | **94.5%** |
| DBA ↔ ag basket | — | **deferred** — the basket composition is X01 open item **O-1** and is not invented here |

**Interpretation limit, binding.** MAP_v2 is explicit that a low rate is "a
diagnostic warning that requires investigation … not proof of an implementation
defect, and it grants no permission to tune the construction toward higher
agreement". **No threshold is sealed and none is invented.** This diagnostic does
not prove accounting correctness, does not prove accounting invalidity,
authorises no tuning toward ETF agreement, and is not an X01 result.

**Terminal-month note (raised by the Astra delta verification).** The final
observation compares a **partial** ETF month (the cache ends 2026-06-12) against
a **full** futures month (to 2026-06-30). That asymmetry is tolerable in a
diagnostic and the diagnostic was **not** recomputed for it. It must **not**
carry into X01: the sealed paired window already **excludes June 2026 from both
legs** (draft §3.1), and **this diagnostic's window is not the X01 evaluation
window**. Nothing here changes protected-data handling.

### §5.5 Held-front jump diagnostic (reported, not a gate)

Fable §5's gap: the only held-front validity guard is `<= 0`, so a *positive*
vendor artifact on a held contract would pass silently. Held-front sessions with
|move| > 20% are now enumerated per root — CL 5, RB 5, NG 2, PA 2, HO 1, SI 1,
HG 1, all others 0; **17 in total across 16 years**, matching Fable's independent
count, all attributable to known market events. **Reported, not a gate**: no
arbitrary numeric filter is introduced (repair scope §7).


### §5.6 Cost / unit regression — helper level (PASS)

The verified legacy defect is **unchanged by the repair** and is preserved as an
implementation fact. This is the HELPER-level regression; the end-to-end path
test that actually exercises `chain_returns` is §5.3, which is the one Fable
required. `costs.cost_per_side_pct` divides by `settle × multiplier`
with no price-unit divisor:

| Root | Uncorrected | Corrected | Ratio |
|---|---|---|---|
| ZC | 0.0600 bps | **6.0000 bps** | 100× |
| ZW / KE | 0.0462 bps | **4.6154 bps** | 100× |
| HE | 0.0368 bps | **3.6765 bps** | 100× |
| ZL | 0.0315 bps | **3.1481 bps** | 100× |
| ZS | 0.0250 bps | **2.5000 bps** | 100× |
| LE | 0.0223 bps | **2.2321 bps** | 100× |
| GF | 0.0167 bps | **1.6667 bps** | 100× |
| CL, HO, RB, NG, GC, SI, HG, PL, PA, **ZM** | unchanged | unchanged | 1× |

Regression tests assert, for all 18 roots, that `tick_size × multiplier ==
tick_value` **and** that applying the divisor changes cost by exactly 100× for
the eight cents-quoted roots and exactly 1× for the other ten. **ZM is decimal
dollars despite being a grain** — the natural assumption that all grains are
cents-quoted is wrong, and the test pins it.

**The broken cost function is not inherited into any X01 performance path**: the
divisor is applied at this program's boundary. The carry repository is unmodified.

---

## §6 X03 structural — rerun on the AUTHORITATIVE comparator

**The prior X03 result is INVALID and SUPERSEDED — twice over.** The v1 run
(raw-symbol panels) was an artefact of a stuck A1 series. The v2 run used a
comparator that Fable §8 found **mis-described and not the accepted rule**: it
rolled on five **calendar days** while the docstring said "5 sessions", it rolled
into the next **listed** month regardless of liquidity (walking through dead
serial months, which is what drove metals to 98–100%), and it differed from v1's
comparator without that re-specification being disclosed. Neither is evidence.

**Authoritative comparator, read from source rather than inferred:**
`commodity-carry-research/src/robustness.py::fixed_calendar_front_series`,
specified in carry `DEVIATIONS.md` 2026-07-16 (PREREGISTRATION §8 item 7):

- **roll timing** — the last business day of the month **preceding** the front
  contract's expiry month; parameter-free, no N to tune;
- **candidate selection** — the same **A2 existence filter**: earliest later
  expiration with **open interest at t−1 strictly positive**;
- **OI lag** — t−1 throughout; no look-ahead.

That function is called directly and unmodified; the carry repository is not
edited.

| Root | A1 rolls | Authoritative calendar rolls | Disagreement (authoritative) | (naive, non-authoritative) | A1 median days-to-expiry at roll |
|---|---|---|---|---|---|
| CL | 136 | 194 | **55.4%** | 41.0% | 9.0 |
| HO | 192 | 194 | **51.1%** | 32.6% | 15.0 |
| RB | 193 | 194 | **47.2%** | 35.9% | 16.0 |
| NG | 127 | 194 | **48.2%** | 55.5% | 14.0 |
| GC | 81 | 194 | **68.4%** | 98.4% | 34.0 |
| SI | 82 | 194 | **72.0%** | 99.5% | 37.0 |
| HG | 82 | 194 | **78.2%** | 100.0% | 42.0 |
| PL | 66 | 185 | **70.8%** | 99.2% | 36.0 |
| PA | 65 | 145 | **48.6%** | 98.4% | 34.0 |
| ZC | 69 | 81 | **35.2%** | 45.8% | 31.0 |
| ZS | 78 | 113 | **42.1%** | 53.4% | 30.0 |
| ZW | 80 | 81 | **25.7%** | 38.9% | 31.0 |
| ZM | 81 | 129 | **49.4%** | 62.3% | 31.0 |
| ZL | 80 | 129 | **50.9%** | 63.3% | 32.0 |
| KE | 63 | 63 | **24.4%** | 36.1% | 31.0 |
| LE | 97 | 97 | **29.8%** | 71.4% | 49.0 |
| HE | 114 | 130 | **44.4%** | 61.7% | 33.0 |
| GF | 121 | 128 | **29.3%** | 63.4% | 38.0 |

**Aggregate on the authoritative comparator:** mean **48.40%**, median 48.40%,
range **24.4% (KE) – 78.2% (HG)**; A1 rolls **1,807** vs authoritative **2,639**.
**All 18 roots exceed 10%.** The naive comparator's mean was 64.27%.

**This reproduces Fable's independent Appendix C figures exactly** — mean 48.4%,
KE 24.4% minimum, HG 78.2% maximum, metals 68–78%, energy 47–55%,
grains/livestock 24–51%, all roots above 10%.

### Structural reading, and what it does not say

```
STRUCTURAL_DOF_REQUIRED        = TRUE
ROLL_RULE_DOF                  = REQUIRED   (conservative governance declaration)
ROLL_RULE_ECONOMIC_MATERIALITY = UNRESOLVED
```

**Structural non-equivalence is established** — under *both* comparators, on
every root. The two rules hold a different contract on roughly half of all
sessions and differ materially in roll count.

**Economic materiality is NOT established, and this record does not imply it.**
V2 §X03's consequence clause is conditional on the roll rule "proving material
(declared margin, designer-proposed)", and X01 precondition 2 accepts "declared
a DoF **or** recorded immaterial within a declared margin". **No margin was
sealed and no performance quantity was computed**, so materiality is
`UNRESOLVED` and belongs to the X01 **S2 secondary arm**, after the seal.
Structural disagreement does **not** prove an economically meaningful
performance difference — and the magnitude is comparator-dependent (64% naive vs
48% authoritative), which is itself a reason not to read a magnitude as
materiality.

Declaring the DoF costs nothing in validity: A1 remains primary by architecture,
the X01 draft already carries S2 as the roll-rule sensitivity arm, and the
declaration is fail-closed. **The A2 challenge must fix which calendar
comparator S2 uses.**

**No roll rule was selected**, and no Δ Sharpe, PnL, return series or
correlation of any performance quantity was computed.


---


---

## §7 Consequences for X01

| Precondition | Status |
|---|---|
| 1 — X02a mechanical truth passes | **PENDING INDEPENDENT VERIFICATION.** Builder-side complete: panel sanity PASS, gross and net ledger reconciliations PASS (reported separately), end-to-end cost path PASS with a verified sabotage failure, sign-agreement diagnostic computed, truncation invariance and roll monotonicity PASS. **Not MET** — the prior "MET" was the overclaim Fable identified, and this session produced the repair and cannot certify it. |
| 2 — X03 structural complete; roll rule declared a DoF or recorded immaterial | **PENDING INDEPENDENT VERIFICATION.** Builder-side complete on the **authoritative** carry comparator: `ROLL_RULE_DOF = REQUIRED` (governance declaration) and `ROLL_RULE_ECONOMIC_MATERIALITY = UNRESOLVED`. Materiality was **not** established and is the X01 S2 arm's question. |

**These are two of six preconditions.** O-1…O-6, the shared-Databento append
home, the fresh Astra A2 challenge and Aaron's seal all remain open.
**`X01_PREREG_SEALED = NO`, `X01_FULL_PERFORMANCE_EXECUTED = NO`.**

**Trial accounting unmoved.** No strategy-return series was constructed, so the
Databento contribution stays **0** against the frozen `N_trials = 14`.

---

## §8 Append log

| Date (UTC) | Appended | By |
|---|---|---|
| 2026-09-07 | Created. X02a/X03 attempted and **BLOCKED** on the raw-symbol panel defect. | Wave-1 session (Claude Opus 5) |
| 2026-09-08 | **Production cash-path repair.** §5.2b added: `tsmom_chain_net_returns`, a TSMOM-local cash-first production chain (percentage derived FROM the cash ledger). Production synthetic CL roll cost **$25.00**; roll-day reconciliation **1.18e-17** (was $3.39); event-semantics tests; production divisor regression. Mutations A–D all DETECTED. §5.2a's "acceptable divergence" conclusion is marked **SUPERSEDED** — the divergence was a production defect, now repaired. Carry untouched and retained as a labelled legacy reference. §5.2c preserves the full 7-step lineage. **X03 not rerun; X01 precondition 1 still PENDING.** | Wave-1 repair session (Claude Opus 5) |
| 2026-09-08 | **Astra cash-ledger repair** (delta verification `OVERALL = FAIL`, `X02_INDEPENDENT_STATUS = FAIL`). §5.2a added: the one-contract cash ledger rebuilt from the frozen Sec 5 **dollar** primitive; synthetic CL $25.00 regression with a literal oracle; the Path A vs Path B roll-day divergence **detected and quantified** rather than tuned away; independence **MEANINGFUL**, mutation-verified (A/B/C all DETECTED). Sign-diagnostic terminal-month note added (§5.4). Second timestamp erratum appended to both ledgers and the state file. **X03 not rerun; its comparator unchanged. Carry not modified. X01 precondition 1 remains PENDING.** | Wave-1 repair session (Claude Opus 5) |
| 2026-09-08 | **Bounded Fable-audit repair** (audit `b2ea7694…f8acd`, `CONDITIONAL_PASS`, 1 blocker). B1 closed: costed dollar ledger built, **gross and net reconciliations separated** (§5.2), end-to-end cost path repaired and sabotage-verified (§5.3), sign-agreement diagnostic computed (§5.4), held-front jump diagnostic added (§5.5). X03 rerun on the **authoritative** carry `fixed_calendar_front_series` comparator (§6). OI publication lag reproduced from bytes (§2.2). Carry stat_type-6 finding recorded for the carry owner (§9). Status wording corrected from `COMPLETE`/`MET` to builder-side pending. §3.1 column label corrected. | Wave-1 repair session (Claude Opus 5) |
| 2026-09-08 | **Bounded contract-identity repair.** Persistent key adopted from carry's `build_outright_panel` (F1/F6/F9/F10); expiry heuristic deleted; OI stat_type divergence disclosed (§2.1); re-extraction §3 with cross-validation against carry's QA; panel-sanity gate §4 (failed first, investigated, two checks relocated to their canonical locus); **X02a COMPLETE** §5; **X03 COMPLETE, `ROLL_RULE_DOF = REQUIRED`** §6. Prior invalid outputs retained as lineage. | Wave-1 repair session (Claude Opus 5) |

---

## §9 Cross-project finding — RECORDED ONLY, for the carry owner

```
CROSS_PROJECT_CARRY_FINDING = UNRESOLVED_FOR_CARRY_PROJECT
```

`commodity-carry-research/src/pipeline.py:100` reads `stat_type == 6` into a
column named `oi`. The vendor enum and the data both say `6 = CLEARED_VOLUME`
and `9 = OPEN_INTEREST`. Evidence, independently confirmed by Fable §4:

| Evidence | stat_type 6 | stat_type 9 |
|---|---|---|
| Untraded far month `CLZ36`, three sessions | 0 each day | 20 each day (constant, positive) |
| Sum over CL outrights, 2026-06-26/29/30 | 748,962 / 744,110 / 516,212 (varies like volume) | 1,919,698 / 1,932,308 / 1,929,492 (stable; ≈ CME's reported CL open interest) |
| Zeros among 58 CL outrights (2026-06-30) | 17 | 0 |
| Correlation with `ohlcv-1d` `volume` | 0.92–0.95 | 0.73–0.81 |
| `CLK0` in the 2020-04-20 file | 240,628 | 108,593 (the publicly reported May-2020 open interest) |

**Consequence for the carry project (not adjudicated here):** its front-contract
series, A2 existence filter and published results were computed on **cleared
volume**, not open interest, and its `DATA_QA_REPORT.md` field identification is
inconsistent with the vendor enum.

**Scope discipline.** `commodity-carry-research` was **not modified, not rerun
and not re-audited** by this repair. This is recorded as fact, with enough
evidence for a later dedicated carry-owner review. **It is not a TSMOM blocker**:
TSMOM independently uses `stat_type 9` — in the superseded v1 extractor and in
the repaired v2 alike — so no TSMOM conclusion ever inherited stat_type 6.
