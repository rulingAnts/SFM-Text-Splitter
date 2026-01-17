@echo off
setlocal
rem Change to repo root
cd /d "%~dp0"

echo [+] Ensuring pip and runtime deps...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

where pyinstaller >nul 2>&1
if errorlevel 1 (
  echo [i] PyInstaller not found; installing globally...
  python -m pip install pyinstaller
)

if not exist assets\appicon.ico (
  echo [!] Missing assets\appicon.ico. Please add the icon and retry.
  exit /b 1
)

echo [+] Building with PyInstaller (windowed, onefile)...
python -m PyInstaller --clean --noconfirm sfm_text_splitter.spec

if exist "dist\SFM Text Splitter.exe" (
  echo [*] Build complete: dist\SFM Text Splitter.exe
) else (
  echo [!] Build failed; see PyInstaller output above.
)
endlocal
