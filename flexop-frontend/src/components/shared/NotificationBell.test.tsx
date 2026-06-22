import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { http, HttpResponse } from 'msw';
import { describe, expect, it } from 'vitest';
import { NotificationBell } from './NotificationBell';
import { renderWithProviders } from '@/test/test-utils';
import { server } from '@/test/msw/server';
import { API_BASE } from '@/test/msw/constants';
import { mockNotificacionNoLeida, paginated } from '@/test/msw/fixtures';

describe('NotificationBell (MSW)', () => {
  it('muestra mensaje sin notificaciones nuevas', async () => {
    server.use(
      http.get(`${API_BASE}/notificaciones/`, () => HttpResponse.json(paginated([]))),
    );

    const user = userEvent.setup();
    renderWithProviders(<NotificationBell />);

    await user.click(screen.getByRole('button'));
    expect(await screen.findByText('Sin notificaciones nuevas')).toBeInTheDocument();
  });

  it('muestra badge y titulos de no leidas', async () => {
    const user = userEvent.setup();
    renderWithProviders(<NotificationBell />);

    expect(await screen.findByText('1')).toBeInTheDocument();

    await user.click(screen.getByRole('button'));
    expect(await screen.findByText(mockNotificacionNoLeida.titulo)).toBeInTheDocument();
    expect(screen.getByText(mockNotificacionNoLeida.mensaje)).toBeInTheDocument();
  });

  it('marca notificacion como leida al hacer click', async () => {
    let marcada = false;

    server.use(
      http.post(`${API_BASE}/notificaciones/:id/marcar_leida/`, ({ params }) => {
        marcada = true;
        return HttpResponse.json({
          ...mockNotificacionNoLeida,
          id: Number(params.id),
          leida: true,
        });
      }),
      http.get(`${API_BASE}/notificaciones/`, () =>
        HttpResponse.json(
          paginated(marcada ? [] : [mockNotificacionNoLeida]),
        ),
      ),
    );

    const user = userEvent.setup();
    renderWithProviders(<NotificationBell />);

    await user.click(screen.getByRole('button'));
    await user.click(await screen.findByText(mockNotificacionNoLeida.titulo));

    expect(marcada).toBe(true);
  });
});
