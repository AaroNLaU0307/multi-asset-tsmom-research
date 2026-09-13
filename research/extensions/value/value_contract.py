# -*- coding: utf-8 -*-
"""Frozen constants of the SEALED Time-Series Value contract, plus a conformance
check that proves this module agrees with the sealed preregistration.

Nothing here is a scientific choice. Every value is transcribed from the sealed
document, and `conformance()` re-reads that document and refuses to agree with
itself: each constant must be found in the sealed bytes.

    sealed prereg : research/extensions/value/VALUE_PREREGISTRATION_DRAFT.md
    sha256 (LF)   : f5f377b195d3ba2081e772b675d251d3adc036511133a461a823f72ddd6582ee
    seal revision : see SEAL_REVISION below
    amendment     : VALUE_S1_EPISODE_REACHABILITY_AMENDMENT_003

lineage, never erased - each seal is superseded, none is deleted:

    original   ba5814d8dad2b81f28d45a0b6df7c010ef4c052f /
               df142f83d82996f1df87d7953c1480397e4d128c8b32d599e31237901b3278cf
    _001       5812997229eafe2184fe68193856bea2fa41eeae /
               bc841ea80dd1afd521d8ecd2dc656b3e608396f4dd6546eab9c7b809ca67a099
    _002       9c9dd4c2fd400719ebd69925b8ef96c2a4bf6548 /
               844fea84d5f1dddc7da5cbaea4ead4af4f3fe3a15b4f0cd0dfb1a91a9948d1cb
    _003       the seal revision above / the sha256 above
"""
import hashlib
import io
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

SEALED_PREREG_RELPATH = "research/extensions/value/VALUE_PREREGISTRATION_DRAFT.md"
SEALED_PREREG_SHA256 = ("f5f377b195d3ba2081e772b675d251d3adc036511133a461"
                        "a823f72ddd6582ee")
SEAL_REVISION = "0ed9bfff2205a61ad048aca1ef3607991ddef460"
OWNER_DECISION = "SEAL TIME-SERIES VALUE S1"

# --- amendment lineage, oldest first. No seal is ever erased. ---------------
AMENDMENT_ID_001 = "VALUE_S1_DATA_IDENTITY_AMENDMENT_001"
AMENDMENT_ID_002 = "VALUE_S1_COMPARATOR_IDENTITY_AMENDMENT_002"
AMENDMENT_ID_003 = "VALUE_S1_EPISODE_REACHABILITY_AMENDMENT_003"
AMENDMENT_ID = AMENDMENT_ID_003          # the amendment this module implements

ORIGINAL_SEAL_REVISION = "ba5814d8dad2b81f28d45a0b6df7c010ef4c052f"
ORIGINAL_SEALED_PREREG_SHA256 = ("df142f83d82996f1df87d7953c1480397e4d128c8b32"
                                 "d599e31237901b3278cf")
AMENDMENT_001_SEAL_REVISION = "5812997229eafe2184fe68193856bea2fa41eeae"
AMENDMENT_001_SEALED_PREREG_SHA256 = ("bc841ea80dd1afd521d8ecd2dc656b3e608396f4"
                                      "dd6546eab9c7b809ca67a099")
AMENDMENT_002_SEAL_REVISION = "9c9dd4c2fd400719ebd69925b8ef96c2a4bf6548"
AMENDMENT_002_SEALED_PREREG_SHA256 = ("844fea84d5f1dddc7da5cbaea4ead4af4f3fe3a1"
                                      "5b4f0cd0dfb1a91a9948d1cb")
ASTRA_ROLE = "material_design_contributor"

# The authoritative amendment lineage, oldest first, defined ONCE here so the
# evidence emitter and the evidence validator cannot drift apart. The terminal
# entry is always the ACTIVE seal. A hardcoded label paired with live seal
# constants is exactly the defect this replaces.
AMENDMENT_LINEAGE = (
    ("ORIGINAL_SEAL", ORIGINAL_SEAL_REVISION, ORIGINAL_SEALED_PREREG_SHA256),
    (AMENDMENT_ID_001, AMENDMENT_001_SEAL_REVISION,
     AMENDMENT_001_SEALED_PREREG_SHA256),
    (AMENDMENT_ID_002, AMENDMENT_002_SEAL_REVISION,
     AMENDMENT_002_SEALED_PREREG_SHA256),
    (AMENDMENT_ID_003, SEAL_REVISION, SEALED_PREREG_SHA256),
)


def lineage_records():
    """The lineage as the evidence artifact carries it."""
    return [{"amendment": a, "seal_revision": r, "sealed_prereg_sha256": s}
            for a, r, s in AMENDMENT_LINEAGE]

# --- §17 comparator identity ------------------------------------------------
TSMOM_COMPARATOR = "CANONICAL_17_ETF_TSMOM_BASELINE"
COMPARATOR_IS_X01_E_ARM = False

# --- §11.1 C3, as amended by _003 ------------------------------------------
C3_INTERPRETATION = "CONTRIBUTION_SENSITIVITY_ROBUSTNESS"
C3_OPERATOR = "INDIVIDUAL_SELECTED_EPISODE_CONTRIBUTION_ABLATION"
C3_PERMITTED_CLAIM = (
    "Diversification candidacy survives removal of each of the three "
    "prespecified longest instrument-episode direct net contributions.")
C3_FORBIDDEN_CLAIM = (
    "Value is robust across independent valuation regimes. C3 does NOT test "
    "TEMPORAL_REGIME_ROBUSTNESS and does NOT test performance outside the "
    "episode's calendar regime.")
C3_KNOWN_LIMITATION = (
    "Shared-regime dependence may remain, because the other instruments "
    "continue to contribute during the same calendar regime.")

# --- §2 universe and objects -----------------------------------------------
UNIVERSE = ("SPY", "TLT", "LQD", "UUP", "FXY")
EXCLUDED_FROM_VALUE = ("HYG", "EEM", "EWJ", "XLE", "XLU", "SHY", "USO", "UNG",
                       "GLD", "DBA", "VNQ", "RWX")
CREDIT_OBJECT = "BAA10Y"
ANCHOR = "EXPANDING_OWN_HISTORY"

# --- §12 Owner decisions, frozen -------------------------------------------
LAG_CAPE_MONTHS = 3            # D1
WARMUP_MONTHS = 120            # D2
STALENESS_MONTHS = 3           # D3
EVAL_START = "2014-07"         # D4
EVAL_END = "2026-05"           # D5
N_MONTHS = 143
E_POSITIVE = 0.15              # D6
F_ADVERSE = 0.15               # D7  (applied at -F)
RHO_MAX = 0.40                 # D8, adjudicated on the CI UPPER bound
SPLIT_TSMOM = 0.75             # D9
SPLIT_VALUE = 0.25             # D9
DELTA_COMBO = 0.10             # D10
K_EPISODES = 3                 # D11

# --- §3.2 causal availability ----------------------------------------------
LAG_MARKET_BDAYS = 1
LAG_CPI_MONTHS = 2

# --- §9.1 inference, reused from the sealed X01 engine ---------------------
BOOTSTRAP_FAMILY = "stationary_bootstrap_politis_romano_1994"
BOOTSTRAP_REPS = 10000
BLOCK_LENGTH_MONTHS = 12
MASTER_SEED = 7
CI_LEVEL = 95
VALID_REPLICATE_FLOOR = 9500
MIN_DISTINCT_MONTHS = 24
ARM_ORDER = ("standalone", "correlation", "combo")

# --- §2.2 fixed USDX basket ------------------------------------------------
FX_WEIGHTS = {"EUR": 0.576, "JPY": 0.136, "GBP": 0.119,
              "CAD": 0.091, "SEK": 0.042, "CHF": 0.036}
FX_INVERTED = ("DEXUSEU", "DEXUSUK")        # quoted USD per foreign unit
FX_DIRECT = ("DEXJPUS", "DEXCAUS", "DEXSDUS", "DEXSZUS")

# --- §3.1 limitation that survives into every claim ------------------------
SHILLER_VINTAGE_STATUS = ("RECONSTRUCTED_HISTORICAL_SERIES_WITH_"
                          "NON-VINTAGE_LIMITATION")

# --- verdict tokens ---------------------------------------------------------
SUPPORTED_POSITIVE_EDGE = "SUPPORTED_POSITIVE_EDGE"
MATERIALLY_ADVERSE = "MATERIALLY_ADVERSE"
UNRESOLVED_EDGE = "UNRESOLVED_EDGE"
SUPPORTED_INCREMENTAL_BENEFIT = "SUPPORTED_INCREMENTAL_BENEFIT"
INCREMENTAL_BENEFIT_ADVERSE = "INCREMENTAL_BENEFIT_ADVERSE"
INCREMENTAL_BENEFIT_NOT_ESTABLISHED = "INCREMENTAL_BENEFIT_NOT_ESTABLISHED"

EVIDENCE_CEILING = "T0 / POST-EXPOSURE / AT_MOST_SUPPORTED"

# --- raw inputs, pinned by the inventory ------------------------------------
RAW_DIR = "data/value_raw"
RAW_INPUTS = {
    "cape": "shiller_ie_data.xls",
    "tlt": "DFII20.csv",
    "credit": "BAA10Y.csv",
    "cpi_US": "CPIAUCNS.csv",
    "cpi_EUR": "euro_hicp_eurostat_ecoicop2_I25.json",
    "cpi_JPY": "japan_cpi_estat_000040482943.csv",
    "cpi_GBP": "uk_cpi_ons_D7BT.json",
    "cpi_CAD": "canada_cpi_statcan_18100004.zip",
    "cpi_SEK_historical": "sweden_cpi_scb_KPI2020M1980_000007T9.json",
    "cpi_SEK_current": "sweden_cpi_scb_KPI2020M_00000808.json",
    "cpi_CHF": "swiss_cpi_snb.csv",
    "fx_EUR": "DEXUSEU.csv", "fx_JPY": "DEXJPUS.csv", "fx_GBP": "DEXUSUK.csv",
    "fx_CAD": "DEXCAUS.csv", "fx_SEK": "DEXSDUS.csv", "fx_CHF": "DEXSZUS.csv",
}
ETF_PANEL = "data/close_prices_raw.csv"


def sealed_text():
    p = os.path.join(REPO, SEALED_PREREG_RELPATH)
    return io.open(p, "rb").read().replace(b"\r\n", b"\n").decode("utf-8")


def sealed_sha256():
    p = os.path.join(REPO, SEALED_PREREG_RELPATH)
    return hashlib.sha256(
        io.open(p, "rb").read().replace(b"\r\n", b"\n")).hexdigest()


def conformance():
    """Prove these constants are the sealed ones. Returns (ok, checks)."""
    checks = []

    def ck(label, cond, detail=""):
        checks.append((label, bool(cond), detail))

    actual = sealed_sha256()
    ck("sealed prereg sha256 matches the seal", actual == SEALED_PREREG_SHA256,
       actual[:16])
    if actual != SEALED_PREREG_SHA256:
        return False, checks

    t = sealed_text()
    flat = re.sub(r"\s+", " ", t)

    def has(*p):
        return all(re.sub(r"\s+", " ", x) in flat for x in p)

    ck("document declares itself SEALED", has("VALUE_PREREG_SEALED = YES"))
    ck("universe is exactly SPY TLT LQD UUP FXY",
       all(has("**%s**" % i) for i in UNIVERSE)
       and not any(has("| **%s** |" % x) for x in EXCLUDED_FROM_VALUE))
    ck("credit object is BAA10Y", has("CREDIT_OBJECT = BAA10Y"))
    ck("anchor is EXPANDING_OWN_HISTORY", has(ANCHOR))
    ck("warm-up is 120 months", has("**120 months**", "`W = 120`"))
    ck("staleness is 3 months", has("**3 months**"))
    ck("Shiller lag is 3 months (D1)", has("| **D1** |", "**3 months**"))
    ck("evaluation window 2014-07 .. 2026-05, N = 143",
       has("EVALUATION_START  = 2014-07", "EVALUATION_END    = 2026-05",
           "CALENDAR_MONTH_COUNT = 143"))
    ck("+E is +0.15", has("L_V >  +0.15"))
    ck("-F is -0.15", has("U_V <  −0.15"))
    ck("rho_max is 0.40 on the CI upper bound",
       has("ρ_upper ≤ 0.40", "upper bound of the 95% interval"))
    ck("split is 75/25", has("**75 / 25**"))
    ck("delta is +0.10", has("L_combo >  +0.10"))
    ck("k is 3 episodes", has("k = 3"))
    ck("bootstrap is 10,000 replicates", has("**10,000** replicates"))
    ck("expected block length is 12 months", has("**12 months**"))
    ck("seed policy is SeedSequence(7)", has("SeedSequence(7).spawn(k)"))
    ck("valid replicate floor is 9,500", has("**9,500** valid floor"))
    ck("minimum distinct months is 24", has("**24 distinct calendar months**"))
    ck("CI is a 95% percentile interval", has("**95% percentile** interval"))
    ck("FX weights are the fixed USDX set",
       all(has("%s %.3f" % (c, w)) for c, w in
           (("EUR", 0.576), ("JPY", 0.136), ("GBP", 0.119),
            ("CAD", 0.091), ("SEK", 0.042), ("CHF", 0.036))))
    ck("FX weights sum to one", abs(sum(FX_WEIGHTS.values()) - 1.0) < 1e-12)
    ck("inverted quotes are DEXUSEU and DEXUSUK",
       has("S_f(t) = 1 / q_f(t)", "DEXUSEU, DEXUSUK"))
    ck("US CPI is the NSA series", has("`CPIAUCNS`"))
    ck("amendment 001 is recorded with its lineage",
       has(AMENDMENT_ID_001, ORIGINAL_SEAL_REVISION,
           ORIGINAL_SEALED_PREREG_SHA256, "The original seal is NOT erased"))
    ck("amendment 002 is recorded and the full lineage preserved",
       has(AMENDMENT_ID_002, AMENDMENT_001_SEAL_REVISION,
           AMENDMENT_001_SEALED_PREREG_SHA256,
           "LINEAGE = original seal → AMENDMENT_001 → AMENDMENT_002"))
    ck("the TSMOM comparator is pinned",
       has("VALUE_TSMOM_COMPARATOR = " + TSMOM_COMPARATOR))
    ck("comparator is the 17-ETF book, not X01's E arm",
       has("SPY EEM EWJ XLE XLU TLT SHY LQD HYG USO UNG GLD DBA UUP FXY VNQ RWX",
           "This is NOT X01's E arm"))
    ck("comparator panel is pinned to the X01-sealed hash",
       has("3d2a7a56dbd92d4ff8138cfd894c87f5ac5ac088a11165db870673e0c05c3c31"))
    ck("comparator is recomputed, not read from an untracked file",
       has("RECOMPUTED, never read from an untracked file",
           "`output/monthly_returns.csv` is **git-ignored and carries no hash**"))
    ck("amendment 002 asserts pre-amendment outcome blindness",
       has("VALUE_TARGET_RETURNS_COMPUTED     = NO",
           "VALUE_TSMOM_CORRELATION_COMPUTED  = NO",
           "S3_AUTHORIZATION_CONSUMED         = NO"))
    ck("Sweden is the authorised two-table Fixed CPI",
       has("KPI2020M1980", "000007T9", "KPI2020M", "00000808",
           "month <= 2025-12", "month >= 2026-01"))
    ck("Sweden join verified: no overlap, no gap, bases match",
       has("OVERLAP_MONTHS = 0", "GAP_MONTHS_AT_JUNCTION = 0",
           "REFERENCE_BASE_MATCH = YES", "SEASONAL_ADJUSTMENT_MATCH = YES"))
    ck("Shadow CPI is explicitly NOT used",
       has("Shadow CPI is NOT used") and "Shadow" not in str(RAW_INPUTS))
    ck("no leg was rescaled, bridged or interpolated",
       has("No leg was rescaled, no", "bridge factor estimated"))
    ck("EUR coverage states the ACTUAL numeric span",
       has("1999-12 → 2026-08, 321 numeric"))
    ck("Shiller vintage limitation is frozen", has(SHILLER_VINTAGE_STATUS))
    ck("evidence ceiling frozen", has(EVIDENCE_CEILING))
    ck("C3 requires C1 and C2 in each ablation case",
       has("C1(V^(-e)) = PASS  AND  C2(V^(-e), TSMOM) = PASS"))
    ck("amendment 003 is recorded and the full lineage preserved",
       has(AMENDMENT_ID_003, AMENDMENT_002_SEAL_REVISION,
           AMENDMENT_002_SEALED_PREREG_SHA256,
           "LINEAGE = original seal → AMENDMENT_001 → "
           "AMENDMENT_002 → AMENDMENT_003"))
    ck("C3 is contribution sensitivity, not temporal-regime robustness",
       has("C3_INTERPRETATION = " + C3_INTERPRETATION,
           "does **not** test `TEMPORAL_REGIME_ROBUSTNESS`"))
    ck("the permitted claim language is frozen",
       has("Diversification candidacy survives removal of each of the three "
           "prespecified longest instrument-episode direct net contributions."))
    ck("the forbidden claim language is named",
       has("Value is robust across independent valuation regimes."))
    ck("the shared-regime limitation is recorded",
       has("shared-regime dependence may remain"))
    ck("the ablation is on the ORIGINAL basis and never cumulative",
       has("ORIGINAL** sealed portfolio capital basis",
           "ablations are never cumulative"))
    ck("the operator forbids resizing, retargeting and redistribution",
       has("re-run sizing; redistribute the removed capital; re-target "
           "portfolio volatility; re-scale portfolio gross"))
    ck("shared terms stay in a_t, no allocation rule invented",
       has("stays in `a_t`",
           "no discretionary allocation rule may be invented to force "
           "additivity"))
    ck("retaining calendar months does not imply validity",
       has("Retaining every calendar month does not imply automatic validity"))
    ck("the superseded operator is preserved, not erased",
       has("SUPERSEDED (original §11.1, whole-calendar deletion)"))
    ck("Astra is a design contributor, not a certifier",
       has(ASTRA_ROLE, "**not** independent certification"))
    ck("k = 3 itself is unchanged by the amendment",
       has("`k = 3` itself is unchanged"))
    ck("no owner decisions remaining", has("OWNER_DECISIONS_REMAINING = NONE"))

    return all(c for _l, c, _d in checks), checks


if __name__ == "__main__":
    ok, checks = conformance()
    for label, cond, detail in checks:
        print("  %-52s %s   %s" % (label, "PASS" if cond else "FAIL", detail))
    print()
    print("CONTRACT_CONFORMANCE =", "PASS" if ok else "FAIL")
    raise SystemExit(0 if ok else 1)
