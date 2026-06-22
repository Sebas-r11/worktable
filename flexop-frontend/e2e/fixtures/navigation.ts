/**
 * Rutas del sidebar por rol (debe coincidir con src/lib/auth/nav.ts).
 * No incluye el ítem raíz del dashboard: el login ya valida esa pantalla.
 */
export interface E2ENavRoute {
  linkLabel: string;
  path: string;
  heading: RegExp | string;
}

export const E2E_NAV_BY_ROLE: Record<string, E2ENavRoute[]> = {
  OPERARIO: [
    {
      linkLabel: 'Producción',
      path: '/operario/produccion',
      heading: /Registro de Producción/,
    },
    {
      linkLabel: 'Incidencias',
      path: '/operario/incidencias',
      heading: /Incidencias/,
    },
  ],
  SUPERVISOR: [
    { linkLabel: 'Alertas', path: '/supervisor/alertas', heading: /Alertas/ },
    {
      linkLabel: 'Reasignaciones',
      path: '/supervisor/sugerencias',
      heading: /Sugerencias de Reasignación/,
    },
    { linkLabel: 'Asignaciones', path: '/supervisor/asignaciones', heading: /^Asignaciones$/ },
    { linkLabel: 'Incidencias', path: '/supervisor/incidencias', heading: /Incidencias/ },
  ],
  GERENTE: [
    { linkLabel: 'Reportes', path: '/gerente/reportes', heading: /^Reportes$/ },
    { linkLabel: 'Métricas', path: '/gerente/metricas', heading: /Métricas de Eficiencia/ },
    { linkLabel: 'Órdenes', path: '/gerente/ordenes', heading: /Órdenes de Producción/ },
  ],
  ADMIN: [
    { linkLabel: 'Máquinas', path: '/admin/maquinas', heading: /^Máquinas$/ },
    { linkLabel: 'Operarios', path: '/admin/operarios', heading: /^Operarios$/ },
  ],
};
