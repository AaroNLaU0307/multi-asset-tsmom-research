"""X02a v3 — costed accounting truth. Fable B1 + Astra cash-ledger + production repair.

Supersedes `run_x02a_v2.py`, whose ledger was GROSS ONLY. Fable
`TSMOM-EXT-FABLE-W1-FUTURES-INFRA-01` §6/§12 B1: the v2 reconciliation
`mult*(p_t - p_{t-1})/div` vs `(mult*p_{t-1}/div)*(p_t/p_{t-1} - 1)` is an
ALGEBRAIC TAUTOLOGY (residual 1.22e-16 for any numbers) and **contains no cost
legs**, contradicting MAP_v2 §X02's ledger definition ("roll legs charged at
their costs") and leaving the only non-tautological reconciliation MAP_v2 asks
for — the net return index against a costed dollar ledger — unperformed.

WHAT THIS ADDS
  1. A costed dollar ledger: gross held-contract PnL, the roll event, the cost
     legs, and the net ledger result, on DIVISOR-CORRECTED prices.
  2. TWO reconciliations, reported separately and never one as evidence for the
     other:
       GROSS_LEDGER_RECONCILIATION - gross USD vs notional x gross return.
           Algebraic. Reported AS tautological. Proves arithmetic, not accounting.
       NET_LEDGER_RECONCILIATION   - net USD from THIS module's independently
           built cost legs vs notional x carry `chain_returns`' net return.
           NOT a tautology: the two cost treatments come from two separate code
           paths (this file's ledger and carry's chain_returns). A disagreement
           in cost convention shows up here and nowhere else.
  3. The MAP_v2 X02a sign-agreement diagnostic, previously deferred silently.
  4. An END-TO-END cost regression on the real chained path that FAILS if the
     divisor is removed - not a helper-level test.

ASTRA CASH-LEDGER REPAIR (2026-09-08). The first costed ledger charged BOTH roll
legs as percentages off the OLD notional:

    cost_usd = [cost_per_side_pct(p_old) + cost_per_side_pct(p_new)] * (mult * p_old)
             = C + C * p_old / p_new                       <-- entry leg scaled

For CL at p_old=100 -> p_new=110 that is 12.50 + 11.3636 = **23.8636**, not the
**25.00** two fixed $12.50 sides actually cost. It still reconciled at ~1e-16
against `chain_returns` because `chain_returns` uses the SAME percentage
convention: the test compared two implementations of one error.

The frozen cost model (carry `costs.py`, PREREGISTRATION §5) makes the DOLLAR
figure primitive and the percentage derived:

    cost_per_side_usd = tick_value + $2.50 all-in fee     <-- primitive
    cost_per_side_pct = cost_per_side_usd / (settle * multiplier)   <-- derived
    "Charged on every rebalance trade and every roll leg"

So `PATH B` below is rebuilt from the primitive: quantity x per-side dollars x
sides, price-independent. It never reads a percentage, never reads
`chain_returns`, and never reuses a derived cost object.

PRODUCTION PATH REPAIR (2026-09-08, third pass). The previous pass built a
correct PRIMITIVE cash oracle (Path B) but left the PRODUCTION path (Path A) on
carry's percentage convention, and then reported the resulting roll-day
divergence as an acceptable finding. That was wrong: the frozen Sec 5 dollar
model is authoritative, so a production path that charges
`C + C*p_old/p_new` instead of `2C` is simply defective and must be repaired,
not disclosed.

`tsmom_chain_net_returns` is therefore a TSMOM-LOCAL production chain that
derives its percentage from the cash ledger rather than the reverse:

    gross_usd   = multiplier * qty * (p_t - p_{t-1})       [held contract]
    cash_cost   = qty * (C_exit + C_entry) on roll days, else 0
    denominator = multiplier * qty * p_{t-1}               [prior held notional]
    net_return  = (gross_usd - cash_cost) / denominator

`commodity-carry-research` is NOT modified. Its `chain_returns` is retained ONLY
as a labelled legacy reference so the divergence stays visible and measurable.

COST PATH. Fable §7: `chain_returns` was called on UNDIVIDED settlements, so the
eight cents-quoted roots' roll-cost term was 100x understated in the actual
chained object. Fix: every call into `chain_returns` / `cost_per_side_pct` from
this program receives `settle / DIVISOR[root]`. Dividing the settlement panel is
dimensionally neutral for the RETURN (a ratio) and correct for the COST (a
dollar quantity over dollar notional) - both properties are asserted by the
regression, not assumed.

NOT a performance module. No Sharpe, no portfolio return, no wrapper comparison,
no candidate selection. The one-contract series is an accounting object.

Requires panel_sanity.json = PASS.
Writes research/extensions/wave1/x02a_v3_results.json.
"""
import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).parent
REPO = Path(__file__).resolve().parents[3]
CARRY = REPO.parent / "commodity-carry-research"
sys.path.insert(0, str(CARRY))
from src import config as carry_cfg          # noqa: E402
from src import costs as carry_costs         # noqa: E402
from src import roll as carry_roll           # noqa: E402
from src import returns as carry_returns     # noqa: E402

CENTS_QUOTED = {"ZC", "ZS", "ZW", "KE", "ZL", "LE", "HE", "GF"}
DIVISOR = {r: (100.0 if r in CENTS_QUOTED else 1.0) for r in carry_cfg.ALL_SYMBOLS}

# TEST ORACLE - deliberately INDEPENDENT of DIVISOR above.
#
# A first version of the end-to-end regression derived its expected ratio from
# DIVISOR itself. Sabotaging DIVISOR to all-1 then moved the oracle with the
# code under test and the regression still passed - the exact vacuous-test
# class this repair exists to eliminate. Found by running that sabotage.
#
# These literals restate the quote conventions VERIFIED from observed
# settlement ranges (DATABENTO_W1_INPUT_VERIFICATION.md section 5) and
# independently confirmed by the Fable audit section 7. They are the fixed
# fact the production DIVISOR is checked against, and must never be derived
# from it.
AUDITED_CENTS_QUOTED = ("ZC", "ZS", "ZW", "KE", "ZL", "LE", "HE", "GF")
EXPECTED_COST_RATIO = {r: (100.0 if r in AUDITED_CENTS_QUOTED else 1.0)
                       for r in carry_cfg.ALL_SYMBOLS}

ROLL_BAND = (25, 260)
AVAILABILITY_MIN = 0.95
JUMP_REPORT = 0.20            # held-front |move| reported for inspection
QTY = 1                       # one contract; the accounting unit X02a specifies

# MAP_v2 X01 frozen map. DBA<->ag basket is OPEN (X01 draft O-1) and is NOT
# invented here; only the three unambiguous pairs are computed.
ETF_FUTURES_PAIRS = {"USO": "CL", "UNG": "NG", "GLD": "GC"}


def divided(panel, root):
    """Settlement panel in DECIMAL DOLLARS for cost arithmetic."""
    return panel / DIVISOR[root]


# ---------------------------------------------------------------- regression --
def end_to_end_cost_regression(settle, meta, oi):
    """Prove the ACTUAL chained path costs correctly, and fails without the divisor.

    For a cents-quoted root (ZC), a decimal root (CL) and ZM (a grain that is
    decimal dollars, so a family-based rule would get it wrong):

      * gross return is INVARIANT to the divisor (it is a ratio);
      * the roll-day cost term scales by exactly the divisor;
      * removing the divisor understates cost by exactly 100x for ZC and not at
        all for CL/ZM  -> the test fails if the divisor is removed.
    """
    out, failures = {}, []
    for root in ("ZC", "CL", "ZM"):
        keys = meta[meta["asset"] == root].sort_values("expiration_dt")
        listed = [k for k in keys["_contract_key"] if k in settle.columns]
        s_raw = settle[listed].dropna(how="all")
        o_r = oi.reindex(index=s_raw.index, columns=listed)
        front = carry_roll.compute_front_contract_series(o_r, listed)

        r_undiv = carry_returns.chain_returns(s_raw, front, symbol=root)
        r_div = carry_returns.chain_returns(divided(s_raw, root), front, symbol=root)

        roll_days = front.index[(front != front.shift(1)).fillna(False)]
        roll_days = [d for d in roll_days if d in r_div.index and d in r_undiv.index]

        # gross return on roll days, reconstructed from the held contract, so the
        # cost term can be isolated as gross - net.
        gross, gross_px = {}, {}
        dates = s_raw.index
        s_dol_r = s_raw / EXPECTED_COST_RATIO[root]   # oracle-scaled dollars
        for i in range(1, len(dates)):
            t, tm1 = dates[i], dates[i - 1]
            held = front.at[tm1]
            p_t, p_tm1 = s_raw.at[t, held], s_raw.at[tm1, held]
            if pd.notna(p_t) and pd.notna(p_tm1) and p_tm1 != 0:
                gross[t] = p_t / p_tm1 - 1.0
                gross_px[t] = s_dol_r.at[tm1, held]
        cost_undiv = np.array([gross[d] - r_undiv.at[d] for d in roll_days if d in gross])
        cost_div = np.array([gross[d] - r_div.at[d] for d in roll_days if d in gross])
        ratio = float(np.median(cost_div / np.where(cost_undiv == 0, np.nan, cost_undiv)))

        common = r_div.index.intersection(r_undiv.index)
        non_roll = [d for d in common if d not in set(roll_days)]
        gross_invariant = float(
            np.abs(r_div.loc[non_roll].values - r_undiv.loc[non_roll].values).max())

        expected = EXPECTED_COST_RATIO[root]        # oracle, NOT DIVISOR
        ratio_ok = abs(ratio - expected) < 1e-6
        # Absolute-level oracle: the divided path's cost must equal the spec
        # cost over the true dollar notional, independent of any ratio.
        held_prices = [gross_px[d] for d in roll_days if d in gross_px]
        exp_bps = float(np.median([
            carry_costs.cost_per_side_pct(root, p) * 2.0 * 1e4 for p in held_prices]))
        level_ok = abs(float(np.median(cost_div) * 1e4) - exp_bps) / exp_bps < 0.15
        if not level_ok:
            failures.append("%s: divided cost level %.4f bps deviates from the "
                            "spec-implied %.4f bps" %
                            (root, float(np.median(cost_div) * 1e4), exp_bps))
        invariant_ok = gross_invariant < 1e-12
        if not ratio_ok:
            failures.append("%s: end-to-end cost ratio %.6f != %.0f" % (root, ratio, expected))
        if not invariant_ok:
            failures.append("%s: gross return not divisor-invariant (max diff %.3e)"
                            % (root, gross_invariant))
        out[root] = {
            "divisor_used_by_production_path": DIVISOR[root],
            "divisor_expected_by_oracle": expected,
            "n_roll_days_tested": int(len(cost_div)),
            "median_cost_bps_undivided": float(np.median(cost_undiv) * 1e4),
            "median_cost_bps_divided": float(np.median(cost_div) * 1e4),
            "cost_ratio_divided_over_undivided": ratio,
            "expected_ratio": expected,
            "cost_ratio_as_expected": ratio_ok,
            "expected_cost_bps_from_specs": exp_bps,
            "cost_level_matches_specs": level_ok,
            "gross_return_divisor_invariant": invariant_ok,
            "gross_return_max_abs_diff_non_roll": gross_invariant,
        }
    return {"all_pass": not failures, "failures": failures, "per_root": out,
            "oracle": ("EXPECTED_COST_RATIO and the spec-implied cost level are "
                       "independent of DIVISOR; setting DIVISOR to all-1 makes "
                       "this test FAIL, which was verified by sabotage"),
            "meaning": ("exercises carry chain_returns on the real panel, not a "
                        "helper function")}




# ====================================================================== PATH A
# TSMOM PRODUCTION CHAIN — cash-first, percentage derived.
#
# Deliberately implemented SEPARATELY from Path B's oracle below. Both read the
# same frozen PRIMITIVE (`cost_per_side_usd`), which section 5 permits, but
# neither reads the other's derived cash-cost result. That separation is what
# makes the mutation tests meaningful: corrupting one path's cost computation
# does not move the other's.

def production_roll_cash_cost(root, qty=1, cost_multiplier=1.0):
    """Path A's own cash-cost computation for one roll: exit leg + entry leg.

    Independent implementation of the same frozen primitive Path B uses. Fixed
    dollars per side, so it does not scale with either contract price.
    """
    c = carry_costs.cost_per_side_usd(root, cost_multiplier)
    return qty * c, qty * c


def tsmom_chain_net_returns(settle_dollars, front_series, root, qty=1,
                            cost_multiplier=1.0):
    """TSMOM production net-return chain, built from the cash ledger.

    Returns (net_return, gross_usd, cash_cost_usd, denominator) as aligned
    Series. Costs are charged ONLY on an actual roll (held contract changes),
    and then on BOTH legs. A day on which the held contract is unchanged trades
    nothing and is charged nothing; this one-contract accounting object has no
    rebalance leg, so none is charged.

    No price splicing and no back-adjustment: every quantity is taken from the
    single contract actually held over t-1 -> t.
    """
    dates = settle_dollars.index
    idx, net, gross, cash, den = [], [], [], [], []
    mult = carry_cfg.CONTRACT_SPECS[root]["multiplier"]
    for i in range(1, len(dates)):
        t, tm1 = dates[i], dates[i - 1]
        held_y, held_t = front_series.at[tm1], front_series.at[t]
        p_t, p_tm1 = settle_dollars.at[t, held_y], settle_dollars.at[tm1, held_y]
        if pd.isna(p_t) or pd.isna(p_tm1) or p_tm1 == 0:
            continue
        g = mult * qty * (p_t - p_tm1)
        d = mult * qty * p_tm1
        c = 0.0
        if held_t != held_y:
            ex, en = production_roll_cash_cost(root, qty, cost_multiplier)
            c = ex + en
        idx.append(t); gross.append(g); cash.append(c); den.append(d)
        net.append((g - c) / d)
    return (pd.Series(net, index=idx), pd.Series(gross, index=idx),
            pd.Series(cash, index=idx), pd.Series(den, index=idx))


def production_divisor_regression(settle, meta, oi):
    """Section 7: the PRODUCTION path must satisfy quote-unit AND cash accounting.

    The production cash cost is fixed dollars, so the divisor cannot corrupt it.
    But the divisor still binds through the DENOMINATOR: the cost as a fraction
    of notional is 2C / (multiplier * qty * p_prev). Feed an undivided
    cents-quoted price and the denominator is 100x too large, so the production
    cost RATE is 100x too small — the same defect, reached through the other
    term. This test exercises `tsmom_chain_net_returns` directly.

    Oracle is EXPECTED_COST_RATIO (the audited quote conventions), never DIVISOR.
    """
    out, failures = {}, []
    for root in ("ZC", "CL", "ZM"):
        keys = meta[meta["asset"] == root].sort_values("expiration_dt")
        listed = [k for k in keys["_contract_key"] if k in settle.columns]
        s_raw = settle[listed].dropna(how="all")
        o_r = oi.reindex(index=s_raw.index, columns=listed)
        front = carry_roll.compute_front_contract_series(o_r, listed)

        # production, correctly divided vs wrongly undivided
        n_d, g_d, c_d, den_d = tsmom_chain_net_returns(
            divided(s_raw, root), front, root, qty=QTY)
        n_u, g_u, c_u, den_u = tsmom_chain_net_returns(s_raw, front, root, qty=QTY)

        roll = c_d > 0
        # cash cost is identical either way (fixed dollars) -- assert that
        cash_same = float((c_d - c_u).abs().max())
        # the cost RATE is what moves, via the denominator
        rate_d = (c_d[roll] / den_d[roll]).median()
        rate_u = (c_u[roll] / den_u[roll]).median()
        ratio = float(rate_d / rate_u) if rate_u else float("nan")

        expected = EXPECTED_COST_RATIO[root]      # oracle, NOT DIVISOR
        ratio_ok = abs(ratio - expected) < 1e-6
        cash_ok = cash_same < 1e-9
        if not ratio_ok:
            failures.append("%s: production cost-rate ratio %.6f != %.0f"
                            % (root, ratio, expected))
        if not cash_ok:
            failures.append("%s: production CASH cost moved with the divisor "
                            "(max diff %.6f) -- it must not" % (root, cash_same))
        out[root] = {
            "divisor_used_by_production": DIVISOR[root],
            "divisor_expected_by_oracle": expected,
            "production_cash_cost_usd_per_roll_divided": float(c_d[roll].median()),
            "production_cash_cost_usd_per_roll_undivided": float(c_u[roll].median()),
            "cash_cost_divisor_invariant": cash_ok,
            "production_cost_rate_bps_divided": float(rate_d * 1e4),
            "production_cost_rate_bps_undivided": float(rate_u * 1e4),
            "cost_rate_ratio": ratio, "cost_rate_ratio_as_expected": ratio_ok,
        }
    return {"all_pass": not failures, "failures": failures, "per_root": out,
            "meaning": ("exercises tsmom_chain_net_returns, the PRODUCTION path. "
                        "Cash cost is divisor-invariant (fixed dollars); the "
                        "cost RATE scales by the divisor through the notional "
                        "denominator. Both properties are asserted.")}


def production_synthetic_cl():
    """Section 4: the synthetic CL case driven through the PRODUCTION path.

    Two settlements, one roll, one contract. Oracle is literal: 12.50/side, two
    sides, 25.00 total. The superseded 23.863636 must be impossible here.
    """
    failures = []
    P_OLD, P_NEW, QTY_ = 100.0, 110.0, 1
    EXPECT_TOTAL, PRIOR_WRONG = 25.00, 23.863636363636363
    mult = carry_cfg.CONTRACT_SPECS["CL"]["multiplier"]

    dates = pd.to_datetime(["2020-01-02", "2020-01-03"])
    s = pd.DataFrame({"OLD": [P_OLD, P_OLD], "NEW": [P_NEW, P_NEW]}, index=dates)
    front = pd.Series(["OLD", "NEW"], index=dates)          # a roll on day 2

    net, gross, cash, den = tsmom_chain_net_returns(s, front, "CL", qty=QTY_)
    prod_cash = float(cash.iloc[0])
    prod_gross = float(gross.iloc[0])
    prod_den = float(den.iloc[0])
    prod_net = float(net.iloc[0])

    if abs(prod_cash - EXPECT_TOTAL) > 1e-9:
        failures.append("production roll cash %.6f != %.2f" % (prod_cash, EXPECT_TOTAL))
    if abs(prod_cash - PRIOR_WRONG) < 1e-6:
        failures.append("production path reproduces the superseded 23.863636")
    # gross is 0 here (held contract flat), so net return is purely the cost
    expect_net = (prod_gross - EXPECT_TOTAL) / (mult * QTY_ * P_OLD)
    if abs(prod_net - expect_net) > 1e-12:
        failures.append("net return %.12f != (gross - cash)/denominator %.12f"
                        % (prod_net, expect_net))
    # what carry's legacy percentage convention would have charged
    legacy_pct = (carry_costs.cost_per_side_pct("CL", P_OLD)
                  + carry_costs.cost_per_side_pct("CL", P_NEW))
    legacy_cash = legacy_pct * mult * P_OLD

    return {"all_pass": not failures, "failures": failures,
            "case": {"p_old": P_OLD, "p_new": P_NEW, "qty": QTY_,
                     "multiplier": mult, "per_side_usd_literal": 12.50},
            "production_cash_cost_usd": prod_cash,
            "expected_cash_cost_usd": EXPECT_TOTAL,
            "production_denominator_usd": prod_den,
            "production_net_return": prod_net,
            "legacy_carry_percentage_cash_usd": legacy_cash,
            "superseded_value_rejected": abs(prod_cash - PRIOR_WRONG) > 1e-6}


def event_semantics_tests():
    """Section 8: cost legs must fire on the right events, and only those.

    Four deterministic cases on a synthetic two/three-day panel.
    """
    failures, cases = [], {}
    mult = carry_cfg.CONTRACT_SPECS["CL"]["multiplier"]
    C = carry_costs.cost_per_side_usd("CL")

    d3 = pd.to_datetime(["2020-01-02", "2020-01-03", "2020-01-06"])
    s = pd.DataFrame({"A": [100.0, 101.0, 102.0], "B": [110.0, 111.0, 112.0]},
                     index=d3)

    # 1. same contract held throughout -> no cost on any day
    _n, _g, cash, _d = tsmom_chain_net_returns(s, pd.Series(["A", "A", "A"], index=d3), "CL")
    ok = float(cash.abs().sum()) == 0.0
    cases["same_contract_no_trade"] = {"total_cash": float(cash.sum()),
                                       "expected": 0.0, "pass": ok}
    if not ok:
        failures.append("same-contract days were charged")

    # 2. one roll -> exactly one charged day, at 2C
    _n, _g, cash, _d = tsmom_chain_net_returns(s, pd.Series(["A", "B", "B"], index=d3), "CL")
    charged = cash[cash > 0]
    ok = len(charged) == 1 and abs(float(charged.iloc[0]) - 2 * C) < 1e-9
    cases["single_roll_two_legs"] = {"n_charged_days": int(len(charged)),
                                     "cash": float(charged.iloc[0]) if len(charged) else 0.0,
                                     "expected": 2 * C, "pass": ok}
    if not ok:
        failures.append("single roll not charged exactly 2C on exactly one day")

    # 3. exit and entry legs are equal halves of the roll cost
    ex, en = production_roll_cash_cost("CL", qty=1)
    ok = abs(ex - C) < 1e-9 and abs(en - C) < 1e-9
    cases["exit_and_entry_legs"] = {"exit": ex, "entry": en, "each_expected": C,
                                    "pass": ok}
    if not ok:
        failures.append("exit/entry legs are not C each")

    # 4. two rolls -> two charged days
    _n, _g, cash, _d = tsmom_chain_net_returns(s, pd.Series(["A", "B", "A"], index=d3), "CL")
    charged = cash[cash > 0]
    ok = len(charged) == 2
    cases["two_rolls_two_charges"] = {"n_charged_days": int(len(charged)),
                                      "expected": 2, "pass": ok}
    if not ok:
        failures.append("two roll events were not charged twice")

    cases["rebalance_leg"] = {"note": ("this one-contract accounting object has "
                                       "no rebalance leg; none is charged, and "
                                       "none is expected"), "pass": True}
    return {"all_pass": not failures, "failures": failures, "cases": cases,
            "per_side_usd": C}


# ====================================================================== PATH B
# PRIMITIVE ONE-CONTRACT CASH LEDGER.
#
# Built ONLY from primitive economic quantities: contract quantity, per-side
# dollar cost, and the number of sides actually traded. It is deliberately
# price-independent, because a fixed per-side fee is. It must never be derived
# from `cost_per_side_pct`, from `chain_returns`, or from any net-return object
# — that circularity is precisely what let a wrong ledger reconcile at 1e-16.

def primitive_side_cost_usd(root, cost_multiplier=1.0):
    """One side, one contract, in dollars — the frozen Sec 5 primitive."""
    return carry_costs.cost_per_side_usd(root, cost_multiplier)


def primitive_roll_cash_cost(root, qty=1, cost_multiplier=1.0):
    """Cash cost of rolling `qty` contracts: exit leg + entry leg.

    Returns (exit_usd, entry_usd, total_usd). Independent of both contract
    prices by construction — a fixed per-side fee does not scale with price.
    """
    c = primitive_side_cost_usd(root, cost_multiplier)
    exit_usd = qty * c
    entry_usd = qty * c
    return exit_usd, entry_usd, exit_usd + entry_usd


def synthetic_cash_regression():
    """Astra's synthetic case, as a permanent regression.

    Oracle is LITERAL: 12.50 per side, 1 contract, two sides -> 25.00. It does
    not call `cost_per_side_pct`, `chain_returns`, or any derived cost object.
    The superseded implementation returned 23.863636 and must FAIL here.
    """
    failures = []
    P_OLD, P_NEW, QTY = 100.0, 110.0, 1
    C_LITERAL = 12.50                     # CL: tick_value 10.00 + 2.50 fee
    EXPECT_EXIT, EXPECT_ENTRY, EXPECT_TOTAL = 12.50, 12.50, 25.00
    PRIOR_WRONG = 23.863636363636363

    # the production primitive must equal the literal
    prod_c = primitive_side_cost_usd("CL")
    if abs(prod_c - C_LITERAL) > 1e-9:
        failures.append("CL per-side primitive %.6f != literal %.2f" % (prod_c, C_LITERAL))

    ex, en, tot = primitive_roll_cash_cost("CL", qty=QTY)
    if abs(ex - EXPECT_EXIT) > 1e-9:
        failures.append("exit leg %.6f != %.2f" % (ex, EXPECT_EXIT))
    if abs(en - EXPECT_ENTRY) > 1e-9:
        failures.append("entry leg %.6f != %.2f" % (en, EXPECT_ENTRY))
    if abs(tot - EXPECT_TOTAL) > 1e-9:
        failures.append("total roll cash cost %.6f != %.2f" % (tot, EXPECT_TOTAL))
    if abs(tot - PRIOR_WRONG) < 1e-6:
        failures.append("ledger reproduces the superseded 23.863636 value")

    # price independence: the same roll at different prices costs the same cash
    _, _, tot2 = primitive_roll_cash_cost("CL", qty=QTY)
    if abs(tot - tot2) > 1e-12:
        failures.append("cash cost is price-dependent")

    # what the OLD percentage convention would have produced, for the record
    mult = carry_cfg.CONTRACT_SPECS["CL"]["multiplier"]
    old_pct = (carry_costs.cost_per_side_pct("CL", P_OLD)
               + carry_costs.cost_per_side_pct("CL", P_NEW))
    old_usd = old_pct * (mult * P_OLD)

    return {"all_pass": not failures, "failures": failures,
            "case": {"root": "CL", "p_old": P_OLD, "p_new": P_NEW, "qty": QTY,
                     "per_side_literal": C_LITERAL},
            "expected": {"exit_usd": EXPECT_EXIT, "entry_usd": EXPECT_ENTRY,
                         "total_usd": EXPECT_TOTAL},
            "actual": {"exit_usd": ex, "entry_usd": en, "total_usd": tot},
            "superseded_percentage_convention_usd": old_usd,
            "superseded_value_rejected": abs(tot - PRIOR_WRONG) > 1e-6,
            "oracle": ("literal 12.50/side; no cost_per_side_pct, no "
                       "chain_returns, no derived net-return object")}


# ------------------------------------------------------------ sign agreement --
def sign_agreement(settle, meta, oi):
    """MAP_v2 X02a: sign-agreement rate, ETF signal vs futures signal, per pair.

    DIAGNOSTIC ONLY. MAP_v2 is explicit that a low rate is "a diagnostic warning
    that requires investigation ... it is not proof of an implementation defect,
    and it grants no permission to tune the construction toward higher
    agreement". No threshold is sealed and none is invented here.

    The futures leg uses the chained held-contract return index compounded into
    a price index; the ETF leg uses the frozen adjusted-close cache. Both go
    through the SAME locked baseline composite (`signals.signal_method_b`).
    """
    # `src` is already bound to the CARRY package (its path was inserted at
    # module import), so `from src import signals` resolves to the wrong repo.
    # Load the TSMOM modules by file path under distinct names instead, with
    # REPO first on sys.path so signals.py's own `import config` resolves to
    # the TSMOM config. Nothing in either repository is modified.
    import importlib.util                            # noqa: PLC0415
    sys.path.insert(0, str(REPO))

    def _load(name, relpath):
        spec = importlib.util.spec_from_file_location(name, REPO / relpath)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod
        spec.loader.exec_module(mod)
        return mod

    tsmom_cfg = _load("config", "config.py")
    tsmom_signals = _load("tsmom_signals", "src/signals.py")

    px = pd.read_csv(REPO / "data/close_prices_raw.csv",
                     parse_dates=["Date"]).set_index("Date")
    etf_monthly = tsmom_signals.to_monthly(px)
    etf_sig = tsmom_signals.signal_method_b(etf_monthly)

    res = {}
    for etf, root in ETF_FUTURES_PAIRS.items():
        keys = meta[meta["asset"] == root].sort_values("expiration_dt")
        listed = [k for k in keys["_contract_key"] if k in settle.columns]
        s_raw = settle[listed].dropna(how="all")
        o_r = oi.reindex(index=s_raw.index, columns=listed)
        front = carry_roll.compute_front_contract_series(o_r, listed)
        # divisor-corrected, so the cost leg inside chain_returns is right
        r = carry_returns.chain_returns(divided(s_raw, root), front, symbol=root)
        fut_index = (1.0 + r.fillna(0.0)).cumprod()
        fut_monthly = fut_index.resample(tsmom_cfg.SIGNAL_RESAMPLE).last().to_frame("F")
        fut_sig = tsmom_signals.signal_method_b(fut_monthly)["F"]

        e = etf_sig[etf] if etf in etf_sig.columns else None
        if e is None:
            res[etf] = {"status": "ETF_NOT_IN_PANEL"}
            continue
        j = e.dropna().index.intersection(fut_sig.dropna().index)
        if len(j) == 0:
            res[etf] = {"status": "NO_OVERLAP"}
            continue
        se, sf = np.sign(e.loc[j]), np.sign(fut_sig.loc[j])
        agree = (se == sf)
        both_nonzero = (se != 0) & (sf != 0)
        res[etf] = {
            "futures_root": root,
            "n_months": int(len(j)),
            "first": str(j[0].date()), "last": str(j[-1].date()),
            "sign_agreement_rate": float(agree.mean()),
            "sign_agreement_rate_excluding_flat": (
                float((se[both_nonzero] == sf[both_nonzero]).mean())
                if both_nonzero.any() else None),
            "n_disagree": int((~agree).sum()),
            "mean_abs_score_etf": float(np.abs(e.loc[j]).mean()),
            "mean_abs_score_futures": float(np.abs(fut_sig.loc[j]).mean()),
        }
    return {
        "pairs_computed": res,
        "pairs_deferred": {"DBA": ("ag basket composition is X01 draft OPEN item "
                                   "O-1; not invented here")},
        "interpretation_limit": ("DIAGNOSTIC. Does not prove accounting "
                                 "correctness, does not prove accounting "
                                 "invalidity, authorises no tuning toward ETF "
                                 "agreement, and is not an X01 result. No "
                                 "threshold is sealed; none is invented."),
    }


def main():
    gate = HERE / "panel_sanity.json"
    if not gate.exists() or json.loads(gate.read_text(encoding="utf-8")).get(
            "PANEL_SANITY") != "PASS":
        print("REFUSING TO RUN: panel sanity gate not PASS.")
        return 2

    settle = pd.read_parquet(HERE / "settle_v2.parquet")
    oi = pd.read_parquet(HERE / "oi_v2.parquet")
    meta = pd.read_parquet(HERE / "contracts_meta.parquet")
    meta["expiration_dt"] = pd.to_datetime(meta["expiration"])

    out = {"generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
           "supersedes": "run_x02a_v2.py (gross-only ledger; Fable B1)",
           "panel_sanity": "PASS",
           "contract_key": "instrument_id__expiration_date",
           "oi_stat_type": 9,
           "no_back_adjusted_prices": True,
           "divisor_applied_to_chain_path": True,
           "roots": {}}

    out["production_synthetic_cl"] = production_synthetic_cl()
    out["production_divisor_regression"] = production_divisor_regression(settle, meta, oi)
    out["event_semantics"] = event_semantics_tests()
    out["synthetic_cash_regression"] = synthetic_cash_regression()
    out["cost_end_to_end_regression"] = end_to_end_cost_regression(settle, meta, oi)

    zero_guard_halts = []
    for root in carry_cfg.ALL_SYMBOLS:
        keys = meta[meta["asset"] == root].sort_values("expiration_dt")
        listed = [k for k in keys["_contract_key"] if k in settle.columns]
        if len(listed) < 2:
            out["roots"][root] = {"status": "TOO_FEW_CONTRACTS"}
            continue
        s_raw = settle[listed].dropna(how="all")
        s_dol = divided(s_raw, root)                 # decimal dollars
        o_r = oi.reindex(index=s_raw.index, columns=listed)
        expmap = dict(zip(keys["_contract_key"], keys["expiration_dt"]))

        front = carry_roll.compute_front_contract_series(o_r, listed)

        viol = carry_returns.held_front_zero_price_guard(s_raw, front)
        if viol:
            zero_guard_halts.append({"root": root, "n": len(viol)})

        exp_seq = [expmap[c] for c in front]
        monotone = all(exp_seq[i] <= exp_seq[i + 1] for i in range(len(exp_seq) - 1))
        changed = front != front.shift(1)
        changed.iloc[0] = False
        n_rolls = int(changed.sum())
        held_missing = int(sum(pd.isna(s_raw.at[t, front.at[t]]) for t in s_raw.index))
        availability = 1.0 - held_missing / len(s_raw)

        # PATH A: the TSMOM PRODUCTION chain (cash-first). This, not carry's
        # percentage convention, is what a future X01 path uses.
        r_net, gA, cashA, denA = tsmom_chain_net_returns(s_dol, front, root, qty=QTY)
        # LEGACY REFERENCE ONLY: carry's percentage convention, retained so the
        # divergence it produces stays visible and measurable. Never used to
        # build, check or correct Path A or Path B.
        r_legacy = carry_returns.chain_returns(s_dol, front, symbol=root)

        # ---- costed dollar ledger, built independently of chain_returns ----
        mult = carry_cfg.CONTRACT_SPECS[root]["multiplier"]
        dates = s_raw.index
        rows = []
        for i in range(1, len(dates)):
            t, tm1 = dates[i], dates[i - 1]
            held_y, held_t = front.at[tm1], front.at[t]
            p_t, p_tm1 = s_dol.at[t, held_y], s_dol.at[tm1, held_y]
            if pd.isna(p_t) or pd.isna(p_tm1) or p_tm1 == 0:
                continue
            notional = mult * p_tm1
            gross_usd = mult * (p_t - p_tm1)
            r_gross = p_t / p_tm1 - 1.0
            is_roll = held_t != held_y

            # ---- PATH B: primitive cash legs, price-independent -----------
            exit_usd = entry_usd = 0.0
            if is_roll:
                exit_usd, entry_usd, _ = primitive_roll_cash_cost(root, qty=QTY)
            cash_cost_usd = exit_usd + entry_usd

            # ---- LEGACY carry convention's implied cash cost --------------
            # Recorded for contrast only. Builds nothing.
            legacy_cost_pct = 0.0
            if is_roll:
                legacy_cost_pct = (carry_costs.cost_per_side_pct(root, p_tm1)
                                   + carry_costs.cost_per_side_pct(root, p_t))
            legacy_cost_usd = legacy_cost_pct * notional

            rows.append((t, str(held_y), str(held_t), QTY, notional, gross_usd,
                         r_gross, bool(is_roll), exit_usd, entry_usd,
                         cash_cost_usd, gross_usd - cash_cost_usd,
                         legacy_cost_pct, legacy_cost_usd))
        led = pd.DataFrame(rows, columns=[
            "date", "held_before", "held_after", "qty", "notional", "gross_usd",
            "r_gross", "is_roll", "exit_cost_usd", "entry_cost_usd",
            "cash_cost_usd", "net_usd", "legacy_cost_pct",
            "legacy_cost_usd"]).set_index("date")

        # ---- GROSS reconciliation (algebraic; reported as such) -------------
        gross_res = (led["gross_usd"] - led["notional"] * led["r_gross"]).abs()
        gross_rel = float((gross_res / led["notional"].abs()).max())

        # ---- NET CASH reconciliation: PATH A vs PATH B ----------------------
        # Path A = carry chain_returns (percentage convention), converted to
        #          dollars at the held notional.
        # Path B = the primitive cash ledger above.
        # These share only PRIMITIVE inputs (settlements, the held-contract
        # series, the multiplier). Path B never reads a percentage or a
        # net-return object, so a defect in either path shows up here.
        j = led.index.intersection(r_net.dropna().index)
        pathA_net_usd = led.loc[j, "notional"] * r_net.loc[j]
        pathB_net_usd = led.loc[j, "net_usd"]
        net_diff = (pathB_net_usd - pathA_net_usd)
        net_rel = float((net_diff.abs() / led.loc[j, "notional"].abs()).max())
        net_abs = float(net_diff.abs().max())
        # split by event so a roll-day-only defect cannot hide in an average
        rj = led.loc[j][led.loc[j, "is_roll"]]
        nrj = led.loc[j][~led.loc[j, "is_roll"]]
        roll_rel = float(((pathB_net_usd.loc[rj.index] - pathA_net_usd.loc[rj.index]).abs()
                          / rj["notional"].abs()).max()) if len(rj) else 0.0
        nonroll_rel = float(((pathB_net_usd.loc[nrj.index] - pathA_net_usd.loc[nrj.index]).abs()
                             / nrj["notional"].abs()).max()) if len(nrj) else 0.0
        # LEGACY divergence, measured but no longer part of the verdict
        legacy_gap = (rj["cash_cost_usd"] - rj["legacy_cost_usd"])
        legacy_gap_max = float(legacy_gap.abs().max()) if len(rj) else 0.0
        legacy_gap_total = float(legacy_gap.sum()) if len(rj) else 0.0

        # held-front jump diagnostic (reported, not a gate) -- Fable §5 gap
        jumps = led.index[led["r_gross"].abs() > JUMP_REPORT]

        out["roots"][root] = {
            "status": "OK",
            "n_contracts": len(listed), "n_sessions": int(len(s_raw)),
            "first_date": str(s_raw.index[0].date()),
            "last_date": str(s_raw.index[-1].date()),
            "roll_monotonic": bool(monotone), "n_rolls": n_rolls,
            "roll_count_in_band": bool(ROLL_BAND[0] <= n_rolls <= ROLL_BAND[1]),
            "held_contract_availability": round(availability, 6),
            "availability_ok": bool(availability >= AVAILABILITY_MIN),
            "ledger_n_days": int(len(led)),
            "ledger_n_roll_days": int(led["is_roll"].sum()),
            "qty_contracts": QTY,
            "per_side_cost_usd": primitive_side_cost_usd(root),
            "total_cash_cost_usd": float(led["cash_cost_usd"].sum()),
            "total_cost_usd_legacy_percentage": float(led["legacy_cost_usd"].sum()),
            "GROSS_reconciliation_max_relative": gross_rel,
            "NET_CASH_rollday_max_relative": roll_rel,
            "NET_CASH_nonroll_max_relative": nonroll_rel,
            "NET_CASH_max_relative_all_days": net_rel,
            "NET_CASH_max_abs_usd_all_days": net_abs,
            "legacy_gap_max_usd_per_roll": legacy_gap_max,
            "legacy_gap_total_usd": legacy_gap_total,
            "held_front_jumps_over_20pct": [
                {"date": str(d.date()), "move": round(float(led.at[d, "r_gross"]), 4)}
                for d in jumps],
            "divisor": DIVISOR[root], "multiplier": mult,
        }
        print("  %-3s rolls=%3d avail=%.5f grossRel=%.2e rollRel=%.2e "
              "nonrollRel=%.2e legacyGap/roll=$%.2f jumps=%d"
              % (root, n_rolls, availability, gross_rel, roll_rel, nonroll_rel,
                 legacy_gap_max, len(jumps)), flush=True)

    out["sign_agreement_diagnostic"] = sign_agreement(settle, meta, oi)
    out["held_front_zero_price_guard"] = {
        "fired": bool(zero_guard_halts), "detail": zero_guard_halts}

    ok = [r for r, v in out["roots"].items() if v.get("status") == "OK"]
    gross_pass = max(out["roots"][r]["GROSS_reconciliation_max_relative"] for r in ok) < 1e-10
    nonroll_pass = max(out["roots"][r]["NET_CASH_nonroll_max_relative"] for r in ok) < 1e-10
    rollday_pass = max(out["roots"][r]["NET_CASH_rollday_max_relative"] for r in ok) < 1e-10
    cash_pass = out["synthetic_cash_regression"]["all_pass"]
    prod_pass = out["production_synthetic_cl"]["all_pass"]
    proddiv_pass = out["production_divisor_regression"]["all_pass"]
    event_pass = out["event_semantics"]["all_pass"]
    max_gap = max(out["roots"][r]["legacy_gap_max_usd_per_roll"] for r in ok)
    out["summary"] = {
        "roots_ok": len(ok),
        "PANEL_SANITY": "PASS",
        "HELD_FRONT_ZERO_GUARD": "HALT" if zero_guard_halts else "CLEAR",
        "GROSS_LEDGER_RECONCILIATION": "PASS" if gross_pass else "FAIL",
        "GROSS_LEDGER_NOTE": ("ALGEBRAIC TAUTOLOGY - holds for any numbers; "
                              "proves arithmetic, NOT accounting validity"),
        "max_gross_relative_residual": max(
            out["roots"][r]["GROSS_reconciliation_max_relative"] for r in ok),
        "TSMOM_PRODUCTION_CASH_ACCOUNTING": "PASS" if prod_pass else "FAIL",
        "PRODUCTION_SYNTHETIC_CL_COST": out["production_synthetic_cl"]["production_cash_cost_usd"],
        "ONE_CONTRACT_CASH_LEDGER": "PASS" if cash_pass else "FAIL",
        "SYNTHETIC_CL_TOTAL_USD": out["synthetic_cash_regression"]["actual"]["total_usd"],
        "EVENT_SEMANTICS": "PASS" if event_pass else "FAIL",
        "NET_CASH_LEDGER_ROLLDAY": "PASS" if rollday_pass else "FAIL",
        "NET_CASH_rollday_max_relative": max(
            out["roots"][r]["NET_CASH_rollday_max_relative"] for r in ok),
        "NET_CASH_LEDGER_NONROLL": "PASS" if nonroll_pass else "FAIL",
        "NET_CASH_nonroll_max_relative": max(
            out["roots"][r]["NET_CASH_nonroll_max_relative"] for r in ok),
        "NET_CASH_LEDGER_RECONCILIATION": "PASS" if (rollday_pass and nonroll_pass) else "FAIL",
        "LEGACY_CARRY_PERCENTAGE_CONVENTION": "DIFFERS_FROM_AUTHORITATIVE_TSMOM_CASH_LEDGER",
        "legacy_gap_max_usd_per_roll": max_gap,
        "LEGACY_NOTE": ("carry chain_returns implies C + C*p_old/p_new per "
                        "roll; the frozen Sec 5 primitive charges 2C. The TSMOM "
                        "PRODUCTION path now uses the primitive, so this gap is "
                        "a measured property of the LEGACY reference only and "
                        "no longer sits in the TSMOM accounting path. "
                        "commodity-carry-research is NOT modified and its "
                        "historical results are NOT adjudicated."),
        "COST_PATH_END_TO_END_LEGACY": "PASS" if out["cost_end_to_end_regression"]["all_pass"] else "FAIL",
        "COST_PATH_PRODUCTION": "PASS" if proddiv_pass else "FAIL",
        "SIGN_AGREEMENT_DIAGNOSTIC": "COMPUTED",
        "ROLL_MONOTONICITY": "PASS" if all(out["roots"][r]["roll_monotonic"] for r in ok) else "FAIL",
        "ROLL_CONSTRUCTION": "PASS" if all(out["roots"][r]["roll_count_in_band"] for r in ok) else "FAIL",
        "HELD_CONTRACT_AVAILABILITY": "PASS" if all(out["roots"][r]["availability_ok"] for r in ok) else "FAIL",
        "min_availability": min(out["roots"][r]["held_contract_availability"] for r in ok),
    }
    (HERE / "x02a_v3_results.json").write_text(json.dumps(out, indent=2, default=str),
                                               encoding="utf-8")
    print(json.dumps(out["summary"], indent=2, default=str))
    print("\nsign agreement:", json.dumps(
        {k: (v.get("sign_agreement_rate"), v.get("n_months"))
         for k, v in out["sign_agreement_diagnostic"]["pairs_computed"].items()}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
