#!/usr/bin/env bash
# Build (si hace falta) y sirve Next en modo producción para E2E (sin lock de next dev).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/flexop-frontend"

PORT="${PLAYWRIGHT_FRONTEND_PORT:-3010}"
HOST="${PLAYWRIGHT_FRONTEND_HOST:-127.0.0.1}"
BACKEND="${PLAYWRIGHT_BACKEND_URL:-http://127.0.0.1:8010}"
export NEXT_PUBLIC_API_URL="${BACKEND}/api"

if [ "${CI:-}" = "true" ] || [ ! -f ".next/BUILD_ID" ]; then
  echo "[e2e] Building frontend..."
  npm run build
fi

echo "[e2e] Frontend listo en http://${HOST}:${PORT}"
exec npx next start --hostname "$HOST" --port "$PORT"
