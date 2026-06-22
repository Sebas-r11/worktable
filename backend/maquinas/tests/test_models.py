"""
Tests unitarios — app maquinas.
"""
import pytest
from django.utils import timezone

from maquinas.models import EstadoMaquina, Maquina


@pytest.mark.django_db
class TestMaquina:
    def test_cambiar_estado_crea_historial(self, maquina, supervisor_user):
        maquina.cambiar_estado(
            Maquina.EstadoChoices.MANTENIMIENTO,
            usuario=supervisor_user,
            observacion='Test',
        )
        maquina.refresh_from_db()
        assert maquina.estado_actual == Maquina.EstadoChoices.MANTENIMIENTO
        assert maquina.historial_estados.count() == 1

    def test_str_incluye_codigo(self, maquina):
        assert 'MAQ-001' in str(maquina)


@pytest.mark.django_db
class TestEstadoMaquina:
    def test_duracion_entre_cambios(self, maquina, supervisor_user):
        t0 = timezone.now()
        e1 = EstadoMaquina.objects.create(
            maquina=maquina,
            estado=Maquina.EstadoChoices.DISPONIBLE,
            fecha_hora=t0,
        )
        EstadoMaquina.objects.create(
            maquina=maquina,
            estado=Maquina.EstadoChoices.OPERANDO,
            fecha_hora=t0 + timezone.timedelta(hours=2),
        )
        duracion = e1.duracion()
        assert duracion is not None
        assert duracion.total_seconds() == pytest.approx(7200, rel=0.1)

    def test_duracion_none_si_es_ultimo_estado(self, maquina):
        estado = EstadoMaquina.objects.create(
            maquina=maquina,
            estado=Maquina.EstadoChoices.DISPONIBLE,
        )
        assert estado.duracion() is None
