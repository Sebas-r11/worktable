# Capítulo 11 — Módulos del sistema

[← Índice](./README.md) | [← Anterior](./10-modelo-datos.md) | [Siguiente →](./12-casos-uso.md)

---

## Módulo 1 — Usuarios y autenticación

| Aspecto | Detalle |
|---------|---------|
| **Nombre** | `usuarios` |
| **Objetivo** | Gestionar identidad, roles, empresas y autenticación JWT |
| **Funcionalidades** | Login/logout/refresh; CRUD usuarios; CRUD empresas; perfil `me`; cambio de contraseña |
| **Usuarios** | Todos (auth); ADMIN (gestión usuarios/empresas) |
| **Archivos clave** | `models.py`, `views.py`, `views_auth.py`, `permissions.py`, `mixins.py` |

## Módulo 2 — Máquinas

| Aspecto | Detalle |
|---------|---------|
| **Nombre** | `maquinas` |
| **Objetivo** | Catálogo de equipos, tipos y unidades de medida |
| **Funcionalidades** | CRUD tipos/unidades/máquinas; listar disponibles/operando; cambiar estado con historial |
| **Usuarios** | SUPERVISOR+ (escritura); ADMIN (UI máquinas) |
| **Archivos clave** | `models.py`, `views.py` |

## Módulo 3 — Operaciones

| Aspecto | Detalle |
|---------|---------|
| **Nombre** | `operaciones` |
| **Objetivo** | Coordinar trabajo diario: turnos, operarios, asignaciones, incidencias |
| **Funcionalidades** | CRUD turnos/habilidades/operarios/asignaciones; iniciar/pausar/finalizar; incidencias resolver/escalar |
| **Usuarios** | OPERARIO (ejecución); SUPERVISOR (coordinación); ADMIN (operarios list) |
| **Archivos clave** | `models.py`, `views.py`, `querysets.py` |

## Módulo 4 — Métricas y producción

| Aspecto | Detalle |
|---------|---------|
| **Nombre** | `metricas` |
| **Objetivo** | Registrar producción y calcular eficiencia |
| **Funcionalidades** | CRUD producción; calcular métricas; objetivos y cumplimiento (API) |
| **Usuarios** | OPERARIO (registro); GERENTE (consulta); SUPERVISOR+ (objetivos API) |
| **Archivos clave** | `models.py`, `efficiency.py`, `views.py`, `querysets.py` |

## Módulo 5 — Alertas y notificaciones

| Aspecto | Detalle |
|---------|---------|
| **Nombre** | `alertas` |
| **Objetivo** | Detectar desviaciones y notificar usuarios |
| **Funcionalidades** | Reglas evaluables; alertas activas; resolver/escalar; notificaciones leídas |
| **Usuarios** | SUPERVISOR (gestión alertas); todos (notificaciones propias) |
| **Archivos clave** | `models.py`, `views.py`, `querysets.py` |

## Módulo 6 — Reasignaciones

| Aspecto | Detalle |
|---------|---------|
| **Nombre** | `reasignaciones` |
| **Objetivo** | Sugerir y aplicar reasignaciones operario–máquina |
| **Funcionalidades** | Generar sugerencias; aceptar (crea asignación); rechazar; historial |
| **Usuarios** | SUPERVISOR |
| **Archivos clave** | `models.py`, `views.py` |

## Módulo 7 — Reportes y dashboards

| Aspecto | Detalle |
|---------|---------|
| **Nombre** | `reportes` |
| **Objetivo** | Consolidar KPIs y exportar información |
| **Funcionalidades** | Dashboard operario/supervisor/gerente; CSV; historial reportes; descarga segura |
| **Usuarios** | OPERARIO, SUPERVISOR, GERENTE (según dashboard) |
| **Archivos clave** | `views.py`, `models.py` |

## Módulo 8 — Órdenes de producción

| Aspecto | Detalle |
|---------|---------|
| **Nombre** | `ordenes` |
| **Objetivo** | Planificar producción y gestionar despacho |
| **Funcionalidades** | CRUD órdenes; ciclo iniciar/completar; cola despacho; reordenar |
| **Usuarios** | GERENTE (órdenes y despacho); SUPERVISOR+ (órdenes API write) |
| **Archivos clave** | `models.py`, `views.py`, `ordering.py` |

## Módulo 9 — Cliente web (frontend)

| Aspecto | Detalle |
|---------|---------|
| **Nombre** | `flexop-frontend` |
| **Objetivo** | Interfaz de usuario por rol consumiendo la API |
| **Funcionalidades** | Login; 17 páginas dashboard; formularios; gráficos; paginación |
| **Usuarios** | OPERARIO, SUPERVISOR, GERENTE, ADMIN |
| **Archivos clave** | `src/app/`, `src/hooks/useApi.ts`, `src/lib/api/` |

## Módulos auxiliares (no funcionales de negocio)

| Módulo | Propósito |
|--------|-----------|
| `backend/tests/` | Multitenancy, seguridad escritura, populate |
| `backend/flexop/` | Settings, URLs raíz, tests seguridad |
| `scripts/e2e-*.sh` | Arranque para Playwright |
| `.github/workflows/` | CI automatizado |
| `backend/reciclables/` | Documentación legacy (no app activa) |
