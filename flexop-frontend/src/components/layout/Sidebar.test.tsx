import { render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { Sidebar } from './Sidebar';

vi.mock('@/stores/authStore', () => ({
  useAuthStore: vi.fn(),
}));

import { useAuthStore } from '@/stores/authStore';

describe('Sidebar', () => {
  it('muestra navegacion de operario', () => {
    vi.mocked(useAuthStore).mockReturnValue({
      user: {
        id: 1,
        username: 'op',
        email: 'op@test.com',
        first_name: 'Ana',
        last_name: 'Op',
        rol: 'OPERARIO',
        empresa: 1,
        activo: true,
      },
    } as ReturnType<typeof useAuthStore>);

    render(<Sidebar />);
    expect(screen.getByText('FLEX-OP')).toBeInTheDocument();
    expect(screen.getByText('Mi Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Producción')).toBeInTheDocument();
    expect(screen.getByText('OPERARIO')).toBeInTheDocument();
  });

  it('sin usuario no muestra items de nav', () => {
    vi.mocked(useAuthStore).mockReturnValue({ user: null } as ReturnType<typeof useAuthStore>);
    render(<Sidebar />);
    expect(screen.queryByText('Mi Dashboard')).not.toBeInTheDocument();
  });
});
