#!/usr/bin/env bash
set -e

echo "=== Cleaning workspace (MES project) ==="

# Clean build artifacts
rm -rf frontend/dist frontend/.vite

# Clean cache and temp files
rm -rf tmp .temp .cache

# Note: PostgreSQL data is in Docker volume (postgres_data) managed by docker compose
# To fully reset: docker compose -f docker/docker-compose.dev.yml down -v

echo "✅ Workspace cleaned."