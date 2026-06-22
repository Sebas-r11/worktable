"""
ViewSets del modulo de Ordenes de Produccion para FLEX-OP

Este archivo contiene las vistas para gestionar ordenes de produccion
y la cola de despacho. Las ordenes son el corazon de la produccion.
"""
from rest_framework import viewsets, status
from usuarios.permissions import IsAuthenticatedFlex, IsSupervisorOrAboveForWrite, IsGerenteOrAbove
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.utils import timezone

from usuarios.mixins import EmpresaFilterMixin

from .models import OrdenProduccion, ColaDespacho
from .ordering import ordenar_cola_despacho, ordenar_ordenes_produccion

ORDEN_SELECT_RELATED = ('empresa', 'maquina', 'creada_por')
COLA_SELECT_RELATED = ('orden', 'orden__maquina', 'empresa', 'despachado_por')
from .serializers import (
    OrdenProduccionSerializer,
    OrdenProduccionCreateSerializer,
    OrdenProduccionListSerializer,
    ColaDespachoSerializer,
    ActualizarProduccionSerializer
)


class OrdenProduccionViewSet(EmpresaFilterMixin, viewsets.ModelViewSet):
    """
    ViewSet para gestionar ordenes de produccion.
    """

    empresa_lookup = 'empresa'
    queryset = OrdenProduccion.objects.all()
    permission_classes = [IsSupervisorOrAboveForWrite]
    filterset_fields = ['estado', 'prioridad', 'maquina', 'empresa']
    search_fields = ['numero_orden', 'producto']
    ordering_fields = ['fecha_creacion', 'fecha_limite', 'prioridad']

    def get_queryset(self):
        return ordenar_ordenes_produccion(
            super().get_queryset().select_related(*ORDEN_SELECT_RELATED)
        )

    def get_serializer_class(self):
        if self.action == 'create':
            return OrdenProduccionCreateSerializer
        if self.action == 'list':
            return OrdenProduccionListSerializer
        return OrdenProduccionSerializer

    def perform_create(self, serializer):
        empresa = self.request.user.empresa
        year = timezone.now().year
        prefix = f'ORD-{year}-'
        with transaction.atomic():
            ultimo = (
                OrdenProduccion.objects.filter(
                    empresa=empresa,
                    numero_orden__startswith=prefix,
                )
                .select_for_update()
                .order_by('-numero_orden')
                .values_list('numero_orden', flat=True)
                .first()
            )
            secuencia = int(ultimo.rsplit('-', 1)[-1]) + 1 if ultimo else 1
            numero_orden = f'{prefix}{secuencia:04d}'
            serializer.save(
                empresa=empresa,
                creada_por=self.request.user,
                numero_orden=numero_orden,
            )

    @action(detail=True, methods=['post'])
    def iniciar(self, request, pk=None):
        orden = self.get_object()
        if orden.estado != OrdenProduccion.EstadoChoices.PENDIENTE:
            return Response(
                {'error': 'Solo se pueden iniciar ordenes pendientes'},
                status=status.HTTP_400_BAD_REQUEST
            )
        orden.iniciar()
        return Response({
            'mensaje': f'Orden {orden.numero_orden} iniciada',
            'orden': OrdenProduccionSerializer(orden).data
        })

    @action(detail=True, methods=['post'])
    def registrar_produccion(self, request, pk=None):
        orden = self.get_object()
        serializer = ActualizarProduccionSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if orden.estado not in (
            OrdenProduccion.EstadoChoices.PENDIENTE,
            OrdenProduccion.EstadoChoices.EN_PROCESO,
        ):
            return Response(
                {'error': 'Solo se puede registrar produccion en ordenes activas'},
                status=status.HTTP_400_BAD_REQUEST
            )

        cantidad = serializer.validated_data['cantidad']
        orden.registrar_produccion(cantidad)
        orden.refresh_from_db()

        completada = orden.estado == OrdenProduccion.EstadoChoices.LISTA

        return Response({
            'mensaje': f'Produccion registrada: {cantidad} unidades',
            'cantidad_total_producida': orden.cantidad_producida,
            'cantidad_requerida': orden.cantidad_requerida,
            'orden_completada': completada,
            'orden': OrdenProduccionSerializer(orden).data
        })

    @action(detail=True, methods=['post'])
    def completar(self, request, pk=None):
        orden = self.get_object()

        if orden.estado == OrdenProduccion.EstadoChoices.LISTA:
            return Response(
                {'error': 'La orden ya esta lista para despacho'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if orden.estado == OrdenProduccion.EstadoChoices.CANCELADA:
            return Response(
                {'error': 'No se puede completar una orden cancelada'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if orden.cantidad_producida == 0:
            return Response(
                {'error': 'La orden no tiene produccion registrada'},
                status=status.HTTP_400_BAD_REQUEST
            )

        orden.completar()
        cola = orden.posicion_cola.filter(
            estado=ColaDespacho.EstadoChoices.EN_COLA
        ).first()

        return Response({
            'mensaje': f'Orden {orden.numero_orden} completada y agregada a cola de despacho',
            'posicion_manual': cola.posicion_manual if cola else 0,
            'orden': OrdenProduccionSerializer(orden).data
        })

    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        orden = self.get_object()

        if orden.estado in (
            OrdenProduccion.EstadoChoices.LISTA,
            OrdenProduccion.EstadoChoices.DESPACHADA,
        ):
            return Response(
                {'error': 'No se puede cancelar una orden lista o despachada'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if orden.estado == OrdenProduccion.EstadoChoices.CANCELADA:
            return Response(
                {'error': 'La orden ya esta cancelada'},
                status=status.HTTP_400_BAD_REQUEST
            )

        motivo = request.data.get('motivo', 'Sin motivo especificado')
        orden.estado = OrdenProduccion.EstadoChoices.CANCELADA
        orden.notas = f"{orden.notas or ''}\n[CANCELADA] {motivo}".strip()
        orden.save()

        return Response({
            'mensaje': f'Orden {orden.numero_orden} cancelada',
            'orden': OrdenProduccionSerializer(orden).data
        })

    @action(detail=False, methods=['get'])
    def pendientes(self, request):
        ordenes = self.get_queryset().filter(
            estado=OrdenProduccion.EstadoChoices.PENDIENTE
        )
        serializer = OrdenProduccionListSerializer(ordenes, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def en_progreso(self, request):
        ordenes = self.get_queryset().filter(
            estado=OrdenProduccion.EstadoChoices.EN_PROCESO
        )
        serializer = OrdenProduccionListSerializer(ordenes, many=True)
        return Response(serializer.data)


class ColaDespachoViewSet(EmpresaFilterMixin, viewsets.ModelViewSet):
    """ViewSet para la cola de despacho."""

    empresa_lookup = 'empresa'
    queryset = ColaDespacho.objects.all()
    serializer_class = ColaDespachoSerializer
    permission_classes = [IsGerenteOrAbove]
    filterset_fields = ['estado']
    ordering_fields = ['posicion_manual', 'fecha_entrada']
    http_method_names = ['get', 'head', 'options', 'post']

    def get_queryset(self):
        return ordenar_cola_despacho(
            super().get_queryset().select_related(*COLA_SELECT_RELATED)
        )

    @action(detail=True, methods=['post'])
    def despachar(self, request, pk=None):
        item = self.get_object()

        if item.estado == ColaDespacho.EstadoChoices.DESPACHADA:
            return Response(
                {'error': 'Este item ya fue despachado'},
                status=status.HTTP_400_BAD_REQUEST
            )

        item.despachar(request.user)
        item.orden.despachar(request.user)

        return Response({
            'mensaje': f'Orden {item.orden.numero_orden} despachada',
            'fecha_despacho': item.fecha_despacho,
            'item': ColaDespachoSerializer(item).data
        })

    @action(detail=False, methods=['post'])
    def reordenar(self, request):
        nuevo_orden = request.data.get('orden', [])

        if not nuevo_orden:
            return Response(
                {'error': 'Se requiere una lista de IDs'},
                status=status.HTTP_400_BAD_REQUEST
            )

        empresa = request.user.empresa
        items = ColaDespacho.objects.filter(
            id__in=nuevo_orden,
            empresa=empresa,
            estado=ColaDespacho.EstadoChoices.EN_COLA
        )

        if items.count() != len(nuevo_orden):
            return Response(
                {'error': 'Algunos IDs no son validos o ya fueron despachados'},
                status=status.HTTP_400_BAD_REQUEST
            )

        for posicion, item_id in enumerate(nuevo_orden, start=1):
            ColaDespacho.objects.filter(id=item_id).update(posicion_manual=posicion)

        return Response({
            'mensaje': 'Cola reordenada exitosamente',
            'nuevo_orden': nuevo_orden
        })

    @action(detail=False, methods=['get'])
    def pendientes(self, request):
        items = self.get_queryset().filter(
            estado=ColaDespacho.EstadoChoices.EN_COLA
        )
        serializer = self.get_serializer(items, many=True)
        return Response(serializer.data)
