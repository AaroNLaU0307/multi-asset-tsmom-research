"""CTA-EDGE-02-BENB — the sealed contract, as executable constants.

Every value here is transcribed from the SEALED `BENB_PREREGISTRATION.md`
(sha256 1b7ca2122ba14c4097e4d76d7a733bf0c77ab9c0d02dd93a38c25bc1be5160cf) and from
Aaron's Owner decision BENB-OD-1, and from nothing else. Changing any value here is
changing the sealed design, which is a new lineage.

`benb_tests.py` re-derives these numbers from the sealed Markdown, so a silent drift
between this file and the contract is a test failure rather than a quiet divergence.
"""

from __future__ import annotations

import os

LINEAGE = "CTA-EDGE-02-BENB"
CONTRACT_ID = "CTA-EDGE-02-BENB-PREREG-01"
SEALED_PREREG_SHA256 = (
    "1b7ca2122ba14c4097e4d76d7a733bf0c77ab9c0d02dd93a38c25bc1be5160cf")
SEAL_MANIFEST_SHA256 = (
    "6aa0d21401b9887f4a44ab6559fa10d7a59ae5a8b512e1ad306543c061483703")
SEAL_COMMIT = "c1a3f8155a9fdb86d55b620c33498f604fcbf8d0"

# --------------------------------------------------------------------------- #
# §A instruments                                                              #
# --------------------------------------------------------------------------- #
PRIMARY_TICKER = "HYG"
SECONDARY_TICKER = "LQD"          # declared replication, NO RESCUE POWER
PRIMARY_CELL = "PRIMARY"
SECONDARY_CELL = "SECONDARY"

# --------------------------------------------------------------------------- #
# §D.3 the abnormal-basis feature                                             #
# --------------------------------------------------------------------------- #
#: expanding median of b_s for s < t, strictly causal. No window, nothing to search.
MIN_PRIOR_HISTORY = 250

# --------------------------------------------------------------------------- #
# §F cost model                                                               #
# --------------------------------------------------------------------------- #
ONE_WAY_COST_BPS = 5.0
ROUND_TRIP_COST_BPS = 10.0        # open(t+1) entry + close(t+1) exit

# --------------------------------------------------------------------------- #
# §H materiality — M1 sealed at S1, M2 by BENB-OD-1                           #
# --------------------------------------------------------------------------- #
M1_RETURN_FLOOR_BPS = 0.0         # lower 95 % bound of mean NET_TRADE_RETURN, STRICT >
M2_SHARPE = 0.30                  # lower 95 % bound of calendarised Sharpe, STRICT >
SHARPE_PERIODS_PER_YEAR = 12
SHARPE_DDOF = 1
RISK_FREE = 0.0

# --------------------------------------------------------------------------- #
# §G inference — ONE bootstrap family                                         #
# --------------------------------------------------------------------------- #
BOOTSTRAP_B = 10_000              # PRODUCTION constant. Tests may use fewer.
CI_LOWER_PCT = 2.5
CI_UPPER_PCT = 97.5
#: §J.2(d): leave-one-year-out must leave a non-degenerate two-year sample.
MIN_YEARS_WITH_DISCOUNT = 3

# --------------------------------------------------------------------------- #
# Paths and pinned identities (§C)                                            #
# --------------------------------------------------------------------------- #
BENB_DIR = os.path.join("research", "extensions", "benb")
DATA_DIR = os.path.join("data", "benb")

PINNED = {
    "ishares_HYG_fund_download.xml":
        "10dcd91e095a56d83762019738aa5b14374ea5d1f723616636b52170150ec533",
    "ishares_LQD_fund_download.xml":
        "d0cc3b0121806b20a227b00ae50d3f8523e6cc560e7bae16d715824b50ce0a47",
    "HYG_raw_ohlc.csv":
        "1ed30697cd0c665d9abe3d60abfe8c03314fb8889f3a459df207c5b85cb3bce8",
    "LQD_raw_ohlc.csv":
        "9d120233fd18bbd28188c18ce5a99b8347416f58b903d7452b83b47d011fe036",
    "HYG_nav_daily.csv":
        "7735da958ef10522e39c9138b8cf8c686206585f3b805c327588fb61e9eae5de",
    "LQD_nav_daily.csv":
        "3d78dbd80b92e9715eb9f6249597d65556d12b6517aad6832640e7296698007a",
    "benb_price_meta.json":
        "8179c06f8f8dd088d3b08cb9b4d6a1a8abbd210239f3e2b226e70de223d8b339",
}

#: S0-repair structural eligibility, recomputed and unchanged at S1. These are
#: STRUCTURAL counts. They are NOT the primary sample size: the discount-side subset
#: is unknown at seal and stays unknown until the governed run.
STRUCTURAL_ELIGIBLE = {"HYG": 4415, "LQD": 5539}
STRUCTURAL_COMMON = {"HYG": 4887, "LQD": 6069}

# --------------------------------------------------------------------------- #
# Declared powers — enforced in benb_classify.py                              #
# --------------------------------------------------------------------------- #
POWERS = {
    "HYG_BETA_T":    {"promotion": True,  "rescue": False},
    "BETA_O":        {"promotion": False, "rescue": False},
    "BETA_N":        {"promotion": False, "rescue": False},
    "LQD_SECONDARY": {"promotion": False, "rescue": False},
    "PREMIUM_SIDE":  {"promotion": False, "rescue": False},
}

EVIDENCE_CEILING = "supported"
NAV_PROVENANCE = "RECONSTRUCTED_HISTORICAL_SERIES_WITH_NON-VINTAGE_LIMITATION"
FORBIDDEN_CAUSAL_REMINDER = (
    "REDUCED-FORM PREDICTIVE / MARKET-STRUCTURE CLAIM ONLY. A supported result does NOT "
    "prove authorised-participant causality, dealer-balance-sheet causality, that NAV is "
    "inefficient generally, that credit is mispriced generally, crisis diversification, "
    "or any TSMOM improvement. A stale-NAV result does NOT prove ETFs are inefficient or "
    "that issuer NAV is wrong in any legal or accounting sense. An overnight-convergence "
    "result is NOT a harvestable edge under this signal timing. Evidence ceiling is "
    "`supported` on a reused price sample - never confirmed, never independently "
    "confirmed."
)

STATUS_MAP = {
    "F":   ("unresolved",   "IDENTIFICATION_INSUFFICIENT_FOR_THE_CLAIM"),
    "A-M": ("not_promoted", "MIXED_NON_HARVESTABLE_CONVERGENCE"),
    "A":   ("not_promoted", "STALE_NAV_DOMINATED"),
    "B":   ("not_promoted", "OVERNIGHT_PRICE_DISCOVERY_ONLY"),
    "C1":  ("not_promoted", "TRADABLE_CONVERGENCE_EXCLUDED"),
    "C2":  ("unresolved",   "LOW_POWER"),
    "G":   ("unresolved",   "YEAR_DEPENDENT_FRAGILE"),
    "D":   ("not_promoted", "TARGET_MARGIN_EXCLUDED"),
    "S":   ("supported",    ""),
    "E":   ("unresolved",   "LOW_POWER"),
}
