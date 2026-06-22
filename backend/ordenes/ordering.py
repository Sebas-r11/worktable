"""
Ordenamiento de negocio para órdenes y cola de despacho.

La prioridad CharField (BAJA, NORMAL, ALTA, URGENTE) no debe ordenarse
lexicográficamente; se anota un peso numérico explícito.
"""
from django.db.models import Case, IntegerField, QuerySet, When

PRIORIDAD_PESO = {
    'URGENTE': 4,
    'ALTA': 3,
    'NORMAL': 2,
    'BAJA': 1,
}


def _annotate_prioridad_peso(qs: QuerySet, prioridad_field: str) -> QuerySet:
    return qs.annotate(
        prioridad_peso=Case(
            When(**{prioridad_field: 'URGENTE'}, then=4),
            When(**{prioridad_field: 'ALTA'}, then=3),
            When(**{prioridad_field: 'NORMAL'}, then=2),
            When(**{prioridad_field: 'BAJA'}, then=1),
            default=0,
            output_field=IntegerField(),
        )
    )


def ordenar_ordenes_produccion(qs: QuerySet) -> QuerySet:
    """Órdenes: URGENTE primero, luego fecha límite, luego creación."""
    return _annotate_prioridad_peso(qs, 'prioridad').order_by(
        '-prioridad_peso',
        'fecha_limite',
        '-fecha_creacion',
    )


def ordenar_cola_despacho(qs: QuerySet) -> QuerySet:
    """
    Cola: prioridad de la orden, fecha límite, posición manual, entrada en cola.
    Criterio único compartido por API, modelo y despacho.
    """
    return _annotate_prioridad_peso(qs, 'orden__prioridad').order_by(
        '-prioridad_peso',
        'orden__fecha_limite',
        'posicion_manual',
        'fecha_entrada',
    )
