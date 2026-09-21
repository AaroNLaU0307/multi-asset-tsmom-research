# -*- coding: utf-8 -*-
"""C-A SEAL-GATE S_0 ACQUISITION — a ONE-OFF S1 provenance tool.

WHAT THIS IS
------------
The §Z.1 item 7 seal-time snapshot step of CA_PREREGISTRATION_DRAFT.md §E.1:
acquire S_0, hash it, and record its identity. S_0 pins what was available at the
seal gate and establishes provenance. Nothing else.

WHAT THIS IS NOT
----------------
* NOT the S2 append-only prospective snapshot writer (CA §Z.2 item 4). It writes
  one file, once, at the seal gate, and is not part of any pipeline.
* NOT S_G. S_G is the go-live base snapshot and is NOT created here.
* NOT a strategy run. No signal, no sizing, no position, no return of the book,
  no performance quantity is computed anywhere in this file.

HARD SAFETY PROPERTY
--------------------
The frozen historical panel `data/close_prices_raw.csv` is NEVER opened for
writing. Its SHA-256 is verified from bytes BEFORE and AFTER the run and the
script aborts on any mismatch. It is never passed to any writer, and
`src.fetch_data.fetch_universe` — whose `force=True` path writes to that exact
path — is deliberately NOT imported or called (C-D quirk register Q-6).

Acquisition semantics are copied from `src/fetch_data.py::_fetch_one` so that
S_0 and the frozen panel are comparable: per-ticker
`yf.Ticker(t).history(period="max", auto_adjust=True)`, the `Close` column,
tz-naive normalised index, duplicates dropped keeping the last, sorted ascending.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import sys
import time
from datetime import datetime, timezone

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
os.chdir(REPO)
sys.path.insert(0, REPO)

import config  # noqa: E402

FROZEN = "data/close_prices_raw.csv"
FROZEN_SHA = "3d2a7a56dbd92d4ff8138cfd894c87f5ac5ac088a11165db870673e0c05c3c31"
OUT_DIR = os.path.join("data", "prospective")


def sha256_of(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def guard_frozen(stage: str) -> str:
    got = sha256_of(FROZEN)
    if got != FROZEN_SHA:
        raise SystemExit(
            "ABORT (%s): frozen panel hash mismatch.\n  expected %s\n  got      %s"
            % (stage, FROZEN_SHA, got)
        )
    print("  frozen-panel guard %-6s OK  %s" % (stage, got))
    return got


def fetch_one(ticker: str):
    """Mirror of src/fetch_data.py::_fetch_one. Returns (series|None, error)."""
    import yfinance as yf

    last_err = ""
    for attempt in range(1, config.FETCH_RETRIES + 1):
        try:
            df = yf.Ticker(ticker).history(period=config.FETCH_PERIOD, auto_adjust=True)
            if df is None or df.empty or "Close" not in df.columns:
                last_err = "empty response"
            else:
                s = df["Close"].copy()
                idx = pd.to_datetime(s.index)
                if idx.tz is not None:
                    idx = idx.tz_localize(None)
                s.index = idx.normalize()
                s = s[~s.index.duplicated(keep="last")].sort_index()
                s.name = ticker
                if len(s) > 0:
                    return s, ""
                last_err = "zero rows after cleaning"
        except Exception as exc:  # noqa: BLE001
            last_err = "%s: %s" % (type(exc).__name__, exc)
        if attempt < config.FETCH_RETRIES:
            time.sleep(config.FETCH_SLEEP_SEC * attempt)
    return None, last_err


def main() -> int:
    print("C-A SEAL-GATE S_0 ACQUISITION")
    import yfinance as yf

    print("  runtime: python %s  pandas %s  yfinance %s"
          % (sys.version.split()[0], pd.__version__, yf.__version__))
    guard_frozen("before")

    started = datetime.now(timezone.utc)
    tickers = list(config.TICKERS)
    print("  acquiring %d tickers, period=%s, auto_adjust=True" % (len(tickers), config.FETCH_PERIOD))

    series, meta = {}, []
    for i, t in enumerate(tickers, 1):
        s, err = fetch_one(t)
        if s is None:
            meta.append({"ticker": t, "ok": False, "rows": 0, "first": None, "last": None, "error": err})
            print("    [%2d/%d] %-5s FAIL  %s" % (i, len(tickers), t, err[:70]))
        else:
            series[t] = s
            meta.append({"ticker": t, "ok": True, "rows": int(s.notna().sum()),
                         "first": str(s.index.min().date()), "last": str(s.index.max().date()),
                         "error": ""})
            print("    [%2d/%d] %-5s ok    %5d rows  %s..%s"
                  % (i, len(tickers), t, int(s.notna().sum()), s.index.min().date(), s.index.max().date()))
        time.sleep(config.FETCH_SLEEP_SEC)
    finished = datetime.now(timezone.utc)

    if not series:
        print("\nNO TICKER ACQUIRED — S_0 NOT CREATED")
        guard_frozen("after")
        return 2

    panel = pd.DataFrame(series).reindex(columns=[t for t in tickers if t in series]).sort_index()
    panel.index.name = "Date"

    os.makedirs(OUT_DIR, exist_ok=True)
    stamp = started.strftime("%Y%m%dT%H%M%SZ")
    out = os.path.join(OUT_DIR, "S0_%s.csv" % stamp).replace("\\", "/")
    if os.path.abspath(out) == os.path.abspath(FROZEN):
        raise SystemExit("ABORT: refusing to write to the frozen panel path")
    panel.to_csv(out, lineterminator="\n")

    sha = sha256_of(out)
    size = os.path.getsize(out)
    ident = {
        "artifact": "S_0",
        "role": "C-A seal-time snapshot (CA_PREREGISTRATION_DRAFT.md §E.1)",
        "path": out,
        "sha256": sha,
        "byte_size": size,
        "acquisition_started_utc": started.isoformat(timespec="seconds"),
        "acquisition_finished_utc": finished.isoformat(timespec="seconds"),
        "source": "yfinance (Yahoo Finance), Ticker.history(period='max', auto_adjust=True)",
        "runtime": {"python": sys.version.split()[0], "pandas": pd.__version__, "yfinance": yf.__version__},
        "tickers_requested": len(tickers),
        "tickers_acquired": len(series),
        "first_date": str(panel.index.min().date()),
        "last_date": str(panel.index.max().date()),
        "rows": int(panel.shape[0]),
        "columns": int(panel.shape[1]),
        "frozen_panel_sha256_verified": FROZEN_SHA,
        "per_ticker": meta,
        "NOT": ["not S_G", "not the prospective scored sample", "not T4 evidence",
                "not a target-performance run", "not a reveal"],
    }
    ident_path = os.path.join(OUT_DIR, "S0_%s.identity.json" % stamp).replace("\\", "/")
    with io.open(ident_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(ident, fh, indent=2, sort_keys=False)
        fh.write("\n")

    print("\n  S_0 path      %s" % out)
    print("  S_0 sha256    %s" % sha)
    print("  S_0 bytes     %d" % size)
    print("  S_0 window    %s .. %s  (%d rows x %d cols)"
          % (ident["first_date"], ident["last_date"], ident["rows"], ident["columns"]))
    print("  identity json %s" % ident_path)
    guard_frozen("after")
    print("\nS_0 ACQUIRED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
