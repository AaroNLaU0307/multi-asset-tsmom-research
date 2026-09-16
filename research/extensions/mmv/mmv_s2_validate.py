"""CTA-EDGE-04-MMV — S2 SYNTHETIC VALIDATOR.

Every test builds its own synthetic world. Not one test reads a real macro
value, a real price, or a real canonical TSMOM sign, and none constructs the
candidate feature over the 218 canonical decision dates.

    python research/extensions/mmv/mmv_s2_validate.py

Exit code 0 iff every test passes.

PASS = sealed behaviour reproduced. FAIL = sealed behaviour violated. No test
depends on markdown line wrapping, document formatting or prose.
"""

from __future__ import annotations

import ast
import datetime as dt
import hashlib
import inspect
import os
import subprocess
import sys
import traceback
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
os.chdir(REPO)
if REPO not in sys.path:
    sys.path.insert(0, REPO)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import numpy as np                                             # noqa: E402
import pandas as pd                                            # noqa: E402

import config                                                  # noqa: E402
from src import portfolio as canonical_portfolio               # noqa: E402
from engine import (PREREG_SHA256, SEAL_SHA256,                # noqa: E402
                    SEALED_COMMIT)
from engine import concordance, gate05, legs, policy, risk     # noqa: E402
from engine import start as startmod                           # noqa: E402
from engine import votes                                       # noqa: E402
from engine.pit import (UNDEFINED, ContractViolation,          # noqa: E402
                        VintageSeries, months_back, parse_value,
                        require_months)

MMV = "research/extensions/mmv"
ENGINE = os.path.join(MMV, "engine")

TESTS = []
RESULTS = []


def test(group):
    def deco(fn):
        TESTS.append((group, fn.__name__, fn))
        return fn
    return deco


def expect_raises(exc, fn, *a, **k):
    try:
        fn(*a, **k)
    except exc:
        return True
    except Exception as e:                                       # noqa: BLE001
        raise AssertionError("expected %s, got %s: %s"
                            % (exc.__name__, type(e).__name__, e))
    raise AssertionError("expected %s, nothing raised" % exc.__name__)


# ===========================================================================
# SYNTHETIC WORLD BUILDERS — no real data, ever
# ===========================================================================

def monthly_series(series_id, start_year, n_months, values, vintage,
                   release_times=None):
    """A single-vintage synthetic ALFRED series.

    ``values`` is a list of exact numeric strings, one per consecutive month
    beginning at ``start_year``-01-01.
    """
    obs = []
    y, m = start_year, 1
    for k in range(n_months):
        obs.append({"date": dt.date(y, m, 1).isoformat(),
                    "realtime_start": vintage,
                    "realtime_end": "9999-12-31",
                    "value": values[k]})
        m += 1
        if m > 12:
            m = 1
            y += 1
    return VintageSeries(series_id, obs, release_times)


def linear_series(series_id, start_year, n_months, first, step, vintage,
                  release_times=None):
    vals = [str(first + step * k) for k in range(n_months)]
    return monthly_series(series_id, start_year, n_months, vals, vintage,
                          release_times)


def flat_growth_snapshot(newest, direction):
    """A 13-month snapshot whose 12-month change has the requested sign."""
    base = Fraction(100)
    delta = Fraction(direction)
    return {months_back(newest, k): base + (delta if k == 0 else 0)
            for k in range(13)}


def ann(date_str, time_or_none, target):
    return policy.PolicyAnnouncement(
        dt.date.fromisoformat(date_str), time_or_none, Fraction(target))


# ===========================================================================
# GROUP 1 — SEALED AUTHORITY
# ===========================================================================

@test("SEAL")
def t_seal_manifest_hash_matches():
    h = hashlib.sha256(open(MMV + "/MMV_SEAL_MANIFEST.md", "rb").read()).hexdigest()
    assert h == SEAL_SHA256, h


@test("SEAL")
def t_preregistration_hash_matches():
    h = hashlib.sha256(open(MMV + "/MMV_PREREGISTRATION.md", "rb").read()).hexdigest()
    assert h == PREREG_SHA256, h


@test("SEAL")
def t_sealed_commit_is_ancestor_of_head():
    r = subprocess.run(["git", "merge-base", "--is-ancestor", SEALED_COMMIT, "HEAD"])
    assert r.returncode == 0, "S2 branch does not descend from the sealed commit"


@test("SEAL")
def t_sealed_artifacts_unmodified_on_this_branch():
    r = subprocess.run(["git", "diff", "--name-only", SEALED_COMMIT, "HEAD"],
                       capture_output=True, text=True)
    changed = set(r.stdout.split())
    sealed = {MMV + "/MMV_PREREGISTRATION.md", MMV + "/MMV_SEAL_MANIFEST.md",
              MMV + "/mmv_preseal_check.py", MMV + "/MMV_S0_FRAME.md",
              MMV + "/MMV_S1_HOLD_RECORD.md",
              "ops/OWNER_DECISION_RECORD_CTA_EDGE_04_MMV.md"}
    assert not (changed & sealed), "sealed artifacts modified: %s" % (changed & sealed)


# ===========================================================================
# GROUP 2 — PIT RESOLVER
# ===========================================================================

@test("PIT")
def t_vintage_before_cutoff_is_eligible():
    s = linear_series("X", 2000, 24, 100, 1, "2002-01-10")
    assert s.eligible_vintage("2002-03-31") == dt.date(2002, 1, 10)


@test("PIT")
def t_vintage_after_cutoff_never_eligible():
    s = linear_series("X", 2000, 24, 100, 1, "2002-06-10")
    assert s.eligible_vintage("2002-03-31") is None
    assert s.as_of("2002-03-31") == {}


@test("PIT")
def t_same_day_vintage_before_cutoff_time_is_eligible():
    s = linear_series("X", 2000, 24, 100, 1, "2002-03-29",
                      {dt.date(2002, 3, 29): dt.time(14, 0)})
    assert s.eligible_vintage("2002-03-29") == dt.date(2002, 3, 29)


@test("PIT")
def t_same_day_vintage_after_cutoff_time_uses_prior():
    obs = [{"date": "2000-01-01", "realtime_start": "2002-01-10",
            "realtime_end": "9999-12-31", "value": "1"},
           {"date": "2000-02-01", "realtime_start": "2002-03-29",
            "realtime_end": "9999-12-31", "value": "2"}]
    s = VintageSeries("X", obs, {dt.date(2002, 3, 29): dt.time(16, 0)})
    assert s.eligible_vintage("2002-03-29") == dt.date(2002, 1, 10)


@test("PIT")
def t_same_day_vintage_with_no_published_time_uses_prior():
    obs = [{"date": "2000-01-01", "realtime_start": "2002-01-10",
            "realtime_end": "9999-12-31", "value": "1"},
           {"date": "2000-02-01", "realtime_start": "2002-03-29",
            "realtime_end": "9999-12-31", "value": "2"}]
    s = VintageSeries("X", obs)                    # no release_times at all
    assert s.eligible_vintage("2002-03-29") == dt.date(2002, 1, 10)


@test("PIT")
def t_same_day_exactly_at_cutoff_is_eligible():
    s = linear_series("X", 2000, 24, 100, 1, "2002-03-29",
                      {dt.date(2002, 3, 29): dt.time(15, 45)})
    assert s.eligible_vintage("2002-03-29") == dt.date(2002, 3, 29)


@test("PIT")
def t_same_day_one_minute_after_cutoff_is_not_eligible():
    s = linear_series("X", 2000, 24, 100, 1, "2002-03-29",
                      {dt.date(2002, 3, 29): dt.time(15, 46)})
    assert s.eligible_vintage("2002-03-29") is None


@test("PIT")
def t_no_final_revised_leakage_revision_invisible_before_publication():
    obs = [{"date": "2001-01-01", "realtime_start": "2001-02-15",
            "realtime_end": "2003-01-01", "value": "100"},
           {"date": "2001-01-01", "realtime_start": "2003-01-02",
            "realtime_end": "9999-12-31", "value": "999"}]
    s = VintageSeries("X", obs)
    assert s.as_of("2002-06-30")[dt.date(2001, 1, 1)] == Fraction(100)


@test("PIT")
def t_revision_becomes_visible_after_publication():
    # Without this, the leakage test above would pass vacuously.
    obs = [{"date": "2001-01-01", "realtime_start": "2001-02-15",
            "realtime_end": "2003-01-01", "value": "100"},
           {"date": "2001-01-01", "realtime_start": "2003-01-02",
            "realtime_end": "9999-12-31", "value": "999"}]
    s = VintageSeries("X", obs)
    assert s.as_of("2003-06-30")[dt.date(2001, 1, 1)] == Fraction(999)


@test("PIT")
def t_missing_marker_is_omitted_not_zero():
    obs = [{"date": "2001-01-01", "realtime_start": "2001-02-15",
            "realtime_end": "9999-12-31", "value": "."},
           {"date": "2001-02-01", "realtime_start": "2001-02-15",
            "realtime_end": "9999-12-31", "value": "5"}]
    snap = VintageSeries("X", obs).as_of("2002-01-01")
    assert dt.date(2001, 1, 1) not in snap
    assert snap[dt.date(2001, 2, 1)] == Fraction(5)


@test("PIT")
def t_parse_value_is_exact_not_float():
    v = parse_value("0.1")
    assert isinstance(v, Fraction) and v == Fraction(1, 10)
    assert parse_value(".") is UNDEFINED
    assert parse_value("") is UNDEFINED


@test("PIT")
def t_latest_reference_is_newest_valued_month():
    s = linear_series("X", 2000, 15, 100, 1, "2001-06-01")
    assert s.latest_reference("2002-01-01") == dt.date(2001, 3, 1)


@test("PIT")
def t_months_back_crosses_year_boundary():
    assert months_back(dt.date(2001, 3, 1), 12) == dt.date(2000, 3, 1)
    assert months_back(dt.date(2001, 1, 1), 1) == dt.date(2000, 12, 1)
    assert months_back(dt.date(2001, 1, 1), 24) == dt.date(1999, 1, 1)


@test("PIT")
def t_require_months_detects_hole_at_the_exact_lag():
    snap = {months_back(dt.date(2010, 1, 1), k): Fraction(1) for k in range(30)}
    del snap[dt.date(2009, 1, 1)]                 # exactly the m-12 lag
    assert len(snap) == 29                        # a naive COUNT would pass
    assert not require_months(snap, dt.date(2010, 1, 1), 13)


@test("PIT")
def t_require_months_passes_on_contiguous_history():
    snap = {months_back(dt.date(2010, 1, 1), k): Fraction(1) for k in range(13)}
    assert require_months(snap, dt.date(2010, 1, 1), 13)
    assert not require_months(snap, dt.date(2010, 1, 1), 25)


@test("PIT")
def t_first_release_chain_takes_earliest_publication():
    obs = [{"date": "2001-01-01", "realtime_start": "2001-02-15",
            "realtime_end": "2003-01-01", "value": "100"},
           {"date": "2001-01-01", "realtime_start": "2003-01-02",
            "realtime_end": "9999-12-31", "value": "999"}]
    chain = VintageSeries("X", obs).first_release_chain()
    assert chain[dt.date(2001, 1, 1)] == Fraction(100)


# ===========================================================================
# GROUP 3 — POLICY RESOLVER (announcement authority)
# ===========================================================================

@test("POLICY")
def t_policy_earlier_announcement_is_eligible():
    s = policy.PolicySchedule([ann("2015-03-18", dt.time(14, 0), 1)])
    assert s.eligible("2015-06-30") == Fraction(1)


@test("POLICY")
def t_policy_same_day_before_cutoff_admits_new_target():
    s = policy.PolicySchedule([ann("2015-01-31", dt.time(14, 0), 1),
                               ann("2015-06-30", dt.time(14, 0), 2)])
    assert s.eligible("2015-06-30") == Fraction(2)


@test("POLICY")
def t_policy_same_day_after_cutoff_retains_previous():
    s = policy.PolicySchedule([ann("2015-01-31", dt.time(14, 0), 1),
                               ann("2015-06-30", dt.time(16, 30), 2)])
    assert s.eligible("2015-06-30") == Fraction(1)


@test("POLICY")
def t_policy_same_day_unknown_time_retains_previous():
    s = policy.PolicySchedule([ann("2015-01-31", dt.time(14, 0), 1),
                               ann("2015-06-30", None, 2)])
    assert s.eligible("2015-06-30") == Fraction(1)


@test("POLICY")
def t_policy_same_day_exactly_at_cutoff_admits_new_target():
    s = policy.PolicySchedule([ann("2015-01-31", dt.time(14, 0), 1),
                               ann("2015-06-30", dt.time(15, 45), 2)])
    assert s.eligible("2015-06-30") == Fraction(2)


@test("POLICY")
def t_policy_future_announcement_never_eligible():
    s = policy.PolicySchedule([ann("2015-01-31", dt.time(14, 0), 1),
                               ann("2015-09-17", dt.time(14, 0), 2)])
    assert s.eligible("2015-06-30") == Fraction(1)


@test("POLICY")
def t_policy_undefined_before_any_announcement():
    s = policy.PolicySchedule([ann("2015-01-31", dt.time(14, 0), 1)])
    assert s.eligible("2014-12-31") is UNDEFINED


@test("POLICY")
def t_policy_lagged_leg_obeys_the_same_rule():
    s = policy.PolicySchedule([ann("2014-06-30", dt.time(14, 0), 1),
                               ann("2015-06-30", dt.time(16, 0), 5)])
    now, then = s.eligible_pair("2015-06-30")
    assert now == Fraction(1)      # same-day 16:00 rejected
    assert then == Fraction(1)


@test("POLICY")
def t_policy_duplicate_announcement_date_raises():
    expect_raises(ContractViolation, policy.PolicySchedule,
                  [ann("2015-06-30", dt.time(14, 0), 1),
                   ann("2015-06-30", dt.time(14, 0), 2)])


@test("POLICY")
def t_splice_uses_single_target_through_2008_12_15():
    single = {dt.date(2008, 12, 15): Fraction(1)}
    assert policy.spliced_target("2008-12-15", single, {}, {}) == Fraction(1)


@test("POLICY")
def t_splice_uses_range_midpoint_from_2008_12_16():
    lo = {dt.date(2008, 12, 16): Fraction(0)}
    hi = {dt.date(2008, 12, 16): Fraction(1, 4)}
    got = policy.spliced_target("2008-12-16", {}, lo, hi)
    assert got == Fraction(1, 8), got


@test("POLICY")
def t_splice_midpoint_is_exact_not_float():
    lo = {dt.date(2010, 1, 4): Fraction(0)}
    hi = {dt.date(2010, 1, 4): Fraction(1, 4)}
    got = policy.spliced_target("2010-01-04", {}, lo, hi)
    assert isinstance(got, Fraction) and got * 8 == 1


@test("POLICY")
def t_splice_single_target_ignored_after_boundary():
    single = {dt.date(2009, 1, 2): Fraction(99)}
    assert policy.spliced_target("2009-01-02", single, {}, {}) is UNDEFINED


@test("POLICY")
def t_splice_contiguity_rejects_overlap():
    expect_raises(ContractViolation, policy.assert_splice_contiguous,
                  [dt.date(2008, 12, 16)], [dt.date(2008, 12, 16)])


@test("POLICY")
def t_splice_contiguity_rejects_gap():
    expect_raises(ContractViolation, policy.assert_splice_contiguous,
                  [dt.date(2008, 12, 10)], [dt.date(2008, 12, 15)])


@test("POLICY")
def t_splice_contiguity_accepts_the_sealed_boundary():
    policy.assert_splice_contiguous([dt.date(2008, 12, 15)],
                                    [dt.date(2008, 12, 16)])


@test("POLICY")
def t_inverted_range_raises_rather_than_silently_averaging():
    lo = {dt.date(2010, 1, 4): Fraction(2)}
    hi = {dt.date(2010, 1, 4): Fraction(1)}
    expect_raises(ContractViolation, policy.spliced_target,
                  "2010-01-04", {}, lo, hi)


@test("POLICY")
def t_realtime_start_is_structurally_absent_from_the_policy_api():
    """The S1 audit finding cannot be reintroduced: no policy entry point
    accepts a realtime/vintage parameter at all."""
    forbidden = ("realtime", "vintage", "catalog")
    for name, obj in vars(policy).items():
        if not (inspect.isfunction(obj) or inspect.isclass(obj)):
            continue
        target = obj.__init__ if inspect.isclass(obj) else obj
        try:
            params = list(inspect.signature(target).parameters)
        except (TypeError, ValueError):
            continue
        for p in params:
            assert not any(f in p.lower() for f in forbidden), \
                "%s(%s) exposes a vintage-metadata parameter" % (name, p)


@test("POLICY")
def t_policy_metadata_regression_poisoned_catalog_stamp_changes_nothing():
    """Regression for the exact S1 defect.

    A synthetic DFEDTAR-shaped world where EVERY historical observation is
    stamped with a single late realtime_start -- the 2008-12-15 discontinuation
    artefact -- must produce byte-identical policy eligibility to an honest
    world, because the resolver reads announcements, not catalog stamps.
    """
    honest = {dt.date(1990, 1, 2): Fraction(8), dt.date(1995, 1, 3): Fraction(6)}
    schedule = policy.PolicySchedule([
        ann("1990-01-02", dt.time(14, 0), 8),
        ann("1995-01-03", dt.time(14, 0), 6)])
    before = [schedule.eligible(d) for d in
              ("1991-06-28", "1996-06-28", "2007-06-29")]

    # Now poison the catalog: pretend FRED stamped everything 2008-12-15.
    poisoned_obs = [{"date": d.isoformat(), "realtime_start": "2008-12-15",
                     "realtime_end": "9999-12-31", "value": str(v)}
                    for d, v in honest.items()]
    poisoned = VintageSeries("DFEDTAR", poisoned_obs)
    # The ALFRED view says NOTHING was public before 2008-12-15 ...
    assert poisoned.as_of("1991-06-28") == {}
    assert poisoned.as_of("2007-06-29") == {}
    # ... yet the policy leg is unaffected, because it never consults it.
    after = [schedule.eligible(d) for d in
             ("1991-06-28", "1996-06-28", "2007-06-29")]
    assert before == after == [Fraction(8), Fraction(6), Fraction(6)]


@test("POLICY")
def t_forbidden_policy_series_are_named_and_excluded():
    assert "DGS2" in policy.FORBIDDEN_POLICY_SERIES
    assert "FEDFUNDS" in policy.FORBIDDEN_POLICY_SERIES


# ===========================================================================
# GROUP 4 — PRIMITIVE MACRO LEGS
# ===========================================================================

def _growth_pair_case(si, sp, expected):
    newest = dt.date(2010, 1, 1)
    g = legs.growth_leg(flat_growth_snapshot(newest, si),
                        flat_growth_snapshot(newest, sp))
    assert g == expected, "(%d,%d) -> %r, expected %r" % (si, sp, g, expected)


for _si, _sp in legs.GROWTH_TRUTH_TABLE:
    def _mk(si=_si, sp=_sp):
        @test("LEGS")
        def fn():
            _growth_pair_case(si, sp, legs.GROWTH_TRUTH_TABLE[(si, sp)])
        fn.__name__ = "t_growth_pair_%s_%s" % (
            "neg" if si < 0 else ("zero" if si == 0 else "pos"),
            "neg" if sp < 0 else ("zero" if sp == 0 else "pos"))
        TESTS[-1] = ("LEGS", fn.__name__, TESTS[-1][2])
    _mk()


@test("LEGS")
def t_growth_truth_table_equals_sign_of_sign_sum():
    for (a, b), want in legs.GROWTH_TRUTH_TABLE.items():
        assert legs.sign(a + b) == want


@test("LEGS")
def t_growth_undefined_when_indpro_missing():
    newest = dt.date(2010, 1, 1)
    assert legs.growth_leg({}, flat_growth_snapshot(newest, 1)) is UNDEFINED


@test("LEGS")
def t_growth_undefined_when_payems_missing():
    newest = dt.date(2010, 1, 1)
    assert legs.growth_leg(flat_growth_snapshot(newest, 1), {}) is UNDEFINED


@test("LEGS")
def t_growth_undefined_when_the_exact_lag_is_absent():
    newest = dt.date(2010, 1, 1)
    snap = flat_growth_snapshot(newest, 1)
    del snap[months_back(newest, 12)]
    assert legs.growth_leg(snap, flat_growth_snapshot(newest, 1)) is UNDEFINED


@test("LEGS")
def t_growth_sign_is_exact_for_a_tiny_change():
    """No epsilon exists to swallow a small move; the contract forbids one."""
    newest = dt.date(2010, 1, 1)
    snap = {months_back(newest, k): Fraction(100) for k in range(13)}
    snap[newest] = Fraction(100) + Fraction(1, 10 ** 15)
    assert legs.growth_leg(snap, snap) == 1


@test("LEGS")
def t_inflation_leg_is_zero_when_the_rate_is_constant():
    newest = dt.date(2010, 1, 1)
    snap = {}
    for k in range(25):
        m = months_back(newest, k)
        snap[m] = Fraction(100) * (Fraction(102, 100) ** (24 - k))
    # constant 2% per month -> constant pi12 -> change in rate is ZERO
    assert legs.inflation_leg(snap) == 0


@test("LEGS")
def t_inflation_leg_is_the_change_in_the_rate_not_the_rate():
    """Discriminating: a steadily rising index has pi12 > 0 in every month,
    yet the sealed leg reads the CHANGE in that rate and must be 0."""
    newest = dt.date(2010, 1, 1)
    snap = {months_back(newest, k): Fraction(100 + (24 - k)) for k in range(25)}
    # index rises by a constant 1 unit/month; pi12 DECELERATES on a ratio basis
    assert legs.inflation_leg(snap) == -1


def _two_regime_cpi(old_rate, new_rate):
    """25 months: the oldest 12 grow at ``old_rate``, the newest 12 at
    ``new_rate``. pi12(m) then reads the new regime and pi12(m-12) the old."""
    newest = dt.date(2010, 1, 1)
    level = Fraction(100)
    snap = {months_back(newest, 24): level}
    for step in range(1, 25):
        rate = old_rate if step <= 12 else new_rate
        level = level * (1 + rate)
        snap[months_back(newest, 24 - step)] = level
    return snap


@test("LEGS")
def t_inflation_leg_positive_when_the_rate_accelerates():
    snap = _two_regime_cpi(Fraction(1, 1000), Fraction(3, 1000))
    assert legs.inflation_leg(snap) == 1


@test("LEGS")
def t_inflation_leg_negative_when_the_rate_decelerates():
    snap = _two_regime_cpi(Fraction(3, 1000), Fraction(1, 1000))
    assert legs.inflation_leg(snap) == -1


@test("LEGS")
def t_inflation_undefined_with_only_24_months():
    newest = dt.date(2010, 1, 1)
    snap = {months_back(newest, k): Fraction(100 + k) for k in range(24)}
    assert legs.inflation_leg(snap) is UNDEFINED


@test("LEGS")
def t_inflation_defined_with_25_months():
    newest = dt.date(2010, 1, 1)
    snap = {months_back(newest, k): Fraction(100 + (24 - k)) for k in range(25)}
    assert legs.inflation_leg(snap) is not UNDEFINED


@test("LEGS")
def t_inflation_zero_base_raises_rather_than_dividing():
    newest = dt.date(2010, 1, 1)
    snap = {months_back(newest, k): Fraction(100) for k in range(25)}
    snap[months_back(newest, 12)] = Fraction(0)
    expect_raises(ContractViolation, legs.inflation_leg, snap)


@test("LEGS")
def t_policy_leg_three_states():
    assert legs.policy_leg(Fraction(2), Fraction(1)) == 1
    assert legs.policy_leg(Fraction(1), Fraction(2)) == -1
    assert legs.policy_leg(Fraction(1), Fraction(1)) == 0


@test("LEGS")
def t_policy_leg_undefined_when_either_side_missing():
    assert legs.policy_leg(UNDEFINED, Fraction(1)) is UNDEFINED
    assert legs.policy_leg(Fraction(1), UNDEFINED) is UNDEFINED


@test("LEGS")
def t_sign_zero_is_zero_uniformly():
    assert legs.sign(0) == 0
    assert legs.sign(Fraction(0)) == 0
    assert legs.sign(Fraction(0, 5)) == 0


@test("LEGS")
def t_sign_refuses_undefined_rather_than_coercing_it():
    expect_raises(ContractViolation, legs.sign, UNDEFINED)


@test("LEGS")
def t_only_twelve_month_lookback_exists():
    assert legs.LOOKBACK_MONTHS == 12
    assert legs.GROWTH_MONTHS_REQUIRED == 13
    assert legs.INFLATION_MONTHS_REQUIRED == 25


@test("LEGS")
def t_forbidden_inflation_series_named():
    assert legs.INFLATION_SERIES == "CPILFENS"
    assert legs.FORBIDDEN_INFLATION_SERIES == {"CPIAUCSL", "CPILFESL", "PCEPILFE"}


# ===========================================================================
# GROUP 5 — COEFFICIENT TABLE, DOMAIN, VOTE SEMANTICS
# ===========================================================================

ALL_STATES = [(g, i, p) for g in (-1, 0, 1) for i in (-1, 0, 1)
              for p in (-1, 0, 1)]


@test("VOTES")
def t_exactly_fifteen_mapped_instruments():
    assert len(votes.MAPPED) == 15


@test("VOTES")
def t_mapped_is_canonical_17_minus_real_estate():
    assert votes.MAPPED == votes.CANONICAL_17 - votes.NOT_MAPPED
    assert votes.NOT_MAPPED == {"VNQ", "RWX"}


@test("VOTES")
def t_vnq_is_not_in_the_signal_domain():
    assert "VNQ" not in votes.MAPPED
    expect_raises(votes.NotInDomain, votes.raw_direction, "VNQ", 1, 1, 1)


@test("VOTES")
def t_rwx_is_not_in_the_signal_domain():
    assert "RWX" not in votes.MAPPED
    expect_raises(votes.NotInDomain, votes.raw_direction, "RWX", 1, 1, 1)


@test("VOTES")
def t_unmapped_never_returns_zero_or_undefined():
    for inst in ("VNQ", "RWX"):
        try:
            votes.raw_direction(inst, 0, 0, 0)
        except votes.NotInDomain:
            continue
        raise AssertionError("%s returned a value instead of raising" % inst)


@test("VOTES")
def t_all_coefficients_are_ternary():
    vals = {v for c in votes.COEFFICIENTS.values() for v in c}
    assert vals <= {-1, 0, 1}, vals
    assert sum(len(c) for c in votes.COEFFICIENTS.values()) == 45


@test("VOTES")
def t_coefficient_table_is_read_only():
    try:
        votes.COEFFICIENTS["SPY"] = (0, 0, 0)
    except TypeError:
        return
    raise AssertionError("the sealed coefficient table is mutable")


@test("VOTES")
def t_equity_class_row_is_exactly_the_sealed_triple():
    for inst in ("SPY", "EEM", "EWJ", "XLE", "XLU"):
        assert votes.COEFFICIENTS[inst] == (1, 0, -1)


@test("VOTES")
def t_duration_credit_commodity_dollar_rows_are_sealed():
    assert votes.COEFFICIENTS["TLT"] == (-1, -1, -1)
    assert votes.COEFFICIENTS["SHY"] == (-1, -1, -1)
    assert votes.COEFFICIENTS["LQD"] == (1, 0, 0)
    assert votes.COEFFICIENTS["HYG"] == (1, 0, 0)
    for inst in ("USO", "UNG", "GLD", "DBA"):
        assert votes.COEFFICIENTS[inst] == (0, 1, 0)
    assert votes.COEFFICIENTS["UUP"] == (0, 1, 1)
    assert votes.COEFFICIENTS["FXY"] == (0, -1, -1)


@test("VOTES")
def t_all_27_states_produce_ternary_directions():
    seen = set()
    for s in ALL_STATES:
        row = votes.direction_row(*s)
        assert len(row) == 15
        assert set(row.values()) <= {-1, 0, 1}
        seen.add(s)
    assert len(seen) == 27


@test("VOTES")
def t_fxy_is_exactly_negative_uup_in_all_27_states():
    for s in ALL_STATES:
        assert votes.raw_direction("FXY", *s) == -votes.raw_direction("UUP", *s)


@test("VOTES")
def t_xle_equals_xlu_in_all_27_states():
    for s in ALL_STATES:
        assert votes.raw_direction("XLE", *s) == votes.raw_direction("XLU", *s)


@test("VOTES")
def t_all_five_equity_instruments_agree_in_all_27_states():
    for s in ALL_STATES:
        vals = {votes.raw_direction(i, *s)
                for i in ("SPY", "EEM", "EWJ", "XLE", "XLU")}
        assert len(vals) == 1, (s, vals)


@test("VOTES")
def t_credit_equals_growth_in_all_27_states():
    for g, i, p in ALL_STATES:
        assert votes.raw_direction("LQD", g, i, p) == g
        assert votes.raw_direction("HYG", g, i, p) == g


@test("VOTES")
def t_commodities_equal_inflation_in_all_27_states():
    for g, i, p in ALL_STATES:
        for inst in ("USO", "UNG", "GLD", "DBA"):
            assert votes.raw_direction(inst, g, i, p) == i


@test("VOTES")
def t_tlt_equals_shy_in_all_27_states():
    for s in ALL_STATES:
        assert votes.raw_direction("TLT", *s) == votes.raw_direction("SHY", *s)


@test("VOTES")
def t_equity_equals_sign_g_minus_p_in_all_27_states():
    for g, i, p in ALL_STATES:
        assert votes.raw_direction("XLE", g, i, p) == legs.sign(g - p)


@test("VOTES")
def t_uup_equals_sign_i_plus_p_in_all_27_states():
    for g, i, p in ALL_STATES:
        assert votes.raw_direction("UUP", g, i, p) == legs.sign(i + p)


@test("VOTES")
def t_tie_resolves_to_flat_with_no_priority_theme():
    # TLT = (-1,-1,-1): G=+1, I=-1, P=0 -> -1 +1 + 0 = 0 -> flat
    assert votes.raw_direction("TLT", 1, -1, 0) == 0
    # equity = (+1,0,-1): G=+1, P=+1 -> 1 - 1 = 0 -> flat
    assert votes.raw_direction("SPY", 1, 0, 1) == 0


@test("VOTES")
def t_zero_leg_abstains_and_never_vetoes():
    # TLT loads on all three; a silent growth leg must not force flat.
    assert votes.raw_direction("TLT", 0, 1, 1) == -1
    assert votes.raw_direction("TLT", 0, -1, -1) == 1


@test("VOTES")
def t_missing_unrelated_leg_does_not_undefine_the_instrument():
    # HYG depends only on G. Missing I and P must be irrelevant.
    assert votes.raw_direction("HYG", 1, UNDEFINED, UNDEFINED) == 1
    assert votes.raw_direction("LQD", -1, UNDEFINED, UNDEFINED) == -1
    assert votes.raw_direction("GLD", UNDEFINED, 1, UNDEFINED) == 1
    assert votes.raw_direction("SPY", 1, UNDEFINED, -1) == 1


@test("VOTES")
def t_missing_required_leg_undefines_the_instrument():
    assert votes.raw_direction("HYG", UNDEFINED, 1, 1) is UNDEFINED
    assert votes.raw_direction("GLD", 1, UNDEFINED, 1) is UNDEFINED
    assert votes.raw_direction("SPY", 1, 1, UNDEFINED) is UNDEFINED
    assert votes.raw_direction("TLT", UNDEFINED, 1, 1) is UNDEFINED


@test("VOTES")
def t_missing_is_never_converted_to_zero():
    for inst in sorted(votes.MAPPED):
        for legidx, name in enumerate(("G", "I", "P")):
            state = [0, 0, 0]
            state[legidx] = UNDEFINED
            got = votes.raw_direction(inst, *state)
            if name in votes.required_legs(inst):
                assert got is UNDEFINED, (inst, name, got)
            else:
                assert got == 0, (inst, name, got)


@test("VOTES")
def t_required_legs_are_dependency_sensitive():
    assert votes.required_legs("HYG") == ("G",)
    assert votes.required_legs("GLD") == ("I",)
    assert votes.required_legs("SPY") == ("G", "P")
    assert votes.required_legs("TLT") == ("G", "I", "P")
    assert votes.required_legs("UUP") == ("I", "P")


@test("VOTES")
def t_assert_domain_rejects_real_estate():
    expect_raises(ContractViolation, votes.assert_domain,
                  sorted(votes.MAPPED) + ["VNQ"])


@test("VOTES")
def t_assert_domain_rejects_a_short_domain():
    expect_raises(ContractViolation, votes.assert_domain,
                  sorted(votes.MAPPED)[:14])


@test("VOTES")
def t_assert_domain_accepts_exactly_the_fifteen():
    votes.assert_domain(votes.MAPPED)


# ===========================================================================
# GROUP 6 — GATE 0.5
# ===========================================================================

def _cells(n_agree, n_total, instrument="SPY"):
    mmv, tsm = {}, {}
    for k in range(n_total):
        key = (dt.date(2000, 1, 1) + dt.timedelta(days=k), instrument)
        mmv[key] = 1
        tsm[key] = 1 if k < n_agree else -1
    return mmv, tsm


@test("GATE05")
def t_gate05_79_of_100_passes():
    o = gate05.evaluate(*_cells(79, 100))
    assert o.eligible_cells == 100 and o.agreement_cells == 79
    assert o.kill is False


@test("GATE05")
def t_gate05_799_of_1000_passes():
    o = gate05.evaluate(*_cells(799, 1000))
    assert o.kill is False and o.pooled_agreement == Fraction(799, 1000)


@test("GATE05")
def t_gate05_80_of_100_kills_inclusive():
    o = gate05.evaluate(*_cells(80, 100))
    assert o.kill is True and o.pooled_agreement == Fraction(4, 5)


@test("GATE05")
def t_gate05_800_of_1000_kills_inclusive():
    o = gate05.evaluate(*_cells(800, 1000))
    assert o.kill is True


@test("GATE05")
def t_gate05_81_of_100_kills():
    assert gate05.evaluate(*_cells(81, 100)).kill is True


@test("GATE05")
def t_gate05_threshold_is_exact_rational_not_float():
    o = gate05.evaluate(*_cells(80, 100))
    assert isinstance(o.pooled_agreement, Fraction)
    assert gate05.KILL_THRESHOLD == Fraction(4, 5)
    assert gate05.kills(4, 5) and gate05.kills(400, 500)
    assert not gate05.kills(3999, 5000)


@test("GATE05")
def t_gate05_zero_versus_zero_is_agreement():
    key = (dt.date(2000, 1, 31), "SPY")
    o = gate05.evaluate({key: 0}, {key: 0})
    assert o.eligible_cells == 1 and o.agreement_cells == 1


@test("GATE05")
def t_gate05_zero_versus_nonzero_is_disagreement():
    for other in (1, -1):
        key = (dt.date(2000, 1, 31), "SPY")
        o = gate05.evaluate({key: 0}, {key: other})
        assert o.eligible_cells == 1 and o.agreement_cells == 0


@test("GATE05")
def t_gate05_zeros_are_never_discarded():
    keys = [(dt.date(2000, 1, 31), i) for i in ("SPY", "GLD", "TLT")]
    o = gate05.evaluate({k: 0 for k in keys}, {k: 0 for k in keys})
    assert o.eligible_cells == 3, "zero cells were dropped from the denominator"


@test("GATE05")
def t_gate05_excludes_undefined_mmv_cells():
    a = (dt.date(2000, 1, 31), "SPY")
    b = (dt.date(2000, 2, 29), "SPY")
    o = gate05.evaluate({a: 1, b: UNDEFINED}, {a: 1, b: 1})
    assert o.eligible_cells == 1 and o.excluded_mmv_undefined == 1


@test("GATE05")
def t_gate05_excludes_undefined_tsmom_cells():
    a = (dt.date(2000, 1, 31), "SPY")
    b = (dt.date(2000, 2, 29), "SPY")
    o = gate05.evaluate({a: 1, b: 1}, {a: 1, b: UNDEFINED})
    assert o.eligible_cells == 1 and o.excluded_tsmom_undefined == 1


@test("GATE05")
def t_gate05_excludes_unmapped_from_numerator_and_denominator():
    d = dt.date(2000, 1, 31)
    mmv = {(d, "SPY"): 1, (d, "VNQ"): 1, (d, "RWX"): 1}
    tsm = {(d, "SPY"): 1, (d, "VNQ"): 1, (d, "RWX"): 1}
    o = gate05.evaluate(mmv, tsm)
    assert o.eligible_cells == 1, "unmapped cells entered the denominator"
    assert o.agreement_cells == 1, "unmapped cells entered the numerator"
    assert o.excluded_unmapped == 2


@test("GATE05")
def t_gate05_unmapped_cannot_push_agreement_down():
    """The artefact the contract exists to prevent, demonstrated.

    If VNQ/RWX were coded as signal 0 while TSMOM is active, they would inject
    disagreement every month -- the direction that helps MMV survive the kill.
    """
    d0 = dt.date(2000, 1, 31)
    mmv, tsm = {}, {}
    for k in range(10):
        d = d0 + dt.timedelta(days=k)
        mmv[(d, "SPY")] = 1
        tsm[(d, "SPY")] = 1
    correct = gate05.evaluate(dict(mmv), dict(tsm))
    for k in range(10):
        d = d0 + dt.timedelta(days=k)
        mmv[(d, "VNQ")] = 0
        tsm[(d, "VNQ")] = 1
    with_artefact = gate05.evaluate(mmv, tsm)
    assert correct.pooled_agreement == Fraction(1, 1)
    assert with_artefact.pooled_agreement == Fraction(1, 1), \
        "unmapped real estate changed the pooled rate"


@test("GATE05")
def t_gate05_per_instrument_cannot_override_pooled():
    d0 = dt.date(2000, 1, 31)
    mmv, tsm = {}, {}
    for k in range(100):
        d = d0 + dt.timedelta(days=k)
        mmv[(d, "SPY")] = 1
        tsm[(d, "SPY")] = 1                       # SPY agrees 100%
        mmv[(d, "GLD")] = 1
        tsm[(d, "GLD")] = -1                      # GLD agrees 0%
    o = gate05.evaluate(mmv, tsm)
    per = gate05.per_instrument_agreement(mmv, tsm)
    assert per["SPY"] == (100, 100) and per["GLD"] == (0, 100)
    assert o.pooled_agreement == Fraction(1, 2) and o.kill is False
    assert not hasattr(o, "per_instrument")
    for value in per.values():
        assert isinstance(value, tuple) and len(value) == 2, \
            "per-instrument diagnostic returned a verdict, not counts"


@test("GATE05")
def t_gate05_outcome_exposes_no_rescue_field():
    o = gate05.evaluate(*_cells(50, 100))
    assert set(o._fields) == {
        "eligible_cells", "agreement_cells", "pooled_agreement", "kill",
        "excluded_unmapped", "excluded_mmv_undefined", "excluded_tsmom_undefined"}


@test("GATE05")
def t_gate05_empty_denominator_raises_rather_than_passing():
    a = (dt.date(2000, 1, 31), "SPY")
    expect_raises(ContractViolation, gate05.evaluate, {a: UNDEFINED}, {a: 1})


@test("GATE05")
def t_gate05_rejects_a_non_ternary_sign():
    a = (dt.date(2000, 1, 31), "SPY")
    expect_raises(ContractViolation, gate05.evaluate, {a: 0.5}, {a: 1})


@test("GATE05")
def t_gate05_takes_the_union_of_both_key_sets():
    a = (dt.date(2000, 1, 31), "SPY")
    b = (dt.date(2000, 2, 29), "SPY")
    o = gate05.evaluate({a: 1}, {a: 1, b: 1})
    assert o.eligible_cells == 1 and o.excluded_mmv_undefined == 1


@test("GATE05")
def t_gate05_guard_rejects_unmapped_cells_when_asked():
    expect_raises(ContractViolation, gate05.assert_no_unmapped,
                  [(dt.date(2000, 1, 31), "VNQ")])


# ===========================================================================
# GROUP 7 — FIRST-RELEASE DIAGNOSTIC
# ===========================================================================

@test("CONCORD")
def t_concordance_module_defines_no_threshold():
    src = open(os.path.join(ENGINE, "concordance.py"), encoding="utf-8").read()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for tgt in node.targets:
                if isinstance(tgt, ast.Name):
                    name = tgt.id.lower()
                    assert "threshold" not in name or name == "no_threshold_exists"
                    assert "kill" not in name and "promote" not in name


@test("CONCORD")
def t_concordance_report_has_no_verdict_field():
    r = concordance.compare({}, {})
    for f in r._fields:
        assert not any(w in f.lower() for w in
                       ("kill", "pass", "fail", "promote", "rescue", "verdict"))


@test("CONCORD")
def t_concordance_counts_disagreement():
    d0 = dt.date(2000, 1, 31)
    a, b = {}, {}
    for k in range(10):
        key = (d0 + dt.timedelta(days=k), "SPY")
        a[key] = 1
        b[key] = 1 if k < 7 else -1
    r = concordance.compare(a, b)
    assert r.compared_cells == 10 and r.disagreement_cells == 3
    assert r.disagreement_rate == Fraction(3, 10)


@test("CONCORD")
def t_concordance_excludes_undefined_on_either_side():
    a = (dt.date(2000, 1, 31), "SPY")
    b = (dt.date(2000, 2, 29), "SPY")
    r = concordance.compare({a: 1, b: UNDEFINED}, {a: 1, b: 1})
    assert r.compared_cells == 1


@test("CONCORD")
def t_concordance_excludes_unmapped():
    d = dt.date(2000, 1, 31)
    r = concordance.compare({(d, "VNQ"): 1}, {(d, "VNQ"): -1})
    assert r.compared_cells == 0


@test("CONCORD")
def t_concordance_reports_by_leg():
    a = {dt.date(2000, 1, 31): {"G": 1, "I": 1, "P": 0}}
    b = {dt.date(2000, 1, 31): {"G": -1, "I": 1, "P": 0}}
    out = concordance.compare_legs(a, b)
    assert out["G"] == (1, 1) and out["I"] == (0, 1) and out["P"] == (0, 1)


@test("CONCORD")
def t_concordance_exposes_no_callable_that_returns_a_verdict():
    for name, obj in vars(concordance).items():
        if inspect.isfunction(obj) and obj.__module__ == concordance.__name__:
            assert not any(w in name.lower() for w in
                           ("kill", "gate", "promote", "rescue", "decide"))


# ===========================================================================
# GROUP 8 — CANONICAL RISK WRAPPER INTEGRATION
# ===========================================================================

def _synthetic_prices(n_days=800, instruments=None):
    cols = sorted(instruments or votes.MAPPED)
    idx = pd.bdate_range("2015-01-01", periods=n_days)
    rng = np.random.default_rng(20260917)
    steps = rng.normal(0.0002, 0.01, size=(n_days, len(cols)))
    px = 100 * np.exp(np.cumsum(steps, axis=0))
    return pd.DataFrame(px, index=idx, columns=cols)


@test("RISK")
def t_wrapper_parameters_match_canonical_config():
    for key, want in risk.WRAPPER_AUTHORITY.items():
        assert getattr(config, key) == want, (key, getattr(config, key), want)


@test("RISK")
def t_cost_traces_to_canonical_config():
    assert risk.ONE_WAY_COST_BPS == config.TRANSACTION_COST_BPS == 2.0


@test("RISK")
def t_signal_frame_has_exactly_fifteen_columns():
    d = dt.date(2020, 1, 31)
    raw = {(d, i): 1 for i in votes.MAPPED}
    f = risk.signal_frame(raw)
    assert list(f.columns) == sorted(votes.MAPPED) and f.shape[1] == 15


@test("RISK")
def t_signal_frame_rejects_real_estate_columns():
    d = dt.date(2020, 1, 31)
    raw = {(d, i): 1 for i in votes.MAPPED}
    raw[(d, "VNQ")] = 0
    expect_raises(ContractViolation, risk.signal_frame, raw)


@test("RISK")
def t_signal_frame_maps_undefined_to_nan_not_zero():
    d = dt.date(2020, 1, 31)
    raw = {(d, i): 1 for i in votes.MAPPED}
    raw[(d, "GLD")] = UNDEFINED
    f = risk.signal_frame(raw)
    assert pd.isna(f.loc[pd.Timestamp(d), "GLD"])
    assert f.loc[pd.Timestamp(d), "SPY"] == 1.0


@test("RISK")
def t_flat_signal_is_zero_and_stays_live():
    d = dt.date(2020, 1, 31)
    raw = {(d, i): 0 for i in votes.MAPPED}
    f = risk.signal_frame(raw)
    assert (f.loc[pd.Timestamp(d)] == 0).all()
    _base, n_live = canonical_portfolio.equal_weight_aggregate(
        f.astype("float64"))
    assert int(n_live.iloc[0]) == 15


@test("RISK")
def t_undefined_cells_leave_the_live_count():
    d = dt.date(2020, 1, 31)
    raw = {(d, i): 1 for i in votes.MAPPED}
    raw[(d, "GLD")] = UNDEFINED
    raw[(d, "UNG")] = UNDEFINED
    f = risk.signal_frame(raw)
    _base, n_live = canonical_portfolio.equal_weight_aggregate(f)
    assert int(n_live.iloc[0]) == 13


@test("RISK")
def t_unmapped_zero_columns_would_dilute_the_book():
    """Demonstrates WHY VNQ/RWX must be absent rather than zero.

    This test asserts the canonical wrapper's behaviour, not MMV's: a zero
    (non-NaN) column counts as a live asset and shrinks every real weight.
    """
    d = pd.Timestamp("2020-01-31")
    cols15 = sorted(votes.MAPPED)
    w15 = pd.DataFrame([[1.0] * 15], index=[d], columns=cols15)
    base15, live15 = canonical_portfolio.equal_weight_aggregate(w15)
    w17 = w15.copy()
    w17["VNQ"] = 0.0
    w17["RWX"] = 0.0
    base17, live17 = canonical_portfolio.equal_weight_aggregate(w17)
    assert int(live15.iloc[0]) == 15 and int(live17.iloc[0]) == 17
    assert base15.loc[d, "SPY"] > base17.loc[d, "SPY"], \
        "unmapped real estate failed to dilute, so this guard is vacuous"
    assert abs(base17.loc[d, "SPY"] / base15.loc[d, "SPY"] - 15 / 17) < 1e-12


@test("RISK")
def t_assert_no_dilution_rejects_a_seventeen_column_frame():
    d = pd.Timestamp("2020-01-31")
    f = pd.DataFrame([[1.0] * 15], index=[d], columns=sorted(votes.MAPPED))
    f["VNQ"] = 0.0
    expect_raises(ContractViolation, risk.assert_no_dilution, f)


@test("RISK")
def t_build_runs_end_to_end_on_synthetic_prices():
    px = _synthetic_prices()
    month_ends = px.resample(config.SIGNAL_RESAMPLE).last().index
    rng = np.random.default_rng(7)
    sig = pd.DataFrame(
        rng.choice([-1.0, 0.0, 1.0], size=(len(month_ends), 15)),
        index=month_ends, columns=sorted(votes.MAPPED))
    out = risk.build(px, sig)
    assert set(out) >= {"asset_weight", "base_weight", "leverage",
                        "port_weight", "position", "turnover"}
    assert out["port_weight"].shape[1] == 15
    live = out["n_live"].dropna()
    assert (live <= 15).all(), "live asset count exceeded the MMV domain"


@test("RISK")
def t_build_respects_the_asset_weight_cap():
    px = _synthetic_prices()
    month_ends = px.resample(config.SIGNAL_RESAMPLE).last().index
    sig = pd.DataFrame(1.0, index=month_ends, columns=sorted(votes.MAPPED))
    out = risk.build(px, sig)
    w = out["asset_weight"].abs().max().max()
    assert w <= config.MAX_ASSET_WEIGHT + 1e-12, w


@test("RISK")
def t_build_respects_the_gross_leverage_cap():
    px = _synthetic_prices()
    month_ends = px.resample(config.SIGNAL_RESAMPLE).last().index
    sig = pd.DataFrame(1.0, index=month_ends, columns=sorted(votes.MAPPED))
    out = risk.build(px, sig)
    gross = out["port_weight"].abs().sum(axis=1).dropna()
    assert (gross <= config.MAX_GROSS_LEVERAGE + 1e-9).all(), gross.max()


@test("RISK")
def t_position_is_the_prior_decision_no_same_bar_lookahead():
    d = pd.date_range("2020-01-31", periods=4, freq=config.SIGNAL_RESAMPLE)
    w = pd.DataFrame([[1.0] * 15, [2.0] * 15, [3.0] * 15, [4.0] * 15],
                     index=d, columns=sorted(votes.MAPPED))
    held = canonical_portfolio.positions_from_weights(w)
    assert pd.isna(held.iloc[0, 0])
    assert held.iloc[1, 0] == 1.0 and held.iloc[3, 0] == 3.0


@test("RISK")
def t_cost_is_two_bps_of_turnover():
    d = pd.date_range("2020-01-31", periods=2, freq=config.SIGNAL_RESAMPLE)
    w = pd.DataFrame([[0.0] * 15, [1.0] * 15], index=d,
                     columns=sorted(votes.MAPPED))
    c = risk.cost_series(w)
    assert abs(float(c.iloc[1]) - 15 * 2.0 / 1e4) < 1e-15


@test("RISK")
def t_turnover_treats_a_flat_month_as_a_real_position():
    d = pd.date_range("2020-01-31", periods=2, freq=config.SIGNAL_RESAMPLE)
    w = pd.DataFrame([[1.0] * 15, [0.0] * 15], index=d,
                     columns=sorted(votes.MAPPED))
    assert float(risk.turnover(w).iloc[1]) == 15.0


# ===========================================================================
# GROUP 9 — STRUCTURAL START RULE
# ===========================================================================

def _start_world(n_growth=20, n_cpi=30, with_policy=True):
    ind = linear_series("INDPRO", 2000, n_growth, 100, 1, "2000-01-01")
    pay = linear_series("PAYEMS", 2000, n_growth, 100, 1, "2000-01-01")
    cpi = linear_series("CPILFENS", 2000, n_cpi, 100, 1, "2000-01-01")
    sched = policy.PolicySchedule(
        [ann("1990-01-02", dt.time(14, 0), 5)] if with_policy else [])
    return ind, pay, cpi, sched


@test("START")
def t_start_excludes_a_date_with_insufficient_growth_history():
    ind, pay, cpi, sched = _start_world(n_growth=12, n_cpi=30)
    t = dt.date(2010, 1, 31)
    r = startmod.evaluate_date(t, canonical_month_ends=[t], indpro=ind,
                               payems=pay, cpi=cpi, policy_schedule=sched,
                               priced_instruments=votes.MAPPED)
    assert not r.eligible and r.reason == "insufficient_growth_history"


@test("START")
def t_start_excludes_a_date_with_insufficient_inflation_history():
    ind, pay, cpi, sched = _start_world(n_growth=20, n_cpi=24)
    t = dt.date(2010, 1, 31)
    r = startmod.evaluate_date(t, canonical_month_ends=[t], indpro=ind,
                               payems=pay, cpi=cpi, policy_schedule=sched,
                               priced_instruments=votes.MAPPED)
    assert not r.eligible and r.reason == "insufficient_inflation_history"


@test("START")
def t_start_admits_the_first_fully_eligible_date():
    ind, pay, cpi, sched = _start_world()
    t = dt.date(2010, 1, 31)
    r = startmod.evaluate_date(t, canonical_month_ends=[t], indpro=ind,
                               payems=pay, cpi=cpi, policy_schedule=sched,
                               priced_instruments=votes.MAPPED)
    assert r.eligible and r.reason is None


@test("START")
def t_start_excludes_a_date_with_no_announced_policy_target():
    ind, pay, cpi, sched = _start_world(with_policy=False)
    t = dt.date(2010, 1, 31)
    r = startmod.evaluate_date(t, canonical_month_ends=[t], indpro=ind,
                               payems=pay, cpi=cpi, policy_schedule=sched,
                               priced_instruments=votes.MAPPED)
    assert not r.eligible and r.reason == "no_announced_policy_target"


@test("START")
def t_start_excludes_a_non_canonical_date():
    ind, pay, cpi, sched = _start_world()
    r = startmod.evaluate_date(dt.date(2010, 1, 15), canonical_month_ends=[],
                               indpro=ind, payems=pay, cpi=cpi,
                               policy_schedule=sched,
                               priced_instruments=votes.MAPPED)
    assert not r.eligible and r.reason == "not_canonical_month_end"


@test("START")
def t_start_excludes_a_date_with_no_eligible_vintage():
    ind = linear_series("INDPRO", 2000, 20, 100, 1, "2099-01-01")
    _i, pay, cpi, sched = _start_world()
    t = dt.date(2010, 1, 31)
    r = startmod.evaluate_date(t, canonical_month_ends=[t], indpro=ind,
                               payems=pay, cpi=cpi, policy_schedule=sched,
                               priced_instruments=votes.MAPPED)
    assert not r.eligible and r.reason == "no_eligible_growth_vintage"


@test("START")
def t_start_summary_counts_every_exclusion():
    rows = [startmod.Eligibility(dt.date(2010, 1, 31), True, None),
            startmod.Eligibility(dt.date(2010, 2, 28), False,
                                 "insufficient_growth_history"),
            startmod.Eligibility(dt.date(2010, 3, 31), False,
                                 "no_announced_policy_target")]
    s = startmod.summarise(rows)
    assert s["eligible"] == 1
    assert s["insufficient_growth_history"] == 1
    assert sum(s.values()) == 3


# ===========================================================================
# GROUP 10 — OUTCOME FIREWALL
# ===========================================================================

FORBIDDEN_OUTPUT = ("result", "backtest", "sharpe", "bootstrap", "pnl",
                    "separab", "outcome", "agreement")


@test("FIREWALL")
def t_no_mmv_output_artifact_exists():
    found = []
    for root, dirs, files in os.walk(MMV):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for f in files:
            if f.endswith((".csv", ".parquet", ".pkl", ".npy")):
                found.append(os.path.join(root, f))
            elif f.endswith(".json") and "MANIFEST" not in f.upper():
                found.append(os.path.join(root, f))
    assert not found, "MMV data artifact exists: %s" % found


@test("FIREWALL")
def t_no_historical_signal_or_position_file_exists():
    for p in ("data/mmv/MMV_SIGNAL_PANEL.csv", "data/mmv/MMV_POSITIONS.csv",
              "data/mmv/MMV_GATE05.json", MMV + "/s3"):
        assert not os.path.exists(p), p


@test("FIREWALL")
def t_engine_modules_read_no_data_at_import():
    """Importing the engine must not touch the frozen macro bytes."""
    for mod in sorted(os.listdir(ENGINE)):
        if not mod.endswith(".py"):
            continue
        tree = ast.parse(open(os.path.join(ENGINE, mod), encoding="utf-8").read())
        for node in tree.body:                      # module level only
            assert not isinstance(node, (ast.For, ast.While, ast.With)), \
                "%s executes control flow at import" % mod
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                fn = node.value.func
                name = getattr(fn, "id", getattr(fn, "attr", ""))
                assert name not in ("open", "read", "load", "read_csv"), \
                    "%s reads at import" % mod


@test("FIREWALL")
def t_no_engine_module_hardcodes_the_frozen_data_directory():
    for mod in sorted(os.listdir(ENGINE)):
        if not mod.endswith(".py"):
            continue
        src = open(os.path.join(ENGINE, mod), encoding="utf-8").read()
        code = "\n".join(l for l in src.splitlines()
                         if not l.strip().startswith("#"))
        assert "data/mmv" not in code, "%s references the frozen data dir" % mod


@test("FIREWALL")
def t_engine_defines_no_pnl_sharpe_or_bootstrap_function():
    for mod in sorted(os.listdir(ENGINE)):
        if not mod.endswith(".py"):
            continue
        tree = ast.parse(open(os.path.join(ENGINE, mod), encoding="utf-8").read())
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                n = node.name.lower()
                for w in ("sharpe", "bootstrap", "pnl", "backtest", "promote"):
                    assert w not in n, "%s defines %s()" % (mod, node.name)


#: Paths no S2 build file may actually READ. Naming one in prose is fine and
#: sometimes necessary -- the sealed FOMC freeze has to explain that it derived
#: the six collisions from the canonical panel. Substring matching cannot tell
#: an explanation from an access, so these checks parse the call sites instead.
FORBIDDEN_READS = ("data/mmv", "close_prices_raw", "monthly_signal_panel")

READ_CALLS = {"open", "read_csv", "read_json", "read_parquet", "load", "loads",
              "read_text", "read_bytes"}


def opened_literals(src: str):
    """String literals passed to a file-reading call, at any nesting depth."""
    out = []
    for node in ast.walk(ast.parse(src)):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        name = getattr(fn, "id", None) or getattr(fn, "attr", None)
        if name not in READ_CALLS:
            continue
        for arg in ast.walk(node):
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                out.append(arg.value)
    return out


@test("FIREWALL")
def t_validator_itself_never_opens_the_frozen_macro_files():
    src = open(os.path.abspath(__file__), encoding="utf-8").read()
    for literal in opened_literals(src):
        for bad in FORBIDDEN_READS:
            assert bad not in literal, "validator opens %r" % literal


@test("FIREWALL")
def t_no_s2_build_file_reads_the_canonical_panel_or_frozen_macro_data():
    checked = 0
    for root, dirs, files in os.walk(MMV):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for f in files:
            if not f.endswith(".py"):
                continue
            path = os.path.join(root, f)
            if f in ("mmv_preseal_check.py", "mmv_data_freeze.py",
                     "mmv_fomc_timing_freeze.py"):
                continue                     # sealed S1 artifacts, pinned
            checked += 1
            for literal in opened_literals(open(path, encoding="utf-8").read()):
                for bad in FORBIDDEN_READS:
                    assert bad not in literal, "%s opens %r" % (path, literal)
    assert checked >= 9, "expected the engine plus the validator, saw %d" % checked


@test("FIREWALL")
def t_the_read_guard_is_not_vacuous():
    """The guard above must actually catch a read. Prove it on a sample."""
    caught = opened_literals("import json\njson.load(open('data/mmv/x.json'))\n")
    assert any("data/mmv" in c for c in caught), caught
    assert not opened_literals("x = 'data/mmv is only mentioned here'\n")


@test("FIREWALL")
def t_engine_imports_no_forbidden_series_identifier():
    banned = {"CPIAUCSL", "CPILFESL", "PCEPILFE", "DGS2", "FEDFUNDS"}
    for mod in sorted(os.listdir(ENGINE)):
        if not mod.endswith(".py"):
            continue
        src = open(os.path.join(ENGINE, mod), encoding="utf-8").read()
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                if node.value in banned:
                    # allowed ONLY inside the explicit forbidden-set constants
                    assert mod in ("legs.py", "policy.py"), \
                        "%s embeds forbidden series %s" % (mod, node.value)


# ===========================================================================
# RUNNER
# ===========================================================================

def main() -> int:
    print("=" * 78)
    print("CTA-EDGE-04-MMV — S2 SYNTHETIC VALIDATOR")
    print("=" * 78)
    print("Synthetic worlds only. No real macro value, price or canonical "
          "TSMOM sign is read.")
    print()

    groups = []
    for group, name, fn in TESTS:
        if not groups or groups[-1] != group:
            groups.append(group)

    current = None
    npass = nfail = 0
    for group, name, fn in TESTS:
        if group != current:
            current = group
            print("--- %s %s" % (group, "-" * max(0, 73 - len(group))))
        try:
            fn()
            RESULTS.append((group, name, True, ""))
            npass += 1
            print("  [PASS] %s" % name)
        except Exception as e:                                   # noqa: BLE001
            RESULTS.append((group, name, False, "%s: %s" % (type(e).__name__, e)))
            nfail += 1
            print("  [FAIL] %s" % name)
            print("         %s: %s" % (type(e).__name__, e))
            tb = traceback.format_exc().strip().splitlines()
            print("         %s" % tb[-3].strip() if len(tb) > 3 else "")

    print()
    print("=" * 78)
    print("S2 SYNTHETIC VALIDATION: %d/%d PASS" % (npass, npass + nfail))
    if nfail:
        print("VERDICT: FAIL")
        for g, n, ok, why in RESULTS:
            if not ok:
                print("   FAILED %s/%s: %s" % (g, n, why))
        return 1
    print("VERDICT: PASS — sealed behaviour reproduced")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    sys.exit(main())
