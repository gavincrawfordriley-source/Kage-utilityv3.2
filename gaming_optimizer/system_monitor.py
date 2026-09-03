"""
System monitor — pulls live CPU, GPU, RAM usage and temperatures on Windows.
All queries are cheap and non-blocking. Fails gracefully on unsupported systems.
"""
import os
import subprocess
import shutil

try:
    import psutil
except ImportError:
    psutil = None


def cpu_usage() -> float:
    if psutil is None:
        return 0.0
    try:
        return float(psutil.cpu_percent(interval=None))
    except Exception:
        return 0.0


def ram_usage() -> tuple[float, float, float]:
    """Returns (percent, used_gb, total_gb)."""
    if psutil is None:
        return 0.0, 0.0, 0.0
    try:
        m = psutil.virtual_memory()
        return float(m.percent), m.used / (1024**3), m.total / (1024**3)
    except Exception:
        return 0.0, 0.0, 0.0


def _gpu_via_nvidia_smi() -> tuple[float | None, float | None]:
    """Returns (gpu_util_percent, gpu_temp_c) or (None, None)."""
    exe = shutil.which("nvidia-smi") or r"C:\Windows\System32\nvidia-smi.exe"
    if not os.path.exists(exe):
        return None, None
    try:
        r = subprocess.run(
            [exe, "--query-gpu=utilization.gpu,temperature.gpu",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=2,
            stdin=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        if r.returncode != 0:
            return None, None
        line = (r.stdout or "").strip().splitlines()[0]
        util_s, temp_s = [x.strip() for x in line.split(",")]
        util = float(util_s) if util_s.replace(".", "").isdigit() else None
        temp = float(temp_s) if temp_s.replace(".", "").isdigit() else None
        return util, temp
    except Exception:
        return None, None


def gpu_usage() -> float | None:
    util, _ = _gpu_via_nvidia_smi()
    return util


def gpu_temp() -> float | None:
    _, temp = _gpu_via_nvidia_smi()
    return temp


def cpu_temp() -> float | None:
    """
    Best-effort Windows CPU temperature.
    Uses WMI MSAcpi_ThermalZoneTemperature (works on many desktops/laptops).
    Kelvin*10 → Celsius.
    """
    if os.name != "nt":
        return None
    try:
        import wmi
        w = wmi.WMI(namespace=r"root\wmi")
        temps = w.MSAcpi_ThermalZoneTemperature()
        if not temps:
            return None
        # First zone is usually the CPU package on most boards
        kelvin_10 = temps[0].CurrentTemperature
        return (kelvin_10 / 10.0) - 273.15
    except Exception:
        return None


def snapshot() -> dict:
    """Convenience: return everything at once for the UI."""
    cpu_pct = cpu_usage()
    ram_pct, ram_used, ram_total = ram_usage()
    g_util, g_temp = _gpu_via_nvidia_smi()
    return {
        "cpu_pct": cpu_pct,
        "cpu_temp": cpu_temp(),
        "gpu_pct": g_util if g_util is not None else 0.0,
        "gpu_temp": g_temp,
        "gpu_present": g_util is not None,
        "ram_pct": ram_pct,
        "ram_used_gb": ram_used,
        "ram_total_gb": ram_total,
    }
