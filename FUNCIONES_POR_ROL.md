# Funciones Por Rol En FLEX-OP

Este documento resume las funciones actualmente implementadas en el sistema por cada rol de usuario, tomando como referencia las pantallas activas del frontend y las operaciones disponibles en backend.

## Resumen General

| Rol | Objetivo principal | Módulos visibles |
| --- | --- | --- |
| Operario | Ejecutar trabajo en piso y reportar producción/incidencias | Dashboard, Producción, Incidencias |
| Supervisor | Coordinar operación diaria y resolver desviaciones | Dashboard, Alertas, Reasignaciones, Asignaciones, Incidencias |
| Gerente | Supervisar KPIs, métricas y órdenes de producción | Dashboard, Reportes, Métricas, Órdenes |
| Admin | Administrar usuarios, máquinas y operarios | Usuarios, Máquinas, Operarios |

## Operario

### Rutas principales

- `/operario`
- `/operario/produccion`
- `/operario/incidencias`

### Funciones implementadas

- Ver su dashboard personal con asignación activa y métricas del día.
- Iniciar una tarea pendiente cuando tiene una asignación disponible.
- Finalizar una tarea activa desde el dashboard.
- Consultar su producción del día y su objetivo operativo.
- Registrar producción manual asociada a su asignación activa.
- Ver historial de registros de producción.
- Reportar incidencias operativas desde piso.
- Seleccionar máquina, tipo de incidencia, título y descripción del problema.
- Consultar el listado de incidencias reportadas.

### Alcance operativo

- El operario está orientado a ejecución y registro.
- No administra usuarios, máquinas ni órdenes globales.

## Supervisor

### Rutas principales

- `/supervisor`
- `/supervisor/alertas`
- `/supervisor/sugerencias`
- `/supervisor/asignaciones`
- `/supervisor/incidencias`

### Funciones implementadas

- Ver dashboard operativo con máquinas en operación, alertas activas, incidencias abiertas y eficiencia del turno.
- Revisar alertas activas desde el dashboard y resolverlas de forma directa.
- Consultar el listado completo de alertas.
- Resolver alertas individuales.
- Resolver todas las alertas activas en lote.
- Consultar sugerencias de reasignación generadas por el sistema.
- Aceptar o rechazar sugerencias de reasignación.
- Ver impacto estimado de cada sugerencia.
- Crear nuevas asignaciones de operarios a máquinas y turnos.
- Consultar el estado actual de las asignaciones.
- Iniciar asignaciones pendientes.
- Finalizar asignaciones activas.
- Consultar incidencias abiertas, en proceso y resueltas.
- Resolver incidencias abiertas.

### Alcance operativo

- El supervisor actúa sobre la operación diaria.
- Está enfocado en coordinación, respuesta a alertas y control de ejecución.

## Gerente

### Rutas principales

- `/gerente`
- `/gerente/reportes`
- `/gerente/metricas`
- `/gerente/ordenes`

### Funciones implementadas

- Ver dashboard gerencial con KPIs globales.
- Consultar eficiencia general, OEE aproximado y cumplimiento de objetivos.
- Visualizar tendencia de eficiencia de los últimos días.
- Revisar top de operarios por eficiencia.
- Consultar distribución de incidencias por tipo.
- Ver historial de reportes generados.
- Exportar reportes en CSV.
- Descargar archivos de reportes existentes cuando están disponibles.
- Consultar métricas de eficiencia por máquina.
- Visualizar gráfico comparativo de eficiencia por máquina.
- Revisar registros de métricas con producción real y objetivo.
- Crear órdenes de producción nuevas.
- Asignar prioridad, fecha límite, máquina y notas a cada orden.
- Iniciar órdenes pendientes.
- Completar órdenes en proceso.
- Consultar la cola de despacho.
- Despachar la siguiente orden disponible en cola.

### Alcance operativo

- El gerente opera a nivel de seguimiento estratégico y planificación.
- Se centra en indicadores, reportes y control de órdenes de producción.

## Admin

### Rutas principales

- `/admin/usuarios`
- `/admin/maquinas`
- `/admin/operarios`

### Funciones implementadas

#### Gestión de usuarios

- Ver listado completo de usuarios.
- Buscar usuarios por nombre, usuario, email o rol.
- Crear nuevos usuarios.
- Asignar rol al crear el usuario.
- Editar usuario existente.
- Modificar nombre, apellido, username, email, teléfono, rol y estado.
- Activar o desactivar usuarios.
- Restablecer contraseña de cualquier usuario desde el panel.

#### Gestión de máquinas

- Ver listado de máquinas registradas.
- Crear nuevas máquinas.
- Asociar tipo de máquina y eficiencia objetivo.
- Consultar estado y actividad de cada máquina.
- Activar o desactivar máquinas.

#### Gestión de operarios

- Ver listado de operarios con usuario asociado.
- Consultar código de empleado, turno y habilidades.
- Ver estado activo/inactivo del operario.
- Activar o desactivar operarios.

### Alcance operativo

- El admin está orientado a configuración y administración del sistema.
- Actualmente no tiene un dashboard gerencial propio; su foco está en mantenimiento de catálogos y usuarios.

## Funciones comunes para todos los roles

- Iniciar sesión con usuario y contraseña.
- Mantener sesión autenticada mediante JWT.
- Cerrar sesión.
- Navegar a su espacio según el rol asignado.
- Ver notificaciones asociadas al usuario autenticado.

## Nota de alcance

Este documento describe las funciones actualmente visibles e implementadas en la versión actual del proyecto. Si se agregan nuevos módulos o permisos por rol, conviene actualizar este archivo para mantenerlo alineado con el sistema real.