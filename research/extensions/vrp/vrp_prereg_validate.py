# -*- coding: utf-8 -*-
"""Mechanical validation of the TSMOM-VRP-01 S1 package.

Structure, vocabulary, constants and provenance only. NO market data, NO settlement,
NO return, NO performance quantity is read or computed. This script never opens data/.

Convention follows research/extensions/ca/ca_prereg_validate.py and
research/extensions/value/value_prereg_validate.py.

Exit code 0 = every check PASS; 1 = at least one FAIL.
"""
import hashlib
import io
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
WORKSPACE = os.path.abspath(os.path.join(REPO, ".."))
os.chdir(REPO)

PREREG = "research/extensions/vrp/VRP_PREREGISTRATION.md"
ACC = "research/extensions/vrp/VRP_IMPLEMENTATION_ACCEPTANCE_CONTRACT.md"
EXP = "research/extensions/vrp/VRP_EXPOSURE_DISCLOSURE.md"
S0_REPAIRED = os.path.join(WORKSPACE, "2026-09-14-tsmom-vrp-01-s0-frame-fable-02-repaired.md")
ODR = os.path.join(WORKSPACE, "2026-09-14-tsmom-vrp-01-owner-decision-record.md")

S0_REPAIRED_SHA = "53f2d094d6fa06358869dda88e77daa80e0feba22c7f9253f2649e622a70d03a"
ODR_SHA = "76232d6c29980c79ece2ba6ead744c203fcf6fa15a70b6045cca91c1d40b9be3"
ETF_PANEL_SHA = "3d2a7a56dbd92d4ff8138cfd894c87f5ac5ac088a11165db870673e0c05c3c31"

ok = True


def ck(label, cond, detail=""):
    global ok
    if not cond:
        ok = False
    print("  %-70s %s   %s" % (label, "PASS" if cond else "FAIL", detail))


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def flat(s):
    return re.sub(r"\s+", " ", s)


def has(hay, *phrases):
    return all(flat(p) in hay for p in phrases)


def section(title):
    print("\n" + title)


# --------------------------------------------------------------------------- #
section("PROVENANCE — authoritative inputs")
for label, path, expected in (("repaired S0 frame", S0_REPAIRED, S0_REPAIRED_SHA),
                              ("Owner Decision Record", ODR, ODR_SHA)):
    exists = os.path.isfile(path)
    ck("%s present" % label, exists, path)
    if exists:
        got = sha256_file(path)
        ck("%s SHA256 matches pinned" % label, got == expected, got[:16])

# --------------------------------------------------------------------------- #
section("PACKAGE — artifacts present, LF-only, no data")
for p in (PREREG, ACC, EXP):
    ck("present: %s" % p, os.path.isfile(p))
for p in (PREREG, ACC, EXP):
    if os.path.isfile(p):
        raw = open(p, "rb").read()
        ck("LF-only bytes: %s" % os.path.basename(p), b"\r" not in raw, "%d bytes" % len(raw))
pkg_dir = "research/extensions/vrp"
bad = [f for f in os.listdir(pkg_dir)
       if f.lower().endswith((".csv", ".parquet", ".json", ".pkl", ".npy", ".h5", ".xlsx"))]
ck("no data-like files inside the package", not bad, ",".join(bad))
ck("no data/vix directory exists yet", not os.path.isdir("data/vix"))

if not os.path.isfile(PREREG):
    print("\nRESULT: FAIL (preregistration missing)")
    sys.exit(1)

pre = flat(io.open(PREREG, encoding="utf-8").read())
acc = flat(io.open(ACC, encoding="utf-8").read()) if os.path.isfile(ACC) else ""
exp = flat(io.open(EXP, encoding="utf-8").read()) if os.path.isfile(EXP) else ""

# --------------------------------------------------------------------------- #
section("PROVENANCE — hash references inside the contract")
ck("contract references repaired S0 hash", S0_REPAIRED_SHA in pre)
ck("contract references ODR hash", ODR_SHA in pre)
ck("contract references frozen ETF panel hash", ETF_PANEL_SHA in pre)
ck("contract records S0-01 as historical only", has(pre, "historical only"))

# --------------------------------------------------------------------------- #
section("OWNER VALUES — exact transcription (VRP-OD-2 … VRP-OD-9)")
REQUIRED = [
    ("theta = 0.25", "theta = 0.25"),
    ("b = 0.30", "b = 0.30"),
    ("+E = +0.075", "= +0.075"),
    ("−F = −0.075", "−F = −0.075"),
    ("J = 30", "J = 30"),
    ("sensitivity 0.01·K", "0.01 · K"),
    ("m_J = 40", "m_J = 40"),
    ("lambda = 0.10", "lambda = 0.10"),
    ("R_J = 0.50·K", "0.50 · K"),
    ("(1−b)K ≥ R_J : 0.70·K", "0.70 · K"),
    ("granularity ±10 %", "±10 %"),
    ("c0 = 0.10", "0.10 , normalized_contemporaneous_minimum_tick"),
    ("c0 = spread + slippage together", "TOTAL SPREAD + SLIPPAGE TOGETHER"),
    ("commission $2.00", "$2.00 per standard-contract-side"),
    ("funding charge NONE", "funding charge = NONE"),
    ("c0 = 0.05 descriptive only", "c0 = 0.05"),
    ("beta = 0.06", "beta = 0.06"),
    ("s = 0.20", "= 0.20"),
    ("W0 = $1,000,000", "$1,000,000"),
    ("K_0 = $200,000", "$200,000"),
    ("$2,000 per VIX point", "$2,000 per VIX point"),
    ("delta_tail = 0.0075", "delta_tail = 0.0075"),
    ("k = 3", "k = 3"),
    ("ratio floor 0.0025", "0.0025"),
    ("ratio floor 95 %", "≥ 95 %"),
    ("cutoff 2026-09-01", "2026-09-01"),
    ("Stage A last month 2026-08", "2026-08"),
    ("Stage B ends 2026-05-31", "2026-05-31"),
    ("June 1–12 2026 not an observation", "NOT a monthly observation"),
    ("N_A = 120", "N_A = 120"),
    ("N_B = 120", "N_B = 120"),
    ("n_T_min_prosp = 10", "n_T_min_prosp = 10"),
    ("sigma_plan = 15 %", "sigma_plan = 15 %"),
    ("planning dispersion 4.3", "4.3 comparable points"),
    ("dependence inflation 1.25", "1.25"),
    ("block length 12", "12 months"),
    ("10,000 replicates", "10,000"),
    ("9,500 floor", "9,500"),
    ("seed 7", "SeedSequence(7)"),
    ("24 distinct months rule", "24 distinct calendar months"),
    ("ceil(0.5·|T_full|)", "ceil( 0.5 · |T_full| )"),
    ("FM-1 DGS3MO", "DGS3MO"),
    ("FM-1 7 calendar days", "7 calendar days"),
    ("FM-1 Y/100/12", "Y / 100 / 12"),
]
for label, phrase in REQUIRED:
    ck(label, has(pre, phrase))

# --------------------------------------------------------------------------- #
section("STRUCTURE — sealed sections and states")
for label, phrase in [
    ("object A no claim power", "NO CLAIM POWER"),
    ("VIX² − realised variance is not a premise", "IS NOT an edge premise"),
    ("no P&L-free edge premise", "There is no P&L-free edge premise"),
    ("precedence levels 1–4", "LEVEL 4"),
    ("Stage B only if Stage A supported", "ONLY IF VRP-A = SUPPORTED"),
    ("Stage A state materially_adverse", "materially_adverse"),
    ("Stage A state usefulness_excluded", "usefulness_excluded"),
    ("equality unresolved", "Equality L = +0.075 is UNRESOLVED"),
    ("no Class-2 relabelling", "No post-result Class-2 relabelling"),
    ("stress on PRE-STRESS holdings", "PRE-STRESS holdings"),
    ("J is NOT spot VIX", "NOT** spot VIX"),
    ("Stage A benchmark not self-financing", "NOT a self-financing wealth path"),
    ("no clipping", "below −100 %"),
    ("EXCESS OF CASH primary", "EXCESS OF CASH"),
    ("roll weight formula", "w_front(d) = dr(d) / dt"),
    ("front zero before final settlement", "reaches zero at the last settlement before final settlement"),
    ("missing-price max 2", "Maximum 2 carry-forward business days per contract per calendar month"),
    ("never drop the month", "never dropping the month"),
    ("2007 rescaling", "2007 quotation / multiplier rescaling"),
    ("book exhaustion terminates", "terminate the ledger"),
    ("no restart", "No restart"),
    ("pro-rata liquidation", "pro-rata slice"),
    ("no external borrowing", "No external borrowing"),
    ("oracle identity", "0.80 · r_core,t + 0.20 · r_A,t"),
    ("Stage B estimand D", "mean_{t ∈ T} ( r_book,t − r_core,t )"),
    ("ratio has no gate power", "tail-retention ratio has no gate power"),
    ("joint triple resampling", "aligned triple `(r_book, r_core, r_SPY)` jointly"),
    ("no sign clipping", "no sign clipping"),
    ("annualisation arithmetic", "12 · mean"),
    ("C-A blindness", "2026-09-11"),
    ("DEFERRED_EVALUATION_FROZEN_WINDOW", "DEFERRED_EVALUATION_FROZEN_WINDOW"),
    ("NOT_EVALUABLE", "NOT_EVALUABLE"),
    ("no early C-A reveal", "an early C-A reveal"),
    ("DESIGN_INFORMED_FIRST_LOCAL_USE", "DESIGN_INFORMED_FIRST_LOCAL_USE"),
    ("N_trials = 0", "N_trials = 0"),
    ("failure classes 1–5", "TRULY_UNTESTED_SUBSPACE_REMAINS"),
    ("stop rule present", "Stage A SUPPORTED → Stage B may execute ONCE"),
    ("descriptives PROMOTION_POWER = NONE", "PROMOTION_POWER = NONE"),
    ("ten self-check questions all NO", "SELF_CHECK_1_TO_10 = ALL_NO"),
    ("contributor disclosure", "MATERIAL DESIGN CONTRIBUTOR"),
    ("ChatGPT controller", "programme controller / acceptance checker"),
    ("canonical frozen", "remains FROZEN"),
    ("C-A live", "LIVE / S3 PASSIVE ACCRUAL"),
    ("C-D closed", "CLOSED AT HOLD"),
    ("no upgrade of canonical evidence", "upgrades canonical TSMOM evidence"),
]:
    ck(label, phrase is True or has(pre, phrase))

# --------------------------------------------------------------------------- #
section("FORBIDDEN PHRASES AND OBJECTS")
for label, phrase in [
    ("no 'latest available'", "latest available"),
    ("no contango filter", "sell only in contango"),
    ("no weekly futures as object", "hold weekly"),
]:
    # the phrase may appear only inside an explicit prohibition; require that every occurrence is negated
    idxs = [m.start() for m in re.finditer(re.escape(flat(phrase)), pre)]
    negated = all(any(w in pre[max(0, i - 120):i + 120] for w in ("never", "NOT", "not ", "no ", "No ")) for i in idxs)
    ck(label, negated, "%d occurrence(s), all negated" % len(idxs))

# --------------------------------------------------------------------------- #
section("COMPANION ARTIFACTS")
ck("acceptance contract lists sabotage tests", has(acc, "Sabotage tests"))
ck("acceptance contract lists C-A access audit", has(acc, "C-A access audit"))
ck("acceptance contract pins frozen constants", has(acc, "theta=0.25, b=0.30, E=0.075"))
ck("acceptance contract: no outcome before acceptance", has(acc, "No generated outcome before acceptance"))
ck("exposure disclosure: no VIX outcome accessed", has(exp, "Historical VIX-futures settlement values"))
ck("exposure disclosure: contributor provenance", has(exp, "MATERIAL_DESIGN_CONTRIBUTOR"))
ck("exposure disclosure: design-exposed episodes", has(exp, "April 2025 volatility episode"))

print("\nRESULT: %s" % ("PASS" if ok else "FAIL"))
sys.exit(0 if ok else 1)
