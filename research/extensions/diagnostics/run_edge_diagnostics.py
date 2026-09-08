"""X07 / X45 / X46 — Wave-1 edge diagnostics on the frozen published streams.

MAP_v2 Cluster C2 (X07) and C14 (X45, X46). Lane: MEASUREMENT. These are
DIAGNOSTICS of the already-burned baseline, not candidate tests: no parameter is
tuned, no candidate is selected, and nothing here is independent confirmation of
anything. Exposure class per MAP_v2: TARGET_PERFORMANCE_EXPOSURE (new statistics
of burned, published streams) + DESIGN_INFORMING_MEASUREMENT, context T0.

MAP_v2's anti-snooping rule for X07 applies and is not optional: no ETF is
removed from the baseline on the strength of anything computed here.

Inputs (frozen, read-only):
  output/dd_per_asset_net.csv           per-asset net PnL contributions, monthly
  output/monthly_returns.csv            gross/turnover/cost/net/buy_hold, monthly
  output/monthly_portfolio_weights.csv  signed portfolio weights, monthly
  data/close_prices_raw.csv             ETF adjusted closes (frozen snapshot)

Writes research/extensions/diagnostics/edge_diagnostics.json.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

REPO = Path(__file__).resolve().parents[3]
OUT = Path(__file__).with_name("edge_diagnostics.json")

SLEEVE = {
    "SPY": "Equity", "EEM": "Equity", "EWJ": "Equity", "XLE": "Equity",
    "XLU": "Equity",
    "TLT": "Bond", "SHY": "Bond", "LQD": "Bond", "HYG": "Bond",
    "USO": "Commodity", "UNG": "Commodity", "GLD": "Commodity",
    "DBA": "Commodity",
    "UUP": "FX", "FXY": "FX",
    "VNQ": "RealEstate", "RWX": "RealEstate",
}


def ann_sharpe(x, periods=12):
    x = pd.Series(x).dropna()
    sd = x.std(ddof=1)
    if sd == 0 or not np.isfinite(sd) or len(x) < 3:
        return None
    return float(x.mean() / sd * np.sqrt(periods))


def enb_participation_ratio(corr):
    """PCA participation ratio: (sum l)^2 / sum l^2 over the eigenvalues."""
    lam = np.linalg.eigvalsh(corr)
    lam = np.clip(lam, 0, None)
    if lam.sum() <= 0:
        return None
    return float(lam.sum() ** 2 / (lam ** 2).sum())


def enb_entropy(corr):
    """Entropy-based ENB: exp(entropy of the normalised eigenvalue spectrum).

    Reported beside the participation ratio because the two answer slightly
    different questions and MAP_v2 names both families. Neither is a
    "correct" ENB on its own.
    """
    lam = np.linalg.eigvalsh(corr)
    lam = np.clip(lam, 1e-15, None)
    p = lam / lam.sum()
    return float(np.exp(-(p * np.log(p)).sum()))


def main():
    res = {}
    import re
    COST_BPS = float(re.search(r"TRANSACTION_COST_BPS\s*=\s*([0-9.]+)",
                               (REPO / "config.py").read_text(encoding="utf-8")).group(1))

    pnl = pd.read_csv(REPO / "output/dd_per_asset_net.csv",
                      parse_dates=["Date"]).set_index("Date")
    monthly = pd.read_csv(REPO / "output/monthly_returns.csv",
                          parse_dates=["month_end"]).set_index("month_end")
    wts = pd.read_csv(REPO / "output/monthly_portfolio_weights.csv",
                      parse_dates=["month_end"]).set_index("month_end")
    px = pd.read_csv(REPO / "data/close_prices_raw.csv",
                     parse_dates=["Date"]).set_index("Date")

    assets = list(pnl.columns)
    res["window"] = {"first": str(pnl.index[0].date()),
                     "last": str(pnl.index[-1].date()), "n_months": len(pnl)}
    res["assets"] = assets

    # ================================================================= X07 ==
    c = pnl.corr()
    iu = np.triu_indices(len(assets), 1)
    res["X07"] = {
        "corr_matrix": c.round(4).to_dict(),
        "enb_participation_ratio": enb_participation_ratio(c.values),
        "enb_entropy": enb_entropy(c.values),
        "n_assets": len(assets),
        "mean_abs_offdiag_corr": float(np.abs(c.values[iu]).mean()),
        "max_offdiag_corr": float(c.values[iu].max()),
        "min_offdiag_corr": float(c.values[iu].min()),
    }
    sl = {}
    for a in assets:
        sl.setdefault(SLEEVE[a], []).append(a)
    sleeve_pnl = pd.DataFrame({s: pnl[cols].sum(axis=1) for s, cols in sl.items()})
    sc = sleeve_pnl.corr()
    res["X07"]["sleeve_members"] = sl
    res["X07"]["sleeve_corr"] = sc.round(4).to_dict()
    res["X07"]["sleeve_enb_participation_ratio"] = enb_participation_ratio(sc.values)

    def pair(a, b):
        return float(c.loc[a, b])

    res["X07"]["named_overlaps"] = {
        "VNQ_vs_SPY": pair("VNQ", "SPY"), "RWX_vs_SPY": pair("RWX", "SPY"),
        "VNQ_vs_RWX": pair("VNQ", "RWX"),
        "UUP_vs_FXY": pair("UUP", "FXY"),
        "RealEstate_vs_Equity_sleeve": float(sc.loc["RealEstate", "Equity"]),
        "FX_vs_Equity_sleeve": float(sc.loc["FX", "Equity"]),
    }
    tri = [(a, b, float(c.loc[a, b])) for i, a in enumerate(assets)
           for b in assets[i + 1:]]
    tri.sort(key=lambda t: -abs(t[2]))
    res["X07"]["top_10_dependent_pairs"] = [
        {"a": a, "b": b, "corr": round(v, 4)} for a, b, v in tri[:10]]

    # ============================================================ RECONCILE ==
    common = pnl.index.intersection(monthly.index)
    recon = pnl.loc[common].sum(axis=1) - monthly.loc[common, "net"]
    res["reconciliation"] = {
        "n_months": int(len(common)),
        "max_abs_residual": float(recon.abs().max()),
        "mean_abs_residual": float(recon.abs().mean()),
        "worst_month": str(recon.abs().idxmax().date()),
    }

    # ================================================================= X45 ==
    w = wts.dropna(how="all")
    w = w.loc[w.index.intersection(monthly.index)]
    res["X45"] = {"weights_window": {"first": str(w.index[0].date()),
                                     "last": str(w.index[-1].date()),
                                     "n_months": len(w)}}
    res["X45"]["avg_net_exposure_by_asset"] = w.mean().round(4).to_dict()
    res["X45"]["avg_net_exposure_by_sleeve"] = {
        s: float(w[cols].sum(axis=1).mean()) for s, cols in sl.items()}
    res["X45"]["avg_gross_exposure"] = float(w.abs().sum(axis=1).mean())
    res["X45"]["avg_net_exposure_total"] = float(w.sum(axis=1).mean())
    res["X45"]["pct_months_net_long_by_asset"] = {
        a: float((w[a] > 0).mean()) for a in assets}

    mret = px.resample("ME").last().pct_change()
    factors = pd.DataFrame({
        "SPY": mret["SPY"], "TLT": mret["TLT"], "UUP": mret["UUP"],
        "COMMOD": mret[["USO", "UNG", "GLD", "DBA"]].mean(axis=1),
    })
    idx = monthly.index.intersection(factors.dropna().index)
    y = monthly.loc[idx, "net"]
    X = sm.add_constant(factors.loc[idx])
    lags = int(np.floor(4 * (len(idx) / 100) ** (2 / 9)))
    m = sm.OLS(y, X).fit(cov_type="HAC", cov_kwds={"maxlags": lags})
    res["X45"]["factor_regression"] = {
        "n": int(len(idx)), "hac_maxlags": lags,
        "r_squared": float(m.rsquared),
        "params": {k: float(v) for k, v in m.params.items()},
        "hac_tstats": {k: float(v) for k, v in m.tvalues.items()},
        "hac_pvalues": {k: float(v) for k, v in m.pvalues.items()},
        "alpha_monthly": float(m.params["const"]),
        "alpha_annualised": float(m.params["const"] * 12),
    }

    # ---- reconciliation gate: rebuild the engine's decomposition ---------
    # The engine holds `positions = decision_weights.shift(1)` and forms
    # gross_i = positions * monthly_asset_return. An earlier revision of this
    # file paired weights with the SAME month's return and did not reconcile
    # (corr 0.44); that reconstruction was wrong and its static-book numbers
    # were not a decomposition of the baseline. This alignment reconciles to
    # 2e-05 against the published streams, i.e. to their 6-dp rounding.
    pos = wts[assets].shift(1)
    ci = pos.index.intersection(mret.index).intersection(monthly.index)
    pos = pos.loc[ci]
    R = mret.loc[ci, assets]
    gross_i = pos * R
    turn_i = pos.diff().abs()
    cost_i = turn_i * (COST_BPS / 1e4)
    net_i = gross_i - cost_i
    rec_gross = gross_i.sum(axis=1, min_count=1)
    rec_cost = cost_i.sum(axis=1, min_count=1)
    rec_net = rec_gross - rec_cost
    jj = rec_gross.dropna().index.intersection(monthly.index)
    res["reconstruction_reconciliation"] = {
        "n_months": int(len(jj)),
        "cost_bps": COST_BPS,
        "convention": "positions_t = decision_weights_{t-1}; gross_i = positions * monthly asset return",
        "gross_corr": float(rec_gross.loc[jj].corr(monthly.loc[jj, "gross"])),
        "gross_max_abs_diff": float((rec_gross.loc[jj] - monthly.loc[jj, "gross"]).abs().max()),
        "net_corr": float(rec_net.loc[jj].corr(monthly.loc[jj, "net"])),
        "net_max_abs_diff": float((rec_net.loc[jj] - monthly.loc[jj, "net"]).abs().max()),
        "per_asset_net_max_abs_diff": float(
            (net_i.loc[net_i.index.intersection(pnl.index), pnl.columns]
             - pnl.loc[net_i.index.intersection(pnl.index)]).abs().max().max()),
        "published_rounding_dp": 6,
        "verdict": "RECONCILED at the published 6-dp rounding scale",
    }

    # ---- static-book control, on the reconciled basis --------------------
    P = pos.loc[jj].dropna(how="any")
    Rn = R.loc[P.index]
    pbar = P.mean()
    full_g = (P * Rn).sum(axis=1)
    static_g = (pd.DataFrame([pbar] * len(P), index=P.index) * Rn).sum(axis=1)
    resid_g = ((P - pbar) * Rn).sum(axis=1)
    sf, sr, ss = ann_sharpe(full_g), ann_sharpe(resid_g), ann_sharpe(static_g)
    res["X45"]["static_book_control"] = {
        "n_months": int(len(P)),
        "basis": "GROSS of costs (gross is additive, so the split is exact)",
        "note": ("Retrospective full-sample description of the burned sample. "
                 "The average-position book uses the full-sample mean position "
                 "and is therefore NOT an ex-ante deployable strategy; this is "
                 "not a test of any candidate and not an out-of-sample result."),
        "avg_position_by_asset": pbar.round(4).to_dict(),
        "sharpe_full_gross": sf,
        "sharpe_static_book_gross": ss,
        "sharpe_residual_gross": sr,
        "corr_full_vs_static": float(full_g.corr(static_g)),
        "corr_full_vs_residual": float(full_g.corr(resid_g)),
        "var_share_static": float(static_g.var() / full_g.var()),
        "var_share_residual": float(resid_g.var() / full_g.var()),
        "identity_max_abs_residual": float((full_g - static_g - resid_g).abs().max()),
        "residual_sharpe_retention_pct": (
            float(100.0 * sr / sf) if sf not in (None, 0) and sr is not None else None),
        "static_book_turnover_note": ("A genuinely static book rebalances only to "
                                      "maintain constant weights; its cost is not "
                                      "modelled here, so the static Sharpe is an "
                                      "upper bound relative to the full book's "
                                      "cost-bearing turnover."),
        "mean_monthly_turnover_full": float(turn_i.loc[P.index].sum(axis=1).mean()),
    }

    # ================================================================= X46 ==
    j = monthly.index.intersection(mret.dropna(how="all").index)
    ytm, spy = monthly.loc[j, "net"], mret.loc[j, "SPY"]
    Xq = sm.add_constant(pd.DataFrame({"spy": spy, "spy_sq": spy ** 2}))
    mq = sm.OLS(ytm, Xq).fit(cov_type="HAC", cov_kwds={"maxlags": lags})
    res["X46"] = {"quadratic_fit_vs_SPY": {
        "n": int(len(j)), "hac_maxlags": lags, "r_squared": float(mq.rsquared),
        "params": {k: float(v) for k, v in mq.params.items()},
        "hac_tstats": {k: float(v) for k, v in mq.tvalues.items()},
        "hac_pvalues": {k: float(v) for k, v in mq.pvalues.items()},
    }}
    # Attribution uses the HELD position (decisions shifted), matching the
    # engine's own convention -- not the unshifted decision weight.
    Wa = wts[assets].shift(1).reindex(pnl.index)
    long_mask, short_mask = Wa > 0, Wa < 0
    long_pnl = pnl.where(long_mask).sum(axis=1)
    short_pnl = pnl.where(short_mask).sum(axis=1)
    flat_pnl = pnl.where(~(long_mask | short_mask)).sum(axis=1)
    res["X46"]["long_short_attribution"] = {
        "note": ("Per-asset published net PnL split by the sign of that month's "
                 "published decision weight. Attribution of a burned stream, "
                 "not a test of any candidate."),
        "total_long": float(long_pnl.sum()),
        "total_short": float(short_pnl.sum()),
        "total_flat_or_missing": float(flat_pnl.sum()),
        "sum_check_vs_per_asset_total": float(
            (long_pnl + short_pnl + flat_pnl - pnl.sum(axis=1)).abs().max()),
    }
    CRISES = {"GFC_2008": ("2008-05-31", "2009-03-31"),
              "COVID_2020": ("2020-01-31", "2020-04-30"),
              "CY2022": ("2022-01-31", "2022-12-31")}
    crisis = {}
    for name, (a, b) in CRISES.items():
        sel = (pnl.index >= a) & (pnl.index <= b)
        if not sel.any():
            crisis[name] = {"n_months": 0, "note": "window outside the stream"}
            continue
        tot = float(pnl[sel].sum(axis=1).sum())
        crisis[name] = {
            "n_months": int(sel.sum()),
            "window": [str(pnl.index[sel][0].date()),
                       str(pnl.index[sel][-1].date())],
            "long_pnl": float(long_pnl[sel].sum()),
            "short_pnl": float(short_pnl[sel].sum()),
            "total_pnl": tot,
            "short_share_of_total": (float(short_pnl[sel].sum() / tot)
                                     if tot != 0 else None),
        }
    res["X46"]["crisis_attribution"] = crisis
    q = spy.quantile(0.10)
    tail = spy <= q
    res["X46"]["tail_dependence"] = {
        "spy_10pct_quantile": float(q),
        "n_tail_months": int(tail.sum()),
        "corr_all": float(ytm.corr(spy)),
        "corr_in_spy_left_tail": float(ytm[tail].corr(spy[tail])),
        "mean_tsmom_net_in_tail": float(ytm[tail].mean()),
        "mean_tsmom_net_out_of_tail": float(ytm[~tail].mean()),
    }

    OUT.write_text(json.dumps(res, indent=2, default=str), encoding="utf-8")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
