"""Risk-parity CONTROL experiment: equal-weight vs inverse-volatility vs full
risk parity (ERC, covariance-based) aggregation — same signals, same window, same
costs, same portfolio vol target + leverage cap. Only the cross-asset risk
allocation differs.

This is a scientific control, NOT a search for a better strategy. The main
strategy stays equal-weight regardless of the outcome. We report honestly whether
the more complex schemes beat, tie, or lose to equal-weight.

Run:  python rp_comparison.py
"""

from __future__ import annotations

import datetime as dt

import numpy as np
import pandas as pd

import config
import universe
from src import fetch_data, performance as perf, plots, portfolio, signals, validation

AGGS = {
    "Equal-weight (MAIN)": "equal_weight",
    "Inverse-vol": "inverse_vol",
    "Risk parity (ERC)": "risk_parity",
}
HEADLINE_BPS = 5.0   # realistic blended ETF cost for the headline comparison


def _fmt_pct(x):
    return "n/a" if pd.isna(x) else f"{x*100:.1f}%"


def main():
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    prices, _ = fetch_data.fetch_universe(force=False)
    px = prices[universe.TICKERS]
    mpx = signals.to_monthly(px)

    builds = {name: portfolio.build_portfolio(px, method="B", agg=agg) for name, agg in AGGS.items()}

    # common full-universe window: all 17 signals ready (shared) AND ERC cov ready.
    aw = builds["Equal-weight (MAIN)"]["asset_weight"]
    fd = aw.notna().all(axis=1)
    ew_start = fd[fd].index.min()
    rp_fd = builds["Risk parity (ERC)"]["base_weight"].notna().all(axis=1)
    rp_start = rp_fd[rp_fd].index.min()
    first_full = max(ew_start, rp_start)

    rets = {}
    for name, b in builds.items():
        r = perf.portfolio_returns(b["position"], mpx, cost_bps=0.0)
        rets[name] = r.loc[r.index > first_full]
    common = rets["Equal-weight (MAIN)"].index
    for r in rets.values():
        common = common.intersection(r.index)

    # net series at each cost
    def net(name, bps):
        r = rets[name].loc[common]
        return r["gross"] - r["turnover"] * (bps / 1e4)

    rows = []
    cis = {}
    regimes = {}
    subp = {}
    turn = {}
    for name in AGGS:
        m5 = perf.metrics(net(name, HEADLINE_BPS))
        cis[name] = validation.bootstrap_ci(net(name, HEADLINE_BPS), "sharpe")
        regimes[name] = validation.regime_performance(net(name, HEADLINE_BPS))
        subp[name] = validation.subperiod_performance(net(name, HEADLINE_BPS))["sharpe"]
        turn[name] = float(rets[name].loc[common, "turnover"].mean() * 12)
        rows.append({
            "method": name,
            "sharpe_2bps": perf.sharpe_ratio(net(name, 2.0)),
            "sharpe_5bps": m5["sharpe"],
            "sharpe_10bps": perf.sharpe_ratio(net(name, 10.0)),
            "ann_return_5bps": m5["ann_return"],
            "ann_vol": m5["ann_vol"],
            "max_dd": m5["max_drawdown"],
            "calmar": m5["calmar"],
            "win_rate": m5["win_rate"],
            "turnover_ann": turn[name],
            "ci_lo": cis[name]["lo"],
            "ci_hi": cis[name]["hi"],
            "crosses_0": cis[name]["crosses_0"],
        })
    comp = pd.DataFrame(rows).set_index("method")
    comp.round(4).to_csv(config.RP_COMPARISON_CSV)

    # equity curves (net @ headline cost)
    curves = {name: perf.equity_curve(net(name, HEADLINE_BPS)) for name in AGGS}
    plots.plot_equity_curves(curves, config.RP_EQUITY_PNG,
                             f"Aggregation control: equal-weight vs inverse-vol vs risk parity "
                             f"(net @ {HEADLINE_BPS:.0f}bps, log)")

    _report(comp, cis, regimes, subp, common, first_full)

    # console
    print(f"\n=== RISK-PARITY CONTROL ({common.min().date()} -> {common.max().date()}, "
          f"{len(common)} months, net @ {HEADLINE_BPS:.0f}bps) ===")
    print(f"{'method':22}{'Sh@2':>7}{'Sh@5':>7}{'Sh@10':>7}{'maxDD':>8}{'turn':>7}  CI@5bps")
    for name in AGGS:
        r = comp.loc[name]
        print(f"{name:22}{r['sharpe_2bps']:>7.2f}{r['sharpe_5bps']:>7.2f}{r['sharpe_10bps']:>7.2f}"
              f"{_fmt_pct(r['max_dd']):>8}{r['turnover_ann']:>6.1f}x  "
              f"[{r['ci_lo']:.2f},{r['ci_hi']:.2f}] cross0={r['crosses_0']}")
    print("  crisis alpha (cum return @5bps):")
    for reg in regimes["Equal-weight (MAIN)"].index:
        line = f"    {reg:16}"
        for name in AGGS:
            line += f" {name.split()[0][:4]}={_fmt_pct(regimes[name].loc[reg,'cum_return']):>7}"
        print(line)
    print(f"  report: {config.RP_REPORT_MD}")


def _t(rows, header):
    h = "| " + " | ".join(header) + " |"
    s = "| " + " | ".join("---" for _ in header) + " |"
    b = "\n".join("| " + " | ".join(str(c) for c in r) + " |" for r in rows)
    return "\n".join([h, s, b])


def _report(comp, cis, regimes, subp, common, first_full):
    ew, iv, rp = "Equal-weight (MAIN)", "Inverse-vol", "Risk parity (ERC)"
    L = []
    a = L.append
    a("# Risk-Parity Control Experiment — Aggregation Comparison")
    a("")
    a(f"*Generated {dt.datetime.now():%Y-%m-%d %H:%M}. A scientific CONTROL — the main "
      "strategy stays equal-weight; this only tests whether complex risk allocation beats it.*")
    a(f"*Common window {common.min().date()} → {common.max().date()} ({len(common)} months), "
      f"net of {HEADLINE_BPS:.0f} bps, identical signals/vol-target/cap. Only the 17-asset "
      "aggregation differs.*")
    a("")
    a("## Methods")
    a("- **Equal-weight (MAIN):** average of the per-asset vol-scaled weights (each ~10% vol). "
      "Ignores correlations; already a naive risk parity.")
    a("- **Inverse-vol:** weight ∝ signal / vol (equal standalone risk). Ignores correlations.")
    a(f"- **Risk parity (ERC):** covariance-based equal risk contribution, {config.RP_COV_WINDOW_DAYS}"
      "-day rolling covariance. Accounts for correlations — the 'complex' option; needs a noisier, "
      "longer-window covariance estimate.")
    a("")

    a("## Headline comparison")
    a("")
    rows = [[name,
             f"{comp.loc[name,'sharpe_2bps']:.2f}",
             f"{comp.loc[name,'sharpe_5bps']:.2f}",
             f"{comp.loc[name,'sharpe_10bps']:.2f}",
             f"[{comp.loc[name,'ci_lo']:.2f}, {comp.loc[name,'ci_hi']:.2f}]"
             + ("" if not comp.loc[name, "crosses_0"] else " ⚠crosses0"),
             _fmt_pct(comp.loc[name, "max_dd"]),
             f"{comp.loc[name,'calmar']:.2f}",
             _fmt_pct(comp.loc[name, "win_rate"]),
             f"{comp.loc[name,'turnover_ann']:.1f}x"]
            for name in AGGS]
    a(_t(rows, ["method", "Sharpe@2bps", "Sharpe@5bps", "Sharpe@10bps", "Sharpe 95% CI (5bps)",
                "max DD", "Calmar", "win", "turnover"]))
    a("")

    a("## Crisis alpha (cumulative return, net @5bps)")
    a("")
    rr = [[reg] + [_fmt_pct(regimes[name].loc[reg, "cum_return"]) for name in AGGS]
          for reg in regimes[ew].index]
    a(_t(rr, ["regime"] + list(AGGS.keys())))
    a("")

    a("## Sub-period Sharpe (4-year blocks, net @5bps)")
    a("")
    periods = subp[ew].index
    rr = [[p] + [f"{subp[name].get(p, float('nan')):.2f}" for name in AGGS] for p in periods]
    a(_t(rr, ["period"] + list(AGGS.keys())))
    a("")

    # honest read
    s_ew, s_iv, s_rp = (comp.loc[n, "sharpe_5bps"] for n in (ew, iv, rp))
    # is the difference inside bootstrap noise? compare RP point to EW CI.
    rp_inside_ew_ci = comp.loc[ew, "ci_lo"] <= s_rp <= comp.loc[ew, "ci_hi"]
    iv_inside_ew_ci = comp.loc[ew, "ci_lo"] <= s_iv <= comp.loc[ew, "ci_hi"]
    a("## Honest read")
    a("")
    a(f"- Net Sharpe @5bps: **equal-weight {s_ew:.2f}**, inverse-vol {s_iv:.2f}, "
      f"risk parity {s_rp:.2f}.")
    a(f"- Inverse-vol vs EW: Δ={s_iv-s_ew:+.2f} — "
      f"{'within' if iv_inside_ew_ci else 'outside'} EW's 95% bootstrap CI "
      f"[{comp.loc[ew,'ci_lo']:.2f}, {comp.loc[ew,'ci_hi']:.2f}] (i.e. "
      f"{'not distinguishable from noise' if iv_inside_ew_ci else 'a real difference'}).")
    a(f"- Risk parity vs EW: Δ={s_rp-s_ew:+.2f} — "
      f"{'within' if rp_inside_ew_ci else 'outside'} EW's CI "
      f"(i.e. {'not distinguishable from noise' if rp_inside_ew_ci else 'a real difference'}).")
    better = max(s_iv, s_rp) > s_ew + 0.10
    if not better:
        a("- **Conclusion: the complex schemes do NOT beat equal-weight by a meaningful, "
          "noise-exceeding margin.** Inverse-vol is essentially equal-weight by construction "
          "(both are correlation-ignoring risk weighting); ERC adds a noisy covariance estimate "
          "for no clear gain. **This supports keeping the simple equal-weight aggregation** — "
          "it is as good, with fewer parameters and no reliance on an unstable covariance matrix.")
    else:
        a("- A complex scheme shows a higher point Sharpe; but check whether it exceeds EW's CI "
          "(noise) and whether it depends on covariance stability before reading anything into it. "
          "**The main strategy still stays equal-weight (this is a control, not an adoption).**")
    a("")
    a("- **Main strategy unchanged:** still equal-weight aggregation; lookbacks, target vols, vol "
      "window and leverage cap are the same conventional values. Risk parity is a control only.")
    a("")
    config.RP_REPORT_MD.write_text("\n".join(L), encoding="utf-8")


if __name__ == "__main__":
    main()
