"""CTA-EDGE-01-TA — mechanical S1 seal validator.

Machine checks before model checks. Every assertion here is decidable without any
judgment and without any candidate outcome.

    python research/extensions/ta/ta_prereg_validate.py        # from the repo root

Exit 0 = PASS (all checks), exit 1 = FAIL (at least one check failed).
"""

from __future__ import annotations

import itertools
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ta_auction_fetch as ta  # noqa: E402

TA = os.path.join("research", "extensions", "ta")
CONTRACT = os.path.join(TA, "TA_PREREGISTRATION.md")
MANIFEST = os.path.join(TA, "TA_DATA_MANIFEST.md")
S0 = os.path.join(TA, "TA_S0_FRAME.md")
REPAIR = os.path.join(TA, "TA_S0_REPAIR_RECORD.md")
DISCLOSURE = os.path.join(TA, "TA_EXPOSURE_DISCLOSURE.md")
OWNER = os.path.join("ops", "OWNER_DECISION_RECORD_CTA_EDGE_01_TA.md")
BUILDER = os.path.join(TA, "ta_auction_fetch.py")

RAW_SHA = "e807f06647c420f22f7654186e076cf15cebac2a6be7de16d8d1a5fbbcaba552"
CAL_SHA = "b27be5b1d94cfc13fc8310e0d5216675e097a2245fc954e4b12ed282563f7cb6"
PANEL_SHA = "3d2a7a56dbd92d4ff8138cfd894c87f5ac5ac088a11165db870673e0c05c3c31"

M1_NET = 8.0        # bps per event
M1_GROSS = 16.0     # bps per event
M2 = 0.30           # calendarised annualised Sharpe
COST_BPS = 8.0

_results: list[tuple[bool, str, str]] = []


def check(name: str, ok: bool, detail: str = "") -> bool:
    _results.append((bool(ok), name, detail))
    return bool(ok)


def read(path: str) -> str:
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


# --------------------------------------------------------------------------- #
# A. Package presence and seal status                                          #
# --------------------------------------------------------------------------- #


def section_a() -> None:
    for p in (CONTRACT, MANIFEST, S0, REPAIR, DISCLOSURE, OWNER, BUILDER,
              os.path.join(TA, "TA_EVENT_CALENDAR.csv")):
        check(f"A/present {p}", os.path.exists(p))
    c = read(CONTRACT)
    check("A/contract is SEALED", "STATUS                 = SEALED" in c)
    check("A/contract claims no run authorization",
          "RUN_AUTHORIZATION_CREATED = NO" in c)
    check("A/contract: S2 not authorized", "S2_AUTHORIZED          = NO" in c)
    check("A/contract: real run not authorized", "REAL_RUN_AUTHORIZED    = NO" in c)
    check("A/contract declares itself sole design authority",
          "SOLE design authority" in c)
    check("A/repair record names the contract as sole authority",
          "SOLE_DESIGN_AUTHORITY = research/extensions/ta/TA_PREREGISTRATION.md"
          in read(REPAIR))
    check("A/S0 preserved unmodified flag", "S0_ARTIFACT_MODIFIED = NO" in read(REPAIR))


# --------------------------------------------------------------------------- #
# B. Owner decision and the two materiality bars                               #
# --------------------------------------------------------------------------- #


def section_b() -> None:
    o = read(OWNER)
    c = read(CONTRACT)
    check("B/TA-OD-1 recorded", "TA-OD-1" in o)
    check("B/M2 value +0.30 in the Owner record",
          "M2 = +0.30 annualised CALENDARISED Sharpe" in o)
    check("B/M2 owner-confirmed before exposure",
          "BEFORE any candidate outcome was accessed" in o)
    check("B/M2 immutability stated", "must not be\nchanged after exposure" in o)
    check("B/M1 net bar in contract", "mean AC_NET  >=  +8.0 bps per event" in c)
    check("B/M1 gross bar in contract", "mean AC_GROSS >= +16.0 bps" in c)
    check("B/M2 bar in contract",
          "calendarised annualised Sharpe  >=  +0.30" in c)
    check("B/cost constant is 8.0", "COST_BPS                       = 4 x 2 = 8.0 bps" in c)
    check("B/no threshold left as TBD/TODO",
          not re.search(r"\bTBD\b|\bTODO\b|<to be decided>", c))


# --------------------------------------------------------------------------- #
# C. The five mandatory repairs                                                #
# --------------------------------------------------------------------------- #


def section_c() -> None:
    c = read(CONTRACT)
    r = read(REPAIR)

    # R1 - SHY has no kill or damage power anywhere
    check("C/R1 SHY placebo removed", "SHY_HARD_PLACEBO    = REMOVED" in c)
    check("C/R1 SHY final role recorded",
          "SHY_FINAL_ROLE      = MATURITY_GRADIENT_DIAGNOSTIC" in c)
    check("C/R1 SHY kill power NONE", "SHY_KILL_POWER      = NONE" in c)
    check("C/R1 SHY damage power NONE", "SHY_DAMAGE_POWER    = NONE" in c)
    check("C/R1 SHY promotion power NONE", "SHY_PROMOTION_POWER = NONE" in c)
    check("C/R1 no classification rule references SHY",
          "No classification rule in §I references SHY" in c)
    # the §I classification block must not mention SHY at all
    i_start = c.index("## §I Classification")
    i_end = c.index("## §J Multiplicity")
    check("C/R1 section I is SHY-free", "SHY" not in c[i_start:i_end],
          "SHY appears inside the classification section")

    # R2 - self-differencing wording
    check("C/R2 semantic rule present",
          "SELF_DIFFERENCING  =  REDUCES SENSITIVITY TO A LOCALLY STABLE COMMON EXPECTED DRIFT"
          in c)
    check("C/R2 non-removal stated",
          "SELF_DIFFERENCING != EXACT REMOVAL OF NON-AUCTION SHOCKS"
          in c.replace("!=  EXACT", "!= EXACT"))
    check("C/R2 'cancels exactly' is gone from the contract",
          "cancels exactly" not in c)

    # R3 - position path
    check("C/R3 no short-to-long flip claimed",
          "There is NO short-to-long flip." in c)
    for frag in ("flat   ->  SHORT 1 unit", "SHORT  ->  flat",
                 "FLAT                      <-- exposure is ZERO",
                 "flat   ->  LONG 1 unit", "LONG   ->  flat"):
        check(f"C/R3 path mark {frag[:24]!r}", frag in c)
    check("C/R3 four one-way units", "= 4" in c and "4 x 2 = 8.0 bps" in c)
    check("C/R3 behavioural assertion is mandatory at S2",
          "BEHAVIOURAL ASSERTION — exposure is ZERO across the auction-day bar" in c)
    check("C/R3 repair record documents the flip removal",
          "There is NO short-to-long flip." in r)

    # R4 - M2 construction
    check("C/R4 calendarised monthly construction",
          "CALENDARISED_SHARPE = mean(MONTHLY_TA_RETURN) / sd(MONTHLY_TA_RETURN) * sqrt(12)"
          in c)
    check("C/R4 zero months retained", "MONTHLY_TA_RETURN[m] = sum of AC_NET_i" in c
          and "= 0 if no valid primary event falls in month m." in c)
    check("C/R4 ddof fixed", "sd uses ddof = 1." in c)
    check("C/R4 ambiguous sqrt(events per year) removed",
          "sqrt(number of event weeks per year)" not in c
          and "sqrt(events per year)" not in c)
    check("C/R4 no leverage / vol targeting / weight search",
          "NO leverage optimisation · NO volatility targeting · NO capital scaling ·" in c)

    # R5 - taxonomy with class I
    for cls in ("CLASS A -- DIRECTIONAL ETF PATTERN EXCLUDED",
                "CLASS B -- TARGET MARGIN RELIABLY EXCLUDED",
                "CLASS C -- UNRESOLVED / LOW POWER",
                "CLASS D -- SUPPORTED ETF-LEVEL EFFECT",
                "CLASS I -- IDENTIFICATION / DEPENDENCE FAILURE"):
        check(f"C/R5 {cls[:9]}", cls in c)
    check("C/R5 first match wins", "FIRST MATCH WINS" in c)
    check("C/R5 damage cannot upgrade",
          "it can\nnever upgrade A, B, C or I to D" in c)


# --------------------------------------------------------------------------- #
# D. Damage rules are quantitative and fixed                                   #
# --------------------------------------------------------------------------- #


def section_d() -> None:
    c = read(CONTRACT)
    check("D/SPY damage rule is absolute and tied to M1 gross",
          "TRIGGER  iff   L95( mean AC_GROSS of SPY )  >=  +16.0 bps per event" in c)
    check("D/SPY rule takes no TLT input",
          "takes no TLT input" in c)
    check("D/macro-QRA damage rule quantitative",
          "TRIGGER  iff   b0  <  +16.0 bps" in c)
    check("D/macro-QRA NOT_EVALUABLE defined",
          "fewer than 20 events have all four signed covariates = 0" in c)
    check("D/macro-QRA model fixed, no selection",
          "NO interactions. NO alternative windows. NO stepwise selection." in c)
    check("D/LOYO rule quantitative",
          "PASS  iff  LOYO_y > 0 for ALL 21 years." in c)
    check("D/exactly one fragility metric",
          "**Exactly one fragility metric exists.**" in c)
    check("D/one bootstrap family only",
          "NO second bootstrap family. NO parametric Sharpe test. NO HAC stack." in c)
    check("D/seed protocol sealed",
          "numpy.random.SeedSequence(7).spawn(5)[4]" in c)
    check("D/every diagnostic has a declared power",
          "| quantity | role | PROMOTION | DAMAGE | KILL |" in c)


# --------------------------------------------------------------------------- #
# E. The classification function is total, single-valued, and unpromotable     #
# --------------------------------------------------------------------------- #


def classify_result(L_AC, U_AC, L_S, U_S, loyo_ok, spy_dmg, macro_dmg):
    """Reference implementation of contract §I.2. First match wins."""
    L_N, U_N = L_AC - COST_BPS, U_AC - COST_BPS
    if U_AC <= 0:
        return "A"
    if (U_N < M1_NET) or (U_S < M2):
        return "B"
    W = (L_N >= M1_NET) and (L_S >= M2)
    if W:
        if loyo_ok and (not spy_dmg) and (not macro_dmg):
            return "D"
        return "I"
    return "C"


def section_e() -> None:
    grid_ac = [-40.0, -8.0, 0.0, 0.01, 8.0, 16.0, 16.5, 40.0, 120.0]
    grid_s = [-1.0, 0.0, 0.1, 0.2999, 0.30, 0.31, 1.5]
    total = 0
    bad_order = []
    upgrades = []
    classes = set()
    for L_AC, U_AC in itertools.product(grid_ac, repeat=2):
        if L_AC > U_AC:
            continue
        for L_S, U_S in itertools.product(grid_s, repeat=2):
            if L_S > U_S:
                continue
            for loyo, spy, mac in itertools.product((True, False), repeat=3):
                total += 1
                k = classify_result(L_AC, U_AC, L_S, U_S, loyo, spy, mac)
                if k not in "ABCDI":
                    bad_order.append((L_AC, U_AC, L_S, U_S))
                classes.add(k)
                # no diagnostic may upgrade: firing a damage flag must never
                # move a class TOWARDS D
                base = classify_result(L_AC, U_AC, L_S, U_S, True, False, False)
                if k == "D" and base != "D":
                    upgrades.append((L_AC, U_AC, L_S, U_S, loyo, spy, mac))
    check("E/classification is total and single-valued",
          not bad_order, f"{len(bad_order)} undefined cases of {total}")
    check("E/no diagnostic can upgrade a class to D",
          not upgrades, f"{len(upgrades)} illegal upgrades")
    check("E/all five classes are reachable", classes == set("ABCDI"),
          f"reachable = {sorted(classes)}")
    # explicit boundary probes
    check("E/A wins over B when U_AC <= 0",
          classify_result(-40.0, 0.0, -1.0, -1.0, True, False, False) == "A")
    check("E/B on Sharpe upper bound below M2",
          classify_result(20.0, 40.0, 0.0, 0.2999, True, False, False) == "B")
    check("E/D at both lower bounds exactly on the bars",
          classify_result(16.0, 40.0, 0.30, 1.5, True, False, False) == "D")
    check("E/I when LOYO fails on a would-be D",
          classify_result(16.0, 40.0, 0.30, 1.5, False, False, False) == "I")
    check("E/I when SPY damage fires on a would-be D",
          classify_result(16.0, 40.0, 0.30, 1.5, True, True, False) == "I")
    check("E/I when macro damage fires on a would-be D",
          classify_result(16.0, 40.0, 0.30, 1.5, True, False, True) == "I")
    check("E/C when the interval spans a bar",
          classify_result(0.01, 40.0, 0.31, 1.5, True, False, False) == "C")


# --------------------------------------------------------------------------- #
# F. Data identity and the sealed event counts                                 #
# --------------------------------------------------------------------------- #


def section_f() -> None:
    ok_raw = os.path.exists(ta.RAW_PATH)
    check("F/raw extract present", ok_raw, ta.RAW_PATH)
    if not ok_raw:
        return
    check("F/raw sha256 matches the seal", ta.sha256_file(ta.RAW_PATH) == RAW_SHA)
    check("F/event calendar sha256 matches the seal",
          ta.sha256_file(ta.CALENDAR_PATH) == CAL_SHA)
    if os.path.exists(ta.PANEL_PATH):
        check("F/frozen panel sha256 matches the programme pin",
              ta.sha256_file(ta.PANEL_PATH) == PANEL_SHA)
    else:
        check("F/frozen panel present", False, ta.PANEL_PATH)
        return

    raw = ta.load_raw()
    check("F/raw row count 2373", raw["row_count"] == 2373, str(raw["row_count"]))
    check("F/raw retrieval timestamp pinned",
          raw["retrieved_at_utc"] == "2026-09-14T16:55:38Z")
    check("F/raw cutoff is the frozen panel end",
          raw["filter_auction_date_lte"] == "2026-06-12")
    check("F/no auction OUTCOME field was requested",
          not ({"high_yield", "bid_to_cover_ratio", "primary_dealer_accepted",
                "direct_bidder_accepted", "indirect_bidder_accepted",
                "comp_accepted", "price_per100"} & set(raw["fields"])))

    cals = ta.trading_calendar()
    try:
        grid = ta.common_grid(cals)
        check("F/common grid identity holds for TLT, IEF, SHY, SPY", True)
    except AssertionError as exc:
        check("F/common grid identity holds for TLT, IEF, SHY, SPY", False, str(exc))
        return
    check("F/grid is 6007 days", len(grid) == 6007, str(len(grid)))
    check("F/grid endpoints", str(grid[0]) == "2002-07-30" and str(grid[-1]) == "2026-06-12")

    # PRIMARY
    infam = [r for r in raw["data"] if ta.classify(r) == ta.PRIMARY_TENOR]
    ev = ta.family_events(raw, ta.PRIMARY_TENOR, ta.PRIMARY_YEARS)
    check("F/on-cycle rule is a NO-OP on the primary family",
          len(ev) == len(infam) == 245, f"{len(infam)} -> {len(ev)}")
    wins = ta.build_windows(ev, grid)
    valid = sorted((w for w in wins if w["valid_window"] == "YES"),
                   key=lambda w: int(w["t0_index"]))
    check("F/PRIMARY valid windows == 213", len(valid) == 213, str(len(valid)))
    check("F/PRIMARY first t0 2006-02-09", valid[0]["auction_date"] == "2006-02-09")
    check("F/PRIMARY last t0 2026-05-13", valid[-1]["auction_date"] == "2026-05-13")
    years = sorted({w["auction_date"][:4] for w in valid})
    check("F/PRIMARY 21 calendar years", len(years) == 21, str(len(years)))
    gaps = [int(b["t0_index"]) - int(a["t0_index"]) for a, b in zip(valid, valid[1:])]
    check("F/PRIMARY zero overlapping windows",
          min(gaps) > ta.OVERLAP_GAP, f"min gap {min(gaps)}")
    from collections import Counter
    months = Counter(w["calendar_month"] for w in valid)
    check("F/PRIMARY max one event per calendar month",
          max(months.values()) == 1, str(max(months.values())))
    weeks = Counter((w["iso_year"], w["iso_week"]) for w in valid)
    check("F/PRIMARY 213 unique ISO weeks, max 1 per week",
          len(weeks) == 213 and max(weeks.values()) == 1)
    mg = ta.month_grid(valid)
    check("F/PRIMARY month grid 2006-02..2026-05 = 244",
          len(mg) == 244 and mg[0] == "2006-02" and mg[-1] == "2026-05", str(len(mg)))
    check("F/PRIMARY 31 zero months", len(mg) - len(months) == 31,
          str(len(mg) - len(months)))
    check("F/PRIMARY reopening split 73/140",
          Counter(w["reopening"] for w in valid) == Counter({"Yes": 140, "No": 73}))

    # SECONDARY
    infam2 = [r for r in raw["data"] if ta.classify(r) == ta.SECONDARY_TENOR]
    ev2 = ta.family_events(raw, ta.SECONDARY_TENOR, ta.SECONDARY_YEARS)
    check("F/SECONDARY on-cycle rule drops exactly 5",
          len(infam2) == 317 and len(ev2) == 312, f"{len(infam2)} -> {len(ev2)}")
    valid2 = [w for w in ta.build_windows(ev2, grid) if w["valid_window"] == "YES"]
    check("F/SECONDARY valid windows == 258", len(valid2) == 258, str(len(valid2)))
    check("F/SECONDARY 25 calendar years",
          len({w["auction_date"][:4] for w in valid2}) == 25)

    # structural overlap - the fact that forces the reduced-form reading
    prof = ta.overlap_profile(wins, raw, grid, ta.qra_dates(raw))
    n = len(prof)
    with_10y = sum(1 for p in prof.values() if p["counts"].get("10-Year"))
    clean = sum(1 for p in prof.values()
                if sum(v for k, v in p["counts"].items() if k != ta.PRIMARY_TENOR) == 0)
    check("F/every primary window contains a 10-Year auction",
          with_10y == n == 213, f"{with_10y}/{n}")
    check("F/no primary window is free of another auction", clean == 0, str(clean))

    # rebuild reproducibility
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        out = os.path.join(d, "rebuild.csv")
        res = ta.build(out_path=out)
        check("F/event calendar rebuilds to the sealed sha256",
              res["sha256"] == CAL_SHA, res["sha256"])
        check("F/event calendar has 557 rows", res["rows"] == 557, str(res["rows"]))


# --------------------------------------------------------------------------- #
# G. Outcome blindness                                                         #
# --------------------------------------------------------------------------- #

FORBIDDEN_ARTIFACTS = (
    "TA_EVIDENCE.json", "TA_RESULTS.json", "TA_AC.csv", "TA_BOOTSTRAP.csv",
    "TA_SHARPE.json", "TA_RUN_RECORD.md",
)


def section_g() -> None:
    for name in FORBIDDEN_ARTIFACTS:
        check(f"G/no outcome artifact {name}", not os.path.exists(os.path.join(TA, name)))
    check("G/no execution authorization record for this lineage",
          "CTA-EDGE-01-TA" not in read(os.path.join("ops", "EXECUTION_AUTHORIZATIONS.md")))
    src = read(BUILDER)
    # the builder must never compute a return or a statistic
    banned = [r"np\.log", r"math\.log", r"\.pct_change", r"pnl", r"sharpe",
              r"bootstrap", r"\bmean\s*\(", r"returns?\s*="]
    hits = [b for b in banned if re.search(b, src, re.I)]
    check("G/builder module computes no return, P&L or statistic",
          not hits, f"matched {hits}")
    check("G/builder documents the presence-mask-only panel contact",
          "presence mask only" in src and "never retained" in src)
    check("G/contract records outcome blindness", "CANDIDATE_OUTCOME_ACCESSED = NO"
          in read(DISCLOSURE))
    check("G/disclosure records both design contributors",
          "FABLE_DESIGN_EXPOSED = YES" in read(DISCLOSURE)
          and "ASTRA_DESIGN_EXPOSED = YES" in read(DISCLOSURE))


# --------------------------------------------------------------------------- #
# H. Governance records                                                        #
# --------------------------------------------------------------------------- #


def section_h() -> None:
    sr = read(os.path.join("research", "extensions", "SAMPLE_REUSE.md"))
    tl = read(os.path.join("research", "extensions", "TRIAL_LEDGER.md"))
    rx = read(os.path.join("ops", "REVIEWER_EXPOSURE_LOG.md"))
    check("H/SAMPLE_REUSE carries the CTA-EDGE-01-TA KB-1 addendum",
          "KB-1 addendum — `CTA-EDGE-01-TA`" in sr)
    check("H/SAMPLE_REUSE keeps the evidence ceiling at supported",
          "Never `confirmed`, never `independently confirmed`, whatever the result" in sr)
    check("H/TRIAL_LEDGER declares family F-TA", "**`F-TA`**" in tl)
    check("H/TRIAL_LEDGER states m = 1 with no correction",
          "**m = 1; NO multiplicity correction**" in tl)
    check("H/TRIAL_LEDGER asserts no N_trials figure",
          "`N_trials` on the ETF panel is **NOT ASSERTED**" in tl)
    check("H/REVIEWER_EXPOSURE_LOG has rows S31, S32, S33",
          all(f"| S3{i} |" in rx for i in (1, 2, 3)))
    c = read(CONTRACT)
    check("H/D-ETF-COUNT not decided here",
          "D-ETF-COUNT" in c and "UNKNOWN_PENDING_AARON_DECISION" in c
          and "that decision is NOT taken here" in c)


def main() -> int:
    for fn in (section_a, section_b, section_c, section_d,
               section_e, section_f, section_g, section_h):
        try:
            fn()
        except Exception as exc:  # a crashing check is a failing check
            check(f"{fn.__name__} raised", False, f"{type(exc).__name__}: {exc}")
    width = max(len(n) for _, n, _ in _results)
    failed = 0
    for ok, name, detail in _results:
        if not ok:
            failed += 1
            print(f"FAIL  {name:<{width}}  {detail}")
    print(f"\nCTA-EDGE-01-TA S1 VALIDATOR: {len(_results) - failed}/{len(_results)} PASS")
    print("RESULT:", "PASS" if failed == 0 else f"FAIL ({failed} failing)")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
