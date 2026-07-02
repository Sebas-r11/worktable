import apiClient from './client';
import type {
  LoginCredentials,
  AuthTokens,
  AuthUser,
  Usuario,
  Empresa,
  PaginatedResponse,
} from '@/types';

// ─── Auth ─────────────────────────────────────────────────────────
export const authApi = {
  login: (credentials: LoginCredentials) =>
    apiClient.post<AuthTokens>('/auth/login/', credentials),

  refresh: (refresh: string) =>
    apiClient.post<{ access: string }>('/auth/refresh/', { refresh }),

  verify: (token: string) =>
    apiClient.post('/auth/verify/', { token }),

  logout: (refresh: string) =>
    apiClient.post('/auth/logout/', { refresh }),

  me: () =>
    apiClient.get<AuthUser>('/usuarios/me/'),
};

// ─── Usuarios ─────────────────────────────────────────────────────
export const usuariosApi = {
  list: (params?: Record<string, unknown>) =>
    apiClient.get<PaginatedResponse<Usuario>>('/usuarios/', { params }),

  get: (id: number) =>
    apiClient.get<Usuario>(`/usuarios/${id}/`),

  create: (data: Partial<Usuario>) =>
    apiClient.post<Usuario>('/usuarios/', data),

  update: (id: number, data: Partial<Usuario>) =>
    apiClient.patch<Usuario>(`/usuarios/${id}/`, data),

  setPassword: (id: number, data: { new_password: string; new_password2: string }) =>
    apiClient.post<{ message: string }>(`/usuarios/${id}/set_password/`, data),

  delete: (id: number) =>
    apiClient.delete(`/usuarios/${id}/`),
};

// ─── Empresas ─────────────────────────────────────────────────────
export const empresasApi = {
  list: () =>
    apiClient.get<PaginatedResponse<Empresa>>('/empresas/'),

  get: (id: number) =>
    apiClient.get<Empresa>(`/empresas/${id}/`),

  create: (data: Partial<Empresa>) =>
    apiClient.post<Empresa>('/empresas/', data),

  update: (id: number, data: Partial<Empresa>) =>
    apiClient.patch<Empresa>(`/empresas/${id}/`, data),
};
