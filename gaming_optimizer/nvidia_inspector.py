"""
NVIDIA Profile Inspector auto-optimization.

Detects nvidiaProfileInspector.exe on the user's PC and applies a bundled
gaming-optimized profile via the CLI flag  '-silentImport <path.nip>'.
"""
import os
import subprocess
import sys
from pathlib import Path

INSPECTOR_EXE = "nvidiaProfileInspector.exe"

# Bundled preset name (co-located with this module OR extracted from PyInstaller bundle)
PRESET_NAME = "kage_max_performance.nip"


def _search_paths() -> list[Path]:
    home = Path.home()
    return [
        home / "Desktop" / INSPECTOR_EXE,
        home / "Downloads" / INSPECTOR_EXE,
        home / "Documents" / INSPECTOR_EXE,
        home / "Downloads" / "nvidiaProfileInspector" / INSPECTOR_EXE,
        Path("C:/Program Files/nvidiaProfileInspector") / INSPECTOR_EXE,
        Path("C:/Program Files (x86)/nvidiaProfileInspector") / INSPECTOR_EXE,
        Path("C:/nvidiaProfileInspector") / INSPECTOR_EXE,
        Path("C:/Tools/nvidiaProfileInspector") / INSPECTOR_EXE,
    ]


def find_inspector() -> str | None:
    """Return absolute path to nvidiaProfileInspector.exe, or None if not installed."""
    for p in _search_paths():
        try:
            if p.exists():
                return str(p)
        except Exception:
            continue
    # Also check PATH
    from shutil import which
    p = which(INSPECTOR_EXE)
    if p:
        return p
    # Last resort — recurse Desktop and Downloads shallow (depth 2)
    for root in (Path.home() / "Desktop", Path.home() / "Downloads"):
        try:
            if not root.exists():
                continue
            for child in root.iterdir():
                if child.is_dir():
                    cand = child / INSPECTOR_EXE
                    if cand.exists():
                        return str(cand)
        except Exception:
            continue
    return None


def _preset_path() -> str:
    """Return the bundled .nip preset (works both dev and PyInstaller runtime)."""
    here = os.path.dirname(os.path.abspath(__file__))
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        here = sys._MEIPASS
    return os.path.join(here, PRESET_NAME)


def apply_optimized(exe_path: str) -> tuple[bool, str]:
    """
    Silently apply the Kage max-performance preset via nvidiaProfileInspector.
    Returns (ok, message).
    """
    preset = _preset_path()
    if not os.path.exists(preset):
        return False, f"Preset file missing: {preset}"
    try:
        # -silentImport applies the .nip without opening the GUI
        subprocess.Popen(
            [exe_path, "-silentImport", preset],
            stdin=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        return True, "Applied Kage max-performance NVIDIA profile."
    except Exception as e:
        return False, f"Failed to run Profile Inspector: {e}"


def launch_gui(exe_path: str) -> bool:
    """Open Profile Inspector so the user can browse settings themselves."""
    try:
        subprocess.Popen(
            [exe_path],
            stdin=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        return True
    except Exception:
        return False
