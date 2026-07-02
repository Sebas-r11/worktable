# Capítulo 1 — Resumen ejecutivo

[← Índice](./README.md) | [Siguiente →](./02-introduccion.md)

---

## Descripción general del sistema

**FLEX-OP** (Flexible Operations Platform) es una aplicación web para la gestión operativa de planta de producción. Consta de:

- **Backend:** API REST en Django 4.2 con 8 aplicaciones de dominio (`usuarios`, `maquinas`, `operaciones`, `metricas`, `alertas`, `reasignaciones`, `reportes`, `ordenes`).
- **Frontend:** SPA en Next.js 16 con interfaces diferenciadas por rol.
- **Persistencia:** PostgreSQL en Docker/CI; SQLite como fallback local sin `DATABASE_URL`.
- **Despliegue:** Docker Compose (desarrollo y producción), CI en GitHub Actions.

El sistema implementa un modelo **multi-empresa (multi-tenant)**: cada usuario pertenece a una `Empresa` y los datos operativos se filtran por tenant.

## Problema que resuelve (evidenciado por el dominio implementado)

Según las entidades y flujos presentes en el código, el sistema aborda:

| Problema operativo | Evidencia en código |
|--------------------|---------------------|
| Coordinar operarios y máquinas | Modelo `Asignacion`, estados PENDIENTE→ACTIVA→COMPLETADA |
| Registrar producción en piso | `RegistroProduccion`, página `/operario/produccion` |
| Gestionar incidencias | `Incidencia` con prioridad, escalamiento y resolución |
| Detectar desviaciones automáticamente | `ReglaAlerta.evaluar()`, `Alerta`, `Notificacion` |
| Optimizar asignaciones | `SugerenciaReasignacion.generar_sugerencias()` |
| Medir eficiencia | `MetricaEficiencia.calcular_para_asignacion()`, dashboards gerente |
| Planificar y despachar órdenes | `OrdenProduccion`, `ColaDespacho` |
| Administrar usuarios y catálogos | CRUD en módulo admin del frontend + ViewSets |

> **Nota:** No existe en el repositorio un documento formal de diagnóstico organizacional. La tabla anterior se infiere **únicamente** del dominio modelado e implementado.

## Usuarios objetivo (definidos en código)

Rol definido en `usuarios.models.User.RolChoices` y usado en permisos y rutas del frontend:

| Rol | Código | Interfaz principal |
|-----|--------|-------------------|
| Operario | `OPERARIO` | `/operario/*` |
| Supervisor | `SUPERVISOR` | `/supervisor/*` |
| Gerente | `GERENTE` | `/gerente/*` |
| Administrador | `ADMIN` | `/admin/*` (+ acceso a rutas de otros roles) |

## Beneficios (derivados de funcionalidades implementadas)

| Beneficio | Soporte en el sistema |
|-----------|----------------------|
| Trazabilidad de producción | Registros con asignación, usuario y timestamp |
| Visibilidad en tiempo casi real | Polling 30–60 s en dashboards y alertas |
| Decisiones basadas en datos | Dashboards gerente, métricas, exportación CSV |
| Respuesta a incidentes | Alertas, incidencias, notificaciones |
| Seguridad por roles | Permisos DRF + guardas de ruta en frontend |
| Aislamiento por empresa | `EmpresaFilterMixin`, validación de tenant |
| Despliegue reproducible | Docker, migraciones, seed idempotente |
