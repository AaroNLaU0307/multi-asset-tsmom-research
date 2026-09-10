"""X01 target-construction tests — SYNTHETIC DATA ONLY.

Every fixture here is hand-built: synthetic daily price frames, synthetic
settlement/open-interest panels, synthetic contract-metadata rows, synthetic
position books. **No test in this file opens the frozen ETF CSV or any parquet
panel**, and none produces a Sharpe, ΔS, bootstrap, confidence interval or
crisis statistic. That is asserted, not merely intended (see `test_safety`).

Scope: the construction layer of `x01_target_construction.py` — E, F/A1, S1, S2,
the pairing rule — plus the runner's live tracked-text pin check.
"""

import copy
import importlib.util
import io
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


tc = _load("x01_tc", os.path.join(HERE, "x01_target_construction.py"))
runner = _load("x01_rn", os.path.join(HERE, "x01_runner.py"))

# The console encoding is not guaranteed to cover the sealed contract's own
# notation (cp1252 has no U+0394). Degrade the OUTPUT rather than the test.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

_fails, _out = [], []


def ck(name, ok, detail=""):
    _out.append("  %-64s %s%s" % (name, "PASS" if ok else "FAIL",
                                  ("   " + detail) if detail else ""))
    if not ok:
        _fails.append(name)


def flush(title):
    print("=" * 84); print(title); print("=" * 84)
    print("\n".join(_out)); del _out[:]; print()


# --------------------------------------------------------------------------- #
# synthetic fixtures
# --------------------------------------------------------------------------- #
def synth_etf_daily(n_years=6, tickers=("USO", "UNG", "GLD", "DBA"), seed=11):
    """Deterministic synthetic daily ETF closes. Not market data."""
    rng = np.random.default_rng(seed)
    days = pd.bdate_range("2015-01-01", periods=252 * n_years)
    out = {}
    for i, t in enumerate(tickers):
        steps = 1.0 + rng.normal(0.0003 + i * 0.0001, 0.009, len(days))
        out[t] = 100.0 * np.cumprod(steps)
    return pd.DataFrame(out, index=days)


def synth_futures(root="CL", n_contracts=6, days_per=60, seed=5, start="2020-01-01"):
    """Synthetic settlement/OI panels + metadata for ONE root.

    Contracts overlap so a front series can roll; OI is arranged so the later
    contract overtakes the earlier one, which is what the A1 rule keys on.
    """
    rng = np.random.default_rng(seed)
    total = days_per * (n_contracts + 1)
    dates = pd.bdate_range(start, periods=total)
    keys = ["%d__2020-%02d-01" % (1000 + i, i + 2) for i in range(n_contracts)]
    settle = pd.DataFrame(index=dates, columns=keys, dtype="float64")
    oi = pd.DataFrame(0.0, index=dates, columns=keys)
    for i, k in enumerate(keys):
        lo, hi = i * days_per, min(total, (i + 2) * days_per)
        px = 60.0 + i * 0.5 + np.cumsum(rng.normal(0, 0.15, hi - lo))
        settle.iloc[lo:hi, settle.columns.get_loc(k)] = px
        ramp = np.linspace(10.0, 5000.0, hi - lo)
        oi.iloc[lo:hi, oi.columns.get_loc(k)] = ramp
    meta = pd.DataFrame({
        "asset": [root] * n_contracts,
        "_contract_key": keys,
        "expiration": ["2020-%02d-01" % (i + 2) for i in range(n_contracts)],
    })
    meta["expiration_dt"] = pd.to_datetime(meta["expiration"])
    return settle, oi, meta


# --------------------------------------------------------------------------- #
# 1. E — the ETF reference leg
# --------------------------------------------------------------------------- #
def test_E():
    daily = synth_etf_daily()
    res = tc.construct_E(daily)

    ck("E returns a ConstructionResult with a monthly net stream",
       res.arm == "E" and isinstance(res.net, pd.Series) and len(res.net) > 12)
    ck("E emits NO statistic (no sharpe/ci/bootstrap attribute)",
       not any(hasattr(res, a) for a in ("sharpe", "ci", "bootstrap", "delta_s")))
    ck("E net = gross - cost exactly (zero residual)",
       float(np.max(np.abs((res.gross - res.cost - res.net).values))) == 0.0)
    ck("E emits no undefined month (no NaN net or cost)",
       int(res.net.isna().sum()) == 0 and int(res.cost.isna().sum()) == 0)
    ck("E cost is never negative", bool((res.cost >= 0).all()))
    ck("E turnover is non-negative", bool((res.turnover >= 0).all()))
    ck("E records the month dropped for undefined turnover",
       res.meta["months_dropped_undefined_turnover"] >= 1)
    ck("E records the sealed O-6 zero-carry treatment",
       res.meta["cash_yield"] is None and res.meta["borrow"] is None)
    ck("E does NOT deduct the expense ratio again",
       res.meta["expense_ratio_deducted_again"] is False)
    ck("E applies NO portfolio vol target and NO gross cap (sleeve-standalone)",
       res.meta["portfolio_vol_target_applied"] is False
       and res.meta["gross_leverage_cap_applied"] is False)
    ck("E uses the accepted equal-weight aggregation",
       res.meta["aggregation"] == "equal_weight_aggregate")

    # signal binding — sealed §3.7, on the SAME synthetic frame
    monthly = tc.month_end_prices(daily)
    sig = tc.composite_signal(monthly)
    ck("E signal values lie on the sealed mean-of-signs grid",
       set(np.unique(sig.dropna().values.round(10))) <= {-1.0, -0.75, -0.5, -0.25,
                                                         0.0, 0.25, 0.5, 0.75, 1.0})
    ck("E signal is NaN before all four horizons exist",
       bool(sig.iloc[:12].isna().all().all()))

    # sizing / cap semantics
    vol = tc.month_end_vol(daily)
    w = tc.decision_weights(sig, vol)
    ck("E weights are capped at |2.0|", bool((w.abs().dropna(how="all") <= 2.0 + 1e-12).all().all()))
    ck("E lag: position held = previous month's decision",
       bool(tc.held_positions(w).iloc[5].equals(w.iloc[4])))

    # deterministic missing-month behaviour (§3.5 incomplete sleeve)
    holed = daily.copy()
    hole_month = holed.index[(holed.index.year == 2019) & (holed.index.month == 6)]
    holed.loc[hole_month, "DBA"] = np.nan
    res2 = tc.construct_E(holed)
    ck("E drops months where a sleeve leg is unavailable (never renormalises)",
       res2.meta["months_dropped_incomplete_sleeve"] >= 1,
       "dropped=%d" % res2.meta["months_dropped_incomplete_sleeve"])
    ck("E with a hole never renormalises across ETFs (fewer months, not reweighted)",
       len(res2.net) <= len(res.net))

    # synthetic turnover cost, checked against the sealed convention directly
    pos = pd.DataFrame({"A": [0.0, 1.0, 1.0], "B": [0.0, 0.0, -1.0]},
                       index=pd.date_range("2020-01-31", periods=3, freq="ME"))
    px = pd.DataFrame({"A": [10.0, 11.0, 12.0], "B": [10.0, 10.0, 10.0]}, index=pos.index)
    acc = tc.accepted()
    fr = acc["performance"].portfolio_returns(pos, px, cost_bps=2.0)
    ck("E cost = one-way turnover x bps/1e4 (baseline convention reused)",
       abs(fr["cost"].iloc[1] - 1.0 * 2.0 / 1e4) < 1e-15,
       "turnover=%.3f cost=%.8f" % (fr["turnover"].iloc[1], fr["cost"].iloc[1]))
    flush("1. E — ETF reference leg (synthetic prices)")


# --------------------------------------------------------------------------- #
# 2. F / A1
# --------------------------------------------------------------------------- #
def test_F():
    settle, oi, meta = synth_futures()
    listed = tc.listed_keys_for_root(meta, "CL", settle.columns)
    ck("persistent contract identity: keys are instrument_id__expiration",
       all("__" in k for k in listed) and len(listed) == 6)
    ck("listed order is exchange-listed expiry order",
       listed == sorted(listed, key=lambda k: k.split("__")[1]))

    front = tc.front_series(oi.reindex(columns=listed), listed, rule="A1")
    rolls = int((front != front.shift(1)).sum()) - 1
    ck("A1 front series rolls forward and is monotonic", rolls >= 1,
       "rolls=%d" % rolls)
    order = {k: i for i, k in enumerate(listed)}
    seq = [order[v] for v in front.dropna()]
    ck("A1 never rolls backward", all(b >= a for a, b in zip(seq, seq[1:])))

    settle_d = tc.divided_settlements(settle[listed], "CL")
    ck("divisor applied before any notional (CL divisor = 1.0)",
       bool(np.allclose(settle_d.fillna(0).values, settle[listed].fillna(0).values)))

    # quantity conversion (sealed §3.8)
    q = tc.contract_quantities(weight=0.8, capital=1e6, multiplier=1000.0, price=70.0)
    ck("quantity = w*K/(mult*P)", abs(q - 0.8 * 1e6 / (1000.0 * 70.0)) < 1e-12)
    ck("quantities are continuous (not rounded)", abs(q - round(q)) > 1e-9)

    # traded quantity semantics
    cases = [({"k1": 1.0}, {"k1": 1.0}, 0.0), ({"k1": 1.0}, {"k1": 0.0}, 1.0),
             ({"k1": 1.0}, {"k1": 2.0}, 1.0), ({"k1": 1.0}, {"k1": -1.0}, 2.0),
             ({"k1": 1.0}, {"k2": 1.0}, 2.0)]
    for prev, now, want in cases:
        got = sum(tc.traded_quantity(prev, now).values())
        ck("traded qty %s -> %s = %.0f" % (list(prev.values()), list(now.values()), want),
           abs(got - want) < 1e-12)
    ck("+1 -> -1 reversal charges TWO sides",
       abs(sum(tc.traded_quantity({"k": 1.0}, {"k": -1.0}).values()) - 2.0) < 1e-12)
    ck("roll charges old exit + new entry as two identities",
       tc.traded_quantity({"old": 1.0}, {"new": 1.0}) == {"new": 1.0, "old": 1.0})

    # cash-first primitive, unchanged
    acc = tc.accepted()
    c_cl = acc["carry_costs"].cost_per_side_usd("CL")
    ck("accepted per-side primitive reused unchanged (CL = $12.50)",
       abs(c_cl - 12.50) < 1e-9, "got %.4f" % c_cl)
    cost = tc.cash_cost(tc.traded_quantity({"old": 1.0}, {"new": 1.0}),
                        {"old": "CL", "new": "CL"})
    ck("roll cash cost = 2 sides x $12.50 = $25.00", abs(cost - 25.0) < 1e-9)
    ck("cash cost is never negative",
       tc.cash_cost(tc.traded_quantity({"k": 5.0}, {"k": 1.0}), {"k": "CL"}) >= 0)

    # The cost PATH and the roll double-count are proved by intervention on the
    # live ledger in `test_pnl_route_reachability`, and the whole daily book is
    # proved against closed-form oracles in section 2b. Searching this module's
    # source text for a phrase would prove neither, so no such check is made.
    mapping = {"USO": ["CL"]}
    res = tc.construct_futures_leg(settle, oi, meta, arm="A1", capital=1e6, mapping=mapping)
    ck("A1 leg emits no statistic",
       not any(hasattr(res, a) for a in ("sharpe", "ci", "bootstrap")))
    ck("A1 leg records continuous-quantity limitation",
       res.meta["quantity_type"] == "continuous_research_quantities")
    ck("A1 leg records zero-carry (no yield/financing/borrow/ER)",
       all(res.meta[k] is None for k in
           ("cash_yield", "margin_financing", "borrow", "expense_ratio")))
    flush("2. F / A1 — primitives (synthetic panels)")


# --------------------------------------------------------------------------- #
# 2b. THE DAILY FUTURES BOOK — independent oracles on the production path
# --------------------------------------------------------------------------- #
# Every expectation in this section is computed from the SEALED ALGEBRA applied
# to hand-chosen numbers. No expectation is produced by calling the function
# under test, by calling one of its helpers, or by searching its source text.
# The two constants below are typed out as literals on purpose: deriving them
# from `CONTRACT_SPECS` / `cost_per_side_usd` would let a change in production
# move the oracle together with the code, which is the vacuous-test class this
# section exists to avoid.
CL_MULT, CL_C = 1000.0, 12.50        # multiplier ; tick_value 10.00 + 2.50
NG_MULT, NG_C = 10000.0, 12.50       # multiplier ; tick_value 10.00 + 2.50

# Deliberately DISTINCT month to month, with sign changes, so a one-month
# timing error cannot coincidentally reproduce the right numbers.
WSEQ = [0.30, 0.80, -0.50, 1.20, 0.10, -0.90, 0.60, 0.40, 0.70, -0.20,
        0.50, 0.90, -0.30, 1.10, 0.20, -0.60, 0.35, 0.85, -0.45, 0.55]


class fixed_decision(object):
    """Pin the DECISION frame while leaving the whole book path in production.

    This fixes an INPUT to the stage under test (strike -> book -> cost), never
    an expectation: every expected value is still derived below from the sealed
    formulae. Column `j` is offset in the sequence so two exposures never carry
    the same weight in the same month.
    """

    def __init__(self, seq):
        self.seq = list(seq)

    def __enter__(self):
        self._real = tc.decision_weights
        seq = self.seq

        def _fake(signal_monthly, vol_monthly):
            cols = {}
            for j, c in enumerate(signal_monthly.columns):
                cols[c] = [seq[(i + j) % len(seq)]
                           for i in range(len(signal_monthly.index))]
            return pd.DataFrame(cols, index=signal_monthly.index)

        tc.decision_weights = _fake
        return self

    def __exit__(self, *exc):
        tc.decision_weights = self._real
        return False


def linear_panel(root, days, base=100.0, step=0.25, n_contracts=1,
                 roll_at=None, blank_days=()):
    """One root, one or two contracts, a strictly deterministic settle path.

    With `n_contracts == 1` the front never rolls. With 2, open interest is
    arranged so the successor overtakes in time for the roll to be effective on
    `roll_at` (the A1 rule keys on t-1 open interest). Both contracts carry the
    SAME price path, so a roll changes the identity without changing the price —
    which keeps the gross oracle a closed form across the roll.
    `blank_days` NaNs out every contract of this root on those sessions, which
    is how a ROOT-LOCAL missing session is produced.
    """
    keys = ["%s%d__2030-%02d-01" % (root, 7000 + i, i + 1) for i in range(n_contracts)]
    px = base + step * np.arange(len(days), dtype="float64")
    settle = pd.DataFrame({k: px.copy() for k in keys}, index=days)
    oi = pd.DataFrame({k: np.full(len(days), 100.0) for k in keys}, index=days)
    if n_contracts >= 2 and roll_at is not None:
        prior = days[days.get_loc(pd.Timestamp(roll_at)) - 1]
        oi.loc[oi.index >= prior, keys[1]] = 500.0
    for d in blank_days:
        if pd.Timestamp(d) in settle.index:
            settle.loc[pd.Timestamp(d), :] = np.nan
    meta = pd.DataFrame({
        "asset": [root] * n_contracts, "_contract_key": keys,
        "expiration": ["2030-%02d-01" % (i + 1) for i in range(n_contracts)]})
    meta["expiration_dt"] = pd.to_datetime(meta["expiration"])
    return settle, oi, meta


def multi_panel(specs, days):
    """Concatenate several `linear_panel` roots into one settle/oi/meta triple."""
    S, O, M = [], [], []
    for s in specs:
        kw = dict(s)
        st, oi, me = linear_panel(kw.pop("root"), days, **kw)
        S.append(st); O.append(oi); M.append(me)
    return (pd.concat(S, axis=1), pd.concat(O, axis=1),
            pd.concat(M, ignore_index=True))


def sessions_by_month(days):
    """The ledger's own index: the panel's sessions minus the first (a return
    needs a predecessor). Grouped by calendar month, in order."""
    per = {}
    for d in days[1:]:
        per.setdefault(d.to_period("M"), []).append(d)
    return per, sorted(per)


def oracle_one_root(days, seq, capital, mult, cps, base, step, n_legs=1):
    """Closed-form expectation for ONE ETF mapped to ONE root, linear prices.

    Written from the sealed text alone:
      * the decision at month-end `i` is struck on the LAST SESSION of month i;
      * `q_i = w_i * K / (multiplier * P(strike_i))`                    (§3.8)
      * month i's gross  = `q_{i-1} * multiplier * (P_t - P_{t-1})` summed over
        month i's sessions — a linear path makes every term `step`;
      * month i's cost   = `|q_{i-1} - q_{i-2}| * C`, because a trade is charged
        to the period in which the position it creates earns (as E does).
    """
    per_month, months = sessions_by_month(days)
    price = {d: base + step * days.get_loc(d) for d in days}
    q = {}
    for i, m in enumerate(months):
        q[m] = (seq[i % len(seq)] / n_legs) * capital / (mult * price[per_month[m][-1]])
    gross, cost = {}, {}
    for i, m in enumerate(months):
        if i == 0:
            continue
        gross[m] = q[months[i - 1]] * mult * step * len(per_month[m])
        cost[m] = abs(q[months[i - 1]] - (q[months[i - 2]] if i >= 2 else 0.0)) * cps
    return months, per_month, q, gross, cost


def as_periods(series):
    return {d.to_period("M"): float(v) for d, v in series.items()}


def run_leg(settle, oi, meta, mapping, seq, capital=1e6, arm="A1"):
    with fixed_decision(seq):
        return tc.construct_futures_leg(settle, oi, meta, arm=arm,
                                        capital=capital, mapping=mapping)


# --------------------------------------------------------------------------- #
def test_book_timing():
    """BLOCKER 1 — the quantity earning month M must follow the M-1 decision."""
    days = pd.bdate_range("2011-03-01", periods=190)
    settle, oi, meta = multi_panel([dict(root="CL", base=100.0, step=0.25)], days)
    res = run_leg(settle, oi, meta, {"USO": ["CL"]}, WSEQ)

    months, per_month, q, g_exp, c_exp = oracle_one_root(
        days, WSEQ, 1e6, CL_MULT, CL_C, 100.0, 0.25)
    got_g, got_c = as_periods(res.gross), as_periods(res.cost)

    ck("every decision-governed month is reported, and no other",
       sorted(got_g) == months[1:], "got %d want %d" % (len(got_g), len(months) - 1))

    worst_g = max(abs(got_g[m] - g_exp[m] / 1e6) for m in got_g)
    worst_c = max(abs(got_c[m] - c_exp[m] / 1e6) for m in got_c)
    ck("monthly GROSS matches the independent M-1 oracle to 1e-12",
       worst_g < 1e-12, "max |diff| = %.3e" % worst_g)
    ck("monthly COST matches the independent M-1 oracle to 1e-12",
       worst_c < 1e-12, "max |diff| = %.3e" % worst_c)

    # The falsification the repair exists for: the SAME arithmetic run one
    # month staler must be visibly wrong, otherwise the oracle above cannot
    # tell M-1 from M-2 and the PASS above would be empty.
    stale = {}
    for i, m in enumerate(months):
        if i >= 2:
            stale[m] = q[months[i - 2]] * CL_MULT * 0.25 * len(per_month[m])
    disagree = sum(1 for m in stale if abs(got_g[m] - stale[m] / 1e6) > 1e-9)
    ck("the M-2 (stale) prediction is rejected in every month it covers",
       disagree == len(stale) and len(stale) > 4,
       "%d/%d months disagree with M-2" % (disagree, len(stale)))

    ck("the reported HELD frame is the decision frame lagged exactly once",
       abs(float(res.positions.iloc[4]["USO"]) - WSEQ[3]) < 1e-12,
       "held[4]=%.4f want w[3]=%.4f" % (float(res.positions.iloc[4]["USO"]), WSEQ[3]))
    ck("the rebalance EVENT is dated at the panel month-end session",
       res.meta["strike_rule"] == "panel_last_session_of_the_decision_month")
    ck("the MARK is the root's last available settle in the decision month",
       res.meta["mark_rule"] == "root_last_available_settle_in_the_decision_month")
    ck("a panel where every root prints at month end produces NO stale mark",
       res.meta["stale_mark_rebalances"] == [],
       str(res.meta["stale_mark_rebalances"])[:80])
    flush("2b. BOOK — blocker 1: month M follows the M-1 decision")


# --------------------------------------------------------------------------- #
def test_book_first_earning():
    """Stage D — a quantity struck at t first earns on the session AFTER t.

    A differential test, so it needs no arithmetic oracle at all: change ONE
    month's decision and nothing before the following month may move.
    """
    days = pd.bdate_range("2011-03-01", periods=170)
    settle, oi, meta = multi_panel([dict(root="CL", base=100.0, step=0.25)], days)
    a = list(WSEQ[:8])
    b = list(a); b[3] = a[3] * 3.0            # perturb decision month 3 only

    ga = as_periods(run_leg(settle, oi, meta, {"USO": ["CL"]}, a).gross)
    gb = as_periods(run_leg(settle, oi, meta, {"USO": ["CL"]}, b).gross)
    months = sorted(ga)

    ck("perturbing decision month 3 leaves months 1..3 bit-identical",
       all(ga[m] == gb[m] for m in months[:3]),
       "first move at %s" % next((str(m) for m in months if ga[m] != gb[m]), "none"))
    ck("the strike month's OWN gross is unchanged (it earns from the NEXT session)",
       ga[months[2]] == gb[months[2]])
    ck("the FOLLOWING month's gross changes (M-1, not M-2)",
       abs(ga[months[3]] - gb[months[3]]) > 1e-9,
       "delta=%.6e" % abs(ga[months[3]] - gb[months[3]]))
    ck("months after the perturbed one are unaffected (no leakage forward)",
       all(abs(ga[m] - gb[m]) < 1e-15 for m in months[4:]))
    flush("2b. BOOK — stage D: first earning session is the one after the strike")


# --------------------------------------------------------------------------- #
def test_book_strike_calendar():
    """BLOCKER 2 — the strike binds to the month's LAST TRADING SESSION."""
    days = pd.bdate_range("2011-03-01", "2011-11-30")
    holiday = pd.Timestamp("2011-06-30")          # holiday-style month end
    days = days.drop(holiday)
    settle, oi, meta = multi_panel([dict(root="CL", base=100.0, step=0.25)], days)
    res = run_leg(settle, oi, meta, {"USO": ["CL"]}, WSEQ)

    ck("fixture really contains a SATURDAY month end (2011-04-30)",
       pd.Timestamp("2011-04-30").dayofweek == 5)
    ck("fixture really contains a SUNDAY month end (2011-07-31, the sealed first "
       "paired month-end)", pd.Timestamp("2011-07-31").dayofweek == 6)
    ck("fixture really contains a holiday-style month end (2011-06-30 removed)",
       holiday not in days and pd.Timestamp("2011-06-30").dayofweek == 3)

    _months, per_month, _q, g_exp, c_exp = oracle_one_root(
        days, WSEQ, 1e6, CL_MULT, CL_C, 100.0, 0.25)
    for label, want in (("2011-04", "2011-04-29"), ("2011-05", "2011-05-31"),
                        ("2011-06", "2011-06-29"), ("2011-07", "2011-07-29")):
        p = pd.Period(label, freq="M")
        ck("last trading session of %s is %s" % (label, want),
           str(per_month[p][-1].date()) == want, str(per_month[p][-1].date()))

    got_g, got_c = as_periods(res.gross), as_periods(res.cost)
    ck("reported months are exactly the months that HAVE sessions (none "
       "fabricated for a non-session month-end label)",
       sorted(got_g) == _months[1:],
       "got %d want %d" % (len(got_g), len(_months) - 1))
    for label in ("2011-05", "2011-06", "2011-07", "2011-08"):
        p = pd.Period(label, freq="M")
        ck("%s is present and matches the last-session oracle" % label,
           p in got_g and abs(got_g[p] - g_exp[p] / 1e6) < 1e-12
           and abs(got_c[p] - c_exp[p] / 1e6) < 1e-12)
    ck("a weekend/holiday month end never skips a month's re-strike",
       all(abs(got_c[pd.Period(l, freq="M")]) > 1e-12
           for l in ("2011-05", "2011-07", "2011-08")))
    flush("2b. BOOK — blocker 2: weekend and holiday month ends")


# --------------------------------------------------------------------------- #
def test_book_gaps():
    """BLOCKER 3 — a root-local missing session is NOT a trade.

    Five cases, each a differential against the same panel without the gap:
      A  one missing session mid-month
      B  three consecutive missing sessions
      C  a missing session immediately before the month-end strike
      D  a genuine roll                (must charge exactly two sides)
      E  a genuine sign change         (must charge |q_old| + |q_new|)
    """
    days = pd.bdate_range("2011-03-01", periods=150)
    mapping = {"USO": ["CL"], "UNG": ["NG"]}
    base_spec = [dict(root="CL", base=100.0, step=0.25),
                 dict(root="NG", base=4.0, step=0.01)]
    s0, o0, m0 = multi_panel(base_spec, days)
    ref = run_leg(s0, o0, m0, mapping, WSEQ)
    ref_c, ref_g = as_periods(ref.cost), as_periods(ref.gross)

    may = [d for d in days if d.month == 5]
    cases = [("A  one missing session", [may[7]]),
             ("B  three consecutive missing sessions", may[7:10]),
             ("C  missing session just before the month-end strike", [may[-2]])]
    for name, blanks in cases:
        spec = [dict(base_spec[0], blank_days=blanks), base_spec[1]]
        s1, o1, m1 = multi_panel(spec, days)
        r1 = run_leg(s1, o1, m1, mapping, WSEQ)
        got = as_periods(r1.cost)
        same = (sorted(got) == sorted(ref_c)
                and max(abs(got[k] - ref_c[k]) for k in got) < 1e-12)
        ck("%s charges NOTHING (no phantom exit/re-entry)" % name, same,
           "" if same else "max diff %.3e"
           % max(abs(got.get(k, 0) - ref_c[k]) for k in ref_c))
        ck("%s is recorded as carried, not silently absorbed" % name,
           r1.meta["gap_sessions_carried_without_trade"].get("USO/CL", 0) == len(blanks),
           str(r1.meta["gap_sessions_carried_without_trade"]))
        ck("%s leaves the OTHER exposure's book untouched" % name,
           abs(as_periods(r1.gross)[pd.Period("2011-08", freq="M")]
               - ref_g[pd.Period("2011-08", freq="M")]) < 1e-9)

    # D — a genuine roll on a FLAT price path: q is constant, so the entry and
    #     the roll are the only trades that can be charged, and the total is a
    #     closed-form number. If the ledger's own roll cash were added on top,
    #     this total would be strictly larger.
    fdays = pd.bdate_range("2011-03-01", periods=120)
    roll_at = pd.Timestamp([d for d in fdays if d.month == 5][10])
    s2, o2, m2 = multi_panel(
        [dict(root="CL", base=100.0, step=0.0, n_contracts=2, roll_at=roll_at)], fdays)
    flat = [0.5] * 12
    r2 = run_leg(s2, o2, m2, {"USO": ["CL"]}, flat)
    q = 0.5 * 1e6 / (CL_MULT * 100.0)
    want = (q + 2.0 * q) * CL_C / 1e6           # entry + roll exit + roll entry
    got_total = float(r2.cost.sum())
    ck("D  flat path, one roll: total cost = (entry + 2 roll sides) exactly",
       abs(got_total - want) < 1e-12,
       "got %.10f want %.10f" % (got_total, want))
    ck("D  gross is exactly zero on a flat price path",
       float(r2.gross.abs().max()) == 0.0)
    ck("D  a constant decision re-strikes at the same size and charges nothing "
       "for it", abs(got_total - want) < 1e-12)

    # E — a sign change must charge |q_old| + |q_new|, not |Δ|position||.
    s3, o3, m3 = multi_panel(
        [dict(root="CL", base=100.0, step=0.0, n_contracts=1)], fdays)
    alt = [0.5, -0.5] * 6
    r3 = run_leg(s3, o3, m3, {"USO": ["CL"]}, alt)
    n_months = len(r3.cost)
    want_e = (q + 2.0 * q * (n_months - 1)) * CL_C / 1e6
    ck("E  alternating sign: entry then TWO sides at every reversal",
       abs(float(r3.cost.sum()) - want_e) < 1e-12,
       "got %.10f want %.10f over %d months" % (float(r3.cost.sum()), want_e, n_months))
    flush("2b. BOOK — blocker 3: gaps carry, real events trade")


# --------------------------------------------------------------------------- #
def test_book_missing_root_month():
    """SEALED §3.5 missing-root-month — renormalise WITHIN the ETF's root map."""
    days = pd.bdate_range("2011-03-01", periods=150)
    dark = [d for d in days if (d.year, d.month) == (2011, 6)]
    spec = [dict(root="CL", base=100.0, step=0.25),
            dict(root="NG", base=4.0, step=0.01, blank_days=dark)]
    s, o, m = multi_panel(spec, days)
    res = run_leg(s, o, m, {"DBA": ["CL", "NG"]}, WSEQ)

    subs = res.meta["missing_root_month_substitutions"]
    ck("the missing root-month is RECORDED, per month, per ETF",
       any(x["decision_month"] == "2011-06" and x["ineligible_roots"] == ["NG"]
           for x in subs), str(subs)[:120])
    ck("the substitution states that the total leg weight is conserved",
       all(x["total_leg_weight_conserved"] for x in subs))

    # July is governed by the June decision, in which only CL was eligible, so
    # CL must carry the WHOLE leg weight — not half of it.
    per_month, months = sessions_by_month(days)
    price = {d: 100.0 + 0.25 * days.get_loc(d) for d in days}
    i_june = months.index(pd.Period("2011-06", freq="M"))
    w_june = WSEQ[i_june % len(WSEQ)]                 # column 0 == CL
    strike = per_month[months[i_june]][-1]
    q_full = w_june * 1e6 / (CL_MULT * price[strike])
    july = pd.Period("2011-07", freq="M")
    got = as_periods(res.gross)[july]
    want_full = q_full * CL_MULT * 0.25 * len(per_month[july]) / 1e6
    want_half = want_full / 2.0
    ck("the surviving root carries the FULL renormalised leg weight",
       abs(got - want_full) < 1e-12, "got %.10f full %.10f" % (got, want_full))
    ck("it is NOT left at half weight (gross exposure is conserved)",
       abs(got - want_half) > 1e-9)
    ck("the dark root's forced exit is disclosed, not silently vanished",
       any(x.get("forced_exit_no_eligible_session") for x in subs))
    flush("2b. BOOK — sealed §3.5 missing-root-month renormalisation")


# --------------------------------------------------------------------------- #
def test_pnl_route_reachability():
    """§3.4 — the accepted cash-first ledger is the ONLY reachable PnL route,
    and only its GROSS leg is consumed. Both are proved by INTERVENTION on the
    live function object, not by searching the source text."""
    days = pd.bdate_range("2011-03-01", periods=110)
    settle, oi, meta = multi_panel([dict(root="CL", base=100.0, step=0.25)], days)
    mapping = {"USO": ["CL"]}
    ref = run_leg(settle, oi, meta, mapping, WSEQ)

    acc = tc.accepted()
    real = acc["x02a"].tsmom_chain_net_returns

    def exploding(*a, **k):
        raise AssertionError("the accepted ledger was bypassed")

    acc["x02a"].tsmom_chain_net_returns = exploding
    try:
        try:
            run_leg(settle, oi, meta, mapping, WSEQ)
            bypassed = True
        except AssertionError:
            bypassed = False
    finally:
        acc["x02a"].tsmom_chain_net_returns = real
    ck("disabling the accepted ledger makes construction IMPOSSIBLE "
       "(no second PnL calculator exists)", not bypassed)

    def inflated_cash(*a, **k):
        net, gross, cash, den = real(*a, **k)
        return net, gross, cash * 1e9 + 1e9, den

    acc["x02a"].tsmom_chain_net_returns = inflated_cash
    try:
        poisoned = run_leg(settle, oi, meta, mapping, WSEQ)
    finally:
        acc["x02a"].tsmom_chain_net_returns = real
    same_g = float((poisoned.gross - ref.gross).abs().max())
    same_c = float((poisoned.cost - ref.cost).abs().max())
    ck("inflating the ledger's CASH leg by 1e9 changes nothing "
       "(ROLL_COST_DOUBLE_COUNT = NO)", same_g == 0.0 and same_c == 0.0,
       "gross drift %.3e cost drift %.3e" % (same_g, same_c))
    ck("the control is live: the poisoned ledger really was called",
       poisoned.net is not None and len(poisoned.net) == len(ref.net))
    flush("2b. BOOK — the cash-first route is the only route, gross leg only")


# --------------------------------------------------------------------------- #
def test_import_purity():
    """§4 — importing the construction module reads NO data file. Instrumented
    mechanically; the instrument itself is proved live by a control read."""
    import builtins
    seen = []
    real = {"open": builtins.open, "io": io.open,
            "csv": pd.read_csv, "pq": pd.read_parquet}

    def rec(fn, tag):
        def w(*a, **k):
            if a:
                seen.append((tag, str(a[0])))
            return fn(*a, **k)
        return w

    def is_data(path):
        low = path.lower()
        return (low.endswith((".csv", ".parquet"))
                or (os.sep + "data" + os.sep) in low or "/data/" in low)

    builtins.open = rec(real["open"], "open")
    io.open = rec(real["io"], "io.open")
    pd.read_csv = rec(real["csv"], "read_csv")
    pd.read_parquet = rec(real["pq"], "read_parquet")
    control = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "_import_purity_control.csv")
    try:
        for k in [k for k in list(sys.modules) if k.startswith("x01_tc_probe")]:
            del sys.modules[k]
        probe = _load("x01_tc_probe", os.path.join(HERE, "x01_target_construction.py"))
        during_import = list(seen)
        # CONTROL: a read the instrument must catch and classify as data.
        with io.open(control, "w", encoding="utf-8") as fh:
            fh.write("a,b\n1,2\n")
        with io.open(control, encoding="utf-8") as fh:
            fh.read()
    finally:
        builtins.open, io.open = real["open"], real["io"]
        pd.read_csv, pd.read_parquet = real["csv"], real["pq"]
        if os.path.exists(control):
            os.remove(control)

    ck("the instrument observes reads at all (control file was recorded)",
       any(p.endswith("_import_purity_control.csv") for _t, p in seen))
    ck("the classifier flags a data-shaped path (control is classified)",
       any(is_data(p) for _t, p in seen if p.endswith("_import_purity_control.csv")))
    offenders = [p for _t, p in during_import if is_data(p)]
    ck("importing the construction module opens NO data file",
       offenders == [], "opened %s" % offenders[:2])
    ck("importing it loads NO accepted component and runs no computation",
       probe._ACCEPTED == {}, str(list(probe._ACCEPTED))[:60])
    ck("the module namespace holds only callables and constants (no frames)",
       not any(isinstance(v, (pd.DataFrame, pd.Series))
               for v in vars(probe).values()))
    flush("2b. IMPORT PURITY — mechanically instrumented, control-verified")


# --------------------------------------------------------------------------- #
# 2c. ROOT-SPECIFIC MONTH-END CAUSALITY
# --------------------------------------------------------------------------- #
# The monthly rebalance is an EXPOSURE-level event. Its quantity is determined
# by a decision that does not exist until the PANEL's month-end session. A root
# whose own last priceable session falls before that date is still MARKED at its
# last available settle — the accepted monthly stale-mark convention — but the
# EVENT cannot be timestamped before the decision that sizes it, which would
# record a transaction earlier than its own cause.
#
# ZC and ZS: multiplier 5000 each; C = tick_value 12.50 + 2.50 = 15.00. Typed as
# literals, never read back from production.
ZC_MULT, ZC_C = 5000.0, 15.00
ZS_MULT, ZS_C = 5000.0, 15.00
# Sealed §3.2: `settle / DIVISOR[root]` is applied BEFORE any notional or cost.
# ZC and ZS are cents-quoted grains, so the divisor is 100. Stated here as an
# independent literal, never read back from the production DIVISOR table.
GRAIN_DIVISOR = 100.0


def root_sessions(days, blank):
    """The sessions a root actually has once `blank` days are NaN-ed out."""
    dark = {pd.Timestamp(d) for d in blank}
    return [d for d in days if d not in dark]


def oracle_basket(days, seq, capital, cfgs):
    """Closed-form expectation for ONE ETF over an N-root basket.

    Independent of production, from the sealed text:
      * the leg weight is split equally over the ELIGIBLE roots (§3.6/§3.5);
      * `q_root(M) = (w_M / n) * K / (multiplier * P_root(mark_M))` where the
        mark is the root's LAST AVAILABLE settle inside decision month M (§3.8);
      * the accepted cash-first ledger's per-contract gross at one of the root's
        own sessions t is `multiplier * (P_t - P_prev_session)` (§3.4), scaled by
        the quantity carried INTO t;
      * a rebalance is charged to the period in which the position it creates
        earns, i.e. the month after the panel month-end event.
    """
    per_month, months = sessions_by_month(days)
    idx = {d: i for i, d in enumerate(days)}
    n = len(cfgs)
    # §3.2 divides the quote BEFORE the notional. It cancels out of gross —
    # `q * mult * dP` scales one way and `q` the other — but NOT out of cost,
    # which is linear in the quantity. That asymmetry is exactly why §3.2 says
    # the divisor binds through the denominator, and it makes cost the channel
    # that actually tests it.
    price = lambda c, d: (c["base"] + c["step"] * idx[d]) / c.get("divisor", 1.0)

    q, mark_of = {}, {}
    for c in cfgs:
        by_m = {}
        for d in c["sessions"]:
            by_m.setdefault(d.to_period("M"), []).append(d)
        c["_by_m"] = by_m
        for i, m in enumerate(months):
            if m not in by_m:
                continue
            mark = by_m[m][-1]
            mark_of[(c["root"], m)] = mark
            q[(c["root"], m)] = ((seq[i % len(seq)] / n) * capital
                                 / (c["mult"] * price(c, mark)))

    gross, cost = {}, {}
    for i, m in enumerate(months):
        if i == 0:
            continue
        g = 0.0
        k = 0.0
        for c in cfgs:
            held_q = q.get((c["root"], months[i - 1]))
            rs = c["sessions"]
            if held_q is not None:
                for j in range(1, len(rs)):
                    if rs[j].to_period("M") == m:
                        g += held_q * c["mult"] * (price(c, rs[j]) - price(c, rs[j - 1]))
            prev2 = q.get((c["root"], months[i - 2])) if i >= 2 else 0.0
            if held_q is not None:
                k += abs(held_q - (prev2 or 0.0)) * c["cps"]
        gross[m], cost[m] = g, k
    return months, per_month, q, mark_of, gross, cost


def test_root_specific_rebalance_timestamp():
    """A root that stops printing before the panel's month-end still rebalances
    ON the panel's month-end, marked at its own last available settle."""
    days = pd.bdate_range("2011-03-01", periods=150)
    may = [d for d in days if (d.year, d.month) == (2011, 5)]
    dark = may[-2:]                    # root A misses the FINAL TWO sessions
    s, o, m = multi_panel(
        [dict(root="ZC", base=500.0, step=0.40, blank_days=dark),
         dict(root="ZS", base=1200.0, step=0.90)], days)
    res = run_leg(s, o, m, {"DBA": ["ZC", "ZS"]}, WSEQ)

    cfgs = [dict(root="ZC", base=500.0, step=0.40, mult=ZC_MULT, cps=ZC_C,
                 divisor=GRAIN_DIVISOR, sessions=root_sessions(days, dark)),
            dict(root="ZS", base=1200.0, step=0.90, mult=ZS_MULT, cps=ZS_C,
                 divisor=GRAIN_DIVISOR, sessions=list(days))]
    months, per_month, q, mark_of, g_exp, c_exp = oracle_basket(
        days, WSEQ, 1e6, cfgs)
    MAY, JUN = pd.Period("2011-05", freq="M"), pd.Period("2011-06", freq="M")

    ck("fixture: root A really loses the panel's final two May sessions",
       [d for d in cfgs[0]["sessions"] if d.to_period("M") == MAY][-1] == may[-3]
       and per_month[MAY][-1] == may[-1])
    ck("fixture: the peer root remains priceable through the panel month end",
       [d for d in cfgs[1]["sessions"] if d.to_period("M") == MAY][-1] == may[-1])

    # A — the EVENT timestamp
    stale = res.meta["stale_mark_rebalances"]
    hit = [x for x in stale if x["decision_month"] == "2011-05" and x["root"] == "ZC"]
    ck("A  the stale-mark rebalance is disclosed for root A in 2011-05",
       len(hit) == 1, str(stale)[:100])
    if hit:
        ck("A  root A's rebalance EVENT is dated at panel_last_session[M]",
           hit[0]["event_date"] == str(may[-1]), hit[0]["event_date"])
        ck("A  it is NOT dated at root A's own last priceable session",
           hit[0]["event_date"] != str(may[-3]))
        # C — the mark
        ck("C  root A is MARKED at its last available settle inside May",
           hit[0]["mark_date"] == str(may[-3]), hit[0]["mark_date"])
    ck("A  the peer root, printing at month end, raises NO stale mark",
       not any(x["root"] == "ZS" for x in stale))

    # B — the sizing still comes from the exposure-level month-end decision,
    #     and D/E — quantity and monthly gross are the sealed ones.
    got_g, got_c = as_periods(res.gross), as_periods(res.cost)
    worst_g = max(abs(got_g[k] - g_exp[k] / 1e6) for k in got_g)
    ck("B/D/E  monthly GROSS matches the sealed-quantity oracle to 1e-12",
       worst_g < 1e-12, "max |diff| = %.3e" % worst_g)

    # C falsification: sizing root A on the PANEL month-end price instead of its
    # own last available settle would be a different, wrong number.
    wrong = [dict(cfgs[0], sessions=list(days)), dict(cfgs[1])]
    _m2, _p2, _q2, _mk2, g_wrong, _c2 = oracle_basket(days, WSEQ, 1e6, wrong)
    _m3, _p3, _q3, _mk3, _g3, c_undiv = oracle_basket(
        days, WSEQ, 1e6, [dict(c, divisor=1.0) for c in cfgs])
    ck("C  marking root A at the panel month-end price would NOT match "
       "(the stale mark is really being used)",
       abs(got_g[JUN] - g_wrong[JUN] / 1e6) > 1e-9,
       "delta = %.3e" % abs(got_g[JUN] - g_wrong[JUN] / 1e6))

    # F/G — total cash cost and its reporting period
    worst_c = max(abs(got_c[k] - c_exp[k] / 1e6) for k in got_c)
    ck("G  monthly COST matches the earning-period oracle to 1e-12",
       worst_c < 1e-12, "max |diff| = %.3e" % worst_c)
    ck("G  root A's May rebalance is charged to JUNE, the month it earns in",
       abs(got_c[JUN] - c_exp[JUN] / 1e6) < 1e-12 and got_c[JUN] > 0)
    ck("F  total cash cost over the reported window matches the oracle total",
       abs(float(res.cost.sum()) - sum(c_exp[k] for k in got_c) / 1e6) < 1e-12,
       "got %.12f" % float(res.cost.sum()))
    ck("§3.2  the cents divisor is applied BEFORE the notional (an undivided "
       "quote would give a 100x smaller cash cost)",
       abs(got_c[JUN] - c_undiv[JUN] / 1e6) > 1e-9,
       "divided %.10f undivided %.10f" % (c_exp[JUN] / 1e6, c_undiv[JUN] / 1e6))
    flush("2c. CAUSALITY - root-specific month-end rebalance timestamp")


def test_decision_uses_the_panel_month_end():
    """Why the event must carry the panel's date: the exposure-level decision
    reads the panel's FINAL session, which root A never saw.

    This runs the REAL signal/sizing path - no injected decision frame - and is
    a differential test, so it needs no arithmetic oracle.
    """
    days = pd.bdate_range("2011-03-01", periods=430)
    target = sorted({d.to_period("M") for d in days})[-3]
    in_target = [d for d in days if d.to_period("M") == target]
    dark = in_target[-2:]
    spec = [dict(root="ZC", base=500.0, step=0.40, blank_days=dark),
            dict(root="ZS", base=1200.0, step=0.90)]

    s0, o0, m0 = multi_panel(spec, days)
    s1 = s0.copy()
    for col in [c for c in s1.columns if c.startswith("ZS")]:
        s1.loc[in_target[-1], col] = s1.loc[in_target[-1], col] * 0.80

    base = tc.construct_futures_leg(s0, o0, m0, arm="A1", capital=1e6,
                                    mapping={"DBA": ["ZC", "ZS"]})
    pert = tc.construct_futures_leg(s1, o0, m0, arm="A1", capital=1e6,
                                    mapping={"DBA": ["ZC", "ZS"]})
    bp = {d.to_period("M"): float(v) for d, v in base.positions["DBA"].items()}
    pp = {d.to_period("M"): float(v) for d, v in pert.positions["DBA"].items()}
    after = target + 1
    ck("the real signal path produced a live decision frame",
       target in bp and after in bp and pd.notna(bp[after]),
       "months=%d" % len(bp))
    if target in bp and after in bp:
        moved = abs(pp[after] - bp[after])
        ck("perturbing the PEER's final session materially moves the decision "
           "that root A's rebalance carries",
           moved > 1e-9 and moved > 0.05 * max(abs(bp[after]), 1e-12),
           "held[M+1] %.6f -> %.6f" % (bp[after], pp[after]))
        ck("the PRIOR month's decision is untouched (the perturbation is "
           "confined to month M's decision)",
           abs(pp[target] - bp[target]) < 1e-12)
    ck("root A had no session on the perturbed date, yet its rebalance is "
       "dated there",
       any(x["event_date"] == str(in_target[-1]) and x["root"] == "ZC"
           for x in base.meta["stale_mark_rebalances"]),
       str(base.meta["stale_mark_rebalances"])[:100])
    flush("2c. CAUSALITY - the decision reads the panel's final session")


# --------------------------------------------------------------------------- #
# 2d. A GENUINE ROLL BETWEEN THE MARK DATE AND THE EVENT DATE
# --------------------------------------------------------------------------- #
# The hard case for the two-date rebalance model. A root's MARK date (its last
# priceable session in the decision month) can precede the panel's EVENT date,
# and the root's own roll rule can hand the front to a NEW contract in between.
# The delayed rebalance must then re-size the identity the book is ACTUALLY
# holding. Writing the mark date's — now obsolete — identity back would undo a
# real roll and manufacture a round trip that never happened.
#
# Literal constants, typed out and never read back from production:
#   CL  multiplier 1000, per-side C = tick_value 10.00 + 2.50 = 12.50, divisor 1
#   NG  multiplier 10000, per-side C = tick_value 10.00 + 2.50 = 12.50, divisor 1
CLM, NGM, SIDE = 1000.0, 10000.0, 12.50
C1_BASE, C2_BASE, A_STEP = 100.00, 130.00, 0.25
NG_BASE, NG_STEP = 4.00, 0.01

# SAME-SIGN weights, deliberately. This fixture discriminates "re-size the
# identity actually held" (one side, `|q_new - q_old|`) from "exit the held one
# and re-enter the obsolete one" (two sides, `|q_old| + |q_new|`). Those two
# quantities are EQUAL whenever the position reverses sign, which would make the
# discriminating assertion vacuous — the sign-change path is covered separately
# in section 2b case E. Non-vacuity is asserted below rather than assumed.
IDSEQ = [0.30, 0.80, 0.55, 0.95, 0.40, 0.70, 0.25, 0.90]


def roll_gap_panel(days, dark):
    """Root A (CL, two contracts) plus a peer (NG) that prices every session.

    C1 is priced on every session; C2 is priced on every session EXCEPT `dark`,
    which is the panel's final two sessions of the target month. Open interest
    hands the front to C2 on the FIRST dark session, so between root A's mark
    date and the panel's event date the front really has rolled — while C2's
    missing settle is what stops those sessions from being priceable.

    The peer prices throughout, so the panel calendar keeps every session and
    the event date is a real session even for a root that cannot be marked on it.
    """
    c1, c2, ng = "CL7001__2030-01-01", "CL7002__2030-02-01", "NG7001__2030-01-01"
    i = np.arange(len(days), dtype="float64")
    settle = pd.DataFrame({c1: C1_BASE + A_STEP * i,
                           c2: C2_BASE + A_STEP * i,
                           ng: NG_BASE + NG_STEP * i}, index=days)
    settle.loc[[pd.Timestamp(d) for d in dark], c2] = np.nan
    oi = pd.DataFrame({c1: np.full(len(days), 100.0),
                       c2: np.full(len(days), 10.0),
                       ng: np.full(len(days), 100.0)}, index=days)
    # A1 keys on t-1 open interest, so the successor must lead by the session
    # BEFORE the first dark day for the roll to be effective ON it.
    lead_from = days[days.get_loc(pd.Timestamp(dark[0])) - 1]
    oi.loc[oi.index >= lead_from, c2] = 500.0
    meta = pd.DataFrame({
        "asset": ["CL", "CL", "NG"], "_contract_key": [c1, c2, ng],
        "expiration": ["2030-01-01", "2030-02-01", "2030-01-01"]})
    meta["expiration_dt"] = pd.to_datetime(meta["expiration"])
    return settle, oi, meta, (c1, c2, ng)


def test_roll_between_mark_and_event():
    days = pd.bdate_range("2011-03-01", periods=110)
    may = [d for d in days if (d.year, d.month) == (2011, 5)]
    d1, d2, d3 = may[-3], may[-2], may[-1]        # mark, roll, event
    settle, oi, meta, (c1, c2, _ng) = roll_gap_panel(days, (d2, d3))
    mapping = {"USO": ["CL"], "UNG": ["NG"]}

    # --- fixture shape. These check the FIXTURE is the one described, not the
    #     answer; every expected number below comes from the literals above.
    listed = tc.listed_keys_for_root(meta, "CL", settle.columns)
    front = tc.front_series(oi.reindex(columns=listed), listed, rule="A1")
    ck("fixture: the front is still C1 on root A's mark date",
       front.at[d1] == c1, str(front.at[d1]))
    ck("fixture: a GENUINE roll to C2 happens between the mark and the event",
       front.at[d2] == c2 and front.at[d3] == c2)
    ck("fixture: C2 has no settle on those two sessions, so they are not "
       "priceable and the mark cannot advance",
       bool(pd.isna(settle.at[d2, c2])) and bool(pd.isna(settle.at[d3, c2])))
    ck("fixture: C1 still settles there, so root A keeps the sessions",
       bool(pd.notna(settle.at[d2, c1])) and bool(pd.notna(settle.at[d3, c1])))

    res = run_leg(settle, oi, meta, mapping, IDSEQ)

    # --- the two dates, as disclosed by production
    hit = [x for x in res.meta["stale_mark_rebalances"]
           if x["decision_month"] == "2011-05" and x["root"] == "CL"]
    ck("the May rebalance is disclosed as mark-before-event", len(hit) == 1,
       str(res.meta["stale_mark_rebalances"])[:100])
    if hit:
        ck("mark date = root A's last priceable session",
           hit[0]["mark_date"] == str(d1), hit[0]["mark_date"])
        ck("event date = the panel's month-end session",
           hit[0]["event_date"] == str(d3), hit[0]["event_date"])
        ck("the MARK sits on the now-obsolete identity C1",
           hit[0]["marked_on"] == c1, str(hit[0]["marked_on"]))

    # --- independent literal oracle -----------------------------------------
    idx = {d: k for k, d in enumerate(days)}
    per_month, months = sessions_by_month(days)
    price_c1 = lambda d: C1_BASE + A_STEP * idx[d]
    price_c2 = lambda d: C2_BASE + A_STEP * idx[d]
    price_ng = lambda d: NG_BASE + NG_STEP * idx[d]

    # marks: root A is marked on C1 up to and including May (its May mark is d1,
    # before the roll); from June the front is C2 and it marks on C2.
    marks = {}
    for j, m in enumerate(months):
        L = per_month[m][-1]
        marks[m] = (d1, price_c1(d1)) if m == pd.Period("2011-05", freq="M") else (
            (L, price_c1(L)) if L <= d1 else (L, price_c2(L)))
    # q_j = (w_j / 2) * K / (multiplier * P_mark) -- two ETFs, so the sleeve's
    # equal weighting halves each leg (§3.6); one root per ETF, so no further
    # split. Column 0 is USO, column 1 is UNG, per `fixed_decision`.
    q = {m: (IDSEQ[j % len(IDSEQ)] / 2.0) * 1e6 / (CLM * marks[m][1])
         for j, m in enumerate(months)}
    pq = {m: (IDSEQ[(j + 1) % len(IDSEQ)] / 2.0) * 1e6
              / (NGM * price_ng(per_month[m][-1]))
          for j, m in enumerate(months)}

    # the accepted ledger prices the contract held at t-1, so root A has NO row
    # on the event day (C2 had no settle the session before) nor on the first
    # June session (C2 had no settle on the event day). Every other session
    # contributes exactly `multiplier * step`, whichever contract is held.
    jun_first = [d for d in days if (d.year, d.month) == (2011, 6)][0]
    rows_a = [d for d in days[1:] if d not in (d3, jun_first)]
    ck("oracle: root A loses exactly two ledger rows to the dark pair",
       len(rows_a) == len(days) - 3)

    g_exp, c_exp = {}, {}
    for j, m in enumerate(months):
        if j == 0:
            continue
        prev = months[j - 1]
        g_exp[m] = (q[prev] * CLM * A_STEP * sum(1 for d in rows_a if d.to_period("M") == m)
                    + pq[prev] * NGM * NG_STEP * len(per_month[m]))
        prev2_q = q[months[j - 2]] if j >= 2 else 0.0
        prev2_p = pq[months[j - 2]] if j >= 2 else 0.0
        k = abs(q[prev] - prev2_q) * SIDE + abs(pq[prev] - prev2_p) * SIDE
        if m == pd.Period("2011-05", freq="M"):
            # the genuine roll: the quantity in force leaves C1 and enters C2,
            # two sides, charged on the session after it happens (still May).
            k += 2.0 * abs(q[months[1]]) * SIDE
        c_exp[m] = k

    got_g, got_c = as_periods(res.gross), as_periods(res.cost)
    MAY = pd.Period("2011-05", freq="M")
    JUN = pd.Period("2011-06", freq="M")

    wg = max(abs(got_g[m] - g_exp[m] / 1e6) for m in got_g)
    ck("monthly GROSS matches the independent literal oracle to 1e-12",
       wg < 1e-12, "max |diff| = %.3e" % wg)
    wc = max(abs(got_c[m] - c_exp[m] / 1e6) for m in got_c)
    ck("monthly COST matches the independent literal oracle to 1e-12",
       wc < 1e-12, "max |diff| = %.3e" % wc)

    # --- the six required flags, each against a literal counterfactual --------
    resize_may = (abs(q[months[1]] - q[months[0]]) * SIDE
                  + abs(pq[months[1]] - pq[months[0]]) * SIDE) / 1e6
    roll_two_sides = 2.0 * abs(q[months[1]]) * SIDE / 1e6
    ck("the roll counterfactuals are numerically distinct (this test is not "
       "vacuous)", roll_two_sides > 1e-9)
    ck("INTERMEDIATE_ROLL_PRESERVED  May cost minus the re-size is exactly the "
       "roll's two sides",
       abs((got_c[MAY] - resize_may) - roll_two_sides) < 1e-12,
       "residual %.12f want %.12f" % (got_c[MAY] - resize_may, roll_two_sides))
    ck("ROLL_EXIT_ENTRY_CHARGED_ONCE  a second roll charge would not fit",
       abs(got_c[MAY] - (resize_may + 2.0 * roll_two_sides)) > 1e-9)
    ck("ROLL_EXIT_ENTRY_CHARGED_ONCE  and the roll is not missing either",
       abs(got_c[MAY] - resize_may) > 1e-9)

    peer_jun = abs(pq[months[2]] - pq[months[1]]) * SIDE / 1e6
    one_side = abs(q[months[2]] - q[months[1]]) * SIDE / 1e6
    revert_pair = (abs(q[months[1]]) + abs(q[months[2]])) * SIDE / 1e6
    phantom_back = 2.0 * abs(q[months[2]]) * SIDE / 1e6
    ck("the identity counterfactuals are numerically distinct (this test is "
       "not vacuous): one side %.9f vs reverting pair %.9f"
       % (one_side, revert_pair),
       abs(one_side - revert_pair) > 1e-9)
    ck("EVENT_RESIZE_APPLIES_TO_CURRENT_IDENTITY  the delayed rebalance is ONE "
       "side on the identity actually held",
       abs((got_c[JUN] - peer_jun) - one_side) < 1e-12,
       "residual %.12f want %.12f" % (got_c[JUN] - peer_jun, one_side))
    ck("STALE_IDENTITY_NOT_RESTORED  June's root-A charge IS the single "
       "re-size, and is none of the reverting forms",
       abs((got_c[JUN] - peer_jun) - one_side) < 1e-12
       and abs((got_c[JUN] - peer_jun) - revert_pair) > 1e-9
       and abs((got_c[JUN] - peer_jun) - (revert_pair + phantom_back)) > 1e-9,
       "got %.12f  one-side %.12f  revert %.12f  revert+return %.12f"
       % (got_c[JUN] - peer_jun, one_side, revert_pair,
          revert_pair + phantom_back))
    ck("FALSE_ROUND_TRIP_CREATED = NO  no reverting pair, and no rolling back",
       abs((got_c[JUN] - peer_jun) - (revert_pair + phantom_back)) > 1e-9)
    ck("NEXT_SESSION_HAS_NO_PHANTOM_TRADE  June leaves no room for a return "
       "trip on the session after the event",
       abs((got_c[JUN] - peer_jun) - (one_side + phantom_back)) > 1e-9
       and abs((got_c[JUN] - peer_jun) - one_side) < 1e-12)
    ck("June's total cost is exactly the delayed re-size plus the peer's own "
       "re-size, with nothing else in it",
       abs(got_c[JUN] - (one_side + peer_jun)) < 1e-12,
       "got %.12f want %.12f" % (got_c[JUN], one_side + peer_jun))
    flush("2d. IDENTITY - a genuine roll between the mark and the event")


# --------------------------------------------------------------------------- #
# 2e. THE §7 DIAGNOSTIC INTERFACE — additive, authoritative, inert
# --------------------------------------------------------------------------- #
# Sealed §7 needs two per-exposure objects the legs build and then discard: the
# monthly return frame per mapped pair, and the composite signal frame. They are
# now surfaced on `ConstructionResult.diagnostics`.
#
# The tests below do not ask whether the numbers "look right". They ask whether
# the exposed objects ARE the ones the construction actually used, which is a
# closed-form question in both cases:
#   * E's gross is `(positions × monthly_returns).sum()` by the accepted
#     `portfolio_returns`, so the exposed frame must reproduce `res.gross`;
#   * the composite is a function of the same monthly frame, so recomputing it
#     from the exposed returns must reproduce the exposed signal.
# A reconstruction that merely resembled the originals would fail both.
def frames_match(a, b, min_finite):
    """Frame equality that one-sided missingness cannot slip through.

    The previous comparisons reduced a difference with `nanmax`, which ignores a
    NaN on either side — so blanking a valid row on ONE side left every check
    green. Index, columns and the MISSING-VALUE MASK are compared first, and only
    then are the finite values compared. `min_finite` is required so an all-NaN
    or mostly-NaN fixture cannot pass by having nothing to disagree about.

    Returns `(ok, detail)`.
    """
    if list(a.columns) != list(b.columns):
        return False, "columns differ: %s vs %s" % (list(a.columns), list(b.columns))
    if not a.index.equals(b.index):
        return False, "index differs (%d vs %d rows)" % (len(a.index), len(b.index))
    ma, mb = a.isna(), b.isna()
    if not ma.equals(mb):
        n = int((ma != mb).to_numpy().sum())
        return False, "missing-value masks differ in %d cell(s)" % n

    # FINITE means `np.isfinite`, not "not null". `notna` counts ±inf as present,
    # so a frame of 99 infinities and one real number satisfied a coverage
    # requirement of 50 — and `inf - inf` is NaN, which `nanmax` then discards,
    # so the value comparison saw nothing either. Both holes are closed here: an
    # unexpected infinity in a finite-domain frame is rejected outright rather
    # than counted, and coverage is counted over genuinely finite cells.
    fa = np.isfinite(a.to_numpy(dtype="float64"))
    fb = np.isfinite(b.to_numpy(dtype="float64"))
    inf_a = int((~fa & ~ma.to_numpy()).sum())
    inf_b = int((~fb & ~mb.to_numpy()).sum())
    if inf_a or inf_b:
        return False, ("unexpected non-finite value(s) in a finite-domain frame: "
                       "%d on the left, %d on the right (±inf is not a missing "
                       "value and is never treated as one)" % (inf_a, inf_b))
    if not (fa == fb).all():
        return False, ("finite masks differ in %d cell(s)"
                       % int((fa != fb).sum()))

    finite = int(fa.sum())
    if finite < min_finite:
        return False, ("only %d genuinely finite value(s) compared, below the "
                       "required %d" % (finite, min_finite))
    delta = np.abs(a.to_numpy(dtype="float64") - b.to_numpy(dtype="float64"))
    worst = float(np.max(delta[fa])) if finite else 0.0
    if worst != 0.0:
        return False, "max |diff| = %.3e over %d finite values" % (worst, finite)
    return True, "%d genuinely finite values, masks identical" % finite


def test_finite_coverage_comparator():
    """BLOCKER B — the frame comparator's coverage gate must mean `np.isfinite`.

    `notna` treats ±inf as a present value, so a frame that is 99 parts infinity
    and one part real number satisfied `min_finite = 50`; and because
    `inf - inf` is NaN, the value comparison was then suppressed by `nanmax` as
    well. Each adversarial frame below asserts the comparator's VERDICT, so a
    revert to `notna` flips these assertions rather than hiding behind them.
    """
    idx = pd.date_range("2011-07-31", periods=100, freq="ME")

    # A — 99 inf + 1 finite, identical on both sides
    a = pd.DataFrame({"X": [np.inf] * 99 + [1.0]}, index=idx)
    ok, detail = frames_match(a, a.copy(), min_finite=50)
    ck("A  99 inf + 1 finite with min_finite=50 is REFUSED", not ok, detail)
    ck("A  the fixture really has only ONE finite value, while `notna` counts "
       "100 (so the case is discriminating)",
       int(np.isfinite(a.to_numpy()).sum()) == 1
       and int(a.notna().to_numpy().sum()) == 100)

    # B — one side finite, the other inf, same NaN mask
    b1 = pd.DataFrame({"X": [1.0] * 100}, index=idx)
    b2 = b1.copy(); b2.iloc[7, 0] = np.inf
    ok, detail = frames_match(b1, b2, min_finite=50)
    ck("B  finite on one side, inf on the other is REFUSED", not ok, detail)
    ck("B  and neither side is NaN there, so a mask check alone would miss it",
       not bool(b1.isna().iloc[7, 0]) and not bool(b2.isna().iloc[7, 0]))

    # C — +inf against -inf
    c1 = b1.copy(); c1.iloc[3, 0] = np.inf
    c2 = b1.copy(); c2.iloc[3, 0] = -np.inf
    ok, detail = frames_match(c1, c2, min_finite=50)
    ck("C  +inf against -inf is REFUSED", not ok, detail)
    ck("C  their difference is NaN, which is exactly what nanmax used to "
       "swallow", bool(np.isnan(np.inf - np.inf)))

    # D — a genuinely finite frame above the threshold
    r = np.random.default_rng(3)
    d1 = pd.DataFrame({"X": r.normal(0.0, 1.0, 100)}, index=idx)
    ok, detail = frames_match(d1, d1.copy(), min_finite=50)
    ck("D  a valid finite frame above the threshold PASSES", ok, detail)
    ok, detail = frames_match(d1, d1 + 1e-9, min_finite=50)
    ck("D  and a real numeric difference in it is still caught", not ok, detail)

    # E — matching NaN masks are legitimate (warm-up months) if enough remains
    e1 = d1.copy(); e1.iloc[:20, 0] = np.nan
    ok, detail = frames_match(e1, e1.copy(), min_finite=50)
    ck("E  matching NaN masks with sufficient finite coverage PASSES", ok, detail)
    ck("E  and the coverage counted is the finite remainder, not the row count",
       "80 genuinely finite" in detail, detail)
    e2 = e1.copy(); e2.iloc[25, 0] = np.nan
    ok, detail = frames_match(e1, e2, min_finite=50)
    ck("E  a one-sided extra NaN is still REFUSED by the mask check", not ok,
       detail)

    # non-vacuity: the threshold is actually consulted
    ok, detail = frames_match(d1, d1.copy(), min_finite=101)
    ck("the coverage threshold is really enforced (101 > 100 available)",
       not ok, detail)
    flush("2e. FINITE COVERAGE — ±inf is not a value, and never a missing one")


def test_diagnostic_interface():
    daily = synth_etf_daily()
    res = tc.construct_E(daily)
    d = res.diagnostics
    ck("E exposes a diagnostics payload", d is not None)
    ck("it declares the arm it came from", d.arm == "E")
    ck("the exposures are the sealed four, in the declared order",
       d.columns == list(tc.SEALED_ETFS), str(d.columns))
    ck("the monthly return frame is indexed by month-end",
       bool(d.monthly_returns.index.equals(tc.month_end_prices(daily).index)))

    # IDENTITY 1 — the exposed frame is the one that earned E's gross.
    rets = d.monthly_returns.reindex_like(res.positions)
    regross = (res.positions * rets).sum(axis=1, min_count=1).dropna()
    common = regross.index.intersection(res.gross.index)
    worst = float(np.max(np.abs(regross.loc[common] - res.gross.loc[common])))
    ck("the exposed monthly returns REPRODUCE E's gross exactly, so they are "
       "the authoritative frame and not a reconstruction",
       worst == 0.0 and len(common) == len(res.gross),
       "max |diff| = %.3e over %d/%d months" % (worst, len(common), len(res.gross)))

    # IDENTITY 2 — the exposed signal is the composite of that same frame.
    recon = (1.0 + d.monthly_returns.fillna(0.0)).cumprod()
    ok, detail = frames_match(d.composite_signal, tc.composite_signal(recon),
                              min_finite=50)
    ck("the exposed composite signal is the composite OF the exposed returns, "
       "index, columns and MISSING MASK included", ok, detail)
    ck("the signal lies on the sealed mean-of-signs grid",
       set(np.unique(d.composite_signal.dropna(how="all").stack().round(10)))
       <= {-1.0, -0.75, -0.5, -0.25, 0.0, 0.25, 0.5, 0.75, 1.0})

    # NO LOOKAHEAD — truncating the input cannot change earlier diagnostics.
    cut = daily.loc[:daily.index[int(len(daily) * 0.7)]]
    dc = tc.construct_E(cut).diagnostics
    ov = dc.monthly_returns.index.intersection(d.monthly_returns.index)[:-1]
    ok, detail = frames_match(dc.monthly_returns.loc[ov],
                              d.monthly_returns.loc[ov], min_finite=40)
    ck("truncating the panel leaves earlier monthly returns unchanged "
       "(no lookahead)", ok, detail)
    ok, detail = frames_match(dc.composite_signal.loc[ov],
                              d.composite_signal.loc[ov], min_finite=40)
    ck("and leaves the earlier composite unchanged, mask included", ok, detail)

    # MISSING DATA — the frame carries the ACCEPTED primitive's own treatment,
    # whatever that is, rather than a treatment invented for the diagnostic.
    # `monthly_asset_returns` is `pct_change()` with pandas' default pad, and E's
    # gross already depends on exactly that; the hole itself is handled by the
    # sealed §3.5 incomplete-sleeve rule, which drops the month from the
    # evaluated stream. Asserting NaN here would have asserted a behaviour the
    # accepted layer does not have.
    holed = daily.copy()
    hole = holed.index[(holed.index.year == 2019) & (holed.index.month == 6)]
    holed.loc[hole, "DBA"] = np.nan
    rh = tc.construct_E(holed)
    dh = rh.diagnostics
    want = tc.accepted()["performance"].monthly_asset_returns(
        tc.month_end_prices(holed[list(tc.SEALED_ETFS)]))
    ck("with a hole, the diagnostic frame is bit-identical to the accepted "
       "primitive's own output",
       bool(dh.monthly_returns.equals(want)))
    # §3.5 drops the month the holed DECISION governs, not the holed month
    # itself: positions are `weights.shift(1)`, so June's unusable decision
    # removes JULY, while June keeps the position May decided.
    rb = tc.construct_E(daily)
    ck("§3.5 drops the month the holed decision GOVERNS (2019-07), not the "
       "holed month itself (2019-06)",
       pd.Timestamp("2019-07-31") not in rh.net.index
       and pd.Timestamp("2019-06-30") in rh.net.index
       and pd.Timestamp("2019-07-31") in rb.net.index,
       "incomplete-sleeve drops %d -> %d"
       % (rb.meta["months_dropped_incomplete_sleeve"],
          rh.meta["months_dropped_incomplete_sleeve"]))

    # DETERMINISM
    ck("column ordering is deterministic across runs",
       tc.construct_E(daily).diagnostics.columns == d.columns)

    # every arm exposes it
    # long enough that the 12-month composite is actually defined; a 7-month
    # fixture leaves every composite NaN and the comparison below vacuous
    days = pd.bdate_range("2011-03-01", periods=430)
    s, o, m = multi_panel([dict(root="CL", base=100.0, step=0.25),
                           dict(root="NG", base=4.0, step=0.01)], days)
    mapping = {"USO": ["CL"], "UNG": ["NG"]}
    for arm in ("A1", "S1", "S2"):
        r = run_leg(s, o, m, mapping, WSEQ, arm=arm)
        ck("arm %s exposes diagnostics tagged with its own arm" % arm,
           r.diagnostics is not None and r.diagnostics.arm == arm)
        ck("arm %s exposes the mapped exposures, not the roots" % arm,
           r.diagnostics.columns == ["USO", "UNG"], str(r.diagnostics.columns))
        rec = (1.0 + r.diagnostics.monthly_returns.fillna(0.0)).cumprod()
        ok, detail = frames_match(r.diagnostics.composite_signal,
                                  tc.composite_signal(rec), min_finite=10)
        ck("arm %s composite matches the composite of its own returns, mask "
           "included" % arm, ok, detail)
    flush("2e. DIAGNOSTIC INTERFACE — authoritative objects, additive only")


def test_identity_turnover():
    """BLOCKER 4 — §7 turnover for a futures leg is an IDENTITY-trade quantity.

    An equal-size roll moves the exposure weight by exactly zero while the §3.8
    book exits one contract and enters another, and the cash ledger charges both
    sides. A weight-difference turnover therefore reports 0 for a month in which
    the leg demonstrably traded, which is why the diagnostic is taken from the
    book itself.

    Literal constants, typed out: CL multiplier 1000, per-side C = 12.50.
    Flat prices keep `q = w·K/(mult·P)` constant, so the only trades are the ones
    each case is about.
    """
    CLM, SIDE = 1000.0, 12.50
    fdays = pd.bdate_range("2011-03-01", periods=120)
    may = [d for d in fdays if d.month == 5]
    q = 0.5 * 1e6 / (CLM * 100.0)          # = 5.0 contracts

    def leg(seq, n_contracts=1, roll_at=None):
        s, o, m = multi_panel([dict(root="CL", base=100.0, step=0.0,
                                    n_contracts=n_contracts, roll_at=roll_at)], fdays)
        return run_leg(s, o, m, {"USO": ["CL"]}, seq)

    # A — no trade after the entry: constant decision, one contract
    a = leg([0.5] * 12)
    ta = a.diagnostics.identity_turnover
    ck("A  constant decision: only the initial entry trades, exactly q",
       abs(float(ta.sum()) - q) < 1e-12, "got %r want %r" % (float(ta.sum()), q))

    # B — pure resize, no roll: 0.5 -> 0.75 changes q by half of itself
    b = leg([0.5, 0.75] + [0.75] * 10)
    q2 = 0.75 * 1e6 / (CLM * 100.0)
    tb = b.diagnostics.identity_turnover
    ck("B  pure resize: entry + |q2 - q|, literal oracle",
       abs(float(tb.sum()) - (q + abs(q2 - q))) < 1e-12,
       "got %r want %r" % (float(tb.sum()), q + abs(q2 - q)))

    # C — sign reversal: +q -> -q trades 2q on the same identity
    c = leg([0.5, -0.5] + [-0.5] * 10)
    tc_ = c.diagnostics.identity_turnover
    ck("C  sign reversal charges TWO sides on one identity",
       abs(float(tc_.sum()) - (q + 2.0 * q)) < 1e-12,
       "got %r want %r" % (float(tc_.sum()), 3.0 * q))

    # D — the equal-size roll: THE case a weight difference cannot see
    d = leg([0.5] * 12, n_contracts=2, roll_at=may[10])
    td = d.diagnostics.identity_turnover
    weight_turnover = float(pd.DataFrame(d.positions).diff().abs()
                            .sum(axis=1, min_count=1).fillna(0.0).sum())
    ck("D  equal-size roll: identity turnover = entry + two roll sides",
       abs(float(td.sum()) - 3.0 * q) < 1e-12,
       "got %r want %r" % (float(td.sum()), 3.0 * q))
    ck("D  the roll month itself carries exactly two sides",
       abs(float(td.loc[pd.Timestamp("2011-05-31")]) - 2.0 * q) < 1e-12,
       "got %r" % float(td.loc[pd.Timestamp("2011-05-31")]))
    ck("D  IDENTITY_ROLL_TURNOVER_COUNTED — the weight-difference proxy reports "
       "ZERO for that same leg, which is the defect this replaces",
       weight_turnover == 0.0 and float(td.sum()) > 0.0,
       "weight proxy %r vs identity %r" % (weight_turnover, float(td.sum())))
    ck("D  turnover reconciles with the realised cash cost at C = $12.50/side",
       abs(float(d.cost.sum()) * 1e6 - float(td.sum()) * SIDE) < 1e-9,
       "cost %r vs turnover*C %r"
       % (float(d.cost.sum()) * 1e6, float(td.sum()) * SIDE))

    # E — roll AND resize in the same window
    e_ = leg([0.5, 0.5, 0.9] + [0.9] * 9, n_contracts=2, roll_at=may[10])
    te = e_.diagnostics.identity_turnover
    ck("E  roll + resize reconciles with its own cash cost",
       abs(float(e_.cost.sum()) * 1e6 - float(te.sum()) * SIDE) < 1e-9)
    ck("E  and it exceeds the equal-size roll's turnover (the resize is there)",
       float(te.sum()) > float(td.sum()),
       "roll+resize %r vs roll %r" % (float(te.sum()), float(td.sum())))

    ck("the ETF leg exposes no identity turnover — it has no contract "
       "identities, and its sealed turnover is already on the result",
       tc.construct_E(synth_etf_daily()).diagnostics.identity_turnover is None)
    ck("identity turnover shares the monthly index of the leg's own streams",
       bool(td.index.equals(d.cost.index)))
    flush("2e. IDENTITY TURNOVER (§7) — the unit that actually measures a roll")


def test_diagnostics_are_inert():
    """The payload cannot reach any economic or inferential output."""
    inf = _load("x01_inf_wire", os.path.join(HERE, "x01_inference.py"))
    # the futures fixture must span the SAME calendar as the ETF fixture, or the
    # paired sample is empty and there is nothing to be invariant about
    days = pd.bdate_range("2015-01-01", periods=430)
    s, o, m = multi_panel([dict(root="CL", base=100.0, step=0.25),
                           dict(root="NG", base=4.0, step=0.01)], days)
    f = run_leg(s, o, m, {"USO": ["CL"], "UNG": ["NG"]}, WSEQ)
    e = tc.construct_E(synth_etf_daily())

    cfg = inf.BootstrapConfig(
        family="stationary_bootstrap_politis_romano_1994",
        expected_block_length_months=12, replications=120, ci_level=95,
        ci_method="percentile", percentile_interpolation="linear", master_seed=7,
        arm_order=["primary", "S1", "S2"], valid_replicate_floor=110,
        min_distinct_months=24)
    # the production boundary requires the sealed calendar, so the invariance
    # check is run on a real one rather than on whatever the fixtures produced
    sealed = pd.date_range("2011-07-31", "2026-05-31", freq="ME")
    rr = np.random.default_rng(77)
    e_net = pd.Series(rr.normal(0.005, 0.03, len(sealed)), index=sealed)
    f_net = pd.Series(rr.normal(0.004, 0.03, len(sealed)), index=sealed)
    before = inf.run_primary(e_net, f_net, cfg=cfg)

    # corrupt the payload completely; the economics and the primary must not move
    f.diagnostics.monthly_returns.iloc[:, :] = 999.0
    f.diagnostics.composite_signal.iloc[:, :] = -1.0
    f.diagnostics.identity_turnover.iloc[:] = 999.0
    e.diagnostics.monthly_returns.iloc[:, :] = -999.0
    after = inf.run_primary(e_net, f_net, cfg=cfg)
    ck("DIAGNOSTICS_CAN_AFFECT_PRIMARY_VERDICT = NO — corrupting the payload "
       "leaves ΔS, the interval and the classification bit-identical",
       (before.delta_s == after.delta_s and before.ci == after.ci
        and before.classification == after.classification
        and before.counts == after.counts))
    ck("the primary entry point takes only return series, so it cannot read a "
       "payload at all",
       set(__import__("inspect").signature(inf.run_primary).parameters)
       == {"e", "f", "cfg", "boundary_b", "seed_sequence", "expected_index"})
    ck("the corruption was real (the fixture is not vacuous)",
       float(f.diagnostics.monthly_returns.to_numpy().max()) == 999.0)
    flush("2e. DIAGNOSTICS ARE INERT — no path to a primary verdict")


def test_diagnostic_wiring():
    """Interface-compatibility proof only: no orchestration, no artifact."""
    inf = _load("x01_inf_wire2", os.path.join(HERE, "x01_inference.py"))
    days = pd.bdate_range("2015-01-01", periods=430)
    s, o, m = multi_panel([dict(root="CL", base=100.0, step=0.25),
                           dict(root="NG", base=4.0, step=0.01)], days)
    f = run_leg(s, o, m, {"USO": ["CL"], "UNG": ["NG"]}, WSEQ)
    e = tc.construct_E(synth_etf_daily())

    ev0 = inf.align_pair(e.net, f.net)[0].index
    corr = inf.pair_correlations(e.diagnostics.monthly_returns,
                                 f.diagnostics.monthly_returns,
                                 evaluation_index=ev0)
    ck("PAIR_CORRELATION_WIRING — the two exposed frames feed pair_correlations "
       "directly", sorted(corr) == ["UNG", "USO"], str(sorted(corr)))
    ck("each mapped pair reports a finite correlation over shared months",
       all(np.isfinite(v["correlation"]) and v["n_months"] > 1
           for v in corr.values()), str(corr))

    sa = inf.sign_agreement_rate(e.diagnostics.composite_signal["USO"],
                                 f.diagnostics.composite_signal["USO"],
                                 evaluation_index=ev0)
    ck("SIGN_AGREEMENT_WIRING — the two exposed composites feed "
       "sign_agreement_rate directly",
       "sign_agreement_rate" in sa and sa["n_months"] > 0, str(sa)[:90])
    ck("the rate is a proportion", 0.0 <= sa["sign_agreement_rate"] <= 1.0)

    # the evaluated index is the paired one; every diagnostic is scoped to it
    ev = inf.align_pair(e.net, f.net)[0].index
    full = inf.path_diagnostics(
        e.net, f.net,
        etf_monthly=e.diagnostics.monthly_returns,
        futures_monthly=f.diagnostics.monthly_returns,
        signal_e=e.diagnostics.composite_signal["USO"],
        signal_f=f.diagnostics.composite_signal["USO"],
        turnover_e=e.turnover, turnover_f=f.diagnostics.identity_turnover,
        cost_e=e.cost, cost_f=f.cost, evaluation_index=ev)
    ck("the whole sealed §7 block assembles from construction outputs alone",
       full.pair_correlations and full.sign_agreement
       and np.isfinite(full.turnover_e) and np.isfinite(full.turnover_f)
       and np.isfinite(full.realised_cost_e) and np.isfinite(full.realised_cost_f))
    ck("F turnover is now reported, from the §3.8 IDENTITY book rather than a "
       "weight difference",
       np.isfinite(full.turnover_f) and full.turnover_f > 0)
    ck("and it is not E's number", full.turnover_f != full.turnover_e)
    ck("no evidence artifact was created by the wiring proof",
       [x for x in os.listdir(HERE) if x.endswith((".parquet", ".csv"))] == [])
    flush("2e. DIAGNOSTIC WIRING — construction output feeds inference unchanged")


# --------------------------------------------------------------------------- #
# 3. S1
# --------------------------------------------------------------------------- #
def test_S1():
    dates = pd.bdate_range("2020-01-01", periods=6)
    old, new = "1__2020-02-01", "2__2020-03-01"
    settle = pd.DataFrame({old: [95.0, 100.0, np.nan, np.nan, np.nan, np.nan],
                           new: [np.nan, 110.0, 121.0, 121.0, 121.0, 121.0]},
                          index=dates)
    front = pd.Series([old, new, new, new, new, new], index=dates)

    adj, info = tc.ratio_adjusted_prices(settle, front)
    ck("pre-roll level unchanged (history is never restated)",
       abs(adj.iloc[0] - 95.0) < 1e-12, "got %.6f" % adj.iloc[0])
    ck("roll continuity: 100/110 maps to 100, NOT 121",
       abs(adj.iloc[1] - 100.0) < 1e-12 and abs(adj.iloc[1] - 121.0) > 20,
       "got %.6f" % adj.iloc[1])
    ck("subsequent raw 121 maps to adjusted 110 (+10%)",
       abs(adj.iloc[2] - 110.0) < 1e-12, "got %.6f" % adj.iloc[2])
    ck("adjusted return equals the new contract's own return",
       abs((adj.iloc[2] / adj.iloc[1] - 1) - (121.0 / 110.0 - 1)) < 1e-15)
    ck("S1 status OK when both contracts settle at the roll", info["status"] == "OK")

    # second roll compounds multiplicatively
    d2 = pd.bdate_range("2020-01-01", periods=4)
    a, b, c = "1__x", "2__y", "3__z"
    s2 = pd.DataFrame({a: [100.0, 100.0, np.nan, np.nan],
                       b: [np.nan, 110.0, 115.5, np.nan],
                       c: [np.nan, np.nan, 60.0, 66.0]}, index=d2)
    f2 = pd.Series([a, b, c, c], index=d2)
    adj2, _ = tc.ratio_adjusted_prices(s2, f2)
    k1 = 100.0 / 110.0
    ck("successive roll factors compound (k2 = k1 * P_old2/P_new2)",
       abs(adj2.iloc[2] - (k1 * 115.5 / 60.0) * 60.0) < 1e-12)
    ck("continuity holds at the SECOND roll too",
       abs(adj2.iloc[2] - k1 * 115.5) < 1e-12)

    # missing common settlement -> declared fallback, then UNDEFINED
    # both settle on day 0; on the roll day (day 2) the OLD contract has no
    # settlement, so the sealed fallback must reach back to the latest common date
    d3 = pd.bdate_range("2020-01-01", periods=3)
    s3 = pd.DataFrame({a: [100.0, 100.0, np.nan], b: [110.0, 110.0, 121.0]}, index=d3)
    f3 = pd.Series([a, a, b], index=d3)
    _adj3, info3 = tc.ratio_adjusted_prices(s3, f3, sessions_back=0)
    ck("no common settlement within the bound -> S1_ADJUSTMENT_UNDEFINED",
       info3["status"] == tc.S1_ADJUSTMENT_UNDEFINED, info3["status"])
    adj4, info4 = tc.ratio_adjusted_prices(s3, f3, sessions_back=10)
    ck("latest-common-date fallback is searched within the sealed bound",
       info4["status"] == "OK", info4["status"])
    ck("fallback uses the latest date where BOTH settle (100/110)",
       abs(adj4.iloc[-1] - (100.0 / 110.0) * 121.0) < 1e-12)
    ck("sealed fallback bound is 10 sessions", tc.S1_FALLBACK_MAX_SESSIONS == 10)

    # UNDEFINED must TERMINATE the series, not continue on the stale factor.
    d5 = pd.bdate_range("2020-01-01", periods=8)
    s5 = pd.DataFrame({a: [100.0, 101.0, 102.0] + [np.nan] * 5,
                       b: [np.nan] * 3 + [50.0, 51.0, 52.0, 53.0, 54.0]}, index=d5)
    f5 = pd.Series([a, a, a, b, b, b, b, b], index=d5)
    adj5, info5 = tc.ratio_adjusted_prices(s5, f5, sessions_back=0)
    ck("an unpriceable roll is reported as S1_ADJUSTMENT_UNDEFINED",
       info5["status"] == tc.S1_ADJUSTMENT_UNDEFINED)
    ck("the undefined span is reported with its start date",
       info5["undefined_from"] == str(d5[3]), str(info5["undefined_from"]))
    ck("NO adjusted value is emitted on or after the undefined roll",
       len(adj5) == 3 and adj5.index.max() == d5[2], "n=%d" % len(adj5))
    ck("the history BEFORE the roll stands, unrestated (k = 1)",
       list(adj5.values) == [100.0, 101.0, 102.0], str(list(adj5.values)))
    ck("no usable-looking continuation on the stale factor (no 102 -> 50 jump)",
       float(adj5.pct_change().abs().max()) < 0.05,
       "max |step| = %.4f" % float(adj5.pct_change().abs().max()))

    # and it must not be silently substituted for inside the ag basket
    days6 = pd.bdate_range("2020-01-01", periods=12)
    k1, k2 = "XX7001__2030-01-01", "XX7002__2030-02-01"
    good = pd.DataFrame({"ZC9001__2030-01-01": np.linspace(500.0, 511.0, 12)},
                        index=days6)
    dis = pd.DataFrame({k1: [70.0] * 6 + [np.nan] * 6,
                        k2: [np.nan] * 6 + [30.0, 31.0, 32.0, 33.0, 34.0, 35.0]},
                       index=days6)
    settle6 = pd.concat([good, dis], axis=1)
    oi6 = pd.DataFrame(100.0, index=days6, columns=settle6.columns)
    oi6.loc[oi6.index >= days6[5], k2] = 900.0
    meta6 = pd.DataFrame({
        "asset": ["ZC", "ZS", "ZS"],
        "_contract_key": ["ZC9001__2030-01-01", k1, k2],
        "expiration": ["2030-01-01", "2030-01-01", "2030-02-01"]})
    meta6["expiration_dt"] = pd.to_datetime(meta6["expiration"])
    basket, _fr, notes6 = tc._exposure_signal_returns(
        settle6, oi6, meta6, ["ZC", "ZS"], arm="S1")
    ck("the undefined root is flagged in the basket's notes",
       notes6.get("ZS") == tc.S1_ADJUSTMENT_UNDEFINED, str(notes6))
    ck("the ag basket is UNDEFINED where an undefined root is undefined "
       "(never quietly averaged over the survivors)",
       bool(basket.loc[basket.index >= days6[6]].isna().all()),
       "non-NaN after the break: %d"
       % int(basket.loc[basket.index >= days6[6]].notna().sum()))
    ck("the basket is still defined BEFORE the break",
       bool(basket.loc[basket.index < days6[6]].notna().any()))

    # S1 changes the signal input ONLY
    ck("S1 arm changes signal input only; roll rule stays A1",
       tc.arm_spec("S1")["signal_input"] == "ratio_adjusted"
       and tc.arm_spec("S1")["roll_rule"] == tc.arm_spec("A1")["roll_rule"])
    ck("S1 PnL still routes through the accepted cash-first ledger",
       tc.arm_spec("S1")["pnl_route"] == "run_x02a_v3.py::tsmom_chain_net_returns")
    flush("3. S1 — causal forward ratio adjustment (synthetic rolls)")


# --------------------------------------------------------------------------- #
# 4. S2
# --------------------------------------------------------------------------- #
def test_S2():
    acc = tc.accepted()
    ck("S2 binds to the accepted carry comparator function object",
       acc["carry_robustness"].fixed_calendar_front_series.__name__
       == runner.CARRY_S2_SYMBOL)
    ck("S2 arm changes the roll rule only; signal input stays chained",
       tc.arm_spec("S2")["roll_rule"] == "fixed_calendar"
       and tc.arm_spec("S2")["signal_input"] == tc.arm_spec("A1")["signal_input"])

    settle, oi, meta = synth_futures()
    listed = tc.listed_keys_for_root(meta, "CL", settle.columns)
    expiry = {k: meta.loc[meta["_contract_key"] == k, "expiration_dt"].iloc[0] for k in listed}
    f_cal = tc.front_series(oi.reindex(columns=listed), listed,
                            rule="fixed_calendar", expiry_by_key=expiry)
    f_a1 = tc.front_series(oi.reindex(columns=listed), listed, rule="A1")
    ck("fixed-calendar front series is produced by the accepted function",
       isinstance(f_cal, pd.Series) and f_cal.notna().any())
    ck("fixed-calendar timing differs from A1 on synthetic panels",
       bool((f_cal.fillna("") != f_a1.fillna("")).any()))

    # the superseded naive comparator must be unreachable from the active seam
    try:
        tc.front_series(oi.reindex(columns=listed), listed, rule="naive_next_listed")
        reachable = True
    except ValueError:
        reachable = False
    ck("superseded naive comparator is NOT reachable from the active seam",
       not reachable)

    # wrong dependency revision / blob must be rejected by the runner's pins
    man = json.load(io.open(runner.MANIFEST, encoding="utf-8"))
    import copy
    bad = copy.deepcopy(man)
    bad["carry_s2_dependency"]["revision"] = "f" * 40
    r = runner.preflight(manifest=bad, strict_state=False)
    ck("wrong carry S2 REVISION is refused",
       any("carry S2 revision" in x for x in r.reasons))
    bad2 = copy.deepcopy(man)
    bad2["carry_s2_dependency"]["sha256"] = "0" * 64
    r2 = runner.preflight(manifest=bad2, strict_state=False)
    ck("wrong carry S2 BLOB is refused", any("carry S2 file" in x for x in r2.reasons))
    ck("carry repository is not modified by X01",
       man["carry_s2_dependency"]["note"].startswith("READ ONLY"))
    flush("4. S2 — accepted fixed-calendar comparator binding")


# --------------------------------------------------------------------------- #
# 5. pairing / sample rule
# --------------------------------------------------------------------------- #
def test_sample():
    full = pd.date_range("2010-07-31", "2026-06-30", freq="ME")
    kept = tc.paired_window(full, full)
    ck("sealed window start is 2011-07-31", str(kept[0].date()) == "2011-07-31")
    ck("sealed window end is 2026-05-31", str(kept[-1].date()) == "2026-05-31")
    ck("sealed window length is 179 paired months", len(kept) == 179, "got %d" % len(kept))
    ck("warm-up months before 2011-07 are excluded",
       not any(d < pd.Timestamp("2011-07-31") for d in kept))
    ck("June-2026 never leaks in",
       not any((d.year == 2026 and d.month == 6) for d in kept))

    # mismatched availability -> deterministic intersection, dropped from BOTH
    f_short = full.drop(pd.Timestamp("2015-03-31"))
    kept2 = tc.paired_window(full, f_short)
    ck("a month present in only one leg is dropped from both",
       len(kept2) == 178 and pd.Timestamp("2015-03-31") not in kept2)
    rep = tc.pairing_report(full, f_short)
    ck("pairing report is deterministic and flags the shortfall",
       rep["n_paired"] == 178 and rep["matches_expected"] is False
       and rep["e_only"] == 1)
    ck("pairing never back-fills or silently extends",
       tc.paired_window(full[:50], full).max() <= full[:50].max())
    ck("expected month count is the sealed 179", tc.EXPECTED_PAIRED_MONTHS == 179)
    flush("5. SAMPLE — deterministic pairing rule (no real observations)")


# --------------------------------------------------------------------------- #
# 6. safety
# --------------------------------------------------------------------------- #
def test_safety():
    src = io.open(os.path.join(HERE, "x01_target_construction.py"), encoding="utf-8").read()
    ck("STATIC boundary: no read_csv/read_parquet anywhere in the module",
       "pd.read_csv" not in src and "pd.read_parquet" not in src)
    ck("construction module contains no Sharpe / bootstrap / CI code",
       not any(tok in src.lower() for tok in
               ("def sharpe", "def bootstrap", "def confidence", "np.percentile")))
    ck("STATIC boundary: the module names no real data path",
       "close_prices_raw" not in src and "settle_v2.parquet" not in src)

    # Import purity is proved MECHANICALLY in `test_import_purity` (filesystem
    # calls instrumented, with a live control read). The two checks above are
    # static boundary checks on the text and are labelled as such; neither is
    # offered as evidence of economic correctness.

    ck("execute CLI still refuses (fail-closed)", runner.cmd_execute(None) == 2)
    man = json.load(io.open(runner.MANIFEST, encoding="utf-8"))
    ck("manifest still declares execution_authorized = false",
       man["execution_authorized"] is False)
    tcb = man.get("target_construction_binding") or {}
    ck("manifest BINDS the construction module to a real revision, not a "
       "placeholder",
       bool(tcb.get("target_construction_revision"))
       and tcb.get("target_construction_revision") != "null"
       and len(str(tcb.get("target_construction_revision"))) == 40,
       str(tcb.get("target_construction_revision")))
    ck("the frozen blob is recorded as the INDEPENDENTLY ACCEPTED bytes",
       any(m["path"].endswith("x01_target_construction.py")
           and m["sha256_at_freeze"] == m["accepted_review_pin"]
           for m in tcb.get("modules", [])))
    pend = {e["path"] for e in man.get("pending_binding", [])}
    ck("every execution-relevant module that is NOT revision-addressable is "
       "declared PENDING binding, and nothing else is",
       pend == {"research/extensions/x01/x01_inference.py",
                "research/extensions/x01/x01_inference_tests.py"},
       str(sorted(pend)))
    ck("the frozen construction module is still bound by revision, and its "
       "binding status is DERIVED from the live bytes rather than asserted",
       man["target_construction_binding"]["status"].startswith("BOUND"))
    # The unbound gate must survive binding: re-introduce one pending module
    # into a COPY of the manifest and preflight must refuse again.
    still_gated = copy.deepcopy(man)
    still_gated["pending_binding"] = [
        {"path": "research/extensions/x01/x01_target_construction.py",
         "status": "UNCOMMITTED_PENDING_BINDING"}]
    ck("the unbound-module gate still refuses if anything returns to pending",
       not runner.preflight(manifest=still_gated, strict_state=False).ok)
    # A binding that does not reproduce the accepted bytes must be refused.
    forged = copy.deepcopy(man)
    forged.setdefault("target_construction_binding", {}).setdefault(
        "modules", [{}])[0]["accepted_review_pin"] = "0" * 64
    fr = runner.preflight(manifest=forged, strict_state=False)
    ck("a freeze that does not reproduce the accepted bytes is REFUSED",
       any("INDEPENDENTLY ACCEPTED" in x for x in fr.reasons))
    nulled = copy.deepcopy(man)
    nulled.setdefault("target_construction_binding", {})["target_construction_revision"] = None
    ck("a null target_construction_revision is REFUSED",
       any("binds a target-construction revision" in x
           for x in runner.preflight(manifest=nulled, strict_state=False).reasons))

    # LIVE tracked-text pin check — defence in depth beside the dirty-tree guard
    bad = copy.deepcopy(man)
    for e in bad["inputs"]:
        if e["path"] == "config.py":
            e["sha256"] = "9" * 64
    r2 = runner.preflight(manifest=bad, strict_state=False, status=([], []))
    ck("LIVE worktree bytes are compared, not only the blob at HEAD",
       any("LIVE worktree bytes match the pin: config.py" in x for x in r2.reasons),
       "; ".join(x for x in r2.reasons if "config.py" in x)[:90])
    ck("blob-at-HEAD comparison also fires independently",
       any("blob at HEAD matches the pin: config.py" in x for x in r2.reasons))
    r3 = runner.preflight(manifest=copy.deepcopy(man), strict_state=False,
                          status=(["config.py"], []))
    ck("dirty-tree policy refuses the same path INDEPENDENTLY",
       any("no pinned path is modified" in x for x in r3.reasons))
    ck("no X01 target artifact exists on disk",
       [f for f in os.listdir(HERE) if f.endswith((".parquet", ".csv"))] == [])
    flush("6. SAFETY — boundary, fail-closed, defence in depth")


def main():
    test_E(); test_F()
    test_book_timing(); test_book_first_earning(); test_book_strike_calendar()
    test_book_gaps(); test_book_missing_root_month()
    test_root_specific_rebalance_timestamp(); test_decision_uses_the_panel_month_end()
    test_roll_between_mark_and_event()
    test_diagnostic_interface(); test_identity_turnover()
    test_finite_coverage_comparator()
    test_diagnostics_are_inert()
    test_diagnostic_wiring()
    test_pnl_route_reachability(); test_import_purity()
    test_S1(); test_S2(); test_sample(); test_safety()
    print("=" * 84)
    print("X01_CONSTRUCTION_SYNTHETIC_VALIDATION = %s   (%d failed)"
          % ("PASS" if not _fails else "FAIL", len(_fails)))
    for f in _fails:
        print("   FAILED:", f)
    print("TARGET_X01_OUTCOME_ACCESSED = NO   (synthetic fixtures only)")
    print("=" * 84)
    return 0 if not _fails else 1


if __name__ == "__main__":
    sys.exit(main())
