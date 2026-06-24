"""Screening *suggestion* (not a decision) via a greedy correlation filter.

Logic, fully transparent:
1. Order the assets by KEEP_PRIORITY (canonical anchors first, likely duplicates
   last).
2. Walk the list. KEEP an asset unless it is |corr| >= HIGH_CORR_STRONG with an
   asset that is *already kept* — in which case it is a DROP candidate, annotated
   with that kept asset and the correlation. We compare against already-kept
   assets only (greedy pairwise), NOT transitive components: SPY-EFA=0.85 and
   EFA-EEM=0.83 should not chain SPY and EEM together when SPY-EEM is only 0.75.
3. |corr| (not signed) is used so an inverse pair (UUP vs FXE ~ -0.94) is treated
   as redundant.
4. Every KEEP row records its closest already-kept neighbour; those at
   |corr| >= BORDERLINE_CORR are surfaced as optional further-trim candidates for
   a tighter universe.
5. Coverage check confirms every top-level factor keeps a representative.

Nothing is removed from disk or from the data — output is a suggestion table.
"""

from __future__ import annotations

import pandas as pd

import config


def _closest_kept(corr: pd.DataFrame, ticker: str, kept: list[str]) -> tuple[str | None, float]:
    """Return (kept_asset_with_largest_|corr|, signed_corr) or (None, 0.0)."""
    best, best_r = None, 0.0
    for k in kept:
        r = float(corr.loc[ticker, k])
        if abs(r) > abs(best_r):
            best, best_r = k, r
    return best, best_r


def greedy_filter(
    corr: pd.DataFrame,
    priority: dict,
    strong_threshold: float,
) -> tuple[list, list, dict]:
    """Pure greedy pairwise correlation filter (no config / label dependencies).

    Assets are visited in ascending ``priority`` order; one is dropped iff its
    |corr| to an already-kept asset >= ``strong_threshold``. Comparison is against
    kept assets only — NOT transitive — so a chain A~B~C with A,C uncorrelated
    keeps both A and C.

    Returns (kept, drop, info) where info[t] = (nearest_kept_or_None, signed_corr,
    kept_bool).
    """
    order = sorted(corr.columns, key=lambda t: (priority.get(t, 99), str(t)))
    kept: list = []
    drop: list = []
    info: dict = {}
    for t in order:
        partner, r = _closest_kept(corr, t, kept)
        if partner is not None and abs(r) >= strong_threshold:
            drop.append(t)
            info[t] = (partner, r, False)
        else:
            kept.append(t)
            info[t] = (partner, r, True)
    return kept, drop, info


def build_recommendations(corr: pd.DataFrame) -> tuple[pd.DataFrame, list[str], list[str]]:
    """Return (recommendation_table, keep_list, drop_list)."""
    _, _, info = greedy_filter(corr, config.KEEP_PRIORITY, config.HIGH_CORR_STRONG)

    decision: dict[str, dict] = {}
    for t, (partner, r, is_kept) in info.items():
        if not is_kept:
            decision[t] = {
                "decision": "DROP (candidate)",
                "nearest_kept": partner,
                "corr_with_kept": round(r, 3),
                "reason": (
                    f"|corr|={abs(r):.2f} with kept {partner} "
                    f"({config.ASSET_UNIVERSE[partner]}) — factor already represented"
                ),
            }
        else:
            if partner is None:
                reason = "anchor — first asset processed for its factor"
            elif abs(r) >= config.BORDERLINE_CORR:
                reason = (
                    f"kept, but borderline: |corr|={abs(r):.2f} with {partner} "
                    f"(<{config.HIGH_CORR_STRONG:.2f}) — optional further-trim candidate"
                )
            else:
                reason = f"distinct: nearest kept asset {partner} only |corr|={abs(r):.2f}"
            decision[t] = {
                "decision": "KEEP",
                "nearest_kept": partner or "",
                "corr_with_kept": round(r, 3) if partner is not None else "",
                "reason": reason,
            }

    rows = [
        {"ticker": t, "factor": config.ASSET_UNIVERSE[t], **decision[t]}
        for t in config.TICKERS
    ]
    table = pd.DataFrame(rows).set_index("ticker")
    table.to_csv(config.RECOMMENDATIONS_CSV)

    keep_sorted = [t for t in config.TICKERS if decision[t]["decision"] == "KEEP"]
    drop_sorted = [t for t in config.TICKERS if decision[t]["decision"] != "KEEP"]
    return table, keep_sorted, drop_sorted


def borderline_keeps(rec_table: pd.DataFrame) -> list[tuple[str, str, float]]:
    """KEEP rows whose closest kept neighbour is in [BORDERLINE_CORR, STRONG).

    These are the candidates to trim if the user wants a tighter (~20) universe.
    """
    out = []
    for t, row in rec_table.iterrows():
        if row["decision"] != "KEEP":
            continue
        r = row["corr_with_kept"]
        if isinstance(r, (int, float)) and abs(r) >= config.BORDERLINE_CORR:
            out.append((t, row["nearest_kept"], float(r)))
    out.sort(key=lambda x: abs(x[2]), reverse=True)
    return out


def coverage(keep: list[str]) -> dict[str, list[str]]:
    """Map each top-level factor -> kept tickers, to confirm nothing is orphaned."""
    cov: dict[str, list[str]] = {}
    for t in keep:
        cov.setdefault(config.top_factor(t), []).append(t)
    return cov
