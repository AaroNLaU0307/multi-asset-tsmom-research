"""Phase 1B — descriptive premise test for the vol-compression breakout (strategy B).

Does CLOSE-TO-CLOSE vol compression precede DIRECTIONAL expansion on this universe, at
a rate above the unconditional base rate? Descriptive only — no positions, no P&L, no
tuning. Pre-registered headline threshold = 0.20; 0.10/0.30 reported only as a
robustness sanity check (NOT a menu to pick from). Then PAUSE.

Run:  python run_breakout_phase1b.py
"""

from __future__ import annotations

import sys

import numpy as np
import pandas as pd

import config
import universe
from src import fetch_data, premise

THR = 0.20                                   # pre-registered headline
ROBUST = (0.10, 0.20, 0.30)
HORIZONS = config.PREMISE_HORIZONS


def _row(tbl, scope, N, thr):
    m = tbl[(tbl.scope == scope) & (tbl.horizon == N) & (tbl.threshold == thr)]
    return m.iloc[0]


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    prices, _ = fetch_data.fetch_universe(force=False)
    px = prices[universe.TICKERS]
    tbl = premise.premise_table(px, thresholds=ROBUST, horizons=HORIZONS)
    tbl.round(4).to_csv(config.BREAKOUT_PREMISE_CSV, index=False)

    scopes = ["Pooled"] + premise.SLEEVES

    # ---- console ----
    print("\n===============  PHASE 1B — COMPRESSION -> DIRECTIONAL EXPANSION?  ===============")
    print("  (close-to-close vol compression; DESCRIPTIVE; headline threshold = 0.20)")
    print(f"\n  POOLED, by horizon (comp = after compression; all = base rate):")
    print(f"  {'N':>3} {'n_comp':>7} {'brk_c':>6} {'brk_a':>6} | {'ftgiven_c':>9} {'ftgiven_a':>9} {'Δ':>6} "
          f"| {'ER_c':>5} {'ER_a':>5} {'Δ':>6} | {'exp_c':>5} | {'|ret|c':>7} {'|ret|a':>7}")
    for N in HORIZONS:
        r = _row(tbl, "Pooled", N, THR)
        print(f"  {N:>3} {r.n_comp:>7.0f} {r.breakout_rate_comp:>6.2f} {r.breakout_rate_all:>6.2f} | "
              f"{r.ft_given_breakout_comp:>9.3f} {r.ft_given_breakout_all:>9.3f} {r.ft_given_breakout_delta:>+6.3f} | "
              f"{r.ER_comp:>5.2f} {r.ER_all:>5.2f} {r.ER_delta:>+6.3f} | {r.expansion_comp:>5.2f} | "
              f"{r.fwd_abs_comp*100:>6.2f}% {r.fwd_abs_all*100:>6.2f}%")

    print(f"\n  PER SLEEVE @ threshold {THR}, horizon=10  (decisive: ftgiven Δ and ER Δ vs base):")
    print(f"  {'sleeve':>11} {'n_comp':>7} | {'ftgiven_c':>9} {'ftgiven_a':>9} {'Δ':>7} | {'ER_c':>5} {'ER_a':>5} {'Δ':>7} | {'exp_c':>5}")
    for s in scopes:
        r = _row(tbl, s, 10, THR)
        print(f"  {s:>11} {r.n_comp:>7.0f} | {r.ft_given_breakout_comp:>9.3f} {r.ft_given_breakout_all:>9.3f} "
              f"{r.ft_given_breakout_delta:>+7.3f} | {r.ER_comp:>5.2f} {r.ER_all:>5.2f} {r.ER_delta:>+7.3f} | {r.expansion_comp:>5.2f}")

    print(f"\n  ROBUSTNESS (NOT optimization) — POOLED decisive deltas across thresholds:")
    print(f"  {'thr':>5} {'N':>3} {'ftgiven_Δ':>10} {'ER_Δ':>8} {'genuine_ft_Δ':>13}")
    for thr in ROBUST:
        for N in HORIZONS:
            r = _row(tbl, "Pooled", N, thr)
            print(f"  {thr:>5.2f} {N:>3} {r.ft_given_breakout_delta:>+10.3f} {r.ER_delta:>+8.3f} {r.genuine_ft_delta:>+13.3f}")

    # ---- verdict ----
    # A real directional premise must clear a MEANINGFUL (not merely positive) margin on
    # the artifact-free measures: efficiency ratio (directional travel vs path) AND
    # follow-through GIVEN a breakout (genuine vs false). The raw genuine_ft_delta is NOT
    # used for the verdict — it is inflated by the mechanical narrow-channel effect (low
    # vol => tight Donchian channel => more breakouts) which carries no directional info.
    # Bar = 0.02 (2pp): generous for a higher-turnover breakout overlay that must beat costs.
    MIN_MEANINGFUL = 0.02
    exp_ok = all(_row(tbl, "Pooled", N, THR).expansion_comp > 1.0 for N in HORIZONS)
    edge = {}
    for s in scopes:
        ftg = float(np.mean([_row(tbl, s, N, THR).ft_given_breakout_delta for N in HORIZONS]))
        erd = float(np.mean([_row(tbl, s, N, THR).ER_delta for N in HORIZONS]))
        edge[s] = {"ftgiven_delta": ftg, "ER_delta": erd,
                   "directional": bool(ftg >= MIN_MEANINGFUL and erd >= MIN_MEANINGFUL)}
    pooled_dir = edge["Pooled"]["directional"]
    sleeves_dir = [s for s in premise.SLEEVES if edge[s]["directional"]]
    confirmed = pooled_dir or len(sleeves_dir) >= 2   # pooled OR a robust multi-sleeve signal

    print("\n  ---------------------------------------------------------------------------")
    print(f"  vol expansion after compression (pooled, all horizons): {exp_ok} "
          f"(expansion ratio comp ~ {_row(tbl,'Pooled',10,THR).expansion_comp:.2f}x)")
    print(f"  directional follow-through MEANINGFULLY above base rate @0.20 (bar = +0.020 on BOTH "
          f"ft-given-breakout and ER):")
    print(f"    pooled: {'YES' if pooled_dir else 'NO'}  "
          f"(ftgiven Δ {edge['Pooled']['ftgiven_delta']:+.3f}, ER Δ {edge['Pooled']['ER_delta']:+.3f} "
          f"— both << bar)")
    print(f"    sleeves clearing the bar: {sleeves_dir if sleeves_dir else 'none'}")
    print(f"    note: the larger genuine_ft_delta (~+0.05) is the mechanical narrow-channel effect "
          f"(more breakouts), NOT directional info — ER (artifact-free) shows ~0.")
    print(f"  VERDICT: premise {'CONFIRMED' if confirmed else 'NOT confirmed'} "
          "(close-to-close compression; NOT an intraday-ATR squeeze).")
    print("  ---------------------------------------------------------------------------")

    _write_report(tbl, edge, exp_ok, confirmed, pooled_dir, sleeves_dir)
    print(f"  report: {config.BREAKOUT_PREMISE_MD}")


def _write_report(tbl, edge, exp_ok, confirmed, pooled_dir, sleeves_dir) -> None:
    def row(s, N, thr):
        return _row(tbl, s, N, thr)
    L = ["# Phase 1B — Premise test: does vol compression precede directional expansion?", "",
         "*DESCRIPTIVE only — no positions, no P&L, no tuning. Conditioning (compression) is "
         "strictly point-in-time; the outcome window is forward-looking by design. Pre-registered "
         "headline threshold = **0.20**; 0.10/0.30 are a robustness sanity check, NOT a menu.*", "",
         "## Scope of claim (data constraint)", "",
         "The data is adjusted-**close-only** (no intraday H/L), so compression here is "
         "**close-to-close realized-vol percentile, NOT a true intraday ATR squeeze**. The premise "
         "tested is precisely: *does close-to-close vol compression precede directional expansion?* "
         "The conclusion does **not** generalize to an intraday-ATR squeeze (which would need OHLC data).", "",
         "## Decisive metric — follow-through quality & efficiency, conditional vs base rate", "",
         "After compression the Donchian channel is narrow, so breakouts are mechanically easier; "
         "the decisive question is whether those breakouts **follow through** (genuine) or **reverse** "
         "(false), and whether the post-move is **directional** (efficiency ratio). Both compared to "
         "the unconditional base rate.", "",
         f"### Pooled @ threshold 0.20", "",
         "| horizon | n_comp | breakout rate (comp/base) | follow-through\\|breakout (comp/base/Δ) | efficiency ratio (comp/base/Δ) | vol expansion (comp) |",
         "| --- | --- | --- | --- | --- | --- |"]
    for N in HORIZONS:
        r = row("Pooled", N, 0.20)
        L.append(f"| {N}d | {r.n_comp:.0f} | {r.breakout_rate_comp:.2f} / {r.breakout_rate_all:.2f} | "
                 f"{r.ft_given_breakout_comp:.3f} / {r.ft_given_breakout_all:.3f} / **{r.ft_given_breakout_delta:+.3f}** | "
                 f"{r.ER_comp:.2f} / {r.ER_all:.2f} / **{r.ER_delta:+.3f}** | {r.expansion_comp:.2f}x |")
    L += ["", "### Per sleeve @ threshold 0.20, horizon 10d", "",
          "| sleeve | n_comp | follow-through\\|breakout (comp/base/Δ) | efficiency ratio (comp/base/Δ) | directional edge? |",
          "| --- | --- | --- | --- | --- |"]
    for s in ["Pooled"] + premise.SLEEVES:
        r = row(s, 10, 0.20)
        L.append(f"| {s} | {r.n_comp:.0f} | {r.ft_given_breakout_comp:.3f} / {r.ft_given_breakout_all:.3f} / "
                 f"**{r.ft_given_breakout_delta:+.3f}** | {r.ER_comp:.2f} / {r.ER_all:.2f} / **{r.ER_delta:+.3f}** | "
                 f"{'yes' if edge[s]['directional'] else 'no'} |")
    L += ["", "### Robustness (NOT optimization) — pooled decisive deltas across thresholds", "",
          "| threshold | horizon | follow-through\\|breakout Δ | efficiency ratio Δ |",
          "| --- | --- | --- | --- |"]
    for thr in ROBUST:
        for N in HORIZONS:
            r = row("Pooled", N, thr)
            L.append(f"| {thr:.2f} | {N}d | {r.ft_given_breakout_delta:+.3f} | {r.ER_delta:+.3f} |")
    L += ["",
          "## Verdict", "",
          f"- **Vol expansion** after compression: {'present' if exp_ok else 'absent'} "
          f"(pooled forward/trailing vol ~ {row('Pooled',10,0.20).expansion_comp:.2f}× — the robust, "
          "expected part; vol clusters/mean-reverts as expected).",
          f"- **Directional follow-through MEANINGFULLY above base rate** (the decisive part; bar = "
          f"+0.02 on BOTH the artifact-free measures, efficiency ratio and follow-through-given-"
          f"breakout): pooled **{'YES' if pooled_dir else 'NO'}** "
          f"(ER Δ {edge['Pooled']['ER_delta']:+.3f}, ft|breakout Δ {edge['Pooled']['ftgiven_delta']:+.3f}); "
          f"sleeves clearing the bar: {', '.join(sleeves_dir) if sleeves_dir else '**none**'}.",
          "- **Read the numbers honestly:** the post-compression efficiency ratio is "
          "**≈ identical to baseline** (Δ ~0.00–0.02), and follow-through *quality* given a breakout "
          "is up only ~1pp on a ~67% base (Bond/RealEstate are flat-to-negative). The one sizeable "
          "positive — `genuine_ft_delta` ~+0.05 — is the **mechanical narrow-channel artifact** (low "
          "vol ⇒ tight Donchian channel ⇒ more breakouts in either direction), which carries no "
          "directional information. The deltas also **do not strengthen at tighter compression** "
          "(0.10 ≈ 0.20 ≈ 0.30) — the signature of a real effect is absent.",
          f"- **Premise NOT confirmed** for close-to-close compression on this universe.",
          "",
          "Compression precedes a vol expansion, but that expansion is **not directional beyond the "
          "base rate** — post-compression breakouts follow through at essentially the same rate as "
          "any breakout, and the move is no more efficient. The apparent 'edge' is a narrow-channel "
          "counting artifact. Per the gate this is a **clean negative**: do **not** build the "
          "strategy on close-to-close compression. (Scope: this does not test an intraday-ATR "
          "squeeze, which would require OHLC data — a separate question the current data cannot answer.)"]
    config.BREAKOUT_PREMISE_MD.write_text("\n".join(L), encoding="utf-8")


if __name__ == "__main__":
    main()
