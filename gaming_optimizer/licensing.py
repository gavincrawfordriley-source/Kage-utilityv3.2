"""
FragBoost licensing — free vs premium unlock.

- SECRET_CODE  ('FRAG42')  → unlocks locked tweaks on this PC (persists).
- OWNER_CODE   ('2006james') → wipes any saved unlock on this PC AND blocks
  future use of the secret code (owner revoke). Owner can re-unlock by
  entering the same owner code again (it toggles).

State file: %APPDATA%\GamingOptimizer\license.json
"""
import json
import hashlib
from pathlib import Path
from optimizations import APPDIR

# ---- codes (change here if you ever want to rotate them) ----
SECRET_CODE = "FRAG42"
OWNER_CODE = "2006james"

LICENSE_FILE = APPDIR / "license.json"


def _hash(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _load():
    if LICENSE_FILE.exists():
        try:
            return json.loads(LICENSE_FILE.read_text())
        except Exception:
            return {}
    return {}


def _save(d):
    LICENSE_FILE.write_text(json.dumps(d, indent=2))


def is_unlocked() -> bool:
    d = _load()
    if d.get("revoked_by_owner"):
        return False
    return d.get("unlocked") is True


def is_owner_revoked() -> bool:
    return _load().get("revoked_by_owner") is True


def submit_code(code: str) -> tuple[str, str]:
    """
    Returns (level, message).
      level ∈ {"owner_unlock", "owner_revoke", "unlock", "already", "bad"}
    """
    code = (code or "").strip()
    if not code:
        return "bad", "Please enter a code."

    if code == OWNER_CODE:
        d = _load()
        if d.get("revoked_by_owner"):
            # owner re-enabling access
            d["revoked_by_owner"] = False
            d["unlocked"] = True
            _save(d)
            return "owner_unlock", "\U0001F451  Owner override: premium re-enabled on this PC."
        else:
            # owner revoking
            d["revoked_by_owner"] = True
            d["unlocked"] = False
            _save(d)
            return "owner_revoke", "\U0001F451  Owner override: premium access REVOKED on this PC."

    if code == SECRET_CODE:
        d = _load()
        if d.get("revoked_by_owner"):
            return "bad", "\u274C This PC has been revoked by the owner. Only the owner code can restore access."
        if d.get("unlocked"):
            return "already", "\u2713 Premium already unlocked on this PC."
        d["unlocked"] = True
        _save(d)
        return "unlock", "\U0001F513  Premium unlocked \u2014 all 53 tweaks are now available."

    return "bad", "\u274C Invalid code."
