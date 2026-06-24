"""Step-1 pipeline orchestrator.

Run order:
  1. fetch adjusted Close (cached)        -> data/close_prices_raw.csv
  2. data quality table                   -> output/data_quality.csv
  3. common analysis period (date-align)
  4. daily-return correlation matrix      -> output/correlation_matrix.csv
  5. hierarchical clustering + dendrogram -> output/clusters.csv, dendrogram.png
  6. clustered correlation heatmap        -> output/correlation_heatmap.png
  7. high-correlation pair lists          -> output/high_corr_pairs.csv
  8. screening suggestion                 -> output/recommendations.csv
  9. markdown report                      -> output/ANALYSIS_REPORT.md

Usage:
  python run_analysis.py            # uses cached prices if present
  python run_analysis.py --refetch  # force a fresh yfinance pull
"""

from __future__ import annotations

import argparse
import random

import numpy as np

import config
from src import (
    clustering,
    correlation,
    data_quality,
    fetch_data,
    plots,
    recommend,
    report,
)


def main(refetch: bool = False) -> None:
    random.seed(config.RANDOM_SEED)
    np.random.seed(config.RANDOM_SEED)
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("== 1. fetch ==")
    prices, fetch_results = fetch_data.fetch_universe(force=refetch)

    print("== 2. data quality ==")
    quality = data_quality.build_quality_table(prices)

    print("== 3. common period ==")
    c_start, c_end, aligned = data_quality.common_period(prices)
    print(f"   common period: {c_start.date()} -> {c_end.date()}  ({len(aligned)} days)")

    print("== 4. correlation ==")
    returns = correlation.daily_returns(aligned)
    corr = correlation.correlation_matrix(returns)
    pairs = correlation.high_corr_pairs(corr)

    print("== 5. clustering ==")
    Z, labels = clustering.build_linkage(corr)
    order = clustering.leaf_order(Z, labels)
    clusters = clustering.clusters_at_thresholds(Z, labels)
    eff_counts = clustering.effective_factor_counts(clusters)
    plots.plot_dendrogram(Z, labels)

    print("== 6. heatmap ==")
    plots.plot_heatmap(corr, order)

    print("== 7-8. screening suggestion ==")
    rec_table, keep, drop = recommend.build_recommendations(corr)
    cov = recommend.coverage(keep)
    borderline = recommend.borderline_keeps(rec_table)

    print("== 9. report ==")
    report.write_report(
        quality=quality,
        fetch_results=fetch_results,
        common_start=c_start,
        common_end=c_end,
        n_common_days=len(aligned),
        corr=corr,
        pairs=pairs,
        clusters=clusters,
        eff_counts=eff_counts,
        rec_table=rec_table,
        keep=keep,
        drop=drop,
        coverage=cov,
        borderline=borderline,
    )

    print("\n== DONE ==")
    print(f"   effective groups by cut: {eff_counts}")
    print(f"   suggested keep ({len(keep)}): {keep}")
    print(f"   suggested drop ({len(drop)}): {drop}")
    print(f"   report: {config.REPORT_MD}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--refetch", action="store_true", help="force fresh yfinance download")
    args = ap.parse_args()
    main(refetch=args.refetch)
