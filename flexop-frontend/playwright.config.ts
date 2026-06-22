import { defineConfig, devices } from '@playwright/test';

const BACKEND_PORT = process.env.PLAYWRIGHT_BACKEND_PORT ?? '8010';
const FRONTEND_PORT = process.env.PLAYWRIGHT_FRONTEND_PORT ?? '3010';
const BACKEND_URL = process.env.PLAYWRIGHT_BACKEND_URL ?? `http://127.0.0.1:${BACKEND_PORT}`;
const FRONTEND_URL = process.env.PLAYWRIGHT_BASE_URL ?? `http://127.0.0.1:${FRONTEND_PORT}`;
const isCI = !!process.env.CI;

export default defineConfig({
  testDir: './e2e',
  fullyParallel: false,
  forbidOnly: isCI,
  retries: isCI ? 2 : 0,
  workers: 1,
  timeout: 60_000,
  expect: { timeout: 15_000 },
  reporter: isCI ? [['github'], ['html', { open: 'never' }]] : [['html', { open: 'on-failure' }]],
  use: {
    baseURL: FRONTEND_URL,
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  webServer: [
    {
      command: 'bash ../scripts/e2e-backend.sh',
      url: `${BACKEND_URL}/admin/login/`,
      reuseExistingServer: !isCI,
      timeout: 180_000,
      cwd: '.',
      env: { E2E_BACKEND_PORT: BACKEND_PORT },
    },
    {
      command: 'bash ../scripts/e2e-frontend.sh',
      url: FRONTEND_URL,
      reuseExistingServer: !isCI,
      timeout: isCI ? 300_000 : 240_000,
      env: {
        PLAYWRIGHT_FRONTEND_PORT: FRONTEND_PORT,
        PLAYWRIGHT_BACKEND_URL: BACKEND_URL,
      },
    },
  ],
});
