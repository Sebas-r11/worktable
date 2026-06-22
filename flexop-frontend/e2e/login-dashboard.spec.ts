import { test, expect } from '@playwright/test';
import { E2E_USERS } from './fixtures/users';
import { loginAs } from './helpers/auth';

test.describe('Login → dashboard por rol', () => {
  for (const user of E2E_USERS) {
    test(`${user.rol}: redirige y muestra navegación`, async ({ page }) => {
      await loginAs(page, user);

      await expect(page).toHaveURL(new RegExp(`${user.expectedPath.replace('/', '\\/')}`));
      await expect(page.getByRole('heading', { name: user.expectedHeading })).toBeVisible();
      await expect(page.getByRole('link', { name: user.expectedNavItem })).toBeVisible();
    });
  }

  test('credenciales inválidas muestran error', async ({ page }) => {
    await page.goto('/login');
    await page.getByLabel(/usuario/i).fill('usuario_inexistente');
    await page.getByLabel(/contraseña/i).fill('mal');
    const loginFailed = page.waitForResponse(
      (res) => res.url().includes('/auth/login') && res.status() === 401,
    );
    await page.getByRole('button', { name: /iniciar sesión/i }).click();
    await loginFailed;

    await expect(page).toHaveURL(/\/login/);
    await expect(
      page.getByRole('alert').filter({ hasText: /active account|credencial/i }),
    ).toBeVisible({ timeout: 15_000 });
  });

  test('ruta protegida sin sesión redirige a login', async ({ page, context }) => {
    await context.clearCookies();
    await page.goto('/login');
    await page.evaluate(() => localStorage.clear());
    await page.goto('/gerente');
    await expect(page).toHaveURL(/\/login/, { timeout: 30_000 });
    await expect(page.getByText('FLEX-OP')).toBeVisible();
  });
});
