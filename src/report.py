"""Assemble the human-readable markdown report from all analysis artifacts."""

from __future__ import annotations

import datetime as dt

import pandas as pd

import config


def _md_table(df: pd.DataFrame, index_label: str | None = None) -> str:
    d = df.copy()
    if index_label is not None:
        d.index.name = index_label
        d = d.reset_index()
    def cell(v) -> str:
        if pd.isna(v):
            return ""
        # Escape pipes so values like "|corr|=0.85" don't break the table.
        return str(v).replace("|", "\\|")

    cols = list(d.columns)
    head = "| " + " | ".join(str(c) for c in cols) + " |"
    sep = "| " + " | ".join("---" for _ in cols) + " |"
    body = "\n".join(
        "| " + " | ".join(cell(v) for v in row) + " |"
        for row in d.itertuples(index=False, name=None)
    )
    return "\n".join([head, sep, body])


def write_report(
    *,
    quality: pd.DataFrame,
    fetch_results,
    common_start: pd.Timestamp,
    common_end: pd.Timestamp,
    n_common_days: int,
    corr: pd.DataFrame,
    pairs: pd.DataFrame,
    clusters: pd.DataFrame,
    eff_counts: dict[float, int],
    rec_table: pd.DataFrame,
    keep: list[str],
    drop: list[str],
    coverage: dict[str, list[str]],
    borderline: list[tuple[str, str, float]],
) -> None:
    L: list[str] = []
    add = L.append

    add("# Multi-Asset TSMOM — Step 1: Data, Correlation & Universe Screening")
    add("")
    add(f"*Generated: {dt.datetime.now():%Y-%m-%d %H:%M}*  ")
    add(f"*Universe: {len(config.TICKERS)} ETFs. Source: yfinance (adjusted Close, "
        "`auto_adjust=True`).*  ")
    add("*Scope: data acquisition + correlation analysis + screening **suggestions** only. "
        "No strategy, no signals, no backtest. Nothing is auto-dropped.*")
    add("")

    # ----- fetch status -----
    failed = [r for r in fetch_results if not r.ok]
    add("## 0. Fetch status")
    if failed:
        add(f"**{len(failed)} ticker(s) failed to download:**")
        for r in failed:
            add(f"- `{r.ticker}` — {r.error}")
    else:
        add(f"All {len(fetch_results)} tickers fetched successfully.")
    add("")

    # ----- data quality -----
    add("## 1. Data quality")
    add("")
    short = quality.index[quality["short_history_flag"]].tolist()
    jumpy = quality.index[quality["n_jumps"] > 0].tolist()
    spiky = quality.index[quality["n_spike_revert"] > 0].tolist()
    add(f"- **Short-history flags** (start after {config.LATE_START_FLAG}): "
        + (", ".join(f"`{t}`" for t in short) if short else "none"))
    add(f"- **Daily-jump anomalies** (|return| > {config.JUMP_THRESHOLD:.0%}): "
        + (", ".join(f"`{t}`" for t in jumpy) if jumpy else "none"))
    add(f"- **Suspected bad prints** (spike-and-revert, both legs > "
        f"{config.SPIKE_REVERT_MOVE:.0%}): "
        + (", ".join(f"`{t}`" for t in spiky) if spiky else "none"))
    add("")
    add(_md_table(
        quality[["factor", "start_date", "end_date", "n_trading_days",
                 "internal_missing", "short_history_flag", "n_jumps",
                 "max_abs_daily_move", "max_move_date", "n_spike_revert",
                 "spike_revert_detail"]],
        index_label="ticker",
    ))
    add("")
    add("> `internal_missing` = NaNs inside a ticker's own [start,end] span measured "
        "against the union trading calendar (i.e. days peers traded but this ETF did not).")
    if spiky:
        add("")
        add("**Suspected data errors to eyeball before use:**")
        for t in spiky:
            add(f"- `{t}`: {quality.loc[t, 'spike_revert_detail']} "
                "— big move offset by a big opposite move next day (round-trip = likely bad tick).")
    add("")

    # ----- common period -----
    add("## 2. Common analysis period")
    add("")
    add(f"Correlation is computed only where **all tickers overlap**:")
    add("")
    add(f"- **{common_start.date()} → {common_end.date()}**")
    add(f"- **{n_common_days} common trading days** (~{n_common_days/252:.1f} years)")
    add("")
    binding = quality.loc[quality["start_date"] == common_start.date().isoformat()].index.tolist()
    if binding:
        add(f"The window is bounded by the youngest ETF(s): {', '.join(f'`{t}`' for t in binding)}.")
        add("")

    # ----- correlation -----
    add("## 3. Correlation matrix")
    add("")
    add(f"Computed on **daily simple returns** (`pct_change`), method = {config.CORR_METHOD}. "
        "Returns, not price levels, are used — price correlation is spuriously inflated by "
        "common trends.")
    add("")
    add(f"- Full matrix: [`correlation_matrix.csv`]({config.CORRELATION_CSV.name})")
    add(f"- Heatmap (clustered order): [`correlation_heatmap.png`]({config.HEATMAP_PNG.name})")
    add("")

    # ----- high corr pairs -----
    strong = pairs[pairs["band"] == "strong"].reset_index(drop=True)
    moderate = pairs[pairs["band"] == "moderate"].reset_index(drop=True)
    add("## 4. 'Fake diversification' — high-correlation pairs")
    add("")
    add(f"### 4a. Strong / redundant — |r| ≥ {config.HIGH_CORR_STRONG:.2f}  "
        f"({len(strong)} pairs)")
    add("")
    add(_md_table(strong[["asset_a", "asset_b", "corr", "factor_a", "factor_b"]])
        if not strong.empty else "_none_")
    add("")
    add(f"### 4b. Moderate — {config.HIGH_CORR_MODERATE:.2f} ≤ |r| < {config.HIGH_CORR_STRONG:.2f}  "
        f"({len(moderate)} pairs)")
    add("")
    add(_md_table(moderate[["asset_a", "asset_b", "corr", "factor_a", "factor_b"]])
        if not moderate.empty else "_none_")
    add("")
    add("> Bands use **|r|** so inverse pairs (negative correlation) count as redundant.")
    add("")

    # ----- clustering -----
    add("## 5. Hierarchical clustering — effective independent factors")
    add("")
    add(f"Average linkage on distance `d = 1 - corr`. Dendrogram: "
        f"[`dendrogram.png`]({config.DENDROGRAM_PNG.name}). Cluster assignments: "
        f"[`clusters.csv`]({config.CLUSTERS_CSV.name}).")
    add("")
    add("**Number of clusters when the tree is cut at each co-movement tolerance:**")
    add("")
    add("| cut @ correlation | distance | # clusters (≈ independent groups) |")
    add("| --- | --- | --- |")
    for c in config.CLUSTER_CORR_THRESHOLDS:
        add(f"| {c:.2f} | {1-c:.2f} | {eff_counts[c]} |")
    add("")
    mid = config.HIGH_CORR_MODERATE
    add(f"**Read:** at a corr≈{mid:.2f} tolerance the 30 ETFs collapse into "
        f"**~{eff_counts[mid]} effective groups** — that is the honest count of "
        "independent risk bets this universe actually offers, far fewer than 30.")
    add("")

    # ----- recommendations -----
    add("## 6. Screening suggestion (for your confirmation)")
    add("")
    add(f"Greedy correlation filter: assets are processed in keep-priority order and an asset "
        f"is dropped only if |r| ≥ {config.HIGH_CORR_STRONG:.2f} with an asset **already kept** "
        "(pairwise, not transitive — so distinct regional equities are not chained together).")
    add("")
    add(f"- **Suggested KEEP ({len(keep)})**: " + ", ".join(f"`{t}`" for t in keep))
    add(f"- **Suggested DROP candidates ({len(drop)})**: "
        + (", ".join(f"`{t}`" for t in drop) if drop else "none"))
    add("")
    add(_md_table(
        rec_table[["factor", "decision", "nearest_kept", "corr_with_kept", "reason"]],
        index_label="ticker",
    ))
    add("")

    # ----- optional tighter trim -----
    add(f"### 6a. Optional further trim → ~20 (borderline keeps, "
        f"{config.BORDERLINE_CORR:.2f} ≤ |r| < {config.HIGH_CORR_STRONG:.2f})")
    add("")
    if borderline:
        add("These survive the 0.80 filter but still co-move strongly with a kept anchor. A "
            "tighter, more-independent universe could drop the ones that are not the sole "
            "representative of their factor:")
        add("")
        add("| ticker | factor | closest kept | corr |")
        add("| --- | --- | --- | --- |")
        for t, partner, r in borderline:
            add(f"| `{t}` | {config.ASSET_UNIVERSE[t]} | `{partner}` | {r:+.2f} |")
    else:
        add("_No borderline keeps._")
    add("")

    add("### Factor coverage of the suggested-keep set")
    add("")
    for fac in sorted(coverage):
        add(f"- **{fac}**: " + ", ".join(f"`{t}`" for t in coverage[fac]))
    add("")
    add("> These are suggestions. No data or asset has been removed. Confirm the keep/drop "
        "list before step 2 (momentum signal construction).")
    add("")

    config.REPORT_MD.write_text("\n".join(L), encoding="utf-8")
