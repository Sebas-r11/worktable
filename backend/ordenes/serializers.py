"""
Serializers del modulo de Ordenes de Produccion para FLEX-OP

Este archivo contiene los serializers para ordenes de produccion y cola de despacho.
Las ordenes representan el trabajo que debe realizarse en planta.
"""
from decimal import Decimal

from rest_framework import serializers

from .models import OrdenProduccion, ColaDespacho


class OrdenProduccionSerializer(serializers.ModelSerializer):
    # Serializer para ordenes de produccion
    """
    Serializer para el modelo OrdenProduccion
    """

    # Campos de solo lectura calculados
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    cantidad_pendiente = serializers.SerializerMethodField()
    porcentaje_completado = serializers.SerializerMethodField()
    dias_restantes = serializers.SerializerMethodField()

    # maquina es FK, mostrar nombre
    maquina_nombre = serializers.CharField(source='maquina.nombre', read_only=True)

    class Meta:
        model = OrdenProduccion
        fields = [
            'id', 'numero_orden', 'empresa', 'producto', 'descripcion', 'unidad',
            'cantidad_requerida', 'cantidad_producida', 'cantidad_pendiente',
            'porcentaje_completado', 'fecha_creacion', 'fecha_limite',
            'dias_restantes', 'prioridad', 'estado', 'estado_display',
            'maquina', 'maquina_nombre', 'notas',
        ]
        read_only_fields = [
            'id', 'numero_orden', 'cantidad_producida', 'fecha_creacion', 'estado',
        ]

    def get_cantidad_pendiente(self, obj):
        """Calcula la cantidad que falta por producir"""
        pendiente = obj.cantidad_requerida - obj.cantidad_producida
        return max(0, pendiente)

    def get_porcentaje_completado(self, obj):
        """Calcula el porcentaje de avance de la orden"""
        if obj.cantidad_requerida == 0:
            return 0
        return round((obj.cantidad_producida / obj.cantidad_requerida) * 100, 2)

    def get_dias_restantes(self, obj):
        """Calcula los dias que faltan para la fecha limite"""
        from django.utils import timezone
        if not obj.fecha_limite:
            return None
        delta = obj.fecha_limite.date() - timezone.now().date()
        return delta.days


class OrdenProduccionCreateSerializer(serializers.ModelSerializer):
    # Serializer para crear ordenes
    """
    Serializer simplificado para crear ordenes de produccion
    """

    class Meta:
        model = OrdenProduccion
        fields = [
            'id', 'empresa', 'producto', 'descripcion', 'unidad',
            'cantidad_requerida', 'fecha_limite', 'prioridad', 'maquina', 'notas',
            'numero_orden',
        ]
        read_only_fields = ['id', 'numero_orden', 'empresa']

    def validate_cantidad_requerida(self, value):
        """Valida que la cantidad sea positiva"""
        if value <= 0:
            raise serializers.ValidationError('La cantidad debe ser mayor a cero')
        return value

    def validate_fecha_limite(self, value):
        """Valida que la fecha limite sea futura"""
        from django.utils import timezone
        if value and value.date() < timezone.now().date():
            raise serializers.ValidationError('La fecha limite no puede ser en el pasado')
        return value


class OrdenProduccionListSerializer(serializers.ModelSerializer):
    # Serializer resumido para listados
    """
    Serializer resumido para listar ordenes de produccion
    """

    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    porcentaje = serializers.SerializerMethodField()
    maquina_nombre = serializers.CharField(source='maquina.nombre', read_only=True)

    class Meta:
        model = OrdenProduccion
        fields = [
            'id', 'numero_orden', 'producto', 'cantidad_requerida',
            'cantidad_producida', 'porcentaje', 'fecha_limite',
            'prioridad', 'estado', 'estado_display',
            'maquina', 'maquina_nombre',
        ]

    def get_porcentaje(self, obj):
        """Porcentaje de avance"""
        if obj.cantidad_requerida == 0:
            return 0
        return round((obj.cantidad_producida / obj.cantidad_requerida) * 100, 1)


class ColaDespachoSerializer(serializers.ModelSerializer):
    # Serializer para cola de despacho
    """
    Serializer para el modelo ColaDespacho
    """

    # Informacion de la orden
    orden_numero = serializers.CharField(source='orden.numero_orden', read_only=True)
    producto = serializers.CharField(source='orden.producto', read_only=True)
    cantidad = serializers.DecimalField(
        source='orden.cantidad_producida', max_digits=12, decimal_places=2, read_only=True
    )
    despachada = serializers.SerializerMethodField()

    def get_despachada(self, obj):
        return obj.estado == 'DESPACHADA'

    class Meta:
        model = ColaDespacho
        fields = [
            'id', 'orden', 'orden_numero', 'producto', 'cantidad',
            'posicion_manual', 'estado', 'despachada', 'fecha_entrada',
            'fecha_despacho',
        ]
        read_only_fields = ['id', 'fecha_entrada']


class ActualizarProduccionSerializer(serializers.Serializer):
    # Serializer para actualizar produccion de una orden
    """
    Serializer para actualizar la cantidad producida de una orden
    """
    
    cantidad = serializers.DecimalField(
        max_digits=12, decimal_places=2, min_value=Decimal('0.01')
    )
    
    def validate_cantidad(self, value):
        """Valida que la cantidad sea positiva"""
        if value <= 0:
            raise serializers.ValidationError('La cantidad debe ser mayor a cero')
        return value
