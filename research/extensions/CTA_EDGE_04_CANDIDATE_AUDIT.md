# CTA-EDGE-04 — CANDIDATE SELECTION AUDIT

```
RECORD_TYPE = CANDIDATE_SELECTION_AUDIT
DATE        = 2026-09-16
SCOPE       = inventory of the UNRESOLVED Round-1 CTA discovery backlog after three
              closed lineages. NOT an S0. NOT a selection. NOT a backtest.
BRANCH      = cta-edge/physical-inventory-news-s0  (no new lineage branch opened)

HISTORICAL_OUTCOME_ACCESSED = NO   BACKTEST_RUN = NO   NEW_LINEAGE_OPENED = NO
```

> **CANDIDATE-STATUS UPDATE — 2026-09-18. Appended; nothing below is edited.** This audit records the backlog as it stood on 2026-09-16 and is retained as written. Two candidates have moved since:
>
> * **F5 `MACRO_MOMENTUM_VINTAGE`** became `CTA-EDGE-04-MMV` and is now **CLOSED / TERMINAL** (class D, `UNRESOLVED / LOW_POWER`). See [`mmv/MMV_CLOSEOUT.md`](mmv/MMV_CLOSEOUT.md).
> * **F7 `REBALANCING_FLOW_REVERSAL`** is **NOT AN ACTIVE EDGE CANDIDATE**. It is **preserved as a mechanism-study candidate**, its historical return run was **NEVER EXECUTED** and its return outcome is **UNEXPOSED**. `CTA-EDGE-05` is **not assigned to F7**. See [`F7_NONRUN_DISPOSITION.md`](F7_NONRUN_DISPOSITION.md).
>
> **F4 `INVENTORY_STATE_COMMODITY_CURVE` is the next candidate for PRE-S0 review. F4 S0 is NOT AUTHORIZED** — no lineage is opened by that note or by the F7 disposition.

> **UPDATED 2026-09-19 — F4 IS NOW PARKED PRE-OUTCOME.** The note above records the state on 2026-09-18 and is retained unedited. F4 went through PRE-S0 review and an S0 **data-PIT feasibility audit**, which executed successfully and returned **`PARKED_PRE_OUTCOME`**, reason `LOAD_BEARING_NG_STATE_NOT_PIT_RECONSTRUCTIBLE`: EIA publishes no per-release vintage of the natural-gas same-week historical comparison and its revisions file carries no revision-date field, so the load-bearing NG inventory STATE cannot be reconstructed under the accepted F4 definition. **This is not a falsification of F4, of storage theory or of trend conditionality** — no F4 outcome was ever exposed and no primary trial was consumed. **`CTA-EDGE-05` is UNASSIGNED** after the park, and no next candidate is selected here. Record: [`f4/F4_PREOUTCOME_PARK_CLOSEOUT.md`](f4/F4_PREOUTCOME_PARK_CLOSEOUT.md).

---

## §1 Discovery authorities — located, not reconstructed

```
ROUND1_DISCOVERY_AUTHORITIES_FOUND = YES

PRIMARY (Fable, on disk, outside the repo)
  Quant trade/2026-09-15-cta-edge-discovery-r1-mechanism-feature-map-fable-01.md
  635 lines · 97,240 bytes
  sha256 02ca5f45fe41763e55a353090645c3b2a98b6dcf5fce572623ede604e569344a
  Cited by name in research/extensions/ta/TA_EXPOSURE_DISCLOSURE.md §2, which is how
  it was located. Structure: §0 constraints · §1 families F1-F10 · §2 fifteen ideas
  set aside · §3 comparison · §4 top five · §5 final recommendation.

SECONDARY (Fable, on disk, outside the repo)
  Quant trade/2026-09-16-cta-edge-03-pins-od-1-expectation-source-fable-01.md
  223 lines · sha256 9fe1a9e7a03a274b9334f84780f23567943b329d7d7ba3ef74229a0bae604b8e
  The adopted PINS-OD-1 advice. Confirms that document exists in bytes.

ASTRA ROUND-1 = NOT PERSISTED IN THIS WORKSPACE.
  A disk-wide search found no Astra CTA discovery artifact. This matches the
  limitation already recorded in TA_EXPOSURE_DISCLOSURE.md §2 and
  ops/REVIEWER_EXPOSURE_LOG.md S32/S38: Astra's round-1 output reached the S0
  sessions only through the controller's task brief. Astra's recoverable CTA
  contributions are therefore only what the repository's own S0 frames record:
  an identification CHALLENGE to F1/TA, and the PINS candidate itself.
  This is a provenance gap, recorded and not repaired.

NO CONTROLLER SHORTLIST ARTIFACT EXISTS in the repository. The Fable map's §4 top
  five is the only ranked list on file. research/extensions/idea_registry/
  IDEA_REGISTRY_v2.csv is the TSMOM-extension X-register (X01-X46) — a different
  axis, holding MEASUREMENT designs on the core, not CTA-edge candidates.
```

```
TOTAL_ORIGINAL_CANDIDATES = 10 mechanism families (F1-F10) + 15 ideas set aside in §2
                            + 1 Astra-originated candidate (PINS) = 26 distinct entries
ALREADY_USED_OR_CLOSED    = 3   F1 -> CTA-EDGE-01-TA · F3 -> CTA-EDGE-02-BENB ·
                                PINS (Astra) -> CTA-EDGE-03-PINS
REMAINING_CANDIDATES      = 7 families (F2, F4, F5, F6, F7, F8, F9, F10 minus none)
                            = F2 F4 F5 F6 F7 F8 F9 F10 -> 8 families
                            + the 15 §2 set-asides, none revived
```

*(F1, F3 and PINS are excluded from everything below.)*

---

## §2 Candidate inventory — the eight unresolved families

### F7 — `REBALANCING_FLOW_REVERSAL`

```
ORIGIN                 = FABLE            ORIGINAL_DISCOVERY_STATUS = shortlisted (rank 3)
MECHANISM              = Balanced mandates (pensions, target-date, 60/40) must sell the
                         intra-month outperformer and buy the underperformer at calendar
                         boundaries regardless of view. The flow is price-insensitive,
                         predictable in SIGN from the month-to-date equity-bond gap, and
                         meets thin liquidity at the boundary. Payer: the rebalancing
                         mandate. Paid: whoever supplies liquidity over the boundary.
INFORMATION_SOURCE     = flow (exogenous calendar x price-derived gap)
PROPOSED_INSTRUMENT    = SPY / TLT pair, 2-4 session relative position
DATA_REQUIRED          = SPY and TLT daily closes + the exchange calendar. NOTHING ELSE.
POINT_IN_TIME_RISK     = LOW. Daily closes; no revisions, no vintages, no consensus,
                         no entitlement. The only mapping choice (which session is
                         "month-end") is fixed once by rule.
EXPECTED_DATA_COST     = ZERO. Verified in hand: data/close_prices_raw.csv carries SPY
                         (col 2) and TLT (col 8), 8,400 rows, 1993-01-29 .. 2026-06-12.
LIKELY_FREQUENCY       = daily observation, ~2-4 trading days of exposure per month
DISTINCT_FROM_TREND    = MEDIUM-HIGH. The gap is price-derived, but the prediction is an
                         INTERACTION of an exogenous calendar with the gap and its sign
                         flips month to month; no monotone transform of past returns
                         reproduces a calendar-timed reversal. The placebo makes this
                         TESTABLE rather than asserted.
DISTINCT_FROM_CARRY    = YES (no term-structure object)
DISTINCT_FROM_EDGE_01  = YES (auction supply, different calendar and payer)
DISTINCT_FROM_EDGE_02  = YES (ETF-NAV arbitrage capital, different payer)
DISTINCT_FROM_EDGE_03  = YES (physical news, different information class)
WHY_NOT_SELECTED_FIRST = Ranked 3rd behind F1 and F3, which Fable judged to have more
                         independent events (F1) and higher portfolio relevance (F3).
                         Not excluded on any scientific defect.
FABLE_DESIGN_EXPOSED_IF_SELECTED = YES   ASTRA_DESIGN_EXPOSED_IF_SELECTED = NO
CLASSIFICATION         = EDGE_CANDIDATE
```

### F5 — `MACRO_MOMENTUM_VINTAGE`

```
ORIGIN                 = FABLE            ORIGINAL_DISCOVERY_STATUS = shortlisted (rank 4)
MECHANISM              = Markets underreact to slow, lagged, revised fundamental
                         information the way they underreact to price. A sleeve trading
                         the DIRECTION OF CHANGE in growth, inflation and policy earns
                         the premium for acting before consensus updates. Payer: mandates
                         and investors that update over quarters. Persists because release
                         lags and revisions are permanent.
INFORMATION_SOURCE     = macro (vintage fundamentals)
PROPOSED_INSTRUMENT    = the 17-ETF core universe, sign-only, monthly
DATA_REQUIRED          = ALFRED vintages for CPIAUCSL, PCEPILFE, PAYEMS, INDPRO, UNRATE;
                         fed funds / DGS2 (unrevised, partly on disk); foreign CPI already
                         on disk from the Value study (non-vintage for some - a stated
                         limitation); ETF panel in hand.
POINT_IN_TIME_RISK     = LOW-MEDIUM with ALFRED, HIGH without it. ALFRED is a free,
                         documented, machine-readable TRUE VINTAGE archive - it exists
                         precisely to answer "what did the data say on date X". The
                         residual risk is the alignment layer, which is testable
                         mechanically, and the foreign legs which may lack vintages.
EXPECTED_DATA_COST     = ZERO (ALFRED is free and public). Not fetched.
LIKELY_FREQUENCY       = monthly
DISTINCT_FROM_TREND    = MEDIUM. Different information, SAME instruments and horizon; it
                         will agree with the price trend in every sustained regime and
                         differ mainly at turns. This is the candidate's weak point.
DISTINCT_FROM_CARRY    = YES          DISTINCT_FROM_EDGE_01/02/03 = YES / YES / YES
WHY_NOT_SELECTED_FIRST = Ranked 4th. Its own screen has "a real chance of returning the
                         core's static bet in another vocabulary"; 10-15 effective macro
                         turns give low power; the mapping table is a large design space.
FABLE_DESIGN_EXPOSED_IF_SELECTED = YES   ASTRA_DESIGN_EXPOSED_IF_SELECTED = NO
CLASSIFICATION         = EDGE_CANDIDATE
```

### F4 — `INVENTORY_STATE_COMMODITY_CURVE`

```
ORIGIN                 = FABLE            ORIGINAL_DISCOVERY_STATUS = shortlisted (rank 5)
MECHANISM              = Theory of storage (Kaldor, Working): convenience yield is convex
                         in inventories, so backwardation, price volatility and shock
                         persistence are all state-dependent on physical scarcity. Payer:
                         in a low-inventory state, consumers needing the physical good pay
                         holders of inventory and near-dated long risk.
INFORMATION_SOURCE     = physical
PROPOSED_INSTRUMENT    = the Databento 18-root CME commodity panel (~12-13 roots covered)
DATA_REQUIRED          = EIA weekly petroleum + natural-gas storage; USDA WASDE archive
                         (monthly, first release only, point-in-time reconstruction
                         laborious); COMEX warehouse stocks (free, scraping) and/or LME
                         (LICENSED); USDA NASS livestock. ~13 heterogeneous series.
POINT_IN_TIME_RISK     = MEDIUM-HIGH, BUT MATERIALLY REDUCED BY THE PINS WORK (see §5).
                         EIA weekly are official and lightly revised; WASDE are FORECASTS
                         revised monthly so only first release is PIT; warehouse-stock
                         definitions are exchange-specific; LME history is not free.
EXPECTED_DATA_COST     = LOW in money, HIGH in labour. Free sources except LME.
LIKELY_FREQUENCY       = weekly inputs -> monthly state
DISTINCT_FROM_TREND    = HIGH. Physical stocks are not a function of past futures prices
                         at these horizons.
DISTINCT_FROM_CARRY    = MEDIUM. The closed carry study tested the UNCONDITIONAL basis
                         (both arms flat). F4 introduces a NEW variable (physical stocks)
                         and a DIFFERENT claim (the basis-return relation is
                         state-dependent), with the unconditional null as its MOTIVATION
                         rather than its target. Shares the panel and the basis as premise.
DISTINCT_FROM_EDGE_01  = YES   DISTINCT_FROM_EDGE_02 = YES
DISTINCT_FROM_EDGE_03  = YES, and the distinction must be stated: PINS was inventory
                         NEWS (first-published surprise vs expectation -> post-release
                         return). F4 is inventory STATE (normalised level -> basis and
                         trend persistence). Different claim, different failure mode, and
                         crucially F4 NEEDS NO CONSENSUS SERIES - which is exactly what
                         killed PINS.
WHY_NOT_SELECTED_FIRST = Ranked 5th: the most expensive data assembly in the map, on a
                         burned, shared, GFC-absent panel at 17 trials, bounded by the
                         commodity sleeve.
FABLE_DESIGN_EXPOSED_IF_SELECTED = YES   ASTRA_DESIGN_EXPOSED_IF_SELECTED = NO*
                         *Astra is exposed to the PINS inventory-news candidate. F4 is a
                         different claim from a different seat, so Astra is NOT
                         automatically exposed - but the adjacency should be declared at
                         S0 rather than asserted away.
CLASSIFICATION         = EDGE_CANDIDATE
```

### F6 — `MACRO_ANNOUNCEMENT_PREMIUM`

```
ORIGIN                 = FABLE   ORIGINAL_DISCOVERY_STATUS = absorbed into F1, "not a slot
                                 of its own"; "just outside the five"
MECHANISM              = Scheduled announcements resolve macro uncertainty at a known
                         time; holders of risk through the resolution are paid for bearing
                         concentrated non-diversifiable risk.
INFORMATION_SOURCE     = institutional calendar
DATA_REQUIRED          = SPY/TLT closes (in hand) + FOMC and BLS release calendars.
EXPECTED_DATA_COST     = ZERO, AND ALREADY PAID. The closed TA lineage built and
                         preserved a working release-calendar parser:
                         research/extensions/ta/ta_macro_calendar.py with
                         TA_MACRO_CALENDAR_MANIFEST.md — CPI 251 releases 2006-01-18 ..
                         2026-12-10, NFP 251, FOMC 171, from Federal Reserve and BLS
                         primary sources. TA's closure preserved all of it.
POINT_IN_TIME_RISK     = LOW (official, unrevised calendars)
DISTINCT_FROM_TREND    = HIGH        DISTINCT_FROM_CARRY = YES
DISTINCT_FROM_EDGE_01  = MEDIUM. F6 was DESIGNED as F1's control-day coefficients; the
                         calendars overlap mid-month and TA's own closure was caused by
                         that entanglement (only 7 of 213 windows macro-clean).
DISTINCT_FROM_EDGE_02/03 = YES / YES
WHY_NOT_SELECTED_FIRST = Never proposed as a lineage. Fable: "a by-product of F1's
                         controls, not a slot of its own", and its abandon condition is
                         "no announcement-day premium after 2010 at the cost bar - then it
                         is a decayed equity anomaly and not worth a lineage".
STATUS CHANGE          = ITS HOST LINEAGE IS DEAD. F1 closed, so F6's designated home no
                         longer exists. That ORPHANS it; it does not PROMOTE it. Two
                         standing priors remain against it: documented post-2015 decay,
                         and the seasonality wall (0/18 calendar effects at ETF
                         granularity).
FABLE_DESIGN_EXPOSED_IF_SELECTED = YES   ASTRA_DESIGN_EXPOSED_IF_SELECTED = NO
CLASSIFICATION         = EDGE_CANDIDATE (weak), NOT SHORTLISTED — see §6
```

### F2 — `DEALER_INTERMEDIATION_CAPACITY`

```
ORIGIN                 = FABLE (candidate) / ASTRA (the intermediation challenge that
                         produced it)   ORIGINAL_DISCOVERY_STATUS = absorbed as F1's
                         conditional cell F1.c; "standalone is not proposed now"
MECHANISM              = Post-2008 regulation made dealer balance sheet the scarce input
                         in Treasury intermediation; when dealers already warehouse large
                         inventories the marginal unit of duration requires higher
                         expected return.
INFORMATION_SOURCE     = institutional constraint / positioning
DATA_REQUIRED          = NY Fed primary-dealer statistics (free, weekly, 1998 -> , with
                         DOCUMENTED SERIES BREAKS in 2001, 2013 and 2015); DTCC GCF repo;
                         NY Fed fails; FRED swap spread (ends 2016).
POINT_IN_TIME_RISK     = MEDIUM. Raw positions and raw spreads qualify; model-based
                         variables (EBP, ACM/Kim-Wright term premia) are RE-ESTIMATED and
                         are inadmissible as features.
EXPECTED_DATA_COST     = ZERO in money; MEDIUM in labour (break-bridging).
DISTINCT_FROM_TREND    = HIGH in information, MEDIUM in POSITION - "long duration when
                         dealer inventories are high" will often coincide with the core's
                         structurally long bond exposure and must pass the X45
                         position-level screen.
DISTINCT_FROM_EDGE_01  = LOW. It was designed as a cell INSIDE the now-closed TA, and it
                         would inherit TA's fatal problem: identification insufficiency at
                         daily ETF granularity.
WHY_NOT_SELECTED_FIRST = Explicitly not proposed standalone: only ~20-30 independent
                         inventory swings and ~5 funding-stress events, so a standalone
                         null would be low-information.
STATUS CHANGE          = Host lineage dead. The reason it was never standalone (low power)
                         has NOT changed.
FABLE_DESIGN_EXPOSED_IF_SELECTED = YES   ASTRA_DESIGN_EXPOSED_IF_SELECTED = YES
CLASSIFICATION         = EDGE_CANDIDATE (weak), NOT SHORTLISTED — see §6
```

### F8 — `POSITIONING_CROWDING` — PARKED

```
ORIGIN                 = FABLE   ORIGINAL_DISCOVERY_STATUS = PARKED
PARK_REASON            = Positions are functions of prices: every public positioning proxy
                         is reproducible from past returns, so a positive is "trend
                         strength in positioning vocabulary" and a null is unattributable.
                         Carried over from the Phase-C adjudication
                         POSITIONING_PROMOTE_TO_S0 = NO ("wrong instrument for the right
                         question"). Fable's own instruction: it "should stay parked until
                         financial futures are owned AND the static-control lineage's
                         commodity placebo has reported."
HAS_PARK_REASON_CHANGED = NO — verified, both conditions still unmet:
                         (a) financial futures are NOT owned. The Databento holding is 18
                             COMMODITY roots (CL HO RB NG GC SI HG PL PA ZC ZS ZW ZM ZL KE
                             LE HE GF). The NQ/MNQ intraday files on disk belong to the
                             separate Intraday-Trend project and are not this programme's
                             panel.
                         (b) no static-control lineage or commodity-placebo artifact
                             exists anywhere in the repository (searched).
                         The only thing round 1 added was feature F8.c, which Fable judged
                         "not strong enough to lift the park".
CLASSIFICATION         = PARKED. NOT REVIVED.
```

### F9 — `STOCK_BOND_CORRELATION_REGIME`

```
ORIGIN                 = FABLE   ORIGINAL_DISCOVERY_STATUS = "Information, not a slot"
MECHANISM              = The sign regime of the stock-bond correlation is the state in
                         which the core's diversification is most likely to fail, because
                         the core's static component (X45) is long bonds, credit and
                         equity together.
PORTFOLIO ROLE         = "Portfolio-construction information ONLY: it tells the book how
                         many bets its static component holds. Any use as a de-grossing
                         gate on the core is the crash-defence class and is not proposed."
CLASSIFICATION         = PORTFOLIO_COMPONENT. Not an independent CTA information edge.
                         Fable's own abandon condition includes "Aaron ruling that
                         portfolio-construction information without a return claim is not
                         a research slot in this cycle (a reasonable ruling)".
```

### F10 — `TREND_STRUCTURE_STATE`

```
ORIGIN                 = FABLE   ORIGINAL_DISCOVERY_STATUS = REVIEWED AND DEMOTED
REASON                 = "Every feature is a transformation of past returns of the 17
                         assets. The prior correlation of any resulting book with the core
                         is >= 0.9; the hindsight timing residual bounds the upside at
                         roughly 0.15 Sharpe." Fable: "abandoned as a discovery direction
                         here; no lineage is proposed." The register already holds the
                         correct MEASUREMENT designs (X19-X23).
CLASSIFICATION         = DEMOTED / not an edge candidate. The X-register holds the cheap
                         descriptive pass if ever wanted.
```

### The fifteen §2 set-asides — none revived

VIX term-structure state · implied correlation / MOVE / dealer gamma · cross-currency
basis and OIS · EPFR and fund flows · corporate issuance calendar · ACM / Kim-Wright term
premia · vol-control flow proxies · open-interest-confirmed trend · ETF volume / Amihud ·
curve curvature and deferred carry · index-roll congestion · crypto funding carry ·
single-name idiosyncratic trend · short-horizon futures reversal · macro-regime gates.

Each carries a stated reason in the map (not owned, not free, revised, deterministic
function of past returns, another programme's object, or closed on power). **None has had
its reason overturned by anything in the three closed lineages.** Two are worth one line:
the **corporate issuance calendar** ("the mechanism is F1's on a different issuer") is
recorded as a later extension of F1, and F1 is now closed; the **VIX term-structure state**
remains blocked by the spent VRP trial.

---

## §3 Sample-reuse and trial overlap

| candidate | PRICE_SAMPLE_REUSE | PHYSICAL/FLOW/FUNDAMENTAL REUSE | TRIAL_FAMILY_OVERLAP |
|---|---|---|---|
| **F7** | ETF panel, **BURNED / T0**, 8-plus prior uses, `D-ETF` open | none — the flow is inferred from the same prices | **MEDIUM** with the closed seasonality overlay (E1, 0/18 turn-of-month). No family declared yet. |
| **F5** | ETF panel, **BURNED / T0** | ALFRED vintages **NEW**, no prior programme exposure | LOW. No macro-change signal has ever been built. Value used *levels*; the yield-curve overlay used a level as a *gate*. |
| **F4** | Databento 18-root panel, **BURNED / T1**, `N_trials = 14 -> 17` after X01, **SHARED** with the pre-seal mean-reversion programme, **GFC absent** | EIA / USDA / COMEX **NEW** | **MEDIUM** with the closed commodity-carry study (same panel, basis as premise). Its own §12 rates this MEDIUM rather than LOW for exactly that reason. |
| **F6** | ETF panel, **BURNED / T0** | release calendars are metadata, no burn | LOW-MEDIUM with seasonality (both calendar-anchored at ETF granularity) |
| **F2** | ETF panel **BURNED**, or cash/futures not owned | NY Fed dealer stats **NEW** | LOW with closed work, but HIGH structural inheritance from closed TA |
| **F8** | both panels burned | COT **NEW**, never fetched | **HIGH** with parked X41 and with the closed crash-defence class |

```
EVIDENCE_CEILING for every candidate above = supported.
A new physical, flow or fundamental leg does NOT launder a reused price sample - the
reading sealed at CTA-EDGE-02-BENB and inherited here. No candidate can reach
`confirmed` on these panels.
```

---

## §4 Execution / infrastructure and portfolio classifications

```
EDGE_CANDIDATE          F7, F5, F4, and weakly F6 and F2
EXECUTION_INFRASTRUCTURE  F7.d — the frozen core's own month-end execution exposure to
                        the rebalancing concession. This is a MEASUREMENT about the
                        canonical book's implementation, it WAITS under the C-A
                        safeguards, and it must not be used to promote F7 as an edge.
                        It is sequenced with the registered X30 (execution-day
                        robustness), not duplicated.
PORTFOLIO_COMPONENT     F9 (stock-bond correlation regime)
PARKED                  F8 (positioning / crowding) — park intact
DEMOTED                 F10 (trend-structure state) and the 15 §2 set-asides
```

**No idea is promoted merely because it is unused.** F7.d, F9 and F10 are all "available"
and none of them becomes an edge candidate on that basis.

---

## §5 The data-first filter, applied with what PINS taught

PINS closed because a *market-consensus* leg could not be reconstructed point-in-time
without a commercial entitlement. Applying that lesson as a filter, rather than as a
general pessimism about data:

```
WHAT PINS ACTUALLY ESTABLISHED, AND WHAT SURVIVES IT

  ESTABLISHED (reusable): EIA first-published vintages ARE reconstructible - 765
  archived WPSR releases 2012-01-05 .. 2026-09-10, each with 15 machine-readable CSVs,
  enumerated and committed at research/extensions/pins/PINS_EIA_RELEASE_DATES.txt.
  That work product is a genuine asset for F4, whose EIA leg is the same archive.

  KILLED: any candidate needing a historical MARKET-EXPECTATION or SURVEY series
  behind a commercial entitlement.

  NOT KILLED: candidates needing official published QUANTITIES (levels, positions,
  vintages, calendars). Those are free and documented.
```

| candidate | new data needed to reach S1 | entitlement required? | cheapest pre-outcome gate |
|---|---|---|---|
| **F7** | **NONE** | no | calendar placebo — kill if non-boundary windows show the same gap-conditioned reversal |
| **F5** | ALFRED vintages (free API) | no | **PnL-free** position-level sign agreement vs the canonical composite; stop above the declared bound |
| **F4** | ~13 inventory series; EIA path already mapped; **LME licensed** | only for LME, which is avoidable via COMEX | **PnL-free** premise: do normalised stocks explain the front basis with the theoretical sign and convex shape? |
| **F6** | none (TA's calendar parser exists) | no | announcement-day excess return vs the cost bar, post-2010 |
| **F2** | NY Fed dealer stats (free, breaks) | no | the F1.c ordering contrast — **but its host lineage is closed** |

**Not one shortlisted candidate needs a new institutional entitlement to reach S1.** That
is the single most useful thing this audit establishes, and it is a direct consequence of
running the PINS feasibility gate before spending anything.

---

## §6 Shortlist — at most three, compared on factual dimensions only

**Not ranked by expected return.** The ordering below is by *data and falsification
cost*, which is the programme's own stated post-PINS preference, and the factual
dimensions are laid out so the controller can weight them differently.

| dimension | **F7 REBALANCING_FLOW_REVERSAL** | **F5 MACRO_MOMENTUM_VINTAGE** | **F4 INVENTORY_STATE_COMMODITY_CURVE** |
|---|---|---|---|
| economic mechanism | mandate rebalancing; price-insensitive payer, exogenous timing | underreaction to slow revised fundamentals | theory of storage; convex convenience yield |
| information class | flow × exogenous calendar | macro vintage | physical |
| data feasibility | **HIGHEST — nothing to fetch** | HIGH — free ALFRED | LOWEST — 13 heterogeneous series |
| PIT feasibility | **HIGHEST — no revisions at all** | HIGH — ALFRED is a true vintage archive | MEDIUM — WASDE forecasts, exchange definitions |
| distinctness from trend | MEDIUM-HIGH, and **testable via placebo** | **MEDIUM — the weak point**; may collapse into X45 | **HIGHEST** |
| overlap with closed work | MEDIUM (seasonality 0/18) — see §7 | LOW | MEDIUM (carry panel, burned + shared + no GFC) |
| independent events | ~75-90 material month-ends | ~10-15 macro turns | ~20-25 inventory states |
| cheapest falsification | calendar placebo, one build unit | **PnL-free position screen, closes in an afternoon** | PnL-free inventory→basis premise |
| complexity | **LOW** | MEDIUM-HIGH (vintage alignment) | **HIGH** |
| design exposure if selected | Fable YES · Astra NO | Fable YES · Astra NO | Fable YES · Astra NO (adjacent to PINS) |
| main reason not to test | small effect on the panel where seasonality went 0/18; may have migrated earlier in the month; sits near the mean-reversion programme's territory | the mapping table is a large design space that must be frozen from theory first; low power; lags into crashes | most expensive assembly in the map, on a burned, shared, GFC-absent panel at 17 trials |

```
VIABLE_EDGE_04_SHORTLIST
  1. F7  REBALANCING_FLOW_REVERSAL
  2. F5  MACRO_MOMENTUM_VINTAGE
  3. F4  INVENTORY_STATE_COMMODITY_CURVE

CTA_EDGE_04_FROM_EXISTING_BACKLOG = VIABLE
NEW_DISCOVERY_ROUND_REQUIRED      = NO
```

**Excluded from the shortlist, with reasons:**

* **F6** — never proposed as a lineage; orphaned by TA's closure rather than promoted;
  two standing priors against it (post-2015 decay, the 0/18 seasonality wall). Its
  cheapest use is as a declared control inside whichever calendar-based lineage runs.
* **F2** — designed as a cell inside the closed TA and would inherit TA's fatal daily-ETF
  identification problem; ~20-30 independent swings make a standalone null
  low-information; Fable did not propose it standalone and that reason is unchanged.
* **F8** — parked, park conditions verified still unmet.
* **F9** — portfolio-construction information, not an edge.
* **F10** and the 15 set-asides — demoted with unchanged reasons.

---

## §7 The one genuinely difficult question — and why Fable should not answer it

```
HIGH_DIFFICULTY_OWNER_DECISION_REQUIRED = YES
FABLE_OWNER_ADVICE_RECOMMENDED          = NO
```

> **ANSWERED 2026-09-18 — this question is no longer outstanding.** The flags above are retained as the state on 2026-09-16 and are **stale**; they are not edited. An independent review seat — not Fable, not the F7 originator and not its design author — adjudicated the question and returned **`ORIGINAL_F7_DISTINCTNESS = PASS`**: the original F7 was **genuinely distinct** and was **NOT** a post-hoc conditional re-cut of the closed seasonality / turn-of-month null.
>
> The precedent this sets is narrow and worth stating exactly: *“the unconditional test failed but the conditional one is different”* is an **adjudicable** distinctness argument in this programme, not a barred one — when the mechanism, the object and the prediction genuinely differ. It does not make that argument automatically valid for any future proposal.
>
> F7 was nevertheless removed from the active edge queue, for a **different reason entirely**: the fully repaired object was `MATERIALLY_REDESIGNED` and its strongest admissible claim was a predictive relation rather than an executable edge. Full record, including the provenance limits on the adjudicating seat, in [`F7_NONRUN_DISPOSITION.md`](F7_NONRUN_DISPOSITION.md).

It is **not** the choice among F7/F5/F4 — those differ on factual dimensions laid out
above and the choice is an ordinary Owner weighting.

The difficult question is specific to F7, and it is a governance precedent as much as a
scientific one:

```
QUESTION
  The closed seasonality overlay tested the UNCONDITIONAL turn-of-month return of the
  book and its sleeves and returned 0/18. F7 proposes a CONDITIONAL, sign-flipping,
  cross-asset boundary effect on the SAME BURNED PANEL.

  Fable's argument: a sign-flipping effect averages to roughly zero unconditionally, so
  the unconditional null is CONSISTENT WITH F7 and is not evidence against it; the
  mechanism, the object and the prediction are all different.

  That argument is correct in principle. It is ALSO the exact shape of a post-hoc
  conditional re-cut of a failed calendar study on the same sample. Whether F7 is a new
  mechanism or a rescue of a closed null is a judgement with precedent consequences for
  every future "the unconditional test failed but the conditional one is different"
  proposal in this programme.

WHY NOT FABLE
  Fable ORIGINATED F7 and WROTE the distinctness argument. Asking Fable to adjudicate
  whether its own argument clears the rescue bar is not an independent check.

WHO IS ELIGIBLE
  GPT-6 Astra is exposed to CTA-EDGE-01-TA (F1 identification challenge) and to
  CTA-EDGE-03-PINS (the candidate itself). Astra is NOT exposed to F7, F5 or F4.
  Astra is therefore a legitimately fresh seat for this specific adjudication.
  Exposure is lineage-specific and was checked per candidate, not assumed.
```

If the controller selects **F5** or **F4** instead, this question does not arise and no
high-difficulty decision is outstanding.

---

## §8 What this audit did not do

```
No historical outcome was accessed.       No backtest was run.
No new lineage was opened.                No S0 frame was written.
No candidate was selected.                No seal, build or run authorization exists.
Fable and Astra were NOT asked for new ideas.
No parked candidate was revived and no set-aside reason was overturned.
```

Design-exposure status was **checked per candidate against the repository**, not assumed
from the programme's general history: Fable is exposed to every family it authored (F2,
F4, F5, F6, F7, F8, F9, F10); Astra is exposed to F1/TA and to PINS, and to F2 through
the intermediation challenge that produced it — and to nothing else in this backlog.
