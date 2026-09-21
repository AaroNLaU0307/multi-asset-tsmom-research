# -*- coding: utf-8 -*-
"""TSMOM-VRP-01 - module M: the reveal-control layer.

Three states are kept strictly apart (sealed section S and acceptance item 21):

    COMPUTE   a real Stage-A or Stage-B outcome may be GENERATED only when the
              acceptance log shows every acceptance-contract item PASS at the current
              commit AND a single-use Owner EXECUTION authorisation for this lineage is
              present in COMMITTED state.
    STORE     what is generated is written to the VRP family's own protected store as
              GENERATED_NOT_SEEN. It is hashed. It is never printed, logged, returned
              into a summary JSON, or rendered by a notebook.
    REVEAL    a value leaves the store only under a separate single-use Owner REVEAL
              authorisation, also read from committed state.

`ProtectedResult` makes the store/reveal boundary structural rather than a convention:
its repr, str, format and iteration all refuse, and `.value` raises until `.reveal()`
has been given a valid reveal grant. A debug `print(result)` therefore cannot leak a
real outcome.

The VRP protected store is a SIBLING of the C-A mechanism (sealed section P). It is
never the C-A store, never the C-A key, and this module holds no C-A path at all.

DURING S2 NOTHING HERE IS SATISFIED, BY DESIGN: no execution authorisation exists, so
every attempt to generate a real outcome raises `RunNotAuthorized`.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import re
import subprocess
from typing import Any, Dict, List, Optional

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

LINEAGE = "TSMOM-VRP-01"
OPS_AUTHORIZATIONS = "ops/EXECUTION_AUTHORIZATIONS.md"
ACCEPTANCE_LOG = "research/extensions/vrp/s2/VRP_S2_ACCEPTANCE_LOG.json"
PROTECTED_STORE = os.path.join(REPO, "data", "vrp_protected")   # git-ignored; VRP's own

SYNTHETIC = "SYNTHETIC"
REAL = "REAL"


class RunNotAuthorized(RuntimeError):
    """A real, outcome-bearing run was attempted without the sealed preconditions."""


class RevealNotAuthorized(RuntimeError):
    """A generated value was requested without a single-use Owner reveal grant."""


# --------------------------------------------------------------------------- #
# committed-state readers
# --------------------------------------------------------------------------- #
def read_committed(path: str) -> Optional[str]:
    """Bytes as COMMITTED at HEAD. A working-tree file is never authority (D2)."""
    try:
        out = subprocess.run(["git", "show", "HEAD:%s" % path], cwd=REPO,
                             capture_output=True, check=False)
    except OSError:
        return None
    if out.returncode != 0:
        return None
    return out.stdout.decode("utf-8", "replace")


def _json_blocks(text: str) -> List[Dict[str, Any]]:
    blocks: List[Dict[str, Any]] = []
    for m in re.finditer(r"```(?:json|text)\s*\n(.*?)```", text, re.S):
        body = m.group(1).strip()
        if not body.startswith("{"):
            continue
        try:
            blocks.append(json.loads(body))
        except ValueError:
            continue          # a schema TEMPLATE with <placeholders>, not a record
    return blocks


def vrp_authorization_records() -> List[Dict[str, Any]]:
    """Every committed authorization/lifecycle record bound to THIS lineage."""
    text = read_committed(OPS_AUTHORIZATIONS)
    if text is None:
        return []
    out = []
    for rec in _json_blocks(text):
        binding = rec.get("binding") or {}
        if binding.get("research_id") == LINEAGE or str(
                rec.get("authorization_id", "")).startswith("VRP-AUTH"):
            out.append(rec)
    return out


def active_execution_authorization(kind: str = "EXECUTION") -> Optional[Dict[str, Any]]:
    """The single-use grant for `kind`, if one is committed and not yet consumed."""
    records = vrp_authorization_records()
    grants = {r["authorization_id"]: r for r in records
              if r.get("record_type") == "AUTHORIZATION"
              and r.get("status") == "AUTHORIZED"
              and str(r.get("grant_kind", "EXECUTION")).upper() == kind.upper()}
    for r in records:
        if r.get("record_type") == "LIFECYCLE" and r.get("event") in (
                "CONSUMED", "CONSUMED_OR_INDETERMINATE", "REVOKED"):
            grants.pop(r.get("authorization_id"), None)
    if len(grants) != 1:
        return None
    return next(iter(grants.values()))


def acceptance_log_all_pass() -> Dict[str, Any]:
    """Acceptance item 21: the tracked acceptance log must show every item PASS at the
    CURRENT commit."""
    text = read_committed(ACCEPTANCE_LOG)
    if text is None:
        return {"ok": False, "reason": "acceptance log is not committed"}
    try:
        log = json.loads(text)
    except ValueError:
        return {"ok": False, "reason": "acceptance log is not valid JSON"}
    items = log.get("items") or []
    if not items:
        return {"ok": False, "reason": "acceptance log contains no items"}
    failing = [it.get("item") for it in items if it.get("result") != "PASS"]
    head = current_commit()
    if log.get("commit") not in (head, None):
        return {"ok": False, "reason": "acceptance log was recorded at %s, HEAD is %s"
                                       % (log.get("commit"), head)}
    return {"ok": not failing, "reason": "items not PASS: %s" % failing if failing else "",
            "items": len(items)}


def current_commit() -> Optional[str]:
    try:
        out = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO,
                             capture_output=True, check=False)
    except OSError:
        return None
    return out.stdout.decode().strip() if out.returncode == 0 else None


# --------------------------------------------------------------------------- #
# the gate
# --------------------------------------------------------------------------- #
def require_run_authorization(data_kind: str, run_id: str = "",
                              stage: str = "STAGE_A") -> None:
    """The governed-run entry gate. SYNTHETIC data always passes; REAL data needs both
    sealed preconditions AND a grant whose SCOPE covers the stage being run.

    The stage check is not decorative. A grant issued for one historical Stage-A run must
    not silently open Stage B: the sealed stop rule (section O) makes Stage B a separate,
    conditional, separately authorised act. A grant carrying
    `binding.stage_b_authorized = false` refuses Stage B even while it authorises Stage A.
    Acceptance item 21 asserts the refusal.
    """
    if data_kind == SYNTHETIC:
        return
    if data_kind != REAL:
        raise RunNotAuthorized("unknown data_kind %r" % data_kind)
    acc = acceptance_log_all_pass()
    if not acc["ok"]:
        raise RunNotAuthorized(
            "REAL run refused: the acceptance contract is not fully PASS in committed "
            "state (%s)" % acc.get("reason"))
    grant = active_execution_authorization("EXECUTION")
    if grant is None:
        raise RunNotAuthorized(
            "REAL run refused: no single-use Owner EXECUTION authorisation for %s is "
            "present in committed state" % LINEAGE)
    if run_id and grant.get("binding", {}).get("run_id") != run_id:
        raise RunNotAuthorized("REAL run refused: run_id does not match the grant")
    binding = grant.get("binding", {})
    if stage.upper().startswith("STAGE_B"):
        if not binding.get("stage_b_authorized", False):
            raise RunNotAuthorized(
                "REAL Stage-B run refused: grant %s does not authorise Stage B "
                "(binding.stage_b_authorized is not true)"
                % grant.get("authorization_id"))
    elif binding.get("stage") and "STAGE_A" not in str(binding["stage"]).upper():
        raise RunNotAuthorized(
            "REAL Stage-A run refused: grant %s is scoped to %r"
            % (grant.get("authorization_id"), binding["stage"]))


# --------------------------------------------------------------------------- #
# GENERATED_NOT_SEEN
# --------------------------------------------------------------------------- #
class ProtectedResult:
    """A generated real outcome held as GENERATED_NOT_SEEN.

    Printing it, formatting it, or reading `.value` without a reveal grant all refuse.
    Only `digest` and `label` are ever safe to display.
    """

    __slots__ = ("_payload", "_label", "_digest", "_revealed")

    def __init__(self, payload: Any, label: str):
        self._payload = payload
        self._label = label
        self._digest = hashlib.sha256(
            json.dumps(payload, sort_keys=True, default=str).encode("utf-8")).hexdigest()
        self._revealed = False

    @property
    def label(self) -> str:
        return self._label

    @property
    def digest(self) -> str:
        return self._digest

    @property
    def revealed(self) -> bool:
        return self._revealed

    def __repr__(self) -> str:
        return "<ProtectedResult %s GENERATED_NOT_SEEN sha256=%s>" % (
            self._label, self._digest[:16])

    __str__ = __repr__

    def __format__(self, spec: str) -> str:
        return self.__repr__()

    def __iter__(self):
        raise RevealNotAuthorized("%s is GENERATED_NOT_SEEN" % self._label)

    def __len__(self):
        raise RevealNotAuthorized("%s is GENERATED_NOT_SEEN" % self._label)

    @property
    def value(self) -> Any:
        if not self._revealed:
            raise RevealNotAuthorized(
                "%s is GENERATED_NOT_SEEN; a single-use Owner REVEAL authorisation "
                "committed in %s is required" % (self._label, OPS_AUTHORIZATIONS))
        return self._payload

    def reveal(self) -> Any:
        grant = active_execution_authorization("REVEAL")
        if grant is None:
            raise RevealNotAuthorized(
                "no single-use Owner REVEAL authorisation for %s is present in "
                "committed state" % LINEAGE)
        self._revealed = True
        return self._payload


def store_generated_not_seen(payload: Any, label: str) -> Dict[str, str]:
    """Write a generated outcome into the VRP family's OWN protected store.

    Returns only the metadata (path, digest, timestamp) - never the payload.
    """
    os.makedirs(PROTECTED_STORE, exist_ok=True)
    result = ProtectedResult(payload, label)
    stamp = _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    name = "%s_%s_%s.json" % (LINEAGE, re.sub(r"[^A-Za-z0-9_.-]", "_", label), stamp)
    path = os.path.join(PROTECTED_STORE, name)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"label": label, "classification": "GENERATED_NOT_SEEN",
                   "sha256": result.digest, "generated_utc": stamp,
                   "payload": payload}, fh, indent=2, sort_keys=True, default=str)
    return {"path": os.path.relpath(path, REPO).replace("\\", "/"),
            "sha256": result.digest, "classification": "GENERATED_NOT_SEEN",
            "generated_utc": stamp}
