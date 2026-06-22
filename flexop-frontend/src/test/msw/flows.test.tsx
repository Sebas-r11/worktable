import { screen, waitFor } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { http, HttpResponse } from 'msw';
import SupervisorDashboard from '@/app/(dashboard)/supervisor/page';
import { renderWithProviders } from '@/test/test-utils';
import { server } from './server';
import { API_BASE } from './constants';
import { mockAlertaActiva, mockSugerenciaPendiente, paginated } from './fixtures';
import { getAlertaTexto, getSugerenciaRazonLabel } from '@/lib/display/entities';

/**
 * Flujo multi-endpoint: el dashboard supervisor dispara en paralelo
 * dashboard, alertas activas y sugerencias pendientes.
 */
describe('MSW — flujos multi-endpoint', () => {
  it('dashboard supervisor carga alertas y sugerencias en paralelo', async () => {
    renderWithProviders(<SupervisorDashboard />);

    await waitFor(() => {
      expect(screen.getByText('Dashboard Supervisor')).toBeInTheDocument();
    });

    expect(await screen.findByText(getAlertaTexto(mockAlertaActiva))).toBeInTheDocument();
    expect(screen.getByText(getSugerenciaRazonLabel(mockSugerenciaPendiente))).toBeInTheDocument();
    expect(screen.getAllByText('Alertas activas').length).toBeGreaterThan(0);
  });

  it('dashboard sin alertas activas muestra estado vacío', async () => {
    server.use(
      http.get(`${API_BASE}/alertas/`, () => HttpResponse.json(paginated([]))),
      http.get(`${API_BASE}/dashboard/supervisor/`, () =>
        HttpResponse.json({
          maquinas_estado: [],
          alertas_activas: 0,
          alertas_criticas: 0,
          sugerencias_pendientes: 0,
          eficiencia_turno: 0,
          ranking_operarios: [],
          incidencias_abiertas: 0,
        }),
      ),
    );

    renderWithProviders(<SupervisorDashboard />);

    await waitFor(() => {
      expect(screen.getByText('Sin alertas activas')).toBeInTheDocument();
    });
  });
});
