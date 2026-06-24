"""Tests for the volatility-scaling / position-sizing layer.

Priorities:
  1. Correctness of the inverse-vol sizing and the per-asset cap.
  2. NO LOOK-AHEAD — rolling vol is strictly backward-looking, and sized weights
     are truncation-invariant.

Run:  python -m pytest -q
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import sizing  # noqa: E402


def _synthetic_daily(seed: int = 7, years: int = 6, cols=("A", "B")) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2004-01-01", periods=years * 252)
    out = {}
    for c in cols:
        steps = rng.normal(0.0003, 0.01, size=len(idx))
        out[c] = 100.0 * np.exp(np.cumsum(steps))
    return pd.DataFrame(out, index=idx)


def _monthly(values: dict[str, list[float]]) -> pd.DataFrame:
    n = len(next(iter(values.values())))
    idx = pd.date_range("2010-01-31", periods=n, freq="ME")
    return pd.DataFrame(values, index=idx)


# --------------------------------------------------------------------------- #
# 1. Inverse-vol sizing + cap (pure target_weights)
# --------------------------------------------------------------------------- #
def test_inverse_vol_and_cap():
    # one month, four assets. target_vol=0.10, cap=2.0.
    signal = _monthly({"HV": [1.0], "MV": [1.0], "LV": [1.0], "FLAT": [0.0]})
    vol = _monthly({"HV": [0.50], "MV": [0.10], "LV": [0.02], "FLAT": [0.10]})
    w = sizing.target_weights(signal, vol, target_vol=0.10, max_weight=2.0)

    assert w["HV"].iloc[0] == 0.20          # 0.10/0.50
    assert w["MV"].iloc[0] == 1.00          # 0.10/0.10
    assert w["LV"].iloc[0] == 2.00          # 0.10/0.02 = 5.0 -> capped to 2.0
    assert w["FLAT"].iloc[0] == 0.0         # flat signal -> 0 weight
    # lower vol => larger position
    assert abs(w["MV"].iloc[0]) > abs(w["HV"].iloc[0])


def test_short_signal_sizing_and_sign():
    signal = _monthly({"X": [-1.0]})
    vol = _monthly({"X": [0.10]})
    w = sizing.target_weights(signal, vol, target_vol=0.10, max_weight=2.0)
    assert w["X"].iloc[0] == -1.0           # short, sized 1x


def test_missing_vol_gives_nan_weight():
    signal = _monthly({"X": [1.0, 1.0]})
    vol = _monthly({"X": [np.nan, 0.10]})
    w = sizing.target_weights(signal, vol, target_vol=0.10, max_weight=2.0)
    assert np.isnan(w["X"].iloc[0])         # no vol -> cannot size
    assert w["X"].iloc[1] == 1.0


# --------------------------------------------------------------------------- #
# 2. NO LOOK-AHEAD — rolling vol is backward-only
# --------------------------------------------------------------------------- #
def test_rolling_vol_uses_only_past_returns():
    daily = _synthetic_daily(cols=("A",))
    window = 20
    vol = sizing.rolling_volatility(daily, window=window, annualize=True)
    rets = daily["A"].pct_change()
    k = 100
    expected = rets.iloc[k - window + 1 : k + 1].std(ddof=1) * np.sqrt(252)
    assert np.isclose(vol["A"].iloc[k], expected)
    # before a full window exists, vol is NaN (no partial / no peeking)
    assert vol["A"].iloc[:window].isna().all()


# --------------------------------------------------------------------------- #
# 3. NO LOOK-AHEAD — truncation invariance of sized weights
# --------------------------------------------------------------------------- #
def test_weight_truncation_invariance():
    daily = _synthetic_daily()
    full = sizing.build_position_sizes(daily, method="B")["weight"]
    cut = full.index[40]
    trunc = sizing.build_position_sizes(daily.loc[:cut], method="B")["weight"]
    pd.testing.assert_frame_equal(full.loc[trunc.index], trunc)


def test_position_is_weight_shifted_one_month():
    daily = _synthetic_daily()
    out = sizing.build_position_sizes(daily, method="B")
    pd.testing.assert_frame_equal(out["position"], out["weight"].shift(1))
    assert out["position"].iloc[0].isna().all()
