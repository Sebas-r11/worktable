import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { http, HttpResponse } from 'msw';
import { beforeEach, describe, expect, it } from 'vitest';
import GerenteOrdenesPage from './page';
import { renderWithProviders } from '@/test/test-utils';
import { server } from '@/test/msw/server';
import { API_BASE } from '@/test/msw/constants';
import {
  mockColaDespacho,
  mockOrdenEnProceso,
  mockGerenteUser,
  paginated,
} from '@/test/msw/fixtures';
import { useAuthStore } from '@/stores/authStore';

describe('GerenteOrdenesPage (MSW)', () => {
  beforeEach(() => {
    useAuthStore.setState({
      user: mockGerenteUser,
      isAuthenticated: true,
      isLoading: false,
      error: null,
    });
  });

  it('completar orden refresca la cola de despacho', async () => {
    let colaCalls = 0;

    server.use(
      http.get(`${API_BASE}/ordenes/`, () =>
        HttpResponse.json(paginated([mockOrdenEnProceso])),
      ),
      http.get(`${API_BASE}/cola-despacho/pendientes/`, () => {
        colaCalls += 1;
        if (colaCalls === 1) {
          return HttpResponse.json([mockColaDespacho]);
        }
        return HttpResponse.json([]);
      }),
      http.post(`${API_BASE}/cola-despacho/:id/despachar/`, () =>
        HttpResponse.json({ mensaje: 'Orden despachada' }),
      ),
      http.post(`${API_BASE}/ordenes/:id/completar/`, () =>
        HttpResponse.json({ ...mockOrdenEnProceso, estado: 'COMPLETADA' }),
      ),
    );

    const user = userEvent.setup();
    renderWithProviders(<GerenteOrdenesPage />);

    expect(await screen.findByText(/Cola de despacho/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Despachar/i })).toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: /Completar/i }));

    await waitFor(() => {
      expect(screen.getByText('Cola de despacho vacía')).toBeInTheDocument();
    });
    expect(colaCalls).toBeGreaterThan(1);
  });
});
