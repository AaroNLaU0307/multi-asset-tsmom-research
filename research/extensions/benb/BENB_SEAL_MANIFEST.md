# CTA-EDGE-02-BENB — S1 SEAL MANIFEST

```
LINEAGE                      = CTA-EDGE-02-BENB
CONTRACT_ID                  = CTA-EDGE-02-BENB-PREREG-01
SEAL_ACT                     = S1 SEAL COMPLETION, performed by Claude Opus 5 (Main
                               Agent / builder seat) under the programme controller's
                               CTA-EDGE-02-BENB narrow seal-completion authorisation
                               and Aaron's Owner decision BENB-OD-1
UTC_SEAL_TIMESTAMP           = 2026-09-14T19:00:20Z
SEAL_BRANCH                  = cta-edge/bond-etf-nav-s0
BASE_COMMIT                  = 023326230d068e71ab28c0a1533e6a2354b9576c
                               ("ta: CTA-EDGE-01-TA CLOSED PRE-OUTCOME")
REPOSITORY_HEAD_BEFORE_SEAL  = 023326230d068e71ab28c0a1533e6a2354b9576c  (= BASE_COMMIT;
                               worktree clean apart from the untracked BENB artifacts)
SEAL_COMMIT                  = recorded in the S1 return block and in PROJECT_STATE at
                               S2 acceptance (a manifest cannot contain the hash of the
                               commit that contains it)
```

## Lineage base

```
BRANCH CREATED FROM          = the accepted programme HEAD after the CTA-EDGE-01-TA
                               pre-outcome closure
LOCAL main                   = d232d3361b23a9f64182c2ec8881284f0fc3b36e
main IS AN ANCESTOR OF HEAD  = YES
```

Nothing was merged, rebased, force-pushed or pushed; no branch was deleted; `main` was
not modified. The CTA-EDGE-01-TA package on this branch is untouched and its own
validator still passes.

## What this seal completes

The S1 design pass returned **HOLD on exactly one item**: the `M2` risk-adjusted
usefulness floor and its boundary operator, which the design pass established could
**not** be inherited from C-A, from CTA-EDGE-01-TA, or from any programme-wide
convention — because the programme has none. The Owner has now taken that decision.

```
BENB-OD-1   M2_METRIC            = calendarised annualised Sharpe of the sealed
                                   fixed-unit, discount-only HYG sleeve
            MONTHLY_CONSTRUCTION = sum NET_TRADE_RETURN by ENTRY calendar month
            ZERO_SIGNAL_MONTH    = exactly 0        RISK_FREE_RATE = 0
            ANNUALISATION        = sqrt(12)
            M2_VALUE             = +0.30
            M2_BOUNDARY_OPERATOR = STRICT  >
            PASS CONDITION       = lower endpoint of the 95 % bootstrap interval for the
                                   calendarised annualised Sharpe STRICTLY > +0.30
            DECIDED BEFORE       = any basis, discount-sign count, regression, return
                                   outcome or backtest existed for this lineage
            INHERITED            = NO. BENB-specific.
```

**No other sealed value changed.** M1, the cost, the horizon, the sample, the estimand,
the diagnostics, the inference, the fragility rule and the classification structure are
byte-identical in substance to the design the controller accepted.

## Authoritative input hashes — recompute before use

| Input | Location | SHA256 |
|---|---|---|
| **S0 frame** (accepted direction; provenance, never design authority on a superseded point) | `research/extensions/benb/BENB_S0_FRAME.md` | `5dabf6fc8af3b1c7455db72b468537428b9ca11d0188c68481e5c96b97a03b73` |
| **S0 data/design repair record** (binding) | `research/extensions/benb/BENB_S0_REPAIR_RECORD.md` | `a4d81db3cc159f193a6aafdb3b5e5a263d138b3e307a1f7c54b1def456d0898b` |
| **Owner decision record** (BENB-OD-1) | `ops/OWNER_DECISION_RECORD_CTA_EDGE_02_BENB.md` | `63a3da1b79fad18486139950c7845bee20951b2dd2ec87f8dd446da07162d943` |

Both S0 artifacts are preserved **byte-for-byte** and were not rewritten at any point.

## Pinned data — acquired under the S0 data authorisation, not re-fetched

`data/benb/` is git-ignored under the repository's blanket `data/` policy. The
BlackRock workbook additionally carries an explicit licence restriction (*"solely for
your personal, non-commercial use … you may not copy, distribute, modify, post, frame
or deep link this content"*), which that policy already satisfies.

| file | bytes | SHA256 |
|---|---:|---|
| `ishares_HYG_fund_download.xml` | 4,675,317 | `10dcd91e095a56d83762019738aa5b14374ea5d1f723616636b52170150ec533` |
| `ishares_LQD_fund_download.xml` | 8,845,823 | `d0cc3b0121806b20a227b00ae50d3f8523e6cc560e7bae16d715824b50ce0a47` |
| `HYG_raw_ohlc.csv` | 648,827 | `1ed30697cd0c665d9abe3d60abfe8c03314fb8889f3a459df207c5b85cb3bce8` |
| `LQD_raw_ohlc.csv` | 824,802 | `9d120233fd18bbd28188c18ce5a99b8347416f58b903d7452b83b47d011fe036` |
| `HYG_nav_daily.csv` | 155,726 | `7735da958ef10522e39c9138b8cf8c686206585f3b805c327588fb61e9eae5de` |
| `LQD_nav_daily.csv` | 198,877 | `3d78dbd80b92e9715eb9f6249597d65556d12b6517aad6832640e7296698007a` |
| `benb_price_meta.json` | 695 | `8179c06f8f8dd088d3b08cb9b4d6a1a8abbd210239f3e2b226e70de223d8b339` |

```
RE-FETCH AFTER SEAL = FORBIDDEN unless a separate repair is authorised.
NAV_PROVENANCE      = RECONSTRUCTED_HISTORICAL_SERIES_WITH_NON-VINTAGE_LIMITATION
```

The ex-date calendars are **inside** these pinned files — the issuer's `Ex-Dividends`
column and the price source's `Dividends` column — and the sealed rule uses their union
(contract §D.4). No separate ex-date artifact exists or is needed.

## S1 artifact hashes — working-copy bytes = git blob bytes

Every file below is LF-only and covered by `.gitattributes` (`*.md`, `*.py` →
`text eol=lf`), so each SHA256 is both the working-copy and the git-blob identity.

| Artifact | SHA256 |
|---|---|
| **`BENB_PREREGISTRATION.md`** — the sealed contract, sole design authority | `1b7ca2122ba14c4097e4d76d7a733bf0c77ab9c0d02dd93a38c25bc1be5160cf` |
| `benb_prereg_validate.py` — mechanical pre-seal validator (**RESULT: PASS, 72/72, exit 0**) | `dfaff01a38011ec898199e2e00d6fa8324ba4bcd52bd87d10d043eb9617db984` |
| `BENB_SEAL_MANIFEST.md` — this file | recorded in the S1 return block (a file cannot contain its own hash) |

## Boundaries sealed

```
PRIMARY_ETF        = HYG          SECONDARY_ETF = LQD (NO RESCUE POWER)
SIGNAL AVAILABILITY = official NAV_t institutionally available after close(t) and
                      before open(t+1); public-website same-evening timestamp NOT
                      ESTABLISHED and not relied upon
EARLIEST EXECUTION = open(t+1).  NO same-close execution. NO overnight return credited.
BASIS              = b_t = ln(P_close,t / NAV_t), RAW unadjusted close / issuer NAV
ABNORMAL BASIS     = x_t = b_t - m_t, m_t = EXPANDING median of b_s for s < t,
                     minimum 250 prior observations, no imputation
PRIMARY SAMPLE     = x_t < 0 ONLY.  d_t = -x_t, CONTINUOUS, no threshold.
                     Premium side DESCRIPTIVE_ONLY, no promotion, no rescue.
EX-DATE RULE       = exclude t when t+1 is an ex-date, union of the two pinned calendars
DECOMPOSITION      = delta_b == R_OVERNIGHT + R_TRADABLE - R_NAV   (exact; verified to
                     1.776e-15 on 200,000 synthetic draws at S0 repair)
PRIMARY            = beta_T on R_TRADABLE (open(t+1) -> close(t+1)); Gate 1 iff L_T > 0
DIAGNOSTICS        = beta_O, beta_N; PROMOTION_POWER = NONE; may explain a failure,
                     may NEVER rescue beta_T
FIXED TRADE        = long 1 fixed unit at open(t+1), flat at close(t+1), else no
                     position; no sizing by d_t, no leverage, no vol targeting
COST               = 5.0 bps one-way, 10.0 bps round trip (fixed; conservative in
                     normal conditions, declared OPTIMISTIC in deep stress, and the
                     bias therefore runs IN FAVOUR of the strategy)
M1                 = lower 95 % bound of mean NET_TRADE_RETURN  >  0     STRICT
M2                 = lower 95 % bound of calendarised Sharpe    >  +0.30 STRICT (OD-1)
INFERENCE          = ONE calendar-year block bootstrap, B = 10,000, 95 % percentile,
                     ONE set of draws shared by beta_T, beta_O, beta_N, mean
                     NET_TRADE_RETURN and the Sharpe. x_t computed ONCE causally; the
                     bootstrap resamples year blocks of FROZEN observation tuples and
                     NEVER recomputes the expanding median inside a replicate.
FRAGILITY          = leave-one-calendar-year-out beta_T point estimate > 0 for EVERY
                     year. Exactly one fragility diagnostic.
CLASSES            = F · A-M · A · B · C1 · C2 · G · D · S · E, ordered, first match
                     wins, proved total, single-valued and exhaustive over a synthetic
                     sweep, with 0 illegal promotions to S
MULTIPLICITY       = m = 1 on HYG beta_T. No correction; no selection across cells.
EVIDENCE CEILING   = supported.  NEVER confirmed. NEVER independently confirmed.
```

## Prohibited outcome access — statement of record

At S1 and at this seal, for this lineage: **no** `b_t`, `x_t`, discount-sign count,
`beta_T`, `beta_O`, `beta_N`, strategy return, Sharpe, bootstrap replicate, P&L or
candidate statistic of any kind was computed, read, plotted or inferred; **no** strategy
engine, optimiser or backtest exists; **no** outcome artifact exists anywhere for this
lineage. Historical prices and NAVs were **never joined** — the only cross-file
operations ever performed on them were set operations on dates and counts. March 2020
was never inspected, singled out or filtered for. Signal frequency was never inspected.
The protected C-A store, key, position and return layers were **not** touched and no C-A
quantity was computed or inferred. Canonical TSMOM was not modified. CTA-EDGE-01-TA was
not reopened.

```
DISCOUNT_OBSERVATION_COUNT = UNKNOWN AT SEAL, deliberately.
```

Data acquisition beyond the consumed S0 grant begins only after controller / Aaron
acceptance of this seal; any real run needs a separate single-use Owner execution
authorisation; any reveal a separate single-use Owner reveal authorisation.

## Design-contributor disclosure — binding

- **Claude Fable 5.1** — `material_design_contributor` for CTA-EDGE-02-BENB (the BENB
  candidate, the stale-NAV alternative, the price-versus-NAV decomposition concept, the
  candidate instrument family, the portfolio-risk warning). **BARRED from blind
  certification** of this design or of any result under it. Seat row **S34**.
- **GPT-6 Astra** — **NOT design-exposed to this lineage.** Participation in the overall
  discovery round is not design exposure. Astra therefore **remains available as a fresh
  independent seat for CTA-EDGE-02-BENB** — unlike CTA-EDGE-01-TA, where both Fable and
  Astra were barred and no fresh certifier remained. This status may not be rewritten
  later for convenience in either direction.
- **Claude Opus 5** — the producing seat for the S0 frame, the S0 repair, this contract
  and the validator. It **must not certify them**. Seat row **S35**.
- **ChatGPT (Aaron-side)** — programme controller / acceptance checker.
- **Aaron** — Owner; every gate after this seal is Aaron's, and BENB-OD-1 is his.

## Pre-seal checks performed

1. **Repository state** verified mechanically: branch, HEAD, worktree, and `main` as an
   ancestor of HEAD.
2. **Provenance**: both S0 artifacts reproduce their pinned SHA256 byte-for-byte; all
   seven pinned data files reproduce their SHA256.
3. **Adversarial inspection**, all 22 original hazards plus the new M2 hazards: no
   adjusted close in the basis; no same-close lookahead; overnight never credited as
   tradable; premium observations cannot enter primary support; `beta_O`/`beta_N` have
   no rescue power; no severity-based sizing; no threshold; one horizon; cost defined;
   M2 defined **with authority**; the **strict** operator consistent in the Owner record,
   the contract and every classification branch; **no `>=` anywhere in the classification
   block**; no class can reach `S` without **both** M1 and M2; the point estimate can
   never substitute for the interval endpoint; classification disjoint and exhaustive;
   the mixed `beta_O`/`beta_N` case handled as `CLASS A-M`; no LQD rescue path; no stale
   `NOT SET` placeholder anywhere.
4. **Mechanical properties of the classification function** over a synthetic sweep: total
   and single-valued; all ten classes reachable; **0 illegal promotions to `S`**;
   `L_S = 0.300000` fails M2; `L_S = 0.3000001` may pass; `L_R = 0` exactly fails M1.
5. **Governance records** present: `F-BENB` declared before any member runs; the KB-1
   sample-reuse addendum; seat rows S34 and S35; and **no** execution authorisation for
   this lineage.
6. **`benb_prereg_validate.py` RESULT: PASS, 72 of 72 checks, exit 0.**

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

*Any receiver recomputes every hash above before use; chat-carried bytes are never a
source of truth.*
