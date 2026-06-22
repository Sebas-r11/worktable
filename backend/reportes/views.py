"""
ViewSets del modulo de Reportes para FLEX-OP

Este archivo contiene las vistas para generar reportes y dashboards.
Los dashboards proporcionan informacion en tiempo real segun el rol del usuario.
"""
from rest_framework import viewsets, status
from usuarios.permissions import (
    IsAuthenticatedFlex,
    IsGerenteOrAbove,
    IsOperario,
    IsSupervisorOrAbove,
)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Sum, Avg, Count
from django.utils import timezone
from django.http import FileResponse
from datetime import timedelta
import csv
from django.http import HttpResponse

from usuarios.mixins import EmpresaFilterMixin, EmpresaPerformCreateMixin

from .models import ReporteGenerado
from .serializers import ReporteGeneradoSerializer


class ReporteGeneradoViewSet(EmpresaPerformCreateMixin, EmpresaFilterMixin, viewsets.ModelViewSet):
    empresa_lookup = 'empresa'
    # Gestiona el historial de reportes generados
    """
    ViewSet para gestionar reportes generados
    
    Mantiene un historial de reportes que se han generado
    para poder descargarlos nuevamente.
    
    Endpoints disponibles:
    - GET /reportes-generados/ - Lista reportes generados
    - GET /reportes-generados/{id}/ - Obtiene un reporte especifico
    - DELETE /reportes-generados/{id}/ - Elimina un reporte
    """
    
    queryset = ReporteGenerado.objects.all()
    serializer_class = ReporteGeneradoSerializer
    permission_classes = [IsAuthenticatedFlex]
    filterset_fields = ['tipo', 'formato', 'empresa']
    
    # Solo lectura y eliminacion
    http_method_names = ['get', 'head', 'options', 'delete']

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticatedFlex, IsGerenteOrAbove])
    def descargar(self, request, pk=None):
        """Descarga autenticada del archivo — evita URLs arbitrarias en el cliente."""
        reporte = self.get_object()
        if not reporte.archivo:
            return Response(
                {'error': 'Este reporte no tiene archivo asociado'},
                status=status.HTTP_404_NOT_FOUND,
            )
        filename = reporte.archivo.name.rsplit('/', 1)[-1]
        return FileResponse(
            reporte.archivo.open('rb'),
            as_attachment=True,
            filename=filename,
        )


class DashboardOperarioView(APIView):
    # Dashboard para operarios
    """
    Vista de dashboard para operarios
    
    Proporciona la informacion que un operario necesita ver:
    - Su asignacion actual
    - Eficiencia del dia
    - Produccion registrada
    - Progreso hacia el objetivo
    
    GET /dashboard/operario/
    """
    
    permission_classes = [IsAuthenticatedFlex, IsOperario]

    def get(self, request):
        """Obtiene los datos del dashboard del operario"""
        from operaciones.models import Operario, Asignacion, Incidencia
        from metricas.models import RegistroProduccion, MetricaEficiencia
        
        user = request.user
        hoy = timezone.now().date()
        
        # Verificar que el usuario sea operario
        if not hasattr(user, 'perfil_operario'):
            return Response(
                {'error': 'Usuario no tiene perfil de operario'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        operario = user.perfil_operario
        
        # Asignación del día: ACTIVA tiene prioridad; si no, PENDIENTE (para iniciar tarea)
        asignacion_activa = Asignacion.objects.filter(
            operario=operario,
            fecha=hoy,
            estado=Asignacion.EstadoChoices.ACTIVA,
        ).first()
        if not asignacion_activa:
            asignacion_activa = Asignacion.objects.filter(
                operario=operario,
                fecha=hoy,
                estado=Asignacion.EstadoChoices.PENDIENTE,
            ).first()
        
        asignacion_data = None
        if asignacion_activa:
            asignacion_data = {
                'id': asignacion_activa.id,
                'estado': asignacion_activa.estado,
                'maquina': asignacion_activa.maquina.nombre,
                'maquina_codigo': asignacion_activa.maquina.codigo,
                'turno': asignacion_activa.turno.nombre,
                'hora_inicio': str(asignacion_activa.hora_inicio_real) if asignacion_activa.hora_inicio_real else None
            }
        
        # Produccion del dia
        produccion_hoy = RegistroProduccion.objects.filter(
            asignacion__operario=operario,
            fecha_hora__date=hoy
        ).aggregate(total=Sum('cantidad'))['total'] or 0
        
        # Eficiencia del dia
        metricas_hoy = MetricaEficiencia.objects.filter(
            operario=operario,
            fecha=hoy
        )
        eficiencia_hoy = metricas_hoy.aggregate(
            promedio=Avg('eficiencia_calculada')
        )['promedio'] or 0
        
        # Tareas completadas hoy
        tareas_hoy = Asignacion.objects.filter(
            operario=operario,
            fecha=hoy,
            estado='COMPLETADA'
        ).count()
        
        # Objetivo del dia (simplificado - en produccion vendria de ObjetivoProduccion)
        objetivo_dia = 1000  # Valor por defecto
        porcentaje_objetivo = (float(produccion_hoy) / objetivo_dia * 100) if objetivo_dia > 0 else 0
        
        incidencias_abiertas = Incidencia.objects.filter(
            reportado_por=user,
            estado__in=[
                Incidencia.EstadoChoices.ABIERTA,
                Incidencia.EstadoChoices.EN_PROCESO,
            ],
        ).count()

        return Response({
            'asignacion_activa': asignacion_data,
            'eficiencia_hoy': round(float(eficiencia_hoy), 2),
            'produccion_hoy': produccion_hoy,
            'objetivo_dia': objetivo_dia,
            'porcentaje_objetivo': round(porcentaje_objetivo, 2),
            'tareas_completadas_hoy': tareas_hoy,
            'eficiencia_promedio': float(operario.eficiencia_promedio),
            'incidencias_abiertas': incidencias_abiertas,
        })


class DashboardSupervisorView(APIView):
    # Dashboard para supervisores
    """
    Vista de dashboard para supervisores
    
    Proporciona la informacion que un supervisor necesita ver:
    - Estado de todas las maquinas
    - Alertas activas
    - Sugerencias de reasignacion
    - Eficiencia del turno
    - Ranking de operarios
    
    GET /dashboard/supervisor/
    """
    
    permission_classes = [IsAuthenticatedFlex, IsSupervisorOrAbove]

    def get(self, request):
        """Obtiene los datos del dashboard del supervisor"""
        from maquinas.models import Maquina
        from alertas.models import Alerta
        from reasignaciones.models import SugerenciaReasignacion
        from operaciones.models import Operario, Incidencia
        from metricas.models import MetricaEficiencia
        
        user = request.user
        empresa = user.empresa
        hoy = timezone.now().date()
        
        # Estado de maquinas
        maquinas = Maquina.objects.filter(empresa=empresa, activa=True)
        maquinas_estado = []
        for maquina in maquinas:
            color = 'verde'
            if maquina.estado_actual == 'PARADA':
                color = 'rojo'
            elif maquina.estado_actual == 'MANTENIMIENTO':
                color = 'amarillo'
            elif maquina.estado_actual == 'OPERANDO':
                color = 'verde'
            else:
                color = 'gris'
            
            maquinas_estado.append({
                'id': maquina.id,
                'codigo': maquina.codigo,
                'nombre': maquina.nombre,
                'estado': maquina.estado_actual,
                'color': color
            })
        
        # Alertas activas
        alertas_activas = Alerta.objects.filter(
            empresa=empresa,
            estado='ACTIVA'
        ).count()
        
        alertas_criticas = Alerta.objects.filter(
            empresa=empresa,
            estado='ACTIVA',
            prioridad='CRITICA'
        ).count()
        
        # Sugerencias pendientes
        sugerencias_pendientes = SugerenciaReasignacion.objects.filter(
            empresa=empresa,
            estado='PENDIENTE'
        ).count()
        
        # Eficiencia del turno
        eficiencia_turno = MetricaEficiencia.objects.filter(
            operario__usuario__empresa=empresa,
            fecha=hoy
        ).aggregate(promedio=Avg('eficiencia_calculada'))['promedio'] or 0
        
        # Ranking de operarios del turno
        ranking = Operario.objects.filter(
            usuario__empresa=empresa,
            activo=True
        ).order_by('-eficiencia_promedio')[:10]
        
        ranking_operarios = [
            {
                'codigo': op.codigo_empleado,
                'nombre': op.usuario.get_full_name(),
                'eficiencia': float(op.eficiencia_promedio)
            }
            for op in ranking
        ]
        
        # Incidencias abiertas
        incidencias_abiertas = Incidencia.objects.filter(
            maquina__empresa=empresa,
            estado__in=['ABIERTA', 'EN_PROCESO']
        ).count()
        
        return Response({
            'maquinas_estado': maquinas_estado,
            'alertas_activas': alertas_activas,
            'alertas_criticas': alertas_criticas,
            'sugerencias_pendientes': sugerencias_pendientes,
            'eficiencia_turno': round(eficiencia_turno, 2),
            'ranking_operarios': ranking_operarios,
            'incidencias_abiertas': incidencias_abiertas
        })


class DashboardGerenteView(APIView):
    # Dashboard para gerentes
    """
    Vista de dashboard para gerentes
    
    Proporciona KPIs y metricas gerenciales:
    - Eficiencia general
    - OEE aproximado
    - Cumplimiento de objetivos
    - Tendencias de eficiencia
    - Comparativa por turnos
    - Rankings de operarios y maquinas
    
    GET /dashboard/gerente/
    """
    
    permission_classes = [IsAuthenticatedFlex, IsGerenteOrAbove]

    def get(self, request):
        """Obtiene los datos del dashboard del gerente"""
        from maquinas.models import Maquina
        from operaciones.models import Operario, Turno, Incidencia
        from metricas.models import MetricaEficiencia, RegistroProduccion
        
        user = request.user
        empresa = user.empresa
        hoy = timezone.now().date()
        hace_7_dias = hoy - timedelta(days=7)
        
        # Eficiencia general (promedio de los ultimos 7 dias)
        eficiencia_general = MetricaEficiencia.objects.filter(
            operario__usuario__empresa=empresa,
            fecha__gte=hace_7_dias
        ).aggregate(promedio=Avg('eficiencia_calculada'))['promedio'] or 0
        eficiencia_general = float(eficiencia_general)
        
        # OEE aproximado (simplificado: disponibilidad * rendimiento * calidad)
        # En produccion real seria un calculo mas complejo
        maquinas_total = Maquina.objects.filter(empresa=empresa, activa=True).count()
        maquinas_operando = Maquina.objects.filter(
            empresa=empresa, 
            activa=True,
            estado_actual='OPERANDO'
        ).count()
        
        disponibilidad = (maquinas_operando / maquinas_total * 100) if maquinas_total > 0 else 0
        oee_aproximado = disponibilidad * (eficiencia_general / 100) * 0.95  # 95% calidad estimada
        
        # Cumplimiento de objetivos (simplificado)
        cumplimiento_objetivos = min(eficiencia_general, 100)
        
        # Produccion
        produccion_dia = RegistroProduccion.objects.filter(
            asignacion__maquina__empresa=empresa,
            fecha_hora__date=hoy
        ).aggregate(total=Sum('cantidad'))['total'] or 0
        
        produccion_semana = RegistroProduccion.objects.filter(
            asignacion__maquina__empresa=empresa,
            fecha_hora__date__gte=hace_7_dias
        ).aggregate(total=Sum('cantidad'))['total'] or 0
        
        # Tendencia de eficiencia (ultimos 7 dias) — una query agrupada
        tendencia_rows = MetricaEficiencia.objects.filter(
            operario__usuario__empresa=empresa,
            fecha__gte=hace_7_dias,
            fecha__lte=hoy,
        ).values('fecha').annotate(
            eficiencia=Avg('eficiencia_calculada')
        )
        eficiencia_por_fecha = {
            str(row['fecha']): float(row['eficiencia'] or 0)
            for row in tendencia_rows
        }
        tendencia = [
            {
                'fecha': str(hoy - timedelta(days=6 - i)),
                'eficiencia': round(
                    eficiencia_por_fecha.get(str(hoy - timedelta(days=6 - i)), 0),
                    2,
                ),
            }
            for i in range(7)
        ]

        # Comparativa por turnos — una query agrupada
        eficiencia_por_turno = {
            row['asignacion__turno__nombre']: float(row['eficiencia'] or 0)
            for row in MetricaEficiencia.objects.filter(
                asignacion__turno__empresa=empresa,
                fecha=hoy,
            ).values('asignacion__turno__nombre').annotate(
                eficiencia=Avg('eficiencia_calculada')
            )
        }
        comparativa_turnos = [
            {
                'turno': turno.nombre,
                'eficiencia': round(eficiencia_por_turno.get(turno.nombre, 0), 2),
            }
            for turno in Turno.objects.filter(empresa=empresa, activo=True)
        ]
        
        # Top 10 operarios
        top_operarios = Operario.objects.filter(
            usuario__empresa=empresa,
            activo=True
        ).order_by('-eficiencia_promedio')[:10]
        
        top_operarios_data = [
            {
                'codigo': op.codigo_empleado,
                'nombre': op.usuario.get_full_name(),
                'eficiencia': float(op.eficiencia_promedio)
            }
            for op in top_operarios
        ]
        
        # Bottom 5 operarios
        bottom_operarios = Operario.objects.filter(
            usuario__empresa=empresa,
            activo=True
        ).order_by('eficiencia_promedio')[:5]
        
        bottom_operarios_data = [
            {
                'codigo': op.codigo_empleado,
                'nombre': op.usuario.get_full_name(),
                'eficiencia': float(op.eficiencia_promedio)
            }
            for op in bottom_operarios
        ]
        
        # Ranking de maquinas — una query agrupada
        ranking_maquinas = [
            {
                'codigo': row['maquina__codigo'],
                'nombre': row['maquina__nombre'],
                'eficiencia': round(float(row['eficiencia'] or 0), 2),
            }
            for row in MetricaEficiencia.objects.filter(
                maquina__empresa=empresa,
                fecha__gte=hace_7_dias,
            ).values('maquina__codigo', 'maquina__nombre').annotate(
                eficiencia=Avg('eficiencia_calculada')
            ).order_by('-eficiencia')
        ]
        
        # Estadisticas de incidencias
        incidencias = Incidencia.objects.filter(
            maquina__empresa=empresa,
            fecha_reporte__date__gte=hace_7_dias
        )
        
        estadisticas_incidencias = {
            'total': incidencias.count(),
            'abiertas': incidencias.filter(estado__in=['ABIERTA', 'EN_PROCESO']).count(),
            'resueltas': incidencias.filter(estado='RESUELTA').count(),
            'por_tipo': list(
                incidencias.values('tipo').annotate(total=Count('id'))
            )
        }
        
        return Response({
            'eficiencia_general': round(eficiencia_general, 2),
            'oee_aproximado': round(oee_aproximado, 2),
            'cumplimiento_objetivos': round(cumplimiento_objetivos, 2),
            'produccion_total_dia': produccion_dia,
            'produccion_total_semana': produccion_semana,
            'tendencia_eficiencia': tendencia,
            'comparativa_turnos': comparativa_turnos,
            'top_operarios': top_operarios_data,
            'bottom_operarios': bottom_operarios_data,
            'ranking_maquinas': ranking_maquinas[:10],
            'estadisticas_incidencias': estadisticas_incidencias
        })


class ExportarCSVView(APIView):
    # Vista para exportar datos a CSV
    """
    Vista para exportar datos a CSV
    
    Permite exportar diferentes tipos de datos a formato CSV.
    
    GET /reportes/exportar-csv/?tipo=eficiencia&fecha_inicio=2026-03-01&fecha_fin=2026-03-09
    """
    
    permission_classes = [IsGerenteOrAbove]

    def get(self, request):
        """Genera y retorna un archivo CSV"""
        tipo = request.query_params.get('tipo')
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin', timezone.now().date())
        
        if not tipo:
            return Response(
                {'error': 'Se requiere el parametro tipo'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not fecha_inicio:
            return Response(
                {'error': 'Se requiere el parametro fecha_inicio'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        empresa = request.user.empresa
        
        # Crear respuesta CSV
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{tipo}_{fecha_inicio}_{fecha_fin}.csv"'
        
        writer = csv.writer(response)
        
        if tipo == 'eficiencia':
            from metricas.models import MetricaEficiencia
            
            writer.writerow(['Fecha', 'Operario', 'Maquina', 'Produccion Real', 'Produccion Teorica', 'Eficiencia'])
            
            metricas = MetricaEficiencia.objects.filter(
                operario__usuario__empresa=empresa,
                fecha__gte=fecha_inicio,
                fecha__lte=fecha_fin
            ).select_related('operario__usuario', 'maquina')
            
            for m in metricas:
                writer.writerow([
                    m.fecha,
                    m.operario.usuario.get_full_name(),
                    m.maquina.nombre,
                    m.produccion_real,
                    m.produccion_teorica,
                    m.eficiencia_calculada
                ])
        
        elif tipo == 'produccion':
            from metricas.models import RegistroProduccion
            
            writer.writerow(['Fecha', 'Maquina', 'Operario', 'Cantidad', 'Observaciones'])
            
            registros = RegistroProduccion.objects.filter(
                asignacion__maquina__empresa=empresa,
                fecha_hora__date__gte=fecha_inicio,
                fecha_hora__date__lte=fecha_fin
            ).select_related('asignacion__maquina', 'asignacion__operario__usuario')
            
            for r in registros:
                writer.writerow([
                    r.fecha_hora.date(),
                    r.asignacion.maquina.nombre,
                    r.asignacion.operario.usuario.get_full_name(),
                    r.cantidad,
                    r.observaciones
                ])
        
        elif tipo == 'incidencias':
            from operaciones.models import Incidencia
            
            writer.writerow(['Fecha', 'Maquina', 'Tipo', 'Prioridad', 'Estado', 'Titulo', 'Tiempo Abierta (min)'])
            
            incidencias = Incidencia.objects.filter(
                maquina__empresa=empresa,
                fecha_reporte__date__gte=fecha_inicio,
                fecha_reporte__date__lte=fecha_fin
            ).select_related('maquina')
            
            for i in incidencias:
                writer.writerow([
                    i.fecha_reporte.date(),
                    i.maquina.nombre,
                    i.get_tipo_display(),
                    i.get_prioridad_display(),
                    i.get_estado_display(),
                    i.titulo,
                    i.tiempo_abierta_minutos()
                ])
        
        else:
            return Response(
                {'error': f'Tipo de reporte no soportado: {tipo}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return response

