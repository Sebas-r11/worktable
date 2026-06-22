'use client';

import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useIncidencias, useMaquinas } from '@/hooks/useApi';
import { operacionesApi } from '@/lib/api/operaciones';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from '@/components/ui/table';
import {
  Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle,
} from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { StatusBadge } from '@/components/shared/StatusBadge';
import { PageLoader } from '@/components/shared/LoadingSpinner';
import { EmptyState } from '@/components/shared/EmptyState';
import { PaginationBar } from '@/components/shared/PaginationBar';
import { AlertCircle, CheckCircle } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';

export default function SupervisorIncidenciasPage() {
  const qc = useQueryClient();
  const [page, setPage] = useState(1);
  const { data, isLoading } = useIncidencias({ page });
  const { data: maquinas } = useMaquinas();
  const [resolveTarget, setResolveTarget] = useState<number | null>(null);
  const [solucion, setSolucion] = useState('');

  const resolver = useMutation({
    mutationFn: ({ id, solucion: texto }: { id: number; solucion: string }) =>
      operacionesApi.incidenciaResolver(id, texto),
    onSuccess: () => {
      toast.success('Incidencia resuelta');
      setResolveTarget(null);
      setSolucion('');
      qc.invalidateQueries({ queryKey: ['incidencias'] });
      qc.invalidateQueries({ queryKey: ['dashboard'] });
    },
    onError: () => toast.error('Error al resolver incidencia'),
  });

  const openResolveDialog = (id: number) => {
    setResolveTarget(id);
    setSolucion('');
  };

  const submitResolve = () => {
    if (resolveTarget == null) return;
    const texto = solucion.trim();
    if (!texto) {
      toast.error('Indica la solución aplicada');
      return;
    }
    resolver.mutate({ id: resolveTarget, solucion: texto });
  };

  if (isLoading) return <PageLoader />;

  const incidencias = data?.results ?? [];
  const abiertas = incidencias.filter((i) => i.estado === 'ABIERTA' || i.estado === 'EN_PROCESO');

  const maquinaMap = Object.fromEntries((maquinas?.results ?? []).map((m) => [m.id, m.nombre]));

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <AlertCircle className="h-6 w-6" /> Incidencias
          {abiertas.length > 0 && (
            <Badge variant="destructive" className="ml-1">{abiertas.length}</Badge>
          )}
        </h1>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm text-muted-foreground">
            {data?.count ?? 0} incidencias totales · {abiertas.length} abiertas
          </CardTitle>
        </CardHeader>
        <CardContent>
          {incidencias.length === 0 ? (
            <EmptyState
              icon={AlertCircle}
              title="Sin incidencias"
              description="No hay incidencias registradas."
            />
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Título</TableHead>
                  <TableHead>Máquina</TableHead>
                  <TableHead>Prioridad</TableHead>
                  <TableHead>Estado</TableHead>
                  <TableHead>Fecha</TableHead>
                  <TableHead className="text-right">Acción</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {incidencias.map((inc) => (
                  <TableRow key={inc.id}>
                    <TableCell className="font-medium">{inc.titulo}</TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {inc.maquina_nombre ?? maquinaMap[inc.maquina] ?? `#${inc.maquina}`}
                    </TableCell>
                    <TableCell>
                      <StatusBadge value={inc.prioridad} />
                    </TableCell>
                    <TableCell>
                      <StatusBadge value={inc.estado} />
                    </TableCell>
                    <TableCell className="text-xs text-muted-foreground">
                      {new Date(inc.fecha_reporte).toLocaleString('es')}
                    </TableCell>
                    <TableCell className="text-right">
                      {(inc.estado === 'ABIERTA' || inc.estado === 'EN_PROCESO') && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => openResolveDialog(inc.id)}
                          disabled={resolver.isPending}
                        >
                          <CheckCircle className="h-3 w-3 mr-1" />
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

      <Dialog
        open={resolveTarget != null}
        onOpenChange={(open) => {
          if (!open) {
            setResolveTarget(null);
            setSolucion('');
          }
        }}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Resolver incidencia</DialogTitle>
            <DialogDescription>
              Describe la solución aplicada. Este texto queda registrado en el sistema.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-2">
            <Label htmlFor="solucion">Solución</Label>
            <textarea
              id="solucion"
              className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              value={solucion}
              onChange={(e) => setSolucion(e.target.value)}
              placeholder="Ej.: Se reinició el equipo y se reemplazó el sensor."
              rows={4}
            />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setResolveTarget(null)}>
              Cancelar
            </Button>
            <Button onClick={submitResolve} disabled={resolver.isPending}>
              Confirmar resolución
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
