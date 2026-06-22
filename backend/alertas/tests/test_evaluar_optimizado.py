"""
Tests de evaluación de reglas — idempotencia y queries acotadas.
"""
from datetime import date
from decimal import Decimal

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from alertas.models import Alerta, ReglaAlerta
from metricas.models import ObjetivoProduccion


@pytest.mark.django_db
class TestEvaluarReglasOptimizado:
    def test_evaluar_eficiencia_idempotente(
        self, empresa, operario
    ):
        operario.eficiencia_promedio = Decimal('50')
        operario.save(update_fields=['eficiencia_promedio'])
        regla = ReglaAlerta.objects.create(
            nombre='Eficiencia minima',
            tipo=ReglaAlerta.TipoReglaChoices.EFICIENCIA_BAJA,
            umbral=Decimal('70'),
            empresa=empresa,
        )
        primera = regla.evaluar()
        segunda = regla.evaluar()
        assert len(primera) == 1
        assert len(segunda) == 0
        assert Alerta.objects.filter(regla=regla, estado='ACTIVA').count() == 1

    def test_evaluar_objetivo_queries_acotadas(self, empresa, maquina):
        ObjetivoProduccion.objects.create(
            tipo=ObjetivoProduccion.TipoObjetivoChoices.POR_MAQUINA,
            maquina=maquina,
            empresa=empresa,
            cantidad_objetivo=Decimal('10000'),
            fecha_inicio=date.today(),
            activo=True,
        )
        regla = ReglaAlerta.objects.create(
            nombre='Objetivo minimo',
            tipo=ReglaAlerta.TipoReglaChoices.OBJETIVO_NO_ALCANZADO,
            umbral=Decimal('100'),
            empresa=empresa,
        )
        with CaptureQueriesContext(connection) as ctx:
            regla.evaluar()
        assert len(ctx) <= 15
