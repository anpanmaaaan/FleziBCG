#!/bin/bash

set -e

echo "=== Rebuilding Frontend (Vite) ==="

cd frontend

# Remove build artifacts
echo "→ Cleaning frontend build artifacts"
rm -rf dist .vite

# Ensure dependencies
if [ ! -d "node_modules" ]; then
  echo "→ Installing frontend dependencies"
  npm install
else
  echo "→ Dependencies already installed"
fi

# Build frontend
echo "→ Building frontend"
npm run build

echo "✅ Frontend rebuild completed"