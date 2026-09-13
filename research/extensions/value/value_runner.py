# -*- coding: utf-8 -*-
"""Value CLI. The S3 real-run entry point exists but is CLOSED.

    conformance   prove the implementation constants match the sealed contract
    validate      schema / date / provenance / causal-availability checks only
    execute       the S3 real run — REFUSES; no authorization mechanism exists

`execute` is deliberately a refusal today. S2 builds the study; running it is a
separate Owner decision, and there is no authorization record to spend.
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

VALUE_EXECUTION_AUTHORIZED = False    # S3 only; flipping this is not a code change
AUTHORIZATION_MECHANISM_NOTE = (
    "No Value execution-authorization mechanism exists. S2 builds the study; a "
    "real run requires a separate explicit Owner decision, which has not been "
    "made and for which no record exists.")


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
    ck("no Value execution authorization exists",
       VALUE_EXECUTION_AUTHORIZED is False)
    print("  VALUE_TARGET_RETURNS_COMPUTED = NO")
    print("  VALUE_SHARPE_COMPUTED = NO")
    print("  VALUE_TSMOM_CORRELATION_COMPUTED = NO")
    print("  COMBINATION_OUTCOME_COMPUTED = NO")
    print()
    print("VALUE_DATA_VALIDATION =", "PASS" if ok else "FAIL")
    return EXIT_OK if ok else EXIT_FAIL


def cmd_execute(args):
    """The S3 entry point. It refuses, and refusing is its whole job today."""
    print("VALUE EXECUTION OUTCOME: EXECUTION_REFUSED")
    print("  refusal_stage          : authorization")
    print("  refusal_reason         : %s" % AUTHORIZATION_MECHANISM_NOTE)
    print("  run_id                 : %s" % getattr(args, "run_id", None))
    print("  target constructor calls: 0")
    print("  artifact               : none")
    return EXIT_REFUSED


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("conformance").set_defaults(func=cmd_conformance)
    sub.add_parser("validate").set_defaults(func=cmd_validate)
    ex = sub.add_parser("execute", help="S3 real run — refuses")
    ex.add_argument("--run-id", dest="run_id")
    ex.add_argument("--authorization-id", dest="authorization_id")
    ex.set_defaults(func=cmd_execute)
    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
