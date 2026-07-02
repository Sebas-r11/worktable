import { describe, expect, it } from 'vitest';
import { getStatusVariant } from './statusVariants';

describe('getStatusVariant', () => {
  it('mapea estados operativos', () => {
    expect(getStatusVariant('ACTIVA')).toBe('default');
    expect(getStatusVariant('PENDIENTE')).toBe('secondary');
    expect(getStatusVariant('PARADA')).toBe('destructive');
  });

  it('mapea prioridades criticas', () => {
    expect(getStatusVariant('CRITICA')).toBe('destructive');
    expect(getStatusVariant('BAJA')).toBe('outline');
  });

  it('mapea estados de maquina y alerta', () => {
    expect(getStatusVariant('DISPONIBLE')).toBe('default');
    expect(getStatusVariant('FUERA_SERVICIO')).toBe('destructive');
    expect(getStatusVariant('ESCALADA')).toBe('destructive');
    expect(getStatusVariant('DESCARTADA')).toBe('outline');
    expect(getStatusVariant('EXPIRADA')).toBe('outline');
  });

  it('valor desconocido usa secondary', () => {
    expect(getStatusVariant('DESCONOCIDO')).toBe('secondary');
  });
});
