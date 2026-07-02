import { describe, expect, it } from 'vitest';
import { canAccessPath, getDashboardRoute } from './routes';
import { getNavItemsForRole, navByRole } from './nav';

describe('canAccessPath', () => {
  it('operario accede a rutas operario', () => {
    expect(canAccessPath('/operario', 'OPERARIO')).toBe(true);
    expect(canAccessPath('/operario/produccion', 'OPERARIO')).toBe(true);
  });

  it('operario no accede a supervisor ni gerente', () => {
    expect(canAccessPath('/supervisor', 'OPERARIO')).toBe(false);
    expect(canAccessPath('/supervisor/alertas', 'OPERARIO')).toBe(false);
    expect(canAccessPath('/gerente/ordenes', 'OPERARIO')).toBe(false);
  });

  it('gerente accede a gerente pero no a supervisor', () => {
    expect(canAccessPath('/gerente', 'GERENTE')).toBe(true);
    expect(canAccessPath('/gerente/ordenes', 'GERENTE')).toBe(true);
    expect(canAccessPath('/supervisor', 'GERENTE')).toBe(false);
    expect(canAccessPath('/supervisor/asignaciones', 'GERENTE')).toBe(false);
  });

  it('supervisor accede a supervisor pero no a gerente', () => {
    expect(canAccessPath('/supervisor/incidencias', 'SUPERVISOR')).toBe(true);
    expect(canAccessPath('/gerente/reportes', 'SUPERVISOR')).toBe(false);
  });

  it('admin accede a todas las secciones', () => {
    expect(canAccessPath('/admin/usuarios', 'ADMIN')).toBe(true);
    expect(canAccessPath('/supervisor', 'ADMIN')).toBe(true);
    expect(canAccessPath('/gerente', 'ADMIN')).toBe(true);
    expect(canAccessPath('/operario', 'ADMIN')).toBe(true);
  });
});

describe('getDashboardRoute', () => {
  it('devuelve ruta por rol', () => {
    expect(getDashboardRoute('GERENTE')).toBe('/gerente');
    expect(getDashboardRoute('SUPERVISOR')).toBe('/supervisor');
  });
});

describe('nav alineado con guards', () => {
  it('cada item de nav es accesible para su rol', () => {
    (Object.keys(navByRole) as Array<keyof typeof navByRole>).forEach((rol) => {
      getNavItemsForRole(rol).forEach((item) => {
        expect(canAccessPath(item.href, rol)).toBe(true);
      });
    });
  });
});
