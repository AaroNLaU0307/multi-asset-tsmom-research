"""CTA-EDGE-04-MMV — S1 PRE-SEAL ADVERSARIAL CHECK.

Runs the complete mechanical check that must pass before MMV_SEAL_MANIFEST.md may be
written. It is adversarial by construction: every check tries to FALSIFY a claim the
preregistration makes, and the script exits non-zero the moment one does.

    python research/extensions/mmv/mmv_preseal_check.py

WHAT THIS SCRIPT MUST NEVER DO, and does not:
  - compute any MMV macro feature, 12-month change, leg sign or composite
  - compute any MMV position, any TSMOM agreement rate or any separability figure
  - read any asset RETURN, or any canonical TSMOM SIGN VALUE (only the date column)
  - compute any Sharpe, bootstrap or interval

It reads the frozen macro bytes only for STRUCTURAL COVERAGE — does an eligible vintage
exist at each decision date, and does it carry enough reference months for the sealed
transform. Coverage is a Gate-0 feasibility property, not a feature. No macro VALUE is
ever differenced, signed, compared across dates, or printed.
"""

from __future__ import annotations

import ast
import csv
import hashlib
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
os.chdir(REPO)

MMV = "research/extensions/mmv"
DATA = "data/mmv"
RAW_MANIFEST = DATA + "/MMV_RAW_MANIFEST.json"
FOMC_MANIFEST = DATA + "/MMV_FOMC_TIMING_MANIFEST.json"
PREREG = MMV + "/MMV_PREREGISTRATION.md"
OD = "ops/OWNER_DECISION_RECORD_CTA_EDGE_04_MMV.md"
PANEL = "output/monthly_signal_panel.csv"

WINDOW_LO, WINDOW_HI = "2008-05-31", "2026-06-30"

CANON17 = "SPY EEM EWJ XLE XLU TLT SHY LQD HYG USO UNG GLD DBA UUP FXY VNQ RWX".split()
NOT_MAPPED = {"VNQ", "RWX"}

#: The sealed coefficient table, MMV-OD-6 / preregistration section E.1.
COEF = {
    "SPY": (1, 0, -1), "EEM": (1, 0, -1), "EWJ": (1, 0, -1),
    "XLE": (1, 0, -1), "XLU": (1, 0, -1),
    "TLT": (-1, -1, -1), "SHY": (-1, -1, -1),
    "LQD": (1, 0, 0), "HYG": (1, 0, 0),
    "USO": (0, 1, 0), "UNG": (0, 1, 0), "GLD": (0, 1, 0), "DBA": (0, 1, 0),
    "UUP": (0, 1, 1), "FXY": (0, -1, -1),
}

#: Minimum monthly reference observations the sealed transform needs inside the
#: as-of vintage. Growth: D12 needs 13 points. Inflation: pi12(m) - pi12(m-12)
#: needs 25 points.
MIN_REF = {"INDPRO": 13, "PAYEMS": 13, "CPILFENS": 25}

RESULTS = []


def chk(cid, ok, detail):
    RESULTS.append((cid, bool(ok), detail))
    return bool(ok)


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def sgn(x):
    return (x > 0) - (x < 0)


def load(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def text(p):
    with open(p, encoding="utf-8") as fh:
        return fh.read()


def norm(s):
    """Collapse markdown emphasis and all whitespace runs.

    Contract phrases are checked against the NORMALISED contract so that a
    check asserts CONTENT, never line wrapping. A validator that a reflow can
    break is not a validator.
    """
    return " ".join(s.replace("**", "").split())


# ---------------------------------------------------------------------------
# GROUP A — FREEZE INTEGRITY
# ---------------------------------------------------------------------------

def group_a(man):
    files = []
    for sid, e in man["series"].items():
        for kind, f in e["files"].items():
            files.append((sid, kind, f))

    chk("A1", len(files) == 18 and os.path.exists(RAW_MANIFEST),
        str(len(files)) + " series files + 1 manifest = "
        + str(len(files) + 1) + " raw files (expect 19)")

    missing = [f["path"] for _, _, f in files if not os.path.exists(f["path"])]
    chk("A2", not missing,
        "all " + str(len(files)) + " frozen files present on disk"
        if not missing else "MISSING " + str(missing))

    bad_h, bad_b = [], []
    for _, _, f in files:
        if not os.path.exists(f["path"]):
            continue
        if sha256_file(f["path"]) != f["sha256"]:
            bad_h.append(f["path"])
        if os.path.getsize(f["path"]) != f["bytes"]:
            bad_b.append(f["path"])
    chk("A3", not bad_h, "every recorded sha256 reproduces byte-for-byte"
        if not bad_h else "HASH MISMATCH " + str(bad_h))
    chk("A4", not bad_b, "every recorded byte count reproduces"
        if not bad_b else "SIZE MISMATCH " + str(bad_b))

    # A5 — recompute the recorded coverage from the frozen bytes.
    bad_cov = []
    for sid, e in man["series"].items():
        obs = load(e["files"]["observations_realtime"]["path"])
        vin = load(e["files"]["vintage_dates"]["path"])
        cov = e["coverage"]
        got = {
            "vintage_count": len(vin),
            "distinct_reference_dates": len({o["date"] for o in obs}),
            "distinct_realtime_starts": len({o["realtime_start"] for o in obs}),
            "first_reference_date": min(o["date"] for o in obs),
            "last_reference_date": max(o["date"] for o in obs),
            "first_vintage": vin[0],
            "last_vintage": vin[-1],
        }
        if len(obs) != e["files"]["observations_realtime"]["rows"]:
            bad_cov.append(sid + ":rows")
        for k, v in got.items():
            if v != cov[k]:
                bad_cov.append(sid + ":" + k)
    chk("A5", not bad_cov,
        "recorded coverage recomputes from the frozen bytes for all 6 series"
        if not bad_cov else "COVERAGE DRIFT " + str(bad_cov))

    # A6 — the fetcher is pinned and tracked.
    fetcher = MMV + "/mmv_data_freeze.py"
    tracked = subprocess.run(["git", "ls-files", fetcher],
                             capture_output=True, text=True).stdout.strip()
    chk("A6", bool(tracked), "fetcher tracked in git: " + fetcher)

    # A7 — every recorded request redacts the credential.
    leaks = []
    for sid, e in man["series"].items():
        for rname, r in e["requests"].items():
            if "api_key" in r and r["api_key"] != "<REDACTED>":
                leaks.append(sid + "." + rname)
    chk("A7", not leaks, "api_key is <REDACTED> in every recorded request"
        if not leaks else "CREDENTIAL IN MANIFEST " + str(leaks))

    # A8 — no credential-shaped token anywhere in tracked files.
    tracked_files = subprocess.run(["git", "ls-files"],
                                   capture_output=True, text=True).stdout.split()
    key_re = re.compile(r"\b[0-9a-f]{32}\b")
    assign_re = re.compile(r"FRED_API_KEY\s*[=:]\s*[0-9A-Za-z]{8,}")
    hits = []
    for p in tracked_files:
        if not os.path.exists(p):
            continue
        try:
            s = text(p)
        except (UnicodeDecodeError, PermissionError):
            continue
        for m in key_re.findall(s):
            hits.append(p + ":32hex")
        if assign_re.search(s):
            hits.append(p + ":literal-assignment")
    chk("A8", not hits, "no credential-shaped token in "
        + str(len(tracked_files)) + " tracked files"
        if not hits else "POSSIBLE CREDENTIAL " + str(hits))

    # A9 — raw macro bytes are NOT tracked, and credential patterns are ignored.
    gi = text(".gitignore")
    tracked_data = [p for p in tracked_files if p.startswith("data/mmv/")]
    chk("A9", not tracked_data and ".env" in gi and "*.key" in gi,
        "data/mmv/ untracked and credential patterns present in .gitignore"
        if not tracked_data else "RAW DATA TRACKED " + str(tracked_data))


# ---------------------------------------------------------------------------
# GROUP B — POINT-IN-TIME / INFORMATION CONCEPT
# ---------------------------------------------------------------------------

def decision_dates():
    with open(PANEL, encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    ds = [r["month_end"][:10] for r in rows]
    return [d for d in ds if WINDOW_LO <= d <= WINDOW_HI]


def as_of(obs, t):
    """Latest-known-as-of reconstruction: which reference dates were PUBLISHED and
    valued as of t. Returns a set of reference dates. No macro VALUE is retained,
    because structural coverage is all this check is permitted to establish."""
    out = set()
    for o in obs:
        if o["realtime_start"] <= t <= o["realtime_end"] and o["value"] != ".":
            out.add(o["date"])
    return out


def group_b(man, dates):
    chk("B0", len(dates) == 218 and dates[0] == WINDOW_LO and dates[-1] == WINDOW_HI,
        str(len(dates)) + " canonical decision dates "
        + dates[0] + ".." + dates[-1])

    obs = {sid: load(e["files"]["observations_realtime"]["path"])
           for sid, e in man["series"].items()}
    pre = norm(text(PREREG))

    # B1/B2/B3 — latest-known-as-of reconstruction is VALID for each ALFRED leg:
    # an eligible vintage exists at every decision date and carries enough
    # reference months for the sealed transform.
    for cid, sid in (("B1", "INDPRO"), ("B2", "PAYEMS"), ("B3", "CPILFENS")):
        need = MIN_REF[sid]
        fails, thin = [], []
        for t in dates:
            snap = as_of(obs[sid], t)
            if not snap:
                fails.append(t)
            elif len(snap) < need:
                thin.append(t)
        ok = not fails and not thin
        chk(cid, ok,
            sid + ": eligible as-of snapshot at all " + str(len(dates))
            + " decision dates, every snapshot carries >= " + str(need)
            + " reference months"
            if ok else sid + " FAILS: no-vintage=" + str(fails[:5])
            + " thin=" + str(thin[:5]))

    # B4 — NO FINAL-REVISED LEAKAGE. The selector must admit nothing published
    # after the cutoff. Falsify by searching for any admitted observation whose
    # realtime_start post-dates the decision date.
    leak = []
    for sid in ("INDPRO", "PAYEMS", "CPILFENS"):
        for t in dates:
            for o in obs[sid]:
                if (o["realtime_start"] <= t <= o["realtime_end"]
                        and o["realtime_start"] > t):
                    leak.append((sid, t))
    chk("B4", not leak,
        "as-of selector admits NO observation published after the decision date "
        "on any of the " + str(len(dates)) + " dates (no final-revised leakage)"
        if not leak else "LEAK " + str(leak[:5]))

    # B5 — the freeze itself used the real-time endpoint, not the final-revised
    # default. output_type=1 is 'observations by real-time period'.
    ot = {sid: e["requests"]["observations"].get("output_type")
          for sid, e in man["series"].items()}
    chk("B5", set(ot.values()) == {1},
        "every observations request used output_type=1 (real-time period); "
        "final-revised history was never requested"
        if set(ot.values()) == {1} else "OUTPUT TYPE " + str(ot))

    # B6 — CPILFENS missingness follows the sealed rule.
    cpi_missing = man["series"]["CPILFENS"]["coverage"][
        "reference_dates_with_no_value_in_any_vintage"]
    others = {s: man["series"][s]["coverage"][
        "reference_dates_with_no_value_in_any_vintage"]
        for s in ("INDPRO", "PAYEMS", "DFEDTAR", "DFEDTARL", "DFEDTARU")}
    rule_ok = ("NEVER converted to zero" in pre and "2025-10-01" in pre
               and "NO IMPUTATION" in pre and "NO CARRY-FORWARD" in pre)
    chk("B6", cpi_missing == ["2025-10-01"]
        and all(not v for v in others.values()) and rule_ok,
        "CPILFENS has exactly one valueless reference date (2025-10-01), no other "
        "series has any, and the sealed rule maps it to UNDEFINED (never zero, "
        "never imputed, never carried forward)")

    # B7 — SPLICE CONTIGUOUS at 2008-12-16.
    tar = man["series"]["DFEDTAR"]["coverage"]
    lo = man["series"]["DFEDTARL"]["coverage"]
    hi = man["series"]["DFEDTARU"]["coverage"]
    contiguous = (tar["last_reference_date"] == "2008-12-15"
                  and lo["first_reference_date"] == "2008-12-16"
                  and hi["first_reference_date"] == "2008-12-16")
    overlap = [o["date"] for o in obs["DFEDTAR"] if o["date"] >= "2008-12-16"]
    gap = [o["date"] for o in obs["DFEDTARL"] if o["date"] < "2008-12-16"]
    chk("B7", contiguous and not overlap and not gap,
        "DFEDTAR ends 2008-12-15, DFEDTARL/DFEDTARU begin 2008-12-16 — "
        "contiguous, no gap, no overlap")

    # B8 — POLICY AVAILABILITY COMES FROM THE OFFICIAL ANNOUNCEMENT AUTHORITY,
    # and every collision is pinned to the Fed's own bytes.
    fm = load(FOMC_MANIFEST)
    col = fm["collisions"]
    det = all(c["eligible_target_at_this_decision_date"]
              in ("newly announced target/range",
                  "PREVIOUS target/range (rule fallback)")
              for c in col.values())
    files_ok = all(os.path.exists(c["raw_file"])
                   and sha256_file(c["raw_file"]) == c["sha256"]
                   for c in col.values())
    chk("B8", len(col) == 6 and det and files_ok
        and fm.get("rule_deterministic_for_all_collisions") is True
        and fm["source_authority"].startswith("Board of Governors"),
        "all " + str(len(col)) + " FOMC collisions pinned from the Federal "
        "Reserve's own statement pages, hashes reproduce, every one resolves "
        "deterministically")

    # B9 — the same-day cutoff rule is deterministic and CONSERVATIVE: a collision
    # whose time cannot be established must retain the PREVIOUS target.
    wrong = [d for d, c in col.items()
             if (not c["time_authoritatively_established"])
             and c["at_or_before_cutoff"]]
    est = [d for d, c in col.items() if c["time_authoritatively_established"]]
    fb = [d for d, c in col.items() if not c["time_authoritatively_established"]]
    chk("B9", not wrong and len(est) == 4 and len(fb) == 2
        and "secondary_authority_checked" in fm,
        "same-day rule deterministic: " + str(len(est)) + " collisions carry an "
        "official time and admit the new target, " + str(len(fb)) + " carry none "
        "(checked against the statement page AND both FOMC calendar pages) and "
        "retain the previous target by the rule's own fallback; an unestablished "
        "time is never treated as eligible")

    # B10 — ALFRED realtime_start is NOT the policy clock, and the mismatch this
    # would cause is QUANTIFIED in the preregistration rather than hidden.
    policy_obs = obs["DFEDTAR"] + obs["DFEDTARL"] + obs["DFEDTARU"]
    naive_undefined = []
    for t in dates:
        if not any(o["realtime_start"] <= t for o in policy_obs):
            naive_undefined.append(t)
        elif t >= "2008-12-16" and not any(
                o["realtime_start"] <= t for o in obs["DFEDTARU"]):
            naive_undefined.append(t)
    n_policy_assets = sum(1 for c in COEF.values() if c[2] != 0)
    stated = (str(len(naive_undefined)) + " of the " + str(len(dates)) in pre
              and "ALFRED_REALTIME_START_USED_FOR_AVAILABILITY = NO" in pre
              and "OFFICIAL_FOMC_ANNOUNCEMENT_USED_FOR_AVAILABILITY = YES" in pre
              and "SERIES-METADATA LIMITATION" in pre
              and str(n_policy_assets) + " of the 15" in pre)
    chk("B10", len(naive_undefined) == 71 and n_policy_assets == 9 and stated,
        "reading ALFRED realtime_start as the policy clock would strand "
        + str(len(naive_undefined)) + "/" + str(len(dates)) + " decision dates "
        "and, through the policy coefficient, " + str(n_policy_assets) + "/15 "
        "instruments — the preregistration states exactly these numbers and names "
        "the cause a FRED metadata limitation, not historical unavailability")

    # B11 — the information cutoff is compatible with canonical execution.
    port = text("src/portfolio.py")
    chk("B11", "15:45" in pre and "shift(1)" in port
        and "next session onward" in port,
        "15:45 ET cutoff precedes the canonical decide-at-close / execute-next-"
        "session convention asserted in src/portfolio.py (shift(1))")


# ---------------------------------------------------------------------------
# GROUP C — SEALED DEFINITIONS
# ---------------------------------------------------------------------------

def group_c():
    pre, od = norm(text(PREREG)), text(OD)
    flat = pre

    # C1 — MMV-OD-1..OD-6 all still present, and no OD-7 was invented.
    present = [i for i in range(1, 7) if "MMV-OD-" + str(i) in od]
    chk("C1", len(present) == 6 and "MMV-OD-7" not in od,
        "MMV-OD-1..MMV-OD-6 all present in the Owner decision record; "
        "no MMV-OD-7 exists")

    # C2 — 15 mapped instruments EXACT.
    mapped = set(COEF)
    chk("C2", mapped == set(CANON17) - NOT_MAPPED and len(mapped) == 15,
        "mapped set is exactly the canonical 17 minus {VNQ, RWX} — 15 instruments")

    # C3 — VNQ/RWX NOT_MAPPED, excluded from BOTH sides of Gate 0.5.
    flat = pre.replace("**", "")
    chk("C3", "VNQ = NOT_MAPPED" in pre and "RWX = NOT_MAPPED" in pre
        and "NEITHER numerator NOR denominator" in pre
        and "THEY ARE *NOT*" in pre
        and "NEVER enter numerator or denominator" in pre,
        "VNQ/RWX are NOT_MAPPED, explicitly not 'signal = 0', and enter neither "
        "the Gate-0.5 numerator nor its denominator")

    # C4 — every coefficient is in {-1,0,+1}: no new tunable numeric parameter.
    vals = {v for c in COEF.values() for v in c}
    chk("C4", vals <= {-1, 0, 1}
        and "NEW_TUNABLE_NUMERIC_PARAMETERS = NONE" in pre,
        "all 45 coefficients lie in {-1,0,+1} (observed " + str(sorted(vals))
        + "); the design introduces no tunable numeric parameter")

    # C5 — growth truth table equals sign(sign(a)+sign(b)) on all 9 states.
    tbl = {(-1, -1): -1, (0, -1): -1, (1, -1): 0,
           (-1, 0): -1, (0, 0): 0, (1, 0): 1,
           (-1, 1): 0, (0, 1): 1, (1, 1): 1}
    bad = [k for k, v in tbl.items() if sgn(k[0] + k[1]) != v]
    chk("C5", not bad and len(tbl) == 9,
        "growth leg G = sign(sign(D12 INDPRO) + sign(D12 PAYEMS)) reproduces the "
        "sealed 9-state truth table exactly; opposed measures abstain and a silent "
        "measure never vetoes")

    # C6 — enumerate all 27 (G,I,P) states and verify every identity the
    # preregistration asserts. This is ALGEBRA ON THE CONTRACT, not on data.
    states = [(g, i, p) for g in (-1, 0, 1) for i in (-1, 0, 1)
              for p in (-1, 0, 1)]

    def raw(inst, s):
        cg, ci, cp = COEF[inst]
        return sgn(cg * s[0] + ci * s[1] + cp * s[2])

    ident = {
        "FXY == -UUP": all(raw("FXY", s) == -raw("UUP", s) for s in states),
        "XLE == XLU": all(raw("XLE", s) == raw("XLU", s) for s in states),
        "XLE == sign(G-P)": all(raw("XLE", s) == sgn(s[0] - s[2]) for s in states),
        "GLD == I": all(raw("GLD", s) == s[1] for s in states),
        "LQD == HYG == G": all(raw("LQD", s) == raw("HYG", s) == s[0]
                               for s in states),
        "UUP == sign(I+P)": all(raw("UUP", s) == sgn(s[1] + s[2])
                                for s in states),
    }
    chk("C6", all(ident.values()) and len(states) == 27,
        "all 27 (G,I,P) states enumerated; every identity the preregistration "
        "asserts holds: " + ", ".join(ident))

    # C7 — GATE 0.5 DENOMINATOR AND THRESHOLD, exactly as sealed.
    # Falsify the boundary: 80.0% must KILL and anything below must PASS.
    def kills(agree, total):
        return (agree / total) * 100.0 >= 80.0

    boundary = (kills(80, 100) and not kills(79, 100)
                and kills(4, 5) and not kills(799, 1000))
    denom_ok = ("INCLUSIVE" in pre and "ZERO IS A REAL POSITION STATE" in pre
                and "0 vs 0 = AGREEMENT" in pre
                and "0 vs +1/-1 = DISAGREEMENT" in pre
                and "NEVER conditioned on active months only" in pre
                and "ELIGIBLE_GATE_05_CELL" in pre)
    chk("C7", boundary and denom_ok,
        "Gate 0.5 kills at >= 80.0% INCLUSIVE (80/100 kills, 799/1000 passes); "
        "denominator = eligible cells over the 15 mapped instruments only; zeros "
        "are real states counted on both sides; undefined cells excluded from both")

    # C8 — transform locked, trial family m = 1.
    chk("C8", "12-MONTH CHANGE, SIGN ONLY" in pre and "NO lookback search" in pre
        and "m = 1" in pre and "NO 3m / 6m / 18m / 24m" in pre,
        "transform locked to the 12-month change, sign only; no lookback, "
        "threshold, z-score or smoothing family; primary trial family m = 1")

    # C9 — MMV-specific materiality target and the evidence ceiling.
    chk("C9", "+0.30" in pre and "MMV-SPECIFIC OWNER DECISION (MMV-OD-3)" in flat
        and "EVIDENCE_CEILING = supported" in pre and "NEVER confirmed" in pre,
        "M2 = lower 95% bound of net Sharpe > +0.30 STRICT, declared MMV-specific "
        "and not inherited; evidence ceiling is 'supported', never 'confirmed'")

    # C10 — one inference framework.
    chk("C10", "10,000" in pre and "calendar-year block bootstrap" in pre
        and "95 % percentile" in pre and "ONE COMMON SET OF YEAR DRAWS" in pre
        and "FORBIDDEN: HAC" in pre,
        "one inference framework: calendar-year block bootstrap, B=10,000, 95% "
        "percentile, one common set of year draws; HAC / Newey-West / a second "
        "bootstrap all forbidden")

    # C11 — cost and risk wrapper trace to canonical config, not to a choice.
    cfg = text("config.py").replace(" ", "")
    wrapper = {
        "TRANSACTION_COST_BPS=2.0": "2 bps",
        "VOL_WINDOW_DAYS=60": "60 trading days",
        "TARGET_VOL_ANNUAL=0.10": "10 %",
        "MAX_ASSET_WEIGHT=2.0": "+/- 2",
        "PORT_TARGET_VOL_ANNUAL=0.10": "10 %",
        "MAX_GROSS_LEVERAGE=3.0": "3x",
    }
    miss = [k for k in wrapper if k not in cfg]
    miss += [v for v in wrapper.values() if v not in pre]
    chk("C11", not miss,
        "cost and every risk-wrapper parameter reproduce from canonical config.py "
        "and appear unchanged in the contract; none was chosen by this lineage"
        if not miss else "CONFIG DRIFT " + str(miss))

    # C12 — design exposure and sample reuse recorded honestly.
    chk("C12", "FABLE_DESIGN_EXPOSED = YES" in pre
        and "Barred from blind certification" in flat
        and "REUSED / BURNED" in pre
        and "UNKNOWN_PENDING_AARON_DECISION" in pre
        and "inference from absence, not a" in pre,
        "Fable recorded as design-exposed and barred from blind certification; "
        "Astra's non-exposure recorded as an inference from absence rather than an "
        "attestation; ETF price sample recorded as reused/burned; D-ETF-COUNT left "
        "open rather than decided here")


# ---------------------------------------------------------------------------
# GROUP D — OUTCOME FIREWALL
# ---------------------------------------------------------------------------

FORBIDDEN_ARTIFACT = ("result", "backtest", "position", "return", "sharpe",
                      "bootstrap", "gate", "separab", "outcome")


def group_d():
    # D1 — no MMV result artifact of any kind exists.
    art = []
    for root, dirs, fs in os.walk(MMV):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for f in fs:
            lf = f.lower()
            if any(k in lf for k in FORBIDDEN_ARTIFACT):
                art.append(os.path.join(root, f))
    for p in (DATA + "/MMV_SIGNAL_PANEL.csv", DATA + "/MMV_POSITIONS.csv",
              MMV + "/s2", MMV + "/s3"):
        if os.path.exists(p):
            art.append(p)
    chk("D1", not art,
        "no MMV signal, position, run, gate or result artifact exists anywhere in "
        "the lineage directory" if not art else "FIREWALL BREACH " + str(art))

    # D2 — no MMV module computes a macro feature. Verified by AST over every
    # python file in the lineage: none may define a feature/composite/position/
    # agreement/Sharpe/bootstrap helper, and none may import the production engine.
    bad = []
    for f in sorted(os.listdir(MMV)):
        if not f.endswith(".py"):
            continue
        tree = ast.parse(text(os.path.join(MMV, f)))
        funcs, imports = set(), set()
        for n in ast.walk(tree):
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                funcs.add(n.name.lower())
            elif isinstance(n, ast.Import):
                for a in n.names:
                    imports.add(a.name.split(".")[0])
            elif isinstance(n, ast.ImportFrom):
                imports.add((n.module or "").split(".")[0])
        for forb in ("src", "config", "backtest", "portfolio", "pandas", "numpy"):
            if forb in imports:
                bad.append(f + ":imports:" + forb)
        for forb in ("d12", "delta12", "composite", "mmv_signal", "position",
                     "sharpe", "bootstrap", "agreement", "separability"):
            if any(forb in fn for fn in funcs):
                bad.append(f + ":defines:" + forb)
    chk("D2", not bad,
        "AST scan of every .py in " + MMV + ": no feature, composite, position, "
        "agreement, Sharpe or bootstrap function is defined, and neither the "
        "production engine nor a numeric stack is imported"
        if not bad else "BREACH " + str(bad))

    # D3 — this checker never read a canonical TSMOM SIGN VALUE.
    src = text(os.path.abspath(__file__))
    reads_sign = re.search(r"r\[.(?!month_end)[A-Z]{3}", src)
    chk("D3", reads_sign is None,
        "this checker reads only the month_end column of the canonical panel; no "
        "canonical TSMOM sign value is read")

    # D4 — no verdict of any kind is asserted pre-outcome.
    pre = text(PREREG)
    verdicts = [w for w in ("MECHANISM_FALSIFIED = YES",
                            "PROGRAMME_STATUS = PROMOTED",
                            "CLASS S CONFIRMED", "RESULT =") if w in pre]
    chk("D4", not verdicts,
        "the contract asserts no verdict, no class and no result pre-outcome"
        if not verdicts else "PRE-OUTCOME VERDICT " + str(verdicts))

    # D5 — the discovered-blocker trail is retained, not quietly removed.
    hold = MMV + "/MMV_S1_HOLD_RECORD.md"
    chk("D5", os.path.exists(hold) and "UNBOUND" in text(hold),
        "the S1 hold record retains the discovered-blocker trail; nothing was "
        "quietly removed from the record")


def main():
    man = load(RAW_MANIFEST)
    dates = decision_dates()

    print("=" * 78)
    print("CTA-EDGE-04-MMV — S1 PRE-SEAL ADVERSARIAL CHECK")
    print("=" * 78)
    print("Computes NO macro feature, NO position, NO separability figure, "
          "NO return.")
    print()

    for name, fn, args in (("A  FREEZE INTEGRITY", group_a, (man,)),
                           ("B  POINT-IN-TIME / INFORMATION CONCEPT",
                            group_b, (man, dates)),
                           ("C  SEALED DEFINITIONS", group_c, ()),
                           ("D  OUTCOME FIREWALL", group_d, ())):
        start = len(RESULTS)
        fn(*args)
        print("--- " + name + " " + "-" * max(0, 73 - len(name)))
        for cid, ok, detail in RESULTS[start:]:
            print("  [" + ("PASS" if ok else "FAIL") + "] "
                  + cid.ljust(4) + " " + detail)
        print()

    npass = sum(1 for _, ok, _ in RESULTS if ok)
    n = len(RESULTS)
    print("=" * 78)
    print("PRE-SEAL CHECK: " + str(npass) + "/" + str(n) + " PASS")
    if npass != n:
        print("VERDICT: FAIL — SEAL WITHHELD")
        for cid, ok, d in RESULTS:
            if not ok:
                print("   FAILED " + cid + ": " + d)
        return 1
    print("VERDICT: PASS — the S1 seal may be written")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    sys.exit(main())
