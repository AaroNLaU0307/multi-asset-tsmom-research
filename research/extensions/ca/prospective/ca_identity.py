# -*- coding: utf-8 -*-
"""Instrument-identity event handling — sealed §K, implemented literally.

Sealed rule 1: identity is the FUND ENTITY, not the symbol. The registry is keyed
by the FIGI pair; ticker, CUSIP, ISIN, venue, sponsor and name may all change
without changing the object.

Sealed rule 3: when the economic object changes, the canonical record ENDS; it is
never patched. The ONLY successor path is the five-condition rule, and ANY
AMBIGUITY RESOLVES TO TERMINATION.

Hard property of this module: **it can never substitute a new economic object.**
There is no replacement code path at all. A MATERIAL_OBJECT_CHANGE produces a
freeze instruction, never a swap.
"""
from __future__ import annotations

import io
import json

from . import ca_contract as K

IDENTITY_PRESERVING = "IDENTITY_PRESERVING"
TEMPORARY_DATA_EVENT = "TEMPORARY_DATA_EVENT"
MATERIAL_OBJECT_CHANGE = "MATERIAL_OBJECT_CHANGE"

# Sealed §K event table.
EVENT_CLASS = {
    "A_TICKER_RENAME": IDENTITY_PRESERVING,
    "B_IDENTIFIER_CHANGE": IDENTITY_PRESERVING,
    "C_SPLIT_OR_REVERSE_SPLIT": IDENTITY_PRESERVING,
    "D_MERGER_SUCCESSOR": None,          # only under the five-condition rule
    "E_MERGER_DIFFERENT_MANDATE": MATERIAL_OBJECT_CHANGE,
    "F_CLOSURE_LIQUIDATION_DELISTING": MATERIAL_OBJECT_CHANGE,
    "G_BENCHMARK_METHODOLOGY_CHANGE": None,   # asset-class and sleeve membership test
    "H_TRADING_HALT": None,                   # <= 1 calendar month -> temporary
    "I_SHORT_MISSING_DATA": TEMPORARY_DATA_EVENT,
    "J_DATA_SOURCE_LOSS": None,               # reconciled alternative source -> temporary
}

SUCCESSOR_CONDITIONS = (
    "legal_economic_continuity_stated_ratio",
    "same_asset_class_sleeve_currency_no_leverage_same_or_replacement_index",
    "no_discretionary_selection_exactly_one_successor",
    "externally_documented_sponsor_filing",
    "successor_treatment_mechanically_defined",
)


class CanonicalRecordFrozen(Exception):
    """Raised when a caller tries to continue past a freeze boundary."""


def load_registry(path: str | None = None) -> dict:
    with io.open(K.repo_path(path or K.INSTRUMENT_REGISTRY), encoding="utf-8") as fh:
        return json.load(fh)


def registry_identity(reg: dict) -> dict:
    """The identity/version binding written into every ledger record."""
    return {
        "artifact": K.INSTRUMENT_REGISTRY,
        "sha256": K.sha256_file(K.INSTRUMENT_REGISTRY),
        "object_count": reg.get("object_count"),
        "status": reg.get("status"),
    }


def classify(event: dict) -> dict:
    """Classify one externally documented instrument event.

    `event` carries only externally documented facts — sealed §K: material change is
    judged from external fund/benchmark documentation ONLY, never from strategy
    outcomes. This function has no access to any outcome and takes none.
    """
    etype = event.get("event_type")
    if etype not in EVENT_CLASS:
        return _terminate(event, "unrecognised event type %r; ambiguity resolves to termination" % etype)

    fixed = EVENT_CLASS[etype]
    if fixed is not None:
        return _result(event, fixed, "sealed §K fixed classification for %s" % etype)

    if etype == "D_MERGER_SUCCESSOR":
        missing = [c for c in SUCCESSOR_CONDITIONS if event.get(c) is not True]
        if missing:
            return _terminate(event,
                              "successor rule requires ALL FIVE conditions; unmet or unverified: %s"
                              % ", ".join(missing))
        return _result(event, IDENTITY_PRESERVING,
                       "all five sealed successor conditions verified from external documents")

    if etype == "G_BENCHMARK_METHODOLOGY_CHANGE":
        same_class = event.get("same_asset_class")
        same_sleeve = event.get("same_sleeve")
        if same_class is None or same_sleeve is None:
            return _terminate(event, "asset-class/sleeve membership not established; ambiguity terminates")
        if same_class and same_sleeve:
            return _result(event, IDENTITY_PRESERVING,
                           "fund remains in the same asset class and sleeve; disclosed. "
                           "The only test is membership — no judgment of how different.")
        return _result(event, MATERIAL_OBJECT_CHANGE, "the fund left its asset class or sleeve")

    if etype == "H_TRADING_HALT":
        days = event.get("halt_calendar_days")
        if days is None:
            return _terminate(event, "halt duration unknown; ambiguity terminates")
        if days <= 31 and event.get("trading_resumed") is True:
            return _result(event, TEMPORARY_DATA_EVENT,
                           "resumed within one calendar month; executed position held at the "
                           "prior weight, logged as an execution deviation, not a rule change")
        return _result(event, MATERIAL_OBJECT_CHANGE, "halt exceeded one calendar month; treated as event F")

    if etype == "J_DATA_SOURCE_LOSS":
        if event.get("alternative_source_reproduces_overlap") is True:
            return _result(event, TEMPORARY_DATA_EVENT,
                           "predeclared alternative source reproduces the overlap at the return "
                           "level within tolerance; it succeeds by rule")
        return _result(event, MATERIAL_OBJECT_CHANGE,
                       "no reconciled source; DATA-INTEGRITY TERMINATION, logged distinctly "
                       "from an object termination")

    return _terminate(event, "unhandled branch; ambiguity resolves to termination")


def _result(event, classification, reason) -> dict:
    out = {
        "ticker": event.get("ticker"),
        "share_class_figi": event.get("share_class_figi"),
        "event_type": event.get("event_type"),
        "classification": classification,
        "reason": reason,
        "external_documents": event.get("external_documents", []),
        "record_continues": classification in (IDENTITY_PRESERVING, TEMPORARY_DATA_EVENT),
        "freezes_canonical_record": classification == MATERIAL_OBJECT_CHANGE,
        "replacement_instrument_permitted": False,   # NEVER. No code path exists.
        "reveal_triggered": False,                   # freeze does NOT reveal (§K)
    }
    if out["freezes_canonical_record"]:
        out["freeze_instruction"] = freeze_instruction(event)
    return out


def _terminate(event, reason) -> dict:
    out = _result(event, MATERIAL_OBJECT_CHANGE, "AMBIGUITY -> TERMINATE: " + reason)
    out["ambiguous"] = True
    return out


def freeze_instruction(event) -> dict:
    """Sealed §K freeze rule. Freeze, do NOT reveal, do NOT replace."""
    return {
        "action": "FREEZE_CANONICAL_17_RECORD",
        "exposure_exits_at": "last available month-end close; position 0 thereafter",
        "record_state": "FROZEN, NOT REVEALED — performance is not revealed merely "
                        "because the record terminated",
        "successor_record": "CANONICAL_MINUS_k generated automatically, generated-not-seen; "
                            "a DIFFERENT object that cannot upgrade the canonical-17 claim; "
                            "its adjudication is an Owner decision taken at the terminal look",
        "replacement_instrument": "NEVER, inside this lineage",
        "effective_month": event.get("effective_month"),
    }


def guard_record_open(freeze_state: dict | None, month: str) -> None:
    """§G condition 5 — refuse to score past a freeze boundary."""
    if freeze_state and freeze_state.get("frozen_from_month") and month >= freeze_state["frozen_from_month"]:
        raise CanonicalRecordFrozen(
            "REFUSED: the canonical-17 record is frozen from %s; %s cannot be scored (§K)"
            % (freeze_state["frozen_from_month"], month))
