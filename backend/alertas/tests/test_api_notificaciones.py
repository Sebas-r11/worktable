"""
Tests API de notificaciones (Fase 1.3 — solo lectura + acciones de marca).
"""
import pytest
from rest_framework import status

from alertas.models import Notificacion


@pytest.fixture
def notificacion_supervisor(supervisor_user):
    return Notificacion.objects.create(
        usuario=supervisor_user,
        titulo='Alerta de prueba',
        mensaje='Mensaje de prueba',
        leida=False,
    )


@pytest.fixture
def notificacion_otro_usuario(admin_user):
    return Notificacion.objects.create(
        usuario=admin_user,
        titulo='Solo admin',
        mensaje='No visible para supervisor',
        leida=False,
    )


@pytest.mark.django_db
class TestNotificacionApi:
    def test_lista_solo_notificaciones_del_usuario(
        self,
        auth_client_supervisor,
        notificacion_supervisor,
        notificacion_otro_usuario,
    ):
        response = auth_client_supervisor.get('/api/notificaciones/')
        assert response.status_code == status.HTTP_200_OK
        ids = {item['id'] for item in response.data['results']}
        assert notificacion_supervisor.id in ids
        assert notificacion_otro_usuario.id not in ids

    def test_post_crear_notificacion_no_permitido(
        self,
        auth_client_supervisor,
        admin_user,
    ):
        response = auth_client_supervisor.post(
            '/api/notificaciones/',
            {
                'usuario': admin_user.id,
                'titulo': 'Inyeccion',
                'mensaje': 'No deberia crearse',
            },
            format='json',
        )
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        assert not Notificacion.objects.filter(titulo='Inyeccion').exists()

    def test_patch_no_cambia_usuario(
        self,
        auth_client_supervisor,
        notificacion_supervisor,
        admin_user,
    ):
        response = auth_client_supervisor.patch(
            f'/api/notificaciones/{notificacion_supervisor.id}/',
            {'usuario': admin_user.id, 'titulo': 'Titulo editado'},
            format='json',
        )
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_marcar_leida(
        self,
        auth_client_supervisor,
        notificacion_supervisor,
    ):
        response = auth_client_supervisor.post(
            f'/api/notificaciones/{notificacion_supervisor.id}/marcar_leida/'
        )
        assert response.status_code == status.HTTP_200_OK
        notificacion_supervisor.refresh_from_db()
        assert notificacion_supervisor.leida is True

    def test_marcar_todas_leidas(
        self,
        auth_client_supervisor,
        supervisor_user,
    ):
        Notificacion.objects.create(
            usuario=supervisor_user,
            titulo='N1',
            mensaje='M1',
            leida=False,
        )
        Notificacion.objects.create(
            usuario=supervisor_user,
            titulo='N2',
            mensaje='M2',
            leida=False,
        )
        response = auth_client_supervisor.post('/api/notificaciones/marcar_todas_leidas/')
        assert response.status_code == status.HTTP_200_OK
        assert (
            Notificacion.objects.filter(usuario=supervisor_user, leida=False).count()
            == 0
        )
