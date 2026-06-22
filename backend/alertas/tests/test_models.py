"""
Tests unitarios — app alertas.
"""
from decimal import Decimal

import pytest

from alertas.models import Alerta, ReglaAlerta
from operaciones.models import Incidencia


@pytest.mark.django_db
class TestReglaAlerta:
    def test_evaluar_eficiencia_baja_genera_alerta(self, empresa, operario):
        operario.eficiencia_promedio = Decimal('50')
        operario.save()
        regla = ReglaAlerta.objects.create(
            nombre='Eficiencia minima',
            tipo=ReglaAlerta.TipoReglaChoices.EFICIENCIA_BAJA,
            umbral=Decimal('70'),
            unidad_umbral='%',
            empresa=empresa,
            activa=True,
        )
        alertas = regla.evaluar()
        assert len(alertas) == 1
        assert alertas[0].operario_relacionado == operario

    def test_no_duplica_alerta_activa_misma_regla(self, empresa, operario):
        operario.eficiencia_promedio = Decimal('40')
        operario.save()
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

    def test_evaluar_incidencia_sin_resolver(self, empresa, maquina, operario_user):
        from django.utils import timezone
        from datetime import timedelta

        regla = ReglaAlerta.objects.create(
            nombre='Incidencia abierta',
            tipo=ReglaAlerta.TipoReglaChoices.INCIDENCIA_SIN_RESOLVER,
            umbral=Decimal('0'),
            empresa=empresa,
        )
        inc = Incidencia.objects.create(
            maquina=maquina,
            tipo=Incidencia.TipoChoices.FALLA_MAQUINA,
            titulo='Falla test',
            descripcion='Test',
            reportado_por=operario_user,
        )
        inc.fecha_reporte = timezone.now() - timedelta(hours=2)
        inc.save(update_fields=['fecha_reporte'])

        alertas = regla.evaluar()
        assert any(a.incidencia_relacionada_id == inc.id for a in alertas)


@pytest.mark.django_db
class TestAlerta:
    def test_resolver(self, empresa, supervisor_user):
        alerta = Alerta.objects.create(
            titulo='Test',
            descripcion='Desc',
            empresa=empresa,
        )
        alerta.resolver(supervisor_user, 'Solucionado')
        alerta.refresh_from_db()
        assert alerta.estado == Alerta.EstadoChoices.RESUELTA
        assert alerta.resuelta_por == supervisor_user
