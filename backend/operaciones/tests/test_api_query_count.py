"""
Tests de conteo de queries en listados API (regresión N+1).
"""
from datetime import date

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from operaciones.models import Asignacion


def _query_count(client, url):
    with CaptureQueriesContext(connection) as ctx:
        response = client.get(url)
    assert response.status_code == 200
    return len(ctx)


@pytest.mark.django_db
class TestListadosSinNPlus1:
    def test_asignaciones_queries_estables_con_mas_filas(
        self,
        auth_client_supervisor,
        operario,
        maquina,
        turno,
        supervisor_user,
    ):
        for i in range(5):
            Asignacion.objects.create(
                operario=operario,
                maquina=maquina,
                turno=turno,
                fecha=date.today(),
                estado=Asignacion.EstadoChoices.PENDIENTE,
                asignado_por=supervisor_user,
            )

        base = _query_count(auth_client_supervisor, '/api/asignaciones/')

        for i in range(15):
            Asignacion.objects.create(
                operario=operario,
                maquina=maquina,
                turno=turno,
                fecha=date.today(),
                estado=Asignacion.EstadoChoices.PENDIENTE,
                asignado_por=supervisor_user,
            )

        extended = _query_count(auth_client_supervisor, '/api/asignaciones/')
        assert extended <= base + 2

    def test_operarios_list_no_n_plus_uno(
        self, auth_client_supervisor, operario
    ):
        queries = _query_count(auth_client_supervisor, '/api/operarios/')
        assert queries <= 12
