# -*- coding: utf-8 -*-
"""TSMOM-VRP-01 - module F: the cost engine (sealed section G).

    cost_points(i,t)  = max( c0 , normalized_contemporaneous_minimum_tick(i,t) )
    c0 = 0.10         TOTAL spread + slippage together. No further half-spread is added
                      anywhere, by anything, ever.
    normalized tick   = tick_quoted(i,t) * M_quoted(i,t) / $1,000
    cost_dollars(i,t) = cost_points(i,t) * M_i * |dq_i,t|  +  $4.00 * |dq_i,t| * (M_i/1000)
                        where $4.00 = $2.00 commission + $2.00 exchange/clearing per
                        standard-contract-side, pro-rated by fractional quantity and by
                        the mini multiplier
    funding charge    = NONE. The primary is excess-of-cash; margin is funded from K;
                        no borrowing exists in this object.

The `c0 = 0.05` variant is DESCRIPTIVE ONLY (R12, PROMOTION_POWER = NONE). It is
reachable exclusively through `descriptive_cost_dollars`, which refuses to be called
from the primary path: `PRIMARY_C0` is a module constant that the primary functions
read directly and no argument can override.
"""
from __future__ import annotations

import datetime as _dt
from typing import Optional

import vrp_specs as vspecs
from vrp_constants import (COMMON_BASIS_MULTIPLIER, STANDARD_MULTIPLIER, c0,
                           c0_descriptive, commission, fee)

PRIMARY_C0 = c0                       # 0.10 - the only value the primary path may use
DESCRIPTIVE_C0 = c0_descriptive       # 0.05 - R12 only
DOLLAR_CONSTANTS_PER_STANDARD_SIDE = commission + fee   # $2.00 + $2.00


class PrimaryCostViolation(RuntimeError):
    """Raised when anything tries to run a non-sealed c0 through the primary path."""


def cost_points(d: _dt.date, floor: Optional[float] = None) -> float:
    """max(c0, tick_comparable(d)) comparable VIX points per contract-side."""
    if floor is None:
        floor = PRIMARY_C0
    return max(floor, vspecs.tick_comparable(d))


def cost_dollars(d: _dt.date, dq: float, multiplier: float = STANDARD_MULTIPLIER) -> float:
    """The sealed section G cost of trading |dq| contracts of one contract on date `d`.

    `multiplier` is the contract's economic $ per COMPARABLE point ($1,000 standard,
    $100 mini). The primary path never passes a floor; `PRIMARY_C0` is used.
    """
    q = abs(float(dq))
    if q == 0.0:
        return 0.0
    pts = cost_points(d)
    if pts < PRIMARY_C0:
        raise PrimaryCostViolation(
            "primary cost_points fell below the sealed c0 = %.2f on %s" % (PRIMARY_C0, d))
    slippage = pts * multiplier * q
    fixed = DOLLAR_CONSTANTS_PER_STANDARD_SIDE * q * (multiplier / COMMON_BASIS_MULTIPLIER)
    return slippage + fixed


def descriptive_cost_dollars(d: _dt.date, dq: float,
                             multiplier: float = STANDARD_MULTIPLIER) -> float:
    """R12 ONLY: the c0 = 0.05 sensitivity. PROMOTION_POWER = NONE.

    Never called by `vrp_stage_a` or `vrp_stage_b` on the primary path;
    `vrp_validators.check_descriptive_cost_isolation` proves the primary modules do not
    reference this function at all.
    """
    q = abs(float(dq))
    if q == 0.0:
        return 0.0
    pts = max(DESCRIPTIVE_C0, vspecs.tick_comparable(d))
    slippage = pts * multiplier * q
    fixed = DOLLAR_CONSTANTS_PER_STANDARD_SIDE * q * (multiplier / COMMON_BASIS_MULTIPLIER)
    return slippage + fixed


def funding_charge(*_args, **_kwargs) -> float:
    """Section G: NONE. Present so that any code reaching for a funding charge gets zero
    and so that a sabotage test can prove no funding charge ever enters a ledger."""
    return 0.0
