# -*- coding: utf-8 -*-
"""TSMOM-VRP-01 - the S2 acceptance runner.

Runs every mechanical gate S2 must satisfy and writes the tracked acceptance log
`research/extensions/vrp/s2/VRP_S2_ACCEPTANCE_LOG.json`, which
`vrp_reveal.acceptance_log_all_pass` reads from COMMITTED state before any real run may
ever be generated (acceptance item 21).

    python research/extensions/vrp/vrp_s2_accept.py

Exit 0 = every required item PASS. No real Stage-A or Stage-B outcome is produced.
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)

import vrp_ca_audit as vaudit        # noqa: E402
import vrp_validators as vval        # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

S2_DIR = os.path.join(HERE, "s2")
LOG_PATH = os.path.join(S2_DIR, "VRP_S2_ACCEPTANCE_LOG.json")
S2A_RESULT = os.path.join(REPO, "data", "vix", "manifests", "vrp_s2a_result.json")

PYTHON = sys.executable

# item -> (title, level, the test-name prefix that evidences it)
ITEMS = [
    (1, "Data hashes", 1, "test_i01_"),
    (2, "Specification-history tests", 1, "test_i02_"),
    (3, "Contract identity", 1, "test_i03_"),
    (4, "Roll-weight determinism", 1, "test_i04_"),
    (5, "Missing-data branch tests", 1, "test_i05_"),
    (6, "Cost rule tests", 1, "test_i06_"),
    (7, "2007 rescaling tests", 1, "test_i07_"),
    (8, "Tick-history tests", 1, "test_i08_"),
    (9, "Stress identity", 1, "test_i09_"),
    (10, "Granularity gate", 2, "test_i10_"),
    (11, "Stressed-margin gate", 2, "test_i11_"),
    (12, "Stage-A accounting oracle", 1, "test_i12_"),
    (13, "Self-financing Stage-B ledger oracle", 1, "test_i13_"),
    (14, "Forced-liquidation oracle", 1, "test_i14_"),
    (15, "Book-exhaustion oracle", 1, "test_i15_"),
    (16, "Bootstrap reproducibility", 1, "test_i16_"),
    (17, "Every result state synthetically reachable", 1, "test_i17_"),
    (18, "Sabotage tests", 1, "test_sab_"),
    (19, "C-A access audit", 1, "test_i19_"),
    (20, "Frozen-constant transcription", 1, "test_i20_"),
    (21, "No generated outcome before acceptance", 1, "test_i21_"),
]

SECRET_PATTERNS = [
    (r"(?i)\b(api[_-]?key|secret|passwd|password|token|bearer)\b\s*[:=]\s*['\"][^'\"]{8,}",
     "assigned credential literal"),
    (r"(?i)[?&](api[_-]?key|token|access[_-]?key|secret)=", "credential in a URL"),
    (r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----", "private key block"),
    (r"\bAKIA[0-9A-Z]{16}\b", "AWS access key id"),
    (r"\bgh[pousr]_[A-Za-z0-9]{16,}", "GitHub token"),
]


def run(cmd, cwd=REPO):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def section(title):
    print("\n" + title)
    print("-" * 78)


def secret_scan():
    """Scan every file this build created or touched for credential-like content."""
    targets = []
    for name in sorted(os.listdir(HERE)):
        if name.endswith((".py", ".md", ".json")):
            targets.append(os.path.join(HERE, name))
    if os.path.isdir(S2_DIR):
        targets += [os.path.join(S2_DIR, f) for f in sorted(os.listdir(S2_DIR))]
    man_dir = os.path.join(REPO, "data", "vix", "manifests")
    if os.path.isdir(man_dir):
        targets += [os.path.join(man_dir, f) for f in sorted(os.listdir(man_dir))]
    findings = []
    for path in targets:
        try:
            text = open(path, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        for pattern, label in SECRET_PATTERNS:
            for m in re.finditer(pattern, text):
                findings.append({"file": os.path.relpath(path, REPO).replace("\\", "/"),
                                 "kind": label, "line": text[:m.start()].count("\n") + 1})
    return findings, len(targets)


def _accepted_log_is_frozen():
    """Once a single-use Owner EXECUTION grant is committed, S2 acceptance is CLOSED and
    its log is a historical record that must not be rewritten.

    Item 21's own evidence asserts that no execution authorisation exists, so re-running
    this runner after a grant is committed necessarily reports item 21 as FAIL. Allowing
    that to overwrite the accepted log would destroy the record of S2 acceptance and
    permanently block the very run the grant authorises - a circularity, not a finding.
    """
    sys.path.insert(0, HERE)
    import vrp_reveal as _vreveal
    return _vreveal.active_execution_authorization("EXECUTION") is not None


def main() -> int:
    os.makedirs(S2_DIR, exist_ok=True)
    print("TSMOM-VRP-01 - S2 ACCEPTANCE RUNNER")
    print("=" * 78)
    if _accepted_log_is_frozen():
        print("")
        print("REFUSED: a single-use Owner EXECUTION grant is committed, so S2")
        print("acceptance is CLOSED and its log is frozen as a historical record.")
        print("Re-running would report item 21 FAIL purely because the grant exists,")
        print("overwrite the accepted all-PASS record, and block the authorised run.")
        print("Use research/extensions/vrp/s3/vrp_s3_stage_a.py preflight instead: it")
        print("re-runs every check and accounts for the enumerated S3 state transition.")
        return 0

    # --------------------------------------------------------------- #
    section("A. S2A data gate")
    s2a = run([PYTHON, os.path.join("research", "extensions", "vrp", "vrp_data_validate.py")])
    s2a_pass = s2a.returncode == 0
    print("  S2A_DATA_ACQUISITION_STATUS = %s" % ("PASS" if s2a_pass else "FAIL"))
    s2a_detail = {}
    if os.path.isfile(S2A_RESULT):
        with open(S2A_RESULT, encoding="utf-8") as fh:
            s2a_detail = json.load(fh)

    # --------------------------------------------------------------- #
    section("B. acceptance suite")
    pytest_out = run([PYTHON, "-m", "pytest",
                      os.path.join("research", "extensions", "vrp", "vrp_tests.py"),
                      "-v", "--no-header", "--tb=line", "-p", "no:cacheprovider"])
    lines = pytest_out.stdout.splitlines()
    passed = {}
    failed = {}
    for line in lines:
        m = re.search(r"vrp_tests\.py::(\S+)\s+(PASSED|FAILED|ERROR|XFAIL|XPASS)", line)
        if m:
            (passed if m.group(2) in ("PASSED", "XFAIL") else failed)[m.group(1)] = True
    if not passed and not failed:
        print("  WARNING: no per-test lines parsed; pytest exit code %d"
              % pytest_out.returncode)
        print("\n".join(lines[-15:]))
    total = len(passed) + len(failed)
    print("  tests: %d passed, %d failed (total %d)" % (len(passed), len(failed), total))
    if failed:
        for name in sorted(failed):
            print("    FAILED %s" % name)

    def item_result(prefix):
        hits = [n for n in list(passed) + list(failed) if n.startswith(prefix)]
        if not hits:
            return "FAIL", 0, 0
        bad = [n for n in hits if n in failed]
        return ("PASS" if not bad else "FAIL"), len(hits), len(bad)

    # --------------------------------------------------------------- #
    section("C. standalone validators")
    validator_rows = vval.run_all()
    for r in validator_rows:
        print("  %-56s %s" % (r["check"], "PASS" if r["pass"] else "FAIL"))
    validators_pass = all(r["pass"] for r in validator_rows)

    # --------------------------------------------------------------- #
    section("D. C-A access audit")
    audit = vaudit.audit()
    with open(vaudit.AUDIT_LOG, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(audit, fh, indent=2, sort_keys=True)
    print("  C-A ACCESS AUDIT: %s (%d files)"
          % ("PASS" if audit["pass"] else "FAIL", len(audit["files_audited"])))

    # --------------------------------------------------------------- #
    section("E. secret scan")
    findings, scanned = secret_scan()
    print("  scanned %d files, %d finding(s)" % (scanned, len(findings)))
    for f in findings:
        print("    %s:%s %s" % (f["file"], f["line"], f["kind"]))
    secrets_pass = not findings

    # --------------------------------------------------------------- #
    section("F. acceptance-contract items")
    items = []
    for number, title, level, prefix in ITEMS:
        result, n_tests, n_bad = item_result(prefix)
        if number == 1 and not s2a_pass:
            result = "FAIL"
        if number == 19 and not audit["pass"]:
            result = "FAIL"
        if number == 20 and not validators_pass:
            result = "FAIL"
        items.append({"item": number, "title": title, "level": level,
                      "result": result, "tests": n_tests, "failing_tests": n_bad,
                      "evidence_prefix": prefix})
        print("  %2d  %-46s %-6s  (%d test%s)"
              % (number, title, result, n_tests, "" if n_tests == 1 else "s"))

    all_pass = (all(i["result"] == "PASS" for i in items)
                and s2a_pass and validators_pass and audit["pass"] and secrets_pass)

    head = run(["git", "rev-parse", "HEAD"]).stdout.strip() or None
    log = {
        "lineage": "TSMOM-VRP-01",
        "contract_id": "TSMOM-VRP-01-PREREG-01",
        "s1_seal_commit": "16d84545ba1385a482dbac7e776b31275f6fa5f7",
        "generated_utc": _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "commit": None,   # set by the commit that contains this log; see the report
        "recorded_at_head_before_commit": head,
        "items": items,
        "s2a_status": "PASS" if s2a_pass else "FAIL",
        "s2a_counts": s2a_detail.get("counts", {}),
        "acceptance_suite": {"passed": len(passed), "failed": len(failed), "total": total},
        "validators": validator_rows,
        "ca_access_audit": {k: audit[k] for k in sorted(audit) if k != "files_audited"},
        "secret_scan": {"files_scanned": scanned, "findings": findings,
                        "result": "PASS" if secrets_pass else "FAIL"},
        "REAL_STAGE_A_COMPUTED": "NO",
        "REAL_STAGE_B_COMPUTED": "NO",
        "REAL_PERFORMANCE_REVEALED": "NO",
        "S3_AUTHORIZED": "NO",
        "REAL_RUN_AUTHORIZED": "NO",
        "overall": "PASS" if all_pass else "FAIL",
    }
    with open(LOG_PATH, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(log, fh, indent=2, sort_keys=True)

    section("S2 ACCEPTANCE RESULT")
    print("  IMPLEMENTATION_ACCEPTANCE_CONTRACT = %s" % log["overall"])
    print("  log: %s" % os.path.relpath(LOG_PATH, REPO).replace("\\", "/"))
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
