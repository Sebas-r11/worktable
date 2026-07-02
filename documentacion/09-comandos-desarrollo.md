# Capítulo 9 — Comandos de desarrollo

[← Índice](./README.md) | [← Anterior](./08-datos-demostracion.md) | [Siguiente: Flujo operativo →](./10-flujo-operativo.md)

---

## Backend (local)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python populate_db.py
python manage.py runserver
pytest -q
```

## Frontend (local)

```bash
cd flexop-frontend
npm install
npm run dev          # http://localhost:3000
npm test -- --run    # Vitest
npm run test:e2e     # Playwright
```

## Docker

```bash
docker compose up --build          # desarrollo
docker compose down                # detener
docker compose -f docker-compose.prod.yml up --build -d   # producción
```
