"""Step 5 — the reveal: compute portfolio returns and run the full, honest
validation. Reports gross AND net of costs. No parameter is tuned to flatter the
result; a null (CI crossing 0) is reported as plainly as an edge.

Run:  python run_backtest.py
"""

from __future__ import annotations

import datetime as dt

import numpy as np
import pandas as pd

import config
import universe
from src import fetch_data, performance as perf, plots, portfolio, signals, validation


def _fmt_pct(x: float) -> str:
    return "n/a" if pd.isna(x) else f"{x*100:.1f}%"


def _metrics_row(name: str, m: dict) -> list[str]:
    return [name, _fmt_pct(m["ann_return"]), _fmt_pct(m["ann_vol"]),
            f"{m['sharpe']:.2f}", _fmt_pct(m["max_drawdown"]),
            f"{m['calmar']:.2f}" if not pd.isna(m["calmar"]) else "n/a",
            _fmt_pct(m["win_rate"])]


def _md_table(rows, header) -> str:
    h = "| " + " | ".join(header) + " |"
    s = "| " + " | ".join("---" for _ in header) + " |"
    b = "\n".join("| " + " | ".join(str(c) for c in r) + " |" for r in rows)
    return "\n".join([h, s, b])


def main() -> None:
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    prices, _ = fetch_data.fetch_universe(force=False)
    px = prices[universe.TICKERS]

    # ---- portfolio -> returns ----
    port = portfolio.build_portfolio(px, method="B")
    positions = port["position"]                      # held weights (shift(1) of decisions)
    monthly_px = signals.to_monthly(px)
    rets = perf.portfolio_returns(positions, monthly_px, cost_bps=config.TRANSACTION_COST_BPS)

    # HONESTY: evaluate only the period when ALL 17 assets are live. Equal-weight
    # aggregation would otherwise run from 1994 on a smaller, growing universe (SPY/
    # EWJ/XLE/bonds...), which is a DIFFERENT strategy than the locked 17-asset one.
    # The per-asset weight is NaN before an asset has a 12-month signal; the 17 only
    # coexist from ~2008 (UNG inception 2007-04). A return month M is full-universe
    # iff the decision (month M-1) had all 17 weights.
    asset_w = port["asset_weight"]
    full_decision = asset_w.notna().all(axis=1)
    first_full_decision = full_decision[full_decision].index.min()
    rets = rets.loc[rets.index > first_full_decision]
    gross, net = rets["gross"], rets["net"]

    # buy-and-hold benchmark, aligned to the strategy's period
    bh_all = perf.buy_and_hold_returns(monthly_px)
    bh = bh_all.reindex(net.index).dropna()

    # ---- core metrics ----
    m_gross = perf.metrics(gross)
    m_net = perf.metrics(net)
    m_bh = perf.metrics(bh)

    # ---- bootstrap CIs (on net) ----
    ci_sharpe = validation.bootstrap_ci(net, stat="sharpe")
    ci_ann = validation.bootstrap_ci(net, stat="ann_return")

    # ---- regimes & sub-periods ----
    reg_strat = validation.regime_performance(net)
    reg_bh = validation.regime_performance(bh)
    subp = validation.subperiod_performance(net)
    yearly = validation.yearly_returns(net)

    # ---- monte carlo ----
    mc = validation.monte_carlo(net)

    # ---- turnover / cost disclosure ----
    avg_turnover_ann = float(rets["turnover"].mean() * 12)
    cost_drag_ann = m_gross["ann_return"] - m_net["ann_return"]

    # ---- figures ----
    eq_net = perf.equity_curve(net)
    eq_gross = perf.equity_curve(gross)
    eq_bh = perf.equity_curve(bh)
    plots.plot_equity_curves(
        {"TSMOM net": eq_net, "TSMOM gross": eq_gross, "Equal-weight buy&hold": eq_bh},
        config.EQUITY_CURVE_PNG,
        "Multi-asset TSMOM vs equal-weight buy & hold (growth of $1, log)",
    )
    plots.plot_drawdown(perf.drawdown_curve(net), config.DRAWDOWN_PNG,
                        "TSMOM (net) drawdown")
    plots.plot_fan_chart(mc["fan"], config.FAN_CHART_PNG,
                         "Monte Carlo (bootstrap) fan chart — net returns", actual=eq_net)

    # ---- persist returns ----
    out_csv = rets.copy()
    out_csv["buy_hold"] = bh.reindex(out_csv.index)
    out_csv.rename_axis("month_end").round(6).to_csv(config.MONTHLY_RETURNS_CSV)

    _write_report(
        net=net, gross=gross, bh=bh, m_gross=m_gross, m_net=m_net, m_bh=m_bh,
        ci_sharpe=ci_sharpe, ci_ann=ci_ann, reg_strat=reg_strat, reg_bh=reg_bh,
        subp=subp, yearly=yearly, mc=mc, avg_turnover_ann=avg_turnover_ann,
        cost_drag_ann=cost_drag_ann,
    )

    # ---- console ----
    print("\n===================  BACKTEST SUMMARY (net of costs)  ===================")
    print(f"  period: {net.index.min().date()} -> {net.index.max().date()}  ({len(net)} months)")
    print(f"  ann_return={_fmt_pct(m_net['ann_return'])}  ann_vol={_fmt_pct(m_net['ann_vol'])}  "
          f"Sharpe={m_net['sharpe']:.2f}  maxDD={_fmt_pct(m_net['max_drawdown'])}  "
          f"Calmar={m_net['calmar']:.2f}  win={_fmt_pct(m_net['win_rate'])}")
    print(f"  Sharpe 95% CI: [{ci_sharpe['lo']:.2f}, {ci_sharpe['hi']:.2f}]  "
          f"crosses 0: {ci_sharpe['crosses_0']}  (frac>0={ci_sharpe['frac_gt_0']:.3f})")
    print(f"  AnnRet 95% CI: [{_fmt_pct(ci_ann['lo'])}, {_fmt_pct(ci_ann['hi'])}]  "
          f"crosses 0: {ci_ann['crosses_0']}")
    print(f"  buy&hold: Sharpe={m_bh['sharpe']:.2f}  maxDD={_fmt_pct(m_bh['max_drawdown'])}")
    print("  --- regimes (strategy cum return) ---")
    for name in reg_strat.index:
        print(f"    {name:16} strat={_fmt_pct(reg_strat.loc[name,'cum_return']):>8}  "
              f"b&h={_fmt_pct(reg_bh.loc[name,'cum_return']):>8}")
    print(f"  MC bootstrap: P(loss)={mc['stats']['bootstrap']['p_loss']:.3f}  "
          f"P(DD>=20%)={mc['stats']['bootstrap']['p_dd_20']:.3f}  "
          f"P(DD>=30%)={mc['stats']['bootstrap']['p_dd_30']:.3f}")
    print(f"  avg annual turnover={avg_turnover_ann:.1f}x  cost drag={_fmt_pct(cost_drag_ann)}/yr")
    verdict = "EDGE CONFIRMED" if not ci_sharpe["crosses_0"] else "NO CONFIRMABLE EDGE (CI crosses 0)"
    print(f"  VERDICT: {verdict}")
    print(f"  report: {config.BACKTEST_REPORT_MD}")


def _write_report(*, net, gross, bh, m_gross, m_net, m_bh, ci_sharpe, ci_ann,
                  reg_strat, reg_bh, subp, yearly, mc, avg_turnover_ann, cost_drag_ann) -> None:
    L: list[str] = []
    add = L.append
    add("# Backtest & Validation — Multi-Asset TSMOM (equal-weight, vol-targeted)")
    add("")
    add(f"*Generated {dt.datetime.now():%Y-%m-%d %H:%M}. Honest validation — results "
        "reported as-is, no parameter tuning.*")
    add(f"*Return period: **{net.index.min().date()} → {net.index.max().date()}** "
        f"({len(net)} months). rf = {config.RISK_FREE_ANNUAL:.0%} (disclosed).*")
    add("")

    # verdict up top
    edge = not ci_sharpe["crosses_0"]
    add("## TL;DR — does this strategy have a confirmable edge?")
    add("")
    add(f"- **Net Sharpe = {m_net['sharpe']:.2f}**, 95% bootstrap CI "
        f"**[{ci_sharpe['lo']:.2f}, {ci_sharpe['hi']:.2f}]** "
        f"→ **{'DOES NOT cross 0' if edge else 'CROSSES 0'}** "
        f"({ci_sharpe['frac_gt_0']*100:.1f}% of resamples > 0).")
    add(f"- Net annualized return 95% CI: **[{_fmt_pct(ci_ann['lo'])}, {_fmt_pct(ci_ann['hi'])}]** "
        f"→ {'excludes 0' if not ci_ann['crosses_0'] else 'includes 0'}.")
    add(f"- **Verdict: {'a statistically confirmable edge at the 95% level.' if edge else 'NO confirmable edge — the CI crosses 0.'}**")
    add("")

    # costs
    add("## 1. Return calculation & costs")
    add("")
    add("- **Evaluation window = only months when all 17 assets are live** (full universe "
        "with 12-month signals, from ~2008). Earlier months would be a smaller, growing "
        "universe — a different strategy — so they are excluded for an honest read.")
    add("- Monthly return = Σ(position × asset monthly return); **position = portfolio "
        "weight `shift(1)`** (decided the prior month-end → no look-ahead, unit-tested).")
    add(f"- Costs: **{config.TRANSACTION_COST_BPS:.0f} bps one-way × turnover** "
        "(liquid-ETF convention; intra-month drift ignored). Reported gross & net.")
    add(f"- Avg annual turnover ≈ **{avg_turnover_ann:.1f}×**; cost drag ≈ "
        f"**{_fmt_pct(cost_drag_ann)}/yr**.")
    add("")

    # core metrics
    add("## 2. Core performance (gross vs net vs buy&hold)")
    add("")
    header = ["", "ann return", "ann vol", "Sharpe", "max DD", "Calmar", "win rate"]
    rows = [_metrics_row("TSMOM gross", m_gross),
            _metrics_row("TSMOM net", m_net),
            _metrics_row("Equal-wt buy&hold", m_bh)]
    add(_md_table(rows, header))
    add("")

    # bootstrap
    add("## 3. Bootstrap confidence intervals (net, 10,000 resamples)")
    add("")
    add(f"- **Sharpe**: point {ci_sharpe['point']:.2f}, 95% CI "
        f"[{ci_sharpe['lo']:.2f}, {ci_sharpe['hi']:.2f}] — "
        f"**{'crosses 0' if ci_sharpe['crosses_0'] else 'does not cross 0'}**.")
    add(f"- **Annual return**: point {_fmt_pct(ci_ann['point'])}, 95% CI "
        f"[{_fmt_pct(ci_ann['lo'])}, {_fmt_pct(ci_ann['hi'])}] — "
        f"**{'crosses 0' if ci_ann['crosses_0'] else 'does not cross 0'}**.")
    add("")

    # regimes
    add("## 4. Regime attribution (crisis alpha test)")
    add("")
    rr = [[name, reg_strat.loc[name, "months"],
           _fmt_pct(reg_strat.loc[name, "cum_return"]),
           _fmt_pct(reg_bh.loc[name, "cum_return"])]
          for name in reg_strat.index]
    add(_md_table(rr, ["regime", "months", "TSMOM cum return", "buy&hold cum return"]))
    add("")
    add("> Crisis alpha = does the strategy hold up (or profit) when buy&hold is "
        "crashing? Momentum can go short; buy&hold cannot.")
    add("")

    # subperiods
    add("## 5. Walk-forward / sub-period stability (no params fit)")
    add("")
    if not subp.empty:
        sr = [[idx, r["months"], _fmt_pct(r["ann_return"]), f"{r['sharpe']:.2f}",
               _fmt_pct(r["max_drawdown"])] for idx, r in subp.iterrows()]
        add(_md_table(sr, ["period", "months", "ann return", "Sharpe", "max DD"]))
    add("")

    # monte carlo
    add("## 6. Monte Carlo path risk (10,000 paths each)")
    add("")
    for scheme in ("bootstrap", "shuffle"):
        s = mc["stats"][scheme]
        add(f"**{scheme}** — maxDD median {_fmt_pct(s['dd_median'])}, "
            f"5th-pctile {_fmt_pct(s['dd_p95'])}, worst {_fmt_pct(s['dd_worst'])}; "
            f"terminal $1→ median {s['term_median']:.2f} "
            f"(95% [{s['term_lo']:.2f}, {s['term_hi']:.2f}]); "
            f"P(loss)={s['p_loss']*100:.1f}%, P(DD≥20%)={s['p_dd_20']*100:.1f}%, "
            f"P(DD≥30%)={s['p_dd_30']*100:.1f}%.")
        add("")
    add(f"Fan chart: [`{config.FAN_CHART_PNG.name}`]({config.FAN_CHART_PNG.name}).")
    add("")

    # vs buy and hold
    add("## 7. vs Buy & Hold")
    add("")
    add(f"- Sharpe: **TSMOM {m_net['sharpe']:.2f}** vs **buy&hold {m_bh['sharpe']:.2f}**.")
    add(f"- Max drawdown: **TSMOM {_fmt_pct(m_net['max_drawdown'])}** vs "
        f"**buy&hold {_fmt_pct(m_bh['max_drawdown'])}**.")
    add("- Crisis windows (cum return), strategy vs buy&hold: see §4.")
    add(f"- Equity curves: [`{config.EQUITY_CURVE_PNG.name}`]({config.EQUITY_CURVE_PNG.name}); "
        f"drawdown: [`{config.DRAWDOWN_PNG.name}`]({config.DRAWDOWN_PNG.name}).")
    add("> Note: TSMOM is vol-targeted (~10%); buy&hold is unlevered. Sharpe is "
        "scale-free (fair); raw drawdowns also reflect the vol difference.")
    add("")

    # yearly
    add("## 8. Calendar-year net returns")
    add("")
    yr = [[int(y), _fmt_pct(v)] for y, v in yearly.items()]
    add(_md_table(yr, ["year", "net return"]))
    add("")

    config.BACKTEST_REPORT_MD.write_text("\n".join(L), encoding="utf-8")


if __name__ == "__main__":
    main()
