# -*- coding: utf-8 -*-
"""The sealed inference engine and decision-state classifiers (§N, §N.1, §O, §P.5).

Architecture is the sealed one and is not a design choice here: stationary
bootstrap (Politis-Romano), expected block length 12 months, 10,000 replicates,
ONE central 95 % percentile interval with linear interpolation, the deterministic
`SeedSequence(7)` protocol, invalid replicates discarded-and-counted against a
9,500 floor, and joint resampling where statistics share the same path.

§N.1: there is ONE interval per estimand. This module offers no confidence-level
parameter, no one-sided option and no alternative construction — those are not
omissions, they are the sealed prohibition expressed as an API.

§N.2: the month draws depend only on (seed, N, block length), never on which
statistics are evaluated, so the primary's interval is bit-identical whether or
not FM-1 is adjudicable.

The S2 test suite validates this module on SYNTHETIC series only and proves it
agrees with the sealed reachability harness.
"""
from __future__ import annotations

import numpy as np

from . import ca_contract as K


class InferenceProcedureFailure(Exception):
    """Mechanical condition (§N) — explicitly NOT one of the §O decision states."""


def sharpe(r: np.ndarray) -> float:
    r = np.asarray(r, dtype=float)
    sd = np.std(r, ddof=1)
    if not np.isfinite(sd) or sd <= 0:
        return float("nan")
    return float(np.mean(r) / sd * np.sqrt(12.0))


def stationary_bootstrap_indices(n: int, n_rep: int, block_len: int, rng) -> np.ndarray:
    """Geometric block lengths, circular wrap. Depends only on (rng, n, block_len)."""
    p = 1.0 / block_len
    starts = rng.integers(0, n, size=(n_rep, n))
    newblock = rng.random((n_rep, n)) < p
    newblock[:, 0] = True
    idx = np.empty((n_rep, n), dtype=np.int64)
    idx[:, 0] = starts[:, 0]
    for t in range(1, n):
        cont = (idx[:, t - 1] + 1) % n
        idx[:, t] = np.where(newblock[:, t], starts[:, t], cont)
    return idx


def draw_indices(n: int, *, n_rep: int = K.BOOTSTRAP_REPLICATES,
                 block_len: int = K.BOOTSTRAP_BLOCK_LEN, arm: int = 0) -> np.ndarray:
    ss = np.random.SeedSequence(K.MASTER_SEED).spawn(arm + 1)[arm]
    return stationary_bootstrap_indices(n, n_rep, block_len, np.random.default_rng(ss))


def interval(series_map: dict, idx: np.ndarray) -> dict:
    """ONE central 95 % percentile interval per statistic, from ONE index matrix."""
    n_rep = idx.shape[0]
    distinct = np.array([len(np.unique(row)) for row in idx])
    enough = distinct >= K.MIN_DISTINCT_MONTHS       # limb 1 — evaluated FIRST (§N)
    out = {}
    for name, s in series_map.items():
        s = np.asarray(s, dtype=float)
        vals = np.full(n_rep, np.nan)
        for k in range(n_rep):
            if enough[k]:
                vals[k] = sharpe(s[idx[k]])          # limb 2 — undefined -> invalid
        valid = np.isfinite(vals)
        n_valid = int(valid.sum())
        if n_valid < K.VALID_REPLICATE_FLOOR:
            out[name] = {"L": None, "U": None, "n_valid": n_valid,
                         "mechanical": "INFERENCE_PROCEDURE_FAILURE"}
            continue
        alpha = (100 - K.CI_LEVEL) / 2.0
        out[name] = {"L": float(np.percentile(vals[valid], alpha)),
                     "U": float(np.percentile(vals[valid], 100 - alpha)),
                     "n_valid": n_valid, "mechanical": None}
    return out


# --------------------------------------------------------------------------- #
# §O primary decision states
# --------------------------------------------------------------------------- #
def primary_state(L: float, U: float) -> dict:
    P_MAT = L > K.POSITIVE_MATERIALITY_FLOOR
    P_POS = L > 0.0
    P_RULED = U < K.POSITIVE_MATERIALITY_FLOOR
    P_ADV = U < K.ADVERSE_MATERIALITY_THRESHOLD
    est = {n for n, v in (("P_MAT", P_MAT), ("P_POS", P_POS),
                          ("P_RULED", P_RULED), ("P_ADV", P_ADV)) if v}
    if P_MAT:
        cid, label = "C1", "MATERIAL_POSITIVE_PERSISTENCE"
    elif P_ADV:
        cid, label = "C4", "MATERIALLY_ADVERSE"
    elif P_POS and P_RULED:
        cid, label = "C2", "POSITIVE_BUT_DECAYED"
    elif P_POS:
        cid, label = "C3", "POSITIVE_SIGN_ESTABLISHED, MATERIALITY_UNRESOLVED"
    elif P_RULED:
        cid, label = "C5", "MATERIAL_PERSISTENCE_RULED_OUT"
    else:
        cid, label = "C6", "UNRESOLVED"
    return {"configuration": cid, "label": label, "established": sorted(est),
            "L": L, "U": U}


# --------------------------------------------------------------------------- #
# §P.5 FM-1 — SIGN AGAINST ZERO ONLY. No materiality floors.
# --------------------------------------------------------------------------- #
def fm1_state(L: float | None, U: float | None, *, rf_missing_unresolved: bool = False) -> dict:
    if rf_missing_unresolved:
        return {"state": "NOT_ADJUDICABLE", "label": "NOT ADJUDICABLE — DATA INCOMPLETE",
                "L": None, "U": None, "primary_adjudication": "UNAFFECTED"}
    if L > 0.0:
        st = "FM1_POSITIVE"
    elif U < 0.0:
        st = "FM1_NEGATIVE"
    else:
        st = "FM1_SIGN_UNRESOLVED"
    return {"state": st, "label": st, "L": L, "U": U}
