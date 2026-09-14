# -*- coding: utf-8 -*-
"""TSMOM-VRP-01 - S2A raw data acquisition and hash pinning.

Acquires ONLY what the sealed contract section L requires, from the section L
PRIMARY AUTHORITY (Cboe / CFE official per-contract historical data files, the
official *settlement* field). Two Cboe official endpoints cover the window:

    ARCHIVE   https://cdn.cboe.com/resources/futures/archive/volume-and-price/
              CFE_<monthcode><yy>_VX.csv
              the delisted-contract archive; complete contract life, official Settle

    CURRENT   https://cdn.cboe.com/data/us/futures/market_statistics/historical_data/
              VX/VX_<final_settlement_date>.csv
              the market-statistics archive, keyed by final settlement date

Both are Cboe official (SOURCE_AUTHORITY_LEVEL = 1 / PRIMARY). Neither is a vendor
copy, so the section L fallback-authority clause is not exercised. Where a contract
is served by both, both raw files are pinned and cross-checked; the operative source
is the one carrying a populated official settlement field over the whole contract
life (see `vrp_raw.py`).

WHAT THIS MODULE DOES NOT DO
    It computes no return, no basis, no carry, no roll yield, no average and no
    strategy quantity. It downloads bytes, writes them once, and hashes them.
    Raw bytes are IMMUTABLE: a file that already exists is never rewritten; if the
    remote bytes differ from the pinned hash the acquisition FAILS loudly.

No credential of any kind is used, sent, stored, logged or hashed: both endpoints
are public and unauthenticated.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request
from typing import Dict, List, Optional, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)

import vrp_calendar as vcal  # noqa: E402

RAW_DIR = os.path.join(REPO, "data", "vix", "raw")
DOC_DIR = os.path.join(REPO, "data", "vix", "raw", "specifications")
MANIFEST_DIR = os.path.join(REPO, "data", "vix", "manifests")
MANIFEST_JSON = os.path.join(MANIFEST_DIR, "vrp_raw_manifest.json")

ARCHIVE_URL = ("https://cdn.cboe.com/resources/futures/archive/volume-and-price/"
               "CFE_%s%02d_VX.csv")
CURRENT_URL = ("https://cdn.cboe.com/data/us/futures/market_statistics/"
               "historical_data/VX/VX_%s.csv")

USER_AGENT = "TSMOM-VRP-01 research acquisition (sealed lineage; personal research use)"

# The acquisition window: every monthly contract that can carry a settlement on or
# before the sealed Stage-A cutoff, plus the two contracts that are eligible on the
# last covered business day. Contracts that never listed simply return 404/403.
FIRST_CANDIDATE = (2004, 1)
LAST_CANDIDATE = (2026, 12)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _fetch(url: str, timeout: int = 45, attempts: int = 3) -> Tuple[Optional[bytes], int]:
    """Return (bytes, http_status). (None, status) when the resource is absent."""
    last_status = 0
    for attempt in range(attempts):
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read(), resp.status
        except urllib.error.HTTPError as exc:
            last_status = exc.code
            if exc.code in (403, 404):        # absent, not an error worth retrying
                return None, exc.code
        except (urllib.error.URLError, TimeoutError, OSError):
            last_status = -1
        time.sleep(1.5 * (attempt + 1))
    return None, last_status


def _looks_like_vx_csv(data: bytes) -> bool:
    head = data[:200].decode("utf-8", "replace")
    return head.startswith("Trade Date,Futures,")


def _store(name: str, data: bytes, url: str, directory: str = RAW_DIR) -> Dict[str, object]:
    """Write raw bytes ONCE and pin them. Never rewrites an existing raw file."""
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, name)
    digest = sha256_bytes(data)
    if os.path.exists(path):
        existing = sha256_file(path)
        if existing != digest:
            raise RuntimeError(
                "RAW IMMUTABILITY VIOLATION: %s already exists with SHA256 %s but the "
                "remote now serves %s. Raw bytes are never overwritten." % (name, existing, digest))
    else:
        with open(path, "wb") as fh:
            fh.write(data)
    return {
        "file_name": name,
        "relative_path": os.path.relpath(path, REPO).replace("\\", "/"),
        "url": url,
        "source": "Cboe (CFE) official historical per-contract data file",
        "source_authority_level": "1 / PRIMARY",
        "acquisition_timestamp_utc": _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sha256": digest,
        "bytes": len(data),
        "transformation_status": "RAW",
        "license_retention": ("Cboe personal / research use; NO REDISTRIBUTION; raw bytes retained "
                              "in the git-ignored data/vix/ tree for the life of the lineage"),
    }


def acquire_contracts(verbose: bool = True) -> Dict[str, object]:
    """Acquire every monthly VX contract file available from either Cboe endpoint."""
    candidates = vcal.monthly_contracts(FIRST_CANDIDATE, LAST_CANDIDATE)
    rows: List[Dict[str, object]] = []
    misses: List[Dict[str, object]] = []

    for (year, month, expiry) in candidates:
        code = vcal.month_code(month)
        key = "%04d-%02d" % (year, month)
        got_any = False

        archive_url = ARCHIVE_URL % (code, year % 100)
        data, status = _fetch(archive_url)
        if data is not None and _looks_like_vx_csv(data):
            row = _store("VX_archive_%s%02d.csv" % (code, year % 100), data, archive_url)
            row.update({"contract_month": key, "rule_expiry": expiry.isoformat(),
                        "endpoint": "ARCHIVE", "symbol_code": "%s%02d" % (code, year % 100)})
            rows.append(row)
            got_any = True

        current_url = CURRENT_URL % expiry.isoformat()
        data, status2 = _fetch(current_url)
        if data is not None and _looks_like_vx_csv(data):
            row = _store("VX_current_%s.csv" % expiry.isoformat(), data, current_url)
            row.update({"contract_month": key, "rule_expiry": expiry.isoformat(),
                        "endpoint": "CURRENT", "symbol_code": "%s%02d" % (code, year % 100)})
            rows.append(row)
            got_any = True

        if not got_any:
            misses.append({"contract_month": key, "rule_expiry": expiry.isoformat(),
                           "archive_status": status, "current_status": status2})
        if verbose:
            print("  %s  expiry %s  archive=%s current=%s" % (
                key, expiry.isoformat(),
                "yes" if any(r["contract_month"] == key and r["endpoint"] == "ARCHIVE" for r in rows) else "-",
                "yes" if any(r["contract_month"] == key and r["endpoint"] == "CURRENT" for r in rows) else "-"))
        time.sleep(0.12)

    return {"contract_files": rows, "unavailable": misses}


SPEC_DOCUMENTS = [
    # (file name, url, what it documents)
    ("cboe_vx_contract_specifications.html",
     "https://www.cboe.com/tradable_products/vix/vix_futures/specifications/",
     "Cboe VX standard monthly contract specifications: multiplier, tick, final settlement rule"),
    ("cboe_vxm_mini_specifications.html",
     "https://www.cboe.com/tradable_products/vix/mini_vix_futures/specifications/",
     "Cboe Mini VX (VXM) specifications: $100 multiplier, used ONLY by the granularity check"),
    ("cfe_holiday_calendar.html",
     "https://www.cboe.com/about/hours/us-futures/",
     "CFE trading hours and holiday calendar"),
    ("cfe_fee_schedule.html",
     "https://www.cboe.com/us/futures/membership/fee_schedule/",
     "CFE fee schedule (exchange + clearing), for the documented comparison of section G constants"),
    ("cboe_vx_historical_data_index.html",
     "https://www.cboe.com/us/futures/market_statistics/historical_data/",
     "Cboe historical data index page; documents the per-contract file layout used above"),
]


def acquire_specification_documents(verbose: bool = True) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    for name, url, what in SPEC_DOCUMENTS:
        data, status = _fetch(url)
        if data is None:
            rows.append({"file_name": name, "url": url, "documents": what,
                         "status": "UNAVAILABLE", "http_status": status})
            if verbose:
                print("  %-46s UNAVAILABLE (http %s)" % (name, status))
            continue
        row = _store(name, data, url, directory=DOC_DIR)
        row["documents"] = what
        row["source"] = "Cboe public product / rule documentation"
        row["status"] = "ACQUIRED"
        rows.append(row)
        if verbose:
            print("  %-46s %d bytes  %s" % (name, len(data), row["sha256"][:16]))
        time.sleep(0.2)
    return rows


def main() -> int:
    os.makedirs(MANIFEST_DIR, exist_ok=True)
    print("TSMOM-VRP-01 S2A ACQUISITION - Cboe official VX settlement files")
    print("=" * 78)
    print("\n[1] Monthly VX contract files")
    contracts = acquire_contracts()
    print("\n[2] Specification / calendar / fee documents")
    docs = acquire_specification_documents()

    manifest = {
        "lineage": "TSMOM-VRP-01",
        "generated_utc": _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "s1_seal_commit": "16d84545ba1385a482dbac7e776b31275f6fa5f7",
        "contract_files": contracts["contract_files"],
        "unavailable_contracts": contracts["unavailable"],
        "specification_documents": docs,
    }
    with open(MANIFEST_JSON, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(manifest, fh, indent=2, sort_keys=True)
    print("\nraw contract files : %d" % len(contracts["contract_files"]))
    print("unavailable months : %d" % len(contracts["unavailable"]))
    print("manifest           : %s" % os.path.relpath(MANIFEST_JSON, REPO))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
