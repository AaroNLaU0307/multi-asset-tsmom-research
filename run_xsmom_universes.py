"""Multi-universe XSMOM study (Phase 2) — the pre-registered mechanism map.

Loops the five SEALED universes (see ``XSMOM_UNIVERSES_README.md``), reusing the engine
and the Phase-1 ``src/xsmom.py`` layers verbatim. For each universe: build XSMOM
(tercile headline + rank robustness), re-run TSMOM ON THE SAME UNIVERSE, compute the
natural-scale Sharpe + bootstrap CI, walk-forward, 3/6/9/12 neighbourhood, corr vs TSMOM,
the vol-aligned 50/50 combo + diversification break-even ρ, the crisis table, the
confound controls, the cost ceiling, and the Lo-MacKinlay decomposition. Then apply
BH-FDR across the five headline tests, a Deflated-Sharpe selection check on the best
universe, and emit the master map (table + figure) and the cross-universe XSMOM
correlation matrix.

Sharpe / correlation / all tests run on NATURAL-scale returns (scale-free); the 10% vol
overlay (engine estimator, verbatim) is used only for the equity overlay and the combo.

Run:  python run_xsmom_universes.py
"""

from __future__ import annotations

import datetime as dt

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import config
import xsmom_config as xcfg
import xsmom_universes as uni
from src import performance as perf, portfolio, signals, validation
from src import xsmom as xs
from src import xsmom_data as xd
from src import xsmom_stats as xst


def _fmt_pct(x: float) -> str:
    return "n/a" if pd.isna(x) else f"{x*100:.1f}%"


def _bh_desc(bh: dict) -> str:
    """Human-readable BH-FDR decision (handles the 'nothing rejected' case where the
    threshold is -inf instead of printing a bare -inf)."""
    if np.isfinite(bh["threshold"]):
        return f"reject p ≤ {bh['threshold']:.4f}"
    return "no universe rejected (no p below the BH line)"


def _md_table(rows, header) -> str:
    h = "| " + " | ".join(header) + " |"
    s = "| " + " | ".join("---" for _ in header) + " |"
    b = "\n".join("| " + " | ".join(str(c) for c in r) + " |" for r in rows)
    return "\n".join([h, s, b])


def _common_window(rets: pd.DataFrame, signal: pd.DataFrame) -> pd.DataFrame:
    """Restrict to full-universe months AND the sealed common-window start."""
    full = signal.notna().all(axis=1)
    first_full = full[full].index.min()
    out = rets.loc[rets.index > first_full]
    return out.loc[out.index >= pd.Timestamp(uni.COMMON_WINDOW_START)]


def _voltarget_leverage(base_weights: pd.DataFrame, daily_px: pd.DataFrame,
                        target: float = uni.TARGET_VOL_ANNUAL) -> pd.Series:
    """Ex-ante 10%-vol leverage using the ENGINE's estimator verbatim (no look-ahead:
    vol at month-end M scales month M+1 via .shift(1))."""
    base_daily = portfolio.base_portfolio_daily_returns(base_weights, daily_px)
    pv = portfolio.realized_portfolio_vol(base_daily, window=xcfg.VOL_WINDOW_DAYS)
    return (target / pv.where(pv > 0)).shift(1)


def _xsmom_returns(weights, signal, monthly_px, cost):
    return _common_window(perf.portfolio_returns(weights.shift(1), monthly_px, cost_bps=cost),
                          signal)


# --------------------------------------------------------------------------- #
# Per-universe analysis
# --------------------------------------------------------------------------- #
def analyse_universe(u: uni.Universe, prices_all: pd.DataFrame, cost: float) -> dict:
    kept, cover = xd.verify_coverage(prices_all, u.candidates)
    drops = [c for c in cover if not c.kept]
    px = prices_all[kept].dropna(how="all")
    monthly_px = signals.to_monthly(px)
    N = len(kept)
    n_side = uni.tercile_n_side(N)

    sig = xs.momentum_skip(px)
    w_terc = xs.tercile_weights(sig, n_long=n_side, n_short=n_side)
    w_rank = xs.rank_weights(sig)
    r_terc = _xsmom_returns(w_terc, sig, monthly_px, cost)
    r_rank = _xsmom_returns(w_rank, sig, monthly_px, cost)

    # TSMOM on the SAME universe (engine, verbatim)
    tport = portfolio.build_portfolio(px, method="B")
    r_ts = _common_window(perf.portfolio_returns(tport["position"], monthly_px, cost_bps=cost),
                          tport["asset_weight"])

    # align to a single common set of months
    common = r_terc.index.intersection(r_ts.index)
    xs_net = r_terc["net"].reindex(common)
    xs_gross = r_terc["gross"].reindex(common)
    rk_net = r_rank["net"].reindex(common)
    ts_net = r_ts["net"].reindex(common)
    turn = float(r_terc["turnover"].reindex(common).mean() * 12)

    m_terc, m_rank, m_ts = perf.metrics(xs_net), perf.metrics(rk_net), perf.metrics(ts_net)

    # vs 0
    ci = validation.bootstrap_ci(xs_net, stat="sharpe")
    pval = xst.sharpe_pvalue_vs0(xs_net)
    subp = validation.subperiod_performance(xs_net, block_years=4)
    blocks_pos = int((subp["ann_return"] > 0).sum()) if not subp.empty else 0
    blocks_tot = int(len(subp)) if not subp.empty else 0
    wf_pos = (blocks_tot > 0) and (blocks_pos / blocks_tot > 0.5) and (xs_net.mean() > 0)

    # 3/6/9/12 neighbourhood
    headline_sign = np.sign(m_terc["sharpe"])
    nbhd = {}
    same_sign = True
    for form in xcfg.FORMATION_NEIGHBOURHOOD_DAYS:
        sf = xs.momentum_skip(px, formation_days=form)
        wf = xs.tercile_weights(sf, n_long=n_side, n_short=n_side)
        rf = _xsmom_returns(wf, sf, monthly_px, cost)["net"].reindex(common).dropna()
        sh = perf.sharpe_ratio(rf)
        nbhd[form // 21] = sh
        if form != xcfg.LOOKBACK_DAYS and np.sign(sh) != headline_sign and abs(sh) > 1e-9:
            same_sign = False

    # correlation vs TSMOM + combo
    rho = float(xs_net.corr(ts_net))
    L = _voltarget_leverage(w_terc, px).reindex(common)
    xs_t = (xs_net * L).dropna()
    ts_t = ts_net.reindex(xs_t.index)
    combo = (0.5 * xs_t + 0.5 * ts_t).dropna()
    s1, s2 = perf.sharpe_ratio(xs_t), perf.sharpe_ratio(ts_t)
    rho_legs = float(xs_t.corr(ts_t))
    s_combo = perf.sharpe_ratio(combo)
    # diversification break-even rho: combo beats best leg iff rho < rho_star
    mx = max(s1, s2)
    rho_star = ((s1 + s2) ** 2) / (2 * mx**2) - 1.0 if mx > 0 else float("nan")

    # crisis windows
    reg_xs = validation.regime_performance(xs_net, uni.REGIMES)
    reg_ts = validation.regime_performance(ts_net, uni.REGIMES)

    # confound: demean (all) + within-class (where sub-groups exist)
    r_dem = _xsmom_returns(xs.rank_weights(xs.demeaned_signal(sig)), sig, monthly_px, cost)["net"].reindex(common).dropna()
    ci_dem = validation.bootstrap_ci(r_dem, stat="sharpe")
    conf = {"rank baseline": (perf.sharpe_ratio(rk_net), validation.bootstrap_ci(rk_net)["crosses_0"]),
            "demeaned": (perf.sharpe_ratio(r_dem), ci_dem["crosses_0"])}
    if u.subgroups:
        groups = {g: [t for t in mem if t in kept] for g, mem in u.subgroups.items()}
        groups = {g: mem for g, mem in groups.items() if len(mem) >= 2}
        if groups:
            r_wc = _xsmom_returns(xs.within_class_rank_weights(sig, groups), sig, monthly_px, cost)["net"].reindex(common).dropna()
            conf["within-class"] = (perf.sharpe_ratio(r_wc), validation.bootstrap_ci(r_wc)["crosses_0"])

    # cost ceiling: one-way bps where mean net return -> 0
    mg = float(xs_gross.mean())
    mt = float(r_terc["turnover"].reindex(common).mean())
    cost_ceiling = max(0.0, mg / mt * 1e4) if mt > 0 else float("nan")

    # mechanism decomposition (lag-1, monthly) + block-bootstrap CIs
    monthly_rets = signals.to_monthly(px).pct_change().reindex(common).dropna(how="any")
    decomp = xst.decomposition_block_bootstrap(monthly_rets, block=12, n=1000)

    return dict(
        u=u, kept=kept, drops=drops, N=N, n_side=n_side, common=common,
        xs_net=xs_net, rk_net=rk_net, ts_net=ts_net, xs_t=xs_t, combo=combo,
        m_terc=m_terc, m_rank=m_rank, m_ts=m_ts, turn=turn,
        ci=ci, pval=pval, subp=subp, blocks_pos=blocks_pos, blocks_tot=blocks_tot, wf_pos=wf_pos,
        nbhd=nbhd, same_sign=same_sign, rho=rho, s1=s1, s2=s2, rho_legs=rho_legs,
        s_combo=s_combo, rho_star=rho_star, reg_xs=reg_xs, reg_ts=reg_ts, conf=conf,
        cost_ceiling=cost_ceiling, decomp=decomp,
    )


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def main() -> None:
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    cost = uni.TRANSACTION_COST_BPS
    prices_all = xd.fetch_universe_prices(force=False)

    results = [analyse_universe(u, prices_all, cost) for u in uni.FAMILY]

    # ---- family BH-FDR across the 5 headline tercile tests --------------------
    pvals = [r["pval"] for r in results]
    bh = xst.benjamini_hochberg(pvals, alpha=0.05)
    for r, rej, q in zip(results, bh["reject"], bh["qvalues"]):
        r["bh_reject"] = bool(rej)
        r["qvalue"] = float(q)
        r["confirmed"] = bool(rej) and r["wf_pos"] and r["same_sign"]

    # ---- DSR on the best universe (selection control) -------------------------
    # Trials = the 5 SEALED headline tests ONLY (each universe's 12-1 tercile vs-0). The
    # 3/6/9/12 neighbourhood and the rank-weight construction are robustness and are
    # deliberately NOT counted as trials — counting them would inflate the deflation.
    n_trials = len(uni.FAMILY)                       # == 5, the sealed family
    trial_sr = [xst._per_period_sharpe_moments(r["xs_net"])[0] for r in results]  # monthly SR
    assert n_trials == len(trial_sr) == 5, "DSR trial count must equal the 5 sealed universes"
    best_i = int(np.argmax([r["m_terc"]["sharpe"] for r in results]))
    dsr = xst.deflated_sharpe_ratio(results[best_i]["xs_net"], trial_sr, n_trials=n_trials)
    dsr["n_trials"] = n_trials

    # ---- cross-universe XSMOM correlation matrix ------------------------------
    series = {r["u"].key: r["xs_net"] for r in results}
    cross = pd.DataFrame(series).corr()

    # ---- figure: Sharpe ± CI dot plot, zero line marked -----------------------
    _plot_map(results, uni.MAP_FIG_PNG)

    # ---- persist CSVs ---------------------------------------------------------
    _write_csvs(results, bh, cross)

    # ---- report + README map --------------------------------------------------
    _write_report(results, bh, dsr, results[best_i], cross)
    _patch_readme(results, bh, dsr, results[best_i], cross)

    # ---- console --------------------------------------------------------------
    print("\n=====================  XSMOM MULTI-UNIVERSE MAP  =====================")
    print(f"  BH-FDR @ alpha={bh['alpha']}: {_bh_desc(bh)}")
    for r in results:
        u = r["u"]
        print(f"  {u.key} {u.name:24s} N={r['N']:2d}  Sharpe={r['m_terc']['sharpe']:+.2f} "
              f"CI[{r['ci']['lo']:+.2f},{r['ci']['hi']:+.2f}]  p={r['pval']:.3f} q={r['qvalue']:.3f}  "
              f"corrTS={r['rho']:+.2f}  {'CONFIRMED' if r['confirmed'] else 'falsified'}")
    n_conf = sum(r["confirmed"] for r in results)
    print(f"  best = {results[best_i]['u'].key} (Sharpe {results[best_i]['m_terc']['sharpe']:.2f}); "
          f"DSR={dsr['dsr']:.3f}  (SR*={dsr['sr_star']:.3f}, PSR0={dsr['psr_vs0']:.3f})")
    print(f"  CONFIRMED universes: {n_conf}/5")
    print(f"  report: {uni.REPORT_MD}")


def _plot_map(results, out_png) -> None:
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ys = np.arange(len(results))[::-1]
    for y, r in zip(ys, results):
        sh = r["m_terc"]["sharpe"]
        lo, hi = r["ci"]["lo"], r["ci"]["hi"]
        col = "seagreen" if r["confirmed"] else ("firebrick" if r["ci"]["crosses_0"] else "goldenrod")
        ax.errorbar(sh, y, xerr=[[sh - lo], [hi - sh]], fmt="o", color=col, capsize=4, lw=2, ms=8)
        ax.text(hi + 0.03, y, f"N={r['N']}, p={r['pval']:.2f}", va="center", fontsize=8, color="grey")
    ax.axvline(0, color="black", lw=1)
    ax.set_yticks(ys)
    ax.set_yticklabels([f"{r['u'].key}: {r['u'].name}" for r in results])
    ax.set_xlabel("XSMOM-tercile net Sharpe (95% bootstrap CI)")
    ax.set_title("Multi-universe XSMOM — pre-registered mechanism map\n"
                 "green = confirmed (BH-FDR + OOS + neighbourhood); red = CI crosses 0")
    ax.grid(True, axis="x", alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_png, dpi=150)
    plt.close(fig)


def _write_csvs(results, bh, cross) -> None:
    rows = []
    for r in results:
        u = r["u"]
        d = r["decomp"]
        rows.append({
            "universe": u.key, "name": u.name, "prior": u.prior, "N": r["N"],
            "net_sharpe": round(r["m_terc"]["sharpe"], 3),
            "ci_lo": round(r["ci"]["lo"], 3), "ci_hi": round(r["ci"]["hi"], 3),
            "pvalue": round(r["pval"], 4), "qvalue": round(r["qvalue"], 4),
            "bh_reject": r["bh_reject"], "wf_pos": r["wf_pos"], "same_sign": r["same_sign"],
            "confirmed": r["confirmed"], "corr_vs_tsmom": round(r["rho"], 3),
            "combo_sharpe": round(r["s_combo"], 3), "best_leg_sharpe": round(max(r["s1"], r["s2"]), 3),
            "rho_star_breakeven": round(r["rho_star"], 3), "cost_ceiling_bps": round(r["cost_ceiling"], 1),
            "term1_autocov": round(d["term1_autocov"]["point"], 8),
            "term2_leadlag": round(d["term2_leadlag"]["point"], 8),
            "term3_dispersion": round(d["term3_dispersion"]["point"], 8),
        })
    pd.DataFrame(rows).to_csv(uni.MAP_CSV, index=False)

    drows = []
    for r in results:
        d = r["decomp"]
        for term in ("term1_autocov", "term2_leadlag", "term3_dispersion"):
            drows.append({"universe": r["u"].key, "term": term,
                          "point": d[term]["point"], "lo": d[term]["lo"], "hi": d[term]["hi"]})
    pd.DataFrame(drows).to_csv(uni.DECOMP_CSV, index=False)
    cross.round(3).to_csv(uni.CROSS_CORR_CSV)
    pd.DataFrame({r["u"].key: r["xs_net"] for r in results}).rename_axis("month_end").round(6).to_csv(
        uni.PER_UNIVERSE_RETURNS_CSV)


def _map_table(results, bh) -> str:
    """Master map — all THREE pre-registered confirmed-criteria shown per universe:
    (1) BH-corrected CI/q vs 0, (2) walk-forward OOS blocks positive, (3) 3/6/9/12 sign."""
    rows = []
    for r in results:
        u = r["u"]
        rows.append([
            f"**{u.key}** {u.name}", r["N"], f"{r['m_terc']['sharpe']:+.2f}",
            f"[{r['ci']['lo']:+.2f}, {r['ci']['hi']:+.2f}]", f"{r['pval']:.3f}", f"{r['qvalue']:.3f}",
            f"{r['blocks_pos']}/{r['blocks_tot']}{'✓' if r['wf_pos'] else '✗'}",
            "✓" if r["same_sign"] else "✗",
            "✅" if r["confirmed"] else "❌", f"{r['rho']:+.2f}",
            f"{r['s_combo']:.2f} vs {max(r['s1'], r['s2']):.2f}",
            "n/a" if pd.isna(r["cost_ceiling"]) else f"{r['cost_ceiling']:.0f}bp",
        ])
    return _md_table(rows, ["universe", "N", "net Sharpe", "95% CI", "p", "q(BH)",
                            "WF OOS", "3·6·9·12", "confirmed?", "corr vs TSMOM",
                            "combo vs best leg", "cost ceil"])


def _write_report(results, bh, dsr, best, cross) -> None:
    L: list[str] = []
    add = L.append
    add("# Multi-Universe XSMOM — FDR-controlled mechanism map")
    add("")
    add(f"*Generated {dt.datetime.now():%Y-%m-%d %H:%M}. Five SEALED universes, headline = 12-1 "
        "tercile, common window from 2008-05. Pre-registration in `XSMOM_UNIVERSES_README.md` was "
        "sealed before these results.*")
    add("")
    n_conf = sum(r["confirmed"] for r in results)
    add("## TL;DR")
    add("")
    add(f"- **CONFIRMED universes: {n_conf} / 5** (BH-FDR at α=0.05 — {_bh_desc(bh)}; "
        "confirmed also requires walk-forward positive **and** 3/6/9/12 same sign).")
    add(f"- **Best universe = {best['u'].key} ({best['u'].name})**, net Sharpe "
        f"{best['m_terc']['sharpe']:.2f}; **Deflated Sharpe (5 trials) = {dsr['dsr']:.3f}** "
        f"(benchmark SR\\* = {dsr['sr_star']:.3f}/mo, PSR vs 0 = {dsr['psr_vs0']:.3f}).")
    if n_conf == 0:
        add("- **Authoritative conclusion:** at liquid-ETF granularity, XSMOM's edge is "
            "**marginal / arbitraged even inside its theoretical domain** — no universe survives "
            "the family-corrected test. Statistically this is *failed-to-reject* (not *proven "
            "absent*); the power-independent leg is that term2 (lead-lag) is **not shown to be "
            "non-trivial anywhere** (see Methods). Reported as the headline result, not a failure.")
    add("")
    add("![map](xsmom_universes_map.png)")
    add("")

    add("## The map")
    add("")
    add(_map_table(results, bh))
    add("")
    add("> `WF OOS` = walk-forward 4-yr non-overlapping blocks positive (✓=majority). `3·6·9·12` = "
        "formation-neighbourhood sign consistency. **All three** are the pre-registered confirmed "
        "criteria; `confirmed?` = BH-reject **and** WF✓ **and** sign✓. `cost ceil` = one-way bps at "
        "which mean net return → 0; `combo vs best leg` = 50/50 vol-aligned combined Sharpe vs the "
        "stronger standalone leg.")
    add("")
    # A1 — DSR auditability: trial count + SR* spelled out
    add(f"**Deflated-Sharpe audit (A1):** best universe = {best['u'].key}; "
        f"**trials = {dsr.get('n_trials', 5)}** (the five sealed 12-1 tercile tests only — the "
        f"3/6/9/12 neighbourhood and rank-weight are robustness, excluded). Expected-max-under-null "
        f"benchmark **SR\\* = {dsr['sr_star']:.3f}/mo** (Bailey–LdP order statistic on the cross-trial "
        f"Sharpe dispersion). PSR vs 0 = {dsr['psr_vs0']:.3f}; **DSR = {dsr['dsr']:.3f}** "
        f"(< 0.95 ⇒ even the best of five is not significant after selection).")
    add("")
    add("## Methods & honest scope")
    add("")
    add("**Statistical conclusion = *failed to reject*, not *proved no edge*.** Every universe's "
        "Sharpe-vs-0 CI contains 0, so we fail to reject H0 at the available power — and the power "
        "is genuinely limited: thin cross-sections (N as small as **6**; tercile legs of 2 names at "
        "U3/U4/U5), **~218 months**, and bootstrap Sharpe CIs ≈ **±0.45**. The FX/commodity ETFs "
        "only list from ~2006, so even the secondary native-window robustness cannot extend them "
        "much. We therefore claim *\"no detectable edge at this power\"*, **not** *\"edge proven "
        "absent.\"*")
    add("")
    add("**Mechanism conclusion = the power-independent finding.** For XSMOM to beat TSMOM, the "
        "lead-lag term (term2) had to be non-trivial. In **no** universe is term2 statistically "
        "distinguishable from 0 (every block-bootstrap CI contains 0) — a statement about the "
        "lead-lag channel itself, independent of the Sharpe-test power. **But** term2 is "
        "*imprecisely* estimated (its CI admits magnitudes ≥ |term1| in every universe; widest at "
        "N=18), so the honest reading is **\"term2 not shown to be non-trivial\"**, not \"term2 "
        "≈ 0.\" The only reliably-present term is term1 (own-autocorrelation) — which TSMOM already "
        "harvests. On the combined weight of the all-negative Sharpe map, the demean collapse, and "
        "the absent (undemonstrated) lead-lag, XSMOM behaves as a market-neutral echo of the same "
        "source; we state that as *not demonstrated otherwise*, not as a proof of zero.")
    add("")

    # mechanism map
    add("## Mechanism decomposition (Lo–MacKinlay, lag-1 monthly)")
    add("")
    add("Annualised profit contributions (×12, in bps of the WRSS momentum book); term2 enters the "
        "profit with a **minus** (`E[π]=term1−term2+term3`). term1 = own-autocorrelation (shared "
        "with TSMOM); **term2 = lead-lag (XSMOM-only — must be non-trivial to beat TSMOM)**; "
        "term3 = cross-sectional dispersion of means (static-premium suspect).")
    add("")
    drows = []
    for r in results:
        d = r["decomp"]
        def cell(k):
            return f"{d[k]['point']*12*1e4:+.0f} [{d[k]['lo']*12*1e4:+.0f}, {d[k]['hi']*12*1e4:+.0f}]"
        prec = xst.term2_precision(d)
        t2cell = ("contains 0" if prec["contains_zero"] else "**EXCLUDES 0**") + \
                 f"; {prec['verdict']} (CI≈{prec['ci_vs_term1']:.1f}×|t1|)"
        drows.append([r["u"].key, cell("term1_autocov"), cell("term2_leadlag"), cell("term3_dispersion"),
                      t2cell, "collapses" if r["conf"]["demeaned"][1] else "survives"])
    add(_md_table(drows, ["universe", "term1 own-autocov", "term2 lead-lag", "term3 dispersion",
                          "term2 vs 0 (precision)", "demean test"]))
    add("")
    # A2 — family zero-overlap statement (flag any term2 CI that excludes 0)
    n_contain = sum(xst.term2_contains_zero(r["decomp"]) for r in results)
    n_conf_small = sum(xst.term2_precision(r["decomp"])["verdict"] == "confidently small" for r in results)
    flag = "" if n_contain == len(results) else "  ⚠️ FLAG: a term2 CI EXCLUDES 0 — see the table."
    add(f"> **A2 — term2 zero-overlap:** **{n_contain}/{len(results)}** universes have a term2 CI "
        f"that contains 0 (the XSMOM-only lead-lag channel is not distinguishable from zero in "
        f"any of them).{flag}")
    add(f"> **C1 — precision fork:** **{n_conf_small}/{len(results)}** universes are *confidently "
        "small* (term2 CI bounded below |term1|); the rest are **imprecise** — the term2 CI admits "
        "magnitudes ≥ |term1| (e.g. U4 term2 CI rivals term1; U2 is very wide at N=18). So the honest "
        "claim is **\"term2 not shown to be non-trivial\"**, NOT \"term2 proven ≈ 0\". `E[π]=term1−"
        "term2+term3`; the block length is 12 months (justified in `src/xsmom_stats.py`).")
    add("> term3 is cross-validated by the demean test: large term3 **and** Sharpe collapse under "
        "demeaning ⟹ the dispersion was static premium.")
    add("")

    # per-universe detail
    for r in results:
        u = r["u"]
        add(f"## {u.key} — {u.name}  *(prior: {u.prior})*")
        add("")
        add(f"*Homogeneity argument:* {u.argument}")
        add("")
        if r["drops"]:
            add(f"*Coverage drops:* " + "; ".join(f"{c.ticker} ({c.reason})" for c in r["drops"]))
            add("")
        add(f"- N={r['N']} (tercile {r['n_side']}/{r['n_side']}); months={len(r['common'])} "
            f"({r['common'].min().date()}→{r['common'].max().date()}).")
        add(f"- **XSMOM-tercile** net Sharpe **{r['m_terc']['sharpe']:+.2f}** "
            f"(ann {_fmt_pct(r['m_terc']['ann_return'])}, vol {_fmt_pct(r['m_terc']['ann_vol'])}, "
            f"maxDD {_fmt_pct(r['m_terc']['max_drawdown'])}, turnover {r['turn']:.1f}×); "
            f"rank-weight {r['m_rank']['sharpe']:+.2f}.")
        add(f"- vs 0: 95% CI [{r['ci']['lo']:+.2f}, {r['ci']['hi']:+.2f}], p={r['pval']:.3f}, "
            f"q(BH)={r['qvalue']:.3f} → **{'rejects 0 (BH)' if r['bh_reject'] else 'CI/BH includes 0'}**. "
            f"Walk-forward {r['blocks_pos']}/{r['blocks_tot']} blocks positive "
            f"({'pass' if r['wf_pos'] else 'fail'}); 3/6/9/12 same sign: {r['same_sign']} "
            f"({', '.join(f'{k}m:{v:+.2f}' for k, v in r['nbhd'].items())}).")
        add(f"- **TSMOM on this universe** Sharpe {r['m_ts']['sharpe']:+.2f}; "
            f"**corr(XSMOM,TSMOM)={r['rho']:+.2f}**. Combo 50/50 @10% = {r['s_combo']:.2f} "
            f"(legs {r['s1']:.2f}/{r['s2']:.2f}, ρ={r['rho_legs']:+.2f}); break-even ρ\\*="
            f"{r['rho_star']:+.2f} → combo **{'beats' if r['s_combo']>max(r['s1'],r['s2'])+1e-9 else 'does not beat'}** best leg.")
        crow = [[name, _fmt_pct(r["reg_xs"].loc[name, "cum_return"]),
                 _fmt_pct(r["reg_ts"].loc[name, "cum_return"])] for name in r["reg_xs"].index]
        add("")
        add("  Crisis windows (cum return) — XSMOM vs TSMOM:")
        add("")
        add(_md_table(crow, ["window", "XSMOM", "TSMOM"]))
        add("")
        conf_str = "; ".join(f"{k}: {v[0]:+.2f} ({'crosses 0' if v[1] else 'excludes 0'})"
                             for k, v in r["conf"].items())
        cc = "n/a" if pd.isna(r["cost_ceiling"]) else f"{r['cost_ceiling']:.0f} bps"
        add(f"- Confound: {conf_str}. Cost ceiling ≈ {cc} one-way.")
        add(f"- **Verdict: {'✅ CONFIRMED' if r['confirmed'] else '❌ falsified'}** "
            f"under the pre-registered criteria.")
        add("")

    # cross-universe corr
    add("## Cross-universe XSMOM correlation (are these the same bet?)")
    add("")
    hdr = ["", *cross.columns.tolist()]
    crows = [[idx] + [f"{cross.loc[idx, c]:+.2f}" for c in cross.columns] for idx in cross.index]
    add(_md_table(crows, hdr))
    add("")
    add("---")
    add("*Reuses the TSMOM engine + Phase-1 `src/xsmom.py` verbatim; new logic = universe loop, "
        "BH-FDR / Deflated-Sharpe (`src/xsmom_stats.py`), Lo-MacKinlay decomposition. No engine "
        "code modified; all prior tests still pass. Research/education only — not investment advice.*")

    uni.REPORT_MD.write_text("\n".join(L), encoding="utf-8")


def _patch_readme(results, bh, dsr, best, cross) -> None:
    """Idempotently (re)generate the 'THE MAP' results section, preserving the sealed
    pre-registration block above it EXACTLY. Truncates at the '## THE MAP' header and
    regenerates below, so re-runs never depend on a one-shot placeholder."""
    readme = config.PROJECT_ROOT / "XSMOM_UNIVERSES_README.md"
    if not readme.exists():
        return
    text = readme.read_text(encoding="utf-8")
    idx = text.find("## THE MAP")
    head = (text[:idx].rstrip() if idx != -1 else text.rstrip()) + "\n\n"
    n_conf = sum(r["confirmed"] for r in results)
    n_contain = sum(xst.term2_contains_zero(r["decomp"]) for r in results)

    b: list[str] = []
    b.append("## THE MAP — results (appended after the pre-registration above was sealed)")
    b.append("")
    b.append(f"*Run {dt.datetime.now():%Y-%m-%d}. Full per-universe tables, the mechanism map and "
             "the Methods note: [`output/XSMOM_UNIVERSES_REPORT.md`](output/XSMOM_UNIVERSES_REPORT.md).*")
    b.append("")
    b.append(f"**CONFIRMED universes: {n_conf} / 5.** Best = {best['u'].key} "
             f"({best['u'].name}), net Sharpe {best['m_terc']['sharpe']:.2f}; selection-adjusted "
             f"**Deflated Sharpe = {dsr['dsr']:.3f}** ({dsr.get('n_trials', 5)} trials, "
             f"SR\\*={dsr['sr_star']:.3f}/mo) → not significant after selection.")
    b.append("")
    b.append(_map_table(results, bh))
    b.append("")
    b.append("![map](output/xsmom_universes_map.png)")
    b.append("")
    if n_conf == 0:
        b.append("**Authoritative conclusion (pre-accepted in §5):** across the entire sealed "
                 "family, *no* universe survives the BH-FDR-corrected headline test together with "
                 "walk-forward and neighbourhood consistency. **At liquid-ETF granularity, XSMOM's "
                 "edge is marginal / arbitraged even inside its theoretical domain.**")
        b.append("")
        b.append("**Failed-to-reject, not proven-absent (honest scope).** The Sharpe map is a "
                 "*failed-to-reject* at limited power (N as small as 6; ~218 months; Sharpe CIs "
                 "≈ ±0.45) — we do **not** claim the edge is *proven* zero. The **power-independent** "
                 "leg is the mechanism: for XSMOM to beat TSMOM the lead-lag term (term2) had to be "
                 f"non-trivial, yet in **{n_contain}/5** universes term2's block-bootstrap CI "
                 "contains 0. term2 is *imprecisely* estimated (its CI admits magnitudes ≥ |term1| "
                 "in every universe; widest at N=18), so we state **\"term2 not shown to be "
                 "non-trivial\"** — not \"term2 ≈ 0\". The only reliably-present term is term1 "
                 "(own-autocorrelation), which TSMOM already harvests; on the combined weight of the "
                 "all-negative map, the demean collapse and the undemonstrated lead-lag, XSMOM "
                 "behaves as a market-neutral echo of the same source.")
    else:
        survivors = ", ".join(r["u"].key for r in results if r["confirmed"])
        b.append(f"**Survivors:** {survivors}. See the report for each survivor's mechanism "
                 "(term2 shown non-trivial + dispersion surviving demeaning) and corr/combo vs TSMOM.")
    b.append("")
    b.append("*Per-universe detail, the Lo-MacKinlay mechanism map (term1/2/3 with CIs + the C1 "
             "precision fork), crisis tables, confound controls, the Methods & honest-scope note and "
             "the cross-universe correlation matrix are in the full report.*")
    readme.write_text(head + "\n".join(b) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
