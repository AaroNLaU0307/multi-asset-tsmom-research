"""Tests for the causal yield-curve primitives (src/yields.py).

The signal path (align -> slope -> trailing percentile -> tercile state, used at t-1)
must be strictly causal / truncation-invariant: recomputing on a prefix [0..i] must
reproduce the full-series history exactly. Forward-fill alignment must never pull a
future value backward. Constructed/synthetic series with asserted outcomes, per the
repo's testing convention.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from src import yields as Y


def _bdays(n: int, start: str = "2005-01-03") -> pd.DatetimeIndex:
    return pd.bdate_range(start, periods=n)


# --------------------------------------------------------------------------- #
# Causal alignment (past-only ffill)
# --------------------------------------------------------------------------- #
def test_align_to_calendar_is_past_only_ffill():
    # yields observed on d0 and d2 only; calendar has d0..d3.
    cal = _bdays(4)
    ydf = pd.DataFrame({"DGS10": [4.0, np.nan, 5.0, np.nan]}, index=cal)
    ydf = ydf.dropna()  # only d0, d2 are "published"
    aligned = Y.align_to_calendar(ydf, cal)["DGS10"]
    assert aligned.loc[cal[0]] == 4.0
    assert aligned.loc[cal[1]] == 4.0           # d1 carries d0 forward (NOT d2)
    assert aligned.loc[cal[2]] == 5.0
    assert aligned.loc[cal[3]] == 5.0           # d3 carries d2 forward


def test_align_never_backfills_a_future_value():
    cal = _bdays(5)
    # first publication is at d2; d0/d1 have no PAST value -> must stay NaN, not 9.0
    ydf = pd.DataFrame({"DGS10": [9.0, 9.5, 10.0]}, index=cal[2:])
    aligned = Y.align_to_calendar(ydf, cal)["DGS10"]
    assert aligned.loc[cal[0]] != aligned.loc[cal[0]]   # NaN
    assert aligned.loc[cal[1]] != aligned.loc[cal[1]]   # NaN
    assert aligned.loc[cal[2]] == 9.0


# --------------------------------------------------------------------------- #
# Truncation invariance of the state path
# --------------------------------------------------------------------------- #
def _series_equal_on_overlap(a: pd.Series, b: pd.Series) -> bool:
    common = a.index.intersection(b.index)
    aa, bb = a.loc[common], b.loc[common]
    both_nan = aa.isna() & bb.isna()
    close = np.isclose(aa.to_numpy(dtype=float), bb.to_numpy(dtype=float), equal_nan=False)
    return bool((both_nan | close).all())


def test_trailing_pctile_truncation_invariant():
    rng = np.random.default_rng(7)
    idx = _bdays(900)
    s = pd.Series(np.cumsum(rng.normal(size=900)) * 0.01 + 1.5, index=idx)
    full = Y.trailing_pctile(s, window=60)
    for cut in (300, 500, 750):
        pref = Y.trailing_pctile(s.iloc[:cut], window=60)
        assert _series_equal_on_overlap(full.iloc[:cut], pref)


def test_slope_then_state_truncation_invariant():
    rng = np.random.default_rng(11)
    idx = _bdays(800)
    aligned = pd.DataFrame(
        {
            "DGS10": 4.0 + np.cumsum(rng.normal(size=800)) * 0.01,
            "DGS3MO": 3.5 + np.cumsum(rng.normal(size=800)) * 0.01,
        },
        index=idx,
    )
    full_state = Y.tercile_state(Y.trailing_pctile(Y.slope(aligned, "DGS10", "DGS3MO"), window=120))
    for cut in (400, 600):
        pref_state = Y.tercile_state(
            Y.trailing_pctile(Y.slope(aligned.iloc[:cut], "DGS10", "DGS3MO"), window=120)
        )
        common = full_state.index[:cut]
        # object dtype: compare label-by-label, NaN==NaN treated equal
        a, b = full_state.loc[common], pref_state.loc[common]
        assert all((x == y) or (pd.isna(x) and pd.isna(y)) for x, y in zip(a, b))


# --------------------------------------------------------------------------- #
# Tercile buckets + raw inversion
# --------------------------------------------------------------------------- #
def test_tercile_state_buckets_and_boundaries():
    pr = pd.Series([0.0, 1 / 3, 0.5, 2 / 3, 1.0, np.nan], index=_bdays(6))
    st = Y.tercile_state(pr, lo=1 / 3, hi=2 / 3)
    assert st.iloc[0] == "flat"
    assert st.iloc[1] == "flat"      # boundary <= lo
    assert st.iloc[2] == "mid"
    assert st.iloc[3] == "steep"     # boundary >= hi
    assert st.iloc[4] == "steep"
    assert pd.isna(st.iloc[5])       # undefined percentile


def test_inversion_state_uses_zero_threshold():
    sl = pd.Series([-0.5, 0.0, 0.3, np.nan], index=_bdays(4))
    st = Y.inversion_state(sl)
    assert st.iloc[0] == "flat"      # inverted (<0)
    assert st.iloc[1] == "steep"     # 0 is not inverted
    assert st.iloc[2] == "steep"
    assert pd.isna(st.iloc[3])


# --------------------------------------------------------------------------- #
# Outcome helpers
# --------------------------------------------------------------------------- #
def test_forward_cum_return_matches_manual_and_has_no_lookahead_tail():
    idx = _bdays(6)
    r = pd.Series([0.01, -0.02, 0.03, 0.00, 0.05, -0.01], index=idx)
    fwd = Y.forward_cum_return(r, h=2)
    # at t0: (1.01*0.98)-1
    assert np.isclose(fwd.iloc[0], (1.01 * 0.98) - 1.0)
    # at t1: (0.98*1.03)-1
    assert np.isclose(fwd.iloc[1], (0.98 * 1.03) - 1.0)
    # last day has no full forward window -> NaN (no peeking past the end)
    assert pd.isna(fwd.iloc[-1])


def test_runs_to_episodes_merges_short_gaps():
    idx = _bdays(20)
    mask = pd.Series(False, index=idx)
    mask.iloc[2:5] = True            # run A (3 days)
    mask.iloc[7:9] = True            # run B (2 days), gap of 2 days from A
    mask.iloc[15:17] = True          # run C (2 days), gap of 6 days from B
    eps = Y.runs_to_episodes(mask, bridge=3)
    # A and B merge (gap 2 <= 3); C stays separate (gap 6 > 3)
    assert len(eps) == 2
    assert eps[0]["start"] == idx[2] and eps[0]["end"] == idx[8]
    assert eps[1]["start"] == idx[15] and eps[1]["end"] == idx[16]
    # with bridge=0, no merging -> 3 episodes
    assert len(Y.runs_to_episodes(mask, bridge=0)) == 3
