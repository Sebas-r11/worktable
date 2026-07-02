import type { AuthUser } from '@/types';

export const DASHBOARD_ROUTES: Record<AuthUser['rol'], string> = {
  OPERARIO: '/operario',
  SUPERVISOR: '/supervisor',
  GERENTE: '/gerente',
  ADMIN: '/admin/usuarios',
};

/** Prefijos de ruta permitidos por rol (fuente única para guards y nav). */
export const ROLE_ALLOWED_PREFIXES: Record<AuthUser['rol'], readonly string[]> = {
  OPERARIO: ['/operario'],
  SUPERVISOR: ['/supervisor'],
  GERENTE: ['/gerente'],
  ADMIN: ['/admin', '/operario', '/supervisor', '/gerente'],
};

const PROTECTED_PREFIXES = ['/admin', '/gerente', '/supervisor', '/operario'] as const;

export function getDashboardRoute(rol: string): string {
  return DASHBOARD_ROUTES[rol as AuthUser['rol']] ?? '/login';
}

export function canAccessPath(pathname: string, rol: AuthUser['rol'] | undefined): boolean {
  if (!rol) return false;

  const sectionPrefix = [...PROTECTED_PREFIXES]
    .sort((a, b) => b.length - a.length)
    .find((prefix) => pathname === prefix || pathname.startsWith(`${prefix}/`));

  if (!sectionPrefix) return true;

  return ROLE_ALLOWED_PREFIXES[rol].some(
    (allowed) => sectionPrefix === allowed || sectionPrefix.startsWith(`${allowed}/`),
  );
}
