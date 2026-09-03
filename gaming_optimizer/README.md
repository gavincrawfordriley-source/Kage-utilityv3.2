# FragBoost — Windows 11 Gaming Optimizer

A modern, dark-themed desktop app that applies (and safely reverts) the tweaks
every gaming guide tells you to do — with one click each.

## Tweaks included
| Tweak | What it does |
|---|---|
| ⚡ Ultimate Performance Power Plan | Unlocks the hidden power plan for max CPU responsiveness |
| ❌ Disable Xbox Game Bar & Game DVR | Kills the overlay + background recorder that eats FPS |
| 🎮 Enable Windows Game Mode | Prioritises resources for your active game |
| ✨ Disable Visual Effects & Animations | Sets Windows to "best performance" |
| 🚀 Disable Startup Apps | Boots Windows lean; fully restorable |
| 🧹 Clean Temp Files | Wipes %TEMP%, Windows\Temp, Prefetch |
| 🖱 Disable Mouse Acceleration | 1:1 aim, no "Enhance pointer precision" |

Every change is backed up to `%APPDATA%\GamingOptimizer\backup.json` and can be
reverted with **Restore All** or by flipping the individual toggle off.

---

## Running from source (dev)

```bat
pip install -r requirements.txt
python main.py
```

Right-click → **Run as administrator** if you want power-plan / HKLM tweaks.

---

## Building the .exe to share with friends

On any Windows 11 machine with Python 3.10+ installed, just double-click:

```
build.bat
```

You'll get a single portable file:

```
dist\FragBoost.exe
```

- No install needed on your friend's PC
- UAC prompts for admin automatically (`--uac-admin` flag)
- Roughly 25 MB, ships with its own Python runtime

Send that one file. Done.

---

## Safety

- Every registry key & powercfg GUID is **backed up before change**
- Nothing is destructive — restore returns you exactly to your previous values
- Temp cleanup only deletes files Windows also deletes automatically
- No telemetry, no network calls, 100% offline
