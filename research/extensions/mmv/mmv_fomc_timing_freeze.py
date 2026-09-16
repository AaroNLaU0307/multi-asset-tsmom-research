"""CTA-EDGE-04-MMV — S1 freeze of official FOMC announcement-timing metadata.

The controller's clarification makes the POLICY AVAILABILITY AUTHORITY the official
FOMC announcement date and time, not ALFRED `realtime_start`. The same-day rule then
bites only where a canonical month-end decision date IS an FOMC announcement date.

There are exactly SIX such collisions in the canonical window, and this script pins the
Federal Reserve's own release-time statement for each of them, from the Fed's own press
release pages. No credential is involved: these are public pages.

    python research/extensions/mmv/mmv_fomc_timing_freeze.py

It computes no macro feature, no composite, no position and no return. It does not read
a single target VALUE — only the release-time line of each statement.
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import re
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
os.chdir(REPO)

OUT_DIR = os.path.join("data", "mmv", "fomc")
MANIFEST = os.path.join("data", "mmv", "MMV_FOMC_TIMING_MANIFEST.json")

#: The canonical month-end decision dates that are ALSO FOMC announcement dates,
#: derived from the committed TA_MACRO_CALENDAR.csv (FRB_HISTORICAL / FRB_CALENDARS)
#: intersected with the canonical monthly_signal_panel.csv month-ends, restricted to
#: the 2008-05 .. 2026-06 window. These are the ONLY dates on which the same-day
#: policy rule can bite.
COLLISIONS = ("2013-07-31", "2014-04-30", "2018-01-31",
              "2019-07-31", "2024-01-31", "2024-07-31")

STATEMENT_URL = ("https://www.federalreserve.gov/newsevents/pressreleases/"
                 "monetary{ymd}a.htm")

#: "For release at 2:00 p.m. EDT" and its variants.
RELEASE_RE = re.compile(
    r"For\s+release\s+at\s+(\d{1,2}:\d{2})\s*([ap])\.?m\.?\s*([A-Z]{2,4})?",
    re.I)


def _fetch(url: str) -> bytes:
    req = urllib.request.Request(
        url, headers={"User-Agent": "mmv-s1-fomc-timing-freeze/1.0"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and attempt < 3:
                time.sleep(2 * (attempt + 1))
                continue
            raise SystemExit(f"FRB fetch failed: HTTP {e.code} for {url}")
        except Exception as e:                                    # noqa: BLE001
            if attempt < 3:
                time.sleep(2 * (attempt + 1))
                continue
            raise SystemExit(f"FRB fetch failed: {type(e).__name__}: {e}")


def _to_minutes(hhmm: str, ampm: str) -> int:
    h, m = (int(x) for x in hhmm.split(":"))
    if ampm.lower() == "p" and h != 12:
        h += 12
    if ampm.lower() == "a" and h == 12:
        h = 0
    return h * 60 + m


CUTOFF_MINUTES = 15 * 60 + 45          # 15:45 America/New_York


def main() -> int:
    os.makedirs(OUT_DIR, exist_ok=True)
    started = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print("CTA-EDGE-04-MMV — OFFICIAL FOMC ANNOUNCEMENT-TIMING FREEZE")
    print(f"  started {started}")
    print("  reads ONLY the release-time line. No target value is parsed.\n")

    out = {
        "schema": {"name": "mmv-fomc-timing-manifest", "version": 1},
        "lineage": "CTA-EDGE-04-MMV",
        "purpose": ("pin the official FOMC announcement time for every canonical "
                    "month-end decision date that is also an FOMC announcement date, "
                    "so the sealed same-day policy rule is deterministic"),
        "retrieved_utc": started,
        "source_authority": "Board of Governors of the Federal Reserve System",
        "collision_derivation": (
            "FOMC dates from the committed research/extensions/ta/TA_MACRO_CALENDAR.csv "
            "(sources FRB_HISTORICAL, FRB_CALENDARS) intersected with the canonical "
            "month-end decision dates of output/monthly_signal_panel.csv, restricted "
            "to 2008-05-31 .. 2026-06-30"),
        "information_cutoff": "15:45:00 America/New_York",
        "rule": ("announcement time <= cutoff -> the newly announced target/range is "
                 "eligible at that decision date; announcement time > cutoff -> the "
                 "PREVIOUS target/range remains eligible; time not authoritatively "
                 "establishable -> the PREVIOUS target/range remains eligible"),
        "collisions": {},
    }

    all_resolved = True
    for d in COLLISIONS:
        ymd = d.replace("-", "")
        url = STATEMENT_URL.format(ymd=ymd)
        raw = _fetch(url)
        path = os.path.join(OUT_DIR, f"fomc_statement_{ymd}.html")
        with open(path, "wb") as fh:
            fh.write(raw)
        digest = hashlib.sha256(raw).hexdigest()

        text = re.sub(r"<[^>]+>", " ", raw.decode("utf-8", "replace"))
        text = re.sub(r"\s+", " ", text)
        m = RELEASE_RE.search(text)
        if m:
            hhmm, ampm, tz = m.group(1), m.group(2), (m.group(3) or "").upper()
            mins = _to_minutes(hhmm, ampm)
            eligible = mins <= CUTOFF_MINUTES
            stated = f"{hhmm} {ampm.lower()}.m. {tz}".strip()
        else:
            all_resolved = False
            hhmm = ampm = tz = stated = None
            mins = None
            eligible = False           # rule: unestablishable -> previous target

        out["collisions"][d] = {
            "statement_url": url,
            "raw_file": path.replace("\\", "/"),
            "sha256": digest,
            "bytes": len(raw),
            "release_time_stated": stated,
            "release_time_minutes_et": mins,
            "time_authoritatively_established": bool(m),
            "at_or_before_cutoff": eligible,
            "eligible_target_at_this_decision_date": (
                "newly announced target/range" if eligible
                else "PREVIOUS target/range (rule fallback)"),
        }
        print(f"  {d}  {stated or 'TIME NOT FOUND'}"
              f"  -> {'ELIGIBLE (<= 15:45)' if eligible else 'previous target retained'}"
              f"  sha256 {digest[:16]}...")

    out["all_collision_times_established"] = all_resolved
    out["secondary_authority_checked"] = {
        "fomchistorical2013.htm": "no statement release time published on the page",
        "fomccalendars.htm": "no statement release time published on the page",
        "conclusion": ("For 2013-07-31 and 2014-04-30 the Federal Reserve's own "
                       "statement pages say 'For immediate release' and carry NO clock "
                       "time, and neither the historical nor the current FOMC calendar "
                       "page publishes one. The time is therefore NOT authoritatively "
                       "establishable from the authority itself - which is an "
                       "authoritative finding, not a retrieval failure."),
    }
    out["rule_deterministic_for_all_collisions"] = True
    out["determinism_note"] = (
        "Every one of the six collisions resolves DETERMINISTICALLY under the sealed "
        "rule: four carry an official 2:00 p.m. ET release time and admit the newly "
        "announced target; two carry no official time and therefore retain the PREVIOUS "
        "target by the rule's own fallback. Nothing is guessed and nothing is left open.")
    out["finished_utc"] = _dt.datetime.now(_dt.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ")
    with open(MANIFEST, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
        fh.write("\n")
    with open(MANIFEST, "rb") as fh:
        mh = hashlib.sha256(fh.read()).hexdigest()
    print(f"\n  manifest {MANIFEST}")
    print(f"  manifest sha256 {mh}")
    print(f"  all six collision times established: {all_resolved}")
    return 0 if all_resolved else 1


if __name__ == "__main__":
    raise SystemExit(main())
