"""Figures: correlation heatmap (block-ordered) and clustering dendrogram."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")  # headless / reproducible

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import dendrogram

import config


def plot_heatmap(corr: pd.DataFrame, order: list[str], out_png=config.HEATMAP_PNG,
                 title: str | None = None) -> None:
    """Diverging heatmap of the NxN correlation matrix, ordered by clustering
    leaf order so redundancy blocks line up on the diagonal."""
    m = corr.loc[order, order]
    n = len(order)

    fig, ax = plt.subplots(figsize=(13, 11))
    im = ax.imshow(m.values, cmap="RdBu_r", vmin=-1.0, vmax=1.0, aspect="equal")

    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(order, rotation=90, fontsize=8)
    ax.set_yticklabels(order, fontsize=8)
    ax.set_xticks(np.arange(-0.5, n, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, n, 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=0.5)
    ax.tick_params(which="minor", length=0)

    # Annotate only strong cells to keep the grid readable.
    for i in range(n):
        for j in range(n):
            v = m.values[i, j]
            if i != j and abs(v) >= config.HIGH_CORR_STRONG:
                ax.text(j, i, f"{v:.2f}", ha="center", va="center",
                        fontsize=6, color="white")

    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("Pearson correlation of daily returns")
    ax.set_title(title or ("Daily-return correlation (ordered by hierarchical clustering)\n"
                           "white labels = |r| >= 0.80"), fontsize=11)
    fig.tight_layout()
    fig.savefig(out_png, dpi=150)
    plt.close(fig)


def plot_dendrogram(Z: np.ndarray, labels: list[str], out_png=config.DENDROGRAM_PNG,
                    title: str | None = None) -> None:
    """Hierarchical clustering tree with reference cut lines at the thresholds."""
    fig, ax = plt.subplots(figsize=(14, 7))
    dendrogram(Z, labels=labels, ax=ax, leaf_rotation=90, leaf_font_size=9,
               color_threshold=1.0 - config.HIGH_CORR_MODERATE)
    for c in config.CLUSTER_CORR_THRESHOLDS:
        d = 1.0 - c
        ax.axhline(d, ls="--", lw=1, color="grey", alpha=0.8)
        ax.text(ax.get_xlim()[1], d, f"  cut @ corr={c:.2f}  (d={d:.2f})",
                va="center", fontsize=8, color="grey")
    ax.set_ylabel("distance  (1 - correlation)")
    ax.set_title(title or "Hierarchical clustering of the 30-ETF universe (average linkage, 1 - corr)")
    fig.tight_layout()
    fig.savefig(out_png, dpi=150)
    plt.close(fig)


# --------------------------------------------------------------------------- #
# Step 5 — backtest figures
# --------------------------------------------------------------------------- #
def plot_equity_curves(curves: dict, out_png, title: str, logy: bool = True) -> None:
    """Overlay growth-of-$1 curves. ``curves`` = {label: pd.Series}."""
    fig, ax = plt.subplots(figsize=(12, 6))
    for label, s in curves.items():
        ax.plot(s.index, s.values, label=label, linewidth=1.5)
    if logy:
        ax.set_yscale("log")
    ax.set_ylabel("growth of $1" + (" (log)" if logy else ""))
    ax.set_title(title)
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_png, dpi=150)
    plt.close(fig)


def plot_drawdown(dd: pd.Series, out_png, title: str) -> None:
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.fill_between(dd.index, dd.values * 100, 0.0, color="firebrick", alpha=0.5)
    ax.set_ylabel("drawdown (%)")
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_png, dpi=150)
    plt.close(fig)


def plot_fan_chart(fan, out_png, title: str, actual=None) -> None:
    """Monte Carlo percentile bands (5/25/50/75/95) of growth-of-$1."""
    fig, ax = plt.subplots(figsize=(12, 6))
    x = fan.index
    ax.fill_between(x, fan[5], fan[95], color="steelblue", alpha=0.20, label="5–95%")
    ax.fill_between(x, fan[25], fan[75], color="steelblue", alpha=0.35, label="25–75%")
    ax.plot(x, fan[50], color="navy", lw=1.5, label="median")
    if actual is not None:
        ax.plot(actual.index, actual.values, color="black", lw=1.5, ls="--", label="realized")
    ax.set_yscale("log")
    ax.set_ylabel("growth of $1 (log)")
    ax.set_title(title)
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_png, dpi=150)
    plt.close(fig)
