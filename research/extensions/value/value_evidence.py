# -*- coding: utf-8 -*-
"""The authoritative Value evidence artifact: schema and validator.

Defined and validated BEFORE S3, so a one-shot run cannot discover its own
schema defect after the fact.

Two asymmetries are deliberate:

* the FULL block is required exactly when `FULL_EXECUTED` is true, and
  **forbidden** when it is false. A refused branch that nevertheless carries a
  `ΔS_combo` would mean the combination was computed after the sealed rule said
  not to, so its mere presence is a violation;
* every C3 case must carry both intervals it was adjudicated on. "C1 and C2
  passed" without the intervals is a claim, not evidence.
"""
import io
import json

SCHEMA = "VALUE_S3_EVIDENCE_V1"

# --- top level ---------------------------------------------------------------
REQUIRED = (
    "schema",
    "RUN_ID", "AUTHORIZATION_ID",
    "SEALED_PREREG_SHA256", "SEAL_REVISION", "AMENDMENT_LINEAGE",
    "CODE_IDENTITY", "INPUT_PROVENANCE",
    "EVALUATION_START", "EVALUATION_END", "N",
    "VALUE_STANDALONE_STATISTICS", "VALUE_STANDALONE_CI",
    "VALUE_STANDALONE_STATE", "C1",
    "VALUE_TSMOM_CORRELATION", "CORRELATION_CI", "C2",
    "SELECTED_EPISODES", "C3_CASES", "C3", "CANDIDACY",
    "FULL_EXECUTED",
    "BOOTSTRAP_COUNTS", "DIAGNOSTICS",
    "SHILLER_VINTAGE_LIMITATION", "EVIDENCE_CEILING",
    "OUTCOME_EXPOSURE_STATE",
)

FULL_FIELDS = ("FULL_STATISTICS", "FULL_CI", "FULL_STATE")

CI_FIELDS = ("lower", "upper", "level", "n_valid")
CASE_FIELDS = ("episode", "omitted_months", "months_remaining",
               "standalone_ci", "c1", "correlation_ci", "c2", "valid")

STANDALONE_STATES = ("SUPPORTED_POSITIVE_EDGE", "MATERIALLY_ADVERSE",
                     "UNRESOLVED_EDGE")
FULL_STATES = ("SUPPORTED_INCREMENTAL_BENEFIT", "INCREMENTAL_BENEFIT_ADVERSE",
               "INCREMENTAL_BENEFIT_NOT_ESTABLISHED")


class EvidenceSchemaError(ValueError):
    pass


def _is_ci(obj, allow_none=False):
    if obj is None:
        return allow_none
    return isinstance(obj, dict) and all(k in obj for k in CI_FIELDS)


def validate(ev):
    """Return (ok, problems). Structural only — it never judges an outcome."""
    problems = []

    def bad(msg):
        problems.append(msg)

    if not isinstance(ev, dict):
        return False, ["evidence is not an object"]

    for k in REQUIRED:
        if k not in ev:
            bad("missing required field: %s" % k)
    if ev.get("schema") != SCHEMA:
        bad("schema is %r, expected %r" % (ev.get("schema"), SCHEMA))

    # --- window ------------------------------------------------------------
    if not isinstance(ev.get("N"), int) or ev.get("N", 0) <= 0:
        bad("N must be a positive integer")

    # --- standalone --------------------------------------------------------
    if not _is_ci(ev.get("VALUE_STANDALONE_CI")):
        bad("VALUE_STANDALONE_CI must carry %s" % (CI_FIELDS,))
    if ev.get("VALUE_STANDALONE_STATE") not in STANDALONE_STATES:
        bad("VALUE_STANDALONE_STATE is not one of %s" % (STANDALONE_STATES,))
    if not isinstance(ev.get("C1"), bool):
        bad("C1 must be boolean")

    # --- correlation -------------------------------------------------------
    if not _is_ci(ev.get("CORRELATION_CI")):
        bad("CORRELATION_CI must carry %s" % (CI_FIELDS,))
    if not isinstance(ev.get("C2"), bool):
        bad("C2 must be boolean")

    # --- episodes and C3 ---------------------------------------------------
    eps = ev.get("SELECTED_EPISODES")
    if not isinstance(eps, list) or not eps:
        bad("SELECTED_EPISODES must be a non-empty list")
    cases = ev.get("C3_CASES")
    if not isinstance(cases, list) or not cases:
        bad("C3_CASES must be a non-empty list")
    else:
        if isinstance(eps, list) and len(cases) != len(eps):
            bad("C3_CASES has %d entries for %d selected episodes"
                % (len(cases), len(eps)))
        for i, case in enumerate(cases):
            if not isinstance(case, dict):
                bad("C3_CASES[%d] is not an object" % i)
                continue
            for k in CASE_FIELDS:
                if k not in case:
                    bad("C3_CASES[%d] missing %s" % (i, k))
            if not isinstance(case.get("omitted_months"), list):
                bad("C3_CASES[%d].omitted_months must list the calendar months"
                    % i)
            # An invalid case legitimately has no intervals; a valid one must
            # show both, because that is what it was adjudicated on.
            if case.get("valid"):
                if not _is_ci(case.get("standalone_ci")):
                    bad("C3_CASES[%d] is valid but carries no standalone CI" % i)
                if not _is_ci(case.get("correlation_ci")):
                    bad("C3_CASES[%d] is valid but carries no correlation CI" % i)
    if not isinstance(ev.get("C3"), bool):
        bad("C3 must be boolean")

    cand = ev.get("CANDIDACY")
    if not isinstance(cand, dict) or "candidate" not in cand:
        bad("CANDIDACY must be an object carrying `candidate`")

    # --- the conditional FULL block ----------------------------------------
    fe = ev.get("FULL_EXECUTED")
    if not isinstance(fe, bool):
        bad("FULL_EXECUTED must be boolean")
    elif fe:
        for k in FULL_FIELDS:
            if k not in ev:
                bad("FULL_EXECUTED is true but %s is missing" % k)
        if not _is_ci(ev.get("FULL_CI")):
            bad("FULL_CI must carry %s" % (CI_FIELDS,))
        if ev.get("FULL_STATE") not in FULL_STATES:
            bad("FULL_STATE is not one of %s" % (FULL_STATES,))
        if isinstance(cand, dict) and not cand.get("candidate"):
            bad("FULL was executed although candidacy did not pass")
    else:
        for k in FULL_FIELDS:
            if k in ev:
                bad("FULL_EXECUTED is false but %s is present — the sealed "
                    "branch forbids computing it" % k)
        if isinstance(cand, dict) and cand.get("candidate"):
            bad("candidacy passed but FULL was not executed")

    # --- bootstrap accounting ----------------------------------------------
    bc = ev.get("BOOTSTRAP_COUNTS")
    if not isinstance(bc, dict) or not bc:
        bad("BOOTSTRAP_COUNTS must record attempted/valid/discarded per arm")
    else:
        for arm, c in bc.items():
            if not isinstance(c, dict):
                bad("BOOTSTRAP_COUNTS[%s] is not an object" % arm)
                continue
            for k in ("attempted", "valid", "discarded"):
                if k not in c:
                    bad("BOOTSTRAP_COUNTS[%s] missing %s" % (arm, k))

    if not ev.get("SHILLER_VINTAGE_LIMITATION"):
        bad("the Shiller vintage limitation must survive into the artifact")
    if not ev.get("EVIDENCE_CEILING"):
        bad("the evidence ceiling must be recorded")

    return (not problems), problems


def write(ev, path):
    ok, problems = validate(ev)
    if not ok:
        raise EvidenceSchemaError(
            "refusing to write an invalid evidence artifact:\n  - "
            + "\n  - ".join(problems))
    io.open(path, "w", encoding="utf-8").write(
        json.dumps(ev, indent=1, sort_keys=True) + "\n")
    return path
