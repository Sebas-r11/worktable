# Capítulo 5 — Alcance del proyecto

[← Índice](./README.md) | [← Anterior](./04-objetivos.md) | [Siguiente →](./06-metodologia.md)

---

## Alcance funcional (implementado en código)

| Módulo | Incluido | No incluido / parcial |
|--------|----------|------------------------|
| Autenticación JWT | Login, refresh, logout, verify, me | Registro público de usuarios |
| Usuarios y empresas | CRUD usuarios (admin), CRUD empresas (admin) | UI de empresas en frontend |
| Máquinas | CRUD tipos, unidades, máquinas; cambio de estado | UI productos (`/productos/` en API sin página) |
| Operaciones | Turnos, habilidades, operarios, asignaciones, eventos, incidencias | Crear operario/turno desde frontend admin |
| Producción y métricas | Registro, cálculo eficiencia, objetivos (API) | UI objetivos de producción |
| Alertas | Reglas, alertas, notificaciones | UI reglas de alerta |
| Reasignaciones | Generar, listar, aceptar, rechazar sugerencias | — |
| Reportes | Dashboards 3 roles, CSV, historial, descarga | PDF/Excel real (modelo tiene formato PDF; export usa CSV) |
| Órdenes | CRUD órdenes, cola despacho, despachar | — |
| Admin Django | `/admin/` | No documentado como módulo usuario final |

## Alcance técnico

| Elemento | Estado |
|--------|--------|
| API REST JSON | ✅ Implementada |
| Frontend SPA (Next.js) | ✅ Implementado |
| Base de datos relacional | ✅ PostgreSQL / SQLite |
| Autenticación stateless JWT | ✅ |
| Multi-tenant por empresa | ✅ |
| Paginación API (20 ítems) | ✅ |
| Paginación UI (`PaginationBar`) | ✅ En listados principales |
| Docker desarrollo | ✅ |
| Docker producción (gunicorn + next start) | ✅ |
| CI GitHub Actions | ✅ |
| WhiteNoise estáticos | ✅ |
| Celery / Redis tareas async | ❌ En `requirements.txt` pero **sin uso en código** |
| Reportes PDF (reportlab) | ❌ Dependencia sin imports |
| Django templates HTML | ❌ **No existen** (`forms.py` tampoco) |
| Django forms | ❌ **No existen** |
| Autenticación server-side Next.js middleware | ❌ Middleware solo proxy `/api/*` |
| httpOnly cookies | ❌ Tokens en cookies accesibles por JS |

## Limitaciones

| Limitación | Detalle |
|------------|---------|
| Empresa demo única en seed | `populate_db.py` crea una empresa ACME |
| Dashboard operario objetivo fijo | `DashboardOperarioView` usa `objetivo_dia = 1000` hardcodeado |
| Endpoint `por_turno` documentado pero ausente | Docstring en `MetricaEficienciaViewSet` sin `@action` |
| Reportes generados sin archivo en seed | `descargar` retorna 404 si `archivo` vacío |
| Protección de rutas frontend solo cliente | Usuario autenticado puede intentar URLs directas (API sí valida permisos) |
| Menú Perfil sin funcionalidad | `TopBar` ítem "Perfil" sin handler |
| Badge pendientes sugerencias | Cuenta solo página actual del listado |
| `django-password-validators` | En requirements, no configurado en settings |
| Swagger solo en DEBUG | Producción no expone documentación interactiva |
