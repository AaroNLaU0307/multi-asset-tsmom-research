"""X03 v2 — roll-rule diagnostics, STRUCTURAL / PRE-SEAL ONLY.

Supersedes `run_x03_structural.py`. That run reported 100% A1-vs-calendar
disagreement, which was an ARTEFACT of a stuck A1 series on raw-symbol panels,
not a structural finding. It is INVALID and superseded; it is not evidence.

MAP_v2 Cluster C1 §X03 pre-seal clause: "Roll dates, roll counts, open-interest
crossover timing and contract availability under the A1 and calendar rules. No
delta net Sharpe, no PnL correlation, no wrapper-performance comparison before
the X01 seal."

So: NO return series, NO Sharpe, NO PnL, NO correlation of any performance
quantity, and NO roll-rule selection. A1 remains primary by the architecture.

The single permitted question:

    Is the roll-rule choice mechanically/materially different enough that it
    must be DECLARED as a preregistered design degree of freedom for X01?

COMPARATOR. The calendar rule is a declared structural comparator, fixed ex
ante and not searched: roll out of the held contract `CALENDAR_LEAD_DAYS`
sessions before its expiration date. Expiration is now authoritative (from the
definition schema), so no expiry heuristic is involved.

Requires panel_sanity.json = PASS.

Writes research/extensions/wave1/x03_structural_v2.json.
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

CALENDAR_LEAD_DAYS = 5      # declared ex ante; not searched, not tuned


def calendar_front(dates, listed, expmap):
    """Monotonic fixed-calendar front: leave a contract LEAD sessions before
    its expiration date."""
    out, idx = [], 0
    for t in dates:
        while idx < len(listed) - 1:
            e = expmap[listed[idx]]
            if (e.date() - t.date()).days <= CALENDAR_LEAD_DAYS:
                idx += 1
            else:
                break
        out.append(listed[idx])
    return pd.Series(out, index=dates, dtype=object)


def main():
    gate = HERE / "panel_sanity.json"
    if not gate.exists() or json.loads(gate.read_text(encoding="utf-8")).get(
            "PANEL_SANITY") != "PASS":
        print("REFUSING TO RUN: panel sanity gate not PASS.")
        return 2

    settle = pd.read_parquet(HERE / "settle_v2.parquet")
    oi = pd.read_parquet(HERE / "oi_v2.parquet")
    meta = pd.read_parquet(HERE / "contracts_meta.parquet")
    meta["expiration_dt"] = pd.to_datetime(meta["expiration"]).dt.tz_localize(None)

    out = {"generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
           "calendar_lead_days": CALENDAR_LEAD_DAYS,
           "supersedes": "run_x03_structural.py (raw-symbol panels, INVALID)",
           "scope": ("STRUCTURAL ONLY: roll dates, counts, OI crossover timing, "
                     "availability, rule disagreement. No return, no Sharpe, no "
                     "PnL, no performance comparison, no roll-rule selection."),
           "roots": {}}

    for root in carry_cfg.ALL_SYMBOLS:
        keys = meta[meta["asset"] == root].sort_values("expiration_dt")
        listed = [k for k in keys["_contract_key"] if k in settle.columns]
        if len(listed) < 2:
            continue
        s_r = settle[listed].dropna(how="all")
        o_r = oi.reindex(index=s_r.index, columns=listed)
        expmap = dict(zip(keys["_contract_key"], keys["expiration_dt"]))

        f_a1 = carry_roll.compute_front_contract_series(o_r, listed)
        f_cal = calendar_front(s_r.index, listed, expmap)

        def stats(f):
            ch = f != f.shift(1)
            ch.iloc[0] = False
            rd = list(f.index[ch])
            dte = [(expmap[f.shift(1).at[t]].date() - t.date()).days for t in rd]
            miss = int(sum(pd.isna(s_r.at[t, f.at[t]]) for t in s_r.index))
            return {"n_rolls": int(ch.sum()),
                    "days_to_expiry_at_roll_median": float(np.median(dte)) if dte else None,
                    "days_to_expiry_at_roll_p10": float(np.percentile(dte, 10)) if dte else None,
                    "days_to_expiry_at_roll_p90": float(np.percentile(dte, 90)) if dte else None,
                    "held_missing_settlement": miss,
                    "availability": round(1.0 - miss / len(s_r), 6)}

        a1s, cals = stats(f_a1), stats(f_cal)

        # OI crossover timing: sessions between the first t-1 OI crossover and
        # the A1 roll that follows it.
        oi_lag = o_r.shift(1)
        pos = {c: i for i, c in enumerate(listed)}
        ch = f_a1 != f_a1.shift(1)
        ch.iloc[0] = False
        lags = []
        for t in f_a1.index[ch]:
            prev = f_a1.shift(1).at[t]
            i0 = pos[prev]
            window = f_a1.index[f_a1.index <= t][-120:]
            for u in window:
                row = oi_lag.loc[u].iloc[i0:]
                if row.notna().sum() < 2:
                    continue
                if float(row.iloc[0]) < float(np.nanmax(row.values[1:])):
                    lags.append((t - u).days)
                    break

        # structural difference: share of sessions the two rules hold different
        # contracts, and how far apart in the expiry sequence they are
        diff_mask = f_a1.values != f_cal.values
        gap = [abs(pos[a] - pos[b]) for a, b in zip(f_a1.values, f_cal.values)]
        out["roots"][root] = {
            "n_contracts": len(listed), "sessions": int(len(s_r)),
            "A1": a1s, "CALENDAR": cals,
            "oi_crossover_to_roll_lag_days": {
                "n": len(lags),
                "median": float(np.median(lags)) if lags else None,
                "p90": float(np.percentile(lags, 90)) if lags else None},
            "rule_disagreement_session_share": float(diff_mask.mean()),
            "expiry_sequence_gap_when_disagreeing": {
                "mean": float(np.mean([g for g in gap if g > 0])) if any(gap) else 0.0,
                "max": int(max(gap)) if gap else 0},
        }
        print("  %-3s rollsA1=%3d rollsCAL=%3d disagree=%5.1f%% availA1=%.4f"
              % (root, a1s["n_rolls"], cals["n_rolls"],
                 100 * out["roots"][root]["rule_disagreement_session_share"],
                 a1s["availability"]), flush=True)

    d = [v["rule_disagreement_session_share"] for v in out["roots"].values()]
    out["summary"] = {
        "n_roots": len(out["roots"]),
        "disagreement_share_mean": float(np.mean(d)),
        "disagreement_share_median": float(np.median(d)),
        "disagreement_share_min": float(np.min(d)),
        "disagreement_share_max": float(np.max(d)),
        "total_rolls_A1": int(sum(v["A1"]["n_rolls"] for v in out["roots"].values())),
        "total_rolls_CALENDAR": int(sum(v["CALENDAR"]["n_rolls"] for v in out["roots"].values())),
        "roots_disagreeing_over_10pct_of_sessions": [
            r for r, v in out["roots"].items()
            if v["rule_disagreement_session_share"] > 0.10],
        "min_availability_A1": min(v["A1"]["availability"] for v in out["roots"].values()),
    }
    (HERE / "x03_structural_v2.json").write_text(
        json.dumps(out, indent=2, default=str), encoding="utf-8")
    print(json.dumps(out["summary"], indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
