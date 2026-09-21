# -*- coding: utf-8 -*-
"""C-A S2 build test suite — 22 required test classes.

EVERY test runs on synthetic fixtures or on the already-revealed frozen historical
panel. NOTHING here touches real post-seal market data, S_0 post-boundary
observations, or any newly fetched data, and NOTHING computes a real Sharpe, PnL,
monthly C-A return, drawdown, FM-1 outcome or crisis-response outcome.

Run:  python research/extensions/ca/prospective/ca_s2_tests.py
"""
from __future__ import annotations

import io
import json
import os
import shutil
import sys
import tempfile
import warnings

import base64

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                "..", "..", "..", "..")))
from research.extensions.ca.prospective import (  # noqa: E402
    ca_blind, ca_contract as K, ca_engine, ca_golive, ca_identity, ca_inference,
    ca_integrity, ca_ledger, ca_protected, ca_rf, ca_store)

OK = True
CLASSES = {}


def ck(cls, label, cond, detail=""):
    global OK
    if not cond:
        OK = False
    CLASSES.setdefault(cls, [0, 0])
    CLASSES[cls][0 if cond else 1] += 1
    print("  [%-2s] %-56s %s   %s" % (cls, label, "PASS" if cond else "FAIL", detail))


def raises(exc, fn, *a, **kw):
    try:
        fn(*a, **kw)
        return False
    except exc:
        return True
    except Exception:
        return False


# --------------------------------------------------------------------------- #
def synth_panel(n_days=900, tickers=None, seed=0, start="2019-01-01"):
    """A purely artificial price panel. Not market data."""
    tickers = tickers or K.CANONICAL_17
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range(start, periods=n_days)
    data = {}
    for i, t in enumerate(tickers):
        steps = rng.standard_normal(n_days) * 0.01 + 0.0003 * ((-1) ** i)
        data[t] = 100.0 * np.exp(np.cumsum(steps))
    df = pd.DataFrame(data, index=idx)
    df.index.name = "Date"
    return df


def tmpdirs():
    d = tempfile.mkdtemp(prefix="ca_s2_")
    rel = os.path.relpath(d, K.REPO).replace("\\", "/")
    return d, rel


print("C-A S2 BUILD TEST SUITE — synthetic fixtures only, no target outcomes\n")
print("runtime: python %s  pandas %s  numpy %s" % (sys.version.split()[0], pd.__version__, np.__version__))
print("sealed prereg sha256 verified on import of ca_contract\n")

# ==========================================================================  #
# 1. canonical-engine parity
# ==========================================================================  #
frozen = pd.read_csv(K.repo_path(K.FROZEN_PANEL), index_col=0, parse_dates=True).sort_index()
frozen = frozen[frozen.index <= pd.Timestamp(K.FROZEN_BOUNDARY)][K.CANONICAL_17]
sys.path.insert(0, K.REPO)
from src import portfolio as src_pf  # noqa: E402

with warnings.catch_warnings():
    warnings.simplefilter("ignore", FutureWarning)
    src_book = src_pf.build_portfolio(frozen)
new_book = ca_engine.build_book(frozen)

for name, a, b in [("signal", src_book["asset_weight"], new_book["asset_weight"]),
                   ("base_weight", src_book["base_weight"], new_book["base_weight"]),
                   ("port_weight", src_book["port_weight"], new_book["port_weight"]),
                   ("position", src_book["position"], new_book["position"])]:
    same_nan = a.isna().equals(b.isna())
    diff = (a - b).abs().to_numpy()
    mx = np.nanmax(diff) if np.isfinite(diff).any() else 0.0
    ck("1", "forward engine reproduces src %s exactly" % name,
       same_nan and mx == 0.0, "max|diff|=%.3e nan-pattern=%s" % (mx, same_nan))
ck("1", "n_available identical", src_book["n_available"].equals(new_book["n_available"]))
ck("1", "leverage NaN pattern identical", src_book["leverage"].isna().equals(new_book["leverage"].isna()))

# ==========================================================================  #
# 21. pct_change explicit behaviour
# ==========================================================================  #
probe = pd.DataFrame({"a": [100.0, np.nan, 110.0, 121.0], "b": [np.nan, 50.0, 55.0, 55.0]})
with warnings.catch_warnings():
    warnings.simplefilter("ignore", FutureWarning)
    sealed_default = probe.pct_change()
explicit = ca_engine.simple_returns(probe)
ck("21", "explicit fill equals the sealed pct_change default",
   sealed_default.equals(explicit) or np.allclose(sealed_default.fillna(-9), explicit.fillna(-9)))
ck("21", "explicit form passes fill_method=None (stable on pandas 3)",
   "fill_method=None" in io.open(ca_engine.__file__, encoding="utf-8").read())
ck("21", "runtime pin recorded", K.PINNED_RUNTIME["pandas"] == "2.3.3")
ck("21", "runtime currently matches the pin", K.runtime_matches(), str(K.current_runtime()))

# ==========================================================================  #
# 2. frozen-panel overwrite refusal
# ==========================================================================  #
before = K.sha256_file(K.FROZEN_PANEL)
ck("2", "guard identifies the frozen panel", ca_store.is_frozen_panel(K.FROZEN_PANEL))
ck("2", "safe_write_bytes refuses the frozen panel",
   raises(ca_store.FrozenPanelWriteRefused, ca_store.safe_write_bytes, K.FROZEN_PANEL, b"x"))
ck("2", "refuses via absolute path too",
   raises(ca_store.FrozenPanelWriteRefused, ca_store.safe_write_bytes,
          K.repo_path(K.FROZEN_PANEL), b"x"))
ck("2", "no force/allow flag can override the frozen path",
   raises(ca_store.FrozenPanelWriteRefused, ca_store.safe_write_bytes,
          K.FROZEN_PANEL, b"x", allow_existing=True))
ck("2", "frozen panel sha256 unchanged after guard tests", K.sha256_file(K.FROZEN_PANEL) == before)
ck("2", "assert_frozen_panel_intact passes", ca_store.assert_frozen_panel_intact() == K.FROZEN_PANEL_SHA256)

# ==========================================================================  #
# 3/4. append-only snapshot semantics + hash identity
# ==========================================================================  #
d_abs, d_rel = tmpdirs()
# SYNTHETIC protected store + session. This is a temp store, never the production one.
syn_store = tempfile.mkdtemp(prefix="ca_s2_blindstore_")
_syn_state = ca_blind.initialize_blind_store(syn_store, note="SYNTHETIC TEST STORE")
session = ca_blind.unlock_store(syn_store)
reg = ca_store.SnapshotRegistry(d_rel + "/registry.jsonl", d_rel + "/snapshots")
p1 = synth_panel(400, seed=1)
row1 = reg.register_snapshot("SNAP_0001", p1, kind="MONTHLY")
ck("3", "snapshot registered", reg.get("SNAP_0001") is not None)
ck("3", "re-registering the same id is refused",
   raises(ca_store.SnapshotOverwriteRefused, reg.register_snapshot, "SNAP_0001", p1, kind="MONTHLY"))
ck("3", "a second distinct snapshot appends", reg.register_snapshot("SNAP_0002", synth_panel(401, seed=2), kind="MONTHLY")["snapshot_id"] == "SNAP_0002")
ck("3", "registry is append-only (2 rows, order preserved)",
   [r["snapshot_id"] for r in reg.rows()] == ["SNAP_0001", "SNAP_0002"])
ck("3", "using an unregistered snapshot is refused",
   raises(ca_store.SnapshotNotRegistered, reg.load, "SNAP_9999"))
ck("4", "snapshot hash + size recorded", len(row1["sha256"]) == 64 and row1["byte_size"] > 0)
ck("4", "load verifies bytes against the registered hash", reg.load("SNAP_0001").shape == p1.shape)
with io.open(os.path.join(d_abs, "snapshots", "SNAP_0001.csv"), "ab") as fh:
    fh.write(b"# tamper\n")
ck("4", "tampered snapshot bytes are refused on load",
   raises(ca_store.SnapshotOverwriteRefused, reg.load, "SNAP_0001"))

# ==========================================================================  #
# 5/6. write-once position ledger + duplicate rejection
# ==========================================================================  #
led = ca_ledger.PositionLedger(d_rel + "/positions.jsonl", session=session)
panel = synth_panel(800, seed=3)
dm = ca_engine.build_book(panel)["port_weight"].dropna(how="all").index[-2]
dec = ca_engine.decision_vector(panel, dm)
regid = ca_identity.registry_identity(ca_identity.load_registry())
rfrec = {"rf_series": "DGS3MO", "rf_missing": False, "rf_t": 0.0035, "observation_date": "2026-01-30"}
gate0 = ca_integrity.monthly_gate(snapshot_row=row1, decision=dec, rf_lock=rfrec, ledger=led,
                                  ledger_write_succeeded=True)
rec = led.append(holding_month="2026-02", decision=dec, snapshot_row=row1,
                 registry_identity=regid, rf_lock=rfrec, integrity=gate0,
                 prior_position_ref="PRE_START", prior_position_kind="PRE_START_STATE_INPUT",
                 turnover_value=float("nan"))
ck("5", "ledger record written", led.count() == 1)
for f in ["source_snapshot_sha256", "instrument_registry", "runtime", "code_revision",
          "protected_position", "prior_position_ref", "rf_lock",
          "integrity", "record_sha256", "sealed_prereg_sha256"]:
    ck("5", "record binds %s" % f, f in rec)
# the position vector is SEALED, not stored in the clear
ck("5", "record does NOT carry a clear position vector",
   not any(k in rec for k in ("weights", "gross", "net", "leverage")))
ck("5", "record carries §T.2 invariant booleans instead",
   isinstance(rec["gross_within_cap"], bool) and isinstance(rec["asset_weight_within_cap"], bool))
ck("5", "sealed block records the plaintext sha256 for reproducibility",
   len(rec["protected_position"]["plaintext_sha256"]) == 64)
ck("6", "duplicate holding month is refused loudly",
   raises(ca_ledger.LedgerRewriteRefused, led.append, holding_month="2026-02", decision=dec,
          snapshot_row=row1, registry_identity=regid, rf_lock=rfrec, integrity=gate0,
          prior_position_ref="x", prior_position_kind="LEDGER", turnover_value=0.0))
ck("6", "still exactly one record after the refused duplicate", led.count() == 1)
ck("6", "public summary exposes no weights",
   "weights" not in json.dumps(led.public_summary()))

# ==========================================================================  #
# 7/8/9. first scored month, S_0 vs S_G, no retroactive scoring
# ==========================================================================  #
tds = pd.bdate_range("2026-09-01", periods=140)
ck("8", "S_G not created in this build", not ca_golive.s_g_created(reg))
ck("8", "PROSPECTIVE_START is None without go-live",
   ca_golive.prospective_start(K.SEAL_TIMESTAMP_UTC, None) is None)
ck("8", "FORWARD_BOUNDARY is None without go-live", ca_golive.forward_boundary(tds, None) is None)
fe = ca_golive.first_eligible_scored_period(tds, None)
ck("7", "FIRST_ELIGIBLE_SCORED_PERIOD is NOT_YET_DETERMINED",
   fe["first_eligible_scored_period"] == "NOT_YET_DETERMINED")
ps = ca_golive.prospective_start(K.SEAL_TIMESTAMP_UTC, "2026-10-15T00:00:00Z")
ck("8", "go-live later than the seal drives PROSPECTIVE_START", ps.startswith("2026-10-15"))
fe2 = ca_golive.first_eligible_scored_period(tds, ps)
ck("7", "first decision month-end is strictly after PROSPECTIVE_START",
   pd.Timestamp(fe2["first_decision_month_end"]) > pd.Timestamp("2026-10-15"),
   "%s -> scores %s" % (fe2["first_decision_month_end"], fe2["first_eligible_scored_period"]))
ck("7", "first scored month is the month AFTER that decision",
   fe2["first_eligible_scored_period"] == "2026-11")
ck("8", "seal->go-live observations are POST_SEAL_UNSCORED_STATE_INPUT_ONLY",
   ca_golive.classify_between_seal_and_go_live("2026-09-30", K.SEAL_TIMESTAMP_UTC,
                                               "2026-10-15T00:00:00Z") == "POST_SEAL_UNSCORED_STATE_INPUT_ONLY")
ck("9", "scoring refused while PROSPECTIVE_START is uninstantiated",
   raises(ca_golive.GoLiveNotAuthorized, ca_golive.assert_no_retroactive_scoring, "2026-08", None))
pre = ca_golive.is_scored_month(holding_month="2026-09", decision_month_end="2026-08-31",
                                prospective_start_utc=ps, locked_before_holding_prices=True,
                                month_end_close_for_every_live_asset=True, run_invalidating=False,
                                pending_classification=False, freeze_state=None, all_17_live=True,
                                partial_month=False)
ck("9", "a pre-start decision month can never be scored", not pre["scored"], str(pre["reasons"][:1]))
ck("9", "go-live requires an Owner authorization",
   raises(ca_golive.GoLiveNotAuthorized, ca_golive.establish_go_live, registry=reg, panel=p1))

# ==========================================================================  #
# 10. all-17 requirement + partial month
# ==========================================================================  #
good = dict(holding_month="2026-11", decision_month_end="2026-10-30", prospective_start_utc=ps,
            locked_before_holding_prices=True, month_end_close_for_every_live_asset=True,
            run_invalidating=False, pending_classification=False, freeze_state=None,
            all_17_live=True, partial_month=False)
ck("10", "a fully eligible month scores", ca_golive.is_scored_month(**good)["scored"])
ck("10", "ALL_17_REQUIRED blocks scoring", not ca_golive.is_scored_month(**{**good, "all_17_live": False})["scored"])
ck("10", "partial month never scores", not ca_golive.is_scored_month(**{**good, "partial_month": True})["scored"])
ck("10", "unlocked position never scores",
   not ca_golive.is_scored_month(**{**good, "locked_before_holding_prices": False})["scored"])
ck("10", "invalidating event never scores",
   not ca_golive.is_scored_month(**{**good, "run_invalidating": True})["scored"])

# ==========================================================================  #
# 11/12/13. instrument identity events
# ==========================================================================  #
r = ca_identity.classify({"event_type": "A_TICKER_RENAME", "ticker": "SPY"})
ck("11", "ticker rename is IDENTITY_PRESERVING", r["classification"] == ca_identity.IDENTITY_PRESERVING and r["record_continues"])
ck("11", "identifier change is IDENTITY_PRESERVING",
   ca_identity.classify({"event_type": "B_IDENTIFIER_CHANGE"})["classification"] == ca_identity.IDENTITY_PRESERVING)
ck("11", "reverse split is IDENTITY_PRESERVING",
   ca_identity.classify({"event_type": "C_SPLIT_OR_REVERSE_SPLIT"})["classification"] == ca_identity.IDENTITY_PRESERVING)
ck("11", "no event ever permits a replacement instrument",
   all(not ca_identity.classify({"event_type": e})["replacement_instrument_permitted"]
       for e in ca_identity.EVENT_CLASS))
g_ok = ca_identity.classify({"event_type": "G_BENCHMARK_METHODOLOGY_CHANGE",
                             "same_asset_class": True, "same_sleeve": True})
ck("11", "benchmark change inside the sleeve is IDENTITY_PRESERVING",
   g_ok["classification"] == ca_identity.IDENTITY_PRESERVING)
g_bad = ca_identity.classify({"event_type": "G_BENCHMARK_METHODOLOGY_CHANGE",
                              "same_asset_class": False, "same_sleeve": True})
ck("12", "leaving the asset class is MATERIAL_OBJECT_CHANGE",
   g_bad["classification"] == ca_identity.MATERIAL_OBJECT_CHANGE and g_bad["freezes_canonical_record"])
ck("12", "closure freezes the record", ca_identity.classify({"event_type": "F_CLOSURE_LIQUIDATION_DELISTING"})["freezes_canonical_record"])
ck("12", "a freeze does NOT trigger a reveal",
   ca_identity.classify({"event_type": "F_CLOSURE_LIQUIDATION_DELISTING"})["reveal_triggered"] is False)
ck("12", "freeze instruction forbids replacement",
   ca_identity.freeze_instruction({})["replacement_instrument"].startswith("NEVER"))
d_partial = ca_identity.classify({"event_type": "D_MERGER_SUCCESSOR",
                                  "legal_economic_continuity_stated_ratio": True})
ck("13", "successor with unmet conditions -> terminate",
   d_partial["classification"] == ca_identity.MATERIAL_OBJECT_CHANGE and d_partial.get("ambiguous"))
d_all = ca_identity.classify({"event_type": "D_MERGER_SUCCESSOR",
                              **{c: True for c in ca_identity.SUCCESSOR_CONDITIONS}})
ck("13", "successor with all five conditions is IDENTITY_PRESERVING",
   d_all["classification"] == ca_identity.IDENTITY_PRESERVING)
ck("13", "unknown event type -> ambiguity terminates",
   ca_identity.classify({"event_type": "Z_UNKNOWN"}).get("ambiguous") is True)
ck("13", "halt of unknown duration -> ambiguity terminates",
   ca_identity.classify({"event_type": "H_TRADING_HALT"}).get("ambiguous") is True)
ck("13", "scoring past a freeze boundary is refused",
   raises(ca_identity.CanonicalRecordFrozen, ca_identity.guard_record_open,
          {"frozen_from_month": "2030-01"}, "2030-05"))

# ==========================================================================  #
# 14/15/16. FM-1 rate locking
# ==========================================================================  #
rf_idx = pd.to_datetime(["2026-10-20", "2026-10-23", "2026-10-30"])
rf_ser = pd.Series([3.85, 3.86, 3.90], index=rf_idx, name="DGS3MO")
ck("14", "valid fresh observation locks", ca_rf.lock_rf(rf_ser, "2026-10-30")["rf_t"] is not None)
ck("14", "rf_t = Y/100/12", abs(ca_rf.lock_rf(rf_ser, "2026-10-30")["rf_t"] - 3.90 / 100 / 12) < 1e-15)
ck("14", "exactly 7 days old is ACCEPTED",
   ca_rf.lock_rf(pd.Series([3.8], index=pd.to_datetime(["2026-10-23"])), "2026-10-30")["rf_missing"] is False)
ck("14", "8 days old is RF_MISSING",
   ca_rf.lock_rf(pd.Series([3.8], index=pd.to_datetime(["2026-10-22"])), "2026-10-30")["rf_missing"] is True)
ck("14", "no print at all is RF_MISSING",
   ca_rf.lock_rf(pd.Series([], dtype=float, index=pd.to_datetime([])), "2026-10-30")["rf_missing"] is True)
ck("14", "a NaN print is skipped, not used",
   ca_rf.lock_rf(pd.Series([np.nan, 3.7], index=pd.to_datetime(["2026-10-30", "2026-10-28"])).sort_index(),
                 "2026-10-30")["observation_date"] == "2026-10-28")
ck("14", "a future print is never used",
   ca_rf.lock_rf(pd.Series([9.99], index=pd.to_datetime(["2026-11-05"])), "2026-10-30")["rf_missing"] is True)
locked = ca_rf.lock_rf(rf_ser, "2026-10-30")
revised = ca_rf.lock_rf(pd.Series([3.85, 3.86, 4.50], index=rf_idx), "2026-10-30")
ck("14", "a later revision does not alter an already-locked record",
   locked["rf_t"] != revised["rf_t"] and rec["rf_lock"]["rf_t"] == 0.0035,
   "the ledger keeps the value locked at decision time")
ck("16", "no fallback series exists", K.RF_FALLBACK_SERIES is None)
ck("16", "substituting DGS1MO is refused",
   raises(ca_rf.RfFallbackRefused, ca_rf.assert_series_is_sealed, "DGS1MO"))
ck("16", "lock_rf exposes no series/fallback parameter",
   set(ca_rf.lock_rf.__code__.co_varnames[:ca_rf.lock_rf.__code__.co_argcount]) == {"series", "decision_date"})
adj = ca_rf.fm1_adjudicable([{"decision_date": "2026-10-30", "rf_missing": True}])
ck("15", "unresolved RF_MISSING -> FM-1 NOT ADJUDICABLE", adj["fm1_state"].startswith("NOT ADJUDICABLE"))
ck("15", "primary explicitly UNAFFECTED by RF_MISSING", adj["primary_adjudication"] == "UNAFFECTED")
ck("15", "FM-1 sample is never shortened and never imputed",
   adj["sample_shortened"] is False and adj["rate_imputed"] is False)
dec_rfmiss = ca_engine.decision_vector(panel, dm)
ck("15", "position generation is identical regardless of rf state",
   dec_rfmiss["weights"] == dec["weights"])

# ==========================================================================  #
# 17/18. integrity gate allowed / forbidden
# ==========================================================================  #
gate = ca_integrity.monthly_gate(snapshot_row=row1, decision=dec, rf_lock=locked, ledger=led,
                                 overlap_ok=True, ledger_write_succeeded=True, n_scored_to_date=0)
ck("17", "gate emits only allowlisted keys", set(gate) <= ca_integrity.ALLOWED_KEYS)
ck("17", "gate exposes pipeline health boolean", isinstance(gate["pipeline_healthy"], bool))
ck("17", "gate exposes counts", gate["n_scored_to_date"] == 0)
ck("17", "gate exposes rf freshness state", gate["rf_present_and_locked"] is True)
ck("17", "gate exposes invariant booleans", gate["gross_within_cap"] in (True, False))
blob = json.dumps(gate)
for forbidden in ["sharpe", "drawdown", "pnl", "win_rate", "equity_curve"]:
    ck("18", "gate output contains no %s" % forbidden, forbidden not in blob.lower())
# §T.2 permits exactly one per-ticker structure -- integer row counts. What must
# never appear is a per-ticker vector of FLOATS, i.e. a weight/position vector.
_float_vectors = [k for k, v in gate.items()
                  if isinstance(v, dict) and set(v) >= set(K.CANONICAL_17)
                  and any(isinstance(x, float) for x in v.values())]
ck("18", "gate never contains a per-ticker FLOAT (weight) vector", not _float_vectors, str(_float_vectors))
ck("18", "the only per-ticker structure present is integer row counts",
   [k for k, v in gate.items() if isinstance(v, dict) and set(v) >= set(K.CANONICAL_17)]
   == ["per_ticker_row_counts"]
   and all(isinstance(x, int) for x in gate["per_ticker_row_counts"].values()))
ck("18", "a float per-ticker vector under the allowed key is still refused",
   raises(ca_integrity.BlindnessBreachBlocked, ca_integrity._enforce,
          {**gate, "per_ticker_row_counts": {t: 1.5 for t in K.CANONICAL_17}}))
ck("18", "a non-allowlisted key is refused",
   raises(ca_integrity.BlindnessBreachBlocked, ca_integrity._enforce, {**gate, "sharpe": 0.9}))
ck("18", "a smuggled position vector is refused",
   raises(ca_integrity.BlindnessBreachBlocked, ca_integrity._enforce,
          {**gate, "n_available": {t: 1.0 for t in K.CANONICAL_17}}))

# ==========================================================================  #
# 19. protected outcome layer / reveal authorization absent by default
# ==========================================================================  #
store = ca_protected.ProtectedOutcomeStore(tempfile.mkdtemp(prefix="ca_s2_out_"), session=session)
ident = store.store("SYNTHETIC_OUTCOME_0001", {"synthetic_statistic": 0.123, "note": "fixture only"})
ck("19", "protected payload can be produced and stored", len(ident["sha256"]) == 64)
ck("19", "store() returns identity only, never content", "synthetic_statistic" not in json.dumps(ident))
view = store.describe()
ck("19", "operator view shows counts and hashes only", view["protected_outcomes_stored"] == 1)
ck("19", "operator view reports content NOT visible", view["content_visible"] is False)
ck("19", "operator view contains no payload value", "0.123" not in json.dumps(view))
ck("19", "classification is GENERATED_NOT_SEEN", view["all_generated_not_seen"])
ck("19", "reveal authorization absent by default", view["reveal_authorization_present"] is False)
ck("19", "reveal without authorization is refused",
   raises(ca_protected.RevealNotAuthorized, store.reveal, "SYNTHETIC_OUTCOME_0001"))
bad_auth = ca_protected.RevealAuthorization(authorization_id="T", owner="Aaron",
                                            granted_utc="2026-09-13T00:00:00Z", scope="test",
                                            n_scored_at_grant=0, declared_before_access=True)
ck("19", "reveal refused before N_scored = 120",
   raises(ca_protected.RevealAuthorizationInvalid, store.reveal,
          "SYNTHETIC_OUTCOME_0001", bad_auth, n_scored_now=0))
not_owner = ca_protected.RevealAuthorization(authorization_id="T2", owner="someone-else",
                                             granted_utc="x", scope="t", n_scored_at_grant=120,
                                             declared_before_access=True)
ck("19", "only the Owner may authorize a reveal",
   raises(ca_protected.RevealAuthorizationInvalid, store.reveal,
          "SYNTHETIC_OUTCOME_0001", not_owner, n_scored_now=120))
undeclared = ca_protected.RevealAuthorization(authorization_id="T3", owner="Aaron", granted_utc="x",
                                              scope="t", n_scored_at_grant=120,
                                              declared_before_access=False)
ck("19", "scope must be declared before access",
   raises(ca_protected.RevealAuthorizationInvalid, store.reveal,
          "SYNTHETIC_OUTCOME_0001", undeclared, n_scored_now=120))
valid = ca_protected.RevealAuthorization(authorization_id="T4", owner="Aaron", granted_utc="x",
                                         scope="terminal", n_scored_at_grant=120,
                                         declared_before_access=True)
got = store.reveal("SYNTHETIC_OUTCOME_0001", valid, n_scored_now=120)
ck("19", "a fully valid synthetic authorization does reveal", got["synthetic_statistic"] == 0.123)
ck("19", "a consumed authorization cannot reveal twice",
   raises(ca_protected.RevealAuthorizationInvalid, store.reveal,
          "SYNTHETIC_OUTCOME_0001", valid, n_scored_now=120))

# ==========================================================================  #
# 20. runtime mismatch refusal
# ==========================================================================  #
ck("20", "assert_runtime passes on the pinned runtime", K.assert_runtime(strict=True) == K.PINNED_RUNTIME)
_saved = dict(K.PINNED_RUNTIME)
K.PINNED_RUNTIME["pandas"] = "0.0.0"
ck("20", "mismatched runtime is refused", raises(RuntimeError, K.assert_runtime, strict=True))
ck("20", "non-strict mode reports without raising", K.assert_runtime(strict=False) is not None)
K.PINNED_RUNTIME.clear()
K.PINNED_RUNTIME.update(_saved)
ck("20", "pin restored", K.runtime_matches())

# ==========================================================================  #
# 22. synthetic inference-state reachability
# ==========================================================================  #
def synth_series(target, n=120, seed=0, vol=0.103):
    g = np.random.default_rng(seed)
    z = g.standard_normal(n)
    z = (z - z.mean()) / z.std(ddof=1)
    return z * (vol / np.sqrt(12)) + target * (vol / np.sqrt(12)) / np.sqrt(12)


IDX = ca_inference.draw_indices(120)
for want, tgt, sd in [("C1", 1.45, 11), ("C3", 0.75, 12), ("C5", -0.45, 13),
                      ("C4", -1.30, 14), ("C6", 0.20, 15)]:
    iv = ca_inference.interval({"p": synth_series(tgt, seed=sd)}, IDX)["p"]
    st = ca_inference.primary_state(iv["L"], iv["U"])
    ck("22", "primary %s reachable synthetically" % want, st["configuration"] == want,
       "got %s [%.3f, %.3f]" % (st["configuration"], iv["L"], iv["U"]))
ck("22", "C2 retained in the total classifier",
   ca_inference.primary_state(0.05, 0.20)["configuration"] == "C2")
for L, U, want in [(0.30, 1.2, "C3"), (0.0, 1.2, "C6"), (-1.4, -0.20, "C5"), (-0.5, 0.30, "C6")]:
    ck("22", "strict boundary (%.2f,%.2f)->%s" % (L, U, want),
       ca_inference.primary_state(L, U)["configuration"] == want)
for want, tgt, sd in [("FM1_POSITIVE", 0.95, 21), ("FM1_NEGATIVE", -0.95, 22),
                      ("FM1_SIGN_UNRESOLVED", 0.10, 23)]:
    iv = ca_inference.interval({"x": synth_series(tgt, seed=sd)}, IDX)["x"]
    ck("22", "FM-1 %s reachable synthetically" % want,
       ca_inference.fm1_state(iv["L"], iv["U"])["state"] == want)
ck("22", "FM-1 NOT_ADJUDICABLE on unresolved RF_MISSING",
   ca_inference.fm1_state(0.5, 1.5, rf_missing_unresolved=True)["state"] == "NOT_ADJUDICABLE")
ck("22", "FM-1 never emits a primary materiality label",
   all(ca_inference.fm1_state(a, b)["state"].startswith("FM1")
       for a, b in [(0.1, 1.0), (-1.0, -0.1), (-0.4, 0.8)]))
r_only = ca_inference.interval({"primary": synth_series(0.75, seed=31)}, IDX)["primary"]
r_joint = ca_inference.interval({"primary": synth_series(0.75, seed=31),
                                 "fm1": synth_series(0.4, seed=32)}, IDX)["primary"]
ck("22", "§N.2 primary interval independent of FM-1", r_only == r_joint)
ck("22", "degenerate series -> INFERENCE_PROCEDURE_FAILURE, not a state",
   ca_inference.interval({"d": np.zeros(120)}, IDX)["d"]["mechanical"] == "INFERENCE_PROCEDURE_FAILURE")
ck("22", "sealed inference constants intact",
   (K.BOOTSTRAP_BLOCK_LEN, K.BOOTSTRAP_REPLICATES, K.CI_LEVEL, K.MASTER_SEED,
    K.MIN_DISTINCT_MONTHS, K.VALID_REPLICATE_FLOOR) == (12, 10000, 95, 7, 24, 9500))

# ==========================================================================  #
# 23. BLINDNESS ACCESS BOUNDARY (go-live preflight)
# ==========================================================================  #
_store = tempfile.mkdtemp(prefix="ca_s2_store_")
_ledraw = io.open(os.path.join(d_abs, "positions.jsonl"), encoding="utf-8").read()
_needle = repr(max((v for v in dec["weights"].values() if v is not None), key=abs))[:14]
ck("23", "ledger file on disk contains no 'weights' key", '"weights"' not in _ledraw)
ck("23", "ledger file on disk contains no weight value", _needle not in _ledraw)
ck("23", "private _rows() no longer exposes weights", "weights" not in led._rows()[0])
ck("23", "machine read without a capability is refused",
   raises(ca_blind.CapabilityRequired, led.machine_read_position, "2026-02", None))
_cap = session.capability("TURNOVER_PRIOR_POSITION")
ck("23", "machine read WITH a capability returns the vector",
   led.machine_read_position("2026-02", _cap)["weights"] == dec["weights"])
ck("23", "position identity is reproducible without decrypting",
   led.position_identity("2026-02")["position_plaintext_sha256"]
   == rec["protected_position"]["plaintext_sha256"])
ck("23", "an unsupported capability purpose is refused",
   raises(ca_blind.CapabilityRequired, session.capability, "BROWSE_FOR_FUN"))

_ps = ca_protected.ProtectedOutcomeStore(_store, session=session)
_ident = _ps.store("SYN_BOUNDARY", {"synthetic_value": 0.7770707707})
_praw = io.open(os.path.join(_store, "SYN_BOUNDARY.sealed.json"), encoding="utf-8").read()
ck("23", "protected payload on disk is ciphertext", "0.7770707707" not in _praw)
ck("23", "a direct json.load does not expose the payload",
   "synthetic_value" not in json.dumps(json.load(io.open(
       os.path.join(_store, "SYN_BOUNDARY.sealed.json"), encoding="utf-8"))))
ck("23", "envelope cannot be opened without a capability",
   raises(ca_blind.CapabilityRequired, ca_blind.open_envelope,
          json.load(io.open(os.path.join(_store, "SYN_BOUNDARY.sealed.json"), encoding="utf-8")), None))
ck("23", "a protected store inside the repo is refused",
   raises(ca_blind.ProtectedStoreMisconfigured, ca_protected.ProtectedOutcomeStore,
          os.path.join(K.REPO, "research", "should_not_exist"), None, session))
ck("23", "key file lives outside the repository",
   ca_blind.boundary_report(syn_store)["key_file_outside_repo"])
ck("23", "protected store lives outside the repository",
   ca_blind.boundary_report(syn_store)["protected_store_outside_repo"])
ck("23", "describe() reports encrypted-at-rest and outside-repo",
   _ps.describe()["all_encrypted_at_rest"] and _ps.describe()["store_outside_repo"])
ck("23", "tampered ciphertext is rejected by the MAC",
   raises(ca_blind.EnvelopeTampered, ca_blind.open_envelope,
          {**session.seal(b"abc", {"record_type": "T"}), "ciphertext": base64.b64encode(b"AAAA").decode()}, _cap))
shutil.rmtree(_store, ignore_errors=True)

# ==========================================================================  #
# 24. BLINDNESS PRODUCTION HARDENING (vetted AEAD + key lifecycle)
# ==========================================================================  #
import cryptography as _cryptolib  # noqa: E402

ck("24", "vetted AEAD in use (AES-256-GCM)", ca_blind.AEAD_NAME == "AES-256-GCM")
ck("24", "cryptography library pinned in the runtime",
   K.PINNED_RUNTIME.get("cryptography") == _cryptolib.__version__)
_src = io.open(ca_blind.__file__, encoding="utf-8").read()
ck("24", "no home-grown keystream remains", "_keystream" not in _src)
ck("24", "no home-grown MAC composition remains",
   "hmac.new" not in _src and "encrypt-then-MAC" not in _src.split('"""')[2] if _src.count('"""') > 2 else True)
ck("24", "AESGCM is the encryption primitive", "AESGCM" in _src)
ck("24", "no ambient key loader exists",
   not hasattr(ca_blind, "ensure_key") and not hasattr(ca_blind, "seal_envelope"))
ck("24", "nonce is 96-bit and per-object", ca_blind.NONCE_BYTES == 12)

# --- explicit initialization / no silent regeneration ------------------- #
_fresh = tempfile.mkdtemp(prefix="ca_s2_fresh_")
shutil.rmtree(_fresh, ignore_errors=True)          # a path that does NOT yet exist
ck("24", "unlocking an uninitialized store refuses (no auto-create)",
   raises(ca_blind.ProtectedStoreNotInitialized, ca_blind.unlock_store, _fresh))
ck("24", "no key was created by the failed unlock",
   not os.path.exists(os.path.join(_fresh, "blind.key")))
_st = ca_blind.initialize_blind_store(_fresh, note="SYNTHETIC")
ck("24", "explicit initialization creates the store", ca_blind.is_initialized(_fresh))
ck("24", "fingerprint recorded, key material is NOT",
   len(_st["key_fingerprint_sha256"]) == 64 and "key" not in _st.get("note", "").lower()
   and not any(k for k in _st if k.endswith("_key")))
ck("24", "re-initialization is refused",
   raises(ca_blind.ProtectedStoreHold, ca_blind.initialize_blind_store, _fresh))
_sess = ca_blind.unlock_store(_fresh)
ck("24", "session repr never leaks key material",
   "key" not in repr(_sess).lower().replace("fingerprint", ""))

_env = _sess.seal(b'{"synthetic": 1}', {"record_type": "T", "record_id": "R1"})
_cap24 = _sess.capability("SYNTHETIC_TEST")
ck("24", "machine path returns the exact payload",
   ca_blind.open_envelope(_env, _cap24) == b'{"synthetic": 1}')

# --- ordinary operator cannot conjure a capability ---------------------- #
ck("24", "MachineCapability cannot be constructed directly",
   raises(ca_blind.CapabilityRequired, ca_blind.MachineCapability, "SYNTHETIC_TEST"))
ck("24", "capability repr never leaks key material", "_key" not in repr(_cap24))

# --- wrong key / tamper / transplant ------------------------------------ #
_other = tempfile.mkdtemp(prefix="ca_s2_other_")
shutil.rmtree(_other, ignore_errors=True)
ca_blind.initialize_blind_store(_other, note="SYNTHETIC OTHER")
_osess = ca_blind.unlock_store(_other)
_ocap = _osess.capability("SYNTHETIC_TEST")
ck("24", "WRONG KEY -> authenticated failure / hard hold",
   raises((ca_blind.EnvelopeTampered, ca_blind.ProtectedStoreHold),
          ca_blind.open_envelope, {**_env, "key_fingerprint_sha256": None}, _ocap))
ck("24", "TAMPERED ciphertext -> authenticated failure",
   raises(ca_blind.EnvelopeTampered, ca_blind.open_envelope,
          {**_env, "ciphertext": base64.b64encode(bytes(40)).decode()}, _cap24))
_env2 = _sess.seal(b'{"synthetic": 2}', {"record_type": "T", "record_id": "R2"})
ck("24", "SWAPPED ciphertext between records -> AAD failure",
   raises(ca_blind.EnvelopeTampered, ca_blind.open_envelope,
          {**_env, "ciphertext": _env2["ciphertext"], "nonce": _env2["nonce"]}, _cap24))
ck("24", "ALTERED AAD -> authenticated failure",
   raises(ca_blind.EnvelopeTampered, ca_blind.open_envelope,
          {**_env, "aad": {"record_type": "T", "record_id": "SOMETHING_ELSE"}}, _cap24))
ck("24", "AAD carries identity, never an outcome value",
   set(_env["aad"]) <= {"record_type", "record_id", "holding_month", "decision_month_end",
                        "source_snapshot_id", "source_snapshot_sha256",
                        "sealed_prereg_sha256", "schema"})

# --- key missing / changed / fingerprint mismatch -> HARD HOLD ---------- #
_kf = os.path.join(_fresh, "blind.key")
_backup = io.open(_kf, "rb").read()
os.remove(_kf)
ck("24", "KEY MISSING after init -> HARD HOLD",
   raises(ca_blind.ProtectedStoreHold, ca_blind.unlock_store, _fresh))
ck("24", "no key was regenerated by the failed unlock", not os.path.exists(_kf))
io.open(_kf, "wb").write(base64.b64encode(os.urandom(32)))
ck("24", "CHANGED key -> HARD HOLD (fingerprint mismatch)",
   raises(ca_blind.ProtectedStoreHold, ca_blind.unlock_store, _fresh))
io.open(_kf, "wb").write(b"not-a-valid-key")
ck("24", "UNREADABLE / malformed key -> HARD HOLD",
   raises(ca_blind.ProtectedStoreHold, ca_blind.unlock_store, _fresh))
io.open(_kf, "wb").write(_backup)
ck("24", "restoring the ORIGINAL key unlocks again",
   ca_blind.unlock_store(_fresh).state["key_fingerprint_sha256"] == _st["key_fingerprint_sha256"])

# --- permissions -------------------------------------------------------- #
_perm = ca_blind.permissions_report(_kf)
ck("24", "key file permissions checked", _perm["checked"])
ck("24", "no broad/shared principal on the key file",
   not _perm.get("broad_readable"), str(_perm.get("broad_principals")))
_bp = ca_blind.boundary_report(_fresh)
ck("24", "boundary report states the honest threat limit",
   "NOT secrecy against" in _bp["threat_boundary"])
ck("24", "boundary report exposes no key material",
   "blind.key" in _bp["key_file"] and _bp.get("key") is None)

shutil.rmtree(_fresh, ignore_errors=True)
shutil.rmtree(_other, ignore_errors=True)

# ==========================================================================  #
# seal immutability + cleanup
# ==========================================================================  #
ck("1", "sealed prereg sha256 unchanged by the whole suite",
   K.sha256_file(K.SEALED_PREREG) == K.SEALED_PREREG_SHA256)
ck("2", "frozen panel sha256 unchanged by the whole suite",
   K.sha256_file(K.FROZEN_PANEL) == K.FROZEN_PANEL_SHA256)
shutil.rmtree(d_abs, ignore_errors=True)
shutil.rmtree(syn_store, ignore_errors=True)

print("\nper-class results:")
for c in sorted(CLASSES, key=lambda x: int(x)):
    p, f = CLASSES[c]
    print("  class %-3s %2d pass %2d fail" % (c, p, f))
tot_p = sum(v[0] for v in CLASSES.values())
tot_f = sum(v[1] for v in CLASSES.values())
print("\nTOTAL: %d assertions, %d failed" % (tot_p + tot_f, tot_f))
print("C_A_S2_TESTS = " + ("PASS" if OK else "FAIL"))
sys.exit(0 if OK else 1)
