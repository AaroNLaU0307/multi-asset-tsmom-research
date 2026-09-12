# Time-Series Value — Phase A data record

**Study family:** `FINANCIAL_ASSET_TIME_SERIES_VALUE` · **Anchor:** `EXPANDING_OWN_HISTORY`
**Phase:** A — bounded point-in-time data acquisition and verification
**Date:** 2026-09-13 · **Seat:** Claude Opus 5, Main Agent
**Machine inventory:** [`VALUE_DATA_INVENTORY.json`](VALUE_DATA_INVENTORY.json)

```
VALUE_DATA_PIT_READINESS = BLOCKED
S1 NOT ENTERED
TARGET_OUTCOMES_COMPUTED = NO
```

This is a data-feasibility finding, not a research finding. Nothing was joined to
an ETF return series; no position, PnL, Sharpe, correlation or premise statistic
exists.

## What survived

| instrument | valuation object | source | coverage | PIT class |
|---|---|---|---|---|
| **SPY** | real earnings yield (inverse CAPE) | Shiller `ie_data.xls` | 1871.01 → 2026.09, monthly | `PIT_DATA_ACQUIRED_BUT_LIMITED` |
| **TLT** | real yield, construction **B** (market) | FRED `DFII20` | 2004-07-27 → 2026-09-10, daily | `PIT_READY` |
| **TLT** | real yield, construction **A** (nominal − expected inflation) | FRED `DGS20` + `EXPINF20YR` | 1962 / 1982 → 2026-09, daily / monthly | `PIT_FEASIBLE_WITH_DECLARED_LAG` |

`DFII30`, `DGS30` and `EXPINF10YR` were also retained as declared alternates.

**S1 recommendation for TLT, on causal validity and interpretability only — not
on any outcome:** prefer **construction B** (`DFII20`). It is a market-observed
quote, published next business day, never revised, and its 20-year maturity is
the closest available match to TLT's 20+ year mandate, so a one-business-day lag
is sufficient and no vintage problem arises. Construction A reaches back to 1982
but its second leg, `EXPINF20YR`, is a *model-based* Cleveland Fed estimate whose
entire history moves when the model is re-estimated — a declared lag fixes
release timing but not revision. The cost of preferring B is that the evaluation
cannot start before roughly 2005, and TIPS liquidity was thin early and acutely
distorted in 2008-09.

**The SPY limitation must not be glossed.** Shiller's history is *reconstructed*,
not vintage: trailing earnings are revised after the fact and the real series is
deflated with the current CPI vintage. A declared publication lag makes the
construction causal with respect to *release timing* only. A CAPE value dated
1995-03 is today's estimate of 1995-03, not what an investor could have computed
then. This is classified `PIT_DATA_ACQUIRED_BUT_LIMITED` and must be carried into
any preregistration in those words.

**Provenance trap, verified this retrieval.** The legacy Yale URL
`econ.yale.edu/~shiller/data/ie_data.xls` still resolves but serves a **stale copy
ending 2023.09**. Only the `shillerdata.com` link recorded in the inventory is
current. Anyone reproducing this must use the recorded URL and check the hash.

## What is blocked, and why

| object | status | reason |
|---|---|---|
| **LQD** IG OAS | `PIT_NOT_RELIABLY_FEASIBLE` | **Licensing.** FRED serves ICE BofA OAS under terms stating *"Reproduction of this data in any form is prohibited except with the prior written permission of ICE Data Indices"*, internal use only. Consistent with that, the endpoint returns only a rolling window — 795 rows, 2023-09-12 → 2026-09-10 — and ignores `cosd`/`coed`. |
| **HYG** HY OAS | `PIT_NOT_RELIABLY_FEASIBLE` | Same licence, same rolling window. |
| **UUP** real FX vs fixed USDX weights | `PIT_NOT_RELIABLY_FEASIBLE` | Nominal FX legs are clean back to 1971. The **CPI legs are not**: Japan is discontinued at 2021-06 across every FRED variant tried, and UK / Canada / Sweden / Switzerland all stop at 2025-03/04. Only the euro area is current. OECD's public SDMX API returned HTTP 403. |
| **FXY** bilateral JPY real FX | `PIT_NOT_RELIABLY_FEASIBLE` | Fails on the Japan CPI leg alone, as above. |

Roughly three years of credit spread cannot support an `EXPANDING_OWN_HISTORY`
anchor with a warm-up, and the licence independently blocks redistributing a
snapshot for reproducibility. The probe copies of both ICE series were **deleted,
not retained**. Per §A8 nothing was substituted: no BIS effective index, no
price-based proxy, no widened universe.

## Why this is BLOCKED rather than a reduced universe

Four of six accepted objects failed, and they are not scattered — they are the
**entire credit sleeve and the entire FX sleeve**. What survives is `{SPY, TLT}`:
two instruments across two asset classes. That is still coherent as a *concept*,
but it is a materially different research object from the cross-asset value family
S0 accepted, and the FULL-stage target is `INCREMENTAL_PORTFOLIO_BENEFIT` against
a multi-asset TSMOM book — a question a two-instrument sleeve answers much more
weakly. Under the Phase A rule that is a material change to the meaning of the
factor family, so S1 was not entered.

## The smallest decision required

One Owner decision unblocks this. The options, neutrally:

1. **Narrow the family explicitly** to `{SPY, TLT}` — equity and duration value
   only — renaming the object so no later reader mistakes it for a cross-asset
   value study. Cheapest, honest, and executable today; delivers a weaker
   diversification test.
2. **Authorize licensed sources** for credit OAS and a current foreign CPI
   (entitled ICE/Bloomberg feed; national statistics offices or an OECD API key).
   Restores the full six-instrument design; costs money and time.
3. **Redefine the credit object explicitly** to a public, unrestricted spread with
   real history — FRED `BAA10Y` (1986-01-02 → 2026-09-10) and/or `AAA10Y`
   (1983-01-03 →). This is **not** an OAS and references Moody's seasoned
   corporate yields rather than the LQD/HYG indices, so it is a *scientific scope
   change requiring your explicit approval*, not a substitution I may make. It
   would restore a credit sleeve but still leaves FX blocked.

**Recommendation, on mechanism and coherence only:** option 1 if you want a
defensible study now, option 2 if the cross-asset claim is the point. Option 3 is
legitimate only as an openly declared redefinition, and even then FX stays
blocked, so it cannot by itself restore the original family.

No option has been adopted. No proxy was invented. No preregistration exists.
