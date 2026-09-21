# -*- coding: utf-8 -*-
"""CTA-EDGE-05 / F6 — the S3 primary run driver.

```
THIS DRIVER CONTAINS NO SCIENCE.
```

It performs no arithmetic on a return, defines no estimator, and chooses no
parameter. Every scientific quantity comes from the ACCEPTED S2 modules at
build commit 43f0bb3156673402866f4c1e2d06f25044455d48, whose file hashes are
re-verified here before anything runs. This file only orchestrates: preflight,
sentinel, one call into `f6_pipeline.run_real`, artifact, execution record.

Two modes, and the asymmetry is the point:

```
--preflight   structural checks ONLY. Accesses NO target value, produces NO
              statistic, consumes NOTHING, and is repeatable.
--execute     writes the exposure sentinel, then crosses the irreversible
              boundary. Runs EXACTLY ONCE.
```

`--execute` refuses if a result artifact already exists, so a second primary
execution cannot happen by re-invocation.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import f6_authorization as auth       # noqa: E402
import f6_classify as fcls            # noqa: E402
import f6_contract as K               # noqa: E402
import f6_data as fdata               # noqa: E402
import f6_engine as feng              # noqa: E402
import f6_inference as finf           # noqa: E402
import f6_pipeline as fpipe           # noqa: E402
import f6_report as frep              # noqa: E402

os.chdir(K.REPO)

PKG = "research/extensions/f6"
RUN_ID = "CTA-EDGE-05-F6-S3-PRIMARY-001"
BUILD_COMMIT = "43f0bb3156673402866f4c1e2d06f25044455d48"
BUILD_HASH = "050bb3d73e7c95930d79ebb987797d5a720c5d5081f70b423c3ebeb0a9a05d49"

S3_DIR = "%s/s3" % PKG
SENTINEL = "%s/F6_S3_RUN_SENTINEL.json" % S3_DIR
RESULT = "%s/F6_S3_RESULT.json" % S3_DIR

#: the accepted S2 implementation, pinned by the build manifest
IMPL_PINS = {
    "f6_contract.py": None, "f6_authorization.py": None, "f6_data.py": None,
    "f6_engine.py": None, "f6_inference.py": None, "f6_classify.py": None,
    "f6_report.py": None, "f6_pipeline.py": None,
}

#: P1 / P2 class tokens as the S3 brief names them, mapped from the sealed ones
P1_NAMES = {K.CLASS_POSITIVE: "HARVESTABLE",
            K.CLASS_UNRESOLVED: "UNRESOLVED",
            K.CLASS_ABSENT: "ECONOMICALLY_EXCLUDED"}
P2_NAMES = {K.CLASS_POSITIVE: "SPECIFIC",
            K.CLASS_UNRESOLVED: "UNRESOLVED",
            K.CLASS_ABSENT: "ABSENT"}


def sha(rel):
    with open(K.abspath(rel), "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def git(*args):
    return subprocess.run(["git"] + list(args), cwd=K.REPO,
                          capture_output=True, text=True).stdout.strip()


def log(msg):
    """Operational status only. NEVER a historical target metric."""
    print("[%s] %s" % (dt.datetime.now(dt.timezone.utc).strftime("%H:%M:%S"),
                       msg), flush=True)


# --------------------------------------------------------------------------- #
# PREFLIGHT — touches no target value                                         #
# --------------------------------------------------------------------------- #
def preflight():
    checks, fail = [], []

    def ck(name, ok, detail=""):
        checks.append({"check": name, "ok": bool(ok), "detail": str(detail)})
        if not ok:
            fail.append(name)
        log("  %-46s %s %s" % (name, "PASS" if ok else "FAIL", detail))

    log("PREFLIGHT — structural only, no target value is accessed")

    ck("working tree clean", git("status", "--porcelain") == "")
    ck("build commit is an ancestor of HEAD",
       subprocess.run(["git", "merge-base", "--is-ancestor", BUILD_COMMIT,
                       "HEAD"], cwd=K.REPO).returncode == 0)
    ck("seal commit is an ancestor of the build commit",
       subprocess.run(["git", "merge-base", "--is-ancestor", K.SEAL_COMMIT,
                       BUILD_COMMIT], cwd=K.REPO).returncode == 0)

    seal = fdata.verify_seal_integrity(strict=False)
    ck("seal integrity (%d pins)" % len(seal["pins"]), seal["ok"], seal["failed"])

    bm = json.load(open(K.abspath("%s/F6_S2_BUILD_MANIFEST.json" % PKG),
                        encoding="utf-8"))
    drift = [n for n, h in bm["implementation_files"].items()
             if sha("%s/%s" % (PKG, n)) != h]
    ck("accepted S2 implementation unchanged", not drift, drift)
    ck("build hash pinned in the manifest", bm["build_hash"] == BUILD_HASH)

    st = auth.authorization_status()
    ck("F6 EXECUTION authorization visible in COMMITTED state",
       st["active_execution_authorizations"] == 1, st["authorization_id"])
    try:
        auth.require_run_authorization(auth.REAL, run_id=RUN_ID)
        ck("guard admits this exact run_id", True, RUN_ID)
    except auth.RunNotAuthorized as e:
        ck("guard admits this exact run_id", False, str(e)[:120])
    try:
        auth.require_run_authorization(auth.REAL, run_id="SOME-OTHER-RUN")
        ck("guard REFUSES a different run_id", False)
    except auth.RunNotAuthorized:
        ck("guard REFUSES a different run_id", True)

    fam = fdata.load_event_manifest()
    v = fdata.validate_event_manifest(fam)
    ck("event manifest 462 / 471 / 9", v["n_sessions"] == 462
       and v["labels"] == K.FAMILY_LABELS and v["overlap"] == 9)

    sessions = fdata.panel_sessions()
    grid, boundary = fdata.primary_grid(sessions)
    ck("population %d rows, boundary %s" % (K.P2_ROWS,
                                            K.OPENING_BOUNDARY_SESSION),
       len(grid) == K.P2_ROWS
       and str(boundary.date()) == K.OPENING_BOUNDARY_SESSION)

    sys.path.insert(0, K.REPO)
    import config as cfg
    from src import seasonality as seas
    tom = seas.is_tom(grid, last=cfg.SEAS_TOM_LAST,
                      first=cfg.SEAS_TOM_FIRST).astype(int).values
    frame = feng.build_frame(grid, boundary, set(fam), tom,
                             fdata.auction_sessions(sessions))
    ck("EVENT column sums to 462", int(frame["EVENT"].sum()) == 462)
    X = feng.design_matrix(frame)
    ck("design matrix full rank 9, Friday reference",
       feng.check_design_rank(X) == K.DESIGN_RANK)
    ys = sorted(set(int(y) for y in frame["year"]))
    ck("15 contiguous year blocks 2011..2025", ys == list(K.PRIMARY_YEARS))
    import numpy as np
    bad = [y for y in ys
           if np.linalg.matrix_rank(feng.design_matrix(
               frame[frame["year"] == y]).reindex(
               columns=X.columns, fill_value=0.0).to_numpy(float))
           != K.DESIGN_RANK]
    ck("every individual year full rank", not bad, bad)

    vd, val, rows = fdata.load_cash_series()
    prev = [boundary] + list(grid[:-1])
    carries = [feng.map_cash_rate(p, vd, val, rows)[1] for p in prev]
    ck("DGS3MO maps all %d sessions, no unexplained gap" % K.P2_ROWS,
       len(carries) == K.P2_ROWS and max(carries) <= 4)

    ck("B == 100000", K.BOOTSTRAP_B == 100000)
    ck("seed == 2540719150 and reproduces from its source string",
       K.BOOTSTRAP_SEED_LITERAL == 2540719150
       and int(hashlib.sha256(K.BOOTSTRAP_SEED_SOURCE.encode("ascii"))
               .hexdigest()[:8], 16) == 2540719150)
    ck("quantile implementation is numpy linear",
       K.QUANTILE_METHOD == "linear")
    ck("terminal classifier exhaustive (10 reachable states)",
       len(fcls.reachable_states()) == 10
       and all(fcls.classify(*s)["terminal_classification"]
               not in K.FORBIDDEN_TERMINAL_STATES
               for s in fcls.reachable_states()))
    ck("runtime matches the sealed environment",
       sys.version.split()[0] == K.PINNED_ENV["python"]
       and np.__version__ == K.PINNED_ENV["numpy"])
    ck("no result artifact exists yet", not os.path.isfile(K.abspath(RESULT)))

    ok = not fail
    log("PREFLIGHT %s (%d checks, %d failing)"
        % ("PASS" if ok else "FAIL", len(checks), len(fail)))
    return {"ok": ok, "checks": checks, "failing": fail}


# --------------------------------------------------------------------------- #
# SENTINEL — written immediately BEFORE the first target read                 #
# --------------------------------------------------------------------------- #
def write_sentinel(auth_commit):
    os.makedirs(K.abspath(S3_DIR), exist_ok=True)
    doc = {
        "schema": {"name": "f6-s3-run-sentinel", "version": 1},
        "run_id": RUN_ID,
        "seal_id": K.SEAL_ID,
        "seal_commit": K.SEAL_COMMIT,
        "build_commit": BUILD_COMMIT,
        "build_hash": BUILD_HASH,
        "f6_auth_commit": auth_commit,
        "authorization_id": (auth.active_execution_authorization() or {}
                             ).get("authorization_id"),
        "timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "state": "TARGET_ACCESS_ABOUT_TO_BEGIN",
        "note": "NOT A RESULT. This exists so a process crash cannot make "
                "exposure status ambiguous. Once this file exists and the real "
                "target load has begun, the primary trial is treated as "
                "CONSUMED unless it can be PROVEN the target load never "
                "occurred.",
    }
    p = K.abspath(SENTINEL)
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(doc, fh, indent=1, sort_keys=True)
        fh.write("\n")
    return doc


# --------------------------------------------------------------------------- #
# EXECUTE — exactly once                                                      #
# --------------------------------------------------------------------------- #
def execute(auth_commit):
    if os.path.isfile(K.abspath(RESULT)):
        raise SystemExit("REFUSING: a result artifact already exists at %s. "
                         "One primary execution means one." % RESULT)
    pf = preflight()
    if not pf["ok"]:
        raise SystemExit("PREFLIGHT FAILED before any target access: %s"
                         % pf["failing"])

    log("writing exposure sentinel")
    write_sentinel(auth_commit)
    log("SENTINEL WRITTEN — crossing the irreversible boundary now")
    log("running the sealed primary (B=%d). Operational status only; no "
        "intermediate target metric is printed." % K.BOOTSTRAP_B)

    started = dt.datetime.now(dt.timezone.utc)
    res = fpipe.run_real(run_id=RUN_ID,
                         progress=lambda i: log("  bootstrap %d/%d"
                                                % (i, K.BOOTSTRAP_B))
                         if i % 10000 == 0 else None)
    finished = dt.datetime.now(dt.timezone.utc)
    log("sealed pipeline COMPLETE; serializing result")

    p1, p2, p3, verdict = res["p1"], res["p2"], res["p3"], res["verdict"]
    doc = frep.empty_result(build_hash=BUILD_HASH)
    doc["run_state"] = "COMPLETE"
    doc["data_kind"] = auth.REAL
    doc["run_id"] = RUN_ID
    doc["measurement"]["p1_estimate"] = p1["point"]
    doc["measurement"]["p2_beta_event"] = p2["point"]
    doc["inference"]["p1_lower"] = p1["lower"]
    doc["inference"]["p1_upper"] = p1["upper"]
    doc["inference"]["p2_lower"] = p2["lower"]
    doc["inference"]["p2_upper"] = p2["upper"]
    doc["gate"]["p1_class"] = P1_NAMES[p1["klass"]]
    doc["gate"]["p2_class"] = P2_NAMES[p2["klass"]]
    doc["gate"]["p3_evaluated"] = verdict["p3_evaluated"]
    doc["gate"]["p3_pass"] = (verdict["p3_pass"] if verdict["p3_evaluated"]
                              else "NOT_APPLICABLE_BY_SEAL")
    doc["gate"]["p3_year_results"] = (p3["per_year"] if p3 is not None
                                      else "NOT_APPLICABLE_BY_SEAL")
    doc["verdict"]["terminal_classification"] = \
        verdict["terminal_classification"]
    doc["verdict"]["research_status"] = verdict["research_status"]
    doc["verdict"]["qualifier"] = verdict["qualifier"]
    doc["provenance"]["authorization_id"] = (
        auth.active_execution_authorization() or {}).get("authorization_id")
    doc["provenance"]["f6_auth_commit"] = auth_commit
    doc["provenance"]["build_commit"] = BUILD_COMMIT
    doc["provenance"]["started_utc"] = started.isoformat()
    doc["provenance"]["finished_utc"] = finished.isoformat()
    doc["provenance"]["runtime"] = {"python": sys.version.split()[0],
                                    "numpy": __import__("numpy").__version__,
                                    "pandas": __import__("pandas").__version__}
    doc["provenance"]["f6_primary_trial_consumed"] = True
    doc["provenance"]["primary_execution_count"] = 1
    doc["provenance"]["bootstrap_execution_count"] = 1
    doc["provenance"]["sealed_class_tokens"] = {"p1": p1["klass"],
                                                "p2": p2["klass"]}

    v = frep.validate_result(doc)
    if not v["ok"]:
        raise SystemExit("result artifact failed structural validation: %s"
                         % v["errors"])
    frep.write_result(doc, K.abspath(RESULT))
    log("result written: %s" % RESULT)

    sent = json.load(open(K.abspath(SENTINEL), encoding="utf-8"))
    sent["state"] = "TARGET_ACCESS_COMPLETED"
    sent["f6_outcome_exposure_occurred"] = True
    sent["f6_primary_trial_consumed"] = True
    sent["result_artifact"] = RESULT
    sent["completed_utc"] = finished.isoformat()
    with open(K.abspath(SENTINEL), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(sent, fh, indent=1, sort_keys=True)
        fh.write("\n")
    log("sentinel closed: TARGET_ACCESS_COMPLETED")
    return doc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preflight", action="store_true")
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--auth-commit", default="")
    a = ap.parse_args()
    if a.preflight == a.execute:
        raise SystemExit("choose exactly one of --preflight / --execute")
    if a.preflight:
        return 0 if preflight()["ok"] else 1
    if not a.auth_commit:
        raise SystemExit("--execute requires --auth-commit")
    execute(a.auth_commit)
    log("DONE. Interpretation belongs to S4, not to this driver.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
