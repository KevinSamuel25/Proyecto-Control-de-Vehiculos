from django.core.paginator import Paginator
from django.db.models import Q
from django.db.models.deletion import ProtectedError

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Proveedor
from .serializers import ProveedorSerializer


def verificar_admin(request):
    if not request.user.is_authenticated:
        return Response(
            {'error': 'Autenticacion requerida.'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    if not request.user.is_staff:
        return Response(
            {'error': 'Se requiere administrador.'},
            status=status.HTTP_403_FORBIDDEN
        )

    return None


@api_view(['GET', 'POST'])
def proveedores_api(request):

    if request.method == 'GET':
        proveedores = Proveedor.objects.all().order_by('id')

        buscar = request.query_params.get('buscar')

        if buscar:
            proveedores = proveedores.filter(
                Q(nombre__icontains=buscar) |
                Q(cedula_juridica__icontains=buscar)
            )

        paginator = Paginator(proveedores, 5)
        pagina = paginator.get_page(request.query_params.get('page', 1))

        serializer = ProveedorSerializer(
            pagina.object_list,
            many=True
        )

        return Response({
            'pagina_actual': pagina.number,
            'total_paginas': paginator.num_pages,
            'total_registros': paginator.count,
            'resultados': serializer.data
        })

    error = verificar_admin(request)
    if error is not None:
        return error

    serializer = ProveedorSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def proveedor_detalle_api(request, pk):

    try:
        proveedor = Proveedor.objects.get(pk=pk)
    except Proveedor.DoesNotExist:
        return Response(
            {'error': 'Proveedor no encontrado.'},
            status=status.HTTP_404_NOT_FOUND
        )

    if request.method == 'GET':
        serializer = ProveedorSerializer(proveedor)
        return Response(serializer.data)

    error = verificar_admin(request)
    if error is not None:
        return error

    if request.method in ['PUT', 'PATCH']:

        serializer = ProveedorSerializer(
            proveedor,
            data=request.data,
            partial=request.method == 'PATCH'
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    if request.method == 'DELETE':
        try:
            proveedor.delete()
            return Response(
                status=status.HTTP_204_NO_CONTENT
            )
        except ProtectedError:
            return Response(
                {'error': 'No se puede eliminar un proveedor con repuestos asociados.'},
                status=status.HTTP_409_CONFLICT
            )