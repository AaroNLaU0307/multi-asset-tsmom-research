"""Corrected futures panel extraction — persistent contract identity.

REPLACES `extract_settle_oi.py`, whose panels were keyed by RAW SYMBOL and are
INVALID: CME parent symbology reuses a one-digit year every 10 years, so a
16-year panel merged two contracts into one column (`GCM1` spanned 2010-2026).

CANONICAL IDENTITY, reused rather than reinvented. This adopts
`commodity-carry-research/src/pipeline.py::build_outright_panel`'s method
verbatim in substance:

    _contract_key = str(instrument_id) + "__" + expiration.date()

- joins definition to statistics on **(date, instrument_id)** — a single-date
  key, safe from carry finding **F6** (instrument_id reuse across different
  real contracts), which only bites when instrument_id is used without a date;
- keys on the **calendar DATE** of expiration, not the timestamp — carry
  finding **F10**, where one KE contract's expiration time was corrected
  mid-life and timestamp keying froze the roll permanently;
- **excludes raw_symbol from the key entirely** — carry finding **F9**, where
  one CL contract appeared as `CLM19` then `CLM9` and symbol-keying split it;
- filters `instrument_class == "F"`, the vendor's own outright flag, which is
  the authoritative spread filter (carry F1). No string heuristic is used.

No expiry-year guessing remains anywhere in this path: expiration is read from
the definition schema.

OPEN INTEREST — a disclosed divergence from the carry implementation.
`pipeline.py` line 100 reads `stat_type == 6` into a column named `oi`. The
vendor enum is unambiguous: `StatType.CLEARED_VOLUME = 6`,
`StatType.OPEN_INTEREST = 9`, and on 2026-06-30 CLQ6 carries 170,488 at
stat_type 6 versus 245,241 at stat_type 9 — different quantities. The A1 roll
rule is specified on OPEN INTEREST, so this extraction uses **stat_type 9**.
The divergence is recorded in FUTURES_INFRA_TRUTH.md; it is a disclosure about
code this program reuses, not a verdict on the carry study, and the carry
repository is not modified.

Reads existing local files only. No purchase, no refresh, no protected data.

Writes:
  contracts_meta.parquet   one row per _contract_key: asset, expiration, span
  settle_v2.parquet        date x _contract_key settlement
  oi_v2.parquet            date x _contract_key open interest
  extract_v2_meta.json
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
_DATE_RE = re.compile(r"(\d{8})")

CARRY = Path(__file__).resolve().parents[3].parent / "commodity-carry-research"
sys.path.insert(0, str(CARRY))
from src import config as carry_cfg   # noqa: E402

ROOTS = set(carry_cfg.ALL_SYMBOLS)
STAT_SETTLEMENT = 3
STAT_OPEN_INTEREST = 9          # vendor enum; NOT 6 (= CLEARED_VOLUME)


def main():
    def_files = {(_DATE_RE.search(f.name).group(1)): f
                 for f in sorted((DATA_DIR / "definition").glob("*.dbn.zst"))}
    stat_files = {(_DATE_RE.search(f.name).group(1)): f
                  for f in sorted((DATA_DIR / "statistics").glob("*.dbn.zst"))}
    days = sorted(set(def_files) & set(stat_files))

    settle = collections.defaultdict(dict)
    oi = collections.defaultdict(dict)
    meta = {}                       # key -> {asset, expiration, class}
    n_def_only = len(set(def_files) - set(stat_files))
    n_stat_only = len(set(stat_files) - set(def_files))
    n_settle = n_oi = 0
    dropped_nonF = 0

    for i, day in enumerate(days, 1):
        d = db.DBNStore.from_file(def_files[day]).to_df()
        need = ["instrument_id", "asset", "instrument_class", "expiration"]
        if not all(c in d.columns for c in need):
            continue
        d = d[need].copy()
        d = d[d["asset"].astype(str).isin(ROOTS)]
        dropped_nonF += int((d["instrument_class"].astype(str) != "F").sum())
        d = d[d["instrument_class"].astype(str) == "F"]          # outright only
        if d.empty:
            continue
        d = d.drop_duplicates(subset=["instrument_id"])
        exp_date = pd.to_datetime(d["expiration"]).dt.date.astype(str)
        d["_contract_key"] = d["instrument_id"].astype(str) + "__" + exp_date
        idmap = dict(zip(d["instrument_id"].astype(int), d["_contract_key"]))
        for iid, key, asset, e in zip(d["instrument_id"].astype(int),
                                      d["_contract_key"], d["asset"].astype(str),
                                      exp_date):
            m = meta.setdefault(key, {"asset": asset, "expiration": e,
                                      "instrument_id": int(iid)})
            if m["asset"] != asset:
                raise ValueError("contract key %s spans assets %s/%s"
                                 % (key, m["asset"], asset))

        s = db.DBNStore.from_file(stat_files[day]).to_df()
        if "stat_type" not in s.columns:
            continue
        s = s[s["stat_type"].isin((STAT_SETTLEMENT, STAT_OPEN_INTEREST))]
        if s.empty:
            continue
        # last value of the day per (instrument_id, stat_type), as carry does
        s = s.reset_index()
        s = s.groupby(["instrument_id", "stat_type"], as_index=False).last()
        dd = pd.Timestamp(day).date()
        for iid, st, price, qty in zip(s["instrument_id"].astype(int),
                                       s["stat_type"].astype(int),
                                       s["price"], s["quantity"]):
            key = idmap.get(iid)
            if key is None:
                continue
            if st == STAT_SETTLEMENT:
                if pd.notna(price):
                    settle[dd][key] = float(price); n_settle += 1
            else:
                q = int(qty) if pd.notna(qty) else None
                if q is not None and q != 2147483647:
                    oi[dd][key] = q; n_oi += 1
        if i % 250 == 0:
            print("  %d/%d days  settle=%d oi=%d keys=%d"
                  % (i, len(days), n_settle, n_oi, len(meta)), flush=True)

    s_df = pd.DataFrame.from_dict(settle, orient="index").sort_index()
    o_df = pd.DataFrame.from_dict(oi, orient="index").sort_index()
    s_df.index = pd.to_datetime(s_df.index)
    o_df.index = pd.to_datetime(o_df.index)
    s_df = s_df.reindex(sorted(s_df.columns), axis=1)
    o_df = o_df.reindex(sorted(o_df.columns), axis=1)

    rows = []
    for key, m in meta.items():
        col = s_df[key] if key in s_df.columns else pd.Series(dtype=float)
        obs = col.dropna()
        rows.append({"_contract_key": key, "asset": m["asset"],
                     "instrument_id": m["instrument_id"],
                     "expiration": m["expiration"],
                     "n_settle_obs": int(len(obs)),
                     "first_obs": str(obs.index[0].date()) if len(obs) else None,
                     "last_obs": str(obs.index[-1].date()) if len(obs) else None})
    c_df = pd.DataFrame(rows).sort_values(["asset", "expiration", "_contract_key"])

    s_df.to_parquet(HERE / "settle_v2.parquet")
    o_df.to_parquet(HERE / "oi_v2.parquet")
    c_df.to_parquet(HERE / "contracts_meta.parquet")

    out = {
        "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "contract_key_definition": "str(instrument_id) + '__' + expiration.date()",
        "identity_source": "commodity-carry-research/src/pipeline.py::build_outright_panel",
        "oi_stat_type": STAT_OPEN_INTEREST,
        "oi_stat_type_note": ("vendor StatType.OPEN_INTEREST=9; carry pipeline "
                              "reads stat_type 6 = CLEARED_VOLUME into a column "
                              "named 'oi' -- disclosed divergence"),
        "n_days_paired": len(days),
        "n_definition_only_days": n_def_only,
        "n_statistics_only_days": n_stat_only,
        "n_settlement_points": n_settle,
        "n_oi_points": n_oi,
        "n_persistent_contracts": int(len(c_df)),
        "n_non_outright_rows_dropped": int(dropped_nonF),
        "settle_shape": list(s_df.shape), "oi_shape": list(o_df.shape),
        "settle_first_date": str(s_df.index.min().date()),
        "settle_last_date": str(s_df.index.max().date()),
        "oi_first_date": str(o_df.index.min().date()),
        "oi_last_date": str(o_df.index.max().date()),
        "contracts_by_root": c_df.groupby("asset").size().to_dict(),
    }
    (HERE / "extract_v2_meta.json").write_text(json.dumps(out, indent=2),
                                               encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
