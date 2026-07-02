import type { Alerta, Maquina, MetricaEficiencia, SugerenciaReasignacion } from '@/types';

export function getAlertaTexto(alerta: Alerta): string {
  if (alerta.titulo && alerta.descripcion && alerta.titulo !== alerta.descripcion) {
    return `${alerta.titulo} — ${alerta.descripcion}`;
  }
  return alerta.titulo || alerta.descripcion || '';
}

export function getMaquinaEstado(maquina: Maquina): string {
  return maquina.estado_actual;
}

function toNumber(value: string | number | null | undefined): number {
  const n = Number(value);
  return Number.isFinite(n) ? n : 0;
}

/** El API Django devuelve DecimalField como string en JSON. */
export function getMetricaEficiencia(metrica: MetricaEficiencia): number {
  return toNumber(metrica.eficiencia_calculada);
}

export function getMetricaObjetivo(metrica: MetricaEficiencia): number {
  return toNumber(metrica.produccion_teorica);
}

export function getSugerenciaImpacto(s: SugerenciaReasignacion): number {
  return toNumber(s.impacto_estimado);
}

export function getSugerenciaRazonLabel(s: SugerenciaReasignacion): string {
  return s.razon_display ?? s.razon;
}

export function getSugerenciaOperarioLabel(s: SugerenciaReasignacion): string {
  return s.operario_codigo ?? s.operario_nombre ?? `#${s.operario}`;
}

export function getSugerenciaMaquinaDestinoLabel(s: SugerenciaReasignacion): string {
  return s.maquina_destino_codigo ?? s.maquina_destino_nombre ?? `#${s.maquina_destino}`;
}

export function formatFechaApi(value: string): string {
  return new Date(value).toLocaleString('es');
}
