@echo off
REM =====================================================
REM  Kage Utility — one-click build script
REM =====================================================

echo.
echo [1/4] Installing dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo.
echo [2/4] Generating custom app icon, background, and audio...
python generate_icon.py
python generate_bg.py
python -c "from sound import ensure_sfx; ensure_sfx()"
python -c "from voice import ensure_voice; ensure_voice()"
if not exist voice.wav copy /Y whoosh.wav voice.wav >nul
if not exist voice.wav (
  echo WARNING: voice.wav could not be generated. Aborting build.
  pause
  exit /b 1
)

echo.
echo [3/4] Cleaning old build...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist KageUtility.spec del KageUtility.spec

echo.
echo [4/4] Building KageUtility.exe...
python -m PyInstaller ^
  --noconfirm ^
  --onefile ^
  --windowed ^
  --name KageUtility ^
  --icon=icon.ico ^
  --uac-admin ^
  --add-data "icon.ico;." ^
  --add-data "icon.png;." ^
  --add-data "splash_source.png;." ^
  --add-data "bg.png;." ^
  --add-data "whoosh.wav;." ^
  --add-data "voice.wav;." ^
  --add-data "kage_max_performance.nip;." ^
  --collect-all customtkinter ^
  --hidden-import pystray._win32 ^
  --hidden-import pypresence ^
  --hidden-import psutil ^
  --hidden-import wmi ^
  main.py

if not exist dist\KageUtility.exe (
  echo.
  echo =====================================================
  echo   BUILD FAILED. Scroll up to see the PyInstaller error.
  echo =====================================================
  pause
  exit /b 1
)

echo.
echo =====================================================
echo   Done!  Your executable is at:  dist\KageUtility.exe
echo =====================================================
pause
