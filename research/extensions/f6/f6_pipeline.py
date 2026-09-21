# -*- coding: utf-8 -*-
"""CTA-EDGE-05 / F6 — end-to-end orchestration, A through K.

```
A sealed authority loading      f6_data.verify_seal_integrity
B input validation              f6_data / f6_engine.build_frame
C event-manifest validation     f6_data.validate_event_manifest
D return construction           f6_engine.simple_returns
E cash proxy mapping            f6_engine.map_cash_rate / rf_hold
F P1                            f6_engine.p1_mean
G P2 regression                 f6_engine.ols_beta_event
H year-block bootstrap          f6_inference
I P3 LOYO                       f6_engine.loyo
J terminal classifier           f6_classify.classify
K result serialization          f6_report
```

`run_synthetic()` exercises every branch on fixtures. `run_real()` is the
production path and its FIRST action is the run guard, so at S2 it raises before
a single historical price byte is parsed.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Sequence

import numpy as np
import pandas as pd

import f6_authorization as auth
import f6_classify as fcls
import f6_contract as K
import f6_data as fdata
import f6_engine as feng
import f6_inference as finf
import f6_report as frep


def build_cash_vector(frame: pd.DataFrame, vdates, values,
                      rows_present) -> np.ndarray:
    """rf_hold for every row, benchmark date = prev(d). Fail-closed on a gap."""
    out = np.empty(len(frame), float)
    for i, (d, p, h) in enumerate(zip(frame.index, frame["prev"],
                                      frame["HOLD"])):
        rate, _carry = feng.map_cash_rate(p, vdates, values, rows_present)
        out[i] = feng.rf_hold(rate, int(h))
    return out


def evaluate(frame: pd.DataFrame, r_excess: np.ndarray, b: int,
             seed: int = K.BOOTSTRAP_SEED_LITERAL) -> Dict[str, Any]:
    """F + G + H + I + J on a prepared population. No I/O, no authority reads."""
    p1_point, p2_point = feng.point_estimates(frame, r_excess)
    draws = finf.bootstrap(frame, r_excess, b=b, seed=seed)
    p1 = finf.summarize(draws["p1_draws"], p1_point)
    p2 = finf.summarize(draws["beta_event_draws"], p2_point)

    # P3 is evaluated ONLY on the harvestable+specific branch. Computing it
    # elsewhere would manufacture an unsealed quantity, so we do not.
    if fcls.p3_is_evaluated(p1["klass"], p2["klass"]):
        p3 = feng.loyo(frame, r_excess)
        verdict = fcls.classify(p1["klass"], p2["klass"], p3["p3_pass"])
    else:
        p3 = None
        verdict = fcls.classify(p1["klass"], p2["klass"], None)
    return {"p1": p1, "p2": p2, "p3": p3, "verdict": verdict,
            "bootstrap": {"b": draws["b"], "seed": draws["seed"],
                          "blocks": draws["blocks"]}}


def run_synthetic(fixture: Dict[str, Any], b: int = 200) -> Dict[str, Any]:
    """The synthetic path. Never touches sealed files or real prices."""
    auth.require_run_authorization(auth.SYNTHETIC)
    frame = fixture["frame"]
    r_excess = fixture["r_excess"]
    return evaluate(frame, r_excess, b=b, seed=fixture.get("seed",
                                                           K.BOOTSTRAP_SEED_LITERAL))


def run_real(run_id: str, progress=None) -> Dict[str, Any]:
    """THE PRODUCTION PATH. Refuses at S2.

    Order matters and is deliberate: the guard fires before seal verification,
    before the manifest is read and long before any price is parsed, so a
    refusal cannot leak so much as a file handle on the outcome panel.
    """
    auth.require_run_authorization(auth.REAL, run_id=run_id)      # FIRST

    fdata.verify_seal_integrity(strict=True)                      # A
    fam = fdata.load_event_manifest()                             # C
    sessions = fdata.panel_sessions()
    grid, boundary = fdata.primary_grid(sessions)                 # B
    import sys as _sys
    _sys.path.insert(0, K.REPO)
    import config as _cfg
    from src import seasonality as _seas
    tom = _seas.is_tom(grid, last=_cfg.SEAS_TOM_LAST,
                       first=_cfg.SEAS_TOM_FIRST).astype(int).values
    frame = feng.build_frame(grid, boundary, set(fam), tom,
                             fdata.auction_sessions(sessions))
    if len(frame) != K.P2_ROWS:
        raise feng.SealedSpecViolation(
            "P2 population is %d rows, sealed %d" % (len(frame), K.P2_ROWS))
    if int(frame["EVENT"].sum()) != K.FINAL_PRIMARY_EVENT_COUNT:
        raise feng.SealedSpecViolation("EVENT count does not match the seal")
    feng.check_design_rank(feng.design_matrix(frame))

    prices = fdata.load_price_values(auth.REAL, run_id=run_id)    # D (guarded)
    R = feng.simple_returns(prices, grid, list(frame["prev"]))
    vdates, values, rows_present = fdata.load_cash_series()       # E
    rf = build_cash_vector(frame, vdates, values, rows_present)
    r_excess = feng.excess_returns(R, rf)

    res = evaluate(frame, r_excess, b=K.BOOTSTRAP_B,              # F-J
                   seed=K.BOOTSTRAP_SEED_LITERAL)
    res["run_id"] = run_id
    return res


def status() -> Dict[str, Any]:
    """Outcome-blind build status. Safe to call at any time."""
    a = auth.authorization_status()
    return {
        "lineage": K.LINEAGE, "seal_id": K.SEAL_ID,
        "seal_commit": K.SEAL_COMMIT,
        "S1": K.S1_STATUS,
        "S2_BUILD_AUTHORIZED": K.S2_BUILD_AUTHORIZED,
        "S3_RUN_AUTHORIZED": bool(a["real_run_authorized"]),
        "RETURN_REVEAL_AUTHORIZED": K.RETURN_REVEAL_AUTHORIZED,
        "HISTORICAL_OUTCOME_RUN": "NOT_AUTHORIZED"
        if not a["real_run_authorized"] else "AUTHORIZED",
        "authorization": a,
        "empty_result_schema_valid":
            frep.validate_result(frep.empty_result())["ok"],
    }
