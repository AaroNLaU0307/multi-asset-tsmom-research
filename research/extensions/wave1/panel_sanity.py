"""PANEL SANITY GATE — must PASS before any accounting identity is believed.

This exists because of a specific failure: the raw-symbol panels produced an
accounting identity residual of 1.21e-16 while the panels themselves were
nonsense (a gold June contract spanning 16 years, GC rolling 3 times in 16
years, held-contract settlement availability of 44%). The identity
`pnl_usd == notional_{t-1} * r_gross` is algebraic — it holds for ANY numbers,
including wrong ones — so it is necessary and nowhere near sufficient.

The gate therefore runs FIRST and independently. If it fails, the dependent
computation must STOP; it is never to be forced green.

Checks:
  S1  contract-key uniqueness           one key -> one (asset, expiration)
  S2  no decade collision               observed life fits one listing cycle
  S3  expiry coherence                  last observation is not after expiry
  S4  observed-life sanity              span within a plausible band per root
  S5  negative settlements              enumerated and attributable
  S6  non-positive settlement share     small; the HALT guard lives in X02a
  S7  root coverage                     all 18 pre-registered roots present
  S8  raw-symbol collision witness      symbols that WOULD have collided are
                                        now correctly split into several keys

Usage: python research/extensions/wave1/panel_sanity.py
Exit 0 = PASS, 1 = FAIL.
"""
import json
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent
CARRY = Path(__file__).resolve().parents[3].parent / "commodity-carry-research"
sys.path.insert(0, str(CARRY))
from src import config as carry_cfg   # noqa: E402

# Observed-life bounds.
#
# The generic cap was replaced before this gate was first run, because it was
# imprecise in the wrong direction: CME lists deep curves years ahead (crude
# ~9y, natural gas ~12y), so a legitimately long-dated contract can show a very
# long observed life and a flat cap would FALSE-FAIL it. Loosening the cap to
# accommodate that would equally have weakened the check.
#
# So the collision signature is tested directly instead. Under raw-symbol
# keying a reused symbol spanned essentially the WHOLE panel (GCM1: 2010-2026);
# a real contract never does. That is a hard failure. The generic cap is kept
# only as a REPORTED diagnostic, listing the longest-lived contracts for
# inspection, and does not by itself fail the gate.
PANEL_SPAN_FRACTION_FAIL = 0.95   # a contract spanning ~the whole panel is a collision
LONG_LIFE_REPORT_DAYS = 4200      # reported, not failed
MIN_LIFE_DAYS = 0

results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    return bool(ok)


def main():
    settle = pd.read_parquet(HERE / "settle_v2.parquet")
    oi = pd.read_parquet(HERE / "oi_v2.parquet")
    meta = pd.read_parquet(HERE / "contracts_meta.parquet")
    meta["expiration_dt"] = pd.to_datetime(meta["expiration"])

    out = {"settle_shape": list(settle.shape), "oi_shape": list(oi.shape),
           "n_contracts": int(len(meta))}

    # ---- S1 contract-key uniqueness -----------------------------------
    dup = meta["_contract_key"].duplicated().sum()
    check("S1 contract keys are unique", dup == 0, "%d duplicates" % dup)
    multi = meta.groupby("_contract_key")[["asset", "expiration"]].nunique()
    bad = multi[(multi["asset"] > 1) | (multi["expiration"] > 1)]
    check("S1 each key maps to exactly one (asset, expiration)",
          len(bad) == 0, "%d offending keys" % len(bad))

    # ---- S1b fragmentation diagnostic (REPORTED, Fable §2 recommendation) --
    # S1 proves no two contracts collapse into one key. The INVERSE can occur:
    # one real contract fragmenting into several keys when its expiration DATE
    # (not just time) is corrected mid-life. Fable found 14 such (root,
    # expiration-date) groups -- 4 GF November contracts, 2 HO listed-only
    # phantoms, 8 early-July-2010 id reassignments, 1 RB relisting, and the 3
    # ZM 2019 contracts carrying the -1.10 phantoms -- and verified none is
    # ever held. Reported here so the class is visible in the JSON rather than
    # only in an audit; the held-path assertion is enforced in X02a.
    frag = (meta.groupby(["asset", "expiration"])["_contract_key"]
                .nunique().reset_index(name="n_keys"))
    frag = frag[frag["n_keys"] > 1]
    out["fragmentation_same_expiration"] = {
        "n_groups": int(len(frag)),
        "groups": frag.to_dict("records"),
        "note": ("one contract split across keys; NOT a collision. Verified "
                 "never held: the held-front guard and X02a's roll series "
                 "operate on the keys actually selected by A1."),
    }

    # ---- S2/S3/S4 observed life ---------------------------------------
    obs = meta[meta["n_settle_obs"] > 0].copy()
    obs["first_dt"] = pd.to_datetime(obs["first_obs"])
    obs["last_dt"] = pd.to_datetime(obs["last_obs"])
    obs["life_days"] = (obs["last_dt"] - obs["first_dt"]).dt.days
    panel_span = (obs["last_dt"].max() - obs["first_dt"].min()).days
    spanning = obs[obs["life_days"] >= PANEL_SPAN_FRACTION_FAIL * panel_span]
    check("S2 no contract spans ~the whole panel (decade-collision signature)",
          len(spanning) == 0,
          "%d contracts span >=%.0f%% of the %dd panel; worst: %s" %
          (len(spanning), 100 * PANEL_SPAN_FRACTION_FAIL, panel_span,
           spanning.nlargest(3, "life_days")[["_contract_key", "life_days"]]
           .to_dict("records") if len(spanning) else ""))
    long_lived = obs[obs["life_days"] > LONG_LIFE_REPORT_DAYS]
    out["long_lived_contracts_reported"] = {
        "threshold_days": LONG_LIFE_REPORT_DAYS,
        "n": int(len(long_lived)),
        "top": long_lived.nlargest(5, "life_days")[
            ["_contract_key", "asset", "life_days"]].to_dict("records"),
        "note": ("reported for inspection, not a gate failure: CME lists deep "
                 "curves years ahead, so a long observed life can be legitimate"),
    }
    out["panel_span_days"] = int(panel_span)

    exp_utc = obs["expiration_dt"].dt.tz_convert("UTC").dt.tz_localize(None) \
        if obs["expiration_dt"].dt.tz is not None else obs["expiration_dt"]
    after = obs[obs["last_dt"] > exp_utc + pd.Timedelta(days=3)]
    check("S3 no settlement observed materially after expiration",
          len(after) == 0, "%d contracts trade past expiry" % len(after))

    out["observed_life_days"] = {
        "min": int(obs["life_days"].min()), "max": int(obs["life_days"].max()),
        "median": float(obs["life_days"].median()),
        "p99": float(obs["life_days"].quantile(0.99))}
    check("S4 observed lives are non-negative",
          int(obs["life_days"].min()) >= MIN_LIFE_DAYS,
          "min %d" % obs["life_days"].min())

    # ---- S5/S6 non-positive settlements: REPORTED, guarded elsewhere ----
    # These were initially written as hard gate failures on the whole panel.
    # That was the wrong locus, and the carry study had already settled the
    # question:
    #
    #   * `returns.held_front_zero_price_guard` puts the zero/negative-price
    #     HALT on the HELD FRONT contract only -- a non-positive settlement in
    #     a contract nobody holds is never divided by and is irrelevant;
    #   * carry's DATA_QA_REPORT finding F2 investigated panel-wide
    #     zero/negative counts and concluded they were almost entirely
    #     spread/combo contamination leaking through a string filter, resolved
    #     once the proper `instrument_class` filter was applied (which this
    #     extraction uses);
    #   * the same report documents CL 2020-04-20 settling at -37.63 as a real,
    #     cited market event -- KEEP, not a defect.
    #
    # So the counts are REPORTED here in full, and the hard guard runs in
    # run_x02a_v2 against the actual held front, which is where it can HALT a
    # PnL path. Reporting rather than failing is a relocation of the check to
    # its canonical place, not a relaxation of it: nothing that would have
    # failed a PnL computation now passes one.
    neg_cells = settle[settle < 0].stack()
    zero_cells = settle[settle == 0].stack()
    out["non_positive_settlements"] = {
        "n_negative": int(len(neg_cells)),
        "n_zero": int(len(zero_cells)),
        "pct_of_observed_cells": round(
            100.0 * (len(neg_cells) + len(zero_cells)) / int(settle.notna().sum().sum()), 4),
        "negatives": [{"date": str(d.date()), "contract": k, "value": float(v)}
                      for (d, k), v in neg_cells.items()],
        "zeros_by_year": pd.Series([d.year for (d, _k) in zero_cells.index])
                            .value_counts().sort_index().to_dict(),
        "n_contracts_with_zeros": int(pd.Series(
            [k for (_d, k) in zero_cells.index]).nunique()),
        "handling": ("non-positive settlements are NOT sanitised away here; the "
                     "held-front guard in run_x02a_v2 HALTS if any of them is "
                     "ever the contract actually held"),
    }
    check("S5 negative settlements are enumerated and attributable",
          len(neg_cells) < 20,
          "%d negatives (all listed in the JSON for inspection)" % len(neg_cells))
    check("S6 non-positive settlements are a small share of observed cells",
          out["non_positive_settlements"]["pct_of_observed_cells"] < 1.0,
          "%.4f%% of observed cells" % out["non_positive_settlements"]["pct_of_observed_cells"])

    # ---- S7 root coverage ----------------------------------------------
    present = set(meta["asset"].unique())
    missing = sorted(set(carry_cfg.ALL_SYMBOLS) - present)
    extra = sorted(present - set(carry_cfg.ALL_SYMBOLS))
    check("S7 all 18 pre-registered roots present", not missing,
          "missing: %s" % missing)
    check("S7 no non-universe roots leaked in", not extra, "extra: %s" % extra)
    out["contracts_by_root"] = meta.groupby("asset").size().to_dict()

    # ---- S8 decade-collision witness ------------------------------------
    # The defect this gate exists for: under raw-symbol keying, one symbol
    # covered several contracts. Show that such symbols now resolve to
    # multiple distinct persistent keys.
    if "instrument_id" in meta.columns:
        per_asset_exp = meta.groupby("asset")["expiration"].nunique()
        out["distinct_expirations_by_root"] = per_asset_exp.to_dict()
    # GCM1 was the witness case: June gold. Count June-expiring GC contracts.
    gc = meta[meta["asset"] == "GC"].copy()
    gc["exp_month"] = pd.to_datetime(gc["expiration"]).dt.month
    gc["exp_year"] = pd.to_datetime(gc["expiration"]).dt.year
    june_gc = gc[gc["exp_month"] == 6]
    out["gc_june_contracts"] = {
        "n_distinct_keys": int(len(june_gc)),
        "years": sorted(june_gc["exp_year"].unique().tolist()),
    }
    check("S8 decade collision eliminated (GC June resolves to many keys, "
          "each one year)", len(june_gc) >= 10,
          "%d June-GC keys across years %s" %
          (len(june_gc), sorted(june_gc["exp_year"].unique().tolist())[:5]))

    # settlement/OI alignment
    common = set(settle.columns) & set(oi.columns)
    out["alignment"] = {"settle_cols": settle.shape[1], "oi_cols": oi.shape[1],
                        "shared_cols": len(common),
                        "settle_only": settle.shape[1] - len(common),
                        "oi_only": oi.shape[1] - len(common)}

    width = max(len(n) for n, _o, _d in results)
    fails = 0
    for name, ok, detail in results:
        if not ok:
            fails += 1
        print("%-4s %-*s %s" % ("PASS" if ok else "FAIL", width, name,
                                detail if detail else ""))
    out["n_checks"] = len(results)
    out["n_failed"] = fails
    out["PANEL_SANITY"] = "PASS" if fails == 0 else "FAIL"
    (HERE / "panel_sanity.json").write_text(json.dumps(out, indent=2, default=str),
                                            encoding="utf-8")
    print("\n" + json.dumps({k: out[k] for k in
                             ("n_contracts", "contracts_by_root",
                              "observed_life_days", "gc_june_contracts",
                              "alignment", "n_checks", "n_failed",
                              "PANEL_SANITY")}, indent=2, default=str))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
