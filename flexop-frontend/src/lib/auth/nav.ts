import type { LucideIcon } from 'lucide-react';
import {
  LayoutDashboard,
  Cpu,
  Users,
  Activity,
  BarChart3,
  Bell,
  Shuffle,
  FileText,
  ClipboardList,
  PackagePlus,
  AlertCircle,
} from 'lucide-react';
import type { AuthUser } from '@/types';
import { canAccessPath } from './routes';

export interface NavItem {
  href: string;
  label: string;
  icon: LucideIcon;
}

export const navByRole: Record<AuthUser['rol'], NavItem[]> = {
  OPERARIO: [
    { href: '/operario', label: 'Mi Dashboard', icon: LayoutDashboard },
    { href: '/operario/produccion', label: 'Producción', icon: PackagePlus },
    { href: '/operario/incidencias', label: 'Incidencias', icon: AlertCircle },
  ],
  SUPERVISOR: [
    { href: '/supervisor', label: 'Dashboard', icon: LayoutDashboard },
    { href: '/supervisor/alertas', label: 'Alertas', icon: Bell },
    { href: '/supervisor/sugerencias', label: 'Reasignaciones', icon: Shuffle },
    { href: '/supervisor/asignaciones', label: 'Asignaciones', icon: Activity },
    { href: '/supervisor/incidencias', label: 'Incidencias', icon: AlertCircle },
  ],
  GERENTE: [
    { href: '/gerente', label: 'Dashboard', icon: LayoutDashboard },
    { href: '/gerente/reportes', label: 'Reportes', icon: FileText },
    { href: '/gerente/metricas', label: 'Métricas', icon: BarChart3 },
    { href: '/gerente/ordenes', label: 'Órdenes', icon: ClipboardList },
  ],
  ADMIN: [
    { href: '/admin/usuarios', label: 'Usuarios', icon: Users },
    { href: '/admin/maquinas', label: 'Máquinas', icon: Cpu },
    { href: '/admin/operarios', label: 'Operarios', icon: Users },
  ],
};

export function getNavItemsForRole(rol: string): NavItem[] {
  const items = navByRole[rol as AuthUser['rol']] ?? [];
  return items.filter((item) => canAccessPath(item.href, rol as AuthUser['rol']));
}

export function isNavItemActive(pathname: string, href: string): boolean {
  if (pathname === href) return true;
  const rootPaths = ['/operario', '/supervisor', '/gerente'];
  if (rootPaths.includes(href)) return false;
  return pathname.startsWith(`${href}/`);
}
