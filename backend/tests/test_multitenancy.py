"""
Tests de aislamiento por empresa (multitenancy).
"""
import pytest
from datetime import date
from rest_framework import status

from maquinas.models import Maquina, TipoMaquina, UnidadEficiencia
from operaciones.models import Asignacion, Operario, Turno
from usuarios.models import User


@pytest.mark.django_db
class TestMultitenancy:
    def test_no_ver_asignacion_de_otra_empresa(
        self,
        auth_client_supervisor,
        empresa_b,
        supervisor_empresa_b,
        tipo_maquina,
        unidad_eficiencia,
    ):
        tipo_b = TipoMaquina.objects.create(
            nombre='Tipo B', empresa=empresa_b
        )
        unidad_b = UnidadEficiencia.objects.create(
            nombre='u/h B', abreviatura='u/h', empresa=empresa_b
        )
        maquina_b = Maquina.objects.create(
            codigo='MAQ-B-001',
            nombre='Maquina B',
            tipo=tipo_b,
            empresa=empresa_b,
            capacidad_teorica=100,
            unidad_capacidad=unidad_b,
        )
        from datetime import time

        turno_b = Turno.objects.create(
            nombre='Turno B',
            hora_inicio=time(8, 0),
            hora_fin=time(16, 0),
            empresa=empresa_b,
        )
        user_b = User.objects.create_user(
            username='op_b',
            email='op_b@test.com',
            password='TestPass123!',
            rol=User.RolChoices.OPERARIO,
            empresa=empresa_b,
        )
        op_b = Operario.objects.create(
            usuario=user_b,
            codigo_empleado='EMP-B-001',
            fecha_contratacion=date.today(),
            turno_actual=turno_b,
        )
        asignacion_b = Asignacion.objects.create(
            operario=op_b,
            maquina=maquina_b,
            turno=turno_b,
            fecha=date.today(),
            asignado_por=supervisor_empresa_b,
        )

        response = auth_client_supervisor.get(
            f'/api/asignaciones/{asignacion_b.id}/'
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_crear_usuario_requiere_admin(self, auth_client_supervisor, empresa):
        response = auth_client_supervisor.post(
            '/api/usuarios/',
            {
                'username': 'nuevo_user',
                'email': 'nuevo@test.com',
                'password': 'TestPass123!',
                'password2': 'TestPass123!',
                'rol': 'OPERARIO',
                'empresa': empresa.id,
            },
            format='json',
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_puede_crear_usuario(self, auth_client_admin, empresa):
        response = auth_client_admin.post(
            '/api/usuarios/',
            {
                'username': 'nuevo_por_admin',
                'email': 'admin_crea@test.com',
                'password': 'TestPass123!',
                'password2': 'TestPass123!',
                'rol': 'OPERARIO',
                'empresa': empresa.id,
            },
            format='json',
        )
        assert response.status_code == status.HTTP_201_CREATED
