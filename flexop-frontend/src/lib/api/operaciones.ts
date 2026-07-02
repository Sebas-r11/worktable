import apiClient from './client';
import type {
  Turno,
  Operario,
  Asignacion,
  Incidencia,
  PaginatedResponse,
} from '@/types';

export const operacionesApi = {
  // Turnos
  turnosList: (params?: Record<string, unknown>) =>
    apiClient.get<PaginatedResponse<Turno>>('/turnos/', { params }),

  turnoCreate: (data: Partial<Turno>) =>
    apiClient.post<Turno>('/turnos/', data),

  turnoUpdate: (id: number, data: Partial<Turno>) =>
    apiClient.patch<Turno>(`/turnos/${id}/`, data),

  // Operarios
  operariosList: (params?: Record<string, unknown>) =>
    apiClient.get<PaginatedResponse<Operario>>('/operarios/', { params }),

  operarioGet: (id: number) =>
    apiClient.get<Operario>(`/operarios/${id}/`),

  operarioCreate: (data: Partial<Operario>) =>
    apiClient.post<Operario>('/operarios/', data),

  operarioUpdate: (id: number, data: Partial<Operario>) =>
    apiClient.patch<Operario>(`/operarios/${id}/`, data),

  // Asignaciones
  asignacionesList: (params?: Record<string, unknown>) =>
    apiClient.get<PaginatedResponse<Asignacion>>('/asignaciones/', { params }),

  asignacionGet: (id: number) =>
    apiClient.get<Asignacion>(`/asignaciones/${id}/`),

  asignacionCreate: (data: Partial<Asignacion>) =>
    apiClient.post<Asignacion>('/asignaciones/', data),

  asignacionIniciar: (id: number) =>
    apiClient.post<Asignacion>(`/asignaciones/${id}/iniciar/`),

  asignacionFinalizar: (id: number) =>
    apiClient.post<Asignacion>(`/asignaciones/${id}/finalizar/`),

  asignacionesActivas: () =>
    apiClient.get<Asignacion[]>('/asignaciones/activas/'),

  // Incidencias
  incidenciasList: (params?: Record<string, unknown>) =>
    apiClient.get<PaginatedResponse<Incidencia>>('/incidencias/', { params }),

  incidenciaCreate: (data: Partial<Incidencia>) =>
    apiClient.post<Incidencia>('/incidencias/', data),

  incidenciaResolver: (id: number, solucion: string) =>
    apiClient.post<Incidencia>(`/incidencias/${id}/resolver/`, { solucion }),
};
