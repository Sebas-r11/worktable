import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { http, HttpResponse } from 'msw';
import { describe, expect, it } from 'vitest';
import SupervisorAlertasPage from './page';
import { renderWithProviders } from '@/test/test-utils';
import { server } from '@/test/msw/server';
import { API_BASE } from '@/test/msw/constants';
import { mockAlertaActiva, paginated } from '@/test/msw/fixtures';

describe('SupervisorAlertasPage (MSW)', () => {
  it('lista alertas con titulo y estado', async () => {
    renderWithProviders(<SupervisorAlertasPage />);

    expect(await screen.findByText('Alertas')).toBeInTheDocument();
    expect(screen.getByText(mockAlertaActiva.titulo)).toBeInTheDocument();
    expect(screen.getByText('ALTA')).toBeInTheDocument();
    expect(screen.getByText('ACTIVA')).toBeInTheDocument();
  });

  it('resuelve una alerta activa', async () => {
    let resuelta = false;
    server.use(
      http.get(`${API_BASE}/alertas/`, () => {
        const alerta = resuelta
          ? { ...mockAlertaActiva, estado: 'RESUELTA' as const }
          : mockAlertaActiva;
        return HttpResponse.json(paginated([alerta]));
      }),
      http.post(`${API_BASE}/alertas/:id/resolver/`, () => {
        resuelta = true;
        return HttpResponse.json({ ...mockAlertaActiva, estado: 'RESUELTA' });
      }),
    );

    const user = userEvent.setup();
    renderWithProviders(<SupervisorAlertasPage />);

    await screen.findByText(mockAlertaActiva.titulo);
    await user.click(screen.getByRole('button', { name: 'Resolver' }));

    await waitFor(() => {
      expect(screen.getByText('RESUELTA')).toBeInTheDocument();
    });
  });
});
