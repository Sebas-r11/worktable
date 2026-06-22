// ─── Autenticación ───────────────────────────────────────────────
export interface LoginCredentials {
  username: string;
  password: string;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface AuthUser {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  rol: 'OPERARIO' | 'SUPERVISOR' | 'GERENTE' | 'ADMIN';
  empresa: number | null;
  activo: boolean;
}

// ─── Paginación ───────────────────────────────────────────────────
export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// ─── Empresa ─────────────────────────────────────────────────────
export interface Empresa {
  id: number;
  nombre: string;
  razon_social: string;
  ruc: string;
  direccion: string;
  telefono: string;
  email: string;
  activo: boolean;
}

// ─── Usuarios ────────────────────────────────────────────────────
export interface Usuario {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  rol: 'OPERARIO' | 'SUPERVISOR' | 'GERENTE' | 'ADMIN';
  telefono?: string | null;
  empresa: number | null;
  empresa_detalle?: Empresa;
  activo: boolean;
  fecha_ingreso: string;
}

// ─── Máquinas ────────────────────────────────────────────────────
export interface TipoMaquina {
  id: number;
  nombre: string;
  descripcion?: string;
  empresa: number;
  empresa_nombre?: string;
  total_maquinas?: number;
}

export interface UnidadEficiencia {
  id: number;
  nombre: string;
  abreviatura: string;
  descripcion?: string;
  empresa: number;
  empresa_nombre?: string;
}

export type MaquinaEstado = 'DISPONIBLE' | 'OPERANDO' | 'MANTENIMIENTO' | 'PARADA' | 'FUERA_SERVICIO';

export interface Maquina {
  id: number;
  codigo: string;
  nombre: string;
  tipo: number;
  tipo_nombre?: string;
  tipo_detalle?: TipoMaquina;
  empresa: number;
  empresa_nombre?: string;
  marca?: string;
  modelo?: string;
  numero_serie?: string;
  ubicacion?: string;
  capacidad_teorica: number;
  unidad_capacidad: number;
  unidad_nombre?: string;
  estado_actual: MaquinaEstado;
  estado_display?: string;
  activa: boolean;
  fecha_creacion?: string;
  fecha_actualizacion?: string;
}

export interface Producto {
  id: number;
  nombre: string;
  codigo: string;
  descripcion: string;
  unidad_medida: string;
  empresa: number;
  activo: boolean;
}

// ─── Operaciones ─────────────────────────────────────────────────
export interface Turno {
  id: number;
  nombre: string;
  hora_inicio: string;
  hora_fin: string;
  empresa: number;
  activo: boolean;
}

export interface Habilidad {
  id: number;
  nombre: string;
  descripcion: string;
  empresa: number;
}

export interface Operario {
  id: number;
  usuario: number;
  usuario_detalle?: Usuario;
  usuario_nombre?: string;
  usuario_username?: string;
  usuario_email?: string;
  codigo_empleado?: string;
  habilidades: number[];
  habilidades_detalle?: Habilidad[];
  habilidades_nombres?: string[];
  turno: number | null;
  turno_actual?: number | null;
  turno_detalle?: Turno;
  turno_nombre?: string;
  disponible?: boolean;
  activo: boolean;
}

export interface Asignacion {
  id: number;
  operario: number;
  operario_detalle?: Operario;
  operario_nombre?: string;
  operario_codigo?: string;
  maquina: number;
  maquina_detalle?: Maquina;
  maquina_nombre?: string;
  maquina_codigo?: string;
  turno: number;
  turno_detalle?: Turno;
  turno_nombre?: string;
  estado: 'PENDIENTE' | 'ACTIVA' | 'COMPLETADA' | 'CANCELADA';
  fecha: string;
  hora_inicio_real: string | null;
  hora_fin_real: string | null;
  observaciones?: string;
  fecha_creacion: string;
  fecha_actualizacion?: string;
}

export interface Incidencia {
  id: number;
  asignacion: number | null;
  maquina: number;
  maquina_nombre?: string;
  tipo: 'FALLA_MAQUINA' | 'FALTA_MATERIAL' | 'PROBLEMA_CALIDAD' | 'OTRO';
  titulo: string;
  descripcion: string;
  estado: 'ABIERTA' | 'EN_PROCESO' | 'RESUELTA' | 'ESCALADA';
  prioridad: 'BAJA' | 'MEDIA' | 'ALTA' | 'CRITICA';
  fecha_reporte: string;
  fecha_resolucion: string | null;
  solucion?: string;
}

// ─── Métricas ────────────────────────────────────────────────────
export interface RegistroProduccion {
  id: number;
  asignacion: number;
  asignacion_info?: { operario: string; maquina: string; fecha: string };
  cantidad: number;
  observaciones?: string;
  fecha_hora: string;
  registrado_por?: number;
  registrado_por_nombre?: string;
}

export interface MetricaEficiencia {
  id: number;
  operario: number;
  operario_nombre?: string;
  operario_codigo?: string;
  maquina: number;
  maquina_nombre?: string;
  maquina_codigo?: string;
  asignacion?: number | null;
  fecha: string;
  fecha_calculo?: string;
  produccion_real: number;
  produccion_teorica: number;
  horas_trabajadas?: number;
  eficiencia_calculada: number;
  unidad?: string;
}

export interface ObjetivoProduccion {
  id: number;
  tipo: string;
  tipo_display?: string;
  maquina?: number | null;
  maquina_nombre?: string;
  turno?: number | null;
  turno_nombre?: string;
  operario?: number | null;
  operario_nombre?: string;
  empresa: number;
  cantidad_objetivo: number;
  periodo_inicio: string;
  periodo_fin: string;
  activo: boolean;
  cumplimiento?: number;
}

// ─── Alertas ─────────────────────────────────────────────────────
export interface ReglaAlerta {
  id: number;
  nombre: string;
  descripcion?: string;
  tipo: string;
  tipo_display?: string;
  umbral: number;
  unidad_umbral?: string;
  prioridad: 'BAJA' | 'MEDIA' | 'ALTA' | 'CRITICA';
  prioridad_display?: string;
  empresa: number;
  empresa_nombre?: string;
  activa: boolean;
  fecha_creacion?: string;
  fecha_actualizacion?: string;
  total_alertas?: number;
}

export interface Alerta {
  id: number;
  regla?: number | null;
  regla_nombre?: string;
  regla_detalle?: ReglaAlerta;
  titulo: string;
  descripcion: string;
  prioridad: 'BAJA' | 'MEDIA' | 'ALTA' | 'CRITICA';
  prioridad_display?: string;
  estado: 'ACTIVA' | 'RESUELTA' | 'ESCALADA' | 'DESCARTADA';
  estado_display?: string;
  operario_relacionado?: number | null;
  operario_nombre?: string;
  maquina_relacionada?: number | null;
  maquina_nombre?: string;
  incidencia_relacionada?: number | null;
  incidencia_titulo?: string;
  empresa?: number;
  fecha_creacion: string;
  fecha_resolucion?: string | null;
  resuelta_por?: number | null;
  resuelta_por_nombre?: string;
  notas_resolucion?: string;
}

export interface Notificacion {
  id: number;
  usuario: number;
  alerta?: number | null;
  alerta_titulo?: string;
  titulo: string;
  mensaje: string;
  leida: boolean;
  fecha_lectura?: string | null;
  fecha_creacion: string;
}

// ─── Reasignaciones ──────────────────────────────────────────────
export interface SugerenciaReasignacion {
  id: number;
  operario: number;
  operario_nombre?: string;
  operario_codigo?: string;
  operario_eficiencia?: number;
  maquina_origen?: number | null;
  maquina_origen_nombre?: string;
  maquina_origen_codigo?: string;
  maquina_destino: number;
  maquina_destino_nombre?: string;
  maquina_destino_codigo?: string;
  razon: string;
  razon_display?: string;
  descripcion?: string;
  impacto_estimado: number | string;
  estado: 'PENDIENTE' | 'ACEPTADA' | 'RECHAZADA' | 'EXPIRADA';
  estado_display?: string;
  empresa?: number;
  fecha_creacion: string;
  fecha_decision?: string | null;
  decidido_por?: number | null;
  decidido_por_nombre?: string;
  notas_decision?: string;
  asignacion_creada?: number | null;
}

// ─── Reportes generados ──────────────────────────────────────────
export interface ReporteGenerado {
  id: number;
  tipo: string;
  tipo_display?: string;
  formato: string;
  formato_display?: string;
  fecha_inicio: string;
  fecha_fin: string;
  archivo?: string | null;
  empresa: number;
  generado_por?: number;
  generado_por_nombre?: string;
  fecha_generacion: string;
  parametros?: Record<string, unknown>;
}

// ─── Órdenes ─────────────────────────────────────────────────────
export interface OrdenProduccion {
  id: number;
  numero_orden: string;
  producto: string;
  descripcion?: string;
  unidad?: string;
  cantidad_requerida: number;
  cantidad_producida: number;
  cantidad_pendiente?: number;
  porcentaje_completado?: number;
  estado: 'PENDIENTE' | 'EN_PROCESO' | 'LISTA' | 'DESPACHADA' | 'CANCELADA';
  prioridad: 'BAJA' | 'NORMAL' | 'ALTA' | 'URGENTE';
  fecha_limite: string;
  fecha_creacion?: string;
  maquina?: number | null;
  maquina_nombre?: string;
  notas?: string;
}

export interface ColaDespacho {
  id: number;
  orden: number;
  orden_detalle?: OrdenProduccion;
  orden_numero?: string;
  producto?: string;
  cantidad?: number;
  posicion_manual: number;
  estado: 'EN_COLA' | 'DESPACHADA';
  fecha_entrada: string;
  fecha_despacho: string | null;
}

// ─── Reportes / Dashboard ────────────────────────────────────────
export interface DashboardAsignacionActiva {
  id: number;
  maquina: string;
  maquina_codigo?: string;
  turno: string;
  hora_inicio: string | null;
  estado?: string;
}

export interface DashboardOperario {
  asignacion_activa: DashboardAsignacionActiva | null;
  produccion_hoy: number;
  objetivo_dia: number;
  porcentaje_objetivo: number;
  eficiencia_hoy: number;
  tareas_completadas_hoy: number;
  eficiencia_promedio: number;
  // legacy aliases
  objetivo_hoy?: number;
  incidencias_abiertas?: number;
}

export interface DashboardSupervisor {
  maquinas_estado: { id: number; codigo: string; nombre: string; estado: string; color: string }[];
  alertas_activas: number;
  alertas_criticas: number;
  sugerencias_pendientes: number;
  eficiencia_turno: number;
  ranking_operarios: { codigo: string; nombre: string; eficiencia: number }[];
  incidencias_abiertas: number;
  // legacy alias used in some pages
  operarios_activos?: number;
}

export interface DashboardGerente {
  eficiencia_general: number;
  oee_aproximado: number;
  cumplimiento_objetivos: number;
  produccion_dia: number;
  produccion_total_dia?: number;
  produccion_semana: number;
  produccion_total_semana?: number;
  tendencia: { fecha: string; eficiencia: number }[];
  tendencia_eficiencia?: { fecha: string; eficiencia: number }[];
  top_operarios: { codigo: string; nombre: string; eficiencia: number }[];
  bottom_operarios?: { codigo: string; nombre: string; eficiencia: number }[];
  comparativa_turnos: { turno: string; eficiencia: number }[];
  ranking_maquinas?: { codigo: string; nombre: string; eficiencia: number }[];
  estadisticas_incidencias?: {
    total: number;
    abiertas: number;
    resueltas: number;
    por_tipo: { tipo: string; total: number }[];
  };
  // legacy aliases used in charts
  oee?: number;
  cumplimiento?: number;
}
