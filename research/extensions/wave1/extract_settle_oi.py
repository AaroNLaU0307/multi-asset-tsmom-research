"""Extract daily SETTLEMENT and OPEN INTEREST per outright contract, 18 roots.

X02a / X03 input builder. Reads the `statistics` schema only (stat_type 3 =
SETTLEMENT_PRICE, 9 = OPEN_INTEREST), keeps OUTRIGHT contracts of the 18
pre-registered roots, and drops every calendar spread. No PnL, no return, no
strategy output is produced here; this is an input extraction.

Why settlement and not ohlcv close: the carry study's construction is
settlement-based, and settlement is the price a futures position is actually
marked and margined at. Using an ohlcv close in a dollar ledger would be a
different (and wrong) accounting object.

Writes:
  research/extensions/wave1/settle_panel.parquet   date x contract settlement
  research/extensions/wave1/oi_panel.parquet       date x contract open interest
  research/extensions/wave1/extract_meta.json
"""
import collections
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path

import databento as db
import pandas as pd

DATA_DIR = Path(os.environ.get("DATA_DIR", r"C:\Users\Aaron\quant-data\commodity-carry"))
HERE = Path(__file__).parent

CARRY = Path(__file__).resolve().parents[3].parent / "commodity-carry-research"
sys.path.insert(0, str(CARRY))
from src import config as carry_cfg  # noqa: E402

ROOTS = list(carry_cfg.ALL_SYMBOLS)
MONTH_CODES = "FGHJKMNQUVXZ"
STAT_SETTLEMENT = 3
STAT_OPEN_INTEREST = 9

_OUT = {}
for r in ROOTS:
    _OUT[r] = re.compile(r"^" + re.escape(r) + r"([" + MONTH_CODES + r"])(\d{1,2})$")


def outright_root(sym):
    """Root iff `sym` is an OUTRIGHT of one of the 18 roots, else None.

    Longest-root-first so that a 1-2 char root cannot shadow a longer one.
    Any symbol containing '-' is a calendar/inter-commodity spread and is
    rejected outright: 79% of this delivery is spreads.
    """
    if "-" in sym:
        return None
    for r in sorted(ROOTS, key=len, reverse=True):
        if sym.startswith(r) and _OUT[r].match(sym):
            return r
    return None


def main():
    files = sorted((DATA_DIR / "statistics").glob("*.dbn.zst"))
    settle = collections.defaultdict(dict)     # date -> {contract: price}
    oi = collections.defaultdict(dict)         # date -> {contract: qty}
    seen_contracts = set()
    n_files = 0
    n_settle = n_oi = 0

    for f in files:
        try:
            df = db.DBNStore.from_file(f).to_df(map_symbols=True)
        except Exception as exc:                       # pragma: no cover
            print("SKIP", f.name, type(exc).__name__, exc)
            continue
        n_files += 1
        if "stat_type" not in df.columns:
            continue
        df = df[df["stat_type"].isin((STAT_SETTLEMENT, STAT_OPEN_INTEREST))]
        if df.empty:
            continue
        day = pd.Timestamp(f.name.split("-")[-1].split(".")[0]).date()
        for sym, st, price, qty in zip(df["symbol"].astype(str),
                                       df["stat_type"].astype(int),
                                       df["price"], df["quantity"]):
            r = outright_root(sym)
            if r is None:
                continue
            seen_contracts.add(sym)
            if st == STAT_SETTLEMENT:
                if pd.notna(price):
                    settle[day][sym] = float(price)
                    n_settle += 1
            else:
                q = int(qty) if pd.notna(qty) else None
                # 2147483647 is the DBN null sentinel for an absent quantity.
                if q is not None and q != 2147483647:
                    oi[day][sym] = q
                    n_oi += 1
        if n_files % 250 == 0:
            print("  %d/%d files, %d settle, %d oi" % (n_files, len(files), n_settle, n_oi),
                  flush=True)

    s_df = pd.DataFrame.from_dict(settle, orient="index").sort_index()
    o_df = pd.DataFrame.from_dict(oi, orient="index").sort_index()
    s_df.index = pd.to_datetime(s_df.index)
    o_df.index = pd.to_datetime(o_df.index)
    s_df = s_df.reindex(sorted(s_df.columns), axis=1)
    o_df = o_df.reindex(sorted(o_df.columns), axis=1)
    s_df.to_parquet(HERE / "settle_panel.parquet")
    o_df.to_parquet(HERE / "oi_panel.parquet")

    meta = {
        "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "n_files_read": n_files, "n_files_available": len(files),
        "n_settlement_points": n_settle, "n_oi_points": n_oi,
        "n_outright_contracts": len(seen_contracts),
        "settle_shape": list(s_df.shape), "oi_shape": list(o_df.shape),
        "settle_first_date": str(s_df.index.min().date()),
        "settle_last_date": str(s_df.index.max().date()),
        "oi_first_date": str(o_df.index.min().date()),
        "oi_last_date": str(o_df.index.max().date()),
        "roots": ROOTS,
    }
    (HERE / "extract_meta.json").write_text(json.dumps(meta, indent=2),
                                            encoding="utf-8")
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()
