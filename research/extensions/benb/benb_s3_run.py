"""CTA-EDGE-02-BENB — the S3 SINGLE GOVERNED HISTORICAL RUN driver.

This is the ONE process invocation the Owner grant authorises. It is written and
committed BEFORE the grant is exercised, so the code that touches the outcome is fixed
in committed bytes before any outcome exists.

    python research/extensions/benb/benb_s3_run.py --execute

Phases, in order, and the phase boundary matters:

  PHASE 0  GRANT      read the single-use grant from COMMITTED state and check every
                      bound identity: lineage, run_id, rng_seed, S1 seal manifest
                      sha256, S2 implementation commit. No data is opened here.
  PHASE 1  LEVEL-1    verify the seven pinned file identities, load the panels through
                      the guarded RealCellSource, and reproduce the SEALED STRUCTURAL
                      eligibility counts. NO basis, NO feature, NO outcome is computed
                      in this phase, so an abort here spends no trial.
  PHASE 2  GOVERNED   the sealed computation: feature, decomposition, Gate 1, Gate 2,
                      monthly P&L, ONE bootstrap, LOYO, LQD secondary, classification.
                      Crossing into this phase is what spends the trial.

Nothing in this file may choose, tune, threshold, filter or interpret. Every definition
comes from the sealed contract through `benb_contract` and the S2 modules; this driver
only sequences them, checks the grant, and writes the artifact.
"""

from __future__ import annotations

import argparse
import collections
import datetime as _dt
import hashlib
import json
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
os.chdir(REPO)

import benb_authorization as auth          # noqa: E402
import benb_contract as K                  # noqa: E402
import benb_data as bdata                  # noqa: E402
import benb_engine as beng                 # noqa: E402
import benb_feature as bfeat               # noqa: E402
import benb_inference as binf              # noqa: E402
import benb_pipeline as bpipe              # noqa: E402
import benb_report as brep                 # noqa: E402

RUN_ID = "BENB-RUN-20260915-01"
AUTHORIZATION_ID = "BENB-AUTH-0001"
RNG_SEED = 1788924436

S3_DIR = os.path.join(K.BENB_DIR, "s3")
RESULT_PATH = os.path.join(S3_DIR, "BENB_S3_RESULT.json")
FACTS_PATH = os.path.join(S3_DIR, "BENB_S3_FEATURE_REALISATION.json")


class MechanicalFailure(RuntimeError):
    """A pre-run or in-run mechanical failure. Never converted into a verdict."""


def rule(title):
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def sha256_of(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def git(*args):
    out = subprocess.run(["git", *args], cwd=REPO, capture_output=True, check=False)
    return out.stdout.decode("utf-8", "replace").strip() if out.returncode == 0 else ""


# --------------------------------------------------------------------------- #
# PHASE 0 — the grant                                                          #
# --------------------------------------------------------------------------- #


def phase0_grant():
    rule("PHASE 0 — THE SINGLE-USE OWNER GRANT (committed state only)")
    grant = auth.active_execution_authorization("EXECUTION")
    if grant is None:
        raise MechanicalFailure(
            "no single active BENB EXECUTION grant in committed state; refusing")
    b = grant.get("binding", {})
    checks = [
        ("authorization_id", grant.get("authorization_id"), AUTHORIZATION_ID),
        ("lineage", b.get("lineage"), K.LINEAGE),
        ("run_id", b.get("run_id"), RUN_ID),
        ("rng_seed", b.get("rng_seed"), RNG_SEED),
        ("s1_seal_manifest_sha256", b.get("s1_seal_manifest_sha256"),
         K.SEAL_MANIFEST_SHA256),
        ("sealed_prereg_sha256", b.get("sealed_prereg_sha256"),
         K.SEALED_PREREG_SHA256),
        ("s2_implementation_commit", b.get("s2_implementation_commit"),
         "d1ccefc8c6ed6e15e6366856ff0b64a0f6516bc3"),
        ("scope", grant.get("scope"), "ONE_SHOT_SINGLE_OUTCOME_BEARING_RUN"),
        ("status", grant.get("status"), "AUTHORIZED"),
    ]
    bad = []
    for name, got, want in checks:
        ok = got == want
        bad += [] if ok else [(name, got, want)]
        print(f"  {'OK  ' if ok else 'FAIL'} {name:<26} {got}")
    if bad:
        raise MechanicalFailure(f"grant binding mismatch: {bad}")
    # the guard itself must recognise this exact run_id
    auth.require_run_authorization(auth.REAL, RUN_ID)
    print(f"  OK   guard recognises {RUN_ID} under {AUTHORIZATION_ID}")
    if os.path.exists(RESULT_PATH):
        raise MechanicalFailure(
            f"{RESULT_PATH} already exists: a governed result is already on disk and "
            f"this grant is ONE_SHOT. Refusing a second execution.")
    print("  OK   no prior governed BENB result artifact exists")
    return grant


# --------------------------------------------------------------------------- #
# PHASE 1 — LEVEL-1 pre-run integrity. No feature, no outcome.                  #
# --------------------------------------------------------------------------- #


def phase1_level1():
    rule("PHASE 1 — LEVEL-1 PRE-RUN INTEGRITY (no basis, no feature, no outcome)")
    hashes = {}
    for name, want in sorted(K.PINNED.items()):
        got = sha256_of(os.path.join(K.DATA_DIR, name))
        hashes[name] = got
        ok = got == want
        print(f"  {'OK  ' if ok else 'FAIL'} {name:<32} {got[:16]}...")
        if not ok:
            raise MechanicalFailure(
                f"LEVEL-1 FAILURE: {name} sha256 {got} != sealed pin {want}. "
                f"Refusing to substitute a new download.")
    for name in ("BENB_PREREGISTRATION.md", "BENB_SEAL_MANIFEST.md"):
        got = sha256_of(os.path.join(K.BENB_DIR, name))
        want = (K.SEALED_PREREG_SHA256 if "PREREG" in name
                else K.SEAL_MANIFEST_SHA256)
        hashes[name] = got
        if got != want:
            raise MechanicalFailure(f"LEVEL-1 FAILURE: {name} seal hash changed")
        print(f"  OK   {name:<32} {got[:16]}...")

    source = bdata.RealCellSource(run_id=RUN_ID)      # the guard runs inside here
    cells, structural = {}, {}
    for ticker in (K.PRIMARY_TICKER, K.SECONDARY_TICKER):
        cell = source.load(ticker)
        cell.validate()
        elig = bdata.eligibility(cell)
        cells[ticker] = (cell, elig)
        structural[ticker] = {
            "common_grid_dates": len(cell.grid),
            "sealed_common": K.STRUCTURAL_COMMON[ticker],
            "eligible": len(elig.eligible),
            "sealed_eligible": K.STRUCTURAL_ELIGIBLE[ticker],
            "excluded_burn_in": len(elig.excluded_burn_in),
            "excluded_no_next": len(elig.excluded_no_next),
            "excluded_ex_date": len(elig.excluded_ex_date),
            "first_date": str(cell.grid[0]), "last_date": str(cell.grid[-1]),
            "ex_dates_in_union": len(cell.ex_dates),
        }
        s = structural[ticker]
        print(f"\n  {ticker}")
        print(f"    common grid dates      {s['common_grid_dates']:>6}   "
              f"sealed {s['sealed_common']:>6}   "
              f"{'MATCH' if s['common_grid_dates'] == s['sealed_common'] else 'MISMATCH'}")
        print(f"    structurally eligible  {s['eligible']:>6}   "
              f"sealed {s['sealed_eligible']:>6}   "
              f"{'MATCH' if s['eligible'] == s['sealed_eligible'] else 'MISMATCH'}")
        print(f"    excluded: burn-in {s['excluded_burn_in']}  "
              f"no-next {s['excluded_no_next']}  ex-date {s['excluded_ex_date']}")
        print(f"    span {s['first_date']} .. {s['last_date']}")
        if s["common_grid_dates"] != s["sealed_common"]:
            raise MechanicalFailure(
                f"LEVEL-1 FAILURE: {ticker} common-grid count "
                f"{s['common_grid_dates']} != sealed {s['sealed_common']}")
        if s["eligible"] != s["sealed_eligible"]:
            raise MechanicalFailure(
                f"LEVEL-1 FAILURE: {ticker} structural eligibility "
                f"{s['eligible']} != sealed {s['sealed_eligible']}. STOPPING BEFORE "
                f"ANY FEATURE IS COMPUTED — no outcome exists and no trial is spent.")
    print("\n  LEVEL-1: PASS. Nothing outcome-bearing has been computed yet.")
    return source, cells, structural, hashes


# --------------------------------------------------------------------------- #
# PHASE 2 — the governed computation                                           #
# --------------------------------------------------------------------------- #


def feature_realisation_facts(cell, elig, obs):
    """Section 6 of the run brief. Mechanical tabulation, no interpretation."""
    rows = bfeat.features(cell)
    disc = bfeat.discount_rows(rows, elig.eligible)
    prem = bfeat.premium_rows(rows, elig.eligible)
    by_year = collections.Counter(o.date.year for o in obs)
    by_entry_month = collections.Counter(o.entry_month for o in obs)
    by_month_of_year = collections.Counter(o.date.month for o in obs)
    months = sorted(by_entry_month)
    grid = beng.month_grid(months[0], months[-1]) if months else []
    zero_months = [m for m in grid if by_entry_month.get(m, 0) == 0]
    n_elig = len(elig.eligible)
    return {
        "structurally_eligible": n_elig,
        "discount_observations": len(disc),
        "premium_observations": len(prem),
        "discount_percent_of_eligible": (100.0 * len(disc) / n_elig) if n_elig else None,
        "first_signal_date": str(min(o.date for o in obs)) if obs else None,
        "last_signal_date": str(max(o.date for o in obs)) if obs else None,
        "calendar_years_represented": len(by_year),
        "calendar_years": sorted(by_year),
        "signals_by_calendar_year": {str(y): by_year[y] for y in sorted(by_year)},
        "signals_by_month_of_year": {str(m): by_month_of_year.get(m, 0)
                                     for m in range(1, 13)},
        "signals_by_entry_month": {m: by_entry_month.get(m, 0) for m in grid},
        "month_grid_length": len(grid),
        "zero_signal_months": len(zero_months),
        "zero_signal_month_list": zero_months,
        "max_signals_in_one_entry_month": max(by_entry_month.values()) if obs else 0,
        "max_signal_entry_month": (max(by_entry_month, key=by_entry_month.get)
                                   if obs else None),
        "severity_min": min(o.d for o in obs) if obs else None,
        "severity_max": max(o.d for o in obs) if obs else None,
        "severity_mean": (sum(o.d for o in obs) / len(obs)) if obs else None,
    }


def identity_check(cell, obs_dates):
    """The sealed three-component identity, re-verified on every used observation."""
    idx = {d: i for i, d in enumerate(cell.grid)}
    worst, worst_date = 0.0, None
    for d in obs_dates:
        dec = beng.decompose(cell, d, cell.grid[idx[d] + 1])
        r = abs(dec.identity_residual)
        if r > worst:
            worst, worst_date = r, d
    return worst, worst_date


def phase2_governed(source, cells, rng):
    rule("PHASE 2 — THE GOVERNED COMPUTATION  (the trial is spent here)")
    results, facts, identity = {}, {}, {}
    for ticker, role in ((K.PRIMARY_TICKER, K.PRIMARY_CELL),
                         (K.SECONDARY_TICKER, K.SECONDARY_CELL)):
        cell, elig = cells[ticker]
        print(f"\n  {ticker} ({role}) — bootstrap B = {K.BOOTSTRAP_B:,}")
        try:
            res = bpipe.run_cell(source, ticker, role, b=K.BOOTSTRAP_B, rng=rng)
        except AssertionError as exc:
            raise MechanicalFailure(f"{ticker}: decomposition identity failed: {exc}")
        results[ticker] = res
        facts[ticker] = feature_realisation_facts(cell, elig, res.obs)
        worst, worst_date = identity_check(cell, [o.date for o in res.obs])
        identity[ticker] = {"max_abs_residual": worst, "at": str(worst_date),
                            "tolerance": 1e-12,
                            "n_checked": len(res.obs)}
        print(f"    discount observations {res.n_discount:>6}   "
              f"premium {res.n_premium:>6}   years {res.years_with_discount}")
        print(f"    identity max |residual| {worst:.3e} over {len(res.obs)} obs")
        if res.defects:
            print(f"    DEFECTS: {res.defects}")
    return results, facts, identity


# --------------------------------------------------------------------------- #


def report_primary(res, verdict, facts):
    rule("HYG PRIMARY — SEALED STATISTICS")
    b = res.boot
    f = facts
    print(f"  structurally eligible        {f['structurally_eligible']:,}")
    print(f"  discount observations        {f['discount_observations']:,}"
          f"   ({f['discount_percent_of_eligible']:.2f} % of eligible)")
    print(f"  premium observations         {f['premium_observations']:,}")
    print(f"  signal span                  {f['first_signal_date']} .. "
          f"{f['last_signal_date']}")
    print(f"  calendar years represented   {f['calendar_years_represented']}")
    print(f"  month grid                   {f['month_grid_length']} months, "
          f"{f['zero_signal_months']} with zero signals")
    print(f"  max signals in one month     {f['max_signals_in_one_entry_month']}"
          f" ({f['max_signal_entry_month']})")
    print(f"\n  GATE 1 (95 % calendar-year block bootstrap, B = {b.replicates:,})")
    for name, iv in (("beta_T", b.beta_T), ("beta_O", b.beta_O), ("beta_N", b.beta_N)):
        print(f"    {name}   {iv.point:12.4f}   [{iv.lower:12.4f}, {iv.upper:12.4f}]")
    print(f"    GATE1_PASS (L_T > 0)  {b.beta_T.lower > 0.0}")
    print(f"\n  GATE 2")
    print(f"    mean NET_TRADE_RETURN  {b.mean_net.point:10.4f} bps   "
          f"[{b.mean_net.lower:10.4f}, {b.mean_net.upper:10.4f}]")
    print(f"    M1_PASS (L_R > 0)      {b.mean_net.lower > K.M1_RETURN_FLOOR_BPS}")
    print(f"    calendarised Sharpe    {b.sharpe.point:10.4f}       "
          f"[{b.sharpe.lower:10.4f}, {b.sharpe.upper:10.4f}]")
    print(f"    M2_PASS (L_S > +0.30)  {b.sharpe.lower > K.M2_SHARPE}")
    print(f"\n  LOYO   passes {res.loyo.passes}   "
          f"min beta_T {res.loyo.min_beta_T:.4f} (dropping {res.loyo.min_year})")
    for y, v in sorted(res.loyo.per_year_beta_T.items()):
        print(f"    drop {y}   beta_T {v:12.4f}")
    print(f"\n  FINAL_CLASS       {verdict.klass}   {verdict.title}")
    print(f"  RESEARCH_STATUS   {verdict.research_status}")
    print(f"  QUALIFIER         {verdict.qualifier}")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--execute", action="store_true",
                    help="perform the single governed historical run")
    args = ap.parse_args(argv)
    if not args.execute:
        print("refusing to run without --execute (this grant is ONE_SHOT)")
        return 2

    print(f"CTA-EDGE-02-BENB  S3 GOVERNED HISTORICAL RUN")
    print(f"  run_id {RUN_ID}   authorization {AUTHORIZATION_ID}   seed {RNG_SEED}")
    started = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    grant = phase0_grant()
    source, cells, structural, hashes = phase1_level1()

    rng = np.random.Generator(np.random.PCG64(np.random.SeedSequence(RNG_SEED)))
    results, facts, identity = phase2_governed(source, cells, rng)

    primary = results[K.PRIMARY_TICKER]
    secondary = results[K.SECONDARY_TICKER]
    verdict = bpipe.classify_primary(primary, hashes_ok=True)
    report_primary(primary, verdict, facts[K.PRIMARY_TICKER])

    rule("LQD SECONDARY — REPORTED ALONGSIDE, NO RESCUE POWER")
    sb = secondary.boot
    print(f"  discount observations {secondary.n_discount:,}   "
          f"years {secondary.years_with_discount}")
    for name, iv in (("beta_T", sb.beta_T), ("beta_O", sb.beta_O),
                     ("beta_N", sb.beta_N)):
        print(f"    {name}   {iv.point:12.4f}   [{iv.lower:12.4f}, {iv.upper:12.4f}]")
    print(f"    mean NET  {sb.mean_net.point:10.4f} bps   "
          f"[{sb.mean_net.lower:10.4f}, {sb.mean_net.upper:10.4f}]")
    print(f"    Sharpe    {sb.sharpe.point:10.4f}       "
          f"[{sb.sharpe.lower:10.4f}, {sb.sharpe.upper:10.4f}]")
    print("  PROMOTION_POWER = NONE   RESCUE_POWER = NONE")

    finished = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    sec_summary = bpipe.secondary_summary(secondary)
    sec_summary["beta_O"] = sb.beta_O.as_dict()
    sec_summary["beta_N"] = sb.beta_N.as_dict()
    sec_summary["mean_net_trade_return_bps"] = sb.mean_net.as_dict()
    sec_summary["calendarised_sharpe"] = sb.sharpe.as_dict()
    sec_summary["loyo_beta_T"] = secondary.loyo.as_dict()
    sec_summary["years_with_discount"] = secondary.years_with_discount
    sec_summary["premium_observations"] = secondary.n_premium

    doc = brep.build_result(
        data_kind="REAL", verdict=verdict, primary=primary,
        secondary_summary=sec_summary, run_authorization_id=AUTHORIZATION_ID,
        extra={
            "HISTORICAL_OUTCOME_EXPOSED": "YES",
            "run_id": RUN_ID,
            "rng_seed": RNG_SEED,
            "rng_stream": ("one numpy PCG64 stream seeded with the grant's rng_seed, "
                           "consumed HYG PRIMARY first then LQD SECONDARY, so the "
                           "primary result does not depend on the secondary running"),
            "bootstrap_replicates": K.BOOTSTRAP_B,
            "execution_commit_at_start": git("rev-parse", "HEAD"),
            "s2_implementation_commit": grant["binding"]["s2_implementation_commit"],
            "authorization_scope": grant.get("scope"),
            "started_utc": started, "finished_utc": finished,
            "input_hashes": hashes,
            "structural_pre_run_check": structural,
            "decomposition_identity": identity,
            "feature_realisation": facts[K.PRIMARY_TICKER],
            "feature_realisation_secondary": facts[K.SECONDARY_TICKER],
            "premium_side_descriptives": {
                "hyg_premium_eligible_observations": primary.n_premium,
                "lqd_premium_eligible_observations": secondary.n_premium,
                "note": ("The sealed contract makes the premium side DESCRIPTIVE_ONLY "
                         "and enumerates no premium statistic. The accepted S2 "
                         "implementation emits the eligible count and nothing else, so "
                         "the count and nothing else is reported here. Inventing a "
                         "premium statistic after the seal would be a design change."),
                "promotion_power": "NONE", "rescue_power": "NONE"},
            "gate_results": {
                "GATE1_PASS": bool(primary.boot.beta_T.lower > 0.0),
                "M1_PASS": bool(primary.boot.mean_net.lower > K.M1_RETURN_FLOOR_BPS),
                "M2_PASS": bool(primary.boot.sharpe.lower > K.M2_SHARPE),
                "LOYO_PASS": bool(primary.loyo.passes)},
            "sample_reuse": {
                "etf_price_leg": "BURNED / REUSED CONTEXT (KB-1, 6 of 6)",
                "nav_leg": "NEW external historical source",
                "overall": "DEPENDENT / MIXED PROVENANCE",
                "n_trials": ("NOT ASSERTED; D-ETF-COUNT remains "
                             "UNKNOWN_PENDING_AARON_DECISION"),
                "hypothesis_family": "F-BENB, m = 1"},
        })
    chk = brep.validate_result(doc)
    if not chk["ok"]:
        raise MechanicalFailure(f"result artifact invalid: {chk['problems']}")
    info = brep.write_result(doc, RESULT_PATH)
    os.makedirs(S3_DIR, exist_ok=True)
    with open(FACTS_PATH, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"run_id": RUN_ID, "HYG": facts[K.PRIMARY_TICKER],
                   "LQD": facts[K.SECONDARY_TICKER]}, fh, indent=1, sort_keys=True)
        fh.write("\n")

    rule("ARTIFACT")
    print(f"  {info['path']}")
    print(f"  sha256 {info['sha256']}")
    print(f"  {FACTS_PATH}")
    print(f"  sha256 {sha256_of(FACTS_PATH)}")
    print(f"\n  HISTORICAL_OUTCOME_EXPOSED = YES")
    print(f"  EVIDENCE_CEILING = {K.EVIDENCE_CEILING}  (never independently confirmed)")
    print(f"  EXECUTION_COUNT = 1")
    print(f"\n  FINAL_CLASS = {verdict.klass}   "
          f"PROGRAMME_STATUS = {verdict.research_status}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except MechanicalFailure as exc:
        print(f"\nMECHANICAL FAILURE — STOPPING BEFORE A SCIENTIFIC VERDICT:\n  {exc}")
        raise SystemExit(3)
