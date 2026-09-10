"""X01 sealed inference layer — INFERENCE ONLY, NO CONSTRUCTION, NO EXECUTION.

What this module is
-------------------
The statistics half of the sealed X01 contract: the part §6.1 freezes and the
construction layer deliberately does not contain. Given two **already
constructed** paired monthly net return series it produces

* ``Sharpe(E)`` and ``Sharpe(F)``            (§4)
* the primary scalar ``ΔS = Sharpe(F) − Sharpe(E)``  (§4)
* a **paired, jointly resampled** stationary bootstrap of ``ΔS``  (§6.1)
* the 95 % **percentile** interval and its valid-replicate accounting (§6.1)
* the three-state classification against ``−B = −0.15``  (§5)
* S1 / S2 as **descriptive sensitivities with no verdict**  (§8.3)
* the two sealed crisis windows  (§7.1)
* the sealed §7 path diagnostics.

What this module is NOT
-----------------------
It **constructs nothing and reads nothing**. It never opens the ETF panel or a
parquet file, never calls ``construct_E`` or ``construct_futures_leg``, never
learns where target data lives, never writes a result file, never touches a
ledger and never authorizes execution. Every input arrives as an explicit
argument. Importing it performs no computation and reads no data file — both
asserted by test.

Construction and inference stay separated in both directions: the construction
module holds no statistic, and this module holds no construction.

Where the numbers come from
---------------------------
Nothing here is a design choice. Every value traces to the sealed
preregistration, and the three that §6.1 delegates to ``config.py``
(``BOOTSTRAP_N``, ``CI_LEVEL``, ``RANDOM_SEED``) are **read from there** rather
than retyped, then checked against the sealed literals so a drift in either
fails closed instead of passing silently.
"""

from __future__ import annotations

import importlib.util
import math
import os
import sys
from dataclasses import dataclass, field

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

# --------------------------------------------------------------------------- #
# Sealed constants — each with the section that fixes it.
# --------------------------------------------------------------------------- #
SHARPE_PERIODS_PER_YEAR = 12          # §4: monthly returns, annualised by √12
BOUNDARY_B = 0.15                     # §5 / §15 O-2: ADOPTED, and not alterable
BOOTSTRAP_FAMILY = "stationary_bootstrap_politis_romano_1994"   # §6.1
ARM_ORDER = ("primary", "S1", "S2")   # §6.1, the fixed spawn order
VALID_REPLICATE_FLOOR = 9500          # §6.1
MIN_DISTINCT_MONTHS = 24              # §6.1 / §4
EXPECTED_PAIRED_MONTHS = 179          # §3.5
SEALED_FIRST_PAIRED_MONTH_END = "2011-07-31"   # §3.5
SEALED_LAST_PAIRED_MONTH_END = "2026-05-31"    # §3.5, after the §3.1 exclusion
CI_METHOD = "percentile"              # §6.1 — BCa deliberately rejected there
PERCENTILE_INTERPOLATION = "linear"   # numpy's default, recorded not hidden

# §7.1, both windows inclusive of their endpoint months. The COVID window is the
# repository's pre-existing canonical `config.REGIMES["COVID 2020"]` expressed as
# the three month-ends it contains; 2020-02-29 is the leap day.
COVID_2020_MONTH_ENDS = ("2020-02-29", "2020-03-31", "2020-04-30")
CY2022_BOUNDS = ("2022-01-31", "2022-12-31")

# §5 outcome states, verbatim.
PRESERVATION = "PRESERVATION_SUPPORTED"
DEGRADATION = "MATERIAL_DEGRADATION_SUPPORTED"
UNRESOLVED = "UNRESOLVED_INSUFFICIENT_PRECISION"
# §6.1: a mechanical condition, explicitly NOT one of the three outcome states.
PROCEDURE_FAILURE = "INFERENCE_PROCEDURE_FAILURE"


class SealedSampleViolation(ValueError):
    """The supplied paired sample is not the sealed evaluation calendar.

    Raised rather than returned. §4 requires "all 179 paired months present" for
    the point estimate, so a shortened, reordered, duplicated or non-finite
    sample is not a weaker version of the study — it is a different one. Silently
    intersecting a missing month away would hand back a verdict computed on a
    sample nobody preregistered.
    """


class InvalidIntervalError(ValueError):
    """A classification was attempted on an interval that is not a valid one.

    §5's three states partition the real line for every `(L, U)` with `L <= U`.
    A NaN or infinite endpoint is outside that domain entirely, so mapping it to
    any of the three would convert a MECHANICAL failure into a research outcome.
    """

# §8.3, the sealed secondary regime.
SECONDARY_INFERENCE_ROLE = "DESCRIPTIVE_SENSITIVITY"
S1_S2_PROMOTION_POWER = "NONE"
SECONDARY_MATERIALITY_GATE = "NONE"
BH_FDR_REQUIRED = False

_ACCEPTED = {}


def accepted():
    """Load the accepted performance module lazily, under a private namespace.

    Lazy so importing this module touches nothing. Private namespace because
    both this repository and the carry repository ship a top-level ``src``
    package; a bare ``from src import performance`` resolves to whichever path
    happens to come first. This is the same defence the construction layer uses,
    reached independently — this module does not import the construction layer,
    so the two halves stay separable.
    """
    if _ACCEPTED:
        return _ACCEPTED
    if REPO not in sys.path:
        sys.path.insert(0, REPO)          # performance.py does a bare `import config`
    import types

    pkg_name = "x01_inf_src"
    if pkg_name not in sys.modules:
        pkg = types.ModuleType(pkg_name)
        pkg.__path__ = [os.path.join(REPO, "src")]
        sys.modules[pkg_name] = pkg

    def _load_sub(short):
        full = "%s.%s" % (pkg_name, short)
        if full in sys.modules:
            return sys.modules[full]
        spec = importlib.util.spec_from_file_location(
            full, os.path.join(REPO, "src", short + ".py"))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[full] = mod
        spec.loader.exec_module(mod)
        setattr(sys.modules[pkg_name], short, mod)
        return mod

    import config as tsmom_config                       # noqa: E402
    _ACCEPTED["performance"] = _load_sub("performance")
    _ACCEPTED["config"] = tsmom_config
    return _ACCEPTED


def sealed_bootstrap_config():
    """The frozen §6.1 procedure, read from the sources the seal names.

    §6.1 delegates three values to ``config.py`` by name — ``BOOTSTRAP_N``,
    ``CI_LEVEL`` and ``RANDOM_SEED`` — so they are READ from there rather than
    retyped here, and then checked against the sealed literals. If the two ever
    disagree this raises instead of quietly preferring one: a pinned input that
    has moved under a sealed contract is a stop condition, not a preference.

    ``L`` is likewise derived, not asserted: §6.1 anchors the expected block
    length to "the longest signal-formation window", which is
    ``max(MOMENTUM_LOOKBACKS_MONTHS)``.
    """
    cfg = accepted()["config"]
    n = int(cfg.BOOTSTRAP_N)
    level = int(cfg.CI_LEVEL)
    seed = int(cfg.RANDOM_SEED)
    block = int(max(cfg.MOMENTUM_LOOKBACKS_MONTHS))
    sealed = {"replications": 10000, "ci_level": 95, "master_seed": 7,
              "expected_block_length_months": 12}
    got = {"replications": n, "ci_level": level, "master_seed": seed,
           "expected_block_length_months": block}
    if got != sealed:
        raise ValueError(
            "config.py no longer reproduces the sealed §6.1 values: %r vs sealed %r"
            % (got, sealed))
    return BootstrapConfig(
        family=BOOTSTRAP_FAMILY, expected_block_length_months=block,
        replications=n, ci_level=level, ci_method=CI_METHOD,
        percentile_interpolation=PERCENTILE_INTERPOLATION,
        master_seed=seed, arm_order=list(ARM_ORDER),
        valid_replicate_floor=VALID_REPLICATE_FLOOR,
        min_distinct_months=MIN_DISTINCT_MONTHS)


def arm_seed_sequence(arm):
    """The sealed per-arm child stream: ``SeedSequence(7).spawn(3)``, fixed order.

    This is NOT a second seed system. It is the one sealed derivation, and the
    test suite binds it to the runner's already-frozen ``seed_protocol()`` by
    comparing ``spawn_key`` and the generated-state fingerprint — the two
    properties that actually identify a child, since all three report
    ``entropy == 7`` and that property therefore cannot distinguish them.
    """
    import numpy as np

    if arm not in ARM_ORDER:
        raise ValueError("unknown arm %r; the sealed order is %r" % (arm, ARM_ORDER))
    cfg = accepted()["config"]
    children = np.random.SeedSequence(int(cfg.RANDOM_SEED)).spawn(len(ARM_ORDER))
    return children[ARM_ORDER.index(arm)]


# --------------------------------------------------------------------------- #
# Result types — deterministic, and carrying no more authority than they should
# --------------------------------------------------------------------------- #
class SecondaryArmHasNoVerdict(AttributeError):
    """Raised when code asks a secondary arm for a classification.

    §8.3 gives S1 and S2 ``S1_S2_PROMOTION_POWER = NONE`` and forbids assigning
    any outcome state from them. Making that a runtime error rather than a
    comment is the point: a later caller cannot reach for `.classification` on a
    sensitivity arm by accident.
    """


@dataclass(frozen=True)
class BootstrapConfig:
    family: str
    expected_block_length_months: int
    replications: int
    ci_level: int
    ci_method: str
    percentile_interpolation: str
    master_seed: int
    arm_order: list
    valid_replicate_floor: int
    min_distinct_months: int


@dataclass(frozen=True)
class BootstrapCounts:
    """Attempted / valid / discarded, with the reason each discard fired.

    §6.1 requires invalid replicates to be "discarded and counted — never
    re-drawn", so the counts are part of the result, not debug output.
    """
    attempted: int
    valid: int
    discarded: int
    discarded_too_few_distinct_months: int
    discarded_zero_std_e: int
    discarded_zero_std_f: int

    def __post_init__(self):
        if self.attempted != self.valid + self.discarded:
            raise ValueError("replicate counts do not add up")


@dataclass(frozen=True)
class ConfidenceInterval:
    lower: float
    upper: float
    level: int
    method: str
    n_valid: int


@dataclass(frozen=True)
class SharpePair:
    sharpe_e: float
    sharpe_f: float
    n_months: int
    periods_per_year: int = SHARPE_PERIODS_PER_YEAR


@dataclass(frozen=True)
class PrimaryResult:
    """The one object in this module that carries an outcome state."""
    arm: str
    sharpes: SharpePair
    delta_s: float
    ci: ConfidenceInterval
    counts: BootstrapCounts
    config: BootstrapConfig
    classification: str
    boundary_b: float = BOUNDARY_B
    boundary: float = -BOUNDARY_B


@dataclass(frozen=True)
class SecondaryResult:
    """S1 / S2. Deliberately has no `classification` attribute.

    It reports its own ΔS and interval under the identical §6.1 procedure, as
    §8.3 requires, and nothing else: no p-value, no threshold, no pass/fail
    label, no materiality verdict.
    """
    arm: str
    sharpes: SharpePair
    delta_s: float
    ci: ConfidenceInterval
    counts: BootstrapCounts
    config: BootstrapConfig
    role: str = SECONDARY_INFERENCE_ROLE
    promotion_power: str = S1_S2_PROMOTION_POWER
    materiality_gate: str = SECONDARY_MATERIALITY_GATE
    bh_fdr_required: bool = BH_FDR_REQUIRED

    @property
    def classification(self):
        raise SecondaryArmHasNoVerdict(
            "%s is a DESCRIPTIVE_SENSITIVITY arm (§8.3): it assigns no outcome "
            "state, cannot rescue or replace the primary, and has "
            "S1_S2_PROMOTION_POWER = NONE." % self.arm)


@dataclass(frozen=True)
class WindowDiagnostic:
    name: str
    month_ends: list
    n_months: int
    sharpe_e: float
    sharpe_f: float
    delta_s: float
    role: str = "DESCRIPTIVE_NEVER_A_GATE"


@dataclass(frozen=True)
class PathDiagnostics:
    """§7 / §4 path-level diagnostics. Reported, never gates (§8.0)."""
    n_months: int
    tracking_error_monthly: float
    tracking_error_annualised: float
    max_abs_d: float
    mean_d: float
    pair_correlations: dict = field(default_factory=dict)
    sign_agreement: dict = field(default_factory=dict)
    turnover_e: float = float("nan")
    turnover_f: float = float("nan")
    realised_cost_e: float = float("nan")
    realised_cost_f: float = float("nan")
    role: str = "DESCRIPTIVE_NEVER_A_GATE"


# --------------------------------------------------------------------------- #
# ITEM 1 — Sharpe (§4)
# --------------------------------------------------------------------------- #
def is_degenerate(values):
    """True when a series is MATHEMATICALLY constant, or too short to have a sd.

    §4 makes Sharpe undefined when ``std = 0``. That is a statement about the
    mathematical standard deviation, and a constant series has one exactly.
    Floating-point accumulation does not realise it: 179 copies of ``0.01``
    accumulate to a sample sd of ``1.74e-18`` rather than ``0``, and the sealed
    "undefined" branch is then never taken — the ratio comes out near ``2e16``
    and reads as a performance value.

    So constancy is decided EXACTLY, on the input representation, by comparing
    the finite observations' maximum with their minimum. That introduces no
    statistical threshold and no tolerance: a series is either constant or it is
    not. A genuinely non-constant series with a tiny variance is NOT degenerate
    and is left alone, which is why the test is `max == min` and not `sd < eps`.
    """
    import numpy as np

    v = np.asarray(values, dtype="float64").ravel()
    v = v[np.isfinite(v)]
    if v.size < 2:
        return True
    return bool(v.max() == v.min())


def sharpe(series):
    """Sealed §4 Sharpe, via the accepted primitive, with §4's own zero-variance
    branch decided exactly.

    §4 freezes the statistic as ``src/performance.py::sharpe_ratio`` "unchanged
    and not re-specified here" — ``mean(x) / std(x, ddof=1) * sqrt(12)``, monthly,
    raw returns, no risk-free subtraction, no compounding — and separately fixes
    the branch: ``std = 0`` or ``n < 2`` means UNDEFINED. The primitive is still
    the calculator, and it is called unchanged; what is decided here is only
    which branch §4 puts the input in, because the primitive's float arithmetic
    cannot see that a constant series has ``std = 0``.
    """
    if is_degenerate(series):
        return float("nan")
    return float(accepted()["performance"].sharpe_ratio(
        series, periods_per_year=SHARPE_PERIODS_PER_YEAR))


def _sharpe_vectorised(samples):
    """The same statistic over a (replicates, months) array.

    A 10,000-iteration Python loop calling the accepted scalar primitive would
    compute exactly this, slowly. The test suite pins the two together on random
    inputs rather than trusting that they agree.
    """
    import numpy as np

    mean = samples.mean(axis=1)
    sd = samples.std(axis=1, ddof=1)
    # the same exact constancy test as `is_degenerate`, one row at a time
    constant = samples.max(axis=1) == samples.min(axis=1)
    usable = (sd > 0) & ~constant
    with np.errstate(invalid="ignore", divide="ignore"):
        return (np.where(usable, mean / sd * math.sqrt(SHARPE_PERIODS_PER_YEAR),
                         np.nan), np.where(constant, 0.0, sd))


def sharpe_pair(e, f):
    """Both legs' Sharpes on the SAME paired months (§4)."""
    e, f = align_pair(e, f)
    return SharpePair(sharpe_e=sharpe(e), sharpe_f=sharpe(f), n_months=len(e))


def align_pair(e, f):
    """The paired observation set: identical index on both legs.

    §4 makes ``(F_t, E_t)`` the resampling unit and §3.5 makes the evaluated
    index the INTERSECTION of the two legs. A month present in only one leg is
    not a paired observation, so it is dropped from both — never filled.
    """
    import pandas as pd

    e = pd.Series(e).dropna()
    f = pd.Series(f).dropna()
    idx = e.index.intersection(f.index).sort_values()
    return e.loc[idx], f.loc[idx]


# --------------------------------------------------------------------------- #
# ITEM 2 — the primary scalar (§4)
# --------------------------------------------------------------------------- #
def delta_sharpe(e, f):
    """``ΔS = Sharpe(F) − Sharpe(E)`` — futures MINUS ETF, in that order (§4).

    The order is the sign convention the whole contract rests on: §5 classifies
    against ``−B``, so a NEGATIVE ΔS is the futures leg being worse. Reversing
    the subtraction would silently invert every outcome state.
    """
    pair = sharpe_pair(e, f)
    return pair.sharpe_f - pair.sharpe_e


# --------------------------------------------------------------------------- #
# ITEM 3 — the paired joint stationary bootstrap (§6.1)
# --------------------------------------------------------------------------- #
def distinct_calendar_months(idx):
    """§6.1 counts DISTINCT CALENDAR MONTHS drawn, not the replicate's length.

    Each observation in the paired sample is one month-end, so the number of
    distinct calendar months a replicate spans is the number of distinct indices
    it drew. A replicate of 179 draws that lands on 5 months spans 5 months, not
    179 — substituting the length would let a badly degenerate replicate through.
    """
    import numpy as np

    return int(np.unique(np.asarray(idx)).size)


def stationary_bootstrap_indices(n, expected_block_length, rng):
    """One replicate's index vector — Politis & Romano (1994).

    Geometric block lengths with probability ``1/L`` of starting a new block at
    each step, and a CIRCULAR wrap so no observation is under-sampled at the
    edges. This is the same construction the accepted carry implementation uses
    (`commodity-carry-research/src/stats.py::stationary_bootstrap_sharpe`), which
    cannot be called here: it is single-series, computes a Sharpe rather than a
    paired ΔS, and annualises by √252.

    The properties that make this the stationary bootstrap rather than something
    else are tested directly, not asserted: ``L = 1`` degenerates to IID,
    ``L → ∞`` degenerates to one circular block, and the wrap is exact.
    """
    import numpy as np

    p_restart = 1.0 / float(expected_block_length)
    idx = np.empty(n, dtype=np.int64)
    idx[0] = rng.integers(0, n)
    restarts = rng.random(n) < p_restart
    for i in range(1, n):
        if restarts[i]:
            idx[i] = rng.integers(0, n)
        else:
            idx[i] = (idx[i - 1] + 1) % n
    return idx


def paired_stationary_bootstrap(e, f, cfg=None, arm="primary", seed_sequence=None):
    """Jointly resample ``(F_t, E_t)`` and recompute ΔS inside every replicate.

    The pairing is the whole point of §6.1: ONE index vector is drawn per
    replicate and applied to BOTH legs, so no index is ever drawn for one leg
    that is not drawn for the other. Resampling the legs independently would
    destroy the cross-leg dependence that determines the precision of ΔS, and
    would do so in the direction that makes the interval look better behaved
    than it is.

    Returns ``(delta_s_star, counts)`` where the first is the array of ΔS values
    from the VALID replicates only. Invalid replicates are discarded and
    counted, never re-drawn (§6.1: re-drawing conditions the sample on validity
    and biases the interval).
    """
    import numpy as np

    cfg = sealed_bootstrap_config() if cfg is None else cfg
    e, f = align_pair(e, f)
    ev, fv = e.to_numpy(dtype=float), f.to_numpy(dtype=float)
    n = len(ev)
    if n < 2:
        raise ValueError("a bootstrap needs at least two paired observations")

    ss = arm_seed_sequence(arm) if seed_sequence is None else seed_sequence
    rng = np.random.default_rng(ss)

    idx_all = np.empty((cfg.replications, n), dtype=np.int64)
    for b in range(cfg.replications):
        idx_all[b] = stationary_bootstrap_indices(
            n, cfg.expected_block_length_months, rng)

    e_star = ev[idx_all]                      # SAME indices for both legs
    f_star = fv[idx_all]
    s_e, sd_e = _sharpe_vectorised(e_star)
    s_f, sd_f = _sharpe_vectorised(f_star)

    # §6.1 validity: a positive standard deviation in BOTH legs and at least 24
    # distinct calendar months. Each observation is one month-end, so the number
    # of distinct calendar months drawn is the number of distinct indices.
    distinct = np.array([distinct_calendar_months(row) for row in idx_all])
    too_few = distinct < cfg.min_distinct_months
    zero_e = ~(sd_e > 0)
    zero_f = ~(sd_f > 0)
    invalid = too_few | zero_e | zero_f

    counts = BootstrapCounts(
        attempted=int(cfg.replications),
        valid=int((~invalid).sum()),
        discarded=int(invalid.sum()),
        discarded_too_few_distinct_months=int(too_few.sum()),
        discarded_zero_std_e=int(zero_e.sum()),
        discarded_zero_std_f=int(zero_f.sum()))
    return (s_f - s_e)[~invalid], counts


# --------------------------------------------------------------------------- #
# ITEMS 4 & 5 — validity floor and the percentile interval (§6.1)
# --------------------------------------------------------------------------- #
def percentile_ci(values, level=95, n_valid=None):
    """The sealed percentile interval: 2.5th and 97.5th of the ΔS* values.

    §6.1 chooses percentile over BCa deliberately — BCa's acceleration term is
    estimated from the target sample and would put an outcome-touching component
    inside the interval. No alternative interval is computed anywhere here, so
    none can be selected after the fact.
    """
    import numpy as np

    lo_q = (100.0 - level) / 2.0
    values = np.asarray(values, dtype=float)
    lo, hi = np.percentile(values, [lo_q, 100.0 - lo_q])
    return ConfidenceInterval(
        lower=float(lo), upper=float(hi), level=int(level), method=CI_METHOD,
        n_valid=int(len(values) if n_valid is None else n_valid))


def procedure_failed(counts, cfg):
    """§6.1: fewer than 9,500 valid replicates is a MECHANICAL failure.

    Explicitly not one of the three §5 outcome states. The response is to report
    it with the invalid count — never to widen the interval, lower the floor, or
    re-run under a different seed.
    """
    return counts.valid < cfg.valid_replicate_floor


# --------------------------------------------------------------------------- #
# ITEM 6 — the primary classification (§5)
# --------------------------------------------------------------------------- #
def interval_is_valid(ci):
    """A finite, ordered interval — the only domain §5's partition is defined on."""
    return (ci is not None
            and math.isfinite(ci.lower) and math.isfinite(ci.upper)
            and ci.lower <= ci.upper)


def classify(ci, boundary_b=BOUNDARY_B):
    """The three sealed states, against ``−B`` and never against zero (§5).

        L > −B   → PRESERVATION_SUPPORTED            (strict)
        U < −B   → MATERIAL_DEGRADATION_SUPPORTED    (strict)
        otherwise → UNRESOLVED_INSUFFICIENT_PRECISION (inclusive)

    The comparisons are exact and strict, with no tolerance: §5 states that a
    bound which merely TOUCHES ``−B`` never supports a claim, so ``L = −B`` and
    ``U = −B`` are both UNRESOLVED. Adding an epsilon would convert a sealed
    tie into a claim.
    """
    # A NaN or infinite endpoint, or an inverted interval, is not a weak
    # result — it is not a result. It is refused rather than classified.
    if not interval_is_valid(ci):
        raise InvalidIntervalError(
            "classification requires a finite ordered interval; got "
            "[%r, %r]. A non-finite or inverted interval is a MECHANICAL "
            "inference failure and is never one of the three §5 outcome states."
            % (None if ci is None else ci.lower, None if ci is None else ci.upper))
    boundary = -float(boundary_b)
    if ci.lower > boundary:
        return PRESERVATION
    if ci.upper < boundary:
        return DEGRADATION
    return UNRESOLVED


# --------------------------------------------------------------------------- #
# The primary arm, end to end (§4 → §5 → §6.1)
# --------------------------------------------------------------------------- #
def _run_arm(arm, e, f, cfg, seed_sequence):
    """The unvalidated engine, shared by the primary and the secondaries.

    Deliberately separate from the production entry points: it is the reusable
    low-level path for property tests, and it carries NO sample gate, which is
    exactly why nothing that yields a verdict may call it directly.
    """
    pair = sharpe_pair(e, f)
    dist, counts = paired_stationary_bootstrap(
        e, f, cfg=cfg, arm=arm, seed_sequence=seed_sequence)
    if procedure_failed(counts, cfg):
        ci = ConfidenceInterval(float("nan"), float("nan"), cfg.ci_level,
                                CI_METHOD, counts.valid)
    else:
        ci = percentile_ci(dist, level=cfg.ci_level)
    return pair, dist, counts, ci


def run_primary(e, f, cfg=None, boundary_b=BOUNDARY_B, seed_sequence=None,
                expected_index=None):
    """The single confirmatory test, and the sealed sample gate that guards it.

    The gate runs FIRST and refuses rather than repairs (§3.5/§4). A sample that
    is short by one month is not a slightly weaker study; it is a different one,
    and the previous version quietly intersected a NaN month away and still
    returned a verdict on 178 months.

    `expected_index` exists for tests that need a different calendar of the same
    strict shape. It is NOT an escape hatch: it still demands an exact index
    match, exact ordering, no duplicates, identical indexes on both legs and a
    finite observation everywhere. There is no way to reach this function with an
    unvalidated sample.
    """
    cfg = sealed_bootstrap_config() if cfg is None else cfg
    e, f = require_sealed_sample(e, f, expected_index=expected_index)
    pair = sharpe_pair(e, f)
    dist, counts = paired_stationary_bootstrap(
        e, f, cfg=cfg, arm="primary", seed_sequence=seed_sequence)
    if procedure_failed(counts, cfg):
        ci = ConfidenceInterval(float("nan"), float("nan"), cfg.ci_level,
                                CI_METHOD, counts.valid)
        classification = PROCEDURE_FAILURE
    else:
        ci = percentile_ci(dist, level=cfg.ci_level)
        classification = classify(ci, boundary_b)
    return PrimaryResult(
        arm="primary", sharpes=pair, delta_s=pair.sharpe_f - pair.sharpe_e,
        ci=ci, counts=counts, config=cfg, classification=classification,
        boundary_b=float(boundary_b), boundary=-float(boundary_b))


# --------------------------------------------------------------------------- #
# ITEM 7 — S1 / S2 descriptive sensitivity (§8.3)
# --------------------------------------------------------------------------- #
def run_secondary(arm, e, f, cfg=None, seed_sequence=None, expected_index=None):
    """S1 or S2 under the IDENTICAL §6.1 procedure and its own seeded stream.

    Same machinery, deliberately: §8.3 says the secondaries report "their own ΔS
    point estimate and 95 % interval under the identical §6.1 procedure and
    their own seeded streams, alongside the primary's". What differs is only
    what the result is ALLOWED to do — which is nothing.

    No comparison test between arms is computed here, because §8.3 says none
    exists.
    """
    if arm not in ("S1", "S2"):
        raise ValueError("secondary arms are S1 and S2; got %r" % (arm,))
    cfg = sealed_bootstrap_config() if cfg is None else cfg
    # §8.3 puts the secondaries under the IDENTICAL §6.1 procedure, so they meet
    # the identical sample gate. A sensitivity computed on a different calendar
    # would not characterise the primary's robustness; it would describe
    # something else.
    e, f = require_sealed_sample(e, f, expected_index=expected_index)
    pair, dist, counts, ci = _run_arm(arm, e, f, cfg, seed_sequence)
    return SecondaryResult(
        arm=arm, sharpes=pair, delta_s=pair.sharpe_f - pair.sharpe_e,
        ci=ci, counts=counts, config=cfg)


def primary_classification(result):
    """Read an outcome state, and refuse to read one from a secondary arm.

    §8.3 prohibition 1: "No outcome state is ever assigned from S1 or S2." This
    is that prohibition made mechanical at the one place a caller would reach
    for it.
    """
    if isinstance(result, SecondaryResult):
        raise SecondaryArmHasNoVerdict(
            "%s is a DESCRIPTIVE_SENSITIVITY arm (§8.3) and assigns no outcome "
            "state; the primary alone determines the contract's outcome."
            % result.arm)
    if not isinstance(result, PrimaryResult):
        raise TypeError("expected a PrimaryResult, got %r" % type(result).__name__)
    return result.classification


# --------------------------------------------------------------------------- #
# ITEM 8 — the two sealed crisis windows (§7.1)
# --------------------------------------------------------------------------- #
def crisis_windows(e, f, evaluation_index=None):
    """Exactly the two sealed windows. No others, and no gate.

    §7.1 fixes COVID 2020 as the three month-ends 2020-02-29 / 03-31 / 04-30 —
    the repository's pre-existing canonical regime, adopted verbatim — and CY2022
    as the plain calendar year. ``config.REGIMES`` is deliberately NOT reused
    wholesale: it also carries "Calm 2012-2019", which §7.1 says is not an X01
    window, and "GFC 2008", which the futures panel cannot reach.

    A window statistic is the §4 Sharpe on the subset of evaluated paired months
    whose month-end falls inside the window, on the same net streams. Windows are
    never re-centred, extended, shifted or split, and no crisis result can rescue
    or overturn the primary.
    """
    import pandas as pd

    e, f = align_pair(e, f)
    if evaluation_index is not None:
        # §7.1: "the subset of the 179 EVALUATED paired months whose month-end
        # falls inside the window" — the window is cut from the evaluated
        # sample, never from a longer history that happens to be available.
        e, f = e.loc[evaluation_index], f.loc[evaluation_index]
    out = []

    covid = pd.DatetimeIndex([pd.Timestamp(d) for d in COVID_2020_MONTH_ENDS])
    idx = e.index.intersection(covid)
    out.append(_window(e, f, "COVID 2020", idx))

    lo, hi = (pd.Timestamp(CY2022_BOUNDS[0]), pd.Timestamp(CY2022_BOUNDS[1]))
    idx = e.index[(e.index >= lo) & (e.index <= hi)]
    out.append(_window(e, f, "CY2022", idx))
    return out


def _window(e, f, name, idx):
    es, fs = e.loc[idx], f.loc[idx]
    s_e = sharpe(es) if len(es) >= 2 else float("nan")
    s_f = sharpe(fs) if len(fs) >= 2 else float("nan")
    return WindowDiagnostic(
        name=name, month_ends=[str(d.date()) for d in idx], n_months=len(idx),
        sharpe_e=s_e, sharpe_f=s_f, delta_s=s_f - s_e)


# --------------------------------------------------------------------------- #
# ITEM 9 — the sealed §7 path diagnostics
# --------------------------------------------------------------------------- #
def sign_agreement_rate(signal_e, signal_f, evaluation_index=None):
    """§7 sign-agreement between the ETF and futures COMPOSITE signals.

    The rate definition follows the accepted MAP_v2 X02a diagnostic
    (``research/extensions/wave1/run_x02a_v3.py::sign_agreement``): sign equality
    on the two composites' common index, plus the excluding-flat variant over the
    months where both signs are non-zero. That function reads the frozen ETF
    panel itself, so it cannot be called from a module that must stay data-pure;
    only the rate arithmetic is reproduced, and the tests pin it to a hand-counted
    oracle rather than to the function.

    §7 is explicit that a low rate is a warning requiring investigation, is NOT
    proof of a defect, and grants NO permission to tune the futures construction
    toward higher agreement.
    """
    import numpy as np
    import pandas as pd

    a, b = pd.Series(signal_e), pd.Series(signal_f)
    if evaluation_index is not None:
        # scope FIRST, then intersect where both composites are defined: the
        # warm-up NaNs inside the window are legitimately absent, months outside
        # the window are not diagnostics of this study at all
        a = scope_to_evaluation(a, evaluation_index, "signal_e")
        b = scope_to_evaluation(b, evaluation_index, "signal_f")
    a, b = a.dropna(), b.dropna()
    idx = a.index.intersection(b.index).sort_values()
    if len(idx) == 0:
        return {"status": "NO_OVERLAP", "n_months": 0}
    se, sf = np.sign(a.loc[idx].to_numpy()), np.sign(b.loc[idx].to_numpy())
    agree = se == sf
    both = (se != 0) & (sf != 0)
    return {
        "n_months": int(len(idx)),
        "sign_agreement_rate": float(agree.mean()),
        "sign_agreement_rate_excluding_flat":
            float((se[both] == sf[both]).mean()) if both.any() else None,
        "n_disagree": int((~agree).sum()),
        "role": "DESCRIPTIVE_NEVER_A_GATE",
    }


def pair_correlations(etf_monthly, futures_monthly, evaluation_index=None):
    """§7 monthly return correlation PER MAPPED PAIR.

    Both arguments are frames keyed by the mapped exposure (USO, UNG, GLD, DBA):
    the ETF's own monthly returns and its mapped futures basket's monthly
    returns. Pearson correlation on the pair's common months.

    MAP_v2's "expect ≥ 0.9" is a designer expectation about price pairs, not a
    gate, and no threshold is applied here.
    """
    import pandas as pd

    a, b = pd.DataFrame(etf_monthly), pd.DataFrame(futures_monthly)
    if evaluation_index is not None:
        a = scope_to_evaluation(a, evaluation_index, "etf_monthly")
        b = scope_to_evaluation(b, evaluation_index, "futures_monthly")
    out = {}
    for key in [c for c in a.columns if c in b.columns]:
        x, y = a[key].dropna(), b[key].dropna()
        idx = x.index.intersection(y.index)
        out[key] = {"n_months": int(len(idx)),
                    "correlation": float(x.loc[idx].corr(y.loc[idx]))
                    if len(idx) > 1 else float("nan")}
    return out


def leg_turnover(positions):
    """One-way turnover of a leg's HELD weight frame — E's own convention.

    ``portfolio_returns`` defines E's turnover as ``|Δposition|`` summed across
    the sleeve, so applying the same expression to the futures leg's held frame
    is the symmetric diagnostic §3.6 asks for ("identical to E, element for
    element"). It is computed here, from the frame the construction layer already
    returns, so no frozen construction byte moves.

    This is the WEIGHT turnover. The futures book's traded CONTRACT quantity is a
    different object, it is what actually drives the cash cost, and the frozen
    construction layer does not expose it — recorded as an interface gap rather
    than approximated.
    """
    import pandas as pd

    p = pd.DataFrame(positions)
    return p.diff().abs().sum(axis=1, min_count=1)


def scope_to_evaluation(obj, index, name):
    """Restrict a supplied diagnostic series/frame to the EVALUATED index.

    §7's diagnostics describe the evaluated study, so they are computed on the
    evaluated months and on no others. A caller that hands over a longer history
    — the natural thing to do, since the construction layer returns full
    histories — must not have those extra months silently folded into a
    correlation, a sign-agreement rate or a realised cost.

    Coverage is REQUIRED, not patched: if a supplied object is missing an
    evaluated month, that is refused rather than filled, because inventing the
    row would fabricate a diagnostic observation.
    """
    import pandas as pd

    if obj is None:
        return None
    obj = pd.Series(obj) if isinstance(obj, pd.Series) else pd.DataFrame(obj) \
        if not isinstance(obj, (pd.Series, pd.DataFrame)) else obj
    missing = index.difference(obj.index)
    if len(missing):
        raise SealedSampleViolation(
            "diagnostic input %r does not cover the evaluated index: %d of %d "
            "evaluated month(s) absent (first %s). Diagnostic rows are never "
            "invented to close a gap."
            % (name, len(missing), len(index), str(missing[0].date())))
    return obj.loc[index]


def path_diagnostics(e, f, etf_monthly=None, futures_monthly=None,
                     signal_e=None, signal_f=None,
                     turnover_e=None, turnover_f=None,
                     cost_e=None, cost_f=None, evaluation_index=None):
    """The §7 / §4 diagnostic block. Reported alongside; never a gate (§8.0).

    ``D_t = F_t − E_t``. Tracking error is reported BOTH monthly and annualised
    by √12, each labelled: §4 calls ``D`` "the monthly difference series" and
    names "tracking error" without fixing a scaling, and since the quantity can
    never affect an outcome state, emitting both is honest where silently picking
    one would not be.

    EVERY supplied input is first scoped to the evaluated paired index — the one
    the primary is computed on — so no diagnostic can be computed over months the
    study does not evaluate.
    """
    e, f = align_pair(e, f)
    idx = e.index if evaluation_index is None else evaluation_index
    e, f = e.loc[idx], f.loc[idx]
    etf_monthly = scope_to_evaluation(etf_monthly, idx, "etf_monthly")
    futures_monthly = scope_to_evaluation(futures_monthly, idx, "futures_monthly")
    signal_e = scope_to_evaluation(signal_e, idx, "signal_e")
    signal_f = scope_to_evaluation(signal_f, idx, "signal_f")
    turnover_e = scope_to_evaluation(turnover_e, idx, "turnover_e")
    turnover_f = scope_to_evaluation(turnover_f, idx, "turnover_f")
    cost_e = scope_to_evaluation(cost_e, idx, "cost_e")
    cost_f = scope_to_evaluation(cost_f, idx, "cost_f")
    d = f - e
    sd = float(d.std(ddof=1)) if len(d) > 1 else float("nan")
    return PathDiagnostics(
        n_months=len(d),
        tracking_error_monthly=sd,
        tracking_error_annualised=sd * math.sqrt(SHARPE_PERIODS_PER_YEAR),
        max_abs_d=float(d.abs().max()) if len(d) else float("nan"),
        mean_d=float(d.mean()) if len(d) else float("nan"),
        pair_correlations=(pair_correlations(etf_monthly, futures_monthly)
                           if etf_monthly is not None and futures_monthly is not None
                           else {}),
        sign_agreement=(sign_agreement_rate(signal_e, signal_f)
                        if signal_e is not None and signal_f is not None else {}),
        # E's turnover is its own |Δposition| convention, already returned by
        # `construct_E`. F's is the IDENTITY-trade quantity from the §3.8 book —
        # NOT a weight difference, which is exactly zero across an equal-size
        # roll that in fact trades two sides.
        turnover_e=(float(turnover_e.sum()) if turnover_e is not None
                    else float("nan")),
        turnover_f=(float(turnover_f.sum()) if turnover_f is not None
                    else float("nan")),
        realised_cost_e=(float(cost_e.sum()) if cost_e is not None else float("nan")),
        realised_cost_f=(float(cost_f.sum()) if cost_f is not None else float("nan")))


# --------------------------------------------------------------------------- #
# Sample-rule check (§3.5) — a refusal, not a report
# --------------------------------------------------------------------------- #
def sealed_evaluation_index():
    """The sealed evaluated calendar: 2011-07-31 … 2026-05-31, 179 month-ends.

    Derived from the sealed endpoints rather than stored as a list, and checked
    against the sealed count so a wrong endpoint cannot pass silently.
    """
    import pandas as pd

    idx = pd.date_range(SEALED_FIRST_PAIRED_MONTH_END,
                        SEALED_LAST_PAIRED_MONTH_END, freq="ME")
    if len(idx) != EXPECTED_PAIRED_MONTHS:
        raise SealedSampleViolation(
            "the sealed endpoints no longer span %d month-ends; got %d"
            % (EXPECTED_PAIRED_MONTHS, len(idx)))
    return idx


def require_sealed_sample(e, f, expected_index=None):
    """The production gate: the supplied pair MUST be the sealed calendar.

    Nothing is repaired here. No NaN is dropped, no month is intersected away,
    nothing is back-filled, re-ordered or shortened — because every one of those
    would silently answer a different question than the one preregistered. §4 is
    explicit that the point estimate requires all 179 paired months present, so
    anything else is refused before a single statistic is computed.

    Checked: both legs carry exactly the sealed index, in order, without
    duplicates, with identical indexes, and with a finite observation in every
    month on both legs.
    """
    import numpy as np
    import pandas as pd

    want = sealed_evaluation_index() if expected_index is None else expected_index
    e, f = pd.Series(e), pd.Series(f)
    for name, s in (("E", e), ("F", f)):
        if s.index.has_duplicates:
            raise SealedSampleViolation("%s carries duplicate month-ends" % name)
        if not s.index.is_monotonic_increasing:
            raise SealedSampleViolation("%s is not in ascending month-end order" % name)
    if not e.index.equals(f.index):
        raise SealedSampleViolation(
            "E and F must carry the identical evaluated index; they differ in "
            "%d month(s)" % len(e.index.symmetric_difference(f.index)))
    if not e.index.equals(want):
        missing = want.difference(e.index)
        extra = e.index.difference(want)
        raise SealedSampleViolation(
            "the supplied sample is not the sealed evaluation calendar "
            "(%s … %s, N = %d): %d supplied, %d sealed month(s) missing, "
            "%d unsealed month(s) present"
            % (SEALED_FIRST_PAIRED_MONTH_END, SEALED_LAST_PAIRED_MONTH_END,
               EXPECTED_PAIRED_MONTHS, len(e.index), len(missing), len(extra)))
    for name, s in (("E", e), ("F", f)):
        bad = ~np.isfinite(s.to_numpy(dtype="float64"))
        if bad.any():
            raise SealedSampleViolation(
                "%s has %d non-finite observation(s) in the sealed sample; the "
                "primary point estimate requires all %d paired months present "
                "(§4), and a missing month is never dropped to make one fit."
                % (name, int(bad.sum()), EXPECTED_PAIRED_MONTHS))
    return e, f
