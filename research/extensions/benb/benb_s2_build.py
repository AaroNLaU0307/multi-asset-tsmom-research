"""CTA-EDGE-02-BENB — the S2 build driver.

SYNTHETIC ONLY. This script never loads a historical price or NAV value: it verifies
the seal, verifies the PINNED FILE IDENTITIES (bytes hashed, never parsed), demonstrates
that the hard run guard refuses a REAL run, exercises the sealed pipeline end to end on
the four synthetic economic worlds, and writes ONE example S3 result artifact stamped
`SYNTHETIC_ONLY = YES`.

    python research/extensions/benb/benb_s2_build.py [--b 2000] [--production-b]

Nothing here is a research result. A synthetic world's class is a property of the
fixture that was constructed, not of HYG.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
os.chdir(REPO)

import benb_authorization as auth          # noqa: E402
import benb_contract as K                  # noqa: E402
import benb_data as bdata                  # noqa: E402
import benb_fixtures as fx                 # noqa: E402
import benb_pipeline as bpipe              # noqa: E402
import benb_report as brep                 # noqa: E402

SEED = 20260915
HEADLINE_WORLD = "TRADABLE_CONVERGENCE"
EXAMPLE_PATH = os.path.join(K.BENB_DIR, "BENB_SYNTHETIC_EXAMPLE_RESULT.json")

WORLD_EXPECTATION = {
    "STALE_NAV": "beta_N supported negative; beta_T not supported; never harvestable",
    "OVERNIGHT_DISCOVERY": "beta_O supported positive; the move happens before entry",
    "TRADABLE_CONVERGENCE": "beta_T supported positive; the only world reaching Gate 2",
    "MIXED": "beta_O positive AND beta_N negative with beta_T unsupported",
}


def rng():
    return np.random.Generator(np.random.PCG64(np.random.SeedSequence(SEED)))


def sha256_of(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def rule(title):
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


# --------------------------------------------------------------------------- #


def verify_seal():
    rule("1. SEAL VERIFICATION")
    rows = [
        ("BENB_PREREGISTRATION.md",
         sha256_of(os.path.join(K.BENB_DIR, "BENB_PREREGISTRATION.md")),
         K.SEALED_PREREG_SHA256),
        ("BENB_SEAL_MANIFEST.md",
         sha256_of(os.path.join(K.BENB_DIR, "BENB_SEAL_MANIFEST.md")),
         K.SEAL_MANIFEST_SHA256),
    ]
    ok = True
    for name, got, want in rows:
        match = got == want
        ok = ok and match
        print(f"  {'OK  ' if match else 'FAIL'} {name}")
        print(f"       sha256 {got}")
    print(f"  seal commit {K.SEAL_COMMIT}")
    return ok


def verify_pinned_identities():
    rule("2. PINNED DATA IDENTITIES  (bytes hashed, never parsed)")
    ok = True
    for name, want in sorted(K.PINNED.items()):
        path = os.path.join(K.DATA_DIR, name)
        if not os.path.exists(path):
            print(f"  MISS {name}  (git-ignored and absent in this checkout)")
            ok = False
            continue
        got = sha256_of(path)
        match = got == want
        ok = ok and match
        print(f"  {'OK  ' if match else 'FAIL'} {name}  {got[:16]}...")
    print("  NOTE: file identity only. No price, NAV, basis or date was read here.")
    return ok


def show_run_guard():
    rule("3. HARD RUN GUARD  (S2 must be unable to execute a REAL run)")
    st = auth.authorization_status()
    print(f"  ledger                         {st['ledger']}")
    print(f"  active EXECUTION grants        {st['active_execution_authorizations']}")
    print(f"  real_run_authorized            {st['real_run_authorized']}")
    try:
        bdata.RealCellSource(run_id="BENB-RUN-0001")
    except auth.RunNotAuthorized as exc:
        print(f"  RealCellSource()               REFUSED -> {type(exc).__name__}")
        print(f"    {str(exc).splitlines()[0]}")
        return True
    print("  RealCellSource()               *** NOT REFUSED — BUILD BLOCKER ***")
    return False


def run_world(name, b, n=300):
    cell = fx.build_world(**fx.WORLDS[name], n_signals=n, noise=0.00004, seed=3)
    src = fx.source(cell)
    bdata.assert_synthetic(src)
    t0 = time.time()
    res = bpipe.run_cell(src, cell.ticker, "PRIMARY", b=b, rng=rng())
    verdict = bpipe.classify_primary(res)
    return res, verdict, time.time() - t0


def exercise_worlds(b):
    rule(f"4. SYNTHETIC ECONOMIC WORLDS  (B = {b:,})")
    out = {}
    for name in ("STALE_NAV", "OVERNIGHT_DISCOVERY", "TRADABLE_CONVERGENCE", "MIXED"):
        res, v, secs = run_world(name, b)
        bt, bo, bn = res.boot.beta_T, res.boot.beta_O, res.boot.beta_N
        out[name] = (res, v)
        print(f"\n  {name}")
        print(f"    expectation   {WORLD_EXPECTATION[name]}")
        print(f"    n_discount {res.n_discount:>5}   n_premium {res.n_premium:>5}   "
              f"years {res.years_with_discount}   months {len(res.month_grid)}")
        print(f"    beta_T   {bt.point:12.2f}  [{bt.lower:12.2f}, {bt.upper:12.2f}]")
        print(f"    beta_O   {bo.point:12.2f}  [{bo.lower:12.2f}, {bo.upper:12.2f}]")
        print(f"    beta_N   {bn.point:12.2f}  [{bn.lower:12.2f}, {bn.upper:12.2f}]")
        print(f"    LOYO passes {res.loyo.passes}   "
              f"min beta_T {res.loyo.min_beta_T:.2f} in {res.loyo.min_year}")
        print(f"    CLASS {v.klass}  {v.title}")
        print(f"    research_status {v.research_status}   qualifier {v.qualifier!r}")
        print(f"    ({secs:.1f}s)")
    return out


def exercise_no_rescue(b):
    rule("5. FIREWALLS  (LQD and the premium side carry no rescue power)")
    src = fx.source(
        fx.build_world(**fx.WORLDS["STALE_NAV"], n_signals=300, noise=0.00004,
                       seed=3, ticker="HYG"),
        fx.build_world(**fx.WORLDS["TRADABLE_CONVERGENCE"], n_signals=300,
                       noise=0.00004, seed=3, ticker="LQD"))
    p = bpipe.run_cell(src, "HYG", "PRIMARY", b=b, rng=rng())
    s = bpipe.run_cell(src, "LQD", "SECONDARY", b=b, rng=rng())
    v = bpipe.classify_primary(p)
    summary = bpipe.secondary_summary(s)
    print(f"  HYG (primary, stale-NAV world)   beta_T lower "
          f"{p.boot.beta_T.lower:.2f}   CLASS {v.klass}")
    print(f"  LQD (secondary, spectacular)     beta_T lower "
          f"{s.boot.beta_T.lower:.2f}   promotion_power "
          f"{summary['promotion_power']}  rescue_power {summary['rescue_power']}")
    print(f"  premium observations available   {p.n_premium}")
    print(f"  HYG verdict after both           CLASS {v.klass} / {v.research_status}")
    print("  classify_primary() takes the PRIMARY cell and nothing else.")
    return v, summary


def write_example(worlds, b, secondary_summary):
    rule("6. EXAMPLE S3 RESULT ARTIFACT  (SYNTHETIC_ONLY = YES)")
    res, verdict = worlds[HEADLINE_WORLD]
    doc = brep.build_result(
        data_kind=auth.SYNTHETIC, verdict=verdict, primary=res,
        secondary_summary=secondary_summary,
        extra={
            "example_artifact": True,
            "synthetic_world": f"SYNTHETIC_{HEADLINE_WORLD}_FIXTURE",
            "synthetic_world_note": (
                "Every number in this file is a property of a CONSTRUCTED FIXTURE. It "
                "is not a HYG result, not evidence about HYG, and not a backtest. The "
                "headline world is the one that populates every schema field, "
                "including the Gate-2 flags."),
            "bootstrap_replicates_used": b,
            "production_bootstrap_replicates": K.BOOTSTRAP_B,
        })
    chk = brep.validate_result(doc)
    if not chk["ok"]:
        print(f"  SCHEMA INVALID: {chk['problems']}")
        return None
    info = brep.write_result(doc, EXAMPLE_PATH)
    print(f"  wrote {info['path']}")
    print(f"  sha256 {info['sha256']}")
    print(f"  synthetic_only = {doc['synthetic_only']}   "
          f"run_authorization_id = {doc['run_authorization_id']}")
    print(f"  final_class = {doc['final_class']}   "
          f"research_status = {doc['research_status']}")
    print(f"  fields {len(doc)}   required {len(brep.REQUIRED_FIELDS)}")
    return info


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--b", type=int, default=2000,
                    help="bootstrap replicates for the synthetic worlds")
    ap.add_argument("--production-b", action="store_true",
                    help=f"use the sealed production B = {K.BOOTSTRAP_B:,}")
    args = ap.parse_args(argv)
    b = K.BOOTSTRAP_B if args.production_b else args.b

    print(f"CTA-EDGE-02-BENB  S2 BUILD DRIVER   lineage {K.LINEAGE}")
    print(f"SYNTHETIC ONLY. No real BENB outcome is computed or inspected.")

    seal_ok = verify_seal()
    pins_ok = verify_pinned_identities()
    guard_ok = show_run_guard()
    worlds = exercise_worlds(b)
    _, secondary = exercise_no_rescue(b)
    info = write_example(worlds, b, secondary)

    rule("SUMMARY")
    print(f"  seal verified                  {seal_ok}")
    print(f"  pinned identities reproduce    {pins_ok}")
    print(f"  REAL run refused at S2         {guard_ok}")
    for name, (_, v) in worlds.items():
        print(f"  {name:<22} CLASS {v.klass:<4} {v.research_status}")
    print(f"  example artifact               "
          f"{info['sha256'] if info else 'NOT WRITTEN'}")
    ok = seal_ok and pins_ok and guard_ok and info is not None
    print(f"\n  S2 BUILD DRIVER: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
