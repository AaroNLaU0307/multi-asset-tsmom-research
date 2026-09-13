# -*- coding: utf-8 -*-
"""The S3 study orchestration: the sealed contract, executed end to end.

This module connects components that already exist. It introduces no scientific
choice: every constant comes from `value_contract`, every rule from
`value_signal` / `value_inference` / `value_portfolio`, the sleeve from
`value_sleeve` (§4) and the comparator from `value_comparator` (§17).

The order is the sealed order, and the FULL stage is genuinely conditional: when
candidacy fails, `ΔS_combo` is never computed — not computed and withheld, but
never computed at all.

`fixtures` exists so the synthetic rehearsal drives this identical code path
with controlled inputs. Production passes None.
"""
import datetime
import os
import sys
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for _p in (_REPO, HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import value_comparator as K        # noqa: E402
import value_contract as C          # noqa: E402
import value_data as D              # noqa: E402
import value_evidence as EV         # noqa: E402
import value_inference as I         # noqa: E402
import value_portfolio as VP        # noqa: E402
import value_signal as VS           # noqa: E402
import value_sleeve as SL           # noqa: E402


class StudyError(RuntimeError):
    pass


def _utc_now():
    return datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ")


def _ci_public(ci):
    """The interval as it enters the artifact."""
    return {"lower": ci["lower"], "upper": ci["upper"],
            "level": ci["level"], "n_valid": ci["n_valid"]}


def run_study(run_id=None, authorization_id=None, sources=None, panel=None,
              fixtures=None, outcome_exposure_state="GENERATED_NOT_SEEN"):
    """Execute the sealed study once and return the evidence artifact."""
    run_id = run_id or ("VALUE_S3_RUN_" + uuid.uuid4().hex[:16])
    diagnostics = {"started_utc": _utc_now()}
    counts = {}

    # -- 1. the active sealed contract --------------------------------------
    ok, checks = C.conformance()
    if not ok:
        failed = [l for l, c, _d in checks if not c]
        raise StudyError("the sealed contract does not conform: %s" % failed)

    # -- 2. comparator identity and input provenance ------------------------
    if fixtures is None:
        ok, kchecks = K.verify_identity()
        if not ok:
            failed = [l for l, c, _d in kchecks if not c]
            raise StudyError("the §17 comparator identity failed: %s" % failed)

    # -- 3-6. the Value sleeve (objects -> signals -> weights -> net returns)
    if fixtures is not None:
        months = list(fixtures["months"])
        value_net = list(fixtures["value_net"])
        signals = fixtures["signals"]
        sleeve_diag = dict(fixtures.get("sleeve_diagnostics", {}))
        ledger = fixtures.get("ledger")
    else:
        months = D.m_range(C.EVAL_START, C.EVAL_END)
        months, value_net, sleeve_diag, ledger = SL.build_sleeve(
            months, sources, panel)
        signals = SL.signals_on(months, sources)
    diagnostics["sleeve"] = sleeve_diag

    # -- 7. the frozen comparator, recomputed -------------------------------
    if fixtures is not None:
        comp_months, comp_net = list(months), list(fixtures["comparator_net"])
    else:
        comp_months, comp_net = K.comparator_window(months[0], months[-1])

    # -- 8. align on the sealed window --------------------------------------
    if comp_months != months:
        raise StudyError("the comparator and the Value sleeve are not aligned")
    if len(months) != C.N_MONTHS:
        raise StudyError("the sample is %d months; the contract seals %d"
                         % (len(months), C.N_MONTHS))
    if not (len(value_net) == len(comp_net) == len(months)):
        raise StudyError("paired series lengths disagree")

    # -- 9-10. Object A, standalone edge, and C1 ----------------------------
    sa = I.standalone_ci(value_net, months=months)
    counts["standalone"] = dict(sa["counts"])
    standalone_state = I.standalone_verdict(sa["lower"], sa["upper"])
    c1 = I.c1_pass(standalone_state)

    # -- 11-12. dependence with the frozen comparator, and C2 ---------------
    cc = I.correlation_ci(value_net, comp_net, months=months)
    counts["correlation"] = dict(cc["counts"])
    rho_upper = cc["upper"]
    c2 = I.c2_pass(rho_upper)

    # -- 13. the k = 3 sealed episodes, from the signal path only -----------
    episodes = VS.select_episodes(signals, k=C.K_EPISODES)
    if len(episodes) < C.K_EPISODES:
        raise StudyError(
            "only %d episodes exist; the contract seals k = %d"
            % (len(episodes), C.K_EPISODES))

    # -- 14-15. contribution ablation per episode, then C3 ------------------
    # AMENDMENT_003: remove the episode instrument's own attributed net
    # contribution in the mapped contribution months. Every calendar month is
    # retained, every other instrument is untouched, nothing is re-sized,
    # re-targeted, re-scaled or redistributed, and each case starts from the
    # ORIGINAL series.
    if ledger is None:
        raise StudyError("C3 requires the contribution ledger")
    if not ledger.get("reconciles"):
        raise StudyError("the contribution ledger does not reconcile")

    def adjudicate(episode):
        ablated, ablated_months = SL.ablate(months, value_net, ledger, episode)
        r_sa = I.standalone_ci(ablated, months=months)
        r_state = I.standalone_verdict(r_sa["lower"], r_sa["upper"])
        r_cc = I.correlation_ci(ablated, comp_net, months=months)
        return {
            "c1": I.c1_pass(r_state),
            "c2": I.c2_pass(r_cc["upper"]),
            "ablated_contribution_months": ablated_months,
            "standalone_ci": _ci_public(r_sa),
            "standalone_state": r_state,
            "correlation_point_estimate": I.pearson(ablated, comp_net),
            "correlation_ci": _ci_public(r_cc),
            "bootstrap_counts": {"standalone": dict(r_sa["counts"]),
                                 "correlation": dict(r_cc["counts"])},
        }

    raw_cases = I.run_c3_ablation(months, episodes, adjudicate,
                                  k=C.K_EPISODES)

    c3_cases = []
    for episode, case in zip(episodes[:C.K_EPISODES], raw_cases):
        mapped = SL.contribution_months(episode, months)
        entry = {
            "EPISODE_IDENTITY": repr(episode),
            "INSTRUMENT": episode.instrument,
            "EPISODE_SIGNAL_MONTHS": list(episode.months),
            "ABLATED_CONTRIBUTION_MONTHS": case.get(
                "ablated_contribution_months", mapped),
            "CONTRIBUTION_ACCOUNTING_IDENTITY": ledger["identity"],
            "C1_RESULT": bool(case["c1"]),
            "CORRELATION_STATISTIC": case.get("correlation_point_estimate"),
            "CORRELATION_CI": case.get("correlation_ci"),
            "C2_RESULT": bool(case["c2"]),
            "INFERENCE_VALIDITY": ("VALID" if not case.get("invalid")
                                   else "INVALID"),
            # retained for continuity with the rest of the artifact
            "episode": repr(episode),
            "instrument": episode.instrument,
            "start": episode.start,
            "end": episode.end,
            "sign": int(episode.sign),
            "months_retained": len(months),
            "standalone_ci": case.get("standalone_ci"),
            "standalone_state": case.get("standalone_state"),
            "c1": bool(case["c1"]),
            "correlation_ci": case.get("correlation_ci"),
            "c2": bool(case["c2"]),
            "valid": not case.get("invalid", False),
        }
        if case.get("invalid"):
            entry["invalid_reason"] = case.get("reason")
        else:
            for arm, c in (case.get("bootstrap_counts") or {}).items():
                counts["c3_%s_%s_%s"
                       % (episode.instrument, episode.start, arm)] = c
        c3_cases.append(entry)

    c3 = I.c3_pass(raw_cases, k=C.K_EPISODES)

    # -- 16. candidacy -------------------------------------------------------
    cand = I.candidacy(standalone_state, rho_upper, raw_cases)

    # -- 17. the FULL stage, genuinely conditional --------------------------
    full_executed = bool(cand["candidate"])
    full_block = {}
    if full_executed:
        combined = VP.combine(comp_net, value_net,
                              w_tsmom=C.SPLIT_TSMOM, w_value=C.SPLIT_VALUE)
        fc = I.combo_ci(comp_net, list(combined), months=months)
        counts["combo"] = dict(fc["counts"])
        full_block = {
            "FULL_STATISTICS": {
                "estimand": "delta_sharpe_combo",
                "definition": "Sharpe(TSMOM + Value) - Sharpe(TSMOM)",
                "split_tsmom": C.SPLIT_TSMOM,
                "split_value": C.SPLIT_VALUE,
                "point_estimate": (I.sharpe(list(combined))
                                   - I.sharpe(comp_net)),
            },
            "FULL_CI": _ci_public(fc),
            "FULL_STATE": I.combo_verdict(fc["lower"], fc["upper"]),
        }

    # -- 18-20. the evidence artifact, with provenance and accounting -------
    diagnostics["finished_utc"] = _utc_now()
    diagnostics["episodes_considered"] = len(
        VS.rank_episodes([e for inst in signals
                          for e in VS.episodes_for(inst, signals[inst])]))
    diagnostics["credit_duration_overlap_note"] = (
        "§10 declares the credit-duration overlap DIAGNOSTIC ONLY; it carries "
        "no adjudicating power")

    ev = {
        "schema": EV.SCHEMA,
        "RUN_ID": run_id,
        "AUTHORIZATION_ID": authorization_id,
        "SEALED_PREREG_SHA256": C.SEALED_PREREG_SHA256,
        "SEAL_REVISION": C.SEAL_REVISION,
        # Derived from the contract's single authoritative definition. Never
        # hand-assembled: pairing a hardcoded label with live seal constants is
        # what produced the stale-_002 row in the 2026-09-13 artifact.
        "AMENDMENT_LINEAGE": C.lineage_records(),
        "CODE_IDENTITY": _code_identity(),
        "INPUT_PROVENANCE": _input_provenance(synthetic=fixtures is not None),
        "EVALUATION_START": months[0],
        "EVALUATION_END": months[-1],
        "N": len(months),

        "VALUE_STANDALONE_STATISTICS": {
            "statistic": "annualised net Sharpe against a zero benchmark",
            "periods_per_year": I.SHARPE_PERIODS_PER_YEAR,
            "point_estimate": I.sharpe(value_net),
        },
        "VALUE_STANDALONE_CI": _ci_public(sa),
        "VALUE_STANDALONE_STATE": standalone_state,
        "C1": bool(c1),

        "VALUE_TSMOM_CORRELATION": {
            "statistic": "Pearson correlation, Value vs frozen TSMOM, monthly net",
            "comparator": C.TSMOM_COMPARATOR,
            "point_estimate": I.pearson(value_net, comp_net),
            "adjudicated_on": "the upper bound of the 95% interval",
            "rho_max": C.RHO_MAX,
        },
        "CORRELATION_CI": _ci_public(cc),
        "C2": bool(c2),

        "C3_INTERPRETATION": C.C3_INTERPRETATION,
        "C3_OPERATOR": C.C3_OPERATOR,
        "C3_PERMITTED_CLAIM": C.C3_PERMITTED_CLAIM,
        "C3_FORBIDDEN_CLAIM": C.C3_FORBIDDEN_CLAIM,
        "C3_KNOWN_LIMITATION": C.C3_KNOWN_LIMITATION,
        "CONTRIBUTION_LEDGER": {
            "identity": ledger["identity"],
            "contribution_definition": ledger["contribution_definition"],
            "shared_term_policy": ledger["shared_term_policy"],
            "signal_to_contribution_month": ledger[
                "signal_to_contribution_month"],
            "timing_map": ledger["timing_map"],
            "tolerance": ledger["tolerance"],
            "max_abs_residual": ledger["max_abs_residual"],
            "reconciles": ledger["reconciles"],
            "weight_redistribution": False,
            "vol_retarget_after_ablation": False,
            "gross_rescale_after_ablation": False,
            "ablations_cumulative": False,
        },
        "SELECTED_EPISODES": [
            {"instrument": e.instrument, "start": e.start, "end": e.end,
             "months": len(e.months), "sign": int(e.sign)}
            for e in episodes[:C.K_EPISODES]],
        "C3_CASES": c3_cases,
        "C3": bool(c3),
        "CANDIDACY": dict(cand),

        "FULL_EXECUTED": full_executed,

        "BOOTSTRAP_COUNTS": counts,
        "DIAGNOSTICS": diagnostics,
        "SHILLER_VINTAGE_LIMITATION": C.SHILLER_VINTAGE_STATUS,
        "EVIDENCE_CEILING": C.EVIDENCE_CEILING,
        "OUTCOME_EXPOSURE_STATE": outcome_exposure_state,
    }
    ev.update(full_block)

    ok, problems = EV.validate(ev)
    if not ok:
        raise StudyError("the evidence artifact is structurally invalid: %s"
                         % problems)
    return ev


def _code_identity():
    import hashlib
    import io
    out = {}
    for name in ("value_contract.py", "value_data.py", "value_signal.py",
                 "value_inference.py", "value_portfolio.py",
                 "value_comparator.py", "value_sleeve.py",
                 "value_orchestrator.py", "value_evidence.py",
                 "value_authorization.py", "value_runner.py"):
        p = os.path.join(HERE, name)
        if os.path.exists(p):
            out[name] = hashlib.sha256(io.open(p, "rb").read()).hexdigest()
    for rel in sorted(K.CANONICAL_CODE_SHA256):
        out[rel] = K.code_sha256(rel)
    return out


def _input_provenance(synthetic=False):
    import hashlib
    import io
    prov = {
        "synthetic_fixtures": bool(synthetic),
        "comparator": K.provenance(),
    }
    if synthetic:
        prov["note"] = ("SYNTHETIC REHEARSAL — these inputs are fabricated and "
                        "carry no research meaning")
        return prov
    raws = {}
    for key, fname in sorted(C.RAW_INPUTS.items()):
        p = os.path.join(_REPO, C.RAW_DIR, fname)
        if os.path.exists(p):
            raws[key] = {
                "file": "%s/%s" % (C.RAW_DIR, fname),
                "sha256_of_raw_file_on_disk":
                    hashlib.sha256(io.open(p, "rb").read()).hexdigest(),
            }
        else:
            raws[key] = {"file": "%s/%s" % (C.RAW_DIR, fname),
                         "MISSING": True}
    prov["value_raw_inputs"] = raws
    prov["hash_convention"] = ("RAW file sha256; data/ is git-ignored so raw "
                               "bytes are pinned here")
    return prov
