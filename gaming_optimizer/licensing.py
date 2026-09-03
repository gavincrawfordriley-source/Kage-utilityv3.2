"""
Kage Utility licensing — free / premium / partner / owner tiers.

Codes (all rotatable at runtime, all case-insensitive):
  - Premium code default:  'FRAG42'
  - Partner code default:  'KAGE-PARTNER'
  - Owner code default:    '2006james'

State: %APPDATA%\\GamingOptimizer\\license.json
  {
    "unlocked": True,        # premium
    "partner":  True,        # partner tier
    "owner":    True,        # owner status (persistent per-PC)
    "revoked_by_owner": False
  }

Config: %APPDATA%\\GamingOptimizer\\owner_config.json
  {
    "secret_code":  "..."    # rotated premium code
    "partner_code": "..."    # rotated partner code
    "owner_code":   "..."    # rotated owner code
    "custom_bg_path": "..."  # path to user-supplied background image
  }
"""
import json
from pathlib import Path
from optimizations import APPDIR

# Defaults (used when nothing rotated yet)
DEFAULT_OWNER_CODE = "2006james"
DEFAULT_PARTNER_CODE = "KAGE-PARTNER"
DEFAULT_SECRET_CODE = "FRAG42"

# Backward-compat alias (old settings_ui references licensing.OWNER_CODE)
OWNER_CODE = DEFAULT_OWNER_CODE

LICENSE_FILE = APPDIR / "license.json"
OWNER_CFG = APPDIR / "owner_config.json"


# ---------- storage helpers ----------
def _load(p: Path):
    if p.exists():
        try:
            return json.loads(p.read_text())
        except Exception:
            return {}
    return {}


def _save(p: Path, d):
    p.write_text(json.dumps(d, indent=2))


# ---------- current codes (rotated wins) ----------
def get_secret_code() -> str:
    return _load(OWNER_CFG).get("secret_code") or DEFAULT_SECRET_CODE


def get_partner_code() -> str:
    return _load(OWNER_CFG).get("partner_code") or DEFAULT_PARTNER_CODE


def get_owner_code() -> str:
    return _load(OWNER_CFG).get("owner_code") or DEFAULT_OWNER_CODE


# ---------- rotation ----------
def _rotate(key: str, new_code: str, forbidden: list[str]) -> bool:
    new_code = (new_code or "").strip()
    if not new_code or len(new_code) < 3 or len(new_code) > 40:
        return False
    if new_code.lower() in [c.lower() for c in forbidden if c]:
        return False
    cfg = _load(OWNER_CFG)
    cfg[key] = new_code
    _save(OWNER_CFG, cfg)
    return True


def rotate_secret_code(new_code: str) -> bool:
    return _rotate("secret_code", new_code,
                   [get_owner_code(), get_partner_code()])


def rotate_partner_code(new_code: str) -> bool:
    return _rotate("partner_code", new_code,
                   [get_owner_code(), get_secret_code()])


def rotate_owner_code(new_code: str) -> bool:
    return _rotate("owner_code", new_code,
                   [get_partner_code(), get_secret_code()])


def reset_secret_code():
    cfg = _load(OWNER_CFG)
    cfg.pop("secret_code", None)
    _save(OWNER_CFG, cfg)


def reset_partner_code():
    cfg = _load(OWNER_CFG)
    cfg.pop("partner_code", None)
    _save(OWNER_CFG, cfg)


def reset_owner_code():
    cfg = _load(OWNER_CFG)
    cfg.pop("owner_code", None)
    _save(OWNER_CFG, cfg)


# ---------- tier checks (persistent per-PC) ----------
def is_unlocked() -> bool:
    d = _load(LICENSE_FILE)
    if d.get("revoked_by_owner"):
        return False
    return d.get("unlocked") is True or d.get("owner") is True or d.get("partner") is True


def is_partner() -> bool:
    return _load(LICENSE_FILE).get("partner") is True or _load(LICENSE_FILE).get("owner") is True


def is_owner() -> bool:
    return _load(LICENSE_FILE).get("owner") is True


def is_owner_revoked() -> bool:
    return _load(LICENSE_FILE).get("revoked_by_owner") is True


# ---------- session (owner-console gating) ----------
_OWNER_SESSION = {"active": False}


def is_owner_session() -> bool:
    """True if owner code was entered this session, OR PC is persistently owner."""
    return _OWNER_SESSION["active"] or is_owner()


def clear_owner_session():
    _OWNER_SESSION["active"] = False


# ---------- custom background (owner / partner only) ----------
def get_custom_bg_path() -> str | None:
    return _load(OWNER_CFG).get("custom_bg_path")


def set_custom_bg_path(path: str) -> bool:
    if not path:
        return False
    cfg = _load(OWNER_CFG)
    cfg["custom_bg_path"] = str(path)
    _save(OWNER_CFG, cfg)
    return True


def reset_custom_bg():
    cfg = _load(OWNER_CFG)
    cfg.pop("custom_bg_path", None)
    _save(OWNER_CFG, cfg)


# ---------- manual revoke (owner console) ----------
def owner_revoke_pc():
    """Owner action: revoke premium on this PC."""
    d = _load(LICENSE_FILE)
    d["revoked_by_owner"] = True
    d["unlocked"] = False
    _save(LICENSE_FILE, d)


def owner_reenable_pc():
    d = _load(LICENSE_FILE)
    d["revoked_by_owner"] = False
    d["unlocked"] = True
    _save(LICENSE_FILE, d)


# ---------- code submission ----------
def submit_code(code: str) -> tuple[str, str]:
    """
    Returns (level, message).
      level ∈ {"owner_unlock", "partner_unlock", "unlock",
               "already", "bad"}
    All comparisons are case-insensitive and whitespace-tolerant.
    """
    code = (code or "").strip()
    if not code:
        return "bad", "Please enter a code."
    code_norm = code.lower()

    # 1) Owner code — grants persistent owner + premium
    if code_norm == get_owner_code().lower():
        _OWNER_SESSION["active"] = True
        d = _load(LICENSE_FILE)
        d["owner"] = True
        d["unlocked"] = True
        d["revoked_by_owner"] = False
        _save(LICENSE_FILE, d)
        return "owner_unlock", (
            "\U0001F451  Owner rights granted on this PC. "
            "Full access to Owner Console, Partnership Panel, and background customization."
        )

    # 2) Partner code — grants partner (which includes premium + customization)
    if code_norm == get_partner_code().lower():
        d = _load(LICENSE_FILE)
        if d.get("revoked_by_owner"):
            return "bad", "\u274C This PC has been revoked by the owner."
        d["partner"] = True
        d["unlocked"] = True
        _save(LICENSE_FILE, d)
        return "partner_unlock", (
            "\U0001F91D  Partner tier unlocked \u2014 exclusive tweaks + background customization enabled."
        )

    # 3) Premium code
    if code_norm == get_secret_code().lower():
        d = _load(LICENSE_FILE)
        if d.get("revoked_by_owner"):
            return "bad", "\u274C This PC has been revoked by the owner."
        if d.get("unlocked"):
            return "already", "\u2713 Premium already unlocked on this PC."
        d["unlocked"] = True
        _save(LICENSE_FILE, d)
        return "unlock", "\U0001F513  Premium unlocked \u2014 all tweaks available."

    return "bad", "\u274C Invalid code."
