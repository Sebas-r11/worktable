"""
Tests de API — exportar CSV y reportes generados (B-09).
"""
from datetime import date, timedelta

import pytest
from django.utils import timezone
from rest_framework import status

from metricas.models import MetricaEficiencia
from reportes.models import ReporteGenerado


@pytest.mark.django_db
class TestExportarCSVView:
    def test_requiere_tipo(self, auth_client_gerente):
        response = auth_client_gerente.get(
            '/api/exportar-csv/',
            {'fecha_inicio': '2026-05-01'},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'tipo' in response.data['error'].lower()

    def test_requiere_fecha_inicio(self, auth_client_gerente):
        response = auth_client_gerente.get(
            '/api/exportar-csv/',
            {'tipo': 'eficiencia'},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'fecha_inicio' in response.data['error'].lower()

    def test_tipo_no_soportado(self, auth_client_gerente):
        response = auth_client_gerente.get(
            '/api/exportar-csv/',
            {'tipo': 'inventario', 'fecha_inicio': '2026-05-01'},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_exportar_eficiencia_csv(
        self, auth_client_gerente, asignacion_completada_con_produccion, operario, maquina
    ):
        asignacion = asignacion_completada_con_produccion
        MetricaEficiencia.calcular_para_asignacion(asignacion)
        hoy = date.today().isoformat()

        response = auth_client_gerente.get(
            '/api/exportar-csv/',
            {'tipo': 'eficiencia', 'fecha_inicio': hoy, 'fecha_fin': hoy},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response['Content-Type'] == 'text/csv'
        content = response.content.decode('utf-8')
        assert 'Fecha' in content
        assert 'Eficiencia' in content
        assert maquina.nombre in content

    def test_exportar_produccion_csv(
        self, auth_client_gerente, asignacion_completada_con_produccion, maquina
    ):
        hoy = date.today().isoformat()
        response = auth_client_gerente.get(
            '/api/exportar-csv/',
            {'tipo': 'produccion', 'fecha_inicio': hoy},
        )
        assert response.status_code == status.HTTP_200_OK
        content = response.content.decode('utf-8')
        assert 'Cantidad' in content
        assert maquina.nombre in content

    def test_operario_no_puede_exportar_csv(self, auth_client_operario):
        hoy = date.today().isoformat()
        response = auth_client_operario.get(
            '/api/exportar-csv/',
            {'tipo': 'eficiencia', 'fecha_inicio': hoy},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_supervisor_no_puede_exportar_csv(self, auth_client_supervisor):
        hoy = date.today().isoformat()
        response = auth_client_supervisor.get(
            '/api/exportar-csv/',
            {'tipo': 'produccion', 'fecha_inicio': hoy},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestReporteGeneradoViewSet:
    def test_lista_filtrada_por_empresa(
        self, auth_client_gerente, gerente_user, empresa, empresa_b, supervisor_user
    ):
        ReporteGenerado.objects.create(
            tipo=ReporteGenerado.TipoReporteChoices.EFICIENCIA_DIARIA,
            formato=ReporteGenerado.FormatoChoices.CSV,
            fecha_inicio=date.today(),
            fecha_fin=date.today(),
            empresa=empresa,
            generado_por=gerente_user,
        )
        ReporteGenerado.objects.create(
            tipo=ReporteGenerado.TipoReporteChoices.KPI_GERENCIAL,
            formato=ReporteGenerado.FormatoChoices.PDF,
            fecha_inicio=date.today(),
            fecha_fin=date.today(),
            empresa=empresa_b,
            generado_por=supervisor_user,
        )

        response = auth_client_gerente.get('/api/reportes-generados/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['empresa'] == empresa.id

    def test_detalle_reporte(self, auth_client_gerente, gerente_user, empresa):
        reporte = ReporteGenerado.objects.create(
            tipo=ReporteGenerado.TipoReporteChoices.PRODUCCION_DIARIA,
            formato=ReporteGenerado.FormatoChoices.CSV,
            fecha_inicio=date.today() - timedelta(days=7),
            fecha_fin=date.today(),
            empresa=empresa,
            generado_por=gerente_user,
            parametros={'origen': 'test'},
        )
        response = auth_client_gerente.get(f'/api/reportes-generados/{reporte.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['tipo'] == 'PRODUCCION_DIARIA'
        assert response.data['parametros']['origen'] == 'test'

    def test_eliminar_reporte(self, auth_client_gerente, gerente_user, empresa):
        reporte = ReporteGenerado.objects.create(
            tipo=ReporteGenerado.TipoReporteChoices.INCIDENCIAS,
            formato=ReporteGenerado.FormatoChoices.CSV,
            fecha_inicio=date.today(),
            fecha_fin=date.today(),
            empresa=empresa,
            generado_por=gerente_user,
        )
        response = auth_client_gerente.delete(f'/api/reportes-generados/{reporte.id}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not ReporteGenerado.objects.filter(pk=reporte.id).exists()

    def test_operario_no_ve_reportes_otra_empresa(
        self, auth_client_operario, gerente_user, empresa_b
    ):
        reporte = ReporteGenerado.objects.create(
            tipo=ReporteGenerado.TipoReporteChoices.EFICIENCIA_DIARIA,
            formato=ReporteGenerado.FormatoChoices.CSV,
            fecha_inicio=date.today(),
            fecha_fin=date.today(),
            empresa=empresa_b,
            generado_por=gerente_user,
        )
        response = auth_client_operario.get(f'/api/reportes-generados/{reporte.id}/')
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_descargar_reporte_autenticado(
        self, auth_client_gerente, gerente_user, empresa, settings, tmp_path
    ):
        from django.core.files.uploadedfile import SimpleUploadedFile

        settings.MEDIA_ROOT = tmp_path
        reporte = ReporteGenerado.objects.create(
            tipo=ReporteGenerado.TipoReporteChoices.EFICIENCIA_DIARIA,
            formato=ReporteGenerado.FormatoChoices.CSV,
            fecha_inicio=date.today(),
            fecha_fin=date.today(),
            empresa=empresa,
            generado_por=gerente_user,
            archivo=SimpleUploadedFile(
                'test.csv',
                b'Fecha,Eficiencia\n2026-05-28,80',
                content_type='text/csv',
            ),
        )
        response = auth_client_gerente.get(
            f'/api/reportes-generados/{reporte.id}/descargar/'
        )
        assert response.status_code == status.HTTP_200_OK
        content = b''.join(response.streaming_content)
        assert b'Eficiencia' in content
