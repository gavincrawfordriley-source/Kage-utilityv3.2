"""
Windows 11 Gaming Optimizations
All tweak logic lives here. Each tweak has apply() and restore() methods.
Registry & powercfg backups are stored in backup.json so restore is safe.
"""
import os
import json
import shutil
import subprocess
import ctypes
import winreg
from pathlib import Path

BACKUP_FILE = Path(os.getenv("APPDATA", ".")) / "GamingOptimizer" / "backup.json"
BACKUP_FILE.parent.mkdir(parents=True, exist_ok=True)


# ---------- helpers ----------
def _load_backup():
    if BACKUP_FILE.exists():
        try:
            return json.loads(BACKUP_FILE.read_text())
        except Exception:
            return {}
    return {}


def _save_backup(data):
    BACKUP_FILE.write_text(json.dumps(data, indent=2))


def _run(cmd, shell=True):
    """Run a command hidden and capture output."""
    try:
        result = subprocess.run(
            cmd,
            shell=shell,
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        return result.returncode == 0, (result.stdout or "") + (result.stderr or "")
    except Exception as e:
        return False, str(e)


def _reg_get(hive, path, name):
    try:
        with winreg.OpenKey(hive, path, 0, winreg.KEY_READ) as key:
            val, typ = winreg.QueryValueEx(key, name)
            return val, typ
    except FileNotFoundError:
        return None, None
    except Exception:
        return None, None


def _reg_set(hive, path, name, value, typ=winreg.REG_DWORD):
    try:
        winreg.CreateKey(hive, path)
        with winreg.OpenKey(hive, path, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, name, 0, typ, value)
        return True
    except Exception as e:
        return False


def _reg_delete(hive, path, name):
    try:
        with winreg.OpenKey(hive, path, 0, winreg.KEY_SET_VALUE) as key:
            winreg.DeleteValue(key, name)
        return True
    except Exception:
        return False


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


# ---------- 1. Power Plan ----------
HIGH_PERF_GUID = "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"
ULTIMATE_GUID = "e9a42b02-d5df-448d-aa00-03f14749eb61"


def get_power_plan_status():
    ok, out = _run("powercfg /getactivescheme")
    if not ok:
        return "unknown"
    if HIGH_PERF_GUID in out.lower() or ULTIMATE_GUID in out.lower():
        return "on"
    return "off"


def apply_power_plan():
    backup = _load_backup()
    ok, out = _run("powercfg /getactivescheme")
    if ok and "guid:" in out.lower():
        current = out.lower().split("guid:")[1].strip().split(" ")[0]
        backup["power_plan_guid"] = current
        _save_backup(backup)

    # Try Ultimate Performance first (unlock it), fall back to High Performance
    _run(f"powercfg -duplicatescheme {ULTIMATE_GUID}")
    ok, _ = _run(f"powercfg /setactive {ULTIMATE_GUID}")
    if not ok:
        ok, _ = _run(f"powercfg /setactive {HIGH_PERF_GUID}")
    return ok


def restore_power_plan():
    backup = _load_backup()
    prev = backup.get("power_plan_guid")
    if prev:
        _run(f"powercfg /setactive {prev}")
    else:
        # Balanced plan default
        _run("powercfg /setactive 381b4222-f694-41f0-9685-ff5bb260df2e")
    return True


# ---------- 2. Xbox Game Bar & Game DVR ----------
def get_gamebar_status():
    val, _ = _reg_get(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\GameBar", "AppCaptureEnabled")
    val2, _ = _reg_get(winreg.HKEY_CURRENT_USER, r"System\GameConfigStore", "GameDVR_Enabled")
    if val == 0 and val2 == 0:
        return "on"  # meaning tweak is applied
    return "off"


def apply_gamebar_disable():
    backup = _load_backup()
    keys = [
        (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\GameBar", "AppCaptureEnabled", 0),
        (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\GameBar", "AutoGameModeEnabled", 1),
        (winreg.HKEY_CURRENT_USER, r"System\GameConfigStore", "GameDVR_Enabled", 0),
        (winreg.HKEY_CURRENT_USER, r"System\GameConfigStore", "GameDVR_FSEBehaviorMode", 2),
    ]
    saved = backup.get("gamebar", {})
    for hive, path, name, new in keys:
        old, _ = _reg_get(hive, path, name)
        saved[f"{path}\\{name}"] = old
    backup["gamebar"] = saved
    _save_backup(backup)

    for hive, path, name, new in keys:
        _reg_set(hive, path, name, new)
    # HKLM policy - disables game bar entirely (requires admin)
    _reg_set(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows\GameDVR", "AllowGameDVR", 0)
    return True


def restore_gamebar():
    backup = _load_backup()
    saved = backup.get("gamebar", {})
    for full_path, val in saved.items():
        parts = full_path.rsplit("\\", 1)
        path, name = parts[0], parts[1]
        if val is None:
            _reg_delete(winreg.HKEY_CURRENT_USER, path, name)
        else:
            _reg_set(winreg.HKEY_CURRENT_USER, path, name, val)
    _reg_delete(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows\GameDVR", "AllowGameDVR")
    return True


# ---------- 3. Windows Game Mode ----------
def get_gamemode_status():
    val, _ = _reg_get(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\GameBar", "AllowAutoGameMode")
    val2, _ = _reg_get(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\GameBar", "AutoGameModeEnabled")
    if val == 1 or val2 == 1:
        return "on"
    return "off"


def apply_gamemode():
    backup = _load_backup()
    keys = [
        (r"Software\Microsoft\GameBar", "AllowAutoGameMode"),
        (r"Software\Microsoft\GameBar", "AutoGameModeEnabled"),
    ]
    saved = backup.get("gamemode", {})
    for path, name in keys:
        old, _ = _reg_get(winreg.HKEY_CURRENT_USER, path, name)
        saved[f"{path}\\{name}"] = old
        _reg_set(winreg.HKEY_CURRENT_USER, path, name, 1)
    backup["gamemode"] = saved
    _save_backup(backup)
    return True


def restore_gamemode():
    backup = _load_backup()
    saved = backup.get("gamemode", {})
    for full_path, val in saved.items():
        parts = full_path.rsplit("\\", 1)
        path, name = parts[0], parts[1]
        if val is None:
            _reg_delete(winreg.HKEY_CURRENT_USER, path, name)
        else:
            _reg_set(winreg.HKEY_CURRENT_USER, path, name, val)
    return True


# ---------- 4. Visual Effects / Animations ----------
def get_visualfx_status():
    val, _ = _reg_get(winreg.HKEY_CURRENT_USER,
                      r"Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects",
                      "VisualFXSetting")
    if val == 2:
        return "on"
    return "off"


def apply_visualfx_disable():
    backup = _load_backup()
    val, _ = _reg_get(winreg.HKEY_CURRENT_USER,
                      r"Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects",
                      "VisualFXSetting")
    backup["visualfx"] = val
    # Also backup UserPreferencesMask
    upm, _ = _reg_get(winreg.HKEY_CURRENT_USER, r"Control Panel\Desktop", "UserPreferencesMask")
    backup["visualfx_upm"] = list(upm) if upm else None
    _save_backup(backup)

    _reg_set(winreg.HKEY_CURRENT_USER,
             r"Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects",
             "VisualFXSetting", 2)
    # Disable window animations
    _reg_set(winreg.HKEY_CURRENT_USER, r"Control Panel\Desktop\WindowMetrics",
             "MinAnimate", "0", winreg.REG_SZ)
    # Disable menu animation
    _reg_set(winreg.HKEY_CURRENT_USER, r"Control Panel\Desktop", "UserPreferencesMask",
             bytes([0x90, 0x12, 0x03, 0x80, 0x10, 0x00, 0x00, 0x00]), winreg.REG_BINARY)
    return True


def restore_visualfx():
    backup = _load_backup()
    val = backup.get("visualfx")
    if val is None:
        _reg_delete(winreg.HKEY_CURRENT_USER,
                    r"Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects",
                    "VisualFXSetting")
    else:
        _reg_set(winreg.HKEY_CURRENT_USER,
                 r"Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects",
                 "VisualFXSetting", val)
    upm = backup.get("visualfx_upm")
    if upm:
        _reg_set(winreg.HKEY_CURRENT_USER, r"Control Panel\Desktop", "UserPreferencesMask",
                 bytes(upm), winreg.REG_BINARY)
    _reg_set(winreg.HKEY_CURRENT_USER, r"Control Panel\Desktop\WindowMetrics",
             "MinAnimate", "1", winreg.REG_SZ)
    return True


# ---------- 5. Startup Apps ----------
STARTUP_KEYS = [
    (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
    (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run"),
]


def list_startup_apps():
    apps = []
    for hive, path in STARTUP_KEYS:
        try:
            with winreg.OpenKey(hive, path, 0, winreg.KEY_READ) as key:
                i = 0
                while True:
                    try:
                        name, value, _ = winreg.EnumValue(key, i)
                        apps.append({
                            "name": name,
                            "command": value,
                            "hive": "HKCU" if hive == winreg.HKEY_CURRENT_USER else "HKLM",
                            "path": path,
                        })
                        i += 1
                    except OSError:
                        break
        except FileNotFoundError:
            continue
    return apps


def get_startup_status():
    apps = list_startup_apps()
    if not apps:
        return "on"  # nothing to disable, treat as clean
    return "off"


def disable_all_startup():
    backup = _load_backup()
    apps = list_startup_apps()
    backup["startup_apps"] = apps
    _save_backup(backup)
    for app in apps:
        hive = winreg.HKEY_CURRENT_USER if app["hive"] == "HKCU" else winreg.HKEY_LOCAL_MACHINE
        _reg_delete(hive, app["path"], app["name"])
    return True


def restore_startup():
    backup = _load_backup()
    apps = backup.get("startup_apps", [])
    for app in apps:
        hive = winreg.HKEY_CURRENT_USER if app["hive"] == "HKCU" else winreg.HKEY_LOCAL_MACHINE
        _reg_set(hive, app["path"], app["name"], app["command"], winreg.REG_SZ)
    return True


# ---------- 6. Temp Files Cleanup ----------
def get_temp_status():
    return "off"  # always available to run


def clean_temp_files():
    paths = [
        os.getenv("TEMP", ""),
        os.getenv("TMP", ""),
        r"C:\Windows\Temp",
        os.path.expandvars(r"%LOCALAPPDATA%\Temp"),
        os.path.expandvars(r"%SystemRoot%\Prefetch"),
    ]
    total = 0
    for p in set(paths):
        if not p or not os.path.exists(p):
            continue
        for root, dirs, files in os.walk(p):
            for f in files:
                fp = os.path.join(root, f)
                try:
                    total += os.path.getsize(fp)
                    os.remove(fp)
                except Exception:
                    continue
            for d in dirs:
                dp = os.path.join(root, d)
                try:
                    shutil.rmtree(dp, ignore_errors=True)
                except Exception:
                    continue
    return total  # bytes freed


# ---------- 7. Mouse Acceleration ----------
def get_mouseaccel_status():
    val, _ = _reg_get(winreg.HKEY_CURRENT_USER, r"Control Panel\Mouse", "MouseSpeed")
    if val == "0":
        return "on"
    return "off"


def apply_mouseaccel_disable():
    backup = _load_backup()
    saved = {}
    for name in ("MouseSpeed", "MouseThreshold1", "MouseThreshold2"):
        old, _ = _reg_get(winreg.HKEY_CURRENT_USER, r"Control Panel\Mouse", name)
        saved[name] = old
    backup["mouseaccel"] = saved
    _save_backup(backup)

    _reg_set(winreg.HKEY_CURRENT_USER, r"Control Panel\Mouse", "MouseSpeed", "0", winreg.REG_SZ)
    _reg_set(winreg.HKEY_CURRENT_USER, r"Control Panel\Mouse", "MouseThreshold1", "0", winreg.REG_SZ)
    _reg_set(winreg.HKEY_CURRENT_USER, r"Control Panel\Mouse", "MouseThreshold2", "0", winreg.REG_SZ)
    return True


def restore_mouseaccel():
    backup = _load_backup()
    saved = backup.get("mouseaccel", {})
    defaults = {"MouseSpeed": "1", "MouseThreshold1": "6", "MouseThreshold2": "10"}
    for name in ("MouseSpeed", "MouseThreshold1", "MouseThreshold2"):
        val = saved.get(name) or defaults[name]
        _reg_set(winreg.HKEY_CURRENT_USER, r"Control Panel\Mouse", name, val, winreg.REG_SZ)
    return True


# ---------- Tweak registry (used by GUI) ----------
TWEAKS = [
    {
        "id": "power_plan",
        "title": "Ultimate/High Performance Power Plan",
        "desc": "Unlocks and activates the Ultimate Performance power plan for maximum CPU responsiveness.",
        "icon": "\u26A1",
        "requires_admin": True,
        "apply": apply_power_plan,
        "restore": restore_power_plan,
        "status": get_power_plan_status,
    },
    {
        "id": "gamebar",
        "title": "Disable Xbox Game Bar & Game DVR",
        "desc": "Turns off Xbox Game Bar overlay and background recording that steal FPS.",
        "icon": "\u274C",
        "requires_admin": True,
        "apply": apply_gamebar_disable,
        "restore": restore_gamebar,
        "status": get_gamebar_status,
    },
    {
        "id": "gamemode",
        "title": "Enable Windows Game Mode",
        "desc": "Prioritizes system resources for the game currently in focus.",
        "icon": "\U0001F3AE",
        "requires_admin": False,
        "apply": apply_gamemode,
        "restore": restore_gamemode,
        "status": get_gamemode_status,
    },
    {
        "id": "visualfx",
        "title": "Disable Visual Effects & Animations",
        "desc": "Adjusts Windows for best performance — no fade, no shadows, no window animations.",
        "icon": "\u2728",
        "requires_admin": False,
        "apply": apply_visualfx_disable,
        "restore": restore_visualfx,
        "status": get_visualfx_status,
    },
    {
        "id": "startup",
        "title": "Disable All Startup Apps",
        "desc": "Removes autostart entries so Windows boots lean. Fully restorable.",
        "icon": "\U0001F680",
        "requires_admin": True,
        "apply": disable_all_startup,
        "restore": restore_startup,
        "status": get_startup_status,
    },
    {
        "id": "temp",
        "title": "Clean Temp Files",
        "desc": "Deletes junk from %TEMP%, C:\\Windows\\Temp and Prefetch. Frees disk & I/O.",
        "icon": "\U0001F9F9",
        "requires_admin": True,
        "apply": clean_temp_files,
        "restore": lambda: True,  # nothing to restore
        "status": get_temp_status,
    },
    {
        "id": "mouseaccel",
        "title": "Disable Mouse Acceleration",
        "desc": "Turns off 'Enhance pointer precision' for consistent 1:1 aim.",
        "icon": "\U0001F5B1",
        "requires_admin": False,
        "apply": apply_mouseaccel_disable,
        "restore": restore_mouseaccel,
        "status": get_mouseaccel_status,
    },
]
