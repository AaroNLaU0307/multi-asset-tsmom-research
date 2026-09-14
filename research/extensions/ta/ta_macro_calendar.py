"""CTA-EDGE-01-TA — official macro-release CALENDAR metadata fetch and normalisation.

S2 CALENDAR METADATA ONLY, under the S2 authorisation to obtain the calendars the
sealed `TA_PREREGISTRATION.md` §G.3 identification diagnostic requires.

    IT MUST NOT read any market price, index level, or economic data VALUE.
    IT MUST NOT compute any return, P&L or statistic.

Only three things are taken from each page: the DATE of a release, the name of the
release, and the URL it came from. No published number is read, stored or used.

Sealed covariate definitions (`TA_PREREGISTRATION.md` §G.3)
-----------------------------------------------------------
    CPI  = the date of the BLS Consumer Price Index news release
    NFP  = the date of the BLS Employment Situation news release
    FOMC = the date of the FOMC post-meeting statement
    QRA  = the Quarterly Refunding Announcement date — NOT fetched here; it is
           already derived from the pinned Treasury auction record by
           `ta_auction_fetch.qra_dates()`.

Authorities
-----------
    BLS  https://www.bls.gov/schedule/<year>/home.htm      (annual release schedule)
    FRB  https://www.federalreserve.gov/monetarypolicy/fomchistorical<year>.htm
         https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm

Usage (from the repository root)
--------------------------------
    python research/extensions/ta/ta_macro_calendar.py fetch
    python research/extensions/ta/ta_macro_calendar.py build
    python research/extensions/ta/ta_macro_calendar.py report
"""

from __future__ import annotations

import csv
import datetime as _dt
import hashlib
import html
import json
import os
import re
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# --------------------------------------------------------------------------- #
# Constants                                                                    #
# --------------------------------------------------------------------------- #

#: The primary cell spans 2006-02-09 .. 2026-05-13, so its return-bearing days lie
#: inside 2006 .. 2026. Those are exactly the years fetched.
FIRST_YEAR = 2006
LAST_YEAR = 2026

BLS_YEAR_URL = "https://www.bls.gov/schedule/{year}/home.htm"
#: 2006 and 2007 predate the HTML schedule table: those /schedule/<year>/home.htm pages
#: are navigation shells whose actual content is the official annual schedule PDF. The
#: PDF is the BLS authority for those two years and is parsed structurally.
BLS_PDF_URL = "https://www.bls.gov/bls/bls{year}sched.pdf"
BLS_PDF_YEARS = (2006, 2007)
FOMC_HIST_URL = "https://www.federalreserve.gov/monetarypolicy/fomchistorical{year}.htm"
FOMC_CAL_URL = "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm"

#: The Fed publishes per-year historical pages with a lag; recent years live on the
#: rolling calendars page. The split is read from what actually responds, not assumed:
#: `fetch()` tries the historical page for every year and falls back to the calendars
#: page, and records which source supplied each year.
RAW_DIR = os.path.join("data", "ta", "macro_raw")
RAW_INDEX = os.path.join("data", "ta", "ta_macro_raw_index.json")
CALENDAR_PATH = os.path.join("research", "extensions", "ta", "TA_MACRO_CALENDAR.csv")

_HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/140.0 Safari/537.36"),
    "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "close",
}

#: Exact BLS release-title prefixes. Deliberately strict: "Employment Situation of
#: Veterans" and "Consumer Price Index ... Annual" style releases are NOT the monthly
#: news release the covariate names, and the prefix match excludes them.
BLS_SERIES = {
    "CPI": "Consumer Price Index for ",
    "NFP": "Employment Situation for ",
}

CAL_COLUMNS = ["series", "date", "weekday", "source", "source_url", "detail"]


# --------------------------------------------------------------------------- #
# Helpers                                                                      #
# --------------------------------------------------------------------------- #


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(path: str) -> str:
    with open(path, "rb") as fh:
        return sha256_bytes(fh.read())


def _get(url: str) -> bytes:
    req = urllib.request.Request(url, headers=_HEADERS)
    with urllib.request.urlopen(req, timeout=90) as resp:
        return resp.read()


def _strip(fragment: str) -> str:
    """Tag-free, entity-decoded, whitespace-collapsed cell text.

    Collapsing runs of whitespace matters: BLS release titles wrap part of the name
    in a nested anchor, so stripping tags leaves ``Employment Situation  for December
    2009`` with a double space. Without the collapse the exact-prefix match silently
    finds nothing, which is a parse failure that looks like an empty calendar.
    """
    text = html.unescape(re.sub(r"<[^>]+>", " ", fragment)).replace("\xa0", " ")
    return re.sub(r"\s+", " ", text).strip()


# --------------------------------------------------------------------------- #
# 1. Fetch — raw pages only, each pinned by sha256                             #
# --------------------------------------------------------------------------- #


def fetch(raw_dir: str = RAW_DIR, index_path: str = RAW_INDEX) -> dict:
    os.makedirs(raw_dir, exist_ok=True)
    pages = []

    for year in range(FIRST_YEAR, LAST_YEAR + 1):
        url = BLS_YEAR_URL.format(year=year)
        body = _get(url)
        name = f"bls_schedule_{year}.html"
        with open(os.path.join(raw_dir, name), "wb") as fh:
            fh.write(body)
        pages.append({"kind": "BLS_YEAR", "year": year, "url": url, "file": name,
                      "bytes": len(body), "sha256": sha256_bytes(body)})

    for year in BLS_PDF_YEARS:
        url = BLS_PDF_URL.format(year=year)
        body = _get(url)
        name = f"bls_schedule_{year}.pdf"
        with open(os.path.join(raw_dir, name), "wb") as fh:
            fh.write(body)
        pages.append({"kind": "BLS_YEAR_PDF", "year": year, "url": url, "file": name,
                      "bytes": len(body), "sha256": sha256_bytes(body)})

    fomc_cal = _get(FOMC_CAL_URL)
    with open(os.path.join(raw_dir, "fomc_calendars.html"), "wb") as fh:
        fh.write(fomc_cal)
    pages.append({"kind": "FOMC_CALENDARS", "year": None, "url": FOMC_CAL_URL,
                  "file": "fomc_calendars.html", "bytes": len(fomc_cal),
                  "sha256": sha256_bytes(fomc_cal)})

    for year in range(FIRST_YEAR, LAST_YEAR + 1):
        url = FOMC_HIST_URL.format(year=year)
        try:
            body = _get(url)
        except Exception:
            continue                      # covered by the rolling calendars page
        name = f"fomc_historical_{year}.html"
        with open(os.path.join(raw_dir, name), "wb") as fh:
            fh.write(body)
        pages.append({"kind": "FOMC_HISTORICAL", "year": year, "url": url,
                      "file": name, "bytes": len(body), "sha256": sha256_bytes(body)})

    index = {
        "lineage": "CTA-EDGE-01-TA",
        "scope": "MACRO RELEASE CALENDAR METADATA ONLY - no price, no data value",
        "retrieved_at_utc": _dt.datetime.now(_dt.timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"),
        "first_year": FIRST_YEAR,
        "last_year": LAST_YEAR,
        "page_count": len(pages),
        "pages": sorted(pages, key=lambda p: (p["kind"], str(p["year"]))),
    }
    os.makedirs(os.path.dirname(index_path), exist_ok=True)
    with open(index_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(index, fh, indent=1, sort_keys=True)
        fh.write("\n")
    index["index_sha256"] = sha256_file(index_path)
    return index


def load_index(index_path: str = RAW_INDEX) -> dict:
    with open(index_path, "r", encoding="utf-8") as fh:
        return json.load(fh)


# --------------------------------------------------------------------------- #
# 2. Parse — deterministic, structural                                         #
# --------------------------------------------------------------------------- #

_MONTHS = {m: i for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July", "August",
     "September", "October", "November", "December"], start=1)}


def parse_bls_year(text: str, year: int) -> list[dict]:
    """Extract the monthly CPI and Employment Situation release dates for one year.

    The BLS annual schedule is a table of rows
    ``<td>Friday, January 08, 2010</td><td>08:30 AM</td><td>Employment Situation for
    December 2009</td>``. Only the DATE and the release TITLE are read.
    """
    out = []
    for row in re.findall(r"<tr[^>]*>(.*?)</tr>", text, re.S | re.I):
        cells = [_strip(c) for c in
                 re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row, re.S | re.I)]
        if len(cells) < 3:
            continue
        title = cells[-1]
        series = None
        for key, prefix in BLS_SERIES.items():
            if title.startswith(prefix):
                series = key
                break
        if series is None:
            continue
        m = re.search(r"(January|February|March|April|May|June|July|August|September|"
                      r"October|November|December)\s+(\d{1,2}),\s+(\d{4})", cells[0])
        if not m:
            continue
        d = _dt.date(int(m.group(3)), _MONTHS[m.group(1)], int(m.group(2)))
        if d.year != year:
            continue
        out.append({"series": series, "date": d, "detail": title})
    return out


#: `Consumer Price Index(es)?` tolerates a real BLS typo: the 2006 annual schedule
#: spells the February release "Consumer Price Indexes, January 2006". Without the
#: optional plural that release silently vanishes from the calendar.
_PDF_NAMES = {"CPI": r"Consumer Price Index(?:es)?", "NFP": r"The Employment Situation"}
_MONTH_RE = "Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec"
_PDF_ROW = re.compile(
    r"(?P<name>" + "|".join(_PDF_NAMES.values()) + r"),\s+"
    r"(?P<ref_month>" + _MONTH_RE + r")[a-z]*\.?\s+(?P<ref_year>\d{4})\s+"
    r"(?P<rel_month>" + _MONTH_RE + r")[a-z]*\.?\s+(?P<rel_day>\d{1,2})")
_ABBR = {m[:3]: i for m, i in _MONTHS.items()}


def parse_bls_year_pdf(pdf_bytes: bytes, year: int) -> list[dict]:
    """Extract CPI and Employment Situation release dates from a BLS annual schedule PDF.

    Rows read as ``<Release Name>, <reference month> <reference year>  <release month>
    <release day>[, <year>]  <time>``. The reference month/year of the DATA is skipped
    explicitly so it can never be mistaken for the RELEASE date, and the release year is
    the schedule year — a BLS annual schedule contains only its own calendar year.
    Only the date and the release name are read; no published figure exists in a
    schedule.
    """
    try:
        from pypdf import PdfReader
    except ImportError as exc:                                   # pragma: no cover
        raise RuntimeError(
            "parsing the 2006/2007 BLS schedule PDFs needs pypdf; the normalised "
            "TA_MACRO_CALENDAR.csv is committed, so this is only needed to rebuild "
            "the calendar from raw bytes") from exc
    import io as _io
    reader = PdfReader(_io.BytesIO(pdf_bytes))
    text = chr(10).join((pg.extract_text() or "") for pg in reader.pages)
    text = text.replace(chr(0x00a0), " ")
    out = []
    for m in _PDF_ROW.finditer(text):
        series = "CPI" if m.group("name").startswith("Consumer Price Index") else "NFP"
        ref_month = _ABBR[m.group("ref_month")[:3]]
        ref_year = int(m.group("ref_year"))
        rel_month = _ABBR[m.group("rel_month")[:3]]
        # The release always follows the reference period, so a January release of
        # December data belongs to the NEXT calendar year. Stamping every row with the
        # schedule year would misdate exactly the rows that spill across the year end -
        # which is how the 2006 schedule's January-2007 employment release first
        # appeared as 2006-01-05.
        rel_year = ref_year if rel_month > ref_month else ref_year + 1
        d = _dt.date(rel_year, rel_month, int(m.group("rel_day")))
        if not (FIRST_YEAR <= d.year <= LAST_YEAR):
            continue
        out.append({"series": series, "date": d,
                    "detail": f"{m.group('name')} (BLS {year} annual schedule)"})
    return out


def parse_fomc_historical(text: str, year: int) -> list[dict]:
    """Statement dates from a Fed per-year historical page.

    Each scheduled meeting panel carries an anchor whose visible text is exactly
    ``Statement`` pointing at ``.../<YYYYMMDD>a.htm``. Only that anchor is read, so
    minutes, implementation notes and projection materials are excluded.
    """
    out = []
    for m in re.finditer(r"<a[^>]*href=\"([^\"]*?(\d{8})a\.htm)\"[^>]*>(.*?)</a>",
                         text, re.S | re.I):
        if _strip(m.group(3)).lower() != "statement":
            continue
        stamp = m.group(2)
        d = _dt.date(int(stamp[:4]), int(stamp[4:6]), int(stamp[6:]))
        if d.year != year:
            continue
        out.append({"series": "FOMC", "date": d, "detail": "FOMC statement"})
    return out


def parse_fomc_calendars(text: str) -> list[dict]:
    """Statement dates from the Fed's rolling FOMC calendars page.

    On that page the statement is rendered as ``Statement: PDF | HTML``. Each
    ``Statement:`` label is located first and only the first
    ``monetary<YYYYMMDD>a.htm`` link inside the following span is taken, so minutes
    and implementation notes cannot be picked up.
    """
    out = []
    for m in re.finditer(r"Statement:", text):
        window = text[m.end():m.end() + 400]
        link = re.search(r"monetary(\d{8})a\.htm", window)
        if not link:
            continue
        stamp = link.group(1)
        d = _dt.date(int(stamp[:4]), int(stamp[4:6]), int(stamp[6:]))
        out.append({"series": "FOMC", "date": d, "detail": "FOMC statement"})
    return out


# --------------------------------------------------------------------------- #
# 3. Build the normalised calendar                                             #
# --------------------------------------------------------------------------- #


def build(raw_dir: str = RAW_DIR, index_path: str = RAW_INDEX,
          out_path: str = CALENDAR_PATH) -> dict:
    index = load_index(index_path)
    rows: list[dict] = []
    fomc_years_from_historical: set[int] = set()

    for page in index["pages"]:
        path = os.path.join(raw_dir, page["file"])
        with open(path, "rb") as fh:
            raw = fh.read()
        if sha256_bytes(raw) != page["sha256"]:
            raise AssertionError(f"raw page {page['file']} does not match its pin")
        text = raw.decode("utf-8", "replace")
        if page["kind"] == "BLS_YEAR":
            for rec in parse_bls_year(text, page["year"]):
                rows.append({**rec, "source": "BLS", "source_url": page["url"]})
        elif page["kind"] == "BLS_YEAR_PDF":
            for rec in parse_bls_year_pdf(raw, page["year"]):
                rows.append({**rec, "source": "BLS_PDF", "source_url": page["url"]})
        elif page["kind"] == "FOMC_HISTORICAL":
            found = parse_fomc_historical(text, page["year"])
            if found:
                fomc_years_from_historical.add(page["year"])
                for rec in found:
                    rows.append({**rec, "source": "FRB_HISTORICAL",
                                 "source_url": page["url"]})

    cal_page = next(p for p in index["pages"] if p["kind"] == "FOMC_CALENDARS")
    with open(os.path.join(raw_dir, cal_page["file"]), "rb") as fh:
        cal_text = fh.read().decode("utf-8", "replace")
    for rec in parse_fomc_calendars(cal_text):
        if rec["date"].year in fomc_years_from_historical:
            continue                      # the per-year historical page is authoritative
        if not (FIRST_YEAR <= rec["date"].year <= LAST_YEAR):
            continue
        rows.append({**rec, "source": "FRB_CALENDARS", "source_url": cal_page["url"]})

    # QRA - not fetched: derived from the PINNED Treasury auction record, and written
    # into the same committed calendar so the run-time artifact is self-contained and
    # never depends on the git-ignored raw extract.
    import ta_auction_fetch as _auc
    for d in sorted(_auc.qra_dates(_auc.load_raw())):
        if FIRST_YEAR <= d.year <= LAST_YEAR:
            rows.append({"series": "QRA", "date": d,
                         "detail": "Quarterly Refunding Announcement (derived from the "
                                   "pinned Treasury auction record)",
                         "source": "TREASURY_AUCTION_RECORD",
                         "source_url": _auc.API_BASE})

    seen = set()
    unique = []
    for r in sorted(rows, key=lambda r: (r["series"], r["date"], r["source"])):
        key = (r["series"], r["date"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(r)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="\n") as fh:
        wtr = csv.DictWriter(fh, fieldnames=CAL_COLUMNS, lineterminator="\n")
        wtr.writeheader()
        for r in unique:
            wtr.writerow({"series": r["series"], "date": r["date"].isoformat(),
                          "weekday": r["date"].strftime("%a"), "source": r["source"],
                          "source_url": r["source_url"], "detail": r["detail"]})
    return {"path": out_path, "rows": len(unique), "sha256": sha256_file(out_path)}


def load_calendar(path: str = CALENDAR_PATH) -> dict[str, set]:
    """{series -> set(date)} for the sealed covariate construction."""
    out: dict[str, set] = {}
    with open(path, "r", encoding="utf-8", newline="") as fh:
        for rec in csv.DictReader(fh):
            out.setdefault(rec["series"], set()).add(
                _dt.date.fromisoformat(rec["date"]))
    return out


def report() -> None:
    from collections import Counter
    cal = load_calendar()
    print(f"CALENDAR sha256 = {sha256_file(CALENDAR_PATH)}")
    for series in sorted(cal):
        d = sorted(cal[series])
        per_year = Counter(x.year for x in d)
        gaps = [y for y in range(FIRST_YEAR, LAST_YEAR + 1) if per_year.get(y, 0) == 0]
        print(f"  {series:<5} n={len(d):<4} {d[0]} .. {d[-1]}  "
              f"per-year min/max = {min(per_year.values())}/{max(per_year.values())}"
              + (f"  YEARS WITH NONE: {gaps}" if gaps else ""))
        print(f"        per year: " + " ".join(
            f"{y}:{per_year.get(y, 0)}" for y in range(FIRST_YEAR, LAST_YEAR + 1)))


def main(argv: list[str]) -> int:
    cmd = argv[1] if len(argv) > 1 else "report"
    if cmd == "fetch":
        idx = fetch()
        print(json.dumps({k: v for k, v in idx.items() if k != "pages"}, indent=2))
        print(f"pages fetched: {idx['page_count']}")
    elif cmd == "build":
        print(json.dumps(build(), indent=2))
    elif cmd == "report":
        report()
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
