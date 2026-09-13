# -*- coding: utf-8 -*-
"""C-A SEAL-GATE S_0 OVERLAP VERIFICATION — §Z.1 item 7, step 4-6.

Compares the seal-time snapshot S_0 against the frozen historical panel over
their common window, AT THE DAILY-RETURN LEVEL, as CA §E.1 requires.

Why the daily-return level and not the price level: adjusted-close series are
rescaled by construction every time a distribution is paid, so prices over the
overlap are EXPECTED to differ by a per-ticker constant factor. A constant
multiplicative rescale leaves simple daily returns invariant, so the return level
is where a genuine vendor discrepancy shows up and a routine re-adjustment does
not.

NO strategy quantity is computed anywhere in this file: no signal, no volatility,
no position, no portfolio return, no performance statistic. Only per-ticker simple
daily returns of raw adjusted closes, which are data-integrity quantities.

Returns are computed EXPLICITLY as p_t / p_{t-1} - 1 rather than via
`pct_change()`, whose default fill behaviour is version-dependent (C-D quirk
register Q-1).

The enumeration scale (1e-8 absolute on a daily return) is the tightest return
tolerance declared anywhere in the contract family (C-D spec §5 level 15). It is
used here to ENUMERATE candidate discrepancies. It is NOT a sealed acceptance
threshold, and this script does not adjudicate one.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
os.chdir(REPO)

FROZEN = "data/close_prices_raw.csv"
FROZEN_SHA = "3d2a7a56dbd92d4ff8138cfd894c87f5ac5ac088a11165db870673e0c05c3c31"
FROZEN_BOUNDARY = pd.Timestamp("2026-06-12")
ENUM_SCALE = 1e-8

CANONICAL = ["SPY", "EEM", "EWJ", "XLE", "XLU", "TLT", "SHY", "LQD", "HYG",
             "USO", "UNG", "GLD", "DBA", "UUP", "FXY", "VNQ", "RWX"]


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def rets(df):
    """Explicit simple daily returns; no pct_change, no fill."""
    return df / df.shift(1) - 1.0


def main():
    s0_path = sys.argv[1]
    print("C-A SEAL-GATE S_0 OVERLAP VERIFICATION")

    got = sha256_of(FROZEN)
    print("  frozen %s  sha256 %s  %s" % (FROZEN, got, "OK" if got == FROZEN_SHA else "MISMATCH"))
    if got != FROZEN_SHA:
        raise SystemExit("ABORT: frozen panel hash mismatch")
    print("  S_0    %s  sha256 %s" % (s0_path, sha256_of(s0_path)))

    fz = pd.read_csv(FROZEN, index_col=0, parse_dates=True).sort_index()
    s0 = pd.read_csv(s0_path, index_col=0, parse_dates=True).sort_index()

    print("\n  frozen window %s .. %s  (%d rows x %d cols)"
          % (fz.index.min().date(), fz.index.max().date(), fz.shape[0], fz.shape[1]))
    print("  S_0    window %s .. %s  (%d rows x %d cols)"
          % (s0.index.min().date(), s0.index.max().date(), s0.shape[0], s0.shape[1]))

    # ---- calendar / coverage over the common window --------------------- #
    s0_hist = s0[s0.index <= FROZEN_BOUNDARY]
    only_fz = fz.index.difference(s0_hist.index)
    only_s0 = s0_hist.index.difference(fz.index)
    common = fz.index.intersection(s0_hist.index)
    print("\n  COMMON WINDOW (<= %s)" % FROZEN_BOUNDARY.date())
    print("    frozen rows %d | S_0 historical rows %d | common rows %d"
          % (fz.shape[0], s0_hist.shape[0], len(common)))
    print("    trading days only in frozen : %d %s"
          % (len(only_fz), [str(d.date()) for d in only_fz[:5]] if len(only_fz) else ""))
    print("    trading days only in S_0    : %d %s"
          % (len(only_s0), [str(d.date()) for d in only_s0[:5]] if len(only_s0) else ""))

    post = s0[s0.index > FROZEN_BOUNDARY]
    print("    S_0 rows AFTER the frozen boundary: %d  (%s .. %s)"
          % (post.shape[0],
             post.index.min().date() if len(post) else "-",
             post.index.max().date() if len(post) else "-"))
    print("      -> POST_SEAL_UNSCORED_STATE_INPUT_ONLY (CA §E.1). Not scored. Not T4.")

    # ---- daily-return comparison, per ticker, on the common window ------ #
    cols = [c for c in fz.columns if c in s0.columns]
    rf = rets(fz.loc[common, cols])
    r0 = rets(s0_hist.loc[common, cols])

    print("\n  PER-TICKER DAILY-RETURN COMPARISON on %d common trading days" % len(common))
    print("  %-6s %-9s %-9s %-12s %-12s %-8s %s"
          % ("ticker", "canonical", "n_pairs", "max|d ret|", "mean|d ret|", ">1e-8", "n_only_one_side"))
    rows, exceed_total, worst = [], 0, ("-", 0.0, None)
    for c in cols:
        a, b = rf[c], r0[c]
        both = a.notna() & b.notna()
        one = (a.notna() ^ b.notna()).sum()
        n = int(both.sum())
        if n == 0:
            d_max = d_mean = float("nan")
            n_ex = 0
        else:
            d = (a[both] - b[both]).abs()
            d_max, d_mean = float(d.max()), float(d.mean())
            n_ex = int((d > ENUM_SCALE).sum())
            if d_max > worst[1]:
                worst = (c, d_max, d.idxmax())
        exceed_total += n_ex
        rows.append({"ticker": c, "canonical": c in CANONICAL, "n_pairs": n,
                     "max_abs_dret": d_max, "mean_abs_dret": d_mean,
                     "n_gt_enum_scale": n_ex, "n_one_side_only": int(one)})
        print("  %-6s %-9s %-9d %-12.3e %-12.3e %-8d %d"
              % (c, "YES" if c in CANONICAL else "-", n, d_max, d_mean, n_ex, one))

    canon_rows = [r for r in rows if r["canonical"]]
    print("\n  CANONICAL 17 SUMMARY")
    print("    tickers compared            : %d" % len(canon_rows))
    print("    max |delta daily return|    : %.3e" % max(r["max_abs_dret"] for r in canon_rows))
    print("    pairs above %.0e          : %d" % (ENUM_SCALE, sum(r["n_gt_enum_scale"] for r in canon_rows)))
    print("    one-side-only observations  : %d" % sum(r["n_one_side_only"] for r in canon_rows))
    print("  ALL 30 SUMMARY")
    print("    max |delta daily return|    : %.3e  (%s on %s)"
          % (worst[1], worst[0], worst[2].date() if worst[2] is not None else "-"))
    print("    pairs above %.0e          : %d" % (ENUM_SCALE, exceed_total))

    # ---- price-level rescale diagnostic (expected, not an exceedance) ---- #
    print("\n  PRICE-LEVEL RESCALE DIAGNOSTIC (expected; distributions rescale adjusted closes)")
    print("  %-6s %-14s %-14s %s" % ("ticker", "median ratio", "ratio spread", "reading"))
    for c in [x for x in cols if x in CANONICAL]:
        a = fz.loc[common, c]
        b = s0_hist.loc[common, c]
        both = a.notna() & b.notna() & (b != 0)
        if both.sum() == 0:
            print("  %-6s %-14s %-14s %s" % (c, "-", "-", "no overlap"))
            continue
        ratio = (a[both] / b[both])
        med, spread = float(ratio.median()), float(ratio.max() - ratio.min())
        reading = "constant factor" if spread < 1e-6 * max(1.0, abs(med)) else "NOT a constant factor"
        print("  %-6s %-14.10f %-14.3e %s" % (c, med, spread, reading))

    out = {
        "frozen_panel": {"path": FROZEN, "sha256": got},
        "s0": {"path": s0_path, "sha256": sha256_of(s0_path)},
        "frozen_boundary": str(FROZEN_BOUNDARY.date()),
        "common_trading_days": int(len(common)),
        "days_only_in_frozen": [str(d.date()) for d in only_fz],
        "days_only_in_s0_history": [str(d.date()) for d in only_s0],
        "s0_rows_after_boundary": int(post.shape[0]),
        "enumeration_scale_abs_daily_return": ENUM_SCALE,
        "per_ticker": rows,
        "canonical_max_abs_dret": max(r["max_abs_dret"] for r in canon_rows),
        "canonical_pairs_above_enumeration_scale": sum(r["n_gt_enum_scale"] for r in canon_rows),
        "all_max_abs_dret": worst[1],
        "all_pairs_above_enumeration_scale": exceed_total,
    }
    op = os.path.splitext(s0_path)[0] + ".overlap.json"
    with io.open(op, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=2, default=float)
        fh.write("\n")
    print("\n  overlap record %s" % op)

    print("  frozen re-verified after: %s" % ("OK" if sha256_of(FROZEN) == FROZEN_SHA else "MISMATCH"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
