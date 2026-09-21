# -*- coding: utf-8 -*-
"""Canonical FORWARD engine — the sealed rule, with every convention explicit.

This reproduces the sealed canonical behaviour of `src/` exactly. It does NOT
modernise, clean up or "improve" the scientific rule: sealed §B.1 and §B.2
deliberately preserve two behaviours that a refactor would otherwise silently
change, and both are reproduced here on purpose and covered by tests.

The ONE deliberate difference from `src/` is that every convention that `src/`
obtains from a library default is written out explicitly, exactly as sealed §B.2
requires:

    "the forward engine must call `pct_change` with the fill behaviour written
     explicitly to reproduce the sealed behaviour, and the seal must pin the
     runtime. This is a specification-tightening that preserves behaviour
     exactly; it is NOT a rule change."

`simple_returns()` is therefore `ffill().pct_change(fill_method=None)`, which is
value-identical to the sealed runtime's `pct_change()` default of
`fill_method='pad'` and is stable across pandas 3.x. `ca_s2_tests.py` proves the
equivalence rather than asserting it.

Preserved sealed behaviours (§B.1), reproduced deliberately:
  * a flat composite (`signal == 0`) yields weight 0.0, which is NON-NaN, so the
    asset COUNTS in `n_available` and dilutes the book; where a flat signal and a
    missing volatility coincide the flat-signal override wins and the asset is in
    the book at zero;
  * NaN leverage propagates from either input, so a missing vol estimate yields no
    position rather than a cap-only value.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import ca_contract as K


# --------------------------------------------------------------------------- #
# Explicit primitives
# --------------------------------------------------------------------------- #
def simple_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """Explicit equivalent of the sealed `pct_change()` default (fill_method='pad')."""
    return prices.ffill().pct_change(fill_method=None)


def to_monthly(daily_prices: pd.DataFrame) -> pd.DataFrame:
    """Last available daily close within the calendar month, labelled at month-end."""
    return daily_prices.resample("ME").last()


def momentum_return(monthly: pd.DataFrame, n: int) -> pd.DataFrame:
    return monthly / monthly.shift(n) - 1.0


def composite_signal(monthly: pd.DataFrame) -> pd.DataFrame:
    """Sign each horizon first, then mean the four signs; all four required."""
    frames = [np.sign(momentum_return(monthly, n)) for n in K.MOMENTUM_LOOKBACKS_MONTHS]
    arr = np.stack([f.to_numpy(dtype=float) for f in frames], axis=0)
    valid = ~np.isnan(arr)
    count = valid.sum(axis=0)
    summ = np.nansum(arr, axis=0)
    with np.errstate(invalid="ignore", divide="ignore"):
        mean = summ / np.where(count == 0, np.nan, count)
    score = np.where(count >= K.MOMENTUM_MIN_PERIODS, mean, np.nan)
    return pd.DataFrame(score, index=monthly.index, columns=monthly.columns)


def asset_volatility(daily_prices: pd.DataFrame) -> pd.DataFrame:
    rets = simple_returns(daily_prices)
    vol = rets.rolling(window=K.VOL_WINDOW_DAYS, min_periods=K.VOL_WINDOW_DAYS).std(ddof=1)
    return (vol * np.sqrt(K.TRADING_DAYS_PER_YEAR)).resample("ME").last()


def asset_weights(signal: pd.DataFrame, vol: pd.DataFrame) -> pd.DataFrame:
    v = vol.reindex(index=signal.index, columns=signal.columns)
    scalar = K.TARGET_VOL_ANNUAL / v.where(v > 0)
    raw = signal * scalar
    capped = raw.clip(lower=-K.MAX_ASSET_WEIGHT, upper=K.MAX_ASSET_WEIGHT)
    # SEALED §B.1: a flat signal is a deliberate 0 position regardless of vol, and
    # this override runs AFTER the vol-derived NaN. Preserved exactly.
    return capped.where(signal != 0, 0.0)


def equal_weight_aggregate(w: pd.DataFrame):
    avail = w.notna().sum(axis=1)
    base = w.fillna(0.0).div(avail.where(avail > 0), axis=0)
    return base, avail


def base_book_daily_returns(base: pd.DataFrame, daily_prices: pd.DataFrame) -> pd.Series:
    rets = simple_returns(daily_prices)
    held = base.reindex(rets.index, method="ffill").shift(1)
    return (held * rets).sum(axis=1, min_count=1)


def portfolio_volatility(base_daily: pd.Series) -> pd.Series:
    v = base_daily.rolling(K.PORT_VOL_WINDOW_DAYS, min_periods=K.PORT_VOL_WINDOW_DAYS).std(ddof=1)
    return (v * np.sqrt(K.TRADING_DAYS_PER_YEAR)).resample("ME").last()


def leverage(port_vol: pd.Series, gross_base: pd.Series):
    l_raw = K.PORT_TARGET_VOL_ANNUAL / port_vol.where(port_vol > 0)
    l_cap = K.MAX_GROSS_LEVERAGE / gross_base.where(gross_base > 0)
    # skipna=False so NaN in EITHER input propagates (sealed §B; warm-up -> NaN).
    L = pd.concat([l_raw, l_cap], axis=1).min(axis=1, skipna=False)
    return L, l_raw, (l_raw > l_cap).fillna(False)


def build_book(daily_prices: pd.DataFrame) -> dict:
    """daily prices -> decision weights and held positions. NO returns are computed."""
    monthly = to_monthly(daily_prices)
    sig = composite_signal(monthly)
    vol = asset_volatility(daily_prices)
    w = asset_weights(sig, vol)
    base, avail = equal_weight_aggregate(w)
    gross_base = base.abs().sum(axis=1)
    pvol = portfolio_volatility(base_book_daily_returns(base, daily_prices)).reindex(base.index)
    L, l_raw, cap_binds = leverage(pvol, gross_base)
    port_w = base.mul(L, axis=0)
    return {
        "monthly_prices": monthly, "signal": sig, "asset_vol": vol, "asset_weight": w,
        "base_weight": base, "n_available": avail, "gross_base": gross_base,
        "port_vol": pvol, "leverage": L, "leverage_raw": l_raw, "cap_binds": cap_binds,
        "port_weight": port_w,                       # weight decided AT month-end
        "position": port_w.shift(1),                 # position HELD during the month
        "gross": port_w.abs().sum(axis=1),
        "net": port_w.sum(axis=1),
    }


def decision_vector(daily_prices: pd.DataFrame, decision_month_end: pd.Timestamp) -> dict:
    """The sealed decision for the month FOLLOWING `decision_month_end`.

    Computed from the supplied snapshot alone. Returns the decision weight vector
    and the mechanical invariants — never a return, never a performance quantity.
    """
    book = build_book(daily_prices)
    d = pd.Timestamp(decision_month_end)
    if d not in book["port_weight"].index:
        raise KeyError("decision month-end %s not present in the snapshot" % d.date())
    w = book["port_weight"].loc[d]
    return {
        "decision_month_end": str(d.date()),
        "weights": {k: (None if pd.isna(v) else float(v)) for k, v in w.items()},
        "gross": None if pd.isna(book["gross"].loc[d]) else float(book["gross"].loc[d]),
        "net": None if pd.isna(book["net"].loc[d]) else float(book["net"].loc[d]),
        "leverage": None if pd.isna(book["leverage"].loc[d]) else float(book["leverage"].loc[d]),
        "n_available": int(book["n_available"].loc[d]),
        "cap_binds": bool(book["cap_binds"].loc[d]),
    }


# --------------------------------------------------------------------------- #
# Mechanical invariants (§T.2 — booleans, never the vector)
# --------------------------------------------------------------------------- #
def invariants(decision: dict) -> dict:
    w = [v for v in decision["weights"].values() if v is not None]
    return {
        "gross_within_cap": (decision["gross"] is None) or (decision["gross"] <= K.MAX_GROSS_LEVERAGE + 1e-9),
        "asset_weight_within_cap": all(abs(x) <= K.MAX_GROSS_LEVERAGE + 1e-9 for x in w),
        "all_17_present": len(decision["weights"]) == len(K.CANONICAL_17),
        "n_available": decision["n_available"],
    }


def turnover(current: dict, prior: dict | None) -> float:
    """Sealed one-way turnover. `prior` may be the pre-start held position (§F.1 step 2)."""
    if prior is None:
        return float("nan")
    tot = 0.0
    for t in K.CANONICAL_17:
        a, b = current["weights"].get(t), prior["weights"].get(t)
        if a is None or b is None:
            return float("nan")
        tot += abs(a - b)
    return tot
