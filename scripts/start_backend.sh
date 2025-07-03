#!/usr/bin/env bash
# Start backend Flask server, ensuring port 5001 is free.
# Usage: ./scripts/start_backend.sh

set -euo pipefail

PORT=${FLASK_PORT:-5001}
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Activate venv
source .venv/bin/activate

# Kill any process already listening on $PORT
if lsof -ti tcp:"$PORT" > /dev/null; then
  echo "[start_backend] Port $PORT busy – terminating existing process..."
  lsof -ti tcp:"$PORT" | xargs kill -9 || true
fi

# Run backend (CTRL+C to stop)
exec python backend/app.py 