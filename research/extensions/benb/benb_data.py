"""CTA-EDGE-02-BENB — data sources, validation, alignment and the ex-date calendar.

Components B, C, D and E of the S2 build, plus the real-data firewall.

Price and NAV reach the outcome engine through a `CellSource` and through nothing else.
There are exactly two implementations:

* `SyntheticCellSource` — fixture series held in memory. `data_kind = SYNTHETIC`.
  It has **no path attribute and performs no file access at all**, so no test can fall
  through to the production historical files if a patch is forgotten or mis-ordered.
* `RealCellSource` — the pinned historical files. `data_kind = REAL`. Its constructor
  calls the run guard **before opening anything**, so an unauthorised historical run
  terminates before a single price or NAV byte is read.

This is dependency injection, not mocking.
"""

from __future__ import annotations

import csv
import datetime as _dt
import hashlib
import os
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Set

from benb_authorization import REAL, SYNTHETIC, require_run_authorization
import benb_contract as K

_MON = {m: i for i, m in enumerate(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov",
     "Dec"], start=1)}


class DataDefect(RuntimeError):
    """A structural defect in the inputs. Never silently repaired."""


@dataclass
class CellData:
    """One fund's aligned, validated, date-only-intersected panel."""
    ticker: str
    grid: List[_dt.date]                      # ascending common dates
    p_open: Dict[_dt.date, float]
    p_close: Dict[_dt.date, float]
    nav: Dict[_dt.date, float]
    ex_dates: Set[_dt.date]                   # UNION of the two calendars
    data_kind: str = SYNTHETIC
    provenance: Dict[str, str] = field(default_factory=dict)

    def validate(self) -> None:
        """Structural validation. Raises rather than repairing."""
        if len(self.grid) != len(set(self.grid)):
            raise DataDefect(f"{self.ticker}: duplicated dates in the grid")
        if self.grid != sorted(self.grid):
            raise DataDefect(f"{self.ticker}: grid is not ascending")
        for d in self.grid:
            for name, m in (("open", self.p_open), ("close", self.p_close),
                            ("nav", self.nav)):
                if d not in m:
                    raise DataDefect(f"{self.ticker}: missing {name} on {d}")
                if not (m[d] > 0.0):
                    raise DataDefect(f"{self.ticker}: non-positive {name} on {d}")


# --------------------------------------------------------------------------- #
# B / C / D / E — sources                                                      #
# --------------------------------------------------------------------------- #


def align_grid(price_dates: Iterable[_dt.date],
               nav_dates: Iterable[_dt.date]) -> List[_dt.date]:
    """Contract §D.1: the common grid is the DATE-ONLY INTERSECTION, ascending.

    Never a forward fill, never a reindex, never a merge_asof, never a nearest-date
    match. A price day with no issuer NAV, or a NAV day with no traded price, simply
    does not exist for this study. Exposed as a function so the rule is testable
    without touching the historical panel.
    """
    return sorted(set(price_dates) & set(nav_dates))


class CellSource:
    data_kind = "UNSET"

    def load(self, ticker: str) -> CellData:
        raise NotImplementedError


class SyntheticCellSource(CellSource):
    """Fixture prices and NAVs. Touches no file and no network, ever."""

    data_kind = SYNTHETIC

    def __init__(self, cells: Mapping[str, CellData]):
        if not cells:
            raise ValueError("a synthetic source needs at least one cell")
        self._cells = dict(cells)
        for c in self._cells.values():
            c.data_kind = SYNTHETIC
            c.validate()

    def tickers(self) -> Sequence[str]:
        return sorted(self._cells)

    def load(self, ticker: str) -> CellData:
        return self._cells[ticker]


class RealCellSource(CellSource):
    """The pinned historical files — REACHABLE ONLY WITH A COMMITTED OWNER GRANT."""

    data_kind = REAL

    def __init__(self, run_id: str = "", data_dir: str = K.DATA_DIR,
                 verify_hashes: bool = True):
        # THE GUARD COMES FIRST. Nothing below it runs without a committed grant, so an
        # unauthorised historical invocation never opens a price or NAV file.
        require_run_authorization(REAL, run_id)
        self._dir = data_dir
        self._verify = verify_hashes

    def _pin_check(self, name: str) -> str:
        path = os.path.join(self._dir, name)
        digest = hashlib.sha256(open(path, "rb").read()).hexdigest()
        if self._verify and digest != K.PINNED[name]:
            raise DataDefect(
                f"LEVEL-1 PRE-RUN FAILURE: {name} sha256 {digest} does not match the "
                f"sealed pin {K.PINNED[name]}")
        return path

    def load(self, ticker: str) -> CellData:
        px_path = self._pin_check(f"{ticker}_raw_ohlc.csv")
        nav_path = self._pin_check(f"{ticker}_nav_daily.csv")

        p_open: Dict[_dt.date, float] = {}
        p_close: Dict[_dt.date, float] = {}
        px_dividends: Set[_dt.date] = set()
        with open(px_path, "r", encoding="utf-8", newline="") as fh:
            rd = csv.DictReader(fh)
            key = [c for c in (rd.fieldnames or []) if c.lower().startswith("date")][0]
            for r in rd:
                d = _dt.date.fromisoformat(r[key][:10])
                p_open[d] = float(r["Open"])
                p_close[d] = float(r["Close"])
                if (r.get("Dividends") or "0").strip() not in ("", "0", "0.0"):
                    px_dividends.add(d)

        nav: Dict[_dt.date, float] = {}
        issuer_ex: Set[_dt.date] = set()
        with open(nav_path, "r", encoding="utf-8", newline="") as fh:
            for r in csv.DictReader(fh):
                d = _dt.date.fromisoformat(r["date"])
                nav[d] = float(r["nav_per_share"])
                if (r.get("ex_dividend") or "").strip():
                    issuer_ex.add(d)

        grid = align_grid(p_close, nav)          # §D.1 intersection
        cell = CellData(
            ticker=ticker, grid=grid,
            p_open={d: p_open[d] for d in grid},
            p_close={d: p_close[d] for d in grid},
            nav={d: nav[d] for d in grid},
            ex_dates=(issuer_ex | px_dividends),          # §D.4 UNION
            data_kind=REAL,
            provenance={"price": px_path, "nav": nav_path,
                        "nav_provenance": K.NAV_PROVENANCE})
        cell.validate()
        return cell


def is_synthetic(source: CellSource) -> bool:
    return source.data_kind == SYNTHETIC


def assert_synthetic(source: CellSource) -> None:
    """S2 harness gate: every validation path must be synthetic."""
    if not is_synthetic(source):
        raise AssertionError(
            f"S2 validation may only use SYNTHETIC sources; got "
            f"{source.data_kind!r} ({type(source).__name__})")


def synthetic_source_cannot_reach_production_paths(source: CellSource) -> bool:
    """Mechanical proof for §24: a synthetic source holds no path to production data."""
    if not is_synthetic(source):
        return False
    blob = repr(getattr(source, "__dict__", {}))
    return (K.DATA_DIR not in blob and "data/benb" not in blob
            and "data\\benb" not in blob
            and not any(hasattr(source, a) for a in ("_dir", "_path", "_paths")))


# --------------------------------------------------------------------------- #
# D — eligibility                                                              #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class Eligibility:
    index: Dict[_dt.date, int]
    eligible: List[_dt.date]
    excluded_ex_date: List[_dt.date]
    excluded_burn_in: List[_dt.date]
    excluded_no_next: List[_dt.date]


def eligibility(cell: CellData,
                min_prior: int = K.MIN_PRIOR_HISTORY) -> Eligibility:
    """Contract §D.2. A date is eligible iff:

    1. it is on the common grid (true by construction of `CellData.grid`);
    2. the next grid date exists;
    3. at least `min_prior` prior grid observations exist;
    4. the next grid date is NOT an ex-date (the §D.4 union).
    """
    grid = cell.grid
    idx = {d: i for i, d in enumerate(grid)}
    elig, ex, burn, nonext = [], [], [], []
    for i, d in enumerate(grid):
        if i < min_prior:
            burn.append(d)
            continue
        if i + 1 >= len(grid):
            nonext.append(d)
            continue
        if grid[i + 1] in cell.ex_dates:
            ex.append(d)
            continue
        elig.append(d)
    return Eligibility(index=idx, eligible=elig, excluded_ex_date=ex,
                       excluded_burn_in=burn, excluded_no_next=nonext)
