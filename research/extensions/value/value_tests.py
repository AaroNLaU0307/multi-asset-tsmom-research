# -*- coding: utf-8 -*-
"""Synthetic validation of the Value S2 implementation.

Every test uses hand-built fixtures. No real target return, Sharpe, correlation,
combination outcome or verdict is produced anywhere in this file.
"""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import value_contract as C          # noqa: E402
import value_data as D              # noqa: E402
import value_inference as I         # noqa: E402
import value_portfolio as P         # noqa: E402
import value_signal as S            # noqa: E402

_checks = []


def ck(label, cond, detail=""):
    _checks.append((label, bool(cond), detail))


def flush(title):
    width = max(len(l) for l, _c, _d in _checks) if _checks else 10
    print("=" * (width + 22))
    print(title)
    print("=" * (width + 22))
    for label, cond, detail in _checks:
        print("  %-*s %s   %s" % (width, label, "PASS" if cond else "FAIL", detail))
    print()


def _raises(fn, exc):
    try:
        fn()
        return False
    except exc:
        return True
    except Exception:
        return False


# --------------------------------------------------------------------------- #
# 1. month arithmetic and causal availability
# --------------------------------------------------------------------------- #
def test_time_and_availability():
    ck("T1 month keys round-trip", D.m_str(D.m_key("2014-07")) == "2014-07")
    ck("T1 shift crosses a year boundary", D.m_shift("2014-12", 1) == "2015-01")
    ck("T1 the sealed window is exactly N months",
       len(D.m_range(C.EVAL_START, C.EVAL_END)) == C.N_MONTHS,
       "%d" % len(D.m_range(C.EVAL_START, C.EVAL_END)))

    s = {"2020-01": 1.0, "2020-02": 2.0, "2020-03": 3.0}
    ref, v = D.admissible_at(s, "2020-03", 2)
    ck("T2 a 2-month lag at 2020-03 admits 2020-01, not 2020-03",
       (ref, v) == ("2020-01", 1.0), "%s=%s" % (ref, v))
    ref, v = D.admissible_at(s, "2020-01", 2)
    ck("T2 nothing is admissible before the lag has elapsed", ref is None)
    ref, _ = D.admissible_at(s, "2099-01", 2)
    ck("T2 a far-future t still returns the latest PAST month",
       ref == "2020-03")
    ck("T2 no future reference month is ever returned",
       all(D.m_key(D.admissible_at(s, t, 2)[0] or "1900-01") <= D.m_key(t) - 2
           for t in ("2020-03", "2020-04", "2020-05")))

    ck("T3 staleness: a gap inside the tolerance is fresh",
       not D.is_stale("2020-01", "2020-04", 2, staleness=3))
    ck("T3 staleness: a gap beyond lag+tolerance is stale",
       D.is_stale("2020-01", "2020-07", 2, staleness=3))
    ck("T3 a missing reference month is stale", D.is_stale(None, "2020-01", 2))
    flush("1. time, causal availability and staleness")


# --------------------------------------------------------------------------- #
# 2. real-FX algebra
# --------------------------------------------------------------------------- #
def test_real_fx():
    ck("T4 direct quotes are used as-is",
       D.s_foreign_per_usd(150.0, False) == 150.0)
    ck("T4 USD-per-foreign quotes are inverted",
       abs(D.s_foreign_per_usd(1.25, True) - 0.8) < 1e-12)
    ck("T4 a non-positive quote yields None",
       D.s_foreign_per_usd(0.0, False) is None)

    r = D.r_bilateral(100.0, 110.0, 100.0)
    ck("T5 r_f = log S + log P_US - log P_f",
       abs(r - (math.log(100.0) + math.log(110.0) - math.log(100.0))) < 1e-12)
    r2 = D.r_bilateral(120.0, 110.0, 100.0)
    ck("T5 a nominally stronger USD RAISES r (USD richer)", r2 > r)
    ck("T5 x_UUP negates it, so higher = USD cheaper", D.x_uup(r2) < D.x_uup(r))
    ck("T5 x_FXY takes +r_JPY, so a rich USD = cheap JPY",
       D.x_fxy(r2) > D.x_fxy(r))

    legs = {c: 1.0 for c in C.FX_WEIGHTS}
    ck("T6 a unit basket aggregates to the weight sum, i.e. 1.0",
       abs(D.r_basket(legs) - 1.0) < 1e-12)
    legs2 = dict(legs); legs2["EUR"] = 2.0
    ck("T6 EUR carries 0.576 of the basket",
       abs(D.r_basket(legs2) - (1.0 + 0.576)) < 1e-12)
    legs3 = dict(legs); legs3["JPY"] = None
    ck("T6 a missing leg voids the basket — no partial object",
       D.r_basket(legs3) is None)
    ck("T6 weights sum to one", abs(sum(C.FX_WEIGHTS.values()) - 1.0) < 1e-12)

    # CPI rebasing invariance: scaling a price level by a constant shifts r by a
    # constant, which an expanding z-score removes exactly.
    base = [D.r_bilateral(100.0, p, 100.0) for p in (100.0, 101.0, 102.0, 103.0)]
    rebased = [D.r_bilateral(100.0, p * 2.5, 100.0)
               for p in (100.0, 101.0, 102.0, 103.0)]
    diffs = [b - a for a, b in zip(base, rebased)]
    ck("T7 rebasing a CPI shifts log-r by a CONSTANT",
       max(diffs) - min(diffs) < 1e-12, "shift=%.6f" % diffs[0])
    months = ["%04d-%02d" % (2000 + i // 12, i % 12 + 1) for i in range(140)]
    a = S.expanding_z(list(zip(months, [100.0 + i * 0.1 for i in range(140)])))
    b = S.expanding_z(list(zip(months, [(100.0 + i * 0.1) + 7.0
                                        for i in range(140)])))
    za = [z for _m, z in a if z is not None]
    zb = [z for _m, z in b if z is not None]
    ck("T7 an additive shift leaves every z unchanged",
       len(za) == len(zb) and max(abs(x - y) for x, y in zip(za, zb)) < 1e-9)
    flush("2. real-FX algebra, orientation and rebasing invariance")


# --------------------------------------------------------------------------- #
# 3. signal engine
# --------------------------------------------------------------------------- #
def test_signal():
    months = ["%04d-%02d" % (2000 + i // 12, i % 12 + 1) for i in range(150)]
    vals = [float(i) for i in range(150)]
    z = S.expanding_z(list(zip(months, vals)))
    ck("T8 nothing is emitted before the 120-month warm-up",
       all(v is None for _m, v in z[:119]), "first 119 are None")
    ck("T8 the first z appears exactly at observation 120",
       z[119][1] is not None and z[118][1] is None)

    # a causal z must not change when the FUTURE is altered
    vals_future = list(vals)
    vals_future[140:] = [999.0] * 10
    z2 = S.expanding_z(list(zip(months, vals_future)))
    ck("T9 changing months 141+ leaves month 130's z untouched",
       abs(z[129][1] - z2[129][1]) < 1e-12, "causal")

    flat = S.expanding_z(list(zip(months, [5.0] * 150)))
    ck("T10 zero dispersion yields no z", all(v is None for _m, v in flat))
    ck("T10 and therefore a zero signal",
       all(s == 0 for _m, s in S.sign_signal(flat)))

    sig = S.sign_signal([("2020-01", 1.5), ("2020-02", -0.2),
                         ("2020-03", 0.0), ("2020-04", None)])
    ck("T11 sign-only: +/-/0, and sign(0) = 0",
       [s for _m, s in sig] == [1, -1, 0, 0])
    flush("3. expanding normalisation and the sign-only primary")


# --------------------------------------------------------------------------- #
# 4. episodes and the deletion operator
# --------------------------------------------------------------------------- #
def test_episodes():
    sig = [("2020-%02d" % m, s) for m, s in
           zip(range(1, 13), [1, 1, 1, -1, -1, 0, 0, 0, 0, 1, 1, 1])]
    eps = S.episodes_for("SPY", sig)
    ck("T12 maximal runs of constant sign",
       [len(e) for e in eps] == [3, 2, 4, 3], str([len(e) for e in eps]))
    ck("T12 boundaries are the run endpoints",
       eps[0].start == "2020-01" and eps[0].end == "2020-03")

    # ties: same length -> earlier start wins; same start -> instrument order
    a = S.Episode("TLT", ["2020-01", "2020-02"], 1)
    b = S.Episode("SPY", ["2020-03", "2020-04"], 1)
    c = S.Episode("SPY", ["2020-01", "2020-02"], -1)
    ranked = S.rank_episodes([a, b, c])
    ck("T13 equal length, earlier start ranks first",
       ranked[0].start == "2020-01")
    ck("T13 equal length and start, fixed instrument order decides",
       ranked[0].instrument == "SPY" and ranked[1].instrument == "TLT",
       "%s then %s" % (ranked[0].instrument, ranked[1].instrument))
    ck("T13 the ordering is total, so ranking is reproducible",
       [repr(e) for e in S.rank_episodes([c, a, b])] ==
       [repr(e) for e in ranked])

    big = S.Episode("LQD", ["2021-%02d" % m for m in range(1, 8)], 1)
    ck("T14 longer episodes outrank shorter ones",
       S.rank_episodes([a, big])[0] is big)
    sel = S.select_episodes({"SPY": sig}, k=3)
    ck("T14 exactly k episodes are selected", len(sel) == 3)

    months = ["2020-%02d" % m for m in range(1, 13)]
    remaining = S.delete_months(months, eps[0])
    ck("T15 the operator deletes the episode's CALENDAR MONTHS",
       remaining == ["2020-%02d" % m for m in range(4, 13)],
       "%d of %d remain" % (len(remaining), len(months)))
    ck("T15 deletion removes those months for EVERY instrument, not one",
       set(eps[0].months).isdisjoint(remaining))
    flush("4. valuation episodes, ties and the deletion operator")


# --------------------------------------------------------------------------- #
# 5. verdict boundaries
# --------------------------------------------------------------------------- #
def test_verdicts():
    ck("T16 standalone SUPPORTED above +E",
       I.standalone_verdict(0.20, 0.60) == C.SUPPORTED_POSITIVE_EDGE)
    ck("T16 standalone ADVERSE below -F",
       I.standalone_verdict(-0.70, -0.20) == C.MATERIALLY_ADVERSE)
    ck("T16 standalone UNRESOLVED when the interval spans",
       I.standalone_verdict(-0.30, 0.30) == C.UNRESOLVED_EDGE)
    ck("T17 L == +E exactly is UNRESOLVED, not SUPPORTED",
       I.standalone_verdict(0.15, 0.90) == C.UNRESOLVED_EDGE)
    ck("T17 U == -F exactly is UNRESOLVED, not ADVERSE",
       I.standalone_verdict(-0.90, -0.15) == C.UNRESOLVED_EDGE)
    ck("T17 a wholly positive interval below +E is still UNRESOLVED",
       I.standalone_verdict(0.01, 0.14) == C.UNRESOLVED_EDGE)

    ck("T18 FULL SUPPORTED above +delta",
       I.combo_verdict(0.15, 0.40) == C.SUPPORTED_INCREMENTAL_BENEFIT)
    ck("T18 FULL ADVERSE wholly below zero",
       I.combo_verdict(-0.40, -0.05) == C.INCREMENTAL_BENEFIT_ADVERSE)
    ck("T18 FULL NOT_ESTABLISHED otherwise",
       I.combo_verdict(-0.05, 0.20) == C.INCREMENTAL_BENEFIT_NOT_ESTABLISHED)
    ck("T19 L == +delta exactly is NOT_ESTABLISHED",
       I.combo_verdict(0.10, 0.50) == C.INCREMENTAL_BENEFIT_NOT_ESTABLISHED)
    ck("T19 U == 0 exactly is NOT_ESTABLISHED, not ADVERSE",
       I.combo_verdict(-0.50, 0.0) == C.INCREMENTAL_BENEFIT_NOT_ESTABLISHED)
    ck("T19 a positive interval below +delta is NOT_ESTABLISHED, not ADVERSE",
       I.combo_verdict(0.01, 0.08) == C.INCREMENTAL_BENEFIT_NOT_ESTABLISHED)
    ck("T20 ADVERSE and NOT_ESTABLISHED are never the same token",
       I.combo_verdict(-0.4, -0.05) != I.combo_verdict(-0.05, 0.2))
    flush("5. verdict engines and every boundary touch")


# --------------------------------------------------------------------------- #
# 6. candidacy and C3
# --------------------------------------------------------------------------- #
def test_candidacy():
    ok3 = [{"c1": True, "c2": True}] * 3
    ck("T21 C1 fails only on MATERIALLY_ADVERSE",
       I.c1_pass(C.UNRESOLVED_EDGE) and I.c1_pass(C.SUPPORTED_POSITIVE_EDGE)
       and not I.c1_pass(C.MATERIALLY_ADVERSE))
    ck("T22 C2 adjudicates on the CI UPPER bound", I.c2_pass(0.25))
    ck("T22 rho_upper == rho_max exactly PASSES", I.c2_pass(0.40))
    ck("T22 above rho_max fails", not I.c2_pass(0.4001))
    ck("T22 a missing upper bound fails", not I.c2_pass(None))

    ck("T23 C3 passes when C1 and C2 hold in all three", I.c3_pass(ok3))
    ck("T23 C3 FAILS if C1 fails in any one case",
       not I.c3_pass([{"c1": True, "c2": True}, {"c1": False, "c2": True},
                      {"c1": True, "c2": True}]))
    ck("T23 C3 FAILS if C2 fails in any one case",
       not I.c3_pass([{"c1": True, "c2": True}, {"c1": True, "c2": False},
                      {"c1": True, "c2": True}]))
    ck("T24 an INVALID reduced sample is a FAIL, never a default pass",
       not I.c3_pass([{"c1": True, "c2": True}, {"invalid": True},
                      {"c1": True, "c2": True}]))
    ck("T24 fewer than k cases is a FAIL",
       not I.c3_pass([{"c1": True, "c2": True}] * 2))
    ck("T25 sign stability has NO role: C3 is a function of C1 and C2 only",
       I.c3_pass([{"c1": True, "c2": True, "sign_changed": True}] * 3))

    r = I.candidacy(C.UNRESOLVED_EDGE, 0.25, ok3)
    ck("T26 an UNRESOLVED standalone edge can still be a candidate",
       r["candidate"] and r["c1"] and r["c2"] and r["c3"])
    r = I.candidacy(C.MATERIALLY_ADVERSE, 0.25, ok3)
    ck("T26 MATERIALLY_ADVERSE can never be a candidate", not r["candidate"])
    r = I.candidacy(C.UNRESOLVED_EDGE, 0.9, ok3)
    ck("T26 excess dependence blocks candidacy via C2 alone",
       not r["candidate"] and r["c1"] and not r["c2"])

    # run_c3 drives the real deletion operator over synthetic episodes
    months = ["2020-%02d" % m for m in range(1, 13)]
    eps = [S.Episode("SPY", months[0:3], 1), S.Episode("TLT", months[4:6], -1),
           S.Episode("LQD", months[8:10], 1)]
    seen = []

    def recompute(remaining):
        seen.append(len(remaining))
        return {"c1": True, "c2": True}
    cases = I.run_c3(months, eps, recompute)
    ck("T27 run_c3 applies the operator once per episode", len(cases) == 3)
    ck("T27 each case really shrank the sample", seen == [9, 10, 10], str(seen))
    ck("T27 all-pass cases give C3 PASS", I.c3_pass(cases))

    def recompute_invalid(remaining):
        raise I.InferenceInvalid("floor not met")
    cases = I.run_c3(months, eps, recompute_invalid)
    ck("T28 an InferenceInvalid case is recorded invalid and C3 FAILS",
       all(c["invalid"] for c in cases) and not I.c3_pass(cases))
    flush("6. candidacy C1/C2/C3 and the leave-one-episode-out rule")


# --------------------------------------------------------------------------- #
# 7. bootstrap engine
# --------------------------------------------------------------------------- #
def test_bootstrap():
    rng = np.random.default_rng(0)
    idx = I.x01inf.stationary_bootstrap_indices(50, 12, rng)
    ck("T29 the reused X01 engine returns one index per observation",
       len(idx) == 50 and idx.min() >= 0 and idx.max() < 50)

    ck("T30 seeds are the sealed SeedSequence(7) spawn, one per arm",
       I.seed_for("standalone").entropy == 7
       and I.seed_for("standalone").spawn_key != I.seed_for("combo").spawn_key)
    ck("T30 an unknown arm is refused rather than silently seeded",
       _raises(lambda: I.seed_for("whatever"), ValueError))

    n = 160
    months = ["%04d-%02d" % (2000 + i // 12, i % 12 + 1) for i in range(n)]
    g = np.random.default_rng(11)
    v = g.normal(0.004, 0.03, n)
    t = 0.6 * v + g.normal(0.0, 0.02, n)

    FAST = dict(reps=400, floor=350)      # speed only; T35 exercises the real floor
    a = I.standalone_ci(v, months=months, **FAST)
    b = I.standalone_ci(v, months=months, **FAST)
    ck("T31 the bootstrap is deterministic across runs",
       a["lower"] == b["lower"] and a["upper"] == b["upper"],
       "[%.6f, %.6f]" % (a["lower"], a["upper"]))
    ck("T31 the interval is ordered", a["lower"] <= a["upper"])
    ck("T31 every replicate is accounted for",
       a["counts"]["valid"] + a["counts"]["discarded"]
       == a["counts"]["attempted"])

    c1 = I.correlation_ci(v, t, months=months, **FAST)
    c2 = I.correlation_ci(v, t, months=months, **FAST)
    ck("T32 the correlation CI is deterministic and ordered",
       c1 == c2 and c1["lower"] <= c1["upper"])
    ck("T32 it uses a different arm seed than the standalone statistic",
       (a["lower"], a["upper"]) != (c1["lower"], c1["upper"]))

    # joint resampling: a permuted second leg must change a PAIRED statistic
    perm = t.copy()
    np.random.default_rng(3).shuffle(perm)
    c3 = I.correlation_ci(v, perm, months=months, **FAST)
    ck("T33 permuting one leg changes the paired interval, so the pairing is real",
       (c1["lower"], c1["upper"]) != (c3["lower"], c3["upper"]))

    ck("T34 a degenerate series cannot reach the valid floor",
       _raises(lambda: I.standalone_ci(np.zeros(n), months=months, reps=200,
                                       floor=150), I.InferenceInvalid))
    ck("T34 too few distinct months is refused",
       _raises(lambda: I.standalone_ci(v[:10], months=months[:10], reps=200,
                                       floor=150), I.InferenceInvalid))
    ck("T35 the sealed floor is enforced, not advisory",
       _raises(lambda: I.standalone_ci(v, months=months, reps=100,
                                       floor=C.VALID_REPLICATE_FLOOR),
               I.InferenceInvalid))
    # Structural, via the AST: the property that matters is that every resample
    # goes through the stationary generator. Grepping for the string "iid" would
    # also match the prose FORBIDDING it, which is why this is a call-graph check.
    import ast
    src = open(os.path.join(HERE, "value_inference.py"), encoding="utf-8").read()
    tree = ast.parse(src)
    resamplers, index_calls = set(), 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr == "stationary_bootstrap_indices":
                index_calls += 1
                resamplers.add("stationary")
            # any direct RNG draw of an index vector would be an IID resample
            if (node.func.attr in ("choice", "integers", "randint")
                    and isinstance(node.func.value, ast.Name)
                    and node.func.value.id == "rng"):
                resamplers.add("iid:%s" % node.func.attr)
    ck("T35 the ONLY resampler is the stationary bootstrap",
       resamplers == {"stationary"} and index_calls >= 1,
       "resamplers=%s calls=%d" % (sorted(resamplers), index_calls))
    ck("T35 it is the SEALED X01 engine, not a local reimplementation",
       I.x01inf.stationary_bootstrap_indices.__module__ == "x01_inference")
    ck("T35 NON-VACUITY: the AST check can see an rng index draw",
       "iid:integers" in _detect_resamplers(
           "import numpy as np\n"
           "def f(n, rng):\n    return rng.integers(0, n, n)\n"))
    flush("7. bootstrap determinism, pairing and invalid-replicate accounting")


def _detect_resamplers(src):
    """The same AST rule applied to a probe source, so T35 is not vacuous."""
    import ast
    found = set()
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr == "stationary_bootstrap_indices":
                found.add("stationary")
            if (node.func.attr in ("choice", "integers", "randint")
                    and isinstance(node.func.value, ast.Name)
                    and node.func.value.id == "rng"):
                found.add("iid:%s" % node.func.attr)
    return found


# --------------------------------------------------------------------------- #
# 8. portfolio construction
# --------------------------------------------------------------------------- #
def test_portfolio():
    sig = {"SPY": 1, "TLT": -1, "LQD": 0, "UUP": 1, "FXY": -1}
    vols = {"SPY": 0.10, "TLT": 0.20, "LQD": 0.05, "UUP": 0.10, "FXY": None}
    w = P.asset_weights(sig, vols)
    ck("T36 weight = sign * target_vol / vol",
       abs(w["SPY"] - 1.0) < 1e-12 and abs(w["TLT"] + 0.5) < 1e-12)
    ck("T36 a zero signal gives a zero weight", w["LQD"] == 0.0)
    ck("T36 a missing volatility gives a zero weight", w["FXY"] == 0.0)
    ck("T37 weights are capped at the inherited max",
       abs(P.asset_weights({"SPY": 1}, {"SPY": 0.001})["SPY"])
       <= P.MAX_ASSET_WEIGHT + 1e-12)

    agg = P.equal_risk_aggregate(w)
    ck("T38 equal risk weight divides by the universe size",
       abs(agg["SPY"] - 1.0 / len(C.UNIVERSE)) < 1e-12)
    ck("T38 a stale instrument's risk is NOT redistributed",
       agg["LQD"] == 0.0 and abs(agg["SPY"] - 0.2) < 1e-12)

    capped, scale = P.apply_gross_cap({"a": 2.0, "b": 2.0})
    ck("T39 the gross cap scales weights down proportionally",
       abs(sum(abs(v) for v in capped.values()) - P.MAX_GROSS_LEVERAGE) < 1e-12
       and abs(scale - 0.75) < 1e-12)
    nochange, scale1 = P.apply_gross_cap({"a": 0.5})
    ck("T39 a portfolio inside the cap is untouched", scale1 == 1.0)

    ck("T40 turnover is the sum of absolute weight changes",
       abs(P.turnover({"a": 0.0, "b": 1.0}, {"a": 0.5, "b": 0.0}) - 1.5) < 1e-12)
    ck("T40 a sign flip is charged as a real trade, not zero",
       P.turnover({"a": 1.0}, {"a": -1.0}) == 2.0)
    ck("T40 unwinding to zero on staleness is charged",
       P.cost_for({"a": 1.0}, {"a": 0.0}) > 0)
    ck("T40 the cost rate is the inherited 2.0 bps per unit turnover",
       abs(P.cost_for({"a": 0.0}, {"a": 1.0}) - 2.0 / 10000.0) < 1e-15)

    t = np.array([0.01, 0.02, -0.01])
    v = np.array([0.00, 0.01, 0.02])
    comb = P.combine(t, v)
    ck("T41 the combination is the frozen 75/25 split",
       np.allclose(comb, 0.75 * t + 0.25 * v))
    ck("T41 a split that does not sum to one is refused",
       _raises(lambda: P.combine(t, v, 0.8, 0.3), ValueError))
    ck("T41 unaligned series are refused",
       _raises(lambda: P.combine(t, v[:2]), ValueError))

    cfg = P.inherited_config()
    ck("T42 sizing knobs are inherited from config.py, not redefined",
       cfg["target_vol"] == P.TARGET_VOL_ANNUAL
       and cfg["max_asset_weight"] == P.MAX_ASSET_WEIGHT
       and cfg["max_gross"] == P.MAX_GROSS_LEVERAGE, str(cfg))
    flush("8. sizing, caps, aggregation, costs and the frozen combination")


# --------------------------------------------------------------------------- #
# 9. object construction on synthetic inputs
# --------------------------------------------------------------------------- #
def test_objects_synthetic():
    months = ["%04d-%02d" % (2000 + i // 12, i % 12 + 1) for i in range(140)]
    hist = ["%04d-%02d" % (1990 + i // 12, i % 12 + 1) for i in range(260)]
    cape = {m: 20.0 + (i % 7) for i, m in enumerate(hist)}
    tlt = {m: 1.0 + 0.01 * (i % 11) for i, m in enumerate(hist)}
    credit = {m: 2.0 + 0.02 * (i % 5) for i, m in enumerate(hist)}
    fx = {c: {m: 1.0 + 0.001 * i for i, m in enumerate(hist)} for c in C.FX_WEIGHTS}
    cpi = {c: {m: 100.0 + 0.1 * i for i, m in enumerate(hist)}
           for c in ("US",) + tuple(C.FX_WEIGHTS)}

    objs = D.build_objects(months, sources={"cape": cape, "tlt": tlt,
                                            "credit": credit, "fx": fx,
                                            "cpi": cpi})
    ck("T43 all five sealed objects are produced",
       sorted(objs) == sorted(C.UNIVERSE), str(sorted(objs)))
    ck("T43 SPY is the real earnings yield, i.e. the CAPE inverse",
       abs(objs["SPY"]["2005-01"]
           - 1.0 / cape[D.m_shift("2005-01", -C.LAG_CAPE_MONTHS)]) < 1e-12)
    ck("T43 every month of the window has a value",
       all(objs[i][months[-1]] is not None for i in C.UNIVERSE))

    # a stale CPI must void UUP and FXY rather than silently carry forward
    cpi_short = {c: {m: v for m, v in cpi[c].items() if m <= "2004-01"}
                 for c in cpi}
    objs2 = D.build_objects(months, sources={"cape": cape, "tlt": tlt,
                                             "credit": credit, "fx": fx,
                                             "cpi": cpi_short})
    ck("T44 a CPI stale beyond the tolerance voids UUP",
       objs2["UUP"]["2006-01"] is None)
    ck("T44 and voids FXY", objs2["FXY"]["2006-01"] is None)
    ck("T44 while leaving the non-FX objects intact",
       objs2["SPY"]["2006-01"] is not None
       and objs2["TLT"]["2006-01"] is not None)

    sig = S.build_signals(objs, months)
    ck("T45 signals exist for the full universe",
       sorted(sig) == sorted(C.UNIVERSE))
    ck("T45 every signal is in {-1, 0, +1}",
       all(s in (-1, 0, 1) for inst in sig for _m, s in sig[inst]))
    ck("T45 warm-up suppresses early signals",
       all(s == 0 for _m, s in sig["SPY"][:5]))
    flush("9. object construction and signal assembly on synthetic inputs")


# --------------------------------------------------------------------------- #
# 10. contract conformance and the closed S3 boundary
# --------------------------------------------------------------------------- #
def test_contract_and_safety():
    ok, _checks_ = C.conformance()
    ck("T46 implementation constants match the sealed contract", ok)
    ck("T46 the sealed hash is unchanged",
       C.sealed_sha256() == C.SEALED_PREREG_SHA256)
    ck("T47 HYG is not a Value instrument",
       "HYG" not in C.UNIVERSE and "HYG" in C.EXCLUDED_FROM_VALUE)
    ck("T47 the universe is exactly the sealed five",
       C.UNIVERSE == ("SPY", "TLT", "LQD", "UUP", "FXY"))
    ck("T48 the Shiller limitation is carried in code, not only in prose",
       C.SHILLER_VINTAGE_STATUS.startswith("RECONSTRUCTED_HISTORICAL_SERIES"))
    ck("T48 Shiller is never relabelled PIT_READY",
       "PIT_READY" not in C.SHILLER_VINTAGE_STATUS)

    import value_runner as R
    ck("T49 no Value execution authorization exists",
       R.VALUE_EXECUTION_AUTHORIZED is False)
    code = R.cmd_execute(type("A", (), {"run_id": "SYNTHETIC-NOT-A-RUN"})())
    ck("T49 the S3 entry point REFUSES and returns a non-zero code",
       code == R.EXIT_REFUSED, "exit=%s" % code)
    ck("T50 no evidence artifact exists anywhere in the Value directory",
       not any(f.lower().endswith(".json") and "evidence" in f.lower()
               for f in os.listdir(HERE)))
    ck("T50 the sealed prereg was not modified by the build",
       C.sealed_sha256() == C.SEALED_PREREG_SHA256)
    flush("10. sealed-contract conformance and the closed S3 boundary")


def main():
    global _checks
    failed = 0
    for fn in (test_time_and_availability, test_real_fx, test_signal,
               test_episodes, test_verdicts, test_candidacy, test_bootstrap,
               test_portfolio, test_objects_synthetic, test_contract_and_safety):
        _checks = []
        fn()
        failed += sum(1 for _l, c, _d in _checks if not c)
    print("=" * 96)
    print("VALUE_S2_SYNTHETIC_VALIDATION = %s   (%d failed)"
          % ("PASS" if failed == 0 else "FAIL", failed))
    print("VALUE_TARGET_RETURNS_COMPUTED = NO   (synthetic fixtures only)")
    print("TARGET_BACKTEST_RUN = NO")
    print("=" * 96)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
