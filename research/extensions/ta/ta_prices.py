"""CTA-EDGE-01-TA — price access, behind the real-data firewall.

Prices enter the outcome engine through a `PriceSource` and through nothing else.
There are exactly two implementations:

* `SyntheticPriceSource` — fixture series held in memory. `data_kind = SYNTHETIC`.
  Every S2 validation uses this, and it cannot reach the real panel: it has no path
  and no file access at all.
* `RealPanelPriceSource` — the frozen ETF panel. `data_kind = REAL`. Its constructor
  calls the run guard BEFORE opening anything, so an unauthorised historical run
  terminates before a single price byte is read.

This is dependency injection, not mocking. Tests pass a synthetic source in; nothing
is patched, so no test can silently fall through to the real loader if a patch is
forgotten or applied in the wrong order.
"""

from __future__ import annotations

import csv
import datetime as _dt
import hashlib
import os
from typing import Dict, Iterable, List, Mapping, Optional, Sequence

from ta_authorization import REAL, SYNTHETIC, require_run_authorization
import ta_contract as K


class PriceSource:
    """Read-only access to one close per (ticker, date). No returns, no statistics."""

    data_kind = "UNSET"

    def tickers(self) -> Sequence[str]:
        raise NotImplementedError

    def grid(self) -> List[_dt.date]:
        """The ordered trading grid every cell of this source shares."""
        raise NotImplementedError

    def close(self, ticker: str, day: _dt.date) -> float:
        raise NotImplementedError

    def describe(self) -> Dict[str, object]:
        return {"data_kind": self.data_kind, "tickers": list(self.tickers()),
                "grid_days": len(self.grid())}


class SyntheticPriceSource(PriceSource):
    """Fixture prices. Touches no file and no network, ever."""

    data_kind = SYNTHETIC

    def __init__(self, series: Mapping[str, Mapping[_dt.date, float]],
                 grid: Optional[Iterable[_dt.date]] = None):
        if not series:
            raise ValueError("a synthetic source needs at least one series")
        self._series = {t: dict(s) for t, s in series.items()}
        if grid is None:
            days: set = set()
            for s in self._series.values():
                days |= set(s)
            self._grid = sorted(days)
        else:
            self._grid = sorted(grid)

    def tickers(self) -> Sequence[str]:
        return sorted(self._series)

    def grid(self) -> List[_dt.date]:
        return list(self._grid)

    def close(self, ticker: str, day: _dt.date) -> float:
        try:
            return self._series[ticker][day]
        except KeyError as exc:
            raise KeyError(f"synthetic source has no close for {ticker} on {day}") from exc


class RealPanelPriceSource(PriceSource):
    """The frozen ETF panel — REACHABLE ONLY WITH A COMMITTED OWNER GRANT."""

    data_kind = REAL

    def __init__(self, tickers: Sequence[str], panel_path: str = K.PANEL_PATH,
                 run_id: str = "", verify_sha256: bool = True):
        # THE GUARD COMES FIRST. Nothing below it runs without a committed grant,
        # so an unauthorised historical invocation never opens the panel.
        require_run_authorization(REAL, run_id)

        self._tickers = tuple(tickers)
        self._panel_path = panel_path
        if verify_sha256:
            digest = hashlib.sha256(open(panel_path, "rb").read()).hexdigest()
            if digest != K.PANEL_SHA256:
                raise RuntimeError(
                    f"LEVEL-1 PRE-RUN FAILURE: panel sha256 {digest} does not match "
                    f"the sealed pin {K.PANEL_SHA256}")
        series: Dict[str, Dict[_dt.date, float]] = {t: {} for t in self._tickers}
        with open(panel_path, "r", encoding="utf-8", newline="") as fh:
            for rec in csv.DictReader(fh):
                day = _dt.date.fromisoformat(rec["Date"][:10])
                for t in self._tickers:
                    raw = (rec[t] or "").strip()
                    if raw:
                        series[t][day] = float(raw)
        self._series = series
        common = None
        for t in self._tickers:
            days = set(series[t])
            common = days if common is None else (common & days)
        self._grid = sorted(common or [])

    def tickers(self) -> Sequence[str]:
        return self._tickers

    def grid(self) -> List[_dt.date]:
        return list(self._grid)

    def close(self, ticker: str, day: _dt.date) -> float:
        return self._series[ticker][day]


def is_synthetic(source: PriceSource) -> bool:
    return source.data_kind == SYNTHETIC


def assert_synthetic(source: PriceSource) -> None:
    """Used by the S2 harness: every validation path must be synthetic."""
    if not is_synthetic(source):
        raise AssertionError(
            f"S2 validation may only use SYNTHETIC price sources; got "
            f"{source.data_kind!r} ({type(source).__name__})")
