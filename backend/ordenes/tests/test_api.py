"""
Tests de API — app ordenes.
"""
from decimal import Decimal

import pytest
from rest_framework import status

from ordenes.models import ColaDespacho, OrdenProduccion


@pytest.mark.django_db
class TestOrdenProduccionAPI:
    def test_listar_ordenes_filtra_por_empresa(
        self, auth_client_supervisor, orden_produccion
    ):
        response = auth_client_supervisor.get('/api/ordenes/')
        assert response.status_code == status.HTTP_200_OK
        ids = [o['id'] for o in response.data['results']]
        assert orden_produccion.id in ids

    def test_registrar_produccion_completa_orden(
        self, auth_client_supervisor, orden_produccion
    ):
        url = f'/api/ordenes/{orden_produccion.id}/registrar_produccion/'
        response = auth_client_supervisor.post(
            url, {'cantidad': '100'}, format='json'
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['orden_completada'] is True
        orden_produccion.refresh_from_db()
        assert orden_produccion.estado == OrdenProduccion.EstadoChoices.LISTA
        assert ColaDespacho.objects.filter(orden=orden_produccion).exists()

    def test_cancelar_orden_lista_falla(
        self, auth_client_supervisor, orden_produccion
    ):
        orden_produccion.registrar_produccion(Decimal('100'))
        url = f'/api/ordenes/{orden_produccion.id}/cancelar/'
        response = auth_client_supervisor.post(url, {}, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_crear_orden_genera_numero(
        self, auth_client_supervisor, empresa, orden_fecha_limite
    ):
        response = auth_client_supervisor.post(
            '/api/ordenes/',
            {
                'empresa': empresa.id,
                'producto': 'Nuevo producto',
                'cantidad_requerida': '50',
                'fecha_limite': orden_fecha_limite.isoformat(),
                'prioridad': 'NORMAL',
            },
            format='json',
        )
        assert response.status_code == status.HTTP_201_CREATED
        orden = OrdenProduccion.objects.get(pk=response.data['id'])
        assert orden.numero_orden.startswith('ORD-')

    def test_crear_ordenes_secuenciales_incrementan_numero(
        self, auth_client_supervisor, empresa, orden_fecha_limite
    ):
        payload = {
            'empresa': empresa.id,
            'producto': 'Producto secuencial',
            'cantidad_requerida': '10',
            'fecha_limite': orden_fecha_limite.isoformat(),
            'prioridad': 'NORMAL',
        }
        r1 = auth_client_supervisor.post('/api/ordenes/', payload, format='json')
        r2 = auth_client_supervisor.post('/api/ordenes/', payload, format='json')
        assert r1.status_code == status.HTTP_201_CREATED
        assert r2.status_code == status.HTTP_201_CREATED
        n1 = OrdenProduccion.objects.get(pk=r1.data['id']).numero_orden
        n2 = OrdenProduccion.objects.get(pk=r2.data['id']).numero_orden
        assert int(n2.rsplit('-', 1)[-1]) == int(n1.rsplit('-', 1)[-1]) + 1
