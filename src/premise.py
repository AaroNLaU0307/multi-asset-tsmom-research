"""Phase 1B — DESCRIPTIVE premise test for the vol-compression breakout (strategy B).

The make-or-break question, characterized on this universe: after CLOSE-TO-CLOSE
volatility compresses (causal vol percentile <= threshold), does a *directional*
expansion follow — genuine breakouts that follow through — at a rate ABOVE the
unconditional base rate? Or does compression precede vol expansion that is mostly
non-directional (false breakouts / chop)?

This is descriptive only: NO positions, NO P&L, NO tuning. The conditioning variable
(compression) is strictly point-in-time; the outcome window is forward-looking BY
DESIGN (we are characterizing "what happens next"). Reuses the causal daily primitives
in ``src/daily.py``.

Scope of claim (data constraint): the data is adjusted-CLOSE-only (no intraday H/L), so
"compression" is close-to-close realized-vol percentile, NOT a true intraday ATR squeeze.
Conclusions do not generalize to an OHLC/ATR squeeze.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

import config
import universe
from . import daily

SLEEVE_OF: dict[str, str] = {t: g for g, ts in universe.GROUPS.items() for t in ts}
SLEEVES: list[str] = list(universe.GROUPS.keys())


def forward_stats(px: pd.DataFrame, horizon: int,
                  lookback: int = config.BREAKOUT_LOOKBACK) -> dict[str, pd.DataFrame]:
    """Forward-window (t, t+N] outcome panels aligned to day t.

    All forward quantities use shift(-N) (future data) — intended: this is a
    descriptive characterization of what follows compression, not a tradeable signal.
    """
    N = horizon
    close = px
    ret = close.pct_change()
    absdiff = close.diff().abs()

    end = close.shift(-N)                                   # close at t+N
    net = (end - close).abs()                               # |net move| over the window
    path = absdiff.rolling(N).sum().shift(-N)               # Σ|daily change| over (t, t+N]
    er = net / path.where(path > config.ER_FLOOR_DENOM)     # forward efficiency ratio
    fwd_ret = end / close - 1.0

    fwd_max = close.rolling(N).max().shift(-N)              # max close over (t, t+N]
    fwd_min = close.rolling(N).min().shift(-N)
    rh = daily.recent_high(px, lookback)                    # causal channel top (excl. today)
    rl = daily.recent_low(px, lookback)

    up_break = fwd_max > rh
    dn_break = fwd_min < rl
    breakout = up_break | dn_break
    up_ft = up_break & (end > rh)                           # broke up AND finished above channel
    dn_ft = dn_break & (end < rl)
    follow = up_ft | dn_ft                                  # genuine follow-through (not reversed)

    fwd_vol = ret.rolling(N).std(ddof=1).shift(-N) * np.sqrt(config.TRADING_DAYS_PER_YEAR)
    trail_vol = ret.rolling(N).std(ddof=1) * np.sqrt(config.TRADING_DAYS_PER_YEAR)
    expansion = fwd_vol / trail_vol.where(trail_vol > 0)    # forward vol / trailing vol

    valid = net.notna() & path.notna() & rh.notna() & rl.notna()
    return {
        "er": er, "fwd_ret": fwd_ret, "fwd_abs": fwd_ret.abs(),
        "breakout": breakout, "follow": follow, "expansion": expansion, "valid": valid,
    }


def _masked_mean(metric: pd.DataFrame, mask: pd.DataFrame, cols: list[str]) -> float:
    arr = metric[cols].where(mask[cols]).to_numpy()
    return float(np.nanmean(arr)) if np.isfinite(arr).any() else float("nan")


def _masked_rate(boolean: pd.DataFrame, mask: pd.DataFrame, cols: list[str]) -> tuple[float, int]:
    sub = boolean[cols].astype(float).where(mask[cols])   # bool->float so NaN masking is numeric
    arr = sub.to_numpy()
    n = int(np.isfinite(arr).sum())
    return (float(np.nansum(arr) / n) if n else float("nan"), n)


def premise_table(px: pd.DataFrame,
                  thresholds=(0.10, 0.20, 0.30),
                  horizons=config.PREMISE_HORIZONS,
                  lookback: int = config.BREAKOUT_LOOKBACK) -> pd.DataFrame:
    """Per-(scope, horizon, threshold) conditional-vs-base-rate directional stats.

    'comp' = conditioned on compression (vol pctile <= threshold); 'all' = unconditional
    base rate over the same valid cells. The decisive columns are the *deltas*:
    follow-through and efficiency ratio above base rate => compression carries directional
    information; <= 0 => it does not (premise fails)."""
    volp = daily.vol_percentile(px)
    scopes = [("Pooled", list(px.columns))] + [(s, universe.GROUPS[s]) for s in SLEEVES]
    rows = []
    for N in horizons:
        fs = forward_stats(px, N, lookback)
        valid = fs["valid"]
        for thr in thresholds:
            comp = (volp <= thr) & valid
            for scope, cols in scopes:
                brk_c, n_c = _masked_rate(fs["breakout"], comp, cols)
                brk_a, n_a = _masked_rate(fs["breakout"], valid, cols)
                ft_c, _ = _masked_rate(fs["follow"], comp, cols)     # genuine FT rate (incl. no-breakout=0)
                ft_a, _ = _masked_rate(fs["follow"], valid, cols)
                # follow-through GIVEN a breakout (quality: genuine vs false)
                ftg_c = (ft_c / brk_c) if brk_c and not np.isnan(brk_c) else np.nan
                ftg_a = (ft_a / brk_a) if brk_a and not np.isnan(brk_a) else np.nan
                er_c = _masked_mean(fs["er"], comp, cols)
                er_a = _masked_mean(fs["er"], valid, cols)
                exp_c = _masked_mean(fs["expansion"], comp, cols)
                exp_a = _masked_mean(fs["expansion"], valid, cols)
                abs_c = _masked_mean(fs["fwd_abs"], comp, cols)
                abs_a = _masked_mean(fs["fwd_abs"], valid, cols)
                rows.append({
                    "scope": scope, "horizon": N, "threshold": thr,
                    "n_comp": n_c, "n_all": n_a,
                    "breakout_rate_comp": brk_c, "breakout_rate_all": brk_a,
                    "genuine_ft_comp": ft_c, "genuine_ft_all": ft_a,
                    "genuine_ft_delta": ft_c - ft_a,
                    "ft_given_breakout_comp": ftg_c, "ft_given_breakout_all": ftg_a,
                    "ft_given_breakout_delta": ftg_c - ftg_a,
                    "ER_comp": er_c, "ER_all": er_a, "ER_delta": er_c - er_a,
                    "expansion_comp": exp_c, "expansion_all": exp_a,
                    "fwd_abs_comp": abs_c, "fwd_abs_all": abs_a,
                })
    return pd.DataFrame(rows)
