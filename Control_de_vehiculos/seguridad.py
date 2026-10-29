from rest_framework import status
from rest_framework.response import Response

GRUPO_OPERADOR = 'Operador'
GRUPO_CONSULTA = 'Consulta'


def es_administrador(usuario):
    return usuario.is_authenticated and usuario.is_staff


def es_operador(usuario):
    return es_administrador(usuario) or (
        usuario.is_authenticated
        and usuario.groups.filter(name=GRUPO_OPERADOR).exists()
    )


def requiere_admin(peticion):
    if not es_administrador(peticion.user):
        return Response(
            {'error': 'Se requiere rol administrador para esta operación.'},
            status=status.HTTP_403_FORBIDDEN,
        )
    return None


def requiere_operador(peticion):
    if not es_operador(peticion.user):
        return Response(
            {'error': 'Se requiere rol operador o administrador para esta operación.'},
            status=status.HTTP_403_FORBIDDEN,
        )
    return None
