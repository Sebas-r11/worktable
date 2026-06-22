import { beforeEach, describe, expect, it } from 'vitest';
import { useAuthStore } from './authStore';
import { mockSupervisorUser } from '@/test/msw/fixtures';

describe('useAuthStore (MSW)', () => {
  beforeEach(() => {
    useAuthStore.setState({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
    });
  });

  it('login exitoso autentica usuario', async () => {
    await useAuthStore.getState().login({
      username: 'supervisor1',
      password: 'super123',
    });

    const state = useAuthStore.getState();
    expect(state.isAuthenticated).toBe(true);
    expect(state.user?.username).toBe(mockSupervisorUser.username);
    expect(state.error).toBeNull();
  });

  it('login fallido muestra error del API', async () => {
    await useAuthStore.getState().login({ username: 'bad', password: 'wrong' });

    const state = useAuthStore.getState();
    expect(state.isAuthenticated).toBe(false);
    expect(state.error).toBeTruthy();
  });

  it('loadUser restaura sesion cuando /me responde', async () => {
    await useAuthStore.getState().loadUser();
    expect(useAuthStore.getState().isAuthenticated).toBe(true);
  });

  it('logout resetea estado', async () => {
    useAuthStore.setState({ user: mockSupervisorUser, isAuthenticated: true });
    await useAuthStore.getState().logout();
    const state = useAuthStore.getState();
    expect(state.isAuthenticated).toBe(false);
    expect(state.user).toBeNull();
  });

  it('logout llama al endpoint de blacklist', async () => {
    let logoutCalled = false;
    const { server } = await import('@/test/msw/server');
    const { http, HttpResponse } = await import('msw');
    const { API_BASE } = await import('@/test/msw/constants');
    const { saveTokens } = await import('@/lib/api/client');

    saveTokens('access-test', 'refresh-test');
    server.use(
      http.post(`${API_BASE}/auth/logout/`, async ({ request }) => {
        logoutCalled = true;
        const body = (await request.json()) as { refresh?: string };
        expect(body.refresh).toBe('refresh-test');
        return HttpResponse.json({}, { status: 200 });
      }),
    );

    useAuthStore.setState({ user: mockSupervisorUser, isAuthenticated: true });
    await useAuthStore.getState().logout();
    expect(logoutCalled).toBe(true);
  });

  it('clearError limpia mensaje', () => {
    useAuthStore.setState({ error: 'Error previo' });
    useAuthStore.getState().clearError();
    expect(useAuthStore.getState().error).toBeNull();
  });
});
