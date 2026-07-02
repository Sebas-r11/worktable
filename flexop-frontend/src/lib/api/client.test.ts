import { beforeEach, describe, expect, it, vi } from 'vitest';
import Cookies from 'js-cookie';

vi.mock('js-cookie', () => ({
  default: {
    get: vi.fn(),
    set: vi.fn(),
    remove: vi.fn(),
  },
}));

describe('token helpers', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('saveTokens guarda access y refresh', async () => {
    const { saveTokens } = await import('./client');
    saveTokens('access-123', 'refresh-456');
    expect(Cookies.set).toHaveBeenCalledWith('flexop_access', 'access-123', { sameSite: 'strict' });
    expect(Cookies.set).toHaveBeenCalledWith('flexop_refresh', 'refresh-456', { sameSite: 'strict' });
  });

  it('clearTokens elimina ambos tokens', async () => {
    const { clearTokens } = await import('./client');
    clearTokens();
    expect(Cookies.remove).toHaveBeenCalledWith('flexop_access');
    expect(Cookies.remove).toHaveBeenCalledWith('flexop_refresh');
  });

  it('getAccessToken lee cookie', async () => {
    vi.mocked(Cookies.get).mockReturnValue('token-abc');
    const { getAccessToken } = await import('./client');
    expect(getAccessToken()).toBe('token-abc');
  });
});
