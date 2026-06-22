"""
Tests de permisos — EmpresaViewSet (Fase 2.1).
"""
import pytest
from rest_framework import status


@pytest.mark.django_db
class TestEmpresaPermissions:
    def test_operario_no_puede_patch_empresa(self, auth_client_operario, empresa):
        response = auth_client_operario.patch(
            f'/api/empresas/{empresa.id}/',
            {'nombre': 'Nombre hackeado'},
            format='json',
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        empresa.refresh_from_db()
        assert empresa.nombre == 'Empresa Test'

    def test_admin_puede_patch_empresa(self, auth_client_admin, empresa):
        response = auth_client_admin.patch(
            f'/api/empresas/{empresa.id}/',
            {'nombre': 'Empresa Actualizada'},
            format='json',
        )
        assert response.status_code == status.HTTP_200_OK
        empresa.refresh_from_db()
        assert empresa.nombre == 'Empresa Actualizada'

    def test_supervisor_puede_listar_su_empresa(self, auth_client_supervisor, empresa):
        response = auth_client_supervisor.get('/api/empresas/')
        assert response.status_code == status.HTTP_200_OK
        ids = {item['id'] for item in response.data['results']}
        assert empresa.id in ids

    def test_operario_no_puede_crear_empresa(self, auth_client_operario):
        response = auth_client_operario.post(
            '/api/empresas/',
            {
                'nombre': 'Empresa Nueva',
                'razon_social': 'Nueva SAC',
                'ruc': '20111111111',
                'email': 'nueva@test.com',
            },
            format='json',
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
