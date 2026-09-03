"""Profile presets — save/load named collections of enabled tweaks."""
import json
from pathlib import Path
from optimizations import APPDIR, TWEAKS

PROFILES_FILE = APPDIR / "profiles.json"

# Built-in presets (tweak_id lists)
BUILTIN = {
    "Competitive FPS": [
        "power_plan", "core_parking", "cpu_throttle", "usb_suspend", "pcie_lpm",
        "nagle", "net_throttle", "net_buffers", "qos_reserve",
        "hp_gpu", "gpu_preempt", "game_priority",
        "mouse_accel", "sticky_keys", "kb_delay", "device_priority",
        "prio_sep", "fullscreen_notifs", "focus_assist", "sys_responsiveness",
        "game_bar", "game_dvr", "game_mode", "hags", "no_fso",
        "vfx", "no_anim", "no_transp", "menu_delay",
        "bg_apps", "widgets", "cortana",
    ],
    "AAA Cinematic": [
        "power_plan", "core_parking", "cpu_throttle",
        "hp_gpu", "gpu_preempt", "game_priority",
        "game_mode", "hags", "auto_hdr", "no_fso",
        "bg_apps", "widgets", "sysmain",
        "audio_dpc",
    ],
    "Streaming Setup": [
        "power_plan", "core_parking",
        "game_mode", "hags",
        "bg_apps", "widgets", "cortana",
        "audio_enh", "audio_dpc",
        "prio_sep", "sys_responsiveness",
    ],
    "Minimal / Safe": [
        "game_mode", "game_bar", "game_dvr",
        "vfx", "no_anim", "menu_delay",
        "clean_temp", "clean_dns",
        "ad_id", "feedback",
    ],
}


def _load():
    if PROFILES_FILE.exists():
        try:
            return json.loads(PROFILES_FILE.read_text())
        except Exception:
            return {}
    return {}


def _save(d):
    PROFILES_FILE.write_text(json.dumps(d, indent=2))


def list_profiles():
    user = _load()
    result = {}
    for name, ids in BUILTIN.items():
        result[name] = {"builtin": True, "tweaks": ids}
    for name, ids in user.items():
        result[name] = {"builtin": False, "tweaks": ids}
    return result


def save_profile(name: str, tweak_ids: list):
    if not name.strip():
        return False
    if name in BUILTIN:
        return False  # can't overwrite built-ins
    user = _load()
    user[name] = tweak_ids
    _save(user)
    return True


def delete_profile(name: str):
    if name in BUILTIN:
        return False
    user = _load()
    if name in user:
        del user[name]
        _save(user)
        return True
    return False


def get_profile(name: str):
    return list_profiles().get(name)


def current_enabled_ids():
    """IDs of all tweaks currently in 'on' state."""
    result = []
    for t in TWEAKS:
        try:
            if t["status"]() == "on":
                result.append(t["id"])
        except Exception:
            pass
    return result
