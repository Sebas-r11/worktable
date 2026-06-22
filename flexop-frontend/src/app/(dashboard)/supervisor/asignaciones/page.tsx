'use client';

import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useAsignaciones, useMaquinas, useOperarios, useTurnos } from '@/hooks/useApi';
import { operacionesApi } from '@/lib/api/operaciones';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from '@/components/ui/select';
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger,
} from '@/components/ui/dialog';
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from '@/components/ui/table';
import { StatusBadge } from '@/components/shared/StatusBadge';
import { PaginationBar } from '@/components/shared/PaginationBar';
import { PageLoader } from '@/components/shared/LoadingSpinner';
import { EmptyState } from '@/components/shared/EmptyState';
import { Activity, Play, Square, Plus } from 'lucide-react';
import { toast } from 'sonner';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';

const schema = z.object({
  operario: z.string().min(1, 'Selecciona un operario'),
  maquina: z.string().min(1, 'Selecciona una máquina'),
  turno: z.string().min(1, 'Selecciona un turno'),
  fecha: z.string().min(1, 'Selecciona una fecha'),
  observaciones: z.string().optional(),
});
type FormData = z.infer<typeof schema>;

export default function SupervisorAsignacionesPage() {
  const qc = useQueryClient();
  const [open, setOpen] = useState(false);
  const [page, setPage] = useState(1);
  const { data, isLoading } = useAsignaciones({ page });
  const { data: maquinas } = useMaquinas();
  const { data: operarios } = useOperarios();
  const { data: turnos } = useTurnos();

  const { register, handleSubmit, setValue, watch, reset, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { fecha: new Date().toISOString().slice(0, 10) },
  });

  const operarioId = watch('operario');
  const maquinaId = watch('maquina');
  const turnoId = watch('turno');

  const crear = useMutation({
    mutationFn: (values: FormData) =>
      operacionesApi.asignacionCreate({
        operario: Number(values.operario),
        maquina: Number(values.maquina),
        turno: Number(values.turno),
        fecha: values.fecha,
        observaciones: values.observaciones,
      }),
    onSuccess: () => {
      toast.success('Asignación creada');
      qc.invalidateQueries({ queryKey: ['asignaciones'] });
      reset();
      setOpen(false);
    },
    onError: (err: unknown) => {
      const msg = (err as { response?: { data?: { detail?: string; operario?: string[] } } })?.response?.data;
      toast.error(msg?.operario?.[0] ?? msg?.detail ?? 'Error al crear asignación');
    },
  });

  const iniciar = useMutation({
    mutationFn: (id: number) => operacionesApi.asignacionIniciar(id),
    onSuccess: () => { toast.success('Asignación iniciada'); qc.invalidateQueries({ queryKey: ['asignaciones'] }); },
    onError: () => toast.error('Error al iniciar'),
  });

  const finalizar = useMutation({
    mutationFn: (id: number) => operacionesApi.asignacionFinalizar(id),
    onSuccess: () => { toast.success('Asignación finalizada'); qc.invalidateQueries({ queryKey: ['asignaciones'] }); },
    onError: () => toast.error('Error al finalizar'),
  });

  if (isLoading) return <PageLoader />;
  const asignaciones = data?.results ?? [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Activity className="h-6 w-6" /> Asignaciones
        </h1>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button size="sm"><Plus className="h-4 w-4 mr-2" /> Nueva asignación</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>Nueva asignación</DialogTitle></DialogHeader>
            <form onSubmit={handleSubmit((d) => crear.mutate(d))} className="space-y-4">
              <div className="space-y-2">
                <Label>Operario</Label>
                <Select
                  value={operarioId}
                  onValueChange={(v) => setValue('operario', v, { shouldValidate: true })}
                >
                  <SelectTrigger><SelectValue placeholder="Seleccionar operario..." /></SelectTrigger>
                  <SelectContent>
                    {(operarios?.results ?? []).map((op) => (
                      <SelectItem key={op.id} value={String(op.id)}>
                        {op.usuario_nombre ?? `#${op.usuario}`}{op.codigo_empleado ? ` (${op.codigo_empleado})` : ''}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {errors.operario && <p className="text-xs text-destructive">{errors.operario.message}</p>}
              </div>
              <div className="space-y-2">
                <Label>Máquina</Label>
                <Select
                  value={maquinaId}
                  onValueChange={(v) => setValue('maquina', v, { shouldValidate: true })}
                >
                  <SelectTrigger><SelectValue placeholder="Seleccionar máquina..." /></SelectTrigger>
                  <SelectContent>
                    {(maquinas?.results ?? []).map((m) => (
                      <SelectItem key={m.id} value={String(m.id)}>{m.nombre} — {m.codigo}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {errors.maquina && <p className="text-xs text-destructive">{errors.maquina.message}</p>}
              </div>
              <div className="space-y-2">
                <Label>Turno</Label>
                <Select
                  value={turnoId}
                  onValueChange={(v) => setValue('turno', v, { shouldValidate: true })}
                >
                  <SelectTrigger><SelectValue placeholder="Seleccionar turno..." /></SelectTrigger>
                  <SelectContent>
                    {(turnos?.results ?? []).map((t) => (
                      <SelectItem key={t.id} value={String(t.id)}>{t.nombre}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {errors.turno && <p className="text-xs text-destructive">{errors.turno.message}</p>}
              </div>
              <div className="space-y-2">
                <Label>Fecha</Label>
                <Input type="date" {...register('fecha')} />
                {errors.fecha && <p className="text-xs text-destructive">{errors.fecha.message}</p>}
              </div>
              <div className="space-y-2">
                <Label>Observaciones</Label>
                <Input {...register('observaciones')} placeholder="Opcional..." />
              </div>
              <div className="flex gap-2 justify-end">
                <Button type="button" variant="outline" onClick={() => setOpen(false)}>Cancelar</Button>
                <Button type="submit" disabled={crear.isPending}>
                  {crear.isPending ? 'Creando...' : 'Crear'}
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm text-muted-foreground">
            {data?.count ?? 0} asignaciones · {asignaciones.filter((a) => a.estado === 'ACTIVA').length} activas
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          {asignaciones.length === 0 ? (
            <EmptyState title="Sin asignaciones" description="No hay asignaciones registradas" icon={Activity} className="py-16" />
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Operario</TableHead>
                  <TableHead>Máquina</TableHead>
                  <TableHead>Turno</TableHead>
                  <TableHead>Fecha</TableHead>
                  <TableHead>Estado</TableHead>
                  <TableHead>Inicio</TableHead>
                  <TableHead className="text-right">Acción</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {asignaciones.map((a) => (
                  <TableRow key={a.id}>
                    <TableCell className="text-sm font-medium">
                      {a.operario_nombre ?? `#${a.operario}`}
                    </TableCell>
                    <TableCell className="text-sm">
                      {a.maquina_nombre ?? `#${a.maquina}`}
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {a.turno_nombre ?? `#${a.turno}`}
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">{a.fecha}</TableCell>
                    <TableCell><StatusBadge value={a.estado} /></TableCell>
                    <TableCell className="text-xs text-muted-foreground">
                      {a.hora_inicio_real ? new Date(a.hora_inicio_real).toLocaleTimeString('es') : '—'}
                    </TableCell>
                    <TableCell className="text-right">
                      {a.estado === 'PENDIENTE' && (
                        <Button size="sm" onClick={() => iniciar.mutate(a.id)} disabled={iniciar.isPending}>
                          <Play className="h-3 w-3 mr-1" /> Iniciar
                        </Button>
                      )}
                      {a.estado === 'ACTIVA' && (
                        <Button size="sm" variant="outline" onClick={() => finalizar.mutate(a.id)} disabled={finalizar.isPending}>
                          <Square className="h-3 w-3 mr-1" /> Finalizar
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
