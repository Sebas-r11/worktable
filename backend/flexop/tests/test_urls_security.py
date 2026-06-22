"""
Tests de URLs y documentación API (Fase 3.3).
"""
import pytest
from django.test import Client, override_settings
from rest_framework import status


@pytest.mark.django_db
class TestSwaggerDebugOnly:
    def test_swagger_disponible_en_debug(self):
        client = Client()
        with override_settings(DEBUG=True, ALLOWED_HOSTS=['testserver']):
            response = client.get('/swagger/')
        assert response.status_code == status.HTTP_200_OK

    def test_swagger_no_disponible_en_produccion(self):
        client = Client()
        with override_settings(DEBUG=False, ALLOWED_HOSTS=['testserver']):
            response = client.get('/swagger/')
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_redoc_no_disponible_en_produccion(self):
        client = Client()
        with override_settings(DEBUG=False, ALLOWED_HOSTS=['testserver']):
            response = client.get('/redoc/')
        assert response.status_code == status.HTTP_404_NOT_FOUND
