# Capítulo 19 — Manual de usuario

[← Índice](./README.md) | [← Anterior](./18-manual-tecnico.md)

---

## Acceso al sistema

| Paso | Acción |
|------|--------|
| 1 | Abrir navegador en http://localhost:3000 (o URL de despliegue) |
| 2 | Será redirigido a **/login** si no hay sesión |
| 3 | Ingresar usuario y contraseña |
| 4 | El sistema redirige al dashboard según su rol |

### Credenciales de demostración (`populate_db.py`)

| Usuario | Contraseña | Rol |
|---------|------------|-----|
| `operario1` | `operario123` | Operario |
| `supervisor1` | `super123` | Supervisor |
| `gerente1` | `gerente123` | Gerente |
| `admin` | `admin123` | Administrador |

## Navegación general

- **Barra lateral (Sidebar):** enlaces según rol.
- **Barra superior (TopBar):** campana de notificaciones, menú usuario, cerrar sesión.
- **Listados:** paginación inferior con Anterior / Siguiente cuando hay más de 20 registros.

---

## Módulo Operario

### Dashboard (`/operario`)

| Elemento | Uso |
|----------|-----|
| Tarjetas KPI | Producción del día, objetivo, estado asignación |
| Botón Iniciar | Disponible si hay asignación PENDIENTE |
| Botón Finalizar | Disponible si hay asignación ACTIVA |

**Captura sugerida:** Dashboard con asignación activa y KPIs visibles.

### Producción (`/operario/produccion`)

1. Verificar que tiene asignación activa (botón Registrar habilitado).
2. Clic en **Registrar**.
3. Ingresar cantidad y observaciones opcionales.
4. **Guardar**.

**Captura sugerida:** Diálogo de registro de producción.

### Incidencias (`/operario/incidencias`)

1. Clic en **Reportar incidencia**.
2. Seleccionar máquina, tipo, prioridad.
3. Completar título y descripción.
4. **Enviar**.

**Captura sugerida:** Formulario de incidencia y listado paginado.

---

## Módulo Supervisor

### Dashboard (`/supervisor`)

- Resumen de máquinas, alertas activas y sugerencias pendientes.
- Acciones rápidas: resolver alerta, aceptar sugerencia.

**Captura sugerida:** Vista con alertas y sugerencias en panel.

### Alertas (`/supervisor/alertas`)

- Listado de alertas con estado y prioridad.
- **Resolver** en fila individual.
- **Resolver todas** para lote.

**Captura sugerida:** Tabla de alertas con botón resolver.

### Sugerencias (`/supervisor/sugerencias`)

- Revisar razón, operario, máquina destino, impacto estimado.
- **Aceptar** o **Rechazar** en sugerencias PENDIENTE.

**Captura sugerida:** Fila con impacto +15% y botones de acción.

### Asignaciones (`/supervisor/asignaciones`)

1. **Nueva asignación:** operario + máquina + turno + fecha.
2. En listado: **Iniciar** / **Finalizar** según estado.

**Captura sugerida:** Diálogo nueva asignación.

### Incidencias (`/supervisor/incidencias`)

- Filtrar por estado en listado.
- **Resolver** con texto de solución.

**Captura sugerida:** Diálogo de resolución.

---

## Módulo Gerente

### Dashboard (`/gerente`)

- KPIs: eficiencia general, OEE aproximado, cumplimiento.
- Gráficos: tendencia, turnos, ranking.

**Captura sugerida:** Dashboard con gráficos Recharts.

### Reportes (`/gerente/reportes`)

- **Exportar CSV:** genera archivo últimos 7 días (eficiencia).
- Historial: botón descarga por reporte generado.

**Captura sugerida:** Tabla historial + toast de descarga exitosa.

### Métricas (`/gerente/metricas`)

- Gráfico de barras por máquina.
- Tabla con eficiencia %, producción real y teórica.

**Captura sugerida:** Gráfico + tabla paginada.

### Órdenes (`/gerente/ordenes`)

1. **Nueva orden:** producto, cantidad, prioridad, fecha límite, máquina.
2. **Iniciar** orden pendiente.
3. **Completar** orden en progreso → entra a cola.
4. En panel cola: **Despachar**.

**Captura sugerida:** Split vista órdenes + cola de despacho.

---

## Módulo Administrador

### Usuarios (`/admin/usuarios`)

- Buscar por nombre, email, rol.
- **Nuevo usuario:** datos personales, rol, contraseña.
- **Editar** / **Restablecer contraseña** / activar-desactivar.

**Captura sugerida:** Listado con badge de rol.

### Máquinas (`/admin/maquinas`)

- **Nueva máquina:** código, nombre, tipo, capacidad, unidad.
- Activar/desactivar desde listado.

**Captura sugerida:** Formulario creación máquina.

### Operarios (`/admin/operarios`)

- Listado con código empleado, turno, habilidades.
- Toggle **activo/inactivo** únicamente.

**Captura sugerida:** Tabla operarios con switch activo.

> **Nota:** No existe en UI la creación de operarios; debe hacerse vía API o admin Django.

---

## Notificaciones

1. Clic en icono campana (TopBar).
2. Ver notificaciones no leídas.
3. Clic en una notificación para marcarla leída.

**Captura sugerida:** Dropdown con badge de contador.

## Cerrar sesión

1. Clic en avatar (esquina superior derecha).
2. Seleccionar **Cerrar sesión**.

---

## Funcionalidades no disponibles en interfaz

| Función | Estado |
|---------|--------|
| Editar perfil propio | Menú Perfil sin acción |
| Gestionar empresas | Solo API |
| Configurar reglas de alerta | Solo API |
| Definir objetivos de producción | Solo API |
