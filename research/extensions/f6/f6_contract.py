# -*- coding: utf-8 -*-
"""CTA-EDGE-05 / F6 — the sealed contract, as executable constants.

Every value here is transcribed from the SEALED
`F6_S1_PREREGISTRATION_SEALED.md` (sha256
f26df71d4596dd8cacd261e571040b5b0e39fd37ef897c87422af31eeef275d9), from
`F6_S1_SEALED_MANIFEST.json`, and from nothing else. Changing any value here is
changing the sealed design, which is a new lineage — not a build fix.

`f6_tests.py` re-derives these numbers from the sealed Markdown and from the
sealed manifest, so a silent drift between this file and the contract is a test
failure rather than a quiet divergence.
"""

from __future__ import annotations

import os

# --------------------------------------------------------------------------- #
# seal identity                                                               #
# --------------------------------------------------------------------------- #
LINEAGE = "CTA-EDGE-05 / F6 MACRO_ANNOUNCEMENT_PREMIUM"
LINEAGE_SHORT = "CTA-EDGE-05"
SEAL_ID = "CTA-EDGE-05-F6-S1-2026-09-21"
SEAL_DATE = "2026-09-21"
SEAL_COMMIT = "0fd380682c6f0438c13ab25aa41c8fc9a3f5b70c"
SEALED_PREREG_SHA256 = (
    "f26df71d4596dd8cacd261e571040b5b0e39fd37ef897c87422af31eeef275d9")
SEALED_MANIFEST_SHA256 = (
    "7e61af335eae8a3b236c13724d9705cbb269bfa393894d43f2d6fcdfa4c841c7")
SEAL_RECORD_SHA256 = (
    "d88d851685a6a41ca5d8a39dcba93141acd335166c515e83b3ae06c37d1ca878")

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

SEALED_PREREG_RELPATH = "research/extensions/f6/F6_S1_PREREGISTRATION_SEALED.md"
SEALED_MANIFEST_RELPATH = "research/extensions/f6/F6_S1_SEALED_MANIFEST.json"
SEAL_RECORD_RELPATH = "research/extensions/f6/F6_S1_SEAL_RECORD.md"

# --------------------------------------------------------------------------- #
# §2 instrument and scope                                                     #
# --------------------------------------------------------------------------- #
PRIMARY_TICKER = "SPY"
#: struck entirely from CTA-EDGE-05 outcome computation; never a target column
PROHIBITED_TARGETS = ("TLT", "IEF")
#: a separate future lineage; never computed here
PROHIBITED_OBJECTS = ("F6.b", "F6B", "PRE_FOMC_DRIFT")

# --------------------------------------------------------------------------- #
# §3 event universe                                                           #
# --------------------------------------------------------------------------- #
EVENT_MANIFEST_RELPATH = "research/extensions/f6/F6_FINAL_EVENT_MANIFEST.json"
EVENT_MANIFEST_SHA256 = (
    "49ff27bfc20eb98265c440bac7368e92022b356d77647dce9151f012e40ed382")
FINAL_PRIMARY_EVENT_COUNT = 462
FAMILY_LABELS = {"FOMC": 119, "CPI": 176, "NFP": 176}
FAMILY_LABELS_TOTAL = 471
MULTI_EVENT_SESSIONS = 9
OVERLAP_ADJUSTMENT = 9
FAMILIES = ("FOMC", "CPI", "NFP")

PRIMARY_YEAR_FIRST = 2011
PRIMARY_YEAR_LAST = 2025
PRIMARY_YEARS = tuple(range(PRIMARY_YEAR_FIRST, PRIMARY_YEAR_LAST + 1))
YEAR_BLOCK_COUNT = 15
#: 2026 carries NO F6 outcome quantity. Not a window choice — a prohibition.
PROHIBITED_YEARS = (2026,)

#: permanently excluded pre-outcome by SCHEDULE_PIT_FAIL_CLOSED. Never reinstated.
PIT_EXCLUSIONS = (
    ("NFP", "2013-10-22"), ("CPI", "2013-10-30"), ("CPI", "2013-11-20"),
    ("NFP", "2025-11-20"), ("NFP", "2025-12-16"), ("CPI", "2025-12-18"),
)

# --------------------------------------------------------------------------- #
# §4/§5 trade, population and the opening boundary                            #
# --------------------------------------------------------------------------- #
POSITION_UNITS = 1.0              # long 1 unit notional, no leverage
P2_ROWS = 3772                    # every 2011..2025 trading session, none dropped
FIRST_PRIMARY_SESSION = "2011-01-03"
#: supplies the lagged close, the interval boundary and HOLD for the first 2011
#: session. NEVER a regression row, NEVER an event, NEVER a bootstrap member.
OPENING_BOUNDARY_SESSION = "2010-12-31"

# --------------------------------------------------------------------------- #
# §6 cash proxy — OWNER-CHOSEN                                                #
# --------------------------------------------------------------------------- #
CASH_SERIES = "DGS3MO"
CASH_RELPATH = "data/DGS3MO.csv"
CASH_SHA256 = (
    "50da2bfbb25e3e3241af7a4ad16e5a1bb5f08cdfb46bcb92f224954dce054319")
CASH_PERCENT_DIVISOR = 100.0
#: OWNER-CHOSEN. MUST NEVER be attributed to Treasury, H.15 or FRED.
CASH_DAYCOUNT = 365.0
CASH_DAYCOUNT_ATTRIBUTION = "OWNER-CHOSEN"
#: carry ONLY across source-explained non-publication. There is no day threshold.
CASH_ARBITRARY_DAY_RULE = None

# --------------------------------------------------------------------------- #
# §7 return objects                                                           #
# --------------------------------------------------------------------------- #
PANEL_RELPATH = "data/close_prices_raw.csv"
PANEL_SHA256 = (
    "3d2a7a56dbd92d4ff8138cfd894c87f5ac5ac088a11165db870673e0c05c3c31")
ENTRY_COST_BPS = 2.0
EXIT_COST_BPS = 2.0
ROUND_TRIP_COST = 0.0004          # 2 bps entry + 2 bps exit
#: P2 is GROSS of event transaction cost. Control sessions are never charged.
P2_IS_GROSS_OF_COST = True

# --------------------------------------------------------------------------- #
# §8 the ONE fixed P2 model                                                   #
# --------------------------------------------------------------------------- #
WEEKDAY_REFERENCE = "Friday"
WEEKDAY_INDICATORS = ("Monday", "Tuesday", "Wednesday", "Thursday")
DESIGN_COLUMNS = (
    "const", "EVENT",
    "weekday_Monday", "weekday_Tuesday", "weekday_Wednesday", "weekday_Thursday",
    "TOM", "HOLD", "AUCTION",
)
DESIGN_RANK = 9
TOM_SOURCE = "src/seasonality.py::is_tom (sealed)"
AUCTION_RELPATH = "research/extensions/ta/TA_EVENT_CALENDAR.csv"
AUCTION_SHA256 = (
    "b27be5b1d94cfc13fc8310e0d5216675e097a2245fc954e4b12ed282563f7cb6")
AUCTION_TENORS = ("10-Year", "30-Year")

# --------------------------------------------------------------------------- #
# §10 bootstrap — frozen pre-outcome                                          #
# --------------------------------------------------------------------------- #
BOOTSTRAP_B = 100000
BOOTSTRAP_SEED_SOURCE = (
    "CTA-EDGE-05|F6|S1_BOOTSTRAP|" + EVENT_MANIFEST_SHA256)
BOOTSTRAP_SEED_LITERAL = 2540719150
QUANTILE_LOWER = 0.025
QUANTILE_UPPER = 0.975
QUANTILE_METHOD = "linear"
QUANTILE_IMPLEMENTATION = 'numpy.percentile(..., method="linear")'
PINNED_ENV = {"numpy": "2.5.0", "pandas": "2.3.3", "python": "3.13.14"}
INTERVAL_WORDING = "two-sided nominal 95% percentile bootstrap"

# --------------------------------------------------------------------------- #
# §12 terminal classification                                                 #
# --------------------------------------------------------------------------- #
CLASS_POSITIVE = "positive"        # lower endpoint > 0
CLASS_UNRESOLVED = "unresolved"    # lower <= 0 < upper
CLASS_ABSENT = "excluded_absent"   # upper <= 0

TERMINAL_SUPPORTED = "SUPPORTED_HISTORICAL_EDGE"
TERMINAL_FRAGILITY = "ONE_YEAR_FRAGILITY / NOT_PROMOTED"
TERMINAL_UNRESOLVED = "UNRESOLVED"
TERMINAL_NOT_SPECIFIC_POSITIVE = (
    "POSITIVE_PAYOFF_NOT_ANNOUNCEMENT_SPECIFIC / NOT_PROMOTED")
TERMINAL_NOT_SPECIFIC = "NOT_ANNOUNCEMENT_SPECIFIC / NOT_PROMOTED"
TERMINAL_NOT_PROMOTED = "NOT_PROMOTED"
#: these states DO NOT EXIST for F6 and must never be emitted
FORBIDDEN_TERMINAL_STATES = ("LOW_POWER", "MECHANISM_FALSIFIED",
                             "INSUFFICIENT_EVIDENCE", "CONFIRMED")

# --------------------------------------------------------------------------- #
# §14 reuse and evidence ceiling                                              #
# --------------------------------------------------------------------------- #
SAMPLE_REUSE_CLASS = "T0_REUSED_DEPENDENT"
EVIDENCE_CEILING = "SUPPORTED"
INDEPENDENT_CONFIRMATION = False

# --------------------------------------------------------------------------- #
# §15 claim cap                                                               #
# --------------------------------------------------------------------------- #
CLAIM_MUST_NOT = (
    "causal uncertainty compensation", "independent confirmation",
    "individual FOMC alpha", "individual CPI alpha", "individual NFP alpha",
    "TLT premium", "F6.b pre-FOMC drift", "post-2015 persistence",
    "future persistence", "buy-and-hold dominance", "LOYO significance",
    "stable LOYO magnitudes", "production-grade fills",
    "exact finite-sample 95% coverage",
)

# --------------------------------------------------------------------------- #
# S2/S3 lifecycle                                                             #
# --------------------------------------------------------------------------- #
S1_STATUS = "SEALED"
S2_BUILD_AUTHORIZED = True
S3_RUN_AUTHORIZED = False          # NOT granted by the seal, and not by this build
RETURN_REVEAL_AUTHORIZED = False
F6_PRIMARY_TRIAL_CONSUMED = False


def abspath(relpath: str) -> str:
    return os.path.join(REPO, relpath.replace("/", os.sep))
