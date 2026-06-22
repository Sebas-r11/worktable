import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi, beforeEach } from 'vitest';
import LoginPage from './page';

const mockLogin = vi.fn();
const mockClearError = vi.fn();

vi.mock('@/stores/authStore', () => ({
  useAuthStore: vi.fn(),
}));

import { useAuthStore } from '@/stores/authStore';

describe('LoginPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(useAuthStore).mockReturnValue({
      login: mockLogin,
      isAuthenticated: false,
      isLoading: false,
      error: null,
      user: null,
      clearError: mockClearError,
      logout: vi.fn(),
      loadUser: vi.fn(),
    } as ReturnType<typeof useAuthStore>);
  });

  it('renderiza formulario de login', () => {
    render(<LoginPage />);
    expect(screen.getByText('FLEX-OP')).toBeInTheDocument();
    expect(screen.getByLabelText(/usuario/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/contraseña/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /iniciar sesión/i })).toBeInTheDocument();
  });

  it('muestra error del store', () => {
    vi.mocked(useAuthStore).mockReturnValue({
      login: mockLogin,
      isAuthenticated: false,
      isLoading: false,
      error: 'Credenciales incorrectas',
      user: null,
      clearError: mockClearError,
      logout: vi.fn(),
      loadUser: vi.fn(),
    } as ReturnType<typeof useAuthStore>);

    render(<LoginPage />);
    expect(screen.getByText('Credenciales incorrectas')).toBeInTheDocument();
  });

  it('envia credenciales al submit', async () => {
    const user = userEvent.setup();
    mockLogin.mockResolvedValue(undefined);
    render(<LoginPage />);

    await user.type(screen.getByLabelText(/usuario/i), 'supervisor_test');
    await user.type(screen.getByLabelText(/contraseña/i), 'TestPass123!');
    await user.click(screen.getByRole('button', { name: /iniciar sesión/i }));

    await waitFor(() => {
      expect(mockClearError).toHaveBeenCalled();
      expect(mockLogin).toHaveBeenCalledWith({
        username: 'supervisor_test',
        password: 'TestPass123!',
      });
    });
  });

  it('valida campos requeridos', async () => {
    const user = userEvent.setup();
    render(<LoginPage />);
    await user.click(screen.getByRole('button', { name: /iniciar sesión/i }));
    expect(await screen.findByText('El usuario es requerido')).toBeInTheDocument();
    expect(mockLogin).not.toHaveBeenCalled();
  });
});
