# -*- coding: utf-8 -*-
"""C-A prospective pipeline orchestrator — go-live and the monthly cycle.

Operator-facing by design: `status()` emits only sealed §T.2 allowlisted facts.
Nothing here prints a position vector, a return, or any performance quantity.

`go_live()` is run ONCE, under an Owner `GoLiveAuthorization`. It acquires and
registers `S_G`, establishes `PIPELINE_GO_LIVE`, and fixes `PROSPECTIVE_START`,
`FORWARD_BOUNDARY`, the first eligible decision month-end and the first eligible
scored month. It does not compute a position: the first decision belongs to the
first eligible decision month-end, not to go-live.
"""
from __future__ import annotations

import io
import json
import os
import time
from datetime import datetime, timezone

import pandas as pd

from . import ca_blind
from . import ca_contract as K
from . import ca_identity
from . import ca_store

# Market data is git-ignored in this repository for vendor licensing; identity is
# pinned in tracked state instead (CA_SNAPSHOT_REGISTRY.md).
SNAPSHOT_DIR = "data/prospective/snapshots"
SNAPSHOT_REGISTRY = "data/prospective/ca_snapshot_registry.jsonl"
# Operational state IS tracked: it carries identity and dates, never key material,
# never a position, never an outcome.
OPERATIONAL_STATE = "research/extensions/ca/prospective/CA_OPERATIONAL_STATE.json"


def registry() -> ca_store.SnapshotRegistry:
    return ca_store.SnapshotRegistry(SNAPSHOT_REGISTRY, SNAPSHOT_DIR)


def ledger_path() -> str:
    """The position ledger lives in the protected store, outside the repository."""
    return os.path.join(ca_blind.default_store_dir(), "positions.jsonl")


# --------------------------------------------------------------------------- #
# Operational state
# --------------------------------------------------------------------------- #
def read_state():
    p = K.repo_path(OPERATIONAL_STATE)
    if not os.path.exists(p):
        return None
    with io.open(p, encoding="utf-8") as fh:
        return json.load(fh)


def _write_state(state: dict) -> str:
    p = K.repo_path(OPERATIONAL_STATE)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(state, fh, indent=2, sort_keys=True)
        fh.write("\n")
    return p


# --------------------------------------------------------------------------- #
# Sealed acquisition path (identical call shape to src/fetch_data.py::_fetch_one)
# --------------------------------------------------------------------------- #
def acquire_panel(tickers=None) -> tuple:
    import yfinance as yf

    tickers = list(tickers or K.CANONICAL_17)
    series, meta = {}, []
    for t in tickers:
        s, err = None, ""
        for attempt in range(1, 5):
            try:
                df = yf.Ticker(t).history(period="max", auto_adjust=True)
                if df is None or df.empty or "Close" not in df.columns:
                    err = "empty response"
                else:
                    x = df["Close"].copy()
                    idx = pd.to_datetime(x.index)
                    if idx.tz is not None:
                        idx = idx.tz_localize(None)
                    x.index = idx.normalize()
                    x = x[~x.index.duplicated(keep="last")].sort_index()
                    x.name = t
                    if len(x) > 0:
                        s = x
                        break
                    err = "zero rows after cleaning"
            except Exception as exc:  # noqa: BLE001
                err = "%s: %s" % (type(exc).__name__, exc)
            time.sleep(1.0 * attempt)
        meta.append({"ticker": t, "ok": s is not None,
                     "rows": int(s.notna().sum()) if s is not None else 0,
                     "error": err if s is None else ""})
        if s is not None:
            series[t] = s
        time.sleep(1.0)
    panel = pd.DataFrame(series).sort_index()
    panel.index.name = "Date"
    return panel, meta


# --------------------------------------------------------------------------- #
# Boundary arithmetic
# --------------------------------------------------------------------------- #
def _naive(ts):
    t = pd.Timestamp(ts)
    return t.tz_convert(None) if t.tz is not None else t


def scheduled_first_decision(prospective_start) -> dict:
    """First canonical decision month-end STRICTLY AFTER prospective_start.

    The canonical decision date is the last TRADING day of a calendar month. Its
    exact date is confirmed mechanically from the snapshot when that month closes;
    the scheduled value below uses the last business day and is labelled as such.
    """
    ps = _naive(prospective_start)
    month_end = (ps + pd.offsets.MonthEnd(0))
    cand = month_end if month_end.weekday() < 5 else month_end - pd.offsets.BDay(1)
    if cand <= ps:
        nxt = ps + pd.offsets.MonthEnd(1)
        cand = nxt if nxt.weekday() < 5 else nxt - pd.offsets.BDay(1)
    holding = (cand + pd.offsets.MonthBegin(1))
    return {
        "first_eligible_decision_month_end_scheduled": str(cand.date()),
        "first_eligible_decision_month": "%04d-%02d" % (cand.year, cand.month),
        "first_eligible_scored_month": "%04d-%02d" % (holding.year, holding.month),
        "rule": ("the last TRADING day of the decision month, strictly after "
                 "PROSPECTIVE_START; the exact date is confirmed from that month's "
                 "snapshot and may move if it is an exchange holiday"),
    }


# --------------------------------------------------------------------------- #
# GO-LIVE — once, under Owner authorization
# --------------------------------------------------------------------------- #
def go_live(authorization, *, note: str = "") -> dict:
    K.assert_seal_intact()
    K.assert_runtime(strict=True)
    ca_store.assert_frozen_panel_intact("go-live start")

    if read_state() is not None:
        raise RuntimeError("REFUSED: PIPELINE_GO_LIVE is already recorded; go-live happens once")
    sd = ca_blind.default_store_dir()
    if not ca_blind.is_initialized(sd):
        raise ca_blind.ProtectedStoreNotInitialized(
            "REFUSED: initialize the protected store before go-live")
    vb = ca_blind.verify_backup(sd)
    if not (vb["exists"] and vb["fingerprint_match"]):
        raise ca_blind.ProtectedStoreHold(
            "REFUSED: the production key has no verified off-repository backup. "
            "No protected prospective record may be written without one.")
    sess = ca_blind.unlock_store(sd)          # verifies the fingerprint

    reg = registry()
    if any(r.get("kind") == "S_G" for r in reg.rows()):
        raise RuntimeError("REFUSED: an S_G is already registered")

    acq_start = datetime.now(timezone.utc).replace(microsecond=0)
    panel, meta = acquire_panel()
    acq_end = datetime.now(timezone.utc).replace(microsecond=0)

    missing = [t for t in K.CANONICAL_17 if t not in panel.columns]
    if missing:
        raise RuntimeError("REFUSED: S_G is missing canonical objects: %s" % missing)

    sg_id = "S_G_%s" % acq_start.strftime("%Y%m%dT%H%M%SZ")
    row = reg.register_snapshot(sg_id, panel, kind="S_G",
                                note=note or "C-A go-live base snapshot (sealed §E.1)")

    ca_store.assert_frozen_panel_intact("after S_G registration")

    # PIPELINE_GO_LIVE = the moment the pipeline is accepted AND has taken its
    # first snapshot under the sealed rule (§E). Not the acquisition start.
    go_live_utc = datetime.now(timezone.utc).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")
    prospective_start = max(pd.Timestamp(K.SEAL_TIMESTAMP_UTC), pd.Timestamp(go_live_utc))
    trading_days = pd.DatetimeIndex(panel.index)
    prior = [d for d in trading_days if d < _naive(prospective_start)]
    forward_boundary = str(prior[-1].date()) if prior else None
    sched = scheduled_first_decision(prospective_start)

    reg_identity = ca_identity.registry_identity(ca_identity.load_registry())
    state = {
        "schema": "CA_OPERATIONAL_STATE_V1",
        "c_a_s1": "SEALED",
        "sealed_prereg_sha256": K.SEALED_PREREG_SHA256,
        "c_a_seal_timestamp_utc": K.SEAL_TIMESTAMP_UTC,
        "c_a_s2_build": "COMPLETE",
        "c_a_pipeline": "LIVE",
        "pipeline_go_live_timestamp_utc": go_live_utc,
        "prospective_start_utc": str(prospective_start),
        "forward_boundary": forward_boundary,
        "first_eligible_decision_month_end_scheduled": sched["first_eligible_decision_month_end_scheduled"],
        "first_eligible_decision_month": sched["first_eligible_decision_month"],
        "first_eligible_scored_month": sched["first_eligible_scored_month"],
        "first_eligible_rule": sched["rule"],
        "n_scored": 0,
        "s_g": {k: row[k] for k in ("snapshot_id", "path", "sha256", "byte_size",
                                    "rows", "columns", "first_date", "last_date",
                                    "registered_utc")},
        "s_g_acquisition": {
            "started_utc": acq_start.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "finished_utc": acq_end.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "source": "yfinance (Yahoo Finance), Ticker.history(period='max', auto_adjust=True)",
            "yfinance_version": __import__("yfinance").__version__,
            "acquisition_runtime_note": ("yfinance is recorded but deliberately NOT in the hard "
                                         "runtime pin: the scientific computation runs on the "
                                         "REGISTERED, HASHED snapshot, not on the fetch library, "
                                         "and halting a 10-year pipeline on a vendor patch bump "
                                         "would protect nothing scientific."),
            "tickers_requested": len(K.CANONICAL_17),
            "tickers_acquired": int(panel.shape[1]),
            "all_canonical_present": True,
        },
        "s_0": {"path": K.S0_PATH, "sha256": K.S0_SHA256},
        "frozen_panel": {"path": K.FROZEN_PANEL, "sha256": K.FROZEN_PANEL_SHA256},
        "instrument_registry": reg_identity,
        "runtime": K.current_runtime(),
        "blind_store": {
            "store_dir": sd,
            "key_fingerprint_sha256": sess.state["key_fingerprint_sha256"],  # NON-SECRET
            "aead": sess.state["aead"],
            "backup_verified": True,
            "backup_path": vb["backup_path"],
        },
        "post_seal_unscored_state_input_only": {
            "window": "observations after the C-A seal and strictly before PROSPECTIVE_START",
            "may_update_state": True,
            "scored": False,
            "counts_toward_n_scored": False,
            "may_be_relabelled_t4_later": False,
        },
        "terminal_reveal_authorized": False,
        "target_performance_computed": False,
        "target_outcome_revealed": False,
        "recorded_utc": go_live_utc,
    }
    # The authorization is single-use. A second go-live is refused by the state
    # file above as well, but the object must not remain spendable.
    if getattr(authorization, "consumed", False):
        raise RuntimeError("REFUSED: this go-live authorization is already consumed")
    authorization.consumed = True
    state["owner_authorization"] = {
        "authorization_id": authorization.authorization_id,
        "owner": authorization.owner,
        "granted_utc": authorization.granted_utc,
        "scope": authorization.scope,
        "consumed": True,
        "consumed_utc": go_live_utc,
        "is_not": ["TARGET_REVEAL_AUTHORIZATION", "C_D_AUTHORIZATION",
                   "PHASE_C_AUTHORIZATION", "TERMINAL_ADJUDICATION_AUTHORIZATION"],
    }
    _write_state(state)
    return state


# --------------------------------------------------------------------------- #
# Operator-safe status — sealed §T.2 only
# --------------------------------------------------------------------------- #
def status() -> dict:
    st = read_state()
    if st is None:
        return {"pipeline": "NOT_LIVE", "n_scored": 0}
    sd = ca_blind.default_store_dir()
    lp = ledger_path()
    n_records = 0
    if os.path.exists(lp):
        with io.open(lp, encoding="utf-8") as fh:
            n_records = sum(1 for line in fh if line.strip())
    return {
        "pipeline": st["c_a_pipeline"],
        "pipeline_go_live_timestamp_utc": st["pipeline_go_live_timestamp_utc"],
        "prospective_start_utc": st["prospective_start_utc"],
        "forward_boundary": st["forward_boundary"],
        "first_eligible_decision_month_end_scheduled": st["first_eligible_decision_month_end_scheduled"],
        "first_eligible_scored_month": st["first_eligible_scored_month"],
        "n_scored": st["n_scored"],
        "position_records_locked": n_records,
        "snapshots_registered": len(registry().rows()),
        "s_g_sha256": st["s_g"]["sha256"],
        "blind_store_initialized": ca_blind.is_initialized(sd),
        "key_fingerprint_sha256": st["blind_store"]["key_fingerprint_sha256"],
        "key_backup_verified": ca_blind.verify_backup(sd)["fingerprint_match"],
        "runtime_matches": K.runtime_matches(),
        "sealed_prereg_intact": K.sha256_file(K.SEALED_PREREG) == K.SEALED_PREREG_SHA256,
        "frozen_panel_intact": ca_store.verify_frozen_panel(),
        "terminal_reveal_authorized": False,
        "target_performance_computed": False,
        "target_outcome_revealed": False,
    }
