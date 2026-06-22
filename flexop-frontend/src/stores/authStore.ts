'use client';

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { authApi } from '@/lib/api/usuarios';
import { saveTokens, clearTokens, getRefreshToken } from '@/lib/api/client';
import type { AuthUser, LoginCredentials } from '@/types';

interface AuthState {
  user: AuthUser | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => Promise<void>;
  loadUser: () => Promise<void>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      login: async (credentials) => {
        set({ isLoading: true, error: null });
        try {
          const { data: tokens } = await authApi.login(credentials);
          saveTokens(tokens.access, tokens.refresh);

          const { data: user } = await authApi.me();
          set({ user, isAuthenticated: true, isLoading: false });
        } catch (err: unknown) {
          const message =
            (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
            'Credenciales incorrectas';
          set({ error: message, isLoading: false, isAuthenticated: false, user: null });
          clearTokens();
        }
      },

      logout: async () => {
        const refresh = getRefreshToken();
        try {
          if (refresh) {
            await authApi.logout(refresh);
          }
        } catch {
          // Ignorar errores de red al cerrar sesión
        } finally {
          clearTokens();
          set({ user: null, isAuthenticated: false, error: null });
        }
      },

      loadUser: async () => {
        set({ isLoading: true });
        try {
          const { data: user } = await authApi.me();
          set({ user, isAuthenticated: true, isLoading: false });
        } catch {
          clearTokens();
          set({ user: null, isAuthenticated: false, isLoading: false });
        }
      },

      clearError: () => set({ error: null }),
    }),
    {
      name: 'flexop-auth',
      // Solo persiste el usuario, NO el estado de carga o error
      partialize: (state) => ({ user: state.user, isAuthenticated: state.isAuthenticated }),
    }
  )
);
