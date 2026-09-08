"""X03 — roll-rule diagnostics, STRUCTURAL / PRE-SEAL PORTION ONLY.

MAP_v2 Cluster C1 §X03, pre-seal clause, verbatim: "Roll dates, roll counts,
open-interest crossover timing and contract availability under the A1 and
calendar rules. **No delta net Sharpe, no PnL correlation, no wrapper-performance
comparison before the X01 seal**".

This script therefore computes NO return series, NO Sharpe, NO PnL and NO
correlation of any performance quantity. It compares two roll rules on
STRUCTURE alone. Nothing here selects a roll rule: A1 stays primary by the
architecture, and a roll rule is never chosen on performance.

The single permitted question:

    Is the roll-rule choice mechanically/materially different enough that it
    must be DECLARED as a design degree of freedom before X01 is sealed?

Comparator rule. The calendar rule used here is a **declared structural
comparator**, fixed ex ante for this diagnostic: roll to the next listed
contract `CALENDAR_LEAD_DAYS` sessions before the held contract's expiry month
begins. It is not tuned, not selected, and no variant of it is searched.

Writes research/extensions/wave1/x03_structural.json.
"""
import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).parent
CARRY = Path(__file__).resolve().parents[3].parent / "commodity-carry-research"
sys.path.insert(0, str(CARRY))
from src import config as carry_cfg          # noqa: E402
from src import roll as carry_roll           # noqa: E402

sys.path.insert(0, str(HERE))
from run_x02a import parse_contract, resolve_expiry   # noqa: E402

CALENDAR_LEAD_DAYS = 5      # declared ex ante for this diagnostic; not searched


def calendar_front(dates, listed, expiries):
    """Front contract under the declared fixed-calendar comparator.

    Hold the earliest-expiring contract whose expiry month starts more than
    CALENDAR_LEAD_DAYS sessions ahead. Monotonic by construction: the index
    into the expiry-ordered sequence never decreases.
    """
    out, idx = [], 0
    for t in dates:
        while idx < len(listed) - 1:
            e = expiries[listed[idx]]
            first_of_expiry_month = dt.date(e.year, e.month, 1)
            if (first_of_expiry_month - t.date()).days <= CALENDAR_LEAD_DAYS:
                idx += 1
            else:
                break
        out.append(listed[idx])
    return pd.Series(out, index=dates, dtype=object)


def main():
    settle = pd.read_parquet(HERE / "settle_panel.parquet")
    oi = pd.read_parquet(HERE / "oi_panel.parquet")
    roots = list(carry_cfg.ALL_SYMBOLS)

    out = {"generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
           "calendar_lead_days": CALENDAR_LEAD_DAYS,
           "scope": ("STRUCTURAL ONLY: roll dates, roll counts, OI crossover "
                     "timing, contract availability, and rule disagreement. "
                     "No return, no Sharpe, no PnL, no performance comparison."),
           "roots": {}}

    for root in roots:
        cols = [c for c in settle.columns
                if (p := parse_contract(c, roots)) is not None and p[0] == root]
        if not cols:
            continue
        s_r = settle[cols].dropna(how="all")
        o_r = oi.reindex(index=s_r.index, columns=cols)

        expiries = {}
        for c in cols:
            _, m, yd = parse_contract(c, roots)
            obs = s_r[c].dropna()
            if obs.empty:
                continue
            e, _gap = resolve_expiry(m, yd, obs.index[-1].date())
            expiries[c] = e
        listed = sorted(expiries, key=lambda c: (expiries[c], c))
        if len(listed) < 2:
            continue
        s_r, o_r = s_r[listed], o_r[listed]

        f_a1 = carry_roll.compute_front_contract_series(o_r, listed)
        f_cal = calendar_front(s_r.index, listed, expiries)

        def roll_stats(f):
            changed = f != f.shift(1)
            changed.iloc[0] = False
            roll_dates = list(f.index[changed])
            dte = []
            for t in roll_dates:
                prev = f.shift(1).at[t]
                e = expiries[prev]
                dte.append((e - t.date()).days)
            return {"n_rolls": int(changed.sum()),
                    "roll_dates_first": str(roll_dates[0].date()) if roll_dates else None,
                    "roll_dates_last": str(roll_dates[-1].date()) if roll_dates else None,
                    "days_to_expiry_at_roll_median": float(np.median(dte)) if dte else None,
                    "days_to_expiry_at_roll_min": int(min(dte)) if dte else None,
                    "days_to_expiry_at_roll_max": int(max(dte)) if dte else None}

        a1s, cals = roll_stats(f_a1), roll_stats(f_cal)

        # contract availability: does the HELD contract have a settlement?
        def availability(f):
            held_missing = 0
            for t in s_r.index:
                if pd.isna(s_r.at[t, f.at[t]]):
                    held_missing += 1
            return {"sessions": int(len(s_r)),
                    "held_contract_missing_settlement": held_missing,
                    "availability_pct": float(100.0 * (1 - held_missing / len(s_r)))}

        # OI crossover timing: first session at which a later contract's t-1 OI
        # exceeds the A1-held contract's, versus the session A1 actually rolls.
        oi_lag = o_r.shift(1)
        lags = []
        pos = {c: i for i, c in enumerate(listed)}
        changed = f_a1 != f_a1.shift(1)
        changed.iloc[0] = False
        for t in f_a1.index[changed]:
            prev = f_a1.shift(1).at[t]
            i0 = pos[prev]
            window = f_a1.index[(f_a1.index <= t)][-120:]
            cross = None
            for u in window:
                row = oi_lag.loc[u].iloc[i0:]
                if row.notna().sum() < 2:
                    continue
                if float(row.iloc[0]) < float(np.nanmax(row.values[1:])):
                    cross = u
                    break
            if cross is not None:
                lags.append((t - cross).days)
        # disagreement between the two rules
        disagree = float((f_a1.values != f_cal.values).mean())

        out["roots"][root] = {
            "n_contracts": len(listed),
            "sessions": int(len(s_r)),
            "A1": {**a1s, **availability(f_a1)},
            "CALENDAR": {**cals, **availability(f_cal)},
            "oi_crossover_to_roll_lag_days": {
                "n": len(lags),
                "median": float(np.median(lags)) if lags else None,
                "p90": float(np.percentile(lags, 90)) if lags else None,
                "max": int(max(lags)) if lags else None},
            "rule_disagreement_session_share": disagree,
        }
        print("  %-3s rolls A1=%3d CAL=%3d  disagree=%.1f%%  avail A1=%.2f%%"
              % (root, a1s["n_rolls"], cals["n_rolls"], 100 * disagree,
                 out["roots"][root]["A1"]["availability_pct"]), flush=True)

    d = [v["rule_disagreement_session_share"] for v in out["roots"].values()]
    ra = [v["A1"]["n_rolls"] for v in out["roots"].values()]
    rc = [v["CALENDAR"]["n_rolls"] for v in out["roots"].values()]
    out["summary"] = {
        "n_roots": len(out["roots"]),
        "disagreement_share_mean": float(np.mean(d)),
        "disagreement_share_min": float(np.min(d)),
        "disagreement_share_max": float(np.max(d)),
        "total_rolls_A1": int(sum(ra)),
        "total_rolls_CALENDAR": int(sum(rc)),
        "roots_with_disagreement_above_10pct": [
            r for r, v in out["roots"].items()
            if v["rule_disagreement_session_share"] > 0.10],
    }
    (HERE / "x03_structural.json").write_text(
        json.dumps(out, indent=2, default=str), encoding="utf-8")
    print(json.dumps(out["summary"], indent=2))


if __name__ == "__main__":
    main()
