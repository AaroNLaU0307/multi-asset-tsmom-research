# -*- coding: utf-8 -*-
"""TSMOM-VRP-01 — FROZEN SCIENTIFIC CONSTANTS.

Every value here is transcribed verbatim from the sealed contract
`VRP_PREREGISTRATION.md` (SHA256 dd5822440bedbe58f49940651bddf656f4dbb593295b59c4eff2b45b89cf53e6).

NONE OF THESE IS A TUNABLE PARAMETER. Changing one is a contract violation,
not a configuration change. `vrp_validators.check_frozen_constants` asserts
each value against the sealed text on every acceptance run
(acceptance contract item 20).

This module imports nothing but the standard library and touches no data.
"""
from __future__ import annotations

import datetime as _dt

# --------------------------------------------------------------------------- #
# Contract identity
# --------------------------------------------------------------------------- #
LINEAGE = "TSMOM-VRP-01"
CONTRACT_ID = "TSMOM-VRP-01-PREREG-01"
PREREG_SHA256 = "dd5822440bedbe58f49940651bddf656f4dbb593295b59c4eff2b45b89cf53e6"
ACCEPTANCE_CONTRACT_SHA256 = "4fad50df6ef0c031cdb67e8100034718f49382ce0dd4e6df8e93f29afecb7dbb"
EXPOSURE_DISCLOSURE_SHA256 = "afae108d6e894c3822c783d45d77b85e09838578e5e7bf8040ad6dac6a3788c1"
S1_SEAL_COMMIT = "16d84545ba1385a482dbac7e776b31275f6fa5f7"

# --------------------------------------------------------------------------- #
# §C — Stage-A economics and margin (VRP-OD-2)
# --------------------------------------------------------------------------- #
theta = 0.25          # premium-to-stress ratio (M2 margin concept)
b = 0.30              # stress budget as a fraction of committed capital K
E = 0.075             # +E = theta * b : required annual excess return on K
F = -0.075            # -F : symmetric materially-adverse threshold

# --------------------------------------------------------------------------- #
# §D — sizing, stress scenario, reserve, granularity (VRP-OD-3)
# --------------------------------------------------------------------------- #
J = 30                # stress primitive: parallel +30 comparable VIX points
m_J = 40              # stressed margin: comparable points per contract-equivalent
LAMBDA = 0.10         # liquidity buffer as a fraction of K ("lambda" in the contract)
GRANULARITY_TOL = 0.10    # +/- 10 % integer-contract representability (§D.4)
STANDARD_MULTIPLIER = 1000.0   # $ per comparable VIX point, standard VX contract
MINI_MULTIPLIER = 100.0        # $ per comparable VIX point, mini VX contract
COMMON_BASIS_MULTIPLIER = 1000.0   # the common economic $/point basis (§F.5)

# --------------------------------------------------------------------------- #
# §G — cost convention (VRP-OD-6)
# --------------------------------------------------------------------------- #
c0 = 0.10             # comparable VIX points per contract-side: TOTAL spread + slippage
c0_descriptive = 0.05  # DESCRIPTIVE ONLY (R12); PROMOTION_POWER = NONE
commission = 2.00     # $ per standard-contract-side
fee = 2.00            # $ exchange + clearing per standard-contract-side
FUNDING_CHARGE = 0.0  # none; the primary is excess-of-cash

# --------------------------------------------------------------------------- #
# §H / §I — Stage-B book (VRP-OD-7) and tail estimand
# --------------------------------------------------------------------------- #
beta = 0.06           # fraction of TOTAL book wealth losable from the sleeve under J
s = 0.20              # = beta / b : strategic sleeve capital share
W0 = 1000000          # $ normalized RESEARCH book wealth (not a deployable NAV claim)
CORE_SHARE = 0.80     # = 1 - s
delta_tail = 0.0075   # required Stage-B compatibility margin, per tail month
SPY_TAIL_QUANTILE = 0.10   # X46 rule
k = 3                 # post-tail descriptive horizon, months (R10)
ratio_floor = 0.0025  # |mean_T(r_core)| floor for the §I.4 descriptive ratio
RATIO_SIGN_FRACTION = 0.95  # denominator must retain one sign in >= 95 % of replicates
CANONICAL_COST_BPS = 0.0002  # canonical 2-bps weight-turnover cost convention

# --------------------------------------------------------------------------- #
# §K — sample and evaluation boundaries (VRP-OD-8)
# --------------------------------------------------------------------------- #
cutoff = _dt.date(2026, 9, 1)          # STAGE_A_CUTOFF_DATE, a fixed calendar date
STAGE_A_LAST_MONTH = "2026-08"
stageB_end = _dt.date(2026, 5, 31)     # STAGE_B_LAST_MONTH = 2026-05
STAGE_B_LAST_MONTH = "2026-05"
CA_FORWARD_BOUNDARY = _dt.date(2026, 9, 11)   # §K.3 C-A blindness boundary
CORE_FROZEN_BOUNDARY = _dt.date(2026, 6, 12)  # frozen core boundary
ETF_PANEL_SHA256 = "3d2a7a56dbd92d4ff8138cfd894c87f5ac5ac088a11165db870673e0c05c3c31"

# --------------------------------------------------------------------------- #
# §P / §Q — prospective clocks
# --------------------------------------------------------------------------- #
N_A = 120             # COMPLETE, ELIGIBLE, NON-INVALIDATED scored months
N_B = 120             # CALENDAR months; the window freezes there
n_T_min_prosp = 10    # systemic-tail months required inside the frozen window
MAX_CARRY_FORWARD_DAYS = 2   # §F.4, per contract per calendar month

# --------------------------------------------------------------------------- #
# §J — inference (reused X01 §6.1 protocol)
# --------------------------------------------------------------------------- #
block = 12            # expected stationary-bootstrap block length, months (p = 1/12)
reps = 10000          # replicates
floor = 9500          # valid-replicate floor out of `reps`
seed = 7              # master seed; derived from nothing
SEED_SPAWN_ORDER = (
    "stage_a_historical",
    "stage_b_historical",
    "vrp_a_prospective",
    "vrp_b_prospective",
)
CI_LOWER_PCT = 2.5
CI_UPPER_PCT = 97.5
STAGE_A_MIN_DISTINCT_MONTHS = 24   # X01 replicate-validity rule
ANNUALISATION = 12                 # arithmetic: 12 * mean; never geometric

# --------------------------------------------------------------------------- #
# §J.3 — mechanical tolerances (reproducibility only; they change no estimand)
# --------------------------------------------------------------------------- #
TOL_RETURN_REL = 1e-9
TOL_WEIGHT_ABS = 1e-12
TOL_DOLLAR_ABS = 1e-6

# --------------------------------------------------------------------------- #
# §E.3 — FM-1 collateral yield convention (DESCRIPTIVE ONLY)
# --------------------------------------------------------------------------- #
FM1_SERIES = "DGS3MO"
FM1_MAX_LOOKBACK_DAYS = 7
FM1_DIVISOR = 1200.0   # Y / 100 / 12

__all__ = [n for n in dir() if not n.startswith("_")]
