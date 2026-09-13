# -*- coding: utf-8 -*-
"""Blindness boundary — protected storage outside the repo, encrypted at rest.

WHY THIS EXISTS
---------------
The S2 build protected prospective positions and outcomes by API discipline: the
operator-facing views returned counts and booleans, but the underlying JSON sat in
plaintext on disk, so `cat`, an editor, a repo-wide grep, or a one-line
`json.load` exposed the position vector and the payload with no authorization at
all. A go-live preflight probe demonstrated exactly that. Sealed §T.3 requires
that no human see a position vector before the authorized terminal reveal, so a
rule that depends only on operators choosing the polite API is not sufficient.

THE BOUNDARY, AND ITS HONEST LIMIT
----------------------------------
Three mechanisms, smallest set that makes ordinary access fail:

  1. PROTECTED STORE OUTSIDE THE REPOSITORY. Nothing protected is written into the
     working tree, so git, grep, code review, editors and diff never surface it.
  2. ENCRYPTED AT REST. The bytes on disk are ciphertext. `cat` yields nothing.
  3. THE KEY LIVES OUTSIDE THE REPOSITORY and is never committed. Reading requires
     the key plus a deliberate capability call — not a stray file open.

**Honest limit, stated plainly: Aaron owns this machine and the key file, so this
is not secrecy against Aaron.** It cannot be, and nothing here pretends otherwise.
What it does provide is the standard the contract actually needs: the sealed
blindness rule no longer depends only on voluntary API discipline. Ordinary
operational use — running the pipeline, reading a report, opening the store,
grepping the repo — cannot expose a position vector or an outcome. Circumvention
now requires deliberately locating the key and calling a decryption path, which is
a knowing act and not an accident.

CRYPTOGRAPHY
------------
`cryptography` is not installed in this environment (checked, both interpreters),
so this uses a stdlib construction: encrypt-then-MAC with domain-separated
subkeys, a 16-byte random nonce, and an HMAC-SHA256 counter-mode keystream. That
is a sound construction for at-rest confidentiality against ordinary access, and
it is **not** offered as a substitute for a vetted AEAD against a motivated
attacker. The threat model here is an operator's ordinary reach, not an adversary.

REPRODUCIBILITY IS NOT WEAKENED
-------------------------------
The SHA-256 of the *plaintext* is recorded in the clear alongside the ciphertext,
so record identity stays reproducible and verifiable without decrypting. The
machine pipeline reads through `open_envelope` with a `MachineCapability` whenever
it legitimately needs the prior position (turnover) or a recomputation.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import io
import os
import secrets

from . import ca_contract as K

KEY_ENV = "CA_PROSPECTIVE_KEY_FILE"
STORE_ENV = "CA_PROSPECTIVE_STORE"


class ProtectedStoreMisconfigured(Exception):
    """Raised when the protected store or key would live inside the repository."""


class CapabilityRequired(Exception):
    """Raised when protected content is requested without a machine capability."""


class EnvelopeTampered(Exception):
    """Raised when an envelope fails its authentication tag."""


# --------------------------------------------------------------------------- #
# Locations — outside the repository, always
# --------------------------------------------------------------------------- #
def default_store_dir() -> str:
    env = os.environ.get(STORE_ENV)
    if env:
        return os.path.abspath(env)
    base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    return os.path.abspath(os.path.join(base, "ca_prospective_store"))


def default_key_file() -> str:
    env = os.environ.get(KEY_ENV)
    if env:
        return os.path.abspath(env)
    return os.path.join(default_store_dir(), "blind.key")


def _inside_repo(path: str) -> bool:
    a = os.path.normcase(os.path.abspath(path))
    b = os.path.normcase(os.path.abspath(K.REPO))
    return a == b or a.startswith(b + os.sep)


def assert_outside_repo(path: str, what: str) -> str:
    if _inside_repo(path):
        raise ProtectedStoreMisconfigured(
            "REFUSED: the %s must live OUTSIDE the repository working tree so that "
            "git, grep, editors and code review can never surface protected content. "
            "Got %s, which is inside %s." % (what, path, K.REPO))
    return os.path.abspath(path)


def ensure_store(store_dir: str | None = None) -> str:
    d = assert_outside_repo(store_dir or default_store_dir(), "protected store")
    os.makedirs(d, exist_ok=True)
    return d


def ensure_key(key_file: str | None = None) -> bytes:
    """Return the 32-byte blinding key, creating it on first use. Never in the repo."""
    kf = assert_outside_repo(key_file or default_key_file(), "blinding key file")
    os.makedirs(os.path.dirname(kf), exist_ok=True)
    if not os.path.exists(kf):
        with io.open(kf, "wb") as fh:
            fh.write(base64.b64encode(secrets.token_bytes(32)))
        try:
            os.chmod(kf, 0o600)
        except Exception:
            pass
    with io.open(kf, "rb") as fh:
        return base64.b64decode(fh.read())


# --------------------------------------------------------------------------- #
# Capability — the supported machine path, made explicit and auditable
# --------------------------------------------------------------------------- #
class MachineCapability:
    """Held by the pipeline when it legitimately needs protected content.

    Legitimate purposes are exactly the ones the sealed contract requires: the
    prior position vector for turnover (§F.1 step 2), a locked-vs-recomputed
    diagnostic (§T.2), and the terminal reveal (§V).
    """

    PURPOSES = ("TURNOVER_PRIOR_POSITION", "LOCKED_VS_RECOMPUTED_DIAGNOSTIC",
                "TERMINAL_REVEAL", "SYNTHETIC_TEST")

    def __init__(self, purpose: str, *, key_file: str | None = None):
        if purpose not in self.PURPOSES:
            raise CapabilityRequired(
                "unsupported purpose %r; the supported machine purposes are %s"
                % (purpose, list(self.PURPOSES)))
        self.purpose = purpose
        self._key = ensure_key(key_file)


# --------------------------------------------------------------------------- #
# Encrypt-then-MAC, stdlib only
# --------------------------------------------------------------------------- #
def _subkeys(key: bytes):
    enc = hmac.new(key, b"ca-prospective-enc", hashlib.sha256).digest()
    mac = hmac.new(key, b"ca-prospective-mac", hashlib.sha256).digest()
    return enc, mac


def _keystream(enc_key: bytes, nonce: bytes, n: int) -> bytes:
    out = bytearray()
    counter = 0
    while len(out) < n:
        out += hmac.new(enc_key, nonce + counter.to_bytes(8, "big"), hashlib.sha256).digest()
        counter += 1
    return bytes(out[:n])


def seal_envelope(plaintext: bytes, *, key_file: str | None = None) -> dict:
    """Encrypt-then-MAC. Records the PLAINTEXT sha256 in the clear for reproducibility."""
    key = ensure_key(key_file)
    enc_key, mac_key = _subkeys(key)
    nonce = secrets.token_bytes(16)
    ct = bytes(a ^ b for a, b in zip(plaintext, _keystream(enc_key, nonce, len(plaintext))))
    tag = hmac.new(mac_key, nonce + ct, hashlib.sha256).hexdigest()
    return {
        "scheme": "HMAC-SHA256-CTR+HMAC-SHA256 (encrypt-then-MAC, stdlib)",
        "nonce": base64.b64encode(nonce).decode(),
        "ciphertext": base64.b64encode(ct).decode(),
        "tag": tag,
        "plaintext_sha256": hashlib.sha256(plaintext).hexdigest(),
        "plaintext_bytes": len(plaintext),
    }


def open_envelope(env: dict, capability: MachineCapability | None = None,
                  *, key_file: str | None = None) -> bytes:
    """The ONLY decryption path. Refuses without a MachineCapability."""
    if capability is None or not isinstance(capability, MachineCapability):
        raise CapabilityRequired(
            "REFUSED: protected content requires a MachineCapability naming a supported "
            "purpose. Sealed §T.3: no human may see a position vector before the "
            "authorized terminal reveal.")
    key = ensure_key(key_file)
    enc_key, mac_key = _subkeys(key)
    nonce = base64.b64decode(env["nonce"])
    ct = base64.b64decode(env["ciphertext"])
    if not hmac.compare_digest(hmac.new(mac_key, nonce + ct, hashlib.sha256).hexdigest(), env["tag"]):
        raise EnvelopeTampered("REFUSED: envelope authentication tag does not verify")
    pt = bytes(a ^ b for a, b in zip(ct, _keystream(enc_key, nonce, len(ct))))
    if hashlib.sha256(pt).hexdigest() != env["plaintext_sha256"]:
        raise EnvelopeTampered("REFUSED: decrypted plaintext does not match the recorded hash")
    return pt


def boundary_report() -> dict:
    """Operator-safe description of where the boundary is. No content."""
    store, keyf = default_store_dir(), default_key_file()
    return {
        "protected_store_dir": store,
        "protected_store_outside_repo": not _inside_repo(store),
        "key_file": keyf,
        "key_file_outside_repo": not _inside_repo(keyf),
        "key_file_present": os.path.exists(keyf),
        "encrypted_at_rest": True,
        "scheme": "HMAC-SHA256-CTR + HMAC-SHA256 encrypt-then-MAC (stdlib; no AEAD library available)",
        "honest_limit": ("Aaron owns the machine and the key file, so this is not secrecy "
                         "against the Owner. It removes the dependence on voluntary API "
                         "discipline: ordinary operational access cannot expose protected "
                         "content."),
    }
