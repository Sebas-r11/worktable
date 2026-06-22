'use client';

import { useState } from 'react';
import { useAlertas, useResolverAlerta } from '@/hooks/useApi';
import { alertasApi } from '@/lib/api';
import { useQueryClient, useMutation } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from '@/components/ui/table';
import { StatusBadge } from '@/components/shared/StatusBadge';
import { PageLoader } from '@/components/shared/LoadingSpinner';
import { EmptyState } from '@/components/shared/EmptyState';
import { PaginationBar } from '@/components/shared/PaginationBar';
import { Bell, CheckCircle } from 'lucide-react';
import { toast } from 'sonner';
import { formatFechaApi } from '@/lib/display/entities';

export default function SupervisorAlertasPage() {
  const qc = useQueryClient();
  const [page, setPage] = useState(1);
  const { data, isLoading } = useAlertas({ page });
  const resolverAlerta = useResolverAlerta();

  const resolverTodas = useMutation({
    mutationFn: async () => {
      const activas = data?.results.filter((a) => a.estado === 'ACTIVA') ?? [];
      const results = await Promise.allSettled(
        activas.map((a) => alertasApi.alertaResolver(a.id)),
      );
      const fallidas = results.filter((r) => r.status === 'rejected').length;
      if (fallidas > 0) {
        throw new Error(`${fallidas} alertas no pudieron resolverse`);
      }
    },
    onSuccess: () => {
      toast.success('Todas las alertas resueltas');
      qc.invalidateQueries({ queryKey: ['alertas'] });
      qc.invalidateQueries({ queryKey: ['dashboard'] });
      qc.invalidateQueries({ queryKey: ['notificaciones'] });
    },
    onError: (err) => {
      const msg = err instanceof Error ? err.message : 'Error al resolver alertas';
      toast.error(msg);
      qc.invalidateQueries({ queryKey: ['alertas'] });
      qc.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });

  if (isLoading) return <PageLoader />;

  const alertas = data?.results ?? [];
  const activas = alertas.filter((a) => a.estado === 'ACTIVA');

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Bell className="h-6 w-6" /> Alertas
          {activas.length > 0 && (
            <Badge variant="destructive" className="ml-1">{activas.length}</Badge>
          )}
        </h1>
        {activas.length > 0 && (
          <Button
            size="sm"
            variant="outline"
            onClick={() => resolverTodas.mutate()}
            disabled={resolverTodas.isPending}
          >
            <CheckCircle className="h-4 w-4 mr-2" />
            Resolver todas
          </Button>
        )}
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm text-muted-foreground">
            {data?.count ?? 0} alertas totales · {activas.length} activas
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          {alertas.length === 0 ? (
            <EmptyState
              title="Sin alertas"
              description="El sistema no ha generado alertas"
              icon={Bell}
              className="py-16"
            />
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Alerta</TableHead>
                  <TableHead>Prioridad</TableHead>
                  <TableHead>Estado</TableHead>
                  <TableHead>Creada</TableHead>
                  <TableHead className="text-right">Acción</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {alertas.map((alerta) => (
                  <TableRow key={alerta.id}>
                    <TableCell className="max-w-[300px]">
                      <p className="text-sm font-medium">{alerta.titulo}</p>
                      {alerta.descripcion && alerta.descripcion !== alerta.titulo && (
                        <p className="text-xs text-muted-foreground">{alerta.descripcion}</p>
                      )}
                    </TableCell>
                    <TableCell><StatusBadge value={alerta.prioridad} /></TableCell>
                    <TableCell><StatusBadge value={alerta.estado} /></TableCell>
                    <TableCell className="text-xs text-muted-foreground">
                      {formatFechaApi(alerta.fecha_creacion)}
                    </TableCell>
                    <TableCell className="text-right">
                      {alerta.estado === 'ACTIVA' && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => {
                            resolverAlerta.mutate(alerta.id, {
                              onSuccess: () => toast.success('Alerta resuelta'),
                              onError: () => toast.error('Error'),
                            });
                          }}
                          disabled={resolverAlerta.isPending}
                        >
                          Resolver
                        </Button>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
          <PaginationBar
            page={page}
            total={data?.count ?? 0}
            onPageChange={setPage}
          />
        </CardContent>
      </Card>
    </div>
  );
}
