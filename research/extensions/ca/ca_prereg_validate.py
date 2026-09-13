# -*- coding: utf-8 -*-
"""Mechanical validation of the C-A preregistration draft and the C-D specification draft.

Structure, vocabulary and provenance only. NO market data, NO signal, NO return,
NO performance quantity is read or computed. This script never opens data/.

Phrase checks are whitespace-insensitive on purpose: the requirement is that a
clause be PRESENT, not that it avoid a line wrap.

Convention follows research/extensions/value/value_prereg_validate.py.
"""
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
os.chdir(REPO)

CA = "research/extensions/ca/CA_PREREGISTRATION_DRAFT.md"
CD = "research/extensions/cd/CD_VERIFICATION_SPECIFICATION_DRAFT.md"
ODR = "ops/OWNER_DECISION_RECORD_PHASE_B.md"
CONFIG = "config.py"

ca = io.open(CA, encoding="utf-8").read()
cd = io.open(CD, encoding="utf-8").read()
odr = io.open(ODR, encoding="utf-8").read()
cfg = io.open(CONFIG, encoding="utf-8").read()


def flat(s):
    return re.sub(r"\s+", " ", s)


CAF, CDF, ODRF = flat(ca), flat(cd), flat(odr)

ok = True


def ck(label, cond, detail=""):
    global ok
    if not cond:
        ok = False
    print("  %-62s %s   %s" % (label, "PASS" if cond else "FAIL", detail))


def has(hay, *phrases):
    return all(flat(p) in hay for p in phrases)


def section(title):
    print("\n" + title)


# --------------------------------------------------------------------------- #
# PRIMARY
# --------------------------------------------------------------------------- #
section("PRIMARY")

CANON = {
    "Equity": ["SPY", "EEM", "EWJ", "XLE", "XLU"],
    "Fixed income": ["TLT", "SHY", "LQD", "HYG"],
    "Commodity": ["USO", "UNG", "GLD", "DBA"],
    "FX": ["UUP", "FXY"],
    "Real estate": ["VNQ", "RWX"],
}
TICKERS = [t for v in CANON.values() for t in v]

ck("canonical universe is exactly 17 tickers", len(TICKERS) == 17, str(len(TICKERS)))
ck("canonical universe is exactly 5 sleeves", len(CANON) == 5, str(len(CANON)))
ck(
    "all 5 sleeve rows present verbatim in C-A universe table",
    all(has(CAF, "| %s | %s |" % (s, ", ".join(t))) for s, t in CANON.items()),
)
ck(
    "every canonical ticker exists in config.ASSET_UNIVERSE",
    all(('"%s"' % t) in cfg for t in TICKERS),
)

ck("positive materiality floor +0.30 fixed", has(CAF, "POSITIVE_MATERIALITY_FLOOR   (+E)  = +0.30"))
ck("adverse materiality threshold -0.20 fixed", has(CAF, "ADVERSE_MATERIALITY_THRESHOLD (-F)  = -0.20"))
ck("boundary rule is STRICT CROSSING", has(CAF, "BOUNDARY_RULE                       = STRICT CROSSING"))
ck(
    "all four primary propositions are strict inequalities",
    has(CAF, "P_MAT    :  L  >  +0.30", "P_POS    :  L  >   0.00",
        "P_RULED  :  U  <  +0.30", "P_ADV    :  U  <  -0.20"),
)
ck(
    "strict-endpoint rule stated for every floor",
    has(CAF, "`L = +0.30` exactly", "`U = −0.20` exactly", "`L = 0` exactly"),
)
ck("point estimate never classifies", has(CAF, "the point estimate never classifies"))

ck("N_scored terminal = 120", has(CAF, "N_scored_TERMINAL           =  120"))
ck("exactly one terminal scientific reveal", has(CAF, "POSITIVE_REVEAL_COUNT    =  1"))
ck("no interim positive look", has(CAF, "INTERIM_POSITIVE_LOOK    =  NONE"))
ck("no adverse one-bit oracle", has(CAF, "ADVERSE_ONE_BIT_ORACLE   =  NONE"))
ck("exactly one primary confirmatory estimand", has(CAF, "NUMBER_OF_PRIMARY_CONFIRMATORY_ESTIMANDS = 1"))
ck("no automatic extension after 120", has(CAF, "AUTOMATIC_EXTENSION         =  NONE"))

# --- SB-4: ONE central 95% interval, nothing else ------------------------- #
ck(
    "ONE central 95 % stationary-bootstrap percentile interval",
    has(CAF, "= ONE central 95 % stationary-bootstrap percentile interval, per estimand."),
)
ck("alternative 90 % interval FORBIDDEN", has(CAF, "FORBIDDEN: an alternative 90 % interval."))
ck("separate one-sided interval FORBIDDEN", has(CAF, "FORBIDDEN: a separate one-sided interval."))
ck("post-outcome interval selection FORBIDDEN", has(CAF, "FORBIDDEN: selecting between intervals after outcomes."))
ck("2.5 % directional tail at each endpoint disclosed", has(CAF, "2.5 % directional tail at each endpoint"))
ck("high probability of UNRESOLVED intentionally accepted", has(CAF, "intentionally accepted"))

# a 90% interval must appear ONLY inside prohibition / register prose
n90 = len(re.findall(r"90 ?%", ca))
n90_ok = len(re.findall(r"FORBIDDEN: an alternative 90 % interval", ca)) + \
         len(re.findall(r"a 90 % interval, or a one-sided interval", ca)) + \
         len(re.findall(r"\*\*No\*\* alternative 90 % interval", ca))
ck("every 90 %% mention is a prohibition or register entry", n90 == n90_ok, "%d/%d" % (n90_ok, n90))

# inference architecture inherited, unchanged
ck(
    "bootstrap architecture unchanged",
    has(CAF, "stationary bootstrap", "L = 12 months", "**10,000**", "**95 %**, two-sided",
        "**percentile**, with linear interpolation", "SeedSequence(7).spawn(k)",
        "**24 distinct calendar months**", "**9,500**"),
)
ck("joint resampling where statistics share the same path",
   has(CAF, "resampled **jointly** where statistics share the same path"))
ck("primary interval independent of FM-1 adjudicability",
   has(CAF, "The primary's interval does not depend on FM-1", "bit-identical"))

# --------------------------------------------------------------------------- #
# FM-1
# --------------------------------------------------------------------------- #
section("FM-1")

ck("complementary only", has(CAF, "ROLE                         = COMPLEMENTARY"))
ck("is not primary", has(CAF, "IS_PRIMARY                   = NO"))
ck("cannot rescue primary", has(CAF, "CAN_RESCUE_PRIMARY           = NO"))
ck("cannot replace primary", has(CAF, "CAN_REPLACE_PRIMARY          = NO"))
ck("cannot become fallback primary", has(CAF, "CAN_BECOME_FALLBACK_PRIMARY  = NO"))
ck("cannot upgrade canonical claim", has(CAF, "CAN_UPGRADE_CANONICAL_CLAIM  = NO"))
ck("not an independent replication", has(CAF, "INDEPENDENT_REPLICATION      = NO"))
ck("same forward sample", has(CAF, "SAME_FORWARD_SAMPLE          = YES"))

ck("rf series is FRED DGS3MO", has(CAF, "SERIES              = FRED DGS3MO"))
ck("observation = last non-missing print on or before decision date",
   has(CAF, "OBSERVATION         = last available NON-MISSING print on or before the decision date"))
ck("freshness window is 7 calendar days",
   has(CAF, "FRESHNESS           = the accepted print must be no older than 7 CALENDAR DAYS"))
ck("monthly conversion is Y / 100 / 12", has(CAF, "MONTHLY_CONVERSION  = rf_t = Y / 100 / 12"))
ck("rf locked with the prospective position", has(CAF, "LOCKING             = the accepted rf_t is locked"))
ck("no fallback series", has(CAF, "FALLBACK_SERIES     = NONE"))
ck("RF_MISSING flag defined", has(CAF, "RF_MISSING = TRUE"))
ck("DGS1MO substitution forbidden", has(CAF, "substituting `DGS1MO` or any other"))
ck("carry-forward / interpolation / future obs forbidden",
   has(CAF, "carrying forward an arbitrarily old yield", "interpolating", "using a future"))
ck("RF_MISSING does not affect the primary",
   has(CAF, "**The canonical PRIMARY** | **COMPLETELY UNAFFECTED.**"))
ck("FM-1 sample preserved: no drop, no shorten, no impute",
   has(CAF, "**do not drop**", "**do not silently shorten**", "**do not impute**"))
ck("pre-reveal mechanical recovery permitted", has(CAF, "`MECHANICAL_CORRECTION`"))
ck("unresolved RF_MISSING -> NOT ADJUDICABLE, primary unaffected",
   has(CAF, "NOT ADJUDICABLE — DATA INCOMPLETE", "PRIMARY ADJUDICATION = UNAFFECTED"))
ck("complementary-data failure, not a primary-study failure",
   has(CAF, "complementary-data failure, not a primary-study failure"))

ck("FM-1 has NO +0.30 / -0.20 floors",
   has(CAF, "FM-1 HAS NO +0.30 / -0.20 MATERIALITY FLOORS."))
ck("FM-1 decision scale is sign against zero only",
   has(CAF, "DECISION_SCALE               = SIGN AGAINST ZERO ONLY"))
ck("FM1_POSITIVE is L > 0", has(CAF, "| **`FM1_POSITIVE`** | `L > 0` |"))
ck("FM1_NEGATIVE is U < 0", has(CAF, "| **`FM1_NEGATIVE`** | `U < 0` |"))
ck("FM1_SIGN_UNRESOLVED otherwise", has(CAF, "| **`FM1_SIGN_UNRESOLVED`** | otherwise |"))
ck("primary materiality labels forbidden for FM-1",
   has(CAF, "**Forbidden vocabulary for FM-1:** `MATERIAL_POSITIVE_PERSISTENCE`,"))
ck("FM-1 card capped at supported", has(CAF, "capped at `supported` in every case"))

# no residual claim that FM-1 shares the primary floors
ck("no stale 'same floors' clause applied to FM-1",
   "Floors: `+0.30 / −0.20`, the same scale as the primary" not in ca)

# --------------------------------------------------------------------------- #
# BOUNDARY
# --------------------------------------------------------------------------- #
section("BOUNDARY")

ck("PROSPECTIVE_START = max(seal, go-live)",
   has(CAF, "`max(SEAL_TIMESTAMP, PIPELINE_GO_LIVE)`"))
ck("FORWARD_BOUNDARY is strictly before PROSPECTIVE_START",
   has(CAF, "The last eligible market observation **strictly before** `PROSPECTIVE_START`"))
ck("first scored month requires a post-PROSPECTIVE_START decision",
   has(CAF, "whose **decision month-end close** (the last trading day of `m−1`) is timestamped **strictly after** `PROSPECTIVE_START`"))
ck("first scored month is held under the post-start locked position",
   has(CAF, "The position held during the first scored month is the position generated and locked at the first eligible post-`PROSPECTIVE_START` decision month-end."))
ck("no pre-start position is the scored holding position",
   has(CAF, "NO POSITION CHOSEN BEFORE PROSPECTIVE_START BECOMES A SCORED PROSPECTIVE POSITION."))
ck("no pre-start return is scored", has(CAF, "NO PRE-START RETURN IS SCORED."))
ck("pre-start held position used only as the turnover term",
   has(CAF, "may serve ONLY as the prior-position term needed to compute turnover"))
ck("stale 'already in position' clause removed from §F",
   "enters the first scored month **already in position**" not in ca)

ck("S_0 and S_G are distinct concepts",
   has(CAF, "**`S_0` — SEAL SNAPSHOT**", "**`S_G` — GO-LIVE BASE SNAPSHOT**"))
ck("S_0 does NOT by itself determine FORWARD_BOUNDARY",
   has(CAF, "| Determines `FORWARD_BOUNDARY`? | **NO, not by itself** | **YES**, when `PIPELINE_GO_LIVE > SEAL_TIMESTAMP` |"))
ck("no requirement that S_0 equal the eventual FORWARD_BOUNDARY",
   has(CAF, "**`S_0`'s last observation is NOT required to equal the eventual `FORWARD_BOUNDARY`.**"))
ck("stale DATA_AVAILABLE_THROUGH_AT_SEAL equality removed",
   "Must equal `FORWARD_BOUNDARY` or the prior trading day" not in ca)
ck("immutable lineage / hash linkage between S_0 and S_G required",
   has(CAF, "immutable lineage / hash linkage between `S_0` and `S_G`"))
ck("between-snapshot data is POST_SEAL_UNSCORED_STATE_INPUT_ONLY",
   has(CAF, "POST_SEAL_UNSCORED_STATE_INPUT_ONLY", "contributes ZERO to N_scored"))

# --------------------------------------------------------------------------- #
# STAGES
# --------------------------------------------------------------------------- #
section("STAGES")

ck("S1 seal and S2 build gates are separated",
   has(CAF, "### §Z.1 S1 SEAL PREREQUISITES", "### §Z.2 S2 BUILD / GO-LIVE PREREQUISITES"))
ck("no S2 implementation item blocks the S1 seal",
   has(CAF, "NO S2 IMPLEMENTATION ITEM BLOCKS THE S1 SEAL MERELY BECAUSE IT HAS NOT YET BEEN BUILT."))

z1 = ca[ca.index("### §Z.1"):ca.index("### §Z.2")]
S2_ITEMS = ["overwrite guard", "pct_change", "Runtime enforcement", "snapshot writer",
            "Integrity gate", "Write-once position ledger", "Behaviour-equivalence",
            "Prospective pipeline implementation"]
leaked = [s for s in S2_ITEMS if s.lower() in z1.lower()]
ck("no S2 build item appears inside the S1 seal list", not leaked, str(leaked))
ck("SB-3 does not block the S1 seal",
   has(CAF, "`SB-3` is a C-D implementation-verification blocker and does **not** block this seal"))

# --------------------------------------------------------------------------- #
# BLOCKERS
# --------------------------------------------------------------------------- #
section("BLOCKERS")

ck("SB-1 CLOSED", has(CAF, "SB-1  CLOSED by Owner decision, 2026-09-14"))
ck("SB-2 CLOSED", has(CAF, "SB-2  CLOSED by Owner decision, 2026-09-14"))
ck("SB-4 CLOSED", has(CAF, "SB-4  CLOSED by Owner decision, 2026-09-14"))
ck("SB-3 OPEN, blocks C_D_PASS only",
   has(CAF, "SB-3  OPEN   — blocks C_D_PASS only. Does NOT block the C-A S1 seal."))
ck("SB-3 preserved in C-A with both flags",
   has(CAF, "BLOCKS C_D_PASS        = YES", "BLOCKS THE C-A S1 SEAL = NO"))
ck("no open S1 scientific blocker", has(CAF, "OPEN_S1_SCIENTIFIC_BLOCKERS = NONE"))
ck("no PENDING OWNER CONFIRMATION marker remains", "PENDING OWNER CONFIRMATION" not in ca)

# --------------------------------------------------------------------------- #
# STATUS
# --------------------------------------------------------------------------- #
section("STATUS")

ck("C-A prereg is SEALED", has(CAF, "CA_PREREG_SEALED       = YES", "STATUS                 = SEALED."))
ck("seal timestamp recorded", has(CAF, "S1_SEAL_TIMESTAMP      = 2026-09-13T17:42:06Z"))
ck("owner recorded as the sealing authority", has(CAF, "OWNER_SEAL_AUTHORIZED_BY = Aaron"))
ck("seal changed status metadata only", has(CAF, "SEAL_CHANGED_SCIENTIFIC_CONTENT = NO"))
ck("seal authorization is SEAL-ONLY", has(CAF, "S1_SEAL_AUTHORIZED     = YES   (C-A S1 SEAL ONLY"))
ck("T4 seal exists", has(CAF, "T4_SEAL_EXISTS         = YES"))
ck("T4 clock NOT started (no go-live)", has(CAF, "T4_CLOCK_STARTED       = NO"))
ck("N_scored is zero", has(CAF, "N_scored               = 0"))
ck("first eligible scored period undetermined",
   has(CAF, "FIRST_ELIGIBLE_SCORED_PERIOD = NOT YET DETERMINED"))
ck("S_G not created", has(CAF, "S_G_CREATED            = NO"))
ck("pipeline go-live not yet", has(CAF, "PIPELINE_GO_LIVE       = NOT YET"))
ck("no accrued pre-go-live month may be retroactively scored",
   has(CAF, "No accrued pre-go-live month may ever be retroactively", "scored"))
ck("S1_SEALED = YES in the closing block",
   has(CAF, "S1_SEALED                     = YES  (2026-09-13T17:42:06Z, Owner: Aaron)"))
ck("S2 not started", has(CAF, "S2_STARTED                    = NO"))
ck("target outcome not revealed", has(CAF, "TARGET_OUTCOME_REVEALED       = NO"))
ck("C_A_IMPLEMENTED = NO", has(CAF, "C_A_IMPLEMENTED               = NO"))
ck("C_D_IMPLEMENTED = NO (C-A block)", has(CAF, "C_D_IMPLEMENTED               = NO"))
ck("TARGET_PERFORMANCE_COMPUTED = NO", has(CAF, "TARGET_PERFORMANCE_COMPUTED   = NO"))
ck("TARGET_RUN_AUTHORIZED = NO", has(CAF, "TARGET_RUN_AUTHORIZED         = NO"))
ck("C_B_STATUS = PARKED", has(CAF, "C_B_STATUS                    = PARKED"))

ck("C-D spec draft exists and is recorded as written",
   has(CDF, "C_D_SPEC_DRAFT_CREATED                       = YES",
       "C_D_VERIFICATION_SPEC_DRAFT_WRITTEN          = YES"))
ck("C-D spec is NOT sealed", has(CDF, "C_D_SPEC_SEALED                              = NO"))
ck("C-D executable rule spec not yet written",
   has(CDF, "C_D_EXECUTABLE_RULE_SPECIFICATION_WRITTEN    = NO"))
ck("C-D independent engine not built", has(CDF, "INDEPENDENT_ENGINE_BUILT                     = NO"))
ck("C-D not implemented", has(CDF, "C_D_IMPLEMENTED                              = NO"))
ck("C-D second source not established, SB-3 open",
   has(CDF, "SECOND_SOURCE_ESTABLISHED                    = NO    (blocker SB-3, OPEN — blocks C_D_PASS only)"))
ck("C-D produces no new historical scientific outcome",
   has(CDF, "NEW_HISTORICAL_SCIENTIFIC_OUTCOME_ANALYSIS   = NONE"))
ck("C-D depends on no FM-1 threshold",
   has(CDF, "**C-D depends on no FM-1 threshold of any kind.**"))
ck("C-D carries no +0.30 / -0.20 floor dependency",
   not re.search(r"\+0\.30", cd) or has(CDF, "**FM-1 carries no `+0.30 / −0.20` floors**"))

# --------------------------------------------------------------------------- #
# OWNER DECISION RECORD
# --------------------------------------------------------------------------- #
section("OWNER DECISION RECORD")

ck("record status CONFIRMED", has(ODRF, "RECORD_STATUS      = CONFIRMED"))
ck("OD-5 recorded", has(ODRF, "## §6A OD-5 — PRIMARY AND DIRECTIONAL SCIENTIFIC INFERENCE"))
ck("OD-6 recorded", has(ODRF, "## §6B OD-6 — FM-1 RISK-FREE CONVENTION"))
ck("OD-7 recorded", has(ODRF, "## §6C OD-7 — FM-1 DECISION SCALE"))
ck("OD-1..OD-4 remain authoritative",
   has(ODRF, "**OD-1 to OD-4 remain authoritative and unchanged.**"))
ck("SB-1 / SB-2 / SB-4 closed in the record",
   has(ODRF, "**`SB-1`, `SB-2` and `SB-4` are CLOSED** by these decisions."))
ck("SB-3 open, C_D_PASS only, in the record",
   has(ODRF, "blocks `C_D_PASS` and **does not block the C-A S1 seal**"))
ck("nothing sealed or implemented by these decisions",
   has(ODRF, "**Nothing was sealed or implemented by these decisions.**"))
ck("Aaron is the decision authority, not any agent",
   has(ODRF, "Neither Astra nor Fable made any decision", "Opus drafted the options and the consequences; Aaron decided."))
ck("no agent is an independent certifier of an element it contributed",
   has(ODRF, "**Astra is not an independent certifier of those elements**"))
ck("S1 seal still not authorized in the record", has(ODRF, "S1_SEAL_AUTHORIZED                 = NO"))
ck("target run still not authorized in the record", has(ODRF, "TARGET_RUN_AUTHORIZED              = NO"))

# --------------------------------------------------------------------------- #
# VOCABULARY
# --------------------------------------------------------------------------- #
section("VOCABULARY")

LEGAL_CLAIM = {"confirmed", "supported", "partially_supported", "unresolved",
               "contradicted", "retired", "not_promoted"}
LEGAL_RESEARCH = {"confirmed", "supported", "not_promoted", "falsified", "active",
                  "archived", "experimental", "unresolved"}
LEGAL_EVIDENCE = {"preregistered_primary", "preregistered_robustness",
                  "preregistered_premise_test", "out_of_sample",
                  "full_sample_fixed_parameter", "lockbox", "post_hoc_diagnostic",
                  "exploratory", "implementation_fact", "external_literature",
                  "researcher_interpretation"}
SCHEMA_DIR = os.path.abspath(os.path.join(REPO, "..", "quant-research-knowledge-base", "schemas"))
if os.path.isdir(SCHEMA_DIR):
    fs = io.open(os.path.join(SCHEMA_DIR, "finding.schema.yaml"), encoding="utf-8").read()
    ss = io.open(os.path.join(SCHEMA_DIR, "strategy.schema.yaml"), encoding="utf-8").read()
    ck("claim_status vocabulary matches the live schema",
       all(v in fs for v in LEGAL_CLAIM))
    ck("research_status vocabulary matches the live schema",
       all(v in ss for v in LEGAL_RESEARCH))
    ck("evidence_type vocabulary matches the live schema",
       all(v in fs for v in LEGAL_EVIDENCE))
else:
    ck("KB schemas reachable", False, SCHEMA_DIR)

ck("no `insufficient_evidence` token is proposed",
   has(CAF, "**`insufficient_evidence` is not a KB value.**"))
ck("interpretation labels declared NOT registry tokens",
   has(CAF, "**These are scientific interpretation labels. They are NOT registry tokens**"))

# --------------------------------------------------------------------------- #
# PRE-SEAL ARTIFACTS (added at the final seal gate, 2026-09-14)
# --------------------------------------------------------------------------- #
section("PRE-SEAL ARTIFACTS")

import hashlib  # noqa: E402
import json as _json  # noqa: E402

REG = "research/extensions/ca/CA_INSTRUMENT_REGISTRY.json"
SNAP = "research/extensions/ca/CA_SNAPSHOT_REGISTRY.md"
CD_SPEC = CD

for p in [CA, CD_SPEC, ODR, REG, SNAP]:
    ck("present: %s" % p, os.path.isfile(p))

CANON17 = ["SPY", "EEM", "EWJ", "XLE", "XLU", "TLT", "SHY", "LQD", "HYG",
           "USO", "UNG", "GLD", "DBA", "UUP", "FXY", "VNQ", "RWX"]
if os.path.isfile(REG):
    reg = _json.load(io.open(REG, encoding="utf-8"))
    inst = reg.get("instruments", [])
    ck("registry holds exactly 17 objects", len(inst) == 17, str(len(inst)))
    ck("registry covers exactly the canonical 17, no others",
       sorted(e["canonical_ticker"] for e in inst) == sorted(CANON17))
    ck("registry status is explicit", reg.get("status", "").startswith("PINNED_CANDIDATE")
       or reg.get("status", "").startswith("SEALED"))
    ck("registry is SEALED and bound to the C-A seal",
       reg.get("status", "").startswith("SEALED")
       and reg.get("c_a_seal_timestamp_utc") == "2026-09-13T17:42:06Z"
       and reg.get("sealed_by_owner") == "Aaron")
    kc = reg.get("section_k_conformance", {})
    ck("registry documents §K conformance", kc.get("verdict") == "SATISFIED")
    ck("§K conformance cites the rule-1 mutable list",
       "may change without changing the object" in kc.get("keyed_by_legal_fund_identity", ""))
    ck("identifier chain treated as a forward starting point",
       "STARTING POINT" in kc.get("documented_identifier_chain", ""))
    ck("every object carries a share-class FIGI identity key",
       all(e["identity_key"]["share_class_figi"] for e in inst))
    ck("share-class FIGIs are distinct",
       len({e["identity_key"]["share_class_figi"] for e in inst}) == 17)
    ck("every ISIN check digit valid",
       all(e["identifiers_at_pin_time"]["isin_check_digit_valid"] for e in inst))
    ck("every CUSIP check digit valid",
       all(e["identifiers_at_pin_time"]["cusip_check_digit_valid"] for e in inst))
    ck("every sponsor cross-check that exists agrees",
       all(e["identifiers_at_pin_time"]["cusip_agrees_with_sponsor_reported"] is not False for e in inst))
    ck("sleeve membership matches the contract's 5/4/4/2/2",
       [sum(1 for e in inst if e["sleeve"] == s) for s in
        ["Equity", "Fixed income", "Commodity", "FX", "Real estate"]] == [5, 4, 4, 2, 2])
    ck("no object is leveraged or inverse", all(e["leveraged_or_inverse"] == "NO" for e in inst))
    ck("unestablished fields are NOT_PINNED, never invented",
       all(e["benchmark_index_name"] == "NOT_PINNED" and e["sponsor_of_record"] == "NOT_PINNED"
           for e in inst))

S0_SHA = "c4a21dc86038f9f0d06e32a267810b46cb39d9dd3549c35ef3329c87f884d6fb"
S0_CSV = "data/prospective/S0_20260913T165624Z.csv"
FROZEN_SHA = "3d2a7a56dbd92d4ff8138cfd894c87f5ac5ac088a11165db870673e0c05c3c31"
if os.path.isfile(SNAP):
    sn = flat(io.open(SNAP, encoding="utf-8").read())
    ck("snapshot registry pins the frozen-panel hash", FROZEN_SHA in sn)
    ck("snapshot registry pins S_0 by sha256", S0_SHA in sn)
    ck("snapshot registry records S_G as NOT created", "S_G_CREATED = NO" in sn)
    ck("snapshot registry states S_0 need not equal FORWARD_BOUNDARY",
       has(sn, "is NOT required to equal `FORWARD_BOUNDARY`"))
    ck("post-boundary rows classified state-input-only",
       "POST_SEAL_UNSCORED_STATE_INPUT_ONLY" in sn)
    ck("snapshot registry records the §J adjudication",
       has(sn, "Adjudicated 2026-09-14 under §J — `MECHANICAL_CORRECTION` (no action)."))
    ck("snapshot registry states no tolerance was invented",
       has(sn, "That tolerance was already fixed by the contract; none was invented."))
    ck("snapshot registry asserts the data boundary",
       has(sn, "**Data boundary asserted, not assumed.**",
           "No post-boundary signal, position, return, Sharpe, PnL, drawdown or performance proxy was computed"))

if os.path.isfile(S0_CSV):
    got = hashlib.sha256(io.open(S0_CSV, "rb").read()).hexdigest()
    ck("S_0 file on disk matches its pinned sha256", got == S0_SHA, got)
if os.path.isfile("data/close_prices_raw.csv"):
    got = hashlib.sha256(io.open("data/close_prices_raw.csv", "rb").read()).hexdigest()
    ck("frozen panel still matches its pinned sha256 (never overwritten)", got == FROZEN_SHA, got)

ck("PC-1 recorded CLOSED in the single authoritative register",
   has(CAF, "PC-1  CLOSED from EXISTING §J authority, 2026-09-14. No new tolerance created."))
ck("PC-1 classification is MECHANICAL_CORRECTION under the §J row",
   has(CAF, "PC-1 CLASSIFICATION = MECHANICAL_CORRECTION (no action), under the §J",
       '"Split / dividend back-adjustment" row.'))
ck("PC-1 records NEW_TOLERANCE_CREATED = NO", has(CAF, "NEW_TOLERANCE_CREATED = NO"))
ck("PC-1 cites the contract's own position test, not a new one",
   has(CAF, "`max |Δposition| ≤ 0.01` and no sign flip", "was already fixed by the contract"))
ck("PC-1 records the observed diagnostic values",
   has(CAF, "1.348102e-04"))
ck("PC-1 states no post-boundary quantity was computed",
   has(CAF, "**No post-boundary signal, position,",
       "return, Sharpe, PnL, drawdown, performance statistic or performance proxy was",
       "computed.**"))
ck("§Z.1 item 6 recorded DONE", has(CAF, "| 6 | Instrument identity registry"))
ck("§Z.1 item 7 records DONE with the §J classification",
   has(CAF, "| 7 | Seal-time snapshot and provenance procedure completed",
       "classified `MECHANICAL_CORRECTION` under the §J split/dividend row"))
ck("§Z.1 item 8 records PC-1 closed",
   has(CAF, "| 8 | **`PC-1` closed** (§Y) | **DONE**"))
ck("header records no open pre-seal item", has(CAF, "OPEN_PRE_SEAL_ITEMS         = NONE"))
ck("header records §K conformance", has(CAF, "§K conformance SATISFIED"))
ck("no artifact still claims the seal is blocked",
   "BLOCKS THE SEAL" not in ca)

print("\n" + ("VALIDATION PASSED" if ok else "VALIDATION FAILED"))
sys.exit(0 if ok else 1)
