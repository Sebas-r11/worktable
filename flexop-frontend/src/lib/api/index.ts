import apiClient from './client';
import type {
  Alerta,
  ReglaAlerta,
  Notificacion,
  SugerenciaReasignacion,
  OrdenProduccion,
  ColaDespacho,
  RegistroProduccion,
  MetricaEficiencia,
  ObjetivoProduccion,
  DashboardOperario,
  DashboardSupervisor,
  DashboardGerente,
  ReporteGenerado,
  PaginatedResponse,
} from '@/types';

// ─── Métricas ─────────────────────────────────────────────────────
export const metricasApi = {
  produccionList: (params?: Record<string, unknown>) =>
    apiClient.get<PaginatedResponse<RegistroProduccion>>('/produccion/', { params }),

  produccionCreate: (data: Partial<RegistroProduccion>) =>
    apiClient.post<RegistroProduccion>('/produccion/', data),

  metricasList: (params?: Record<string, unknown>) =>
    apiClient.get<PaginatedResponse<MetricaEficiencia>>('/metricas/', { params }),

  objetivosList: (params?: Record<string, unknown>) =>
    apiClient.get<PaginatedResponse<ObjetivoProduccion>>('/objetivos/', { params }),

  objetivoCreate: (data: Partial<ObjetivoProduccion>) =>
    apiClient.post<ObjetivoProduccion>('/objetivos/', data),
};

// ─── Alertas ──────────────────────────────────────────────────────
export const alertasApi = {
  reglasList: () =>
    apiClient.get<PaginatedResponse<ReglaAlerta>>('/reglas-alerta/'),

  reglaCreate: (data: Partial<ReglaAlerta>) =>
    apiClient.post<ReglaAlerta>('/reglas-alerta/', data),

  reglaUpdate: (id: number, data: Partial<ReglaAlerta>) =>
    apiClient.patch<ReglaAlerta>(`/reglas-alerta/${id}/`, data),

  reglaDelete: (id: number) =>
    apiClient.delete(`/reglas-alerta/${id}/`),

  alertasList: (params?: Record<string, unknown>) =>
    apiClient.get<PaginatedResponse<Alerta>>('/alertas/', { params }),

  alertaResolver: (id: number) =>
    apiClient.post<Alerta>(`/alertas/${id}/resolver/`),

  alertasEstadisticas: () =>
    apiClient.get('/alertas/estadisticas/'),

  notificacionesList: () =>
    apiClient.get<PaginatedResponse<Notificacion>>('/notificaciones/'),

  notificacionMarcarLeida: (id: number) =>
    apiClient.post(`/notificaciones/${id}/marcar_leida/`),
};

// ─── Reasignaciones ───────────────────────────────────────────────
export const reasignacionesApi = {
  sugerenciasList: (params?: Record<string, unknown>) =>
    apiClient.get<PaginatedResponse<SugerenciaReasignacion>>('/sugerencias/', { params }),

  sugerenciaAceptar: (id: number) =>
    apiClient.post<SugerenciaReasignacion>(`/sugerencias/${id}/aceptar/`),

  sugerenciaRechazar: (id: number, notas = 'Rechazada por el supervisor') =>
    apiClient.post<SugerenciaReasignacion>(`/sugerencias/${id}/rechazar/`, { notas }),
};

// ─── Órdenes ──────────────────────────────────────────────────────
export const ordenesApi = {
  list: (params?: Record<string, unknown>) =>
    apiClient.get<PaginatedResponse<OrdenProduccion>>('/ordenes/', { params }),

  get: (id: number) =>
    apiClient.get<OrdenProduccion>(`/ordenes/${id}/`),

  create: (data: Partial<OrdenProduccion>) =>
    apiClient.post<OrdenProduccion>('/ordenes/', data),

  iniciar: (id: number) =>
    apiClient.post<OrdenProduccion>(`/ordenes/${id}/iniciar/`),

  completar: (id: number) =>
    apiClient.post<OrdenProduccion>(`/ordenes/${id}/completar/`),

  registrarProduccion: (id: number, data: { cantidad: number }) =>
    apiClient.post(`/ordenes/${id}/registrar_produccion/`, data),

  colaDespacho: () =>
    apiClient.get<ColaDespacho[]>('/cola-despacho/pendientes/'),

  despachar: (id: number) =>
    apiClient.post(`/cola-despacho/${id}/despachar/`),
};

// ─── Reportes / Dashboard ─────────────────────────────────────────
export const reportesApi = {
  dashboardOperario: () =>
    apiClient.get<DashboardOperario>('/dashboard/operario/'),

  dashboardSupervisor: () =>
    apiClient.get<DashboardSupervisor>('/dashboard/supervisor/'),

  dashboardGerente: () =>
    apiClient.get<DashboardGerente>('/dashboard/gerente/'),

  exportarCSV: (params?: Record<string, unknown>) =>
    apiClient.get('/exportar-csv/', { params, responseType: 'blob' }),

  reportesGenerados: (params?: Record<string, unknown>) =>
    apiClient.get<PaginatedResponse<ReporteGenerado>>('/reportes-generados/', { params }),

  descargarReporte: (id: number) =>
    apiClient.get(`/reportes-generados/${id}/descargar/`, { responseType: 'blob' }),
};
