#!/usr/bin/env bash

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="$PROJECT_ROOT/FilmOnDemandAPPUI/filmondemand-app"
VENV_DIR="$PROJECT_ROOT/.venv"
BACKEND_PID=""

cleanup() {
    if [ -n "${BACKEND_PID:-}" ] && kill -0 "$BACKEND_PID" 2>/dev/null; then
        echo
        echo "Stopping FastAPI backend..."
        kill "$BACKEND_PID" 2>/dev/null || true
        wait "$BACKEND_PID" 2>/dev/null || true
    fi
}

trap cleanup EXIT INT TERM

require_command() {
    local command_name="$1"
    local install_hint="$2"

    if ! command -v "$command_name" >/dev/null 2>&1; then
        echo "ERROR: '$command_name' is not installed."
        echo "$install_hint"
        exit 1
    fi
}

echo "==============================================="
echo " FilmOnDemand - Starting Servers"
echo "==============================================="

require_command "python3" "Install Python 3, then make sure 'python3' is available in your PATH."
require_command "npm" "Install Node.js from https://nodejs.org or via Homebrew, then try again."

echo
echo "[1/4] Preparing Python virtual environment..."
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
fi

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

echo
echo "[2/4] Installing Python backend dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install -r "$PROJECT_ROOT/requirements.txt"

echo
echo "[3/4] Starting FastAPI backend on port 8000..."
cd "$PROJECT_ROOT"
python3 -m uvicorn server.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

echo "Waiting 3 seconds for backend to start..."
sleep 3

echo
echo "[4/4] Starting React frontend..."
cd "$FRONTEND_DIR"

if [ ! -d "node_modules" ]; then
    echo "Installing UI dependencies..."
    if [ -f "package-lock.json" ]; then
        npm ci
    else
        npm install
    fi
fi

npm run dev
