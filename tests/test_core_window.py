"""The core runner is pinned to the published window and panel, and states its verdict
with the repo's status vocabulary.

* ``CORE_END_DATE`` truncation: a panel that runs past the published end (a fresh
  yfinance pull has no end date) is cut back before any signal is computed.
* ``CORE_PANEL_SHA256``: the cached panel is checked against the recorded pin; a
  mismatch warns by default and is fatal with ``--verify-panel``.
* ``verdict_label``: a CI above 0 is "SUPPORTED", never "confirmed".

Synthetic panels only — no market data is needed.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import config
import run_backtest
import universe
from src import fetch_data


def _synthetic_panel(end: str) -> pd.DataFrame:
    idx = pd.bdate_range("2025-01-02", end)
    rng = np.random.default_rng(0)
    cols = [*universe.TICKERS, "QQQ"]                       # an extra, non-core column
    return pd.DataFrame(100 * np.exp(np.cumsum(rng.normal(0, 0.01, (len(idx), len(cols))), 0)),
                        index=idx, columns=cols)


def test_core_end_date_is_the_published_panel_end():
    assert config.CORE_END_DATE == "2026-06-12"
    assert len(config.CORE_PANEL_SHA256) == 64


def test_truncate_to_end_keeps_the_end_day_and_drops_later_rows():
    px = _synthetic_panel("2026-09-25")
    out = fetch_data.truncate_to_end(px, "2026-06-12")
    assert out.index.max() == pd.Timestamp("2026-06-12")
    assert (out.index <= pd.Timestamp("2026-06-12")).all()
    pd.testing.assert_frame_equal(out, px.loc[:"2026-06-12"])


def test_check_file_sha256_match_warn_and_strict(tmp_path):
    f = tmp_path / "panel.csv"
    f.write_bytes(b"Date,SPY\n2026-06-12,1.0\n")
    pin = fetch_data.file_sha256(f)
    assert fetch_data.check_file_sha256(f, pin) is True
    assert fetch_data.check_file_sha256(f, "0" * 64) is False           # warn, not fatal
    with pytest.raises(ValueError):
        fetch_data.check_file_sha256(f, "0" * 64, strict=True)
    with pytest.raises(ValueError):
        fetch_data.check_file_sha256(tmp_path / "missing.csv", pin, strict=True)


def test_load_core_panel_truncates_a_longer_pull(tmp_path, monkeypatch):
    px = _synthetic_panel("2026-09-25")                     # runs past CORE_END_DATE
    cache = tmp_path / "close_prices_raw.csv"
    px.to_csv(cache)
    monkeypatch.setattr(config, "RAW_PRICES_CSV", cache)
    monkeypatch.setattr(fetch_data, "fetch_universe", lambda force=False: (px, []))
    out = run_backtest.load_core_panel()
    assert list(out.columns) == universe.TICKERS
    assert out.index.max() == pd.Timestamp(config.CORE_END_DATE)
    with pytest.raises(ValueError):                         # synthetic cache != the pin
        run_backtest.load_core_panel(verify_panel=True)


def test_verdict_label_uses_the_status_vocabulary():
    supported = run_backtest.verdict_label({"lo": 0.29, "hi": 1.23, "crosses_0": False})
    assert supported == "SUPPORTED — CI excludes 0; not independently confirmed"
    assert "CONFIRMED" not in supported.replace("not independently confirmed", "")
    assert run_backtest.verdict_label({"lo": -0.1, "hi": 0.9, "crosses_0": True}).startswith(
        "NOT SUPPORTED")
    assert run_backtest.verdict_label({"lo": -0.9, "hi": -0.1, "crosses_0": False}).startswith(
        "NEGATIVE")
