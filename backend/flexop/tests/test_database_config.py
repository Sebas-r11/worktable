"""
Tests de configuración de base de datos (Fase 3.1).
"""
import os
import subprocess
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[2]


def test_database_url_usa_postgresql():
    result = subprocess.run(
        [
            sys.executable,
            '-c',
            'import django; django.setup(); from django.conf import settings; '
            'print(settings.DATABASES["default"]["ENGINE"])',
        ],
        cwd=BACKEND_DIR,
        env={
            **os.environ,
            'DJANGO_SETTINGS_MODULE': 'flexop.settings',
            'DEBUG': 'True',
            'DATABASE_URL': 'postgres://flexop:flexop@localhost:5432/flexop',
        },
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert 'postgresql' in result.stdout


def test_sin_database_url_usa_sqlite():
    env = os.environ.copy()
    env['DJANGO_SETTINGS_MODULE'] = 'flexop.settings'
    env['DEBUG'] = 'True'
    env.pop('DATABASE_URL', None)
    result = subprocess.run(
        [
            sys.executable,
            '-c',
            'import django; django.setup(); from django.conf import settings; '
            'print(settings.DATABASES["default"]["ENGINE"])',
        ],
        cwd=BACKEND_DIR,
        env=env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert 'sqlite3' in result.stdout
