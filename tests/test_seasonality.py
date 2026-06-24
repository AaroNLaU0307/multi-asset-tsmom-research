"""Tests for the seasonality premise primitives (strategy C, Step 1).

Fragile pieces, tested on constructed calendars with asserted outcomes:
  * day-labellers (turn-of-month, winter/summer, week-start incl. holiday Monday);
  * truncation-invariance of the causal components;
  * the HAC difference-in-means slope identity and the BH-FDR procedure;
  * E2 per-year spread + year-level jackknife on a known series.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from src import seasonality as seas


# --------------------------------------------------------------------------- #
# Day labellers
# --------------------------------------------------------------------------- #
def test_is_tom_asserted_days():
    idx = pd.bdate_range("2020-01-01", "2020-03-31")
    tom = seas.is_tom(idx)
    # first 3 trading days of January (Jan 1 is a Wed; bdate_range has no holidays)
    for d in ("2020-01-01", "2020-01-02", "2020-01-03"):
        assert tom[pd.Timestamp(d)]
    assert not tom[pd.Timestamp("2020-01-06")]        # 4th trading day -> not TOM
    assert tom[pd.Timestamp("2020-01-31")]            # last trading day of Jan
    assert not tom[pd.Timestamp("2020-01-15")]        # mid-month
    # turn into February: last of Jan already True; first 3 of Feb (Feb 1 = Sat)
    for d in ("2020-02-03", "2020-02-04", "2020-02-05"):
        assert tom[pd.Timestamp(d)]
    assert not tom[pd.Timestamp("2020-02-06")]
    assert tom[pd.Timestamp("2020-02-28")]            # last trading day of Feb


def test_is_winter_asserted_months():
    idx = pd.to_datetime(["2020-01-15", "2020-04-15", "2020-05-15",
                          "2020-07-15", "2020-10-15", "2020-11-15", "2020-12-15"])
    w = seas.is_winter(idx)
    assert list(w.to_numpy()) == [True, True, False, False, False, True, True]


def test_is_week_start_handles_holiday_monday():
    # A normal week: Monday is the week-start.
    idx = pd.bdate_range("2020-01-06", "2020-01-10")   # Mon..Fri
    ws = seas.is_week_start(idx)
    assert ws[pd.Timestamp("2020-01-06")]              # Monday
    assert not ws[pd.Timestamp("2020-01-07")]          # Tuesday
    # Holiday Monday dropped -> Tuesday becomes the first trading day of the week.
    idx2 = pd.DatetimeIndex(["2020-01-07", "2020-01-08", "2020-01-09", "2020-01-10"])
    ws2 = seas.is_week_start(idx2)
    assert ws2[pd.Timestamp("2020-01-07")]             # Tuesday is now week-start
    assert not ws2[pd.Timestamp("2020-01-08")]


# --------------------------------------------------------------------------- #
# Truncation-invariance (no look-ahead) of the causal components
# --------------------------------------------------------------------------- #
def test_truncation_invariance_winter_and_weekstart():
    idx = pd.bdate_range("2018-01-01", "2020-12-31")
    cut = idx[int(len(idx) * 0.6)]
    for fn in (seas.is_winter, seas.is_week_start):
        full = fn(idx)
        trunc = fn(idx[idx <= cut])
        common = trunc.index
        assert (full.loc[common].to_numpy() == trunc.to_numpy()).all()


def test_truncation_invariance_tom_complete_months():
    # is_tom is stable on complete months; cut at a month-end so the prefix has no
    # partial trailing month (the 'last trading day' component needs the month closed).
    idx = pd.bdate_range("2018-01-01", "2020-12-31")
    cut = pd.Timestamp("2019-06-28")                   # last business day of Jun 2019
    full = seas.is_tom(idx)
    trunc = seas.is_tom(idx[idx <= cut])
    common = trunc.index
    assert (full.loc[common].to_numpy() == trunc.to_numpy()).all()


# --------------------------------------------------------------------------- #
# HAC difference-in-means slope identity
# --------------------------------------------------------------------------- #
def test_hac_slope_equals_mean_difference():
    rng = np.random.default_rng(0)
    n = 600
    d = (np.arange(n) % 5 == 0).astype(float)          # ~20% effect-days
    # Strong signal vs noise so the realized sign is reliable (the identity below is
    # exact regardless; the sign/finiteness checks need signal >> sampling noise).
    y = 0.005 * d + rng.normal(0, 0.005, n)            # true +50 bps on effect-days
    res = seas.hac_diff_test(y, d, lag=10)
    manual = y[d == 1].mean() - y[d == 0].mean()
    assert abs(res["delta"] - manual) < 1e-12          # slope on dummy == mean diff
    assert res["delta"] > 0 and np.isfinite(res["t"])
    assert res["t"] > 0                                # positive effect -> positive t
    assert 0.0 <= res["p"] <= 1.0
    assert res["n_eff"] + res["n_non"] == n


# --------------------------------------------------------------------------- #
# Benjamini-Hochberg FDR
# --------------------------------------------------------------------------- #
def test_bh_fdr_all_reject():
    p = np.array([0.01, 0.02, 0.03, 0.04, 0.05])
    p_adj, reject = seas.bh_fdr(p, q=0.05)
    assert reject.all()
    assert np.allclose(p_adj, 0.05)


def test_bh_fdr_only_smallest():
    p = np.array([0.001, 0.4, 0.5, 0.6, 0.7])
    p_adj, reject = seas.bh_fdr(p, q=0.05)
    assert list(reject) == [True, False, False, False, False]
    assert abs(p_adj[0] - 0.005) < 1e-9
    assert (p_adj[1:] >= 0.5).all()


def test_bh_fdr_monotone_and_bounded():
    rng = np.random.default_rng(1)
    p = rng.uniform(0, 1, 18)
    p_adj, _ = seas.bh_fdr(p, q=0.10)
    assert (p_adj <= 1.0).all() and (p_adj >= 0.0).all()
    # adjusted p-values are monotone in the raw ranking
    order = np.argsort(p)
    assert np.all(np.diff(p_adj[order]) >= -1e-12)


# --------------------------------------------------------------------------- #
# E2 year-level robustness on a known series
# --------------------------------------------------------------------------- #
def test_e2_per_year_and_jackknife_known():
    idx = pd.bdate_range("2010-01-01", "2012-12-31")
    win = idx.month.isin(seas.config.SEAS_WINTER_MONTHS)
    r = np.where(win, 0.002, 0.0)                      # winter +20 bps, summer 0
    s = pd.Series(r, index=idx)
    py = seas.e2_per_year(s)
    assert list(py.index) == [2010, 2011, 2012]
    assert np.allclose(py["spread_bps"].to_numpy(), 20.0)   # (0.002-0.0)*1e4
    jk = seas.e2_year_jackknife(s)
    assert abs(jk["full_bps"] - 20.0) < 1e-9
    assert abs(jk["loo_min_bps"] - 20.0) < 1e-9 and abs(jk["loo_max_bps"] - 20.0) < 1e-9
