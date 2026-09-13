# -*- coding: utf-8 -*-
"""Value portfolio construction, reusing the existing programme machinery.

Sizing, caps, vol targeting and the gross cap come from `src/` rather than being
reimplemented; only the Value-specific aggregation and the frozen 75/25
combination live here.
"""
import os
import sys

import numpy as np

from value_contract import (SPLIT_TSMOM, SPLIT_VALUE, UNIVERSE)

_REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     "..", "..", ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

COST_BPS_PER_UNIT_TURNOVER = 2.0     # inherited from the ETF programme; not tuned
TARGET_VOL_ANNUAL = 0.10             # config.TARGET_VOL_ANNUAL
MAX_ASSET_WEIGHT = 2.0               # config.MAX_ASSET_WEIGHT
MAX_GROSS_LEVERAGE = 3.0             # config.MAX_GROSS_LEVERAGE


def inherited_config():
    """Read the programme's own knobs so this module cannot silently diverge."""
    import config
    return {"target_vol": float(config.TARGET_VOL_ANNUAL),
            "max_asset_weight": float(config.MAX_ASSET_WEIGHT),
            "max_gross": float(config.MAX_GROSS_LEVERAGE),
            "cost_bps": COST_BPS_PER_UNIT_TURNOVER}


def asset_weights(signals_at_t, vols_at_t, target_vol=TARGET_VOL_ANNUAL,
                  max_weight=MAX_ASSET_WEIGHT):
    """w_i = s_i * target_vol / vol_i, capped. Same form as src.sizing."""
    out = {}
    for inst in UNIVERSE:
        s = signals_at_t.get(inst, 0)
        v = vols_at_t.get(inst)
        if not s or v is None or not np.isfinite(v) or v <= 0:
            out[inst] = 0.0
            continue
        w = float(s) * target_vol / float(v)
        out[inst] = float(np.clip(w, -max_weight, max_weight))
    return out


def equal_risk_aggregate(weights):
    """The sealed low-DoF rule: equal risk weight across the five instruments.

    Each instrument is already scaled to the same target volatility, so equal
    risk weight is equal nominal weight on those scaled positions: divide by the
    universe size. Stale/zero instruments are NOT redistributed - their risk is
    simply absent, as §4.1 requires.
    """
    n = len(UNIVERSE)
    return {k: v / n for k, v in weights.items()}


def apply_gross_cap(weights, max_gross=MAX_GROSS_LEVERAGE):
    gross = sum(abs(v) for v in weights.values())
    if gross <= max_gross or gross == 0:
        return dict(weights), 1.0
    scale = max_gross / gross
    return {k: v * scale for k, v in weights.items()}, scale


def vol_target_leverage(realised_vol, target_vol=TARGET_VOL_ANNUAL,
                        max_gross=MAX_GROSS_LEVERAGE):
    if realised_vol is None or not np.isfinite(realised_vol) or realised_vol <= 0:
        return 0.0
    return float(min(target_vol / realised_vol, max_gross))


def turnover(prev_weights, new_weights):
    """Sum of absolute weight changes - the sealed turnover definition."""
    keys = set(prev_weights) | set(new_weights)
    return float(sum(abs(new_weights.get(k, 0.0) - prev_weights.get(k, 0.0))
                     for k in keys))


def cost_for(prev_weights, new_weights, cost_bps=COST_BPS_PER_UNIT_TURNOVER):
    """A signal change, a roll to zero on staleness and any other weight change
    are all charged identically."""
    return turnover(prev_weights, new_weights) * cost_bps / 10000.0


def combine(tsmom_returns, value_returns,
            w_tsmom=SPLIT_TSMOM, w_value=SPLIT_VALUE):
    """The single frozen 75/25 risk split. No grid, no optimiser, no reallocation."""
    t = np.asarray(tsmom_returns, dtype=float)
    v = np.asarray(value_returns, dtype=float)
    if t.shape != v.shape:
        raise ValueError("combination requires aligned paired series")
    if abs((w_tsmom + w_value) - 1.0) > 1e-12:
        raise ValueError("the frozen split must sum to one")
    return w_tsmom * t + w_value * v
