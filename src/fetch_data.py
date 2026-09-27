"""Pull adjusted daily Close prices for the universe via yfinance.

Design notes
------------
* We download each ticker individually with ``Ticker.history(period="max",
  auto_adjust=True)``. Per-ticker fetching makes failures explicit (we never
  silently skip a ticker) and gives each series its own true inception date.
* ``auto_adjust=True`` => the returned ``Close`` is the split/dividend-adjusted
  price, which is what we want for return-based correlation.
* yfinance is an unofficial source and rate-limits, so each ticker gets a few
  retries with a polite pause.
* Results are cached to ``data/close_prices_raw.csv`` (wide, union of all
  trading days). Re-runs read the cache unless ``force=True`` so we do not hammer
  Yahoo on every analysis run.
* The pull has no end date, so a cache is only comparable to a published result
  after ``truncate_to_end`` and a ``file_sha256`` check against the recorded pin
  (``config.CORE_END_DATE`` / ``config.CORE_PANEL_SHA256`` for the core).
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

import config


def truncate_to_end(prices: pd.DataFrame, end: str | pd.Timestamp) -> pd.DataFrame:
    """Drop every row dated after ``end`` (``end`` itself is kept)."""
    return prices.loc[prices.index <= pd.Timestamp(end)]


def file_sha256(path: str | Path) -> str:
    """SHA-256 of a file's bytes."""
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def check_file_sha256(path: str | Path, expected: str, *, strict: bool = False,
                      label: str = "panel") -> bool:
    """Compare ``path``'s SHA-256 with the recorded pin ``expected``.

    Returns True on a match. On a mismatch (or a missing file) it raises ``ValueError``
    when ``strict`` and otherwise prints a warning and returns False — results computed
    from a different file will not reproduce the published numbers byte-for-byte."""
    path = Path(path)
    got = file_sha256(path) if path.exists() else "missing"
    if got == expected:
        print(f"[fetch] {label} sha256 matches the recorded pin ({expected[:12]}…)")
        return True
    msg = (f"{label} {path.name} sha256 {got[:12]}… differs from the recorded pin "
           f"{expected[:12]}…; results will not reproduce the published numbers exactly")
    if strict:
        raise ValueError(msg)
    print(f"[fetch] WARNING: {msg}")
    return False


@dataclass
class FetchResult:
    ticker: str
    ok: bool
    rows: int
    error: str = ""


def _fetch_one(ticker: str) -> tuple[pd.Series | None, str]:
    """Return (adjusted Close series indexed by tz-naive date, error_message)."""
    import yfinance as yf

    last_err = ""
    for attempt in range(1, config.FETCH_RETRIES + 1):
        try:
            df = yf.Ticker(ticker).history(
                period=config.FETCH_PERIOD, auto_adjust=True
            )
            if df is None or df.empty or "Close" not in df.columns:
                last_err = "empty response"
            else:
                s = df["Close"].copy()
                # Normalise index to tz-naive calendar dates for clean alignment.
                idx = pd.to_datetime(s.index)
                if idx.tz is not None:
                    idx = idx.tz_localize(None)
                s.index = idx.normalize()
                s = s[~s.index.duplicated(keep="last")].sort_index()
                s.name = ticker
                if len(s) > 0:
                    return s, ""
                last_err = "zero rows after cleaning"
        except Exception as exc:  # noqa: BLE001 - report any failure, never hide it
            last_err = f"{type(exc).__name__}: {exc}"
        if attempt < config.FETCH_RETRIES:
            time.sleep(config.FETCH_SLEEP_SEC * attempt)
    return None, last_err


def fetch_universe(force: bool = False) -> tuple[pd.DataFrame, list[FetchResult]]:
    """Fetch (or load cached) adjusted Close prices for the whole universe.

    Returns
    -------
    prices : DataFrame  (index = union of all trading dates, columns = tickers)
    results : list[FetchResult]  (per-ticker fetch status, for the failure report)
    """
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not force and config.RAW_PRICES_CSV.exists():
        prices = pd.read_csv(config.RAW_PRICES_CSV, index_col=0, parse_dates=True)
        prices = prices.reindex(columns=config.TICKERS)
        results = [
            FetchResult(t, ok=prices[t].notna().any(), rows=int(prices[t].notna().sum()))
            for t in config.TICKERS
        ]
        print(f"[fetch] loaded cached prices: {config.RAW_PRICES_CSV}")
        return prices, results

    series: dict[str, pd.Series] = {}
    results: list[FetchResult] = []
    for i, ticker in enumerate(config.TICKERS, start=1):
        s, err = _fetch_one(ticker)
        if s is None:
            results.append(FetchResult(ticker, ok=False, rows=0, error=err))
            print(f"[fetch] {i:2d}/{len(config.TICKERS)}  {ticker:5s}  FAILED  ({err})")
        else:
            series[ticker] = s
            results.append(FetchResult(ticker, ok=True, rows=len(s)))
            print(
                f"[fetch] {i:2d}/{len(config.TICKERS)}  {ticker:5s}  ok  "
                f"{len(s):5d} rows  {s.index.min().date()} -> {s.index.max().date()}"
            )
        time.sleep(config.FETCH_SLEEP_SEC)

    if not series:
        raise RuntimeError("No tickers fetched successfully — aborting.")

    prices = pd.concat(series.values(), axis=1).sort_index()
    prices = prices.reindex(columns=config.TICKERS)  # keep canonical order incl. failed
    prices.index.name = "Date"
    prices.to_csv(config.RAW_PRICES_CSV)

    meta = pd.DataFrame(
        [{"ticker": r.ticker, "ok": r.ok, "rows": r.rows, "error": r.error} for r in results]
    )
    meta.to_csv(config.FETCH_META_CSV, index=False)
    print(f"[fetch] saved {config.RAW_PRICES_CSV}  shape={prices.shape}")
    return prices, results
