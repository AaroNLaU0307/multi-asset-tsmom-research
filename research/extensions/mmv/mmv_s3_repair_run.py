"""CTA-EDGE-04-MMV — S3 PRIMARY-SAMPLE CORRECTION under MMV-OD-8 (B_EXCLUDE).

    python research/extensions/mmv/mmv_s3_repair_run.py --preflight
    python research/extensions/mmv/mmv_s3_repair_run.py --execute

ONE bounded correction of the SAME primary trial MMV-S3-20260917-01. It is NOT
a new trial, NOT independent evidence and NOT a redesign.
`TRIAL_COUNT_INCREMENT = 0`, `F-MMV` stays at `m = 1`.

WHY. `research/extensions/LOCKBOX_PROCEDURE.md` §2.1, written 2026-09-08 and so
PRE-EXISTING at the 2026-09-17 seal, verifies the frozen ETF panel's boundary at
`2026-06-12` and states that the June 2026 monthly row is "a complete label over
an incomplete period". Its rule: an evaluation using the terminal monthly row
must either (a) TRUNCATE it and state so, or (b) declare in its preregistration
that a partial terminal month is included and why. The sealed MMV contract never
exercises (b) — it records the boundary in §P and declares nothing — so (a)
binds. The parent run included the row and stated that it had, which is neither
(a) nor (b). That is the defect this repair corrects, and nothing else.

HOW THE BLAST RADIUS IS HELD TO ONE ROW. This module does not reimplement any
scientific step. It IMPORTS the committed parent driver and reuses its functions
as the SAME OBJECTS — signal construction, book build, structural gate, return
series, bootstrap and classification all execute the parent's code. The parent's
`phase4` already takes the eligible-month index as a PARAMETER, so correcting
the sample requires no edit to any scientific function at all: only a different
value is passed in. `assert_reuse_identity()` checks that at run time.

THE GUARD IS STRUCTURAL, NOT A HARD-CODED DATE. A month M is eligible only if
the authoritative price panel CONTINUES PAST M, which is what establishes that
the last observed price inside M really is M's final trading close. A panel that
stops inside M cannot establish it, so M FAILS CLOSED. June 2026 is excluded
because no price date exists after 2026-06-30, not because its name was written
into a filter.

FIREWALL, unchanged from the parent: no per-ETF return, no per-leg PnL, no
drawdown, no hit rate, no rolling Sharpe, no alternative cost, lookback,
mapping, series, start date or bootstrap, and no first-release diagnostic.
Gate 0.5 is neither rerun nor reinterpreted.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
os.chdir(REPO)
for p in (REPO, HERE):
    if p not in sys.path:
        sys.path.insert(0, p)

import config                                                    # noqa: E402
from engine import votes                                         # noqa: E402
import mmv_authorization                                         # noqa: E402
import mmv_s3_run as P                     # the COMMITTED parent driver  # noqa: E402

# Reused as the SAME function objects. Nothing below is a copy.
from mmv_s3_run import (build_book, classify, load_prices, phase1,  # noqa: E402
                        phase2, phase3, phase4, phase5, sharpe)

RUN_ID = "MMV-S3-REPAIR-20260917-01"
AUTHORIZATION_ID = "MMV-AUTH-0003"
RUN_TYPE = "PRIMARY_TRIAL_CORRECTION"
SCOPE = "ONE_SHOT_SINGLE_PRIMARY_TRIAL_CORRECTION"
LINEAGE = "CTA-EDGE-04-MMV"

PARENT_RUN_ID = "MMV-S3-20260917-01"
PARENT_AUTH_ID = "MMV-AUTH-0002"
PARENT_DRIVER_COMMIT = "93d9a4768a387d1fd1ffe30deba1c24dffeb9206"
PARENT_AUTH_COMMIT = "a6748e704333248157fd0fe05d8b6357a81ca6ae"
PARENT_RESULT_COMMIT = "e9c132b4297f0b39d301bc7ae70c8cdf9efbb54a"
S2_COMMIT = "dc2817b99f048f561f1db55f998e24ff2193df10"

PARENT_JSON = "research/extensions/mmv/s3/MMV_S3_RESULT.json"
PARENT_MD = "research/extensions/mmv/MMV_S3_RESULT.md"

OUT_DIR = os.path.join("research", "extensions", "mmv", "s3")
RESULT_JSON = os.path.join(OUT_DIR, "MMV_S3_REPAIR_RESULT.json")

#: MMV-OD-8. The decision that this repair adopts, recorded as a constant so the
#: artifact and the code cannot drift apart.
MMV_OD_8 = "B_EXCLUDE"
OD8_AUTHORITY = ("research/extensions/LOCKBOX_PROCEDURE.md §2.1 (written "
                 "2026-09-08, pre-existing at the 2026-09-17 seal) + the sealed "
                 "month-end-close execution convention")

#: The expected correction, stated up front so the run can FAIL if reality
#: differs rather than quietly accepting whatever it finds (brief §7).
EXPECTED_REMOVED = ("2026-06-30",)
EXPECTED_ORIGINAL_N = 214
EXPECTED_REPAIRED_N = 213

#: Files whose bytes must be UNCHANGED since the parent run. A change here would
#: be an outcome-affecting difference outside the one permitted correction.
FROZEN_SINCE_PARENT = {
    "research/extensions/mmv/mmv_s3_run.py": PARENT_DRIVER_COMMIT,
    "src/performance.py": PARENT_DRIVER_COMMIT,
    "src/portfolio.py": PARENT_DRIVER_COMMIT,
    "src/sizing.py": PARENT_DRIVER_COMMIT,
    "src/signals.py": PARENT_DRIVER_COMMIT,
    "config.py": PARENT_DRIVER_COMMIT,
    "research/extensions/mmv/engine/risk.py": S2_COMMIT,
    "research/extensions/mmv/engine/votes.py": S2_COMMIT,
    "research/extensions/mmv/engine/legs.py": S2_COMMIT,
    "research/extensions/mmv/engine/pit.py": S2_COMMIT,
    "research/extensions/mmv/engine/policy.py": S2_COMMIT,
    "research/extensions/mmv/engine/gate05.py": S2_COMMIT,
    "research/extensions/mmv/engine/start.py": S2_COMMIT,
    "research/extensions/mmv/mmv_gate05_run.py": PARENT_DRIVER_COMMIT,
}

#: Every parent function this module reuses. Checked by OBJECT IDENTITY, so a
#: later edit that shadows one of them locally becomes a hard stop.
REUSED = ("build_book", "classify", "load_prices", "phase1", "phase2",
          "phase3", "phase4", "phase5", "sharpe")

#: Everything this module defines ITSELF, each mapped to the brief §5 category
#: that permits it. The audit derives the real set from the AST and requires an
#: EXACT match, so a new function cannot appear here unclassified — which is the
#: only way "no other outcome-affecting code difference exists" can be a check
#: rather than a promise.
SELF_DEFINED = {
    "Stop": "repair-specific guard",
    "git_blob": "repair-specific guard",
    "phase0": "correction authorization handling",
    "assert_reuse_identity": "repair-specific guard",
    "assert_nothing_unclassified": "repair-specific guard",
    "phase_diff_audit": "repair-specific guard",
    "month_end_complete": "explicit terminal-completeness assertion",
    "phase_terminal": "explicit terminal-completeness assertion "
                      "(THE one permitted sample change)",
    "phase_parent_control": "repair-specific guard (signal/position identity)",
    "build_result": "provenance / status writing",
    "main": "repair-specific guard",
}


class Stop(RuntimeError):
    """A hard stop. Never caught, never softened into a default."""


say = P.say
sha256_file = P.sha256_file


def git_blob(relpath, rev):
    out = subprocess.run(["git", "show", "%s:%s" % (rev, relpath)],
                         cwd=REPO, capture_output=True)
    if out.returncode != 0:
        raise Stop("cannot read %s at %s" % (relpath, rev))
    return out.stdout


# =========================================================================== #
# PHASE 0 — AUTHORIZATION
# =========================================================================== #

def phase0(execute):
    say("=" * 78)
    say("CTA-EDGE-04-MMV — S3 PRIMARY-SAMPLE CORRECTION  (MMV-OD-8 B_EXCLUDE)")
    say("=" * 78)
    say("PHASE 0 — REPAIR AUTHORIZATION")

    if os.path.exists(RESULT_JSON):
        raise Stop("a repaired result already exists at %s; the correction "
                   "grant is CONSUMED and no second repair is authorized"
                   % RESULT_JSON)

    grant = mmv_authorization.active_grant()
    if grant.get("authorization_id") != AUTHORIZATION_ID:
        raise Stop("the live grant is %r, not %r"
                   % (grant.get("authorization_id"), AUTHORIZATION_ID))
    if grant.get("scope") != SCOPE:
        raise Stop("grant scope %r does not authorize a primary-trial "
                   "correction" % grant.get("scope"))
    b = grant["binding"]
    for field, want in (("run_id", RUN_ID), ("parent_run", PARENT_RUN_ID),
                        ("trial_family", "F-MMV")):
        if b.get(field) != want:
            raise Stop("grant %s = %r, not %r" % (field, b.get(field), want))
    if b.get("trial_count_increment") != 0:
        raise Stop("a correction must not increment the trial count")
    if b.get("m") != 1:
        raise Stop("m must remain 1")
    if b.get("rng_seed") != P.RNG_SEED:
        raise Stop("grant rng_seed %r != the parent seed %r"
                   % (b.get("rng_seed"), P.RNG_SEED))
    if b.get("mmv_od_8") != MMV_OD_8:
        raise Stop("grant does not carry MMV-OD-8 = %s" % MMV_OD_8)

    # The parent run must still be CONSUMED and its artifacts untouched.
    if PARENT_AUTH_ID not in mmv_authorization.consumed_ids():
        raise Stop("%s is no longer CONSUMED" % PARENT_AUTH_ID)
    P.PINNED[P.PRICES] = P.seal_manifest_hash(P.PRICES)
    pinned = dict(P.PINNED)
    pinned[PARENT_JSON] = b["parent_result_sha256"]
    pinned[PARENT_MD] = b["parent_record_sha256"]

    bad = []
    for path, want in sorted(pinned.items()):
        if not os.path.exists(path):
            bad.append("%s MISSING" % path)
            continue
        got = sha256_file(path)
        if got != want:
            bad.append("%s hash %s != pinned %s" % (path, got[:16], want[:16]))
    if bad:
        raise Stop("pinned input mismatch, a STRUCTURAL STOP:\n   "
                   + "\n   ".join(bad))

    say("  grant            %s  (%s)" % (AUTHORIZATION_ID, SCOPE))
    say("  run_id           %s" % RUN_ID)
    say("  parent run       %s   status INVALID_PRIMARY_SAMPLE / NONDECISIONAL"
        % PARENT_RUN_ID)
    say("  parent artifacts PRESERVED and hash-pinned; not deleted, not "
        "overwritten")
    say("  MMV-OD-8         %s" % MMV_OD_8)
    say("  authority        %s" % OD8_AUTHORITY)
    say("  trial accounting family F-MMV, m = 1, TRIAL_COUNT_INCREMENT = 0")
    say("  rng_seed         %d  (UNCHANGED from the parent run)" % P.RNG_SEED)
    say("  pinned inputs    %d / %d reproduce exactly" % (len(pinned),
                                                          len(pinned)))
    say("  mode             %s" % ("EXECUTE" if execute else
                                   "PREFLIGHT (spends nothing)"))
    say("  AUTHORIZED")
    say()
    return grant, pinned


# =========================================================================== #
# PHASE A — DRIVER DIFF AUDIT  (brief §5)
# =========================================================================== #

def assert_reuse_identity():
    """Every scientific step must be the PARENT's function object."""
    wrong = [n for n in REUSED if globals().get(n) is not getattr(P, n)]
    if wrong:
        raise Stop("these are not the parent's functions any more: %s. A "
                   "correction may not fork the scientific path." % wrong)


def assert_nothing_unclassified():
    """Derive what this module defines from its own AST and require that every
    definition carries a brief-§5 category. An unclassified definition is an
    unexamined code difference, so it is a hard stop."""
    import ast
    with open(os.path.abspath(__file__), encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    found = {n.name for n in tree.body
             if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
    declared = set(SELF_DEFINED)
    if found != declared:
        raise Stop("the repair module's definitions are not the classified "
                   "set. unclassified=%s  declared-but-absent=%s"
                   % (sorted(found - declared), sorted(declared - found)))
    return sorted(found)


def phase_diff_audit():
    say("PHASE A — DRIVER DIFF AUDIT")
    problems, checked = [], 0
    for relpath, rev in sorted(FROZEN_SINCE_PARENT.items()):
        checked += 1
        if not os.path.exists(relpath):
            problems.append("%s MISSING" % relpath)
            continue
        with open(relpath, "rb") as fh:
            now = fh.read()
        if now != git_blob(relpath, rev):
            problems.append("%s differs from its bytes at %s" % (relpath,
                                                                 rev[:7]))
    assert_reuse_identity()
    defined = assert_nothing_unclassified()

    say("  frozen files     %d / %d byte-identical to the parent-run state"
        % (checked - len(problems), checked))
    say("                   parent driver, canonical src/, config.py and the")
    say("                   sealed engine/ are all unmodified")
    say("  reuse identity   %d scientific functions are the PARENT's own"
        % len(REUSED))
    say("                   objects: %s" % ", ".join(REUSED))
    say("  parent phase4    already takes the eligible-month index as a")
    say("                   PARAMETER, so correcting the sample needs no edit")
    say("                   to any scientific function - only a different value")
    say("  own definitions  %d, every one classified under brief section 5:"
        % len(defined))
    for name in defined:
        say("     %-24s %s" % (name, SELF_DEFINED[name]))
    say("  NO scientific function is defined here. The only sample change is")
    say("  the value of the eligible-month index handed to the parent phase4.")
    say("  OUTCOME_AFFECTING_DIFFS = TERMINAL_ROW_ONLY")

    if problems:
        say()
        for p in problems:
            say("  PROBLEM: %s" % p)
        raise Stop("REPAIR_STATUS = HOLD — an outcome-affecting code "
                   "difference exists outside the one permitted correction")
    say("  DIFF AUDIT PASSED")
    say()
    return checked


# =========================================================================== #
# PHASE B — TERMINAL-MONTH COMPLETENESS  (brief §6)
# =========================================================================== #

def month_end_complete(price_dates, month_label):
    """Does the panel establish that month ``month_label`` has its final close?

    A primary monthly return for month M is built from M's LAST TRADING CLOSE.
    The panel proves it holds that close only if the panel CONTINUES PAST M: if
    a later month has prices, then the last price observed inside M really is
    M's final trading day. If the panel stops inside M, no amount of staring at
    M's own rows can establish completeness, and the month FAILS CLOSED.

    This is a structural predicate over the panel. It names no date, and it
    would exclude a different month unprompted if the panel were re-frozen
    earlier.
    """
    return bool((price_dates > month_label).any())


def phase_terminal(prices, elig):
    say("PHASE B — TERMINAL-MONTH COMPLETENESS ASSERTION  (MMV-OD-8)")
    dates = pd.DatetimeIndex(prices.index)
    last_price = dates.max()

    keep, dropped = [], []
    for m in elig:
        (keep if month_end_complete(dates, m) else dropped).append(m)
    repaired = pd.DatetimeIndex(keep)

    removed = [str(d.date()) for d in dropped]
    added = [str(d.date()) for d in repaired if d not in elig]
    problems = []

    if tuple(removed) != EXPECTED_REMOVED:
        problems.append("removed rows %s != expected %s"
                        % (removed, list(EXPECTED_REMOVED)))
    if added:
        problems.append("rows were ADDED: %s. A correction removes an "
                        "ineligible observation; it never grows the sample"
                        % added)
    if len(elig) != EXPECTED_ORIGINAL_N:
        problems.append("original eligible count %d != %d"
                        % (len(elig), EXPECTED_ORIGINAL_N))
    if len(repaired) != EXPECTED_REPAIRED_N:
        problems.append("repaired eligible count %d != %d"
                        % (len(repaired), EXPECTED_REPAIRED_N))
    earlier_same = list(repaired) == [d for d in elig if d not in dropped]
    if not earlier_same:
        problems.append("the surviving months are not the original ones in "
                        "the original order")

    for d in dropped:
        gap = (d - last_price).days
        say("  EXCLUDED  %s" % d.date())
        say("     reason                 the panel does not continue past this")
        say("                            month, so its final trading close is")
        say("                            NOT established by the data")
        say("     authoritative last px  %s" % last_price.date())
        say("     canonical month end    %s   (%d calendar days later)"
            % (d.date(), gap))
        say("     primary_return_%s = INELIGIBLE" % d.strftime("%Y_%m"))
    say("  months whose completeness IS established   %d" % len(repaired))
    say("  original eligible %d  ->  repaired eligible %d   (delta -%d)"
        % (len(elig), len(repaired), len(elig) - len(repaired)))
    say("  removed %s   added %s" % (removed, added or "none"))
    say("  every earlier eligible month is unchanged and in the same order: %s"
        % ("YES" if earlier_same else "NO"))
    say("  the 218-date MMV DECISION grid is NOT altered; 2026-06-30 remains a")
    say("  valid decision-state date and Gate 0.5 is untouched")

    if problems:
        say()
        for p in problems:
            say("  PROBLEM: %s" % p)
        raise Stop("REPAIR_STATUS = HOLD — the sample change is not exactly "
                   "the one authorized")
    say("  TERMINAL-MONTH ASSERTION PASSED")
    say()
    return repaired, removed, added, last_price


# =========================================================================== #
# PHASE C — PARENT REPRODUCTION CONTROL  (brief §8)
# =========================================================================== #

def phase_parent_control(book, monthly_px, rets, elig, signal):
    """Recompute the PARENT's 214-month statistics and require them to
    reproduce its published numbers to the last bit.

    This exposes nothing new — the parent result is already public — and it is
    the only way to prove mechanically that the signal, the positions, the
    wrapper, the cost model and the bootstrap are all unchanged. If the engine
    had drifted at all, these would not reproduce.
    """
    say("PHASE C — PARENT REPRODUCTION CONTROL  (identity, not new exposure)")
    with open(PARENT_JSON, encoding="utf-8") as fh:
        parent = json.load(fh)

    gross, turn, cost, net, boundary, _dev = phase4(book, monthly_px, rets,
                                                    elig)
    res, _years, _block = phase5(gross, net)

    problems = []
    pairs = [("gate1", "gross_mean"), ("m1", "net_mean"),
             ("m2", "net_sharpe")]
    for key, stat in pairs:
        for end in ("point", "lower", "upper"):
            got, want = res[stat][end], parent[key][end]
            if got != want:
                problems.append("%s.%s reproduces as %r, parent published %r"
                                % (key, end, got, want))
    ca = parent["cost_accounting"]
    if float(turn.sum()) != ca["aggregate_turnover"]:
        problems.append("aggregate turnover does not reproduce")
    if float(cost.sum()) != ca["aggregate_cost"]:
        problems.append("aggregate cost does not reproduce")
    if len(elig) != parent["sample"]["eligible_return_months"]:
        problems.append("parent eligible month count does not reproduce")
    if boundary != [parent["execution_convention"]["entry_trade_boundary_month"]]:
        problems.append("the entry-trade boundary month moved")

    sig_ok = sorted(signal.columns) == sorted(votes.MAPPED)
    if not sig_ok:
        problems.append("the signal frame is not the sealed 15 instruments")

    say("  parent statistics reproduce EXACTLY from this run's book:")
    say("     gross mean, net mean, net Sharpe, all three 95%% intervals")
    say("     aggregate turnover %.4f and aggregate cost %.6f"
        % (turn.sum(), cost.sum()))
    say("     entry-trade boundary month %s" % (boundary[0] if boundary
                                                else "none"))
    say("  => SIGNAL_IDENTITY_VERIFIED and POSITION_IDENTITY_VERIFIED: the")
    say("     macro feature, the 218-date decision grid, the positions, the")
    say("     wrapper, the cost model and the bootstrap are all UNCHANGED.")
    say("     Only the eligible-return-month index differs.")

    if problems:
        say()
        for p in problems:
            say("  PROBLEM: %s" % p)
        raise Stop("REPAIR_STATUS = HOLD — the repair does not reproduce the "
                   "parent run, so more than the terminal row has changed")
    say("  PARENT REPRODUCTION CONTROL PASSED")
    say()
    return True


# =========================================================================== #

def build_result(res, gross, turn, cost, net, elig, years, block, boundary,
                 devs, removed, added, last_price, pinned, frozen_n,
                 gate05, warmup):
    g1, m1, m2 = res["gross_mean"], res["net_mean"], res["net_sharpe"]
    gate1 = "PASS" if g1["lower"] > 0.0 else "FAIL"
    m1r = "PASS" if m1["lower"] > 0.0 else "FAIL"
    m2r = "PASS" if m2["lower"] > P.M2_TARGET else "FAIL"
    cls, label, status, failure = classify(g1, m1, m2)

    return {
        "schema": {"name": "mmv-s3-repair-result", "version": 1},
        "lineage": LINEAGE,
        "run_id": RUN_ID,
        "run_type": RUN_TYPE,
        "authorization_id": AUTHORIZATION_ID,
        "executed_utc": dt.datetime.now(dt.timezone.utc)
                          .strftime("%Y-%m-%dT%H:%M:%SZ"),
        "supersedes": {
            "parent_run": PARENT_RUN_ID,
            "parent_authorization": PARENT_AUTH_ID,
            "parent_result_artifact": PARENT_JSON,
            "parent_result_sha256": sha256_file(PARENT_JSON),
            "parent_result_status": "INVALID_PRIMARY_SAMPLE",
            "parent_decisional_status": "NONDECISIONAL",
            "statement": "THIS RESULT SUPERSEDES THE PRIOR PRIMARY VERDICT "
                         "FOR DECISIONAL PURPOSES.",
            "parent_preserved_unmodified": True,
            "independent_evidence": False,
            "note": "The two results are the SAME primary trial, one of them "
                    "computed on an invalid sample. They are never to be "
                    "presented as two pieces of evidence.",
        },
        "mmv_od_8": {
            "decision": MMV_OD_8,
            "authority": OD8_AUTHORITY,
            "rule": "a primary monthly return requires the close of the final "
                    "trading day of that calendar month",
            "lockbox_option_a": "truncate the terminal monthly row and state so",
            "lockbox_option_b": "declare in the preregistration that a partial "
                                "terminal month is included and why",
            "sealed_contract_exercised_option_b": False,
            "therefore": "option (a) binds; the parent run did neither, having "
                         "included the row and merely stated that it had",
            "new_scientific_choice": False,
            "decision_grid_altered": False,
        },
        "correction": {
            "original_eligible_return_months": EXPECTED_ORIGINAL_N,
            "repaired_eligible_return_months": len(elig),
            "removed_return_rows": removed,
            "added_return_rows": added,
            "all_earlier_months_identical": True,
            "authoritative_last_price_date": str(last_price.date()),
            "terminal_completeness_rule": "month M is eligible only if the "
                                          "authoritative price panel contains "
                                          "a date strictly after M's last "
                                          "calendar day; a panel that stops "
                                          "inside M cannot establish M's final "
                                          "trading close, so M fails closed",
            "rule_is_structural_not_a_hardcoded_date": True,
            "outcome_affecting_diffs": "TERMINAL_ROW_ONLY",
            "frozen_files_verified_byte_identical": frozen_n,
            "reused_parent_functions": list(REUSED),
            "signal_identity_verified": True,
            "position_identity_verified": True,
        },
        "inputs": {p: sha256_file(p) for p in sorted(pinned)},
        "gate05_accepted": {
            "result": gate05["gate05"]["result"],
            "pooled_agreement_exact": gate05["gate05"]["pooled_agreement_exact"],
            "recomputed_at_repair": False,
            "why_unaffected": "Gate 0.5 compares DECISION-DATE position states "
                              "and never requires the following month to be a "
                              "complete return observation",
        },
        "execution_convention": {
            "return_interval": "month-end close to month-end close, label ME",
            "execution_lag": "held(M) = portfolio weight decided at month-end "
                             "M-1 (shift(1))",
            "information_cutoff": "15:45:00 America/New_York",
            "cost_rule": "%.1f bps one-way x turnover, charged in the month the "
                         "trade executes, subtracted once"
                         % config.TRANSACTION_COST_BPS,
            "entry_trade_boundary_month": boundary[0] if boundary else None,
            "changed_from_parent": False,
        },
        "sample": {
            "decision_months": 218,
            "decision_grid_unchanged": True,
            "eligible_return_months": len(elig),
            "first_return_month": str(elig[0].date()),
            "last_return_month": str(elig[-1].date()),
            "wrapper_warmup_months_excluded": [str(d.date()) for d in warmup],
            "terminal_partial_month_excluded": list(EXPECTED_REMOVED),
            "mapped_instruments": sorted(votes.MAPPED),
            "mapped_instrument_n": 15,
            "unmapped": sorted(votes.NOT_MAPPED),
            "calendar_year_blocks": years,
            "block_months": {str(k): v for k, v in block.items()},
        },
        "risk_wrapper": dict(P.risk.WRAPPER_AUTHORITY),
        "cost_accounting": {
            "one_way_bps": config.TRANSACTION_COST_BPS,
            "aggregate_turnover": float(turn.sum()),
            "mean_monthly_turnover": float(turn.mean()),
            "aggregate_cost": float(cost.sum()),
            "mean_monthly_cost": float(cost.mean()),
            "canonical_reconciliation_max_abs_deviation": devs,
            "reconciliation_identity_bound": P.RECON_TOL,
            "reconciliation_bound_is_not_a_research_threshold": True,
        },
        "inference": {
            "method": "calendar-year block bootstrap over FROZEN monthly "
                      "strategy tuples, unchanged from the parent run",
            "B": P.BOOTSTRAP_B,
            "interval": "95% percentile (2.5 / 97.5)",
            "common_draw_set": True,
            "rng_seed": P.RNG_SEED,
            "boundary_block_semantics": "a calendar year is ONE block whatever "
                                        "its month count; the 2026 block loses "
                                        "its terminal month and is drawn as a "
                                        "5-month block. This is the same rule "
                                        "that already produced a 4-month 2008 "
                                        "block in the parent run",
            "boundary_semantics_unambiguous": True,
            "hac_or_second_bootstrap": False,
        },
        "gate1": {"statistic": "mean monthly GROSS MMV portfolio return",
                  "rule": "lower 95% endpoint > 0, STRICT",
                  "result": gate1, **g1},
        "m1": {"statistic": "mean monthly NET MMV portfolio return",
               "rule": "lower 95% endpoint > 0, STRICT",
               "result": m1r, **m1},
        "m2": {"statistic": "annualised NET Sharpe, rf = 0, ddof = 1, x sqrt(12)",
               "rule": "lower 95%% endpoint > %+.2f, STRICT" % P.M2_TARGET,
               "target": P.M2_TARGET, "result": m2r, **m2},
        "verdict": {
            "terminal_class": cls,
            "class_label": label,
            "programme_status": status,
            "failure_type": failure,
            "evidence_ceiling": "supported",
            "never": ["confirmed", "independently confirmed"],
            "classification_rule": "contract section K, FIRST MATCH WINS, "
                                   "applied from scratch; the parent's class "
                                   "was NOT carried forward",
            "old_result_decisional": False,
            "new_result_decisional": True,
        },
        "trial_accounting": {
            "trial_family": "F-MMV",
            "m": 1,
            "trial_count_increment": 0,
            "is_new_trial": False,
            "is_independent_evidence": False,
        },
        "firewall": {
            "RETURN_OUTCOME_ACCESSED": True,
            "FIRST_RELEASE_DIAGNOSTIC_RUN": False,
            "PER_INSTRUMENT_RETURN_DIAGNOSTICS_RUN": False,
            "PER_LEG_RETURN_DIAGNOSTICS_RUN": False,
            "ALTERNATIVE_PARAMETER_CELL_RUN": False,
            "ALTERNATIVE_SAMPLE_ENDPOINT_RUN": False,
            "DRAWDOWN_COMPUTED": False,
            "HIT_RATE_COMPUTED": False,
            "ROLLING_SHARPE_COMPUTED": False,
            "YEARLY_RANKINGS_COMPUTED": False,
            "ALTERNATIVE_COST_RUN": False,
            "ALTERNATE_BOOTSTRAP_RUN": False,
            "GATE05_RERUN": False,
            "RESCUE_ANALYSIS_PERFORMED": False,
            "PARENT_ARTIFACT_MODIFIED": False,
        },
        "no_rescue": "No series, transform, coefficient, mapping, threshold, "
                     "cost, target, bootstrap, sample rule or execution rule "
                     "may be changed after this result. Any further hypothesis "
                     "requires a NEW LINEAGE with its own preregistration and "
                     "seal.",
    }, cls, status, failure, gate1, m1r, m2r


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--preflight", action="store_true")
    a = ap.parse_args()
    if a.execute == a.preflight:
        say("choose exactly one of --preflight or --execute")
        return 2

    _grant, pinned = phase0(a.execute)
    frozen_n = phase_diff_audit()
    gate05 = phase1()
    dec, raw, _ur = phase2()
    prices = load_prices()
    book, signal, monthly_px, rets, elig, warmup = phase3(dec, raw, prices)
    repaired, removed, added, last_price = phase_terminal(prices, elig)

    if a.preflight:
        say("=" * 78)
        say("PREFLIGHT COMPLETE — the correction is exactly one terminal row.")
        say("No repaired statistic was produced and nothing was consumed.")
        say("=" * 78)
        return 0

    phase_parent_control(book, monthly_px, rets, elig, signal)

    say("PHASE D — REPAIRED PRIMARY SERIES AND INFERENCE")
    gross, turn, cost, net, boundary, devs = phase4(book, monthly_px, rets,
                                                    repaired)
    res, years, block = phase5(gross, net)

    result, cls, status, failure, g1r, m1r, m2r = build_result(
        res, gross, turn, cost, net, repaired, years, block, boundary, devs,
        removed, added, last_price, pinned, frozen_n, gate05, warmup)

    g1, m1, m2 = res["gross_mean"], res["net_mean"], res["net_sharpe"]
    say("PHASE E — GATES AND SEALED CLASSIFICATION  (applied from scratch)")
    say("  GATE 1  gross mean    %+.8f   95%% [%+.8f, %+.8f]   %s"
        % (g1["point"], g1["lower"], g1["upper"], g1r))
    say("  M1      net mean      %+.8f   95%% [%+.8f, %+.8f]   %s"
        % (m1["point"], m1["lower"], m1["upper"], m1r))
    say("  M2      net Sharpe    %+.6f     95%% [%+.6f, %+.6f]   %s"
        % (m2["point"], m2["lower"], m2["upper"], m2r))
    say()
    say("  TERMINAL CLASS   %s — %s" % (cls, result["verdict"]["class_label"]))
    say("  PROGRAMME_STATUS %s" % status)
    say("  FAILURE_TYPE     %s" % failure)
    say("  EVIDENCE CEILING supported   (never confirmed)")
    say()

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(RESULT_JSON, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(result, fh, indent=1, sort_keys=True)
        fh.write("\n")
    say("=" * 78)
    say("REPAIRED RESULT  %s" % RESULT_JSON)
    say("sha256           %s" % sha256_file(RESULT_JSON))
    say()
    say("PARENT PRESERVED %s" % PARENT_JSON)
    say("sha256           %s   (unchanged)" % sha256_file(PARENT_JSON))
    say()
    say("Mark %s CONSUMED. TRIAL_COUNT_INCREMENT = 0."
        % AUTHORIZATION_ID)
    say("=" * 78)
    return 0


if __name__ == "__main__":
    sys.exit(main())
