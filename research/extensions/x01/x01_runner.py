"""X01 execution runner — PRE-EXECUTION SKELETON.

SCOPE, and the line this file exists to hold
--------------------------------------------
This module builds and enforces the X01 **execution manifest**, and it separates
two operations that must never be confused:

* ``build-manifest`` / ``preflight`` — read metadata, hash bytes, compare
  against the manifest. **Neither constructs a target series.** ``preflight``
  never opens a price panel for computation; it hashes files as opaque bytes.
* ``execute`` — would construct ``E``, ``F``, ``A1``, ``S1``, ``S2``, the paired
  179-month sample and the sealed statistics. **It is not implemented and
  refuses to run.** Its first line of real work would cross the target-execution
  boundary, which needs a separate Aaron authorization.

Building this file is not executing X01. No target series exists.

Why a manifest at all
---------------------
The canonical QROS seal (``qros_runtime.eligibility.seal_state``) compares the
preregistration **blob at ``seal_revision``** against the **blob at HEAD**. That
detects a later *committed* change to the contract. It cannot detect an
*uncommitted working-tree* edit, because neither blob moves. The manifest closes
that residual by pinning every byte the runner will consume, and by refusing to
proceed when any pin fails. It adds no governance concepts — it is a build-time
input contract.

Two revisions, and why neither is self-referential
--------------------------------------------------
``runner_base_revision`` (R1) is the immutable revision holding the runner and
the execution-relevant code whose blobs are pinned. The manifest is bound to R1
in a **later** commit (R2), because a commit cannot contain its own SHA. So
execution runs from a HEAD at or after R2, and ``HEAD == R1`` is deliberately
**not** required. What is verified instead:

* every pinned blob **at the current HEAD** still equals the value pinned at R1
  (a later *committed* edit to a pinned module therefore fails);
* the manifest's worktree bytes equal its **blob at HEAD** (an *uncommitted*
  edit to the manifest therefore fails);
* no pinned execution input has an uncommitted edit;
* only the narrowly role-validated governance changes are allowlisted.

There is no manifest self-hash field. Manifest integrity comes from the binding
commit plus the worktree-vs-HEAD refusal, not from hashing itself.

Hash convention — ONE representation, stated explicitly
-------------------------------------------------------
``core.autocrlf = true`` on this machine, so a working-tree text file and its git
blob can differ byte-for-byte while carrying identical content. Mixing the two
would make pins platform-dependent. Therefore:

* **tracked text** → ``sha256`` of the **git blob bytes at the declared
  revision** (``git cat-file blob <rev>:<path>``). EOL-normalised by git, so it
  is identical on every platform. Working-tree comparisons use ``lf_sha256``,
  the LF-normalised counterpart, so a CRLF checkout compares equal to its blob.
* **git-ignored data** (the parquet panels, the ETF CSV) → ``sha256`` of the
  **raw file on disk**, because there is no blob to appeal to.

Both are labelled per entry. The runner uses the same convention it wrote.
"""

import argparse
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CARRY = os.path.abspath(os.path.join(REPO, "..", "commodity-carry-research"))
RUNTIME = os.path.abspath(os.path.join(REPO, "..", "qros-runtime", "qros.py"))
MANIFEST = os.path.join(HERE, "X01_EXECUTION_MANIFEST.json")

SEALED_PREREG = "research/extensions/x01/X01_PREREGISTRATION_DRAFT.md"
SEALED_PREREG_SHA256 = "9c7b104f980fddb5613f02a3e8c1fab68ed9750b03b8161d42f92c3c96986743"
A2_RECORD = "research/extensions/review_history/X01_STAGE_A2_DESIGN_REVIEW_2026-09-08.md"
A2_RECORD_SHA256 = "173d138e00642554d5e30be4c463b9156f504f00e6c5ef01471592c4030acebe"
SEAL_REVISION = "df5b28ab7324c7ba789ab231431f077288c3fd84"

BLOB = "sha256_of_git_blob_bytes_at_revision"
RAW = "sha256_of_raw_file_on_disk"

# The runner's own execution-relevant code, pinned at the runner-base revision.
# The accepted implementation, in the two halves the sealed contract keeps
# apart: construction (E / A1 / S1 / S2, plus the additive §7 diagnostic
# interface) and inference (Sharpe, ΔS, the paired bootstrap, the CI and the
# classification). Both were audited and accepted together and are frozen at
# bc6c80536cd0fefc2ed1f440ca65d1c73d270e37, so both are revision-addressable
# and pinned exactly like the rest of the X01 machinery.
ACCEPTED_IMPLEMENTATION_FREEZE_REVISION = "bc6c80536cd0fefc2ed1f440ca65d1c73d270e37"

TARGET_CONSTRUCTION = [
    ("research/extensions/x01/x01_target_construction.py",
     "sealed target-construction layer for E / A1 / S1 / S2, with the additive "
     "§7 diagnostic interface"),
    ("research/extensions/x01/x01_construction_tests.py",
     "synthetic-only tests for the construction layer"),
]

INFERENCE = [
    ("research/extensions/x01/x01_inference.py",
     "sealed inference layer: Sharpe, ΔS, the paired joint stationary "
     "bootstrap, the percentile CI and the §5 classification, plus the S1/S2 "
     "descriptive arms, the sealed crisis windows and the §7 path diagnostics"),
    ("research/extensions/x01/x01_inference_tests.py",
     "synthetic-only tests for the inference layer"),
]

# Backwards-compatible alias: the construction freeze revision and the
# implementation freeze revision are the same commit now that both halves were
# accepted and frozen together.
TARGET_CONSTRUCTION_FREEZE_REVISION = ACCEPTED_IMPLEMENTATION_FREEZE_REVISION

# The bytes an independent audit accepted, recorded so a freeze can be checked
# against what was actually REVIEWED rather than against itself.
ACCEPTED_REVIEW_PINS = {
    "research/extensions/x01/x01_target_construction.py":
        "262aac9adf013a13b535ea816cd9373e747130235384b4559d83f9ffe412eb83",
    "research/extensions/x01/x01_construction_tests.py":
        "4e5cc510398c3b99eacb92ac23134c636d1a8bb2c9a1801e9bc382687245a90b",
    "research/extensions/x01/x01_inference.py":
        "1ece832e4d5a872a5dead732ea4ce1f24b36be56e3ea2238ebc376505ec50b06",
    "research/extensions/x01/x01_inference_tests.py":
        "0437f9cd060b40bc4efde36473f01922342aca9fcff045ebc8b05db572c4c65c",
}

# Provenance, kept rather than overwritten. The first construction freeze is a
# historical fact about a revision and stays true forever; it simply no longer
# describes the accepted implementation, because a later authorized delta added
# the §7 diagnostic interface and an audit accepted the result. Recording the
# supersession is what stops the old hash from reading as current.
SUPERSEDED_FREEZES = [
    {"revision": "851e9d3fd8d23c2f6802f796fcc32a21c5bd5a70",
     "scope": "target-construction only (no inference layer existed yet)",
     "accepted_review_pins": {
         "research/extensions/x01/x01_target_construction.py":
             "787b27b1634b1262397816ac2e9127d1e1f037acaf06caaf496c032a2f579e34",
         "research/extensions/x01/x01_construction_tests.py":
             "0e3248abd04a672138877ea55eefa1ac9d22b4b90a3380f72ce4fd1df6216f27"},
     "superseded_by": "the authorized additive §7 diagnostic-interface delta, "
                      "accepted together with the inference layer",
     "still_true": "those blobs remain exactly those bytes at that revision"},
]

# The accepted items 10-12 execution infrastructure, frozen at its own
# revision. It is a SEPARATE freeze from the construction/inference one because
# it was accepted separately, by a separate audit, at a later revision — and
# recording one revision for two different acceptances would make the earlier
# one unverifiable.
EXECUTION_INFRASTRUCTURE_FREEZE_REVISION = "699607a4f69156464886b46ddeddfd6dcc20863a"

# Exactly the six paths `x01_authorization.EXECUTION_INFRASTRUCTURE_PATHS`
# names. That list is what a D4 authorization binds, so the two must agree;
# `build_manifest` checks that they do rather than trusting this copy.
EXECUTION_INFRASTRUCTURE = [
    ("research/extensions/x01/x01_authorization.py",
     "item 12: the Owner D1-D6 execution-authorization mechanism"),
    ("research/extensions/x01/x01_evidence.py",
     "item 10: the evidence artifact schema and its validator"),
    ("research/extensions/x01/x01_execution_tests.py",
     "the synthetic-only execution-infrastructure suite"),
    ("research/extensions/x01/x01_orchestrator.py",
     "item 11: the ordered, fail-closed production execution path"),
    ("research/extensions/x01/x01_production.py",
     "the production adapters and the plan that wires them"),
    ("research/extensions/x01/x01_runner.py",
     "this runner, including the production `execute` entrypoint"),
]

# The bytes the independent audit accepted, recorded so the freeze can be
# checked against what was REVIEWED rather than against itself.
EXECUTION_INFRASTRUCTURE_REVIEW_PINS = {
    "research/extensions/x01/x01_authorization.py":
        "c11dee532a459b2f0899c9b3735a207a9319b9907ebfbba5b70acc3710f936b5",
    "research/extensions/x01/x01_evidence.py":
        "186605e67320d14805859961bb1c3c9846c8e3f563caf0dda0a844e4905163dc",
    "research/extensions/x01/x01_execution_tests.py":
        "37c4faf632d826ad60b10b04577752b0e370749973e4765247a6f44cff9e3e21",
    "research/extensions/x01/x01_orchestrator.py":
        "4d15528159610441ad96f0412ae212d3b1ee70a4b0397822d7f580022dcc92ea",
    "research/extensions/x01/x01_production.py":
        "307ea3b4f5394065143fd432d8628cf6fd78f5941359324b06d80671ee9dca74",
    "research/extensions/x01/x01_runner.py":
        "8ecb1b65dab68209060cf58f26d14ce6530ee08f7b08a68b2a281c85d2b4c77d",
}

# The authorization ledger is deliberately NOT pinned. It is append-only
# governance state, not code: a future Aaron authorization ADDS a record to it,
# and a hash pin would make every legitimate authorization break preflight. Its
# integrity comes from the append-only discipline the authorization layer
# enforces — a committed grant, committed records a strict prefix of the
# worktree ones — not from a frozen hash.
AUTHORIZATION_LEDGER = "ops/EXECUTION_AUTHORIZATIONS.md"

RUNNER_CODE = [
    ("research/extensions/x01/x01_runner.py", "this runner"),
    ("research/extensions/x01/x01_contract_tests.py",
     "the synthetic contract gate; execution safety depends on it"),
    ("research/extensions/validate_wave0.py", "the governance validator"),
] + TARGET_CONSTRUCTION + INFERENCE + [
    (path, why) for path, why in EXECUTION_INFRASTRUCTURE
    if path != "research/extensions/x01/x01_runner.py"]

# Tracked text the runner will materially consume. Pinned as BLOB hashes.
TRACKED_INPUTS = [
    (SEALED_PREREG, "the sealed scientific contract"),
    (A2_RECORD, "the A2 provenance record"),
    ("config.py", "frozen signal/sizing/cost/bootstrap constants"),
    ("src/signals.py", "baseline mean-of-signs composite (sealed 3.7)"),
    ("src/sizing.py", "per-asset vol targeting"),
    ("src/portfolio.py", "equal-weight sleeve aggregation"),
    ("src/performance.py", "the sealed Sharpe convention"),
    ("research/extensions/wave1/run_x02a_v3.py",
     "accepted X02 cash-first accounting (tsmom_chain_net_returns)"),
]

# git-ignored data. Pinned as RAW hashes; there is no blob for these.
# `data/` and `*.parquet` are git-ignored (market-data licensing), so the frozen
# ETF panel and the futures panels live here — which is also how the sealed
# contract §3.6 pins the ETF panel, by raw-file sha256 `3d2a7a56...c3c31`.
IGNORED_DATA_INPUTS = [
    ("data/close_prices_raw.csv", "frozen ETF panel (sealed E source)"),
    ("research/extensions/wave1/settle_v2.parquet", "settlement panel"),
    ("research/extensions/wave1/oi_v2.parquet", "open-interest panel"),
    ("research/extensions/wave1/contracts_meta.parquet", "contract definitions"),
]

# Execution-relevant modules that EXIST but are not yet revision-addressable.
# EMPTY: both accepted halves are now frozen and pinned. The list and its
# unconditional preflight refusal are kept deliberately, so that any module
# added here in future keeps production fail-closed until it too is bound.
PENDING_BINDING = []

# Present in the tree but NOT consumed by X01. Recorded so the inventory is
# complete and auditable; deliberately NOT hash-pinned, since pinning a
# non-input would imply that it is one.
NOT_CONSUMED = [
    ("research/extensions/wave1/settle_panel.parquet",
     "superseded raw-symbol-keyed panel from the first extraction; INVALID "
     "(CME one-digit years repeat on a 10-year cycle and merged two contracts "
     "per column) and retained only as implementation-error lineage. The sealed "
     "contract §3.6 names only the _v2 set, and no accepted implementation reads it"),
    ("research/extensions/wave1/oi_panel.parquet",
     "same superseded extraction; referenced neither by the sealed contract nor "
     "by any accepted implementation"),
    ("data/DGS3MO.csv",
     "a risk-free series would be material only under O-6 Option 2 (full carry "
     "accounting). Aaron adopted Option 1 SYMMETRIC_ZERO_CARRY, so no cash yield "
     "enters either leg and this file is not consumed"),
]

# Cross-repository S2 dependency. Carry is READ ONLY and is never modified.
CARRY_S2_PATH = "src/robustness.py"
CARRY_S2_SYMBOL = "fixed_calendar_front_series"

# The only tracked files whose in-flight modification the runner tolerates, and
# only after validating the ROLE of the change. Everything else refuses.
GOVERNANCE_APPEND_ONLY = (
    "ops/EXPOSURE_LEDGER.md",
    "ops/REVIEWER_EXPOSURE_LOG.md",
    "research/extensions/TRIAL_LEDGER.md",
)
GOVERNANCE_STATE = "qros-state.yaml"

# A ledger RECORD ROW: an exposure event (`| 2026-...` / `| UNKNOWN`) or a
# reviewer seat row (`| S12 |`). These are what "append-only" protects.
_RECORD_ROW = re.compile(r"^-\|\s*(?:20\d\d-|UNKNOWN|S\d+\s*\|)")


# --------------------------------------------------------------------------- #
# git helpers — metadata and bytes only, never a price computation
# --------------------------------------------------------------------------- #
def _git(repo, *args):
    out = subprocess.run(["git", "-C", repo] + list(args), capture_output=True)
    if out.returncode != 0:
        raise RuntimeError("git %s failed in %s: %s"
                           % (" ".join(args), repo, out.stderr.decode()[:200]))
    return out.stdout


def blob_sha256(repo, rev, path):
    """sha256 of the git blob bytes at `rev`. None when the path is absent."""
    try:
        return hashlib.sha256(_git(repo, "cat-file", "blob",
                                   "%s:%s" % (rev, path))).hexdigest()
    except RuntimeError:
        return None


def raw_sha256(abspath):
    """sha256 of the raw file, streamed. Never parses the file's contents."""
    if not os.path.exists(abspath):
        return None
    h = hashlib.sha256()
    with open(abspath, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def lf_sha256(abspath):
    """sha256 of a text file normalised to LF — the working-tree counterpart of
    a git blob hash, so a CRLF checkout compares equal to its blob."""
    if not os.path.exists(abspath):
        return None
    with open(abspath, "rb") as fh:
        return hashlib.sha256(fh.read().replace(b"\r\n", b"\n")).hexdigest()


def head(repo):
    return _git(repo, "rev-parse", "HEAD").decode().strip()


def porcelain(repo):
    """(modified_tracked, deleted_tracked) as sorted path lists."""
    modified, deleted = [], []
    for line in _git(repo, "status", "--porcelain",
                     "--untracked-files=no").decode().splitlines():
        code, path = line[:2], line[3:].strip().replace("\\", "/")
        if "D" in code:
            deleted.append(path)
        elif code.strip():
            modified.append(path)
    return sorted(modified), sorted(deleted)


def diff_only_adds(diff_lines):
    """Pure predicate: does this unified diff delete or alter any line?"""
    for line in diff_lines:
        if line.startswith("---") or line.startswith("+++"):
            continue
        if line.startswith("-"):
            return False
    return True


def diff_deletes_no_record_row(diff_lines):
    """Pure predicate: does this diff remove or alter an append-only RECORD ROW?

    The ledgers are append-only **in their rows**. Each also carries a derived
    "Normalized values as of the last row below" summary, which the file itself
    labels "a derived reading of the rows ... not a stored authority" and which
    is necessarily rewritten whenever a row is appended. Demanding a literally
    addition-only diff would refuse every legitimate append. This predicate
    protects the rows and permits the derived summary to move.

    Split out from the git call so the policy can be exercised on synthetic
    diffs without mutating a real governance file.
    """
    for line in diff_lines:
        if line.startswith("---") or line.startswith("+++"):
            continue
        if _RECORD_ROW.match(line):
            return False
    return True


def diff_is_append_only(repo, path):
    """True when the worktree diff against HEAD removes no record row."""
    return diff_deletes_no_record_row(
        _git(repo, "diff", "--unified=0", "--", path)
        .decode("utf-8", "replace").splitlines())


# --------------------------------------------------------------------------- #
# seed identity
# --------------------------------------------------------------------------- #
def seed_protocol():
    """Identify the three sealed child streams WITHOUT relying on `.entropy`.

    `SeedSequence(7).spawn(3)` returns three children that all report
    `entropy == 7` — the property does **not** distinguish them. What does is
    the deterministic `spawn_key` (`(0,)`, `(1,)`, `(2,)`) plus the state each
    child generates. Both are recorded, per arm, in the sealed arm order.

    This changes no statistical protocol. It is a precise operational
    representation of the already-sealed rule (see DEVIATIONS.md D-X01-1).
    """
    arms = ["primary", "S1", "S2"]
    try:
        import numpy as _np
        children = _np.random.SeedSequence(7).spawn(3)
        record = [{"arm": arm,
                   "spawn_key": list(child.spawn_key),
                   "master_entropy": 7,
                   "state_fingerprint_u32x4":
                       [int(v) for v in child.generate_state(4)]}
                  for arm, child in zip(arms, children)]
    except Exception:                      # numpy absent at manifest-build time
        record = None
    return {
        "master_seed": 7,
        "arm_order": arms,
        "derivation": "numpy.random.SeedSequence(7).spawn(3)",
        "identity_convention": (
            "Child streams are identified by `spawn_key` plus a 4x uint32 "
            "generated-state fingerprint. The `.entropy` property is NOT an "
            "identifier: all three children report entropy == 7, so it cannot "
            "distinguish them."),
        "note": ("The sealed text says the spawned values are written into it at "
                 "seal time; they are not. See DEVIATIONS.md D-X01-1. The streams "
                 "are re-derived mechanically from the sealed rule and recorded "
                 "here BEFORE any target output is read."),
        "child_streams": record,
    }


# --------------------------------------------------------------------------- #
# manifest
# --------------------------------------------------------------------------- #
def _binding_status(modules, revision=None, pins=None):
    """DERIVED, never asserted. `BOUND` means two things, both checked.

    1. the freeze REPRODUCED the reviewed bytes — every module's blob at the
       freeze revision equals the hash an independent audit accepted;
    2. the worktree matches what is COMMITTED — no uncommitted edit is sitting
       on top of the binding.

    The second clause is deliberately against HEAD and not against the freeze
    revision. A test module legitimately changes after its own freeze, because
    the binding it has to assert does not exist until the binding commit is
    made; treating that as a supersession would report every correct binding as
    broken. Which modules moved after the freeze is disclosed separately in
    `post_freeze_updated`, so nothing is hidden by the distinction.
    """
    revision = revision or ACCEPTED_IMPLEMENTATION_FREEZE_REVISION
    pins = pins if pins is not None else ACCEPTED_REVIEW_PINS
    rev_head = head(REPO)
    reviewed = all(blob_sha256(REPO, revision, path) == pins[path]
                   for path, _w in modules)
    if not reviewed:
        return "FREEZE_DOES_NOT_REPRODUCE_ACCEPTED_BYTES"
    committed = all(lf_sha256(os.path.join(REPO, path)) == blob_sha256(REPO, rev_head, path)
                    for path, _w in modules)
    if not committed:
        return "BOUND_REVISION_SUPERSEDED_BY_UNCOMMITTED_WORKTREE_DELTA"
    return "BOUND"


def _post_freeze_updated(modules, revision=None):
    """Modules whose committed bytes have moved since their own freeze.

    Recorded, not smoothed over: a reader can see exactly which bound files are
    no longer byte-identical to the freeze revision and why that is legitimate.
    """
    revision = revision or ACCEPTED_IMPLEMENTATION_FREEZE_REVISION
    rev_head = head(REPO)
    return [path for path, _w in modules
            if blob_sha256(REPO, rev_head, path)
            != blob_sha256(REPO, revision, path)]


def _binding_block(modules, meaning, revision=None, pins=None):
    """One accepted-implementation binding, in the shape preflight verifies.

    `revision` and `pins` are parameters because there is now more than one
    accepted implementation: construction and inference were accepted together
    at one revision, and the items 10-12 execution infrastructure at another.
    One builder, three blocks, one rule preflight can verify them all with.
    """
    revision = revision or ACCEPTED_IMPLEMENTATION_FREEZE_REVISION
    pins = pins if pins is not None else ACCEPTED_REVIEW_PINS
    return {
        "accepted_implementation_revision": revision,
        "status": _binding_status(modules, revision, pins),
        "modules": [
            {"path": path, "role": why, "hash_convention": BLOB,
             "sha256_at_freeze": blob_sha256(REPO, revision, path),
             "accepted_review_pin": pins[path]}
            for path, why in modules],
        "live_worktree_sha256_lf": {
            path: lf_sha256(os.path.join(REPO, path)) for path, _w in modules},
        "sha256_at_head": {
            path: blob_sha256(REPO, head(REPO), path) for path, _w in modules},
        "post_freeze_updated": _post_freeze_updated(modules, revision),
        "post_freeze_updated_note": (
            "Committed bytes that have moved since the freeze revision. A test "
            "module appears here legitimately: the binding it asserts does not "
            "exist until the binding commit, so it cannot have been frozen "
            "already asserting it. `sha256_at_freeze` vs `accepted_review_pin` "
            "is the check that the freeze reproduced what was reviewed, and it "
            "is unaffected."),
        "meaning": meaning,
    }


def _execution_infrastructure_revision():
    """The revision a D4 authorization binds, read from the authorization layer.

    Deliberately delegated rather than reimplemented: the manifest must record
    the value an authorization will actually be compared against, and two
    implementations of one rule is how those drift apart.
    """
    import importlib.util as _ilu

    spec = _ilu.spec_from_file_location(
        "x01_auth_for_manifest", os.path.join(HERE, "x01_authorization.py"))
    mod = _ilu.module_from_spec(spec)
    spec.loader.exec_module(mod)
    declared = [path for path, _w in EXECUTION_INFRASTRUCTURE]
    if sorted(mod.EXECUTION_INFRASTRUCTURE_PATHS) != sorted(declared):
        raise RuntimeError(
            "the runner's EXECUTION_INFRASTRUCTURE and the authorization "
            "layer's EXECUTION_INFRASTRUCTURE_PATHS disagree: %r vs %r"
            % (declared, list(mod.EXECUTION_INFRASTRUCTURE_PATHS)))
    return mod.execution_infrastructure_revision(REPO)


def build_manifest():
    """Pin every byte the future runner will consume. Reads no price data."""
    tsmom_head = head(REPO)
    carry_head = head(CARRY)

    entries = []
    for path, why in RUNNER_CODE:
        entries.append({"path": path, "role": why, "kind": "runner_code",
                        "hash_convention": BLOB, "revision": tsmom_head,
                        "sha256": blob_sha256(REPO, tsmom_head, path)})
    for path, why in TRACKED_INPUTS:
        entries.append({"path": path, "role": why, "kind": "tracked_text",
                        "hash_convention": BLOB, "revision": tsmom_head,
                        "sha256": blob_sha256(REPO, tsmom_head, path)})
    for path, why in IGNORED_DATA_INPUTS:
        entries.append({"path": path, "role": why, "kind": "git_ignored_data",
                        "hash_convention": RAW, "revision": None,
                        "sha256": raw_sha256(os.path.join(REPO, path))})

    return {
        "manifest_version": 2,
        "study": "X01 — commodity-sleeve futures transfer, matched-map arm",
        "purpose": ("Prospective byte pin for X01 execution. Closes the residual "
                    "that qros seal_state cannot see: an UNCOMMITTED working-tree "
                    "edit to the sealed contract or to any runner input."),
        "execution_authorized": False,
        "execution_authorization_note": (
            "A sealed preregistration and a FULL lane are NOT run authorization. "
            "`execute` refuses until Aaron authorizes target execution separately."),
        "hash_conventions": {
            BLOB: ("sha256 of `git cat-file blob <revision>:<path>`. Used for all "
                   "tracked text. EOL-normalised by git, so it is identical on "
                   "every platform despite core.autocrlf=true."),
            RAW: ("sha256 of the raw file on disk, streamed. Used for git-ignored "
                  "data (parquet, and data/ which is git-ignored), which has no "
                  "blob to appeal to."),
        },
        "sealed_contract": {
            "seal_revision": SEAL_REVISION,
            "prereg_path": SEALED_PREREG,
            "prereg_sha256_blob_at_seal": blob_sha256(REPO, SEAL_REVISION, SEALED_PREREG),
            "prereg_sha256_reviewed_pin": SEALED_PREREG_SHA256,
            "a2_record_path": A2_RECORD,
            "a2_record_sha256_blob_at_seal": blob_sha256(REPO, SEAL_REVISION, A2_RECORD),
            "a2_record_sha256_reviewed_pin": A2_RECORD_SHA256,
        },
        "runner_base": {
            "runner_base_revision": tsmom_head,
            "meaning": (
                "The immutable revision containing the runner and the "
                "execution-relevant code whose blobs are pinned below. It is NOT "
                "a claim that the later manifest-binding commit names itself: a "
                "commit cannot contain its own 40-hex SHA, and no such self-hash "
                "field exists here. Execution may run from a LATER HEAD (the "
                "manifest-binding revision and beyond); what is verified is that "
                "every pinned blob at the CURRENT HEAD still equals the value "
                "pinned at this base revision."),
            "manifest_self_hash": None,
            "manifest_integrity": (
                "protected by (1) the manifest-binding commit and (2) the "
                "worktree-vs-HEAD refusal in preflight, not by a self-hash."),
        },
        "inference_binding": _binding_block(
            INFERENCE,
            "The revision at which the independently accepted sealed INFERENCE "
            "implementation was frozen. Same mechanism, same checks and the same "
            "freeze commit as the construction binding below; recorded as its "
            "own block because the sealed contract keeps construction and "
            "inference apart and preflight verifies them separately."),
        "execution_infrastructure_binding": dict(
            _binding_block(
                EXECUTION_INFRASTRUCTURE,
                "The revision at which the independently accepted items 10-12 "
                "execution infrastructure was frozen. Same builder, same checks "
                "and the same meaning as the two scientific bindings, at its "
                "own revision because it was accepted by its own audit. These "
                "six paths are also the boundary a D4 authorization binds: "
                "changing any of them moves "
                "`execution_infrastructure_revision` and invalidates every "
                "authorization bound to the old one. BINDING IS NOT "
                "AUTHORIZATION.",
                revision=EXECUTION_INFRASTRUCTURE_FREEZE_REVISION,
                pins=EXECUTION_INFRASTRUCTURE_REVIEW_PINS),
            execution_infrastructure_revision=_execution_infrastructure_revision(),
            boundary_paths=[path for path, _w in EXECUTION_INFRASTRUCTURE],
            authorization_ledger={
                "path": AUTHORIZATION_LEDGER,
                "sha256_at_freeze": blob_sha256(
                    REPO, EXECUTION_INFRASTRUCTURE_FREEZE_REVISION,
                    AUTHORIZATION_LEDGER),
                "pinned": False,
                "why_not_pinned": (
                    "Append-only governance state, not code. A future Aaron "
                    "authorization adds a record; a hash pin would make every "
                    "legitimate authorization break preflight. Integrity comes "
                    "from the append-only discipline the authorization layer "
                    "enforces, not from a frozen hash."),
                "records_at_freeze": 0}),
        "superseded_freezes": SUPERSEDED_FREEZES,
        # Both halves go through the SAME builder, so the two blocks cannot
        # drift apart in shape and preflight can verify them with one rule.
        # `target_construction_revision` is kept as an alias of the accepted
        # implementation revision, because that is the field name the audited
        # contract already specifies.
        "target_construction_binding": dict(
            _binding_block(
                TARGET_CONSTRUCTION,
                "The revision at which the independently accepted "
                "target-construction implementation — including the additive §7 "
                "diagnostic interface — was frozen. `sha256_at_freeze` is read "
                "from git at that revision and must equal "
                "`accepted_review_pin`, the bytes the audit accepted: a freeze "
                "that does not reproduce the reviewed bytes is not a freeze. "
                "Current integrity is carried by the runner_code pins below, "
                "compared both at HEAD and against the live worktree. "
                "BINDING IS NOT AUTHORIZATION: `execution_authorized` stays "
                "false and `execute` refuses unconditionally, without "
                "consulting preflight, the manifest or this block."),
            target_construction_revision=ACCEPTED_IMPLEMENTATION_FREEZE_REVISION),
        "not_consumed_by_x01": [{"path": p, "reason": w} for p, w in NOT_CONSUMED],
        "pending_binding": [
            {"path": path, "role": why,
             "target_construction_revision": None,
             "sha256_worktree_lf": lf_sha256(os.path.join(REPO, path)),
             "status": "UNCOMMITTED_PENDING_BINDING",
             "note": ("Present in the working tree and NOT revision-addressable. "
                      "No git revision or blob pin is fabricated for it. Preflight "
                      "REFUSES while this list is non-empty, so production stays "
                      "fail-closed until a future authorized binding commit.")}
            for path, why in PENDING_BINDING
            if os.path.exists(os.path.join(REPO, path))
        ],
        "carry_s2_dependency": {
            "repo": "commodity-carry-research",
            "revision": carry_head,
            "path": CARRY_S2_PATH,
            "symbol": CARRY_S2_SYMBOL,
            "hash_convention": BLOB,
            "sha256": blob_sha256(CARRY, carry_head, CARRY_S2_PATH),
            "note": "READ ONLY. carry is never modified by X01.",
        },
        "inputs": entries,
        "dirty_worktree_policy": {
            "refuse_if_any_pinned_path_modified_or_deleted": True,
            "append_only_allowlist": list(GOVERNANCE_APPEND_ONLY),
            "state_allowlist": [GOVERNANCE_STATE],
            "rule": ("A modified tracked file refuses execution unless it is in "
                     "an allowlist AND its role validates: the append-only "
                     "governance ledgers must delete or alter no RECORD ROW "
                     "(their derived normalisation summary may move); "
                     "qros-state.yaml must keep its seal pointer, lane and sealed "
                     "input pins unchanged against HEAD. There is no blanket "
                     "'dirty tree is okay' rule, and this does not rely on QROS "
                     "R10, which does not hold the target-execution edge."),
        },
        "seed_protocol": seed_protocol(),
    }


def cmd_build_manifest(_args):
    m = build_manifest()
    with open(MANIFEST, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(m, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    missing = [e["path"] for e in m["inputs"] if e["sha256"] is None]
    print("manifest written: %s" % os.path.relpath(MANIFEST, REPO))
    print("  runner base revision : %s" % m["runner_base"]["runner_base_revision"])
    for kind in ("runner_code", "tracked_text", "git_ignored_data"):
        print("  %-20s : %d" % (kind, sum(1 for e in m["inputs"] if e["kind"] == kind)))
    print("  not consumed         : %d" % len(m["not_consumed_by_x01"]))
    print("  carry S2 revision    : %s" % m["carry_s2_dependency"]["revision"][:12])
    if missing:
        print("  UNRESOLVED PINS      : %s" % ", ".join(missing))
        return 1
    return 0


# --------------------------------------------------------------------------- #
# preflight — the refusal gate. Constructs nothing.
# --------------------------------------------------------------------------- #
class Refusal(object):
    def __init__(self):
        self.reasons = []
        self.checks = []

    def check(self, name, ok, detail=""):
        self.checks.append((name, bool(ok), detail))
        if not ok:
            self.reasons.append("%s%s" % (name, (" — " + detail) if detail else ""))

    @property
    def ok(self):
        return not self.reasons


def seal_state_from_runtime():
    """Ask the CANONICAL runtime. No second sealing mechanism is implemented."""
    if not os.path.exists(RUNTIME):
        return None, "the qros runtime is not present at %s" % RUNTIME
    out = subprocess.run(
        [sys.executable, RUNTIME, "--state", os.path.join(REPO, "qros-state.yaml"),
         "check"], capture_output=True)
    text = (out.stdout + out.stderr).decode("utf-8", "replace")
    for line in text.splitlines():
        if "SEAL=" in line:
            return line.split("SEAL=", 1)[1].split()[0].strip(), line.strip()
    return None, "no SEAL= line in the runtime's output"


def preflight(manifest=None, strict_state=True, status=None):
    """Verify every manifest pin. Opens no price panel for computation.

    `status` injects a `(modified, deleted)` pair instead of reading the live
    worktree, so the dirty-tree policy can be exercised deterministically
    without dirtying a real file.
    """
    r = Refusal()
    if manifest is None:
        if not os.path.exists(MANIFEST):
            r.check("execution manifest exists", False, MANIFEST)
            return r
        with open(MANIFEST, encoding="utf-8") as fh:
            manifest = json.load(fh)
    now_head = head(REPO)

    # A. the canonical seal, asked of the canonical runtime
    if strict_state:
        state, detail = seal_state_from_runtime()
        r.check("canonical seal derives VERIFIED", state == "VERIFIED",
                detail if state != "VERIFIED" else "")

    # B. the sealed contract, as bytes on disk RIGHT NOW. This is the check
    #    seal_state structurally cannot make.
    sc = manifest["sealed_contract"]
    live = lf_sha256(os.path.join(REPO, sc["prereg_path"]))
    r.check("worktree preregistration matches the sealed contract",
            live == sc["prereg_sha256_reviewed_pin"], "on disk %s" % (live or "MISSING"))
    r.check("sealed prereg blob at seal_revision matches the reviewed pin",
            sc["prereg_sha256_blob_at_seal"] == sc["prereg_sha256_reviewed_pin"])
    r.check("A2 record blob at seal_revision matches the reviewed pin",
            sc["a2_record_sha256_blob_at_seal"] == sc["a2_record_sha256_reviewed_pin"])

    # C. runner base. Execution runs from a LATER HEAD than the base, so
    #    HEAD == base is deliberately NOT required.
    rb = manifest["runner_base"]
    r.check("manifest names a runner base revision", bool(rb.get("runner_base_revision")),
            "null — the runner's own bytes are not yet revision-addressable")
    r.check("manifest declares no self-hash", rb.get("manifest_self_hash") is None)
    if rb.get("runner_base_revision"):
        r.check("runner base revision resolves in this repository",
                blob_sha256(REPO, rb["runner_base_revision"],
                            "research/extensions/x01/x01_runner.py") is not None)

    # C1b. anything execution-relevant that is not yet revision-addressable
    #      keeps production fail-closed. No pin is fabricated for it.
    for e in manifest.get("pending_binding", []):
        r.check("execution-relevant module is revision-bound: %s" % e["path"], False,
                e.get("status", "UNCOMMITTED_PENDING_BINDING"))

    # C1c. the target-construction binding, verified against git rather than
    #      taken on the manifest's word. The freeze must reproduce the bytes an
    #      independent audit accepted; anything else is a rebind, not a freeze.
    for _label, _key, _revkey in (
            ("target-construction", "target_construction_binding",
             "target_construction_revision"),
            ("inference", "inference_binding", "accepted_implementation_revision"),
            ("execution-infrastructure", "execution_infrastructure_binding",
             "accepted_implementation_revision")):
        _b = manifest.get(_key)
        r.check("manifest binds an accepted %s revision" % _label,
                bool(_b and _b.get(_revkey)),
                "absent or null — that half of the implementation is not bound")
    tcb = manifest.get("target_construction_binding")
    infb = manifest.get("inference_binding")
    eib = manifest.get("execution_infrastructure_binding")
    for tag, blk, revkey in (("construction", tcb, "target_construction_revision"),
                             ("inference", infb, "accepted_implementation_revision"),
                             ("execution-infrastructure", eib,
                              "accepted_implementation_revision")):
        if not (blk and blk.get(revkey)):
            continue
        rev = blk[revkey]
        for mod in blk.get("modules", []):
            at_freeze = blob_sha256(REPO, rev, mod["path"])
            r.check("bound blob resolves at the freeze revision: %s" % mod["path"],
                    at_freeze is not None, "revision %s does not resolve" % rev[:12])
            r.check("frozen blob equals the recorded freeze hash: %s" % mod["path"],
                    at_freeze == mod.get("sha256_at_freeze"),
                    "git %s recorded %s" % (str(at_freeze)[:12],
                                            str(mod.get("sha256_at_freeze"))[:12]))
            r.check("frozen blob equals the INDEPENDENTLY ACCEPTED bytes: %s"
                    % mod["path"],
                    at_freeze == mod.get("accepted_review_pin"),
                    "git %s accepted %s" % (str(at_freeze)[:12],
                                            str(mod.get("accepted_review_pin"))[:12]))
        del tag

    # C2. the manifest itself must be committed and unedited.
    man_rel = os.path.relpath(MANIFEST, REPO).replace("\\", "/")
    man_head = blob_sha256(REPO, now_head, man_rel)
    man_live = lf_sha256(MANIFEST)
    r.check("execution manifest is committed at HEAD", man_head is not None,
            "not committed — bind it before execution")
    r.check("no uncommitted edit to the execution manifest",
            man_head is None or man_head == man_live,
            "worktree manifest differs from its blob at HEAD")

    # D/E. every pinned input, by its own declared convention.
    #
    # TWO INDEPENDENT comparisons for tracked text, deliberately:
    #   * blob-at-HEAD  -> catches a later COMMITTED edit;
    #   * live worktree -> catches an UNCOMMITTED edit, which the blob check
    #     structurally CANNOT see because the blob does not move.
    # The live side uses `lf_sha256`, the LF-normalised counterpart of a git blob
    # hash; `.gitattributes` pins these paths to LF, so the two representations
    # are the same bytes and the comparison is exact. This is defence in depth
    # BESIDE the dirty-tree policy, never a replacement for it.
    for e in manifest["inputs"]:
        path = e["path"]
        label = "runner code" if e["kind"] == "runner_code" else "pinned input"
        if e["hash_convention"] == BLOB:
            at_head = blob_sha256(REPO, now_head, path)
            live = lf_sha256(os.path.join(REPO, path))
            r.check("%s blob at HEAD matches the pin: %s" % (label, path),
                    at_head == e["sha256"],
                    "pinned %s HEAD %s" % (str(e["sha256"])[:12], str(at_head)[:12]))
            r.check("%s LIVE worktree bytes match the pin: %s" % (label, path),
                    live == e["sha256"],
                    "pinned %s live %s" % (str(e["sha256"])[:12], str(live)[:12]))
        else:
            now = raw_sha256(os.path.join(REPO, path))
            r.check("pinned input unchanged: %s" % path, now == e["sha256"],
                    "expected %s got %s" % (str(e["sha256"])[:12], str(now)[:12]))

    # F. cross-repository S2 dependency
    c = manifest["carry_s2_dependency"]
    try:
        carry_now_rev = head(CARRY)
        carry_now = blob_sha256(CARRY, carry_now_rev, c["path"])
    except RuntimeError as exc:
        carry_now_rev, carry_now = None, None
        r.check("carry repository readable", False, str(exc)[:120])
    r.check("carry S2 revision unchanged", carry_now_rev == c["revision"],
            "expected %s got %s" % (c["revision"][:12], str(carry_now_rev)[:12]))
    r.check("carry S2 file unchanged", carry_now == c["sha256"])

    # G. dirty-worktree policy — smallest allowlist, role-validated
    modified, deleted = porcelain(REPO) if status is None else status
    pinned = {e["path"] for e in manifest["inputs"]
              if e["kind"] in ("tracked_text", "runner_code")} | {
        sc["prereg_path"], sc["a2_record_path"], man_rel}
    hit = sorted((set(modified) | set(deleted)) & pinned)
    r.check("no pinned path is modified or deleted", not hit, ", ".join(hit))

    allow = set(manifest["dirty_worktree_policy"]["append_only_allowlist"])
    state_allow = set(manifest["dirty_worktree_policy"]["state_allowlist"])
    unapproved = sorted(set(modified) - allow - state_allow)
    r.check("no unapproved tracked modification", not unapproved, ", ".join(unapproved))
    if status is None:                       # role validation needs the real tree
        for path in sorted(set(modified) & allow):
            r.check("append-only governance file keeps every record row: %s" % path,
                    diff_is_append_only(REPO, path))
        for path in sorted(set(modified) & state_allow):
            r.check("qros-state seal pointer unchanged vs HEAD: %s" % path,
                    _state_pointer_unchanged(path))
    r.check("no tracked deletion", not deleted, ", ".join(deleted))
    return r


def _state_pointer_unchanged(path):
    """The state file may move, but never its seal pointer, lane or sealed pins."""
    import yaml
    at_head = yaml.safe_load(_git(REPO, "show", "HEAD:%s" % path).decode("utf-8"))
    now = yaml.safe_load(open(os.path.join(REPO, path), encoding="utf-8").read())
    if at_head.get("prereg") != now.get("prereg"):
        return False
    if at_head.get("lane") != now.get("lane"):
        return False
    sealed_ids = {"x01_preregistration_sealed", "x01_a2_review_record"}
    pick = lambda d: {i["id"]: i.get("observed_sha256")
                      for i in (d.get("inputs") or []) if i["id"] in sealed_ids}
    return pick(at_head) == pick(now)


def cmd_preflight(args):
    r = preflight(strict_state=not args.no_runtime)
    width = max(len(n) for n, _, _ in r.checks)
    for name, ok, detail in r.checks:
        print("  %-*s %s%s" % (width, name, "PASS" if ok else "REFUSE",
                               ("   " + detail) if detail and not ok else ""))
    print()
    if r.ok:
        print("PRE_EXECUTION_PREFLIGHT = PASS — every manifest pin holds.")
        print("This is NOT execution authorization.")
        return 0
    print("PRE_EXECUTION_PREFLIGHT = REFUSE (%d condition(s) failed)" % len(r.reasons))
    for reason in r.reasons:
        print("   " + reason)
    return 1


# --------------------------------------------------------------------------- #
# execute — the production entrypoint.
# --------------------------------------------------------------------------- #
# It is complete. What stands between this command and a real X01 execution is
# an AUTHORIZATION — a committed record in `ops/EXECUTION_AUTHORIZATIONS.md`
# naming this exact run and binding the seven D4 identities — and two run-time
# arguments. No further production code has to be written for an authorized run
# to proceed, and none of it can be reached without the authorization.
#
# The path is `x01_production.build_plan` followed by `x01_orchestrator.run`,
# and there is no second route. Every gate — preflight, committed authorization,
# the atomic one-shot claim, the step-2 exposure and trial commitment, the
# cumulative Databento read, the seed-stream record, the sealed sample — runs in
# the authoritative order inside that one call.
_PRODUCTION_MODULE = None


def _production():
    """Load the production adapters lazily, and exactly ONCE.

    Lazy because importing them pulls in the orchestrator, which pulls in this
    module again, and because `preflight` must stay usable where pandas is not
    installed. Cached because a second copy of one file defines a second set of
    exception classes, and an `except` clause in one copy does not catch what
    the other raises.
    """
    global _PRODUCTION_MODULE
    if _PRODUCTION_MODULE is None:
        path = os.path.join(HERE, "x01_production.py")
        spec = importlib.util.spec_from_file_location("x01_prod_entry", path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules["x01_prod_entry"] = mod
        spec.loader.exec_module(mod)
        _PRODUCTION_MODULE = mod
    return _PRODUCTION_MODULE


def cmd_execute(args):
    """Run X01. Refuses unless a committed Owner authorization permits it."""
    _artifact, code = _production().execute(args)
    return code


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("build-manifest", help="pin every input byte").set_defaults(
        func=cmd_build_manifest)
    pf = sub.add_parser("preflight", help="verify pins; constructs nothing")
    pf.add_argument("--no-runtime", action="store_true",
                    help="skip the canonical qros seal query (offline checks only)")
    pf.set_defaults(func=cmd_preflight)
    ex = sub.add_parser(
        "execute", help="run X01 — refuses without a committed Owner "
                        "authorization naming this run")
    ex.add_argument("--authorization-id", dest="authorization_id",
                    help="the committed Owner authorization to spend")
    ex.add_argument("--run-id", dest="run_id",
                    help="the unique run this authorization binds")
    ex.add_argument("--artifact", dest="artifact",
                    help="path to publish the evidence artifact to")
    ex.add_argument("--exposure-classification", dest="exposure_classification",
                    help="the ratified TBL-EXPOSURE-CLASSES token the step-2 "
                         "event carries. Owner input; there is no default")
    ex.add_argument("--no-runtime", action="store_true",
                    help="INERT for execution: the canonical seal query is "
                         "mandatory on every production path")
    ex.set_defaults(func=cmd_execute)
    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
