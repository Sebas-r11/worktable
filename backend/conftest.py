"""
Fixtures compartidas para tests de FLEX-OP.
"""
from datetime import date, time, timedelta
from decimal import Decimal

import pytest
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from maquinas.models import Maquina, TipoMaquina, UnidadEficiencia
from operaciones.models import Asignacion, Habilidad, Operario, Turno
from usuarios.models import Empresa, User


@pytest.fixture
def api_client():
    return APIClient()


def _auth_client(api_client, user):
    token = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
    return api_client


@pytest.fixture
def empresa(db):
    return Empresa.objects.create(
        nombre='Empresa Test',
        razon_social='Empresa Test SAC',
        ruc='20999999999',
        email='test@empresa.com',
        activa=True,
    )


@pytest.fixture
def empresa_b(db):
    return Empresa.objects.create(
        nombre='Empresa B',
        razon_social='Empresa B SAC',
        ruc='20888888888',
        email='b@empresa.com',
        activa=True,
    )


@pytest.fixture
def admin_user(empresa):
    user = User.objects.create_user(
        username='admin_test',
        email='admin@test.com',
        password='TestPass123!',
        first_name='Admin',
        last_name='Test',
        rol=User.RolChoices.ADMIN,
        empresa=empresa,
        activo=True,
    )
    return user


@pytest.fixture
def supervisor_user(empresa):
    return User.objects.create_user(
        username='supervisor_test',
        email='supervisor@test.com',
        password='TestPass123!',
        first_name='Super',
        last_name='Visor',
        rol=User.RolChoices.SUPERVISOR,
        empresa=empresa,
        activo=True,
    )


@pytest.fixture
def operario_user(empresa):
    return User.objects.create_user(
        username='operario_test',
        email='operario@test.com',
        password='TestPass123!',
        first_name='Oper',
        last_name='Ario',
        rol=User.RolChoices.OPERARIO,
        empresa=empresa,
        activo=True,
    )


@pytest.fixture
def auth_client_admin(api_client, admin_user):
    return _auth_client(api_client, admin_user)


@pytest.fixture
def auth_client_supervisor(api_client, supervisor_user):
    return _auth_client(api_client, supervisor_user)


@pytest.fixture
def auth_client_operario(api_client, operario_user):
    return _auth_client(api_client, operario_user)


@pytest.fixture
def gerente_user(empresa):
    return User.objects.create_user(
        username='gerente_test',
        email='gerente@test.com',
        password='TestPass123!',
        first_name='Ger',
        last_name='Ente',
        rol=User.RolChoices.GERENTE,
        empresa=empresa,
        activo=True,
    )


@pytest.fixture
def auth_client_gerente(api_client, gerente_user):
    return _auth_client(api_client, gerente_user)


@pytest.fixture
def turno(empresa):
    return Turno.objects.create(
        nombre='Turno Mañana',
        hora_inicio=time(6, 0),
        hora_fin=time(14, 0),
        empresa=empresa,
        activo=True,
    )


@pytest.fixture
def tipo_maquina(empresa):
    return TipoMaquina.objects.create(
        nombre='Llenadora Test',
        descripcion='Tipo de prueba',
        empresa=empresa,
    )


@pytest.fixture
def unidad_eficiencia(empresa):
    return UnidadEficiencia.objects.create(
        nombre='Unidades por hora',
        abreviatura='u/h',
        empresa=empresa,
    )


@pytest.fixture
def maquina(empresa, tipo_maquina, unidad_eficiencia):
    return Maquina.objects.create(
        codigo='MAQ-001',
        nombre='Llenadora 1',
        tipo=tipo_maquina,
        empresa=empresa,
        capacidad_teorica=Decimal('100.00'),
        unidad_capacidad=unidad_eficiencia,
        estado_actual=Maquina.EstadoChoices.DISPONIBLE,
        activa=True,
    )


@pytest.fixture
def habilidad(empresa, tipo_maquina):
    hab = Habilidad.objects.create(
        nombre='Operador Llenadora',
        descripcion='Habilidad de prueba',
        empresa=empresa,
    )
    hab.tipos_maquina.add(tipo_maquina)
    return hab


@pytest.fixture
def operario(operario_user, turno, habilidad):
    op = Operario.objects.create(
        usuario=operario_user,
        codigo_empleado='EMP-001',
        fecha_contratacion=date.today(),
        turno_actual=turno,
        disponible=True,
        activo=True,
    )
    op.habilidades.add(habilidad)
    return op


@pytest.fixture
def asignacion_pendiente(operario, maquina, turno, supervisor_user):
    return Asignacion.objects.create(
        operario=operario,
        maquina=maquina,
        turno=turno,
        fecha=date.today(),
        estado=Asignacion.EstadoChoices.PENDIENTE,
        asignado_por=supervisor_user,
    )


@pytest.fixture
def tipo_maquina_b(empresa_b):
    return TipoMaquina.objects.create(
        nombre='Llenadora B',
        descripcion='Tipo empresa B',
        empresa=empresa_b,
    )


@pytest.fixture
def unidad_eficiencia_b(empresa_b):
    return UnidadEficiencia.objects.create(
        nombre='Unidades por hora B',
        abreviatura='u/h',
        empresa=empresa_b,
    )


@pytest.fixture
def turno_b(empresa_b):
    return Turno.objects.create(
        nombre='Turno B',
        hora_inicio=time(6, 0),
        hora_fin=time(14, 0),
        empresa=empresa_b,
        activo=True,
    )


@pytest.fixture
def maquina_b(empresa_b, tipo_maquina_b, unidad_eficiencia_b):
    return Maquina.objects.create(
        codigo='MAQ-B-001',
        nombre='Llenadora B',
        tipo=tipo_maquina_b,
        empresa=empresa_b,
        capacidad_teorica=Decimal('80.00'),
        unidad_capacidad=unidad_eficiencia_b,
        estado_actual=Maquina.EstadoChoices.DISPONIBLE,
        activa=True,
    )


@pytest.fixture
def operario_user_b(empresa_b):
    return User.objects.create_user(
        username='operario_b',
        email='operario@empresa-b.com',
        password='TestPass123!',
        first_name='Oper',
        last_name='B',
        rol=User.RolChoices.OPERARIO,
        empresa=empresa_b,
        activo=True,
    )


@pytest.fixture
def operario_b(operario_user_b, turno_b):
    return Operario.objects.create(
        usuario=operario_user_b,
        codigo_empleado='EMP-B-001',
        fecha_contratacion=date.today(),
        turno_actual=turno_b,
        disponible=True,
        activo=True,
    )


@pytest.fixture
def asignacion_empresa_b(operario_b, maquina_b, turno_b, supervisor_empresa_b):
    return Asignacion.objects.create(
        operario=operario_b,
        maquina=maquina_b,
        turno=turno_b,
        fecha=date.today(),
        estado=Asignacion.EstadoChoices.PENDIENTE,
        asignado_por=supervisor_empresa_b,
    )


@pytest.fixture
def orden_fecha_limite():
    return timezone.now() + timedelta(days=7)


@pytest.fixture
def supervisor_empresa_b(empresa_b):
    return User.objects.create_user(
        username='supervisor_b',
        email='supervisor@empresa-b.com',
        password='TestPass123!',
        rol=User.RolChoices.SUPERVISOR,
        empresa=empresa_b,
        activo=True,
    )


@pytest.fixture
def auth_client_empresa_b(api_client, supervisor_empresa_b):
    return _auth_client(api_client, supervisor_empresa_b)


@pytest.fixture
def orden_produccion(empresa, supervisor_user, maquina, orden_fecha_limite):
    from ordenes.models import OrdenProduccion

    return OrdenProduccion.objects.create(
        numero_orden='ORD-TEST-0001',
        producto='Producto Test',
        cantidad_requerida=Decimal('100'),
        cantidad_producida=Decimal('0'),
        fecha_limite=orden_fecha_limite,
        empresa=empresa,
        maquina=maquina,
        creada_por=supervisor_user,
        estado=OrdenProduccion.EstadoChoices.PENDIENTE,
    )


@pytest.fixture
def asignacion_completada_con_produccion(
    asignacion_pendiente, supervisor_user
):
    from metricas.models import RegistroProduccion

    asignacion_pendiente.iniciar()
    RegistroProduccion.objects.create(
        asignacion=asignacion_pendiente,
        cantidad=Decimal('500'),
        registrado_por=supervisor_user,
    )
    asignacion_pendiente.finalizar()
    return asignacion_pendiente
