/**
 * Usuarios de prueba creados por backend/populate_db.py
 */
export interface E2EUser {
  username: string;
  password: string;
  rol: string;
  expectedPath: string;
  expectedHeading: RegExp | string;
  expectedNavItem: string;
}

export const E2E_USERS: E2EUser[] = [
  {
    username: 'operario1',
    password: 'operario123',
    rol: 'OPERARIO',
    expectedPath: '/operario',
    expectedHeading: 'Mi Dashboard',
    expectedNavItem: 'Mi Dashboard',
  },
  {
    username: 'supervisor1',
    password: 'super123',
    rol: 'SUPERVISOR',
    expectedPath: '/supervisor',
    expectedHeading: 'Dashboard Supervisor',
    expectedNavItem: 'Dashboard',
  },
  {
    username: 'gerente1',
    password: 'gerente123',
    rol: 'GERENTE',
    expectedPath: '/gerente',
    expectedHeading: 'Dashboard Gerente',
    expectedNavItem: 'Dashboard',
  },
  {
    username: 'admin',
    password: 'admin123',
    rol: 'ADMIN',
    expectedPath: '/admin/usuarios',
    expectedHeading: 'Usuarios',
    expectedNavItem: 'Usuarios',
  },
];
