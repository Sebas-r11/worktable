'use client';

import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useOrdenes, useColaDespacho, useMaquinas } from '@/hooks/useApi';
import { ordenesApi } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
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
import { PageLoader } from '@/components/shared/LoadingSpinner';
import { EmptyState } from '@/components/shared/EmptyState';
import { PaginationBar } from '@/components/shared/PaginationBar';
import { ClipboardList, Truck, Play, CheckSquare, Plus } from 'lucide-react';
import { toast } from 'sonner';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { useAuthStore } from '@/stores/authStore';
import { isAxiosError } from 'axios';

const schema = z.object({
  producto: z.string().min(1, 'Requerido'),
  cantidad_requerida: z.string().transform(Number).pipe(z.number().min(1)),
  fecha_limite: z.string().min(1, 'Selecciona una fecha'),
  prioridad: z.enum(['BAJA', 'NORMAL', 'ALTA', 'URGENTE']),
  maquina: z.string().optional(),
  notas: z.string().optional(),
});
type FormInput = { producto: string; cantidad_requerida: string; fecha_limite: string; prioridad: 'BAJA' | 'NORMAL' | 'ALTA' | 'URGENTE'; maquina?: string; notas?: string };
type FormData = z.infer<typeof schema>;

function apiErrorMessage(err: unknown, fallback: string): string {
  if (isAxiosError(err) && err.response?.data) {
    const data = err.response.data as Record<string, unknown>;
    if (typeof data.detail === 'string') return data.detail;
    const first = Object.values(data).flat()[0];
    if (typeof first === 'string') return first;
  }
  return fallback;
}

export default function GerenteOrdenesPage() {
  const qc = useQueryClient();
  const empresa = useAuthStore((s) => s.user?.empresa);
  const [open, setOpen] = useState(false);
  const [page, setPage] = useState(1);
  const { data, isLoading } = useOrdenes({ page });
  const { data: cola } = useColaDespacho();
  const { data: maquinas } = useMaquinas();

  const { register, handleSubmit, setValue, watch, reset, formState: { errors } } = useForm<FormInput>({
    resolver: zodResolver(schema) as never,
    defaultValues: {
      prioridad: 'NORMAL',
      fecha_limite: new Date(Date.now() + 7 * 86400000).toISOString().slice(0, 10),
    },
  });

  const prioridad = watch('prioridad');
  const maquinaId = watch('maquina');

  const crearOrden = useMutation({
    mutationFn: (values: FormData) => {
      if (!empresa) {
        return Promise.reject(new Error('Sin empresa asignada'));
      }
      return ordenesApi.create({
        producto: values.producto,
        cantidad_requerida: values.cantidad_requerida,
        fecha_limite: `${values.fecha_limite}T23:59:59`,
        prioridad: values.prioridad,
        maquina: values.maquina ? Number(values.maquina) : undefined,
        notas: values.notas,
      });
    },
    onSuccess: () => {
      toast.success('Orden creada');
      qc.invalidateQueries({ queryKey: ['ordenes'] });
      qc.invalidateQueries({ queryKey: ['cola-despacho'] });
      reset();
      setOpen(false);
    },
    onError: (err) => toast.error(apiErrorMessage(err, 'Error al crear orden')),
  });

  const iniciarOrden = useMutation({
    mutationFn: (id: number) => ordenesApi.iniciar(id),
    onSuccess: () => {
      toast.success('Orden iniciada');
      qc.invalidateQueries({ queryKey: ['ordenes'] });
      qc.invalidateQueries({ queryKey: ['cola-despacho'] });
    },
    onError: () => toast.error('Error al iniciar orden'),
  });

  const completarOrden = useMutation({
    mutationFn: (id: number) => ordenesApi.completar(id),
    onSuccess: () => {
      toast.success('Orden completada');
      qc.invalidateQueries({ queryKey: ['ordenes'] });
      qc.invalidateQueries({ queryKey: ['cola-despacho'] });
    },
    onError: () => toast.error('Error al completar orden'),
  });

  const despachar = useMutation({
    mutationFn: (id: number) => ordenesApi.despachar(id),
    onSuccess: () => { toast.success('Orden despachada'); qc.invalidateQueries({ queryKey: ['cola-despacho'] }); },
    onError: () => toast.error('Error al despachar'),
  });

  if (isLoading) return <PageLoader />;

  const ordenes = data?.results ?? [];
  const proxima = cola?.[0];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <ClipboardList className="h-6 w-6" /> Órdenes de Producción
        </h1>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button size="sm"><Plus className="h-4 w-4 mr-2" /> Nueva orden</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>Nueva orden de producción</DialogTitle></DialogHeader>
            <form onSubmit={handleSubmit((d) => crearOrden.mutate(d as unknown as FormData))} className="space-y-4">
              <div className="space-y-2">
                <Label>Producto</Label>
                <Input {...register('producto')} placeholder="Ej: Tornillo M8x20" />
                {errors.producto && <p className="text-xs text-destructive">{errors.producto.message}</p>}
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Cantidad requerida</Label>
                  <Input type="number" min={1} {...register('cantidad_requerida')} />
                  {errors.cantidad_requerida && <p className="text-xs text-destructive">{errors.cantidad_requerida.message}</p>}
                </div>
                <div className="space-y-2">
                  <Label>Prioridad</Label>
                  <Select
                    value={prioridad}
                    onValueChange={(v) => setValue('prioridad', v as FormInput['prioridad'], { shouldValidate: true })}
                  >
                    <SelectTrigger><SelectValue placeholder="Seleccionar..." /></SelectTrigger>
                    <SelectContent>
                      {(['BAJA', 'NORMAL', 'ALTA', 'URGENTE'] as const).map((p) => (
                        <SelectItem key={p} value={p}>{p}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  {errors.prioridad && <p className="text-xs text-destructive">{errors.prioridad.message}</p>}
                </div>
              </div>
              <div className="space-y-2">
                <Label>Fecha límite</Label>
                <Input type="date" {...register('fecha_limite')} />
                {errors.fecha_limite && <p className="text-xs text-destructive">{errors.fecha_limite.message}</p>}
              </div>
              <div className="space-y-2">
                <Label>Máquina asignada (opcional)</Label>
                <Select
                  value={maquinaId ?? 'none'}
                  onValueChange={(v) => setValue('maquina', v === 'none' ? undefined : v, { shouldValidate: true })}
                >
                  <SelectTrigger><SelectValue placeholder="Sin máquina..." /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="none">Sin máquina</SelectItem>
                    {(maquinas?.results ?? []).map((m) => (
                      <SelectItem key={m.id} value={String(m.id)}>{m.nombre} ({m.codigo})</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>Notas</Label>
                <Input {...register('notas')} placeholder="Opcional..." />
              </div>
              <div className="flex gap-2 justify-end">
                <Button type="button" variant="outline" onClick={() => setOpen(false)}>Cancelar</Button>
                <Button type="submit" disabled={crearOrden.isPending || !empresa}>
                  {crearOrden.isPending ? 'Creando...' : 'Crear'}
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Cola de despacho */}
      <Card className={proxima ? 'border-primary/30 bg-primary/5' : ''}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <Truck className="h-5 w-5" /> Cola de despacho
          </CardTitle>
        </CardHeader>
        <CardContent>
          {proxima ? (
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Orden #{proxima.orden_numero ?? proxima.orden} — posición {proxima.posicion_manual}</p>
                <p className="text-sm text-muted-foreground">
                  En cola desde {new Date(proxima.fecha_entrada).toLocaleString('es')}
                </p>
              </div>
              <Button onClick={() => despachar.mutate(proxima.id)} disabled={despachar.isPending}>
                <Truck className="h-4 w-4 mr-2" />
                {despachar.isPending ? 'Despachando...' : 'Despachar'}
              </Button>
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">Cola de despacho vacía</p>
          )}
        </CardContent>
      </Card>

      {/* Listado */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm text-muted-foreground">
            {data?.count ?? 0} órdenes
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          {ordenes.length === 0 ? (
            <EmptyState title="Sin órdenes" description="No hay órdenes de producción" icon={ClipboardList} className="py-16" />
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>#</TableHead>
                  <TableHead>Producto</TableHead>
                  <TableHead>Progreso</TableHead>
                  <TableHead>Estado</TableHead>
                  <TableHead>Prioridad</TableHead>
                  <TableHead>Fecha límite</TableHead>
                  <TableHead className="text-right">Acción</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {ordenes.map((ord) => {
                  const pct = ord.cantidad_requerida > 0
                    ? Math.min(100, (ord.cantidad_producida / ord.cantidad_requerida) * 100)
                    : 0;
                  return (
                    <TableRow key={ord.id}>
                      <TableCell className="font-mono text-sm">{ord.numero_orden}</TableCell>
                      <TableCell className="font-medium">{ord.producto}</TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2 min-w-[120px]">
                          <div className="flex-1 bg-slate-200 rounded-full h-1.5">
                            <div
                              className="bg-primary h-1.5 rounded-full transition-all"
                              style={{ width: `${pct}%` }}
                            />
                          </div>
                          <span className="text-xs text-muted-foreground whitespace-nowrap">
                            {ord.cantidad_producida}/{ord.cantidad_requerida}
                          </span>
                        </div>
                      </TableCell>
                      <TableCell><StatusBadge value={ord.estado} /></TableCell>
                      <TableCell>
                        <Badge variant="outline">{ord.prioridad}</Badge>
                      </TableCell>
                      <TableCell className="text-xs text-muted-foreground">
                        {new Date(ord.fecha_limite).toLocaleDateString('es')}
                      </TableCell>
                      <TableCell className="text-right">
                        {ord.estado === 'PENDIENTE' && (
                          <Button size="sm" onClick={() => iniciarOrden.mutate(ord.id)} disabled={iniciarOrden.isPending}>
                            <Play className="h-3 w-3 mr-1" /> Iniciar
                          </Button>
                        )}
                        {ord.estado === 'EN_PROCESO' && (
                          <Button size="sm" variant="outline" onClick={() => completarOrden.mutate(ord.id)} disabled={completarOrden.isPending}>
                            <CheckSquare className="h-3 w-3 mr-1" /> Completar
                          </Button>
                        )}
                      </TableCell>
                    </TableRow>
                  );
                })}
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
