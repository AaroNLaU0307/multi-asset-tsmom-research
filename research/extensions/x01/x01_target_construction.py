"""X01 target-construction layer — CONSTRUCTION ONLY, NO INFERENCE, NO EXECUTION.

What this module is
-------------------
The construction machinery the sealed X01 contract specifies, implemented so a
*later, separately authorized* run can build:

* ``E``      — the ETF reference leg;
* ``F``/``A1`` — the primary futures leg;
* ``S1``     — the signal-input construction sensitivity;
* ``S2``     — the roll-rule sensitivity.

**Nothing here is executed on the X01 target sample by this module.** Every
function is pure with respect to the filesystem: inputs are passed in as
explicit objects. There is no module-level file read, no module-level data
load, and importing this module performs no computation. Orchestration (which
bytes to load, and the pre-outcome accounting that must precede any load) lives
in ``x01_runner.py`` and is deliberately not wired to a data path here.

What this module is NOT
-----------------------
There is **no Sharpe, no ΔS, no bootstrap, no confidence interval, no crisis
metric and no outcome verdict** in this file, by design. The construction layer
emits return series and deterministic construction metadata; inference binds in
a later stage. A construction function that quietly computed a statistic would
blur exactly the boundary the sealed contract draws.

Everything below traces to sealed sections
------------------------------------------
``§3`` sample/window · ``§3.2`` price-unit divisor · ``§3.3`` contract identity ·
``§3.4`` cash-first cost route · ``§3.5`` eligibility, warm-up, missing data ·
``§3.6`` both streams, element for element · ``§3.7`` mean-of-signs signal ·
``§3.8`` traded quantity · ``§8.1`` S1 · ``§8.2`` S2.

Accepted components are **reused, never re-implemented**: the signal comes from
``src/signals.py::signal_method_b``, sizing from ``src/sizing.py``, aggregation
from ``src/portfolio.py::equal_weight_aggregate``, the ETF cost convention from
``src/performance.py::portfolio_returns``, the futures cash ledger from
``run_x02a_v3.py::tsmom_chain_net_returns``, the A1 roll from carry's
``roll.compute_front_contract_series`` and the S2 comparator from carry's
``robustness.fixed_calendar_front_series``.
"""

import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CARRY = os.path.abspath(os.path.join(REPO, "..", "commodity-carry-research"))

# Sealed §3.6 / §15 O-1: the four mapped exposures and their futures roots.
SEALED_MAP = {
    "USO": ["CL"],
    "UNG": ["NG"],
    "GLD": ["GC"],
    "DBA": ["ZC", "ZS", "ZW", "LE", "HE", "GF"],
}
SEALED_ETFS = ["USO", "UNG", "GLD", "DBA"]

# Sealed §3.1 / §3.5: the paired window and the excluded terminal month.
FIRST_PAIRED_MONTH_END = "2011-07-31"
LAST_PAIRED_MONTH_END = "2026-05-31"
EXPECTED_PAIRED_MONTHS = 179
EXCLUDED_TERMINAL_MONTH = "2026-06"

# Sealed §8.1: the S1 fallback bound when the two contracts share no settlement.
S1_FALLBACK_MAX_SESSIONS = 10
S1_ADJUSTMENT_UNDEFINED = "S1_ADJUSTMENT_UNDEFINED"

_ACCEPTED = {}


def accepted():
    """Import the accepted components lazily.

    Lazy on purpose: importing THIS module must not touch the filesystem or run
    a computation (§4 of the build authorization). The accepted modules are code,
    not data, but loading them is still deferred so a synthetic test can import
    the construction layer without the carry repository present.
    """
    if _ACCEPTED:
        return _ACCEPTED
    if REPO not in sys.path:
        sys.path.insert(0, REPO)            # signals.py does a bare `import config`
    if CARRY not in sys.path:
        sys.path.insert(0, CARRY)

    # Both repositories have a top-level `src` package. Importing the TSMOM
    # modules as bare `src.*` would resolve to whichever path came first — the
    # exact collision that once made `from src import signals` return CARRY's
    # module. They are therefore loaded under a private package name, which also
    # satisfies their internal relative imports (`from . import sizing`).
    import types

    pkg_name = "x01_tsmom_src"
    if pkg_name not in sys.modules:
        pkg = types.ModuleType(pkg_name)
        pkg.__path__ = [os.path.join(REPO, "src")]
        sys.modules[pkg_name] = pkg
    pkg = sys.modules[pkg_name]

    def _load_sub(short):
        full = "%s.%s" % (pkg_name, short)
        if full in sys.modules:
            return sys.modules[full]
        spec = importlib.util.spec_from_file_location(
            full, os.path.join(REPO, "src", short + ".py"))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[full] = mod
        spec.loader.exec_module(mod)
        setattr(pkg, short, mod)
        return mod

    def _load(name, path):
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod
        spec.loader.exec_module(mod)
        return mod

    _ACCEPTED["signals"] = _load_sub("signals")
    _ACCEPTED["sizing"] = _load_sub("sizing")
    _ACCEPTED["portfolio"] = _load_sub("portfolio")
    _ACCEPTED["performance"] = _load_sub("performance")
    _ACCEPTED["x02a"] = _load("x01_acc_x02a", os.path.join(
        REPO, "research", "extensions", "wave1", "run_x02a_v3.py"))
    from src import roll as carry_roll                    # noqa: E402
    from src import robustness as carry_robustness        # noqa: E402
    from src import costs as carry_costs                  # noqa: E402
    from src import config as carry_cfg                   # noqa: E402
    _ACCEPTED.update(carry_roll=carry_roll, carry_robustness=carry_robustness,
                     carry_costs=carry_costs, carry_cfg=carry_cfg)
    return _ACCEPTED


class ConstructionResult(object):
    """A construction output — return series plus deterministic metadata.

    Deliberately carries **no statistic**: no Sharpe, no interval, no verdict.
    """

    __slots__ = ("arm", "net", "gross", "cost", "turnover", "positions", "meta")

    def __init__(self, arm, net, gross, cost, turnover=None, positions=None, meta=None):
        self.arm = arm
        self.net = net
        self.gross = gross
        self.cost = cost
        self.turnover = turnover
        self.positions = positions
        self.meta = dict(meta or {})

    def __repr__(self):
        n = 0 if self.net is None else len(self.net)
        return "<ConstructionResult arm=%s months=%d>" % (self.arm, n)


# --------------------------------------------------------------------------- #
# Shared frozen primitives — §3.6 "identical to E, element for element"
# --------------------------------------------------------------------------- #
def month_end_prices(daily_prices):
    """Month-end closes (§3 `SIGNAL_RESAMPLE = "ME"`), via the accepted layer."""
    return accepted()["signals"].to_monthly(daily_prices)


def composite_signal(monthly_prices):
    """Sealed §3.7 mean-of-SIGNS composite. Reuses `signal_method_b` unchanged:
    sign first, mean second, all four horizons required, `np.sign(0) == 0`."""
    return accepted()["signals"].signal_method_b(monthly_prices)


def month_end_vol(daily_prices):
    """Sealed §3.6 sizing input: 60-trading-day ann. vol sampled at month-end."""
    return accepted()["sizing"].volatility_at_month_end(daily_prices)


def decision_weights(signal_monthly, vol_monthly):
    """Sealed §3.6 sizing: `signal x (0.10 / ann_vol)`, `|w| <= 2.0`."""
    return accepted()["sizing"].target_weights(signal_monthly, vol_monthly)


def held_positions(weights_monthly):
    """Sealed §3.6 lag: the month-end decision is HELD through the next month."""
    return accepted()["sizing"].positions_from_weights(weights_monthly)


def drop_incomplete_sleeve_months(positions, required):
    """Sealed §3.5 'Incomplete sleeve': if ANY required leg is unavailable that
    month, the month is dropped from BOTH legs — **never** renormalised across
    ETFs, which would silently change the sleeve's composition.

    This deliberately overrides `equal_weight_aggregate`'s own tolerance of a
    missing column, which renormalises over whatever is available. That
    behaviour is right for the 17-asset baseline and wrong here.
    """
    missing = required if required is not None else list(positions.columns)
    complete = positions[missing].notna().all(axis=1)
    return positions.loc[complete], complete


def equal_weight_legs(positions):
    """Sealed §3.6 aggregation: equal weight across the sleeve's legs, via the
    accepted `portfolio.equal_weight_aggregate`."""
    base, avail = accepted()["portfolio"].equal_weight_aggregate(positions)
    return base, avail


# --------------------------------------------------------------------------- #
# E — the ETF reference leg (§3.6)
# --------------------------------------------------------------------------- #
def construct_E(daily_prices, tickers=None, cost_bps=None):
    """Construct the sealed ETF reference stream E from an EXPLICIT price frame.

    `daily_prices` is supplied by the caller — this function opens nothing. In a
    synthetic test it is a hand-built frame; in a later authorized run it is the
    frozen, hash-pinned ETF panel.

    Returns a ConstructionResult. **No Sharpe is computed here.**
    """
    acc = accepted()
    tickers = list(tickers or SEALED_ETFS)
    cost_bps = acc["performance"].config.TRANSACTION_COST_BPS if cost_bps is None else cost_bps

    daily = daily_prices[tickers]
    monthly = month_end_prices(daily)
    signal = composite_signal(monthly)
    vol = month_end_vol(daily)
    weights = decision_weights(signal, vol)
    positions = held_positions(weights)

    positions, complete = drop_incomplete_sleeve_months(positions, tickers)
    base, avail = equal_weight_legs(positions)

    # The baseline's own ETF convention, reused rather than re-derived:
    # gross = sum(position * asset return); turnover = sum|Δposition| one-way;
    # cost = turnover * bps/1e4; net = gross - cost.
    frame = acc["performance"].portfolio_returns(base, monthly, cost_bps=cost_bps)

    # The first month of any supplied frame has no PRIOR position, so
    # `positions.diff()` leaves turnover/cost/net undefined there. That month is
    # not evaluable and is dropped rather than silently treated as zero-cost.
    # In the sealed run this row falls far outside the 2011-07-31 window anyway
    # (the ETF panel starts 2004-2007), so it can never touch the paired sample.
    n_undefined = int(frame["net"].isna().sum())
    frame = frame.dropna(subset=["net", "cost"])

    return ConstructionResult(
        arm="E", net=frame["net"], gross=frame["gross"], cost=frame["cost"],
        turnover=frame["turnover"], positions=base,
        meta={"tickers": tickers, "cost_bps": cost_bps,
              "months_dropped_incomplete_sleeve": int((~complete).sum()),
              "months_dropped_undefined_turnover": n_undefined,
              "expense_ratio_deducted_again": False,   # §3.6: embedded once
              "cash_yield": None, "borrow": None,      # §15 O-6 SYMMETRIC_ZERO_CARRY
              "aggregation": "equal_weight_aggregate",
              "portfolio_vol_target_applied": False,   # §3.6 sleeve-standalone
              "gross_leverage_cap_applied": False})


# --------------------------------------------------------------------------- #
# Futures primitives — identity, front series, signal input (§3.2/§3.3/§8)
# --------------------------------------------------------------------------- #
def divided_settlements(settle_raw, root, divisor=None):
    """Sealed §3.2: `settle / DIVISOR[root]` BEFORE any notional or cost."""
    div = (accepted()["x02a"].DIVISOR if divisor is None else divisor)[root]
    return settle_raw / div


def listed_keys_for_root(meta, root, available_columns):
    """Sealed §3.3 persistent identity `instrument_id__expiration_date`, in
    exchange-listed expiry order. Identity comes from the accepted metadata
    frame; no symbol heuristic is used anywhere."""
    sub = meta[meta["asset"] == root].sort_values("expiration_dt")
    return [k for k in sub["_contract_key"] if k in available_columns]


def front_series(oi_panel, listed, rule="A1", expiry_by_key=None):
    """The held-front contract per date.

    `rule="A1"`             -> carry `roll.compute_front_contract_series`
                               (sealed primary; OI-max, monotonic, t-1 OI).
    `rule="fixed_calendar"` -> carry `robustness.fixed_calendar_front_series`
                               (sealed S2 comparator, §8.2), invoked directly.

    The S2 comparator is **called, not reproduced from prose** — the sealed
    contract binds S2 to that exact function, and the superseded naive
    comparator is deliberately unreachable from this seam.
    """
    acc = accepted()
    if rule == "A1":
        return acc["carry_roll"].compute_front_contract_series(oi_panel, listed)
    if rule == "fixed_calendar":
        if expiry_by_key is None:
            raise ValueError("fixed_calendar requires expiry_by_key")
        return acc["carry_robustness"].fixed_calendar_front_series(
            oi_panel, listed, expiry_by_key)
    raise ValueError("unknown roll rule %r; sealed rules are A1 and fixed_calendar" % rule)


def chained_gross_returns(settle_dollars, front, root, cost_multiplier=1.0):
    """Sealed §3.6 PRIMARY signal input: the chained held-contract return index's
    per-period GROSS return, taken from the accepted cash ledger.

    `tsmom_chain_net_returns` is the binding route (§3.4). It is called with
    `qty=1` and only its `gross`/`denominator` outputs are used, so the held-
    contract selection, NaN handling and price-unit handling are the accepted
    ones. **No alternative PnL calculator is implemented.**
    """
    acc = accepted()
    _net, gross, _cash, den = acc["x02a"].tsmom_chain_net_returns(
        settle_dollars, front, root, qty=1, cost_multiplier=cost_multiplier)
    return (gross / den).rename(root)


def ratio_adjusted_prices(settle_dollars, front, sessions_back=S1_FALLBACK_MAX_SESSIONS):
    """Sealed §8.1 S1 signal input — causal forward ratio adjustment.

        k_0        = 1
        at roll t:  k_new = k_old * P_old,t / P_new,t
        for u >= t: P_adj,u = k_new * P_new,u
        for u <  t: unchanged   (history is NEVER restated)

    Returns `(adjusted_series, info)`. `info["status"]` is
    `S1_ADJUSTMENT_UNDEFINED` when a roll has no date within `sessions_back`
    on which BOTH contracts settle — reported, never silently patched.
    """
    import pandas as pd

    dates = settle_dollars.index
    out = pd.Series(index=dates, dtype="float64")
    k, undefined_rolls, factors = 1.0, [], []
    prev_held, undefined_from = None, None
    for i, t in enumerate(dates):
        held = front.at[t] if t in front.index else None
        if held is None or (isinstance(held, float) and pd.isna(held)):
            continue
        if prev_held is not None and held != prev_held:
            # roll at t: re-express the NEW contract on the OLD contract's scale
            p_old, p_new = settle_dollars.at[t, prev_held], settle_dollars.at[t, held]
            if pd.isna(p_old) or pd.isna(p_new) or p_new == 0:
                # sealed fallback: latest date <= t where BOTH settle, <= N back
                lo = max(0, i - sessions_back)
                found = None
                for j in range(i, lo - 1, -1):
                    d = dates[j]
                    a, b = settle_dollars.at[d, prev_held], settle_dollars.at[d, held]
                    if pd.notna(a) and pd.notna(b) and b != 0:
                        found = (a, b)
                        break
                if found is None:
                    # SEALED §8.1: this root's S1 series is UNDEFINED from this
                    # roll onward. Continuing on the STALE `k` would emit a
                    # usable-looking adjusted series across a roll that was
                    # never priced — a silent patch of exactly the kind the
                    # sealed rule forbids. History before the roll stands; from
                    # the roll on there is no defined series.
                    undefined_rolls.append(str(t))
                    undefined_from = t
                    break
                p_old, p_new = found
            k = k * (p_old / p_new)
            factors.append({"date": str(t), "k": k})
        price = settle_dollars.at[t, held]
        if pd.notna(price):
            out.at[t] = k * price
        prev_held = held

    if undefined_from is not None:
        # Blank the undefined span explicitly. Dropping it instead would make it
        # indistinguishable from "this root simply had no session", and the
        # sealed rule requires the failure to be REPORTED, not disappeared.
        out.loc[out.index >= undefined_from] = float("nan")
    info = {"status": S1_ADJUSTMENT_UNDEFINED if undefined_rolls else "OK",
            "undefined_rolls": undefined_rolls, "n_rolls": len(factors),
            "final_k": k, "sessions_back": sessions_back,
            "undefined_from": None if undefined_from is None else str(undefined_from)}
    return out.dropna(), info


def s1_signal_returns(settle_dollars, front, root, sessions_back=S1_FALLBACK_MAX_SESSIONS):
    """S1's signal-input RETURN series: the ratio-adjusted price series' own
    percentage change. Signal input only — PnL never comes from here (§8.1)."""
    adj, info = ratio_adjusted_prices(settle_dollars, front, sessions_back)
    return adj.pct_change().rename(root), info


# --------------------------------------------------------------------------- #
# §3.8 — traded quantity and the cash ledger at the portfolio level
# --------------------------------------------------------------------------- #
def contract_quantities(weight, capital, multiplier, price):
    """Sealed §3.8: `q = w * K / (multiplier * P)`.

    CONTINUOUS research quantities — no rounding, no lot constraint. That is a
    stated limitation of the research object, not a tradability claim.
    """
    if price is None or multiplier in (None, 0):
        return None
    return weight * capital / (multiplier * price)


def traded_quantity(book_prev, book_now):
    """Sealed §3.8: `|q_j,t - q_j,t-1|` per CONTRACT IDENTITY.

    A roll is not special-cased: the outgoing identity goes q -> 0 and the
    incoming 0 -> q, so the expression yields two traded sides on its own —
    exactly what the sealed table requires ("a roll is not a special case, it is
    what the expression yields when the identity changes"). Charging the ledger's
    internal roll cost ON TOP would double-count it, so this is the single
    portfolio-level cost expression.
    """
    keys = set(book_prev) | set(book_now)
    return {k: abs(float(book_now.get(k, 0.0)) - float(book_prev.get(k, 0.0)))
            for k in sorted(keys)}


def cash_cost(traded, root_of_key, cost_multiplier=1.0):
    """Sealed §3.8: `Σ_j trade_qty_j * C_j`, `C = cost_per_side_usd` (§3.4).

    The accepted per-side dollar primitive is used unchanged; only the QUANTITY
    it multiplies is this layer's concern.
    """
    per_side = accepted()["carry_costs"].cost_per_side_usd
    total = 0.0
    for key, qty in traded.items():
        if qty:
            total += qty * per_side(root_of_key[key], cost_multiplier)
    return total


# --------------------------------------------------------------------------- #
# §3.5 — the deterministic pairing rule (the RULE, not the 179 observations)
# --------------------------------------------------------------------------- #
def paired_window(e_index, f_index,
                  first=FIRST_PAIRED_MONTH_END, last=LAST_PAIRED_MONTH_END):
    """Sealed §3.5: the evaluated index is the INTERSECTION of the two legs'
    eligible month-ends, bounded by the sealed window.

    * a month present in only one leg is dropped from both;
    * the terminal partial month (2026-06) is excluded by the `last` bound;
    * warm-up is enforced by the `first` bound — no bridge, no shortened
      composite, no back-fill, and the window is never silently shortened.
    """
    import pandas as pd

    lo, hi = pd.Timestamp(first), pd.Timestamp(last)
    common = e_index.intersection(f_index)
    kept = common[(common >= lo) & (common <= hi)]
    return kept.sort_values()


def pairing_report(e_index, f_index, expected=EXPECTED_PAIRED_MONTHS,
                   first=FIRST_PAIRED_MONTH_END, last=LAST_PAIRED_MONTH_END):
    """Deterministic diagnostics for the pairing seam. Emits no statistic."""
    import pandas as pd

    kept = paired_window(e_index, f_index, first, last)
    lo, hi = pd.Timestamp(first), pd.Timestamp(last)
    return {
        "n_paired": len(kept),
        "expected": expected,
        "matches_expected": len(kept) == expected,
        "first": None if not len(kept) else str(kept[0].date()),
        "last": None if not len(kept) else str(kept[-1].date()),
        "dropped_before_window": int(sum(1 for d in e_index.intersection(f_index) if d < lo)),
        "dropped_after_window": int(sum(1 for d in e_index.intersection(f_index) if d > hi)),
        "e_only": int(len(e_index.difference(f_index))),
        "f_only": int(len(f_index.difference(e_index))),
        "excluded_terminal_month": EXCLUDED_TERMINAL_MONTH,
    }


# --------------------------------------------------------------------------- #
# Arms — the three futures constructions differ in EXACTLY one element each
# --------------------------------------------------------------------------- #
ARMS = {
    "A1": {"roll_rule": "A1", "signal_input": "chained"},
    "S1": {"roll_rule": "A1", "signal_input": "ratio_adjusted"},
    "S2": {"roll_rule": "fixed_calendar", "signal_input": "chained"},
}


def arm_spec(arm):
    """The sealed one-element difference per arm, so no caller can improvise.

    S1 changes the SIGNAL INPUT only (§8.1); S2 changes the ROLL RULE only
    (§8.2). Both keep every other element identical to the primary, and both
    keep PnL on the accepted cash-first route.
    """
    if arm not in ARMS:
        raise ValueError("unknown arm %r; sealed arms are %s" % (arm, sorted(ARMS)))
    spec = dict(ARMS[arm])
    spec["pnl_route"] = "run_x02a_v3.py::tsmom_chain_net_returns"
    spec["cost_expression"] = "sum_j |q_j,t - q_j,t-1| * C_j  (sealed 3.8)"
    return spec


def _exposure_signal_returns(settle_raw, oi, meta, roots, arm, cost_multiplier=1.0):
    """The daily SIGNAL-INPUT return series for one mapped ETF exposure.

    Sealed §3.6 signal surface: **one signal per mapped ETF exposure, not per
    root**. For a 1:1 exposure this is that root's series; for the ag proxy the
    roots' series are equal-weighted into a single basket return series first,
    and the composite signal and 60-day vol are computed on THAT.

    Which per-root series feeds the basket is the one thing the arm changes:
    the primary and S2 use the chained held-contract GROSS returns, S1 uses the
    causal ratio-adjusted series' returns (§8.1). The basket composition rule is
    invariant; only its input changes — which is what "S1 changes exactly one
    thing" requires.
    """
    import pandas as pd

    spec = arm_spec(arm)
    per_root, fronts, notes = {}, {}, {}
    for root in roots:
        listed = listed_keys_for_root(meta, root, settle_raw.columns)
        if not listed:
            notes[root] = "no listed contract identity in the supplied panel"
            continue
        raw = settle_raw[listed].dropna(how="all")
        oi_r = oi.reindex(index=raw.index, columns=listed)
        expiry = {k: meta.loc[meta["_contract_key"] == k, "expiration_dt"].iloc[0]
                  for k in listed}
        front = front_series(oi_r, listed, rule=spec["roll_rule"], expiry_by_key=expiry)
        settle_d = divided_settlements(raw, root)
        if spec["signal_input"] == "chained":
            series = chained_gross_returns(settle_d, front, root, cost_multiplier)
            notes[root] = "chained gross"
        else:
            series, info = s1_signal_returns(settle_d, front, root)
            notes[root] = info["status"]
        per_root[root] = series
        fronts[root] = (front, settle_d, listed)

    if not per_root:
        return None, fronts, notes
    frame = pd.DataFrame(per_root)
    # §3.5 missing-root-month: form the leg from the remaining ELIGIBLE roots,
    # renormalised to the same total leg weight. An equal-weight mean over the
    # available columns IS that renormalisation.
    basket = frame.mean(axis=1, skipna=True)

    # An S1 ADJUSTMENT FAILURE is NOT a missing-root-month. `skipna` would
    # quietly average over the remaining roots and hand back a basket that looks
    # complete, substituting for a root whose adjustment is undefined. §8.1
    # requires the failure to surface, so the basket is undefined wherever an
    # undefined-flagged root is undefined; the status travels in `notes`.
    for root, status in notes.items():
        if status == S1_ADJUSTMENT_UNDEFINED and root in frame.columns:
            basket = basket.where(frame[root].notna())
    return basket, fronts, notes


def construct_futures_leg(settle_raw, oi, meta, arm="A1", capital=1.0,
                          mapping=None, cost_multiplier=1.0):
    """Construct the sealed futures stream for one arm from EXPLICIT panels.

    Opens nothing: `settle_raw`, `oi` and `meta` are supplied by the caller —
    synthetic frames in a test, the frozen hash-pinned panels in a later
    authorized run. Returns a ConstructionResult; **no Sharpe is computed.**
    """
    import pandas as pd

    acc = accepted()
    mapping = dict(mapping or SEALED_MAP)
    specs = acc["carry_cfg"].CONTRACT_SPECS

    # 1) one signal-input series per mapped exposure (§3.6 signal surface)
    exposure_returns, exposure_fronts, notes = {}, {}, {}
    for etf, roots in mapping.items():
        series, fronts, note = _exposure_signal_returns(
            settle_raw, oi, meta, roots, arm, cost_multiplier)
        if series is None:
            continue
        exposure_returns[etf] = series
        exposure_fronts[etf] = fronts
        notes[etf] = note
    if not exposure_returns:
        raise ValueError("no mapped exposure could be constructed from the supplied panels")

    daily_returns = pd.DataFrame(exposure_returns).sort_index()
    daily_index = (1.0 + daily_returns.fillna(0.0)).cumprod()

    # 2) sizing — identical to E, element for element (§3.6)
    #
    # FOUR STAGES, named separately because conflating them is exactly what
    # produced a one-month-stale exposure:
    #
    #   A. DECISION frame   `decision_base` — decided AT month-end label M from
    #      information up to and including M. Deliberately NOT shifted.
    #   B. EXPOSURE frame   the daily book  — the contract quantities actually
    #      on the books each session.
    #   C. STRIKE event     each root's LAST ELIGIBLE SESSION of decision month
    #      M — never the calendar label, which is frequently not a session at
    #      all (the sealed first paired month-end, 2011-07-31, is a Sunday).
    #   D. FIRST EARNING    the first session of month M+1.
    #
    # The sealed §3.6 lag is `positions = weights.shift(1)`: the decision at M
    # is held through M+1. In DAILY time the book already delivers that shift —
    # a quantity struck at the close of M's last session first earns on the
    # NEXT session, which is in M+1. Feeding the ALREADY-SHIFTED held frame
    # into the strike therefore shifts twice, and the exposure earning month M
    # would carry the M-2 decision. The strike reads the DECISION frame for
    # that reason; `held_positions` is applied once, to the REPORTED frame.
    monthly = month_end_prices(daily_index)
    signal = composite_signal(monthly)
    vol = month_end_vol(daily_index)
    weights = decision_weights(signal, vol)                     # A
    weights, complete = drop_incomplete_sleeve_months(
        weights, [c for c in weights.columns])
    decision_base, _avail = equal_weight_legs(weights)

    all_days = daily_index.index
    day_set = set(all_days)
    month_of = pd.Series(all_days, index=all_days).dt.to_period("M")
    panel_last_session = {}
    for day in all_days:
        panel_last_session[month_of.at[day]] = day
    next_session = {all_days[i]: all_days[i + 1] for i in range(len(all_days) - 1)}

    # gross-per-one-contract ledgers, one per (etf, root)
    gross_qty1 = {}
    for etf, fronts in exposure_fronts.items():
        for root, (front, settle_d, _listed) in fronts.items():
            _n, g, _c, _d = acc["x02a"].tsmom_chain_net_returns(
                settle_d, front, root, qty=1, cost_multiplier=cost_multiplier)
            gross_qty1[(etf, root)] = (g, front, settle_d)

    # --- C. each root's own PRICEABLE sessions, and the last one per month.
    #     A root is priceable on a session when the roll rule names a front
    #     contract AND that contract settles on that session. This is the
    #     mechanism behind two sealed requirements at once:
    #       * the strike lands on a real trading session, so a Saturday/Sunday/
    #         holiday month-end label never silently skips a month, and no
    #         return row is fabricated for a label that is not a session;
    #       * §3.5's "a mapped root has no eligible contract for the whole
    #         month" is decidable from the DECISION month alone, so the
    #         renormalisation below reads nothing about the month being sized.
    root_last_in_month = {}
    for key, (_g, front, settle_d) in gross_qty1.items():
        per_month = {}
        for d in front.index:
            if d not in day_set or d not in settle_d.index:
                continue
            held = front.at[d]
            if held is None or (isinstance(held, float) and pd.isna(held)):
                continue
            if held not in settle_d.columns:
                continue
            price = settle_d.at[d, held]
            if pd.isna(price) or price == 0:
                continue
            per_month[d.to_period("M")] = (d, held, price)   # last wins
        root_last_in_month[key] = per_month

    # --- the strike plan, built entirely from decision-month information.
    strikes, exits, governed, substitutions = {}, {}, {}, []
    stale_marks = []
    for label in decision_base.index:
        period = pd.Period(label, freq="M")
        if period not in panel_last_session:
            continue
        governed[period + 1] = str(label.date())   # D: which month this governs
        for etf in decision_base.columns:
            w_leg = decision_base.at[label, etf]
            roots = [r for r in mapping.get(etf, []) if (etf, r) in gross_qty1]
            if not roots or pd.isna(w_leg):
                continue
            eligible = [r for r in roots if period in root_last_in_month[(etf, r)]]
            if len(eligible) != len(roots):
                # SEALED §3.5 missing-root-month: the leg is re-formed from the
                # REMAINING eligible roots of that ETF's map, renormalised to
                # the SAME total leg weight, and the substitution is recorded
                # per month. Gross exposure is conserved; the leg weight is
                # never divided over roots that cannot be held, and it is never
                # renormalised ACROSS ETFs (that case drops the month instead).
                substitutions.append(
                    {"decision_month": str(period), "etf": etf,
                     "eligible_roots": list(eligible),
                     "ineligible_roots": [r for r in roots if r not in eligible],
                     "total_leg_weight_conserved": True,
                     # An ineligible root has, by definition, no session in the
                     # decision month on which to close. Its position is closed
                     # at the PANEL's last session of that month and the exit is
                     # charged. That is a data-boundary artefact, so it is named
                     # here rather than absorbed silently.
                     "forced_exit_no_eligible_session": True})
            if not eligible:
                continue
            share = w_leg / len(eligible)
            event_day = panel_last_session[period]
            for root in roots:
                key = (etf, root)
                if root in eligible:
                    # TWO DIFFERENT DATES, and conflating them recorded a
                    # transaction earlier than the decision that caused it.
                    #
                    #   MARK DATE  — the root's own last available settle inside
                    #                the decision month. That stale mark is the
                    #                accepted monthly convention and is what
                    #                prices the sealed quantity.
                    #   EVENT DATE — the PANEL's month-end session. The monthly
                    #                rebalance is an exposure-level event, and
                    #                the decision that determines its quantity
                    #                does not exist until the panel's month-end,
                    #                which may be after the root's last session.
                    #
                    # Dating the event at the mark date timestamped the trade
                    # BEFORE its own cause. The event therefore carries the
                    # panel month-end date. This is the model's monthly
                    # rebalance-event timestamp and is NOT a claim that the
                    # exchange traded this root on that date; the sealed
                    # quantity, the mark and the monthly gross are untouched.
                    mark_day, held, price = root_last_in_month[key][period]
                    strikes.setdefault(event_day, []).append((key, share, price))
                    if mark_day != event_day:
                        stale_marks.append(
                            {"decision_month": str(period), "etf": etf, "root": root,
                             "event_date": str(event_day), "mark_date": str(mark_day),
                             "marked_on": held,
                             "mark_convention": "LAST_AVAILABLE_SETTLE_IN_DECISION_MONTH",
                             "event_convention": "PANEL_LAST_SESSION_OF_DECISION_MONTH"})
                else:
                    # No session in the decision month on which to act: the
                    # position is closed at the last session the PANEL has, and
                    # the exit is charged rather than made to vanish.
                    exits.setdefault(panel_last_session[period], []).append(key)

    # 3) B. the daily contract-identity book (§3.8)
    root_of_key, prev_book = {}, {}
    gross_by_day, cost_by_day = {}, {}
    struck, prev_struck = {}, {}     # (etf, root) -> quantity currently in force
    last_identity = {}               # (etf, root) -> last known held identity
    gap_carried = {}                 # "etf/root" -> sessions carried over a gap
    cost_never_earned = 0.0          # a trade with no following session

    for day in all_days:
        # --- D. the day's gross belongs to the quantity carried INTO the day.
        #     `tsmom_chain_net_returns` reports at t the move of the contract
        #     held over t-1 -> t, so a same-day strike must never retroactively
        #     rescale a return that has already been earned.
        gross_today = 0.0
        for key, q_prev in prev_struck.items():
            if not q_prev:
                continue
            g, _front, _s = gross_qty1[key]
            if day in g.index and pd.notna(g.at[day]):
                gross_today += q_prev * g.at[day]

        # --- identity refresh. A ROOT-LOCAL MISSING SESSION IS NOT A TRADE:
        #     the position is still open in the same contract; the root simply
        #     has no row today. Carrying the last known identity forward leaves
        #     the book unchanged, so no phantom exit/re-entry pair is generated
        #     and no phantom cost is charged. The identity changes only when the
        #     root's own roll rule names a different contract on a session the
        #     root actually has.
        for key, (_g, front, _s) in gross_qty1.items():
            if day in front.index:
                held = front.at[day]
                if held is not None and not (isinstance(held, float) and pd.isna(held)):
                    last_identity[key] = held
            elif struck.get(key):
                tag = "%s/%s" % key
                gap_carried[tag] = gap_carried.get(tag, 0) + 1

        # --- C. strikes, then sealed exits, both at real sessions only.
        #     A strike re-sizes; it never restates the held identity. The book
        #     already carries the most recent identity the root's own roll rule
        #     named, and an eligible root always has a priceable session at or
        #     before the event day, so that identity exists. Writing the mark
        #     date's identity back at the event day could revert a roll the root
        #     made in between and manufacture a round trip.
        for key, share, price in strikes.get(day, ()):
            struck[key] = contract_quantities(
                share, capital, specs[key[1]]["multiplier"], price)
        for key in exits.get(day, ()):
            if struck.get(key):
                struck[key] = 0.0

        # --- B. today's book, keyed by CONTRACT IDENTITY (§3.8). Trade quantity
        #     falls out of `|q_j,t - q_j,t-1|` on this book, so a trade is
        #     charged on, and only on, a genuine event: a month-end re-size, a
        #     sign change, a roll (outgoing q->0, incoming 0->q) or a sealed
        #     exit. A carried gap changes no entry, so it charges nothing.
        now = {}
        for key, q in struck.items():
            if not q:
                continue
            held = last_identity.get(key)
            if held is None:
                continue
            now[held] = now.get(held, 0.0) + q
            root_of_key[held] = key[1]

        # A trade is charged to the period in which the position it creates
        # EARNS — stage D — which is the single rule that makes F's cost timing
        # identical to E's. E charges `|Δposition| × bps` at month M for the
        # trade executed at the close of M-1 (`positions.diff()` on the HELD
        # frame); charging F's month-end strike to month M-1 instead would move
        # the two legs' rebalance costs one month apart, and ΔS is a difference
        # of the two legs. The same rule handles a mid-month roll with no
        # special case: its next session is in its own month.
        traded = traded_quantity(prev_book, now)
        charge = cash_cost(traded, root_of_key, cost_multiplier)
        earns_on = next_session.get(day)
        if earns_on is None:
            cost_never_earned += charge          # no session left to earn it
        else:
            cost_by_day[earns_on] = cost_by_day.get(earns_on, 0.0) + charge
        gross_by_day[day] = gross_today
        prev_book = now
        prev_struck = dict(struck)

    gross_d = pd.Series(gross_by_day).sort_index()
    cost_d = pd.Series(cost_by_day).sort_index()
    gross_m = gross_d.groupby(month_of.reindex(gross_d.index)).sum()
    cost_m = cost_d.groupby(month_of.reindex(cost_d.index)).sum()

    # A month is evaluable only if a real month-end decision GOVERNS it. This
    # excludes the months before the first strike — sealed §3.5: "Before
    # 2011-07-31 the futures leg holds no position and produces no return row.
    # There is no zero-return padding" — and any month whose governing decision
    # month was dropped by the incomplete-sleeve rule. Those are the same months
    # E drops, reached through the same one-month lag, rather than being covered
    # by carrying a stale position into them.
    cost_m = cost_m.reindex(gross_m.index, fill_value=0.0)
    keep = [p for p in gross_m.index if p in governed]
    gross_m, cost_m = gross_m.loc[keep], cost_m.loc[keep]
    if len(gross_m):
        idx = pd.PeriodIndex(gross_m.index).to_timestamp(how="end").normalize()
    else:
        idx = pd.DatetimeIndex([])
    gross_m.index, cost_m.index = idx, idx
    net_m = (gross_m - cost_m) / capital

    return ConstructionResult(
        arm=arm, net=net_m, gross=gross_m / capital, cost=cost_m / capital,
        turnover=None, positions=held_positions(decision_base),
        meta={"arm_spec": arm_spec(arm), "mapping": mapping, "capital": capital,
              "signal_input_notes": notes,
              # `positions` is the HELD frame, label M = exposure held during
              # month M — identical in construction to E's. The book is struck
              # from the unshifted DECISION frame; the shift appears once, here.
              "positions_frame": "held_label_M_is_decision_at_M_minus_1",
              "strike_rule": "panel_last_session_of_the_decision_month",
              "mark_rule": "root_last_available_settle_in_the_decision_month",
              "first_earning_session": "the_session_after_the_strike",
              "stale_mark_rebalances": stale_marks,
              "s1_undefined_roots": sorted(
                  {r for note in notes.values() for r, s in note.items()
                   if s == S1_ADJUSTMENT_UNDEFINED}),
              "missing_root_month_substitutions": substitutions,
              "gap_sessions_carried_without_trade": gap_carried,
              "cost_charged_to": "the_period_in_which_the_new_position_earns",
              "cost_dropped_no_following_session": cost_never_earned,
              "months_governed_by_a_decision": len(governed),
              "months_dropped_incomplete_sleeve": int((~complete).sum()),
              "cash_yield": None, "margin_financing": None, "borrow": None,
              "expense_ratio": None,
              "quantity_type": "continuous_research_quantities"})
