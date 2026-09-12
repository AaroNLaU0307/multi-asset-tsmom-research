"""X01 production orchestration — WIRING ONLY, STRUCTURALLY FAIL-CLOSED.

What this module is
-------------------
The path a future authorized run would take, in one place, in order. It wires
the accepted layers together and enforces the ordering the authoritative
sources fix. It contains **no scientific logic of its own** — no Sharpe, no ΔS,
no bootstrap, no classification, no signal, no roll, no cost — because all of
that is single-source in the bound construction and inference modules and is
called, never re-derived.

The four-step pre-execution sequence, verbatim from `x01_runner.py::cmd_execute`
--------------------------------------------------------------------------------
    1. pass preflight;
    2. record the exposure event and the A1/S1/S2 attempt classifications,
       plus E's prospective ETF +1;
    3. read the then-current authoritative cumulative Databento state
       (never hard-code 14 -> 17);
    4. record the child seed streams by spawn_key and state fingerprint;
    ONLY THEN construct anything, and only then read an output.

That ordering is the reason this module exists as a gate rather than a script.
Step 2 puts the exposure and trial records BEFORE any construction: they are
prospective commitments, made while no outcome exists, which is what makes them
worth anything. A run that constructed first and recorded afterwards would be
recording a decision it had already seen the answer to.

Five things this module keeps apart
-----------------------------------
Owner authorization · target data read · target construction · outcome exposure ·
evidence persistence. They happen at different points, they are gated
separately, and none implies another. In particular an authorization record is
not an outcome and creates no exposure by existing; the exposure event is bound
to step 2, where the commitment is actually made.

Why nothing here can touch real data today
------------------------------------------
Every boundary the run would cross is an injected adapter, and every default
adapter REFUSES. There is no code path from this module to the frozen panels:
the default data adapter raises, the default authorization provider is not even
consulted, and the default recorder writes nothing. A test supplies synthetic
adapters; a real run would supply real ones, and only alongside a committed,
active, exactly-bound authorization record under the Owner's D1–D6 mechanism in
`x01_authorization.py`. No such record exists.
"""

from __future__ import annotations

import hashlib
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

# The ordered stages. `STAGES_BEFORE_CONSTRUCTION` is the closed set that must
# ALL have passed before a single target constructor may be called; the
# fail-closed tests assert exactly that.
STAGE_PREFLIGHT = "preflight"
STAGE_AUTHORIZATION = "authorization"
STAGE_EXPOSURE_RECORD = "exposure_and_trial_record"
STAGE_CUMULATIVE_STATE = "cumulative_databento_state"
STAGE_SEED_RECORD = "seed_stream_record"
STAGE_SEALED_SAMPLE = "sealed_sample"
STAGE_CONSTRUCTION = "construction"
STAGE_INFERENCE = "inference"
STAGE_ARTIFACT = "evidence_artifact"
STAGE_PERSIST = "persistence"
STAGE_PROVENANCE = "external_provenance"

STAGES_BEFORE_CONSTRUCTION = (
    STAGE_PREFLIGHT, STAGE_AUTHORIZATION, STAGE_EXPOSURE_RECORD,
    STAGE_CUMULATIVE_STATE, STAGE_SEED_RECORD, STAGE_SEALED_SAMPLE)

# §10.1's closed attempt set, declared once so nothing downstream re-types it.
# The Databento contribution is DERIVED from the set, never written as a
# literal: a fourth arm would change it here and everywhere at once, and an
# arm removed could not leave a stale `3` behind.
X01_VARIANT_ATTEMPTS = (
    {"arm": "A1", "object": "primary futures F", "contribution": 1},
    {"arm": "S1", "object": "construction-sensitivity F", "contribution": 1},
    {"arm": "S2", "object": "roll-rule-sensitivity F", "contribution": 1},
)
X01_DATABENTO_CONTRIBUTION = sum(a["contribution"] for a in X01_VARIANT_ATTEMPTS)
# E is one prospective attempt on the ETF panel — a DIFFERENT sample. It is
# counted on its own axis and never enters the Databento total.
X01_ETF_PROSPECTIVE_CONTRIBUTION = 1

SEALED_FIRST_MONTH_END = "2011-07-31"
SEALED_LAST_MONTH_END = "2026-05-31"
SEALED_N = 179
SEALED_MAPPED_ETFS = ("USO", "UNG", "GLD", "DBA")


class OrchestrationRefused(RuntimeError):
    """A gate did not open. No constructor was called and nothing was computed."""

    def __init__(self, stage, reason, detail=None):
        self.stage = stage
        self.reason = reason
        self.detail = list(detail or [])
        super().__init__("%s: %s" % (stage, reason))


class OrchestrationMechanicalFailure(RuntimeError):
    """A break part-way through. Never a scientific outcome.

    `failure_class` carries the ORIGINAL exception type through the guard. The
    wrapper's own name says only that something broke; the class underneath is
    what tells an operator whether it was a disk, a permission or a panel.
    """

    def __init__(self, stage, reason, detail=None, failure_class=None):
        self.stage = stage
        self.reason = reason
        self.detail = list(detail or [])
        self.failure_class = failure_class
        super().__init__("%s: %s" % (stage, reason))


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


_LAYERS = {}


def layers():
    """Load the construction, inference, evidence, authorization and runner layers.

    Lazy, so importing this module reads nothing and computes nothing. These are
    the single source of every scientific rule; this module only calls them.
    """
    if _LAYERS:
        return _LAYERS
    _LAYERS["construction"] = _load(
        "x01_orch_tc", os.path.join(HERE, "x01_target_construction.py"))
    _LAYERS["inference"] = _load(
        "x01_orch_inf", os.path.join(HERE, "x01_inference.py"))
    _LAYERS["evidence"] = _load(
        "x01_orch_ev", os.path.join(HERE, "x01_evidence.py"))
    _LAYERS["authorization"] = _load(
        "x01_orch_auth", os.path.join(HERE, "x01_authorization.py"))
    _LAYERS["runner"] = _load(
        "x01_orch_rn", os.path.join(HERE, "x01_runner.py"))
    return _LAYERS


# --------------------------------------------------------------------------- #
# ITEM 12 — the authorization gate.
#
# The MECHANISM is now Owner policy. Aaron sealed it as D1–D6: a machine-
# readable record in the append-only `ops/EXECUTION_AUTHORIZATIONS.md`, valid
# only in committed git state, ONE_SHOT, bound to exactly seven identities, not
# itself an exposure event, and permanently consumed at durable step 2. It lives
# in `x01_authorization.py`; this module only consults it.
#
# `AUTHORIZATION_MECHANISM_DECLARED` is a statement about POLICY, not about
# permission. The default provider below still has nothing to consult and still
# refuses, which is why the shipped repository cannot execute: a declared
# mechanism with no committed record is exactly as closed as no mechanism.
# --------------------------------------------------------------------------- #
AUTHORIZATION_MECHANISM_DECLARED = True
AUTHORIZATION_MECHANISM_NOTE = (
    "No execution-authorization provider was supplied to this run. The Owner "
    "mechanism (D1-D6) is declared and implemented in x01_authorization.py, but "
    "an unsupplied provider is not consulted and cannot be assumed permissive; "
    "a passing preflight is not authorization and cannot become one.")


class NoAuthorizationMechanism(object):
    """The default provider. Refuses, because there is nothing to consult.

    It is not the Owner mechanism and does not pretend to be: it is what a run
    gets when no provider was wired in at all. `declared = False` keeps it out
    of the gate entirely, so "nothing was consulted" and "the mechanism said no"
    stay distinguishable — only the first is true of the shipped default.
    """

    declared = False

    def authorization_for(self, execution_identity):
        return None, ("no execution-authorization provider was supplied; a "
                      "passing preflight is not authorization and cannot become "
                      "one")


class RefusingDataAdapter(object):
    """The default target-data boundary. Every read refuses.

    A build task must have no path to the frozen panels, and this is where that
    is enforced rather than promised.
    """

    def etf_panel(self):
        raise OrchestrationRefused(
            STAGE_CONSTRUCTION, "the default data adapter refuses every target "
            "read; a real run must inject an authorized adapter")

    def futures_panels(self):
        raise OrchestrationRefused(
            STAGE_CONSTRUCTION, "the default data adapter refuses every target "
            "read; a real run must inject an authorized adapter")


class RefusingRecorder(object):
    """The default governance recorder. Writes nothing and refuses.

    Step 2 and step 4 of the sealed sequence are real appends to append-only
    ledgers. A build task must not make them, so the default recorder refuses
    and the tests inject a scratch one.
    """

    def record_exposure_and_attempts(self, payload):
        raise OrchestrationRefused(
            STAGE_EXPOSURE_RECORD, "the default recorder refuses to append a real "
            "exposure or trial record")

    def read_cumulative_databento_state(self):
        raise OrchestrationRefused(
            STAGE_CUMULATIVE_STATE, "the default recorder cannot read the "
            "authoritative cumulative state")

    def record_seed_streams(self, payload):
        raise OrchestrationRefused(
            STAGE_SEED_RECORD, "the default recorder refuses to append a real "
            "seed-stream record")


class TargetAdapterCallCounter(object):
    """Counts every target constructor call. The fail-closed tests read this.

    An ordering claim is only worth what a counter says: "no constructor ran"
    is checked, not asserted.
    """

    def __init__(self):
        self.calls = []

    def note(self, what):
        self.calls.append(what)

    @property
    def n(self):
        return len(self.calls)


# --------------------------------------------------------------------------- #
# the sealed sample, constructed by orchestration and not merely trusted
# --------------------------------------------------------------------------- #
def sealed_evaluation_index():
    """`2011-07-31 … 2026-05-31`, 179 month-ends, built from the sealed endpoints.

    `N179_ENFORCEMENT_LOCATION = BOTH`: orchestration CONSTRUCTS the calendar
    here and the inference boundary refuses independently. Neither relies on the
    other noticing, because a sample defect that only inference caught would
    already have cost a target read.
    """
    import pandas as pd

    idx = pd.date_range(SEALED_FIRST_MONTH_END, SEALED_LAST_MONTH_END, freq="ME")
    if len(idx) != SEALED_N:
        raise OrchestrationRefused(
            STAGE_SEALED_SAMPLE,
            "the sealed endpoints no longer span %d month-ends; got %d"
            % (SEALED_N, len(idx)))
    return idx


def calendar_digest(index):
    """A deterministic fingerprint of the evaluated calendar.

    Recorded in the artifact so the sample is reproducible rather than merely
    counted: two runs that both say "179" but evaluated different months have
    different digests.
    """
    body = "\n".join(str(d.date()) for d in index)
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def enforce_sealed_sample(e_net, f_net):
    """Both legs must carry exactly the sealed calendar. No repair, ever.

    Nothing is dropped, intersected, back-filled or re-ordered — the sealed
    contract requires all 179 paired months present, so anything else is a
    different study and is refused here before inference is even called.
    """
    import numpy as np
    import pandas as pd

    want = sealed_evaluation_index()
    problems = []
    for name, s in (("E", pd.Series(e_net)), ("F", pd.Series(f_net))):
        if s.index.has_duplicates:
            problems.append("%s carries duplicate month-ends" % name)
        if not s.index.is_monotonic_increasing:
            problems.append("%s is not in ascending month-end order" % name)
        if not s.index.equals(want):
            problems.append(
                "%s is not the sealed calendar: %d supplied, %d sealed month(s) "
                "missing, %d unsealed month(s) present"
                % (name, len(s.index), len(want.difference(s.index)),
                   len(s.index.difference(want))))
        elif not np.isfinite(s.to_numpy(dtype="float64")).all():
            problems.append("%s has a non-finite observation in the sealed sample"
                            % name)
    if problems:
        raise OrchestrationRefused(
            STAGE_SEALED_SAMPLE, "the constructed sample is not the sealed "
            "evaluation calendar", problems)
    return want


# --------------------------------------------------------------------------- #
# the run
# --------------------------------------------------------------------------- #
class ExecutionPlan(object):
    """Everything a run needs, all of it injected. No default reaches real data."""

    def __init__(self, data_adapter=None, authorization_provider=None,
                 recorder=None, artifact_path=None, clock=None,
                 counter=None, preflight_fn=None, run_id="unset",
                 capital=1.0, cost_multiplier=1.0, artifact_tmp_path=None,
                 artifact_provenance_path=None, repo=None):
        self.data = data_adapter or RefusingDataAdapter()
        self.authorization = authorization_provider or NoAuthorizationMechanism()
        self.recorder = recorder or RefusingRecorder()
        self.artifact_path = artifact_path
        self.clock = clock or (lambda: "UNSET")
        self.counter = counter or TargetAdapterCallCounter()
        self.preflight_fn = preflight_fn
        self.run_id = run_id
        self.capital = capital
        self.cost_multiplier = cost_multiplier
        self.artifact_tmp_path = artifact_tmp_path
        self.artifact_provenance_path = artifact_provenance_path
        self.repo = repo or REPO
        self.publication = None
        self.stages_passed = []


def execution_identity(plan):
    """The identity a run and its authorization are bound to.

    Read from the manifest and git rather than declared, so an authorization can
    be checked against the revision that would actually execute.
    """
    L = layers()
    rn = L["runner"]
    auth = L["authorization"]
    import json

    # Repo-relative rather than global, so the whole path can be stood up in a
    # throwaway repository. It changes nothing for a real run, where the plan's
    # repo IS this repo — and it is what lets the production entrypoint be
    # tested end to end without a frozen panel or a real authorization.
    repo = getattr(plan, "repo", None) or REPO
    manifest_path = os.path.join(repo, "research", "extensions", "x01",
                                 "X01_EXECUTION_MANIFEST.json")
    with open(manifest_path, encoding="utf-8") as fh:
        man = json.load(fh)
    head = rn.head(repo)
    tcb = man.get("target_construction_binding") or {}
    infb = man.get("inference_binding") or {}
    return {
        "research_id": "TSMOM-EXT-001",
        # D4 binds the run itself, so the run has to say which one it is.
        "run_id": plan.run_id,
        # D4's "execution-infrastructure Git revision". Deliberately not HEAD:
        # the authorization record is itself committed, and a commit cannot
        # contain its own hash. While any infrastructure file is uncommitted or
        # differs from its committed bytes this is an unmatchable sentinel, so
        # no authorization can match and the repository cannot execute.
        "execution_infrastructure_revision":
            auth.execution_infrastructure_revision(repo),
        "prereg_sha256": man["sealed_contract"]["prereg_sha256_reviewed_pin"],
        "prereg_seal_revision": man["sealed_contract"]["seal_revision"],
        "construction_binding_revision": tcb.get("accepted_implementation_revision"),
        "construction_sha256": next(
            (m["sha256_at_freeze"] for m in tcb.get("modules", [])
             if m["path"].endswith("x01_target_construction.py")), None),
        "inference_binding_revision": infb.get("accepted_implementation_revision"),
        "inference_sha256": next(
            (m["sha256_at_freeze"] for m in infb.get("modules", [])
             if m["path"].endswith("x01_inference.py")), None),
        "runner_revision": man["runner_base"]["runner_base_revision"],
        "manifest_sha256": rn.lf_sha256(manifest_path),
        "execution_revision": head,
        "input_pins": [{"path": i["path"], "sha256": i["sha256"],
                        "hash_convention": i["hash_convention"]}
                       for i in man["inputs"]],
        "carry_s2_dependency": {
            "revision": man["carry_s2_dependency"]["revision"],
            "sha256": man["carry_s2_dependency"]["sha256"]},
    }


def _gate_preflight(plan):
    """Step 1 — pass preflight. Seal, bindings and every input pin, in one gate."""
    L = layers()
    pf = plan.preflight_fn or (lambda: L["runner"].preflight())
    r = pf()
    if not getattr(r, "ok", False):
        raise OrchestrationRefused(
            STAGE_PREFLIGHT, "preflight did not pass", list(getattr(r, "reasons", [])))
    return r


def _gate_authorization(plan, identity):
    """Owner authorization. Separate from preflight, and never implied by it.

    A passing preflight proves byte integrity. It says nothing about permission,
    and this gate exists so the two can never be confused.

    D5: this gate is read-only with respect to exposure and trial accounting.
    Nothing here appends to any exposure ledger or increments any attempt count;
    that begins at step 2, below, and only there.
    """
    provider = plan.authorization
    if not getattr(provider, "declared", False):
        raise OrchestrationRefused(
            STAGE_AUTHORIZATION, AUTHORIZATION_MECHANISM_NOTE)
    record, why = provider.authorization_for(identity)
    if not record:
        raise OrchestrationRefused(
            STAGE_AUTHORIZATION, why or "no Owner authorization for this execution "
            "identity")
    # D6/§9: an authorization that cannot be marked consumed must not be spent.
    # A provider with no lifecycle session could authorize a run whose
    # consumption nobody records, which is the one-shot rule with the enforcement
    # removed — so the absence of the capability is itself a refusal.
    if not hasattr(provider, "open_session"):
        raise OrchestrationRefused(
            STAGE_AUTHORIZATION,
            "the authorization provider offers no consumption session, so a "
            "ONE_SHOT authorization could not be marked consumed (D3/D6)")
    if not isinstance(record, dict) or not record.get("authorization_id") \
            or record.get("run_id") != plan.run_id:
        raise OrchestrationRefused(
            STAGE_AUTHORIZATION,
            "the authorization reference does not identify this run: it names "
            "run_id %r and this run is %r"
            % (record.get("run_id") if isinstance(record, dict) else None,
               plan.run_id))
    auth = layers()["authorization"]
    try:
        session = provider.open_session(record)
    except auth.AuthorizationError as exc:
        raise OrchestrationRefused(
            STAGE_AUTHORIZATION,
            "the ONE_SHOT lifecycle refused to open a session for this run",
            [str(exc)])
    return record, session


def _bookkeep(session, what, *args):
    """Call one lifecycle method and report rather than explode.

    A failure to WRITE the bookkeeping is itself a mechanical problem, and it
    must not be able to escape `run()` as an uncaught exception and lose the
    artifact — but it also must not be swallowed, because an unresolved
    write-ahead marker is precisely what makes an authorization indeterminate.
    """
    try:
        getattr(session, what)(*args)
        return None
    except Exception as exc:                          # noqa: BLE001
        return "authorization bookkeeping %s failed: %r" % (what, exc)


def _commit_step2(plan, identity, session, governance):
    """Step 2, wrapped in D6's consumption bookkeeping. No new scientific step.

    The sealed four-step sequence is untouched: step 2 still happens exactly
    where it always did, before any construction. What surrounds it is the
    write-ahead marker and its resolution — governance bookkeeping around the
    durable step-2 boundary, which is where §10 puts it.
    """
    auth = layers()["authorization"]
    problems = []
    try:
        session.begin_step2()
    except auth.AuthorizationError as exc:
        # A lost race, or a stale validation, or an authorization consumed since
        # it was checked. Nothing has been committed and no constructor has run,
        # so this is a REFUSAL, not a partial execution.
        raise OrchestrationRefused(
            STAGE_AUTHORIZATION,
            "the ONE_SHOT claim on this authorization was not obtained, so this "
            "run must not enter step 2", [str(exc)])
    except FATAL_PROGRAMMER_ERRORS:
        raise
    except Exception as exc:                          # noqa: BLE001
        raise OrchestrationMechanicalFailure(
            STAGE_EXPOSURE_RECORD,
            "the write-ahead authorization marker could not be recorded, so "
            "step 2 was not attempted",
            ["%s: %s" % (type(exc).__name__, exc)],
            failure_class=type(exc).__name__) from exc
    try:
        ref = _step2_exposure(plan, identity)
    except auth.Step2NotDurable as exc:
        # The ONLY branch that leaves the authorization usable: the recorder
        # PROVED nothing durable was written. §7's before-step-2 rule.
        problems.append(_bookkeep(session, "step2_definitely_not_written",
                                  repr(exc)))
        governance["authorization_status"] = session.status
        governance["authorization_consumed"] = False
        raise OrchestrationMechanicalFailure(
            STAGE_EXPOSURE_RECORD,
            "the exposure and trial commitment failed with proof that nothing "
            "durable was written; the authorization was NOT consumed",
            [repr(exc)] + [p for p in problems if p])
    except BaseException as exc:                      # noqa: BLE001
        # Everything else is ambiguous by default: we do not know whether the
        # commitment reached durable storage, and D6 makes unknown = spent.
        problems.append(_bookkeep(session, "step2_ambiguous", repr(exc)))
        governance["authorization_status"] = session.status
        governance["authorization_consumed"] = True
        governance["authorization_detail"] = [p for p in problems if p]
        if isinstance(exc, (OrchestrationRefused, OrchestrationMechanicalFailure)) \
                or isinstance(exc, FATAL_PROGRAMMER_ERRORS):
            raise
        # An ordinary adapter or storage failure. It is recorded as a mechanical
        # failure rather than raised, so the spent authorization and the
        # ambiguous exposure state survive in an artifact.
        raise OrchestrationMechanicalFailure(
            STAGE_EXPOSURE_RECORD,
            "the exposure and trial commitment failed and its persistence is "
            "indeterminate",
            ["%s: %s" % (type(exc).__name__, exc)],
            failure_class=type(exc).__name__) from exc
    problems.append(_bookkeep(session, "step2_durably_completed", ref))
    governance["authorization_status"] = session.status
    governance["authorization_consumed"] = True
    if any(problems):
        governance["authorization_detail"] = [p for p in problems if p]
    return ref


def _step2_exposure(plan, identity):
    """Step 2 — the prospective exposure event and the attempt classifications.

    Made BEFORE construction, which is the whole reason it counts: §10.1's `+3`
    (the primary F, S1's F and S2's F) and E's prospective ETF `+1` are
    commitments taken while no outcome exists.
    """
    payload = {
        "kind": "X01_PRE_EXECUTION_EXPOSURE_AND_ATTEMPTS",
        "execution_identity": identity,
        "variant_attempts": [dict(a) for a in X01_VARIANT_ATTEMPTS],
        "databento_contribution": X01_DATABENTO_CONTRIBUTION,
        "etf_panel_prospective_attempt": {
            "arm": "E", "contribution": X01_ETF_PROSPECTIVE_CONTRIBUTION,
            "sample": "dataset.yfinance.multi-asset-etf-panel",
            "convention": "E_COUNTS_AS_ONE_PROSPECTIVE_ATTEMPT"},
        "not_attempts": ["bootstrap replicates of any arm",
                         "crisis-window slices of an already-constructed series"],
        "recorded_before_any_construction": True,
    }
    ref = plan.recorder.record_exposure_and_attempts(payload)
    if not ref:
        raise OrchestrationMechanicalFailure(
            STAGE_EXPOSURE_RECORD, "the exposure and attempt record returned no "
            "reference, so nothing can be cited as having been recorded")
    return ref


# The only exceptions allowed to escape `run()`. They are programmer errors —
# a typo, a bad call, an impossible state — and turning one into a tidy
# EXECUTION_MECHANICAL_FAILURE record would hide a defect in this module behind
# a governance-shaped artifact. Everything else is infrastructure: an adapter,
# a disk, a ledger, a panel. Those are recorded, never raised.
FATAL_PROGRAMMER_ERRORS = (SyntaxError, NameError, ImportError, IndentationError,
                           SystemExit, KeyboardInterrupt)


def _guard(stage, reason, fn, *args, **kwargs):
    """Run one stage; convert any ordinary failure into a structured one.

    An exception that escapes `run()` destroys the evidence of its own run: the
    caller gets a traceback and no artifact, so nothing records that an
    authorization was spent, an exposure was committed, or how far the attempt
    got. That is the one outcome a governed execution cannot afford.
    """
    try:
        return fn(*args, **kwargs)
    except (OrchestrationRefused, OrchestrationMechanicalFailure):
        raise
    except FATAL_PROGRAMMER_ERRORS:
        raise
    except Exception as exc:                          # noqa: BLE001
        raise OrchestrationMechanicalFailure(
            stage, reason, ["%s: %s" % (type(exc).__name__, exc)],
            failure_class=type(exc).__name__) from exc


def _step3_cumulative_state(plan):
    """Step 3 — read the then-current cumulative Databento state.

    Read at execution and never hard-coded: §10.1 deletes the old `14 → 17`
    string precisely because cross-project history can move between seal and
    execution, and the resulting total forces DSR recomputation against the
    total actually obtaining.

    The value read here ALREADY INCLUDES this run
    ---------------------------------------------
    Step 3 happens after step 2, and step 2 durably appends this run's A1, S1
    and S2 rows to the authoritative §6.1 register. The fresh read therefore
    returns the post-commitment total, and adding the contribution again would
    publish it twice — 14 would become 20 rather than 17.

    The earlier code did exactly that, because it was written when step 2
    recorded only the exposure row and the register was advanced by hand
    afterwards. That assumption is obsolete, so the seam is repaired rather
    than the arithmetic patched: `resulting_total` IS the authoritative total,
    and the current run's contribution is reported beside it as its own named
    quantity, never summed into it.
    """
    state = plan.recorder.read_cumulative_databento_state()
    if not isinstance(state, dict) or not isinstance(state.get("cumulative"), int):
        raise OrchestrationMechanicalFailure(
            STAGE_CUMULATIVE_STATE, "the authoritative cumulative Databento state "
            "was not readable as an integer total")
    return {
        "cumulative_at_execution": state["cumulative"],
        "source": state.get("source"),
        # Distinct quantities, unambiguously named. The first is what THIS run
        # contributed; the second is the authoritative total that already
        # contains it.
        "current_run_databento_contribution": X01_DATABENTO_CONTRIBUTION,
        "authoritative_total_after_step2": state["cumulative"],
        "resulting_total": state["cumulative"],
        "current_run_etf_contribution": X01_ETF_PROSPECTIVE_CONTRIBUTION,
        "etf_contribution_sample": "dataset.yfinance.multi-asset-etf-panel",
        "note": ("read at execution, AFTER step 2 durably registered this run's "
                 "attempts, so the total already includes them; the current-run "
                 "contribution is recorded separately and is never added again. "
                 "The ETF attempt sits on a different sample and is not part of "
                 "this total"),
    }


def _step4_seed_streams(plan):
    """Step 4 — record the child seed streams by spawn_key and state fingerprint.

    `.entropy` cannot identify the children (all three report 7), so the record
    is the spawn_key plus a generated-state fingerprint, taken from the runner's
    frozen protocol rather than re-derived here.
    """
    L = layers()
    protocol = L["runner"].seed_protocol()
    if not protocol.get("child_streams"):
        raise OrchestrationMechanicalFailure(
            STAGE_SEED_RECORD, "the seed protocol produced no child streams")
    ref = plan.recorder.record_seed_streams(protocol)
    if not ref:
        raise OrchestrationMechanicalFailure(
            STAGE_SEED_RECORD, "the seed-stream record returned no reference")
    return protocol, ref


def _construct_all(plan):
    """Construction, entirely by CALLING the bound layer. No logic here."""
    L = layers()
    tc = L["construction"]
    plan.counter.note("etf_panel")
    etf = plan.data.etf_panel()
    plan.counter.note("futures_panels")
    settle, oi, meta = plan.data.futures_panels()

    plan.counter.note("construct_E")
    e = tc.construct_E(etf)
    arms = {"E": e}
    for arm in ("A1", "S1", "S2"):
        plan.counter.note("construct_futures_leg:%s" % arm)
        arms[arm] = tc.construct_futures_leg(
            settle, oi, meta, arm=arm, capital=plan.capital,
            cost_multiplier=plan.cost_multiplier)
    return arms


def _infer_all(plan, arms, index):
    """Inference, entirely by CALLING the bound layer. No statistic is re-derived."""
    L = layers()
    inf = L["inference"]
    e_net = arms["E"].net.loc[index]
    primary = inf.run_primary(e_net, arms["A1"].net.loc[index])
    secondary = {a: inf.run_secondary(a, e_net, arms[a].net.loc[index])
                 for a in ("S1", "S2")}
    windows = inf.crisis_windows(e_net, arms["A1"].net.loc[index],
                                 evaluation_index=index)
    diag = inf.path_diagnostics(
        e_net, arms["A1"].net.loc[index],
        etf_monthly=arms["E"].diagnostics.monthly_returns,
        futures_monthly=arms["A1"].diagnostics.monthly_returns,
        signal_e=arms["E"].diagnostics.composite_signal[SEALED_MAPPED_ETFS[0]],
        signal_f=arms["A1"].diagnostics.composite_signal[SEALED_MAPPED_ETFS[0]],
        turnover_e=arms["E"].turnover,
        turnover_f=arms["A1"].diagnostics.identity_turnover,
        cost_e=arms["E"].cost, cost_f=arms["A1"].cost,
        evaluation_index=index)
    return primary, secondary, windows, diag


def _primary_block(primary):
    L = layers()
    inf = L["inference"]
    c = primary.config
    blk = {
        "sharpe_e": primary.sharpes.sharpe_e,
        "sharpe_f": primary.sharpes.sharpe_f,
        "delta_s": primary.delta_s,
        "boundary_b": primary.boundary_b,
        "boundary": primary.boundary,
        "bootstrap": {
            "family": c.family,
            "expected_block_length_months": c.expected_block_length_months,
            "replications_attempted": c.replications,
            "ci_level": c.ci_level,
            "ci_method": c.ci_method,
            "percentile_interpolation": c.percentile_interpolation,
            "valid_replicate_floor": c.valid_replicate_floor,
            "min_distinct_months": c.min_distinct_months,
            "master_seed": c.master_seed,
            "arm_order": list(c.arm_order)},
        "bootstrap_counts": {
            "attempted": primary.counts.attempted,
            "valid": primary.counts.valid,
            "discarded": primary.counts.discarded,
            "discarded_too_few_distinct_months":
                primary.counts.discarded_too_few_distinct_months,
            "discarded_zero_std_e": primary.counts.discarded_zero_std_e,
            "discarded_zero_std_f": primary.counts.discarded_zero_std_f},
        "discard_reasons": ["too_few_distinct_calendar_months",
                            "zero_standard_deviation_in_E",
                            "zero_standard_deviation_in_F"],
    }
    if primary.classification != inf.PROCEDURE_FAILURE:
        blk["ci"] = {"lower": primary.ci.lower, "upper": primary.ci.upper,
                     "level": primary.ci.level, "method": primary.ci.method,
                     "n_valid": primary.ci.n_valid}
        blk["classification"] = primary.classification
    return blk


def _secondary_block(secondary):
    L = layers()
    inf = L["inference"]
    out = {"bh_fdr_required": False,
           "materiality_gate": inf.SECONDARY_MATERIALITY_GATE,
           "note": ("§8.3: reported side by side with the primary; no comparison "
                    "test between arms is computed and no verdict is attached")}
    for arm, res in secondary.items():
        out[arm] = {
            "delta_s": res.delta_s,
            "sharpe_e": res.sharpes.sharpe_e,
            "sharpe_f": res.sharpes.sharpe_f,
            "ci": {"lower": res.ci.lower, "upper": res.ci.upper,
                   "level": res.ci.level, "method": res.ci.method,
                   "n_valid": res.ci.n_valid},
            "role": res.role,
            "promotion_power": res.promotion_power,
            "bootstrap_counts": {"attempted": res.counts.attempted,
                                 "valid": res.counts.valid,
                                 "discarded": res.counts.discarded}}
    return out


def _diagnostics_block(windows, diag):
    return {
        "crisis_windows": [
            {"name": w.name, "n_months": w.n_months, "month_ends": w.month_ends,
             "sharpe_e": w.sharpe_e, "sharpe_f": w.sharpe_f,
             "delta_s": w.delta_s, "role": w.role} for w in windows],
        "pair_correlations": diag.pair_correlations,
        "tracking_error_monthly": diag.tracking_error_monthly,
        "tracking_error_annualised": diag.tracking_error_annualised,
        "max_abs_d": diag.max_abs_d,
        "mean_d": diag.mean_d,
        "sign_agreement": diag.sign_agreement,
        "turnover_e": diag.turnover_e,
        "turnover_f": diag.turnover_f,
        "realised_cost_e": diag.realised_cost_e,
        "realised_cost_f": diag.realised_cost_f,
        "role": diag.role,
    }


def _mechanical(ev, identity, governance, run_instance, reason, stage,
                exc=None, detail=None, sample=None, arms=None,
                failure_class=None):
    """One structured mechanical-failure record, with every field named.

    Backlog C: the previous call site passed the detail list positionally into
    `sample`, so a construction failure recorded a Python repr where the sample
    block belonged and left `failure_detail` empty. Every field here is keyword
    only at the call sites below.
    """
    gov = dict(governance)
    gov["failure_class"] = failure_class or (
        type(exc).__name__ if exc is not None else "OrchestrationMechanicalFailure")
    return ev.mechanical_failure(identity, gov, run_instance, reason, stage,
                                 sample=sample, arms=arms,
                                 detail=list(detail or []))


def _constructed_sample(arms, index):
    """What was ACTUALLY constructed, for a failure after construction began.

    A post-construction failure must not report the sealed sample as though it
    had been evaluated, and must not report nothing at all: the first is a
    claim the run did not earn, the second denies that targets were read.
    """
    import numpy as np
    import pandas as pd

    out = {"first_month_end": SEALED_FIRST_MONTH_END,
           "last_month_end": SEALED_LAST_MONTH_END,
           "expected_n": SEALED_N,
           "evaluated_n": 0,
           "calendar_digest": None,
           "missingness_state":
               "SEALED_SAMPLE_NOT_SATISFIED_AFTER_CONSTRUCTION"}
    for name, arm in (("e", "E"), ("f", "A1")):
        try:
            s = pd.Series(arms[arm].net).reindex(index)
            out["constructed_finite_months_%s" % name] = int(
                np.isfinite(s.to_numpy(dtype="float64")).sum())
        except Exception:                             # noqa: BLE001
            out["constructed_finite_months_%s" % name] = None
    return out


def _constructed_arms(arms, protocol=None):
    blk = {}
    for a in ("E", "A1", "S1", "S2"):
        try:
            blk[a] = {"arm": a, "months": int(len(arms[a].net))}
        except Exception:                             # noqa: BLE001
            blk[a] = {"arm": a, "months": None}
    if protocol is not None:
        blk["seed_protocol"] = protocol
    return blk


def run(plan):
    """The whole path, in the authoritative order, fail-closed at every gate.

    Returns a finished evidence artifact in one of the four states. It never
    returns a scientific verdict for a mechanical problem: a refused gate yields
    EXECUTION_REFUSED, a break yields EXECUTION_MECHANICAL_FAILURE, and an
    inference procedure failure yields its own state with the counts and no
    classification.
    """
    L = layers()
    ev = L["evidence"]
    run_instance = {"run_id": plan.run_id, "generated_utc": plan.clock()}
    identity, governance = {"research_id": "TSMOM-EXT-001"}, {}

    try:
        identity = execution_identity(plan)
    except Exception as exc:                      # noqa: BLE001
        return ev.refused(identity, {"preflight_result": "NOT_REACHED"},
                          run_instance,
                          "the execution identity could not be established",
                          STAGE_PREFLIGHT, [repr(exc)])

    def passed(stage):
        """Mark a stage complete and keep the last one nameable.

        §7 requires a post-step-2 failure to record the last successfully
        completed orchestration stage, so it is maintained as the run goes
        rather than reconstructed afterwards.
        """
        plan.stages_passed.append(stage)
        governance["last_completed_stage"] = stage

    # ---- the gates, in order ------------------------------------------------
    try:
        pf = _guard(STAGE_PREFLIGHT, "preflight could not be evaluated",
                    _gate_preflight, plan)
        passed(STAGE_PREFLIGHT)
        governance["preflight_result"] = "PASS"
        governance["preflight_checks"] = len(getattr(pf, "checks", []))

        auth, session = _guard(STAGE_AUTHORIZATION,
                               "the Owner authorization could not be evaluated",
                               _gate_authorization, plan, identity)
        passed(STAGE_AUTHORIZATION)
        governance["authorization_reference"] = auth
        governance["authorization_id"] = auth["authorization_id"]
        governance["authorization_status"] = session.status
        governance["authorization_consumed"] = False
        # D5: the exposure axis has not moved yet, and says so.
        governance["exposure_state"] = "NOT_YET_COMMITTED_AUTHORIZATION_IS_NOT_EXPOSURE"

        exposure_ref = _commit_step2(plan, identity, session, governance)
        passed(STAGE_EXPOSURE_RECORD)
        governance["exposure_record_reference"] = exposure_ref
        governance["trial_accounting_reference"] = exposure_ref
        governance["exposure_state"] = "COMMITTED_AT_STEP_2"

        cumulative = _guard(STAGE_CUMULATIVE_STATE,
                            "the authoritative cumulative Databento state "
                            "could not be read",
                            _step3_cumulative_state, plan)
        passed(STAGE_CUMULATIVE_STATE)
        governance["cumulative_databento_state"] = cumulative

        protocol, seed_ref = _guard(STAGE_SEED_RECORD,
                                    "the child seed streams could not be "
                                    "recorded", _step4_seed_streams, plan)
        passed(STAGE_SEED_RECORD)
        governance["seed_record_reference"] = seed_ref

        index = _guard(STAGE_SEALED_SAMPLE,
                       "the sealed evaluation calendar could not be constructed",
                       sealed_evaluation_index)
        passed(STAGE_SEALED_SAMPLE)
    except OrchestrationRefused as exc:
        governance.setdefault("preflight_result",
                              "PASS" if STAGE_PREFLIGHT in plan.stages_passed
                              else "REFUSE")
        return ev.refused(identity, governance, run_instance,
                          exc.reason, exc.stage, exc.detail)
    except OrchestrationMechanicalFailure as exc:
        return _mechanical(ev, identity, governance, run_instance, exc.reason,
                           exc.stage, detail=exc.detail,
                           failure_class=getattr(exc, "failure_class", None))

    # ---- only now may a constructor be called ------------------------------
    #
    # B5. Past this line EXECUTION_REFUSED is no longer available. A refusal
    # means a gate did not open and nothing was constructed; once target
    # constructors have run, that is simply false, and a record saying it would
    # deny that an authorization was spent and that the targets were read. From
    # here every mechanical problem is EXECUTION_MECHANICAL_FAILURE, and the
    # only other legitimate state is the sealed inference's own
    # INFERENCE_PROCEDURE_FAILURE.
    try:
        arms = _construct_all(plan)
    except FATAL_PROGRAMMER_ERRORS:
        raise
    except Exception as exc:                      # noqa: BLE001
        return _mechanical(ev, identity, governance, run_instance,
                           "target construction failed", STAGE_CONSTRUCTION,
                           exc=exc, detail=["%s: %s" % (type(exc).__name__, exc)])
    passed(STAGE_CONSTRUCTION)

    try:
        index = enforce_sealed_sample(arms["E"].net.reindex(index),
                                      arms["A1"].net.reindex(index))
    except OrchestrationRefused as exc:
        # The sample contract failed AFTER construction. The targets have been
        # read and the authorization is spent, so this is a mechanical failure
        # that says what was constructed — not a refusal that says nothing was.
        return _mechanical(
            ev, identity, governance, run_instance,
            "the constructed sample is not the sealed evaluation calendar",
            STAGE_SEALED_SAMPLE, failure_class="SealedSampleNotSatisfied",
            detail=[exc.reason] + list(exc.detail),
            sample=_constructed_sample(arms, index),
            arms=_constructed_arms(arms, protocol))
    except FATAL_PROGRAMMER_ERRORS:
        raise
    except Exception as exc:                      # noqa: BLE001
        return _mechanical(
            ev, identity, governance, run_instance,
            "the sealed-sample check could not be completed",
            STAGE_SEALED_SAMPLE, exc=exc,
            detail=["%s: %s" % (type(exc).__name__, exc)],
            sample=_constructed_sample(arms, index),
            arms=_constructed_arms(arms, protocol))

    sample = {"first_month_end": SEALED_FIRST_MONTH_END,
              "last_month_end": SEALED_LAST_MONTH_END,
              "expected_n": SEALED_N, "evaluated_n": len(index),
              "calendar_digest": calendar_digest(index),
              "missingness_state": "NONE_ALL_179_PAIRED_MONTHS_PRESENT"}
    arms_block = {a: {"arm": a, "months": int(len(arms[a].net))}
                  for a in ("E", "A1", "S1", "S2")}
    arms_block["seed_protocol"] = protocol
    if plan.artifact_path:
        # Named before the record is finalized, because these are facts known in
        # advance. The file HASH is not among them: it cannot be, and that is
        # exactly why it lives in the sidecar instead.
        governance["artifact_file"] = os.path.basename(plan.artifact_path)
        governance["artifact_provenance_file"] = os.path.basename(
            plan.artifact_provenance_path
            or ev.provenance_path_for(plan.artifact_path))
        governance["artifact_identity_convention"] = \
            ev.ARTIFACT_IDENTITY_CONVENTION

    try:
        primary, secondary, windows, diag = _infer_all(plan, arms, index)
    except FATAL_PROGRAMMER_ERRORS:
        raise
    except Exception as exc:                      # noqa: BLE001
        return _mechanical(ev, identity, governance, run_instance,
                           "inference failed", STAGE_INFERENCE, exc=exc,
                           detail=["%s: %s" % (type(exc).__name__, exc)],
                           sample=sample, arms=arms_block)

    inf = L["inference"]
    pblk = _primary_block(primary)
    if primary.classification == inf.PROCEDURE_FAILURE:
        artifact = ev.procedure_failure(identity, governance, run_instance,
                                        sample, arms_block, pblk)
    else:
        artifact = ev.completed(identity, governance, run_instance, sample,
                                arms_block, pblk, _secondary_block(secondary),
                                _diagnostics_block(windows, diag))

    # ---- validation, then ATOMIC publication -------------------------------
    try:
        errs = ev.validate(artifact, identity.get("execution_revision"))
    except FATAL_PROGRAMMER_ERRORS:
        raise
    except Exception as exc:                      # noqa: BLE001
        return _mechanical(ev, identity, governance, run_instance,
                           "the evidence artifact could not be validated",
                           STAGE_ARTIFACT, exc=exc,
                           detail=["%s: %s" % (type(exc).__name__, exc)],
                           sample=sample, arms=arms_block)
    if errs:
        return _mechanical(
            ev, identity, governance, run_instance,
            "the evidence artifact failed its own schema validation",
            STAGE_ARTIFACT, failure_class="EvidenceSchemaError", detail=errs,
            sample=sample, arms=arms_block)
    passed(STAGE_ARTIFACT)

    if plan.artifact_path:
        # B6. The file's sha256 is NOT embedded in the file: a record cannot
        # contain its own hash, and the old write-hash-embed-rewrite protocol
        # recorded the digest of a file it then replaced. The payload digest
        # (`content_digest`) stays inside; the published-bytes digest goes in a
        # sidecar provenance record, and publication is a rename, so the final
        # path never holds a partially written artifact.
        try:
            publication = ev.publish_artifact(
                plan.artifact_path, artifact,
                identity.get("execution_revision"),
                provenance_extra={
                    "run_id": plan.run_id,
                    "authorization_id": governance.get("authorization_id"),
                    "generated_utc": run_instance.get("generated_utc"),
                    "execution_revision": identity.get("execution_revision")},
                tmp_path=plan.artifact_tmp_path,
                provenance_path=plan.artifact_provenance_path)
        except ev.ArtifactProvenanceError as exc:
            # The artifact IS published and its identity is intact; only the
            # external provenance record failed. Say exactly that.
            plan.publication = exc.provenance
            return _mechanical(
                ev, identity, governance, run_instance,
                "the evidence artifact was published but its external "
                "provenance record could not be written",
                STAGE_PROVENANCE, failure_class="ArtifactProvenanceError",
                detail=[str(exc)], sample=sample, arms=arms_block)
        except FATAL_PROGRAMMER_ERRORS:
            raise
        except Exception as exc:                  # noqa: BLE001
            return _mechanical(
                ev, identity, governance, run_instance,
                "the evidence artifact could not be persisted", STAGE_PERSIST,
                exc=exc, detail=["%s: %s" % (type(exc).__name__, exc)],
                sample=sample, arms=arms_block)
        plan.publication = publication
        passed(STAGE_PERSIST)
        passed(STAGE_PROVENANCE)
    return artifact
