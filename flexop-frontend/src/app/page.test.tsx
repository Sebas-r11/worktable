import { screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import HomePage from './page';
import { renderWithProviders } from '@/test/test-utils';
import { useAuthStore } from '@/stores/authStore';
import { mockSupervisorUser } from '@/test/msw/fixtures';

const replaceMock = vi.fn();

vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: vi.fn(),
    replace: replaceMock,
    prefetch: vi.fn(),
    back: vi.fn(),
  }),
  usePathname: () => '/',
  useSearchParams: () => new URLSearchParams(),
}));

describe('HomePage', () => {
  beforeEach(() => {
    replaceMock.mockClear();
    useAuthStore.setState({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
    });
  });

  it('llama loadUser y redirige al dashboard del rol', async () => {
    renderWithProviders(<HomePage />);

    await waitFor(() => {
      expect(useAuthStore.getState().isAuthenticated).toBe(true);
    });

    await waitFor(() => {
      expect(replaceMock).toHaveBeenCalledWith('/supervisor');
    });
  });

  it('redirige a login si loadUser falla', async () => {
    useAuthStore.setState({
      user: mockSupervisorUser,
      isAuthenticated: true,
    });

    const loadUser = vi.fn(async () => {
      useAuthStore.setState({
        user: null,
        isAuthenticated: false,
        isLoading: false,
      });
    });
    useAuthStore.setState({ loadUser });

    renderWithProviders(<HomePage />);

    await waitFor(() => {
      expect(replaceMock).toHaveBeenCalledWith('/login');
    });
  });
});
