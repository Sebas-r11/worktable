"""
Tests unitarios de modelos — app operaciones.
"""
from datetime import date, time

import pytest
from django.core.exceptions import ValidationError

from maquinas.models import Maquina, TipoMaquina, UnidadEficiencia
from operaciones.models import Asignacion, Habilidad, Operario, Turno
from usuarios.models import Empresa, User


@pytest.mark.django_db
class TestTurno:
    def test_str_incluye_nombre_y_horario(self, turno):
        texto = str(turno)
        assert 'Turno Mañana' in texto
        assert '06:00' in texto
        assert '14:00' in texto

    def test_duracion_horas_turno_diurno(self, empresa):
        turno = Turno.objects.create(
            nombre='Mañana',
            hora_inicio=time(6, 0),
            hora_fin=time(14, 0),
            empresa=empresa,
        )
        assert turno.duracion_horas() == pytest.approx(8.0)

    def test_duracion_horas_cruza_medianoche(self, empresa):
        turno = Turno.objects.create(
            nombre='Noche',
            hora_inicio=time(22, 0),
            hora_fin=time(6, 0),
            empresa=empresa,
        )
        assert turno.duracion_horas() == pytest.approx(8.0)


@pytest.mark.django_db
class TestOperarioPuedeOperar:
    def test_puede_operar_sin_habilidades_requeridas(self, operario, maquina, tipo_maquina):
        tipo_maquina.habilidades_requeridas.clear()
        assert operario.puede_operar(maquina) is True

    def test_puede_operar_con_habilidad_requerida(self, operario, maquina):
        assert operario.puede_operar(maquina) is True

    def test_no_puede_operar_sin_habilidad(self, operario, maquina, habilidad):
        operario.habilidades.remove(habilidad)
        assert operario.puede_operar(maquina) is False


@pytest.mark.django_db
class TestAsignacionClean:
    def test_rechaza_operario_sin_habilidad(self, operario, maquina, turno, habilidad):
        operario.habilidades.remove(habilidad)
        asignacion = Asignacion(
            operario=operario,
            maquina=maquina,
            turno=turno,
            fecha=date.today(),
            estado=Asignacion.EstadoChoices.PENDIENTE,
        )
        with pytest.raises(ValidationError) as exc:
            asignacion.full_clean()
        assert 'habilidad' in str(exc.value).lower()

    def test_rechaza_dos_asignaciones_activas_mismo_dia(
        self, operario, maquina, turno, supervisor_user
    ):
        Asignacion.objects.create(
            operario=operario,
            maquina=maquina,
            turno=turno,
            fecha=date.today(),
            estado=Asignacion.EstadoChoices.ACTIVA,
            asignado_por=supervisor_user,
        )
        segunda = Asignacion(
            operario=operario,
            maquina=maquina,
            turno=turno,
            fecha=date.today(),
            estado=Asignacion.EstadoChoices.ACTIVA,
        )
        with pytest.raises(ValidationError):
            segunda.full_clean()


@pytest.mark.django_db
class TestAsignacionFlujo:
    def test_iniciar_cambia_estado_y_marca_operario_no_disponible(
        self, asignacion_pendiente, operario, maquina
    ):
        asignacion_pendiente.iniciar()
        asignacion_pendiente.refresh_from_db()
        operario.refresh_from_db()
        maquina.refresh_from_db()

        assert asignacion_pendiente.estado == Asignacion.EstadoChoices.ACTIVA
        assert asignacion_pendiente.hora_inicio_real is not None
        assert operario.disponible is False
        assert maquina.estado_actual == Maquina.EstadoChoices.OPERANDO
        assert asignacion_pendiente.eventos.filter(
            tipo='INICIO'
        ).exists()

    def test_iniciar_desde_estado_no_pendiente_falla(self, asignacion_pendiente):
        asignacion_pendiente.estado = Asignacion.EstadoChoices.ACTIVA
        asignacion_pendiente.save()
        with pytest.raises(ValidationError):
            asignacion_pendiente.iniciar()

    def test_finalizar_completa_y_libera_operario(
        self, asignacion_pendiente, operario, maquina
    ):
        asignacion_pendiente.iniciar()
        asignacion_pendiente.finalizar()
        asignacion_pendiente.refresh_from_db()
        operario.refresh_from_db()
        maquina.refresh_from_db()

        assert asignacion_pendiente.estado == Asignacion.EstadoChoices.COMPLETADA
        assert asignacion_pendiente.hora_fin_real is not None
        assert operario.disponible is True
        assert operario.total_tareas_completadas == 1
        assert maquina.estado_actual == Maquina.EstadoChoices.DISPONIBLE

    def test_duracion_minutos_tras_finalizar(self, asignacion_pendiente):
        asignacion_pendiente.iniciar()
        asignacion_pendiente.finalizar()
        assert asignacion_pendiente.duracion_minutos() is not None
        assert asignacion_pendiente.duracion_minutos() >= 0

    def test_iniciar_rechaza_maquina_con_asignacion_activa(
        self, operario, maquina, turno, supervisor_user, empresa, habilidad
    ):
        from usuarios.models import User

        otro_user = User.objects.create_user(
            username='operario2',
            email='operario2@test.com',
            password='TestPass123!',
            first_name='Otro',
            last_name='Operario',
            rol=User.RolChoices.OPERARIO,
            empresa=empresa,
            activo=True,
        )
        otro_operario = Operario.objects.create(
            usuario=otro_user,
            codigo_empleado='EMP-002',
            fecha_contratacion=date.today(),
            turno_actual=turno,
            disponible=True,
            activo=True,
        )
        otro_operario.habilidades.add(habilidad)

        primera = Asignacion.objects.create(
            operario=operario,
            maquina=maquina,
            turno=turno,
            fecha=date.today(),
            estado=Asignacion.EstadoChoices.PENDIENTE,
            asignado_por=supervisor_user,
        )
        segunda = Asignacion.objects.create(
            operario=otro_operario,
            maquina=maquina,
            turno=turno,
            fecha=date.today(),
            estado=Asignacion.EstadoChoices.PENDIENTE,
            asignado_por=supervisor_user,
        )
        primera.iniciar()
        with pytest.raises(ValidationError):
            segunda.iniciar()

    def test_finalizar_no_libera_maquina_si_queda_otra_activa(
        self, operario, maquina, turno, supervisor_user, empresa, habilidad
    ):
        from usuarios.models import User

        otro_user = User.objects.create_user(
            username='operario3',
            email='operario3@test.com',
            password='TestPass123!',
            first_name='Tercer',
            last_name='Operario',
            rol=User.RolChoices.OPERARIO,
            empresa=empresa,
            activo=True,
        )
        otro_operario = Operario.objects.create(
            usuario=otro_user,
            codigo_empleado='EMP-003',
            fecha_contratacion=date.today(),
            turno_actual=turno,
            disponible=True,
            activo=True,
        )
        otro_operario.habilidades.add(habilidad)

        asignacion_a = Asignacion.objects.create(
            operario=operario,
            maquina=maquina,
            turno=turno,
            fecha=date.today(),
            estado=Asignacion.EstadoChoices.PENDIENTE,
            asignado_por=supervisor_user,
        )
        asignacion_b = Asignacion.objects.create(
            operario=otro_operario,
            maquina=maquina,
            turno=turno,
            fecha=date.today(),
            estado=Asignacion.EstadoChoices.PENDIENTE,
            asignado_por=supervisor_user,
        )
        asignacion_a.iniciar()
        Asignacion.objects.filter(pk=asignacion_b.pk).update(
            estado=Asignacion.EstadoChoices.ACTIVA,
        )
        maquina.refresh_from_db()
        assert maquina.estado_actual == Maquina.EstadoChoices.OPERANDO

        asignacion_a.finalizar()
        maquina.refresh_from_db()
        assert maquina.estado_actual == Maquina.EstadoChoices.OPERANDO


@pytest.mark.django_db
class TestOperarioStr:
    def test_str_incluye_codigo_y_nombre(self, operario):
        assert 'EMP-001' in str(operario)
