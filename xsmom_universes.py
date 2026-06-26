"""SEALED universe family for the multi-universe XSMOM study (Phase 2).

This file encodes the pre-registration in [`XSMOM_UNIVERSES_README.md`]: the five
universes, each with a *theoretical homogeneity argument written before any result*,
and the locked design knobs shared with Phase 1. **The family is sealed at five** — no
universe may be added, dropped (except for failed data coverage, which is reported), or
substituted on the basis of results.

Headline per universe = **12-1 tercile** only (in the BH-FDR family). The 3/6/9/12
neighbourhood and the rank-weight construction are robustness and are NOT in the family.
The tercile fraction is held constant across the family (`n_side = round(N/3)` per leg)
for comparability; thin legs at small N are acknowledged, not optimised away.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import config
import xsmom_config as xcfg

# --------------------------------------------------------------------------- #
# Coverage rule (data, not result): a ticker is KEPT iff it has prices on/before
# COVERAGE_CUTOFF, i.e. >= ~252 trading days before the common-window start so a
# 12-1 signal exists by 2008-05. Tickers failing this are dropped AND reported;
# the homogeneity argument / inclusion decision do not change.
# --------------------------------------------------------------------------- #
COMMON_WINDOW_START = "2008-05-01"   # Phase-1 study start (full-universe months from here)
COVERAGE_CUTOFF = "2007-05-01"       # need data by here to form the 12-1 signal at 2008-05

# Crisis windows (reuse Phase-1 set incl. the 2009 momentum-crash window).
REGIMES = xcfg.REGIMES

TARGET_VOL_ANNUAL = xcfg.TARGET_VOL_ANNUAL
TRANSACTION_COST_BPS = xcfg.TRANSACTION_COST_BPS


@dataclass(frozen=True)
class Universe:
    key: str
    name: str
    prior: str                       # "strong" | "weak" | "predicted negative"
    candidates: list[str]            # candidate tickers (pre-coverage-verification)
    argument: str                    # one-line a-priori homogeneity argument
    # optional sub-classes for the within-class confound control (only where the
    # universe genuinely contains distinct betas, e.g. commodities / bonds). For
    # single-class universes (sectors / countries / FX) within-class == baseline.
    subgroups: dict[str, list[str]] | None = field(default=None)


# --------------------------------------------------------------------------- #
# THE SEALED FAMILY (order = U1..U5)
# --------------------------------------------------------------------------- #
FAMILY: list[Universe] = [
    Universe(
        key="U1", name="US equity sectors", prior="strong",
        candidates=["XLB", "XLE", "XLF", "XLI", "XLK", "XLP", "XLU", "XLV", "XLY"],
        argument="All large-cap US equity → share the US market factor → ranking nets out "
                 "market beta → residual is pure sector-rotation dispersion (textbook XSMOM "
                 "domain, Moskowitz-Grinblatt 1999).",
    ),
    Universe(
        key="U2", name="Country equity indices", prior="strong",
        candidates=["EWA", "EWC", "EWG", "EWH", "EWJ", "EWL", "EWP", "EWQ", "EWU", "EWW",
                    "EWS", "EWY", "EWT", "EWZ", "EWI", "EWN", "EWM", "EWD"],
        argument="All single-country equity → share the global equity factor → ranking nets "
                 "it out → residual is country momentum (Asness-Liew-Stevens 1997). Large N.",
    ),
    Universe(
        key="U3", name="G10 FX vs USD", prior="weak",
        candidates=["FXA", "FXB", "FXC", "FXE", "FXF", "FXY"],
        argument="All majors quoted vs USD → share the USD factor → ranking nets it out → "
                 "residual is currency cross-momentum. Small N → thin legs; FX momentum weak.",
    ),
    Universe(
        key="U4", name="Commodities (ETF)", prior="weak/caveated",
        candidates=["GLD", "SLV", "USO", "UNG", "DBA", "DBB", "DBO"],
        argument="Loosely 'all commodities' but heterogeneous drivers; commodity ETFs suffer "
                 "roll/contango decay and are NOT clean futures proxies — itself a confound.",
        subgroups={"metals": ["GLD", "SLV", "DBB"], "energy": ["USO", "UNG", "DBO"],
                   "agri": ["DBA"]},
    ),
    Universe(
        key="U5", name="Bonds (NEGATIVE CONTROL)", prior="predicted negative",
        candidates=["SHY", "IEF", "TLT", "LQD", "HYG", "TIP", "EMB"],
        argument="Duration and credit are different betas → ranking sorts on static term/credit "
                 "premia, not dynamic momentum. Predicted to look weakly positive raw and "
                 "collapse hardest under demeaning — a negative that validates the confound theory.",
        subgroups={"govt": ["SHY", "IEF", "TLT", "TIP"], "credit": ["LQD", "HYG", "EMB"]},
    ),
]

FAMILY_BY_KEY: dict[str, Universe] = {u.key: u for u in FAMILY}

# All unique candidate tickers across the family (for one batched data fetch).
ALL_TICKERS: list[str] = sorted({t for u in FAMILY for t in u.candidates})


def tercile_n_side(n_assets: int) -> int:
    """Constant-fraction tercile size held across the family: round(N/3) per leg
    (≥ 1). N=9→3, 18→6, 7→2, 6→2. Thin legs at small N are acknowledged, not tuned."""
    return max(1, round(n_assets / 3))


# --------------------------------------------------------------------------- #
# Output artifacts (separate from Phase-1 outputs — nothing clobbered).
# --------------------------------------------------------------------------- #
OUTPUT_DIR = config.OUTPUT_DIR
DATA_DIR = config.DATA_DIR
UNIVERSES_PRICES_CSV = DATA_DIR / "xsmom_universes_prices.csv"     # NEW cache (not the engine's)
UNIVERSES_FETCH_META_CSV = DATA_DIR / "xsmom_universes_fetch_meta.csv"

REPORT_MD = OUTPUT_DIR / "XSMOM_UNIVERSES_REPORT.md"
MAP_CSV = OUTPUT_DIR / "xsmom_universes_map.csv"
DECOMP_CSV = OUTPUT_DIR / "xsmom_universes_decomposition.csv"
CROSS_CORR_CSV = OUTPUT_DIR / "xsmom_universes_cross_corr.csv"
MAP_FIG_PNG = OUTPUT_DIR / "xsmom_universes_map.png"
PER_UNIVERSE_RETURNS_CSV = OUTPUT_DIR / "xsmom_universes_returns.csv"
