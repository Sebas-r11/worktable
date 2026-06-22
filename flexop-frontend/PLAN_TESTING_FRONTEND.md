# Plan de testing — FLEX-OP Frontend

**Stack:** Next.js 16 + React 19 + Zustand + TanStack Query + Vitest + MSW  
**Estado:** 76 tests Vitest + 12 E2E Playwright

---

## Comandos

```bash
cd flexop-frontend
npm install
npm test              # Vitest (unitario/integración)
npm run test:watch
npm run test:coverage
npm run test:e2e:install   # navegador Chromium (primera vez)
npm run test:e2e           # E2E Playwright (levanta API :8010 y Next :3010)
npm run test:e2e:ui        # modo interactivo
```

E2E usa `scripts/e2e-backend.sh` (API :8010) y `scripts/e2e-frontend.sh` (`next build` + `next start` en :3010). No comparte el lock de `next dev` con el servidor en :3000.

---

## Cobertura actual

| Área | Tests | Tipo |
|------|-------|------|
| `lib/utils`, `lib/display/entities` | Helpers | Unitario |
| `lib/auth/routes`, `lib/auth/nav` | Rutas y menú por rol | Unitario |
| `lib/ui/statusVariants` | Variantes badge | Unitario |
| `lib/api/client`, `lib/api/reportes` | Tokens + rutas API | Unitario |
| `stores/authStore` | login/logout/loadUser | Integración |
| `hooks/useApi` | órdenes, alertas, métricas, sugerencias, dashboard | Integración |
| `StatusBadge`, `EmptyState`, `NotificationBell` | UI | Componente |
| `Sidebar`, `TopBar` | Layout | Componente |
| `login/page` | Formulario + validación | Integración |
| `supervisor/alertas`, `supervisor/sugerencias` | Páginas supervisor | Integración |
| `gerente/metricas`, `gerente/reportes` | Páginas gerente | Integración |
| `admin/usuarios`, `admin/maquinas` | Páginas admin | Integración |
| `operario/page`, `operario/produccion`, `operario/incidencias` | Páginas operario | Integración |
| `e2e/login-dashboard.spec.ts` | Login → dashboard (4 roles) | E2E Playwright |
| `e2e/navigation-logout.spec.ts` | Navegación sidebar + logout | E2E Playwright |
| `test/msw/flows.test.tsx` | Dashboard supervisor (3 endpoints paralelos) | MSW integración |

**Utilidad:** `src/test/test-utils.tsx`, `src/test/msw/` (handlers + fixtures), `e2e/fixtures/users.ts`

### MSW (P2)

Handlers en `src/test/msw/handlers.ts` interceptan `apiClient` (axios) sin `vi.mock('@/lib/api')`.
Los tests de páginas y hooks usan red simulada coherente; `server.use()` permite escenarios puntuales.

---

## Cobertura (P4)

`npm run test:coverage` aplica umbrales en `vitest.config.ts` (áreas: `lib`, `stores`, `hooks`, `components/shared`):

| Métrica | Umbral |
|---------|--------|
| statements / lines | 70% |
| branches | 75% |
| functions | 50% |

CI: job `frontend-test` ejecuta `npm run test:coverage` tras `npm test`.

## Pendiente (siguiente iteración)

| Prioridad | Área |
|-----------|------|
| — | Plan frontend Vitest/E2E base completado |

---

## Bugs frontend — corregidos

| ID | Fix |
|----|-----|
| F-01 | Tipos y UI de máquinas: `estado_actual`, `capacidad_teorica`, `unidad_capacidad`, `activa`; formulario admin alineado al API |
| F-02 | `Alerta`: `titulo`, `descripcion`, `fecha_creacion`, estados `ESCALADA`/`DESCARTADA` |
| F-03 | `SugerenciaReasignacion`: `operario`, `maquina_destino_*`, `razon_display`, `fecha_creacion` |
| F-04 | `sugerenciaRechazar` envía `{ notas }` requerido por el backend |
| F-05 | Métricas: `eficiencia_calculada`, `produccion_teorica`; producción: `fecha_hora`; reportes: `fecha_generacion` |
| F-06 | `exportarCSV` usaba ruta incorrecta (`/reportes/exportar-csv/` → `/exportar-csv/`) y sin query params |
| F-07 | Métricas: API devuelve decimales como string; `.toFixed()` rompía la página en producción/E2E |

Helpers: `src/lib/display/entities.ts`

---

## Registro

| Fecha | Entregable |
|-------|------------|
| 2026-05-28 | Vitest + ~30 tests iniciales |
| 2026-05-28 | Fixes F-01–F-05 + tests display helpers |
| 2026-05-28 | **60 tests** Vitest + fix F-06 export CSV |
| 2026-05-28 | **6 tests E2E** Playwright + CI job `e2e-test`; fix dashboard gerente (Decimal) |
| 2026-05-28 | **P2 MSW**: handlers compartidos, flujos multi-endpoint, tests sin mocks manuales de API |
| 2026-05-28 | Fix interceptor 401 en `/auth/login`; axios `fetch` adapter para MSW en Vitest |
| 2026-05-28 | **P3**: 13 tests admin (usuarios, máquinas) + operario (dashboard, producción, incidencias); **75 tests** Vitest |
| 2026-05-28 | **P4**: cobertura Vitest con umbrales + CI; **P5**: 6 E2E navegación/logout (**12 E2E** total) |
| 2026-05-28 | Fix métricas: `Decimal` API como string + E2E `next start` vía `scripts/e2e-frontend.sh`; **76 Vitest**, **12 E2E** OK |
