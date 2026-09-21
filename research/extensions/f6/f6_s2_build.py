# -*- coding: utf-8 -*-
"""CTA-EDGE-05 / F6 — S2 build validation and manifest emission.

Runs the static checks, the full synthetic suite and the guard probe, then
writes `F6_S2_BUILD_MANIFEST.json` and `F6_S2_BUILD_VALIDATION.json`.

```
IT NEVER RUNS THE HISTORICAL TARGET. It asserts the opposite: that the
production path REFUSES, here and now, with no F6 grant in committed state.
```
"""

from __future__ import annotations

import ast
import hashlib
import json
import os
import py_compile
import subprocess
import sys
import datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import f6_authorization as auth       # noqa: E402
import f6_contract as K               # noqa: E402
import f6_data as fdata               # noqa: E402
import f6_pipeline as fpipe           # noqa: E402
import f6_report as frep              # noqa: E402

os.chdir(K.REPO)

IMPL = ["f6_contract.py", "f6_authorization.py", "f6_data.py", "f6_engine.py",
        "f6_inference.py", "f6_classify.py", "f6_report.py", "f6_pipeline.py"]
TESTS = ["f6_fixtures.py", "f6_oracle.py", "f6_tests.py"]
TOOLS = ["f6_s2_build.py"]
PKG = "research/extensions/f6"


def sha(rel):
    with open(K.abspath(rel), "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def build_hash(files):
    """A deterministic identity for THIS build: hash of the sorted file hashes."""
    h = hashlib.sha256()
    for rel in sorted(files):
        h.update(rel.encode("utf-8"))
        h.update(b"\0")
        h.update(sha(rel).encode("ascii"))
        h.update(b"\n")
    return h.hexdigest()


def static_checks():
    """Byte-compile and AST-parse every module.

    The compiled output goes to a scratch file, not `os.devnull`: on Windows
    that is `nul`, and py_compile refuses to write a non-regular file.
    """
    import tempfile
    out = {"compiled": [], "failed": []}
    with tempfile.TemporaryDirectory() as tmp:
        for name in IMPL + TESTS + TOOLS:
            rel = "%s/%s" % (PKG, name)
            try:
                py_compile.compile(K.abspath(rel), doraise=True,
                                   cfile=os.path.join(tmp, name + "c"))
                ast.parse(open(K.abspath(rel), encoding="utf-8").read())
                out["compiled"].append(name)
            except Exception as e:                   # noqa: BLE001
                out["failed"].append({"file": name, "error": repr(e)})
    out["ok"] = not out["failed"]
    return out


def guard_probe():
    """Prove the production path refuses, without going near the panel."""
    st = auth.authorization_status()
    refused, reason = False, None
    try:
        fpipe.run_real(run_id="F6-S2-GUARD-PROBE")
    except auth.RunNotAuthorized as e:
        refused, reason = True, str(e)
    except Exception as e:                           # noqa: BLE001
        reason = "WRONG EXCEPTION: %r" % (e,)
    return {"real_run_refused": refused,
            "refusal_reason": reason,
            "active_execution_authorizations":
                st["active_execution_authorizations"],
            "ledger": st["ledger"], "auth_id_prefix": st["auth_id_prefix"],
            "synthetic_allowed": auth.require_run_authorization(auth.SYNTHETIC)
                is None,
            "ok": bool(refused and st["active_execution_authorizations"] == 0)}


def run_tests():
    p = subprocess.run([sys.executable, "-m", "pytest",
                        K.abspath("%s/f6_tests.py" % PKG),
                        "-q", "--no-header", "-p", "no:warnings"],
                       capture_output=True, text=True, cwd=K.REPO)
    tail = [l for l in p.stdout.splitlines() if l.strip()][-1:]
    line = tail[0] if tail else ""
    import re
    passed = int((re.search(r"(\d+) passed", line) or [0, 0])[1] or 0) \
        if re.search(r"(\d+) passed", line) else 0
    failed = int(re.search(r"(\d+) failed", line).group(1)) \
        if re.search(r"(\d+) failed", line) else 0
    return {"returncode": p.returncode, "summary": line,
            "passed": passed, "failed": failed,
            "ok": p.returncode == 0 and failed == 0 and passed > 0}


def main():
    seal = fdata.verify_seal_integrity(strict=False)
    static = static_checks()
    guard = guard_probe()
    tests = run_tests()
    schema_ok = frep.validate_result(frep.empty_result())["ok"]
    files = ["%s/%s" % (PKG, n) for n in IMPL + TESTS + TOOLS]
    bh = build_hash(files)

    ok = all([seal["ok"], static["ok"], guard["ok"], tests["ok"], schema_ok])

    validation = {
        "schema": {"name": "f6-s2-build-validation", "version": 1},
        "generated": dt.date.today().isoformat(),
        "build_validation": "PASS" if ok else "FAIL",
        "seal_integrity": seal,
        "static_checks": static,
        "historical_run_guard": guard,
        "tests": tests,
        "result_schema_valid": schema_ok,
        "build_hash": bh,
        "HISTORICAL_OUTCOME_RUN": "NOT_AUTHORIZED",
        "S3_AUTHORIZATION_REQUIRED": True,
        "firewall": {
            "real_spy_price_value_accessed": False,
            "real_f6_return_computed": False,
            "real_beta_event_computed": False,
            "real_bootstrap_executed": False,
            "real_loyo_performance_computed": False,
            "f6_primary_trial_consumed": False,
            "performance_exposure_added": False,
            "note": "Every numeric result produced by this build came from "
                    "SYNTHETIC fixtures. The only real-price reader is "
                    "f6_data.load_price_values, whose first statement is the "
                    "run guard, and the guard probe above shows it refusing.",
        },
    }
    vpath = K.abspath("%s/F6_S2_BUILD_VALIDATION.json" % PKG)
    with open(vpath, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(validation, fh, indent=1, sort_keys=True)
        fh.write("\n")

    manifest = {
        "schema": {"name": "f6-s2-build-manifest", "version": 1},
        "lineage": K.LINEAGE,
        "generated": dt.date.today().isoformat(),
        "stage": "S2_BUILD",
        "HISTORICAL_OUTCOME_RUN": "NOT_AUTHORIZED",
        "S3_AUTHORIZATION_REQUIRED": True,
        "S3_RUN_AUTHORIZED": False,
        "RETURN_REVEAL_AUTHORIZED": False,
        "F6_PRIMARY_TRIAL_CONSUMED": False,
        "seal": {
            "seal_id": K.SEAL_ID, "seal_date": K.SEAL_DATE,
            "seal_commit": K.SEAL_COMMIT,
            "sealed_preregistration_sha256": K.SEALED_PREREG_SHA256,
            "sealed_manifest_sha256": K.SEALED_MANIFEST_SHA256,
            "seal_record_sha256": K.SEAL_RECORD_SHA256,
            "event_manifest_sha256": K.EVENT_MANIFEST_SHA256,
            "integrity_verified": seal["ok"],
        },
        "build_hash": bh,
        "implementation_files": {n: sha("%s/%s" % (PKG, n)) for n in IMPL},
        "test_files": {n: sha("%s/%s" % (PKG, n)) for n in TESTS},
        "tool_files": {n: sha("%s/%s" % (PKG, n)) for n in TOOLS},
        "runtime": {
            "python": sys.version.split()[0],
            "numpy": __import__("numpy").__version__,
            "pandas": __import__("pandas").__version__,
            "pinned_by_seal": dict(K.PINNED_ENV),
            "note": "If the execution environment differs at S3, the "
                    "implementation must still reproduce the sealed quantile "
                    "semantics. A changed default is not acceptable.",
        },
        "run_guard": {
            "mechanism": "the repository's existing append-only Owner ledger "
                         "ops/EXECUTION_AUTHORIZATIONS.md, read from COMMITTED "
                         "git state; F6-AUTH scope",
            "fail_closed": True,
            "grant_requires_commit": True,
            "blocking_requires_nothing": True,
            "active_grants_now": guard["active_execution_authorizations"],
            "real_run_refused_now": guard["real_run_refused"],
            "no_grant_was_created_by_this_build": True,
        },
        "sealed_settings_reproduced": {
            "final_primary_event_count": K.FINAL_PRIMARY_EVENT_COUNT,
            "family_labels": dict(K.FAMILY_LABELS),
            "p2_rows": K.P2_ROWS,
            "weekday_reference": K.WEEKDAY_REFERENCE,
            "weekday_indicators": list(K.WEEKDAY_INDICATORS),
            "design_columns": list(K.DESIGN_COLUMNS),
            "round_trip_cost": K.ROUND_TRIP_COST,
            "cash_daycount": K.CASH_DAYCOUNT,
            "cash_daycount_attribution": K.CASH_DAYCOUNT_ATTRIBUTION,
            "year_blocks": K.YEAR_BLOCK_COUNT,
            "bootstrap_B": K.BOOTSTRAP_B,
            "bootstrap_seed_literal": K.BOOTSTRAP_SEED_LITERAL,
            "bootstrap_seed_source": K.BOOTSTRAP_SEED_SOURCE,
            "quantile_implementation": K.QUANTILE_IMPLEMENTATION,
            "opening_boundary_session": K.OPENING_BOUNDARY_SESSION,
            "sample_reuse_class": K.SAMPLE_REUSE_CLASS,
            "evidence_ceiling": K.EVIDENCE_CEILING,
            "independent_confirmation": K.INDEPENDENT_CONFIRMATION,
        },
        "validation_artifact": "F6_S2_BUILD_VALIDATION.json",
        "result_schema": "f6_report.empty_result() — six layers, every outcome "
                         "slot NOT_RUN, zero placeholders refused",
    }
    mpath = K.abspath("%s/F6_S2_BUILD_MANIFEST.json" % PKG)
    with open(mpath, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(manifest, fh, indent=1, sort_keys=True)
        fh.write("\n")

    print("seal integrity  : %s" % ("PASS" if seal["ok"] else "FAIL"))
    print("static checks   : %s (%d files)" % ("PASS" if static["ok"] else
                                               "FAIL", len(static["compiled"])))
    print("run guard       : %s (%d active grants, real run refused=%s)"
          % ("PASS" if guard["ok"] else "FAIL",
             guard["active_execution_authorizations"], guard["real_run_refused"]))
    print("tests           : %s  %s" % ("PASS" if tests["ok"] else "FAIL",
                                        tests["summary"]))
    print("result schema   : %s" % ("PASS" if schema_ok else "FAIL"))
    print("BUILD_VALIDATION= %s" % ("PASS" if ok else "FAIL"))
    print("build_hash      = %s" % bh)
    print("wrote %s" % mpath)
    print("wrote %s" % vpath)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
