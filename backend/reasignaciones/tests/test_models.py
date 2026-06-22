"""
Tests unitarios — app reasignaciones.
"""
from decimal import Decimal

import pytest

from maquinas.models import Maquina
from reasignaciones.models import SugerenciaReasignacion


@pytest.mark.django_db
class TestSugerenciaReasignacion:
    def test_generar_sugerencias_maquina_disponible(
        self, empresa, operario, maquina, tipo_maquina
    ):
        maquina.estado_actual = Maquina.EstadoChoices.DISPONIBLE
        maquina.save()
        operario.disponible = True
        operario.save()

        sugerencias = SugerenciaReasignacion.generar_sugerencias(empresa)
        assert len(sugerencias) >= 1
        assert sugerencias[0].maquina_destino == maquina
        assert sugerencias[0].estado == SugerenciaReasignacion.EstadoChoices.PENDIENTE

    def test_aceptar_crea_asignacion(self, empresa, operario, maquina, turno, supervisor_user):
        sugerencia = SugerenciaReasignacion.objects.create(
            operario=operario,
            maquina_destino=maquina,
            razon=SugerenciaReasignacion.RazonChoices.MAQUINA_DISPONIBLE,
            descripcion='Test',
            impacto_estimado=Decimal('80'),
            empresa=empresa,
        )
        asignacion = sugerencia.aceptar(supervisor_user, 'Aceptada en test')
        sugerencia.refresh_from_db()

        assert sugerencia.estado == SugerenciaReasignacion.EstadoChoices.ACEPTADA
        assert sugerencia.asignacion_creada_id == asignacion.id
        assert asignacion.operario == operario
        assert asignacion.maquina == maquina

    def test_rechazar(self, empresa, operario, maquina, supervisor_user):
        sugerencia = SugerenciaReasignacion.objects.create(
            operario=operario,
            maquina_destino=maquina,
            razon=SugerenciaReasignacion.RazonChoices.MAQUINA_DISPONIBLE,
            descripcion='Test',
            empresa=empresa,
        )
        sugerencia.rechazar(supervisor_user, 'No aplica')
        sugerencia.refresh_from_db()
        assert sugerencia.estado == SugerenciaReasignacion.EstadoChoices.RECHAZADA

    def test_str_muestra_codigos(self, empresa, operario, maquina):
        sugerencia = SugerenciaReasignacion.objects.create(
            operario=operario,
            maquina_destino=maquina,
            razon=SugerenciaReasignacion.RazonChoices.MAQUINA_DISPONIBLE,
            descripcion='Test',
            empresa=empresa,
        )
        assert 'MAQ-001' in str(sugerencia)
