import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { http, HttpResponse } from 'msw';
import { describe, expect, it, vi, beforeEach } from 'vitest';
import { reportesApi } from '@/lib/api';
import { createTestQueryClient, renderWithProviders } from '@/test/test-utils';
import { server } from '@/test/msw/server';
import { API_BASE } from '@/test/msw/constants';
import { mockReporte, paginated } from '@/test/msw/fixtures';

describe('GerenteReportesPage (MSW)', () => {
  it('lista reportes generados', async () => {
    const { default: GerenteReportesPage } = await import('./page');
    const queryClient = createTestQueryClient();
    await queryClient.prefetchQuery({
      queryKey: ['reportes-generados'],
      queryFn: async () => {
        const response = await reportesApi.reportesGenerados();
        return response.data;
      },
    });

    renderWithProviders(<GerenteReportesPage />, { queryClient });

    expect(await screen.findByText('Reportes')).toBeInTheDocument();
    expect(screen.getByText(new RegExp(`${mockReporte.tipo_display!} #${mockReporte.id}`))).toBeInTheDocument();
  });

  it('exportarCSV via API con query params', async () => {
    let capturedTipo = '';
    server.use(
      http.get(`${API_BASE}/exportar-csv/`, ({ request }) => {
        capturedTipo = new URL(request.url).searchParams.get('tipo') ?? '';
        return HttpResponse.text('Fecha,Eficiencia\n2026-05-28,80', {
          headers: { 'Content-Type': 'text/csv' },
        });
      }),
    );

    await reportesApi.exportarCSV({
      tipo: 'eficiencia',
      fecha_inicio: '2026-05-01',
      fecha_fin: '2026-05-28',
    });

    expect(capturedTipo).toBe('eficiencia');
  });

  it('muestra estado vacio sin historial', async () => {
    server.use(
      http.get(`${API_BASE}/reportes-generados/`, () => HttpResponse.json(paginated([]))),
      http.get(`${API_BASE}/reportes-generados`, () => HttpResponse.json(paginated([]))),
    );

    const { default: GerenteReportesPage } = await import('./page');
    renderWithProviders(<GerenteReportesPage />);
    expect(await screen.findByText('Sin reportes')).toBeInTheDocument();
  });
});
