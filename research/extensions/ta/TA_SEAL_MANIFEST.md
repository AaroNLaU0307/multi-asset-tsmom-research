# CTA-EDGE-01-TA — S1 SEAL MANIFEST

```
LINEAGE                      = CTA-EDGE-01-TA
CONTRACT_ID                  = CTA-EDGE-01-TA-PREREG-01
SEAL_ACT                     = S1 DESIGN + PRE-SEAL REPAIR + CONDITIONAL SEAL, performed by
                               Claude Opus 5 (Main Agent / builder seat) under the programme
                               controller's CTA-EDGE-01-TA S1 authorisation of 2026-09-15,
                               which accepted S0 = PASS, confirmed M2 = +0.30 as an Owner
                               methodology decision, and mandated five pre-seal repairs
UTC_SEAL_TIMESTAMP           = 2026-09-14T17:16:13Z
SEAL_BRANCH                  = cta-edge/ta-auction-s1
BASE_COMMIT                  = 6b8208e64824c81aa4d5523449410c74fb485b0a
                               ("docs: programme handoff + retrospective for Phases A–D")
REPOSITORY_HEAD_BEFORE_SEAL  = 6b8208e64824c81aa4d5523449410c74fb485b0a   (= BASE_COMMIT;
                               worktree clean apart from the untracked accepted S0 artifact)
SEAL_COMMIT                  = recorded in the S1 return block and in PROJECT_STATE at S2
                               acceptance (a manifest cannot contain the hash of the commit
                               that contains it)
```

## Lineage base — stated in full, because the VRP lineage was re-sealed for getting this wrong

```
BRANCH CREATED FROM          = the controller's designated ACCEPTED HEAD, 6b8208e6
LOCAL main                   = d232d3361b23a9f64182c2ec8881284f0fc3b36e
origin/main                  = 04190ead6f2f669d201ee68ee3ec39b19e3316be  (ancestor of main)
main IS AN ANCESTOR OF HEAD  = YES
HEAD AHEAD OF main BY        = 13 commits — the complete TSMOM-VRP-01 S1→S4 arc, its
                               closure and diagnostic, the README corrections, and the
                               Phase A–D programme handoff
```

This base is **deliberate and instructed**: the controller directed that the new lineage
branch be cut from the current accepted HEAD, and that HEAD is the accepted programme state
including the accepted handoff. It is **not** the VRP defect, which was inheriting an
*unmerged, unrelated* C-D lineage. Nothing was merged, rebased, force-pushed or pushed; no
branch was deleted; `main` was not modified.

## Authoritative input hashes — recompute before use

| Input | Location | SHA256 |
|---|---|---|
| **Accepted S0 frame** (provenance, **never design authority**) | `research/extensions/ta/TA_S0_FRAME.md` | `eea466e49e1a1f29f4e33590bf1623d0123d71c59ae9c624c7a8f73cb95deb31` |
| Fable discovery map (design-contributor input) | workspace root `2026-09-15-cta-edge-discovery-r1-mechanism-feature-map-fable-01.md` | `02ca5f45fe41763e55a353090645c3b2a98b6dcf5fce572623ede604e569344a` |
| Owner decision record (TA-OD-1 … TA-OD-5) | `ops/OWNER_DECISION_RECORD_CTA_EDGE_01_TA.md` | `a6c2c6458004e65eeb924540d723c5e5db841c32f8cf8339f7bdebcbd5336fcd` |
| Official Treasury auction extract (git-ignored; 1,006,030 bytes; retrieved 2026-09-14T16:55:38Z; 2,373 rows) | `data/ta/ta_auctions_raw.json` | `e807f06647c420f22f7654186e076cf15cebac2a6be7de16d8d1a5fbbcaba552` |
| Frozen ETF panel (git-ignored; pinned by the programme) | `data/close_prices_raw.csv` | `3d2a7a56dbd92d4ff8138cfd894c87f5ac5ac088a11165db870673e0c05c3c31` |

```
OWNER_DECISIONS_HASH  = a6c2c6458004e65eeb924540d723c5e5db841c32f8cf8339f7bdebcbd5336fcd
OWNER_M2_CONFIRMATION = YES  (M2 = +0.30, fixed BEFORE any candidate outcome was accessed)
OWNER_VALUES_CHANGED  = NO
S0_ARTIFACT_MODIFIED  = NO
```

## S1 artifact hashes — working-copy bytes = git blob bytes

Every file below is LF-only on disk and is covered by `.gitattributes`
(`*.md`, `*.csv`, `*.py` → `text eol=lf`), so each SHA256 is both the working-copy and the
git-blob identity and reproduces from any checkout regardless of `core.autocrlf`.

| Artifact | SHA256 |
|---|---|
| **`TA_PREREGISTRATION.md`** — the sealed contract, sole design authority | `3b495fcb220a86b9c4226e308e4814bdfdd871d1c69ce352e99b78977436d35b` |
| `TA_S0_REPAIR_RECORD.md` — the S0 → S1 supersession record | `1030349c4bf777916a31d9e84801ee712337ae449ab1a891e8707bc5bc2cf7e3` |
| `TA_EVENT_CALENDAR.csv` — the sealed event calendar, 557 rows, dates and metadata only | `b27be5b1d94cfc13fc8310e0d5216675e097a2245fc954e4b12ed282563f7cb6` |
| `TA_DATA_MANIFEST.md` — sources, queries, timestamps, hashes | `0176c532852570953087f31f978a65d080f4e0fc7286fd5757f2034325434abc` |
| `TA_EXPOSURE_DISCLOSURE.md` — design-contributor and outcome-exposure disclosure | `b4b400e458f4a78fad7492713e126653a808580197bb7271ff4effbcb836d7de` |
| `ta_auction_fetch.py` — metadata fetch and event-calendar builder | `0b8caf588b1cd4777e8fc46de0b4b0fd7aabd9b210d7aa04ac7e30f7e89b0806` |
| `ta_prereg_validate.py` — mechanical validator (**RESULT: PASS, 122/122, exit 0**) | `75567df54b26b942f7fa59dca58afffdce031a03303c0d1e2df0aa1e0b975124` |
| `TA_SEAL_MANIFEST.md` — this file | recorded in the S1 return block (a file cannot contain its own hash) |

## Sealed seed protocol (constants only; no data)

`numpy.random.SeedSequence(7).spawn(5)[4]` — a new, previously unused child of the
programme's existing seed constant `7`; children 0…3 remain TSMOM-VRP-01's and are
untouched. That child's `.spawn(2)` gives `[0]` for the primary-grid bootstrap
(TLT, SPY, SHY) and `[1]` for the secondary (IEF). Each drives
`numpy.random.Generator(numpy.random.PCG64(child))`. `B = 10,000`, 95 % percentile.
The seed is a fixed constant of the programme and is derived from nothing.

## Boundaries sealed

```
FROZEN PANEL BOUNDARY   = 2026-06-12. Nothing after it is an observation, ever.
AUCTION RECORD CUTOFF   = 2026-06-12.
COMMON GRID             = 6,007 trading days, 2002-07-30 .. 2026-06-12, zero internal
                          gaps; TLT, IEF, SHY and SPY share an IDENTICAL date set.
PRIMARY CELL            = TLT / 30-Year. 213 valid complete windows,
                          2006-02-09 .. 2026-05-13, 21 calendar years,
                          213 unique ISO weeks, max 1 event per week AND per month,
                          ZERO overlapping windows (min consecutive gap 17 grid days),
                          73 original issues / 140 reopenings.
MONTH GRID (M2)         = 2006-02 .. 2026-05 = 244 months, of which 31 are zero months.
SECONDARY CELL          = IEF / 10-Year. 258 valid windows, 2002-08-07 .. 2026-05-12,
                          25 calendar years, exactly ONE overlapping pair
                          (2019-06-12 / 2019-06-21), both retained.
WINDOWS                 = PRE close(t0-6)->close(t0-1); POST close(t0)->close(t0+5);
                          the auction-day bar belongs to NEITHER.
POSITION PATH           = flat -> SHORT -> flat -> [FLAT across the auction-day bar]
                          -> LONG -> flat.  There is NO short-to-long flip.
COST                    = 4 one-way units x 2 bps = 8.0 bps per instrument per event.
M1                      = mean AC_NET >= +8.0 bps/event  (gross +16.0).
M2                      = calendarised annualised Sharpe >= +0.30  (Owner-confirmed).
TAXONOMY                = A / B / C / D / I, ordered, first match wins, verified
                          disjoint and exhaustive over a synthetic sweep.
```

## Prohibited outcome access — statement of record

At S1 and at this seal, for this lineage: **no** ETF event return, `AC`, leg return,
auction-day bar return, mean, interval, Sharpe, bootstrap replicate, P&L, portfolio
quantity or candidate statistic of any kind was computed, read, plotted or inferred; **no**
strategy engine, optimiser or backtest exists; **no** outcome artifact exists anywhere for
this lineage. The only contact with the frozen ETF panel was `trading_calendar()`, which
read the `Date` column and a **non-null presence mask** for TLT, IEF, SHY and SPY and
retained no numeric value — corroborated mechanically by the validator, which asserts that
the builder module contains no return, P&L or statistic computation. The protected C-A
store, key, position and return layers were **not** touched and no C-A quantity was
computed or inferred. Canonical TSMOM was not modified. Auction **outcome** fields
(yields, bid-to-cover, bidder allotments) were deliberately **not requested** from the
Treasury endpoint.

Data acquisition beyond the consumed TA-OD-5 metadata grant begins only after controller /
Aaron acceptance of this seal **and** a separate Owner data authorisation; any real run
needs a separate single-use Owner execution authorisation; any reveal a separate single-use
Owner reveal authorisation.

## Design-contributor disclosure — binding

- **Claude Fable 5.1** — `material_design_contributor` (the CTA edge-discovery round-1 map,
  the Treasury-auction candidate, the IEF/TLT mapping, the reduced-form event-window
  framing, the dealer-inventory secondary proposal). Never a blind certifier of this design
  or its results.
- **GPT-6 Astra** — `material_design_contributor` (the independent identification challenge
  that made the primary claim `REDUCED_FORM`, parked the dealer cell, and forced
  `CAUSAL_MECHANISM_EFFECTIVE_N` to be recorded separately). Never a blind certifier of this
  design or its results. **Provenance gap recorded:** no Astra artifact is persisted in this
  workspace; the contribution reached the S0 session only through the controller's brief.
- **Claude Opus 5** — the producing seat for the S0 frame, this contract, the builder and
  the validator. It **must not certify them**.
- **ChatGPT (Aaron-side)** — programme controller / acceptance checker.
- **Aaron** — Owner; every gate after this seal is Aaron's.
- Canonical TSMOM remains FROZEN; C-A remains LIVE / S3 passive accrual, untouched; C-D
  remains at HOLD; TSMOM-VRP-01, Value, X01, XSMOM and the four overlays remain CLOSED.
  Nothing in this package upgrades any of them.

Seat-axis records: `ops/REVIEWER_EXPOSURE_LOG.md` rows **S31** (Fable), **S32** (Astra),
**S33** (the producing seat).

## Pre-seal checks performed

1. **Repository state verified mechanically**: branch, HEAD, worktree and the
   `main` → HEAD ancestry, all read from git and recorded above.
2. **Data identity**: the raw extract and the frozen panel reproduce their pinned SHA256;
   the event calendar **rebuilds from the pinned raw bytes to `b27be5b1…7cb6` exactly**.
3. **Structural assertions**: the common-grid identity across TLT/IEF/SHY/SPY; 213 primary
   valid windows; 0 primary overlaps; max 1 primary event per calendar month; 244-month
   grid with 31 zero months; 21 primary calendar years; 258 secondary valid windows; the
   on-cycle rule is a no-op on the primary family.
4. **Adversarial pre-seal inspection** (contract §T.3, ten questions, every answer NO):
   no undefined threshold; no unbound choice point; no contradictory rule; no impossible or
   overlapping verdict class; no hidden rescue path; no diagnostic that can promote; no
   post-result discretion; no wording that upgrades reduced-form to causal; **SHY retains no
   kill or damage power and does not appear anywhere in the classification section**; no
   short-to-long-flip wording; no ambiguous Sharpe annualisation; no outcome-selected sample
   rule.
5. **Classification function proved total, single-valued and unpromotable** over a synthetic
   sweep of the five interval bounds × the three diagnostic flags, with all five classes
   reachable and no flag combination able to move any class to `D`.
6. **`ta_prereg_validate.py` RESULT: PASS, 122 of 122 checks, exit 0.**

```
SEAL_AUTHORITY               = AUTHORITATIVE_PENDING_CONTROLLER_ACCEPTANCE
NEXT_AUTHORIZED_GATE         = CONTROLLER / AARON S1 ACCEPTANCE -> S2 BUILD
S2_AUTHORIZED                = NO
DATA_ACQUISITION_AUTHORIZED  = NO
REAL_RUN_AUTHORIZED          = NO
RUN_AUTHORIZATION_CREATED    = NO
REVEAL_AUTHORIZED            = NO
NOTHING_PUSHED               = YES
MAIN_MODIFIED                = NO
```

*Any receiver recomputes every hash above before use; chat-carried bytes are never a source
of truth.*
