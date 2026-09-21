"""CTA-EDGE-02-BENB — the end-to-end cell pipeline and the LQD secondary path.

Component O of the S2 build. One function runs a cell from source to intervals; the
PRIMARY (HYG) and the SECONDARY (LQD) use the identical code path with identical sealed
definitions — that is what "replication" means here.

`classify_primary()` takes the PRIMARY cell result and nothing else. The secondary
result is not a parameter, so LQD cannot reach the verdict even by mistake.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence

import numpy as np

import benb_contract as K
from benb_classify import Verdict, classify, evaluable
from benb_data import CellSource, Eligibility, eligibility
from benb_engine import (Observation, gate_one, month_grid, monthly_series,
                         observations)
from benb_feature import FeatureRow, discount_rows, features, premium_rows
from benb_inference import BootstrapResult, LoyoResult, leave_one_year_out, \
    year_block_bootstrap


@dataclass
class CellResult:
    ticker: str
    cell_role: str
    data_kind: str
    n_grid: int
    n_eligible: int
    n_discount: int
    n_premium: int
    years_with_discount: int
    month_grid: List[str]
    obs: List[Observation]
    gate1: object
    boot: Optional[BootstrapResult] = None
    loyo: Optional[LoyoResult] = None
    premium_descriptive: Dict[str, float] = field(default_factory=dict)
    defects: List[str] = field(default_factory=list)

    @property
    def var_d_positive(self) -> bool:
        ds = [o.d for o in self.obs]
        return len(ds) >= 2 and max(ds) > min(ds)


def run_cell(source: CellSource, ticker: str, cell_role: str,
             b: int = K.BOOTSTRAP_B,
             rng: np.random.Generator | None = None,
             run_bootstrap: bool = True) -> CellResult:
    """Source -> features -> eligibility -> discount sample -> decomposition ->
    Gate 1 -> fixed trade -> monthly P&L -> ONE bootstrap -> LOYO."""
    cell = source.load(ticker)
    cell.validate()
    rows = features(cell)
    elig = eligibility(cell)
    disc = discount_rows(rows, elig.eligible)
    prem = premium_rows(rows, elig.eligible)
    obs = observations(cell, rows, disc)

    months: List[str] = []
    if obs:
        ms = sorted(o.entry_month for o in obs)
        months = month_grid(ms[0], ms[-1])

    g = None
    defects: List[str] = []
    try:
        g = gate_one(obs) if len(obs) >= 2 else None
    except ValueError as exc:
        defects.append(f"gate_one: {exc}")

    res = CellResult(
        ticker=ticker, cell_role=cell_role, data_kind=cell.data_kind,
        n_grid=len(cell.grid), n_eligible=len(elig.eligible),
        n_discount=len(disc), n_premium=len(prem),
        years_with_discount=len({o.year for o in obs}),
        month_grid=months, obs=obs, gate1=g, defects=defects,
        # DESCRIPTIVE ONLY. Never an input to classification.
        premium_descriptive={"n_premium_eligible": float(len(prem))})

    if run_bootstrap and g is not None and res.years_with_discount >= 1:
        try:
            res.boot = year_block_bootstrap(obs, months, b=b, rng=rng)
            res.loyo = leave_one_year_out(obs)
        except ValueError as exc:
            defects.append(f"bootstrap: {exc}")
    return res


def classify_primary(primary: CellResult, hashes_ok: bool = True) -> Verdict:
    """The verdict. Takes the PRIMARY cell and nothing else.

    There is deliberately no `secondary` and no `premium` parameter: the LQD
    replication and the premium side cannot reach this function's inputs.
    """
    decomposition_ok = not any(d.startswith("identity") for d in primary.defects)
    ok = evaluable(hashes_ok=hashes_ok, decomposition_ok=decomposition_ok,
                   var_d_positive=primary.var_d_positive,
                   n_years_with_discount=primary.years_with_discount)
    if not ok or primary.boot is None or primary.loyo is None:
        return classify(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, False, is_evaluable=False)
    bt, bo, bn = primary.boot.beta_T, primary.boot.beta_O, primary.boot.beta_N
    mr, sh = primary.boot.mean_net, primary.boot.sharpe
    return classify(bt.lower, bt.upper, bo.lower, bo.upper, bn.lower, bn.upper,
                    mr.lower, mr.upper, sh.lower, sh.upper,
                    primary.loyo.passes, is_evaluable=True)


def secondary_summary(secondary: CellResult) -> Dict[str, object]:
    """LQD, reported alongside. PROMOTION_POWER = NONE. RESCUE_POWER = NONE."""
    out: Dict[str, object] = {
        "ticker": secondary.ticker,
        "n_discount": secondary.n_discount,
        "promotion_power": "NONE", "rescue_power": "NONE",
        "note": ("declared secondary replication; identical sealed definitions; "
                 "cannot rescue, promote or qualify the HYG verdict"),
    }
    if secondary.boot is not None:
        out["beta_T"] = secondary.boot.beta_T.as_dict()
    return out
