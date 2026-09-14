"""CTA-EDGE-01-TA — the S2 build driver.

Runs the whole S2 validation path and writes the S2 artifacts. It computes NO real
outcome: the only real inputs it touches are the sealed event calendar, the macro
calendars and the panel's DATE column with a non-null presence mask.

    python research/extensions/ta/ta_s2_build.py            # from the repository root
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import ta_auction_fetch as auc      # noqa: E402
import ta_authorization as auth     # noqa: E402
import ta_calendar as tcal          # noqa: E402
import ta_classify as tcls          # noqa: E402
import ta_contract as K             # noqa: E402
import ta_covariates as tcov        # noqa: E402
import ta_diagnostics as tdiag      # noqa: E402
import ta_inference as tinf         # noqa: E402
import ta_report as trep            # noqa: E402

S2_DIR = os.path.join(K.TA_DIR, "s2")
CROSSTAB_MD = os.path.join(K.TA_DIR, "TA_MACRO_CROSSTAB.md")
SYNTHETIC_RESULT = os.path.join(S2_DIR, "TA_S2_SYNTHETIC_RESULT.json")


def _sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def render_crosstab(ct, covs, primary_events) -> str:
    per = ct["per_covariate"]
    lines = [
        "# CTA-EDGE-01-TA — MACRO / QRA COVARIATE CROSS-TABULATION",
        "",
        "```",
        f"LINEAGE                 = {K.LINEAGE}",
        f"SEALED_PREREG_SHA256    = {K.SEALED_PREREG_SHA256}",
        "STAGE                   = S2, produced BEFORE any AC exists",
        "CONTAINS_RETURNS        = NO   (every number below is a COUNT)",
        f"GENERATED_UTC           = "
        f"{_dt.datetime.now(_dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}",
        "```",
        "",
        "The sealed contract §G.3 requires this table to be reported **before any `AC`",
        "is computed**, so that Class-D reachability is known to the Owner while the",
        "lineage is still outcome-blind. Covariates are the sealed signed form:",
        "`+1` a release on a POST return-bearing day, `-1` on a PRE one, `0` otherwise.",
        "",
        f"Events: **{ct['n_events']}** primary windows "
        f"({primary_events[0].t0} … {primary_events[-1].t0}).",
        "",
        "| covariate | POST `+1` | neither `0` | PRE `-1` |",
        "|---|---:|---:|---:|",
    ]
    for c in K.MACRO_COVARIATES:
        lines.append(f"| **{c}** | {per[c]['post_plus1']} | {per[c]['neither_0']} | "
                     f"{per[c]['pre_minus1']} |")
    lines += [
        "",
        "## Combination counts (CPI, NFP, FOMC, QRA)",
        "",
        "| combination | events |",
        "|---|---:|",
    ]
    for combo, n in list(ct["combinations"].items())[:15]:
        lines.append(f"| `{combo}` | {n} |")
    lines += [
        f"",
        f"Distinct combinations observed: **{ct['distinct_combinations']}**.",
        "",
        "## The sealed evaluability test",
        "",
        "```",
        f"DESIGN_MATRIX_COLUMNS   = {ct['design_matrix_columns']}",
        f"DESIGN_MATRIX_RANK      = {ct['design_matrix_rank']}",
        f"REFERENCE_GROUP_N       = {ct['reference_group_n']}   "
        f"(events with all four signed covariates = 0)",
        f"MIN_REFERENCE_GROUP     = {ct['min_reference_group']}",
        f"MACRO_SPEC_EVALUABLE    = {'YES' if ct['evaluable'] else 'NO'}",
        f"NOT_EVALUABLE_REASONS   = {ct['not_evaluable_reasons']}",
        "```",
        "",
    ]
    if not ct["evaluable"]:
        lines += [
            "> **The sealed §G.3 diagnostic is mechanically `NOT_EVALUABLE`, and this was",
            "> established from the CALENDAR ALONE, with no return in existence.** Under the",
            "> sealed rule `NOT_EVALUABLE` makes the macro/QRA damage diagnostic TRIGGER,",
            "> so a would-be Class D becomes **Class I**. The specification is **not**",
            "> redesigned and the seal is **not** amended: the S1 contract disclosed this",
            "> exact risk and required this exact pre-check, and the pre-check has fired.",
            "",
            "The finding is itself the substantive result of the pre-check: at daily",
            "close-to-close frequency the mid-month refunding week is almost never",
            "macro-clean, which is precisely why the intraday literature had to go",
            "intraday to identify the effect.",
            "",
        ]
    return "\n".join(lines) + "\n"


def main() -> int:
    os.makedirs(S2_DIR, exist_ok=True)
    out = {}

    # 1. seal identity
    out["event_calendar_sha256"] = tcal.sealed_calendar_sha256()
    assert out["event_calendar_sha256"] == K.EVENT_CALENDAR_SHA256

    # 2. the sealed event calendar
    primary = tcal.load_sealed_events(K.PRIMARY_CELL)
    secondary = tcal.load_sealed_events(K.SECONDARY_CELL)
    out["primary"] = tcal.validate_primary(primary)
    out["secondary"] = tcal.validate_secondary(secondary)
    assert out["primary"]["ok"] and out["secondary"]["ok"]

    # 3. the outcome-free macro cross-tabulation
    grid = auc.common_grid(auc.trading_calendar())        # presence mask only
    covs = tcov.build_covariates(primary, grid, tcov.load_macro_calendar())
    out["covariates"] = tcov.write_covariates(covs)
    ct = tcov.crosstab(covs)
    with open(CROSSTAB_MD, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(render_crosstab(ct, covs, primary))
    out["crosstab"] = {"path": CROSSTAB_MD, "sha256": _sha(CROSSTAB_MD),
                       "evaluable": ct["evaluable"],
                       "reference_group_n": ct["reference_group_n"],
                       "design_matrix_rank": ct["design_matrix_rank"]}

    # 4. the authorization guard
    out["authorization"] = auth.authorization_status()
    try:
        auth.require_run_authorization(auth.REAL, run_id="TA-RUN-0001")
        out["historical_run_without_authorization"] = "NOT_BLOCKED"
    except auth.RunNotAuthorized:
        out["historical_run_without_authorization"] = "BLOCKED"

    # 5. the SYNTHETIC example report — schema only, no real outcome
    iv = tinf.Interval
    macro = tdiag.macro_not_evaluable(covs)
    verdict = tcls.classify(l_ac_gross=-2.0, u_ac_gross=11.0, l_sharpe=-0.20,
                            u_sharpe=0.18, loyo_passes=True, spy_damage=False,
                            macro_damage=macro.triggered)
    doc = trep.build_result(
        data_kind=auth.SYNTHETIC, verdict=verdict,
        primary={"n_events": len(primary), "years": list(K.PRIMARY_YEARS),
                 "mean_gross": iv(4.5, -2.0, 11.0, K.BOOTSTRAP_B, K.BOOTSTRAP_B),
                 "mean_net_point": -3.5,
                 "sharpe": iv(-0.01, -0.20, 0.18, K.BOOTSTRAP_B, K.BOOTSTRAP_B)},
        loyo=tinf.LoyoResult({y: 1.0 for y in K.PRIMARY_YEARS},
                             {y: 0.05 for y in K.PRIMARY_YEARS}, 1.0, 2006, True),
        secondary=tdiag.SecondaryResult(len(secondary), iv(1.0, -6.0, 8.0, 1, 1)),
        gradient=tdiag.GradientResult(len(primary), iv(0.2, -1.5, 1.9, 1, 1)),
        placebo=tdiag.spy_damage(iv(0.4, -2.2, 3.0, 1, 1), len(primary)),
        macro=macro,
        monthly_grid={"months": K.MONTH_GRID_N,
                      "event_months": K.MONTH_GRID_EVENT_MONTHS,
                      "zero_months": K.MONTH_GRID_ZERO_MONTHS},
        descriptives={"WARNING": "ALL NUMBERS ABOVE ARE SYNTHETIC PLACEHOLDERS. "
                                 "No real CTA-EDGE-01-TA outcome exists."})
    out["synthetic_result"] = trep.write_result(doc, SYNTHETIC_RESULT)
    out["synthetic_result"]["final_class"] = doc["final_class"]

    print(json.dumps(out, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
