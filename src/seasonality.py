"""Step 1 — DESCRIPTIVE premise test for calendar / seasonality effects (strategy C).

Pre-registered family (``research/seasonality/PREREGISTRATION.md``), 3 effects, each
tested pooled + per sleeve = 18 cells:
  * E1 turn-of-month  — last trading day of a month + first 3 trading days of the next.
  * E2 Halloween/Sell-in-May — winter (Nov-Apr) vs summer (May-Oct).
  * E3 Monday — first trading day of each calendar week (holiday-robust).

DESCRIPTIVE ONLY: mean daily return on effect-days vs non-effect-days. No positions,
no P&L, no strategy, no tuning. Reuses the verified-causal daily returns
(``src.daily.daily_returns``) on the same cached adjusted-close panel the monthly
engine resamples.

Causality note. The day-labellers are deterministic functions of the realized
trading-day index. The components that Step 2 would use as TRADEABLE signals — the
*first* k trading days of a month, the day-of-week / week-start, and the winter/summer
month — are all same-day knowable (causal). The single "*last* trading day of the
month" component is a calendar property used here for DESCRIPTION only; a tradeable
Step-2 rule would replace it with a causal proxy (e.g. an exchange-calendar expected
month-end). Truncation-invariance of the causal components is unit-tested.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

import config
import universe

SLEEVES: list[str] = list(universe.GROUPS.keys())
SCOPES: list[str] = ["Pooled"] + SLEEVES
EFFECTS: tuple[str, ...] = ("E1_TOM", "E2_Halloween", "E3_Monday")
# Prior directions (+1 => effect-days expected higher; -1 => lower).
PRIOR_SIGN: dict[str, int] = {"E1_TOM": +1, "E2_Halloween": +1, "E3_Monday": -1}


# --------------------------------------------------------------------------- #
# Day labellers (deterministic calendar functions of the trading-day index)
# --------------------------------------------------------------------------- #
def _rank_in_group(index: pd.DatetimeIndex, keys) -> pd.Series:
    """1-based ordinal position of each date within its group (stable order)."""
    order = pd.Series(np.arange(len(index)), index=index)
    return order.groupby(keys).rank(method="first")


def is_tom(index: pd.DatetimeIndex,
           last: int = config.SEAS_TOM_LAST,
           first: int = config.SEAS_TOM_FIRST) -> pd.Series:
    """E1: True on the last ``last`` trading day(s) of each month OR the first
    ``first`` trading day(s) of each month (the turn-of-the-month window)."""
    idx = pd.DatetimeIndex(index)
    ym = idx.to_period("M")
    rank_start = _rank_in_group(idx, ym.values)          # 1 = first trading day of month
    size = pd.Series(1, index=idx).groupby(ym.values).transform("size")
    rank_end = size.to_numpy() - rank_start.to_numpy() + 1   # 1 = last trading day of month
    is_first = rank_start.to_numpy() <= first
    is_last = rank_end <= last
    return pd.Series(is_first | is_last, index=idx)


def is_winter(index: pd.DatetimeIndex,
              winter_months=config.SEAS_WINTER_MONTHS) -> pd.Series:
    """E2: True if the trading day falls in a winter (Nov-Apr) month."""
    idx = pd.DatetimeIndex(index)
    return pd.Series(idx.month.isin(winter_months), index=idx)


def is_week_start(index: pd.DatetimeIndex) -> pd.Series:
    """E3: True on the first trading day of each calendar week (Monday, or the first
    trading day after a holiday Monday)."""
    idx = pd.DatetimeIndex(index)
    wk = idx.to_period("W")
    rank = _rank_in_group(idx, wk.values)
    return pd.Series(rank.to_numpy() == 1, index=idx)


def effect_dummy(effect: str, index: pd.DatetimeIndex) -> pd.Series:
    """0/1 effect-day indicator for a pre-registered effect (1 = effect-day)."""
    if effect == "E1_TOM":
        d = is_tom(index)
    elif effect == "E2_Halloween":
        d = is_winter(index)
    elif effect == "E3_Monday":
        d = is_week_start(index)
    else:
        raise ValueError(f"unknown effect {effect!r}")
    return d.astype(int)


# --------------------------------------------------------------------------- #
# Scope return series (equal-weight, balanced cross-section)
# --------------------------------------------------------------------------- #
def scope_returns(rets: pd.DataFrame, scope: str) -> pd.Series:
    """Equal-weight mean daily return of the in-scope assets (Pooled = all 17)."""
    cols = list(rets.columns) if scope == "Pooled" else universe.GROUPS[scope]
    return rets[cols].mean(axis=1)


def balanced_returns(px: pd.DataFrame) -> pd.DataFrame:
    """Per-asset daily returns on the balanced all-present window (drops the single
    leading NaN day so every cell of the cross-section is defined)."""
    from . import daily
    rets = daily.daily_returns(px[universe.TICKERS])
    return rets.dropna(how="any")


# --------------------------------------------------------------------------- #
# Test statistics
# --------------------------------------------------------------------------- #
def hac_diff_test(y: np.ndarray, d: np.ndarray, lag: int = config.SEAS_HAC_LAG) -> dict:
    """OLS r = a + b*1[effect] + e with Newey-West (Bartlett, ``lag``) HAC SEs.

    The slope ``b`` on a 0/1 dummy with intercept IS the difference in group means
    (mean_effect - mean_non). Returns Δ (=b), HAC t, two-sided normal p, SE, counts.
    """
    y = np.asarray(y, float)
    d = np.asarray(d, float)
    n = len(y)
    X = np.column_stack([np.ones(n), d])
    XtX_inv = np.linalg.inv(X.T @ X)
    beta = XtX_inv @ (X.T @ y)
    resid = y - X @ beta
    u = X * resid[:, None]                       # score contributions (n x 2)
    S = u.T @ u                                  # Gamma_0
    for j in range(1, lag + 1):
        w = 1.0 - j / (lag + 1.0)                # Bartlett weight
        G = u[j:].T @ u[:-j]
        S += w * (G + G.T)
    V = XtX_inv @ S @ XtX_inv
    se = float(np.sqrt(V[1, 1]))
    t = float(beta[1] / se) if se > 0 else np.nan
    p = float(2.0 * stats.norm.sf(abs(t))) if np.isfinite(t) else np.nan
    return {"delta": float(beta[1]), "t": t, "p": p, "se": se,
            "n_eff": int(d.sum()), "n_non": int((1 - d).sum()),
            "mean_eff": float(y[d == 1].mean()), "mean_non": float(y[d == 0].mean())}


def block_bootstrap_ci(y: np.ndarray, d: np.ndarray,
                       block: int = config.SEAS_BLOCK_LEN,
                       n_boot: int = config.SEAS_BOOTSTRAP_N,
                       seed: int = config.RANDOM_SEED,
                       ci: float = config.CI_LEVEL) -> dict:
    """Moving-block bootstrap of Δ = mean(eff) - mean(non). Blocks of (y, d) pairs are
    resampled together so within-block calendar clustering is preserved."""
    y = np.asarray(y, float)
    d = np.asarray(d, float)
    n = len(y)
    rng = np.random.default_rng(seed)
    nblocks = int(np.ceil(n / block))
    offs = np.arange(block)
    deltas = np.empty(n_boot)
    for b in range(n_boot):
        starts = rng.integers(0, n - block + 1, size=nblocks)
        idx = (starts[:, None] + offs[None, :]).ravel()[:n]
        yb, db = y[idx], d[idx]
        eff = db == 1
        deltas[b] = (yb[eff].mean() - yb[~eff].mean()) if eff.any() and (~eff).any() else np.nan
    deltas = deltas[np.isfinite(deltas)]
    lo, hi = np.percentile(deltas, [(100 - ci) / 2, 100 - (100 - ci) / 2])
    return {"lo": float(lo), "hi": float(hi),
            "frac_gt_0": float((deltas > 0).mean()),
            "crosses_0": bool(lo < 0 < hi)}


def _delta(y: np.ndarray, d: np.ndarray) -> float:
    eff = d == 1
    return float(y[eff].mean() - y[~eff].mean())


# --------------------------------------------------------------------------- #
# Robustness — high-frequency effects (E1, E3): sub-period + winsorized concentration
# --------------------------------------------------------------------------- #
def subperiod_deltas(y: np.ndarray, d: np.ndarray) -> dict:
    """Δ on equal halves and equal thirds (split by position)."""
    n = len(y)
    out: dict[str, float] = {}
    h = n // 2
    out["H1"], out["H2"] = _delta(y[:h], d[:h]), _delta(y[h:], d[h:])
    t = n // 3
    out["T1"], out["T2"], out["T3"] = _delta(y[:t], d[:t]), _delta(y[t:2 * t], d[t:2 * t]), _delta(y[2 * t:], d[2 * t:])
    return out


def winsor_concentration(y: np.ndarray, d: np.ndarray,
                         limits=config.SEAS_WINSOR) -> dict:
    """Δ after winsorizing the scope returns at ``limits``; plus the share of the raw
    Δ removed by dropping the single most extreme effect-day."""
    lo_q, hi_q = np.quantile(y, limits)
    yw = np.clip(y, lo_q, hi_q)
    delta_w = _delta(yw, d)
    raw = _delta(y, d)
    eff_idx = np.where(d == 1)[0]
    mean_non = y[d == 0].mean()
    dev = np.abs(y[eff_idx] - mean_non)          # contribution of each effect-day to the gap
    drop = eff_idx[np.argmax(dev)]
    keep = np.ones(len(y), bool); keep[drop] = False
    delta_drop1 = _delta(y[keep], d[keep])
    share_top1 = float((raw - delta_drop1) / raw) if raw != 0 else np.nan
    return {"delta_winsor": float(delta_w), "delta_drop_top1": float(delta_drop1),
            "share_top1_effect_day": share_top1}


# --------------------------------------------------------------------------- #
# Robustness — annual effect (E2): per-year spread + year-level jackknife
# --------------------------------------------------------------------------- #
def e2_per_year(series: pd.Series, winter_months=config.SEAS_WINTER_MONTHS) -> pd.DataFrame:
    """Per calendar year: mean winter-month return, mean summer-month return, and the
    winter-minus-summer spread (bps/day). One row per year that has both seasons."""
    idx = pd.DatetimeIndex(series.index)
    win = idx.month.isin(winter_months)
    df = pd.DataFrame({"r": series.to_numpy(), "year": idx.year, "winter": win})
    rows = []
    for y, g in df.groupby("year"):
        w, s = g.loc[g["winter"], "r"], g.loc[~g["winter"], "r"]
        if len(w) and len(s):
            rows.append({"year": int(y), "n_winter": len(w), "n_summer": len(s),
                         "winter_bps": w.mean() * 1e4, "summer_bps": s.mean() * 1e4,
                         "spread_bps": (w.mean() - s.mean()) * 1e4})
    return pd.DataFrame(rows).set_index("year")


def e2_year_jackknife(series: pd.Series, winter_months=config.SEAS_WINTER_MONTHS) -> dict:
    """Leave-one-calendar-year-out winter-minus-summer Δ, plus dropping the 2 years
    whose per-year spread is most extreme (jointly). Δ in bps/day."""
    idx = pd.DatetimeIndex(series.index)
    r = series.to_numpy()
    win = np.asarray(idx.month.isin(winter_months))
    yr = np.asarray(idx.year)

    def delta_excluding(mask_keep: np.ndarray) -> float:
        rr, ww = r[mask_keep], win[mask_keep]
        return (rr[ww].mean() - rr[~ww].mean()) * 1e4

    full = delta_excluding(np.ones(len(r), bool))
    years = np.unique(yr)
    loo = {int(y): delta_excluding(yr != y) for y in years}
    loo_vals = np.array(list(loo.values()))
    # the 2 most extreme years by |per-year spread|
    py = e2_per_year(series, winter_months)
    extreme2 = py["spread_bps"].abs().sort_values(ascending=False).head(2).index.tolist()
    drop2 = delta_excluding(~np.isin(yr, extreme2))
    return {"full_bps": float(full),
            "loo_min_bps": float(loo_vals.min()), "loo_max_bps": float(loo_vals.max()),
            "loo_min_year": int(min(loo, key=loo.get)), "loo_max_year": int(max(loo, key=loo.get)),
            "drop_top2_years": [int(x) for x in extreme2], "drop_top2_bps": float(drop2)}


# --------------------------------------------------------------------------- #
# Multiplicity — Benjamini-Hochberg FDR
# --------------------------------------------------------------------------- #
def bh_fdr(pvals, q: float = config.SEAS_FDR_Q) -> tuple[np.ndarray, np.ndarray]:
    """Return (BH-adjusted p-values, reject flags) for control at level ``q``."""
    p = np.asarray(pvals, float)
    m = len(p)
    order = np.argsort(p)
    ranked = p[order]
    ranks = np.arange(1, m + 1)
    adj = np.minimum.accumulate((ranked * m / ranks)[::-1])[::-1]
    adj = np.clip(adj, 0.0, 1.0)
    p_adj = np.empty(m); p_adj[order] = adj
    passed = ranked <= (ranks / m) * q
    reject = np.zeros(m, bool)
    if passed.any():
        kmax = np.where(passed)[0].max() + 1
        reject[order[:kmax]] = True
    return p_adj, reject


# --------------------------------------------------------------------------- #
# Family driver
# --------------------------------------------------------------------------- #
def run_family(px: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    """Compute the full 18-cell pre-registered family. Returns the results table
    (one row per effect x scope, with HAC test, bootstrap CI, robustness, BH-FDR) and
    the per-year E2 tables keyed by scope."""
    rets = balanced_returns(px)
    index = rets.index
    dummies = {e: effect_dummy(e, index).to_numpy() for e in EFFECTS}

    rows = []
    e2_year_tables: dict[str, pd.DataFrame] = {}
    for effect in EFFECTS:
        d = dummies[effect]
        for scope in SCOPES:
            s = scope_returns(rets, scope)
            y = s.to_numpy()
            test = hac_diff_test(y, d)
            boot = block_bootstrap_ci(y, d)
            row = {"effect": effect, "scope": scope, "prior_sign": PRIOR_SIGN[effect],
                   "delta_bps": test["delta"] * 1e4, "t_hac": test["t"], "p_raw": test["p"],
                   "mean_eff_bps": test["mean_eff"] * 1e4, "mean_non_bps": test["mean_non"] * 1e4,
                   "n_eff": test["n_eff"], "n_non": test["n_non"],
                   "boot_lo_bps": boot["lo"] * 1e4, "boot_hi_bps": boot["hi"] * 1e4,
                   "boot_crosses_0": boot["crosses_0"]}
            if effect in ("E1_TOM", "E3_Monday"):
                sp = subperiod_deltas(y, d)
                wc = winsor_concentration(y, d)
                row.update({f"{k}_bps": v * 1e4 for k, v in sp.items()})
                row["delta_winsor_bps"] = wc["delta_winsor"] * 1e4
                row["share_top1_eff_day"] = wc["share_top1_effect_day"]
            else:  # E2 — year-level robustness
                jk = e2_year_jackknife(s)
                row["loo_min_bps"], row["loo_max_bps"] = jk["loo_min_bps"], jk["loo_max_bps"]
                row["loo_min_year"], row["loo_max_year"] = jk["loo_min_year"], jk["loo_max_year"]
                row["drop_top2_bps"] = jk["drop_top2_bps"]
                row["drop_top2_years"] = jk["drop_top2_years"]
                py = e2_per_year(s)
                row["years_positive"] = int((py["spread_bps"] > 0).sum())
                row["years_total"] = int(len(py))
                e2_year_tables[scope] = py
            rows.append(row)

    df = pd.DataFrame(rows)
    p_adj, reject = bh_fdr(df["p_raw"].to_numpy())
    df["p_bh"] = p_adj
    df["fdr_reject"] = reject
    return add_verdicts(df), e2_year_tables


# --------------------------------------------------------------------------- #
# Decision rule (§4 of the pre-registration) — the 5-criteria conjunction
# --------------------------------------------------------------------------- #
def add_verdicts(df: pd.DataFrame,
                 bar: float = config.SEAS_MAGNITUDE_BPS,
                 retain: float = config.SEAS_WINSOR_RETAIN) -> pd.DataFrame:
    """Append the five pre-registered pass/fail flags and the CONFIRMED verdict.

    An effect×scope cell is CONFIRMED only if it clears ALL of: BH-FDR survival, sign
    matches the prior, |Δ| >= magnitude bar, effect-appropriate stability, and
    effect-appropriate non-concentration (daily winsorize for E1/E3; year jackknife
    for E2)."""
    df = df.copy()
    flags = {"pass_fdr": [], "pass_sign": [], "pass_magnitude": [],
             "pass_stable": [], "pass_concentration": [], "CONFIRMED": []}
    for _, r in df.iterrows():
        prior = int(r["prior_sign"])
        d = r["delta_bps"]
        pass_fdr = bool(r["fdr_reject"])
        pass_sign = np.sign(d) == prior
        pass_mag = abs(d) >= bar
        if r["effect"] in ("E1_TOM", "E3_Monday"):
            halves_ok = (np.sign(r["H1_bps"]) == prior) and (np.sign(r["H2_bps"]) == prior)
            thirds_ok = sum(np.sign(r[f"{t}_bps"]) == prior for t in ("T1", "T2", "T3")) >= 2
            pass_stable = bool(halves_ok and thirds_ok)
            dw = r["delta_winsor_bps"]
            pass_conc = bool((np.sign(dw) == prior) and (abs(dw) >= retain * bar))
        else:  # E2 — year-level (prior is +1)
            consistent = r["years_positive"] if prior > 0 else r["years_total"] - r["years_positive"]
            pass_stable = bool(consistent > r["years_total"] / 2)
            loo_sign_ok = (np.sign(r["loo_min_bps"]) == prior) and (np.sign(r["loo_max_bps"]) == prior)
            d2 = r["drop_top2_bps"]
            pass_conc = bool(loo_sign_ok and (np.sign(d2) == prior) and (abs(d2) >= bar))
        confirmed = bool(pass_fdr and pass_sign and pass_mag and pass_stable and pass_conc)
        for k, v in zip(flags, [pass_fdr, pass_sign, pass_mag, pass_stable, pass_conc, confirmed]):
            flags[k].append(v)
    for k, v in flags.items():
        df[k] = v
    return df
