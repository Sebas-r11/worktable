import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import { http, HttpResponse } from 'msw';
import GerenteMetricasPage from './page';
import { renderWithProviders } from '@/test/test-utils';
import { server } from '@/test/msw/server';
import { API_BASE } from '@/test/msw/constants';
import { mockMetrica, paginated } from '@/test/msw/fixtures';

describe('GerenteMetricasPage (MSW)', () => {
  it('muestra tabla de metricas con eficiencia calculada', async () => {
    renderWithProviders(<GerenteMetricasPage />);

    expect(await screen.findByText('Métricas de Eficiencia')).toBeInTheDocument();
    expect(screen.getAllByText(mockMetrica.maquina_nombre!).length).toBeGreaterThan(0);
    expect(screen.getAllByText('80.0%').length).toBeGreaterThan(0);
    expect(screen.getByTestId('metricas-chart')).toBeInTheDocument();
  });

  it('muestra estado vacio sin metricas', async () => {
    server.use(
      http.get(`${API_BASE}/metricas/`, () => HttpResponse.json(paginated([]))),
    );

    renderWithProviders(<GerenteMetricasPage />);
    expect(await screen.findByText('Sin métricas')).toBeInTheDocument();
  });

  it('pagina resultados cuando hay mas de una pagina', async () => {
    let requestedPage = 1;
    server.use(
      http.get(`${API_BASE}/metricas/`, ({ request }) => {
        const url = new URL(request.url);
        requestedPage = Number(url.searchParams.get('page') ?? 1);
        const item = { ...mockMetrica, id: requestedPage, maquina_nombre: `Máquina ${requestedPage}` };
        return HttpResponse.json({
          count: 45,
          next: requestedPage < 3 ? `?page=${requestedPage + 1}` : null,
          previous: requestedPage > 1 ? `?page=${requestedPage - 1}` : null,
          results: [item],
        });
      }),
    );

    const user = userEvent.setup();
    renderWithProviders(<GerenteMetricasPage />);

    expect(await screen.findByText('Máquina 1')).toBeInTheDocument();
    expect(screen.getByText(/Mostrando 1–20 de 45/)).toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: /Siguiente/i }));

    await waitFor(() => {
      expect(requestedPage).toBe(2);
      expect(screen.getByText('Máquina 2')).toBeInTheDocument();
    });
  });
});
