# -*- coding: utf-8 -*-
"""Value CLI. The S3 real-run entry point exists and is GUARDED.

    conformance   prove the implementation constants match the sealed contract
    validate      schema / date / provenance / causal-availability checks only
    status        is an authorization active? does an evidence artifact exist?
    authorize     OWNER ACT — mint the one single-use S3 authorization
    execute       the S3 real run — requires an active single-use authorization

`execute` refuses before any target calculation unless exactly one ACTIVE
authorization exists that is bound to the sealed bytes on disk. It spends that
authorization before running, so a failure cannot silently free a second
attempt, and it never overwrites an existing evidence artifact. Minting an
authorization is an Owner act; nothing in the build does it.
"""
import argparse
import hashlib
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import value_contract as C           # noqa: E402
import value_data as D               # noqa: E402

EXIT_OK = 0
EXIT_FAIL = 1
EXIT_REFUSED = 2

AUTHORIZATION_MECHANISM_NOTE = (
    "Execution requires one ACTIVE single-use authorization object bound to the "
    "sealed bytes (value_authorization.py). Minting it is an Owner act. There is "
    "no code flag that opens the run.")


def cmd_conformance(_args):
    ok, checks = C.conformance()
    width = max(len(l) for l, _c, _d in checks)
    for label, cond, detail in checks:
        print("  %-*s %s   %s" % (width, label, "PASS" if cond else "FAIL", detail))
    print()
    print("CONTRACT_CONFORMANCE =", "PASS" if ok else "FAIL")
    return EXIT_OK if ok else EXIT_FAIL


def cmd_validate(_args):
    """Real raw data is touched ONLY for schema, dates, units and availability.

    No object series, signal, return, Sharpe, correlation or verdict is produced.
    """
    ok = True

    def ck(label, cond, detail=""):
        nonlocal ok
        if not cond:
            ok = False
        print("  %-54s %s   %s" % (label, "PASS" if cond else "FAIL", detail))

    print("== sealed contract ==")
    actual = C.sealed_sha256()
    ck("sealed prereg sha256 unchanged", actual == C.SEALED_PREREG_SHA256,
       actual[:16])

    print()
    print("== raw inputs present and pinned ==")
    inv_path = os.path.join(C.REPO, "research/extensions/value/"
                                    "VALUE_DATA_INVENTORY.json")
    import json
    inv = json.load(io.open(inv_path, encoding="utf-8"))
    pinned = {}
    for block in ("accepted_objects", "unblock_pass", "phase_a_closure",
                  "phase_a_correction"):
        node = inv.get(block)
        rows = node if isinstance(node, list) else (node or {}).get("series", [])
        for r in rows or []:
            if r.get("raw_file"):
                pinned[os.path.basename(r["raw_file"])] = \
                    r.get("sha256_of_raw_file_on_disk")
    us = inv["s1_final_repair"]["us_cpi_corrected"]
    pinned[os.path.basename(us["raw_file"])] = us["sha256_of_raw_file_on_disk"]

    for key, fname in sorted(C.RAW_INPUTS.items()):
        p = os.path.join(C.REPO, C.RAW_DIR, fname)
        if not os.path.isfile(p):
            ck("present: %s" % fname, False, "MISSING")
            continue
        h = hashlib.sha256(io.open(p, "rb").read()).hexdigest()
        want = pinned.get(fname)
        ck("pinned: %-40s" % fname, want is None or h == want,
           h[:16] if want else "(not individually pinned)")

    print()
    print("== schema and causal availability (dates only) ==")
    months = D.m_range(C.EVAL_START, C.EVAL_END)
    ck("evaluation window length is the sealed N",
       len(months) == C.N_MONTHS, "%d months" % len(months))
    ck("window endpoints are the sealed ones",
       months[0] == C.EVAL_START and months[-1] == C.EVAL_END,
       "%s .. %s" % (months[0], months[-1]))

    cape = D.load_shiller_cape()
    tlt = D.load_fred_daily_to_monthly("DFII20.csv")
    credit = D.load_fred_daily_to_monthly("BAA10Y.csv")
    for name, series, lag in (("CAPE", cape, C.LAG_CAPE_MONTHS),
                              ("DFII20", tlt, 0), ("BAA10Y", credit, 0)):
        ref_first, _ = D.admissible_at(series, months[0], lag)
        ref_last, _ = D.admissible_at(series, months[-1], lag)
        ck("%s admissible across the window" % name,
           ref_first is not None and ref_last is not None,
           "%s -> %s" % (ref_first, ref_last))
        ck("%s never uses a future reference month" % name,
           ref_last is None or D.m_key(ref_last) <= D.m_key(months[-1]) - lag)

    cpi = {c: fn() for c, fn in D.CPI_LOADERS.items()}
    for cur in ("US",) + tuple(C.FX_WEIGHTS):
        s = cpi[cur]
        # Coverage must span the WHOLE window under the declared lag, not merely
        # exist at the end. Counting index periods rather than observations that
        # actually carry a value is exactly how a gap gets missed.
        first_usable = D.m_shift(min(s), C.LAG_CPI_MONTHS) if s else None
        last_ref, _ = D.admissible_at(s, months[-1], C.LAG_CPI_MONTHS)
        covers = (bool(s) and first_usable is not None
                  and D.m_key(first_usable) <= D.m_key(months[0])
                  and last_ref is not None)
        ck("CPI %s covers the whole window" % cur, covers,
           "%d obs %s..%s, usable from %s"
           % (len(s), min(s) if s else "-", max(s) if s else "-", first_usable))
    for cur, fname in D.FX_FILES.items():
        s = D.load_fred_daily_to_monthly(fname)
        ref, _ = D.admissible_at(s, months[-1], 0)
        ck("FX %s admissible at the window end" % cur, ref is not None,
           "%d months, ref %s" % (len(s), ref))

    print()
    print("== safety ==")
    import value_authorization as A
    _auth = A.load()
    ck("no ACTIVE Value execution authorization exists",
       _auth is None or _auth.get("status") != A.STATUS_ACTIVE,
       A.status_line())
    ck("no evidence artifact exists yet",
       not os.path.exists(os.path.join(HERE, "VALUE_EVIDENCE.json")))
    print("  VALUE_TARGET_RETURNS_COMPUTED = NO")
    print("  VALUE_SHARPE_COMPUTED = NO")
    print("  VALUE_TSMOM_CORRELATION_COMPUTED = NO")
    print("  COMBINATION_OUTCOME_COMPUTED = NO")
    print()
    print("VALUE_DATA_VALIDATION =", "PASS" if ok else "FAIL")
    return EXIT_OK if ok else EXIT_FAIL


def cmd_authorize(args):
    """OWNER ACT. Mint the one single-use authorization. Never self-invoked."""
    import value_authorization as A
    if args.owner_decision != A.OWNER_DECISION_PHRASE:
        print("AUTHORIZATION REFUSED: the Owner decision phrase must be given "
              "in full.")
        print("  expected: %s" % A.OWNER_DECISION_PHRASE)
        return EXIT_REFUSED
    try:
        auth = A.create(C.sealed_sha256(), C.SEAL_REVISION,
                        args.owner_decision)
    except A.AuthorizationError as exc:
        print("AUTHORIZATION REFUSED: %s" % exc)
        return EXIT_REFUSED
    print("AUTHORIZATION CREATED")
    print("  authorization_id : %s" % auth["authorization_id"])
    print("  sealed bytes     : %s" % auth["sealed_prereg_sha256"][:16])
    print("  seal revision    : %s" % auth["seal_revision"])
    print("  single use       : YES — one run, then permanently consumed")
    return EXIT_OK


def cmd_execute(args):
    """The S3 entry point.

    guard -> validate exactly one active authorization -> execute once ->
    consume -> refuse reuse. Without a valid authorization it refuses BEFORE any
    target calculation, which is what it did as a pure stub and still does.
    """
    import value_authorization as A
    import value_evidence as EV
    import value_orchestrator as O

    sealed = C.sealed_sha256()
    if sealed != C.SEALED_PREREG_SHA256:
        print("VALUE EXECUTION OUTCOME: EXECUTION_REFUSED")
        print("  refusal_stage  : sealed contract identity")
        print("  refusal_reason : the contract on disk is not the sealed one")
        print("  target calculations executed: NONE")
        return EXIT_REFUSED

    try:
        auth = A.validate_active(sealed, C.SEAL_REVISION)
    except A.AuthorizationError as exc:
        print("VALUE EXECUTION OUTCOME: EXECUTION_REFUSED")
        print("  refusal_stage  : authorization")
        print("  refusal_reason : %s" % exc)
        print("  target calculations executed: NONE")
        print("  artifact       : none")
        return EXIT_REFUSED

    run_id = getattr(args, "run_id", None) or (
        "VALUE_S3_RUN_" + auth["authorization_id"].split("_")[-1])
    out_path = getattr(args, "out", None) or os.path.join(
        HERE, "VALUE_EVIDENCE.json")
    if os.path.exists(out_path):
        print("VALUE EXECUTION OUTCOME: EXECUTION_REFUSED")
        print("  refusal_stage  : evidence artifact")
        print("  refusal_reason : %s already exists and is never overwritten"
              % out_path)
        print("  target calculations executed: NONE")
        return EXIT_REFUSED

    # Spend the authorization BEFORE the study runs. A crash must not leave a
    # spendable authorization behind and quietly permit a second attempt.
    A.consume(auth, run_id)

    try:
        ev = O.run_study(run_id=run_id,
                         authorization_id=auth["authorization_id"],
                         outcome_exposure_state=args.exposure_state)
        EV.write(ev, out_path)
    except Exception as exc:                       # noqa: BLE001
        print("VALUE EXECUTION OUTCOME: EXECUTION_FAILED")
        print("  authorization  : %s (CONSUMED — not restored)"
              % auth["authorization_id"])
        print("  run_id         : %s" % run_id)
        print("  failure        : %s: %s" % (type(exc).__name__, exc))
        print("  artifact       : none")
        return EXIT_FAIL

    print("VALUE EXECUTION OUTCOME: EXECUTION_COMPLETED")
    print("  run_id            : %s" % run_id)
    print("  authorization_id  : %s (CONSUMED)" % auth["authorization_id"])
    print("  sealed bytes      : %s" % sealed[:16])
    print("  evaluation window : %s .. %s  N=%d"
          % (ev["EVALUATION_START"], ev["EVALUATION_END"], ev["N"]))
    print("  evidence artifact : %s" % out_path)
    print("  schema validation : PASS")
    print("  outcome exposure  : %s" % ev["OUTCOME_EXPOSURE_STATE"])
    return EXIT_OK


def cmd_status(_args):
    import value_authorization as A
    print(A.status_line())
    ev = os.path.join(HERE, "VALUE_EVIDENCE.json")
    print("REAL_EVIDENCE_ARTIFACT_CREATED = %s"
          % ("YES  (%s)" % ev if os.path.exists(ev) else "NO"))
    return EXIT_OK


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("conformance").set_defaults(func=cmd_conformance)
    sub.add_parser("validate").set_defaults(func=cmd_validate)
    sub.add_parser("status").set_defaults(func=cmd_status)

    au = sub.add_parser("authorize", help="OWNER ACT — mint one single-use "
                                          "S3 authorization")
    au.add_argument("--owner-decision", dest="owner_decision", required=True)
    au.set_defaults(func=cmd_authorize)

    ex = sub.add_parser("execute", help="S3 real run — needs an authorization")
    ex.add_argument("--run-id", dest="run_id")
    ex.add_argument("--out", dest="out")
    ex.add_argument("--exposure-state", dest="exposure_state",
                    default="GENERATED_NOT_SEEN")
    ex.set_defaults(func=cmd_execute)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
