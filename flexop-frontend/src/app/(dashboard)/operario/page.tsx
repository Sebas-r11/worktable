'use client';

import { useQuery, useQueryClient } from '@tanstack/react-query';
import { reportesApi } from '@/lib/api';
import { operacionesApi } from '@/lib/api/operaciones';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Activity, Target, AlertCircle, CheckCircle } from 'lucide-react';
import { toast } from 'sonner';
import { DataFetchAlert } from '@/components/shared/DataFetchAlert';

export default function OperarioDashboard() {
  const qc = useQueryClient();
  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['dashboard', 'operario'],
    queryFn: () => reportesApi.dashboardOperario().then((r) => r.data),
    refetchInterval: 30_000,
  });

  const handleIniciarTarea = async () => {
    if (!data?.asignacion_activa) return;
    try {
      await operacionesApi.asignacionIniciar(data.asignacion_activa.id);
      toast.success('Tarea iniciada');
      await qc.invalidateQueries({ queryKey: ['dashboard'] });
      refetch();
    } catch {
      toast.error('Error al iniciar la tarea');
    }
  };

  const handleFinalizarTarea = async () => {
    if (!data?.asignacion_activa) return;
    try {
      await operacionesApi.asignacionFinalizar(data.asignacion_activa.id);
      toast.success('Tarea finalizada');
      await qc.invalidateQueries({ queryKey: ['dashboard'] });
      await qc.invalidateQueries({ queryKey: ['asignaciones'] });
      refetch();
    } catch {
      toast.error('Error al finalizar la tarea');
    }
  };

  if (isLoading) {
    return <div className="animate-pulse space-y-4"><div className="h-32 bg-slate-200 rounded-lg" /></div>;
  }

  if (isError) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold">Mi Dashboard</h1>
        <DataFetchAlert error={error} onRetry={() => refetch()} />
      </div>
    );
  }

  const eficiencia = data?.eficiencia_hoy ?? 0;
  const estadoAsignacion = data?.asignacion_activa?.estado ?? 'ACTIVA';
  const eficienciaColor =
    eficiencia >= 90 ? 'text-green-600' : eficiencia >= 70 ? 'text-yellow-600' : 'text-red-600';

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Mi Dashboard</h1>

      {/* Asignación activa */}
      {data?.asignacion_activa ? (
        <Card className="border-primary/30 bg-primary/5">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5 text-primary" />
              Asignación actual
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center gap-4">
              <Badge
                variant={
                  estadoAsignacion === 'ACTIVA' ? 'default' : 'secondary'
                }
              >
                {estadoAsignacion}
              </Badge>
              <span className="text-sm text-muted-foreground">
                Máquina: {data.asignacion_activa.maquina}
              </span>
              {data.asignacion_activa.turno && (
                <span className="text-sm text-muted-foreground">Turno: {data.asignacion_activa.turno}</span>
              )}
            </div>
            <div className="flex gap-3">
              {estadoAsignacion === 'PENDIENTE' && (
                <Button onClick={handleIniciarTarea} size="sm">
                  Iniciar tarea
                </Button>
              )}
              {estadoAsignacion === 'ACTIVA' && (
                <Button onClick={handleFinalizarTarea} variant="outline" size="sm">
                  Finalizar tarea
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardContent className="py-8 text-center text-muted-foreground">
            Sin asignación activa por el momento
          </CardContent>
        </Card>
      )}

      {/* KPIs */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Producción hoy
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{data?.produccion_hoy ?? 0}</p>
            <p className="text-xs text-muted-foreground">unidades</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Objetivo hoy
            </CardTitle>
          </CardHeader>
          <CardContent className="flex items-center gap-2">
            <Target className="h-4 w-4 text-muted-foreground" />
            <p className="text-2xl font-bold">{data?.objetivo_dia ?? 0}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Eficiencia
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className={`text-2xl font-bold ${eficienciaColor}`}>
              {eficiencia.toFixed(1)}%
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Incidencias abiertas
            </CardTitle>
          </CardHeader>
          <CardContent className="flex items-center gap-2">
            {(data?.incidencias_abiertas ?? 0) > 0 ? (
              <AlertCircle className="h-4 w-4 text-destructive" />
            ) : (
              <CheckCircle className="h-4 w-4 text-green-500" />
            )}
            <p className="text-2xl font-bold">{data?.incidencias_abiertas ?? 0}</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
