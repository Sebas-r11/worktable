"""
Mixins compartidos para ViewSets de FLEX-OP.
"""
from rest_framework.exceptions import PermissionDenied


class EmpresaPerformCreateMixin:
    """Fija empresa del usuario autenticado al crear; impide cambiarla en updates."""

    def perform_create(self, serializer):
        empresa = getattr(self.request.user, 'empresa', None)
        if empresa is None:
            raise PermissionDenied('Usuario sin empresa asignada.')

        model = serializer.Meta.model
        field_names = {f.name for f in model._meta.get_fields()}
        if 'empresa' in field_names:
            serializer.save(empresa=empresa)
        else:
            serializer.save()

    def perform_update(self, serializer):
        if 'empresa' in serializer.validated_data:
            serializer.validated_data.pop('empresa')
        serializer.save()


class EmpresaFilterMixin:
    """
    Restringe el queryset a la empresa del usuario autenticado.
    Definir `empresa_lookup` en cada ViewSet (ej. 'empresa', 'maquina__empresa').
    """

    empresa_lookup = 'empresa'

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if not user.is_authenticated:
            return qs.none()
        empresa = user.empresa
        if empresa is None:
            return qs.none()
        return qs.filter(**{self.empresa_lookup: empresa})
