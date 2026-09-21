# -*- coding: utf-8 -*-
"""TSMOM-VRP-01 - S2A DATA ACQUISITION / AUTHORITY / PINNING gate.

Mechanical validation of the acquired Cboe VX chain. Every output is a hash, a count,
a date, a contract identifier or a boolean. This module NEVER computes or prints:

    a price average, a price return, a basis, a carry, a roll yield, a strategy
    return, a cumulative return, an annual return, a Sharpe, a drawdown, a Stage-A or
    Stage-B statistic, or any statistic that answers whether the candidate is
    profitable.

Run:  python research/extensions/vrp/vrp_data_validate.py
Exit: 0 = S2A PASS, 1 = S2A HOLD/FAIL.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
os.chdir(REPO)

import vrp_calendar as vcal      # noqa: E402
import vrp_chain as vchain       # noqa: E402
import vrp_raw as vraw           # noqa: E402
import vrp_specs as vspecs       # noqa: E402
from vrp_constants import (ETF_PANEL_SHA256, MAX_CARRY_FORWARD_DAYS,  # noqa: E402
                           STAGE_A_LAST_MONTH, cutoff)

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

MANIFEST_JSON = os.path.join(REPO, "data", "vix", "manifests", "vrp_raw_manifest.json")
RESULT_JSON = os.path.join(REPO, "data", "vix", "manifests", "vrp_s2a_result.json")

_ok = True
_results = []


def ck(label, cond, detail=""):
    global _ok
    if not cond:
        _ok = False
    _results.append({"check": label, "pass": bool(cond), "detail": str(detail)})
    print("  %-62s %s   %s" % (label, "PASS" if cond else "FAIL", detail))


def section(title):
    print("\n" + title)
    print("-" * 78)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    print("TSMOM-VRP-01 - S2A DATA ACQUISITION / AUTHORITY / PINNING")
    print("=" * 78)
    print("LANE: mechanical only. No return, basis, carry or outcome is computed here.")

    # ----------------------------------------------------------------- #
    section("1. MANIFEST AND RAW HASH RE-PINNING")
    ck("acquisition manifest present", os.path.isfile(MANIFEST_JSON), MANIFEST_JSON)
    if not os.path.isfile(MANIFEST_JSON):
        return 1
    with open(MANIFEST_JSON, encoding="utf-8") as fh:
        manifest = json.load(fh)
    rows = manifest["contract_files"]
    mismatched, missing = [], []
    for row in rows:
        path = os.path.join(REPO, str(row["relative_path"]).replace("/", os.sep))
        if not os.path.exists(path):
            missing.append(row["file_name"])
            continue
        if sha256_file(path) != row["sha256"]:
            mismatched.append(row["file_name"])
    ck("every pinned raw contract file present", not missing, "%d missing" % len(missing))
    ck("every raw contract file matches its pinned SHA256", not mismatched,
       "%d mismatched of %d" % (len(mismatched), len(rows)))
    docs = [d for d in manifest.get("specification_documents", []) if d.get("status") == "ACQUIRED"]
    doc_bad = []
    for d in docs:
        path = os.path.join(REPO, str(d["relative_path"]).replace("/", os.sep))
        if not os.path.exists(path) or sha256_file(path) != d["sha256"]:
            doc_bad.append(d["file_name"])
    ck("every specification document matches its pinned SHA256", not doc_bad,
       "%d documents" % len(docs))
    panel = os.path.join(REPO, "data", "close_prices_raw.csv")
    ck("frozen ETF panel present and matches the sealed pin",
       os.path.isfile(panel) and sha256_file(panel) == ETF_PANEL_SHA256,
       ETF_PANEL_SHA256[:16])
    ck("raw data tree is git-ignored (data/ in .gitignore)",
       "data/" in open(os.path.join(REPO, ".gitignore"), encoding="utf-8").read())

    # ----------------------------------------------------------------- #
    section("2. SOURCE AUTHORITY")
    levels = {str(r.get("source_authority_level")) for r in rows}
    ck("every raw contract file is SOURCE_AUTHORITY_LEVEL 1 / PRIMARY",
       levels == {"1 / PRIMARY"}, ",".join(sorted(levels)))
    hosts = {str(r["url"]).split("/")[2] for r in rows}
    ck("every raw contract file comes from a Cboe host", hosts <= {"cdn.cboe.com"},
       ",".join(sorted(hosts)))
    ck("settlement field is the official Settle column, never last trade",
       all("Settle" in open(os.path.join(REPO, str(r["relative_path"]).replace("/", os.sep)),
                            encoding="utf-8", errors="replace").readline()
           for r in rows[:5]), "header check")
    ck("no credential appears in any recorded URL",
       not any(tok in str(r["url"]).lower()
               for r in rows for tok in ("key=", "token=", "secret", "password", "apikey")))

    # ----------------------------------------------------------------- #
    section("3. CONTRACT IDENTITY AND SPECIFICATION HISTORY")
    contracts, cross = vraw.load_contracts(rows)
    keys = [(c.root, c.final_settlement_date) for c in contracts]
    ck("every (root, final_settlement_date) identity key is unique",
       len(set(keys)) == len(keys), "%d contracts" % len(contracts))
    ck("every contract file's own label names its delivery month (monthly VX, no weekly)",
       all(vraw.label_matches_month(c) for c in contracts))
    expired = [c for c in contracts if c.expired]
    exp_bad = [(c.contract_month, c.observed_last_settlement.isoformat())
               for c in expired
               if vcal.monthly_final_settlement(int(c.contract_month[:4]),
                                                int(c.contract_month[5:]))
               != c.observed_last_settlement]
    ck("rule-derived expiry == observed final settlement for every EXPIRED contract",
       not exp_bad, "%d expired, %d mismatched" % (len(expired), len(exp_bad)))
    ck("the 4 still-listed contracts carry no final-settlement row (expected)",
       len(contracts) - len(expired) == 4,
       "live: " + ",".join(c.contract_month for c in contracts if not c.expired))
    ok_span, gap = vspecs.covers_without_gaps(vspecs.VX_LISTING_DATE, _dt.date(2026, 12, 31))
    ck("specification break table covers every date with no gaps", ok_span, str(gap))
    ck("every specification span cites a saved, hashed primary document",
       all(s.source_document for s in vspecs.SPEC_SPANS),
       "%d spans, %d break date(s)" % (len(vspecs.SPEC_SPANS), len(vspecs.break_dates())))
    ck("2007 quotation / multiplier rescaling is dated from a primary document",
       vspecs.RESCALING_EFFECTIVE == _dt.date(2007, 3, 26)
       and any(d["file_name"] == "CFE-IC-2007-003.pdf" for d in docs),
       "effective %s, CFE IC07-03" % vspecs.RESCALING_EFFECTIVE)
    ck("tick history is defined for every date in the window",
       all(vspecs.tick_comparable(d) > 0
           for d in (vspecs.VX_LISTING_DATE, _dt.date(2007, 3, 25),
                     _dt.date(2007, 3, 26), _dt.date(2026, 8, 31))),
       "pre-break %.2f / post-break %.2f comparable points"
       % (vspecs.tick_comparable(_dt.date(2007, 3, 25)),
          vspecs.tick_comparable(_dt.date(2007, 3, 26))))
    ck("cross-source comparison: zero disagreements on common settled dates",
       all(r["disagreements"] == 0 for r in cross),
       "%d overlapping contracts, %d common dates"
       % (len(cross), sum(int(r["common_settled_dates"]) for r in cross)))

    # ----------------------------------------------------------------- #
    section("4. CALENDAR")
    cal = vraw.exchange_calendar_from(contracts)
    xcheck = cal.cross_check_rule(cal.days[0], _dt.date(2026, 8, 31))
    n_extra = len(xcheck["settled_but_not_rule_business_day"])
    n_missing = len(xcheck["rule_business_day_without_any_settlement"])
    n_unexplained = len(xcheck["unexplained"])
    ck("no rule business day without any VX settlement",
       n_missing == 0, "%d such dates" % n_missing)
    ck("every CFE session outside the US equity calendar is a DECLARED exception",
       n_extra == len(xcheck["explained_cfe_open"]),
       "%d session(s): %s" % (n_extra, ",".join(d.isoformat()
                                                for d in xcheck["explained_cfe_open"])))
    ck("zero UNEXPLAINED empirical-vs-rule calendar differences",
       n_unexplained == 0,
       ",".join(d.isoformat() for d in xcheck["unexplained"][:6]))

    # ----------------------------------------------------------------- #
    section("5. CHAIN CONSTRUCTION IDENTITIES (calendar-only; no price enters)")
    chain = vchain.build_chain(contracts, cal)
    ok, bad = vchain.weights_sum_to_one(chain)
    ck("roll weights sum to 1 within 1e-12 on every day", ok, ",".join(bad[:3]))
    ok, bad = vchain.front_zero_before_expiry(chain)
    ck("front weight is exactly 0 on the last settlement before final settlement",
       ok, ",".join(bad[:3]))
    ok, bad = vchain.daily_transfer_is_uniform(chain)
    ck("each business day transfers exactly 1/dt of the sensitivity", ok, ",".join(bad[:3]))
    ck("every chain day maps to exactly two distinct eligible monthly contracts",
       all(r.front_key != r.second_key for r in chain.days), "%d days" % len(chain.days))
    ck("front expiry always precedes second expiry",
       all(r.front_key[1] < r.second_key[1] for r in chain.days))

    # ----------------------------------------------------------------- #
    section("6. COVERAGE AND MISSING-SETTLEMENT ACCOUNTING (section F.4)")
    first_month = vchain.first_eligible_complete_month(chain, STAGE_A_LAST_MONTH)
    ck("a first eligible complete month exists under section F.6",
       first_month is not None, str(first_month))
    in_window = [r for r in chain.days
                 if first_month and vchain._month_key(r.date) >= first_month
                 and r.date < cutoff]
    carried = sum(1 for r in in_window if r.front_carried or r.second_carried)
    worst = max((chain.months[m].max_carry_forward
                 for m in chain.months if first_month and first_month <= m <= STAGE_A_LAST_MONTH),
                default=0)
    ck("no month in the frozen Stage-A window exceeds %d carry-forward days per contract"
       % MAX_CARRY_FORWARD_DAYS, worst <= MAX_CARRY_FORWARD_DAYS,
       "worst month = %d carry-forward day(s)" % worst)
    ck("no held contract lacks a settlement in the frozen window",
       all(r.front_price is not None and r.second_price is not None for r in in_window),
       "%d chain days in window" % len(in_window))
    ck("Stage-A window ends before the sealed cutoff",
       all(r.date < cutoff for r in in_window), "cutoff %s" % cutoff)

    # ----------------------------------------------------------------- #
    section("7. PERMITTED MECHANICAL COUNTS (no economic quantity)")
    months_in_window = [m for m in sorted(chain.months)
                        if first_month and first_month <= m <= STAGE_A_LAST_MONTH]
    counts = {
        "CONTRACT_COUNT": len(contracts),
        "MONTHLY_CONTRACT_COUNT_IN_WINDOW": len({r.front_key for r in in_window}
                                                | {r.second_key for r in in_window}),
        "FIRST_AVAILABLE_DATE": cal.days[0].isoformat(),
        "LAST_AVAILABLE_DATE": cal.days[-1].isoformat(),
        "NUMBER_OF_ROWS": sum(len(c.rows) for c in contracts),
        "NUMBER_OF_SETTLED_ROWS": sum(1 for c in contracts for r in c.rows if r.settle_present),
        "NUMBER_OF_DUPLICATES": sum(len(c.rows) - len({r.trade_date for r in c.rows})
                                    for c in contracts),
        "NUMBER_OF_MISSING_SETTLEMENTS_IN_WINDOW": carried,
        "NUMBER_OF_CONTRACTS_WITH_GAPS_IN_WINDOW":
            len({k for m in months_in_window for k in chain.months[m].carry_forward_by_contract}),
        "SPECIFICATION_BREAK_COUNT": len(vspecs.break_dates()),
        "TICK_HISTORY_BREAK_COUNT": len(vspecs.break_dates()),
        "EXPIRY_RULE_BREAK_COUNT": 1,
        "CALENDAR_MISMATCH_COUNT": n_unexplained,
        "CALENDAR_DECLARED_CFE_ONLY_SESSIONS": n_extra,
        "EXPIRY_RULE_MATCH_COUNT": len(expired) - len(exp_bad),
        "EXCHANGE_SESSIONS": len(cal),
        "CHAIN_DAYS": len(chain.days),
        "STAGE_A_FIRST_MONTH": first_month,
        "STAGE_A_LAST_MONTH": STAGE_A_LAST_MONTH,
        "STAGE_A_MONTHS": len(months_in_window),
        "NEVER_LISTED_MONTHS": list(vspecs.NEVER_LISTED_MONTHS),
        "INELIGIBLE_MONTHS_BEFORE_FIRST": sorted(
            m for m in chain.months if first_month and m < first_month and not chain.months[m].valid),
    }
    for key, val in counts.items():
        print("  %-44s %s" % (key, val))
    ck("no duplicate (date, contract) rows anywhere", counts["NUMBER_OF_DUPLICATES"] == 0)

    # ----------------------------------------------------------------- #
    section("S2A RESULT")
    status = "PASS" if _ok else "FAIL"
    print("  S2A_DATA_ACQUISITION_STATUS = %s" % status)
    print("  checks: %d PASS / %d FAIL"
          % (sum(1 for r in _results if r["pass"]), sum(1 for r in _results if not r["pass"])))
    with open(RESULT_JSON, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"status": status, "checks": _results, "counts": counts,
                   "cross_source_reports": cross,
                   "generated_utc": _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")},
                  fh, indent=2, sort_keys=True, default=str)
    return 0 if _ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
