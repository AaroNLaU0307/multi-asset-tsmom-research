# -*- coding: utf-8 -*-
"""Synthetic end-to-end rehearsal of the S3 orchestration.

The real run is one-shot, so every branch is walked here first, on fabricated
data, through the identical `value_orchestrator.run_study` code path. Ten cases:

    1  candidacy passes -> FULL executes -> evidence schema complete
    2  C1 fails         -> candidacy fails -> FULL never computed
    3  C2 fails         -> candidacy fails -> FULL never computed
    4  one C3 jackknife fails -> candidacy fails -> FULL never computed
    5  FULL supported
    6  FULL not established
    7  FULL adverse
    8  invalid bootstrap / insufficient valid replicates
    9  authorization absent      -> refuses before any target calculation
   10  authorization consumed    -> refuses reuse

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


def make_returns(seed, sharpe_v, sharpe_t, rho, n, sigma_mult=1.0):
    """`sigma_mult` scales the Value leg's volatility only, which is how a
    zero-Sharpe sleeve can still dilute a good book's Sharpe."""
    rng = np.random.default_rng(seed)
    z1 = rng.standard_normal(n)
    z2 = rng.standard_normal(n)
    sv = SIGMA * sigma_mult
    t = sharpe_t / np.sqrt(12.0) * SIGMA + SIGMA * z1
    e = rho * z1 + np.sqrt(max(0.0, 1.0 - rho * rho)) * z2
    v = sharpe_v / np.sqrt(12.0) * sv + sv * e
    return list(v), list(t)


def synthetic_sources(first="2000-01", last="2026-08"):
    """Fabricated raw objects in the shape `value_data.build_objects` expects.

    Dense monthly coverage so the §3.2 lags and the §4.1 staleness window are
    satisfied, and long enough that the 120-month warm-up has elapsed by the
    sealed evaluation start.
    """
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
    for cur, fname in D.FX_FILES.items():
        start = 1.2 if cur in ("EUR", "GBP") else 100.0 if cur == "JPY" else 1.3
        fx[cur] = walk(start, start * 0.02, start * 0.4, start * 2.5)

    return {
        "cape": walk(25.0, 0.6, 8.0, 45.0),
        "tlt": walk(1.6, 0.09, -1.0, 4.5),
        "credit": walk(2.4, 0.09, 0.6, 6.5),
        "fx": fx,
        "cpi": cpi,
    }


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


def fixtures(value_net, comparator_net, ms, sig=None):
    return {"months": ms, "value_net": value_net,
            "comparator_net": comparator_net,
            "signals": sig if sig is not None else make_signals(ms),
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
        print("  %-4s %-46s %s   %s"
              % (case, label, "PASS" if ok else "FAIL", detail))

    print("== synthetic end-to-end rehearsal ==")
    print("   fabricated data; no real Value quantity is computed")
    print()

    # -- CASE 0 : the REAL sleeve path on fabricated inputs ------------------
    # The fixture cases below inject the sleeve's output, so without this the
    # §4 construction itself would first execute on the one-shot real run.
    # Here it runs for real — objects, signals, sizing, equal-risk aggregation,
    # the portfolio vol target and gross cap, turnover and cost — on data that
    # carries no research meaning.
    import value_sleeve as SL
    src, pan = synthetic_sources(), synthetic_panel()
    sm, snet, sdiag = SL.build_sleeve(ms, sources=src, panel=pan)
    ssig = SL.signals_on(ms, sources=src)
    record("0", "sleeve builds on the sealed window",
           sm == ms and len(snet) == n, "N=%d" % len(snet))
    record("0", "every sleeve month is finite",
           all(np.isfinite(x) for x in snet))
    record("0", "signals cover the window for all five instruments",
           set(ssig) == set(C.UNIVERSE)
           and all(len(v) == n for v in ssig.values()),
           "%d instruments" % len(ssig))
    import value_signal as VS
    seps = VS.select_episodes(ssig, k=C.K_EPISODES)
    record("0", "at least k episodes exist on the signal path",
           len(seps) == C.K_EPISODES,
           "; ".join("%s %s..%s" % (e.instrument, e.start, e.end)
                     for e in seps))
    record("0", "the sleeve records its inherited machinery",
           sdiag.get("portfolio_risk_source") == "src/portfolio.py::leverage"
           and sdiag.get("cost_bps_per_unit_turnover") == 2.0,
           "warm-up from %s" % sdiag.get("object_history_start"))

    # -- CASE 1 + 5 : candidacy passes, FULL executes, supported ------------
    v, t = make_returns(11, sharpe_v=2.6, sharpe_t=0.7, rho=0.0, n=n)
    ev = _run(fixtures(v, t, ms))
    ok_schema, problems = EV.validate(ev)
    record("1", "candidacy passes and FULL executes",
           ev["CANDIDACY"]["candidate"] and ev["FULL_EXECUTED"],
           "C1=%s C2=%s C3=%s" % (ev["C1"], ev["C2"], ev["C3"]))
    record("1", "evidence schema complete", ok_schema, str(problems[:2]))
    record("1", "every C3 case carries both intervals",
           all(c["standalone_ci"] and c["correlation_ci"]
               for c in ev["C3_CASES"] if c["valid"]),
           "%d cases" % len(ev["C3_CASES"]))
    record("5", "FULL supported verdict",
           ev.get("FULL_STATE") == C.SUPPORTED_INCREMENTAL_BENEFIT,
           str(ev.get("FULL_STATE")))

    # -- CASE 6 : FULL not established --------------------------------------
    v, t = make_returns(12, sharpe_v=0.35, sharpe_t=0.7, rho=0.0, n=n)
    ev6 = _run(fixtures(v, t, ms))
    record("6", "FULL not-established verdict",
           ev6["FULL_EXECUTED"]
           and ev6.get("FULL_STATE") == C.INCREMENTAL_BENEFIT_NOT_ESTABLISHED,
           "%s (executed=%s)" % (ev6.get("FULL_STATE"), ev6["FULL_EXECUTED"]))

    # -- CASE 7 : FULL adverse ----------------------------------------------
    # A sleeve need not be adverse on its own to hurt the book: this one has a
    # ~zero Sharpe (so C1 passes) but three times the volatility, and diluting a
    # strong book with it plausibly lowers the combined Sharpe.
    v, t = make_returns(13, sharpe_v=0.0, sharpe_t=1.5, rho=0.0, n=n,
                        sigma_mult=3.0)
    ev7 = _run(fixtures(v, t, ms))
    record("7", "FULL adverse verdict",
           ev7["FULL_EXECUTED"]
           and ev7.get("FULL_STATE") == C.INCREMENTAL_BENEFIT_ADVERSE,
           "%s (executed=%s)" % (ev7.get("FULL_STATE"), ev7["FULL_EXECUTED"]))

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

    # -- CASE 4 : one C3 jackknife fails ------------------------------------
    # The whole standalone result rests on one valuation episode: outside SPY's
    # first 35-month episode the sleeve is badly negative, and the episode's
    # returns are what keep the full sample out of MATERIALLY_ADVERSE. Delete
    # that episode and C1 fails on the reduced sample — exactly the dependence
    # C3 exists to catch.
    rng4 = np.random.default_rng(16)
    z1, z2 = rng4.standard_normal(n), rng4.standard_normal(n)
    t = list(0.8 / np.sqrt(12.0) * SIGMA + SIGMA * z1)
    v = np.asarray(-1.8 / np.sqrt(12.0) * SIGMA + SIGMA * z2)
    v[:35] = 0.048 + SIGMA * z2[:35]          # SPY's first 35-month episode
    v = list(v)
    ev4 = _run(fixtures(v, t, ms))
    failing = [c for c in ev4["C3_CASES"] if not (c["c1"] and c["c2"])]
    record("4", "full sample passes C1 and C2",
           ev4["C1"] and ev4["C2"],
           "rho_upper=%.3f" % ev4["CORRELATION_CI"]["upper"])
    record("4", "a jackknife case fails -> C3 fails",
           (not ev4["C3"]) and len(failing) >= 1,
           "%d of %d cases fail" % (len(failing), len(ev4["C3_CASES"])))
    record("4", "candidacy fails and FULL never computed",
           (not ev4["CANDIDACY"]["candidate"])
           and (not ev4["FULL_EXECUTED"])
           and not any(k in ev4 for k in EV.FULL_FIELDS))

    # -- CASE 8 : invalid bootstrap -----------------------------------------
    flat = [0.0] * n
    _v, t8 = make_returns(17, sharpe_v=0.0, sharpe_t=0.7, rho=0.0, n=n)
    try:
        _run(fixtures(flat, t8, ms))
        record("8", "degenerate sample raises InferenceInvalid", False,
               "no exception raised")
    except I.InferenceInvalid as exc:
        record("8", "degenerate sample raises InferenceInvalid", True,
               str(exc)[:44])
    except O.StudyError as exc:
        record("8", "degenerate sample raises InferenceInvalid",
               "valid replicates" in str(exc), str(exc)[:44])

    # the same failure INSIDE a jackknife must be a C3 FAIL, never a pass
    cases = [{"c1": True, "c2": True}, {"invalid": True, "c1": False,
                                        "c2": False},
             {"c1": True, "c2": True}]
    record("8", "an invalid jackknife case fails C3",
           I.c3_pass(cases, k=3) is False)

    # -- CASE 9 / 10 : the authorization guard ------------------------------
    import value_authorization as A
    tmp = os.path.join(tempfile.mkdtemp(prefix="value_auth_"), "auth.json")
    try:
        A.validate_active("x" * 64, "rev", path=tmp)
        record("9", "absent authorization refuses", False, "no exception")
    except A.AuthorizationError as exc:
        record("9", "absent authorization refuses", True, str(exc)[:44])

    auth = A.create("x" * 64, "rev", A.OWNER_DECISION_PHRASE, path=tmp)
    A.validate_active("x" * 64, "rev", path=tmp)          # spendable once
    A.consume(auth, "REHEARSAL_RUN", path=tmp)
    try:
        A.validate_active("x" * 64, "rev", path=tmp)
        record("10", "consumed authorization refuses reuse", False,
               "no exception")
    except A.AuthorizationError as exc:
        record("10", "consumed authorization refuses reuse", True,
               str(exc)[:44])
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
    ok_bad, _p = EV.validate(bad)
    record("E", "schema rejects FULL fields on a refused branch", not ok_bad)

    print()
    failed = [r for r in results if not r[2]]
    print("  cases run: %d   failed: %d" % (len(results), len(failed)))
    print()
    print("SYNTHETIC_END_TO_END =", "PASS" if not failed else "FAIL")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
