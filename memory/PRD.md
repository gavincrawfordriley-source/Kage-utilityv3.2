# FragBoost — PRD

## Original problem statement
> "i want an app that can help optimize a pc for gaming like max power plan turns of xbox game bar and game mode yk that type of thing"

## Product
Windows 11 desktop gaming optimizer with 53 real, reversible tweaks.
Free tier (32) + Premium tier (21, code-gated) + Owner override.

## Codes (owned by James)
- Secret / premium: `FRAG42`  (rotatable at runtime via Owner Console)
- Owner override:   `2006james`  (hardcoded; toggles revoke ↔ re-enable per PC)

## Tech
- Python 3.10+, CustomTkinter (dark GUI, 5 themes)
- PyInstaller `--onefile --windowed --uac-admin` → single portable EXE

## Files (/app/gaming_optimizer)
- `optimizations.py` — 53 tweaks (registry, powercfg, services, schtasks)
- `licensing.py` — free/premium/owner code logic + runtime code rotation
- `themes.py` — 5 colour palettes
- `profiles.py` — 4 built-in presets + save/load custom profiles
- `benchmark.py` — system snapshot with Optimization Score %
- `settings_ui.py` — tabbed settings modal (Themes / Profiles / Benchmark / Owner)
- `main.py` — main CTk GUI with category-grouped cards & lock overlay
- `build.bat` — one-click PyInstaller build
- `README.md` — usage + code reference

## Tweak split
- 21 LOCKED (premium): CPU & Power (5), Network (5), GPU/DirectX (3), Input (4), System (4)
- 32 FREE: Gaming (6), Visuals (5), Startup (7), Disk (7), Privacy (5), Audio (2)

## Features shipped
- v1.0: 53 tweaks, free/premium codes, owner revoke, Apply All / Restore All
- v1.1: Custom themes (5), Profile presets (4 built-in + custom), Benchmark snapshot, Owner Console with runtime code rotation

## Safety
- Every registry/powercfg value backed up to %APPDATA%\GamingOptimizer\backup.json BEFORE mutation
- Individual toggles + Apply All + Restore All
- Non-Windows platforms show a warning; tweaks silently no-op
- License, settings, profiles, owner config persisted in %APPDATA%\GamingOptimizer

## Verified
- All 53 tweaks load successfully
- Licensing flow tested end-to-end
- Code rotation tested (rotate + reset)
- Owner session flag set correctly on 2006james entry
- All 4 built-in profiles reference valid tweak IDs
- Python lint: 0 errors

## Backlog
- Icon / branded EXE resource
- Auto-update via GitHub release check
- Per-tweak "undo last" instead of full Restore All
- Optional: export/import profiles as .json files to share with friends
