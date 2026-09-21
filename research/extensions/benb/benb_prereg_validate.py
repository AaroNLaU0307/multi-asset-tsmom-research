"""CTA-EDGE-02-BENB — mechanical S1 pre-seal validator.

Machine checks before model checks. Every assertion is decidable without judgment and
WITHOUT ANY CANDIDATE OUTCOME: it reads the sealed contract text, the pinned data
hashes, and a synthetic sweep of the classification function. It never computes a
basis, an abnormal basis, a coefficient, a return, a Sharpe or a bootstrap.

    python research/extensions/benb/benb_prereg_validate.py     # from the repo root

Exit 0 = PASS (all checks), exit 1 = FAIL.
"""

from __future__ import annotations

import hashlib
import itertools
import os
import re
import sys

BENB = os.path.join("research", "extensions", "benb")
PREREG = os.path.join(BENB, "BENB_PREREGISTRATION.md")
S0 = os.path.join(BENB, "BENB_S0_FRAME.md")
REPAIR = os.path.join(BENB, "BENB_S0_REPAIR_RECORD.md")
OWNER = os.path.join("ops", "OWNER_DECISION_RECORD_CTA_EDGE_02_BENB.md")

S0_SHA = "5dabf6fc8af3b1c7455db72b468537428b9ca11d0188c68481e5c96b97a03b73"
REPAIR_SHA = "a4d81db3cc159f193a6aafdb3b5e5a263d138b3e307a1f7c54b1def456d0898b"

PINNED_DATA = {
    "ishares_HYG_fund_download.xml": "10dcd91e095a56d83762019738aa5b14374ea5d1f723616636b52170150ec533",
    "ishares_LQD_fund_download.xml": "d0cc3b0121806b20a227b00ae50d3f8523e6cc560e7bae16d715824b50ce0a47",
    "HYG_raw_ohlc.csv": "1ed30697cd0c665d9abe3d60abfe8c03314fb8889f3a459df207c5b85cb3bce8",
    "LQD_raw_ohlc.csv": "9d120233fd18bbd28188c18ce5a99b8347416f58b903d7452b83b47d011fe036",
    "HYG_nav_daily.csv": "7735da958ef10522e39c9138b8cf8c686206585f3b805c327588fb61e9eae5de",
    "LQD_nav_daily.csv": "3d78dbd80b92e9715eb9f6249597d65556d12b6517aad6832640e7296698007a",
    "benb_price_meta.json": "8179c06f8f8dd088d3b08cb9b4d6a1a8abbd210239f3e2b226e70de223d8b339",
}

#: The sealed materiality constants. Transcribed from BENB-OD-1 and asserted against the
#: contract text, so a drift between this file and the contract breaks a check.
M1_RETURN_FLOOR = 0.0      # lower bound of mean NET_TRADE_RETURN, STRICT >
M2_SHARPE = 0.30           # lower bound of the calendarised Sharpe, STRICT >

_results: list[tuple[bool, str, str]] = []


def check(name: str, ok, detail: str = "") -> None:
    _results.append((bool(ok), name, detail))


def read(path: str) -> str:
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def sha(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


# --------------------------------------------------------------------------- #
# The sealed classification function (contract §J.3), transcribed exactly      #
# --------------------------------------------------------------------------- #


def classify(L_T, U_T, L_O, U_O, L_N, U_N, L_R, U_R, L_S, U_S,
             loyo_ok, evaluable=True):
    """First match wins. STRICT operators throughout, per BENB-OD-1."""
    if not evaluable:
        return "F"
    if L_T <= 0:                                        # Gate 1 not supported
        nav_neg = U_N < 0
        on_pos = L_O > 0
        if nav_neg and on_pos:
            return "A-M"
        if nav_neg:
            return "A"
        if on_pos:
            return "B"
        return "C1" if U_T <= 0 else "C2"
    if not loyo_ok:                                     # Gate 1 supported
        return "G"
    if (U_R <= 0) or (U_S <= M2_SHARPE):
        return "D"
    if (L_R > M1_RETURN_FLOOR) and (L_S > M2_SHARPE):
        return "S"
    return "E"


CLASSES = ("F", "A-M", "A", "B", "C1", "C2", "G", "D", "S", "E")


def sweep():
    g = [-2.0, -0.5, 0.0, 1e-9, 0.5, 2.0]
    s = [-1.0, 0.0, 0.2999999, 0.30, 0.3000001, 1.5]
    r = [-5.0, -1e-9, 0.0, 1e-9, 3.0]
    for L_T, U_T in itertools.product(g, repeat=2):
        if L_T > U_T:
            continue
        for L_N, U_N in ((-1.0, -0.5), (-1.0, 0.5), (0.5, 1.0)):
            for L_O, U_O in ((0.5, 1.0), (-0.5, 0.5), (-1.0, -0.5)):
                for L_R, U_R in itertools.product(r, repeat=2):
                    if L_R > U_R:
                        continue
                    for L_S, U_S in itertools.product(s, repeat=2):
                        if L_S > U_S:
                            continue
                        for loyo in (True, False):
                            yield (L_T, U_T, L_O, U_O, L_N, U_N,
                                   L_R, U_R, L_S, U_S, loyo)


# --------------------------------------------------------------------------- #
# A. Package, provenance and pinned data                                       #
# --------------------------------------------------------------------------- #


def section_a() -> None:
    for p in (PREREG, S0, REPAIR, OWNER):
        check(f"A/present {p}", os.path.exists(p))
    check("A/S0 frame preserved byte-for-byte", sha(S0) == S0_SHA)
    check("A/S0 repair record preserved byte-for-byte", sha(REPAIR) == REPAIR_SHA)
    for name, want in PINNED_DATA.items():
        p = os.path.join("data", "benb", name)
        check(f"A/pinned data {name}", os.path.exists(p) and sha(p) == want)
    c = read(PREREG)
    check("A/contract is SEALED", "STATUS                 = SEALED" in c)
    check("A/seal created flag", "S1_SEAL_CREATED            = YES" in c)
    check("A/S2 not authorized", "S2_AUTHORIZED              = NO" in c)
    check("A/no run authorization", "RUN_AUTHORIZATION_CREATED  = NO" in c)
    check("A/contract cites the Owner decision record",
          "ops/OWNER_DECISION_RECORD_CTA_EDGE_02_BENB.md" in c)


# --------------------------------------------------------------------------- #
# B. The original 22 pre-seal hazards                                          #
# --------------------------------------------------------------------------- #


def section_b() -> None:
    c = read(PREREG)
    check("B/adjusted close never used in the basis",
          "RAW UNADJUSTED regular-session closing market price" in c
          and "An adjusted close may not appear anywhere in the basis" in c)
    check("B/no same-close lookahead",
          "NO SAME-CLOSE EXECUTION." in c
          and "EARLIEST_PERMITTED_EXECUTION          = open(t+1)" in c)
    check("B/overnight never credited as tradable",
          "NO OVERNIGHT RETURN MAY EVER BE CREDITED TO THE STRATEGY." in c
          and "ONLY R_TRADABLE MAY SUPPORT THE HARVESTABLE EDGE." in c)
    check("B/premium cannot enter primary support",
          "PREMIUM observations (x_t >= 0): DESCRIPTIVE_ONLY" in c)
    check("B/beta_O and beta_N have no rescue power",
          "They may NEVER rescue beta_T." in c
          and "appear in no condition that can produce `CLASS S`" in c)
    check("B/no severity-based position sizing", "NO position sizing by d_t." in c)
    check("B/no arbitrary threshold",
          "There is NO additional discount threshold." in c)
    check("B/single horizon", "NO second horizon." in c
          and "NO holding-period search." in c)
    check("B/cost defined", "ONE_WAY_COST    = 5.0 bps" in c
          and "ROUND_TRIP_COST = 10.0 bps" in c)
    check("B/precedence explicit, first match wins",
          "FIRST MATCH WINS" in c and c.count("STEP ") >= 10)
    check("B/mixed beta_O/beta_N case handled",
          "CLASS A-M -- MIXED NON-HARVESTABLE CONVERGENCE" in c)
    check("B/C1 and C2 not collapsed",
          "CLASS C1 -- TRADABLE CONVERGENCE RELIABLY EXCLUDED" in c
          and "CLASS C2 -- UNRESOLVED / LOW POWER" in c)
    check("B/fragility has its own class", "CLASS G -- FRAGILE / YEAR-DEPENDENT" in c)
    check("B/no LQD rescue path", "LQD CANNOT RESCUE HYG." in c)
    check("B/bootstrap reconstruction resolved at S1",
          "BOOTSTRAP_RECONSTRUCTION_RULE" in c
          and "is NOT recomputed inside a replicate" in c)
    check("B/exactly one fragility diagnostic",
          "Exactly one fragility diagnostic exists." in c)
    check("B/slope-materiality withdrawn", "IS WITHDRAWN AND MAY NOT RETURN" in c)
    check("B/no basis or sign count before seal",
          "DISCOUNT_OBSERVATION_COUNT = UNKNOWN AT S1" in c
          and "HISTORICAL_BASIS_COMPUTED  = NO" in c)
    check("B/evidence ceiling fixed",
          "EVIDENCE_CEILING = supported" in c and "NEVER confirmed" in c)
    check("B/Fable exposed YES, Astra NO",
          "FABLE_DESIGN_EXPOSED = YES" in c and "ASTRA_DESIGN_EXPOSED = NO" in c)
    check("B/ex-date rule sealed",
          "EXCLUDE observation t whenever t+1 is an ex-date" in c)
    check("B/discount-only primary sample",
          "PRIMARY_SAMPLE = eligible observations with x_t < 0 ONLY" in c)


# --------------------------------------------------------------------------- #
# C. The new M2 checks                                                         #
# --------------------------------------------------------------------------- #


def section_c() -> None:
    c = read(PREREG)
    o = read(OWNER)
    check("C/M2 exists in the contract",
          "M2_VALUE             = +0.30" in c and "M2_METRIC            =" in c)
    check("C/M2 authority exists (BENB-OD-1)",
          "DECISION_ID  = BENB-OD-1" in o and "M2_VALUE              = +0.30" in o)
    check("C/Owner record states the STRICT operator",
          "M2_BOUNDARY_OPERATOR  = STRICT  >" in o)
    check("C/contract states the STRICT operator",
          "M2_BOUNDARY_OPERATOR = STRICT  >" in c)
    check("C/M2 pass rule is on the interval LOWER endpoint",
          "lower 95 % bound of the calendarised annualised Sharpe  >  +0.30" in c)
    check("C/boundary semantics spelled out",
          "L_S = 0.300000...   ->  FAILS M2" in c)
    check("C/point estimate can never pass M2",
          "The POINT estimate of the Sharpe NEVER passes M2." in c)
    check("C/Owner record fixes the monthly construction",
          "MONTHLY_CONSTRUCTION  = sum NET_TRADE_RETURN by ENTRY calendar month" in o
          and "ZERO_SIGNAL_MONTH     = exactly 0" in o
          and "RISK_FREE_RATE        = 0" in o
          and "ANNUALISATION         = sqrt(12)" in o)
    check("C/Owner record forbids the three post-hoc repairs",
          "NO active-month-only Sharpe." in o and "NO sparsity adjustment." in o
          and "NO post-outcome threshold change" in o)
    check("C/decision recorded as BENB-specific, not inherited",
          "NOT INHERITED FROM  C-A · CTA-EDGE-01-TA · any programme-wide convention." in o)
    check("C/decision taken before any outcome",
          "DECIDED BEFORE  historical basis computation" in o)
    check("C/M1 semantics unchanged",
          "M1  lower 95 % bound of mean NET_TRADE_RETURN  >  0" in c
          and "M1 semantics are **unchanged** by this decision." in c)

    # the classification branches must use the strict operator, and no ">=" anywhere
    j0 = c.index("### J.3 The sealed decision order")
    j1 = c.index("**Disjointness and exhaustiveness.**")
    block = c[j0:j1]
    check("C/CLASS S branch uses STRICT >",
          "iff  (L_R > 0) AND (L_S > +0.30)" in block)
    check("C/CLASS D branch uses <= on the Sharpe upper bound",
          "iff  (U_R <= 0) OR (U_S <= +0.30)" in block)
    check("C/no '>=' anywhere in the classification block",
          ">=" not in block, "a classification branch uses >=")
    check("C/no stale 'M2 OPERATOR' placeholder remains",
          "M2 OPERATOR" not in c and "NOT SET" not in c)


# --------------------------------------------------------------------------- #
# D. Mechanical properties of the classification function                      #
# --------------------------------------------------------------------------- #


def section_d() -> None:
    seen = set()
    bad = 0
    promote = []
    m2_boundary_ok = True
    for case in sweep():
        # the evaluability gate is swept too, so CLASS F is reached by the sweep
        # itself rather than only by a bespoke probe
        seen.add(classify(*case, evaluable=False))
        k = classify(*case)
        if k not in CLASSES:
            bad += 1
        seen.add(k)
        # no diagnostic may promote: firing beta_O / beta_N cannot create S
        L_T, U_T, L_O, U_O, L_N, U_N, L_R, U_R, L_S, U_S, loyo = case
        if k == "S":
            base = classify(L_T, U_T, -1.0, -0.5, 0.5, 1.0,
                            L_R, U_R, L_S, U_S, loyo)
            if base != "S":
                promote.append(case)
            if not (L_S > 0.30):
                m2_boundary_ok = False
            if not (L_R > 0.0):
                m2_boundary_ok = False
    check("D/classification total and single-valued", bad == 0, f"{bad} undefined")
    check("D/all classes reachable", set(CLASSES) <= seen,
          f"missing {sorted(set(CLASSES) - seen)}")
    check("D/no diagnostic can promote to S", not promote, f"{len(promote)} cases")
    check("D/CLASS S always satisfies BOTH M1 and M2 strictly", m2_boundary_ok)
    check("D/F is reachable only via NOT EVALUABLE",
          classify(1, 2, 1, 2, -2, -1, 1, 2, 1, 2, True, evaluable=False) == "F")

    # explicit boundary probes required by the task
    base = dict(L_T=1.0, U_T=2.0, L_O=-1.0, U_O=-0.5, L_N=0.5, U_N=1.0,
                L_R=1.0, U_R=3.0, loyo_ok=True)
    exactly = classify(base["L_T"], base["U_T"], base["L_O"], base["U_O"],
                       base["L_N"], base["U_N"], base["L_R"], base["U_R"],
                       0.30, 1.5, True)
    above = classify(base["L_T"], base["U_T"], base["L_O"], base["U_O"],
                     base["L_N"], base["U_N"], base["L_R"], base["U_R"],
                     0.3000001, 1.5, True)
    check("D/Sharpe lower bound EXACTLY 0.30 fails M2", exactly != "S",
          f"got {exactly}")
    check("D/Sharpe lower bound just above 0.30 may pass", above == "S",
          f"got {above}")
    # M1 boundary: mean net return lower bound exactly 0 must fail
    m1_exact = classify(1.0, 2.0, -1.0, -0.5, 0.5, 1.0, 0.0, 3.0, 1.0, 1.5, True)
    check("D/mean net return lower bound EXACTLY 0 fails M1", m1_exact != "S",
          f"got {m1_exact}")
    # point estimate cannot substitute: a huge U_S with L_S below the bar is never S
    pt = classify(1.0, 2.0, -1.0, -0.5, 0.5, 1.0, 1.0, 3.0, 0.0, 99.0, True)
    check("D/point-estimate/upper-bound Sharpe cannot substitute for the lower bound",
          pt != "S", f"got {pt}")


# --------------------------------------------------------------------------- #
# E. Governance records                                                        #
# --------------------------------------------------------------------------- #


def section_e() -> None:
    tl = read(os.path.join("research", "extensions", "TRIAL_LEDGER.md"))
    sr = read(os.path.join("research", "extensions", "SAMPLE_REUSE.md"))
    rx = read(os.path.join("ops", "REVIEWER_EXPOSURE_LOG.md"))
    ea = read(os.path.join("ops", "EXECUTION_AUTHORIZATIONS.md"))
    check("E/TRIAL_LEDGER declares family F-BENB", "**`F-BENB`**" in tl)
    check("E/TRIAL_LEDGER states m = 1 with no correction",
          "**m = 1; NO multiplicity correction**" in tl and "F-BENB" in tl)
    check("E/TRIAL_LEDGER asserts no N_trials figure for the ETF panel",
          "D-ETF-COUNT" in tl and "UNKNOWN_PENDING_AARON_DECISION" in tl)
    check("E/SAMPLE_REUSE carries the BENB addendum",
          "KB-1 addendum — `CTA-EDGE-02-BENB`" in sr)
    check("E/SAMPLE_REUSE records mixed provenance and the ceiling",
          "MIXED" in sr.upper() and "CTA-EDGE-02-BENB" in sr)
    check("E/REVIEWER_EXPOSURE_LOG has the Fable and Astra rows",
          "| S34 |" in rx and "| S35 |" in rx)
    check("E/no execution authorization exists for this lineage",
          "CTA-EDGE-02-BENB" not in ea and "BENB-AUTH" not in ea)


def main() -> int:
    for fn in (section_a, section_b, section_c, section_d, section_e):
        try:
            fn()
        except Exception as exc:                       # a crashing check fails
            check(f"{fn.__name__} raised", False, f"{type(exc).__name__}: {exc}")
    width = max(len(n) for _, n, _ in _results)
    failed = 0
    for ok, name, detail in _results:
        if not ok:
            failed += 1
            print(f"FAIL  {name:<{width}}  {detail}")
    print(f"\nCTA-EDGE-02-BENB S1 PRE-SEAL VALIDATOR: "
          f"{len(_results) - failed}/{len(_results)} PASS")
    print("RESULT:", "PASS" if failed == 0 else f"FAIL ({failed} failing)")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
