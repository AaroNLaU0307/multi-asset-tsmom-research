"""Data acquisition for the multi-universe XSMOM study (Phase 2).

Reuses the engine's per-ticker fetch (``fetch_data._fetch_one`` — same yfinance path,
retries, tz-normalisation, dedup) but caches to a SEPARATE file
(``xsmom_universes_prices.csv``) so the engine's own cache (``close_prices_raw.csv``) is
never touched. Coverage verification + the drop rule live here; the homogeneity argument
and inclusion decisions (in ``xsmom_universes.py``) are unaffected by what gets dropped.
"""

from __future__ import annotations

import time
from dataclasses import dataclass

import pandas as pd

import config
import xsmom_universes as uni
from . import fetch_data


@dataclass
class Coverage:
    ticker: str
    kept: bool
    first: str
    last: str
    reason: str = ""


def fetch_universe_prices(tickers: list[str] = uni.ALL_TICKERS,
                          force: bool = False) -> pd.DataFrame:
    """Fetch (or load cached) adjusted daily closes for every universe candidate.

    Cached to ``xsmom_universes_prices.csv`` (wide, union of trading days). Re-runs read
    the cache unless ``force=True``. Per-ticker fetch makes any failure explicit.
    """
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not force and uni.UNIVERSES_PRICES_CSV.exists():
        px = pd.read_csv(uni.UNIVERSES_PRICES_CSV, index_col=0, parse_dates=True)
        missing = [t for t in tickers if t not in px.columns]
        if not missing:
            print(f"[xsmom-data] loaded cached prices: {uni.UNIVERSES_PRICES_CSV}")
            return px.reindex(columns=tickers)
        print(f"[xsmom-data] cache missing {missing} — refetching all")

    series: dict[str, pd.Series] = {}
    for i, t in enumerate(tickers, 1):
        s, err = fetch_data._fetch_one(t)
        if s is None:
            print(f"[xsmom-data] {i:2d}/{len(tickers)} {t:5s} FAILED ({err})")
        else:
            series[t] = s
            print(f"[xsmom-data] {i:2d}/{len(tickers)} {t:5s} ok {len(s):5d} rows "
                  f"{s.index.min().date()} -> {s.index.max().date()}")
        time.sleep(config.FETCH_SLEEP_SEC)

    if not series:
        raise RuntimeError("No universe tickers fetched — aborting.")
    px = pd.concat(series.values(), axis=1).sort_index().reindex(columns=tickers)
    px.index.name = "Date"
    px.to_csv(uni.UNIVERSES_PRICES_CSV)
    print(f"[xsmom-data] saved {uni.UNIVERSES_PRICES_CSV}  shape={px.shape}")
    return px


def verify_coverage(prices: pd.DataFrame, candidates: list[str],
                    cutoff: str = uni.COVERAGE_CUTOFF) -> tuple[list[str], list[Coverage]]:
    """Apply the pre-registered coverage rule: KEEP a ticker iff it has data on/before
    ``cutoff`` (so a 12-1 signal exists at the common-window start). Returns
    (kept_tickers, coverage_records) — drops are reported, never silent."""
    cutoff_ts = pd.Timestamp(cutoff)
    kept: list[str] = []
    records: list[Coverage] = []
    for t in candidates:
        col = prices[t].dropna() if t in prices.columns else pd.Series(dtype=float)
        if col.empty:
            records.append(Coverage(t, False, "—", "—", "no data"))
            continue
        first, last = col.index.min(), col.index.max()
        if first <= cutoff_ts:
            kept.append(t)
            records.append(Coverage(t, True, str(first.date()), str(last.date())))
        else:
            records.append(Coverage(t, False, str(first.date()), str(last.date()),
                                    f"inception {first.date()} > {cutoff} (no 2008 coverage)"))
    return kept, records
