"""CTA-EDGE-04-MMV — POLICY ANNOUNCEMENT SCHEDULE FREEZE.

Completes the one data-authority gap S2 deliberately left open: the mapping from
each administered target regime to the OFFICIAL announcement that made it
public. The sealed contract determines eligibility given a schedule; it does not
build the schedule, and no calendar rule can build it correctly.

    python research/extensions/mmv/mmv_policy_schedule_freeze.py

WHY NO HEURISTIC WORKS — established from the sources, not assumed:

  * The Federal Reserve's open-market table and the frozen FRED series both
    carry EFFECTIVE dates, not announcement dates. The Fed states this against
    itself in a footnote: "On July 10, 2024, this date was corrected from
    March 3, 2020, to March 4, 2020" — that intermeeting cut was ANNOUNCED on
    the 3rd and took effect on the 4th.
  * The effective-minus-announcement offset is NOT constant. It is 0 days
    through 2016 and 1 day from 2017-03-16 onward, so a fixed lag is wrong
    somewhere whichever lag is chosen.
  * The repository's committed FOMC calendar does not contain 2008-01-22 at
    all, so a "latest calendar event <= effective date" rule would attribute
    that intermeeting cut to the December 2007 meeting, six weeks early.

So each regime is matched to its announcement by DOCUMENT CONTENT: the accepted
announcement is the latest candidate date whose official Federal Reserve press
release actually states that exact target. Proximity is never the criterion.

FORBIDDEN AND ABSENT: ALFRED realtime_start, nearest scheduled meeting, fixed
publication lag, generic calendar heuristics, third-party timelines.

This script builds POLICY METADATA ONLY. It computes no 12-month change, no
sign, no P_t, and no MMV feature of any kind.
"""

from __future__ import annotations

import csv
import datetime as dt
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from fractions import Fraction
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
os.chdir(REPO)

RAW_DIR = os.path.join("data", "mmv", "policy")
OUT_CSV = os.path.join("research", "extensions", "mmv",
                       "MMV_POLICY_ANNOUNCEMENT_SCHEDULE.csv")
OUT_MANIFEST = os.path.join("data", "mmv", "MMV_POLICY_SCHEDULE_MANIFEST.json")
PANEL = os.path.join("output", "monthly_signal_panel.csv")
FOMC_TIMING_MANIFEST = os.path.join("data", "mmv",
                                    "MMV_FOMC_TIMING_MANIFEST.json")

#: Contract section D.3 splice.
SPLICE_LAST_SINGLE = dt.date(2008, 12, 15)

#: The sealed MMV decision window is 2008-05-31 .. 2026-06-30. The policy leg
#: reads target(t) AND target(t-12 months), so the schedule must cover targets
#: back to 2007-05-31: the regime in force on that date and every regime
#: beginning on or before the last decision date.
DECISIONS_FROM = dt.date(2008, 5, 31)
TARGETS_NEEDED_FROM = dt.date(2007, 5, 31)
TARGETS_NEEDED_TO = dt.date(2026, 6, 30)

#: Contract section C: 15:45:00 America/New_York.
CUTOFF_TIME = dt.time(15, 45)

#: How far back to look for the announcing press release. Generous enough for a
#: long weekend; the ACCEPTANCE test is document content, never distance.
CANDIDATE_LOOKBACK_DAYS = 7

STATEMENT_URLS = (
    "https://www.federalreserve.gov/newsevents/pressreleases/monetary{ymd}a.htm",
    "https://www.federalreserve.gov/newsevents/pressreleases/monetary{ymd}b.htm",
    "https://www.federalreserve.gov/boarddocs/press/monetary/{y}/{ymd}/",
    "https://www.federalreserve.gov/boarddocs/press/monetary/{y}/{ymd}/default.htm",
)

OPENMARKET_URL = "https://www.federalreserve.gov/monetarypolicy/openmarket.htm"
HISTORICAL_CAL = "https://www.federalreserve.gov/monetarypolicy/fomchistorical%d.htm"
CURRENT_CAL = "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm"
HISTORICAL_CAL_YEARS = range(2006, 2021)

RELEASE_TIME_RE = re.compile(
    r"For\s+release\s+at\s+(\d{1,2}):(\d{2})\s*([ap])\.?\s*m\.?\s*([A-Z]{2,4})?",
    re.I)
RELEASE_DATE_RE = re.compile(
    r"Release\s+Date:\s*([A-Z][a-z]+\s+\d{1,2},\s+\d{4})")
IMMEDIATE_RE = re.compile(r"For\s+immediate\s+release", re.I)

MONTH_NAMES = ["January", "February", "March", "April", "May", "June", "July",
               "August", "September", "October", "November", "December"]
MONTHS = {m: i for i, m in enumerate(MONTH_NAMES, start=1)}
MONTH_ALT = "|".join(MONTH_NAMES)

YEAR_BLOCK_RE = re.compile(r"(\d{4})\s+FOMC\s+Meetings")

#: A CROSS-MONTH meeting is written with a slash on BOTH page families, and the
#: month names may be full or abbreviated: "Jan/Feb 31-1", "Oct/Nov 31-1",
#: "Jul/Aug 31-1", "April/May 30-1". This form must be consumed BEFORE the
#: single-month pattern, because "April/May 30-1" otherwise yields a spurious
#: partial match on "May 30-1" — which in 2019 happened to land on the right
#: date and would have hidden the bug.
MONTH_ABBR = {m[:3]: i for i, m in enumerate(MONTH_NAMES, start=1)}
#: Full names first so the alternation prefers "September" over "Sep".
MONTH_TOKEN = "|".join(MONTH_NAMES + [m[:3] for m in MONTH_NAMES])

CAL_SLASH_RE = re.compile(
    r"\b(%s)\s*/\s*(%s)\s+(\d{1,2})\s*-\s*(\d{1,2})\b" % (MONTH_TOKEN,
                                                          MONTH_TOKEN))
CAL_SINGLE_RE = re.compile(
    r"\b(%s)\s+(\d{1,2})(?:\s*-\s*(\d{1,2}))?\b" % MONTH_TOKEN)

#: A scheduled meeting entry is followed by this word on its page family.
HISTORICAL_KEYWORD = "Meeting"
CURRENT_KEYWORD = "Statement"

#: The intermeeting federal-funds target actions in the required window, from
#: the Federal Reserve's own calendars. Named so that losing one is a HOLD
#: rather than a quietly shorter list: an intermeeting action misfiled as a
#: scheduled decision is exactly the availability error this freeze exists to
#: prevent.
EXPECTED_INTERMEETING = ("2008-01-22", "2008-10-08", "2020-03-03", "2020-03-15")

#: The FOMC holds eight regularly scheduled meetings most years. 2020 is a real
#: exception: the scheduled March 17-18 meeting was replaced by the UNSCHEDULED
#: March 15 meeting, so that year has seven scheduled meetings and the guard
#: must not reject it. The guard exists to catch PARSE LOSS, not to assert a
#: fact about Federal Reserve scheduling.
MIN_SCHEDULED_MEETINGS_PER_YEAR = 7


# --------------------------------------------------------------------------- #
# fetching, with an on-disk cache so the freeze is reproducible
# --------------------------------------------------------------------------- #

def fetch(url: str, allow_404: bool = False):
    os.makedirs(RAW_DIR, exist_ok=True)
    key = hashlib.sha256(url.encode()).hexdigest()[:24]
    path = os.path.join(RAW_DIR, "page_%s.html" % key)
    if os.path.exists(path):
        with open(path, "rb") as fh:
            return fh.read(), path
    req = urllib.request.Request(
        url, headers={"User-Agent": "mmv-policy-schedule-freeze/1.0"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                raw = r.read()
            with open(path, "wb") as fh:
                fh.write(raw)
            with open(path + ".url", "w", encoding="utf-8") as fh:
                fh.write(url + "\n")
            return raw, path
        except urllib.error.HTTPError as e:
            if e.code == 404 or allow_404:
                if e.code == 404:
                    return None, None
            if e.code in (429, 500, 502, 503, 504) and attempt < 3:
                time.sleep(2 * (attempt + 1))
                continue
            if allow_404:
                return None, None
            raise SystemExit("fetch failed HTTP %d for %s" % (e.code, url))
        except Exception:                                        # noqa: BLE001
            if attempt < 3:
                time.sleep(2 * (attempt + 1))
                continue
            if allow_404:
                return None, None
            raise
    return None, None


def plain(raw: bytes) -> str:
    txt = raw.decode("utf-8", "replace")
    txt = re.sub(r"(?is)<(script|style).*?</\1>", " ", txt)
    txt = re.sub(r"<[^>]+>", " ", txt)
    txt = txt.replace("&nbsp;", " ").replace("&amp;", "&")
    for dash in "‐‑‒–—−":
        txt = txt.replace(dash, "-")
    return re.sub(r"\s+", " ", txt)


# --------------------------------------------------------------------------- #
# the Federal Reserve's own notation
# --------------------------------------------------------------------------- #

FRACTION_WORDS = {Fraction(1, 4): "1/4", Fraction(1, 2): "1/2",
                  Fraction(3, 4): "3/4"}


def fed_notation(x: Fraction) -> str:
    """Render a target the way the Federal Reserve writes it: 5-1/4, 1/2, 2."""
    whole = int(x)
    frac = x - whole
    if frac == 0:
        return str(whole)
    word = FRACTION_WORDS.get(frac)
    if word is None:
        raise SystemExit("unexpected target fraction %s" % x)
    return word if whole == 0 else "%d-%s" % (whole, word)


def target_patterns(kind, value, lower, upper):
    """Regexes matching the Federal Reserve ANNOUNCING this target.

    Anchored on to/of/at so the sentence must be SETTING the new level rather
    than recalling the old one.
    """
    if kind == "SINGLE_TARGET":
        v = re.escape(fed_notation(value))
        return [re.compile(r"(?:to|of|at)\s+%s\s+percent" % v, re.I)]
    lo, hi = re.escape(fed_notation(lower)), re.escape(fed_notation(upper))
    return [re.compile(r"(?:to|of|at)\s+%s\s+to\s+%s\s+percent" % (lo, hi),
                       re.I)]


# --------------------------------------------------------------------------- #
# regimes from the frozen series
# --------------------------------------------------------------------------- #

def frozen_values(sid: str) -> dict:
    with open("data/mmv/%s.observations.realtime.json" % sid,
              encoding="utf-8") as fh:
        obs = json.load(fh)
    out = {}
    for o in obs:
        if o["value"] == ".":
            continue
        out.setdefault(o["date"], set()).add(o["value"])
    revised = {d: v for d, v in out.items() if len(v) > 1}
    if revised:
        raise SystemExit(
            "%s carries revised values, contradicting the sealed premise that "
            "administered rates are never revised: %s" % (sid, sorted(revised)[:5]))
    return {dt.date.fromisoformat(d): Fraction(next(iter(v)))
            for d, v in out.items()}


def regimes():
    tar, lo, hi = (frozen_values("DFEDTAR"), frozen_values("DFEDTARL"),
                   frozen_values("DFEDTARU"))
    if max(tar) != SPLICE_LAST_SINGLE:
        raise SystemExit("DFEDTAR does not end at the sealed splice date")
    first_range = SPLICE_LAST_SINGLE + dt.timedelta(days=1)
    if min(lo) != first_range or min(hi) != first_range:
        raise SystemExit("range series does not begin at the sealed splice date")

    out, prev = [], None
    for d in sorted(tar):
        if tar[d] != prev:
            out.append({"effective_start_date": d,
                        "target_type": "SINGLE_TARGET",
                        "target_value": tar[d], "target_lower": None,
                        "target_upper": None, "target_midpoint": tar[d]})
            prev = tar[d]
    prev = None
    for d in sorted(set(lo) & set(hi)):
        r = (lo[d], hi[d])
        if r != prev:
            out.append({"effective_start_date": d,
                        "target_type": "TARGET_RANGE",
                        "target_value": None, "target_lower": lo[d],
                        "target_upper": hi[d],
                        "target_midpoint": (lo[d] + hi[d]) / 2})
            prev = r
    out.sort(key=lambda r: r["effective_start_date"])
    return out


def required(all_regimes):
    starts = [r["effective_start_date"] for r in all_regimes]
    in_force = max(d for d in starts if d <= TARGETS_NEEDED_FROM)
    return [r for r in all_regimes
            if in_force <= r["effective_start_date"] <= TARGETS_NEEDED_TO]


def normalised(regime):
    if regime["target_type"] == "SINGLE_TARGET":
        return ("SINGLE", regime["target_value"])
    return ("RANGE", regime["target_lower"], regime["target_upper"])


# --------------------------------------------------------------------------- #
# the Fed's own open-market table — an INDEPENDENT confirmation of the regimes
# --------------------------------------------------------------------------- #

class _Tables(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tables, self.cur, self.row, self.cell = [], None, None, None

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self.cur = []
        elif tag == "tr" and self.cur is not None:
            self.row = []
        elif tag in ("td", "th") and self.row is not None:
            self.cell = []

    def handle_endtag(self, tag):
        if tag == "table" and self.cur is not None:
            self.tables.append(self.cur)
            self.cur = None
        elif tag == "tr" and self.row is not None:
            if self.row:
                self.cur.append(self.row)
            self.row = None
        elif tag in ("td", "th") and self.cell is not None:
            self.row.append(re.sub(r"\s+", " ", "".join(self.cell)).strip())
            self.cell = None

    def handle_data(self, data):
        if self.cell is not None:
            self.cell.append(data)


def parse_fed_level(s: str):
    s = s.strip()
    if "-" in s:
        lo, hi = s.split("-", 1)
        return ("RANGE", Fraction(lo.strip()), Fraction(hi.strip()))
    return ("SINGLE", Fraction(s))


def openmarket_table():
    raw, path = fetch(OPENMARKET_URL)
    text = raw.decode("utf-8", "replace")
    years = [int(y) for y in re.findall(r"<h4[^>]*>\s*(\d{4})\s*</h4>", text)]
    if not years:
        years = [int(y) for y in re.findall(r'id="year(\d{4})"', text)]
    p = _Tables()
    p.feed(text)
    tables = [t for t in p.tables
              if t and t[0][:1] == ["Date"] and "Level (%)" in t[0]]
    out = {}
    for year, table in zip(years, tables):
        for row in table[1:]:
            if len(row) < 4:
                continue
            m = re.match(r"([A-Z][a-z]+)\s+(\d{1,2})", row[0])
            if not m:
                continue
            out[dt.date(year, MONTHS[m.group(1)], int(m.group(2)))] = row[3]
    return out, path, hashlib.sha256(raw).hexdigest()


# --------------------------------------------------------------------------- #
# scheduled FOMC meetings — the authority for the INTERMEETING flag
# --------------------------------------------------------------------------- #

def _month_num(token: str) -> int:
    token = token.strip()
    return MONTHS.get(token) or MONTH_ABBR[token[:3]]


def _calendar_entries(text, year, keyword):
    """(end_date, unscheduled) for every meeting entry in ``text``.

    Slash forms are matched first and their spans blanked, so the single-month
    pattern cannot produce a partial match inside one.
    """
    out = []
    chars = list(text)

    def _annotation(end):
        """The Federal Reserve's own label for the entry ending at ``end``.

        Returns None when this is not a meeting entry at all, otherwise the
        parenthesised annotation the Fed writes between the date and the
        keyword: "" for an ordinary scheduled meeting, "unscheduled", or
        "cancelled" (2020's March 17-18 meeting, which never happened).

        The keyword must follow IMMEDIATELY, allowing only that annotation.
        Searching a loose 60-character window instead lets prose match:
        "minutes of January 29/30 meeting" injected a spurious 2008-01-29 into
        the scheduled set, and a spurious scheduled date can only ever HIDE an
        intermeeting action.
        """
        w = text[end:end + 90].lstrip(" *–-")
        annot = ""
        if w.startswith("("):
            close = w.find(")")
            if close == -1 or close > 32:
                return None
            annot = w[1:close].strip().lower()
            w = w[close + 1:].lstrip()
        # CASE-SENSITIVE: the Fed's headings capitalise "Meeting" and
        # "Statement"; lowercase "meeting" appears only in prose such as
        # "See end of minutes of March 15 meeting", which is a cross-reference,
        # not a calendar entry. Matching it would file an UNSCHEDULED meeting
        # as a scheduled one and silently drop an intermeeting action.
        if w.startswith("Conference Call"):
            return None
        if not w.startswith(keyword):
            return None
        return annot

    for m in CAL_SLASH_RE.finditer(text):
        m1, m2, _d1, d2 = m.groups()
        annot = _annotation(m.end())
        if annot is None or "cancel" in annot:
            continue
        end_month = _month_num(m2)
        end_year = year + 1 if end_month < _month_num(m1) else year
        try:
            d = dt.date(end_year, end_month, int(d2))
        except ValueError:
            continue
        out.append((d, "unscheduled" in annot))
        for i in range(m.start(), m.end()):
            chars[i] = " "

    masked = "".join(chars)
    for m in CAL_SINGLE_RE.finditer(masked):
        mon, d1, d2 = m.groups()
        annot = _annotation(m.end())
        if annot is None or "cancel" in annot:
            continue
        try:
            d = dt.date(year, _month_num(mon), int(d2 or d1))
        except ValueError:
            continue
        out.append((d, "unscheduled" in annot))
    return out


def scheduled_meeting_end_dates():
    """Last day of every SCHEDULED FOMC meeting, from the Fed's own calendars.

    A "Conference Call" is not a scheduled meeting. A meeting the Fed itself
    labels "(unscheduled)" is not a scheduled meeting either — the March 2020
    entry is exactly that case, and taking the label at face value is what
    keeps 2020-03-15 correctly classified as an intermeeting action.

    Returns (scheduled_ends, unscheduled_ends, sources). The unscheduled set is
    kept because it CORROBORATES every intermeeting classification instead of
    leaving it to rest on an absence.
    """
    sched, unsched, sources = {}, {}, []
    for year in HISTORICAL_CAL_YEARS:
        url = HISTORICAL_CAL % year
        raw, path = fetch(url, allow_404=True)
        if raw is None:
            continue
        sources.append({"url": url, "sha256": hashlib.sha256(raw).hexdigest()})
        text = plain(raw)
        for d, unsch in _calendar_entries(text, year, HISTORICAL_KEYWORD):
            (unsched if unsch else sched).setdefault(d, url)
        # conference calls are recorded separately as corroboration
        for m in re.finditer(r"\b(%s)\s+(\d{1,2})\s+Conference\s+Call"
                             % MONTH_TOKEN, text):
            try:
                unsched.setdefault(
                    dt.date(year, _month_num(m.group(1)), int(m.group(2))), url)
            except ValueError:
                pass

    raw, path = fetch(CURRENT_CAL)
    sources.append({"url": CURRENT_CAL,
                    "sha256": hashlib.sha256(raw).hexdigest()})
    text = plain(raw)
    blocks = list(YEAR_BLOCK_RE.finditer(text))
    for i, b in enumerate(blocks):
        year = int(b.group(1))
        stop = blocks[i + 1].start() if i + 1 < len(blocks) else len(text)
        chunk = text[b.end():stop]
        for d, unsch in _calendar_entries(chunk, year, CURRENT_KEYWORD):
            (unsched if unsch else sched).setdefault(d, CURRENT_CAL)
    return sched, unsched, sources


def check_calendar_completeness(ends, first_year, last_year):
    """Catch PARSE LOSS in the calendar scrape.

    Without this, a calendar-format change that drops entries would not fail —
    it would quietly reclassify scheduled decisions as intermeeting actions and
    still exit 0. That is the failure mode most likely to survive review, so it
    gets an explicit guard.
    """
    thin = []
    for y in range(first_year, last_year + 1):
        n = sum(1 for d in ends if d.year == y)
        if n < MIN_SCHEDULED_MEETINGS_PER_YEAR:
            thin.append("%d has only %d scheduled meeting ends" % (y, n))
    return thin


# --------------------------------------------------------------------------- #
# announcement discovery, by DOCUMENT CONTENT
# --------------------------------------------------------------------------- #

def find_announcement(regime):
    """The official press release that announced this regime.

    Candidates run backwards from the effective date, and a candidate is
    ACCEPTED only if its press release states this exact target. The latest
    accepted candidate wins. Distance is never the criterion; if no release
    states the target, nothing is returned and the freeze HOLDs.
    """
    pats = target_patterns(regime["target_type"], regime["target_value"],
                           regime["target_lower"], regime["target_upper"])
    eff = regime["effective_start_date"]
    for back in range(0, CANDIDATE_LOOKBACK_DAYS + 1):
        cand = eff - dt.timedelta(days=back)
        ymd = cand.strftime("%Y%m%d")
        for tmpl in STATEMENT_URLS:
            url = tmpl.format(ymd=ymd, y=cand.year)
            raw, path = fetch(url, allow_404=True)
            if raw is None:
                continue
            text = plain(raw)
            if not any(p.search(text) for p in pats):
                continue
            return {"announcement_date": cand, "url": url,
                    "raw_file": path.replace("\\", "/"),
                    "sha256": hashlib.sha256(raw).hexdigest(),
                    "bytes": len(raw), "text": text,
                    "candidates_examined": back + 1}
    return None


def release_time(text: str):
    m = RELEASE_TIME_RE.search(text)
    if m:
        hh, mm = int(m.group(1)), int(m.group(2))
        ap = m.group(3).lower()
        if ap == "p" and hh != 12:
            hh += 12
        if ap == "a" and hh == 12:
            hh = 0
        return dt.time(hh, mm), (m.group(4) or "").upper(), "VERIFIED"
    return None, "", "NOT_ESTABLISHED"


def stated_release_date(text: str):
    m = RELEASE_DATE_RE.search(text)
    if not m:
        return None
    mon, day, year = re.match(r"([A-Z][a-z]+)\s+(\d{1,2}),\s+(\d{4})",
                              m.group(1)).groups()
    return dt.date(int(year), MONTHS[mon], int(day))


def month_ends():
    with open(PANEL, encoding="utf-8") as fh:
        return {dt.date.fromisoformat(r["month_end"][:10])
                for r in csv.DictReader(fh)}


# --------------------------------------------------------------------------- #

def main() -> int:
    started = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print("=" * 78)
    print("CTA-EDGE-04-MMV — POLICY ANNOUNCEMENT SCHEDULE FREEZE")
    print("=" * 78)
    print("POLICY METADATA ONLY. No 12-month change, no sign, no P_t.")
    print()

    every = regimes()
    needed = required(every)
    print("  regimes in the frozen series   : %d" % len(every))
    print("  required for the sealed window : %d  (%s .. %s)"
          % (len(needed), needed[0]["effective_start_date"],
             needed[-1]["effective_start_date"]))

    om, om_path, om_hash = openmarket_table()
    sched, unsched, cal_sources = scheduled_meeting_end_dates()
    print("  Federal Reserve open-market rows: %d" % len(om))
    print("  scheduled FOMC meeting ends     : %d  (from %d official calendar "
          "pages)" % (len(sched), len(cal_sources)))
    print("  unscheduled meetings / calls    : %d" % len(unsched))

    rows, problems = [], []
    thin = check_calendar_completeness(
        sched, needed[0]["effective_start_date"].year + 1,
        needed[-1]["effective_start_date"].year - 1)
    if thin:
        problems.extend("calendar parse incomplete: " + t for t in thin)
    print("  calendar completeness           : %s"
          % ("every full year shows >= %d scheduled meetings"
             % MIN_SCHEDULED_MEETINGS_PER_YEAR
             if not thin else "INCOMPLETE"))
    print()
    for r in needed:
        eff = r["effective_start_date"]
        found = find_announcement(r)
        if found is None:
            problems.append("no official press release states the target for "
                            "the regime effective %s" % eff)
            continue
        t, tz, status = release_time(found["text"])
        stated = stated_release_date(found["text"])
        if stated is not None and stated != found["announcement_date"]:
            problems.append("page release date %s disagrees with URL date %s"
                            % (stated, found["announcement_date"]))

        ann = found["announcement_date"]
        intermeeting = ann not in sched
        # Corroborate POSITIVELY. An intermeeting classification must rest on
        # the Federal Reserve labelling a Conference Call or an unscheduled
        # meeting, not merely on the date being absent from a scrape that
        # could have dropped it.
        corroborated = ""
        if intermeeting:
            for back in range(0, 3):
                probe = ann - dt.timedelta(days=back)
                if probe in unsched:
                    corroborated = probe.isoformat()
                    break
            if not corroborated:
                problems.append(
                    "%s is classified INTERMEETING but no Conference Call or "
                    "unscheduled meeting is recorded on the Federal Reserve "
                    "calendar within two days of it" % ann)

        # The Fed's table is dated by EFFECTIVE date, which for two regimes is
        # one day later than FRED's stamp. Record the delta rather than assume.
        om_hit = None
        for probe in (eff, eff + dt.timedelta(days=1)):
            if probe in om and parse_fed_level(om[probe]) == normalised(r):
                om_hit = probe
                break

        rows.append({
            "effective_start_date": eff.isoformat(),
            "target_type": r["target_type"],
            "target_value": ("" if r["target_value"] is None
                             else "%g" % float(r["target_value"])),
            "target_lower": ("" if r["target_lower"] is None
                             else "%g" % float(r["target_lower"])),
            "target_upper": ("" if r["target_upper"] is None
                             else "%g" % float(r["target_upper"])),
            "target_midpoint": "%g" % float(r["target_midpoint"]),
            "official_announcement_date": ann.isoformat(),
            "official_announcement_time_et": t.strftime("%H:%M:%S") if t else "",
            "announcement_timezone": tz,
            "announcement_time_status": status,
            "announcement_minus_effective_days": (ann - eff).days,
            "is_intermeeting": "YES" if intermeeting else "NO",
            "intermeeting_corroborating_calendar_entry": corroborated,
            "stated_release_date": stated.isoformat() if stated else "",
            "official_source": found["url"],
            "source_sha256": found["sha256"],
            "source_bytes": found["bytes"],
            "raw_file": found["raw_file"],
            "candidates_examined": found["candidates_examined"],
            "frb_openmarket_date": om_hit.isoformat() if om_hit else "",
            "frb_openmarket_level": om.get(om_hit, "") if om_hit else "",
            "frb_confirms_level": "YES" if om_hit else "NO",
            "frb_minus_fred_effective_days": ((om_hit - eff).days
                                              if om_hit else ""),
            "notes": ("INTERMEETING: announcement is not the conclusion of a "
                      "scheduled FOMC meeting per the Federal Reserve's own "
                      "calendar" if intermeeting else ""),
        })
        print("  %s  ann %s  %s  off %+d  %s%s%s"
              % (eff, ann, (t.strftime("%H:%M") + " " + tz) if t else "  --:--   ",
                 (ann - eff).days,
                 "FRB ok" if om_hit else "FRB MISMATCH",
                 "  INTERMEETING" if intermeeting else "",
                 "  TIME NOT ESTABLISHED" if status != "VERIFIED" else ""))

    got_inter = tuple(r["official_announcement_date"] for r in rows
                      if r["is_intermeeting"] == "YES")
    if got_inter != EXPECTED_INTERMEETING:
        problems.append(
            "intermeeting set is %s but the Federal Reserve's calendars record "
            "%s; a missing entry means the calendar parse filed an "
            "intermeeting action as a scheduled decision"
            % (list(got_inter), list(EXPECTED_INTERMEETING)))

    # ---- independent, DATE-FREE confirmation: the ordered level sequence ----
    lo_d = min(r["effective_start_date"] for r in needed)
    hi_d = max(r["effective_start_date"] for r in needed) + dt.timedelta(days=2)
    fed_seq = [parse_fed_level(om[d]) for d in sorted(om) if lo_d <= d <= hi_d]
    our_seq = [normalised(r) for r in needed]
    seq_match = fed_seq == our_seq
    if not seq_match:
        problems.append("the Federal Reserve's ordered level sequence (%d) "
                        "does not match the frozen regimes (%d)"
                        % (len(fed_seq), len(our_seq)))

    if problems:
        print("\n  PROBLEMS:")
        for p in problems:
            print("   - %s" % p)
        print("\nPOLICY_SCHEDULE_STATUS = HOLD")
        return 2

    # ---- section 6: reconcile every cutoff the sealed rule can bite on ------
    me = month_ends()
    needed_cutoffs = {d for d in me if TARGETS_NEEDED_FROM <= d <= TARGETS_NEEDED_TO}
    decisions = {d for d in me if DECISIONS_FROM <= d <= TARGETS_NEEDED_TO}
    by_ann = {dt.date.fromisoformat(r["official_announcement_date"]): r
              for r in rows}
    collisions = []
    for d in sorted(set(by_ann) & needed_cutoffs):
        r = by_ann[d]
        verified = r["announcement_time_status"] == "VERIFIED"
        eligible = bool(verified and dt.time.fromisoformat(
            r["official_announcement_time_et"]) <= CUTOFF_TIME)
        collisions.append({
            "cutoff_date": d.isoformat(),
            "cutoff_role": "DECISION" if d in decisions else "LAGGED_ONLY",
            "announcement_time_status": r["announcement_time_status"],
            "official_announcement_time_et": r["official_announcement_time_et"],
            "eligible_target_at_this_cutoff": (
                "newly announced target/range" if eligible
                else "PREVIOUS target/range (rule fallback)"),
        })

    with open(FOMC_TIMING_MANIFEST, encoding="utf-8") as fh:
        pinned = json.load(fh)
    pinned_dates = sorted(pinned["collisions"])
    pinned_with_change = [d for d in pinned_dates
                          if dt.date.fromisoformat(d) in by_ann]

    fields = list(rows[0].keys())
    with open(OUT_CSV, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    with open(OUT_CSV, "rb") as fh:
        csv_hash = hashlib.sha256(fh.read()).hexdigest()

    verified_n = sum(1 for r in rows
                     if r["announcement_time_status"] == "VERIFIED")
    inter = [r["official_announcement_date"] for r in rows
             if r["is_intermeeting"] == "YES"]
    offsets = sorted({r["announcement_minus_effective_days"] for r in rows})
    frb_delta = sorted({r["frb_minus_fred_effective_days"] for r in rows})

    manifest = {
        "schema": {"name": "mmv-policy-announcement-schedule", "version": 1},
        "lineage": "CTA-EDGE-04-MMV",
        "purpose": ("official announcement authority for the administered "
                    "policy target; completes the S2 construction gap without "
                    "changing any sealed definition"),
        "retrieved_utc": started,
        "finished_utc": dt.datetime.now(dt.timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"),
        "source_authority": "Board of Governors of the Federal Reserve System",
        "schedule_csv": OUT_CSV.replace("\\", "/"),
        "schedule_csv_sha256": csv_hash,
        "regime_count": len(rows),
        "regimes_in_frozen_series": len(every),
        "window_targets_needed_from": TARGETS_NEEDED_FROM.isoformat(),
        "window_targets_needed_to": TARGETS_NEEDED_TO.isoformat(),
        "first_effective_start": rows[0]["effective_start_date"],
        "last_effective_start": rows[-1]["effective_start_date"],
        "announcement_time_verified": verified_n,
        "announcement_time_not_established": len(rows) - verified_n,
        "announcement_minus_effective_offsets_observed": offsets,
        "intermeeting_count": len(inter),
        "intermeeting_announcement_dates": inter,
        "intermeeting_corroborated": {
            r["official_announcement_date"]:
                r["intermeeting_corroborating_calendar_entry"]
            for r in rows if r["is_intermeeting"] == "YES"},
        "unscheduled_or_conference_call_dates_known": len(unsched),
        "scheduled_meeting_end_dates_known": len(sched),
        "calendar_sources": cal_sources,
        "frb_openmarket_url": OPENMARKET_URL,
        "frb_openmarket_sha256": om_hash,
        "frb_openmarket_raw_file": om_path.replace("\\", "/"),
        "frb_ordered_level_sequence_matches": seq_match,
        "frb_minus_fred_effective_day_deltas_observed": frb_delta,
        "frb_effective_date_differs_from_fred": [
            r["effective_start_date"] for r in rows
            if r["frb_minus_fred_effective_days"] not in ("", 0)],
        "cutoff_collisions": collisions,
        "pinned_fomc_timing_collisions": pinned_dates,
        "pinned_collisions_that_are_target_changes": pinned_with_change,
        "alfred_realtime_start_used": False,
        "nearest_meeting_heuristic_used": False,
        "fixed_publication_lag_used": False,
        "acceptance_criterion": (
            "the latest candidate date whose OFFICIAL Federal Reserve press "
            "release states this exact target; proximity is never the "
            "criterion"),
    }
    with open(OUT_MANIFEST, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(manifest, fh, indent=1, sort_keys=True)
        fh.write("\n")
    with open(OUT_MANIFEST, "rb") as fh:
        man_hash = hashlib.sha256(fh.read()).hexdigest()

    print()
    print("  regimes frozen                : %d" % len(rows))
    print("  announcement time VERIFIED    : %d" % verified_n)
    print("  announcement time NOT_EST.    : %d" % (len(rows) - verified_n))
    print("  offsets observed (ann - eff)  : %s" % offsets)
    print("  intermeeting actions          : %d  %s" % (len(inter), inter))
    print("  FRB ordered level sequence    : %s"
          % ("MATCHES exactly" if seq_match else "MISMATCH"))
    print("  FRB vs FRED effective deltas  : %s days" % frb_delta)
    print()
    print("  cutoff collisions (the sealed same-day rule bites here): %d"
          % len(collisions))
    for c in collisions:
        print("    %s  %-11s  %s  -> %s"
              % (c["cutoff_date"], c["cutoff_role"],
                 c["announcement_time_status"],
                 c["eligible_target_at_this_cutoff"]))
    print()
    print("  %s" % OUT_CSV)
    print("  csv sha256      %s" % csv_hash)
    print("  manifest sha256 %s" % man_hash)
    print()
    print("POLICY_SCHEDULE_STATUS = PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
