"""
Regresión B-01: deduplicación de alertas por objetivo.
"""
from datetime import date
from decimal import Decimal

import pytest

from alertas.models import Alerta, ReglaAlerta
from metricas.models import ObjetivoProduccion


@pytest.mark.django_db
class TestAlertaObjetivoDeduplicacion:
    def test_no_duplica_por_objetivo(self, empresa, maquina):
        objetivo = ObjetivoProduccion.objects.create(
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
        primera = regla.evaluar()
        segunda = regla.evaluar()
        assert len(primera) == 1
        assert len(segunda) == 0
        assert Alerta.objects.filter(
            objetivo_relacionado=objetivo,
            estado=Alerta.EstadoChoices.ACTIVA,
        ).count() == 1
