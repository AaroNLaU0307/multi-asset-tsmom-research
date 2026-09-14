"""CTA-EDGE-01-TA — the sealed macro / QRA covariates and their cross-tabulation.

Component O of the S2 build, plus the outcome-free pre-check the seal requires
(§G.3, §T.2 item 6): the covariate cross-tabulation must be reported BEFORE any `AC`
exists, so Class-D reachability is known while the lineage is still outcome-blind.

Nothing here reads a price or computes a return. Every quantity is a count.
"""

from __future__ import annotations

import csv
import datetime as _dt
import hashlib
import os
from collections import Counter
from dataclasses import dataclass
from typing import Dict, List, Mapping, Sequence, Set

import ta_contract as K
from ta_calendar import Event

COVARIATE_PATH = os.path.join(K.TA_DIR, "TA_MACRO_COVARIATES.csv")
COV_COLUMNS = ["t0", "calendar_month", "year"] + [c.lower() for c in K.MACRO_COVARIATES]


def load_macro_calendar(path: str = K.MACRO_CALENDAR_PATH) -> Dict[str, Set[_dt.date]]:
    """{series -> set(date)} for CPI, NFP, FOMC and QRA."""
    out: Dict[str, Set[_dt.date]] = {c: set() for c in K.MACRO_COVARIATES}
    with open(path, "r", encoding="utf-8", newline="") as fh:
        for rec in csv.DictReader(fh):
            if rec["series"] in out:
                out[rec["series"]].add(_dt.date.fromisoformat(rec["date"]))
    return out


def signed_covariate(dates: Set[_dt.date], pre_days: Sequence[_dt.date],
                     post_days: Sequence[_dt.date]) -> int:
    """§G.3: 1{release on a POST return-bearing day} - 1{release on a PRE one}.

    A release present on both sides, or on neither, correctly scores 0 — `AC` is a
    difference of the two windows, so a release matters through which side it lands on.
    """
    return (int(any(d in dates for d in post_days))
            - int(any(d in dates for d in pre_days)))


@dataclass(frozen=True)
class EventCovariates:
    t0: _dt.date
    calendar_month: str
    year: int
    values: Dict[str, int]

    @property
    def is_reference(self) -> bool:
        """True iff every sealed covariate is 0 — the intercept's reference group."""
        return all(v == 0 for v in self.values.values())


def build_covariates(events: Sequence[Event], grid: Sequence[_dt.date],
                     calendar: Mapping[str, Set[_dt.date]]) -> List[EventCovariates]:
    out = []
    for e in events:
        pre, post = e.pre_days(grid), e.post_days(grid)
        out.append(EventCovariates(
            t0=e.t0, calendar_month=e.calendar_month, year=e.year,
            values={c: signed_covariate(calendar.get(c, set()), pre, post)
                    for c in K.MACRO_COVARIATES}))
    return out


def design_matrix(covs: Sequence[EventCovariates]):
    """[1, CPI, NFP, FOMC, QRA] per event — the sealed §G.3 model's X."""
    import numpy as np
    rows = [[1.0] + [float(c.values[k]) for k in K.MACRO_COVARIATES] for c in covs]
    return np.asarray(rows, dtype=float)


def evaluability(covs: Sequence[EventCovariates]) -> Dict[str, object]:
    """The sealed NOT_EVALUABLE test — rank deficiency OR a reference group under 20."""
    import numpy as np
    X = design_matrix(covs)
    rank = int(np.linalg.matrix_rank(X)) if X.size else 0
    ref_n = sum(1 for c in covs if c.is_reference)
    reasons = []
    if rank < X.shape[1]:
        reasons.append(f"RANK_DEFICIENT (rank {rank} < {X.shape[1]} columns)")
    if ref_n < K.MACRO_MIN_REFERENCE_GROUP:
        reasons.append(f"REFERENCE_GROUP_TOO_SMALL ({ref_n} < "
                       f"{K.MACRO_MIN_REFERENCE_GROUP})")
    return {"n_events": len(covs), "design_matrix_rank": rank,
            "design_matrix_columns": int(X.shape[1]) if X.size else 0,
            "reference_group_n": ref_n,
            "min_reference_group": K.MACRO_MIN_REFERENCE_GROUP,
            "evaluable": not reasons, "not_evaluable_reasons": reasons}


def crosstab(covs: Sequence[EventCovariates]) -> Dict[str, object]:
    """PRE / POST / neither counts, combination counts, rank and reference group.

    Contains ZERO returns. This is the artefact the seal requires before any `AC` is
    computed.
    """
    per: Dict[str, Dict[str, int]] = {}
    for c in K.MACRO_COVARIATES:
        vals = Counter(x.values[c] for x in covs)
        per[c] = {"post_plus1": vals.get(1, 0), "neither_0": vals.get(0, 0),
                  "pre_minus1": vals.get(-1, 0)}
    combos = Counter(tuple(x.values[c] for c in K.MACRO_COVARIATES) for x in covs)
    out = {"per_covariate": per,
           "combinations": {",".join(str(v) for v in k): n
                            for k, n in sorted(combos.items(), key=lambda kv: -kv[1])},
           "distinct_combinations": len(combos)}
    out.update(evaluability(covs))
    return out


def write_covariates(covs: Sequence[EventCovariates],
                     path: str = COVARIATE_PATH) -> Dict[str, object]:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        w = csv.DictWriter(fh, fieldnames=COV_COLUMNS, lineterminator="\n")
        w.writeheader()
        for c in covs:
            row = {"t0": c.t0.isoformat(), "calendar_month": c.calendar_month,
                   "year": c.year}
            row.update({k.lower(): c.values[k] for k in K.MACRO_COVARIATES})
            w.writerow(row)
    return {"path": path, "rows": len(covs),
            "sha256": hashlib.sha256(open(path, "rb").read()).hexdigest()}


def load_covariates(path: str = COVARIATE_PATH) -> List[EventCovariates]:
    out = []
    with open(path, "r", encoding="utf-8", newline="") as fh:
        for rec in csv.DictReader(fh):
            out.append(EventCovariates(
                t0=_dt.date.fromisoformat(rec["t0"]),
                calendar_month=rec["calendar_month"], year=int(rec["year"]),
                values={c: int(rec[c.lower()]) for c in K.MACRO_COVARIATES}))
    return out
