import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { renderHook, waitFor } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import {
  useAlertas,
  useMetricas,
  useOrdenes,
  useSugerencias,
  useDashboardSupervisor,
  useRechazarSugerencia,
} from './useApi';
import {
  mockAlertaActiva,
  mockDashboardSupervisor,
  mockMetrica,
  mockOrden,
  mockSugerenciaPendiente,
} from '@/test/msw/fixtures';

function wrapper({ children }: { children: React.ReactNode }) {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
}

describe('useApi hooks (MSW)', () => {
  it('useOrdenes carga listado', async () => {
    const { result } = renderHook(() => useOrdenes(), { wrapper });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data?.results[0].numero_orden).toBe(mockOrden.numero_orden);
  });

  it('useAlertas filtra por estado ACTIVA', async () => {
    const { result } = renderHook(() => useAlertas({ estado: 'ACTIVA' }), { wrapper });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data?.results[0].titulo).toBe(mockAlertaActiva.titulo);
  });

  it('useMetricas carga eficiencia_calculada', async () => {
    const { result } = renderHook(() => useMetricas(), { wrapper });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data?.results[0].eficiencia_calculada).toBe(mockMetrica.eficiencia_calculada);
  });

  it('useSugerencias carga sugerencias pendientes', async () => {
    const { result } = renderHook(() => useSugerencias({ estado: 'PENDIENTE' }), { wrapper });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data?.results[0].operario_codigo).toBe(mockSugerenciaPendiente.operario_codigo);
  });

  it('useDashboardSupervisor carga KPIs', async () => {
    const { result } = renderHook(() => useDashboardSupervisor(), { wrapper });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data?.alertas_activas).toBe(mockDashboardSupervisor.alertas_activas);
  });

  it('useRechazarSugerencia envia notas al API', async () => {
    const { result } = renderHook(() => useRechazarSugerencia(), { wrapper });
    result.current.mutate(5);
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    const body = result.current.data as { data?: { estado: string } };
    expect(body.data?.estado).toBe('RECHAZADA');
  });
});
