#!/usr/bin/env bash
set -euo pipefail

# start.sh - create venv if needed, install deps, and run ticker_server
ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$ROOT_DIR/venv"

if [ ! -d "$VENV_DIR" ]; then
  echo "Creating virtualenv..."
  python3 -m venv "$VENV_DIR"
fi

echo "Activating virtualenv..."
# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"

echo "Installing dependencies..."
pip install -r "$ROOT_DIR/requirements.txt"

echo "Starting ticker_server on port ${PORT:-5000}..."
PORT=${PORT:-5000}
export PORT
python "$ROOT_DIR/ticker_server.py"
