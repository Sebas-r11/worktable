import apiClient from './client';
import type { TipoMaquina, Maquina, Producto, UnidadEficiencia, PaginatedResponse } from '@/types';

export const maquinasApi = {
  // Tipos de máquina
  tiposList: (params?: Record<string, unknown>) =>
    apiClient.get<PaginatedResponse<TipoMaquina>>('/tipos-maquina/', { params }),

  tipoCreate: (data: Partial<TipoMaquina>) =>
    apiClient.post<TipoMaquina>('/tipos-maquina/', data),

  tipoUpdate: (id: number, data: Partial<TipoMaquina>) =>
    apiClient.patch<TipoMaquina>(`/tipos-maquina/${id}/`, data),

  tipoDelete: (id: number) =>
    apiClient.delete(`/tipos-maquina/${id}/`),

  unidadesList: (params?: Record<string, unknown>) =>
    apiClient.get<PaginatedResponse<UnidadEficiencia>>('/unidades-eficiencia/', { params }),

  // Máquinas
  list: (params?: Record<string, unknown>) =>
    apiClient.get<PaginatedResponse<Maquina>>('/maquinas/', { params }),

  get: (id: number) =>
    apiClient.get<Maquina>(`/maquinas/${id}/`),

  create: (data: Partial<Maquina>) =>
    apiClient.post<Maquina>('/maquinas/', data),

  update: (id: number, data: Partial<Maquina>) =>
    apiClient.patch<Maquina>(`/maquinas/${id}/`, data),

  delete: (id: number) =>
    apiClient.delete(`/maquinas/${id}/`),

  // Productos
  productosList: (params?: Record<string, unknown>) =>
    apiClient.get<PaginatedResponse<Producto>>('/productos/', { params }),

  productoCreate: (data: Partial<Producto>) =>
    apiClient.post<Producto>('/productos/', data),

  productoUpdate: (id: number, data: Partial<Producto>) =>
    apiClient.patch<Producto>(`/productos/${id}/`, data),

  productoDelete: (id: number) =>
    apiClient.delete(`/productos/${id}/`),
};
