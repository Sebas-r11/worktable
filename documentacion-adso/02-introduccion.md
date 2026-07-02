# Capítulo 2 — Introducción

[← Índice](./README.md) | [← Anterior](./01-resumen-ejecutivo.md) | [Siguiente →](./03-planteamiento-problema.md)

---

## Presentación del proyecto

FLEX-OP es un **sistema de información web** orientado a la operación de planta industrial. El nombre del proyecto Django es `flexop` y la aplicación cliente se denomina `flexop-frontend`.

Componentes identificados en el repositorio:

| Componente | Ruta | Descripción |
|------------|------|-------------|
| API REST | `backend/` | Lógica de negocio, persistencia, autenticación JWT |
| Cliente web | `flexop-frontend/` | Interfaz por rol, consumo de API vía Axios |
| Orquestación | `docker-compose.yml`, `docker-compose.prod.yml` | Servicios db, backend, frontend |
| CI | `.github/workflows/backend-tests.yml` | Tests backend, frontend y E2E |
| Datos demo | `backend/populate_db.py` | Empresa ACME y usuarios de prueba |

## Justificación

> **⚠️ No existe en el repositorio** un documento de justificación académica u organizacional (acta, carta de la empresa, etc.).

**Lo que sí evidencia el código:**

1. **Complejidad operativa modelada:** 22 modelos de dominio, 18 ViewSets/APIViews, más de 40 acciones custom en la API.
2. **Separación de responsabilidades por rol:** cuatro perfiles con permisos distintos en backend (`usuarios/permissions.py`) y frontend (`lib/auth/routes.ts`).
3. **Necesidad de integración:** frontend desacoplado del backend vía REST + JWT, patrón habitual en arquitecturas modernas.
4. **Calidad verificable:** ~139 tests pytest, suite Vitest con MSW, E2E Playwright en CI.

## Importancia para la organización

> **⚠️ No hay datos de una organización real** en el código. La empresa demo es ficticia: **ACME Industries** (RUC `20123456789` en `populate_db.py`).

**Capacidades que una organización obtendría al desplegar el sistema** (según funcionalidades implementadas):

- Centralizar asignaciones operario–máquina–turno.
- Automatizar alertas por reglas configurables.
- Consolidar KPIs gerenciales sin hojas de cálculo manuales.
- Auditar eventos de asignación (`Evento`) e historial de estados de máquina (`EstadoMaquina`).
