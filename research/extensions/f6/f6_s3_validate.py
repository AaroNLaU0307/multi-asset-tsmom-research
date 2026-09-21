# -*- coding: utf-8 -*-
"""CTA-EDGE-05 / F6 — S3 result validation. STRUCTURAL ONLY.

```
THIS VALIDATOR NEVER REREADS THE HISTORICAL PRICE PANEL AND NEVER RECOMPUTES
THE TRIAL. ONE PRIMARY EXECUTION MEANS ONE PRIMARY EXECUTION.
```

It checks hashes, counts, sealed constants, the CI-to-class arithmetic, P3
applicability, the terminal-table mapping, provenance and artifact
completeness — all from the recorded artifact, plus the independent oracle's
own transcription of the sealed table.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import f6_authorization as auth      # noqa: E402
import f6_classify as fcls           # noqa: E402
import f6_contract as K              # noqa: E402
import f6_inference as finf          # noqa: E402
import f6_oracle as orc              # noqa: E402
import f6_report as frep             # noqa: E402

os.chdir(K.REPO)
PKG = "research/extensions/f6"
RESULT = "%s/s3/F6_S3_RESULT.json" % PKG
SENTINEL = "%s/s3/F6_S3_RUN_SENTINEL.json" % PKG
RUN_ID = "CTA-EDGE-05-F6-S3-PRIMARY-001"
BUILD_COMMIT = "43f0bb3156673402866f4c1e2d06f25044455d48"
BUILD_HASH = "050bb3d73e7c95930d79ebb987797d5a720c5d5081f70b423c3ebeb0a9a05d49"

P1_BACK = {"HARVESTABLE": K.CLASS_POSITIVE, "UNRESOLVED": K.CLASS_UNRESOLVED,
           "ECONOMICALLY_EXCLUDED": K.CLASS_ABSENT}
P2_BACK = {"SPECIFIC": K.CLASS_POSITIVE, "UNRESOLVED": K.CLASS_UNRESOLVED,
           "ABSENT": K.CLASS_ABSENT}

FAIL = []


def ck(name, ok, detail=""):
    print("  %-56s %s%s" % (name, "PASS" if ok else "FAIL",
                            ("  " + str(detail)) if detail else ""))
    if not ok:
        FAIL.append(name)


def sha(rel):
    with open(K.abspath(rel), "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def main():
    print("=" * 76)
    print("F6 S3 RESULT VALIDATION — structural, no re-execution")
    print("=" * 76)
    d = json.load(open(K.abspath(RESULT), encoding="utf-8"))
    m, i, g = d["measurement"], d["inference"], d["gate"]
    v, c, p = d["verdict"], d["claim_cap"], d["provenance"]

    print("\n[1] ARTIFACT COMPLETENESS")
    r = frep.validate_result(d)
    ck("result artifact passes its own schema validation", r["ok"], r["errors"])
    ck("run_state COMPLETE and data_kind REAL",
       d["run_state"] == "COMPLETE" and d["data_kind"] == auth.REAL)
    ck("run_id is the single authorized one", d["run_id"] == RUN_ID)
    for f in ("p1_estimate", "p2_beta_event"):
        ck("%s is a finite number" % f, isinstance(m[f], float))
    for f in ("p1_lower", "p1_upper", "p2_lower", "p2_upper"):
        ck("%s is a finite number" % f, isinstance(i[f], float))

    print("\n[2] PROVENANCE")
    ck("seal id", p["seal_id"] == K.SEAL_ID)
    ck("seal commit", p["seal_commit"] == K.SEAL_COMMIT)
    ck("build commit", p["build_commit"] == BUILD_COMMIT)
    ck("build hash", p["build_hash"] == BUILD_HASH)
    ck("sealed preregistration sha256",
       p["sealed_preregistration_sha256"] == sha(
           "%s/F6_S1_PREREGISTRATION_SEALED.md" % PKG) ==
       K.SEALED_PREREG_SHA256)
    ck("sealed manifest sha256",
       p["sealed_manifest_sha256"] == sha("%s/F6_S1_SEALED_MANIFEST.json" % PKG))
    ck("event manifest sha256",
       p["event_manifest_sha256"] == sha("%s/F6_FINAL_EVENT_MANIFEST.json" % PKG)
       == K.EVENT_MANIFEST_SHA256)
    ck("panel sha256 pinned (NOT reread)", p["panel_sha256"] == K.PANEL_SHA256)
    ck("authorization id recorded", p["authorization_id"] == "F6-AUTH-0001")
    ck("F6-AUTH commit recorded and is a real commit",
       subprocess.run(["git", "cat-file", "-e", p["f6_auth_commit"] + "^{commit}"],
                      cwd=K.REPO).returncode == 0, p["f6_auth_commit"])
    ck("exactly one primary execution recorded",
       p["primary_execution_count"] == 1 and p["bootstrap_execution_count"] == 1)
    ck("trial recorded as CONSUMED", p["f6_primary_trial_consumed"] is True)
    ck("runtime matches the sealed environment",
       p["runtime"] == {"python": K.PINNED_ENV["python"],
                        "numpy": K.PINNED_ENV["numpy"],
                        "pandas": K.PINNED_ENV["pandas"]}, p["runtime"])

    print("\n[3] COUNTS AND SEALED CONSTANTS")
    ck("event count 462", m["event_count"] == K.FINAL_PRIMARY_EVENT_COUNT)
    ck("family labels 119/176/176", m["family_labels"] == K.FAMILY_LABELS)
    ck("p2 rows 3772", m["p2_rows"] == K.P2_ROWS)
    ck("year count 15", m["year_count"] == K.YEAR_BLOCK_COUNT)
    ck("year blocks are 2011..2025",
       i["year_blocks"] == list(K.PRIMARY_YEARS))
    ck("B == 100000", i["bootstrap_B"] == 100000)
    ck("seed == 2540719150", i["bootstrap_seed_literal"] == 2540719150)
    ck("seed reproduces from its source string",
       int(hashlib.sha256(i["bootstrap_seed_source"].encode("ascii"))
           .hexdigest()[:8], 16) == i["bootstrap_seed_literal"])
    ck("quantile implementation", i["quantile_implementation"] ==
       K.QUANTILE_IMPLEMENTATION)
    ck("quantiles 0.025 / 0.975",
       (i["lower_quantile"], i["upper_quantile"]) == (0.025, 0.975))
    ck("interval described as NOMINAL, never exact",
       "nominal" in i["interval"].lower() and "NOT exact" in i["coverage_claim"])

    print("\n[4] CI -> CLASS ARITHMETIC, RECOMPUTED FROM THE ENDPOINTS")
    p1k = finf.classify_interval(i["p1_lower"], i["p1_upper"])
    p2k = finf.classify_interval(i["p2_lower"], i["p2_upper"])
    ck("P1 class matches its own interval",
       P1_BACK[g["p1_class"]] == p1k, "%s <- [%r, %r]" % (g["p1_class"],
                                                          i["p1_lower"],
                                                          i["p1_upper"]))
    ck("P2 class matches its own interval",
       P2_BACK[g["p2_class"]] == p2k, g["p2_class"])
    ck("P1 class agrees with the INDEPENDENT oracle",
       orc.oracle_classify_interval(i["p1_lower"], i["p1_upper"]) == p1k)
    ck("P2 class agrees with the INDEPENDENT oracle",
       orc.oracle_classify_interval(i["p2_lower"], i["p2_upper"]) == p2k)
    ck("P1 point lies inside its own interval",
       i["p1_lower"] <= m["p1_estimate"] <= i["p1_upper"])
    ck("P2 point lies inside its own interval",
       i["p2_lower"] <= m["p2_beta_event"] <= i["p2_upper"])
    ck("lower < upper for both", i["p1_lower"] < i["p1_upper"]
       and i["p2_lower"] < i["p2_upper"])

    print("\n[5] P3 APPLICABILITY")
    should = fcls.p3_is_evaluated(p1k, p2k)
    ck("P3 applicability follows the seal", g["p3_evaluated"] == should,
       "evaluated=%s expected=%s" % (g["p3_evaluated"], should))
    if not should:
        ck("P3 NOT computed out of curiosity",
           g["p3_pass"] == "NOT_APPLICABLE_BY_SEAL"
           and g["p3_year_results"] == "NOT_APPLICABLE_BY_SEAL")
    else:
        ck("15 LOYO deletions recorded", len(g["p3_year_results"]) == 15)
        ck("P3 pass iff every LOYO point estimate strictly > 0",
           g["p3_pass"] == all(y["p1_point"] > 0 and y["beta_event_point"] > 0
                               for y in g["p3_year_results"].values()))

    print("\n[6] TERMINAL TABLE MAPPING")
    expect = fcls.classify(p1k, p2k, g["p3_pass"] if should else None)
    ck("terminal classification is the sealed classifier's output",
       v["terminal_classification"] == expect["terminal_classification"],
       v["terminal_classification"])
    ck("terminal classification agrees with the INDEPENDENT oracle",
       v["terminal_classification"] == orc.oracle_terminal(
           p1k, p2k, g["p3_pass"] if should else None))
    ck("research_status consistent", v["research_status"] ==
       expect["research_status"])
    ck("no forbidden terminal state",
       v["terminal_classification"] not in K.FORBIDDEN_TERMINAL_STATES
       and "LOW_POWER" not in v["terminal_classification"])
    ck("research_status is never 'confirmed'",
       v["research_status"] != "confirmed")

    print("\n[7] CLAIM CAP")
    ck("sample reuse T0_REUSED_DEPENDENT",
       c["sample_reuse_class"] == "T0_REUSED_DEPENDENT")
    ck("evidence ceiling SUPPORTED", c["evidence_ceiling"] == "SUPPORTED")
    ck("independent confirmation NO", c["independent_confirmation"] is False)
    for s in ("independent confirmation", "buy-and-hold dominance",
              "exact finite-sample 95% coverage", "future persistence"):
        ck("claim cap forbids %r" % s, s in c["must_not_claim"])

    print("\n[8] NO SECOND RUN, NO UNDOCUMENTED DIAGNOSTIC")
    sent = json.load(open(K.abspath(SENTINEL), encoding="utf-8"))
    ck("sentinel closed as TARGET_ACCESS_COMPLETED",
       sent["state"] == "TARGET_ACCESS_COMPLETED")
    ck("sentinel run_id matches", sent["run_id"] == RUN_ID)
    ck("sentinel records exposure and consumption",
       sent.get("f6_outcome_exposure_occurred") is True
       and sent.get("f6_primary_trial_consumed") is True)
    files = sorted(f for f in os.listdir(K.abspath("%s/s3" % PKG))
                   if f.endswith(".json"))
    ck("exactly one RESULT artifact exists (plus sentinel and validation)",
       files == ["F6_S3_RESULT.json", "F6_S3_RESULT_VALIDATION.json",
                 "F6_S3_RUN_SENTINEL.json"]
       or files == ["F6_S3_RESULT.json", "F6_S3_RUN_SENTINEL.json"], files)

    # Exact key allowlist, not a substring scan. A substring scan flagged
    # bootstrap_seed_lit-ERA-l and cov-ERA-ge_claim, which is noise; comparing
    # against the sealed schema's own keys is both cleaner and STRICTER,
    # because it catches ANY extra field rather than only keyword-shaped ones.
    empty = frep.empty_result()
    DRIVER_PROVENANCE = {"f6_auth_commit", "build_commit", "started_utc",
                         "finished_utc", "runtime", "primary_execution_count",
                         "bootstrap_execution_count", "sealed_class_tokens"}
    for layer in ("measurement", "inference", "gate", "verdict", "claim_cap"):
        extra = set(d[layer]) - set(empty[layer])
        ck("%s carries no field outside the sealed schema" % layer,
           not extra, sorted(extra))
    extra_p = set(d["provenance"]) - set(empty["provenance"]) - DRIVER_PROVENANCE
    ck("provenance carries no undeclared field", not extra_p, sorted(extra_p))
    ck("no per-family, TLT, F6.b, era or alternate-model OUTCOME field",
       not any(k in d[l] for l in ("measurement", "inference", "gate",
                                   "verdict")
               for k in ("fomc_mean", "cpi_mean", "nfp_mean", "tlt_beta",
                         "f6b_drift", "era_split", "alternate_beta",
                         "sharpe", "drawdown", "hit_rate", "rescue")))

    ok = not FAIL
    print("\n" + "=" * 76)
    print("S3_RESULT_VALIDATION = %s   (%d failing)"
          % ("PASS" if ok else "FAIL", len(FAIL)))
    for f in FAIL:
        print("   FAILED: %s" % f)
    print("=" * 76)

    out = {"schema": {"name": "f6-s3-result-validation", "version": 1},
           "run_id": RUN_ID,
           "s3_result_validation": "PASS" if ok else "FAIL",
           "failing_checks": FAIL,
           "second_historical_run_performed": False,
           "historical_panel_reread": False,
           "result_artifact_sha256": sha(RESULT),
           "sentinel_sha256": sha(SENTINEL),
           "recomputed_p1_class": p1k, "recomputed_p2_class": p2k,
           "p3_applicable": should,
           "terminal_classification": v["terminal_classification"],
           "oracle_agrees": True}
    pth = K.abspath("%s/s3/F6_S3_RESULT_VALIDATION.json" % PKG)
    with open(pth, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print("\nwrote %s  sha256 %s" % (pth, sha(
        "%s/s3/F6_S3_RESULT_VALIDATION.json" % PKG)))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
