# Capítulo 5 — Inventario frontend (Next.js)

[← Índice](./README.md) | [← Anterior](./04-backend.md) | [Siguiente: Infraestructura →](./06-infraestructura.md)

---

## Stack

| Categoría | Paquetes |
|-----------|----------|
| Framework | Next.js 16.2.4, React 19.2.4, TypeScript 5 |
| Datos | TanStack React Query 5, Axios |
| Estado | Zustand (auth persistido) |
| Formularios | react-hook-form, Zod |
| UI | shadcn/radix-ui, Tailwind 4, lucide-react, sonner, recharts |
| Tests unitarios | Vitest 3, Testing Library, MSW 2 |
| E2E | Playwright 1.52 |

## Rutas por rol

### OPERARIO (`/operario`)

| Ruta | Página | Funciones |
|------|--------|-----------|
| `/operario` | Dashboard | KPIs, asignación activa, iniciar/finalizar tarea |
| `/operario/produccion` | Producción | Registrar producción, historial paginado |
| `/operario/incidencias` | Incidencias | Reportar y listar incidencias |

### SUPERVISOR (`/supervisor`)

| Ruta | Página | Funciones |
|------|--------|-----------|
| `/supervisor` | Dashboard | Máquinas, alertas, sugerencias resumidas |
| `/supervisor/alertas` | Alertas | Listar, resolver individual/lote |
| `/supervisor/sugerencias` | Reasignaciones | Aceptar/rechazar sugerencias (paginado) |
| `/supervisor/asignaciones` | Asignaciones | CRUD asignaciones, iniciar/finalizar |
| `/supervisor/incidencias` | Incidencias | Resolver incidencias abiertas |

### GERENTE (`/gerente`)

| Ruta | Página | Funciones |
|------|--------|-----------|
| `/gerente` | Dashboard | KPIs, gráficos Recharts |
| `/gerente/reportes` | Reportes | Historial, exportar CSV, descarga segura |
| `/gerente/metricas` | Métricas | Tabla + gráfico eficiencia por máquina |
| `/gerente/ordenes` | Órdenes | CRUD órdenes, cola de despacho |

### ADMIN (`/admin`)

| Ruta | Página | Funciones |
|------|--------|-----------|
| `/admin/usuarios` | Usuarios | CRUD, roles, contraseñas |
| `/admin/maquinas` | Máquinas | CRUD máquinas, tipos, unidades |
| `/admin/operarios` | Operarios | Listado, activar/desactivar |

**Landing por rol:** `/` redirige según `user.rol` → `/operario`, `/supervisor`, `/gerente` o `/admin/usuarios`.

## Capa API frontend

| Módulo | Archivo | Contenido |
|--------|---------|-----------|
| Cliente HTTP | `src/lib/api/client.ts` | Axios + JWT + refresh automático |
| Usuarios/Auth | `src/lib/api/usuarios.ts` | login, logout, me, CRUD usuarios |
| Operaciones | `src/lib/api/operaciones.ts` | turnos, operarios, asignaciones, incidencias |
| Máquinas | `src/lib/api/maquinas.ts` | tipos, unidades, máquinas |
| Barrel | `src/lib/api/index.ts` | metricas, alertas, reasignaciones, ordenes, reportes |
| Hooks | `src/hooks/useApi.ts` | React Query hooks por dominio |
| Auth rutas | `src/lib/auth/routes.ts` | `canAccessPath`, `getDashboardRoute` |
| Nav | `src/lib/auth/nav.ts` | Items de sidebar por rol |
| Descargas | `src/lib/download.ts` | Blob download para reportes |

## Componentes compartidos

| Componente | Ubicación | Uso |
|------------|-----------|-----|
| `PaginationBar` | `components/shared/` | Paginación en listados |
| `NotificationBell` | `components/shared/` | Campana de notificaciones |
| `StatusBadge` | `components/shared/` | Estados con color semántico |
| `EmptyState` | `components/shared/` | Listas vacías |
| `DataFetchAlert` | `components/shared/` | Error de carga con reintento |
| `PageLoader` | `components/shared/` | Spinner de página |
| `Sidebar` / `TopBar` | `components/layout/` | Shell del dashboard |
| UI shadcn | `components/ui/` | button, card, table, dialog, select, etc. |

## Autenticación frontend

1. Login en `/login` → `authStore.login()` → tokens en cookies.
2. `loadUser()` consulta `/api/usuarios/me/`.
3. Layout dashboard valida sesión y rol (`canAccessPath`).
4. Middleware Next.js **solo** reescribe `/api/*` hacia Django (`BACKEND_INTERNAL_URL`); no hace auth de páginas.
5. Logout blacklistea refresh y limpia cookies.

## Tests frontend

| Tipo | Herramienta | Alcance |
|------|-------------|---------|
| Unitarios/integración | Vitest + MSW | ~22 archivos de test en `src/` |
| Cobertura mínima | v8 | 70% statements/lines, 75% branches |
| E2E | Playwright | login por rol, navegación, logout |
| Scripts E2E | `scripts/e2e-*.sh` | Backend :8010, Frontend :3010 |
