"""Export the full monthly signal panel for the final 17-asset universe.

Rows = month-end dates, columns = 17 tickers, values = Method B composite signal
(the signals.py default: mean of the {1,3,6,12}-month momentum signs, continuous
in [-1, +1]). For manual spot-checking of any month. No backtest, no performance.

Usage:  python export_signals.py
"""

from __future__ import annotations

import config
import universe
from src import fetch_data, signals


def main() -> None:
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    prices, _ = fetch_data.fetch_universe(force=False)
    px = prices[universe.TICKERS]

    panel = signals.monthly_signals(px, method="B")        # default: mean composite
    panel.index.name = "month_end"
    panel = panel.round(4)
    panel.to_csv(config.MONTHLY_SIGNAL_PANEL_CSV)

    n_rows = int(panel.dropna(how="all").shape[0])
    first = panel.dropna(how="all").index.min()
    last = panel.index.max()
    print(f"[export] {config.MONTHLY_SIGNAL_PANEL_CSV}")
    print(f"         {panel.shape[1]} assets x {n_rows} signal months "
          f"({first.date()} -> {last.date()})")
    print("         values = Method B composite (mean of 1/3/6/12m momentum signs, [-1,+1])")


if __name__ == "__main__":
    main()
