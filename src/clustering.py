"""Hierarchical clustering of the universe on correlation distance.

Distance metric: d = 1 - corr  (range 0..2). Two assets that move together
(corr -> 1) are at distance 0; uncorrelated assets sit at d = 1. Average linkage
is used because it does not assume Euclidean coordinates (unlike Ward) and is a
standard choice for correlation-based asset clustering.

NOTE: this distance uses *signed* correlation, so a strongly negative pair is
treated as far apart. That is intentional for the dendrogram (it reflects
co-movement structure for a long-only diversification read). Redundancy that
comes from inverse exposure (|corr| high, sign negative) is handled separately
in the high-correlation pair list / recommendation step, which uses |corr|.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import dendrogram, fcluster, linkage
from scipy.spatial.distance import squareform

import config


def build_linkage(corr: pd.DataFrame) -> tuple[np.ndarray, list[str]]:
    """Return (scipy linkage matrix, ordered label list matching corr columns)."""
    labels = list(corr.columns)
    dist = 1.0 - corr.values
    np.fill_diagonal(dist, 0.0)
    dist = (dist + dist.T) / 2.0           # enforce exact symmetry for squareform
    dist = np.clip(dist, 0.0, 2.0)
    condensed = squareform(dist, checks=False)
    Z = linkage(condensed, method=config.LINKAGE_METHOD)
    return Z, labels


def leaf_order(Z: np.ndarray, labels: list[str]) -> list[str]:
    """Dendrogram leaf ordering — used to block-order the heatmap."""
    dn = dendrogram(Z, labels=labels, no_plot=True)
    return list(dn["ivl"])


def clusters_at_thresholds(
    Z: np.ndarray,
    labels: list[str],
    out_csv=config.CLUSTERS_CSV,
    factor_map: dict[str, str] | None = None,
) -> pd.DataFrame:
    """Cluster id per asset when the tree is cut at each correlation threshold.

    A cut at correlation level c corresponds to distance (1 - c). The number of
    distinct cluster ids at that cut is the count of 'effective independent
    groups' at that co-movement tolerance.
    """
    fmap = factor_map if factor_map is not None else config.ASSET_UNIVERSE
    out = pd.DataFrame(index=labels)
    out.index.name = "ticker"
    out["factor"] = [fmap.get(t, "") for t in labels]
    for c in config.CLUSTER_CORR_THRESHOLDS:
        d = 1.0 - c
        cl = fcluster(Z, t=d, criterion="distance")
        out[f"cluster_corr>={c:.2f}"] = cl
    if out_csv is not None:
        out.to_csv(out_csv)
    return out


def effective_factor_counts(clusters: pd.DataFrame) -> dict[float, int]:
    """{threshold: n_clusters} — the headline 'how many independent bets' read."""
    counts = {}
    for c in config.CLUSTER_CORR_THRESHOLDS:
        counts[c] = int(clusters[f"cluster_corr>={c:.2f}"].nunique())
    return counts
