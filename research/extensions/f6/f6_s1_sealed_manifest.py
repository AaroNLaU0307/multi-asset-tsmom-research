# -*- coding: utf-8 -*-
"""Emit F6_S1_SEALED_MANIFEST.json. POST-SEAL bytes. Every pin COMPUTED.

Generated AFTER the sealed preregistration and AFTER the F-F6 trial-ledger
append, so the TRIAL_LEDGER pin is the POST-APPEND hash, never the pre-append
one.
"""
import hashlib, json, os, subprocess
import datetime as dt

REPO = r"C:\Users\Aaron\OneDrive\Desktop\Quant trade\multi-asset-tsmom-research"
WS = r"C:\Users\Aaron\OneDrive\Desktop\Quant trade"
os.chdir(REPO)
F6 = "research/extensions/f6"

PRE_APPEND_LEDGER = "711d4ab41eac6ef53985b260835b186e7fd95eea0a452ba8f05ab99e08b2d0e2"

def sha(p):
    with open(p, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()

ITEMS = [
 ("sealed_preregistration", F6 + "/F6_S1_PREREGISTRATION_SEALED.md", REPO,
  "THE SEALED CONTRACT. Authoritative for every frozen research constant."),
 ("seal_record", F6 + "/F6_S1_SEAL_RECORD.md", REPO,
  "immutable seal identity; pins the five non-circular post-seal hashes"),
 ("final_event_manifest", F6 + "/F6_FINAL_EVENT_MANIFEST.json", REPO,
  "the authoritative 462-session event sample"),
 ("final_schedule_pit_gate", F6 + "/F6_SCHEDULE_PIT_FINAL_GATE.md", REPO,
  "the fail-closed eligibility ruling that produced it"),
 ("owner_decision_record", "ops/OWNER_DECISION_RECORD_CTA_EDGE_05_F6.md", REPO,
  "POST-SEAL: includes the additive §12 seal authorization entry"),
 ("final_independent_astra_review",
  "research/extensions/review_history/"
  "F6_FINAL_INDEPENDENT_REVIEW_2026-09-21_ASTRA_01.md", REPO,
  "active independent review authority; PASS. Did NOT authorize the seal."),
 ("final_independent_astra_review_sidecar",
  "research/extensions/review_history/"
  "F6_FINAL_INDEPENDENT_REVIEW_2026-09-21_ASTRA_01.md.sha256", REPO,
  "checksum sidecar copied verbatim; this manifest entry is the binding pin"),
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
  "original bytes, NO original hash, NOT independent evidence, NOT recovered"),
 ("sample_reuse", "research/extensions/SAMPLE_REUSE.md", REPO,
  "T0_REUSED_DEPENDENT classification authority"),
 ("trial_ledger_post_append", "research/extensions/TRIAL_LEDGER.md", REPO,
  "POST-APPEND. Carries the F-F6 prospective family row, SEALED / NOT "
  "EXECUTED. This is the AUTHORITATIVE TRIAL_LEDGER pin."),
 ("exposure_ledger", "ops/EXPOSURE_LEDGER.md", REPO,
  "UNCHANGED by the seal; no outcome revealed, so no EXPOSURE_EVENT exists"),
 ("spy_panel_authority", "data/close_prices_raw.csv", REPO,
  "frozen single-vendor adjusted-close panel; EXECUTION PROXY"),
 ("dgs3mo_authority", "data/DGS3MO.csv", REPO,
  "Owner-chosen ex-post cash opportunity-cost proxy source"),
 ("tom_authority_contract", "research/seasonality/PREREGISTRATION.md", REPO,
  "sealed seasonality contract defining TOM"),
 ("tom_authority_implementation", "src/seasonality.py", REPO,
  "sealed is_tom implementation reused verbatim"),
 ("ta_auction_authority_contract",
  "research/extensions/ta/TA_PREREGISTRATION.md", REPO,
  "sealed TA object pinning the 10y/30y auction definition"),
 ("ta_auction_calendar", "research/extensions/ta/TA_EVENT_CALENDAR.csv", REPO,
  "auction dates used to build AUCTION(d)"),
 ("preseal_validation_evidence", F6 + "/F6_S1_PRESEAL_VALIDATION.json", REPO,
  "final pre-seal mechanical validation, 0 failing checks"),
 ("preseal_validation_script", F6 + "/f6_s1_preseal_validate.py", REPO,
  "the validator that produced it"),
 ("preseal_manifest", F6 + "/F6_S1_PRESEAL_MANIFEST.json", REPO,
  "SUPERSEDED by this sealed manifest; retained as the accepted pre-seal state"),
 ("s1_preregistration_draft", F6 + "/F6_S1_PREREGISTRATION_DRAFT.md", REPO,
  "SUPERSEDED by the sealed contract; retained unmodified"),
 ("round1_f6_authority",
  "2026-09-15-cta-edge-discovery-r1-mechanism-feature-map-fable-01.md", WS,
  "original Round-1 F6 fields 1-15"),
 ("od_1a_1h", "Research Reports/"
  "2026-09-20-cta-edge-05-f6-od-1a-1h-s0-design-decisions-fable-01.md", WS,
  "OD-1 S0 design decisions (Fable advice, not review, not authorization)"),
 ("od_2a_2h", "Research Reports/"
  "2026-09-20-cta-edge-05-f6-od-2a-2h-pooling-control-gates-fable-01.md", WS,
  "OD-2 pooling and control gates. Its Monday-reference prose is SUPERSEDED "
  "by the canonical Friday reference; OD-2 itself is NOT rewritten and its "
  "own text records that the EVENT coefficient is invariant to that choice."),
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

lp = pins["trial_ledger_post_append"]["sha256"]
if lp == PRE_APPEND_LEDGER:
    raise SystemExit("REFUSING: TRIAL_LEDGER pin is still the PRE-APPEND hash")

val = json.load(open(os.path.join(F6, "F6_S1_PRESEAL_VALIDATION.json"),
                     encoding="utf-8"))
head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                      text=True).stdout.strip()

out = {
 "schema": {"name": "f6-s1-sealed-manifest", "version": 1},
 "lineage": "CTA-EDGE-05 / F6 MACRO_ANNOUNCEMENT_PREMIUM",
 "seal_id": "CTA-EDGE-05-F6-S1-2026-09-21",
 "seal_date": "2026-09-21",
 "SEAL_STATUS": "SEALED",
 "sealed": True,
 "owner_seal_authorization": True,
 "authorization_literal": "seal",
 "authorized_by": "Aaron (Owner)",
 "no_return_exposure_before_seal": True,
 "preseal_commit": "96901c48a0e5fe8cfd3d5e46db204a6e5a0e21f6",
 "generated": dt.date.today().isoformat(),
 "git_head_at_generation": head,

 "supersedes": {
   "preseal_manifest": pins["preseal_manifest"]["sha256"],
   "s1_preregistration_draft": pins["s1_preregistration_draft"]["sha256"],
   "note": "Superseded artifacts are RETAINED UNMODIFIED as the accepted "
           "pre-seal state. Supersession is by citation, never by rewriting."},

 "trial_ledger_pin_discipline": {
   "authoritative_pin": "trial_ledger_post_append",
   "post_append_sha256": lp,
   "pre_append_sha256_NOT_AUTHORITATIVE": PRE_APPEND_LEDGER,
   "note": "This manifest was generated AFTER the F-F6 append. The "
           "pre-append hash is recorded only to make the transition "
           "auditable; it is explicitly NOT the authoritative pin."},

 "authorization_chain": {
   "fable": "constructive design advice (OD-1, OD-2, OD-TY / OD-CASH). "
            "NOT review, NOT authorization.",
   "astra": "independent adversarial review. PASS / "
            "B_READY_FOR_S1_SEAL_WITH_CLAIM_CAP_NARROWING. "
            "S1_SEAL_AUTHORIZED_BY_THIS_REVIEW = NO.",
   "owner": "Aaron. Adoption, and the SOLE seal authorization: \"seal\".",
   "never_collapse": True,
   "historical_provenance_reservation": {
     "value": True, "blocking": False,
     "note": "The pre-S0 independent artifact was NEVER PERSISTED and is NOT "
             "RECOVERED. Nothing in this seal claims otherwise."}},

 "design_changed_at_seal": False,
 "canonical_weekday_parameterization": {
   "weekday_reference": "FRIDAY",
   "included_indicators": ["Monday", "Tuesday", "Wednesday", "Thursday"],
   "with_intercept": True,
   "status": "CANONICAL PARAMETERIZATION of the already-accepted full-rank "
             "weekday control space. NOT a new model, NOT a design change.",
   "superseded_prose": "OD-2 described the same space with Monday as "
             "reference AND in the same sentence recorded that the EVENT "
             "coefficient is invariant to the choice of reference. The sealed "
             "contract carries FRIDAY only. OD-2 is historical and NOT "
             "rewritten.",
   "verified_in_preseal_matrix": val["pooled_design"]["weekday_baseline"]},

 "frozen_constants": {
   "final_primary_event_count": val["final_event_count"],
   "family_labels": val["family_labels"],
   "family_labels_total": val["family_labels_total"],
   "multi_event_sessions": val["multi_event_sessions"],
   "overlap_adjustment": val["overlap_adjustment"],
   "primary_years": [2011, 2025],
   "y2026": "NO F6 OUTCOME QUANTITY MAY BE FORMED",
   "p2_rows": val["p2_rows"],
   "opening_boundary": val["opening_boundary"],
   "round_trip_cost": 0.0004,
   "cost_decomposition": "2 bps entry + 2 bps exit",
   "cash_proxy": "DGS3MO, rf_hold = (annual percent/100) * HOLD_calendar_days "
                 "/ 365. The /365 is OWNER-CHOSEN and must NEVER be "
                 "attributed to Treasury, H.15 or FRED.",
   "year_blocks": 15,
   "bootstrap_B": 100000,
   "bootstrap_seed_source": val["bootstrap"]["seed_source_string"],
   "bootstrap_seed_literal": val["bootstrap"]["seed_literal_uint32"],
   "interval": "two-sided nominal 95% percentile bootstrap",
   "lower_quantile": 0.025, "upper_quantile": 0.975,
   "quantile_implementation": "numpy.percentile(..., method=\"linear\")",
   "pinned_environment": {"numpy": "2.5.0", "pandas": "2.3.3",
                          "python": "3.13.14"},
   "environment_drift_rule": "If the execution environment differs, the "
     "implementation MUST still reproduce the sealed quantile semantics. Do "
     "NOT silently use a changed default.",
   "sample_reuse_class": "T0_REUSED_DEPENDENT",
   "evidence_ceiling": "SUPPORTED",
   "independent_confirmation": False,
   "pit_exclusions_permanent": ["NFP 2013-10-22", "CPI 2013-10-30 (label only)",
     "CPI 2013-11-20", "NFP 2025-11-20", "NFP 2025-12-16", "CPI 2025-12-18"],
   "post_seal_reinstatement": "FORBIDDEN"},

 "per_year_rank": val["per_year_rank"],
 "individual_year_matrix_rank_pass": val["individual_year_matrix_rank_pass"],
 "dgs3mo": val["dgs3mo"],

 "accounting": {
   "trial_ledger_changed": True,
   "f_f6_row_appended": True, "f_f6_row_count": 1,
   "f6_family_status": "SEALED / NOT EXECUTED",
   "f6_primary_trial_spent": False,
   "f6_primary_trial_consumed": False,
   "variant_attempt_rows_added": 0,
   "executed_trial_counter_incremented": False,
   "exposure_ledger_changed": False,
   "f6_performance_exposure_added": False,
   "exposure_reason": "An EXPOSURE_EVENT is a computation or read that REVEALS "
     "OUTCOMES OR MEASUREMENTS. None exists for F6, so there is no row to "
     "append and no new exposure type was invented."},

 "post_seal_state": {
   "S1": "SEALED", "S2_BUILD_AUTHORIZED": True,
   "S3_RUN_AUTHORIZED": False, "RETURN_REVEAL_AUTHORIZED": False,
   "note": "S2 authorizes code and build work ONLY. The historical run stays "
           "forbidden until S2 implementation is complete, implementation "
           "acceptance passes, and a SEPARATE S3 run authorization is issued "
           "by Aaron."},

 "firewall": dict(val["firewall"], seal_operation_outcome_blind=True),

 "self_reference_policy": "This manifest pins the seal record; the seal record "
   "does NOT pin this manifest, which would be a hash cycle. This manifest's "
   "own SHA256 is recorded EXTERNALLY in the seal commit message and the task "
   "return.",

 "pins": pins,
}

p = os.path.join(F6, "F6_S1_SEALED_MANIFEST.json")
with open(p, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(out, fh, indent=1, sort_keys=True)
    fh.write("\n")
print("wrote %s" % p)
print("pins: %d   all present" % len(pins))
print("POST-APPEND TRIAL_LEDGER pin: %s" % lp)
print("FINAL_SEALED_MANIFEST_SHA256 %s" % sha(p))
