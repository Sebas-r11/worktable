# FLEX-OP — Levantar con Docker

**Demo gratis en internet (Vercel + Render + SQLite):** ver [DEPLOY-DEMO.md](./DEPLOY-DEMO.md).

## Estructura del proyecto

```
ProyectoWorkT/
├── backend/              ← Django REST API  → puerto 8000
├── flexop-frontend/      ← Next.js frontend → puerto 3000
├── docker-compose.yml    ← desarrollo (PostgreSQL + runserver + next dev)
└── docker-compose.prod.yml ← producción (gunicorn + next start)
```

## Requisitos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (incluye `docker compose`)

## Desarrollo

```bash
docker compose up --build
```

Servicios:
- **PostgreSQL** (`db`) — datos persistentes en volumen `postgres_data`
- **Backend** — `runserver`, migraciones al arrancar; seed demo solo si la DB está vacía
- **Frontend** — `next dev` con hot reload

URLs:
- **Frontend:** http://localhost:3000
- **Backend / API:** http://localhost:8000/api
- **Swagger (solo DEBUG):** http://localhost:8000/swagger

### Usuarios de demo (tras `populate_db`)

| Usuario | Contraseña | Rol |
|---------|------------|-----|
| `admin` | `admin123` | ADMIN |
| `supervisor1` | `super123` | SUPERVISOR |
| `gerente1` | `gerente123` | GERENTE |
| `operario1` | `operario123` | OPERARIO |

## Producción

```bash
cp .env.example .env
# Editar SECRET_KEY, POSTGRES_PASSWORD, ALLOWED_HOSTS, etc.

docker compose -f docker-compose.prod.yml up --build -d
```

| Variable | Descripción |
|----------|-------------|
| `SECRET_KEY` | Obligatorio con `DEBUG=False` |
| `DATABASE_URL` | Conexión PostgreSQL |
| `RUN_POPULATE=1` | Carga datos demo solo en primer despliegue |
| `SERVE_MEDIA=1` | Sirve `/media/` desde Django (activo en `docker-compose.prod.yml`) |
| `ALLOWED_HOSTS` | Dominios permitidos (sin `*`) |

Imágenes de producción:
- `backend/Dockerfile.prod` — gunicorn + entrypoint con migraciones
- `flexop-frontend/Dockerfile.prod` — `next build` + `next start`

## Base de datos

| Entorno | Motor |
|---------|--------|
| Local sin Docker | SQLite (si no hay `DATABASE_URL`) |
| Docker dev/prod | PostgreSQL vía `DATABASE_URL` |
| CI (GitHub Actions) | PostgreSQL 16 |

## Detener

```bash
docker compose down
# Producción:
docker compose -f docker-compose.prod.yml down
```

## Recargar datos de prueba (desarrollo)

```bash
# Regenerar datos demo (borra operaciones/órdenes/alertas de la empresa demo)
docker compose exec backend env POPULATE_RESET=1 python populate_db.py
```

En el primer arranque con DB vacía, el entrypoint carga el seed automáticamente. Los reinicios **no** borran datos operativos.

## Notas

- Las imágenes subidas se conservan en el volumen `backend_media`.
- **Static** (`/static/`, admin CSS): WhiteNoise + `collectstatic` en el entrypoint.
- **Media** (`/media/`): `SERVE_MEDIA=1` en prod (o nginx delante en despliegues grandes).
- Swagger y ReDoc responden **404** cuando `DEBUG=False`.

## Error `ContainerConfig` o imagen no encontrada

```bash
docker compose down --remove-orphans
docker compose up --build -d
```

Usa **`docker compose`** (V2), no `docker-compose`.

## Error 500 en `POST /api/auth/login`

Suele ser la barra final en la URL. Reinicia el frontend tras cambios en proxy:

```bash
docker compose restart frontend
```

## Sin Docker

```bash
# Terminal 1 — backend (SQLite por defecto)
cd backend && .venv/bin/python manage.py migrate && .venv/bin/python manage.py runserver 8000

# Terminal 2 — frontend
cd flexop-frontend && npm run dev
```
