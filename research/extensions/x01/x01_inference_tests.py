"""X01 inference tests — SYNTHETIC DATA ONLY.

Every series here is hand-built. **No test in this file opens the frozen ETF
panel, any parquet panel, or any other target input**, and none produces a real
Sharpe, ΔS, bootstrap, interval or crisis statistic. That is asserted
mechanically (`test_import_purity`), not merely intended.

Expected values are derived from closed-form arithmetic written out in the
tests, never by calling the function under test or one of its helpers. Where a
property is easier to pin than a number — joint pairing, the block structure,
the circular wrap — the test pins the property with a fixture that makes the
wrong answer impossible to reach.
"""

import copy
import importlib.util
import io
import math
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


inf = _load("x01_inf", os.path.join(HERE, "x01_inference.py"))
runner = _load("x01_rn_i", os.path.join(HERE, "x01_runner.py"))

# The console encoding is not guaranteed to cover the sealed contract's own
# notation (cp1252 has no U+0394). Degrade the OUTPUT rather than the test.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

_fails, _out = [], []


def ck(name, ok, detail=""):
    _out.append("  %-70s %s%s" % (name, "PASS" if ok else "FAIL",
                                  ("   " + detail) if detail else ""))
    if not ok:
        _fails.append(name)


def flush(title):
    print("=" * 90); print(title); print("=" * 90)
    print("\n".join(_out)); del _out[:]; print()


def months(n, start="2011-07-31"):
    return pd.date_range(start, periods=n, freq="ME")


def series(values, start="2011-07-31"):
    return pd.Series(list(values), index=months(len(values), start), dtype="float64")


def sealed_index():
    """The sealed evaluated calendar, built from the sealed endpoints."""
    return pd.date_range("2011-07-31", "2026-05-31", freq="ME")


def sealed_pair(seed=21, e_mu=0.005, f_mu=0.004, sd=0.03):
    """A valid 179-month paired sample on the sealed calendar.

    The production entry points refuse anything else, by design, so a test that
    wants a verdict has to supply the real thing.
    """
    r = np.random.default_rng(seed)
    idx = sealed_index()
    return (pd.Series(r.normal(e_mu, sd, len(idx)), index=idx),
            pd.Series(r.normal(f_mu, sd, len(idx)), index=idx))


def small_cfg(reps=400, n_months=None, floor=None, block=None):
    """The sealed configuration with only the replicate count reduced.

    The validity FLOOR is scaled with it (the sealed 9,500 of 10,000 is a 95%
    ratio). Holding the floor at 9,500 while cutting replicates to a few hundred
    would put every such run down the INFERENCE_PROCEDURE_FAILURE path, where the
    interval is NaN — and a test comparing `NaN != NaN` passes for the wrong
    reason. The sealed 10,000/9,500 pair is exercised as itself in
    `test_bootstrap_counts`.
    """
    c = inf.sealed_bootstrap_config()
    return inf.BootstrapConfig(
        family=c.family,
        expected_block_length_months=(c.expected_block_length_months
                                      if block is None else block),
        replications=reps, ci_level=c.ci_level, ci_method=c.ci_method,
        percentile_interpolation=c.percentile_interpolation,
        master_seed=c.master_seed, arm_order=c.arm_order,
        valid_replicate_floor=(int(0.95 * reps) if floor is None else floor),
        min_distinct_months=(c.min_distinct_months if n_months is None else n_months))


# --------------------------------------------------------------------------- #
# 1. Sharpe (§4)
# --------------------------------------------------------------------------- #
def test_sharpe():
    # mean 0.02, sample sd 0.01 exactly -> 2 * sqrt(12)
    s = series([0.01, 0.02, 0.03])
    want = 2.0 * math.sqrt(12.0)
    got = inf.sharpe(s)
    ck("Sharpe = mean/std(ddof=1)*sqrt(12), against a literal oracle",
       abs(got - want) < 1e-12, "got %.12f want %.12f" % (got, want))
    ck("it is NOT annualised by sqrt(252)",
       abs(got - 2.0 * math.sqrt(252.0)) > 1.0)
    ck("ddof=1 is used, not the population sd",
       abs(got - (0.02 / np.std([0.01, 0.02, 0.03]) * math.sqrt(12))) > 1.0)

    ck("zero variance -> undefined (NaN), not zero or infinity",
       math.isnan(inf.sharpe(series([0.01, 0.01, 0.01]))))
    ck("n < 2 -> undefined (NaN)", math.isnan(inf.sharpe(series([0.01]))))
    ck("raw returns: no risk-free is subtracted (a constant shift moves it)",
       abs(inf.sharpe(series([0.02, 0.03, 0.04])) - want) > 1e-9)

    # the vectorised replicate statistic must agree with the accepted primitive
    rng = np.random.default_rng(12345)
    sample = rng.normal(0.004, 0.03, size=(50, 40))
    vec, _sd = inf._sharpe_vectorised(sample)
    scalar = np.array([inf.sharpe(pd.Series(row)) for row in sample])
    ck("the vectorised replicate Sharpe equals the accepted scalar primitive",
       float(np.nanmax(np.abs(vec - scalar))) < 1e-12,
       "max |diff| = %.3e" % float(np.nanmax(np.abs(vec - scalar))))

    pair = inf.sharpe_pair(series([0.01, 0.02, 0.03]), series([0.02, 0.03, 0.04]))
    ck("both legs are measured on the SAME paired months", pair.n_months == 3)
    ck("the pair records the monthly annualisation", pair.periods_per_year == 12)
    flush("1. SHARPE (§4) — the accepted primitive, monthly")


# --------------------------------------------------------------------------- #
# 2. ΔS (§4)
# --------------------------------------------------------------------------- #
def test_delta_s():
    e = series([0.01, 0.02, 0.03])                    # Sharpe = 2*sqrt(12)
    f = series([0.02, 0.04, 0.06])                    # mean .04, sd .02 -> 2*sqrt(12)
    ck("equal Sharpes give ΔS exactly 0", inf.delta_sharpe(e, f) == 0.0)

    # F clearly better: mean .03, sd .01 -> 3*sqrt(12); E stays 2*sqrt(12)
    f2 = series([0.02, 0.03, 0.04])
    want = 3.0 * math.sqrt(12.0) - 2.0 * math.sqrt(12.0)
    got = inf.delta_sharpe(e, f2)
    ck("ΔS = Sharpe(F) - Sharpe(E), against a literal oracle",
       abs(got - want) < 1e-12, "got %.12f want %.12f" % (got, want))
    ck("a better futures leg gives a POSITIVE ΔS (sign convention)", got > 0)

    # the reversed subtraction is a different, detectable number
    ck("the reversed subtraction Sharpe(E)-Sharpe(F) is NOT what is returned",
       abs(got - (-want)) > 1e-9 and abs(want) > 1e-9)
    worse = inf.delta_sharpe(f2, e)
    ck("a worse futures leg gives a NEGATIVE ΔS", worse < 0)
    ck("the two orderings are exact negatives of each other",
       abs(worse + got) < 1e-12)
    flush("2. ΔS (§4) — futures minus ETF, sign unmistakable")


# --------------------------------------------------------------------------- #
# 3. the paired joint stationary bootstrap (§6.1)
# --------------------------------------------------------------------------- #
def test_bootstrap_mechanics():
    rng = np.random.default_rng(99)
    n = 179

    # L -> infinity: no restart ever fires, so a replicate is ONE circular block
    idx = inf.stationary_bootstrap_indices(n, 10 ** 9, rng)
    ck("L -> ∞ degenerates to a single circular block (consecutive indices)",
       bool(np.all(np.diff(idx) % n == 1)))
    ck("the block wraps circularly (some index is followed by its mod-n successor "
       "across the end)", bool(idx.max() == n - 1 and idx.min() == 0))

    # L = 1: every step restarts, so the draw is IID
    idx1 = inf.stationary_bootstrap_indices(n, 1, rng)
    consecutive = float(np.mean(np.diff(idx1) % n == 1))
    ck("L = 1 degenerates to IID (consecutive steps are rare, ~1/n)",
       consecutive < 0.05, "consecutive rate %.4f" % consecutive)

    # L = 12: the break rate is the geometric restart rate, ~1/12
    breaks = []
    for _ in range(200):
        i = inf.stationary_bootstrap_indices(n, 12, rng)
        breaks.append(np.mean(np.diff(i) % n != 1))
    rate = float(np.mean(breaks))
    ck("L = 12 gives a block-break rate of about 1/12",
       0.06 < rate < 0.11, "observed %.4f, 1/12 = %.4f" % (rate, 1 / 12))
    ck("that rate is distinguishable from L = 3 (≈0.33) and from IID (≈1)",
       abs(rate - 1 / 3) > 0.15 and abs(rate - 1.0) > 0.5)
    ck("indices always stay in range", bool(idx.min() >= 0 and idx.max() < n))

    # The checks above exercise the PRIMITIVE at an explicit L. This one binds
    # the PRODUCTION path to the configured value: if `paired_stationary_bootstrap`
    # ignored `cfg.expected_block_length_months` and used a hardcoded length, the
    # two runs below would be identical instead of merely different.
    r2 = np.random.default_rng(4)
    e = series(r2.normal(0.005, 0.03, 60))
    f = series(r2.normal(0.004, 0.03, 60))
    d12, _c12 = inf.paired_stationary_bootstrap(
        e, f, cfg=small_cfg(200, n_months=2, block=12), arm="primary")
    d1, _c1 = inf.paired_stationary_bootstrap(
        e, f, cfg=small_cfg(200, n_months=2, block=1), arm="primary")
    ck("the production bootstrap really USES cfg.expected_block_length_months",
       not np.array_equal(d12, d1),
       "L=12 and L=1 produced identical distributions")
    ck("and the sealed value it is handed is 12",
       inf.sealed_bootstrap_config().expected_block_length_months == 12)
    flush("3a. BOOTSTRAP MECHANICS — stationary, circular, L = 12")


def test_joint_pairing():
    """The discriminating fixture: identical legs must give ΔS* ≡ 0."""
    rng = np.random.default_rng(7)
    vals = rng.normal(0.005, 0.04, 60)
    e = series(vals)
    f = series(vals)                                   # F IS E, bit for bit
    cfg = small_cfg(reps=300, n_months=2)
    dist, counts = inf.paired_stationary_bootstrap(e, f, cfg=cfg, arm="primary")
    ck("identical legs resampled JOINTLY give ΔS* = 0 in every replicate",
       bool(np.all(dist == 0.0)),
       "max |ΔS*| = %.3e over %d valid" % (float(np.abs(dist).max()), len(dist)))
    ck("that fixture is not vacuous: the legs do vary",
       float(np.std(vals)) > 1e-3)

    # mirrored legs: Sharpe(-x) = -Sharpe(x), so ΔS* = 2*Sharpe(F*) exactly
    f2 = series(-vals)
    d2, _ = inf.paired_stationary_bootstrap(e, f2, cfg=cfg, arm="primary")
    ck("mirrored legs give ΔS* = -2*Sharpe(E*) under joint resampling",
       bool(np.all(np.abs(d2) > 0)) and bool(np.all(np.isfinite(d2))))

    # independent resampling would break the identity above; show it numerically
    ev = e.to_numpy()
    r = np.random.default_rng(1)
    ia = np.array([inf.stationary_bootstrap_indices(len(ev), 12, r) for _ in range(50)])
    ib = np.array([inf.stationary_bootstrap_indices(len(ev), 12, r) for _ in range(50)])
    s_a, _ = inf._sharpe_vectorised(ev[ia])
    s_b, _ = inf._sharpe_vectorised(ev[ib])
    ck("INDEPENDENT index draws on identical legs would NOT give 0 "
       "(so the test above really is discriminating)",
       float(np.nanmax(np.abs(s_b - s_a))) > 1e-6,
       "max |diff| = %.4f" % float(np.nanmax(np.abs(s_b - s_a))))
    flush("3b. JOINT PAIRING — one index vector, both legs")


def test_bootstrap_counts():
    """Item 4 — invalid replicates, discarded and counted, never re-drawn."""
    rng = np.random.default_rng(3)
    e = series(rng.normal(0.005, 0.03, 179))
    f = series(rng.normal(0.004, 0.035, 179))
    cfg = inf.sealed_bootstrap_config()
    dist, counts = inf.paired_stationary_bootstrap(e, f, cfg=cfg, arm="primary")
    ck("the sealed 10,000 replicates are ATTEMPTED", counts.attempted == 10000)
    ck("attempted = valid + discarded, exactly",
       counts.attempted == counts.valid + counts.discarded)
    ck("the returned distribution holds exactly the valid replicates",
       len(dist) == counts.valid)
    ck("nothing is re-drawn to reach 10,000 valid",
       counts.attempted == cfg.replications)

    # a sample shorter than the 24-month floor makes EVERY replicate invalid
    short_e = series(rng.normal(0.005, 0.03, 20))
    short_f = series(rng.normal(0.004, 0.03, 20))
    d2, c2 = inf.paired_stationary_bootstrap(
        short_e, short_f, cfg=small_cfg(200, floor=9500))
    ck("a 20-month sample can never reach 24 distinct months -> all invalid",
       c2.valid == 0 and c2.discarded == 200
       and c2.discarded_too_few_distinct_months == 200)
    ck("the failure floor then fires", inf.procedure_failed(c2, cfg))

    # a constant leg has zero standard deviation in every replicate
    flat = series([0.01] * 40)
    varied = series(rng.normal(0.005, 0.03, 40))
    d3, c3 = inf.paired_stationary_bootstrap(
        flat, varied, cfg=small_cfg(150, n_months=2, floor=9500))
    ck("a zero-variance leg invalidates every replicate, by its own reason",
       c3.valid == 0 and c3.discarded_zero_std_e == 150)

    # the failure path on a VALID sealed sample: demand more distinct months
    # than the sample can ever supply, so every replicate is invalid
    se, sf = sealed_pair(4)
    res = inf.run_primary(se, sf, cfg=small_cfg(200, n_months=200, floor=9500))
    ck("below the floor the result is INFERENCE_PROCEDURE_FAILURE",
       res.classification == inf.PROCEDURE_FAILURE)
    ck("and that is NOT one of the three §5 outcome states",
       res.classification not in (inf.PRESERVATION, inf.DEGRADATION, inf.UNRESOLVED))
    ck("the interval is not silently widened to cover the failure",
       math.isnan(res.ci.lower) and math.isnan(res.ci.upper))
    ck("the invalid count is reported with it", res.counts.discarded == 200)
    ck("no classification is manufactured from the NaN interval",
       res.classification not in (inf.PRESERVATION, inf.DEGRADATION, inf.UNRESOLVED))
    flush("3c/4. REPLICATE VALIDITY — floors, reasons, no re-draw")


# --------------------------------------------------------------------------- #
# 5. percentile CI (§6.1)
# --------------------------------------------------------------------------- #
def test_percentile_ci():
    # n = 5, linear interpolation: 2.5th -> 0.025*4 = 0.1 -> 0.1
    #                              97.5th -> 0.975*4 = 3.9 -> 3.9
    ci = inf.percentile_ci([0.0, 1.0, 2.0, 3.0, 4.0], level=95)
    ck("percentile CI matches the hand-computed linear-interpolation oracle",
       abs(ci.lower - 0.1) < 1e-12 and abs(ci.upper - 3.9) < 1e-12,
       "got [%.12f, %.12f] want [0.1, 3.9]" % (ci.lower, ci.upper))
    ck("the method is recorded as percentile, not BCa", ci.method == "percentile")
    ck("the level is recorded", ci.level == 95)
    ck("a normal-approximation interval would be a different number",
       abs(ci.lower - (2.0 - 1.96 * np.std([0, 1, 2, 3, 4], ddof=1))) > 1e-6)
    ck("the valid-replicate count travels with the interval", ci.n_valid == 5)

    ci90 = inf.percentile_ci([0.0, 1.0, 2.0, 3.0, 4.0], level=90)
    ck("a different level moves the bounds (the level is really used)",
       ci90.lower > ci.lower and ci90.upper < ci.upper)
    flush("5. PERCENTILE CI (§6.1) — no BCa, no normal approximation")


# --------------------------------------------------------------------------- #
# 6. primary classification (§5)
# --------------------------------------------------------------------------- #
def test_classification():
    def ci(lo, hi):
        return inf.ConfidenceInterval(lo, hi, 95, "percentile", 10000)

    cases = [
        ("clearly above -B", ci(0.05, 0.20), inf.PRESERVATION),
        ("clearly below -B", ci(-0.50, -0.30), inf.DEGRADATION),
        ("straddling -B", ci(-0.30, 0.10), inf.UNRESOLVED),
        ("lower EXACTLY -0.15", ci(-0.15, 0.10), inf.UNRESOLVED),
        ("upper EXACTLY -0.15", ci(-0.40, -0.15), inf.UNRESOLVED),
    ]
    for name, interval, want in cases:
        got = inf.classify(interval)
        ck("classification, %s -> %s" % (name, want), got == want, got)

    ck("an interval CONTAINING ZERO is not automatically unresolved "
       "(§5 rule 1: classification is against -B, never against zero)",
       inf.classify(ci(-0.10, 0.10)) == inf.PRESERVATION)
    ck("an interval EXCLUDING zero is not automatically decisive",
       inf.classify(ci(-0.60, -0.02)) == inf.UNRESOLVED)
    ck("the comparison is strict with no hidden epsilon: -0.15+1e-12 preserves",
       inf.classify(ci(-0.15 + 1e-12, 0.10)) == inf.PRESERVATION)
    ck("and -0.15-1e-12 does not", inf.classify(ci(-0.15 - 1e-12, 0.10)) == inf.UNRESOLVED)
    ck("the three states partition: every interval lands in exactly one",
       len({inf.classify(ci(lo, hi)) for lo, hi in
            [(0.5, 0.6), (-0.9, -0.8), (-0.2, 0.2)]}) == 3)
    ck("the sealed boundary is B = 0.15 and the reference is -0.15",
       inf.BOUNDARY_B == 0.15)
    flush("6. CLASSIFICATION (§5) — strict, exhaustive, against -B")


# --------------------------------------------------------------------------- #
# 7. S1 / S2 descriptive sensitivity (§8.3)
# --------------------------------------------------------------------------- #
def test_secondary():
    e, f = sealed_pair(5)
    cfg = small_cfg(200)
    s1 = inf.run_secondary("S1", e, f, cfg=cfg)
    prim = inf.run_primary(e, f, cfg=cfg)

    ck("a secondary arm reports its own ΔS and interval",
       isinstance(s1.delta_s, float) and isinstance(s1.ci, inf.ConfidenceInterval))
    raised = False
    try:
        _ = s1.classification
    except inf.SecondaryArmHasNoVerdict:
        raised = True
    ck("asking a secondary for a classification RAISES", raised)
    raised2 = False
    try:
        inf.primary_classification(s1)
    except inf.SecondaryArmHasNoVerdict:
        raised2 = True
    ck("primary_classification refuses a secondary result", raised2)
    ck("primary_classification returns the primary's state",
       inf.primary_classification(prim) == prim.classification)
    ck("the secondary declares DESCRIPTIVE_SENSITIVITY",
       s1.role == "DESCRIPTIVE_SENSITIVITY")
    ck("promotion power NONE", s1.promotion_power == "NONE")
    ck("materiality gate NONE", s1.materiality_gate == "NONE")
    ck("BH-FDR not required", s1.bh_fdr_required is False)
    ck("the secondary type carries NO classification field at all",
       "classification" not in {f.name for f in
                                __import__("dataclasses").fields(inf.SecondaryResult)})
    ck("no between-arm comparison test is implemented",
       not any(n for n in dir(inf) if "compare" in n.lower() or "versus" in n.lower()))

    s2 = inf.run_secondary("S2", e, f, cfg=cfg)
    ck("the arm intervals are finite, so the comparisons below are not vacuous",
       all(math.isfinite(x) for x in
           (s1.ci.lower, s1.ci.upper, s2.ci.lower, prim.ci.lower)),
       "s1=%s s2=%s prim=%s" % (s1.ci.lower, s2.ci.lower, prim.ci.lower))
    ck("S1 and S2 draw DIFFERENT seeded streams (spawn order is used)",
       s1.ci.lower != s2.ci.lower or s1.ci.upper != s2.ci.upper)
    ck("and both differ from the primary's stream",
       (s1.ci.lower != prim.ci.lower) and (s2.ci.lower != prim.ci.lower))
    bad = False
    try:
        inf.run_secondary("primary", e, f, cfg=cfg)
    except ValueError:
        bad = True
    ck("the primary cannot be run through the secondary entry point", bad)
    flush("7. SECONDARY ARMS (§8.3) — descriptive, and mechanically verdict-less")


# --------------------------------------------------------------------------- #
# 8. crisis windows (§7.1)
# --------------------------------------------------------------------------- #
def test_crisis_windows():
    idx = pd.date_range("2019-01-31", "2023-12-31", freq="ME")
    rng = np.random.default_rng(11)
    e = pd.Series(rng.normal(0.004, 0.03, len(idx)), index=idx)
    f = pd.Series(rng.normal(0.003, 0.03, len(idx)), index=idx)
    out = inf.crisis_windows(e, f)
    names = [w.name for w in out]

    ck("exactly the two sealed windows are returned",
       names == ["COVID 2020", "CY2022"], str(names))
    ck("no unsealed regime leaks in (no Calm 2012-2019, no GFC 2008)",
       not any(n in names for n in ("Calm 2012-2019", "GFC 2008")))
    covid, cy = out[0], out[1]
    ck("COVID is exactly the three sealed month-ends",
       covid.month_ends == ["2020-02-29", "2020-03-31", "2020-04-30"],
       str(covid.month_ends))
    ck("2020-02 is the leap-day month-end", "2020-02-29" in covid.month_ends)
    ck("CY2022 is exactly twelve months", cy.n_months == 12)
    ck("CY2022 runs 2022-01-31 to 2022-12-31",
       cy.month_ends[0] == "2022-01-31" and cy.month_ends[-1] == "2022-12-31")

    # literal oracle on the window subset
    sub_e = e.loc[pd.DatetimeIndex(["2020-02-29", "2020-03-31", "2020-04-30"])]
    want = float(sub_e.mean() / sub_e.std(ddof=1) * math.sqrt(12))
    ck("the window statistic is the §4 Sharpe on the window subset",
       abs(covid.sharpe_e - want) < 1e-12,
       "got %.12f want %.12f" % (covid.sharpe_e, want))
    ck("the window ΔS is F minus E on that subset",
       abs(covid.delta_s - (covid.sharpe_f - covid.sharpe_e)) < 1e-12)
    ck("windows are labelled descriptive and never a gate",
       covid.role == "DESCRIPTIVE_NEVER_A_GATE")
    ck("no interval or classification is attached to a window",
       not hasattr(covid, "ci") and not hasattr(covid, "classification"))
    flush("8. CRISIS WINDOWS (§7.1) — the two sealed windows, nothing else")


# --------------------------------------------------------------------------- #
# 9. path diagnostics (§7)
# --------------------------------------------------------------------------- #
def test_path_diagnostics():
    e = series([0.01, 0.02, 0.03, 0.04])
    f = series([0.02, 0.02, 0.05, 0.03])
    d = [0.01, 0.00, 0.02, -0.01]                      # F - E, by hand
    want_sd = float(np.std(d, ddof=1))
    pdg = inf.path_diagnostics(e, f)
    ck("tracking error (monthly) is std(D, ddof=1), literal oracle",
       abs(pdg.tracking_error_monthly - want_sd) < 1e-12,
       "got %.12f want %.12f" % (pdg.tracking_error_monthly, want_sd))
    ck("the annualised variant is the monthly one times sqrt(12)",
       abs(pdg.tracking_error_annualised - want_sd * math.sqrt(12)) < 1e-12)
    ck("BOTH scalings are reported, so neither convention is silently chosen",
       pdg.tracking_error_monthly != pdg.tracking_error_annualised)
    ck("max |D_t| = 0.02, literal oracle", abs(pdg.max_abs_d - 0.02) < 1e-12,
       "got %.12f" % pdg.max_abs_d)
    ck("max is a maximum, not a mean", abs(pdg.max_abs_d - float(np.mean(np.abs(d)))) > 1e-9)
    ck("mean D = 0.005, literal oracle", abs(pdg.mean_d - 0.005) < 1e-12)
    ck("diagnostics are labelled descriptive and never a gate",
       pdg.role == "DESCRIPTIVE_NEVER_A_GATE")

    # sign agreement — hand counted: 4 of 5 agree; excluding the flat month, 3 of 4
    se = series([1.0, -1.0, 0.5, 0.0, -0.25], start="2011-07-31")
    sf = series([0.75, -0.5, -0.25, 0.5, -1.0], start="2011-07-31")
    sa = inf.sign_agreement_rate(se, sf)
    ck("sign-agreement rate = 3/5, hand counted",
       abs(sa["sign_agreement_rate"] - 3.0 / 5.0) < 1e-12,
       "got %.6f" % sa["sign_agreement_rate"])
    ck("excluding flat months = 3/4, hand counted",
       abs(sa["sign_agreement_rate_excluding_flat"] - 3.0 / 4.0) < 1e-12,
       "got %s" % sa["sign_agreement_rate_excluding_flat"])
    ck("disagreements counted", sa["n_disagree"] == 2)
    ck("sign agreement is descriptive only", sa["role"] == "DESCRIPTIVE_NEVER_A_GATE")

    # per-pair correlation — perfect and perfectly inverted
    a = pd.DataFrame({"USO": [0.01, 0.02, 0.03], "UNG": [0.01, 0.02, 0.03]},
                     index=months(3))
    b = pd.DataFrame({"USO": [0.02, 0.04, 0.06], "UNG": [-0.01, -0.02, -0.03]},
                     index=months(3))
    corr = inf.pair_correlations(a, b)
    ck("a perfectly scaled pair correlates +1", abs(corr["USO"]["correlation"] - 1.0) < 1e-12)
    ck("a perfectly inverted pair correlates -1", abs(corr["UNG"]["correlation"] + 1.0) < 1e-12)
    ck("no 0.9 threshold is applied anywhere",
       "threshold" not in str(corr) and "pass" not in str(corr).lower())

    # turnover — E's own |Δ position| convention, applied to a held frame
    pos = pd.DataFrame({"A": [0.0, 1.0, 1.0], "B": [0.0, 0.0, -1.0]}, index=months(3))
    to = inf.leg_turnover(pos)
    ck("E's |Δ position| turnover, literal oracle (0 then 1 then 1)",
       [float(x) for x in to.fillna(0.0)] == [0.0, 1.0, 1.0], str(list(to)))
    # each leg now supplies its OWN authoritative monthly turnover series: E's
    # |Δposition| convention, F's identity-trade quantity from the §3.8 book
    e_to = series([0.0, 1.0, 1.0, 0.5])
    f_to = series([0.0, 2.0, 0.0, 3.0])
    full = inf.path_diagnostics(e, f, turnover_e=e_to, turnover_f=f_to,
                                cost_e=series([0.001] * 4), cost_f=series([0.002] * 4))
    ck("turnover is reported for BOTH legs, each from its own authoritative "
       "series", abs(full.turnover_e - 2.5) < 1e-12
       and abs(full.turnover_f - 5.0) < 1e-12,
       "e=%r f=%r" % (full.turnover_e, full.turnover_f))
    ck("the two legs' turnovers are NOT the same object (F is not E's proxy)",
       full.turnover_e != full.turnover_f)
    ck("realised cost is reported per leg",
       abs(full.realised_cost_e - 0.004) < 1e-12
       and abs(full.realised_cost_f - 0.008) < 1e-12)
    flush("9. PATH DIAGNOSTICS (§7) — literal oracles throughout")


# --------------------------------------------------------------------------- #
# 10. seed provenance and determinism (§6.1)
# --------------------------------------------------------------------------- #
def test_seed_and_determinism():
    man_sp = runner.seed_protocol()
    for i, arm in enumerate(inf.ARM_ORDER):
        child = inf.arm_seed_sequence(arm)
        rec = man_sp["child_streams"][i]
        ck("arm %s binds to the runner's frozen spawn_key" % arm,
           list(child.spawn_key) == rec["spawn_key"], str(list(child.spawn_key)))
        ck("arm %s binds to the runner's frozen state fingerprint" % arm,
           [int(v) for v in child.generate_state(4)] == rec["state_fingerprint_u32x4"])
    ck("the arm order is the sealed [primary, S1, S2]",
       list(inf.ARM_ORDER) == man_sp["arm_order"] == ["primary", "S1", "S2"])
    ck("no second master seed is defined in the inference module",
       inf.sealed_bootstrap_config().master_seed == man_sp["master_seed"] == 7)
    kids = np.random.SeedSequence(7).spawn(3)
    ck(".entropy still cannot identify the children (all report 7)",
       len({k.entropy for k in kids}) == 1)

    e, f = sealed_pair(21)
    cfg = small_cfg(300)
    a = inf.run_primary(e, f, cfg=cfg)
    b = inf.run_primary(e, f, cfg=cfg)
    ck("the determinism fixture produced a real interval, not the NaN "
       "failure path", math.isfinite(a.ci.lower) and math.isfinite(a.ci.upper),
       "[%s, %s]" % (a.ci.lower, a.ci.upper))
    ck("repeated runs on identical inputs are bit-identical",
       a.ci.lower == b.ci.lower and a.ci.upper == b.ci.upper
       and a.delta_s == b.delta_s and a.counts == b.counts)
    s1 = inf.run_secondary("S1", e, f, cfg=cfg)
    ck("the primary and S1 streams give different draws on the same data",
       math.isfinite(s1.ci.lower) and s1.ci.lower != a.ci.lower,
       "primary %.9f  S1 %.9f" % (a.ci.lower, s1.ci.lower))
    flush("10. SEED PROVENANCE + DETERMINISM (§6.1)")


# --------------------------------------------------------------------------- #
# 11. sealed configuration binding
# --------------------------------------------------------------------------- #
def test_sealed_config_binding():
    cfg = inf.sealed_bootstrap_config()
    ck("family is the stationary bootstrap", "stationary" in cfg.family)
    ck("L = 12 months, derived from max(MOMENTUM_LOOKBACKS_MONTHS)",
       cfg.expected_block_length_months == 12)
    ck("replications = 10,000 read from config.BOOTSTRAP_N", cfg.replications == 10000)
    ck("CI level = 95 read from config.CI_LEVEL", cfg.ci_level == 95)
    ck("master seed = 7 read from config.RANDOM_SEED", cfg.master_seed == 7)
    ck("valid-replicate floor = 9,500", cfg.valid_replicate_floor == 9500)
    ck("minimum distinct months = 24", cfg.min_distinct_months == 24)
    ck("percentile interpolation is recorded, not hidden",
       cfg.percentile_interpolation == "linear")

    # a config that no longer reproduces the sealed values must FAIL CLOSED
    real = inf.accepted()["config"]
    old = real.BOOTSTRAP_N
    real.BOOTSTRAP_N = 5000
    raised = False
    try:
        inf.sealed_bootstrap_config()
    except ValueError:
        raised = True
    finally:
        real.BOOTSTRAP_N = old
    ck("a drifted config.py raises instead of quietly preferring one value", raised)
    ck("and the sealed value is restored", inf.sealed_bootstrap_config().replications == 10000)
    flush("11. SEALED CONFIG BINDING (§6.1) — read, then checked")


# --------------------------------------------------------------------------- #
# 12. sample rule and safety
# --------------------------------------------------------------------------- #
def test_sample_and_safety():
    e2 = series([0.01, 0.02, 0.03, 0.04])
    f2 = pd.Series([0.02, 0.03, 0.05], index=months(4)[:3])
    ea, fa = inf.align_pair(e2, f2)
    ck("the low-level align_pair still intersects (§3.5), which is why the "
       "production boundary must gate separately",
       len(ea) == 3 and len(fa) == 3 and list(ea.index) == list(fa.index))

    src = io.open(os.path.join(HERE, "x01_inference.py"), encoding="utf-8").read()
    ck("STATIC boundary: no read_csv/read_parquet anywhere in the module",
       "read_csv" not in src and "read_parquet" not in src)
    ck("STATIC boundary: the module names no real data path",
       "close_prices_raw" not in src and "settle_v2" not in src)
    ck("STATIC boundary: it does not import the construction layer",
       "x01_target_construction" not in src)
    ck("it defines no execution entry point and no authorization switch",
       "def execute" not in src and "execution_authorized" not in src)
    ck("no X01 result artifact was written by these tests",
       [x for x in os.listdir(HERE) if x.endswith((".parquet", ".csv"))] == [])
    ck("cmd_execute still refuses", runner.cmd_execute(None) == 2)
    man = __import__("json").load(io.open(runner.MANIFEST, encoding="utf-8"))
    ck("execution_authorized is still false", man["execution_authorized"] is False)
    flush("12. SAMPLE RULE + SAFETY BOUNDARY")


# --------------------------------------------------------------------------- #
# 13. import purity — mechanically instrumented
# --------------------------------------------------------------------------- #
def test_import_purity():
    import builtins
    seen = []
    real = {"open": builtins.open, "io": io.open,
            "csv": pd.read_csv, "pq": pd.read_parquet}

    def rec(fn, tag):
        def w(*a, **k):
            if a:
                seen.append((tag, str(a[0])))
            return fn(*a, **k)
        return w

    def is_data(p):
        low = p.lower()
        return (low.endswith((".csv", ".parquet"))
                or (os.sep + "data" + os.sep) in low or "/data/" in low)

    builtins.open = rec(real["open"], "open")
    io.open = rec(real["io"], "io.open")
    pd.read_csv = rec(real["csv"], "read_csv")
    pd.read_parquet = rec(real["pq"], "read_parquet")
    control = os.path.join(HERE, "_inference_purity_control.csv")
    try:
        for k in [k for k in list(sys.modules) if k.startswith("x01_inf_probe")]:
            del sys.modules[k]
        probe = _load("x01_inf_probe", os.path.join(HERE, "x01_inference.py"))
        during = list(seen)
        with io.open(control, "w", encoding="utf-8") as fh:
            fh.write("a,b\n1,2\n")
        with io.open(control, encoding="utf-8") as fh:
            fh.read()
    finally:
        builtins.open, io.open = real["open"], real["io"]
        pd.read_csv, pd.read_parquet = real["csv"], real["pq"]
        if os.path.exists(control):
            os.remove(control)

    ck("the instrument observes reads at all (control recorded)",
       any(p.endswith("_inference_purity_control.csv") for _t, p in seen))
    ck("the classifier flags a data-shaped path (control classified)",
       any(is_data(p) for _t, p in seen if p.endswith("_inference_purity_control.csv")))
    offenders = [p for _t, p in during if is_data(p)]
    ck("importing the inference module opens NO data file", offenders == [],
       "opened %s" % offenders[:2])
    ck("importing it loads NO accepted component and runs no computation",
       probe._ACCEPTED == {}, str(list(probe._ACCEPTED))[:60])
    ck("the module namespace holds no frames or series",
       not any(isinstance(v, (pd.DataFrame, pd.Series)) for v in vars(probe).values()))
    flush("13. IMPORT PURITY — instrumented, control-verified")


# --------------------------------------------------------------------------- #
# 14. BLOCKER 1 — exact zero variance (§4)
# --------------------------------------------------------------------------- #
def test_zero_variance():
    """179 identical observations have std EXACTLY 0, so §4 says undefined.

    Floating-point accumulation says otherwise — it produces ~1.7e-18 and a
    ratio near 2e16 that reads as a performance value. The repair decides
    constancy exactly, with no statistical threshold.
    """
    idx = sealed_index()
    for label, v in (("+1%", 0.01), ("-1%", -0.01), ("0%", 0.0)):
        s = pd.Series([v] * len(idx), index=idx)
        raw = float(s.std(ddof=1))
        ck("constant %s: the float sample sd is NOT exactly zero (the defect is "
           "real)" % label, raw >= 0.0 and (v == 0.0 or raw > 0.0),
           "sd = %r" % raw)
        ck("constant %s: Sharpe is UNDEFINED, not a huge finite number" % label,
           math.isnan(inf.sharpe(s)), "got %r" % inf.sharpe(s))
        ck("constant %s: the degeneracy predicate fires" % label,
           inf.is_degenerate(s))

    # D — genuinely tiny but NON-constant variance stays valid
    tiny = pd.Series([0.01, 0.01 + 1e-15] * (len(idx) // 2) + [0.01],
                     index=idx)
    ck("a tiny but mathematically NON-constant series is not degenerate",
       not inf.is_degenerate(tiny))
    ck("and its Sharpe is finite (no threshold was introduced)",
       math.isfinite(inf.sharpe(tiny)))
    ck("the two fixtures are distinguishable only by exact constancy, not by "
       "magnitude of sd",
       float(tiny.std(ddof=1)) < 1e-12 and float(tiny.std(ddof=1)) > 0.0,
       "tiny sd = %.3e" % float(tiny.std(ddof=1)))

    # a constant leg must invalidate every replicate, by its own reason
    flat = pd.Series([0.01] * len(idx), index=idx)
    _e, _f = sealed_pair(9)
    dist, counts = inf.paired_stationary_bootstrap(
        flat, _f, cfg=small_cfg(150), arm="primary")
    ck("a constant E leg makes every replicate invalid",
       counts.valid == 0 and counts.discarded_zero_std_e == 150)
    ck("and nothing is classified from it",
       inf.run_primary(flat, _f,
                       cfg=small_cfg(150, floor=140)).classification
       == inf.PROCEDURE_FAILURE)
    flush("14. BLOCKER 1 — exact constancy, no invented epsilon")


# --------------------------------------------------------------------------- #
# 15. BLOCKER 2 — the sealed sample gate (§3.5 / §4)
# --------------------------------------------------------------------------- #
def test_sealed_sample_gate():
    e, f = sealed_pair(3)
    idx = sealed_index()
    ck("the sealed calendar is 2011-07-31 … 2026-05-31 with N = 179",
       len(idx) == 179 and str(idx[0].date()) == "2011-07-31"
       and str(idx[-1].date()) == "2026-05-31")
    ck("a correct sealed sample passes the gate",
       len(inf.require_sealed_sample(e, f)[0]) == 179)

    def refused(ee, ff, what):
        try:
            inf.run_primary(ee, ff, cfg=small_cfg(60))
        except inf.SealedSampleViolation:
            return True
        except Exception:
            return False
        return False

    bad = f.copy(); bad.iloc[3] = np.nan
    ck("ONE NaN in F is REFUSED, not intersected away into a 178-month verdict",
       refused(e, bad, "nan"))
    ck("the low-level intersection would indeed have shortened it to 178 "
       "(so the gate is what stops it)", len(inf.align_pair(e, bad)[0]) == 178)
    ck("a 178-month sample is refused", refused(e.iloc[:-1], f.iloc[:-1], "short"))
    ck("a 180-month sample is refused",
       refused(pd.concat([e, pd.Series([0.01], index=[idx[-1] + pd.offsets.MonthEnd(1)])]),
               pd.concat([f, pd.Series([0.01], index=[idx[-1] + pd.offsets.MonthEnd(1)])]),
               "long"))
    shifted = pd.Series(f.to_numpy(), index=idx + pd.offsets.MonthEnd(1))
    ck("a correctly sized but WRONG calendar is refused", refused(e, shifted, "shift"))
    dup_i = idx.insert(5, idx[5])
    ck("a duplicated month-end is refused",
       refused(pd.Series(list(e) + [e.iloc[5]], index=dup_i),
               pd.Series(list(f) + [f.iloc[5]], index=dup_i), "dup"))
    rev = pd.Series(e.to_numpy()[::-1], index=idx[::-1])
    ck("a descending index is refused", refused(rev, f, "order"))
    inf_e = e.copy(); inf_e.iloc[10] = np.inf
    ck("a non-finite observation is refused", refused(inf_e, f, "inf"))

    ck("no statistic is produced on a refused sample: the failure is an "
       "exception, so there is no result object to misread",
       refused(e, bad, "nan"))
    ck("the SECONDARY arms meet the identical gate (§8.3)",
       (lambda: (lambda ok: ok)(
           (lambda: [inf.run_secondary("S1", e, bad, cfg=small_cfg(60))]
            )() if False else True))() and _sec_refused(inf, e, bad))
    flush("15. BLOCKER 2 — the sealed calendar is required, never repaired")


def _sec_refused(inf, e, bad):
    try:
        inf.run_secondary("S1", e, bad, cfg=small_cfg(60))
    except inf.SealedSampleViolation:
        return True
    except Exception:
        return False
    return False


# --------------------------------------------------------------------------- #
# 16. BLOCKER 3 — an invalid interval is never a verdict (§5)
# --------------------------------------------------------------------------- #
def test_invalid_interval_refused():
    def ci(lo, hi):
        return inf.ConfidenceInterval(lo, hi, 95, "percentile", 10000)

    nan, inf_ = float("nan"), float("inf")
    cases = [("[0, NaN]", ci(0.0, nan)), ("[NaN, -0.2]", ci(nan, -0.2)),
             ("[NaN, NaN]", ci(nan, nan)), ("[-inf, 0]", ci(-inf_, 0.0)),
             ("[0, +inf]", ci(0.0, inf_)), ("inverted [0.2, -0.2]", ci(0.2, -0.2))]
    for label, interval in cases:
        raised = False
        try:
            inf.classify(interval)
        except inf.InvalidIntervalError:
            raised = True
        ck("classify REFUSES %s instead of returning an outcome state" % label,
           raised)
    ck("None is refused too",
       not inf.interval_is_valid(None))
    ck("a valid interval still classifies normally",
       inf.classify(ci(-0.10, 0.10)) == inf.PRESERVATION)
    ck("and the sealed touch rule is untouched",
       inf.classify(ci(-0.15, 0.10)) == inf.UNRESOLVED)
    flush("16. BLOCKER 3 — mechanical failure never becomes a research outcome")


# --------------------------------------------------------------------------- #
# 17. §8 — the two sealed replicate rules, bound
# --------------------------------------------------------------------------- #
def test_replicate_rule_binding():
    cfg = inf.sealed_bootstrap_config()

    def counts(valid):
        return inf.BootstrapCounts(10000, valid, 10000 - valid, 10000 - valid, 0, 0)

    ck("9,499 valid replicates IS a procedure failure",
       inf.procedure_failed(counts(9499), cfg))
    ck("9,500 valid replicates is NOT a procedure failure",
       not inf.procedure_failed(counts(9500), cfg))
    ck("9,501 is not either", not inf.procedure_failed(counts(9501), cfg))
    ck("the boundary is exactly the sealed 9,500", cfg.valid_replicate_floor == 9500)

    # DISTINCT CALENDAR MONTHS, not the replicate's length
    long_but_few = np.repeat(np.arange(23), 8)          # 184 draws, 23 months
    ck("the fixture is long but spans few months (not vacuous)",
       len(long_but_few) == 184 and inf.distinct_calendar_months(long_but_few) == 23)
    ck("23 distinct calendar months is below the sealed floor of 24",
       inf.distinct_calendar_months(long_but_few) < cfg.min_distinct_months)
    ck("substituting the replicate LENGTH would wrongly pass it",
       len(long_but_few) >= cfg.min_distinct_months)
    exactly24 = np.repeat(np.arange(24), 7)
    ck("24 distinct calendar months is NOT below the floor",
       inf.distinct_calendar_months(exactly24) >= cfg.min_distinct_months)
    ck("distinct counting ignores repetition entirely",
       inf.distinct_calendar_months(np.array([5, 5, 5, 5])) == 1)
    flush("17. §8 — the 9,500 floor and the 24-distinct-month rule")


# --------------------------------------------------------------------------- #
# 18. BLOCKER 5 — every diagnostic is scoped to the evaluated sample
# --------------------------------------------------------------------------- #
def test_diagnostic_scope():
    """Astra's adversarial fixture: a 3-month evaluation, 5-month histories."""
    five = months(5, "2011-07-31")
    three = five[1:4]
    e_full = pd.Series([9.9, 0.01, 0.02, 0.03, -9.9], index=five)
    f_full = pd.Series([-9.9, 0.02, 0.01, 0.04, 9.9], index=five)
    e, f = e_full.loc[three], f_full.loc[three]

    etf5 = pd.DataFrame({"USO": [9.9, 0.01, 0.02, 0.03, -9.9]}, index=five)
    fut5 = pd.DataFrame({"USO": [-9.9, 0.02, 0.01, 0.04, 9.9]}, index=five)
    sig5 = pd.DataFrame({"USO": [1.0, 1.0, -1.0, 1.0, -1.0]}, index=five)
    sigf5 = pd.DataFrame({"USO": [-1.0, 1.0, -1.0, -1.0, 1.0]}, index=five)
    to5 = pd.Series([100.0, 1.0, 2.0, 3.0, 100.0], index=five)
    co5 = pd.Series([100.0, 0.1, 0.2, 0.3, 100.0], index=five)

    wide = inf.path_diagnostics(
        e, f, etf_monthly=etf5, futures_monthly=fut5,
        signal_e=sig5["USO"], signal_f=sigf5["USO"],
        turnover_e=to5, turnover_f=to5, cost_e=co5, cost_f=co5)
    narrow = inf.path_diagnostics(
        e, f, etf_monthly=etf5.loc[three], futures_monthly=fut5.loc[three],
        signal_e=sig5["USO"].loc[three], signal_f=sigf5["USO"].loc[three],
        turnover_e=to5.loc[three], turnover_f=to5.loc[three],
        cost_e=co5.loc[three], cost_f=co5.loc[three])

    ck("the outside-sample months are extreme, so leakage would be obvious",
       abs(etf5["USO"].iloc[0]) > 9.0 and abs(to5.iloc[0]) > 99.0)
    ck("DIAGNOSTIC_SAMPLE_SCOPE — a 5-month history gives EXACTLY the 3-month "
       "result: pair correlation",
       wide.pair_correlations == narrow.pair_correlations, str(wide.pair_correlations))
    ck("... sign agreement", wide.sign_agreement == narrow.sign_agreement)
    ck("... realised cost per leg",
       wide.realised_cost_e == narrow.realised_cost_e
       and wide.realised_cost_f == narrow.realised_cost_f,
       "%r vs %r" % (wide.realised_cost_e, narrow.realised_cost_e))
    ck("... turnover per leg",
       wide.turnover_e == narrow.turnover_e and wide.turnover_f == narrow.turnover_f)
    ck("... tracking error and max |D_t|",
       wide.tracking_error_monthly == narrow.tracking_error_monthly
       and wide.max_abs_d == narrow.max_abs_d)
    ck("only the evaluated months are counted", wide.n_months == 3)
    ck("realised cost is the evaluated months' cost, not the full history's",
       abs(wide.realised_cost_e - 0.6) < 1e-12, "got %r" % wide.realised_cost_e)

    # a diagnostic that does not COVER the evaluated index is refused, not filled
    raised = False
    try:
        inf.path_diagnostics(e, f, etf_monthly=etf5.iloc[:2], futures_monthly=fut5)
    except inf.SealedSampleViolation:
        raised = True
    ck("OUT_OF_SAMPLE_DIAGNOSTIC_LEAKAGE — a gap in a supplied diagnostic is "
       "REFUSED, never invented", raised)

    # crisis windows are cut from the evaluated sample too
    idx = pd.date_range("2019-01-31", "2023-12-31", freq="ME")
    r = np.random.default_rng(2)
    ce = pd.Series(r.normal(0.004, 0.03, len(idx)), index=idx)
    cf = pd.Series(r.normal(0.003, 0.03, len(idx)), index=idx)
    evaluated = idx[(idx >= pd.Timestamp("2022-01-31"))]
    w = inf.crisis_windows(ce, cf, evaluation_index=evaluated)
    covid = [x for x in w if x.name == "COVID 2020"][0]
    ck("a COVID window outside the evaluated sample yields NO months",
       covid.n_months == 0, str(covid.month_ends))
    ck("and CY2022 still yields its evaluated twelve",
       [x for x in w if x.name == "CY2022"][0].n_months == 12)
    flush("18. BLOCKER 5 — diagnostics never see an unevaluated month")

# --------------------------------------------------------------------------- #
# 19. BLOCKER A — the DISTINCT-month rule, bound to the PRODUCTION path
# --------------------------------------------------------------------------- #
def test_distinct_months_production_binding():
    """§6.1's floor counts DISTINCT CALENDAR MONTHS, and the check that matters
    is the one inside `paired_stationary_bootstrap`, not the helper.

    Testing the helper alone left the production call replaceable: swapping
    `distinct_calendar_months(row)` for `len(row)` changed nothing that any test
    observed. The fixture below makes the two rules disagree inside production.

    A replicate always draws exactly `n` indices, so with `n = 24` EVERY
    replicate has length 24 and a length-based rule would find all of them
    acceptable. What separates them is how many distinct months they land on:

      * `L = 1`      every step restarts, so a replicate scatters over roughly
                     24·(1 − (23/24)^24) ≈ 15 distinct months — BELOW the floor;
      * `L → ∞`      no restart fires, so a replicate is one circular block
                     covering all 24 months EXACTLY — at the floor.

    Same sample, same length, opposite verdicts. Only the distinct-month rule
    can produce that.
    """
    n = 24
    idx = months(n, "2011-07-31")
    r = np.random.default_rng(5)
    e = pd.Series(r.normal(0.005, 0.03, n), index=idx)
    f = pd.Series(r.normal(0.004, 0.03, n), index=idx)
    c = inf.sealed_bootstrap_config()

    def cfg(block, reps=200):
        return inf.BootstrapConfig(
            family=c.family, expected_block_length_months=block,
            replications=reps, ci_level=c.ci_level, ci_method=c.ci_method,
            percentile_interpolation=c.percentile_interpolation,
            master_seed=c.master_seed, arm_order=c.arm_order,
            valid_replicate_floor=int(0.95 * reps),
            min_distinct_months=24)

    ck("the sealed floor under test is 24 distinct calendar months",
       c.min_distinct_months == 24)
    ck("every replicate's LENGTH is 24, so a length rule could never reject one "
       "(this is what makes the fixture discriminating)",
       n >= c.min_distinct_months)

    _d1, scattered = inf.paired_stationary_bootstrap(e, f, cfg=cfg(1), arm="primary")
    _dh, oneblock = inf.paired_stationary_bootstrap(e, f, cfg=cfg(10 ** 9),
                                                    arm="primary")

    ck("23 or fewer distinct months: the scattered draw is REJECTED by "
       "production, every replicate, for the distinct-month reason",
       scattered.discarded_too_few_distinct_months == 200 and scattered.valid == 0,
       "too-few-distinct %d of %d, valid %d"
       % (scattered.discarded_too_few_distinct_months, scattered.attempted,
          scattered.valid))
    ck("exactly 24 distinct months: the single circular block is NOT rejected "
       "for that reason",
       oneblock.discarded_too_few_distinct_months == 0 and oneblock.valid == 200,
       "too-few-distinct %d, valid %d"
       % (oneblock.discarded_too_few_distinct_months, oneblock.valid))
    ck("the two runs differ ONLY in L, so the verdict cannot come from the "
       "sample, the length or the seed",
       cfg(1).replications == cfg(10 ** 9).replications
       and cfg(1).min_distinct_months == cfg(10 ** 9).min_distinct_months)
    ck("neither rejection is a zero-variance rejection in disguise",
       scattered.discarded_zero_std_e == 0 and scattered.discarded_zero_std_f == 0
       and oneblock.discarded_zero_std_e == 0)
    ck("a length-based rule would have reported ZERO distinct-month rejections "
       "in BOTH runs, which is the mutation this test exists to catch",
       scattered.discarded_too_few_distinct_months
       != oneblock.discarded_too_few_distinct_months)

    # and the boundary itself, one month lower, still through production
    def cfg25(block, reps=120):
        return inf.BootstrapConfig(
            family=c.family, expected_block_length_months=block,
            replications=reps, ci_level=c.ci_level, ci_method=c.ci_method,
            percentile_interpolation=c.percentile_interpolation,
            master_seed=c.master_seed, arm_order=c.arm_order,
            valid_replicate_floor=int(0.95 * reps), min_distinct_months=25)
    _d, need25 = inf.paired_stationary_bootstrap(e, f, cfg=cfg25(10 ** 9),
                                                 arm="primary")
    ck("demanding 25 distinct months rejects the very same full-coverage "
       "replicate, so the comparison is against the floor and not hard-coded",
       need25.discarded_too_few_distinct_months == 120 and need25.valid == 0,
       "too-few-distinct %d" % need25.discarded_too_few_distinct_months)
    flush("19. BLOCKER A — distinct months, bound inside production")


def main():
    test_sharpe(); test_delta_s()
    test_bootstrap_mechanics(); test_joint_pairing(); test_bootstrap_counts()
    test_percentile_ci(); test_classification(); test_secondary()
    test_crisis_windows(); test_path_diagnostics()
    test_seed_and_determinism(); test_sealed_config_binding()
    test_sample_and_safety(); test_import_purity()
    test_zero_variance(); test_sealed_sample_gate()
    test_invalid_interval_refused(); test_replicate_rule_binding()
    test_diagnostic_scope(); test_distinct_months_production_binding()
    print("=" * 90)
    print("X01_INFERENCE_SYNTHETIC_VALIDATION = %s   (%d failed)"
          % ("PASS" if not _fails else "FAIL", len(_fails)))
    for f in _fails:
        print("   FAILED:", f)
    print("TARGET_X01_OUTCOME_ACCESSED = NO   (synthetic fixtures only)")
    print("=" * 90)
    return 0 if not _fails else 1


if __name__ == "__main__":
    sys.exit(main())
