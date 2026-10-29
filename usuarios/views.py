from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


def _roles_de(usuario):
    roles = list(usuario.groups.values_list('name', flat=True))
    if usuario.is_staff:
        roles.insert(0, 'Administrador')
    return roles


class VistaTokenLogin(ObtainAuthToken):

    def post(self, peticion, *args, **kwargs):
        serializador = self.get_serializer(data=peticion.data)
        serializador.is_valid(raise_exception=True)
        usuario = serializador.validated_data['user']
        token, _ = Token.objects.get_or_create(user=usuario)
        return Response({
            'token': token.key,
            'usuario': {
                'id': usuario.id,
                'username': usuario.username,
                'email': usuario.email,
                'roles': _roles_de(usuario),
            },
        })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_api(peticion):
    Token.objects.filter(user=peticion.user).delete()
    return Response(
        {'mensaje': 'Sesión cerrada. El token ha sido invalidado.'},
        status=status.HTTP_200_OK,
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def perfil_api(peticion):
    usuario = peticion.user
    return Response({
        'id': usuario.id,
        'username': usuario.username,
        'email': usuario.email,
        'es_administrador': usuario.is_staff,
        'roles': _roles_de(usuario),
    })
