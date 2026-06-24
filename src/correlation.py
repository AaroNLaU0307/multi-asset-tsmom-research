"""Daily-return correlation matrix and the high-correlation pair lists."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

import config


def daily_returns(aligned_prices: pd.DataFrame) -> pd.DataFrame:
    """Simple daily returns on the common-period, date-aligned price panel.

    Correlation is computed on returns (not prices): price levels are highly
    autocorrelated and trending, so price correlation is spuriously inflated.
    """
    return aligned_prices.pct_change().dropna(how="any")


def correlation_matrix(returns: pd.DataFrame, out_csv: Path | None = config.CORRELATION_CSV) -> pd.DataFrame:
    corr = returns.corr(method=config.CORR_METHOD)
    if out_csv is not None:
        corr.to_csv(out_csv)
    return corr


def high_corr_pairs(
    corr: pd.DataFrame,
    out_csv: Path | None = config.HIGH_CORR_CSV,
    factor_map: dict[str, str] | None = None,
) -> pd.DataFrame:
    """All unique asset pairs, sorted by |corr| desc, tagged by threshold band.

    band: "strong" (|r|>=0.80), "moderate" (0.60<=|r|<0.80), else "".
    Signed correlation is reported; the band uses |r| so an inverse pair
    (e.g. UUP vs FXE ~ -0.9) is correctly seen as redundant.
    """
    fmap = factor_map if factor_map is not None else config.ASSET_UNIVERSE
    cols = list(corr.columns)
    recs = []
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            a, b = cols[i], cols[j]
            r = float(corr.iloc[i, j])
            ar = abs(r)
            if ar >= config.HIGH_CORR_STRONG:
                band = "strong"
            elif ar >= config.HIGH_CORR_MODERATE:
                band = "moderate"
            else:
                band = ""
            recs.append(
                {
                    "asset_a": a,
                    "asset_b": b,
                    "corr": round(r, 4),
                    "abs_corr": round(ar, 4),
                    "band": band,
                    "factor_a": fmap.get(a, ""),
                    "factor_b": fmap.get(b, ""),
                }
            )
    pairs = pd.DataFrame(recs).sort_values("abs_corr", ascending=False).reset_index(drop=True)
    # Persist only the flagged (>=moderate) pairs; that is the deliverable.
    flagged = pairs[pairs["band"] != ""].reset_index(drop=True)
    if out_csv is not None:
        flagged.to_csv(out_csv, index=False)
    return pairs
