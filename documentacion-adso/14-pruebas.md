# Capítulo 14 — Pruebas

[← Índice](./README.md) | [← Anterior](./13-seguridad.md) | [Siguiente →](./15-resultados.md)

---

## Estrategia de pruebas (evidenciada en repositorio)

| Capa | Herramienta | Ubicación |
|------|-------------|-----------|
| Unitarias backend | pytest | `backend/**/tests/` |
| Integración API | pytest + APIClient | `test_api_*.py` |
| Unitarias frontend | Vitest | `flexop-frontend/src/**/*.test.*` |
| Integración UI | Vitest + MSW | Páginas con handlers mock |
| E2E | Playwright | `flexop-frontend/e2e/` |
| CI | GitHub Actions | `.github/workflows/backend-tests.yml` |

**Total aproximado:** ~139 tests pytest + ~76 Vitest + 12 escenarios E2E (según `PLAN_TESTING_FRONTEND.md`).

---

## Casos de prueba funcionales (muestra representativa)

| ID | Módulo | Caso | Resultado esperado | Archivo test |
|----|--------|------|-------------------|--------------|
| CP-F001 | Auth | Login usuario activo | 200 + tokens | `test_auth.py` |
| CP-F002 | Auth | Login usuario inactivo | 401 | `test_auth.py` |
| CP-F003 | Asignaciones | Listar como supervisor | 200 paginado | `test_api_asignaciones.py` |
| CP-F004 | Asignaciones | Iniciar pendiente | Estado ACTIVA | `test_api_asignaciones.py` |
| CP-F005 | Asignaciones | Finalizar activa | COMPLETADA + métrica | `test_api_metricas.py` |
| CP-F006 | Asignaciones | Eliminar activa | 400 | `test_api_asignaciones.py` |
| CP-F007 | Órdenes | Crear sin numero_orden | Auto-generado | `test_api.py` |
| CP-F008 | Órdenes | Ordenamiento prioridad | URGENTE primero | `test_ordering.py` |
| CP-F009 | Despacho | Flujo completar→despachar | Cola actualizada | `test_despacho.py` |
| CP-F010 | Alertas | Evaluar reglas idempotente | Sin duplicados | `test_evaluar_optimizado.py` |
| CP-F011 | Sugerencias | Aceptar crea asignación | Nueva Asignacion | `test_models.py` |
| CP-F012 | Reportes | Export CSV gerente | 200 text/csv | `test_exportar_y_generados.py` |
| CP-F013 | Reportes | Descargar reporte | FileResponse | `test_exportar_y_generados.py` |
| CP-F014 | Dashboard | Operario solo operario | 403 otros roles | `test_dashboards.py` |
| CP-F015 | Frontend login | Formulario válido | Redirect dashboard | `login.test.tsx` |
| CP-F016 | Frontend órdenes | Completar refresca cola | UI actualizada | `ordenes.test.tsx` |
| CP-F017 | Frontend paginación | Siguiente página métricas | page=2 en API | `metricas.test.tsx` |
| CP-F018 | E2E | Login 4 roles | URL correcta cada rol | `login-dashboard.spec.ts` |
| CP-F019 | E2E | Navegación sidebar | Todas rutas rol | `navigation-logout.spec.ts` |
| CP-F020 | Populate | Ejecutar dos veces sin reset | No borra datos | `test_populate_db.py` |

---

## Casos de prueba de validación

| ID | Caso | Regla validada | Evidencia |
|----|------|----------------|-----------|
| CP-V001 | Dos asignaciones activas mismo operario | `Asignacion.clean()` | `test_models.py` |
| CP-V002 | Operario sin habilidad para máquina | `puede_operar()` | `test_models.py` |
| CP-V003 | Login form campos vacíos | Zod min length | `login.test.tsx` |
| CP-V004 | Producción cantidad < 1 | Zod pipe min(1) | schema en `produccion/page.tsx` |
| CP-V005 | Incidencia título corto | Zod min 3 | `incidencias/page.tsx` |
| CP-V006 | Crear usuario contraseñas no coinciden | Zod refine | `usuarios/page.tsx` |
| CP-V007 | FK operario otra empresa en asignación | `validate_same_empresa` | `test_security_writes.py` |
| CP-V008 | Inyección empresa en PATCH usuario | Campo empresa ignorado | `test_security_writes.py` |
| CP-V009 | SECRET_KEY faltante en prod | ImproperlyConfigured | `test_settings_security.py` |
| CP-V010 | ALLOWED_HOSTS wildcard prod | ImproperlyConfigured | `test_settings_security.py` |

---

## Casos de prueba de seguridad

| ID | Caso | Resultado esperado | Archivo |
|----|------|-------------------|---------|
| CP-S001 | Operario accede dashboard gerente API | 403 | `test_dashboards.py` |
| CP-S002 | Operario lista usuarios otra empresa | Vacío / 404 | `test_multitenancy.py` |
| CP-S003 | Supervisor crea asignación cross-tenant | 400 | `test_multitenancy.py` |
| CP-S004 | Swagger en DEBUG=False | 404 | `test_urls_security.py` |
| CP-S005 | Media sin SERVE_MEDIA en prod | 404 | `test_static_media_prod.py` |
| CP-S006 | JWT refresh tras logout | Blacklist | `authStore.test.ts` |
| CP-S007 | Ruta /gerente como operario frontend | Redirect /operario | `routes.test.ts` |
| CP-S008 | Admin PATCH otro usuario empresa | Bloqueado | `test_api_usuarios.py` |
| CP-S009 | Cola despacho como supervisor | 403 | permisos ViewSet |
| CP-S010 | Export CSV como operario | 403 | `test_exportar_y_generados.py` |

---

## Cobertura y umbrales CI

| Proyecto | Umbral | Comando |
|----------|--------|---------|
| Backend | ≥30% apps dominio | `pytest --cov-fail-under=30` |
| Frontend | 70% statements/lines, 75% branches | `npm run test:coverage` |

## Archivos de test vacíos (deuda)

Los siguientes `tests.py` en raíz de apps contienen solo `# Create your tests here.`:

`usuarios`, `maquinas`, `operaciones`, `metricas`, `alertas`, `reasignaciones`, `ordenes`, `reportes`.

Las pruebas reales están en subcarpetas `tests/`.
