"""CTA-EDGE-04-MMV — S2 DATA-LAYER PARSER CHECK.

Contract-scoped by the S2 brief section 14:

    You MAY: verify frozen raw files load; verify schemas; verify hashes;
             verify timestamp parsing; verify one-record / synthetic-fixture
             plumbing.
    You MAY NOT: iterate over the 218 real decision dates to create historical
             macro legs; produce a historical G/I/P time series; produce
             historical raw ETF positions; inspect historical MMV-vs-TSMOM
             agreement.

The boundary between DATA PARSER VALIDATION and CANDIDATE FEATURE EXECUTION is
kept by construction, not by care: this script resolves NO cutoff date, calls
nothing from `engine.legs` or `engine.votes`, and touches exactly ONE
observation per series. It cannot build a leg because it never looks at a
second reference month.

    python research/extensions/mmv/mmv_s2_parser_check.py
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
os.chdir(REPO)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from engine.pit import UNDEFINED, VintageSeries, parse_value   # noqa: E402

RAW_MANIFEST = os.path.join("data", "mmv", "MMV_RAW_MANIFEST.json")
FOMC_MANIFEST = os.path.join("data", "mmv", "MMV_FOMC_TIMING_MANIFEST.json")

OBS_KEYS = {"date", "realtime_start", "realtime_end", "value"}

RESULTS = []


def chk(cid, ok, detail):
    RESULTS.append((cid, bool(ok), detail))


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main() -> int:
    print("=" * 78)
    print("CTA-EDGE-04-MMV — S2 DATA-LAYER PARSER CHECK")
    print("=" * 78)
    print("Loads and schema-checks the frozen bytes. Resolves NO cutoff date, "
          "builds NO leg.")
    print()

    with open(RAW_MANIFEST, encoding="utf-8") as fh:
        man = json.load(fh)

    for sid in sorted(man["series"]):
        entry = man["series"][sid]
        obs_meta = entry["files"]["observations_realtime"]
        vin_meta = entry["files"]["vintage_dates"]
        path = obs_meta["path"]

        # 1. hash
        digest = sha256_file(path)
        chk(sid + ".hash", digest == obs_meta["sha256"],
            "frozen bytes reproduce the pinned sha256")

        with open(path, encoding="utf-8") as fh:
            obs = json.load(fh)
        with open(vin_meta["path"], encoding="utf-8") as fh:
            vintages = json.load(fh)

        # 2. schema — checked on the WHOLE file (structure, never values)
        keys_ok = all(set(o) == OBS_KEYS for o in obs)
        chk(sid + ".schema", keys_ok and len(obs) == obs_meta["rows"],
            "%d rows, every row carries exactly %s"
            % (len(obs), sorted(OBS_KEYS)))

        # 3. timestamp parsing — every row's three dates must be ISO parseable
        bad = []
        for o in obs:
            try:
                dt.date.fromisoformat(o["date"])
                dt.date.fromisoformat(o["realtime_start"])
                dt.date.fromisoformat(o["realtime_end"])
            except ValueError:
                bad.append(o["date"])
                break
        chk(sid + ".timestamps", not bad,
            "all three date fields parse as ISO dates on every row")

        # 4. VintageSeries plumbing — construction only
        series = VintageSeries(sid, obs)
        chk(sid + ".plumbing",
            len(series.vintage_dates) == len(set(vintages)),
            "VintageSeries derives %d distinct vintage dates, matching the "
            "frozen vintage list" % len(series.vintage_dates))

        # 5. ONE record round-trips through the exact-value parser.
        #    One. Looking at a second reference month would begin a transform.
        first = obs[0]
        val = parse_value(first["value"])
        ok = val is UNDEFINED or isinstance(val, Fraction)
        chk(sid + ".one_record", ok,
            "the first observation parses to %s (exact, never float)"
            % ("UNDEFINED" if val is UNDEFINED else "Fraction"))

    # 6. FOMC timing manifest plumbs into pit.VintageSeries release_times
    with open(FOMC_MANIFEST, encoding="utf-8") as fh:
        fomc = json.load(fh)
    release_times = {}
    unestablished = []
    for d, c in fomc["collisions"].items():
        if c["time_authoritatively_established"]:
            mins = c["release_time_minutes_et"]
            release_times[dt.date.fromisoformat(d)] = dt.time(mins // 60,
                                                              mins % 60)
        else:
            unestablished.append(d)
    chk("fomc.parse", len(fomc["collisions"]) == 6 and len(release_times) == 4
        and len(unestablished) == 2,
        "6 collisions parse: 4 carry an official time, 2 carry none and are "
        "NOT given one here")
    chk("fomc.shape",
        all(isinstance(v, dt.time) for v in release_times.values()),
        "established times materialise as datetime.time, the shape "
        "pit.VintageSeries and policy.PolicySchedule consume")

    npass = sum(1 for _c, ok, _d in RESULTS if ok)
    n = len(RESULTS)
    for cid, ok, detail in RESULTS:
        print("  [%s] %-22s %s" % ("PASS" if ok else "FAIL", cid, detail))
    print()
    print("=" * 78)
    print("PARSER CHECK: %d/%d PASS" % (npass, n))
    if npass != n:
        print("VERDICT: FAIL")
        return 1
    print("VERDICT: PASS — the frozen data layer parses; no feature was built")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    sys.exit(main())
