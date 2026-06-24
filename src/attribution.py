"""Drawdown attribution diagnostic — per-asset/sleeve PnL decomposition, drawdown
episode identification, and chop-vs-turning-point-crash classification.

DESCRIPTIVE ONLY. This module does not tune, optimize, or add any overlay. It
reuses the *exact* vol-scaled positions produced by the confirmed TSMOM pipeline
(``portfolio.build_portfolio`` -> ``positions``) and characterizes the realized
equity curve. The single question it answers: are the strategy's drawdowns driven
by (a) choppy/range-bound whipsaw or (b) held-trend momentum crashes — overall and
per sleeve?

No look-ahead caveat
--------------------
The episode REGIME LABELS here are full-sample descriptive (we are characterizing
history, which is legitimate). The strictly point-in-time / causal regime variables
meant to be reusable as live signals live in ``src/regime.py``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

import config
import universe
from . import performance as perf, signals


# --------------------------------------------------------------------------- #
# Sleeve map (reuse the locked universe groups)
# --------------------------------------------------------------------------- #
SLEEVE_OF: dict[str, str] = {t: g for g, ts in universe.GROUPS.items() for t in ts}
SLEEVES: list[str] = list(universe.GROUPS.keys())


def sleeve_frame(per_asset: pd.DataFrame) -> pd.DataFrame:
    """Collapse a per-asset (columns = tickers) frame to per-sleeve sums."""
    grp = per_asset.T.groupby(SLEEVE_OF).sum(min_count=1).T   # pandas 3: no axis=1 groupby
    return grp.reindex(columns=[s for s in SLEEVES if s in grp.columns])


# --------------------------------------------------------------------------- #
# Step 1 — per-asset PnL decomposition (+ reconciliation gate)
# --------------------------------------------------------------------------- #
def decompose(
    daily_px: pd.DataFrame,
    cost_bps: float = config.TRANSACTION_COST_BPS,
) -> dict[str, object]:
    """Reuse the main pipeline's positions and decompose net PnL per asset.

    per-asset gross_i  = position_i * monthly_return_i
    per-asset cost_i   = |Δposition_i| * cost_bps/1e4   (one-way, same as the engine)
    per-asset net_i    = gross_i - cost_i

    These sum EXACTLY to the engine's portfolio gross/cost/net, so the portfolio
    return is reconstructed additively. The evaluation window matches the backtest:
    only months when all 17 assets are live (full universe with 12-month signals).
    """
    from . import portfolio  # local import to avoid any import cycle at module load

    port = portfolio.build_portfolio(daily_px, method="B")
    positions = port["position"]                       # held weights = shift(1) of decisions
    monthly_px = signals.to_monthly(daily_px)

    # canonical engine return stream (the reconciliation reference)
    engine = perf.portfolio_returns(positions, monthly_px, cost_bps=cost_bps)

    # full-universe evaluation window (identical rule to run_backtest.py)
    asset_w = port["asset_weight"]
    full_decision = asset_w.notna().all(axis=1)
    first_full = full_decision[full_decision].index.min()

    rets = monthly_asset = perf.monthly_asset_returns(monthly_px).reindex_like(positions)
    gross_i = positions * rets                          # per-asset gross contribution
    turn_i = positions.diff().abs()                     # per-asset one-way turnover
    cost_i = turn_i * (cost_bps / 1e4)
    net_i = gross_i - cost_i

    port_gross = gross_i.sum(axis=1, min_count=1)
    port_cost = cost_i.sum(axis=1, min_count=1)
    port_net = port_gross - port_cost

    # restrict everything to the evaluated window (align to engine's dropna + window)
    keep = engine.index[engine.index > first_full]
    out = {
        "positions": positions,
        "monthly_px": monthly_px,
        "monthly_asset_ret": monthly_asset.loc[keep],
        "gross_i": gross_i.loc[keep],
        "cost_i": cost_i.loc[keep],
        "net_i": net_i.loc[keep],
        "port_gross": port_gross.loc[keep],
        "port_cost": port_cost.loc[keep],
        "port_net": port_net.loc[keep],
        "engine_net": engine["net"].loc[keep],
        "engine_gross": engine["gross"].loc[keep],
        "port_weight": port["port_weight"],
        "first_full": first_full,
    }
    return out


def reconcile(dec: dict, ref_net: pd.Series | None = None, tol: float = config.DD_RECONCILE_TOL) -> dict:
    """Compare the reconstructed portfolio net against the engine (and an optional
    serialized reference). Returns a dict of diffs; ``ok`` is the gate."""
    a = dec["port_net"]
    b = dec["engine_net"].reindex(a.index)
    d_engine = (a - b).abs()
    res = {
        "n": int(len(a)),
        "max_abs_diff_engine": float(d_engine.max()),
        "cum_diff_engine": float(a.sum() - b.sum()),
        "ok": bool(d_engine.max() <= tol),
    }
    if ref_net is not None:
        common = a.index.intersection(ref_net.index)
        d_ref = (a.reindex(common) - ref_net.reindex(common)).abs()
        res["n_ref"] = int(len(common))
        res["max_abs_diff_ref"] = float(d_ref.max())
        res["cum_diff_ref"] = float(a.reindex(common).sum() - ref_net.reindex(common).sum())
    return res


# --------------------------------------------------------------------------- #
# Step 2 — drawdown episode identification
# --------------------------------------------------------------------------- #
def find_episodes(net: pd.Series, min_depth: float = config.DD_MIN_DEPTH) -> pd.DataFrame:
    """Identify peak->trough->recovery drawdown episodes on the net equity curve.

    An episode runs from the last all-time-high (peak) through the underwater span
    to the first month equity reclaims the peak (recovery). Ongoing (unrecovered)
    drawdowns at the end of the sample are kept with recovery=NaT. Episodes shallower
    than ``min_depth`` are dropped as trivial.
    """
    eq = perf.equity_curve(net)
    vals = eq.to_numpy()
    idx = eq.index
    n = len(vals)
    rows = []
    i = 1
    while i < n:
        if vals[i] < vals[:i].max() - 1e-15:           # underwater (below running peak)
            peak_pos = int(np.argmax(vals[:i]))         # last all-time high before the dip
            peak_val = vals[peak_pos]
            j = i
            while j < n and vals[j] < peak_val - 1e-15:
                j += 1
            span = slice(peak_pos, min(j, n))           # peak .. recovery(or end)
            seg = vals[peak_pos + 1 : (j if j < n else n) + 0]
            trough_rel = int(np.argmin(vals[peak_pos + 1 : (j if j <= n else n)])) + peak_pos + 1
            depth = vals[trough_rel] / peak_val - 1.0
            recovered = j < n
            rows.append({
                "peak_date": idx[peak_pos],
                "trough_date": idx[trough_rel],
                "recovery_date": idx[j] if recovered else pd.NaT,
                "depth": float(depth),
                "decline_months": int(trough_rel - peak_pos),
                "recovery_months": int(j - trough_rel) if recovered else np.nan,
                "underwater_months": int((j if recovered else n - 1) - peak_pos),
                "recovered": bool(recovered),
            })
            i = j if recovered else n                    # jump past the resolved episode
        else:
            i += 1
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df = df[df["depth"] <= -abs(min_depth)].copy()
    df = df.sort_values("depth").reset_index(drop=True)
    df.insert(0, "episode_id", range(1, len(df) + 1))
    return df


def flag_episodes(episodes: pd.DataFrame, top_n: int = config.DD_FLAG_TOP_N,
                  depth: float = config.DD_FLAG_DEPTH) -> pd.DataFrame:
    """Mark episodes for detailed attribution: the ``top_n`` deepest OR depth>=``depth``."""
    ep = episodes.copy()
    rank = ep["depth"].rank(method="first")             # most negative = rank 1
    ep["flagged"] = (rank <= top_n) | (ep["depth"] <= -abs(depth))
    return ep


# --------------------------------------------------------------------------- #
# Step 3 — attribution (where: asset / sleeve), over each episode's decline phase
# --------------------------------------------------------------------------- #
def _decline_window(net_i: pd.DataFrame, peak_date, trough_date) -> pd.DataFrame:
    """Per-asset net contributions over the loss-accrual months (peak+1 .. trough)."""
    mask = (net_i.index > peak_date) & (net_i.index <= trough_date)
    return net_i.loc[mask]


def attribute(dec: dict, episodes: pd.DataFrame) -> pd.DataFrame:
    """Per-episode, per-asset additive attribution of the decline-phase PnL.

    Returns a long frame: one row per (episode_id, asset) with the summed net
    contribution and the sleeve. Sum over assets ~ the episode's arithmetic
    decline-phase return (the additive analogue of the compounded depth).
    """
    net_i = dec["net_i"]
    recs = []
    for _, ep in episodes.iterrows():
        win = _decline_window(net_i, ep["peak_date"], ep["trough_date"])
        contrib = win.sum(min_count=1)
        for tkr, v in contrib.items():
            if pd.isna(v):
                continue
            recs.append({
                "episode_id": int(ep["episode_id"]),
                "peak_date": ep["peak_date"], "trough_date": ep["trough_date"],
                "depth": ep["depth"], "asset": tkr, "sleeve": SLEEVE_OF[tkr],
                "net_contrib": float(v),
            })
    return pd.DataFrame(recs)


def cross_sleeve_codrawdown(dec: dict, episodes: pd.DataFrame) -> pd.DataFrame:
    """For each episode: how many sleeves lost money during the decline (systemic vs
    idiosyncratic). ``n_sleeves_down`` near the sleeve count = broad/systemic."""
    net_i = dec["net_i"]
    recs = []
    for _, ep in episodes.iterrows():
        win = _decline_window(net_i, ep["peak_date"], ep["trough_date"])
        sleeve_pnl = win.sum(min_count=1).groupby(SLEEVE_OF).sum()
        sleeve_pnl = sleeve_pnl.reindex([s for s in SLEEVES if s in sleeve_pnl.index])
        n_down = int((sleeve_pnl < 0).sum())
        recs.append({
            "episode_id": int(ep["episode_id"]),
            "depth": ep["depth"],
            "n_sleeves": int(sleeve_pnl.notna().sum()),
            "n_sleeves_down": n_down,
            "frac_sleeves_down": float(n_down / max(sleeve_pnl.notna().sum(), 1)),
            "worst_sleeve": sleeve_pnl.idxmin() if sleeve_pnl.notna().any() else None,
            "worst_sleeve_pnl": float(sleeve_pnl.min()) if sleeve_pnl.notna().any() else np.nan,
        })
    return pd.DataFrame(recs)


def sleeve_standalone_summary(dec: dict) -> pd.DataFrame:
    """Full-sample standalone summary per sleeve, where a sleeve's stream is its
    contribution to portfolio net (sum of its assets' net_i). These sum across
    sleeves to the portfolio net, so PnL/drawdown contributions reconcile exactly.
    """
    net_i = dec["net_i"]
    port_net = dec["port_net"]
    sleeve_ret = sleeve_frame(net_i).fillna(0.0)        # contribution streams
    # portfolio drawdown months (for "contribution to total drawdown")
    dd = perf.drawdown_curve(port_net)
    in_dd = dd < 0
    total_pnl = port_net.sum()
    total_dd_loss = port_net[in_dd & (port_net < 0)].sum()

    recs = []
    for s in sleeve_ret.columns:
        r = sleeve_ret[s]
        m = perf.metrics(r)
        contrib_pnl = float(r.sum())
        # the sleeve's share of losses incurred during portfolio drawdown months
        dd_contrib = float(r[in_dd & (port_net < 0)].sum())
        nz = r[r != 0]
        recs.append({
            "sleeve": s,
            "sharpe": m["sharpe"],
            "ann_return": m["ann_return"],
            "ann_vol": m["ann_vol"],
            "max_drawdown": m["max_drawdown"],
            "hit_rate": float((nz > 0).mean()) if len(nz) else np.nan,
            "contrib_to_pnl": contrib_pnl,
            "contrib_to_pnl_pct": float(contrib_pnl / total_pnl) if total_pnl != 0 else np.nan,
            "contrib_to_dd_loss": dd_contrib,
            "contrib_to_dd_loss_pct": float(dd_contrib / total_dd_loss) if total_dd_loss != 0 else np.nan,
        })
    return pd.DataFrame(recs)


# --------------------------------------------------------------------------- #
# Daily strategy stream (texture only — gross-of-cost intra-month drift of the
# fixed monthly book). Used for efficiency-ratio / worst-k-day / skew metrics that
# need daily granularity; the official DEPTH always uses the monthly net curve.
# --------------------------------------------------------------------------- #
def daily_strategy(dec: dict, daily_px: pd.DataFrame) -> tuple[pd.Series, pd.DataFrame]:
    """(daily_gross_return, per-asset daily contribution) of the held monthly book."""
    rets = daily_px.pct_change()
    held = dec["port_weight"].reindex(rets.index, method="ffill").shift(1)
    contrib = held * rets
    return contrib.sum(axis=1, min_count=1), contrib


def efficiency_ratio(price: pd.Series, floor: float = config.ER_FLOOR_DENOM) -> float:
    """|end - start| / Σ|daily change|. ~1 = clean directional move; ~0 = chop."""
    s = price.dropna()
    if len(s) < 2:
        return float("nan")
    net = abs(float(s.iloc[-1]) - float(s.iloc[0]))
    path = float(s.diff().abs().sum())
    return net / max(path, floor)


# --------------------------------------------------------------------------- #
# Step 4 — chop vs turning-point-crash classification
# --------------------------------------------------------------------------- #
def _prior_trend_sign(monthly_px: pd.DataFrame, peak_date, lookback: int = 12) -> pd.Series:
    """Sign of each asset's trailing 12-month return as of the peak (the trend the
    strategy was riding into the episode)."""
    mp = monthly_px.loc[:peak_date]
    if len(mp) <= lookback:
        return pd.Series(0.0, index=monthly_px.columns)
    mom = mp.iloc[-1] / mp.iloc[-1 - lookback] - 1.0
    return np.sign(mom)


def chop_vs_crash(dec: dict, episodes: pd.DataFrame, daily_px: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Per-episode chop-vs-crash decomposition + corroborating metrics.

    Engine (position-conditional split, additive): each asset-month's net
    contribution in the decline window is assigned to a bucket —
      * CRASH  : position HELD (sign unchanged vs prior month) AND aligned with the
                 entry 12m trend  -> a trend-following position bleeding as the trend
                 reversed (a turning-point momentum crash).
      * CHOP   : sign-flip / churn / counter-trend hold -> whipsaw.
    The buckets are additive and sum to the episode's decline-phase contribution.

    Corroborating per-episode metrics (context, not the split):
      1. turnover_signflips_per_mo : position sign-flips / decline months (whipsaw rate)
      2. efficiency_ratio          : avg |move|/path over decline-window daily prices,
                                     weighted by each asset's loss (low=chop, high=trend)
      3. worst_k_day_share + daily_skew : loss concentration / crash signature
      4. pre_episode_ER            : prior-trend strength (avg over loss assets)
    Returns (episode_table, per_asset_bucket_table).
    """
    net_i = dec["net_i"]
    monthly_px = dec["monthly_px"]
    daily_gross, _ = daily_strategy(dec, daily_px)
    # align positions to the eval window; keep the prior month via shift on the FULL
    # frame BEFORE reindexing so the first eval month still has its predecessor.
    pos_full = dec["positions"]
    positions = pos_full.reindex(net_i.index)
    prev_full = pos_full.shift(1).reindex(net_i.index)

    ep_rows, asset_rows = [], []
    for _, ep in episodes.iterrows():
        peak, trough = ep["peak_date"], ep["trough_date"]
        win_mask = (net_i.index > peak) & (net_i.index <= trough)
        win_net = net_i.loc[win_mask]                              # decline months x assets
        win_pos = positions.loc[win_mask]
        prev_pos = prev_full.loc[win_mask]
        trend = _prior_trend_sign(monthly_px, peak)

        crash_bucket = 0.0
        chop_bucket = 0.0
        signflips = 0
        n_pos_slots = 0
        for t in win_net.index:
            for tkr in win_net.columns:
                v = win_net.loc[t, tkr]
                if pd.isna(v):
                    continue
                p = win_pos.loc[t, tkr]
                pp = prev_pos.loc[t, tkr]
                if pd.isna(p):
                    continue
                n_pos_slots += 1
                sp, spp = np.sign(p), np.sign(pp) if not pd.isna(pp) else 0.0
                held = (sp == spp) and (sp != 0)
                aligned = (sp == trend.get(tkr, 0.0)) and (sp != 0)
                if sp != spp:
                    signflips += 1
                if held and aligned:
                    crash_bucket += v
                else:
                    chop_bucket += v

        # per-asset bucket detail (for sleeve roll-up)
        for tkr in win_net.columns:
            col = win_net[tkr].dropna()
            if col.empty:
                continue
            c_crash = c_chop = 0.0
            for t in col.index:
                v = col[t]
                p = win_pos.loc[t, tkr]
                pp = prev_pos.loc[t, tkr]
                if pd.isna(p):
                    continue
                sp = np.sign(p)
                spp = np.sign(pp) if not pd.isna(pp) else 0.0
                held = (sp == spp) and (sp != 0)
                aligned = (sp == trend.get(tkr, 0.0)) and (sp != 0)
                if held and aligned:
                    c_crash += v
                else:
                    c_chop += v
            # per-asset efficiency ratio over the decline window (daily price)
            dwin = daily_px[tkr].loc[(daily_px.index >= peak) & (daily_px.index <= trough)]
            er = efficiency_ratio(dwin)
            pre = daily_px[tkr].loc[(daily_px.index < peak)].tail(config.PRE_EPISODE_WINDOW_DAYS)
            pre_er = efficiency_ratio(pre)
            asset_rows.append({
                "episode_id": int(ep["episode_id"]), "asset": tkr, "sleeve": SLEEVE_OF[tkr],
                "net_contrib": float(col.sum()), "crash_contrib": float(c_crash),
                "chop_contrib": float(c_chop), "efficiency_ratio": er, "pre_episode_ER": pre_er,
            })

        # loss-weighted efficiency ratio + pre-episode trend over the LOSING assets
        a_df = pd.DataFrame([r for r in asset_rows if r["episode_id"] == int(ep["episode_id"])])
        losers = a_df[a_df["net_contrib"] < 0]
        w = (-losers["net_contrib"])
        er_w = float((losers["efficiency_ratio"] * w).sum() / w.sum()) if w.sum() > 0 else np.nan
        pre_w = float((losers["pre_episode_ER"] * w).sum() / w.sum()) if w.sum() > 0 else np.nan

        # daily loss concentration over the decline window
        dwin = daily_gross.loc[(daily_gross.index > peak) & (daily_gross.index <= trough)].dropna()
        tot_neg = dwin[dwin < 0].sum()
        worst_k = dwin.nsmallest(config.WORST_K_DAYS).sum()
        worst_k_share = float(worst_k / tot_neg) if tot_neg < 0 else np.nan
        daily_skew = float(dwin.skew()) if len(dwin) > 2 else np.nan

        total = crash_bucket + chop_bucket
        crash_share = float(crash_bucket / total) if total != 0 else np.nan
        ep_rows.append({
            "episode_id": int(ep["episode_id"]),
            "peak_date": peak, "trough_date": trough, "depth": ep["depth"],
            "decline_months": int(ep["decline_months"]),
            "crash_contrib": float(crash_bucket), "chop_contrib": float(chop_bucket),
            "crash_share": crash_share, "chop_share": (1 - crash_share) if pd.notna(crash_share) else np.nan,
            "label": ("crash" if pd.notna(crash_share) and crash_share >= 0.5 else "chop"),
            "turnover_signflips_per_mo": float(signflips / max(ep["decline_months"], 1)),
            "efficiency_ratio_lossw": er_w,
            "pre_episode_ER_lossw": pre_w,
            "worst_k_day_share": worst_k_share,
            "daily_skew": daily_skew,
        })

    return pd.DataFrame(ep_rows), pd.DataFrame(asset_rows)


def aggregate_chop_crash(ep_cc: pd.DataFrame, asset_cc: pd.DataFrame) -> dict[str, object]:
    """Overall and per-sleeve chop-vs-crash split, weighted by realized loss.

    The split is computed on the additive decline-phase contributions: we sum the
    crash/chop buckets across episodes (overall) and across (episode, sleeve) pairs
    (per sleeve), restricting to the loss side so the shares describe drawdown.
    """
    # overall: sum buckets across episodes, but only count the net adverse part
    crash = ep_cc["crash_contrib"].sum()
    chop = ep_cc["chop_contrib"].sum()
    total = crash + chop
    overall = {
        "crash_contrib": float(crash), "chop_contrib": float(chop),
        "crash_share": float(crash / total) if total != 0 else np.nan,
        "chop_share": float(chop / total) if total != 0 else np.nan,
    }
    # per sleeve
    g = asset_cc.groupby("sleeve")[["crash_contrib", "chop_contrib", "net_contrib"]].sum()
    g["total_bucket"] = g["crash_contrib"] + g["chop_contrib"]
    g["crash_share"] = g["crash_contrib"] / g["total_bucket"].where(g["total_bucket"] != 0)
    g["chop_share"] = g["chop_contrib"] / g["total_bucket"].where(g["total_bucket"] != 0)
    g = g.reindex([s for s in SLEEVES if s in g.index])
    return {"overall": overall, "per_sleeve": g.reset_index()}
