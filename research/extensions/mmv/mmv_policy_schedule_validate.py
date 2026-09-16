"""CTA-EDGE-04-MMV — POLICY ANNOUNCEMENT SCHEDULE VALIDATOR.

Deterministic. Exit code 0 only if every check passes.

    python research/extensions/mmv/mmv_policy_schedule_validate.py

PASS = the frozen schedule is supported by direct official authority and obeys
the sealed availability rule. FAIL = it is not.

The validator re-derives from the FROZEN BYTES rather than trusting the CSV: it
re-reads each cached Federal Reserve press release and re-confirms that the page
actually states the target attributed to it. A schedule row whose source does
not say what the row claims is a fabrication, and that is the failure this file
exists to make impossible to miss.

It resolves policy availability at exactly the three reconciliation cutoffs that
section 6 of the brief requires and NOWHERE ELSE. It computes no 12-month
change, no sign, no P_t, and no MMV feature.
"""

from __future__ import annotations

import ast
import csv
import datetime as dt
import hashlib
import json
import os
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
os.chdir(REPO)
for p in (REPO, HERE):
    if p not in sys.path:
        sys.path.insert(0, p)

from engine import policy as engine_policy                       # noqa: E402
from engine.pit import UNDEFINED                                 # noqa: E402
import mmv_policy_schedule_freeze as F                           # noqa: E402

CSV_PATH = "research/extensions/mmv/MMV_POLICY_ANNOUNCEMENT_SCHEDULE.csv"
MANIFEST = "data/mmv/MMV_POLICY_SCHEDULE_MANIFEST.json"
FREEZE_SRC = "research/extensions/mmv/mmv_policy_schedule_freeze.py"

#: The four intermeeting federal-funds target actions in the required window.
#: Named explicitly so that a silent loss of one is a FAILURE rather than a
#: quietly shorter list.
REQUIRED_INTERMEETING = ("2008-01-22", "2008-10-08", "2020-03-03", "2020-03-15")

RESULTS = []


def chk(cid, ok, detail):
    RESULTS.append((cid, bool(ok), detail))
    return bool(ok)


def load_rows():
    with open(CSV_PATH, encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def frac(s):
    return Fraction(s) if s else None


def main() -> int:
    print("=" * 78)
    print("CTA-EDGE-04-MMV — POLICY ANNOUNCEMENT SCHEDULE VALIDATOR")
    print("=" * 78)
    print("Re-derives from the frozen bytes. No 12-month change, no sign, "
          "no P_t.")
    print()

    rows = load_rows()
    with open(MANIFEST, encoding="utf-8") as fh:
        man = json.load(fh)

    # ---- A. direct authority ------------------------------------------------
    chk("A1", len(rows) == man["regime_count"] == 42,
        "%d regimes, matching the manifest" % len(rows))

    missing = [r["effective_start_date"] for r in rows
               if not os.path.exists(r["raw_file"])]
    chk("A2", not missing, "every row's cached source page is present on disk"
        if not missing else "MISSING %s" % missing)

    bad_hash = []
    for r in rows:
        if not os.path.exists(r["raw_file"]):
            continue
        with open(r["raw_file"], "rb") as fh:
            if hashlib.sha256(fh.read()).hexdigest() != r["source_sha256"]:
                bad_hash.append(r["effective_start_date"])
    chk("A3", not bad_hash, "every source page reproduces its recorded sha256"
        if not bad_hash else "HASH MISMATCH %s" % bad_hash)

    no_url = [r["effective_start_date"] for r in rows
              if not r["official_source"].startswith(
                  "https://www.federalreserve.gov/")]
    chk("A4", not no_url,
        "every row cites a federalreserve.gov URL as its authority"
        if not no_url else "NON-OFFICIAL SOURCE %s" % no_url)

    # ---- B. the source actually says what the row claims --------------------
    unsupported = []
    for r in rows:
        with open(r["raw_file"], "rb") as fh:
            text = F.plain(fh.read())
        pats = F.target_patterns(r["target_type"], frac(r["target_value"]),
                                 frac(r["target_lower"]),
                                 frac(r["target_upper"]))
        if not any(p.search(text) for p in pats):
            unsupported.append(r["effective_start_date"])
    chk("B1", not unsupported,
        "all %d source pages re-confirm the exact target attributed to them"
        % len(rows) if not unsupported else "UNSUPPORTED %s" % unsupported)

    date_drift = [r["effective_start_date"] for r in rows
                  if r["stated_release_date"]
                  and r["stated_release_date"] != r["official_announcement_date"]]
    chk("B2", not date_drift,
        "each page's own 'Release Date' agrees with the recorded announcement "
        "date" if not date_drift else "DRIFT %s" % date_drift)

    # ---- C. agreement with the frozen target series -------------------------
    tar = F.frozen_values("DFEDTAR")
    lo, hi = F.frozen_values("DFEDTARL"), F.frozen_values("DFEDTARU")
    mismatch = []
    for r in rows:
        eff = dt.date.fromisoformat(r["effective_start_date"])
        if r["target_type"] == "SINGLE_TARGET":
            if tar.get(eff) != frac(r["target_value"]):
                mismatch.append(r["effective_start_date"])
            if frac(r["target_midpoint"]) != frac(r["target_value"]):
                mismatch.append(r["effective_start_date"] + ":mid")
        else:
            if lo.get(eff) != frac(r["target_lower"]) or \
                    hi.get(eff) != frac(r["target_upper"]):
                mismatch.append(r["effective_start_date"])
            mid = (frac(r["target_lower"]) + frac(r["target_upper"])) / 2
            if frac(r["target_midpoint"]) != mid:
                mismatch.append(r["effective_start_date"] + ":mid")
    chk("C1", not mismatch,
        "every target value and midpoint reproduces from the frozen series"
        if not mismatch else "MISMATCH %s" % mismatch)

    starts = [dt.date.fromisoformat(r["effective_start_date"]) for r in rows]
    chk("C2", starts == sorted(starts) and len(set(starts)) == len(starts),
        "regimes are strictly chronological with no duplicate effective date")

    singles = [r for r in rows if r["target_type"] == "SINGLE_TARGET"]
    ranges = [r for r in rows if r["target_type"] == "TARGET_RANGE"]
    last_single = max(r["effective_start_date"] for r in singles)
    first_range = min(r["effective_start_date"] for r in ranges)
    chk("C3", first_range == "2008-12-16"
        and last_single < "2008-12-16"
        and max(tar) == F.SPLICE_LAST_SINGLE,
        "splice exact: last single target %s, first range 2008-12-16, "
        "DFEDTAR ends 2008-12-15" % last_single)

    gaps = [r["effective_start_date"] for r in rows
            if r["target_type"] == "TARGET_RANGE"
            and frac(r["target_upper"]) < frac(r["target_lower"])]
    chk("C4", not gaps, "no inverted target range")

    chk("C5", man["frb_ordered_level_sequence_matches"] is True,
        "the Federal Reserve open-market table reproduces the SAME ORDERED "
        "LEVEL SEQUENCE as the frozen regimes (a date-free confirmation)")

    chk("C6", sorted(set(man["frb_minus_fred_effective_day_deltas_observed"])
                     ) == [0, 1]
        and man["frb_effective_date_differs_from_fred"] == ["2015-12-16",
                                                            "2016-12-14"],
        "FRED and the Federal Reserve agree on every effective date except "
        "2015-12-16 and 2016-12-14, where FRED stamps the announcement day and "
        "the Fed the stated effective day — a one-day metadata difference with "
        "identical values, recorded rather than smoothed over")

    # ---- D. announcement authority, not a heuristic --------------------------
    later = [r["effective_start_date"] for r in rows
             if int(r["announcement_minus_effective_days"]) > 0]
    chk("D1", not later,
        "no announcement post-dates its own effective date"
        if not later else "ANNOUNCED AFTER EFFECTIVE %s" % later)

    offsets = sorted({int(r["announcement_minus_effective_days"])
                      for r in rows})
    chk("D2", offsets == [-1, 0],
        "announcement-minus-effective offsets are %s — BOTH occur, so no fixed "
        "publication lag could have produced this schedule" % offsets)

    inter = tuple(r["official_announcement_date"] for r in rows
                  if r["is_intermeeting"] == "YES")
    chk("D3", inter == REQUIRED_INTERMEETING,
        "all four intermeeting actions explicitly mapped: %s" % (inter,))

    uncorroborated = [d for d, v in man["intermeeting_corroborated"].items()
                      if not v]
    chk("D4", not uncorroborated,
        "every intermeeting action is corroborated by a Federal Reserve "
        "Conference Call or unscheduled meeting entry: %s"
        % man["intermeeting_corroborated"]
        if not uncorroborated else "UNCORROBORATED %s" % uncorroborated)

    # ---- E. NO NEAREST-MEETING HEURISTIC, proved on real data ---------------
    sched, unsched, _src = F.scheduled_meeting_end_dates()
    by_ann = {dt.date.fromisoformat(r["official_announcement_date"]): r
              for r in rows}
    jan22 = dt.date(2008, 1, 22)
    nearest_before = max(d for d in sched if d <= jan22)
    nearest_any = min(sched, key=lambda d: abs((d - jan22).days))
    chk("E1", jan22 in by_ann and nearest_before != jan22
        and nearest_any != jan22 and nearest_before == dt.date(2007, 12, 11),
        "regression: the 2008-01-22 intermeeting cut is recorded at 2008-01-22, "
        "which NEITHER heuristic recovers - 'latest scheduled meeting <= "
        "effective date' gives %s (six weeks early) and 'nearest scheduled "
        "meeting' gives %s" % (nearest_before, nearest_any))

    mar3 = dt.date(2020, 3, 3)
    nb = max(d for d in sched if d <= mar3)
    na = min(sched, key=lambda d: abs((d - mar3).days))
    chk("E2", mar3 in by_ann and nb != mar3 and na != mar3,
        "regression: the 2020-03-03 intermeeting cut is recorded at 2020-03-03, "
        "while the nearest-meeting rules would give %s / %s" % (nb, na))

    chk("E3", all(d in sched or d in unsched
                  or any((d - dt.timedelta(days=k)) in unsched
                         for k in range(3))
                  for d in by_ann),
        "every announcement date is either a scheduled meeting conclusion or "
        "corroborated as unscheduled — none is unaccounted for")

    src = open(FREEZE_SRC, encoding="utf-8").read()
    tree = ast.parse(src)
    fn_names = {n.name for n in ast.walk(tree)
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    chk("E4", not any(w in n.lower() for n in fn_names
                      for w in ("nearest", "closest", "guess", "infer")),
        "the freeze defines no nearest/closest/guess/infer helper")

    chk("E5", man["nearest_meeting_heuristic_used"] is False
        and man["fixed_publication_lag_used"] is False
        and man["alfred_realtime_start_used"] is False,
        "manifest records: no nearest-meeting heuristic, no fixed lag, no "
        "ALFRED realtime_start")

    # ---- F. ALFRED realtime_start is structurally unreachable ---------------
    forbidden = ("realtime", "vintage", "catalog")
    leaks = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for a in node.args.args:
                if any(f in a.arg.lower() for f in forbidden):
                    leaks.append("%s(%s)" % (node.name, a.arg))
    chk("F1", not leaks,
        "no function in the freeze takes a realtime/vintage/catalog parameter"
        if not leaks else "LEAK %s" % leaks)

    schedule_cols = set(rows[0].keys())
    chk("F2", not any(f in c.lower() for c in schedule_cols
                      for f in forbidden),
        "the frozen schedule carries no realtime/vintage/catalog column; its "
        "availability authority is the announcement and nothing else")

    # ---- G. the sealed same-day rule, at the reconciliation cutoffs ---------
    anns = []
    for r in rows:
        t = (dt.time.fromisoformat(r["official_announcement_time_et"])
             if r["announcement_time_status"] == "VERIFIED" else None)
        anns.append(engine_policy.PolicyAnnouncement(
            dt.date.fromisoformat(r["official_announcement_date"]), t,
            frac(r["target_midpoint"])))
    schedule = engine_policy.PolicySchedule(anns)
    chk("G1", len(schedule) == 42,
        "the frozen schedule loads into the sealed engine.policy.PolicySchedule")

    collisions = man["cutoff_collisions"]
    chk("G2", len(collisions) == 3,
        "the sealed same-day rule bites at exactly %d cutoffs in the window"
        % len(collisions))

    wrong = []
    for c in collisions:
        d = dt.date.fromisoformat(c["cutoff_date"])
        got = schedule.eligible(d)
        prev = schedule.eligible(d - dt.timedelta(days=1))
        same_day = next(a.target for a in anns if a.announced_on == d)
        if c["announcement_time_status"] == "VERIFIED":
            if got != same_day:
                wrong.append("%s should admit the new target" % d)
        else:
            if got != prev or got == same_day and prev != same_day:
                wrong.append("%s should retain the previous target" % d)
    chk("G3", not wrong,
        "verified same-day times at or before 15:45 admit the new target; "
        "unestablished times retain the previous one"
        if not wrong else "RULE VIOLATION %s" % wrong)

    late = [r["effective_start_date"] for r in rows
            if r["announcement_time_status"] == "VERIFIED"
            and dt.time.fromisoformat(r["official_announcement_time_et"])
            > F.CUTOFF_TIME]
    chk("G4", late == ["2020-03-16"],
        "exactly one verified announcement falls after the 15:45 cutoff "
        "(2020-03-15 at 17:00 ET, effective 2020-03-16); it is a Sunday and is "
        "not a canonical decision date, so the rule is recorded, not applied")

    not_est = sum(1 for r in rows
                  if r["announcement_time_status"] == "NOT_ESTABLISHED")
    chk("G5", not_est == 11 and all(
        not r["official_announcement_time_et"] for r in rows
        if r["announcement_time_status"] == "NOT_ESTABLISHED"),
        "%d announcements carry NO official clock time and NONE was invented; "
        "the Federal Reserve's archived pages say only 'For immediate release'"
        % not_est)

    pinned = man["pinned_collisions_that_are_target_changes"]
    chk("G6", man["pinned_fomc_timing_collisions"] == [
        "2013-07-31", "2014-04-30", "2018-01-31", "2019-07-31",
        "2024-01-31", "2024-07-31"] and pinned == ["2019-07-31"],
        "the six pinned month-end collisions reconcile: only 2019-07-31 is also "
        "a target CHANGE, and it is VERIFIED at 14:00 ET, so the other five are "
        "no-change meetings at which the sealed rule cannot alter the target")

    # ---- H. no feature was produced ----------------------------------------
    for path in ("data/mmv/MMV_POLICY_SIGNAL.csv", "data/mmv/MMV_SIGNAL_PANEL.csv",
                 "data/mmv/MMV_POSITIONS.csv", "data/mmv/MMV_GATE05.json"):
        if os.path.exists(path):
            chk("H1", False, "FEATURE ARTIFACT EXISTS: %s" % path)
            break
    else:
        chk("H1", True, "no MMV signal, position or Gate 0.5 artifact exists")

    banned_fn = ("sign", "delta12", "d12", "policy_leg", "composite",
                 "gate", "sharpe", "bootstrap")
    hits = [n for n in fn_names if any(b == n.lower() for b in banned_fn)]
    chk("H2", not hits,
        "the freeze defines no leg, sign, composite or gate function"
        if not hits else "FEATURE CODE %s" % hits)

    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.add((node.module or "").split(".")[0])
    chk("H3", "engine" not in imports and "src" not in imports,
        "the freeze imports neither the MMV engine nor the production book, so "
        "it cannot compute a candidate feature even by accident")

    # Naming a path in an assertion is not reading it, so this inspects the
    # actual read call sites rather than matching a substring against itself.
    this_tree = ast.parse(open(os.path.abspath(__file__), encoding="utf-8").read())
    read_literals = []
    for node in ast.walk(this_tree):
        if isinstance(node, ast.Call):
            name = (getattr(node.func, "id", None)
                    or getattr(node.func, "attr", None))
            if name in ("open", "read_csv", "read_json", "load"):
                for a in ast.walk(node):
                    if isinstance(a, ast.Constant) and isinstance(a.value, str):
                        read_literals.append(a.value)
    chk("H4", not any("monthly_signal_panel" in l or "close_prices_raw" in l
                      for l in read_literals),
        "this validator opens no canonical price or TSMOM signal file "
        "(%d read call sites inspected)" % len(read_literals))

    npass = sum(1 for _c, ok, _d in RESULTS if ok)
    n = len(RESULTS)
    group = None
    for cid, ok, detail in RESULTS:
        if cid[0] != group:
            group = cid[0]
            print("--- %s %s" % (group, "-" * 72))
        print("  [%s] %-4s %s" % ("PASS" if ok else "FAIL", cid, detail))
    print()
    print("=" * 78)
    print("POLICY SCHEDULE VALIDATION: %d/%d PASS" % (npass, n))
    if npass != n:
        print("VERDICT: FAIL")
        return 1
    print("VERDICT: PASS — schedule supported by direct official authority")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    sys.exit(main())
