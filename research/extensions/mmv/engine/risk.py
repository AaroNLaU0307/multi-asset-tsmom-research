"""Integration with the CANONICAL portfolio risk wrapper — contract section F.

    Adopted unchanged from the canonical implementation. Canonical TSMOM itself
    is a frozen research benchmark and is not modified by this lineage in any
    way.

So this module CALLS `src.sizing` and `src.portfolio`; it does not reimplement
them, and it does not clone-and-mutate them. Every parameter below is read from
`config.py` at call time rather than copied, so a divergence between the
contract and the canonical book becomes an error here instead of a silent
difference between two hard-coded numbers.

The one thing this module must get right that the canonical path never had to
think about: MMV's alpha domain is 15 instruments, not 17. See `signal_frame`.
"""

from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "..", "..", ".."))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import config                                          # noqa: E402
from src import portfolio as canonical_portfolio       # noqa: E402
from src import sizing as canonical_sizing             # noqa: E402

from .pit import UNDEFINED, ContractViolation          # noqa: E402
from .votes import MAPPED, NOT_MAPPED, assert_domain   # noqa: E402

#: Contract section G / MMV-OD-5, traced to config.py:196.
ONE_WAY_COST_BPS = config.TRANSACTION_COST_BPS


def signal_frame(raw: dict, dates=None) -> pd.DataFrame:
    """Build the MMV signal frame: exactly 15 columns, UNDEFINED -> NaN.

    ``raw`` is ``{(date, instrument): sign_or_UNDEFINED}``.

    Two failure modes this guards, both of which would corrupt the result in
    MMV's favour or against it without raising anything:

    * VNQ/RWX present as ZERO columns would inject mechanical Gate 0.5
      disagreement every month the canonical composite is non-zero, pushing
      pooled agreement down — the direction that helps MMV survive the kill.
    * VNQ/RWX present as NaN columns would be excluded from Gate 0.5 correctly
      but would still sit in the frame handed to the risk wrapper, where
      `equal_weight_aggregate` counts columns that are NOT NaN. A NaN column
      is excluded there too, so the immediate harm is nil — but the column has
      no business existing, and a later `fillna(0)` anywhere upstream would
      turn it into the first failure mode silently.

    The contract's answer to both is that VNQ/RWX are ABSENT. This function
    enforces absence rather than trusting it.
    """
    instruments = {i for _d, i in raw}
    assert_domain(instruments)
    idx = sorted({d for d, _i in raw}) if dates is None else list(dates)
    cols = sorted(MAPPED)
    frame = pd.DataFrame(np.nan, index=pd.DatetimeIndex(idx), columns=cols,
                         dtype="float64")
    for (d, i), v in raw.items():
        if v is UNDEFINED:
            continue                       # stays NaN: UNDEFINED, never zero
        frame.loc[pd.Timestamp(d), i] = float(v)
    return frame


def assert_no_dilution(signal: pd.DataFrame) -> None:
    """The 15-vs-17 check the contract's section E.2 exists to prevent.

    `src.portfolio.equal_weight_aggregate` divides each asset's weight by the
    number of assets carrying a NON-NaN weight that month. A flat MMV cell is a
    real position and correctly counts as live. An unmapped real-estate column
    carrying 0.0 would ALSO count as live, shrinking every live MMV weight by
    15/17 for no reason connected to macro information.
    """
    present = set(signal.columns)
    if present & NOT_MAPPED:
        raise ContractViolation(
            "unmapped real estate in the MMV signal frame: %s. VNQ/RWX are "
            "outside the MMV alpha domain; they are not live flat signals."
            % sorted(present & NOT_MAPPED))
    if present != MAPPED:
        raise ContractViolation(
            "MMV signal frame must carry exactly the 15 mapped instruments; "
            "got %d columns" % len(present))


def build(daily_prices: pd.DataFrame, signal: pd.DataFrame) -> dict:
    """Run the sealed directions through the canonical wrapper, unchanged.

    Returns the canonical panel dict plus MMV-specific bookkeeping. Every step
    is a canonical function call:

        asset vol      src.sizing.volatility_at_month_end   60d, annualized
        asset weight   src.sizing.target_weights            10% target, +/-2 cap
        book           src.portfolio.equal_weight_aggregate  equal weight
        portfolio vol  src.portfolio.realized_portfolio_vol
        leverage       src.portfolio.leverage                10% target, 3x cap
        held position  src.portfolio.positions_from_weights  shift(1)
    """
    assert_no_dilution(signal)
    prices = daily_prices[sorted(MAPPED)]

    vol = canonical_sizing.volatility_at_month_end(
        prices, window=config.VOL_WINDOW_DAYS)
    asset_w = canonical_sizing.target_weights(
        signal, vol,
        target_vol=config.TARGET_VOL_ANNUAL,
        max_weight=config.MAX_ASSET_WEIGHT)

    base, n_live = canonical_portfolio.equal_weight_aggregate(asset_w)
    gross_base = base.abs().sum(axis=1)

    base_rets = canonical_portfolio.base_portfolio_daily_returns(base, prices)
    port_vol = canonical_portfolio.realized_portfolio_vol(
        base_rets, window=config.PORT_VOL_WINDOW_DAYS).reindex(base.index)

    L, l_raw, cap_binds = canonical_portfolio.leverage(
        port_vol, gross_base,
        target_vol=config.PORT_TARGET_VOL_ANNUAL,
        max_gross=config.MAX_GROSS_LEVERAGE)
    port_w = canonical_portfolio.portfolio_weights(base, L)
    held = canonical_portfolio.positions_from_weights(port_w)

    return {
        "signal": signal,
        "asset_vol": vol,
        "asset_weight": asset_w,
        "base_weight": base,
        "n_live": n_live,
        "gross_base": gross_base,
        "port_vol": port_vol,
        "leverage": L,
        "leverage_raw": l_raw,
        "cap_binds": cap_binds,
        "port_weight": port_w,
        "position": held,
        "turnover": turnover(port_w),
    }


def turnover(port_weights: pd.DataFrame) -> pd.Series:
    """Sum of absolute weight changes between consecutive decision dates."""
    return port_weights.fillna(0.0).diff().abs().sum(axis=1)


def cost_series(port_weights: pd.DataFrame,
                one_way_bps: float = ONE_WAY_COST_BPS) -> pd.Series:
    """Monthly transaction cost = one-way cost x turnover, contract section G."""
    return turnover(port_weights) * (one_way_bps / 1e4)


#: The canonical parameters this module is required to reproduce, for the
#: validator to check against config.py rather than against a second copy.
WRAPPER_AUTHORITY = {
    "VOL_WINDOW_DAYS": 60,
    "TARGET_VOL_ANNUAL": 0.10,
    "MAX_ASSET_WEIGHT": 2.0,
    "PORT_TARGET_VOL_ANNUAL": 0.10,
    "MAX_GROSS_LEVERAGE": 3.0,
    "TRANSACTION_COST_BPS": 2.0,
}
