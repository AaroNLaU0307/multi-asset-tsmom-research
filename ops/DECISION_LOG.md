# DECISION_LOG — multi-asset TSMOM research

**Append-only**, under `QUANT_WORKFLOW_VNEXT.md` v2 §6 (a workspace-local file, not in
this repository).

**What goes here:** one row per grant decision, seal, reveal, verdict, disposition,
methodology change, or delegate/Owner decision. The builder is the only writer.
Delegate messages and relayed Owner messages are recorded **verbatim**, with the sender
session and the UTC recording time, before anyone acts on them. Rows are never edited;
a correction is a new row that cites the old one.

**What stays where it is:**
- Earlier decisions stay in `ops/OWNER_DECISION_RECORD_*.md`.
- `OWNER_DECISION_RECORD_PHASE_B.md` is hash-pinned in C-A's sealed identity, so it
  takes no appends.
- Grants and consumptions stay in `ops/EXECUTION_AUTHORIZATIONS.md`.

**Times:** `recorded` is UTC. Aaron's local date for all rows below is 2026-09-26.

**Delegate:** session "Louie Price Action 行为重建项目"
(`local_e86f12a0-ee97-4cf4-9187-9d44d25284f4`), Claude Fable 5.1.

**Direct confirmation:** every Owner item below was relayed by the delegate and then
**confirmed by Aaron directly in the Opus builder session** before this file was
written.

---

## DL-001 · recorded 2026-09-25T18:20Z · Aaron · workflow v2 activated

QUANT_WORKFLOW v2 is **ACTIVATED**, effective 2026-09-26, with no retroactivity.

- The activation record is
  `../Workspace Docs/workflow-evolution-2026-09-22/OWNER_ACTIVATION_2026-09-26.md`
  (workspace-local).
- Consequence here: gates that older records call "Owner-only" are now split.
  - Aaron keeps the irreversible, external and financial gates.
  - The delegate decides the rest (v2 §4).

## DL-002 · recorded 2026-09-25T18:20Z · Aaron (relayed, confirmed directly) · state cut

Verbatim:

> 2. TSMOM STATE CUT (delegated decision: approved). In multi-asset-tsmom-research, rewrite PROJECT_STATE.md to v2 §6: current state only, about one screen, LIVE_GRANTS, LIVE_OBLIGATIONS (C-A 2026-09-30 must appear), closed lineages reduced to one line plus a pointer to their closeout. No scientific content, verdict, count or Owner decision may change; closeouts and ledgers are untouched; the old file stays in git history. Run the link check. Commit locally with a message citing this decision. No push.

**Superseded in part by DL-008.** C-A is closed, so the state file shows
`LIVE_OBLIGATIONS = NONE`, not the 2026-09-30 obligation.

**Builder note: why an archive copy exists.** The pre-cut file declares itself the
authoritative home of the final X01 and Time-Series Value verdicts. It is therefore
preserved **byte-exact** as `PROJECT_STATE_ARCHIVE_2026-09-26.md`, sha256
`a2cae76f18c5ed678206cfb05673d48af1c29b4ae53a96e69ad2c761931db3c9`, and remains in git
history too. From now on, that archive is the verdict record for both lineages.

## DL-003 · recorded 2026-09-25T18:20Z · delegate · C-A (a) — WITHDRAWN by DL-008

Verbatim:

> (a) AUTHORIZED: build the live monthly_cycle branch and fix the scheduling boundary, classified under v2 §8 as IMPLEMENTATION_FIX restoring the sealed contract. Requirements: the due condition is a window, not an instant — due from decision month-end + 5 business days through the end of that business day (and reported OVERDUE, never silently skipped, until the cycle is recorded); use an exchange holiday calendar; tests for the boundary (before, on, after, holiday) and for the no-skip behaviour; a synthetic dry run demonstrating the 2026-09-30 → 2026-10-07 cycle end to end without touching real outcomes; a runbook entry giving the exact command Aaron runs on 2026-10-07 on his machine, plus the FRED DGS3MO fetch step. No outcome access, no reveal, no change to the sealed prereg text. Checkpoint and message the delegate when built; acceptance must land before 2026-10-07.

**Never acted on.** Nothing was built or fixed.

## DL-004 · recorded 2026-09-25T18:20Z · delegate · C-A (b) — WITHDRAWN by DL-008

Verbatim:

> (b) DECIDED: monthly locks need no per-run grant; CA-GOLIVE-0001 covers prospective accrual. The first live run still requires the mechanical preflight (key fingerprint, store, data identity) to pass; record the preflight output in the run record.

**Never acted on.**

## DL-005 · recorded 2026-09-25T18:20Z · delegate · C-A (c) — WITHDRAWN by DL-008

Verbatim:

> (c) DECIDED, classified METHODOLOGY_CHANGE before exposure (TERMINAL_REVEAL_AUTHORIZED = NO): missed-cycle rule — if a cycle is missed before any position has been locked, the prospective window start shifts to the next decision month-end and the shift is logged with the reason; after the first lock, the existing no-gap rule applies unchanged. Record it as a dated amendment file beside the prereg citing this decision; the sealed prereg bytes are not edited.

**Never acted on.** No amendment file was written.

## DL-006 · recorded 2026-09-25T18:20Z · delegate · C-A (d) — WITHDRAWN by DL-008

Verbatim:

> (d) CLARIFY, in your report: the sealed prereg is dated 2026-09-13 yet SB-3 (second-source rule for missing bars) is "OPEN in the prereg draft". State whether the sealed text leaves SB-3 open; if it does, propose the minimal default for the first cycle and I will decide.

**Never answered.** The question lapsed when C-A closed.

## DL-007 · recorded 2026-09-25T18:20Z · delegate · stale-line correction

Verbatim:

> (e) Also correct the stale "S3 RUN NOT AUTHORIZED / NOT LIVE" lines when you do the block-2 state cut, since PROJECT_STATE must carry the LIVE status and the 2026-10-07 obligation under LIVE_OBLIGATIONS.

This is resolved by DL-008: C-A is now one closed line, so there are no live lines left
to correct.

## DL-008 · recorded 2026-09-25T18:20Z · Aaron (relayed, confirmed directly) · C-A CLOSED_PRE_OUTCOME

Verbatim:

> OWNER DECISION 2026-09-26 (Aaron, relayed by the delegate; Aaron will confirm the repository writes directly in your session): the C-A prospective confirmation programme is CLOSED, disposition CLOSED_PRE_OUTCOME. N_scored = 0, no position ever generated, no outcome accessed, so nothing is lost and no rescue rule is needed. Consequences: BLOCK 4 is CANCELLED in full — do not build the live monthly cycle, do not fix the scheduler, do not write the missed-cycle amendment; decisions (a)–(d) sent earlier are withdrawn. Canonical TSMOM stays "SUPPORTED — NOT INDEPENDENTLY CONFIRMED". BLOCK 2 proceeds as instructed once Aaron approves the writes in your session, with these changes: log this closure in the decision log with the earlier decisions marked WITHDRAWN; in the rewritten PROJECT_STATE, C-A appears as one closed line with a pointer, LIVE_OBLIGATIONS = NONE, LIVE_GRANTS = NONE (CA-GOLIVE-0001 consumed and now void by closure); write a short C-A closeout file beside its records citing this decision; the sealed C-A prereg and OD-8/OD-9 records stay untouched. Then commit locally, no push, and report to the delegate.

The closeout is `research/extensions/ca/CA_CLOSEOUT.md`.

## DL-009 · recorded 2026-09-25T18:20Z · Aaron (relayed, confirmed directly) · standing research-mode authorization

**Effective** at the commit that introduces this file.

Verbatim text: `ops/MANDATE_2026-09-26_AGI_RESEARCH_MODE.md`, recorded unchanged. It
grants broad method autonomy under v2. It changes no gate:
- Owner-retained gates stay with Aaron.
- Delegated gates stay with the delegate.
- The builder never authorizes its own run, reveal or verdict.
