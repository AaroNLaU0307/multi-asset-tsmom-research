"""Portfolio sanity check — for representative month-ends, show the portfolio's
leverage, gross/net exposure, and net long/short by factor group. Exports the
monthly portfolio-weight panel and a risk panel.

No returns / Sharpe / drawdown — risk control & exposures only (step 5 does P&L).

Usage:  python check_portfolio.py
"""

from __future__ import annotations

import pandas as pd

import config
import universe
from src import fetch_data, portfolio

CHECK_MONTHS = {
    "2008-10": "GFC crash — expect short risk assets, long havens, LOW leverage",
    "2020-03": "COVID crash — expect short risk assets, long havens, LOW leverage",
    "2017-06": "calm bull — expect long risk assets, HIGHER leverage (maybe capped)",
}


def _match_month_end(index: pd.DatetimeIndex, ym: str) -> pd.Timestamp:
    period = pd.Period(ym, freq="M")
    hits = [d for d in index if d.to_period("M") == period]
    if not hits:
        raise KeyError(f"No month-end in index for {ym}")
    return hits[0]


def _dir(v: float) -> str:
    if pd.isna(v) or abs(v) < 1e-9:
        return "flat"
    return "net long" if v > 0 else "net short"


def main() -> None:
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    prices, _ = fetch_data.fetch_universe(force=False)
    px = prices[universe.TICKERS]

    out = portfolio.build_portfolio(px, method="B")
    pw = out["port_weight"]

    # ---- export panels ----
    pw.round(4).rename_axis("month_end").to_csv(config.PORT_WEIGHTS_PANEL_CSV)
    risk = pd.DataFrame({
        "n_available": out["n_available"],
        "gross_base": out["gross_base"].round(4),
        "port_vol_annual": out["port_vol"].round(4),
        "leverage_raw": out["leverage_raw"].round(4),
        "leverage": out["leverage"].round(4),
        "cap_binds": out["cap_binds"],
        "gross": out["gross"].round(4),
        "net": out["net"].round(4),
    }).rename_axis("month_end")
    risk.to_csv(config.PORT_RISK_PANEL_CSV)

    tv, cap = config.PORT_TARGET_VOL_ANNUAL, config.MAX_GROSS_LEVERAGE

    L: list[str] = []
    add = L.append
    add("# Portfolio Check — equal-weight aggregation + vol targeting (final 17)")
    add("")
    add("*Scope: portfolio weights & risk control only. No returns/Sharpe/drawdown (step 5).*")
    add("")
    add("## Method & parameters (conventional, NOT optimized)")
    add("- **Aggregation:** equal-weight average of the 17 per-asset vol-scaled weights "
        "(`base = Σ wᵢ / N_available`; NaN weight = not in book).")
    add(f"- **Portfolio vol target:** {tv:.0%} annualized. "
        "`leverage = target / realized_port_vol`.")
    add(f"- **Realized port vol:** rolling std of the *base* (unlevered) portfolio's daily "
        f"returns, {config.PORT_VOL_WINDOW_DAYS}-day window, annualized ×√252, backward-only.")
    add(f"- **Gross-leverage cap:** Σ|weights| ≤ {cap:.1f} (safety valve vs over-levering in calm).")
    add("- No covariance/risk-parity optimization (estimation error, unstable crisis "
        "correlations); risk parity left as an optional later benchmark.")
    add("")

    print(f"[params] port_target_vol={tv:.0%}, vol_window={config.PORT_VOL_WINDOW_DAYS}d, "
          f"max_gross={cap:.1f}")

    for ym, note in CHECK_MONTHS.items():
        t = _match_month_end(pw.index, ym)
        pv = out["port_vol"].at[t]
        lev = out["leverage"].at[t]
        lev_raw = out["leverage_raw"].at[t]
        capped = bool(out["cap_binds"].at[t])
        gross = out["gross"].at[t]
        net = out["net"].at[t]
        navail = int(out["n_available"].at[t])
        holding = (t + pd.offsets.MonthEnd(1)).strftime("%Y-%m")

        add(f"## As of {t.date()} → sizes the portfolio held in {holding}")
        add(f"*{note}*")
        add("")
        add(f"- **Realized port vol (est):** {pv*100:.1f}%  → "
            f"**leverage = {lev_raw:.2f} (raw) → {lev:.2f} (applied)**"
            f"{'  ⚠ GROSS CAP BINDS' if capped else ''}")
        add(f"- **Gross notional:** {gross:.2f}×   **Net exposure:** {net:+.2f}   "
            f"(live assets: {navail}/17)")
        add("")
        add("| factor group | net exposure | gross | direction |")
        add("| --- | --- | --- | --- |")
        rows_print = []
        for grp, members in universe.GROUPS.items():
            g_net = float(pw.loc[t, members].sum())
            g_gross = float(pw.loc[t, members].abs().sum())
            add(f"| {grp} | {g_net:+.2f} | {g_gross:.2f} | {_dir(g_net)} |")
            rows_print.append((grp, g_net, g_gross))
        add("")

        print(f"\n=== {t.date()} ({note.split(' — ')[0]}) ===")
        print(f"  port_vol={pv*100:5.1f}%  leverage={lev_raw:5.2f}->{lev:4.2f}"
              f"{'  [CAP]' if capped else ''}  gross={gross:4.2f}  net={net:+5.2f}  N={navail}")
        for grp, g_net, g_gross in rows_print:
            print(f"    {grp:12} net={g_net:+6.2f}  gross={g_gross:5.2f}  {_dir(g_net)}")

    config.PORTFOLIO_CHECK_MD.write_text("\n".join(L), encoding="utf-8")
    print(f"\n[written] {config.PORT_WEIGHTS_PANEL_CSV}")
    print(f"[written] {config.PORT_RISK_PANEL_CSV}")
    print(f"[written] {config.PORTFOLIO_CHECK_MD}")


if __name__ == "__main__":
    main()
