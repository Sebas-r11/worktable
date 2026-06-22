import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { http, HttpResponse } from 'msw';
import { describe, expect, it } from 'vitest';
import SupervisorSugerenciasPage from './page';
import { renderWithProviders } from '@/test/test-utils';
import { server } from '@/test/msw/server';
import { API_BASE } from '@/test/msw/constants';
import { mockSugerenciaPendiente, paginated } from '@/test/msw/fixtures';

describe('SupervisorSugerenciasPage (MSW)', () => {
  it('muestra sugerencia con labels del API', async () => {
    renderWithProviders(<SupervisorSugerenciasPage />);

    expect(await screen.findByText('Sugerencias de Reasignación')).toBeInTheDocument();
    expect(screen.getByText(mockSugerenciaPendiente.razon_display!)).toBeInTheDocument();
    expect(screen.getByText('EMP-001')).toBeInTheDocument();
    expect(screen.getByText('MAQ-002')).toBeInTheDocument();
    expect(screen.getByText('+15.2%')).toBeInTheDocument();
  });

  it('acepta sugerencia pendiente', async () => {
    let aceptada = false;
    server.use(
      http.get(`${API_BASE}/sugerencias/`, () => {
        const item = aceptada
          ? { ...mockSugerenciaPendiente, estado: 'ACEPTADA' as const }
          : mockSugerenciaPendiente;
        return HttpResponse.json(paginated([item]));
      }),
      http.post(`${API_BASE}/sugerencias/:id/aceptar/`, () => {
        aceptada = true;
        return HttpResponse.json({ ...mockSugerenciaPendiente, estado: 'ACEPTADA' });
      }),
    );

    const user = userEvent.setup();
    renderWithProviders(<SupervisorSugerenciasPage />);

    await screen.findByText(mockSugerenciaPendiente.razon_display!);
    await user.click(screen.getByRole('button', { name: 'Aceptar' }));

    await waitFor(() => {
      expect(screen.getByText('ACEPTADA')).toBeInTheDocument();
    });
  });

  it('pagina resultados cuando hay mas de una pagina', async () => {
    let requestedPage = 1;
    server.use(
      http.get(`${API_BASE}/sugerencias/`, ({ request }) => {
        const url = new URL(request.url);
        requestedPage = Number(url.searchParams.get('page') ?? 1);
        const item = {
          ...mockSugerenciaPendiente,
          id: requestedPage,
          razon_display: `Razón página ${requestedPage}`,
        };
        return HttpResponse.json({
          count: 45,
          next: requestedPage < 3 ? `?page=${requestedPage + 1}` : null,
          previous: requestedPage > 1 ? `?page=${requestedPage - 1}` : null,
          results: [item],
        });
      }),
    );

    const user = userEvent.setup();
    renderWithProviders(<SupervisorSugerenciasPage />);

    expect(await screen.findByText('Razón página 1')).toBeInTheDocument();
    expect(screen.getByText(/Mostrando 1–20 de 45/)).toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: /Siguiente/i }));

    await waitFor(() => {
      expect(requestedPage).toBe(2);
      expect(screen.getByText('Razón página 2')).toBeInTheDocument();
    });
  });
});
