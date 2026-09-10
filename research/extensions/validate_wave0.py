#!/usr/bin/env python3
"""Deterministic Wave-0 governance checks for TSMOM-EXT-001.

WHAT THIS IS. A static consistency checker for the Wave-0 governance runtime:
hashes, file presence, ledger shape, canonical vocabulary, and the presence of
the prohibitions the accepted V2 architecture requires. It reads bytes and
compares them.

WHAT THIS IS NOT. It runs no strategy logic. It computes no return, no Sharpe,
no drawdown, no comparison, no optimisation, and it opens no protected data. It
imports nothing from `src/`. If a future edit makes that untrue, the edit is
wrong, not this comment.

AUTHORITY FOR THE LEDGER. `qros_runtime.exposure.parse_ledger` is the canonical
parser and **this module defers to it**: when it is importable its result is
authoritative and the local implementation runs only as a cross-check that must
agree. A local-only verdict is never accepted silently — if the canonical parser
cannot be reached, the run FAILS with a remediation message rather than reporting
a PASS it cannot back. `qros check` remains the authoritative validator for
`qros-state.yaml`.

STRUCTURE, and why. Every governance rule below is a **pure function over text**,
separated from the file-reading checks that apply it. That separation is what
lets the fixture suite in `FIXTURES` feed each rule known-good and known-bad
inputs and assert the verdict. A rule that cannot be handed a hostile input
cannot be shown to work; the previous revision of this file was structured that
way and passed 61 checks while accepting five classes of invalid fixture.

REPAIR HISTORY. Rewritten at the bounded Wave-0 repair after a fresh GPT-6 Astra
verifier reproduced `61 checks / 0 failures` and then demonstrated invalid
fixtures that still passed: B3a affirmative forbidden-token use ("No objection to
FULL-lite" read as a denial because it starts with "No"); B3b reviewer events
counted by `startswith("| S")`, which counted a later table's header and passed
with zero real event rows; B3c weakest-tier inheritance detected by searching for
the words "weakest-tier"; B3d correlation-consolidation detected the same way;
B3e an empty `EXPLICIT_MAP` accepted that the canonical parser rejects.

Usage:  python research/extensions/validate_wave0.py
Exit:   0 = every check and every fixture passed · 1 = at least one FAIL

Standard library only.
"""

import hashlib
import os
import re
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
WORKSPACE = os.path.dirname(REPO)

# The accepted V2 architecture, pinned to the bytes Aaron authorised Wave 0
# against. A mismatch means Wave 0 is being run against different architecture
# bytes, which is a STOP condition, not a warning.
V2_PINS = {
    "research/extensions/TSMOM_EXTENSION_RESEARCH_MAP_v2.md":
        "e9555a0220b58fdf6dfaee40613c5b28b114ea02b2a94137b1a23c56a87dbace",
    "research/extensions/TSMOM_EXTENSION_RESEARCH_PROGRAM_v2.md":
        "e9555f561e302c4f937a05829bd23b2368c79765b4c275b788f8fe14264d46c2",
    "research/extensions/idea_registry/IDEA_REGISTRY_v2.csv":
        "7e3024edd1e553745c75f83f3f107df84d2814ae06be4876f53aae117108717c",
    "research/extensions/DASHBOARD_v2.md":
        "951801bcea0281811b501ca19f63b26a3f3e488ef7cd4ca28a1f6641bf5e19b7",
    "research/extensions/review_history/ASTRA_ROUND2_CONVERGENCE_2026-09-08.md":
        "0a89d43919813eee302863eb642571347370e374c7966c9a81303dc9e0579869",
}

# The governance records. `validate_wave0.py` is deliberately NOT in this list:
# it is the checker, not a governance record, and its own fixture strings
# contain the very tokens the scans forbid.
WAVE0_ARTIFACTS = (
    "qros-state.yaml",
    "ops/EXPOSURE_LEDGER.md",
    "ops/REVIEWER_EXPOSURE_LOG.md",
    "research/extensions/SAMPLE_REUSE.md",
    "research/extensions/TRIAL_LEDGER.md",
    "research/extensions/LOCKBOX_PROCEDURE.md",
    "research/extensions/DATA_INVENTORY_SPEC.md",
    "research/extensions/WAVE0_VERIFICATION_RECORD.md",
)

# L6 spec section 10.1, fixed. The runtime parses the FIRST markdown table in
# the ledger as this one, so the ledger must contain exactly one table.
LEDGER_COLUMNS = ("ts", "scope", "classification", "granularity",
                  "artifact_or_pointer", "note")
EXPOSURE_CLASSES = {"NO_OUTCOME", "GENERATED_NOT_SEEN",
                    "REVEALED_AGGREGATE", "REVEALED_TARGET_METRIC"}
EXPOSURE_SCOPES = {"HISTORICAL_CUMULATIVE", "CURRENT_REVIEW_SCOPE"}
CONTRIBUTION = {"NO_OUTCOME": 0, "GENERATED_NOT_SEEN": 0,
                "REVEALED_AGGREGATE": 1, "REVEALED_TARGET_METRIC": 2}
AXIS_ORDER = ("NONE", "AGGREGATE", "TARGET_METRIC")

RULE_COLUMN_CANONICAL = "CLASSIFICATION_COLUMN_IS_CANONICAL"
RULE_EXPLICIT_MAP = "EXPLICIT_MAP"

# Character-for-character the canonical patterns (qros_runtime/exposure.py
# lines 73-75). Copied rather than re-derived so the local cross-check cannot
# drift into a different dialect.
_RULE_LINE = re.compile(r"^NORMALIZATION_RULE:\s*(?P<rule>[A-Z_]+)\s*$")
_MAP_LINE = re.compile(r"^(?P<token>[^->|]+?)\s*->\s*(?P<cls>[A-Z_]+)\s*$")
_SEPARATOR = re.compile(r"^\|[\s:|-]+\|$")

# S1-S6 existed at Wave-0 execution and the log is append-only, so the count can
# only grow. A floor catches the B3b scenario -- every real event row deleted
# while a stray table header keeps the checker green.
MIN_SEAT_EVENTS = 6

results = []
fixture_results = []


def check(name, ok, detail="", bucket=None):
    (fixture_results if bucket == "fixture" else results).append(
        (name, bool(ok), detail))
    return bool(ok)


def read(relpath, binary=False):
    path = os.path.join(REPO, relpath)
    mode = "rb" if binary else "r"
    kwargs = {} if binary else {"encoding": "utf-8"}
    with open(path, mode, **kwargs) as fh:
        return fh.read()


def sha256(relpath):
    return hashlib.sha256(read(relpath, binary=True)).hexdigest()


def exists(relpath):
    return os.path.isfile(os.path.join(REPO, relpath))


# ==========================================================================
# RULES — pure functions over text. Each is exercised by FIXTURES below.
# ==========================================================================

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+|\n")

# Markup and determiners that may sit between a negator and the token it
# negates without breaking the negation. Anything else -- a content word, a
# preposition -- means the negation attaches to something other than the token.
_ADJACENT = re.compile(
    r"^[\s`*_\"'‘’“”(\[-]*"
    r"(?:such\s+)?(?:a\s+|an\s+|the\s+)?"
    r"[\s`*_\"'‘’“”(\[-]*$")

_NEGATOR = re.compile(r"(?i)\b(?:no|not|never|neither|nor)\b")

# If any of these appears in the same sentence, the sentence is accepting or
# permitting the construct, whatever negator it happens to contain. This is the
# second, independent trap: B3a's "No objection to X" is caught by adjacency AND
# by "objection".
_ACCEPTANCE = re.compile(
    r"(?i)\b(?:objection|objections|acceptable|acceptance|allowed|allowable|"
    r"permitted|permissible|approve[sd]?|approval|endorse[sd]?|sanctioned|"
    r"fine\s+with|ok\s+with|okay\s+with|we\s+(?:may|can|will|should)\s+use|"
    r"may\s+be\s+used|is\s+adopted|are\s+adopted|adopt\s+the)\b")


def sentences(text):
    return [s.strip() for s in _SENTENCE_SPLIT.split(text) if s.strip()]


def uses_forbidden_token(text, token):
    """True when `token` appears somewhere that is not a denial of it.

    An occurrence counts as a DENIAL only when BOTH hold:
      1. a negator (`no`/`not`/`never`/`neither`/`nor`) sits immediately before
         it, with nothing between them but markup, quotes and at most one
         determiner; and
      2. the sentence carries no acceptance marker.

    Condition 1 is what separates "there is no `X` value" (the negation attaches
    to the token) from "No objection to X" (it attaches to "objection"). The
    previous revision used proximity alone and read the second as a denial --
    finding B3a.
    """
    for m in re.finditer(re.escape(token), text):
        window = text[max(0, m.start() - 60):m.start()]
        negators = list(_NEGATOR.finditer(window))
        adjacent = bool(negators) and bool(
            _ADJACENT.match(window[negators[-1].end():]))
        if not adjacent:
            return True
        # Second trap: the sentence this occurrence sits in.
        start = text.rfind("\n", 0, m.start()) + 1
        for delim in (". ", "! ", "? "):
            cut = text.rfind(delim, start, m.start())
            if cut != -1:
                start = max(start, cut + len(delim))
        end = len(text)
        for delim in (".", "!", "?", "\n"):
            cut = text.find(delim, m.end())
            if cut != -1:
                end = min(end, cut + 1)
        if _ACCEPTANCE.search(text[start:end]):
            return True
    return False


_SEAT_HEADER_SIGNATURE = ("#", "ts", "seat")
_SEAT_ID = re.compile(r"^\**\s*(S\d+)\s*\**$")


def seat_event_ids(text):
    """Ids of the ACTUAL reviewer-event records, ignoring headers.

    Repairs B3b. The previous revision counted any line starting `| S`, which
    matched section 4's `| Seat | Status ... |` header and therefore reported 7
    where 6 existed -- and would have reported a passing count with every real
    event row deleted.

    The event table is identified by its header signature, not by position, and
    only rows of that table whose first cell is an `S<n>` id are counted.
    """
    ids, in_event_table, header_seen = [], False, False
    for raw in text.split("\n"):
        stripped = raw.strip()
        if not (stripped.startswith("|") and stripped.endswith("|")):
            if stripped:
                in_event_table = False if header_seen else in_event_table
            continue
        if _SEPARATOR.match(stripped):
            continue
        cells = [c.strip().strip("`*").lower()
                 for c in stripped[1:-1].split("|")]
        if all(sig in cells for sig in _SEAT_HEADER_SIGNATURE):
            in_event_table, header_seen = True, True
            continue
        if not in_event_table:
            continue
        m = _SEAT_ID.match(stripped[1:-1].split("|")[0].strip())
        if m:
            ids.append(m.group(1))
        else:
            # A row in the event table that is not an event ends it.
            in_event_table = False
    return ids


_NEGATED_SENTENCE = re.compile(
    r"(?i)\b(?:no|not|never|neither|nor|reject(?:s|ed)?|refus\w+|forbid\w*|"
    r"forbidden|prohibit\w*|barred|disallow\w*|must\s+not|cannot|can't|"
    r"is\s+not|are\s+not|does\s+not|do\s+not|explicitly\s+not)\b")

_WEAKEST_QUALIFIER = re.compile(
    r"(?i)\b(?:weakest|lowest|minimum|min|worst|least)\b")
_TIER_NOUN = re.compile(
    r"(?i)\b(?:tier|tiers|context|contexts|T0|exposure|sample|samples|"
    r"lineage|evidence|status|grade)\b")

# --------------------------------------------------------------------------
# B3c. The weakest-tier detector is POLARITY-AWARE, because the two ways of
# stating the forbidden rule carry opposite grammatical signs:
#
#   "evidence is CAPPED BY the weakest tier"      -- positive, asserts the cap
#   "evidence can NEVER EXCEED the weakest tier"  -- negated, asserts the SAME
#
# A sentence-wide "is there a negator?" test reads the second as a denial,
# which is exactly how the fresh-Astra counterexample
#   "Effective rule: a candidate can never exceed its weakest historical
#    evidence tier."
# passed the complete validator at exit 0 / 114 checks / 0 failures.
#
# So predicates are split into two families whose polarity is opposite, and
# negation is resolved LOCALLY to the predicate rather than over the sentence:
#   CAP family    -- negated => denies the cap;  bare => asserts it
#   EXCEED family -- negated => ASSERTS the cap; bare => denies it
# --------------------------------------------------------------------------

# Positive polarity ASSERTS a cap: the weakest tier binds the claim.
_CAP_PREDICATE = re.compile(
    r"(?i)(?:capp?(?:ed|s)?\b|ceiling|inherit(?:s|ed|ance)?\b|"
    r"limited\s+to|bounded\s+by|pinned\s+to|restricted\s+to|confined\s+to|"
    r"is\s+the\s+(?:minimum|lowest|weakest)|no\s+higher\s+than|"
    r"determined\s+by\s+the|governed\s+by\s+the)")

# Positive polarity DENIES a cap: the claim may rise above the weakest tier.
# Negated, these ASSERT it.
_EXCEED_PREDICATE = re.compile(
    r"(?i)(?:exceed\w*|rise\s+above|rises\s+above|go\s+beyond|goes\s+beyond|"
    r"surpass\w*|strengthen\w*|improve\s+(?:on|upon)|"
    r"be\s+stronger\s+than|climb\s+above)")

_NEGATOR_LOCAL = re.compile(
    r"(?i)(?:\bno\b|\bnot\b|\bnever\b|\bneither\b|\bnor\b|n't\b|"
    r"\bcannot\b|\bcan['’]t\b)")

# A frame that rejects the rule it then quotes. This is a general category --
# the same shape as the acceptance markers used for B3a -- not a string
# exception for any one sentence.
_REJECTION_FRAME = re.compile(
    r"(?i)(?:explicitly\s+not|not\s+adopted|never\s+adopted|"
    r"do(?:es)?\s+not\s+adopt|we\s+reject|is\s+rejected|are\s+rejected|"
    r"rejects?\b|is\s+(?:prohibited|forbidden|barred)|"
    r"are\s+(?:prohibited|forbidden|barred)|must\s+never\s+be\s+applied|"
    r"no\s+rule\s+of\s+the\s+form|any\s+rule\s+of\s+the\s+form|"
    r"there\s+is\s+no\b|and\s+none\s+is)")

ASSERTS_CAP = "ASSERTS_CAP"
DENIES_CAP = "DENIES_CAP"


def _negator_before(sentence, index, span=34):
    return bool(_NEGATOR_LOCAL.search(sentence[max(0, index - span):index]))


def _negator_near(sentence, start, end, before=34, after=26):
    return bool(_NEGATOR_LOCAL.search(
        sentence[max(0, start - before):end + after]))


def weakest_tier_verdict(sentence):
    """`ASSERTS_CAP`, `DENIES_CAP`, or None when the rule is not discussed."""
    if not (_WEAKEST_QUALIFIER.search(sentence)
            and _TIER_NOUN.search(sentence)):
        return None
    caps = list(_CAP_PREDICATE.finditer(sentence))
    exceeds = list(_EXCEED_PREDICATE.finditer(sentence))
    if not caps and not exceeds:
        return None
    first = min(m.start() for m in caps + exceeds)
    frame = _REJECTION_FRAME.search(sentence)
    if frame and frame.start() < first:
        # The sentence quotes the rule in order to reject it.
        return DENIES_CAP
    verdicts = []
    for m in caps:
        # "claim ceiling is NOT pinned to ..." puts the negator after the head
        # noun, so a cap predicate is tested on both sides.
        verdicts.append(DENIES_CAP
                        if _negator_near(sentence, m.start(), m.end())
                        else ASSERTS_CAP)
    for m in exceeds:
        # Polarity inverts here: a negated "exceed" IS the cap.
        verdicts.append(ASSERTS_CAP
                        if _negator_before(sentence, m.start())
                        else DENIES_CAP)
    return ASSERTS_CAP if ASSERTS_CAP in verdicts else DENIES_CAP

_CONSOLIDATION_VERB = re.compile(
    r"(?i)\b(?:eras\w+|merg\w+|consolidat\w+|delet\w+|remov\w+|collaps\w+|"
    r"dropp?\w*|combin\w+|re-?group\w*|de-?duplicat\w+|fold\w*\s+into)\b")
_ATTEMPT_NOUN = re.compile(
    r"(?i)\b(?:attempts?|variants?|trials?|configurations?|rows?)\b")
_CORRELATION_TRIGGER = re.compile(r"(?i)correlat\w+")


def _asserting_sentences(text, patterns):
    """Sentences matching EVERY pattern and carrying no negation/rejection.

    A rule is asserted only when it is stated affirmatively. A sentence that
    states the rule in order to forbid it -- which is what the Wave-0 artifacts
    do -- carries a negation marker and is not an assertion of it.
    """
    hits = []
    for sentence in sentences(text):
        if not all(p.search(sentence) for p in patterns):
            continue
        if _NEGATED_SENTENCE.search(sentence):
            continue
        hits.append(sentence)
    return hits


def asserts_weakest_tier_inheritance(text):
    """Sentences asserting that evidence is capped by the weakest prior tier.

    Repairs B3c in two passes of this file's history. The original revision
    searched for the literal phrase "no weakest-tier inheritance" and passed any
    document carrying the denial *and* an actual rule. The second used
    sentence-wide negation and read "can never exceed" as a denial. This one
    resolves polarity per predicate, via `weakest_tier_verdict`.
    """
    return [s for s in sentences(text)
            if weakest_tier_verdict(s) == ASSERTS_CAP]


def asserts_correlation_consolidation(text):
    """Sentences allowing attempts to be merged/erased on observed correlation.

    Repairs B3d, by the same reasoning as B3c.
    """
    return _asserting_sentences(
        text, (_CONSOLIDATION_VERB, _ATTEMPT_NOUN, _CORRELATION_TRIGGER))


def parse_ledger_local(text):
    """Local implementation of the section 10.1 ledger shape.

    A CROSS-CHECK, never the authority: `parse_ledger` below prefers the
    canonical parser and requires this one to agree with it. Repairs B3e by
    rejecting an `EXPLICIT_MAP` with no mapping lines, which the canonical
    parser rejects and the previous revision accepted.
    """
    rule, mapping, rows = None, {}, []
    header_seen, in_map = False, False
    for raw in text.split("\n"):
        stripped = raw.strip()
        if not stripped:
            in_map = False if rule != RULE_EXPLICIT_MAP else in_map
            continue
        if not header_seen:
            m = _RULE_LINE.match(stripped)
            if m:
                if rule is not None:
                    return None, {}, [], "two NORMALIZATION_RULE declarations"
                rule = m.group("rule")
                in_map = rule == RULE_EXPLICIT_MAP
                continue
            if in_map:
                m = _MAP_LINE.match(stripped)
                if m:
                    token = m.group("token").strip().strip("`")
                    if token in mapping:
                        return None, {}, [], ("duplicate normalization mapping "
                                              "for %r" % token)
                    mapping[token] = m.group("cls")
                    continue
        if stripped.startswith("|") and stripped.endswith("|"):
            if _SEPARATOR.match(stripped):
                continue
            cells = [c.strip() for c in stripped[1:-1].split("|")]
            if not header_seen:
                header_seen = True
                normalized = tuple(c.strip("`").lower() for c in cells)
                if normalized != LEDGER_COLUMNS:
                    return None, {}, [], ("header is %s, ratified is %s"
                                          % (" | ".join(normalized),
                                             " | ".join(LEDGER_COLUMNS)))
                continue
            if len(cells) != len(LEDGER_COLUMNS):
                return None, {}, [], ("a row carries %d cells, not %d — a "
                                      "second markdown table would do this"
                                      % (len(cells), len(LEDGER_COLUMNS)))
            rows.append(dict(zip(LEDGER_COLUMNS, cells)))
    if rule is None:
        return None, {}, [], "no NORMALIZATION_RULE declared in the header block"
    if rule not in (RULE_COLUMN_CANONICAL, RULE_EXPLICIT_MAP):
        return None, {}, [], "unrecognised NORMALIZATION_RULE %r" % rule
    if rule == RULE_EXPLICIT_MAP and not mapping:
        return None, {}, [], "EXPLICIT_MAP declared with no mapping lines"
    if not header_seen:
        return None, {}, [], "no event table"
    return rule, mapping, rows, None


def load_canonical_parser():
    """`qros_runtime.exposure.parse_ledger`, or None with the reason why."""
    runtime = os.path.join(WORKSPACE, "qros-runtime")
    if not os.path.isdir(runtime):
        return None, "qros-runtime not found at %s" % runtime
    if runtime not in sys.path:
        sys.path.insert(0, runtime)
    try:
        from qros_runtime import exposure as canonical      # noqa: PLC0415
    except Exception as exc:                                # noqa: BLE001
        return None, "import failed: %s" % exc
    return canonical.parse_ledger, ""


CANONICAL_PARSER, CANONICAL_WHY = load_canonical_parser()


def parse_ledger(text):
    """The authoritative parse: canonical when reachable, else local."""
    if CANONICAL_PARSER is not None:
        return CANONICAL_PARSER(text)
    return parse_ledger_local(text)


def parsers_agree(text):
    """(agree, detail) over rule, row count and ok-vs-problem."""
    if CANONICAL_PARSER is None:
        return None, CANONICAL_WHY
    c_rule, _c_map, c_rows, c_problem = CANONICAL_PARSER(text)
    l_rule, _l_map, l_rows, l_problem = parse_ledger_local(text)
    same = (c_rule == l_rule
            and len(c_rows) == len(l_rows)
            and (c_problem is None) == (l_problem is None))
    if same:
        return True, ""
    return False, ("canonical=(rule=%r rows=%d problem=%r) "
                   "local=(rule=%r rows=%d problem=%r)"
                   % (c_rule, len(c_rows), c_problem,
                      l_rule, len(l_rows), l_problem))


# ==========================================================================
# FIXTURES — the rules above, fed known-good and known-bad input.
# ==========================================================================

_GOOD_LEDGER = """
NORMALIZATION_RULE: CLASSIFICATION_COLUMN_IS_CANONICAL

| ts | scope | classification | granularity | artifact_or_pointer | note |
|---|---|---|---|---|---|
| 2026-01-01T00:00:00Z | CURRENT_REVIEW_SCOPE | NO_OUTCOME | NONE | a.md | n |
"""

_GOOD_EXPLICIT_MAP = """
NORMALIZATION_RULE: EXPLICIT_MAP
`local_token` -> NO_OUTCOME

| ts | scope | classification | granularity | artifact_or_pointer | note |
|---|---|---|---|---|---|
| 2026-01-01T00:00:00Z | CURRENT_REVIEW_SCOPE | local_token | NONE | a.md | n |
"""

_EMPTY_EXPLICIT_MAP = """
NORMALIZATION_RULE: EXPLICIT_MAP

| ts | scope | classification | granularity | artifact_or_pointer | note |
|---|---|---|---|---|---|
| 2026-01-01T00:00:00Z | CURRENT_REVIEW_SCOPE | NO_OUTCOME | NONE | a.md | n |
"""

_WRONG_HEADER_LEDGER = """
NORMALIZATION_RULE: CLASSIFICATION_COLUMN_IS_CANONICAL

| ts | scope | classification | sample | artifact_or_pointer | note |
|---|---|---|---|---|---|
| 2026-01-01T00:00:00Z | CURRENT_REVIEW_SCOPE | NO_OUTCOME | NONE | a.md | n |
"""

_SECOND_TABLE_LEDGER = _GOOD_LEDGER + """
| a | b | c |
|---|---|---|
| 1 | 2 | 3 |
"""

_SEAT_LOG_WITH_EVENTS = """
| # | ts | seat | window | consequence |
|---|---|---|---|---|
| S1 | UNKNOWN | Astra R1 | fresh | burned |
| S2 | UNKNOWN | Astra R2 | continuation | burned |

## Seat map

| Seat | Status |
|---|---|
| Astra | burned |
"""

# B3b's demonstrated fixture: every real event row deleted, the section-4 table
# left in place. The previous revision counted its header and passed.
_SEAT_LOG_NO_EVENTS = """
| # | ts | seat | window | consequence |
|---|---|---|---|---|

## Seat map

| Seat | Status |
|---|---|
| Astra | burned |
"""


def run_fixtures():
    def fx(name, ok, detail=""):
        check(name, ok, detail, bucket="fixture")

    # --- B3a: forbidden-token use vs denial ------------------------------
    fx("[+] legitimate denial is not a use: 'There is no `X` value'",
       not uses_forbidden_token(
           "There is **no `insufficient_evidence`** value.",
           "insufficient_evidence"))
    fx("[+] legitimate denial is not a use: 'No `X` value exists'",
       not uses_forbidden_token(
           "**No `insufficient_evidence` value exists** in the schema.",
           "insufficient_evidence"))
    fx("[+] legitimate denial is not a use: 'no `FULL-lite` lane'",
       not uses_forbidden_token(
           "There is no `FULL-lite` lane and none is introduced.",
           "FULL-lite"))
    fx("[-] REJECTS affirmative use behind a leading 'No': "
       "'No objection to FULL-lite'",
       uses_forbidden_token(
           "No objection to FULL-lite for cheap studies.", "FULL-lite"))
    fx("[-] REJECTS affirmative use: 'we may use insufficient_evidence'",
       uses_forbidden_token(
           "For unclear cases we may use insufficient_evidence.",
           "insufficient_evidence"))
    fx("[-] REJECTS bare affirmative use: 'status: insufficient_evidence'",
       uses_forbidden_token("status: insufficient_evidence",
                            "insufficient_evidence"))
    fx("[-] REJECTS 'No reason not to allow FULL-lite' "
       "(negator present, acceptance marker present)",
       uses_forbidden_token(
           "No reason not to allow FULL-lite here.", "FULL-lite"))

    # --- B3b: reviewer event counting ------------------------------------
    ids = seat_event_ids(_SEAT_LOG_WITH_EVENTS)
    fx("[+] counts real reviewer events and ignores a later table header",
       ids == ["S1", "S2"], "counted %r" % (ids,))
    empty = seat_event_ids(_SEAT_LOG_NO_EVENTS)
    fx("[-] REJECTS a seat log whose event rows were all deleted",
       empty == [], "counted %r" % (empty,))

    # --- B3c: weakest-tier inheritance, polarity-aware -------------------
    # The first negative fixture is the fresh-Astra counterexample, preserved
    # VERBATIM as a permanent regression. It is the sentence that passed the
    # complete validator at exit 0 / 114 checks / 0 failures.
    for label, sentence in (
            ("the verbatim Astra counterexample",
             "Effective rule: a candidate can never exceed its weakest "
             "historical evidence tier."),
            ("a cap phrased as 'cannot rise above'",
             "Later validation cannot rise above the weakest previous "
             "evidence tier."),
            ("a cap phrased as the weakest tier being the ceiling",
             "The weakest historical evidence tier is the ceiling for all "
             "later evidence."),
            ("a cap phrased as 'capped at'",
             "A candidate's evidence is capped at the weakest tier used "
             "anywhere in its design lineage."),
            ("a cap phrased as inheritance",
             "Each claim inherits the lowest evidence context of any sample "
             "in its history."),
            ("a cap phrased as 'may not exceed'",
             "Later evidence may not exceed the weakest prior tier."),
            ("a cap phrased as 'limited to'",
             "The claim grade is limited to the weakest historical exposure "
             "tier."),
    ):
        fx("[-] REJECTS %s" % label,
           bool(asserts_weakest_tier_inheritance(sentence)),
           "" if asserts_weakest_tier_inheritance(sentence)
           else "verdict=%r for %r" % (weakest_tier_verdict(sentence),
                                       sentence))

    for label, sentence in (
            ("'is not permanently capped by'",
             "A candidate is not permanently capped by its weakest "
             "historical evidence tier."),
            ("'Do not apply weakest-tier inheritance.'",
             "Do not apply weakest-tier inheritance."),
            ("disclosure plus later strengthening",
             "Historical exposure remains disclosed, but later independent "
             "evidence may strengthen the claim."),
            ("'ceiling is not pinned to the weakest context'",
             "A candidate's claim ceiling is not pinned to the weakest "
             "context in its history."),
            ("the standing Rule 2 denial",
             "Rule 2 — there is no weakest-tier inheritance, and none is "
             "implemented here."),
            ("a rule quoted inside an explicit rejection frame",
             "Explicitly not adopted: any rule of the form \"a candidate "
             "designed on an exposed sample can never exceed *status X*\", "
             "or \"a family's ceiling is the minimum over its members' "
             "contexts\"."),
            ("an affirmative permission to exceed the weakest tier",
             "Later independent evidence may exceed the weakest historical "
             "tier."),
    ):
        fx("[+] does not flag %s" % label,
           not asserts_weakest_tier_inheritance(sentence),
           "" if not asserts_weakest_tier_inheritance(sentence)
           else "verdict=%r for %r" % (weakest_tier_verdict(sentence),
                                       sentence))

    # --- B3d: post-result correlation consolidation ----------------------
    fx("[+] the standing prohibition is not an assertion",
       not asserts_correlation_consolidation(
           "Attempts are never erased, merged or re-grouped because their "
           "PnL turned out to be highly correlated."))
    fx("[+] the section 0B rule text is not an assertion",
       not asserts_correlation_consolidation(
           "Never deleted, merged or consolidated after observing PnL "
           "correlation or any outcome."))
    fx("[-] REJECTS a rule merging attempts on observed correlation",
       bool(asserts_correlation_consolidation(
           "Attempts whose PnL correlation exceeds 0.9 are merged into a "
           "single row.")))
    fx("[-] REJECTS a rule deleting attempts on observed correlation",
       bool(asserts_correlation_consolidation(
           "Highly correlated variants may be deleted from the register "
           "once the correlation is measured.")))

    # --- B3e: ledger parsing, aligned with the canonical parser ----------
    for label, text, should_parse in (
            ("valid CLASSIFICATION_COLUMN_IS_CANONICAL ledger",
             _GOOD_LEDGER, True),
            ("valid EXPLICIT_MAP ledger with a mapping line",
             _GOOD_EXPLICIT_MAP, True),
            ("EXPLICIT_MAP with no mapping lines", _EMPTY_EXPLICIT_MAP, False),
            ("ledger with a non-ratified header column",
             _WRONG_HEADER_LEDGER, False),
            ("ledger carrying a second markdown table",
             _SECOND_TABLE_LEDGER, False),
    ):
        _rule, _map, _rows, problem = parse_ledger(text)
        ok = (problem is None) == should_parse
        sign = "[+]" if should_parse else "[-]"
        verb = "accepts" if should_parse else "REJECTS"
        fx("%s %s %s" % (sign, verb, label), ok,
           "" if ok else "problem=%r, expected parse=%s"
                         % (problem, should_parse))
        agree, detail = parsers_agree(text)
        fx("    local parser agrees with canonical on: %s" % label,
           agree is True,
           detail if agree is not True else "")


# ==========================================================================
# CHECKS — the rules applied to the real artifacts.
# ==========================================================================

def check_v2_hashes():
    for relpath, expected in sorted(V2_PINS.items()):
        if not exists(relpath):
            check("V2 hash %s" % relpath, False, "MISSING")
            continue
        actual = sha256(relpath)
        check("V2 hash %s" % relpath, actual == expected,
              "" if actual == expected else "expected %s got %s"
              % (expected, actual))


def check_artifacts_present():
    for relpath in WAVE0_ARTIFACTS:
        check("artifact present %s" % relpath, exists(relpath),
              "" if exists(relpath) else "MISSING")


def parse_state():
    """A deliberately small reader for the runtime's YAML subset.

    It reads only what these checks need. `qros check` is the authoritative
    parser; this one exists so a failure here is independent of it.
    """
    text = read("qros-state.yaml")
    scalars, inputs = {}, []
    current, block = None, None
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if raw.startswith("  - id:"):
            current = {"id": raw.split(":", 1)[1].strip().strip('"')}
            inputs.append(current)
            continue
        if raw.startswith("    ") and current is not None and ":" in raw:
            k, v = raw.strip().split(":", 1)
            current[k.strip()] = v.strip().strip('"')
            continue
        if raw.startswith("  ") and ":" in raw and block:
            k, v = raw.strip().split(":", 1)
            scalars["%s.%s" % (block, k.strip())] = v.strip().strip('"')
            continue
        if not raw.startswith(" ") and ":" in raw:
            current = None
            k, v = raw.split(":", 1)
            v = v.strip()
            if v in ("", "[]", "{}"):
                block = k.strip()
                scalars[k.strip()] = v
            else:
                block = None
                scalars[k.strip()] = v.strip('"')
    return scalars, inputs


def check_statefile():
    try:
        scalars, inputs = parse_state()
    except Exception as exc:                                # noqa: BLE001
        check("qros-state.yaml parses", False, str(exc))
        return None

    check("qros-state.yaml parses", True)
    check("schema_version == 17", scalars.get("schema_version") == "17",
          scalars.get("schema_version", "<absent>"))
    check("research_id == TSMOM-EXT-001",
          scalars.get("research_id") == "TSMOM-EXT-001",
          scalars.get("research_id", "<absent>"))
    check("lane is a legal token",
          scalars.get("lane") in ("EXPLORATORY", "MEASUREMENT", "FULL"),
          scalars.get("lane", "<absent>"))
    check("workflow_stage is a legal token",
          scalars.get("workflow_stage") in tuple("ABCDEFGHIJKL") + ("A2",),
          scalars.get("workflow_stage", "<absent>"))
    check("measurement_materiality is a legal token",
          scalars.get("measurement_materiality")
          in ("ORDINARY", "MATERIAL", "UNKNOWN", "N_A"),
          scalars.get("measurement_materiality", "<absent>"))
    check("outcome_exposure.scope is a legal token",
          scalars.get("outcome_exposure.scope") in EXPOSURE_SCOPES,
          scalars.get("outcome_exposure.scope", "<absent>"))
    check("outcome_exposure.declared is a legal value",
          scalars.get("outcome_exposure.declared")
          in AXIS_ORDER + ("UNKNOWN",),
          scalars.get("outcome_exposure.declared", "<absent>"))
    check("trial_accounting.canonical_ref is present and resolves",
          exists(scalars.get("trial_accounting.canonical_ref", "")),
          scalars.get("trial_accounting.canonical_ref", "<absent>"))

    ids = set(entry["id"] for entry in inputs)
    check("inputs[] names the research-axis ledger (`exposure_record`)",
          "exposure_record" in ids)
    check("inputs[] names the seat-axis ledger (`reviewer_exposure_log`)",
          "reviewer_exposure_log" in ids)

    for entry in inputs:
        missing = [f for f in ("id", "path", "observed_revision",
                               "observed_sha256") if f not in entry]
        if missing:
            check("input %s has every required field" % entry.get("id"),
                  False, "missing %s" % ", ".join(missing))
            continue
        path = entry["path"]
        if not exists(path):
            check("input %s resolves" % entry["id"], False,
                  "no file at %s" % path)
            continue
        actual = sha256(path)
        check("input %s hash matches" % entry["id"],
              actual == entry["observed_sha256"],
              "" if actual == entry["observed_sha256"]
              else "declared %s, actual %s"
                   % (entry["observed_sha256"], actual))
    return scalars


def check_exposure_ledger():
    check("canonical ledger parser is reachable and is the authority",
          CANONICAL_PARSER is not None,
          "" if CANONICAL_PARSER is not None
          else "%s — a local-only verdict is not accepted; make qros-runtime "
               "importable before trusting this run" % CANONICAL_WHY)
    if not exists("ops/EXPOSURE_LEDGER.md"):
        check("exposure ledger parses", False, "MISSING")
        return None
    text = read("ops/EXPOSURE_LEDGER.md")
    rule, _mapping, rows, problem = parse_ledger(text)
    if problem:
        check("exposure ledger parses", False, problem)
        return None
    check("exposure ledger parses", True,
          "rule=%s rows=%d" % (rule, len(rows)))
    agree, detail = parsers_agree(text)
    check("local and canonical parsers agree on the real ledger",
          agree is True, detail if agree is not True else "")
    check("exposure ledger declares a recognised normalization rule",
          rule in (RULE_COLUMN_CANONICAL, RULE_EXPLICIT_MAP), rule)
    check("exposure ledger carries at least one row", len(rows) > 0,
          "%d rows" % len(rows))

    bad_cls = sorted(set(r["classification"].strip("`") for r in rows)
                     - EXPOSURE_CLASSES)
    check("every classification is a canonical TBL-EXPOSURE-CLASSES token",
          not bad_cls, ", ".join(bad_cls))
    bad_scope = sorted(set(r["scope"].strip("`") for r in rows)
                       - EXPOSURE_SCOPES)
    check("every scope is a canonical TBL-EXPOSURE-SCOPES token",
          not bad_scope, ", ".join(bad_scope))

    normalized = {}
    for scope in EXPOSURE_SCOPES:
        in_scope = [r for r in rows if r["scope"].strip("`") == scope]
        if not in_scope:
            normalized[scope] = "UNKNOWN"
            continue
        top = max(CONTRIBUTION[r["classification"].strip("`")]
                  for r in in_scope)
        normalized[scope] = AXIS_ORDER[top]
    return normalized


def check_exposure_agreement(scalars, normalized):
    if scalars is None or normalized is None:
        check("declared exposure agrees with the ledger", False,
              "one side did not parse")
        return
    scope = scalars.get("outcome_exposure.scope")
    declared = scalars.get("outcome_exposure.declared")
    actual = normalized.get(scope)
    check("declared exposure agrees with the ledger for the declared scope",
          declared == actual,
          "declared %s, ledger normalizes %s to %s" % (declared, scope, actual))


def check_reviewer_log():
    if not exists("ops/REVIEWER_EXPOSURE_LOG.md"):
        check("reviewer exposure log parses", False, "MISSING")
        return
    text = read("ops/REVIEWER_EXPOSURE_LOG.md")
    ids = seat_event_ids(text)
    check("reviewer log carries real seat event records",
          len(ids) >= MIN_SEAT_EVENTS,
          "%d events %s (floor %d; the log is append-only, so a drop is a "
          "deletion)" % (len(ids), ids, MIN_SEAT_EVENTS))
    check("seat event ids are unique", len(set(ids)) == len(ids),
          "duplicates: %s" % sorted(set(i for i in ids if ids.count(i) > 1)))
    check("reviewer log states that seat independence is not statistical "
          "independence",
          "never** empirical independence" in text
          or "never" in text and "statistical" in text.lower())
    check("reviewer log records the two-axis separation",
          "consumes no research degrees of freedom" in text)
    # B2: every row named by the errata index must exist as a real event row.
    cited = set(re.findall(r"\*\*(S\d+)\*\*", text)) & set(
        re.findall(r"S\d+", text))
    dangling = sorted(c for c in cited if c not in ids)
    check("every seat row cited in the errata index resolves to an event row",
          not dangling, "dangling: %s" % ", ".join(dangling))
    check("Astra Round 2 is recorded as a CONTINUATION, not a fresh session",
          "CONTINUATION" in text and "not a fresh independent reviewer session"
          in text)


def contains_all(relpath, needles):
    if not exists(relpath):
        return False, ["<file missing>"]
    text = read(relpath)
    missing = [n for n in needles if n not in text]
    return not missing, missing


def check_content_rules():
    ok, missing = contains_all(
        "research/extensions/TRIAL_LEDGER.md",
        ["EXPOSURE_EVENT", "VARIANT_ATTEMPT", "HYPOTHESIS_FAMILY",
         "GOVERNED_N_TRIALS_CONTRIBUTION"])
    check("TRIAL_LEDGER implements the four-object distinction", ok,
          "missing " + ", ".join(missing) if missing else "")

    ok, missing = contains_all(
        "research/extensions/TRIAL_LEDGER.md",
        ["No post-result correlation consolidation",
         "No post-hoc family merging",
         "No automatic `+1` per attempt",
         "No silent recomputation of frozen historical counts"])
    check("TRIAL_LEDGER states the four prohibitions explicitly", ok,
          "missing " + ", ".join(missing) if missing else "")

    ok, missing = contains_all(
        "research/extensions/TRIAL_LEDGER.md",
        ["N_trials = 14", "UNKNOWN_PENDING_AARON_DECISION", "D-ETF-COUNT"])
    check("TRIAL_LEDGER preserves the verified Databento count and records "
          "the ETF count as an open decision", ok,
          "missing " + ", ".join(missing) if missing else "")

    ok, missing = contains_all(
        "research/extensions/SAMPLE_REUSE.md",
        ["design lineage", "validation evidence",
         "no weakest-tier inheritance", "T0", "T1", "T2", "T3", "T4"])
    check("SAMPLE_REUSE separates lineage from evidence and rejects "
          "weakest-tier inheritance", ok,
          "missing " + ", ".join(missing) if missing else "")

    ok, missing = contains_all(
        "research/extensions/LOCKBOX_PROCEDURE.md",
        ["FROZEN HISTORICAL WORKING SNAPSHOT",
         "ACCRUED BUT PROTECTED HOLDOUT",
         "PROSPECTIVE FORWARD ACCRUAL",
         "never relabelled prospective"])
    check("LOCKBOX_PROCEDURE keeps the three states distinguishable", ok,
          "missing " + ", ".join(missing) if missing else "")

    ok, missing = contains_all(
        "research/extensions/DATA_INVENTORY_SPEC.md",
        ["SPECIFICATION ONLY — NOT EXECUTED",
         "not established as owned; inventory pending"])
    check("DATA_INVENTORY_SPEC is defined, not executed, and uses "
          "epistemically correct ownership language", ok,
          "missing " + ", ".join(missing) if missing else "")


def check_semantic_prohibitions():
    """B3c/B3d applied to the real artifacts, not just to fixtures."""
    for relpath in WAVE0_ARTIFACTS:
        if not exists(relpath):
            continue
        text = read(relpath)
        hits = asserts_weakest_tier_inheritance(text)
        check("no weakest-tier inheritance rule is asserted in %s" % relpath,
              not hits, hits[0][:160] if hits else "")
        hits = asserts_correlation_consolidation(text)
        check("no post-result correlation consolidation rule is asserted "
              "in %s" % relpath, not hits, hits[0][:160] if hits else "")


def check_lockbox_release_order():
    """B1: authorization must precede protected outcome access."""
    if not exists("research/extensions/LOCKBOX_PROCEDURE.md"):
        check("lockbox release order is authorization-first", False, "MISSING")
        return
    text = read("research/extensions/LOCKBOX_PROCEDURE.md")
    check("lockbox states the authorization-first principle",
          "AUTHORIZATION MUST PRECEDE PROTECTED OUTCOME ACCESS" in text)
    steps = re.findall(r"^(\d+)\.\s+\*\*(.+?)\*\*", text, re.M)
    auth = [int(n) for n, body in steps
            if re.search(r"(?i)aaron .{0,40}authoriz", body)]
    access = [int(n) for n, body in steps
              if re.search(r"(?i)access/release the protected|read the outcome",
                           body)]
    ok = bool(auth) and bool(access) and max(auth) < min(access)
    check("the authorization step precedes every protected-access step",
          ok, "authorization at step(s) %s, protected access at step(s) %s"
              % (auth or "<none found>", access or "<none found>"))


def check_trial_ledger_decision_storage():
    """NB1: the ETF decision must not be routed to `human_decisions[]`."""
    path = "research/extensions/TRIAL_LEDGER.md"
    if not exists(path):
        check("ETF-count decision storage is legal", False, "MISSING")
        return
    text = read(path)
    # The file may discuss `human_decisions[]` in order to rule it out; what it
    # must not do is direct the decision INTO it.
    directs = [s for s in sentences(text)
               if "human_decisions" in s
               and re.search(r"(?i)\b(?:append|record|write|store)\w*\b", s)
               and not _NEGATED_SENTENCE.search(s)]
    check("the ETF-count decision is NOT routed into `human_decisions[]`",
          not directs, directs[0][:200] if directs else "")
    check("the ETF-count decision names a legal durable mechanism instead",
          "trial_accounting.value_anchor" in text
          and "observed_sha256" in text
          and "authoritative record" in text)
    check("the canonical `human_decisions[].type` enum is quoted, not extended",
          "DORMANT_ENTER" in text and "REVIEW_ATTEMPT_EXCLUDED" in text
          and "no new type is to be invented" in text)
    check("`D-ETF-COUNT` is still undecided",
          "UNKNOWN_PENDING_AARON_DECISION" in text
          and "is NOT decided by this correction" in text)


def check_unknowns_preserved():
    text = read("research/extensions/WAVE0_VERIFICATION_RECORD.md")
    for token in ("UNKNOWN_PENDING_AUTHORITATIVE_VERIFICATION",
                  "UNKNOWN_PENDING_AARON_DECISION",
                  "not established as owned; inventory pending"):
        check("verification record preserves %s" % token, token in text)


def check_no_invented_vocabulary():
    offenders = {}
    for relpath in WAVE0_ARTIFACTS:
        if not exists(relpath):
            continue
        text = read(relpath)
        for token in ("insufficient_evidence", "FULL-lite", "FULL_LITE"):
            if uses_forbidden_token(text, token):
                offenders.setdefault(token, []).append(relpath)
        # Sol is the global routing file's Codex seat. Program v2 section 1
        # designates GPT-6 Astra for A2 and Stage I on this program; a Wave-0
        # artifact must not reintroduce Sol as an active reviewer.
        if re.search(r"\bSol\b", text):
            offenders.setdefault("Sol routing", []).append(relpath)
    check("no `insufficient_evidence` value is used",
          "insufficient_evidence" not in offenders,
          ", ".join(offenders.get("insufficient_evidence", [])))
    check("no `FULL-lite` lane is introduced",
          not (offenders.get("FULL-lite") or offenders.get("FULL_LITE")),
          ", ".join(offenders.get("FULL-lite", [])
                    + offenders.get("FULL_LITE", [])))
    check("no active Sol reviewer routing is reintroduced",
          "Sol routing" not in offenders,
          ", ".join(offenders.get("Sol routing", [])))


# Paths a Wave-0 artifact names as the OUTPUT of a task that Wave 0
# deliberately did not run. Their absence is the correct state; their presence
# would mean the task ran without its separate authorisation.
FUTURE_PATHS = {
    "research/extensions/DATA_INVENTORY.md":
        "output of the inventory task, which is defined but NOT executed "
        "(DATA_INVENTORY_SPEC.md section 4); running it needs a separate "
        "Aaron authorisation",
}


def check_cross_references():
    pattern = re.compile(r"`((?:ops|research)/[A-Za-z0-9_./-]+\.(?:md|py|csv))`")
    broken = []
    for relpath in WAVE0_ARTIFACTS:
        if not exists(relpath):
            continue
        for target in set(pattern.findall(read(relpath))):
            if target in FUTURE_PATHS:
                continue
            if not exists(target):
                broken.append("%s -> %s" % (relpath, target))
    check("every repo-relative cross-reference resolves", not broken,
          "; ".join(sorted(broken)))

    for target, reason in sorted(FUTURE_PATHS.items()):
        check("deferred output %s is absent, as it must be" % target,
              not exists(target),
              "" if not exists(target)
              else "PRESENT — the task that produces it (%s) was not "
                   "authorised" % reason)


# Every .py under research/extensions/ must be DECLARED here with the reason it
# is not extension strategy code. This is a REGISTRY, not a mute button: an
# undeclared module still fails the check, so adding code to the extension tree
# stays a deliberate, reviewable act.
#
# The invariant being protected is Program v2 rule 14: no extension STRATEGY is
# constructed. A module that generates signals, sizes positions, builds a
# portfolio or evaluates a candidate's deployment performance would violate it
# and must NOT be added here -- it needs a sealed contract and Aaron's separate
# strategy-build authorisation first.
DECLARED_EXTENSION_MODULES = {
    "research/extensions/x01/x01_target_construction.py":
        "X01 sealed target-construction layer for E / A1 / S1 / S2. Pure "
        "construction functions over EXPLICITLY SUPPLIED inputs: no "
        "module-level file read, no target data loaded on import, and no "
        "Sharpe, bootstrap, CI or crisis statistic anywhere in it",
    "research/extensions/x01/x01_construction_tests.py":
        "synthetic-only tests for the construction layer; hand-built price "
        "frames, settlement/OI panels and position books. Opens no frozen "
        "panel and produces no X01 outcome",
    "research/extensions/x01/x01_runner.py":
        "X01 execution manifest builder and preflight refusal gate. "
        "PRE-EXECUTION ONLY: it hashes bytes and compares pins, parses no "
        "price panel, and its `execute` subcommand refuses -- constructing "
        "E, F, A1, S1 or S2 needs a separate Aaron authorization",
    "research/extensions/x01/x01_contract_tests.py":
        "X01 sealed-contract tests on SYNTHETIC data only; asserts the "
        "sealed signal, cost-quantity, S1, S2, B, COVID and bootstrap "
        "contracts and the runner's refusal behaviour. Loads no target "
        "panel for a computation",
    "research/extensions/validate_wave0.py":
        "the Wave-0 governance checker itself",
    "research/extensions/diagnostics/run_edge_diagnostics.py":
        "X07/X45/X46 diagnostics on the frozen PUBLISHED baseline streams; "
        "decomposes an existing burned stream, constructs no candidate",
    "research/extensions/wave1/probe_databento.py":
        "Databento input verification; metadata, coverage and units only",
    "research/extensions/wave1/extract_settle_oi.py":
        "settlement / open-interest extraction; raw vendor inputs only. "
        "SUPERSEDED by extract_contracts_v2.py; its raw-symbol-keyed panels "
        "are INVALID and are retained only as implementation-error lineage",
    "research/extensions/wave1/run_x02a.py":
        "X02a mechanical accounting truth -- no signal, no position, no "
        "portfolio, no Sharpe. SUPERSEDED by run_x02a_v3.py; its output is "
        "INVALID (raw-symbol panels) and is retained only as "
        "implementation-error lineage",
    "research/extensions/wave1/run_x03_structural.py":
        "X03 pre-seal STRUCTURAL roll diagnostics; roll dates, counts, OI "
        "crossover timing and availability -- no return series, no PnL. "
        "SUPERSEDED by run_x03_structural_v2.py; its output is INVALID and is "
        "retained only as implementation-error lineage",
    "research/extensions/wave1/extract_contracts_v2.py":
        "corrected extraction on persistent contract keys "
        "(instrument_id + expiration date); raw vendor inputs only",
    "research/extensions/wave1/panel_sanity.py":
        "panel-sanity gate that must PASS before any accounting identity is "
        "believed; reads panels, computes no strategy quantity",
    "research/extensions/wave1/run_x02a_v2.py":
        "X02a v2 on persistent contract keys. SUPERSEDED by run_x02a_v3.py: "
        "its ledger was GROSS-ONLY and carried no cost legs (Fable B1). "
        "Retained as lineage",
    "research/extensions/wave1/run_x02a_v3.py":
        "X02a v3 COSTED accounting truth: gross and net ledger reconciliations "
        "reported separately, end-to-end cost regression, sign-agreement "
        "diagnostic -- no signal, no position, no portfolio, no Sharpe",
    "research/extensions/wave1/run_x03_structural_v3.py":
        "X03 v3 structural roll diagnostics on the AUTHORITATIVE carry "
        "fixed-calendar comparator -- no return series, no PnL, no selection",
    "research/extensions/wave1/run_x03_structural_v2.py":
        "X03 v2 structural roll diagnostics. SUPERSEDED by "
        "run_x03_structural_v3.py: its comparator was mis-described (calendar "
        "days, not sessions) and was not the carry-accepted rule (Fable §8). "
        "Retained as lineage",
}


def check_no_strategy_build():
    ext = os.path.join(REPO, "research", "extensions")
    py = []
    for root, _dirs, files in os.walk(ext):
        for name in files:
            if name.endswith(".py"):
                py.append(os.path.relpath(os.path.join(root, name),
                                          REPO).replace("\\", "/"))
    unexpected = sorted(set(py) - set(DECLARED_EXTENSION_MODULES))
    check("no undeclared extension module exists", not unexpected,
          "undeclared: " + ", ".join(unexpected) if unexpected else "")
    check("every declared extension module is present",
          all(exists(m) for m in DECLARED_EXTENSION_MODULES),
          ", ".join(m for m in DECLARED_EXTENSION_MODULES if not exists(m)))


def main():
    run_fixtures()

    check_v2_hashes()
    check_artifacts_present()
    scalars = check_statefile()
    normalized = check_exposure_ledger()
    check_exposure_agreement(scalars, normalized)
    check_reviewer_log()
    check_content_rules()
    check_semantic_prohibitions()
    check_lockbox_release_order()
    check_trial_ledger_decision_storage()
    check_unknowns_preserved()
    check_no_invented_vocabulary()
    check_cross_references()
    check_no_strategy_build()

    every = fixture_results + results
    width = max(len(name) for name, _ok, _d in every)
    failures = 0

    print("=" * 8 + " FIXTURES  ([+] must pass · [-] must be rejected) "
          + "=" * 8)
    for name, ok, detail in fixture_results:
        if not ok:
            failures += 1
        line = "%-4s %-*s" % ("PASS" if ok else "FAIL", width, name)
        print(line + ("  %s" % detail if detail else ""))

    print("\n" + "=" * 8 + " CHECKS " + "=" * 8)
    for name, ok, detail in results:
        if not ok:
            failures += 1
        line = "%-4s %-*s" % ("PASS" if ok else "FAIL", width, name)
        print(line + ("  %s" % detail if detail else ""))

    pos = [r for r in fixture_results if r[0].lstrip().startswith("[+]")]
    neg = [r for r in fixture_results if r[0].lstrip().startswith("[-]")]
    agr = [r for r in fixture_results if r[0].lstrip().startswith("local")]
    print("\nfixtures: %d (%d positive, %d negative, %d parser-agreement)"
          % (len(fixture_results), len(pos), len(neg), len(agr)))
    print("  positive passed : %d/%d" % (sum(1 for r in pos if r[1]), len(pos)))
    print("  negative rejected: %d/%d" % (sum(1 for r in neg if r[1]), len(neg)))
    print("checks  : %d" % len(results))
    print("TOTAL   : %d checks, %d failed" % (len(every), failures))
    print("CANONICAL_PARSER_CROSS_CHECK = %s"
          % ("ACTIVE" if CANONICAL_PARSER is not None
             else "UNAVAILABLE (%s)" % CANONICAL_WHY))
    print("WAVE_0_STATIC_VALIDATION = %s"
          % ("PASS" if failures == 0 else "FAIL"))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
