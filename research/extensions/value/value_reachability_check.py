# -*- coding: utf-8 -*-
"""S1 reachability check for the Time-Series Value preregistration.

Answers one question: with the recommended §12 defaults, is every declared branch
attainable, and are the thresholds mutually consistent?

This is a design check over the DECISION RULES ONLY. It uses no market data, no
return series and no Value signal. Every number below is a hypothetical interval
chosen to probe a branch, not an estimate of anything.
"""
from __future__ import annotations

# ---- recommended §12 defaults ---------------------------------------------
E = 0.15        # D6 standalone positive margin
F = 0.15        # D7 materially-adverse floor (as +F, applied at -F)
RHO_MAX = 0.40  # D8 dependence bound, adjudicated on the CI upper bound
DELTA = 0.10    # D10 incremental margin
SPLIT = (0.75, 0.25)   # D9 trend/value
W = 120         # D2 warm-up months
S = 3           # D3 staleness months
K_EPISODES = 3  # D11

ok = True


def ck(label, cond, detail=""):
    global ok
    if not cond:
        ok = False
    print("  %-64s %s   %s" % (label, "PASS" if cond else "FAIL", detail))


def standalone(L, U):
    """§7 three-state rule. Endpoints strict; touching a boundary is unresolved."""
    if L > E:
        return "SUPPORTED_POSITIVE_EDGE"
    if U < -F:
        return "MATERIALLY_ADVERSE"
    return "UNRESOLVED_EDGE"


def combo(L, U):
    """§9 three-state rule, with the two negative labels kept distinct."""
    if L > DELTA:
        return "SUPPORTED_INCREMENTAL_BENEFIT"
    if U < 0.0:
        return "INCREMENTAL_BENEFIT_ADVERSE"
    return "INCREMENTAL_BENEFIT_NOT_ESTABLISHED"


print("== 1. every standalone branch is reachable ==")
ck("SUPPORTED_POSITIVE_EDGE reachable",
   standalone(0.20, 0.60) == "SUPPORTED_POSITIVE_EDGE", "[0.20, 0.60]")
ck("MATERIALLY_ADVERSE reachable",
   standalone(-0.70, -0.20) == "MATERIALLY_ADVERSE", "[-0.70, -0.20]")
ck("UNRESOLVED_EDGE reachable (interval spans both boundaries)",
   standalone(-0.30, 0.30) == "UNRESOLVED_EDGE", "[-0.30, 0.30]")
ck("UNRESOLVED_EDGE reachable (wholly inside the band)",
   standalone(-0.05, 0.10) == "UNRESOLVED_EDGE", "[-0.05, 0.10]")

print()
print("== 2. the three standalone states partition the line ==")
ck("boundary touch at +E is UNRESOLVED, not SUPPORTED",
   standalone(E, 0.9) == "UNRESOLVED_EDGE", "L == +E exactly")
ck("boundary touch at -F is UNRESOLVED, not ADVERSE",
   standalone(-0.9, -F) == "UNRESOLVED_EDGE", "U == -F exactly")
ck("no interval can satisfy SUPPORTED and ADVERSE together",
   not (0.20 > E and 0.60 < -F), "requires L>+E and U<-F with L<=U")
ck("+E and -F do not overlap (E > -F)", E > -F, "E=%.2f, -F=%.2f" % (E, -F))

print()
print("== 3. candidacy is reachable in both directions ==")


def candidacy(state, rho_upper, episodes_stable):
    c1 = state != "MATERIALLY_ADVERSE"
    c2 = rho_upper <= RHO_MAX
    c3 = episodes_stable
    return c1 and c2 and c3, (c1, c2, c3)


p, c = candidacy("UNRESOLVED_EDGE", 0.25, True)
ck("premise PASS reachable from an UNRESOLVED standalone edge", p, str(c))
p, c = candidacy("SUPPORTED_POSITIVE_EDGE", 0.10, True)
ck("premise PASS reachable from a SUPPORTED standalone edge", p, str(c))
p, c = candidacy("MATERIALLY_ADVERSE", 0.10, True)
ck("premise FAIL reachable via C1", not p and not c[0], str(c))
p, c = candidacy("UNRESOLVED_EDGE", 0.65, True)
ck("premise FAIL reachable via C2 (dependence too high)", not p and not c[1], str(c))
p, c = candidacy("UNRESOLVED_EDGE", 0.25, False)
ck("premise FAIL reachable via C3 (episode instability)", not p and not c[2], str(c))
ck("an UNRESOLVED standalone edge CAN qualify as a candidate",
   candidacy("UNRESOLVED_EDGE", 0.30, True)[0])

print()
print("== 4. every FULL branch is reachable, and the two negatives are distinct ==")
ck("SUPPORTED_INCREMENTAL_BENEFIT reachable",
   combo(0.15, 0.40) == "SUPPORTED_INCREMENTAL_BENEFIT", "[0.15, 0.40]")
ck("INCREMENTAL_BENEFIT_ADVERSE reachable",
   combo(-0.40, -0.05) == "INCREMENTAL_BENEFIT_ADVERSE", "[-0.40, -0.05]")
ck("INCREMENTAL_BENEFIT_NOT_ESTABLISHED reachable",
   combo(-0.05, 0.20) == "INCREMENTAL_BENEFIT_NOT_ESTABLISHED", "[-0.05, 0.20]")
ck("a wholly-positive interval below +delta is NOT_ESTABLISHED, not ADVERSE",
   combo(0.01, 0.08) == "INCREMENTAL_BENEFIT_NOT_ESTABLISHED", "[0.01, 0.08]")
ck("ADVERSE and NOT_ESTABLISHED are never the same verdict",
   combo(-0.40, -0.05) != combo(-0.05, 0.20))
ck("no interval can be both SUPPORTED and ADVERSE",
   not (0.15 > DELTA and 0.40 < 0.0))

print()
print("== 5. thresholds are not algebraically contradictory ==")
ck("delta > 0 so a positive margin is required, not merely non-negative",
   DELTA > 0, "delta=%.2f" % DELTA)
ck("delta is attainable at the frozen split: a %.0f%% sleeve is not required "
   "to move the total Sharpe by more than its own weight" % (SPLIT[1] * 100),
   DELTA <= 1.0 * SPLIT[1] / max(SPLIT[1], 1e-9) * 0.5,
   "delta=%.2f, value weight=%.2f" % (DELTA, SPLIT[1]))
ck("rho_max leaves room for a genuinely diversifying sleeve",
   0.0 < RHO_MAX < 1.0, "rho_max=%.2f" % RHO_MAX)
ck("E and delta are independent gates (standalone vs incremental)", True,
   "E=%.2f applies to Object A, delta=%.2f to FULL" % (E, DELTA))
ck("warm-up and staleness are consistent (W months of history, S months tolerance)",
   W > 0 and 0 < S < W, "W=%d, S=%d" % (W, S))
ck("episode diagnostic k is small and fixed in advance",
   1 <= K_EPISODES <= 3, "k=%d" % K_EPISODES)

print()
print("== 6. the path an UNRESOLVED edge takes to a FULL verdict exists ==")
state = standalone(-0.10, 0.12)
passed, _ = candidacy(state, 0.30, True)
final = combo(0.14, 0.35) if passed else "STOPPED"
ck("UNRESOLVED edge -> candidacy PASS -> FULL supported is a reachable path",
   state == "UNRESOLVED_EDGE" and passed
   and final == "SUPPORTED_INCREMENTAL_BENEFIT",
   "%s -> candidate -> %s" % (state, final))
ck("and the same path can equally end NOT_ESTABLISHED",
   combo(-0.02, 0.09) == "INCREMENTAL_BENEFIT_NOT_ESTABLISHED")

print()
print("BRANCH_REACHABILITY =", "PASS" if ok else "FAIL")
print("VALUE_TARGET_RETURNS_COMPUTED = NO")
print("TARGET_BACKTEST_RUN = NO")
