import type {
  Alerta,
  AuthUser,
  ColaDespacho,
  DashboardGerente,
  DashboardOperario,
  DashboardSupervisor,
  Incidencia,
  Maquina,
  MetricaEficiencia,
  Notificacion,
  OrdenProduccion,
  RegistroProduccion,
  ReporteGenerado,
  SugerenciaReasignacion,
  TipoMaquina,
  UnidadEficiencia,
  Usuario,
} from '@/types';

export const mockSupervisorUser: AuthUser = {
  id: 2,
  username: 'supervisor1',
  email: 'supervisor@test.com',
  first_name: 'Super',
  last_name: 'Visor',
  rol: 'SUPERVISOR',
  empresa: 1,
  activo: true,
};

export const mockAdminUser: AuthUser = {
  id: 10,
  username: 'admin',
  email: 'admin@test.com',
  first_name: 'Admin',
  last_name: 'Sistema',
  rol: 'ADMIN',
  empresa: 1,
  activo: true,
};

export const mockOperarioUser: AuthUser = {
  id: 3,
  username: 'operario1',
  email: 'operario@test.com',
  first_name: 'Ana',
  last_name: 'Oper',
  rol: 'OPERARIO',
  empresa: 1,
  activo: true,
};

export const mockUsuarioOperario: Usuario = {
  id: 3,
  username: 'operario1',
  email: 'operario@test.com',
  first_name: 'Ana',
  last_name: 'Oper',
  rol: 'OPERARIO',
  telefono: '999111222',
  empresa: 1,
  activo: true,
  fecha_ingreso: '2026-01-15',
};

export const mockUsuarioGerente: Usuario = {
  id: 4,
  username: 'gerente1',
  email: 'gerente@test.com',
  first_name: 'Carlos',
  last_name: 'Gerente',
  rol: 'GERENTE',
  telefono: null,
  empresa: 1,
  activo: true,
  fecha_ingreso: '2026-02-01',
};

export const mockGerenteUser: AuthUser = {
  id: 4,
  username: 'gerente1',
  email: 'gerente@test.com',
  first_name: 'Carlos',
  last_name: 'Gerente',
  rol: 'GERENTE',
  empresa: 1,
  activo: true,
};

export const mockTipoMaquina: TipoMaquina = {
  id: 1,
  nombre: 'Llenadora',
  empresa: 1,
};

export const mockUnidadEficiencia: UnidadEficiencia = {
  id: 1,
  nombre: 'Unidades por hora',
  abreviatura: 'u/h',
  empresa: 1,
};

export const mockDashboardOperario: DashboardOperario = {
  asignacion_activa: {
    id: 10,
    maquina: 'Llenadora 1',
    maquina_codigo: 'MAQ-001',
    turno: 'Mañana',
    hora_inicio: null,
    estado: 'PENDIENTE',
  },
  produccion_hoy: 120,
  objetivo_dia: 200,
  porcentaje_objetivo: 60,
  eficiencia_hoy: 88.5,
  tareas_completadas_hoy: 2,
  eficiencia_promedio: 85,
  incidencias_abiertas: 1,
};

export const mockRegistroProduccion: RegistroProduccion = {
  id: 1,
  asignacion: 10,
  cantidad: 50,
  observaciones: 'Turno mañana',
  fecha_hora: '2026-05-28T08:30:00Z',
};

export const mockIncidencia: Incidencia = {
  id: 1,
  asignacion: 10,
  maquina: 2,
  maquina_nombre: 'Llenadora 1',
  tipo: 'FALLA_MAQUINA',
  titulo: 'Parada inesperada',
  descripcion: 'La máquina dejó de responder',
  estado: 'ABIERTA',
  prioridad: 'ALTA',
  fecha_reporte: '2026-05-28T14:00:00Z',
  fecha_resolucion: null,
};

export const mockAlertaActiva: Alerta = {
  id: 1,
  titulo: 'Capacidad baja',
  descripcion: 'Máquina INY-001 por debajo del 70%',
  prioridad: 'ALTA',
  estado: 'ACTIVA',
  fecha_creacion: '2026-05-28T12:00:00Z',
};

export const mockSugerenciaPendiente: SugerenciaReasignacion = {
  id: 5,
  operario: 1,
  operario_codigo: 'EMP-001',
  operario_nombre: 'Ana Oper',
  maquina_destino: 2,
  maquina_destino_codigo: 'MAQ-002',
  razon: 'BAJA_EFICIENCIA',
  razon_display: 'Baja eficiencia en turno',
  descripcion: 'Reasignar a máquina con mayor demanda',
  estado: 'PENDIENTE',
  impacto_estimado: 15.2,
  fecha_creacion: '2026-05-28T10:00:00Z',
};

export const mockDashboardSupervisor: DashboardSupervisor = {
  maquinas_estado: [
    { id: 1, codigo: 'MAQ-001', nombre: 'Llenadora 1', estado: 'OPERANDO', color: 'verde' },
  ],
  alertas_activas: 2,
  alertas_criticas: 1,
  sugerencias_pendientes: 1,
  eficiencia_turno: 85.5,
  ranking_operarios: [],
  incidencias_abiertas: 1,
};

export const mockMetrica: MetricaEficiencia = {
  id: 1,
  operario: 1,
  maquina: 2,
  maquina_nombre: 'Llenadora 1',
  fecha: '2026-05-28',
  produccion_real: 80,
  produccion_teorica: 100,
  eficiencia_calculada: 80,
  unidad: 'u/h',
};

export const mockMaquina: Maquina = {
  id: 2,
  codigo: 'MAQ-001',
  nombre: 'Llenadora 1',
  tipo: 1,
  empresa: 1,
  capacidad_teorica: 100,
  unidad_capacidad: 1,
  unidad_nombre: 'u/h',
  estado_actual: 'OPERANDO',
  activa: true,
};

export const mockOrden: OrdenProduccion = {
  id: 1,
  numero_orden: 'ORD-001',
  producto: 'Producto A',
  cantidad_requerida: 100,
  cantidad_producida: 0,
  estado: 'PENDIENTE',
  prioridad: 'NORMAL',
  fecha_limite: '2026-06-01',
};

export const mockOrdenEnProceso: OrdenProduccion = {
  ...mockOrden,
  estado: 'EN_PROCESO',
  cantidad_producida: 50,
};

export const mockColaDespacho: ColaDespacho = {
  id: 1,
  orden: 1,
  orden_numero: 'ORD-001',
  producto: 'Producto A',
  cantidad: 100,
  posicion_manual: 1,
  estado: 'EN_COLA',
  fecha_entrada: '2026-05-28T10:00:00Z',
  fecha_despacho: null,
};

export const mockDashboardGerente: DashboardGerente = {
  eficiencia_general: 82.5,
  oee_aproximado: 75.2,
  cumplimiento_objetivos: 88,
  produccion_dia: 1200,
  produccion_semana: 8400,
  tendencia: [{ fecha: '2026-05-28', eficiencia: 82 }],
  tendencia_eficiencia: [{ fecha: '2026-05-28', eficiencia: 82 }],
  top_operarios: [{ codigo: 'EMP-001', nombre: 'Ana Oper', eficiencia: 91 }],
  comparativa_turnos: [{ turno: 'Mañana', eficiencia: 85 }],
  estadisticas_incidencias: {
    total: 5,
    abiertas: 2,
    resueltas: 3,
    por_tipo: [{ tipo: 'FALLA_MAQUINA', total: 2 }],
  },
};

export const mockReporte: ReporteGenerado = {
  id: 3,
  tipo: 'EFICIENCIA_DIARIA',
  tipo_display: 'Eficiencia Diaria',
  formato: 'CSV',
  formato_display: 'CSV',
  fecha_inicio: '2026-05-01',
  fecha_fin: '2026-05-28',
  fecha_generacion: '2026-05-28T12:00:00Z',
  empresa: 1,
};

export const mockNotificacionNoLeida: Notificacion = {
  id: 1,
  usuario: 1,
  titulo: 'Incidencia escalada',
  mensaje: 'Revisar máquina MAQ-001',
  leida: false,
  fecha_creacion: '2026-05-28T10:00:00Z',
};

export function paginated<T>(results: T[]) {
  return { count: results.length, next: null, previous: null, results };
}
