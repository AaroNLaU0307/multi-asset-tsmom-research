"""The three primitive macro legs, contract section D.

    TRANSFORM = 12-MONTH CHANGE, SIGN ONLY.
      NO 3m / 6m / 18m / 24m · NO z-score · NO standardisation · NO magnitude
      scaling · NO threshold · NO percentile · NO smoothing family · NO
      lookback search.
    sign(0) = 0 everywhere.

Every quantity here is a Fraction, so `sign` is exact and no epsilon exists to
tune. That is a contract requirement, not a style preference: an epsilon would
be a threshold, and section D forbids thresholds.
"""

from __future__ import annotations

import datetime as dt
from fractions import Fraction
from typing import Mapping

from .pit import UNDEFINED, ContractViolation, months_back

#: Contract section D. The ONLY horizon. Not a parameter, not a default.
LOOKBACK_MONTHS = 12

#: Reference months each leg must find at the exact required lags.
GROWTH_MONTHS_REQUIRED = 13        # m and m-12
INFLATION_MONTHS_REQUIRED = 25     # m, m-12 and m-24

#: Contract section D.2. The inflation leg is defined on this series and no
#: other; there is no series family and no fallback.
INFLATION_SERIES = "CPILFENS"
FORBIDDEN_INFLATION_SERIES = frozenset({"CPIAUCSL", "CPILFESL", "PCEPILFE"})


def sign(x) -> int:
    """Exact three-valued sign. sign(0) = 0, uniformly, for every leg."""
    if x is UNDEFINED:
        raise ContractViolation("sign() called on UNDEFINED; callers must "
                                "propagate UNDEFINED rather than sign it")
    return (x > 0) - (x < 0)


# --------------------------------------------------------------------------- #
# Growth — contract section D.1
# --------------------------------------------------------------------------- #

def change_12m(snapshot: Mapping, newest: dt.date):
    """sign-ready 12-month change of a level series: X(m) - X(m-12)."""
    prior = months_back(newest, LOOKBACK_MONTHS)
    if newest not in snapshot or prior not in snapshot:
        return UNDEFINED
    return snapshot[newest] - snapshot[prior]


def growth_leg(indpro_snapshot: Mapping, payems_snapshot: Mapping,
               indpro_newest: dt.date | None = None,
               payems_newest: dt.date | None = None):
    """G = sign( sign(D12 INDPRO) + sign(D12 PAYEMS) ).

    The sealed nine-state truth table, stated as arithmetic rather than as a
    lookup so there is one definition rather than two that can drift:

        (-1,-1) -> -1   (0,-1) -> -1   (+1,-1) ->  0
        (-1, 0) -> -1   (0, 0) ->  0   (+1, 0) -> +1
        (-1,+1) ->  0   (0,+1) -> +1   (+1,+1) -> +1

    One measure, one vote. Opposed measures ABSTAIN — they do not break the tie
    toward either. A silent measure (sign 0) does NOT veto the other.

    Both measures are required: the leg is UNDEFINED when either is
    unavailable. A single available measure is NOT promoted to carry the leg,
    because "one vote" and "the whole leg" are different objects and the
    contract sealed the two-measure form.
    """
    if not indpro_snapshot or not payems_snapshot:
        return UNDEFINED
    i_new = indpro_newest or max(indpro_snapshot)
    p_new = payems_newest or max(payems_snapshot)
    di = change_12m(indpro_snapshot, i_new)
    dp = change_12m(payems_snapshot, p_new)
    if di is UNDEFINED or dp is UNDEFINED:
        return UNDEFINED
    return sign(sign(di) + sign(dp))


# --------------------------------------------------------------------------- #
# Inflation — contract section D.2
# --------------------------------------------------------------------------- #

def pi12(snapshot: Mapping, month: dt.date):
    """pi12(m) = CPILFENS(m) / CPILFENS(m-12) - 1, exact."""
    prior = months_back(month, LOOKBACK_MONTHS)
    if month not in snapshot or prior not in snapshot:
        return UNDEFINED
    base = snapshot[prior]
    if base == 0:
        raise ContractViolation(
            "CPILFENS base value is zero at %s; the sealed ratio is undefined "
            "and no substitute is authorized" % prior)
    return Fraction(snapshot[month], base) - 1


def inflation_leg(cpi_snapshot: Mapping, newest: dt.date | None = None):
    """I = sign[ pi12(m) - pi12(m-12) ].

    The RATE of core inflation, not its level. The contract records why: the
    12-month change of a core price index IS pi12, whose sign is +1 in every
    month of the window — a static bet, not a momentum signal. The sealed leg
    is therefore the change in the rate, which needs 25 reference months.
    """
    if not cpi_snapshot:
        return UNDEFINED
    m = newest or max(cpi_snapshot)
    now = pi12(cpi_snapshot, m)
    then = pi12(cpi_snapshot, months_back(m, LOOKBACK_MONTHS))
    if now is UNDEFINED or then is UNDEFINED:
        return UNDEFINED
    return sign(now - then)


# --------------------------------------------------------------------------- #
# Policy — contract section D.3
# --------------------------------------------------------------------------- #

def policy_leg(target_now, target_12m_ago):
    """P = sign[ target(t) - target(t - 12 months) ].

    Both legs must be publicly ANNOUNCED by their respective cutoffs; the
    caller resolves them through `policy.PolicySchedule`, which is structurally
    incapable of consulting a FRED realtime stamp.
    """
    if target_now is UNDEFINED or target_12m_ago is UNDEFINED:
        return UNDEFINED
    return sign(target_now - target_12m_ago)


# --------------------------------------------------------------------------- #
# The sealed truth table, exposed for verification
# --------------------------------------------------------------------------- #

GROWTH_TRUTH_TABLE = {
    (-1, -1): -1, (0, -1): -1, (1, -1): 0,
    (-1, 0): -1, (0, 0): 0, (1, 0): 1,
    (-1, 1): 0, (0, 1): 1, (1, 1): 1,
}
