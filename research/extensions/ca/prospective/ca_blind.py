# -*- coding: utf-8 -*-
"""Blindness boundary — protected store outside the repo, AES-256-GCM at rest.

WHY THIS EXISTS
---------------
A go-live probe showed the first build's protected files were plaintext JSON in
the working tree: `cat`, an editor, a repo grep or a one-line `json.load` exposed
a position vector and an outcome payload with no authorization. Sealed §T.3
forbids any human seeing a position vector before the authorized terminal reveal,
so a rule resting on voluntary API discipline was not sufficient.

An interim repair used a hand-rolled encrypt-then-MAC construction. That is not
acceptable for a study that must hold for ~10 years, so it has been **removed
entirely** and replaced with a vetted AEAD.

WHAT PROTECTS THE CONTENT NOW
-----------------------------
* **AES-256-GCM** from `cryptography` (pyca). No home-grown cipher, no home-grown
  MAC composition, no home-grown key derivation.
* **A fresh 96-bit nonce per object**, from `os.urandom`.
* **Associated data** binds each ciphertext to its own immutable envelope identity
  (record type, record id, holding month, snapshot identity, sealed prereg hash,
  schema version), so ciphertext cannot be silently transplanted between records.
  No scientific outcome value is ever placed in AAD.
* **Authentication failure hard-fails** (`InvalidTag` -> `EnvelopeTampered`).
  There is no "decrypt anyway" path.
* **Plaintext is never written to disk.** Sealing happens in memory and only the
  ciphertext envelope is written.
* Protected content and the key live **outside the repository**; a path inside the
  repo is refused.

KEY LIFECYCLE — EXPLICIT, AND NEVER AUTOMATIC
---------------------------------------------
`initialize_blind_store()` is the ONLY thing that may create a key, and it refuses
if the store is already initialized. Nothing else creates key material — there is
no "ensure_key" ambient path any more. Once a store is initialized:

    key missing | key unreadable | fingerprint changed  ->  HARD HOLD

`unlock_store()` raises `ProtectedStoreHold` and **never** generates a new key,
continues with a different key, overwrites the stored identity, or creates a
second key. The non-secret fingerprint `SHA256(master_key)` is recorded in the
store's own state file (S2 operational state — never in the sealed S1 contract)
and is verified on every unlock.

THE CAPABILITY IS NOT DECORATIVE
--------------------------------
A `MachineCapability` cannot be constructed by ordinary code: it is issued only by
an unlocked `BlindSession`, and it carries the key. Calling `MachineCapability(...)`
directly raises. Since there is no ambient key loader, code that has not explicitly
unlocked a fingerprint-verified store cannot decrypt anything.

HONEST THREAT BOUNDARY
----------------------
Aaron owns this machine, the key file and the repository. This is **not** secrecy
against the Owner or a machine administrator, and nothing here pretends otherwise.
The property actually delivered is the one the contract needs: **accidental or
normal supported operator actions cannot decrypt protected content.** Deliberate
Owner/admin circumvention is outside the threat model.
"""
from __future__ import annotations

import base64
import hashlib
import io
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

import cryptography as _cryptography

from . import ca_contract as K

KEY_ENV = "CA_PROSPECTIVE_KEY_FILE"
STORE_ENV = "CA_PROSPECTIVE_STORE"
STATE_FILENAME = "store_state.json"

AEAD_NAME = "AES-256-GCM"
NONCE_BYTES = 12
KEY_BYTES = 32
SCHEMA = "CA_BLIND_ENVELOPE_V2_AESGCM"


class ProtectedStoreMisconfigured(Exception):
    """Raised when the protected store or key would live inside the repository."""


class ProtectedStoreNotInitialized(Exception):
    """Raised when the store has not been explicitly initialized."""


class ProtectedStoreHold(Exception):
    """HARD HOLD: key missing, unreadable, or its fingerprint changed."""


class CapabilityRequired(Exception):
    """Raised when protected content is requested without an issued capability."""


class EnvelopeTampered(Exception):
    """Raised when AEAD authentication fails. Never recoverable."""


# --------------------------------------------------------------------------- #
# Locations — outside the repository, always
# --------------------------------------------------------------------------- #
def default_store_dir() -> str:
    env = os.environ.get(STORE_ENV)
    if env:
        return os.path.abspath(env)
    base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    return os.path.abspath(os.path.join(base, "ca_prospective_store"))


def default_key_file(store_dir: str | None = None) -> str:
    env = os.environ.get(KEY_ENV)
    if env:
        return os.path.abspath(env)
    return os.path.join(store_dir or default_store_dir(), "blind.key")


def _inside_repo(path: str) -> bool:
    a = os.path.normcase(os.path.abspath(path))
    b = os.path.normcase(os.path.abspath(K.REPO))
    return a == b or a.startswith(b + os.sep)


def assert_outside_repo(path: str, what: str) -> str:
    if _inside_repo(path):
        raise ProtectedStoreMisconfigured(
            "REFUSED: the %s must live OUTSIDE the repository working tree so git, "
            "grep, editors and code review can never surface protected content. "
            "Got %s." % (what, path))
    return os.path.abspath(path)


def state_path(store_dir: str | None = None) -> str:
    return os.path.join(assert_outside_repo(store_dir or default_store_dir(),
                                            "protected store"), STATE_FILENAME)


def store_state(store_dir: str | None = None):
    p = state_path(store_dir)
    if not os.path.exists(p):
        return None
    with io.open(p, encoding="utf-8") as fh:
        return json.load(fh)


def is_initialized(store_dir: str | None = None) -> bool:
    return store_state(store_dir) is not None


# --------------------------------------------------------------------------- #
# Local permission hardening (best effort, honestly reported)
# --------------------------------------------------------------------------- #
def _harden_permissions(path: str) -> dict:
    """Restrict to the current user. Windows: icacls. POSIX: chmod 0600/0700."""
    out = {"path": path, "method": None, "ok": False, "detail": ""}
    try:
        if os.name == "nt":
            user = os.environ.get("USERNAME") or ""
            subprocess.run(["icacls", path, "/inheritance:r"],
                           capture_output=True, text=True, timeout=30)
            r = subprocess.run(["icacls", path, "/grant:r", "%s:(F)" % user],
                               capture_output=True, text=True, timeout=30)
            out.update(method="icacls", ok=(r.returncode == 0), detail=r.stdout.strip()[-120:])
        else:
            os.chmod(path, 0o700 if os.path.isdir(path) else 0o600)
            out.update(method="chmod", ok=True, detail="0600/0700")
    except Exception as exc:  # noqa: BLE001
        out.update(detail="%s: %s" % (type(exc).__name__, exc))
    return out


BROAD_PRINCIPALS = ("Everyone", "BUILTIN\\Users", "Authenticated Users", "BUILTIN\\Guests")


def permissions_report(path: str) -> dict:
    """Report whether broad/shared principals can read the path. No key material."""
    rep = {"path": path, "exists": os.path.exists(path), "broad_principals": [],
           "checked": False, "detail": ""}
    if not rep["exists"]:
        return rep
    try:
        if os.name == "nt":
            r = subprocess.run(["icacls", path], capture_output=True, text=True, timeout=30)
            rep["checked"] = True
            rep["detail"] = r.stdout.strip()[-300:]
            rep["broad_principals"] = [p for p in BROAD_PRINCIPALS if p in r.stdout]
        else:
            mode = os.stat(path).st_mode & 0o777
            rep["checked"] = True
            rep["detail"] = oct(mode)
            if mode & 0o077:
                rep["broad_principals"] = ["group/other"]
    except Exception as exc:  # noqa: BLE001
        rep["detail"] = "%s: %s" % (type(exc).__name__, exc)
    rep["broad_readable"] = bool(rep["broad_principals"])
    return rep


# --------------------------------------------------------------------------- #
# Explicit initialization — the ONLY place a key is ever created
# --------------------------------------------------------------------------- #
def fingerprint(key: bytes) -> str:
    """Non-secret stable identity of the key. Safe to record in operational state."""
    return hashlib.sha256(key).hexdigest()


def initialize_blind_store(store_dir: str | None = None, key_file: str | None = None,
                           *, note: str = "") -> dict:
    """Create the protected store and its key EXACTLY ONCE. Refuses to re-initialize."""
    sd = assert_outside_repo(store_dir or default_store_dir(), "protected store")
    kf = assert_outside_repo(key_file or default_key_file(sd), "blinding key file")
    if is_initialized(sd):
        raise ProtectedStoreHold(
            "REFUSED: protected store at %s is ALREADY INITIALIZED. Re-initialising "
            "would create a second key and orphan every existing protected record. "
            "There is no re-initialise path." % sd)
    if os.path.exists(kf):
        raise ProtectedStoreHold(
            "REFUSED: a key already exists at %s but the store has no state file. "
            "Refusing to adopt or overwrite an unidentified key — resolve manually." % kf)
    os.makedirs(sd, exist_ok=True)
    _harden_permissions(sd)
    key = AESGCM.generate_key(bit_length=256)          # secure RNG, vetted library
    os.makedirs(os.path.dirname(kf), exist_ok=True)
    with io.open(kf, "wb") as fh:
        fh.write(base64.b64encode(key))
    _harden_permissions(kf)
    state = {
        "schema": "CA_BLIND_STORE_V1",
        "aead": AEAD_NAME,
        "key_bytes": KEY_BYTES,
        "nonce_bytes": NONCE_BYTES,
        "cryptography_version": _cryptography.__version__,
        "key_file": kf,
        "key_fingerprint_sha256": fingerprint(key),     # NON-SECRET
        "initialized_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "sealed_prereg_sha256": K.SEALED_PREREG_SHA256,
        "note": note,
    }
    with io.open(state_path(sd), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(state, fh, indent=2, sort_keys=True)
        fh.write("\n")
    _harden_permissions(state_path(sd))
    return state


# --------------------------------------------------------------------------- #
# Unlock — hard-fails; never regenerates
# --------------------------------------------------------------------------- #
class BlindSession:
    """An unlocked protected store. The ONLY issuer of MachineCapability."""

    __slots__ = ("store_dir", "state", "_key")

    def __init__(self, store_dir: str, state: dict, key: bytes):
        self.store_dir = store_dir
        self.state = state
        self._key = key

    def __repr__(self) -> str:                 # never leak key material
        return "<BlindSession store=%s fingerprint=%s…>" % (
            self.store_dir, self.state["key_fingerprint_sha256"][:12])

    __str__ = __repr__

    def capability(self, purpose: str) -> "MachineCapability":
        return MachineCapability(purpose, _token=_ISSUE_TOKEN, _key=self._key)

    # -- sealing / opening ------------------------------------------------- #
    def seal(self, plaintext: bytes, aad: dict) -> dict:
        return _seal(self._key, plaintext, aad)

    def open(self, envelope: dict, capability: "MachineCapability") -> bytes:
        return open_envelope(envelope, capability)


def unlock_store(store_dir: str | None = None, key_file: str | None = None) -> BlindSession:
    """Open an initialized store. HARD HOLD on missing / unreadable / changed key."""
    sd = assert_outside_repo(store_dir or default_store_dir(), "protected store")
    state = store_state(sd)
    if state is None:
        raise ProtectedStoreNotInitialized(
            "REFUSED: protected store at %s is not initialized. Run the explicit "
            "initialize_blind_store() step during the authorized go-live procedure. "
            "Nothing here creates a key implicitly." % sd)
    kf = key_file or state.get("key_file") or default_key_file(sd)
    if not os.path.exists(kf):
        raise ProtectedStoreHold(
            "HARD HOLD: the protected store at %s is initialized but its key file %s "
            "is MISSING. A new key is NOT generated and will never be. Restore the "
            "original key (fingerprint %s) from its off-repository backup."
            % (sd, kf, state["key_fingerprint_sha256"]))
    try:
        with io.open(kf, "rb") as fh:
            key = base64.b64decode(fh.read())
    except Exception as exc:  # noqa: BLE001
        raise ProtectedStoreHold(
            "HARD HOLD: key file %s is UNREADABLE (%s: %s). No key is generated."
            % (kf, type(exc).__name__, exc))
    if len(key) != KEY_BYTES:
        raise ProtectedStoreHold(
            "HARD HOLD: key file %s does not contain a %d-byte key." % (kf, KEY_BYTES))
    got = fingerprint(key)
    if got != state["key_fingerprint_sha256"]:
        raise ProtectedStoreHold(
            "HARD HOLD: key FINGERPRINT MISMATCH at %s.\n  expected %s\n  got      %s\n"
            "This is a different key. Continuing would orphan every existing protected "
            "record. Restoring a different key is forbidden." % (sd, state["key_fingerprint_sha256"], got))
    return BlindSession(sd, state, key)


# --------------------------------------------------------------------------- #
# Capability — issued only by an unlocked session
# --------------------------------------------------------------------------- #
_ISSUE_TOKEN = object()


class MachineCapability:
    """Carries the key for one declared machine purpose.

    Cannot be constructed by ordinary code: it is issued by `BlindSession.capability`
    and by nothing else. Because there is no ambient key loader, code that has not
    explicitly unlocked a fingerprint-verified store cannot decrypt anything.
    """

    PURPOSES = ("TURNOVER_PRIOR_POSITION", "LOCKED_VS_RECOMPUTED_DIAGNOSTIC",
                "TERMINAL_REVEAL", "SYNTHETIC_TEST")

    __slots__ = ("purpose", "_key")

    def __init__(self, purpose: str, *, _token=None, _key=None):
        if _token is not _ISSUE_TOKEN:
            raise CapabilityRequired(
                "REFUSED: a MachineCapability cannot be constructed directly. It is "
                "issued only by an unlocked BlindSession — unlock_store(...).capability(...) "
                "— which requires an initialized store and a verified key fingerprint.")
        if purpose not in self.PURPOSES:
            raise CapabilityRequired(
                "unsupported purpose %r; supported: %s" % (purpose, list(self.PURPOSES)))
        self.purpose = purpose
        self._key = _key

    def __repr__(self) -> str:                 # never leak key material
        return "<MachineCapability purpose=%s>" % self.purpose

    __str__ = __repr__


# --------------------------------------------------------------------------- #
# AEAD sealing / opening
# --------------------------------------------------------------------------- #
def canonical_aad(aad: dict) -> bytes:
    """Deterministic AAD bytes. Immutable identity fields only — never an outcome."""
    return json.dumps(aad, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _seal(key: bytes, plaintext: bytes, aad: dict) -> dict:
    nonce = os.urandom(NONCE_BYTES)
    ct = AESGCM(key).encrypt(nonce, plaintext, canonical_aad(aad))
    return {
        "schema": SCHEMA,
        "aead": AEAD_NAME,
        "nonce": base64.b64encode(nonce).decode(),
        "ciphertext": base64.b64encode(ct).decode(),
        "aad": aad,                                    # clear, non-secret, binding
        "plaintext_sha256": hashlib.sha256(plaintext).hexdigest(),   # reproducible identity
        "plaintext_bytes": len(plaintext),
        "key_fingerprint_sha256": fingerprint(key),    # non-secret
    }


def open_envelope(env: dict, capability: MachineCapability | None = None) -> bytes:
    """The ONLY decryption path. Requires an issued capability. Auth failure hard-fails."""
    if capability is None or not isinstance(capability, MachineCapability):
        raise CapabilityRequired(
            "REFUSED: protected content requires a MachineCapability issued by an "
            "unlocked BlindSession. Sealed §T.3: no human may see a position vector "
            "before the authorized terminal reveal.")
    key = capability._key
    if key is None:
        raise CapabilityRequired("REFUSED: capability carries no key material")
    if env.get("key_fingerprint_sha256") and env["key_fingerprint_sha256"] != fingerprint(key):
        raise ProtectedStoreHold(
            "HARD HOLD: this envelope was sealed under a different key "
            "(%s…) than the unlocked one (%s…)."
            % (env["key_fingerprint_sha256"][:12], fingerprint(key)[:12]))
    try:
        pt = AESGCM(key).decrypt(base64.b64decode(env["nonce"]),
                                 base64.b64decode(env["ciphertext"]),
                                 canonical_aad(env.get("aad", {})))
    except InvalidTag:
        raise EnvelopeTampered(
            "REFUSED: AEAD authentication failed — the ciphertext, its nonce or its "
            "associated data has been altered, or it was sealed under another key. "
            "There is no unauthenticated decryption path.")
    if hashlib.sha256(pt).hexdigest() != env["plaintext_sha256"]:
        raise EnvelopeTampered("REFUSED: plaintext does not match the recorded hash")
    return pt


# --------------------------------------------------------------------------- #
# Operator-safe reporting — no key material, ever
# --------------------------------------------------------------------------- #
def boundary_report(store_dir: str | None = None) -> dict:
    sd = store_dir or default_store_dir()
    st = store_state(sd) if not _inside_repo(sd) else None
    kf = (st or {}).get("key_file") or default_key_file(sd)
    return {
        "protected_store_dir": sd,
        "protected_store_outside_repo": not _inside_repo(sd),
        "key_file": kf,
        "key_file_outside_repo": not _inside_repo(kf),
        "store_initialized": st is not None,
        "key_fingerprint_sha256": (st or {}).get("key_fingerprint_sha256"),
        "key_file_present": os.path.exists(kf),
        "aead": AEAD_NAME,
        "cryptography_version": _cryptography.__version__,
        "custom_crypto": False,
        "store_permissions": permissions_report(sd),
        "key_permissions": permissions_report(kf),
        "threat_boundary": ("Accidental or normal supported operator actions cannot "
                            "decrypt protected content. This is NOT secrecy against "
                            "Aaron or a machine administrator, who own the key."),
    }
