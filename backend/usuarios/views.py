"""
ViewSets para autenticación en FLEX-OP
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import update_session_auth_hash

from .mixins import EmpresaFilterMixin
from .models import User, Empresa
from .permissions import IsAdminUser, IsAuthenticatedFlex
from .serializers import (
    UserSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer,
    AdminSetPasswordSerializer,
    EmpresaSerializer
)


class UserViewSet(EmpresaFilterMixin, viewsets.ModelViewSet):
    # Gestiona el CRUD de usuarios y acciones como ver perfil, cambiar contraseña, listar operarios y supervisores
    """ViewSet para gestionar usuarios"""

    empresa_lookup = 'empresa'
    queryset = User.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer
    
    def get_permissions(self):
        """Solo administradores pueden crear usuarios."""
        if self.action == 'create':
            return [IsAdminUser()]
        if self.action == 'destroy':
            return [IsAdminUser()]
        return [IsAuthenticatedFlex()]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance != request.user and not request.user.es_admin:
            return Response(
                {'detail': 'No tiene permiso para modificar este usuario.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance != request.user and not request.user.es_admin:
            return Response(
                {'detail': 'No tiene permiso para modificar este usuario.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().partial_update(request, *args, **kwargs)

    def perform_create(self, serializer):
        empresa = getattr(self.request.user, 'empresa', None)
        if empresa is not None:
            serializer.save(empresa=empresa)
        else:
            serializer.save()
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Obtener información del usuario actual"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def change_password(self, request, pk=None):
        """Cambiar contraseña de usuario"""
        user = self.get_object()
        
        # Solo el usuario puede cambiar su propia contraseña o un admin
        if user != request.user and not request.user.es_admin:
            return Response(
                {'error': 'No tienes permiso para cambiar la contraseña de este usuario.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            # Verificar contraseña actual
            if not user.check_password(serializer.data.get('old_password')):
                return Response(
                    {'old_password': 'Contraseña actual incorrecta.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Establecer nueva contraseña
            user.set_password(serializer.data.get('new_password'))
            user.save()
            
            # Mantener la sesión activa después del cambio
            update_session_auth_hash(request, user)
            
            return Response({'message': 'Contraseña actualizada exitosamente.'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def set_password(self, request, pk=None):
        """Permite a un admin restablecer la contraseña de cualquier usuario."""
        if not request.user.es_admin:
            return Response(
                {'error': 'Solo un administrador puede restablecer contraseñas.'},
                status=status.HTTP_403_FORBIDDEN
            )

        user = self.get_object()
        serializer = AdminSetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            user.set_password(serializer.validated_data['new_password'])
            user.save()

            if user == request.user:
                update_session_auth_hash(request, user)

            return Response({'message': 'Contraseña restablecida exitosamente.'})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def operarios(self, request):
        """Listar solo usuarios con rol operario"""
        operarios = self.get_queryset().filter(rol=User.RolChoices.OPERARIO)
        serializer = self.get_serializer(operarios, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def supervisores(self, request):
        """Listar solo usuarios con rol supervisor"""
        supervisores = self.get_queryset().filter(rol=User.RolChoices.SUPERVISOR)
        serializer = self.get_serializer(supervisores, many=True)
        return Response(serializer.data)


class EmpresaViewSet(viewsets.ModelViewSet):
    # Gestiona el CRUD de empresas (alta, baja, modificación, listado)
    """ViewSet para gestionar empresas"""

    queryset = Empresa.objects.all()
    serializer_class = EmpresaSerializer
    permission_classes = [IsAuthenticatedFlex]

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsAdminUser()]
        return [IsAuthenticatedFlex()]

    def get_queryset(self):
        user = self.request.user
        if user.es_admin:
            return Empresa.objects.all()
        if user.empresa_id:
            return Empresa.objects.filter(pk=user.empresa_id)
        return Empresa.objects.none()
    
    filterset_fields = ['activa']
    search_fields = ['nombre', 'ruc', 'razon_social']
    ordering_fields = ['nombre', 'fecha_creacion']
