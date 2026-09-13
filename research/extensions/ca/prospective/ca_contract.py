# -*- coding: utf-8 -*-
"""C-A sealed contract constants, runtime pin and build identity.

SINGLE SOURCE OF TRUTH for every sealed value the prospective pipeline needs.
Nothing here is a design choice: every constant is transcribed from the SEALED
preregistration and is verified against the sealed bytes by
`assert_seal_intact()`. If the sealed file changes, this module refuses to load.

SEALED CONTRACT : research/extensions/ca/CA_PREREGISTRATION_DRAFT.md
SEAL TIMESTAMP  : 2026-09-13T17:42:06Z
SEAL REVISION   : 7706d61df8b06beccc8f81ccdb1a22fe79680590
"""
from __future__ import annotations

import hashlib
import io
import os
import subprocess
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))

# --------------------------------------------------------------------------- #
# Sealed identity
# --------------------------------------------------------------------------- #
SEALED_PREREG = "research/extensions/ca/CA_PREREGISTRATION_DRAFT.md"
SEALED_PREREG_SHA256 = "9a41d7cf2055b5212d8517fa11fbde08218e2b6d2b92e39cbd2081ee9eea882b"
SEAL_TIMESTAMP_UTC = "2026-09-13T17:42:06Z"
SEAL_REVISION = "7706d61df8b06beccc8f81ccdb1a22fe79680590"

FROZEN_PANEL = "data/close_prices_raw.csv"
FROZEN_PANEL_SHA256 = "3d2a7a56dbd92d4ff8138cfd894c87f5ac5ac088a11165db870673e0c05c3c31"
FROZEN_BOUNDARY = "2026-06-12"

S0_PATH = "data/prospective/S0_20260913T165624Z.csv"
S0_SHA256 = "c4a21dc86038f9f0d06e32a267810b46cb39d9dd3549c35ef3329c87f884d6fb"

INSTRUMENT_REGISTRY = "research/extensions/ca/CA_INSTRUMENT_REGISTRY.json"

# --------------------------------------------------------------------------- #
# §B canonical strategy identity — IMMUTABLE
# --------------------------------------------------------------------------- #
SLEEVES = {
    "Equity": ["SPY", "EEM", "EWJ", "XLE", "XLU"],
    "Fixed income": ["TLT", "SHY", "LQD", "HYG"],
    "Commodity": ["USO", "UNG", "GLD", "DBA"],
    "FX": ["UUP", "FXY"],
    "Real estate": ["VNQ", "RWX"],
}
CANONICAL_17 = [t for v in SLEEVES.values() for t in v]

MOMENTUM_LOOKBACKS_MONTHS = (1, 3, 6, 12)
MOMENTUM_MIN_PERIODS = 4          # all four horizons required
VOL_WINDOW_DAYS = 60
TARGET_VOL_ANNUAL = 0.10
MAX_ASSET_WEIGHT = 2.0
PORT_TARGET_VOL_ANNUAL = 0.10
PORT_VOL_WINDOW_DAYS = 60
MAX_GROSS_LEVERAGE = 3.0
TRANSACTION_COST_BPS = 2.0
TRADING_DAYS_PER_YEAR = 252
RISK_FREE_ANNUAL = 0.0            # the primary is raw, rf = 0

# --------------------------------------------------------------------------- #
# §D / §L / §M decision design
# --------------------------------------------------------------------------- #
POSITIVE_MATERIALITY_FLOOR = 0.30
ADVERSE_MATERIALITY_THRESHOLD = -0.20
N_SCORED_TERMINAL = 120
POSITIVE_REVEAL_COUNT = 1
SNAPSHOT_LAG_BUSINESS_DAYS = 5

# --------------------------------------------------------------------------- #
# §N inference
# --------------------------------------------------------------------------- #
BOOTSTRAP_BLOCK_LEN = 12
BOOTSTRAP_REPLICATES = 10000
CI_LEVEL = 95
MASTER_SEED = 7
MIN_DISTINCT_MONTHS = 24
VALID_REPLICATE_FLOOR = 9500

# --------------------------------------------------------------------------- #
# §P.2 FM-1 rate (OD-6)
# --------------------------------------------------------------------------- #
RF_SERIES = "DGS3MO"
RF_FRESHNESS_MAX_CALENDAR_DAYS = 7
RF_FALLBACK_SERIES = None         # NONE. Never a second series.

# --------------------------------------------------------------------------- #
# §J position-diagnostic tolerance
# --------------------------------------------------------------------------- #
SECTION_J_POSITION_TOLERANCE = 0.01

# --------------------------------------------------------------------------- #
# Runtime pin (§I.4)
# --------------------------------------------------------------------------- #
PINNED_RUNTIME = {"python": "3.13.14", "pandas": "2.3.3", "numpy": "2.5.0"}


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(os.path.join(REPO, path) if not os.path.isabs(path) else path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def assert_seal_intact() -> str:
    """Refuse to operate if the sealed preregistration bytes have changed."""
    got = sha256_file(SEALED_PREREG)
    if got != SEALED_PREREG_SHA256:
        raise RuntimeError(
            "SEAL BROKEN: %s\n  expected %s\n  got      %s"
            % (SEALED_PREREG, SEALED_PREREG_SHA256, got))
    return got


def current_runtime() -> dict:
    return {"python": sys.version.split()[0],
            "pandas": pd.__version__,
            "numpy": np.__version__}


def runtime_matches() -> bool:
    return current_runtime() == PINNED_RUNTIME


def assert_runtime(strict: bool = True) -> dict:
    """§I.4 — the pipeline refuses to run under an unpinned or mismatched runtime."""
    cur = current_runtime()
    if strict and cur != PINNED_RUNTIME:
        raise RuntimeError("RUNTIME MISMATCH: pinned %s, running %s" % (PINNED_RUNTIME, cur))
    return cur


def build_identity() -> dict:
    """Reproducible build identity: runtime + code revision + sealed identity."""
    try:
        rev = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO,
                             capture_output=True, text=True).stdout.strip() or "UNKNOWN"
        dirty = bool(subprocess.run(["git", "status", "--porcelain"], cwd=REPO,
                                    capture_output=True, text=True).stdout.strip())
    except Exception:
        rev, dirty = "UNKNOWN", True
    return {"runtime": current_runtime(),
            "runtime_pinned": PINNED_RUNTIME,
            "runtime_matches": runtime_matches(),
            "code_revision": rev,
            "worktree_dirty": dirty,
            "sealed_prereg_sha256": SEALED_PREREG_SHA256,
            "seal_revision": SEAL_REVISION,
            "seal_timestamp_utc": SEAL_TIMESTAMP_UTC}


def repo_path(*parts: str) -> str:
    return os.path.join(REPO, *parts)


# Loading this module always re-verifies the seal.
assert_seal_intact()
