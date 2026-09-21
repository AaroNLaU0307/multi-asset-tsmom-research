# -*- coding: utf-8 -*-
"""Frozen-panel guard + append-only prospective snapshot store and registry.

Implements sealed §I.1 / §I.2 and LOCKBOX_PROCEDURE §3.1.

Three hard guarantees, each independently testable:
  1. NOTHING here can write to the frozen historical panel. Every write goes
     through `safe_write_bytes`, which refuses the frozen path outright — there is
     no `force` parameter and no code path that bypasses it.
  2. A snapshot file is written ONCE. Re-writing an existing snapshot id raises.
  3. The registry is append-only JSONL: rows are appended, never edited or
     reordered, and a snapshot's identity is recorded BEFORE any scientific use.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
from datetime import datetime, timezone

import pandas as pd

from . import ca_contract as K


class FrozenPanelWriteRefused(Exception):
    """Raised on any attempt to write the immutable historical panel."""


class SnapshotOverwriteRefused(Exception):
    """Raised on any attempt to overwrite an existing snapshot or registry row."""


class SnapshotNotRegistered(Exception):
    """Raised when a snapshot is used scientifically before it was registered."""


PROTECTED_PATHS = (K.FROZEN_PANEL,)


def _norm(path: str) -> str:
    p = path if os.path.isabs(path) else os.path.join(K.REPO, path)
    return os.path.normcase(os.path.normpath(os.path.abspath(p)))


def is_frozen_panel(path: str) -> bool:
    return _norm(path) in {_norm(p) for p in PROTECTED_PATHS}


def assert_not_frozen(path: str) -> None:
    if is_frozen_panel(path):
        raise FrozenPanelWriteRefused(
            "REFUSED: %s is the immutable frozen historical panel (LOCKBOX §3.1). "
            "A refresh writes a NEW snapshot with its own hash; it never overwrites "
            "the frozen panel. There is no override." % path)


def safe_write_bytes(path: str, data: bytes, *, allow_existing: bool = False) -> str:
    """The ONLY write primitive in this package. No force flag exists."""
    assert_not_frozen(path)
    full = path if os.path.isabs(path) else os.path.join(K.REPO, path)
    if os.path.exists(full) and not allow_existing:
        raise SnapshotOverwriteRefused("REFUSED: %s already exists; snapshots are write-once" % path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with io.open(full, "wb") as fh:
        fh.write(data)
    return full


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def verify_frozen_panel() -> bool:
    return K.sha256_file(K.FROZEN_PANEL) == K.FROZEN_PANEL_SHA256


def assert_frozen_panel_intact(stage: str = "") -> str:
    got = K.sha256_file(K.FROZEN_PANEL)
    if got != K.FROZEN_PANEL_SHA256:
        raise FrozenPanelWriteRefused(
            "FROZEN PANEL ALTERED%s: expected %s got %s"
            % ((" (%s)" % stage) if stage else "", K.FROZEN_PANEL_SHA256, got))
    return got


# --------------------------------------------------------------------------- #
# Append-only snapshot registry
# --------------------------------------------------------------------------- #
class SnapshotRegistry:
    """Append-only JSONL registry of snapshot identities."""

    def __init__(self, registry_path: str, store_dir: str):
        self.registry_path = registry_path
        self.store_dir = store_dir

    # -- reading ----------------------------------------------------------- #
    def rows(self) -> list:
        full = os.path.join(K.REPO, self.registry_path)
        if not os.path.exists(full):
            return []
        out = []
        with io.open(full, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    out.append(json.loads(line))
        return out

    def ids(self) -> set:
        return {r["snapshot_id"] for r in self.rows()}

    def get(self, snapshot_id: str):
        for r in self.rows():
            if r["snapshot_id"] == snapshot_id:
                return r
        return None

    # -- writing ----------------------------------------------------------- #
    def _append(self, row: dict) -> dict:
        if row["snapshot_id"] in self.ids():
            raise SnapshotOverwriteRefused(
                "REFUSED: snapshot_id %s already registered; the registry is append-only"
                % row["snapshot_id"])
        full = os.path.join(K.REPO, self.registry_path)
        assert_not_frozen(self.registry_path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with io.open(full, "a", encoding="utf-8", newline="") as fh:
            fh.write(json.dumps(row, sort_keys=True) + "\n")
        return row

    def register_snapshot(self, snapshot_id: str, panel: "pd.DataFrame", *,
                          kind: str, taken_utc: str | None = None,
                          note: str = "") -> dict:
        """Write the snapshot file ONCE and append its identity BEFORE any use."""
        assert_frozen_panel_intact("before snapshot write")
        rel = os.path.join(self.store_dir, "%s.csv" % snapshot_id).replace("\\", "/")
        csv_bytes = panel.to_csv(lineterminator="\n").encode("utf-8")
        safe_write_bytes(rel, csv_bytes)                      # refuses overwrite
        row = {
            "snapshot_id": snapshot_id,
            "kind": kind,                                      # MONTHLY | S_0 | S_G | FIXTURE
            "path": rel,
            "sha256": sha256_bytes(csv_bytes),
            "byte_size": len(csv_bytes),
            "rows": int(panel.shape[0]),
            "columns": int(panel.shape[1]),
            "first_date": str(pd.Timestamp(panel.index.min()).date()),
            "last_date": str(pd.Timestamp(panel.index.max()).date()),
            "per_ticker_rows": {c: int(panel[c].notna().sum()) for c in panel.columns},
            "registered_utc": taken_utc or datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "note": note,
        }
        self._append(row)
        assert_frozen_panel_intact("after snapshot write")
        return row

    def load(self, snapshot_id: str) -> "pd.DataFrame":
        """Load a snapshot, refusing if it was never registered or if bytes drifted."""
        row = self.get(snapshot_id)
        if row is None:
            raise SnapshotNotRegistered(
                "REFUSED: snapshot %s was never registered; identity is recorded "
                "BEFORE scientific use (§I.2)" % snapshot_id)
        full = os.path.join(K.REPO, row["path"])
        with io.open(full, "rb") as fh:
            data = fh.read()
        if sha256_bytes(data) != row["sha256"]:
            raise SnapshotOverwriteRefused(
                "REFUSED: snapshot %s bytes differ from the registered hash" % snapshot_id)
        return pd.read_csv(io.BytesIO(data), index_col=0, parse_dates=True).sort_index()
