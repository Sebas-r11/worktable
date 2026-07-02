#!/bin/sh
set -e

python manage.py migrate --noinput
python manage.py collectstatic --noinput

if [ "${POPULATE_RESET:-0}" = "1" ]; then
  POPULATE_RESET=1 python populate_db.py
elif [ "${RUN_POPULATE:-1}" = "1" ]; then
  python populate_db.py
fi

exec "$@"
