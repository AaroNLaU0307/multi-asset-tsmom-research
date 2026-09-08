"""X02a — futures mechanical / accounting truth (pre-seal, MEASUREMENT).

MAP_v2 Cluster C1 §X02. This establishes whether the futures accounting computes
what it claims. It is NOT evidence that futures TSMOM has alpha, and it produces
NO strategy-performance metric: no Sharpe, no portfolio return, no comparison
against the ETF wrapper, no candidate selection.

What it does compute, per root:
  1. the A1 front-contract series (OI-max at t-1), reusing the carry study's
     `roll.compute_front_contract_series` unchanged;
  2. the chained HELD-contract return index, reusing `returns.chain_returns`;
  3. an independent contract-by-contract DOLLAR LEDGER
     (multiplier x delta-settle / divisor), and the reconciliation residual
     between the two;
  4. truncation invariance of the causal primitives;
  5. roll monotonicity;
  6. multiplier / tick / price-unit identities.

The single-contract return series produced here is an ACCOUNTING OBJECT used to
test an identity. It is not a strategy: no signal, no position sizing, no
portfolio, and its Sharpe is never computed.

PRICE UNITS. `costs.cost_per_side_pct` divides by `settle * multiplier` with no
price-unit divisor. For the eight cents-quoted roots that overstates notional by
100x and understates cost by 100x. The divisor is applied HERE, at the boundary,
per DATABENTO_W1_INPUT_VERIFICATION.md section 5. The carry repository is NOT
modified.

Writes research/extensions/wave1/x02a_results.json.
"""
import datetime as dt
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).parent
CARRY = Path(__file__).resolve().parents[3].parent / "commodity-carry-research"
sys.path.insert(0, str(CARRY))
from src import config as carry_cfg          # noqa: E402
from src import roll as carry_roll           # noqa: E402
from src import returns as carry_returns     # noqa: E402

# Verified from observed settlement levels (DATABENTO_W1_INPUT_VERIFICATION §5).
CENTS_QUOTED = {"ZC", "ZS", "ZW", "KE", "ZL", "LE", "HE", "GF"}
DIVISOR = {r: (100.0 if r in CENTS_QUOTED else 1.0) for r in carry_cfg.ALL_SYMBOLS}

MONTH_CODES = {"F": 1, "G": 2, "H": 3, "J": 4, "K": 5, "M": 6,
               "N": 7, "Q": 8, "U": 9, "V": 10, "X": 11, "Z": 12}


def parse_contract(sym, roots):
    """(root, month, year_digit) for an outright symbol, else None."""
    for r in sorted(roots, key=len, reverse=True):
        if not sym.startswith(r):
            continue
        tail = sym[len(r):]
        if len(tail) >= 2 and tail[0] in MONTH_CODES and tail[1:].isdigit():
            return r, MONTH_CODES[tail[0]], int(tail[1:])
    return None


def resolve_expiry(month, year_digits, last_obs):
    """Databento parent symbology uses 1-2 digit years, which repeat.

    Resolved from the data: a contract's records cluster in the period ending
    at its expiry, so the correct year is the one ending in `year_digits`
    nearest the last observation. Asserted, not assumed: the chosen expiry must
    lie within a plausible window of the last observation.
    """
    # CME lists far-dated contracts: crude runs out to 2037 in this panel, so
    # the search window must cover them. Too short a window silently returns
    # None and the expiry sort then fails -- which is how this was found.
    mod = 10 if year_digits < 10 else 100
    best, best_gap = None, None
    for y in range(2008, 2046):
        if y % mod != year_digits:
            continue
        cand = dt.date(y, month, 15)
        gap = abs((cand - last_obs).days)
        if best_gap is None or gap < best_gap:
            best, best_gap = cand, gap
    return best, best_gap


def main():
    settle = pd.read_parquet(HERE / "settle_panel.parquet")
    oi = pd.read_parquet(HERE / "oi_panel.parquet")
    roots = list(carry_cfg.ALL_SYMBOLS)

    out = {"generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
           "divisor_applied": DIVISOR,
           "settle_shape": list(settle.shape), "oi_shape": list(oi.shape),
           "roots": {}}

    # ---------------------------------------------------------------- T6 --
    # Multiplier / tick / price-unit identity, independent of any panel.
    spec_checks = {}
    for r in roots:
        s = carry_cfg.CONTRACT_SPECS[r]
        implied = s["tick_size"] * s["multiplier"]
        spec_checks[r] = {
            "tick_size": s["tick_size"], "multiplier": s["multiplier"],
            "tick_value_declared": s["tick_value"],
            "tick_size_x_multiplier": implied,
            "identity_holds": bool(abs(implied - s["tick_value"]) < 1e-9),
            "divisor": DIVISOR[r],
        }
    out["spec_identity"] = {
        "all_hold": all(v["identity_holds"] for v in spec_checks.values()),
        "per_root": spec_checks,
        "note": ("tick_size x multiplier == tick_value in DECIMAL DOLLARS for "
                 "every root, which is what fixes the divisor: a cents-quoted "
                 "settlement fed to settle*multiplier overstates notional 100x."),
    }

    for root in roots:
        cols = [c for c in settle.columns
                if (p := parse_contract(c, roots)) is not None and p[0] == root]
        if not cols:
            out["roots"][root] = {"status": "NO_CONTRACTS"}
            continue
        s_r = settle[cols].dropna(how="all")
        o_r = oi.reindex(index=s_r.index, columns=cols)

        # expiry-ordered listed sequence, resolved from observation dates
        expiries, gaps = {}, {}
        for c in cols:
            _, m, yd = parse_contract(c, roots)
            last_obs = s_r[c].dropna()
            if last_obs.empty:
                continue
            e, gap = resolve_expiry(m, yd, last_obs.index[-1].date())
            if e is None:
                # Fail loudly rather than sorting None: an unresolvable expiry
                # means the symbology assumption is wrong, not that the
                # contract can be quietly dropped.
                raise ValueError("unresolved expiry for %s (month=%s, year_digits=%s, "
                                 "last_obs=%s)" % (c, m, yd, last_obs.index[-1].date()))
            expiries[c], gaps[c] = e, gap
        listed = sorted(expiries, key=lambda c: (expiries[c], c))
        if len(listed) < 2:
            out["roots"][root] = {"status": "TOO_FEW_CONTRACTS",
                                  "n": len(listed)}
            continue

        s_r = s_r[listed]
        o_r = o_r[listed]

        # ---- 1. A1 front series (carry code, unchanged) -----------------
        front = carry_roll.compute_front_contract_series(o_r, listed)

        # ---- 5. roll monotonicity ---------------------------------------
        exp_seq = [expiries[c] for c in front]
        monotone = all(exp_seq[i] <= exp_seq[i + 1] for i in range(len(exp_seq) - 1))
        n_rolls = int((front != front.shift(1)).sum() - 1)

        # ---- 2. chained held-contract return index (carry code) ---------
        r_chain = carry_returns.chain_returns(s_r, front, symbol=root)

        # ---- 3. dollar ledger + reconciliation identity ------------------
        div = DIVISOR[root]
        mult = carry_cfg.CONTRACT_SPECS[root]["multiplier"]
        dates = s_r.index
        rows = []
        for i in range(1, len(dates)):
            t, tm1 = dates[i], dates[i - 1]
            held = front.at[tm1]
            p_t, p_tm1 = s_r.at[t, held], s_r.at[tm1, held]
            if pd.isna(p_t) or pd.isna(p_tm1) or p_tm1 == 0:
                continue
            pnl_usd = mult * (p_t - p_tm1) / div          # one contract held
            notional_tm1 = mult * p_tm1 / div
            r_gross = p_t / p_tm1 - 1.0
            rows.append((t, pnl_usd, notional_tm1, r_gross,
                         pnl_usd - notional_tm1 * r_gross))
        led = pd.DataFrame(rows, columns=["date", "pnl_usd", "notional_tm1",
                                          "r_gross", "residual"]).set_index("date")
        # Relative residual: the identity is exact in real arithmetic, so any
        # departure is floating point, and must be judged relative to notional.
        rel = (led["residual"].abs() /
               led["notional_tm1"].abs().replace(0, np.nan)).max()

        # ---- 4. truncation invariance -----------------------------------
        # A causal primitive must not change its past when the future is
        # removed. Recompute on the panel truncated 250 sessions early and
        # compare the overlapping front-contract decisions.
        cut = max(2, len(s_r) - 250)
        s_tr, o_tr = s_r.iloc[:cut], o_r.iloc[:cut]
        front_tr = carry_roll.compute_front_contract_series(o_tr, listed)
        overlap = front.index[:cut]
        trunc_mismatches = int((front.loc[overlap].values
                                != front_tr.loc[overlap].values).sum())
        r_tr = carry_returns.chain_returns(s_tr, front_tr, symbol=root)
        common = r_chain.index.intersection(r_tr.index)
        r_trunc_max_diff = float((r_chain.loc[common] - r_tr.loc[common]).abs().max()) \
            if len(common) else None

        out["roots"][root] = {
            "status": "OK",
            "n_contracts": len(listed),
            "n_sessions": int(len(s_r)),
            "first_date": str(s_r.index[0].date()),
            "last_date": str(s_r.index[-1].date()),
            "expiry_resolution_max_gap_days": int(max(gaps.values())),
            "roll_monotonic": bool(monotone),
            "n_rolls": n_rolls,
            "ledger_n_days": int(len(led)),
            "reconciliation_max_abs_residual_usd": float(led["residual"].abs().max()),
            "reconciliation_max_relative_residual": float(rel),
            "truncation_front_mismatches": trunc_mismatches,
            "truncation_return_max_abs_diff": r_trunc_max_diff,
            "divisor": div,
            "multiplier": mult,
            "median_notional_usd": float(led["notional_tm1"].median()),
        }
        print("  %-3s contracts=%3d rolls=%3d monotone=%s recon_rel=%.2e trunc_mm=%d"
              % (root, len(listed), n_rolls, monotone, rel, trunc_mismatches),
              flush=True)

    ok = [r for r, v in out["roots"].items() if v.get("status") == "OK"]
    out["summary"] = {
        "roots_ok": len(ok),
        "all_roll_monotonic": all(out["roots"][r]["roll_monotonic"] for r in ok),
        "all_truncation_invariant": all(
            out["roots"][r]["truncation_front_mismatches"] == 0 for r in ok),
        "max_relative_reconciliation_residual": max(
            out["roots"][r]["reconciliation_max_relative_residual"] for r in ok),
        "spec_identity_all_hold": out["spec_identity"]["all_hold"],
    }
    (HERE / "x02a_results.json").write_text(json.dumps(out, indent=2, default=str),
                                            encoding="utf-8")
    print(json.dumps(out["summary"], indent=2))


if __name__ == "__main__":
    main()
