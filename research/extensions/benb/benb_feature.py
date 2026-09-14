"""CTA-EDGE-02-BENB — the causal basis feature and the discount-side filter.

Components F and G of the S2 build.

    b_t = ln( P_close,t / NAV_t )                       raw close over issuer NAV
    m_t = MEDIAN{ b_s : s < t }                         EXPANDING, strictly causal
    x_t = b_t - m_t
    d_t = -x_t  on the DISCOUNT side only (x_t < 0)

`m_t` never sees `b_t`. That is not a comment, it is the loop invariant: the median is
taken over `values[:i]` and the current observation is appended only afterwards.
"""

from __future__ import annotations

import datetime as _dt
import math
import statistics
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence

import benb_contract as K
from benb_data import CellData


@dataclass(frozen=True)
class FeatureRow:
    date: _dt.date
    index: int
    b: float
    m: Optional[float]       # None before the minimum history is reached
    x: Optional[float]
    has_feature: bool

    @property
    def is_discount(self) -> bool:
        return self.has_feature and self.x is not None and self.x < 0.0

    @property
    def is_premium(self) -> bool:
        return self.has_feature and self.x is not None and self.x >= 0.0

    @property
    def severity(self) -> Optional[float]:
        """d_t = -x_t, defined only on the discount side."""
        return -self.x if self.is_discount else None


def basis(cell: CellData, day: _dt.date) -> float:
    """b_t = ln(P_close,t / NAV_t). RAW close, official issuer NAV."""
    return math.log(cell.p_close[day]) - math.log(cell.nav[day])


def features(cell: CellData,
             min_prior: int = K.MIN_PRIOR_HISTORY) -> List[FeatureRow]:
    """Every grid date's causal feature row.

    The expanding median uses ONLY observations strictly before the current date, and
    the current basis is appended to the history AFTER the median is taken. A future
    observation can therefore never alter a historical `x_t`.
    """
    history: List[float] = []
    out: List[FeatureRow] = []
    for i, day in enumerate(cell.grid):
        b = basis(cell, day)
        if len(history) >= min_prior:
            m = statistics.median(history)         # history holds s < day only
            out.append(FeatureRow(day, i, b, m, b - m, True))
        else:
            out.append(FeatureRow(day, i, b, None, None, False))
        history.append(b)                          # strictly AFTER the median
    return out


def discount_rows(rows: Sequence[FeatureRow],
                  eligible: Sequence[_dt.date]) -> List[FeatureRow]:
    """§D.5 primary sample: eligible AND x_t < 0. Continuous, no threshold."""
    ok = set(eligible)
    return [r for r in rows if r.date in ok and r.is_discount]


def premium_rows(rows: Sequence[FeatureRow],
                 eligible: Sequence[_dt.date]) -> List[FeatureRow]:
    """DESCRIPTIVE ONLY. PROMOTION_POWER = NONE. RESCUE_POWER = NONE.

    Never passed to `benb_classify`, which accepts no premium argument at all.
    """
    ok = set(eligible)
    return [r for r in rows if r.date in ok and r.is_premium]


def by_date(rows: Sequence[FeatureRow]) -> Dict[_dt.date, FeatureRow]:
    return {r.date: r for r in rows}
