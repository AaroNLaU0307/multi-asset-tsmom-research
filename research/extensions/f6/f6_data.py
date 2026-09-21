# -*- coding: utf-8 -*-
"""CTA-EDGE-05 / F6 — (B) input validation and (C) event-manifest validation.

Two access tiers, and the split is the firewall:

* **metadata tier** — schemas, column names, file hashes, date indices, the
  event manifest, calendar metadata. Permitted at S2, needs no authorization,
  and **never parses the SPY column**.
* **value tier** — `load_price_values()` is the ONLY function in the package
  that parses a real price, and its first statement is the run guard.

`f6_tests.py` proves the split by source inspection, not by assertion.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

import f6_authorization as auth
import f6_contract as K


class SealIntegrityError(RuntimeError):
    """A pinned authority does not reproduce. Never repaired, only reported."""


class InputValidationError(RuntimeError):
    """A sealed input requirement failed. Deterministic STOP, no fallback."""


def sha256_file(relpath: str) -> str:
    with open(K.abspath(relpath), "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


# --------------------------------------------------------------------------- #
# (A) sealed authority loading                                                #
# --------------------------------------------------------------------------- #
def verify_seal_integrity(strict: bool = True) -> Dict[str, Any]:
    """Recompute every pin the engine depends on. Fail-closed."""
    pins = {
        "sealed_preregistration": (K.SEALED_PREREG_RELPATH, K.SEALED_PREREG_SHA256),
        "sealed_manifest": (K.SEALED_MANIFEST_RELPATH, K.SEALED_MANIFEST_SHA256),
        "seal_record": (K.SEAL_RECORD_RELPATH, K.SEAL_RECORD_SHA256),
        "event_manifest": (K.EVENT_MANIFEST_RELPATH, K.EVENT_MANIFEST_SHA256),
        "spy_panel": (K.PANEL_RELPATH, K.PANEL_SHA256),
        "cash_series": (K.CASH_RELPATH, K.CASH_SHA256),
        "auction_calendar": (K.AUCTION_RELPATH, K.AUCTION_SHA256),
    }
    out, bad = {}, []
    for name, (rel, want) in pins.items():
        p = K.abspath(rel)
        if not os.path.isfile(p):
            out[name] = {"path": rel, "expected": want, "got": None,
                         "ok": False}
            bad.append(name)
            continue
        got = sha256_file(rel)
        ok = (got == want)
        out[name] = {"path": rel, "expected": want, "got": got, "ok": ok}
        if not ok:
            bad.append(name)
    res = {"ok": not bad, "failed": bad, "pins": out,
           "seal_id": K.SEAL_ID, "seal_commit": K.SEAL_COMMIT}
    if bad and strict:
        raise SealIntegrityError(
            "SEAL INTEGRITY FAILURE — these pinned authorities do not "
            "reproduce: %s. The sealed authority is NOT repaired here." % bad)
    return res


# --------------------------------------------------------------------------- #
# (C) event-manifest validation                                               #
# --------------------------------------------------------------------------- #
def load_event_manifest(path: Optional[str] = None,
                        verify_hash: bool = True) -> Dict[str, List[str]]:
    """The sealed 462-session event sample, validated against the contract."""
    rel = K.EVENT_MANIFEST_RELPATH if path is None else None
    p = K.abspath(K.EVENT_MANIFEST_RELPATH) if path is None else path
    if verify_hash and rel is not None:
        got = sha256_file(rel)
        if got != K.EVENT_MANIFEST_SHA256:
            raise SealIntegrityError(
                "event manifest hash %s != sealed %s"
                % (got, K.EVENT_MANIFEST_SHA256))
    with open(p, encoding="utf-8") as fh:
        doc = json.load(fh)
    fam = {e["session"]: sorted(e["families"]) for e in doc["event_sessions"]}
    validate_event_manifest(fam)
    return fam


def validate_event_manifest(fam: Dict[str, List[str]],
                            expect_counts: bool = True) -> Dict[str, Any]:
    """Every sealed count identity, enforced. A failure is a STOP."""
    labels: Dict[str, int] = {}
    for v in fam.values():
        for f in v:
            labels[f] = labels.get(f, 0) + 1
    overlap = sum(len(v) - 1 for v in fam.values())
    multi = sum(1 for v in fam.values() if len(v) > 1)
    n = len(fam)

    bad = set(labels) - set(K.FAMILIES)
    if bad:
        raise InputValidationError("unknown event families: %s" % sorted(bad))
    for s in fam:
        y = int(s[:4])
        if y in K.PROHIBITED_YEARS:
            raise InputValidationError(
                "PROHIBITED YEAR %d present in the event manifest (%s). 2026 "
                "carries no F6 outcome quantity." % (y, s))
        if not (K.PRIMARY_YEAR_FIRST <= y <= K.PRIMARY_YEAR_LAST):
            raise InputValidationError("session %s is outside 2011..2025" % s)
    for f, d in K.PIT_EXCLUSIONS:
        if f in fam.get(d, []):
            raise InputValidationError(
                "PIT_UNRESOLVED label %s %s was REINSTATED. The sealed rule "
                "forbids post-seal reinstatement." % (f, d))
    if sum(labels.values()) - overlap != n:
        raise InputValidationError(
            "label reconciliation failed: %d labels - %d overlap != %d sessions"
            % (sum(labels.values()), overlap, n))
    if expect_counts:
        if n != K.FINAL_PRIMARY_EVENT_COUNT:
            raise InputValidationError(
                "event count %d != sealed %d" % (n, K.FINAL_PRIMARY_EVENT_COUNT))
        if labels != K.FAMILY_LABELS:
            raise InputValidationError(
                "family labels %s != sealed %s" % (labels, K.FAMILY_LABELS))
        if sum(labels.values()) != K.FAMILY_LABELS_TOTAL:
            raise InputValidationError("family label total mismatch")
        if multi != K.MULTI_EVENT_SESSIONS or overlap != K.OVERLAP_ADJUSTMENT:
            raise InputValidationError(
                "overlap mismatch: multi %d overlap %d" % (multi, overlap))
    return {"n_sessions": n, "labels": labels, "multi": multi,
            "overlap": overlap}


# --------------------------------------------------------------------------- #
# metadata tier — NEVER parses the SPY column                                 #
# --------------------------------------------------------------------------- #
def panel_sessions() -> pd.DatetimeIndex:
    """The panel DATE INDEX only. `usecols=['Date']` — no price byte is parsed."""
    df = pd.read_csv(K.abspath(K.PANEL_RELPATH), usecols=["Date"],
                     parse_dates=["Date"])
    return pd.DatetimeIndex(sorted(df["Date"].unique()))


def panel_columns() -> List[str]:
    """Header row only — schema metadata."""
    with open(K.abspath(K.PANEL_RELPATH), encoding="utf-8") as fh:
        return next(csv.reader(fh))


def primary_grid(sessions: Optional[pd.DatetimeIndex] = None
                 ) -> Tuple[pd.DatetimeIndex, pd.Timestamp]:
    """The sealed P2 population and its opening boundary input.

    Returns (grid, boundary). `grid` is EVERY 2011..2025 trading session, with
    NO row dropped. `boundary` is the immediately preceding panel session — an
    INPUT BOUNDARY OBSERVATION, never a regression row.
    """
    s = panel_sessions() if sessions is None else sessions
    lo = pd.Timestamp("%d-01-01" % K.PRIMARY_YEAR_FIRST)
    hi = pd.Timestamp("%d-12-31" % K.PRIMARY_YEAR_LAST)
    grid = s[(s >= lo) & (s <= hi)]
    if len(grid) == 0:
        raise InputValidationError("empty primary grid")
    i0 = s.searchsorted(grid[0], side="left")
    if i0 == 0:
        raise InputValidationError(
            "no prior panel session exists before %s, so the sealed opening "
            "boundary rule cannot be satisfied" % grid[0].date())
    boundary = s[i0 - 1]
    if boundary.year >= K.PRIMARY_YEAR_FIRST:
        raise InputValidationError("boundary session is not prior-year")
    return grid, boundary


def auction_sessions(sessions: pd.DatetimeIndex) -> set:
    """AUCTION(d) support: 10y/30y nominal coupon auctions, sealed definition."""
    out = set()
    with open(K.abspath(K.AUCTION_RELPATH), encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["tenor_family"] in K.AUCTION_TENORS and r["auction_date"]:
                j = sessions.searchsorted(pd.Timestamp(r["auction_date"]),
                                          side="left")
                if j < len(sessions):
                    out.add(sessions[j])
    return out


def load_cash_series(path: Optional[str] = None) -> Tuple[pd.DatetimeIndex, Dict, set]:
    """DGS3MO observations. A RATE, not a target outcome; not firewalled."""
    p = K.abspath(K.CASH_RELPATH) if path is None else path
    r = pd.read_csv(p)
    r["observation_date"] = pd.to_datetime(r["observation_date"])
    r[K.CASH_SERIES] = pd.to_numeric(r[K.CASH_SERIES], errors="coerce")
    rows_present = set(r["observation_date"])
    have = r.loc[r[K.CASH_SERIES].notna()]
    values = dict(zip(have["observation_date"], have[K.CASH_SERIES]))
    return pd.DatetimeIndex(sorted(values)), values, rows_present


# --------------------------------------------------------------------------- #
# value tier — THE ONLY REAL-PRICE READER. Guarded.                           #
# --------------------------------------------------------------------------- #
def load_price_values(data_kind: str, run_id: str = "") -> pd.Series:
    """Parse the real SPY column. **Refuses without a committed Owner grant.**

    This is the single choke point. Every other function in this package works
    on dates, schemas, hashes and the event manifest, so at S2 no code path
    reaches a price value at all.
    """
    auth.require_run_authorization(data_kind, run_id=run_id)   # FIRST statement
    if data_kind != auth.REAL:
        raise auth.RunNotAuthorized(
            "load_price_values is the REAL reader; synthetic runs supply their "
            "own fixture prices and must not call it")
    df = pd.read_csv(K.abspath(K.PANEL_RELPATH), usecols=["Date",
                                                          K.PRIMARY_TICKER],
                     parse_dates=["Date"]).set_index("Date")
    return df[K.PRIMARY_TICKER]
