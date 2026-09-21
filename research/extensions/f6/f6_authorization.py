# -*- coding: utf-8 -*-
"""CTA-EDGE-05 / F6 — the hard production-run guard.

**NOT a new mechanism.** It reuses the repository's existing one: the append-only
Owner ledger `ops/EXECUTION_AUTHORIZATIONS.md`, read from COMMITTED git state,
with the same fenced-``json`` record shape and lifecycle events that
`x01_authorization.py` defines and `benb_authorization.py` scoped for the
previous lineage. Only the lineage scope differs (`F6-AUTH` ids).

Two inherited asymmetries make it safe:

* **GRANTING requires committed state.** A grant is read only from the committed
  blob, so nobody authorises a real run by editing a file in the worktree.
* **BLOCKING does not.** Any doubt — unreadable ledger, missing ledger, no git,
  more than one live grant — refuses. Fail-closed is not symmetric.

At S2 **no CTA-EDGE-05 / F6 grant exists**, so `require_run_authorization(REAL)`
raises before any historical price byte is opened. `f6_tests.py` proves that
rather than promising it.

```
A SEAL IS NOT AUTHORIZATION TO EXECUTE.
S2_BUILD_AUTHORIZED = YES does NOT imply S3_RUN_AUTHORIZED.
```

This module deliberately contains **no** way to mint a grant. Creating the future
S3 authorization is an Owner action against the committed ledger, not a function
call, and no test fixture may stand in for one: `SYNTHETIC` is a separate
`data_kind`, never a forged `REAL` grant.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
from typing import Any, Dict, List, Optional

from f6_contract import LINEAGE, LINEAGE_SHORT, REPO

LEDGER_RELPATH = "ops/EXECUTION_AUTHORIZATIONS.md"
AUTH_ID_PREFIX = "F6-AUTH"

#: the two legal data kinds. There is no third, and no "dry run on real data".
SYNTHETIC = "SYNTHETIC"
REAL = "REAL"


class RunNotAuthorized(RuntimeError):
    """Raised INSTEAD of reading any real price value."""


def read_committed(relpath: str, rev: str = "HEAD") -> Optional[str]:
    """The committed blob, or None. None is a refusal, never an empty ledger."""
    try:
        out = subprocess.run(["git", "show", "%s:%s" % (rev, relpath)], cwd=REPO,
                             capture_output=True, check=False)
    except OSError:
        return None
    if out.returncode != 0:
        return None
    return out.stdout.decode("utf-8", "replace")


def _fenced_json_blocks(text: str) -> List[Dict[str, Any]]:
    blocks: List[Dict[str, Any]] = []
    for m in re.finditer(r"```json\s*\n(.*?)\n```", text, re.S):
        try:
            blocks.append(json.loads(m.group(1)))
        except ValueError:
            # An unparseable record makes the ledger's state UNKNOWN, and unknown
            # is a refusal, not an absence of grants.
            blocks.append({"record_type": "UNPARSEABLE"})
    return blocks


def f6_authorization_records(rev: str = "HEAD") -> List[Dict[str, Any]]:
    text = read_committed(LEDGER_RELPATH, rev)
    if text is None:
        return [{"record_type": "UNPARSEABLE"}]
    out = []
    for r in _fenced_json_blocks(text):
        if r.get("record_type") == "UNPARSEABLE":
            out.append(r)
            continue
        aid = str(r.get("authorization_id", ""))
        lin = str(r.get("lineage", ""))
        if aid.startswith(AUTH_ID_PREFIX) or lin in (LINEAGE, LINEAGE_SHORT):
            out.append(r)
    return out


def active_execution_authorization(kind: str = "EXECUTION",
                                   rev: str = "HEAD") -> Optional[Dict[str, Any]]:
    """The single-use grant for `kind`, if EXACTLY ONE is committed and live."""
    records = f6_authorization_records(rev)
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
    if len(grants) != 1:          # zero is a refusal; two or more is also a refusal
        return None
    return next(iter(grants.values()))


def require_run_authorization(data_kind: str, run_id: str = "") -> None:
    """The governed-run entry gate, called BEFORE any real price byte is read.

    Fail-closed: every path that is not an explicit, committed, single-use,
    correctly-scoped Owner grant raises.
    """
    if data_kind == SYNTHETIC:
        return
    if data_kind != REAL:
        raise RunNotAuthorized("unknown data_kind %r" % (data_kind,))
    grant = active_execution_authorization("EXECUTION")
    if grant is None:
        raise RunNotAuthorized(
            "REAL run refused: no single-use Owner EXECUTION authorization for "
            "%s is present in committed state (%s). A seal is not authorization "
            "to execute." % (LINEAGE, LEDGER_RELPATH))
    binding = grant.get("binding", {}) or {}
    if binding.get("lineage") not in (None, LINEAGE, LINEAGE_SHORT):
        raise RunNotAuthorized(
            "REAL run refused: grant %s is scoped to %r, not %s"
            % (grant.get("authorization_id"), binding.get("lineage"), LINEAGE))
    if binding.get("seal_id") not in (None, "CTA-EDGE-05-F6-S1-2026-09-21"):
        raise RunNotAuthorized(
            "REAL run refused: grant is bound to a different seal_id")
    if run_id and binding.get("run_id") != run_id:
        raise RunNotAuthorized("REAL run refused: run_id does not match the grant")


def authorization_status() -> Dict[str, Any]:
    grant = active_execution_authorization("EXECUTION")
    return {
        "lineage": LINEAGE,
        "ledger": LEDGER_RELPATH,
        "auth_id_prefix": AUTH_ID_PREFIX,
        "active_execution_authorizations": 0 if grant is None else 1,
        "authorization_id": None if grant is None else grant.get("authorization_id"),
        "real_run_authorized": grant is not None,
        "note": "A seal is not authorization to execute. S3 authorization is a "
                "separate committed Owner record.",
    }
