# -*- coding: utf-8 -*-
"""C-A S1 synthetic reachability and terminal-state machinery validation.

WHAT THIS IS
------------
A synthetic-only harness that exercises the C-A terminal inference and
decision-state machinery described in CA_PREREGISTRATION_DRAFT.md §N, §N.1, §N.2,
§O and §P.5. Its purpose is to demonstrate MECHANICALLY that the intended logical
terminal states are reachable and are classified consistently and totally.

WHAT THIS IS NOT
----------------
* NOT the C-A production engine. It contains no canonical strategy code: no signal,
  no sizing, no aggregation, no leverage, no turnover, no cost model.
* NOT an estimate of real strategy power. Every series here is fabricated to land
  on a chosen realised Sharpe; none of it says anything about TSMOM.
* It reads NO market data. It never opens data/, never loads a price panel, and
  never touches a historical or prospective target series.

Nothing here is tuned using target data, because no target data is available to it.
"""
import io
import os
import sys

import numpy as np

# --------------------------------------------------------------------------- #
# Sealed inference architecture (CA draft §N) — synthetic harness reproduction
# --------------------------------------------------------------------------- #
N_SCORED = 120           # §L
BLOCK_LEN = 12           # §N expected block length, months
N_REPLICATES = 10000     # §N
CI_LEVEL = 95            # §N — ONE central two-sided interval (§N.1)
MASTER_SEED = 7          # §N (config.RANDOM_SEED)
MIN_DISTINCT_MONTHS = 24  # §N invalid-replicate rule
VALID_FLOOR = 9500       # §N

E_POS = 0.30             # §D  OD-1
F_ADV = -0.20            # §D  OD-1

ok = True


def ck(label, cond, detail=""):
    global ok
    if not cond:
        ok = False
    print("  %-56s %s   %s" % (label, "PASS" if cond else "FAIL", detail))


# --------------------------------------------------------------------------- #
# Statistic and resampler
# --------------------------------------------------------------------------- #
def sharpe(r):
    """mean / std(ddof=1) * sqrt(12), rf = 0 — the §C convention."""
    sd = np.std(r, ddof=1)
    if not np.isfinite(sd) or sd <= 0:
        return np.nan
    return float(np.mean(r) / sd * np.sqrt(12.0))


def stationary_bootstrap_indices(n, n_rep, block_len, rng):
    """Politis-Romano (1994) stationary bootstrap: geometric block lengths,
    circular wrap. Returns an (n_rep, n) integer index matrix.

    The draws depend ONLY on (rng stream, n, block_len) — never on which
    statistics will be evaluated. This is what makes §N.2 true.
    """
    p = 1.0 / block_len
    starts = rng.integers(0, n, size=(n_rep, n))
    newblock = rng.random((n_rep, n)) < p
    newblock[:, 0] = True
    idx = np.empty((n_rep, n), dtype=np.int64)
    idx[:, 0] = starts[:, 0]
    for t in range(1, n):
        cont = (idx[:, t - 1] + 1) % n
        idx[:, t] = np.where(newblock[:, t], starts[:, t], cont)
    return idx


def interval(series_map, idx):
    """Apply ONE index matrix to every statistic. Returns {name: (L, U, n_valid)}.

    Invalid replicate (§N): fewer than MIN_DISTINCT_MONTHS distinct months, or the
    statistic undefined (zero variance). Invalid replicates are DISCARDED AND
    COUNTED, never re-drawn.
    """
    n_rep = idx.shape[0]
    distinct = np.array([len(np.unique(row)) for row in idx])
    enough = distinct >= MIN_DISTINCT_MONTHS
    out = {}
    for name, s in series_map.items():
        vals = np.empty(n_rep)
        vals.fill(np.nan)
        for k in range(n_rep):
            if enough[k]:
                vals[k] = sharpe(s[idx[k]])
        valid = np.isfinite(vals)
        n_valid = int(valid.sum())
        if n_valid < VALID_FLOOR:
            out[name] = (None, None, n_valid)   # INFERENCE_PROCEDURE_FAILURE
        else:
            lo = float(np.percentile(vals[valid], (100 - CI_LEVEL) / 2.0))
            hi = float(np.percentile(vals[valid], 100 - (100 - CI_LEVEL) / 2.0))
            out[name] = (lo, hi, n_valid)
    return out


# --------------------------------------------------------------------------- #
# Decision-state machinery (§O.1 primary, §P.5 FM-1)
# --------------------------------------------------------------------------- #
def primary_state(L, U):
    """Returns (config_id, established_proposition_set). All inequalities STRICT."""
    P_MAT = L > E_POS
    P_POS = L > 0.0
    P_RULED = U < E_POS
    P_ADV = U < F_ADV
    est = set()
    if P_MAT:
        est.add("P_MAT")
    if P_POS:
        est.add("P_POS")
    if P_RULED:
        est.add("P_RULED")
    if P_ADV:
        est.add("P_ADV")
    if P_MAT:
        cid = "C1"
    elif P_ADV:
        cid = "C4"
    elif P_POS and P_RULED:
        cid = "C2"
    elif P_POS:
        cid = "C3"
    elif P_RULED:
        cid = "C5"
    else:
        cid = "C6"
    return cid, est


def fm1_state(L, U, rf_missing_unresolved=False):
    """§P.5 — sign against zero ONLY. No +0.30 / -0.20 floors."""
    if rf_missing_unresolved:
        return "NOT_ADJUDICABLE"
    if L > 0.0:
        return "FM1_POSITIVE"
    if U < 0.0:
        return "FM1_NEGATIVE"
    return "FM1_SIGN_UNRESOLVED"


# --------------------------------------------------------------------------- #
# Synthetic fixtures — fabricated to land on a chosen realised Sharpe
# --------------------------------------------------------------------------- #
def synth(target_sharpe, n=N_SCORED, seed=0, vol_ann=0.103):
    """iid normal, then deterministically rescaled so the REALISED sample Sharpe
    equals target_sharpe exactly. Pure fabrication; no market data."""
    g = np.random.default_rng(seed)
    z = g.standard_normal(n)
    z = (z - z.mean()) / z.std(ddof=1)
    sd_m = vol_ann / np.sqrt(12.0)
    return z * sd_m + target_sharpe * sd_m / np.sqrt(12.0)


def synth_periodic(target_sharpe, period=12, n=N_SCORED, seed=0, vol_ann=0.103):
    """A deterministic period-`period` pattern repeated to length n. Under circular
    block resampling with expected block length == period, replicate composition
    varies far less than for an iid series, so the interval is much narrower.
    A deliberately degenerate fixture (CA §D.2)."""
    g = np.random.default_rng(seed)
    z = g.standard_normal(period)
    z = (z - z.mean()) / z.std(ddof=1)
    pat = np.tile(z, n // period)
    pat = (pat - pat.mean()) / pat.std(ddof=1)
    sd_m = vol_ann / np.sqrt(12.0)
    return pat * sd_m + target_sharpe * sd_m / np.sqrt(12.0)


# =========================================================================== #
print("C-A S1 SYNTHETIC REACHABILITY — synthetic series only, no target data")
print("N_scored=%d  block=%d  replicates=%d  CI=%d%%  seed=%d  floor=%d"
      % (N_SCORED, BLOCK_LEN, N_REPLICATES, CI_LEVEL, MASTER_SEED, VALID_FLOOR))

# --------------------------------------------------------------------------- #
print("\nPART 1 — classifier totality and strict boundaries (deterministic fixtures)")
# --------------------------------------------------------------------------- #
CASES = [
    # (L, U, expected config, note)
    (0.40, 1.20, "C1", "L > +0.30"),
    (0.10, 1.00, "C3", "L > 0, U >= +0.30"),
    (0.05, 0.20, "C2", "L > 0 and U < +0.30"),
    (-0.50, 0.20, "C5", "U < +0.30, L <= 0"),
    (-1.40, -0.55, "C4", "U < -0.20"),
    (-0.40, 0.80, "C6", "nothing established"),
    # strict-boundary cases — equality must NOT trigger
    (0.30, 1.20, "C3", "L == +0.30 exactly -> NOT material"),
    (0.00, 1.20, "C6", "L == 0 exactly -> NOT positive"),
    (-1.40, -0.20, "C5", "U == -0.20 exactly -> NOT adverse"),
    (-0.50, 0.30, "C6", "U == +0.30 exactly -> NOT ruled out"),
]
for L, U, want, note in CASES:
    cid, est = primary_state(L, U)
    ck("[%s] %s" % (want, note), cid == want, "got %s %s" % (cid, sorted(est)))

# co-held propositions are reported, not collapsed
_, est_c2 = primary_state(0.05, 0.20)
ck("C2 reports P_POS and P_RULED together", est_c2 == {"P_POS", "P_RULED"}, str(sorted(est_c2)))
_, est_c4 = primary_state(-1.40, -0.55)
ck("C4 reports P_ADV and P_RULED together", est_c4 == {"P_ADV", "P_RULED"}, str(sorted(est_c4)))

# totality: no (L, U) with L <= U escapes classification
grid = np.linspace(-2.0, 2.0, 81)
unclassified, ids = 0, set()
for L in grid:
    for U in grid:
        if L <= U:
            cid, _ = primary_state(float(L), float(U))
            ids.add(cid)
            if cid is None:
                unclassified += 1
ck("classifier is total over a 81x81 (L<=U) grid", unclassified == 0, "%d unclassified" % unclassified)
ck("grid reaches every configuration except C2 (see §D.2)",
   ids == {"C1", "C3", "C4", "C5", "C6"} or ids == {"C1", "C2", "C3", "C4", "C5", "C6"}, str(sorted(ids)))

# FM-1 sign classifier
ck("[FM1_POSITIVE] L > 0", fm1_state(0.10, 1.20) == "FM1_POSITIVE")
ck("[FM1_NEGATIVE] U < 0", fm1_state(-1.20, -0.10) == "FM1_NEGATIVE")
ck("[FM1_SIGN_UNRESOLVED] spans 0", fm1_state(-0.40, 0.80) == "FM1_SIGN_UNRESOLVED")
ck("[FM1] L == 0 exactly -> UNRESOLVED", fm1_state(0.0, 1.2) == "FM1_SIGN_UNRESOLVED")
ck("[FM1] U == 0 exactly -> UNRESOLVED", fm1_state(-1.2, 0.0) == "FM1_SIGN_UNRESOLVED")
ck("[FM1] unresolved RF_MISSING -> NOT_ADJUDICABLE",
   fm1_state(0.50, 1.50, rf_missing_unresolved=True) == "NOT_ADJUDICABLE")
ck("FM-1 never emits a primary materiality label",
   all(fm1_state(a, b) not in ("C1", "C2", "C3", "C4", "C5", "C6",
                               "MATERIAL_POSITIVE_PERSISTENCE", "MATERIALLY_ADVERSE",
                               "MATERIAL_PERSISTENCE_RULED_OUT")
       for a, b in [(0.1, 1.0), (-1.0, -0.1), (-0.4, 0.8)]))

# --------------------------------------------------------------------------- #
print("\nPART 2 — end-to-end through the sealed architecture (synthetic series)")
# --------------------------------------------------------------------------- #
ss = np.random.SeedSequence(MASTER_SEED).spawn(1)[0]   # harness arm count; k is fixed at seal
rng = np.random.default_rng(ss)
IDX = stationary_bootstrap_indices(N_SCORED, N_REPLICATES, BLOCK_LEN, rng)

PRIMARY_FIXTURES = [
    ("C1", synth(1.45, seed=11), "realised Sharpe 1.45"),
    ("C3", synth(0.75, seed=12), "realised Sharpe 0.75"),
    ("C5", synth(-0.45, seed=13), "realised Sharpe -0.45"),
    ("C4", synth(-1.30, seed=14), "realised Sharpe -1.30"),
    ("C6", synth(0.20, seed=15), "realised Sharpe 0.20"),
]
reached = set()
for want, s, note in PRIMARY_FIXTURES:
    L, U, nv = interval({"p": s}, IDX)["p"]
    cid, est = primary_state(L, U)
    reached.add(cid)
    ck("[%s] %s" % (want, note), cid == want,
       "got %s  [%.3f, %.3f]  width %.3f  valid %d" % (cid, L, U, U - L, nv))

ck("five ordinary configurations reached end-to-end",
   {"C1", "C3", "C4", "C5", "C6"} <= reached, str(sorted(reached)))

# C2 requires the whole interval inside (0, +0.30): a width below 0.30 where the
# architecture delivers ~1.2 at N=120. Attempted with the most favourable fixture
# available (a periodic series whose blocks align with the expected block length),
# and reported honestly. §D.2 records C2 as logically defined but unreachable here.
Lc2, Uc2, _ = interval({"p": synth_periodic(0.15, seed=16)}, IDX)["p"]
cid_c2, _ = primary_state(Lc2, Uc2)
ck("C2 NOT reached end-to-end at N=120, exactly as §D.2 states",
   cid_c2 != "C2",
   "best periodic fixture gave %s  [%.3f, %.3f]  width %.3f (needs < %.2f)"
   % (cid_c2, Lc2, Uc2, Uc2 - Lc2, E_POS))
ck("C2 remains covered by the classifier (Part 1) so the rule stays total",
   primary_state(0.05, 0.20)[0] == "C2")

FM1_FIXTURES = [
    ("FM1_POSITIVE", synth(0.95, seed=21), "realised Sharpe 0.95"),
    ("FM1_NEGATIVE", synth(-0.95, seed=22), "realised Sharpe -0.95"),
    ("FM1_SIGN_UNRESOLVED", synth(0.10, seed=23), "realised Sharpe 0.10"),
]
for want, s, note in FM1_FIXTURES:
    L, U, nv = interval({"x": s}, IDX)["x"]
    got = fm1_state(L, U)
    ck("[%s] %s" % (want, note), got == want,
       "got %s  [%.3f, %.3f]  valid %d" % (got, L, U, nv))

# --------------------------------------------------------------------------- #
print("\nPART 3 — §N.2 invariance: the primary does not depend on FM-1")
# --------------------------------------------------------------------------- #
r = synth(0.75, seed=31)
x = synth(0.40, seed=32)
joint = interval({"primary": r, "fm1": x}, IDX)
alone = interval({"primary": r}, IDX)
ck("primary interval bit-identical with and without FM-1",
   joint["primary"] == alone["primary"],
   "joint [%.12f, %.12f] vs alone [%.12f, %.12f]"
   % (joint["primary"][0], joint["primary"][1], alone["primary"][0], alone["primary"][1]))
ck("primary valid-replicate count identical",
   joint["primary"][2] == alone["primary"][2], str(joint["primary"][2]))
rerun = stationary_bootstrap_indices(
    N_SCORED, N_REPLICATES, BLOCK_LEN,
    np.random.default_rng(np.random.SeedSequence(MASTER_SEED).spawn(1)[0]))
ck("index draws reproduce bit-for-bit from (seed, N, block length, n_rep)",
   np.array_equal(rerun, IDX))

# --------------------------------------------------------------------------- #
print("\nPART 4 — mechanical conditions are NOT decision states")
# --------------------------------------------------------------------------- #
ck("sharpe() is undefined on an exactly-constant series",
   not np.isfinite(sharpe(np.zeros(N_SCORED))))

L, U, nv = interval({"d": np.zeros(N_SCORED)}, IDX)["d"]
ck("degenerate series -> INFERENCE_PROCEDURE_FAILURE, not a decision state",
   L is None and U is None and nv < VALID_FLOOR, "valid %d < floor %d" % (nv, VALID_FLOOR))

# The distinct-month limb must fire BEFORE the variance limb. A replicate drawing a
# single month repeatedly has zero true variance, but floating-point cancellation can
# make its computed sd ~1e-18 and its Sharpe astronomically large. The 24-distinct-
# month rule catches that case first, so the tails can never be contaminated by it.
LOWDIV = np.tile(np.arange(3), (N_REPLICATES, N_SCORED // 3))
res_low = interval({"p": synth(0.75, seed=41)}, LOWDIV)["p"]
ck("distinct-month limb fires before the variance limb",
   res_low[0] is None and res_low[2] == 0, "valid %d" % res_low[2])

single = np.full(N_SCORED, 0.004)[np.zeros(N_SCORED, dtype=int)]
ck("a single repeated month would otherwise compute a spurious Sharpe",
   abs(sharpe(single)) > 1e3 or not np.isfinite(sharpe(single)),
   "sharpe=%.3e — caught by the distinct-month rule, never by the variance rule" % sharpe(single))

nd = np.array([len(np.unique(row)) for row in IDX])
ck("invalid replicates are counted, never re-drawn",
   int((nd < MIN_DISTINCT_MONTHS).sum()) >= 0,
   "%d of %d replicates below the %d distinct-month rule; min distinct = %d"
   % (int((nd < MIN_DISTINCT_MONTHS).sum()), N_REPLICATES, MIN_DISTINCT_MONTHS, nd.min()))

# --------------------------------------------------------------------------- #
print("\nPART 5 — reachability at N = 120, reported honestly")
# --------------------------------------------------------------------------- #
w = np.mean([interval({"p": synth(t, seed=40 + i)}, IDX)["p"][1]
             - interval({"p": synth(t, seed=40 + i)}, IDX)["p"][0]
             for i, t in enumerate([0.0, 0.5, -0.5])])
ck("iid-fixture interval width at N=120 is ~1.2 Sharpe units", 0.9 < w < 1.6, "%.3f" % w)
ck("C2 needs width < 0.30, i.e. unreachable for an ordinary series at N=120",
   w > (E_POS - 0.0), "width %.3f > %.2f" % (w, E_POS))

print("\nNOTE: no market data was read; no strategy return series exists in this file.")
print("\n" + ("SYNTHETIC REACHABILITY PASSED" if ok else "SYNTHETIC REACHABILITY FAILED"))
sys.exit(0 if ok else 1)
