"""
ViewSets del modulo de Operaciones para FLEX-OP

Este archivo contiene las vistas que manejan las peticiones HTTP para
turnos, habilidades, operarios, asignaciones, eventos e incidencias.
"""
from rest_framework import viewsets, filters, status
from usuarios.permissions import (
    IsAuthenticatedFlex,
    IsSupervisorOrAbove,
    IsSupervisorOrAboveForWrite,
    CanTransitionAsignacion,
)
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone

from usuarios.mixins import EmpresaFilterMixin, EmpresaPerformCreateMixin

from .querysets import (
    asignaciones_optimizadas,
    eventos_optimizados,
    habilidades_optimizadas,
    incidencias_optimizadas,
    operarios_optimizados,
    turnos_optimizados,
)
from .models import Turno, Habilidad, Operario, Asignacion, Evento, Incidencia
from .serializers import (
    TurnoSerializer, 
    HabilidadSerializer, 
    OperarioSerializer,
    AsignacionSerializer,
    AsignacionCreateSerializer,
    EventoSerializer,
    IncidenciaSerializer,
    IncidenciaCreateSerializer,
    ResolverIncidenciaSerializer
)


class TurnoViewSet(EmpresaPerformCreateMixin, EmpresaFilterMixin, viewsets.ModelViewSet):
    empresa_lookup = 'empresa'
    # Gestiona el CRUD de turnos de trabajo
    """
    ViewSet para gestionar turnos de trabajo
    
    Los turnos definen los horarios de trabajo de los operarios.
    Solo usuarios autenticados pueden acceder a estos endpoints.
    
    Endpoints disponibles:
    - GET /turnos/ - Lista todos los turnos
    - POST /turnos/ - Crea un nuevo turno
    - GET /turnos/{id}/ - Obtiene un turno especifico
    - PUT /turnos/{id}/ - Actualiza un turno
    - DELETE /turnos/{id}/ - Elimina un turno
    - GET /turnos/activos/ - Lista solo turnos activos
    """
    
    queryset = Turno.objects.all()
    serializer_class = TurnoSerializer
    permission_classes = [IsSupervisorOrAboveForWrite]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre']
    ordering_fields = ['hora_inicio', 'nombre']
    filterset_fields = ['empresa', 'activo']
    
    def get_queryset(self):
        return turnos_optimizados(super().get_queryset())
    
    @action(detail=False, methods=['get'])
    def activos(self, request):
        """
        Lista solo los turnos que estan activos
        
        Util para mostrar opciones en formularios de asignacion.
        """
        activos = self.get_queryset().filter(activo=True)
        serializer = self.get_serializer(activos, many=True)
        return Response(serializer.data)


class HabilidadViewSet(EmpresaPerformCreateMixin, EmpresaFilterMixin, viewsets.ModelViewSet):
    empresa_lookup = 'empresa'
    # Gestiona el CRUD de habilidades de operarios
    """
    ViewSet para gestionar habilidades
    
    Las habilidades definen que capacidades tienen los operarios
    y que tipos de maquinas pueden operar.
    
    Endpoints disponibles:
    - GET /habilidades/ - Lista todas las habilidades
    - POST /habilidades/ - Crea una nueva habilidad
    - GET /habilidades/{id}/ - Obtiene una habilidad especifica
    - PUT /habilidades/{id}/ - Actualiza una habilidad
    - DELETE /habilidades/{id}/ - Elimina una habilidad
    - GET /habilidades/{id}/operarios/ - Lista operarios con esta habilidad
    """
    
    queryset = Habilidad.objects.all()
    serializer_class = HabilidadSerializer
    permission_classes = [IsSupervisorOrAboveForWrite]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['nombre']
    filterset_fields = ['empresa']
    
    def get_queryset(self):
        return habilidades_optimizadas(super().get_queryset())
    
    @action(detail=True, methods=['get'])
    def operarios(self, request, pk=None):
        """
        Lista todos los operarios que tienen esta habilidad
        
        Util para saber quien puede operar ciertos tipos de maquinas.
        """
        habilidad = self.get_object()
        operarios = operarios_optimizados(
            habilidad.operarios.filter(activo=True)
        )
        serializer = OperarioSerializer(operarios, many=True)
        return Response(serializer.data)


class OperarioViewSet(EmpresaFilterMixin, viewsets.ModelViewSet):
    empresa_lookup = 'usuario__empresa'
    # Gestiona el CRUD de operarios y acciones especiales
    """
    ViewSet para gestionar operarios
    
    Los operarios son los usuarios que operan las maquinas.
    Este viewset permite gestionarlos y consultar su estado.
    
    Endpoints disponibles:
    - GET /operarios/ - Lista todos los operarios
    - POST /operarios/ - Crea un nuevo operario
    - GET /operarios/{id}/ - Obtiene un operario especifico
    - PUT /operarios/{id}/ - Actualiza un operario
    - DELETE /operarios/{id}/ - Elimina un operario
    - GET /operarios/disponibles/ - Lista operarios disponibles
    - GET /operarios/{id}/puede-operar-maquina/ - Verifica si puede operar una maquina
    - GET /operarios/{id}/asignaciones/ - Lista asignaciones del operario
    """
    
    queryset = Operario.objects.all()
    serializer_class = OperarioSerializer
    permission_classes = [IsSupervisorOrAboveForWrite]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['codigo_empleado', 'usuario__first_name', 'usuario__last_name']
    ordering_fields = ['codigo_empleado', 'eficiencia_promedio']
    filterset_fields = ['disponible', 'activo', 'turno_actual']
    
    def get_queryset(self):
        return operarios_optimizados(super().get_queryset())
    
    @action(detail=False, methods=['get'])
    def disponibles(self, request):
        """
        Lista operarios disponibles para ser asignados
        
        Retorna solo operarios que estan activos y marcados como disponibles.
        """
        disponibles = self.get_queryset().filter(disponible=True, activo=True)
        serializer = self.get_serializer(disponibles, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def puede_operar_maquina(self, request, pk=None):
        """
        Verifica si el operario puede operar una maquina especifica
        
        Parametros de query:
        - maquina_id: ID de la maquina a verificar
        
        Retorna un objeto con el resultado de la verificacion.
        """
        operario = self.get_object()
        maquina_id = request.query_params.get('maquina_id')
        
        if not maquina_id:
            return Response(
                {'error': 'Se requiere el parametro maquina_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from maquinas.models import Maquina
            empresa = request.user.empresa
            maquina = Maquina.objects.get(id=maquina_id, empresa=empresa)
            puede = operario.puede_operar(maquina)
            
            return Response({
                'operario': operario.codigo_empleado,
                'maquina': maquina.codigo,
                'puede_operar': puede,
                'razon': '' if puede else f'No tiene habilidad para {maquina.tipo.nombre}'
            })
        except Maquina.DoesNotExist:
            return Response(
                {'error': 'Maquina no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['get'])
    def asignaciones(self, request, pk=None):
        """
        Lista todas las asignaciones del operario
        
        Parametros de query opcionales:
        - fecha: Filtrar por fecha especifica (YYYY-MM-DD)
        - estado: Filtrar por estado (PENDIENTE, ACTIVA, COMPLETADA, CANCELADA)
        """
        operario = self.get_object()
        asignaciones = asignaciones_optimizadas(operario.asignaciones.all())
        
        # Aplicar filtros opcionales
        fecha = request.query_params.get('fecha')
        if fecha:
            asignaciones = asignaciones.filter(fecha=fecha)
        
        estado = request.query_params.get('estado')
        if estado:
            asignaciones = asignaciones.filter(estado=estado)
        
        serializer = AsignacionSerializer(asignaciones, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def ranking(self, request):
        """
        Obtiene el ranking de operarios por eficiencia
        
        Parametros de query opcionales:
        - limite: Cantidad de operarios a retornar (default 10)
        - orden: 'asc' o 'desc' (default 'desc')
        """
        limite = int(request.query_params.get('limite', 10))
        orden = request.query_params.get('orden', 'desc')
        
        if orden == 'asc':
            operarios = self.get_queryset().filter(activo=True).order_by('eficiencia_promedio')[:limite]
        else:
            operarios = self.get_queryset().filter(activo=True).order_by('-eficiencia_promedio')[:limite]
        
        serializer = self.get_serializer(operarios, many=True)
        return Response(serializer.data)


class AsignacionViewSet(EmpresaFilterMixin, viewsets.ModelViewSet):
    empresa_lookup = 'operario__usuario__empresa'
    # Gestiona el CRUD de asignaciones operario-maquina
    """
    ViewSet para gestionar asignaciones
    
    Las asignaciones vinculan operarios con maquinas en fechas especificas.
    Este es el nucleo operativo del sistema.
    
    Endpoints disponibles:
    - GET /asignaciones/ - Lista todas las asignaciones
    - POST /asignaciones/ - Crea una nueva asignacion
    - GET /asignaciones/{id}/ - Obtiene una asignacion especifica
    - PUT /asignaciones/{id}/ - Actualiza una asignacion
    - DELETE /asignaciones/{id}/ - Elimina una asignacion
    - GET /asignaciones/activas/ - Lista asignaciones activas
    - GET /asignaciones/del-dia/ - Lista asignaciones del dia actual
    - POST /asignaciones/{id}/iniciar/ - Inicia una asignacion
    - POST /asignaciones/{id}/finalizar/ - Finaliza una asignacion
    - POST /asignaciones/{id}/pausar/ - Pausa una asignacion
    - POST /asignaciones/{id}/reanudar/ - Reanuda una asignacion
    """
    
    queryset = Asignacion.objects.all()
    permission_classes = [IsAuthenticatedFlex]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['operario__codigo_empleado', 'maquina__codigo', 'maquina__nombre']
    ordering_fields = ['fecha', 'estado', 'fecha_creacion']
    filterset_fields = ['estado', 'operario', 'maquina', 'turno', 'fecha']
    
    def get_serializer_class(self):
        """Retorna el serializer apropiado segun la accion"""
        if self.action == 'create':
            return AsignacionCreateSerializer
        return AsignacionSerializer

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsSupervisorOrAbove()]
        if self.action in ('iniciar', 'finalizar', 'pausar', 'reanudar', 'eventos'):
            return [CanTransitionAsignacion()]
        return [IsAuthenticatedFlex()]

    def get_queryset(self):
        return asignaciones_optimizadas(super().get_queryset())

    def destroy(self, request, *args, **kwargs):
        asignacion = self.get_object()
        if asignacion.estado not in (
            Asignacion.EstadoChoices.PENDIENTE,
            Asignacion.EstadoChoices.CANCELADA,
        ):
            return Response(
                {
                    'error': (
                        'Solo se pueden eliminar asignaciones pendientes '
                        'o canceladas'
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=False, methods=['get'])
    def activas(self, request):
        """
        Lista todas las asignaciones que estan actualmente activas
        
        Util para ver el estado actual de la operacion.
        """
        activas = self.get_queryset().filter(estado=Asignacion.EstadoChoices.ACTIVA)
        serializer = self.get_serializer(activas, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def del_dia(self, request):
        """
        Lista todas las asignaciones del dia actual
        
        Parametros de query opcionales:
        - fecha: Fecha especifica (YYYY-MM-DD), por defecto hoy
        """
        fecha = request.query_params.get('fecha', timezone.now().date())
        asignaciones = self.get_queryset().filter(fecha=fecha)
        serializer = self.get_serializer(asignaciones, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def iniciar(self, request, pk=None):
        """
        Inicia una asignacion pendiente
        
        Cambia el estado de PENDIENTE a ACTIVA, registra la hora de inicio
        y cambia el estado de la maquina a OPERANDO.
        """
        asignacion = self.get_object()
        
        try:
            asignacion.iniciar()
            serializer = self.get_serializer(asignacion)
            return Response({
                'mensaje': 'Asignacion iniciada correctamente',
                'asignacion': serializer.data
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def finalizar(self, request, pk=None):
        """
        Finaliza una asignacion activa
        
        Cambia el estado de ACTIVA a COMPLETADA, registra la hora de fin
        y cambia el estado de la maquina a DISPONIBLE.
        
        Opcionalmente puede recibir en el body:
        - observaciones: Notas sobre la finalizacion
        """
        asignacion = self.get_object()
        observaciones = request.data.get('observaciones', '')
        
        try:
            if observaciones:
                asignacion.observaciones += f"\nFinalizacion: {observaciones}"
                asignacion.save()
            
            asignacion.finalizar()
            
            # Calcular metrica de eficiencia
            from metricas.models import MetricaEficiencia
            MetricaEficiencia.calcular_para_asignacion(asignacion)
            
            serializer = self.get_serializer(asignacion)
            return Response({
                'mensaje': 'Asignacion finalizada correctamente',
                'asignacion': serializer.data
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def pausar(self, request, pk=None):
        """
        Registra una pausa en la asignacion
        
        Crea un evento de tipo PAUSA. Puede recibir:
        - motivo: Razon de la pausa
        """
        asignacion = self.get_object()
        motivo = request.data.get('motivo', 'Pausa registrada')
        
        if asignacion.estado != Asignacion.EstadoChoices.ACTIVA:
            return Response(
                {'error': 'Solo se pueden pausar asignaciones activas'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Crear evento de pausa
        Evento.objects.create(
            asignacion=asignacion,
            tipo=Evento.TipoEventoChoices.PAUSA,
            registrado_por=request.user,
            observaciones=motivo
        )
        
        return Response({
            'mensaje': 'Pausa registrada',
            'motivo': motivo
        })
    
    @action(detail=True, methods=['post'])
    def reanudar(self, request, pk=None):
        """
        Registra la reanudacion despues de una pausa
        
        Crea un evento de tipo REANUDACION.
        """
        asignacion = self.get_object()
        
        if asignacion.estado != Asignacion.EstadoChoices.ACTIVA:
            return Response(
                {'error': 'Solo se pueden reanudar asignaciones activas'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Crear evento de reanudacion
        Evento.objects.create(
            asignacion=asignacion,
            tipo=Evento.TipoEventoChoices.REANUDACION,
            registrado_por=request.user,
            observaciones='Tarea reanudada'
        )
        
        return Response({
            'mensaje': 'Reanudacion registrada'
        })
    
    @action(detail=True, methods=['get'])
    def eventos(self, request, pk=None):
        """
        Lista todos los eventos de una asignacion
        
        Permite ver el historial completo de lo que ocurrio
        durante la asignacion.
        """
        asignacion = self.get_object()
        eventos = asignacion.eventos.all()
        serializer = EventoSerializer(eventos, many=True)
        return Response(serializer.data)


class EventoViewSet(EmpresaFilterMixin, viewsets.ModelViewSet):
    empresa_lookup = 'asignacion__operario__usuario__empresa'
    # Gestiona eventos operacionales
    """
    ViewSet para gestionar eventos
    
    Los eventos registran lo que ocurre durante las asignaciones.
    Generalmente se crean automaticamente pero tambien pueden
    crearse manualmente.
    
    Endpoints disponibles:
    - GET /eventos/ - Lista todos los eventos
    - POST /eventos/ - Crea un nuevo evento
    - GET /eventos/{id}/ - Obtiene un evento especifico
    """
    
    queryset = Evento.objects.all()
    serializer_class = EventoSerializer
    permission_classes = [IsSupervisorOrAboveForWrite]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['fecha_hora']
    filterset_fields = ['asignacion', 'tipo']
    
    def get_queryset(self):
        return eventos_optimizados(super().get_queryset())
    
    def perform_create(self, serializer):
        """Asigna automaticamente el usuario que registra el evento"""
        serializer.save(registrado_por=self.request.user)


class IncidenciaViewSet(EmpresaFilterMixin, viewsets.ModelViewSet):
    empresa_lookup = 'maquina__empresa'
    # Gestiona incidencias y problemas
    """
    ViewSet para gestionar incidencias
    
    Las incidencias son problemas que afectan la produccion
    y deben ser resueltos.
    
    Endpoints disponibles:
    - GET /incidencias/ - Lista todas las incidencias
    - POST /incidencias/ - Reporta una nueva incidencia
    - GET /incidencias/{id}/ - Obtiene una incidencia especifica
    - PUT /incidencias/{id}/ - Actualiza una incidencia
    - DELETE /incidencias/{id}/ - Elimina una incidencia
    - GET /incidencias/abiertas/ - Lista incidencias sin resolver
    - POST /incidencias/{id}/resolver/ - Marca como resuelta
    - POST /incidencias/{id}/escalar/ - Escala a nivel superior
    """
    
    queryset = Incidencia.objects.all()
    permission_classes = [IsAuthenticatedFlex]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['titulo', 'descripcion', 'maquina__codigo']
    ordering_fields = ['fecha_reporte', 'prioridad']
    filterset_fields = ['estado', 'tipo', 'prioridad', 'maquina']
    
    def get_serializer_class(self):
        """Retorna el serializer apropiado segun la accion"""
        if self.action == 'create':
            return IncidenciaCreateSerializer
        return IncidenciaSerializer

    def get_permissions(self):
        if self.action in ('update', 'partial_update', 'destroy', 'escalar'):
            return [IsSupervisorOrAbove()]
        if self.action == 'resolver':
            return [IsSupervisorOrAbove()]
        return [IsAuthenticatedFlex()]

    def get_queryset(self):
        return incidencias_optimizadas(super().get_queryset())
    
    @action(detail=False, methods=['get'])
    def abiertas(self, request):
        """
        Lista incidencias que no han sido resueltas
        
        Incluye incidencias con estado ABIERTA o EN_PROCESO.
        """
        abiertas = self.get_queryset().filter(
            estado__in=[
                Incidencia.EstadoChoices.ABIERTA,
                Incidencia.EstadoChoices.EN_PROCESO
            ]
        )
        serializer = self.get_serializer(abiertas, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def resolver(self, request, pk=None):
        """
        Marca una incidencia como resuelta
        
        Requiere en el body:
        - solucion: Descripcion de como se resolvio
        """
        incidencia = self.get_object()
        serializer = ResolverIncidenciaSerializer(data=request.data)
        
        if serializer.is_valid():
            incidencia.resolver(
                usuario=request.user,
                solucion=serializer.validated_data['solucion']
            )
            return Response({
                'mensaje': 'Incidencia resuelta',
                'incidencia': IncidenciaSerializer(incidencia).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def escalar(self, request, pk=None):
        """
        Escala una incidencia a nivel superior
        
        Puede recibir en el body:
        - motivo: Razon por la que se escala
        """
        incidencia = self.get_object()
        motivo = request.data.get('motivo', 'Escalada por tiempo sin resolver')
        incidencia.escalar(motivo=motivo)

        return Response({
            'mensaje': 'Incidencia escalada',
            'motivo': motivo
        })
    
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """
        Obtiene estadisticas de incidencias
        
        Retorna contadores por tipo, estado y prioridad.
        """
        from django.db.models import Count
        
        stats = {
            'por_estado': list(
                self.get_queryset().values('estado').annotate(total=Count('id'))
            ),
            'por_tipo': list(
                self.get_queryset().values('tipo').annotate(total=Count('id'))
            ),
            'por_prioridad': list(
                self.get_queryset().values('prioridad').annotate(total=Count('id'))
            ),
            'total': self.get_queryset().count(),
            'abiertas': self.get_queryset().filter(
                estado__in=['ABIERTA', 'EN_PROCESO']
            ).count()
        }
        
        return Response(stats)

