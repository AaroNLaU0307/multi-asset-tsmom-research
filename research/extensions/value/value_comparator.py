# -*- coding: utf-8 -*-
"""The frozen TSMOM comparator, pinned and deterministically recomputed.

The sealed Value contract asks whether a Value sleeve adds anything to "the
frozen TSMOM strategy". Until `VALUE_S1_COMPARATOR_IDENTITY_AMENDMENT_002` that
comparator was named but never identified, so no run could be reproduced from
the sealed bytes. This module is that identity, expressed as code.

Nothing here is a scientific choice. Every element is transcribed from an
authoritative repo artifact, and `provenance()` records which one:

    MAP_v2 §A.1 "The mechanism as implemented (frozen)"
        research/extensions/TSMOM_EXTENSION_RESEARCH_MAP_v2.md
    X01 §3.7 "The signal — MEAN OF SIGNS, restored to the frozen V2 definition"
        research/extensions/x01/X01_PREREGISTRATION_DRAFT.md  (SEALED)
    the canonical modules themselves: universe.py, config.py, src/signals.py,
        src/sizing.py, src/portfolio.py, src/performance.py

**The comparator is the full canonical 17-ETF book, NOT X01's E arm.** X01's E
arm reuses the same primitives but deliberately restricts to four commodity
ETFs and removes the portfolio-level volatility target and gross cap, because
those "depend on the other four sleeves and would inject non-commodity
information into a commodity wrapper test" (X01 §3, E table). The Value
contract needs the opposite: §4.8 keeps "the existing portfolio volatility
target and gross cap, unchanged", and §2's universe partition is exactly the
17-asset book (5 valued + 12 excluded). Reusing X01's E arm here would be a
different object.

Every canonical argument is passed EXPLICITLY below. A default argument is not
authority, so this module never relies on one.
"""
import hashlib
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import value_contract as C          # noqa: E402

COMPARATOR_ID = "CANONICAL_17_ETF_TSMOM_BASELINE"

# The frozen ETF panel, pinned byte-for-byte by the SEALED X01 contract (§3, E
# table) as `dataset.yfinance.multi-asset-etf-panel`. Value inherits that pin
# rather than minting a second identity for the same bytes.
PANEL_RELPATH = "data/close_prices_raw.csv"
PANEL_SHA256 = "3d2a7a56dbd92d4ff8138cfd894c87f5ac5ac088a11165db870673e0c05c3c31"

# Canonical construction, read from MAP_v2 §A.1 and the modules it cites.
SIGNAL_METHOD = "B"                  # signals.signal_method_b, mean-of-signs
AGGREGATION = "equal_weight"         # portfolio.equal_weight_aggregate
EXPECTED_UNIVERSE_N = 17

# Code identities at the pinned revision (git blob bytes, BLOB convention).
CANONICAL_CODE_SHA256 = {
    "universe.py":
        "7cc04c2f65a76f81afd99a46c0be33163a9d24887b40a98ef6c63a52d45fd384",
    "config.py":
        "6c2d9820963cb5cc0bd1991b4697417d755333fc87f73081eaf403e45cba258f",
    "src/signals.py":
        "b5e8afcf1e5f5666eeaf503fc8c0bf3f45751edc92b14cb390b13ff712676c20",
    "src/sizing.py":
        "434ca65e40035b93421d91e3ee7aa15cb6719b23c53ce477f26fee3cff581081",
    "src/portfolio.py":
        "aa06eb1c5fcd69be57f911fab21b76e299f5e71ee727fd27aa138ddf52aa4479",
    "src/performance.py":
        "f96976fb2220319219cc75db4ee775f3d14fab1dedd27254704c6ee49a9285ba",
}


class ComparatorIdentityError(RuntimeError):
    """The pinned comparator could not be reproduced. Never repaired silently."""


def panel_sha256():
    p = os.path.join(_REPO, PANEL_RELPATH)
    return hashlib.sha256(io.open(p, "rb").read()).hexdigest()


def code_sha256(relpath):
    """Working-tree bytes of a canonical module, BLOB convention (LF-normalised
    is not applied: these are read as stored, matching `git show HEAD:<path>`
    for a repo that stores LF)."""
    p = os.path.join(_REPO, relpath)
    return hashlib.sha256(io.open(p, "rb").read()).hexdigest()


def verify_identity():
    """Prove the pinned inputs and code are the ones on disk. (ok, checks)."""
    checks = []

    def ck(label, cond, detail=""):
        checks.append((label, bool(cond), detail))

    actual = panel_sha256()
    ck("ETF panel matches the X01-sealed pin", actual == PANEL_SHA256,
       actual[:16])

    for rel, want in sorted(CANONICAL_CODE_SHA256.items()):
        got = code_sha256(rel)
        ck("canonical code unchanged: %s" % rel, got == want, got[:16])

    import universe
    ck("universe is the canonical 17-asset book",
       len(universe.TICKERS) == EXPECTED_UNIVERSE_N, str(len(universe.TICKERS)))

    # The Value universe partition must reproduce the book exactly; if it does
    # not, the comparator and the study are talking about different worlds.
    partition = set(C.UNIVERSE) | set(C.EXCLUDED_FROM_VALUE)
    ck("Value universe partition == the comparator book",
       partition == set(universe.TICKERS),
       "%d valued + %d excluded" % (len(C.UNIVERSE),
                                    len(C.EXCLUDED_FROM_VALUE)))
    ck("valued and excluded sets are disjoint",
       not (set(C.UNIVERSE) & set(C.EXCLUDED_FROM_VALUE)))

    import config
    for name, want in (("TARGET_VOL_ANNUAL", 0.10), ("MAX_ASSET_WEIGHT", 2.0),
                       ("VOL_WINDOW_DAYS", 60), ("PORT_TARGET_VOL_ANNUAL", 0.10),
                       ("PORT_VOL_WINDOW_DAYS", 60), ("MAX_GROSS_LEVERAGE", 3.0),
                       ("TRANSACTION_COST_BPS", 2.0),
                       ("MOMENTUM_MIN_PERIODS", 4), ("SIGNAL_COMBINE", "mean"),
                       ("SIGNAL_RESAMPLE", "ME")):
        got = getattr(config, name)
        ck("config.%s == %r" % (name, want), got == want, repr(got))
    ck("config.MOMENTUM_LOOKBACKS_MONTHS == (1, 3, 6, 12)",
       tuple(config.MOMENTUM_LOOKBACKS_MONTHS) == (1, 3, 6, 12),
       repr(tuple(config.MOMENTUM_LOOKBACKS_MONTHS)))

    return all(c for _l, c, _d in checks), checks


def build_comparator_full():
    """Recompute the canonical book's monthly NET return series, full history.

    This is a deterministic re-derivation from the pinned panel and the pinned
    canonical modules. It reads the cached panel (`force=False`) and never
    touches the network. The git-ignored `output/monthly_returns.csv` is NOT
    consulted: it is a historical convenience artifact, not authority.
    """
    if panel_sha256() != PANEL_SHA256:
        raise ComparatorIdentityError(
            "ETF panel does not match the X01-sealed pin %s" % PANEL_SHA256)

    import config
    import universe
    from src import fetch_data, performance as perf, portfolio, signals

    prices, _ = fetch_data.fetch_universe(force=False)
    px = prices[universe.TICKERS]

    # Every canonical argument explicit — MAP_v2 §A.1, not a default.
    port = portfolio.build_portfolio(
        px,
        method=SIGNAL_METHOD,                       # mean-of-signs composite
        agg=AGGREGATION,                            # equal_weight_aggregate
        target_vol=config.PORT_TARGET_VOL_ANNUAL,   # 10% portfolio vol target
        vol_window=config.PORT_VOL_WINDOW_DAYS,     # 60d
        max_gross=config.MAX_GROSS_LEVERAGE,        # 3.0x gross cap
    )
    positions = port["position"]                    # decisions held next month
    monthly_px = signals.to_monthly(px)
    rets = perf.portfolio_returns(
        positions, monthly_px, cost_bps=config.TRANSACTION_COST_BPS)

    # Full-universe honesty rule, canonical: a return month counts only when the
    # decision month carried all 17 weights. Equal-weight aggregation on a
    # smaller growing universe is a different strategy.
    asset_w = port["asset_weight"]
    full_decision = asset_w.notna().all(axis=1)
    if not bool(full_decision.any()):
        raise ComparatorIdentityError("no full-universe decision month exists")
    first_full = full_decision[full_decision].index.min()
    rets = rets.loc[rets.index > first_full]
    return rets["net"]


def comparator_window(start=None, end=None):
    """The comparator on the sealed evaluation window, as (months, values).

    months are 'YYYY-MM' strings in ascending order. Raises rather than
    silently short-changing the window.
    """
    start = C.EVAL_START if start is None else start
    end = C.EVAL_END if end is None else end
    net = build_comparator_full()
    pairs = [("%04d-%02d" % (ts.year, ts.month), float(v))
             for ts, v in net.items()]
    sel = [(m, v) for m, v in pairs if start <= m <= end]
    sel.sort(key=lambda mv: mv[0])

    months = [m for m, _v in sel]
    if len(set(months)) != len(months):
        raise ComparatorIdentityError("duplicate comparator months")
    if len(months) != C.N_MONTHS:
        raise ComparatorIdentityError(
            "comparator covers %d months on %s..%s; the sealed contract "
            "requires %d" % (len(months), start, end, C.N_MONTHS))
    if months[0] != start or months[-1] != end:
        raise ComparatorIdentityError(
            "comparator window is %s..%s, sealed window is %s..%s"
            % (months[0], months[-1], start, end))
    import math
    if any(math.isnan(v) or math.isinf(v) for _m, v in sel):
        raise ComparatorIdentityError("comparator has a non-finite month")
    return months, [v for _m, v in sel]


def series_digest(months, values):
    """A stable digest of the comparator series, for run provenance."""
    h = hashlib.sha256()
    for m, v in zip(months, values):
        h.update(("%s=%.12e;" % (m, v)).encode("ascii"))
    return h.hexdigest()


def provenance():
    """Everything a reader needs to reproduce the comparator from sealed bytes."""
    return {
        "comparator_id": COMPARATOR_ID,
        "description": ("the canonical 17-ETF multi-asset TSMOM book as frozen "
                        "in MAP_v2 §A.1, deterministically recomputed"),
        "is_x01_e_arm": False,
        "relation_to_x01": (
            "shares X01 §3.7's signal definition and X01's ETF panel pin and "
            "cost convention; differs by design in universe (17 vs X01-E's 4 "
            "commodity ETFs) and by retaining the portfolio-level volatility "
            "target and gross cap that X01-E deliberately removes"),
        "universe_source": "universe.py::TICKERS (17 ETFs)",
        "signal": ("mean-of-signs composite of the 1/3/6/12-month month-end "
                   "returns, all four horizons required, combine='mean', "
                   "resample='ME', np.sign(0)=0"),
        "signal_source": "src/signals.py::signal_method_b; X01 §3.7; MAP_v2 §A.1",
        "sizing": "w = score x 0.10 / sigma_60d, clipped to +/-2.0",
        "sizing_source": "src/sizing.py::target_weights",
        "aggregation": "equal weight over available assets, base_i = w_i / N_live",
        "aggregation_source": "src/portfolio.py::equal_weight_aggregate",
        "portfolio_risk": ("L = min(0.10 / sigma_60d(base book), 3.0 / "
                           "gross_base); gross capped at 3.0x"),
        "portfolio_risk_source": "src/portfolio.py::leverage",
        "timing": "decision at month-end t, held through t+1 (shift(1))",
        "cost_convention": ("2.0 bps one-way per unit turnover on "
                            "sum|delta position|"),
        "cost_source": "src/performance.py; config.TRANSACTION_COST_BPS",
        "return_basis": "NET monthly returns",
        "panel": PANEL_RELPATH,
        "panel_sha256": PANEL_SHA256,
        "panel_sha256_convention": "RAW (the file is git-ignored)",
        "code_sha256": dict(CANONICAL_CODE_SHA256),
        "code_sha256_convention": "RAW bytes of the working-tree file",
        "authority": [
            "research/extensions/TSMOM_EXTENSION_RESEARCH_MAP_v2.md §A.1",
            "research/extensions/x01/X01_PREREGISTRATION_DRAFT.md §3.7 (SEALED)",
            "universe.py, config.py, src/signals.py, src/sizing.py, "
            "src/portfolio.py, src/performance.py",
        ],
        "not_authority": [
            "output/monthly_returns.csv - git-ignored, unhashed; a historical "
            "convenience artifact only, never the scientific authority",
        ],
    }


if __name__ == "__main__":
    ok, checks = verify_identity()
    width = max(len(l) for l, _c, _d in checks)
    for label, cond, detail in checks:
        print("  %-*s %s   %s" % (width, label, "PASS" if cond else "FAIL",
                                  detail))
    print()
    print("COMPARATOR_IDENTITY_PINNED =", "YES" if ok else "NO")
    raise SystemExit(0 if ok else 1)
