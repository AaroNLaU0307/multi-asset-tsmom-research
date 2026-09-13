# -*- coding: utf-8 -*-
"""GENERATED-NOT-SEEN protected outcome store and the reveal gate (sealed §M, §T, §V).

The sealed architecture permits outcomes to be GENERATED and stored while forbidding
any human or agent from SEEING them before the single authorized terminal reveal.
This module is the mechanism, and it is procedural rather than cryptographic —
exactly what sealed §T.1 says the contract relies on:

    "the pipeline writes the locked position vectors and the checkpoint return
     series to disk, they are hashed and registered, and NO SESSION READS THEM —
     precisely the GENERATED_NOT_SEEN classification already used for X01-RUN-0001."

Enforcement here:
  * `store()` writes a payload and returns ONLY its hash and size — never content;
  * `describe()` is the operator view: booleans and counts, never a value;
  * `reveal()` REQUIRES a `RevealAuthorization` whose four sealed conditions are
    checked. No authorization exists by default and none is created by this module;
  * there is no other accessor. `read_payload` is private and raises without an
    authorization object.

Sealed §M: POSITIVE_REVEAL_COUNT = 1. A consumed authorization can never authorize
a second access.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
from datetime import datetime, timezone

from . import ca_contract as K
from . import ca_store


class RevealNotAuthorized(Exception):
    """Raised on any attempt to read protected outcome content without authorization."""


class RevealAuthorizationInvalid(Exception):
    """Raised when a presented authorization fails a sealed condition."""


FORBIDDEN_IN_OPERATOR_VIEW = (
    "cumulative_return", "sharpe", "drawdown", "win_rate", "sleeve_performance",
    "fm1_performance", "crisis_response", "monthly_return", "pnl", "equity_curve",
    "weights", "position", "positions", "net_return", "gross_return",
)


class RevealAuthorization:
    """An Owner reveal authorization. Construction alone is NOT authorization —
    `validate()` enforces the sealed §V conditions, and nothing in this package
    ever constructs one on its own initiative."""

    def __init__(self, *, authorization_id: str, owner: str, granted_utc: str,
                 scope: str, n_scored_at_grant: int, declared_before_access: bool):
        self.authorization_id = authorization_id
        self.owner = owner
        self.granted_utc = granted_utc
        self.scope = scope
        self.n_scored_at_grant = n_scored_at_grant
        self.declared_before_access = declared_before_access
        self.consumed = False

    def validate(self, *, n_scored_now: int) -> None:
        if self.owner != "Aaron":
            raise RevealAuthorizationInvalid("only the Owner may authorize a reveal (§V step 4)")
        if not self.declared_before_access:
            raise RevealAuthorizationInvalid(
                "the access scope must be declared BEFORE authorization (§V step 3); "
                "authorization must precede protected outcome access")
        if n_scored_now < K.N_SCORED_TERMINAL:
            raise RevealAuthorizationInvalid(
                "the single terminal reveal occurs at N_scored = %d; N_scored is %d (§M)"
                % (K.N_SCORED_TERMINAL, n_scored_now))
        if self.consumed:
            raise RevealAuthorizationInvalid(
                "this authorization is CONSUMED; POSITIVE_REVEAL_COUNT = 1 (§M)")


class ProtectedOutcomeStore:
    """Outcomes may be produced and stored. They may not be seen."""

    def __init__(self, store_dir: str, index_path: str):
        self.store_dir = store_dir
        self.index_path = index_path

    def _index(self) -> list:
        full = os.path.join(K.REPO, self.index_path)
        if not os.path.exists(full):
            return []
        out = []
        with io.open(full, encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    out.append(json.loads(line))
        return out

    def store(self, outcome_id: str, payload: dict) -> dict:
        """Generate-and-store. Returns identity ONLY — never the payload."""
        rel = os.path.join(self.store_dir, "%s.json" % outcome_id).replace("\\", "/")
        data = (json.dumps(payload, sort_keys=True, indent=2) + "\n").encode("utf-8")
        ca_store.safe_write_bytes(rel, data)          # write-once, refuses the frozen panel
        row = {
            "outcome_id": outcome_id,
            "path": rel,
            "sha256": hashlib.sha256(data).hexdigest(),
            "byte_size": len(data),
            "classification": "GENERATED_NOT_SEEN",
            "stored_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }
        idx = os.path.join(K.REPO, self.index_path)
        os.makedirs(os.path.dirname(idx), exist_ok=True)
        with io.open(idx, "a", encoding="utf-8", newline="") as fh:
            fh.write(json.dumps(row, sort_keys=True) + "\n")
        return row

    def describe(self) -> dict:
        """THE OPERATOR VIEW. Booleans, counts and hashes only — no content, ever."""
        rows = self._index()
        view = {
            "protected_outcomes_stored": len(rows),
            "outcome_ids": [r["outcome_id"] for r in rows],
            "all_generated_not_seen": all(r["classification"] == "GENERATED_NOT_SEEN" for r in rows),
            "payload_hashes": {r["outcome_id"]: r["sha256"] for r in rows},
            "reveal_authorization_present": False,
            "content_visible": False,
        }
        _assert_no_forbidden_key(view)
        return view

    def reveal(self, outcome_id: str, authorization=None, *, n_scored_now: int = 0) -> dict:
        """The ONLY path to content. Refuses without a valid Owner authorization."""
        if authorization is None:
            raise RevealNotAuthorized(
                "REFUSED: protected outcome %s is GENERATED_NOT_SEEN. Reveal requires an "
                "Owner authorization declared before access (§V). None is present, and "
                "this package never creates one." % outcome_id)
        if not isinstance(authorization, RevealAuthorization):
            raise RevealNotAuthorized("REFUSED: not a RevealAuthorization")
        authorization.validate(n_scored_now=n_scored_now)
        row = next((r for r in self._index() if r["outcome_id"] == outcome_id), None)
        if row is None:
            raise KeyError(outcome_id)
        with io.open(os.path.join(K.REPO, row["path"]), encoding="utf-8") as fh:
            payload = json.load(fh)
        authorization.consumed = True
        return payload


def _assert_no_forbidden_key(view: dict) -> None:
    leaked = [k for k in view
              if any(f in str(k).lower() for f in FORBIDDEN_IN_OPERATOR_VIEW)]
    if leaked:
        raise RevealNotAuthorized(
            "BLINDNESS BREACH BLOCKED: operator view would expose %s (§T.3)" % leaked)
