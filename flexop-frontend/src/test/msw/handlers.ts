import { http, HttpResponse } from 'msw';
import { API_BASE } from './constants';
import {
  mockAlertaActiva,
  mockDashboardOperario,
  mockDashboardGerente,
  mockDashboardSupervisor,
  mockColaDespacho,
  mockIncidencia,
  mockMaquina,
  mockMetrica,
  mockNotificacionNoLeida,
  mockOrden,
  mockOrdenEnProceso,
  mockRegistroProduccion,
  mockReporte,
  mockSugerenciaPendiente,
  mockSupervisorUser,
  mockTipoMaquina,
  mockUnidadEficiencia,
  mockUsuarioGerente,
  mockUsuarioOperario,
  paginated,
} from './fixtures';

export const handlers = [
  http.post(`${API_BASE}/auth/login/`, async ({ request }) => {
    const body = (await request.json()) as { username?: string; password?: string };
    if (body.username === 'bad' || body.password === 'wrong') {
      return HttpResponse.json({ detail: 'No active account found' }, { status: 401 });
    }
    return HttpResponse.json({
      access: 'test-access-token',
      refresh: 'test-refresh-token',
    });
  }),

  http.post(`${API_BASE}/auth/logout/`, () => HttpResponse.json({}, { status: 200 })),

  http.get(`${API_BASE}/usuarios/me/`, () => HttpResponse.json(mockSupervisorUser)),

  http.get(`${API_BASE}/alertas/`, ({ request }) => {
    const estado = new URL(request.url).searchParams.get('estado');
    const results = estado === 'ACTIVA' ? [mockAlertaActiva] : [mockAlertaActiva];
    return HttpResponse.json(paginated(results));
  }),

  http.post(`${API_BASE}/alertas/:id/resolver/`, ({ params }) =>
    HttpResponse.json({
      ...mockAlertaActiva,
      id: Number(params.id),
      estado: 'RESUELTA',
      fecha_resolucion: new Date().toISOString(),
    }),
  ),

  http.get(`${API_BASE}/notificaciones/`, () =>
    HttpResponse.json(paginated([mockNotificacionNoLeida])),
  ),

  http.post(`${API_BASE}/notificaciones/:id/marcar_leida/`, ({ params }) =>
    HttpResponse.json({
      ...mockNotificacionNoLeida,
      id: Number(params.id),
      leida: true,
    }),
  ),

  http.get(`${API_BASE}/sugerencias/`, ({ request }) => {
    const estado = new URL(request.url).searchParams.get('estado');
    const results = estado === 'PENDIENTE' ? [mockSugerenciaPendiente] : [mockSugerenciaPendiente];
    return HttpResponse.json(paginated(results));
  }),

  http.post(`${API_BASE}/sugerencias/:id/aceptar/`, ({ params }) =>
    HttpResponse.json({ ...mockSugerenciaPendiente, id: Number(params.id), estado: 'ACEPTADA' }),
  ),

  http.post(`${API_BASE}/sugerencias/:id/rechazar/`, async ({ params, request }) => {
    const body = (await request.json()) as { notas?: string };
    return HttpResponse.json({
      ...mockSugerenciaPendiente,
      id: Number(params.id),
      estado: 'RECHAZADA',
      notas_decision: body.notas,
    });
  }),

  http.get(`${API_BASE}/dashboard/supervisor/`, () =>
    HttpResponse.json(mockDashboardSupervisor),
  ),

  http.get(`${API_BASE}/dashboard/gerente/`, () =>
    HttpResponse.json(mockDashboardGerente),
  ),

  http.get(`${API_BASE}/metricas/`, () => HttpResponse.json(paginated([mockMetrica]))),

  http.get(`${API_BASE}/usuarios/`, () =>
    HttpResponse.json(paginated([mockUsuarioOperario, mockUsuarioGerente])),
  ),

  http.get(`${API_BASE}/tipos-maquina/`, () =>
    HttpResponse.json(paginated([mockTipoMaquina])),
  ),

  http.get(`${API_BASE}/unidades-eficiencia/`, () =>
    HttpResponse.json(paginated([mockUnidadEficiencia])),
  ),

  http.get(`${API_BASE}/maquinas/`, () => HttpResponse.json(paginated([mockMaquina]))),

  http.post(`${API_BASE}/maquinas/`, async ({ request }) => {
    const body = (await request.json()) as Partial<typeof mockMaquina>;
    return HttpResponse.json({ ...mockMaquina, ...body, id: 99 }, { status: 201 });
  }),

  http.patch(`${API_BASE}/maquinas/:id/`, async ({ params, request }) => {
    const body = (await request.json()) as Partial<typeof mockMaquina>;
    return HttpResponse.json({
      ...mockMaquina,
      id: Number(params.id),
      ...body,
    });
  }),

  http.get(`${API_BASE}/dashboard/operario/`, () =>
    HttpResponse.json(mockDashboardOperario),
  ),

  http.get(`${API_BASE}/produccion/`, () =>
    HttpResponse.json(paginated([mockRegistroProduccion])),
  ),

  http.post(`${API_BASE}/produccion/`, async ({ request }) => {
    const body = (await request.json()) as { cantidad?: number; observaciones?: string };
    return HttpResponse.json(
      {
        ...mockRegistroProduccion,
        id: 2,
        cantidad: body.cantidad ?? 1,
        observaciones: body.observaciones,
        fecha_hora: new Date().toISOString(),
      },
      { status: 201 },
    );
  }),

  http.get(`${API_BASE}/incidencias/`, () =>
    HttpResponse.json(paginated([mockIncidencia])),
  ),

  http.post(`${API_BASE}/incidencias/`, async ({ request }) => {
    const body = (await request.json()) as Partial<typeof mockIncidencia>;
    return HttpResponse.json(
      {
        ...mockIncidencia,
        id: 2,
        ...body,
        fecha_reporte: new Date().toISOString(),
      },
      { status: 201 },
    );
  }),

  http.post(`${API_BASE}/asignaciones/:id/iniciar/`, ({ params }) =>
    HttpResponse.json({
      id: Number(params.id),
      estado: 'ACTIVA',
      maquina: mockDashboardOperario.asignacion_activa?.maquina,
    }),
  ),

  http.post(`${API_BASE}/asignaciones/:id/finalizar/`, ({ params }) =>
    HttpResponse.json({
      id: Number(params.id),
      estado: 'COMPLETADA',
    }),
  ),

  http.post(`${API_BASE}/incidencias/:id/resolver/`, async ({ params, request }) => {
    const body = (await request.json()) as { solucion?: string };
    return HttpResponse.json({
      ...mockIncidencia,
      id: Number(params.id),
      estado: 'RESUELTA',
      solucion: body.solucion ?? '',
      fecha_resolucion: new Date().toISOString(),
    });
  }),

  http.get(`${API_BASE}/ordenes/`, () => HttpResponse.json(paginated([mockOrden]))),

  http.post(`${API_BASE}/ordenes/:id/iniciar/`, ({ params }) =>
    HttpResponse.json({ ...mockOrdenEnProceso, id: Number(params.id) }),
  ),

  http.post(`${API_BASE}/ordenes/:id/completar/`, ({ params }) =>
    HttpResponse.json({
      ...mockOrdenEnProceso,
      id: Number(params.id),
      estado: 'COMPLETADA',
      cantidad_producida: 100,
    }),
  ),

  http.get(`${API_BASE}/cola-despacho/pendientes/`, () =>
    HttpResponse.json([mockColaDespacho]),
  ),

  http.post(`${API_BASE}/cola-despacho/:id/despachar/`, ({ params }) =>
    HttpResponse.json({
      mensaje: 'Orden despachada',
      item: { ...mockColaDespacho, id: Number(params.id), estado: 'DESPACHADA' },
    }),
  ),

  http.post(`${API_BASE}/ordenes/`, async ({ request }) => {
    const body = (await request.json()) as Partial<typeof mockOrden>;
    return HttpResponse.json(
      {
        ...mockOrden,
        id: 99,
        ...body,
        numero_orden: 'ORD-2026-0099',
        estado: 'PENDIENTE',
        cantidad_producida: 0,
      },
      { status: 201 },
    );
  }),

  http.get(`${API_BASE}/reportes-generados/`, () =>
    HttpResponse.json(paginated([mockReporte])),
  ),

  http.get(`${API_BASE}/reportes-generados`, () =>
    HttpResponse.json(paginated([mockReporte])),
  ),

  http.get(`${API_BASE}/reportes-generados/:id/descargar/`, () =>
    new HttpResponse('Fecha,Eficiencia\n2026-05-28,80', {
      headers: { 'Content-Type': 'text/csv' },
    }),
  ),

  http.get(`${API_BASE}/exportar-csv/`, ({ request }) => {
    const url = new URL(request.url);
    if (!url.searchParams.get('tipo') || !url.searchParams.get('fecha_inicio')) {
      return HttpResponse.json({ error: 'Parametros requeridos' }, { status: 400 });
    }
    return new HttpResponse('Fecha,Operario,Maquina\n2026-05-28,Test,MAQ-001', {
      headers: { 'Content-Type': 'text/csv' },
    });
  }),
];
