"""
Tests unitarios — app ordenes.
"""
from decimal import Decimal

import pytest
from django.utils import timezone

from ordenes.models import ColaDespacho, OrdenProduccion


@pytest.mark.django_db
class TestOrdenProduccion:
    def test_porcentaje_avance(self, orden_produccion):
        orden_produccion.cantidad_producida = Decimal('25')
        assert orden_produccion.porcentaje_avance() == 25.0

    def test_esta_atrasada_si_paso_fecha_limite(self, orden_produccion):
        orden_produccion.fecha_limite = timezone.now() - timezone.timedelta(days=1)
        assert orden_produccion.esta_atrasada() is True

    def test_no_atrasada_si_lista(self, orden_produccion):
        orden_produccion.estado = OrdenProduccion.EstadoChoices.LISTA
        orden_produccion.fecha_limite = timezone.now() - timezone.timedelta(days=1)
        assert orden_produccion.esta_atrasada() is False

    def test_iniciar_desde_pendiente(self, orden_produccion):
        orden_produccion.iniciar()
        orden_produccion.refresh_from_db()
        assert orden_produccion.estado == OrdenProduccion.EstadoChoices.EN_PROCESO
        assert orden_produccion.fecha_inicio is not None

    def test_registrar_produccion_completa_y_crea_cola(self, orden_produccion):
        orden_produccion.registrar_produccion(Decimal('100'))
        orden_produccion.refresh_from_db()
        assert orden_produccion.estado == OrdenProduccion.EstadoChoices.LISTA
        assert ColaDespacho.objects.filter(orden=orden_produccion).exists()

    def test_completar_manual_crea_cola(self, orden_produccion):
        orden_produccion.iniciar()
        orden_produccion.cantidad_producida = Decimal('10')
        orden_produccion.save()
        orden_produccion.completar()
        assert orden_produccion.estado == OrdenProduccion.EstadoChoices.LISTA
        assert ColaDespacho.objects.filter(orden=orden_produccion).exists()

    def test_completar_no_duplica_entrada_cola(self, orden_produccion):
        orden_produccion.iniciar()
        orden_produccion.completar()
        orden_produccion.completar()
        assert (
            ColaDespacho.objects.filter(
                orden=orden_produccion,
                estado=ColaDespacho.EstadoChoices.EN_COLA,
            ).count()
            == 1
        )

    def test_registrar_produccion_no_excede_cantidad_requerida(self, orden_produccion):
        orden_produccion.registrar_produccion(Decimal('60'))
        orden_produccion.registrar_produccion(Decimal('100'))
        orden_produccion.refresh_from_db()
        assert orden_produccion.cantidad_producida == Decimal('100')
        assert (
            ColaDespacho.objects.filter(
                orden=orden_produccion,
                estado=ColaDespacho.EstadoChoices.EN_COLA,
            ).count()
            == 1
        )


@pytest.mark.django_db
class TestColaDespacho:
    def test_siguiente_a_despachar(self, orden_produccion, empresa):
        orden_produccion.completar()
        siguiente = ColaDespacho.siguiente_a_despachar(empresa)
        assert siguiente is not None
        assert siguiente.orden == orden_produccion

    def test_tiempo_en_cola_minutos(self, orden_produccion, empresa):
        orden_produccion.completar()
        cola = ColaDespacho.objects.get(orden=orden_produccion)
        assert cola.tiempo_en_cola_minutos() >= 0
