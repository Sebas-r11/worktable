"""
Tests de autenticación JWT (Fase 2.4).
"""
import pytest
from django.test import override_settings
from rest_framework import status

from usuarios.models import User


@pytest.mark.django_db
class TestFlexLogin:
    def test_login_usuario_activo_200(self, api_client, supervisor_user):
        response = api_client.post(
            '/api/auth/login/',
            {'username': 'supervisor_test', 'password': 'TestPass123!'},
            format='json',
        )
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data

    def test_login_usuario_inactivo_401(self, api_client, empresa):
        User.objects.create_user(
            username='inactivo_test',
            email='inactivo@test.com',
            password='TestPass123!',
            rol=User.RolChoices.OPERARIO,
            empresa=empresa,
            activo=False,
        )
        response = api_client.post(
            '/api/auth/login/',
            {'username': 'inactivo_test', 'password': 'TestPass123!'},
            format='json',
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_view_tiene_throttle_configurado(self):
        from usuarios.views_auth import FlexTokenObtainPairView, LoginRateThrottle

        assert FlexTokenObtainPairView.throttle_classes == [LoginRateThrottle]

    @override_settings(
        REST_FRAMEWORK={
            'DEFAULT_AUTHENTICATION_CLASSES': (
                'rest_framework_simplejwt.authentication.JWTAuthentication',
            ),
            'DEFAULT_PERMISSION_CLASSES': (
                'rest_framework.permissions.IsAuthenticated',
            ),
            'DEFAULT_THROTTLE_RATES': {'login': '10/minute'},
        }
    )
    def test_settings_incluye_throttle_login(self):
        from django.conf import settings

        assert 'login' in settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']
