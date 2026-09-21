# -*- coding: utf-8 -*-
"""Emit F6_S1_PRESEAL_MANIFEST.json. Every pin is COMPUTED, never typed."""
import hashlib, json, os, subprocess, sys
import datetime as dt

REPO = r"C:\Users\Aaron\OneDrive\Desktop\Quant trade\multi-asset-tsmom-research"
WS = r"C:\Users\Aaron\OneDrive\Desktop\Quant trade"
os.chdir(REPO)
F6 = "research/extensions/f6"

def sha(p):
    with open(p, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()

# (key, path, root, role)
ITEMS = [
 ("final_event_manifest", F6 + "/F6_FINAL_EVENT_MANIFEST.json", REPO,
  "the authoritative 462-session event sample"),
 ("final_schedule_pit_gate", F6 + "/F6_SCHEDULE_PIT_FINAL_GATE.md", REPO,
  "the fail-closed eligibility ruling that produced it"),
 ("owner_decision_record", "ops/OWNER_DECISION_RECORD_CTA_EDGE_05_F6.md", REPO,
  "current F6 Owner decisions, including F6-OD-TY / F6-OD-CASH / F6-OD-PIT"),
 ("final_independent_astra_review",
  "research/extensions/review_history/"
  "F6_FINAL_INDEPENDENT_REVIEW_2026-09-21_ASTRA_01.md", REPO,
  "ACTIVE pre-S1 independent review authority; PASS / "
  "B_READY_FOR_S1_SEAL_WITH_CLAIM_CAP_NARROWING"),
 ("frozen_metadata_audit_rule", F6 + "/F6_METADATA_AUDIT_RULE.md", REPO,
  "frozen pre-retrieval audit rule, immutable"),
 ("s0_feasibility_report", F6 + "/F6_EVENT_SCHEDULE_PIT_REPORT.md", REPO,
  "S0 schedule-PIT feasibility"),
 ("s0_repair_record", F6 + "/F6_S0_REPAIR_RECORD.md", REPO, "S0 repair pass"),
 ("s0_completion_record", F6 + "/F6_S0_COMPLETION_RECORD.md", REPO,
  "S0 completion; its 467 count is SUPERSEDED by the final manifest"),
 ("independent_adjudication_transcript",
  F6 + "/F6_INDEPENDENT_ADJUDICATION_CONTROLLER_TRANSCRIPT.md", REPO,
  "controller-supplied RECONSTRUCTION of the missing pre-S0 review. NOT the "
  "original bytes, carries NO original hash, NOT independent evidence"),
 ("sample_reuse", "research/extensions/SAMPLE_REUSE.md", REPO,
  "T0_REUSED_DEPENDENT classification authority"),
 ("trial_ledger", "research/extensions/TRIAL_LEDGER.md", REPO,
  "UNCHANGED at pre-seal; the F-F6 row is due AT SEAL"),
 ("exposure_ledger", "ops/EXPOSURE_LEDGER.md", REPO,
  "UNCHANGED; no outcome revealed, so no EXPOSURE_EVENT exists"),
 ("spy_panel_authority", "data/close_prices_raw.csv", REPO,
  "frozen single-vendor adjusted-close panel; EXECUTION PROXY"),
 ("dgs3mo_authority", "data/DGS3MO.csv", REPO,
  "Owner-chosen ex-post cash opportunity-cost proxy source"),
 ("tom_authority_contract", "research/seasonality/PREREGISTRATION.md", REPO,
  "sealed seasonality contract defining TOM"),
 ("tom_authority_implementation", "src/seasonality.py", REPO,
  "sealed is_tom implementation reused verbatim"),
 ("ta_auction_authority_contract", "research/extensions/ta/TA_PREREGISTRATION.md",
  REPO, "sealed TA object pinning the 10y/30y auction definition"),
 ("ta_auction_calendar", "research/extensions/ta/TA_EVENT_CALENDAR.csv", REPO,
  "auction dates used to build AUCTION(d)"),
 ("s1_preregistration_draft", F6 + "/F6_S1_PREREGISTRATION_DRAFT.md", REPO,
  "THIS DRAFT. NOT SEALED."),
 ("preseal_validation_evidence", F6 + "/F6_S1_PRESEAL_VALIDATION.json", REPO,
  "machine output of the pre-seal validation"),
 ("preseal_validation_script", F6 + "/f6_s1_preseal_validate.py", REPO,
  "the validator that produced it"),
 ("round1_f6_authority",
  "2026-09-15-cta-edge-discovery-r1-mechanism-feature-map-fable-01.md", WS,
  "original Round-1 F6 fields 1-15"),
 ("od_1a_1h", "Research Reports/"
  "2026-09-20-cta-edge-05-f6-od-1a-1h-s0-design-decisions-fable-01.md", WS,
  "OD-1 S0 design decisions"),
 ("od_2a_2h", "Research Reports/"
  "2026-09-20-cta-edge-05-f6-od-2a-2h-pooling-control-gates-fable-01.md", WS,
  "OD-2 pooling and control gates"),
 ("od_ty_od_cash", "Research Reports/"
  "2026-09-21-cta-edge-05-f6-od-3a-3b-terminal-year-cash-return-object-fable-01.md",
  WS, "F6-OD-TY / F6-OD-CASH, filed under its historical od-3a-3b name"),
]

pins, missing = {}, []
for key, rel, root, role in ITEMS:
    p = os.path.join(root, rel)
    if not os.path.isfile(p):
        missing.append(rel)
        continue
    pins[key] = {"path": rel.replace("\\", "/"),
                 "root": "repository" if root == REPO else "workspace",
                 "sha256": sha(p), "role": role}
if missing:
    raise SystemExit("MISSING PINS: %s" % missing)

val = json.load(open(os.path.join(F6, "F6_S1_PRESEAL_VALIDATION.json"),
                     encoding="utf-8"))
if not val["validated"]:
    raise SystemExit("validation did not pass; refusing to emit a manifest")

head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                      text=True).stdout.strip()

out = {
 "schema": {"name": "f6-s1-preseal-manifest", "version": 1},
 "lineage": "CTA-EDGE-05 / F6 MACRO_ANNOUNCEMENT_PREMIUM",
 "generated": dt.date.today().isoformat(),
 "git_head_at_generation": head,

 "SEAL_STATUS": "DRAFT / OWNER_APPROVAL_REQUIRED",
 "sealed": False,
 "seal_note": "This manifest pins the inputs a seal would freeze. It IS NOT a "
              "seal. Aaron alone performs the irreversible seal action. On "
              "seal this manifest is SUPERSEDED by the seal manifest.",

 "final_independent_review": {
   "imported": True,
   "sha256": pins["final_independent_astra_review"]["sha256"],
   "source_path": r"C:\Users\Aaron\OneDrive\Documents\ChatGPT"
                  r"\multi-asset-tsmom-research\reviews"
                  r"\F6_FINAL_INDEPENDENT_REVIEW_2026-09-21_ASTRA_01.md",
   "byte_identical_to_source": True,
   "rewritten_or_normalized": False,
   "status": "PASS",
   "final_class": "B_READY_FOR_S1_SEAL_WITH_CLAIM_CAP_NARROWING",
   "seal_authorized_by_this_review": False,
   "sidecar": "F6_FINAL_INDEPENDENT_REVIEW_2026-09-21_ASTRA_01.md.sha256, "
              "copied verbatim from the source workspace. The repository's own "
              "convention is MANIFEST PINNING (it carried no checksum sidecars "
              "before this one), so THIS MANIFEST ENTRY is the binding pin and "
              "the sidecar is a faithful copy of the accompanying artifact."},

 "historical_provenance_reservation": {
   "value": True, "blocking": False,
   "note": "The pre-S0 independent artifact was NEVER PERSISTED and is NOT "
           "RECOVERED. The transcript pinned above is a controller-supplied "
           "reconstruction with no original hash. Nothing here claims "
           "recovery or retrospective certification."},

 "claim_identity": {
   "scientific_object": "historical pooled scheduled-macro-announcement-day "
                        "edge in SPY",
   "promotion_instrument": "SPY ONLY",
   "tlt": "STRUCK ENTIRELY FROM CTA-EDGE-05 OUTCOME COMPUTATION",
   "f6b_pre_fomc_drift": "SEPARATE FUTURE LINEAGE; NOT COMPUTED",
   "f6c_era_split": "DESCRIPTIVE ONLY; NO PROMOTION; NO RESCUE",
   "global_pooling": "MATERIAL PRE-OUTCOME DESIGN COMPLETION, NOT ORIGINAL "
                     "PROMOTION AUTHORITY",
   "sample_reuse_class": "T0_REUSED_DEPENDENT",
   "evidence_ceiling": "SUPPORTED",
   "independent_confirmation": False},

 "event_universe": {
   "families": ["FOMC", "CPI", "NFP"],
   "primary_years": [2011, 2025],
   "y2026": "NO F6 OUTCOME QUANTITY MAY BE FORMED",
   "final_primary_event_count": val["final_event_count"],
   "family_labels": val["family_labels"],
   "family_labels_total": val["family_labels_total"],
   "multi_event_sessions": val["multi_event_sessions"],
   "overlap_adjustment": val["overlap_adjustment"],
   "same_day_rule": "ONE trade, ONE unit, ONE return, ONE primary "
                    "observation. Diagnostic labels may be multiple. NO "
                    "DOUBLE NOTIONAL.",
   "pit_exclusions_permanent": ["NFP 2013-10-22", "CPI 2013-10-30 (label only)",
                                "CPI 2013-11-20", "NFP 2025-11-20",
                                "NFP 2025-12-16", "CPI 2025-12-18"],
   "post_seal_reinstatement": "FORBIDDEN"},

 "trade": {"position": "long 1 unit notional SPY on every eligible event "
                       "session",
   "entry": "prior eligible trading-session close",
   "exit": "eligible event-session close",
   "otherwise": "flat", "leverage": "none",
   "excluded_inputs": ["consensus", "actual macro print", "surprise",
                       "post-release reaction", "NQ signal", "TLT signal"],
   "price_representation": "frozen single-vendor adjusted-close SPY panel",
   "execution_status": "EXECUTION PROXY. NOT production-grade fill evidence."},

 "p2_population": {
   "rule": "EVERY trading session in calendar years 2011-2025. NO ROW DROPPED.",
   "rows": val["p2_rows"],
   "opening_boundary": val["opening_boundary"],
   "opening_2011_row_rule_validated": True},

 "cash_proxy": {
   "series": "DGS3MO",
   "role": "OWNER-CHOSEN EX-POST CASH OPPORTUNITY-COST PROXY",
   "not_role": ["signal", "eligibility input", "position input",
                "sizing input"],
   "formula": "rf_hold(d) = (DGS3MO annual percent / 100) * "
              "HOLD_calendar_days(d) / 365",
   "daycount_attribution": "THE /365 CONVENTION IS OWNER-CHOSEN. It must "
                           "NEVER be attributed to Treasury, H.15 or FRED.",
   "mapping_rule": "last official observation dated on or before the "
                   "benchmark date, carrying forward ONLY across "
                   "source-explained non-publication. NO arbitrary 7-day rule.",
   "unexplained_gap_behaviour": "IMPLEMENTATION HOLD. Do not substitute "
                                "another cash series.",
   "validation": val["dgs3mo"]},

 "return_objects": {
   "R": "AdjClose(d) / AdjClose(prev(d)) - 1",
   "r_excess": "R(d) - rf_hold(d)",
   "r_net": "r_excess(t) - 0.0004",
   "round_trip_cost": 0.0004,
   "cost_decomposition": "2 bps entry + 2 bps exit",
   "p1_target": "event-weighted arithmetic mean of r_net over the 462 "
                "eligible event sessions",
   "p2_dependent": "r_excess(d) over ALL 2011-2025 trading sessions",
   "p2_cost_treatment": "GROSS of event transaction cost. Do NOT subtract a "
                        "hypothetical strategy cost from control sessions.",
   "computed": False},

 "fixed_p2_model": {
   "specification": "r_excess(d) = a + beta_EVENT*EVENT(d) + weekday dummies "
                    "+ TOM(d) + HOLD(d) + AUCTION(d) + error(d)",
   "columns": val["pooled_design"]["columns"],
   "weekday_baseline": val["pooled_design"]["weekday_baseline"],
   "shape": val["pooled_design"]["shape"],
   "rank": val["pooled_design"]["rank"],
   "full_rank": val["pooled_design"]["full_rank"],
   "event_in_span_of_controls": val["pooled_design"]["event_in_span_of_controls"],
   "tom_source": "src/seasonality.py::is_tom (sealed), SEAS_TOM_LAST / "
                 "SEAS_TOM_FIRST from config",
   "auction_source": "TA_EVENT_CALENDAR.csv, tenor_family in {10-Year, "
                     "30-Year} nominal coupon auctions",
   "forbidden": ["interactions", "matched-control alternative",
                 "alternate regression", "variable selection",
                 "fallback model", "post-result model repair"],
   "interpretation": "CONDITIONAL LINEAR ASSOCIATION, not causal "
                     "identification. The control is NOT called conservative."},

 "gates": {
   "P1": "lower endpoint of the nominal 95% calendar-year percentile-bootstrap "
         "interval for mean r_net > 0",
   "P2": "lower endpoint of the nominal 95% calendar-year percentile-bootstrap "
         "interval for beta_EVENT > 0",
   "P3": "ONLY if P1 and P2 pass. Delete one complete calendar year at a time, "
         "refit the identical objects; EVERY P1 point estimate AND every P2 "
         "beta_EVENT point estimate must remain STRICTLY > 0. No "
         "deletion-specific significance requirement.",
   "P3_failure": "ONE_YEAR_FRAGILITY / NOT_PROMOTED. NOT mechanism "
                 "falsification.",
   "promotion_uses": "LOWER ENDPOINT ONLY"},

 "bootstrap": dict(val["bootstrap"], **{
   "procedure": ["draw 15 calendar-year labels WITH REPLACEMENT from "
                 "{2011..2025}",
                 "concatenate the complete year blocks, duplicating a year's "
                 "rows if drawn more than once",
                 "compute the EVENT-WEIGHTED P1 mean on the replicated event "
                 "rows",
                 "refit the EXACT fixed P2 OLS on the replicated daily rows",
                 "retain the P1 mean and beta_EVENT"],
   "same_draw_for_p1_and_p2": True,
   "estimand_weighting": "EVENT-WEIGHTED / SESSION-WEIGHTED, NOT equally "
                         "weighted annual means",
   "interval_wording": "NOMINAL 95% PERCENTILE-BOOTSTRAP INTERVAL. Never "
                       "'exact 95% coverage'.",
   "seed_provenance": "derived from FINAL_EVENT_MANIFEST_SHA256 (metadata) "
                      "per the current Owner instruction, which SUPERSEDES "
                      "OD-2's seal-derived seed. NEVER derived from returns "
                      "or from a post-result artifact.",
   "executed": False}),

 "per_year_rank": val["per_year_rank"],
 "individual_year_matrix_rank_pass": val["individual_year_matrix_rank_pass"],
 "bootstrap_rank_owner_review_required": not val["individual_year_matrix_rank_pass"],

 "inference_limitation": [
   "15 year blocks imply approximate, assumption-dependent inference.",
   "A large event count does not create additional independent year clusters.",
   "The bootstrap does NOT establish finite-sample calibrated 95% coverage.",
   "The bootstrap does NOT establish cross-regime replication.",
   "The bootstrap does NOT establish future persistence.",
   "LOYO does NOT validate bootstrap coverage.",
   "LOYO does NOT establish stable magnitudes."],

 "terminal_classification": {
   "P1 harvestable + P2 specific + P3 pass": "SUPPORTED_HISTORICAL_EDGE",
   "P1 harvestable + P2 specific + P3 fail": "ONE_YEAR_FRAGILITY / NOT_PROMOTED",
   "P1 harvestable + P2 unresolved": "UNRESOLVED",
   "P1 harvestable + P2 absent":
     "POSITIVE_PAYOFF_NOT_ANNOUNCEMENT_SPECIFIC / NOT_PROMOTED",
   "P1 unresolved + P2 specific": "UNRESOLVED",
   "P1 unresolved + P2 unresolved": "UNRESOLVED",
   "P1 unresolved + P2 absent":
     "NOT_ANNOUNCEMENT_SPECIFIC / NOT_PROMOTED, payoff itself unresolved",
   "P1 economically excluded": "NOT_PROMOTED regardless of P2",
   "definitions": {"positive": "lower endpoint > 0",
     "unresolved": "lower endpoint <= 0 < upper endpoint",
     "excluded_absent": "upper endpoint <= 0"},
   "forbidden_labels": ["LOW_POWER", "observed-power calculation",
                        "mechanism-falsified from these gates"]},

 "diagnostics": {
   "additional_promotion_capable_diagnostics": "FORBIDDEN",
   "per_family_summaries": "permitted ONLY where already adopted by Owner "
                           "authority; PROMOTION_POWER = NONE, RESCUE_POWER = "
                           "NONE, no alternate weighting, no family-deletion "
                           "rescue",
   "new_lofo_or_regime_diagnostics": "FORBIDDEN — not added merely because "
                                     "the reviewer mentioned them "
                                     "illustratively",
   "tlt": "NONE", "f6b": "NONE", "y2026_performance": "NONE"},

 "claim_cap": {
   "strongest_success_claim": "On the frozen single-vendor adjusted-close SPY "
     "panel for 2011-2025, the predeclared prior-close-to-event-session-close "
     "pooled rule on the 462 archive-eligible scheduled FOMC, CPI and "
     "Employment Situation sessions met its fixed promotion criteria: its mean "
     "event payoff, after the Owner-chosen DGS3MO cash opportunity-cost proxy "
     "and 4 bps round-trip cost, had a nominal 95% calendar-year "
     "percentile-bootstrap lower endpoint above zero; the EVENT coefficient in "
     "the fixed gross cash-excess return regression with weekday, TOM, "
     "holding-length and 10y/30y-auction controls also had a nominal lower "
     "endpoint above zero; and both point estimates remained positive after "
     "each single-calendar-year deletion.",
   "qualifiers": ["HISTORICAL", "DEPENDENT", "T0", "SUPPORTED",
                  "adjusted-close execution proxy", "Owner-chosen cash proxy",
                  "approximate 15-year-block inference"],
   "must_not_claim": ["causal uncertainty compensation",
     "independent confirmation", "individual FOMC alpha",
     "individual CPI alpha", "individual NFP alpha", "TLT premium",
     "pre-FOMC drift", "post-2015 persistence", "future persistence",
     "buy-and-hold dominance", "significance after every LOYO deletion",
     "production-grade fills", "exact finite-sample 95% coverage"]},

 "accounting": {
   "trial_ledger_changed": False,
   "trial_ledger_reason": "The HYPOTHESIS_FAMILY schema declares a family AT "
     "THE SEAL ('appended here at the seal, before any member has run' — F-TA, "
     "F-BENB). F6 is NOT SEALED, so the F-F6 row is not yet due. The row is "
     "DRAFTED in the preregistration draft section 16.1 so it can be appended "
     "at the seal rather than transcribed late as F-MMV was.",
   "exposure_ledger_changed": False,
   "exposure_ledger_reason": "An EXPOSURE_EVENT is a computation or read that "
     "REVEALS OUTCOMES OR MEASUREMENTS. No F6 outcome or measurement exists, "
     "so there is no row to append.",
   "ledger_preseal_owner_review_required": False,
   "f6_primary_trial_consumed": False},

 "preseal_validation": {
   "validated": val["validated"], "failing_checks": val["failing_checks"],
   "cross_tabs": val["cross_tabs"],
   "result_contingent_branch_found": False,
   "result_contingent_note": "Every branch in the gate and terminal tables is "
     "fixed pre-outcome and is terminal or vetoing, never selective. P3 is "
     "evaluated only after a passing pair and can solely downgrade. No branch "
     "chooses a different estimator, weight, sample, cost or model as a "
     "function of a result. The independent review concurred."},

 "firewall": val["firewall"],
 "pins": pins,
}

p = os.path.join(F6, "F6_S1_PRESEAL_MANIFEST.json")
with open(p, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(out, fh, indent=1, sort_keys=True)
    fh.write("\n")
print("wrote %s" % p)
print("pins: %d   all present" % len(pins))
print("PRESEAL_MANIFEST_SHA256 %s" % sha(p))
