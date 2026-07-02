#!/bin/sh
set -e

echo "==> Migraciones (SQLite)..."
python manage.py migrate --noinput

echo "==> Cargando datos demo (POPULATE_SCALE=${POPULATE_SCALE:-demo})..."
export POPULATE_SCALE="${POPULATE_SCALE:-demo}"
if [ "${POPULATE_RESET:-0}" = "1" ]; then
  POPULATE_RESET=1 python populate_db.py
else
  python populate_db.py
fi

echo "==> Arrancando Gunicorn (1 worker, SQLite)..."
exec gunicorn flexop.wsgi:application \
  --bind "0.0.0.0:${PORT:-8000}" \
  --workers 1 \
  --threads 2 \
  --timeout 180 \
  --access-logfile - \
  --error-logfile -
