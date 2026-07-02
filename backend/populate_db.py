"""Populate FLEX-OP with reusable demo data for all modules."""

import os
import random
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

# Escala del dataset demo (reproducible con random.seed)
RNG = random.Random(42)
HISTORY_DAYS = 60
NUM_OPERARIOS = 25
ASSIGNMENTS_WEEKDAY = (5, 10)
ASSIGNMENTS_WEEKEND = (1, 4)
NUM_INCIDENCIAS = 55
NUM_ORDENES = 45
NUM_REPORTES = 28
NUM_SUGERENCIAS_MANUAL = 12
NUM_ACTIVE_ASSIGNMENTS = 4
NUM_PENDING_ASSIGNMENTS = 15
NUM_CANCELLED_ASSIGNMENTS = 8


def _apply_populate_scale():
    """Ajusta volumen de datos: POPULATE_SCALE=full (local) | demo (deploy gratis)."""
    global HISTORY_DAYS, NUM_OPERARIOS, ASSIGNMENTS_WEEKDAY, ASSIGNMENTS_WEEKEND
    global NUM_INCIDENCIAS, NUM_ORDENES, NUM_REPORTES, NUM_SUGERENCIAS_MANUAL
    global NUM_ACTIVE_ASSIGNMENTS, NUM_PENDING_ASSIGNMENTS, NUM_CANCELLED_ASSIGNMENTS

    if os.getenv('POPULATE_SCALE', 'full').lower() != 'demo':
        return

    HISTORY_DAYS = 21
    NUM_OPERARIOS = 12
    ASSIGNMENTS_WEEKDAY = (3, 6)
    ASSIGNMENTS_WEEKEND = (1, 3)
    NUM_INCIDENCIAS = 25
    NUM_ORDENES = 20
    NUM_REPORTES = 12
    NUM_SUGERENCIAS_MANUAL = 6
    NUM_ACTIVE_ASSIGNMENTS = 3
    NUM_PENDING_ASSIGNMENTS = 8
    NUM_CANCELLED_ASSIGNMENTS = 4


_apply_populate_scale()

MACHINE_TYPE_SPECS = [
    ('Llenadora', 'LLE', Decimal('300.00'), 3),
    ('Etiquetadora', 'ETQ', Decimal('500.00'), 3),
    ('Empacadora', 'EMP', Decimal('400.00'), 3),
    ('Selladora', 'SEL', Decimal('350.00'), 3),
    ('Transportador', 'TRN', Decimal('200.00'), 2),
    ('Linea de Inspeccion', 'INS', Decimal('600.00'), 2),
]

OPERARIO_NAMES = [
    ('Juan', 'Perez'),
    ('Ana', 'Lopez'),
    ('Pedro', 'Ramirez'),
    ('Luis', 'Torres'),
    ('Carmen', 'Vega'),
    ('Miguel', 'Castro'),
    ('Rosa', 'Flores'),
    ('Diego', 'Rojas'),
    ('Elena', 'Mendoza'),
    ('Jorge', 'Silva'),
    ('Patricia', 'Herrera'),
    ('Ricardo', 'Gutierrez'),
    ('Sofia', 'Navarro'),
    ('Fernando', 'Ortega'),
    ('Lucia', 'Morales'),
    ('Andres', 'Campos'),
    ('Valeria', 'Paredes'),
    ('Hector', 'Salazar'),
    ('Gabriela', 'Ruiz'),
    ('Oscar', 'Vargas'),
    ('Daniela', 'Cruz'),
    ('Roberto', 'Aguilar'),
    ('Mariana', 'Ibarra'),
    ('Felipe', 'Soto'),
    ('Claudia', 'Reyes'),
]

PRODUCTOS = [
    'Botella 500ml lote premium',
    'Botella 1L linea clasica',
    'Pack etiquetado promocional',
    'Botella 250ml cliente exportacion',
    'Jarra 2L familia',
    'Botella 750ml gourmet',
    'Pack multipack 6 unidades',
    'Envase 330ml retail',
    'Botella 1.5L supermercado',
    'Lote etiquetas temporada',
    'Caja display 12 botellas',
    'Botella 600ml sport',
    'Pack corporativo personalizado',
    'Botella 400ml kids',
    'Envase retornable 1L',
    'Lote sellado alta demanda',
    'Botella 900ml restaurante',
    'Pack exportacion Asia',
    'Botella 200ml muestra',
    'Caja master 24 unidades',
    'Botella 1.2L premium',
    'Envase biodegradable 500ml',
    'Pack promocion verano',
    'Botella 350ml conveniencia',
    'Lote inspeccion calidad A',
    'Botella 800ml farmacia',
    'Pack retail cadena nacional',
    'Envase 500ml e-commerce',
    'Botella 1L organico',
    'Lote urgente cliente VIP',
    'Pack sellado especial',
    'Botella 450ml eventos',
    'Envase 1L distribuidor norte',
    'Caja pallet 48 unidades',
    'Botella 550ml linea economica',
    'Pack etiquetado black friday',
    'Botella 700ml horeca',
    'Envase 300ml vending',
    'Lote reposicion Q2',
    'Botella 650ml club',
    'Pack multipack 4 unidades',
    'Envase 900ml mayorista',
    'Botella 480ml campana',
    'Lote inspeccion reforzada',
    'Botella 520ml lanzamiento',
]

INCIDENCIA_TITULOS = [
    'Sensor de temperatura fuera de rango',
    'Reposicion de tapas demorada',
    'Etiquetas desalineadas en lote',
    'Falla en motor principal',
    'Cinta transportadora detenida',
    'Falta de film transparente',
    'Lectura erronea del codigo de barras',
    'Vibracion anormal en selladora',
    'Parada por limpieza profunda',
    'Desviacion en peso del envase',
    'Atasco en linea de empaque',
    'Fuga de presion en llenadora',
    'Calibracion pendiente del cabezal',
    'Material recibido con defectos',
    'Sobrecarga en transportador',
    'Interrupcion por cambio de formato',
    'Alarma de seguridad activada',
    'Retraso en entrega de insumos',
    'Muestra fuera de tolerancia',
    'Fallo en sistema neumatico',
]


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


def pick_compatible_pair(operarios, maquinas):
    pairs = [
        (operario, maquina)
        for operario in operarios
        for maquina in maquinas
        if operario.puede_operar(maquina)
    ]
    if pairs:
        return RNG.choice(pairs)
    return operarios[0], maquinas[0]


def pick_turno(turnos, hour):
    if 7 <= hour < 15:
        return turnos['manana']
    if 15 <= hour < 23:
        return turnos['tarde']
    return turnos['noche']


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

    operario.disponible = True
    operario.save(update_fields=['disponible'])
    maquina.estado_actual = Maquina.EstadoChoices.DISPONIBLE
    maquina.save(update_fields=['estado_actual'])
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
    cantidad_1 = Decimal(str(RNG.randint(120, 280)))
    cantidad_2 = Decimal(str(RNG.randint(180, 360)))
    RegistroProduccion.objects.create(
        asignacion=asignacion,
        cantidad=cantidad_1,
        fecha_hora=start + timedelta(minutes=40),
        observaciones='Primer bloque de produccion',
        registrado_por=operario.usuario,
    )
    RegistroProduccion.objects.create(
        asignacion=asignacion,
        cantidad=cantidad_2,
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
        'supervisor2': upsert_user(
            username='supervisor2',
            email='supervisor2@acme.com',
            password='super123',
            first_name='Laura',
            last_name='Quispe',
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

    unidad = UnidadEficiencia.objects.update_or_create(
        empresa=empresa,
        nombre='Unidades por Hora',
        defaults={'abreviatura': 'u/h', 'descripcion': 'Cantidad producida por hora'},
    )[0]

    tipos_maquina = {}
    habilidades = {}
    for type_name, prefix, capacidad, _count in MACHINE_TYPE_SPECS:
        tipo = TipoMaquina.objects.update_or_create(
            nombre=type_name,
            defaults={'descripcion': f'Maquina tipo {type_name.lower()}', 'empresa': empresa},
        )[0]
        tipos_maquina[type_name] = tipo

        hab_nombre = f'Operación de {type_name}'
        habilidad = Habilidad.objects.update_or_create(
            empresa=empresa,
            nombre=hab_nombre,
            defaults={'descripcion': f'Capacitado para operar {type_name.lower()}'},
        )[0]
        habilidad.tipos_maquina.set([tipo])
        habilidades[type_name] = habilidad

    hab_mantenimiento = Habilidad.objects.update_or_create(
        empresa=empresa,
        nombre='Mantenimiento Básico',
        defaults={'descripcion': 'Conocimientos de mantenimiento preventivo'},
    )[0]

    maquinas = {}
    maquinas_list = []
    machine_counter = 1
    for type_name, prefix, capacidad, count in MACHINE_TYPE_SPECS:
        tipo = tipos_maquina[type_name]
        for index in range(1, count + 1):
            codigo = f'{prefix}-{machine_counter:03d}'
            machine_counter += 1
            key = f'{prefix.lower()}_{index}'
            maquina = Maquina.objects.update_or_create(
                codigo=codigo,
                defaults={
                    'nombre': f'{type_name} {index}',
                    'tipo': tipo,
                    'empresa': empresa,
                    'marca': RNG.choice(['ACME', 'LabelPro', 'PackMaster', 'FlexLine']),
                    'modelo': f'{prefix}-{capacidad}',
                    'capacidad_teorica': capacidad - Decimal(str(index * 10)),
                    'unidad_capacidad': unidad,
                    'estado_actual': Maquina.EstadoChoices.DISPONIBLE,
                    'activa': True,
                },
            )[0]
            maquinas[key] = maquina
            maquinas_list.append(maquina)

    operarios = {}
    operarios_list = []
    turno_keys = ['manana', 'tarde', 'noche']
    all_habilidades = list(habilidades.values()) + [hab_mantenimiento]

    for index in range(1, NUM_OPERARIOS + 1):
        first_name, last_name = OPERARIO_NAMES[index - 1]
        username = f'operario{index}'
        users[username] = upsert_user(
            username=username,
            email=f'{username}@acme.com',
            password='operario123',
            first_name=first_name,
            last_name=last_name,
            rol=User.RolChoices.OPERARIO,
            empresa=empresa,
        )
        operario = Operario.objects.update_or_create(
            usuario=users[username],
            defaults={
                'codigo_empleado': f'OP-{index:03d}',
                'fecha_contratacion': date(2020 + (index % 5), (index % 12) + 1, min(index, 28)),
                'turno_actual': turnos[turno_keys[index % 3]],
                'disponible': True,
                'activo': True,
            },
        )[0]

        if index == 1:
            operario.habilidades.set([habilidades['Llenadora'], hab_mantenimiento])
        elif index == 2:
            operario.habilidades.set([habilidades['Etiquetadora']])
        elif index == 3:
            operario.habilidades.set([
                habilidades['Llenadora'],
                habilidades['Etiquetadora'],
                hab_mantenimiento,
            ])
        else:
            num_skills = RNG.randint(1, 3)
            operario.habilidades.set(RNG.sample(all_habilidades, num_skills))

        operarios[username] = operario
        operarios_list.append(operario)

    return {
        'empresa': empresa,
        'users': users,
        'turnos': turnos,
        'maquinas': maquinas,
        'maquinas_list': maquinas_list,
        'operarios': operarios,
        'operarios_list': operarios_list,
        'habilidades': habilidades,
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


def seed_completed_history(context, *, now, asignado_por):
    operarios_list = context['operarios_list']
    maquinas_list = context['maquinas_list']
    turnos = context['turnos']

    for days_ago in range(HISTORY_DAYS, 0, -1):
        day = now - timedelta(days=days_ago)
        is_weekend = day.weekday() >= 5
        low, high = ASSIGNMENTS_WEEKEND if is_weekend else ASSIGNMENTS_WEEKDAY
        for _ in range(RNG.randint(low, high)):
            operario, maquina = pick_compatible_pair(operarios_list, maquinas_list)
            start_hour = RNG.randint(6, 14)
            start = day.replace(hour=start_hour, minute=RNG.randint(0, 45), second=0, microsecond=0)
            duration = RNG.choice([6, 7, 8])
            capacidad = float(maquina.capacidad_teorica or 250)
            cantidad = Decimal(str(RNG.randint(int(capacidad * 5), int(capacidad * 9))))
            create_completed_assignment(
                operario=operario,
                maquina=maquina,
                turno=pick_turno(turnos, start_hour),
                start=start,
                duration_hours=duration,
                cantidad_total=cantidad,
                asignado_por=asignado_por,
                observaciones='Asignacion historica de demostracion',
            )


def seed_incidencias(context, *, now, users, active_assignments):
    empresa = context['empresa']
    maquinas_list = context['maquinas_list']
    operarios_list = context['operarios_list']
    tipos = list(Incidencia.TipoChoices.values)
    prioridades = list(Incidencia.PrioridadChoices.values)
    estados = list(Incidencia.EstadoChoices.values)
    supervisores = [users['supervisor'], users['supervisor2']]

    for index in range(NUM_INCIDENCIAS):
        maquina = RNG.choice(maquinas_list)
        operario = RNG.choice(operarios_list)
        estado = RNG.choices(estados, weights=[18, 12, 55, 15], k=1)[0]
        prioridad = RNG.choice(prioridades)
        tipo = RNG.choice(tipos)
        titulo = f'{RNG.choice(INCIDENCIA_TITULOS)} #{index + 1}'
        days_ago = RNG.randint(0, HISTORY_DAYS)
        fecha_reporte = now - timedelta(days=days_ago, hours=RNG.randint(1, 10))

        asignacion = None
        if estado in (Incidencia.EstadoChoices.EN_PROCESO, Incidencia.EstadoChoices.ABIERTA) and active_assignments:
            asignacion = RNG.choice(active_assignments)

        incidencia = Incidencia.objects.create(
            asignacion=asignacion,
            maquina=maquina,
            tipo=tipo,
            prioridad=prioridad,
            estado=estado,
            titulo=titulo,
            descripcion=f'Incidencia generada para pruebas de volumen en {maquina.nombre}.',
            reportado_por=operario.usuario,
            resuelto_por=RNG.choice(supervisores) if estado == Incidencia.EstadoChoices.RESUELTA else None,
            solucion='Intervencion de mantenimiento y validacion de linea.' if estado == Incidencia.EstadoChoices.RESUELTA else '',
        )
        fields = {'fecha_reporte': fecha_reporte}
        if estado == Incidencia.EstadoChoices.RESUELTA:
            fields['fecha_resolucion'] = fecha_reporte + timedelta(hours=RNG.randint(1, 48))
        touch(incidencia, **fields)

    # Mantener una maquina en parada para disparar alertas
    maquina_parada = context['maquinas_list'][1]
    maquina_parada.estado_actual = Maquina.EstadoChoices.PARADA
    maquina_parada.save(update_fields=['estado_actual'])
    EstadoMaquina.objects.create(
        maquina=maquina_parada,
        estado=Maquina.EstadoChoices.PARADA,
        fecha_hora=now - timedelta(hours=3),
        usuario=users['supervisor'],
        observacion='Parada por inspeccion de sensor',
    )


def seed_ordenes(context, *, now, users):
    empresa = context['empresa']
    maquinas_list = context['maquinas_list']
    estados = [
        OrdenProduccion.EstadoChoices.PENDIENTE,
        OrdenProduccion.EstadoChoices.EN_PROCESO,
        OrdenProduccion.EstadoChoices.LISTA,
        OrdenProduccion.EstadoChoices.DESPACHADA,
        OrdenProduccion.EstadoChoices.CANCELADA,
    ]
    prioridades = list(OrdenProduccion.PrioridadChoices.values)
    ordenes = []

    for index in range(NUM_ORDENES):
        estado = RNG.choices(estados, weights=[20, 25, 20, 30, 5], k=1)[0]
        cantidad = Decimal(str(RNG.randint(600, 3500)))
        producida = Decimal('0.00')
        fecha_inicio = None
        fecha_completada = None
        fecha_despachada = None

        if estado == OrdenProduccion.EstadoChoices.EN_PROCESO:
            producida = (cantidad * Decimal(str(RNG.uniform(0.2, 0.85)))).quantize(Decimal('0.01'))
            fecha_inicio = now - timedelta(hours=RNG.randint(2, 72))
        elif estado == OrdenProduccion.EstadoChoices.LISTA:
            producida = cantidad
            fecha_inicio = now - timedelta(days=RNG.randint(1, 10))
            fecha_completada = now - timedelta(hours=RNG.randint(1, 48))
        elif estado == OrdenProduccion.EstadoChoices.DESPACHADA:
            producida = cantidad
            fecha_inicio = now - timedelta(days=RNG.randint(3, 30))
            fecha_completada = fecha_inicio + timedelta(hours=RNG.randint(4, 20))
            fecha_despachada = fecha_completada + timedelta(hours=RNG.randint(1, 12))
        elif estado == OrdenProduccion.EstadoChoices.CANCELADA:
            fecha_inicio = now - timedelta(days=RNG.randint(1, 15))

        orden = OrdenProduccion.objects.create(
            numero_orden=f'OP-{1001 + index}',
            producto=PRODUCTOS[index % len(PRODUCTOS)],
            descripcion='Orden generada para dataset demo de alto volumen',
            cantidad_requerida=cantidad,
            cantidad_producida=producida,
            fecha_limite=now + timedelta(days=RNG.randint(-5, 14)),
            fecha_inicio=fecha_inicio,
            fecha_completada=fecha_completada,
            fecha_despachada=fecha_despachada,
            estado=estado,
            prioridad=RNG.choice(prioridades),
            maquina=RNG.choice(maquinas_list),
            empresa=empresa,
            creada_por=users['gerente'],
            notas='Generada por populate_db expandido.',
        )
        ordenes.append(orden)

        if estado == OrdenProduccion.EstadoChoices.LISTA:
            cola = ColaDespacho.objects.create(
                orden=orden,
                empresa=empresa,
                estado=ColaDespacho.EstadoChoices.EN_COLA,
                posicion_manual=index + 1,
                notas='En cola de despacho',
            )
            touch(cola, fecha_entrada=now - timedelta(hours=RNG.randint(1, 48)))
        elif estado == OrdenProduccion.EstadoChoices.DESPACHADA:
            cola = ColaDespacho.objects.create(
                orden=orden,
                empresa=empresa,
                estado=ColaDespacho.EstadoChoices.DESPACHADA,
                posicion_manual=index + 1,
                despachado_por=users['admin'],
                notas='Despacho completado',
            )
            touch(
                cola,
                fecha_entrada=fecha_completada - timedelta(hours=2),
                fecha_despacho=fecha_despachada,
            )

    return ordenes


def seed_operational_data(context):
    now = timezone.now()
    today = timezone.localdate()
    empresa = context['empresa']
    users = context['users']
    turnos = context['turnos']
    operarios = context['operarios']
    operarios_list = context['operarios_list']
    maquinas_list = context['maquinas_list']

    seed_completed_history(context, now=now, asignado_por=users['supervisor'])

    active_assignments = []
    busy_operarios = set()
    busy_maquinas = set()
    attempts = 0
    while len(active_assignments) < NUM_ACTIVE_ASSIGNMENTS and attempts < 200:
        attempts += 1
        operario, maquina = pick_compatible_pair(operarios_list, maquinas_list)
        if operario.id in busy_operarios or maquina.id in busy_maquinas:
            continue
        if not operario.disponible:
            continue
        start = now - timedelta(hours=RNG.randint(1, 3), minutes=RNG.randint(0, 50))
        active = create_active_assignment(
            operario=operario,
            maquina=maquina,
            turno=pick_turno(turnos, start.hour),
            start=start,
            asignado_por=users['supervisor'],
            observaciones='Produccion del turno actual',
        )
        active_assignments.append(active)
        busy_operarios.add(operario.id)
        busy_maquinas.add(maquina.id)

    pending_assignments = []
    attempts = 0
    while len(pending_assignments) < NUM_PENDING_ASSIGNMENTS and attempts < 300:
        attempts += 1
        operario, maquina = pick_compatible_pair(operarios_list, maquinas_list)
        if operario.id in busy_operarios or maquina.id in busy_maquinas:
            continue
        pending = Asignacion.objects.create(
            operario=operario,
            maquina=maquina,
            turno=operario.turno_actual,
            fecha=today + timedelta(days=RNG.randint(0, 2)),
            estado=Asignacion.EstadoChoices.PENDIENTE,
            asignado_por=users['supervisor'],
            observaciones='Asignacion pendiente de inicio',
        )
        pending_assignments.append(pending)
        busy_operarios.add(operario.id)
        busy_maquinas.add(maquina.id)

    for _ in range(NUM_CANCELLED_ASSIGNMENTS):
        operario, maquina = pick_compatible_pair(operarios_list, maquinas_list)
        Asignacion.objects.create(
            operario=operario,
            maquina=maquina,
            turno=operario.turno_actual,
            fecha=today - timedelta(days=RNG.randint(1, 14)),
            estado=Asignacion.EstadoChoices.CANCELADA,
            asignado_por=users['supervisor'],
            observaciones='Cancelada por ajuste de plan de produccion',
        )

    for operario in operarios_list:
        operario.total_tareas_completadas = Asignacion.objects.filter(
            operario=operario,
            estado=Asignacion.EstadoChoices.COMPLETADA,
        ).count()
        operario.actualizar_eficiencia_promedio()
        operario.save(update_fields=['total_tareas_completadas', 'eficiencia_promedio', 'disponible'])

    seed_incidencias(context, now=now, users=users, active_assignments=active_assignments)

    for maquina in maquinas_list[:5]:
        ObjetivoProduccion.objects.create(
            tipo=ObjetivoProduccion.TipoObjetivoChoices.POR_MAQUINA,
            maquina=maquina,
            empresa=empresa,
            cantidad_objetivo=Decimal(str(RNG.randint(900, 1800))),
            fecha_inicio=today - timedelta(days=RNG.randint(0, 7)),
            descripcion=f'Objetivo diario de {maquina.nombre}',
        )

    for turno_key in ('manana', 'tarde', 'noche'):
        ObjetivoProduccion.objects.create(
            tipo=ObjetivoProduccion.TipoObjetivoChoices.POR_TURNO,
            turno=turnos[turno_key],
            empresa=empresa,
            cantidad_objetivo=Decimal(str(RNG.randint(2200, 4200))),
            fecha_inicio=today,
            descripcion=f'Objetivo del {turnos[turno_key].nombre.lower()}',
        )

    for operario in RNG.sample(operarios_list, min(8, len(operarios_list))):
        ObjetivoProduccion.objects.create(
            tipo=ObjetivoProduccion.TipoObjetivoChoices.POR_OPERARIO,
            operario=operario,
            empresa=empresa,
            cantidad_objetivo=Decimal(str(RNG.randint(700, 1400))),
            fecha_inicio=today,
            descripcion=f'Meta individual de {operario.usuario.get_full_name()}',
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
        maquina_relacionada=maquinas_list[0],
        empresa=empresa,
    )
    objective_alert = Alerta.objects.filter(empresa=empresa, titulo__icontains='Objetivo').first()
    if objective_alert:
        objective_alert.escalar('Se requiere revision del plan diario con gerencia.')

    for usuario_key in ('supervisor', 'supervisor2', 'gerente', 'admin'):
        Notificacion.objects.create(
            usuario=users[usuario_key],
            alerta=manual_alert,
            titulo=f'Alerta operativa — {usuario_key}',
            mensaje='Notificacion generada por el seed de alto volumen.',
            leida=RNG.choice([True, False]),
        )

    razones = list(SugerenciaReasignacion.RazonChoices.values)
    estados_sug = list(SugerenciaReasignacion.EstadoChoices.values)
    for index in range(NUM_SUGERENCIAS_MANUAL):
        operario, maquina_destino = pick_compatible_pair(operarios_list, maquinas_list)
        maquina_origen = RNG.choice(maquinas_list) if RNG.random() > 0.3 else None
        estado = RNG.choices(estados_sug, weights=[35, 25, 25, 15], k=1)[0]
        sugerencia = SugerenciaReasignacion.objects.create(
            operario=operario,
            maquina_origen=maquina_origen,
            maquina_destino=maquina_destino,
            razon=RNG.choice(razones),
            descripcion=f'Sugerencia automatica de prueba #{index + 1}',
            impacto_estimado=Decimal(str(RNG.uniform(2, 95))).quantize(Decimal('0.01')),
            estado=estado,
            empresa=empresa,
            decidido_por=users['supervisor'] if estado not in (
                SugerenciaReasignacion.EstadoChoices.PENDIENTE,
                SugerenciaReasignacion.EstadoChoices.EXPIRADA,
            ) else None,
            fecha_decision=now - timedelta(hours=RNG.randint(1, 72)) if estado not in (
                SugerenciaReasignacion.EstadoChoices.PENDIENTE,
                SugerenciaReasignacion.EstadoChoices.EXPIRADA,
            ) else None,
            notas_decision='Decision registrada en seed demo.' if estado not in (
                SugerenciaReasignacion.EstadoChoices.PENDIENTE,
                SugerenciaReasignacion.EstadoChoices.EXPIRADA,
            ) else '',
        )
        if estado == SugerenciaReasignacion.EstadoChoices.ACEPTADA and pending_assignments:
            sugerencia.asignacion_creada = RNG.choice(pending_assignments)
            sugerencia.save(update_fields=['asignacion_creada'])

    SugerenciaReasignacion.generar_sugerencias(empresa)

    ordenes = seed_ordenes(context, now=now, users=users)

    report_types = list(ReporteGenerado.TipoReporteChoices.values)
    report_formats = list(ReporteGenerado.FormatoChoices.values)
    for index in range(NUM_REPORTES):
        fecha_fin = today - timedelta(days=index % 30)
        fecha_inicio = fecha_fin - timedelta(days=RNG.randint(1, 14))
        ReporteGenerado.objects.create(
            tipo=RNG.choice(report_types),
            formato=RNG.choice(report_formats),
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            empresa=empresa,
            generado_por=users['gerente'],
            parametros={'demo': True, 'indice': index, 'rango': [str(fecha_inicio), str(fecha_fin)]},
        )

    return {
        'active_assignments': active_assignments,
        'pending_assignments': pending_assignments,
        'ordenes': ordenes,
    }


def print_summary(context):
    empresa = context['empresa']
    asignaciones = Asignacion.objects.filter(operario__usuario__empresa=empresa)
    completadas = asignaciones.filter(estado=Asignacion.EstadoChoices.COMPLETADA).count()
    activas = asignaciones.filter(estado=Asignacion.EstadoChoices.ACTIVA).count()
    pendientes = asignaciones.filter(estado=Asignacion.EstadoChoices.PENDIENTE).count()

    print('\n' + '=' * 60)
    print('Datos demo cargados correctamente (dataset expandido)')
    print('=' * 60)
    print(f"Empresa: {empresa.nombre}")
    print(f"Usuarios: {User.objects.filter(empresa=empresa).count()}")
    print(f"Operarios: {Operario.objects.filter(usuario__empresa=empresa).count()}")
    print(f"Maquinas: {Maquina.objects.filter(empresa=empresa).count()}")
    print(f"Asignaciones: {asignaciones.count()} (completadas: {completadas}, activas: {activas}, pendientes: {pendientes})")
    print(f"Registros produccion: {RegistroProduccion.objects.filter(asignacion__operario__usuario__empresa=empresa).count()}")
    print(f"Metricas eficiencia: {MetricaEficiencia.objects.filter(operario__usuario__empresa=empresa).count()}")
    print(f"Incidencias: {Incidencia.objects.filter(maquina__empresa=empresa).count()}")
    print(f"Alertas: {Alerta.objects.filter(empresa=empresa).count()}")
    print(f"Notificaciones: {Notificacion.objects.filter(usuario__empresa=empresa).count()}")
    print(f"Sugerencias: {SugerenciaReasignacion.objects.filter(empresa=empresa).count()}")
    print(f"Ordenes: {OrdenProduccion.objects.filter(empresa=empresa).count()}")
    print(f"Reportes: {ReporteGenerado.objects.filter(empresa=empresa).count()}")
    print('\nCredenciales principales:')
    print('  admin / admin123')
    print('  supervisor1 / super123')
    print('  supervisor2 / super123')
    print('  gerente1 / gerente123')
    print('  operario1..operario25 / operario123')


def main():
    reset = os.environ.get('POPULATE_RESET', '0') == '1'
    print('Preparando dataset demo expandido para FLEX-OP...')
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
            print('Sin datos operativos — cargando seed demo expandido...')
            seed_operational_data(context)
        else:
            print(
                'Datos operativos existentes — omitiendo seed '
                '(use POPULATE_RESET=1 para regenerar).'
            )
    print_summary(context)


if __name__ == '__main__':
    main()
