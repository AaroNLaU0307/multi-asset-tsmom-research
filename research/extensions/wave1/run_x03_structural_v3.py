"""X03 v3 — structural roll-rule diagnostics on the AUTHORITATIVE comparator.

Supersedes `run_x03_structural_v2.py`. Fable
`TSMOM-EXT-FABLE-W1-FUTURES-INFRA-01` §8 found its comparator both
mis-described and not the accepted rule:

  * it rolled when `(expiration - t).days <= 5` — five CALENDAR days, while the
    docstring and the truth document said "5 sessions";
  * it was not the carry-accepted fixed-calendar rule that MAP_v2 §X03 anchors
    the roll-rule question on;
  * it rolled into the next LISTED month regardless of liquidity, so it walked
    through dead serial months — which is why metals showed 98–100%;
  * and it differed from the v1 comparator (5 days before the first of the
    expiry MONTH) without that re-specification being disclosed.

AUTHORITATIVE COMPARATOR, read from the source rather than inferred:
`commodity-carry-research/src/robustness.py::fixed_calendar_front_series`,
specified in carry `DEVIATIONS.md` 2026-07-16 (§8 item 7):

    roll timing   = the last business day of the month PRECEDING the front
                    contract's expiry month (parameter-free; no N to tune)
    candidate     = the A2 existence filter — earliest-expiration outright with
                    expiration > incumbent's AND open interest at t-1 strictly
                    positive
    OI lag        = t-1 throughout (`oi_panel.shift(1)`); no look-ahead

That function is called directly, unmodified. The carry repository is not
edited.

The naive five-calendar-day comparator is ALSO reported, labelled
NON-AUTHORITATIVE, because Fable established that the disagreement magnitude is
comparator-dependent (≈64% naive vs ≈48% carry-accepted) and the record must
carry both rather than quietly swapping one number for another.

STRUCTURAL ONLY. No return series, no Sharpe, no PnL, no correlation of any
performance quantity, and no roll-rule selection. A1 remains primary.

Requires panel_sanity.json = PASS.
Writes research/extensions/wave1/x03_structural_v3.json.
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
from src import config as carry_cfg              # noqa: E402
from src import roll as carry_roll               # noqa: E402
from src import robustness as carry_robustness   # noqa: E402

NAIVE_LEAD_CALENDAR_DAYS = 5     # non-authoritative; retained for continuity


def naive_calendar_front(dates, listed, expmap):
    """The v2 comparator, retained ONLY for continuity of the record.

    Rolls `NAIVE_LEAD_CALENDAR_DAYS` CALENDAR days before the expiration date,
    into the next LISTED contract regardless of liquidity. Explicitly labelled
    non-authoritative: it walks through dead serial months.
    """
    out, idx = [], 0
    for t in dates:
        while idx < len(listed) - 1:
            if (expmap[listed[idx]].date() - t.date()).days <= NAIVE_LEAD_CALENDAR_DAYS:
                idx += 1
            else:
                break
        out.append(listed[idx])
    return pd.Series(out, index=dates, dtype=object)


def roll_stats(f, s_r, expmap):
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

    out = {
        "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "supersedes": "run_x03_structural_v2.py (naive 5-calendar-day comparator)",
        "authoritative_comparator": {
            "source": "commodity-carry-research/src/robustness.py::fixed_calendar_front_series",
            "specification": "carry DEVIATIONS.md 2026-07-16, PREREGISTRATION §8 item 7",
            "roll_timing": "last business day of the month preceding the expiry month",
            "candidate_selection": "A2 existence filter: earliest later expiration with OI at t-1 > 0",
            "free_parameters": "none",
            "oi_lag": "t-1 (oi_panel.shift(1))",
        },
        "non_authoritative_comparator": {
            "rule": "roll %d CALENDAR days before the expiration date, into the "
                    "next LISTED contract regardless of liquidity"
                    % NAIVE_LEAD_CALENDAR_DAYS,
            "why_reported": ("Fable §8 established the disagreement magnitude is "
                             "comparator-dependent; both are recorded rather "
                             "than silently swapping one number for the other"),
            "why_not_authoritative": ("walks through dead serial months, which "
                                      "is what drove the metals to 98-100%"),
        },
        "scope": ("STRUCTURAL ONLY: roll dates, counts, days-to-expiry, "
                  "availability, rule disagreement. No return, no Sharpe, no "
                  "PnL, no performance comparison, no roll-rule selection."),
        "roots": {},
    }

    for root in carry_cfg.ALL_SYMBOLS:
        keys = meta[meta["asset"] == root].sort_values("expiration_dt")
        listed = [k for k in keys["_contract_key"] if k in settle.columns]
        if len(listed) < 2:
            continue
        s_r = settle[listed].dropna(how="all")
        o_r = oi.reindex(index=s_r.index, columns=listed)
        expmap = dict(zip(keys["_contract_key"], keys["expiration_dt"]))

        f_a1 = carry_roll.compute_front_contract_series(o_r, listed)
        f_auth = carry_robustness.fixed_calendar_front_series(o_r, listed, expmap)
        f_naive = naive_calendar_front(s_r.index, listed, expmap)

        d_auth = float((f_a1.values != f_auth.values).mean())
        d_naive = float((f_a1.values != f_naive.values).mean())

        out["roots"][root] = {
            "n_contracts": len(listed), "sessions": int(len(s_r)),
            "A1": roll_stats(f_a1, s_r, expmap),
            "AUTHORITATIVE_CALENDAR": roll_stats(f_auth, s_r, expmap),
            "NAIVE_CALENDAR": roll_stats(f_naive, s_r, expmap),
            "disagreement_A1_vs_AUTHORITATIVE": d_auth,
            "disagreement_A1_vs_NAIVE": d_naive,
        }
        print("  %-3s A1=%3d AUTH=%3d NAIVE=%3d | disagree AUTH=%5.1f%% NAIVE=%5.1f%%"
              % (root, out["roots"][root]["A1"]["n_rolls"],
                 out["roots"][root]["AUTHORITATIVE_CALENDAR"]["n_rolls"],
                 out["roots"][root]["NAIVE_CALENDAR"]["n_rolls"],
                 100 * d_auth, 100 * d_naive), flush=True)

    da = [v["disagreement_A1_vs_AUTHORITATIVE"] for v in out["roots"].values()]
    dn = [v["disagreement_A1_vs_NAIVE"] for v in out["roots"].values()]
    below = [r for r, v in out["roots"].items()
             if v["disagreement_A1_vs_AUTHORITATIVE"] <= 0.10]
    out["summary"] = {
        "n_roots": len(out["roots"]),
        "AUTHORITATIVE_disagreement_mean": float(np.mean(da)),
        "AUTHORITATIVE_disagreement_median": float(np.median(da)),
        "AUTHORITATIVE_disagreement_min": float(np.min(da)),
        "AUTHORITATIVE_disagreement_max": float(np.max(da)),
        "AUTHORITATIVE_min_root": min(out["roots"], key=lambda r:
                                      out["roots"][r]["disagreement_A1_vs_AUTHORITATIVE"]),
        "AUTHORITATIVE_max_root": max(out["roots"], key=lambda r:
                                      out["roots"][r]["disagreement_A1_vs_AUTHORITATIVE"]),
        "NAIVE_disagreement_mean": float(np.mean(dn)),
        "all_roots_above_10pct_AUTHORITATIVE": not below,
        "roots_at_or_below_10pct": below,
        "total_rolls_A1": int(sum(v["A1"]["n_rolls"] for v in out["roots"].values())),
        "total_rolls_AUTHORITATIVE": int(sum(
            v["AUTHORITATIVE_CALENDAR"]["n_rolls"] for v in out["roots"].values())),
        "STRUCTURAL_DOF_REQUIRED": True,
        "ECONOMIC_MATERIALITY": "UNRESOLVED",
        "materiality_note": ("Structural non-equivalence is established under "
                            "BOTH comparators. No margin was sealed and no "
                            "performance quantity was computed, so economic "
                            "materiality is UNRESOLVED and is the X01 S2 "
                            "secondary arm's question. Structural disagreement "
                            "does NOT imply an economically meaningful "
                            "performance difference."),
    }
    (HERE / "x03_structural_v3.json").write_text(
        json.dumps(out, indent=2, default=str), encoding="utf-8")
    print(json.dumps(out["summary"], indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
