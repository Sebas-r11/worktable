# Plan de testing — FLEX-OP Backend

**Proyecto:** Django 4.2 + DRF + SimpleJWT  
**Estado actual:** **69 tests**, bugs B-01–B-07 resueltos  
**Última actualización:** 2026-05-28

---

## Resumen

| Métrica | Valor |
|---------|--------|
| Tests | **69 passed** |
| Cobertura (apps críticas) | ~80% |
| CI | `.github/workflows/backend-tests.yml` (umbral 30%) |

```bash
cd backend && .venv/bin/pytest -v
```

---

## Fases — todas completadas ✅

### Fase 0 — Infraestructura ✅
`pytest.ini`, `conftest.py`, fixtures por rol, CI

### Fase 1 — Tests unitarios ✅
| App | Archivos |
|-----|----------|
| operaciones | `test_models.py` |
| usuarios | `test_models.py` |
| metricas | `test_models.py` |
| ordenes | `test_models.py`, `test_despacho.py` |
| maquinas | `test_models.py` |
| alertas | `test_models.py`, `test_objetivo_dedup.py` |
| reasignaciones | `test_models.py` |

### Fase 2 — API / integración ✅
| App | Archivos |
|-----|----------|
| operaciones | `test_api_asignaciones.py`, `test_api_metricas.py` |
| ordenes | `test_api.py` |
| reasignaciones | `test_api.py` |
| reportes | `test_dashboards.py` |
| global | `tests/test_multitenancy.py` |

### Fase 3 — Correcciones de código ✅
Ver tabla «Bugs resueltos» abajo.

### Fase 4 — CI ✅
GitHub Actions + `--cov-fail-under=30`

---

## Bugs resueltos (B-01 – B-07)

| ID | Descripción | Solución |
|----|-------------|----------|
| B-01 | Alertas de objetivo duplicadas por día | FK `objetivo_relacionado` + filtro en `_evaluar_objetivo_no_alcanzado` |
| B-02 | `posicion_cola.get()` fallaba con múltiples filas | `.filter(EN_COLA).order_by(...).first()` |
| B-03 | `aceptar()` sin validar asignación | `Asignacion()` + `save()` → `full_clean()` |
| B-04 | `fecha_ingreso` DateField con `auto_now_add` | `default=date.today` + migración |
| B-05 | Dashboards sin permiso por rol | `IsOperario`, `IsSupervisorOrAbove`, `IsGerenteOrAbove` |
| B-06 | `escalar` incidencia sin notificar | `Incidencia.escalar()` + notificaciones a gerentes |
| B-07 | Deprecation Swagger | `SWAGGER_USE_COMPAT_RENDERERS = False` |

### Otros fixes previos
- Multitenancy (`EmpresaFilterMixin`)
- Registro usuarios solo admin
- Órdenes alineadas al modelo
- Métricas: horas mínimas + tope eficiencia
- JWT `token_blacklist`
- `Asignacion.save()` → `full_clean()`

---

## Bugs pendientes / mejoras futuras

| ID | Prioridad | Descripción |
|----|-----------|-------------|
| B-09 | ~~Baja~~ | ~~Tests de `ExportarCSVView` y `ReporteGeneradoViewSet`~~ ✅ `reportes/tests/test_exportar_y_generados.py` |
| B-10 | Baja | Admin también puede ver dashboard gerente (definir si es deseado) |
| B-11 | Info | Subir `--cov-fail-under` a 50% |
| B-12 | ~~Info~~ | ~~Tests E2E con frontend~~ ✅ Playwright en `flexop-frontend/e2e/` |

---

## Estructura de tests

```
backend/
├── conftest.py
├── operaciones/tests/
├── usuarios/tests/
├── metricas/tests/
├── ordenes/tests/
├── maquinas/tests/
├── alertas/tests/
├── reasignaciones/tests/
├── reportes/tests/
└── tests/test_multitenancy.py
```

---

## Migraciones añadidas

- `alertas/migrations/0003_fix_bugs.py` — `objetivo_relacionado`
- `usuarios/migrations/0002_fix_bugs.py` — `fecha_ingreso`

---

## Registro de progreso

| Fecha | Entregable |
|-------|------------|
| 2026-05-28 AM | 24 tests iniciales |
| 2026-05-28 PM | 53 tests + fixes P0 |
| 2026-05-28 noche | **69 tests** + reasignaciones/reportes + **bugs B-01–B-07** |
| 2026-05-28 | **78 tests** + B-09 exportar CSV y reportes generados |
