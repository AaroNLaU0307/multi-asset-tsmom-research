"""CTA-EDGE-04-MMV — the single authorized historical PnL-free Gate 0.5 run.

    python research/extensions/mmv/mmv_gate05_run.py --execute

Authorized by MMV-AUTH-0001 under run_id MMV-GATE05-20260917-01, read from
COMMITTED git state. Deterministic: no RNG, no resampling, no tie-break.

PHASES, in order, each a hard stop:

    0  AUTHORIZATION   the committed grant, the run_id, every pinned input hash
    1  PRE-RUN         six-collision accounting, policy coverage through sample
                       end, and the single canonical direction input pinned
    2  FEATURE         the FIRST historical construction of G, I, P and raw
    3  STRUCTURAL      the sealed sanity gate; ANY unexplained undefinedness
                       stops the run BEFORE pooled agreement is computed
    4  GATE 0.5        the single primary statistic, exact integer counts

Phases 0, 1 and 3 abort before any pooled agreement exists, so a failure there
spends nothing.

DIAGNOSTIC EXPOSURE IS DELIBERATELY MINIMAL. Per-instrument, per-leg and
calendar-period agreement are preregistered as non-promotional but are NOT
required for this kill decision, so they are NEVER COMPUTED here — not computed
and withheld, not computed at all.

ABSOLUTE RETURN FIREWALL. This module reads no price, no return, no cost and no
performance statistic. It opens exactly one canonical file, the sealed monthly
SIGNAL panel, and reads only its direction cells.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import os
import sys
from collections import Counter
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
os.chdir(REPO)
for p in (REPO, HERE):
    if p not in sys.path:
        sys.path.insert(0, p)

from engine import gate05, legs, policy, votes                   # noqa: E402
from engine.pit import UNDEFINED, VintageSeries, months_back     # noqa: E402
import mmv_authorization                                         # noqa: E402

RUN_ID = "MMV-GATE05-20260917-01"
RUN_TYPE = "HISTORICAL_PNL_FREE_SEPARABILITY"

OUT_DIR = os.path.join("research", "extensions", "mmv", "gate05")
RESULT_JSON = os.path.join(OUT_DIR, "MMV_GATE05_RESULT.json")

PANEL = "output/monthly_signal_panel.csv"
SCHEDULE = "research/extensions/mmv/MMV_POLICY_ANNOUNCEMENT_SCHEDULE.csv"
FOMC_TIMING = "data/mmv/MMV_FOMC_TIMING_MANIFEST.json"

DECISIONS_FROM, DECISIONS_TO = "2008-05-31", "2026-06-30"
LAG_MONTHS = 12

#: Every input this run may read, with the hash the grant pins it at.
PINNED = {
    "research/extensions/mmv/MMV_PREREGISTRATION.md":
        "4bad9f0bcdb7e4991ab920d12e24a60f4d237205e5a43af693a8dadadb56b225",
    "research/extensions/mmv/MMV_SEAL_MANIFEST.md":
        "75016e778ad58e8fe16e4833cf91c19eb52448b4d42138ab265460f371e8c0d5",
    SCHEDULE:
        "ae34bf1e192c4355fb71136a3e3017dfd07525ac8e48d7d3ea102130fa6a11da",
    "data/mmv/INDPRO.observations.realtime.json":
        "3f53f959e399e21a060c6c7ab04392b82950c916826a1c964472d8c78682ddd9",
    "data/mmv/PAYEMS.observations.realtime.json":
        "c773c5681807fe0057dd66814aa18bfc03b8c0201be57a50f425b48e7c471bd6",
    "data/mmv/CPILFENS.observations.realtime.json":
        "75c3c36306c109b11683d808471b30aa8061a2dfc0a4141a6668e6fe8b9ad2f4",
    PANEL:
        "fa154e01ec597070729b5489ee4f8ed0e588add30c70d33196d7bf3c8069173f",
}


class Stop(RuntimeError):
    """A hard stop. Never caught, never softened into a default."""


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def load_json(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def say(msg=""):
    print(msg, flush=True)


# =========================================================================== #
# PHASE 0 — AUTHORIZATION
# =========================================================================== #

def phase0():
    say("=" * 78)
    say("CTA-EDGE-04-MMV — HISTORICAL PnL-FREE GATE 0.5")
    say("=" * 78)
    say("PHASE 0 — AUTHORIZATION")

    grant = mmv_authorization.require(RUN_ID)
    binding = grant["binding"]
    say("  grant            %s  (%s)" % (grant["authorization_id"],
                                         grant["scope"]))
    say("  run_id           %s" % binding["run_id"])
    say("  rng_seed         %r  (deterministic: no resampling exists)"
        % binding["rng_seed"])
    if binding["rng_seed"] is not None:
        raise Stop("the grant carries an RNG seed; this run is deterministic "
                   "and a seed would imply a stochastic step the seal "
                   "does not contain")

    bad = []
    for path, want in sorted(PINNED.items()):
        if not os.path.exists(path):
            bad.append("%s MISSING" % path)
            continue
        got = sha256_file(path)
        if got != want:
            bad.append("%s hash %s != pinned %s" % (path, got[:16], want[:16]))
    if bad:
        raise Stop("pinned input mismatch, which is a STRUCTURAL STOP and "
                   "never a substitution:\n   " + "\n   ".join(bad))
    say("  pinned inputs    %d / %d reproduce exactly" % (len(PINNED),
                                                          len(PINNED)))
    say("  AUTHORIZED")
    say()
    return grant


# =========================================================================== #
# PHASE 1 — PRE-RUN ACCOUNTING
# =========================================================================== #

def decision_dates():
    with open(PANEL, encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    allm = [dt.date.fromisoformat(r["month_end"][:10]) for r in rows]
    dec = [d for d in allm if DECISIONS_FROM <= d.isoformat() <= DECISIONS_TO]
    return allm, dec


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


def phase1(allm, dec, schedule, sched_rows):
    say("PHASE 1 — PRE-RUN ACCOUNTING")

    # ---- section 3: six-collision accounting -------------------------------
    pinned_collisions = sorted(load_json(FOMC_TIMING)["collisions"])
    by_ann = {dt.date.fromisoformat(r["official_announcement_date"]): r
              for r in sched_rows}
    classes, counts = {}, Counter()
    for d in pinned_collisions:
        day = dt.date.fromisoformat(d)
        row = by_ann.get(day)
        if row is None:
            cls = "C"            # collision, but no new target value announced
        elif row["announcement_time_status"] == "VERIFIED":
            cls = "A"
        else:
            cls = "B"
        classes[d] = cls
        counts[cls] += 1
    total = counts["A"] + counts["B"] + counts["C"]
    say("  six-collision accounting  A=%d  B=%d  C=%d  total=%d"
        % (counts["A"], counts["B"], counts["C"], total))
    for d in pinned_collisions:
        say("     %s  class %s" % (d, classes[d]))
    if total != 6:
        raise Stop("collision accounting does not sum to six: %d" % total)

    # ---- section 4: policy coverage THROUGH SAMPLE END ---------------------
    # The last policy CHANGE is not the end of policy coverage: the final
    # regime carries forward. Verify a defined target at EVERY required cutoff.
    idx = {d: i for i, d in enumerate(allm)}
    missing_now, missing_lag, lag_mismatch = [], [], []
    for d in dec:
        k = idx[d]
        if k < LAG_MONTHS:
            missing_lag.append(d.isoformat())
            continue
        lag_date = allm[k - LAG_MONTHS]
        if schedule.eligible(d) is UNDEFINED:
            missing_now.append(d.isoformat())
        if schedule.eligible(lag_date) is UNDEFINED:
            missing_lag.append(lag_date.isoformat())
        # the calendar-day reading of "t - 12 months", cross-checked
        alt = policy._shift_months(d, -LAG_MONTHS)
        if schedule.eligible(alt) != schedule.eligible(lag_date):
            lag_mismatch.append(d.isoformat())
    if missing_now or missing_lag:
        raise Stop("policy regime undefined at required cutoffs: now=%s lag=%s"
                   % (missing_now[:5], missing_lag[:5]))
    say("  policy coverage           defined at all %d decision cutoffs and "
        "all %d lagged cutoffs" % (len(dec), len(dec)))
    say("  last policy CHANGE        %s  (regime carries forward to %s)"
        % (sched_rows[-1]["effective_start_date"], DECISIONS_TO))
    if lag_mismatch:
        raise Stop("the canonical-month-end and calendar-day readings of "
                   "'t - 12 months' disagree on %d dates: %s"
                   % (len(lag_mismatch), lag_mismatch[:5]))
    say("  12-month lag reading      canonical month-end and calendar-day "
        "readings agree on all %d dates" % len(dec))

    # ---- section 5: the ONE canonical direction input ----------------------
    pin = {
        "path": PANEL,
        "sha256": sha256_file(PANEL),
        "rows": len(allm),
        "instrument_columns": 17,
        "date_coverage": "%s .. %s" % (allm[0], allm[-1]),
        "decision_window": "%s .. %s" % (dec[0], dec[-1]),
        "decision_months": len(dec),
        "direction_coding": (
            "sign(canonical TSMOM composite). The panel carries the canonical "
            "composite in {-1,-0.75,-0.5,-0.25,0,+0.25,+0.5,+0.75,+1} (the mean "
            "of the four sealed lookback votes). The canonical position is that "
            "composite scaled by a STRICTLY POSITIVE vol-target scalar, so the "
            "canonical position DIRECTION is sign(composite). An empty cell is "
            "UNDEFINED, never 0."),
        "returns_accessed": False,
    }
    say("  canonical direction input %s" % PANEL)
    say("     sha256 %s" % pin["sha256"])
    say("     %d rows x %d instruments, %s"
        % (pin["rows"], pin["instrument_columns"], pin["date_coverage"]))
    say("     coding: sign(composite); empty -> UNDEFINED, never 0")
    say()
    return {"collision_classes": classes, "collision_counts": dict(counts),
            "direction_pin": pin}


# =========================================================================== #
# PHASE 2 — HISTORICAL FEATURE (first time)
# =========================================================================== #

def build_series():
    out = {}
    for sid in ("INDPRO", "PAYEMS", "CPILFENS"):
        obs = load_json("data/mmv/%s.observations.realtime.json" % sid)
        # No authoritative release CLOCK time exists for these releases, so a
        # vintage dated ON the decision day is not admissible and the sealed
        # rule falls back to the prior eligible vintage. release_times is
        # therefore deliberately empty: the rule is applied, not bypassed.
        out[sid] = VintageSeries(sid, obs, release_times={})
    return out


def phase2(dec, allm, series, schedule):
    say("PHASE 2 — HISTORICAL MMV FEATURE  (first construction)")
    idx = {d: i for i, d in enumerate(allm)}

    leg_rows, same_day_vintages = {}, Counter()
    ref_lag = {sid: Counter() for sid in ("INDPRO", "PAYEMS", "CPILFENS")}

    for d in dec:
        snaps = {}
        for sid, vs in series.items():
            v = vs.eligible_vintage(d)
            if any(x == d for x in vs.vintage_dates):
                same_day_vintages[sid] += 1
            snaps[sid] = vs.as_of(d)
            if snaps[sid]:
                newest = max(snaps[sid])
                months = (d.year - newest.year) * 12 + (d.month - newest.month)
                ref_lag[sid][months] += 1

        g = legs.growth_leg(snaps["INDPRO"], snaps["PAYEMS"])
        i = legs.inflation_leg(snaps["CPILFENS"])
        lag_date = allm[idx[d] - LAG_MONTHS]
        now, then = schedule.eligible(d), schedule.eligible(lag_date)
        p = legs.policy_leg(now, then)
        leg_rows[d] = {"G": g, "I": i, "P": p}

    raw = {}
    undef_reason = Counter()
    for d in dec:
        L = leg_rows[d]
        for inst in sorted(votes.MAPPED):
            v = votes.raw_direction(inst, L["G"], L["I"], L["P"])
            raw[(d, inst)] = v
            if v is UNDEFINED:
                need = votes.required_legs(inst)
                why = [n for n in need if L[n] is UNDEFINED]
                undef_reason["+".join(why) + "_leg_unavailable"] += 1

    defined_legs = {k: sum(1 for d in dec if leg_rows[d][k] is not UNDEFINED)
                    for k in ("G", "I", "P")}
    say("  decision months           %d  (%s .. %s)" % (len(dec), dec[0], dec[-1]))
    say("  legs defined              G=%d  I=%d  P=%d  of %d"
        % (defined_legs["G"], defined_legs["I"], defined_legs["P"], len(dec)))
    for sid in ("INDPRO", "PAYEMS", "CPILFENS"):
        lags = sorted(ref_lag[sid].items())
        say("  %-9s newest-ref lag  %s months (count)"
            % (sid, ", ".join("%d:%d" % kv for kv in lags)))
    say("  same-day vintages         %s  (excluded by the sealed rule: no "
        "authoritative release clock time)" % dict(same_day_vintages))
    say("  raw cells                 %d = %d months x 15 mapped instruments"
        % (len(raw), len(dec)))
    say()
    return raw, leg_rows, defined_legs, dict(undef_reason), \
        {k: dict(v) for k, v in ref_lag.items()}, dict(same_day_vintages)


# =========================================================================== #
# PHASE 3 — STRUCTURAL SANITY GATE  (before any pooled agreement)
# =========================================================================== #

def canonical_signs(dec):
    with open(PANEL, encoding="utf-8") as fh:
        rows = {dt.date.fromisoformat(r["month_end"][:10]): r
                for r in csv.DictReader(fh)}
    out, undef = {}, 0
    for d in dec:
        r = rows[d]
        for inst in sorted(votes.MAPPED):
            cell = r[inst].strip()
            if cell == "":
                out[(d, inst)] = UNDEFINED
                undef += 1
            else:
                v = Fraction(cell)
                out[(d, inst)] = (v > 0) - (v < 0)
    return out, undef


def phase3(dec, raw, tsmom, leg_rows, undef_reason, tsmom_undef):
    say("PHASE 3 — STRUCTURAL SANITY GATE")
    problems = []

    months = sorted({d for d, _i in raw})
    if months != dec:
        problems.append("decision-date set differs from the sealed window")
    insts = {i for _d, i in raw}
    if insts != votes.MAPPED or len(insts) != 15:
        problems.append("mapped instrument set is not the sealed 15")
    if "VNQ" in insts or "RWX" in insts:
        problems.append("VNQ/RWX reached the position matrix")
    if len(raw) != len(dec) * 15:
        problems.append("duplicate or missing instrument-months")

    # every undefined MMV cell must be explained by a SEALED missing leg
    undef_cells = [k for k, v in raw.items() if v is UNDEFINED]
    explained = 0
    for (d, inst) in undef_cells:
        need = votes.required_legs(inst)
        if any(leg_rows[d][n] is UNDEFINED for n in need):
            explained += 1
    if explained != len(undef_cells):
        problems.append("%d undefined cells are NOT explained by a sealed "
                        "missing leg" % (len(undef_cells) - explained))

    # a zero must never stand in for a missing leg
    for (d, inst), v in raw.items():
        if v == 0:
            need = votes.required_legs(inst)
            if any(leg_rows[d][n] is UNDEFINED for n in need):
                problems.append("a missing leg was coded 0 at %s %s" % (d, inst))
                break

    bad_sign = [k for k, v in raw.items() if v not in (-1, 0, 1)
                and v is not UNDEFINED]
    if bad_sign:
        problems.append("non-ternary MMV direction at %s" % bad_sign[:3])

    zero_cells = sum(1 for v in raw.values() if v == 0)
    defined_cells = sum(1 for v in raw.values() if v is not UNDEFINED)

    say("  decision-date set         %d, matches the sealed window" % len(months))
    say("  mapped instruments        %d   VNQ present: NO   RWX present: NO"
        % len(insts))
    say("  instrument-months         %d, no duplicates" % len(raw))
    say("  MMV defined cells         %d" % defined_cells)
    say("  MMV undefined cells       %d, all explained by sealed missing legs"
        % len(undef_cells))
    for reason, n in sorted(undef_reason.items()):
        say("     %-34s %d" % (reason, n))
    say("  MMV zero (flat) cells     %d  (a real position state)" % zero_cells)
    say("  canonical undefined cells %d  (warm-up / no canonical signal)"
        % tsmom_undef)
    say("  no missing value coded 0  : confirmed")
    say("  no future vintage         : enforced by the eligible-vintage rule")
    say("  no final-revised data     : enforced by output_type=1 real-time bytes")
    say("  no unsealed series        : INDPRO PAYEMS CPILFENS + announced target")
    say("  no return field accessed  : this module opens no price or return file")

    if problems:
        say()
        for p in problems:
            say("  PROBLEM: %s" % p)
        raise Stop("GATE05_STATUS = HOLD_STRUCTURAL")
    say("  STRUCTURAL SANITY PASSED")
    say()
    return {"defined_cells": defined_cells, "undefined_cells": len(undef_cells),
            "zero_cells": zero_cells, "tsmom_undefined_cells": tsmom_undef}


# =========================================================================== #
# PHASE 4 — GATE 0.5
# =========================================================================== #

def phase4(raw, tsmom, ctx, grant, pre):
    say("PHASE 4 — GATE 0.5  (single primary statistic)")
    gate05.assert_no_unmapped(raw.keys())
    out = gate05.evaluate(raw, tsmom)

    pct = float(out.pooled_agreement) * 100.0
    say("  eligible cells            %d" % out.eligible_cells)
    say("  agreement cells           %d" % out.agreement_cells)
    say("  pooled exact agreement    %d / %d  =  %s  =  %.6f %%"
        % (out.agreement_cells, out.eligible_cells,
           out.pooled_agreement, pct))
    say("  sealed threshold          >= 80.0 %% INCLUSIVE")
    say("  excluded: unmapped %d | MMV undefined %d | canonical undefined %d"
        % (out.excluded_unmapped, out.excluded_mmv_undefined,
           out.excluded_tsmom_undefined))
    say()
    result = "KILL" if out.kill else "PASS"
    say("  GATE05_RESULT = %s" % result)
    say()

    record = {
        "schema": {"name": "mmv-gate05-result", "version": 1},
        "lineage": "CTA-EDGE-04-MMV",
        "run_id": RUN_ID,
        "run_type": RUN_TYPE,
        "authorization_id": grant["authorization_id"],
        "executed_utc": dt.datetime.now(dt.timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"),
        "rng_seed": None,
        "deterministic": True,
        "inputs": {p: sha256_file(p) for p in sorted(PINNED)},
        "canonical_direction_input": ctx["direction_pin"],
        "six_collision_accounting": {
            "classes": ctx["collision_classes"],
            "counts": ctx["collision_counts"]},
        "structural": pre,
        "gate05": {
            "eligible_cells": out.eligible_cells,
            "agreement_cells": out.agreement_cells,
            "pooled_agreement_exact": "%d/%d" % (out.pooled_agreement.numerator,
                                                 out.pooled_agreement.denominator),
            "pooled_agreement_percent": pct,
            "threshold": "agreement / eligible >= 4/5, inclusive",
            "kill": out.kill,
            "result": result,
            "excluded_unmapped": out.excluded_unmapped,
            "excluded_mmv_undefined": out.excluded_mmv_undefined,
            "excluded_tsmom_undefined": out.excluded_tsmom_undefined,
        },
        "firewall": {
            "RETURN_OUTCOME_ACCESSED": False,
            "PNL_COMPUTED": False,
            "SHARPE_COMPUTED": False,
            "BOOTSTRAP_RUN": False,
            "GATE1_RUN": False,
            "M1_RUN": False,
            "M2_RUN": False,
            "FIRST_RELEASE_DIAGNOSTIC_RUN": False,
            "PER_INSTRUMENT_AGREEMENT_COMPUTED": False,
            "PER_LEG_AGREEMENT_COMPUTED": False,
            "CALENDAR_PERIOD_AGREEMENT_COMPUTED": False,
        },
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(RESULT_JSON, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(record, fh, indent=1, sort_keys=True)
        fh.write("\n")
    say("  result artifact  %s" % RESULT_JSON)
    say("  sha256           %s" % sha256_file(RESULT_JSON))
    return out, record


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--execute", action="store_true",
                    help="perform the single authorized historical run")
    args = ap.parse_args()
    if not args.execute:
        say("refusing: this run is outcome-bearing and requires --execute")
        return 2
    if os.path.exists(RESULT_JSON):
        raise Stop("a result artifact already exists at %s; the grant is "
                   "CONSUMED and no rerun is authorized" % RESULT_JSON)

    grant = phase0()
    allm, dec = decision_dates()
    schedule, sched_rows = load_schedule()
    ctx = phase1(allm, dec, schedule, sched_rows)
    series = build_series()
    raw, leg_rows, defined_legs, undef_reason, ref_lag, same_day = phase2(
        dec, allm, series, schedule)
    tsmom, tsmom_undef = canonical_signs(dec)
    pre = phase3(dec, raw, tsmom, leg_rows, undef_reason, tsmom_undef)
    pre["legs_defined"] = defined_legs
    pre["undefined_reasons"] = undef_reason
    pre["newest_reference_lag_months"] = ref_lag
    pre["same_day_vintages_excluded"] = same_day
    phase4(raw, tsmom, ctx, grant, pre)
    say()
    say("=" * 78)
    say("RUN COMPLETE — the authorization is now CONSUMED")
    say("=" * 78)
    return 0


if __name__ == "__main__":
    sys.exit(main())
