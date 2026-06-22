"""
Tests unitarios — app usuarios.
"""
import pytest

from usuarios.models import Empresa, User


@pytest.mark.django_db
class TestUser:
    def test_es_operario(self, operario_user):
        assert operario_user.es_operario is True
        assert operario_user.es_admin is False

    def test_es_admin(self, admin_user):
        assert admin_user.es_admin is True
        assert admin_user.es_operario is False

    def test_str_incluye_rol(self, operario_user):
        texto = str(operario_user)
        assert 'Oper' in texto or 'operario_test' in texto


@pytest.mark.django_db
class TestEmpresa:
    def test_str_es_nombre(self, empresa):
        assert str(empresa) == 'Empresa Test'
