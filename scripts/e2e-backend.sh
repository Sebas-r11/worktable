#!/usr/bin/env bash
# Prepara DB y levanta Django para E2E (Playwright / local).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/backend"

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate

pip install -q -r requirements.txt
python manage.py migrate --noinput
python populate_db.py

PORT="${E2E_BACKEND_PORT:-8010}"
echo "[e2e] Backend listo en http://127.0.0.1:${PORT}"
exec python manage.py runserver "127.0.0.1:${PORT}" --noreload
