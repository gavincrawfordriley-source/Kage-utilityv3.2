@echo off
REM =====================================================
REM  Kage Utility — one-click build script
REM =====================================================

echo.
echo [1/4] Installing dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo.
echo [2/4] Generating custom app icon...
python generate_icon.py

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
  --collect-all customtkinter ^
  --hidden-import pystray._win32 ^
  --hidden-import pypresence ^
  main.py

echo.
echo =====================================================
echo   Done!  Your executable is at:  dist\KageUtility.exe
echo =====================================================
pause
