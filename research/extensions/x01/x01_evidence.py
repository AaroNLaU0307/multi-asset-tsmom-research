"""X01 evidence artifact — SCHEMA AND VALIDATOR ONLY, NO STUDY, NO EXECUTION.

What this module is
-------------------
The record format the sealed X01 study writes its result into, plus the
validator that refuses an internally inconsistent record. It is the answer to
one question: *after outcomes exist, what may be written down, and what must
already have been true for writing it to be legitimate?*

Fixing that BEFORE any outcome exists is the point. A schema invented after the
numbers are visible can be shaped around them; this one cannot, because it is
frozen first and because the validator rejects the combinations that would let a
mechanical failure be read as a research result.

What this module is NOT
-----------------------
It computes no statistic, constructs nothing, reads no target data and holds no
scientific logic. It never decides an outcome state — it only checks that the
state a caller reports is *consistent* with the record around it. Writing is an
explicit call with a caller-supplied path; nothing here knows where real results
would live.

Four outcome states, deliberately separate
------------------------------------------
``COMPLETED_EVIDENCE`` is the only one that may carry a §5 classification.

``INFERENCE_PROCEDURE_FAILURE`` is §6.1's mechanical condition — fewer than
9,500 valid replicates. §6.1 says explicitly that it is **not** one of the three
outcome states, so a record in this state carries no classification at all.

``EXECUTION_REFUSED`` is a gate that did not open: no authorization, a failed
preflight, a seal mismatch, a sample contract violation. Nothing was computed.

``EXECUTION_MECHANICAL_FAILURE`` is a break part-way through: a construction
error, a failed write, a partial persistence. A partial run is never a verdict.

Keeping them apart is the schema's main safety property. Collapsing any two
would let "the machinery broke" and "the strategy degraded" occupy the same
field, and only one of those is a research finding.
"""

from __future__ import annotations

import calendar
import hashlib
import json
import math
import os

SCHEMA_NAME = "x01-evidence"
SCHEMA_VERSION = 1

# The four states. Exhaustive and mutually exclusive.
COMPLETED_EVIDENCE = "COMPLETED_EVIDENCE"
INFERENCE_PROCEDURE_FAILURE = "INFERENCE_PROCEDURE_FAILURE"
EXECUTION_REFUSED = "EXECUTION_REFUSED"
EXECUTION_MECHANICAL_FAILURE = "EXECUTION_MECHANICAL_FAILURE"
OUTCOME_STATES = (COMPLETED_EVIDENCE, INFERENCE_PROCEDURE_FAILURE,
                  EXECUTION_REFUSED, EXECUTION_MECHANICAL_FAILURE)

# The §5 classifications a COMPLETED_EVIDENCE record may carry, and nothing else.
SEALED_CLASSIFICATIONS = ("PRESERVATION_SUPPORTED", "MATERIAL_DEGRADATION_SUPPORTED",
                          "UNRESOLVED_INSUFFICIENT_PRECISION")

# Sealed expectations the validator checks a record against. These are the same
# values the sealed contract fixes; duplicating them here is deliberate, so the
# validator can reject a record whose configuration drifted from the seal
# without having to import and run the inference layer to find out.
SEALED_EXPECTATIONS = {
    "research_id": "TSMOM-EXT-001",
    "prereg_sha256": "4db18f6cc084bf4a4ba9260e7ba81489e658d74adf03818aa4169208a40f54c5",
    "sample_first_month_end": "2011-07-31",
    "sample_last_month_end": "2026-05-31",
    "expected_n": 179,
    "boundary_b": 0.15,
    "bootstrap_family": "stationary_bootstrap_politis_romano_1994",
    "expected_block_length_months": 12,
    "replications_attempted": 10000,
    "ci_level": 95,
    "ci_method": "percentile",
    "valid_replicate_floor": 9500,
    "min_distinct_months": 24,
    "master_seed": 7,
    "arm_order": ["primary", "S1", "S2"],
    "secondary_role": "DESCRIPTIVE_SENSITIVITY",
    "secondary_promotion_power": "NONE",
    "bh_fdr_required": False,
    "crisis_windows": ["COVID 2020", "CY2022"],
}

# Fields that legitimately differ between two runs of the same study and are
# therefore EXCLUDED from the content digest. Everything else is included, so a
# changed number changes the digest.
DIGEST_EXCLUDED_TOP_LEVEL = ("run_instance", "content_digest")

# A secondary arm may never carry any of these.
FORBIDDEN_SECONDARY_KEYS = ("classification", "outcome_state", "verdict",
                            "promotion", "p_value", "pass", "significant")

# Keys that only a result-bearing record may carry, ANYWHERE in it. A state that
# means "nothing was computed" or "the machinery broke" must not contain a
# scientific quantity at any depth — including inside a secondary block that a
# field-by-field omission check would never look at.
SCIENTIFIC_KEYS = ("classification", "delta_s", "sharpe_e", "sharpe_f",
                   "verdict", "promotion_power", "p_value", "significant",
                   "bootstrap_counts")

# §7.1, exactly. Two windows, named AND dated: a record that carries the right
# name over the wrong months has evaluated a different window and is not this
# study's §7 output. `Calm 2012-2019` and `GFC 2008` are excluded by the seal.
SEALED_CRISIS_WINDOWS = {
    "COVID 2020": ["2020-02-29", "2020-03-31", "2020-04-30"],
    "CY2022": ["2022-01-31", "2022-02-28", "2022-03-31", "2022-04-30",
               "2022-05-31", "2022-06-30", "2022-07-31", "2022-08-31",
               "2022-09-30", "2022-10-31", "2022-11-30", "2022-12-31"],
}

# The sealed §6.1 bootstrap identity, checked on the PRIMARY block itself and
# not only on the seed protocol beside it.
SEALED_BOOTSTRAP_IDENTITY = {
    "master_seed": 7,
    "arm_order": ["primary", "S1", "S2"],
    "percentile_interpolation": "linear",
}


def sealed_month_ends():
    """The sealed §3.5 calendar, built from the endpoints with stdlib only.

    Deliberately NOT the orchestrator's pandas `date_range`. The digest check
    below is worth something only because the two are independent
    implementations of the same sealed rule; re-using the producer's own helper
    would make the check a tautology.
    """
    out, y, m = [], 2011, 7
    while (y, m) <= (2026, 5):
        out.append("%04d-%02d-%02d" % (y, m, calendar.monthrange(y, m)[1]))
        m += 1
        if m == 13:
            y, m = y + 1, 1
    return out


def sealed_calendar_digest():
    """sha256 over the sealed month-ends, LF-joined. The reproducibility pin."""
    return hashlib.sha256(
        "\n".join(sealed_month_ends()).encode("utf-8")).hexdigest()


class EvidenceSchemaError(ValueError):
    """The record is not a valid X01 evidence artifact.

    Raised rather than returned wherever a caller might otherwise persist an
    inconsistent record and treat the absence of an exception as approval.
    """


# --------------------------------------------------------------------------- #
# canonical form and digest
# --------------------------------------------------------------------------- #
NONFINITE_SENTINEL = "__nonfinite__:%s"


def _sanitize(obj):
    """Replace non-finite floats with an explicit sentinel STRING.

    Used only for digesting. JSON has no NaN or infinity, so a record carrying
    one cannot be written at all — but it can still be CONSTRUCTED, and the
    validator has to be able to see it in order to reject it. Mapping to a
    visible sentinel keeps the digest total and deterministic without inventing
    a numeric value that was never computed.
    """
    if isinstance(obj, dict):
        return {k: _sanitize(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_sanitize(v) for v in obj]
    if isinstance(obj, float) and not math.isfinite(obj):
        return NONFINITE_SENTINEL % obj
    return obj


def canonical_json(obj, allow_non_finite=False):
    """Deterministic serialization: sorted keys, no incidental whitespace, LF.

    Two runs of the same study must produce byte-identical output, so the
    representation cannot depend on dict insertion order or on a pretty-printer.
    `allow_nan` stays False, so a non-finite value can never reach a persisted
    file; `allow_non_finite=True` sanitizes first and is used only for digesting
    a record that is about to be refused.
    """
    if allow_non_finite:
        obj = _sanitize(obj)
    return json.dumps(obj, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"), allow_nan=False)


def content_digest(artifact):
    """sha256 over the canonical form, excluding declared run-instance metadata.

    The exclusion list is explicit and small. A field is excluded because two
    honest runs must differ in it (a wall-clock stamp, a run id), never because
    it would be inconvenient for it to be pinned.
    """
    body = {k: v for k, v in artifact.items() if k not in DIGEST_EXCLUDED_TOP_LEVEL}
    return hashlib.sha256(
        canonical_json(body, allow_non_finite=True).encode("utf-8")).hexdigest()


def finalize(artifact):
    """Attach the content digest. The record is complete after this."""
    out = dict(artifact)
    out.pop("content_digest", None)
    out["content_digest"] = content_digest(out)
    return out


# --------------------------------------------------------------------------- #
# constructors — one per outcome state, so a caller cannot forget the state
# --------------------------------------------------------------------------- #
def _base(outcome_state, identity, governance, run_instance):
    return {
        "schema": {"name": SCHEMA_NAME, "version": SCHEMA_VERSION},
        "outcome_state": outcome_state,
        "identity": dict(identity),
        "sample": None,
        "arms": None,
        "primary": None,
        "secondary": None,
        "diagnostics": None,
        "governance": dict(governance),
        "run_instance": dict(run_instance),
    }


def refused(identity, governance, run_instance, reason, refusal_stage,
            refusal_detail=None):
    """A gate did not open. Nothing was constructed and nothing was computed."""
    a = _base(EXECUTION_REFUSED, identity, governance, run_instance)
    a["governance"]["refusal_reason"] = reason
    a["governance"]["refusal_stage"] = refusal_stage
    a["governance"]["refusal_detail"] = refusal_detail or []
    return finalize(a)


def mechanical_failure(identity, governance, run_instance, reason, stage,
                       sample=None, arms=None, detail=None):
    """A break part-way through. Explicitly not a scientific outcome."""
    a = _base(EXECUTION_MECHANICAL_FAILURE, identity, governance, run_instance)
    a["sample"] = sample
    a["arms"] = arms
    a["governance"]["failure_reason"] = reason
    a["governance"]["failure_stage"] = stage
    a["governance"]["failure_detail"] = detail or []
    return finalize(a)


def procedure_failure(identity, governance, run_instance, sample, arms, primary):
    """§6.1's mechanical inference condition. Carries counts, never a verdict."""
    a = _base(INFERENCE_PROCEDURE_FAILURE, identity, governance, run_instance)
    a["sample"] = sample
    a["arms"] = arms
    a["primary"] = dict(primary)
    a["primary"].pop("classification", None)
    return finalize(a)


def completed(identity, governance, run_instance, sample, arms, primary,
              secondary, diagnostics):
    """The only state that may carry a §5 classification."""
    a = _base(COMPLETED_EVIDENCE, identity, governance, run_instance)
    a["sample"] = sample
    a["arms"] = arms
    a["primary"] = primary
    a["secondary"] = secondary
    a["diagnostics"] = diagnostics
    return finalize(a)


# --------------------------------------------------------------------------- #
# validator
# --------------------------------------------------------------------------- #
def _finite(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def validate(artifact, expect_execution_revision=None):
    """Return the list of consistency violations. Empty means the record is sound.

    Every rule here refuses a record that would let something be read as more
    than it is: a verdict without the sample that entitles it, a classification
    on a broken interval, a sensitivity arm with promotion power, a completed
    study without the provenance that makes it reproducible.
    """
    e = []
    if not isinstance(artifact, dict):
        return ["artifact is not an object"]

    sch = artifact.get("schema") or {}
    if sch.get("name") != SCHEMA_NAME:
        e.append("schema.name must be %r" % SCHEMA_NAME)
    if sch.get("version") != SCHEMA_VERSION:
        e.append("schema.version must be %r" % SCHEMA_VERSION)

    state = artifact.get("outcome_state")
    if state not in OUTCOME_STATES:
        e.append("outcome_state %r is not one of the four declared states" % (state,))

    # digest integrity
    if "content_digest" in artifact:
        if artifact["content_digest"] != content_digest(artifact):
            e.append("content_digest does not match the canonical body")
    else:
        e.append("content_digest is absent")

    ident = artifact.get("identity") or {}
    gov = artifact.get("governance") or {}
    sample = artifact.get("sample")
    primary = artifact.get("primary")
    secondary = artifact.get("secondary")

    # ---- provenance -------------------------------------------------------
    if ident.get("research_id") != SEALED_EXPECTATIONS["research_id"]:
        e.append("identity.research_id must be %r"
                 % SEALED_EXPECTATIONS["research_id"])
    if ident.get("prereg_sha256") != SEALED_EXPECTATIONS["prereg_sha256"]:
        e.append("identity.prereg_sha256 is not the sealed preregistration hash")

    result_bearing = state in (COMPLETED_EVIDENCE, INFERENCE_PROCEDURE_FAILURE)
    required_ident = ("research_id", "prereg_sha256", "prereg_seal_revision",
                      "construction_binding_revision", "construction_sha256",
                      "inference_binding_revision", "inference_sha256",
                      "runner_revision", "manifest_sha256", "execution_revision",
                      "execution_infrastructure_revision", "run_id")
    if result_bearing:
        for k in required_ident:
            if not ident.get(k):
                e.append("a result-bearing record needs identity.%s" % k)
        if not ident.get("input_pins"):
            e.append("a result-bearing record needs identity.input_pins")
    if expect_execution_revision and ident.get("execution_revision") \
            and ident["execution_revision"] != expect_execution_revision:
        e.append("identity.execution_revision %r does not match the revision the "
                 "run actually executed at (%r)"
                 % (ident["execution_revision"], expect_execution_revision))

    # ---- governance -------------------------------------------------------
    if result_bearing:
        if not gov.get("authorization_reference"):
            e.append("a result-bearing record needs "
                     "governance.authorization_reference — a real execution "
                     "cannot have happened without an Owner authorization to cite")
        if gov.get("preflight_result") != "PASS":
            e.append("a result-bearing record needs governance.preflight_result "
                     "== 'PASS'")
        if not gov.get("exposure_record_reference"):
            e.append("a result-bearing record needs "
                     "governance.exposure_record_reference")
        if not gov.get("trial_accounting_reference"):
            e.append("a result-bearing record needs "
                     "governance.trial_accounting_reference")
    if state == EXECUTION_REFUSED and not gov.get("refusal_reason"):
        e.append("EXECUTION_REFUSED needs governance.refusal_reason")
    if state == EXECUTION_MECHANICAL_FAILURE and not gov.get("failure_reason"):
        e.append("EXECUTION_MECHANICAL_FAILURE needs governance.failure_reason")

    # ---- nothing computed in the non-result states -------------------------
    if state == EXECUTION_REFUSED:
        for k in ("sample", "arms", "primary", "secondary", "diagnostics"):
            if artifact.get(k) is not None:
                e.append("EXECUTION_REFUSED must carry no %s: a gate that did not "
                         "open computed nothing" % k)
    if state in (EXECUTION_REFUSED, EXECUTION_MECHANICAL_FAILURE):
        # A RECURSIVE scan, not a field-by-field omission list. A scientific
        # quantity nested three levels down inside a secondary block is exactly
        # as much a leak as one at the top, and only a walk of the whole record
        # finds it. `governance` is excluded because a failure's own free-text
        # detail is prose about the break, not a result.
        e += _scan_for_scientific_content(
            {k: v for k, v in artifact.items() if k != "governance"}, state)
        gov_text = canonical_json(gov, allow_non_finite=True)
        for cls in SEALED_CLASSIFICATIONS:
            if cls in gov_text:
                e.append("%s names the §5 classification %r in its governance "
                         "block: a break may describe itself, never conclude"
                         % (state, cls))

    # ---- sample -----------------------------------------------------------
    if result_bearing:
        if not isinstance(sample, dict):
            e.append("a result-bearing record needs a sample block")
        else:
            if sample.get("first_month_end") != SEALED_EXPECTATIONS["sample_first_month_end"]:
                e.append("sample.first_month_end must be the sealed %r"
                         % SEALED_EXPECTATIONS["sample_first_month_end"])
            if sample.get("last_month_end") != SEALED_EXPECTATIONS["sample_last_month_end"]:
                e.append("sample.last_month_end must be the sealed %r"
                         % SEALED_EXPECTATIONS["sample_last_month_end"])
            if sample.get("expected_n") != SEALED_EXPECTATIONS["expected_n"]:
                e.append("sample.expected_n must be the sealed 179")
            if state == COMPLETED_EVIDENCE and sample.get("evaluated_n") != 179:
                e.append("a COMPLETED_EVIDENCE record must have evaluated_n == 179 "
                         "(§4 requires all 179 paired months present)")
            if not sample.get("calendar_digest"):
                e.append("sample.calendar_digest is required, so the evaluated "
                         "calendar is reproducible and not merely counted")
            elif sample["calendar_digest"] != sealed_calendar_digest():
                # Re-derived here from the sealed endpoints with stdlib, so this
                # refuses a record that counted 179 months of the WRONG calendar
                # — the exact failure a bare count cannot see.
                e.append("sample.calendar_digest %r is not the digest of the "
                         "sealed §3.5 calendar (%s): a result-bearing record "
                         "must have evaluated the sealed months themselves"
                         % (sample["calendar_digest"],
                            sealed_calendar_digest()[:16] + "..."))
            if sample.get("missingness_state") is None:
                e.append("sample.missingness_state is required")

    # ---- primary ----------------------------------------------------------
    if state == COMPLETED_EVIDENCE:
        if not isinstance(primary, dict):
            e.append("COMPLETED_EVIDENCE needs a primary block")
        else:
            e += _validate_primary(primary, require_classification=True)
    elif state == INFERENCE_PROCEDURE_FAILURE:
        if not isinstance(primary, dict):
            e.append("INFERENCE_PROCEDURE_FAILURE needs a primary block carrying "
                     "the replicate counts")
        else:
            if primary.get("classification") is not None:
                e.append("INFERENCE_PROCEDURE_FAILURE must carry NO classification: "
                         "§6.1 states it is not one of the three outcome states")
            e += _validate_primary(primary, require_classification=False)
            counts = primary.get("bootstrap_counts") or {}
            if _finite(counts.get("valid")) and \
                    counts["valid"] >= SEALED_EXPECTATIONS["valid_replicate_floor"]:
                e.append("INFERENCE_PROCEDURE_FAILURE with %r valid replicates is "
                         "inconsistent: the sealed floor is %d"
                         % (counts.get("valid"),
                            SEALED_EXPECTATIONS["valid_replicate_floor"]))
    elif primary is not None:
        e.append("%s must carry no primary inference block" % state)

    # ---- secondary --------------------------------------------------------
    if state == COMPLETED_EVIDENCE:
        if not isinstance(secondary, dict):
            e.append("COMPLETED_EVIDENCE needs a secondary block")
        else:
            for arm in ("S1", "S2"):
                blk = secondary.get(arm)
                if not isinstance(blk, dict):
                    e.append("secondary.%s is required" % arm)
                    continue
                if blk.get("role") != SEALED_EXPECTATIONS["secondary_role"]:
                    e.append("secondary.%s.role must be %r"
                             % (arm, SEALED_EXPECTATIONS["secondary_role"]))
                if blk.get("promotion_power") != SEALED_EXPECTATIONS["secondary_promotion_power"]:
                    e.append("secondary.%s.promotion_power must be NONE (§8.3)" % arm)
                for bad in FORBIDDEN_SECONDARY_KEYS:
                    if bad in blk:
                        e.append("secondary.%s must not carry %r: §8.3 gives the "
                                 "secondaries no promotion power and no verdict"
                                 % (arm, bad))
                if not _finite(blk.get("delta_s")):
                    e.append("secondary.%s.delta_s must be finite" % arm)
                e += _validate_ci(blk.get("ci"), "secondary.%s.ci" % arm,
                                  expect_n_valid=(blk.get("bootstrap_counts")
                                                  or {}).get("valid"))
            if secondary.get("bh_fdr_required") is not False:
                e.append("secondary.bh_fdr_required must be false (§8.3)")

    # ---- diagnostics ------------------------------------------------------
    if state == COMPLETED_EVIDENCE:
        d = artifact.get("diagnostics")
        if not isinstance(d, dict):
            e.append("COMPLETED_EVIDENCE needs a diagnostics block")
        else:
            windows = [w.get("name") for w in (d.get("crisis_windows") or [])]
            if windows != SEALED_EXPECTATIONS["crisis_windows"]:
                e.append("diagnostics.crisis_windows must be exactly %r (§7.1)"
                         % (SEALED_EXPECTATIONS["crisis_windows"],))
            else:
                # The NAME is not the window. §7.1 fixes the months, and a
                # record carrying the sealed label over different dates has
                # evaluated some other window entirely.
                for w in d["crisis_windows"]:
                    want = SEALED_CRISIS_WINDOWS[w["name"]]
                    got = w.get("month_ends")
                    if got != want:
                        e.append("diagnostics crisis window %r must cover "
                                 "exactly the sealed §7.1 month-ends %r, not %r"
                                 % (w["name"], want, got))
                    if w.get("n_months") != len(want):
                        e.append("diagnostics crisis window %r must report "
                                 "n_months == %d" % (w["name"], len(want)))
            for k in ("pair_correlations", "tracking_error_monthly",
                      "tracking_error_annualised", "max_abs_d", "sign_agreement",
                      "turnover_e", "turnover_f", "realised_cost_e",
                      "realised_cost_f"):
                if k not in d:
                    e.append("diagnostics.%s is a sealed §7 output and is required" % k)
            if d.get("role") != "DESCRIPTIVE_NEVER_A_GATE":
                e.append("diagnostics.role must be DESCRIPTIVE_NEVER_A_GATE (§8.0)")

    # ---- arms -------------------------------------------------------------
    if result_bearing:
        arms = artifact.get("arms") or {}
        for arm in ("E", "A1", "S1", "S2"):
            blk = arms.get(arm)
            if blk is None:
                e.append("arms.%s is required" % arm)
                continue
            if not isinstance(blk, dict):
                e.append("arms.%s must be an object" % arm)
                continue
            # The KEY is not the identity. A block filed under "A1" that names
            # itself something else has recorded a different arm's result under
            # the primary's name, which is the one substitution the §5 verdict
            # would silently inherit.
            if blk.get("arm") != arm:
                e.append("arms.%s declares arm %r: the block filed under an arm "
                         "must be that arm" % (arm, blk.get("arm")))
            if not isinstance(blk.get("months"), int):
                e.append("arms.%s.months must be an integer" % arm)
            elif state == COMPLETED_EVIDENCE and blk["months"] < \
                    SEALED_EXPECTATIONS["expected_n"]:
                # `months` is the CONSTRUCTED series length, which legitimately
                # exceeds the evaluated sample: the legs carry warm-up months
                # the sealed window does not evaluate, and the two legs need not
                # be the same length. What cannot happen is an arm shorter than
                # the sealed sample it is supposed to have covered.
                e.append("arms.%s.months is %d, fewer than the sealed %d "
                         "evaluated month-ends: the arm cannot have covered the "
                         "sealed sample"
                         % (arm, blk["months"], SEALED_EXPECTATIONS["expected_n"]))
        seeds = arms.get("seed_protocol") or {}
        if seeds.get("master_seed") != SEALED_EXPECTATIONS["master_seed"]:
            e.append("arms.seed_protocol.master_seed must be the sealed 7")
        if seeds.get("arm_order") != SEALED_EXPECTATIONS["arm_order"]:
            e.append("arms.seed_protocol.arm_order must be %r"
                     % (SEALED_EXPECTATIONS["arm_order"],))
        keys = [c.get("spawn_key") for c in (seeds.get("child_streams") or [])]
        if keys != [[0], [1], [2]]:
            e.append("arms.seed_protocol child spawn_keys must be [[0],[1],[2]] — "
                     "`.entropy` cannot identify the children")
    return e


def _scan_for_scientific_content(node, state, path="artifact"):
    """Walk the WHOLE record looking for anything only a result may carry.

    A state that means "nothing was computed" or "the machinery broke" must
    contain no scientific quantity at any depth. A field-by-field omission list
    checks the places someone thought of; this checks every place.
    """
    e = []
    if isinstance(node, dict):
        for k, v in node.items():
            if k in SCIENTIFIC_KEYS:
                e.append("%s carries %s.%s — a state in which nothing was "
                         "computed must hold no scientific quantity at any "
                         "depth" % (state, path, k))
            e += _scan_for_scientific_content(v, state, "%s.%s" % (path, k))
    elif isinstance(node, (list, tuple)):
        for i, v in enumerate(node):
            e += _scan_for_scientific_content(v, state, "%s[%d]" % (path, i))
    elif isinstance(node, str) and node in SEALED_CLASSIFICATIONS:
        e.append("%s carries the §5 classification %r at %s"
                 % (state, node, path))
    return e


def _validate_primary(primary, require_classification):
    e = []
    cfg = primary.get("bootstrap") or {}
    for key, want in (("family", SEALED_EXPECTATIONS["bootstrap_family"]),
                      ("expected_block_length_months",
                       SEALED_EXPECTATIONS["expected_block_length_months"]),
                      ("replications_attempted",
                       SEALED_EXPECTATIONS["replications_attempted"]),
                      ("ci_level", SEALED_EXPECTATIONS["ci_level"]),
                      ("ci_method", SEALED_EXPECTATIONS["ci_method"]),
                      ("valid_replicate_floor",
                       SEALED_EXPECTATIONS["valid_replicate_floor"]),
                      ("min_distinct_months",
                       SEALED_EXPECTATIONS["min_distinct_months"])):
        if cfg.get(key) != want:
            e.append("primary.bootstrap.%s must be the sealed %r (got %r)"
                     % (key, want, cfg.get(key)))
    # The seed identity is checked on the PRIMARY block itself, not only on the
    # seed protocol recorded beside it. A record whose bootstrap ran under a
    # different master seed is not reproducible from the seal, however correct
    # the protocol block next to it looks.
    for key, want in sorted(SEALED_BOOTSTRAP_IDENTITY.items()):
        if cfg.get(key) != want:
            e.append("primary.bootstrap.%s must be the sealed %r (got %r)"
                     % (key, want, cfg.get(key)))
    if primary.get("boundary_b") != SEALED_EXPECTATIONS["boundary_b"]:
        e.append("primary.boundary_b must be the sealed 0.15")
    if primary.get("boundary") != -SEALED_EXPECTATIONS["boundary_b"]:
        e.append("primary.boundary must be -0.15")
    for k in ("sharpe_e", "sharpe_f", "delta_s"):
        if not _finite(primary.get(k)):
            e.append("primary.%s must be finite" % k)
    if _finite(primary.get("sharpe_e")) and _finite(primary.get("sharpe_f")) \
            and _finite(primary.get("delta_s")):
        if abs((primary["sharpe_f"] - primary["sharpe_e"]) - primary["delta_s"]) > 1e-12:
            e.append("primary.delta_s must equal Sharpe(F) - Sharpe(E) exactly")
    counts = primary.get("bootstrap_counts") or {}
    for k in ("attempted", "valid", "discarded",
              "discarded_too_few_distinct_months", "discarded_zero_std_e",
              "discarded_zero_std_f"):
        if not isinstance(counts.get(k), int):
            e.append("primary.bootstrap_counts.%s must be an integer" % k)
    if all(isinstance(counts.get(k), int) for k in ("attempted", "valid", "discarded")):
        if counts["attempted"] != counts["valid"] + counts["discarded"]:
            e.append("primary.bootstrap_counts do not add up")
        if counts["attempted"] != SEALED_EXPECTATIONS["replications_attempted"]:
            e.append("primary.bootstrap_counts.attempted must be the sealed 10,000")

    if require_classification:
        cls = primary.get("classification")
        if cls not in SEALED_CLASSIFICATIONS:
            e.append("primary.classification must be one of the three sealed §5 "
                     "states (got %r)" % (cls,))
        ci_errors = _validate_ci(primary.get("ci"), "primary.ci",
                                 expect_n_valid=counts.get("valid"))
        e += ci_errors
        if not ci_errors and cls in SEALED_CLASSIFICATIONS:
            e += _check_classification_matches_ci(primary["ci"], cls,
                                                  primary.get("boundary_b"))
        if isinstance(counts.get("valid"), int) and \
                counts["valid"] < SEALED_EXPECTATIONS["valid_replicate_floor"]:
            e.append("a classification with only %d valid replicates is "
                     "inconsistent: below the sealed floor the record must be "
                     "INFERENCE_PROCEDURE_FAILURE" % counts["valid"])
    return e


def _validate_ci(ci, label, expect_n_valid=None):
    """The interval, plus the one relationship it cannot be allowed to contradict.

    `n_valid` is the number of replicates the interval was actually taken over.
    If it disagrees with the recorded bootstrap counts, one of the two is a
    fiction, and the interval is the half a verdict rests on.
    """
    if not isinstance(ci, dict):
        return ["%s is required" % label]
    e = []
    if expect_n_valid is not None and ci.get("n_valid") != expect_n_valid:
        e.append("%s.n_valid is %r but the recorded bootstrap counts say %r "
                 "valid replicates: the interval and the counts describe "
                 "different runs" % (label, ci.get("n_valid"), expect_n_valid))
    lo, hi = ci.get("lower"), ci.get("upper")
    if not _finite(lo) or not _finite(hi):
        e.append("%s must have finite endpoints: a non-finite interval is a "
                 "mechanical failure, never a classifiable result" % label)
    elif lo > hi:
        e.append("%s is inverted" % label)
    if ci.get("level") != SEALED_EXPECTATIONS["ci_level"]:
        e.append("%s.level must be the sealed 95" % label)
    if ci.get("method") != SEALED_EXPECTATIONS["ci_method"]:
        e.append("%s.method must be the sealed percentile interval" % label)
    return e


def _check_classification_matches_ci(ci, classification, boundary_b):
    """§5's partition, re-derived from the recorded interval.

    The validator does not trust the recorded classification: it recomputes
    which of the three states the recorded interval falls in and refuses a
    mismatch. That is what stops a verdict from being written next to an
    interval that does not support it.
    """
    b = SEALED_EXPECTATIONS["boundary_b"] if boundary_b is None else float(boundary_b)
    boundary = -b
    lo, hi = float(ci["lower"]), float(ci["upper"])
    if lo > boundary:
        want = "PRESERVATION_SUPPORTED"
    elif hi < boundary:
        want = "MATERIAL_DEGRADATION_SUPPORTED"
    else:
        want = "UNRESOLVED_INSUFFICIENT_PRECISION"
    if classification != want:
        return ["primary.classification %r does not follow from the recorded "
                "interval [%r, %r] against %r, which yields %r"
                % (classification, lo, hi, boundary, want)]
    return []


def require_valid(artifact, expect_execution_revision=None):
    """Validate and RAISE. Used on the persistence path, so an inconsistent
    record cannot be written by a caller that ignored a returned list."""
    errs = validate(artifact, expect_execution_revision)
    if errs:
        raise EvidenceSchemaError(
            "%d evidence-artifact violation(s): %s" % (len(errs), "; ".join(errs)))
    return artifact


# --------------------------------------------------------------------------- #
# persistence — explicit path, canonical bytes
# --------------------------------------------------------------------------- #
def write_artifact(path, artifact, expect_execution_revision=None):
    """Validate, then write canonical bytes to a caller-supplied path.

    Validation happens FIRST and raises, so a record that fails the schema is
    never written at all. The bytes are the canonical form plus a trailing
    newline, so two runs of the same study produce byte-identical files.
    """
    require_valid(artifact, expect_execution_revision)
    data = canonical_json(artifact) + "\n"
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(data)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def read_artifact(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


# --------------------------------------------------------------------------- #
# publication — atomic, with the file's identity recorded OUTSIDE the file
# --------------------------------------------------------------------------- #
# A file cannot contain its own sha256: embedding the hash changes the bytes the
# hash describes. Writing, hashing, embedding and rewriting produces a record
# whose stated file identity is the identity of a file that no longer exists —
# which is worse than recording nothing, because it looks authoritative.
#
# So the two identities are kept apart and named:
#   * `content_digest` lives INSIDE the artifact and pins the payload;
#   * `artifact_file_sha256` lives OUTSIDE it, in a sidecar provenance record,
#     and pins the exact published bytes.
#
# Publication is atomic: the bytes are written to a temporary path, fsynced,
# hashed, and only then renamed into place. A failure before the rename leaves
# no artifact at the final path at all, so a completed evidence artifact never
# becomes visible unless it was completely and verifiably written.
PROVENANCE_SUFFIX = ".provenance.json"
ARTIFACT_IDENTITY_CONVENTION = "FILE_SHA256_RECORDED_IN_EXTERNAL_PROVENANCE_RECORD"


class ArtifactProvenanceError(RuntimeError):
    """The artifact WAS published, but its external provenance was not written.

    Carries the provenance that could not be stored, so the caller can report
    what actually happened instead of implying the publication failed too.
    """

    def __init__(self, message, provenance):
        self.provenance = dict(provenance)
        super().__init__(message)


def provenance_path_for(path):
    return path + PROVENANCE_SUFFIX


def _atomic_replace(src, dst):
    """`os.replace` by another name, so a test can make publication fail.

    Not a switch: it is the same call. Naming it gives the failure-injection
    tests something to replace without reaching into `os` for the whole process.
    """
    os.replace(src, dst)


def publish_artifact(path, artifact, expect_execution_revision=None,
                     provenance_extra=None, tmp_path=None,
                     provenance_path=None):
    """Validate, write, fsync, hash, then ATOMICALLY publish. Returns provenance.

    Order matters at every step. Validation first, so an inconsistent record is
    never written anywhere. The temporary file is fsynced before it is hashed,
    and the hash is taken over the bytes read back from disk, so the recorded
    identity is the identity of what is actually stored rather than of what was
    intended. The rename is last, so the final path either does not exist or
    holds the complete, hashed artifact.
    """
    require_valid(artifact, expect_execution_revision)
    data = (canonical_json(artifact) + "\n").encode("utf-8")
    tmp = tmp_path or "%s.tmp-%d" % (path, os.getpid())
    prov_path = provenance_path or provenance_path_for(path)

    try:
        with open(tmp, "wb") as fh:
            fh.write(data)
            fh.flush()
            os.fsync(fh.fileno())
        with open(tmp, "rb") as fh:
            written = fh.read()
    except Exception:
        _discard(tmp)
        raise
    if written != data:
        _discard(tmp)
        raise EvidenceSchemaError(
            "the bytes read back from the temporary artifact differ from the "
            "bytes intended; nothing was published")
    file_sha256 = hashlib.sha256(written).hexdigest()

    try:
        _atomic_replace(tmp, path)
    except Exception:
        _discard(tmp)
        raise

    provenance = {
        "schema": {"name": SCHEMA_NAME + "-provenance", "version": SCHEMA_VERSION},
        "artifact_file": os.path.basename(path),
        "artifact_file_sha256": file_sha256,
        "artifact_file_bytes": len(data),
        "content_digest": artifact.get("content_digest"),
        "outcome_state": artifact.get("outcome_state"),
        "identity_convention": ARTIFACT_IDENTITY_CONVENTION,
    }
    if provenance_extra:
        provenance.update(provenance_extra)
    try:
        body = canonical_json(provenance) + "\n"
        with open(prov_path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body)
            fh.flush()
            os.fsync(fh.fileno())
    except Exception as exc:                          # noqa: BLE001
        raise ArtifactProvenanceError(
            "the evidence artifact was published at %s but its external "
            "provenance record could not be written: %r"
            % (os.path.basename(path), exc), provenance)
    return provenance


def _discard(path):
    try:
        if os.path.exists(path):
            os.remove(path)
    except OSError:
        pass


def read_provenance(path):
    with open(provenance_path_for(path), encoding="utf-8") as fh:
        return json.load(fh)


def verify_published(path, provenance=None):
    """Recompute the published file's sha256 and compare it to what was recorded.

    This is the check the old write-hash-embed-rewrite protocol could never
    pass, and it is the one an auditor actually wants: do the bytes on disk
    still hash to the identity the provenance claims?
    """
    prov = provenance if provenance is not None else read_provenance(path)
    with open(path, "rb") as fh:
        actual = hashlib.sha256(fh.read()).hexdigest()
    return actual == prov.get("artifact_file_sha256"), actual
