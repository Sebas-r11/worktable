# Capítulo 1 — Resumen ejecutivo

[← Índice](./README.md) | [Siguiente: Estructura del repositorio →](./02-estructura-repositorio.md)

---

FLEX-OP es un sistema web para coordinar la operación en planta: asignación de operarios a máquinas, registro de producción, incidencias, alertas automáticas, sugerencias de reasignación, métricas de eficiencia, órdenes de producción y cola de despacho. Incluye cuatro roles de usuario con interfaces diferenciadas y un modelo multi-empresa (tenant) donde cada registro operativo pertenece a una `Empresa`.

| Capa | Tecnología | Puerto (dev) |
|------|------------|--------------|
| Frontend | Next.js 16, React 19, TypeScript, Tailwind 4 | 3000 |
| Backend | Django 4.2, Django REST Framework, SimpleJWT | 8000 |
| Base de datos | PostgreSQL 16 (Docker/CI); SQLite (local sin `DATABASE_URL`) | 5432 |
| Contenedores | Docker Compose (dev y prod) | — |
