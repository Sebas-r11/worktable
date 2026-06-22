"""
Tests de permisos — AlertaViewSet (Fase 2.2).
"""
import pytest
from rest_framework import status

from alertas.models import Alerta


@pytest.fixture
def alerta_activa(empresa, supervisor_user):
    return Alerta.objects.create(
        titulo='Alerta test permisos',
        descripcion='Descripcion test',
        prioridad='MEDIA',
        estado=Alerta.EstadoChoices.ACTIVA,
        empresa=empresa,
    )


@pytest.mark.django_db
class TestAlertaPermissions:
    def test_operario_no_puede_resolver_alerta(
        self, auth_client_operario, alerta_activa
    ):
        response = auth_client_operario.post(
            f'/api/alertas/{alerta_activa.id}/resolver/',
            {'notas': 'Intento operario'},
            format='json',
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        alerta_activa.refresh_from_db()
        assert alerta_activa.estado == Alerta.EstadoChoices.ACTIVA

    def test_supervisor_puede_resolver_alerta(
        self, auth_client_supervisor, alerta_activa, supervisor_user
    ):
        response = auth_client_supervisor.post(
            f'/api/alertas/{alerta_activa.id}/resolver/',
            {'notas': 'Resuelta por supervisor'},
            format='json',
        )
        assert response.status_code == status.HTTP_200_OK
        alerta_activa.refresh_from_db()
        assert alerta_activa.estado == Alerta.EstadoChoices.RESUELTA

    def test_operario_no_puede_escalar_alerta(
        self, auth_client_operario, alerta_activa
    ):
        response = auth_client_operario.post(
            f'/api/alertas/{alerta_activa.id}/escalar/',
            {'notas': 'Intento escalar'},
            format='json',
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_operario_puede_listar_alertas(
        self, auth_client_operario, alerta_activa
    ):
        response = auth_client_operario.get('/api/alertas/')
        assert response.status_code == status.HTTP_200_OK
