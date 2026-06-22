import { test, expect } from '@playwright/test';
import { E2E_USERS } from './fixtures/users';
import { E2E_NAV_BY_ROLE } from './fixtures/navigation';
import { loginAs, logoutViaTopBar } from './helpers/auth';

test.describe('Navegación entre secciones', () => {
  for (const user of E2E_USERS) {
    const routes = E2E_NAV_BY_ROLE[user.rol];
    if (!routes?.length) continue;

    test(`${user.rol}: sidebar lleva a cada sección`, async ({ page }) => {
      await loginAs(page, user);

      for (const route of routes) {
        const navLink = page.getByRole('navigation').getByRole('link', {
          name: route.linkLabel,
          exact: true,
        });
        await expect(navLink).toHaveAttribute('href', route.path);
        await navLink.click();
        await expect(page).toHaveURL(new RegExp(`${route.path.replace('/', '\\/')}`));
        await expect(page.getByRole('heading', { name: /couldn.t load/i })).not.toBeVisible();
        await expect(page.getByRole('heading', { name: route.heading })).toBeVisible({
          timeout: 30_000,
        });
      }
    });
  }
});

test.describe('Cerrar sesión', () => {
  test('logout vuelve a login y bloquea rutas protegidas', async ({ page, context }) => {
    const user = E2E_USERS.find((u) => u.rol === 'SUPERVISOR')!;
    await loginAs(page, user);

    await page.getByRole('link', { name: 'Alertas' }).click();
    await expect(page).toHaveURL(/\/supervisor\/alertas/);

    await logoutViaTopBar(page);
    await expect(page).toHaveURL(/\/login/);
    await expect(page.getByText('FLEX-OP')).toBeVisible();

    await context.clearCookies();
    await page.evaluate(() => localStorage.clear());
    await page.goto('/supervisor');
    await expect(page).toHaveURL(/\/login/, { timeout: 30_000 });
  });

  test('operario puede cerrar sesión desde el dashboard', async ({ page }) => {
    const user = E2E_USERS.find((u) => u.rol === 'OPERARIO')!;
    await loginAs(page, user);
    await expect(page.getByRole('heading', { name: 'Mi Dashboard' })).toBeVisible();

    await logoutViaTopBar(page);
    await expect(page).toHaveURL(/\/login/);
    await expect(page.getByLabel(/usuario/i)).toBeVisible();
  });
});
