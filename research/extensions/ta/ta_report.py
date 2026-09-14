"""CTA-EDGE-01-TA — the result-artifact schema and report writer.

Component Q of the S2 build. The schema is fixed now so the future governed run has
nowhere to invent a field; at S2 it is only ever populated from SYNTHETIC fixtures and
every such artifact is stamped `SYNTHETIC_ONLY = YES`.

A real artifact can only be produced by a run that passed the authorization guard, and
`build_result()` refuses to stamp `SYNTHETIC_ONLY = NO` unless it is handed a REAL
data_kind together with a run authorization id.
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
from typing import Any, Dict, Mapping, Optional, Sequence

import ta_contract as K

SCHEMA_VERSION = "TA-RESULT-1"

#: Every field the future governed-run artifact must carry. The writer refuses to emit
#: an artifact missing any of them, so a field cannot be quietly dropped at S3.
REQUIRED_FIELDS = (
    "schema_version", "lineage", "contract_id", "synthetic_only", "data_kind",
    "generated_at_utc", "sealed_prereg_sha256", "seal_commit", "run_authorization_id",
    "data_hashes", "event_calendar_sha256", "macro_calendar_sha256",
    "macro_covariates_sha256", "primary_event_count", "primary_years",
    "mean_ac_gross_bps", "mean_ac_net_bps", "mean_ac_net_ci95",
    "calendarised_sharpe", "calendarised_sharpe_ci95", "monthly_grid",
    "loyo", "secondary_ief", "gradient_shy", "placebo_spy", "macro_qra",
    "diagnostic_triggers", "final_class", "research_status", "qualifier",
    "evidence_ceiling", "forbidden_interpretations", "descriptives",
)


def _sha(path: str) -> Optional[str]:
    try:
        return hashlib.sha256(open(path, "rb").read()).hexdigest()
    except OSError:
        return None


def build_result(*, data_kind: str, verdict, primary, loyo, secondary, gradient,
                 placebo, macro, monthly_grid: Mapping[str, Any],
                 descriptives: Mapping[str, Any] | None = None,
                 run_authorization_id: Optional[str] = None,
                 data_hashes: Mapping[str, Any] | None = None) -> Dict[str, Any]:
    """Assemble the result artifact. `primary` carries the two primary intervals."""
    synthetic = data_kind != "REAL"
    if not synthetic and not run_authorization_id:
        raise ValueError(
            "a REAL result artifact requires a run_authorization_id; refusing to "
            "stamp SYNTHETIC_ONLY = NO without one")
    doc: Dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "lineage": K.LINEAGE,
        "contract_id": K.CONTRACT_ID,
        "synthetic_only": "YES" if synthetic else "NO",
        "data_kind": data_kind,
        "generated_at_utc": _dt.datetime.now(_dt.timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"),
        "sealed_prereg_sha256": K.SEALED_PREREG_SHA256,
        "seal_commit": K.SEAL_COMMIT,
        "run_authorization_id": run_authorization_id,
        "data_hashes": dict(data_hashes or {}),
        "event_calendar_sha256": _sha(K.EVENT_CALENDAR_PATH),
        "macro_calendar_sha256": _sha(K.MACRO_CALENDAR_PATH),
        "macro_covariates_sha256": _sha(
            os.path.join(K.TA_DIR, "TA_MACRO_COVARIATES.csv")),
        "primary_event_count": primary["n_events"],
        "primary_years": primary["years"],
        "mean_ac_gross_bps": primary["mean_gross"].as_dict(),
        "mean_ac_net_bps": primary["mean_net_point"],
        "mean_ac_net_ci95": [primary["mean_gross"].lower - K.COST_BPS,
                             primary["mean_gross"].upper - K.COST_BPS],
        "calendarised_sharpe": primary["sharpe"].point,
        "calendarised_sharpe_ci95": [primary["sharpe"].lower, primary["sharpe"].upper],
        "monthly_grid": dict(monthly_grid),
        "loyo": loyo.as_dict(),
        "secondary_ief": secondary.as_dict() if secondary else None,
        "gradient_shy": gradient.as_dict() if gradient else None,
        "placebo_spy": placebo.as_dict() if placebo else None,
        "macro_qra": macro.as_dict() if macro else None,
        "diagnostic_triggers": list(verdict.triggers),
        "final_class": verdict.klass,
        "research_status": verdict.research_status,
        "qualifier": verdict.qualifier,
        "evidence_ceiling": K.EVIDENCE_CEILING,
        "forbidden_interpretations": K.FORBIDDEN_CAUSAL_REMINDER,
        "descriptives": dict(descriptives or {}),
    }
    missing = [f for f in REQUIRED_FIELDS if f not in doc]
    if missing:
        raise AssertionError(f"result artifact is missing fields: {missing}")
    return doc


def validate_result(doc: Mapping[str, Any]) -> Dict[str, Any]:
    problems = [f"missing field {f}" for f in REQUIRED_FIELDS if f not in doc]
    if doc.get("final_class") not in K.STATUS_MAP:
        problems.append(f"unknown final_class {doc.get('final_class')!r}")
    else:
        status, qualifier = K.STATUS_MAP[doc["final_class"]]
        if doc.get("research_status") != status:
            problems.append("research_status does not match the sealed §I.4 mapping")
        if doc["final_class"] == "I" and doc.get("qualifier") != qualifier:
            problems.append("a Class-I result must carry the mandatory qualifier")
    if doc.get("evidence_ceiling") != K.EVIDENCE_CEILING:
        problems.append("evidence ceiling must be `supported`")
    if doc.get("synthetic_only") == "NO" and not doc.get("run_authorization_id"):
        problems.append("a non-synthetic artifact needs a run_authorization_id")
    return {"ok": not problems, "problems": problems}


def write_result(doc: Mapping[str, Any], path: str) -> Dict[str, Any]:
    check = validate_result(doc)
    if not check["ok"]:
        raise AssertionError(f"refusing to write an invalid artifact: {check['problems']}")
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(doc, fh, indent=1, sort_keys=True, default=str)
        fh.write("\n")
    return {"path": path, "sha256": _sha(path)}


def render_markdown(doc: Mapping[str, Any]) -> str:
    """A short human-readable rendering. Never a substitute for the JSON artifact."""
    lines = [
        f"# {doc['lineage']} — result artifact ({doc['schema_version']})",
        "",
        "```",
        f"SYNTHETIC_ONLY        = {doc['synthetic_only']}",
        f"DATA_KIND             = {doc['data_kind']}",
        f"RUN_AUTHORIZATION_ID  = {doc['run_authorization_id']}",
        f"SEALED_PREREG_SHA256  = {doc['sealed_prereg_sha256']}",
        f"EVENT_CALENDAR_SHA256 = {doc['event_calendar_sha256']}",
        f"PRIMARY_EVENT_COUNT   = {doc['primary_event_count']}",
        f"MEAN_AC_GROSS_BPS     = {doc['mean_ac_gross_bps']['point']}",
        f"MEAN_AC_NET_BPS       = {doc['mean_ac_net_bps']}",
        f"MEAN_AC_NET_CI95      = {doc['mean_ac_net_ci95']}",
        f"CALENDARISED_SHARPE   = {doc['calendarised_sharpe']}",
        f"SHARPE_CI95           = {doc['calendarised_sharpe_ci95']}",
        f"DIAGNOSTIC_TRIGGERS   = {doc['diagnostic_triggers']}",
        f"FINAL_CLASS           = {doc['final_class']}  ({doc['research_status']}"
        + (f" / {doc['qualifier']}" if doc['qualifier'] else "") + ")",
        f"EVIDENCE_CEILING      = {doc['evidence_ceiling']}",
        "```",
        "",
        "> " + doc["forbidden_interpretations"],
    ]
    return "\n".join(lines) + "\n"
