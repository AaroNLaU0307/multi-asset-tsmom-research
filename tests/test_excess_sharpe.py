"""The T-bill sensitivity (run_excess_sharpe.py) recomputes from the committed series.

``output/excess_return_sensitivity.csv`` must equal what ``run_excess_sharpe.excess_series``
builds from the committed ``output/monthly_returns.csv`` and ``data/DGS3MO.csv``; the rf
rule is ``ca_rf``'s (last print on or before the prior month-end, at most 7 calendar days
old, Y/100/12), and the rf = 0 headline series is untouched. No market data is needed.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import run_excess_sharpe  # noqa: E402


def _committed() -> pd.DataFrame:
    return pd.read_csv(ROOT / "output/excess_return_sensitivity.csv", index_col=0, parse_dates=True)


def test_committed_table_recomputes_from_the_committed_series():
    rebuilt = run_excess_sharpe.excess_series()
    committed = _committed()
    assert list(rebuilt.index) == list(committed.index)
    for col in ("net", "rf_annual_pct", "rf_t", "excess"):
        assert ((rebuilt[col] - committed[col]).abs() < 1e-15).all(), col
    for col in ("rf_decision_date", "rf_observation_date"):
        assert list(rebuilt[col]) == list(committed[col]), col


def test_definition_is_net_minus_rf_on_the_whole_book():
    t = _committed()
    core = pd.read_csv(ROOT / "output/monthly_returns.csv", index_col=0, parse_dates=True)["net"]
    pd.testing.assert_series_equal(t["net"], core, check_names=False)
    assert ((t["excess"] - (t["net"] - t["rf_annual_pct"] / 100 / 12)).abs() < 1e-15).all()
    decision = t.index - pd.offsets.MonthEnd(1)
    assert list(pd.to_datetime(t["rf_decision_date"])) == list(decision)
    age = (pd.to_datetime(t["rf_decision_date"]) - pd.to_datetime(t["rf_observation_date"])).dt.days
    assert ((age >= 0) & (age <= 7)).all()

