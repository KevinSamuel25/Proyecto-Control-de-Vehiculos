from django.core.paginator import Paginator
from django.db.models import Q
from django.db.models.deletion import ProtectedError

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from Control_de_vehiculos.seguridad import requiere_admin
from .models import Proveedor
from .serializers import ProveedorSerializer


@api_view(['GET', 'POST'])
def proveedores_api(peticion):

    if peticion.method == 'GET':
        proveedores = Proveedor.objects.all().order_by('id')

        buscar = peticion.query_params.get('buscar')

        if buscar:
            proveedores = proveedores.filter(
                Q(nombre__icontains=buscar) |
                Q(cedula_juridica__icontains=buscar)
            )

        paginador = Paginator(proveedores, 5)
        pagina = paginador.get_page(peticion.query_params.get('page', 1))

        serializador = ProveedorSerializer(
            pagina.object_list,
            many=True
        )

        return Response({
            'pagina_actual': pagina.number,
            'total_paginas': paginador.num_pages,
            'total_registros': pagina.paginator.count,
            'resultados': serializador.data
        })

    error = requiere_admin(peticion)
    if error is not None:
        return error

    serializador = ProveedorSerializer(data=peticion.data)

    if serializador.is_valid():
        serializador.save()
        return Response(
            serializador.data,
            status=status.HTTP_201_CREATED
        )

    return Response(
        serializador.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def proveedor_detalle_api(peticion, pk):

    try:
        proveedor = Proveedor.objects.get(pk=pk)
    except Proveedor.DoesNotExist:
        return Response(
            {'error': 'Proveedor no encontrado.'},
            status=status.HTTP_404_NOT_FOUND
        )

    if peticion.method == 'GET':
        serializador = ProveedorSerializer(proveedor)
        return Response(serializador.data)

    error = requiere_admin(peticion)
    if error is not None:
        return error

    if peticion.method in ['PUT', 'PATCH']:

        serializador = ProveedorSerializer(
            proveedor,
            data=peticion.data,
            partial=peticion.method == 'PATCH'
        )

        if serializador.is_valid():
            serializador.save()
            return Response(serializador.data)

        return Response(
            serializador.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    if peticion.method == 'DELETE':
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
