"""CTA-EDGE-01-TA — official Treasury auction METADATA fetch and event-calendar build.

S1 DESIGN METADATA ONLY. This module is bound by the lineage's sealed S1 contract
(`TA_PREREGISTRATION.md`):

    IT MUST NOT open ETF prices for returns.
    IT MUST NOT calculate event returns.
    IT MUST NOT compute P&L.
    IT MUST NOT compute any candidate statistic.

The single point of contact with the ETF panel is `trading_calendar()`, which reads
the panel's `Date` column and a **non-null boolean presence mask** for the named
columns, and never retains the numeric value. A presence mask is data availability,
not a price and not a return. Nothing else in this file touches the panel.

Source of authority
-------------------
U.S. Treasury Fiscal Data, dataset "Treasury Securities Auctions Data":
    https://fiscaldata.treasury.gov/datasets/treasury-securities-auctions-data/
    https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/od/auctions_query

Usage (from the repository root)
--------------------------------
    python research/extensions/ta/ta_auction_fetch.py fetch    # write the raw extract
    python research/extensions/ta/ta_auction_fetch.py build    # write the event calendar
    python research/extensions/ta/ta_auction_fetch.py report   # print the S1 count block
"""

from __future__ import annotations

import csv
import datetime as _dt
import hashlib
import json
import os
import sys
import urllib.parse
import urllib.request
from collections import Counter, defaultdict

# --------------------------------------------------------------------------- #
# Sealed constants — every one of these is fixed by TA_PREREGISTRATION.md      #
# --------------------------------------------------------------------------- #

API_BASE = (
    "https://api.fiscaldata.treasury.gov/services/api/fiscal_service"
    "/v1/accounting/od/auctions_query"
)

#: The frozen ETF panel's last observation. The research event calendar never
#: extends past it.
PANEL_LAST_DATE = "2026-06-12"

#: Fetch window. Starts well before the panel so the historical auction-frequency
#: question is answered from the official record, not from recollection.
FETCH_FIRST_DATE = "1990-01-01"

#: Exactly the fields this lineage may use. Auction OUTCOME fields (yields, prices,
#: bid-to-cover, bidder allotments) are deliberately NOT requested: they are not
#: needed to define the event calendar, and requesting them would widen the
#: lineage's data surface for no design gain.
FIELDS = [
    "cusip",
    "security_type",
    "security_term",
    "original_security_term",
    "announcemt_date",
    "auction_date",
    "issue_date",
    "maturity_date",
    "reopening",
    "inflation_index_security",
    "floating_rate",
    "cash_management_bill_cmb",
    "offering_amt",
]

RAW_DIR = os.path.join("data", "ta")
RAW_PATH = os.path.join(RAW_DIR, "ta_auctions_raw.json")
CALENDAR_PATH = os.path.join("research", "extensions", "ta", "TA_EVENT_CALENDAR.csv")
PANEL_PATH = os.path.join("data", "close_prices_raw.csv")

#: Tenor families, keyed on the official `original_security_term`.
PRIMARY_TENOR = "30-Year"
SECONDARY_TENOR = "10-Year"
PRIMARY_YEARS = 30
SECONDARY_YEARS = 10

#: ON-CYCLE RULE (sealed). An auction joins a tenor family only if the security
#: still has at least (tenor - 6 months) to run at the auction. This excludes
#: off-cycle reopenings of heavily seasoned notes — which are not the mid-month
#: refunding auction the mechanism describes — using nothing but the official
#: record. It is a NO-OP on the primary family (0 of 245 rows dropped), so it
#: cannot have been chosen to shape the primary result.
ON_CYCLE_SLACK_DAYS = 183

#: Window geometry, sealed. Offsets are in COMMON-GRID TRADING DAYS on the frozen
#: panel: not calendar days, not generic business days.
PRE_OFFSET_OPEN = -6    # close(t0-6) opens the pre window
PRE_OFFSET_CLOSE = -1   # close(t0-1) closes the pre window
POST_OFFSET_OPEN = 0    # close(t0)   opens the post window
POST_OFFSET_CLOSE = +5  # close(t0+5) closes the post window

#: The common event grid. All four instruments share an identical trading calendar
#: over the panel's TLT range (verified: 6,007 days, zero set differences, zero
#: internal gaps), so one grid serves every cell.
GRID_TICKER = "TLT"
ALL_TICKERS = ("TLT", "IEF", "SHY", "SPY")

#: Two events collide when their 12-mark spans touch, i.e. when the gap between
#: their t0 grid indices is at most (POST_OFFSET_CLOSE - PRE_OFFSET_OPEN) = 11.
OVERLAP_GAP = POST_OFFSET_CLOSE - PRE_OFFSET_OPEN


# --------------------------------------------------------------------------- #
# Helpers                                                                      #
# --------------------------------------------------------------------------- #


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _date(s):
    return _dt.date.fromisoformat(s[:10]) if s else None


def _truthy(v) -> bool:
    return str(v).strip().lower() in {"yes", "y", "true", "1"}


# --------------------------------------------------------------------------- #
# 1. Fetch — official metadata only                                            #
# --------------------------------------------------------------------------- #


def fetch(out_path: str = RAW_PATH) -> dict:
    """Page the official auctions endpoint and write a deterministic raw extract."""
    rows: list[dict] = []
    page = 1
    query_urls: list[str] = []
    while True:
        params = {
            "fields": ",".join(FIELDS),
            "filter": (
                f"auction_date:gte:{FETCH_FIRST_DATE},"
                f"auction_date:lte:{PANEL_LAST_DATE},"
                "security_type:in:(Note,Bond)"
            ),
            "sort": "auction_date,cusip",
            "page[size]": "10000",
            "page[number]": str(page),
        }
        url = API_BASE + "?" + urllib.parse.urlencode(params, safe=":,()[]")
        query_urls.append(url)
        with urllib.request.urlopen(url, timeout=180) as resp:
            payload = json.load(resp)
        rows.extend(payload["data"])
        if page >= int(payload["meta"]["total-pages"]):
            break
        page += 1

    retrieved_at = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    rows.sort(key=lambda r: (r["auction_date"], r["cusip"] or "", r["security_term"] or ""))
    doc = {
        "source": "U.S. Treasury Fiscal Data - Treasury Securities Auctions Data",
        "endpoint": API_BASE,
        "query_urls": query_urls,
        "retrieved_at_utc": retrieved_at,
        "filter_auction_date_gte": FETCH_FIRST_DATE,
        "filter_auction_date_lte": PANEL_LAST_DATE,
        "filter_security_type": ["Note", "Bond"],
        "fields": FIELDS,
        "row_count": len(rows),
        "data": rows,
    }
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(doc, fh, indent=1, sort_keys=True)
        fh.write("\n")
    return {"path": out_path, "rows": len(rows), "sha256": sha256_file(out_path),
            "retrieved_at_utc": retrieved_at}


def load_raw(path: str = RAW_PATH) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


# --------------------------------------------------------------------------- #
# 2. Classification — mechanical, from the official fields only                #
# --------------------------------------------------------------------------- #


def classify(row: dict) -> str:
    """Tenor-family key for a raw auction row.

    TIPS, FRNs and CMBs are separated out and keep their own keys so that
    calendar-overlap accounting can still see them.
    """
    if _truthy(row.get("cash_management_bill_cmb")):
        return "CMB"
    if _truthy(row.get("inflation_index_security")):
        return "TIPS"
    if _truthy(row.get("floating_rate")):
        return "FRN"
    return (row.get("original_security_term") or "").strip() or "UNKNOWN"


def remaining_days(row: dict) -> int:
    return (_date(row["maturity_date"]) - _date(row["auction_date"])).days


def on_cycle(row: dict, tenor_years: int) -> bool:
    return remaining_days(row) >= tenor_years * 365.25 - ON_CYCLE_SLACK_DAYS


def family_events(raw: dict, tenor: str, tenor_years: int,
                  apply_on_cycle: bool = True) -> list[dict]:
    """Every in-family auction of one tenor, ascending, after the on-cycle rule."""
    out = [r for r in raw["data"] if classify(r) == tenor]
    if apply_on_cycle:
        out = [r for r in out if on_cycle(r, tenor_years)]
    out.sort(key=lambda r: (r["auction_date"], r["cusip"] or ""))
    return out


def qra_dates(raw: dict) -> set:
    """Quarterly Refunding Announcement dates, derived from the pinned record.

    The QRA is the statement that announces the quarterly refunding sizes. Its date
    is exactly the `announcemt_date` shared by the ORIGINAL-ISSUE 10-year note and
    30-year bond of the Feb / May / Aug / Nov refunding. No external calendar is
    needed and none is used.
    """
    out = set()
    for tenor, yrs in ((SECONDARY_TENOR, SECONDARY_YEARS), (PRIMARY_TENOR, PRIMARY_YEARS)):
        for r in family_events(raw, tenor, yrs):
            if str(r.get("reopening", "")).strip().lower() == "no" and r.get("announcemt_date"):
                out.add(_date(r["announcemt_date"]))
    return out


# --------------------------------------------------------------------------- #
# 3. The common trading grid — the ONLY panel contact                          #
# --------------------------------------------------------------------------- #


def trading_calendar(tickers=ALL_TICKERS, panel_path: str = PANEL_PATH) -> dict:
    """Ordered trading days per ticker, from the frozen panel.

    Reads `Date` and a NON-NULL PRESENCE MASK per ticker. The numeric close is
    inspected only to ask "is this cell empty?" and is never retained, returned,
    differenced or aggregated. No price and no return leaves this function.
    """
    cals: dict[str, list] = {t: [] for t in tickers}
    with open(panel_path, "r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        missing = [t for t in tickers if t not in (reader.fieldnames or [])]
        if missing:
            raise KeyError(f"panel is missing columns: {missing}")
        for rec in reader:
            day = _date(rec["Date"])
            if day is None:
                continue
            for t in tickers:
                if (rec[t] or "").strip() != "":      # presence mask only
                    cals[t].append(day)
    for t in tickers:
        cals[t].sort()
    return cals


def common_grid(cals: dict) -> list:
    """The sealed event grid, with its cross-instrument identity assertion."""
    grid = cals[GRID_TICKER]
    lo, hi = grid[0], grid[-1]
    base = set(grid)
    for t in cals:
        other = {d for d in cals[t] if lo <= d <= hi}
        if other != base:
            raise AssertionError(
                f"{t} trading days differ from the {GRID_TICKER} grid inside "
                f"{lo}..{hi}: {len(base - other)} missing, {len(other - base)} extra"
            )
    return grid


# --------------------------------------------------------------------------- #
# 4. Event-window construction — dates and indices only                        #
# --------------------------------------------------------------------------- #


def build_windows(events: list[dict], grid: list) -> list[dict]:
    index = {d: i for i, d in enumerate(grid)}
    n = len(grid)
    out = []
    for ev in events:
        t0 = _date(ev["auction_date"])
        i = index.get(t0)
        iso = t0.isocalendar()
        rec = {
            "auction_date": ev["auction_date"],
            "cusip": ev["cusip"],
            "security_term": ev["security_term"],
            "original_security_term": ev["original_security_term"],
            "remaining_term_days": str(remaining_days(ev)),
            "reopening": ev["reopening"],
            "announcemt_date": (ev["announcemt_date"] or "")[:10],
            "issue_date": (ev["issue_date"] or "")[:10],
            "offering_amt": ev["offering_amt"],
            "t0_is_trading_day": "YES" if i is not None else "NO",
            "iso_year": str(iso[0]),
            "iso_week": str(iso[1]),
            "calendar_month": ev["auction_date"][:7],
        }
        if i is None:
            rec.update(valid_window="NO", exclusion_reason="T0_NOT_ON_GRID",
                       pre_open="", pre_close="", post_open="", post_close="",
                       t0_index="")
            out.append(rec)
            continue
        lo, hi = i + PRE_OFFSET_OPEN, i + POST_OFFSET_CLOSE
        if lo < 0 or hi > n - 1:
            rec.update(
                valid_window="NO",
                exclusion_reason=("WINDOW_BEFORE_PANEL_START" if lo < 0
                                  else "WINDOW_AFTER_PANEL_END"),
                pre_open="", pre_close="", post_open="", post_close="",
                t0_index=str(i),
            )
            out.append(rec)
            continue
        rec.update(
            valid_window="YES", exclusion_reason="",
            pre_open=grid[lo].isoformat(),
            pre_close=grid[i + PRE_OFFSET_CLOSE].isoformat(),
            post_open=grid[i + POST_OFFSET_OPEN].isoformat(),
            post_close=grid[hi].isoformat(),
            t0_index=str(i),
        )
        out.append(rec)
    return out


def return_bearing_days(rec: dict, grid: list) -> list:
    """The days whose close-to-close return enters AC.

    PRE contributes grid[i-5..i-1]; POST contributes grid[i+1..i+5]. The auction-day
    bar grid[i] is EXCLUDED — it belongs to neither window by construction.
    """
    i = int(rec["t0_index"])
    return [grid[j] for j in range(i + PRE_OFFSET_OPEN + 1, i + PRE_OFFSET_CLOSE + 1)] + \
           [grid[j] for j in range(i + POST_OFFSET_OPEN + 1, i + POST_OFFSET_CLOSE + 1)]


def split_days(rec: dict, grid: list) -> tuple[list, list]:
    """(pre return-bearing days, post return-bearing days) for one valid window."""
    i = int(rec["t0_index"])
    pre = [grid[j] for j in range(i + PRE_OFFSET_OPEN + 1, i + PRE_OFFSET_CLOSE + 1)]
    post = [grid[j] for j in range(i + POST_OFFSET_OPEN + 1, i + POST_OFFSET_CLOSE + 1)]
    return pre, post


def signed_indicator(dates: set, pre: list, post: list) -> int:
    """The sealed signed covariate form: 1{in POST} - 1{in PRE}.

    AC is a difference of the two windows, so a release matters through WHICH side
    it lands on. A release in both sides, or in neither, scores 0.
    """
    return int(any(d in dates for d in post)) - int(any(d in dates for d in pre))


def overlap_profile(rows: list[dict], raw: dict, grid: list, qra: set) -> dict:
    """Per-window counts of other auctions, plus the QRA and own-announcement marks."""
    by_day = defaultdict(list)
    for r in raw["data"]:
        by_day[_date(r["auction_date"])].append(classify(r))
    prof = {}
    for w in rows:
        if w["valid_window"] != "YES":
            continue
        pre, post = split_days(w, grid)
        days = pre + post
        c: Counter = Counter()
        for d in days:
            for fam in by_day.get(d, []):
                c[fam] += 1
        ann = {_date(w["announcemt_date"])} if w["announcemt_date"] else set()
        prof[w["auction_date"]] = {
            "counts": c,
            "qra_in_window": any(d in qra for d in days),
            "qra_signed": signed_indicator(qra, pre, post),
            "ann_in_window": any(d in ann for d in days),
            "ann_signed": signed_indicator(ann, pre, post),
        }
    return prof


# --------------------------------------------------------------------------- #
# 5. The committed event calendar                                              #
# --------------------------------------------------------------------------- #

OVL_FAMILIES = ["2-Year", "3-Year", "5-Year", "7-Year", "10-Year",
                "20-Year", "30-Year", "TIPS", "FRN"]

CAL_COLUMNS = (
    ["cell", "instrument", "tenor_family", "auction_date", "cusip", "security_term",
     "original_security_term", "remaining_term_days", "reopening", "announcemt_date",
     "issue_date", "offering_amt", "t0_is_trading_day", "valid_window",
     "exclusion_reason", "pre_open", "pre_close", "post_open", "post_close",
     "t0_index", "iso_year", "iso_week", "calendar_month",
     "qra_in_window", "qra_signed", "ann_in_window", "ann_signed"]
    + [f"ovl_{f.replace('-', '')}" for f in OVL_FAMILIES]
)

CELLS = (("PRIMARY", "TLT", PRIMARY_TENOR, PRIMARY_YEARS),
         ("SECONDARY", "IEF", SECONDARY_TENOR, SECONDARY_YEARS))


def build(raw_path: str = RAW_PATH, out_path: str = CALENDAR_PATH) -> dict:
    raw = load_raw(raw_path)
    grid = common_grid(trading_calendar())
    qra = qra_dates(raw)
    rows: list[dict] = []
    for cell, ticker, tenor, yrs in CELLS:
        wins = build_windows(family_events(raw, tenor, yrs), grid)
        prof = overlap_profile(wins, raw, grid, qra)
        for w in wins:
            p = prof.get(w["auction_date"])
            rec = {"cell": cell, "instrument": ticker, "tenor_family": tenor, **w}
            rec["qra_in_window"] = ("YES" if p["qra_in_window"] else "NO") if p else ""
            rec["qra_signed"] = str(p["qra_signed"]) if p else ""
            rec["ann_in_window"] = ("YES" if p["ann_in_window"] else "NO") if p else ""
            rec["ann_signed"] = str(p["ann_signed"]) if p else ""
            for f in OVL_FAMILIES:
                rec[f"ovl_{f.replace('-', '')}"] = str(p["counts"].get(f, 0)) if p else ""
            rows.append(rec)
    rows.sort(key=lambda r: (r["cell"], r["auction_date"], r["cusip"] or ""))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="\n") as fh:
        wtr = csv.DictWriter(fh, fieldnames=CAL_COLUMNS, lineterminator="\n")
        wtr.writeheader()
        for r in rows:
            wtr.writerow({k: r.get(k, "") for k in CAL_COLUMNS})
    return {"path": out_path, "rows": len(rows), "sha256": sha256_file(out_path)}


# --------------------------------------------------------------------------- #
# 6. The S1 count report                                                       #
# --------------------------------------------------------------------------- #


def month_grid(valid: list[dict]) -> list[str]:
    first, last = valid[0]["calendar_month"], valid[-1]["calendar_month"]
    y0, m0 = int(first[:4]), int(first[5:])
    y1, m1 = int(last[:4]), int(last[5:])
    out = []
    y, m = y0, m0
    while (y, m) <= (y1, m1):
        out.append(f"{y:04d}-{m:02d}")
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


def report(raw_path: str = RAW_PATH) -> dict:
    raw = load_raw(raw_path)
    cals = trading_calendar()
    grid = common_grid(cals)
    qra = qra_dates(raw)
    facts: dict = {}

    print(f"RAW   rows={raw['row_count']}  retrieved={raw['retrieved_at_utc']}")
    print(f"RAW   sha256={sha256_file(raw_path)}")
    print(f"GRID  {GRID_TICKER}: {len(grid)} trading days {grid[0]} .. {grid[-1]} "
          f"(identical for {', '.join(ALL_TICKERS)})")
    print(f"QRA   dates derived from the record: {len(qra)} "
          f"({min(qra)} .. {max(qra)})")
    print("FAMS  " + str(dict(sorted(Counter(classify(r) for r in raw['data']).items(),
                                     key=lambda kv: -kv[1]))))

    for cell, ticker, tenor, yrs in CELLS:
        infam = [r for r in raw["data"] if classify(r) == tenor]
        ev = family_events(raw, tenor, yrs)
        dropped = [(r["auction_date"], r["security_term"]) for r in infam
                   if not on_cycle(r, yrs)]
        wins = build_windows(ev, grid)
        valid = sorted((w for w in wins if w["valid_window"] == "YES"),
                       key=lambda w: int(w["t0_index"]))
        gaps = [int(b["t0_index"]) - int(a["t0_index"]) for a, b in zip(valid, valid[1:])]
        ovl = [(a["auction_date"], b["auction_date"], g)
               for a, b, g in zip(valid, valid[1:], gaps) if g <= OVERLAP_GAP]
        months = Counter(w["calendar_month"] for w in valid)
        weeks = Counter((w["iso_year"], w["iso_week"]) for w in valid)
        years = sorted({w["auction_date"][:4] for w in valid})
        mg = month_grid(valid)
        print(f"\n=== {cell}  {ticker} / {tenor} ===")
        print(f"  in-family rows 1990-01-01..{PANEL_LAST_DATE} : {len(infam)}")
        print(f"  dropped by the ON-CYCLE rule                 : {len(dropped)} {dropped}")
        print(f"  on-cycle auctions                            : {len(ev)}")
        print(f"  VALID COMPLETE WINDOWS                       : {len(valid)}")
        print(f"  exclusions: " + str(dict(Counter(
            w["exclusion_reason"] for w in wins if w["exclusion_reason"]))))
        print(f"  first valid t0 {valid[0]['auction_date']}   last {valid[-1]['auction_date']}")
        print(f"  calendar years represented : {len(years)}  ({years[0]}..{years[-1]})")
        print(f"  unique ISO auction weeks   : {len(weeks)}  max events per week: "
              f"{max(weeks.values())}")
        print(f"  max valid events per calendar month: {max(months.values())}"
              + (f"   months>1: {{{', '.join(f'{k}: {v}' for k, v in months.items() if v > 1)}}}"
                 if any(v > 1 for v in months.values()) else "   (none)"))
        print(f"  min consecutive t0 gap: {min(gaps)} grid days "
              f"(collision threshold <= {OVERLAP_GAP})")
        print(f"  OVERLAPPING VALID WINDOWS : {len(ovl)} {ovl}")
        print(f"  reopening split: {dict(Counter(w['reopening'] for w in valid))}")
        print(f"  month grid: {mg[0]} .. {mg[-1]} = {len(mg)} months "
              f"({len(months)} event months, {len(mg) - len(months)} zero months)")
        print(f"  auctions per calendar year (in-family): "
              + " ".join(f"{y}:{c}" for y, c in
                         sorted(Counter(r['auction_date'][:4] for r in infam).items())))
        facts[cell] = {
            "in_family": len(infam), "on_cycle": len(ev), "valid": len(valid),
            "dropped": dropped, "first": valid[0]["auction_date"],
            "last": valid[-1]["auction_date"], "years": len(years),
            "weeks": len(weeks), "max_per_week": max(weeks.values()),
            "max_per_month": max(months.values()), "overlaps": len(ovl),
            "min_gap": min(gaps), "month_grid": len(mg),
            "event_months": len(months), "zero_months": len(mg) - len(months),
            "month_first": mg[0], "month_last": mg[-1],
            "per_year": dict(sorted(Counter(w["auction_date"][:4] for w in valid).items())),
        }

    print("\n=== STRUCTURAL CALENDAR OVERLAP INSIDE THE PRIMARY WINDOWS ===")
    wins = build_windows(family_events(raw, PRIMARY_TENOR, PRIMARY_YEARS), grid)
    prof = overlap_profile(wins, raw, grid, qra)
    n = len(prof)
    present: Counter = Counter()
    total: Counter = Counter()
    for p in prof.values():
        total.update(p["counts"])
        for fam in p["counts"]:
            present[fam] += 1
    print(f"  valid primary windows examined: {n}")
    for fam, cnt in sorted(present.items(), key=lambda kv: -kv[1]):
        print(f"    {fam:<10} in {cnt:>3}/{n} windows ({100.0*cnt/n:5.1f}%)   "
              f"total auctions {total[fam]}")
    clean = sum(1 for p in prof.values()
                if sum(v for k, v in p["counts"].items() if k != PRIMARY_TENOR) == 0)
    qin = sum(1 for p in prof.values() if p["qra_in_window"])
    ain = sum(1 for p in prof.values() if p["ann_in_window"])
    print(f"  windows with NO other auction of any family: {clean}/{n}")
    print(f"  windows whose return-bearing span contains a QRA: {qin}/{n} "
          f"({100.0*qin/n:.1f}%)   signed: "
          + str(dict(sorted(Counter(p["qra_signed"] for p in prof.values()).items()))))
    print(f"  windows containing their OWN announcement date   : {ain}/{n} "
          f"({100.0*ain/n:.1f}%)   signed: "
          + str(dict(sorted(Counter(p["ann_signed"] for p in prof.values()).items()))))
    facts["overlap"] = {"n": n, "present": dict(present), "clean": clean, "qra": qin}
    return facts


def main(argv: list[str]) -> int:
    cmd = argv[1] if len(argv) > 1 else "report"
    if cmd == "fetch":
        print(json.dumps(fetch(), indent=2))
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
