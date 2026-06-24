"""Signal sanity check — print momentum signal directions for the final 17 at a
few representative month-ends, for manual review. No backtest, no performance.

For each chosen month-end we show every asset's per-horizon momentum sign
(1/3/6/12m), Method A (12m), and Method B composite (mean + vote). The signal at
month-end M is what would drive the position held during month M+1 (no look-ahead).

Usage:  python check_signals.py
"""

from __future__ import annotations

import numpy as np
import pandas as pd

import config
import universe
from src import fetch_data, signals

# Representative month-ends: 2008 GFC, 2020 COVID, and a calm bull month.
CHECK_MONTHS = {
    "2008-10": "GFC crash (post-Lehman) — expect equities short, Treasuries long",
    "2020-03": "COVID crash — expect equities short, Treasuries/USD bid",
    "2017-06": "calm bull market — expect equities long, low-vol drift",
}

SIGN_TXT = {1.0: "+1 long", -1.0: "-1 short", 0.0: " 0 flat"}


def _fmt_sign(v) -> str:
    if pd.isna(v):
        return " –"
    return SIGN_TXT.get(float(v), f"{v:+.2f}")


def _row_for_month(monthly: pd.DataFrame, per_horizon: dict, a12, b_mean, b_vote,
                   target: pd.Timestamp, ticker: str) -> list[str]:
    s = {n: per_horizon[n].at[target, ticker] for n in config.MOMENTUM_LOOKBACKS_MONTHS}
    return [
        ticker,
        universe.FINAL_UNIVERSE[ticker],
        _fmt_sign(s[1]), _fmt_sign(s[3]), _fmt_sign(s[6]), _fmt_sign(s[12]),
        _fmt_sign(a12.at[target, ticker]),
        (f"{b_mean.at[target, ticker]:+.2f}" if pd.notna(b_mean.at[target, ticker]) else " –"),
        _fmt_sign(b_vote.at[target, ticker]),
    ]


def _match_month_end(index: pd.DatetimeIndex, ym: str) -> pd.Timestamp:
    period = pd.Period(ym, freq="M")
    hits = [d for d in index if d.to_period("M") == period]
    if not hits:
        raise KeyError(f"No month-end in signal index for {ym}")
    return hits[0]


def main() -> None:
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    prices, _ = fetch_data.fetch_universe(force=False)
    tickers = universe.TICKERS
    px = prices[tickers]

    # ---- window confirmation ----
    aligned = px.dropna(how="any")
    start, end = aligned.index.min(), aligned.index.max()
    starts = {t: px[t].dropna().index.min() for t in tickers}
    binding = max(starts, key=lambda k: starts[k])
    covers_2008 = start <= pd.Timestamp("2008-09-15")
    covers_2020 = start <= pd.Timestamp("2020-02-19")

    # ---- signals ----
    monthly = signals.to_monthly(px)
    per_horizon = {n: np.sign(signals.momentum_return(monthly, n))
                   for n in config.MOMENTUM_LOOKBACKS_MONTHS}
    a12 = signals.signal_method_a(monthly, lookback_months=config.MOMENTUM_LOOKBACK_A)
    b_mean = signals.signal_method_b(monthly, combine="mean")
    b_vote = signals.signal_method_b(monthly, combine="vote")

    ordered = [t for grp in universe.GROUPS.values() for t in grp]
    header = ["ticker", "factor", "1m", "3m", "6m", "12m", "A(12m)", "B mean", "B vote"]

    L: list[str] = []
    add = L.append
    add("# Signal Sanity Check — final 17-asset universe")
    add("")
    add("*Scope: signal generation only (no sizing, no returns, no performance).*")
    add("")
    add("## Data window")
    add(f"- Common window: **{start.date()} → {end.date()}** "
        f"({len(aligned)} trading days), bound by `{binding}` ({starts[binding].date()})")
    add(f"- Covers 2008 GFC? **{'YES' if covers_2008 else 'NO'}**  |  "
        f"Covers 2020 COVID? **{'YES' if covers_2020 else 'NO'}**")
    add("")
    add("## Conventions")
    add("- Signal at month-end **M** drives the position held during month **M+1** "
        "(`positions = signal.shift(1)`) — no look-ahead.")
    add(f"- Method B = mean of the {list(config.MOMENTUM_LOOKBACKS_MONTHS)}-month "
        "momentum signs; `mean` ∈ [-1,+1] (agreement strength), `vote` = majority {-1,0,+1}.")
    add("- `+1 long`, `-1 short`, `0 flat`, `–` = insufficient history.")
    add("")

    print(f"[window] {start.date()} -> {end.date()} ({len(aligned)} days), "
          f"binding {binding}; covers 2008={covers_2008}, 2020={covers_2020}")

    for ym, note in CHECK_MONTHS.items():
        target = _match_month_end(monthly.index, ym)
        holding = (target + pd.offsets.MonthEnd(1)).strftime("%Y-%m")
        add(f"## Signal as of {target.date()} → drives positions held in {holding}")
        add(f"*{note}*")
        add("")
        rows = [_row_for_month(monthly, per_horizon, a12, b_mean, b_vote, target, t)
                for t in ordered]
        add("| " + " | ".join(header) + " |")
        add("| " + " | ".join("---" for _ in header) + " |")
        for r in rows:
            add("| " + " | ".join(r) + " |")
        add("")

        print(f"\n=== signals as of {target.date()} ({note.split(' — ')[0]}) ===")
        print(f"{'ticker':6} {'factor':26} {'1m':>7}{'3m':>8}{'6m':>8}{'12m':>8}"
              f"{'A12':>9}{'Bmean':>8}{'Bvote':>9}")
        for r in rows:
            print(f"{r[0]:6} {r[1]:26} {r[2]:>7}{r[3]:>8}{r[4]:>8}{r[5]:>8}"
                  f"{r[6]:>9}{r[7]:>8}{r[8]:>9}")

    out = config.OUTPUT_DIR / "signal_check.md"
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"\n[written] {out}")


if __name__ == "__main__":
    main()
