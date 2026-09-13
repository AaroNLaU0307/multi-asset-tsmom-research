# -*- coding: utf-8 -*-
"""The Value sleeve's monthly NET return series, built to §4 of the sealed
contract.

§4 steps 6 and 8 say the sleeve is sized by "the existing core volatility-sizing
and position-cap machinery, unchanged" and then takes "the existing portfolio
volatility target and gross cap, unchanged". This module therefore calls the
programme's own modules rather than reimplementing them, so the Value sleeve and
the §17 comparator share one identical portfolio-risk layer:

    src/sizing.py::volatility_at_month_end     per-asset ex-ante vol
    src/portfolio.py::base_portfolio_daily_returns / realized_portfolio_vol /
                      leverage / portfolio_weights / positions_from_weights
    src/performance.py::portfolio_returns      turnover, cost, net

Only the two things §4 makes specific to Value are Value's own:

    the signal        sign of the expanding-history z of the valuation object
                      (value_signal), NOT a momentum composite
    the aggregation   equal RISK weight across the five instruments, dividing by
                      the fixed universe size so a stale instrument's risk is
                      absent rather than redistributed (§4.1)

Nothing here is a scientific choice.
"""
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for _p in (_REPO, HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import value_contract as C          # noqa: E402
import value_data as D              # noqa: E402
import value_portfolio as VP        # noqa: E402
import value_signal as VS           # noqa: E402


class SleeveError(RuntimeError):
    """The sleeve could not be built as sealed. Never repaired silently."""


def _month_key(ts):
    return "%04d-%02d" % (ts.year, ts.month)


def object_history_start(sources=None):
    """The earliest month any raw object carries, read from the data.

    §4 step 3 standardises against "every observation from the object's first
    available month through t inclusive", so the history must start where the
    data starts. This is read, never assumed.
    """
    s = sources or {}
    firsts = []
    cape = s.get("cape") or D.load_shiller_cape()
    tlt = s.get("tlt") or D.load_fred_daily_to_monthly("DFII20.csv")
    credit = s.get("credit") or D.load_fred_daily_to_monthly("BAA10Y.csv")
    fx = s.get("fx") or {c: D.load_fred_daily_to_monthly(f)
                         for c, f in D.FX_FILES.items()}
    cpi = s.get("cpi") or {c: fn() for c, fn in D.CPI_LOADERS.items()}
    for series in [cape, tlt, credit] + list(fx.values()) + list(cpi.values()):
        if series:
            firsts.append(min(series))
    if not firsts:
        raise SleeveError("no raw object carries any observation")
    return min(firsts)


def load_panel():
    """The five Value instruments' daily adjusted closes, from the pinned panel."""
    path = os.path.join(_REPO, C.ETF_PANEL)
    px = pd.read_csv(path, index_col=0, parse_dates=True)
    missing = [t for t in C.UNIVERSE if t not in px.columns]
    if missing:
        raise SleeveError("the pinned ETF panel lacks %s" % (missing,))
    return px[list(C.UNIVERSE)]


def build_sleeve(months=None, sources=None, panel=None):
    """Monthly NET returns of the Value sleeve on the sealed window.

    Returns (months, net_returns, diagnostics). `sources` and `panel` exist so
    the synthetic rehearsal can drive the identical code path; production passes
    None and the pinned files are read.
    """
    import config
    from src import performance as perf, portfolio, signals as sigmod, sizing

    window_months = list(months) if months is not None else D.m_range(
        C.EVAL_START, C.EVAL_END)

    px = load_panel() if panel is None else panel
    monthly_px = sigmod.to_monthly(px)

    # --- the object and signal history, from the object's first month --------
    start = object_history_start(sources)
    hist = D.m_range(start, window_months[-1])
    objects = D.build_objects(hist, sources)
    signals = VS.build_signals(objects, hist)          # {inst: [(month, sign)]}
    sig_by_month = {inst: dict(pairs) for inst, pairs in signals.items()}

    # --- per-asset ex-ante vol, the existing machinery unchanged -------------
    vol = sizing.volatility_at_month_end(px, config.VOL_WINDOW_DAYS)

    # --- §4 steps 5-7: sign signal -> vol sizing -> equal RISK weight --------
    idx = monthly_px.index
    rows = []
    for ts in idx:
        m = _month_key(ts)
        sig_t = {inst: sig_by_month.get(inst, {}).get(m, 0) for inst in C.UNIVERSE}
        vol_t = {}
        for inst in C.UNIVERSE:
            v = vol[inst].get(ts, np.nan) if inst in vol.columns else np.nan
            vol_t[inst] = None if not np.isfinite(v) else float(v)
        w = VP.asset_weights(sig_t, vol_t,
                             target_vol=config.TARGET_VOL_ANNUAL,
                             max_weight=config.MAX_ASSET_WEIGHT)
        rows.append(VP.equal_risk_aggregate(w))        # divide by the fixed 5
    base = pd.DataFrame(rows, index=idx, columns=list(C.UNIVERSE))

    # --- §4 step 8: the existing portfolio vol target and gross cap ----------
    base_daily = portfolio.base_portfolio_daily_returns(base, px)
    port_vol = portfolio.realized_portfolio_vol(
        base_daily, window=config.PORT_VOL_WINDOW_DAYS).reindex(base.index)
    gross_base = base.abs().sum(axis=1)
    L, _l_raw, cap_binds = portfolio.leverage(
        port_vol, gross_base,
        target_vol=config.PORT_TARGET_VOL_ANNUAL,
        max_gross=config.MAX_GROSS_LEVERAGE)
    port_w = portfolio.portfolio_weights(base, L)

    # --- decision at month-end t, held through t+1; §5 costs at 2.0 bps ------
    positions = portfolio.positions_from_weights(port_w)
    rets = perf.portfolio_returns(positions, monthly_px,
                                  cost_bps=config.TRANSACTION_COST_BPS)

    by_month = {_month_key(ts): float(v) for ts, v in rets["net"].items()}
    missing = [m for m in window_months if m not in by_month]
    if missing:
        raise SleeveError(
            "the Value sleeve has no return for %d sealed month(s): %s"
            % (len(missing), missing[:6]))
    net = [by_month[m] for m in window_months]
    if any((not np.isfinite(v)) for v in net):
        raise SleeveError("the Value sleeve has a non-finite month")

    diagnostics = {
        "object_history_start": start,
        "history_months": len(hist),
        "gross_cap_binding_months": int(
            cap_binds.reindex(idx).fillna(False).loc[
                [t for t in idx if _month_key(t) in set(window_months)]].sum()),
        "turnover_definition": "sum of absolute changes in held weights",
        "cost_bps_per_unit_turnover": float(config.TRANSACTION_COST_BPS),
        "aggregation": ("equal risk weight across the fixed five-instrument "
                        "universe; stale instruments are not redistributed"),
        "sizing_source": "src/sizing.py::volatility_at_month_end",
        "portfolio_risk_source": "src/portfolio.py::leverage",
        "cost_source": "src/performance.py::portfolio_returns",
    }
    return window_months, net, diagnostics


def signals_on(months=None, sources=None):
    """The frozen signal path over the sealed window — episodes use only this."""
    window_months = list(months) if months is not None else D.m_range(
        C.EVAL_START, C.EVAL_END)
    start = object_history_start(sources)
    hist = D.m_range(start, window_months[-1])
    objects = D.build_objects(hist, sources)
    full = VS.build_signals(objects, hist)
    keep = set(window_months)
    return {inst: [(m, s) for m, s in pairs if m in keep]
            for inst, pairs in full.items()}
