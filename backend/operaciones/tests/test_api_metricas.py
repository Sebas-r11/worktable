"""
Tests de integración asignación → métrica de eficiencia.
"""
from decimal import Decimal

import pytest
from rest_framework import status

from metricas.models import MetricaEficiencia, RegistroProduccion


@pytest.mark.django_db
class TestAsignacionMetricaIntegracion:
    def test_finalizar_crea_metrica(
        self, auth_client_supervisor, asignacion_pendiente, supervisor_user
    ):
        asignacion_pendiente.iniciar()
        RegistroProduccion.objects.create(
            asignacion=asignacion_pendiente,
            cantidad=Decimal('500'),
            registrado_por=supervisor_user,
        )

        url = f'/api/asignaciones/{asignacion_pendiente.id}/finalizar/'
        response = auth_client_supervisor.post(url)
        assert response.status_code == status.HTTP_200_OK
        assert MetricaEficiencia.objects.filter(asignacion=asignacion_pendiente).exists()
