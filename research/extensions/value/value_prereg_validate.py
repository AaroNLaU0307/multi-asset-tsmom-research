# -*- coding: utf-8 -*-
"""Mechanical validation of the Time-Series Value preregistration draft.

Structure and provenance only. No market data, no signal, no return, no
performance quantity is read or computed.

Phrase checks are whitespace-insensitive on purpose: the requirement is that a
clause be PRESENT, not that it avoid a line wrap. A raw substring search fails on
wrapping and would pass on a clause reworded into meaninglessness.
"""
import hashlib
import io
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
os.chdir(REPO)
PREREG = "research/extensions/value/VALUE_PREREGISTRATION_DRAFT.md"
INVENTORY = "research/extensions/value/VALUE_DATA_INVENTORY.json"

t = io.open(PREREG, encoding="utf-8").read()
flat = re.sub(r"\s+", " ", t)
inv = json.load(io.open(INVENTORY, encoding="utf-8"))

ok = True


def ck(label, cond, detail=""):
    global ok
    if not cond:
        ok = False
    print("  %-58s %s   %s" % (label, "PASS" if cond else "FAIL", detail))


def has(*phrases):
    return all(re.sub(r"\s+", " ", p) in flat for p in phrases)


print("== C3 semantics ==")
ck("C3 requires the premise conditions to survive",
   has("premise conditions survive",
       "both **C1 and C2 are recomputed",
       "all three** jackknife cases"))
ck("C3 pass rule is C1 AND C2 in every jackknife",
   has("C1(sample " + chr(92) + " M(e)) = PASS  AND  C2(sample "
       + chr(92) + " M(e)) = PASS"))
ck("exactly one deletion operator, frozen",
   has("The deletion operator — exactly one, FROZEN",
       "delete those calendar months from the entire paired evaluation sample"))
ck("operator forbids the weaker alternatives",
   has("remove only the contributing instrument while keeping the portfolio sample",
       "replace an instrument", "reweight the sleeve",
       "redraw episode boundaries", "use returns to define an episode"))
ck("invalid jackknife case is a FAIL, not a default pass",
   has("counts as **FAIL**, never as a pass"))
ck("superseded sign rule demoted, no adjudicating power",
   has("no adjudicating power", "It cannot pass, fail, or modify C3"))
ck("D11 row states the restored rule",
   has("C1 ∧ C2 both pass in all three leave-one-episode-out samples"))
ck("episode definition is return-free and deterministic",
   has("maximal run of consecutive months", "never from returns",
       "That ordering is total"))

print()
print("== CPI seasonal-adjustment consistency ==")
ck("policy frozen as all-items NSA for every economy",
   has("ALL-ITEMS NOT-SEASONALLY-ADJUSTED PRICE INDEX FOR EVERY ECONOMY"))
ck("seven economies each marked NSA", t.count("| **NSA** |") == 7,
   "%d rows" % t.count("| **NSA** |"))
ck("US corrected to CPIAUCNS; no live CPIAUCSL cut-off row",
   has("`CPIAUCNS` (US)") and "| `CPIAUCSL` (US) |" not in t)
ck("SA/NSA established mechanically, not by ticker convention alone",
   has("0.00633", "0.00133", "factor of 4.7"))
ck("Japan SA tables 16-1/16-2 explicitly excluded",
   has("16-1 and", "are **not** used"))
ck("reason is measurement consistency, not signal behaviour",
   has("not** chosen by inspecting signal behaviour"))

print()
print("== real-FX specification ==")
ck("bilateral formula stated algebraically",
   has("r_f(t) = log S_f(t) + log P_US(t−2) − log P_f(t−2)"))
ck("nominal orientation / inversion rule explicit",
   has("S_f(t) = 1 / q_f(t)", "DEXUSEU, DEXUSUK"))
ck("basket aggregation frozen as a weighted mean of logs",
   has("r_basket(t) = Σ_f  w_f · r_f(t)", "weighted geometric mean"))
ck("fixed USDX weights, BIS effective index forbidden",
   has("EUR 0.576", "Σ w_f = 1", "changing-weight BIS effective index is **forbidden**"))
ck("both Value objects defined algebraically",
   has("x_UUP(t) = − r_basket(t)", "x_FXY(t) = + r_JPY(t)"))
ck("log choice justified by base invariance", has("Why logs"))

print()
print("== frozen window and decisions ==")
ck("evaluation window unchanged",
   has("EVALUATION_START  = 2014-07", "EVALUATION_END    = 2026-05",
       "CALENDAR_MONTH_COUNT = 143"))
ck("TLT named as the binding start object", has("**TLT binds the start.**"))
ck("future availability is prospective, not asserted as fact",
   has("prospectively rather than as a current fact",
       "not a claim that any future month's ETF prices exist"))
ck("panel deliberately not refreshed", has("deliberately **not** refreshed"))
ck("eleven owner decisions frozen",
   len(re.findall(r"\|\s*\*\*(D\d+)\*\*\s*\|", t)) == 11)
ck("no owner decisions remaining", has("OWNER_DECISIONS_REMAINING = NONE"))

print()
print("== unchanged commitments ==")
ck("credit object fixed, BAA-AAA inactive, overlap diagnostic-only",
   has("CREDIT_OBJECT = BAA10Y", "not an active fallback",
       "DIAGNOSTIC / CLAIM-INTERPRETATION ONLY"))
ck("standalone and FULL inequalities strict with boundary treatment",
   has("L_V >  +0.15", "U_V <  −0.15", "L_combo >  +0.10", "U_combo <   0.00",
       "Both inequalities are **strict**"))
ck("three FULL labels with distinct meanings",
   has("a strict adverse finding", "this is NOT evidence of harm"))
ck("one bootstrap engine; IID correlation interval forbidden",
   has("one engine for all three interval statistics",
       "an IID correlation interval is", "explicitly forbidden"))
ck("Shiller vintage limitation frozen",
   has("RECONSTRUCTED_HISTORICAL_SERIES_WITH_NON-VINTAGE_LIMITATION"))
ck("claim ceiling explicit", has("T0 / POST-EXPOSURE / AT_MOST_SUPPORTED"))
# Seal state: assert INTERNAL CONSISTENCY rather than hard-coding one state, so
# this validator stays meaningful both before and after the Owner seal.
sealed_flag = has("VALUE_PREREG_SEALED = YES")
unsealed_flag = has("VALUE_PREREG_SEALED = NO")
ck("seal flag is present and unambiguous", sealed_flag != unsealed_flag,
   "SEALED" if sealed_flag else "UNSEALED")
if sealed_flag:
    ck("sealed: heading, status and closing gate all agree",
       has("PREREGISTRATION (**SEALED**)", "STATUS = SEALED",
           "VALUE_PREREG_SEAL_DECISION",
           "This contract is SEALED and its scientific content is frozen",
           "NEXT GATE = S2 BUILD"))
    ck("sealed: still not executed and not authorised",
       has("VALUE_FULL_PERFORMANCE_EXECUTED = NO",
           "A SEAL IS NOT AUTHORIZATION TO EXECUTE",
           "no such authorization exists"))
else:
    ck("unsealed: heading and closing gate agree",
       has("PREREGISTRATION **DRAFT** (UNSEALED)", "NEXT GATE = AARON"))
ck("no target outcome recorded", has("TARGET_OUTCOMES_COMPUTED = NO"))

print()
print("== provenance ==")
groups = (inv["accepted_objects"] + inv["unblock_pass"]["series"]
          + inv["phase_a_closure"]["series"] + inv["phase_a_correction"]["series"]
          + [inv["s1_final_repair"]["us_cpi_corrected"]])
seen, bad = set(), []
for a in groups:
    f = a.get("raw_file")
    if not f or f in seen:
        continue
    seen.add(f)
    if not os.path.isfile(f):
        bad.append((f, "missing"))
        continue
    h = hashlib.sha256(io.open(f, "rb").read()).hexdigest()
    if h != a.get("sha256_of_raw_file_on_disk"):
        bad.append((f, "hash mismatch"))
ck("every recorded raw file re-hashes", not bad, "%d file(s) checked" % len(seen))
ck("CPI policy recorded in the inventory",
   inv["s1_final_repair"]["cpi_seasonal_adjustment_policy"].startswith("ALL-ITEMS NOT"))

print()
print("PREREG_MECHANICAL_VALIDATION =", "PASS" if ok else "FAIL")
print("VALUE_TARGET_RETURNS_COMPUTED = NO")
print("TARGET_BACKTEST_RUN = NO")
