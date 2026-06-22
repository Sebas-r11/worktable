"""
Tests de permisos — UserViewSet (Fase 2.5).
"""
import pytest
from rest_framework import status

from usuarios.models import User


@pytest.mark.django_db
class TestUserPermissions:
    def test_supervisor_no_puede_delete_usuario(
        self, auth_client_supervisor, operario_user
    ):
        response = auth_client_supervisor.delete(
            f'/api/usuarios/{operario_user.id}/'
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert User.objects.filter(pk=operario_user.id).exists()

    def test_usuario_puede_patch_propio_perfil(
        self, auth_client_operario, operario_user
    ):
        response = auth_client_operario.patch(
            f'/api/usuarios/{operario_user.id}/',
            {'first_name': 'NombrePropio'},
            format='json',
        )
        assert response.status_code == status.HTTP_200_OK
        operario_user.refresh_from_db()
        assert operario_user.first_name == 'NombrePropio'

    def test_supervisor_no_puede_patch_otro_usuario(
        self, auth_client_supervisor, operario_user
    ):
        response = auth_client_supervisor.patch(
            f'/api/usuarios/{operario_user.id}/',
            {'first_name': 'NoPermitido'},
            format='json',
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_puede_delete_usuario(self, auth_client_admin, operario_user):
        user_id = operario_user.id
        response = auth_client_admin.delete(f'/api/usuarios/{user_id}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not User.objects.filter(pk=user_id).exists()
