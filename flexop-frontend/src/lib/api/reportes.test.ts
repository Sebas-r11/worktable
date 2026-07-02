import { describe, expect, it } from 'vitest';
import { http, HttpResponse } from 'msw';
import { server } from '@/test/msw/server';
import { API_BASE } from '@/test/msw/constants';
import { reportesApi, reasignacionesApi } from './index';

describe('reportesApi (MSW)', () => {
  it('exportarCSV llama /exportar-csv/ con query params', async () => {
    let capturedTipo = '';
    server.use(
      http.get(`${API_BASE}/exportar-csv/`, ({ request }) => {
        capturedTipo = new URL(request.url).searchParams.get('tipo') ?? '';
        return new HttpResponse('Fecha,Operario\n', {
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
});

describe('reasignacionesApi (MSW)', () => {
  it('sugerenciaRechazar envia notas en el body', async () => {
    let body: { notas?: string } = {};
    server.use(
      http.post(`${API_BASE}/sugerencias/:id/rechazar/`, async ({ request }) => {
        body = (await request.json()) as { notas?: string };
        return HttpResponse.json({ id: 7, estado: 'RECHAZADA' });
      }),
    );

    await reasignacionesApi.sugerenciaRechazar(7, 'No aplica hoy');
    expect(body.notas).toBe('No aplica hoy');
  });
});
