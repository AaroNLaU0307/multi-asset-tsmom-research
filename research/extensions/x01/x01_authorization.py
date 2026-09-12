"""X01 execution authorization — Owner policy D1–D6, mechanical and fail-closed.

What this module is
-------------------
The machine-readable side of a single Owner decision: *may this exact run
happen, once?* Aaron sealed the policy as six decisions and this module is
their implementation, with no discretion of its own.

    D1  the authority is a dedicated append-only ledger,
        ``ops/EXECUTION_AUTHORIZATIONS.md``, carrying a machine-readable
        record — not ``human_decisions[]``, whose three-token vocabulary
        (DORMANT_ENTER / DORMANT_EXIT / REVIEW_ATTEMPT_EXCLUDED) is closed and
        means something else entirely, and not a chat statement.
    D2  the record counts only in COMMITTED git state. A worktree-only record
        is INVALID, and that check refuses rather than warns.
    D3  ONE_SHOT. One ``authorization_id`` authorizes exactly one
        outcome-bearing run: never persistent, never reusable after
        consumption, never implicit, never transferable to another ``run_id``.
    D4  the record binds exactly seven identities and every one must match
        exactly. No fuzzy matching, no fallback, no default.
    D5  authorizing is NOT exposure. Validating a record touches no exposure or
        trial ledger; exposure begins at the authoritative step 2.
    D6  consumption is permanent at durable step 2. Failures before step 2 do
        not consume; an ambiguous step 2 resolves to CONSUMED_OR_INDETERMINATE
        and is never reusable.

The asymmetry that makes this safe
----------------------------------
GRANTING power requires committed state; BLOCKING it does not. A grant is read
only from the committed blob, so nobody can authorize a run by editing a file.
Lifecycle events — the ones that consume or invalidate — are honoured from the
worktree too, because a run that has already spent an authorization must be
stopped even though the appended event has not been committed yet. Fail-closed
is not symmetric, and pretending it is would be the bug.

Crash safety without a transaction
----------------------------------
There is no way to make "write the exposure record" and "mark the
authorization consumed" one atomic act across two files. So the order is
write-ahead: an in-flight marker is appended and flushed BEFORE step 2 is
attempted, and a resolving event is appended after. A process that dies in
between leaves a dangling in-flight marker, and an unresolved marker resolves
to CONSUMED_OR_INDETERMINATE. The failure mode is therefore "an authorization
is spent that maybe should not have been", which costs a new Owner
authorization, rather than "an authorization is reused", which costs a second
undisclosed look at the target.

What this module never does
---------------------------
It computes no statistic, constructs nothing, reads no target data, and appends
nothing to any exposure or trial ledger. Validation is read-only with respect to
exposure accounting, and that is enforced here rather than promised: the
provider counts ledger writes across a validation and refuses if the count
moved.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess

# --------------------------------------------------------------------------- #
# D1 — the record and where it lives
# --------------------------------------------------------------------------- #
LEDGER_RELPATH = "ops/EXECUTION_AUTHORIZATIONS.md"
SCHEMA_NAME = "x01-execution-authorization"
SCHEMA_VERSION = 1
OWNER_IDENTITY = "Aaron"
RESEARCH_ID = "TSMOM-EXT-001"
ONE_SHOT_SCOPE = "ONE_SHOT_SINGLE_OUTCOME_BEARING_RUN"

RECORD_TYPE_AUTHORIZATION = "AUTHORIZATION"
RECORD_TYPE_LIFECYCLE = "LIFECYCLE"
RECORD_TYPES = (RECORD_TYPE_AUTHORIZATION, RECORD_TYPE_LIFECYCLE)

# D4 — exactly these seven, in this order. Adding an eighth silently would mean
# binding something nothing checks; dropping one would mean checking less than
# the Owner decided. Both are refused by an exact set comparison below.
BOUND_IDENTITY_FIELDS = (
    "research_id",
    "run_id",
    "prereg_sha256",
    "execution_infrastructure_revision",
    "construction_binding_revision",
    "inference_binding_revision",
    "manifest_sha256",
)

_HEX40 = re.compile(r"^[0-9a-f]{40}$")
_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_RUN_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{2,63}$")
_AUTH_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{2,63}$")
_UTC = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})$")

# Shape rules per bound field. A shape rule is not a substitute for the exact
# comparison against the live identity — it exists so a malformed record is
# refused as malformed rather than silently failing to match something.
FIELD_SHAPES = {
    "research_id": lambda v: v == RESEARCH_ID,
    "run_id": lambda v: bool(_RUN_ID.match(v)),
    "prereg_sha256": lambda v: bool(_HEX64.match(v)),
    "execution_infrastructure_revision": lambda v: bool(_HEX40.match(v)),
    "construction_binding_revision": lambda v: bool(_HEX40.match(v)),
    "inference_binding_revision": lambda v: bool(_HEX40.match(v)),
    "manifest_sha256": lambda v: bool(_HEX64.match(v)),
}

AUTHORIZATION_KEYS_REQUIRED = frozenset(
    ("record_type", "schema", "authorization_id", "owner", "authorized_utc",
     "status", "scope", "binding"))
AUTHORIZATION_KEYS_OPTIONAL = frozenset(("note",))
LIFECYCLE_KEYS_REQUIRED = frozenset(
    ("record_type", "schema", "authorization_id", "event", "event_utc",
     "run_id", "reason"))
LIFECYCLE_KEYS_OPTIONAL = frozenset(("evidence", "note"))

# --------------------------------------------------------------------------- #
# D3 / D6 / §8 — the append-only lifecycle
# --------------------------------------------------------------------------- #
STATUS_AUTHORIZED = "AUTHORIZED"
STATUS_CONSUMED = "CONSUMED"
STATUS_CONSUMED_OR_INDETERMINATE = "CONSUMED_OR_INDETERMINATE"
STATUS_INVALIDATED = "INVALIDATED"
STATUS_NO_SUCH_AUTHORIZATION = "NO_SUCH_AUTHORIZATION"
STATUS_LEDGER_UNUSABLE = "LEDGER_UNUSABLE"

# The four the machine must be able to distinguish (§8), plus the two states
# that are not lifecycle states at all but still have to be nameable.
LIFECYCLE_STATUSES = (STATUS_AUTHORIZED, STATUS_CONSUMED,
                      STATUS_CONSUMED_OR_INDETERMINATE, STATUS_INVALIDATED)
BLOCKING_STATUSES = (STATUS_CONSUMED, STATUS_CONSUMED_OR_INDETERMINATE,
                     STATUS_INVALIDATED, STATUS_NO_SUCH_AUTHORIZATION,
                     STATUS_LEDGER_UNUSABLE)

EVENT_STEP2_STARTED = "STEP2_ATTEMPT_STARTED"
EVENT_STEP2_ABANDONED = "STEP2_ABANDONED_NO_DURABLE_WRITE"
EVENT_CONSUMED = "CONSUMED"
EVENT_INDETERMINATE = "CONSUMED_OR_INDETERMINATE"
EVENT_INVALIDATED = "INVALIDATED"
LIFECYCLE_EVENTS = (EVENT_STEP2_STARTED, EVENT_STEP2_ABANDONED, EVENT_CONSUMED,
                    EVENT_INDETERMINATE, EVENT_INVALIDATED)
TERMINAL_EVENTS = {EVENT_CONSUMED: STATUS_CONSUMED,
                   EVENT_INDETERMINATE: STATUS_CONSUMED_OR_INDETERMINATE,
                   EVENT_INVALIDATED: STATUS_INVALIDATED}

# --------------------------------------------------------------------------- #
# refusal reason codes — asserted on by tests, so a refusal cannot silently
# change its meaning while still "refusing"
# --------------------------------------------------------------------------- #
REASON_NO_LEDGER = "AUTHORIZATION_LEDGER_ABSENT_FROM_COMMITTED_GIT_STATE"
REASON_MALFORMED = "AUTHORIZATION_LEDGER_MALFORMED"
REASON_NOT_COMMITTED = "AUTHORIZATION_NOT_IN_COMMITTED_GIT_STATE"
REASON_APPEND_ONLY = "AUTHORIZATION_LEDGER_APPEND_ONLY_VIOLATION"
REASON_NO_SUCH = "NO_SUCH_AUTHORIZATION_ID"
REASON_DUPLICATE = "DUPLICATE_AUTHORIZATION_ID"
REASON_NOT_ACTIVE = "AUTHORIZATION_NOT_ACTIVE"
REASON_BINDING = "AUTHORIZATION_BINDING_MISMATCH"
REASON_IDENTITY_INCOMPLETE = "EXECUTION_IDENTITY_INCOMPLETE"
REASON_VALIDATION_MUTATED = "AUTHORIZATION_VALIDATION_MUTATED_LEDGER"
REASON_ALREADY_CLAIMED = "AUTHORIZATION_ALREADY_CLAIMED"
REASON_LEDGER_MISSING_FROM_WORKTREE = "AUTHORIZATION_LEDGER_MISSING_FROM_WORKTREE"
REASON_CLAIM_LOST = "AUTHORIZATION_CLAIM_LOST_TO_ANOTHER_PROCESS"
REASON_STALE_VALIDATION = "AUTHORIZATION_NO_LONGER_ACTIVE_AT_STEP2_BOUNDARY"

# The execution infrastructure whose revision D4 binds. Deliberately NOT the
# repository HEAD: the authorization record is itself committed, and a record
# cannot contain the hash of the commit that contains it. What it can name — and
# what actually matters — is the revision of the code that would execute.
EXECUTION_INFRASTRUCTURE_PATHS = (
    "research/extensions/x01/x01_authorization.py",
    "research/extensions/x01/x01_evidence.py",
    "research/extensions/x01/x01_execution_tests.py",
    "research/extensions/x01/x01_orchestrator.py",
    "research/extensions/x01/x01_production.py",
    "research/extensions/x01/x01_runner.py",
)
UNCOMMITTED_INFRASTRUCTURE = "UNCOMMITTED_EXECUTION_INFRASTRUCTURE"
DIRTY_INFRASTRUCTURE = "EXECUTION_INFRASTRUCTURE_WORKTREE_DIFFERS_FROM_HEAD"


class AuthorizationError(RuntimeError):
    """A caller used the lifecycle API in a way the Owner policy forbids."""


class Step2NotDurable(Exception):
    """PROOF that the authoritative step-2 write left nothing durable.

    A recorder raises this only when it can demonstrate that no byte of the
    exposure and trial commitment reached durable storage. Every other failure —
    including a plain exception — is ambiguous by default, because "we do not
    know" and "nothing was written" are different, and only one of them lets an
    authorization survive. Recorders that cannot prove atomicity simply never
    raise this, and their failures fail closed.
    """


# --------------------------------------------------------------------------- #
# parsing — the ledger is markdown for humans and fenced JSON for the machine
# --------------------------------------------------------------------------- #
def _fenced_json_blocks(text):
    """Every ```json block, in file order, with its 1-based start line.

    Only ```json fences are records. Documentation, schema examples and the
    file's own prose live in ```text fences and are invisible here, which is
    why the shipped ledger can explain the format without accidentally
    containing an authorization.
    """
    blocks, cur, start = [], None, 0
    for i, line in enumerate(text.splitlines(), start=1):
        s = line.strip()
        if cur is None:
            if s == "```json":
                cur, start = [], i
            continue
        if s == "```":
            blocks.append(("\n".join(cur), start))
            cur = None
            continue
        cur.append(line)
    if cur is not None:
        blocks.append((None, start))
    return blocks


def _validate_schema_block(payload, where, problems):
    sch = payload.get("schema")
    if not isinstance(sch, dict) or sch.get("name") != SCHEMA_NAME \
            or sch.get("version") != SCHEMA_VERSION:
        problems.append("%s: schema must be {'name': %r, 'version': %d}"
                        % (where, SCHEMA_NAME, SCHEMA_VERSION))


def _validate_key_set(payload, required, optional, where, problems):
    keys = set(payload)
    missing = sorted(required - keys)
    extra = sorted(keys - required - optional)
    if missing:
        problems.append("%s: missing %s" % (where, ", ".join(missing)))
    if extra:
        problems.append("%s: unrecognised key(s) %s — an unrecognised field is "
                        "refused rather than ignored, because a record must not "
                        "appear to say more than the machine checks"
                        % (where, ", ".join(extra)))


def _validate_authorization(payload, where, problems):
    _validate_key_set(payload, AUTHORIZATION_KEYS_REQUIRED,
                      AUTHORIZATION_KEYS_OPTIONAL, where, problems)
    _validate_schema_block(payload, where, problems)
    aid = payload.get("authorization_id")
    if not isinstance(aid, str) or not _AUTH_ID.match(aid):
        problems.append("%s: authorization_id is missing or malformed" % where)
    if payload.get("owner") != OWNER_IDENTITY:
        problems.append("%s: owner must be %r — the Owner is the only authority "
                        "for a real run" % (where, OWNER_IDENTITY))
    ts = payload.get("authorized_utc")
    if not isinstance(ts, str) or not _UTC.match(ts):
        problems.append("%s: authorized_utc must be an ISO-8601 UTC timestamp"
                        % where)
    if payload.get("status") != STATUS_AUTHORIZED:
        problems.append("%s: an AUTHORIZATION record is written with status %r; "
                        "later states are appended as LIFECYCLE records, never "
                        "edited in" % (where, STATUS_AUTHORIZED))
    if payload.get("scope") != ONE_SHOT_SCOPE:
        problems.append("%s: scope must be %r (D3)" % (where, ONE_SHOT_SCOPE))

    binding = payload.get("binding")
    if not isinstance(binding, dict):
        problems.append("%s: binding block is missing" % where)
        return
    want, got = set(BOUND_IDENTITY_FIELDS), set(binding)
    if want != got:
        problems.append(
            "%s: binding must be EXACTLY the seven D4 identities; missing %s, "
            "unexpected %s" % (where, sorted(want - got) or "none",
                               sorted(got - want) or "none"))
    for field in BOUND_IDENTITY_FIELDS:
        if field not in binding:
            continue
        value = binding[field]
        if not isinstance(value, str) or not FIELD_SHAPES[field](value):
            problems.append("%s: binding.%s is not a well-formed %s"
                            % (where, field, field))


def _validate_lifecycle(payload, where, problems):
    _validate_key_set(payload, LIFECYCLE_KEYS_REQUIRED, LIFECYCLE_KEYS_OPTIONAL,
                      where, problems)
    _validate_schema_block(payload, where, problems)
    aid = payload.get("authorization_id")
    if not isinstance(aid, str) or not _AUTH_ID.match(aid):
        problems.append("%s: authorization_id is missing or malformed" % where)
    if payload.get("event") not in LIFECYCLE_EVENTS:
        problems.append("%s: event %r is not one of %s"
                        % (where, payload.get("event"), list(LIFECYCLE_EVENTS)))
    ts = payload.get("event_utc")
    if not isinstance(ts, str) or not _UTC.match(ts):
        problems.append("%s: event_utc must be an ISO-8601 UTC timestamp" % where)
    rid = payload.get("run_id")
    if not isinstance(rid, str) or not _RUN_ID.match(rid):
        problems.append("%s: run_id is missing or malformed" % where)
    if not payload.get("reason"):
        problems.append("%s: reason is required — a lifecycle transition with no "
                        "stated cause is not auditable" % where)


def parse_ledger(text):
    """(records, problems). ANY problem makes the whole ledger unusable.

    There is no partial credit: a ledger the parser cannot fully account for is
    a ledger whose authorization state is unknown, and unknown fails closed.
    """
    problems = []
    if text is None:
        return [], ["the authorization ledger is absent"]
    records = []
    for raw, line in _fenced_json_blocks(text):
        where = "record at line %d" % line
        if raw is None:
            problems.append("%s: unterminated ```json fence" % where)
            continue
        try:
            payload = json.loads(raw)
        except Exception as exc:                      # noqa: BLE001
            problems.append("%s: not parseable JSON (%s)" % (where, exc))
            continue
        if not isinstance(payload, dict):
            problems.append("%s: a record must be a JSON object" % where)
            continue
        kind = payload.get("record_type")
        if kind == RECORD_TYPE_AUTHORIZATION:
            _validate_authorization(payload, where, problems)
        elif kind == RECORD_TYPE_LIFECYCLE:
            _validate_lifecycle(payload, where, problems)
        else:
            problems.append("%s: record_type %r is not one of %s"
                            % (where, kind, list(RECORD_TYPES)))
            continue
        records.append(payload)
    return records, problems


def canonical(payload):
    """Deterministic bytes for one record, used only for identity comparison."""
    return json.dumps(payload, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False)


def committed_is_prefix_of(committed, worktree):
    """§8: history is appended to, never rewritten.

    The committed record list must be an exact prefix of the worktree list. A
    worktree that dropped, reordered or edited a committed record has rewritten
    history, and the whole ledger is refused — including the grants it still
    appears to contain.
    """
    if len(worktree) < len(committed):
        return False
    return all(canonical(a) == canonical(b)
               for a, b in zip(committed, worktree[:len(committed)]))


# --------------------------------------------------------------------------- #
# lifecycle resolution
# --------------------------------------------------------------------------- #
class Lifecycle(object):
    """The resolved state of exactly one authorization_id."""

    __slots__ = ("authorization_id", "status", "grant", "problems", "in_flight",
                 "history")

    def __init__(self, authorization_id, status, grant=None, problems=None,
                 in_flight=False, history=None):
        self.authorization_id = authorization_id
        self.status = status
        self.grant = grant
        self.problems = list(problems or [])
        self.in_flight = in_flight
        self.history = list(history or [])

    @property
    def active(self):
        return self.status == STATUS_AUTHORIZED and not self.problems

    def __repr__(self):                               # pragma: no cover - debug
        return "<Lifecycle %s %s%s>" % (self.authorization_id, self.status,
                                        " +problems" if self.problems else "")


def resolve(records, authorization_id):
    """Replay the append-only history for one id and return where it ended.

    Terminal states absorb: the first one wins and nothing afterwards can
    return the authorization to AUTHORIZED. An in-flight marker that was never
    resolved is a crashed attempt, and D6's ambiguity rule makes that
    CONSUMED_OR_INDETERMINATE.
    """
    grants = [r for r in records
              if r.get("record_type") == RECORD_TYPE_AUTHORIZATION
              and r.get("authorization_id") == authorization_id]
    events = [r for r in records
              if r.get("record_type") == RECORD_TYPE_LIFECYCLE
              and r.get("authorization_id") == authorization_id]

    if not grants:
        return Lifecycle(authorization_id, STATUS_NO_SUCH_AUTHORIZATION,
                         history=events)
    if len(grants) > 1:
        return Lifecycle(
            authorization_id, STATUS_LEDGER_UNUSABLE, grant=None,
            problems=["%d AUTHORIZATION records share authorization_id %r; the "
                      "id no longer identifies one grant and is unusable"
                      % (len(grants), authorization_id)],
            history=events)

    grant = grants[0]
    bound_run_id = (grant.get("binding") or {}).get("run_id")
    status, in_flight, problems = STATUS_AUTHORIZED, False, []

    for ev in events:
        if ev.get("run_id") != bound_run_id:
            problems.append(
                "lifecycle event %r names run_id %r but the grant binds %r — a "
                "single authorization covers exactly one run (D3)"
                % (ev.get("event"), ev.get("run_id"), bound_run_id))
        kind = ev.get("event")
        if status != STATUS_AUTHORIZED:
            problems.append(
                "lifecycle event %r appears after the authorization already "
                "reached the terminal state %s" % (kind, status))
            continue
        if kind == EVENT_STEP2_STARTED:
            if in_flight:
                problems.append(
                    "a second %s appears while an earlier attempt was still "
                    "unresolved" % EVENT_STEP2_STARTED)
            in_flight = True
        elif kind == EVENT_STEP2_ABANDONED:
            if not in_flight:
                problems.append("%s appears with no attempt in flight"
                                % EVENT_STEP2_ABANDONED)
            in_flight = False
        else:
            status = TERMINAL_EVENTS[kind]
            in_flight = False

    if status == STATUS_AUTHORIZED and in_flight:
        # D6: a started attempt with no resolving event. Whether step 2 became
        # durable is exactly the question we cannot answer, so it fails closed.
        status = STATUS_CONSUMED_OR_INDETERMINATE
        problems.append(
            "an attempt recorded %s and never resolved; whether step 2 was "
            "durably completed is indeterminate, so the authorization is "
            "treated as spent (D6)" % EVENT_STEP2_STARTED)
    if problems and status == STATUS_AUTHORIZED:
        status = STATUS_CONSUMED_OR_INDETERMINATE
    return Lifecycle(authorization_id, status, grant, problems, in_flight, events)


# --------------------------------------------------------------------------- #
# storage — one provider, two interchangeable backings
# --------------------------------------------------------------------------- #
def _git(repo, *args):
    out = subprocess.run(["git", "-C", repo] + list(args), capture_output=True)
    if out.returncode != 0:
        raise RuntimeError("git %s failed: %s"
                           % (" ".join(args), out.stderr.decode()[:200]))
    return out.stdout


class GitLedgerSource(object):
    """The real backing: committed bytes from git, worktree bytes from disk."""

    def __init__(self, repo, relpath=LEDGER_RELPATH, revision="HEAD"):
        self.repo = repo
        self.relpath = relpath
        self._revision = revision

    def revision(self):
        try:
            return _git(self.repo, "rev-parse", self._revision).decode().strip()
        except RuntimeError:
            return None

    def committed_text(self):
        """The blob at the revision. None when the path is not in that tree."""
        try:
            return _git(self.repo, "cat-file", "blob",
                        "%s:%s" % (self._revision, self.relpath)
                        ).decode("utf-8", "replace")
        except RuntimeError:
            return None

    def worktree_text(self):
        path = os.path.join(self.repo, self.relpath.replace("/", os.sep))
        if not os.path.exists(path):
            return None
        with open(path, encoding="utf-8") as fh:
            return fh.read()


class InMemoryLedgerSource(object):
    """A synthetic backing with the SAME two questions. Tests use this.

    It models the one distinction D2 turns on — committed bytes versus worktree
    bytes — and nothing else, so the provider logic under test is the real one.
    """

    def __init__(self, committed=None, worktree=None,
                 revision="0123456789abcdef0123456789abcdef01234567"):
        self.committed = committed
        self.worktree = worktree if worktree is not None else committed
        self._revision = revision

    def revision(self):
        return self._revision

    def committed_text(self):
        return self.committed

    def worktree_text(self):
        return self.worktree


def render_record(payload):
    """One record as the markdown the ledger actually stores."""
    kind = payload.get("record_type")
    label = payload.get("event") or payload.get("status") or kind
    return ("\n### %s — %s — %s\n\n```json\n%s\n```\n"
            % (kind, payload.get("authorization_id"), label,
               json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=False)))


class InMemoryLedgerAppender(object):
    """Appends into an InMemoryLedgerSource's WORKTREE text.

    Appending to the worktree and not to the committed text is deliberate and
    is what a real run does: a run cannot commit, so the events it writes are
    uncommitted — and they still block reuse, because blocking does not require
    committed state.
    """

    def __init__(self, source, crash_before_resolution=False):
        self.source = source
        self.records = []
        self.crash_before_resolution = crash_before_resolution

    @property
    def count(self):
        return len(self.records)

    def append(self, payload):
        if self.crash_before_resolution and payload.get("event") != EVENT_STEP2_STARTED:
            raise RuntimeError("synthetic process death before the resolving "
                               "lifecycle event could be appended")
        self.records.append(payload)
        self.source.worktree = (self.source.worktree or "") + render_record(payload)
        return "%s:%s:%d" % (payload.get("authorization_id"),
                             payload.get("event"), len(self.records))


# --------------------------------------------------------------------------- #
# D3 — the atomic one-shot claim
# --------------------------------------------------------------------------- #
CLAIM_DIRNAME = "execution-claims"
CLAIM_SUFFIX = ".claim"


def claim_root(repo, relpath=None):
    return os.path.join(repo, "ops", CLAIM_DIRNAME) if relpath is None \
        else os.path.join(repo, relpath)


class ClaimLost(Exception):
    """Another process won the claim. This process must not enter step 2."""


class FileClaimStore(object):
    """Exactly-once entry to step 2, enforced by the filesystem.

    Why this exists at all
    ----------------------
    Validating an authorization and replaying the ledger afterwards cannot stop
    a second run: two processes can both validate the same active authorization,
    both believe it is theirs, and both reach step 2 before either has written
    anything. Ledger replay then discovers the double commitment after two
    exposure events already exist, which is exactly too late. Per-provider
    in-memory bookkeeping is no better — it cannot see another process at all.

    What makes it atomic
    --------------------
    ``os.open(..., O_CREAT | O_EXCL)`` is a single system call in which the
    kernel guarantees exactly one creator. Every loser gets ``FileExistsError``.
    It works across processes, across sessions and across interpreters, which a
    Python-level lock does not.

    A claim is never released on failure, only on PROVEN non-durability
    (§7's before-step-2 rule). An unexplained claim is permanent, so a process
    that dies immediately after claiming leaves the authorization unavailable —
    the fail-closed direction.
    """

    def __init__(self, root):
        self.root = root

    def _path(self, authorization_id):
        # The id is sanitised for the filesystem and disambiguated by a digest,
        # so two distinct ids can never collide on one file and a legal id
        # containing ':' cannot produce an illegal Windows path.
        safe = re.sub(r"[^A-Za-z0-9._-]", "_", authorization_id)[:48]
        tag = hashlib.sha256(authorization_id.encode("utf-8")).hexdigest()[:16]
        return os.path.join(self.root, "%s-%s%s" % (safe, tag, CLAIM_SUFFIX))

    def claim(self, authorization_id, payload):
        """True if THIS caller won. False if someone else already holds it."""
        if not os.path.isdir(self.root):
            os.makedirs(self.root, exist_ok=True)
        path = self._path(authorization_id)
        try:
            fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError:
            return False
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(canonical(payload) + "\n")
            fh.flush()
            os.fsync(fh.fileno())
        return True

    def existing(self, authorization_id):
        """The claim payload, or None. Read-only: it never creates anything.

        An unreadable or half-written claim file still counts as a claim. The
        file's EXISTENCE is the fact; its contents are only for the audit trail,
        so a torn write must not read as "unclaimed".
        """
        path = self._path(authorization_id)
        if not os.path.exists(path):
            return None
        try:
            with open(path, encoding="utf-8") as fh:
                return json.loads(fh.read())
        except Exception:                             # noqa: BLE001
            return {"claim_record": "UNREADABLE_BUT_PRESENT",
                    "file": os.path.basename(path)}

    def release(self, authorization_id):
        """Release a claim. Legitimate in EXACTLY one case.

        Only after it is PROVEN that step 2 wrote nothing durable and that the
        abandonment has itself been durably recorded. Any other release would
        hand a second process an authorization that may already have been spent.
        """
        path = self._path(authorization_id)
        if os.path.exists(path):
            os.remove(path)


class FileLedgerAppender(object):
    """Appends to a real file and FLUSHES IT DURABLY before returning.

    ``os.fsync`` is the whole point: the write-ahead ordering only protects
    anything if the in-flight marker is on the platter before step 2 is
    attempted. A buffered append would leave exactly the window it exists to
    close.
    """

    def __init__(self, path):
        self.path = path
        self.records = []

    @property
    def count(self):
        return len(self.records)

    def append(self, payload):
        with open(self.path, "a", encoding="utf-8", newline="\n") as fh:
            fh.write(render_record(payload))
            fh.flush()
            os.fsync(fh.fileno())
        self.records.append(payload)
        return "%s:%s:%d" % (payload.get("authorization_id"),
                             payload.get("event"), len(self.records))


# --------------------------------------------------------------------------- #
# the provider — what the orchestrator's authorization gate consults
# --------------------------------------------------------------------------- #
class LedgerAuthorizationProvider(object):
    """D1–D6, enforced. Returns a citable reference or a refusal reason.

    ``declared`` is True because the Owner HAS declared a mechanism. That is a
    statement about policy, not about permission: this provider still refuses
    every identity for which no committed, active, exactly-bound record exists,
    which today is all of them.
    """

    declared = True

    def __init__(self, source, authorization_id, appender=None, clock=None,
                 claim_store=None):
        self.source = source
        self.authorization_id = authorization_id
        self.appender = appender
        self.clock = clock or (lambda: "1970-01-01T00:00:00Z")
        self.claim_store = claim_store
        self.validations = 0
        self.last_lifecycle = None
        self._session = None

    # -- D5 ---------------------------------------------------------------- #
    def _ledger_write_count(self):
        return self.appender.count if self.appender is not None else 0

    def authorization_for(self, identity):
        """(reference, None) or (None, why). NEVER touches exposure accounting.

        The write counter around the body is not decoration. D5 says validating
        an authorization is not an exposure event and must not move any ledger;
        counting is how that becomes a check instead of a claim.
        """
        self.validations += 1
        before = self._ledger_write_count()
        reference, why = self._validate(identity)
        if self._ledger_write_count() != before:
            return None, ("%s: validating an authorization appended to a ledger; "
                          "D5 makes validation read-only with respect to "
                          "exposure and lifecycle accounting"
                          % REASON_VALIDATION_MUTATED)
        return reference, why

    def _load(self):
        """(committed_records, worktree_records, refusal_or_None).

        The one place both views of the ledger are read and reconciled, so the
        provider and the step-2 boundary can never disagree about what it says.
        """
        committed_text = self.source.committed_text()
        worktree_text = self.source.worktree_text()

        if committed_text is None:
            # "There is no ledger" and "your ledger is not committed" send the
            # operator to different places, so they are different refusals.
            if worktree_text is not None:
                return None, None, ("%s: %s exists in the working tree but not "
                                    "in committed git state, and D2 makes an "
                                    "uncommitted authorization INVALID"
                                    % (REASON_NOT_COMMITTED, LEDGER_RELPATH))
            return None, None, ("%s: %s is not present at the applicable "
                                "revision" % (REASON_NO_LEDGER, LEDGER_RELPATH))
        if worktree_text is None:
            # The ledger is committed but absent from the working tree. Falling
            # back to committed bytes here would silently discard every
            # uncommitted consumption event and could make a spent authorization
            # look active, so a missing tracked ledger fails closed instead.
            return None, None, ("%s: %s is committed but missing from the "
                                "working tree; an absent ledger cannot be read "
                                "as an unconsumed one"
                                % (REASON_LEDGER_MISSING_FROM_WORKTREE,
                                   LEDGER_RELPATH))

        committed, c_problems = parse_ledger(committed_text)
        if c_problems:
            return None, None, ("%s: the committed ledger has %d problem(s): %s"
                                % (REASON_MALFORMED, len(c_problems),
                                   "; ".join(c_problems[:3])))
        worktree, w_problems = parse_ledger(worktree_text)
        if w_problems:
            return None, None, ("%s: the working-tree ledger has %d problem(s): "
                                "%s" % (REASON_MALFORMED, len(w_problems),
                                        "; ".join(w_problems[:3])))
        if not committed_is_prefix_of(committed, worktree):
            return None, None, ("%s: the working-tree ledger is not the "
                                "committed ledger plus appended records; a "
                                "rewritten history cannot be reconciled and is "
                                "refused whole" % REASON_APPEND_ONLY)
        return committed, worktree, None

    def resolve_now(self):
        """Re-read the ledger from storage and resolve the CURRENT state.

        Called again at the step-2 boundary. A validation performed earlier is a
        statement about the past: between it and the outcome-bearing attempt
        another process may have consumed the same authorization, and permission
        does not carry forward across that gap.
        """
        committed, worktree, refusal = self._load()
        if refusal is not None:
            return Lifecycle(self.authorization_id, STATUS_LEDGER_UNUSABLE,
                             problems=[refusal])
        if resolve(committed, self.authorization_id).status == \
                STATUS_NO_SUCH_AUTHORIZATION:
            return Lifecycle(self.authorization_id, STATUS_NO_SUCH_AUTHORIZATION)
        return resolve(worktree, self.authorization_id)

    def _validate(self, identity):
        # ---- D2: the grant is read from COMMITTED bytes, never the worktree --
        committed, worktree, refusal = self._load()
        if refusal is not None:
            return None, refusal

        # ---- the GRANT must be committed; BLOCKING evidence need not be ------
        committed_state = resolve(committed, self.authorization_id)
        if committed_state.status == STATUS_NO_SUCH_AUTHORIZATION:
            worktree_state = resolve(worktree, self.authorization_id)
            if worktree_state.grant is not None:
                return None, ("%s: authorization %r exists only in the working "
                              "tree. D2: uncommitted is INVALID, and this check "
                              "is not advisory"
                              % (REASON_NOT_COMMITTED, self.authorization_id))
            return None, ("%s: no committed AUTHORIZATION record for %r"
                          % (REASON_NO_SUCH, self.authorization_id))
        if committed_state.status == STATUS_LEDGER_UNUSABLE:
            return None, ("%s: %s" % (REASON_DUPLICATE,
                                      "; ".join(committed_state.problems)))

        state = resolve(worktree, self.authorization_id)
        self.last_lifecycle = state
        if not state.active:
            return None, ("%s: authorization %r resolves to %s%s"
                          % (REASON_NOT_ACTIVE, self.authorization_id,
                             state.status,
                             (" — " + "; ".join(state.problems))
                             if state.problems else ""))

        # An existing claim is a fact about availability, not about the ledger:
        # some process already reached the step-2 boundary with this
        # authorization. It is READ here and never created here, so validating
        # still reserves nothing (D5).
        if self.claim_store is not None:
            held = self.claim_store.existing(self.authorization_id)
            if held is not None:
                return None, ("%s: authorization %r is already claimed (%s). A "
                              "claim is taken immediately before the "
                              "outcome-bearing boundary and is released only on "
                              "proof that step 2 wrote nothing"
                              % (REASON_ALREADY_CLAIMED, self.authorization_id,
                                 canonical(held)[:120]))

        # ---- D4: exactly seven identities, each exactly equal ---------------
        # The grant comes from the COMMITTED record list, never from the working
        # tree. The append-only prefix rule above already makes the two the same
        # bytes, so this changes no behaviour today; it is the second line of
        # defence, and it is the line that still holds if the first is ever
        # weakened. `state` is used only for the LIFECYCLE, where working-tree
        # evidence is honoured deliberately.
        grant = committed_state.grant
        binding = grant["binding"]
        missing = [f for f in BOUND_IDENTITY_FIELDS if not identity.get(f)]
        if missing:
            return None, ("%s: the run could not establish %s, so the "
                          "authorization cannot be checked against it"
                          % (REASON_IDENTITY_INCOMPLETE, ", ".join(missing)))
        mismatches = []
        for field in BOUND_IDENTITY_FIELDS:
            want, got = binding[field], identity.get(field)
            if not isinstance(got, str) or got != want:
                mismatches.append("%s: authorized %r, would execute %r"
                                  % (field, want, got))
        if mismatches:
            return None, ("%s: %d of the seven bound identities differ — %s"
                          % (REASON_BINDING, len(mismatches),
                             "; ".join(mismatches)))

        return {
            "authorization_id": grant["authorization_id"],
            "owner": grant["owner"],
            "authorized_utc": grant["authorized_utc"],
            "run_id": binding["run_id"],
            "scope": grant["scope"],
            "status_at_validation": state.status,
            "ledger": LEDGER_RELPATH,
            "ledger_revision": self.source.revision(),
            "bound_identity_fields": list(BOUND_IDENTITY_FIELDS),
            "commit_requirement": "COMMITTED_GIT_STATE_REQUIRED",
            "validation_touched_exposure_accounting": False,
        }, None

    # -- D6 / §9 ----------------------------------------------------------- #
    def open_session(self, reference):
        """One session per provider. A second is a double-execution attempt."""
        if self._session is not None:
            raise AuthorizationError(
                "a second execution session was opened against authorization "
                "%s; D3 authorizes exactly one outcome-bearing run"
                % self.authorization_id)
        if self.appender is None:
            raise AuthorizationError(
                "no append-only lifecycle store is configured, so consumption "
                "could not be recorded; refusing rather than running "
                "unaccountably")
        if self.claim_store is None:
            raise AuthorizationError(
                "no atomic claim store is configured, so exactly-once entry to "
                "step 2 cannot be guaranteed across processes; refusing rather "
                "than relying on in-process bookkeeping that another process "
                "cannot see")
        self._session = AuthorizationSession(reference, self.appender,
                                             self.clock, self.claim_store,
                                             provider=self)
        return self._session


class AuthorizationSession(object):
    """Governance bookkeeping around the durable step-2 boundary.

    It inserts no scientific step. Step 2 is unchanged and still happens exactly
    where the sealed four-step sequence puts it; this only writes what is known
    about it, before and after, into the append-only authorization ledger.
    """

    def __init__(self, reference, appender, clock, claim_store=None,
                 provider=None):
        self.reference = reference
        self.authorization_id = reference["authorization_id"]
        self.run_id = reference["run_id"]
        self.appender = appender
        self.clock = clock
        self.claim_store = claim_store
        self.provider = provider
        self.status = STATUS_AUTHORIZED
        self.attempted = False
        self.begun = False
        self.claimed = False
        self.resolved = False
        self.events = []

    def _append(self, event, reason, evidence=None):
        payload = {
            "record_type": RECORD_TYPE_LIFECYCLE,
            "schema": {"name": SCHEMA_NAME, "version": SCHEMA_VERSION},
            "authorization_id": self.authorization_id,
            "event": event,
            "event_utc": self.clock(),
            "run_id": self.run_id,
            "reason": reason,
        }
        if evidence is not None:
            payload["evidence"] = evidence
        ref = self.appender.append(payload)
        self.events.append(event)
        return ref

    def begin_step2(self):
        """Re-check, CLAIM atomically, then write the in-flight marker.

        Three things in this order, and the order is the whole point.

        1. Re-resolve the ledger. The validation that opened this session is a
           statement about the past; another process may have consumed the
           authorization since, and a stale validation must never carry
           permission forward.
        2. Take the atomic claim. This is the exactly-once boundary: the kernel
           decides the winner, so two processes that both validated
           successfully cannot both proceed. It happens BEFORE the marker and
           before step 2, so a loser stops with nothing written.
        3. Write the write-ahead marker.

        A crash anywhere after (2) leaves a claim nobody released, and an
        unreleased claim makes the authorization unavailable. That is the
        fail-closed direction: a wasted authorization, never a reused one.
        """
        if self.attempted:
            raise AuthorizationError(
                "step 2 was already attempted under authorization %s; a second "
                "attempt would be a second outcome-bearing commitment"
                % self.authorization_id)
        self.attempted = True

        if self.provider is not None:
            state = self.provider.resolve_now()
            if not state.active:
                raise AuthorizationError(
                    "%s: authorization %s resolves to %s at the step-2 "
                    "boundary; an earlier successful validation does not carry "
                    "permission forward%s"
                    % (REASON_STALE_VALIDATION, self.authorization_id,
                       state.status,
                       (" — " + "; ".join(state.problems))
                       if state.problems else ""))

        if self.claim_store is None:
            raise AuthorizationError(
                "no atomic claim store is configured, so exactly-once entry to "
                "step 2 cannot be guaranteed across processes")
        won = self.claim_store.claim(self.authorization_id, {
            "authorization_id": self.authorization_id,
            "run_id": self.run_id,
            "pid": os.getpid(),
            "claimed_utc": self.clock(),
            "note": "claimed immediately before the outcome-bearing boundary",
        })
        if not won:
            raise AuthorizationError(
                "%s: authorization %s was already claimed by another process; "
                "exactly one claimant may enter step 2 (D3)"
                % (REASON_CLAIM_LOST, self.authorization_id))
        self.claimed = True
        self.begun = True
        return self._append(
            EVENT_STEP2_STARTED,
            "the authoritative step-2 exposure and trial commitment is about to "
            "be attempted; if this marker is never resolved the authorization "
            "is indeterminate and unusable (D6)")

    def _resolve(self, event, reason, evidence=None):
        if not self.begun:
            raise AuthorizationError("step 2 was never begun under %s"
                                     % self.authorization_id)
        if self.resolved:
            raise AuthorizationError("the step-2 attempt under %s was already "
                                     "resolved" % self.authorization_id)
        self.resolved = True
        return self._append(event, reason, evidence)

    def step2_durably_completed(self, evidence_reference):
        """D6: consumed, permanently. The claim is NEVER released."""
        self.status = STATUS_CONSUMED
        return self._resolve(EVENT_CONSUMED, "STEP2_DURABLY_COMPLETED",
                             {"exposure_record_reference": evidence_reference})

    def step2_definitely_not_written(self, reason):
        """§7: nothing durable exists, so the authorization survives.

        The claim is released here and ONLY here. Release is safe exactly when
        two things are true together: the recorder proved nothing durable was
        written, and the abandonment itself has been durably recorded. If the
        abandonment cannot be recorded, the claim stays and the status becomes
        indeterminate — because a caller that ignored the write failure would
        otherwise be told the authorization is still good while the ledger says
        an attempt started and never finished.
        """
        try:
            ref = self._resolve(EVENT_STEP2_ABANDONED,
                                "STEP2_PROVEN_NOT_DURABLE: %s" % reason)
        except Exception:
            self.status = STATUS_CONSUMED_OR_INDETERMINATE
            raise
        self.status = STATUS_AUTHORIZED
        if self.claimed and self.claim_store is not None:
            self.claim_store.release(self.authorization_id)
            self.claimed = False
        return ref

    def step2_ambiguous(self, reason):
        """§7: persistence unknown, so it is spent. Fail closed.

        The status moves first. If the resolving event cannot be appended, the
        ledger is left holding a dangling marker — which replays as
        indeterminate anyway — and a caller that swallowed the write failure
        still sees the same answer here.
        """
        self.status = STATUS_CONSUMED_OR_INDETERMINATE
        return self._resolve(EVENT_INDETERMINATE,
                             "STEP2_PERSISTENCE_AMBIGUOUS: %s" % reason)


# --------------------------------------------------------------------------- #
# execution-infrastructure identity
# --------------------------------------------------------------------------- #
def _committed_blob(repo, rev, path):
    try:
        return _git(repo, "cat-file", "blob", "%s:%s" % (rev, path))
    except RuntimeError:
        return None


def execution_infrastructure_revision(repo, paths=EXECUTION_INFRASTRUCTURE_PATHS,
                                      revision="HEAD"):
    """The revision D4 binds, or an unmatchable sentinel saying why there isn't one.

    Every sentinel is deliberately not 40 hex characters, so a record can never
    bind to one: while any part of the execution infrastructure is uncommitted
    or differs from its committed bytes, no authorization can match, and the
    repository cannot execute. That is the honest state today.
    """
    import hashlib

    absent, dirty = [], []
    for rel in paths:
        blob = _committed_blob(repo, revision, rel)
        if blob is None:
            absent.append(rel)
            continue
        disk = os.path.join(repo, rel.replace("/", os.sep))
        if not os.path.exists(disk):
            dirty.append(rel)
            continue
        with open(disk, "rb") as fh:
            live = fh.read().replace(b"\r\n", b"\n")
        if hashlib.sha256(live).hexdigest() != \
                hashlib.sha256(blob.replace(b"\r\n", b"\n")).hexdigest():
            dirty.append(rel)
    if absent:
        return "%s:%s" % (UNCOMMITTED_INFRASTRUCTURE, ",".join(sorted(absent)))
    if dirty:
        return "%s:%s" % (DIRTY_INFRASTRUCTURE, ",".join(sorted(dirty)))
    try:
        rev = _git(repo, "rev-list", "-1", revision, "--",
                   *paths).decode().strip()
    except RuntimeError:
        return "%s:git-unavailable" % UNCOMMITTED_INFRASTRUCTURE
    return rev or ("%s:no-revision-touches-these-paths"
                   % UNCOMMITTED_INFRASTRUCTURE)


def repo_authorization_status(repo, relpath=LEDGER_RELPATH):
    """What the REAL repository would answer today. Read-only.

    Used by the safety tests to state `TARGET_EXECUTION_AUTHORIZED = NO` as a
    machine result rather than as a claim.
    """
    source = GitLedgerSource(repo, relpath)
    committed_text = source.committed_text()
    worktree_text = source.worktree_text()
    committed, c_problems = parse_ledger(committed_text) if committed_text \
        else ([], ["ledger is not in committed git state"])
    worktree, w_problems = parse_ledger(worktree_text) if worktree_text \
        else ([], ["ledger is absent from the working tree"])
    grants = [r for r in committed
              if r.get("record_type") == RECORD_TYPE_AUTHORIZATION]
    active = [g for g in grants
              if resolve(worktree or committed,
                         g["authorization_id"]).active]
    return {
        "ledger_path": relpath,
        "ledger_committed": committed_text is not None,
        "ledger_in_worktree": worktree_text is not None,
        "committed_problems": c_problems,
        "worktree_problems": w_problems,
        "committed_authorization_records": len(grants),
        "active_authorizations": len(active),
        "execution_infrastructure_revision":
            execution_infrastructure_revision(repo),
        "target_execution_authorized": bool(active),
    }
