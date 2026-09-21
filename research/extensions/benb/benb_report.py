"""CTA-EDGE-02-BENB — the S3 result-artifact schema and report writer.

Component P of the S2 build. The schema is fixed now so the future governed run has
nowhere to invent a field. At S2 it is only ever populated from SYNTHETIC fixtures and
every such artifact is stamped `SYNTHETIC_ONLY = YES`.

`build_result()` refuses to stamp `SYNTHETIC_ONLY = NO` without a run authorization id,
and `validate_result()` refuses an artifact whose class, status and qualifier do not
match the sealed §I.4 mapping.
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
from typing import Any, Dict, Mapping, Optional

import benb_contract as K

SCHEMA_VERSION = "BENB-RESULT-1"

REQUIRED_FIELDS = (
    "schema_version", "lineage", "contract_id", "synthetic_only", "data_kind",
    "generated_at_utc", "sealed_prereg_sha256", "seal_manifest_sha256", "seal_commit",
    "run_authorization_id", "raw_price_hashes", "nav_hashes",
    "basis_data_provenance_warning", "structural_eligible_count",
    "discount_observation_count", "years_with_discount", "month_grid",
    "beta_T", "beta_O", "beta_N", "mean_net_trade_return_bps",
    "calendarised_sharpe", "loyo_beta_T", "lqd_secondary", "premium_descriptive",
    "classification_flags", "final_class", "research_status", "qualifier",
    "evidence_ceiling", "forbidden_interpretations",
)


def _sha(path: str) -> Optional[str]:
    try:
        with open(path, "rb") as fh:
            return hashlib.sha256(fh.read()).hexdigest()
    except OSError:
        return None


def build_result(*, data_kind: str, verdict, primary, secondary_summary=None,
                 run_authorization_id: Optional[str] = None,
                 extra: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    synthetic = data_kind != "REAL"
    if not synthetic and not run_authorization_id:
        raise ValueError(
            "a REAL result artifact requires a run_authorization_id; refusing to stamp "
            "SYNTHETIC_ONLY = NO without one")
    boot = primary.boot
    loyo = primary.loyo
    doc: Dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "lineage": K.LINEAGE,
        "contract_id": K.CONTRACT_ID,
        "synthetic_only": "YES" if synthetic else "NO",
        "data_kind": data_kind,
        "generated_at_utc": _dt.datetime.now(_dt.timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"),
        "sealed_prereg_sha256": K.SEALED_PREREG_SHA256,
        "seal_manifest_sha256": K.SEAL_MANIFEST_SHA256,
        "seal_commit": K.SEAL_COMMIT,
        "run_authorization_id": run_authorization_id,
        "raw_price_hashes": {n: h for n, h in K.PINNED.items() if "ohlc" in n},
        "nav_hashes": {n: h for n, h in K.PINNED.items()
                       if "nav_daily" in n or "fund_download" in n},
        "basis_data_provenance_warning": (
            f"{K.NAV_PROVENANCE}. The ETF price leg is REUSED / BURNED context; the NAV "
            f"leg is a new external source. Combined provenance is MIXED / DEPENDENT: a "
            f"new NAV leg does NOT launder a reused price sample."),
        "structural_eligible_count": primary.n_eligible,
        "discount_observation_count": primary.n_discount,
        "years_with_discount": primary.years_with_discount,
        "month_grid": {"months": len(primary.month_grid),
                       "first": primary.month_grid[0] if primary.month_grid else None,
                       "last": primary.month_grid[-1] if primary.month_grid else None},
        "beta_T": boot.beta_T.as_dict() if boot else None,
        "beta_O": boot.beta_O.as_dict() if boot else None,
        "beta_N": boot.beta_N.as_dict() if boot else None,
        "mean_net_trade_return_bps": boot.mean_net.as_dict() if boot else None,
        "calendarised_sharpe": boot.sharpe.as_dict() if boot else None,
        "loyo_beta_T": loyo.as_dict() if loyo else None,
        "lqd_secondary": dict(secondary_summary) if secondary_summary else None,
        "premium_descriptive": dict(primary.premium_descriptive),
        "classification_flags": {
            "gate1_supported": bool(boot and boot.beta_T.lower > 0.0),
            "m1_supported": bool(boot and boot.mean_net.lower > K.M1_RETURN_FLOOR_BPS),
            "m2_supported": bool(boot and boot.sharpe.lower > K.M2_SHARPE),
            "loyo_ok": bool(loyo and loyo.passes),
            "m2_operator": "STRICT >", "m2_value": K.M2_SHARPE,
            "m1_operator": "STRICT >", "m1_value": K.M1_RETURN_FLOOR_BPS,
        },
        "final_class": verdict.klass,
        "research_status": verdict.research_status,
        "qualifier": verdict.qualifier,
        "evidence_ceiling": K.EVIDENCE_CEILING,
        "forbidden_interpretations": K.FORBIDDEN_CAUSAL_REMINDER,
    }
    if extra:
        doc.update(dict(extra))
    missing = [f for f in REQUIRED_FIELDS if f not in doc]
    if missing:
        raise AssertionError(f"result artifact is missing fields: {missing}")
    return doc


def validate_result(doc: Mapping[str, Any]) -> Dict[str, Any]:
    problems = [f"missing field {f}" for f in REQUIRED_FIELDS if f not in doc]
    k = doc.get("final_class")
    if k not in K.STATUS_MAP:
        problems.append(f"unknown final_class {k!r}")
    else:
        status, qualifier = K.STATUS_MAP[k]
        if doc.get("research_status") != status:
            problems.append("research_status does not match the sealed mapping")
        if qualifier and doc.get("qualifier") != qualifier:
            problems.append(f"class {k} must carry the qualifier {qualifier!r}")
    if doc.get("evidence_ceiling") != K.EVIDENCE_CEILING:
        problems.append("evidence ceiling must be `supported`")
    if doc.get("synthetic_only") == "NO" and not doc.get("run_authorization_id"):
        problems.append("a non-synthetic artifact needs a run_authorization_id")
    flags = doc.get("classification_flags") or {}
    if flags.get("m2_operator") != "STRICT >" or flags.get("m2_value") != K.M2_SHARPE:
        problems.append("M2 must be recorded as STRICT > +0.30")
    return {"ok": not problems, "problems": problems}


def write_result(doc: Mapping[str, Any], path: str) -> Dict[str, Any]:
    chk = validate_result(doc)
    if not chk["ok"]:
        raise AssertionError(f"refusing to write an invalid artifact: {chk['problems']}")
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(doc, fh, indent=1, sort_keys=True, default=str)
        fh.write("\n")
    return {"path": path, "sha256": _sha(path)}
