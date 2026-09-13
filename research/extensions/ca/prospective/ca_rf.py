# -*- coding: utf-8 -*-
"""FM-1 risk-free rate locking — sealed OD-6 / §P.2, implemented literally.

    SERIES              = FRED DGS3MO
    OBSERVATION         = last available NON-MISSING print on or before the decision date
    FRESHNESS           = the accepted print must be no older than 7 CALENDAR DAYS
    MONTHLY_CONVERSION  = rf_t = Y / 100 / 12
    LOCKING             = the accepted rf_t is locked with the prospective position
    FALLBACK_SERIES     = NONE

If no valid print exists inside the freshness window: `RF_MISSING = TRUE`.

Forbidden and therefore absent from this module by construction: substituting
DGS1MO or any other series; carrying forward an arbitrarily old yield;
interpolating; using a future observation. There is no parameter that enables any
of them — `lock_rf` takes no series argument and no fallback argument.

THE CANONICAL PRIMARY IS COMPLETELY UNAFFECTED BY RF_MISSING. Nothing in this
module is consulted by `ca_engine`, and the position ledger records the rf state
alongside the position without the position depending on it.
"""
from __future__ import annotations

from datetime import timedelta

import pandas as pd

from . import ca_contract as K


class RfFallbackRefused(Exception):
    """Raised on any attempt to use a series other than the sealed DGS3MO."""


def assert_series_is_sealed(series_name: str) -> None:
    if series_name != K.RF_SERIES:
        raise RfFallbackRefused(
            "REFUSED: FM-1 is sealed to %s with FALLBACK_SERIES = NONE (OD-6). "
            "Requested %r." % (K.RF_SERIES, series_name))


def load_dgs3mo(path: str) -> pd.Series:
    """Load the FRED CMT CSV. Missing values arrive as '.' and stay missing."""
    df = pd.read_csv(path)
    date_col = "observation_date" if "observation_date" in df.columns else df.columns[0]
    val_col = K.RF_SERIES if K.RF_SERIES in df.columns else df.columns[1]
    s = pd.Series(pd.to_numeric(df[val_col], errors="coerce").values,
                  index=pd.to_datetime(df[date_col]), name=K.RF_SERIES)
    return s[~s.index.duplicated(keep="last")].sort_index()


def lock_rf(series: pd.Series, decision_date) -> dict:
    """Resolve and LOCK rf for the month decided at `decision_date`.

    Returns a record that is written once into the position ledger and never
    revised — a later FRED revision changes nothing already locked (§I.3).
    """
    d = pd.Timestamp(decision_date).normalize()
    # Only observations ON OR BEFORE the decision date. A future print is never used.
    past = series[series.index <= d].dropna()
    if len(past) == 0:
        return {"rf_series": K.RF_SERIES, "rf_missing": True, "rf_value_annual_pct": None,
                "rf_t": None, "observation_date": None, "age_calendar_days": None,
                "decision_date": str(d.date()), "reason": "no non-missing print on or before the decision date"}
    obs_date = past.index[-1]
    age = (d - obs_date).days
    if age > K.RF_FRESHNESS_MAX_CALENDAR_DAYS:
        return {"rf_series": K.RF_SERIES, "rf_missing": True, "rf_value_annual_pct": None,
                "rf_t": None, "observation_date": str(obs_date.date()), "age_calendar_days": int(age),
                "decision_date": str(d.date()),
                "reason": "stalest acceptable print is %d calendar days old; freshness window is %d"
                          % (age, K.RF_FRESHNESS_MAX_CALENDAR_DAYS)}
    y = float(past.iloc[-1])
    return {"rf_series": K.RF_SERIES, "rf_missing": False, "rf_value_annual_pct": y,
            "rf_t": y / 100.0 / 12.0, "observation_date": str(obs_date.date()),
            "age_calendar_days": int(age), "decision_date": str(d.date()), "reason": ""}


def fm1_adjudicable(rf_records: list) -> dict:
    """§P.2 — any unresolved RF_MISSING month at the reveal makes FM-1 NOT ADJUDICABLE.

    The sample is NEVER shortened and the rate is NEVER imputed: FM-1 must preserve
    the same scored-month sample as the primary.
    """
    missing = [r["decision_date"] for r in rf_records if r.get("rf_missing")]
    return {
        "fm1_adjudicable": len(missing) == 0,
        "fm1_state": "ADJUDICABLE" if not missing else "NOT ADJUDICABLE — DATA INCOMPLETE",
        "unresolved_rf_missing_months": missing,
        "primary_adjudication": "UNAFFECTED",
        "sample_shortened": False,
        "rate_imputed": False,
        "note": ("A complementary-data failure, not a primary-study failure."
                 if missing else ""),
    }
