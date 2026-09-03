# Kage Utility 影 — PRD

## Original problem statement
> "i want an app that can help optimize a pc for gaming like max power plan turns of xbox game bar and game mode yk that type of thing"

## Product
Kage Utility — Windows 11 desktop gaming optimizer.
53 real reversible tweaks. Free tier + code-gated premium tier + owner override.
Black + purple ninja/shadow aesthetic. Ships as a single portable EXE with custom icon.

## Codes (owned by James)
- Secret / premium: `FRAG42`  (rotatable at runtime via Owner Console)
- Owner override:   `2006james`  (hardcoded)

## Tech stack
- Python 3.10+, CustomTkinter, Pillow (icon), packaging (semver)
- PyInstaller `--onefile --windowed --uac-admin --icon=icon.ico`

## Files (/app/gaming_optimizer)
- `optimizations.py` — 53 tweaks
- `licensing.py` — free/premium/owner logic + runtime code rotation
- `themes.py` — 6 palettes (Kage Purple default)
- `profiles.py` — 4 built-ins + custom save/load
- `benchmark.py` — system snapshot + score
- `history.py` — undo stack for single-step revert
- `updater.py` — async GitHub release check
- `settings_ui.py` — tabbed settings modal (Themes / Profiles / Benchmark / Owner)
- `generate_icon.py` — programmatic Kage K-shuriken icon (PIL)
- `main.py` — main CTk GUI
- `build.bat` — one-click build (icon gen + PyInstaller)
- `icon.ico` / `icon.png` — generated brand assets

## v1.2 additions (this iteration)
- Full rebrand: FragBoost → Kage Utility, tagline "Move like a shadow"
- Custom app icon: black tile + glowing purple K-shuriken (generated programmatically at build)
- Kage Purple as default theme
- Undo Last button + history tracking
- Auto-update check via `updater.py` (GitHub releases API, non-blocking)

## Safety
- Every value backed up before mutation
- Undo Last, Restore All, per-tweak toggle restore
- Non-Windows: silent no-op with warning

## Verified
- All 53 tweaks load, all 6 themes present, all 4 profiles valid
- History flow tested (record/drop/peek/pop/clear)
- Updater tested (silent when URL empty, semver compare correct)
- Icon generated cleanly at 512px multi-size .ico
- Lint: 0 errors across all modules

## Backlog
- Share profiles as .kage files (export/import)
- Set `RELEASES_URL` once repo is public
- Optional: signed EXE for SmartScreen trust
