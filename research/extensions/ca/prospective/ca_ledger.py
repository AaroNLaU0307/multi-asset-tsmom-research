# -*- coding: utf-8 -*-
"""Append-only, WRITE-ONCE prospective position ledger (sealed §I.1).

    "The vector, its gross, net, leverage and the snapshot hash are written once
     and NEVER changed. No later data can enter it."

Guarantees:
  * one record per intended holding month — a second write for the same month
    raises loudly, it does not silently win or merge;
  * records are appended as JSONL and never edited or reordered;
  * every record binds enough to reproduce the decision: source snapshot hash,
    instrument-registry identity, runtime, code revision, the prior-position
    reference used for turnover, the rf lock, and the integrity-gate result.

A ledger record CONTAINS the position vector, because reproducibility requires it.
It is therefore protected material: sealed §T.3 says positions are outcomes by
another name, so the ledger file is read by machinery, never displayed to an
operator. `ca_integrity` is the only operator-facing view and it emits booleans
and counts only.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
from datetime import datetime, timezone

from . import ca_contract as K
from . import ca_store


class LedgerRewriteRefused(Exception):
    """Raised on any attempt to rewrite or duplicate an accepted decision record."""


class PositionLedger:
    def __init__(self, path: str):
        self.path = path

    # -- reading (machine-only) -------------------------------------------- #
    def _rows(self) -> list:
        full = os.path.join(K.REPO, self.path)
        if not os.path.exists(full):
            return []
        out = []
        with io.open(full, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    out.append(json.loads(line))
        return out

    def holding_months(self) -> set:
        return {r["holding_month"] for r in self._rows()}

    def count(self) -> int:
        return len(self._rows())

    def get(self, holding_month: str):
        for r in self._rows():
            if r["holding_month"] == holding_month:
                return r
        return None

    def last_accepted(self):
        rows = self._rows()
        return rows[-1] if rows else None

    # -- writing ------------------------------------------------------------ #
    def append(self, *, holding_month: str, decision: dict, snapshot_row: dict,
               registry_identity: dict, rf_lock: dict, integrity: dict,
               prior_position_ref: str | None, prior_position_kind: str,
               turnover_value, decision_timestamp_utc: str | None = None) -> dict:
        """Write ONE decision record. A duplicate holding month fails loudly."""
        if holding_month in self.holding_months():
            raise LedgerRewriteRefused(
                "REFUSED: a decision record for holding month %s already exists. "
                "The position ledger is write-once (§I.1); records are never "
                "rewritten, merged or superseded." % holding_month)

        rec = {
            "schema": "CA_POSITION_LEDGER_V1",
            "holding_month": holding_month,
            "decision_month_end": decision["decision_month_end"],
            "decision_timestamp_utc": decision_timestamp_utc or datetime.now(timezone.utc).isoformat(timespec="seconds"),
            # reproducibility bindings
            "source_snapshot_id": snapshot_row["snapshot_id"],
            "source_snapshot_sha256": snapshot_row["sha256"],
            "instrument_registry": registry_identity,
            "runtime": K.current_runtime(),
            "runtime_pinned_match": K.runtime_matches(),
            "code_revision": K.build_identity()["code_revision"],
            "sealed_prereg_sha256": K.SEALED_PREREG_SHA256,
            # the canonical decision
            "weights": decision["weights"],
            "gross": decision["gross"],
            "net": decision["net"],
            "leverage": decision["leverage"],
            "n_available": decision["n_available"],
            "cap_binds": decision["cap_binds"],
            # turnover lineage (§F.1 step 2)
            "prior_position_ref": prior_position_ref,
            "prior_position_kind": prior_position_kind,   # PRE_START_STATE_INPUT | LEDGER
            "turnover": None if turnover_value != turnover_value else float(turnover_value),
            # FM-1 rate, locked WITH the position (OD-6); the primary does not use it
            "rf_lock": rf_lock,
            # gate result
            "integrity": integrity,
        }
        rec["record_sha256"] = hashlib.sha256(
            json.dumps(rec, sort_keys=True).encode("utf-8")).hexdigest()

        full = os.path.join(K.REPO, self.path)
        ca_store.assert_not_frozen(self.path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with io.open(full, "a", encoding="utf-8", newline="") as fh:
            fh.write(json.dumps(rec, sort_keys=True) + "\n")
        return rec

    # -- operator-safe summary (NO position data) --------------------------- #
    def public_summary(self) -> dict:
        """Counts and booleans only. Never a weight, never a return."""
        rows = self._rows()
        return {
            "records": len(rows),
            "holding_months_locked": sorted(r["holding_month"] for r in rows),
            "all_records_have_snapshot_binding": all(r.get("source_snapshot_sha256") for r in rows),
            "all_records_runtime_pinned": all(r.get("runtime_pinned_match") for r in rows),
            "rf_missing_months": [r["holding_month"] for r in rows if r["rf_lock"].get("rf_missing")],
        }
