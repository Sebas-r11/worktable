"""
Tests de seguridad en escrituras multitenancy (Fase 1.1+).
"""
import pytest
from datetime import date, time
from decimal import Decimal
from rest_framework import status

from maquinas.models import Maquina, TipoMaquina, UnidadEficiencia
from operaciones.models import Turno


@pytest.mark.django_db
class TestEmpresaWriteSecurity:
    def test_crear_maquina_ignora_empresa_ajena_en_body(
        self,
        auth_client_supervisor,
        empresa,
        empresa_b,
        tipo_maquina,
        unidad_eficiencia,
    ):
        response = auth_client_supervisor.post(
            '/api/maquinas/',
            {
                'codigo': 'SEC-001',
                'nombre': 'Maquina Segura',
                'tipo': tipo_maquina.id,
                'empresa': empresa_b.id,
                'capacidad_teorica': '75.00',
                'unidad_capacidad': unidad_eficiencia.id,
            },
            format='json',
        )
        assert response.status_code == status.HTTP_201_CREATED
        maquina = Maquina.objects.get(codigo='SEC-001')
        assert maquina.empresa_id == empresa.id

    def test_patch_maquina_no_cambia_empresa(
        self,
        auth_client_supervisor,
        maquina,
        empresa_b,
    ):
        original_empresa_id = maquina.empresa_id
        response = auth_client_supervisor.patch(
            f'/api/maquinas/{maquina.id}/',
            {'empresa': empresa_b.id, 'nombre': 'Nombre actualizado'},
            format='json',
        )
        assert response.status_code == status.HTTP_200_OK
        maquina.refresh_from_db()
        assert maquina.empresa_id == original_empresa_id
        assert maquina.nombre == 'Nombre actualizado'

    def test_crear_turno_asigna_empresa_del_usuario(
        self,
        auth_client_supervisor,
        empresa,
        empresa_b,
    ):
        response = auth_client_supervisor.post(
            '/api/turnos/',
            {
                'nombre': 'Turno Tarde Sec',
                'hora_inicio': '14:00:00',
                'hora_fin': '22:00:00',
                'empresa': empresa_b.id,
                'activo': True,
            },
            format='json',
        )
        assert response.status_code == status.HTTP_201_CREATED
        turno = Turno.objects.get(nombre='Turno Tarde Sec')
        assert turno.empresa_id == empresa.id

    def test_supervisor_empresa_b_no_ve_maquina_empresa_a(
        self,
        auth_client_empresa_b,
        maquina,
    ):
        response = auth_client_empresa_b.get(f'/api/maquinas/{maquina.id}/')
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_crear_tipo_maquina_sin_empresa_en_respuesta_editable(
        self,
        auth_client_supervisor,
        empresa,
        empresa_b,
    ):
        response = auth_client_supervisor.post(
            '/api/tipos-maquina/',
            {
                'nombre': 'Tipo Seguro',
                'descripcion': 'Test',
                'empresa': empresa_b.id,
            },
            format='json',
        )
        assert response.status_code == status.HTTP_201_CREATED
        tipo = TipoMaquina.objects.get(nombre='Tipo Seguro')
        assert tipo.empresa_id == empresa.id


@pytest.mark.django_db
class TestCrossTenantFkValidation:
    def test_crear_asignacion_rechaza_maquina_otra_empresa(
        self,
        auth_client_supervisor,
        operario,
        maquina_b,
        turno,
    ):
        response = auth_client_supervisor.post(
            '/api/asignaciones/',
            {
                'operario': operario.id,
                'maquina': maquina_b.id,
                'turno': turno.id,
                'fecha': str(date.today()),
            },
            format='json',
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'maquina' in response.data

    def test_crear_incidencia_rechaza_maquina_otra_empresa(
        self,
        auth_client_operario,
        asignacion_pendiente,
        maquina_b,
    ):
        response = auth_client_operario.post(
            '/api/incidencias/',
            {
                'asignacion': asignacion_pendiente.id,
                'maquina': maquina_b.id,
                'tipo': 'FALLA_MAQUINA',
                'prioridad': 'MEDIA',
                'titulo': 'Fallo cross-tenant',
                'descripcion': 'Test seguridad',
            },
            format='json',
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'maquina' in response.data

    def test_crear_registro_produccion_rechaza_asignacion_otra_empresa(
        self,
        auth_client_operario,
        asignacion_empresa_b,
    ):
        response = auth_client_operario.post(
            '/api/produccion/',
            {
                'asignacion': asignacion_empresa_b.id,
                'cantidad': '10.00',
            },
            format='json',
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'asignacion' in response.data
