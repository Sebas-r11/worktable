# Capítulo 2 — Estructura del repositorio

[← Índice](./README.md) | [← Anterior](./01-resumen-ejecutivo.md) | [Siguiente: Arquitectura →](./03-arquitectura.md)

---

```
ProyectoWorkT/
├── backend/                    # API Django REST
│   ├── flexop/                 # Proyecto Django (settings, urls, wsgi)
│   ├── usuarios/               # Usuarios, empresas, auth JWT
│   ├── maquinas/               # Tipos, máquinas, unidades de eficiencia
│   ├── operaciones/            # Turnos, operarios, asignaciones, incidencias
│   ├── metricas/               # Producción, eficiencia, objetivos
│   ├── alertas/                # Reglas, alertas, notificaciones
│   ├── reasignaciones/         # Sugerencias inteligentes
│   ├── reportes/               # Dashboards y exportación CSV
│   ├── ordenes/                # Órdenes de producción y cola de despacho
│   ├── tests/                  # Tests transversales (multitenancy, seguridad)
│   ├── populate_db.py          # Seed de datos demo (idempotente)
│   ├── docker-entrypoint.sh    # migrate + collectstatic + populate
│   ├── Dockerfile              # Desarrollo (runserver)
│   ├── Dockerfile.prod         # Producción (gunicorn)
│   ├── requirements.txt
│   └── manage.py
├── flexop-frontend/            # SPA Next.js App Router
│   ├── src/app/                # Rutas (auth + dashboard por rol)
│   ├── src/components/         # UI compartida (shadcn + custom)
│   ├── src/hooks/              # React Query hooks
│   ├── src/lib/                # API client, auth, utilidades
│   ├── src/stores/             # Zustand (auth)
│   ├── src/test/msw/           # Mocks para Vitest
│   ├── e2e/                    # Playwright
│   ├── Dockerfile / Dockerfile.prod
│   └── vitest.config.ts
├── documentacion/              # Documentación ADSO por capítulos
├── docker-compose.yml          # Desarrollo
├── docker-compose.prod.yml     # Producción
├── docker-compose.hub.yml      # Imágenes publicadas en Docker Hub
├── .github/workflows/          # CI: backend, frontend, e2e
├── scripts/                    # e2e-backend.sh, e2e-frontend.sh
├── README-DOCKER.md
├── FUNCIONES_POR_ROL.md        # Detalle funcional por rol
└── DOCUMENTACION_ADSO.md       # Índice principal (apunta a documentacion/)
```
