# -*- coding: utf-8 -*-
"""§J locked-vs-recomputed POSITION diagnostic for the S_0 / frozen-panel overlap.

WHY THIS EXISTS
---------------
CA_PREREGISTRATION_DRAFT.md §J, row "Split / dividend back-adjustment", states the
treatment and the test verbatim:

    "Expected and absorbed: multiplicative rescaling leaves returns and signals
     invariant within a single snapshot. The locked-vs-recomputed position
     diagnostic measures any residual."
    class = MECHANICAL_CORRECTION (no action) if max |Δposition| <= 0.01 and no
            sign flip; otherwise the vendor-correction row.

The test is therefore ALREADY NUMERIC AND ALREADY DECLARED (0.01 on positions).
This script runs that one diagnostic and nothing else. It creates NO new tolerance.

HARD DATA BOUNDARY
------------------
Both panels are truncated to the frozen historical common window ending
2026-06-12 BEFORE any computation. The truncation is asserted, not assumed. No
post-boundary observation enters the engine through any path — not prices, not the
volatility windows, not the momentum lookbacks.

WHAT IS EMITTED
---------------
Only the two quantities §J names: max |Δposition| and the sign-flip condition
(plus the counts needed to read them). Deliberately NOT computed and NOT emitted:
any monthly return, gross or net; any Sharpe; any PnL; any drawdown; any
performance statistic or proxy; any position vector itself.

The canonical engine necessarily forms a base-book daily return series internally
to estimate portfolio volatility for risk targeting (src/portfolio.py says so in
its own docstring: "we do build a portfolio return stream, but ONLY to estimate
its volatility for risk targeting - not to evaluate performance"). That series is
never read, never printed and never returned by this script.
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
sys.path.insert(0, REPO)

from src import portfolio as pf  # noqa: E402

FROZEN = "data/close_prices_raw.csv"
FROZEN_SHA = "3d2a7a56dbd92d4ff8138cfd894c87f5ac5ac088a11165db870673e0c05c3c31"
BOUNDARY = pd.Timestamp("2026-06-12")

CANON17 = ["SPY", "EEM", "EWJ", "XLE", "XLU", "TLT", "SHY", "LQD", "HYG",
           "USO", "UNG", "GLD", "DBA", "UUP", "FXY", "VNQ", "RWX"]

SECTION_J_POSITION_TOLERANCE = 0.01   # verbatim from §J. NOT invented here.

ok = True


def ck(label, cond, detail=""):
    global ok
    if not cond:
        ok = False
    print("  %-56s %s   %s" % (label, "PASS" if cond else "FAIL", detail))


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_truncated(path):
    df = pd.read_csv(path, index_col=0, parse_dates=True).sort_index()
    df = df[df.index <= BOUNDARY]
    missing = [t for t in CANON17 if t not in df.columns]
    if missing:
        raise SystemExit("ABORT: canonical tickers absent from %s: %s" % (path, missing))
    return df[CANON17]


def main():
    s0_path = sys.argv[1]
    print("§J LOCKED-vs-RECOMPUTED POSITION DIAGNOSTIC — S_0 versus frozen panel")
    print("  runtime: python %s  pandas %s  numpy %s"
          % (sys.version.split()[0], pd.__version__, np.__version__))
    print("  §J test (verbatim, not invented): max |Δposition| <= %.2f AND no sign flip"
          % SECTION_J_POSITION_TOLERANCE)

    got = sha256_of(FROZEN)
    ck("frozen panel hash unchanged", got == FROZEN_SHA, got)
    print("  S_0 sha256 %s" % sha256_of(s0_path))

    fz = load_truncated(FROZEN)
    s0 = load_truncated(s0_path)

    # --- the data boundary is ASSERTED, not assumed ----------------------- #
    ck("frozen slice ends on or before the boundary", fz.index.max() <= BOUNDARY, str(fz.index.max().date()))
    ck("S_0 slice ends on or before the boundary", s0.index.max() <= BOUNDARY, str(s0.index.max().date()))
    ck("ZERO post-boundary rows entered the engine",
       int((fz.index > BOUNDARY).sum()) == 0 and int((s0.index > BOUNDARY).sum()) == 0)
    ck("both slices carry exactly the canonical 17", list(fz.columns) == CANON17 == list(s0.columns))
    ck("identical trading calendars over the window", fz.index.equals(s0.index),
       "%d vs %d rows" % (len(fz), len(s0)))

    # --- positions only --------------------------------------------------- #
    pos_fz = pf.build_portfolio(fz)["position"]
    pos_s0 = pf.build_portfolio(s0)["position"]

    common_idx = pos_fz.index.intersection(pos_s0.index)
    a = pos_fz.loc[common_idx, CANON17]
    b = pos_s0.loc[common_idx, CANON17]

    both = a.notna() & b.notna()
    one_side = (a.notna() ^ b.notna())
    delta = (a - b).abs().where(both)

    max_abs_dpos = float(np.nanmax(delta.to_numpy())) if both.to_numpy().any() else float("nan")
    n_cells = int(both.to_numpy().sum())

    # sign flip = the decision direction differs on a cell both panels priced
    sign_a = np.sign(a.where(both).fillna(0.0))
    sign_b = np.sign(b.where(both).fillna(0.0))
    flips = ((sign_a != sign_b) & both)
    n_flips = int(flips.to_numpy().sum())

    # months where all 17 position cells are non-NaN in BOTH panels. NOTE: this is
    # NOT the canonical "all 17 assets live" evaluation window -- equal_weight_aggregate
    # fills an absent asset with 0.0, so its position is 0.0 rather than NaN. The §J
    # test uses the GLOBAL max below; this subset is reported only as a cross-check.
    all17 = both.sum(axis=1) == 17
    sub_delta = delta[all17]
    sub_flips = int(flips[all17].to_numpy().sum())
    sub_max = float(np.nanmax(sub_delta.to_numpy())) if all17.any() else float("nan")

    print("\n  months compared            : %d  (%s .. %s)"
          % (len(common_idx), common_idx.min().date(), common_idx.max().date()))
    print("  months, 17 cells non-NaN   : %d  (NOT the all-17-live eval window)" % int(all17.sum()))
    print("  position cells compared    : %d" % n_cells)
    print("  cells present on one side  : %d" % int(one_side.to_numpy().sum()))
    print("  max |Δposition|  (all)     : %.6e" % max_abs_dpos)
    print("  max |Δposition|  (subset)  : %.6e" % sub_max)
    print("  sign flips       (all)     : %d" % n_flips)
    print("  sign flips       (subset)  : %d" % sub_flips)

    within = max_abs_dpos <= SECTION_J_POSITION_TOLERANCE
    no_flip = (n_flips == 0)
    ck("§J condition 1 — max |Δposition| <= 0.01", within, "%.6e" % max_abs_dpos)
    ck("§J condition 2 — no sign flip", no_flip, "%d flips" % n_flips)

    verdict = ("MECHANICAL_CORRECTION (no action)" if (within and no_flip)
               else "FAILS THE §J DIVIDEND ROW -> falls through to the vendor-correction row")
    print("\n  §J CLASSIFICATION: %s" % verdict)

    out = {
        "diagnostic": "SECTION_J_LOCKED_VS_RECOMPUTED_POSITION",
        "authority": "CA_PREREGISTRATION_DRAFT.md §J, row 'Split / dividend back-adjustment'",
        "test_declared_by_contract": {"max_abs_delta_position": SECTION_J_POSITION_TOLERANCE,
                                      "sign_flip_permitted": False},
        "new_tolerance_created": False,
        "frozen_panel_sha256": got,
        "s0_sha256": sha256_of(s0_path),
        "data_boundary": str(BOUNDARY.date()),
        "post_boundary_rows_used": 0,
        "universe": CANON17,
        "months_compared": int(len(common_idx)),
        "months_with_17_non_nan_cells": int(all17.sum()),
        "position_cells_compared": n_cells,
        "section_j_quantity_is_the_global_max": True,
        "cells_present_on_one_side_only": int(one_side.to_numpy().sum()),
        "max_abs_delta_position_all": max_abs_dpos,
        "max_abs_delta_position_subset": sub_max,
        "sign_flips_all": n_flips,
        "sign_flips_subset": sub_flips,
        "condition_1_within_tolerance": bool(within),
        "condition_2_no_sign_flip": bool(no_flip),
        "section_j_classification": ("MECHANICAL_CORRECTION" if (within and no_flip) else "FALLS_THROUGH"),
        "emitted_deliberately_not": ["monthly return", "gross return", "net return", "Sharpe",
                                     "PnL", "drawdown", "any performance statistic or proxy",
                                     "any position vector"],
    }
    op = os.path.splitext(s0_path)[0] + ".position_diagnostic.json"
    with io.open(op, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=2, default=float)
        fh.write("\n")
    print("  record %s" % op)
    ck("frozen panel hash still unchanged after the run", sha256_of(FROZEN) == FROZEN_SHA)

    print("\n" + ("DIAGNOSTIC PASSED" if ok else "DIAGNOSTIC FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
