# -*- coding: utf-8 -*-
"""TSMOM-VRP-01 - S3 GOVERNED HISTORICAL STAGE-A RUN.

Four commands, deliberately separate processes so that GENERATE / PROTECT / VERIFY /
REVEAL is a structural boundary and not a convention:

    preflight   gates A-K. Prints gate results only. Touches no return.
    run         executes the ONE governed Stage-A run, stores the evidence in the VRP
                protected store as GENERATED_NOT_SEEN, prints INTEGRITY METADATA ONLY.
    verify      the post-compute integrity gate. Prints booleans, counts and hashes only.
    reveal      the SINGLE authorised reveal of the predeclared Stage-A evidence package.
                Requires a committed single-use Owner REVEAL grant.

NOTHING EXCEPT `reveal` MAY PRINT A SCIENTIFIC VALUE. `run` and `verify` never format a
monthly return, a mean, an interval bound, a classification or a descriptive.

Stage B is not implemented here, not imported here, and cannot be reached from here.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(PKG, "..", "..", ".."))
sys.path.insert(0, PKG)
os.chdir(REPO)

import vrp_ca_audit as vaudit        # noqa: E402
import vrp_calendar as vcal          # noqa: E402
import vrp_chain as vchain           # noqa: E402
import vrp_constants as K            # noqa: E402
import vrp_costs as vcosts           # noqa: E402
import vrp_inference as vinf         # noqa: E402
import vrp_raw as vraw               # noqa: E402
import vrp_reveal as vreveal         # noqa: E402
import vrp_sizing as vsizing         # noqa: E402
import vrp_specs as vspecs           # noqa: E402
import vrp_stage_a as vsa            # noqa: E402
import vrp_validators as vval        # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

RUN_ID = "VRP-STAGE-A-RUN-0001"
MANIFEST_JSON = os.path.join(REPO, "data", "vix", "manifests", "vrp_raw_manifest.json")
RUN_MANIFEST = os.path.join(HERE, "VRP_STAGE_A_RUN_MANIFEST.json")
PROTECTED_POINTER = os.path.join(HERE, "VRP_STAGE_A_PROTECTED_POINTER.json")

S1_SEAL = "16d84545ba1385a482dbac7e776b31275f6fa5f7"
S2_BUILD = "72499019ce9ef97f16d1ddf3b3982697a4e6c4cc"
S2_CLOSURE = "f196cfdc3a866f64ca8d12d5b91bd9433b327d06"
ERRATUM_SHA = "b8a089ac2f1d3f26d0493684bb3512cfe564b4f82d49690c3b7daa77b28e8f1a"
DGS3MO = os.path.join(REPO, "data", "DGS3MO.csv")

# The sealed window. Both endpoints are fixed by section K.1; the first month was fixed
# MECHANICALLY by section F.6 at S2A and is re-derived here, never assumed.
SEALED_FIRST_MONTH = "2006-09"
SEALED_LAST_MONTH = K.STAGE_A_LAST_MONTH          # "2026-08"
SEALED_MONTHS = 240

# Stage A is a RETURN-ON-COMMITTED-CAPITAL benchmark and r_A is EXACTLY invariant to K:
# VM scales linearly with K (q is proportional to S = 0.01K) and every component of the
# section G cost is pro-rated by fractional quantity, hence also linear in K. K_0 is the
# only committed capital the contract names in dollars (section H.1 at W0).
K_STAGE_A = K.s * K.W0                             # $200,000

# ---------------------------------------------------------------------------
# THE S3 STATE TRANSITION, ENUMERATED.
#
# Two accepted S2 validators contain assertions that were TRUE during S2 and that the
# Owner-authorised S3 execution grant NECESSARILY makes false - exactly the same class as
# the S1 validator's "no data/vix directory exists yet", one stage later:
#
#   * "no single-use Owner EXECUTION authorisation is committed"  - one now is;
#   * "the governed-run entry gate REFUSES a real run"            - it now admits Stage A;
#   * test_i21_no_execution_authorization_exists                  - same fact;
#   * test_i21_real_stage_a_is_refused_during_s2                  - Stage A is now authorised.
#
# NEITHER VALIDATOR IS MODIFIED AND NEITHER EXIT CODE IS RELABELLED. The gate below
# instead requires that these are the ONLY failures, so any OTHER regression still blocks
# the run. Stage B is deliberately NOT on this list: `test_i21_real_stage_b_is_refused...`
# must keep passing, and it does, because `require_run_authorization` is stage-scoped and
# VRP-AUTH-0001 carries `stage_b_authorized = false`.
EXPECTED_S3_STATE_FLIPS_POST_S2 = [
    "no single-use Owner EXECUTION authorisation is committed",
    "the governed-run entry gate REFUSES a real run",
]
EXPECTED_S3_STATE_FLIPS_TESTS = [
    "test_i21_no_execution_authorization_exists",
    "test_i21_real_stage_a_is_refused_during_s2",
]
POST_S2_EXPECTED_PASSES = 45      # 47 total minus the two enumerated S3-state flips

_ok = True
_gates = []


def ck(label, cond, detail=""):
    global _ok
    if not cond:
        _ok = False
    _gates.append({"check": label, "pass": bool(cond), "detail": str(detail)})
    print("  %-62s %s   %s" % (label, "PASS" if cond else "FAIL", detail))


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


# --------------------------------------------------------------------------- #
# shared loaders
# --------------------------------------------------------------------------- #
def load_chain():
    with open(MANIFEST_JSON, encoding="utf-8") as fh:
        manifest = json.load(fh)
    contracts, cross = vraw.load_contracts(manifest["contract_files"])
    cal = vraw.exchange_calendar_from(contracts)
    chain = vchain.build_chain(contracts, cal)
    return manifest, contracts, cal, chain


def sealed_window_days(chain):
    """The chain days of the sealed window, as Stage-A DayInput rows.

    The window is VERIFIED against the sealed endpoints; it is never silently shortened
    or extended.
    """
    months = sorted({vchain._month_key(r.date) for r in chain.days
                     if SEALED_FIRST_MONTH <= vchain._month_key(r.date) <= SEALED_LAST_MONTH})
    rows = [r for r in chain.days
            if SEALED_FIRST_MONTH <= vchain._month_key(r.date) <= SEALED_LAST_MONTH]
    last_session = {}
    for r in rows:
        last_session[vchain._month_key(r.date)] = r.date
    days = [vsa.DayInput(date=r.date, front_key=r.front_key, second_key=r.second_key,
                         w_front=r.w_front, w_second=r.w_second,
                         front_price=r.front_price, second_price=r.second_price,
                         month_end=(r.date == last_session[vchain._month_key(r.date)]))
            for r in rows]
    return months, days


def fm1_monthly_rf(calendar, months):
    """Section E.3 FM-1, reused verbatim: FRED DGS3MO, the last non-missing print on or
    before the DECISION DATE (the last exchange business day of month t-1), within a
    maximum lookback of 7 CALENDAR days, no fallback series, converted Y/100/12.

    Implemented here in the VRP package; the C-A implementation is never imported.
    Returns {month: rate or None}. A month with no print in the lookback is UNDEFINED and
    reported as such; the primary is unaffected.
    """
    prints = {}
    with open(DGS3MO, encoding="utf-8") as fh:
        header = fh.readline()
        for line in fh:
            parts = line.strip().split(",")
            if len(parts) < 2 or not parts[1] or parts[1] == ".":
                continue
            try:
                prints[_dt.date.fromisoformat(parts[0])] = float(parts[1])
            except ValueError:
                continue
    out = {}
    for m in months:
        y, mo = int(m[:4]), int(m[5:])
        py, pmo = (y - 1, 12) if mo == 1 else (y, mo - 1)
        try:
            decision = calendar.last_session_of_month(py, pmo)
        except KeyError:
            out[m] = None
            continue
        value = None
        for back in range(0, K.FM1_MAX_LOOKBACK_DAYS + 1):
            d = decision - _dt.timedelta(days=back)
            if d in prints:
                value = prints[d] / K.FM1_DIVISOR
                break
        out[m] = value
    return out


# --------------------------------------------------------------------------- #
# PREFLIGHT - gates A to K
# --------------------------------------------------------------------------- #
def cmd_preflight(_args) -> int:
    print("TSMOM-VRP-01 - S3 PRE-RUN GATES (A-K)")
    print("=" * 78)
    print("No return is computed in this command.")

    section("A. S1 / S2 ancestry")
    for label, commit in (("canonical base (main)", "d232d3361b23a9f64182c2ec8881284f0fc3b36e"),
                          ("S1 seal", S1_SEAL), ("S2 build", S2_BUILD),
                          ("S2 governance closure", S2_CLOSURE)):
        rc, _ = git("merge-base", "--is-ancestor", commit, "HEAD")
        ck("%s is an ancestor of HEAD" % label, rc == 0, commit[:12])
    _, main_head = git("rev-parse", "main")
    ck("main is unmoved at the canonical base",
       main_head == "d232d3361b23a9f64182c2ec8881284f0fc3b36e", main_head[:12])

    section("B. sealed-artifact hashes")
    ok, detail = vval.check_sealed_artifact_hashes()
    ck("all four sealed S1 artifacts byte-identical to the seal", ok, detail)

    section("C. mechanical erratum hash")
    erratum = os.path.join(PKG, "VRP_S1_MECHANICAL_ERRATUM_01.md")
    got = sha256_file(erratum) if os.path.isfile(erratum) else ""
    ck("VRP_S1_MECHANICAL_ERRATUM_01.md matches the authorised hash",
       got == ERRATUM_SHA, got[:16])
    src = open(os.path.join(PKG, "vrp_stage_a.py"), encoding="utf-8").read()
    ck("the engine implements the SIGNED VM convention of the erratum",
       "vm += q * STANDARD_MULTIPLIER" in src
       and "vm += -q * STANDARD_MULTIPLIER" not in src)

    section("D. post-S2 state-transition validator (S3-state transition accounted)")
    proc = subprocess.run([sys.executable,
                           os.path.join("research", "extensions", "vrp", "s2",
                                        "vrp_post_s2_validate.py")],
                          cwd=REPO, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    import re as _re
    # Read the validator's own JSON record rather than scraping stdout: its labels are
    # padded to a fixed width and the longest ones leave a single space before the verdict,
    # which a whitespace regex silently mis-parses.
    with open(os.path.join(REPO, "research", "extensions", "vrp", "s2",
                           "VRP_POST_S2_STATE_VALIDATION.json"), encoding="utf-8") as fh:
        d_rec = json.load(fh)
    d_fails = sorted(c["check"] for c in d_rec["checks"] if not c["pass"])
    d_passes = [c for c in d_rec["checks"] if c["pass"]]
    ck("post-S2 validator content checks still PASS",
       len(d_passes) == POST_S2_EXPECTED_PASSES,
       "%d PASS of %d" % (len(d_passes), len(d_rec["checks"])))
    ck("the ONLY post-S2 failures are the enumerated S3-state assertions",
       d_fails == sorted(EXPECTED_S3_STATE_FLIPS_POST_S2),
       "; ".join(d_fails) or "none")
    ck("the original S1 validator still reports 113 content checks PASS",
       d_rec["original_s1_content_checks_pass"] == 113
       and d_rec["original_s1_failing_checks"] == [d_rec["expected_state_failure"]],
       "exit %s" % d_rec["original_s1_validator_exit"])

    section("E. S2A data authority and raw hash re-verification")
    proc = subprocess.run([sys.executable,
                           os.path.join("research", "extensions", "vrp",
                                        "vrp_data_validate.py")],
                          cwd=REPO, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    ck("S2A data gate PASSES (raw hashes re-verified)", proc.returncode == 0,
       "exit %d" % proc.returncode)

    manifest, contracts, cal, chain = load_chain()
    months, days = sealed_window_days(chain)

    section("F. VRP-VALIDITY (mechanical, P&L-free)")
    ck("first eligible complete month is the sealed 2006-09",
       vchain.first_eligible_complete_month(chain, SEALED_LAST_MONTH) == SEALED_FIRST_MONTH,
       str(vchain.first_eligible_complete_month(chain, SEALED_LAST_MONTH)))
    ck("the eligible window is EXACTLY the sealed window",
       months and months[0] == SEALED_FIRST_MONTH and months[-1] == SEALED_LAST_MONTH,
       "%s..%s" % (months[0], months[-1]) if months else "empty")
    ck("month count is exactly %d" % SEALED_MONTHS, len(months) == SEALED_MONTHS,
       "%d months" % len(months))
    ck("the window contains no month at or after the cutoff %s" % K.cutoff,
       all(d.date < K.cutoff for d in days))
    ck("September 2026 is excluded", "2026-09" not in months)
    ck("months are contiguous with no gap month",
       all(_next_month(months[i]) == months[i + 1] for i in range(len(months) - 1)))
    worst = max(chain.months[m].max_carry_forward for m in months)
    ck("no month exceeds %d carry-forward days per contract" % K.MAX_CARRY_FORWARD_DAYS,
       worst <= K.MAX_CARRY_FORWARD_DAYS, "worst = %d" % worst)
    ck("every held contract has a settlement on every day of the window",
       all(d.front_price is not None and d.second_price is not None for d in days),
       "%d chain days" % len(days))
    ok, bad = vchain.weights_sum_to_one(chain)
    ck("roll weights sum to 1 within 1e-12", ok, ",".join(bad[:2]))
    ok, bad = vchain.front_zero_before_expiry(chain)
    ck("front weight is 0 on the last settlement before final settlement", ok)
    ok, bad = vchain.daily_transfer_is_uniform(chain)
    ck("daily transfer is exactly 1/dt", ok)
    ok, detail = vval.check_expiry_identity(contracts)
    ck("expiry identity holds for every expired contract", ok, detail)
    ok, detail = vval.check_calendar_consistency(cal, cal.days[0], K.stageB_end)
    ck("calendar consistency: zero unexplained differences", ok, detail)
    ok, detail = vval.check_no_last_trade_price()
    ck("official settlement only; no last-trade or SOQ on any primary path", ok)
    ok, gap = vspecs.covers_without_gaps(vspecs.VX_LISTING_DATE, K.cutoff)
    ck("specification break table covers the window with no gaps", ok, str(gap))

    section("G. VRP-IMPLEMENTABILITY")
    legs = [(("VX", _dt.date(2020, 1, 22)), 0.5, 1000.0),
            (("VX", _dt.date(2020, 2, 19)), 0.5, 1000.0)]
    holdings = vsizing.holdings_for(K_STAGE_A, legs)
    cond = vsizing.implementability_condition(K_STAGE_A, holdings)
    ck("stressed-margin gate (1-b)K >= R_J", cond["pass"] is True,
       "slack = 0.20*K")
    gran = vsizing.integer_granularity(K.s * K.W0)
    ck("integer granularity within +/-10 %% at the sealed research book", gran["pass"] is True,
       "%d standard / %d mini contracts, %.1f %% error"
       % (gran["standard_contracts"], gran["mini_contracts"], 100 * gran["best_rel_error"]))
    ck("stress identity Loss_J = 0.30*K",
       abs(vsizing.stress_loss(holdings) - 0.30 * K_STAGE_A) < 1e-6)

    section("H. C-A firewall audit")
    audit = vaudit.audit()
    ck("static C-A access audit PASSES", audit["pass"] is True,
       "%d files, %d findings" % (len(audit["files_audited"]), len(audit["findings"])))

    section("I. acceptance suite (S3-state transition accounted) and secret scan")
    proc = subprocess.run([sys.executable, "-m", "pytest",
                           os.path.join("research", "extensions", "vrp", "vrp_tests.py"),
                           "-q", "--no-header", "--tb=no", "-p", "no:cacheprovider"],
                          cwd=REPO, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    t_fails = sorted(set(_re.findall(r"vrp_tests\.py::(\S+)", proc.stdout)))
    ck("the ONLY acceptance-suite failures are the enumerated S3-state assertions",
       t_fails == sorted(EXPECTED_S3_STATE_FLIPS_TESTS),
       "; ".join(t_fails) or "none")
    m = _re.search(r"(\d+) failed, (\d+) passed", proc.stdout)
    ck("every other acceptance test still passes",
       bool(m) and int(m.group(1)) == len(EXPECTED_S3_STATE_FLIPS_TESTS),
       m.group(0) if m else proc.stdout.strip().splitlines()[-1:])
    sys.path.insert(0, PKG)
    import vrp_s2_accept as vaccept
    findings, scanned = vaccept.secret_scan()
    ck("secret scan clean", not findings, "%d files, %d finding(s)"
       % (scanned, len(findings)))

    section("J. reveal-control readiness")
    acc = vreveal.acceptance_log_all_pass()
    ck("acceptance log is committed and all items PASS", acc["ok"], acc.get("reason", ""))
    grant = vreveal.active_execution_authorization("EXECUTION")
    ck("a single-use Owner EXECUTION grant is committed",
       grant is not None, grant.get("authorization_id") if grant else "NONE")
    ck("no REVEAL grant is committed yet (reveal comes after verification)",
       vreveal.active_execution_authorization("REVEAL") is None)

    section("K. protected result store readiness")
    store = vreveal.PROTECTED_STORE
    ck("the VRP protected store is its own, never the C-A store",
       os.path.normpath(store).replace("\\", "/").endswith("data/vrp_protected"))
    ck("the protected store is EMPTY (no prior governed run)",
       (not os.path.isdir(store)) or not os.listdir(store),
       "%d file(s)" % (len(os.listdir(store)) if os.path.isdir(store) else 0))
    ck("the protected store path is git-ignored",
       git("check-ignore", "data/vrp_protected")[0] == 0
       or git("check-ignore", "data")[0] == 0)

    section("PRE-RUN GATE RESULT")
    print("  S3_PRE_RUN_GATES = %s   (%d PASS / %d FAIL)"
          % ("PASS" if _ok else "FAIL",
             sum(1 for g in _gates if g["pass"]), sum(1 for g in _gates if not g["pass"])))
    with open(os.path.join(HERE, "VRP_S3_PRERUN_GATES.json"), "w",
              encoding="utf-8", newline="\n") as fh:
        json.dump({"run_id": RUN_ID, "result": "PASS" if _ok else "FAIL",
                   "generated_utc": _dt.datetime.now(_dt.timezone.utc)
                   .strftime("%Y-%m-%dT%H:%M:%SZ"),
                   "gates": _gates}, fh, indent=2, sort_keys=True)
    return 0 if _ok else 1


def _next_month(m):
    y, mo = int(m[:4]), int(m[5:])
    mo += 1
    if mo == 13:
        y, mo = y + 1, 1
    return "%04d-%02d" % (y, mo)


# --------------------------------------------------------------------------- #
# RUN - the one governed Stage-A execution
# --------------------------------------------------------------------------- #
def cmd_run(_args) -> int:
    print("TSMOM-VRP-01 - S3 GOVERNED STAGE-A RUN")
    print("=" * 78)
    print("INTEGRITY METADATA ONLY. No scientific value is printed by this command.")

    store = vreveal.PROTECTED_STORE
    if os.path.isdir(store) and os.listdir(store):
        print("\n  REFUSED: the protected store is not empty. A governed run already "
              "exists and RUN_COUNT must remain 1.")
        return 1

    manifest, contracts, cal, chain = load_chain()
    months, days = sealed_window_days(chain)
    if not (months and months[0] == SEALED_FIRST_MONTH
            and months[-1] == SEALED_LAST_MONTH and len(months) == SEALED_MONTHS):
        print("\n  REFUSED: the eligible window is not exactly the sealed window.")
        return 1

    # ---- THE GOVERNED RUN. Gated by the committed Owner EXECUTION grant. ----
    result = vsa.run_stage_a(days, K_STAGE_A, vreveal.REAL, run_id=RUN_ID)
    monthly = [m.r_A for m in result.months]
    if len(monthly) != SEALED_MONTHS:
        print("\n  REFUSED: produced %d months, expected %d." % (len(monthly), SEALED_MONTHS))
        return 1

    mean_monthly = sum(monthly) / len(monthly)
    mu_a = vsa.annualised_mean(monthly)
    interval = vinf.stage_a_interval(monthly, stream="stage_a_historical", n_reps=K.reps)
    vinf.enforce_floor(interval)
    state = vsa.classify(interval.lower, interval.upper, K.E, K.F)

    # ---- predeclared Stage-A descriptives (PROMOTION_POWER = NONE) ----
    S = vsizing.dollar_sensitivity(K_STAGE_A)
    daily = result.daily
    net_daily = [d.variation_margin - d.cost for d in daily]
    r1_points = {m.month: m.variation_margin / S for m in result.months}
    worst_1d = min(net_daily) / K_STAGE_A
    worst_5d = min(sum(net_daily[i:i + 5]) for i in range(len(net_daily) - 4)) / K_STAGE_A
    worst_month = min(monthly)
    # R12: c0 = 0.05. cost_points = max(0.10, tick) = 0.10 under the primary and
    # max(0.05, tick) = 0.05 under the descriptive, on EVERY day of the window
    # (tick_comparable is 0.01 pre-2007-03-26 and 0.05 after, both <= 0.05). The
    # sensitivity is therefore exact arithmetic on the stored ledger: NO SECOND RUN.
    assert all(abs(d.cost_points - 0.10) < 1e-12 for d in daily)
    assert all(vspecs.tick_comparable(d.date) <= K.c0_descriptive + 1e-12 for d in daily)
    by_month_turnover = {}
    for d in daily:
        by_month_turnover.setdefault(vchain._month_key(d.date), 0.0)
        by_month_turnover[vchain._month_key(d.date)] += d.turnover_contracts
    monthly_005 = []
    for m in result.months:
        t = by_month_turnover[m.month]
        cost_005 = (K.c0_descriptive * K.STANDARD_MULTIPLIER * t
                    + vcosts.DOLLAR_CONSTANTS_PER_STANDARD_SIDE * t)
        monthly_005.append((m.variation_margin - cost_005) / K_STAGE_A)
    mu_a_005 = vsa.annualised_mean(monthly_005)
    rf = fm1_monthly_rf(cal, [m.month for m in result.months])
    total_return = vsa.descriptive_total_return(monthly, [rf[m.month] for m in result.months])
    defined_tr = [x for x in total_return if x is not None]

    payload = {
        "run_id": RUN_ID,
        "run_timestamp_utc": _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "lineage": "TSMOM-VRP-01",
        "seal_commit": S1_SEAL,
        "s2_build_commit": S2_BUILD,
        "s2_closure_commit": S2_CLOSURE,
        "code_commit": git("rev-parse", "HEAD")[1],
        "erratum_sha256": ERRATUM_SHA,
        "prereg_sha256": K.PREREG_SHA256,
        "raw_manifest_sha256": sha256_file(MANIFEST_JSON),
        "raw_contract_file_count": len(manifest["contract_files"]),
        "raw_file_sha256s": {r["file_name"]: r["sha256"] for r in manifest["contract_files"]},
        "dgs3mo_sha256": sha256_file(DGS3MO),
        "sample_first_month": months[0],
        "sample_last_month": months[-1],
        "month_count": len(months),
        "chain_days": len(days),
        "K": K_STAGE_A,
        "sealed_constants": {
            "theta": K.theta, "b": K.b, "E": K.E, "F": K.F, "J": K.J, "m_J": K.m_J,
            "lambda": K.LAMBDA, "c0": K.c0, "commission": K.commission, "fee": K.fee,
            "beta": K.beta, "s": K.s, "W0": K.W0, "delta_tail": K.delta_tail,
            "block": K.block, "reps": K.reps, "floor": K.floor, "seed": K.seed,
            "cutoff": str(K.cutoff), "stageB_end": str(K.stageB_end),
        },
        "rng": {"master_seed": K.seed, "stream": interval.stream,
                "spawned_entropy": vinf.spawned_entropy(),
                "block_p": vinf.P_BLOCK, "replicates": K.reps, "floor": K.floor},
        # ---- PRIMARY (scientific; GENERATED_NOT_SEEN) ----
        "monthly_returns": {m.month: m.r_A for m in result.months},
        "monthly_mean": mean_monthly,
        "annualised_mean_excess_on_K": mu_a,
        "ci_95_low": interval.lower,
        "ci_95_high": interval.upper,
        "bootstrap": {"valid_replicates": interval.valid_replicates,
                      "invalid_replicates": interval.invalid_replicates,
                      "floor_met": interval.floor_met},
        "classification": state,
        # ---- predeclared descriptives, PROMOTION_POWER = NONE ----
        "descriptives": {
            "R1_gross_carry_points_per_unit_sensitivity_by_month": r1_points,
            "R1_mean_monthly_points": sum(r1_points.values()) / len(r1_points),
            "R2_worst_1day_sleeve_loss_fraction_of_K": worst_1d,
            "R3_worst_5day_sleeve_loss_fraction_of_K": worst_5d,
            "R4_worst_monthly_sleeve_loss_fraction_of_K": worst_month,
            "R4_stress_budget_b": K.b,
            "R5_capital_exhaustion_events": list(result.capital_exhaustion_months),
            "R5_capital_exhaustion_count": len(result.capital_exhaustion_months),
            "R5_intra_month_exhaustion_months": [m.month for m in result.months
                                                 if m.intra_month_exhaustion],
            "R12_c0_005_annualised_mean": mu_a_005,
            "R13_collateral_total_return_defined_months": len(defined_tr),
            "R13_collateral_total_return_undefined_months":
                [m.month for m, x in zip(result.months, total_return) if x is None],
            "R13_annualised_mean_total_return":
                (12.0 * sum(defined_tr) / len(defined_tr)) if defined_tr else None,
            "R14_point_estimate": mu_a,
            "R14_lower": interval.lower,
            "R14_upper": interval.upper,
            "R14_invalid_replicates": interval.invalid_replicates,
        },
        "stage_b": {"executed": False, "authorized": False},
        "trial_ledger_transition": {
            "sample": "dataset.cboe.vix-futures-monthly-chain",
            "before": 0, "after": 1, "increment": 1,
            "stage_a_trial_spent": True, "stage_b_trial_spent": False,
        },
    }

    meta = vreveal.store_generated_not_seen(payload, "stage_a_historical")
    protected = vreveal.ProtectedResult(payload, "stage_a_historical")

    print("\n  RUN_ID                     = %s" % RUN_ID)
    print("  RUN_COUNT                  = 1")
    print("  SAMPLE                     = %s .. %s" % (months[0], months[-1]))
    print("  MONTH_COUNT                = %d" % len(months))
    print("  CHAIN_DAYS                 = %d" % len(days))
    print("  BOOTSTRAP_VALID_REPLICATES = %d / %d (floor %d)"
          % (interval.valid_replicates, K.reps, K.floor))
    print("  RESULT_STATE               = GENERATED_NOT_SEEN")
    print("  PROTECTED_RESULT_SHA256    = %s" % meta["sha256"])
    print("  PROTECTED_PATH             = %s" % meta["path"])
    print("  STAGE_B_EXECUTED           = NO")
    print("\n  (no monthly return, mean, interval bound, classification or descriptive "
          "was printed)")

    with open(PROTECTED_POINTER, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"run_id": RUN_ID, "protected": meta,
                   "month_count": len(months), "chain_days": len(days),
                   "sample_first_month": months[0], "sample_last_month": months[-1],
                   "bootstrap_valid_replicates": interval.valid_replicates,
                   "result_state": "GENERATED_NOT_SEEN"},
                  fh, indent=2, sort_keys=True)

    with open(RUN_MANIFEST, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({
            "run_id": RUN_ID,
            "run_timestamp_utc": payload["run_timestamp_utc"],
            "lineage": "TSMOM-VRP-01",
            "seal_commit": S1_SEAL, "s2_build_commit": S2_BUILD,
            "s2_closure_commit": S2_CLOSURE, "code_commit": payload["code_commit"],
            "erratum_sha256": ERRATUM_SHA, "prereg_sha256": K.PREREG_SHA256,
            "raw_manifest_sha256": payload["raw_manifest_sha256"],
            "raw_contract_file_count": payload["raw_contract_file_count"],
            "dgs3mo_sha256": payload["dgs3mo_sha256"],
            "sample": {"first_month": months[0], "last_month": months[-1],
                       "month_count": len(months), "chain_days": len(days)},
            "K": K_STAGE_A,
            "rng": payload["rng"],
            "protected_result_sha256": meta["sha256"],
            "protected_result_path": meta["path"],
            "result_state": "GENERATED_NOT_SEEN",
            "reveal_count": 0, "reveal_timestamp_utc": None,
            "stage_b_executed": False, "stage_b_authorized": False,
            "run_count": 1,
        }, fh, indent=2, sort_keys=True)
    print("  RUN_MANIFEST               = %s"
          % os.path.relpath(RUN_MANIFEST, REPO).replace("\\", "/"))
    assert not protected.revealed
    return 0


# --------------------------------------------------------------------------- #
# VERIFY - the post-compute integrity gate
# --------------------------------------------------------------------------- #
def _load_protected():
    store = vreveal.PROTECTED_STORE
    files = sorted(f for f in os.listdir(store)) if os.path.isdir(store) else []
    if len(files) != 1:
        return None, files
    with open(os.path.join(store, files[0]), encoding="utf-8") as fh:
        return json.load(fh), files


def cmd_verify(_args) -> int:
    print("TSMOM-VRP-01 - S3 POST-COMPUTE INTEGRITY GATE")
    print("=" * 78)
    print("Booleans, counts and hashes only. No scientific value is printed.")

    blob, files = _load_protected()
    section("INTEGRITY")
    ck("RUN_COUNT = 1 (exactly one protected result exists)",
       blob is not None, "%d file(s)" % len(files))
    if blob is None:
        return 1
    p = blob["payload"]
    manifest, contracts, cal, chain = load_chain()
    months, days = sealed_window_days(chain)

    ck("SAMPLE_MATCH", p["sample_first_month"] == SEALED_FIRST_MONTH
       and p["sample_last_month"] == SEALED_LAST_MONTH
       and [m.__str__() for m in months[:1]] == [SEALED_FIRST_MONTH],
       "%s..%s" % (p["sample_first_month"], p["sample_last_month"]))
    ck("MONTH_COUNT = 240", p["month_count"] == SEALED_MONTHS, str(p["month_count"]))
    ck("monthly series length matches the month count",
       len(p["monthly_returns"]) == SEALED_MONTHS, str(len(p["monthly_returns"])))
    sealed = p["sealed_constants"]
    ck("SEALED_CONSTANTS_MATCH",
       sealed == {"theta": K.theta, "b": K.b, "E": K.E, "F": K.F, "J": K.J, "m_J": K.m_J,
                  "lambda": K.LAMBDA, "c0": K.c0, "commission": K.commission, "fee": K.fee,
                  "beta": K.beta, "s": K.s, "W0": K.W0, "delta_tail": K.delta_tail,
                  "block": K.block, "reps": K.reps, "floor": K.floor, "seed": K.seed,
                  "cutoff": str(K.cutoff), "stageB_end": str(K.stageB_end)})
    ok, detail = vval.check_frozen_constants()
    ck("OWNER_VALUES_MATCH (constants re-asserted against the sealed text)", ok, detail)
    live = {r["file_name"]: r["sha256"] for r in manifest["contract_files"]}
    ck("RAW_HASHES_MATCH", p["raw_file_sha256s"] == live,
       "%d files" % len(live))
    ck("raw manifest hash unchanged since the run",
       p["raw_manifest_sha256"] == sha256_file(MANIFEST_JSON))
    _, head = git("rev-parse", "HEAD")
    ck("CODE_COMMIT_MATCH (the run recorded the commit it actually ran at)",
       p["code_commit"] == head, "run %s vs HEAD %s"
       % (p["code_commit"][:12], head[:12]))
    ck("the run's seal / build / closure pins match this lineage",
       p["seal_commit"] == S1_SEAL and p["s2_build_commit"] == S2_BUILD
       and p["s2_closure_commit"] == S2_CLOSURE)
    ok, detail = vval.check_sealed_artifact_hashes()
    ck("S1_HASHES_MATCH", ok, detail)
    ck("ERRATUM_HASH_MATCH", p["erratum_sha256"] == ERRATUM_SHA
       and sha256_file(os.path.join(PKG, "VRP_S1_MECHANICAL_ERRATUM_01.md")) == ERRATUM_SHA)
    ck("RNG_MATCH (seed, streams, block, replicates, floor)",
       p["rng"]["master_seed"] == K.seed
       and p["rng"]["replicates"] == K.reps and p["rng"]["floor"] == K.floor
       and abs(p["rng"]["block_p"] - 1.0 / K.block) < 1e-15
       and p["rng"]["spawned_entropy"] == json.loads(json.dumps(vinf.spawned_entropy())),
       "seed %d, stream %s" % (K.seed, p["rng"]["stream"]))
    ck("bootstrap valid-replicate floor met",
       p["bootstrap"]["floor_met"] is True
       and p["bootstrap"]["valid_replicates"] >= K.floor,
       "%d valid / %d" % (p["bootstrap"]["valid_replicates"], K.reps))
    ck("NO_STAGE_B_EXECUTION", p["stage_b"]["executed"] is False
       and p["stage_b"]["authorized"] is False)
    audit = vaudit.audit()
    ck("NO_C_A_ACCESS", audit["pass"] is True
       and audit["CANONICAL_FORWARD_RETURN_COMPUTED"] == "NO")
    ck("TRIAL_LEDGER_INCREMENT = EXACTLY_1",
       p["trial_ledger_transition"]["increment"] == 1
       and p["trial_ledger_transition"]["before"] == 0
       and p["trial_ledger_transition"]["after"] == 1
       and p["trial_ledger_transition"]["stage_b_trial_spent"] is False)
    recomputed = hashlib.sha256(
        json.dumps(p, sort_keys=True, default=str).encode("utf-8")).hexdigest()
    ck("PROTECTED_RESULT_HASHED and reproducible", recomputed == blob["sha256"],
       blob["sha256"][:16])
    ck("RESULT_STATE = GENERATED_NOT_SEEN", blob["classification"] == "GENERATED_NOT_SEEN")

    section("POST-COMPUTE GATE RESULT")
    status = "PASS" if _ok else "FAIL"
    print("  S3_POST_COMPUTE_GATE = %s   (%d PASS / %d FAIL)"
          % (status, sum(1 for g in _gates if g["pass"]),
             sum(1 for g in _gates if not g["pass"])))
    with open(os.path.join(HERE, "VRP_S3_POSTCOMPUTE_GATES.json"), "w",
              encoding="utf-8", newline="\n") as fh:
        json.dump({"run_id": RUN_ID, "result": status,
                   "protected_result_sha256": blob["sha256"],
                   "generated_utc": _dt.datetime.now(_dt.timezone.utc)
                   .strftime("%Y-%m-%dT%H:%M:%SZ"),
                   "gates": _gates}, fh, indent=2, sort_keys=True)
    return 0 if _ok else 1


# --------------------------------------------------------------------------- #
# REVEAL - the single authorised reveal
# --------------------------------------------------------------------------- #
def cmd_reveal(_args) -> int:
    print("TSMOM-VRP-01 - S3 SINGLE AUTHORISED STAGE-A REVEAL")
    print("=" * 78)
    blob, files = _load_protected()
    if blob is None:
        print("  REFUSED: expected exactly one protected result, found %d." % len(files))
        return 1
    with open(RUN_MANIFEST, encoding="utf-8") as fh:
        rm = json.load(fh)
    if rm.get("reveal_count", 0) != 0:
        print("  REFUSED: reveal_count is already %d. ONE reveal only."
              % rm["reveal_count"])
        return 1

    protected = vreveal.ProtectedResult(blob["payload"], "stage_a_historical")
    payload = protected.reveal()          # requires the committed single-use REVEAL grant

    p = payload
    d = p["descriptives"]
    st = p["classification"]
    print("\n" + "=" * 78)
    print("PRIMARY  —  TSMOM-VRP-01 VRP-A, historical Stage A")
    print("=" * 78)
    print("  HISTORICAL_STAGE_A_WINDOW              = %s .. %s"
          % (p["sample_first_month"], p["sample_last_month"]))
    print("  N_MONTHS                               = %d" % p["month_count"])
    print("  ANNUALISED_MEAN_NET_EXCESS_RETURN_ON_K = %+.6f  (%+.4f %%)"
          % (p["annualised_mean_excess_on_K"], 100 * p["annualised_mean_excess_on_K"]))
    print("  CI_95_LOW                              = %+.6f  (%+.4f %%)"
          % (p["ci_95_low"], 100 * p["ci_95_low"]))
    print("  CI_95_HIGH                             = %+.6f  (%+.4f %%)"
          % (p["ci_95_high"], 100 * p["ci_95_high"]))
    print("  ECONOMIC_USEFULNESS_MARGIN             = +0.075  (+7.5 %)")
    print("  ADVERSE_FLOOR                          = -0.075  (-7.5 %)")
    print("  STAGE_A_STATE                          = %s" % st["state"])
    print("  FAILURE_CLASS                          = %s"
          % (st["failure_class"] or "NONE"))
    print("  FAILURE_SUBTAG                         = %s" % (st["subtag"] or "NONE"))
    print("  STAGE_A_TRIAL_SPENT                    = YES")
    print("  BOOTSTRAP                              = %d valid / %d replicates "
          "(floor %d), %d invalid"
          % (p["bootstrap"]["valid_replicates"], p["rng"]["replicates"],
             p["rng"]["floor"], p["bootstrap"]["invalid_replicates"]))
    print("\n" + "-" * 78)
    print("PREDECLARED STAGE-A DESCRIPTIVES  —  PROMOTION_POWER = NONE")
    print("-" * 78)
    print("  R1  mean monthly gross carry, comparable points per unit sensitivity = %+.4f"
          % d["R1_mean_monthly_points"])
    print("  R2  worst 1-day sleeve loss, fraction of K                           = %+.6f"
          % d["R2_worst_1day_sleeve_loss_fraction_of_K"])
    print("  R3  worst 5-day sleeve loss, fraction of K                           = %+.6f"
          % d["R3_worst_5day_sleeve_loss_fraction_of_K"])
    print("  R4  worst monthly sleeve loss, fraction of K (budget b = %.2f)       = %+.6f"
          % (d["R4_stress_budget_b"], d["R4_worst_monthly_sleeve_loss_fraction_of_K"]))
    print("  R5  CAPITAL_EXHAUSTION events                                        = %d %s"
          % (d["R5_capital_exhaustion_count"],
             d["R5_capital_exhaustion_events"] or ""))
    print("  R12 c0 = 0.05 cost sensitivity, annualised mean                      = %+.6f"
          % d["R12_c0_005_annualised_mean"])
    tr = d["R13_annualised_mean_total_return"]
    print("  R13 FM-1 collateral total return, annualised mean                    = %s"
          % ("%+.6f" % tr if tr is not None else "UNDEFINED"))
    print("      defined months = %d / %d; undefined = %s"
          % (d["R13_collateral_total_return_defined_months"], p["month_count"],
             d["R13_collateral_total_return_undefined_months"] or "none"))
    print("  R14 point estimate %+.6f, L %+.6f, U %+.6f, invalid replicates %d"
          % (d["R14_point_estimate"], d["R14_lower"], d["R14_upper"],
             d["R14_invalid_replicates"]))
    print("\n  Stage-B descriptives (R6-R11) are NOT reported: Stage B has not run.")
    print("=" * 78)

    rm["reveal_count"] = 1
    rm["reveal_timestamp_utc"] = _dt.datetime.now(_dt.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ")
    rm["result_state"] = "REVEALED_ONCE"
    with open(RUN_MANIFEST, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(rm, fh, indent=2, sort_keys=True)
    with open(os.path.join(HERE, "VRP_STAGE_A_REVEALED_PACKAGE.json"), "w",
              encoding="utf-8", newline="\n") as fh:
        json.dump({
            "run_id": RUN_ID, "reveal_count": 1,
            "reveal_timestamp_utc": rm["reveal_timestamp_utc"],
            "protected_result_sha256": blob["sha256"],
            "HISTORICAL_STAGE_A_WINDOW": "%s..%s" % (p["sample_first_month"],
                                                     p["sample_last_month"]),
            "N_MONTHS": p["month_count"],
            "ANNUALISED_MEAN_NET_EXCESS_RETURN_ON_K": p["annualised_mean_excess_on_K"],
            "CI_95_LOW": p["ci_95_low"], "CI_95_HIGH": p["ci_95_high"],
            "ECONOMIC_USEFULNESS_MARGIN": K.E, "ADVERSE_FLOOR": K.F,
            "STAGE_A_STATE": st["state"], "FAILURE_CLASS": st["failure_class"] or "NONE",
            "FAILURE_SUBTAG": st["subtag"] or "NONE",
            "STAGE_A_TRIAL_SPENT": "YES",
            "bootstrap": p["bootstrap"],
            "monthly_mean": p["monthly_mean"],
            "descriptives": d,
            "STAGE_B_EXECUTED": "NO",
        }, fh, indent=2, sort_keys=True)
    print("\n  REVEAL_COUNT = 1   (the single authorised reveal is now consumed)")
    return 0


# --------------------------------------------------------------------------- #
# POSTSTATE - the post-run state-transition validator
# --------------------------------------------------------------------------- #
# The governed run and the single reveal necessarily falsify four more S2-state
# assertions, on top of the two the EXECUTION grant already flipped. Same discipline as
# before: NOTHING is modified or relabelled; the validator below requires these to be the
# ONLY failures, so any other regression is still caught.
POSTRUN_FLIPS_POST_S2 = [
    "no single-use Owner EXECUTION authorisation is committed",
    "no single-use Owner REVEAL authorisation is committed",
    "the VRP protected store is empty or absent",
    "the governed-run entry gate REFUSES a real run",
]
POSTRUN_FLIPS_TESTS = [
    "test_i21_no_execution_authorization_exists",
    "test_i21_protected_result_refuses_to_print_or_yield_its_value",
    "test_i21_real_stage_a_is_refused_during_s2",
    "test_s2_no_real_outcome_artifacts_exist",
]


def cmd_poststate(_args) -> int:
    print("TSMOM-VRP-01 - S3 POST-RUN STATE-TRANSITION VALIDATOR")
    print("=" * 78)
    print("Accounts for the state the governed run and the single reveal necessarily")
    print("created. No accepted validator is modified and no exit code is relabelled.")
    import re as _re

    section("1. accepted validators: only the enumerated post-run flips")
    subprocess.run([sys.executable, os.path.join("research", "extensions", "vrp", "s2",
                                                 "vrp_post_s2_validate.py")],
                   cwd=REPO, capture_output=True, text=True,
                   encoding="utf-8", errors="replace")
    with open(os.path.join(REPO, "research", "extensions", "vrp", "s2",
                           "VRP_POST_S2_STATE_VALIDATION.json"), encoding="utf-8") as fh:
        rec = json.load(fh)
    fails = sorted(c["check"] for c in rec["checks"] if not c["pass"])
    ck("post-S2 validator: only the enumerated post-run flips fail",
       fails == sorted(POSTRUN_FLIPS_POST_S2), "; ".join(fails) or "none")
    ck("post-S2 validator: every other check still PASSES",
       len([c for c in rec["checks"] if c["pass"]])
       == len(rec["checks"]) - len(POSTRUN_FLIPS_POST_S2),
       "%d PASS of %d" % (len([c for c in rec["checks"] if c["pass"]]), len(rec["checks"])))
    ck("original S1 validator still reports 113 content checks PASS",
       rec["original_s1_content_checks_pass"] == 113
       and rec["original_s1_failing_checks"] == [rec["expected_state_failure"]],
       "exit %s" % rec["original_s1_validator_exit"])

    proc = subprocess.run([sys.executable, "-m", "pytest",
                           os.path.join("research", "extensions", "vrp", "vrp_tests.py"),
                           "-q", "--no-header", "--tb=no", "-p", "no:cacheprovider"],
                          cwd=REPO, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    t_fails = sorted(set(_re.findall(r"vrp_tests\.py::(\S+)", proc.stdout)))
    ck("acceptance suite: only the enumerated post-run flips fail",
       t_fails == sorted(POSTRUN_FLIPS_TESTS), "; ".join(t_fails) or "none")
    m = _re.search(r"(\d+) failed, (\d+) passed", proc.stdout)
    ck("acceptance suite: every other test still passes",
       bool(m) and int(m.group(1)) == len(POSTRUN_FLIPS_TESTS), m.group(0) if m else "?")

    section("2. the reveal-control protections that must STILL hold")
    probe = vreveal.ProtectedResult({"A": 0.123456789}, "probe")
    ck("repr / str / format still hide the value",
       all("0.123456789" not in f(probe) for f in (repr, str, lambda x: format(x))))
    refused = False
    try:
        _ = probe.value
    except vreveal.RevealNotAuthorized:
        refused = True
    ck("`.value` is still refused before a reveal", refused)
    refused = False
    try:
        list(probe)
    except vreveal.RevealNotAuthorized:
        refused = True
    ck("iteration is still refused", refused)

    section("3. run and reveal are each exactly once")
    with open(RUN_MANIFEST, encoding="utf-8") as fh:
        rm = json.load(fh)
    ck("RUN_COUNT = 1", rm["run_count"] == 1, str(rm["run_count"]))
    ck("REVEAL_COUNT = 1", rm["reveal_count"] == 1, str(rm["reveal_count"]))
    ck("RESULT_STATE = REVEALED_ONCE", rm["result_state"] == "REVEALED_ONCE",
       rm["result_state"])
    blob, files = _load_protected()
    ck("exactly one protected result exists", blob is not None, "%d file(s)" % len(files))
    ck("the protected result hash is unchanged since the run",
       blob is not None and blob["sha256"] == rm["protected_result_sha256"],
       rm["protected_result_sha256"][:16])
    ck("a re-run is refused (the protected store is not empty)",
       os.path.isdir(vreveal.PROTECTED_STORE) and bool(os.listdir(vreveal.PROTECTED_STORE)))

    section("4. Stage B and C-A firewalls after the run")
    ck("Stage B was NOT executed",
       blob is not None and blob["payload"]["stage_b"]["executed"] is False)
    refused = False
    try:
        vreveal.require_run_authorization(vreveal.REAL, stage="STAGE_B")
    except vreveal.RunNotAuthorized:
        refused = True
    ck("a real Stage-B run is STRUCTURALLY refused by the live grant", refused)
    audit = vaudit.audit()
    ck("C-A static audit still PASSES", audit["pass"] is True
       and audit["CANONICAL_FORWARD_RETURN_COMPUTED"] == "NO")
    ok, detail = vval.check_sealed_artifact_hashes()
    ck("sealed S1 artifacts still byte-identical", ok, detail)
    ck("erratum still matches the authorised hash",
       sha256_file(os.path.join(PKG, "VRP_S1_MECHANICAL_ERRATUM_01.md")) == ERRATUM_SHA)

    section("POST-RUN STATE RESULT")
    status = "PASS" if _ok else "FAIL"
    print("  POST_RUN_STATE_VALIDATOR = %s   (%d PASS / %d FAIL)"
          % (status, sum(1 for g in _gates if g["pass"]),
             sum(1 for g in _gates if not g["pass"])))
    with open(os.path.join(HERE, "VRP_S3_POSTRUN_STATE.json"), "w",
              encoding="utf-8", newline="\n") as fh:
        json.dump({"run_id": RUN_ID, "result": status,
                   "enumerated_postrun_flips_post_s2": POSTRUN_FLIPS_POST_S2,
                   "enumerated_postrun_flips_tests": POSTRUN_FLIPS_TESTS,
                   "generated_utc": _dt.datetime.now(_dt.timezone.utc)
                   .strftime("%Y-%m-%dT%H:%M:%SZ"),
                   "gates": _gates}, fh, indent=2, sort_keys=True)
    return 0 if _ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="TSMOM-VRP-01 S3 governed Stage-A run")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("preflight").set_defaults(fn=cmd_preflight)
    sub.add_parser("run").set_defaults(fn=cmd_run)
    sub.add_parser("verify").set_defaults(fn=cmd_verify)
    sub.add_parser("reveal").set_defaults(fn=cmd_reveal)
    sub.add_parser("poststate").set_defaults(fn=cmd_poststate)
    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
