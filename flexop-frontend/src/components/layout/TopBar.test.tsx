import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi, beforeEach } from 'vitest';
import { TopBar } from './TopBar';

const mockLogout = vi.fn();
const mockReplace = vi.fn();

vi.mock('next/navigation', () => ({
  useRouter: () => ({ replace: mockReplace, push: vi.fn() }),
  usePathname: () => '/gerente',
  useSearchParams: () => new URLSearchParams(),
}));

vi.mock('@/stores/authStore', () => ({
  useAuthStore: vi.fn(),
}));

vi.mock('@/components/shared/NotificationBell', () => ({
  NotificationBell: () => <div data-testid="notification-bell" />,
}));

import { useAuthStore } from '@/stores/authStore';

describe('TopBar', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(useAuthStore).mockReturnValue({
      user: {
        id: 1,
        username: 'gerente_test',
        email: 'gerente@test.com',
        first_name: 'Ger',
        last_name: 'Ente',
        rol: 'GERENTE',
        empresa: 1,
        activo: true,
      },
      logout: mockLogout,
      login: vi.fn(),
      isAuthenticated: true,
      isLoading: false,
      error: null,
      clearError: vi.fn(),
      loadUser: vi.fn(),
    } as ReturnType<typeof useAuthStore>);
  });

  it('muestra iniciales y campana de notificaciones', () => {
    render(<TopBar />);
    expect(screen.getByText('GE')).toBeInTheDocument();
    expect(screen.getByTestId('notification-bell')).toBeInTheDocument();
  });

  it('cierra sesion y redirige a login', async () => {
    const user = userEvent.setup();
    render(<TopBar />);

    await user.click(screen.getByRole('button', { name: 'GE' }));
    await user.click(screen.getByText('Cerrar sesión'));

    expect(mockLogout).toHaveBeenCalled();
    expect(mockReplace).toHaveBeenCalledWith('/login');
  });
});
