"""
Tests de ordenamiento de negocio — app ordenes.
"""
from decimal import Decimal

import pytest
from rest_framework import status

from ordenes.models import ColaDespacho, OrdenProduccion


def _crear_orden(empresa, supervisor_user, maquina, fecha_limite, prioridad, suffix):
    return OrdenProduccion.objects.create(
        numero_orden=f'ORD-PRI-{suffix}',
        producto=f'Producto {suffix}',
        cantidad_requerida=Decimal('10'),
        cantidad_producida=Decimal('10'),
        fecha_limite=fecha_limite,
        empresa=empresa,
        maquina=maquina,
        creada_por=supervisor_user,
        estado=OrdenProduccion.EstadoChoices.PENDIENTE,
        prioridad=prioridad,
    )


@pytest.mark.django_db
class TestOrdenamientoPrioridad:
    def test_pendientes_ordenadas_por_prioridad_negocio(
        self, auth_client_supervisor, empresa, supervisor_user, maquina, orden_fecha_limite
    ):
        _crear_orden(empresa, supervisor_user, maquina, orden_fecha_limite, 'BAJA', '001')
        _crear_orden(empresa, supervisor_user, maquina, orden_fecha_limite, 'URGENTE', '002')
        _crear_orden(empresa, supervisor_user, maquina, orden_fecha_limite, 'ALTA', '003')

        response = auth_client_supervisor.get('/api/ordenes/pendientes/')
        assert response.status_code == status.HTTP_200_OK
        prioridades = [o['prioridad'] for o in response.data]
        assert prioridades == ['URGENTE', 'ALTA', 'BAJA']

    def test_cola_despacho_y_siguiente_usan_mismo_orden(
        self, empresa, supervisor_user, maquina, orden_fecha_limite
    ):
        baja = _crear_orden(
            empresa, supervisor_user, maquina, orden_fecha_limite, 'BAJA', '010'
        )
        urgente = _crear_orden(
            empresa, supervisor_user, maquina, orden_fecha_limite, 'URGENTE', '011'
        )
        baja.iniciar()
        baja.completar()
        urgente.iniciar()
        urgente.completar()

        siguiente = ColaDespacho.siguiente_a_despachar(empresa)
        pendientes = list(ColaDespacho.cola_en_espera(empresa=empresa))

        assert siguiente is not None
        assert pendientes[0].orden.prioridad == 'URGENTE'
        assert siguiente.id == pendientes[0].id
