# -*- coding: utf-8 -*-
"""CTA-EDGE-05 / F6 — (K) the S3 result schema, designed now and empty now.

Six layers, deliberately not merged, because collapsing them is how a
measurement gets read as a verdict and a verdict as a claim:

```
MEASUREMENT      point estimates and counts
INFERENCE        intervals, their nominal status, the bootstrap settings
GATE             P1 / P2 / P3 pass-fail
TERMINAL VERDICT the sealed §12 state
CLAIM CAP        what a pass may and may not be said to support
PROVENANCE       seal id, hashes, build hash, authorization
```

No historical value is filled here. An unrun quantity is the string
``NOT_RUN``, never ``0``, ``0.0`` or an empty interval — a zero placeholder in a
return field is indistinguishable from a real zero result, and this programme
has already had one artifact whose status contradicted its class.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

import f6_contract as K

NOT_RUN = "NOT_RUN"
SCHEMA_NAME = "f6-s3-result"
SCHEMA_VERSION = 1

#: fields that must be NOT_RUN in any artifact whose run has not happened
_OUTCOME_FIELDS = (
    "p1_estimate", "p1_lower", "p1_upper", "p1_class",
    "p2_beta_event", "p2_lower", "p2_upper", "p2_class",
    "p3_year_results", "p3_pass", "terminal_classification",
)


def empty_result(build_hash: str = NOT_RUN,
                 event_count: Optional[int] = None) -> Dict[str, Any]:
    """The S3 schema with every outcome slot structurally absent."""
    return {
        "schema": {"name": SCHEMA_NAME, "version": SCHEMA_VERSION},
        "run_state": NOT_RUN,
        "data_kind": NOT_RUN,
        "run_id": NOT_RUN,

        # ---- MEASUREMENT ----------------------------------------------- #
        "measurement": {
            "p1_estimate": NOT_RUN,
            "p2_beta_event": NOT_RUN,
            "event_count": (K.FINAL_PRIMARY_EVENT_COUNT if event_count is None
                            else int(event_count)),
            "p2_rows": K.P2_ROWS,
            "year_count": K.YEAR_BLOCK_COUNT,
            "family_labels": dict(K.FAMILY_LABELS),
            "multi_event_sessions": K.MULTI_EVENT_SESSIONS,
        },

        # ---- INFERENCE -------------------------------------------------- #
        "inference": {
            "p1_lower": NOT_RUN, "p1_upper": NOT_RUN,
            "p2_lower": NOT_RUN, "p2_upper": NOT_RUN,
            "bootstrap_B": K.BOOTSTRAP_B,
            "bootstrap_seed_literal": K.BOOTSTRAP_SEED_LITERAL,
            "bootstrap_seed_source": K.BOOTSTRAP_SEED_SOURCE,
            "year_blocks": list(K.PRIMARY_YEARS),
            "quantile_implementation": K.QUANTILE_IMPLEMENTATION,
            "lower_quantile": K.QUANTILE_LOWER,
            "upper_quantile": K.QUANTILE_UPPER,
            "interval": K.INTERVAL_WORDING,
            "coverage_claim": "NOMINAL / APPROXIMATE. NOT exact finite-sample "
                              "95% coverage. 15 year blocks imply approximate, "
                              "assumption-dependent inference; a large event "
                              "count creates no additional clusters.",
            "pinned_environment": dict(K.PINNED_ENV),
        },

        # ---- GATE -------------------------------------------------------- #
        "gate": {
            "p1_class": NOT_RUN, "p2_class": NOT_RUN,
            "p3_evaluated": NOT_RUN, "p3_pass": NOT_RUN,
            "p3_year_results": NOT_RUN,
            "p1_rule": "lower endpoint of the nominal 95% interval for mean "
                       "r_net > 0",
            "p2_rule": "lower endpoint of the nominal 95% interval for "
                       "beta_EVENT > 0",
            "p3_rule": "evaluated ONLY after P1 and P2 pass; every LOYO P1 and "
                       "beta_EVENT point estimate STRICTLY > 0; NO "
                       "deletion-level significance requirement",
        },

        # ---- TERMINAL VERDICT -------------------------------------------- #
        "verdict": {
            "terminal_classification": NOT_RUN,
            "research_status": NOT_RUN,
            "qualifier": NOT_RUN,
            "forbidden_states": list(K.FORBIDDEN_TERMINAL_STATES),
        },

        # ---- CLAIM CAP ---------------------------------------------------- #
        "claim_cap": {
            "sample_reuse_class": K.SAMPLE_REUSE_CLASS,
            "evidence_ceiling": K.EVIDENCE_CEILING,
            "independent_confirmation": K.INDEPENDENT_CONFIRMATION,
            "execution_status": "adjusted-close EXECUTION PROXY; NOT "
                                "production-grade fill evidence",
            "cash_proxy": "DGS3MO, /365 OWNER-CHOSEN; never attributed to "
                          "Treasury, H.15 or FRED",
            "must_not_claim": list(K.CLAIM_MUST_NOT),
        },

        # ---- PROVENANCE --------------------------------------------------- #
        "provenance": {
            "lineage": K.LINEAGE,
            "seal_id": K.SEAL_ID,
            "seal_commit": K.SEAL_COMMIT,
            "sealed_preregistration_sha256": K.SEALED_PREREG_SHA256,
            "sealed_manifest_sha256": K.SEALED_MANIFEST_SHA256,
            "event_manifest_sha256": K.EVENT_MANIFEST_SHA256,
            "panel_sha256": K.PANEL_SHA256,
            "cash_sha256": K.CASH_SHA256,
            "build_hash": build_hash,
            "authorization_id": NOT_RUN,
            "f6_primary_trial_consumed": False,
        },
    }


def validate_result(doc: Dict[str, Any]) -> Dict[str, Any]:
    """Structural acceptance. A document whose status contradicts its content
    is rejected rather than written."""
    errs = []
    if doc.get("schema", {}).get("name") != SCHEMA_NAME:
        errs.append("wrong schema name")
    inf, gate, meas = doc.get("inference", {}), doc.get("gate", {}), \
        doc.get("measurement", {})
    ver, cap = doc.get("verdict", {}), doc.get("claim_cap", {})

    if inf.get("bootstrap_B") != K.BOOTSTRAP_B:
        errs.append("bootstrap_B is not the sealed value")
    if inf.get("bootstrap_seed_literal") != K.BOOTSTRAP_SEED_LITERAL:
        errs.append("seed is not the sealed value")
    if inf.get("quantile_implementation") != K.QUANTILE_IMPLEMENTATION:
        errs.append("quantile implementation is not the sealed one")
    if "exact" in str(inf.get("coverage_claim", "")).lower().replace(
            "not exact", ""):
        errs.append("coverage claim asserts exactness")
    if meas.get("event_count") != K.FINAL_PRIMARY_EVENT_COUNT:
        errs.append("event_count is not the sealed 462")
    if meas.get("year_count") != K.YEAR_BLOCK_COUNT:
        errs.append("year_count is not 15")
    if cap.get("evidence_ceiling") != K.EVIDENCE_CEILING:
        errs.append("evidence ceiling is not SUPPORTED")
    if cap.get("independent_confirmation") is not False:
        errs.append("independent_confirmation must be False")
    if ver.get("terminal_classification") in K.FORBIDDEN_TERMINAL_STATES:
        errs.append("forbidden terminal state")
    if ver.get("research_status") == "confirmed":
        errs.append("research_status 'confirmed' is unreachable for F6")

    unrun = doc.get("run_state") == NOT_RUN
    slots = [meas.get("p1_estimate"), meas.get("p2_beta_event"),
             inf.get("p1_lower"), inf.get("p1_upper"), inf.get("p2_lower"),
             inf.get("p2_upper"), gate.get("p1_class"), gate.get("p2_class"),
             gate.get("p3_pass"), ver.get("terminal_classification")]
    if unrun:
        filled = [s for s in slots if s != NOT_RUN]
        if filled:
            errs.append("run_state=NOT_RUN but outcome slots are filled: %r"
                        % filled)
        if doc.get("provenance", {}).get("f6_primary_trial_consumed"):
            errs.append("NOT_RUN artifact claims the trial was consumed")
    else:
        if any(s == NOT_RUN for s in slots):
            errs.append("run_state is not NOT_RUN but outcome slots are empty")
    return {"ok": not errs, "errors": errs}


def write_result(doc: Dict[str, Any], path: str) -> str:
    v = validate_result(doc)
    assert v["ok"], "refusing to persist an invalid result artifact: %s" % v["errors"]
    d = os.path.dirname(os.path.abspath(path))
    if d and not os.path.isdir(d):
        os.makedirs(d)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(doc, fh, indent=1, sort_keys=True)
        fh.write("\n")
    return path
