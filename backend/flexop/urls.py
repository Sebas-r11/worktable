"""
URL configuration for flexop project - FLEX-OP Platform
"""
from functools import wraps

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.http import Http404, JsonResponse
from django.views.static import serve
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
    TokenBlacklistView,
)
from usuarios.views_auth import FlexTokenObtainPairView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="FLEX-OP API",
        default_version='v1',
        description="API REST para FLEX-OP - Flexible Operations Platform",
        contact=openapi.Contact(email="admin@flexop.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


def _debug_only(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not settings.DEBUG:
            raise Http404()
        return view(request, *args, **kwargs)

    return wrapper


def health_check(_request):
    return JsonResponse({'status': 'ok', 'service': 'flexop-api'})


urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Health check (Render / monitoreo)
    path('api/health/', health_check, name='health-check'),

    # API JWT Authentication
    path('api/auth/login/', FlexTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/logout/', TokenBlacklistView.as_view(), name='token_blacklist'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # API Modules - Modulos principales de FLEX-OP
    path('api/', include('usuarios.urls')),       # Usuarios y empresas
    path('api/', include('maquinas.urls')),       # Maquinas y productos
    path('api/', include('operaciones.urls')),    # Turnos, operarios, asignaciones
    path('api/', include('metricas.urls')),       # Produccion y metricas
    path('api/', include('alertas.urls')),        # Alertas y notificaciones
    path('api/', include('reasignaciones.urls')), # Sugerencias de reasignacion
    path('api/', include('reportes.urls')),       # Dashboards y reportes
    path('api/', include('ordenes.urls')),        # Ordenes de produccion

    # API Documentation (solo disponible con DEBUG=True)
    path(
        'swagger/',
        _debug_only(schema_view.with_ui('swagger', cache_timeout=0)),
        name='schema-swagger-ui',
    ),
    path(
        'redoc/',
        _debug_only(schema_view.with_ui('redoc', cache_timeout=0)),
        name='schema-redoc',
    ),
    path(
        'swagger.json',
        _debug_only(schema_view.without_ui(cache_timeout=0)),
        name='schema-json',
    ),
]

def _serve_media(request, path, document_root=None):
    if not (settings.DEBUG or getattr(settings, 'SERVE_MEDIA', False)):
        raise Http404()
    return serve(request, path, document_root=settings.MEDIA_ROOT)


urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', _serve_media),
]

# Personalización del admin
admin.site.site_header = "FLEX-OP Administración"
admin.site.site_title = "FLEX-OP Admin"
admin.site.index_title = "Panel de Administración"

