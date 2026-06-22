import type { Page } from '@playwright/test';
import type { E2EUser } from '../fixtures/users';

export async function loginAs(page: Page, user: E2EUser) {
  await page.goto('/login');
  await page.getByLabel(/usuario/i).fill(user.username);
  await page.getByLabel(/contraseña/i).fill(user.password);
  await page.getByRole('button', { name: /iniciar sesión/i }).click();
  await page.waitForURL(`**${user.expectedPath}**`, { timeout: 45_000 });
  await page.getByRole('heading', { name: user.expectedHeading }).waitFor({ state: 'visible' });
}

export async function logoutViaTopBar(page: Page) {
  const avatarBtn = page.locator('header button').last();
  await avatarBtn.click();
  await page.getByRole('menuitem', { name: /cerrar sesión/i }).click();
  await page.waitForURL('**/login', { timeout: 30_000 });
}
