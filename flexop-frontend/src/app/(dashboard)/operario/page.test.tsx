import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { http, HttpResponse } from 'msw';
import { describe, expect, it } from 'vitest';
import OperarioDashboard from './page';
import { renderWithProviders } from '@/test/test-utils';
import { server } from '@/test/msw/server';
import { API_BASE } from '@/test/msw/constants';
import { mockDashboardOperario } from '@/test/msw/fixtures';

describe('OperarioDashboard (MSW)', () => {
  it('muestra asignación pendiente y KPIs', async () => {
    renderWithProviders(<OperarioDashboard />);

    expect(await screen.findByText('Mi Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Asignación actual')).toBeInTheDocument();
    expect(screen.getByText('PENDIENTE')).toBeInTheDocument();
    expect(screen.getByText(/Llenadora 1/)).toBeInTheDocument();
    expect(screen.getByText('120')).toBeInTheDocument();
    expect(screen.getByText('200')).toBeInTheDocument();
    expect(screen.getByText('88.5%')).toBeInTheDocument();
    expect(screen.getByText('1')).toBeInTheDocument();
  });

  it('inicia tarea cuando la asignación está pendiente', async () => {
    let estado = 'PENDIENTE';
    server.use(
      http.get(`${API_BASE}/dashboard/operario/`, () =>
        HttpResponse.json({
          ...mockDashboardOperario,
          asignacion_activa: {
            ...mockDashboardOperario.asignacion_activa!,
            estado,
          },
        }),
      ),
      http.post(`${API_BASE}/asignaciones/:id/iniciar/`, () => {
        estado = 'ACTIVA';
        return HttpResponse.json({ id: 10, estado: 'ACTIVA' });
      }),
    );

    const user = userEvent.setup();
    renderWithProviders(<OperarioDashboard />);

    await screen.findByRole('button', { name: 'Iniciar tarea' });
    await user.click(screen.getByRole('button', { name: 'Iniciar tarea' }));

    await waitFor(() => {
      expect(screen.getByRole('button', { name: 'Finalizar tarea' })).toBeInTheDocument();
    });
  });

  it('muestra mensaje sin asignación activa', async () => {
    server.use(
      http.get(`${API_BASE}/dashboard/operario/`, () =>
        HttpResponse.json({
          ...mockDashboardOperario,
          asignacion_activa: null,
        }),
      ),
    );

    renderWithProviders(<OperarioDashboard />);

    expect(
      await screen.findByText('Sin asignación activa por el momento'),
    ).toBeInTheDocument();
  });

  it('muestra alerta cuando el dashboard falla', async () => {
    server.use(
      http.get(`${API_BASE}/dashboard/operario/`, () =>
        HttpResponse.json({ detail: 'Error interno' }, { status: 500 }),
      ),
    );

    renderWithProviders(<OperarioDashboard />);

    expect(await screen.findByText('No se pudieron cargar los datos')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Reintentar/i })).toBeInTheDocument();
  });
});
