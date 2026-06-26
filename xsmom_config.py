"""Configuration for the Cross-Sectional Momentum (XSMOM) study.

This is an *extension* of the multi-asset TSMOM project: it reuses the same 17-ETF
universe (``universe.TICKERS``), the same engine (``src/portfolio.py``,
``src/performance.py``, ``src/validation.py``) and the same cost / seed / vol-window
conventions (``config.py``). Only XSMOM-specific knobs live here.

Anti-overfitting (non-negotiable, mirrors ``config.py``)
--------------------------------------------------------
Every parameter below is an academic convention, fixed *before* looking at any
result. We do NOT scan for a "best" lookback, quantile threshold, or vol window.
The Jegadeesh-Titman 12-1 default and equal terciles are used as-is; the
3/6/9/12-month neighbourhood is run only as a sign/magnitude robustness check,
never to pick a winner.
"""

from __future__ import annotations

import config  # shared conventions: cost, seed, vol window, trading days, regimes

# --------------------------------------------------------------------------- #
# Signal layer — 12-1 momentum with an explicit skip-month.
# signal_{i,t} = P_{i, t-SKIP_DAYS} / P_{i, t-LOOKBACK_DAYS} - 1
# i.e. the cumulative return from ~12 months ago to ~1 month ago, skipping the
# most recent month (filters 1-month reversal / bid-ask bounce / microstructure
# noise). One trading month ~= 21 trading days; 12 months ~= 252.
# --------------------------------------------------------------------------- #
SKIP_DAYS = 21           # explicit skip-month gap (trading days) — NOT implicit
LOOKBACK_DAYS = 252      # formation-window start (trading days back) = 12 months

# 3/6/9/12-month formation neighbourhood (each with the SAME 21-day skip).
# k months back == 21*k trading days. ROBUSTNESS ONLY — reports sign/magnitude
# consistency; never used to select a "best" lookback.
FORMATION_NEIGHBOURHOOD_DAYS: tuple[int, ...] = (63, 126, 189, 252)  # 3,6,9,12 months

# --------------------------------------------------------------------------- #
# Portfolio construction layer.
# HEADLINE = tercile: 17/3 ~= 5.67 -> 6 each is the closest exact-third split with
# better intra-leg diversification (long top 6, short bottom 6, middle 5 flat).
# Equal weight within each leg (+1/6 long, -1/6 short) => dollar-neutral.
# --------------------------------------------------------------------------- #
N_LONG = 6               # tercile long count
N_SHORT = 6              # tercile short count
RANK_METHOD = "average"  # tie handling for cross-sectional ranks (Lo-MacKinlay weights)

# --------------------------------------------------------------------------- #
# Risk-alignment layer (portfolio-level only). Used ONLY for the equity-curve
# overlay and the combined-portfolio construction; Sharpe / correlation / all
# statistical tests run on natural (un-targeted) returns, which are scale-free.
# The vol estimate itself is the ENGINE's estimator, called verbatim
# (``portfolio.realized_portfolio_vol`` / ``PORT_VOL_WINDOW_DAYS``), so the window
# matches TSMOM by construction.
# --------------------------------------------------------------------------- #
TARGET_VOL_ANNUAL = config.PORT_TARGET_VOL_ANNUAL   # 10% — reuse, do not redefine
VOL_WINDOW_DAYS = config.PORT_VOL_WINDOW_DAYS       # 60d — reuse the engine's window

# --------------------------------------------------------------------------- #
# Comparison / analysis conventions (reuse the engine's where they exist).
# --------------------------------------------------------------------------- #
TRANSACTION_COST_BPS = config.TRANSACTION_COST_BPS  # 2 bps one-way (liquid ETF)
RANDOM_SEED = config.RANDOM_SEED
BOOTSTRAP_N = config.BOOTSTRAP_N
MONTE_CARLO_N = config.MONTE_CARLO_N
CI_LEVEL = config.CI_LEVEL

# Crisis windows. TSMOM and XSMOM have DIFFERENT-shaped tails, so we add the
# spring-2009 momentum-crash window (the violent rebound of beaten-down losers
# that blows up a relative-strength short leg) to the engine's 2008/2020 set.
# TSMOM's tail is DIRECTIONAL (wrong about market direction) and it earns crisis
# alpha by going net-short; XSMOM has no directional crisis-alpha mechanism.
MOMENTUM_CRASH_2009 = ("2009-03-01", "2009-06-30")
REGIMES: dict[str, tuple[str, str]] = {
    "GFC 2008": config.REGIMES["GFC 2008"],
    "Mom-crash 2009": MOMENTUM_CRASH_2009,
    "COVID 2020": config.REGIMES["COVID 2020"],
    "Calm 2012-2019": config.REGIMES["Calm 2012-2019"],
}

# --------------------------------------------------------------------------- #
# Output artifacts (kept separate from the TSMOM outputs so nothing is clobbered).
# --------------------------------------------------------------------------- #
OUTPUT_DIR = config.OUTPUT_DIR
XSMOM_REPORT_MD = OUTPUT_DIR / "XSMOM_REPORT.md"
XSMOM_RETURNS_CSV = OUTPUT_DIR / "xsmom_monthly_returns.csv"
XSMOM_HEADTOHEAD_CSV = OUTPUT_DIR / "xsmom_vs_tsmom.csv"
XSMOM_ROBUSTNESS_CSV = OUTPUT_DIR / "xsmom_robustness.csv"
XSMOM_CONFOUND_CSV = OUTPUT_DIR / "xsmom_confound.csv"
XSMOM_EQUITY_PNG = OUTPUT_DIR / "xsmom_equity_curves.png"
XSMOM_CRISIS_CSV = OUTPUT_DIR / "xsmom_crisis_windows.csv"
