import { describe, expect, it } from 'vitest';
import { getNavItemsForRole, isNavItemActive, navByRole } from './nav';

describe('getNavItemsForRole', () => {
  it('operario tiene 3 items', () => {
    expect(getNavItemsForRole('OPERARIO')).toHaveLength(3);
  });

  it('supervisor incluye alertas y asignaciones', () => {
    const hrefs = getNavItemsForRole('SUPERVISOR').map((i) => i.href);
    expect(hrefs).toContain('/supervisor/alertas');
    expect(hrefs).toContain('/supervisor/asignaciones');
  });

  it('rol invalido devuelve array vacio', () => {
    expect(getNavItemsForRole('X')).toEqual([]);
  });
});

describe('isNavItemActive', () => {
  it('coincide ruta exacta', () => {
    expect(isNavItemActive('/operario', '/operario')).toBe(true);
  });

  it('no marca hijo en dashboard raiz operario', () => {
    expect(isNavItemActive('/operario/produccion', '/operario')).toBe(false);
  });

  it('marca subruta para secciones anidadas', () => {
    expect(isNavItemActive('/supervisor/alertas/1', '/supervisor/alertas')).toBe(true);
  });
});

describe('navByRole', () => {
  it('cubre los 4 roles', () => {
    expect(Object.keys(navByRole)).toEqual(
      expect.arrayContaining(['OPERARIO', 'SUPERVISOR', 'GERENTE', 'ADMIN'])
    );
  });
});
