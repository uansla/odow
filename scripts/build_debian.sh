#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
PYTHON=/home/software/.venv-3.13/bin/python
if [[ ! -x "$PYTHON" ]]; then echo "Missing Python: $PYTHON" >&2; exit 1; fi
export PATH="/home/software/.venv-3.13/bin:$PATH"
for tool in ffmpeg deno; do
  if ! command -v "$tool" >/dev/null 2>&1; then echo "Missing runtime: $tool" >&2; exit 1; fi
done
cd "$ROOT"
"$PYTHON" -m PyInstaller --noconfirm --clean --windowed --onedir --name Odow --specpath build --paths src --exclude-module pytest --exclude-module numpy --exclude-module PIL --exclude-module PySide6.QtWebEngineCore --exclude-module PySide6.QtWebEngineWidgets --exclude-module PySide6.QtPdf --exclude-module PySide6.QtPdfWidgets --collect-all yt_dlp --collect-all yt_dlp_ejs --add-binary "$(command -v deno):." src/odow/app.py
echo "Build ready: $ROOT/dist/Odow"
