"""CTA-EDGE-04-MMV — the single authorized PRIMARY HISTORICAL RETURN run (S3).

    python research/extensions/mmv/mmv_s3_run.py --preflight   # spends nothing
    python research/extensions/mmv/mmv_s3_run.py --execute     # spends the trial

Authorized by MMV-AUTH-0002 under run_id MMV-S3-20260917-01, read from COMMITTED
git state. The bootstrap seed is fixed mechanically from the S1 seal hash and is
never chosen from an outcome.

PHASES, in order, each a hard stop:

    0  AUTHORIZATION   the committed grant, run_id, scope, seed derivation, and
                       every pinned input hash including the canonical prices
    1  PRE-RUN STATE   the ACCEPTED Gate 0.5 PASS is READ, never recomputed; the
                       consumed MMV-AUTH-0001 must still be consumed; the sealed
                       execution convention must resolve to exactly one authority
    2  SEALED SIGNAL   the sealed MMV directions, rebuilt with the COMMITTED
                       Gate-0.5 constructor and checked against the Gate-0.5
                       structural fingerprint. No canonical TSMOM sign is read.
    3  STRUCTURAL      the section-11 sanity gate: alignment, lag, causality,
                       truncation invariance. Aborts BEFORE any return value.
    4  RETURN SERIES   ONE gross and ONE net monthly series, reconciled against
                       the canonical src/performance.py implementation
    5  INFERENCE       one calendar-year block bootstrap, one draw set, three
                       statistics: Gate 1, M1, M2
    6  VERDICT         the sealed first-match classification and the artifact

Phases 0-3 touch no return. A failure there spends nothing.

--preflight runs 0-3 and stops. It is repeatable and consumes no authorization,
because no primary historical return result is produced.

FIREWALL. This module computes NO per-ETF return, NO per-leg PnL, NO drawdown,
NO hit rate, NO rolling Sharpe, NO alternative cost, lookback, mapping, series
or start date, and does NOT run the first-release concordance diagnostic.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
os.chdir(REPO)
for p in (REPO, HERE):
    if p not in sys.path:
        sys.path.insert(0, p)

import config                                                    # noqa: E402
from src import performance as perf                              # noqa: E402
from src import signals as canonical_signals                     # noqa: E402
from engine import risk, votes                                   # noqa: E402
from engine.pit import UNDEFINED                                 # noqa: E402
import mmv_authorization                                         # noqa: E402
import mmv_gate05_run as g05                                     # noqa: E402

RUN_ID = "MMV-S3-20260917-01"
AUTHORIZATION_ID = "MMV-AUTH-0002"
RUN_TYPE = "PRIMARY_HISTORICAL_RETURN"
SCOPE = "ONE_SHOT_SINGLE_PRIMARY_RETURN_RUN"
LINEAGE = "CTA-EDGE-04-MMV"

#: Section 3. Derived from the S1 seal hash, not chosen.
SEAL_SHA = "75016e778ad58e8fe16e4833cf91c19eb52448b4d42138ab265460f371e8c0d5"
RNG_SEED = int(SEAL_SHA[:8], 16)              # 0x75016e77 = 1963028087

BOOTSTRAP_B = 10_000
CI_LOWER_PCT, CI_UPPER_PCT = 2.5, 97.5
M2_TARGET = 0.30
MONTHS_PER_YEAR = 12

#: Floating-point identity bound for the canonical-implementation
#: reconciliation in phase 4. NOT a research threshold: no gate, class or
#: verdict reads it, and it is ~9 orders of magnitude below a monthly return.
RECON_TOL = 1e-12

OUT_DIR = os.path.join("research", "extensions", "mmv", "s3")
RESULT_JSON = os.path.join(OUT_DIR, "MMV_S3_RESULT.json")

PRICES = "data/close_prices_raw.csv"
GATE05_JSON = "research/extensions/mmv/gate05/MMV_GATE05_RESULT.json"

#: Every input this run may read. The Gate-0.5 set, plus the canonical price
#: panel (new at S3) and the accepted Gate-0.5 result it must not recompute.
PINNED = dict(g05.PINNED)
PINNED.update({
    PRICES: "",                # filled at phase 0 from the sealed manifest
    GATE05_JSON:
        "1fa8df006574199cef2a6153f57f354d6fa93475b07c5c576036cebb09b6c3d8",
    "research/extensions/mmv/MMV_GATE05_RESULT.md":
        "05e20ef8740ccd55b051c4be31b0b85e1b38e9479ef703009037dcd1d8062440",
    "research/extensions/mmv/MMV_GATE05_AUDIT.md":
        "029a5618182a9043680f14102b57de25386ce6bf87569c717d3520185fbee713",
})

#: The Gate-0.5 structural fingerprint the S3 signal reconstruction must
#: reproduce EXACTLY. Checking these recomputes no agreement statistic: not one
#: canonical TSMOM sign is read anywhere in this module.
GATE05_FINGERPRINT = {
    "decision_months": 218,
    "defined_cells": 3270,
    "undefined_cells": 0,
    "zero_cells": 718,
    "legs_defined": {"G": 218, "I": 218, "P": 218},
}

#: Truncation dates for the causality test (phase 3). Month-ends, spread across
#: the sample, chosen structurally and never from an outcome.
TRUNCATION_DATES = ("2011-06-30", "2015-12-31", "2019-09-30", "2023-03-31")


class Stop(RuntimeError):
    """A hard stop. Never caught, never softened into a default."""


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def say(msg=""):
    print(msg, flush=True)


def seal_manifest_hash(relpath):
    """The sha256 the SEALED manifest pins for ``relpath``.

    Read from the seal rather than restated here, so a price panel that moved
    after the seal is a structural stop instead of a number I typed twice.
    """
    with open("research/extensions/mmv/MMV_SEAL_MANIFEST.md", encoding="utf-8") as fh:
        text = fh.read()
    want = None
    for line in text.splitlines():
        if relpath in line:
            for tok in line.replace("|", " ").replace("`", " ").split():
                if len(tok) == 64 and all(c in "0123456789abcdef" for c in tok):
                    if want is not None and want != tok:
                        raise Stop("two different hashes for %s in the seal"
                                   % relpath)
                    want = tok
    if want is None:
        raise Stop("the sealed manifest pins no hash for %s" % relpath)
    return want


# =========================================================================== #
# PHASE 0 — AUTHORIZATION
# =========================================================================== #

def phase0(execute):
    say("=" * 78)
    say("CTA-EDGE-04-MMV — S3 PRIMARY HISTORICAL RETURN RUN")
    say("=" * 78)
    say("PHASE 0 — AUTHORIZATION")

    if os.path.exists(RESULT_JSON):
        raise Stop("a primary return result already exists at %s; the grant is "
                   "CONSUMED and no rerun is authorized" % RESULT_JSON)

    grant = mmv_authorization.active_grant()
    if grant.get("authorization_id") != AUTHORIZATION_ID:
        raise Stop("the live grant is %r, not %r"
                   % (grant.get("authorization_id"), AUTHORIZATION_ID))
    if grant.get("scope") != SCOPE:
        raise Stop("grant scope %r does not authorize a primary return run"
                   % grant.get("scope"))
    binding = grant["binding"]
    if binding.get("run_id") != RUN_ID:
        raise Stop("grant %s authorizes run_id %r, not %r"
                   % (AUTHORIZATION_ID, binding.get("run_id"), RUN_ID))

    # The seed is DERIVED, and the derivation is checked rather than trusted.
    if binding.get("rng_seed") != RNG_SEED:
        raise Stop("grant rng_seed %r != the seal-derived %r"
                   % (binding.get("rng_seed"), RNG_SEED))
    if sha256_file("research/extensions/mmv/MMV_SEAL_MANIFEST.md") != SEAL_SHA:
        raise Stop("the S1 seal manifest does not reproduce its pinned hash")
    if RNG_SEED != int(SEAL_SHA[:8], 16):
        raise Stop("seed derivation broken")

    PINNED[PRICES] = seal_manifest_hash(PRICES)

    bad = []
    for path, want in sorted(PINNED.items()):
        if not os.path.exists(path):
            bad.append("%s MISSING" % path)
            continue
        got = sha256_file(path)
        if got != want:
            bad.append("%s hash %s != pinned %s" % (path, got[:16], want[:16]))
    if bad:
        raise Stop("pinned input mismatch, which is a STRUCTURAL STOP and "
                   "never a substitution:\n   " + "\n   ".join(bad))

    say("  grant            %s  (%s)" % (AUTHORIZATION_ID, SCOPE))
    say("  run_id           %s" % RUN_ID)
    say("  rng_seed         %d   = int(seal[:8], 16), seal %s.."
        % (RNG_SEED, SEAL_SHA[:8]))
    say("  bootstrap B      %d   calendar-year blocks, 95%% percentile"
        % BOOTSTRAP_B)
    say("  pinned inputs    %d / %d reproduce exactly" % (len(PINNED),
                                                          len(PINNED)))
    say("  mode             %s" % ("EXECUTE (spends the primary return trial)"
                                   if execute else "PREFLIGHT (spends nothing)"))
    say("  AUTHORIZED")
    say()
    return grant


# =========================================================================== #
# PHASE 1 — PRE-RUN STATE
# =========================================================================== #

def phase1():
    say("PHASE 1 — PRE-RUN STATE")

    with open(GATE05_JSON, encoding="utf-8") as fh:
        g = json.load(fh)
    if g["gate05"]["result"] != "PASS" or g["gate05"]["kill"]:
        raise Stop("the accepted Gate 0.5 artifact does not carry a PASS")
    if g["firewall"]["RETURN_OUTCOME_ACCESSED"]:
        raise Stop("the Gate 0.5 artifact claims returns were accessed")
    say("  gate 0.5         READ from the committed artifact, never recomputed")
    say("                   %s = %s, kill=%s"
        % (g["gate05"]["pooled_agreement_exact"], g["gate05"]["result"],
           g["gate05"]["kill"]))

    consumed = mmv_authorization.consumed_ids()
    if "MMV-AUTH-0001" not in consumed:
        raise Stop("MMV-AUTH-0001 is no longer marked CONSUMED; the Gate 0.5 "
                   "rerun guard has been weakened")
    say("  MMV-AUTH-0001    still CONSUMED -> no Gate 0.5 rerun is possible")

    # ---- section 7: the execution convention must resolve to ONE authority --
    src = open(os.path.join(REPO, "src", "performance.py"), encoding="utf-8").read()
    need = [
        ("monthly close-to-close asset return",
         "return monthly_prices.pct_change()"),
        ("position held during M = weight decided at M-1",
         "positions.diff().abs().sum(axis=1, min_count=1)"),
        ("gross = held position x month return",
         'gross = (positions * rets).sum(axis=1, min_count=1)'),
        ("net = gross - cost, once",
         "net = gross - cost"),
    ]
    missing = [name for name, frag in need if frag not in src]
    if missing:
        raise Stop("the canonical execution convention could not be recovered "
                   "from src/performance.py: %s" % missing)
    shift_src = open(os.path.join(REPO, "src", "portfolio.py"),
                     encoding="utf-8").read()
    if "return port_weights.shift(1)" not in shift_src:
        raise Stop("the canonical shift(1) execution lag is not where the "
                   "contract says it is")
    if config.SIGNAL_RESAMPLE != "ME":
        raise Stop("canonical resample rule changed")
    if config.TRANSACTION_COST_BPS != 2.0:
        raise Stop("sealed cost authority changed")

    say("  return interval  MONTH-END CLOSE -> MONTH-END CLOSE, label ME")
    say("                   src/signals.py::to_monthly + "
        "src/performance.py::monthly_asset_returns")
    say("  execution lag    position held during M = portfolio weight decided")
    say("                   at month-end M-1  (src/portfolio.py shift(1))")
    say("  cost             %.1f bps one-way x turnover, charged in the month"
        % config.TRANSACTION_COST_BPS)
    say("                   the trade executes, subtracted ONCE")
    say("  UNIQUELY DETERMINED — nothing invented")
    say()
    return g


# =========================================================================== #
# PHASE 2 — THE SEALED MMV SIGNAL
# =========================================================================== #

def phase2():
    say("PHASE 2 — SEALED MMV DIRECTIONS  (committed Gate-0.5 constructor)")
    say("  re-invoking mmv_gate05_run.phase2 verbatim; no agreement statistic")
    say("  is formed and no canonical TSMOM sign is read anywhere in S3.")
    say()

    allm, dec = g05.decision_dates()
    schedule, _rows = g05.load_schedule()
    series = g05.build_series()
    raw, leg_rows, defined_legs, undef_reason, _lag, _same = \
        g05.phase2(dec, allm, series, schedule)

    defined = sum(1 for v in raw.values() if v is not UNDEFINED)
    undef = sum(1 for v in raw.values() if v is UNDEFINED)
    zeros = sum(1 for v in raw.values() if v == 0)
    fp = {"decision_months": len(dec), "defined_cells": defined,
          "undefined_cells": undef, "zero_cells": zeros,
          "legs_defined": defined_legs}
    if fp != GATE05_FINGERPRINT:
        raise Stop("the S3 signal reconstruction does not reproduce the Gate "
                   "0.5 structural fingerprint.\n   got  %s\n   want %s"
                   % (fp, GATE05_FINGERPRINT))
    say("  fingerprint      months=%d defined=%d undefined=%d zero=%d "
        "legs G/I/P=%d/%d/%d" % (fp["decision_months"], fp["defined_cells"],
                                 fp["undefined_cells"], fp["zero_cells"],
                                 defined_legs["G"], defined_legs["I"],
                                 defined_legs["P"]))
    say("  IDENTICAL to the accepted Gate 0.5 run. Same directions, same "
        "sample.")
    say()
    return dec, raw, undef_reason


# =========================================================================== #
# PHASE 3 — STRUCTURAL SANITY  (before any return VALUE)
# =========================================================================== #

def load_prices():
    px = pd.read_csv(PRICES, index_col=0, parse_dates=True)
    return px.sort_index()


def build_book(raw, dates, prices):
    """The sealed directions through the canonical wrapper, unchanged."""
    signal = risk.signal_frame(raw, dates=dates)
    return risk.build(prices, signal), signal


def phase3(dec, raw, prices):
    say("PHASE 3 — STRUCTURAL SANITY GATE  (no return value exists yet)")
    problems = []

    idx = pd.DatetimeIndex([pd.Timestamp(d) for d in dec])
    book, signal = build_book(raw, idx, prices)
    port_w = book["port_weight"]
    held = book["position"]

    # --- the alpha domain ---------------------------------------------------
    if sorted(signal.columns) != sorted(votes.MAPPED) or signal.shape[1] != 15:
        problems.append("the signal frame is not the sealed 15 instruments")
    if set(signal.columns) & votes.NOT_MAPPED:
        problems.append("VNQ/RWX reached the MMV book")

    # --- the decision index must be contiguous month-ends --------------------
    if not idx.is_unique:
        problems.append("duplicate decision month")
    if not idx.is_monotonic_increasing:
        problems.append("decision dates are not ordered")
    expect = pd.date_range(idx[0], idx[-1], freq="ME")
    if not idx.equals(expect):
        problems.append("the decision index is not a contiguous month-end grid; "
                        "shift(1) would silently span a gap")

    # --- execution lag: held(M) must BE the weight decided at M-1 ------------
    lag_ok = port_w.iloc[:-1].reset_index(drop=True).equals(
        held.iloc[1:].reset_index(drop=True))
    if not lag_ok:
        problems.append("held(M) != port_weight(M-1): the execution lag is not "
                        "exactly one month")

    # --- monthly prices and the return grid ---------------------------------
    monthly_px = canonical_signals.to_monthly(prices[sorted(votes.MAPPED)])
    rets = perf.monthly_asset_returns(monthly_px)
    if not idx.isin(monthly_px.index).all():
        problems.append("a decision month-end is absent from the canonical "
                        "monthly price grid")

    # --- eligible return months, derived not chosen -------------------------
    live = held.notna().any(axis=1)
    cand = [d for d in idx if bool(live.get(d, False))]
    missing_ret = []
    for d in cand:
        cols = held.loc[d].dropna().index
        if d not in rets.index or rets.loc[d, cols].isna().any():
            missing_ret.append(d)
    if missing_ret:
        problems.append("%d eligible months have a missing asset return: %s"
                        % (len(missing_ret), [str(x.date()) for x in missing_ret[:3]]))
    elig = pd.DatetimeIndex(cand)

    warmup = [d for d in idx if d not in elig]
    if warmup != list(idx[:len(warmup)]):
        problems.append("months without a book are not a contiguous warm-up")

    # --- full-universe check: MMV never trades a partial book ---------------
    aw = book["asset_weight"]
    partial = int((~aw.notna().all(axis=1)).sum())
    if partial:
        problems.append("%d decision months carry fewer than 15 sized weights"
                        % partial)

    # --- causality: truncation invariance of the whole wrapper --------------
    trunc_report = []
    for t in TRUNCATION_DATES:
        T = pd.Timestamp(t)
        sub_raw = {k: v for k, v in raw.items() if pd.Timestamp(k[0]) <= T}
        sub_idx = idx[idx <= T]
        sub_book, _ = build_book(sub_raw, sub_idx, prices.loc[:T])
        same = []
        for key in ("asset_vol", "asset_weight", "port_weight"):
            a = book[key].loc[:T]
            b = sub_book[key].loc[:T]
            same.append(a.equals(b))
        pv_a, pv_b = book["port_vol"].loc[:T], sub_book["port_vol"].loc[:T]
        same.append(pv_a.equals(pv_b))
        ok = all(same)
        trunc_report.append((t, ok))
        if not ok:
            problems.append("truncation invariance FAILED at %s: the wrapper "
                            "uses information after the decision date" % t)

    say("  mapped instruments        %d   VNQ present: NO   RWX present: NO"
        % signal.shape[1])
    say("  decision months           %d, contiguous month-ends, no duplicates"
        % len(idx))
    say("  sized weights             all 15 present on every decision month"
        if not partial else "  sized weights             PARTIAL BOOK")
    say("  execution lag             held(M) == port_weight(M-1)  EXACT")
    say("  wrapper warm-up           %d months with no book (%s)"
        % (len(warmup),
           ", ".join(str(d.date()) for d in warmup) if warmup else "none"))
    say("                            portfolio vol needs %d daily base returns"
        % config.PORT_VOL_WINDOW_DAYS)
    say("  eligible return months    %d   %s .. %s"
        % (len(elig), elig[0].date(), elig[-1].date()))
    say("  missing returns           0 unexplained")
    say("  truncation invariance     %s"
        % "  ".join("%s:%s" % (t, "OK" if ok else "FAIL")
                    for t, ok in trunc_report))
    say("                            vol, weights and leverage recomputed on a "
        "truncated panel are BITWISE identical")

    if problems:
        say()
        for p in problems:
            say("  PROBLEM: %s" % p)
        raise Stop("S3_STATUS = HOLD_STRUCTURAL")
    say("  STRUCTURAL SANITY PASSED")
    say()
    return book, signal, monthly_px, rets, elig, warmup


# =========================================================================== #
# PHASE 4 — THE PRIMARY RETURN SERIES
# =========================================================================== #

def phase4(book, monthly_px, rets, elig):
    say("PHASE 4 — PRIMARY MONTHLY RETURN SERIES")
    held = book["position"]

    r = rets.reindex_like(held)
    gross_full = (held * r).sum(axis=1, min_count=1)

    # Turnover of the trade EXECUTED at the start of month M: the book moves
    # from what was held in M-1 to what was decided at M-1. An absent book is
    # FLAT, exactly as engine/risk.py::turnover has defined it since the sealed
    # S2 build, so the entry trade is charged in full rather than dropped.
    prior = held.shift(1)
    turn_full = (held.fillna(0.0) - prior.fillna(0.0)).abs().sum(axis=1)
    cost_full = turn_full * (config.TRANSACTION_COST_BPS / 1e4)
    net_full = gross_full - cost_full

    gross = gross_full.reindex(elig)
    turn = turn_full.reindex(elig)
    cost = cost_full.reindex(elig)
    net = net_full.reindex(elig)

    # ---- reconciliation against the CANONICAL implementation ---------------
    # NUMERICAL IDENTITY, not bit-identity. `sum(axis=1)` and
    # `sum(axis=1, min_count=1)` are the same formula down different pandas
    # reduction paths and can differ by one ULP. RECON_TOL is a floating-point
    # identity bound, NOT a research threshold: nothing is classified,
    # accepted or rejected by it, and it sits ~9 orders of magnitude below the
    # smallest quantity any gate reads. The observed deviations are recorded.
    canon = perf.portfolio_returns(held, monthly_px,
                                   cost_bps=config.TRANSACTION_COST_BPS)
    canon0 = perf.portfolio_returns(held, monthly_px, cost_bps=0.0)
    defined = canon["turnover"].reindex(elig).notna()

    def dev(a, b):
        return float((a - b).abs().max())

    deviations = {
        "gross_vs_canonical": dev(canon["gross"].reindex(elig), gross),
        "gross_vs_canonical_zero_cost": dev(canon0["gross"].reindex(elig), gross),
        "turnover_vs_canonical": dev(canon["turnover"].reindex(elig)[defined],
                                     turn[defined]),
        "net_vs_canonical": dev(canon["net"].reindex(elig)[defined],
                                net[defined]),
    }
    problems = []
    for name, d in sorted(deviations.items()):
        if not (d <= RECON_TOL):
            problems.append("%s deviates by %.3e, above the identity bound %.0e"
                            % (name, d, RECON_TOL))
    boundary = [str(d.date()) for d in elig[~defined]]
    if len(boundary) > 1:
        problems.append("more than one canonical-undefined turnover month: %s"
                        % boundary)
    if gross.isna().any() or net.isna().any() or cost.isna().any():
        problems.append("NaN inside the eligible primary series")
    # These two are true by construction; they are here so that a later edit
    # that breaks them cannot pass silently. The NON-vacuous accounting check
    # is the canonical reconciliation above: gross at 0 bps == gross at 2 bps
    # == this gross, which is what "cost applied once" actually means.
    if not np.array_equal((gross - cost - net).to_numpy(), np.zeros(len(elig))):
        problems.append("net != gross - cost")
    if not np.array_equal(
            cost.to_numpy(),
            (turn * (config.TRANSACTION_COST_BPS / 1e4)).to_numpy()):
        problems.append("cost != turnover x sealed one-way rate")

    say("  eligible months           %d" % len(elig))
    say("  gross series              (held weight) x (month-end to month-end "
        "asset return)")
    say("  canonical reconciliation  gross, turnover, net vs src/performance.py")
    for name, d in sorted(deviations.items()):
        say("     %-32s max |dev| = %.3e" % (name, d))
    say("  entry-trade boundary      %s  (canonical turnover is NaN there; the "
        % (boundary[0] if boundary else "none"))
    say("                            sealed S2 rule charges the full entry "
        "trade instead)")
    say("  cost applied              ONCE  (gross at 0 bps == gross at %.1f bps)"
        % config.TRANSACTION_COST_BPS)
    say("  aggregate turnover        %.4f   mean %.6f / month"
        % (turn.sum(), turn.mean()))
    say("  aggregate cost            %.6f   mean %.8f / month"
        % (cost.sum(), cost.mean()))

    if problems:
        say()
        for p in problems:
            say("  PROBLEM: %s" % p)
        raise Stop("S3_STATUS = HOLD_STRUCTURAL")
    say("  RETURN ACCOUNTING RECONCILES")
    say()
    return gross, turn, cost, net, boundary, deviations


# =========================================================================== #
# PHASE 5 — INFERENCE
# =========================================================================== #

def percentile_interval(point, draws):
    """The BENB convention (research/extensions/benb/benb_inference.py), which
    is the established calendar-year block-bootstrap interval in this
    programme: percentile endpoints at 2.5 / 97.5 over the finite replicates."""
    vals = np.asarray([v for v in draws if np.isfinite(v)], dtype=float)
    if vals.size == 0:
        raise Stop("every bootstrap replicate was non-finite")
    return {"point": float(point),
            "lower": float(np.percentile(vals, CI_LOWER_PCT)),
            "upper": float(np.percentile(vals, CI_UPPER_PCT)),
            "valid_replicates": int(vals.size),
            "replicates": BOOTSTRAP_B}


def sharpe(net_values):
    sd = float(np.std(net_values, ddof=1))
    if sd == 0.0:
        return float("nan")
    return float(np.mean(net_values)) / sd * float(np.sqrt(MONTHS_PER_YEAR))


def phase5(gross, net):
    say("PHASE 5 — INFERENCE  (one bootstrap, one draw set, three statistics)")

    years = sorted({int(d.year) for d in gross.index})
    g_by = {y: gross[gross.index.year == y].to_numpy() for y in years}
    n_by = {y: net[net.index.year == y].to_numpy() for y in years}
    n = len(years)

    rng = np.random.Generator(np.random.PCG64(np.random.SeedSequence(RNG_SEED)))
    draws = rng.integers(0, n, size=(BOOTSTRAP_B, n))

    point = {"gross_mean": float(gross.mean()),
             "net_mean": float(net.mean()),
             "net_sharpe": sharpe(net.to_numpy())}
    acc = {k: np.empty(BOOTSTRAP_B) for k in point}
    for b, row in enumerate(draws):
        gv = np.concatenate([g_by[years[j]] for j in row])
        nv = np.concatenate([n_by[years[j]] for j in row])
        acc["gross_mean"][b] = gv.mean()
        acc["net_mean"][b] = nv.mean()
        acc["net_sharpe"][b] = sharpe(nv)

    out = {k: percentile_interval(point[k], acc[k]) for k in point}

    say("  calendar-year blocks      %d  (%d .. %d), %d months"
        % (n, years[0], years[-1], len(gross)))
    say("  block sizes               %s"
        % ", ".join("%d:%d" % (y, len(g_by[y])) for y in years))
    say("  replicates                B = %d, one common draw set" % BOOTSTRAP_B)
    say("  rng                       numpy PCG64, SeedSequence(%d)" % RNG_SEED)
    say()
    return out, years, {y: len(g_by[y]) for y in years}


# =========================================================================== #
# PHASE 6 — GATES AND THE SEALED CLASSIFICATION
# =========================================================================== #

def classify(g1, m1, m2):
    """Contract section K, FIRST MATCH WINS. Gate 0.5 already survived, so
    CLASS B cannot match; CLASS A is a structural stop handled by phases 0-4."""
    if g1["upper"] <= 0.0:
        return ("C", "PREDICTIVE RESPONSE RELIABLY ABSENT / ADVERSE",
                "NOT_PROMOTED", "PREDICTIVE_RESPONSE_ABSENT_OR_ADVERSE")
    if g1["lower"] <= 0.0:                      # spans zero
        return ("D", "PREDICTIVE RESPONSE UNRESOLVED",
                "UNRESOLVED / LOW_POWER", "NONE")
    if m1["upper"] <= 0.0 or m2["upper"] <= M2_TARGET:
        return ("E", "PRESENT BUT ECONOMIC TARGET EXCLUDED",
                "NOT_PROMOTED", "TARGET_MARGIN_EXCLUDED")
    if m1["lower"] <= 0.0 or m2["lower"] <= M2_TARGET:
        return ("F", "ECONOMIC USEFULNESS UNRESOLVED",
                "UNRESOLVED / LOW_POWER", "NONE")
    return ("S", "SUPPORTED MMV EDGE", "SUPPORTED", "NONE")


def phase6(res, gross, turn, cost, net, elig, years, block, warmup,
           boundary, gate05, deviations):
    say("PHASE 6 — GATES AND SEALED CLASSIFICATION")
    g1, m1, m2 = res["gross_mean"], res["net_mean"], res["net_sharpe"]

    gate1 = "PASS" if g1["lower"] > 0.0 else "FAIL"
    m1r = "PASS" if m1["lower"] > 0.0 else "FAIL"
    m2r = "PASS" if m2["lower"] > M2_TARGET else "FAIL"
    cls, label, status, failure = classify(g1, m1, m2)

    say("  GATE 1  gross mean    %+.8f   95%% [%+.8f, %+.8f]   %s"
        % (g1["point"], g1["lower"], g1["upper"], gate1))
    say("  M1      net mean      %+.8f   95%% [%+.8f, %+.8f]   %s"
        % (m1["point"], m1["lower"], m1["upper"], m1r))
    say("  M2      net Sharpe    %+.6f     95%% [%+.6f, %+.6f]   %s"
        % (m2["point"], m2["lower"], m2["upper"], m2r))
    say()
    say("  TERMINAL CLASS   %s — %s" % (cls, label))
    say("  PROGRAMME_STATUS %s" % status)
    say("  FAILURE_TYPE     %s" % failure)
    say("  EVIDENCE CEILING supported   (never confirmed)")
    say()

    result = {
        "schema": {"name": "mmv-s3-result", "version": 1},
        "lineage": LINEAGE,
        "run_id": RUN_ID,
        "run_type": RUN_TYPE,
        "authorization_id": AUTHORIZATION_ID,
        "executed_utc": dt.datetime.now(dt.timezone.utc)
                          .strftime("%Y-%m-%dT%H:%M:%SZ"),
        "rng_seed": RNG_SEED,
        "rng_seed_derivation": "int(S1 seal manifest sha256[:8], 16) = "
                               "int('%s', 16)" % SEAL_SHA[:8],
        "rng_stream": "numpy PCG64 via SeedSequence(%d); ONE draw matrix of "
                      "shape (B, n_years) serves Gate 1, M1 and M2" % RNG_SEED,
        "inputs": {p: sha256_file(p) for p in sorted(PINNED)},
        "gate05_accepted": {
            "result": gate05["gate05"]["result"],
            "pooled_agreement_exact": gate05["gate05"]["pooled_agreement_exact"],
            "recomputed_at_s3": False,
        },
        "execution_convention": {
            "return_interval": "month-end close to month-end close, labelled "
                               "ME (src/signals.py::to_monthly)",
            "asset_return": "src/performance.py::monthly_asset_returns = "
                            "monthly_prices.pct_change()",
            "execution_lag": "position held during month M = portfolio weight "
                             "decided at month-end M-1 "
                             "(src/portfolio.py::positions_from_weights, shift(1))",
            "information_cutoff": "15:45:00 America/New_York on the decision "
                                  "date (contract section C)",
            "cost_rule": "%.1f bps one-way x turnover, charged in the month the "
                         "trade executes, subtracted from gross exactly once"
                         % config.TRANSACTION_COST_BPS,
            "entry_trade_boundary_month": boundary[0] if boundary else None,
            "entry_trade_rule": "the canonical positions.diff() is undefined "
                                "at the first held month; the sealed S2 rule "
                                "engine/risk.py::turnover treats an absent "
                                "book as FLAT, so the entry trade is charged "
                                "in full (the conservative direction)",
            "uniquely_determined_by_sealed_authority": True,
            "invented_convention": False,
        },
        "sample": {
            "decision_months": 218,
            "eligible_return_months": len(elig),
            "first_return_month": str(elig[0].date()),
            "last_return_month": str(elig[-1].date()),
            "wrapper_warmup_months_excluded": [str(d.date()) for d in warmup],
            "last_month_is_truncated_to_the_frozen_panel":
                "the frozen daily panel ends 2026-06-12, so the final return "
                "month 2026-06-30 spans a partial month. Contract section H "
                "forbids extending the window past the authoritative panel.",
            "mapped_instruments": sorted(votes.MAPPED),
            "mapped_instrument_n": 15,
            "unmapped": sorted(votes.NOT_MAPPED),
            "calendar_year_blocks": years,
            "block_months": {str(k): v for k, v in block.items()},
        },
        "risk_wrapper": dict(risk.WRAPPER_AUTHORITY),
        "cost_accounting": {
            "one_way_bps": config.TRANSACTION_COST_BPS,
            "aggregate_turnover": float(turn.sum()),
            "mean_monthly_turnover": float(turn.mean()),
            "aggregate_cost": float(cost.sum()),
            "mean_monthly_cost": float(cost.mean()),
            "reconciles_with_canonical_implementation": True,
            "canonical_reconciliation_max_abs_deviation": deviations,
            "reconciliation_identity_bound": RECON_TOL,
            "reconciliation_bound_is_not_a_research_threshold": True,
        },
        "inference": {
            "method": "calendar-year block bootstrap over FROZEN monthly "
                      "strategy tuples; complete calendar years resampled with "
                      "replacement; the PIT macro signal is computed once on "
                      "the true chronology and never rebuilt inside a replicate",
            "B": BOOTSTRAP_B,
            "interval": "95% percentile (2.5 / 97.5)",
            "common_draw_set": True,
            "hac_or_second_bootstrap": False,
        },
        "gate1": {"statistic": "mean monthly GROSS MMV portfolio return",
                  "rule": "lower 95% endpoint > 0, STRICT",
                  "result": gate1, **g1},
        "m1": {"statistic": "mean monthly NET MMV portfolio return",
               "rule": "lower 95% endpoint > 0, STRICT",
               "result": m1r, **m1},
        "m2": {"statistic": "annualised NET Sharpe, rf = 0, ddof = 1, x sqrt(12)",
               "rule": "lower 95%% endpoint > %+.2f, STRICT" % M2_TARGET,
               "target": M2_TARGET, "result": m2r, **m2},
        "verdict": {
            "terminal_class": cls,
            "class_label": label,
            "programme_status": status,
            "failure_type": failure,
            "evidence_ceiling": "supported",
            "never": ["confirmed", "independently confirmed"],
            "classification_rule": "contract section K, FIRST MATCH WINS",
        },
        "firewall": {
            "RETURN_OUTCOME_ACCESSED": True,
            "PRIMARY_RETURN_TRIAL_SPENT": True,
            "FIRST_RELEASE_DIAGNOSTIC_RUN": False,
            "PER_INSTRUMENT_RETURN_DIAGNOSTICS_RUN": False,
            "PER_LEG_RETURN_DIAGNOSTICS_RUN": False,
            "ALTERNATIVE_PARAMETER_CELL_RUN": False,
            "DRAWDOWN_COMPUTED": False,
            "HIT_RATE_COMPUTED": False,
            "ROLLING_SHARPE_COMPUTED": False,
            "BEST_WORST_PERIOD_COMPUTED": False,
            "ALTERNATIVE_COST_RUN": False,
            "ALTERNATIVE_START_DATE_RUN": False,
            "GATE05_RERUN": False,
            "RESCUE_ANALYSIS_PERFORMED": False,
        },
        "no_rescue": "No series, transform, coefficient, mapping, threshold, "
                     "cost, target, bootstrap, sample or execution rule may be "
                     "changed after this result. Any such work requires a NEW "
                     "LINEAGE with its own preregistration and seal.",
    }
    return result, cls, status, failure, gate1, m1r, m2r


# =========================================================================== #

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--preflight", action="store_true")
    a = ap.parse_args()
    if a.execute == a.preflight:
        say("choose exactly one of --preflight (spends nothing) or --execute")
        return 2

    grant = phase0(a.execute)
    gate05 = phase1()
    dec, raw, _undef_reason = phase2()
    prices = load_prices()
    book, _signal, monthly_px, rets, elig, warmup = phase3(dec, raw, prices)

    if a.preflight:
        say("=" * 78)
        say("PREFLIGHT COMPLETE — phases 0-3 passed. No return was accessed,")
        say("no statistic was produced, and no authorization was consumed.")
        say("=" * 78)
        return 0

    gross, turn, cost, net, boundary, devs = phase4(book, monthly_px, rets,
                                                    elig)
    res, years, block = phase5(gross, net)
    result, cls, status, failure, g1r, m1r, m2r = phase6(
        res, gross, turn, cost, net, elig, years, block, warmup, boundary,
        gate05, devs)

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(RESULT_JSON, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(result, fh, indent=1, sort_keys=True)
        fh.write("\n")
    say("=" * 78)
    say("RESULT ARTIFACT  %s" % RESULT_JSON)
    say("sha256           %s" % sha256_file(RESULT_JSON))
    say()
    say("THE PRIMARY RETURN TRIAL IS NOW SPENT. Mark %s CONSUMED."
        % AUTHORIZATION_ID)
    say("=" * 78)
    _ = grant
    return 0


if __name__ == "__main__":
    sys.exit(main())
