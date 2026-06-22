"""Querysets optimizados — app metricas."""
from django.db.models import QuerySet


def registros_produccion_optimizados(qs: QuerySet) -> QuerySet:
    return qs.select_related(
        'asignacion',
        'asignacion__operario',
        'asignacion__maquina',
        'registrado_por',
    )


def metricas_optimizadas(qs: QuerySet) -> QuerySet:
    return qs.select_related(
        'operario',
        'operario__usuario',
        'maquina',
        'maquina__unidad_capacidad',
        'asignacion',
    )


def objetivos_optimizados(qs: QuerySet) -> QuerySet:
    return qs.select_related(
        'empresa',
        'maquina',
        'turno',
        'operario',
        'operario__usuario',
    )
