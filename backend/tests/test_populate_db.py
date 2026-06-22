"""Tests de idempotencia de populate_db."""
import pytest

from operaciones.models import Asignacion


@pytest.mark.django_db
class TestPopulateIdempotente:
    def test_main_no_borra_datos_operativos_sin_reset(self, monkeypatch):
        monkeypatch.delenv('POPULATE_RESET', raising=False)
        from populate_db import main, seed_master_data, seed_operational_data

        context = seed_master_data()
        seed_operational_data(context)
        empresa = context['empresa']
        count_antes = Asignacion.objects.filter(
            operario__usuario__empresa=empresa,
        ).count()
        main()
        count_despues = Asignacion.objects.filter(
            operario__usuario__empresa=empresa,
        ).count()
        assert count_despues == count_antes
        assert count_antes > 0
