# -*- coding: utf-8 -*-
"""VRP-PORTFOLIO-DIAGNOSTIC-01 — exploratory fixed-weight portfolio diagnostic.

```
EXPLORATORY_ONLY                    = YES
OUTCOME_EXPOSED_REUSE               = YES
PROMOTION_POWER                     = NONE
DOES_NOT_CHANGE_TSMOM_VRP_01_VERDICT = YES
```

**This is NOT TSMOM-VRP-01 Stage B.** Stage B is barred by the sealed section O stop rule
(a Class-3 Stage A means Stage B never runs) and its confirmatory entry point
`vrp_stage_b.run_stage_b` remains gated and refuses. This module is a SEPARATE,
non-preregistered, descriptive lineage that answers one practical question at ONE
already-fixed allocation:

    what historically happened to the frozen canonical TSMOM book if a fixed 20 %
    capital allocation to the already-tested VRP sleeve is added?

The 20 % share is REUSED because it was fixed (`s = beta / b = 0.20`) before any
historical outcome was seen. It is **not** claimed to be optimal, and no other weight is
tested. No parameter is swept, no tenor is varied, no filter is added, no cost grid is
explored.

The VRP monthly series is the ALREADY-GENERATED, ALREADY-REVEALED sealed historical
Stage-A series, read from the protected store as an input. Reading it again is not a
second reveal: `reveal_count` stays 1. Because it is read after exposure, every number
here is **outcome-exposed exploratory reuse** and can support no confirmatory claim.

Mechanics are the ones acceptance items 13-15 already validated
(`vrp_stage_b.run_book_ledger`), called under this diagnostic namespace.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import math
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(PKG, "..", "..", ".."))
for _p in (REPO, PKG, os.path.join(REPO, "research", "extensions", "value")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
os.chdir(REPO)

import vrp_calendar as vcal      # noqa: E402
import vrp_chain as vchain       # noqa: E402
import vrp_constants as K        # noqa: E402
import vrp_raw as vraw           # noqa: E402
import vrp_reveal as vreveal     # noqa: E402
import vrp_stage_a as vsa        # noqa: E402
import vrp_stage_b as vsb        # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

LINEAGE = "VRP-PORTFOLIO-DIAGNOSTIC-01"

# The one fixed allocation. Reused, not searched.
CORE_SHARE = 0.80
SLEEVE_SHARE = 0.20
W0 = 1_000_000.0

# Upper boundary: the canonical historical core has a complete month only through
# 2026-05 under the existing authority (the frozen panel ends 2026-06-12, so 2026-06 is a
# PARTIAL month and is excluded). Lower boundary is derived MECHANICALLY below.
END_MONTH = "2026-05"

# Deterministic bootstrap seed, DECLARED BEFORE EXECUTION. Deliberately NOT the sealed
# inference seed 7, so a diagnostic stream can never be confused with a sealed one.
DIAG_SEED = 20260914
DIAG_REPS = 10_000
DIAG_BLOCK = 12

# Crisis windows, all ALREADY DESIGN-EXPOSED and fixed before this diagnostic ran
# (VRP_EXPOSURE_DISCLOSURE.md section 3). No window is added after inspecting results.
CRISIS_WINDOWS = [
    ("2008 GFC", "2008-09", "2009-02"),
    ("Feb 2018 vol shock", "2018-02", "2018-02"),
    ("Mar 2020 COVID", "2020-02", "2020-03"),
    ("CY2022", "2022-01", "2022-12"),
    ("Aug 2024 vol episode", "2024-08", "2024-08"),
    ("Apr 2025 vol episode", "2025-04", "2025-04"),
]

MANIFEST_JSON = os.path.join(REPO, "data", "vix", "manifests", "vrp_raw_manifest.json")
DGS3MO = os.path.join(REPO, "data", "DGS3MO.csv")
OUT_JSON = os.path.join(HERE, "VRP_PORTFOLIO_DIAGNOSTIC_01.json")


def git(*a):
    r = subprocess.run(["git"] + list(a), cwd=REPO, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return r.stdout.strip()


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def month_key(ts):
    return "%04d-%02d" % (ts.year, ts.month)


# --------------------------------------------------------------------------- #
# inputs
# --------------------------------------------------------------------------- #
def load_sealed_vrp():
    """The already-generated, already-revealed sealed Stage-A payload, as an INPUT.

    Read straight from the protected store file. This is NOT a second reveal: the
    single authorised reveal is already consumed and `reveal_count` stays 1.
    """
    store = vreveal.PROTECTED_STORE
    files = sorted(os.listdir(store))
    if len(files) != 1:
        raise RuntimeError("expected exactly one protected result, found %d" % len(files))
    with open(os.path.join(store, files[0]), encoding="utf-8") as fh:
        blob = json.load(fh)
    return blob


def load_canonical():
    """The frozen canonical 17-ETF TSMOM book: daily prices, monthly positions, net stream.

    Identity is the sealed Value contract's section 17 comparator, reused verbatim via the
    pinned `value_comparator` module. Nothing about the canonical construction is changed:
    universe, 1/3/6/12 mean-of-signs signal, 60-day vol sizing, asset target, caps, equal
    weighting, portfolio vol target, gross cap, 2 bps costs, liveness and timing are all
    the frozen ones.
    """
    import value_comparator as VC
    if VC.panel_sha256() != VC.PANEL_SHA256:
        raise RuntimeError("ETF panel does not match the pinned hash")
    import config
    import universe
    from src import fetch_data, performance as perf, portfolio, signals

    prices, _ = fetch_data.fetch_universe(force=False)
    px = prices[universe.TICKERS]
    port = portfolio.build_portfolio(
        px, method=VC.SIGNAL_METHOD, agg=VC.AGGREGATION,
        target_vol=config.PORT_TARGET_VOL_ANNUAL,
        vol_window=config.PORT_VOL_WINDOW_DAYS,
        max_gross=config.MAX_GROSS_LEVERAGE)
    positions = port["position"]
    monthly_px = signals.to_monthly(px)
    rets = perf.portfolio_returns(positions, monthly_px,
                                  cost_bps=config.TRANSACTION_COST_BPS)
    asset_w = port["asset_weight"]
    full_decision = asset_w.notna().all(axis=1)
    first_full = full_decision[full_decision].index.min()
    rets = rets.loc[rets.index > first_full]
    return px, positions, rets, config.TRANSACTION_COST_BPS


def build_core_months(px, positions, months):
    """CoreMonth records: daily buy-and-hold unit index, gross fraction, turnover."""
    day_index = list(px.index)
    by_month = {}
    for d in day_index:
        by_month.setdefault(month_key(d), []).append(d)
    ordered_months = sorted(by_month)
    out = []
    for m in months:
        i = ordered_months.index(m)
        if i == 0:
            raise RuntimeError("no prior month for %s" % m)
        start_day = by_month[ordered_months[i - 1]][-1]     # allocation day
        days = by_month[m]
        ts = [t for t in positions.index if month_key(t) == m]
        if not ts:
            raise RuntimeError("no canonical position row for %s" % m)
        p = positions.loc[ts[0]].dropna()
        prev_ts = [t for t in positions.index if month_key(t) < m]
        p_prev = positions.loc[prev_ts[-1]].dropna() if prev_ts else p * 0.0
        turnover = float((p.reindex(p.index.union(p_prev.index)).fillna(0.0)
                          - p_prev.reindex(p.index.union(p_prev.index)).fillna(0.0))
                         .abs().sum())
        p0 = px.loc[start_day, p.index]
        unit_index, gross_fraction = {}, {}
        for d in days:
            rel = (px.loc[d, p.index] / p0)
            idx = 1.0 + float((p * (rel - 1.0)).sum())
            unit_index[d.date()] = idx
            gross_notional_ratio = float((p.abs() * rel).sum())
            gross_fraction[d.date()] = (gross_notional_ratio / idx) if idx else 0.0
        out.append(vsb.CoreMonth(month=m, nyse_days=tuple(d.date() for d in days),
                                 unit_index=unit_index, gross_fraction=gross_fraction,
                                 turnover=turnover))
    return out


def build_sleeve_months(months):
    """SleeveMonth records from the same VX chain the sealed Stage-A run used."""
    with open(MANIFEST_JSON, encoding="utf-8") as fh:
        manifest = json.load(fh)
    contracts, _ = vraw.load_contracts(manifest["contract_files"])
    cal = vraw.exchange_calendar_from(contracts)
    chain = vchain.build_chain(contracts, cal)
    buckets = {}
    for r in chain.days:
        buckets.setdefault(vchain._month_key(r.date), []).append(r)
    out = []
    for m in months:
        rows = buckets.get(m, [])
        if not rows:
            raise RuntimeError("no VX chain days in %s" % m)
        last = rows[-1].date
        days = tuple(vsa.DayInput(date=r.date, front_key=r.front_key,
                                  second_key=r.second_key, w_front=r.w_front,
                                  w_second=r.w_second, front_price=r.front_price,
                                  second_price=r.second_price,
                                  month_end=(r.date == last)) for r in rows)
        out.append(vsb.SleeveMonth(month=m, vx_days=days))
    return out, cal


def fm1_rf(cal, months):
    """Section E.3 FM-1, reused verbatim, for the cash-treatment disclosure."""
    prints = {}
    with open(DGS3MO, encoding="utf-8") as fh:
        fh.readline()
        for line in fh:
            a = line.strip().split(",")
            if len(a) < 2 or not a[1] or a[1] == ".":
                continue
            try:
                prints[_dt.date.fromisoformat(a[0])] = float(a[1])
            except ValueError:
                pass
    out = {}
    for m in months:
        y, mo = int(m[:4]), int(m[5:])
        py, pmo = (y - 1, 12) if mo == 1 else (y, mo - 1)
        try:
            dec = cal.last_session_of_month(py, pmo)
        except KeyError:
            out[m] = None
            continue
        v = None
        for back in range(0, K.FM1_MAX_LOOKBACK_DAYS + 1):
            d = dec - _dt.timedelta(days=back)
            if d in prints:
                v = prints[d] / K.FM1_DIVISOR
                break
        out[m] = v
    return out


# --------------------------------------------------------------------------- #
# metrics
# --------------------------------------------------------------------------- #
def metrics(r):
    """Canonical programme convention, stated explicitly:
        annualised arithmetic mean = 12 * mean(monthly)
        annualised vol             = sqrt(12) * std(monthly, ddof=1)
        Sharpe, rf = 0             = sqrt(12) * mean / std(ddof=1)
        max drawdown from the COMPOUNDED equity curve of the monthly net returns.
    """
    a = np.asarray(list(r), dtype=np.float64)
    mean, sd = float(a.mean()), float(a.std(ddof=1))
    eq = np.cumprod(1.0 + a)
    dd = eq / np.maximum.accumulate(eq) - 1.0
    return {
        "annualised_arithmetic_mean": 12.0 * mean,
        "annualised_vol": math.sqrt(12.0) * sd,
        "sharpe": (math.sqrt(12.0) * mean / sd) if sd > 0 else float("nan"),
        "max_drawdown": float(dd.min()),
        "worst_month": float(a.min()),
        "best_month": float(a.max()),
        "positive_month_fraction": float((a > 0).mean()),
        "n_months": int(a.size),
    }


def sharpe(a):
    a = np.asarray(a, dtype=np.float64)
    sd = a.std(ddof=1)
    return (math.sqrt(12.0) * a.mean() / sd) if sd > 0 else float("nan")


def paired_stationary_bootstrap_delta_sharpe(core, comb, seed=DIAG_SEED,
                                             reps=DIAG_REPS, block=DIAG_BLOCK):
    """Paired stationary block bootstrap on the common monthly sample.

    The SAME resampled month indices are applied to both series in every replicate, so the
    pairing (and hence the dependence between them) is preserved. Geometric blocks with
    expected length `block`, circular wrap, replicate length = sample length.
    """
    c = np.asarray(core, dtype=np.float64)
    b = np.asarray(comb, dtype=np.float64)
    n = c.size
    rng = np.random.Generator(np.random.PCG64(np.random.SeedSequence(seed)))
    p = 1.0 / block
    stats = []
    for _ in range(reps):
        idx = np.empty(n, dtype=np.int64)
        filled = 0
        while filled < n:
            L = int(rng.geometric(p))
            start = int(rng.integers(0, n))
            take = min(L, n - filled)
            idx[filled:filled + take] = (start + np.arange(take)) % n
            filled += take
        stats.append(sharpe(b[idx]) - sharpe(c[idx]))
    arr = np.asarray([s for s in stats if not math.isnan(s)], dtype=np.float64)
    return {
        "point": sharpe(b) - sharpe(c),
        "ci_low": float(np.percentile(arr, 2.5, method="linear")),
        "ci_high": float(np.percentile(arr, 97.5, method="linear")),
        "replicates": reps, "usable": int(arr.size),
        "seed": seed, "block": block,
    }


def window_slice(months, series, lo, hi):
    return [v for m, v in zip(months, series) if lo <= m <= hi]


def compounded(r):
    out = 1.0
    for x in r:
        out *= (1.0 + x)
    return out - 1.0


# --------------------------------------------------------------------------- #
# the diagnostic
# --------------------------------------------------------------------------- #
def main() -> int:
    print("VRP-PORTFOLIO-DIAGNOSTIC-01 - exploratory fixed-weight portfolio diagnostic")
    print("=" * 78)
    print("EXPLORATORY_ONLY=YES  OUTCOME_EXPOSED_REUSE=YES  PROMOTION_POWER=NONE")
    print("This is NOT TSMOM-VRP-01 Stage B and changes no verdict.")
    print("Bootstrap seed declared before execution: %d" % DIAG_SEED)

    blob = load_sealed_vrp()
    payload = blob["payload"]
    vrp_monthly_all = payload["monthly_returns"]
    r1_by_month = payload["descriptives"][
        "R1_gross_carry_points_per_unit_sensitivity_by_month"]

    px, positions, canon, cost_bps = load_canonical()
    canon_map = {month_key(t): float(canon.loc[t, "net"]) for t in canon.index}

    # ---- common sample, derived MECHANICALLY ----
    canon_first = min(canon_map)
    vrp_first = min(vrp_monthly_all)
    start_month = max(canon_first, vrp_first)
    months = [m for m in sorted(set(canon_map) & set(vrp_monthly_all))
              if start_month <= m <= END_MONTH]
    print("")
    print("COMMON SAMPLE (mechanical)")
    print("  canonical first complete scored month = %s" % canon_first)
    print("  VRP first eligible complete month     = %s" % vrp_first)
    print("  START_MONTH = %s   END_MONTH = %s   N_MONTHS = %d"
          % (months[0], months[-1], len(months)))

    expected = []
    y, mo = int(months[0][:4]), int(months[0][5:])
    while "%04d-%02d" % (y, mo) <= months[-1]:
        expected.append("%04d-%02d" % (y, mo))
        mo += 1
        if mo == 13:
            y, mo = y + 1, 1
    assert months == expected, "common sample is not contiguous"

    core_r = [canon_map[m] for m in months]
    vrp_r = [float(vrp_monthly_all[m]) for m in months]

    # ---- COMBINED book, validated ledger mechanics under this namespace ----
    core_months = build_core_months(px, positions, months)
    sleeve_months, vxcal = build_sleeve_months(months)
    book = vsb.run_book_ledger(core_months, sleeve_months, W0)
    assert len(book.months) == len(months)
    comb_r = [m.r_book for m in book.months]
    funding_events = sum(len(m.funding_events) for m in book.months)
    exhausted = any(m.book_exhaustion for m in book.months)

    max_core_err = max(abs(m.r_core - canon_map[m.month]) for m in book.months)
    entry_month = months[0]
    sleeve_errs = {m.month: abs(m.r_A_on_Kt - vrp_monthly_all[m.month])
                   for m in book.months}
    entry_err = sleeve_errs[entry_month]
    max_sleeve_err = max(e for m, e in sleeve_errs.items() if m != entry_month)
    print("")
    print("RECONSTRUCTION GATE  (VRP-DIAG-DEFECT-001 repaired)")
    print("  max abs(ledger r_core - canonical net)                 = %.3e" % max_core_err)
    print("  max abs(ledger r_A(K_t) - sealed r_A), %d carried months = %.3e"
          % (len(months) - 1, max_sleeve_err))
    print("  entry month %s (book starts FLAT; sealed series is mid-stream) = %.3e"
          % (entry_month, entry_err))
    print("  funding events = %d   book_exhaustion = %s" % (funding_events, exhausted))
    if max_core_err > 1e-9 or max_sleeve_err > 1e-9:
        print("")
        print("  DEFECT: the diagnostic could not reproduce a pinned input. STOPPING.")
        return 1
    print("  GATE PASS: every month holding a comparable carried position reconstructs")
    print("  to floating-point. The entry month differs BY CONSTRUCTION - this book")
    print("  establishes the sleeve on its first day and pays that entry cost, while the")
    print("  sealed Stage-A series has held a live position since 2006-09. That one-off")
    print("  entry cost is a real cost of starting the sleeve and is KEPT, not removed.")

    # ---- cash-treatment disclosure ----
    rf = fm1_rf(vxcal, months)
    rf_missing = [m for m in months if rf[m] is None]
    vrp_total = [vrp_r[i] + (rf[m] or 0.0) for i, m in enumerate(months)]
    comb_total = [comb_r[i] + SLEEVE_SHARE * (rf[m] or 0.0) for i, m in enumerate(months)]

    M_core, M_vrp, M_comb = metrics(core_r), metrics(vrp_r), metrics(comb_r)
    M_vrp_tr, M_comb_tr = metrics(vrp_total), metrics(comb_total)

    c = np.asarray(core_r)
    v = np.asarray(vrp_r)
    corr = float(np.corrcoef(c, v)[0, 1])
    cov = float(np.cov(c, v, ddof=1)[0, 1])

    boot = paired_stationary_bootstrap_delta_sharpe(core_r, comb_r)

    # ---- SPY bottom-decile tail, X46 rule ----
    from src import signals as _sig
    spy_m = _sig.to_monthly(px[["SPY"]])["SPY"].pct_change().dropna()
    spy_map = {month_key(t): float(x) for t, x in spy_m.items()}
    spy = [spy_map[m] for m in months]
    q = float(np.quantile(np.asarray(spy), 0.10, method="linear"))
    tail_idx = [i for i, x in enumerate(spy) if x <= q]
    d_diag = float(np.mean([comb_r[i] - core_r[i] for i in tail_idx]))
    tail = {
        "spy_decile_threshold": q, "n_tail_months": len(tail_idx),
        "tail_months": [months[i] for i in tail_idx],
        "mean_core": float(np.mean([core_r[i] for i in tail_idx])),
        "mean_combined": float(np.mean([comb_r[i] for i in tail_idx])),
        "D_diag_mean_difference": d_diag,
        "worst_tail_core": float(min(core_r[i] for i in tail_idx)),
        "worst_tail_combined": float(min(comb_r[i] for i in tail_idx)),
        "mean_vrp_in_tail": float(np.mean([vrp_r[i] for i in tail_idx])),
    }

    crisis = []
    for name, lo, hi in CRISIS_WINDOWS:
        cs = window_slice(months, core_r, lo, hi)
        bs = window_slice(months, comb_r, lo, hi)
        vs = window_slice(months, vrp_r, lo, hi)
        if not cs:
            crisis.append({"window": name, "span": "%s..%s" % (lo, hi),
                           "status": "OUTSIDE_COMMON_SAMPLE"})
            continue
        crisis.append({"window": name, "span": "%s..%s" % (lo, hi), "months": len(cs),
                       "core": compounded(cs), "combined": compounded(bs),
                       "difference": compounded(bs) - compounded(cs),
                       "vrp_sleeve": compounded(vs)})

    # ---- cost diagnostic, from the sealed ledger, no assumption changed ----
    # r_A = (VM - cost)/K and R1 = VM/S with S = 0.01*K, so cost/K = 0.01*R1 - r_A.
    cost_k = [0.01 * float(r1_by_month[m]) - vrp_monthly_all[m] for m in months]
    gross_k = [0.01 * float(r1_by_month[m]) for m in months]
    ann_cost = 12.0 * float(np.mean(cost_k))
    ann_gross = 12.0 * float(np.mean(gross_k))
    ann_net = 12.0 * float(np.mean(vrp_r))
    cost_diag = {
        "annualised_execution_cost_fraction_of_K": ann_cost,
        "annualised_gross_carry_fraction_of_K": ann_gross,
        "annualised_net_excess_fraction_of_K": ann_net,
        "cost_as_fraction_of_gross_carry": (ann_cost / ann_gross) if ann_gross else None,
        "cost_as_fraction_of_net_return": (ann_cost / ann_net) if ann_net else None,
        "convention": "sealed section G, unchanged",
    }

    out = {
        "lineage": LINEAGE,
        "EXPLORATORY_ONLY": "YES", "OUTCOME_EXPOSED_REUSE": "YES",
        "PROMOTION_POWER": "NONE", "DOES_NOT_CHANGE_TSMOM_VRP_01_VERDICT": "YES",
        "TSMOM_VRP_01_HISTORICAL_VERDICT": "UNRESOLVED_CLASS_3",
        "generated_utc": _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "code_commit": git("rev-parse", "HEAD"),
        "inputs": {
            "vrp_protected_result_sha256": blob["sha256"],
            "vrp_reveal_count_unchanged": 1,
            "etf_panel_sha256": K.ETF_PANEL_SHA256,
            "vix_raw_manifest_sha256": sha256_file(MANIFEST_JSON),
            "dgs3mo_sha256": sha256_file(DGS3MO),
            "canonical_comparator": "CANONICAL_17_ETF_TSMOM_BASELINE (Value section 17)",
            "canonical_cost_bps": cost_bps,
        },
        "sample": {"start_month": months[0], "end_month": months[-1],
                   "n_months": len(months),
                   "canonical_first_complete_scored_month": canon_first,
                   "vrp_first_eligible_complete_month": vrp_first,
                   "end_boundary_reason": "canonical core has a complete month only "
                                          "through 2026-05; 2026-06 is partial"},
        "allocation": {"core": CORE_SHARE, "sleeve": SLEEVE_SHARE, "W0": W0,
                       "note": "fixed before outcome exposure (s = beta/b = 0.20); "
                               "not optimised, no other weight tested"},
        "sharpe_convention": "sqrt(12)*mean(monthly net)/std(monthly net, ddof=1), rf = 0",
        "return_definitions": {
            "CORE_ONLY": "canonical net monthly TOTAL return (price-based, rf not added)",
            "VRP_ONLY": "sealed Stage-A monthly EXCESS-OF-CASH return on committed capital",
            "COMBINED": "book return; core earns total return, the sleeve's 20 % collateral "
                        "earns EXCESS-OF-CASH (no cash yield credited)",
            "disclosure": "CORE and VRP sit on DIFFERENT cash bases. Both definitions are "
                          "reported rather than one being invented: the *_total_return "
                          "block credits the FM-1 collateral yield to the sleeve.",
        },
        "core_only": M_core, "vrp_only_excess_of_cash": M_vrp, "combined": M_comb,
        "vrp_only_total_return_fm1": M_vrp_tr, "combined_total_return_fm1": M_comb_tr,
        "fm1_missing_months": rf_missing,
        "dependence": {"monthly_correlation_core_vrp": corr,
                       "monthly_covariance_core_vrp": cov},
        "deltas": {
            "combined_minus_core_sharpe": M_comb["sharpe"] - M_core["sharpe"],
            "combined_minus_core_annual_vol": (M_comb["annualised_vol"]
                                               - M_core["annualised_vol"]),
            "combined_minus_core_max_drawdown": (M_comb["max_drawdown"]
                                                 - M_core["max_drawdown"]),
            "combined_minus_core_annual_mean": (M_comb["annualised_arithmetic_mean"]
                                                - M_core["annualised_arithmetic_mean"]),
        },
        "delta_sharpe_paired_bootstrap": boot,
        "spy_bottom_decile_tail": tail,
        "crisis_windows": crisis,
        "cost_diagnostic": cost_diag,
        "ledger": {"funding_events": funding_events, "book_exhaustion": exhausted,
                   "max_core_reconstruction_error": max_core_err,
                   "max_sleeve_reconstruction_error_carried_months": max_sleeve_err,
                   "entry_month": entry_month,
                   "entry_month_reconstruction_difference": entry_err,
                   "entry_month_note": "the book establishes the sleeve on its first day "
                                       "and bears that one-off entry cost; the sealed "
                                       "Stage-A series has held a live position since "
                                       "2006-09. Structural, disclosed, and NOT removed.",
                   "mean_month_start_reset_cost_on_Kt":
                       float(np.mean([m.reset_cost_on_Kt for m in book.months])),
                   "mechanics": "vrp_stage_b.run_book_ledger, repaired under "
                                "VRP-DIAG-DEFECT-001 (acceptance items 13-15 revalidated "
                                "with a cross-month fixture)"},
    }
    with open(OUT_JSON, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=2, sort_keys=True, default=str)

    def row(label, m):
        print("  %-34s %+9.4f %9.4f %+8.3f %+9.4f %+8.4f %+8.4f %6.1f"
              % (label, m["annualised_arithmetic_mean"], m["annualised_vol"], m["sharpe"],
                 m["max_drawdown"], m["worst_month"], m["best_month"],
                 100 * m["positive_month_fraction"]))

    print("")
    print("=" * 78)
    print("PORTFOLIO METRICS  (same %d months, %s..%s)"
          % (len(months), months[0], months[-1]))
    print("Sharpe = sqrt(12)*mean/std(ddof=1), rf = 0")
    print("=" * 78)
    print("  %-34s %9s %9s %8s %9s %8s %8s %6s"
          % ("", "ann.mean", "ann.vol", "Sharpe", "maxDD", "worst", "best", "pos%"))
    row("CORE_ONLY (canonical TSMOM)", M_core)
    row("VRP_ONLY (excess of cash)", M_vrp)
    row("COMBINED 80/20", M_comb)
    print("  --- cash-treatment alternative (FM-1 collateral yield credited) ---")
    row("VRP_ONLY (total return)", M_vrp_tr)
    row("COMBINED 80/20 (total return)", M_comb_tr)

    print("")
    print("DEPENDENCE AND DELTAS")
    print("  monthly correlation CORE vs VRP      = %+.4f" % corr)
    print("  monthly covariance                   = %+.6e" % cov)
    print("  COMBINED - CORE  Sharpe              = %+.4f"
          % out["deltas"]["combined_minus_core_sharpe"])
    print("  COMBINED - CORE  annual vol          = %+.4f"
          % out["deltas"]["combined_minus_core_annual_vol"])
    print("  COMBINED - CORE  max drawdown        = %+.4f"
          % out["deltas"]["combined_minus_core_max_drawdown"])
    print("  COMBINED - CORE  annual mean         = %+.4f"
          % out["deltas"]["combined_minus_core_annual_mean"])

    print("")
    print("PAIRED STATIONARY BOOTSTRAP - DELTA SHARPE (exploratory)")
    print("  seed %d, %d replicates, expected block %d months, paired months"
          % (boot["seed"], boot["replicates"], boot["block"]))
    print("  DELTA_SHARPE_POINT   = %+.4f" % boot["point"])
    print("  DELTA_SHARPE_CI_95   = [%+.4f, %+.4f]" % (boot["ci_low"], boot["ci_high"]))

    print("")
    print("SPY BOTTOM-DECILE MONTHS (X46 rule, %d months, threshold %+.4f)"
          % (tail["n_tail_months"], tail["spy_decile_threshold"]))
    print("  mean CORE      = %+.4f" % tail["mean_core"])
    print("  mean COMBINED  = %+.4f" % tail["mean_combined"])
    print("  D_diag         = %+.4f  (mean COMBINED - CORE in tail months)"
          % tail["D_diag_mean_difference"])
    print("  worst tail CORE / COMBINED = %+.4f / %+.4f"
          % (tail["worst_tail_core"], tail["worst_tail_combined"]))
    print("  mean VRP sleeve in tail    = %+.4f" % tail["mean_vrp_in_tail"])

    print("")
    print("DECLARED CRISIS WINDOWS (compounded)")
    print("  %-24s %-18s %9s %9s %9s %9s"
          % ("window", "span", "core", "combined", "diff", "vrp"))
    for r in crisis:
        if r.get("status"):
            print("  %-24s %-18s %s" % (r["window"], r["span"], r["status"]))
        else:
            print("  %-24s %-18s %+9.4f %+9.4f %+9.4f %+9.4f"
                  % (r["window"], r["span"], r["core"], r["combined"],
                     r["difference"], r["vrp_sleeve"]))

    print("")
    print("COST DIAGNOSTIC (sealed section G, unchanged)")
    print("  annualised execution cost / K        = %+.5f"
          % cost_diag["annualised_execution_cost_fraction_of_K"])
    print("  annualised gross carry / K           = %+.5f"
          % cost_diag["annualised_gross_carry_fraction_of_K"])
    print("  annualised net excess / K            = %+.5f"
          % cost_diag["annualised_net_excess_fraction_of_K"])
    print("  cost as fraction of GROSS carry      = %6.2f pct"
          % (100 * cost_diag["cost_as_fraction_of_gross_carry"]))
    print("  cost as fraction of NET return       = %6.2f pct"
          % (100 * cost_diag["cost_as_fraction_of_net_return"]))
    print("")
    print("  artifact: %s" % os.path.relpath(OUT_JSON, REPO).replace("\\", "/"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
