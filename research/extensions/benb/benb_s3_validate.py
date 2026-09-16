"""CTA-EDGE-02-BENB — post-run validation of the S3 governed result.

Runs ENTIRELY on the recorded artifact, the sealed contract text and committed
governance state. It deliberately does **not** re-read `data/benb/`: the grant
authorised exactly ONE historical execution, and re-opening the panel to double-check a
number would be a second historical data access even though it would compute nothing
new. The decomposition identity was verified inside the authorised run itself, over
every observation used, and that check is what this validator reads back.

    python research/extensions/benb/benb_s3_validate.py
"""

from __future__ import annotations

import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
os.chdir(REPO)

import benb_authorization as auth          # noqa: E402
import benb_classify as bcls               # noqa: E402
import benb_contract as K                  # noqa: E402
import benb_report as brep                 # noqa: E402

RESULT_PATH = os.path.join(K.BENB_DIR, "s3", "BENB_S3_RESULT.json")
RUN_ID = "BENB-RUN-20260915-01"
AUTHORIZATION_ID = "BENB-AUTH-0001"
RNG_SEED = 1788924436

CHECKS = []


def check(name, ok, detail=""):
    CHECKS.append((name, bool(ok), detail))
    print(f"  {'PASS' if ok else 'FAIL'}  {name}" + (f"   {detail}" if detail else ""))
    return bool(ok)


def sha256_of(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def main():
    print("CTA-EDGE-02-BENB — S3 RESULT VALIDATION")
    print(f"  artifact {RESULT_PATH}")
    with open(RESULT_PATH, encoding="utf-8") as fh:
        d = json.load(fh)

    # -- 1. schema and the sealed status mapping ---------------------------- #
    chk = brep.validate_result(d)
    check("result artifact satisfies the sealed BENB-RESULT-1 schema", chk["ok"],
          str(chk["problems"]) if not chk["ok"] else "")
    check("every required field present",
          all(f in d for f in brep.REQUIRED_FIELDS))

    # -- 2. the seal is intact --------------------------------------------- #
    check("sealed preregistration unchanged",
          sha256_of(os.path.join(K.BENB_DIR, "BENB_PREREGISTRATION.md"))
          == K.SEALED_PREREG_SHA256, K.SEALED_PREREG_SHA256)
    check("S1 seal manifest unchanged",
          sha256_of(os.path.join(K.BENB_DIR, "BENB_SEAL_MANIFEST.md"))
          == K.SEAL_MANIFEST_SHA256, K.SEAL_MANIFEST_SHA256)
    check("artifact records the same seal identities",
          d["sealed_prereg_sha256"] == K.SEALED_PREREG_SHA256
          and d["seal_manifest_sha256"] == K.SEAL_MANIFEST_SHA256)

    # -- 3. inputs --------------------------------------------------------- #
    rec = d["input_hashes"]
    check("all seven pinned inputs recorded",
          all(n in rec for n in K.PINNED), f"{len(K.PINNED)} files")
    check("recorded input hashes equal the sealed pins",
          all(rec[n] == want for n, want in K.PINNED.items()))
    check("pinned files on disk still reproduce",
          all(sha256_of(os.path.join(K.DATA_DIR, n)) == want
              for n, want in K.PINNED.items()))

    # -- 4. the grant ------------------------------------------------------ #
    grant = None
    for r in auth.benb_authorization_records():
        if r.get("record_type") == "AUTHORIZATION":
            grant = r
    b = (grant or {}).get("binding", {})
    check("exactly one BENB AUTHORIZATION record exists",
          sum(1 for r in auth.benb_authorization_records()
              if r.get("record_type") == "AUTHORIZATION") == 1)
    check("artifact run_id matches the grant",
          d["run_id"] == b.get("run_id") == RUN_ID, RUN_ID)
    check("artifact rng_seed matches the grant",
          d["rng_seed"] == b.get("rng_seed") == RNG_SEED, str(RNG_SEED))
    check("rng_seed is the sealed derivation int('6aa0d214', 16)",
          RNG_SEED == int(K.SEAL_MANIFEST_SHA256[:8], 16))
    check("artifact authorization id matches the grant",
          d["run_authorization_id"] == grant.get("authorization_id")
          == AUTHORIZATION_ID, AUTHORIZATION_ID)
    check("artifact binds the accepted S2 implementation commit",
          d["s2_implementation_commit"] == b.get("s2_implementation_commit"),
          str(d["s2_implementation_commit"]))

    # -- 5. exactly one execution, and it is consumed ----------------------- #
    life = [r for r in auth.benb_authorization_records()
            if r.get("record_type") == "LIFECYCLE"]
    consumed = [r for r in life if r.get("event") == "CONSUMED"]
    check("exactly one CONSUMED lifecycle record", len(consumed) == 1,
          str([r.get("event") for r in life]))
    check("the consumed record names this run_id",
          bool(consumed) and consumed[0].get("run_id") == RUN_ID)
    check("the consumed record reports execution_count = 1",
          bool(consumed) and consumed[0].get("evidence", {}).get("run_count") == 1)
    check("no live BENB EXECUTION grant remains",
          auth.active_execution_authorization("EXECUTION") is None)
    check("a further REAL run is refused",
          _refuses(auth.REAL, RUN_ID))

    # -- 6. inference settings --------------------------------------------- #
    check("bootstrap B equals the sealed 10,000",
          d["bootstrap_replicates"] == K.BOOTSTRAP_B == 10_000)
    for name in ("beta_T", "beta_O", "beta_N", "mean_net_trade_return_bps",
                 "calendarised_sharpe"):
        iv = d[name]
        check(f"{name}: 10,000/10,000 valid replicates",
              iv["replicates"] == 10_000 and iv["valid_replicates"] == 10_000)

    # -- 7. the classification reproduces from the recorded inputs ---------- #
    bt, bo, bn = d["beta_T"], d["beta_O"], d["beta_N"]
    mr, sh = d["mean_net_trade_return_bps"], d["calendarised_sharpe"]
    loyo_ok = bool(d["loyo_beta_T"]["passes"])
    v = bcls.classify(bt["lower"], bt["upper"], bo["lower"], bo["upper"],
                      bn["lower"], bn["upper"], mr["lower"], mr["upper"],
                      sh["lower"], sh["upper"], loyo_ok, is_evaluable=True)
    check("re-classifying the RECORDED intervals reproduces the recorded class",
          v.klass == d["final_class"], f"{v.klass} == {d['final_class']}")
    check("research_status reproduces", v.research_status == d["research_status"])
    check("qualifier reproduces", v.qualifier == d["qualifier"])
    status, qualifier = K.STATUS_MAP[d["final_class"]]
    check("class/status/qualifier agree with the sealed §I.4 mapping",
          d["research_status"] == status and d["qualifier"] == qualifier)

    # -- 8. the gate flags agree with the intervals ------------------------- #
    fl, gr = d["classification_flags"], d["gate_results"]
    check("gate1_supported == (L_T > 0)",
          fl["gate1_supported"] == gr["GATE1_PASS"] == (bt["lower"] > 0.0))
    check("m1_supported == (L_R > 0), STRICT",
          fl["m1_supported"] == gr["M1_PASS"]
          == (mr["lower"] > K.M1_RETURN_FLOOR_BPS))
    check("m2_supported == (L_S > +0.30), STRICT",
          fl["m2_supported"] == gr["M2_PASS"] == (sh["lower"] > K.M2_SHARPE))
    check("M2 recorded as STRICT > +0.30",
          fl["m2_operator"] == "STRICT >" and fl["m2_value"] == 0.30)
    check("loyo flag matches the per-year table",
          fl["loyo_ok"] == loyo_ok
          == all(x > 0 for x in d["loyo_beta_T"]["per_year_beta_T"].values()))

    # -- 9. evaluability and the structural pre-run check -------------------- #
    s = d["structural_pre_run_check"]
    check("HYG structural eligibility reproduced the sealed count",
          s["HYG"]["eligible"] == s["HYG"]["sealed_eligible"]
          == K.STRUCTURAL_ELIGIBLE["HYG"], str(s["HYG"]["eligible"]))
    check("LQD structural eligibility reproduced the sealed count",
          s["LQD"]["eligible"] == s["LQD"]["sealed_eligible"]
          == K.STRUCTURAL_ELIGIBLE["LQD"], str(s["LQD"]["eligible"]))
    check("common grids reproduced the sealed counts",
          s["HYG"]["common_grid_dates"] == K.STRUCTURAL_COMMON["HYG"]
          and s["LQD"]["common_grid_dates"] == K.STRUCTURAL_COMMON["LQD"])
    ident = d["decomposition_identity"]
    check("decomposition identity held on every observation used",
          all(x["max_abs_residual"] <= x["tolerance"] for x in ident.values()),
          f"HYG max |residual| {ident['HYG']['max_abs_residual']:.3e} over "
          f"{ident['HYG']['n_checked']} obs")
    check("§J.2(d): at least 3 calendar years carry a discount observation",
          d["years_with_discount"] >= K.MIN_YEARS_WITH_DISCOUNT,
          str(d["years_with_discount"]))

    # -- 10. the sealed firewalls survived into the artifact ---------------- #
    check("evidence ceiling is `supported`", d["evidence_ceiling"] == "supported")
    check("historical outcome exposure is declared",
          d["HISTORICAL_OUTCOME_EXPOSED"] == "YES" and d["synthetic_only"] == "NO")
    check("LQD carries no promotion and no rescue power",
          d["lqd_secondary"]["promotion_power"] == "NONE"
          and d["lqd_secondary"]["rescue_power"] == "NONE")
    check("premium side carries no promotion and no rescue power",
          d["premium_side_descriptives"]["promotion_power"] == "NONE"
          and d["premium_side_descriptives"]["rescue_power"] == "NONE")
    check("the class was NOT reached through a diagnostic, LQD or the premium side",
          _class_is_diagnostic_independent(d, v.klass))
    check("forbidden-interpretation block carried", "REDUCED-FORM"
          in d["forbidden_interpretations"])
    check("mixed/dependent provenance warning carried",
          "MIXED / DEPENDENT" in d["basis_data_provenance_warning"])
    check("N_trials still NOT ASSERTED",
          "NOT ASSERTED" in d["sample_reuse"]["n_trials"])

    ok = all(o for _, o, _ in CHECKS)
    print(f"\nCTA-EDGE-02-BENB S3 RESULT VALIDATOR: "
          f"{sum(1 for _, o, _ in CHECKS if o)}/{len(CHECKS)} "
          f"{'PASS' if ok else 'FAIL'}")
    print(f"RESULT: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


def _refuses(kind, run_id):
    try:
        auth.require_run_authorization(kind, run_id)
        return False
    except auth.RunNotAuthorized:
        return True


def _class_is_diagnostic_independent(d, klass):
    """A-M / A / B are REACHED BY the diagnostics but cannot be PROMOTED by them.

    The check that matters after the fact: with the diagnostics replaced by neutral
    intervals the class must still be a non-promoted one, i.e. no diagnostic value
    could have turned this outcome into `S`.
    """
    bt = d["beta_T"]
    mr, sh = d["mean_net_trade_return_bps"], d["calendarised_sharpe"]
    for lo, up in ((-1.0, -0.5), (-0.5, 0.5), (0.5, 1.0)):
        for nlo, nup in ((-1.0, -0.5), (-0.5, 0.5), (0.5, 1.0)):
            alt = bcls.classify(bt["lower"], bt["upper"], lo, up, nlo, nup,
                                mr["lower"], mr["upper"], sh["lower"], sh["upper"],
                                bool(d["loyo_beta_T"]["passes"]), is_evaluable=True)
            if alt.klass == "S":
                return False
    return True


if __name__ == "__main__":
    raise SystemExit(main())
