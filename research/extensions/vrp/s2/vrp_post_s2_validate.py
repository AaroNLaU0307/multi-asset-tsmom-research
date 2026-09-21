# -*- coding: utf-8 -*-
"""TSMOM-VRP-01 - POST-S2 STATE-TRANSITION VALIDATOR.

The hash-pinned S1 validator `research/extensions/vrp/vrp_prereg_validate.py` is
DELIBERATELY NOT MODIFIED and DELIBERATELY STILL EXITS 1 after authorised S2 acquisition.
Exactly one of its checks is a SEAL-TIME STATE assertion:

    no data/vix directory exists yet

which was intentionally TRUE at S1 (nothing had been acquired) and intentionally becomes
FALSE once Owner-authorised S2 acquisition occurs - because section L of the sealed
contract itself mandates that raw files land under `data/vix/raw/`. Its exit code is NOT
relabelled as PASS anywhere.

This validator checks the STATE TRANSITION instead: that the original validator's
contract/content checks ALL still pass, that the ONLY failure is that one known seal-time
acquisition-state assertion, and that the transition happened for the authorised reason
and left every other invariant intact.

Run:  python research/extensions/vrp/s2/vrp_post_s2_validate.py
Exit: 0 = POST_S2_STATE_TRANSITION_VALIDATOR PASS, 1 = FAIL.

It weakens nothing: it runs the original validator as a subprocess, parses its own output,
and requires 113/113 contract-content checks PASS.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(PKG, "..", "..", ".."))
sys.path.insert(0, PKG)

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ORIGINAL_VALIDATOR = os.path.join("research", "extensions", "vrp", "vrp_prereg_validate.py")
RESULT_JSON = os.path.join(HERE, "VRP_POST_S2_STATE_VALIDATION.json")

# The ONE check that authorised S2 acquisition is expected to flip, verbatim from the
# sealed validator's own label.
EXPECTED_STATE_FAILURE = "no data/vix directory exists yet"
EXPECTED_CONTENT_CHECKS = 113

SEALED_S1_ARTIFACTS = {
    "VRP_PREREGISTRATION.md":
        "dd5822440bedbe58f49940651bddf656f4dbb593295b59c4eff2b45b89cf53e6",
    "VRP_IMPLEMENTATION_ACCEPTANCE_CONTRACT.md":
        "4fad50df6ef0c031cdb67e8100034718f49382ce0dd4e6df8e93f29afecb7dbb",
    "VRP_EXPOSURE_DISCLOSURE.md":
        "afae108d6e894c3822c783d45d77b85e09838578e5e7bf8040ad6dac6a3788c1",
    "vrp_prereg_validate.py":
        "4684ecb2c9a633a9d17413a067aa0987a110718518954579a87ffd6122667876",
}

S1_SEAL_COMMIT = "16d84545ba1385a482dbac7e776b31275f6fa5f7"
CANONICAL_BASE_COMMIT = "d232d3361b23a9f64182c2ec8881284f0fc3b36e"

_ok = True
_rows = []


def ck(label, cond, detail=""):
    global _ok
    if not cond:
        _ok = False
    _rows.append({"check": label, "pass": bool(cond), "detail": str(detail)})
    print("  %-64s %s   %s" % (label, "PASS" if cond else "FAIL", detail))


def section(title):
    print("\n" + title)
    print("-" * 78)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git(*args):
    out = subprocess.run(["git"] + list(args), cwd=REPO, capture_output=True,
                         text=True, encoding="utf-8", errors="replace")
    return out.returncode, out.stdout.strip()


def main() -> int:
    print("TSMOM-VRP-01 - POST-S2 STATE-TRANSITION VALIDATOR")
    print("=" * 78)
    print("The original S1 validator is NOT modified and its exit code is NOT relabelled.")

    # --------------------------------------------------------------- A, B, C --
    section("A-C. ORIGINAL S1 VALIDATOR - content checks intact, one known state failure")
    proc = subprocess.run([sys.executable, ORIGINAL_VALIDATOR], cwd=REPO,
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace")
    out = proc.stdout
    passes = re.findall(r"^\s{2}(.+?)\s{2,}PASS(?:\s|$)", out, re.M)
    fails = re.findall(r"^\s{2}(.+?)\s{2,}FAIL(?:\s|$)", out, re.M)
    passes = [p.strip() for p in passes]
    fails = [f.strip() for f in fails]

    ck("original validator ran", proc.returncode in (0, 1), "exit %d" % proc.returncode)
    ck("original validator content checks PASS (expected %d)" % EXPECTED_CONTENT_CHECKS,
       len(passes) == EXPECTED_CONTENT_CHECKS, "%d PASS" % len(passes))
    ck("exactly ONE original check fails", len(fails) == 1, "%d FAIL: %s"
       % (len(fails), "; ".join(fails)))
    ck("the ONLY failing check is the known seal-time acquisition-state assertion",
       fails == [EXPECTED_STATE_FAILURE], "%r" % (fails[0] if fails else None))
    ck("original validator exit code is 1, reported as-is and NOT relabelled",
       proc.returncode == 1, "exit %d (expected 1)" % proc.returncode)

    # ------------------------------------------------------------------- D --
    section("D. data/vix exists ONLY because authorised S2 acquisition occurred")
    vix_dir = os.path.join(REPO, "data", "vix")
    manifest_json = os.path.join(vix_dir, "manifests", "vrp_raw_manifest.json")
    tracked_manifest = os.path.join(PKG, "VRP_DATA_MANIFEST.md")
    ck("data/vix exists", os.path.isdir(vix_dir))
    ck("data/vix contains ONLY raw/ and manifests/",
       sorted(os.listdir(vix_dir)) == ["manifests", "raw"],
       ",".join(sorted(os.listdir(vix_dir))) if os.path.isdir(vix_dir) else "")
    ck("the acquisition manifest exists and is the reason data/vix exists",
       os.path.isfile(manifest_json))
    ck("a TRACKED provenance manifest pins the acquisition", os.path.isfile(tracked_manifest))
    manifest = {}
    if os.path.isfile(manifest_json):
        with open(manifest_json, encoding="utf-8") as fh:
            manifest = json.load(fh)
    rows = manifest.get("contract_files", [])
    ck("every acquired file is Cboe PRIMARY authority",
       bool(rows) and {str(r.get("source_authority_level")) for r in rows} == {"1 / PRIMARY"},
       "%d raw contract files" % len(rows))
    ck("the acquisition binds to the accepted S1 seal",
       manifest.get("s1_seal_commit") == S1_SEAL_COMMIT, str(manifest.get("s1_seal_commit")))
    mismatched = [r["file_name"] for r in rows
                  if not os.path.exists(os.path.join(REPO, str(r["relative_path"]).replace("/", os.sep)))
                  or sha256_file(os.path.join(REPO, str(r["relative_path"]).replace("/", os.sep))) != r["sha256"]]
    ck("every pinned raw file is present and matches its SHA256", not mismatched,
       "%d mismatched" % len(mismatched))

    # ------------------------------------------------------------------- E --
    section("E. raw data remain git-ignored and uncommitted")
    rc, ignored = git("check-ignore", "data/vix/raw", "data/vix/manifests")
    ck("data/vix/raw and data/vix/manifests are git-ignored", rc == 0,
       ignored.replace("\n", " "))
    rc, tracked = git("ls-files", "data/vix")
    ck("no file under data/vix is tracked by git", tracked == "",
       "%d tracked" % (len(tracked.splitlines()) if tracked else 0))
    # The precise invariant: S2 committed NO data file. `data/` as a whole is not empty of
    # tracked files - `data/xsmom_universes_prices.csv` has been tracked since the XSMOM
    # fold-in (commit f03b5a1), long before this lineage and present at the S1 seal. The
    # honest assertion is that the tracked set under data/ is UNCHANGED since the seal.
    rc, tracked_now = git("ls-files", "data")
    rc2, tracked_at_seal = git("ls-tree", "-r", "--name-only", S1_SEAL_COMMIT, "--", "data")
    now = sorted(tracked_now.splitlines()) if tracked_now else []
    at_seal = sorted(tracked_at_seal.splitlines()) if tracked_at_seal else []
    ck("the tracked file set under data/ is unchanged since the S1 seal",
       now == at_seal, "added since seal: %s" % (sorted(set(now) - set(at_seal)) or "none"))
    ck("no data file was committed by S2", not (set(now) - set(at_seal)),
       "%d tracked under data/, all pre-existing" % len(now))

    # ------------------------------------------------------------------- F --
    section("F. S1 authoritative artifacts remain byte-identical")
    bad = []
    for name, expected in SEALED_S1_ARTIFACTS.items():
        path = os.path.join(PKG, name)
        if not os.path.isfile(path) or sha256_file(path) != expected:
            bad.append(name)
    ck("all four sealed S1 artifacts are byte-identical to the seal", not bad,
       "unchanged: %d" % len(SEALED_S1_ARTIFACTS) if not bad else ",".join(bad))
    rc, diff = git("diff", "--name-only", S1_SEAL_COMMIT, "HEAD", "--",
                   "research/extensions/vrp/VRP_PREREGISTRATION.md",
                   "research/extensions/vrp/VRP_IMPLEMENTATION_ACCEPTANCE_CONTRACT.md",
                   "research/extensions/vrp/VRP_EXPOSURE_DISCLOSURE.md",
                   "research/extensions/vrp/VRP_SEAL_MANIFEST.md",
                   "research/extensions/vrp/vrp_prereg_validate.py")
    ck("git confirms no sealed artifact changed since the seal commit", diff == "",
       diff.replace("\n", " ") or "0 changed")

    # ------------------------------------------------------------------- G --
    section("G. the S2 branch descends from the accepted S1 seal")
    rc_seal, _ = git("merge-base", "--is-ancestor", S1_SEAL_COMMIT, "HEAD")
    ck("the accepted S1 seal is an ancestor of HEAD", rc_seal == 0, S1_SEAL_COMMIT[:12])
    rc_base, _ = git("merge-base", "--is-ancestor", CANONICAL_BASE_COMMIT, "HEAD")
    ck("the canonical base (main) is an ancestor of HEAD", rc_base == 0,
       CANONICAL_BASE_COMMIT[:12])
    _, main_head = git("rev-parse", "main")
    ck("main is unmoved at the canonical base", main_head == CANONICAL_BASE_COMMIT,
       main_head[:12])
    for cd in ("3369ce6", "fa52efd", "85c831c", "6234adf", "083268d"):
        rc_cd, _ = git("merge-base", "--is-ancestor", cd, "HEAD")
        if rc_cd == 0:
            ck("C-D commit %s is NOT an ancestor" % cd, False, "IS an ancestor")
    ck("no C-D-only commit is an ancestor of HEAD", True, "5 checked")
    rc, ca_diff = git("diff", "--name-only", "main", "HEAD", "--", "research/extensions/ca/")
    ck("research/extensions/ca/ is byte-identical to main", ca_diff == "",
       "%d changed" % (len(ca_diff.splitlines()) if ca_diff else 0))

    # ------------------------------------------------------------------- H --
    section("H. no real Stage-A or Stage-B result exists")
    log_path = os.path.join(HERE, "VRP_S2_ACCEPTANCE_LOG.json")
    log = {}
    if os.path.isfile(log_path):
        with open(log_path, encoding="utf-8") as fh:
            log = json.load(fh)
    ck("the acceptance log records REAL_STAGE_A_COMPUTED = NO",
       log.get("REAL_STAGE_A_COMPUTED") == "NO", str(log.get("REAL_STAGE_A_COMPUTED")))
    ck("the acceptance log records REAL_STAGE_B_COMPUTED = NO",
       log.get("REAL_STAGE_B_COMPUTED") == "NO", str(log.get("REAL_STAGE_B_COMPUTED")))
    ck("the acceptance log records REAL_PERFORMANCE_REVEALED = NO",
       log.get("REAL_PERFORMANCE_REVEALED") == "NO",
       str(log.get("REAL_PERFORMANCE_REVEALED")))
    ck("the acceptance log records S3_AUTHORIZED = NO and REAL_RUN_AUTHORIZED = NO",
       log.get("S3_AUTHORIZED") == "NO" and log.get("REAL_RUN_AUTHORIZED") == "NO")

    import vrp_reveal as vreveal
    ck("no single-use Owner EXECUTION authorisation is committed",
       vreveal.active_execution_authorization("EXECUTION") is None)
    ck("no single-use Owner REVEAL authorisation is committed",
       vreveal.active_execution_authorization("REVEAL") is None)
    refused = False
    try:
        vreveal.require_run_authorization(vreveal.REAL)
    except vreveal.RunNotAuthorized:
        refused = True
    ck("the governed-run entry gate REFUSES a real run", refused)

    # ------------------------------------------------------------------- I --
    section("I. no protected VRP outcome store or result exists")
    store = vreveal.PROTECTED_STORE
    ck("the VRP protected store is empty or absent",
       (not os.path.isdir(store)) or not os.listdir(store),
       os.path.relpath(store, REPO).replace("\\", "/"))
    strays = []
    for root, _dirs, files in os.walk(PKG):
        for f in files:
            if re.search(r"(?i)(sharpe|cagr|drawdown|returns?|pnl|performance)\."
                         r"(json|csv|parquet)$", f):
                strays.append(os.path.join(root, f))
    ck("no outcome-shaped result file exists anywhere in the package", not strays,
       ",".join(strays[:3]))

    # ------------------------------------------------------------------- J --
    section("J. C-A protected storage was not accessed")
    import vrp_ca_audit as vaudit
    audit = vaudit.audit()
    ck("static C-A access audit passes", audit["pass"] is True,
       "%d files audited, %d findings" % (len(audit["files_audited"]),
                                          len(audit["findings"])))
    for key in ("C_A_PROSPECTIVE_OUTCOME_ACCESSED", "C_A_PROTECTED_STORE_ACCESSED",
                "C_A_POSITION_LAYER_ACCESSED", "C_A_RETURN_LAYER_ACCESSED",
                "CANONICAL_FORWARD_RETURN_COMPUTED"):
        ck("audit records %s = NO" % key, audit.get(key) == "NO", str(audit.get(key)))
    ck("the VRP protected store is the VRP family's own, never the C-A store",
       audit.get("vrp_protected_store_is_its_own") is True,
       str(audit.get("vrp_protected_store")))

    # ------------------------------------------------------------------ K --
    section("K. the mechanical erratum is present and the sign convention holds")
    erratum = os.path.join(PKG, "VRP_S1_MECHANICAL_ERRATUM_01.md")
    ck("VRP_S1_MECHANICAL_ERRATUM_01.md exists", os.path.isfile(erratum),
       sha256_file(erratum)[:16] if os.path.isfile(erratum) else "")
    if os.path.isfile(erratum):
        text = open(erratum, encoding="utf-8").read()
        for token in ("SCIENTIFIC_DESIGN_CHANGED   = NO",
                      "OWNER_VALUE_CHANGED         = NO",
                      "ESTIMAND_CHANGED            = NO",
                      "OUTCOME_USED_TO_RESOLVE     = NO"):
            ck("erratum declares %s" % token.split("=")[0].strip(), token in text)
        ck("erratum names the proving synthetic test",
           "test_i12_short_position_loses_when_the_curve_rises" in text)
    stage_a = open(os.path.join(PKG, "vrp_stage_a.py"), encoding="utf-8").read()
    ck("vrp_stage_a uses the SIGNED convention (no leading minus on signed q)",
       "vm += q * STANDARD_MULTIPLIER" in stage_a
       and "vm += -q * STANDARD_MULTIPLIER" not in stage_a)
    stage_b = open(os.path.join(PKG, "vrp_stage_b.py"), encoding="utf-8").read()
    ck("vrp_stage_b uses the SIGNED convention",
       "vm += q * STANDARD_MULTIPLIER" in stage_b
       and "vm += -q * STANDARD_MULTIPLIER" not in stage_b)

    # ------------------------------------------------------------------------ #
    section("POST-S2 STATE-TRANSITION RESULT")
    status = "PASS" if _ok else "FAIL"
    print("  ORIGINAL_S1_VALIDATOR              = EXPECTED_POST_S2_STATE_FAILURE (exit %d)"
          % proc.returncode)
    print("  ORIGINAL_S1_CONTENT_CHECKS         = %d PASS / %d FAIL"
          % (len(passes), max(0, len(fails) - 1)))
    print("  POST_S2_STATE_TRANSITION_VALIDATOR = %s" % status)
    print("  checks: %d PASS / %d FAIL"
          % (sum(1 for r in _rows if r["pass"]), sum(1 for r in _rows if not r["pass"])))

    with open(RESULT_JSON, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({
            "lineage": "TSMOM-VRP-01",
            "generated_utc": _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "original_s1_validator": "EXPECTED_POST_S2_STATE_FAILURE",
            "original_s1_validator_exit": proc.returncode,
            "original_s1_content_checks_pass": len(passes),
            "original_s1_failing_checks": fails,
            "expected_state_failure": EXPECTED_STATE_FAILURE,
            "post_s2_state_transition_validator": status,
            "checks": _rows,
        }, fh, indent=2, sort_keys=True)
    return 0 if _ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
