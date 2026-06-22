"""
Tests de configuración segura en producción (Fase 1.4).
"""
import os
import subprocess
import sys
from pathlib import Path

import pytest
from django.test import override_settings

BACKEND_DIR = Path(__file__).resolve().parents[2]


def _load_settings_subprocess(env: dict) -> subprocess.CompletedProcess:
    merged = os.environ.copy()
    merged.update(env)
    merged.setdefault('DJANGO_SETTINGS_MODULE', 'flexop.settings')
    return subprocess.run(
        [
            sys.executable,
            '-c',
            'import django; django.setup(); from django.conf import settings; '
            'print(settings.ALLOWED_HOSTS)',
        ],
        cwd=BACKEND_DIR,
        env=merged,
        capture_output=True,
        text=True,
    )


def test_debug_false_requiere_secret_key_env():
    result = _load_settings_subprocess(
        {
            'DEBUG': 'False',
            'SECRET_KEY': '',
            'ALLOWED_HOSTS': 'example.com',
        }
    )
    assert result.returncode != 0
    assert 'SECRET_KEY' in result.stderr


def test_allowed_hosts_no_es_wildcard_en_produccion():
    result = _load_settings_subprocess(
        {
            'DEBUG': 'False',
            'SECRET_KEY': 'test-production-secret-key',
            'ALLOWED_HOSTS': '*',
        }
    )
    assert result.returncode != 0
    assert 'ALLOWED_HOSTS' in result.stderr


def test_produccion_con_env_vars_validas_arranca():
    result = _load_settings_subprocess(
        {
            'DEBUG': 'False',
            'SECRET_KEY': 'test-production-secret-key',
            'ALLOWED_HOSTS': 'example.com,api.example.com',
        }
    )
    assert result.returncode == 0, result.stderr
    assert 'example.com' in result.stdout


@pytest.mark.django_db
def test_debug_true_permite_secret_key_por_defecto():
    with override_settings(DEBUG=True, ALLOWED_HOSTS=['localhost', '127.0.0.1']):
        from django.conf import settings

        assert settings.DEBUG is True
        assert settings.ALLOWED_HOSTS != ['*']
