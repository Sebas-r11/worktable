"""
Tests de API — dashboards y permisos por rol.
"""
import pytest
from rest_framework import status

from alertas.models import Notificacion


@pytest.mark.django_db
class TestDashboardPermisos:
    def test_dashboard_operario_ok(self, auth_client_operario, operario):
        response = auth_client_operario.get('/api/dashboard/operario/')
        assert response.status_code == status.HTTP_200_OK
        assert 'eficiencia_hoy' in response.data

    def test_dashboard_operario_rechaza_supervisor(self, auth_client_supervisor):
        response = auth_client_supervisor.get('/api/dashboard/operario/')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_dashboard_supervisor_ok(self, auth_client_supervisor):
        response = auth_client_supervisor.get('/api/dashboard/supervisor/')
        assert response.status_code == status.HTTP_200_OK
        assert 'maquinas_estado' in response.data

    def test_dashboard_supervisor_rechaza_operario(self, auth_client_operario):
        response = auth_client_operario.get('/api/dashboard/supervisor/')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_dashboard_gerente_ok(self, auth_client_gerente):
        response = auth_client_gerente.get('/api/dashboard/gerente/')
        assert response.status_code == status.HTTP_200_OK
        assert 'oee_aproximado' in response.data

    def test_dashboard_gerente_con_metricas(
        self, auth_client_gerente, asignacion_completada_con_produccion
    ):
        from metricas.models import MetricaEficiencia

        MetricaEficiencia.calcular_para_asignacion(asignacion_completada_con_produccion)
        response = auth_client_gerente.get('/api/dashboard/gerente/')
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data['oee_aproximado'], (int, float))

    def test_dashboard_gerente_rechaza_operario(self, auth_client_operario):
        response = auth_client_operario.get('/api/dashboard/gerente/')
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestIncidenciaEscalar:
    def test_escalar_crea_notificaciones_gerente(
        self, auth_client_supervisor, maquina, operario_user, gerente_user
    ):
        from operaciones.models import Incidencia

        incidencia = Incidencia.objects.create(
            maquina=maquina,
            tipo=Incidencia.TipoChoices.FALLA_MAQUINA,
            titulo='Falla critica',
            descripcion='Test escalamiento',
            reportado_por=operario_user,
        )
        url = f'/api/incidencias/{incidencia.id}/escalar/'
        response = auth_client_supervisor.post(
            url, {'motivo': 'Sin resolver 2h'}, format='json'
        )
        assert response.status_code == status.HTTP_200_OK
        incidencia.refresh_from_db()
        assert incidencia.estado == 'ESCALADA'
        assert Notificacion.objects.filter(usuario=gerente_user).exists()
