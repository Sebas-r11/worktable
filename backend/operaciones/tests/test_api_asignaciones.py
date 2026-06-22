"""
Tests de API — asignaciones y autenticación.
"""
import pytest
from rest_framework import status


@pytest.mark.django_db
class TestAuth:
    def test_login_exitoso(self, api_client, supervisor_user):
        response = api_client.post(
            '/api/auth/login/',
            {'username': 'supervisor_test', 'password': 'TestPass123!'},
            format='json',
        )
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data

    def test_login_credenciales_invalidas(self, api_client):
        response = api_client.post(
            '/api/auth/login/',
            {'username': 'noexiste', 'password': 'wrong'},
            format='json',
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestAsignacionAPI:
    def test_listar_asignaciones_requiere_autenticacion(self, api_client):
        response = api_client.get('/api/asignaciones/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_listar_asignaciones_autenticado(
        self, auth_client_supervisor, asignacion_pendiente
    ):
        response = auth_client_supervisor.get('/api/asignaciones/')
        assert response.status_code == status.HTTP_200_OK
        ids = [item['id'] for item in response.data['results']]
        assert asignacion_pendiente.id in ids

    def test_iniciar_asignacion(
        self, auth_client_supervisor, asignacion_pendiente
    ):
        url = f'/api/asignaciones/{asignacion_pendiente.id}/iniciar/'
        response = auth_client_supervisor.post(url)
        assert response.status_code == status.HTTP_200_OK
        asignacion_pendiente.refresh_from_db()
        assert asignacion_pendiente.estado == 'ACTIVA'

    def test_finalizar_asignacion(
        self, auth_client_supervisor, asignacion_pendiente
    ):
        iniciar_url = f'/api/asignaciones/{asignacion_pendiente.id}/iniciar/'
        auth_client_supervisor.post(iniciar_url)

        finalizar_url = f'/api/asignaciones/{asignacion_pendiente.id}/finalizar/'
        response = auth_client_supervisor.post(finalizar_url, {}, format='json')
        assert response.status_code == status.HTTP_200_OK
        asignacion_pendiente.refresh_from_db()
        assert asignacion_pendiente.estado == 'COMPLETADA'

    def test_usuario_me(self, auth_client_operario, operario_user):
        response = auth_client_operario.get('/api/usuarios/me/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == operario_user.username
        assert response.data['rol'] == 'OPERARIO'

    def test_eliminar_asignacion_pendiente(
        self, auth_client_supervisor, asignacion_pendiente
    ):
        url = f'/api/asignaciones/{asignacion_pendiente.id}/'
        response = auth_client_supervisor.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_no_eliminar_asignacion_completada(
        self, auth_client_supervisor, asignacion_pendiente
    ):
        auth_client_supervisor.post(
            f'/api/asignaciones/{asignacion_pendiente.id}/iniciar/'
        )
        auth_client_supervisor.post(
            f'/api/asignaciones/{asignacion_pendiente.id}/finalizar/',
            {},
            format='json',
        )
        response = auth_client_supervisor.delete(
            f'/api/asignaciones/{asignacion_pendiente.id}/'
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
