"""Wave-1 bounded Databento input verification (X02/X03 precondition).

METADATA AND STRUCTURE ONLY. Establishes dataset identity, root identity,
schema, coverage, units and roll-relevant availability. Computes NO strategy
return, NO Sharpe, NO PnL, and inspects no protected outcome. Everything read
lies inside the declared frozen snapshot boundary (through 2026-06-30).

SYMBOL RESOLUTION. The delivery is `stype_in=parent`, `stype_out=instrument_id`,
so records carry an integer instrument_id only. An earlier revision of this
probe inverted `metadata.mappings` by hand and produced obvious nonsense (CL
with 7 outright contracts, metals missing entirely, negative "outright"
settlements). That hand-rolled resolution is abandoned: this version uses the
vendor's own `DBNStore.to_df(map_symbols=True)`, chunked so memory stays bounded.

The parent pull contains CALENDAR SPREADS (e.g. `CLZ5-CLM6`) alongside outrights
(e.g. `CLZ5`). They are separated here, because a roll or a PnL path built over
spread instruments would be silently and badly wrong.

Writes research/extensions/wave1/databento_probe.json.
"""
import collections
import datetime as dt
import hashlib
import json
import os
import re
import sys
from pathlib import Path

import databento as db
import pandas as pd

DATA_DIR = Path(os.environ.get("DATA_DIR", r"C:\Users\Aaron\quant-data\commodity-carry"))
OUT = Path(__file__).with_name("databento_probe.json")
CHUNK = 500_000

CARRY = Path(__file__).resolve().parents[3].parent / "commodity-carry-research"
sys.path.insert(0, str(CARRY))
try:
    from src import config as carry_cfg      # noqa: E402
except Exception as _exc:                     # pragma: no cover
    carry_cfg = None
    _CARRY_IMPORT_ERROR = "%s: %s" % (type(_exc).__name__, _exc)
else:
    _CARRY_IMPORT_ERROR = None

# An outright CME contract: root + month code + 1-2 digit year, nothing else.
OUTRIGHT = re.compile(r"^([A-Z0-9]{1,3}?)([FGHJKMNQUVXZ])(\d{1,2})$")
MONTH_CODES = "FGHJKMNQUVXZ"


def classify(sym, known_roots):
    """(kind, root) for a raw symbol. kind in {outright, spread, other}."""
    if not sym or sym == "":
        return "other", None
    if "-" in sym or ":" in sym:
        return "spread", None
    for r in sorted(known_roots, key=len, reverse=True):
        if sym.startswith(r):
            tail = sym[len(r):]
            if len(tail) >= 2 and tail[0] in MONTH_CODES and tail[1:].isdigit():
                return "outright", r
    m = OUTRIGHT.match(sym)
    if m:
        return "outright", m.group(1)
    return "other", None


def blank():
    return {"n_records": 0, "first_date": None, "last_date": None,
            "outrights": set(), "close_min": None, "close_max": None,
            "n_zero_close": 0, "n_neg_close": 0}


def main():
    result = {"data_dir": str(DATA_DIR),
              "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat()}

    ohlcv = DATA_DIR / "ohlcv-1d.dbn.zst"
    h = hashlib.sha256()
    with open(ohlcv, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    result["ohlcv_file"] = {"path": str(ohlcv),
                            "size_bytes": ohlcv.stat().st_size,
                            "sha256": h.hexdigest()}

    store = db.DBNStore.from_file(ohlcv)
    meta = store.metadata
    result["metadata"] = {
        "dataset": getattr(meta, "dataset", None),
        "schema": str(getattr(meta, "schema", None)),
        "stype_in": str(getattr(meta, "stype_in", None)),
        "stype_out": str(getattr(meta, "stype_out", None)),
        "start_utc": str(pd.Timestamp(getattr(meta, "start", 0), unit="ns", tz="UTC")),
        "end_utc": str(pd.Timestamp(getattr(meta, "end", 0), unit="ns", tz="UTC")),
        "symbols": list(getattr(meta, "symbols", []) or []),
    }
    known_roots = [s.split(".")[0] for s in result["metadata"]["symbols"]]
    result["parent_roots"] = known_roots

    per_root = collections.defaultdict(blank)
    spread_records = 0
    other_records = 0
    other_examples = collections.Counter()
    dates = collections.Counter()
    n = 0

    for chunk in store.to_df(map_symbols=True, count=CHUNK):
        n += len(chunk)
        syms = chunk["symbol"].astype(str)
        days = chunk.index.tz_convert("UTC").date if hasattr(chunk.index, "tz_convert") \
            else chunk.index.date
        closes = chunk["close"].astype(float)
        for sym, day, close in zip(syms, days, closes):
            kind, root = classify(sym, known_roots)
            ds = str(day)
            dates[ds] += 1
            if kind == "spread":
                spread_records += 1
                continue
            if kind != "outright" or root is None:
                other_records += 1
                other_examples[sym] += 1
                continue
            d = per_root[root]
            d["n_records"] += 1
            d["outrights"].add(sym)
            if d["first_date"] is None or ds < d["first_date"]:
                d["first_date"] = ds
            if d["last_date"] is None or ds > d["last_date"]:
                d["last_date"] = ds
            if close == 0:
                d["n_zero_close"] += 1
            elif close < 0:
                d["n_neg_close"] += 1
            else:
                if d["close_min"] is None or close < d["close_min"]:
                    d["close_min"] = close
                if d["close_max"] is None or close > d["close_max"]:
                    d["close_max"] = close

    result["n_records_total"] = n
    result["n_spread_records"] = spread_records
    result["n_other_records"] = other_records
    result["other_symbol_examples"] = other_examples.most_common(15)
    result["roots"] = {
        r: {"n_records": d["n_records"],
            "n_outright_contracts": len(d["outrights"]),
            "first_date": d["first_date"], "last_date": d["last_date"],
            "close_min": d["close_min"], "close_max": d["close_max"],
            "n_zero_close": d["n_zero_close"], "n_neg_close": d["n_neg_close"]}
        for r, d in sorted(per_root.items())}

    day_keys = sorted(dates)
    result["session_dates"] = {"n_distinct": len(day_keys),
                               "first": day_keys[0] if day_keys else None,
                               "last": day_keys[-1] if day_keys else None,
                               "tail_10": [(k, dates[k]) for k in day_keys[-10:]]}

    for schema in ("statistics", "definition"):
        d = DATA_DIR / schema
        if d.is_dir():
            files = sorted(d.glob("*.dbn.zst"))
            result[schema] = {"n_files": len(files),
                              "first_file": files[0].name if files else None,
                              "last_file": files[-1].name if files else None,
                              "total_bytes": sum(f.stat().st_size for f in files)}

    if carry_cfg is not None:
        result["carry_universe"] = carry_cfg.ALL_SYMBOLS
        result["carry_sample_start"] = carry_cfg.SAMPLE_START
        result["carry_sample_end"] = carry_cfg.SAMPLE_END
        result["carry_specs"] = carry_cfg.CONTRACT_SPECS
    else:
        result["carry_universe"] = None
        result["carry_import_error"] = _CARRY_IMPORT_ERROR

    OUT.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")
    print("wrote", OUT, "| records:", n, "| outright roots:", len(per_root),
          "| spread recs:", spread_records, "| other:", other_records)


if __name__ == "__main__":
    main()
