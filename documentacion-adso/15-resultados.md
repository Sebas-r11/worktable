# Capítulo 15 — Resultados obtenidos

[← Índice](./README.md) | [← Anterior](./14-pruebas.md) | [Siguiente →](./16-conclusiones.md)

---

## Funcionalidades implementadas

| Área | Estado | Evidencia |
|------|--------|-----------|
| API REST multi-módulo | ✅ Completo | 8 apps, 18 ViewSets |
| Autenticación JWT | ✅ Completo | Login, refresh, logout, blacklist |
| Multi-empresa | ✅ Completo | Mixins + 3 tests dedicados |
| UI por 4 roles | ✅ Completo | 17 páginas Next.js |
| Asignaciones con ciclo de vida | ✅ Completo | iniciar/finalizar/pausar + validaciones |
| Producción e incidencias | ✅ Completo | Páginas operario + API |
| Alertas y notificaciones | ✅ Completo | Reglas, evaluación, campana UI |
| Sugerencias reasignación | ✅ Completo | Generar, aceptar, rechazar |
| Dashboards analíticos | ✅ Completo | 3 dashboards + Recharts |
| Reportes CSV | ✅ Completo | Export + historial |
| Órdenes y cola despacho | ✅ Completo | Priorización + despacho |
| Admin usuarios/máquinas | ✅ Completo | CRUD UI |
| Paginación | ✅ Completo | API 20 + PaginationBar UI |
| Docker dev/prod | ✅ Completo | Compose + Dockerfiles |
| CI 3 jobs | ✅ Completo | backend, frontend, e2e |
| Seed demo | ✅ Completo | populate idempotente |

## Funcionalidades parciales o solo API

| Funcionalidad | Estado |
|---------------|--------|
| Gestión empresas | Solo API |
| Reglas de alerta | Solo API |
| Objetivos producción | Solo API |
| Productos máquina | Endpoint `/productos/` sin UI |
| Crear operario/turno | API existe; UI admin operarios solo toggle activo |
| Reportes PDF | Modelo soporta formato PDF; export real es CSV |
| Perfil usuario | Menú sin implementar |

## Métricas del proyecto (desde código)

| Métrica | Valor |
|---------|-------|
| Modelos Django | 22 |
| Migraciones | 15 archivos |
| Tests pytest | ~139 |
| Tests Vitest | ~76+ |
| Specs E2E | 2 archivos, 4 roles |
| Páginas frontend | 17 |
| Hooks React Query | 18+ |
| Requerimientos funcionales documentados | RF001–RF062 |

## Beneficios alcanzados (verificables)

| Beneficio | Cómo se verifica |
|-----------|------------------|
| Automatización operativa | Flujos asignación→producción→métrica en tests |
| Trazabilidad | Modelos Evento, EstadoMaquina, timestamps |
| Seguridad por capas | 10+ casos prueba seguridad |
| Despliegue repetible | Docker + entrypoint + CI verde esperado |
| Mantenibilidad | Separación apps, querysets, tipos TypeScript |

> **Nota:** No hay métricas de despliegue en producción real ni encuestas de usuarios en el repositorio.
