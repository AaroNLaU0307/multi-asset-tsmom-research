# -*- coding: utf-8 -*-
"""The pre-S3 dry gates. Every one must pass before an Owner authorization.

No target outcome is computed here. The comparator is recomputed — it is the
already-published incumbent book, not a Value quantity — and everything
outcome-bearing runs on synthetic fixtures.
"""
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for _p in (_REPO, HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import value_authorization as A     # noqa: E402
import value_comparator as K        # noqa: E402
import value_contract as C          # noqa: E402
import value_evidence as EV         # noqa: E402
import value_inference as I         # noqa: E402

GATES = []


def gate(name, ok, detail=""):
    GATES.append((name, bool(ok), detail))
    print("  %-34s %s   %s" % (name, "PASS" if ok else "FAIL", detail))


def _script(name, *args):
    r = subprocess.run([sys.executable, os.path.join(HERE, name)] + list(args),
                       capture_output=True, text=True)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def main():
    print("== pre-S3 dry gates ==")
    print()

    # 1 / 8 — the active sealed contract ------------------------------------
    ok, checks = C.conformance()
    failed = [l for l, c, _d in checks if not c]
    gate("CONTRACT_CONFORMANCE", ok, "%d checks" % len(checks))
    gate("ACTIVE_SEALED_PREREG_VALIDATION",
         ok and C.sealed_sha256() == C.SEALED_PREREG_SHA256,
         C.SEALED_PREREG_SHA256[:16] if ok else str(failed[:2]))

    # 2 — comparator identity ------------------------------------------------
    kok, kchecks = K.verify_identity()
    gate("COMPARATOR_IDENTITY_PINNED", kok,
         "%s, %d checks" % (K.COMPARATOR_ID, len(kchecks)))

    # 3 — comparator reproducibility ----------------------------------------
    try:
        m1, v1 = K.comparator_window()
        m2, v2 = K.comparator_window()
        d1, d2 = K.series_digest(m1, v1), K.series_digest(m2, v2)
        gate("COMPARATOR_REPRODUCIBILITY",
             d1 == d2 and m1 == m2 and len(m1) == C.N_MONTHS,
             "N=%d digest %s" % (len(m1), d1[:16]))
    except Exception as exc:                       # noqa: BLE001
        gate("COMPARATOR_REPRODUCIBILITY", False, str(exc)[:50])

    # 4 / 5 / 7 — the synthetic rehearsal ------------------------------------
    reh_code, reh = _script("value_rehearsal.py")
    gate("SYNTHETIC_END_TO_END",
         reh_code == 0 and "SYNTHETIC_END_TO_END = PASS" in reh,
         reh.strip().splitlines()[-3].strip() if reh.strip() else "")
    gate("CONDITIONAL_FULL_BRANCHING",
         reh_code == 0 and reh.count("FULL never computed") >= 3
         and "schema rejects FULL fields on a refused branch" in reh,
         "3 refusal branches + 3 FULL verdicts")
    gate("AUTHORIZATION_SINGLE_USE_TEST",
         reh_code == 0 and "consumed authorization refuses reuse" in reh
         and "absent authorization refuses" in reh)
    gate("LONG_EPISODE_ADJUDICABILITY_TEST",
         reh_code == 0
         and "the whole-window episode is the top selection" in reh
         and "it remains a VALID, adjudicable inference" in reh
         and "FAIL" not in "".join(
             l for l in reh.splitlines() if l.strip().startswith("11 ")),
         "a 143-month episode stays adjudicable under the ablation operator")

    # 6 — evidence schema ----------------------------------------------------
    bad_cases = [
        ({}, "empty"),
        ({"schema": EV.SCHEMA, "FULL_EXECUTED": False,
          "FULL_CI": {"lower": 0, "upper": 1, "level": 95, "n_valid": 1}},
         "FULL fields on a refused branch"),
    ]
    schema_ok = all(not EV.validate(b)[0] for b, _l in bad_cases)
    gate("EVIDENCE_SCHEMA_VALIDATION", schema_ok,
         "%d malformed artifacts rejected" % len(bad_cases))

    # 9 — data provenance ----------------------------------------------------
    code, out = _script("value_runner.py", "validate")
    gate("DATA_PROVENANCE_VALIDATION",
         code == 0 and "VALUE_DATA_VALIDATION = PASS" in out)

    # 10 — bootstrap determinism --------------------------------------------
    rng = np.random.default_rng(3)
    x = list(0.01 + 0.03 * rng.standard_normal(C.N_MONTHS))
    y = list(0.01 + 0.03 * rng.standard_normal(C.N_MONTHS))
    a1 = I.standalone_ci(x)
    a2 = I.standalone_ci(x)
    c1 = I.correlation_ci(x, y)
    seeds = {arm: I.seed_for(arm).entropy for arm in C.ARM_ORDER}
    spawn_keys = {arm: I.seed_for(arm).spawn_key for arm in C.ARM_ORDER}
    gate("BOOTSTRAP_DETERMINISM",
         a1["lower"] == a2["lower"] and a1["upper"] == a2["upper"]
         and len(set(spawn_keys.values())) == len(C.ARM_ORDER)
         and all(e == C.MASTER_SEED for e in seeds.values())
         and a1["counts"]["attempted"] == C.BOOTSTRAP_REPS
         and c1["n_valid"] >= C.VALID_REPLICATE_FLOOR,
         "identical CI on repeat; %d distinct arm seeds from SeedSequence(%d)"
         % (len(set(spawn_keys.values())), C.MASTER_SEED))

    # 11 — C3 semantics ------------------------------------------------------
    P = {"c1": True, "c2": True}
    c3_truth = [
        ([P, P, P], True),
        ([P, {"c1": False, "c2": True}, P], False),
        ([P, {"c1": True, "c2": False}, P], False),
        ([P, {"invalid": True, "c1": False, "c2": False}, P], False),
        ([P, P], False),                              # wrong number of cases
        (None, False),
    ]
    gate("C3_SYNTHETIC_VALIDATION",
         all(I.c3_pass(cases, k=3) is expected for cases, expected in c3_truth),
         "%d truth-table rows; C1 AND C2 in every case" % len(c3_truth))

    # 12 — verdict boundaries ------------------------------------------------
    E, F, Dl = C.E_POSITIVE, C.F_ADVERSE, C.DELTA_COMBO
    boundary = [
        (I.standalone_verdict(E, 9.0), C.UNRESOLVED_EDGE),        # L == +E
        (I.standalone_verdict(E + 1e-9, 9.0), C.SUPPORTED_POSITIVE_EDGE),
        (I.standalone_verdict(-9.0, -F), C.UNRESOLVED_EDGE),      # U == -F
        (I.standalone_verdict(-9.0, -F - 1e-9), C.MATERIALLY_ADVERSE),
        (I.standalone_verdict(0.001, 9.0), C.UNRESOLVED_EDGE),    # zero is not
        (I.standalone_verdict(-9.0, -0.001), C.UNRESOLVED_EDGE),  # the boundary
        (I.combo_verdict(Dl, 9.0), C.INCREMENTAL_BENEFIT_NOT_ESTABLISHED),
        (I.combo_verdict(Dl + 1e-9, 9.0), C.SUPPORTED_INCREMENTAL_BENEFIT),
        (I.combo_verdict(-9.0, 0.0), C.INCREMENTAL_BENEFIT_NOT_ESTABLISHED),
        (I.combo_verdict(-9.0, -1e-9), C.INCREMENTAL_BENEFIT_ADVERSE),
    ]
    rho_edge = (I.c2_pass(C.RHO_MAX) is True
                and I.c2_pass(C.RHO_MAX + 1e-9) is False
                and I.c2_pass(None) is False)
    gate("VERDICT_BOUNDARY_VALIDATION",
         all(got == want for got, want in boundary) and rho_edge,
         "strict +E/-F/+delta/zero; rho_max %.2f passes on equality" % C.RHO_MAX)

    # 12b — C3 structural ADJUDICABILITY on the REAL signal path -----------
    # AMENDMENT_003 replaces the obsolete whole-calendar reachability gate.
    # This asks only whether C3 CAN be adjudicated, never whether it passes,
    # and it uses no target outcome value: episodes come from the signal path,
    # which §11 defines independently of any return, and the rest are
    # invariants of the operator itself.
    try:
        import value_data as D
        import value_signal as VS
        import value_sleeve as SL
        ms = D.m_range(C.EVAL_START, C.EVAL_END)
        sig = SL.signals_on(ms)
        sel = VS.select_episodes(sig, k=C.K_EPISODES)

        mapped = [(e, SL.contribution_months(e, ms)) for e in sel]
        all_mapped = all(len(cm) > 0 for _e, cm in mapped)
        in_window = all(set(cm) <= set(ms) for _e, cm in mapped)
        deterministic = all(
            SL.contribution_months(e, ms) == cm for e, cm in mapped)

        # The operator retains every calendar month by construction. Proven on
        # a neutral series so no real return is touched.
        probe_net = [0.0] * len(ms)
        probe_led = {"contributions": {i: [0.0] * len(ms) for i in C.UNIVERSE},
                     "shared": [0.0] * len(ms)}
        lengths, no_deletion = [], True
        for e, _cm in mapped:
            abl, _am = SL.ablate(ms, probe_net, probe_led, e)
            lengths.append(len(abl))
            if len(abl) != len(ms):
                no_deletion = False
        can_evaluate = all(n >= C.MIN_DISTINCT_MONTHS for n in lengths)

        gate("C3_STRUCTURAL_ADJUDICABILITY",
             len(sel) == C.K_EPISODES and all_mapped and in_window
             and deterministic and no_deletion and can_evaluate,
             "3 episodes map to %s contribution months; %d calendar months "
             "retained in every case (floor %d)"
             % ("/".join(str(len(cm)) for _e, cm in mapped),
                lengths[0] if lengths else 0, C.MIN_DISTINCT_MONTHS))
    except Exception as exc:                       # noqa: BLE001
        gate("C3_STRUCTURAL_ADJUDICABILITY", False, str(exc)[:60])

    # 12c — contribution accounting reconciles ------------------------------
    # Proven on the REAL sleeve code path driven by synthetic inputs. Running
    # it on the real inputs would compute the Value return series, which is a
    # target outcome and is forbidden before the authorized run.
    _recon = [l for l in reh.splitlines()
              if "decomposition reconstructs the sealed series" in l]
    gate("CONTRIBUTION_ACCOUNTING_RECONCILIATION",
         reh_code == 0 and len(_recon) == 1 and "PASS" in _recon[0],
         "V_t = a_t + sum_i c_i,t on the real code path, synthetic inputs")

    # 13 — real-run safety ---------------------------------------------------
    auth = A.load()
    ev_path = os.path.join(HERE, "VALUE_EVIDENCE.json")
    code, out = _script("value_runner.py", "execute", "--run-id", "GATE_PROBE")
    gate("REAL_RUN_SAFETY",
         (auth is None or auth.get("status") != A.STATUS_ACTIVE)
         and not os.path.exists(ev_path)
         and code == 2 and "EXECUTION_REFUSED" in out
         and "target calculations executed: NONE" in out,
         "entry point refuses; no authorization, no artifact")

    print()
    failed = [g for g in GATES if not g[1]]
    print("  gates: %d   failed: %d" % (len(GATES), len(failed)))
    print()
    print("  VALUE_TARGET_RETURNS_COMPUTED    = NO")
    print("  VALUE_SHARPE_COMPUTED            = NO")
    print("  VALUE_TSMOM_CORRELATION_COMPUTED = NO")
    print("  COMBINATION_OUTCOME_COMPUTED     = NO")
    print("  REAL_TARGET_BACKTEST_RUN         = NO")
    print()
    print("PRE_S3_GATES =", "PASS" if not failed else "FAIL")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
