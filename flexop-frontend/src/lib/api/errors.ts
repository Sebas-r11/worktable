import { isAxiosError } from 'axios';

export function getApiErrorMessage(err: unknown, fallback: string): string {
  if (isAxiosError(err)) {
    if (!err.response) {
      return 'No se pudo conectar con el servidor. Verifica que el backend esté en ejecución.';
    }
    const data = err.response.data as Record<string, unknown> | string;
    if (typeof data === 'string') return data;
    if (typeof data.detail === 'string') return data.detail;
    if (typeof data.error === 'string') return data.error;
    const first = Object.values(data).flat()[0];
    if (typeof first === 'string') return first;
    if (Array.isArray(first) && typeof first[0] === 'string') return first[0];
  }
  if (err instanceof Error && err.message) return err.message;
  return fallback;
}
