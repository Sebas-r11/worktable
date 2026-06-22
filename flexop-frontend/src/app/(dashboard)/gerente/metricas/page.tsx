'use client';

import { useState } from 'react';
import { useMetricas, useMaquinas } from '@/hooks/useApi';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from '@/components/ui/table';
import { PageLoader } from '@/components/shared/LoadingSpinner';
import { EmptyState } from '@/components/shared/EmptyState';
import { PaginationBar } from '@/components/shared/PaginationBar';
import { BarChart3 } from 'lucide-react';
import { getMetricaEficiencia, getMetricaObjetivo } from '@/lib/display/entities';
import { MetricasChart, type MetricasChartPoint } from './MetricasChart';

function eficienciaColor(v: number) {
  if (v >= 90) return 'text-green-600';
  if (v >= 70) return 'text-yellow-600';
  return 'text-red-600';
}

export default function GerenteMetricasPage() {
  const [page, setPage] = useState(1);
  const { data, isLoading } = useMetricas({ page });
  const { data: maquinas } = useMaquinas();

  if (isLoading) return <PageLoader />;

  const metricas = data?.results ?? [];
  const maquinaMap = Object.fromEntries((maquinas?.results ?? []).map((m) => [m.id, m.nombre]));

  const chartData: MetricasChartPoint[] = metricas.map((m) => ({
    nombre: m.maquina_nombre ?? maquinaMap[m.maquina] ?? `M${m.maquina}`,
    eficiencia: parseFloat(getMetricaEficiencia(m).toFixed(1)),
  }));

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold flex items-center gap-2">
        <BarChart3 className="h-6 w-6" /> Métricas de Eficiencia
      </h1>

      {chartData.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Eficiencia por máquina</CardTitle>
          </CardHeader>
          <CardContent>
            <MetricasChart data={chartData} />
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="text-sm text-muted-foreground">
            {data?.count ?? 0} registros de métricas
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          {metricas.length === 0 ? (
            <EmptyState title="Sin métricas" description="Aún no hay datos de eficiencia calculados" icon={BarChart3} className="py-16" />
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Máquina</TableHead>
                  <TableHead>Eficiencia</TableHead>
                  <TableHead>Real</TableHead>
                  <TableHead>Teórica</TableHead>
                  <TableHead>Fecha</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {metricas.map((m) => (
                  <TableRow key={m.id}>
                    <TableCell className="font-medium">{m.maquina_nombre ?? maquinaMap[m.maquina] ?? `#${m.maquina}`}</TableCell>
                    <TableCell>
                      <span className={`font-bold ${eficienciaColor(getMetricaEficiencia(m))}`}>
                        {getMetricaEficiencia(m).toFixed(1)}%
                      </span>
                    </TableCell>
                    <TableCell>{m.produccion_real}{m.unidad ? ` ${m.unidad}` : ''}</TableCell>
                    <TableCell>{getMetricaObjetivo(m)}</TableCell>
                    <TableCell className="text-xs text-muted-foreground">{m.fecha}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
          <div className="px-6 pb-4">
            <PaginationBar
              page={page}
              total={data?.count ?? 0}
              onPageChange={setPage}
            />
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
