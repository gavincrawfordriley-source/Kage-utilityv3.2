# FragBoost — PRD

## Original problem statement
> "i want an app that can help optimize a pc for gaming like max power plan turns of xbox game bar and game mode yk that type of thing"

## Product
Windows 11 desktop gaming optimizer with 53 real, reversible tweaks.
Free + premium (code-gated) tiers, plus an owner override for the creator.

## Codes (owned by James)
- Secret / premium: `FRAG42`
- Owner override:   `2006james`  (toggles revoke ↔ re-enable per PC)

## Tech
- Python 3.10+, CustomTkinter (dark GUI)
- PyInstaller `--onefile --windowed --uac-admin` → single portable EXE

## Files (/app/gaming_optimizer)
- `optimizations.py` — all 53 tweaks (registry, powercfg, services, tasks)
- `licensing.py` — free/premium/owner code logic, persisted to %APPDATA%
- `main.py` — CTk GUI with category-grouped cards & lock overlay
- `build.bat` — one-click PyInstaller build
- `README.md` — usage + code reference
- `requirements.txt` — customtkinter + pyinstaller

## Tweak split
- 21 LOCKED (premium): CPU & Power (5), Network (5), GPU/DirectX (3), Input (4), System (4)
- 32 FREE: Gaming (6), Visuals (5), Startup (7), Disk (7), Privacy (5), Audio (2)

## Safety
- Every registry/powercfg value backed up to %APPDATA%\GamingOptimizer\backup.json BEFORE mutation
- Individual toggles + Apply All + Restore All
- Non-Windows platforms show a warning; tweaks silently no-op
- License state persisted to %APPDATA%\GamingOptimizer\license.json

## Verified
- All 53 tweaks load successfully
- Licensing flow tested: bad code → FRAG42 unlock → owner revoke → blocked → owner re-enable ✓
- Python lint: 0 errors

## Backlog / future
- Custom code editor in-app (right now you edit licensing.py)
- Per-tweak lock granularity (some free, some paid per category)
- Auto-update check
- Optional "Undo last" instead of full Restore All
