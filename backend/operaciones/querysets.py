"""Querysets optimizados para evitar N+1 en listados API."""
from django.db.models import Count, Prefetch, QuerySet


def asignaciones_optimizadas(qs: QuerySet) -> QuerySet:
    return qs.select_related(
        'operario',
        'operario__usuario',
        'maquina',
        'maquina__tipo',
        'turno',
        'asignado_por',
    )


def operarios_optimizados(qs: QuerySet) -> QuerySet:
    return qs.select_related(
        'usuario',
        'turno_actual',
    ).prefetch_related('habilidades')


def habilidades_optimizadas(qs: QuerySet) -> QuerySet:
    return qs.select_related('empresa').prefetch_related(
        'tipos_maquina',
    ).annotate(total_operarios=Count('operarios', distinct=True))


def incidencias_optimizadas(qs: QuerySet) -> QuerySet:
    return qs.select_related(
        'maquina',
        'maquina__tipo',
        'reportado_por',
        'asignacion',
        'asignacion__operario',
        'resuelto_por',
    )


def eventos_optimizados(qs: QuerySet) -> QuerySet:
    return qs.select_related(
        'asignacion',
        'asignacion__operario',
        'asignacion__maquina',
        'registrado_por',
    )


def turnos_optimizados(qs: QuerySet) -> QuerySet:
    return qs.select_related('empresa')
