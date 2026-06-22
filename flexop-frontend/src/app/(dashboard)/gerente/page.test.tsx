import { screen } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { describe, expect, it } from 'vitest';
import GerenteDashboard from './page';
import { renderWithProviders } from '@/test/test-utils';
import { server } from '@/test/msw/server';
import { API_BASE } from '@/test/msw/constants';

describe('GerenteDashboard (MSW)', () => {
  it('muestra alerta cuando el dashboard falla', async () => {
    server.use(
      http.get(`${API_BASE}/dashboard/gerente/`, () =>
        HttpResponse.json({ detail: 'Error interno' }, { status: 500 }),
      ),
    );

    renderWithProviders(<GerenteDashboard />);

    expect(await screen.findByText('No se pudieron cargar los datos')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Reintentar/i })).toBeInTheDocument();
  });
});
