from django.core.paginator import Paginator
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Vehiculo
from .serializers import VehiculoSerializer


def _pagina(queryset, serializer_class, page_number):
    paginator = Paginator(queryset, 10)
    page = paginator.get_page(page_number)
    return Response({
        'pagina_actual': page.number,
        'total_paginas': paginator.num_pages,
        'total_registros': paginator.count,
        'resultados': serializer_class(page.object_list, many=True).data,
    })


def _requiere_staff(request):
    return request.user.is_authenticated and request.user.is_staff


def _filtro_entero(value, nombre):
    try:
        entero = int(value)
    except (TypeError, ValueError):
        raise ValueError(f'El filtro {nombre} debe ser un entero.')
    if entero < 0:
        raise ValueError(f'El filtro {nombre} no puede ser negativo.')
    return entero


@api_view(['GET', 'POST'])
def vehiculos_api(request):
    if request.method == 'GET':
        vehiculos = Vehiculo.objects.all().order_by('placa')
        estado = request.query_params.get('estado')
        kilometraje_min = request.query_params.get('kilometraje_min')
        kilometraje_max = request.query_params.get('kilometraje_max')

        if estado:
            vehiculos = vehiculos.filter(estado__iexact=estado)
        if kilometraje_min is not None:
            try:
                kilometraje_min = _filtro_entero(kilometraje_min, 'kilometraje_min')
            except ValueError as error:
                return Response({'error': str(error)}, status=status.HTTP_400_BAD_REQUEST)
            vehiculos = vehiculos.filter(kilometraje__gte=kilometraje_min)
        if kilometraje_max is not None:
            try:
                kilometraje_max = _filtro_entero(kilometraje_max, 'kilometraje_max')
            except ValueError as error:
                return Response({'error': str(error)}, status=status.HTTP_400_BAD_REQUEST)
            vehiculos = vehiculos.filter(kilometraje__lte=kilometraje_max)
        if (
            kilometraje_min is not None
            and kilometraje_max is not None
            and kilometraje_min > kilometraje_max
        ):
            return Response(
                {'error': 'kilometraje_min no puede ser mayor que kilometraje_max.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return _pagina(vehiculos, VehiculoSerializer, request.query_params.get('page', 1))

    if not _requiere_staff(request):
        return Response(
            {'error': 'Se requiere un usuario administrador.'},
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = VehiculoSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def vehiculo_detalle_api(request, pk):
    try:
        vehiculo = Vehiculo.objects.get(pk=pk)
    except Vehiculo.DoesNotExist:
        return Response(
            {'error': 'Vehículo no encontrado.'},
            status=status.HTTP_404_NOT_FOUND,
        )

    if request.method == 'GET':
        return Response(VehiculoSerializer(vehiculo).data)

    if not _requiere_staff(request):
        return Response(
            {'error': 'Se requiere un usuario administrador.'},
            status=status.HTTP_403_FORBIDDEN,
        )

    if request.method in ['PUT', 'PATCH']:
        serializer = VehiculoSerializer(
            vehiculo,
            data=request.data,
            partial=request.method == 'PATCH',
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    vehiculo.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
