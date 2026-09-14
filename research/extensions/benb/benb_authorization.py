"""CTA-EDGE-02-BENB — the hard production-run guard.

NOT a new mechanism. It reuses the repository's existing one: the append-only Owner
ledger `ops/EXECUTION_AUTHORIZATIONS.md`, read from COMMITTED git state, with the same
fenced-``json`` record shape and lifecycle events that `x01_authorization.py` defines,
`vrp_reveal.py` reads and `ta_authorization.py` scoped for the previous lineage. Only
the lineage scope differs (`BENB-AUTH` ids).

Two inherited asymmetries make it safe:

* **GRANTING requires committed state.** A grant is read only from the committed blob,
  so nobody authorises a real run by editing a file in the worktree.
* **BLOCKING does not.** Any doubt - unreadable ledger, missing ledger, no git, more
  than one live grant - refuses. Fail-closed is not symmetric.

At S2 no CTA-EDGE-02-BENB grant exists, so `require_run_authorization(REAL, ...)`
raises before any historical byte is opened. `benb_tests.py` proves it.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
from typing import Any, Dict, List, Optional

from benb_contract import LINEAGE

LEDGER_RELPATH = "ops/EXECUTION_AUTHORIZATIONS.md"
AUTH_ID_PREFIX = "BENB-AUTH"

SYNTHETIC = "SYNTHETIC"
REAL = "REAL"

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "..", ".."))


class RunNotAuthorized(RuntimeError):
    """Raised INSTEAD of reading any real price or NAV value."""


def read_committed(relpath: str, rev: str = "HEAD") -> Optional[str]:
    try:
        out = subprocess.run(["git", "show", f"{rev}:{relpath}"], cwd=REPO,
                             capture_output=True, check=False)
    except OSError:
        return None
    if out.returncode != 0:
        return None
    return out.stdout.decode("utf-8", "replace")


def _fenced_json_blocks(text: str) -> List[Dict[str, Any]]:
    blocks = []
    for m in re.finditer(r"```json\s*\n(.*?)\n```", text, re.S):
        try:
            blocks.append(json.loads(m.group(1)))
        except ValueError:
            # An unparseable record makes the ledger's state UNKNOWN, and unknown is a
            # refusal, not an absence of grants.
            blocks.append({"record_type": "UNPARSEABLE"})
    return blocks


def benb_authorization_records(rev: str = "HEAD") -> List[Dict[str, Any]]:
    text = read_committed(LEDGER_RELPATH, rev)
    if text is None:
        return [{"record_type": "UNPARSEABLE"}]
    return [r for r in _fenced_json_blocks(text)
            if r.get("record_type") == "UNPARSEABLE"
            or str(r.get("authorization_id", "")).startswith(AUTH_ID_PREFIX)
            or str(r.get("lineage", "")) == LINEAGE]


def active_execution_authorization(kind: str = "EXECUTION",
                                   rev: str = "HEAD") -> Optional[Dict[str, Any]]:
    """The single-use grant for `kind`, if exactly one is committed and unconsumed."""
    records = benb_authorization_records(rev)
    if any(r.get("record_type") == "UNPARSEABLE" for r in records):
        return None
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


def require_run_authorization(data_kind: str, run_id: str = "") -> None:
    """The governed-run entry gate, called BEFORE any real price or NAV byte is read."""
    if data_kind == SYNTHETIC:
        return
    if data_kind != REAL:
        raise RunNotAuthorized(f"unknown data_kind {data_kind!r}")
    grant = active_execution_authorization("EXECUTION")
    if grant is None:
        raise RunNotAuthorized(
            f"REAL run refused: no single-use Owner EXECUTION authorization for "
            f"{LINEAGE} is present in committed state ({LEDGER_RELPATH}). "
            f"A seal is not authorization to execute.")
    binding = grant.get("binding", {})
    if binding.get("lineage") not in (None, LINEAGE):
        raise RunNotAuthorized(
            f"REAL run refused: grant {grant.get('authorization_id')} is scoped to "
            f"{binding.get('lineage')!r}, not {LINEAGE}")
    if run_id and binding.get("run_id") != run_id:
        raise RunNotAuthorized("REAL run refused: run_id does not match the grant")


def authorization_status() -> Dict[str, Any]:
    grant = active_execution_authorization("EXECUTION")
    return {
        "lineage": LINEAGE,
        "ledger": LEDGER_RELPATH,
        "active_execution_authorizations": 0 if grant is None else 1,
        "authorization_id": None if grant is None else grant.get("authorization_id"),
        "real_run_authorized": grant is not None,
    }
