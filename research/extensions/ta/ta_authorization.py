"""CTA-EDGE-01-TA — the hard production-run guard.

This is NOT a new authorization mechanism. It reuses the repository's existing one:
the append-only Owner ledger `ops/EXECUTION_AUTHORIZATIONS.md`, read from COMMITTED
git state, with the same fenced-``json`` record shape and the same lifecycle events
that `research/extensions/x01/x01_authorization.py` defines and `vrp_reveal.py` reads.
Only the lineage scope differs.

The two asymmetries that make it safe, inherited unchanged:

* **GRANTING requires committed state.** A grant is read only from the committed blob,
  so nobody authorizes a real run by editing a file in the worktree.
* **BLOCKING does not.** Any doubt - unreadable ledger, missing ledger, no git, more
  than one live grant - refuses. Fail-closed is not symmetric.

At S2 no CTA-EDGE-01-TA grant exists, so `require_run_authorization(REAL, ...)`
raises. That is the intended state and `ta_tests.py` asserts it.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
from typing import Any, Dict, List, Optional

from ta_contract import LINEAGE

LEDGER_RELPATH = "ops/EXECUTION_AUTHORIZATIONS.md"
AUTH_ID_PREFIX = "TA-AUTH"

SYNTHETIC = "SYNTHETIC"
REAL = "REAL"

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "..", ".."))


class RunNotAuthorized(RuntimeError):
    """Raised INSTEAD of reading any real outcome data."""


# --------------------------------------------------------------------------- #
# committed-state ledger reading                                               #
# --------------------------------------------------------------------------- #


def read_committed(relpath: str, rev: str = "HEAD") -> Optional[str]:
    """The file's content in committed git state, or None if it cannot be read."""
    try:
        out = subprocess.run(["git", "show", f"{rev}:{relpath}"], cwd=REPO,
                             capture_output=True, check=False)
    except OSError:
        return None
    if out.returncode != 0:
        return None
    return out.stdout.decode("utf-8", "replace")


def _fenced_json_blocks(text: str) -> List[Dict[str, Any]]:
    """Every ```json fenced block, parsed. Only json fences are records."""
    blocks = []
    for m in re.finditer(r"```json\s*\n(.*?)\n```", text, re.S):
        try:
            blocks.append(json.loads(m.group(1)))
        except ValueError:
            # An unparseable record makes the ledger's state unknown. Unknown is
            # not "no grant" - it is a refusal, signalled by a poison marker.
            blocks.append({"record_type": "UNPARSEABLE"})
    return blocks


def ta_authorization_records(rev: str = "HEAD") -> List[Dict[str, Any]]:
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
    records = ta_authorization_records(rev)
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


# --------------------------------------------------------------------------- #
# the gate                                                                     #
# --------------------------------------------------------------------------- #


def require_run_authorization(data_kind: str, run_id: str = "") -> None:
    """The governed-run entry gate, called BEFORE any real price byte is read.

    SYNTHETIC always passes - that is the S2 path and it touches no real data. REAL
    needs a single-use Owner EXECUTION grant for this lineage present in COMMITTED
    state and not yet consumed.
    """
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
    """Read-only status, for the S2 report. Touches no outcome and no ledger write."""
    grant = active_execution_authorization("EXECUTION")
    return {
        "lineage": LINEAGE,
        "ledger": LEDGER_RELPATH,
        "active_execution_authorizations": 0 if grant is None else 1,
        "authorization_id": None if grant is None else grant.get("authorization_id"),
        "real_run_authorized": grant is not None,
    }
