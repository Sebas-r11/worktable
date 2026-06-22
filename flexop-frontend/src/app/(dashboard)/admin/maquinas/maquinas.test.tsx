import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { http, HttpResponse } from 'msw';
import { beforeEach, describe, expect, it } from 'vitest';
import AdminMaquinasPage from './page';
import { renderWithProviders } from '@/test/test-utils';
import { server } from '@/test/msw/server';
import { API_BASE } from '@/test/msw/constants';
import { mockAdminUser, mockMaquina, paginated } from '@/test/msw/fixtures';
import { useAuthStore } from '@/stores/authStore';

describe('AdminMaquinasPage (MSW)', () => {
  beforeEach(() => {
    useAuthStore.setState({
      user: mockAdminUser,
      isAuthenticated: true,
      isLoading: false,
      error: null,
    });
  });

  it('lista máquinas con código y estado', async () => {
    renderWithProviders(<AdminMaquinasPage />);

    expect(await screen.findByText('Máquinas')).toBeInTheDocument();
    expect(screen.getByText(mockMaquina.codigo)).toBeInTheDocument();
    expect(screen.getByText(mockMaquina.nombre)).toBeInTheDocument();
    expect(screen.getByText('OPERANDO')).toBeInTheDocument();
    expect(screen.getByText(/100/)).toBeInTheDocument();
  });

  it('desactiva una máquina activa', async () => {
    let activa = true;
    server.use(
      http.get(`${API_BASE}/maquinas/`, () =>
        HttpResponse.json(
          paginated([{ ...mockMaquina, activa }]),
        ),
      ),
      http.patch(`${API_BASE}/maquinas/:id/`, () => {
        activa = false;
        return HttpResponse.json({ ...mockMaquina, activa: false });
      }),
    );

    const user = userEvent.setup();
    renderWithProviders(<AdminMaquinasPage />);

    await screen.findByText(mockMaquina.codigo);
    await user.click(screen.getByRole('button', { name: 'Desactivar' }));

    await waitFor(() => {
      expect(screen.getByRole('button', { name: 'Activar' })).toBeInTheDocument();
    });
  });
});
