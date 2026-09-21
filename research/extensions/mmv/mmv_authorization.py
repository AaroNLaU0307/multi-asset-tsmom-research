"""CTA-EDGE-04-MMV — execution-authorization reader.

Scoped to `MMV-AUTH` ids and the `CTA-EDGE-04-MMV` lineage. It reuses the X01
asymmetries unchanged:

    GRANTING REQUIRES COMMITTED STATE.  A grant that exists only in the working
    tree is INVALID, not merely suspect. Writing yourself a permission slip and
    reading it back in the same uncommitted breath is not authorization.

    BLOCKING DOES NOT.  An unreadable ledger, an unparseable record, a missing
    grant, a consumed grant, or more than one live grant all REFUSE. Every
    failure mode resolves toward "no run".

This module never grants anything by itself and never writes to the ledger.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
from typing import Any, Dict, List, Optional

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

LEDGER_RELPATH = "ops/EXECUTION_AUTHORIZATIONS.md"
LINEAGE = "CTA-EDGE-04-MMV"
ID_PREFIX = "MMV-AUTH-"
SCHEMA_NAME = "mmv-execution-authorization"

_FENCE = re.compile(r"```json\s*\n(.*?)\n```", re.S)


class RunNotAuthorized(RuntimeError):
    """The single reason this module ever stops a run."""


def read_committed(relpath: str, rev: str = "HEAD") -> Optional[str]:
    """The file as COMMITTED at ``rev``, or None. Never the working tree."""
    try:
        out = subprocess.run(["git", "show", "%s:%s" % (rev, relpath)],
                             cwd=REPO, capture_output=True, text=True)
    except OSError:
        return None
    if out.returncode != 0:
        return None
    return out.stdout


def _blocks(text: str) -> List[Dict[str, Any]]:
    found = []
    for raw in _FENCE.findall(text or ""):
        try:
            obj = json.loads(raw)
        except json.JSONDecodeError:
            continue                       # unparseable record: ignored, never guessed
        if isinstance(obj, dict):
            found.append(obj)
    return found


def read_worktree(relpath: str) -> Optional[str]:
    """The file as it sits in the WORKING TREE, or None.

    Used for BLOCKING only. A grant here would be worthless, but a CONSUMED
    record here is a reason to refuse: the asymmetry is deliberate.
    """
    path = os.path.join(REPO, relpath)
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return None


def _scoped(text: Optional[str]) -> List[Dict[str, Any]]:
    """Records belonging to this lineage.

    The authorization id prefix and the schema name identify CTA-EDGE-04-MMV on
    their own. `lineage` is checked only when the record carries it, because a
    LIFECYCLE record does not: requiring it would silently DROP consumption
    records, and a dropped consumption record is a guard that fails open.
    """
    out = []
    for obj in _blocks(text or ""):
        if not str(obj.get("authorization_id", "")).startswith(ID_PREFIX):
            continue
        if obj.get("schema", {}).get("name") != SCHEMA_NAME:
            continue
        if "lineage" in obj and obj.get("lineage") != LINEAGE:
            continue
        out.append(obj)
    return out


def mmv_records(rev: str = "HEAD") -> List[Dict[str, Any]]:
    """Records from COMMITTED state. Grants may only ever come from here."""
    return _scoped(read_committed(LEDGER_RELPATH, rev))


def consumed_ids(rev: str = "HEAD") -> set:
    """Every authorization id marked CONSUMED, from committed state UNION the
    working tree.

    Consumption BLOCKS, and blocking does not require a commit. A CONSUMED
    record that has been written but not yet committed still spends the grant:
    the run really did happen, and the commit is bookkeeping that follows it.
    Requiring the commit first would leave a window in which a completed run
    could be repeated.
    """
    out = set()
    for source in (mmv_records(rev), _scoped(read_worktree(LEDGER_RELPATH))):
        for r in source:
            if (r.get("record_type") == "LIFECYCLE"
                    and r.get("event") == "CONSUMED"):
                out.add(r.get("authorization_id"))
    return out


def active_grant(rev: str = "HEAD") -> Dict[str, Any]:
    """The one live EXECUTION grant, or raise.

    A grant is live when it is AUTHORIZED and no LIFECYCLE record has marked it
    CONSUMED. Two live grants is a refusal, not a choice between them.
    """
    records = mmv_records(rev)
    grants = [r for r in records
              if r.get("record_type") == "AUTHORIZATION"
              and r.get("grant_kind") == "EXECUTION"
              and r.get("status") == "AUTHORIZED"]
    consumed = consumed_ids(rev)
    live = [g for g in grants if g.get("authorization_id") not in consumed]

    if not grants:
        raise RunNotAuthorized(
            "no committed CTA-EDGE-04-MMV execution authorization exists in %s"
            % LEDGER_RELPATH)
    if not live:
        raise RunNotAuthorized(
            "every CTA-EDGE-04-MMV grant is CONSUMED (%s); consumption is "
            "permanent and no retry is authorized" % sorted(consumed))
    if len(live) > 1:
        raise RunNotAuthorized(
            "more than one live grant (%s); ambiguity refuses"
            % sorted(g.get("authorization_id") for g in live))
    return live[0]


def require(run_id: str, rev: str = "HEAD") -> Dict[str, Any]:
    """Authorize exactly this ``run_id``, or raise.

    The run_id is compared EXACTLY. A run that renames itself is a different
    run and this grant does not cover it.
    """
    grant = active_grant(rev)
    binding = grant.get("binding", {})
    want = binding.get("run_id")
    if want != run_id:
        raise RunNotAuthorized(
            "grant %s authorizes run_id %r, not %r"
            % (grant.get("authorization_id"), want, run_id))
    if grant.get("scope") != "ONE_SHOT_SINGLE_PNL_FREE_GATE05_RUN":
        raise RunNotAuthorized("unexpected scope %r" % grant.get("scope"))
    return grant


def status(rev: str = "HEAD") -> Dict[str, Any]:
    try:
        grant = active_grant(rev)
    except RunNotAuthorized as e:
        return {"authorized": False, "reason": str(e)}
    return {"authorized": True,
            "authorization_id": grant["authorization_id"],
            "run_id": grant["binding"]["run_id"],
            "scope": grant["scope"]}


if __name__ == "__main__":
    print(json.dumps(status(), indent=1, sort_keys=True))
