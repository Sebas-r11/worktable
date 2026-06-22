'use client';

export interface MetricasChartPoint {
  nombre: string;
  eficiencia: number;
}

/** Gráfico liviano sin recharts (evita fallos de chunk en producción/E2E). */
export function MetricasChart({ data }: { data: MetricasChartPoint[] }) {
  if (data.length === 0) return null;

  const max = Math.max(...data.map((d) => d.eficiencia), 1);

  return (
    <div className="space-y-3 min-h-[200px]" data-testid="metricas-chart">
      {data.map((d) => (
        <div key={d.nombre} className="flex items-center gap-3">
          <span className="w-28 truncate text-xs text-muted-foreground">{d.nombre}</span>
          <div className="flex-1 h-7 rounded-md bg-slate-100 overflow-hidden">
            <div
              className="h-full rounded-md bg-primary transition-all"
              style={{ width: `${(d.eficiencia / max) * 100}%` }}
            />
          </div>
          <span className="w-12 text-right text-xs font-medium">{d.eficiencia}%</span>
        </div>
      ))}
    </div>
  );
}
