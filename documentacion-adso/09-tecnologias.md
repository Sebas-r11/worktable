# Capítulo 9 — Tecnologías utilizadas

[← Índice](./README.md) | [← Anterior](./08-arquitectura.md) | [Siguiente →](./10-modelo-datos.md)

---

## Backend (`backend/requirements.txt`)

| Tecnología | Versión declarada | Propósito | ¿Usado en código? |
|------------|------------------|-----------|-------------------|
| Python | 3.10+ (CI: 3.12) | Lenguaje runtime | ✅ |
| Django | >=4.2, <5.0 | Framework web ORM | ✅ |
| djangorestframework | >=3.14.0 | API REST | ✅ |
| djangorestframework-simplejwt | >=5.3.0 | Autenticación JWT | ✅ |
| psycopg2-binary | >=2.9.9 | Driver PostgreSQL | ✅ (vía engine) |
| dj-database-url | >=2.1.0 | Parse DATABASE_URL | ✅ |
| django-cors-headers | >=4.3.0 | CORS | ✅ |
| python-dotenv | >=1.0.0 | Variables .env | ✅ |
| drf-yasg | >=1.21.7 | Swagger/OpenAPI | ✅ (DEBUG) |
| Pillow | >=10.1.0 | Imágenes ImageField | ✅ (vía Django) |
| gunicorn | >=21.2.0 | Servidor WSGI prod | ✅ (Dockerfile.prod) |
| whitenoise | >=6.6.0 | Archivos estáticos prod | ✅ |
| pytest | >=7.4.3 | Framework de pruebas | ✅ |
| pytest-django | >=4.7.0 | Integración Django | ✅ |
| pytest-cov | >=4.1.0 | Cobertura | ✅ |
| celery | >=5.3.4 | Tareas async | ❌ Sin imports |
| redis | >=5.0.1 | Broker/cache | ❌ Sin imports |
| reportlab | >=4.0.7 | PDF | ❌ Sin imports |
| django-password-validators | >=1.7.1 | Validación contraseñas | ❌ No en settings |
| python-dateutil | >=2.8.2 | Fechas | ❌ Sin imports |
| django-debug-toolbar | >=4.2.0 | Debug UI | ❌ No en INSTALLED_APPS |
| django-extensions | >=3.2.3 | Utilidades Django | ❌ No en INSTALLED_APPS |
| flake8 / black | >=6 / >=23 | Calidad código | CLI only |

## Frontend (`flexop-frontend/package.json`)

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| Next.js | 16.2.4 | Framework React SSR/SSG |
| React | 19.2.4 | UI library |
| TypeScript | ^5 | Tipado estático |
| TanStack React Query | ^5.100.5 | Estado servidor async |
| Axios | ^1.15.2 | Cliente HTTP |
| Zustand | ^5.0.12 | Estado auth |
| react-hook-form | ^7.74.0 | Formularios |
| Zod | ^4.3.6 | Validación esquemas |
| Tailwind CSS | ^4 | Estilos utility-first |
| shadcn / radix-ui | ^4.5 / ^1.4 | Componentes UI |
| Recharts | ^3.8.1 | Gráficos dashboard gerente |
| js-cookie | ^3.0.5 | Cookies JWT |
| sonner | ^2.0.7 | Notificaciones toast |
| Vitest | ^3.2.4 | Tests unitarios |
| MSW | ^2.7.5 | Mock API en tests |
| Playwright | ^1.52.0 | Tests E2E |
| ESLint | ^9 | Linter |

## Infraestructura

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| PostgreSQL | 16 (Alpine en Docker) | BD producción/dev |
| Docker / Compose | — | Contenedorización |
| Node.js | 20 (Alpine en Docker) | Runtime frontend |
| GitHub Actions | — | CI/CD |
| SQLite | 3 | BD fallback local |

## Lo que NO está en el stack

| Elemento | Estado |
|----------|--------|
| Django Templates HTML | No existe |
| Django Forms (`forms.py`) | No existe |
| GraphQL | No implementado |
| WebSockets | No implementado |
| Kubernetes | No hay manifests |
| Nginx | No configurado (recomendado en docs para media a escala) |
