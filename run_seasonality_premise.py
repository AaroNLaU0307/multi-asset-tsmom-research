"""Step 1 — Seasonality premise test (DESCRIPTIVE, read-only).

Computes the pre-registered 18-cell family (research/seasonality/PREREGISTRATION.md):
3 calendar effects (turn-of-month, Halloween/Sell-in-May, Monday) x (pooled + 5 sleeves),
each with: Δ mean daily return (bps), Newey-West HAC t-test (primary p), moving-block
bootstrap CI (cross-check), effect-appropriate stability + concentration checks, and
BH-FDR across the whole family. No positions / P&L / tuning.

Run:  python run_seasonality_premise.py
"""

from __future__ import annotations

import sys

import pandas as pd

import config
import universe
from src import fetch_data, seasonality as seas

EFFECT_LABEL = {"E1_TOM": "E1 Turn-of-Month", "E2_Halloween": "E2 Halloween/Sell-in-May",
                "E3_Monday": "E3 Monday"}
PRIOR_LABEL = {"E1_TOM": "TOM > non-TOM (+)", "E2_Halloween": "winter > summer (+)",
               "E3_Monday": "Monday < rest (-)"}


def _fmt(x, nd=2):
    return "nan" if pd.isna(x) else f"{x:+.{nd}f}"


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    prices, _ = fetch_data.fetch_universe(force=False)
    px = prices[universe.TICKERS]
    rets = seas.balanced_returns(px)
    win_start, win_end, ndays = rets.index.min().date(), rets.index.max().date(), len(rets)

    df, e2_tables = seas.run_family(px)
    df.to_csv(config.SEASONALITY_PREMISE_CSV, index=False)
    # per-year E2 spreads (pooled + per sleeve) stacked into one CSV
    e2_all = pd.concat({k: v for k, v in e2_tables.items()}, names=["scope"]).reset_index()
    e2_all.to_csv(config.SEASONALITY_PERYEAR_CSV, index=False)

    # ----------------------------- console ----------------------------- #
    print("\n=============  SEASONALITY — STEP 1 PREMISE (descriptive)  =============")
    print(f"  balanced daily window: {win_start} -> {win_end}  ({ndays} trading days, 17 assets)")
    print(f"  family: {len(df)} tests (3 effects x [pooled + 5 sleeves]); BH-FDR q={config.SEAS_FDR_Q}; "
          f"magnitude bar={config.SEAS_MAGNITUDE_BPS:.0f} bps/day")
    cols = ["effect", "scope", "delta_bps", "t_hac", "p_raw", "p_bh", "fdr_reject",
            "pass_magnitude", "pass_stable", "pass_concentration", "CONFIRMED"]
    with pd.option_context("display.width", 200, "display.max_rows", 30,
                           "display.float_format", lambda v: f"{v:.3f}"):
        print(df[cols].to_string(index=False))

    n_conf = int(df["CONFIRMED"].sum())
    print(f"\n  CONFIRMED cells: {n_conf}")
    if n_conf:
        for _, r in df[df["CONFIRMED"]].iterrows():
            print(f"    - {r['effect']} / {r['scope']}: Δ={r['delta_bps']:+.2f} bps, p_bh={r['p_bh']:.3f}")

    # ----------------------------- report ------------------------------ #
    md = _build_report(df, e2_tables, win_start, win_end, ndays)
    config.SEASONALITY_PREMISE_MD.write_text(md, encoding="utf-8")
    print(f"\n  report: {config.SEASONALITY_PREMISE_MD}")
    print(f"  family CSV: {config.SEASONALITY_PREMISE_CSV}")
    print(f"  E2 per-year CSV: {config.SEASONALITY_PERYEAR_CSV}")


def _verdict_word(confirmed: bool) -> str:
    return "**CONFIRMED**" if confirmed else "not confirmed"


def _build_report(df, e2_tables, win_start, win_end, ndays) -> str:
    bar = config.SEAS_MAGNITUDE_BPS
    L = ["# Seasonality — Step 1 premise test (descriptive)", "",
         "*DESCRIPTIVE only — mean daily return on effect-days vs non-effect-days. No positions, no "
         "P&L, no tuning. Only the pre-registered effects "
         "([`PREREGISTRATION.md`](PREREGISTRATION.md)) are tested; the family, the BH-FDR plan, the "
         f"{bar:.0f} bps/day magnitude bar, and the decision rule were all fixed before any "
         "computation.*", "",
         f"Balanced daily window **{win_start} → {win_end}** ({ndays} trading days, equal-weight over "
         "the 17 always-present assets). Primary p-value = Newey–West HAC *t* "
         f"(lag {config.SEAS_HAC_LAG}); cross-check = moving-block bootstrap 95% CI "
         f"(block {config.SEAS_BLOCK_LEN}, {config.SEAS_BOOTSTRAP_N:,} resamples, seed "
         f"{config.RANDOM_SEED}). **BH-FDR q = {config.SEAS_FDR_Q}** across all {len(df)} cells.", ""]

    # headline family table
    L += ["## Family results (Δ in bps/day; raw vs FDR-adjusted)", "",
          "| effect | scope | Δ bps | HAC t | p_raw | p_BH | FDR sig? | |Δ|≥bar | stable | not-conc | **verdict** |",
          "| --- | --- | ---: | ---: | ---: | ---: | :--: | :--: | :--: | :--: | :--: |"]
    for _, r in df.iterrows():
        L.append(
            f"| {r['effect']} | {r['scope']} | {_fmt(r['delta_bps'])} | {_fmt(r['t_hac'])} | "
            f"{r['p_raw']:.3f} | {r['p_bh']:.3f} | {'Y' if r['fdr_reject'] else '·'} | "
            f"{'Y' if r['pass_magnitude'] else '·'} | {'Y' if r['pass_stable'] else '·'} | "
            f"{'Y' if r['pass_concentration'] else '·'} | "
            f"{'**CONFIRMED**' if r['CONFIRMED'] else 'no'} |")
    L.append("")

    # per-effect detail
    for eff in seas.EFFECTS:
        sub = df[df["effect"] == eff]
        L += [f"## {EFFECT_LABEL[eff]} — prior: {PRIOR_LABEL[eff]}", ""]
        if eff in ("E1_TOM", "E3_Monday"):
            L += ["Sub-period stability (Δ bps/day) and daily concentration check:", "",
                  "| scope | Δ full | H1 | H2 | T1 | T2 | T3 | Δ winsor | top-1 day share | FDR sig? |",
                  "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--: |"]
            for _, r in sub.iterrows():
                L.append(
                    f"| {r['scope']} | {_fmt(r['delta_bps'])} | {_fmt(r['H1_bps'])} | {_fmt(r['H2_bps'])} | "
                    f"{_fmt(r['T1_bps'])} | {_fmt(r['T2_bps'])} | {_fmt(r['T3_bps'])} | "
                    f"{_fmt(r['delta_winsor_bps'])} | {_fmt(r['share_top1_eff_day'], 2)} | "
                    f"{'Y' if r['fdr_reject'] else '·'} |")
        else:  # E2
            L += ["Year-level stability (per-year winter−summer sign count) and year jackknife "
                  "(Δ bps/day) — *inherently low-powered: ~19 annual cycles*:", "",
                  "| scope | Δ full | yrs +/total | LOO min (yr) | LOO max (yr) | drop top-2 yrs | FDR sig? |",
                  "| --- | ---: | :--: | ---: | ---: | ---: | :--: |"]
            for _, r in sub.iterrows():
                L.append(
                    f"| {r['scope']} | {_fmt(r['delta_bps'])} | {int(r['years_positive'])}/{int(r['years_total'])} | "
                    f"{_fmt(r['loo_min_bps'])} ({int(r['loo_min_year'])}) | "
                    f"{_fmt(r['loo_max_bps'])} ({int(r['loo_max_year'])}) | "
                    f"{_fmt(r['drop_top2_bps'])} | {'Y' if r['fdr_reject'] else '·'} |")
        L.append("")
        # one-line verdict per scope
        verdicts = []
        for _, r in sub.iterrows():
            why = []
            if not r["pass_fdr"]:
                why.append("fails BH-FDR")
            if not r["pass_sign"]:
                why.append("sign opposes prior")
            if not r["pass_magnitude"]:
                why.append(f"|Δ|={abs(r['delta_bps']):.1f}<{bar:.0f} bps")
            if not r["pass_stable"]:
                why.append("unstable")
            if not r["pass_concentration"]:
                why.append("concentration-driven")
            verdicts.append(f"- **{r['scope']}**: {_verdict_word(r['CONFIRMED'])}"
                            + ("" if r["CONFIRMED"] else f" — {', '.join(why)}."))
        L += verdicts + [""]

    # overall verdict
    n_conf = int(df["CONFIRMED"].sum())
    L += ["## Overall verdict", ""]
    if n_conf:
        cells = ", ".join(f"{r['effect']}/{r['scope']}" for _, r in df[df["CONFIRMED"]].iterrows())
        L += [f"**CONFIRMED** on {n_conf} cell(s): {cells}. At least one pre-registered effect clears "
              "all five gates (BH-FDR, sign, magnitude, stability, non-concentration) → proceed to "
              "Step 2, scoped to those sleeves."]
    else:
        n_fdr = int(df["fdr_reject"].sum())
        n_mag = int(df["pass_magnitude"].sum())
        L += [f"**NOT confirmed — clean negative.** Of {len(df)} pre-registered cells, "
              f"{n_fdr} survive BH-FDR and {n_mag} clear the {bar:.0f} bps/day magnitude bar, but **0** "
              "clear all five gates jointly (FDR **and** sign **and** magnitude **and** stability "
              "**and** non-concentration). Per the pre-registered decision rule this is a clean "
              "negative — consistent with the portfolio's honest-falsification record. **Do not build "
              "the overlay.** No Step 2."]
    L.append("")
    return "\n".join(L)


if __name__ == "__main__":
    main()
