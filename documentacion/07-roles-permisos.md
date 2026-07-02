# Capítulo 7 — Roles, módulos y permisos

[← Índice](./README.md) | [← Anterior](./06-infraestructura.md) | [Siguiente: Datos demo →](./08-datos-demostracion.md)

---

| Rol | Módulos UI | Nivel API típico |
|-----|------------|------------------|
| **OPERARIO** | Dashboard, Producción, Incidencias | Lectura propia; escritura producción/incidencias |
| **SUPERVISOR** | + Alertas, Sugerencias, Asignaciones | Coordinación operativa, resolver alertas/incidencias |
| **GERENTE** | + Reportes, Métricas, Órdenes | KPIs, exportación, gestión de órdenes y despacho |
| **ADMIN** | Usuarios, Máquinas, Operarios | CRUD catálogos y usuarios (puede acceder rutas inferiores) |

Funciones detalladas por pantalla: ver [`FUNCIONES_POR_ROL.md`](../FUNCIONES_POR_ROL.md).
