"""Querysets optimizados — app alertas."""
from django.db.models import QuerySet


def alertas_optimizadas(qs: QuerySet) -> QuerySet:
    return qs.select_related(
        'regla',
        'empresa',
        'operario_relacionado',
        'operario_relacionado__usuario',
        'maquina_relacionada',
        'incidencia_relacionada',
        'objetivo_relacionado',
        'resuelta_por',
    )


def notificaciones_optimizadas(qs: QuerySet) -> QuerySet:
    return qs.select_related('alerta', 'usuario')
