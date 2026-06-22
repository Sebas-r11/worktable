import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { http, HttpResponse } from 'msw';
import { describe, expect, it } from 'vitest';
import OperarioProduccionPage from './page';
import { renderWithProviders } from '@/test/test-utils';
import { server } from '@/test/msw/server';
import { API_BASE } from '@/test/msw/constants';
import { mockRegistroProduccion } from '@/test/msw/fixtures';

describe('OperarioProduccionPage (MSW)', () => {
  it('lista registros de producción', async () => {
    renderWithProviders(<OperarioProduccionPage />);

    expect(await screen.findByText('Registro de Producción')).toBeInTheDocument();
    expect(screen.getByText(String(mockRegistroProduccion.cantidad))).toBeInTheDocument();
    expect(screen.getByText('Turno mañana')).toBeInTheDocument();
    expect(screen.getByText('1 registros')).toBeInTheDocument();
  });

  it('habilita registrar con asignación activa', async () => {
    renderWithProviders(<OperarioProduccionPage />);

    await screen.findByText('Registro de Producción');
    const registrar = screen.getByRole('button', { name: /Registrar/i });
    expect(registrar).not.toBeDisabled();
    expect(
      screen.queryByText(/Necesitas una asignación activa/i),
    ).not.toBeInTheDocument();
  });

  it('pagina resultados cuando hay mas de una pagina', async () => {
    let requestedPage = 1;
    server.use(
      http.get(`${API_BASE}/produccion/`, ({ request }) => {
        const url = new URL(request.url);
        requestedPage = Number(url.searchParams.get('page') ?? 1);
        const item = {
          ...mockRegistroProduccion,
          id: requestedPage,
          cantidad: 100 + requestedPage,
          observaciones: `Página ${requestedPage}`,
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
    renderWithProviders(<OperarioProduccionPage />);

    expect(await screen.findByText('Página 1')).toBeInTheDocument();
    expect(screen.getByText(/Mostrando 1–20 de 45/)).toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: /Siguiente/i }));

    await waitFor(() => {
      expect(requestedPage).toBe(2);
      expect(screen.getByText('Página 2')).toBeInTheDocument();
    });
  });
});
