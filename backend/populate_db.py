"""Populate FLEX-OP with reusable demo data for all modules."""

import os
from datetime import date, time, timedelta
from decimal import Decimal

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flexop.settings')
django.setup()

from django.db import transaction
from django.utils import timezone

from alertas.models import Alerta, Notificacion, ReglaAlerta
from maquinas.models import EstadoMaquina, Maquina, TipoMaquina, UnidadEficiencia
from metricas.models import MetricaEficiencia, ObjetivoProduccion, RegistroProduccion
from operaciones.models import Asignacion, Evento, Habilidad, Incidencia, Operario, Turno
from ordenes.models import ColaDespacho, OrdenProduccion
from reasignaciones.models import SugerenciaReasignacion
from reportes.models import ReporteGenerado
from usuarios.models import Empresa, User


def touch(instance, **fields):
    instance.__class__.objects.filter(pk=instance.pk).update(**fields)
    instance.refresh_from_db()
    return instance


def upsert_user(*, username, email, password, first_name, last_name, rol, empresa):
    user = User.objects.filter(username=username).first()
    if user is None:
        user = User(username=username)

    user.email = email
    user.first_name = first_name
    user.last_name = last_name
    user.rol = rol
    user.empresa = empresa
    user.activo = True
    user.is_active = True
    user.is_staff = rol == User.RolChoices.ADMIN
    user.is_superuser = rol == User.RolChoices.ADMIN
    user.set_password(password)
    user.save()
    return user


def create_event(asignacion, tipo, when, usuario, observaciones, datos_json=None):
    event = Evento.objects.create(
        asignacion=asignacion,
        tipo=tipo,
        registrado_por=usuario,
        observaciones=observaciones,
        datos_json=datos_json,
    )
    return touch(event, fecha_hora=when)


def create_completed_assignment(*, operario, maquina, turno, start, duration_hours, cantidad_total, asignado_por, observaciones):
    end = start + timedelta(hours=duration_hours)
    asignacion = Asignacion.objects.create(
        operario=operario,
        maquina=maquina,
        turno=turno,
        fecha=start.date(),
        hora_inicio_real=start,
        hora_fin_real=end,
        estado=Asignacion.EstadoChoices.COMPLETADA,
        asignado_por=asignado_por,
        observaciones=observaciones,
    )

    EstadoMaquina.objects.create(
        maquina=maquina,
        estado=Maquina.EstadoChoices.OPERANDO,
        fecha_hora=start,
        usuario=operario.usuario,
        observacion=f'Inicio historico de asignacion #{asignacion.id}',
    )
    EstadoMaquina.objects.create(
        maquina=maquina,
        estado=Maquina.EstadoChoices.DISPONIBLE,
        fecha_hora=end,
        usuario=operario.usuario,
        observacion=f'Fin historico de asignacion #{asignacion.id}',
    )

    create_event(
        asignacion,
        Evento.TipoEventoChoices.INICIO,
        start,
        operario.usuario,
        f'Inicio de tarea en {maquina.nombre}',
    )
    create_event(
        asignacion,
        Evento.TipoEventoChoices.FIN,
        end,
        operario.usuario,
        f'Fin de tarea en {maquina.nombre}',
    )

    parcial_1 = (cantidad_total * Decimal('0.45')).quantize(Decimal('0.01'))
    parcial_2 = (cantidad_total - parcial_1).quantize(Decimal('0.01'))
    RegistroProduccion.objects.create(
        asignacion=asignacion,
        cantidad=parcial_1,
        fecha_hora=start + timedelta(hours=2),
        observaciones='Registro parcial inicial',
        registrado_por=operario.usuario,
    )
    RegistroProduccion.objects.create(
        asignacion=asignacion,
        cantidad=parcial_2,
        fecha_hora=end - timedelta(minutes=20),
        observaciones='Cierre de produccion del turno',
        registrado_por=operario.usuario,
    )
    MetricaEficiencia.calcular_para_asignacion(asignacion)
    return asignacion


def create_active_assignment(*, operario, maquina, turno, start, asignado_por, observaciones):
    asignacion = Asignacion.objects.create(
        operario=operario,
        maquina=maquina,
        turno=turno,
        fecha=start.date(),
        hora_inicio_real=start,
        estado=Asignacion.EstadoChoices.ACTIVA,
        asignado_por=asignado_por,
        observaciones=observaciones,
    )
    create_event(
        asignacion,
        Evento.TipoEventoChoices.INICIO,
        start,
        operario.usuario,
        f'Inicio de tarea en {maquina.nombre}',
    )
    EstadoMaquina.objects.create(
        maquina=maquina,
        estado=Maquina.EstadoChoices.OPERANDO,
        fecha_hora=start,
        usuario=operario.usuario,
        observacion=f'Asignacion activa #{asignacion.id}',
    )
    RegistroProduccion.objects.create(
        asignacion=asignacion,
        cantidad=Decimal('180.00'),
        fecha_hora=start + timedelta(minutes=40),
        observaciones='Primer bloque de produccion',
        registrado_por=operario.usuario,
    )
    RegistroProduccion.objects.create(
        asignacion=asignacion,
        cantidad=Decimal('240.00'),
        fecha_hora=start + timedelta(hours=1, minutes=30),
        observaciones='Segundo bloque de produccion',
        registrado_por=operario.usuario,
    )
    operario.disponible = False
    operario.save(update_fields=['disponible'])
    maquina.estado_actual = Maquina.EstadoChoices.OPERANDO
    maquina.save(update_fields=['estado_actual'])
    return asignacion


def seed_master_data():
    empresa, _ = Empresa.objects.update_or_create(
        ruc='20123456789',
        defaults={
            'nombre': 'ACME Industries',
            'razon_social': 'ACME Industries S.A.C.',
            'direccion': 'Av. Industrial 123, Lima',
            'telefono': '+51 1 234 5678',
            'email': 'contacto@acme.com',
            'activa': True,
        },
    )

    users = {
        'admin': upsert_user(
            username='admin',
            email='admin@flexop.com',
            password='admin123',
            first_name='Administrador',
            last_name='Sistema',
            rol=User.RolChoices.ADMIN,
            empresa=empresa,
        ),
        'supervisor': upsert_user(
            username='supervisor1',
            email='supervisor@acme.com',
            password='super123',
            first_name='Carlos',
            last_name='Mendoza',
            rol=User.RolChoices.SUPERVISOR,
            empresa=empresa,
        ),
        'gerente': upsert_user(
            username='gerente1',
            email='gerente@acme.com',
            password='gerente123',
            first_name='Maria',
            last_name='Garcia',
            rol=User.RolChoices.GERENTE,
            empresa=empresa,
        ),
        'operario1': upsert_user(
            username='operario1',
            email='operario1@acme.com',
            password='operario123',
            first_name='Juan',
            last_name='Perez',
            rol=User.RolChoices.OPERARIO,
            empresa=empresa,
        ),
        'operario2': upsert_user(
            username='operario2',
            email='operario2@acme.com',
            password='operario123',
            first_name='Ana',
            last_name='Lopez',
            rol=User.RolChoices.OPERARIO,
            empresa=empresa,
        ),
        'operario3': upsert_user(
            username='operario3',
            email='operario3@acme.com',
            password='operario123',
            first_name='Pedro',
            last_name='Ramirez',
            rol=User.RolChoices.OPERARIO,
            empresa=empresa,
        ),
    }

    turnos = {
        'manana': Turno.objects.update_or_create(
            empresa=empresa,
            nombre='Turno Mañana',
            defaults={'hora_inicio': time(7, 0), 'hora_fin': time(15, 0), 'activo': True},
        )[0],
        'tarde': Turno.objects.update_or_create(
            empresa=empresa,
            nombre='Turno Tarde',
            defaults={'hora_inicio': time(15, 0), 'hora_fin': time(23, 0), 'activo': True},
        )[0],
        'noche': Turno.objects.update_or_create(
            empresa=empresa,
            nombre='Turno Noche',
            defaults={'hora_inicio': time(23, 0), 'hora_fin': time(7, 0), 'activo': True},
        )[0],
    }

    tipo_llenadora = TipoMaquina.objects.update_or_create(
        nombre='Llenadora',
        defaults={'descripcion': 'Maquina para llenado de envases', 'empresa': empresa},
    )[0]
    tipo_etiquetadora = TipoMaquina.objects.update_or_create(
        nombre='Etiquetadora',
        defaults={'descripcion': 'Maquina para aplicacion de etiquetas', 'empresa': empresa},
    )[0]

    unidad = UnidadEficiencia.objects.update_or_create(
        empresa=empresa,
        nombre='Unidades por Hora',
        defaults={'abreviatura': 'u/h', 'descripcion': 'Cantidad producida por hora'},
    )[0]

    hab_llenadora = Habilidad.objects.update_or_create(
        empresa=empresa,
        nombre='Operación de Llenadora',
        defaults={'descripcion': 'Capacitado para operar maquinas llenadoras'},
    )[0]
    hab_llenadora.tipos_maquina.set([tipo_llenadora])

    hab_etiquetadora = Habilidad.objects.update_or_create(
        empresa=empresa,
        nombre='Operación de Etiquetadora',
        defaults={'descripcion': 'Capacitado para operar maquinas etiquetadoras'},
    )[0]
    hab_etiquetadora.tipos_maquina.set([tipo_etiquetadora])

    hab_mantenimiento = Habilidad.objects.update_or_create(
        empresa=empresa,
        nombre='Mantenimiento Básico',
        defaults={'descripcion': 'Conocimientos de mantenimiento preventivo'},
    )[0]

    maquinas = {
        'llenadora_1': Maquina.objects.update_or_create(
            codigo='LLE-001',
            defaults={
                'nombre': 'Llenadora Principal',
                'tipo': tipo_llenadora,
                'empresa': empresa,
                'marca': 'ACME',
                'modelo': 'FL-3000',
                'capacidad_teorica': Decimal('300.00'),
                'unidad_capacidad': unidad,
                'estado_actual': Maquina.EstadoChoices.DISPONIBLE,
                'activa': True,
            },
        )[0],
        'llenadora_2': Maquina.objects.update_or_create(
            codigo='LLE-002',
            defaults={
                'nombre': 'Llenadora Secundaria',
                'tipo': tipo_llenadora,
                'empresa': empresa,
                'marca': 'ACME',
                'modelo': 'FL-2500',
                'capacidad_teorica': Decimal('250.00'),
                'unidad_capacidad': unidad,
                'estado_actual': Maquina.EstadoChoices.DISPONIBLE,
                'activa': True,
            },
        )[0],
        'etiquetadora_1': Maquina.objects.update_or_create(
            codigo='ETQ-001',
            defaults={
                'nombre': 'Etiquetadora Automatica',
                'tipo': tipo_etiquetadora,
                'empresa': empresa,
                'marca': 'LabelPro',
                'modelo': 'LP-500',
                'capacidad_teorica': Decimal('500.00'),
                'unidad_capacidad': unidad,
                'estado_actual': Maquina.EstadoChoices.DISPONIBLE,
                'activa': True,
            },
        )[0],
    }

    operarios = {
        'operario1': Operario.objects.update_or_create(
            usuario=users['operario1'],
            defaults={
                'codigo_empleado': 'OP-001',
                'fecha_contratacion': date(2023, 1, 15),
                'turno_actual': turnos['manana'],
                'disponible': True,
                'activo': True,
            },
        )[0],
        'operario2': Operario.objects.update_or_create(
            usuario=users['operario2'],
            defaults={
                'codigo_empleado': 'OP-002',
                'fecha_contratacion': date(2023, 3, 10),
                'turno_actual': turnos['tarde'],
                'disponible': True,
                'activo': True,
            },
        )[0],
        'operario3': Operario.objects.update_or_create(
            usuario=users['operario3'],
            defaults={
                'codigo_empleado': 'OP-003',
                'fecha_contratacion': date(2023, 5, 20),
                'turno_actual': turnos['manana'],
                'disponible': True,
                'activo': True,
            },
        )[0],
    }
    operarios['operario1'].habilidades.set([hab_llenadora, hab_mantenimiento])
    operarios['operario2'].habilidades.set([hab_etiquetadora])
    operarios['operario3'].habilidades.set([hab_llenadora, hab_etiquetadora, hab_mantenimiento])

    return {
        'empresa': empresa,
        'users': users,
        'turnos': turnos,
        'maquinas': maquinas,
        'operarios': operarios,
    }


def reset_operational_data(empresa):
    ReporteGenerado.objects.filter(empresa=empresa).delete()
    ColaDespacho.objects.filter(empresa=empresa).delete()
    OrdenProduccion.objects.filter(empresa=empresa).delete()
    SugerenciaReasignacion.objects.filter(empresa=empresa).delete()
    Notificacion.objects.filter(usuario__empresa=empresa).delete()
    Alerta.objects.filter(empresa=empresa).delete()
    ReglaAlerta.objects.filter(empresa=empresa).delete()
    ObjetivoProduccion.objects.filter(empresa=empresa).delete()
    MetricaEficiencia.objects.filter(operario__usuario__empresa=empresa).delete()
    RegistroProduccion.objects.filter(asignacion__operario__usuario__empresa=empresa).delete()
    Incidencia.objects.filter(maquina__empresa=empresa).delete()
    Evento.objects.filter(asignacion__operario__usuario__empresa=empresa).delete()
    Asignacion.objects.filter(operario__usuario__empresa=empresa).delete()
    EstadoMaquina.objects.filter(maquina__empresa=empresa).delete()
    Operario.objects.filter(usuario__empresa=empresa).update(
        disponible=True,
        eficiencia_promedio=Decimal('0.00'),
        total_tareas_completadas=0,
    )
    Maquina.objects.filter(empresa=empresa).update(estado_actual=Maquina.EstadoChoices.DISPONIBLE)


def seed_operational_data(context):
    now = timezone.now()
    today = timezone.localdate()
    empresa = context['empresa']
    users = context['users']
    turnos = context['turnos']
    maquinas = context['maquinas']
    operarios = context['operarios']

    completed_specs = [
        ('operario1', 'llenadora_1', 'manana', now - timedelta(days=6, hours=9), Decimal('2050.00')),
        ('operario2', 'etiquetadora_1', 'tarde', now - timedelta(days=5, hours=8), Decimal('2900.00')),
        ('operario3', 'llenadora_2', 'manana', now - timedelta(days=4, hours=9), Decimal('1900.00')),
        ('operario1', 'llenadora_1', 'manana', now - timedelta(days=3, hours=9), Decimal('1980.00')),
        ('operario2', 'etiquetadora_1', 'tarde', now - timedelta(days=2, hours=8), Decimal('2400.00')),
        ('operario3', 'llenadora_1', 'manana', now - timedelta(days=1, hours=9), Decimal('2280.00')),
    ]
    for operario_key, maquina_key, turno_key, start, cantidad in completed_specs:
        create_completed_assignment(
            operario=operarios[operario_key],
            maquina=maquinas[maquina_key],
            turno=turnos[turno_key],
            start=start,
            duration_hours=8,
            cantidad_total=cantidad,
            asignado_por=users['supervisor'],
            observaciones='Asignacion historica de demostracion',
        )

    active_assignment = create_active_assignment(
        operario=operarios['operario1'],
        maquina=maquinas['llenadora_1'],
        turno=turnos['manana'],
        start=now - timedelta(hours=2, minutes=10),
        asignado_por=users['supervisor'],
        observaciones='Produccion del turno actual',
    )

    pending_assignment = Asignacion.objects.create(
        operario=operarios['operario2'],
        maquina=maquinas['etiquetadora_1'],
        turno=turnos['tarde'],
        fecha=today,
        estado=Asignacion.EstadoChoices.PENDIENTE,
        asignado_por=users['supervisor'],
        observaciones='Preparada para iniciar despues del cambio de lote',
    )

    Asignacion.objects.create(
        operario=operarios['operario3'],
        maquina=maquinas['llenadora_2'],
        turno=turnos['manana'],
        fecha=today - timedelta(days=1),
        estado=Asignacion.EstadoChoices.CANCELADA,
        asignado_por=users['supervisor'],
        observaciones='Cancelada por ajuste de plan de produccion',
    )

    for operario in operarios.values():
        operario.total_tareas_completadas = Asignacion.objects.filter(
            operario=operario,
            estado=Asignacion.EstadoChoices.COMPLETADA,
        ).count()
        operario.actualizar_eficiencia_promedio()
        operario.save(update_fields=['total_tareas_completadas', 'eficiencia_promedio', 'disponible'])

    maquinas['llenadora_2'].estado_actual = Maquina.EstadoChoices.PARADA
    maquinas['llenadora_2'].save(update_fields=['estado_actual'])
    EstadoMaquina.objects.create(
        maquina=maquinas['llenadora_2'],
        estado=Maquina.EstadoChoices.PARADA,
        fecha_hora=now - timedelta(hours=3),
        usuario=users['supervisor'],
        observacion='Parada por inspeccion de sensor',
    )

    maquinas['etiquetadora_1'].estado_actual = Maquina.EstadoChoices.DISPONIBLE
    maquinas['etiquetadora_1'].save(update_fields=['estado_actual'])
    EstadoMaquina.objects.create(
        maquina=maquinas['etiquetadora_1'],
        estado=Maquina.EstadoChoices.DISPONIBLE,
        fecha_hora=now - timedelta(minutes=45),
        usuario=users['supervisor'],
        observacion='Lista para nuevo lote',
    )

    inc_open = Incidencia.objects.create(
        asignacion=None,
        maquina=maquinas['llenadora_2'],
        tipo=Incidencia.TipoChoices.FALLA_MAQUINA,
        prioridad=Incidencia.PrioridadChoices.CRITICA,
        estado=Incidencia.EstadoChoices.ABIERTA,
        titulo='Sensor de temperatura fuera de rango',
        descripcion='La llenadora secundaria detuvo el lote por lecturas inestables.',
        reportado_por=users['operario3'],
    )
    touch(inc_open, fecha_reporte=now - timedelta(hours=2, minutes=30))

    inc_process = Incidencia.objects.create(
        asignacion=active_assignment,
        maquina=maquinas['llenadora_1'],
        tipo=Incidencia.TipoChoices.FALTA_MATERIAL,
        prioridad=Incidencia.PrioridadChoices.ALTA,
        estado=Incidencia.EstadoChoices.EN_PROCESO,
        titulo='Reposicion de tapas demorada',
        descripcion='Produccion parcial mientras se repone el material de empaque.',
        reportado_por=users['operario1'],
    )
    touch(inc_process, fecha_reporte=now - timedelta(minutes=95))

    inc_resolved = Incidencia.objects.create(
        asignacion=None,
        maquina=maquinas['etiquetadora_1'],
        tipo=Incidencia.TipoChoices.PROBLEMA_CALIDAD,
        prioridad=Incidencia.PrioridadChoices.MEDIA,
        estado=Incidencia.EstadoChoices.RESUELTA,
        titulo='Etiquetas desalineadas en lote anterior',
        descripcion='Se recalibro el cabezal y se validaron las muestras.',
        reportado_por=users['operario2'],
        resuelto_por=users['supervisor'],
        solucion='Recalibracion del cabezal de impresion y prueba de 50 unidades.',
    )
    touch(
        inc_resolved,
        fecha_reporte=now - timedelta(days=1, hours=4),
        fecha_resolucion=now - timedelta(days=1, hours=2, minutes=30),
    )

    ObjetivoProduccion.objects.create(
        tipo=ObjetivoProduccion.TipoObjetivoChoices.POR_MAQUINA,
        maquina=maquinas['llenadora_1'],
        empresa=empresa,
        cantidad_objetivo=Decimal('1200.00'),
        fecha_inicio=today,
        descripcion='Objetivo diario de la linea principal',
    )
    ObjetivoProduccion.objects.create(
        tipo=ObjetivoProduccion.TipoObjetivoChoices.POR_TURNO,
        turno=turnos['manana'],
        empresa=empresa,
        cantidad_objetivo=Decimal('2500.00'),
        fecha_inicio=today,
        descripcion='Objetivo del turno de manana',
    )
    ObjetivoProduccion.objects.create(
        tipo=ObjetivoProduccion.TipoObjetivoChoices.POR_OPERARIO,
        operario=operarios['operario1'],
        empresa=empresa,
        cantidad_objetivo=Decimal('900.00'),
        fecha_inicio=today,
        descripcion='Meta individual del operario principal',
    )

    rules = [
        ReglaAlerta.objects.create(
            nombre='Eficiencia debajo del objetivo',
            descripcion='Detecta operarios con eficiencia promedio baja',
            tipo=ReglaAlerta.TipoReglaChoices.EFICIENCIA_BAJA,
            umbral=Decimal('85.00'),
            unidad_umbral='porcentaje',
            prioridad=ReglaAlerta.PrioridadChoices.MEDIA,
            empresa=empresa,
        ),
        ReglaAlerta.objects.create(
            nombre='Maquina parada critica',
            descripcion='Notifica maquinas detenidas por mas de 30 minutos',
            tipo=ReglaAlerta.TipoReglaChoices.MAQUINA_PARADA,
            umbral=Decimal('30.00'),
            unidad_umbral='minutos',
            prioridad=ReglaAlerta.PrioridadChoices.CRITICA,
            empresa=empresa,
        ),
        ReglaAlerta.objects.create(
            nombre='Incidencia sin resolver',
            descripcion='Detecta incidencias abiertas por mas de una hora',
            tipo=ReglaAlerta.TipoReglaChoices.INCIDENCIA_SIN_RESOLVER,
            umbral=Decimal('60.00'),
            unidad_umbral='minutos',
            prioridad=ReglaAlerta.PrioridadChoices.ALTA,
            empresa=empresa,
        ),
        ReglaAlerta.objects.create(
            nombre='Objetivo diario comprometido',
            descripcion='Genera alerta cuando el cumplimiento esta por debajo del 95%',
            tipo=ReglaAlerta.TipoReglaChoices.OBJETIVO_NO_ALCANZADO,
            umbral=Decimal('95.00'),
            unidad_umbral='porcentaje',
            prioridad=ReglaAlerta.PrioridadChoices.ALTA,
            empresa=empresa,
        ),
    ]
    for rule in rules:
        rule.evaluar()

    manual_alert = Alerta.objects.create(
        titulo='Stock de envases en nivel preventivo',
        descripcion='Conviene reabastecer la linea principal antes del siguiente lote.',
        prioridad=Alerta.PrioridadChoices.MEDIA,
        estado=Alerta.EstadoChoices.ACTIVA,
        maquina_relacionada=maquinas['llenadora_1'],
        empresa=empresa,
    )
    objective_alert = Alerta.objects.filter(empresa=empresa, titulo__icontains='Objetivo').first()
    if objective_alert:
        objective_alert.escalar('Se requiere revision del plan diario con gerencia.')

    Notificacion.objects.create(
        usuario=users['supervisor'],
        alerta=manual_alert,
        titulo='Revisar stock preventivo de envases',
        mensaje='Hay una alerta activa de abastecimiento sobre la linea principal.',
    )
    read_notification = Notificacion.objects.create(
        usuario=users['admin'],
        alerta=manual_alert,
        titulo='Demo de notificacion leida',
        mensaje='Se usa para validar estados de lectura en la bandeja.',
        leida=True,
    )
    touch(read_notification, fecha_lectura=now - timedelta(minutes=25))

    SugerenciaReasignacion.objects.create(
        operario=operarios['operario3'],
        maquina_origen=None,
        maquina_destino=maquinas['etiquetadora_1'],
        razon=SugerenciaReasignacion.RazonChoices.MAQUINA_DISPONIBLE,
        descripcion='Operario libre con habilidad disponible para cubrir la etiquetadora.',
        impacto_estimado=Decimal('92.50'),
        estado=SugerenciaReasignacion.EstadoChoices.PENDIENTE,
        empresa=empresa,
    )
    SugerenciaReasignacion.objects.create(
        operario=operarios['operario2'],
        maquina_origen=maquinas['etiquetadora_1'],
        maquina_destino=maquinas['llenadora_1'],
        razon=SugerenciaReasignacion.RazonChoices.BALANCEAR_CARGA,
        descripcion='Ejemplo historico de sugerencia aceptada para balancear la carga.',
        impacto_estimado=Decimal('6.80'),
        estado=SugerenciaReasignacion.EstadoChoices.ACEPTADA,
        empresa=empresa,
        decidido_por=users['supervisor'],
        fecha_decision=now - timedelta(hours=6),
        notas_decision='Aceptada durante la planificacion del turno.',
        asignacion_creada=pending_assignment,
    )
    SugerenciaReasignacion.objects.create(
        operario=operarios['operario1'],
        maquina_origen=maquinas['llenadora_1'],
        maquina_destino=maquinas['llenadora_2'],
        razon=SugerenciaReasignacion.RazonChoices.OPTIMIZAR_EFICIENCIA,
        descripcion='Ejemplo de sugerencia descartada por prioridad de lote.',
        impacto_estimado=Decimal('4.20'),
        estado=SugerenciaReasignacion.EstadoChoices.RECHAZADA,
        empresa=empresa,
        decidido_por=users['supervisor'],
        fecha_decision=now - timedelta(days=1),
        notas_decision='Se mantiene asignacion actual hasta cerrar la orden urgente.',
    )

    orden_pendiente = OrdenProduccion.objects.create(
        numero_orden='OP-1001',
        producto='Botella 500ml lote premium',
        descripcion='Pedido prioritario para cliente retail',
        cantidad_requerida=Decimal('2000.00'),
        cantidad_producida=Decimal('0.00'),
        fecha_limite=now + timedelta(days=2),
        estado=OrdenProduccion.EstadoChoices.PENDIENTE,
        prioridad=OrdenProduccion.PrioridadChoices.URGENTE,
        maquina=maquinas['llenadora_1'],
        empresa=empresa,
        creada_por=users['gerente'],
        notas='Pendiente de liberar materia prima final.',
    )
    orden_en_proceso = OrdenProduccion.objects.create(
        numero_orden='OP-1002',
        producto='Botella 1L linea clasica',
        descripcion='Produccion de reposicion semanal',
        cantidad_requerida=Decimal('1800.00'),
        cantidad_producida=Decimal('850.00'),
        fecha_limite=now + timedelta(days=1),
        fecha_inicio=now - timedelta(hours=4),
        estado=OrdenProduccion.EstadoChoices.EN_PROCESO,
        prioridad=OrdenProduccion.PrioridadChoices.ALTA,
        maquina=maquinas['llenadora_1'],
        empresa=empresa,
        creada_por=users['gerente'],
        notas='Lote iniciado durante el turno actual.',
    )
    orden_lista = OrdenProduccion.objects.create(
        numero_orden='OP-1003',
        producto='Pack etiquetado promocional',
        descripcion='Orden terminada pendiente de despacho',
        cantidad_requerida=Decimal('1200.00'),
        cantidad_producida=Decimal('1200.00'),
        fecha_limite=now + timedelta(hours=12),
        fecha_inicio=now - timedelta(days=1, hours=2),
        fecha_completada=now - timedelta(hours=3),
        estado=OrdenProduccion.EstadoChoices.LISTA,
        prioridad=OrdenProduccion.PrioridadChoices.NORMAL,
        maquina=maquinas['etiquetadora_1'],
        empresa=empresa,
        creada_por=users['gerente'],
        notas='Lista para salida del camion nocturno.',
    )
    orden_despachada = OrdenProduccion.objects.create(
        numero_orden='OP-1004',
        producto='Botella 250ml cliente exportacion',
        descripcion='Orden cerrada y despachada',
        cantidad_requerida=Decimal('900.00'),
        cantidad_producida=Decimal('900.00'),
        fecha_limite=now - timedelta(days=1),
        fecha_inicio=now - timedelta(days=2, hours=5),
        fecha_completada=now - timedelta(days=1, hours=8),
        fecha_despachada=now - timedelta(days=1, hours=5),
        estado=OrdenProduccion.EstadoChoices.DESPACHADA,
        prioridad=OrdenProduccion.PrioridadChoices.BAJA,
        maquina=maquinas['llenadora_2'],
        empresa=empresa,
        creada_por=users['gerente'],
        notas='Despachada sin observaciones.',
    )
    cola_activa = ColaDespacho.objects.create(
        orden=orden_lista,
        empresa=empresa,
        estado=ColaDespacho.EstadoChoices.EN_COLA,
        posicion_manual=1,
        notas='Primera orden a despachar',
    )
    touch(cola_activa, fecha_entrada=now - timedelta(hours=2, minutes=30))

    cola_despachada = ColaDespacho.objects.create(
        orden=orden_despachada,
        empresa=empresa,
        estado=ColaDespacho.EstadoChoices.DESPACHADA,
        posicion_manual=2,
        despachado_por=users['admin'],
        notas='Despacho completado durante el turno anterior.',
    )
    touch(
        cola_despachada,
        fecha_entrada=now - timedelta(days=1, hours=7),
        fecha_despacho=now - timedelta(days=1, hours=5),
    )

    report_specs = [
        (ReporteGenerado.TipoReporteChoices.KPI_GERENCIAL, ReporteGenerado.FormatoChoices.PDF, today - timedelta(days=7), today),
        (ReporteGenerado.TipoReporteChoices.EFICIENCIA_SEMANAL, ReporteGenerado.FormatoChoices.EXCEL, today - timedelta(days=7), today),
        (ReporteGenerado.TipoReporteChoices.PRODUCCION_DIARIA, ReporteGenerado.FormatoChoices.CSV, today, today),
        (ReporteGenerado.TipoReporteChoices.INCIDENCIAS, ReporteGenerado.FormatoChoices.PDF, today - timedelta(days=3), today),
    ]
    for tipo, formato, fecha_inicio, fecha_fin in report_specs:
        ReporteGenerado.objects.create(
            tipo=tipo,
            formato=formato,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            empresa=empresa,
            generado_por=users['gerente'],
            parametros={'demo': True, 'rango': [str(fecha_inicio), str(fecha_fin)]},
        )

    return {
        'active_assignment': active_assignment,
        'pending_assignment': pending_assignment,
        'ordenes': [orden_pendiente, orden_en_proceso, orden_lista, orden_despachada],
    }


def print_summary(context):
    empresa = context['empresa']
    print('\n' + '=' * 60)
    print('Datos demo cargados correctamente')
    print('=' * 60)
    print(f"Empresa: {empresa.nombre}")
    print(f"Usuarios: {User.objects.filter(empresa=empresa).count()}")
    print(f"Maquinas: {Maquina.objects.filter(empresa=empresa).count()}")
    print(f"Asignaciones: {Asignacion.objects.filter(operario__usuario__empresa=empresa).count()}")
    print(f"Incidencias: {Incidencia.objects.filter(maquina__empresa=empresa).count()}")
    print(f"Alertas: {Alerta.objects.filter(empresa=empresa).count()}")
    print(f"Sugerencias: {SugerenciaReasignacion.objects.filter(empresa=empresa).count()}")
    print(f"Ordenes: {OrdenProduccion.objects.filter(empresa=empresa).count()}")
    print(f"Reportes: {ReporteGenerado.objects.filter(empresa=empresa).count()}")
    print('\nCredenciales principales:')
    print('  admin / admin123')
    print('  supervisor1 / super123')
    print('  gerente1 / gerente123')
    print('  operario1 / operario123')
    print('  operario2 / operario123')
    print('  operario3 / operario123')


def main():
    import os

    reset = os.environ.get('POPULATE_RESET', '0') == '1'
    print('Preparando datos demo completos para FLEX-OP...')
    with transaction.atomic():
        context = seed_master_data()
        empresa = context['empresa']
        tiene_operativo = Asignacion.objects.filter(
            operario__usuario__empresa=empresa,
        ).exists()
        if reset:
            print('POPULATE_RESET=1 — regenerando datos operativos...')
            reset_operational_data(empresa)
            seed_operational_data(context)
        elif not tiene_operativo:
            print('Sin datos operativos — cargando seed demo...')
            seed_operational_data(context)
        else:
            print(
                'Datos operativos existentes — omitiendo seed '
                '(use POPULATE_RESET=1 para regenerar).'
            )
    print_summary(context)


if __name__ == '__main__':
    main()
