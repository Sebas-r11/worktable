'use client';

import { useState } from 'react';
import { reportesApi } from '@/lib/api';
import { downloadBlob } from '@/lib/download';
import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from '@/components/ui/table';
import { PageLoader } from '@/components/shared/LoadingSpinner';
import { EmptyState } from '@/components/shared/EmptyState';
import { PaginationBar } from '@/components/shared/PaginationBar';
import { FileText, Download } from 'lucide-react';
import { toast } from 'sonner';
import type { ReporteGenerado } from '@/types';
import { formatFechaApi } from '@/lib/display/entities';

export default function GerenteReportesPage() {
  const [page, setPage] = useState(1);
  const { data, isLoading } = useQuery({
    queryKey: ['reportes-generados', page],
    queryFn: () => reportesApi.reportesGenerados({ page }).then((r) => r.data),
  });

  const handleExportCSV = async () => {
    try {
      const hoy = new Date().toISOString().slice(0, 10);
      const hace7 = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10);
      const response = await reportesApi.exportarCSV({
        tipo: 'eficiencia',
        fecha_inicio: hace7,
        fecha_fin: hoy,
      });
      downloadBlob(
        new Blob([response.data]),
        `flexop_reporte_${new Date().toISOString().slice(0, 10)}.csv`,
      );
      toast.success('Reporte CSV descargado');
    } catch {
      toast.error('Error al exportar reporte');
    }
  };

  const handleDownloadReporte = async (id: number, tipo: string) => {
    try {
      const response = await reportesApi.descargarReporte(id);
      downloadBlob(response.data as Blob, `reporte_${tipo}_${id}.csv`);
      toast.success('Reporte descargado');
    } catch {
      toast.error('Error al descargar reporte');
    }
  };

  if (isLoading) return <PageLoader />;

  const reportes = Array.isArray(data?.results) ? data.results : [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <FileText className="h-6 w-6" /> Reportes
        </h1>
        <Button size="sm" onClick={handleExportCSV}>
          <Download className="h-4 w-4 mr-2" /> Exportar CSV
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm text-muted-foreground">Historial de reportes generados</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          {reportes.length === 0 ? (
            <EmptyState
              title="Sin reportes"
              description="No hay reportes generados todavía. Usa el botón de exportar para crear uno."
              icon={FileText}
              className="py-16"
            />
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Reporte</TableHead>
                  <TableHead>Tipo</TableHead>
                  <TableHead>Formato</TableHead>
                  <TableHead>Generado</TableHead>
                  <TableHead className="text-right">Descargar</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {reportes.map((r: ReporteGenerado) => (
                  <TableRow key={r.id}>
                    <TableCell className="font-medium">
                      {r.tipo_display ?? r.tipo} #{r.id}
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">{r.tipo_display ?? r.tipo}</TableCell>
                    <TableCell className="text-sm text-muted-foreground">{r.formato_display ?? r.formato}</TableCell>
                    <TableCell className="text-xs text-muted-foreground">
                      {r.fecha_generacion ? formatFechaApi(r.fecha_generacion) : '—'}
                    </TableCell>
                    <TableCell className="text-right">
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() =>
                          handleDownloadReporte(
                            r.id,
                            r.tipo_display ?? r.tipo,
                          )
                        }
                      >
                        <Download className="h-4 w-4" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
          <PaginationBar
            page={page}
            total={data?.count ?? 0}
            onPageChange={setPage}
          />
        </CardContent>
      </Card>
    </div>
  );
}
