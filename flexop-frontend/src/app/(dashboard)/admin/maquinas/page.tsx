'use client';

import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useMaquinas, useTiposMaquina, useUnidadesEficiencia } from '@/hooks/useApi';
import { maquinasApi } from '@/lib/api/maquinas';
import { useAuthStore } from '@/stores/authStore';
import { getMaquinaEstado } from '@/lib/display/entities';
import type { Maquina } from '@/types';
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
import { Cpu, Plus } from 'lucide-react';
import { toast } from 'sonner';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';

const schema = z.object({
  nombre: z.string().min(2, 'Mínimo 2 caracteres'),
  codigo: z.string().min(1, 'Requerido'),
  tipo: z.string().min(1, 'Selecciona un tipo').transform(Number),
  capacidad_teorica: z.string().min(1, 'Requerido').transform(Number).pipe(z.number().positive('Debe ser mayor a 0')),
  unidad_capacidad: z.string().min(1, 'Selecciona una unidad').transform(Number),
  marca: z.string().optional(),
  ubicacion: z.string().optional(),
});
type FormInput = {
  nombre: string;
  codigo: string;
  tipo: string;
  capacidad_teorica: string;
  unidad_capacidad: string;
  marca?: string;
  ubicacion?: string;
};
type FormData = z.infer<typeof schema>;

export default function AdminMaquinasPage() {
  const qc = useQueryClient();
  const empresa = useAuthStore((s) => s.user?.empresa);
  const [open, setOpen] = useState(false);
  const [page, setPage] = useState(1);
  const { data, isLoading } = useMaquinas({ page });
  const { data: tipos } = useTiposMaquina();
  const { data: unidades } = useUnidadesEficiencia();

  const { register, handleSubmit, setValue, watch, reset, formState: { errors } } = useForm<FormInput>({
    resolver: zodResolver(schema) as never,
  });

  const tipoId = watch('tipo');
  const unidadId = watch('unidad_capacidad');

  const crear = useMutation({
    mutationFn: (values: FormData) => {
      if (!empresa) {
        return Promise.reject(new Error('Sin empresa asignada'));
      }
      return maquinasApi.create({
        nombre: values.nombre,
        codigo: values.codigo,
        tipo: values.tipo,
        capacidad_teorica: values.capacidad_teorica,
        unidad_capacidad: values.unidad_capacidad,
        marca: values.marca,
        ubicacion: values.ubicacion,
        empresa,
      });
    },
    onSuccess: () => {
      toast.success('Máquina creada');
      qc.invalidateQueries({ queryKey: ['maquinas'] });
      reset();
      setOpen(false);
    },
    onError: () => toast.error('Error al crear máquina'),
  });

  const toggleActiva = useMutation({
    mutationFn: ({ id, activa }: { id: number; activa: boolean }) =>
      maquinasApi.update(id, { activa: !activa }),
    onSuccess: () => {
      toast.success('Máquina actualizada');
      qc.invalidateQueries({ queryKey: ['maquinas'] });
    },
  });

  if (isLoading) return <PageLoader />;

  const maquinas = data?.results ?? [];
  const tiposList = tipos?.results ?? [];
  const unidadesList = unidades?.results ?? [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Cpu className="h-6 w-6" /> Máquinas
        </h1>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button size="sm"><Plus className="h-4 w-4 mr-2" /> Nueva máquina</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>Nueva máquina</DialogTitle></DialogHeader>
            <form onSubmit={handleSubmit((d) => crear.mutate(d as unknown as FormData))} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Nombre</Label>
                  <Input {...register('nombre')} placeholder="Inyectora A1" />
                  {errors.nombre && <p className="text-xs text-destructive">{errors.nombre.message}</p>}
                </div>
                <div className="space-y-2">
                  <Label>Código</Label>
                  <Input {...register('codigo')} placeholder="INY-001" />
                  {errors.codigo && <p className="text-xs text-destructive">{errors.codigo.message}</p>}
                </div>
              </div>
              <div className="space-y-2">
                <Label>Tipo de máquina</Label>
                <Select
                  value={tipoId}
                  onValueChange={(v) => setValue('tipo', v, { shouldValidate: true })}
                >
                  <SelectTrigger><SelectValue placeholder="Seleccionar..." /></SelectTrigger>
                  <SelectContent>
                    {tiposList.map((t) => (
                      <SelectItem key={t.id} value={String(t.id)}>{t.nombre}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {errors.tipo && <p className="text-xs text-destructive">{errors.tipo.message}</p>}
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Capacidad teórica</Label>
                  <Input type="number" min={0.01} step="any" {...register('capacidad_teorica')} />
                  {errors.capacidad_teorica && <p className="text-xs text-destructive">{errors.capacidad_teorica.message}</p>}
                </div>
                <div className="space-y-2">
                  <Label>Unidad</Label>
                  <Select
                    value={unidadId}
                    onValueChange={(v) => setValue('unidad_capacidad', v, { shouldValidate: true })}
                  >
                    <SelectTrigger><SelectValue placeholder="Seleccionar..." /></SelectTrigger>
                    <SelectContent>
                      {unidadesList.map((u) => (
                        <SelectItem key={u.id} value={String(u.id)}>{u.nombre} ({u.abreviatura})</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  {errors.unidad_capacidad && <p className="text-xs text-destructive">{errors.unidad_capacidad.message}</p>}
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Marca</Label>
                  <Input {...register('marca')} placeholder="Opcional" />
                </div>
                <div className="space-y-2">
                  <Label>Ubicación</Label>
                  <Input {...register('ubicacion')} placeholder="Opcional" />
                </div>
              </div>
              <div className="flex gap-2 justify-end">
                <Button type="button" variant="outline" onClick={() => setOpen(false)}>Cancelar</Button>
                <Button type="submit" disabled={crear.isPending || !empresa}>
                  {crear.isPending ? 'Creando...' : 'Crear'}
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm text-muted-foreground">{data?.count ?? 0} máquinas</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          {maquinas.length === 0 ? (
            <EmptyState title="Sin máquinas" description="Crea la primera máquina de tu planta" icon={Cpu} className="py-16" />
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Código</TableHead>
                  <TableHead>Nombre</TableHead>
                  <TableHead>Estado</TableHead>
                  <TableHead>Capacidad</TableHead>
                  <TableHead>Activa</TableHead>
                  <TableHead className="text-right">Acción</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {maquinas.map((m: Maquina) => (
                  <TableRow key={m.id}>
                    <TableCell className="font-mono text-sm">{m.codigo}</TableCell>
                    <TableCell className="font-medium">{m.nombre}</TableCell>
                    <TableCell><StatusBadge value={getMaquinaEstado(m)} /></TableCell>
                    <TableCell>
                      {m.capacidad_teorica} {m.unidad_nombre ?? ''}
                    </TableCell>
                    <TableCell>
                      <StatusBadge value={m.activa ? 'ACTIVO' : 'INACTIVO'} />
                    </TableCell>
                    <TableCell className="text-right">
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => toggleActiva.mutate({ id: m.id, activa: m.activa })}
                        disabled={toggleActiva.isPending}
                      >
                        {m.activa ? 'Desactivar' : 'Activar'}
                      </Button>
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
