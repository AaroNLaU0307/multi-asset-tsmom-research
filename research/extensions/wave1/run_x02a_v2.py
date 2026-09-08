"""X02a v2 — futures mechanical / accounting truth on PERSISTENT contract keys.

Supersedes `run_x02a.py`, which ran on raw-symbol panels and is INVALID.

MECHANICAL / IMPLEMENTATION TRUTH ONLY. This does not answer whether futures
TSMOM is profitable and computes NO strategy-performance metric: no Sharpe, no
portfolio return, no wrapper comparison, no candidate selection. The one-contract
return series built here is an ACCOUNTING OBJECT used to test an identity.

ORDERING IS LOAD-BEARING. `panel_sanity.py` must PASS before any identity below
is treated as meaningful. The identity is algebraic and held at 1.21e-16 on the
previous, nonsense panels; it is necessary and nowhere near sufficient. This
script refuses to run unless the gate has passed.

NO BACK-ADJUSTED PRICES ANYWHERE IN THE PnL PATH. Every dollar figure is
`multiplier * (settle_t(held) - settle_{t-1}(held)) / divisor` on ONE held
contract, and roll legs are charged as costs. No continuous or ratio-adjusted
series is constructed, spliced or differenced. Program v2 §X02: "Back-adjusted
prices never manufacture traded PnL."

PRICE UNITS. `costs.cost_per_side_pct` divides by `settle * multiplier` with no
price-unit divisor; for the eight cents-quoted roots that understates cost 100x.
The divisor is applied at this program's boundary. The carry repo is unmodified.

Writes research/extensions/wave1/x02a_v2_results.json.
"""
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).parent
CARRY = Path(__file__).resolve().parents[3].parent / "commodity-carry-research"
sys.path.insert(0, str(CARRY))
from src import config as carry_cfg          # noqa: E402
from src import costs as carry_costs         # noqa: E402
from src import roll as carry_roll           # noqa: E402
from src import returns as carry_returns     # noqa: E402

ZERO_GUARD_HALTS = []   # populated by the held-front zero/negative-price guard

CENTS_QUOTED = {"ZC", "ZS", "ZW", "KE", "ZL", "LE", "HE", "GF"}
DIVISOR = {r: (100.0 if r in CENTS_QUOTED else 1.0) for r in carry_cfg.ALL_SYMBOLS}

# A roll every month would be ~192 over the panel; a quarterly-cycle root ~64.
# Outside this band the front series is not credible and is reported as such.
ROLL_BAND = (25, 260)
AVAILABILITY_MIN = 0.95        # held contract must have a settlement


def cost_regression_tests():
    """Unit/cost regression: cents-quoted vs decimal-dollar roots.

    Asserts (a) the spec table is internally consistent in decimal dollars,
    (b) applying the divisor changes cost by exactly 100x for the eight
    cents-quoted roots and not at all for the other ten.
    """
    LVL = {"CL": 70.0, "HO": 2.3, "RB": 2.2, "NG": 3.5, "GC": 1800.0,
           "SI": 25.0, "HG": 3.5, "PL": 1000.0, "PA": 1200.0, "ZC": 500.0,
           "ZS": 1200.0, "ZW": 650.0, "ZM": 350.0, "ZL": 45.0, "KE": 650.0,
           "LE": 140.0, "HE": 85.0, "GF": 180.0}
    rows, failures = {}, []
    for r in carry_cfg.ALL_SYMBOLS:
        spec = carry_cfg.CONTRACT_SPECS[r]
        implied = spec["tick_size"] * spec["multiplier"]
        spec_ok = abs(implied - spec["tick_value"]) < 1e-9
        div = DIVISOR[r]
        raw = carry_costs.cost_per_side_pct(r, LVL[r]) * 1e4
        corr = carry_costs.cost_per_side_pct(r, LVL[r] / div) * 1e4
        ratio = corr / raw if raw else float("nan")
        expect = 100.0 if r in CENTS_QUOTED else 1.0
        ratio_ok = abs(ratio - expect) < 1e-6
        if not spec_ok:
            failures.append("%s: tick_size*multiplier != tick_value" % r)
        if not ratio_ok:
            failures.append("%s: divisor ratio %.4f != %.0f" % (r, ratio, expect))
        rows[r] = {"divisor": div, "cost_bps_uncorrected": round(raw, 4),
                   "cost_bps_corrected": round(corr, 4),
                   "ratio": round(ratio, 4), "expected_ratio": expect,
                   "spec_identity_holds": spec_ok, "ratio_as_expected": ratio_ok}
    return {"all_pass": not failures, "failures": failures, "per_root": rows,
            "n_cents_quoted": len(CENTS_QUOTED)}


def main():
    gate = HERE / "panel_sanity.json"
    if not gate.exists():
        print("REFUSING TO RUN: panel_sanity.json absent. Run panel_sanity.py first.")
        return 2
    sanity = json.loads(gate.read_text(encoding="utf-8"))
    if sanity.get("PANEL_SANITY") != "PASS":
        print("REFUSING TO RUN: PANEL_SANITY=%s. The accounting identity is "
              "algebraic and would pass on invalid panels."
              % sanity.get("PANEL_SANITY"))
        return 2

    settle = pd.read_parquet(HERE / "settle_v2.parquet")
    oi = pd.read_parquet(HERE / "oi_v2.parquet")
    meta = pd.read_parquet(HERE / "contracts_meta.parquet")
    meta["expiration_dt"] = pd.to_datetime(meta["expiration"])

    out = {"generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
           "panel_sanity": sanity.get("PANEL_SANITY"),
           "contract_key": "instrument_id__expiration_date",
           "oi_stat_type": 9,
           "no_back_adjusted_prices": True,
           "divisor_applied": DIVISOR,
           "cost_unit_regression": cost_regression_tests(),
           "roots": {}}

    for root in carry_cfg.ALL_SYMBOLS:
        keys = meta[meta["asset"] == root].sort_values("expiration_dt")
        listed = [k for k in keys["_contract_key"] if k in settle.columns]
        if len(listed) < 2:
            out["roots"][root] = {"status": "TOO_FEW_CONTRACTS", "n": len(listed)}
            continue
        s_r = settle[listed].dropna(how="all")
        o_r = oi.reindex(index=s_r.index, columns=listed)
        expmap = dict(zip(keys["_contract_key"], keys["expiration_dt"]))

        front = carry_roll.compute_front_contract_series(o_r, listed)

        # CANONICAL HALT GUARD, reused verbatim from the carry study:
        # `returns.held_front_zero_price_guard` -- if the contract actually
        # HELD ever has a settlement <= 0, the pipeline must halt rather than
        # divide through it. This is the correct locus for the non-positive
        # settlements the panel gate reports (8,631 zeros, 4 negatives): they
        # only matter when held. A fired guard is recorded, never swallowed.
        violations = carry_returns.held_front_zero_price_guard(s_r, front)
        if violations:
            ZERO_GUARD_HALTS.append(
                {"root": root, "n": len(violations),
                 "examples": [{"date": str(d.date()), "contract": c,
                               "price": float(p)} for d, c, p in violations[:5]]})

        exp_seq = [expmap[c] for c in front]
        monotone = all(exp_seq[i] <= exp_seq[i + 1] for i in range(len(exp_seq) - 1))
        changed = front != front.shift(1)
        changed.iloc[0] = False
        n_rolls = int(changed.sum())

        held_missing = int(sum(pd.isna(s_r.at[t, front.at[t]]) for t in s_r.index))
        availability = 1.0 - held_missing / len(s_r)

        r_chain = carry_returns.chain_returns(s_r, front, symbol=root)

        div, mult = DIVISOR[root], carry_cfg.CONTRACT_SPECS[root]["multiplier"]
        dates = s_r.index
        pnl, notl, rg, res = [], [], [], []
        for i in range(1, len(dates)):
            t, tm1 = dates[i], dates[i - 1]
            held = front.at[tm1]
            p_t, p_tm1 = s_r.at[t, held], s_r.at[tm1, held]
            if pd.isna(p_t) or pd.isna(p_tm1) or p_tm1 == 0:
                continue
            pnl_usd = mult * (p_t - p_tm1) / div
            notional = mult * p_tm1 / div
            r = p_t / p_tm1 - 1.0
            pnl.append(pnl_usd); notl.append(notional); rg.append(r)
            res.append(pnl_usd - notional * r)
        res = np.asarray(res); notl_a = np.asarray(notl)
        rel = float(np.max(np.abs(res) / np.where(notl_a == 0, np.nan, np.abs(notl_a)))) \
            if len(res) else None

        cut = max(2, len(s_r) - 250)
        front_tr = carry_roll.compute_front_contract_series(o_r.iloc[:cut], listed)
        ov = front.index[:cut]
        trunc_mm = int((front.loc[ov].values != front_tr.loc[ov].values).sum())
        r_tr = carry_returns.chain_returns(s_r.iloc[:cut], front_tr, symbol=root)
        common = r_chain.index.intersection(r_tr.index)
        r_diff = float((r_chain.loc[common] - r_tr.loc[common]).abs().max()) \
            if len(common) else None

        out["roots"][root] = {
            "status": "OK",
            "n_contracts": len(listed),
            "n_sessions": int(len(s_r)),
            "first_date": str(s_r.index[0].date()),
            "last_date": str(s_r.index[-1].date()),
            "roll_monotonic": bool(monotone),
            "n_rolls": n_rolls,
            "roll_count_in_band": bool(ROLL_BAND[0] <= n_rolls <= ROLL_BAND[1]),
            "held_contract_availability": round(availability, 6),
            "availability_ok": bool(availability >= AVAILABILITY_MIN),
            "ledger_n_days": int(len(res)),
            "reconciliation_max_relative_residual": rel,
            "truncation_front_mismatches": trunc_mm,
            "truncation_return_max_abs_diff": r_diff,
            "divisor": div, "multiplier": mult,
            "median_notional_usd": float(np.median(notl_a)) if len(notl_a) else None,
        }
        print("  %-3s ctr=%3d rolls=%3d mono=%s avail=%.4f recon=%.2e trunc=%d"
              % (root, len(listed), n_rolls, monotone, availability,
                 rel if rel else float("nan"), trunc_mm), flush=True)

    ok = [r for r, v in out["roots"].items() if v.get("status") == "OK"]
    identity_ok = (not ZERO_GUARD_HALTS
                   and all(out["roots"][r]["roll_monotonic"] for r in ok)
                   and all(out["roots"][r]["truncation_front_mismatches"] == 0 for r in ok)
                   and max(out["roots"][r]["reconciliation_max_relative_residual"]
                           for r in ok) < 1e-10)
    construction_ok = (all(out["roots"][r]["roll_count_in_band"] for r in ok)
                       and all(out["roots"][r]["availability_ok"] for r in ok))
    out["held_front_zero_price_guard"] = {
        "fired": bool(ZERO_GUARD_HALTS),
        "roots_affected": [h["root"] for h in ZERO_GUARD_HALTS],
        "detail": ZERO_GUARD_HALTS,
        "rule": ("carry returns.held_front_zero_price_guard: a settlement <= 0 "
                 "on the HELD front contract is a HALT, not something to mark "
                 "past silently"),
    }
    out["summary"] = {
        "roots_ok": len(ok),
        "HELD_FRONT_ZERO_GUARD": "HALT" if ZERO_GUARD_HALTS else "CLEAR",
        "PANEL_SANITY": sanity.get("PANEL_SANITY"),
        "roll_counts": {r: out["roots"][r]["n_rolls"] for r in ok},
        "all_roll_counts_in_band": all(out["roots"][r]["roll_count_in_band"] for r in ok),
        "min_availability": min(out["roots"][r]["held_contract_availability"] for r in ok),
        "all_availability_ok": all(out["roots"][r]["availability_ok"] for r in ok),
        "all_roll_monotonic": all(out["roots"][r]["roll_monotonic"] for r in ok),
        "all_truncation_invariant": all(
            out["roots"][r]["truncation_front_mismatches"] == 0 for r in ok),
        "max_relative_reconciliation_residual": max(
            out["roots"][r]["reconciliation_max_relative_residual"] for r in ok),
        "COST_UNIT_REGRESSION": "PASS" if out["cost_unit_regression"]["all_pass"] else "FAIL",
        "ROLL_CONSTRUCTION": "PASS" if construction_ok else "FAIL",
        "ACCOUNTING_IDENTITY": "PASS" if identity_ok else "FAIL",
    }
    (HERE / "x02a_v2_results.json").write_text(json.dumps(out, indent=2, default=str),
                                               encoding="utf-8")
    print(json.dumps(out["summary"], indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
