#!/usr/bin/env bash
set -o errexit

echo "==> Instalando dependencias Python..."
pip install -r requirements.txt

echo "==> Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

echo "==> Build completado."
