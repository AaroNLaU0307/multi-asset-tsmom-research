# -*- coding: utf-8 -*-
"""TSMOM-VRP-01 - module B: raw settlement loader, and module C's input layer.

Parses the Cboe official per-contract files acquired by `vrp_acquire.py`, selects the
operative file per contract by a mechanical rule, and converts every price to the
common $1,000-per-point economic basis via `vrp_specs`.

WHAT IS AND IS NOT A SETTLEMENT
    A row carries an OFFICIAL SETTLEMENT iff its `Settle` field parses to a strictly
    positive number. Cboe publishes placeholder rows (all-zero) for days on which a
    contract was listed but the exchange published no settlement; those are NOT
    settlements and are flagged as absent so that the section F.4 carry-forward rule
    can act on them. The `Close` (last trade) field is NEVER used as a price: section
    A5 forbids it and `vrp_validators` asserts that the loader never reads it into a
    price path.

OPERATIVE-SOURCE RULE (mechanical; uses no return and cannot change an estimand)
    Among the candidate raw files for one contract, choose the file with the greatest
    number of rows carrying an official settlement; ties broken by the greater total
    row count, then by ARCHIVE. Where two Cboe files both cover a contract, their
    comparable settlements are cross-checked on every common date and disagreements
    are reported (there is no vendor copy anywhere in this lineage, so the section L
    fallback-authority clause is never exercised).

This module computes no return, no basis, no carry and no average.
"""
from __future__ import annotations

import csv
import datetime as _dt
import io
import os
from typing import Dict, List, NamedTuple, Optional, Sequence, Tuple

import vrp_calendar as vcal
import vrp_specs as vspecs

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
RAW_DIR = os.path.join(REPO, "data", "vix", "raw")

ROOT = "VX"


class RawRow(NamedTuple):
    trade_date: _dt.date
    label: str                 # the file's `Futures` column, e.g. "F (Jan 2024)"
    settle_quoted: float       # as published, on the contemporaneous quoted basis
    settle_present: bool
    volume: int
    open_interest: int


class Contract(NamedTuple):
    root: str
    final_settlement_date: _dt.date    # identity key, with `root`
    contract_month: str                # "YYYY-MM"
    symbol_code: str                   # e.g. "F24"
    source_file: str
    source_endpoint: str
    rows: Tuple[RawRow, ...]
    observed_last_settlement: _dt.date  # the contract's own last settled row
    expired: bool                       # False -> still listed; no final-settlement row yet


def _parse_date(text: str) -> Optional[_dt.date]:
    text = text.strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y"):
        try:
            return _dt.datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def _parse_float(text: str) -> Optional[float]:
    text = text.strip().replace(",", "")
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _parse_int(text: str) -> int:
    v = _parse_float(text)
    return 0 if v is None else int(v)


def parse_raw_file(path: str) -> List[RawRow]:
    """Parse one Cboe per-contract CSV into RawRow records. Prices are left on their
    contemporaneous QUOTED basis here; conversion happens in `normalize_contract`."""
    with io.open(path, encoding="utf-8", errors="replace", newline="") as fh:
        reader = csv.DictReader(fh)
        out: List[RawRow] = []
        for rec in reader:
            d = _parse_date(rec.get("Trade Date", "") or "")
            if d is None:
                continue
            settle = _parse_float(rec.get("Settle", "") or "")
            present = settle is not None and settle > 0.0
            out.append(RawRow(
                trade_date=d,
                label=(rec.get("Futures", "") or "").strip(),
                settle_quoted=float(settle) if settle is not None else 0.0,
                settle_present=bool(present),
                volume=_parse_int(rec.get("Total Volume", "") or ""),
                open_interest=_parse_int(rec.get("Open Interest", "") or ""),
            ))
    out.sort(key=lambda r: r.trade_date)
    return out


def _candidate_files(manifest_rows: Sequence[Dict[str, object]]) -> Dict[str, List[Dict[str, object]]]:
    by_month: Dict[str, List[Dict[str, object]]] = {}
    for row in manifest_rows:
        by_month.setdefault(str(row["contract_month"]), []).append(row)
    return by_month


def choose_operative(candidates: Sequence[Tuple[Dict[str, object], List[RawRow]]]
                     ) -> Tuple[Dict[str, object], List[RawRow]]:
    """The mechanical operative-source rule (see the module docstring)."""
    def key(item: Tuple[Dict[str, object], List[RawRow]]):
        meta, rows = item
        settled = sum(1 for r in rows if r.settle_present)
        return (settled, len(rows), 1 if meta["endpoint"] == "ARCHIVE" else 0)
    return max(candidates, key=key)


def cross_check(a_rows: Sequence[RawRow], b_rows: Sequence[RawRow],
                tol: float = 1e-9) -> Dict[str, object]:
    """Compare two Cboe files for the same contract on their common settled dates,
    on the COMMON economic basis. Returns counts and the disagreeing dates only -
    never a price level, never a return."""
    a = {r.trade_date: r for r in a_rows if r.settle_present}
    b = {r.trade_date: r for r in b_rows if r.settle_present}
    common = sorted(set(a) & set(b))
    bad: List[str] = []
    for d in common:
        pa = vspecs.price_comparable(a[d].settle_quoted, d)
        pb = vspecs.price_comparable(b[d].settle_quoted, d)
        if abs(pa - pb) > max(tol, 1e-9 * max(abs(pa), abs(pb))):
            bad.append(d.isoformat())
    return {"common_settled_dates": len(common),
            "disagreements": len(bad),
            "disagreeing_dates": bad[:20]}


def load_contracts(manifest_rows: Sequence[Dict[str, object]],
                   raw_dir: str = RAW_DIR) -> Tuple[List[Contract], List[Dict[str, object]]]:
    """Load every contract, choosing the operative file per contract.

    Returns (contracts ordered by final settlement date, cross-check reports)."""
    contracts: List[Contract] = []
    reports: List[Dict[str, object]] = []
    for month, metas in sorted(_candidate_files(manifest_rows).items()):
        loaded: List[Tuple[Dict[str, object], List[RawRow]]] = []
        for meta in metas:
            path = os.path.join(raw_dir, str(meta["file_name"]))
            if not os.path.exists(path):
                continue
            loaded.append((meta, parse_raw_file(path)))
        loaded = [(m, r) for (m, r) in loaded if r]
        if not loaded:
            continue
        if len(loaded) == 2:
            rep = cross_check(loaded[0][1], loaded[1][1])
            rep.update({"contract_month": month,
                        "file_a": loaded[0][0]["file_name"],
                        "file_b": loaded[1][0]["file_name"]})
            reports.append(rep)
        meta, rows = choose_operative(loaded)
        settled = [r for r in rows if r.settle_present]
        if not settled:
            continue
        # Identity key = (root, final_settlement_date), section J.3. The final settlement
        # date is the contract's own last settled row (section L, PRIMARY) once the
        # contract has expired. A contract still LISTED has no final-settlement row yet,
        # so for it the rule-derived date is the only available value; the observed-vs-rule
        # identity check in `vrp_validators` is applied to expired contracts, which is
        # exactly where section L's verification has something to verify.
        year, mon = (int(x) for x in month.split("-"))
        rule_expiry = vcal.monthly_final_settlement(year, mon)
        observed_last = settled[-1].trade_date
        expired = observed_last >= rule_expiry
        final = observed_last if expired else rule_expiry
        contracts.append(Contract(
            root=ROOT,
            final_settlement_date=final,
            contract_month=month,
            symbol_code=str(meta.get("symbol_code", "")),
            source_file=str(meta["file_name"]),
            source_endpoint=str(meta["endpoint"]),
            rows=tuple(rows),
            observed_last_settlement=observed_last,
            expired=expired,
        ))
    contracts.sort(key=lambda c: (c.final_settlement_date, c.contract_month))
    return contracts, reports


def normalize_contract(contract: Contract) -> Dict[_dt.date, Optional[float]]:
    """date -> comparable settlement price, or None where no official settlement exists.

    `price_comparable = settle_quoted * M_quoted / 1000` (section F.5), with M_quoted
    taken from the dated specification registry - never inferred from the prices.
    """
    out: Dict[_dt.date, Optional[float]] = {}
    for r in contract.rows:
        out[r.trade_date] = (vspecs.price_comparable(r.settle_quoted, r.trade_date)
                             if r.settle_present else None)
    return out


def label_matches_month(contract: Contract) -> bool:
    """The file's own `Futures` label must name the contract's delivery month.

    A positive identity check that the file served for a monthly final-settlement date
    really is that monthly contract (section A1, section F.1: standard monthly VX only,
    never a weekly).
    """
    year, month = (int(x) for x in contract.contract_month.split("-"))
    code = vcal.month_code(month)
    abbrev = _dt.date(year, month, 1).strftime("%b")
    for r in contract.rows:
        if not r.label:
            continue
        lab = r.label.strip()
        if not lab.startswith(code + " ("):
            return False
        if abbrev not in lab:
            return False
        if (("%d" % year) not in lab) and (("%02d" % (year % 100)) not in lab):
            return False
    return True


def exchange_calendar_from(contracts: Sequence[Contract]) -> vcal.ExchangeCalendar:
    """The empirical CFE business-day calendar: the union of official settlement dates
    across every monthly contract (section L, exchange trading calendar)."""
    days = set()
    for c in contracts:
        for r in c.rows:
            if r.settle_present:
                days.add(r.trade_date)
    return vcal.ExchangeCalendar(days)
