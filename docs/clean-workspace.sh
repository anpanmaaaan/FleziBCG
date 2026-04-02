#!/usr/bin/env bash
set -e

echo "=== Cleaning workspace (MES project) ==="

rm -rf frontend/dist frontend/.vite
rm -f dev.db *.db *.sqlite *.sqlite3
rm -rf tmp .temp .cache

echo "✅ Workspace cleaned."