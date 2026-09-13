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
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import value_contract as _C          # noqa: E402

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
    "C3_INTERPRETATION", "C3_OPERATOR", "C3_PERMITTED_CLAIM",
    "C3_FORBIDDEN_CLAIM", "C3_KNOWN_LIMITATION", "CONTRIBUTION_LEDGER",
    "FULL_EXECUTED",
    "BOOTSTRAP_COUNTS", "DIAGNOSTICS",
    "SHILLER_VINTAGE_LIMITATION", "EVIDENCE_CEILING",
    "OUTCOME_EXPOSURE_STATE",
)

FULL_FIELDS = ("FULL_STATISTICS", "FULL_CI", "FULL_STATE")

CI_FIELDS = ("lower", "upper", "level", "n_valid")
# §10 of the amendment: the minimum each C3 case must carry.
CASE_FIELDS = ("EPISODE_IDENTITY", "INSTRUMENT", "EPISODE_SIGNAL_MONTHS",
               "ABLATED_CONTRIBUTION_MONTHS",
               "CONTRIBUTION_ACCOUNTING_IDENTITY", "C1_RESULT",
               "CORRELATION_STATISTIC", "CORRELATION_CI", "C2_RESULT",
               "INFERENCE_VALIDITY")

C3_INTERPRETATION_REQUIRED = "CONTRIBUTION_SENSITIVITY_ROBUSTNESS"
FORBIDDEN_C3_LANGUAGE = ("TEMPORAL_REGIME_ROBUSTNESS",
                         "robust across independent valuation regimes")

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
            if not isinstance(case.get("EPISODE_SIGNAL_MONTHS"), list):
                bad("C3_CASES[%d].EPISODE_SIGNAL_MONTHS must list the months"
                    % i)
            if not isinstance(case.get("ABLATED_CONTRIBUTION_MONTHS"), list):
                bad("C3_CASES[%d].ABLATED_CONTRIBUTION_MONTHS must list the "
                    "mapped contribution months" % i)
            if case.get("INFERENCE_VALIDITY") not in ("VALID", "INVALID"):
                bad("C3_CASES[%d].INFERENCE_VALIDITY must be VALID or INVALID"
                    % i)
            # The ablation retains every calendar month; a case that reports a
            # reduced sample is running the superseded deletion operator.
            if "months_remaining" in case:
                bad("C3_CASES[%d] reports months_remaining — the sealed "
                    "operator ablates a contribution and deletes no month" % i)
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

    # --- amendment lineage, checked against the contract's own definition ---
    # The 2026-09-13 artifact carried a stale AMENDMENT_002 label on a row whose
    # identities were actually _003, and omitted the genuine _002 row. Presence
    # alone was all the schema then required, so nothing rejected it.
    lin = ev.get("AMENDMENT_LINEAGE")
    want = list(_C.AMENDMENT_LINEAGE)
    if not isinstance(lin, list):
        bad("AMENDMENT_LINEAGE must be a list")
    else:
        if len(lin) != len(want):
            bad("AMENDMENT_LINEAGE has %d entries, the contract defines %d"
                % (len(lin), len(want)))
        labels = [e.get("amendment") for e in lin if isinstance(e, dict)]
        if len(set(labels)) != len(labels):
            bad("AMENDMENT_LINEAGE contains a duplicate amendment label")
        for i, (w_id, w_rev, w_sha) in enumerate(want):
            if i >= len(lin):
                bad("AMENDMENT_LINEAGE is missing the entry for %s" % w_id)
                continue
            e = lin[i]
            if not isinstance(e, dict):
                bad("AMENDMENT_LINEAGE[%d] is not an object" % i)
                continue
            if e.get("amendment") != w_id:
                bad("AMENDMENT_LINEAGE[%d] is labelled %r; the contract has %r "
                    "at that position" % (i, e.get("amendment"), w_id))
            if e.get("seal_revision") != w_rev:
                bad("AMENDMENT_LINEAGE[%d] (%s) records seal revision %r, the "
                    "contract pins %r"
                    % (i, w_id, e.get("seal_revision"), w_rev))
            if e.get("sealed_prereg_sha256") != w_sha:
                bad("AMENDMENT_LINEAGE[%d] (%s) records sealed sha256 %r, the "
                    "contract pins %r"
                    % (i, w_id, e.get("sealed_prereg_sha256"), w_sha))
        missing = [w[0] for w in want if w[0] not in labels]
        if missing:
            bad("AMENDMENT_LINEAGE omits %s" % ", ".join(missing))
        if lin and isinstance(lin[-1], dict):
            if (lin[-1].get("seal_revision") != _C.SEAL_REVISION
                    or lin[-1].get("sealed_prereg_sha256")
                    != _C.SEALED_PREREG_SHA256):
                bad("the terminal AMENDMENT_LINEAGE entry must be the ACTIVE "
                    "seal")

    # --- the frozen C3 interpretation --------------------------------------
    if ev.get("C3_INTERPRETATION") != C3_INTERPRETATION_REQUIRED:
        bad("C3_INTERPRETATION must be %r" % C3_INTERPRETATION_REQUIRED)
    permitted = str(ev.get("C3_PERMITTED_CLAIM", ""))
    for phrase in FORBIDDEN_C3_LANGUAGE:
        if phrase.lower() in permitted.lower():
            bad("C3_PERMITTED_CLAIM contains forbidden language: %r" % phrase)
    if not ev.get("C3_KNOWN_LIMITATION"):
        bad("the shared-regime limitation must survive into the artifact")

    led = ev.get("CONTRIBUTION_LEDGER")
    if not isinstance(led, dict):
        bad("CONTRIBUTION_LEDGER must be an object")
    else:
        if not led.get("reconciles"):
            bad("CONTRIBUTION_LEDGER does not reconcile V_t = a_t + sum_i c_i,t")
        for k, want in (("weight_redistribution", False),
                        ("vol_retarget_after_ablation", False),
                        ("gross_rescale_after_ablation", False),
                        ("ablations_cumulative", False)):
            if led.get(k) is not want:
                bad("CONTRIBUTION_LEDGER.%s must be %r" % (k, want))

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
