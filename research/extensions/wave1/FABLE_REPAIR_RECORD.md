# FABLE_REPAIR_RECORD.md — Wave-1 futures-infra bounded repair

**Program:** TSMOM-EXT-001 · **Wave:** 1 · **Lane:** MEASUREMENT · **Stage:** C/D
**Created:** 2026-09-08 (bounded repair under Aaron's authorization)
**Audit repaired against:** `2026-09-08-tsmom-wave1-futures-infra-fable-audit-01.md`
SHA256 `b2ea769421108dae82e351d564b31e963dd653a4ddeb1d660b275592215f8acd` — **recomputed and MATCHED** before any file was touched.
**Audit verdict:** `OVERALL = CONDITIONAL_PASS`, `CURRENT_BLOCKERS = 1` (B1 bundle).

This record exists because Fable §1 and §10 item 3 found that **no SHA256 was
recorded on disk for any repair artifact** by the producing session, so the
standing artifact-transport rule's "recorded SHA256" precondition was unmet.
Fable's §1 manifest is adopted as the pre-repair pin, and this file is the
post-repair one.

---

## §1 Pre-repair verification

**All 19 audited artifacts matched the Fable §1 manifest byte-for-byte** before
any modification, and all four accepted V2 hashes matched their pins. No
mismatch; no STOP condition.

| Accepted V2 artifact | Pinned SHA256 | Recomputed | Result |
|---|---|---|---|
| `TSMOM_EXTENSION_RESEARCH_MAP_v2.md` | `e9555a0220b58fdf…` | `e9555a0220b58fdf…` | **MATCH** |
| `TSMOM_EXTENSION_RESEARCH_PROGRAM_v2.md` | `e9555f561e302c4f…` | `e9555f561e302c4f…` | **MATCH** |
| `IDEA_REGISTRY_v2.csv` | `7e3024edd1e55374…` | `7e3024edd1e55374…` | **MATCH** |
| `DASHBOARD_v2.md` | `951801bcea028181…` | `951801bcea028181…` | **MATCH** |

---

## §2 Repair manifest — pre-repair, audit, post-repair

| Path | Pre-repair = Fable §1 audit SHA256 | Post-repair SHA256 | Changed |
|---|---|---|---|
| `research/extensions/wave1/FUTURES_INFRA_TRUTH.md` | `84eda54cdca4cbc2…` | `bb3e0d2d6e24ee44…` | **yes** |
| `research/extensions/wave1/DATABENTO_W1_INPUT_VERIFICATION.md` | `2f8f3e93de23efea…` | `2f8f3e93de23efea…` | **yes** |
| `research/extensions/wave1/extract_contracts_v2.py` | `577140c744c0bd3f…` | `577140c744c0bd3f…` | **yes** |
| `research/extensions/wave1/panel_sanity.py` | `452036b16e0d2237…` | `407b76d0ba403b14…` | **yes** |
| `research/extensions/wave1/run_x02a_v2.py` | `7fb2978e96c7cae9…` | `7fb2978e96c7cae9…` | **yes** |
| `research/extensions/wave1/run_x03_structural_v2.py` | `b367b11653828e4d…` | `b367b11653828e4d…` | **yes** |
| `research/extensions/wave1/extract_v2_meta.json` | `0ccc775d0067b9dd…` | `0ccc775d0067b9dd…` | **yes** |
| `research/extensions/wave1/panel_sanity.json` | `15b25cf5918fd2be…` | `c140f4f7dffa47ff…` | **yes** |
| `research/extensions/wave1/x02a_v2_results.json` | `0b63301969a81553…` | `0b63301969a81553…` | **yes** |
| `research/extensions/wave1/x03_structural_v2.json` | `dabe8251e6cf4e4a…` | `dabe8251e6cf4e4a…` | **yes** |
| `research/extensions/wave1/settle_v2.parquet` | `490cbba08c41d09b…` | `490cbba08c41d09b…` | **yes** |
| `research/extensions/wave1/oi_v2.parquet` | `be70a5dd31748e60…` | `be70a5dd31748e60…` | **yes** |
| `research/extensions/wave1/contracts_meta.parquet` | `1fab7943ec5d416c…` | `1fab7943ec5d416c…` | **yes** |
| `research/extensions/x01/X01_PREREGISTRATION_DRAFT.md` | `947f3b293e11f2f0…` | `991239c366075071…` | **yes** |
| `research/extensions/validate_wave0.py` | `8cd2b54a806cf097…` | `c39d54f8fa65f2e2…` | **yes** |
| `qros-state.yaml` | `3e70368b66ae2964…` | `60235209d206ae36…` | **yes** |
| `ops/EXPOSURE_LEDGER.md` | `c1ea87cee96e364a…` | `c64ccd4241b10531…` | **yes** |
| `ops/REVIEWER_EXPOSURE_LOG.md` | `058e63e2d91278fc…` | `9c5c09df0b6b0d71…` | **yes** |
| `research/extensions/TRIAL_LEDGER.md` | `9aa6e71036bca486…` | `9aa6e71036bca486…` | **yes** |
| `research/extensions/wave1/run_x02a_v3.py` | *(new — did not exist at audit)* | `daaf4f9e5787e7b3…` | **new** |
| `research/extensions/wave1/run_x03_structural_v3.py` | *(new — did not exist at audit)* | `1d99ca7de3b1f4e4…` | **new** |
| `research/extensions/wave1/x02a_v3_results.json` | *(new — did not exist at audit)* | `a1f1e9c7fced9740…` | **new** |
| `research/extensions/wave1/x03_structural_v3.json` | *(new — did not exist at audit)* | `7cb64e8b4f76c55d…` | **new** |
| `research/extensions/wave1/FABLE_REPAIR_RECORD.md` | *(new — did not exist at audit)* | *(self; final hash reported separately)* | **new** |

---

## §3 What was repaired, against the audit's own scope

| Audit item | Action |
|---|---|
| **B1(a)** ledger has no cost legs | Costed dollar ledger built in `run_x02a_v3.py`: notional, gross USD, gross return, roll-event flag, cost %, cost USD, net USD. Costs charged on roll days, both legs priced off the old contract, mirroring carry `chain_returns`. |
| **B1(b)** net reconciliation never performed | `NET_LEDGER_RECONCILIATION` added and reported **separately** from the gross one, which is explicitly labelled an algebraic tautology. Net residual 1.22e-16; cost-term agreement vs `chain_returns` 6.5e-18. |
| **B1(c)** sign-agreement silently deferred | Computed for the three unambiguous mapped pairs: USO/CL 91.7%, UNG/NG 90.6%, GLD/GC 94.5% over 181 months. DBA deferred to open item **O-1**, explicitly, not invented. |
| **B1(d)** status overclaimed | `X02_STATUS = COMPLETE` and X01 preconditions "MET" replaced by builder-side `COMPLETE_PENDING_INDEPENDENT_VERIFICATION` and **PENDING**. |
| **§7** cost path inherits the 100x defect | `chain_returns` / `cost_per_side_pct` now receive divisor-corrected settlements. End-to-end regression on the real chained path, with oracles **independent of `DIVISOR`**, verified to FAIL under sabotage. |
| **§8** comparator mis-described / not the accepted rule | X03 rerun on carry `robustness.fixed_calendar_front_series` (last business day of the preceding month + A2 existence filter). Mean 48.40%, range 24.4%–78.2%, all 18 roots >10% — reproducing Fable's Appendix C exactly. |
| **§8** materiality overclaimed | `ROLL_RULE_DOF = REQUIRED` retained as a governance declaration; **`ROLL_RULE_ECONOMIC_MATERIALITY = UNRESOLVED`** stated wherever the DoF is stated. |
| **§4** OI publication lag | Reproduced from bytes and documented: the decision at `t` uses OI as of the **`t−2` close, published `t−1`**. Causal; **described, not "improved"**. |
| **§5** held-front jump gap | Reported diagnostic added (17 sessions >20% across 16 years). No numeric filter invented. |
| **§2** fragmentation not visible | Panel-sanity S1b diagnostic added: 14 (root, expiration) groups with >1 key, reported. |
| **§9** lineage labels one-third true | Validator registry now labels `run_x02a.py`, `extract_settle_oi.py`, `run_x02a_v2.py` and `run_x03_structural_v2.py` as SUPERSEDED with the reason. |
| **§10.1** projected timestamps | Exposure erratum row **20**; reviewer erratum row **S10**; errata index extended. Rows 18–19 and S9 **not edited**. |
| **§10.2** no repair session_log | `session_log[]` entry added to `qros-state.yaml`. |
| **§10.3** no recorded SHA256 | This record. |
| **§10.4** §3.1 column label | Corrected: those counts are keys **with settlement columns** (3,335), not the 3,349 headline. |
| **§11** X01 draft text | §3.3 rewritten to the vendor `instrument_class == "F"` filter and persistent identity; §3 cost line; OI-lag disclosure; precondition wording. |
| **§4** carry stat_type 6 | Recorded only, in `FUTURES_INFRA_TRUTH.md` §9. `commodity-carry-research` **not modified, not rerun, not adjudicated**. |

---

## §4 Not done, deliberately

- **`commodity-carry-research` untouched** — not modified, not rerun, not re-audited.
- **No owner decision resolved**: shared Databento append home, D3, O-1…O-6, the
  degradation boundary, block length and the classification ceiling all remain open.
- **No new strategy-return series**; Databento governed contribution remains **0**
  against the frozen `N_trials = 14`.
- **X01 not sealed, not run.** No Sharpe, no PnL, no wrapper comparison, no
  candidate or roll-rule selection anywhere in this repair.
- **Validator semantics untouched** — registry data only.

---

## §5 Verified-observation record (audit §7)

Preserved as independently confirmed, and **not** replaced by a global `price > 0`
rule, which would delete the legitimate negative WTI settlement:

- CL `22770__2020-04-21` settling **−37.63** on 2020-04-20 is a real market event
  and is **retained**; the held front that day was a different contract, so it
  never enters the held path.
- The three ZM **−1.10** cells (2016-03-07) sit on two-observation phantom
  listings, three years from expiry, with no open interest; **never held**.
- 8,631 zero settlements across 1,075 contracts; **never held**.
- Enforcement stays at the **held-contract** path: carry's
  `held_front_zero_price_guard`, which fired **CLEAR** on all 18 roots.
- **Known limit, not papered over:** that guard tests `<= 0` only, so a *positive*
  vendor artifact on a held contract would still pass. The §5.5 jump diagnostic
  makes such a case visible; **no arbitrary numeric filter was invented.**

---

## §6 Append log

| Date (UTC) | Entry | By |
|---|---|---|
| 2026-09-08 | Record created at the bounded Fable-audit repair. Pre-repair manifest verified (19/19 + 4/4 V2); repair manifest §2; scope mapping §3; exclusions §4; price-quality observations §5. | Wave-1 repair session (Claude Opus 5) |
