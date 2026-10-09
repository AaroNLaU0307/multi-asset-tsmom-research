# data/ — local market-data caches (not committed)

Everything in this folder except this note is git-ignored: the files are vendor market
data (Yahoo Finance via `yfinance`, FRED) that this repository does not redistribute.
The runners create them on first use. The table records what each published result was
computed from, so a re-pulled file can be checked against it.

| file | written by | contents | pin |
|---|---|---|---|
| `close_prices_raw.csv` | `src/fetch_data.fetch_universe` (first run of `run_analysis.py` / `run_backtest.py`) | the 30 candidates in `config.TICKERS`, adjusted close, `Ticker.history(period="max", auto_adjust=True)`; 1993-01-29 → 2026-06-12, 8,400 rows, 3,298,252 bytes | SHA-256 `3d2a7a56dbd92d4ff8138cfd894c87f5ac5ac088a11165db870673e0c05c3c31` (`config.CORE_PANEL_SHA256`; verified 2026-09-07, `research/extensions/SAMPLE_REUSE.md` §2) |
| `xsmom_universes_prices.csv` | `src/xsmom_data.fetch_universe_prices` (first run of `run_xsmom_universes.py`) | the 47 tickers in `xsmom_universes.ALL_TICKERS` — DBA DBB DBO EMB EWA EWC EWD EWG EWH EWI EWJ EWL EWM EWN EWP EWQ EWS EWT EWU EWW EWY EWZ FXA FXB FXC FXE FXF FXY GLD HYG IEF LQD SHY SLV TIP TLT UNG USO XLB XLE XLF XLI XLK XLP XLU XLV XLY — adjusted close, same `yfinance` call; 1996-03-18 → 2026-06-18, 7,613 rows, 5,638,059 bytes | SHA-256 `5b098a2c0eaa9d90524c46b100ed98302cbc732f146a301b49c8fb03464fd1d7` (`xsmom_universes.UNIVERSES_PRICES_SHA256`) |
| `DGS3MO.csv`, `DGS2.csv`, `DGS10.csv` | supplied by hand from FRED (`config.YIELD_FILES`) | daily Treasury yields for the yield-curve study | none recorded |

Sealed extension lineages keep their own inputs under this folder (`prospective/`,
`vix/`, …); those are pinned in the lineage manifests under `research/extensions/`.

## Re-running from a clean clone

- **Core** (`python run_backtest.py`): the pull has no end date, so the runner cuts the
  panel at `config.CORE_END_DATE` (2026-06-12) and compares the cache's SHA-256 with the
  pin above. A mismatch is reported; `python run_backtest.py --verify-panel` refuses to
  run on it. The core control scripts (`robustness.py`, `cost_analysis.py`,
  `rp_comparison.py`) apply the same cut.
- **XSMOM universes** (`python run_xsmom_universes.py`): the runner re-pulls the 47
  tickers, cuts them at `xsmom_universes.UNIVERSES_PRICES_END` (2026-06-18), writes the
  cache and compares its SHA-256 with the pin above. From the pinned file the committed
  `research/xsmom/xsmom_universes_{map,returns,cross_corr}.csv` reproduce byte-for-byte and
  `xsmom_universes_decomposition.csv` to within 5e-20 (checked 2026-09-27). A re-pull
  whose hash differs (Yahoo re-adjusts history for later dividends) will not reproduce
  them exactly.

The XSMOM file was pulled after the 2026-06-18 close and before 2026-06-22 13:35 (+08:00),
when the committed report was generated from it; the exact pull time was not recorded. It
was committed with the XSMOM study (f03b5a1) despite the ignore rule and was removed from
the tree on 2026-09-27.
