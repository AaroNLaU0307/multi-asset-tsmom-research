"""FINAL multi-asset TSMOM universe — 17 ETFs (locked).

Authoritative asset list for step 2 (momentum signals) and beyond. Import
``FINAL_UNIVERSE`` (ticker -> factor label) or the grouped lists below.

Provenance
----------
Derived from the 30-ETF correlation / clustering screening
(``output/ANALYSIS_REPORT.md``) and the 19→17 window analysis
(``output/FINAL_UNIVERSE_REPORT.md``). Confirmed by the user:

* CPER dropped — 2011 inception caps the backtest and loses 2008; copper partly
  proxied by equity/EEM; also had bad-print spike-and-revert data errors.
* WEAT, CORN dropped — they were the *only* assets blocking the 2008 sample
  (2011/2010 inceptions). Agriculture exposure is retained via DBA. Trading two
  moderately-correlated single-grain factors for full 2008 + ~4 extra years of
  history (incl. the GFC, where time-series momentum is most tested) is the
  deliberate tradeoff.

Common data window (all 17 overlap): ~2007-04-18 → today, bound by UNG's
inception; covers both the 2008 GFC and the 2020 COVID crash.
"""

from __future__ import annotations

# --------------------------------------------------------------------------- #
# Final universe: ticker -> "TopFactor/Sub-factor" label.
# Grouped by factor for readability; downstream code relies on membership, not order.
# --------------------------------------------------------------------------- #
FINAL_UNIVERSE: dict[str, str] = {
    # Equity (5)
    "SPY": "Equity/US-LargeCap",
    "EEM": "Equity/EmergingMkts",
    "EWJ": "Equity/Japan",
    "XLE": "Equity/Sector-Energy",
    "XLU": "Equity/Sector-Utilities",
    # Bonds (4)
    "TLT": "Bond/US-Treasury-Long",
    "SHY": "Bond/US-Treasury-Short",
    "LQD": "Bond/US-IG-Credit",
    "HYG": "Bond/US-HY-Credit",
    # Commodities (4)
    "USO": "Commodity/Energy-Oil",
    "UNG": "Commodity/Energy-NatGas",
    "GLD": "Commodity/Metal-Gold",
    "DBA": "Commodity/Agri-Broad",
    # FX (2)
    "UUP": "FX/USD-Bull",
    "FXY": "FX/JPY",
    # Real estate (2)
    "VNQ": "RealEstate/US-REIT",
    "RWX": "RealEstate/ExUS-REIT",
}

TICKERS: list[str] = list(FINAL_UNIVERSE.keys())


def top_factor(ticker: str) -> str:
    """Coarse factor group (text before the first '/')."""
    return FINAL_UNIVERSE[ticker].split("/", 1)[0]


# Grouped views (convenience for reporting / step-3 risk bucketing).
GROUPS: dict[str, list[str]] = {
    "Equity": ["SPY", "EEM", "EWJ", "XLE", "XLU"],
    "Bond": ["TLT", "SHY", "LQD", "HYG"],
    "Commodity": ["USO", "UNG", "GLD", "DBA"],
    "FX": ["UUP", "FXY"],
    "RealEstate": ["VNQ", "RWX"],
}

# --------------------------------------------------------------------------- #
# Assets removed during screening, with reason on record. The number is the
# |daily-return correlation| that drove the drop (where applicable; 2011-2026
# common window). See the two reports under output/.
# --------------------------------------------------------------------------- #
EXCLUDED: dict[str, str] = {
    "QQQ": "0.93 with SPY — US large-cap factor already represented by SPY",
    "XLK": "0.97 with QQQ / 0.92 with SPY — tech is a slice of US equity",
    "IWM": "0.87 with SPY — US small cap co-moves with the broad index",
    "XLF": "0.85 with SPY — financials sector is a slice of US equity",
    "EFA": "0.85 with SPY — developed-ex-US tracks US too closely for a separate bet",
    "IEF": "0.92 with TLT — duration factor covered by TLT (long) + SHY (short)",
    "FXE": "-0.94 with UUP — euro is the inverse of the USD factor (UUP)",
    "XLV": "0.79 with SPY — healthcare is a US-equity slice, not an independent factor",
    "GDX": "0.77 with GLD — gold miners = gold + equity beta, not independent",
    "SLV": "0.79 with GLD — precious-metals factor covered by GLD",
    "CPER": "2011 inception caps the backtest start and loses 2008; copper partly "
            "proxied by equity/EEM; also bad-print spike-and-revert data errors",
    "WEAT": "2011-09 inception — blocked the 2008 sample; agriculture kept via DBA "
            "(DBA-WEAT only 0.55, but the window cost outweighed the diversification)",
    "CORN": "2010-06 inception — blocked the 2008 sample; agriculture kept via DBA "
            "(DBA-CORN only 0.60)",
}
