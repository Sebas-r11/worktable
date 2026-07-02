import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import Cookies from 'js-cookie';

/** En navegador usamos /api (proxy Next → Django). En SSR/tests se puede fijar la URL completa. */
function normalizeApiBaseUrl(url: string): string {
  const trimmed = url.replace(/\/+$/, '');
  return `${trimmed}/`;
}

const BASE_URL = normalizeApiBaseUrl(
  process.env.NEXT_PUBLIC_API_URL ??
    (typeof window !== 'undefined' ? '/api' : 'http://127.0.0.1:8000/api'),
);

const ACCESS_TOKEN_KEY = 'flexop_access';
const REFRESH_TOKEN_KEY = 'flexop_refresh';

// ─── Instancia principal ──────────────────────────────────────────
const apiClient: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,
  // MSW intercepta fetch en Vitest (evita XHR + headers internos de axios)
  adapter: typeof process !== 'undefined' && process.env.VITEST ? 'fetch' : undefined,
});

// ─── Request interceptor: adjunta access token ───────────────────
apiClient.interceptors.request.use(
  (config) => {
    const token = Cookies.get(ACCESS_TOKEN_KEY);
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// ─── Response interceptor: refresca token si expira ──────────────
let isRefreshing = false;
let failedQueue: Array<{
  resolve: (token: string) => void;
  reject: (err: unknown) => void;
}> = [];

function processQueue(error: unknown, token: string | null = null) {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) {
      reject(error);
    } else if (token) {
      resolve(token);
    }
  });
  failedQueue = [];
}

apiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error) => {
    const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean };

    const url = originalRequest.url ?? '';
    const isAuthEndpoint =
      url.includes('/auth/login') ||
      url.includes('/auth/refresh') ||
      url.includes('/auth/verify');

    if (error.response?.status === 401 && !originalRequest._retry && !isAuthEndpoint) {
      if (isRefreshing) {
        // Cola de requests mientras se refresca el token
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            if (originalRequest.headers) {
              (originalRequest.headers as Record<string, string>).Authorization = `Bearer ${token}`;
            }
            return apiClient(originalRequest);
          })
          .catch((err) => Promise.reject(err));
      }

      originalRequest._retry = true;
      isRefreshing = true;

      const refreshToken = Cookies.get(REFRESH_TOKEN_KEY);
      if (!refreshToken) {
        clearTokens();
        window.location.href = '/login';
        return Promise.reject(error);
      }

      try {
        const { data } = await axios.post(`${BASE_URL}/auth/refresh/`, {
          refresh: refreshToken,
        });

        const newAccessToken: string = data.access;
        Cookies.set(ACCESS_TOKEN_KEY, newAccessToken, { sameSite: 'strict' });
        processQueue(null, newAccessToken);
        if (originalRequest.headers) {
          (originalRequest.headers as Record<string, string>).Authorization = `Bearer ${newAccessToken}`;
        }
        return apiClient(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError, null);
        clearTokens();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

// ─── Helpers de tokens ────────────────────────────────────────────
export function saveTokens(access: string, refresh: string) {
  // sameSite: 'strict' previene CSRF. No usamos httpOnly porque es client-side.
  Cookies.set(ACCESS_TOKEN_KEY, access, { sameSite: 'strict' });
  Cookies.set(REFRESH_TOKEN_KEY, refresh, { sameSite: 'strict' });
}

export function clearTokens() {
  Cookies.remove(ACCESS_TOKEN_KEY);
  Cookies.remove(REFRESH_TOKEN_KEY);
}

export function getAccessToken(): string | undefined {
  return Cookies.get(ACCESS_TOKEN_KEY);
}

export function getRefreshToken(): string | undefined {
  return Cookies.get(REFRESH_TOKEN_KEY);
}

export default apiClient;
