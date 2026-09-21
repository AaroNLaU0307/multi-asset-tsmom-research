"""CTA-EDGE-01-TA — the sealed contract, as executable constants.

Every value here is transcribed from the SEALED `TA_PREREGISTRATION.md`
(sha256 3b495fcb220a86b9c4226e308e4814bdfdd871d1c69ce352e99b78977436d35b) and from
nothing else. No value in this module may be changed by any later session: changing
one is changing the sealed design, which is a new lineage.

`ta_prereg_validate.py` and `ta_tests.py` both re-derive these numbers from the sealed
Markdown, so a silent drift between this file and the contract is a test failure
rather than a quiet divergence.
"""

from __future__ import annotations

import os

LINEAGE = "CTA-EDGE-01-TA"
CONTRACT_ID = "CTA-EDGE-01-TA-PREREG-01"
SEALED_PREREG_SHA256 = (
    "3b495fcb220a86b9c4226e308e4814bdfdd871d1c69ce352e99b78977436d35b")
SEAL_COMMIT = "881e684b4ddca73f117ea78af14843dabf3c59c9"

# --------------------------------------------------------------------------- #
# §B.4 Window geometry — grid-day offsets from t0                              #
# --------------------------------------------------------------------------- #
PRE_OFFSET_OPEN = -6
PRE_OFFSET_CLOSE = -1
POST_OFFSET_OPEN = 0
POST_OFFSET_CLOSE = +5
#: two events collide when their t0 grid indices are this close or closer
OVERLAP_GAP = POST_OFFSET_CLOSE - PRE_OFFSET_OPEN          # 11

# --------------------------------------------------------------------------- #
# §E Cost model — the position path is flat across the auction-day bar          #
# --------------------------------------------------------------------------- #
ONE_WAY_BPS = 2.0
ONE_WAY_UNITS_PER_EVENT = 4          # open short, close short, open long, close long
COST_BPS = ONE_WAY_BPS * ONE_WAY_UNITS_PER_EVENT           # 8.0

# --------------------------------------------------------------------------- #
# §E.3 Materiality bars                                                        #
# --------------------------------------------------------------------------- #
M1_NET_BPS = 8.0
M1_GROSS_BPS = M1_NET_BPS + COST_BPS                        # 16.0
M2_SHARPE = 0.30

# --------------------------------------------------------------------------- #
# §C.2 / §C.3 the sealed event calendar                                        #
# --------------------------------------------------------------------------- #
PRIMARY_CELL = "PRIMARY"
SECONDARY_CELL = "SECONDARY"
PRIMARY_INSTRUMENT = "TLT"
SECONDARY_INSTRUMENT = "IEF"
GRADIENT_INSTRUMENT = "SHY"          # diagnostic, no powers at all
PLACEBO_INSTRUMENT = "SPY"           # damage power only

PRIMARY_VALID_WINDOWS = 213
SECONDARY_VALID_WINDOWS = 258
PRIMARY_FIRST_T0 = "2006-02-09"
PRIMARY_LAST_T0 = "2026-05-13"
SECONDARY_FIRST_T0 = "2002-08-07"
SECONDARY_LAST_T0 = "2026-05-12"
PRIMARY_YEARS = tuple(range(2006, 2027))                    # 21 years
SECONDARY_YEARS = tuple(range(2002, 2027))                  # 25 years
PRIMARY_REOPENING_SPLIT = {"No": 73, "Yes": 140}

# --------------------------------------------------------------------------- #
# §F.1 the calendarised month grid                                             #
# --------------------------------------------------------------------------- #
MONTH_GRID_FIRST = "2006-02"
MONTH_GRID_LAST = "2026-05"
MONTH_GRID_N = 244
MONTH_GRID_EVENT_MONTHS = 213
MONTH_GRID_ZERO_MONTHS = 31
SHARPE_PERIODS_PER_YEAR = 12
SHARPE_DDOF = 1
RISK_FREE = 0.0

# --------------------------------------------------------------------------- #
# §H Uncertainty — ONE bootstrap family                                        #
# --------------------------------------------------------------------------- #
BOOTSTRAP_B = 10_000
CI_LOWER_PCT = 2.5
CI_UPPER_PCT = 97.5
#: §H.3 seed protocol, constants only. Children 0..3 of SeedSequence(7) belong to
#: TSMOM-VRP-01 and are untouched; this lineage uses a new child 4.
SEED_ENTROPY = 7
SEED_SPAWN_N = 5
SEED_CHILD_INDEX = 4
SEED_SUBSPAWN_PRIMARY = 0            # drives TLT, SPY, SHY on the primary year set
SEED_SUBSPAWN_SECONDARY = 1          # drives IEF on the secondary year set

# --------------------------------------------------------------------------- #
# §G.3 macro / QRA identification diagnostic                                   #
# --------------------------------------------------------------------------- #
MACRO_COVARIATES = ("CPI", "NFP", "FOMC", "QRA")
MACRO_MIN_REFERENCE_GROUP = 20
MACRO_DAMAGE_BAR_GROSS_BPS = M1_GROSS_BPS                   # 16.0

# --------------------------------------------------------------------------- #
# Paths                                                                        #
# --------------------------------------------------------------------------- #
TA_DIR = os.path.join("research", "extensions", "ta")
EVENT_CALENDAR_PATH = os.path.join(TA_DIR, "TA_EVENT_CALENDAR.csv")
MACRO_CALENDAR_PATH = os.path.join(TA_DIR, "TA_MACRO_CALENDAR.csv")
PANEL_PATH = os.path.join("data", "close_prices_raw.csv")

EVENT_CALENDAR_SHA256 = (
    "b27be5b1d94cfc13fc8310e0d5216675e097a2245fc954e4b12ed282563f7cb6")
PANEL_SHA256 = (
    "3d2a7a56dbd92d4ff8138cfd894c87f5ac5ac088a11165db870673e0c05c3c31")

# --------------------------------------------------------------------------- #
# Declared powers — enforced mechanically in ta_classify.py                    #
# --------------------------------------------------------------------------- #
POWERS = {
    "TLT_PRIMARY":   {"promotion": True,  "damage": False, "kill": False},
    "IEF_SECONDARY": {"promotion": False, "damage": False, "kill": False},
    "SHY_GRADIENT":  {"promotion": False, "damage": False, "kill": False},
    "SPY_PLACEBO":   {"promotion": False, "damage": True,  "kill": False},
    "MACRO_QRA":     {"promotion": False, "damage": True,  "kill": False},
    "LOYO":          {"promotion": False, "damage": True,  "kill": False},
}

EVIDENCE_CEILING = "supported"
FORBIDDEN_CAUSAL_REMINDER = (
    "REDUCED_FORM ONLY. Never evidence of a dealer balance-sheet cause; never a claim "
    "about cash Treasuries; never attributable to 30-year supply specifically (a "
    "10-Year auction sits inside 213 of 213 primary windows); never crisis "
    "diversification; never an improvement to canonical TSMOM. Evidence ceiling is "
    "`supported` on an exposed panel - never confirmed, never independently confirmed."
)

STATUS_MAP = {
    "A": ("not_promoted", ""),
    "B": ("not_promoted", "TARGET_MARGIN_EXCLUDED"),
    "C": ("unresolved", ""),
    "D": ("supported", ""),
    "I": ("unresolved", "IDENTIFICATION_INSUFFICIENT_FOR_THE_CLAIM"),
}
