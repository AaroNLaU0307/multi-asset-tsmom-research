# -*- coding: utf-8 -*-
"""F6 S1 SEAL — atomic ledger + Owner-record append. Governance only."""
import hashlib, io, os, re

REPO = r"C:\Users\Aaron\OneDrive\Desktop\Quant trade\multi-asset-tsmom-research"
os.chdir(REPO)
LEDGER = "research/extensions/TRIAL_LEDGER.md"
OWNER = "ops/OWNER_DECISION_RECORD_CTA_EDGE_05_F6.md"

PREREG = "research/extensions/f6/F6_S1_PREREGISTRATION_SEALED.md"
PREREG_SHA = hashlib.sha256(open(PREREG, "rb").read()).hexdigest()

ROW = (
 "| 5 | **`F-F6`** | `research/extensions/f6/F6_S1_PREREGISTRATION_SEALED.md` "
 "§9/§10/§12, sealed 2026-09-21 (SHA256 `%s`), `SEAL_ID = "
 "CTA-EDGE-05-F6-S1-2026-09-21`; appended here **at the seal, before any "
 "member has run** | **F6-PRIMARY** — the CTA-EDGE-05 / F6 pooled "
 "scheduled-announcement-day SPY rule judged through the sealed P1 + P2 + P3 "
 "conjunction on the 462 archive-eligible event sessions (the ONE primary "
 "member, m = 1) · **F6-DIAG** — per-family FOMC / CPI / NFP summaries, "
 "permitted only where already adopted by Owner authority, all "
 "`PROMOTION_POWER = NONE` and `RESCUE_POWER = NONE` | **m = 1; NO "
 "multiplicity correction**, because no selection across cells occurs — the "
 "verdict is read off the single designated P1/P2/P3 conjunction via the "
 "sealed §12 terminal table. **No automatic +1 per attempt.** P3 is a "
 "leave-one-calendar-year veto on the SAME lineage, not another shot on goal, "
 "and spends no separate trial; diagnostics are not attempts and never enter "
 "`N_trials`. TLT, F6.b, F6.c and 2026 are excluded from outcome computation "
 "entirely and constitute no members | **NOTHING HAS RUN. `F6_FAMILY_STATUS = "
 "SEALED / NOT EXECUTED`.** `F6_PRIMARY_TRIAL_SPENT = NO`. No P1 mean, no "
 "`beta_EVENT`, no interval, no bootstrap statistic, no LOYO quantity and no "
 "result artifact exists; the seal transaction was outcome-blind and read no "
 "SPY price value. Bootstrap frozen pre-outcome at B = 100,000 over 15 "
 "calendar-year blocks 2011–2025, seed **2540719150** derived from "
 "`SHA256(\"CTA-EDGE-05|F6|S1_BOOTSTRAP|\" + FINAL_EVENT_MANIFEST_SHA256)` — "
 "metadata, never returns. `SAMPLE_REUSE_CLASS = T0_REUSED_DEPENDENT`, "
 "`EVIDENCE_CEILING = SUPPORTED`, `INDEPENDENT_CONFIRMATION = NO`. `N_trials` "
 "on the ETF panel is still **NOT ASSERTED** — `D-ETF-COUNT` stays "
 "`UNKNOWN_PENDING_AARON_DECISION`, and the sealed design uses no DSR and no "
 "trial-count deflation |") % PREREG_SHA

NOTE = """
**Appended 2026-09-21 (CTA-EDGE-05 / F6 S1 seal) — ON TIME, at the seal.** `F-F6` is the
programme's **fifth** declared family, and it is declared on exactly the condition the
register states: a **sealed** preregistration, appended **before its first member runs**.
Unlike `F-MMV`, this row is **not** a late transcription — it is written as part of the same
atomic seal transaction that created the sealed contract, which is why no disclosure of a
transcription delay is needed here.

The declaring authority is the sealed preregistration at the hash in the row above, not this
row. A reader who doubts the membership, the `m = 1` treatment or the frozen bootstrap
settings should verify that file against its pinned SHA256 rather than take this row's word
for it.

The BH-FDR standing default below is **not** applied to `F-F6`, which has `m = 1` and no
selection across cells. No existing row or paragraph was edited, deleted or reordered.
"""

src = io.open(LEDGER, encoding="utf-8", newline="").read()
assert "`F-F6`" not in src, "F-F6 already present; refusing to double-append"
lines = src.split("\n")

# anchor: the LAST existing family row, so the table stays contiguous
idx = [i for i, l in enumerate(lines) if l.startswith("| 4 | **`F-MMV`**")]
assert len(idx) == 1, "expected exactly one F-MMV row, got %d" % len(idx)
at = idx[0] + 1
lines.insert(at, ROW)

# the disclosure note goes after the existing F-MMV note paragraph
j = [i for i, l in enumerate(lines)
     if l.startswith("**Appended 2026-09-17 (CTA-EDGE-04-MMV S3 run)")]
assert len(j) == 1
lines.insert(j[0] + 1, NOTE)

out = "\n".join(lines)
assert out.count("`F-F6`") >= 1
io.open(LEDGER, "w", encoding="utf-8", newline="").write(out)
print("TRIAL_LEDGER: F-F6 row appended after F-MMV; rows now %d"
      % len([l for l in out.split("\n")
             if re.match(r"^\| \d+ \| \*\*`F-", l)]))
print("POST_SEAL_TRIAL_LEDGER_SHA256 %s"
      % hashlib.sha256(open(LEDGER, "rb").read()).hexdigest())

OWNER_APPEND = """
---

## §12 S1 SEAL — Owner authorization and execution

*Appended 2026-09-21. **Additive.** Nothing above this line is altered, no
decision is renumbered, and no prior history is rewritten.*

```
OWNER_SEAL_AUTHORIZATION = YES
AUTHORIZATION_LITERAL    = "seal"
AUTHORIZED_BY            = Aaron (Owner)
S1_SEAL_STATUS           = SEALED
SEAL_ID                  = CTA-EDGE-05-F6-S1-2026-09-21
SEAL_DATE                = 2026-09-21
```

```
SEALED CONTRACT  ../research/extensions/f6/F6_S1_PREREGISTRATION_SEALED.md
                 sha256 %s
```

### §12.1 Three sources, never collapsed

```
FABLE          constructive design advice        OD-1 · OD-2 · OD-TY / OD-CASH
ASTRA          independent adversarial review    PASS,
               B_READY_FOR_S1_SEAL_WITH_CLAIM_CAP_NARROWING,
               sha256 23f723ed…ab589
               S1_SEAL_AUTHORIZED_BY_THIS_REVIEW = NO
AARON (OWNER)  adoption, and the SOLE seal authorization ("seal")
```

Advice is not review. Review is not authorization. **The independent review
expressly declined to authorize the seal**; only Aaron's explicit `"seal"` did.
These three remain three separate sources with three different authorities and
must never be presented as one.

### §12.2 What the seal did and did not change

```
SCIENTIFIC DESIGN CHANGED AT SEAL = NO
```

Instrument, SPY-only status, event families, pooled architecture, event
manifest, the 462-event sample, the 2011–2025 window, the 2026 exclusion,
entry, exit, position size, cost, cash proxy, the `/365` convention, P1, P2,
P3, terminal classification, bootstrap blocks, `B`, seed, quantile
implementation, TOM, AUCTION, the PIT exclusions, LOYO semantics and the claim
cap are all **unchanged**.

One parameterization was canonicalized, and it is not a design change:

```
WEEKDAY_REFERENCE = FRIDAY, with Monday/Tuesday/Wednesday/Thursday indicators
and an intercept.
```

OD-2's prose described the same control space with Monday as reference **and in
the same sentence recorded that δ is invariant to the choice of reference** —
which is correct, since `beta_EVENT` is numerically identical whichever weekday
is omitted from a full set alongside an intercept. The sealed contract carries
the Friday reference only. **OD-2 is historical and is not rewritten**; it keeps
its bytes and its pinned hash.

### §12.3 Accounting at seal

```
TRIAL_LEDGER_CHANGED          = YES   exactly one prospective family row, F-F6
F6_FAMILY_STATUS              = SEALED / NOT EXECUTED
F6_PRIMARY_TRIAL_CONSUMED     = NO
EXPOSURE_LEDGER_CHANGED       = NO
F6_PERFORMANCE_EXPOSURE_ADDED = NO
```

No exposure row was created because no F6 return or target measurement has been
revealed, and no new exposure type was invented to accommodate a seal.

### §12.4 Evidence is not upgraded by sealing

```
SAMPLE_REUSE_CLASS       = T0_REUSED_DEPENDENT
EVIDENCE_CEILING         = SUPPORTED
INDEPENDENT_CONFIRMATION = NO
```

### §12.5 Post-seal authorization state

```
S1                       = SEALED
S2_BUILD_AUTHORIZED      = YES
S3_RUN_AUTHORIZED        = NO
RETURN_REVEAL_AUTHORIZED = NO
```

S2 authorizes code and build work **only**. The historical run stays forbidden
until S2 implementation is complete, implementation acceptance passes, and a
**separate** S3 run authorization is issued by Aaron.

```
seal record     ../research/extensions/f6/F6_S1_SEAL_RECORD.md
sealed manifest ../research/extensions/f6/F6_S1_SEALED_MANIFEST.json
```
""" % PREREG_SHA

with io.open(OWNER, "a", encoding="utf-8", newline="") as fh:
    fh.write(OWNER_APPEND)
print("OWNER_RECORD_SHA256 %s"
      % hashlib.sha256(open(OWNER, "rb").read()).hexdigest())
print("SEALED_PREREGISTRATION_SHA256 %s" % PREREG_SHA)
