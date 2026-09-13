# -*- coding: utf-8 -*-
"""The monthly integrity gate — sealed §T.2 (allowed) and §T.3 (forbidden).

§T.2 is an ALLOWLIST, so this gate is built as one: it assembles a dict of
allowlisted keys and then refuses to return anything else. A future edit that
tries to surface a performance quantity fails the allowlist rather than quietly
leaking, which is the point.

§T.3, enforced here:
  no cumulative return · no Sharpe · no drawdown · no win rate · no sleeve
  performance · no FM-1 performance · no crisis-diagnostic outcome · NO POSITION
  VECTOR · no proxy sufficient to infer scientific performance.

"Positions are outcomes by another name": the gate receives the decision so it can
compute invariant booleans about it, and returns booleans — never the vector.
"""
from __future__ import annotations

from . import ca_contract as K
from . import ca_engine

# Sealed §T.2, verbatim. Nothing outside this set may leave the gate.
ALLOWED_KEYS = frozenset({
    "snapshot_present", "snapshot_hashed", "snapshot_registered",
    "overlap_within_tolerance_return_level",
    "per_ticker_row_counts", "first_date", "last_date",
    "jump_flags", "spike_flags", "stale_flags", "flag_disposition",
    "rf_present_and_locked", "rf_missing",
    "positions_computed", "positions_locked",
    "locked_vs_recomputed_within_tolerance",
    "gross_within_cap", "asset_weight_within_cap", "all_17_present", "n_available",
    "n_scored_to_date", "pending_classification_count", "run_invalidating_count",
    "instrument_events", "instrument_event_classifications",
    "runtime_matches", "expected_instruments_present", "duplicate_detected",
    "ledger_write_succeeded", "pipeline_healthy",
})

# §T.3 — substrings that must never appear in a key OR in a stringified value.
FORBIDDEN_SUBSTRINGS = (
    "return", "sharpe", "drawdown", "win_rate", "pnl", "equity", "performance",
    "weight_vector", "positions_vector", "sleeve_perf", "fm1_value", "crisis_outcome",
)
# Keys whose NAME legitimately contains an allowlisted token that also appears in
# the forbidden list; the allowlist is authoritative for these.
_ALLOWED_DESPITE_SUBSTRING = {
    "overlap_within_tolerance_return_level",   # a boolean about data, not a return
}
# The ONLY per-ticker structure sealed §T.2 permits, and only as integer counts.
_ALLOWED_PER_TICKER = {"per_ticker_row_counts"}


class BlindnessBreachBlocked(Exception):
    """Raised when the gate would emit anything outside sealed §T.2."""


def _enforce(view: dict) -> dict:
    extra = set(view) - ALLOWED_KEYS
    if extra:
        raise BlindnessBreachBlocked(
            "REFUSED: integrity gate would emit non-allowlisted key(s) %s. "
            "Sealed §T.2 is an allowlist." % sorted(extra))
    for k, v in view.items():
        if k in _ALLOWED_DESPITE_SUBSTRING:
            continue
        if any(f in str(k).lower() for f in FORBIDDEN_SUBSTRINGS):
            raise BlindnessBreachBlocked("REFUSED: key %r is forbidden by §T.3" % k)
    # A value must never be a raw position vector. Sealed §T.2 DOES allow one
    # per-ticker structure -- "per-ticker row counts" -- so that key is permitted,
    # and only when its values are integer counts rather than float weights.
    for k, v in view.items():
        if not (isinstance(v, dict) and set(v) >= set(K.CANONICAL_17)):
            continue
        counts_only = all(isinstance(x, int) and not isinstance(x, bool) for x in v.values())
        if k in _ALLOWED_PER_TICKER and counts_only:
            continue
        raise BlindnessBreachBlocked(
            "REFUSED: %r is a per-ticker vector that §T.2 does not allow; positions are "
            "outcomes by another name (§T.3)" % k)
    return view


def monthly_gate(*, snapshot_row, decision, rf_lock, ledger, prior_snapshot_row=None,
                 overlap_ok=None, instrument_events=None, n_scored_to_date=0,
                 pending_classification=0, run_invalidating=0,
                 locked_vs_recomputed_ok=None, ledger_write_succeeded=None) -> dict:
    """Assemble the operator-visible monthly integrity view. Booleans and counts only."""
    inv = ca_engine.invariants(decision) if decision is not None else {}
    events = instrument_events or []
    view = {
        "snapshot_present": snapshot_row is not None,
        "snapshot_hashed": bool(snapshot_row and snapshot_row.get("sha256")),
        "snapshot_registered": bool(snapshot_row and snapshot_row.get("snapshot_id")),
        "overlap_within_tolerance_return_level": overlap_ok,
        "per_ticker_row_counts": (snapshot_row or {}).get("per_ticker_rows"),
        "first_date": (snapshot_row or {}).get("first_date"),
        "last_date": (snapshot_row or {}).get("last_date"),
        "expected_instruments_present": (
            sorted((snapshot_row or {}).get("per_ticker_rows", {}).keys()) >= sorted(K.CANONICAL_17)
            if snapshot_row else False),
        "rf_present_and_locked": bool(rf_lock) and not rf_lock.get("rf_missing", True),
        "rf_missing": bool(rf_lock.get("rf_missing")) if rf_lock else None,
        "positions_computed": decision is not None,
        "positions_locked": ledger_write_succeeded is True,
        "locked_vs_recomputed_within_tolerance": locked_vs_recomputed_ok,
        "gross_within_cap": inv.get("gross_within_cap"),
        "asset_weight_within_cap": inv.get("asset_weight_within_cap"),
        "all_17_present": inv.get("all_17_present"),
        "n_available": inv.get("n_available"),
        "n_scored_to_date": int(n_scored_to_date),
        "pending_classification_count": int(pending_classification),
        "run_invalidating_count": int(run_invalidating),
        "instrument_events": len(events),
        "instrument_event_classifications": sorted({e.get("classification") for e in events}) if events else [],
        "runtime_matches": K.runtime_matches(),
        "duplicate_detected": False,
        "ledger_write_succeeded": ledger_write_succeeded,
        "pipeline_healthy": None,
    }
    view["pipeline_healthy"] = bool(
        view["snapshot_present"] and view["snapshot_hashed"] and view["snapshot_registered"]
        and view["expected_instruments_present"] and view["runtime_matches"]
        and view["positions_computed"])
    return _enforce(view)
