"""X01 production execution — the real adapters, and the plan that wires them.

What this module is
-------------------
The other half of the production path. `x01_orchestrator.py` is the ORDER a real
run takes; this is what sits at each of its boundaries when the run is real:
the sealed panels, the governance ledgers, the committed authorization, the
atomic claim, and the published evidence file.

It exists so that `x01_runner.py execute` is a thin shell. After a valid
committed Aaron authorization exists, the repository can execute without another
production-code change — the missing input is an AUTHORIZATION and two run-time
arguments, never a function someone still has to write.

Why every boundary is still injectable
--------------------------------------
`build_plan` takes the three NON-GATE boundaries as optional parameters — target
data, governance storage, preflight — so a test can stand the whole path up
without a frozen panel. The authorization provider is deliberately NOT a
parameter: it is always constructed here, from the committed ledger at the
repository being executed. A caller can therefore substitute what a run READS,
and never whether it is PERMITTED.

What this module does not decide
--------------------------------
The exposure classification of the step-2 event is a ratified
`TBL-EXPOSURE-CLASSES` token, and choosing it is exposure accounting — an Owner
decision, not a builder one. It is a REQUIRED argument with no default, checked
against the closed token set. The code is complete; the token is supplied at run
time by whoever holds the authorization.

Nothing here computes a statistic, constructs a target, or decides an outcome.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

# The carry project's frozen anchor. READ-ONLY, always: `commodity-carry-research`
# is another study's record and this program never writes to it.
CARRY_REPO_NAME = "commodity-carry-research"
CARRY_CONFIG_RELPATH = "src/config.py"

ETF_PANEL_RELPATH = "data/close_prices_raw.csv"
SETTLE_RELPATH = "research/extensions/wave1/settle_v2.parquet"
OI_RELPATH = "research/extensions/wave1/oi_v2.parquet"
META_RELPATH = "research/extensions/wave1/contracts_meta.parquet"
PANEL_SANITY_RELPATH = "research/extensions/wave1/panel_sanity.json"

JOURNAL_DIRNAME = "execution-journal"

# --------------------------------------------------------------------------- #
# The authoritative VARIANT_ATTEMPT register (§0B object 2), read from
# `research/extensions/TRIAL_LEDGER.md` §6.1. Its column order is transcribed
# from the file, not remembered:
#
#   | # | attempt | sample | design parent | family | `N_trials` contribution |
#   | convention cited |
#
# §6.1's own PLANNED-NOT-CREATED table is the authority for WHICH rows a real
# X01 execution creates. Four attempts, on TWO different samples: A1, S1 and S2
# on the Databento panel at +1 each (the sealed §10.1 `+3`), and E on the ETF
# panel at +1, "§4, conservative; separate sample". Bootstrap replicates and
# crisis-window slices create no row — the sealed §10.1 table says so
# explicitly — and the planned table's own rows are not attempts until an
# execution creates them here.
TRIAL_LEDGER_RELPATH = "research/extensions/TRIAL_LEDGER.md"
REGISTER_HEADING = "### \u00a76.1"
REGISTER_COLUMNS = ("#", "attempt", "sample", "design parent", "family",
                    "`N_trials` contribution", "convention cited")
DATABENTO_SAMPLE = "dataset.databento.commodity-futures-curves"
ETF_SAMPLE = "dataset.yfinance.multi-asset-etf-panel"
X01_FAMILY = "F-X01"

_DATABENTO_CONVENTION = (
    "carry PREREGISTRATION.md \u00a710 - one trial per distinct constructed "
    "strategy-return series, diagnostics excluded; TRIAL_LEDGER \u00a73.1")
_ETF_CONVENTION = (
    "TRIAL_LEDGER \u00a76.1 planned register - \u00a74 conservative, separate "
    "sample; the ETF panel has no frozen convention (\u00a73.2)")

# The four rows a successful X01 execution registers, in order.
X01_ATTEMPTS = (
    {"attempt": "A1 (primary)", "sample": DATABENTO_SAMPLE,
     "design parent": "X01 (sealed preregistration)", "family": X01_FAMILY,
     "contribution": 1, "convention": _DATABENTO_CONVENTION},
    {"attempt": "S1 (construction sensitivity)", "sample": DATABENTO_SAMPLE,
     "design parent": "X01 A1", "family": X01_FAMILY,
     "contribution": 1, "convention": _DATABENTO_CONVENTION},
    {"attempt": "S2 (roll-rule sensitivity)", "sample": DATABENTO_SAMPLE,
     "design parent": "X01 A1", "family": X01_FAMILY,
     "contribution": 1, "convention": _DATABENTO_CONVENTION},
    {"attempt": "E (ETF reference leg)", "sample": ETF_SAMPLE,
     "design parent": "X01 (sealed preregistration)", "family": X01_FAMILY,
     "contribution": 1, "convention": _ETF_CONVENTION},
)

# Owner policy, sealed after the previous delta closure. Recorded as a constant
# so the token is Aaron's decision on the record rather than a builder default.
OWNER_FIRST_EXECUTION_EXPOSURE_CLASSIFICATION = "GENERATED_NOT_SEEN"

# L6 §10.1, fixed. Six columns, in this order, and the file must keep exactly one
# markdown table.
LEDGER_RELPATH = "ops/EXPOSURE_LEDGER.md"
LEDGER_COLUMNS = ("ts", "scope", "classification", "granularity",
                  "artifact_or_pointer", "note")
EXPOSURE_CLASSES = ("NO_OUTCOME", "GENERATED_NOT_SEEN", "REVEALED_AGGREGATE",
                    "REVEALED_TARGET_METRIC")
EXPOSURE_SCOPES = ("HISTORICAL_CUMULATIVE", "CURRENT_REVIEW_SCOPE")


class ProductionRefusal(RuntimeError):
    """A production boundary refused before doing anything."""


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


_MODS = {}


def mods(orchestrator=None):
    """The layers, loaded once.

    `orchestrator` lets a caller that has ALREADY loaded the orchestrator hand
    that same module object over instead of loading a second copy. Two copies of
    one file define two sets of exception classes, and an `except` clause in one
    then misses an exception raised by the other.
    """
    if _MODS:
        return _MODS
    _MODS["orchestrator"] = orchestrator or _load(
        "x01_prod_orch", os.path.join(HERE, "x01_orchestrator.py"))
    _MODS["authorization"] = _MODS["orchestrator"].layers()["authorization"]
    _MODS["evidence"] = _MODS["orchestrator"].layers()["evidence"]
    _MODS["runner"] = _MODS["orchestrator"].layers()["runner"]
    return _MODS


# --------------------------------------------------------------------------- #
# the sealed target-data boundary
# --------------------------------------------------------------------------- #
class VerifiedSnapshot(object):
    """The exact bytes whose digest was accepted — and the only thing parsed.

    This type exists because a verified PATH is not a verified INPUT. Hashing a
    file and then handing its name to a parser leaves a window in which the
    file can change, and the result is the failure mode provenance exists to
    prevent: an artifact stating a digest that is not the digest of the data
    its numbers came from. Nothing detects that afterwards, because both halves
    look correct on their own.

    So the file is read once, the digest is taken from those bytes, and the
    parser is given a seekable view over the SAME bytes. There is no second
    filesystem read to disagree with the first.

    The bytes are released as soon as the parser is finished with them. What
    survives is the record — path, digest, size — so provenance outlives the
    buffer without keeping tens of megabytes alive for the length of a run.
    """

    __slots__ = ("relpath", "sha256", "convention", "nbytes", "_data",
                 "released")

    def __init__(self, relpath, data, sha256, convention):
        self.relpath = relpath
        self.sha256 = sha256
        self.convention = convention
        self.nbytes = len(data)
        self._data = data
        self.released = False

    def stream(self):
        """A fresh seekable view over the verified bytes. Never the path."""
        if self.released:
            raise ProductionRefusal(
                "the verified snapshot of %s has been released; re-reading the "
                "source would supply bytes nobody verified" % self.relpath)
        return io.BytesIO(self._data)

    def digest_of_snapshot(self):
        """Recompute the digest from the snapshot itself, under its convention.

        Used by the tests to show that the recorded provenance is a property of
        the parsed bytes rather than a value carried alongside them.
        """
        if self.released:
            raise ProductionRefusal(
                "the verified snapshot of %s has been released" % self.relpath)
        data = self._data
        if self.convention == "sha256_of_git_blob_bytes_at_revision":
            data = data.replace(b"\r\n", b"\n")
        return hashlib.sha256(data).hexdigest()

    def release(self):
        """Drop the buffer, keep the record. Deterministic, not garbage-timed."""
        self._data = b""
        self.released = True

    def record(self):
        return {"path": self.relpath, "sha256": self.sha256,
                "bytes": self.nbytes, "hash_convention": self.convention}


class SealedTargetDataAdapter(object):
    """The frozen panels, loaded exactly as the accepted X02 chain loads them,
    and VERIFIED against the manifest before a single byte is parsed.

    Nothing is read at construction time. The panels are opened only when the
    orchestrator calls, which is only after every pre-execution gate has passed —
    so an unauthorized run reaches this object and never opens a file.

    Why the adapter verifies, when preflight already did
    ---------------------------------------------------
    Preflight checks every pinned input at the gate. That leaves a window: the
    gate passes, and the bytes change before construction reads them. The
    window is small and the consequence is not — an artifact that pins
    `3d2a7a56...` while its numbers came from different bytes is a false
    provenance claim, and nothing downstream can detect it.

    So each file is hashed again at the moment it is used, under the manifest's
    own declared convention, and a mismatch REFUSES before the file is parsed.
    The invariant is `data actually used == data the artifact claims`, and it
    holds by construction rather than by timing.
    """

    def __init__(self, repo=REPO, require_panel_sanity=True):
        self.repo = repo
        self.require_panel_sanity = require_panel_sanity
        self.reads = []
        # relpath -> the sha256 actually verified at read time. This is the
        # adapter's own record of what the science was computed from.
        self.verified = {}
        # relpath -> {path, sha256, bytes, hash_convention}. Survives the
        # release of the buffers, so provenance outlives the bytes.
        self.snapshots = {}

    def _path(self, rel):
        return os.path.join(self.repo, rel.replace("/", os.sep))

    def _manifest(self):
        path = os.path.join(self.repo, "research", "extensions", "x01",
                            "X01_EXECUTION_MANIFEST.json")
        if not os.path.exists(path):
            raise ProductionRefusal(
                "the execution manifest is absent, so no input provenance can "
                "be verified")
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)

    def _pin_for(self, rel, manifest):
        for entry in manifest.get("inputs") or []:
            if entry.get("path") == rel:
                return entry
        raise ProductionRefusal(
            "%s is not pinned in the execution manifest; an unpinned "
            "scientific input has no provenance to claim" % rel)

    def verify(self, rel, manifest=None):
        """Read the source ONCE, verify those bytes, and return them as a snapshot.

        Returns a `VerifiedSnapshot`, never a path. A path would have to be
        reopened to be parsed, and the reopened bytes are not the bytes this
        function checked.
        """
        M = mods()
        rn = M["runner"]
        manifest = manifest if manifest is not None else self._manifest()
        entry = self._pin_for(rel, manifest)
        abspath = self._path(rel)
        if not os.path.exists(abspath):
            raise ProductionRefusal("the sealed input %s is absent" % rel)
        convention = entry.get("hash_convention")
        if convention not in (rn.RAW, rn.BLOB):
            raise ProductionRefusal(
                "%s declares an unrecognised hash convention %r, so its "
                "provenance cannot be checked" % (rel, convention))
        expected = entry.get("sha256")
        if not expected:
            raise ProductionRefusal(
                "%s carries no pinned sha256 in the manifest" % rel)

        # THE single read. Everything below — the digest and the parse — comes
        # from this one byte sequence.
        with open(abspath, "rb") as fh:
            data = fh.read()
        digested = data.replace(b"\r\n", b"\n") if convention == rn.BLOB else data
        actual = hashlib.sha256(digested).hexdigest()
        if actual != expected:
            raise ProductionRefusal(
                "PROVENANCE MISMATCH on %s: the manifest pins %s but the bytes "
                "read hash to %s. Construction is refused rather than produce a "
                "result whose stated inputs are not the inputs used"
                % (rel, expected, actual))
        snapshot = VerifiedSnapshot(rel, data, actual, convention)
        self.verified[rel] = actual
        self.snapshots[rel] = snapshot.record()
        return snapshot

    def verified_provenance(self):
        """What this adapter actually verified, for the record."""
        return dict(self.verified)

    def snapshot_records(self):
        """Path, digest, size and convention for every snapshot parsed."""
        return {k: dict(v) for k, v in self.snapshots.items()}

    def _require_panel_sanity(self):
        """The same gate `run_x02a_v3.py` refuses on. Not re-implemented: read."""
        if not self.require_panel_sanity:
            return
        path = self._path(PANEL_SANITY_RELPATH)
        if not os.path.exists(path):
            raise ProductionRefusal(
                "the futures panel-sanity gate %s is absent; the accepted X02 "
                "chain refuses to run without it and so does this"
                % PANEL_SANITY_RELPATH)
        with open(path, encoding="utf-8") as fh:
            gate = json.load(fh)
        if gate.get("PANEL_SANITY") != "PASS":
            raise ProductionRefusal(
                "the futures panel-sanity gate is %r, not PASS"
                % gate.get("PANEL_SANITY"))

    def etf_panel(self):
        import pandas as pd

        # The parser is handed the verified SNAPSHOT, not the path. A mismatch
        # stops the run before any parsing happens at all.
        snapshot = self.verify(ETF_PANEL_RELPATH)
        self.reads.append(ETF_PANEL_RELPATH)
        try:
            return pd.read_csv(snapshot.stream(),
                               parse_dates=["Date"]).set_index("Date")
        finally:
            snapshot.release()

    def futures_panels(self):
        import pandas as pd

        self._require_panel_sanity()
        manifest = self._manifest()
        snapshots = {rel: self.verify(rel, manifest)
                     for rel in (SETTLE_RELPATH, OI_RELPATH, META_RELPATH)}
        self.reads.extend([SETTLE_RELPATH, OI_RELPATH, META_RELPATH])
        try:
            settle = pd.read_parquet(snapshots[SETTLE_RELPATH].stream())
            oi = pd.read_parquet(snapshots[OI_RELPATH].stream())
            meta = pd.read_parquet(snapshots[META_RELPATH].stream())
        finally:
            for snapshot in snapshots.values():
                snapshot.release()
        meta["expiration_dt"] = pd.to_datetime(meta["expiration"])
        return settle, oi, meta


# --------------------------------------------------------------------------- #
# the governance boundary
# --------------------------------------------------------------------------- #
def _atomic_write_text(path, text):
    """Write the whole file through a temp + fsync + rename. Never in place.

    A governance ledger half-written is worse than one not written: the machine
    reads it and believes it.
    """
    tmp = "%s.tmp-%d" % (path, os.getpid())
    try:
        with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            try:
                os.remove(tmp)
            except OSError:
                pass


def ledger_row(fields):
    """One §10.1 row. Refuses a field that would break the parser."""
    if sorted(fields) != sorted(LEDGER_COLUMNS):
        raise ProductionRefusal(
            "an exposure row must carry exactly %r" % (LEDGER_COLUMNS,))
    for col in LEDGER_COLUMNS:
        value = fields[col]
        if not isinstance(value, str) or not value.strip():
            raise ProductionRefusal("exposure row field %r is empty" % col)
        if "|" in value:
            raise ProductionRefusal(
                "exposure row field %r contains a literal '|', which the §10.1 "
                "table parser reads as a column break" % col)
        if "\n" in value:
            raise ProductionRefusal("exposure row field %r contains a newline"
                                    % col)
    if fields["classification"] not in EXPOSURE_CLASSES:
        raise ProductionRefusal(
            "classification %r is not a ratified TBL-EXPOSURE-CLASSES token %r"
            % (fields["classification"], EXPOSURE_CLASSES))
    if fields["scope"] not in EXPOSURE_SCOPES:
        raise ProductionRefusal("scope %r is not a ratified token"
                                % fields["scope"])
    return "| " + " | ".join(fields[c] for c in LEDGER_COLUMNS) + " |"


def count_tables(text):
    """How many markdown tables the file contains. §10.1 requires exactly one."""
    tables, in_table = 0, False
    for line in text.splitlines():
        s = line.strip()
        row = s.startswith("|") and s.endswith("|")
        if row and not in_table:
            tables += 1
            in_table = True
        elif not row:
            in_table = False
    return tables


def append_exposure_row(repo, fields, verify=None):
    """Append one row to the research exposure ledger, atomically and verifiably.

    The file is re-read and re-parsed after the write, and the original bytes
    are restored if the result would not parse. The ledger's shape is
    load-bearing — the runtime reads the first markdown table and every later
    `|…|` line as a row — so an append that broke it would silently corrupt
    every future exposure reading.
    """
    path = os.path.join(repo, LEDGER_RELPATH.replace("/", os.sep))
    if not os.path.exists(path):
        raise ProductionRefusal("the exposure ledger %s is absent"
                                % LEDGER_RELPATH)
    with open(path, encoding="utf-8") as fh:
        original = fh.read()
    before = count_tables(original)
    if before != 1:
        raise ProductionRefusal(
            "the exposure ledger contains %d markdown tables; §10.1 requires "
            "exactly one and this append would compound the problem" % before)

    row = ledger_row(fields)
    body = original if original.endswith("\n") else original + "\n"
    updated = body + row + "\n"
    _atomic_write_text(path, updated)

    with open(path, encoding="utf-8") as fh:
        written = fh.read()
    problems = []
    if count_tables(written) != 1:
        problems.append("the append produced %d markdown tables"
                        % count_tables(written))
    if row not in written.splitlines():
        problems.append("the appended row is not present in the written file")
    if verify is not None:
        ok, detail = verify(written)
        if not ok:
            problems.append(str(detail))
    if problems:
        _atomic_write_text(path, original)
        raise ProductionRefusal(
            "the exposure-ledger append was rolled back: %s" % "; ".join(problems))
    return row


def read_carry_anchor(repo, carry_repo=None):
    """The frozen `N_TRIALS` from the carry preregistration's config. READ-ONLY.

    Parsed rather than imported: importing another project's config would run
    its module-level code, and this is a governance read, not a dependency.
    `carry_repo` is a parameter so the parser can be exercised against a stub
    without reading — let alone writing — the real carry project.
    """
    path = os.path.join(carry_repo or os.path.join(os.path.dirname(repo),
                                                   CARRY_REPO_NAME),
                        CARRY_CONFIG_RELPATH.replace("/", os.sep))
    if not os.path.exists(path):
        raise ProductionRefusal(
            "the authoritative carry anchor %s/%s is not readable, so the "
            "cumulative Databento total cannot be read at execution"
            % (CARRY_REPO_NAME, CARRY_CONFIG_RELPATH))
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.strip().startswith("N_TRIALS"):
                _, _, rhs = line.partition("=")
                rhs = rhs.split("#")[0].strip()
                if rhs.isdigit():
                    return int(rhs), "%s/%s" % (CARRY_REPO_NAME,
                                                CARRY_CONFIG_RELPATH)
    raise ProductionRefusal(
        "no `N_TRIALS = <int>` declaration was found in %s/%s"
        % (CARRY_REPO_NAME, CARRY_CONFIG_RELPATH))


def _cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def _bare(cell):
    """A register cell without its markdown emphasis, for comparison."""
    return cell.replace("`", "").replace("*", "").strip()


def register_view(repo, trial_ledger_relpath=TRIAL_LEDGER_RELPATH):
    """(lines, table_start, table_end, header_cells, rows) for the §6.1 register.

    ONLY the first table under the §6.1 heading is the register. The section
    also carries a PLANNED-NOT-CREATED table whose rows have `+1` contributions
    for attempts that deliberately do not exist yet; reading those as real would
    inflate the cumulative total with work nobody has done.
    """
    path = os.path.join(repo, trial_ledger_relpath.replace("/", os.sep))
    if not os.path.exists(path):
        raise ProductionRefusal("the TSMOM trial ledger %s is absent"
                                % trial_ledger_relpath)
    with open(path, encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.strip().startswith(REGISTER_HEADING):
            start = i
            break
    if start is None:
        raise ProductionRefusal(
            "the \u00a76.1 VARIANT_ATTEMPT register could not be located in %s"
            % trial_ledger_relpath)

    header, tstart, tend, rows = None, None, None, []
    for i in range(start + 1, len(lines)):
        s = lines[i].strip()
        if s.startswith("### ") or s.startswith("## "):
            break
        is_row = s.startswith("|") and s.endswith("|")
        if not is_row:
            if tstart is not None:
                break                                 # the register table ended
            continue
        if tstart is None:
            tstart = i
            header = _cells(lines[i])
        tend = i
        cells = _cells(lines[i])
        if i == tstart or set("".join(cells)) <= set("-: "):
            continue
        if cells and cells[0] in ("\u2014", "-", ""):
            continue                                  # the explicit placeholder
        rows.append(cells)
    if tstart is None:
        raise ProductionRefusal(
            "no VARIANT_ATTEMPT register table was found under \u00a76.1 in %s"
            % trial_ledger_relpath)
    if [_bare(c) for c in header] != [_bare(c) for c in REGISTER_COLUMNS]:
        raise ProductionRefusal(
            "the \u00a76.1 register header is %r, not the expected %r; the "
            "append schema is read from the file and this file no longer "
            "matches it" % (header, list(REGISTER_COLUMNS)))
    return lines, tstart, tend, header, rows


def read_tsmom_contribution(repo, trial_ledger_relpath=TRIAL_LEDGER_RELPATH,
                            sample=None):
    """This program's contribution to date on ONE sample, from the §6.1 register.

    Sample-filtered, because the register legitimately holds attempts on more
    than one sample: A1/S1/S2 on the Databento panel and E on the ETF panel.
    Summing across them would add an ETF attempt to the Databento total, which
    is a different sample's accounting.
    """
    sample = sample or DATABENTO_SAMPLE
    _lines, _s, _e, _h, rows = register_view(repo, trial_ledger_relpath)
    total, counted = 0, 0
    for cells in rows:
        if len(cells) != len(REGISTER_COLUMNS):
            raise ProductionRefusal(
                "a \u00a76.1 register row has %d cells, not the schema's %d: %r"
                % (len(cells), len(REGISTER_COLUMNS), cells))
        if _bare(cells[2]) != sample:
            continue
        counted += 1
        contribution = _bare(cells[5])
        if not contribution.startswith("+") or not contribution[1:].isdigit():
            raise ProductionRefusal(
                "a \u00a76.1 attempt row carries no readable `N_trials` "
                "contribution, so the cumulative total cannot be read: %r"
                % (cells,))
        total += int(contribution[1:])
    return total, counted, trial_ledger_relpath


def register_row(number, attempt, run_id):
    """One register row, in the file's own column order."""
    cells = [str(number), attempt["attempt"], "`%s`" % attempt["sample"],
             attempt["design parent"], "`%s`" % attempt["family"],
             "+%d" % attempt["contribution"],
             "%s; registered by run %s" % (attempt["convention"], run_id)]
    for c in cells:
        if "|" in c or "\n" in c:
            raise ProductionRefusal(
                "a register cell contains a table-breaking character: %r" % c)
    return "| " + " | ".join(cells) + " |"


def register_mentions_run(repo, run_id, trial_ledger_relpath=TRIAL_LEDGER_RELPATH):
    _l, _s, _e, _h, rows = register_view(repo, trial_ledger_relpath)
    marker = "registered by run %s" % run_id
    return any(marker in " ".join(cells) for cells in rows)


def append_trial_attempts(repo, run_id, attempts=X01_ATTEMPTS,
                          trial_ledger_relpath=TRIAL_LEDGER_RELPATH):
    """Append the evaluated attempts to the AUTHORITATIVE register, durably.

    This is the half of step 2 that makes the accounting real. Writing only the
    exposure row and the journal would leave the run reporting an advanced
    cumulative total while the source of truth still read the old one, so the
    next process would read the old one back — the defect this repairs.

    Written whole through a temp + fsync + rename, re-parsed afterwards, and
    rolled back to the original bytes if the result would not parse or the rows
    are not all present.
    """
    if register_mentions_run(repo, run_id, trial_ledger_relpath):
        raise ProductionRefusal(
            "the \u00a76.1 register already carries attempts registered by run "
            "%r; a run registers its attempts exactly once" % run_id)
    lines, tstart, tend, _header, rows = register_view(repo, trial_ledger_relpath)
    path = os.path.join(repo, trial_ledger_relpath.replace("/", os.sep))
    with open(path, encoding="utf-8") as fh:
        original = fh.read()

    next_n = len(rows) + 1
    new_rows = [register_row(next_n + i, a, run_id)
                for i, a in enumerate(attempts)]
    updated = lines[:tend + 1] + new_rows + lines[tend + 1:]
    _atomic_write_text(path, "\n".join(updated) +
                       ("\n" if original.endswith("\n") else ""))

    problems = []
    try:
        _l2, _s2, _e2, _h2, rows2 = register_view(repo, trial_ledger_relpath)
    except ProductionRefusal as exc:
        problems.append("the register no longer parses: %s" % exc)
        rows2 = []
    if not problems:
        if len(rows2) != len(rows) + len(attempts):
            problems.append("expected %d register rows, found %d"
                            % (len(rows) + len(attempts), len(rows2)))
        for row in new_rows:
            if row not in "\n".join(_l2).splitlines():
                problems.append("an appended row is missing from the file")
                break
    if problems:
        _atomic_write_text(path, original)
        raise ProductionRefusal(
            "the \u00a76.1 register append was rolled back: %s"
            % "; ".join(problems))
    return {"register": trial_ledger_relpath, "rows_appended": len(new_rows),
            "first_row_number": next_n,
            "attempts": [a["attempt"] for a in attempts]}


def production_preflight(repo=REPO):
    """The pre-execution gate for a REAL run. The seal check is not optional.

    Why this exists as its own function
    -----------------------------------
    `x01_runner.preflight` already asks the canonical runtime for the seal, but
    it took a `strict_state` parameter, and `execute` was wired to a CLI flag
    that set it False. A production run could therefore skip the canonical seal
    query and still reach the authorization claim, step 2 and the target
    adapter. That is a research-control gate with an off switch, and an off
    switch on a research-control gate is the same as not having the gate.

    So the seal is asked HERE, unconditionally, before anything else, and then
    `preflight` is run in its strict form, which asks again. Two independent
    asks of the same canonical source cost one extra subprocess on a run that
    happens once; the alternative is a single ask reachable through a flag.

    There is no parameter on this function that can weaken it.
    """
    M = mods()
    rn = M["runner"]
    r = rn.Refusal()
    state, detail = rn.seal_state_from_runtime()
    r.check("canonical pre-execution seal derives VERIFIED",
            state == "VERIFIED",
            detail if state != "VERIFIED" else "")
    if not r.ok:
        # Stop here. Running the remaining pin checks would take a broken seal
        # further into the gate sequence than it should ever travel.
        return r
    inner = rn.preflight(strict_state=True)
    for name, ok, det in inner.checks:
        r.check(name, ok, det)
    return r


class ProductionGovernanceRecorder(object):
    """Step 2, step 3 and step 4 against the real governance records.

    Every write is durable before it returns and every one is verified after it
    lands, because step 2 is the prospective commitment the whole study's
    honesty rests on: it is worth something only if it is on disk before any
    outcome exists.
    """

    def __init__(self, repo=REPO, run_id="unset", clock=None,
                 exposure_classification=None, exposure_scope="CURRENT_REVIEW_SCOPE",
                 journal_dir=None, ledger_verifier=None, carry_repo=None):
        if exposure_classification is None:
            # Aaron has since fixed this: the first X01 execution is
            # GENERATED_NOT_SEEN — the artifact is generated and sealed without
            # the operator viewing target metrics, and a later reveal is a
            # separate authorization carrying REVEALED_TARGET_METRIC. The
            # constant records whose decision it is; the recorder still invents
            # nothing and still refuses any token outside the ratified set.
            exposure_classification = OWNER_FIRST_EXECUTION_EXPOSURE_CLASSIFICATION
        if exposure_classification not in EXPOSURE_CLASSES:
            raise ProductionRefusal(
                "exposure classification %r is not one of %r"
                % (exposure_classification, EXPOSURE_CLASSES))
        self.repo = repo
        self.run_id = run_id
        self.clock = clock or _utc_now
        self.exposure_classification = exposure_classification
        self.exposure_scope = exposure_scope
        self.journal_dir = journal_dir or os.path.join(repo, "ops",
                                                       JOURNAL_DIRNAME)
        self.ledger_verifier = ledger_verifier
        self.carry_repo = carry_repo
        self.written = []

    # -- durable machine journal ------------------------------------------- #
    def _journal(self, suffix, payload):
        if not os.path.isdir(self.journal_dir):
            os.makedirs(self.journal_dir, exist_ok=True)
        safe = "".join(c if c.isalnum() or c in "._-" else "_"
                       for c in self.run_id)[:64]
        path = os.path.join(self.journal_dir, "%s.%s.json" % (safe, suffix))
        if os.path.exists(path):
            raise ProductionRefusal(
                "a %s journal already exists for run %r; a run id is used once"
                % (suffix, self.run_id))
        _atomic_write_text(path, json.dumps(payload, indent=2, sort_keys=True,
                                            ensure_ascii=False) + "\n")
        self.written.append(path)
        return os.path.relpath(path, self.repo).replace(os.sep, "/")

    # -- step 2 ------------------------------------------------------------- #
    def _precheck(self):
        """Everything that can fail BEFORE anything durable is written.

        Raising `Step2NotDurable` here is what lets the authorization survive a
        step-2 attempt that never started: §7's before-step-2 rule applies only
        when nothing durable exists, and the only way to be sure of that is to
        find the problems before writing the first byte.
        """
        M = mods()
        problems = []
        try:
            register_view(self.repo)
            if register_mentions_run(self.repo, self.run_id):
                problems.append("the \u00a76.1 register already carries "
                                "attempts for run %r" % self.run_id)
        except ProductionRefusal as exc:
            problems.append(str(exc))
        ledger = os.path.join(self.repo, LEDGER_RELPATH.replace("/", os.sep))
        if not os.path.exists(ledger):
            problems.append("the exposure ledger %s is absent" % LEDGER_RELPATH)
        else:
            with open(ledger, encoding="utf-8") as fh:
                if count_tables(fh.read()) != 1:
                    problems.append("the exposure ledger does not contain "
                                    "exactly one markdown table")
        safe = "".join(c if c.isalnum() or c in "._-" else "_"
                       for c in self.run_id)[:64]
        if os.path.exists(os.path.join(self.journal_dir, "%s.step2.json" % safe)):
            problems.append("a step2 journal already exists for run %r"
                            % self.run_id)
        if problems:
            raise M["authorization"].Step2NotDurable(
                "step 2 was refused before any durable write: %s"
                % "; ".join(problems))

    def record_exposure_and_attempts(self, payload):
        """The prospective exposure event, the attempt classifications, AND the
        authoritative attempt registration.

        Three durable records, in this order, all part of one step-2 commitment:

        1. the machine-readable journal, fsynced;
        2. the human-readable §10.1 exposure row, appended and re-parsed;
        3. the §6.1 VARIANT_ATTEMPT rows, appended and re-parsed.

        (3) is not decoration. Without it a run reports an advanced cumulative
        Databento total while the authoritative register still holds the old
        one, so the next process reads the old one back and the attempts this
        run actually evaluated are never counted. The source of truth has to
        move, not the artifact's displayed number.

        Everything that could fail without writing is checked first, so a
        refusal here leaves the authorization usable; a failure after the first
        durable write is ambiguous and spends it, per the accepted D6 model.
        """
        self._precheck()
        journal_ref = self._journal("step2", {
            "run_id": self.run_id,
            "recorded_utc": self.clock(),
            "exposure_classification": self.exposure_classification,
            "exposure_scope": self.exposure_scope,
            "payload": payload,
        })
        note = (
            "X01 pre-execution step 2. Prospective exposure and trial "
            "commitment recorded BEFORE any target construction. run_id=%s. "
            "authorization=%s. Databento contribution +3 for A1, S1 and S2; "
            "E counts as one prospective ETF attempt "
            "(E_COUNTS_AS_ONE_PROSPECTIVE_ATTEMPT). Bootstrap replicates and "
            "crisis-window slices are NOT attempts. Machine record: %s."
            % (self.run_id,
               (payload.get("execution_identity") or {}).get("run_id", "unset"),
               journal_ref))
        row = append_exposure_row(self.repo, {
            "ts": self.clock(),
            "scope": self.exposure_scope,
            "classification": self.exposure_classification,
            "granularity": "NONE",
            "artifact_or_pointer": journal_ref,
            "note": note,
        }, verify=self.ledger_verifier)
        registered = append_trial_attempts(self.repo, self.run_id)
        return {"journal": journal_ref, "exposure_row": row[:80] + "...",
                "classification": self.exposure_classification,
                "trial_attempts": registered}

    # -- step 3 ------------------------------------------------------------- #
    def read_cumulative_databento_state(self):
        """Read the total at execution. `14 → 17` is never hard-coded."""
        anchor, anchor_src = read_carry_anchor(self.repo, self.carry_repo)
        contribution, rows, ledger_src = read_tsmom_contribution(self.repo)
        return {
            "cumulative": anchor + contribution,
            "source": "%s (N_TRIALS=%d) + %s §6.1 (%d attempt row(s), +%d)"
                      % (anchor_src, anchor, ledger_src, rows, contribution),
        }

    # -- step 4 ------------------------------------------------------------- #
    def record_seed_streams(self, protocol):
        return {"journal": self._journal("seeds", {
            "run_id": self.run_id,
            "recorded_utc": self.clock(),
            "seed_protocol": protocol})}


def _utc_now():
    import datetime as dt

    return dt.datetime.now(dt.timezone.utc).replace(
        microsecond=0).isoformat().replace("+00:00", "Z")


# --------------------------------------------------------------------------- #
# the plan
# --------------------------------------------------------------------------- #
def build_plan(repo=REPO, run_id=None, authorization_id=None,
               artifact_path=None, exposure_classification=None,
               counter=None, clock=None):
    """Everything a real run needs. Every AUTHORITY is built here, not supplied.

    Three things cannot be passed to this function
    ----------------------------------------------
    the authorization provider, the preflight function, and the governance
    recorder. Each is an authority: one decides whether the run is permitted,
    one whether the sealed contract still holds, and one whether the
    outcome-bearing commitment actually reached authoritative storage. All three
    are constructed here from the repository being executed.

    Why the recorder had to join them
    ---------------------------------
    It was a parameter until an audit showed what that allowed: a caller could
    hand in a no-op recorder and reach a valid authorization, an
    apparently-successful step 2, target construction and COMPLETED_EVIDENCE,
    while the authoritative register still held zero rows, the exposure ledger
    never moved, and a fresh process still read the old cumulative total — an
    artifact claiming 17 over storage that still said 14.

    The recorder is not a place a run writes. It is the thing that ATTESTS the
    prospective commitment was made, and an attestation the caller supplies
    attests nothing. So it is built here, and there is no parameter, keyword,
    factory, callback or environment override through which another one can
    arrive.

Four things cannot be passed to this function
    --------------------------------------------
    the authorization provider, the preflight function, the governance recorder
    and the target-data adapter. Every one of them is an authority: whether the
    run is permitted, whether the sealed contract holds, whether the commitment
    reached authoritative storage, and what the science was computed FROM.

    The data adapter was the last to go. Supplying one let a run pass every
    governance gate truthfully — register advanced, exposure row written,
    authorization spent — and still publish COMPLETED_EVIDENCE whose numbers
    came from synthetic panels while the artifact pinned the sealed manifest's
    real input hashes. Honest governance around false provenance is not an
    improvement on dishonest governance; it is harder to see.

    So the canonical adapter is built here, and it verifies every input's bytes
    against the manifest at the moment it reads them. There is no parameter,
    keyword, factory, callback or environment override through which another
    source of scientific data can arrive.

    A synthetic test injects one layer DOWN, at the orchestrator, or stands up a
    complete scratch repository — sealed fixture inputs, re-pinned manifest and
    all — and lets the canonical components run against it. Neither route goes
    through this function, and neither is reachable from the production
    entrypoint.
    """
    M = mods()
    orch, auth, rn = M["orchestrator"], M["authorization"], M["runner"]
    if not run_id:
        raise ProductionRefusal("a run_id is required: D4 binds the run itself")
    if not authorization_id:
        raise ProductionRefusal(
            "an authorization_id is required. A run is permitted by a committed "
            "record in %s naming this exact run, and by nothing else"
            % auth.LEDGER_RELPATH)

    ledger_path = os.path.join(repo, auth.LEDGER_RELPATH.replace("/", os.sep))
    provider = auth.LedgerAuthorizationProvider(
        auth.GitLedgerSource(repo), authorization_id,
        appender=auth.FileLedgerAppender(ledger_path),
        clock=clock or _utc_now,
        claim_store=auth.FileClaimStore(auth.claim_root(repo)))

    # Always the canonical recorder, against the repository being executed.
    # Not a default a caller may override: the parameter does not exist.
    recorder = ProductionGovernanceRecorder(
        repo=repo, run_id=run_id, clock=clock or _utc_now,
        exposure_classification=exposure_classification)
    # Always the canonical sealed reader, which verifies every input against
    # the manifest at read time. Not a default a caller may override: the
    # parameter does not exist.
    data_adapter = SealedTargetDataAdapter(repo)
    # Always the canonical gate. Not a default that a caller may override: the
    # parameter does not exist.
    preflight_fn = lambda: production_preflight(repo)  # noqa: E731

    return orch.ExecutionPlan(
        data_adapter=data_adapter, authorization_provider=provider,
        recorder=recorder, artifact_path=artifact_path,
        clock=clock or _utc_now, counter=counter or orch.TargetAdapterCallCounter(),
        preflight_fn=preflight_fn, run_id=run_id, repo=repo)


EXIT_COMPLETED = 0
EXIT_REFUSED = 2
EXIT_MECHANICAL_FAILURE = 3
EXIT_PROCEDURE_FAILURE = 4


def exit_code_for(artifact):
    M = mods()
    ev = M["evidence"]
    return {ev.COMPLETED_EVIDENCE: EXIT_COMPLETED,
            ev.EXECUTION_REFUSED: EXIT_REFUSED,
            ev.EXECUTION_MECHANICAL_FAILURE: EXIT_MECHANICAL_FAILURE,
            ev.INFERENCE_PROCEDURE_FAILURE: EXIT_PROCEDURE_FAILURE}.get(
                artifact.get("outcome_state"), EXIT_MECHANICAL_FAILURE)


def execute(args, out=None):
    """The production execution path. Returns (artifact, exit_code).

    One path. It builds the plan and calls the accepted orchestrator, which
    runs every gate in the authoritative order. There is no second route and no
    fast path: everything below `orch.run` is the reviewed architecture.
    """
    M = mods()
    orch, ev = M["orchestrator"], M["evidence"]
    out = out or sys.stdout
    if getattr(args, "no_runtime", False):
        # Accepted for symmetry with `preflight`, and inert. It cannot reach any
        # gate: the seal, the bindings, the authorization, the claim, the
        # exposure and trial accounting and the execution-revision check all run
        # regardless. Saying so out loud beats a silently ignored flag.
        out.write("note: --no-runtime does not affect any pre-execution gate; "
                  "the canonical seal check is mandatory for execution\n")
    try:
        plan = build_plan(
            repo=getattr(args, "repo", None) or REPO,
            run_id=getattr(args, "run_id", None),
            authorization_id=getattr(args, "authorization_id", None),
            artifact_path=getattr(args, "artifact", None),
            exposure_classification=getattr(args, "exposure_classification",
                                            None))
    except ProductionRefusal as exc:
        out.write("X01 EXECUTION REFUSED BEFORE ANY GATE: %s\n" % exc)
        return None, EXIT_REFUSED

    artifact = orch.run(plan)
    code = exit_code_for(artifact)
    state = artifact.get("outcome_state")
    gov = artifact.get("governance") or {}
    out.write("X01 EXECUTION OUTCOME: %s\n" % state)
    out.write("  run_id                 : %s\n" % plan.run_id)
    out.write("  authorization_id       : %s\n" % gov.get("authorization_id"))
    out.write("  last_completed_stage   : %s\n" % gov.get("last_completed_stage"))
    out.write("  target constructor calls: %d\n" % plan.counter.n)
    if state == ev.EXECUTION_REFUSED:
        out.write("  refusal_stage          : %s\n" % gov.get("refusal_stage"))
        out.write("  refusal_reason         : %s\n" % gov.get("refusal_reason"))
    if state == ev.EXECUTION_MECHANICAL_FAILURE:
        out.write("  failure_stage          : %s\n" % gov.get("failure_stage"))
        out.write("  failure_class          : %s\n" % gov.get("failure_class"))
        out.write("  failure_reason         : %s\n" % gov.get("failure_reason"))
    if plan.publication:
        out.write("  artifact_file_sha256   : %s\n"
                  % plan.publication.get("artifact_file_sha256"))
    return artifact, code


def add_arguments(parser):
    parser.add_argument("--authorization-id", dest="authorization_id",
                        help="the committed Owner authorization to spend")
    parser.add_argument("--run-id", dest="run_id",
                        help="the unique run this authorization binds")
    parser.add_argument("--artifact", dest="artifact",
                        help="path to publish the evidence artifact to")
    parser.add_argument("--exposure-classification",
                        dest="exposure_classification",
                        choices=list(EXPOSURE_CLASSES),
                        help="the ratified TBL-EXPOSURE-CLASSES token the step-2 "
                             "event carries. Owner input; there is no default")
    parser.add_argument("--no-runtime", action="store_true",
                        help="INERT for execution: the canonical seal query is "
                             "mandatory on every production path")
    return parser


def main(argv=None):
    p = add_arguments(argparse.ArgumentParser(description=__doc__.splitlines()[0]))
    args = p.parse_args(argv)
    _artifact, code = execute(args)
    return code


if __name__ == "__main__":
    sys.exit(main())
