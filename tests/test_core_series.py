"""The core pipeline's committed return series matches the series the headline cites.

``output/monthly_returns.csv`` is written by ``run_backtest.py`` from the pinned panel;
``research/xsmom/xsmom_monthly_returns.csv`` column ``tsmom_net`` is written by
``run_xsmom.py`` from the same engine and is the series ``results/headline.json`` cites.
They must agree month for month. Both files are committed; no market data is needed.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def _read(rel: str) -> pd.DataFrame:
    return pd.read_csv(ROOT / rel, index_col=0, parse_dates=True)


def test_core_net_equals_the_cited_tsmom_net_month_for_month():
    core = _read("output/monthly_returns.csv")["net"]
    cited = _read("research/xsmom/xsmom_monthly_returns.csv")["tsmom_net"]
    assert core.index.equals(cited.index)
    diff = (core - cited).abs()
    assert (diff == 0).all(), diff[diff > 0]


def test_core_series_covers_the_published_window():
    core = _read("output/monthly_returns.csv")
    assert list(core.columns) == ["gross", "turnover", "cost", "net", "buy_hold"]
    assert core.index.min() == pd.Timestamp("2008-05-31")
    assert core.index.max() == pd.Timestamp("2026-06-30")
    assert core["net"].notna().all()
