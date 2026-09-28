"""Sensitivity: the core net Sharpe net of the 3-month T-bill, whole book.

ANALYSIS_EXTENSION (delegate decision of 2026-09-28, research/ERRATA_2026-09-27.md
sections 10 and 11). The rf = 0 headline is unchanged and stays the headline.

Definition:
    excess_t = net_t - rf_t, applied once to the whole book.
    net_t    = the `net` column of the committed output/monthly_returns.csv.
    rf_t     = FRED DGS3MO (data/DGS3MO.csv) under the rule in
               research/extensions/ca/prospective/ca_rf.py: the last non-missing
               print on or before the decision date, no older than 7 calendar
               days, converted Y / 100 / 12. The decision date for return month t
               is the prior calendar month-end, when month t's position is set.
No position-level or leverage-scaled financing. A month whose rf cannot be locked
stops the run (the rule never imputes).

Sharpe and its 95% CI use the headline's own functions and settings:
src/performance.sharpe_ratio and src/validation.bootstrap_ci (iid percentile,
config.BOOTSTRAP_N = 10,000 resamples, seed config.RANDOM_SEED = 7).

Writes output/excess_return_sensitivity.csv.

Run:  python run_excess_sharpe.py
"""

from __future__ import annotations

import pandas as pd

import config
from research.extensions.ca.prospective import ca_rf
from src import performance, validation

CORE_RETURNS_CSV = config.MONTHLY_RETURNS_CSV
DGS3MO_CSV = config.YIELD_FILES["DGS3MO"]
EXCESS_CSV = config.OUTPUT_DIR / "excess_return_sensitivity.csv"
LABEL = "sensitivity: net of 3-month T-bill, whole book"


def excess_series(core_csv=CORE_RETURNS_CSV, dgs3mo_csv=DGS3MO_CSV) -> pd.DataFrame:
    """One row per return month: net, the locked rf and net - rf."""
    net = pd.read_csv(core_csv, index_col=0, parse_dates=True)["net"]
    rf_series = ca_rf.load_dgs3mo(str(dgs3mo_csv))
    rows = []
    for month_end, r in net.items():
        decision = month_end - pd.offsets.MonthEnd(1)
        rec = ca_rf.lock_rf(rf_series, decision)
        if rec["rf_missing"]:
            raise ValueError(f"rf cannot be locked for {month_end.date()}: {rec['reason']}")
        rows.append({"month_end": month_end, "net": r, "rf_decision_date": rec["decision_date"],
                     "rf_observation_date": rec["observation_date"],
                     "rf_annual_pct": rec["rf_value_annual_pct"], "rf_t": rec["rf_t"],
                     "excess": r - rec["rf_t"]})
    return pd.DataFrame(rows).set_index("month_end")


def summary(excess: pd.Series) -> dict[str, float]:
    ci = validation.bootstrap_ci(excess, stat="sharpe")
    return {"sharpe": performance.sharpe_ratio(excess), "ci_lo": ci["lo"], "ci_hi": ci["hi"],
            "months": int(excess.notna().sum())}


def main() -> None:
    table = excess_series()
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    table.to_csv(EXCESS_CSV)
    s = summary(table["excess"])
    print(f"{LABEL}: Sharpe {s['sharpe']:.4f}, 95% CI [{s['ci_lo']:.4f}, {s['ci_hi']:.4f}], "
          f"{s['months']} months {table.index.min().date()}..{table.index.max().date()}")
    print(f"wrote {EXCESS_CSV}")


if __name__ == "__main__":
    main()
