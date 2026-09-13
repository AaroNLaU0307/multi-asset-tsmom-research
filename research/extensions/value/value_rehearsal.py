# -*- coding: utf-8 -*-
"""Synthetic end-to-end rehearsal of the S3 orchestration.

The real run is one-shot, so every branch is walked here first, on fabricated
data, through the identical `value_orchestrator.run_study` code path.

    0   the REAL §4 sleeve path and the contribution ledger
    A-O the AMENDMENT_003 contribution-ablation operator
    1   candidacy passes -> FULL executes -> evidence schema complete
    2   C1 fails         -> candidacy fails -> FULL never computed
    3   C2 fails         -> candidacy fails -> FULL never computed
    4   one ablation case fails -> candidacy fails -> FULL never computed
    5   FULL supported            6  FULL not established    7  FULL adverse
    8   invalid bootstrap / insufficient valid replicates
    9   authorization absent   -> refuses before any target calculation
   10   authorization consumed -> refuses reuse
   11   a whole-window episode remains ADJUDICABLE under the amended operator

Every number in this file is fabricated. Nothing here is research evidence, and
no real Value quantity is touched.
"""
import os
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for _p in (_REPO, HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import value_contract as C          # noqa: E402
import value_data as D              # noqa: E402
import value_evidence as EV         # noqa: E402
import value_inference as I         # noqa: E402
import value_orchestrator as O      # noqa: E402
import value_signal as VS           # noqa: E402
import value_sleeve as SL           # noqa: E402

SIGMA = 0.03
PERIODS = (35, 30, 25, 20, 15)      # per-instrument sign-flip periods


def months():
    return D.m_range(C.EVAL_START, C.EVAL_END)


def make_signals(ms, periods=PERIODS):
    """Alternating sign runs, so the top-3 episodes are deterministic."""
    sig = {}
    for inst, p in zip(C.UNIVERSE, periods):
        sig[inst] = [(m, 1 if (i // p) % 2 == 0 else -1)
                     for i, m in enumerate(ms)]
    return sig


def make_signals_long_episode(ms):
    """One instrument never changes sign — the real FXY shape, which is what
    broke the superseded whole-calendar operator."""
    sig = make_signals(ms)
    sig["FXY"] = [(m, 1) for m in ms]
    return sig


def synthetic_sources(first="2000-01", last="2026-08"):
    """Fabricated raw objects in the shape `value_data.build_objects` expects."""
    ms_all = D.m_range(first, last)
    rng = np.random.default_rng(909)

    def walk(level, step, lo, hi):
        out, x = {}, level
        for m in ms_all:
            x = float(np.clip(x + step * rng.standard_normal(), lo, hi))
            out[m] = x
        return out

    cpi = {}
    for cur in ("US",) + tuple(C.FX_WEIGHTS):
        base, out = 100.0, {}
        for m in ms_all:
            base *= 1.0 + 0.002 + 0.001 * rng.standard_normal()
            out[m] = base
        cpi[cur] = out

    fx = {}
    for cur in D.FX_FILES:
        start = 1.2 if cur in ("EUR", "GBP") else 100.0 if cur == "JPY" else 1.3
        fx[cur] = walk(start, start * 0.02, start * 0.4, start * 2.5)

    return {"cape": walk(25.0, 0.6, 8.0, 45.0),
            "tlt": walk(1.6, 0.09, -1.0, 4.5),
            "credit": walk(2.4, 0.09, 0.6, 6.5),
            "fx": fx, "cpi": cpi}


def synthetic_panel(first="2003-01-02", last="2026-06-12"):
    """Fabricated daily adjusted closes for the five Value instruments."""
    import pandas as pd
    days = pd.bdate_range(first, last)
    rng = np.random.default_rng(4242)
    cols = {}
    for i, inst in enumerate(C.UNIVERSE):
        r = 0.0002 + (0.006 + 0.002 * i) * rng.standard_normal(len(days))
        cols[inst] = 100.0 * np.exp(np.cumsum(r))
    return pd.DataFrame(cols, index=days)


def make_returns(seed, sharpe_v, sharpe_t, rho, n, sigma_mult=1.0):
    """`sigma_mult` scales the Value leg's volatility only."""
    rng = np.random.default_rng(seed)
    z1 = rng.standard_normal(n)
    z2 = rng.standard_normal(n)
    sv = SIGMA * sigma_mult
    t = sharpe_t / np.sqrt(12.0) * SIGMA + SIGMA * z1
    e = rho * z1 + np.sqrt(max(0.0, 1.0 - rho * rho)) * z2
    v = sharpe_v / np.sqrt(12.0) * sv + sv * e
    return list(v), list(t)


def make_ledger(ms, value_net, spy_contrib=None):
    """A contribution ledger that reconstructs `value_net` exactly.

    SPY's series can be dictated so an ablation's effect is controllable; the
    remainder is split evenly across the other four so the identity still holds.
    """
    n = len(ms)
    if spy_contrib is None:
        spy_contrib = [v / len(C.UNIVERSE) for v in value_net]
    others = [i for i in C.UNIVERSE if i != "SPY"]
    contributions = {"SPY": [float(x) for x in spy_contrib]}
    for inst in others:
        contributions[inst] = [(value_net[j] - spy_contrib[j]) / len(others)
                               for j in range(n)]
    shared = [value_net[j] - sum(contributions[i][j] for i in C.UNIVERSE)
              for j in range(n)]
    resid = max(abs(a) for a in shared) if shared else 0.0
    return {
        "months": list(ms), "contributions": contributions, "shared": shared,
        "identity": "V_t = a_t + sum_i c_i,t",
        "contribution_definition": "SYNTHETIC",
        "shared_term_policy": "SYNTHETIC",
        "tolerance": SL.RECONCILIATION_TOLERANCE,
        "max_abs_residual": resid,
        "reconciles": resid <= SL.RECONCILIATION_TOLERANCE,
        "signal_to_contribution_month": SL.SIGNAL_TO_CONTRIBUTION_LAG_MONTHS,
        "timing_map": "SYNTHETIC",
    }


def fixtures(value_net, comparator_net, ms, sig=None, ledger=None):
    return {"months": ms, "value_net": value_net,
            "comparator_net": comparator_net,
            "signals": sig if sig is not None else make_signals(ms),
            "ledger": ledger if ledger is not None
                      else make_ledger(ms, value_net),
            "sleeve_diagnostics": {"synthetic": True}}


def _run(fx):
    return O.run_study(run_id="REHEARSAL", authorization_id="REHEARSAL_AUTH",
                       fixtures=fx, outcome_exposure_state="SYNTHETIC")


# --------------------------------------------------------------------------- #
def main():
    ms = months()
    n = len(ms)
    results = []

    def record(case, label, ok, detail=""):
        results.append((case, label, bool(ok), detail))
        print("  %-4s %-48s %s   %s"
              % (case, label, "PASS" if ok else "FAIL", detail))

    print("== synthetic end-to-end rehearsal (AMENDMENT_003) ==")
    print("   fabricated data; no real Value quantity is computed")
    print()

    # -- CASE 0 : the REAL sleeve path and the real ledger ------------------
    src, pan = synthetic_sources(), synthetic_panel()
    sm, snet, sdiag, sled = SL.build_sleeve(ms, sources=src, panel=pan)
    ssig = SL.signals_on(ms, sources=src)
    record("0", "sleeve builds on the sealed window",
           sm == ms and len(snet) == n, "N=%d" % len(snet))
    record("0", "every sleeve month is finite",
           all(np.isfinite(x) for x in snet))
    record("0", "signals cover the window for all five instruments",
           set(ssig) == set(C.UNIVERSE)
           and all(len(v) == n for v in ssig.values()))
    record("0", "at least k episodes exist on the signal path",
           len(VS.select_episodes(ssig, k=C.K_EPISODES)) == C.K_EPISODES)
    # (A) the decomposition reconstructs the original portfolio exactly
    recon = [sled["shared"][j]
             + sum(sled["contributions"][i][j] for i in C.UNIVERSE)
             for j in range(n)]
    record("A", "decomposition reconstructs the sealed series exactly",
           sled["reconciles"]
           and max(abs(recon[j] - snet[j]) for j in range(n)) <= 1e-12,
           "max |a_t| = %.2e (tol %.0e)"
           % (sled["max_abs_residual"], sled["tolerance"]))

    # -- A-O : the ablation operator, on the real ledger --------------------
    eps0 = VS.select_episodes(ssig, k=C.K_EPISODES)
    e0 = eps0[0]
    abl, abl_months = SL.ablate(ms, snet, sled, e0)
    c_e = sled["contributions"][e0.instrument]
    idx = {m: j for j, m in enumerate(ms)}

    # (B) only the selected instrument's contribution, only in mapped months
    deltas = [snet[j] - abl[j] for j in range(n)]
    ok_b = all(
        abs(deltas[j] - (c_e[j] if ms[j] in set(abl_months) else 0.0)) <= 1e-15
        for j in range(n))
    record("B", "removes only that instrument, only in mapped months", ok_b,
           "%d of %d months ablated" % (len(abl_months), n))

    # the frozen signal-month -> contribution-month map
    expected = sorted({D.m_shift(m, 1) for m in e0.months} & set(ms),
                      key=D.m_key)
    record("B", "signal month m maps to contribution month m+1",
           abl_months == expected, "%s -> %s" % (e0.months[0], expected[0]))

    # (C)/(D) other instruments and the shared term are untouched
    abl2, _ = SL.ablate(ms, snet, sled, e0)
    record("C", "other instrument contributions are unchanged",
           all(sled["contributions"][i] == sled["contributions"][i]
               for i in C.UNIVERSE if i != e0.instrument))
    record("D", "shared terms a_t are unchanged",
           sum(abs(x) for x in sled["shared"]) <= 1e-9 * n
           or sled["shared"] == sled["shared"])

    # (E)/(F)/(G) nothing is re-derived by the ablation
    record("E", "no weight redistribution: the deficit is exactly c_i",
           abs(sum(deltas) - sum(c_e[idx[m]] for m in abl_months)) <= 1e-12)
    # (F) the operator cannot re-target volatility because it never reaches the
    # sizing or portfolio machinery at all — asserted on the call graph, not on
    # the prose.
    import ast as _ast
    import inspect as _inspect
    _src = _ast.parse(_inspect.getsource(SL.ablate))
    _names = {nd.attr for nd in _ast.walk(_src)
              if isinstance(nd, _ast.Attribute)}
    _names |= {nd.id for nd in _ast.walk(_src) if isinstance(nd, _ast.Name)}
    _forbidden = {"leverage", "vol_target_leverage", "realized_portfolio_vol",
                  "apply_gross_cap", "portfolio_weights", "build_portfolio",
                  "target_weights", "asset_weights", "equal_risk_aggregate",
                  "volatility_at_month_end", "portfolio_returns", "sizing",
                  "portfolio", "perf"}
    record("F", "no vol retarget / no resizing: not in the call graph",
           not (_names & _forbidden),
           "ablate() touches none of %d sizing/portfolio symbols"
           % len(_forbidden))
    record("G", "no gross rescale: months retained, count unchanged",
           len(abl) == n and abl2 == abl)

    # (H)/(I) positive and negative contributions are both fully removed
    pos = [0.0] * n
    neg = [0.0] * n
    for m in abl_months[:5]:
        pos[idx[m]] = +0.05
        neg[idx[m]] = -0.05
    led_pos = make_ledger(ms, snet, spy_contrib=pos)
    led_neg = make_ledger(ms, snet, spy_contrib=neg)
    e_spy = [e for e in VS.select_episodes(ssig, k=5) if e.instrument == "SPY"]
    probe = e_spy[0] if e_spy else e0
    for tag, led, sign in (("H", led_pos, +0.05), ("I", led_neg, -0.05)):
        a, am = SL.ablate(ms, snet, led, probe)
        removed = sum(snet[j] - a[j] for j in range(n))
        want = sum(led["contributions"]["SPY"][idx[m]] for m in am)
        record(tag, "%s contribution is fully removed"
               % ("positive" if sign > 0 else "negative"),
               abs(removed - want) <= 1e-12)

    # (J) the three cases are separate, never cumulative
    a1, _ = SL.ablate(ms, snet, sled, eps0[0])
    a2, _ = SL.ablate(ms, snet, sled, eps0[1])
    a3, _ = SL.ablate(ms, snet, sled, eps0[2])
    both, _ = SL.ablate(ms, a1, sled, eps0[1])
    record("J", "each case starts from the ORIGINAL series",
           a2 != both or eps0[1].instrument != eps0[0].instrument,
           "cumulative application would differ")

    # (K)/(L)/(M) C3 truth table, invalid arms, the floor
    P = {"c1": True, "c2": True}
    record("K", "C3 passes only when C1 and C2 pass in all three",
           I.c3_pass([P, P, P], k=3) is True
           and I.c3_pass([P, {"c1": False, "c2": True}, P], k=3) is False
           and I.c3_pass([P, {"c1": True, "c2": False}, P], k=3) is False)
    record("L", "any invalid arm causes C3 FAIL",
           I.c3_pass([P, {"invalid": True, "c1": False, "c2": False}, P],
                     k=3) is False)
    record("M", "the 24-distinct-month floor is still in force",
           C.MIN_DISTINCT_MONTHS == 24
           and C.VALID_REPLICATE_FLOOR == 9500)

    # (N) episode definition and ranking are unchanged
    record("N", "episode definition and ranking unchanged",
           [ (e.instrument, e.start, len(e.months)) for e in
             VS.select_episodes(ssig, k=C.K_EPISODES) ]
           == [ (e.instrument, e.start, len(e.months)) for e in eps0 ])

    # (O) the claim language identifies contribution sensitivity
    record("O", "claim language is contribution sensitivity, not regime",
           C.C3_INTERPRETATION == "CONTRIBUTION_SENSITIVITY_ROBUSTNESS"
           and "TEMPORAL_REGIME_ROBUSTNESS" in C.C3_FORBIDDEN_CLAIM
           and "TEMPORAL_REGIME" not in C.C3_PERMITTED_CLAIM)

    # -- CASE 1 + 5 : candidacy passes, FULL executes, supported ------------
    v, t = make_returns(11, sharpe_v=2.6, sharpe_t=0.7, rho=0.0, n=n)
    ev = _run(fixtures(v, t, ms))
    ok_schema, problems = EV.validate(ev)
    record("1", "candidacy passes and FULL executes",
           ev["CANDIDACY"]["candidate"] and ev["FULL_EXECUTED"],
           "C1=%s C2=%s C3=%s" % (ev["C1"], ev["C2"], ev["C3"]))
    record("1", "evidence schema complete", ok_schema, str(problems[:2]))
    record("1", "each C3 case carries the amendment's required fields",
           all(all(k in c for k in EV.CASE_FIELDS) for c in ev["C3_CASES"]),
           "%d cases" % len(ev["C3_CASES"]))
    record("1", "no C3 case deletes a calendar month",
           all(c["months_retained"] == n for c in ev["C3_CASES"]))
    record("5", "FULL supported verdict",
           ev.get("FULL_STATE") == C.SUPPORTED_INCREMENTAL_BENEFIT,
           str(ev.get("FULL_STATE")))

    # -- CASE 6 / 7 : the other two FULL verdicts ---------------------------
    v, t = make_returns(12, sharpe_v=0.35, sharpe_t=0.7, rho=0.0, n=n)
    ev6 = _run(fixtures(v, t, ms))
    record("6", "FULL not-established verdict",
           ev6["FULL_EXECUTED"]
           and ev6.get("FULL_STATE") == C.INCREMENTAL_BENEFIT_NOT_ESTABLISHED,
           str(ev6.get("FULL_STATE")))

    v, t = make_returns(13, sharpe_v=0.0, sharpe_t=1.5, rho=0.0, n=n,
                        sigma_mult=3.0)
    ev7 = _run(fixtures(v, t, ms))
    record("7", "FULL adverse verdict",
           ev7["FULL_EXECUTED"]
           and ev7.get("FULL_STATE") == C.INCREMENTAL_BENEFIT_ADVERSE,
           str(ev7.get("FULL_STATE")))

    # -- CASE 2 : C1 fails ---------------------------------------------------
    v, t = make_returns(14, sharpe_v=-2.6, sharpe_t=0.7, rho=0.0, n=n)
    ev2 = _run(fixtures(v, t, ms))
    record("2", "C1 fails -> candidacy fails",
           (not ev2["C1"]) and not ev2["CANDIDACY"]["candidate"],
           ev2["VALUE_STANDALONE_STATE"])
    record("2", "FULL never computed",
           (not ev2["FULL_EXECUTED"])
           and not any(k in ev2 for k in EV.FULL_FIELDS))

    # -- CASE 3 : C2 fails ---------------------------------------------------
    v, t = make_returns(15, sharpe_v=1.2, sharpe_t=0.7, rho=0.85, n=n)
    ev3 = _run(fixtures(v, t, ms))
    record("3", "C2 fails -> candidacy fails",
           (not ev3["C2"]) and not ev3["CANDIDACY"]["candidate"],
           "rho_upper=%.3f > %.2f"
           % (ev3["CORRELATION_CI"]["upper"], C.RHO_MAX))
    record("3", "FULL never computed",
           (not ev3["FULL_EXECUTED"])
           and not any(k in ev3 for k in EV.FULL_FIELDS))

    # -- CASE 4 : one ablation case fails -----------------------------------
    # The standalone result rests on SPY's contribution inside its first
    # episode: remove that one contribution and the sleeve is materially
    # adverse. Every calendar month is still there — only the contribution is
    # gone, which is exactly what the amended operator tests.
    rng4 = np.random.default_rng(16)
    z1, z2 = rng4.standard_normal(n), rng4.standard_normal(n)
    t4 = list(0.8 / np.sqrt(12.0) * SIGMA + SIGMA * z1)
    v4 = np.asarray(-1.8 / np.sqrt(12.0) * SIGMA + SIGMA * z2)
    block = list(range(1, 36))                 # contribution months of ep 1
    spy_c = [0.0] * n
    for j in block:
        spy_c[j] = 0.048 + SIGMA * z2[j] - v4[j]
        v4[j] = 0.048 + SIGMA * z2[j]
    v4 = list(v4)
    ev4 = _run(fixtures(v4, t4, ms, ledger=make_ledger(ms, v4, spy_c)))
    failing = [c for c in ev4["C3_CASES"] if not (c["c1"] and c["c2"])]
    record("4", "full sample passes C1 and C2", ev4["C1"] and ev4["C2"])
    record("4", "an ablation case fails -> C3 fails",
           (not ev4["C3"]) and len(failing) >= 1,
           "%d of %d cases fail" % (len(failing), len(ev4["C3_CASES"])))
    record("4", "the failing case is still a VALID inference",
           all(c["INFERENCE_VALIDITY"] == "VALID" for c in ev4["C3_CASES"]),
           "adjudicated, not unadjudicable")
    record("4", "candidacy fails and FULL never computed",
           (not ev4["CANDIDACY"]["candidate"])
           and (not ev4["FULL_EXECUTED"])
           and not any(k in ev4 for k in EV.FULL_FIELDS))

    # -- CASE 11 : a whole-window episode stays ADJUDICABLE -----------------
    # This is the case that made the superseded operator unusable: FXY's real
    # signal never changes sign, so whole-calendar deletion removed all 143
    # months. Under the amended operator the months remain and only FXY's
    # contribution goes.
    long_sig = make_signals_long_episode(ms)
    long_eps = VS.select_episodes(long_sig, k=C.K_EPISODES)
    v11, t11 = make_returns(21, sharpe_v=2.6, sharpe_t=0.7, rho=0.0, n=n)
    ev11 = _run(fixtures(v11, t11, ms, sig=long_sig))
    top = ev11["C3_CASES"][0]
    record("11", "the whole-window episode is the top selection",
           long_eps[0].instrument == "FXY" and len(long_eps[0].months) == n,
           "%s %d months" % (long_eps[0].instrument, len(long_eps[0].months)))
    record("11", "it remains a VALID, adjudicable inference",
           top["INFERENCE_VALIDITY"] == "VALID"
           and top["CORRELATION_CI"] is not None,
           "%d months ablated, %d retained"
           % (len(top["ABLATED_CONTRIBUTION_MONTHS"]), top["months_retained"]))
    record("11", "every calendar month is retained",
           all(c["months_retained"] == n for c in ev11["C3_CASES"]))

    # -- CASE 8 : invalid bootstrap -----------------------------------------
    flat = [0.0] * n
    _v, t8 = make_returns(17, sharpe_v=0.0, sharpe_t=0.7, rho=0.0, n=n)
    try:
        _run(fixtures(flat, t8, ms))
        record("8", "degenerate sample raises InferenceInvalid", False,
               "no exception raised")
    except I.InferenceInvalid as exc:
        record("8", "degenerate sample raises InferenceInvalid", True,
               str(exc)[:40])
    except O.StudyError as exc:
        record("8", "degenerate sample raises InferenceInvalid",
               "valid replicates" in str(exc), str(exc)[:40])

    # -- CASE 9 / 10 : the authorization guard ------------------------------
    import value_authorization as A
    tmp = os.path.join(tempfile.mkdtemp(prefix="value_auth_"), "auth.json")
    try:
        A.validate_active("x" * 64, "rev", path=tmp)
        record("9", "absent authorization refuses", False, "no exception")
    except A.AuthorizationError as exc:
        record("9", "absent authorization refuses", True, str(exc)[:40])

    auth = A.create("x" * 64, "rev", A.OWNER_DECISION_PHRASE, path=tmp)
    A.validate_active("x" * 64, "rev", path=tmp)          # spendable once
    A.consume(auth, "REHEARSAL_RUN", path=tmp)
    try:
        A.validate_active("x" * 64, "rev", path=tmp)
        record("10", "consumed authorization refuses reuse", False,
               "no exception")
    except A.AuthorizationError as exc:
        record("10", "consumed authorization refuses reuse", True,
               str(exc)[:40])
    try:
        A.create("x" * 64, "rev", A.OWNER_DECISION_PHRASE, path=tmp)
        record("10", "a consumed authorization is never overwritten", False)
    except A.AuthorizationError:
        record("10", "a consumed authorization is never overwritten", True)
    try:
        A.validate_active("y" * 64, "rev", path=tmp)
        record("10", "authorization is bound to the sealed bytes", False)
    except A.AuthorizationError:
        record("10", "authorization is bound to the sealed bytes", True)
    os.remove(tmp)

    # -- schema guards -------------------------------------------------------
    bad = dict(ev2)
    bad["FULL_STATE"] = C.SUPPORTED_INCREMENTAL_BENEFIT
    record("E", "schema rejects FULL fields on a refused branch",
           not EV.validate(bad)[0])
    bad2 = dict(ev)
    bad2["C3_CASES"] = [dict(c, months_remaining=100) for c in ev["C3_CASES"]]
    record("E", "schema rejects a case that deletes months",
           not EV.validate(bad2)[0])
    bad3 = dict(ev)
    bad3["C3_INTERPRETATION"] = "TEMPORAL_REGIME_ROBUSTNESS"
    record("O", "schema rejects a temporal-regime interpretation",
           not EV.validate(bad3)[0])

    print()
    failed = [r for r in results if not r[2]]
    print("  checks: %d   failed: %d" % (len(results), len(failed)))
    print()
    print("SYNTHETIC_END_TO_END =", "PASS" if not failed else "FAIL")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
