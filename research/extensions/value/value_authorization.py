# -*- coding: utf-8 -*-
"""The S3 execution authorization — a single-use Owner object.

A seal is not authorization to execute. This module is the only thing that can
open the real run, and it opens it exactly once:

    absent            -> refuse
    wrong seal        -> refuse   (bound to the exact sealed bytes)
    status CONSUMED   -> refuse
    status ACTIVE     -> execute, then mark CONSUMED before the artifact is
                         declared final, so a crash cannot silently free a
                         second attempt

Creating an authorization is an Owner act, never an agent act. `create()` exists
so Aaron can perform it deliberately through `value_runner.py authorize`, which
demands the decision phrase in full. Nothing in the build calls it.
"""
import datetime
import io
import json
import os
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))

AUTH_RELPATH = "research/extensions/value/VALUE_S3_AUTHORIZATION.json"
AUTH_PATH = os.path.join(HERE, "VALUE_S3_AUTHORIZATION.json")
SCHEMA = "VALUE_S3_AUTHORIZATION_V1"

STATUS_ACTIVE = "ACTIVE"
STATUS_CONSUMED = "CONSUMED"

OWNER_DECISION_PHRASE = (
    "AARON OWNER DECISION - AUTHORIZE EXACTLY ONE SEALED S3 REAL RUN "
    "FOR TIME-SERIES VALUE")


class AuthorizationError(RuntimeError):
    """No valid single-use authorization. Execution must not proceed."""


def _utc_now():
    return datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ")


def exists(path=None):
    return os.path.exists(path or AUTH_PATH)


def load(path=None):
    p = path or AUTH_PATH
    if not os.path.exists(p):
        return None
    return json.load(io.open(p, encoding="utf-8"))


def create(sealed_sha256, seal_revision, owner_decision, path=None):
    """OWNER ACT ONLY. Refuses to overwrite an existing authorization, so a
    consumed one can never be silently reset into a second run."""
    p = path or AUTH_PATH
    if os.path.exists(p):
        raise AuthorizationError(
            "an authorization already exists at %s; it is single-use and is "
            "never overwritten" % p)
    if owner_decision != OWNER_DECISION_PHRASE:
        raise AuthorizationError("the Owner decision phrase does not match")
    auth = {
        "schema": SCHEMA,
        "authorization_id": "VALUE_S3_AUTH_" + uuid.uuid4().hex[:16],
        "issued_utc": _utc_now(),
        "owner_decision": owner_decision,
        "sealed_prereg_sha256": sealed_sha256,
        "seal_revision": seal_revision,
        "single_use": True,
        "status": STATUS_ACTIVE,
        "consumed_utc": None,
        "run_id": None,
    }
    io.open(p, "w", encoding="utf-8").write(
        json.dumps(auth, indent=1, sort_keys=True) + "\n")
    return auth


def validate_active(sealed_sha256, seal_revision, path=None):
    """Return the authorization only if it is genuinely spendable, else raise."""
    p = path or AUTH_PATH
    auth = load(p)
    if auth is None:
        raise AuthorizationError(
            "no S3 execution authorization exists at %s. A seal is not "
            "authorization to execute." % AUTH_RELPATH)
    if auth.get("schema") != SCHEMA:
        raise AuthorizationError("unrecognised authorization schema %r"
                                 % auth.get("schema"))
    if auth.get("status") == STATUS_CONSUMED:
        raise AuthorizationError(
            "authorization %s was already consumed at %s by run %s. It is "
            "single-use; there is no second run."
            % (auth.get("authorization_id"), auth.get("consumed_utc"),
               auth.get("run_id")))
    if auth.get("status") != STATUS_ACTIVE:
        raise AuthorizationError("authorization status is %r, not ACTIVE"
                                 % auth.get("status"))
    if not auth.get("single_use"):
        raise AuthorizationError("a reusable authorization is not permitted")
    if auth.get("sealed_prereg_sha256") != sealed_sha256:
        raise AuthorizationError(
            "the authorization is bound to sealed bytes %s but the contract on "
            "disk is %s. The authorization does not cover this contract."
            % (str(auth.get("sealed_prereg_sha256"))[:16], sealed_sha256[:16]))
    if auth.get("seal_revision") != seal_revision:
        raise AuthorizationError(
            "the authorization names seal revision %s, the contract names %s"
            % (auth.get("seal_revision"), seal_revision))
    return auth


def consume(auth, run_id, path=None):
    """Spend it. Written BEFORE the run is declared finished."""
    p = path or AUTH_PATH
    auth = dict(auth)
    auth["status"] = STATUS_CONSUMED
    auth["consumed_utc"] = _utc_now()
    auth["run_id"] = run_id
    io.open(p, "w", encoding="utf-8").write(
        json.dumps(auth, indent=1, sort_keys=True) + "\n")
    return auth


def status_line(path=None):
    auth = load(path)
    if auth is None:
        return "REAL_EXECUTION_AUTHORIZATION_ACTIVE = NO  (none exists)"
    if auth.get("status") == STATUS_ACTIVE:
        return ("REAL_EXECUTION_AUTHORIZATION_ACTIVE = YES  (%s, issued %s)"
                % (auth.get("authorization_id"), auth.get("issued_utc")))
    return ("REAL_EXECUTION_AUTHORIZATION_ACTIVE = NO  (%s consumed %s by %s)"
            % (auth.get("authorization_id"), auth.get("consumed_utc"),
               auth.get("run_id")))
