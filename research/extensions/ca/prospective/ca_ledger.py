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

A ledger record must preserve the position vector, because reproducibility requires
it -- but sealed §T.3 says positions are outcomes by another name. The record is
therefore SPLIT: the position vector and its raw gross/net/leverage values are
ENCRYPTED into a `protected_position` envelope (`ca_blind`), while the clear half
carries identity, reproducibility bindings and §T.2 invariant BOOLEANS. The
plaintext sha256 is recorded in the clear inside the envelope, so record identity
stays verifiable without decrypting.

Reading the vector requires `machine_read_position()` with a `MachineCapability`.
`public_summary()` and `ca_integrity` are the operator-facing views and emit
booleans, counts and hashes only.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
from datetime import datetime, timezone

from . import ca_blind
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

        # SPLIT: the sensitive half (the position vector and its raw gross/net/
        # leverage values) is sealed; the clear half carries identity, bindings and
        # §T.2 invariant BOOLEANS so operator monitoring stays rich without ever
        # exposing a vector. Sealed §T.3: positions are outcomes by another name.
        protected_plain = json.dumps({
            "weights": decision["weights"],
            "gross": decision["gross"],
            "net": decision["net"],
            "leverage": decision["leverage"],
        }, sort_keys=True).encode("utf-8")
        sealed_block = ca_blind.seal_envelope(protected_plain)
        g, w = decision["gross"], [v for v in decision["weights"].values() if v is not None]

        rec = {
            "schema": "CA_POSITION_LEDGER_V2_BLIND",
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
            # the canonical decision — SEALED. Reproducibility is preserved: the
            # plaintext sha256 is recorded in the clear inside the envelope.
            "protected_position": sealed_block,
            # §T.2 invariants, as booleans and counts only
            "gross_within_cap": (g is None) or (g <= K.MAX_GROSS_LEVERAGE + 1e-9),
            "asset_weight_within_cap": all(abs(x) <= K.MAX_GROSS_LEVERAGE + 1e-9 for x in w),
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

    # -- the supported MACHINE path (capability-gated) ---------------------- #
    def machine_read_position(self, holding_month: str, capability) -> dict:
        """Decrypt one record's position block. Requires a MachineCapability.

        This is the path the pipeline uses for the §F.1 turnover prior position and
        the §T.2 locked-vs-recomputed diagnostic. It is never called by any
        operator-facing report.
        """
        rec = self.get(holding_month)
        if rec is None:
            raise KeyError(holding_month)
        return json.loads(ca_blind.open_envelope(rec["protected_position"], capability))

    def position_identity(self, holding_month: str) -> dict:
        """Reproducible identity WITHOUT decrypting — operator-safe."""
        rec = self.get(holding_month)
        if rec is None:
            raise KeyError(holding_month)
        env = rec["protected_position"]
        return {"holding_month": holding_month,
                "position_plaintext_sha256": env["plaintext_sha256"],
                "record_sha256": rec["record_sha256"]}

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
            "all_positions_sealed": all("protected_position" in r and "weights" not in r for r in rows),
            "position_identities": {r["holding_month"]: r["protected_position"]["plaintext_sha256"]
                                    for r in rows},
        }
