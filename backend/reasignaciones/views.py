"""
ViewSets del modulo de Reasignaciones para FLEX-OP

Este archivo contiene las vistas para gestionar sugerencias
de reasignacion de operarios.
"""
from rest_framework import viewsets, filters, status
from usuarios.permissions import IsAuthenticatedFlex, IsSupervisorOrAboveForWrite, IsGerenteOrAbove
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count

from usuarios.mixins import EmpresaFilterMixin, EmpresaPerformCreateMixin

from .models import SugerenciaReasignacion
from .serializers import (
    SugerenciaReasignacionSerializer,
    AceptarSugerenciaSerializer,
    RechazarSugerenciaSerializer
)


class SugerenciaReasignacionViewSet(EmpresaPerformCreateMixin, EmpresaFilterMixin, viewsets.ModelViewSet):
    empresa_lookup = 'empresa'
    # Gestiona sugerencias de reasignacion
    """
    ViewSet para gestionar sugerencias de reasignacion
    
    El sistema genera sugerencias automaticas de reasignacion
    cuando detecta oportunidades de mejora. Los supervisores
    pueden aceptar o rechazar estas sugerencias.
    
    Endpoints disponibles:
    - GET /sugerencias/ - Lista todas las sugerencias
    - GET /sugerencias/{id}/ - Obtiene una sugerencia especifica
    - GET /sugerencias/pendientes/ - Lista sugerencias pendientes
    - POST /sugerencias/{id}/aceptar/ - Acepta y aplica la sugerencia
    - POST /sugerencias/{id}/rechazar/ - Rechaza la sugerencia
    - POST /sugerencias/generar/ - Genera nuevas sugerencias
    - GET /sugerencias/estadisticas/ - Estadisticas de sugerencias
    - GET /sugerencias/historial/ - Historial de decisiones
    """
    
    queryset = SugerenciaReasignacion.objects.all()
    serializer_class = SugerenciaReasignacionSerializer
    permission_classes = [IsAuthenticatedFlex]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['operario__codigo_empleado', 'descripcion']
    ordering_fields = ['fecha_creacion', 'impacto_estimado', 'estado']
    filterset_fields = ['estado', 'razon', 'empresa']
    
    # Deshabilitar creacion manual (se generan automaticamente)
    http_method_names = ['get', 'head', 'options', 'post']
    
    @action(detail=False, methods=['get'])
    def pendientes(self, request):
        """
        Lista sugerencias que estan pendientes de decision
        
        Ordena por impacto estimado para priorizar las mas importantes.
        """
        pendientes = self.get_queryset().filter(
            estado=SugerenciaReasignacion.EstadoChoices.PENDIENTE
        ).order_by('-impacto_estimado', '-fecha_creacion')
        
        serializer = self.get_serializer(pendientes, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def aceptar(self, request, pk=None):
        """
        Acepta una sugerencia y aplica la reasignacion
        
        Crea automaticamente la nueva asignacion del operario
        a la maquina destino.
        
        Puede recibir en el body:
        - notas: Notas sobre por que se acepta
        """
        sugerencia = self.get_object()
        
        if sugerencia.estado != SugerenciaReasignacion.EstadoChoices.PENDIENTE:
            return Response(
                {'error': 'Solo se pueden aceptar sugerencias pendientes'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = AceptarSugerenciaSerializer(data=request.data)
        
        if serializer.is_valid():
            notas = serializer.validated_data.get('notas', '')
            
            try:
                asignacion = sugerencia.aceptar(request.user, notas)
                
                return Response({
                    'mensaje': 'Sugerencia aceptada y reasignacion aplicada',
                    'sugerencia': SugerenciaReasignacionSerializer(sugerencia).data,
                    'asignacion_creada': asignacion.id
                })
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def rechazar(self, request, pk=None):
        """
        Rechaza una sugerencia
        
        Requiere en el body:
        - notas: Razon por la cual se rechaza
        """
        sugerencia = self.get_object()
        
        if sugerencia.estado != SugerenciaReasignacion.EstadoChoices.PENDIENTE:
            return Response(
                {'error': 'Solo se pueden rechazar sugerencias pendientes'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = RechazarSugerenciaSerializer(data=request.data)
        
        if serializer.is_valid():
            notas = serializer.validated_data['notas']
            sugerencia.rechazar(request.user, notas)
            
            return Response({
                'mensaje': 'Sugerencia rechazada',
                'sugerencia': SugerenciaReasignacionSerializer(sugerencia).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def generar(self, request):
        """
        Genera nuevas sugerencias de reasignacion
        
        Analiza la situacion actual y genera sugerencias basadas en:
        - Maquinas disponibles sin operario
        - Operarios disponibles con habilidades
        
        Requiere en el body:
        - empresa_id: ID de la empresa para la cual generar
        """
        from usuarios.models import Empresa

        empresa_id = request.data.get('empresa_id')
        user_empresa = request.user.empresa

        if not user_empresa and not request.user.es_admin:
            return Response(
                {'error': 'Usuario sin empresa asignada'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.user.es_admin and empresa_id:
            empresa = Empresa.objects.filter(id=empresa_id).first()
        else:
            empresa = user_empresa
            if empresa_id and int(empresa_id) != empresa.id:
                return Response(
                    {'error': 'No puede generar sugerencias para otra empresa'},
                    status=status.HTTP_403_FORBIDDEN
                )

        if not empresa:
            return Response(
                {'error': 'Empresa no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            
            sugerencias = SugerenciaReasignacion.generar_sugerencias(empresa)

            return Response({
                'mensaje': f'Se generaron {len(sugerencias)} sugerencias',
                'sugerencias': SugerenciaReasignacionSerializer(sugerencias, many=True).data
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """
        Obtiene estadisticas de sugerencias
        
        Retorna contadores por estado, razon y tasas de aceptacion.
        """
        total = self.get_queryset().count()
        aceptadas = self.get_queryset().filter(estado='ACEPTADA').count()
        rechazadas = self.get_queryset().filter(estado='RECHAZADA').count()
        
        # Tasa de aceptacion
        decididas = aceptadas + rechazadas
        tasa_aceptacion = (aceptadas / decididas * 100) if decididas > 0 else 0
        
        stats = {
            'por_estado': list(
                self.get_queryset().values('estado').annotate(total=Count('id'))
            ),
            'por_razon': list(
                self.get_queryset().values('razon').annotate(total=Count('id'))
            ),
            'total': total,
            'pendientes': self.get_queryset().filter(estado='PENDIENTE').count(),
            'aceptadas': aceptadas,
            'rechazadas': rechazadas,
            'tasa_aceptacion': round(tasa_aceptacion, 2)
        }
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def historial(self, request):
        """
        Obtiene el historial de sugerencias decididas
        
        Muestra sugerencias aceptadas y rechazadas ordenadas por fecha.
        
        Parametro de query opcional:
        - limite: Cantidad de registros (default 20)
        """
        limite = int(request.query_params.get('limite', 20))
        
        historial = self.get_queryset().exclude(
            estado=SugerenciaReasignacion.EstadoChoices.PENDIENTE
        ).order_by('-fecha_decision')[:limite]
        
        serializer = self.get_serializer(historial, many=True)
        return Response(serializer.data)

