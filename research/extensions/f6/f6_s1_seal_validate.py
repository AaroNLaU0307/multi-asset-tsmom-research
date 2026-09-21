# -*- coding: utf-8 -*-
"""F6 S1 SEAL VALIDATION — deterministic, run AFTER the seal.

METADATA ONLY, outcome-blind. Re-derives the design facts from source rather
than trusting the pre-seal JSON, and re-reads the sealed artifacts as bytes.
It never reads a price VALUE: the panel is opened for its DATE INDEX and for
column PRESENCE only.
"""
import hashlib, json, os, re, subprocess, sys
import numpy as np
import pandas as pd

REPO = r"C:\Users\Aaron\OneDrive\Desktop\Quant trade\multi-asset-tsmom-research"
os.chdir(REPO)
sys.path.insert(0, REPO)
import config                                    # noqa: E402
from src import seasonality                      # noqa: E402

F6 = "research/extensions/f6"
SEALED = F6 + "/F6_S1_PREREGISTRATION_SEALED.md"
LEDGER = "research/extensions/TRIAL_LEDGER.md"
OWNER = "ops/OWNER_DECISION_RECORD_CTA_EDGE_05_F6.md"
EXPOSURE = "ops/EXPOSURE_LEDGER.md"
LO, HI = "2011-01-01", "2025-12-31"

FAIL = []
def check(name, ok, detail=""):
    print("  %-56s %s%s" % (name, "PASS" if ok else "FAIL",
                            ("  " + detail) if detail else ""))
    if not ok:
        FAIL.append(name)
    return ok

def sha(p):
    with open(p, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()

print("=" * 78)
print("F6 S1 SEAL VALIDATION")
print("=" * 78)

# ------------------------------------------------------ 1. seal artifacts
print("\n[1] SEAL ARTIFACTS")
check("sealed preregistration exists", os.path.isfile(SEALED))
S = open(SEALED, encoding="utf-8").read()
check("SEAL_STATUS = SEALED", re.search(r"SEAL_STATUS\s*=\s*SEALED", S)
      is not None)
check("SEAL_ID present and canonical",
      "CTA-EDGE-05-F6-S1-2026-09-21" in S)
check("Owner seal authorization recorded in the contract",
      re.search(r'OWNER_SEAL_AUTHORIZATION\s*=\s*Aaron\s*/\s*explicit\s*"seal"',
                S) is not None)
check("NO_RETURN_EXPOSURE_BEFORE_SEAL = YES",
      re.search(r"NO_RETURN_EXPOSURE_BEFORE_SEAL\s*=\s*YES", S) is not None)
check("lineage stated exactly",
      "CTA-EDGE-05 / F6 MACRO_ANNOUNCEMENT_PREMIUM" in S)
for art in ("F6_S1_SEAL_RECORD.md", "F6_S1_SEALED_MANIFEST.json"):
    check("%s exists" % art, os.path.isfile(os.path.join(F6, art)))
man = json.load(open(os.path.join(F6, "F6_S1_SEALED_MANIFEST.json"),
                     encoding="utf-8"))
check("sealed manifest says SEALED",
      man["SEAL_STATUS"] == "SEALED" and man["sealed"] is True)
check("sealed manifest records the Owner authorization literal",
      man["authorization_literal"] == "seal")
check("sealed manifest pins the sealed preregistration by its CURRENT bytes",
      man["pins"]["sealed_preregistration"]["sha256"] == sha(SEALED))
check("sealed manifest pins the seal record by its CURRENT bytes",
      man["pins"]["seal_record"]["sha256"] == sha(os.path.join(
          F6, "F6_S1_SEAL_RECORD.md")))

print("\n[1b] ALL SEALED-MANIFEST PINS RECHECKED")
bad = []
for k, v in man["pins"].items():
    root = REPO if v["root"] == "repository" else \
        r"C:\Users\Aaron\OneDrive\Desktop\Quant trade"
    p = os.path.join(root, v["path"])
    if not os.path.isfile(p) or sha(p) != v["sha256"]:
        bad.append(k)
check("every sealed-manifest pin reproduces (%d pins)" % len(man["pins"]),
      not bad, str(bad))

# ------------------------------------------------------ 2. Owner record
print("\n[2] OWNER DECISION RECORD")
O = open(OWNER, encoding="utf-8").read()
check("OWNER_SEAL_AUTHORIZATION = YES",
      re.search(r"OWNER_SEAL_AUTHORIZATION\s*=\s*YES", O) is not None)
check('AUTHORIZATION_LITERAL = "seal"',
      re.search(r'AUTHORIZATION_LITERAL\s*=\s*"seal"', O) is not None)
check("S1_SEAL_STATUS = SEALED",
      re.search(r"S1_SEAL_STATUS\s*=\s*SEALED", O) is not None)
check("Fable / Astra / Owner kept as three distinct sources",
      all(t in O for t in ("FABLE", "ASTRA", "AARON (OWNER)")))
check("owner record pin in sealed manifest is the POST-APPEND hash",
      man["pins"]["owner_decision_record"]["sha256"] == sha(OWNER))

# -------------------------------------------------- 3. event universe
print("\n[3] EVENT UNIVERSE — re-derived from the manifest bytes")
em = json.load(open(os.path.join(F6, "F6_FINAL_EVENT_MANIFEST.json"),
                    encoding="utf-8"))
fam = {e["session"]: list(e["families"]) for e in em["event_sessions"]}
lab = {}
for v in fam.values():
    for f in v:
        lab[f] = lab.get(f, 0) + 1
overlap = sum(len(v) - 1 for v in fam.values())
multi = sum(1 for v in fam.values() if len(v) > 1)
N = len(fam)
check("FINAL_EVENT_MANIFEST_SHA256 unchanged",
      sha(os.path.join(F6, "F6_FINAL_EVENT_MANIFEST.json")) ==
      "49ff27bfc20eb98265c440bac7368e92022b356d77647dce9151f012e40ed382")
check("final event count == 462", N == 462, "got %d" % N)
check("FOMC == 119", lab.get("FOMC") == 119, "got %s" % lab.get("FOMC"))
check("CPI  == 176", lab.get("CPI") == 176, "got %s" % lab.get("CPI"))
check("NFP  == 176", lab.get("NFP") == 176, "got %s" % lab.get("NFP"))
check("family labels == 471", sum(lab.values()) == 471)
check("multi-event overlaps == 9", multi == 9 and overlap == 9,
      "multi %d overlap %d" % (multi, overlap))
check("471 - 9 == 462", sum(lab.values()) - overlap == N)
check("no 2026 session in the manifest",
      not any(k[:4] == "2026" for k in fam))
EXCL = [("NFP", "2013-10-22"), ("CPI", "2013-10-30"), ("CPI", "2013-11-20"),
        ("NFP", "2025-11-20"), ("NFP", "2025-12-16"), ("CPI", "2025-12-18")]
check("all 6 PIT exclusions still absent (no post-seal reinstatement)",
      all(f not in fam.get(d, []) for f, d in EXCL))
check("2013-10-30 retained FOMC-only", fam.get("2013-10-30") == ["FOMC"])

# ----------------------------------------- 4. design matrix, re-derived
print("\n[4] DESIGN MATRIX — rebuilt from source, metadata only")
px = pd.read_csv("data/close_prices_raw.csv", index_col=0, parse_dates=True,
                 usecols=["Date", "SPY"])
sessions = pd.DatetimeIndex(sorted(px.index.unique()))
grid = sessions[(sessions >= pd.Timestamp(LO)) & (sessions <= pd.Timestamp(HI))]
i0 = sessions.searchsorted(grid[0], side="left")
boundary = sessions[i0 - 1]
check("opening 2011 session is 2011-01-03", str(grid[0].date()) == "2011-01-03")
check("boundary input is 2010-12-31", str(boundary.date()) == "2010-12-31")

df = pd.DataFrame(index=grid)
df["prev"] = [boundary] + list(grid[:-1])
df["EVENT"] = [1 if d.strftime("%Y-%m-%d") in fam else 0 for d in grid]
df["weekday"] = [d.day_name() for d in grid]
df["TOM"] = seasonality.is_tom(grid, last=config.SEAS_TOM_LAST,
                               first=config.SEAS_TOM_FIRST).astype(int).values
df["HOLD"] = [(d - p).days for d, p in zip(grid, df["prev"])]
import csv as _csv
auc = set()
for r in _csv.DictReader(open("research/extensions/ta/TA_EVENT_CALENDAR.csv",
                              encoding="utf-8")):
    if r["tenor_family"] in ("10-Year", "30-Year") and r["auction_date"]:
        j = sessions.searchsorted(pd.Timestamp(r["auction_date"]), side="left")
        if j < len(sessions):
            auc.add(sessions[j])
df["AUCTION"] = [1 if d in auc else 0 for d in grid]
df["year"] = grid.year

check("NO 2010 regression row was added",
      int((df.index.year == 2010).sum()) == 0 and df.index.min() == grid[0])
check("boundary date is used ONLY as an input, never as a row",
      boundary not in set(df.index))
check("P2 population is every 2011-2025 session, none dropped",
      len(df) == len(grid) and df["HOLD"].notna().all(), "%d rows" % len(df))
check("EVENT column sums to 462", int(df.EVENT.sum()) == 462)
check("no 2026 row in the design", not (df["year"] == 2026).any())

# CANONICAL weekday parameterization: FRIDAY reference
WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday"]
def design(frame):
    d = pd.DataFrame(index=frame.index)
    d["const"] = 1.0
    d["EVENT"] = frame["EVENT"].to_numpy(float)
    for w in WEEK:
        d["weekday_" + w] = (frame["weekday"] == w).to_numpy(float)
    for c in ("TOM", "HOLD", "AUCTION"):
        d[c] = frame[c].to_numpy(float)
    return d

X = design(df)
present = set(df["weekday"].unique())
omitted = sorted(present - set(WEEK))
check("WEEKDAY_REFERENCE is FRIDAY and it is UNIQUE", omitted == ["Friday"],
      str(omitted))
check("included indicators are exactly Mon/Tue/Wed/Thu",
      [c for c in X.columns if c.startswith("weekday_")] ==
      ["weekday_" + w for w in WEEK])
check("intercept present", "const" in X.columns)
check("sealed contract declares WEEKDAY_REFERENCE = FRIDAY",
      re.search(r"WEEKDAY_REFERENCE\s*=\s*FRIDAY", S) is not None)
check("sealed contract carries NO Monday-as-reference claim",
      re.search(r"Monday is the reference", S) is None)
A = X.to_numpy(float)
rank = int(np.linalg.matrix_rank(A))
check("pooled design FULL COLUMN RANK", rank == A.shape[1],
      "shape %s rank %d" % (A.shape, rank))
C = X.drop(columns=["EVENT"]).to_numpy(float)
check("EVENT not in the span of the controls",
      int(np.linalg.matrix_rank(np.column_stack([C, X.EVENT.to_numpy()]))) !=
      int(np.linalg.matrix_rank(C)))

years = sorted(df["year"].unique())
check("15 year blocks, contiguous 2011..2025",
      years == list(range(2011, 2026)), "got %d" % len(years))
deficient = []
for y in years:
    Xy = design(df[df["year"] == y]).reindex(columns=X.columns, fill_value=0.0)
    if int(np.linalg.matrix_rank(Xy.to_numpy(float))) != Xy.shape[1]:
        deficient.append(int(y))
check("EVERY individual-year P2 matrix is full rank", not deficient,
      str(deficient))

# ------------------------------------------------------ 5. DGS3MO
print("\n[5] DGS3MO MAPPING")
rf = pd.read_csv("data/DGS3MO.csv")
rf["observation_date"] = pd.to_datetime(rf["observation_date"])
rf["DGS3MO"] = pd.to_numeric(rf["DGS3MO"], errors="coerce")
rows_present = set(rf["observation_date"])
vdates = pd.DatetimeIndex(sorted(rf.loc[rf["DGS3MO"].notna(),
                                        "observation_date"]))
unexplained, carries = [], []
for d, p in zip(df.index, df["prev"]):
    j = vdates.searchsorted(p, side="right") - 1
    if j < 0:
        unexplained.append(str(d.date()))
        continue
    src = vdates[j]
    carries.append((p - src).days)
    k = src + pd.Timedelta(days=1)
    while k <= p:
        if k.weekday() < 5 and k not in rows_present:
            unexplained.append(str(d.date()))
        k += pd.Timedelta(days=1)
check("every session maps to an official observation",
      len(carries) == len(df))
check("ZERO unexplained source gaps", not unexplained, str(unexplained[:3]))
check("max carry is source-explained", max(carries) <= 4,
      "max %d days" % max(carries))

# ------------------------------------------- 6. frozen numeric constants
print("\n[6] FROZEN CONSTANTS IN THE SEALED CONTRACT")
fc = man["frozen_constants"]
check("BOOTSTRAP_B == 100000", fc["bootstrap_B"] == 100000)
check("BOOTSTRAP_SEED_LITERAL == 2540719150",
      fc["bootstrap_seed_literal"] == 2540719150)
check("seed derives from the final event manifest hash",
      fc["bootstrap_seed_source"] ==
      "CTA-EDGE-05|F6|S1_BOOTSTRAP|"
      "49ff27bfc20eb98265c440bac7368e92022b356d77647dce9151f012e40ed382")
check("seed literal reproduces from the source string",
      int(hashlib.sha256(fc["bootstrap_seed_source"].encode("ascii"))
          .hexdigest()[:8], 16) == 2540719150)
check("quantile implementation is numpy linear",
      fc["quantile_implementation"] == 'numpy.percentile(..., method="linear")')
check("quantiles are 0.025 / 0.975",
      (fc["lower_quantile"], fc["upper_quantile"]) == (0.025, 0.975))
check("interval wording is NOMINAL, never 'exact coverage'",
      "nominal" in fc["interval"].lower() and "exact" not in fc["interval"].lower())
check("sealed contract forbids 'exact finite-sample 95% coverage'",
      "exact finite-sample 95% coverage" in S)
check("cost == 0.0004 round trip", fc["round_trip_cost"] == 0.0004)
check("contract states 2 bps entry + 2 bps exit",
      "2 bps entry + 2 bps exit" in S)
check("/365 attributed as OWNER-CHOSEN, not to Treasury/H.15/FRED",
      "OWNER-CHOSEN" in fc["cash_proxy"] and
      re.search(r"MUST NEVER BE ATTRIBUTED TO TREASURY, H\.15 OR FRED", S)
      is not None)
check("evidence ceiling SUPPORTED, no independent confirmation",
      fc["evidence_ceiling"] == "SUPPORTED" and
      fc["independent_confirmation"] is False and
      fc["sample_reuse_class"] == "T0_REUSED_DEPENDENT")

print("\n[7] PROHIBITIONS PRESERVED IN THE SEALED CONTRACT")
check("2026 outcome prohibited",
      "NO F6 OUTCOME QUANTITY MAY BE FORMED" in S)
check("TLT prohibited",
      "STRUCK ENTIRELY FROM CTA-EDGE-05 OUTCOME COMPUTATION" in S)
check("F6.b prohibited", "SEPARATE FUTURE LINEAGE. NOT COMPUTED." in S)
check("no alternate / fallback model", "fallback model" in S and
      "NO FALLBACK MODEL EXISTS" in S)
check("no alternate cash proxy",
      "DO NOT SUBSTITUTE ANOTHER CASH SERIES" in S)
check("no alternate event weights", "no alternate weighting" in S)
check("no result-contingent rescue",
      "RESCUE_POWER    = NONE" in S and "no family-deletion rescue" in S)
check("no LOW_POWER label", "NO LOW_POWER LABEL EXISTS" in S)
check("LOYO significance and stable magnitudes both disclaimed",
      "LOYO significance" in S and "stable LOYO magnitudes" in S)
check("claim cap forbids independent confirmation / buy-and-hold dominance",
      "independent confirmation" in S and "buy-and-hold dominance" in S)

# ------------------------------------------------------ 8. accounting
print("\n[8] ACCOUNTING")
L = open(LEDGER, encoding="utf-8").read()
rows = [l for l in L.split("\n") if l.startswith("| 5 | **`F-F6`**")]
check("F-F6 appears EXACTLY ONCE as a ledger row", len(rows) == 1,
      "%d rows" % len(rows))
row = rows[0] if rows else ""
check("F-F6 status is SEALED / NOT EXECUTED",
      "SEALED / NOT EXECUTED" in row and "NOTHING HAS RUN" in row)
check("F6_PRIMARY_TRIAL_SPENT = NO in the ledger row",
      "`F6_PRIMARY_TRIAL_SPENT = NO`" in row)
check("F-F6 records m = 1, no multiplicity correction",
      "m = 1" in row and "NO multiplicity correction" in row)
check("ledger row claims NO result and NO bootstrap statistic",
      "no bootstrap statistic" in row and "no result artifact exists" in row)
check("no VARIANT_ATTEMPT row added for F6",
      "F-F6" not in L.split("### §6.1")[1].split("### §6.2")[0]
      if "### §6.1" in L else True)
check("sealed manifest: trial ledger pin is POST-APPEND, not pre-append",
      man["pins"]["trial_ledger_post_append"]["sha256"] == sha(LEDGER) and
      man["pins"]["trial_ledger_post_append"]["sha256"] !=
      man["trial_ledger_pin_discipline"]["pre_append_sha256_NOT_AUTHORITATIVE"])
E = open(EXPOSURE, encoding="utf-8").read()
check("NO F6 exposure row exists", "F6" not in E or
      not re.search(r"^\|.*\bF6\b", E, re.M), "")
check("exposure ledger unchanged by the seal",
      man["accounting"]["exposure_ledger_changed"] is False and
      man["pins"]["exposure_ledger"]["sha256"] == sha(EXPOSURE))
check("F6_PRIMARY_TRIAL_CONSUMED = NO",
      man["accounting"]["f6_primary_trial_consumed"] is False)
check("no executed-trial counter incremented",
      man["accounting"]["executed_trial_counter_incremented"] is False)

# ------------------------------------------------------ 9. firewall
print("\n[9] FIREWALL")
tracked = subprocess.run(["git", "ls-files"], capture_output=True,
                         text=True).stdout.splitlines()
hits = [l for l in tracked if "f6" in l.lower() and any(
        t in l.lower() for t in ("result", "outcome", "evidence", "_s3", "_s4",
                                 "perf", "backtest"))]
check("NO F6 result artifact exists", not hits, str(hits))
check("no historical F6 return was accessed",
      man["firewall"]["spy_return_computed"] is False and
      man["firewall"]["beta_event_computed"] is False and
      man["firewall"]["bootstrap_executed"] is False and
      man["firewall"]["price_values_read"] is False)
check("seal operation recorded as outcome-blind",
      man["firewall"]["seal_operation_outcome_blind"] is True)

print("\n[10] POST-SEAL STATE")
ps = man["post_seal_state"]
check("S1 = SEALED", ps["S1"] == "SEALED")
check("S2_BUILD_AUTHORIZED = YES", ps["S2_BUILD_AUTHORIZED"] is True)
check("S3_RUN_AUTHORIZED = NO", ps["S3_RUN_AUTHORIZED"] is False)
check("RETURN_REVEAL_AUTHORIZED = NO",
      ps["RETURN_REVEAL_AUTHORIZED"] is False)
check("contract states S2 does NOT authorize the historical run",
      "IT DOES NOT AUTHORIZE RUNNING THE HISTORICAL F6 OUTCOME" in S)

print("\n" + "=" * 78)
print("FINAL_SEAL_VALIDATION = %s   (%d failing checks)"
      % ("PASS" if not FAIL else "FAIL", len(FAIL)))
for f in FAIL:
    print("   FAILED: %s" % f)
print("=" * 78)

out = {"final_seal_validation": "PASS" if not FAIL else "FAIL",
       "failing_checks": FAIL,
       "seal_id": man["seal_id"], "seal_date": man["seal_date"],
       "sealed_preregistration_sha256": sha(SEALED),
       "seal_record_sha256": sha(os.path.join(F6, "F6_S1_SEAL_RECORD.md")),
       "post_seal_trial_ledger_sha256": sha(LEDGER),
       "owner_decision_record_sha256": sha(OWNER),
       "final_event_manifest_sha256": sha(os.path.join(
           F6, "F6_FINAL_EVENT_MANIFEST.json")),
       "final_event_count": N, "family_labels": lab,
       "multi_event_overlaps": overlap, "p2_rows": int(len(df)),
       "year_blocks": len(years), "weekday_reference": omitted[0] if omitted
       else None, "rank": rank, "rank_deficient_years": deficient,
       "dgs3mo_unexplained_gaps": len(unexplained),
       "bootstrap_B": fc["bootstrap_B"],
       "bootstrap_seed_literal": fc["bootstrap_seed_literal"],
       "quantile_implementation": fc["quantile_implementation"],
       "f_f6_row_count": len(rows),
       "f6_family_status": "SEALED / NOT EXECUTED",
       "f6_primary_trial_consumed": False,
       "f6_performance_exposure_added": False,
       "f6_return_outcome_accessed": False,
       "S1": "SEALED", "S2_BUILD_AUTHORIZED": True,
       "S3_RUN_AUTHORIZED": False, "RETURN_REVEAL_AUTHORIZED": False}
p = os.path.join(F6, "F6_S1_SEAL_VALIDATION.json")
with open(p, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(out, fh, indent=1, sort_keys=True)
    fh.write("\n")
print("\nwrote %s  sha256 %s" % (p, sha(p)))
if FAIL:
    raise SystemExit(1)
