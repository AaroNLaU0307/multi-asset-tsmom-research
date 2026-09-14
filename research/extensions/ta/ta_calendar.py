"""CTA-EDGE-01-TA — event-calendar loading, window construction and validation.

Components A and B of the S2 build. Dates and indices only: this module never sees a
price and never computes a return.
"""

from __future__ import annotations

import csv
import datetime as _dt
import hashlib
from dataclasses import dataclass
from typing import Dict, List, Sequence

import ta_contract as K


@dataclass(frozen=True)
class Event:
    """One valid event window, entirely in dates and grid indices."""
    cell: str
    instrument: str
    t0: _dt.date
    t0_index: int
    pre_open: _dt.date
    pre_close: _dt.date
    post_open: _dt.date
    post_close: _dt.date
    calendar_month: str
    iso_year: int
    reopening: str = ""
    cusip: str = ""

    @property
    def year(self) -> int:
        return self.t0.year

    def pre_days(self, grid: Sequence[_dt.date]) -> List[_dt.date]:
        """Return-bearing PRE days: GRID[i-5 .. i-1]."""
        i = self.t0_index
        return list(grid[i + K.PRE_OFFSET_OPEN + 1: i + K.PRE_OFFSET_CLOSE + 1])

    def post_days(self, grid: Sequence[_dt.date]) -> List[_dt.date]:
        """Return-bearing POST days: GRID[i+1 .. i+5]."""
        i = self.t0_index
        return list(grid[i + K.POST_OFFSET_OPEN + 1: i + K.POST_OFFSET_CLOSE + 1])

    def auction_day_bar(self, grid: Sequence[_dt.date]):
        """The EXCLUDED bar: (GRID[i-1], GRID[i]). Belongs to neither window."""
        i = self.t0_index
        return grid[i + K.PRE_OFFSET_CLOSE], grid[i]


# --------------------------------------------------------------------------- #
# Generic window construction — used by fixtures and asserted against the seal #
# --------------------------------------------------------------------------- #


def windows_from_grid(t0s: Sequence[_dt.date], grid: Sequence[_dt.date],
                      cell: str, instrument: str,
                      meta: Dict[_dt.date, Dict[str, str]] | None = None
                      ) -> List[Event]:
    """Build every VALID window for the given anchors on the given grid.

    §B.5: valid iff t0 is on the grid and both i-6 and i+5 are in range. There is no
    other inclusion criterion, and no outcome may ever remove an event.
    """
    index = {d: i for i, d in enumerate(grid)}
    n = len(grid)
    out: List[Event] = []
    for t0 in sorted(t0s):
        i = index.get(t0)
        if i is None:
            continue
        if i + K.PRE_OFFSET_OPEN < 0 or i + K.POST_OFFSET_CLOSE > n - 1:
            continue
        m = (meta or {}).get(t0, {})
        out.append(Event(
            cell=cell, instrument=instrument, t0=t0, t0_index=i,
            pre_open=grid[i + K.PRE_OFFSET_OPEN],
            pre_close=grid[i + K.PRE_OFFSET_CLOSE],
            post_open=grid[i + K.POST_OFFSET_OPEN],
            post_close=grid[i + K.POST_OFFSET_CLOSE],
            calendar_month=f"{t0.year:04d}-{t0.month:02d}",
            iso_year=t0.isocalendar()[0],
            reopening=m.get("reopening", ""), cusip=m.get("cusip", "")))
    return out


def overlapping_pairs(events: Sequence[Event]) -> List[tuple]:
    ev = sorted(events, key=lambda e: e.t0_index)
    return [(a.t0, b.t0, b.t0_index - a.t0_index)
            for a, b in zip(ev, ev[1:])
            if b.t0_index - a.t0_index <= K.OVERLAP_GAP]


# --------------------------------------------------------------------------- #
# The sealed calendar                                                          #
# --------------------------------------------------------------------------- #


def sealed_calendar_sha256(path: str = K.EVENT_CALENDAR_PATH) -> str:
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def load_sealed_events(cell: str, path: str = K.EVENT_CALENDAR_PATH,
                       verify_sha256: bool = True) -> List[Event]:
    """Every VALID window of one cell, from the committed sealed calendar."""
    if verify_sha256:
        digest = sealed_calendar_sha256(path)
        if digest != K.EVENT_CALENDAR_SHA256:
            raise RuntimeError(
                f"LEVEL-1 PRE-RUN FAILURE: event calendar sha256 {digest} does not "
                f"match the sealed pin {K.EVENT_CALENDAR_SHA256}")
    out: List[Event] = []
    with open(path, "r", encoding="utf-8", newline="") as fh:
        for rec in csv.DictReader(fh):
            if rec["cell"] != cell or rec["valid_window"] != "YES":
                continue
            out.append(Event(
                cell=rec["cell"], instrument=rec["instrument"],
                t0=_dt.date.fromisoformat(rec["auction_date"]),
                t0_index=int(rec["t0_index"]),
                pre_open=_dt.date.fromisoformat(rec["pre_open"]),
                pre_close=_dt.date.fromisoformat(rec["pre_close"]),
                post_open=_dt.date.fromisoformat(rec["post_open"]),
                post_close=_dt.date.fromisoformat(rec["post_close"]),
                calendar_month=rec["calendar_month"],
                iso_year=int(rec["iso_year"]),
                reopening=rec["reopening"], cusip=rec["cusip"]))
    return sorted(out, key=lambda e: e.t0)


def validate_primary(events: Sequence[Event]) -> Dict[str, object]:
    """Assert the sealed §C.2 structure. Any deviation is a LEVEL-1 pre-run failure."""
    from collections import Counter
    problems: List[str] = []
    if len(events) != K.PRIMARY_VALID_WINDOWS:
        problems.append(f"valid windows {len(events)} != {K.PRIMARY_VALID_WINDOWS}")
    if events:
        if events[0].t0.isoformat() != K.PRIMARY_FIRST_T0:
            problems.append(f"first t0 {events[0].t0} != {K.PRIMARY_FIRST_T0}")
        if events[-1].t0.isoformat() != K.PRIMARY_LAST_T0:
            problems.append(f"last t0 {events[-1].t0} != {K.PRIMARY_LAST_T0}")
    years = sorted({e.year for e in events})
    if tuple(years) != K.PRIMARY_YEARS:
        problems.append(f"years {years[:3]}..{years[-3:]} != sealed 21-year set")
    months = Counter(e.calendar_month for e in events)
    if months and max(months.values()) != 1:
        problems.append(f"max events per calendar month {max(months.values())} != 1")
    weeks = Counter((e.iso_year, e.t0.isocalendar()[1]) for e in events)
    if weeks and max(weeks.values()) != 1:
        problems.append(f"max events per ISO week {max(weeks.values())} != 1")
    overlaps = overlapping_pairs(events)
    if overlaps:
        problems.append(f"{len(overlaps)} overlapping primary windows")
    reop = dict(Counter(e.reopening for e in events))
    if reop != K.PRIMARY_REOPENING_SPLIT:
        problems.append(f"reopening split {reop} != {K.PRIMARY_REOPENING_SPLIT}")
    grid = month_grid()
    if len(grid) != K.MONTH_GRID_N:
        problems.append(f"month grid {len(grid)} != {K.MONTH_GRID_N}")
    if len(months) != K.MONTH_GRID_EVENT_MONTHS:
        problems.append(f"event months {len(months)} != {K.MONTH_GRID_EVENT_MONTHS}")
    if len(grid) - len(months) != K.MONTH_GRID_ZERO_MONTHS:
        problems.append(f"zero months {len(grid) - len(months)} != "
                        f"{K.MONTH_GRID_ZERO_MONTHS}")
    return {"ok": not problems, "problems": problems, "n_events": len(events),
            "n_years": len(years), "n_event_months": len(months),
            "n_zero_months": len(grid) - len(months), "n_overlaps": len(overlaps)}


def validate_secondary(events: Sequence[Event]) -> Dict[str, object]:
    problems: List[str] = []
    if len(events) != K.SECONDARY_VALID_WINDOWS:
        problems.append(f"valid windows {len(events)} != {K.SECONDARY_VALID_WINDOWS}")
    years = sorted({e.year for e in events})
    if tuple(years) != K.SECONDARY_YEARS:
        problems.append("secondary year set does not match the sealed 25-year set")
    overlaps = overlapping_pairs(events)
    if len(overlaps) != 1:
        problems.append(f"{len(overlaps)} overlapping secondary windows, sealed is 1")
    return {"ok": not problems, "problems": problems, "n_events": len(events),
            "n_years": len(years), "n_overlaps": len(overlaps),
            "overlaps": [(str(a), str(b), g) for a, b, g in overlaps]}


# --------------------------------------------------------------------------- #
# The calendarised month grid (§F.1)                                           #
# --------------------------------------------------------------------------- #


def month_grid(first: str = K.MONTH_GRID_FIRST, last: str = K.MONTH_GRID_LAST
               ) -> List[str]:
    """Every calendar month from `first` to `last` inclusive. Zero months included."""
    y, m = int(first[:4]), int(first[5:7])
    y1, m1 = int(last[:4]), int(last[5:7])
    out = []
    while (y, m) <= (y1, m1):
        out.append(f"{y:04d}-{m:02d}")
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


def months_of_year(grid: Sequence[str], year: int) -> List[str]:
    """The months a given calendar year contributes to the grid (11 for 2006, 5 for
    2026, 12 otherwise) — the unit the year-block bootstrap concatenates."""
    return [m for m in grid if int(m[:4]) == year]
