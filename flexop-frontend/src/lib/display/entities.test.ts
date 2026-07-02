import { describe, expect, it } from 'vitest';
import {
  getAlertaTexto,
  getMaquinaEstado,
  getMetricaEficiencia,
  getSugerenciaRazonLabel,
} from './entities';
import type { Alerta, Maquina, MetricaEficiencia, SugerenciaReasignacion } from '@/types';

describe('display entities', () => {
  it('getAlertaTexto combina titulo y descripcion', () => {
    const alerta = {
      id: 1,
      titulo: 'Falla',
      descripcion: 'Máquina parada',
      prioridad: 'ALTA',
      estado: 'ACTIVA',
      fecha_creacion: '2026-01-01',
    } as Alerta;
    expect(getAlertaTexto(alerta)).toBe('Falla — Máquina parada');
  });

  it('getMaquinaEstado usa estado_actual', () => {
    const maquina = {
      id: 1,
      codigo: 'M1',
      nombre: 'Torno',
      tipo: 1,
      empresa: 1,
      capacidad_teorica: 100,
      unidad_capacidad: 1,
      estado_actual: 'OPERANDO',
      activa: true,
    } as Maquina;
    expect(getMaquinaEstado(maquina)).toBe('OPERANDO');
  });

  it('getMetricaEficiencia usa eficiencia_calculada', () => {
    const metrica = {
      id: 1,
      operario: 1,
      maquina: 1,
      fecha: '2026-01-01',
      produccion_real: 80,
      produccion_teorica: 100,
      eficiencia_calculada: 80,
    } as MetricaEficiencia;
    expect(getMetricaEficiencia(metrica)).toBe(80);
  });

  it('getMetricaEficiencia convierte strings del API', () => {
    const metrica = {
      id: 1,
      operario: 1,
      maquina: 1,
      fecha: '2026-01-01',
      produccion_real: '80.00',
      produccion_teorica: '100.00',
      eficiencia_calculada: '82.50',
    } as MetricaEficiencia;
    expect(getMetricaEficiencia(metrica)).toBe(82.5);
  });

  it('getSugerenciaRazonLabel prefiere razon_display', () => {
    const s = {
      id: 1,
      operario: 1,
      maquina_destino: 2,
      razon: 'BAJA_EFICIENCIA',
      razon_display: 'Baja eficiencia',
      estado: 'PENDIENTE',
      impacto_estimado: 5,
      fecha_creacion: '2026-01-01',
    } as SugerenciaReasignacion;
    expect(getSugerenciaRazonLabel(s)).toBe('Baja eficiencia');
  });
});
