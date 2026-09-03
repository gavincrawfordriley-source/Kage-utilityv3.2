@echo off
REM =====================================================
REM  FragBoost — one-click build script
REM  Run this on Windows to produce a single .exe you
REM  can send to a friend. No Python needed on their PC.
REM =====================================================

echo.
echo [1/3] Installing dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo.
echo [2/3] Cleaning old build...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist FragBoost.spec del FragBoost.spec

echo.
echo [3/3] Building FragBoost.exe...
python -m PyInstaller ^
  --noconfirm ^
  --onefile ^
  --windowed ^
  --name FragBoost ^
  --uac-admin ^
  --collect-all customtkinter ^
  main.py

echo.
echo =====================================================
echo   Done!  Your executable is at:  dist\FragBoost.exe
echo   Send that single file to your friend.
echo =====================================================
pause
