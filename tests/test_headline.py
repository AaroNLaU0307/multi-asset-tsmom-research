"""``results/headline.json`` is the machine-readable source for the profile table.

Every CSV-backed stat is recomputed here from its committed artifact with the repo's own
functions and must match both the printed ``display`` and the stored ``value`` (to the
display's rounding). Every markdown-backed stat must appear literally in its artifact, on
the row its locator names. No licensed or git-ignored data is needed.
"""

from __future__ import annotations

import json
import math
import re
import sys
from functools import cache
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src import performance, seasonality, validation

HEADLINE = json.loads((ROOT / "results" / "headline.json").read_text(encoding="utf-8"))
TOP_KEYS = {"schema", "repo", "source_commit", "as_of", "rows"}
ROW_KEYS = {"id", "section", "hypothesis", "verdict", "verdict_detail", "mechanism", "stats",
            "caveats"}
STAT_KEYS = {"label", "display", "value", "artifact", "locator", "provenance"}
PROVENANCE = {"reproduced", "repo-reported, not reproduced", "predates fix; pending re-run"}
VERDICTS = {"SUPPORTED", "not_promoted", "falsified"}          # the repo's own vocabulary


def _read(rel: str) -> pd.DataFrame:
    return pd.read_csv(ROOT / rel)


@cache
def _core_net() -> pd.Series:
    r = pd.read_csv(ROOT / "research/xsmom/xsmom_monthly_returns.csv", index_col=0,
                    parse_dates=True)
    return r["tsmom_net"]


@cache
def _core_ci() -> tuple[float, float]:
    ci = validation.bootstrap_ci(_core_net(), stat="sharpe")
    return ci["lo"], ci["hi"]


def _crisis(regime: str) -> float:
    cw = _read("research/xsmom/xsmom_crisis_windows.csv").set_index("regime")
    return float(cw.loc[regime, "cum_return_tsmom"])


def _breakout(col: str) -> float:
    b = _read("research/vol_breakout/breakout_premise_by_sleeve.csv")
    row = b[(b.scope == "Pooled") & (b.horizon == 10) & (b.threshold == 0.2)]
    assert len(row) == 1
    return float(row[col].iloc[0])


@cache
def _season_bh():
    s = _read("research/seasonality/seasonality_premise_family.csv")
    p_adj, reject = seasonality.bh_fdr(s["p_raw"].to_numpy())
    assert (abs(p_adj - s["p_bh"].to_numpy()) < 1e-12).all()
    assert (reject == s["fdr_reject"].to_numpy()).all()
    return s, p_adj, reject


def _yield_family() -> pd.DataFrame:
    return _read("research/yield_spread/yield_spread_premise_family.csv")


def _yield_episode_counts() -> pd.Series:
    return _read("research/yield_spread/yield_spread_episodes.csv").groupby(["spread", "h"]).size()


def _yield_2022_24_share() -> pd.Series:
    ep = _read("research/yield_spread/yield_spread_episodes.csv")
    ep["start"], ep["end"] = pd.to_datetime(ep["start"]), pd.to_datetime(ep["end"])
    covers = (ep.start <= "2023-06-01") & (ep.end >= "2023-06-01")
    return ep[covers].groupby(["spread", "h"]).n_flat_obs.sum() / ep.groupby(["spread", "h"]).n_flat_obs.sum()


def _decomp_contains_zero(term: str) -> int:
    d = _read("research/xsmom/xsmom_universes_decomposition.csv")
    d = d[d.term == term]
    return int(((d.lo <= 0) & (d.hi >= 0)).sum())


def _rng(lo: float, hi: float, fmt: str, suffix: str = "") -> str:
    return f"{lo:{fmt}}–{hi:{fmt}}{suffix}"


def _yield_p_fdr() -> tuple[None, str]:
    fam = _yield_family()
    p_adj, _ = seasonality.bh_fdr(fam["p_raw"].to_numpy())
    assert (abs(p_adj - fam["p_fdr"].to_numpy()) < 1e-12).all()
    return None, _rng(p_adj.min(), p_adj.max(), ".2f")


def _yield_kept_share() -> tuple[None, str]:
    fam = _yield_family()
    kept = fam["delta_drop_2022_24_ann"] / fam["delta_ann"]
    assert (kept > 0).all()                                  # sign preserved in every cell
    return None, _rng(kept.min() * 100, kept.max() * 100, ".0f", "%")


# (row id, stat label) -> () -> (value or None, display)
RECOMPUTE = {
    ("tsmom-core", "net Sharpe (2 bps)"):
        lambda: (v := performance.sharpe_ratio(_core_net()), f"{v:.2f}"),
    ("tsmom-core", "95% CI low (2 bps)"): lambda: (v := _core_ci()[0], f"{v:.2f}"),
    ("tsmom-core", "95% CI high (2 bps)"): lambda: (v := _core_ci()[1], f"{v:.2f}"),
    ("tsmom-core", "GFC 2008 window return"): lambda: (v := _crisis("GFC 2008"), f"{v:+.1%}"),
    ("tsmom-core", "COVID 2020 window return"): lambda: (v := _crisis("COVID 2020"), f"{v:+.1%}"),
    ("vol-breakout", "vol expansion after compression"):
        lambda: (v := _breakout("expansion_comp"), f"{v:.2f}×"),
    ("vol-breakout", "vol expansion, unconditional"):
        lambda: (v := _breakout("expansion_all"), f"{v:.2f}×"),
    ("vol-breakout", "efficiency-ratio change"): lambda: (v := _breakout("ER_delta"), f"{v:+.3f}"),
    ("seasonality", "cells passing BH-FDR"):
        lambda: (v := int(_season_bh()[2].sum()), f"{v}/{len(_season_bh()[0])}"),
    ("seasonality", "smallest BH-adjusted p"):
        lambda: (v := float(_season_bh()[1].min()), f"{v:.2f}"),
    ("seasonality", "cells with raw p < 0.05"):
        lambda: (v := int((_season_bh()[0]["p_raw"] < 0.05).sum()), f"{v}/{len(_season_bh()[0])}"),
    ("yield-curve", "cells confirmed"):
        lambda: (v := int(_yield_family()["CONFIRMED"].sum()), f"{v}/{len(_yield_family())}"),
    ("yield-curve", "BH-FDR adjusted p"): _yield_p_fdr,
    ("yield-curve", "share of the effect kept without 2022–24"): _yield_kept_share,
    ("yield-curve", "cells keeping their sign without 2022–24"):
        lambda: (v := int((_yield_family()["delta_drop_2022_24_ann"]
                           * _yield_family()["delta_ann"] > 0).sum()),
                 f"{v}/{len(_yield_family())}"),
    ("yield-curve", "episodes in the tested flat state"):
        lambda: (None, _rng(_yield_episode_counts().min(), _yield_episode_counts().max(), "d")),
    ("yield-curve", "2022–24 share of flat-state days"):
        lambda: (None, _rng(_yield_2022_24_share().min() * 100,
                            _yield_2022_24_share().max() * 100, ".0f", "%")),
    ("xsmom", "universes confirmed"):
        lambda: (v := int(_read("research/xsmom/xsmom_universes_map.csv")["confirmed"].sum()),
                 f"{v}/5"),
    ("xsmom", "corr with TSMOM (17 ETFs)"):
        lambda: (v := float(pd.read_csv(ROOT / "research/xsmom/xsmom_monthly_returns.csv")
                            [["xsmom_tercile_net", "tsmom_net"]].corr().iloc[0, 1]), f"{v:+.2f}"),
    ("xsmom", "term1 (own-autocorrelation) CI contains 0"):
        lambda: (v := _decomp_contains_zero("term1_autocov"), f"{v}/5"),
    ("xsmom", "term2 (lead-lag) CI contains 0"):
        lambda: (v := _decomp_contains_zero("term2_leadlag"), f"{v}/5"),
}

STATS = [(row["id"], s) for row in HEADLINE["rows"] for s in row["stats"]]


def test_schema():
    assert set(HEADLINE) == TOP_KEYS
    assert HEADLINE["schema"] == "headline/v1"
    assert HEADLINE["repo"] == "AaroNLaU0307/multi-asset-tsmom-research"
    assert HEADLINE["source_commit"] == "PENDING" or re.fullmatch(r"[0-9a-f]{40}",
                                                                   HEADLINE["source_commit"])
    assert HEADLINE["as_of"] == "2026-09-27"
    ids = [row["id"] for row in HEADLINE["rows"]]
    assert len(ids) == len(set(ids))
    for row in HEADLINE["rows"]:
        assert set(row) == ROW_KEYS, row["id"]
        assert row["section"] in {"archive", "other"}
        assert row["verdict"] in VERDICTS, row["id"]
        assert "CONFIRMED" not in row["verdict"].upper() and "FALSIFIED" != row["verdict"]
        for s in row["stats"]:
            assert set(s) == STAT_KEYS, (row["id"], s["label"])
            assert s["provenance"] in PROVENANCE


@pytest.mark.parametrize(("row_id", "stat"), STATS, ids=[f"{r}:{s['label']}" for r, s in STATS])
def test_stat_matches_its_artifact(row_id, stat):
    path = ROOT / stat["artifact"]
    assert path.is_file(), stat["artifact"]
    if path.suffix == ".csv":
        key = (row_id, stat["label"])
        assert key in RECOMPUTE, f"no recomputation registered for CSV-backed stat {key}"
        assert stat["provenance"] == "reproduced"
        value, display = RECOMPUTE[key]()
        assert display == stat["display"]
        if stat["value"] is not None:
            assert math.isclose(stat["value"], value, abs_tol=1e-4), (stat["value"], value)
    else:
        text = path.read_text(encoding="utf-8")
        assert stat["display"] in text
        assert stat["provenance"] != "reproduced"             # markdown numbers are not recomputed
        for row_key in re.findall(r"row '([^']+)'", stat["locator"]):
            lines = [ln for ln in text.splitlines() if ln.startswith("|") and row_key in ln]
            assert any(stat["display"] in ln for ln in lines), (row_key, stat["display"])
