"""
Permisos personalizados por rol — FLEX-OP.
"""
from rest_framework.permissions import SAFE_METHODS, BasePermission, IsAuthenticated


class IsAuthenticatedFlex(IsAuthenticated):
    """Usuario autenticado con cuenta activa."""

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return request.user.activo


class IsAdminUser(BasePermission):
    """Solo administradores del sistema."""

    message = 'Se requiere rol de administrador.'

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.es_admin
        )


class IsSupervisorOrAbove(BasePermission):
    """Supervisor, gerente o administrador."""

    message = 'Se requiere rol de supervisor o superior.'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.es_supervisor or request.user.es_gerente or request.user.es_admin


class IsOperario(BasePermission):
    """Solo operarios de piso."""

    message = 'Se requiere rol de operario.'

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.es_operario
        )


class IsGerenteOrAbove(BasePermission):
    """Gerente o administrador."""

    message = 'Se requiere rol de gerente o superior.'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.es_gerente or request.user.es_admin


class IsSupervisorOrAboveForWrite(BasePermission):
    """Lectura autenticada; escritura solo supervisor, gerente o admin."""

    message = 'Se requiere rol de supervisor o superior.'

    def has_permission(self, request, view):
        if not IsAuthenticatedFlex().has_permission(request, view):
            return False
        if request.method in SAFE_METHODS:
            return True
        return (
            request.user.es_supervisor
            or request.user.es_gerente
            or request.user.es_admin
        )


class CanTransitionAsignacion(BasePermission):
    """Operario solo inicia/finaliza su asignación; supervisor+ el resto."""

    message = 'No tiene permiso sobre esta asignación.'

    def has_permission(self, request, view):
        return IsAuthenticatedFlex().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        if view.action in ('iniciar', 'finalizar', 'pausar', 'reanudar', 'eventos'):
            if request.user.es_operario:
                perfil = getattr(request.user, 'perfil_operario', None)
                return perfil is not None and obj.operario_id == perfil.id
            return (
                request.user.es_supervisor
                or request.user.es_gerente
                or request.user.es_admin
            )
        if request.method in SAFE_METHODS:
            return True
        return (
            request.user.es_supervisor
            or request.user.es_gerente
            or request.user.es_admin
        )
