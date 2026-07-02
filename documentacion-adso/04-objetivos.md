# Capítulo 4 — Objetivos

[← Índice](./README.md) | [← Anterior](./03-planteamiento-problema.md) | [Siguiente →](./05-alcance.md)

---

> **Aviso:** No existe un archivo de objetivos del proyecto de grado en el repositorio. Los objetivos siguientes se **formulan a partir de las capacidades implementadas y verificadas** en código y pruebas.

## Objetivo general

Desarrollar e implementar una **plataforma web multi-rol y multi-empresa** que permita gestionar la operación de planta de producción —asignaciones, producción, incidencias, alertas, métricas, órdenes y reportes— mediante una API REST segura y una interfaz web moderna, desplegable con contenedores Docker.

*Evidencia de cumplimiento:* 8 apps Django, 17 rutas de frontend, docker-compose dev/prod, CI con 3 jobs de prueba.

## Objetivos específicos

| ID | Objetivo específico | Evidencia en el proyecto |
|----|---------------------|--------------------------|
| OE1 | Modelar el dominio operativo de planta | 22 modelos en 8 apps; 15 archivos de migración |
| OE2 | Exponer operaciones vía API REST documentable | ViewSets + Swagger (solo DEBUG); `ENDPOINTS.md` por app |
| OE3 | Autenticar usuarios con JWT y roles | `FlexTokenObtainPairView`, `User.RolChoices`, blacklist |
| OE4 | Aislar datos por empresa (tenant) | `EmpresaFilterMixin`, tests `test_multitenancy.py` |
| OE5 | Proveer interfaz por rol (operario, supervisor, gerente, admin) | 4 secciones en `src/app/(dashboard)/` |
| OE6 | Calcular eficiencia descontando pausas | `metricas/efficiency.py`, `MetricaEficiencia` |
| OE7 | Automatizar alertas por reglas | `ReglaAlerta.evaluar()`, 4 tipos de regla |
| OE8 | Sugerir reasignaciones inteligentes | `SugerenciaReasignacion.generar_sugerencias()` |
| OE9 | Gestionar órdenes y cola de despacho | `OrdenProduccion`, `ColaDespacho`, tests despacho |
| OE10 | Exportar y descargar reportes de forma segura | `ExportarCSVView`, `descargar` con `IsGerenteOrAbove` |
| OE11 | Garantizar calidad con pruebas automatizadas | pytest (~139), Vitest, Playwright E2E en CI |
| OE12 | Facilitar despliegue reproducible | Dockerfiles, entrypoint, `README-DOCKER.md` |
