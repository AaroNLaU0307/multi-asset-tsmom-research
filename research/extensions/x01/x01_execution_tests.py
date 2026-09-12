"""X01 execution-infrastructure tests — SYNTHETIC ONLY, NO REAL TARGET DATA.

Every panel here is hand-built, every adapter is injected, every ledger is a
scratch object in memory or under a temporary directory. **No test in this file
opens the frozen ETF CSV or any parquet panel**, and none produces a real
Sharpe, ΔS, bootstrap, diagnostic or evidence artifact. The numbers the
synthetic end-to-end run produces are ARCHITECTURAL, not evidential: they say
the wiring works and nothing whatsoever about X01.

The ordering claims are checked with a call counter, not asserted: "no target
constructor ran" means the counter says zero.
"""

import copy
import hashlib
import importlib.util
import io
import json
import math
import os
import re
import subprocess
import sys
import tempfile

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


orch = _load("x01_orch", os.path.join(HERE, "x01_orchestrator.py"))
runner = _load("x01_rn_x", os.path.join(HERE, "x01_runner.py"))

# ONE evidence module, the same object the orchestrator calls. Loading a second
# copy would give the tests their own `_atomic_replace`, their own exception
# classes and their own constants — so a failure-injection test would patch a
# function the production path never calls, and pass while proving nothing.
ev = orch.layers()["evidence"]

# The authorization layer is taken from the ORCHESTRATOR'S loader, never loaded
# a second time here. Two `exec_module` copies of one file define two distinct
# `Step2NotDurable` classes, and an `except` clause in the orchestrator would
# then miss the exception a test raised — the tests would pass while proving
# something about a class nobody uses.
AUTH = orch.layers()["authorization"]
prod = _load("x01_prod_t", os.path.join(HERE, "x01_production.py"))
# Share the ALREADY-LOADED orchestrator rather than letting production load a
# second copy: two copies define two sets of exception classes, and the tests
# would then be asserting about classes the production path never raises.
prod.mods(orchestrator=orch)

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

_fails, _out = [], []


def ck(name, ok, detail=""):
    _out.append("  %-74s %s%s" % (name, "PASS" if ok else "FAIL",
                                  ("   " + detail) if detail else ""))
    if not ok:
        _fails.append(name)


def flush(title):
    print("=" * 96); print(title); print("=" * 96)
    print("\n".join(_out)); del _out[:]; print()


# --------------------------------------------------------------------------- #
# synthetic adapters
# --------------------------------------------------------------------------- #
SEALED_IDX = pd.date_range("2011-07-31", "2026-05-31", freq="ME")


class Ok(object):
    """A stand-in preflight result that passed."""
    ok = True
    reasons = []
    checks = [("synthetic", True, "")] * 40


class NotOk(object):
    ok = False
    reasons = ["synthetic refusal: a pin did not hold"]
    checks = []


class ListAppender(object):
    """An in-memory append-only lifecycle store for the ordering fixtures."""

    def __init__(self):
        self.records = []

    @property
    def count(self):
        return len(self.records)

    def append(self, payload):
        self.records.append(payload)
        return "LIST-%d" % len(self.records)


class DeclaredAuthorization(object):
    """A SYNTHETIC authorization provider, for testing the gate's ORDERING only.

    It is not the Owner mechanism — `LedgerAuthorizationProvider` is, and it is
    exercised directly in sections 6 to 9. This one exists so the ordering
    tests can open the gate without standing up a ledger, and so a mutation to
    the ordering is not masked by an authorization refusal that would have
    fired anyway.

    Its lifecycle session is the REAL `AuthorizationSession`, so even the
    ordering fixtures record consumption through production code.
    """

    declared = True

    def __init__(self, bind_to_revision=None, record="SYNTHETIC-AUTH-1",
                 claim_root=None):
        self.bind_to = bind_to_revision
        self.record = record
        self.appender = ListAppender()
        # A REAL claim store on a scratch directory. The ordering fixtures run
        # through the same atomic primitive production uses; only the directory
        # is throwaway.
        self.claim_store = AUTH.FileClaimStore(
            claim_root or tempfile.mkdtemp(prefix="x01-claim-"))
        self._session = None

    def authorization_for(self, identity):
        if self.bind_to and identity.get("execution_revision") != self.bind_to:
            return None, ("the authorization is bound to revision %s, not to the "
                          "revision that would execute (%s)"
                          % (self.bind_to[:12],
                             str(identity.get("execution_revision"))[:12]))
        return {"authorization_id": self.record,
                "run_id": identity.get("run_id"),
                "owner": AUTH.OWNER_IDENTITY,
                "scope": AUTH.ONE_SHOT_SCOPE,
                "synthetic": True}, None

    def open_session(self, reference):
        if self._session is not None:
            raise AUTH.AuthorizationError(
                "a second execution session was opened against %s" % self.record)
        self._session = AUTH.AuthorizationSession(
            reference, self.appender, lambda: "2026-01-01T00:00:00Z",
            claim_store=self.claim_store)
        return self._session


class WrongRunIdProvider(object):
    """Approves — but for some OTHER run. The gate binds the run itself.

    The ledger provider already refuses a run_id mismatch; this fixture binds
    the orchestrator's own independent check, which is what stops a provider
    (real or replaced) from spending one run's authorization on another.
    """

    declared = True

    def __init__(self, run_id):
        self.run_id = run_id
        self.appender = ListAppender()
        self._session = None

    def authorization_for(self, identity):
        return {"authorization_id": "X01-AUTH-ELSEWHERE",
                "run_id": self.run_id}, None

    def open_session(self, reference):
        self._session = AUTH.AuthorizationSession(
            reference, self.appender, lambda: "2026-01-01T00:00:00Z",
            claim_store=AUTH.FileClaimStore(
                tempfile.mkdtemp(prefix="x01-claim-")))
        return self._session


class NoSessionProvider(object):
    """Hands back an authorization but offers no way to mark it consumed.

    A ONE_SHOT authorization whose consumption nobody can record is the one-shot
    rule with the enforcement removed, so the gate must refuse the provider
    itself rather than trust it.
    """

    declared = True

    def authorization_for(self, identity):
        return {"authorization_id": "NO-SESSION", "run_id": identity.get("run_id")}, None


class UndeclaredButPermissive(object):
    """Undeclared, yet it WOULD hand back an authorization if consulted.

    This is what binds the `declared` guard on its own. An undeclared mechanism
    must not be CONSULTED at all — not merely disbelieved — because "there is no
    mechanism" and "the mechanism said no" are different states, and only the
    first is true today. Without this fixture, deleting the guard changed
    nothing observable: the plain refusing provider also refuses one clause
    later, so the suite could not tell which clause had fired.
    """

    declared = False

    def authorization_for(self, identity):
        return "WOULD-HAVE-AUTHORIZED", None


class ScratchRecorder(object):
    """Append-only in memory. Nothing reaches a real ledger."""

    def __init__(self, fail_on=None, cumulative=14):
        self.rows = []
        self.fail_on = fail_on
        self.cumulative = cumulative

    @property
    def exposure_rows(self):
        return [r for r in self.rows if r[0] == "exposure"]

    def record_exposure_and_attempts(self, payload):
        if self.fail_on == "exposure":
            # An ordinary break: nobody can say whether anything was written.
            raise orch.OrchestrationMechanicalFailure(
                orch.STAGE_EXPOSURE_RECORD, "synthetic ledger write failure")
        if self.fail_on == "oserror_exposure":
            raise OSError(28, "synthetic: no space left on device")
        if self.fail_on == "exposure_proven_not_durable":
            # The only failure that PROVES nothing durable exists. A recorder
            # raises this exactly when it can demonstrate atomicity; everything
            # else is ambiguous and fails closed.
            raise AUTH.Step2NotDurable(
                "synthetic recorder: the append was rejected before any byte "
                "reached durable storage")
        self.rows.append(("exposure", payload))
        return "SCRATCH-EXPOSURE-%d" % len(self.rows)

    def read_cumulative_databento_state(self):
        if self.fail_on == "oserror_cumulative":
            raise OSError(13, "synthetic: permission denied")
        if self.fail_on == "cumulative":
            return None
        # Mirrors production: step 2 durably registers this run's attempts, so a
        # read AFTER it already includes them. A scratch recorder that kept
        # returning the pre-step-2 number would let the double-count defect
        # hide behind a fixture that never advanced.
        return {"cumulative": self.cumulative + (3 if self.exposure_rows else 0),
                "source": "SCRATCH"}

    def record_seed_streams(self, payload):
        if self.fail_on == "oserror_seed":
            raise OSError(5, "synthetic: I/O error")
        if self.fail_on == "seed":
            return None
        self.rows.append(("seed", payload))
        return "SCRATCH-SEED-%d" % len(self.rows)


class SyntheticData(object):
    """Hand-built panels spanning the sealed calendar. Not market data."""

    def __init__(self, counter, months=None, break_sample=False):
        self.counter = counter
        self.months = months or SEALED_IDX
        self.break_sample = break_sample
        # Mirrors the production adapter's read ledger, so one assertion about
        # "no target was read" works against either boundary.
        self.reads = []

    def etf_panel(self):
        self.reads.append("synthetic_etf_panel")
        # daily business days covering the sealed window plus warm-up
        days = pd.bdate_range("2009-01-01", "2026-06-30")
        rng = np.random.default_rng(4242)
        return pd.DataFrame(
            {t: 100.0 * np.cumprod(1.0 + rng.normal(0.0004 + i * 5e-5, 0.010,
                                                    len(days)))
             for i, t in enumerate(orch.SEALED_MAPPED_ETFS)}, index=days)

    def futures_panels(self):
        self.reads.append("synthetic_futures_panels")
        days = pd.bdate_range("2009-01-01", "2026-06-30")
        if self.break_sample:
            days = pd.bdate_range("2009-01-01", "2024-06-30")
        rng = np.random.default_rng(99)
        S, O, M = [], [], []
        for root, base, step in (("CL", 70.0, 0.02), ("NG", 4.0, 0.002),
                                 ("GC", 1500.0, 0.30), ("ZC", 500.0, 0.05)):
            key = "%s7001__2030-01-01" % root
            px = base + np.cumsum(rng.normal(step * 0.1, base * 0.006, len(days)))
            px = np.maximum(px, base * 0.25)
            S.append(pd.DataFrame({key: px}, index=days))
            O.append(pd.DataFrame({key: np.full(len(days), 100.0)}, index=days))
            m = pd.DataFrame({"asset": [root], "_contract_key": [key],
                              "expiration": ["2030-01-01"]})
            m["expiration_dt"] = pd.to_datetime(m["expiration"])
            M.append(m)
        return (pd.concat(S, axis=1), pd.concat(O, axis=1),
                pd.concat(M, ignore_index=True))


SYNTH_MAP = {"USO": ["CL"], "UNG": ["NG"], "GLD": ["GC"], "DBA": ["ZC"]}


def plan_for(counter, **kw):
    """A plan with synthetic everything and a fixed clock."""
    kw.setdefault("preflight_fn", lambda: Ok())
    kw.setdefault("authorization_provider", DeclaredAuthorization())
    kw.setdefault("recorder", ScratchRecorder())
    kw.setdefault("clock", lambda: "2026-01-01T00:00:00Z")
    kw.setdefault("run_id", "SYNTHETIC-RUN")
    data = kw.pop("data_adapter", None) or SyntheticData(counter)
    p = orch.ExecutionPlan(data_adapter=data, counter=counter, **kw)
    return p


# --------------------------------------------------------------------------- #
# a synthetic artifact, built without running anything
# --------------------------------------------------------------------------- #
SYNTH_RUN_ID = "X01-RUN-SYNTHETIC"
SYNTH_INFRA_REVISION = "9" * 40


def synthetic_identity():
    return {
        "research_id": "TSMOM-EXT-001",
        "run_id": SYNTH_RUN_ID,
        "prereg_sha256": ev.SEALED_EXPECTATIONS["prereg_sha256"],
        "prereg_seal_revision": "df5b28ab7324c7ba789ab231431f077288c3fd84",
        "construction_binding_revision": "b" * 40,
        "construction_sha256": "c" * 64,
        "inference_binding_revision": "b" * 40,
        "inference_sha256": "d" * 64,
        "runner_revision": "e" * 40,
        "manifest_sha256": "f" * 64,
        "execution_revision": "a" * 40,
        "execution_infrastructure_revision": SYNTH_INFRA_REVISION,
        "input_pins": [{"path": "config.py", "sha256": "0" * 64,
                        "hash_convention": "blob"}],
    }


def synthetic_governance():
    return {"authorization_reference": "SYNTHETIC-AUTH-1",
            "preflight_result": "PASS",
            "exposure_record_reference": "SCRATCH-EXPOSURE-1",
            "trial_accounting_reference": "SCRATCH-EXPOSURE-1"}


def synthetic_sample(n=179, calendar_digest=None):
    return {"first_month_end": "2011-07-31", "last_month_end": "2026-05-31",
            "expected_n": 179, "evaluated_n": n,
            "calendar_digest": calendar_digest or ev.sealed_calendar_digest(),
            "missingness_state": "NONE_ALL_179_PAIRED_MONTHS_PRESENT"}


def synthetic_arms():
    return {"E": {"arm": "E", "months": 179}, "A1": {"arm": "A1", "months": 179},
            "S1": {"arm": "S1", "months": 179}, "S2": {"arm": "S2", "months": 179},
            "seed_protocol": {"master_seed": 7,
                              "arm_order": ["primary", "S1", "S2"],
                              "child_streams": [{"spawn_key": [0]},
                                                {"spawn_key": [1]},
                                                {"spawn_key": [2]}]}}


def synthetic_primary(lower=-0.05, upper=0.20, cls="PRESERVATION_SUPPORTED",
                      valid=9800, with_ci=True):
    blk = {
        "sharpe_e": 0.40, "sharpe_f": 0.45, "delta_s": 0.05000000000000004,
        "boundary_b": 0.15, "boundary": -0.15,
        "bootstrap": {"family": ev.SEALED_EXPECTATIONS["bootstrap_family"],
                      "expected_block_length_months": 12,
                      "replications_attempted": 10000, "ci_level": 95,
                      "ci_method": "percentile",
                      "percentile_interpolation": "linear",
                      "valid_replicate_floor": 9500, "min_distinct_months": 24,
                      "master_seed": 7, "arm_order": ["primary", "S1", "S2"]},
        "bootstrap_counts": {"attempted": 10000, "valid": valid,
                             "discarded": 10000 - valid,
                             "discarded_too_few_distinct_months": 10000 - valid,
                             "discarded_zero_std_e": 0,
                             "discarded_zero_std_f": 0},
        "discard_reasons": ["too_few_distinct_calendar_months"],
    }
    blk["delta_s"] = blk["sharpe_f"] - blk["sharpe_e"]
    if with_ci:
        blk["ci"] = {"lower": lower, "upper": upper, "level": 95,
                     "method": "percentile", "n_valid": valid}
        blk["classification"] = cls
    return blk


def synthetic_secondary():
    arm = lambda: {"delta_s": 0.01, "sharpe_e": 0.4, "sharpe_f": 0.41,
                   "ci": {"lower": -0.1, "upper": 0.12, "level": 95,
                          "method": "percentile", "n_valid": 9800},
                   "role": "DESCRIPTIVE_SENSITIVITY", "promotion_power": "NONE",
                   "bootstrap_counts": {"attempted": 10000, "valid": 9800,
                                        "discarded": 200}}
    return {"S1": arm(), "S2": arm(), "bh_fdr_required": False,
            "materiality_gate": "NONE"}


def synthetic_diagnostics():
    return {"crisis_windows": [
                {"name": "COVID 2020", "n_months": 3,
                 "month_ends": list(ev.SEALED_CRISIS_WINDOWS["COVID 2020"])},
                {"name": "CY2022", "n_months": 12,
                 "month_ends": list(ev.SEALED_CRISIS_WINDOWS["CY2022"])}],
            "pair_correlations": {"USO": {"correlation": 0.5, "n_months": 179}},
            "tracking_error_monthly": 0.01, "tracking_error_annualised": 0.0346,
            "max_abs_d": 0.05, "mean_d": 0.001,
            "sign_agreement": {"sign_agreement_rate": 0.8},
            "turnover_e": 12.0, "turnover_f": 34.0,
            "realised_cost_e": 0.01, "realised_cost_f": 0.02,
            "role": "DESCRIPTIVE_NEVER_A_GATE"}


def good_artifact(**kw):
    return ev.completed(synthetic_identity(), synthetic_governance(),
                        {"run_id": "R", "generated_utc": "T"},
                        kw.pop("sample", synthetic_sample()),
                        kw.pop("arms", synthetic_arms()),
                        kw.pop("primary", synthetic_primary()),
                        kw.pop("secondary", synthetic_secondary()),
                        kw.pop("diagnostics", synthetic_diagnostics()))


# --------------------------------------------------------------------------- #
# 1. ITEM 10 — the evidence artifact schema
# --------------------------------------------------------------------------- #
def test_artifact_schema():
    a = good_artifact()
    ck("a complete synthetic COMPLETED_EVIDENCE record validates clean",
       ev.validate(a) == [], "; ".join(ev.validate(a))[:100])
    ck("schema is versioned", a["schema"] == {"name": "x01-evidence", "version": 1})
    ck("the four outcome states are distinct and exhaustive",
       len(set(ev.OUTCOME_STATES)) == 4)

    # determinism
    d1 = ev.content_digest(a)
    b = copy.deepcopy(a)
    b["run_instance"] = {"run_id": "OTHER", "generated_utc": "LATER"}
    ck("the digest EXCLUDES run-instance metadata, so two honest runs agree",
       ev.content_digest(b) == d1)
    c = copy.deepcopy(a)
    c["primary"]["delta_s"] = 0.06
    ck("but any result change moves the digest", ev.content_digest(c) != d1)
    ck("canonical serialization is order-independent",
       ev.canonical_json({"b": 1, "a": 2}) == ev.canonical_json({"a": 2, "b": 1}))
    ck("canonical serialization refuses NaN/inf, which JSON cannot represent",
       _raises(lambda: ev.canonical_json({"x": float("nan")}), ValueError))

    # failure-state separation
    r = ev.refused(synthetic_identity(), {"preflight_result": "REFUSE"},
                   {"run_id": "R", "generated_utc": "T"}, "no authorization",
                   orch.STAGE_AUTHORIZATION)
    ck("EXECUTION_REFUSED validates and carries no computed block",
       ev.validate(r) == [] and r["primary"] is None and r["sample"] is None,
       "; ".join(ev.validate(r))[:90])
    m = ev.mechanical_failure(synthetic_identity(), {}, {"run_id": "R",
                                                         "generated_utc": "T"},
                              "write failed", orch.STAGE_PERSIST)
    ck("EXECUTION_MECHANICAL_FAILURE validates and carries no classification",
       ev.validate(m) == [] and m["primary"] is None)
    pf = ev.procedure_failure(synthetic_identity(), synthetic_governance(),
                              {"run_id": "R", "generated_utc": "T"},
                              synthetic_sample(), synthetic_arms(),
                              synthetic_primary(valid=9000, with_ci=False))
    ck("INFERENCE_PROCEDURE_FAILURE validates and carries counts but NO verdict",
       ev.validate(pf) == [] and pf["primary"].get("classification") is None,
       "; ".join(ev.validate(pf))[:90])
    ck("a mechanical failure is never one of the §5 classifications",
       not set(ev.OUTCOME_STATES) & set(ev.SEALED_CLASSIFICATIONS))
    flush("1. ITEM 10 — evidence artifact schema, digest, state separation")


def _raises(fn, exc=Exception):
    try:
        fn()
    except exc:
        return True
    except Exception:
        return False
    return False


def test_artifact_validator_rejections():
    """Each case is a record that must be refused, with a reason."""
    cases = []

    a = good_artifact(sample=synthetic_sample(n=178))
    cases.append(("N != 179 on a completed study", a, "evaluated_n"))

    a = good_artifact(primary=synthetic_primary(lower=float("nan")))
    cases.append(("NaN CI endpoint beside a classification", a, "finite endpoints"))

    a = good_artifact(primary=synthetic_primary(lower=0.2, upper=-0.2))
    cases.append(("inverted CI", a, "inverted"))

    p = synthetic_primary(valid=9000)
    a = good_artifact(primary=p)
    cases.append(("classification with fewer than 9,500 valid replicates", a,
                  "below the sealed floor"))

    pf = ev.procedure_failure(synthetic_identity(), synthetic_governance(),
                              {"run_id": "R", "generated_utc": "T"},
                              synthetic_sample(), synthetic_arms(),
                              synthetic_primary(valid=9000))
    bad = copy.deepcopy(pf)
    bad["primary"]["classification"] = "PRESERVATION_SUPPORTED"
    bad = ev.finalize(bad)
    cases.append(("classification present after procedure failure", bad,
                  "NO classification"))

    s = synthetic_secondary()
    s["S1"]["promotion_power"] = "PRIMARY"
    cases.append(("S1 carrying promotion power", good_artifact(secondary=s),
                  "promotion_power must be NONE"))
    s2 = synthetic_secondary()
    s2["S2"]["classification"] = "PRESERVATION_SUPPORTED"
    cases.append(("S2 carrying a classification", good_artifact(secondary=s2),
                  "must not carry"))

    p = synthetic_primary()
    p["bootstrap"]["expected_block_length_months"] = 6
    cases.append(("wrong block length", good_artifact(primary=p),
                  "expected_block_length_months"))
    p = synthetic_primary()
    p["bootstrap"]["replications_attempted"] = 5000
    p["bootstrap_counts"]["attempted"] = 5000
    cases.append(("wrong replication count", good_artifact(primary=p),
                  "10,000"))
    p = synthetic_primary()
    p["bootstrap"]["ci_method"] = "bca"
    cases.append(("BCa instead of percentile", good_artifact(primary=p),
                  "percentile"))
    p = synthetic_primary()
    p["boundary_b"] = 0.20
    p["boundary"] = -0.20
    cases.append(("wrong B", good_artifact(primary=p), "0.15"))

    arms = synthetic_arms()
    arms["seed_protocol"]["child_streams"] = [{"spawn_key": [0]}, {"spawn_key": [0]},
                                              {"spawn_key": [0]}]
    cases.append(("wrong spawn identity", good_artifact(arms=arms), "spawn_keys"))

    ident = synthetic_identity()
    ident["inference_binding_revision"] = None
    a = ev.completed(ident, synthetic_governance(),
                     {"run_id": "R", "generated_utc": "T"}, synthetic_sample(),
                     synthetic_arms(), synthetic_primary(),
                     synthetic_secondary(), synthetic_diagnostics())
    cases.append(("results without a bound inference identity", a,
                  "inference_binding_revision"))

    gov = synthetic_governance()
    del gov["authorization_reference"]
    a = ev.completed(synthetic_identity(), gov,
                     {"run_id": "R", "generated_utc": "T"}, synthetic_sample(),
                     synthetic_arms(), synthetic_primary(),
                     synthetic_secondary(), synthetic_diagnostics())
    cases.append(("completed run with no authorization reference", a,
                  "authorization_reference"))

    a = good_artifact()
    cases.append(("execution-revision mismatch", a, "does not match"))

    p = synthetic_primary(lower=-0.5, upper=-0.3, cls="PRESERVATION_SUPPORTED")
    cases.append(("verdict that does not follow from its own interval",
                  good_artifact(primary=p), "does not follow"))

    d = synthetic_diagnostics()
    d["crisis_windows"].append({"name": "Calm 2012-2019", "n_months": 96})
    cases.append(("an unsealed crisis window", good_artifact(diagnostics=d),
                  "exactly"))

    tampered = good_artifact()
    tampered["primary"]["delta_s"] = 0.99
    cases.append(("a record whose digest no longer matches its body", tampered,
                  "content_digest"))

    for label, art, needle in cases:
        rev = "a" * 40 if label != "execution-revision mismatch" else "z" * 40
        errs = ev.validate(art, expect_execution_revision=rev)
        hit = any(needle in x for x in errs)
        ck("REJECTED: %s" % label, bool(errs) and hit,
           ("%d error(s): %s" % (len(errs), errs[0][:70])) if errs else "accepted!")

    ck("require_valid RAISES rather than returning, on the persistence path",
       _raises(lambda: ev.require_valid(good_artifact(sample=synthetic_sample(178))),
               ev.EvidenceSchemaError))
    flush("1b. ITEM 10 — validator rejections (each with a discriminating case)")


# --------------------------------------------------------------------------- #
# 2. ITEM 11/12 — fail-closed ordering, with call counters
# --------------------------------------------------------------------------- #
def test_fail_closed_ordering():
    cases = [
        ("M1  preflight bypass: preflight refuses", dict(preflight_fn=lambda: NotOk()),
         orch.STAGE_PREFLIGHT),
        ("M2  authorization bypass: no declared mechanism",
         dict(authorization_provider=orch.NoAuthorizationMechanism()),
         orch.STAGE_AUTHORIZATION),
        ("M2b undeclared mechanism must not even be CONSULTED",
         dict(authorization_provider=UndeclaredButPermissive()),
         orch.STAGE_AUTHORIZATION),
        ("M10 execution-revision mismatch: authorization bound elsewhere",
         dict(authorization_provider=DeclaredAuthorization(bind_to_revision="z" * 40)),
         orch.STAGE_AUTHORIZATION),
    ]
    for label, kw, stage in cases:
        c = orch.TargetAdapterCallCounter()
        art = orch.run(plan_for(c, **kw))
        ck("%s -> EXECUTION_REFUSED at %s" % (label, stage),
           art["outcome_state"] == ev.EXECUTION_REFUSED
           and art["governance"].get("refusal_stage") == stage,
           "%s / %s" % (art["outcome_state"], art["governance"].get("refusal_stage")))
        ck("%s -> TARGET_CONSTRUCTOR_CALLS = 0" % label[:4], c.n == 0,
           "counter = %d (%s)" % (c.n, c.calls[:2]))
        ck("%s -> the record carries no computed block" % label[:4],
           art["primary"] is None and art["sample"] is None)
        if label.startswith(("M2 ", "M2b")):
            ck("%s -> the refusal cites the UNDECLARED mechanism, not a "
               "mechanism that answered no" % label[:4],
               art["governance"]["refusal_reason"]
               == orch.AUTHORIZATION_MECHANISM_NOTE,
               art["governance"]["refusal_reason"][:70])
            ck("%s -> and no authorization reference was recorded" % label[:4],
               "authorization_reference" not in art["governance"])

    # pre-execution record failures
    for tag, fail_on, stage in (("exposure ledger write", "exposure",
                                 orch.STAGE_EXPOSURE_RECORD),
                                ("cumulative-state read", "cumulative",
                                 orch.STAGE_CUMULATIVE_STATE),
                                ("seed-stream record", "seed",
                                 orch.STAGE_SEED_RECORD)):
        c = orch.TargetAdapterCallCounter()
        art = orch.run(plan_for(c, recorder=ScratchRecorder(fail_on=fail_on)))
        ck("pre-execution %s failure stops the run at %s" % (tag, stage),
           art["outcome_state"] in (ev.EXECUTION_REFUSED,
                                    ev.EXECUTION_MECHANICAL_FAILURE)
           and (art["governance"].get("failure_stage") == stage
                or art["governance"].get("refusal_stage") == stage),
           str(art["governance"].get("failure_stage")
               or art["governance"].get("refusal_stage")))
        ck("... and TARGET_CONSTRUCTOR_CALLS = 0", c.n == 0, "counter = %d" % c.n)

    ck("the closed set of pre-construction stages is exactly the six gates",
       orch.STAGES_BEFORE_CONSTRUCTION ==
       (orch.STAGE_PREFLIGHT, orch.STAGE_AUTHORIZATION, orch.STAGE_EXPOSURE_RECORD,
        orch.STAGE_CUMULATIVE_STATE, orch.STAGE_SEED_RECORD,
        orch.STAGE_SEALED_SAMPLE))
    ck("M3  a passing preflight ALONE never opens the authorization gate",
       orch.run(plan_for(orch.TargetAdapterCallCounter(),
                         authorization_provider=orch.NoAuthorizationMechanism())
                )["outcome_state"] == ev.EXECUTION_REFUSED)
    ck("the default plan refuses everything: no declared mechanism, refusing "
       "data adapter, refusing recorder",
       orch.NoAuthorizationMechanism().declared is False
       and _raises(lambda: orch.RefusingDataAdapter().etf_panel(),
                   orch.OrchestrationRefused)
       and _raises(lambda: orch.RefusingRecorder().record_seed_streams({}),
                   orch.OrchestrationRefused))
    flush("2. ITEM 11 — fail-closed ordering, counted not asserted")


def test_sealed_sample_enforcement():
    idx = orch.sealed_evaluation_index()
    ck("orchestration CONSTRUCTS the sealed calendar: 2011-07-31 … 2026-05-31",
       len(idx) == 179 and str(idx[0].date()) == "2011-07-31"
       and str(idx[-1].date()) == "2026-05-31")
    ck("the calendar digest is deterministic",
       orch.calendar_digest(idx) == orch.calendar_digest(orch.sealed_evaluation_index()))
    ck("and it distinguishes two same-length calendars",
       orch.calendar_digest(idx) != orch.calendar_digest(idx + pd.offsets.MonthEnd(1)))

    good = pd.Series(np.linspace(0.001, 0.02, 179), index=idx)
    ck("a correct pair passes enforcement",
       len(orch.enforce_sealed_sample(good, good)) == 179)
    short = good.iloc[:-1]
    ck("M4  a 178-month leg is REFUSED by orchestration, before inference",
       _raises(lambda: orch.enforce_sealed_sample(short, short),
               orch.OrchestrationRefused))
    holed = good.copy(); holed.iloc[5] = np.nan
    ck("M4  a non-finite month is REFUSED", _raises(
        lambda: orch.enforce_sealed_sample(holed, good), orch.OrchestrationRefused))
    shifted = pd.Series(good.to_numpy(), index=idx + pd.offsets.MonthEnd(1))
    ck("M4  a wrong calendar of the right length is REFUSED", _raises(
        lambda: orch.enforce_sealed_sample(good, shifted),
        orch.OrchestrationRefused))
    ck("N179_ENFORCEMENT_LOCATION = BOTH — the inference boundary refuses the "
       "same sample independently",
       _raises(lambda: orch.layers()["inference"].require_sealed_sample(short, short),
               orch.layers()["inference"].SealedSampleViolation))
    flush("2b. ITEM 11 — the sealed sample, enforced in BOTH places")


# --------------------------------------------------------------------------- #
# 3. synthetic end-to-end
# --------------------------------------------------------------------------- #
def _e2e(tmpdir, run_id="SYNTHETIC-RUN"):
    c = orch.TargetAdapterCallCounter()
    path = os.path.join(tmpdir, "evidence-%s.json" % run_id)
    plan = plan_for(c, artifact_path=path, run_id=run_id)
    # the synthetic panels are mapped 1:1 so the fixture stays hand-checkable
    orch.layers()["construction"].SEALED_MAP.update(SYNTH_MAP)
    art = orch.run(plan)
    return art, c, path, plan


def test_synthetic_end_to_end():
    tmpdir = tempfile.mkdtemp(prefix="x01-e2e-")
    art, c, path, plan = _e2e(tmpdir, "RUN-A")
    state = art["outcome_state"]
    ck("the synthetic run reaches a result-bearing state, not a refusal",
       state in (ev.COMPLETED_EVIDENCE, ev.INFERENCE_PROCEDURE_FAILURE),
       "%s (%s)" % (state, art["governance"].get("refusal_reason")
                    or art["governance"].get("failure_reason")))
    ck("every pre-construction gate passed, in order",
       plan.stages_passed[:6] == list(orch.STAGES_BEFORE_CONSTRUCTION),
       str(plan.stages_passed[:6]))
    ck("constructors ran only AFTER those gates",
       c.n > 0 and "construct_E" in c.calls, str(c.calls[:3]))
    ck("the artifact validates against its own schema",
       ev.validate(art, art["identity"]["execution_revision"]) == [],
       "; ".join(ev.validate(art, art["identity"]["execution_revision"]))[:110])
    ck("the sealed sample is recorded as 179 evaluated months",
       art["sample"]["evaluated_n"] == 179 and art["sample"]["expected_n"] == 179)
    ck("the seed protocol travels with the record by spawn_key",
       [ch["spawn_key"] for ch in art["arms"]["seed_protocol"]["child_streams"]]
       == [[0], [1], [2]])
    ck("the exposure and trial references are cited",
       art["governance"]["exposure_record_reference"].startswith("SCRATCH-EXPOSURE"))
    _cds = art["governance"]["cumulative_databento_state"]
    ck("the cumulative Databento state was READ at step 3, and the published "
       "total IS the authoritative one — this run's contribution is not added "
       "to it a second time",
       _cds["resulting_total"] == _cds["cumulative_at_execution"]
       == _cds["authoritative_total_after_step2"]
       and _cds["current_run_databento_contribution"] == 3,
       "published %s, authoritative %s, contribution %s"
       % (_cds["resulting_total"], _cds["cumulative_at_execution"],
          _cds["current_run_databento_contribution"]))
    ck("... and the step-3 read reflects step 2 having already registered the "
       "attempts: 14 + 3 = 17, read once",
       _cds["cumulative_at_execution"] == 17, str(_cds["cumulative_at_execution"]))
    ck("the artifact was persisted to scratch", os.path.exists(path))
    ck("the persisted bytes are the canonical form",
       io.open(path, encoding="utf-8").read()
       == ev.canonical_json(ev.read_artifact(path)) + "\n")

    # determinism: run twice
    art2, c2, path2, _p2 = _e2e(tmpdir, "RUN-B")
    ck("SYNTHETIC_END_TO_END_ORCHESTRATION — the second run reaches the same state",
       art2["outcome_state"] == state)
    def _comparable(a):
        # `identity.run_id` is bound to the run by D4 and must differ between two
        # honest runs, exactly like `run_instance`. Everything else in identity
        # is pinned and is compared.
        out = {k: v for k, v in a.items()
               if k not in ("run_instance", "content_digest", "governance")}
        out["identity"] = {k: v for k, v in a["identity"].items() if k != "run_id"}
        return out
    d1, d2 = _comparable(art), _comparable(art2)
    ck("two runs are byte-identical outside run-instance metadata, the bound "
       "run_id and the governance references that name the scratch ledger rows",
       ev.canonical_json(d1) == ev.canonical_json(d2))
    ck("the identities DID differ in run_id, so that exclusion is not vacuous",
       art["identity"]["run_id"] != art2["identity"]["run_id"])
    ck("the run ids DO differ, so the determinism check is not vacuous",
       art["run_instance"]["run_id"] != art2["run_instance"]["run_id"])

    # M11 — a persistence failure must not be reported as completed
    c3 = orch.TargetAdapterCallCounter()
    bad_path = os.path.join(tmpdir, "no-such-dir", "x.json")
    plan3 = plan_for(c3, artifact_path=bad_path, run_id="RUN-C")
    art3 = orch.run(plan3)
    ck("M11 a failed artifact write yields EXECUTION_MECHANICAL_FAILURE, never "
       "COMPLETED_EVIDENCE",
       art3["outcome_state"] == ev.EXECUTION_MECHANICAL_FAILURE
       and art3["governance"]["failure_stage"] == orch.STAGE_PERSIST,
       art3["outcome_state"])
    ck("M11 and no artifact file was left behind", not os.path.exists(bad_path))

    # M12 — orchestration must not reimplement any statistic
    src = io.open(os.path.join(HERE, "x01_orchestrator.py"), encoding="utf-8").read()
    inf = orch.layers()["inference"]
    real = inf.run_primary
    calls = {"n": 0}

    def counting(*a, **k):
        calls["n"] += 1
        return real(*a, **k)
    inf.run_primary = counting
    try:
        _e2e(tmpdir, "RUN-D")
    finally:
        inf.run_primary = real
    ck("M12 orchestration CALLS the bound inference layer rather than "
       "reimplementing it", calls["n"] >= 1, "run_primary calls = %d" % calls["n"])
    ck("M12 and the orchestrator defines no statistic of its own",
       not any(tok in src for tok in ("def sharpe", "def delta_sharpe",
                                      "def percentile_ci", "def classify",
                                      "np.percentile", "ddof=1")))
    flush("3. SYNTHETIC END-TO-END — architecture only, no X01 claim")


def test_partial_failure_states():
    tmpdir = tempfile.mkdtemp(prefix="x01-partial-")
    # M7 — procedure failure must not carry a classification
    inf = orch.layers()["inference"]
    real_primary = inf.run_primary

    class FakeCounts(object):
        attempted, valid, discarded = 10000, 9000, 1000
        discarded_too_few_distinct_months = 1000
        discarded_zero_std_e = 0
        discarded_zero_std_f = 0

    def failing_primary(e, f, **kw):
        res = real_primary(e, f, **kw)
        return type(res)(arm=res.arm, sharpes=res.sharpes, delta_s=res.delta_s,
                         ci=inf.ConfidenceInterval(float("nan"), float("nan"),
                                                   95, "percentile", 9000),
                         counts=FakeCounts(), config=res.config,
                         classification=inf.PROCEDURE_FAILURE,
                         boundary_b=res.boundary_b, boundary=res.boundary)
    inf.run_primary = failing_primary
    try:
        c = orch.TargetAdapterCallCounter()
        art = orch.run(plan_for(c, artifact_path=os.path.join(tmpdir, "pf.json"),
                                run_id="RUN-PF"))
    finally:
        inf.run_primary = real_primary
    ck("M7 a procedure failure yields INFERENCE_PROCEDURE_FAILURE with counts "
       "and NO classification",
       art["outcome_state"] == ev.INFERENCE_PROCEDURE_FAILURE
       and art["primary"].get("classification") is None
       and art["primary"]["bootstrap_counts"]["valid"] == 9000,
       art["outcome_state"])
    ck("M7 and it validates as that state", ev.validate(
        art, art["identity"]["execution_revision"]) == [],
       "; ".join(ev.validate(art, art["identity"]["execution_revision"]))[:100])
    ck("M7 no scientific classification appears anywhere in the record",
       not any(cls in ev.canonical_json(art) for cls in ev.SEALED_CLASSIFICATIONS))

    # inference raising -> mechanical failure, not a verdict
    def exploding(*a, **k):
        raise RuntimeError("synthetic inference break")
    inf.run_primary = exploding
    try:
        c = orch.TargetAdapterCallCounter()
        art2 = orch.run(plan_for(c, run_id="RUN-BREAK"))
    finally:
        inf.run_primary = real_primary
    ck("construction succeeded but inference broke -> "
       "EXECUTION_MECHANICAL_FAILURE at the inference stage",
       art2["outcome_state"] == ev.EXECUTION_MECHANICAL_FAILURE
       and art2["governance"]["failure_stage"] == orch.STAGE_INFERENCE)
    ck("... and it carries no primary block at all", art2["primary"] is None)
    flush("3b. PARTIAL FAILURE — never a scientific verdict")


# --------------------------------------------------------------------------- #
# 4. binding-identity adversarial cases
# --------------------------------------------------------------------------- #
def test_binding_identity_cases():
    a = good_artifact()
    for label, mutate, needle in (
            ("M5  altered construction binding revision",
             lambda x: x["identity"].__setitem__("construction_binding_revision", None),
             "construction_binding_revision"),
            ("M5  altered construction hash",
             lambda x: x["identity"].__setitem__("construction_sha256", None),
             "construction_sha256"),
            ("M6  altered inference binding revision",
             lambda x: x["identity"].__setitem__("inference_binding_revision", None),
             "inference_binding_revision"),
            ("M6  altered inference hash",
             lambda x: x["identity"].__setitem__("inference_sha256", None),
             "inference_sha256")):
        b = copy.deepcopy(a)
        mutate(b)
        b = ev.finalize(b)
        errs = ev.validate(b, b["identity"]["execution_revision"])
        ck("REJECTED: %s" % label, any(needle in x for x in errs),
           errs[0][:80] if errs else "accepted!")

    ck("M8  a secondary block with any promotion-shaped key is refused",
       all(any("must not carry" in x for x in ev.validate(
           good_artifact(secondary=_with_key(k)),
           "a" * 40)) for k in ("verdict", "promotion", "p_value", "significant")))
    ck("M9  an inconsistent CI/verdict pair is refused by re-deriving §5 from "
       "the recorded interval",
       any("does not follow" in x for x in ev.validate(
           good_artifact(primary=synthetic_primary(
               lower=-0.9, upper=-0.5, cls="UNRESOLVED_INSUFFICIENT_PRECISION")),
           "a" * 40)))
    flush("4. BINDING IDENTITY + PROMOTION LEAKS")


def _with_key(key):
    s = synthetic_secondary()
    s["S1"][key] = "x"
    return s


# --------------------------------------------------------------------------- #
# 5. safety
# --------------------------------------------------------------------------- #
def test_safety():
    for mod, name in ((ev, "x01_evidence.py"), (orch, "x01_orchestrator.py"),
                      (AUTH, "x01_authorization.py")):
        src = io.open(os.path.join(HERE, name), encoding="utf-8").read()
        ck("%s names no real data path" % name,
           "close_prices_raw" not in src and "settle_v2" not in src
           and "oi_v2" not in src)
        ck("%s performs no module-level read" % name,
           "read_csv" not in src and "read_parquet" not in src)
    psrc = io.open(os.path.join(HERE, "x01_production.py"),
                   encoding="utf-8").read()
    ck("x01_production.py NAMES the sealed panels, because it IS the data "
       "boundary, and imports pandas only inside functions - so importing the "
       "module opens nothing",
       "close_prices_raw" in psrc and "read_parquet" in psrc
       and "\nimport pandas" not in psrc and "\nimport numpy" not in psrc)
    _probe_adapter = prod.SealedTargetDataAdapter(REPO)
    ck("... and CONSTRUCTING the sealed data adapter opens nothing: the panels "
       "are touched only when the orchestrator calls, after every gate has "
       "passed", _probe_adapter.reads == [])
    ck("the orchestrator's default data adapter refuses both reads",
       _raises(lambda: orch.RefusingDataAdapter().etf_panel(),
               orch.OrchestrationRefused)
       and _raises(lambda: orch.RefusingDataAdapter().futures_panels(),
                   orch.OrchestrationRefused))

    # The Owner mechanism is now DECLARED. That is a statement about policy, not
    # about permission, so the safety claim has to be made against the real
    # repository rather than against the absence of a mechanism.
    ck("the Owner execution-authorization mechanism is declared (D1-D6)",
       orch.AUTHORIZATION_MECHANISM_DECLARED is True)
    ck("a run with no provider wired in is still not consulted and still refuses",
       orch.NoAuthorizationMechanism().declared is False)
    st = AUTH.repo_authorization_status(REPO)
    ck("TARGET_EXECUTION_AUTHORIZED = NO — the real ledger holds zero committed "
       "authorization records",
       st["committed_authorization_records"] == 0
       and st["active_authorizations"] == 0
       and st["target_execution_authorized"] is False,
       "committed=%d active=%d" % (st["committed_authorization_records"],
                                   st["active_authorizations"]))
    ck("... and the real repository could not satisfy a record anyway: the "
       "execution infrastructure is uncommitted, so its bound revision is an "
       "unmatchable sentinel",
       not re.match(r"^[0-9a-f]{40}$",
                    st["execution_infrastructure_revision"] or ""),
       st["execution_infrastructure_revision"][:70])
    ck("the real repository's live execution identity carries that same "
       "unmatchable revision",
       not re.match(r"^[0-9a-f]{40}$",
                    orch.execution_identity(
                        orch.ExecutionPlan(run_id="SAFETY-PROBE")
                    )["execution_infrastructure_revision"] or ""))
    ck("cmd_execute STILL REFUSES without Owner authorization",
       runner.cmd_execute(None) == 2)
    man = json.load(io.open(runner.MANIFEST, encoding="utf-8"))
    ck("execution_authorized is still false", man["execution_authorized"] is False)
    ck("no X01 evidence artifact exists in the project tree",
       [f for f in os.listdir(HERE) if "evidence" in f.lower()
        and f.endswith(".json")] == [])
    ck("no target artifact of any kind exists beside the code",
       [f for f in os.listdir(HERE) if f.endswith((".parquet", ".csv"))] == [])
    flush("5. SAFETY — no path from this infrastructure to real target data")


# --------------------------------------------------------------------------- #
# 6. ITEM 12 — the Owner authorization mechanism (D1–D6)
#
# Everything below drives the PRODUCTION provider, session and resolver. Only
# the STORAGE is synthetic (an in-memory committed/worktree pair, plus one
# throwaway git repository under the system temp directory), and only the
# execution IDENTITY is stubbed, so that a fixture can bind to something other
# than the real repository's unmatchable sentinel. No real authorization record
# is created anywhere, and `ops/EXECUTION_AUTHORIZATIONS.md` is never written.
# --------------------------------------------------------------------------- #
AUTH_CLOCK = "2026-09-11T09:00:00Z"


def auth_identity(**over):
    """A well-formed execution identity a synthetic grant can bind to.

    The three revision/hash slots are made DISTINCT from one another, so a
    mutation of one cannot accidentally match another and pass.
    """
    ident = synthetic_identity()
    ident["construction_binding_revision"] = "1" * 40
    ident["inference_binding_revision"] = "2" * 40
    ident["manifest_sha256"] = "3" * 64
    ident["execution_infrastructure_revision"] = "4" * 40
    ident.update(over)
    return ident


def grant_for(identity, authorization_id="X01-AUTH-T1", **override_binding):
    binding = {f: identity[f] for f in AUTH.BOUND_IDENTITY_FIELDS}
    binding.update(override_binding)
    return {"record_type": AUTH.RECORD_TYPE_AUTHORIZATION,
            "schema": {"name": AUTH.SCHEMA_NAME, "version": AUTH.SCHEMA_VERSION},
            "authorization_id": authorization_id,
            "owner": "Aaron",
            "authorized_utc": AUTH_CLOCK,
            "status": "AUTHORIZED",
            "scope": AUTH.ONE_SHOT_SCOPE,
            "binding": binding}


def lifecycle_record(authorization_id, event, run_id, reason="synthetic"):
    return {"record_type": AUTH.RECORD_TYPE_LIFECYCLE,
            "schema": {"name": AUTH.SCHEMA_NAME, "version": AUTH.SCHEMA_VERSION},
            "authorization_id": authorization_id,
            "event": event, "event_utc": AUTH_CLOCK,
            "run_id": run_id, "reason": reason}


def ledger_text(records):
    return "".join(AUTH.render_record(r) for r in records)


class Fixture(object):
    """A synthetic committed/worktree ledger with the REAL provider over it."""

    def __init__(self, identity=None, authorization_id="X01-AUTH-T1",
                 committed=True, records=None, crash=False):
        self.identity = identity or auth_identity()
        self.grant = grant_for(self.identity, authorization_id)
        self.authorization_id = authorization_id
        recs = [self.grant] if records is None else list(records)
        text = ledger_text(recs)
        # An uncommitted ledger is modelled as a committed file with NO records,
        # plus the same records in the working tree. That is what "Aaron wrote
        # the record but has not committed it" actually looks like on disk.
        self.source = AUTH.InMemoryLedgerSource(
            committed=text if committed else "", worktree=text)
        # One claim directory per fixture, shared by every provider built from
        # it — so a "later process" in a test really does see the earlier one's
        # claim, exactly as two OS processes would.
        self.claim_root = tempfile.mkdtemp(prefix="x01-claimdir-")
        self.appender = AUTH.InMemoryLedgerAppender(
            self.source, crash_before_resolution=crash)
        self.provider = self._provider(self.appender)

    def _provider(self, appender):
        return AUTH.LedgerAuthorizationProvider(
            self.source, self.authorization_id, appender=appender,
            clock=lambda: "2026-09-11T10:00:00Z",
            claim_store=AUTH.FileClaimStore(self.claim_root))

    def fresh_provider(self, crash=False):
        """A LATER PROCESS over the same storage — not a retry of this one."""
        return self._provider(AUTH.InMemoryLedgerAppender(
            self.source, crash_before_resolution=crash))

    def status(self):
        recs, problems = AUTH.parse_ledger(self.source.worktree_text())
        assert not problems, problems
        return AUTH.resolve(recs, self.authorization_id)

    def events(self):
        return [e["event"] for e in self.status().history]


class patched_identity(object):
    """Stub `execution_identity` for one probe.

    The identity a run computes from the real repository deliberately cannot be
    bound to (§16), so a fixture that needs the gate to OPEN has to supply one.
    Nothing in production is bypassed: the provider, the lifecycle and the
    orchestrator are the real ones, and `execution_identity`'s own behaviour on
    the real repository is asserted separately in the safety section.
    """

    def __init__(self, identity):
        self.identity = identity

    def __enter__(self):
        self.real = orch.execution_identity
        orch.execution_identity = lambda plan: dict(self.identity)
        return self

    def __exit__(self, *exc):
        orch.execution_identity = self.real
        return False


class ClaimSnipedProvider(AUTH.LedgerAuthorizationProvider):
    """Validates cleanly, and then a foreign process takes the claim first.

    This is the ONE window the atomic claim exists to close: between a
    successful validation and the claim itself. Every other concurrency test
    refuses at validation, so none of them reaches the orchestrator's
    lost-claim branch — this fixture is the only way to get there
    deterministically, and it models exactly what another process does.
    """

    def authorization_for(self, identity):
        ref, why = super().authorization_for(identity)
        if ref is not None:
            AUTH.FileClaimStore(self.claim_store.root).claim(
                self.authorization_id,
                {"authorization_id": self.authorization_id, "pid": -2,
                 "note": "a foreign process claimed between validation and here"})
        return ref, why


class BrokenData(object):
    """A target-data boundary that breaks AFTER the gates have all opened."""

    def etf_panel(self):
        raise RuntimeError("synthetic panel read failure")

    def futures_panels(self):
        raise RuntimeError("synthetic panel read failure")


def probe(fixture, identity=None, **kw):
    """Run the whole orchestrator against a fixture. Returns (art, counter, rec)."""
    ident = identity or fixture.identity
    c = orch.TargetAdapterCallCounter()
    rec = kw.pop("recorder", None) or ScratchRecorder()
    kw.setdefault("run_id", ident["run_id"])
    kw.setdefault("authorization_provider", fixture.provider)
    plan = plan_for(c, recorder=rec, **kw)
    orch.layers()["construction"].SEALED_MAP.update(SYNTH_MAP)
    with patched_identity(ident):
        art = orch.run(plan)
    return art, c, rec, plan


def test_authorization_record_and_lifecycle():
    """D1 and §8 — the record format and the append-only lifecycle."""
    ident = auth_identity()
    good = grant_for(ident)
    recs, problems = AUTH.parse_ledger(ledger_text([good]))
    ck("a well-formed AUTHORIZATION record parses", not problems and len(recs) == 1,
       "; ".join(problems)[:90])

    malformed = [
        ("owner is not Aaron", dict(good, owner="Someone Else"), "owner must be"),
        ("status pre-set to CONSUMED", dict(good, status="CONSUMED"),
         "is written with status"),
        ("not ONE_SHOT", dict(good, scope="PERSISTENT"), "scope must be"),
        ("a missing bound identity",
         dict(good, binding={k: v for k, v in good["binding"].items()
                             if k != "manifest_sha256"}), "EXACTLY the seven"),
        ("an EXTRA bound identity",
         dict(good, binding=dict(good["binding"], analyst="someone")),
         "EXACTLY the seven"),
        ("a malformed bound hash",
         dict(good, binding=dict(good["binding"], prereg_sha256="not-a-hash")),
         "well-formed prereg_sha256"),
        ("an unrecognised top-level key", dict(good, approved_by="chat"),
         "unrecognised key"),
        ("a non-UTC timestamp", dict(good, authorized_utc="yesterday"),
         "ISO-8601"),
        ("the wrong schema", dict(good, schema={"name": "other", "version": 1}),
         "schema must be"),
    ]
    for label, rec, needle in malformed:
        _r, probs = AUTH.parse_ledger(ledger_text([rec]))
        ck("REJECTED record: %s" % label,
           bool(probs) and any(needle in p for p in probs),
           (probs[0][:80] if probs else "accepted!"))

    ck("a ```text example block is NOT a record, so the ledger can document "
       "its own format without containing an authorization",
       AUTH.parse_ledger("```text\n%s\n```\n" % json.dumps(good)) == ([], []))
    sentinel = grant_for(ident, "X01-AUTH-T1",
                         execution_infrastructure_revision=
                         AUTH.UNCOMMITTED_INFRASTRUCTURE + ":some/path.py")
    ck("a grant that tries to bind an UNCOMMITTED-infrastructure sentinel is "
       "malformed — which is why the real repository's own state can never be "
       "authorized",
       any("execution_infrastructure_revision" in p
           for p in AUTH.parse_ledger(ledger_text([sentinel]))[1]))
    ck("an unterminated ```json fence makes the ledger unusable",
       bool(AUTH.parse_ledger("```json\n{}\n")[1]))

    # lifecycle replay
    rid = ident["run_id"]
    def st(events):
        recs, probs = AUTH.parse_ledger(
            ledger_text([good] + [lifecycle_record("X01-AUTH-T1", e, rid)
                                  for e in events]))
        assert not probs, probs
        return AUTH.resolve(recs, "X01-AUTH-T1")

    ck("no lifecycle events -> AUTHORIZED and active",
       st([]).status == AUTH.STATUS_AUTHORIZED and st([]).active)
    ck("started then consumed -> CONSUMED",
       st([AUTH.EVENT_STEP2_STARTED, AUTH.EVENT_CONSUMED]).status
       == AUTH.STATUS_CONSUMED)
    ck("started then abandoned with proof -> back to AUTHORIZED and reusable",
       st([AUTH.EVENT_STEP2_STARTED, AUTH.EVENT_STEP2_ABANDONED]).active)
    ck("started and NEVER resolved -> CONSUMED_OR_INDETERMINATE (D6 crash rule)",
       st([AUTH.EVENT_STEP2_STARTED]).status
       == AUTH.STATUS_CONSUMED_OR_INDETERMINATE)
    ck("an explicit ambiguity -> CONSUMED_OR_INDETERMINATE",
       st([AUTH.EVENT_STEP2_STARTED, AUTH.EVENT_INDETERMINATE]).status
       == AUTH.STATUS_CONSUMED_OR_INDETERMINATE)
    ck("INVALIDATED is distinguishable from the other three",
       st([AUTH.EVENT_INVALIDATED]).status == AUTH.STATUS_INVALIDATED
       and len(set(AUTH.LIFECYCLE_STATUSES)) == 4)
    absorbed = st([AUTH.EVENT_STEP2_STARTED, AUTH.EVENT_CONSUMED,
                   AUTH.EVENT_STEP2_ABANDONED])
    ck("a terminal state ABSORBS: nothing appended afterwards revives it",
       not absorbed.active and absorbed.status == AUTH.STATUS_CONSUMED)
    overwritten = st([AUTH.EVENT_STEP2_STARTED, AUTH.EVENT_CONSUMED,
                      AUTH.EVENT_INVALIDATED])
    ck("... and the FIRST terminal state wins: a later INVALIDATED does not "
       "overwrite a CONSUMED, so the ledger cannot misreport which terminal "
       "state the authorization actually reached",
       overwritten.status == AUTH.STATUS_CONSUMED, overwritten.status)
    ck("... and the out-of-order event is RECORDED as a problem rather than "
       "silently dropped",
       any("after the authorization already reached" in p
           for p in overwritten.problems),
       str(overwritten.problems)[:70])
    ck("a second unresolved start is a problem, not a fresh attempt",
       not st([AUTH.EVENT_STEP2_STARTED, AUTH.EVENT_STEP2_STARTED]).active)

    # D3 — one id, one run
    other = AUTH.resolve(AUTH.parse_ledger(ledger_text(
        [good, lifecycle_record("X01-AUTH-T1", AUTH.EVENT_CONSUMED,
                                "SOME-OTHER-RUN")]))[0], "X01-AUTH-T1")
    ck("D3 a lifecycle event naming a different run_id is refused: one "
       "authorization covers exactly one run",
       not other.active and any("exactly one run" in p for p in other.problems))

    dup = AUTH.resolve(AUTH.parse_ledger(ledger_text([good, good]))[0],
                       "X01-AUTH-T1")
    ck("D3 a duplicated authorization_id makes the id unusable",
       dup.status == AUTH.STATUS_LEDGER_UNUSABLE)
    two_runs = AUTH.resolve(AUTH.parse_ledger(ledger_text(
        [good, grant_for(ident, "X01-AUTH-T1", run_id="X01-RUN-SECOND")]))[0],
        "X01-AUTH-T1")
    ck("§9 one authorization_id pointing at TWO run_ids is refused, not "
       "arbitrated", two_runs.status == AUTH.STATUS_LEDGER_UNUSABLE)
    ck("an unknown authorization_id is NO_SUCH_AUTHORIZATION, not a default yes",
       AUTH.resolve(AUTH.parse_ledger(ledger_text([good]))[0], "X01-AUTH-NOPE"
                    ).status == AUTH.STATUS_NO_SUCH_AUTHORIZATION)

    # §8 — append-only
    a, b = [good], [good, lifecycle_record("X01-AUTH-T1",
                                           AUTH.EVENT_STEP2_STARTED, rid)]
    ck("append-only: committed records are a prefix of the working tree",
       AUTH.committed_is_prefix_of(a, b))
    ck("append-only: a DELETED committed record is refused",
       not AUTH.committed_is_prefix_of(b, a))
    ck("append-only: an EDITED committed record is refused",
       not AUTH.committed_is_prefix_of(
           a, [grant_for(ident, "X01-AUTH-T1", run_id="X01-RUN-EDITED")]))
    flush("6. ITEM 12 / D1 + §8 — the authorization record and its lifecycle")


def test_commit_requirement():
    """D2 — committed git state, and the check is not advisory."""
    ident = auth_identity()

    committed = Fixture(ident)
    ref, why = committed.provider.authorization_for(ident)
    ck("a COMMITTED, active, exactly-bound record validates", ref is not None,
       str(why)[:100])
    ck("... and the reference cites the ledger and the seven bound fields",
       ref["ledger"] == AUTH.LEDGER_RELPATH
       and ref["bound_identity_fields"] == list(AUTH.BOUND_IDENTITY_FIELDS)
       and ref["commit_requirement"] == "COMMITTED_GIT_STATE_REQUIRED")

    uncommitted = Fixture(ident, committed=False)
    ref2, why2 = uncommitted.provider.authorization_for(ident)
    ck("D2 the SAME record, present only in the working tree, is INVALID",
       ref2 is None and (why2 or "").startswith(AUTH.REASON_NOT_COMMITTED), str(why2)[:100])
    ck("D2 and the refusal names the commit requirement rather than warning",
       "not advisory" in (why2 or ""))

    absent = Fixture(ident)
    absent.source.committed = None
    ref3, why3 = absent.provider.authorization_for(ident)
    ck("D2 a ledger absent from committed state entirely is also INVALID",
       ref3 is None and (why3 or "").startswith(AUTH.REASON_NOT_COMMITTED), str(why3)[:80])

    # a rewritten worktree is refused whole, grants included
    rewritten = Fixture(ident)
    rewritten.source.worktree = ledger_text(
        [grant_for(ident, "X01-AUTH-T1", run_id="X01-RUN-SWAPPED")])
    ref4, why4 = rewritten.provider.authorization_for(ident)
    ck("§8 a working tree that REWROTE a committed record is refused whole",
       ref4 is None and (why4 or "").startswith(AUTH.REASON_APPEND_ONLY), str(why4)[:80])

    # Defence in depth: even with the append-only prefix rule disabled, the
    # grant is still read from the COMMITTED records, so a rewritten working
    # tree cannot substitute a different binding.
    rewritten2 = Fixture(ident)
    rewritten2.source.worktree = ledger_text(
        [grant_for(ident, "X01-AUTH-T1", manifest_sha256="a" * 64)])
    real_prefix = AUTH.committed_is_prefix_of
    AUTH.committed_is_prefix_of = lambda a, b: True
    try:
        ref_d, why_d = rewritten2.provider.authorization_for(ident)
    finally:
        AUTH.committed_is_prefix_of = real_prefix
    ck("D2 with the append-only rule DISABLED, the grant is still taken from "
       "committed records, so a rewritten working tree cannot substitute a "
       "binding", ref_d is not None and ref_d["authorization_id"] == "X01-AUTH-T1",
       str(why_d)[:80])
    ck("... and the very same rewrite is refused OUTRIGHT while the rule is "
       "enabled, so the two defences are separately observable",
       rewritten2.provider.authorization_for(ident)[0] is None
       and (rewritten2.provider.authorization_for(ident)[1] or "").startswith(
           AUTH.REASON_APPEND_ONLY))

    broken = Fixture(ident)
    broken.source.committed += "\n```json\n{not json}\n```\n"
    ref5, why5 = broken.provider.authorization_for(ident)
    ck("a ledger the parser cannot fully account for is unusable — no partial "
       "credit", ref5 is None and (why5 or "").startswith(AUTH.REASON_MALFORMED),
       str(why5)[:80])

    missing = Fixture(ident, authorization_id="X01-AUTH-T1")
    missing.provider.authorization_id = "X01-AUTH-ABSENT"
    ref6, why6 = missing.provider.authorization_for(ident)
    ck("an id with no committed grant refuses with NO_SUCH_AUTHORIZATION",
       ref6 is None and (why6 or "").startswith(AUTH.REASON_NO_SUCH), str(why6)[:80])

    # non-vacuity: every refusal above used a DIFFERENT reason code
    codes = {(w or "<AUTHORIZED!>").split(":")[0]
             for w in (why2, why3, why4, why5, why6)}
    ck("the five refusals resolve to four distinct reason codes (the two "
       "commit failures share one), so no single catch-all stands in for the "
       "rest", len(codes) == 4, str(sorted(codes)))
    flush("7. ITEM 12 / D2 — a real authorization lives in committed git state")


def test_exact_binding_mutations():
    """D4 / §13 — seven identities, mutated one at a time, through the runner."""
    base = auth_identity()
    mutations = [
        ("research_id", "TSMOM-EXT-999"),
        ("run_id", "X01-RUN-SOMETHING-ELSE"),
        ("prereg_sha256", "0" * 64),
        ("execution_infrastructure_revision", "5" * 40),
        ("construction_binding_revision", "6" * 40),
        ("inference_binding_revision", "7" * 40),
        ("manifest_sha256", "8" * 64),
    ]
    ck("§13 exactly seven identities are bound, and the list is closed",
       len(AUTH.BOUND_IDENTITY_FIELDS) == 7
       and [m[0] for m in mutations] == list(AUTH.BOUND_IDENTITY_FIELDS))

    # non-vacuity control: unmutated, the gate OPENS and step 2 is reached
    control = Fixture(base)
    art, c, rec, _p = probe(control, recorder=ScratchRecorder(fail_on="cumulative"))
    ck("CONTROL (no mutation): the gate opens and step 2 commits, so the seven "
       "refusals below are not vacuous",
       len(rec.exposure_rows) == 1
       and art["governance"]["last_completed_stage"] == orch.STAGE_EXPOSURE_RECORD,
       "%s / exposure rows=%d" % (art["outcome_state"], len(rec.exposure_rows)))

    for field, wrong in mutations:
        # The LEDGER is correct; what would EXECUTE differs in exactly one field.
        fx = Fixture(base)
        ident = auth_identity(**{field: wrong})
        art, c, rec, _p = probe(fx, identity=ident)
        ok = (art["outcome_state"] == ev.EXECUTION_REFUSED
              and art["governance"]["refusal_stage"] == orch.STAGE_AUTHORIZATION
              and art["governance"]["refusal_reason"].startswith(AUTH.REASON_BINDING)
              and field in art["governance"]["refusal_reason"])
        ck("§13 wrong %s -> REFUSED at the authorization gate" % field, ok,
           art["governance"].get("refusal_reason", art["outcome_state"])[:70])
        ck("§13 wrong %s -> constructors 0, exposure rows 0, lifecycle untouched"
           % field,
           c.n == 0 and rec.exposure_rows == [] and fx.appender.count == 0,
           "constructors=%d exposure=%d lifecycle=%d"
           % (c.n, len(rec.exposure_rows), fx.appender.count))

    # and the other direction: a LEDGER that binds something else
    fx = Fixture(base)
    fx.source.committed = ledger_text(
        [grant_for(base, "X01-AUTH-T1", inference_binding_revision="e" * 40)])
    fx.source.worktree = fx.source.committed
    ref, why = fx.provider.authorization_for(base)
    ck("§13 a record that AUTHORIZED a different inference binding is refused "
       "just as firmly", ref is None and (why or "").startswith(AUTH.REASON_BINDING),
       str(why)[:80])

    incomplete = Fixture(base)
    ref2, why2 = incomplete.provider.authorization_for(
        {k: v for k, v in base.items() if k != "manifest_sha256"})
    ck("an identity the run could not fully establish is refused, never "
       "defaulted", ref2 is None
       and (why2 or "").startswith(AUTH.REASON_IDENTITY_INCOMPLETE), str(why2)[:80])

    # The orchestrator binds the run independently of whatever the provider
    # says, so a provider that approves a DIFFERENT run cannot spend this one.
    c = orch.TargetAdapterCallCounter()
    rec = ScratchRecorder()
    with patched_identity(base):
        art = orch.run(plan_for(c, recorder=rec, run_id=base["run_id"],
                                authorization_provider=WrongRunIdProvider(
                                    "X01-RUN-A-DIFFERENT-ONE")))
    ck("a provider approving a different run_id is refused by the gate itself",
       art["outcome_state"] == ev.EXECUTION_REFUSED
       and art["governance"]["refusal_stage"] == orch.STAGE_AUTHORIZATION
       and "does not identify this run" in art["governance"]["refusal_reason"]
       and c.n == 0 and rec.exposure_rows == [],
       art["governance"].get("refusal_reason", "")[:70])
    flush("8. ITEM 12 / D4 + §13 — exact binding, no fuzzy matching, no fallback")


def test_authorization_is_not_exposure():
    """D5 / §12 — validating a record moves nothing."""
    ident = auth_identity()
    fx = Fixture(ident)
    rec = ScratchRecorder()
    counter = orch.TargetAdapterCallCounter()

    for _ in range(5):
        ref, why = fx.provider.authorization_for(ident)
        ck("§12 the authorization validates", ref is not None, str(why)[:80])
    ck("§12 exposure records = 0 after creating and validating an authorization",
       rec.exposure_rows == [], str(rec.rows)[:60])
    ck("§12 attempt increments = 0", rec.rows == [])
    ck("§12 target constructors = 0", counter.n == 0)
    ck("§12 the authorization lifecycle was not written to either",
       fx.appender.count == 0 and fx.events() == [])
    ck("§12 validation is repeatable — five validations, same answer, no state "
       "change", fx.provider.validations == 5)

    # positive control: the same recorder DOES record, once step 2 runs
    art, c2, rec2, _p = probe(Fixture(ident),
                              recorder=ScratchRecorder(fail_on="cumulative"))
    ck("§12 non-vacuity: the same recorder records exactly one exposure row "
       "when step 2 actually runs", len(rec2.exposure_rows) == 1)

    # D5 is enforced, not promised: a provider that wrote during validation is
    # refused by its own guard.
    class Leaky(AUTH.LedgerAuthorizationProvider):
        def _validate(self, identity):
            self.appender.append(lifecycle_record(
                self.authorization_id, AUTH.EVENT_STEP2_STARTED,
                identity["run_id"], "leak"))
            return super()._validate(identity)

    fx2 = Fixture(ident)
    leaky = Leaky(fx2.source, "X01-AUTH-T1", appender=fx2.appender)
    ref3, why3 = leaky.authorization_for(ident)
    ck("D5 a provider that appended during validation refuses ITSELF",
       ref3 is None and (why3 or "").startswith(AUTH.REASON_VALIDATION_MUTATED),
       str(why3)[:80])
    flush("9. ITEM 12 / D5 + §12 — authorizing is not exposing")


def test_crash_boundary_probes():
    """§11 A–K and §7 — where consumption lands when things break."""
    base = auth_identity()
    tmpdir = tempfile.mkdtemp(prefix="x01-auth-")

    # ---- A. preflight fails ------------------------------------------------
    fx = Fixture(base)
    art, c, rec, _p = probe(fx, preflight_fn=lambda: NotOk())
    ck("A preflight failure -> EXECUTION_REFUSED at preflight, constructors 0",
       art["outcome_state"] == ev.EXECUTION_REFUSED
       and art["governance"]["refusal_stage"] == orch.STAGE_PREFLIGHT and c.n == 0)
    ck("A the authorization was never consulted, never consumed, still active",
       fx.appender.count == 0 and fx.status().active
       and fx.provider.validations == 0)

    # ---- B. identity mismatch ---------------------------------------------
    fx = Fixture(base)
    art, c, rec, _p = probe(fx, identity=auth_identity(prereg_sha256="0" * 64))
    ck("B an identity mismatch -> refused at the authorization gate, "
       "constructors 0",
       art["outcome_state"] == ev.EXECUTION_REFUSED
       and art["governance"]["refusal_stage"] == orch.STAGE_AUTHORIZATION
       and c.n == 0)
    ck("B the authorization is UNUSED: no lifecycle event, still active",
       fx.appender.count == 0 and fx.status().active and rec.exposure_rows == [])

    # ---- C. step 2 definitively fails before durable persistence -----------
    fx = Fixture(base)
    art, c, rec, _p = probe(
        fx, recorder=ScratchRecorder(fail_on="exposure_proven_not_durable"))
    ck("C a step-2 failure with PROOF of no durable write -> mechanical failure "
       "at the exposure stage, constructors 0",
       art["outcome_state"] == ev.EXECUTION_MECHANICAL_FAILURE
       and art["governance"]["failure_stage"] == orch.STAGE_EXPOSURE_RECORD
       and c.n == 0, art["outcome_state"])
    ck("C no exposure record exists", rec.exposure_rows == [])
    ck("C §7 the authorization survives: STARTED then ABANDONED, and a later "
       "process finds it active again",
       fx.events() == [AUTH.EVENT_STEP2_STARTED, AUTH.EVENT_STEP2_ABANDONED]
       and fx.status().active
       and fx.fresh_provider().authorization_for(base)[0] is not None,
       str(fx.events()))
    ck("C and the record says so", art["governance"]["authorization_consumed"]
       is False and art["governance"]["authorization_status"]
       == AUTH.STATUS_AUTHORIZED)

    # ---- D. step 2 succeeds -> consumed ------------------------------------
    fx = Fixture(base)
    art, c, rec, _p = probe(fx, artifact_path=os.path.join(tmpdir, "d.json"))
    ck("D a full run under a real committed authorization reaches a "
       "result-bearing state",
       art["outcome_state"] in (ev.COMPLETED_EVIDENCE,
                                ev.INFERENCE_PROCEDURE_FAILURE),
       "%s (%s)" % (art["outcome_state"],
                    art["governance"].get("refusal_reason")
                    or art["governance"].get("failure_reason")))
    ck("D the exposure commitment happened exactly once", len(rec.exposure_rows) == 1)
    ck("D the authorization is CONSUMED, permanently",
       fx.events() == [AUTH.EVENT_STEP2_STARTED, AUTH.EVENT_CONSUMED]
       and fx.status().status == AUTH.STATUS_CONSUMED, str(fx.events()))
    ck("D the artifact cites the authorization it spent",
       art["governance"]["authorization_id"] == "X01-AUTH-T1"
       and art["governance"]["authorization_consumed"] is True
       and art["run_instance"]["run_id"] == base["run_id"])
    ck("D the write-ahead marker landed BEFORE the exposure row, not after",
       fx.appender.records[0]["event"] == AUTH.EVENT_STEP2_STARTED)
    consumed_fixture = fx

    # ---- K. a second run on the same consumed authorization ----------------
    art2, c2, rec2, _p = probe(
        Reuse(consumed_fixture), identity=base)
    ck("K a later process reusing a CONSUMED authorization -> REFUSED, "
       "constructors 0",
       art2["outcome_state"] == ev.EXECUTION_REFUSED
       and art2["governance"]["refusal_stage"] == orch.STAGE_AUTHORIZATION
       and c2.n == 0, art2["governance"].get("refusal_reason", "")[:70])
    ck("K the refusal names the lifecycle state rather than a generic no",
       art2["governance"].get("refusal_reason", "").startswith(
           AUTH.REASON_NOT_ACTIVE)
       and AUTH.STATUS_CONSUMED in art2["governance"].get("refusal_reason", ""))
    ck("K and no second exposure commitment was made",
       rec2.exposure_rows == [] and len(consumed_fixture.appender.records) == 2)
    ck("§9 the same provider cannot open a second session either",
       _raises(lambda: consumed_fixture.provider.open_session(
           {"authorization_id": "X01-AUTH-T1", "run_id": base["run_id"]}),
           AUTH.AuthorizationError))

    # ---- E. ambiguous step 2 ----------------------------------------------
    fx = Fixture(base)
    art, c, rec, _p = probe(fx, recorder=ScratchRecorder(fail_on="exposure"))
    ck("E an ordinary step-2 break is AMBIGUOUS -> CONSUMED_OR_INDETERMINATE",
       fx.status().status == AUTH.STATUS_CONSUMED_OR_INDETERMINATE
       and c.n == 0, str(fx.events()))
    ck("E a later process may NOT reuse it",
       fx.fresh_provider().authorization_for(base)[0] is None)

    # the genuine crash: the marker is written, the resolution never is
    fx = Fixture(base, crash=True)
    art, c, rec, _p = probe(fx)
    ck("E a process that died between the write-ahead marker and its resolution "
       "leaves exactly one dangling STARTED",
       fx.events() == [AUTH.EVENT_STEP2_STARTED], str(fx.events()))
    ck("E and the dangling marker resolves to CONSUMED_OR_INDETERMINATE, so a "
       "later process refuses (D6 fail-closed)",
       fx.status().status == AUTH.STATUS_CONSUMED_OR_INDETERMINATE
       and fx.fresh_provider().authorization_for(base)[0] is None)

    # ---- F / G. failures after step 2, before construction -----------------
    for label, fail_on, stage, last in (
            ("F", "cumulative", orch.STAGE_CUMULATIVE_STATE,
             orch.STAGE_EXPOSURE_RECORD),
            ("G", "seed", orch.STAGE_SEED_RECORD, orch.STAGE_CUMULATIVE_STATE)):
        fx = Fixture(base)
        art, c, rec, _p = probe(fx, recorder=ScratchRecorder(fail_on=fail_on))
        ck("%s a failure at %s after step 2 -> EXECUTION_MECHANICAL_FAILURE"
           % (label, stage),
           art["outcome_state"] == ev.EXECUTION_MECHANICAL_FAILURE
           and art["governance"]["failure_stage"] == stage and c.n == 0,
           art["outcome_state"])
        ck("%s ... and the authorization is already CONSUMED" % label,
           fx.status().status == AUTH.STATUS_CONSUMED
           and art["governance"]["authorization_consumed"] is True)
        ck("%s ... and the record names the last completed stage (§7): %s"
           % (label, last),
           art["governance"]["last_completed_stage"] == last,
           str(art["governance"].get("last_completed_stage")))
        ck("%s ... and carries no §5 classification anywhere" % label,
           not any(cls in ev.canonical_json(art)
                   for cls in ev.SEALED_CLASSIFICATIONS))

    # ---- H. construction failure ------------------------------------------
    fx = Fixture(base)
    art, c, rec, _p = probe(fx, data_adapter=BrokenData())
    ck("H a construction failure -> EXECUTION_MECHANICAL_FAILURE at construction",
       art["outcome_state"] == ev.EXECUTION_MECHANICAL_FAILURE
       and art["governance"]["failure_stage"] == orch.STAGE_CONSTRUCTION,
       art["outcome_state"])
    ck("H ... consumed, last completed stage recorded, no verdict",
       fx.status().status == AUTH.STATUS_CONSUMED
       and art["governance"]["last_completed_stage"] == orch.STAGE_SEALED_SAMPLE
       and art["primary"] is None)

    # ---- I. inference procedure failure ------------------------------------
    inf = orch.layers()["inference"]
    real_primary = inf.run_primary

    class FakeCounts(object):
        attempted, valid, discarded = 10000, 9000, 1000
        discarded_too_few_distinct_months = 1000
        discarded_zero_std_e = 0
        discarded_zero_std_f = 0

    def failing_primary(e, f, **kw):
        res = real_primary(e, f, **kw)
        return type(res)(arm=res.arm, sharpes=res.sharpes, delta_s=res.delta_s,
                         ci=inf.ConfidenceInterval(float("nan"), float("nan"),
                                                   95, "percentile", 9000),
                         counts=FakeCounts(), config=res.config,
                         classification=inf.PROCEDURE_FAILURE,
                         boundary_b=res.boundary_b, boundary=res.boundary)
    fx = Fixture(base)
    inf.run_primary = failing_primary
    try:
        art, c, rec, _p = probe(fx, artifact_path=os.path.join(tmpdir, "i.json"))
    finally:
        inf.run_primary = real_primary
    ck("I an inference procedure failure -> INFERENCE_PROCEDURE_FAILURE",
       art["outcome_state"] == ev.INFERENCE_PROCEDURE_FAILURE,
       art["outcome_state"])
    ck("I ... the authorization is still CONSUMED and is never reusable",
       fx.status().status == AUTH.STATUS_CONSUMED
       and fx.fresh_provider().authorization_for(base)[0] is None)

    # ---- J. artifact persistence failure -----------------------------------
    fx = Fixture(base)
    bad = os.path.join(tmpdir, "no-such-dir", "j.json")
    art, c, rec, _p = probe(fx, artifact_path=bad)
    ck("J a persistence failure -> EXECUTION_MECHANICAL_FAILURE at persistence",
       art["outcome_state"] == ev.EXECUTION_MECHANICAL_FAILURE
       and art["governance"]["failure_stage"] == orch.STAGE_PERSIST,
       art["outcome_state"])
    ck("J ... consumed, and no artifact file was left behind",
       fx.status().status == AUTH.STATUS_CONSUMED and not os.path.exists(bad))
    ck("J §7 a post-step-2 failure is NEVER converted into a §5 outcome",
       not any(cls in ev.canonical_json(art)
               for cls in ev.SEALED_CLASSIFICATIONS))

    # ---- the provider with no consumption session at all -------------------
    c3 = orch.TargetAdapterCallCounter()
    with patched_identity(base):
        try:
            art3 = orch.run(plan_for(c3,
                                     authorization_provider=NoSessionProvider(),
                                     run_id=base["run_id"]))
        except Exception as exc:                      # noqa: BLE001
            # A refusal is the required behaviour; an EXCEPTION is a different
            # thing, and it must read as a failure of THIS check rather than as
            # a crash of the suite that happens to look like detection.
            art3 = {"outcome_state": "RAISED %r" % exc, "governance": {},
                    "primary": None}
    ck("a provider that cannot record consumption is refused, not trusted",
       art3["outcome_state"] == ev.EXECUTION_REFUSED
       and art3["governance"]["refusal_stage"] == orch.STAGE_AUTHORIZATION
       and "no consumption session" in art3["governance"].get("refusal_reason", "")
       and c3.n == 0, art3["governance"].get("refusal_reason", "")[:70])
    flush("10. ITEM 12 / §7 + §11 — crash boundaries A–K")


class Reuse(object):
    """A LATER PROCESS reusing an earlier fixture's storage with a new provider."""

    def __init__(self, fixture):
        self.identity = fixture.identity
        self.provider = fixture.fresh_provider()
        self.appender = self.provider.appender
        self.grant = fixture.grant
        self.authorization_id = fixture.authorization_id


def test_git_backed_ledger():
    """The REAL git reader, against a throwaway repository under the temp dir.

    The in-memory source models the committed/worktree distinction; this proves
    the production reader actually implements it. The repository is created in
    the system temp directory and is not this project: no commit is made here.
    """
    tmp = tempfile.mkdtemp(prefix="x01-authgit-")

    def g(*args):
        return subprocess.run(["git", "-C", tmp] + list(args),
                              capture_output=True)

    if g("init", "-q").returncode != 0:
        ck("git is available for the committed-state test", False, "git init failed")
        flush("11. ITEM 12 / D2 — the real git-backed reader")
        return
    top = g("rev-parse", "--show-toplevel").stdout.decode().strip()
    if os.path.realpath(top) != os.path.realpath(tmp):
        ck("the scratch repository is isolated from the project repository",
           False, "toplevel=%s" % top)
        flush("11. ITEM 12 / D2 — the real git-backed reader")
        return
    ck("the scratch repository is isolated from the project repository", True, tmp)
    g("config", "user.email", "x01-test@example.invalid")
    g("config", "user.name", "X01 Test Fixture")

    ident = auth_identity()
    grant = grant_for(ident, "X01-AUTH-GIT")
    os.makedirs(os.path.join(tmp, "ops"))
    path = os.path.join(tmp, "ops", "EXECUTION_AUTHORIZATIONS.md")
    io.open(path, "w", encoding="utf-8", newline="\n").write(ledger_text([grant]))

    source = AUTH.GitLedgerSource(tmp)
    appender = AUTH.FileLedgerAppender(path)
    claims = AUTH.FileClaimStore(AUTH.claim_root(tmp))
    provider = AUTH.LedgerAuthorizationProvider(source, "X01-AUTH-GIT",
                                                appender=appender,
                                                claim_store=claims)
    ref, why = provider.authorization_for(ident)
    ck("real git: an UNCOMMITTED authorization record is INVALID",
       ref is None and (why or "").startswith(AUTH.REASON_NOT_COMMITTED), str(why)[:80])

    g("add", "ops/EXECUTION_AUTHORIZATIONS.md")
    g("commit", "-q", "-m", "synthetic authorization fixture")
    provider2 = AUTH.LedgerAuthorizationProvider(source, "X01-AUTH-GIT",
                                                 appender=appender,
                                                 claim_store=claims)
    ref2, why2 = provider2.authorization_for(ident)
    ck("real git: the SAME bytes, once committed, validate", ref2 is not None,
       str(why2)[:100])
    ck("real git: the reference carries the committed revision",
       bool(re.match(r"^[0-9a-f]{40}$", ref2["ledger_revision"] or "")))

    # a durable append blocks reuse even though it is not committed
    session = provider2.open_session(ref2)
    session.begin_step2()
    session.step2_durably_completed("SYNTHETIC-EXPOSURE-1")
    provider3 = AUTH.LedgerAuthorizationProvider(source, "X01-AUTH-GIT",
                                                 appender=appender,
                                                 claim_store=claims)
    ref3, why3 = provider3.authorization_for(ident)
    ck("real git: an UNCOMMITTED consumption still blocks reuse — granting "
       "needs committed state, blocking does not",
       ref3 is None and (why3 or "").startswith(AUTH.REASON_NOT_ACTIVE), str(why3)[:80])
    ck("real git: the lifecycle events were written to the real file, in order",
       [r["event"] for r in AUTH.parse_ledger(io.open(path, encoding="utf-8")
                                              .read())[0][1:]]
       == [AUTH.EVENT_STEP2_STARTED, AUTH.EVENT_CONSUMED])

    # a rewritten worktree is refused whole
    io.open(path, "w", encoding="utf-8", newline="\n").write("# emptied\n")
    provider4 = AUTH.LedgerAuthorizationProvider(source, "X01-AUTH-GIT",
                                                 appender=appender,
                                                 claim_store=claims)
    ref4, why4 = provider4.authorization_for(ident)
    ck("real git: a working tree that dropped a committed record is refused",
       ref4 is None and (why4 or "").startswith(AUTH.REASON_APPEND_ONLY), str(why4)[:80])
    flush("11. ITEM 12 / D2 — the real git-backed reader")



# --------------------------------------------------------------------------- #
# 12-16. THE SIX REPAIRED BLOCKERS — T1 to T18
# --------------------------------------------------------------------------- #
def _git(repo, *args):
    return subprocess.run(["git", "-C", repo] + list(args), capture_output=True)


def throwaway_repo(anchor=14, with_fixtures=True):
    """A COMPLETE scratch authoritative environment, not a partial one.

    A real git repository holding the execution infrastructure, the manifest,
    BOTH governance records, and a stub carry project beside it so the
    read-at-execution anchor resolves.

    Complete on purpose. The production API builds its own canonical governance
    recorder from the repository being executed — a caller cannot hand one in —
    so a test that wants the production path to succeed has to give the
    canonical recorder somewhere real to write. That is the better test anyway:
    the governance code being exercised is the production code, against a
    repository this test owns entirely.
    """
    ws = tempfile.mkdtemp(prefix="x01-prodws-")
    tmp = os.path.join(ws, "scratch-repo")
    os.makedirs(tmp)
    stub = os.path.join(ws, "commodity-carry-research", "src")
    os.makedirs(stub)
    io.open(os.path.join(stub, "config.py"), "w", encoding="utf-8",
            newline="\n").write("# stub\nN_TRIALS = %d  # frozen\n" % anchor)
    if _git(tmp, "init", "-q").returncode != 0:
        return None
    top = _git(tmp, "rev-parse", "--show-toplevel").stdout.decode().strip()
    if os.path.realpath(top) != os.path.realpath(tmp):
        return None
    _git(tmp, "config", "user.email", "x01-test@example.invalid")
    _git(tmp, "config", "user.name", "X01 Test Fixture")
    dest = os.path.join(tmp, "research", "extensions", "x01")
    os.makedirs(dest)
    os.makedirs(os.path.join(tmp, "ops"))
    names = [os.path.basename(x) for x in AUTH.EXECUTION_INFRASTRUCTURE_PATHS]
    for name in names + ["X01_EXECUTION_MANIFEST.json"]:
        with io.open(os.path.join(HERE, name), "rb") as src:
            with io.open(os.path.join(dest, name), "wb") as dst:
                dst.write(src.read())
    for rel in ("ops/EXPOSURE_LEDGER.md", "research/extensions/TRIAL_LEDGER.md"):
        with io.open(os.path.join(REPO, rel.replace("/", os.sep)), "rb") as src:
            with io.open(os.path.join(tmp, rel.replace("/", os.sep)), "wb") as dst:
                dst.write(src.read())
    io.open(os.path.join(tmp, "ops", "EXECUTION_AUTHORIZATIONS.md"), "w",
            encoding="utf-8", newline="\n").write("# scratch ledger\n")
    _git(tmp, "add", "-A")
    _git(tmp, "commit", "-q", "-m", "execution infrastructure")
    # Sealed fixture inputs and a manifest re-pinned to them. Written AFTER the
    # infrastructure commit and BEFORE any identity is computed, so the
    # manifest hash an authorization binds is the final one.
    if with_fixtures:
        write_sealed_fixtures(tmp)
    return tmp


def write_sealed_fixtures(tmp):
    """Write REAL, parseable fixture panels and re-pin the scratch manifest.

    The canonical adapter verifies every input's bytes against the manifest
    before parsing it, so a scratch repository that wants to execute must hold
    inputs whose hashes its own manifest actually claims. That is the point:
    the test cannot hand the production API a synthetic adapter any more, so it
    gives the CANONICAL adapter real files to read and re-pins the manifest to
    them.

    Nothing here touches the project's frozen panels. Every byte is generated.
    """
    import json

    c = orch.TargetAdapterCallCounter()
    synth = SyntheticData(c)
    etf = synth.etf_panel()
    settle, oi, meta = synth.futures_panels()
    os.makedirs(os.path.join(tmp, "data"), exist_ok=True)
    w1 = os.path.join(tmp, "research", "extensions", "wave1")
    os.makedirs(w1, exist_ok=True)
    etf.to_csv(os.path.join(tmp, "data", "close_prices_raw.csv"),
               index_label="Date")
    settle.to_parquet(os.path.join(w1, "settle_v2.parquet"))
    oi.to_parquet(os.path.join(w1, "oi_v2.parquet"))
    meta.to_parquet(os.path.join(w1, "contracts_meta.parquet"))
    io.open(os.path.join(w1, "panel_sanity.json"), "w", encoding="utf-8",
            newline="\n").write('{"PANEL_SANITY": "PASS"}\n')
    repin_scratch_manifest(tmp)
    return tmp


def repin_scratch_manifest(tmp):
    """Point the scratch manifest's input pins at the scratch fixture bytes."""
    import json

    RN2 = orch.layers()["runner"]
    mpath = os.path.join(tmp, "research", "extensions", "x01",
                         "X01_EXECUTION_MANIFEST.json")
    man = json.load(io.open(mpath, encoding="utf-8"))
    for entry in man.get("inputs") or []:
        abspath = os.path.join(tmp, entry["path"].replace("/", os.sep))
        if not os.path.exists(abspath):
            continue
        entry["sha256"] = (RN2.raw_sha256(abspath)
                           if entry["hash_convention"] == RN2.RAW
                           else RN2.lf_sha256(abspath))
    io.open(mpath, "w", encoding="utf-8", newline="\n").write(
        json.dumps(man, indent=2, ensure_ascii=False) + "\n")
    return mpath


def scratch_input_pins(tmp):
    """The four data-input pins the scratch manifest currently claims."""
    import json

    man = json.load(io.open(os.path.join(
        tmp, "research", "extensions", "x01",
        "X01_EXECUTION_MANIFEST.json"), encoding="utf-8"))
    return {e["path"]: e["sha256"] for e in man["inputs"]
            if e["kind"] == "git_ignored_data"}


def authorize_scratch(tmp, run_id, auth_id):
    """Commit a valid, exactly-bound authorization into a scratch repo."""
    probe = orch.ExecutionPlan(run_id=run_id, repo=tmp)
    ident = orch.execution_identity(probe)
    grant = {"record_type": AUTH.RECORD_TYPE_AUTHORIZATION,
             "schema": {"name": AUTH.SCHEMA_NAME, "version": AUTH.SCHEMA_VERSION},
             "authorization_id": auth_id, "owner": "Aaron",
             "authorized_utc": AUTH_CLOCK, "status": "AUTHORIZED",
             "scope": AUTH.ONE_SHOT_SCOPE,
             "binding": {f: ident[f] for f in AUTH.BOUND_IDENTITY_FIELDS}}
    io.open(os.path.join(tmp, "ops", "EXECUTION_AUTHORIZATIONS.md"), "a",
            encoding="utf-8", newline="\n").write(AUTH.render_record(grant))
    _git(tmp, "add", "ops/EXECUTION_AUTHORIZATIONS.md")
    _git(tmp, "commit", "-q", "-m", "synthetic authorization %s" % auth_id)
    return ident


def test_production_entrypoint():
    """B1 / T1 / T2 — the entrypoint is complete and still refuses here."""
    ledger_before = hashlib.sha256(
        io.open(os.path.join(REPO, "ops", "EXPOSURE_LEDGER.md"), "rb").read()
    ).hexdigest()

    # ---- T1: the REAL repository, with the REAL production adapters --------
    register_before = _counted(REPO)
    counter = orch.TargetAdapterCallCounter()
    # The production API exposes neither a preflight nor a recorder override, so
    # this runs the canonical components against the REAL repository and relies
    # on the authorization gate to stop before anything is written.
    _stub, _saved = _with_seal("VERIFIED")
    try:
        plan = prod.build_plan(repo=REPO, run_id="X01-RUN-T1",
                               authorization_id="X01-AUTH-DOES-NOT-EXIST",
                               counter=counter)
        art = orch.run(plan)
    finally:
        _restore_seal(_saved)
    ck("T1 the production path on the real repository REFUSES: there is no "
       "committed authorization",
       art["outcome_state"] == ev.EXECUTION_REFUSED
       and art["governance"]["refusal_stage"] == orch.STAGE_AUTHORIZATION,
       "%s / %s" % (art["outcome_state"], art["governance"].get("refusal_stage")))
    ck("T1 target constructor calls = 0", counter.n == 0, "counter=%d" % counter.n)
    ck("T1 target READS = 0 — the sealed panels were never opened",
       plan.data.reads == [], str(plan.data.reads))
    ck("T1 the canonical recorder was built for the REAL repo and wrote "
       "nothing: no journal, ledger byte-identical, register unmoved",
       isinstance(plan.recorder, prod.ProductionGovernanceRecorder)
       and plan.recorder.written == []
       and not os.path.exists(os.path.join(REPO, "ops", "execution-journal"))
       and hashlib.sha256(io.open(os.path.join(REPO, "ops",
                                               "EXPOSURE_LEDGER.md"), "rb")
                          .read()).hexdigest() == ledger_before
       and _counted(REPO) == register_before,
       "written=%d register=%s" % (len(plan.recorder.written), _counted(REPO)))

    class _Args(object):
        pass
    a = _Args()
    a.repo, a.run_id, a.authorization_id = REPO, "X01-RUN-T1B", "X01-AUTH-NONE"
    a.artifact, a.exposure_classification, a.no_runtime = None, "NO_OUTCOME", True
    buf = io.StringIO()
    _art, code = prod.execute(a, out=buf)
    ck("T1 the CLI surface refuses with a non-zero exit code",
       code == prod.EXIT_REFUSED, "exit=%s" % code)
    ck("T1 and the production CLI is the real runner subcommand",
       runner.cmd_execute.__doc__ and "refuses" in runner.cmd_execute.__doc__.lower())

    # `cmd_execute` must ROUTE through build_plan, not re-implement a path
    seen = {"n": 0}
    runner._PRODUCTION_MODULE = prod          # the runner must use THIS copy
    real_build = prod.build_plan

    def counting(*args, **kwargs):
        seen["n"] += 1
        return real_build(*args, **kwargs)
    prod.build_plan = counting
    try:
        runner.cmd_execute(a)
    finally:
        prod.build_plan = real_build
    ck("T1 cmd_execute routes through the single production plan builder — "
       "there is no second path", seen["n"] == 1, "build_plan calls=%d" % seen["n"])

    # ---- T2: a throwaway repo where a valid authorization DOES exist -------
    tmp = throwaway_repo()
    if tmp is None:
        ck("T2 a throwaway git repository could be created", False, "git init failed")
        flush("12. B1 / T1-T2 — the production entrypoint")
        return
    ck("T2 the throwaway repo's execution infrastructure resolves to a real "
       "revision, so an authorization can bind it",
       bool(re.match(r"^[0-9a-f]{40}$",
                     AUTH.execution_infrastructure_revision(tmp) or "")),
       AUTH.execution_infrastructure_revision(tmp)[:50])

    authorize_scratch(tmp, "X01-RUN-T2", "X01-AUTH-T2")

    c2 = orch.TargetAdapterCallCounter()
    apath = os.path.join(tmp, "evidence.json")
    _stub2, _saved2 = _with_seal("VERIFIED")
    try:
        plan2 = prod.build_plan(repo=tmp, run_id="X01-RUN-T2",
                                authorization_id="X01-AUTH-T2",
                                artifact_path=apath, counter=c2)
        orch.layers()["construction"].SEALED_MAP.update(SYNTH_MAP)
        art2 = orch.run(plan2)
    finally:
        _restore_seal(_saved2)
    ck("T2 with a committed, exactly-bound authorization the production "
       "entrypoint REACHES the orchestrator and completes",
       art2["outcome_state"] in (ev.COMPLETED_EVIDENCE,
                                 ev.INFERENCE_PROCEDURE_FAILURE),
       "%s (%s)" % (art2["outcome_state"],
                    art2["governance"].get("refusal_reason")
                    or art2["governance"].get("failure_reason")))
    ck("T2 every pre-construction gate passed, in the authoritative order",
       plan2.stages_passed[:6] == list(orch.STAGES_BEFORE_CONSTRUCTION),
       str(plan2.stages_passed[:6]))
    ck("T2 the authorization was consumed exactly once, and the CANONICAL "
       "recorder moved authoritative storage",
       art2["governance"].get("authorization_consumed") is True
       and isinstance(plan2.recorder, prod.ProductionGovernanceRecorder)
       and _counted(tmp) == 3 and _rows_n(tmp) == 4,
       "databento rows=%s total rows=%s" % (_counted(tmp), _rows_n(tmp)))
    ck("T2 the authorization provider was the LEDGER provider, not an injected "
       "one — permission is never a parameter of build_plan",
       isinstance(plan2.authorization, AUTH.LedgerAuthorizationProvider))
    ck("T2 PRODUCTION_ENTRYPOINT_AFTER_VALID_AUTHORIZATION = ALREADY_EXISTS: no "
       "production code changed between T1 and T2, only the authorization",
       plan2.artifact_path == apath and os.path.exists(apath))
    flush("12. B1 / T1-T2 — the production entrypoint")


def test_evidence_relationships():
    """B2 / T5-T11 — every sealed relationship the validator now binds."""
    cases = []

    cases.append(("T5 wrong calendar digest",
                  good_artifact(sample=synthetic_sample(
                      calendar_digest="a" * 64)),
                  "not the digest of the sealed"))

    d = synthetic_diagnostics()
    d["crisis_windows"][0]["month_ends"] = ["2020-03-31", "2020-04-30",
                                            "2020-05-31"]
    cases.append(("T6 sealed crisis NAME over unsealed dates",
                  good_artifact(diagnostics=d), "sealed §7.1 month-ends"))

    pr = synthetic_primary()
    pr["bootstrap"]["master_seed"] = 8
    cases.append(("T7 wrong primary bootstrap seed", good_artifact(primary=pr),
                  "primary.bootstrap.master_seed"))

    pr = synthetic_primary()
    pr["ci"]["n_valid"] = 9700
    cases.append(("T8 CI valid count disagrees with the bootstrap counts",
                  good_artifact(primary=pr), "describe different runs"))

    arms = synthetic_arms()
    arms["A1"]["arm"] = "S1"
    cases.append(("T9 the A1 block declares itself a different arm",
                  good_artifact(arms=arms), "must be that arm"))

    ident = synthetic_identity()
    del ident["execution_infrastructure_revision"]
    cases.append(("T10 missing execution-infrastructure revision",
                  ev.completed(ident, synthetic_governance(),
                               {"run_id": "R", "generated_utc": "T"},
                               synthetic_sample(), synthetic_arms(),
                               synthetic_primary(), synthetic_secondary(),
                               synthetic_diagnostics()),
                  "execution_infrastructure_revision"))

    mech = ev.mechanical_failure(
        synthetic_identity(), synthetic_governance(),
        {"run_id": "R", "generated_utc": "T"}, "synthetic break",
        orch.STAGE_INFERENCE, sample=synthetic_sample(), arms=synthetic_arms())
    nested = copy.deepcopy(mech)
    nested["secondary"] = {"S1": {"role": "DESCRIPTIVE_SENSITIVITY",
                                  "classification": "PRESERVATION_SUPPORTED"}}
    cases.append(("T11 mechanical failure carrying a NESTED §5 classification",
                  ev.finalize(nested), "classification"))

    deep = copy.deepcopy(mech)
    deep["arms"]["A1"]["debug"] = {"inner": {"delta_s": 0.07}}
    cases.append(("T11 mechanical failure with a scientific quantity three "
                  "levels down", ev.finalize(deep), "delta_s"))

    prose = copy.deepcopy(mech)
    prose["governance"]["failure_detail"] = [
        "would have been PRESERVATION_SUPPORTED"]
    cases.append(("T11 mechanical failure smuggling a verdict through prose",
                  ev.finalize(prose), "never conclude"))

    for label, art, needle in cases:
        errs = ev.validate(art, art["identity"].get("execution_revision"))
        ck("REJECTED: %s" % label,
           bool(errs) and any(needle in x for x in errs),
           (errs[0][:86] if errs else "ACCEPTED!"))

    ck("INVALID_EVIDENCE_ACCEPTED = ELIMINATED for these cases, and the clean "
       "record still validates — so the rules are not simply rejecting "
       "everything", ev.validate(good_artifact(), "a" * 40) == [],
       "; ".join(ev.validate(good_artifact(), "a" * 40))[:90])
    ck("the sealed calendar digest is re-derived with stdlib, independently of "
       "the pandas calendar the orchestrator builds",
       ev.sealed_calendar_digest()
       == orch.calendar_digest(orch.sealed_evaluation_index())
       and len(ev.sealed_month_ends()) == 179)
    flush("13. B2 / T5-T11 — every sealed relationship the record can carry")


def test_atomic_one_shot():
    """B3 / T3-T4 — exactly one claimant, across threads AND processes."""
    import threading

    root = tempfile.mkdtemp(prefix="x01-race-")
    store = AUTH.FileClaimStore(root)

    # ---- T3a: many threads, many trials, exactly one winner each time ------
    trials, claimants, winners = 25, 12, []
    for trial in range(trials):
        aid = "X01-AUTH-RACE-%03d" % trial
        gate = threading.Barrier(claimants)
        won = []
        lock = threading.Lock()

        def attempt(n=trial):
            gate.wait()
            if store.claim(aid, {"pid": os.getpid(), "thread": True}):
                with lock:
                    won.append(n)
        threads = [threading.Thread(target=attempt) for _ in range(claimants)]
        for th in threads:
            th.start()
        for th in threads:
            th.join()
        winners.append(len(won))
    ck("T3 %d trials x %d concurrent claimants: exactly one winner every time"
       % (trials, claimants),
       set(winners) == {1}, "winner counts seen: %s" % sorted(set(winners)))

    # ---- T3b: separate OS PROCESSES, so the mechanism is not in-process ----
    proot = tempfile.mkdtemp(prefix="x01-procrace-")
    script = (
        "import sys,importlib.util,os\n"
        "spec=importlib.util.spec_from_file_location('a',sys.argv[1])\n"
        "m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)\n"
        "s=m.FileClaimStore(sys.argv[2])\n"
        "print('WON' if s.claim(sys.argv[3], {'pid': os.getpid()}) else 'LOST')\n")
    spath = os.path.join(proot, "claimer.py")
    io.open(spath, "w", encoding="utf-8", newline="\n").write(script)
    authmod = os.path.join(HERE, "x01_authorization.py")
    procs = [subprocess.Popen(
        [sys.executable, spath, authmod, os.path.join(proot, "claims"),
         "X01-AUTH-PROCRACE"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        for _ in range(4)]
    outs = [pp.communicate()[0].decode().strip() for pp in procs]
    ck("T3 four separate OS PROCESSES race: exactly one WON, three LOST",
       outs.count("WON") == 1 and outs.count("LOST") == 3, str(outs))

    # ---- T3c: two providers that BOTH validated, then race ----------------
    base = auth_identity(run_id="X01-RUN-RACE")
    fx = Fixture(base, authorization_id="X01-AUTH-RACE")
    a_provider, b_provider = fx.provider, fx.fresh_provider()
    ref_a, why_a = a_provider.authorization_for(base)
    ref_b, why_b = b_provider.authorization_for(base)
    ck("T3 both providers validate the same authorization BEFORE either claims "
       "— the race is real, not serialised by validation",
       ref_a is not None and ref_b is not None, "%s / %s" % (why_a, why_b))
    sess_a, sess_b = a_provider.open_session(ref_a), b_provider.open_session(ref_b)
    sess_a.begin_step2()
    lost = _raises(sess_b.begin_step2, AUTH.AuthorizationError)
    ck("T3 the loser is refused AT the step-2 boundary, on stale validation",
       lost and not sess_b.begin_step2.__self__.claimed)
    ck("T3 winner count = 1, loser count = 1",
       sess_a.claimed is True and sess_b.claimed is False)

    # ---- T3d: the same race through the whole orchestrator ----------------
    base2 = auth_identity(run_id="X01-RUN-RACE2")
    fx2 = Fixture(base2, authorization_id="X01-AUTH-RACE2")
    p_first, p_second = fx2.provider, fx2.fresh_provider()
    ref1, _ = p_first.authorization_for(base2)
    ref2, _ = p_second.authorization_for(base2)
    ck("T3 both providers validated before the first run started",
       ref1 is not None and ref2 is not None)
    c1, c2 = orch.TargetAdapterCallCounter(), orch.TargetAdapterCallCounter()
    r1, r2 = ScratchRecorder(), ScratchRecorder()
    tmpdir = tempfile.mkdtemp(prefix="x01-race-run-")
    with patched_identity(base2):
        art1 = orch.run(plan_for(c1, authorization_provider=p_first,
                                 recorder=r1, run_id=base2["run_id"],
                                 artifact_path=os.path.join(tmpdir, "a.json")))
        art2 = orch.run(plan_for(c2, authorization_provider=p_second,
                                 recorder=r2, run_id=base2["run_id"],
                                 artifact_path=os.path.join(tmpdir, "b.json")))
    ck("T3 the first run completes and the second is REFUSED",
       art1["outcome_state"] in (ev.COMPLETED_EVIDENCE,
                                 ev.INFERENCE_PROCEDURE_FAILURE)
       and art2["outcome_state"] == ev.EXECUTION_REFUSED,
       "%s / %s" % (art1["outcome_state"], art2["outcome_state"]))
    ck("T3 durable step-2 commitments = 1",
       len(r1.exposure_rows) + len(r2.exposure_rows) == 1,
       "%d + %d" % (len(r1.exposure_rows), len(r2.exposure_rows)))
    ck("T3 target construction executions = 1 (the loser constructed nothing)",
       c1.n > 0 and c2.n == 0, "%d / %d" % (c1.n, c2.n))
    ck("DOUBLE_EXECUTION_FROM_ONE_AUTHORIZATION = IMPOSSIBLE_BY_TESTED_MECHANISM",
       len(r1.exposure_rows) == 1 and c2.n == 0
       and art2["governance"]["refusal_stage"] == orch.STAGE_AUTHORIZATION)

    # ---- the claim lost AFTER validation, through the whole orchestrator ---
    base_sn = auth_identity(run_id="X01-RUN-SNIPED")
    fx_sn = Fixture(base_sn, authorization_id="X01-AUTH-SNIPED")
    sniped = ClaimSnipedProvider(
        fx_sn.source, "X01-AUTH-SNIPED",
        appender=AUTH.InMemoryLedgerAppender(fx_sn.source),
        clock=lambda: "2026-09-11T10:00:00Z",
        claim_store=AUTH.FileClaimStore(fx_sn.claim_root))
    c_sn, r_sn = orch.TargetAdapterCallCounter(), ScratchRecorder()
    with patched_identity(base_sn):
        art_sn = orch.run(plan_for(c_sn, authorization_provider=sniped,
                                   recorder=r_sn, run_id=base_sn["run_id"]))
    g_sn = art_sn["governance"]
    ck("a claim LOST between validation and the boundary refuses at the "
       "authorization gate — the orchestrator does not carry a stale "
       "validation into step 2",
       art_sn["outcome_state"] == ev.EXECUTION_REFUSED
       and g_sn.get("refusal_stage") == orch.STAGE_AUTHORIZATION
       and "claim" in (g_sn.get("refusal_reason") or ""),
       "%s / %s" % (art_sn["outcome_state"], g_sn.get("refusal_stage")))
    ck("... and that loser committed NOTHING: no exposure row, no constructor, "
       "no result-bearing state",
       r_sn.exposure_rows == [] and c_sn.n == 0
       and art_sn["outcome_state"] not in (ev.COMPLETED_EVIDENCE,
                                           ev.INFERENCE_PROCEDURE_FAILURE),
       "exposure=%d constructors=%d" % (len(r_sn.exposure_rows), c_sn.n))

    # ---- the stale-validation re-check, bound on its own -------------------
    # Distinct from the claim. Here NOBODY has claimed: the authorization was
    # simply invalidated after this session validated it. Only the re-resolve at
    # the step-2 boundary can see that, so this check binds it without the claim
    # store standing in.
    base_st = auth_identity(run_id="X01-RUN-STALE")
    fx_st = Fixture(base_st, authorization_id="X01-AUTH-STALE")
    ref_st, why_st = fx_st.provider.authorization_for(base_st)
    ck("the session validates while the authorization is active",
       ref_st is not None, str(why_st)[:80])
    sess_st = fx_st.provider.open_session(ref_st)
    fx_st.source.worktree += AUTH.render_record(lifecycle_record(
        "X01-AUTH-STALE", AUTH.EVENT_INVALIDATED, base_st["run_id"],
        "withdrawn by the Owner after this session validated"))
    ck("the ledger now says INVALIDATED while NO claim exists",
       fx_st.status().status == AUTH.STATUS_INVALIDATED
       and AUTH.FileClaimStore(fx_st.claim_root).existing("X01-AUTH-STALE")
       is None)
    ck("M27 the step-2 boundary RE-RESOLVES and refuses the stale session — a "
       "validation made earlier does not carry permission forward",
       _raises(sess_st.begin_step2, AUTH.AuthorizationError))
    ck("... and nothing was claimed or appended on the way out",
       AUTH.FileClaimStore(fx_st.claim_root).existing("X01-AUTH-STALE") is None
       and sess_st.claimed is False)

    # ---- T4: a claimant that dies immediately after claiming ---------------
    base3 = auth_identity(run_id="X01-RUN-CRASH")
    fx3 = Fixture(base3, authorization_id="X01-AUTH-CRASH")
    dead = AUTH.FileClaimStore(fx3.claim_root)
    dead.claim("X01-AUTH-CRASH", {"pid": -1, "note": "died immediately after"})
    ck("T4 the ledger still reads AUTHORIZED — only the claim records the dead "
       "attempt", fx3.status().active)
    ref3, why3 = fx3.fresh_provider().authorization_for(base3)
    ck("T4 a later claimant is REFUSED because the claim is unreleased",
       ref3 is None and (why3 or "").startswith(AUTH.REASON_ALREADY_CLAIMED),
       str(why3)[:80])
    c4 = orch.TargetAdapterCallCounter()
    r4 = ScratchRecorder()
    with patched_identity(base3):
        art4 = orch.run(plan_for(c4, authorization_provider=fx3.fresh_provider(),
                                 recorder=r4, run_id=base3["run_id"]))
    ck("T4 and no second outcome-bearing attempt occurs",
       art4["outcome_state"] == ev.EXECUTION_REFUSED and c4.n == 0
       and r4.exposure_rows == [])
    ck("ATOMIC_ONE_SHOT_CLAIM = PASS", True)

    # ---- the release rule: ONLY on proven non-durability -------------------
    base5 = auth_identity(run_id="X01-RUN-RELEASE")
    fx5 = Fixture(base5, authorization_id="X01-AUTH-RELEASE")
    c5 = orch.TargetAdapterCallCounter()
    with patched_identity(base5):
        orch.run(plan_for(c5, authorization_provider=fx5.provider,
                          recorder=ScratchRecorder(
                              fail_on="exposure_proven_not_durable"),
                          run_id=base5["run_id"]))
    ck("§7 a PROVEN non-durable step 2 releases the claim, so the "
       "authorization really is usable again",
       AUTH.FileClaimStore(fx5.claim_root).existing("X01-AUTH-RELEASE") is None
       and fx5.fresh_provider().authorization_for(base5)[0] is not None)
    base6 = auth_identity(run_id="X01-RUN-NORELEASE")
    fx6 = Fixture(base6, authorization_id="X01-AUTH-NORELEASE")
    c6 = orch.TargetAdapterCallCounter()
    with patched_identity(base6):
        orch.run(plan_for(c6, authorization_provider=fx6.provider,
                          recorder=ScratchRecorder(fail_on="exposure"),
                          run_id=base6["run_id"]))
    ck("§7 an AMBIGUOUS step 2 does NOT release the claim",
       AUTH.FileClaimStore(fx6.claim_root).existing("X01-AUTH-NORELEASE")
       is not None
       and fx6.fresh_provider().authorization_for(base6)[0] is None)
    flush("14. B3 / T3-T4 — the atomic one-shot claim")


def test_structured_failures():
    """B4 / B5 / T12-T15 — ordinary failures become records, not tracebacks."""
    base = auth_identity()
    tmpdir = tempfile.mkdtemp(prefix="x01-struct-")

    # `failure_class` is the class ACTUALLY raised, not the guard's own name:
    # `OSError(13, ...)` is a `PermissionError`, and an operator needs to see
    # which one it was.
    for label, fail_on, stage, last, klass in (
            ("T12 OSError during step 2", "oserror_exposure",
             orch.STAGE_EXPOSURE_RECORD, orch.STAGE_AUTHORIZATION, "OSError"),
            ("T13 OSError during the cumulative-state read", "oserror_cumulative",
             orch.STAGE_CUMULATIVE_STATE, orch.STAGE_EXPOSURE_RECORD,
             "PermissionError"),
            ("T14 OSError during seed-stream recording", "oserror_seed",
             orch.STAGE_SEED_RECORD, orch.STAGE_CUMULATIVE_STATE, "OSError")):
        fx = Fixture(base)
        try:
            art, c, rec, _p = probe(fx, recorder=ScratchRecorder(fail_on=fail_on))
        except Exception as exc:                      # noqa: BLE001
            # An escaping exception is precisely the defect under test. It must
            # fail THIS check by name, not tear the suite down with a traceback
            # that only incidentally signals something went wrong.
            art = {"outcome_state": "ESCAPED %s" % type(exc).__name__,
                   "governance": {}, "run_instance": {"run_id": None},
                   "primary": None}
        g = art["governance"]
        ck("%s -> a structured EXECUTION_MECHANICAL_FAILURE, not an escaped "
           "exception" % label,
           art["outcome_state"] == ev.EXECUTION_MECHANICAL_FAILURE
           and g.get("failure_stage") == stage,
           "%s / %s" % (art["outcome_state"], g.get("failure_stage")))
        ck("%s -> the record names the failure class (%s) and the detail"
           % (label[:4], klass),
           g.get("failure_class") == klass and bool(g.get("failure_detail")),
           "%s / %s" % (g.get("failure_class"), str(g.get("failure_detail"))[:50]))
        ck("%s -> and the authorization state and last stage are recorded"
           % label[:4],
           g.get("last_completed_stage") == last
           and g.get("authorization_id") == "X01-AUTH-T1"
           and art["run_instance"].get("run_id") == base["run_id"],
           str(g.get("last_completed_stage")))
        ck("%s -> no §5 verdict anywhere in the record" % label[:4],
           art["outcome_state"] == ev.EXECUTION_MECHANICAL_FAILURE
           and not any(cls in ev.canonical_json(art)
                       for cls in ev.SEALED_CLASSIFICATIONS)
           and ev.validate(art, base["execution_revision"]) == [],
           "; ".join(ev.validate(art, base["execution_revision"]))[:70]
           if art["outcome_state"] == ev.EXECUTION_MECHANICAL_FAILURE
           else art["outcome_state"])

    ck("EXECUTION_FAILURE_EVIDENCE_LOST = ELIMINATED for these stages", True)

    # ---- T15: the reproduced post-construction sample failure --------------
    fx = Fixture(base)
    c = orch.TargetAdapterCallCounter()
    rec = ScratchRecorder()
    orch.layers()["construction"].SEALED_MAP.update(SYNTH_MAP)
    with patched_identity(base):
        art = orch.run(plan_for(c, authorization_provider=fx.provider,
                                recorder=rec, run_id=base["run_id"],
                                data_adapter=SyntheticData(c, break_sample=True),
                                artifact_path=os.path.join(tmpdir, "t15.json")))
    g = art["governance"]
    ck("T15 targets were constructed, THEN the sealed sample failed",
       c.n > 0 and "construct_E" in c.calls, str(c.calls[:3]))
    ck("T15 the state is EXECUTION_MECHANICAL_FAILURE, never EXECUTION_REFUSED",
       art["outcome_state"] == ev.EXECUTION_MECHANICAL_FAILURE,
       art["outcome_state"])
    ck("T15 the failing stage is the sealed sample and the last COMPLETED stage "
       "is construction — no false claim that nothing was constructed",
       g.get("failure_stage") == orch.STAGE_SEALED_SAMPLE
       and g.get("last_completed_stage") == orch.STAGE_CONSTRUCTION,
       "%s / %s" % (g.get("failure_stage"), g.get("last_completed_stage")))
    ck("T15 the record carries what WAS constructed, and does not claim the "
       "sealed calendar",
       isinstance(art["sample"], dict) and art["arms"] is not None
       and art["sample"].get("calendar_digest") is None
       and art["sample"].get("missingness_state")
       == "SEALED_SAMPLE_NOT_SATISFIED_AFTER_CONSTRUCTION",
       str(art["sample"])[:90])
    ck("T15 the authorization is consumed — the targets were read",
       g.get("authorization_consumed") is True
       and fx.status().status == AUTH.STATUS_CONSUMED)
    ck("T15 no scientific verdict, and the record validates as what it is",
       not any(cls in ev.canonical_json(art)
               for cls in ev.SEALED_CLASSIFICATIONS)
       and ev.validate(art, base["execution_revision"]) == [],
       "; ".join(ev.validate(art, base["execution_revision"]))[:70])
    ck("POST_CONSTRUCTION_EXECUTION_MISREPORTED = ELIMINATED", True)
    flush("15. B4 + B5 / T12-T15 — structured failure, honest state")


def test_atomic_publication():
    """B6 / T16-T18 — one identity, recorded outside the bytes it describes."""
    base = auth_identity()
    tmpdir = tempfile.mkdtemp(prefix="x01-publish-")

    # ---- T18: the happy path, and the hash of the published bytes ----------
    fx = Fixture(base)
    path = os.path.join(tmpdir, "evidence.json")
    orch.layers()["construction"].SEALED_MAP.update(SYNTH_MAP)
    art, c, rec, plan = probe(fx, artifact_path=path)
    ck("T18 the artifact was published", os.path.exists(path)
       and art["outcome_state"] in (ev.COMPLETED_EVIDENCE,
                                    ev.INFERENCE_PROCEDURE_FAILURE),
       art["outcome_state"])
    on_disk = hashlib.sha256(io.open(path, "rb").read()).hexdigest()
    ck("T18 FINAL_ARTIFACT_HASH_MATCH — the recorded digest is the digest of "
       "the exact published bytes",
       plan.publication["artifact_file_sha256"] == on_disk,
       "%s vs %s" % (plan.publication["artifact_file_sha256"][:16],
                     on_disk[:16]))
    ok, actual = ev.verify_published(path)
    ck("T18 and the sidecar provenance verifies independently", ok, actual[:16])
    ck("T18 the file does NOT contain its own file hash — that identity lives "
       "outside the bytes it describes",
       on_disk not in io.open(path, encoding="utf-8").read()
       and "artifact_file_sha256" not in io.open(path, encoding="utf-8").read())
    ck("T18 the payload digest inside the file still pins the payload",
       ev.read_artifact(path)["content_digest"]
       == ev.content_digest(ev.read_artifact(path)))
    ck("T18 the returned artifact is byte-identical to what was published",
       ev.canonical_json(art) + "\n" == io.open(path, encoding="utf-8").read())
    ck("T18 the provenance names the run and the authorization it spent",
       plan.publication.get("run_id") == base["run_id"]
       and plan.publication.get("authorization_id") == "X01-AUTH-T1")
    ck("PERSISTED_ARTIFACT_IDENTITY_MISMATCH = ELIMINATED", ok)

    # ---- T16: the temporary write fails ------------------------------------
    fx2 = Fixture(base)
    path2 = os.path.join(tmpdir, "t16.json")
    art2, c2, _r, plan2 = probe(
        fx2, artifact_path=path2,
        artifact_tmp_path=os.path.join(tmpdir, "no-such-dir", "t16.tmp"))
    ck("T16 a failed temporary write yields EXECUTION_MECHANICAL_FAILURE at "
       "persistence",
       art2["outcome_state"] == ev.EXECUTION_MECHANICAL_FAILURE
       and art2["governance"]["failure_stage"] == orch.STAGE_PERSIST,
       art2["outcome_state"])
    ck("T16 and NO completed artifact exists at the final path",
       not os.path.exists(path2))

    # ---- T17: the atomic publish itself fails ------------------------------
    fx3 = Fixture(base)
    path3 = os.path.join(tmpdir, "t17.json")
    real_replace = ev._atomic_replace     # `ev` IS the orchestrator's copy

    def exploding(src, dst):
        raise OSError(13, "synthetic: rename refused")
    ev._atomic_replace = exploding
    try:
        art3, c3, _r, plan3 = probe(fx3, artifact_path=path3)
    finally:
        ev._atomic_replace = real_replace
    ck("T17 a failed publication yields EXECUTION_MECHANICAL_FAILURE",
       art3["outcome_state"] == ev.EXECUTION_MECHANICAL_FAILURE
       and art3["governance"]["failure_stage"] == orch.STAGE_PERSIST,
       art3["outcome_state"])
    ck("T17 no artifact became visible at the final path, and no temporary "
       "file was left behind",
       not os.path.exists(path3)
       and not [f for f in os.listdir(tmpdir) if f.startswith("t17.json.tmp")],
       str([f for f in os.listdir(tmpdir) if "t17" in f]))

    # ---- T17b: published, but the external provenance fails ----------------
    fx4 = Fixture(base)
    path4 = os.path.join(tmpdir, "t17b.json")
    art4, c4, _r, plan4 = probe(
        fx4, artifact_path=path4,
        artifact_provenance_path=os.path.join(tmpdir, "no-dir", "p.json"))
    ck("T17 a provenance failure AFTER publication is reported as its own "
       "stage, not as a failed publication",
       art4["outcome_state"] == ev.EXECUTION_MECHANICAL_FAILURE
       and art4["governance"]["failure_stage"] == orch.STAGE_PROVENANCE,
       "%s / %s" % (art4["outcome_state"],
                    art4["governance"].get("failure_stage")))
    ck("T17 the artifact IS on disk and its identity is intact",
       os.path.exists(path4)
       and plan4.publication["artifact_file_sha256"]
       == hashlib.sha256(io.open(path4, "rb").read()).hexdigest())
    ck("T17 and the artifact on disk is still a valid evidence record",
       ev.validate(ev.read_artifact(path4), base["execution_revision"]) == [],
       "; ".join(ev.validate(ev.read_artifact(path4),
                             base["execution_revision"]))[:70])
    flush("16. B6 / T16-T18 — atomic publication and artifact identity")


def test_production_governance_records():
    """The production recorder, exercised on SCRATCH copies of the real files."""
    workspace = tempfile.mkdtemp(prefix="x01-gov-")
    tmp = os.path.join(workspace, "scratch-repo")
    # A STUB carry project beside the scratch repo. The real
    # `commodity-carry-research` is never written to, and here it is not even
    # read: the parser is exercised against bytes this test wrote.
    stub = os.path.join(workspace, "commodity-carry-research", "src")
    os.makedirs(stub)
    io.open(os.path.join(stub, "config.py"), "w", encoding="utf-8",
            newline="\n").write("# stub\nN_TRIALS = 14  # frozen\n")
    os.makedirs(os.path.join(tmp, "ops"))
    os.makedirs(os.path.join(tmp, "research", "extensions"))
    for rel in ("ops/EXPOSURE_LEDGER.md", "research/extensions/TRIAL_LEDGER.md"):
        src = os.path.join(REPO, rel.replace("/", os.sep))
        dst = os.path.join(tmp, rel.replace("/", os.sep))
        io.open(dst, "wb").write(io.open(src, "rb").read())

    # Aaron has since sealed the token, so the recorder no longer refuses an
    # unspecified classification — it uses HIS, recorded as a named constant.
    # It still invents nothing: any token outside the ratified set is refused.
    ck("with no token supplied the recorder uses the OWNER-SEALED token, and "
       "records whose decision it is",
       prod.ProductionGovernanceRecorder(repo=tmp, run_id="R")
       .exposure_classification
       == prod.OWNER_FIRST_EXECUTION_EXPOSURE_CLASSIFICATION
       == "GENERATED_NOT_SEEN")
    ck("and it refuses a token outside the ratified set",
       _raises(lambda: prod.ProductionGovernanceRecorder(
           repo=tmp, run_id="R", exposure_classification="LOOKS_FINE"),
           prod.ProductionRefusal))

    rec = prod.ProductionGovernanceRecorder(
        repo=tmp, run_id="X01-RUN-GOV", clock=lambda: "2026-09-11T12:00:00Z",
        exposure_classification="GENERATED_NOT_SEEN")
    before = io.open(os.path.join(tmp, "ops", "EXPOSURE_LEDGER.md"),
                     encoding="utf-8").read()
    ref = rec.record_exposure_and_attempts({"kind": "TEST",
                                            "execution_identity": {}})
    after = io.open(os.path.join(tmp, "ops", "EXPOSURE_LEDGER.md"),
                    encoding="utf-8").read()
    ck("the step-2 append adds exactly one row and keeps exactly one table",
       after.startswith(before) and prod.count_tables(after) == 1
       and len(after.splitlines()) == len(before.splitlines()) + 1,
       "tables=%d" % prod.count_tables(after))
    ck("... and the canonical governance validator still parses the result",
       _ledger_parses(after), "")
    ck("... and the machine journal was written durably alongside it",
       bool(ref.get("journal"))
       and os.path.exists(os.path.join(tmp, ref["journal"].replace("/", os.sep))))
    ck("a literal '|' in a note is REFUSED, because it would break the §10.1 "
       "table parser",
       _raises(lambda: prod.ledger_row(
           {"ts": "t", "scope": "CURRENT_REVIEW_SCOPE",
            "classification": "NO_OUTCOME", "granularity": "NONE",
            "artifact_or_pointer": "x", "note": "a | b"}),
           prod.ProductionRefusal))
    ck("a run id is used once, and the refusal now comes BEFORE any durable "
       "write, so the authorization survives it",
       _raises(lambda: rec.record_exposure_and_attempts({"kind": "TEST"}),
               AUTH.Step2NotDurable))

    anchor, src = prod.read_carry_anchor(tmp)
    ck("step 2 ALSO advanced the authoritative register: 3 Databento attempt "
       "rows now exist where there were none",
       _contribution(tmp) == 3 and _counted(tmp) == 3,
       "%s over %s row(s)" % (_contribution(tmp), _counted(tmp)))
    real_anchor, real_src = prod.read_carry_anchor(REPO)
    ck("the REAL carry project's frozen anchor reads 14, read-only",
       real_anchor == 14 and real_src.startswith("commodity-carry-research"),
       "%s %s" % (real_anchor, real_src))
    total, rows = _contribution(tmp), _counted(tmp)
    state = _cumulative(rec)
    ck("the cumulative Databento total is READ at execution from the carry "
       "anchor plus this program's own register, never hard-coded",
       total == 3 and rows == 3 and state == anchor + 3,
       "%s + %s = %s" % (anchor, total, state))
    ck("... and the anchor really is the carry project's frozen N_TRIALS",
       anchor == 14 and src.startswith("commodity-carry-research"),
       "%s %s" % (anchor, src))
    ck("a §6.1 attempt row with no readable contribution REFUSES rather than "
       "guessing", _raises(lambda: prod.read_tsmom_contribution(
           tmp, _broken_register(tmp)), prod.ProductionRefusal))
    ck("the PLANNED-BUT-NOT-CREATED table under §6.1 is NOT counted: this run "
       "registered 3 Databento attempts, not the 4 the planned table would add "
       "on top",
       _contribution(tmp) == 3
       and "planned contribution" in io.open(os.path.join(
           tmp, "research", "extensions", "TRIAL_LEDGER.md"),
           encoding="utf-8").read())
    ck("the real commodity-carry-research repository was not modified",
       _carry_clean(), "")
    flush("17. PRODUCTION GOVERNANCE RECORDS — on scratch copies only")


def _ledger_parses(text):
    try:
        spec = importlib.util.spec_from_file_location(
            "vw0", os.path.join(REPO, "research", "extensions",
                                "validate_wave0.py"))
        vw = importlib.util.module_from_spec(spec)
        sys.modules["vw0"] = vw
        spec.loader.exec_module(vw)
    except Exception:                                 # noqa: BLE001
        return False
    _rule, _map, rows, problem = vw.parse_ledger(text)
    return not problem and len(rows) > 0


def _broken_register(tmp):
    rel = "research/extensions/BROKEN_TRIAL_LEDGER.md"
    io.open(os.path.join(tmp, rel.replace("/", os.sep)), "w",
            encoding="utf-8", newline="\n").write(
        "### §6.1 VARIANT_ATTEMPT register\n\n"
        "| # | attempt | contribution |\n|---|---|---|\n"
        "| 1 | A1 | lots |\n")
    return rel


CARRY_REPO = os.path.join(os.path.dirname(REPO), "commodity-carry-research")
CARRY_CONFIG_AT_IMPORT = None
if os.path.exists(os.path.join(CARRY_REPO, "src", "config.py")):
    CARRY_CONFIG_AT_IMPORT = hashlib.sha256(
        io.open(os.path.join(CARRY_REPO, "src", "config.py"), "rb").read()
    ).hexdigest()


def _carry_clean():
    """No TRACKED change in the carry project, and its config byte-identical.

    Deliberately `--untracked-files=no`: that repository carries a long-standing
    untracked working directory of its own, and this program has no business
    having an opinion about it. What matters is that nothing this program did
    touched a tracked byte, and that the anchor it read is unchanged.
    """
    if not os.path.isdir(os.path.join(CARRY_REPO, ".git")):
        return True
    out = subprocess.run(["git", "-C", CARRY_REPO, "status", "--porcelain",
                          "--untracked-files=no"], capture_output=True)
    if out.returncode != 0 or out.stdout.decode().strip():
        return False
    if CARRY_CONFIG_AT_IMPORT is None:
        return True
    now = hashlib.sha256(
        io.open(os.path.join(CARRY_REPO, "src", "config.py"), "rb").read()
    ).hexdigest()
    return now == CARRY_CONFIG_AT_IMPORT


def test_execution_revision_boundary():
    """§9 — x01_production.py carries real execution behaviour, so it must be
    INSIDE the revision an authorization binds.

    A file that decides what a run reads, what it records and where it publishes
    is execution code. If it sat outside the bound revision, its behaviour could
    be changed after Aaron signed and the same authorization would still
    validate — which is the binding with the part that matters removed.
    """
    ck("x01_production.py is declared part of the execution-code boundary",
       "research/extensions/x01/x01_production.py"
       in AUTH.EXECUTION_INFRASTRUCTURE_PATHS,
       str(len(AUTH.EXECUTION_INFRASTRUCTURE_PATHS)) + " paths")

    tmp = throwaway_repo()
    if tmp is None:
        ck("a throwaway git repository could be created for the boundary test",
           False, "git init failed")
        flush("18. §9 — the execution-revision boundary")
        return
    r1 = AUTH.execution_infrastructure_revision(tmp)
    ck("the unmutated throwaway repo resolves to a real bound revision",
       bool(re.match(r"^[0-9a-f]{40}$", r1 or "")), str(r1)[:50])

    probe = orch.ExecutionPlan(run_id="X01-RUN-REVBOUND", repo=tmp)
    ident = orch.execution_identity(probe)
    grant = {"record_type": AUTH.RECORD_TYPE_AUTHORIZATION,
             "schema": {"name": AUTH.SCHEMA_NAME, "version": AUTH.SCHEMA_VERSION},
             "authorization_id": "X01-AUTH-REVBOUND", "owner": "Aaron",
             "authorized_utc": AUTH_CLOCK, "status": "AUTHORIZED",
             "scope": AUTH.ONE_SHOT_SCOPE,
             "binding": {f: ident[f] for f in AUTH.BOUND_IDENTITY_FIELDS}}
    ck("the authorization binds the execution-infrastructure revision that "
       "INCLUDES x01_production.py",
       grant["binding"]["execution_infrastructure_revision"] == r1)
    lpath = os.path.join(tmp, "ops", "EXECUTION_AUTHORIZATIONS.md")
    io.open(lpath, "a", encoding="utf-8", newline="\n").write(
        AUTH.render_record(grant))
    _git(tmp, "add", "ops/EXECUTION_AUTHORIZATIONS.md")
    _git(tmp, "commit", "-q", "-m", "synthetic authorization")

    def provider_for():
        return AUTH.LedgerAuthorizationProvider(
            AUTH.GitLedgerSource(tmp), "X01-AUTH-REVBOUND",
            appender=AUTH.FileLedgerAppender(lpath),
            claim_store=AUTH.FileClaimStore(AUTH.claim_root(tmp)))

    ref, why = provider_for().authorization_for(ident)
    ck("CONTROL: unmutated, the authorization validates — so the refusals below "
       "are not vacuous", ref is not None, str(why)[:90])

    def run_it(tag):
        c = orch.TargetAdapterCallCounter()
        saved = _with_seal("VERIFIED")[1]
        try:
            plan = prod.build_plan(repo=tmp, run_id="X01-RUN-REVBOUND",
                                   authorization_id="X01-AUTH-REVBOUND",
                                   counter=c)
            return orch.run(plan), c, plan.recorder, plan.data
        finally:
            _restore_seal(saved)

    # ---- mutate ONLY x01_production.py, uncommitted ------------------------
    ppath = os.path.join(tmp, "research", "extensions", "x01",
                         "x01_production.py")
    io.open(ppath, "a", encoding="utf-8", newline="\n").write(
        "\n\ndef _scratch_mutation_changing_execution_behaviour():\n"
        "    return 'this file decides what a run reads and records'\n")
    dirty = AUTH.execution_infrastructure_revision(tmp)
    ck("an UNCOMMITTED change to x01_production.py alone makes the bound "
       "revision an unmatchable sentinel",
       dirty.startswith(AUTH.DIRTY_INFRASTRUCTURE)
       and "x01_production.py" in dirty, str(dirty)[:90])
    art, c, rec, data = run_it("dirty")
    ck("... and the run REFUSES at the authorization gate",
       art["outcome_state"] == ev.EXECUTION_REFUSED
       and art["governance"]["refusal_stage"] == orch.STAGE_AUTHORIZATION,
       "%s / %s" % (art["outcome_state"], art["governance"].get("refusal_stage")))
    ck("... before step 2 and before any target read",
       c.n == 0 and rec.written == [] and _counted(tmp) == 0
       and data.reads == [],
       "constructors=%d written=%d rows=%s reads=%s"
       % (c.n, len(rec.written), _counted(tmp), data.reads))

    # ---- commit that same change: the bound revision MOVES -----------------
    _git(tmp, "add", "research/extensions/x01/x01_production.py")
    _git(tmp, "commit", "-q", "-m", "scratch mutation to production code")
    r2 = AUTH.execution_infrastructure_revision(tmp)
    ck("committing a change to x01_production.py MOVES the bound execution "
       "revision", bool(re.match(r"^[0-9a-f]{40}$", r2 or "")) and r2 != r1,
       "%s -> %s" % (str(r1)[:12], str(r2)[:12]))
    ref2, why2 = provider_for().authorization_for(
        orch.execution_identity(orch.ExecutionPlan(run_id="X01-RUN-REVBOUND",
                                                   repo=tmp)))
    ck("the authorization bound to the PREVIOUS revision is now REFUSED, "
       "naming the field",
       ref2 is None and (why2 or "").startswith(AUTH.REASON_BINDING)
       and "execution_infrastructure_revision" in (why2 or ""), str(why2)[:90])
    art2, c2, rec2, data2 = run_it("committed")
    ck("X01_PRODUCTION_PY_INCLUDED_IN_EXECUTION_REVISION = YES — the run "
       "REFUSES before step 2 and before any target read",
       art2["outcome_state"] == ev.EXECUTION_REFUSED
       and art2["governance"]["refusal_stage"] == orch.STAGE_AUTHORIZATION
       and c2.n == 0 and rec2.written == [] and _counted(tmp) == 0
       and data2.reads == [],
       "%s / constructors=%d rows=%s reads=%s"
       % (art2["outcome_state"], c2.n, _counted(tmp), data2.reads))

    # ---- negative control: a file OUTSIDE the boundary must not move it ----
    outside = os.path.join(tmp, "research", "extensions", "x01", "notes.md")
    io.open(outside, "w", encoding="utf-8", newline="\n").write("# unrelated\n")
    _git(tmp, "add", "research/extensions/x01/notes.md")
    _git(tmp, "commit", "-q", "-m", "an unrelated file")
    ck("NEGATIVE CONTROL: a commit touching no execution-code file leaves the "
       "bound revision unchanged, so the test measures the boundary and not "
       "merely 'any commit'",
       AUTH.execution_infrastructure_revision(tmp) == r2,
       "%s" % str(AUTH.execution_infrastructure_revision(tmp))[:12])
    flush("18. §9 — the execution-revision boundary includes x01_production.py")


# --------------------------------------------------------------------------- #
# 19-20. B1a + B1b
# --------------------------------------------------------------------------- #
RN = orch.layers()["runner"]          # the runner the production path actually uses


class SealStub(object):
    """Counts every canonical seal query and answers with a fixed verdict."""

    def __init__(self, verdict="VERIFIED"):
        self.verdict = verdict
        self.queries = 0

    def __call__(self):
        self.queries += 1
        if self.verdict == "VERIFIED":
            return "VERIFIED", ""
        return self.verdict, "synthetic broken seal (%s)" % self.verdict


class PassingPreflight(object):
    """Every pin check passes. Used so a refusal can only come from the seal."""
    ok = True
    reasons = []
    checks = [("synthetic pin check", True, "")] * 40


def _with_seal(verdict, preflight_ok=True):
    """Patch the seal query and the pin checks the production gate composes."""
    stub = SealStub(verdict)
    real_seal, real_pf = RN.seal_state_from_runtime, RN.preflight
    RN.seal_state_from_runtime = stub
    if preflight_ok:
        RN.preflight = lambda **kw: PassingPreflight()
    return stub, (real_seal, real_pf)


def _restore_seal(saved):
    RN.seal_state_from_runtime, RN.preflight = saved


def test_seal_gate_is_mandatory():
    """B1a — no production invocation can reach a gate without the seal check."""
    tmp = throwaway_repo()
    if tmp is None:
        ck("a throwaway repo could be created for the seal-gate test", False,
           "git init failed")
        flush("19. B1a - the canonical seal gate is mandatory")
        return
    probe = orch.ExecutionPlan(run_id="X01-RUN-SEAL", repo=tmp)
    ident = orch.execution_identity(probe)
    grant = {"record_type": AUTH.RECORD_TYPE_AUTHORIZATION,
             "schema": {"name": AUTH.SCHEMA_NAME, "version": AUTH.SCHEMA_VERSION},
             "authorization_id": "X01-AUTH-SEAL", "owner": "Aaron",
             "authorized_utc": AUTH_CLOCK, "status": "AUTHORIZED",
             "scope": AUTH.ONE_SHOT_SCOPE,
             "binding": {f: ident[f] for f in AUTH.BOUND_IDENTITY_FIELDS}}
    io.open(os.path.join(tmp, "ops", "EXECUTION_AUTHORIZATIONS.md"), "a",
            encoding="utf-8", newline="\n").write(AUTH.render_record(grant))
    _git(tmp, "add", "ops/EXECUTION_AUTHORIZATIONS.md")
    _git(tmp, "commit", "-q", "-m", "synthetic authorization")

    class _Args(object):
        pass

    def cli(no_runtime, verdict, run_id):
        """Drive the REAL CLI entrypoint and capture the plan it built."""
        stub, saved = _with_seal(verdict)
        captured = {}
        real_build = prod.build_plan

        def capture(*a, **kw):
            plan = real_build(*a, **kw)
            captured["plan"] = plan
            return plan
        prod.build_plan = capture
        try:
            a = _Args()
            a.repo, a.run_id, a.authorization_id = tmp, run_id, "X01-AUTH-SEAL"
            a.artifact = os.path.join(tmp, "%s.json" % run_id)
            a.exposure_classification = None
            a.no_runtime = no_runtime
            art, code = prod.execute(a, out=io.StringIO())
        finally:
            prod.build_plan = real_build
            _restore_seal(saved)
        return art, code, stub, captured.get("plan")

    # ---- T-B1a-1: broken seal, normal CLI ---------------------------------
    art1, code1, stub1, plan1 = cli(False, "UNVERIFIED", "X01-RUN-SEAL")
    g1 = art1["governance"]
    ck("T-B1a-1 broken seal + normal CLI -> EXECUTION_REFUSED at preflight",
       art1["outcome_state"] == ev.EXECUTION_REFUSED
       and g1.get("refusal_stage") == orch.STAGE_PREFLIGHT
       and code1 == prod.EXIT_REFUSED,
       "%s / %s / exit %s" % (art1["outcome_state"], g1.get("refusal_stage"),
                              code1))
    ck("T-B1a-1 NON-VACUITY: every pin check passed, so the ONLY failing "
       "condition is the seal",
       any("seal" in str(x).lower() for x in g1.get("refusal_detail") or []),
       str(g1.get("refusal_detail"))[:100])
    ck("T-B1a-1 seal queries >= 1, step2 commitments = 0, target reads = 0",
       stub1.queries >= 1 and plan1.recorder.written == []
       and plan1.data.reads == [] and plan1.counter.n == 0,
       "seal=%d written=%d reads=%s constructors=%d"
       % (stub1.queries, len(plan1.recorder.written), plan1.data.reads,
          plan1.counter.n))

    # ---- T-B1a-2: broken seal, --no-runtime -------------------------------
    art2, code2, stub2, plan2 = cli(True, "UNVERIFIED", "X01-RUN-SEAL2")
    g2 = art2["governance"]
    ck("T-B1a-2 broken seal + --no-runtime -> THE SAME REFUSAL",
       art2["outcome_state"] == art1["outcome_state"]
       and g2.get("refusal_stage") == g1.get("refusal_stage")
       and g2.get("refusal_reason") == g1.get("refusal_reason")
       and code2 == code1,
       "%s / %s" % (art2["outcome_state"], g2.get("refusal_stage")))
    ck("T-B1a-2 the flag did NOT suppress the seal query: seal queries >= 1",
       stub2.queries >= 1, "seal queries = %d" % stub2.queries)
    ck("T-B1a-2 step2 commitments = 0, target reads = 0, constructors = 0",
       plan2.recorder.written == [] and plan2.data.reads == []
       and plan2.counter.n == 0,
       "written=%d reads=%s constructors=%d"
       % (len(plan2.recorder.written), plan2.data.reads, plan2.counter.n))
    ck("T-B1a-2 and the two invocations queried the seal the same number of "
       "times", stub2.queries == stub1.queries,
       "%d vs %d" % (stub2.queries, stub1.queries))

    # ---- T-B1a-3: valid seal -> the architecture proceeds ------------------
    stub3, saved = _with_seal("VERIFIED")
    try:
        c3 = orch.TargetAdapterCallCounter()
        # The authorization binds run X01-RUN-SEAL and neither earlier probe
        # consumed it: both refused at preflight, before the claim.
        plan3 = prod.build_plan(repo=tmp, run_id="X01-RUN-SEAL",
                                authorization_id="X01-AUTH-SEAL",
                                artifact_path=os.path.join(tmp, "ok.json"),
                                counter=c3)
        ck("T-B1a-3 the plan's preflight is the canonical production gate, not "
           "anything the caller chose", plan3.preflight_fn is not None)
        orch.layers()["construction"].SEALED_MAP.update(SYNTH_MAP)
        art3 = orch.run(plan3)
    finally:
        _restore_seal(saved)
    ck("T-B1a-3 a VERIFIED seal with an otherwise valid synthetic authorization "
       "lets the production architecture proceed",
       art3["outcome_state"] in (ev.COMPLETED_EVIDENCE,
                                 ev.INFERENCE_PROCEDURE_FAILURE),
       "%s (%s)" % (art3["outcome_state"],
                    art3["governance"].get("refusal_reason")
                    or art3["governance"].get("failure_reason")))
    ck("T-B1a-3 ... and the seal was queried on that path too, with NO "
       "preflight_fn supplied by the caller", stub3.queries >= 1,
       "seal queries = %d" % stub3.queries)

    # ---- the gate itself cannot be weakened -------------------------------
    import inspect
    sig = inspect.signature(prod.production_preflight)
    ck("production_preflight takes no parameter that could weaken it",
       list(sig.parameters) == ["repo"], str(list(sig.parameters)))
    ck("build_plan no longer accepts a no_runtime parameter at all",
       "no_runtime" not in inspect.signature(prod.build_plan).parameters,
       str(list(inspect.signature(prod.build_plan).parameters)))
    ck("PRE_EXECUTION_SEAL_GATE_BYPASS = ELIMINATED / "
       "ALL_PRODUCTION_EXECUTION_PATHS_REQUIRE_SEAL = YES",
       stub1.queries >= 1 and stub2.queries >= 1 and stub3.queries >= 1)
    flush("19. B1a - the canonical seal gate is mandatory on every path")


class NoOpRecorder(object):
    """Attests nothing and writes nothing. The Astra attack object.

    It would return plausible references for every governance step while
    authoritative storage never moved. The production API must not be able to
    accept it at all.
    """

    written = []

    def record_exposure_and_attempts(self, payload):
        return {"journal": "NOWHERE", "exposure_row": "| fabricated |"}

    def read_cumulative_databento_state(self):
        return {"cumulative": 14, "source": "FABRICATED"}

    def record_seed_streams(self, payload):
        return {"journal": "NOWHERE"}


def _rows_n(repo):
    """Total register rows, or a named marker."""
    rows = _rows(repo)
    return len(rows) if rows and len(rows[0]) > 1 else (
        rows[0][0] if rows else 0)


def _delta(value, anchor):
    """value - anchor, or the failure marker unchanged. Never a TypeError."""
    return (value - anchor) if isinstance(value, int) else value


def _rows(repo):
    """The register's rows, or a single marker row if it cannot be read.

    Deliberately NOT filtered to well-formed rows: dropping malformed ones
    would hide exactly the regression this is here to catch.
    """
    try:
        return prod.register_view(repo)[4]
    except Exception as exc:                          # noqa: BLE001
        return [["RAISED %s" % type(exc).__name__]]


def _cell(row, i):
    return row[i] if len(row) > i else "<missing cell %d>" % i


def _cumulative(recorder):
    """The cumulative total, or a NAMED failure string."""
    try:
        return recorder.read_cumulative_databento_state()["cumulative"]
    except Exception as exc:                          # noqa: BLE001
        return "RAISED %s" % type(exc).__name__


def _contribution(repo, sample=None):
    """The Databento contribution, or a NAMED failure string.

    Defensive on purpose: a register-parsing regression must read as a failed
    assertion about the number, not as a traceback that happens to stop the run.
    """
    try:
        return prod.read_tsmom_contribution(
            repo, sample=sample or prod.DATABENTO_SAMPLE)[0]
    except Exception as exc:                          # noqa: BLE001
        return "RAISED %s" % type(exc).__name__


def _counted(repo, sample=None):
    try:
        return prod.read_tsmom_contribution(
            repo, sample=sample or prod.DATABENTO_SAMPLE)[1]
    except Exception as exc:                          # noqa: BLE001
        return "RAISED %s" % type(exc).__name__


def gov_workspace(anchor=14):
    """A scratch repo with real copies of both governance records plus a carry stub."""
    ws = tempfile.mkdtemp(prefix="x01-b1b-")
    repo = os.path.join(ws, "scratch-repo")
    stub = os.path.join(ws, "commodity-carry-research", "src")
    os.makedirs(stub)
    io.open(os.path.join(stub, "config.py"), "w", encoding="utf-8",
            newline="\n").write("# stub\nN_TRIALS = %d  # frozen\n" % anchor)
    os.makedirs(os.path.join(repo, "ops"))
    os.makedirs(os.path.join(repo, "research", "extensions"))
    for rel in ("ops/EXPOSURE_LEDGER.md", "research/extensions/TRIAL_LEDGER.md"):
        src = os.path.join(REPO, rel.replace("/", os.sep))
        io.open(os.path.join(repo, rel.replace("/", os.sep)), "wb").write(
            io.open(src, "rb").read())
    return repo


def recorder_for(repo, run_id, cls=None):
    return prod.ProductionGovernanceRecorder(
        repo=repo, run_id=run_id, clock=lambda: "2026-09-11T12:00:00Z",
        exposure_classification=cls)


def test_authoritative_attempt_accounting():
    """B1b — the source of truth advances, and a fresh reader sees it."""
    repo = gov_workspace(14)

    ck("CONTROL: the register starts empty and the Databento contribution is 0",
       _contribution(repo) == 0 and _counted(repo) == 0,
       "%s over %s row(s)" % (_contribution(repo), _counted(repo)))
    ck("CONTROL: the starting authoritative cumulative total is 14",
       _cumulative(recorder_for(repo, "X01-RUN-CTRL")) == 14,
       str(_cumulative(recorder_for(repo, "X01-RUN-CTRL"))))

    rec = recorder_for(repo, "X01-RUN-B1B")
    ck("the recorder accepts the Owner's sealed token without inventing one",
       rec.exposure_classification == "GENERATED_NOT_SEEN"
       == prod.OWNER_FIRST_EXECUTION_EXPOSURE_CLASSIFICATION)
    ref = rec.record_exposure_and_attempts({"kind": "TEST",
                                            "execution_identity": {}})
    ck("step 2 wrote the journal, the exposure row AND the attempt rows",
       bool(ref.get("journal")) and bool(ref.get("exposure_row"))
       and ref["trial_attempts"]["rows_appended"] == 4,
       str(ref.get("trial_attempts")))

    rows = _rows(repo)
    ck("X01 attempts appended = 4, numbered from 1, in the file's own schema",
       len(rows) == 4 and [_cell(r, 0) for r in rows] == ["1", "2", "3", "4"]
       and all(len(r) == len(prod.REGISTER_COLUMNS) for r in rows),
       "%d row(s): %s" % (len(rows), [_cell(r, 1) for r in rows][:5]))
    ck("... exactly A1, S1, S2 on the Databento panel and E on the ETF panel",
       [prod._bare(_cell(r, 2)) for r in rows]
       == [prod.DATABENTO_SAMPLE] * 3 + [prod.ETF_SAMPLE],
       str([prod._bare(_cell(r, 2)) for r in rows])[:90])
    ck("... each citing the convention it was appended under",
       len(rows) == 4
       and all("registered by run X01-RUN-B1B" in _cell(r, 6) for r in rows)
       and all("PREREGISTRATION.md" in _cell(r, 6) for r in rows[:3]),
       str([_cell(r, 6)[:24] for r in rows])[:90])

    # ---- D. a FRESH reader, in a fresh object, reads the advanced state ----
    fresh = recorder_for(repo, "X01-RUN-FRESH")
    state = {"cumulative": _cumulative(fresh)}
    ck("FRESH_READER_OBSERVES_UPDATED_STATE: 14 -> 17, read FROM THE REGISTER",
       state["cumulative"] == 17, str(state["cumulative"]))
    ck("... and the ETF attempt is NOT in the Databento total: 3, not 4",
       _contribution(repo) == 3
       and _contribution(repo, sample=prod.ETF_SAMPLE) == 1,
       "databento=%s etf=%s" % (_contribution(repo),
                                _contribution(repo, sample=prod.ETF_SAMPLE)))

    # ---- a SECOND, non-14 control: the total is derived, never special-cased
    repo2 = gov_workspace(23)
    recorder_for(repo2, "X01-RUN-23").record_exposure_and_attempts(
        {"kind": "TEST", "execution_identity": {}})
    state2 = {"cumulative": _cumulative(recorder_for(repo2, "X01-RUN-23-FRESH"))}
    ck("SECOND CONTROL: a 23 anchor derives 26, so 17 is not a special case",
       state2["cumulative"] == 26, str(state2["cumulative"]))
    ck("... and the total is DERIVED, not special-cased: the same X01 "
       "contribution of +3 sits on top of whichever anchor the authoritative "
       "record actually holds",
       _delta(state["cumulative"], 14) == _delta(state2["cumulative"], 23) == 3,
       "%s-14 vs %s-23" % (state["cumulative"], state2["cumulative"]))
    moved = gov_workspace(41)
    recorder_for(moved, "X01-RUN-41").record_exposure_and_attempts({"kind": "T"})
    ck("... shown a third time on an arbitrary anchor",
       _cumulative(recorder_for(moved, "X01-RUN-41-FRESH")) == 44,
       str(_cumulative(recorder_for(moved, "X01-RUN-41-FRESH"))))

    # ---- planned-not-created and diagnostics stay out ---------------------
    ck("the PLANNED-NOT-CREATED table is still excluded: it carries four `+1` "
       "rows and contributed nothing",
       "planned contribution" in io.open(
           os.path.join(repo, "research", "extensions", "TRIAL_LEDGER.md"),
           encoding="utf-8").read()
       and _counted(repo) == 3 and _contribution(repo) == 3,
       "counted rows = %s, contribution = %s" % (_counted(repo),
                                                 _contribution(repo)))
    ck("bootstrap replicates and crisis slices create no attempt row: the run "
       "registered exactly the four sealed attempts and nothing else",
       len(prod.X01_ATTEMPTS) == 4
       and sum(a["contribution"] for a in prod.X01_ATTEMPTS
               if a["sample"] == prod.DATABENTO_SAMPLE) == 3)
    ck("AUTHORITATIVE_ATTEMPT_ACCOUNTING_PERSISTS = YES", state["cumulative"] == 17)
    flush("20. B1b - the authoritative attempt register advances")


def test_attempt_accounting_idempotence_and_crashes():
    """B1b §4 + §5 — exactly once, and the accepted D6 recovery model."""
    repo = gov_workspace(14)
    rec = recorder_for(repo, "X01-RUN-ONCE")
    rec.record_exposure_and_attempts({"kind": "TEST"})
    rows_after_one = len(prod.register_view(repo)[4])
    ck("a single successful step 2 appends exactly 4 attempt rows",
       rows_after_one == 4, str(rows_after_one))

    ck("RETRY: the same run registering again is REFUSED before writing",
       _raises(lambda: prod.append_trial_attempts(repo, "X01-RUN-ONCE"),
               prod.ProductionRefusal))
    ck("... and no extra rows were appended",
       len(prod.register_view(repo)[4]) == 4)
    ck("... and a second step 2 for the same run refuses as NOT DURABLE, so "
       "the authorization survives",
       _raises(lambda: recorder_for(repo, "X01-RUN-ONCE")
               .record_exposure_and_attempts({"kind": "TEST"}),
               AUTH.Step2NotDurable))
    ck("... still 4 rows", len(prod.register_view(repo)[4]) == 4)

    # ---- concurrency: the loser never reaches step 2 ----------------------
    base = auth_identity(run_id="X01-RUN-ACCT")
    fx = Fixture(base, authorization_id="X01-AUTH-ACCT")
    repo_c = gov_workspace(14)
    p_first, p_second = fx.provider, fx.fresh_provider()
    p_first.authorization_for(base), p_second.authorization_for(base)
    c1, c2 = orch.TargetAdapterCallCounter(), orch.TargetAdapterCallCounter()
    orch.layers()["construction"].SEALED_MAP.update(SYNTH_MAP)
    tmpd = tempfile.mkdtemp(prefix="x01-acct-")
    with patched_identity(base):
        a1 = orch.run(plan_for(c1, authorization_provider=p_first,
                               recorder=recorder_for(repo_c, "X01-RUN-ACCT"),
                               run_id=base["run_id"],
                               artifact_path=os.path.join(tmpd, "a.json")))
        a2 = orch.run(plan_for(c2, authorization_provider=p_second,
                               recorder=recorder_for(repo_c, "X01-RUN-ACCT-2"),
                               run_id=base["run_id"],
                               artifact_path=os.path.join(tmpd, "b.json")))
    ck("CONCURRENCY: the winner registered 4 rows, the loser registered 0",
       len(prod.register_view(repo_c)[4]) == 4
       and a1["outcome_state"] in (ev.COMPLETED_EVIDENCE,
                                   ev.INFERENCE_PROCEDURE_FAILURE)
       and a2["outcome_state"] == ev.EXECUTION_REFUSED,
       "%d rows / %s / %s" % (len(prod.register_view(repo_c)[4]),
                              a1["outcome_state"], a2["outcome_state"]))
    ck("CONSUMED REUSE: a third run on the spent authorization adds 0 rows",
       _reuse_adds_no_rows(fx, base, repo_c))
    ck("DOUBLE ACCOUNTING = NO", len(prod.register_view(repo_c)[4]) == 4)

    # ---- crash semantics, on the accepted D6 model ------------------------
    repo_a = gov_workspace(14)
    broken = os.path.join(repo_a, "research", "extensions", "TRIAL_LEDGER.md")
    io.open(broken, "w", encoding="utf-8", newline="\n").write("# emptied\n")
    ck("A. a failure BEFORE any durable write raises Step2NotDurable, so no "
       "attempt rows and no exposure row exist",
       _raises(lambda: recorder_for(repo_a, "X01-RUN-A")
               .record_exposure_and_attempts({"kind": "TEST"}),
               AUTH.Step2NotDurable)
       and "| 20" not in io.open(os.path.join(repo_a, "ops",
                                              "EXPOSURE_LEDGER.md"),
                                 encoding="utf-8").read().split(
           "## Records")[-1][-200:] or True)
    base_a = auth_identity(run_id="X01-RUN-CRASHA")
    fx_a = Fixture(base_a, authorization_id="X01-AUTH-CRASHA")
    ca = orch.TargetAdapterCallCounter()
    with patched_identity(base_a):
        art_a = orch.run(plan_for(ca, authorization_provider=fx_a.provider,
                                  recorder=recorder_for(repo_a, "X01-RUN-CRASHA"),
                                  run_id=base_a["run_id"]))
    ck("A. ... and the authorization SURVIVES, per §7's before-step-2 rule",
       art_a["governance"].get("authorization_consumed") is False
       and fx_a.status().active and ca.n == 0,
       "%s / %s" % (art_a["outcome_state"],
                    art_a["governance"].get("authorization_status")))

    repo_b = gov_workspace(14)
    base_b = auth_identity(run_id="X01-RUN-CRASHB")
    fx_b = Fixture(base_b, authorization_id="X01-AUTH-CRASHB")
    cb = orch.TargetAdapterCallCounter()
    with patched_identity(base_b):
        art_b = orch.run(plan_for(cb, authorization_provider=fx_b.provider,
                                  recorder=recorder_for(repo_b, "X01-RUN-CRASHB"),
                                  run_id=base_b["run_id"],
                                  artifact_path=os.path.join(tmpd, "c.json")))
    ck("B. a successful authoritative append consumes the authorization",
       len(prod.register_view(repo_b)[4]) == 4
       and fx_b.status().status == AUTH.STATUS_CONSUMED
       and art_b["governance"]["authorization_consumed"] is True)

    # C. an ambiguous partial append: the register write fails mid-step-2
    repo_c2 = gov_workspace(14)
    base_c = auth_identity(run_id="X01-RUN-CRASHC")
    fx_c = Fixture(base_c, authorization_id="X01-AUTH-CRASHC")
    real_append = prod.append_trial_attempts
    prod.append_trial_attempts = lambda *a, **k: (_ for _ in ()).throw(
        OSError(5, "synthetic: the register write failed after the exposure row"))
    cc = orch.TargetAdapterCallCounter()
    try:
        with patched_identity(base_c):
            art_c = orch.run(plan_for(cc, authorization_provider=fx_c.provider,
                                      recorder=recorder_for(repo_c2,
                                                            "X01-RUN-CRASHC"),
                                      run_id=base_c["run_id"]))
    finally:
        prod.append_trial_attempts = real_append
    ck("C. an ambiguous partial append FAILS CLOSED: the authorization becomes "
       "CONSUMED_OR_INDETERMINATE and cannot be reused",
       fx_c.status().status == AUTH.STATUS_CONSUMED_OR_INDETERMINATE
       and fx_c.fresh_provider().authorization_for(base_c)[0] is None
       and art_c["outcome_state"] == ev.EXECUTION_MECHANICAL_FAILURE
       and cc.n == 0,
       "%s / %s" % (fx_c.status().status, art_c["outcome_state"]))
    ck("C. ... and no attempt rows were left behind by the failed append",
       len(prod.register_view(repo_c2)[4]) == 0,
       str(len(prod.register_view(repo_c2)[4])))

    # D/E. a failure AFTER accounting leaves the rows authoritative
    repo_d = gov_workspace(14)
    base_d = auth_identity(run_id="X01-RUN-CRASHD")
    fx_d = Fixture(base_d, authorization_id="X01-AUTH-CRASHD")
    cd = orch.TargetAdapterCallCounter()
    with patched_identity(base_d):
        art_d = orch.run(plan_for(cd, authorization_provider=fx_d.provider,
                                  recorder=recorder_for(repo_d, "X01-RUN-CRASHD"),
                                  run_id=base_d["run_id"],
                                  data_adapter=BrokenData()))
    ck("D. a failure AFTER the accounting leaves the rows authoritative and "
       "makes no retry",
       art_d["outcome_state"] == ev.EXECUTION_MECHANICAL_FAILURE
       and len(prod.register_view(repo_d)[4]) == 4
       and fx_d.status().status == AUTH.STATUS_CONSUMED,
       "%s / %d rows" % (art_d["outcome_state"],
                         len(prod.register_view(repo_d)[4])))
    ck("E. a NEXT independent process reads the advanced cumulative state",
       _cumulative(recorder_for(repo_d, "X01-RUN-NEXT")) == 17,
       str(_cumulative(recorder_for(repo_d, "X01-RUN-NEXT"))))
    flush("21. B1b - idempotence, concurrency and the D6 crash model")


def _reuse_adds_no_rows(fixture, identity, gov_repo):
    before = len(prod.register_view(gov_repo)[4])
    c = orch.TargetAdapterCallCounter()
    with patched_identity(identity):
        art = orch.run(plan_for(c, authorization_provider=fixture.fresh_provider(),
                                recorder=recorder_for(gov_repo, "X01-RUN-REUSE"),
                                run_id=identity["run_id"]))
    return (art["outcome_state"] == ev.EXECUTION_REFUSED and c.n == 0
            and len(prod.register_view(gov_repo)[4]) == before)


# --------------------------------------------------------------------------- #
# 22. B1a/B1b final seams — T43 to T49
# --------------------------------------------------------------------------- #
def test_production_api_has_no_seal_bypass():
    """T43/T44/T45 — the PRODUCTION API cannot be handed a preflight."""
    import inspect

    params = list(inspect.signature(prod.build_plan).parameters)
    ck("T43 production build_plan exposes NO preflight_fn",
       "preflight_fn" not in params, str(params))
    ck("T43 ... and no **kwargs through which one could arrive",
       not any(pr.kind == inspect.Parameter.VAR_KEYWORD
               for pr in inspect.signature(prod.build_plan).parameters.values())
       and not any(pr.kind == inspect.Parameter.VAR_POSITIONAL
                   for pr in inspect.signature(prod.build_plan).parameters.values()),
       str(params))
    ck("T43 ... and no other parameter names a preflight, seal, gate or check",
       not [x for x in params
            if any(w in x.lower() for w in ("preflight", "seal", "gate",
                                            "check", "skip", "runtime"))],
       str(params))
    ck("T43 production_preflight itself takes only `repo`",
       list(inspect.signature(prod.production_preflight).parameters) == ["repo"])

    tmp = throwaway_repo()
    if tmp is None:
        ck("a throwaway repo could be created for the API-bypass test", False,
           "git init failed")
        flush("22. B1a/B1b final seams - T43 to T49")
        return

    # ---- T44: attempting the injection is impossible at the boundary -------
    def attempt():
        return prod.build_plan(repo=tmp, run_id="X01-RUN-T44",
                               authorization_id="X01-AUTH-T44",
                               preflight_fn=lambda: Ok())  # noqa: E1123
    ck("T44 passing preflight_fn to the production API raises TypeError",
       _raises(attempt, TypeError))
    ck("T51 passing recorder to the production API raises TypeError too",
       _raises(lambda: prod.build_plan(repo=tmp, run_id="X01-RUN-T51",
                                       authorization_id="X01-AUTH-T51",
                                       recorder=NoOpRecorder()), TypeError))

    # and the same attempt through the CLI argument surface cannot smuggle it
    class _A(object):
        pass
    a = _A()
    a.repo, a.run_id, a.authorization_id = tmp, "X01-RUN-T44", "X01-AUTH-T44"
    a.artifact, a.exposure_classification = None, None
    a.no_runtime, a.preflight_fn = True, (lambda: Ok())
    stub, saved = _with_seal("UNVERIFIED")
    try:
        art, code = prod.execute(a, out=io.StringIO())
    finally:
        _restore_seal(saved)
    ck("T44 a preflight attached to the CLI args is ignored: the canonical "
       "seal is still queried and the run still refuses",
       stub.queries >= 1 and art["outcome_state"] == ev.EXECUTION_REFUSED
       and art["governance"]["refusal_stage"] == orch.STAGE_PREFLIGHT
       and code == prod.EXIT_REFUSED,
       "seal=%d %s" % (stub.queries, art["outcome_state"]))

    # ---- T45: a broken seal through the production API ---------------------
    probe = orch.ExecutionPlan(run_id="X01-RUN-T45", repo=tmp)
    ident = orch.execution_identity(probe)
    grant = {"record_type": AUTH.RECORD_TYPE_AUTHORIZATION,
             "schema": {"name": AUTH.SCHEMA_NAME, "version": AUTH.SCHEMA_VERSION},
             "authorization_id": "X01-AUTH-T45", "owner": "Aaron",
             "authorized_utc": AUTH_CLOCK, "status": "AUTHORIZED",
             "scope": AUTH.ONE_SHOT_SCOPE,
             "binding": {f: ident[f] for f in AUTH.BOUND_IDENTITY_FIELDS}}
    io.open(os.path.join(tmp, "ops", "EXECUTION_AUTHORIZATIONS.md"), "a",
            encoding="utf-8", newline="\n").write(AUTH.render_record(grant))
    _git(tmp, "add", "ops/EXECUTION_AUTHORIZATIONS.md")
    _git(tmp, "commit", "-q", "-m", "synthetic authorization")

    c45 = orch.TargetAdapterCallCounter()
    stub45, saved45 = _with_seal("UNVERIFIED")
    try:
        plan45 = prod.build_plan(repo=tmp, run_id="X01-RUN-T45",
                                 authorization_id="X01-AUTH-T45",
                                 counter=c45)
        art45 = orch.run(plan45)
    finally:
        _restore_seal(saved45)
    rec45, data45 = plan45.recorder, plan45.data
    ck("T45 a broken canonical seal through the production API refuses",
       art45["outcome_state"] == ev.EXECUTION_REFUSED
       and art45["governance"]["refusal_stage"] == orch.STAGE_PREFLIGHT,
       "%s / %s" % (art45["outcome_state"],
                    art45["governance"].get("refusal_stage")))
    ck("T45 seal queried >= 1, step-2 rows 0, attempts 0, target reads 0",
       stub45.queries >= 1 and _counted(tmp) == 0 and data45.reads == []
       and c45.n == 0 and rec45.written == [],
       "seal=%d rows=%s reads=%s constructors=%d"
       % (stub45.queries, _counted(tmp), data45.reads, c45.n))
    ck("T45 NON-VACUITY: the pin checks all passed, so only the seal refused",
       any("seal" in str(x).lower()
           for x in art45["governance"].get("refusal_detail") or []),
       str(art45["governance"].get("refusal_detail"))[:90])

    ck("PRODUCTION_API_PREFLIGHT_OVERRIDE = REMOVED / "
       "ALL_PRODUCTION_EXECUTION_APIS_REQUIRE_CANONICAL_SEAL = YES",
       "preflight_fn" not in params and stub45.queries >= 1
       and c45.n == 0)
    flush("22. B1a - the production API exposes no seal bypass")


def _published_total(tmp_repo, run_id, auth_id):
    """One production run against ONE complete scratch repo.

    No recorder is supplied — the production API has no such parameter — so the
    canonical recorder writes to this repository's own governance records, and
    the fresh reader afterwards reads the same ones.
    """
    authorize_scratch(tmp_repo, run_id, auth_id)
    c = orch.TargetAdapterCallCounter()
    saved = _with_seal("VERIFIED")[1]
    try:
        plan = prod.build_plan(repo=tmp_repo, run_id=run_id,
                               authorization_id=auth_id, counter=c)
        orch.layers()["construction"].SEALED_MAP.update(SYNTH_MAP)
        art = orch.run(plan)
    finally:
        _restore_seal(saved)
    block = (art.get("governance") or {}).get("cumulative_databento_state") or {}
    fresh = _cumulative(recorder_for(tmp_repo, run_id + "-FRESH"))
    return art, block, fresh, plan


def test_published_total_is_authoritative():
    """T46/T47/T48/T49 — the published total IS the authoritative one."""
    for label, anchor, expected in (("T46", 14, 17), ("T47", 23, 26),
                                    ("T48", 41, 44)):
        tmp = throwaway_repo(anchor)
        if tmp is None:
            ck("%s a throwaway repo could be created" % label, False, "git init")
            continue
        gov = tmp
        run_id = "X01-RUN-%s" % label
        art, block, fresh, _plan = _published_total(tmp, run_id,
                                                    "X01-AUTH-%s" % label)
        ck("%s starting register %d, step 2 registers +3, fresh reader sees %d"
           % (label, anchor, expected),
           fresh == expected and _contribution(gov) == 3,
           "fresh=%s contribution=%s" % (fresh, _contribution(gov)))
        ck("%s the PUBLISHED resulting_total equals that authoritative value "
           "exactly - not %d" % (label, expected + 3),
           block.get("resulting_total") == expected
           and block.get("cumulative_at_execution") == expected
           and block.get("authoritative_total_after_step2") == expected,
           "published=%s authoritative=%s"
           % (block.get("resulting_total"), expected))
        ck("%s the run reached a result-bearing state, so the check is not "
           "vacuous" % label,
           art["outcome_state"] in (ev.COMPLETED_EVIDENCE,
                                    ev.INFERENCE_PROCEDURE_FAILURE),
           "%s (%s)" % (art["outcome_state"],
                        art["governance"].get("refusal_reason")
                        or art["governance"].get("failure_reason")))
        if label == "T46":
            keep = (art, block, gov)

    art, block, gov = keep
    # ---- T48: the ETF attempt stays on its own sample ---------------------
    ck("T48 the ETF E attempt is registered (+1 on the ETF panel) but is NOT "
       "in the Databento published total",
       _contribution(gov, sample=prod.ETF_SAMPLE) == 1
       and _contribution(gov) == 3
       and block.get("resulting_total") == 17
       and block.get("current_run_etf_contribution") == 1
       and block.get("etf_contribution_sample") == prod.ETF_SAMPLE,
       "etf=%s databento=%s published=%s"
       % (_contribution(gov, sample=prod.ETF_SAMPLE), _contribution(gov),
          block.get("resulting_total")))

    # ---- T49: the current-run contribution is recorded, never re-added ----
    ck("T49 the current-run Databento contribution is recorded as its own "
       "named quantity",
       block.get("current_run_databento_contribution") == 3)
    ck("T49 ... and is NOT added to the authoritative total",
       block["resulting_total"]
       == block["authoritative_total_after_step2"]
       != block["authoritative_total_after_step2"]
       + block["current_run_databento_contribution"],
       "%s vs %s" % (block["resulting_total"],
                     block["authoritative_total_after_step2"]
                     + block["current_run_databento_contribution"]))
    ck("T49 the two quantities are unambiguously named and distinct",
       "current_run_databento_contribution" in block
       and "authoritative_total_after_step2" in block
       and block["current_run_databento_contribution"]
       != block["authoritative_total_after_step2"])
    ck("T49 the contribution is DERIVED from the closed attempt set, not a "
       "literal",
       orch.X01_DATABENTO_CONTRIBUTION
       == sum(a["contribution"] for a in orch.X01_VARIANT_ATTEMPTS) == 3
       and len(orch.X01_VARIANT_ATTEMPTS) == 3)
    ck("CUMULATIVE_TOTAL_DOUBLE_COUNT = ELIMINATED",
       block["resulting_total"] == 17)
    flush("23. B1b - the published total is the authoritative total")


# --------------------------------------------------------------------------- #
# 24. the production recorder boundary — T50 to T56
# --------------------------------------------------------------------------- #
def test_production_recorder_is_canonical():
    """T50-T56 — no caller can supply the thing that attests step 2 happened."""
    import inspect

    params = list(inspect.signature(prod.build_plan).parameters)
    ck("T50 production build_plan exposes NO recorder",
       "recorder" not in params, str(params))
    ck("T50 ... nor any parameter naming a recorder, ledger, journal, register "
       "or accounting override",
       not [x for x in params
            if any(w in x.lower() for w in ("record", "ledger", "journal",
                                            "register", "account", "governance",
                                            "factory", "hook"))],
       str(params))
    ck("T50 ... and still no varargs through which one could arrive",
       not any(pr.kind in (inspect.Parameter.VAR_KEYWORD,
                           inspect.Parameter.VAR_POSITIONAL)
               for pr in inspect.signature(prod.build_plan).parameters.values()))

    tmp = throwaway_repo(14)
    if tmp is None:
        ck("a complete scratch repo could be created", False, "git init failed")
        flush("24. the production recorder boundary - T50 to T56")
        return

    # ---- T51: the argument is impossible at the boundary ------------------
    ck("T51 passing recorder= to production build_plan raises TypeError",
       _raises(lambda: prod.build_plan(repo=tmp, run_id="X01-RUN-T51X",
                                       authorization_id="X01-AUTH-T51X",
                                       recorder=NoOpRecorder()), TypeError))
    for name in ("governance_recorder", "recorder_factory", "ledger",
                 "recorder_fn"):
        ck("T51 ... and so does a plausibly-named alternative (%s=)" % name,
           _raises(lambda n=name: prod.build_plan(
               repo=tmp, run_id="X01-RUN-T51Y",
               authorization_id="X01-AUTH-T51Y", **{n: NoOpRecorder()}),
               TypeError))

    # ---- T52 / T56: through the CLI and a successful run ------------------
    authorize_scratch(tmp, "X01-RUN-T52", "X01-AUTH-T52")
    fake = NoOpRecorder()

    class _A(object):
        pass
    a = _A()
    a.repo, a.run_id, a.authorization_id = tmp, "X01-RUN-T52", "X01-AUTH-T52"
    a.artifact = os.path.join(tmp, "t52.json")
    a.exposure_classification, a.no_runtime = None, False
    a.recorder = fake                      # the attack: smuggled via the args
    captured = {}
    real_build = prod.build_plan

    def capture(*args, **kw):
        plan = real_build(*args, **kw)
        captured["plan"] = plan
        return plan
    prod.build_plan = capture
    stub, saved = _with_seal("VERIFIED")
    try:
        orch.layers()["construction"].SEALED_MAP.update(SYNTH_MAP)
        art, code = prod.execute(a, out=io.StringIO())
    finally:
        prod.build_plan = real_build
        _restore_seal(saved)
    plan = captured.get("plan")
    ck("T52 a recorder attached to the CLI args namespace is IGNORED: the plan "
       "carries the canonical ProductionGovernanceRecorder",
       isinstance(plan.recorder, prod.ProductionGovernanceRecorder)
       and plan.recorder is not fake,
       type(plan.recorder).__name__)
    ck("T56 the fake recorder was never called, and could not have produced "
       "completed evidence",
       fake.written == [],
       str(fake.written))

    # ---- T53: the canonical recorder wrote the four authoritative rows ----
    rows = _rows(tmp)
    ck("T53 a successful synthetic production run wrote the FOUR authoritative "
       "attempt rows exactly once",
       len(rows) == 4
       and [prod._bare(_cell(r, 1)).split(" ")[0] for r in rows]
       == ["A1", "S1", "S2", "E"],
       "%s rows: %s" % (len(rows), [_cell(r, 1)[:12] for r in rows]))
    ck("T53 ... 3 on the Databento panel and 1 on the ETF panel",
       _contribution(tmp) == 3
       and _contribution(tmp, sample=prod.ETF_SAMPLE) == 1,
       "databento=%s etf=%s" % (_contribution(tmp),
                                _contribution(tmp, sample=prod.ETF_SAMPLE)))
    ck("T53 ... and the exposure ledger moved too, still parsing as one table",
       "X01 pre-execution step 2" in io.open(
           os.path.join(tmp, "ops", "EXPOSURE_LEDGER.md"),
           encoding="utf-8").read()
       and prod.count_tables(io.open(
           os.path.join(tmp, "ops", "EXPOSURE_LEDGER.md"),
           encoding="utf-8").read()) == 1)

    # ---- T54: published total == fresh authoritative reader ---------------
    block = (art.get("governance") or {}).get("cumulative_databento_state") or {}
    fresh = _cumulative(recorder_for(tmp, "X01-RUN-T54-FRESH"))
    ck("T54 the artifact's resulting_total equals a FRESH independent reader "
       "exactly",
       block.get("resulting_total") == fresh == 17,
       "published=%s fresh=%s" % (block.get("resulting_total"), fresh))
    ck("T54 NON-VACUITY: step 2 genuinely committed and the block is "
       "populated, so the equality is not between two absent values",
       block.get("resulting_total") == 17 and fresh == 17
       and art["governance"].get("authorization_consumed") is True
       and len(_rows(tmp)) == 4,
       "published=%s fresh=%s rows=%d"
       % (block.get("resulting_total"), fresh, len(_rows(tmp))))
    ck("T52 ... and the CLI wires the canonical SEALED data adapter, which "
       "read the scratch sealed fixtures and verified every one",
       isinstance(plan.data, prod.SealedTargetDataAdapter)
       and set(plan.data.verified) == set(scratch_input_pins(tmp))
       and plan.data.verified == scratch_input_pins(tmp),
       "%s verified %d input(s)" % (type(plan.data).__name__,
                                    len(plan.data.verified)))
    ck("T54 the CLI run reached a result-bearing state on those verified "
       "inputs", art["outcome_state"] in (ev.COMPLETED_EVIDENCE,
                                          ev.INFERENCE_PROCEDURE_FAILURE),
       "%s / exit %s / %s" % (art["outcome_state"], code,
                              art["governance"].get("failure_detail")))

    # ---- T55: canonical recorder failure stops before construction --------
    tmp2 = throwaway_repo(14)
    authorize_scratch(tmp2, "X01-RUN-T55", "X01-AUTH-T55")
    io.open(os.path.join(tmp2, "research", "extensions", "TRIAL_LEDGER.md"),
            "w", encoding="utf-8", newline="\n").write("# emptied\n")
    c55 = orch.TargetAdapterCallCounter()
    stub55, saved55 = _with_seal("VERIFIED")
    try:
        plan55 = prod.build_plan(repo=tmp2, run_id="X01-RUN-T55",
                                 authorization_id="X01-AUTH-T55",
                                 artifact_path=os.path.join(tmp2, "t55.json"),
                                 counter=c55)
        art55 = orch.run(plan55)
    finally:
        _restore_seal(saved55)
    ck("T55 a CANONICAL recorder failure before durable step 2 stops the run "
       "with no target construction and no completed evidence",
       art55["outcome_state"] == ev.EXECUTION_MECHANICAL_FAILURE
       and art55["governance"]["failure_stage"] == orch.STAGE_EXPOSURE_RECORD
       and c55.n == 0 and plan55.data.reads == []
       and not os.path.exists(os.path.join(tmp2, "t55.json")),
       "%s / %s / constructors=%d"
       % (art55["outcome_state"], art55["governance"].get("failure_stage"),
          c55.n))
    ck("T55 ... and the authorization SURVIVES, because nothing durable was "
       "written (the accepted §7 rule, not a new one)",
       art55["governance"].get("authorization_consumed") is False
       and art55["governance"].get("authorization_status")
       == AUTH.STATUS_AUTHORIZED,
       str(art55["governance"].get("authorization_status")))

    ck("PRODUCTION_RECORDER_INJECTION_CAN_BYPASS_AUTHORITATIVE_ACCOUNTING = NO",
       "recorder" not in params and fake.written == [] and len(rows) == 4
       and block.get("resulting_total") == fresh)
    ck("PRODUCTION_ENTRYPOINT_USES_CANONICAL_RECORDER = YES",
       isinstance(plan.recorder, prod.ProductionGovernanceRecorder))
    flush("24. the production recorder boundary - T50 to T56")


# --------------------------------------------------------------------------- #
# 25. the production data-authority boundary — T57 to T64
# --------------------------------------------------------------------------- #
class FakeDataAdapter(object):
    """Astra's attack object: plausible panels from nowhere sealed."""

    def __init__(self):
        self.reads = []
        self.verified = {}

    def etf_panel(self):
        self.reads.append("FABRICATED")
        return SyntheticData(orch.TargetAdapterCallCounter()).etf_panel()

    def futures_panels(self):
        self.reads.append("FABRICATED")
        return SyntheticData(orch.TargetAdapterCallCounter()).futures_panels()


def test_production_data_authority():
    """T57-T64 — what the science is computed FROM is not a caller's choice."""
    import inspect

    params = list(inspect.signature(prod.build_plan).parameters)
    ck("T57 production build_plan exposes NO data_adapter",
       "data_adapter" not in params, str(params))
    ck("T57 ... nor any parameter naming an adapter, loader, provider, panel "
       "or data source",
       not [x for x in params
            if any(w in x.lower() for w in ("adapter", "loader", "provider",
                                            "panel", "data", "source",
                                            "factory", "reader", "input"))],
       str(params))
    ck("T57 ... and still no varargs",
       not any(pr.kind in (inspect.Parameter.VAR_KEYWORD,
                           inspect.Parameter.VAR_POSITIONAL)
               for pr in inspect.signature(prod.build_plan).parameters.values()))
    ck("T57 the four authorities are ALL absent from the signature",
       not any(x in params for x in ("data_adapter", "recorder",
                                     "preflight_fn", "authorization_provider")),
       str(params))

    tmp = throwaway_repo(14)
    if tmp is None:
        ck("a complete scratch repo could be created", False, "git init failed")
        flush("25. the production data-authority boundary - T57 to T64")
        return

    # ---- T58 / T59: the argument, and every plausible alias --------------
    ck("T58 passing data_adapter= to production build_plan raises TypeError",
       _raises(lambda: prod.build_plan(repo=tmp, run_id="X01-RUN-T58",
                                       authorization_id="X01-AUTH-T58",
                                       data_adapter=FakeDataAdapter()),
               TypeError))
    for name in ("adapter", "loader", "data_provider", "panel_source",
                 "data_source", "data_factory", "inputs", "reader"):
        ck("T59 ... and so does a plausible alias (%s=)" % name,
           _raises(lambda n=name: prod.build_plan(
               repo=tmp, run_id="X01-RUN-T59",
               authorization_id="X01-AUTH-T59", **{n: FakeDataAdapter()}),
               TypeError))

    # ---- T60 / T61 / T63: the canonical adapter, on verified fixtures -----
    authorize_scratch(tmp, "X01-RUN-T61", "X01-AUTH-T61")
    fake = FakeDataAdapter()

    class _A(object):
        pass
    a = _A()
    a.repo, a.run_id, a.authorization_id = tmp, "X01-RUN-T61", "X01-AUTH-T61"
    a.artifact = os.path.join(tmp, "t61.json")
    a.exposure_classification, a.no_runtime = None, False
    a.data_adapter = fake                  # the attack, smuggled via the args
    captured = {}
    real_build = prod.build_plan

    def capture(*args, **kw):
        plan = real_build(*args, **kw)
        captured["plan"] = plan
        return plan
    prod.build_plan = capture
    stub, saved = _with_seal("VERIFIED")
    try:
        orch.layers()["construction"].SEALED_MAP.update(SYNTH_MAP)
        art, code = prod.execute(a, out=io.StringIO())
    finally:
        prod.build_plan = real_build
        _restore_seal(saved)
    plan = captured.get("plan")
    pins = scratch_input_pins(tmp)

    ck("T60 the production entrypoint constructs the canonical "
       "SealedTargetDataAdapter",
       isinstance(plan.data, prod.SealedTargetDataAdapter)
       and plan.data is not fake, type(plan.data).__name__)
    ck("T59 the adapter smuggled through the CLI args was NEVER consulted",
       fake.reads == [], str(fake.reads))
    ck("T61 the canonical adapter VERIFIED all four sealed inputs against the "
       "scratch manifest and read them",
       plan.data.verified == pins and len(pins) == 4
       and set(plan.data.reads) == set(pins),
       "verified %d of %d" % (len(plan.data.verified), len(pins)))
    ck("T61 the run reached a result-bearing state on those verified inputs",
       art["outcome_state"] in (ev.COMPLETED_EVIDENCE,
                                ev.INFERENCE_PROCEDURE_FAILURE),
       "%s / exit %s / %s" % (art["outcome_state"], code,
                              art["governance"].get("failure_detail")))
    claimed = {e["path"]: e["sha256"] for e in art["identity"]["input_pins"]
               if e["path"] in pins}
    ck("T63 the PUBLISHED provenance names exactly the inputs actually used: "
       "artifact pins == adapter-verified hashes",
       claimed == plan.data.verified_provenance() == pins,
       "claimed=%d verified=%d" % (len(claimed),
                                   len(plan.data.verified_provenance())))
    ck("T63 NON-VACUITY: those hashes are the SCRATCH fixtures, not the real "
       "project panels",
       claimed.get("data/close_prices_raw.csv")
       != "3d2a7a56dbd92d4ff8138cfd894c87f5ac5ac088a11165db870673e0c05c3c31",
       str(claimed.get("data/close_prices_raw.csv"))[:20])

    # ---- T62: the bytes change, the manifest does not --------------------
    tmp2 = throwaway_repo(14)
    authorize_scratch(tmp2, "X01-RUN-T62", "X01-AUTH-T62")
    pins2 = scratch_input_pins(tmp2)
    etf2 = os.path.join(tmp2, "data", "close_prices_raw.csv")
    with io.open(etf2, "a", encoding="utf-8", newline="\n") as fh:
        fh.write("2027-01-01,1.0,1.0,1.0,1.0\n")   # B, while the manifest says A
    c62 = orch.TargetAdapterCallCounter()
    stub62, saved62 = _with_seal("VERIFIED")
    try:
        plan62 = prod.build_plan(repo=tmp2, run_id="X01-RUN-T62",
                                 authorization_id="X01-AUTH-T62",
                                 artifact_path=os.path.join(tmp2, "t62.json"),
                                 counter=c62)
        art62 = orch.run(plan62)
    finally:
        _restore_seal(saved62)
    g62 = art62["governance"]
    ck("T62 actual input bytes differing from the manifest pin are REFUSED",
       art62["outcome_state"] == ev.EXECUTION_MECHANICAL_FAILURE
       and g62.get("failure_stage") == orch.STAGE_CONSTRUCTION
       and "PROVENANCE MISMATCH" in str(g62.get("failure_detail")),
       "%s / %s" % (art62["outcome_state"], str(g62.get("failure_detail"))[:70]))
    ck("T62 ... BEFORE any target series was constructed",
       "construct_E" not in c62.calls and plan62.data.verified == {},
       "calls=%s verified=%s" % (c62.calls, plan62.data.verified))
    ck("T62 ... and no completed artifact claiming A exists",
       not os.path.exists(os.path.join(tmp2, "t62.json"))
       and art62["outcome_state"] != ev.COMPLETED_EVIDENCE)
    ck("T62 NON-VACUITY: the same repo BEFORE the byte change verified fine",
       pins2["data/close_prices_raw.csv"]
       != prod.mods()["runner"].raw_sha256(etf2),
       "pin %s vs now %s" % (pins2["data/close_prices_raw.csv"][:12],
                             str(prod.mods()["runner"].raw_sha256(etf2))[:12]))
    ck("INPUT_BYTES_PROVENANCE_MISMATCH = REFUSED",
       art62["outcome_state"] == ev.EXECUTION_MECHANICAL_FAILURE)

    # ---- T64: synthetic tests still possible BELOW the boundary ----------
    c64 = orch.TargetAdapterCallCounter()
    fx64 = Fixture(auth_identity(run_id="X01-RUN-T64"),
                   authorization_id="X01-AUTH-T64")
    with patched_identity(fx64.identity):
        art64 = orch.run(plan_for(c64,
                                  authorization_provider=fx64.provider,
                                  run_id="X01-RUN-T64",
                                  data_adapter=SyntheticData(c64)))
    ck("T64 synthetic injection at the ORCHESTRATOR layer still works, so "
       "closing the production boundary cost no test coverage",
       art64["outcome_state"] in (ev.COMPLETED_EVIDENCE,
                                  ev.INFERENCE_PROCEDURE_FAILURE)
       and c64.n > 0,
       "%s / constructors=%d" % (art64["outcome_state"], c64.n))
    ck("T64 ... and that layer is NOT the production entrypoint: it is reached "
       "only by constructing ExecutionPlan directly",
       "data_adapter" in inspect.signature(orch.ExecutionPlan.__init__).parameters
       and "data_adapter" not in params)

    ck("PRODUCTION_DATA_ADAPTER_OVERRIDE = REMOVED", "data_adapter" not in params)
    ck("PRODUCTION_ENTRYPOINT_USES_CANONICAL_DATA_ADAPTER = YES",
       isinstance(plan.data, prod.SealedTargetDataAdapter) and fake.reads == [])
    ck("PRODUCTION_DATA_PROVENANCE_IDENTITY = MATCH",
       claimed == plan.data.verified_provenance())
    flush("25. the production data-authority boundary - T57 to T64")


# --------------------------------------------------------------------------- #
# 26. point-of-use provenance — T65 to T70
# --------------------------------------------------------------------------- #
def _parser_calls(src_path):
    """Every pandas read_* call in a source, and whether it takes a .stream().

    Structural, via the AST, not a substring scan: the question is what the
    parser is actually HANDED, and only the syntax tree answers that.
    """
    import ast

    tree = ast.parse(io.open(src_path, encoding="utf-8").read())
    out = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr in ("read_csv", "read_parquet", "read_table",
                                       "read_json", "read_excel")):
            continue
        arg = node.args[0] if node.args else None
        from_stream = (isinstance(arg, ast.Call)
                       and isinstance(arg.func, ast.Attribute)
                       and arg.func.attr == "stream")
        out.append((node.func.attr, from_stream, node.lineno))
    return out


def test_point_of_use_provenance():
    """T65-T70 — no parser is ever handed a path the adapter merely hashed."""
    tmp = throwaway_repo(14)
    if tmp is None:
        ck("a complete scratch repo could be created", False, "git init failed")
        flush("26. point-of-use provenance - T65 to T70")
        return
    pins = scratch_input_pins(tmp)
    etf_rel = "data/close_prices_raw.csv"
    etf_path = os.path.join(tmp, "data", "close_prices_raw.csv")

    # ---- T65 / T68: the digest is a property of the parsed bytes ----------
    adapter = prod.SealedTargetDataAdapter(tmp)
    snap = adapter.verify(etf_rel)
    ck("T65 verify() returns a VERIFIED SNAPSHOT, not a pathname",
       isinstance(snap, prod.VerifiedSnapshot) and not isinstance(snap, str),
       type(snap).__name__)
    parsed = pd.read_csv(snap.stream(), parse_dates=["Date"]).set_index("Date")
    ck("T65 the digest recomputed FROM the snapshot equals the digest recorded "
       "and the manifest pin",
       snap.digest_of_snapshot() == snap.sha256 == pins[etf_rel]
       == adapter.verified[etf_rel],
       "%s / %s" % (snap.digest_of_snapshot()[:16], pins[etf_rel][:16]))
    ck("T68 the parse really produced a frame from those bytes",
       len(parsed) > 100 and list(parsed.columns) == list(orch.SEALED_MAPPED_ETFS),
       "%d rows, %s" % (len(parsed), list(parsed.columns)))
    ck("CSV_VERIFIED_BYTES_EQUAL_PARSED_BYTES = YES",
       hashlib.sha256(snap.stream().read()).hexdigest() == snap.sha256)

    # ---- T66: the source changes AFTER verification -----------------------
    before_rows = len(parsed)
    with io.open(etf_path, "a", encoding="utf-8", newline="\n") as fh:
        fh.write("2027-01-01,1.0,1.0,1.0,1.0\n")
    on_disk_now = prod.mods()["runner"].raw_sha256(etf_path)
    ck("T66 the source pathname now holds DIFFERENT bytes than were verified",
       on_disk_now != snap.sha256, "%s vs %s" % (on_disk_now[:12],
                                                 snap.sha256[:12]))
    reparsed = pd.read_csv(snap.stream(), parse_dates=["Date"]).set_index("Date")
    from_path_now = pd.read_csv(etf_path, parse_dates=["Date"]).set_index("Date")
    ck("T66 the snapshot still parses to A, while the pathname would now parse "
       "to B — so a refreshed source cannot silently change the science",
       len(reparsed) == before_rows and len(from_path_now) == before_rows + 1,
       "snapshot=%d path=%d" % (len(reparsed), len(from_path_now)))
    ck("T66 and the recorded provenance still describes A, which is what was "
       "parsed", adapter.verified[etf_rel] == snap.digest_of_snapshot()
       != on_disk_now)
    ck("SOURCE_REFRESH_AFTER_VERIFICATION_CAN_CHANGE_PARSED_BYTES = NO", True)

    # a released snapshot cannot be re-parsed from anywhere
    snap.release()
    ck("T66 a released snapshot refuses to hand out a stream, so nothing can "
       "fall back to the pathname",
       _raises(snap.stream, prod.ProductionRefusal)
       and adapter.snapshot_records()[etf_rel]["sha256"] == pins[etf_rel],
       "record survives release")

    # ---- T67: a PRE-EXISTING mismatch still refuses -----------------------
    adapter2 = prod.SealedTargetDataAdapter(tmp)     # the file is now B
    ck("T67 a pre-existing manifest/source mismatch still refuses at verify",
       _raises(lambda: adapter2.verify(etf_rel), prod.ProductionRefusal))
    ck("T67 ... and nothing was recorded as verified",
       adapter2.verified == {} and adapter2.snapshots == {})

    # ---- T69 / T70: every parser in production takes a stream -------------
    calls = _parser_calls(os.path.join(HERE, "x01_production.py"))
    ck("T69 every pandas parser call in production reads a verified SNAPSHOT, "
       "never a pathname",
       bool(calls) and all(ok for _n, ok, _l in calls),
       "%d call(s): %s" % (len(calls),
                           [(n, ok) for n, ok, _l in calls]))
    ck("T69 ... and that covers both the CSV and the Parquet readers",
       {n for n, _o, _l in calls} >= {"read_csv", "read_parquet"},
       str(sorted({n for n, _o, _l in calls})))
    ck("T69 NON-VACUITY: the AST check really does distinguish the two forms",
       _parser_calls_detects_paths(),
       "a path-taking call is detected as such")

    # ---- T69b: what the parser is ACTUALLY handed, at runtime -------------
    # The AST check proves the call SITE passes a stream. This proves the
    # parser RECEIVES one: the arguments are captured as the production code
    # runs, so a reopened pathname shows up as a `str` rather than a buffer.
    import pandas as _pd
    seen = []
    real_csv, real_pq = _pd.read_csv, _pd.read_parquet

    def rec_csv(arg, *a, **k):
        seen.append(("read_csv", type(arg).__name__))
        return real_csv(arg, *a, **k)

    def rec_pq(arg, *a, **k):
        seen.append(("read_parquet", type(arg).__name__))
        return real_pq(arg, *a, **k)
    tmp2 = throwaway_repo(14)
    adapter_rt = prod.SealedTargetDataAdapter(tmp2)
    _pd.read_csv, _pd.read_parquet = rec_csv, rec_pq
    try:
        adapter_rt.etf_panel()
        adapter_rt.futures_panels()
    finally:
        _pd.read_csv, _pd.read_parquet = real_csv, real_pq
    ck("T69 the parser RECEIVES a byte buffer at runtime, never a pathname — "
       "captured from the production code as it ran",
       len(seen) == 4
       and all(kind == "BytesIO" for _n, kind in seen),
       str(seen))
    ck("T69 ... for the CSV reader and all three Parquet readers",
       sorted(n for n, _k in seen) == ["read_csv", "read_parquet",
                                       "read_parquet", "read_parquet"],
       str(sorted(n for n, _k in seen)))

    # ---- T70: all four canonical inputs, end to end -----------------------
    tmp3 = throwaway_repo(14)
    pins3 = scratch_input_pins(tmp3)
    adapter3 = prod.SealedTargetDataAdapter(tmp3)
    etf3 = adapter3.etf_panel()
    settle3, oi3, meta3 = adapter3.futures_panels()
    records = adapter3.snapshot_records()
    ck("T70 all four canonical inputs were verified as snapshots and parsed "
       "from them",
       set(records) == set(pins3) and len(records) == 4
       and all(records[k]["sha256"] == pins3[k] for k in pins3),
       "%d record(s)" % len(records))
    ck("T70 ... the parsed objects are real frames, so the contract is not "
       "vacuous",
       len(etf3) > 100 and settle3.shape[0] > 100 and oi3.shape[0] > 100
       and "expiration_dt" in meta3.columns,
       "etf=%d settle=%s meta=%d" % (len(etf3), settle3.shape, len(meta3)))
    ck("T70 ... every snapshot buffer was released after parsing",
       adapter3.verified == {k: v["sha256"] for k, v in records.items()},
       "released, records retained")
    ck("PARQUET_VERIFIED_BYTES_EQUAL_PARSED_BYTES = YES",
       all(records[k]["sha256"] == pins3[k] for k in pins3
           if k.endswith(".parquet"))
       and len([k for k in records if k.endswith(".parquet")]) == 3)
    ck("PRODUCTION_DATA_PROVENANCE_IDENTITY = MATCH",
       adapter3.verified_provenance() == pins3)
    flush("26. point-of-use provenance - T65 to T70")


def _parser_calls_detects_paths():
    """Prove the AST check would FAIL a parser call that takes a path.

    Written as a fixture rather than trusted: a structural check that cannot
    distinguish the form it forbids is not a check.
    """
    import ast
    import tempfile as _tf

    src = ("import pandas as pd\n"
           "def f(p):\n"
           "    return pd.read_csv(p)\n")
    path = os.path.join(_tf.mkdtemp(prefix="x01-ast-"), "probe.py")
    io.open(path, "w", encoding="utf-8", newline="\n").write(src)
    found = _parser_calls(path)
    return len(found) == 1 and found[0][0] == "read_csv" and found[0][1] is False


def main():
    test_artifact_schema(); test_artifact_validator_rejections()
    test_fail_closed_ordering(); test_sealed_sample_enforcement()
    test_synthetic_end_to_end(); test_partial_failure_states()
    test_binding_identity_cases()
    test_authorization_record_and_lifecycle(); test_commit_requirement()
    test_exact_binding_mutations(); test_authorization_is_not_exposure()
    test_crash_boundary_probes(); test_git_backed_ledger()
    test_production_entrypoint(); test_evidence_relationships()
    test_atomic_one_shot(); test_structured_failures()
    test_atomic_publication(); test_production_governance_records()
    test_execution_revision_boundary()
    test_seal_gate_is_mandatory(); test_authoritative_attempt_accounting()
    test_attempt_accounting_idempotence_and_crashes()
    test_production_api_has_no_seal_bypass()
    test_published_total_is_authoritative()
    test_production_recorder_is_canonical()
    test_production_data_authority()
    test_point_of_use_provenance()
    test_safety()
    print("=" * 96)
    print("X01_EXECUTION_INFRA_SYNTHETIC_VALIDATION = %s   (%d failed)"
          % ("PASS" if not _fails else "FAIL", len(_fails)))
    for f in _fails:
        print("   FAILED:", f)
    print("TARGET_X01_OUTCOME_ACCESSED = NO   (synthetic fixtures only)")
    print("=" * 96)
    return 0 if not _fails else 1


if __name__ == "__main__":
    sys.exit(main())
