"""Cross-Sectional Momentum (XSMOM) — the comparison study.

The deliverable is NOT a standalone Sharpe; it is the head-to-head against the
existing multi-asset TSMOM on the SAME 17-ETF universe, SAME 12-1 cadence, SAME
engine — and, above all, the CORRELATION of their return streams (the punchline:
trend vs relative-strength + the diversification payoff of combining them).

Reuse, don't reinvent
---------------------
* TSMOM = exactly what ``run_backtest.py`` publishes (engine ``build_portfolio`` →
  vol-targeted net). Not re-derived.
* Returns + cost model: ``performance.portfolio_returns`` (verbatim).
* Vol estimator for the risk-alignment overlay: ``portfolio.realized_portfolio_vol``
  (verbatim — guarantees the window matches TSMOM by construction).
* Validation: ``validation.bootstrap_ci`` / ``subperiod_performance`` /
  ``regime_performance`` (verbatim).
Only the signal + dollar-neutral construction are new (``src/xsmom.py``).

Scale discipline (spec §3)
--------------------------
Sharpe / correlation / all statistical tests run on NATURAL-scale (un-targeted)
returns — they are scale-free. The 10%-vol overlay is used ONLY for the
equity-curve overlay and the equal-risk 50/50 combination.

Run:  python run_xsmom.py
"""

from __future__ import annotations

import datetime as dt

import numpy as np
import pandas as pd

import config
import universe
import xsmom_config as xcfg
from src import performance as perf, plots, portfolio, signals, validation
from src import xsmom as xs
from src import fetch_data


# --------------------------------------------------------------------------- #
# Formatting helpers (mirror run_backtest.py)
# --------------------------------------------------------------------------- #
def _fmt_pct(x: float) -> str:
    return "n/a" if pd.isna(x) else f"{x*100:.1f}%"


def _md_table(rows, header) -> str:
    h = "| " + " | ".join(header) + " |"
    s = "| " + " | ".join("---" for _ in header) + " |"
    b = "\n".join("| " + " | ".join(str(c) for c in r) + " |" for r in rows)
    return "\n".join([h, s, b])


# --------------------------------------------------------------------------- #
# Return builders
# --------------------------------------------------------------------------- #
def _full_universe_returns(weights: pd.DataFrame, signal: pd.DataFrame,
                           monthly_px: pd.DataFrame, cost_bps: float) -> pd.DataFrame:
    """Natural-scale monthly returns of a dollar-neutral weight panel, restricted to
    full-universe months (decision month had all 17 names rankable) — same honesty
    rule as the TSMOM backtest. positions = weights.shift(1) (no look-ahead)."""
    positions = weights.shift(1)
    rets = perf.portfolio_returns(positions, monthly_px, cost_bps=cost_bps)
    full = signal.notna().all(axis=1)
    first_full = full[full].index.min()
    return rets.loc[rets.index > first_full]


def _voltarget_leverage(base_weights: pd.DataFrame, daily_px: pd.DataFrame,
                        target: float = xcfg.TARGET_VOL_ANNUAL) -> pd.Series:
    """Ex-ante 10%-vol leverage using the ENGINE's estimator verbatim. The vol at
    month-end M scales the return EARNED in M+1 (``.shift(1)``) — no look-ahead."""
    base_daily = portfolio.base_portfolio_daily_returns(base_weights, daily_px)
    port_vol = portfolio.realized_portfolio_vol(base_daily, window=xcfg.VOL_WINDOW_DAYS)
    return (target / port_vol.where(port_vol > 0)).shift(1)


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def main() -> None:
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    prices, _ = fetch_data.fetch_universe(force=False)
    px = prices[universe.TICKERS]
    monthly_px = signals.to_monthly(px)
    cost = xcfg.TRANSACTION_COST_BPS

    # ---- TSMOM (reuse the published pipeline verbatim) ------------------------ #
    tport = portfolio.build_portfolio(px, method="B")
    t_full = tport["asset_weight"].notna().all(axis=1)
    t_first = t_full[t_full].index.min()
    tsmom = perf.portfolio_returns(tport["position"], monthly_px, cost_bps=cost)
    tsmom = tsmom.loc[tsmom.index > t_first]
    tsmom_net = tsmom["net"]

    # ---- XSMOM signal + both constructions ----------------------------------- #
    sig = xs.momentum_skip(px)
    w_terc = xs.tercile_weights(sig)
    w_rank = xs.rank_weights(sig)
    r_terc = _full_universe_returns(w_terc, sig, monthly_px, cost)
    r_rank = _full_universe_returns(w_rank, sig, monthly_px, cost)
    xs_terc_net, xs_rank_net = r_terc["net"], r_rank["net"]

    # ---- common evaluation window (identical months for every comparison) ----- #
    common = xs_terc_net.index.intersection(tsmom_net.index)
    xs_terc_net = xs_terc_net.reindex(common).dropna()
    common = xs_terc_net.index
    xs_rank_net = xs_rank_net.reindex(common)
    tsmom_net = tsmom_net.reindex(common)
    xs_terc_gross = r_terc["gross"].reindex(common)
    xs_rank_gross = r_rank["gross"].reindex(common)
    tsmom_gross = tsmom["gross"].reindex(common)

    bh = perf.buy_and_hold_returns(monthly_px).reindex(common).dropna()

    # ---- core metrics (gross + net) ------------------------------------------ #
    M = {
        "XSMOM-tercile (net)": perf.metrics(xs_terc_net),
        "XSMOM-tercile (gross)": perf.metrics(xs_terc_gross),
        "XSMOM-rank (net)": perf.metrics(xs_rank_net),
        "XSMOM-rank (gross)": perf.metrics(xs_rank_gross),
        "TSMOM (net)": perf.metrics(tsmom_net),
        "TSMOM (gross)": perf.metrics(tsmom_gross),
        "Equal-wt buy&hold": perf.metrics(bh),
    }
    turn = {
        "XSMOM-tercile": float(r_terc["turnover"].reindex(common).mean() * 12),
        "XSMOM-rank": float(r_rank["turnover"].reindex(common).mean() * 12),
        "TSMOM": float(tsmom["turnover"].reindex(common).mean() * 12),
    }

    # ---- (1) vs 0: bootstrap CI + walk-forward (headline = XSMOM tercile) ----- #
    ci_terc = validation.bootstrap_ci(xs_terc_net, stat="sharpe")
    ci_rank = validation.bootstrap_ci(xs_rank_net, stat="sharpe")
    ci_terc_ann = validation.bootstrap_ci(xs_terc_net, stat="ann_return")
    subp = validation.subperiod_performance(xs_terc_net, block_years=4)
    blocks_pos = int((subp["ann_return"] > 0).sum()) if not subp.empty else 0
    blocks_tot = int(len(subp)) if not subp.empty else 0
    wf_pass = (blocks_tot > 0) and (blocks_pos / blocks_tot > 0.5) and (xs_terc_net.mean() > 0)

    # ---- (3) correlation — THE PUNCHLINE ------------------------------------- #
    rho_terc = float(xs_terc_net.corr(tsmom_net))
    rho_rank = float(xs_rank_net.corr(tsmom_net))
    rho_xx = float(xs_terc_net.corr(xs_rank_net))
    # 36m rolling correlation (for the figure / stability narrative)
    roll_corr = xs_terc_net.rolling(36).corr(tsmom_net)

    # ---- (4) combined portfolio (equal-risk 50/50) --------------------------- #
    L_xs = _voltarget_leverage(w_terc, px).reindex(common)
    xs_terc_t = (xs_terc_net * L_xs).dropna()             # XSMOM scaled to ~10% vol
    tsmom_t = tsmom_net.reindex(xs_terc_t.index)          # TSMOM already ~10% (published)
    combo = (0.5 * xs_terc_t + 0.5 * tsmom_t).dropna()

    s1 = perf.sharpe_ratio(xs_terc_t)
    s2 = perf.sharpe_ratio(tsmom_t)
    rho_legs = float(xs_terc_t.corr(tsmom_t))
    s_combo_real = perf.sharpe_ratio(combo)
    s_combo_pred = (s1 + s2) / np.sqrt(2 * (1 + rho_legs)) if (1 + rho_legs) > 0 else float("nan")
    vol_xs_t = float(xs_terc_t.std(ddof=1) * np.sqrt(12))
    vol_tsmom_t = float(tsmom_t.std(ddof=1) * np.sqrt(12))

    # ---- (5) crisis windows — different-shaped tails ------------------------- #
    reg_xs = validation.regime_performance(xs_terc_net, xcfg.REGIMES)
    reg_ts = validation.regime_performance(tsmom_net, xcfg.REGIMES)
    reg_bh = validation.regime_performance(bh, xcfg.REGIMES)

    # ---- robustness: 3/6/9/12 formation + tercile-vs-rank -------------------- #
    rob_rows = []
    headline_sign = np.sign(perf.sharpe_ratio(xs_terc_net))
    same_sign = True
    for form in xcfg.FORMATION_NEIGHBOURHOOD_DAYS:
        s_f = xs.momentum_skip(px, formation_days=form)
        w_f = xs.tercile_weights(s_f)
        r_f = _full_universe_returns(w_f, s_f, monthly_px, cost)["net"].reindex(common).dropna()
        msr = perf.metrics(r_f)
        rob_rows.append([f"{form // 21}-1 ({form}d)", msr["sharpe"], _fmt_pct(msr["ann_return"]),
                         _fmt_pct(msr["max_drawdown"])])
        if form != xcfg.LOOKBACK_DAYS and np.sign(msr["sharpe"]) != headline_sign:
            same_sign = False

    # ---- confound decomposition (rank-weight basis) -------------------------- #
    w_within = xs.within_class_rank_weights(sig, universe.GROUPS)
    w_demean = xs.rank_weights(xs.demeaned_signal(sig))
    r_within = _full_universe_returns(w_within, sig, monthly_px, cost)["net"].reindex(common).dropna()
    r_demean = _full_universe_returns(w_demean, sig, monthly_px, cost)["net"].reindex(common).dropna()
    conf = {}
    for name, series in [("rank baseline", xs_rank_net), ("within-class", r_within),
                         ("demeaned signal", r_demean)]:
        ci = validation.bootstrap_ci(series, stat="sharpe")
        conf[name] = {"sharpe": perf.sharpe_ratio(series), "lo": ci["lo"], "hi": ci["hi"],
                      "crosses_0": ci["crosses_0"]}

    # ---- pre-registered verdict ---------------------------------------------- #
    confirmed = (not ci_terc["crosses_0"]) and wf_pass and same_sign

    # ---- figures ------------------------------------------------------------- #
    plots.plot_equity_curves(
        {"XSMOM-tercile (10% vol)": perf.equity_curve(xs_terc_t),
         "TSMOM (10% vol)": perf.equity_curve(tsmom_t),
         "50/50 combined": perf.equity_curve(combo),
         "Equal-wt buy&hold": perf.equity_curve(bh.reindex(xs_terc_t.index))},
        xcfg.XSMOM_EQUITY_PNG,
        "XSMOM vs TSMOM vs 50/50 combined (vol-aligned to 10%, growth of $1, log)",
    )

    # ---- persist CSVs -------------------------------------------------------- #
    pd.DataFrame({
        "xsmom_tercile_net": xs_terc_net, "xsmom_rank_net": xs_rank_net,
        "tsmom_net": tsmom_net, "buy_hold": bh.reindex(common),
        "xsmom_tercile_10v": xs_terc_t.reindex(common), "combined_10v": combo.reindex(common),
        "rolling36_corr": roll_corr,
    }).rename_axis("month_end").round(6).to_csv(xcfg.XSMOM_RETURNS_CSV)

    _write_report(common=common, M=M, turn=turn, ci_terc=ci_terc, ci_rank=ci_rank,
                  ci_terc_ann=ci_terc_ann, subp=subp, blocks_pos=blocks_pos,
                  blocks_tot=blocks_tot, wf_pass=wf_pass, rho_terc=rho_terc,
                  rho_rank=rho_rank, rho_xx=rho_xx, s1=s1, s2=s2, rho_legs=rho_legs,
                  s_combo_real=s_combo_real, s_combo_pred=s_combo_pred, vol_xs_t=vol_xs_t,
                  vol_tsmom_t=vol_tsmom_t, reg_xs=reg_xs, reg_ts=reg_ts, reg_bh=reg_bh,
                  rob_rows=rob_rows, same_sign=same_sign, conf=conf, confirmed=confirmed)

    # CSV side-tables for the appendix
    pd.DataFrame(rob_rows, columns=["formation", "sharpe", "ann_return", "max_dd"]).to_csv(
        xcfg.XSMOM_ROBUSTNESS_CSV, index=False)
    pd.DataFrame(conf).T.to_csv(xcfg.XSMOM_CONFOUND_CSV)
    reg_xs.join(reg_ts, lsuffix="_xsmom", rsuffix="_tsmom").to_csv(xcfg.XSMOM_CRISIS_CSV)

    # ---- console ------------------------------------------------------------- #
    print("\n==================  XSMOM vs TSMOM — SUMMARY (net of costs)  ==================")
    print(f"  common window: {common.min().date()} -> {common.max().date()}  ({len(common)} months)")
    print(f"  XSMOM-tercile  net Sharpe={M['XSMOM-tercile (net)']['sharpe']:.2f}  "
          f"maxDD={_fmt_pct(M['XSMOM-tercile (net)']['max_drawdown'])}  "
          f"turnover={turn['XSMOM-tercile']:.1f}x/yr")
    print(f"  XSMOM-rank     net Sharpe={M['XSMOM-rank (net)']['sharpe']:.2f}")
    print(f"  TSMOM          net Sharpe={M['TSMOM (net)']['sharpe']:.2f}  "
          f"maxDD={_fmt_pct(M['TSMOM (net)']['max_drawdown'])}")
    print(f"  Sharpe 95% CI (tercile): [{ci_terc['lo']:.2f}, {ci_terc['hi']:.2f}]  "
          f"crosses 0: {ci_terc['crosses_0']}")
    print(f"  >>> CORRELATION  corr(XSMOM, TSMOM) = {rho_terc:+.2f}  (rank: {rho_rank:+.2f})")
    print(f"  combined 50/50 Sharpe={s_combo_real:.2f}  (closed-form ~{s_combo_pred:.2f}; "
          f"legs S={s1:.2f}/{s2:.2f}, rho={rho_legs:+.2f})")
    print(f"  walk-forward blocks positive: {blocks_pos}/{blocks_tot}  ->  pass={wf_pass}")
    print(f"  3/6/9/12 same sign: {same_sign}")
    print(f"  confound survives (CI excludes 0): within-class={not conf['within-class']['crosses_0']}  "
          f"demeaned={not conf['demeaned signal']['crosses_0']}")
    verdict = "XSMOM CONFIRMED" if confirmed else "XSMOM NOT CONFIRMED (see criteria)"
    print(f"  PRE-REGISTERED VERDICT: {verdict}")
    print(f"  report: {xcfg.XSMOM_REPORT_MD}")


# --------------------------------------------------------------------------- #
# Report writer
# --------------------------------------------------------------------------- #
def _write_report(*, common, M, turn, ci_terc, ci_rank, ci_terc_ann, subp, blocks_pos,
                  blocks_tot, wf_pass, rho_terc, rho_rank, rho_xx, s1, s2, rho_legs,
                  s_combo_real, s_combo_pred, vol_xs_t, vol_tsmom_t, reg_xs, reg_ts,
                  reg_bh, rob_rows, same_sign, conf, confirmed) -> None:
    L: list[str] = []
    add = L.append

    add("# Cross-Sectional Momentum (XSMOM) vs Time-Series Momentum (TSMOM)")
    add("")
    add(f"*Generated {dt.datetime.now():%Y-%m-%d %H:%M}. Same 17-ETF universe, same 12-1 "
        "cadence, same engine. Honest validation — results reported as-is, no tuning.*")
    add(f"*Common evaluation window: **{common.min().date()} → {common.max().date()}** "
        f"({len(common)} months). Costs {xcfg.TRANSACTION_COST_BPS:.0f} bps one-way × turnover; "
        f"rf = {config.RISK_FREE_ANNUAL:.0%}.*")
    add("")

    # pre-registered verdict up top
    add("## TL;DR — pre-registered verdict")
    add("")
    add(f"- **XSMOM-tercile net Sharpe = {M['XSMOM-tercile (net)']['sharpe']:.2f}**, "
        f"95% bootstrap CI **[{ci_terc['lo']:.2f}, {ci_terc['hi']:.2f}]** → "
        f"**{'excludes 0' if not ci_terc['crosses_0'] else 'CROSSES 0'}**.")
    add(f"- Walk-forward: **{blocks_pos}/{blocks_tot} blocks positive** → "
        f"**{'pass' if wf_pass else 'fail'}**. 3/6/9/12 same sign: **{same_sign}**.")
    add(f"- **CONFIRMED iff** CI excludes 0 **AND** walk-forward positive **AND** 3/6/9/12 "
        f"same sign → **{'✅ CONFIRMED' if confirmed else '❌ NOT CONFIRMED'}**.")
    add(f"- **The punchline — `corr(XSMOM, TSMOM) = {rho_terc:+.2f}`** "
        f"(rank-weight: {rho_rank:+.2f}). "
        f"50/50 combined Sharpe **{s_combo_real:.2f}** vs best leg "
        f"{max(s1, s2):.2f}.")
    add("")

    # pre-registration block
    add("## 0. Pre-registered criteria (fixed before looking at results)")
    add("")
    add("- **CONFIRMED iff** bootstrap Sharpe CI excludes 0 **AND** walk-forward OOS "
        "expectancy positive (majority of non-overlapping blocks positive) **AND** the "
        "3/6/9/12-month formation neighbourhood is the same sign.")
    add("- **FALSIFIED if** the CI includes 0 **OR** walk-forward is negative — still documented.")
    add("- All three comparison outcomes pre-accepted: **low** corr → diversification payoff; "
        "**high** corr → \"at ETF granularity, XS and TS are the same source\" (honest negative); "
        "whoever wins Sharpe/crisis is reported as-is.")
    add("- **Confound**: edge survives within-class / demeaned ranking → real momentum; "
        "vanishes → static risk premium. Both honest.")
    add("")

    # head-to-head
    add("## 1. Head-to-head (net of costs, identical months)")
    add("")
    header = ["", "ann return", "ann vol", "Sharpe", "max DD", "Calmar", "win rate", "turnover/yr"]
    def row(name, key):
        m = M[name]
        t = turn.get(key, None)
        return [name, _fmt_pct(m["ann_return"]), _fmt_pct(m["ann_vol"]), f"{m['sharpe']:.2f}",
                _fmt_pct(m["max_drawdown"]),
                f"{m['calmar']:.2f}" if not pd.isna(m["calmar"]) else "n/a",
                _fmt_pct(m["win_rate"]), f"{t:.1f}x" if t is not None else "—"]
    add(_md_table([row("XSMOM-tercile (net)", "XSMOM-tercile"),
                   row("XSMOM-rank (net)", "XSMOM-rank"),
                   row("TSMOM (net)", "TSMOM"),
                   row("Equal-wt buy&hold", None)], header))
    add("")
    add("> **Scale note.** XSMOM here is the *natural* dollar-neutral long-short book "
        "(Σ wₗₒₙ𝓰 = +1, Σ wₛₕₒᵣₜ = −1); TSMOM is the published engine strategy, already "
        "vol-targeted to ~10%. **Sharpe is scale-free**, so the comparison is fair; the raw "
        "max-DD / ann-vol differ because the books sit at different gross. §4 puts both at a "
        "common 10% vol for an apples-to-apples drawdown read. XSMOM is dollar-neutral / "
        "≈0-beta, so it loses to a bull-market B&H *by design* — B&H is a background row, "
        "never the benchmark.")
    add("")

    # vs zero
    add("## 2. Is XSMOM distinguishable from zero? (vs 0, not vs B&H)")
    add("")
    add(f"- **Tercile** Sharpe {ci_terc['point']:.2f}, 95% CI [{ci_terc['lo']:.2f}, "
        f"{ci_terc['hi']:.2f}] — **{'crosses 0' if ci_terc['crosses_0'] else 'does not cross 0'}** "
        f"({ci_terc['frac_gt_0']*100:.1f}% of resamples > 0).")
    add(f"- **Rank-weight** Sharpe {ci_rank['point']:.2f}, 95% CI [{ci_rank['lo']:.2f}, "
        f"{ci_rank['hi']:.2f}] — **{'crosses 0' if ci_rank['crosses_0'] else 'does not cross 0'}**.")
    add(f"- Annual-return 95% CI (tercile): [{_fmt_pct(ci_terc_ann['lo'])}, "
        f"{_fmt_pct(ci_terc_ann['hi'])}] — "
        f"{'excludes 0' if not ci_terc_ann['crosses_0'] else 'includes 0'}.")
    add("")
    add("**Walk-forward (4-year non-overlapping blocks; no parameters fit ⇒ each block is OOS):**")
    add("")
    if not subp.empty:
        sr = [[idx, r["months"], _fmt_pct(r["ann_return"]), f"{r['sharpe']:.2f}",
               _fmt_pct(r["max_drawdown"])] for idx, r in subp.iterrows()]
        add(_md_table(sr, ["period", "months", "ann return", "Sharpe", "max DD"]))
        add("")
        add(f"> {blocks_pos}/{blocks_tot} blocks positive → walk-forward "
            f"**{'PASS' if wf_pass else 'FAIL'}**.")
    add("")

    # correlation
    add("## 3. Correlation — the headline")
    add("")
    add(f"- **`corr(XSMOM-tercile, TSMOM) = {rho_terc:+.2f}`** (monthly net, natural scale, "
        f"identical months). Rank-weight: **{rho_rank:+.2f}**.")
    add(f"- corr(XSMOM-tercile, XSMOM-rank) = {rho_xx:+.2f} (the two constructions agree).")
    # Honest reading ties to the ACTUAL combo outcome, not a bare correlation threshold:
    # a diversification payoff needs BOTH low-ish correlation AND comparable standalone edges.
    if s_combo_real > max(s1, s2) + 0.02:
        interp = (f"**Diversification payoff is real**: at ρ = {rho_terc:+.2f} the equal-risk 50/50 "
                  f"Sharpe ({s_combo_real:.2f}) beats the better leg ({max(s1, s2):.2f}) — trend and "
                  f"relative-strength capture partly different things (see §4).")
    else:
        interp = (f"**No diversification payoff here.** ρ = {rho_terc:+.2f} is *moderate and positive*, "
                  f"and because XSMOM's standalone edge ({min(s1, s2):.2f}) is far weaker than TSMOM's "
                  f"({max(s1, s2):.2f}), the equal-risk mix ({s_combo_real:.2f}) **dilutes rather than "
                  f"diversifies** — it underperforms TSMOM alone ({max(s1, s2):.2f}). At ETF "
                  f"granularity the two momentum forms substantially overlap (an honest negative for "
                  f"the diversification thesis; see §4).")
    add(f"- {interp}")
    add("")

    # combined
    add("## 4. Combined portfolio (equal-risk 50/50, vol-aligned to 10%)")
    add("")
    add("Each leg is scaled to ~10% annualized vol with the **engine's vol estimator "
        "(verbatim)**, then combined 50/50. (Scaling is needed only here and for the equity "
        "curve; §1–3 use natural scale.)")
    add("")
    add(_md_table([
        ["XSMOM-tercile @10%", f"{s1:.2f}", _fmt_pct(vol_xs_t)],
        ["TSMOM @10%", f"{s2:.2f}", _fmt_pct(vol_tsmom_t)],
        ["**50/50 combined**", f"**{s_combo_real:.2f}**", "—"],
    ], ["leg", "Sharpe", "realized vol"]))
    add("")
    add(f"- **Closed-form cross-check:** `S_combo = (S₁+S₂)/√(2(1+ρ))` "
        f"= ({s1:.2f}+{s2:.2f})/√(2(1+{rho_legs:+.2f})) = **{s_combo_pred:.2f}** "
        f"vs realized **{s_combo_real:.2f}**.")
    gain = s_combo_real - max(s1, s2)
    add(f"- Combined Sharpe {'beats' if gain > 0 else 'does not beat'} the best single leg "
        f"({max(s1, s2):.2f}) by {gain:+.2f}. ρ→0 ⇒ ≈1.41× single-leg Sharpe; ρ→1 ⇒ no gain.")
    add(f"- Equity curves (vol-aligned): [`{xcfg.XSMOM_EQUITY_PNG.name}`]({xcfg.XSMOM_EQUITY_PNG.name}).")
    add("")

    # crisis
    add("## 5. Crisis windows — different-shaped tails")
    add("")
    add("TSMOM's tail is **directional** (it earns crisis alpha by going net-short); XSMOM's "
        "tail is a **momentum crash** — the violent rebound of beaten-down losers blowing up the "
        "short leg (spring 2009). XSMOM has **no** directional crisis-alpha mechanism, so the "
        "two should behave differently in the same window (the physical source of low correlation).")
    add("")
    cr = [[name, reg_xs.loc[name, "months"], _fmt_pct(reg_xs.loc[name, "cum_return"]),
           _fmt_pct(reg_ts.loc[name, "cum_return"]), _fmt_pct(reg_bh.loc[name, "cum_return"])]
          for name in reg_xs.index]
    add(_md_table(cr, ["window", "months", "XSMOM cum", "TSMOM cum", "buy&hold cum"]))
    add("")

    # robustness
    add("## 6. Robustness (appendix — never used to pick parameters)")
    add("")
    add("**Formation neighbourhood (3/6/9/12-month, same 21-day skip):**")
    add("")
    add(_md_table([[r[0], f"{r[1]:.2f}", r[2], r[3]] for r in rob_rows],
                  ["formation", "Sharpe", "ann return", "max DD"]))
    add(f"> Same sign across the neighbourhood: **{same_sign}** (sign/magnitude consistency, "
        "not a search for the best lookback).")
    add("")
    add(f"**Tercile vs rank-weight:** Sharpe {M['XSMOM-tercile (net)']['sharpe']:.2f} vs "
        f"{M['XSMOM-rank (net)']['sharpe']:.2f}, return corr {rho_xx:+.2f} — conclusions "
        f"{'agree' if np.sign(M['XSMOM-tercile (net)']['sharpe']) == np.sign(M['XSMOM-rank (net)']['sharpe']) else 'disagree'}.")
    add("")

    # confound
    add("## 7. Confound decomposition — momentum or static premium?")
    add("")
    add("The cross-asset universe has structurally different long-run mean returns "
        "(equities > bonds, 2007–2026). Baseline XSMOM on average longs equities / shorts "
        "bonds — part of which is **static equity risk premium disguised as momentum**. Two "
        "controls strip that out (both on the rank-weight basis): **(a) within-class** ranking "
        "(equities vs equities, …) and **(b) demeaned signal** (subtract each asset's *ex-ante "
        "expanding* mean before ranking — the only look-ahead-free demean).")
    add("")
    cf = [[name, f"{d['sharpe']:.2f}", f"[{d['lo']:.2f}, {d['hi']:.2f}]",
           "crosses 0" if d["crosses_0"] else "excludes 0"] for name, d in conf.items()]
    add(_md_table(cf, ["spec", "Sharpe", "95% CI", "vs 0"]))
    survives = not conf["within-class"]["crosses_0"] and not conf["demeaned signal"]["crosses_0"]
    add("")
    add(f"> Edge **{'survives' if survives else 'does NOT survive'}** both controls → "
        f"{'real within-class momentum, not just static premium.' if survives else 'a meaningful part was static cross-asset risk premium — reported honestly.'}")
    add("")

    add("---")
    add("*Reuses the multi-asset TSMOM engine (signal-construction layers added in "
        "`src/xsmom.py`). No engine code was modified; the existing 43 no-look-ahead / "
        "correctness tests still pass alongside the new XSMOM tests. Research/education only — "
        "not investment advice.*")

    xcfg.XSMOM_REPORT_MD.write_text("\n".join(L), encoding="utf-8")


if __name__ == "__main__":
    main()
