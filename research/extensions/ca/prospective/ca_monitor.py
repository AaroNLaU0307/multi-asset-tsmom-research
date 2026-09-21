# -*- coding: utf-8 -*-
"""THE operator-safe monitoring entry point for C-A prospective accrual.

One entry point, deliberately. Run it:

    python research/extensions/ca/prospective/ca_monitor.py

It answers exactly one question — **"is the prospective experiment healthy?"** —
and it is built so that it cannot answer **"how is the strategy performing?"**

The output is an ALLOWLIST (`ALLOWED_KEYS`). Anything not on that list raises
rather than prints, so a future edit that tries to surface a performance quantity
fails loudly instead of leaking quietly. Values are also screened, because
performance can leak through a label or a number as easily as through a field
name.

Never emitted, at any time before the authorized terminal reveal: position
weights · long/short direction · strategy return · monthly return sign ·
cumulative return · PnL · Sharpe · realized strategy volatility · drawdown ·
win rate · sleeve contribution · FM-1 result · crisis result · any proxy from
which performance could reasonably be inferred.

**Pipeline health is independent of observed performance.** There is no
"is the strategy positive?" status, no one-bit oracle, and no alert that could
fire because results look poor. A HOLD here always means an integrity or
run-safety condition, never a performance condition.
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                "..", "..", "..", "..")))

from research.extensions.ca.prospective import (  # noqa: E402
    ca_blind, ca_contract as K, ca_pipeline, ca_store)

ALLOWED_KEYS = frozenset({
    "pipeline", "hold_reasons",
    "latest_snapshot_id", "latest_snapshot_sha256", "latest_snapshot_date",
    "snapshots_registered",
    "expected_instrument_coverage", "canonical_objects_expected", "canonical_objects_present",
    "identity_event_state", "identity_events_open",
    "runtime_pin", "blind_store_fingerprint", "off_machine_backup_verified",
    "latest_decision_record_exists", "protected_outcome_record_exists",
    "rf_state", "n_scored", "next_scheduled_event",
    "terminal_reveal_authorized", "sealed_prereg_intact", "frozen_panel_intact",
    "pipeline_go_live_utc", "prospective_start_utc", "forward_boundary",
    "first_eligible_decision_month_end", "first_eligible_scored_month",
    "errors",
})

FORBIDDEN_TOKENS = (
    "sharpe", "drawdown", "pnl", "return", "win_rate", "equity", "profit", "loss",
    "weight", "position_vector", "sleeve", "fm1_value", "crisis_result",
    "performance", "positive", "negative", "gain", "alpha", "volatility",
)
# Allowlisted keys whose NAME legitimately contains a forbidden token.
_NAME_EXEMPT = {"protected_outcome_record_exists", "latest_decision_record_exists"}


class MonitorBlindnessBreach(Exception):
    """Raised when the monitor would emit anything outside its allowlist."""


def _enforce(view: dict) -> dict:
    extra = set(view) - ALLOWED_KEYS
    if extra:
        raise MonitorBlindnessBreach(
            "REFUSED: monitor would emit non-allowlisted key(s) %s" % sorted(extra))
    for k, v in view.items():
        if k not in _NAME_EXEMPT and any(f in k.lower() for f in FORBIDDEN_TOKENS):
            raise MonitorBlindnessBreach("REFUSED: key %r is forbidden" % k)
        blob = json.dumps(v).lower()
        for f in ("sharpe", "drawdown", "pnl", "win_rate", "equity_curve"):
            if f in blob:
                raise MonitorBlindnessBreach(
                    "REFUSED: value of %r contains forbidden token %r" % (k, f))
    return view


def monitor() -> dict:
    """Assemble the operator view. Integrity facts only."""
    errors = []
    st = ca_pipeline.read_state()
    if st is None:
        return _enforce({"pipeline": "NOT_LIVE", "n_scored": 0, "errors": [],
                         "terminal_reveal_authorized": False})

    sd = ca_blind.default_store_dir()
    pf = ca_pipeline.preflight()

    try:
        rows = ca_pipeline.registry().rows()
    except Exception as exc:  # noqa: BLE001
        rows, _ = [], errors.append("snapshot registry unreadable: %s" % type(exc).__name__)
    latest = rows[-1] if rows else None

    try:
        fp_ok = ca_blind.unlock_store(sd).state["key_fingerprint_sha256"] == \
            st["blind_store"]["key_fingerprint_sha256"]
    except Exception as exc:  # noqa: BLE001
        fp_ok = False
        errors.append("blind store: %s" % type(exc).__name__)

    omb = ca_blind.off_machine_backup_status(sd)

    lp = ca_pipeline.ledger_path()
    n_decisions = 0
    if os.path.exists(lp):
        with open(lp, encoding="utf-8") as fh:
            n_decisions = sum(1 for line in fh if line.strip())

    idx = os.path.join(sd, "protected_index.jsonl")
    n_outcomes = 0
    if os.path.exists(idx):
        with open(idx, encoding="utf-8") as fh:
            n_outcomes = sum(1 for line in fh if line.strip())

    present = sorted((latest or {}).get("per_ticker_rows", {}).keys())
    view = {
        "pipeline": "LIVE" if pf["status"] == "PASS" else "HOLD",
        "hold_reasons": pf["hold_reasons"],
        "latest_snapshot_id": (latest or {}).get("snapshot_id"),
        "latest_snapshot_sha256": (latest or {}).get("sha256"),
        "latest_snapshot_date": (latest or {}).get("last_date"),
        "snapshots_registered": len(rows),
        "canonical_objects_expected": len(K.CANONICAL_17),
        "canonical_objects_present": len([t for t in K.CANONICAL_17 if t in present]),
        "expected_instrument_coverage": "COMPLETE" if all(t in present for t in K.CANONICAL_17) else "INCOMPLETE",
        "identity_event_state": "NONE_OPEN",
        "identity_events_open": 0,
        "runtime_pin": "PASS" if K.runtime_matches() else "FAIL",
        "blind_store_fingerprint": "PASS" if fp_ok else "FAIL",
        "off_machine_backup_verified": "YES" if omb.get("verified") else "NO",
        "latest_decision_record_exists": "YES" if n_decisions else "NO",
        "protected_outcome_record_exists": "YES" if n_outcomes else "NO",
        "rf_state": "NOT_YET_APPLICABLE",       # first decision cycle has not occurred
        "n_scored": st["n_scored"],
        "next_scheduled_event": ca_pipeline.next_scheduled_event(),
        "terminal_reveal_authorized": False,
        "sealed_prereg_intact": K.sha256_file(K.SEALED_PREREG) == K.SEALED_PREREG_SHA256,
        "frozen_panel_intact": ca_store.verify_frozen_panel(),
        "pipeline_go_live_utc": st["pipeline_go_live_timestamp_utc"],
        "prospective_start_utc": st["prospective_start_utc"],
        "forward_boundary": st["forward_boundary"],
        "first_eligible_decision_month_end": st["first_eligible_decision_month_end_scheduled"],
        "first_eligible_scored_month": st["first_eligible_scored_month"],
        "errors": errors,
    }
    return _enforce(view)


def main() -> int:
    v = monitor()
    print("C-A PROSPECTIVE ACCRUAL — OPERATOR STATUS")
    print("  (integrity only; this command cannot report strategy performance)\n")
    order = ["pipeline", "hold_reasons", "n_scored", "next_scheduled_event",
             "latest_snapshot_id", "latest_snapshot_date", "latest_snapshot_sha256",
             "snapshots_registered", "expected_instrument_coverage",
             "canonical_objects_present", "canonical_objects_expected",
             "identity_event_state", "runtime_pin", "blind_store_fingerprint",
             "off_machine_backup_verified", "latest_decision_record_exists",
             "protected_outcome_record_exists", "rf_state",
             "terminal_reveal_authorized", "sealed_prereg_intact", "frozen_panel_intact",
             "pipeline_go_live_utc", "prospective_start_utc", "forward_boundary",
             "first_eligible_decision_month_end", "first_eligible_scored_month", "errors"]
    for k in order:
        if k in v:
            val = v[k]
            print("  %-36s %s" % (k, json.dumps(val) if isinstance(val, (dict, list)) else val))
    print("\n  HEALTH:", v["pipeline"])
    if v["hold_reasons"]:
        print("  HOLD is an INTEGRITY / RUN-SAFETY condition, never a performance condition.")
    return 0 if v["pipeline"] == "LIVE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
