"""
FragBoost licensing — free vs premium unlock with owner override.

- SECRET_CODE default: 'FRAG42'  (rotatable at runtime by owner via config)
- OWNER_CODE:          '2006james'  (hardcoded, not rotatable — your master key)

State file: %APPDATA%\\GamingOptimizer\\license.json
Config file: %APPDATA%\\GamingOptimizer\\owner_config.json  (holds rotated secret code)
"""
import json
from pathlib import Path
from optimizations import APPDIR

# Hardcoded (immutable at runtime)
OWNER_CODE = "2006james"
DEFAULT_SECRET_CODE = "FRAG42"

LICENSE_FILE = APPDIR / "license.json"
OWNER_CFG = APPDIR / "owner_config.json"


def _load(p: Path):
    if p.exists():
        try:
            return json.loads(p.read_text())
        except Exception:
            return {}
    return {}


def _save(p: Path, d):
    p.write_text(json.dumps(d, indent=2))


def get_secret_code() -> str:
    """Runtime secret code — rotated one wins if set."""
    cfg = _load(OWNER_CFG)
    return cfg.get("secret_code") or DEFAULT_SECRET_CODE


def rotate_secret_code(new_code: str) -> bool:
    new_code = (new_code or "").strip()
    if not new_code or len(new_code) < 3 or len(new_code) > 40:
        return False
    if new_code == OWNER_CODE:
        return False
    cfg = _load(OWNER_CFG)
    cfg["secret_code"] = new_code
    _save(OWNER_CFG, cfg)
    return True


def reset_secret_code():
    cfg = _load(OWNER_CFG)
    cfg.pop("secret_code", None)
    _save(OWNER_CFG, cfg)


def is_unlocked() -> bool:
    d = _load(LICENSE_FILE)
    if d.get("revoked_by_owner"):
        return False
    return d.get("unlocked") is True


def is_owner_revoked() -> bool:
    return _load(LICENSE_FILE).get("revoked_by_owner") is True


def is_owner_session() -> bool:
    """Was the owner code entered this app session? (session-only flag)"""
    return _OWNER_SESSION["active"]


_OWNER_SESSION = {"active": False}


def clear_owner_session():
    _OWNER_SESSION["active"] = False


def submit_code(code: str) -> tuple[str, str]:
    """
    Returns (level, message).
      level ∈ {"owner_unlock", "owner_revoke", "unlock", "already", "bad"}
    """
    code = (code or "").strip()
    if not code:
        return "bad", "Please enter a code."

    if code == OWNER_CODE:
        _OWNER_SESSION["active"] = True
        d = _load(LICENSE_FILE)
        if d.get("revoked_by_owner"):
            d["revoked_by_owner"] = False
            d["unlocked"] = True
            _save(LICENSE_FILE, d)
            return "owner_unlock", "\U0001F451  Owner override: premium re-enabled on this PC."
        else:
            d["revoked_by_owner"] = True
            d["unlocked"] = False
            _save(LICENSE_FILE, d)
            return "owner_revoke", "\U0001F451  Owner override: premium access REVOKED on this PC."

    if code == get_secret_code():
        d = _load(LICENSE_FILE)
        if d.get("revoked_by_owner"):
            return "bad", "\u274C This PC has been revoked by the owner."
        if d.get("unlocked"):
            return "already", "\u2713 Premium already unlocked on this PC."
        d["unlocked"] = True
        _save(LICENSE_FILE, d)
        return "unlock", "\U0001F513  Premium unlocked \u2014 all 53 tweaks available."

    return "bad", "\u274C Invalid code."
