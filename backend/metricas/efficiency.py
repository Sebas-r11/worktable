"""Cálculo de horas efectivas de trabajo para métricas de eficiencia."""
from decimal import Decimal

from django.utils import timezone


def horas_efectivas_asignacion(asignacion) -> Decimal | None:
    """
    Horas de trabajo restando intervalos PAUSA → REANUDACION.

    Si queda una pausa abierta al finalizar, se resta hasta hora_fin_real.
    """
    from operaciones.models import Evento

    if not asignacion.hora_inicio_real or not asignacion.hora_fin_real:
        return None

    duracion_total = asignacion.hora_fin_real - asignacion.hora_inicio_real
    segundos_pausa = 0
    pausa_inicio = None

    eventos = asignacion.eventos.filter(
        tipo__in=[
            Evento.TipoEventoChoices.PAUSA,
            Evento.TipoEventoChoices.REANUDACION,
        ]
    ).order_by('fecha_hora')

    for evento in eventos:
        if evento.tipo == Evento.TipoEventoChoices.PAUSA:
            pausa_inicio = evento.fecha_hora
        elif pausa_inicio is not None:
            segundos_pausa += (evento.fecha_hora - pausa_inicio).total_seconds()
            pausa_inicio = None

    if pausa_inicio is not None:
        fin = asignacion.hora_fin_real or timezone.now()
        segundos_pausa += (fin - pausa_inicio).total_seconds()

    segundos_efectivos = max(duracion_total.total_seconds() - segundos_pausa, 36)
    horas = Decimal(str(segundos_efectivos / 3600)).quantize(Decimal('0.01'))
    return max(horas, Decimal('0.01'))
