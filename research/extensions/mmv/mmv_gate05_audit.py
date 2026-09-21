"""CTA-EDGE-04-MMV — POST-GATE-0.5 STATIC / ARTIFACT AUDIT.

    python research/extensions/mmv/mmv_gate05_audit.py

STATIC ONLY. This module does NOT rerun Gate 0.5, does NOT recompute the
historical agreement statistic, does NOT touch returns, and creates no
authorization. It reads COMMITTED code, the committed result artifact, the
frozen policy schedule, and runs one SYNTHETIC representation test.

The primary question is whether the committed historical driver converted the
canonical TSMOM COMPOSITE to a three-valued sign BEFORE the Gate 0.5 equality
comparison. The audit answers it three independent ways:

  1. by TRACING the committed code path, line by line;
  2. by a SYNTHETIC test over every composite value the panel can carry;
  3. by an IMPOSSIBILITY argument — the sealed gate rejects any value outside
     {-1, 0, +1}, so a run that completed cannot have compared fractions.

The third is the strongest and needs no trust in the first two.
"""

from __future__ import annotations

import csv
import datetime as dt
import json
import os
import re
import subprocess
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
os.chdir(REPO)
for p in (REPO, HERE):
    if p not in sys.path:
        sys.path.insert(0, p)

from engine import gate05, policy, votes                         # noqa: E402
from engine.pit import UNDEFINED, ContractViolation              # noqa: E402
import mmv_authorization                                         # noqa: E402

DRIVER = "research/extensions/mmv/mmv_gate05_run.py"
ENGINE_GATE = "research/extensions/mmv/engine/gate05.py"
PANEL = "output/monthly_signal_panel.csv"
SCHEDULE = "research/extensions/mmv/MMV_POLICY_ANNOUNCEMENT_SCHEDULE.csv"
FOMC_TIMING = "data/mmv/MMV_FOMC_TIMING_MANIFEST.json"
RESULT = "research/extensions/mmv/gate05/MMV_GATE05_RESULT.json"

DECISIONS_FROM, DECISIONS_TO = "2008-05-31", "2026-06-30"

#: The full composite alphabet the canonical panel can carry.
COMPOSITE_ALPHABET = ["-1", "-0.75", "-0.5", "-0.25", "0",
                      "0.25", "0.5", "0.75", "1"]
EXPECTED_SIGNS = [-1, -1, -1, -1, 0, 1, 1, 1, 1]

RESULTS = []


def chk(cid, ok, detail):
    RESULTS.append((cid, bool(ok), detail))
    return bool(ok)


def committed(path, rev="HEAD"):
    out = subprocess.run(["git", "show", "%s:%s" % (rev, path)],
                         cwd=REPO, capture_output=True, text=True)
    if out.returncode != 0:
        raise SystemExit("cannot read committed %s" % path)
    return out.stdout


def lineno(text, needle, start=1):
    for i, line in enumerate(text.splitlines(), start=1):
        if needle in line and i >= start:
            return i, line.strip()
    return None, None


# --------------------------------------------------------------------------- #
# 1-2. REPRESENTATION AUDIT — trace the committed code path
# --------------------------------------------------------------------------- #

def audit_representation():
    drv = committed(DRIVER)
    eng = committed(ENGINE_GATE)

    n_reader, _ = lineno(drv, "def canonical_signs(")
    # search from the reader's own first line: `with open(PANEL` also occurs in
    # decision_dates() earlier in the file, and an audit that cites the wrong
    # line is not an audit.
    n_open, l_open = lineno(drv, "with open(PANEL", start=n_reader)
    n_parse, l_parse = lineno(drv, "v = Fraction(cell)")
    n_norm, l_norm = lineno(drv, "(v > 0) - (v < 0)")
    n_undef, l_undef = lineno(drv, 'out[(d, inst)] = UNDEFINED')
    n_call, l_call = lineno(drv, "tsmom, tsmom_undef = canonical_signs(dec)")
    n_eval, l_eval = lineno(drv, "out = gate05.evaluate(raw, tsmom)")
    n_valid, l_valid = lineno(eng, "VALID_SIGNS = ")
    n_check, _ = lineno(eng, "def _check_sign(")
    n_raise, l_raise = lineno(eng, "if value not in VALID_SIGNS")
    n_applyt, l_applyt = lineno(eng, "t = _check_sign(tsmom_signs.get")
    n_eq, l_eq = lineno(eng, "if m == t:")

    print("--- 1/2  REPRESENTATION AUDIT: committed code path " + "-" * 25)
    print("  canonical panel reader      %s:%d  canonical_signs()"
          % (DRIVER, n_reader))
    print("     open                     :%d  %s" % (n_open, l_open))
    print("     parsed value type        :%d  %s  (exact rational, not float)"
          % (n_parse, l_parse))
    print("     empty cell               :%d  %s" % (n_undef, l_undef))
    print("  NORMALIZATION FUNCTION      %s:%d" % (DRIVER, n_norm))
    print("     %s" % l_norm)
    print("     -> inline three-valued sign: positive->+1, negative->-1, 0->0")
    print("  Gate 0.5 input construction %s:%d  %s" % (DRIVER, n_call, l_call))
    print("     handed to               %s:%d  %s" % (DRIVER, n_eval, l_eval))
    print("  type guard                  %s:%d  %s"
          % (ENGINE_GATE, n_valid, l_valid))
    print("     _check_sign             :%d, raises at :%d  %s"
          % (n_check, n_raise, l_raise))
    print("     applied to canonical    :%d  %s" % (n_applyt, l_applyt))
    print("  EXACT EQUALITY              %s:%d  %s" % (ENGINE_GATE, n_eq, l_eq))
    print()

    normalized = bool(n_norm) and n_norm > n_parse
    chk("R1", normalized,
        "the committed reader applies (v > 0) - (v < 0) to every parsed "
        "composite at %s:%d, BEFORE the value enters the gate" % (DRIVER, n_norm))
    chk("R2", n_eq is not None and n_applyt is not None and n_applyt < n_eq,
        "the canonical value passes the ternary type guard at %s:%d before the "
        "equality at :%d" % (ENGINE_GATE, n_applyt, n_eq))
    return {"reader": "%s:%d canonical_signs()" % (DRIVER, n_reader),
            "parse": "%s:%d Fraction(cell)" % (DRIVER, n_parse),
            "normalization": "%s:%d (v > 0) - (v < 0)" % (DRIVER, n_norm),
            "gate_input": "%s:%d gate05.evaluate(raw, tsmom)" % (DRIVER, n_eval),
            "type_guard": "%s:%d _check_sign" % (ENGINE_GATE, n_check),
            "equality": "%s:%d if m == t" % (ENGINE_GATE, n_eq)}


# --------------------------------------------------------------------------- #
# 3. SYNTHETIC REPRESENTATION TEST — authorized
# --------------------------------------------------------------------------- #

def synthetic_normalization():
    print("--- 3  SYNTHETIC REPRESENTATION TEST " + "-" * 39)
    got = []
    for cell in COMPOSITE_ALPHABET:
        v = Fraction(cell)
        got.append((v > 0) - (v < 0))          # the exact committed expression
    print("     input  %s" % COMPOSITE_ALPHABET)
    print("     output %s" % got)
    print("     expect %s" % EXPECTED_SIGNS)
    ok = got == EXPECTED_SIGNS
    chk("S1", ok, "the committed normalization maps the full composite "
        "alphabet to exactly [-1,-1,-1,-1,0,+1,+1,+1,+1]")

    # and the sealed gate accepts the normalized values while REJECTING raw ones
    d = dt.date(2020, 1, 31)
    accepted = True
    try:
        gate05.evaluate({(d, "SPY"): 1}, {(d, "SPY"): 1})
    except ContractViolation:
        accepted = False
    rejected = False
    try:
        gate05.evaluate({(d, "SPY"): 1}, {(d, "SPY"): Fraction(1, 2)})
    except ContractViolation:
        rejected = True
    chk("S2", accepted and rejected,
        "the sealed gate ACCEPTS a normalized sign and REJECTS a raw composite "
        "of 1/2 with ContractViolation")
    print()
    return ok


# --------------------------------------------------------------------------- #
# The impossibility argument — decisive, and it recomputes nothing
# --------------------------------------------------------------------------- #

def impossibility():
    print("--- IMPOSSIBILITY ARGUMENT " + "-" * 49)
    with open(PANEL, encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    frac_cells = 0
    for r in rows:
        d = r["month_end"][:10]
        if not (DECISIONS_FROM <= d <= DECISIONS_TO):
            continue
        for inst in sorted(votes.MAPPED):
            cell = r[inst].strip()
            if cell == "":
                continue
            v = Fraction(cell)
            if v not in (-1, 0, 1):
                frac_cells += 1

    with open(RESULT, encoding="utf-8") as fh:
        res = json.load(fh)
    eligible = res["gate05"]["eligible_cells"]

    print("     fractional canonical cells inside the decision window,")
    print("     over the 15 mapped instruments               : %d" % frac_cells)
    print("     eligible cells the completed run reported    : %d" % eligible)
    print("     sealed gate rejects any value not in {-1,0,1}: ContractViolation")
    print()
    chk("I1", frac_cells > 0 and eligible == 3270,
        "%d fractional composite cells lie inside the audited window. Had the "
        "run compared raw composites, the ternary type guard would have raised "
        "on the FIRST of them and no result could exist. A completed run "
        "reporting %d eligible cells is therefore only possible with "
        "sign normalization applied first." % (frac_cells, eligible))
    print()
    return frac_cells, eligible


# --------------------------------------------------------------------------- #
# 6-7. COLLISION RECONCILIATION
# --------------------------------------------------------------------------- #

def load_schedule():
    with open(SCHEDULE, encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    anns = []
    for r in rows:
        t = (dt.time.fromisoformat(r["official_announcement_time_et"])
             if r["announcement_time_status"] == "VERIFIED" else None)
        anns.append(policy.PolicyAnnouncement(
            dt.date.fromisoformat(r["official_announcement_date"]), t,
            Fraction(r["target_midpoint"])))
    return policy.PolicySchedule(anns), rows


def collisions():
    print("--- 6/7  COLLISION RECONCILIATION " + "-" * 42)
    timing = json.load(open(FOMC_TIMING, encoding="utf-8"))
    six = sorted(timing["collisions"])
    schedule, sched_rows = load_schedule()
    by_ann = {r["official_announcement_date"]: r for r in sched_rows}
    with open(RESULT, encoding="utf-8") as fh:
        res = json.load(fh)
    cls = res["six_collision_accounting"]["classes"]

    table = []
    for d in six:
        row = by_ann.get(d)
        changed = row is not None
        if changed:
            status = row["announcement_time_status"]
            tm = row["official_announcement_time_et"] or "--"
        else:
            c = timing["collisions"][d]
            status = ("VERIFIED" if c["time_authoritatively_established"]
                      else "NOT_ESTABLISHED")
            tm = c["release_time_stated"] or "--"
        val = schedule.eligible(dt.date.fromisoformat(d))
        table.append({
            "date": d, "fomc_event": "YES",
            "target_change": "YES" if changed else "NO",
            "time_status": status, "time": tm,
            "gate05_class": cls[d],
            "policy_value_used": str(val),
            "reason": ("new target announced 14:00 ET <= 15:45, admitted"
                       if changed and status == "VERIFIED" else
                       "no target/range change at this meeting, so the "
                       "same-day rule has no new value to gate"),
        })

    hdr = ("date", "FOMC?", "change?", "time status", "time", "G0.5",
           "policy value", "reason")
    print("  | %-10s | %-5s | %-7s | %-15s | %-11s | %-4s | %-12s |"
          % hdr[:7])
    print("  |" + "|".join(["-" * 12, "-" * 7, "-" * 9, "-" * 17, "-" * 13,
                            "-" * 6, "-" * 14]) + "|")
    for t in table:
        print("  | %-10s | %-5s | %-7s | %-15s | %-11s | %-4s | %-12s |"
              % (t["date"], t["fomc_event"], t["target_change"],
                 t["time_status"], t["time"], t["gate05_class"],
                 t["policy_value_used"]))
    print()

    a = sum(1 for t in table if t["gate05_class"] == "A")
    b = sum(1 for t in table if t["gate05_class"] == "B")
    c = sum(1 for t in table if t["gate05_class"] == "C")
    chk("C1", a + b + c == 6 and (a, b, c) == (1, 0, 5),
        "six S1 collisions classify A=%d B=%d C=%d, summing to 6" % (a, b, c))

    # the two lagged cutoffs
    lagged = ["2007-10-31", "2008-04-30"]
    in_six = [d for d in lagged if d in six]
    in_window = [d for d in lagged
                 if DECISIONS_FROM <= d <= DECISIONS_TO]
    chk("C2", not in_six,
        "2007-10-31 and 2008-04-30 are NOT among the six S1 collision dates")
    chk("C3", not in_window,
        "neither lagged cutoff lies in the decision window %s..%s, so neither "
        "could ever have been one of the six (which are DECISION dates)"
        % (DECISIONS_FROM, DECISIONS_TO))
    for d in lagged:
        row = by_ann.get(d)
        chk("C4", row is not None and
            row["announcement_time_status"] == "NOT_ESTABLISHED",
            "%s IS a target-change announcement with time NOT_ESTABLISHED "
            "-> previous target retained (%s effective)"
            % (d, row["effective_start_date"] if row else "?"))
    print()
    return table, (a, b, c), lagged


# --------------------------------------------------------------------------- #
# 8. GUARD AUDIT — static
# --------------------------------------------------------------------------- #

LIFECYCLE_NO_LINEAGE = """```json
{
 "authorization_id": "MMV-AUTH-0001",
 "event": "CONSUMED",
 "record_type": "LIFECYCLE",
 "schema": {"name": "mmv-execution-authorization", "version": 1}
}
```"""

FOREIGN_LINEAGE = """```json
{
 "authorization_id": "MMV-AUTH-0001",
 "event": "CONSUMED",
 "lineage": "SOME-OTHER-LINEAGE",
 "record_type": "LIFECYCLE",
 "schema": {"name": "mmv-execution-authorization", "version": 1}
}
```"""


def guards():
    print("--- 8  AUTHORIZATION / CONSUMPTION GUARD " + "-" * 35)
    src = committed("research/extensions/mmv/mmv_authorization.py")

    # repair 1: consumption is read from committed state UNION the working tree
    n_wt, _ = lineno(src, "def read_worktree(")
    n_cons, _ = lineno(src, "def consumed_ids(")
    uses_wt = "read_worktree(LEDGER_RELPATH)" in src
    grants_committed = "return _scoped(read_committed(LEDGER_RELPATH, rev))" in src
    chk("G1", n_wt and n_cons and uses_wt and grants_committed,
        "consumed_ids() unions committed records with the WORKING TREE "
        "(mmv_authorization.py:%d), while grants come only from committed "
        "state — blocking does not require a commit, granting does" % n_cons)

    # repair 2: a lifecycle record without `lineage` is not dropped
    got = mmv_authorization._scoped(LIFECYCLE_NO_LINEAGE)
    chk("G2", len(got) == 1 and got[0]["event"] == "CONSUMED",
        "a LIFECYCLE record carrying NO lineage field is retained by _scoped "
        "(it would previously have been silently dropped, failing open)")

    foreign = mmv_authorization._scoped(FOREIGN_LINEAGE)
    chk("G3", not foreign,
        "a record declaring a DIFFERENT lineage is still rejected, so the "
        "relaxation did not widen scope")

    st = mmv_authorization.status()
    chk("G4", st["authorized"] is False and "CONSUMED" in st["reason"],
        "live status: %s" % st["reason"])

    drv = committed(DRIVER)
    n_art, l_art = lineno(drv, "if os.path.exists(RESULT_JSON)")
    chk("G5", n_art is not None,
        "the driver independently refuses when a result artifact exists "
        "(%s:%d), so two layers block a rerun" % (DRIVER, n_art))
    print()
    return st


def main() -> int:
    print("=" * 78)
    print("CTA-EDGE-04-MMV — POST-GATE-0.5 STATIC AUDIT")
    print("=" * 78)
    print("No rerun. No recomputation of the agreement statistic. No returns.")
    print()

    trace = audit_representation()
    syn = synthetic_normalization()
    frac_cells, eligible = impossibility()
    table, abc, lagged = collisions()
    st = guards()

    npass = sum(1 for _c, ok, _d in RESULTS if ok)
    n = len(RESULTS)
    print("--- FINDINGS " + "-" * 63)
    for cid, ok, detail in RESULTS:
        print("  [%s] %-4s %s" % ("PASS" if ok else "FAIL", cid, detail))
    print()
    print("=" * 78)
    print("AUDIT: %d/%d PASS" % (npass, n))
    print("VERDICT: %s" % ("PASS" if npass == n else "FAIL"))
    print("=" * 78)
    return 0 if npass == n else 1


if __name__ == "__main__":
    sys.exit(main())
