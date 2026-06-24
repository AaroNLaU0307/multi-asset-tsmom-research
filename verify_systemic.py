"""Phase 0 — bias-free verification of the 'drawdowns are SYSTEMIC' claim.

READ-ONLY / GATING. No overlay, no new strategy, no parameter changes. The drawdown
diagnostic measured co-drawdown on PORTFOLIO-WEIGHTED sleeve contribution streams
(which bake in the equal-weight /N dilution and the shared portfolio leverage). The
crash-defense overlay's entire rationale rests on the sleeves genuinely co-moving, so
here we re-measure on STANDALONE unit-risk sleeve streams — each sleeve run as its own
10%-vol TSMOM via the unchanged ``portfolio.build_portfolio`` code path — and compare.

Outputs a console report + a small markdown artifact (output/, git-ignored). Then PAUSE.
"""

from __future__ import annotations

import sys

import numpy as np
import pandas as pd

import config
import universe
from src import attribution as A, fetch_data, performance as perf, portfolio, regime as R, signals


def _standalone_sleeve_net(px: pd.DataFrame, tickers: list[str]) -> pd.Series:
    """A sleeve traded on its OWN — equal-weight within the sleeve, its own 10% vol
    target — via the unchanged build_portfolio path. Unit-risk across sleeves (each
    targets 10% vol), with NO cross-sleeve weight concentration or shared leverage.
    Restricted to the sleeve's own full-coverage window."""
    sub = px[tickers]
    port = portfolio.build_portfolio(sub, method="B")
    positions = port["position"]
    monthly_px = signals.to_monthly(sub)
    rets = perf.portfolio_returns(positions, monthly_px, cost_bps=config.TRANSACTION_COST_BPS)
    full = port["asset_weight"].notna().all(axis=1)
    first = full[full].index.min()
    return rets["net"].loc[rets.index > first]


def _cum(series: pd.Series, lo, hi) -> float:
    """Arithmetic sum of monthly net over (lo, hi]  (matches the diagnostic's
    additive decline-phase convention)."""
    w = series[(series.index > lo) & (series.index <= hi)]
    return float(w.sum()) if w.notna().any() else np.nan


def _avg_pairwise_corr(frame: pd.DataFrame) -> float:
    c = frame.corr()                         # pairwise-complete by default
    iu = np.triu_indices_from(c.values, k=1)
    vals = c.values[iu]
    vals = vals[~np.isnan(vals)]
    return float(vals.mean()) if len(vals) else np.nan


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    prices, _ = fetch_data.fetch_universe(force=False)
    px = prices[universe.TICKERS]

    # ---- portfolio side: reuse the diagnostic verbatim ----
    dec = A.decompose(px)
    net = dec["port_net"]
    episodes = A.flag_episodes(A.find_episodes(net))
    flagged = episodes[episodes["flagged"]].copy()
    pw_codd = A.cross_sleeve_codrawdown(dec, flagged).set_index("episode_id")

    # ---- standalone unit-risk sleeve streams ----
    standalone = {s: _standalone_sleeve_net(px, ts) for s, ts in universe.GROUPS.items()}
    S = pd.DataFrame(standalone)             # monthly net, columns = sleeves
    sleeves = list(universe.GROUPS.keys())

    # ============================================================== #
    # 1+2. Co-drawdown: standalone vs portfolio-weighted (artifact check)
    # ============================================================== #
    rows = []
    for _, ep in flagged.iterrows():
        eid = int(ep["episode_id"])
        peak, trough = ep["peak_date"], ep["trough_date"]
        cums = {s: _cum(S[s], peak, trough) for s in sleeves}
        defined = {s: v for s, v in cums.items() if not np.isnan(v)}
        n_def = len(defined)
        n_down = sum(v < 0 for v in defined.values())
        rows.append({
            "episode_id": eid, "peak": peak.date(), "trough": trough.date(),
            "depth": ep["depth"],
            "sa_n_defined": n_def, "sa_n_down": n_down,
            "sa_frac_down": (n_down / n_def) if n_def else np.nan,
            "pw_frac_down": float(pw_codd.loc[eid, "frac_sleeves_down"]),
        })
    codd = pd.DataFrame(rows)

    # ============================================================== #
    # 3. Cross-sleeve correlation: outside vs during flagged declines
    # ============================================================== #
    Sc = S.dropna(how="any")                 # common window where all 5 standalone exist
    decline_months = pd.DatetimeIndex([])
    for _, ep in flagged.iterrows():
        m = Sc.index[(Sc.index > ep["peak_date"]) & (Sc.index <= ep["trough_date"])]
        decline_months = decline_months.union(m)
    during = Sc.loc[Sc.index.isin(decline_months)]
    outside = Sc.loc[~Sc.index.isin(decline_months)]
    corr_during = _avg_pairwise_corr(during)
    corr_outside = _avg_pairwise_corr(outside)

    # ============================================================== #
    # 4. Event anchoring
    # ============================================================== #
    # deepest episode (2022-23): standalone sleeve cumulative net
    deep = flagged.sort_values("depth").iloc[0]
    deep_cums = {s: _cum(S[s], deep["peak_date"], deep["trough_date"]) for s in sleeves}
    # crisis windows: is the STRATEGY making money (crisis alpha), not drawing down?
    def _win_cum(series, a, b):
        w = series[(series.index >= pd.Timestamp(a)) & (series.index <= pd.Timestamp(b))]
        return float(w.sum())
    gfc = _win_cum(net, *config.REGIMES["GFC 2008"])
    covid = _win_cum(net, *config.REGIMES["COVID 2020"])
    # are the crisis windows among the flagged drawdown episodes?
    flagged_spans = [(e["peak_date"], e["trough_date"]) for _, e in flagged.iterrows()]
    def _overlaps(a, b):
        a, b = pd.Timestamp(a), pd.Timestamp(b)
        return any((p <= b) and (t >= a) for p, t in flagged_spans)
    gfc_in_dd = _overlaps(*config.REGIMES["GFC 2008"])
    covid_in_dd = _overlaps(*config.REGIMES["COVID 2020"])

    # ---- console ----
    print("\n=================  PHASE 0 — SYSTEMIC VERIFICATION (standalone, bias-free)  =================")
    print(f"  standalone sleeve windows (each its own 10%-vol TSMOM):")
    for s in sleeves:
        print(f"    {s:11} {S[s].dropna().index.min().date()} -> {S[s].dropna().index.max().date()}  "
              f"({S[s].notna().sum()} mo, Sharpe {perf.sharpe_ratio(S[s].dropna()):.2f})")
    print(f"\n  1+2. CO-DRAWDOWN per flagged episode — standalone vs portfolio-weighted:")
    print("       (sa = standalone unit-risk; pw = portfolio-weighted contribution)")
    for r in codd.itertuples():
        print(f"    #{r.episode_id:<2} {str(r.peak):>10}->{str(r.trough):<10} dep {r.depth*100:5.1f}%  "
              f"sa {r.sa_n_down}/{r.sa_n_defined} = {r.sa_frac_down*100:4.0f}%   pw {r.pw_frac_down*100:4.0f}%")
    print(f"\n    MEAN standalone frac-down : {codd['sa_frac_down'].mean()*100:.0f}%")
    print(f"    MEAN portfolio-wtd frac-down: {codd['pw_frac_down'].mean()*100:.0f}%   "
          f"(diagnostic reported ~85%)")
    print(f"\n  3. AVG PAIRWISE CORRELATION of standalone sleeve returns:")
    print(f"     outside drawdowns : {corr_outside:+.3f}   ({len(outside)} mo)")
    print(f"     during  drawdowns : {corr_during:+.3f}   ({len(during)} mo)")
    print(f"     delta (during-outside): {corr_during - corr_outside:+.3f}  "
          f"({'SPIKES' if corr_during > corr_outside else 'does NOT spike'} in drawdowns)")
    print(f"\n  4. EVENT ANCHORING:")
    print(f"     deepest episode #{int(deep['episode_id'])} {deep['peak_date'].date()}->{deep['trough_date'].date()} "
          f"({deep['depth']*100:.1f}%) — standalone sleeve cum net:")
    for s in sleeves:
        v = deep_cums[s]
        print(f"        {s:11} {('n/a' if np.isnan(v) else f'{v*100:+5.1f}%')}")
    print(f"     crisis-alpha check (strategy NET cum return in the window):")
    print(f"        GFC 2008  ({config.REGIMES['GFC 2008'][0]}..{config.REGIMES['GFC 2008'][1]}): "
          f"{gfc*100:+.1f}%   in a flagged drawdown? {gfc_in_dd}")
    print(f"        COVID 2020 ({config.REGIMES['COVID 2020'][0]}..{config.REGIMES['COVID 2020'][1]}): "
          f"{covid*100:+.1f}%   in a flagged drawdown? {covid_in_dd}")

    # ============================================================== #
    # 5. Premise test for the OVERLAY TRIGGER (still verification, not design):
    #    does the causal systemic-risk signal read HIGHER in the actual drawdowns
    #    than in the profitable crises? If crises read higher, a de-grossing trigger
    #    fires where the strategy MAKES money (kills alpha) and stays quiet in the
    #    real drawdowns — i.e. anti-aligned with need.
    # ============================================================== #
    panel = R.build_panel(px)
    mvp = panel["port_vol_pctile"].resample(config.SIGNAL_RESAMPLE).last()
    disp = panel["cross_asset_dispersion"].resample(config.SIGNAL_RESAMPLE).last()
    disp_pctile = disp.rank(pct=True)  # full-sample rank — descriptive context only

    def _mean_over_months(series, months):
        s = series.reindex(months).dropna()
        return float(s.mean()) if len(s) else np.nan

    def _mean_over_window(series, a, b):
        w = series[(series.index >= pd.Timestamp(a)) & (series.index <= pd.Timestamp(b))]
        return float(w.dropna().mean()) if w.notna().any() else np.nan

    trig = {
        "drawdowns": (_mean_over_months(mvp, decline_months), _mean_over_months(disp_pctile, decline_months)),
        "GFC 2008": (_mean_over_window(mvp, *config.REGIMES["GFC 2008"]),
                     _mean_over_window(disp_pctile, *config.REGIMES["GFC 2008"])),
        "COVID 2020": (_mean_over_window(mvp, *config.REGIMES["COVID 2020"]),
                       _mean_over_window(disp_pctile, *config.REGIMES["COVID 2020"])),
        "full sample": (float(mvp.mean()), float(disp_pctile.mean())),
    }

    print(f"\n  5. WOULD A SYSTEMIC-RISK TRIGGER FIRE IN THE RIGHT PLACE?  "
          f"(causal port-vol %ile / cross-asset dispersion %ile)")
    for k, (a, b) in trig.items():
        print(f"     {k:12} port_vol_pctile={a:.2f}   dispersion_pctile={b:.2f}")
    print(f"     -> if GFC/COVID read HIGHER than 'drawdowns', a de-grossing trigger is "
          f"anti-aligned with need.")

    sa_mean = codd["sa_frac_down"].mean()
    corr_spikes = corr_during > corr_outside
    confirmed = (sa_mean >= 0.70) and corr_spikes
    print("\n  ---------------------------------------------------------------------------")
    print(f"  VERDICT: systemic claim {'CONFIRMED' if confirmed else 'NOT confirmed'} on a bias-free basis "
          f"(standalone co-drawdown {sa_mean*100:.0f}%, corr {corr_outside:+.2f}->{corr_during:+.2f}).")
    print("  ---------------------------------------------------------------------------")

    # ---- artifact ----
    out = config.OUTPUT_DIR / "PHASE0_SYSTEMIC_VERIFICATION.md"
    L = ["# Phase 0 — Systemic verification (standalone, bias-free)", "",
         f"*Read-only. Standalone unit-risk sleeve streams (each its own 10%-vol TSMOM via "
         f"`build_portfolio`), vs the diagnostic's portfolio-weighted contribution streams.*", "",
         "## 1+2. Co-drawdown — standalone vs portfolio-weighted", "",
         "| # | window | depth | standalone down | portfolio-wtd down |",
         "| --- | --- | --- | --- | --- |"]
    for r in codd.itertuples():
        L.append(f"| {r.episode_id} | {r.peak}→{r.trough} | {r.depth*100:.1f}% | "
                 f"{r.sa_n_down}/{r.sa_n_defined} ({r.sa_frac_down*100:.0f}%) | {r.pw_frac_down*100:.0f}% |")
    L += ["",
          f"- **Mean standalone frac-down: {codd['sa_frac_down'].mean()*100:.0f}%** "
          f"vs portfolio-weighted {codd['pw_frac_down'].mean()*100:.0f}% (diagnostic ~85%).", "",
          "## 3. Cross-sleeve correlation (standalone, equal-weighted pairs)", "",
          f"- outside drawdowns: **{corr_outside:+.3f}** ({len(outside)} mo)",
          f"- during drawdowns: **{corr_during:+.3f}** ({len(during)} mo)",
          f"- delta: **{corr_during - corr_outside:+.3f}** "
          f"({'spikes' if corr_during > corr_outside else 'does not spike'} during drawdowns)", "",
          "## 4. Event anchoring", "",
          f"- Deepest episode #{int(deep['episode_id'])} ({deep['peak_date'].date()}→{deep['trough_date'].date()}, "
          f"{deep['depth']*100:.1f}%) standalone sleeve cum net: "
          + ", ".join(f"{s} {('n/a' if np.isnan(deep_cums[s]) else f'{deep_cums[s]*100:+.1f}%')}" for s in sleeves) + ".",
          f"- GFC 2008 window strategy net: **{gfc*100:+.1f}%** (in a flagged drawdown? {gfc_in_dd}).",
          f"- COVID 2020 window strategy net: **{covid*100:+.1f}%** (in a flagged drawdown? {covid_in_dd}).", "",
          "## 5. Would a systemic-risk trigger fire in the right place?", "",
          "| window | port_vol_pctile | dispersion_pctile |",
          "| --- | --- | --- |"]
    for k, (a, b) in trig.items():
        L.append(f"| {k} | {a:.2f} | {b:.2f} |")
    L += ["",
          "> If GFC/COVID read higher than 'drawdowns', a de-grossing trigger fires where the "
          "strategy MAKES money (killing crisis alpha) and stays quiet in the real drawdowns.", "",
          f"## Verdict", "",
          f"Systemic claim **{'CONFIRMED' if confirmed else 'NOT confirmed'}** on a bias-free basis."]
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"  artifact: {out}")


if __name__ == "__main__":
    main()
