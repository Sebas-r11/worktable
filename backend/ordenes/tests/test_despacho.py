"""
Regresión B-02: despacho con cola EN_COLA correcta.
"""
from decimal import Decimal

import pytest

from ordenes.models import ColaDespacho, OrdenProduccion


@pytest.mark.django_db
class TestDespachoCola:
    def test_despachar_usa_item_en_cola(self, orden_produccion, supervisor_user):
        orden_produccion.registrar_produccion(Decimal('100'))
        cola = ColaDespacho.objects.get(orden=orden_produccion)
        assert cola.estado == ColaDespacho.EstadoChoices.EN_COLA

        orden_produccion.despachar(supervisor_user)
        orden_produccion.refresh_from_db()
        cola.refresh_from_db()

        assert orden_produccion.estado == OrdenProduccion.EstadoChoices.DESPACHADA
        assert cola.estado == ColaDespacho.EstadoChoices.DESPACHADA
        assert cola.despachado_por == supervisor_user
