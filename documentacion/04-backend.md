# Capítulo 4 — Inventario backend (Django)

[← Índice](./README.md) | [← Anterior](./03-arquitectura.md) | [Siguiente: Frontend →](./05-frontend.md)

---

## Aplicaciones Django

| App | Responsabilidad |
|-----|-----------------|
| `usuarios` | Modelo `User` custom, `Empresa`, login JWT, CRUD usuarios |
| `maquinas` | Catálogo de máquinas, tipos, unidades de eficiencia, historial de estados |
| `operaciones` | Turnos, habilidades, operarios, asignaciones, eventos, incidencias |
| `metricas` | Registros de producción, métricas de eficiencia, objetivos |
| `alertas` | Reglas configurables, alertas activas, notificaciones por usuario |
| `reasignaciones` | Sugerencias de reasignación operario↔máquina |
| `reportes` | Dashboards por rol, exportación CSV, reportes generados |
| `ordenes` | Órdenes de producción y cola de despacho |

## Modelos de dominio (20 modelos)

### usuarios

| Modelo | Campos clave | Relaciones |
|--------|--------------|------------|
| `Empresa` | nombre, ruc (único), activa, logo | 1→N usuarios |
| `User` | rol, activo, telefono, foto_perfil | FK → Empresa; extiende AbstractUser |

### maquinas

| Modelo | Campos clave | Relaciones |
|--------|--------------|------------|
| `TipoMaquina` | nombre, descripcion | FK → Empresa |
| `UnidadEficiencia` | nombre, abreviatura | FK → Empresa |
| `Maquina` | codigo, capacidad_teorica, estado_actual, activa | FK → TipoMaquina, UnidadEficiencia, Empresa |
| `EstadoMaquina` | estado, fecha_hora | FK → Maquina, User (historial) |

### operaciones

| Modelo | Campos clave | Relaciones |
|--------|--------------|------------|
| `Turno` | nombre, hora_inicio, hora_fin | FK → Empresa |
| `Habilidad` | nombre | FK → Empresa; M2M TipoMaquina, Operario |
| `Operario` | codigo_empleado, disponible, eficiencia_promedio | 1:1 User; FK Turno; M2M Habilidad |
| `Asignacion` | fecha, estado (PENDIENTE/ACTIVA/COMPLETADA/CANCELADA) | FK Operario, Maquina, Turno, User |
| `Evento` | tipo (INICIO/FIN/PAUSA/REANUDACION/…) | FK Asignacion, User |
| `Incidencia` | tipo, prioridad, estado, titulo | FK Asignacion, Maquina, User |

### metricas

| Modelo | Campos clave | Relaciones |
|--------|--------------|------------|
| `RegistroProduccion` | cantidad, fecha_hora | FK Asignacion, User |
| `MetricaEficiencia` | produccion_real, eficiencia_calculada | FK Operario, Maquina, Asignacion (único) |
| `ObjetivoProduccion` | tipo, cantidad_objetivo, activo | FK Maquina/Turno/Operario según tipo |

### alertas

| Modelo | Campos clave | Relaciones |
|--------|--------------|------------|
| `ReglaAlerta` | tipo, umbral, prioridad, activa | FK Empresa |
| `Alerta` | titulo, prioridad, estado | FK ReglaAlerta, Operario, Maquina, Incidencia, Empresa |
| `Notificacion` | titulo, mensaje, leida | FK User, Alerta |

### reasignaciones

| Modelo | Campos clave | Relaciones |
|--------|--------------|------------|
| `SugerenciaReasignacion` | razon, impacto_estimado, estado | FK Operario, Maquina origen/destino, Asignacion |

### reportes

| Modelo | Campos clave | Relaciones |
|--------|--------------|------------|
| `ReporteGenerado` | tipo, formato, archivo, parametros (JSON) | FK Empresa, User |

### ordenes

| Modelo | Campos clave | Relaciones |
|--------|--------------|------------|
| `OrdenProduccion` | numero_orden, cantidad_requerida, estado, prioridad | FK Maquina, Empresa, User |
| `ColaDespacho` | estado, posicion_manual, fecha_entrada | FK OrdenProduccion, Empresa |

## Lógica de negocio destacada

| Archivo | Función |
|---------|---------|
| `ordenes/ordering.py` | Ordenamiento unificado por prioridad (URGENTE → BAJA) |
| `metricas/efficiency.py` | Horas efectivas restando intervalos PAUSA/REANUDACION |
| `operaciones/models.py` | `iniciar()`/`finalizar()` con `select_for_update`, exclusividad máquina |
| `operaciones/querysets.py` | Optimización N+1 en asignaciones, operarios, incidencias |
| `metricas/querysets.py` | Querysets optimizados para métricas y producción |
| `alertas/querysets.py` | Prefetch para evaluación de reglas |
| `alertas/models.py` | `evaluar()` idempotente con `get_or_create` |
| `ordenes/models.py` | Cola de despacho automática al completar orden |
| `reasignaciones/models.py` | `generar_sugerencias()`, `aceptar()`, `rechazar()` |
| `usuarios/mixins.py` | Filtrado y creación scoped por empresa |
| `populate_db.py` | Seed idempotente; `POPULATE_RESET=1` para regenerar |

## API REST — Endpoints

Prefijo global: `/api/`. Los ViewSets exponen CRUD estándar (`GET/POST` lista, `GET/PUT/PATCH/DELETE` detalle).

### Autenticación (`flexop/urls.py`)

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/auth/login/` | Obtener access + refresh JWT |
| POST | `/api/auth/logout/` | Blacklist refresh token |
| POST | `/api/auth/refresh/` | Renovar access token |
| POST | `/api/auth/verify/` | Verificar token |

### usuarios

| Recurso | Acciones custom |
|---------|-----------------|
| `/api/usuarios/` | `GET me/`, `GET operarios/`, `GET supervisores/`, `POST {id}/change_password/`, `POST {id}/set_password/` |
| `/api/empresas/` | CRUD (admin) |

### maquinas

| Recurso | Acciones custom |
|---------|-----------------|
| `/api/tipos-maquina/` | CRUD |
| `/api/maquinas/` | `GET disponibles/`, `GET operando/`, `POST {id}/cambiar_estado/` |
| `/api/unidades-eficiencia/` | CRUD |

### operaciones

| Recurso | Acciones custom |
|---------|-----------------|
| `/api/turnos/` | `GET activos/` |
| `/api/habilidades/` | `GET {id}/operarios/` |
| `/api/operarios/` | `GET disponibles/`, `GET ranking/`, `GET {id}/asignaciones/` |
| `/api/asignaciones/` | `GET activas/`, `GET del_dia/`; `POST {id}/iniciar/`, `finalizar/`, `pausar/`, `reanudar/` |
| `/api/incidencias/` | `GET abiertas/`, `GET estadisticas/`; `POST {id}/resolver/`, `escalar/` |
| `/api/eventos/` | CRUD |

### metricas

| Recurso | Acciones custom |
|---------|-----------------|
| `/api/produccion/` | `GET por_asignacion/`, `por_maquina/`, `resumen_dia/` |
| `/api/metricas/` | `GET por_operario/`, `por_maquina/`, `ranking_operarios/`; `POST calcular/` |
| `/api/objetivos/` | `GET activos/`; `GET {id}/cumplimiento/` |

### alertas

| Recurso | Acciones custom |
|---------|-----------------|
| `/api/reglas-alerta/` | `GET activas/`; `POST {id}/evaluar/`, `evaluar_todas/` |
| `/api/alertas/` | `GET activas/`, `por_prioridad/`, `estadisticas/`; `POST {id}/resolver/`, `escalar/` |
| `/api/notificaciones/` | `GET no_leidas/`; `POST {id}/marcar_leida/`, `marcar_todas_leidas/` |

### reasignaciones

| Recurso | Acciones custom |
|---------|-----------------|
| `/api/sugerencias/` | `GET pendientes/`, `estadisticas/`; `POST {id}/aceptar/`, `rechazar/`; `POST generar/` |

### reportes

| Método | Ruta | Descripción |
|--------|------|-------------|
| CRUD | `/api/reportes-generados/` | Historial de reportes |
| GET | `/api/reportes-generados/{id}/descargar/` | Descarga autenticada (gerente+) |
| GET | `/api/dashboard/operario/` | Dashboard operario |
| GET | `/api/dashboard/supervisor/` | Dashboard supervisor |
| GET | `/api/dashboard/gerente/` | Dashboard gerente |
| GET | `/api/exportar-csv/` | Exportación CSV |

### ordenes

| Recurso | Acciones custom |
|---------|-----------------|
| `/api/ordenes/` | `POST {id}/iniciar/`, `registrar_produccion/`, `completar/`, `cancelar/`; `GET pendientes/`, `en_progreso/` |
| `/api/cola-despacho/` | `GET pendientes/` (array sin paginar); `POST {id}/despachar/`; `POST reordenar/` |

### Documentación (solo `DEBUG=True`)

| Ruta | Descripción |
|------|-------------|
| `/swagger/` | Swagger UI |
| `/redoc/` | ReDoc |
| `/swagger.json` | Esquema OpenAPI |

### Otros

| Ruta | Descripción |
|------|-------------|
| `/admin/` | Panel Django Admin |
| `/media/{path}` | Archivos subidos (solo `DEBUG` o `SERVE_MEDIA=True`) |
| `/static/` | Archivos estáticos vía WhiteNoise (producción) |

## Configuración (`flexop/settings.py`)

| Área | Valor / comportamiento |
|------|------------------------|
| `AUTH_USER_MODEL` | `usuarios.User` |
| Paginación | 20 ítems/página |
| JWT access | 60 min (env `JWT_ACCESS_TOKEN_LIFETIME`) |
| JWT refresh | 1440 min (env `JWT_REFRESH_TOKEN_LIFETIME`) |
| Idioma / zona | `es-es`, `America/Lima` |
| CORS | Todo permitido en DEBUG; lista explícita en prod |
| Prod guards | `SECRET_KEY` y `ALLOWED_HOSTS` obligatorios si `DEBUG=False` |
| Static | WhiteNoise `CompressedManifestStaticFilesStorage` |
| Throttle login | 10 intentos/minuto |

## Dependencias Python principales

Django 4.2, DRF, SimpleJWT, psycopg2, dj-database-url, django-cors-headers, drf-yasg, Pillow, gunicorn, whitenoise, pytest, pytest-django, pytest-cov.

## Tests backend

- **~139 tests** en **31 archivos** (pytest).
- Cobertura CI: mínimo 30% en apps de dominio.
- Áreas: modelos, API, multitenancy, seguridad de escritura, dashboards, populate idempotente, static/media prod, URLs en producción.
