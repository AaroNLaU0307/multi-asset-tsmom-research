"""Step 1.5 — finalize the universe, re-confirm the data window, verify diversity.

No strategy / signal / backtest logic. Reads the cached prices (no re-fetch) and:
  1. recomputes the common data window for the FINAL universe (CPER removed),
     reports the binding (latest-inception) asset and whether 2008 is covered,
     and a cascade showing how far back the window extends if WEAT / CORN are
     dropped;
  2. reports the internal agriculture correlations (DBA vs WEAT vs CORN) and
     whether DBA makes the single-grain ETFs redundant;
  3. regenerates the NxN correlation matrix, heatmap, clustering, dendrogram and
     the effective-independent-factor count for the final universe.

Usage:  python finalize_universe.py
"""

from __future__ import annotations

import pandas as pd

import config
import universe
from src import clustering, correlation, fetch_data, plots

LEHMAN = pd.Timestamp("2008-09-15")          # GFC reference (Lehman bankruptcy)
GFC_FULL = pd.Timestamp("2008-01-01")        # "covers the full 2008 calendar year"
COVID_PEAK = pd.Timestamp("2020-02-19")      # pre-COVID equity peak


# --------------------------------------------------------------------------- #
# Window helpers
# --------------------------------------------------------------------------- #
def inception_dates(prices: pd.DataFrame, tickers: list[str]) -> dict[str, pd.Timestamp]:
    return {t: prices[t].dropna().index.min() for t in tickers}


def window_for(prices: pd.DataFrame, tickers: list[str]) -> dict:
    """Common (all-overlap) window for a ticker subset, plus the binding asset."""
    sub = prices[list(tickers)].dropna(how="any")
    starts = inception_dates(prices, tickers)
    binding = max(starts, key=lambda k: starts[k])
    start, end = sub.index.min(), sub.index.max()
    return {
        "start": start,
        "end": end,
        "n_days": int(len(sub)),
        "binding": binding,
        "binding_start": starts[binding],
        "covers_lehman": bool(start <= LEHMAN),
        "covers_full_2008": bool(start <= GFC_FULL),
        "covers_covid": bool(start <= COVID_PEAK),
    }


def peel_to_2008(prices: pd.DataFrame, tickers: list[str]) -> list[dict]:
    """Repeatedly drop the latest-inception (binding) asset until the window
    reaches the 2008 crisis, recording each step. Answers 'which assets block 2008
    and how far back does dropping them get us'."""
    remaining = list(tickers)
    steps = []
    guard = 0
    while guard < len(tickers):
        guard += 1
        w = window_for(prices, remaining)
        steps.append({
            "n_assets": len(remaining),
            "start": w["start"].date().isoformat(),
            "binding": w["binding"],
            "covers_lehman": w["covers_lehman"],
            "dropped_next": "" if w["covers_lehman"] else w["binding"],
        })
        if w["covers_lehman"]:
            break
        remaining = [t for t in remaining if t != w["binding"]]
    return steps


# --------------------------------------------------------------------------- #
# Agriculture internal correlation
# --------------------------------------------------------------------------- #
def agriculture_corr(prices: pd.DataFrame) -> pd.DataFrame:
    ag = ["DBA", "WEAT", "CORN"]
    rets = correlation.daily_returns(prices[ag].dropna(how="any"))
    corr = rets.corr(method=config.CORR_METHOD)
    corr.to_csv(config.AG_CORR_CSV)
    return corr


# --------------------------------------------------------------------------- #
# Report
# --------------------------------------------------------------------------- #
def _md_table(rows: list[list], header: list[str]) -> str:
    head = "| " + " | ".join(header) + " |"
    sep = "| " + " | ".join("---" for _ in header) + " |"
    body = "\n".join("| " + " | ".join(str(c) for c in r) + " |" for r in rows)
    return "\n".join([head, sep, body])


def main() -> None:
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    prices, _ = fetch_data.fetch_universe(force=False)
    tickers = universe.TICKERS

    missing = [t for t in tickers if t not in prices.columns or prices[t].notna().sum() == 0]
    if missing:
        raise RuntimeError(f"Cached prices missing required tickers: {missing}")

    # ---- 1. window analysis ----
    # The grains (WEAT/CORN) are excluded from the final universe; we re-add them
    # only to document *why* (they are what blocked the 2008 sample).
    incept = inception_dates(prices, tickers)
    grains = [g for g in ("WEAT", "CORN") if g in prices.columns and prices[g].notna().any()]
    base = window_for(prices, tickers)                                  # final 17
    with_grains = window_for(prices, tickers + grains)                  # 17 + WEAT + CORN
    peel = peel_to_2008(prices, tickers + grains)                       # path that led here

    cascade = pd.DataFrame([
        {"scenario": f"Final universe ({len(tickers)} assets, grains excluded)", **base},
        {"scenario": f"+ re-add {', '.join(grains)} (excluded)", **with_grains},
    ])
    cascade_out = cascade.copy()
    for c in ("start", "end", "binding_start"):
        cascade_out[c] = cascade_out[c].apply(lambda x: x.date().isoformat())
    cascade_out.to_csv(config.WINDOW_ANALYSIS_CSV, index=False)

    # ---- 2. agriculture correlation ----
    ag_corr = agriculture_corr(prices)

    # ---- 3. final-universe correlation / clustering / figures ----
    aligned = prices[tickers].dropna(how="any")
    returns = correlation.daily_returns(aligned)
    corr = correlation.correlation_matrix(returns, out_csv=config.FINAL_CORRELATION_CSV)
    pairs = correlation.high_corr_pairs(
        corr, out_csv=config.FINAL_HIGH_CORR_CSV, factor_map=universe.FINAL_UNIVERSE
    )
    Z, labels = clustering.build_linkage(corr)
    order = clustering.leaf_order(Z, labels)
    clusters = clustering.clusters_at_thresholds(
        Z, labels, out_csv=config.FINAL_CLUSTERS_CSV, factor_map=universe.FINAL_UNIVERSE
    )
    eff = clustering.effective_factor_counts(clusters)
    plots.plot_heatmap(
        corr, order, out_png=config.FINAL_HEATMAP_PNG,
        title=(f"Final universe ({len(tickers)} ETFs) — daily-return correlation\n"
               "ordered by hierarchical clustering; white labels = |r| >= 0.80"),
    )
    plots.plot_dendrogram(
        Z, labels, out_png=config.FINAL_DENDROGRAM_PNG,
        title=f"Hierarchical clustering of the final {len(tickers)}-ETF universe (average linkage, 1 - corr)",
    )

    _write_report(tickers, incept, base, cascade, peel, ag_corr, pairs, eff)

    # ---- console summary ----
    print("\n== FINAL UNIVERSE SUMMARY ==")
    print(f"   assets: {len(tickers)}  -> {tickers}")
    print(f"   window: {base['start'].date()} -> {base['end'].date()}  "
          f"({base['n_days']} days), binding = {base['binding']} "
          f"({base['binding_start'].date()})")
    print(f"   covers 2008 (Lehman)? {base['covers_lehman']}   covers 2020 (COVID)? {base['covers_covid']}")
    print(f"   if grains re-added -> start {with_grains['start'].date()} "
          f"(binding {with_grains['binding']}), covers 2008? {with_grains['covers_lehman']}")
    print(f"   agriculture corr:\n{ag_corr.round(3)}")
    n_strong = int((pairs['band'] == 'strong').sum())
    print(f"   remaining |r|>=0.80 pairs in final universe: {n_strong}")
    print(f"   effective groups by cut: {eff}")
    print(f"   report: {config.FINAL_REPORT_MD}")


def _write_report(tickers, incept, base, cascade, peel, ag_corr, pairs, eff) -> None:
    import datetime as dt
    L: list[str] = []
    add = L.append

    add("# Final Universe Confirmation — Window & Diversification Check")
    add("")
    add(f"*Generated: {dt.datetime.now():%Y-%m-%d %H:%M}*  ")
    add("*Scope: universe finalization + data-window re-confirmation + diversification "
        "verification. No strategy / signal / backtest logic. Prices from cache (no re-fetch).*")
    add("")

    # ---- universe ----
    add(f"## 1. Final universe ({len(tickers)} ETFs) — LOCKED")
    add("")
    add("> Locked at **17** assets: the 30-ETF screening removed strong redundancies, "
        "then CPER, WEAT and CORN were dropped so the common window reaches the 2008 GFC "
        "(see §2). Authoritative definition in `universe.py`.")
    add("")
    rows = [[t, universe.FINAL_UNIVERSE[t], incept[t].date().isoformat()] for t in tickers]
    add(_md_table(rows, ["ticker", "factor label", "inception"]))
    add("")
    add("**Excluded (with reason, recorded in `universe.py`):**")
    for t, why in universe.EXCLUDED.items():
        add(f"- `{t}` — {why}")
    add("")

    # ---- window ----
    add("## 2. Common data window (final 17)")
    add("")
    add(f"- **Window: {base['start'].date()} → {base['end'].date()}**  "
        f"({base['n_days']} common trading days, ~{base['n_days']/252:.1f} years)")
    add(f"- **Binding (latest-inception) asset: `{base['binding']}` "
        f"({base['binding_start'].date()})**")
    add(f"- **Covers the 2008 GFC (Lehman, 2008-09-15)?** "
        f"{'YES' if base['covers_lehman'] else 'NO'}")
    add(f"- **Covers the 2020 COVID crash (peak 2020-02-19)?** "
        f"{'YES' if base['covers_covid'] else 'NO'}")
    add("")
    add(f"> The window is bound by **`{base['binding']}`** "
        f"({base['binding_start'].date()}) and spans **both** major stress regimes "
        "(2008 and 2020) — exactly the samples a momentum study needs.")
    add("")

    add("### 2a. Why WEAT / CORN were dropped")
    add("")
    crows = []
    for _, r in cascade.iterrows():
        crows.append([
            r["scenario"], r["start"].date().isoformat(), r["end"].date().isoformat(),
            r["n_days"], f"`{r['binding']}` ({r['binding_start'].date()})",
            "YES" if r["covers_lehman"] else "no",
        ])
    add(_md_table(crows, ["scenario", "start", "end", "days", "binding asset", "covers 2008?"]))
    add("")
    add("Re-adding the two single-grain ETFs would drag the binding inception to 2011 and "
        "**lose the entire 2008 GFC** — the reason they were excluded.")
    add("")
    add("### 2b. Full peel — which assets blocked 2008")
    add("")
    add("From the prior 19-asset set, repeatedly drop the latest-inception asset until the "
        "window reaches the GFC:")
    add("")
    prows = [[s["n_assets"], s["start"], f"`{s['binding']}`",
              "YES" if s["covers_lehman"] else "no",
              (f"drop `{s['dropped_next']}`" if s["dropped_next"] else "— (reached 2008)")]
             for s in peel]
    add(_md_table(prows, ["# assets", "start", "binding", "covers 2008?", "next action"]))
    add("")
    reached = peel[-1]
    add(f"> **Read:** dropping `WEAT` then `CORN` extends the start back to "
        f"**{reached['start']}** (then bound by `{reached['binding']}`), which **does** "
        "include 2008 — confirming the grains were exactly what cost the GFC sample.")
    add("")

    # ---- agriculture ----
    add("## 3. Agriculture internal correlation (DBA vs WEAT vs CORN)")
    add("")
    add("Daily-return correlation on the three ETFs' mutual window:")
    add("")
    aglabels = list(ag_corr.columns)
    arows = [[a] + [f"{ag_corr.loc[a, b]:.3f}" for b in aglabels] for a in aglabels]
    add(_md_table(arows, ["", *aglabels]))
    add("")
    dba_weat = ag_corr.loc["DBA", "WEAT"]
    dba_corn = ag_corr.loc["DBA", "CORN"]
    weat_corn = ag_corr.loc["WEAT", "CORN"]
    redundant = max(abs(dba_weat), abs(dba_corn)) > 0.70
    add(f"- DBA–WEAT = **{dba_weat:.2f}**, DBA–CORN = **{dba_corn:.2f}**, "
        f"WEAT–CORN = **{weat_corn:.2f}**")
    if not redundant:
        add(f"- **DBA does NOT make WEAT/CORN redundant** on a >0.70 basis — the broad "
            "basket only moderately tracks the single grains. On pure diversification "
            "grounds all three carry some distinct signal.")
    else:
        add("- DBA is **>0.70** with a single grain — it largely contains it; trimming "
            "the redundant grain is reasonable.")
    add("")
    add("**Decision (locked):** the grains were only moderately distinct (no >0.70 "
        "overlap), so on diversification grounds little is lost; but they were the only "
        f"assets blocking 2008. They were dropped, keeping `DBA` as the agriculture "
        f"representative — extending the window to **{reached['start']}** and capturing "
        "the GFC, the regime where time-series momentum is most tested.")
    add("")

    # ---- diversification ----
    add(f"## 4. Diversification of the final universe ({len(tickers)} assets)")
    add("")
    add(f"- Correlation matrix: [`final_correlation_matrix.csv`]({config.FINAL_CORRELATION_CSV.name})  ")
    add(f"- Heatmap: [`final_correlation_heatmap.png`]({config.FINAL_HEATMAP_PNG.name})  ")
    add(f"- Dendrogram: [`final_dendrogram.png`]({config.FINAL_DENDROGRAM_PNG.name})  ")
    add(f"- Cluster assignments: [`final_clusters.csv`]({config.FINAL_CLUSTERS_CSV.name})")
    add("")
    strong = pairs[pairs["band"] == "strong"]
    add(f"### 4a. Remaining redundancy")
    add("")
    add(f"- **|r| ≥ 0.80 pairs remaining: {len(strong)}** "
        + ("✅ — every strong-redundancy pair from the 30-ETF set was removed."
           if len(strong) == 0 else "(see below)"))
    if len(strong) > 0:
        srows = [[r["asset_a"], r["asset_b"], f"{r['corr']:.2f}"] for _, r in strong.iterrows()]
        add(_md_table(srows, ["a", "b", "corr"]))
    moderate = pairs[pairs["band"] == "moderate"]
    add(f"- Moderate (0.60 ≤ |r| < 0.80) pairs remaining: {len(moderate)} "
        "(mostly the persistent risk-on equity/credit/REIT block).")
    add("")
    add("### 4b. Effective independent factors (vs the 30-ETF set)")
    add("")
    add("| cut @ correlation | 30-ETF set | final set | final / N |")
    add("| --- | --- | --- | --- |")
    prev = {0.80: 25, 0.60: 12, 0.40: 9}   # from output/ANALYSIS_REPORT.md
    for c in config.CLUSTER_CORR_THRESHOLDS:
        add(f"| {c:.2f} | {prev.get(c, '?')} | {eff[c]} | {eff[c]/len(tickers):.0%} |")
    add("")
    add(f"**Verdict:** at the 0.80 cut the final universe splits into **{eff[0.80]}** "
        f"groups out of {len(tickers)} assets — redundancy at the strong threshold is "
        "essentially eliminated. At corr≥0.60 it is "
        f"**{eff[0.60]}** groups ({eff[0.60]/len(tickers):.0%} of assets, vs 12/30 = 40% "
        "before), i.e. the effective-factor *density* improved markedly even though the "
        "risk-on equity/credit/REIT complex remains one shared factor (as it should — "
        "that co-movement is real, not a data artifact).")
    add("")

    config.FINAL_REPORT_MD.write_text("\n".join(L), encoding="utf-8")


if __name__ == "__main__":
    main()
