# Capítulo 16 — Conclusiones

[← Índice](./README.md) | [← Anterior](./15-resultados.md) | [Siguiente →](./17-recomendaciones.md)

---

1. **FLEX-OP es un sistema full-stack funcional** que cubre el ciclo operativo de planta —desde la asignación de personal hasta el despacho de órdenes— con evidencia en 22 modelos de datos, API REST extensa e interfaz web por roles.

2. **La arquitectura Cliente-Servidor con API REST** permitió desacoplar el backend Django del frontend Next.js, facilitando pruebas independientes (pytest, Vitest, Playwright) y despliegue en contenedores.

3. **El modelo multi-empresa está implementado de forma transversal** mediante mixins y validaciones de tenant, con pruebas automatizadas que confirman el aislamiento de datos.

4. **La seguridad se aborda en profundidad en el backend** (JWT, roles, permisos granulares, throttling), aunque el frontend depende de guardas cliente que deben complementarse con la API como única fuente de verdad.

5. **La calidad del software está respaldada por una suite de pruebas amplia** (~139 tests backend, decenas en frontend, E2E en CI), alineada con buenas prácticas ADSO de verificación.

6. **Existen dependencias y capacidades declaradas pero no integradas** (Celery, Redis, ReportLab, PDF), lo que indica espacio de evolución sin afectar el núcleo operativo actual.

7. **No existen formularios ni templates Django** — el proyecto adopta deliberadamente un frontend SPA moderno, coherente con tendencias actuales de desarrollo web.

8. **El sistema está listo para demostración académica** mediante `populate_db.py`, Docker Compose y credenciales documentadas, sin requerir configuración manual extensa en entorno de desarrollo.
