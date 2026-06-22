"""
Tests de archivos estáticos y media en modo producción (Fase #29).
"""
import pytest
from django.core.management import call_command
from django.test import Client, override_settings
from rest_framework import status


@pytest.mark.django_db
class TestStaticMediaProd:
    def test_admin_css_disponible_tras_collectstatic(self, settings, tmp_path):
        settings.STATIC_ROOT = tmp_path / 'staticfiles'
        settings.STATICFILES_STORAGE = (
            'django.contrib.staticfiles.storage.StaticFilesStorage'
        )
        call_command('collectstatic', '--noinput', verbosity=0)
        client = Client()
        with override_settings(DEBUG=False, ALLOWED_HOSTS=['testserver']):
            response = client.get('/static/admin/css/base.css')
        assert response.status_code == status.HTTP_200_OK

    def test_media_url_cuando_serve_media(self, settings, tmp_path):
        media_root = tmp_path / 'media'
        media_root.mkdir()
        (media_root / 'probe.txt').write_text('ok', encoding='utf-8')
        settings.MEDIA_ROOT = media_root
        client = Client()
        with override_settings(
            DEBUG=False,
            ALLOWED_HOSTS=['testserver'],
            SERVE_MEDIA=True,
        ):
            response = client.get('/media/probe.txt')
        assert response.status_code == status.HTTP_200_OK
        assert b''.join(response.streaming_content) == b'ok'

    def test_media_no_expuesto_sin_serve_media(self, settings, tmp_path):
        media_root = tmp_path / 'media'
        media_root.mkdir()
        (media_root / 'probe.txt').write_text('ok', encoding='utf-8')
        settings.MEDIA_ROOT = media_root
        client = Client()
        with override_settings(
            DEBUG=False,
            ALLOWED_HOSTS=['testserver'],
            SERVE_MEDIA=False,
        ):
            response = client.get('/media/probe.txt')
        assert response.status_code == status.HTTP_404_NOT_FOUND
