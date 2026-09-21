# -*- coding: utf-8 -*-
"""S_G / go-live machinery and scored-month eligibility — sealed §E.1, §F.1, §G, §H.

**S_G IS NOT CREATED BY THIS MODULE IN THE S2 BUILD.** Every function here is
either pure computation over supplied values, or is gated behind a
`GoLiveAuthorization` that this package never constructs. `S_G_CREATED` is a fact
read from the snapshot registry, and it is NO until an Owner-authorized go-live
actually registers one.

Sealed definitions implemented:
    PROSPECTIVE_START = max(SEAL_TIMESTAMP, PIPELINE_GO_LIVE)
    FORWARD_BOUNDARY  = last eligible market observation strictly before PROSPECTIVE_START
    FIRST_ELIGIBLE_SCORED_PERIOD = the first calendar month m whose decision
        month-end close (the last trading day of m-1) is strictly after PROSPECTIVE_START
"""
from __future__ import annotations

import pandas as pd

from . import ca_contract as K
from . import ca_identity


class GoLiveNotAuthorized(Exception):
    """Raised on any attempt to instantiate S_G / go-live without Owner authorization."""


class GoLiveAuthorization:
    """Owner authorization to instantiate S_G and establish PIPELINE_GO_LIVE.

    This package NEVER constructs one. Its presence is the whole gate.
    """

    def __init__(self, *, authorization_id: str, owner: str, granted_utc: str, scope: str):
        if owner != "Aaron":
            raise GoLiveNotAuthorized("only the Owner may authorize go-live")
        self.authorization_id = authorization_id
        self.owner = owner
        self.granted_utc = granted_utc
        self.scope = scope
        self.consumed = False


def s_g_created(registry) -> bool:
    return any(r.get("kind") == "S_G" for r in registry.rows())


def establish_go_live(*, registry, panel, authorization=None, go_live_utc=None,
                      snapshot_id="S_G"):
    """Acquire/accept S_G, register it, and establish PIPELINE_GO_LIVE.

    REFUSES without an Owner `GoLiveAuthorization`. Exercised synthetically in the
    S2 test suite; not invoked against real data in the S2 build.
    """
    if authorization is None or not isinstance(authorization, GoLiveAuthorization):
        raise GoLiveNotAuthorized(
            "REFUSED: creating S_G and establishing PIPELINE_GO_LIVE requires a separate "
            "Owner go-live authorization. The C-A S1 seal did not grant it and the S2 "
            "build authorization does not grant it.")
    if authorization.consumed:
        raise GoLiveNotAuthorized("REFUSED: this go-live authorization is already consumed")
    if s_g_created(registry):
        raise GoLiveNotAuthorized("REFUSED: an S_G is already registered; go-live happens once")
    row = registry.register_snapshot(snapshot_id, panel, kind="S_G",
                                     note="go-live base snapshot (sealed §E.1)")
    authorization.consumed = True
    return {"s_g_row": row,
            "pipeline_go_live_utc": go_live_utc or row["registered_utc"],
            "authorization_id": authorization.authorization_id}


# --------------------------------------------------------------------------- #
# Pure boundary computation (no authorization needed; computes, never instantiates)
# --------------------------------------------------------------------------- #
def prospective_start(seal_timestamp_utc: str, pipeline_go_live_utc) -> str | None:
    if pipeline_go_live_utc is None:
        return None                      # not yet instantiated
    a = pd.Timestamp(seal_timestamp_utc)
    b = pd.Timestamp(pipeline_go_live_utc)
    if a.tz is None:
        a = a.tz_localize("UTC")
    if b.tz is None:
        b = b.tz_localize("UTC")
    return max(a, b).isoformat()


def forward_boundary(trading_days, prospective_start_utc) -> str | None:
    """Last eligible market observation STRICTLY BEFORE PROSPECTIVE_START."""
    if prospective_start_utc is None:
        return None
    ps = pd.Timestamp(prospective_start_utc)
    ps_naive = ps.tz_convert(None) if ps.tz is not None else ps
    prior = [d for d in pd.DatetimeIndex(trading_days) if d < ps_naive]
    return str(prior[-1].date()) if prior else None


def first_eligible_scored_period(trading_days, prospective_start_utc) -> dict:
    """The first month m whose DECISION close (last trading day of m-1) is strictly
    after PROSPECTIVE_START. Sealed §E / §F.1 steps 3-4."""
    if prospective_start_utc is None:
        return {"first_eligible_scored_period": "NOT_YET_DETERMINED",
                "first_decision_month_end": None,
                "reason": "PIPELINE_GO_LIVE does not exist, so PROSPECTIVE_START is not instantiated"}
    ps = pd.Timestamp(prospective_start_utc)
    ps_naive = ps.tz_convert(None) if ps.tz is not None else ps
    idx = pd.DatetimeIndex(sorted(pd.DatetimeIndex(trading_days)))
    # last trading day of each calendar month
    month_ends = idx.to_series().groupby([idx.year, idx.month]).max()
    after = [d for d in month_ends if d > ps_naive]
    if not after:
        return {"first_eligible_scored_period": "NOT_YET_DETERMINED",
                "first_decision_month_end": None,
                "reason": "no decision month-end after PROSPECTIVE_START yet"}
    d1 = after[0]
    m1 = (pd.Timestamp(d1) + pd.offsets.MonthBegin(1))
    return {"first_eligible_scored_period": "%04d-%02d" % (m1.year, m1.month),
            "first_decision_month_end": str(pd.Timestamp(d1).date()),
            "reason": "first decision month-end strictly after PROSPECTIVE_START"}


def classify_between_seal_and_go_live(observation_date, seal_timestamp_utc,
                                      pipeline_go_live_utc) -> str:
    """Sealed §E.1 classification of observations between S_0 and S_G."""
    d = pd.Timestamp(observation_date)
    seal = pd.Timestamp(seal_timestamp_utc)
    seal = seal.tz_convert(None) if seal.tz is not None else seal
    if pipeline_go_live_utc is None:
        return "POST_SEAL_UNSCORED_STATE_INPUT_ONLY" if d >= seal.normalize() \
            else "PRE_SEAL_STATE_INPUT_ONLY"
    gl = pd.Timestamp(pipeline_go_live_utc)
    gl = gl.tz_convert(None) if gl.tz is not None else gl
    if d < seal.normalize():
        return "PRE_SEAL_STATE_INPUT_ONLY"
    if d < gl.normalize():
        return "POST_SEAL_UNSCORED_STATE_INPUT_ONLY"
    return "PROSPECTIVE_CANDIDATE"


# --------------------------------------------------------------------------- #
# §G scored-month eligibility — all five conditions, exhaustive
# --------------------------------------------------------------------------- #
def is_scored_month(*, holding_month: str, decision_month_end, prospective_start_utc,
                    locked_before_holding_prices: bool, month_end_close_for_every_live_asset: bool,
                    run_invalidating: bool, pending_classification: bool,
                    freeze_state: dict | None, all_17_live: bool,
                    partial_month: bool) -> dict:
    reasons = []
    if prospective_start_utc is None:
        reasons.append("PROSPECTIVE_START is not instantiated (no PIPELINE_GO_LIVE)")
    else:
        ps = pd.Timestamp(prospective_start_utc)
        ps_naive = ps.tz_convert(None) if ps.tz is not None else ps
        if not (pd.Timestamp(decision_month_end) > ps_naive):
            reasons.append("§G.1 decision close is not strictly after PROSPECTIVE_START")
    if not locked_before_holding_prices:
        reasons.append("§G.2 position was not locked before any price of the holding month")
    if not month_end_close_for_every_live_asset or partial_month:
        reasons.append("§G.3/§H incomplete month — no partial month is ever scored")
    if run_invalidating or pending_classification:
        reasons.append("§G.4 month is RUN_INVALIDATING_EVENT or PENDING_CLASSIFICATION")
    if freeze_state and freeze_state.get("frozen_from_month") and holding_month >= freeze_state["frozen_from_month"]:
        reasons.append("§G.5 canonical-17 record frozen at or before this month")
    if not all_17_live:
        reasons.append("§K ALL_17_REQUIRED — not every canonical object is live")
    return {"holding_month": holding_month, "scored": not reasons, "reasons": reasons}


def assert_no_retroactive_scoring(holding_month: str, prospective_start_utc) -> None:
    """No accrued pre-go-live month may EVER be retroactively scored."""
    if prospective_start_utc is None:
        raise GoLiveNotAuthorized(
            "REFUSED: %s cannot be scored — PROSPECTIVE_START is not instantiated. "
            "No accrued pre-go-live month may ever be retroactively scored." % holding_month)
