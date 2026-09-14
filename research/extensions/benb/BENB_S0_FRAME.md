# BENB_S0_FRAME — `CTA-EDGE-02-BENB` — bond ETF–NAV basis

```
LINEAGE_ID        = CTA-EDGE-02-BENB
CANDIDATE         = BOND_ETF_NAV_BASIS
STAGE             = S0 FRAME — RESEARCH-QUESTION DEFINITION ONLY
S0_FRAME_STATUS   = HOLD   (one named blocker, §G)
STATUS            = PROPOSAL, AWAITING CONTROLLER / OWNER DECISION
CREATED           = 2026-09-15
AUTHOR            = Claude Opus 5 (Main Agent / builder seat)
AUTHORITY         = QUANT_WORKFLOW_VNEXT.md (workspace root). This document
                    authorises NOTHING: no build, no fetch, no run, no reveal.
HISTORICAL_NAV_FETCHED     = NO
BASIS_OUTCOME_ACCESSED     = NO
ETF_RETURN_OUTCOME_ACCESSED = NO
BACKTEST_RUN               = NO
BUILD_STARTED              = NO
S1_SEAL_CREATED            = NO
RUN_AUTHORIZATION_CREATED  = NO
```

> **Reading rule.** Section **A** is fact. Section **B** is external literature and
> market mechanics — other people's results and other people's documentation, never
> this programme's evidence. Section **C** is a **proposal**. Section **D** lists what
> is **not yet tested**. Section **E** is parked. Section **F** is forbidden. Section
> **G** is the blocker. Nothing in C, D or E may be cited as an established property
> of this programme.

---

## A. CURRENT PROGRAMME / DATA FACTS

### A.1 Programme state — read, unchanged by this document

| object | state | touched here? |
|---|---|---|
| canonical TSMOM | `SUPPORTED — NOT INDEPENDENTLY CONFIRMED`, FROZEN research benchmark | **NO** |
| C-A | sealed, LIVE under passive monthly accrual | **NO — not accessed, not inferred** |
| C-D | `HOLD` on the unexplained October-2008 cross-vendor residual | **NO** |
| TSMOM-VRP-01 | CLOSED — `UNRESOLVED` / Class 3 | **NO** |
| Time-Series Value, X01, XSMOM, the four overlays | CLOSED | **NO** |
| **CTA-EDGE-01-TA** | **CLOSED PRE-OUTCOME**, identification design insufficient | **NO — not reopened** |
| knowledge-base repository | not the active workstream | **NOT MODIFIED** |

**Purpose of this lineage, stated once.** Not "make TSMOM's Sharpe higher". The
question is whether a **genuinely different market-structure / intermediation
information source** exists. Portfolio relevance to TSMOM may be considered only
after independent evidence exists, and is not part of this frame.

### A.2 Prior repository work on this object — there is none

Repository grep, 2026-09-15: **no file mentions premium/discount, stale pricing or
authorised participants.** No NAV series has ever been fetched, no basis has ever been
computed, and no ETF-versus-NAV quantity exists anywhere in this repository.

Adjacent records that do exist, checked for overlap:

- **Time-Series Value** used `LQD` as its *public corporate credit* object with the
  BAA10Y spread; **`HYG` was explicitly REMOVED** from that study and its credit object
  was frozen as "LQD only, never an OAS, never high-yield Value". That is a different
  variable class (fundamental cheapness versus own history) and creates no overlap —
  but it does mean LQD's *price history* carries prior programme exposure.
- **Crash defence** used the book's own realised-volatility and dispersion percentiles.
  A different class of variable, and anti-aligned to this one.
- **C-D** recorded an unexplained October-2008 cross-vendor residual on XLE, XLU, RWX,
  DBA, HYG and VNQ. **`HYG` is one of those names.** That is a recorded finding about
  the price panel, and it is a declared data risk for this lineage (§A.3, §C.11).

### A.3 Local price data — metadata only, no basis computed

Verified from `src/fetch_data.py`, `data/fetch_metadata.csv` and a first/last non-null
scan of the panel. **No price value was retained, no return computed, no basis
constructed.**

| ticker | local rows | coverage | note |
|---|---:|---|---|
| **HYG** | 4,825 | 2007-04-11 → 2026-06-12 | proposed PRIMARY |
| **LQD** | 6,007 | 2002-07-30 → 2026-06-12 | proposed SECONDARY |
| TLT | 6,007 | 2002-07-30 → 2026-06-12 | parked negative control |
| IEF | 6,007 | 2002-07-30 → 2026-06-12 | parked |
| **EMB** | — | **ABSENT from the panel** | not evaluable locally |
| VNQ | 5,461 | 2004-09-29 → 2026-06-12 | not needed |

```
PRICE_DATA_CONVENTION = SPLIT- AND DIVIDEND-ADJUSTED CLOSE (total return).
```

**Verified at source, not inferred.** `src/fetch_data.py` fetches every ticker with
`Ticker.history(period="max", auto_adjust=True)`, and its own header states
*"`auto_adjust=True` => the returned `Close` is the split/dividend-adjusted"* close.
`SAMPLE_REUSE.md` KB-1 describes the panel as "30 yfinance **adjusted-close** series".

**This is decisive and it is the blocker.** A published NAV is a **raw per-share**
value. An adjusted close is a **total-return** series. Their ratio drifts upward
monotonically with every distribution ever paid — for LQD since 2002 and HYG since
2007 that is a large accumulated factor, not a rounding issue. `log(adjusted close /
published NAV)` is therefore **not a basis at all**; it is a cumulative-distribution
artefact with a small basis riding on top of it. See §G.

Also absent: **no OHLC anywhere in the panel** — closes only, so no open price exists
for a realistic post-publication entry (§C.6, §G).

### A.4 Sample reuse and evidence ceiling

```
ETF_PRICE_SAMPLE_REUSE_STATUS = BURNED / EXPOSED.
```

The panel is `dataset.yfinance.multi-asset-etf-panel` (KB-1), burned 6 of 6 registered
research paths, carrying `must_not_be_retested_on_same_sample`. LQD additionally
carries Time-Series Value exposure and HYG carries the C-D residual.

```
EVIDENCE_CEILING = supported.  Never confirmed, never independently confirmed.
MIXED PROVENANCE = the NAV history would be a genuinely NEW external series with no
                   prior programme exposure; the ETF PRICE history is burned. A result
                   built on both is dependent evidence, and the ceiling is set by the
                   burned leg. A new NAV series does not launder a burned price series.
N_trials          = NOT ASSERTED. D-ETF-COUNT remains UNKNOWN_PENDING_AARON_DECISION
                    and is NOT decided here.
```

---

## B. VERIFIED EXTERNAL LITERATURE AND MARKET-MECHANICS PRIOR

**Status:** external results and third-party documentation. Not evidence for this
programme. No reported Sharpe, alpha or effect size is imported as a programme claim.
Literature is used here only to fix the mechanism, the timing, one horizon, the
stale-NAV alternative, and the feature construction.

### B.1 The load-bearing sources

| # | source | authority | what it establishes |
|---|---|---|---|
| 1 | **Petajisto, "Inefficiencies in the Pricing of Exchange-Traded Funds"**, *Financial Analysts Journal* **73(1), 24–54 (2017)** | peer-reviewed, Graham & Dodd winner | read from the author's PDF |
| 2 | **Todorov, "The anatomy of bond ETF arbitrage"**, **BIS Quarterly Review, March 2021** | central-bank research | read from the BIS PDF |
| 3 | **BlackRock EII Global Research, "Pricing and Liquidity of Fixed Income ETFs in the Covid-19 Crisis of 2020"**, July 2020, presented to the **SEC Fixed Income Market Structure Advisory Committee** | **ISSUER material — an interested party** | read from the SEC-hosted PDF |
| 4 | **Karmaziene & Terrada, "Fast ETFs, Slow Bonds: Price Adjustment under Monetary Tightening"**, SSRN, 11 Oct 2025 | working paper, not yet peer-reviewed | abstract-level only |

**Petajisto (2017).** Sample **January 2007 – December 2010**; 1,078 ETFs (904 after
the stale-pricing filter); US-listed ETFs, ~97 % of ETF assets. Deviations from NAV sit
within a band of about **200 bps**, and **about 100 bps survives** after his novel
**cross-sectional** stale-pricing control (using the contemporaneous prices of similar
ETFs rather than assuming a price process). Junk-bond ETFs are named among the funds
showing the largest deviations. Mean reversion is short-horizon; his real-time signal
work uses **five-minute periods from 9:30 a.m. to 4:00 p.m.** Critically: the
trading-strategy abnormal returns are reported **BEFORE transaction costs**, and the
paper states in terms that *"the profits are sensitive to transaction costs, so the
execution [matters]"*. **No Sharpe from this paper is imported here.**

**Todorov / BIS (2021).** Bond-ETF arbitrage is weakened because creation and
redemption baskets are **systematically different from holdings** — for the largest bond
ETF the basket is **under 3 %** of actual holdings. AP constraints named: illiquid bond
markets, large minimum trading amounts, and uncertainty about basket composition until
negotiation with the sponsor completes. In March–April 2020 **"steep discounts of share
prices relative to NAV transformed into large premiums"** within days, with tracking
error for some funds exceeding **200 bps** against a historical average of **0.7 bps**.
A footnote states that **"ETF prices may have incorporated information in a timelier
manner than NAV"** and that intraday NAV would give better premium estimates because NAV
can be based on outdated quotes. **Mechanisms are described, not causally identified.**

**BlackRock / SEC FIMSAC (July 2020).** Average **absolute stated premium/discount**,
January–February 2020 versus March–April 2020:

| fund | Jan–Feb 2020 | Mar–Apr 2020 |
|---|---:|---:|
| TLT | 0.13 % | 0.86 % |
| **LQD** | 0.13 % | **1.39 %** |
| **HYG** | 0.21 % | **1.06 %** |

The same deck explicitly documents **"The presence of lag effects in Net Asset Values"**
— daily NAV-based returns regressed on the **previous day's NAV** — and that **"Large
Premiums/Discounts Do Not Persist"**, with NAV *tending to lag*. **This is the issuer
itself documenting that its own NAV is stale.** Weigh it accordingly: it is
authoritative about BlackRock's own NAV construction and self-interested about the
conclusion that ETFs "performed as expected".

**Karmaziene & Terrada (2025).** US corporate bond ETFs, **2022–2023 tightening cycle**.
Rising yields **systematically widen discounts, but only in HIGH-YIELD ETFs**, a pattern
the authors read as **NAVs adjusting slowly because bonds trade infrequently, while ETFs
reprice immediately**. Abstract-level only; not read at full text; recorded as
**corroborating, not load-bearing**.

### B.2 What the verified prior actually says — stated plainly

> **The leading explanation in the verified literature is the stale-NAV alternative,
> not harvestable convergence.** The BIS, the issuer, and the most recent working paper
> all describe NAV as the *lagging* price and the ETF as the *leading* one.

The counterweight is Petajisto: after an explicit cross-sectional stale-pricing control,
**~100 bps of deviation remains**, with pre-cost abnormal returns. So the question is
genuinely two-sided — but the prior points at Case 2 (§C.7), and the honest expectation
for this lineage is that the identification gate is the gate that closes it.

That is precisely why the stale-NAV identification is the **first** gate and the
tradability question is second. It is also why an S0 that cannot construct the basis
correctly must HOLD rather than proceed.

### B.3 NAV mechanics — verified from issuer and exchange documentation

| fact | value | source |
|---|---|---|
| NAV determination | once daily, as of the **regularly scheduled close of the NYSE, normally 4:00 p.m. ET**, on each day the NYSE is open | iShares prospectus language |
| NAV formula | (total assets − total liabilities) / shares outstanding, rounded to the nearest cent | same |
| ETF closing price | the last exchange trade, which **need not occur exactly at 4:00 p.m.** | iShares product documentation |
| bond marks | evaluated / vendor prices; iShares states the **vendor price is not necessarily the valuation price** | iShares product page |
| NAV **dissemination** | **after** the close; documentation reachable here places reported NAV in roughly the **5:00 p.m. – 6:45 p.m. ET** window | Nasdaq MFQS guidance (NextShares) — **NOT iShares authority for HYG** |
| HYG | inception **2007-04-04**, iBoxx USD Liquid High Yield Index, 30-day median bid/ask **0.01 %** | iShares product page |
| LQD | inception **2002-07-22**, iBoxx USD Liquid Investment Grade Index, 30-day median bid/ask **0.01 %** | iShares product page |
| downloadable history | product pages expose a **"Data Download" (Excel)** and a holdings CSV. A **daily historical NAV series is not documented on the page itself**; the published premium/discount artefact reachable from documentation is a **quarterly PDF counting days at a premium/discount**, not a daily series | iShares product pages; iShares literature |

```
NAV_VALUATION_TIME          = 16:00 ET  (VERIFIED)
NAV_PUBLICATION_TIME        = evening of the same day, after the close.
                              NOT ESTABLISHED at issuer authority for HYG.  ~5:00-6:45
                              p.m. ET is third-party guidance for a different product
                              family and is NOT accepted as this lineage's timing fact.
EARLIEST_REALISTIC_SIGNAL_TIME = the EVENING of day t, after the close.
                                 => the earliest executable position is day t+1.
```

**The consequence is absolute and is not negotiable by design cleverness.** NAV is
struck at the same instant the ETF closes, but is *known* only hours later. **Any design
that enters at `close(t)` on a basis computed from `NAV(t)` is lookahead.** This lineage
will not do that (§C.6, §F.5).

---

## C. PROPOSED STUDY DESIGN

**Everything in this section is a proposal. Nothing is sealed, decided or established,
and §G blocks entry to S1.**

### C.1 The primary research question — audited and narrowed

The provisional wording supplied was:

> *"Does an ex-ante abnormal discount of a liquid bond ETF to its authoritative published
> NAV contain economically useful information about subsequent ETF market-price
> convergence, rather than being explained primarily by subsequent NAV catch-down?"*

**Audit.** It is close to right but conflates two claims — "economically useful" and
"rather than NAV catch-down" — into one sentence, and "economically useful" presumes the
answer to the first gate. The identification question must be answerable on its own,
and must be answerable *negatively* without any economic bar being involved. Proposed
replacement, split into a gate and a conditional:

```
PRIMARY (GATE 1 - IDENTIFICATION):
  Following an ex-ante abnormal discount of HYG to its issuer-published NAV, does the
  subsequent one-session convergence of the basis occur through a RISE IN THE ETF
  MARKET PRICE, or through a FALL IN NAV?

CONDITIONAL (GATE 2 - ECONOMIC USEFULNESS), evaluated only if GATE 1 identifies a
  material ETF-price component:
  Is that price component large enough to survive a predeclared round-trip cost?

PRIMARY_CLAIM_TYPE = REDUCED_FORM PREDICTIVE DECOMPOSITION.
                     Not causal. No dealer, AP or balance-sheet cause is claimed.
```

The question is **not** broadened into generic bond liquidity, Fed intervention, dealer
causality, credit risk premium, crisis alpha, or TSMOM improvement. §F is binding.

### C.2 Instrument selection — the exact reasoning

```
PRIMARY_ETF   = HYG   (iShares iBoxx $ High Yield Corporate Bond ETF)
SECONDARY_ETF = LQD   (iShares iBoxx $ Investment Grade Corporate Bond ETF)
                declared replication, NO RESCUE POWER
```

Evaluated structurally, before any outcome, on the criteria §9 of the task requires:

| | HYG | LQD | TLT / IEF | EMB |
|---|---|---|---|---|
| liquidity mismatch (the mechanism) | **strongest** — HY bonds trade least often | strong | **weakest** — Treasuries are the most liquid bond market on earth | strong |
| literature isolates the effect here? | **yes** — Petajisto names junk-bond ETFs; Karmaziene & Terrada find the discount-widening **only in high yield** | partly | no | not covered |
| issuer NAV authority | iShares | iShares | iShares | iShares |
| local price coverage | 2007-04 → 2026-06, 4,825 rows, **includes the GFC** | 2002-07 → 2026-06, 6,007 rows | 6,007 rows | **ABSENT** |
| tradability | 30-day median spread 0.01 % | 0.01 % | tight | wider |
| prior programme exposure | C-D October-2008 residual names HYG | Time-Series Value credit object | TSMOM core, TA lineage | none |
| policy confound | HY was **not** the direct target of the 2020 credit facilities | **LQD's flagship episode is directly confounded** — the Fed's PMCCF/SMCCF targeted investment grade | QE targets Treasuries directly | EM policy |

**Why HYG and not LQD**, despite LQD showing the *larger* March–April 2020 average
absolute dislocation (1.39 % vs 1.06 %): that single episode is exactly the one in which
the Federal Reserve announced facilities purchasing **investment-grade** corporate credit
and IG ETFs. LQD's largest observation is therefore the most policy-contaminated one in
the sample. Selecting the instrument whose headline episode is a direct policy
intervention on the underlying would import a confound at the instrument-selection step.
HYG carries the stronger mechanism and the weaker policy confound.

**Why not TLT/IEF**: the mechanism is a *liquidity mismatch*, and there is essentially
none between a Treasury ETF and the Treasury market. They are the natural negative
control and are **parked** (§E.1) rather than added, to keep the family at two funds.

**Why not EMB**: absent from the local panel entirely; it would require a full new price
acquisition on top of the NAV acquisition, for a third fund the frame does not need.

**Selection basis, stated for the record:** mechanism strength, literature localisation,
policy-confound exposure, coverage and tradability. **Not** literature-reported
profitability, and **not** any historical discount magnitude computed here — none was.

### C.3 The basis — exact definition

```
BASIS_DEFINITION
   b_t = ln( P_t / N_t )
   P_t = the RAW (UNADJUSTED) official closing market price of the ETF on day t
   N_t = the issuer-published per-share NAV struck as of 16:00 ET on day t
   b_t < 0  =>  DISCOUNT       b_t > 0  =>  PREMIUM
```

**Audited against issuer conventions, and the audit is what produces §G:**

- **Raw, never adjusted.** Both legs must be per-share values of the same object at the
  same instant. The published NAV is raw; therefore the price must be raw. The local
  panel is adjusted (§A.3) and is **unusable for this quantity**.
- **Ex-distribution alignment.** On an ex-date the raw price drops by the distribution
  and the raw NAV drops by the same distribution on the same date, so a raw-vs-raw basis
  is **unaffected**. This is the second reason to use raw on both legs: it makes the
  ex-date problem vanish rather than requiring a correction.
- **Time-of-day mismatch is real but small and structural.** NAV is struck at 16:00 ET;
  the last ETF trade need not be exactly at 16:00. That contributes a persistent,
  fund-specific component — which is exactly what the abnormal-basis transform removes
  (§C.4), not something the basis definition should try to fix.
- **The log form is retained.** It is symmetric in premium and discount, it makes the
  convergence decomposition exact and additive (§C.5), and at these magnitudes it is
  numerically indistinguishable from the simple ratio. No alternative is proposed,
  because the log form is what makes §C.5 an identity rather than an approximation.

**The basis definition is fixed here. It is not left to a builder.**

### C.4 The abnormal basis — ONE ex-ante transform, no search

Bond-ETF NAVs are struck on **bid-side evaluated prices**, so a structural, fund-specific
premium/discount level exists and is not the constraint the study is about. The raw basis
must therefore be de-meaned against its own history — causally.

```
ABNORMAL_BASIS_DEFINITION
   x_t = b_t - m_t

NORMALISATION_RULE
   m_t = MEDIAN{ b_s : s <= t-1 },  EXPANDING from the start of the fund's usable
         history, recomputed each day, using information available strictly before t.

MINIMUM_HISTORY_RULE
   x_t exists only once at least 250 trading days of b_s are available.
   Before that the observation is EXCLUDED (not imputed, not back-filled).

UPDATE TIMING
   b_t is knowable only in the EVENING of day t (NAV publication, §B.3).
   m_t uses data through t-1 only.
   => x_t is knowable in the evening of day t, and never earlier.
```

**Why expanding, and why the median.** *Expanding* has no window length, so there is no
window to search over — the single most common route to parameter mining in this design
is closed by construction. *Median* rather than mean because the object of study is
precisely the tail: a mean norm would be dragged by the stress episodes the study is
trying to measure, mechanically shrinking the feature exactly when it matters. *250
trading days* is one year, a calendar fact rather than a tuned number.

**Declared cost of this choice:** the norm drifts as the sample grows, and early
observations are normed against a shorter history than late ones. This is stated now,
before outcomes, and is not to be "fixed" later.

```
FEATURE_FORM      = CONTINUOUS.  x_t enters the estimand linearly.
THRESHOLD_IF_ANY  = NONE.  No threshold, no percentile grid, no "trade when discount
                    > 1 %". The continuous form removes the threshold question entirely
                    from the identification gate. A threshold appears, if ever, only in
                    GATE 2's position rule, and only as a declared consequence of the
                    cost bar (§C.9) - never as a searched parameter.
```

### C.5 The primary identification estimand

The log basis makes the decomposition an **exact identity**, not a model:

```
b_{t+1} - b_t  ==  r^P_{t+1} - r^N_{t+1}

   r^P = ln( P_{t+1} / P_t )   the ETF MARKET-PRICE return
   r^N = ln( N_{t+1} / N_t )   the NAV return
```

Convergence of the basis is therefore, by construction, *either* a price move *or* a NAV
move. The estimand estimates the two separately from the same regressor:

```
PRIMARY_IDENTIFICATION_ESTIMAND

   r^P_{t+1} = a_P + B_P * x_t + e            <-- B_P is the PRIMARY quantity
   r^N_{t+1} = a_N + B_N * x_t + e            <-- B_N is the mandatory CLASSIFIER

   Both OLS, same sample, same regressor, estimated SEPARATELY. No joint model, no
   instrument, no control variables, no interactions.

   SIGN CONVENTION: x_t < 0 is a discount.
      harvestable price convergence  =>  B_P < 0   (discount now, ETF price up next)
      stale-NAV catch-down           =>  B_N > 0   (discount now, NAV down next)
```

**`B_P` alone is the primary number** — it is the only component anyone can trade — and
the economic gate is applied to it. `B_N` is reported alongside as the **mandatory
classifier** that assigns the outcome to a case. Both come from one sample and one
regressor, so no selection occurs.

```
STALE_NAV_ALTERNATIVE_TEST  = B_N, estimated on the same x_t, reported always.
TRADABLE_PRICE_COMPONENT_TEST = B_P against the economic bar of §C.9.

PRICE_SHARE = B_P / (B_P - B_N) is reported as DESCRIPTIVE ONLY,
              PROMOTION_POWER = NONE, and is declared UNDEFINED when the denominator
              is small. It is a ratio whose interpretation flips with the sign of its
              denominator, so it must never carry a verdict.
```

That last exclusion is deliberate: the task requires a decomposition **whose
interpretation does not depend on the observed result**, and a ratio with a
sign-changing denominator fails that test. The pair `(B_P, B_N)` does not.

### C.6 Timing — stated to the hour

```
Signal becomes knowable at:   the EVENING of day t, after NAV publication (§B.3)
Earliest executable position: the OPEN of day t+1
Return measurement begins at: the OPEN of day t+1
Return measurement ends at:   the CLOSE of day t+1
```

```
PRIMARY_HORIZON = ONE TRADING SESSION: open(t+1) -> close(t+1).
```

**Why one session, and why it is the only defensible choice here.** The verified
literature locates the correction immediately after the observation: Petajisto's
real-time work operates intraday on five-minute bars; the BIS records discounts turning
to premiums within days; the issuer's own material records that large premiums and
discounts *do not persist*. A post-publication signal cannot reach the intraday window of
day *t*, so the first reachable window is the session of day *t+1* — and it is reachable
in full only by entering at the open. **No second horizon is proposed.** A 5-day horizon
is not retained even as a robustness cell: the task asks to prefer none, and adding one
would create a second shot on goal for no identification gain.

**The identification regression (§C.5) uses the same one-session horizon**, so the gate
and the trade measure the same object.

```
REALISTIC_ENTRY_POSSIBLE_WITH_EXISTING_DATA = NO.
```

The local panel has **no open prices and no raw prices** (§A.3). A `close(t+1)` entry
*would* be implementable with daily closes and would be strictly post-publication — but
it forfeits the session in which the verified literature places the correction, so it
would measure the residue rather than the effect. **Introducing a `close(t)` entry to
avoid the problem is lookahead and is forbidden (§F.5).** This is a data problem, and it
is named as such in §G rather than designed around.

### C.7 Outcome taxonomy — six distinct classes, defined before any outcome

```
A  STALE_NAV_ONLY
   B_N materially > 0 and B_P not materially < 0.
   The discount closes because NAV falls. A mechanical pricing discrepancy, not a
   harvestable edge, and NOT a statement that the ETF was mispriced.
   research_status = not_promoted

B  NO_CONVERGENCE_INFORMATION
   Neither B_P nor B_N is materially different from zero. The abnormal basis carries
   no information about which object moves next.
   research_status = not_promoted

C  PRICE_CONVERGENCE_PRESENT_BUT_NOT_ECONOMIC
   B_P materially < 0, but the implied per-event return reliably fails the cost bar.
   A real price component that cannot be harvested through this instrument.
   research_status = not_promoted, reason TARGET_MARGIN_EXCLUDED

D  LOW_POWER / UNRESOLVED
   The interval spans the bar. Neither useful nor excluded. TERMINAL.
   research_status = unresolved

E  SUPPORTED_PRICE_CONVERGENCE_EDGE
   B_P materially < 0, the cost bar is cleared, and the fragility diagnostic passes.
   research_status = supported.  Evidence ceiling `supported` - never confirmed.

F  IDENTIFICATION / DATA FAILURE
   NAV publication timing cannot be pinned, NAV alignment fails, the series is revised,
   a structural break (index change, fund restructuring) invalidates the basis, or the
   price/NAV pair cannot be put on a common raw footing.
   research_status = unresolved, with the MANDATORY qualifier
   IDENTIFICATION_INSUFFICIENT_FOR_THE_CLAIM.  Never reported as plain `unresolved`.
```

"Failed" is not a class and is not a permitted verdict word. **Class F is live right
now**: §G is an instance of it, caught before any data was acquired.

### C.8 The cheap falsification gate — ordered, two gates only

```
GATE 1 - IDENTIFICATION  (runs first, closes the lineage on its own)
   Estimate B_P and B_N on HYG over the usable sample. One regression pair.
   If the result is Class A or Class B, the lineage CLOSES before any strategy
   object is constructed. No position, no P&L, no portfolio.

GATE 2 - ECONOMIC USEFULNESS  (only if GATE 1 yields a material B_P)
   Apply the cost bar of §C.9 to the implied one-session return.

The declared secondary (LQD) is estimated once, reported alongside, and has NO RESCUE
POWER: an LQD result never changes the HYG verdict.
No parameter family. No optimiser. No portfolio integration in either gate.
```

### C.9 Cost model and economic materiality

```
TRANSACTION_COST_RULE  (PROPOSED - OWNER DECISION REQUIRED)
   FIXED CONSERVATIVE ONE-WAY COST = 5 bps, round trip 10 bps.
```

**Audit of the programme's 2 bps convention.** The 2 bps one-way convention was
calibrated for month-end rebalancing of a broad ETF book in ordinary conditions. HYG's
**documented 30-day median bid/ask is 0.01 %** — a 0.5 bp half-spread — so 2 bps is
*conservative in calm markets*. But this study's entire economic content sits in stress
episodes, and the verified record shows HYG's absolute dislocation rising fivefold
between calm and March–April 2020 while quoted spreads on credit ETFs widen by an order
of magnitude in exactly those weeks. **A single calm-market spread assumption is
inadequate for a claim that lives in the tail**, and 2 bps would flatter the strategy
precisely where it trades most.

5 bps one-way is therefore proposed: a single fixed conservative number, applied
uniformly, **not** a sensitivity grid and **not** a post-outcome rescue. Because setting
a cost convention is a material methodology decision (vNext §10), the number is
**proposed, not adopted** — it is Aaron's.

```
ECONOMIC_MATERIALITY_RULE  (PROPOSED - OWNER DECISION REQUIRED)
   M1  |B_P| must imply at least ONE ROUND TRIP of expected one-session ETF price
       convergence per 1.00 % of abnormal discount:
           |B_P| >= 0.10      (i.e. >= 10 bps of price return per 1 % of discount)
       The bar comes from the COST (10 bps round trip). The 1 % unit comes from the
       literature's own scale - Petajisto's post-stale-control band is about 100 bps -
       and fixes the UNIT only, never the bar.
   M2  the programme's existing +0.30 annualised Sharpe floor (Aaron's C-A OD-1),
       applied to a calendarised series of the predeclared position, exactly as the
       CTA-EDGE-01-TA contract did.
   Classification uses the INTERVAL against these bars, never the point estimate.
```

```
POSITION SIDE = DISCOUNT SIDE ONLY.
```

The mechanism is asymmetric: a discount arises when *redemption* capacity is scarce and
sellers pay for immediacy — that is the liquidity-provision story. A premium arises when
*creation* capacity is scarce, which is a different constraint with different borrow
economics on the short leg. The task permits framing one side where the mechanism and
implementation support asymmetry, and they do. **The identification regression is
estimated on the FULL sample (it is symmetric and uses every observation); only the
GATE 2 position is one-sided.** That separation is fixed now, before outcomes.

### C.10 Effective sample — rows are not events

```
EXPECTED_DAILY_ROWS        = about 4,800 for HYG (2007-04 -> 2026-06), less the
                             250-day minimum-history burn-in => roughly 4,550 usable.
EXPECTED_EFFECTIVE_EPISODES = 15-25 economically independent abnormal-discount episodes,
                             of which perhaps 5 are extreme.
                             *** INHERITED FROM THE DISCOVERY MAP AS ADVISORY AND
                             *** NOT VERIFIED HERE. Verifying it requires computing the
                             *** basis, which this stage forbids. It is a PLANNING
                             *** RANGE, not a fact.
YEAR BLOCKS                = about 20 calendar years - the inference unit (§C.12).
```

**Stated plainly, before any outcome:** the identification regression has thousands of
daily rows, but the daily observations are strongly autocorrelated and the economically
relevant region is a tail visited a few times a decade. **Thousands of rows are not
thousands of independent tests.** If a positive result turns out to rest mainly on 2008
and 2020, that is a fragility finding and will be reported as one, not as a sample of
4,800.

### C.11 Main risks, named now

```
MAIN_IDENTIFICATION_RISK = STALE NAV. The verified prior (§B.2) says NAV lags. If the
   basis converges through NAV, the discount is an optical artefact and there is nothing
   to trade. Secondary: policy endogeneity - in March 2020 the discount and the
   subsequent return share a common cause (the Fed's announcement), and that is ONE
   episode, not evidence.

MAIN_DATA_RISK = the price/NAV footing (§G). Beyond it: whether the issuer's daily NAV
   history is retrievable at all as a daily series (the documented artefact is a
   QUARTERLY count of days at a premium/discount, not a daily series); whether published
   NAV is ever revised; HYG's presence among the C-D October-2008 cross-vendor residual
   names; and index or fund structural changes across a 19-year window.

MAIN_IMPLEMENTATION_RISK = the signal is knowable only in the evening, so the whole
   claim depends on an OPEN-price execution that the local panel cannot express. A
   close(t+1) fallback is implementable but measures the residue after the session in
   which the literature places the correction.

CRISIS_CONDITIONAL_RISK = the sleeve BUYS a credit ETF at a discount precisely when
   liquidity is disappearing, discounts are widening, and canonical trend is profiting
   from short risk. Convergence is mechanically bounded but the path runs through the
   discount widening further first. Any future portfolio study MUST inspect the declared
   GFC, COVID and other stress windows and may NOT rely on unconditional correlation.
   This is the VRP lesson and it is recorded now. NO PORTFOLIO TEST EXISTS IN S0.
```

```
THIS IS NOT A CRISIS DIVERSIFIER and must never be described as one.
Its first role is MARKET-STRUCTURE / LIQUIDITY-PROVISION INFORMATION, not protection.
```

### C.12 Uncertainty, fragility and multiplicity

```
UNCERTAINTY_PLAN  (ONE framework)
   Calendar-year block bootstrap: resample complete calendar years with replacement,
   B = 10,000, 95 % percentile interval, on B_P and on B_N from the same draws.
   Years, not days: a year block absorbs daily autocorrelation, episode clustering and
   regime dependence in ONE unit, and the dependence that matters here is regime-level.
   NOT STACKED: no HAC, no Newey-West, no second bootstrap family, no fund clustering
   (there is one primary fund), no additional robustness procedure.

FRAGILITY (exactly one diagnostic)
   Leave-one-calendar-year-out on B_P. For a would-be Class E, every LOYO estimate must
   retain the predicted sign. This exists because the effective sample is a handful of
   episodes and a result one year can remove is not a result.

MULTIPLICITY_PLAN
   ONE primary ETF (HYG) · ONE primary horizon (one session) · ONE primary estimand
   (B_P, with B_N as the mandatory classifier). m = 1, no correction, because no
   selection across cells occurs.
   LQD  = declared secondary replication, PROMOTION_POWER = NONE, NO RESCUE POWER.
   PRICE_SHARE, the leg descriptives and any tabulation = PROMOTION_POWER = NONE.
   NO signal definition is left unresolved for a builder to choose.
```

### C.13 Distinctness

```
DISTINCT_FROM_TSMOM            = YES
DISTINCT_FROM_VRP              = YES
DISTINCT_FROM_CRASH_DEFENCE    = YES
DISTINCT_FROM_CARRY            = YES
DISTINCT_FROM_TREASURY_AUCTION = YES
```

The distinguishing information is **a second price for the same economic claim**: the
ETF market price and the issuer's authoritative NAV. NAV is not in the price panel and
**cannot be reconstructed from ETF return history alone** — which is the task's own test
for whether this deserves promotion, and it passes it. Specifically: canonical TSMOM is a
monthly sign composite of past returns; VRP was listed VIX futures; crash defence used
the book's own realised-volatility and dispersion percentiles; Time-Series Value used
fundamental cheapness against own history; carry harvests roll-down on a held position;
CTA-EDGE-01-TA used an exogenous Treasury issuance calendar on duration ETFs and is
closed pre-outcome. None of them sees a NAV. No-trade-band logic is a position-management
rule, not an information source.

---

## D. NOT-YET-TESTED CLAIMS

Unmeasured in this programme. None may be cited as fact.

1. That an abnormal HYG discount predicts **anything** at any horizon. Unmeasured.
2. Whether convergence runs through the ETF price or through NAV. **This is the whole
   question**, and the verified prior points at NAV.
3. The size of any price component, and whether it clears any cost bar.
4. Whether a price component, if present, survives outside 2008 and 2020.
5. That the quoted 0.01 % median spread is attainable in the stress states where the
   mechanism lives. It almost certainly is not.
6. That AP or dealer balance-sheet constraints *cause* anything here. Not claimed,
   not testable with daily price and NAV.
7. The 15–25 episode count. Inherited advisory, unverified (§C.10).
8. That the issuer's daily NAV history is retrievable, complete, unrevised and free of
   structural breaks over 2007–2026.
9. Anything about portfolio relevance to canonical TSMOM.

---

## E. PARKED QUESTIONS

- **E.1 TLT / IEF as a negative control.** The right shape — a near-zero liquidity
  mismatch should show a near-zero price component — but it would make three funds where
  the task allows two, and the within-fund `(B_P, B_N)` decomposition already carries the
  identification. Parked, not rejected.
- **E.2 Cross-sectional breadth** (the fraction of bond ETFs at an abnormal discount) as
  an intermediation-stress *state variable* rather than a tradable signal. A genuinely
  different claim with a different evidential standard. Parked.
- **E.3 Intraday / iNAV.** The BIS notes intraday NAV would give better premium
  estimates, and Petajisto's real-time work is intraday. This is where the question can
  actually be identified cleanly — and it is a different data universe. Parked as the
  natural successor if the daily version is Class A or F.
- **E.4 EMB.** Absent locally; a third acquisition for no framing gain. Parked.
- **E.5 The premium side.** Framed out of GATE 2 by the asymmetry argument (§C.9).
  Parked with its reason recorded.
- **E.6 Creation/redemption basket data.** Todorov's under-3 % basket overlap is the
  mechanism's own frontier. Not free, not needed, parked.

---

## F. FORBIDDEN INTERPRETATIONS

Binding on every later document, seat and stage in this lineage.

1. **Never a causal claim about APs, dealers or balance-sheet capacity.** Daily price and
   NAV cannot identify that. The BIS describes mechanisms; it does not identify them.
2. **Never "the ETF was mispriced".** A discount that closes through NAV means the ETF
   price was the *better* price. Class A is a statement about NAV, not about the ETF.
3. **Never crisis diversification.** The expected conditional risk runs the other way
   (§C.11).
4. **Never an improvement to canonical TSMOM.** No portfolio quantity is computed or
   authorised by this frame.
5. **Never a `close(t)` entry on a `NAV(t)` signal.** NAV is published after the close.
   That is lookahead, it is the single easiest mistake in this design, and it is banned
   outright rather than left to care.
6. **Never a generic bond-liquidity, credit-premium or Fed-intervention claim.** The
   object is one ETF's basis to its own NAV.
7. **Never import a literature Sharpe as programme evidence.** Petajisto's abnormal
   returns are pre-cost and the paper says they are cost-sensitive.
8. **Never treat BlackRock's material as independent.** It is issuer documentation —
   authoritative about NAV construction, self-interested about conclusions.
9. **Never treat daily rows as independent tests** (§C.10).
10. **Evidence ceiling is `supported`** — the ETF price panel is burned, and a new NAV
    series does not launder it.
11. **"Failed" is not a verdict.** The permitted outcomes are A–F of §C.7.

---

## G. THE BLOCKER — why this frame is HOLD

```
S0_FRAME_STATUS = HOLD
```

**One blocking issue, stated once:**

> **The lineage has no usable price input.** The basis (§C.3) requires a **raw,
> unadjusted** ETF close aligned to the 16:00 ET NAV strike, and a realistic
> post-publication entry (§C.6) requires an **open** price. The local panel is
> **dividend-adjusted closes only** — verified at source in `src/fetch_data.py`
> (`auto_adjust=True`) — with no raw series and no OHLC. `log(adjusted close /
> published NAV)` is not a basis; it is a cumulative-distribution artefact.

Two consequences, both of which the task instructs be returned as HOLD rather than
designed around:

```
POINT_IN_TIME_RECONSTRUCTIBLE = HOLD
   NAV valuation time is VERIFIED at 16:00 ET. NAV PUBLICATION time is NOT established
   at issuer authority for HYG - the ~5:00-6:45 p.m. ET window reachable here is
   third-party guidance for a different product family. Task §7: if exact publication
   timing cannot be established, HOLD. Additionally, the daily NAV history itself is
   documented only as a "Data Download"; the premium/discount artefact reachable from
   iShares literature is a QUARTERLY count of days, not a daily series.

REALISTIC_ENTRY_POSSIBLE_WITH_EXISTING_DATA = NO
   No open prices and no raw prices exist locally. Task §14: return DATA / EXECUTION
   DESIGN HOLD rather than introducing lookahead.
```

**Both resolve through ONE Owner data decision**, which is why this is one blocker and
not three:

```
THE SINGLE DECISION
  Authorise acquisition, for HYG (and LQD as the declared secondary), of:
    1. RAW (unadjusted) daily OHLC for the ETF - which supplies both the raw close the
       basis needs and the open the entry needs;
    2. the issuer's DAILY published NAV history;
    3. the issuer's own documented statement of WHEN that NAV is published, from the
       prospectus or SAI - the timing fact this stage could not establish.
  Acquisition is NOT authorised by this document and none was performed.
```

Everything else in this frame is complete and does not depend on that decision: the
question, the instrument choice and its reasoning, the basis, the abnormal-basis
transform, the estimand, the horizon, the taxonomy, the cost and materiality proposals,
the inference plan and the forbidden interpretations are all fixed here.

**Two items additionally require an Owner decision at S1 and are flagged, not taken:**
the 5 bps cost convention (§C.9) and the +0.30 M2 floor carried over from C-A OD-1.

---

## H. Design exposure

```
FABLE_DESIGN_EXPOSED = YES
ASTRA_DESIGN_EXPOSED = NO
```

**Claude Fable 5.1** materially contributed the candidate family (`BOND_ETF_NAV_BASIS`,
discovery map F3), the stale-NAV alternative, the price-versus-NAV decomposition concept,
the candidate ETF set, and the portfolio-risk warning. It is design-exposed for this
lineage and may never later be presented as a fresh blind certifier of it.

**GPT-6 Astra did NOT materially design this candidate in round 1** and is **not**
marked design-exposed. Being present in a discovery round is not design exposure. If
Astra is later used to challenge or redesign this lineage, exposure is recorded **then**.

No row is written to `ops/REVIEWER_EXPOSURE_LOG.md` by this document: writing to the
reviewer-exposure ledger is governance execution, and the rows are written when the
lineage proceeds past this HOLD.

---

## Appendix — sources read

| # | source | how read |
|---|---|---|
| 1 | Petajisto, *Inefficiencies in the Pricing of Exchange-Traded Funds*, FAJ 73(1) 2017 | full PDF, text-extracted from the author's site |
| 2 | Todorov, *The anatomy of bond ETF arbitrage*, BIS Quarterly Review, Mar 2021 | BIS PDF |
| 3 | BlackRock EII Global Research, *Pricing and Liquidity of Fixed Income ETFs in the Covid-19 Crisis of 2020*, Jul 2020, SEC FIMSAC | full PDF, text-extracted from sec.gov |
| 4 | Karmaziene & Terrada, *Fast ETFs, Slow Bonds*, SSRN 5591173, 11 Oct 2025 | **abstract level only** — corroborating, not load-bearing |
| 5 | iShares product pages for HYG and LQD; iShares prospectus NAV language; iShares historical premium/discount literature | fetched |
| 6 | Nasdaq MFQS / NextShares price-display guidance (NAV dissemination window) | fetched — **explicitly NOT accepted as issuer authority for HYG** |
| 7 | `src/fetch_data.py`, `data/fetch_metadata.csv`, `SAMPLE_REUSE.md`, `PROJECT_STATE.md`, `QUANT_WORKFLOW_VNEXT.md`, `research/TSMOM_PROGRAMME_HANDOFF_2026-09.md`, the CTA discovery map F3 | repository, read directly |

**Not read at primary source, and therefore not load-bearing:** Pan & Zeng (2019);
Haddad, Moreira & Muir (2021); Dannhauser; Kolotiy (a student paper). Each is recorded
as context only.

```
END OF S0 FRAME. HOLD. NO SEAL. NO BUILD. NO FETCH. NO RUN.
```
