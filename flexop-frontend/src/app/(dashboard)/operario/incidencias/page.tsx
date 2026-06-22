'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useQueryClient, useMutation } from '@tanstack/react-query';
import { operacionesApi } from '@/lib/api/operaciones';
import { useIncidencias, useDashboardOperario, useMaquinas } from '@/hooks/useApi';
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
import { PageLoader } from '@/components/shared/LoadingSpinner';
import { EmptyState } from '@/components/shared/EmptyState';
import { PaginationBar } from '@/components/shared/PaginationBar';
import { AlertCircle, Plus } from 'lucide-react';
import { toast } from 'sonner';

const schema = z.object({
  tipo: z.enum(['FALLA_MAQUINA', 'FALTA_MATERIAL', 'PROBLEMA_CALIDAD', 'OTRO']),
  titulo: z.string().min(3, 'Mínimo 3 caracteres'),
  descripcion: z.string().min(5, 'Describe la incidencia (mín. 5 caracteres)'),
  prioridad: z.enum(['BAJA', 'MEDIA', 'ALTA', 'CRITICA']),
  maquina: z.string().min(1, 'Selecciona una máquina'),
});
type FormData = z.infer<typeof schema>;

const TIPOS: { value: string; label: string }[] = [
  { value: 'FALLA_MAQUINA', label: 'Falla de Máquina' },
  { value: 'FALTA_MATERIAL', label: 'Falta de Material' },
  { value: 'PROBLEMA_CALIDAD', label: 'Problema de Calidad' },
  { value: 'OTRO', label: 'Otro' },
];

export default function OperarioIncidenciasPage() {
  const qc = useQueryClient();
  const [open, setOpen] = useState(false);
  const [page, setPage] = useState(1);
  const { data: dashboard } = useDashboardOperario();
  const { data: maquinasData } = useMaquinas();
  const { data, isLoading } = useIncidencias({ page });

  const { register, handleSubmit, setValue, watch, reset, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { prioridad: 'MEDIA' },
  });

  const maquinaId = watch('maquina');
  const tipoIncidencia = watch('tipo');
  const prioridad = watch('prioridad');

  const reportar = useMutation({
    mutationFn: (values: FormData) =>
      operacionesApi.incidenciaCreate({
        asignacion: dashboard?.asignacion_activa?.id ?? undefined,
        maquina: Number(values.maquina),
        tipo: values.tipo,
        titulo: values.titulo,
        descripcion: values.descripcion,
        prioridad: values.prioridad,
      }),
    onSuccess: () => {
      toast.success('Incidencia reportada');
      qc.invalidateQueries({ queryKey: ['incidencias'] });
      qc.invalidateQueries({ queryKey: ['dashboard', 'operario'] });
      reset();
      setOpen(false);
    },
    onError: () => toast.error('Error al reportar incidencia'),
  });

  if (isLoading) return <PageLoader />;

  const incidencias = data?.results ?? [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <AlertCircle className="h-6 w-6" /> Incidencias
        </h1>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button size="sm" variant="destructive" disabled={!dashboard?.asignacion_activa}>
              <Plus className="h-4 w-4 mr-2" /> Reportar incidencia
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Reportar incidencia</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleSubmit((d) => reportar.mutate(d))} className="space-y-4">
              <div className="space-y-2">
                <Label>Máquina afectada</Label>
                <Select
                  value={maquinaId}
                  onValueChange={(v) => setValue('maquina', v, { shouldValidate: true })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Seleccionar máquina..." />
                  </SelectTrigger>
                  <SelectContent>
                    {(maquinasData?.results ?? []).map((m) => (
                      <SelectItem key={m.id} value={String(m.id)}>{m.nombre} ({m.codigo})</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {errors.maquina && <p className="text-sm text-destructive">{errors.maquina.message}</p>}
              </div>
              <div className="space-y-2">
                <Label>Tipo</Label>
                <Select
                  value={tipoIncidencia}
                  onValueChange={(v) => setValue('tipo', v as FormData['tipo'], { shouldValidate: true })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Seleccionar tipo..." />
                  </SelectTrigger>
                  <SelectContent>
                    {TIPOS.map((t) => (
                      <SelectItem key={t.value} value={t.value}>{t.label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {errors.tipo && <p className="text-sm text-destructive">{errors.tipo.message}</p>}
              </div>
              <div className="space-y-2">
                <Label htmlFor="titulo">Título</Label>
                <Input id="titulo" {...register('titulo')} placeholder="Ej: Máquina parada sin motivo" />
                {errors.titulo && <p className="text-sm text-destructive">{errors.titulo.message}</p>}
              </div>
              <div className="space-y-2">
                <Label>Prioridad</Label>
                <Select
                  value={prioridad}
                  onValueChange={(v) => setValue('prioridad', v as FormData['prioridad'], { shouldValidate: true })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Seleccionar prioridad..." />
                  </SelectTrigger>
                  <SelectContent>
                    {(['BAJA', 'MEDIA', 'ALTA', 'CRITICA'] as const).map((p) => (
                      <SelectItem key={p} value={p}>{p}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="desc">Descripción</Label>
                <Input id="desc" {...register('descripcion')} placeholder="Describe el problema..." />
                {errors.descripcion && (
                  <p className="text-sm text-destructive">{errors.descripcion.message}</p>
                )}
              </div>
              <div className="flex gap-2 justify-end">
                <Button type="button" variant="outline" onClick={() => setOpen(false)}>Cancelar</Button>
                <Button type="submit" variant="destructive" disabled={reportar.isPending}>
                  {reportar.isPending ? 'Enviando...' : 'Reportar'}
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm text-muted-foreground">{data?.count ?? 0} incidencias</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          {incidencias.length === 0 ? (
            <EmptyState title="Sin incidencias" description="No hay incidencias registradas" icon={AlertCircle} className="py-16" />
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Tipo</TableHead>
                  <TableHead>Título</TableHead>
                  <TableHead>Prioridad</TableHead>
                  <TableHead>Estado</TableHead>
                  <TableHead>Fecha</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {incidencias.map((inc) => (
                  <TableRow key={inc.id}>
                    <TableCell className="font-medium text-sm">{inc.tipo.replace(/_/g, ' ')}</TableCell>
                    <TableCell className="text-sm max-w-[200px] truncate">{inc.titulo}</TableCell>
                    <TableCell><StatusBadge value={inc.prioridad} /></TableCell>
                    <TableCell><StatusBadge value={inc.estado} /></TableCell>
                    <TableCell className="text-xs text-muted-foreground">
                      {new Date(inc.fecha_reporte).toLocaleString('es')}
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
