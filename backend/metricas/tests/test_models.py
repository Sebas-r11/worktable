"""
Tests unitarios — app metricas.
"""
from decimal import Decimal

import pytest

from metricas.models import MetricaEficiencia, ObjetivoProduccion, RegistroProduccion


@pytest.mark.django_db
class TestMetricaEficiencia:
    def test_calcular_para_asignacion_completada(
        self, asignacion_completada_con_produccion, operario
    ):
        asignacion = asignacion_completada_con_produccion
        metrica = MetricaEficiencia.calcular_para_asignacion(asignacion)

        assert metrica is not None
        assert metrica.produccion_real > 0
        assert metrica.eficiencia_calculada >= 0
        operario.refresh_from_db()
        assert operario.eficiencia_promedio >= 0

    def test_calcular_retorna_none_sin_tiempos(self, asignacion_pendiente):
        assert MetricaEficiencia.calcular_para_asignacion(asignacion_pendiente) is None

    def test_division_por_cero_capacidad_cero(
        self, asignacion_completada_con_produccion, maquina
    ):
        maquina.capacidad_teorica = Decimal('0')
        maquina.save()
        metrica = MetricaEficiencia.calcular_para_asignacion(
            asignacion_completada_con_produccion
        )
        assert metrica.eficiencia_calculada == Decimal('0')

    def test_calcular_idempotente_no_duplica(
        self, asignacion_completada_con_produccion
    ):
        m1 = MetricaEficiencia.calcular_para_asignacion(
            asignacion_completada_con_produccion
        )
        m2 = MetricaEficiencia.calcular_para_asignacion(
            asignacion_completada_con_produccion
        )
        assert m1.id == m2.id
        assert MetricaEficiencia.objects.filter(
            asignacion=asignacion_completada_con_produccion
        ).count() == 1

    def test_calcular_resta_tiempo_de_pausa(
        self, asignacion_pendiente, supervisor_user
    ):
        from datetime import timedelta

        from django.utils import timezone

        from operaciones.models import Evento

        asignacion_pendiente.iniciar()
        inicio = timezone.now() - timedelta(hours=2)
        fin = timezone.now()
        asignacion_pendiente.hora_inicio_real = inicio
        asignacion_pendiente.hora_fin_real = fin
        asignacion_pendiente.save(update_fields=['hora_inicio_real', 'hora_fin_real'])

        pausa = Evento.objects.create(
            asignacion=asignacion_pendiente,
            tipo=Evento.TipoEventoChoices.PAUSA,
            registrado_por=supervisor_user,
        )
        Evento.objects.filter(pk=pausa.pk).update(
            fecha_hora=inicio + timedelta(hours=1),
        )
        reanudacion = Evento.objects.create(
            asignacion=asignacion_pendiente,
            tipo=Evento.TipoEventoChoices.REANUDACION,
            registrado_por=supervisor_user,
        )
        Evento.objects.filter(pk=reanudacion.pk).update(
            fecha_hora=inicio + timedelta(hours=1, minutes=30),
        )

        from metricas.models import RegistroProduccion

        RegistroProduccion.objects.create(
            asignacion=asignacion_pendiente,
            cantidad=Decimal('100'),
            registrado_por=supervisor_user,
        )

        metrica = MetricaEficiencia.calcular_para_asignacion(asignacion_pendiente)
        assert metrica is not None
        # 2h totales − 30min pausa = 1.5h efectivas
        assert metrica.horas_trabajadas == Decimal('1.50')


@pytest.mark.django_db
class TestObjetivoProduccion:
    def test_calcular_cumplimiento_por_maquina(
        self, empresa, maquina, asignacion_completada_con_produccion, supervisor_user
    ):
        from datetime import date

        objetivo = ObjetivoProduccion.objects.create(
            tipo=ObjetivoProduccion.TipoObjetivoChoices.POR_MAQUINA,
            maquina=maquina,
            empresa=empresa,
            cantidad_objetivo=Decimal('100'),
            fecha_inicio=date.today(),
            activo=True,
        )
        RegistroProduccion.objects.create(
            asignacion=asignacion_completada_con_produccion,
            cantidad=Decimal('50'),
            registrado_por=supervisor_user,
        )
        resultado = objetivo.calcular_cumplimiento()
        assert resultado['objetivo'] == Decimal('100')
        assert resultado['porcentaje_cumplimiento'] >= 0

    def test_str_por_maquina(self, empresa, maquina):
        from datetime import date

        objetivo = ObjetivoProduccion.objects.create(
            tipo=ObjetivoProduccion.TipoObjetivoChoices.POR_MAQUINA,
            maquina=maquina,
            empresa=empresa,
            cantidad_objetivo=Decimal('200'),
            fecha_inicio=date.today(),
        )
        assert maquina.codigo in str(objetivo) or 'Objetivo' in str(objetivo)
