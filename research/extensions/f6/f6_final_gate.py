# -*- coding: utf-8 -*-
"""F6 FINAL S0 GATE — point-in-time event eligibility, frozen.

Applies the fail-closed schedule-PIT rule, rebuilds every count MECHANICALLY
(nothing transcribed), and asserts the count identities.

METADATA ONLY. No SPY return, no payoff, no cash-excess, no beta_EVENT, no CI,
no Sharpe, no LOYO performance. The price panel is opened for its DATE INDEX
only.
"""
import csv, hashlib, json, os, sys
import datetime as dt
import numpy as np
import pandas as pd

REPO = r"C:\Users\Aaron\OneDrive\Desktop\Quant trade\multi-asset-tsmom-research"
os.chdir(REPO)
sys.path.insert(0, REPO)
import config                                   # noqa: E402
from src import seasonality                     # noqa: E402

OUT = "research/extensions/f6"
LO, HI = "2011-01-01", "2025-12-31"

# --------------------------------------------------------------------------- #
# PART 1/2 — the fail-closed schedule-PIT ruling, one row per CHANGED release.
# Each classification cites the contemporaneous authority that establishes it,
# or records that none was located. NOTHING is inferred from a page's current
# last-modified date, from the actual release date, or from a weekday habit.
# --------------------------------------------------------------------------- #
RESCHEDULES = [
 {"family": "CPI", "reference": "2013-09", "original": "2013-10-16",
  "actual": "2013-10-30", "announcement": None, "announcement_time": None,
  "classification": "PIT_UNRESOLVED",
  "evidence": "no contemporaneous BLS notice naming this date was located. The "
              "2013 blog archive has no entry between 2013-10-17 and "
              "2013-10-25, and the 2013-10-25 entry describes the 10-22 "
              "release RETROSPECTIVELY. The updated-schedule page's only stamp "
              "is 2013-12-06, after the event."},
 {"family": "NFP", "reference": "2013-09", "original": "2013-10-04",
  "actual": "2013-10-22", "announcement": None, "announcement_time": None,
  "classification": "PIT_UNRESOLVED",
  "evidence": "as CPI 2013-09: the only BLS entry mentioning 2013-10-22 is "
              "dated 2013-10-25, AFTER the release."},
 {"family": "NFP", "reference": "2013-10", "original": "2013-11-01",
  "actual": "2013-11-08", "announcement": "2013-10-31",
  "announcement_time": None,
  "classification": "CHANGED_BEFORE_ENTRY",
  "evidence": "BLS blog entry posted 2013-10-31 states verbatim: 'The "
              "Employment Situation for October will be published Friday, "
              "November 8, 2013, at 8:30 A.M. Eastern Time.' That is 8 days "
              "before close(2013-11-07)."},
 {"family": "CPI", "reference": "2013-10", "original": "2013-11-15",
  "actual": "2013-11-20", "announcement": None, "announcement_time": None,
  "classification": "PIT_UNRESOLVED",
  "evidence": "the 2013-10-31 blog says BLS 'updated our full schedule ... for "
              "the remainder of 2013' but does NOT name this date. Inferring "
              "its contents from a page stamped 2013-12-06 is exactly the "
              "inference the rule forbids."},
 {"family": "CPI", "reference": "2025-09", "original": "2025-10-15",
  "actual": "2025-10-24", "announcement": "2025-10-10",
  "announcement_time": None,
  "classification": "CHANGED_BEFORE_ENTRY",
  "evidence": "BLS notice 'September 2025 CPI Release Rescheduled', last "
              "modified 2025-10-10, states BLS will publish on Friday "
              "2025-10-24 at 8:30 A.M. ET. 13 days before close(2025-10-23)."},
 {"family": "NFP", "reference": "2025-09", "original": "2025-10-03",
  "actual": "2025-11-20", "announcement": None, "announcement_time": None,
  "classification": "PIT_UNRESOLVED",
  "evidence": "no dated BLS notice naming 2025-11-20 in advance was located. "
              "The revised-dates page carries only a page-level 2026-02-12 "
              "stamp and the Employment Situation schedule page carries none."},
 {"family": "NFP", "reference": "2025-11", "original": "2025-12-05",
  "actual": "2025-12-16", "announcement": None, "announcement_time": None,
  "classification": "PIT_UNRESOLVED",
  "evidence": "as NFP 2025-09."},
 {"family": "CPI", "reference": "2025-11", "original": "2025-12-10",
  "actual": "2025-12-18", "announcement": None, "announcement_time": None,
  "classification": "PIT_UNRESOLVED",
  "evidence": "as NFP 2025-09."},
]

CANCELLED = [
 {"family": "NFP", "reference": "2025-10", "note": "CANCELLED ENTIRELY; "
  "household data never collected. No event exists."},
 {"family": "CPI", "reference": "2025-10", "note": "CANCELLED ENTIRELY. "
  "No event exists."},
]

EXCLUDE = {(r["family"], r["actual"]) for r in RESCHEDULES
           if r["classification"] == "PIT_UNRESOLVED"}
print("PIT_UNRESOLVED releases excluded pre-outcome: %d" % len(EXCLUDE))
for f, d in sorted(EXCLUDE, key=lambda x: x[1]):
    print("   %s  %s" % (d, f))

# --------------------------------------------------------------------------- #
# PART 4 — final manifest
# --------------------------------------------------------------------------- #
prov = json.load(open(os.path.join(OUT, "F6_PRIMARY_MANIFEST_2011_2025.json"),
                      encoding="utf-8"))
fam = {e["session"]: list(e["families"]) for e in prov["event_sessions"]}

removed_labels, emptied = [], []
for sess in sorted(fam):
    keep = [f for f in fam[sess] if (f, sess) not in EXCLUDE]
    for f in fam[sess]:
        if (f, sess) in EXCLUDE:
            removed_labels.append({"session": sess, "family": f})
    if keep:
        fam[sess] = keep
    else:
        emptied.append(sess)
        del fam[sess]

print("\nlabels removed          : %d" % len(removed_labels))
print("sessions emptied entirely: %d  %s" % (len(emptied), emptied))
survivors = [r["session"] for r in removed_labels if r["session"] in fam]
print("sessions SURVIVING on another family: %s"
      % sorted(set(survivors)))
for s in sorted(set(survivors)):
    print("   %s retained as %s  <- the excluded release was one LABEL, not the"
          " whole session" % (s, fam[s]))

# --------------------------------------------------------------------------- #
# PART 5 — every count regenerated, nothing transcribed
# --------------------------------------------------------------------------- #
px = pd.read_csv("data/close_prices_raw.csv", index_col=0, parse_dates=True,
                 usecols=[0, 1])
sessions = pd.DatetimeIndex(sorted(px.index.unique()))
grid = sessions[(sessions >= pd.Timestamp(LO)) & (sessions <= pd.Timestamp(HI))]
evset = {pd.Timestamp(k) for k in fam}

N = len(fam)
labels = {}
for v in fam.values():
    for f in v:
        labels[f] = labels.get(f, 0) + 1
multi = {k: sorted(v) for k, v in fam.items() if len(v) > 1}
overlap = sum(len(v) - 1 for v in fam.values())

df = pd.DataFrame(index=grid)
df["EVENT"] = [1 if d in evset else 0 for d in grid]
df["weekday"] = [d.day_name() for d in grid]
df["TOM"] = seasonality.is_tom(grid, last=config.SEAS_TOM_LAST,
                               first=config.SEAS_TOM_FIRST).astype(int).values
prev = grid.to_series().shift(1)
df["HOLD"] = [(d - p).days if pd.notna(p) else np.nan for d, p in zip(grid, prev)]
auc = set()
for r in csv.DictReader(open("research/extensions/ta/TA_EVENT_CALENDAR.csv",
                             encoding="utf-8")):
    if r["tenor_family"] in ("10-Year", "30-Year") and r["auction_date"]:
        i = sessions.searchsorted(pd.Timestamp(r["auction_date"]), side="left")
        if i < len(sessions):
            auc.add(sessions[i])
df["AUCTION"] = [1 if d in auc else 0 for d in grid]
df["year"] = grid.year
df = df.iloc[1:]

wk = pd.crosstab(df["weekday"], df["EVENT"])[1].to_dict()
tom = pd.crosstab(df["TOM"], df["EVENT"])[1].to_dict()
au = pd.crosstab(df["AUCTION"], df["EVENT"])[1].to_dict()

print("\nFINAL COUNTS (generated)")
print("  unique event sessions %d" % N)
print("  FOMC %d  CPI %d  NFP %d  (labels %d)"
      % (labels.get("FOMC", 0), labels.get("CPI", 0), labels.get("NFP", 0),
         sum(labels.values())))
print("  multi-event sessions %d  overlap adjustment %d" % (len(multi), overlap))
print("  weekday cells %s -> %d" % (wk, sum(wk.values())))
print("  TOM cells     %s -> %d" % (tom, sum(tom.values())))
print("  AUCTION cells %s -> %d" % (au, sum(au.values())))

A_ = []
A_.append(("weekday sum == N", sum(wk.values()) == N))
A_.append(("TOM sum == N", sum(tom.values()) == N))
A_.append(("AUCTION sum == N", sum(au.values()) == N))
A_.append(("labels - overlap == N", sum(labels.values()) - overlap == N))
A_.append(("EVENT column sum == N", int(df.EVENT.sum()) == N))
for name, ok in A_:
    print("  ASSERT %-26s %s" % (name, "PASS" if ok else "FAIL"))
ALL_OK = all(ok for _, ok in A_)
if not ALL_OK:
    raise SystemExit("COUNT ASSERTION FAILED")

# --------------------------------------------------------------------------- #
# PART 6 — final control matrix
# --------------------------------------------------------------------------- #
X = pd.get_dummies(df[["weekday"]], drop_first=True).astype(float)
X.insert(0, "const", 1.0)
for c in ("EVENT", "TOM", "HOLD", "AUCTION"):
    X[c] = df[c].values.astype(float)
M = X.to_numpy(float)
rank = int(np.linalg.matrix_rank(M))
C = X.drop(columns=["EVENT"]).to_numpy(float)
rc = int(np.linalg.matrix_rank(C))
rce = int(np.linalg.matrix_rank(np.column_stack([C, X["EVENT"].to_numpy()])))
flat = [c for c in X.columns if c != "const" and X[c].nunique() < 2]
years = sorted(df["year"].unique())
per = df.groupby("year")["EVENT"].sum().astype(int)
loyo = {int(y): {"EVENTS_REMOVED": int(per[y]),
                 "EVENTS_REMAINING": int(per.sum() - per[y])} for y in years}
print("\nCONTROL MATRIX shape %s rank %d full_rank %s" % (M.shape, rank,
                                                          rank == M.shape[1]))
print("  EVENT in span of controls: %s" % (rce == rc))
print("  flat required columns: %s" % (flat or "none"))
print("  year blocks %d (%d..%d)" % (len(years), years[0], years[-1]))
rem = [v["EVENTS_REMAINING"] for v in loyo.values()]
print("  LOYO remainders %d..%d" % (min(rem), max(rem)))
for y in years:
    print("     %d  removed %2d  remaining %d"
          % (y, loyo[y]["EVENTS_REMOVED"], loyo[y]["EVENTS_REMAINING"]))

# --------------------------------------------------------------------------- #
final = {
 "schema": {"name": "f6-final-event-manifest", "version": 1},
 "generated": dt.date.today().isoformat(),
 "primary_years": [2011, 2025],
 "schedule_pit_rule": "FAIL-CLOSED. A CHANGED release whose contemporaneous "
   "announcement timing cannot be established from authoritative source is "
   "PIT_UNRESOLVED and is EXCLUDED from the primary sample PRE-OUTCOME. This "
   "is a schedule-authority exclusion, NOT outcome filtering, NOT a mechanism "
   "failure and NOT a return-based exclusion. The actual release date is NEVER "
   "substituted merely because it is known ex post.",
 "exclusion_granularity": "the excluded object is the RELEASE (a family label), "
   "not necessarily the session. A session carrying another independently "
   "knowable event family is RETAINED.",
 "reschedule_rulings": RESCHEDULES,
 "cancelled_releases": CANCELLED,
 "labels_removed": removed_labels,
 "sessions_emptied": emptied,
 "sessions_retained_on_another_family": sorted(set(survivors)),
 "final_counts": {
   "unique_event_sessions": N, "fomc_labels": labels.get("FOMC", 0),
   "cpi_labels": labels.get("CPI", 0), "nfp_labels": labels.get("NFP", 0),
   "family_labels_total": sum(labels.values()),
   "multi_event_sessions": len(multi),
   "multi_event_overlap_adjustment": overlap,
   "events_per_year": {str(k): int(v) for k, v in per.items()},
   "weekday_cells": {k: int(v) for k, v in wk.items()},
   "tom_cells": {str(k): int(v) for k, v in tom.items()},
   "auction_cells": {str(k): int(v) for k, v in au.items()}},
 "count_assertions": {n: bool(o) for n, o in A_},
 "release_time_authority": {
   "CPI": {"time": "08:30 ET", "regime_changes_located": "none",
     "contemporaneous_evidence": [
       "CPI news release USDL-13-2076 header: 'embargoed until 8:30 a.m. "
       "(EDT) Wednesday, October 30, 2013'",
       "BLS revised-dates notice, 2025 reschedules stated at 8:30 AM ET"]},
   "NFP": {"time": "08:30 ET", "regime_changes_located": "none",
     "contemporaneous_evidence": [
       "BLS blog 2013-10-31: 'Friday, November 8, 2013, at 8:30 A.M. Eastern "
       "Time'",
       "BLS revised-dates notice, 2025 reschedules stated at 8:30 AM ET"]},
   "FOMC": {"regimes": [
       {"until": "2013-01-30", "time": "2:15 p.m. ET",
        "status": "NOT VERIFIED from a tier-1 schedule document in this "
                  "session; the boundary is established, the pre-change clock "
                  "time is not"},
       {"from": "2013-03-20", "time": "2:00 p.m. ET",
        "status": "VERIFIED — Fed press release 2013-03-13 states policy "
                  "statements for all regularly scheduled meetings will now be "
                  "released at 2 p.m. ET; the frozen 2018-01-31 statement "
                  "carries 'For release at 2:00 p.m. EST'"}],
     "boundary_note": "the announcement is dated 2013-03-13 and the next "
                      "scheduled meeting concluded 2013-03-20, which is "
                      "therefore the first statement under the 2 p.m. regime.",
     "eligibility_impact": "NONE. Both candidate times fall inside the trading "
                           "session, so a close(t-1)->close(t) trade is "
                           "unaffected either way."}},
 "control_matrix": {"rows": int(len(df)), "shape": list(M.shape), "rank": rank,
   "full_rank": bool(rank == M.shape[1]),
   "event_in_span_of_controls": bool(rce == rc),
   "flat_required_columns": flat, "columns": list(X.columns)},
 "year_blocks": {"count": len(years), "years": [int(y) for y in years],
   "loyo": loyo,
   "loyo_remainder_range": [int(min(rem)), int(max(rem))]},
 "firewall": {"spy_return_read": False, "event_payoff_computed": False,
   "cash_excess_computed": False, "beta_event_computed": False,
   "ci_computed": False, "sharpe_computed": False,
   "loyo_performance_computed": False, "tlt_accessed": False,
   "f6b_accessed": False, "y2026_performance_accessed": False},
 "event_sessions": [{"session": k, "families": sorted(v)}
                    for k, v in sorted(fam.items())],
}
p = os.path.join(OUT, "F6_FINAL_EVENT_MANIFEST.json")
with open(p, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(final, fh, indent=1, sort_keys=True)
    fh.write("\n")
print("\nwrote %s" % p)
print("FINAL_EVENT_MANIFEST_SHA256 %s"
      % hashlib.sha256(open(p, "rb").read()).hexdigest())
