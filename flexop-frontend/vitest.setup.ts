import '@testing-library/jest-dom/vitest';
import axios from 'axios';
import { cleanup } from '@testing-library/react';
import { afterAll, afterEach, beforeAll, vi } from 'vitest';
import { server } from '@/test/msw/server';

// Axios debe usar fetch para que MSW intercepte en Vitest/jsdom
axios.defaults.adapter = 'fetch';

beforeAll(() => {
  server.listen({ onUnhandledRequest: 'warn' });
});

afterEach(() => {
  server.resetHandlers();
  cleanup();
});

afterAll(() => {
  server.close();
});

vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn(),
    prefetch: vi.fn(),
    back: vi.fn(),
  }),
  usePathname: () => '/operario',
  useSearchParams: () => new URLSearchParams(),
}));
