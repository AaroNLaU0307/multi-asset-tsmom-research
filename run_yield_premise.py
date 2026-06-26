"""Yield-curve slope as a macro-regime conditioner — Step-1 PREMISE TEST (descriptive).

Pre-registered in research/yield_spread/PREREGISTRATION.md. Tests whether the curve-slope
regime (continuous trailing-percentile tercile, state at t-1) relates to FORWARD TSMOM
portfolio returns. DESCRIPTIVE ONLY: no positions, no P&L, no overlay, no tuning.

Decision discipline (locked in the contract):
  * BH-FDR q=0.10 across the 6-cell primary family (2 spreads x 3 horizons x tercile state);
  * economic-magnitude bar |delta annualized| >= 4%/yr;
  * the EVENT-LEVEL leave-one-episode-out jackknife is the DECISIVE gate, ranked ABOVE
    significance: an effect that collapses when the dominant 2022-24 episode is dropped is a
    clean negative however significant it looked;
  * two-sided (H+ crisis-alpha vs H- whipsaw), not a back door;
  * raw slope<0 inversion is a robustness view (flatness != inversion);
  * contemporaneous-vs-predictive confound diagnostics (contemporaneous window + t+21 skip).

Run:  python run_yield_premise.py
"""

from __future__ import annotations

import datetime as dt

import numpy as np
import pandas as pd

import config
import universe
from src import attribution as A, fetch_data, seasonality as S, yields as Y

ANN = config.TRADING_DAYS_PER_YEAR
MAG = config.YIELD_MAGNITUDE_ANN


def _ann(delta_hday: float, h: int) -> float:
    """Annualize an h-day cumulative-return difference (linear: x 252/h)."""
    return float(delta_hday * (ANN / h))


def _sign(x: float) -> int:
    return 0 if (x != x or x == 0) else (1 if x > 0 else -1)


# --------------------------------------------------------------------------- #
# Per-cell statistics (reuses the seasonality HAC + block-bootstrap machinery)
# --------------------------------------------------------------------------- #
def delta_stats(y: np.ndarray, d: np.ndarray, h: int) -> dict:
    test = S.hac_diff_test(y, d, lag=h)
    boot = S.block_bootstrap_ci(y, d, block=h, n_boot=config.SEAS_BOOTSTRAP_N,
                                seed=config.RANDOM_SEED, ci=config.CI_LEVEL)
    return {
        "delta_ann": _ann(test["delta"], h),
        "mean_flat_ann": _ann(test["mean_eff"], h),
        "mean_steep_ann": _ann(test["mean_non"], h),
        "t_hac": test["t"], "p_raw": test["p"],
        "n_flat": test["n_eff"], "n_steep": test["n_non"],
        "boot_lo_ann": _ann(boot["lo"], h), "boot_hi_ann": _ann(boot["hi"], h),
        "boot_crosses_0": boot["crosses_0"],
        "_delta_hday": test["delta"],
    }


def jackknife(y: np.ndarray, d: np.ndarray, dates: pd.DatetimeIndex,
              episodes: list[dict], h: int) -> dict:
    """Leave-one-episode-out on the FLAT group vs all STEEP (the decisive gate)."""
    flat = d == 1
    flat_y, flat_dates = y[flat], dates[flat]
    mean_steep = y[~flat].mean()
    full = flat_y.mean() - mean_steep
    full_sign = _sign(full)

    ep_id = np.full(len(flat_y), -1, dtype=int)
    for k, ep in enumerate(episodes):
        in_ep = (flat_dates >= ep["start"]) & (flat_dates <= ep["end"])
        ep_id[in_ep] = k

    per_ep = []
    for k, ep in enumerate(episodes):
        sel = ep_id == k
        n = int(sel.sum())
        if n == 0:
            continue
        d_alone = flat_y[sel].mean() - mean_steep                       # this episode alone vs steep
        rest = flat_y[~sel]
        d_drop = (rest.mean() - mean_steep) if rest.size else np.nan    # effect after dropping it
        per_ep.append({
            "episode": k, "start": ep["start"].date(), "end": ep["end"].date(),
            "n_flat_obs": n,
            "delta_alone_ann": _ann(d_alone, h), "delta_drop_ann": _ann(d_drop, h),
            "_d_drop": d_drop, "same_sign_as_full": _sign(d_alone) == full_sign,
        })

    finite = [p for p in per_ep if p["_d_drop"] == p["_d_drop"]]
    # BINDING = the episode whose removal most WEAKENS the effect (smallest signed
    # effect after the drop, in the effect's own direction) -> worst-case robustness.
    binding = min(finite, key=lambda p: full_sign * p["_d_drop"]) if (finite and full_sign) else None
    largest = max(per_ep, key=lambda p: p["n_flat_obs"]) if per_ep else None   # biggest by data share
    cov = next((p for p in per_ep if p["start"] <= dt.date(2023, 6, 1) <= p["end"]), None)  # the 2022-24 run

    if binding is not None:
        drop_ann = binding["delta_drop_ann"]
        sign_ok = _sign(binding["_d_drop"]) == full_sign and full_sign != 0
        mag_ok = abs(drop_ann) >= MAG
        pass_jk = bool(sign_ok and mag_ok)
        binding_label = f"#{binding['episode']} {binding['start']}..{binding['end']}"
    else:
        drop_ann, sign_ok, mag_ok, pass_jk, binding_label = np.nan, False, False, False, "n/a"

    n_same = sum(p["same_sign_as_full"] for p in per_ep)
    return {
        "n_episodes": len(per_ep),
        "delta_full_ann": _ann(full, h),
        "binding_episode": binding_label,
        "delta_after_drop_ann": drop_ann,
        "jk_sign_preserved": sign_ok, "jk_magnitude_ok": mag_ok, "pass_jackknife": pass_jk,
        "largest_episode": (f"#{largest['episode']} {largest['start']}..{largest['end']} n={largest['n_flat_obs']}"
                            if largest else "n/a"),
        "delta_drop_largest_ann": (largest["delta_drop_ann"] if largest else np.nan),
        "delta_drop_2022_24_ann": (cov["delta_drop_ann"] if cov else np.nan),
        "n_same_sign_episodes": int(n_same),
        "pass_2episode": bool(n_same >= config.YIELD_MIN_EPISODES),
        "per_episode": per_ep,
    }


def _kept(y_w: pd.Series, st_w: pd.Series):
    """Keep flat/steep observations with a defined outcome; return (y, d, dates)."""
    keep = y_w.notna() & st_w.isin(["flat", "steep"])
    yk, stk = y_w[keep], st_w[keep]
    return yk.to_numpy(float), (stk == "flat").to_numpy().astype(int), yk.index


def main() -> None:
    prices, _ = fetch_data.fetch_universe(force=False)
    px = prices[universe.TICKERS]
    dec = A.decompose(px)
    daily_gross, _ = A.daily_strategy(dec, px)
    daily_gross = daily_gross.dropna().rename("tsmom_gross")
    daily_gross = daily_gross.loc[daily_gross.index >= dec["first_full"]]  # confirmed full-17 window only
    calendar = px.index
    W0, W1 = (pd.Timestamp(config.YIELD_WINDOW[0]), pd.Timestamp(config.YIELD_WINDOW[1]))
    cal_w = calendar[(calendar >= W0) & (calendar <= W1)]

    aligned = Y.align_to_calendar(Y.load_yields(), calendar)
    fwd = {h: Y.forward_cum_return(daily_gross, h) for h in config.YIELD_FWD_HORIZONS}
    bwd = {h: Y.backward_cum_return(daily_gross, h) for h in config.YIELD_FWD_HORIZONS}

    print(f"TSMOM daily gross returns: {daily_gross.index.min().date()} .. "
          f"{daily_gross.index.max().date()}  (n={len(daily_gross)})")
    print(f"Premise window: {W0.date()} .. {W1.date()}  (cal days={len(cal_w)})\n")

    primary, robust, episodes_out = [], [], []
    for name, (lg, sg) in config.YIELD_SPREADS.items():
        sl = Y.slope(aligned, lg, sg)
        state = Y.tercile_state(Y.trailing_pctile(sl))
        state_lag = state.shift(1)
        inv_lag = Y.inversion_state(sl).shift(1)

        for h in config.YIELD_FWD_HORIZONS:
            y_w = fwd[h].reindex(cal_w)
            stl_w = state_lag.reindex(cal_w)

            # episodes: contiguous runs of USABLE flat days over the window calendar
            usable_flat = (stl_w == "flat") & y_w.notna()
            eps = Y.runs_to_episodes(usable_flat.fillna(False), config.YIELD_EPISODE_BRIDGE)

            y, d, dates = _kept(y_w, stl_w)
            st = delta_stats(y, d, h)
            jk = jackknife(y, d, dates, eps, h)

            # confound diagnostics
            yb_w = bwd[h].reindex(cal_w)
            stn_w = state.reindex(cal_w)                       # contemporaneous: state at t
            yc, dc, _ = _kept(yb_w, stn_w)
            contemp_ann = _ann(yc[dc == 1].mean() - yc[dc == 0].mean(), h) if dc.sum() and (1 - dc).sum() else np.nan
            ys_w = fwd[h].shift(-config.YIELD_FWD_SKIP).reindex(cal_w)   # forward-skip: start at t+SKIP
            ys, ds, _ = _kept(ys_w, stl_w)
            skip_ann = _ann(ys[ds == 1].mean() - ys[ds == 0].mean(), h) if ds.sum() and (1 - ds).sum() else np.nan

            row = {"spread": name, "h": h, **st, **{k: v for k, v in jk.items() if k != "per_episode"},
                   "H_label": ("H+ (flat->higher)" if st["delta_ann"] > 0 else "H- (flat->lower)"),
                   "mag_ok": abs(st["delta_ann"]) >= MAG,
                   "contemp_ann": contemp_ann, "skip_ann": skip_ann,
                   "skip_sign_preserved": _sign(skip_ann) == _sign(st["delta_ann"]) and _sign(st["delta_ann"]) != 0}
            primary.append(row)
            for pe in jk["per_episode"]:
                episodes_out.append({"spread": name, "h": h, **pe})

            # raw-inversion robustness (binary slope<0 vs >=0)
            yi, di, _ = _kept(y_w, inv_lag.reindex(cal_w))
            if di.sum() and (1 - di).sum():
                ist = delta_stats(yi, di, h)
                robust.append({"spread": name, "h": h, "delta_ann": ist["delta_ann"],
                               "p_raw": ist["p_raw"], "boot_crosses_0": ist["boot_crosses_0"],
                               "n_inv": int(di.sum()), "n_not": int((1 - di).sum())})

    pf = pd.DataFrame(primary)
    # BH-FDR across the full 6-cell primary family
    p_adj, reject = S.bh_fdr(pf["p_raw"].to_numpy(), q=config.YIELD_FDR_Q)
    pf["p_fdr"] = p_adj
    pf["fdr_reject"] = reject
    pf["g1_sig"] = pf["fdr_reject"] & (~pf["boot_crosses_0"])
    pf["g2_mag"] = pf["mag_ok"]
    pf["g4_event"] = pf["pass_jackknife"] & pf["pass_2episode"]
    pf["g5_predictive"] = pf["skip_sign_preserved"]
    pf["CONFIRMED"] = pf["g1_sig"] & pf["g2_mag"] & pf["g4_event"] & pf["g5_predictive"]

    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    pf.to_csv(config.YIELD_PREMISE_CSV, index=False)
    pd.DataFrame(episodes_out).to_csv(config.YIELD_EPISODES_CSV, index=False)

    pd.set_option("display.width", 200, "display.max_columns", 50)
    show = ["spread", "h", "delta_ann", "p_raw", "p_fdr", "fdr_reject", "mag_ok",
            "n_episodes", "n_same_sign_episodes", "delta_after_drop_ann",
            "binding_episode", "pass_jackknife", "pass_2episode", "CONFIRMED"]
    print("=== PRIMARY family (tercile flat-vs-steep state; 6 cells) ===")
    print(pf[show].to_string(index=False, float_format=lambda x: f"{x:.4f}"))

    print("\n=== EPISODE JACKKNIFE (decisive gate — ranked ABOVE significance) ===")
    for name, (lg, sg) in config.YIELD_SPREADS.items():
        for h in config.YIELD_FWD_HORIZONS:
            r = pf[(pf.spread == name) & (pf.h == h)].iloc[0]
            print(f"\n[{name} h={h}d] full delta={r['delta_full_ann']*100:+.2f}%/yr")
            print(f"   drop BINDING (most-weakening) ep {r['binding_episode']} => {r['delta_after_drop_ann']*100:+.2f}%/yr"
                  f"  | sign kept={r['jk_sign_preserved']} mag_ok(>=4%)={r['jk_magnitude_ok']} => pass_jackknife={r['pass_jackknife']}")
            print(f"   drop LARGEST ep {r['largest_episode']} => {r['delta_drop_largest_ann']*100:+.2f}%/yr"
                  f"   |   drop 2022-24 run => {r['delta_drop_2022_24_ann']*100:+.2f}%/yr")
            print(f"   same-sign episodes={int(r['n_same_sign_episodes'])}/{int(r['n_episodes'])} => pass_2episode={r['pass_2episode']}")
            ep = pd.DataFrame([e for e in episodes_out if e["spread"] == name and e["h"] == h])
            if not ep.empty:
                ep = ep[["episode", "start", "end", "n_flat_obs", "delta_alone_ann", "delta_drop_ann"]]
                print(ep.to_string(index=False, float_format=lambda x: f"{x:.4f}"))

    print("\n=== ROBUSTNESS: raw slope<0 inversion (binary) — flatness != inversion check ===")
    print(pd.DataFrame(robust).to_string(index=False, float_format=lambda x: f"{x:.4f}"))

    print("\n=== CONFOUND diagnostics (forward vs contemporaneous vs t+21 skip; annualized) ===")
    print(pf[["spread", "h", "delta_ann", "contemp_ann", "skip_ann", "skip_sign_preserved"]]
          .to_string(index=False, float_format=lambda x: f"{x:.4f}"))

    n_conf = int(pf["CONFIRMED"].sum())
    n_jk = int(pf["g4_event"].sum())
    print(f"\n=== VERDICT ===  cells CONFIRMED: {n_conf}/6   |   cells passing the event gate: {n_jk}/6")
    print("PREMISE CONFIRMED" if n_conf > 0 else
          "PREMISE NOT CONFIRMED -> clean negative (per contract: STOP, do not build the overlay).")


if __name__ == "__main__":
    main()
