"""Sizing sanity check — for representative month-ends, show each asset's signal,
estimated annualized volatility, and final volatility-scaled position weight.

Rows are sorted by volatility so the inverse-vol relationship is visible at a
glance: low-vol assets (SHY) should get large weights, high-vol assets (USO,
UNG) small ones. Also exports the full monthly weight panel.

No portfolio aggregation, no returns, no performance — per-asset sizing only.

Usage:  python check_sizing.py
"""

from __future__ import annotations

import pandas as pd

import config
import universe
from src import fetch_data, signals, sizing

CHECK_MONTHS = {
    "2008-10": "GFC crash — risk assets volatile (big vol => small weight)",
    "2020-03": "COVID crash — vol spike across the board",
    "2017-06": "calm bull market — low vol, larger weights",
}


def _match_month_end(index: pd.DatetimeIndex, ym: str) -> pd.Timestamp:
    period = pd.Period(ym, freq="M")
    hits = [d for d in index if d.to_period("M") == period]
    if not hits:
        raise KeyError(f"No month-end in index for {ym}")
    return hits[0]


def _dir(v) -> str:
    if pd.isna(v):
        return "–"
    if v > 0:
        return "long"
    if v < 0:
        return "short"
    return "flat"


def main() -> None:
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    prices, _ = fetch_data.fetch_universe(force=False)
    px = prices[universe.TICKERS]

    out = sizing.build_position_sizes(px, method="B")
    sig, vol, weight = out["signal"], out["vol"], out["weight"]

    # full weight panel export
    panel = weight.copy().round(4)
    panel.index.name = "month_end"
    panel.to_csv(config.MONTHLY_WEIGHTS_PANEL_CSV)

    tgt, cap = config.TARGET_VOL_ANNUAL, config.MAX_ASSET_WEIGHT

    L: list[str] = []
    add = L.append
    add("# Sizing Sanity Check — volatility-scaled per-asset weights (final 17)")
    add("")
    add("*Scope: per-asset position sizing only. No portfolio risk control, no returns.*")
    add("")
    add("## Convention & parameters (conventional, NOT optimized)")
    add(f"- `weight = clip( signal × target_vol / asset_vol , ±{cap:.1f} )`")
    add(f"- **Vol window** = {config.VOL_WINDOW_DAYS} trading days (~3 months), "
        "rolling std of daily returns, annualized ×√252.")
    add(f"- **Target vol** = {tgt:.0%} annualized per asset.")
    add(f"- **Per-asset cap** = ±{cap:.1f} (leverage guardrail for ultra-low-vol assets).")
    add(f"- `signal` = Method B composite ([-1,+1]); vol & signal both as of the "
        "month-end shown, so the weight drives the *next* month's position (no look-ahead).")
    add("- `tgt/σ` = target_vol / asset_vol (capped) = size a full ±1 signal would get; "
        "`*` marks where the cap binds.")
    add("")

    print(f"[params] vol_window={config.VOL_WINDOW_DAYS}d, target_vol={tgt:.0%}, cap=+/-{cap:.1f}")

    header = ["ticker", "factor", "signal", "dir", "ann σ %", "tgt/σ", "weight"]
    for ym, note in CHECK_MONTHS.items():
        target = _match_month_end(vol.index, ym)
        rows = []
        for t in universe.TICKERS:
            v = vol.at[target, t]
            s = sig.at[target, t]
            w = weight.at[target, t]
            scalar = (tgt / v) if (pd.notna(v) and v > 0) else float("nan")
            capped = pd.notna(scalar) and scalar > cap
            size = min(scalar, cap) if pd.notna(scalar) else float("nan")
            rows.append({
                "ticker": t,
                "factor": universe.FINAL_UNIVERSE[t],
                "signal": s,
                "dir": _dir(s),
                "ann_vol": v,
                "size": size,
                "capped": capped,
                "weight": w,
            })
        # sort by volatility ascending -> low vol (big weight) on top
        rows = sorted(rows, key=lambda r: (pd.isna(r["ann_vol"]), r["ann_vol"]))

        holding = (target + pd.offsets.MonthEnd(1)).strftime("%Y-%m")
        add(f"## As of {target.date()} → sizes positions for {holding}")
        add(f"*{note}*")
        add("")
        add("| " + " | ".join(header) + " |")
        add("| " + " | ".join("---" for _ in header) + " |")
        print(f"\n=== sizing as of {target.date()} ({note.split(' — ')[0]}) ===")
        print(f"{'ticker':6}{'factor':26}{'signal':>8}{'dir':>7}{'annvol%':>8}{'tgt/vol':>9}{'weight':>9}")
        for r in rows:
            sig_s = f"{r['signal']:+.2f}" if pd.notna(r["signal"]) else "–"
            volp = f"{r['ann_vol']*100:.1f}" if pd.notna(r["ann_vol"]) else "–"
            size_s = (f"{r['size']:.2f}{'*' if r['capped'] else ''}"
                      if pd.notna(r["size"]) else "–")
            w_s = f"{r['weight']:+.2f}" if pd.notna(r["weight"]) else "–"
            add(f"| `{r['ticker']}` | {r['factor']} | {sig_s} | {r['dir']} | {volp} | "
                f"{size_s} | {w_s} |")
            print(f"{r['ticker']:6}{r['factor']:26}{sig_s:>8}{r['dir']:>7}{volp:>8}"
                  f"{size_s:>8}{w_s:>9}")
        add("")

    config.SIZING_CHECK_MD.write_text("\n".join(L), encoding="utf-8")
    print(f"\n[written] {config.MONTHLY_WEIGHTS_PANEL_CSV}")
    print(f"[written] {config.SIZING_CHECK_MD}")


if __name__ == "__main__":
    main()
