# -*- coding: utf-8 -*-
"""Value inference and verdict engines.

The bootstrap is REUSED from the sealed X01 engine
(`x01_inference.stationary_bootstrap_indices`) rather than reimplemented: one
index vector per replicate, applied jointly to every leg. An IID interval is
forbidden by the sealed contract and is not implemented anywhere here.

The verdict functions are pure: they take interval bounds and return a token.
They are never wired to real data in S2.
"""
import os
import sys

import numpy as np

from value_contract import (BLOCK_LENGTH_MONTHS, BOOTSTRAP_REPS, CI_LEVEL,
                            DELTA_COMBO, E_POSITIVE, F_ADVERSE,
                            INCREMENTAL_BENEFIT_ADVERSE,
                            INCREMENTAL_BENEFIT_NOT_ESTABLISHED,
                            K_EPISODES, MASTER_SEED, MATERIALLY_ADVERSE,
                            MIN_DISTINCT_MONTHS, RHO_MAX,
                            SUPPORTED_INCREMENTAL_BENEFIT,
                            SUPPORTED_POSITIVE_EDGE, UNRESOLVED_EDGE,
                            VALID_REPLICATE_FLOOR, ARM_ORDER)

_X01 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "x01")
if _X01 not in sys.path:
    sys.path.insert(0, os.path.abspath(_X01))
import x01_inference as x01inf          # noqa: E402  (reused, never modified)

SHARPE_PERIODS_PER_YEAR = 12


class InferenceInvalid(ValueError):
    """The reduced sample cannot support a valid interval. Never a pass."""


# --------------------------------------------------------------------------- #
# statistics
# --------------------------------------------------------------------------- #
def sharpe(x):
    x = np.asarray(x, dtype=float)
    if x.size < 2:
        return None
    sd = x.std(ddof=1)
    if not np.isfinite(sd) or sd <= 0:
        return None
    return float(x.mean() / sd * np.sqrt(SHARPE_PERIODS_PER_YEAR))


def pearson(a, b):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    if a.size < 2 or a.size != b.size:
        return None
    sa, sb = a.std(ddof=1), b.std(ddof=1)
    if not np.isfinite(sa) or not np.isfinite(sb) or sa <= 0 or sb <= 0:
        return None
    return float(((a - a.mean()) * (b - b.mean())).mean() / (sa * sb)
                 * a.size / (a.size - 1))


def seed_for(arm):
    """SeedSequence(7).spawn in the fixed arm order — the sealed policy."""
    if arm not in ARM_ORDER:
        raise ValueError("unknown arm %r; the arm order is frozen" % (arm,))
    return np.random.SeedSequence(MASTER_SEED).spawn(
        len(ARM_ORDER))[ARM_ORDER.index(arm)]


# --------------------------------------------------------------------------- #
# one bootstrap engine for every interval statistic
# --------------------------------------------------------------------------- #
def bootstrap_ci(columns, statistic, arm, months=None,
                 reps=BOOTSTRAP_REPS, block=BLOCK_LENGTH_MONTHS,
                 level=CI_LEVEL, floor=VALID_REPLICATE_FLOOR,
                 min_distinct=MIN_DISTINCT_MONTHS):
    """Stationary bootstrap with JOINT resampling across every column.

    `columns` is a tuple of equal-length sequences. ONE index vector per
    replicate is applied to all of them, so no month is drawn for one leg and
    not another. `statistic(*resampled_columns)` returns a float or None; None
    counts as an invalid replicate.
    """
    cols = [np.asarray(c, dtype=float) for c in columns]
    n = len(cols[0])
    if any(len(c) != n for c in cols):
        raise InferenceInvalid("columns must be the same length")
    if n < 2:
        raise InferenceInvalid("fewer than two observations")
    months = list(months) if months is not None else list(range(n))

    rng = np.random.default_rng(seed_for(arm))
    vals = []
    counts = {"attempted": 0, "valid": 0, "discarded": 0,
              "discarded_too_few_distinct_months": 0,
              "discarded_degenerate": 0}
    for _ in range(reps):
        counts["attempted"] += 1
        idx = x01inf.stationary_bootstrap_indices(n, block, rng)
        if len({months[i] for i in idx}) < min_distinct:
            counts["discarded"] += 1
            counts["discarded_too_few_distinct_months"] += 1
            continue
        v = statistic(*[c[idx] for c in cols])
        if v is None or not np.isfinite(v):
            counts["discarded"] += 1
            counts["discarded_degenerate"] += 1
            continue
        counts["valid"] += 1
        vals.append(float(v))

    if counts["valid"] < floor:
        raise InferenceInvalid(
            "only %d valid replicates, below the sealed floor of %d"
            % (counts["valid"], floor))
    arr = np.asarray(vals, dtype=float)
    lo = float(np.percentile(arr, (100 - level) / 2.0, method="linear"))
    hi = float(np.percentile(arr, 100 - (100 - level) / 2.0, method="linear"))
    return {"lower": lo, "upper": hi, "level": level,
            "n_valid": counts["valid"], "counts": counts}


def standalone_ci(value_returns, arm="standalone", **kw):
    return bootstrap_ci((value_returns,), lambda v: sharpe(v), arm, **kw)


def correlation_ci(value_returns, tsmom_returns, arm="correlation", **kw):
    """C2's interval. The resampling unit is the JOINT monthly pair."""
    return bootstrap_ci((value_returns, tsmom_returns),
                        lambda v, t: pearson(v, t), arm, **kw)


def combo_ci(tsmom_returns, combined_returns, arm="combo", **kw):
    """ΔS_combo = Sharpe(TSMOM + Value) − Sharpe(TSMOM), paired."""
    def delta(t, c):
        st, sc = sharpe(t), sharpe(c)
        return None if st is None or sc is None else sc - st
    return bootstrap_ci((tsmom_returns, combined_returns), delta, arm, **kw)


# --------------------------------------------------------------------------- #
# verdict engines — pure functions of interval bounds (§7, §9)
# --------------------------------------------------------------------------- #
def standalone_verdict(lower, upper, e=E_POSITIVE, f=F_ADVERSE):
    """Strict inequalities; a boundary touch is UNRESOLVED by construction."""
    if lower > e:
        return SUPPORTED_POSITIVE_EDGE
    if upper < -f:
        return MATERIALLY_ADVERSE
    return UNRESOLVED_EDGE


def combo_verdict(lower, upper, delta=DELTA_COMBO):
    """Strict inequalities; a boundary touch is NOT_ESTABLISHED.

    ADVERSE and NOT_ESTABLISHED are different findings and never share a label.
    """
    if lower > delta:
        return SUPPORTED_INCREMENTAL_BENEFIT
    if upper < 0.0:
        return INCREMENTAL_BENEFIT_ADVERSE
    return INCREMENTAL_BENEFIT_NOT_ESTABLISHED


# --------------------------------------------------------------------------- #
# candidacy  (§8)
# --------------------------------------------------------------------------- #
def c1_pass(standalone_state):
    return standalone_state != MATERIALLY_ADVERSE


def c2_pass(rho_upper, rho_max=RHO_MAX):
    """Adjudicated on the CI UPPER bound. `<=` passes, so rho_max exactly passes."""
    return rho_upper is not None and rho_upper <= rho_max


def c3_pass(jackknife_cases, k=K_EPISODES):
    """C3: C1 AND C2 must both pass in EVERY leave-one-episode-out case.

    `jackknife_cases` is a list of dicts {"c1": bool, "c2": bool} of length k, or
    entries carrying "invalid": True. An invalid reduced-sample inference is a
    FAIL — never a pass by default. Sign stability plays no part.
    """
    if jackknife_cases is None or len(jackknife_cases) != k:
        return False
    for case in jackknife_cases:
        if case.get("invalid"):
            return False
        if not (case.get("c1") and case.get("c2")):
            return False
    return True


def candidacy(standalone_state, rho_upper, jackknife_cases):
    c1 = c1_pass(standalone_state)
    c2 = c2_pass(rho_upper)
    c3 = c3_pass(jackknife_cases)
    return {"c1": c1, "c2": c2, "c3": c3, "candidate": bool(c1 and c2 and c3)}


def run_c3_ablation(window_months, episodes, adjudicate, k=K_EPISODES):
    """Apply the sealed CONTRIBUTION-ABLATION operator to each selected episode.

    VALUE_S1_EPISODE_REACHABILITY_AMENDMENT_003. The prior operator deleted an
    episode's whole calendar months from the paired sample, which on the real
    signal path removed almost the entire window and made C3 unadjudicable. The
    sealed operator now removes only the episode instrument's own attributed net
    contribution in the mapped contribution months, retaining every calendar
    month, every other instrument and all shared terms.

    `adjudicate(episode)` returns {"c1": bool, "c2": bool, ...} or raises
    InferenceInvalid, which is recorded as an invalid case and therefore a FAIL.
    Each case starts from the ORIGINAL series: ablations are never cumulative.
    """
    cases = []
    for e in episodes[:k]:
        try:
            r = adjudicate(e)
            case = dict(r)
            case.update({"c1": bool(r["c1"]), "c2": bool(r["c2"]),
                         "invalid": False})
        except InferenceInvalid as exc:
            case = {"c1": False, "c2": False, "invalid": True,
                    "reason": str(exc)}
        case["episode"] = repr(e)
        cases.append(case)
    return cases
