#!/usr/bin/env bash
# Reseed the PH6-STATION demo dataset and immediately verify the seed
# contract (claimable PLANNED op + IN_PROGRESS op present).
#
# Usage (from workspace root):
#   ./backend/scripts/seed_station.sh
#
# Exit code: 0 on success, non-zero if reseed or verification fails.

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
VENV_PYTHON="$REPO_ROOT/.venv/bin/python"

if [ ! -x "$VENV_PYTHON" ]; then
  echo "❌ Python venv not found at $VENV_PYTHON"
  echo "   Run: cd $REPO_ROOT && python -m venv .venv && .venv/bin/pip install -r backend/requirements.txt"
  exit 1
fi

echo "=== PH6-STATION reseed + verify ==="
cd "$REPO_ROOT/backend"
PYTHONPATH="$REPO_ROOT/backend" "$VENV_PYTHON" -m scripts.seed.seed_station_execution_opr
