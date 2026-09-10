"""X01 sealed-contract tests — SYNTHETIC DATA ONLY.

Every test here runs on a hand-built price path, hand-built position books,
literal arithmetic, or a synthetic manifest. **Nothing in this file loads the
X01 target panel for a computation**, constructs `E`, `F`, `A1`, `S1` or `S2`,
or produces any Sharpe, delta-Sharpe, bootstrap or crisis statistic.

The two parquet panels and the ETF CSV are touched only as *opaque bytes* by the
runner's hashing path — never parsed into returns.

What is asserted:

* the sealed binding contracts (signal, cost quantity, S1 continuity, S2
  binding, B, COVID month-ends, bootstrap configuration), each tied back to the
  **sealed bytes** so a test cannot drift away from the contract it guards;
* the runner's **refusal** behaviour — manifest mismatch, dirty pinned path,
  altered git-ignored data pin, altered cross-repo S2 dependency.
"""

import copy
import hashlib
import importlib.util
import io
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, REPO)                      # signals.py does `import config`

_spec = importlib.util.spec_from_file_location(
    "x01_runner", os.path.join(HERE, "x01_runner.py"))
runner = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(runner)

_sig_spec = importlib.util.spec_from_file_location(
    "x01_signals", os.path.join(REPO, "src", "signals.py"))
signals = importlib.util.module_from_spec(_sig_spec)
sys.modules["x01_signals"] = signals
_sig_spec.loader.exec_module(signals)

SEALED = io.open(os.path.join(REPO, runner.SEALED_PREREG), encoding="utf-8").read()

_fails, _out = [], []


def ck(name, ok, detail=""):
    _out.append("  %-62s %s%s" % (name, "PASS" if ok else "FAIL",
                                  ("   " + detail) if detail else ""))
    if not ok:
        _fails.append(name)


def flush(title):
    print("=" * 80); print(title); print("=" * 80)
    print("\n".join(_out)); del _out[:]; print()


# --------------------------------------------------------------------------- #
# 1. signal — mean of SIGNS, four horizons, zero convention
# --------------------------------------------------------------------------- #
def _synthetic_path():
    """Month-ends whose 1/3/6/12m returns are exactly (+.10,+.10,+.10,-.01)."""
    m = [90.0] * 13
    m[12], m[11], m[9], m[6], m[0] = 100.0, 100 / 1.10, 100 / 1.10, 100 / 1.10, 100 / 0.99
    return pd.DataFrame({"X": m},
                        index=pd.date_range("2020-01-31", periods=13, freq="ME"))


def test_signal():
    monthly = _synthetic_path()
    r = {n: float(monthly["X"].iloc[-1] / monthly["X"].iloc[-1 - n] - 1) for n in (1, 3, 6, 12)}
    got = float(signals.signal_method_b(monthly).iloc[-1, 0])
    ck("mean-of-signs composite returns +0.5", abs(got - 0.5) < 1e-12, "got %+.6f" % got)
    ck("mean-of-RETURNS (0.0725) is rejected",
       abs(got - float(np.mean(list(r.values())))) > 0.4)
    ck("sign-of-mean (+1.0) is rejected",
       abs(got - float(np.sign(np.mean(list(r.values()))))) > 0.4)
    ck("score lies on the sealed grid {-1,-0.5,0,+0.5,+1}",
       any(abs(got - g) < 1e-12 for g in (-1, -0.5, 0, 0.5, 1)))
    ck("zero contribution convention: sign(0) == 0", float(np.sign(0.0)) == 0.0)
    ck("four-horizon requirement: NaN before all four exist",
       bool(np.isnan(float(signals.signal_method_b(monthly.iloc[:5]).iloc[-1, 0]))))
    ck("sealed contract states sign-FIRST, mean-SECOND",
       "**sign FIRST, mean SECOND**" in SEALED)
    flush("1. SIGNAL — mean of signs (synthetic path)")


# --------------------------------------------------------------------------- #
# 2. traded quantity + cash-first primitive
# --------------------------------------------------------------------------- #
def traded_qty(prev, now):
    """|q_t - q_{t-1}| per CONTRACT IDENTITY — the sealed 3.8 expression."""
    return {k: abs(now.get(k, 0.0) - prev.get(k, 0.0))
            for k in sorted(set(prev) | set(now))}


def test_cost():
    C = 12.50                                   # CL: tick 10.00 + 2.50, sealed 3.4
    cases = [("+1 -> +1", {"CLZ5": 1.0}, {"CLZ5": 1.0}, 0.0),
             ("+1 ->  0", {"CLZ5": 1.0}, {"CLZ5": 0.0}, 1.0),
             ("+1 -> +2", {"CLZ5": 1.0}, {"CLZ5": 2.0}, 1.0),
             ("+1 -> -1", {"CLZ5": 1.0}, {"CLZ5": -1.0}, 2.0),
             ("roll: old +1->0, new 0->+1", {"CLZ5": 1.0}, {"CLF6": 1.0}, 2.0)]
    for name, prev, now, want in cases:
        q = traded_qty(prev, now)
        total = sum(q.values())
        naive = abs(sum(abs(v) for v in now.values()) - sum(abs(v) for v in prev.values()))
        ck("%-26s traded=%.0f cost=$%.2f" % (name, total, total * C),
           abs(total - want) < 1e-12,
           "want %.0f; delta-|position| gives %.0f" % (want, naive))
        ck("   cost non-negative", total * C >= 0.0)
    ck("reversal: the deleted delta-|position| rule would MISS it",
       sum(traded_qty({"CLZ5": 1.0}, {"CLZ5": -1.0}).values()) == 2.0)
    ck("roll charges two identities, one side each",
       traded_qty({"CLZ5": 1.0}, {"CLF6": 1.0}) == {"CLF6": 1.0, "CLZ5": 1.0})
    mult, P, w = 1000.0, 70.0, 0.8
    rate = lambda K: abs(w * K / (mult * P)) * C / K
    ck("cost RATE invariant to the capital base K",
       abs(rate(1.0) - rate(3.7e9)) < 1e-15)
    ck("sealed contract carries the traded-quantity expression",
       "trade_qty_j,t = | q_j,t − q_j,t−1 |" in SEALED)
    flush("2. COST — absolute traded quantity, cash-first primitive")


# --------------------------------------------------------------------------- #
# 3. S1 forward ratio adjustment
# --------------------------------------------------------------------------- #
def test_s1():
    k_old, p_old, p_new = 1.0, 100.0, 110.0
    k_new = k_old * p_old / p_new                       # sealed 8.1 direction
    ck("adjusted level via OLD contract at roll = 100",
       abs(k_old * p_old - 100.0) < 1e-12)
    ck("adjusted level via NEW contract at roll = 100",
       abs(k_new * p_new - 100.0) < 1e-12)
    ck("continuous across the roll (NOT 121)",
       abs(k_new * p_new - k_old * p_old) < 1e-12 and abs(k_new * p_new - 121.0) > 20)
    ck("subsequent raw 121 maps to adjusted 110 (+10%)",
       abs(k_new * 121.0 - 110.0) < 1e-12)
    ck("adjusted return equals the new contract's own return",
       abs((k_new * 121.0) / (k_new * p_new) - 121.0 / p_new) < 1e-15)
    ck("history is NOT restated (pre-roll 95 stays 95)",
       abs(k_old * 95.0 - 95.0) < 1e-12)
    k2 = k_new * 115.5 / 60.0
    ck("successive factors compound; continuity holds at roll 2",
       abs(k2 * 60.0 - k_new * 115.5) < 1e-12)
    ck("sealed contract carries the corrected direction",
       "k_new = k_old × P_old,τ / P_new,τ" in SEALED)
    ck("S1 PnL still routes through the accepted cash path",
       "tsmom_chain_net_returns" in SEALED)
    flush("3. S1 — causal forward ratio adjustment (synthetic 100/110/121)")


# --------------------------------------------------------------------------- #
# 4. S2 binding, B, COVID, bootstrap config — read from the SEALED bytes
# --------------------------------------------------------------------------- #
def test_sealed_config():
    ck("S2 bound to the accepted comparator by name",
       "fixed_calendar_front_series" in SEALED)
    ck("S2 comparator source exists in carry at the pinned path",
       os.path.exists(os.path.join(runner.CARRY, runner.CARRY_S2_PATH)))
    carry_src = io.open(os.path.join(runner.CARRY, runner.CARRY_S2_PATH),
                        encoding="utf-8").read()
    ck("carry actually defines fixed_calendar_front_series",
       "def %s" % runner.CARRY_S2_SYMBOL in carry_src)
    ck("B = 0.15 with boundary -0.15",
       "`B = 0.15` annualised-Sharpe units" in SEALED and "−0.15" in SEALED)
    ck("COVID month-ends 2020-02-29 / 03-31 / 04-30",
       "**2020-02-29, 2020-03-31, 2020-04-30**" in SEALED)
    ck("2020-02 month-end is the leap day",
       str((pd.Timestamp("2020-02-01") + pd.offsets.MonthEnd(0)).date()) == "2020-02-29")

    # paired-bootstrap configuration parser, against the sealed text
    cfg = {"family": "stationary bootstrap", "L_months": 12, "replicates": 10000,
           "ci": "percentile", "level": 95, "master_seed": 7,
           "arm_order": ["primary", "S1", "S2"], "valid_floor": 9500}
    ck("bootstrap family", "**stationary bootstrap** (Politis & Romano 1994)" in SEALED)
    ck("block length L = 12 months", "**L = 12 months**" in SEALED and cfg["L_months"] == 12)
    ck("replicates 10,000", "| Replications | **10,000**" in SEALED and cfg["replicates"] == 10000)
    ck("95 % percentile CI",
       "| CI level | **95 %**" in SEALED and "**percentile interval**" in SEALED)
    ck("master seed 7 and fixed arm order",
       "SeedSequence(7).spawn(3)" in SEALED and cfg["arm_order"] == ["primary", "S1", "S2"])
    ck("valid-replicate floor 9,500", "fewer than 9,500** valid replicates" in SEALED)
    man = json.load(io.open(runner.MANIFEST, encoding="utf-8"))
    sp = man["seed_protocol"]
    ck("manifest seed protocol matches the sealed rule",
       sp["master_seed"] == 7 and sp["arm_order"] == cfg["arm_order"])
    kids = np.random.SeedSequence(7).spawn(3)
    ck(".entropy does NOT identify the children (all report 7)",
       len({k.entropy for k in kids}) == 1
       and "NOT an identifier" in sp["identity_convention"])
    ck("spawn_key DOES identify the three children",
       len({tuple(k.spawn_key) for k in kids}) == 3)
    ck("manifest records spawn_key + state fingerprint per arm",
       sp["child_streams"] is not None
       and [c["spawn_key"] for c in sp["child_streams"]] == [[0], [1], [2]]
       and all(len(c["state_fingerprint_u32x4"]) == 4 for c in sp["child_streams"]))
    ck("recorded fingerprints reproduce from the sealed rule",
       [c["state_fingerprint_u32x4"] for c in sp["child_streams"]]
       == [[int(v) for v in k.generate_state(4)]
           for k in np.random.SeedSequence(7).spawn(3)])
    flush("4. SEALED CONFIG — S2 binding, B, COVID, bootstrap")


# --------------------------------------------------------------------------- #
# 5. runner refusals — synthetic manifests, real code path
# --------------------------------------------------------------------------- #
def _refuses(manifest, needle):
    r = runner.preflight(manifest=manifest, strict_state=False)
    return (not r.ok) and any(needle in reason for reason in r.reasons)


def test_refusals():
    real = json.load(io.open(runner.MANIFEST, encoding="utf-8"))

    # Structural, not transient: while execution-relevant modules are declared
    # PENDING binding (uncommitted), preflight MUST refuse. Every baseline
    # refusal has to be attributable to that declared pending state or to a
    # path the manifest itself lists as unbound — never to something unexplained.
    base = runner.preflight(manifest=copy.deepcopy(real), strict_state=False)
    pending = {e["path"] for e in real.get("pending_binding", [])}
    def _explained(reason):
        return ("revision-bound" in reason
                or "execution manifest" in reason
                or any(p in reason for p in pending)
                or any(p in reason for p in
                       ("x01_runner.py", "x01_contract_tests.py",
                        "validate_wave0.py", "X01_EXECUTION_MANIFEST.json")))
    unexplained = [x for x in base.reasons if not _explained(x)]
    ck("every baseline refusal is attributable to the declared pending binding",
       unexplained == [], "; ".join(unexplained)[:110])
    gated = copy.deepcopy(real)
    gated["pending_binding"] = [
        {"path": "research/extensions/x01/x01_target_construction.py",
         "status": "UNCOMMITTED_PENDING_BINDING"}]
    ck("preflight is fail-closed whenever a module is unbound",
       not runner.preflight(manifest=gated, strict_state=False).ok)
    ck("manifest names a runner base revision",
       bool(real["runner_base"]["runner_base_revision"]))
    ck("manifest carries NO self-hash field",
       real["runner_base"]["manifest_self_hash"] is None)
    ck("runner code blobs are pinned (runner, tests, validator)",
       sorted(e["path"] for e in real["inputs"] if e["kind"] == "runner_code")
       == sorted(["research/extensions/validate_wave0.py",
                  "research/extensions/x01/x01_target_construction.py",
                  "research/extensions/x01/x01_construction_tests.py",
                  "research/extensions/x01/x01_contract_tests.py",
                  "research/extensions/x01/x01_runner.py"]))
    ck("non-consumed parquet inventory is recorded with reasons",
       {e["path"] for e in real["not_consumed_by_x01"]} >=
       {"research/extensions/wave1/settle_panel.parquet",
        "research/extensions/wave1/oi_panel.parquet"}
       and all(e["reason"] for e in real["not_consumed_by_x01"]))

    m = copy.deepcopy(real)
    for e in m["inputs"]:
        if e["path"].endswith("x01_runner.py"):
            e["sha256"] = "4" * 64
    ck("REFUSE: a pinned runner-code blob differs from the pin (blob at HEAD)",
       _refuses(m, "runner code blob at HEAD matches the pin"))
    ck("REFUSE: the same tamper also fails the LIVE worktree comparison",
       _refuses(m, "runner code LIVE worktree bytes match the pin"))

    m = copy.deepcopy(real)
    m["sealed_contract"]["prereg_sha256_reviewed_pin"] = "0" * 64
    ck("REFUSE: worktree prereg differs from the sealed contract",
       _refuses(m, "worktree preregistration matches the sealed contract"))

    m = copy.deepcopy(real)
    for e in m["inputs"]:
        if e["path"].endswith("run_x02a_v3.py"):
            e["sha256"] = "1" * 64
    ck("REFUSE: pinned implementation module byte mismatch",
       _refuses(m, "run_x02a_v3.py"))

    m = copy.deepcopy(real)
    for e in m["inputs"]:
        if e["path"].endswith("settle_v2.parquet"):
            e["sha256"] = "2" * 64
    ck("REFUSE: altered git-ignored parquet data pin",
       _refuses(m, "settle_v2.parquet"))

    m = copy.deepcopy(real)
    m["carry_s2_dependency"]["revision"] = "f" * 40
    ck("REFUSE: cross-repo S2 revision changed",
       _refuses(m, "carry S2 revision unchanged"))

    m = copy.deepcopy(real)
    m["carry_s2_dependency"]["sha256"] = "3" * 64
    ck("REFUSE: cross-repo S2 file bytes changed",
       _refuses(m, "carry S2 file unchanged"))

    # dirty-worktree policy, exercised deterministically through the injected
    # status seam so the result does not depend on ambient worktree state.
    dirty_pinned = (["research/extensions/wave1/run_x02a_v3.py"], [])
    r = runner.preflight(manifest=copy.deepcopy(real), strict_state=False,
                         status=dirty_pinned)
    ck("REFUSE: a pinned path is modified in the worktree",
       (not r.ok) and any("no pinned path is modified" in x for x in r.reasons))

    r = runner.preflight(manifest=copy.deepcopy(real), strict_state=False,
                         status=(["src/some_unrelated_module.py"], []))
    ck("REFUSE: unapproved tracked modification outside the allowlist",
       (not r.ok) and any("no unapproved tracked modification" in x for x in r.reasons))

    r = runner.preflight(manifest=copy.deepcopy(real), strict_state=False,
                         status=([], ["research/extensions/wave1/run_x02a_v3.py"]))
    ck("REFUSE: a tracked deletion",
       (not r.ok) and any("no tracked deletion" in x for x in r.reasons))

    r = runner.preflight(manifest=copy.deepcopy(real), strict_state=False,
                         status=(["ops/EXPOSURE_LEDGER.md"], []))
    ck("ALLOW: an allowlisted append-only governance ledger is not an unapproved mod",
       not any("no unapproved tracked modification" in x for x in r.reasons))

    ck("append-only predicate accepts an additions-only diff",
       runner.diff_deletes_no_record_row(
           ["--- a/x", "+++ b/x", "@@ -0,0 +1 @@", "+| 2026-09-09T00:00Z | new row |"]))
    ck("append-only predicate REJECTS a deleted EXPOSURE row",
       not runner.diff_deletes_no_record_row(
           ["--- a/x", "+++ b/x", "-| 2026-09-08T01:00Z | ... | Row 24. |"]))
    ck("append-only predicate REJECTS a deleted SEAT row",
       not runner.diff_deletes_no_record_row(["--- a/x", "+++ b/x", "-| S14 | ... |"]))
    ck("append-only predicate PERMITS the derived normalisation summary to move",
       runner.diff_deletes_no_record_row(
           ["--- a/x", "+++ b/x", "-  `REVEALED_TARGET_METRIC` and rows 11-33 are `NO_OUTCOME`",
            "+  `REVEALED_TARGET_METRIC` and rows 11-34 are `NO_OUTCOME`"]))
    ck("no blanket 'dirty tree is okay' rule exists",
       "There is no blanket" in real["dirty_worktree_policy"]["rule"])
    flush("5. RUNNER REFUSALS — synthetic manifests, real code path")


# --------------------------------------------------------------------------- #
# 6. the execution boundary itself
# --------------------------------------------------------------------------- #
def test_boundary():
    man = json.load(io.open(runner.MANIFEST, encoding="utf-8"))
    ck("manifest declares execution_authorized = false",
       man["execution_authorized"] is False)
    ck("execute() refuses (non-zero) and constructs nothing",
       runner.cmd_execute(None) == 2)
    src = io.open(os.path.join(HERE, "x01_runner.py"), encoding="utf-8").read()
    ck("runner never parses a price panel (no read_parquet / read_csv)",
       "read_parquet" not in src and "read_csv" not in src)
    # numpy IS imported by the runner, but only inside `seed_protocol()` to
    # derive SeedSequence(7).spawn(3) — that is seed bookkeeping, not price
    # data. What must be absent is a dataframe library and any module-level
    # array import that could quietly grow into a target-construction path.
    module_level = [ln for ln in src.splitlines()
                    if ln.startswith("import ") or ln.startswith("from ")]
    ck("runner imports no dataframe library at all", "import pandas" not in src)
    ck("runner has no module-level numpy/pandas import",
       not any("numpy" in ln or "pandas" in ln for ln in module_level))
    ck("numpy appears only inside the seed-derivation helper",
       src.count("import numpy") == 1
       and "import numpy" in src.split("def seed_protocol")[1].split("def ")[0])
    ck("runner defines no target-construction entry point",
       not any(("def " + n) in src for n in
               ("build_E", "build_F", "construct_E", "construct_F",
                "sharpe", "delta_sharpe", "run_bootstrap")))
    ck("no X01 target artifact exists on disk",
       sorted(f for f in os.listdir(HERE)
              if f.endswith((".parquet", ".csv"))) == [])
    flush("6. EXECUTION BOUNDARY")


def main():
    test_signal(); test_cost(); test_s1(); test_sealed_config()
    test_refusals(); test_boundary()
    print("=" * 80)
    print("X01_SYNTHETIC_VALIDATION = %s   (%d failed)"
          % ("PASS" if not _fails else "FAIL", len(_fails)))
    for f in _fails:
        print("   FAILED:", f)
    print("TARGET_X01_OUTCOME_ACCESSED = NO   (synthetic data only)")
    print("=" * 80)
    return 0 if not _fails else 1


if __name__ == "__main__":
    sys.exit(main())
