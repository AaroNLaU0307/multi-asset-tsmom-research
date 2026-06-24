"""Phase 1A — daily research infrastructure for the vol-compression breakout (strategy B).

Builds the daily primitives REUSING the existing universe/loader/regime code, then
verifies (i) the primitives are strictly causal (truncation-invariant) and (ii) the
daily returns aggregate back to the validated monthly engine's returns. READ-ONLY
infra; no strategy, no positions, no P&L. Then PAUSE.

Run:  python run_breakout_phase1a.py
"""

from __future__ import annotations

import sys

import numpy as np
import pandas as pd

import config
import universe
from src import daily, fetch_data


def _truncation_invariance(px: pd.DataFrame, fn, cut_frac: float = 0.7) -> float:
    """Recompute a primitive on a price prefix; return max abs diff at the overlap.
    0.0 => the primitive at date t uses only data <= t (no look-ahead)."""
    full = fn(px)
    cut = px.index[int(len(px) * cut_frac)]
    trunc = fn(px.loc[:cut])
    common = trunc.index.intersection(full.index)
    a, b = full.loc[common], trunc.loc[common]
    if isinstance(a, pd.DataFrame):
        a, b = a[trunc.columns], b[trunc.columns]
    return float(np.nanmax((a - b).abs().to_numpy())) if len(common) else float("nan")


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    prices, _ = fetch_data.fetch_universe(force=False)
    px = prices[universe.TICKERS]

    # ---- 1. coverage ----
    cov = pd.DataFrame({
        "first": px.apply(lambda c: c.first_valid_index()),
        "last": px.apply(lambda c: c.last_valid_index()),
        "n_obs": px.notna().sum(),
    }).sort_values("first")
    allp = px.dropna(how="any")
    common_start, common_end = allp.index.min(), allp.index.max()
    short = cov[cov["first"] > pd.Timestamp("2006-01-01")].index.tolist()

    # ---- 2. causal primitives + truncation invariance ----
    prim_checks = {
        "daily_returns": _truncation_invariance(px, daily.daily_returns),
        "realized_vol": _truncation_invariance(px, daily.realized_vol),
        "vol_percentile": _truncation_invariance(px, daily.vol_percentile),
        "recent_high": _truncation_invariance(px, daily.recent_high),
        "recent_low": _truncation_invariance(px, daily.recent_low),
    }
    causal_ok = max(prim_checks.values()) < 1e-12

    # ---- 3. daily -> monthly reconciliation ----
    rec = daily.reconcile_daily_to_monthly(px)
    recon_ok = rec["max_abs_diff"] <= config.DAILY_RECONCILE_TOL

    # ---- sample artifact (one liquid asset's primitives, recent rows) ----
    tkr = "SPY"
    sample = pd.DataFrame({
        "close": px[tkr],
        "ret": daily.daily_returns(px)[tkr],
        "realized_vol": daily.realized_vol(px)[tkr],
        "vol_pctile": daily.vol_percentile(px)[tkr],
        "recent_high_20": daily.recent_high(px)[tkr],
        "recent_low_20": daily.recent_low(px)[tkr],
        "compressed": daily.is_compressed(px)[tkr],
    }).dropna().tail(200)
    sample.round(6).to_csv(config.DAILY_PRIMITIVES_CSV)

    # ---- console ----
    print("\n===============  PHASE 1A — DAILY INFRA (reuse + verify)  ===============")
    print(f"  source: {config.RAW_PRICES_CSV.name} (cached yfinance adj-close, same as monthly engine)")
    print(f"  daily frame: {px.shape[0]} rows x {px.shape[1]} assets  "
          f"{px.index.min().date()} -> {px.index.max().date()}")
    print(f"  all-17-present daily window: {common_start.date()} -> {common_end.date()} ({len(allp)} rows)")
    print(f"  short daily history (<2006): {short if short else 'none'}; window bound by UNG (2007-04-18)")
    print(f"\n  causal primitives — truncation invariance (max abs diff vs prefix):")
    for k, v in prim_checks.items():
        print(f"    {k:16} {v:.2e}")
    print(f"    => strictly causal / no look-ahead: {causal_ok}")
    print(f"\n  daily->monthly reconciliation (compounded daily vs to_monthly().pct_change()):")
    print(f"    max abs diff = {rec['max_abs_diff']:.2e} over {rec['n_obs']} asset-months "
          f"({rec['n_months']} months x {rec['n_assets']} assets)")
    print(f"    => reconciles within tol {config.DAILY_RECONCILE_TOL:.0e}: {recon_ok}")
    if not recon_ok:
        print("  ABORT: daily data does not reconcile with the monthly engine. STOP.")
        sys.exit(1)

    # ---- report ----
    L = ["# Phase 1A — Daily research infrastructure (vol-compression breakout)", "",
         "*Read-only infra. Reuses the existing 17-ETF universe, the cached daily adjusted-close "
         "loader (same source the monthly engine resamples), and the verified-causal regime "
         "primitives. No strategy/positions/P&L.*", "",
         "## Data coverage", "",
         f"- Source: `{config.RAW_PRICES_CSV.name}` — cached yfinance adjusted close, identical to "
         "the monthly backtest's source (so daily and monthly stay reconcilable).",
         f"- Daily frame: **{px.shape[0]} rows × {px.shape[1]} assets**, "
         f"{px.index.min().date()} → {px.index.max().date()}.",
         f"- **All-17-present daily window: {common_start.date()} → {common_end.date()}** "
         f"({len(allp)} trading days), bound by UNG's 2007-04-18 inception — the same bound as the "
         "monthly engine.",
         f"- Short daily history (post-2006 inception): {', '.join(short)}. No tickers are dropped; "
         "the common window already accounts for them.", "",
         "## Causal daily primitives (truncation-invariance)", "",
         "All trailing-window only; breakout references exclude the current day. Recomputing each on "
         "a 70% price prefix reproduces the full-data values exactly at the overlap:", "",
         "| primitive | max abs diff vs prefix |", "| --- | --- |"]
    for k, v in prim_checks.items():
        L.append(f"| `{k}` | {v:.2e} |")
    L += ["",
          f"**Strictly causal / no look-ahead: {causal_ok}.** Built: daily returns, realized vol "
          f"(window {config.COMPRESSION_VOL_WINDOW}d), vol percentile (trailing {config.COMPRESSION_PCTILE_WINDOW}d "
          "rank = the compression measure), recent-high / recent-low "
          f"({config.BREAKOUT_LOOKBACK}d Donchian breakout references).", "",
          "## Daily → monthly reconciliation (ties to the validated engine)", "",
          f"- Compounding daily simple returns within each month vs the engine's "
          "`to_monthly(px).pct_change()`:",
          f"- **max abs diff = {rec['max_abs_diff']:.2e}** over {rec['n_obs']} asset-months "
          f"({rec['n_months']} months × {rec['n_assets']} assets) → reconciles (telescoping "
          "identity). The daily data is consistent with the monthly engine.", "",
          f"Sample primitives (SPY, last 200 rows): [`{config.DAILY_PRIMITIVES_CSV.name}`]"
          f"({config.DAILY_PRIMITIVES_CSV.name}).", "",
          "## Conventions (stated up front, NOT searched)", "",
          f"- compression vol window = {config.COMPRESSION_VOL_WINDOW}d; percentile window = "
          f"{config.COMPRESSION_PCTILE_WINDOW}d; compressed = percentile ≤ {config.COMPRESSION_THRESHOLD}.",
          f"- breakout lookback = {config.BREAKOUT_LOOKBACK}d; premise horizons = "
          f"{config.PREMISE_HORIZONS} days.",
          "- Compression uses realized-vol percentile (adjusted-close data has no intraday H/L for a "
          "true ATR); same verified definition style as the Step-5 regime vars."]
    config.BREAKOUT_PHASE1A_MD.write_text("\n".join(L), encoding="utf-8")
    print(f"\n  report: {config.BREAKOUT_PHASE1A_MD}")


if __name__ == "__main__":
    main()
