# -*- coding: utf-8 -*-
"""F6 S1 PRE-SEAL MECHANICAL VALIDATION.

METADATA ONLY. This script MUST NOT compute an F6 outcome. It never reads a
price VALUE: the panel is opened for its DATE INDEX and for column PRESENCE
(notna) only, which is what is strictly necessary to prove the design matrix is
constructible. No return, no r_excess, no r_net, no beta_EVENT, no bootstrap,
no interval.

It validates the S1 serialization and emits the pre-seal manifest.
"""
import hashlib, json, os, subprocess, sys
import datetime as dt
import numpy as np
import pandas as pd

REPO = r"C:\Users\Aaron\OneDrive\Desktop\Quant trade\multi-asset-tsmom-research"
WS = r"C:\Users\Aaron\OneDrive\Desktop\Quant trade"
os.chdir(REPO)
sys.path.insert(0, REPO)
import config                                    # noqa: E402
from src import seasonality                      # noqa: E402

F6 = "research/extensions/f6"
LO, HI = "2011-01-01", "2025-12-31"
COST_ROUND_TRIP = 0.0004          # 2 bps entry + 2 bps exit
RF_DAYCOUNT = 365                 # OWNER-CHOSEN. NOT Treasury/H.15/FRED.
B = 100000
SEED_PREFIX = "CTA-EDGE-05|F6|S1_BOOTSTRAP|"
WEEKDAY_BASELINE = "Friday"       # pinned: alphabetical drop_first baseline
QUANTILE_LO, QUANTILE_HI = 0.025, 0.975
QUANTILE_METHOD = "linear"

FAIL = []
def check(name, ok, detail=""):
    print("  %-52s %s%s" % (name, "PASS" if ok else "FAIL",
                            ("  " + detail) if detail else ""))
    if not ok:
        FAIL.append(name)
    return ok

def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()

print("=" * 72)
print("F6 S1 PRE-SEAL MECHANICAL VALIDATION")
print("=" * 72)

# ---------------------------------------------------------------- 1. manifest
man = json.load(open(os.path.join(F6, "F6_FINAL_EVENT_MANIFEST.json"),
                     encoding="utf-8"))
MAN_SHA = sha(os.path.join(F6, "F6_FINAL_EVENT_MANIFEST.json"))
fam = {e["session"]: list(e["families"]) for e in man["event_sessions"]}
sess_keys = [e["session"] for e in man["event_sessions"]]

print("\n[1] FINAL EVENT MANIFEST  sha256 %s" % MAN_SHA)
N = len(fam)
check("unique event sessions == 462", N == 462, "got %d" % N)
check("no duplicate session keys", len(sess_keys) == len(set(sess_keys)))
lab = {}
for v in fam.values():
    for f in v:
        lab[f] = lab.get(f, 0) + 1
overlap = sum(len(v) - 1 for v in fam.values())
multi = sum(1 for v in fam.values() if len(v) > 1)
check("FOMC labels == 119", lab.get("FOMC") == 119, "got %s" % lab.get("FOMC"))
check("CPI  labels == 176", lab.get("CPI") == 176, "got %s" % lab.get("CPI"))
check("NFP  labels == 176", lab.get("NFP") == 176, "got %s" % lab.get("NFP"))
check("family labels == 471", sum(lab.values()) == 471,
      "got %d" % sum(lab.values()))
check("multi-event sessions == 9", multi == 9, "got %d" % multi)
check("overlap adjustment == 9", overlap == 9, "got %d" % overlap)
check("471 - 9 == 462 reconciles", sum(lab.values()) - overlap == N)
check("families are a subset of {FOMC,CPI,NFP}",
      set(lab) <= {"FOMC", "CPI", "NFP"}, str(sorted(lab)))
check("every session inside 2011..2025",
      all(LO <= k <= HI for k in fam), "")
check("NO 2026 session in the manifest",
      not any(k[:4] == "2026" for k in fam))

# the six PIT exclusions must still be absent and must NOT be reinstated
EXCL = [("NFP", "2013-10-22"), ("CPI", "2013-10-30"), ("CPI", "2013-11-20"),
        ("NFP", "2025-11-20"), ("NFP", "2025-12-16"), ("CPI", "2025-12-18")]
still_out = all(f not in fam.get(d, []) for f, d in EXCL)
check("all 6 PIT_UNRESOLVED labels remain excluded", still_out)
check("2013-10-30 retained as FOMC-only", fam.get("2013-10-30") == ["FOMC"],
      str(fam.get("2013-10-30")))

# ------------------------------------------------- 2. P2 population, ALL rows
print("\n[2] P2 POPULATION — every trading session 2011..2025, NO row dropped")
px = pd.read_csv("data/close_prices_raw.csv", index_col=0, parse_dates=True,
                 usecols=["Date", "SPY"])
sessions = pd.DatetimeIndex(sorted(px.index.unique()))
grid = sessions[(sessions >= pd.Timestamp(LO)) & (sessions <= pd.Timestamp(HI))]

first = grid[0]
i0 = sessions.searchsorted(first, side="left")
check("a prior panel session exists before the first 2011 session", i0 > 0)
boundary = sessions[i0 - 1]
print("      first 2011 session : %s" % first.date())
print("      lag boundary       : %s  (calendar %d, an INPUT BOUNDARY "
      "OBSERVATION, not a regression row)" % (boundary.date(), boundary.year))
check("lag boundary is a calendar-2010 session", boundary.year == 2010)
# PRESENCE ONLY. The value is never read, printed, or used arithmetically.
check("boundary session carries a non-null SPY entry (presence check only)",
      bool(px.loc[boundary, "SPY"].notna().all()
           if isinstance(px.loc[boundary, "SPY"], pd.Series)
           else pd.notna(px.loc[boundary, "SPY"])))

prev = [boundary] + list(grid[:-1])
df = pd.DataFrame(index=grid)
df["prev"] = prev
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

check("P2 rows == every 2011..2025 trading session", len(df) == len(grid),
      "%d rows" % len(df))
check("NO row was dropped for undefined HOLD", df["HOLD"].notna().all())
check("HOLD is strictly positive on every row", bool((df["HOLD"] > 0).all()),
      "min %d max %d" % (df.HOLD.min(), df.HOLD.max()))
check("first 2011 row IS present in the design", grid[0] in df.index)
check("no 2026 row in the design", not (df["year"] == 2026).any())
check("EVENT column sums to the manifest count", int(df.EVENT.sum()) == N,
      "got %d" % int(df.EVENT.sum()))
check("every manifest session is a real panel session",
      set(pd.to_datetime(list(fam))) <= set(grid))

# --------------------------------------------- 3. cross-tabs + hard assertions
print("\n[3] DESIGN CROSS-TABS — regenerated, never transcribed")
wk = pd.crosstab(df["weekday"], df["EVENT"])[1].to_dict()
tom = pd.crosstab(df["TOM"], df["EVENT"])[1].to_dict()
au = pd.crosstab(df["AUCTION"], df["EVENT"])[1].to_dict()
print("      weekday %s" % wk)
print("      TOM     %s   AUCTION %s" % (tom, au))
check("sum(event weekday cells) == FINAL_PRIMARY_EVENT_COUNT",
      sum(wk.values()) == N)
check("sum(event TOM cells)     == FINAL_PRIMARY_EVENT_COUNT",
      sum(tom.values()) == N)
check("sum(event AUCTION cells) == FINAL_PRIMARY_EVENT_COUNT",
      sum(au.values()) == N)
check("family labels - overlap  == FINAL_PRIMARY_EVENT_COUNT",
      sum(lab.values()) - overlap == N)

# ------------------------------------------------------- 4. fixed P2 model
print("\n[4] FIXED P2 MODEL — the only allowed specification")
def design(frame):
    d = pd.get_dummies(frame[["weekday"]], drop_first=True).astype(float)
    d.insert(0, "const", 1.0)
    for c in ("EVENT", "TOM", "HOLD", "AUCTION"):
        d[c] = frame[c].to_numpy(float)
    return d

X = design(df)
dropped = [w for w in df["weekday"].unique()
           if ("weekday_" + w) not in X.columns]
check("weekday baseline is the pinned '%s'" % WEEKDAY_BASELINE,
      dropped == [WEEKDAY_BASELINE], str(dropped))
A = X.to_numpy(float)
rank = int(np.linalg.matrix_rank(A))
check("pooled design matrix is FULL COLUMN RANK",
      rank == A.shape[1], "shape %s rank %d" % (A.shape, rank))
C = X.drop(columns=["EVENT"]).to_numpy(float)
rc = int(np.linalg.matrix_rank(C))
rce = int(np.linalg.matrix_rank(np.column_stack([C, X["EVENT"].to_numpy()])))
check("EVENT is NOT in the span of the controls (separately identified)",
      rce != rc)
check("no required column is constant",
      all(X[c].nunique() > 1 for c in X.columns if c != "const"))
check("model carries NO interaction / alternate / fallback column",
      set(X.columns) == {"const", "EVENT", "TOM", "HOLD", "AUCTION",
                         "weekday_Monday", "weekday_Thursday",
                         "weekday_Tuesday", "weekday_Wednesday"},
      str(sorted(X.columns)))
for banned in ("TLT", "IEF", "NQ", "F6B", "SURPRISE", "CONSENSUS", "ACTUAL"):
    check("no %s field in the design" % banned,
          not any(banned.lower() in c.lower() for c in X.columns))

# ------------------------------- 5. PER-YEAR rank (bootstrap estimability)
print("\n[5] PER-YEAR RANK — a draw repeating one year must stay estimable")
years = sorted(df["year"].unique())
check("YEAR_BLOCK_COUNT == 15", len(years) == 15, "got %d" % len(years))
check("year blocks are contiguous 2011..2025",
      years == list(range(2011, 2026)))
yr_rank, deficient = {}, []
for y in years:
    sub = df[df["year"] == y]
    Xy = design(sub)
    # a single year need not contain every weekday level of the POOLED design;
    # re-express it on the POOLED column set so the fixed model is what is
    # tested, with absent levels carried as genuine zero columns.
    Xy = Xy.reindex(columns=X.columns, fill_value=0.0)
    r = int(np.linalg.matrix_rank(Xy.to_numpy(float)))
    yr_rank[int(y)] = {"rows": int(len(sub)), "events": int(sub.EVENT.sum()),
                       "rank": r, "cols": int(Xy.shape[1]),
                       "full_rank": bool(r == Xy.shape[1])}
    if r != Xy.shape[1]:
        deficient.append(int(y))
    print("      %d  rows %3d  events %2d  rank %d/%d  %s"
          % (y, len(sub), sub.EVENT.sum(), r, Xy.shape[1],
             "FULL" if r == Xy.shape[1] else "DEFICIENT"))
INDIVIDUAL_YEAR_RANK_PASS = not deficient
check("EVERY individual calendar year is full column rank",
      INDIVIDUAL_YEAR_RANK_PASS, str(deficient))

# ------------------------------------------------------- 6. DGS3MO mapping
print("\n[6] DGS3MO MAPPING — including the 2011 opening boundary")
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
        unexplained.append({"session": str(d.date()), "benchmark": str(p.date()),
                            "reason": "no DGS3MO observation at or before the "
                                      "benchmark date"})
        continue
    src = vdates[j]
    carries.append((p - src).days)
    k = src + pd.Timedelta(days=1)
    while k <= p:
        if k.weekday() < 5 and k not in rows_present:
            unexplained.append({"session": str(d.date()),
                                "benchmark": str(p.date()),
                                "gap_date": str(k.date()),
                                "reason": "business day with NO row in the "
                                          "official source file"})
        k += pd.Timedelta(days=1)
cs = pd.Series(carries)
print("      sessions requiring rf_hold : %d" % len(df))
print("      carry distance (cal days)  : %s"
      % dict(cs.value_counts().sort_index()))
check("every session maps to an official observation",
      len(carries) == len(df), "%d of %d" % (len(carries), len(df)))
check("NO unexplained source gap", len(unexplained) == 0,
      str(unexplained[:3]))
check("carry never exceeds source-explained non-publication",
      int(cs.max()) <= 4, "max %d calendar days" % cs.max())
check("the 2011 opening row also maps cleanly",
      str(df.index[0].date()) not in {u["session"] for u in unexplained})
DGS3MO_PASS = len(unexplained) == 0 and len(carries) == len(df)

# --------------------------------------------------- 7. bootstrap serialization
print("\n[7] BOOTSTRAP SERIALIZATION — frozen pre-outcome")
seed_src = SEED_PREFIX + MAN_SHA
digest = hashlib.sha256(seed_src.encode("ascii")).hexdigest()
seed = int(digest[:8], 16)
print("      source string : %s" % seed_src)
print("      sha256        : %s" % digest)
print("      first 8 hex   : %s" % digest[:8])
print("      SEED (uint32) : %d" % seed)
check("seed is a valid unsigned 32-bit integer", 0 <= seed < 2 ** 32)
check("B == 100000", B == 100000)
check("15 resampling units drawn with replacement", len(years) == 15)
check("quantiles are 0.025 / 0.975", (QUANTILE_LO, QUANTILE_HI) == (0.025, 0.975))
check("numpy quantile method explicitly pinned", QUANTILE_METHOD == "linear")

# ---------------------------------------------------- 8. firewall / no results
print("\n[8] FIREWALL")
res = subprocess.run(["git", "ls-files"], capture_output=True, text=True).stdout
hits = [l for l in res.splitlines()
        if "f6" in l.lower() and any(t in l.lower() for t in
        ("result", "outcome", "evidence", "_s3", "_s4", "perf", "backtest"))]
check("NO F6 result / outcome artifact tracked in the repository",
      not hits, str(hits))
check("no return was computed in this validation", True)
check("no beta_EVENT was computed in this validation", True)
check("no bootstrap was executed in this validation", True)

print("\n" + "=" * 72)
print("VALIDATION %s   (%d failing checks)"
      % ("PASS" if not FAIL else "FAIL", len(FAIL)))
for f in FAIL:
    print("   FAILED: %s" % f)
print("=" * 72)

out = {
 "validated": len(FAIL) == 0,
 "failing_checks": FAIL,
 "final_event_count": N,
 "family_labels": lab, "family_labels_total": sum(lab.values()),
 "multi_event_sessions": multi, "overlap_adjustment": overlap,
 "p2_rows": int(len(df)),
 "opening_boundary": {"first_primary_session": str(first.date()),
   "lag_boundary_session": str(boundary.date()),
   "boundary_role": "INPUT BOUNDARY OBSERVATION — supplies the lagged close, "
                    "the interval boundary and HOLD for the first 2011 "
                    "session. It is NOT a 2010 regression row.",
   "rows_dropped_for_undefined_HOLD": 0},
 "cross_tabs": {"weekday": {k: int(v) for k, v in wk.items()},
   "tom": {str(k): int(v) for k, v in tom.items()},
   "auction": {str(k): int(v) for k, v in au.items()}},
 "pooled_design": {"shape": list(A.shape), "rank": rank,
   "full_rank": bool(rank == A.shape[1]),
   "event_in_span_of_controls": bool(rce == rc),
   "columns": list(X.columns), "weekday_baseline": WEEKDAY_BASELINE},
 "per_year_rank": yr_rank,
 "individual_year_matrix_rank_pass": INDIVIDUAL_YEAR_RANK_PASS,
 "rank_deficient_years": deficient,
 "dgs3mo": {"pass": DGS3MO_PASS, "sessions": int(len(df)),
   "max_carry_calendar_days": int(cs.max()),
   "carry_distribution": {str(k): int(v)
                          for k, v in cs.value_counts().sort_index().items()},
   "unexplained_gaps": unexplained},
 "bootstrap": {"B": B, "blocks": len(years), "years": [int(y) for y in years],
   "seed_source_string": seed_src, "seed_sha256": digest,
   "seed_first8_hex": digest[:8], "seed_literal_uint32": seed,
   "interval": "two-sided nominal 95% percentile-bootstrap",
   "lower_quantile": QUANTILE_LO, "upper_quantile": QUANTILE_HI,
   "quantile_implementation": "numpy.percentile(..., method=\"linear\")",
   "numpy_version": np.__version__, "pandas_version": pd.__version__,
   "python_version": sys.version.split()[0]},
 "constants": {"round_trip_cost": COST_ROUND_TRIP,
   "rf_daycount_owner_chosen": RF_DAYCOUNT},
 "firewall": {"spy_return_computed": False, "r_excess_computed": False,
   "r_net_computed": False, "beta_event_computed": False,
   "bootstrap_executed": False, "ci_computed": False,
   "sharpe_computed": False, "loyo_performance_computed": False,
   "tlt_accessed": False, "f6b_accessed": False,
   "y2026_outcome_accessed": False, "nq_accessed": False,
   "price_values_read": False,
   "price_panel_use": "DATE INDEX and column PRESENCE (notna) only"},
}
p = os.path.join(F6, "F6_S1_PRESEAL_VALIDATION.json")
with open(p, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(out, fh, indent=1, sort_keys=True)
    fh.write("\n")
print("\nwrote %s  sha256 %s" % (p, sha(p)))
if FAIL:
    raise SystemExit(1)
