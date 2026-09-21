# -*- coding: utf-8 -*-
"""CTA-EDGE-05 / F6 — deterministic SYNTHETIC fixtures.

```
NO VALUE HERE IS FITTED TO, DERIVED FROM, OR INFERRED ABOUT THE ACTUAL F6
OUTCOME. Every effect size is an arbitrary round number chosen to exercise a
code branch, and none is a guess at what F6 will do.
```

The core trick is that most fixtures are **exactly linear**: `r_excess` is built
as a deterministic linear function of the sealed regressors with no noise, so
the true `beta_EVENT` is a number chosen here, and OLS must recover it. That
makes the expected value hand-verifiable without running the estimator.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence

import numpy as np
import pandas as pd

import f6_contract as K
import f6_engine as feng

YEARS = list(K.PRIMARY_YEARS)                     # 2011..2025, 15 blocks

#: arbitrary, round, branch-exercising coefficients. Not predictions.
COEF = {"const": 0.00010, "TOM": 0.00030, "HOLD": 0.000010,
        "AUCTION": 0.00020, "weekday_Monday": 0.00005,
        "weekday_Tuesday": -0.00004, "weekday_Wednesday": 0.00006,
        "weekday_Thursday": -0.00003}


def synthetic_calendar(years: Sequence[int] = YEARS,
                       weeks_per_year: int = 8,
                       holiday_every: int = 11) -> pd.DatetimeIndex:
    """A business-day calendar with holidays punched out.

    The holidays matter. On an unbroken `bdate_range`, HOLD is exactly
    ``1 + 2 * Monday`` and so is a linear combination of the intercept and the
    Monday indicator — the block would be rank deficient for a reason that has
    nothing to do with F6. The real panel has holidays and does not suffer this;
    removing a session every `holiday_every` reproduces that.
    """
    out: List[pd.Timestamp] = []
    for y in years:
        days = list(pd.bdate_range("%d-01-03" % y, periods=weeks_per_year * 5))
        out.extend(d for i, d in enumerate(days) if i % holiday_every != 6)
    return pd.DatetimeIndex(sorted(out))


def synthetic_tom(grid: pd.DatetimeIndex) -> np.ndarray:
    """A TOM mask with variation inside every year. Synthetic, not the sealed one."""
    s = pd.Series(grid, index=grid)
    return np.asarray([1 if (d.day <= 3 or d.day >= 27) else 0 for d in s],
                      dtype=int)


def synthetic_auction(grid: pd.DatetimeIndex, every: int = 7) -> set:
    return {d for i, d in enumerate(grid) if i % every == 3}


def synthetic_events(grid: pd.DatetimeIndex, every: int = 6,
                     extra_families: Optional[Dict[str, List[str]]] = None
                     ) -> Dict[str, List[str]]:
    """One event roughly every `every` sessions; one label unless told otherwise.

    `every` is deliberately NOT 5: on a weekly calendar a period-5 event lands on
    the same weekday every time, making EVENT identical to one weekday indicator
    and the block rank deficient for a fixture reason, not an F6 reason.
    """
    fam: Dict[str, List[str]] = {}
    fams = ["FOMC", "CPI", "NFP"]
    for i, d in enumerate(grid):
        if i % every == 2:
            fam[d.strftime("%Y-%m-%d")] = [fams[i % 3]]
    if extra_families:
        for k, v in extra_families.items():
            fam[k] = sorted(v)
    return fam


def make_frame(years: Sequence[int] = YEARS, weeks_per_year: int = 12,
               event_every: int = 6, auction_every: int = 7,
               force_auction_empty: bool = False,
               extra_families: Optional[Dict[str, List[str]]] = None
               ) -> Dict[str, Any]:
    grid = synthetic_calendar(years, weeks_per_year)
    boundary = grid[0] - pd.Timedelta(days=3)
    fam = synthetic_events(grid, event_every, extra_families)
    auc = set() if force_auction_empty else synthetic_auction(grid, auction_every)
    frame = feng.build_frame(grid, boundary, set(fam), synthetic_tom(grid), auc)
    return {"grid": grid, "boundary": boundary, "families": fam, "frame": frame}


def linear_r_excess(frame: pd.DataFrame, beta_event: float,
                    coef: Optional[Dict[str, float]] = None) -> np.ndarray:
    """r_excess EXACTLY linear in the sealed regressors, with NO noise.

    Because there is no error term, OLS must return `beta_event` exactly (to
    floating-point). That is what makes the expected value known in advance.
    """
    c = dict(COEF if coef is None else coef)
    X = feng.design_matrix(frame)
    y = np.full(len(frame), c["const"], float)
    y += beta_event * X["EVENT"].to_numpy(float)
    for name in ("TOM", "HOLD", "AUCTION"):
        y += c[name] * X[name].to_numpy(float)
    for w in K.WEEKDAY_INDICATORS:
        y += c["weekday_" + w] * X["weekday_" + w].to_numpy(float)
    return y


def fixture(beta_event: float, level_shift: float = 0.0,
            noise: float = 0.0, noise_seed: int = 20260921,
            **kw) -> Dict[str, Any]:
    """A complete synthetic case, with P1 and P2 steerable INDEPENDENTLY.

    The decoupling is the whole point of `level_shift`. Adding a constant to
    EVERY row moves the P1 level but is absorbed by the intercept, so
    `beta_EVENT` is untouched. `beta_event` moves the event rows RELATIVE to
    the controls and so moves both. Between them every P1 x P2 cell of the
    sealed terminal table is reachable.
    """
    base = make_frame(**kw)
    frame = base["frame"]
    y = linear_r_excess(frame, beta_event) + float(level_shift)
    if noise:
        g = np.random.default_rng(np.random.SeedSequence(noise_seed))
        y = y + g.normal(0.0, noise, len(frame))
    return {"frame": frame, "r_excess": y, "families": base["families"],
            "grid": base["grid"], "boundary": base["boundary"],
            "beta_event_true": beta_event,
            "seed": K.BOOTSTRAP_SEED_LITERAL}


# --------------------------------------------------------------------------- #
# the six P1 x P2 branch fixtures                                             #
# --------------------------------------------------------------------------- #
# A large effect with zero noise gives a degenerate interval strictly above
# zero; an exactly-zero effect gives an interval collapsed ON zero, which is
# `unresolved` by the sealed definition (lower <= 0 < upper is not satisfied
# when upper == 0, so a zero effect is deliberately steered with a tiny spread).
def f_p1_positive() -> Dict[str, Any]:
    return fixture(beta_event=0.0020)


def f_p1_excluded() -> Dict[str, Any]:
    return fixture(beta_event=-0.0020)


def noisy(beta_event: float, scale: float, seed: int = 20260921,
          **kw) -> Dict[str, Any]:
    """Adds deterministic pseudo-random noise so an interval can straddle zero.

    The noise is seeded and fixed; it is scenery for a branch test, not a model
    of any real return distribution.
    """
    f = fixture(beta_event=beta_event, **kw)
    g = np.random.default_rng(np.random.SeedSequence(seed))
    f["r_excess"] = f["r_excess"] + g.normal(0.0, scale, len(f["frame"]))
    return f


def f_unresolved(seed: int = 20260921) -> Dict[str, Any]:
    """Effect at zero with real spread -> interval straddles zero."""
    return noisy(beta_event=0.0, scale=0.004, seed=seed)


NOISE = 0.004          # deterministic scenery, not a model of any real return


def _p1_centred(beta_event: float, noise: float = NOISE,
                extra: float = 0.0, **kw) -> Dict[str, Any]:
    """A fixture whose P1 point estimate is translated to `extra`.

    Self-calibrating rather than magic-numbered: build once at zero shift, read
    the P1 point, then shift every row by minus that amount (plus `extra`).
    Because a uniform shift is absorbed by the intercept, `beta_EVENT` is
    untouched — which is exactly how a P1-unresolved / P2-decided cell is built.
    """
    probe = fixture(beta_event=beta_event, noise=noise, **kw)
    ev = probe["frame"]["EVENT"].to_numpy(bool)
    p1_0 = feng.p1_mean(feng.net_event_returns(probe["r_excess"][ev]))
    return fixture(beta_event=beta_event, level_shift=extra - p1_0,
                   noise=noise, **kw)


# --- the six P1 x P2 cells, plus the P1-excluded row ----------------------- #
def f_p1pos_p2pos() -> Dict[str, Any]:
    return fixture(beta_event=0.0030, level_shift=0.0050)


def f_p1pos_p2unres() -> Dict[str, Any]:
    return fixture(beta_event=0.0, level_shift=0.0200, noise=NOISE)


def f_p1pos_p2absent() -> Dict[str, Any]:
    return fixture(beta_event=-0.0060, level_shift=0.0300)


def f_p1unres_p2pos() -> Dict[str, Any]:
    return _p1_centred(beta_event=0.0060)


def f_p1unres_p2unres() -> Dict[str, Any]:
    return fixture(beta_event=0.0, level_shift=0.0, noise=NOISE)


def f_p1unres_p2absent() -> Dict[str, Any]:
    return _p1_centred(beta_event=-0.0060)


def f_p1absent() -> Dict[str, Any]:
    return fixture(beta_event=-0.0030, level_shift=-0.0100)


#: (fixture, expected P1 class, expected P2 class) — the sealed table's inputs
BRANCH_CASES = (
    (f_p1pos_p2pos, "positive", "positive"),
    (f_p1pos_p2unres, "positive", "unresolved"),
    (f_p1pos_p2absent, "positive", "excluded_absent"),
    (f_p1unres_p2pos, "unresolved", "positive"),
    (f_p1unres_p2unres, "unresolved", "unresolved"),
    (f_p1unres_p2absent, "unresolved", "excluded_absent"),
    (f_p1absent, "excluded_absent", "excluded_absent"),
)


# --------------------------------------------------------------------------- #
# structural fixtures                                                         #
# --------------------------------------------------------------------------- #
def f_multi_event_same_day() -> Dict[str, Any]:
    """A session carrying TWO family labels: ONE position, ONE observation."""
    base = make_frame()
    grid = base["grid"]
    target = grid[7].strftime("%Y-%m-%d")
    fam = dict(base["families"])
    fam[target] = ["CPI", "FOMC"]
    frame = feng.build_frame(grid, base["boundary"], set(fam),
                             synthetic_tom(grid), synthetic_auction(grid))
    return {"frame": frame, "families": fam, "grid": grid,
            "multi_session": target,
            "r_excess": linear_r_excess(frame, 0.0020)}


def f_rank_deficient() -> Dict[str, Any]:
    """AUCTION identically zero -> a zero column -> rank deficiency -> STOP."""
    base = make_frame(force_auction_empty=True)
    return {"frame": base["frame"],
            "r_excess": np.zeros(len(base["frame"]))}


def f_alternate_weekday_base() -> pd.DataFrame:
    """A frame carrying a weekday outside the sealed set -> design_matrix STOPs."""
    base = make_frame(weeks_per_year=2, years=YEARS[:2])
    f = base["frame"].copy()
    f.loc[f.index[0], "weekday"] = "Saturday"
    return f


def f_prohibited_year_frame() -> pd.DataFrame:
    """A 2026 row, which build_frame must refuse."""
    grid = pd.DatetimeIndex(list(pd.bdate_range("2025-12-01", periods=10))
                            + list(pd.bdate_range("2026-01-05", periods=5)))
    return grid


def cash_fixture(kind: str):
    """DGS3MO variants: normal, source-explained carry, unexplained gap."""
    days = pd.date_range("2011-01-03", "2011-01-31", freq="D")
    rows = set(days)
    values = {d: 0.15 for d in days if d.weekday() < 5}
    if kind == "normal":
        pass
    elif kind == "explained_carry":
        # a published-as-missing holiday: the ROW exists, the value does not
        gone = pd.Timestamp("2011-01-17")
        values.pop(gone, None)
    elif kind == "unexplained_gap":
        # a business day with NO ROW AT ALL in the source file
        gone = pd.Timestamp("2011-01-17")
        values.pop(gone, None)
        rows.discard(gone)
    else:
        raise ValueError(kind)
    return pd.DatetimeIndex(sorted(values)), values, rows


def golden() -> Dict[str, Any]:
    """The hand-verifiable case. See `f6_oracle.golden_expectations`."""
    return {
        "prices": [100.0, 102.0, 102.0, 101.0, 103.02, 103.02, 105.0],
        "dgs3mo_annual_percent": 2.0,
        "hold_days": [3, 1, 1, 1, 1, 3],
        "event_flags": [1, 0, 1, 0, 1, 0],
    }
