# -*- coding: utf-8 -*-
"""TSMOM-VRP-01 - module L: validators and acceptance gates.

Mechanical checks that do not need a fixture: constant transcription against the sealed
text, sealed-artifact hash re-pinning, structural isolation of the descriptive cost
variant, and the guarantee that no primary path can read a last-trade price or add a
funding charge.

Every function returns (ok, detail) so the acceptance runner can log it.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import os
import re
from typing import Dict, List, Sequence, Tuple

import vrp_constants as K

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

PREREG = os.path.join(HERE, "VRP_PREREGISTRATION.md")
ACC = os.path.join(HERE, "VRP_IMPLEMENTATION_ACCEPTANCE_CONTRACT.md")
EXP = os.path.join(HERE, "VRP_EXPOSURE_DISCLOSURE.md")
VALIDATOR = os.path.join(HERE, "vrp_prereg_validate.py")

SEALED_HASHES = {
    "VRP_PREREGISTRATION.md": K.PREREG_SHA256,
    "VRP_IMPLEMENTATION_ACCEPTANCE_CONTRACT.md": K.ACCEPTANCE_CONTRACT_SHA256,
    "VRP_EXPOSURE_DISCLOSURE.md": K.EXPOSURE_DISCLOSURE_SHA256,
    "vrp_prereg_validate.py": "4684ecb2c9a633a9d17413a067aa0987a110718518954579a87ffd6122667876",
}

# Modules that form the PRIMARY path. None of them may reference the descriptive cost
# variant, a last-trade price field, or a funding charge.
PRIMARY_MODULES = ("vrp_chain.py", "vrp_stage_a.py", "vrp_stage_b.py",
                   "vrp_sizing.py", "vrp_inference.py")


def _sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _flat(text: str) -> str:
    return re.sub(r"\s+", " ", text)


def _source(name: str) -> str:
    with open(os.path.join(HERE, name), encoding="utf-8") as fh:
        return fh.read()


def _code_only(src: str) -> str:
    src = re.sub(r'"""(?:.|\n)*?"""', "", src)
    src = re.sub(r"'''(?:.|\n)*?'''", "", src)
    return re.sub(r"#.*", "", src)


# --------------------------------------------------------------------------- #
def check_sealed_artifact_hashes() -> Tuple[bool, str]:
    """The S1 package must be byte-identical to what was sealed."""
    bad = []
    for name, expected in SEALED_HASHES.items():
        path = os.path.join(HERE, name)
        if not os.path.isfile(path) or _sha256(path) != expected:
            bad.append(name)
    return (not bad), ("unchanged: %d artifacts" % len(SEALED_HASHES) if not bad
                       else "MODIFIED: " + ",".join(bad))


def check_frozen_constants() -> Tuple[bool, str]:
    """Acceptance item 20: every frozen constant asserted against the SEALED TEXT."""
    text = _flat(open(PREREG, encoding="utf-8").read())
    required: List[Tuple[str, bool]] = [
        ("theta = 0.25", K.theta == 0.25),
        ("b = 0.30", K.b == 0.30),
        ("+0.075", K.E == 0.075),
        # the sealed text uses U+2212 MINUS SIGN, not an ASCII hyphen
        ("−F = −0.075", K.F == -0.075),
        ("J = 30", K.J == 30),
        ("m_J = 40", K.m_J == 40),
        ("lambda = 0.10", K.LAMBDA == 0.10),
        ("0.10 , normalized_contemporaneous_minimum_tick", K.c0 == 0.10),
        ("c0 = 0.05", K.c0_descriptive == 0.05),
        ("$2.00 per standard-contract-side", K.commission == 2.00 and K.fee == 2.00),
        ("beta = 0.06", K.beta == 0.06),
        ("= 0.20", K.s == 0.20),
        ("$1,000,000", K.W0 == 1000000),
        ("delta_tail = 0.0075", K.delta_tail == 0.0075),
        ("k = 3", K.k == 3),
        ("0.0025", K.ratio_floor == 0.0025),
        ("N_A = 120", K.N_A == 120),
        ("N_B = 120", K.N_B == 120),
        ("n_T_min_prosp = 10", K.n_T_min_prosp == 10),
        ("2026-09-01", K.cutoff == _dt.date(2026, 9, 1)),
        ("2026-05-31", K.stageB_end == _dt.date(2026, 5, 31)),
        ("12 months", K.block == 12),
        ("10,000", K.reps == 10000),
        ("9,500", K.floor == 9500),
        ("SeedSequence(7)", K.seed == 7),
        ("2026-09-11", K.CA_FORWARD_BOUNDARY == _dt.date(2026, 9, 11)),
        ("24 distinct calendar months", K.STAGE_A_MIN_DISTINCT_MONTHS == 24),
    ]
    bad = []
    for phrase, value_ok in required:
        in_text = _flat(phrase) in text
        if not (in_text and value_ok):
            bad.append("%s (text=%s value=%s)" % (phrase, in_text, value_ok))
    # the symmetric threshold and the derived identities
    derived = [
        ("E == theta * b", abs(K.E - K.theta * K.b) < 1e-15),
        ("F == -E", abs(K.F + K.E) < 1e-15),
        ("s == beta / b", abs(K.s - K.beta / K.b) < 1e-15),
        ("sensitivity == 0.01 * K", abs(K.b / K.J - 0.01) < 1e-15),
        ("R_J == 0.50 * K", abs(K.m_J * 0.01 + K.LAMBDA - 0.50) < 1e-15),
        ("(1-b) == 0.70", abs((1 - K.b) - 0.70) < 1e-15),
        ("core share == 0.80", abs(K.CORE_SHARE - (1 - K.s)) < 1e-15),
    ]
    bad += [name for name, ok in derived if not ok]
    return (not bad), ("%d constants + %d identities verified against the sealed text"
                       % (len(required), len(derived)) if not bad else "; ".join(bad))


def check_descriptive_cost_isolation() -> Tuple[bool, str]:
    """Acceptance item 6 / sabotage 'c0=.05 accidentally used in primary': no primary
    module may reference the descriptive cost variant at all."""
    bad = []
    for name in PRIMARY_MODULES:
        code = _code_only(_source(name))
        if "descriptive_cost_dollars" in code or "c0_descriptive" in code \
                or "DESCRIPTIVE_C0" in code:
            bad.append(name)
    return (not bad), ("no primary module references the c0 = 0.05 variant"
                       if not bad else "LEAK: " + ",".join(bad))


def check_no_last_trade_price() -> Tuple[bool, str]:
    """Section A5: official settlement only. No primary module may read a Close/last-trade
    field into a price, and the loader must only ever read `Settle`."""
    bad = []
    for name in PRIMARY_MODULES:
        code = _code_only(_source(name))
        if re.search(r'["\']Close["\']|last_trade|settlement_on_open|\bSOQ\b', code):
            bad.append(name)
    loader = _code_only(_source("vrp_raw.py"))
    reads = set(re.findall(r'rec\.get\(\s*"([A-Za-z ]+)"', loader))
    price_fields = reads & {"Close", "Open", "High", "Low"}
    if price_fields:
        bad.append("vrp_raw.py reads %s" % ",".join(sorted(price_fields)))
    return (not bad), ("settlement-only; loader reads %s" % ",".join(sorted(reads))
                       if not bad else "; ".join(bad))


def check_no_funding_charge() -> Tuple[bool, str]:
    """Section G: funding charge = NONE. No ledger may add one."""
    bad = []
    for name in ("vrp_stage_a.py", "vrp_stage_b.py"):
        code = _code_only(_source(name))
        if "funding_charge" in code or "interest" in code.lower() or "borrow" in code.lower():
            bad.append(name)
    return (not bad), ("no funding charge, interest or borrowing in either ledger"
                       if not bad else "; ".join(bad))


def check_no_clipping() -> Tuple[bool, str]:
    """Sections E.1 and H.2: no loss is clipped at -100 %."""
    bad = []
    for name in ("vrp_stage_a.py", "vrp_stage_b.py"):
        code = _code_only(_source(name))
        if re.search(r"max\(\s*-1(?:\.0)?\s*,", code) or re.search(r"clip\(", code):
            bad.append(name)
    return (not bad), "no clip / floor at -1.0 in either ledger" if not bad else ",".join(bad)


def check_calendar_consistency(calendar, start: _dt.date, end: _dt.date) -> Tuple[bool, str]:
    x = calendar.cross_check_rule(start, end)
    n = len(x["unexplained"])
    return (n == 0), ("%d declared CFE-only session(s), %d unexplained"
                      % (len(x["explained_cfe_open"]), n))


def check_expiry_identity(contracts: Sequence[object]) -> Tuple[bool, str]:
    import vrp_calendar as vcal
    bad = []
    expired = 0
    for c in contracts:
        if not c.expired:
            continue
        expired += 1
        y, m = int(c.contract_month[:4]), int(c.contract_month[5:])
        if vcal.monthly_final_settlement(y, m) != c.observed_last_settlement:
            bad.append(c.contract_month)
    return (not bad), ("%d expired contracts, %d mismatches" % (expired, len(bad)))


def check_seed_protocol() -> Tuple[bool, str]:
    """Acceptance item 16: the spawned entropy values match the seal manifest."""
    import vrp_inference as vinf
    got = vinf.spawned_entropy()
    expected = [{"name": n, "entropy": 7, "spawn_key": (i,)}
                for i, n in enumerate(K.SEED_SPAWN_ORDER)]
    return (got == expected), "SeedSequence(7).spawn(4) children in the sealed order"


def run_all(extra: Dict[str, Tuple[bool, str]] = None) -> List[Dict[str, object]]:
    checks = {
        "sealed S1 artifacts unmodified": check_sealed_artifact_hashes(),
        "frozen constants match the sealed text": check_frozen_constants(),
        "descriptive c0=0.05 isolated from the primary path": check_descriptive_cost_isolation(),
        "no last-trade / SOQ price on any primary path": check_no_last_trade_price(),
        "no funding charge in any ledger": check_no_funding_charge(),
        "no loss clipping in any ledger": check_no_clipping(),
        "seed protocol matches the seal manifest": check_seed_protocol(),
    }
    if extra:
        checks.update(extra)
    return [{"check": name, "pass": ok, "detail": detail}
            for name, (ok, detail) in checks.items()]
