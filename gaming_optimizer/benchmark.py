"""System snapshot / benchmark — reports the state that affects gaming perf."""
import os
import subprocess
import platform


def _run(cmd):
    try:
        r = subprocess.run(
            cmd, shell=True, capture_output=True, text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        return (r.stdout or "").strip()
    except Exception:
        return ""


def collect():
    """Return list of (label, value, good_bool_or_None)."""
    rows = []

    # OS
    rows.append(("Operating System",
                 f"{platform.system()} {platform.release()} ({platform.version()})",
                 None))
    rows.append(("Machine", f"{platform.machine()} \u2013 {platform.processor()}", None))

    if os.name != "nt":
        rows.append(("Note", "Non-Windows platform \u2014 gaming stats unavailable", False))
        return rows

    # Active power plan
    plan = _run("powercfg /getactivescheme")
    good = None
    if "e9a42b02" in plan.lower():
        val, good = "Ultimate Performance", True
    elif "8c5e7fda" in plan.lower():
        val, good = "High Performance", True
    elif "381b4222" in plan.lower():
        val, good = "Balanced", False
    else:
        val = plan.split("(")[-1].rstrip(")").strip() or "Unknown"
    rows.append(("Active Power Plan", val, good))

    # CPU min state
    out = _run("powercfg /query scheme_current sub_processor PROCTHROTTLEMIN")
    if "0x00000064" in out.lower():
        rows.append(("CPU Min State", "100% (no throttling)", True))
    elif out:
        rows.append(("CPU Min State", "throttled (< 100%)", False))

    # Core parking
    out = _run("powercfg /query scheme_current sub_processor CPMINCORES")
    if "0x00000064" in out.lower():
        rows.append(("CPU Core Parking", "Disabled (100% cores active)", True))
    elif out:
        rows.append(("CPU Core Parking", "Enabled", False))

    # Hibernation
    hib = os.path.exists("C:/hiberfil.sys")
    rows.append(("Hibernation", "Enabled (hiberfil.sys present)" if hib else "Disabled",
                 not hib))

    # Game DVR (registry)
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"System\GameConfigStore") as k:
            v, _ = winreg.QueryValueEx(k, "GameDVR_Enabled")
            rows.append(("Game DVR", "Disabled" if v == 0 else "Enabled", v == 0))
    except Exception:
        rows.append(("Game DVR", "Unknown", None))

    # Game Bar
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\GameBar") as k:
            v, _ = winreg.QueryValueEx(k, "AppCaptureEnabled")
            rows.append(("Xbox Game Bar", "Disabled" if v == 0 else "Enabled", v == 0))
    except Exception:
        rows.append(("Xbox Game Bar", "Default", None))

    # Game Mode
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\GameBar") as k:
            v, _ = winreg.QueryValueEx(k, "AllowAutoGameMode")
            rows.append(("Game Mode", "Enabled" if v == 1 else "Disabled", v == 1))
    except Exception:
        rows.append(("Game Mode", "Default", None))

    # HAGS
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                            r"SYSTEM\CurrentControlSet\Control\GraphicsDrivers") as k:
            v, _ = winreg.QueryValueEx(k, "HwSchMode")
            rows.append(("Hardware GPU Scheduling", "On" if v == 2 else "Off", v == 2))
    except Exception:
        rows.append(("Hardware GPU Scheduling", "Default", None))

    # Mouse accel
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Mouse") as k:
            v, _ = winreg.QueryValueEx(k, "MouseSpeed")
            rows.append(("Mouse Acceleration", "Off" if v == "0" else "On", v == "0"))
    except Exception:
        rows.append(("Mouse Acceleration", "Default (On)", False))

    # Visual FX
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                            r"Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects") as k:
            v, _ = winreg.QueryValueEx(k, "VisualFXSetting")
            rows.append(("Visual FX", "Best Performance" if v == 2 else "Default", v == 2))
    except Exception:
        rows.append(("Visual FX", "Default", None))

    # Startup apps count
    try:
        import winreg
        count = 0
        for hive, path in (
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
            (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run"),
        ):
            try:
                with winreg.OpenKey(hive, path) as k:
                    i = 0
                    while True:
                        try:
                            winreg.EnumValue(k, i)
                            count += 1
                            i += 1
                        except OSError:
                            break
            except FileNotFoundError:
                continue
        rows.append(("Startup Apps", f"{count} entries", count == 0))
    except Exception:
        pass

    # SysMain
    out = _run("sc query SysMain")
    if "stopped" in out.lower():
        rows.append(("SysMain (Superfetch)", "Stopped", True))
    elif "running" in out.lower():
        rows.append(("SysMain (Superfetch)", "Running", False))

    # System responsiveness
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                            r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile") as k:
            v, _ = winreg.QueryValueEx(k, "SystemResponsiveness")
            rows.append(("System Responsiveness Reserve",
                         f"{v}% (lower = more for games)", v <= 10))
    except Exception:
        pass

    # Score
    good_count = sum(1 for _, _, g in rows if g is True)
    total = sum(1 for _, _, g in rows if g is not None)
    if total:
        score = int((good_count / total) * 100)
        rows.insert(0, ("Optimization Score", f"{score}%  ({good_count}/{total} tweaks active)",
                        score >= 70))

    return rows
