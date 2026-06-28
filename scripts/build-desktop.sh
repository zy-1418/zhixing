#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP_DIR="$ROOT_DIR/apps/mobile"

if ! command -v flutter >/dev/null 2>&1; then
  echo "Flutter SDK not found. Desktop build is blocked in this environment."
  echo "See docs/BLOCKERS.md for the placeholder workflow."
  exit 0
fi

cd "$APP_DIR"
flutter config --enable-windows-desktop --enable-macos-desktop --enable-linux-desktop
flutter build linux
