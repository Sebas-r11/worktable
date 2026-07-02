# Capítulo 7 — Análisis de requerimientos

[← Índice](./README.md) | [← Anterior](./06-metodologia.md) | [Siguiente →](./08-arquitectura.md)

---

> Requerimientos **extraídos de funcionalidades implementadas** en backend (`views.py`, `models.py`) y frontend (`src/app/`). No hay documento SRS previo en el repositorio.

## Requerimientos funcionales

### Autenticación y usuarios

| ID | Requerimiento | Evidencia |
|----|---------------|-----------|
| RF001 | El sistema debe permitir autenticación con usuario y contraseña devolviendo JWT | `POST /api/auth/login/` |
| RF002 | El sistema debe renovar tokens de acceso con refresh token | `POST /api/auth/refresh/` |
| RF003 | El sistema debe invalidar refresh token al cerrar sesión | `POST /api/auth/logout/` (blacklist) |
| RF004 | El sistema debe rechazar login de usuarios inactivos | `FlexTokenObtainPairView` |
| RF005 | El usuario autenticado debe consultar su perfil | `GET /api/usuarios/me/` |
| RF006 | El admin debe crear, editar y desactivar usuarios | `UserViewSet` + página admin/usuarios |
| RF007 | El admin debe restablecer contraseña de usuarios | `POST .../set_password/` |
| RF008 | El usuario debe cambiar su propia contraseña | `POST .../change_password/` |
| RF009 | El admin debe gestionar empresas | `EmpresaViewSet` (solo API, sin UI) |

### Máquinas

| ID | Requerimiento | Evidencia |
|----|---------------|-----------|
| RF010 | Gestionar tipos de máquina por empresa | `TipoMaquinaViewSet` |
| RF011 | Gestionar unidades de eficiencia por empresa | `UnidadEficienciaViewSet` |
| RF012 | Registrar máquinas con capacidad teórica y estado | `Maquina` model |
| RF013 | Listar máquinas disponibles u operando | acciones `disponibles`, `operando` |
| RF014 | Cambiar estado de máquina con historial | `cambiar_estado()` → `EstadoMaquina` |
| RF015 | Admin debe crear/editar/desactivar máquinas desde UI | `/admin/maquinas` |

### Operaciones

| ID | Requerimiento | Evidencia |
|----|---------------|-----------|
| RF016 | Gestionar turnos de trabajo | `TurnoViewSet` |
| RF017 | Gestionar habilidades y tipos de máquina asociados | `Habilidad` M2M |
| RF018 | Registrar operarios vinculados a usuario OPERARIO | `Operario` 1:1 User |
| RF019 | Verificar si operario puede operar una máquina | `Operario.puede_operar()` |
| RF020 | Crear asignaciones operario–máquina–turno | `AsignacionViewSet` + UI supervisor |
| RF021 | Iniciar asignación (PENDIENTE→ACTIVA) | `Asignacion.iniciar()` |
| RF022 | Finalizar asignación (ACTIVA→COMPLETADA) | `Asignacion.finalizar()` |
| RF023 | Pausar y reanudar asignación | acciones `pausar`, `reanudar` |
| RF024 | Impedir dos asignaciones activas en misma máquina u operario | `Asignacion.clean()` |
| RF025 | Eliminar solo asignaciones PENDIENTE o CANCELADA | `AsignacionViewSet.destroy()` |
| RF026 | Operario debe iniciar/finalizar su tarea desde dashboard | `/operario` |
| RF027 | Registrar eventos de asignación | `Evento` model |
| RF028 | Reportar incidencias con tipo, prioridad y máquina | `IncidenciaViewSet` + UI operario |
| RF029 | Resolver y escalar incidencias | acciones `resolver`, `escalar` |
| RF030 | Supervisor resuelve incidencias desde UI | `/supervisor/incidencias` |

### Producción y métricas

| ID | Requerimiento | Evidencia |
|----|---------------|-----------|
| RF031 | Registrar producción por asignación | `RegistroProduccionViewSet` |
| RF032 | Operario registra producción desde UI | `/operario/produccion` |
| RF033 | Calcular métrica de eficiencia por asignación | `MetricaEficiencia.calcular_para_asignacion()` |
| RF034 | Consultar métricas por operario, máquina y período | acciones en `MetricaEficienciaViewSet` |
| RF035 | Gestionar objetivos de producción | `ObjetivoProduccionViewSet` (API) |
| RF036 | Consultar cumplimiento de objetivo | `GET .../cumplimiento/` |
| RF037 | Gerente visualiza métricas y gráfico por máquina | `/gerente/metricas` |

### Alertas y notificaciones

| ID | Requerimiento | Evidencia |
|----|---------------|-----------|
| RF038 | Configurar reglas de alerta por empresa | `ReglaAlerta` |
| RF039 | Evaluar reglas automáticamente | `evaluar()`, `evaluar_todas` |
| RF040 | Gestionar alertas activas y resolverlas | `AlertaViewSet` |
| RF041 | Supervisor resuelve alertas individual o en lote | UI alertas + `resolverTodas` |
| RF042 | Notificar usuarios con campana de notificaciones | `Notificacion` + `NotificationBell` |
| RF043 | Marcar notificaciones como leídas | `marcar_leida`, `marcar_todas_leidas` |

### Reasignaciones

| ID | Requerimiento | Evidencia |
|----|---------------|-----------|
| RF044 | Generar sugerencias de reasignación | `POST /sugerencias/generar/` |
| RF045 | Listar sugerencias pendientes | `GET pendientes/` |
| RF046 | Aceptar sugerencia (crea nueva asignación) | `SugerenciaReasignacion.aceptar()` |
| RF047 | Rechazar sugerencia | `SugerenciaReasignacion.rechazar()` |
| RF048 | Supervisor gestiona sugerencias desde UI | `/supervisor/sugerencias` |

### Reportes y dashboards

| ID | Requerimiento | Evidencia |
|----|---------------|-----------|
| RF049 | Dashboard personalizado para operario | `DashboardOperarioView` |
| RF050 | Dashboard para supervisor | `DashboardSupervisorView` |
| RF051 | Dashboard gerencial con KPIs y gráficos | `DashboardGerenteView` + Recharts |
| RF052 | Exportar datos a CSV | `ExportarCSVView` |
| RF053 | Historial de reportes generados | `ReporteGeneradoViewSet` |
| RF054 | Descargar reporte de forma autenticada | `GET .../descargar/` |

### Órdenes de producción

| ID | Requerimiento | Evidencia |
|----|---------------|-----------|
| RF055 | Crear órdenes de producción con prioridad | `OrdenProduccionViewSet` |
| RF056 | Iniciar, registrar producción, completar y cancelar órdenes | acciones en ViewSet |
| RF057 | Generar número de orden automáticamente | `perform_create` en views |
| RF058 | Encolar orden al completar | `OrdenProduccion.completar()` |
| RF059 | Gestionar cola de despacho ordenada por prioridad | `ColaDespacho`, `ordering.py` |
| RF060 | Despachar ítem de cola (solo gerente+) | `ColaDespachoViewSet` + UI gerente |

### Administración operarios

| ID | Requerimiento | Evidencia |
|----|---------------|-----------|
| RF061 | Admin lista operarios con turno y habilidades | `/admin/operarios` |
| RF062 | Admin activa/desactiva operarios | `operarioUpdate` con campo `activo` |

## Requerimientos no funcionales

| ID | Requerimiento | Evidencia |
|----|---------------|-----------|
| RNF001 | Autenticación stateless con JWT | `SIMPLE_JWT` en settings |
| RNF002 | Rotación y blacklist de refresh tokens | `ROTATE_REFRESH_TOKENS`, `BLACKLIST_AFTER_ROTATION` |
| RNF003 | Paginación de listados API (20 ítems) | `PAGE_SIZE = 20` |
| RNF004 | Aislamiento de datos por empresa | `EmpresaFilterMixin`, tests multitenancy |
| RNF005 | Usuario inactivo no puede operar | `IsAuthenticatedFlex` |
| RNF006 | Throttle de login (10/min) | `LoginRateThrottle` |
| RNF007 | Throttle anónimo (100/día) | `DEFAULT_THROTTLE_RATES` |
| RNF008 | CORS configurable por entorno | settings DEBUG vs prod |
| RNF009 | SECRET_KEY obligatorio en producción | `ImproperlyConfigured` si falta |
| RNF010 | ALLOWED_HOSTS explícito en producción | sin wildcard |
| RNF011 | Swagger solo en desarrollo | `_debug_only` en urls |
| RNF012 | Archivos estáticos comprimidos en prod | WhiteNoise CompressedManifest |
| RNF013 | Media condicional en producción | `SERVE_MEDIA` env |
| RNF014 | Idioma español y zona America/Lima | settings i18n |
| RNF015 | Concurrencia segura en asignaciones | `select_for_update` en iniciar/finalizar |
| RNF016 | Operaciones atómicas en métricas | `calcular_para_asignacion` transaccional |
| RNF017 | Optimización N+1 en listados | querysets + `test_api_query_count` |
| RNF018 | Cobertura mínima backend CI 30% | workflow pytest --cov-fail-under=30 |
| RNF019 | Cobertura mínima frontend 70% statements | vitest.config thresholds |
| RNF020 | Tests E2E en pipeline CI | job e2e-test |
| RNF021 | Seed idempotente de base de datos | `test_populate_db.py` |
| RNF022 | Despliegue con migraciones automáticas | docker-entrypoint.sh |
| RNF023 | Interfaz responsive con Tailwind | clases utility en componentes |
| RNF024 | Validación de formularios cliente | Zod + react-hook-form |
| RNF025 | Polling para datos operativos (30–60 s) | useApi refetchInterval |

## Requerimientos NO implementados (explícito)

| ID propuesto | Descripción |
|--------------|-------------|
| — | Registro self-service de usuarios |
| — | Recuperación de contraseña por email |
| — | UI para empresas, reglas de alerta, objetivos |
| — | Generación real de PDF (reportlab sin uso) |
| — | Tareas programadas Celery |
| — | Autenticación de dos factores |
| — | Auditoría de cambios (django-simple-history no presente) |
