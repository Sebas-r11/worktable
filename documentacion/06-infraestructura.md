# Capítulo 6 — Infraestructura y despliegue

[← Índice](./README.md) | [← Anterior](./05-frontend.md) | [Siguiente: Roles y permisos →](./07-roles-permisos.md)

---

## Docker Compose — desarrollo

```bash
docker compose up --build
```

| Servicio | Imagen / build | Puerto |
|----------|----------------|--------|
| `db` | postgres:16-alpine | interno |
| `backend` | `backend/Dockerfile` | 8000 |
| `frontend` | `flexop-frontend/Dockerfile` | 3000 |

Entrypoint backend: `migrate` → `collectstatic` → `populate_db` (si DB vacía) → `runserver`.

## Docker Compose — producción

```bash
cp .env.example .env
docker compose -f docker-compose.prod.yml up --build -d
```

| Servicio | Cambio vs dev |
|----------|---------------|
| `backend` | `Dockerfile.prod` + gunicorn (3 workers) |
| `frontend` | `Dockerfile.prod` + `next build` + `next start` |
| Env | `DEBUG=False`, `RUN_POPULATE=0`, `SERVE_MEDIA=1` |

## Variables de entorno relevantes

| Variable | Descripción |
|----------|-------------|
| `SECRET_KEY` | Obligatorio en producción |
| `DATABASE_URL` | PostgreSQL |
| `ALLOWED_HOSTS` | Sin wildcard en prod |
| `CORS_ALLOWED_ORIGINS` | Orígenes del frontend |
| `RUN_POPULATE` | `1` carga demo si DB vacía |
| `POPULATE_RESET` | `1` borra datos operativos y re-seed |
| `SERVE_MEDIA` | `1` expone `/media/` desde Django |
| `NEXT_PUBLIC_API_URL` | URL pública API (prod: `/api`) |
| `BACKEND_INTERNAL_URL` | Proxy interno Next → Django |

## CI/CD (GitHub Actions)

Workflow: `.github/workflows/backend-tests.yml`

| Job | Contenido |
|-----|-----------|
| `backend-test` | Python 3.12, PostgreSQL 16, pytest + coverage ≥30% |
| `frontend-test` | Node 20, `npm test`, `npm run test:coverage` |
| `e2e-test` | migrate + populate + Playwright (depende de los anteriores) |
