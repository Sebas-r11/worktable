export type BadgeVariant = 'default' | 'secondary' | 'destructive' | 'outline';

const STATUS_VARIANT_MAP: Record<string, BadgeVariant> = {
  ACTIVA: 'default',
  ACTIVO: 'default',
  OPERANDO: 'default',
  DISPONIBLE: 'default',
  PENDIENTE: 'secondary',
  COMPLETADA: 'outline',
  COMPLETADO: 'outline',
  FINALIZADA: 'outline',
  FINALIZADO: 'outline',
  CANCELADA: 'outline',
  CANCELADO: 'outline',
  INACTIVA: 'outline',
  INACTIVO: 'outline',
  PARADA: 'destructive',
  MANTENIMIENTO: 'secondary',
  FUERA_SERVICIO: 'destructive',
  BAJA: 'outline',
  MEDIA: 'secondary',
  ALTA: 'destructive',
  CRITICA: 'destructive',
  ABIERTA: 'destructive',
  EN_PROCESO: 'secondary',
  RESUELTA: 'default',
  ESCALADA: 'destructive',
  DESCARTADA: 'outline',
  EXPIRADA: 'outline',
  ADMIN: 'destructive',
  GERENTE: 'default',
  SUPERVISOR: 'secondary',
  OPERARIO: 'outline',
  ACEPTADA: 'default',
  RECHAZADA: 'outline',
  LISTA: 'default',
  DESPACHADA: 'outline',
  EN_COLA: 'secondary',
};

export function getStatusVariant(value: string): BadgeVariant {
  return STATUS_VARIANT_MAP[value] ?? 'secondary';
}
