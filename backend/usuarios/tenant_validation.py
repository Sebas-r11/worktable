"""
Validaciones de pertenencia a empresa para FKs en serializers.
"""
from rest_framework import serializers


def _empresa_id_of(obj):
    if obj is None:
        return None
    if hasattr(obj, 'empresa_id'):
        return obj.empresa_id
    if hasattr(obj, 'usuario') and obj.usuario is not None:
        return obj.usuario.empresa_id
    if hasattr(obj, 'operario') and obj.operario is not None:
        operario_empresa_id = _empresa_id_of(obj.operario)
        if operario_empresa_id is not None:
            return operario_empresa_id
    if hasattr(obj, 'maquina') and obj.maquina is not None:
        return _empresa_id_of(obj.maquina)
    return None


def validate_same_empresa(request, **named_objects):
    """
    Verifica que cada objeto FK pertenezca a la empresa del usuario autenticado.
    named_objects: operario=..., maquina=..., etc.
    """
    user_empresa_id = getattr(request.user, 'empresa_id', None)
    if user_empresa_id is None:
        raise serializers.ValidationError('Usuario sin empresa asignada.')

    errors = {}
    for field_name, obj in named_objects.items():
        if obj is None:
            continue
        obj_empresa_id = _empresa_id_of(obj)
        if obj_empresa_id is not None and obj_empresa_id != user_empresa_id:
            errors[field_name] = 'No pertenece a su empresa.'
    if errors:
        raise serializers.ValidationError(errors)
