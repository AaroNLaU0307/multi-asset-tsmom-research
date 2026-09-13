# -*- coding: utf-8 -*-
"""GENERATED-NOT-SEEN protected outcome store and the reveal gate (sealed §M, §T, §V).

The sealed architecture permits outcomes to be GENERATED and stored while forbidding
any human or agent from SEEING them before the single authorized terminal reveal
(sealed §T.1's GENERATED_NOT_SEEN classification, as used for X01-RUN-0001).

The boundary is enforced technically, not just procedurally: payloads are written
OUTSIDE the repository and ENCRYPTED AT REST by `ca_blind`, so `cat`, a repo grep,
an editor or a stray `json.load` yields ciphertext. See `ca_blind` for the
mechanism and for the honest statement of its limit (Aaron owns the key, so this
is not secrecy against the Owner — it removes the dependence on voluntary API
discipline).

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

from . import ca_blind
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

    def __init__(self, store_dir=None, index_path=None):
        # The protected store lives OUTSIDE the repository working tree. A path
        # inside the repo is refused, so a future caller cannot quietly move
        # protected payloads back under git / grep / editor reach.
        self.store_dir = ca_blind.ensure_store(store_dir)
        self.index_path = ca_blind.assert_outside_repo(
            index_path or os.path.join(self.store_dir, "protected_index.jsonl"),
            "protected index")

    def _index(self) -> list:
        full = self.index_path
        if not os.path.exists(full):
            return []
        out = []
        with io.open(full, encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    out.append(json.loads(line))
        return out

    def store(self, outcome_id: str, payload: dict) -> dict:
        """Generate-and-store. Returns identity ONLY — never the payload.

        The payload is ENCRYPTED AT REST and written outside the repository, so
        `cat`, an editor, a repo grep or a stray `json.load` yields ciphertext.
        """
        full = os.path.join(self.store_dir, "%s.sealed.json" % outcome_id)
        if os.path.exists(full):
            raise ca_store.SnapshotOverwriteRefused(
                "REFUSED: protected outcome %s already exists; the store is write-once"
                % outcome_id)
        plain = (json.dumps(payload, sort_keys=True) + "\n").encode("utf-8")
        envelope = ca_blind.seal_envelope(plain)
        data = (json.dumps(envelope, sort_keys=True, indent=2) + "\n").encode("utf-8")
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with io.open(full, "wb") as fh:
            fh.write(data)
        row = {
            "outcome_id": outcome_id,
            "path": full,
            "sha256": hashlib.sha256(data).hexdigest(),                 # of the ciphertext file
            "payload_plaintext_sha256": envelope["plaintext_sha256"],   # reproducible identity
            "byte_size": len(data),
            "classification": "GENERATED_NOT_SEEN",
            "encrypted_at_rest": True,
            "stored_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }
        idx = self.index_path
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
            "payload_hashes": {r["outcome_id"]: r.get("payload_plaintext_sha256") for r in rows},
            "all_encrypted_at_rest": all(r.get("encrypted_at_rest") for r in rows),
            "store_outside_repo": not ca_blind._inside_repo(self.store_dir),
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
        with io.open(row["path"], encoding="utf-8") as fh:
            envelope = json.load(fh)
        cap = ca_blind.MachineCapability("TERMINAL_REVEAL")
        payload = json.loads(ca_blind.open_envelope(envelope, cap))
        authorization.consumed = True
        return payload


def _assert_no_forbidden_key(view: dict) -> None:
    leaked = [k for k in view
              if any(f in str(k).lower() for f in FORBIDDEN_IN_OPERATOR_VIEW)]
    if leaked:
        raise RevealNotAuthorized(
            "BLINDNESS BREACH BLOCKED: operator view would expose %s (§T.3)" % leaked)
