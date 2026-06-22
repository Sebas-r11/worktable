"""
Tests de API — app reasignaciones.
"""
import pytest
from rest_framework import status

from maquinas.models import Maquina
from reasignaciones.models import SugerenciaReasignacion


@pytest.mark.django_db
class TestSugerenciasAPI:
    def test_generar_sugerencias(
        self, auth_client_supervisor, empresa, operario, maquina
    ):
        maquina.estado_actual = Maquina.EstadoChoices.DISPONIBLE
        maquina.save()
        operario.disponible = True
        operario.save()

        response = auth_client_supervisor.post(
            '/api/sugerencias/generar/',
            {},
            format='json',
        )
        assert response.status_code == status.HTTP_200_OK
        assert 'mensaje' in response.data

    def test_generar_otra_empresa_prohibido(
        self, auth_client_supervisor, empresa_b
    ):
        response = auth_client_supervisor.post(
            '/api/sugerencias/generar/',
            {'empresa_id': empresa_b.id},
            format='json',
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_aceptar_sugerencia_api(
        self, auth_client_supervisor, empresa, operario, maquina, turno, supervisor_user
    ):
        sugerencia = SugerenciaReasignacion.objects.create(
            operario=operario,
            maquina_destino=maquina,
            razon=SugerenciaReasignacion.RazonChoices.MAQUINA_DISPONIBLE,
            descripcion='API test',
            empresa=empresa,
        )
        response = auth_client_supervisor.post(
            f'/api/sugerencias/{sugerencia.id}/aceptar/',
            {'notas': 'OK'},
            format='json',
        )
        assert response.status_code == status.HTTP_200_OK
        assert 'asignacion_creada' in response.data
