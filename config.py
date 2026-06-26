"""Project configuration for the multi-asset TSMOM universe study.

Step 1 only: data acquisition + correlation analysis + universe screening.
No strategy logic, no signals, no backtest. Every parameter that drives the
analysis lives here so runs are reproducible and there are no magic numbers
buried in the modules.
"""

from __future__ import annotations

from pathlib import Path

# --------------------------------------------------------------------------- #
# Paths
# --------------------------------------------------------------------------- #
PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "output"

RAW_PRICES_CSV = DATA_DIR / "close_prices_raw.csv"          # full union history, adjusted Close
FETCH_META_CSV = DATA_DIR / "fetch_metadata.csv"            # per-ticker fetch status

DATA_QUALITY_CSV = OUTPUT_DIR / "data_quality.csv"
CORRELATION_CSV = OUTPUT_DIR / "correlation_matrix.csv"
HIGH_CORR_CSV = OUTPUT_DIR / "high_corr_pairs.csv"
CLUSTERS_CSV = OUTPUT_DIR / "clusters.csv"
RECOMMENDATIONS_CSV = OUTPUT_DIR / "recommendations.csv"
REPORT_MD = OUTPUT_DIR / "ANALYSIS_REPORT.md"

HEATMAP_PNG = OUTPUT_DIR / "correlation_heatmap.png"
DENDROGRAM_PNG = OUTPUT_DIR / "dendrogram.png"

# Final-universe (step-2 confirmation) artifacts — kept separate so the 30-ETF
# screening outputs above are not overwritten.
FINAL_CORRELATION_CSV = OUTPUT_DIR / "final_correlation_matrix.csv"
FINAL_HEATMAP_PNG = OUTPUT_DIR / "final_correlation_heatmap.png"
FINAL_DENDROGRAM_PNG = OUTPUT_DIR / "final_dendrogram.png"
FINAL_CLUSTERS_CSV = OUTPUT_DIR / "final_clusters.csv"
FINAL_HIGH_CORR_CSV = OUTPUT_DIR / "final_high_corr_pairs.csv"
AG_CORR_CSV = OUTPUT_DIR / "agriculture_correlations.csv"
WINDOW_ANALYSIS_CSV = OUTPUT_DIR / "window_analysis.csv"
FINAL_REPORT_MD = OUTPUT_DIR / "FINAL_UNIVERSE_REPORT.md"

# Step 2/3 panels
MONTHLY_SIGNAL_PANEL_CSV = OUTPUT_DIR / "monthly_signal_panel.csv"
MONTHLY_WEIGHTS_PANEL_CSV = OUTPUT_DIR / "monthly_position_weights.csv"
SIGNAL_CHECK_MD = OUTPUT_DIR / "signal_check.md"
SIZING_CHECK_MD = OUTPUT_DIR / "sizing_check.md"

# Step 4 panels (portfolio aggregation + risk control)
PORT_WEIGHTS_PANEL_CSV = OUTPUT_DIR / "monthly_portfolio_weights.csv"
PORT_RISK_PANEL_CSV = OUTPUT_DIR / "monthly_portfolio_risk.csv"
PORTFOLIO_CHECK_MD = OUTPUT_DIR / "portfolio_check.md"

# --------------------------------------------------------------------------- #
# Asset universe (30 ETFs).
# value = "TopFactor/Sub-factor" label used purely for reporting & coverage
# checks. It encodes the *intended* exposure, not an empirical claim — the
# correlation/clustering step is what tests whether these are actually distinct.
# --------------------------------------------------------------------------- #
ASSET_UNIVERSE: dict[str, str] = {
    # Equity indices
    "SPY": "Equity/US-LargeCap",
    "QQQ": "Equity/US-Nasdaq100",
    "IWM": "Equity/US-SmallCap",
    "EFA": "Equity/DevelopedExUS",
    "EEM": "Equity/EmergingMkts",
    "EWJ": "Equity/Japan",
    # Bonds
    "TLT": "Bond/US-Treasury-Long",
    "IEF": "Bond/US-Treasury-Interm",
    "SHY": "Bond/US-Treasury-Short",
    "LQD": "Bond/US-IG-Credit",
    "HYG": "Bond/US-HY-Credit",
    # Energy
    "USO": "Commodity/Energy-Oil",
    "UNG": "Commodity/Energy-NatGas",
    "XLE": "Equity/Sector-Energy",
    # Metals
    "GLD": "Commodity/Metal-Gold",
    "SLV": "Commodity/Metal-Silver",
    "CPER": "Commodity/Metal-Copper",
    # Agriculture
    "DBA": "Commodity/Agri-Broad",
    "WEAT": "Commodity/Agri-Wheat",
    "CORN": "Commodity/Agri-Corn",
    # FX
    "UUP": "FX/USD-Bull",
    "FXE": "FX/EUR",
    "FXY": "FX/JPY",
    # Real estate
    "VNQ": "RealEstate/US-REIT",
    "RWX": "RealEstate/ExUS-REIT",
    # US equity sectors / other
    "XLF": "Equity/Sector-Financials",
    "XLK": "Equity/Sector-Technology",
    "XLV": "Equity/Sector-Healthcare",
    "XLU": "Equity/Sector-Utilities",
    "GDX": "Equity/GoldMiners",
}

TICKERS: list[str] = list(ASSET_UNIVERSE.keys())


def top_factor(ticker: str) -> str:
    """Return the coarse factor group (text before the first '/')."""
    return ASSET_UNIVERSE[ticker].split("/", 1)[0]


# --------------------------------------------------------------------------- #
# Analysis parameters
# --------------------------------------------------------------------------- #
# Data quality
LATE_START_FLAG = "2010-01-01"   # tickers starting after this are flagged "short history"
JUMP_THRESHOLD = 0.50            # |daily return| above this is flagged as a possible data error
# Spike-and-revert detector: a big move immediately offset by a big opposite move
# the next day is the signature of a bad print (round-trip), not a real return.
SPIKE_REVERT_MOVE = 0.25         # both legs must exceed this |daily return|

# Correlation
RETURN_METHOD = "pct_change"     # daily simple returns
CORR_METHOD = "pearson"

# Redundancy thresholds (reported on SIGNED correlation; redundancy test uses |corr|
# because a near -1 pair, e.g. UUP vs FXE, is just the inverse of the same factor).
HIGH_CORR_STRONG = 0.80          # "fake diversification" — redundant
HIGH_CORR_MODERATE = 0.60        # worth noting
BORDERLINE_CORR = 0.70           # kept assets above this (but <STRONG) flagged as
                                 # optional further-trim candidates for a tighter universe

# Hierarchical clustering
LINKAGE_METHOD = "average"       # average linkage on (1 - corr) distance
# Cut the tree at these correlation levels to count effective independent groups.
CLUSTER_CORR_THRESHOLDS = [0.80, 0.60, 0.40]

# yfinance fetch
FETCH_PERIOD = "max"
FETCH_RETRIES = 4
FETCH_SLEEP_SEC = 1.0            # polite pause between tickers / retries

# Reproducibility
RANDOM_SEED = 7


# --------------------------------------------------------------------------- #
# Step 2 — momentum signal parameters.
# Conventional time-series-momentum lookbacks. We DO NOT optimize these; the
# multi-period average of {1,3,6,12} months is the standard academic convention
# (Moskowitz-Ooi-Pedersen 2012 / Hurst-Ooi-Pedersen). Changing them to chase a
# better curve would be overfitting and is out of scope.
# --------------------------------------------------------------------------- #
MOMENTUM_LOOKBACKS_MONTHS = (1, 3, 6, 12)   # Method B multi-period set
MOMENTUM_LOOKBACK_A = 12                      # Method A single-horizon default
SIGNAL_RESAMPLE = "ME"                        # month-END close drives the signal
SIGNAL_COMBINE = "mean"                       # Method B: 'mean' (continuous) | 'vote' (discrete)
# Method B requires all lookbacks present by default (consistent definition over
# time); set <len(lookbacks) to average over whatever periods are available.
MOMENTUM_MIN_PERIODS = len(MOMENTUM_LOOKBACKS_MONTHS)


# --------------------------------------------------------------------------- #
# Step 3 — per-asset volatility scaling / position sizing.
# Conventional values, NOT optimized. The aim is equal ex-ante risk per asset:
# weight = signal * (target_vol / asset_vol), capped to avoid extreme leverage on
# ultra-low-vol assets (e.g. SHY). All three knobs are standard managed-futures
# defaults; tuning them to improve a curve would be overfitting and is out of scope.
# --------------------------------------------------------------------------- #
VOL_WINDOW_DAYS = 60          # rolling window for the ex-ante daily-vol estimate (~3 months)
TARGET_VOL_ANNUAL = 0.10      # per-asset annualized volatility target (10%)
MAX_ASSET_WEIGHT = 2.0        # cap on |weight| per asset (leverage guardrail)
TRADING_DAYS_PER_YEAR = 252   # annualization factor for daily vol


# --------------------------------------------------------------------------- #
# Step 4 — portfolio aggregation + portfolio-level volatility targeting.
# Robust-by-design: EQUAL-WEIGHT aggregation (no covariance / risk-parity
# optimization — estimation error is large, correlations are unstable in crises,
# and complex optimizers routinely lose to 1/N out of sample; risk parity is left
# as an optional later benchmark). A single portfolio vol target + a gross-leverage
# cap. Conventional values, NOT optimized.
# --------------------------------------------------------------------------- #
PORT_TARGET_VOL_ANNUAL = 0.10   # portfolio annualized vol target (10%)
PORT_VOL_WINDOW_DAYS = 60       # rolling window for realized portfolio vol (~3 months)
MAX_GROSS_LEVERAGE = 3.0        # cap on portfolio gross notional, sum|weights| (safety valve)

# Risk-parity CONTROL experiment (not the main strategy — the main aggregation
# stays equal-weight). Covariance for ERC is estimated on a rolling window; it
# needs more data than a single vol and is noisier — a disclosed disadvantage.
RP_COV_WINDOW_DAYS = 252        # rolling window for the ERC covariance estimate (~1 year)


# --------------------------------------------------------------------------- #
# Step 5 — return calculation + validation.
# Conventional values, NOT optimized. Costs reported gross AND net.
# --------------------------------------------------------------------------- #
TRANSACTION_COST_BPS = 2.0      # one-way cost per unit turnover (liquid-ETF convention)
COST_BPS_GRID = (2.0, 5.0, 10.0, 20.0)   # cost-sensitivity sweep (liquid -> illiquid ETFs)
BOOTSTRAP_N = 10000             # bootstrap resamples for CIs
MONTE_CARLO_N = 10000           # Monte Carlo paths (shuffle and bootstrap each)
CI_LEVEL = 95                   # confidence level (%)
RISK_FREE_ANNUAL = 0.0          # Sharpe uses rf = 0 (disclosed; ~1-2% cash would lower it slightly)

# No-trade band: skip an asset's monthly rebalance when its target weight moves
# less than this (fraction of NAV) from the currently-held weight. Suppresses the
# many tiny leverage/vol re-scaling trades that cost money but barely change
# exposure. A prior value, NOT tuned to maximize Sharpe.
NO_TRADE_BAND = 0.05            # 5% of NAV absolute change threshold per asset

# Regime windows (inclusive) for crisis / calm performance attribution.
REGIMES = {
    "GFC 2008": ("2008-09-01", "2009-03-31"),
    "COVID 2020": ("2020-02-01", "2020-04-30"),
    "Calm 2012-2019": ("2012-01-01", "2019-12-31"),
}

# Validation output artifacts
BACKTEST_REPORT_MD = OUTPUT_DIR / "BACKTEST_REPORT.md"
MONTHLY_RETURNS_CSV = OUTPUT_DIR / "monthly_returns.csv"
EQUITY_CURVE_PNG = OUTPUT_DIR / "equity_curve.png"
FAN_CHART_PNG = OUTPUT_DIR / "monte_carlo_fan_chart.png"
DRAWDOWN_PNG = OUTPUT_DIR / "drawdown.png"

# Robustness (parameter-sensitivity) artifacts — for falsifying the "robust"
# hypothesis. NEVER used to change the main strategy parameters.
ROBUSTNESS_REPORT_MD = OUTPUT_DIR / "ROBUSTNESS_REPORT.md"
ROBUSTNESS_CSV = OUTPUT_DIR / "robustness_grid.csv"
ROBUSTNESS_LOOKBACK_PNG = OUTPUT_DIR / "robustness_lookback.png"
ROBUSTNESS_TARGETVOL_PNG = OUTPUT_DIR / "robustness_target_vol.png"
ROBUSTNESS_VOLWINDOW_PNG = OUTPUT_DIR / "robustness_vol_window.png"
ROBUSTNESS_HEATMAP_PNG = OUTPUT_DIR / "robustness_heatmap.png"

# Cost-sensitivity + turnover-reduction artifacts
COST_REPORT_MD = OUTPUT_DIR / "COST_AND_TURNOVER_REPORT.md"
COST_SENSITIVITY_CSV = OUTPUT_DIR / "cost_sensitivity.csv"
COST_SENSITIVITY_PNG = OUTPUT_DIR / "cost_sensitivity.png"

# Risk-parity control-experiment artifacts
RP_REPORT_MD = OUTPUT_DIR / "RISK_PARITY_CONTROL_REPORT.md"
RP_COMPARISON_CSV = OUTPUT_DIR / "risk_parity_comparison.csv"
RP_EQUITY_PNG = OUTPUT_DIR / "risk_parity_equity_curves.png"


# --------------------------------------------------------------------------- #
# DRAWDOWN ATTRIBUTION DIAGNOSTIC (descriptive — NOT a backtest / not optimized).
# Characterizes WHERE the confirmed TSMOM strategy bleeds: chop/whipsaw vs
# turning-point momentum crashes, decomposable per sleeve. Reuses the exact
# vol-scaled positions from the main pipeline (no re-parameterization). All knobs
# are conventional descriptive choices, never tuned to a target.
# --------------------------------------------------------------------------- #
# Episode identification / flagging
DD_RECONCILE_TOL = 1e-8         # max abs monthly diff allowed in the Step-1 reconciliation gate
DD_FLAG_TOP_N = 10              # always flag the N deepest episodes for detailed attribution
DD_FLAG_DEPTH = 0.05           # ...plus any episode whose depth (peak->trough) is >= 5%
DD_MIN_DEPTH = 0.01            # ignore trivial <1% wiggles when listing episodes

# Chop-vs-crash classification (Step 4)
WORST_K_DAYS = 5               # loss-concentration: share of episode loss from the worst k days
PRE_EPISODE_WINDOW_DAYS = 63   # ~3 trading months before the peak — prior-trend strength test
ER_FLOOR_DENOM = 1e-12         # guard for the efficiency-ratio denominator (no movement)
# An asset-month's loss is "crash-type" when the position was HELD (sign unchanged
# vs the prior month) AND aligned with the entry trend (a trend-following position
# bleeding as the trend reversed); otherwise it is "chop-type" (sign-flip / churn /
# counter-trend). The two buckets are additive and sum to the episode contribution.

# Step-5 reusable regime variables — STRICTLY point-in-time (causal). Only data up
# to each date is used: trailing windows + trailing percentile ranks (no full-sample
# normalization). Meant to be reusable as live signals for later overlay design.
REGIME_VOL_WINDOW_DAYS = 60        # realized-vol window (matches the strategy's vol window)
REGIME_VOL_PCTILE_WINDOW = 756     # trailing window (~3y) for the causal vol-percentile rank
REGIME_ER_WINDOW_DAYS = 63         # trailing efficiency-ratio (trendiness) window (~3 months)
REGIME_DISP_WINDOW_DAYS = 21       # trailing window for cross-asset return dispersion (~1 month)

# Diagnostic output artifacts
DD_REPORT_MD = OUTPUT_DIR / "DRAWDOWN_ATTRIBUTION_REPORT.md"
DD_EPISODES_CSV = OUTPUT_DIR / "dd_episodes.csv"
DD_ATTRIBUTION_CSV = OUTPUT_DIR / "dd_episode_attribution.csv"
DD_SLEEVE_SUMMARY_CSV = OUTPUT_DIR / "dd_sleeve_summary.csv"
DD_CHOP_CRASH_CSV = OUTPUT_DIR / "dd_chop_vs_crash.csv"
DD_PER_ASSET_NET_CSV = OUTPUT_DIR / "dd_per_asset_net.csv"
DD_REGIME_VARS_CSV = OUTPUT_DIR / "regime_variables_pit.csv"
DD_UNDERWATER_PNG = OUTPUT_DIR / "dd_underwater.png"
DD_SLEEVE_EQUITY_PNG = OUTPUT_DIR / "dd_sleeve_equity.png"
DD_ATTRIBUTION_PNG = OUTPUT_DIR / "dd_episode_attribution.png"
DD_TIMELINE_PNG = OUTPUT_DIR / "dd_chop_crash_timeline.png"


# --------------------------------------------------------------------------- #
# VOL-COMPRESSION BREAKOUT (strategy B) — daily infra + premise test + (gated)
# overlay. Conventional values, STATED UP FRONT and NOT searched/tuned. Data is
# adjusted-close only (no intraday H/L), so the "ATR" compression measure is the
# daily realized-vol percentile — the same verified-causal definition style as the
# Step-5 regime vars (rolling vol + trailing percentile rank).
# --------------------------------------------------------------------------- #
COMPRESSION_VOL_WINDOW = 20        # daily realized-vol window (~1 trading month, ATR-style)
COMPRESSION_PCTILE_WINDOW = 252    # trailing (~1y) window for the causal vol-percentile rank
COMPRESSION_THRESHOLD = 0.20       # "compressed" = vol percentile <= 0.20 (low-vol regime)
BREAKOUT_LOOKBACK = 20             # Donchian recent-high/low breakout reference (~1 month)
PREMISE_HORIZONS = (5, 10, 20)     # post-compression look-forward windows (Phase 1B, descriptive)
DAILY_RECONCILE_TOL = 1e-9         # daily->monthly return reconciliation tolerance

# Strategy-B / premise artifacts
BREAKOUT_PHASE1A_MD = OUTPUT_DIR / "BREAKOUT_PHASE1A_INFRA.md"
BREAKOUT_PREMISE_MD = OUTPUT_DIR / "BREAKOUT_PHASE1B_PREMISE.md"
BREAKOUT_PREMISE_CSV = OUTPUT_DIR / "breakout_premise_by_sleeve.csv"
DAILY_PRIMITIVES_CSV = OUTPUT_DIR / "daily_primitives_sample.csv"


# --------------------------------------------------------------------------- #
# SEASONALITY / CALENDAR EFFECTS (strategy C) — Step-1 DESCRIPTIVE premise test.
# Every parameter is fixed by the pre-registration contract
# (research/seasonality/PREREGISTRATION.md) BEFORE any computation — none is
# searched/tuned. Descriptive only: mean returns on effect-days vs non-effect-days;
# no positions / P&L / strategy at this step.
# --------------------------------------------------------------------------- #
# Effect definitions (fixed)
SEAS_TOM_LAST = 1                  # E1: last N trading days of each month are TOM
SEAS_TOM_FIRST = 3                 # E1: first N trading days of each month are TOM
SEAS_WINTER_MONTHS = (11, 12, 1, 2, 3, 4)   # E2: Nov-Apr = "winter" (else summer)
# E3 (Monday) = first trading day of each calendar week (handles holiday Mondays).

# Test statistic / multiplicity (fixed)
SEAS_HAC_LAG = 10                  # Newey-West HAC lag (trading days) for the primary t-test
SEAS_BLOCK_LEN = 10                # moving-block bootstrap block length (trading days)
SEAS_BOOTSTRAP_N = BOOTSTRAP_N     # 10,000 resamples (reuse the project default)
SEAS_FDR_Q = 0.10                  # BH-FDR level across the full 18-test family
SEAS_WINSOR = (0.01, 0.99)         # E1/E3 daily concentration check winsorization limits

# Economic-magnitude bar (fixed): |Δ mean daily return| in basis points/day.
SEAS_MAGNITUDE_BPS = 5.0           # confirm requires |Δ| >= 5 bps/day in the prior direction
SEAS_WINSOR_RETAIN = 0.5           # E1/E3: winsorized Δ must retain >= 0.5x the bar (>=2.5 bps)

# Seasonality premise artifacts
SEASONALITY_PREMISE_MD = OUTPUT_DIR / "SEASONALITY_PHASE1_PREMISE.md"
SEASONALITY_PREMISE_CSV = OUTPUT_DIR / "seasonality_premise_family.csv"
SEASONALITY_PERYEAR_CSV = OUTPUT_DIR / "seasonality_e2_per_year.csv"


# --------------------------------------------------------------------------- #
# Keep-priority for the greedy screening filter (lower number = processed and
# kept first). Domain-informed prior: broad / canonical / liquid representatives
# of a factor are processed first so they become the kept anchor; narrow sector
# slices and thematic duplicates are processed last, so they are dropped *only
# when* the data shows they are >= HIGH_CORR_STRONG with an already-kept asset.
# Priorities are unique to make the greedy order fully deterministic; they never
# drop anything on their own — the |corr| test does.
# --------------------------------------------------------------------------- #
KEEP_PRIORITY: dict[str, int] = {
    # --- Factor anchors (kept first) ---
    "SPY": 1,    # US equity beta
    "TLT": 2,    # long Treasury / duration
    "GLD": 3,    # gold
    "USO": 4,    # crude oil
    "UUP": 5,    # US dollar
    "VNQ": 6,    # US real estate
    # --- Distinct secondary exposures (corr to anchors known to be < 0.80) ---
    "EEM": 7,    # EM equity
    "EWJ": 8,    # Japan equity
    "DBA": 9,    # broad agriculture
    "HYG": 10,   # high-yield credit
    "LQD": 11,   # investment-grade credit
    "SHY": 12,   # short-term rates
    "CPER": 13,  # copper
    "UNG": 14,   # natural gas
    "XLU": 15,   # utilities (rate-sensitive defensive, low corr to SPY)
    "XLE": 16,   # energy sector equity
    "FXY": 17,   # Japanese yen
    "SLV": 18,   # silver
    "XLV": 19,   # healthcare sector
    "GDX": 20,   # gold miners
    "WEAT": 21,  # wheat
    "CORN": 22,  # corn
    "RWX": 23,   # ex-US real estate
    # --- Likely duplicates (processed last; dropped if >= 0.80 with a kept asset) ---
    "EFA": 30,   # developed-ex-US equity (~0.85 with SPY)
    "IWM": 31,   # US small cap (~0.87 with SPY)
    "QQQ": 32,   # Nasdaq-100 (~0.93 with SPY)
    "XLK": 33,   # technology sector (~0.97 with QQQ)
    "XLF": 34,   # financials sector (~0.85 with SPY)
    "IEF": 35,   # intermediate Treasury (~0.92 with TLT)
    "FXE": 36,   # euro (~ -0.94 with UUP)
}


# --------------------------------------------------------------------------- #
# YIELD-CURVE MACRO-REGIME overlay (research/yield_spread) — Step-1 premise.
# Every parameter is fixed by the pre-registration
# (research/yield_spread/PREREGISTRATION.md) BEFORE any slope x TSMOM result;
# none is searched/tuned. The conditioning state is STRICTLY causal:
# slope -> trailing-percentile rank (same style as the Step-5 regime vars)
# -> tercile bucket -> used at t-1. Descriptive premise only (no positions/P&L).
# --------------------------------------------------------------------------- #
YIELD_FILES = {                          # user-supplied FRED CSVs in data/ (gitignored)
    "DGS3MO": DATA_DIR / "DGS3MO.csv",
    "DGS2": DATA_DIR / "DGS2.csv",
    "DGS10": DATA_DIR / "DGS10.csv",
}
YIELD_SPREADS = {                        # name -> (long_leg, short_leg)
    "10Y-3M": ("DGS10", "DGS3MO"),       # primary (NY-Fed recession-model standard)
    "10Y-2Y": ("DGS10", "DGS2"),         # robustness
}
YIELD_PRIMARY_SPREAD = "10Y-3M"
YIELD_PCTILE_WINDOW = REGIME_VOL_PCTILE_WINDOW   # 756 td (~3y) causal trailing-percentile window
YIELD_TERCILE_LO = 1.0 / 3.0             # flat  = trailing-slope percentile <= 1/3
YIELD_TERCILE_HI = 2.0 / 3.0             # steep = trailing-slope percentile >= 2/3
YIELD_FWD_HORIZONS = (21, 63, 126)       # forward windows (~1, 3, 6 months); fixed, not searched
YIELD_FWD_SKIP = 21                      # forward-skip robustness: start the window at t+SKIP
YIELD_MAGNITUDE_ANN = 0.04               # economic-magnitude bar: |delta annualized| >= 4%/yr
YIELD_EPISODE_BRIDGE = 10                # merge flat/inversion runs separated by <= N trading days
YIELD_MIN_EPISODES = 2                   # >=2 independent episodes must carry the effect (>=2-episode gate)
YIELD_FDR_Q = 0.10                       # BH-FDR level across the 6-cell primary family
YIELD_WINDOW = ("2007-04-18", "2026-06-12")  # common all-17-present window (matches the engine)

# artifacts
YIELD_PREMISE_MD = OUTPUT_DIR / "YIELD_SPREAD_PHASE1_PREMISE.md"
YIELD_PREMISE_CSV = OUTPUT_DIR / "yield_spread_premise_family.csv"
YIELD_EPISODES_CSV = OUTPUT_DIR / "yield_spread_episodes.csv"
