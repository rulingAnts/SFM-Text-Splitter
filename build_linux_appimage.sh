#!/usr/bin/env bash
set -euo pipefail

# Build a Linux AppImage for SFM Text Splitter using Docker (Ubuntu 20.04)
# Requirements on host: Docker installed and running (macOS supported).
# Usage:
#   ./build_linux_appimage.sh [ARCH]
# ARCH: linux architecture to target; default x86_64. Other values like aarch64 require an appropriate Docker image.

APP_NAME="SFMTextSplitter"
APP_DISPLAY_NAME="SFM Text Splitter"
ARCH="${1:-x86_64}"
UBUNTU_IMAGE="ubuntu:20.04"  # Older glibc for broader compatibility
WORKDIR_HOST="$(pwd)"
DIST_DIR_HOST="${WORKDIR_HOST}/dist/linux"

mkdir -p "${DIST_DIR_HOST}"

# Compose the build commands to run inside Docker (Linux)
read -r -d '' BUILD_CMDS <<'EOF'
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive

# Basic toolchain and Python
apt-get update
apt-get install -y --no-install-recommends \
  python3 python3-venv python3-pip python3-tk \
  build-essential wget xz-utils \
  patchelf desktop-file-utils ca-certificates git

# Create venv and install deps
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip wheel
if [ -f requirements.txt ]; then
  python -m pip install -r requirements.txt
fi
python -m pip install pyinstaller

# Ensure PyInstaller one-file CLI build (avoids spec nuances across OSes)
pyinstaller --onefile --noconsole --name "SFMTextSplitter" scripts/split_sfm.py

# Prepare AppDir structure
APPDIR="AppDir"
mkdir -p "$APPDIR/usr/bin"
mkdir -p "$APPDIR/usr/share/applications"

# Copy built binary
cp "dist/SFMTextSplitter" "$APPDIR/usr/bin/SFMTextSplitter"
chmod +x "$APPDIR/usr/bin/SFMTextSplitter"

# AppRun launcher
cat > "$APPDIR/AppRun" << 'ARUN'
#!/bin/sh
HERE="$(dirname "$0")"
exec "$HERE/usr/bin/SFMTextSplitter" "$@"
ARUN
chmod +x "$APPDIR/AppRun"

# Desktop entry
cat > "$APPDIR/SFMTextSplitter.desktop" << 'DESKTOP'
[Desktop Entry]
Type=Application
Name=SFM Text Splitter
Comment=Split SFM marker-based text files
Exec=SFMTextSplitter %F
Icon=SFMTextSplitter
Categories=Utility;
Terminal=false
DESKTOP

if [ -f assets/appicon.png ]; then
  cp assets/appicon.png "$APPDIR/SFMTextSplitter.png"
else
  echo "[!] assets/appicon.png not found; building AppImage without icon"
fi

# Fetch appimagetool and build AppImage
ARCH="${ARCH:-x86_64}"
APPIMAGE_TOOL_URL="https://github.com/AppImage/AppImageKit/releases/download/13/appimagetool-${ARCH}.AppImage"
wget -O appimagetool.AppImage "$APPIMAGE_TOOL_URL"
chmod +x appimagetool.AppImage

# Build
./appimagetool.AppImage "$APPDIR" "${APP_NAME}-${ARCH}.AppImage"

# Move artifacts to dist/linux
mkdir -p dist/linux
mv "${APP_NAME}-${ARCH}.AppImage" dist/linux/

# List output
ls -lh dist/linux
EOF

# Run the build inside Docker, mounting the repo
echo "[+] Starting Dockerized AppImage build for ${APP_DISPLAY_NAME} (${ARCH})"
docker run --rm \
  -e ARCH="${ARCH}" \
  -v "${WORKDIR_HOST}":/workspace \
  -w /workspace \
  "${UBUNTU_IMAGE}" \
  bash -lc "${BUILD_CMDS}"

echo "[+] Build complete. See dist/linux/${APP_NAME}-${ARCH}.AppImage"
