'use client';

import { useEffect, useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { usuariosApi } from '@/lib/api/usuarios';
import { useAuthStore } from '@/stores/authStore';
import { DataFetchAlert } from '@/components/shared/DataFetchAlert';
import { PaginationBar } from '@/components/shared/PaginationBar';
import type { Usuario } from '@/types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from '@/components/ui/select';
import {
  Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle,
} from '@/components/ui/dialog';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { KeyRound, Pencil, Users, UserPlus } from 'lucide-react';
import { toast } from 'sonner';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';

const createSchema = z.object({
  username: z.string().min(3, 'Mínimo 3 caracteres'),
  email: z.string().email('Email inválido'),
  first_name: z.string().min(1, 'Requerido'),
  last_name: z.string().min(1, 'Requerido'),
  rol: z.enum(['OPERARIO', 'SUPERVISOR', 'GERENTE', 'ADMIN']),
  telefono: z.string().optional(),
  password: z.string().min(6, 'Mínimo 6 caracteres'),
  password2: z.string().min(6, 'Mínimo 6 caracteres'),
}).refine((d) => d.password === d.password2, {
  message: 'Las contraseñas no coinciden',
  path: ['password2'],
});
type CreateForm = z.infer<typeof createSchema>;

const editSchema = z.object({
  username: z.string().min(3, 'Mínimo 3 caracteres'),
  email: z.string().email('Email inválido'),
  first_name: z.string().min(1, 'Requerido'),
  last_name: z.string().min(1, 'Requerido'),
  rol: z.enum(['OPERARIO', 'SUPERVISOR', 'GERENTE', 'ADMIN']),
  telefono: z.string().optional(),
  activo: z.enum(['true', 'false']),
});
type EditForm = z.infer<typeof editSchema>;

const passwordSchema = z.object({
  new_password: z.string().min(6, 'Mínimo 6 caracteres'),
  new_password2: z.string().min(6, 'Mínimo 6 caracteres'),
}).refine((d) => d.new_password === d.new_password2, {
  message: 'Las contraseñas no coinciden',
  path: ['new_password2'],
});
type PasswordForm = z.infer<typeof passwordSchema>;

const rolVariant = (rol: string) => {
  if (rol === 'ADMIN') return 'destructive';
  if (rol === 'GERENTE') return 'default';
  if (rol === 'SUPERVISOR') return 'secondary';
  return 'outline';
};

const getErrorMessage = (err: unknown, fallback: string) => {
  const data = (err as { response?: { data?: Record<string, string[] | string> } })?.response?.data;
  if (!data) return fallback;
  const first = Object.values(data)[0];
  return Array.isArray(first) ? first[0] : String(first);
};

export default function AdminUsuariosPage() {
  const qc = useQueryClient();
  const [open, setOpen] = useState(false);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [editingUser, setEditingUser] = useState<Usuario | null>(null);
  const [passwordUser, setPasswordUser] = useState<Usuario | null>(null);

  const empresa = useAuthStore((s) => s.user?.empresa);

  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['usuarios', page],
    queryFn: () => usuariosApi.list({ page }).then((r) => r.data),
  });

  const { register, handleSubmit, setValue, watch, reset, formState: { errors } } = useForm<CreateForm>({
    resolver: zodResolver(createSchema),
    defaultValues: { rol: 'OPERARIO', telefono: '' },
  });

  const createRol = watch('rol');

  const {
    register: registerEdit,
    handleSubmit: handleSubmitEdit,
    setValue: setEditValue,
    watch: watchEdit,
    reset: resetEdit,
    formState: { errors: editErrors },
  } = useForm<EditForm>({
    resolver: zodResolver(editSchema),
    defaultValues: {
      username: '',
      email: '',
      first_name: '',
      last_name: '',
      rol: 'OPERARIO',
      telefono: '',
      activo: 'true',
    },
  });

  const {
    register: registerPassword,
    handleSubmit: handleSubmitPassword,
    reset: resetPassword,
    formState: { errors: passwordErrors },
  } = useForm<PasswordForm>({
    resolver: zodResolver(passwordSchema),
    defaultValues: { new_password: '', new_password2: '' },
  });

  useEffect(() => {
    if (!editingUser) return;
    resetEdit({
      username: editingUser.username,
      email: editingUser.email,
      first_name: editingUser.first_name,
      last_name: editingUser.last_name,
      rol: editingUser.rol,
      telefono: editingUser.telefono ?? '',
      activo: editingUser.activo ? 'true' : 'false',
    });
  }, [editingUser, resetEdit]);

  useEffect(() => {
    if (!passwordUser) return;
    resetPassword({ new_password: '', new_password2: '' });
  }, [passwordUser, resetPassword]);

  const crearUsuario = useMutation({
    mutationFn: (values: CreateForm) => {
      if (!empresa) {
        return Promise.reject(new Error('Tu usuario no tiene empresa asignada'));
      }
      return usuariosApi.create({ ...values, empresa });
    },
    onSuccess: () => {
      toast.success('Usuario creado');
      qc.invalidateQueries({ queryKey: ['usuarios'] });
      reset();
      setOpen(false);
    },
    onError: (err: unknown) => toast.error(getErrorMessage(err, 'Error al crear usuario')),
  });

  const actualizarUsuario = useMutation({
    mutationFn: (values: EditForm) => {
      if (!editingUser) throw new Error('Usuario no seleccionado');
      return usuariosApi.update(editingUser.id, {
        username: values.username,
        email: values.email,
        first_name: values.first_name,
        last_name: values.last_name,
        rol: values.rol,
        telefono: values.telefono || '',
        activo: values.activo === 'true',
      });
    },
    onSuccess: () => {
      toast.success('Usuario actualizado');
      qc.invalidateQueries({ queryKey: ['usuarios'] });
      setEditingUser(null);
    },
    onError: (err: unknown) => toast.error(getErrorMessage(err, 'Error al actualizar usuario')),
  });

  const resetearPassword = useMutation({
    mutationFn: (values: PasswordForm) => {
      if (!passwordUser) throw new Error('Usuario no seleccionado');
      return usuariosApi.setPassword(passwordUser.id, values);
    },
    onSuccess: () => {
      toast.success('Contraseña restablecida');
      setPasswordUser(null);
      resetPassword();
    },
    onError: (err: unknown) => toast.error(getErrorMessage(err, 'Error al restablecer contraseña')),
  });

  const toggleActivo = useMutation({
    mutationFn: ({ id, activo }: { id: number; activo: boolean }) =>
      usuariosApi.update(id, { activo: !activo }),
    onSuccess: () => {
      toast.success('Usuario actualizado');
      qc.invalidateQueries({ queryKey: ['usuarios'] });
    },
    onError: () => toast.error('Error al actualizar usuario'),
  });

  if (isLoading) {
    return <div className="animate-pulse h-64 bg-slate-200 rounded-lg" />;
  }

  if (isError) {
    return (
      <div className="space-y-4">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Users className="h-6 w-6" /> Usuarios
        </h1>
        <DataFetchAlert error={error} onRetry={() => refetch()} />
      </div>
    );
  }

  const usuarios = (data?.results ?? []).filter((u) => {
    const term = search.trim().toLowerCase();
    if (!term) return true;
    return [u.username, u.email, u.first_name, u.last_name, u.rol, u.telefono ?? '']
      .join(' ')
      .toLowerCase()
      .includes(term);
  });
  const editRol = watchEdit('rol');
  const editActivo = watchEdit('activo');

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Users className="h-6 w-6" /> Usuarios
        </h1>
        <Button size="sm" onClick={() => setOpen(true)}>
          <UserPlus className="h-4 w-4 mr-2" /> Nuevo usuario
        </Button>
      </div>

      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div>
              <p className="font-medium">Administración avanzada de usuarios</p>
              <p className="text-sm text-muted-foreground">
                Busca, edita perfil, cambia rol y restablece contraseña desde el panel admin.
              </p>
            </div>
            <Input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Buscar por usuario, email, nombre o rol"
              className="md:max-w-sm"
            />
          </div>
        </CardContent>
      </Card>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Nuevo usuario</DialogTitle>
            <DialogDescription>Crea un usuario nuevo y asígnale el rol adecuado.</DialogDescription>
          </DialogHeader>
          <form onSubmit={handleSubmit((d) => crearUsuario.mutate(d))} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Nombre</Label>
                <Input {...register('first_name')} placeholder="Juan" />
                {errors.first_name && <p className="text-xs text-destructive">{errors.first_name.message}</p>}
              </div>
              <div className="space-y-2">
                <Label>Apellido</Label>
                <Input {...register('last_name')} placeholder="Pérez" />
                {errors.last_name && <p className="text-xs text-destructive">{errors.last_name.message}</p>}
              </div>
            </div>
            <div className="space-y-2">
              <Label>Usuario</Label>
              <Input {...register('username')} placeholder="juanperez" />
              {errors.username && <p className="text-xs text-destructive">{errors.username.message}</p>}
            </div>
            <div className="space-y-2">
              <Label>Email</Label>
              <Input type="email" {...register('email')} placeholder="juan@empresa.com" />
              {errors.email && <p className="text-xs text-destructive">{errors.email.message}</p>}
            </div>
            <div className="space-y-2">
              <Label>Teléfono</Label>
              <Input {...register('telefono')} placeholder="999999999" />
              {errors.telefono && <p className="text-xs text-destructive">{errors.telefono.message}</p>}
            </div>
            <div className="space-y-2">
              <Label>Rol</Label>
              <Select
                value={createRol}
                onValueChange={(v) => setValue('rol', v as CreateForm['rol'], { shouldValidate: true })}
              >
                <SelectTrigger><SelectValue placeholder="Seleccionar rol..." /></SelectTrigger>
                <SelectContent>
                  {(['OPERARIO', 'SUPERVISOR', 'GERENTE', 'ADMIN'] as const).map((r) => (
                    <SelectItem key={r} value={r}>{r}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Contraseña</Label>
                <Input type="password" {...register('password')} />
                {errors.password && <p className="text-xs text-destructive">{errors.password.message}</p>}
              </div>
              <div className="space-y-2">
                <Label>Confirmar</Label>
                <Input type="password" {...register('password2')} />
                {errors.password2 && <p className="text-xs text-destructive">{errors.password2.message}</p>}
              </div>
            </div>
            <div className="flex gap-2 justify-end">
              <Button type="button" variant="outline" onClick={() => setOpen(false)}>Cancelar</Button>
              <Button type="submit" disabled={crearUsuario.isPending}>
                {crearUsuario.isPending ? 'Creando...' : 'Crear'}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      <Dialog open={Boolean(editingUser)} onOpenChange={(nextOpen) => { if (!nextOpen) setEditingUser(null); }}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Editar usuario</DialogTitle>
            <DialogDescription>Actualiza los datos del usuario, su rol y su estado de acceso.</DialogDescription>
          </DialogHeader>
          <form onSubmit={handleSubmitEdit((values) => actualizarUsuario.mutate(values))} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Nombre</Label>
                <Input {...registerEdit('first_name')} />
                {editErrors.first_name && <p className="text-xs text-destructive">{editErrors.first_name.message}</p>}
              </div>
              <div className="space-y-2">
                <Label>Apellido</Label>
                <Input {...registerEdit('last_name')} />
                {editErrors.last_name && <p className="text-xs text-destructive">{editErrors.last_name.message}</p>}
              </div>
            </div>
            <div className="space-y-2">
              <Label>Usuario</Label>
              <Input {...registerEdit('username')} />
              {editErrors.username && <p className="text-xs text-destructive">{editErrors.username.message}</p>}
            </div>
            <div className="space-y-2">
              <Label>Email</Label>
              <Input type="email" {...registerEdit('email')} />
              {editErrors.email && <p className="text-xs text-destructive">{editErrors.email.message}</p>}
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Teléfono</Label>
                <Input {...registerEdit('telefono')} placeholder="999999999" />
                {editErrors.telefono && <p className="text-xs text-destructive">{editErrors.telefono.message}</p>}
              </div>
              <div className="space-y-2">
                <Label>Rol</Label>
                <Select value={editRol} onValueChange={(v) => setEditValue('rol', v as EditForm['rol'])}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {(['OPERARIO', 'SUPERVISOR', 'GERENTE', 'ADMIN'] as const).map((r) => (
                      <SelectItem key={r} value={r}>{r}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="space-y-2">
              <Label>Estado</Label>
              <Select value={editActivo} onValueChange={(v) => setEditValue('activo', v as EditForm['activo'])}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="true">Activo</SelectItem>
                  <SelectItem value="false">Inactivo</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="flex gap-2 justify-end">
              <Button type="button" variant="outline" onClick={() => setEditingUser(null)}>Cancelar</Button>
              <Button type="submit" disabled={actualizarUsuario.isPending}>
                {actualizarUsuario.isPending ? 'Guardando...' : 'Guardar cambios'}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      <Dialog open={Boolean(passwordUser)} onOpenChange={(nextOpen) => { if (!nextOpen) setPasswordUser(null); }}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Restablecer contraseña{passwordUser ? `: ${passwordUser.username}` : ''}</DialogTitle>
            <DialogDescription>Define una nueva contraseña para el usuario seleccionado.</DialogDescription>
          </DialogHeader>
          <form onSubmit={handleSubmitPassword((values) => resetearPassword.mutate(values))} className="space-y-4">
            <div className="space-y-2">
              <Label>Nueva contraseña</Label>
              <Input type="password" {...registerPassword('new_password')} />
              {passwordErrors.new_password && <p className="text-xs text-destructive">{passwordErrors.new_password.message}</p>}
            </div>
            <div className="space-y-2">
              <Label>Confirmar nueva contraseña</Label>
              <Input type="password" {...registerPassword('new_password2')} />
              {passwordErrors.new_password2 && <p className="text-xs text-destructive">{passwordErrors.new_password2.message}</p>}
            </div>
            <div className="flex gap-2 justify-end">
              <Button type="button" variant="outline" onClick={() => setPasswordUser(null)}>Cancelar</Button>
              <Button type="submit" disabled={resetearPassword.isPending}>
                {resetearPassword.isPending ? 'Actualizando...' : 'Restablecer contraseña'}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm text-muted-foreground">
            {usuarios.length} de {data?.count ?? 0} usuarios visibles
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Usuario</TableHead>
                <TableHead>Nombre</TableHead>
                <TableHead>Email</TableHead>
                <TableHead>Teléfono</TableHead>
                <TableHead>Rol</TableHead>
                <TableHead>Estado</TableHead>
                <TableHead className="text-right">Acciones</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {usuarios.map((u) => (
                <TableRow key={u.id}>
                  <TableCell className="font-mono text-sm">{u.username}</TableCell>
                  <TableCell>{u.first_name} {u.last_name}</TableCell>
                  <TableCell className="text-muted-foreground">{u.email}</TableCell>
                  <TableCell className="text-muted-foreground">{u.telefono || '—'}</TableCell>
                  <TableCell>
                    <Badge variant={rolVariant(u.rol)}>{u.rol}</Badge>
                  </TableCell>
                  <TableCell>
                    <Badge variant={u.activo ? 'default' : 'secondary'}>
                      {u.activo ? 'Activo' : 'Inactivo'}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex justify-end gap-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => setEditingUser(u)}
                      >
                        <Pencil className="h-3 w-3 mr-1" /> Editar
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => setPasswordUser(u)}
                      >
                        <KeyRound className="h-3 w-3 mr-1" /> Clave
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => toggleActivo.mutate({ id: u.id, activo: u.activo })}
                        disabled={toggleActivo.isPending}
                      >
                        {u.activo ? 'Desactivar' : 'Activar'}
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
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
